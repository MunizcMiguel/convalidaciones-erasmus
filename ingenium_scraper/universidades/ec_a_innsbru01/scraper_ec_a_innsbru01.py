"""Fase 2 - Innsbruck Mechatronik: cada modulo del Curriculum (PDF compartido, texto) -> Markdown.

Uso: python universidades/ec_a_innsbru01/scraper_ec_a_innsbru01.py [--sample N | --all | --codes C1 C2]
Solo hay descripcion a nivel de modulo (lecciones con contenido breve + Lernziele + requisitos de inscripcion). Sin profesorado en la fuente.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from discover_ec_a_innsbru01 import modules, page_lines, pdf_url  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_a_innsbru01"
SAMPLE = ["P8", "P1", "P18", "P24", "P25-A1", "W3"]
NL = chr(10)
LERN = re.compile(r"^Lernziele? des Moduls:?$")
ANM = re.compile(r"^Anmeldungsvoraussetzung/en:\s*(.*)$")


def build(entry: dict, block: list[str], body_start: int) -> tuple[str, dict]:
    lv, lernziel, anm = [], [], []
    mode = "lv"
    for l in block[body_start:]:
        s = l.strip()
        if not s or s in ("UMIT", "TIROL", "LFUI", "ECTS-", "AP", "LFUI/", "UMIT TIROL"):
            continue
        if LERN.match(s):
            mode = "lz"
            continue
        m = ANM.match(s)
        if m:
            mode = "anm"
            anm.append(m.group(1))
            continue
        {"lv": lv, "lz": lernziel, "anm": anm}[mode].append(s)
    body = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", "", f"ECTS-AP (Curriculum): {entry['creditos_ects']}", ""]
    body += ["## Lehrveranstaltungen und Inhalte (Curriculum)", "", *lv, ""]
    body += ["## Lernziele des Moduls", "", *(lernziel or ["-"]), ""]
    body += ["## Anmeldungsvoraussetzungen", "", *(anm or ["-"]), ""]
    found = {"contents": bool(lv), "learning_outcomes": bool(lernziel), "assessment": False, "bibliography": False,
             "prerequisites": bool(anm) and not re.fullmatch(r"keine[.]?", " ".join(anm).strip(), re.I)}
    return NL.join(body), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    codes = a.codes or (list(rows) if a.all else [c for c in SAMPLE if c in rows][: a.sample])
    client = PoliteClient(cache_dir=HERE / "raw_cache")
    with pdfplumber.open(client.get_file(pdf_url(client))) as pdf:
        lines = page_lines(pdf)
    heads, e7 = modules(lines)
    by_code = {}
    maxnum = max(int(h["num"]) for h in heads if h["kind"] == "Pflichtmodul" and not h["spec"] and h["num"])
    for n, h in enumerate(heads):
        end = heads[n + 1]["idx"] if n + 1 < len(heads) else e7
        if h["kind"] == "Pflichtmodul":
            code = f"P{h['num']}" if not h["spec"] else f"P{maxnum + 1}-{h['spec']}"
        else:
            code = "W1" if (not h["spec"] and h["num"] == "1") else (f"W2-{h['spec']}" if h["spec"] else "W3")
        by_code[code] = ([t for _, t in lines[h["idx"]:end]], h["body"] - h["idx"])
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in by_code:
            print(f"SKIP {c}")
            continue
        try:
            md, found = build(r, *by_code[c])
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} sin: {[k for k, v in found.items() if not v]}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
