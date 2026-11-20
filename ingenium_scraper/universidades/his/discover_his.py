"""Fase 1 · Descubrimiento — University of Skövde / Högskolan i Skövde (his.se).

Programa: Högskoleingenjör i maskinteknik (MAHIG), 180 hp.

Fuente ÚNICA: la página oficial del programa en www.his.se (HTML estático,
permitida por robots.txt). De ella se extraen:
  * bloque "Kursupplägg" (acordeón FAQ): lista completa de cursos con hp,
    año, termin y fördjupning (itinerario de 3º);
  * bloque "Kursplaner" de la convocatoria de admisión más antigua publicada
    (la que tiene más terminer con kursplan): enlaces PDF a los kursplaner.

IMPORTANTE: los kursplaner viven en https://pdfproxy.his.se/ y su robots.txt
dice "User-agent: * / Disallow: /" (solo Googlebot/Bingbot permitidos). Este
script NO descarga nada de pdfproxy.his.se; solo registra las URL que la
página del programa publica. Ver notas_descubrimiento.md.

La página no publica códigos de curso (viven dentro de los PDF). El campo
`codigo_asignatura` es por tanto una CLAVE PROVISIONAL determinista
(MAHIG-T<termin>-<SLUG-DEL-NOMBRE>), no un código oficial.

Uso:  python universidades/his/discover_his.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
UNIVERSIDAD = "University of Skövde (Högskolan i Skövde)"
SLUG = "his"
PROGRAM_CODE = "MAHIG"
PROGRAM_URL = "https://www.his.se/utbildning/ingenjor-och-teknik/hogskoleingenjor-i-maskinteknik-mahig"
ECTS_PLAN = 180.0

ROMAN = {"i": "1", "ii": "2", "iii": "3"}
LEVEL_RE = re.compile(r"^[ga][12][nfe]$", re.I)  # sufijos de nivel tipo G1N, G2F, A1N


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def ascii_fold(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def norm_key(name: str) -> str:
    """Clave de comparación entre el nombre del 'Kursupplägg' y el del enlace al kursplan."""
    s = ascii_fold(name).lower().replace("&", " och ")
    toks = [t for t in re.split(r"[^a-z0-9]+", s) if t and not LEVEL_RE.match(t)]
    toks = [ROMAN.get(t, t) for t in toks]
    return "".join(toks)


def slug_code(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", ascii_fold(name).upper()).strip("-")


def parse_hp(text: str) -> tuple[str, float]:
    m = re.match(r"^(.*?),\s*(\d+(?:,\d+)?)\s*hp\s*$", clean(text))
    if not m:
        raise ValueError(f"Línea de curso no reconocida: {text!r}")
    return clean(m.group(1)), float(m.group(2).replace(",", "."))


def parse_kursupplagg(soup: BeautifulSoup) -> list[dict]:
    """Devuelve filas {nombre, hp, curso, semestre, track} del acordeón 'Kursupplägg'."""
    h2 = soup.find("h2", string=re.compile(r"Kursuppl.gg"))
    if h2 is None:
        raise RuntimeError("No se encuentra el bloque 'Kursupplägg'")
    dl = h2.find_next("dl", class_="faq")
    rows: list[dict] = []
    for dt in dl.find_all("dt", recursive=False):
        dd = dt.find_next_sibling("dd")
        question = clean(dt.get_text(" "))
        m = re.search(r"År\s*(\d)", question)
        year = int(m.group(1)) if m and "och" not in question else None
        track = None
        term_ready = False
        season = None
        for el in dd.find_all(["h3", "h4", "ul"]):
            if el.name in ("h3", "h4"):
                txt = clean(el.get_text(" "))
                low = txt.lower()
                my = re.match(r"År\s*(\d)\s*[–-]\s*(höst|vår)termin", txt, re.I)
                if my:
                    year, season, term_ready = int(my.group(1)), my.group(2).lower(), True
                elif low in ("hösttermin", "vårtermin"):
                    season, term_ready = low[:-6], True
                else:
                    term_ready = False
                    if el.name == "h3":
                        track = txt  # nombre de la fördjupning (solo se usa si siguen terminer)
                continue
            if not term_ready:
                continue
            term_ready = False
            if year is None:
                raise RuntimeError(f"Termin sin año en {question!r}")
            semestre = (year - 1) * 2 + (1 if season == "höst" else 2)
            for li in el.find_all("li"):
                nombre, hp = parse_hp(li.get_text(" "))
                rows.append({"nombre": nombre, "hp": hp, "curso": year, "semestre": semestre,
                             "season": season, "track": track if year >= 3 else None})
    return rows


def parse_kursplaner(soup: BeautifulSoup) -> tuple[str, str, dict[int, list[tuple[str, str]]]]:
    """Enlaces a kursplaner por termin de la convocatoria con más terminer publicados.
    Devuelve (etiqueta convocatoria, url utbildningsplan, {termin: [(nombre, url)]})."""
    best = None
    for sec in soup.select("section.program-occation-more-info"):
        terms: dict[int, list[tuple[str, str]]] = {}
        first_label = None
        for head in sec.select("div.program-course-semester"):
            label = clean(head.get_text(" "))
            m = re.match(r"Termin\s*(\d+),\s*(.+)$", label)
            if not m:
                continue
            first_label = first_label or m.group(2)
            box = sec.find(id=head.get("aria-controls"))
            links = []
            for a in box.select("div.program-course a[href]"):
                links.append((clean(re.sub(r"\(PDF\)\s*$", "", clean(a.get_text(" ")))), a["href"]))
            terms[int(m.group(1))] = links
        plan = sec.select_one("a.download-study-plan")
        cand = (first_label or "", plan["href"] if plan else "", terms)
        n = sum(len(v) for v in terms.values())
        if best is None or n > sum(len(v) for v in best[2].values()):
            best = cand
    if best is None:
        raise RuntimeError("No se encuentra ningún bloque 'Kursplaner'")
    return best


def match_links(rows: list[dict], terms: dict[int, list[tuple[str, str]]]) -> None:
    for termin, links in terms.items():
        cands = [r for r in rows if r["semestre"] == termin]
        for name, url in links:
            k = norm_key(name)
            hit = [r for r in cands if norm_key(r["nombre"]) == k]
            if not hit:
                hit = [r for r in cands if k.startswith(norm_key(r["nombre"])) or norm_key(r["nombre"]).startswith(k)]
            if len(hit) != 1:
                raise RuntimeError(f"Kursplan '{name}' (termin {termin}) no casa de forma única: {[h['nombre'] for h in hit]}")
            if "url" in hit[0]:
                raise RuntimeError(f"Dos kursplaner para '{hit[0]['nombre']}'")
            hit[0]["url"], hit[0]["nombre_kursplan"] = url, name


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(PROGRAM_URL), "lxml")
    nombre_grado = clean(soup.find("h1").get_text(" "))

    rows = parse_kursupplagg(soup)
    occasion, plan_url, terms = parse_kursplaner(soup)
    match_links(rows, terms)

    # Fusionar cursos repetidos entre fördjupningar (mismo nombre, hp y termin).
    merged: dict[tuple, dict] = {}
    for r in rows:
        key = (norm_key(r["nombre"]), r["hp"], r["semestre"])
        if key in merged:
            if r["track"] and r["track"] not in merged[key]["tracks"]:
                merged[key]["tracks"].append(r["track"])
        else:
            merged[key] = {**r, "tracks": [r["track"]] if r["track"] else []}
    all_tracks = sorted({r["track"] for r in rows if r["track"]})

    entries: list[CatalogEntry] = []
    for r in sorted(merged.values(), key=lambda x: x["semestre"]):  # orden estable por termin
        nombre = r.get("nombre_kursplan") or r["nombre"]
        low = r["nombre"].lower()
        if low.startswith("valfri"):
            caracter = "optativa (valfri kurs, libre elección)"
        elif low.startswith("examensarbete"):
            caracter = "tfg"
        elif r["tracks"] and sorted(r["tracks"]) != all_tracks:
            caracter = "optativa de itinerario (fördjupning: " + " / ".join(r["tracks"]) + ")"
        else:
            caracter = "obligatoria"
        cs = f"År {r['curso']} / {'Hösttermin' if r['season'] == 'höst' else 'Vårtermin'} (termin {r['semestre']})"
        if r["tracks"] and sorted(r["tracks"]) != all_tracks:
            cs += " / Fördjupning: " + ", ".join(r["tracks"])
        url = r.get("url")
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=nombre_grado,
            codigo_asignatura=f"{PROGRAM_CODE}-T{r['semestre']}-{slug_code(r['nombre'])}",
            nombre_asignatura=nombre, curso_semestre=cs, curso=r["curso"], semestre=r["semestre"],
            creditos_ects=r["hp"], caracter=caracter, idioma_pagina="sv",
            url_guia_docente=url, tipo_fuente="pdf" if url else "sin_guia",
        ))

    # ---- validación ----
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes)), "códigos duplicados"
    common = sum(e.creditos_ects for e in entries if e.curso <= 2)
    assert common == 120.0, f"años 1-2 suman {common}, se esperaba 120"
    for t in all_tracks:  # cada itinerario debe sumar 60 hp en 3º
        tot = sum(r["hp"] for r in rows if r["curso"] == 3 and r["track"] == t)
        assert tot == 60.0, f"fördjupning {t}: año 3 suma {tot}"
    assert all(e.url_guia_docente or e.tipo_fuente == "sin_guia" for e in entries)

    m = re.search(r"(\d{4})", occasion)
    y0 = int(m.group(1)) if m else time.localtime().tm_year
    total = sum(e.creditos_ects for e in entries)
    n_url = sum(1 for e in entries if e.url_guia_docente)
    catalog = Catalog(
        meta=CatalogMeta(
            universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=f"{nombre_grado} ({PROGRAM_CODE}), 180 hp",
            curso_academico=f"{y0}/{y0 + 1}", url_plan_estudios=PROGRAM_URL, ects_totales_plan=ECTS_PLAN,
            estrategia_fuente=("HTML estático de la página del programa en www.his.se: lista 'Kursupplägg' "
                               "(cursos, hp, año/termin, fördjupning) + enlaces 'Kursplaner' (PDF en pdfproxy.his.se) "
                               f"de la convocatoria {occasion}."),
            generado_por="discover_his.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
            estado="parcial",
            notas=(f"{len(entries)} filas, {total} hp en total = 120 hp comunes (años 1-2, incl. 7,5 hp valfri kurs) + "
                   f"año 3: {len(all_tracks)} fördjupningar alternativas ({', '.join(all_tracks)}) de 30 hp cada una en otoño "
                   "(FEM compartida por dos) + 7,5 hp valfri kurs + 22,5 hp examensarbete. Cada estudiante cursa 180 hp. "
                   f"Solo {n_url} filas tienen kursplan enlazado (terminer publicados de la convocatoria {occasion}); "
                   "el resto queda como sin_guia. codigo_asignatura es una CLAVE PROVISIONAL (la web no publica códigos; "
                   "están dentro de los PDF). Los PDF están en pdfproxy.his.se, cuyo robots.txt prohíbe todo a bots "
                   f"distintos de Googlebot/Bingbot: NO se han descargado. Utbildningsplan (PDF, mismo host): {plan_url}"),
        ),
        asignaturas=entries,
    )
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {out.name}: {len(entries)} asignaturas, {total} hp, {n_url} con URL | http stats: {http.stats}")


if __name__ == "__main__":
    main()
