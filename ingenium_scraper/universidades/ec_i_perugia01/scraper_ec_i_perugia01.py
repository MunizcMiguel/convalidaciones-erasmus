#!/usr/bin/env python3
"""Fase 2 · Scraper — Università di Perugia, Ingegneria Meccanica (L-9).

Por asignatura, 1 GET a la ficha HTML de www.unipg.it (tabla th/td). Se convierte cada fila en una
sección; se omiten Docente responsabile / Docenti / Ore (nombres) y 'Altre informazioni' se limpia de
contactos. Idioma: el de la ficha (italiano casi siempre).

Uso (desde la raíz del proyecto):
    python universidades/ec_i_perugia01/scraper_ec_i_perugia01.py --sample 5
    python universidades/ec_i_perugia01/scraper_ec_i_perugia01.py --codes GP004941
    python universidades/ec_i_perugia01/scraper_ec_i_perugia01.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString, Tag  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_perugia01"

SAMPLE = [
    "GP004936",   # Matematica I — año 1, matemáticas
    "A005617",    # Meccanica applicata alle macchine — año 2, núcleo mecánico
    "A005615",    # Meccanica razionale — año 2
    "A005623",    # Costruzioni di macchine — año 3
    "A005690_436013",  # Fondamenti di automatica e controlli — año 3, optativa (código con sufijo)
    "A005627",    # Misure meccaniche — año 3
]

# fila -> (título, bloque o None)
SECTIONS = [
    ("Lingua insegnamento", "Teaching language", None),
    ("Contenuti", "Contents", "contents"),
    ("Obiettivi formativi", "Learning objectives", "learning_outcomes"),
    ("Prerequisiti", "Prerequisites", "prerequisites"),
    ("Metodi didattici", "Teaching methods", None),
    ("Modalità di verifica dell'apprendimento", "Assessment methods", "assessment"),
    ("Testi di riferimento", "Reference texts", "bibliography"),
    ("Programma esteso", "Extended programme", "contents"),
    ("Altre informazioni", "Other information", None),
]
META_ROWS = ["Curriculum", "CFU", "Regolamento", "Erogato", "Attività", "Ambito", "Settore", "Anno", "Periodo",
             "Tipo insegnamento", "Tipo attività"]
SKIP = re.compile(r"(?i)(docent|ore$|ricevimento|e-?mail|posta elettronica|contatt)")
PII_LINE = re.compile(r"(?i)^\s*(orario di ricevimento|ricevimento|e-?mail\s*:|contatti|"
                      r".*(office hours|previo appuntamento|posta elettronica|indirizzo di posta|"
                      r"può essere contattato|si prega di contattare|contattare il docente|recapiti|\[email\])).*$")


def td_md(td: Tag) -> str:
    """Celda -> Markdown: <br> -> salto de línea, <li> -> lista."""
    for br in td.find_all("br"):
        br.replace_with(NavigableString("\n"))
    for li in td.find_all("li"):
        li.insert_before(NavigableString("\n- "))
        li.unwrap()
    for ul in td.find_all(["ul", "ol"]):
        ul.unwrap()
    txt = td.get_text()
    lines = [re.sub(r"[ \t ]+", " ", ln).strip() for ln in txt.split("\n")]
    lines = [ln for ln in lines if ln and not PII_LINE.match(ln)]
    return "\n".join(lines).strip()


def table_rows(t: Tag) -> dict[str, Tag]:
    rows: dict[str, Tag] = {}
    for tr in t.select("tr"):
        th, td = tr.find("th"), tr.find("td")
        if th and td:
            rows.setdefault(th.get_text(" ", strip=True), td)
    return rows


def sections_md(rows: dict[str, Tag], level: str, found: dict[str, bool], meta: bool) -> list[str]:
    out: list[str] = []
    if meta:
        out += [f"{level} Informazioni generali", ""]
        for k in META_ROWS:
            if k in rows:
                v = re.sub(r"\s+", " ", rows[k].get_text(" ", strip=True))
                if v:
                    out.append(f"- **{k}:** {v}")
    else:
        for k in ("CFU", "Attività", "Settore", "Periodo"):
            if k in rows:
                v = re.sub(r"\s+", " ", rows[k].get_text(" ", strip=True))
                if v:
                    out.append(f"- **{k}:** {v}")
    for key, _title, block in SECTIONS:
        td = rows.get(key)
        if td is None:
            continue
        md = td_md(td)
        if not md:
            continue
        if block:
            found[block] = True
        out += ["", f"{level} {key}", "", md]
    known = {k for k, _, _ in SECTIONS} | set(META_ROWS) | {"Nome del corso di laurea", "Codice insegnamento", "Codice"}
    for k, td in rows.items():                      # nunca perder una fila con texto
        if k in known or SKIP.search(k) or k == "Erogato altro regolamento":
            continue
        md = td_md(td)
        if md:
            out += ["", f"{level} {k}", "", md]
    return out


def build_markdown(html: str, entry: dict) -> tuple[str, dict[str, bool]]:
    soup = BeautifulSoup(html, "lxml")
    tables = [t for t in soup.find_all("table") if t.find("th")]
    main = next((table_rows(t) for t in tables if t.find("th", string=re.compile("Nome del corso"))), {})
    mods = []
    for t in tables:
        rows = table_rows(t)
        if "Nome del corso di laurea" in rows or not rows:
            continue
        prev = t.find_previous(["h2", "h3", "h4", "h5"])
        mods.append((prev.get_text(" ", strip=True) if prev else "Modulo", rows))
    content_keys = ("Contenuti", "Obiettivi formativi", "Programma esteso", "Testi di riferimento")
    if not any(k in main for k in content_keys) and not any(any(k in r for k in content_keys) for _, r in mods):
        raise ValueError("ficha sin contenido")
    found = {"contents": False, "learning_outcomes": False, "assessment": False,
             "bibliography": False, "prerequisites": False}
    out = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", "", f"- **Corso di laurea:** {entry['nombre_grado']}"]
    out += sections_md(main, "##", found, True)
    for title, rows in mods:
        if not any(rows.get(k) is not None and td_md(rows[k]) for k in content_keys):
            continue
        out += ["", f"## Modulo: {title}", ""] + sections_md(rows, "###", found, False)
    return "\n".join(out).strip() + "\n", found


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--sample", type=int, default=None)
    grp.add_argument("--all", action="store_true")
    grp.add_argument("--codes", nargs="+")
    args = ap.parse_args()
    cat = load_catalog(SLUG)
    if cat is None:
        print("Falta catalogo_urls.json: ejecuta discover_ec_i_perugia01.py", file=sys.stderr)
        return 2
    rows = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    codes = list(rows) if args.all else (args.codes or SAMPLE[: args.sample or 5])
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    failed = 0
    for code in codes:
        e = rows.get(code)
        if e is None:
            print(f"{code}: FAIL no está en el catálogo")
            failed += 1
            continue
        if e["tipo_fuente"] == "sin_guia":
            print(f"{code}: skip sin_guia")
            continue
        try:
            md, found = build_markdown(http.get_text(e["url_guia_docente"]), e)
            p = write_markdown(SLUG, e, md, found)
            miss = [k for k, v in found.items() if not v]
            print(f"{code}: ok [{e['idioma_pagina']}] {len(md)} chars -> {p.name}"
                  + (f" | faltan: {', '.join(miss)}" if miss else ""))
        except (FetchError, ValueError) as ex:
            print(f"{code}: FAIL {type(ex).__name__}: {ex}")
            failed += 1
    print("HTTP:", http.stats)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
