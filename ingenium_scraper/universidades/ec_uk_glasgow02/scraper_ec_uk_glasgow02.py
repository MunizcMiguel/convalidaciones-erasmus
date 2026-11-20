"""Fase 2 - Strathclyde Mechanical & Aerospace Eng.: Module Description Form (PDF por modulo) -> raw_markdown/{codigo}.md
Uso: python universidades/ec_uk_glasgow02/scraper_ec_uk_glasgow02.py [--sample N | --all | --codes C1 C2]
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

HERE = Path(__file__).parent
SLUG = "ec_uk_glasgow02"
SAMPLE = ["MM117", "16232", "ME214", "ME409", "ME301"]
H2 = ["Module Format and Delivery", "Educational Aim", "Learning Outcomes", "Syllabus", "Assessment of Learning Outcomes", "Principles of Assessment and Feedback",
      "Standard Assessment Method(s) Including Percentage Breakdown and Duration of Exams", "Coursework / Submissions deadlines", "Resit Assessment Procedures",
      "Recommended Reading", "Additional Student Feedback"]


def to_markdown(text: str, code: str) -> tuple[str, dict]:
    lines = text.split("\n")
    title = next((l.strip() for l in lines if l.strip().startswith(code + " ")), code)
    head = "\n".join(lines[:14])
    facts = []
    for label, pat in (("Credit weighting (SCQF)", r"Credit Weighting: (\d+)"), ("ECTS", r"\(ECTS (\d+(?:\.\d+)?)\)"), ("Semester", r"Semester: ([^\n]+?)(?:\n|$)"), ("Level", r"Level: (\d)")):
        m = re.search(pat, head)
        if m:
            facts.append(f"- {label}: {m.group(1).strip()}")
    pre = re.search(r"Assumed Prerequisites: (.*?)(?:Academic Suitable|\n[A-Z][a-z]+ [A-Za-z]+:|$)", head, re.S)
    pre_txt = re.sub(r"\s+", " ", re.sub(r"\(BME Compulsory module[^)]*", "", pre.group(1))).strip() if pre else ""
    body_start = next((i for i, l in enumerate(lines) if l.strip().startswith("Module Format and Delivery")), 0)
    body = []
    for l in lines[body_start:]:
        s = l.rstrip()
        if s.strip().startswith(("MODULE TIMETABLE", "Session: 20", "Approved:", "Programme Lead")):
            break
        h = next((x for x in H2 if s.strip().startswith(x)), None)
        body.append(("\n## " + s.strip() + "\n") if h else s)
    md = f"# {title}\n\n" + "\n".join(facts) + (f"\n\n## Assumed prerequisites\n\n{pre_txt}" if pre_txt else "") + "\n\n" + "\n".join(body)
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    low = md.lower()
    found = {"contents": "## syllabus" in low, "learning_outcomes": "## learning outcomes" in low or "## educational aim" in low,
             "assessment": "## standard assessment" in low or "## assessment of learning" in low, "bibliography": "## recommended reading" in low and len(low.split("## recommended reading")[1].strip()) > 60,
             "prerequisites": bool(pre_txt) and pre_txt.lower() not in ("none", "n/a")}
    return md, found


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
        sel = [e for e in cat if e["codigo_asignatura"] in SAMPLE][: a.sample if a.sample is not None else 5]
    c = PoliteClient(cache_dir=HERE / "raw_cache", timeout=40, max_retries=1)
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"], "sin_guia")
            continue
        try:
            with pdfplumber.open(c.get_file(e["url_guia_docente"])) as pdf:
                text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
            body, found = to_markdown(text, e["codigo_asignatura"])
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, str(ex)[:90])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
