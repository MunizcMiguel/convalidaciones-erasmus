"""Fase 2 - Radom (UTH Rad) Mechanical Engineering: syllabus PDF dentro de un ZIP -> raw_markdown/{codigo}.md
Uso: python universidades/ec_pl_radom01/scraper_ec_pl_radom01.py [--sample N | --all | --codes C1 C2]
El ZIP se descarga una vez con PoliteClient (cache) y se leen los miembros en memoria.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_radom01"
SAMPLE = ["A3", "B11", "C4a", "B19", "H02"]
DROP_PREFIX = ("Coordinator", "E-mail address, phone number", "The website of the basic organizational unit")
HEADINGS = {
    "Course description": "## Course description",
    "LEARNING OUTCOMES, CURRICULUM CONTENT": "## Learning outcomes, curriculum content",
    "Literature and teaching aids": "## Literature and teaching aids",
    "Student workload required": "## Student workload (ECTS balance)",
    "Additional information, comments": "## Additional information",
}
BOILER = re.compile(r"In the case of students with special needs.*", re.S)


def table_md(rows: list[list[str]]) -> str:
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def to_markdown(data: bytes, title: str) -> tuple[str, dict]:
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        text = "\n".join(p.extract_text(x_tolerance=1.5) or "" for p in pdf.pages)
        outc = []
        for p in pdf.pages:
            for t in p.extract_tables():
                for r in t:
                    c = [re.sub(r"\s+", " ", (x or "")).strip() for x in r]
                    if re.fullmatch(r"[WUK]\d+", c[0] if c else "") and len([x for x in c if x]) >= 3:
                        outc.append([x for x in c])
    lines = []
    for l in text.splitlines():
        l = l.strip()
        if not l or re.fullmatch(r"[A-Za-z]", l) or re.fullmatch(r"\d{1,2}", l) or l.startswith(DROP_PREFIX) or "@" in l or l.startswith("http://wm.uniwersytetradom"):
            continue
        lines.append(l)
    body = "\n".join(lines)
    # tabla de resultados de aprendizaje: sustituye el texto entrelazado por la tabla extraida
    if outc:
        hdr = ["No.", "Learning outcome (student knows/can/is ready to)", "Field-of-study outcome", "Class type", "Form of verification", "Assessment method"]
        w = len(hdr)
        rows = [hdr] + [(r + [""] * w)[:w] for r in outc]
        a = body.find("Learning outcomes for the course in relation")
        b = body.find("Literature and teaching aids")
        if a >= 0 and b > a:
            body = body[:a] + "### Learning outcomes and verification\n\n" + table_md(rows) + "\n\n" + body[b:]
    body = BOILER.sub("", body).rstrip()
    for k, v in HEADINGS.items():
        body = re.sub(r"(?m)^" + re.escape(k) + r".*$", v if k != "LEARNING OUTCOMES, CURRICULUM CONTENT" else v, body, count=1)
    body = re.sub(r"(?m)^(Primary literature:|Additional literature:|Study aids:)", r"### \1", body)
    body = re.sub(r"(?m)^(Learning Objective:|Curriculum Content:|Didactic \(educational\) methods:)", r"### \1", body)
    body = re.sub(r"(?m)^VERIFICATION OF\s*$\n^LEARNING OUTCOMES\s*$", "", body)
    body = "# " + title + "\n\n" + body
    low = body.lower()
    found = {
        "contents": "curriculum content" in low,
        "learning_outcomes": "learning outcome" in low and bool(outc) or "learning objective" in low,
        "assessment": "course assessment type" in low or "verification" in low,
        "bibliography": "primary literature" in low or "literature and teaching aids" in low,
        "prerequisites": "prerequisites" in low,
    }
    return body, found


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
        sel = [e for e in cat if e["codigo_asignatura"] in SAMPLE][: (a.sample if a.sample is not None else 5)]
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    zips: dict[str, zipfile.ZipFile] = {}
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"], "sin_guia")
            continue
        try:
            zurl, member = e["url_guia_docente"].split("#", 1)
            if zurl not in zips:
                zips[zurl] = zipfile.ZipFile(c.get_file(zurl))
            body, found = to_markdown(zips[zurl].read(member), e["nombre_asignatura"])
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
