"""Fase 2 - UPT Mecanica: fichas (fuente_previa/upt_cursos.json) -> Markdown. Sin red.
Uso: [--sample N | --all | --codes C1 ...]"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_ro_timisoa04"
TITLES = {"Objectives": "Objectives (7. Obiective)", "Lecture Program": "Lecture programme (8.1 Curs)",
          "Practical Program": "Practical programme (8.2 Aplicații)", "Evaluation": "Evaluation (10. Evaluare)"}


def clean(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


def build(entry: dict, c: dict) -> tuple[str, dict]:
    sec = c["sections"]
    h = c["hours"]
    body = [f"# {entry['nombre_asignatura']}", "", f"- Year {c['year']}, semester {c['semester']}, {c['ects']:g} ECTS",
            f"- Hours: course {h['course']}, seminar {h['seminar']}, laboratory {h['lab']}, project {h['project']}",
            f"- Teaching language: {c['teaching_language'] or 'n/a'}"]
    for k, title in TITLES.items():
        v = clean(sec.get(k) or "")
        if k in ("Lecture Program", "Practical Program"):
            v = re.sub(r"\s*Bibliografie\s+", "\n\n**Bibliografie:** ", v)
        if v:
            body += ["", f"## {title}", "", v]
    has = lambda k: bool(clean(sec.get(k) or ""))  # noqa: E731
    biblio = "Bibliografie" in (sec.get("Lecture Program") or "") or "Bibliografie" in (sec.get("Practical Program") or "")
    blocks = {"contents": has("Lecture Program") or has("Practical Program"), "learning_outcomes": has("Objectives"),
              "assessment": has("Evaluation"), "bibliography": biblio, "prerequisites": False}
    return "\n".join(body), blocks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"] if r["tipo_fuente"] != "sin_guia"}
    cursos = json.loads((HERE / "fuente_previa" / "upt_cursos.json").read_text(encoding="utf-8"))
    byname = {(c["code"], c["name"].strip().lower()): c for c in cursos}
    if a.codes:
        codes = a.codes
    elif a.all:
        codes = list(rows)
    else:
        byyear: dict = {}
        for c, r in rows.items():
            byyear.setdefault(r["curso"], []).append(c)
        codes = [byyear[1][0], byyear[2][0], byyear[3][-1], byyear[4][0], byyear[4][-1]][: a.sample]
    fails = 0
    for code in codes:
        r = rows.get(code)
        if not r:
            print(f"SKIP {code}")
            continue
        try:
            nm = r["nombre_asignatura"].lower()
            c = byname.get((code, nm)) or byname[(re.sub(r"-[0-9a-f]{4}$", "", code), nm)]
            md, blocks = build(r, c)
            write_markdown(SLUG, r, md, blocks)
            print(f"ok {code} {r['nombre_asignatura'][:40]} {len(md)} {blocks}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {code}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
