"""Fase 2 - Pardubice (FEI, Bachelor, courses in English): ficha IS/STAG (portal.upce.cz) -> Markdown.
Uso: python universidades/ec_cz_pardub01/scraper_ec_cz_pardub01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, Tag  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

SLUG = "ec_cz_pardub01"
HERE = Path(__file__).parent
SKIP = ("fields of study", "guarantors and lecturers", "activities")  # personal docente / enlaces; 'Activities' = enlace a Moodle
BLOCKS = {
    "contents": ("content",),
    "learning_outcomes": ("course objectives", "competences acquired"),
    "assessment": ("requirements on student", "assessment methods"),
    "bibliography": ("literature",),
    "prerequisites": ("prerequisites",),
}
HEAD_KEYS = ("Accredited / Credits", "Form of course completion", "Type of completion", "Language of instruction", "Semester taught", "Optional course",
             "Prerequisite courses", "Time requirements")


def clean(s: str) -> str:
    return re.sub(r"[ \t\xa0]+", " ", s).strip()


def cell_text(td: Tag) -> str:
    for br in td.find_all("br"):
        br.replace_with("\n")
    lines = [clean(x) for x in td.get_text().splitlines()]
    return "\n".join(x for x in lines if x)


def inner_table_md(t: Tag) -> str:
    rows = [[clean(c.get_text(" ", strip=True)) for c in tr.find_all(["td", "th"])] for tr in t.find_all("tr")]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    w = max(map(len, rows))
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def to_markdown(html: str, entry: dict) -> tuple[str, dict]:
    soup = BeautifulSoup(html, "lxml")
    coat = soup.select_one("div.prohlizeniEntitaSubdetailPanesCoat")
    if coat is None:
        raise ValueError("sin panel de silabo")
    out = [f"# {entry['nombre_asignatura']}"]
    # cabecera: pares th/td de la primera tabla
    info = []
    first = coat.find("table", class_="xg_pane")
    for th in first.find_all("th"):
        k = clean(th.get_text(" ", strip=True))
        if k in HEAD_KEYS and "hideForMobile" not in (th.get("class") or []):
            td = th.find_next("td")
            if td is not None:
                v = " ".join(cell_text(td).split("\n"))
                if v and v != "[HRS/WEEK]":
                    info.append(f"- **{k}**: {v}")
    out.append("\n".join(dict.fromkeys(info)))
    found = {k: False for k in BLOCKS}
    sections: list[tuple[str, list[str]]] = []
    for th in coat.find_all("th", class_="top"):
        row = th.find_parent("tr")
        tds = row.find_all("td", recursive=False)  # variante A: th y td en la misma fila
        if not tds:  # variante B: el contenido va en la fila siguiente
            nxt = row.find_next_sibling("tr")
            tds = nxt.find_all("td", recursive=False) if nxt is not None and nxt.find("th", class_="top", recursive=False) is None else []
        parts = []
        for td in tds:
            inner = td.find("table")
            parts.append(inner_table_md(inner) if inner else cell_text(td))
        sections.append((clean(th.get_text(" ", strip=True)).rstrip(":"), parts))
    for title, parts in sections:
        low = title.lower()
        if low.startswith(SKIP):
            continue
        body = "\n\n".join(x for x in parts if x).strip()
        if not body:
            continue
        out.append(f"## {title}\n\n{body}")
        for k, keys in BLOCKS.items():
            if any(low.startswith(x) for x in keys) and not re.fullmatch(r"(N/A|-|none)\.?", body, re.I):
                found[k] = True
    return "\n\n".join(o for o in out if o), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = [r for r in cat["asignaturas"] if r["tipo_fuente"] != "sin_guia"]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        step = max(1, len(rows) // a.sample)
        rows = rows[::step][: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for r in rows:
        try:
            md, found = to_markdown(http.get_text(r["url_guia_docente"]), r)
            write_markdown(SLUG, r, md, found)
            print(f"ok   {r['codigo_asignatura']} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {r['codigo_asignatura']}: {e}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
