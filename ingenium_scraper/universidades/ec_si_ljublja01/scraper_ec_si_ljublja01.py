#!/usr/bin/env python3
"""Fase 2 · Scraper — Univerza v Ljubljani (FS), asignaturas Erasmus+ (PDF compartido ERASMUS-1.pdf).

Una ficha por página del PDF (paginas_pdf del catálogo). Se convierte el texto de la página a
Markdown: título, línea de horas y secciones Objectives / Programme / Prerequisites / Learning
outcomes / Assessment / Literature. Se elimina la línea «Lecturer».

Uso: python universidades/ec_si_ljublja01/scraper_ec_si_ljublja01.py --sample 5 | --all | --codes C1 C2
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
SLUG = "ec_si_ljublja01"
SAMPLE = ["6024-M", "6037-M", "6055-M", "6046-M", "6017-M"]

HEADS = [  # (regex al inicio de línea, título, bloque)
    (r"Objectives\b\s*(.*)", "Objectives", "learning_outcomes"),
    (r"Programme\b\s*(.*)", "Programme", "contents"),
    (r"Prerequisites\b\s*(.*)", "Prerequisites", "prerequisites"),
    (r"Learning\b\s*(.*)", "Learning outcomes", "learning_outcomes"),
    (r"Assessment\b\s*(.*)", "Assessment", "assessment"),
    (r"Literature\b\s*(.*)", "Literature", "bibliography"),
]


def split_head(text: str) -> tuple[str, float, list[str]]:
    lines = text.split("\n")
    m = re.match(r"^(.*?)\s*(\d+)\s*ECTS\s*(.*)$", lines[0])
    if m:
        return (m.group(1) + " " + m.group(3)).strip(), float(m.group(2)), lines[1:]
    m = re.match(r"^(\d+)\s*ECTS\s*(.*)$", lines[1])
    if m:
        tail, k = m.group(2), 2
        if not tail and not lines[2].startswith("Lecturer"):
            tail, k = lines[2], 3
        return (lines[0] + " " + tail).strip(), float(m.group(1)), lines[k:]
    raise ValueError("cabecera no reconocida: " + lines[0])


def build(text: str, e: dict) -> tuple[str, dict]:
    title, ects, rest = split_head(text)
    out = [f"# {title} ({e['codigo_asignatura']})", "", f"- **ECTS:** {ects:g}", "- **Level:** 2nd cycle (Master), Erasmus+ subject list 2026/27"]
    found = {b: False for b in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    pending_outcomes_word = False
    for ln in rest:
        s = ln.strip()
        if not s or s.startswith("Lecturer:"):
            continue
        if s.startswith("Lectures:"):
            out += [f"- **Hours:** {s}", ""]
            continue
        if re.fullmatch(r"outcomes?", s, re.I):  # resto de la etiqueta «Learning / outcomes» (columna del PDF)
            pending_outcomes_word = False
            continue
        for pat, name, blk in HEADS:
            m = re.match(pat, s)
            if m and not (name == "Learning outcomes" and not re.match(r"Learning\s*(outcomes\b|Knowledge|Skills|$|[A-Z])", s)):
                body = m.group(1).strip()
                out += ["", f"## {name}", ""]
                if name == "Learning outcomes" and body.lower().startswith("outcomes"):
                    body = body[len("outcomes"):].strip()
                elif name == "Learning outcomes":
                    pending_outcomes_word = True
                if body:
                    out.append(body)
                found[blk] = True
                break
        else:
            pending_outcomes_word = False
            out.append(s)
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
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
    pdf_cache: dict[str, list[str]] = {}
    for c in codes:
        e = rows.get(c)
        if e is None:
            print(f"{c}: FAIL no está en el catálogo")
            failed += 1
            continue
        if e["tipo_fuente"] == "sin_guia":
            print(f"{c}: skip sin_guia")
            continue
        try:
            url = e["url_guia_docente"]
            if url not in pdf_cache:
                with pdfplumber.open(http.get_file(url)) as d:
                    pdf_cache[url] = [(p.extract_text() or "") for p in d.pages]
            ini, fin = (int(x) for x in e["paginas_pdf"].split("-"))
            text = "\n".join(pdf_cache[url][ini - 1:fin])
            md, found = build(text, e)
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
