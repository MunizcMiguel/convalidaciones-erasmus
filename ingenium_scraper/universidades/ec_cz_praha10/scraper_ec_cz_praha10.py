"""Fase 2 - ČVUT FS (Bílá kniha): ficha HTML -> raw_markdown/{codigo}.md. Uso: [--sample N | --all | --codes C1 C2]"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_cz_praha10"
SAMPLE = ["E374007", "E151717", "E181135", "E021026", "E341004"]
KEEP = {"Synopsis:": "Synopsis", "Requirements:": "Requirements / prerequisites", "Syllabus of lectures:": "Syllabus of lectures",
        "Syllabus of tutorials:": "Syllabus of tutorials", "Study Objective:": "Study objective (learning outcomes)",
        "Study materials:": "Study materials (bibliography)", "Note:": "Note"}


def clean(node) -> str:
    for br in node.find_all("br"):
        br.replace_with("\n")
    for li in node.find_all("li"):
        li.insert_before("\n- ")
    lines = [re.sub(r"[ \t\xa0]+", " ", l).strip() for l in node.get_text().split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def to_markdown(html: str, title: str, e: dict) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    md = ["# " + title, f"- Code: {e['codigo_asignatura']}\n- ECTS: {e.get('creditos_ects')}"]
    got = {}
    for dt, dd in zip(s.select("dl dt"), s.select("dl dd")):
        k = dt.get_text(strip=True)
        if k in KEEP:
            t = clean(dd)
            if t:
                got[k] = True
                md.append("## " + KEEP[k] + "\n\n" + t)
    if not got:
        raise ValueError("ficha vacía")
    found = {"contents": "Synopsis:" in got or "Syllabus of lectures:" in got, "learning_outcomes": "Study Objective:" in got,
             "assessment": False, "bibliography": "Study materials:" in got, "prerequisites": "Requirements:" in got}
    return "\n\n".join(md), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)["asignaturas"]
    if a.codes:
        sel = [e for e in cat if e["codigo_asignatura"] in a.codes]
    elif a.all:
        sel = cat
    else:
        sel = [e for e in cat if e["codigo_asignatura"] in SAMPLE][: a.sample or 5]
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"])
            continue
        try:
            body, found = to_markdown(c.get_text(e["url_guia_docente"]), e["nombre_asignatura"], e)
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body))
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
