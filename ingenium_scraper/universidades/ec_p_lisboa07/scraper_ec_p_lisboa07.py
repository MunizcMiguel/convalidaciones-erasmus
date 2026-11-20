"""Fase 2 - ISCTE LETI: modal de cada UC en la pagina del grado -> raw_markdown/{codigo}.md
Uso: python universidades/ec_p_lisboa07/scraper_ec_p_lisboa07.py [--sample N | --all | --codes C1 C2]
"""
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
SLUG = "ec_p_lisboa07"
SAMPLE_NAMES = ["Calculus I", "Circuit Theory", "Operating Systems", "Artificial Intelligence", "Random Signals in Telecommunications and Computer Engineering"]
SECTIONS = [("objectives", "Objectives (learning outcomes)"), ("programme", "Programme (contents)"), ("evaluation", "Evaluation (assessment)"), ("bibliography", "Bibliography")]


def pane_md(p) -> str:
    for br in p.find_all("br"):
        br.replace_with("\n")
    for li in p.find_all("li"):
        li.insert_before("- ")
    t = p.get_text("\n").replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = cat["asignaturas"] if isinstance(cat, dict) else cat.asignaturas
    rows = [r if isinstance(r, dict) else r.model_dump() for r in rows]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        rows = [r for r in rows if r["nombre_asignatura"] in SAMPLE_NAMES][: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(http.get_text(rows[0]["url_guia_docente"].split("#")[0]), "lxml")
    fail = 0
    for r in rows:
        mid = r["url_guia_docente"].split("#")[1]
        m = s.find(id=mid)
        if m is None:
            print("FAIL", r["codigo_asignatura"], "sin modal"); fail += 1; continue
        md, found = [f"# {r['nombre_asignatura']}", f"ECTS: {r['creditos_ects']:g} · Year {r['curso']} · Semester {r['semestre']}"], {}
        for key, title in SECTIONS:
            p = m.find(id=f"{key}-tab-pane-{mid.split('-')[-1]}")
            t = pane_md(p) if p else ""
            if t:
                md.append(f"## {title}\n\n{t}")
            found[key] = bool(t)
        blocks = {"contents": found["programme"], "learning_outcomes": found["objectives"], "assessment": found["evaluation"], "bibliography": found["bibliography"], "prerequisites": False}
        write_markdown(SLUG, r, "\n\n".join(md), blocks)
        print("ok", r["codigo_asignatura"], {k: v for k, v in blocks.items() if not v} or "")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
