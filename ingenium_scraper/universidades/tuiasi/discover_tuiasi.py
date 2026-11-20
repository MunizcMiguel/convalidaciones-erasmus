"""Fase 1 (Descubrimiento) - Universitatea Tehnica "Gheorghe Asachi" din Iasi (TUIASI)
Facultatea de Mecanica - licenta "Inginerie Mecanica" (IM), 240 ECTS.

Fuentes (todas en mec.tuiasi.ro, robots.txt solo prohibe /wp-admin/):
  * Plan de estudios 2025-2026 (anos I-IV) del dossier de reacreditacion ARACIS del
    programa ("Anexa B.1.1.1.b ... PSUL"), localizado con la API JSON de WordPress
    (/wp-json/wp/v2/media?search=...). Tablas con capa de texto limpia -> pdfplumber.
  * Fichas de asignatura ("fisa disciplinei"): 4 PDF compartidos, uno por ano
    (FD_an{1..4}_IM_PSUL.pdf), enlazados desde https://mec.tuiasi.ro/fise-discipline-psul/.
    Cada ficha empieza en la pagina que contiene "2.1.2 Codul disciplinei"; el rango de
    paginas se deriva de ahi. Las fichas siguen el orden del plan.

Por que 2025-2026 y no 2026-2027: la pagina "Fise discipline 2026/2027" solo enlaza las
fichas del programa SET (las de IM aparecen sin enlace) y el plan 2026-2027 de 1er ano usa
codigos nuevos (IM.AM.101...) sin ficha publicada. El plan 2025-2026 y las fichas del
dossier PSUL forman un conjunto coherente (mismos codigos, mismo orden).

Uso (desde la raiz del proyecto):  python universidades/tuiasi/discover_tuiasi.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
UNIVERSIDAD = 'Universitatea Tehnică "Gheorghe Asachi" din Iași (TUIASI)'
SLUG = "tuiasi"
GRADO = "Inginerie Mecanică (licență, 4 ani / 240 ECTS) - Facultatea de Mecanică"
CURSO = "2025-26"
URL_FD_PAGE = "https://mec.tuiasi.ro/fise-discipline-psul/"
MEDIA_API = "https://mec.tuiasi.ro/wp-json/wp/v2/media"
PLAN_SEARCH = "Plan-invatamant-IM-2025-2026"
RE_PLAN_FILE = re.compile(r"Anexa-B\.1\.1\.1\.b-Plan-invatamant-IM-2025-2026.*\.pdf$")
RE_FD_FILE = re.compile(r"FD_an([1-4])_IM_PSUL\.pdf$")

RE_CODE_LINE = re.compile(r"2\.1\.2\.?\s*Codul disciplinei\s+(.+?)\s*$", re.M)
RE_NUM = re.compile(r"(?<!\d)([1-4]\d\d)(?!\d)")        # numero de 3 cifras: 1er digito = ano
RE_OPT = re.compile(r"-(\d)\s*$")                          # sufijo de optativa "-1", "-2"...
RE_CAT = re.compile(r"^[A-Z]+\.\d{3}\.(DI|DO|DL)\.")       # categoria dentro del codigo estandar


# ---------------------------------------------------------------- utilidades
def norm_code(raw: str) -> str:
    """'MTC 209 DI DD' / 'MTC.207. DI.DF.' / 'MTC. 406.DI.DD' -> 'MTC.209.DI.DD' ..."""
    c = re.sub(r"[\s.]+", ".", raw.strip().upper()).strip(".")
    return c


def match_key(code: str) -> str | None:
    """Clave de emparejamiento plan<->ficha independiente del prefijo (MTC/MCT/IM varian
    entre plan y ficha): numero de 3 cifras + sufijo de optativa."""
    m = RE_NUM.search(code)
    if not m:
        return None
    o = RE_OPT.search(code)
    return m.group(1) + (f"-{o.group(1)}" if o else "")


def clean(s: str | None) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def num(s: str | None) -> float | None:
    s = clean(s)
    if not s:
        return None
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


# ---------------------------------------------------------------- localizar fuentes
def find_sources(http: PoliteClient) -> tuple[str, dict[int, str]]:
    media = http.get_json(MEDIA_API, params={"search": PLAN_SEARCH, "per_page": 100})
    plans = sorted({m["source_url"] for m in media if RE_PLAN_FILE.search(m.get("source_url", ""))})
    if len(plans) != 1:
        raise RuntimeError(f"Se esperaba 1 PDF de plan, encontrados: {plans}")
    soup = BeautifulSoup(http.get_text(URL_FD_PAGE), "lxml")
    fds: dict[int, str] = {}
    for a in soup.find_all("a", href=True):
        href = urljoin(URL_FD_PAGE, a["href"])
        m = RE_FD_FILE.search(href)
        if m:
            fds[int(m.group(1))] = href
    if sorted(fds) != [1, 2, 3, 4]:
        raise RuntimeError(f"Faltan PDF de fichas por ano: {sorted(fds)}")
    return plans[0], fds


# ---------------------------------------------------------------- plan de estudios
# Columnas de las tablas por ano (21): cat, nr, nombre, codigo, categoria formativa,
# sem1: C S L P Pr SI Ev K, sem2: C S L P Pr SI Ev K
S1, S2 = 5, 13
HOURS = ("C", "S", "L", "P", "Pr", "SI")


def parse_plan(path: Path) -> list[dict]:
    rows: list[dict] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[1:]:
            text = page.extract_text() or ""
            if "PLAN DE INVATAMANT" not in text.upper().replace("Ă", "A").replace("Ț", "T"):
                continue
            for table in page.extract_tables():
                if not table or len(table[0]) != 21:
                    continue
                cat = None
                page_rows: list[dict] = []
                for r in table:
                    code = clean(r[3])
                    if not code or code.lower().startswith("cod"):
                        continue
                    if clean(r[0]):
                        cat = clean(r[0])
                    # la columna de categoria es una celda combinada que a veces viene vacia
                    # (DL del 3er ano): el codigo estandar "PS.nnn.DX..." la lleva dentro.
                    mc = RE_CAT.match(norm_code(code))
                    page_rows.append({
                        "cat": mc.group(1) if mc else cat, "nr": clean(r[1]) or None, "nombre": clean(r[2]), "codigo": norm_code(code),
                        "form": clean(r[4]) or None,
                        "s1": {"h": [clean(x) for x in r[S1:S1 + 6]], "ev": clean(r[S1 + 6]), "k": num(r[S1 + 7])},
                        "s2": {"h": [clean(x) for x in r[S2:S2 + 6]], "ev": clean(r[S2 + 6]), "k": num(r[S2 + 7])},
                    })
                if not page_rows:
                    continue
                # Ano: digito de los codigos de 3 cifras (el encabezado "ANUL ..." de la pag. 4
                # dice "ANUL II" para el 3er ano: errata del PDF, no se usa).
                years = Counter(int(m.group(1)[0]) for x in page_rows if (m := RE_NUM.search(x["codigo"])))
                year = years.most_common(1)[0][0]
                # Grupos de optativas: filas sin nr heredan del grupo (horas/creditos pueden
                # aparecer en cualquiera de sus filas, p. ej. MTC.115 en 1er ano).
                groups: list[list[dict]] = []
                for x in page_rows:
                    if x["nr"] or not groups:
                        groups.append([x])
                    else:
                        groups[-1].append(x)
                for g in groups:
                    for sk in ("s1", "s2"):
                        k = next((x[sk]["k"] for x in g if x[sk]["k"] is not None), None)
                        ev = next((x[sk]["ev"] for x in g if x[sk]["ev"]), "")
                        h = next((x[sk]["h"] for x in g if any(x[sk]["h"])), [""] * 6)
                        for x in g:
                            x[sk] = {"h": h, "ev": ev, "k": k}
                    for x in g:
                        x["nr"] = g[0]["nr"]
                        x["form"] = x["form"] or g[0]["form"]
                        x["year"] = year
                        x["grupo"] = len(g) if len(g) > 1 else 0
                        rows.append(x)
    return rows


# ---------------------------------------------------------------- PDF de fichas
def parse_fd(path: Path) -> tuple[list[dict], int]:
    """Devuelve [{codigo_ficha, pag_ini, pag_fin}] y el numero de paginas."""
    starts: list[dict] = []
    with pdfplumber.open(path) as pdf:
        n = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            # solo la franja superior: la cabecera de la ficha esta en el primer tercio
            top = page.crop((0, 0, page.width, page.height * 0.45)).extract_text() or ""
            m = RE_CODE_LINE.search(top)
            if m:
                starts.append({"codigo_ficha": norm_code(m.group(1)), "pag_ini": i + 1})
    for i, s in enumerate(starts):
        s["pag_fin"] = starts[i + 1]["pag_ini"] - 1 if i + 1 < len(starts) else n
    return starts, n


def caracter(row: dict) -> str:
    n = row["nombre"].lower()
    if row["cat"] == "DI" and "proiectului de diplom" in n and "practica" not in n:
        return "tfg"
    if row["cat"] == "DI" and n.startswith("practica"):
        return "practicas"
    if row["cat"] == "DO":
        return f"optativa (grupo {row['year']}.{row['nr']}, elegir 1 de {row['grupo']})"
    if row["cat"] == "DL":
        return "facultativa"
    return "obligatoria"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    url_plan, url_fds = find_sources(http)
    plan = parse_plan(http.get_file(url_plan))

    # emparejar fichas <-> filas del plan, ano a ano, POR ORDEN: el propio anexo declara que
    # las fichas siguen "ordinea din planul de invatamant", y los codigos escritos en las fichas
    # tienen erratas (IM.413.DO.DS-1 repetido, IM.416.DO.DS-21, IM.315 por MTC.315...).
    # Comprobaciones: mismo numero de fichas que de filas, y el numero de 3 cifras del codigo
    # de la ficha coincide con el del plan salvo erratas que se listan en las notas.
    entries: list[CatalogEntry] = []
    mismatches: list[str] = []
    sin_ficha: list[str] = []
    for year in (1, 2, 3, 4):
        fichas, _ = parse_fd(http.get_file(url_fds[year]))
        prow = [r for r in plan if r["year"] == year]
        if len(fichas) > len(prow):
            raise RuntimeError(f"Ano {year}: {len(fichas)} fichas vs {len(prow)} filas del plan")
        bad = 0
        for f, r in zip(fichas, prow):
            r["ficha"] = f
            kf, kp = match_key(f["codigo_ficha"]), match_key(r["codigo"])
            if kf != kp:
                bad += 1
                mismatches.append(f"{r['codigo']} (ficha dice {f['codigo_ficha']})")
        if bad > len(prow) // 4:
            raise RuntimeError(f"Ano {year}: demasiados codigos discrepantes ({bad}): el orden no cuadra")
        if len(fichas) < len(prow):
            # Faltan fichas al final del PDF: solo se acepta si la ultima pareja esta anclada
            # (mismo codigo en ficha y plan), de modo que las filas sobrantes son las del final.
            if match_key(fichas[-1]["codigo_ficha"]) != match_key(prow[len(fichas) - 1]["codigo"]):
                raise RuntimeError(f"Ano {year}: faltan fichas y la ultima no esta anclada")
            for r in prow[len(fichas):]:
                r["ficha"] = None
                sin_ficha.append(r["codigo"])

    dup = Counter(r["codigo"] for r in plan)
    for r in plan:
        f = r["ficha"]
        sems = [s for s, sk in ((1, "s1"), (2, "s2")) if r[sk]["k"] is not None]
        if not sems:
            raise RuntimeError(f"{r['codigo']}: sin creditos")
        ects = sum(r[f"s{s}"]["k"] for s in sems)
        code = r["codigo"]
        if dup[code] > 1:  # codigo repetido en el plan (DF.DI.L.1.01): se anade el nr. crt.
            code = f"{code}_nr{r['nr']}"
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO,
            codigo_asignatura=code, nombre_asignatura=r["nombre"],
            curso_semestre=f"Anul {r['year']} / Semestrul {'+'.join(map(str, sems))} ({r['cat']}, {r['form']})",
            curso=r["year"], semestre=(r["year"] - 1) * 2 + sems[0], creditos_ects=ects,
            caracter=caracter(r), idioma_pagina="ro",
            url_guia_docente=url_fds[r["year"]] if f else None,
            tipo_fuente="pdf_compartido" if f else "sin_guia",
            paginas_pdf=f"{f['pag_ini']}-{f['pag_fin']}" if f else None,
        ))

    # ------------------------------------------------ comprobaciones
    codes = [e.codigo_asignatura for e in entries]
    if len(codes) != len(set(codes)):
        raise RuntimeError(f"Codigos duplicados: {[c for c, n in Counter(codes).items() if n > 1]}")
    oblig = sum(e.creditos_ects for e in entries if e.caracter in ("obligatoria", "practicas", "tfg"))
    seen_groups: set[str] = set()
    opt = 0.0
    for e in entries:
        if e.caracter.startswith("optativa"):
            g = e.caracter.split("grupo ")[1].split(",")[0]
            if g not in seen_groups:
                seen_groups.add(g)
                opt += e.creditos_ects
    facult = sum(e.creditos_ects for e in entries if e.caracter == "facultativa")
    total_required = oblig + opt
    if abs(total_required - 240) > 0.01:
        raise RuntimeError(f"ECTS obligatorios+optativos = {total_required}, se esperaban 240")

    notas = (
        f"{len(entries)} asignaturas del plan, {len(entries) - len(sin_ficha)} con ficha; sin ficha en el "
        f"dossier (sin_guia): {', '.join(sin_ficha) or 'ninguna'}. ECTS: obligatorias (DI, incl. practicas y "
        f"proyecto de diploma) {oblig:g} + optativas (DO, 1 por grupo, {len(seen_groups)} grupos) {opt:g} = "
        f"{total_required:g} = total del plan (240). Las facultativas (DL: modulo pedagogico, idiomas, etc.) "
        f"suman {facult:g} ECTS adicionales fuera de los 240. El examen de diploma (10 ECTS) se anade a los 240 y "
        "no tiene ficha. Ano academico de las fichas: 2025-2026 (dossier de reacreditacion ARACIS 'PSUL'). "
        "Los PDF de fichas tienen la mayor parte del texto con diacriticos dibujado como contornos vectoriales "
        "(sin capa de texto): el scraper necesita OCR (ver notas_descubrimiento.md). "
        f"Codigo de ficha distinto del plan (erratas en la ficha; se usa el del plan): {'; '.join(mismatches) or 'ninguno'}."
    )
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor",
        curso_academico=CURSO, url_plan_estudios=url_plan, ects_totales_plan=240.0,
        estrategia_fuente=("API JSON de WordPress (media search) para localizar el plan 2025-2026 (PDF, tablas con "
                           "pdfplumber) + pagina HTML del dossier PSUL con 4 PDF compartidos de fichas (uno por ano); "
                           "rango de paginas por la cabecera '2.1.2 Codul disciplinei'."),
        generado_por="discover_tuiasi.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok", notas=notas,
    )
    cat = Catalog(meta=meta, asignaturas=entries)
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(entries)} asignaturas -> {out}")
    print(notas)
    print(f"HTTP: {http.stats}")


if __name__ == "__main__":
    main()
