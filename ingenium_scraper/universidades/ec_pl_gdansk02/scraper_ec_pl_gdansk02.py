"""Fase 2 - Gdansk Tech (Mechanical Engineering): ficha PDF de asignatura (ects.pg.edu.pl) -> Markdown.
Uso: python universidades/ec_pl_gdansk02/scraper_ec_pl_gdansk02.py [--sample N | --all | --codes C1 C2]
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

SLUG = "ec_pl_gdansk02"
HERE = Path(__file__).parent
SECTIONS = [  # (etiqueta al inicio de linea, titulo Markdown, clave de bloque)
    ("Subject objectives", "Subject objectives", None),
    ("Learning outcomes", "Learning outcomes", "learning_outcomes"),
    ("Subject contents", "Subject contents", "contents"),
    ("Prerequisites", "Prerequisites and co-requisites", "prerequisites"),
    ("Assessment methods and criteria", "Assessment methods and criteria", "assessment"),
    ("Recommended reading", "Recommended reading", "bibliography"),
    ("Supplementary literature", "Supplementary literature", None),
    ("eResources addresses", "eResources", None),
    ("Example issues/", "Example issues / questions / tasks", None),
    ("Practical activites within", "Practical activities", None),
]
DROP = re.compile(r"^(Data wygenerowania.*|a \d+ z \d+|Document generated electronically.*|Name and surname Subject supervisor.*|of lecturer \(lecturers\) Teachers.*)$")
SAMPLE_PATTERNS = ["Physics I$", "Mathematics|Calculus", "Strength of Materials|Mechanics", "Thermodynamics|Fluid|Machine Design", "Diploma|Thesis|Bachelor"]


def card_text(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    text = re.sub(r"Prerequisites\s*\nand co-requisites", "Prerequisites and co-requisites", text)
    text = re.sub(r"Assessment methods ([^\n]*)\nand criteria", r"Assessment methods and criteria \1", text)
    text = re.sub(r"Example issues/ ", "Example issues/ ", text)
    return text


def to_markdown(text: str, entry: dict) -> tuple[str, dict]:
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        if DROP.match(ln) or ln in ("and co-requisites", "the subject", "tasks being completed", "and criteria"):
            continue
        lines.append(re.sub(r"^example questions/\s*", "", ln))
    head, cur, secs, order = [], None, {}, []
    for ln in lines:
        hit = next((s for s in SECTIONS if ln.startswith(s[0])), None)
        if hit:
            cur = hit[0]
            order.append(hit)
            secs[cur] = [ln[len(hit[0]):].strip()]
        elif cur is None:
            head.append(ln)
        else:
            secs[cur].append(ln)
    # cabecera: se conservan solo campos utiles (sin profesorado ni unidad)
    keep = re.compile(r"(Field of study|Education level|Year of study|Semester of study|Language of instruction|ECTS credits|Assessment form|Subject group|Subject name and code|Learning profile)")
    head_md = "\n".join("- " + re.sub(r"\s+", " ", ln).strip() for ln in head if keep.search(ln))
    out = [f"# {entry['nombre_asignatura']}", head_md]
    found = {k: False for k in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    for lab, title, key in order:
        body = "\n".join(x for x in secs[lab] if x).strip()
        out.append(f"## {title}\n\n{body}" if body else f"## {title}")
        if body.startswith("Course outcome Subject outcome Method of verification"):
            body = body[len("Course outcome Subject outcome Method of verification"):].strip()
        if key and body and not re.fullmatch(r"(Not applicable|None|-)\.?", body, re.I):
            found[key] = True
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
        pick, seen = [], set()
        for pat in SAMPLE_PATTERNS:
            for r in rows:
                if re.search(pat, r["nombre_asignatura"], re.I) and r["codigo_asignatura"] not in seen:
                    pick.append(r)
                    seen.add(r["codigo_asignatura"])
                    break
        rows = (pick + [r for r in rows if r["codigo_asignatura"] not in seen])[: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for r in rows:
        try:
            md, found = to_markdown(card_text(http.get_file(r["url_guia_docente"])), r)
            write_markdown(SLUG, r, md, found)
            print(f"ok   {r['codigo_asignatura']} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {r['codigo_asignatura']}: {e}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
