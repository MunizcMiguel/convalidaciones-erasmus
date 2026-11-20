#!/usr/bin/env python3
"""Fase 2 · Scraper — Comenius University Bratislava (FMFI), Bachelor Applied Informatics.

Una ficha = rango de páginas del PDF compartido AIS2 (paginas_pdf del catálogo). El texto se
convierte a Markdown con una sección por etiqueta («Course requirements:», «Learning outcomes:»,
«Class syllabus:», «Recommended literature:»…). Se omiten «Lecturers», «Approved by», «Last change»,
«Strana: n» y los encabezados repetidos de cada página.

Uso: python universidades/ec_sk_bratisl02/scraper_ec_sk_bratisl02.py --sample 5 | --all | --codes C1 C2
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_sk_bratisl02"
SAMPLE = [
    "FMFI.KAI/1-AIN-245/22",    # 3D technologies — 2 págs.
    "FMFI.KEF/1-AIN-140/22",    # Computer Principles - Hardware
    "FMFI.KAI/1-AIN-955/15",    # State exam
    "FMFI.KAI/1-AIN-991/15",    # BSc thesis defence
    "FMFI.KDMFI/1-AIN-168/22",  # Web Applications in Praxis
]

SECTIONS = {  # etiqueta -> (título, bloque)
    "Educational activities": ("Educational activities", None),
    "Prerequisites": ("Prerequisites", "prerequisites"),
    "Course requirements": ("Course requirements (assessment)", "assessment"),
    "Learning outcomes": ("Learning outcomes", "learning_outcomes"),
    "Class syllabus": ("Class syllabus", "contents"),
    "State exam syllabus": ("State exam syllabus", "contents"),
    "Recommended literature": ("Recommended literature", "bibliography"),
    "Languages necessary to complete the course": ("Languages", None),
    "Notes": ("Notes", None),
    "Past grade distribution": ("Past grade distribution", None),
}
DROP = re.compile(r"^(Lecturers:|Approved by:|Last change:|Strana:|Academic year:|University:|Faculty:|Course ID:|Total number of evaluated|COURSE DESCRIPTION|STATE EXAM DESCRIPTION|Scale of assessment|Indicative rating)", re.I)
INFO = re.compile(r"^(Type of activities|Number of hours|per week|Form of the course|Number of credits|Recommended semester|Educational level|Exam|Scale of assessment|Indicative rating scale)\b[^\n]*", re.I)


def build(text: str, e: dict) -> tuple[str, dict]:
    found = {b: False for b in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    lines = text.split("\n")
    out = [f"# {e['nombre_asignatura']} ({e['codigo_asignatura']})", ""]
    info, body = [], []
    cur = None
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("A B C D E FX") or re.fullmatch(r"[\d,.\s]+", s):
            continue
        if re.match(r"^(Course ID|Course title):", s) or s.startswith("FMFI.") and s.endswith(e["nombre_asignatura"]):
            continue
        key = s.rstrip(":")
        if s.endswith(":") and key in SECTIONS:
            title, blk = SECTIONS[key]
            cur = key
            body.append(f"\n## {title}\n")
            continue
        if DROP.match(s):
            if s.startswith(("Scale of assessment", "Indicative rating")):
                body.append(s)       # forman parte de la evaluación
            continue
        if INFO.match(s) and cur in (None, "Educational activities"):
            info.append(f"- {s}")
            continue
        if cur is None and s.startswith("Past grade"):
            continue
        body.append(s)
    out += ["## General information", ""] + info + [""] + body
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    md = re.sub(r"^## [^\n]+\n+(?=## |\Z)", "", md, flags=re.M)      # secciones vacías en la ficha
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    for key, (title, blk) in SECTIONS.items():
        if blk and re.search(rf"^## {re.escape(title)}\n+\S", md, re.M):
            sec = re.search(rf"^## {re.escape(title)}\n+((?:(?!^## ).*\n?)*)", md, re.M)
            if sec and len(sec.group(1).strip()) > 0:
                found[blk] = True
    return md, found


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    codes = list(rows) if a.all else a.codes or SAMPLE[: a.sample or 5]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    cache: dict[str, list[str]] = {}
    failed = 0
    for c in codes:
        e = rows.get(c)
        if e is None:
            print(f"{c}: FAIL no está en el catálogo")
            failed += 1
            continue
        try:
            url = e["url_guia_docente"]
            if url not in cache:
                with pdfplumber.open(http.get_file(url)) as d:
                    cache[url] = [(p.extract_text() or "") for p in d.pages]
            ini, fin = (int(x) for x in e["paginas_pdf"].split("-"))
            md, found = build("\n".join(cache[url][ini - 1:fin]), e)
            p = write_markdown(SLUG, e, md, found)
            miss = [k for k, v in found.items() if not v]
            print(f"{c}: ok {len(md)} chars -> {p.name}" + (f" | faltan: {', '.join(miss)}" if miss else ""))
        except (FetchError, ValueError) as ex:
            print(f"{c}: FAIL {type(ex).__name__}: {ex}")
            failed += 1
    print("HTTP:", http.stats)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
