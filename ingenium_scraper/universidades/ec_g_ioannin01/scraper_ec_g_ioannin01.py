#!/usr/bin/env python3
"""Fase 2 · Scraper — University of Ioannina, CSE (grado). Fichas «COURSE OUTLINE» en PDF compartidos (core y elective).

Cada ficha es un rango de páginas (paginas_pdf). El texto sigue la plantilla del Ministerio griego con
instrucciones («Add rows if necessary…», «Description of the evaluation procedure…»). Las líneas de
plantilla se detectan de forma determinista: una línea que aparece en >= 70 % de las fichas de un PDF es
plantilla y se elimina (excepto los títulos de sección). Se omiten datos del apartado GENERAL que no son
académicos (escuela, URL del curso).

Uso: python universidades/ec_g_ioannin01/scraper_ec_g_ioannin01.py --sample 5 | --all | --codes C1 C2
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_g_ioannin01"
SAMPLE = ["MYY102", "MYY203", "MYY404", "MYE054", "MYY1000"]
HEADINGS = ["LEARNING OUTCOMES", "General Competences", "SYLLABUS", "TEACHING and LEARNING METHODS",
            "STUDENT PERFORMANCE EVALUATION", "ATTACHED BIBLIOGRAPHY"]
DROP_START = re.compile(r"^(SCHOOL|ACADEMIC UNIT|LEVEL OF STUDIES|COURSE WEBSITE|COURSE OUTLINE|GENERAL$|COURSE TITLE|COURSE CODE|INDEPENDENT TEACHING|WEEKLY|TEACHING CREDITS|HOURS$|ENGINEERING$)")
cache_pages: dict[str, list[str]] = {}
boiler: dict[str, set[str]] = {}


def pdf_pages(http: PoliteClient, url: str) -> list[str]:
    if url not in cache_pages:
        with pdfplumber.open(http.get_file(url)) as d:
            cache_pages[url] = [(p.extract_text() or "") for p in d.pages]
    return cache_pages[url]


def boilerplate(url: str, rows: list[dict], pages: list[str]) -> set[str]:
    """Líneas presentes en >= 70 % de las fichas del PDF = plantilla."""
    if url not in boiler:
        cnt: collections.Counter = collections.Counter()
        mine = [r for r in rows if r["url_guia_docente"] == url]
        for r in mine:
            ini, fin = (int(x) for x in r["paginas_pdf"].split("-"))
            lines = {ln.strip() for ln in "\n".join(pages[ini - 1:fin]).split("\n") if ln.strip()}
            cnt.update(lines)
        n = max(len(mine), 1)
        boiler[url] = {ln for ln, c in cnt.items() if c / n >= 0.7 and ln not in HEADINGS}
    return boiler[url]


def build(text: str, e: dict, bp: set[str]) -> tuple[str, dict]:
    lines = [ln.strip() for ln in text.split("\n")]
    info = []
    m = re.search(r"SEMESTER\s+(\S+)", text)
    if m:
        info.append(f"- **Semester:** {m.group(1)}")
    info.append(f"- **ECTS (catalog):** {e['creditos_ects']:g}" if e.get("creditos_ects") else "- **ECTS (catalog):** n/a")
    for key, label in (("COURSE TYPE", "Course type"), ("PREREQUISITE COURSES:", "Prerequisite courses"),
                       ("LANGUAGE OF INSTRUCTION", "Language of instruction"), ("IS THE COURSE OFFERED TO", "Offered to Erasmus students")):
        for i, ln in enumerate(lines):
            if ln.startswith(key):
                val = ln[len(key):].strip()
                if key == "LANGUAGE OF INSTRUCTION" or key == "IS THE COURSE OFFERED TO":
                    # el valor puede estar en esta línea o en la siguiente (tras 'and EXAMINATIONS:' / 'ERASMUS STUDENTS')
                    val = val or ""
                    nxt = lines[i + 1] if i + 1 < len(lines) else ""
                    nxt = re.sub(r"^(and EXAMINATIONS:|ERASMUS STUDENTS)\s*", "", nxt)
                    val = (val + " " + nxt).strip() if not val else val
                if val:
                    info.append(f"- **{label}:** {val}")
                break
    body: list[str] = []
    cur = None
    found = {k: False for k in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    sect_text = collections.defaultdict(list)
    for ln in lines:
        if not ln:
            continue
        if ln in HEADINGS or ln.startswith("TEACHING and LEARNING METHODS"):
            cur = "TEACHING and LEARNING METHODS" if ln.startswith("TEACHING") else ln
            continue
        if ln.startswith("STUDENT PERFORMANCE"):
            cur = "STUDENT PERFORMANCE EVALUATION"
            ln = ln[len("STUDENT PERFORMANCE"):].strip()
            if ln.startswith("EVALUATION"):
                ln = ln[len("EVALUATION"):].strip()
            if not ln:
                continue
        if cur is None or DROP_START.match(ln) or ln in bp:
            continue
        if re.match(r"^(Learning outcomes|EVALUATION|Description of the evaluation procedure)$", ln):
            continue
        sect_text[cur].append(ln)
    out = [f"# {e['nombre_asignatura']} ({e['codigo_asignatura']})", "", "## General information", ""] + info
    titles = {"LEARNING OUTCOMES": "Learning outcomes", "General Competences": "General competences", "SYLLABUS": "Syllabus",
              "TEACHING and LEARNING METHODS": "Teaching and learning methods", "STUDENT PERFORMANCE EVALUATION": "Student performance evaluation",
              "ATTACHED BIBLIOGRAPHY": "Bibliography"}
    for h in HEADINGS:
        body_lines = [x for x in sect_text.get(h, []) if not re.match(r"^(Page \d+|\d+)$", x)]
        if h == "General Competences":      # solo las competencias marcadas (viñetas), no la cuadrícula
            body_lines = [x for x in body_lines if x.startswith(("•", "-"))]
        if not body_lines:
            continue
        out += ["", f"## {titles[h]}", ""] + body_lines
        flag = {"LEARNING OUTCOMES": "learning_outcomes", "SYLLABUS": "contents", "STUDENT PERFORMANCE EVALUATION": "assessment", "ATTACHED BIBLIOGRAPHY": "bibliography"}.get(h)
        if flag and len(" ".join(body_lines)) > 15:
            found[flag] = True
    pre = next((i for i in info if "Prerequisite courses" in i), "")
    found["prerequisites"] = bool(pre) and not re.search(r":\*\*\s*(No|-|NONE|NO)\s*$", pre, re.I)
    md = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"
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
    failed = 0
    for c in codes:
        e = rows.get(c)
        if e is None:
            print(f"{c}: FAIL no está en el catálogo")
            failed += 1
            continue
        try:
            url = e["url_guia_docente"]
            pages = pdf_pages(http, url)
            bp = boilerplate(url, list(rows.values()), pages)
            ini, fin = (int(x) for x in e["paginas_pdf"].split("-"))
            md, found = build("\n".join(pages[ini - 1:fin]), e, bp)
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
