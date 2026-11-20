#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Université de Rouen Normandie,
Licence Mécanique, parcours Mécanique-Énergétique (180 ECTS, L1-L3).

Fuente: catálogo ODF (Ametys) en formation.univ-rouen.fr. La página del parcours
contiene el plan completo en HTML estático: un `div.tab-pane[id^=tab-content-]` por
año (L1 y L2 = "Portail Physique-Mécanique-Physique,Chimie", común; L3 = Mécanique-
Énergétique), dentro un `div.tab-pane[id^=semester-]` por semestre, y en cada
semestre un acordeón de UE (unités d'enseignement, que son las que llevan ECTS) con
sus éléments (EC, sin ECTS propios en general). Las UE "au choix" contienen una lista
de opciones (cada opción es una UE de 6 ECTS).

Granularidad del catálogo: una fila por UE (unidad con ECTS); en las UE de elección,
una fila por opción. El código es el identificador ODF/ROF que Ametys pone al final
del slug de la URL (p. ej. `...-L5MCAVC2.html` -> L5MCAVC2).

Uso (desde la raíz del proyecto):
    python universidades/univ_rouen/discover_univ_rouen.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, Tag  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "univ_rouen"
UNIVERSIDAD = "Université de Rouen Normandie"
HOST = "https://formation.univ-rouen.fr"
PLAN_URL = (HOST + "/fr/catalogue-de-l-offre-de-formation/licence-lmd-XA/licence-mecanique-L5MEP09P/"
            "licence-mecanique-mecanique-energetique-LBVZSTJE.html")

CODE_RE = re.compile(r"-([A-Z0-9]+)\.html$")
CREDITS_RE = re.compile(r"^(\d+(?:[.,]\d+)?)\s*cr[ée]dits?$", re.I)
SEM_RE = re.compile(r"^Semestre\s+(\d+)$")
CHOICE_RE = re.compile(r"Au choix\s*:\s*(\d+)\s*parmi\s*(\d+)", re.I)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def code_of(href: str) -> str:
    m = CODE_RE.search(href)
    if not m:
        raise RuntimeError(f"URL sin código ODF: {href}")
    return m.group(1)


def header_info(li: Tag) -> tuple[str, str | None, float | None]:
    """(título, href, créditos) de un item de acordeón Ametys."""
    h = li.find("header", recursive=False)
    if h is None:
        return "", None, None
    a = h.select_one("h2.ametys-accordion__item-title a[href]")
    title_el = h.select_one("h2.ametys-accordion__item-title")
    title = norm((a or title_el or h).get_text(" "))
    cred_el = h.select_one(".ametys-accordion__item-text")
    cred = None
    if cred_el and norm(cred_el.get_text()):
        m = CREDITS_RE.match(norm(cred_el.get_text()))
        if not m:
            raise RuntimeError(f"Texto de créditos inesperado: {cred_el.get_text()!r}")
        cred = float(m.group(1).replace(",", "."))
    return title, (a["href"] if a else None), cred


def child_items(li: Tag) -> list[Tag]:
    """Items (li) del acordeón interno inmediato de `li`."""
    body = li.find("div", class_="collapse", recursive=False)
    if body is None:
        return []
    ul = body.find("ul")
    return ul.find_all("li", recursive=False) if ul else []


def parse_plan(html: str) -> tuple[str, float, list[dict]]:
    soup = BeautifulSoup(html, "lxml")
    nombre = norm(soup.find("h1").get_text(" "))
    # ECTS totales: bloque de cabecera "ECTS / 180 crédits"
    ects_total = None
    for el in soup.find_all(string=re.compile(r"^\s*ECTS\s*$")):
        nxt = el.find_parent().find_next(string=CREDITS_RE)
        if nxt:
            ects_total = float(CREDITS_RE.match(norm(nxt)).group(1))
            break
    if ects_total is None:
        raise RuntimeError("No se encuentran los ECTS totales del parcours")

    rows: list[dict] = []
    years = soup.select("div.tab-pane[id^=tab-content-]")
    if len(years) != 3:
        raise RuntimeError(f"Se esperaban 3 años en el plan, hay {len(years)}")
    for yp in years:
        year_title = norm(yp.find("h3").get_text(" "))
        labels = {a["href"][1:]: norm(a.get_text()) for a in
                  yp.select("a.ametys-tabs-controls__link[href^='#semester-']")}
        for sp in yp.select("div.tab-pane[id^=semester-]"):
            m = SEM_RE.match(labels.get(sp["id"], ""))
            if not m:
                raise RuntimeError(f"Semestre sin etiqueta: {sp['id']}")
            sem = int(m.group(1))
            ul = sp.find("ul", class_="ametys-accordion")
            for ue in ul.find_all("li", recursive=False):
                title, href, cred = header_info(ue)
                if not href or cred is None:
                    raise RuntimeError(f"UE sin enlace o sin créditos: {title!r}")
                kids = child_items(ue)
                choice_kids = [k for k in kids if header_info(k)[1] and
                               re.search(r"choix", header_info(k)[0], re.I)]
                base = {"anio": year_title, "sem": sem, "ue_titulo": title}
                if not choice_kids:
                    rows.append({**base, "codigo": code_of(href), "nombre": title, "creditos": cred,
                                 "url": HOST + href, "caracter": "obligatoria", "grupo": None,
                                 "elementos": [header_info(k)[0] for k in kids]})
                    continue
                if len(choice_kids) != 1 or len(kids) != 1:
                    raise RuntimeError(f"Estructura de elección inesperada en {title!r}")
                grp = choice_kids[0]
                # "Au choix : n parmi m" -> lista de opciones
                cab = next((li for li in grp.find_all("li") if CHOICE_RE.search(header_info(li)[0])), None)
                if cab is None:
                    raise RuntimeError(f"Sin cabecera 'Au choix' en {title!r}")
                n, m_ = map(int, CHOICE_RE.search(header_info(cab)[0]).groups())
                # el contenedor "Au choix" lleva sus opciones en un <ul> hijo directo (sin collapse)
                opts = cab.find("ul", recursive=False).find_all("li", recursive=False)
                if len(opts) != m_:
                    raise RuntimeError(f"{title!r}: {len(opts)} opciones, la cabecera dice {m_}")
                for o in opts:
                    otitle, ohref, ocred = header_info(o)
                    if not ohref or ocred is None:
                        raise RuntimeError(f"Opción sin enlace/créditos en {title!r}: {otitle!r}")
                    if ocred * n != cred:
                        raise RuntimeError(f"{otitle!r}: {ocred} ECTS x {n} != {cred} de la UE {title!r}")
                    rows.append({**base, "codigo": code_of(ohref), "nombre": otitle, "creditos": ocred,
                                 "url": HOST + ohref, "caracter": "obligatoria" if m_ == n else "optativa",
                                 "grupo": f"{code_of(href)} ({title}): {n} parmi {m_}",
                                 "elementos": [header_info(k)[0] for k in child_items(o)]})
    return nombre, ects_total, rows


def academic_year(http: PoliteClient, url: str) -> str:
    """El catálogo ODF no rotula el curso; se toma el curso vigente en la fecha de descarga
    (cacheada): septiembre-agosto."""
    meta = http._paths(url)[1]
    fetched = json.loads(meta.read_text(encoding="utf-8"))["fetched_at"]
    y, mth = int(fetched[:4]), int(fetched[5:7])
    start = y if mth >= 9 else y - 1
    return f"{start}-{start + 1}"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    nombre, ects_total, rows = parse_plan(http.get_text(PLAN_URL))
    curso_acad = academic_year(http, PLAN_URL)
    rows.sort(key=lambda r: r["sem"])  # estable: conserva el orden del plan dentro del semestre

    entries = []
    for r in rows:
        curso = (r["sem"] + 1) // 2
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD,
            nombre_grado=nombre,
            codigo_asignatura=r["codigo"],
            nombre_asignatura=r["nombre"],
            curso_semestre=f"{r['anio']} / Semestre {r['sem']}"
                           + (f" / option de {r['grupo']}" if r["grupo"] else ""),
            curso=curso,
            semestre=r["sem"],
            creditos_ects=r["creditos"],
            caracter=r["caracter"],
            idioma_pagina="fr",
            url_guia_docente=r["url"],
            tipo_fuente="html",
        ))

    # ---------- validación ----------
    codigos = [e.codigo_asignatura for e in entries]
    dup = {c for c in codigos if codigos.count(c) > 1}
    assert not dup, f"Códigos duplicados: {dup}"
    assert all(e.url_guia_docente for e in entries), "Fila sin URL"
    oblig = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    grupos: dict[str, float] = {}
    for r in rows:
        if r["caracter"] == "optativa":
            n = int(re.search(r": (\d+) parmi", r["grupo"]).group(1))
            grupos[r["grupo"]] = r["creditos"] * n
    total = oblig + sum(grupos.values())
    assert total == ects_total, f"ECTS: obligatorias {oblig} + elección {sum(grupos.values())} != {ects_total}"
    por_sem: dict[int, float] = {}
    for r in rows:
        if r["caracter"] == "obligatoria":
            por_sem[r["sem"]] = por_sem.get(r["sem"], 0) + r["creditos"]
    for g, v in grupos.items():
        s = next(r["sem"] for r in rows if r["grupo"] == g)
        por_sem[s] = por_sem.get(s, 0) + v
    assert all(v == 30 for v in por_sem.values()) and sorted(por_sem) == list(range(1, 7)), por_sem

    n_opt = sum(1 for e in entries if e.caracter == "optativa")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=nombre,
        curso_academico=curso_acad,
        url_plan_estudios=PLAN_URL,
        ects_totales_plan=ects_total,
        estrategia_fuente=("HTML estático del catálogo ODF (Ametys) formation.univ-rouen.fr: acordeón del "
                           "plan (años > semestres > UE > éléments) en la página del parcours. Una fila por "
                           "UE (o por opción en las UE au choix); la ficha se compone en Fase 2 con la "
                           "página de la UE y las de sus éléments (Description, Objectifs, Pré-requis, "
                           "Contrôle des connaissances, Compétences visées)."),
        generado_por="discover_univ_rouen.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(f"Licence Mécanique de 3 años: L1-L2 = Portail Physique-Mécanique-Physique,Chimie (PMPC, común "
               f"con las licences de Física y Física-Química), L3 = parcours Mécanique-Énergétique. "
               f"{len(entries)} filas: {len(entries) - n_opt} UE obligatorias ({oblig:g} ECTS) y {n_opt} "
               f"opciones de {len(grupos)} UE au choix ({sum(grupos.values()):g} ECTS cursados); "
               f"total {total:g} = {ects_total:g}. Código = identificador ODF del slug de la URL. "
               f"curso_academico derivado de la fecha de descarga (el catálogo no lo rotula). "
               f"Las fichas de los éléments de L3 solo publican horas (sin descripción): ver "
               f"notas_descubrimiento.md."),
    )
    catalog = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{nombre} [{curso_acad}]: {len(entries)} filas ({n_opt} opciones), {total:g}/{ects_total:g} ECTS "
          f"-> {out}")
    print("ECTS por semestre:", por_sem)
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
