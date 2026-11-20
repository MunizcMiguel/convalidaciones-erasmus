"""Fase 2 - FEUP: convierte las fichas SIGARRA previamente descargadas (fuente_previa/feup_fichas.json) a Markdown.

Sin red (SIGARRA devuelve 403 a PoliteClient). Uso: [--sample N | --all | --codes C1 ...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_p_porto02"
SAMPLE = ["L.EM005", "L.EM014", "L.EM018", "L.EM031", "CTLGE01"]
ORDER = ["Objectives", "Learning outcomes and competences", "Pre-requirements (prior knowledge) and co-requirements (common knowledge)",
         "Program", "Working method", "Teaching methods and learning activities", "Evaluation Type", "Assessment Components",
         "Calculation formula of final grade", "Eligibility for exams", "Examinations or Special Assignments", "Internship work/project",
         "Special assessment (TE, DA, ...)", "Classification improvement", "Amount of time allocated to each course unit",
         "Mandatory literature", "Complementary Bibliography", "Comments from the literature", "Software", "keywords", "Observations"]
PRE = ORDER[2]


def build(entry: dict, ficha: dict) -> tuple[str, dict]:
    sec = ficha["sections"]
    body = [f"# {entry['nombre_asignatura']}", "", f"- Teaching language: {sec.get('Teaching language', 'n/d')}",
            f"- Edition: {ficha.get('instance') or 'n/d'}"]
    for k in ORDER:
        v = (sec.get(k) or "").strip()
        if v:
            body += ["", f"## {k}", "", re.sub(r"[ \t]+", " ", v)]
    has = lambda *ks: any((sec.get(k) or "").strip() for k in ks)  # noqa: E731
    return "\n".join(body), {
        "contents": has("Program"), "learning_outcomes": has("Learning outcomes and competences", "Objectives"),
        "assessment": has("Assessment Components", "Evaluation Type"),
        "bibliography": has("Mandatory literature", "Complementary Bibliography"), "prerequisites": has(PRE)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"] if r["tipo_fuente"] != "sin_guia"}
    fichas = {f["code"]: f for f in json.loads((HERE / "fuente_previa" / "feup_fichas.json").read_text(encoding="utf-8"))}
    codes = a.codes or (list(rows) if a.all else SAMPLE[: a.sample])
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r:
            print(f"SKIP {c}")
            continue
        try:
            md, blocks = build(r, fichas[c])
            write_markdown(SLUG, r, md, blocks)
            print(f"ok {c} {r['nombre_asignatura'][:40]} {len(md)} {blocks}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
