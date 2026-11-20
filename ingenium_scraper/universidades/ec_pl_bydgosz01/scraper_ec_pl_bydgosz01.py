"""Fase 2 - UKW Bydgoszcz (ICT courses in English): silabo PDF de una pagina -> Markdown.
Uso: python universidades/ec_pl_bydgosz01/scraper_ec_pl_bydgosz01.py [--sample N | --all | --codes C1 C2]
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

SLUG = "ec_pl_bydgosz01"
HERE = Path(__file__).parent
# etiqueta (inicio de linea) -> (titulo, clave bloque); None = se descarta (personal docente)
LABELS = [
    ("Title:", "Title", None), ("Lecture hours:", "Hours", None), ("Study period:", "Study period", None),
    ("Number of credits:", "ECTS", None), ("Assessment methods:", "Assessment methods", "assessment"),
    ("Language of", "Language of instruction", None), ("Prerequisites:", "Prerequisites", "prerequisites"),
    ("Course content:", "Course content", "contents"), ("Learning outcomes:", "Learning outcomes", "learning_outcomes"),
    ("Name of lecturer:", None, None), ("Contact", None, None), ("Literature:", "Literature", "bibliography"),
]
STRAY = {"instruction:", "(summer/winter)", "address):", "(email"}


KEYS = {
    "contents": r"course content|course description|content of the course|syllabus|program content|course contents",
    "learning_outcomes": r"learning outcome|goal of|outcomes|learning objective|course objective",
    "assessment": r"assessment|marking|exam|passing|credit conditions|grading",
    "bibliography": r"literature|reading|bibliograph|references|textbook",
    "prerequisites": r"prerequisite",
}
PERSONAL = re.compile(r"(name of lecturer|lecturer|teacher|e-?mail|contact|@)", re.I)


def generic_markdown(text: str, entry: dict) -> tuple[str, dict]:
    """Plantillas heterogeneas (cada docente usa la suya): se conserva el texto sin lineas de profesorado/contacto."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not PERSONAL.search(ln)]
    body = "\n".join(lines)
    low = body.lower()
    found = {k: bool(re.search(rx, low)) for k, rx in KEYS.items()}
    return f"# {entry['nombre_asignatura']}\n\n## Syllabus (original text)\n\n{body}", found


def to_markdown(text: str, entry: dict) -> tuple[str, dict]:
    if not text.lstrip().startswith("Title:"):
        return generic_markdown(text, entry)
    return labelled_markdown(text, entry)


def labelled_markdown(text: str, entry: dict) -> tuple[str, dict]:
    cur, secs, order = None, {}, []
    for ln in text.splitlines():
        ln = ln.strip()
        hit = next((lb for lb in LABELS if ln.startswith(lb[0])), None)
        if hit:
            cur = hit[0]
            order.append(hit)
            secs[cur] = [ln[len(hit[0]):].strip()]
        elif cur is not None and ln.lower() not in STRAY and not ln.lower().startswith("(email"):
            secs[cur].append(ln)
    out = [f"# {entry['nombre_asignatura']}"]
    found = {k: False for k in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    for lab, title, key in order:
        if title is None:
            continue
        body = " ".join(x for x in secs[lab] if x) if lab in ("Title:", "Lecture hours:", "Study period:", "Number of credits:", "Language of", "Assessment methods:") \
            else "\n".join(x for x in secs[lab] if x)
        if lab in ("Title:", "Lecture hours:", "Study period:", "Number of credits:", "Language of"):
            out.append(f"- **{title}**: {body}")
        else:
            out.append(f"## {title}\n\n{body}")
        if key and body.strip() and not re.fullmatch(r"(None|-|n/a)\.?", body.strip(), re.I):
            found[key] = True
    return "\n\n".join(out), found


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
        step = max(1, len(rows) // a.sample)  # diverso: repartido por la lista
        rows = rows[::step][: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for r in rows:
        try:
            with pdfplumber.open(http.get_file(r["url_guia_docente"])) as pdf:
                text = "\n".join((p.extract_text() or "") for p in pdf.pages)
            md, found = to_markdown(text, r)
            write_markdown(SLUG, r, md, found)
            print(f"ok   {r['codigo_asignatura']} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {r['codigo_asignatura']}: {e}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
