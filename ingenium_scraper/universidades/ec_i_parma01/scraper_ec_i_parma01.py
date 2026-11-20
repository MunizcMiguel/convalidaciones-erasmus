"""Fase 2 - Parma: convierte las fichas previamente descargadas (fuente_previa/unipr_fichas.json) a Markdown.

No hace peticiones de red: corsi.unipr.it devuelve 405 a PoliteClient. Uso: [--sample N | --all | --codes C1 ...]
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
SLUG = "ec_i_parma01"
ORDER = ["Learning objectives", "Prerequisites", "Course unit content", "Full programme", "Teaching methods",
         "Assessment methods and criteria", "Bibliography"]


def fmt(text: str) -> str:
    t = text.replace("\r", "")
    t = re.sub(r"\s*[•●]\s*", "\n- ", t)
    return re.sub(r"[ \t]+\n", "\n", t).strip()


def build(entry: dict, ficha: dict) -> tuple[str, dict]:
    sec = ficha["sections"]
    body = [f"# {entry['nombre_asignatura']}", ""]
    for k in ("discipline", "hours", "credits", "language", "semester_info"):
        if ficha.get(k):
            body.append(f"- {k.replace('_', ' ').capitalize()}: {ficha[k]}")
    for k in ORDER:
        v = sec.get(k, "").strip()
        if v:
            body += ["", f"## {k}", "", fmt(v)]
    blocks = {"contents": bool(sec.get("Course unit content", "").strip() or sec.get("Full programme", "").strip()),
              "learning_outcomes": bool(sec.get("Learning objectives", "").strip()),
              "assessment": bool(sec.get("Assessment methods and criteria", "").strip()),
              "bibliography": bool(sec.get("Bibliography", "").strip()),
              "prerequisites": bool(sec.get("Prerequisites", "").strip())}
    return "\n".join(body), blocks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"] if r["tipo_fuente"] != "sin_guia"}
    fichas = json.loads((HERE / "fuente_previa" / "unipr_fichas.json").read_text(encoding="utf-8"))
    if a.codes:
        codes = a.codes
    elif a.all:
        codes = list(rows)
    else:  # diverso y fijo: cursos 1, 2 y 3 (ordenados por codigo)
        by: dict = {}
        for c, r in rows.items():
            by.setdefault(r["curso"], []).append(c)
        codes = [by[1][0], by[2][0], by[2][-1], by[3][0], by[3][-1]][: a.sample]
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r:
            print(f"SKIP {c}")
            continue
        try:
            fid = r["url_guia_docente"].rsplit("/", 1)[1]
            md, blocks = build(r, fichas[fid])
            write_markdown(SLUG, r, md, blocks)
            print(f"ok {c} {r['nombre_asignatura'][:40]} {len(md)} {blocks}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
