#!/usr/bin/env python3
"""Fase 2 · Scraper — Universitatea din Oradea (IETI), Electromechanics.

Cada ficha es un rango de páginas del PDF compartido «FD_licenta_EM_EN_2024-2025.pdf» (paginas_pdf).
El texto (plantilla rumana «SUBJECT DESCRIPTION» con secciones numeradas 1-11) se convierte a
Markdown con una sección por apartado. Se eliminan el apartado 1 (datos del programa) y los
titulares (2.2/2.3 «Holder…»), firmas y fechas.

Uso: python universidades/ec_ro_oradea01/scraper_ec_ro_oradea01.py --sample 5 | --all | --codes C1 C2
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_ro_oradea01"
SAMPLE = ["IETI-0003", "IETI-0272", "IETI-0412", "IETI-0469", "IETI-0451"]   # análisis, máquinas, accionamientos, hidro-neumática, robots

SECTION = [  # (regex de la línea de título, título Markdown, bloque)
    (r"^1\.\s*Data related to the study program", None, None),
    (r"^2\.\s*Data related to the subject", "Subject data", None),
    (r"^3\.\s*Total estimated time", "Workload", None),
    (r"^4\.\s*Pre-?requisites", "Prerequisites", "prerequisites"),
    (r"^5\.\s*Conditions", "Conditions", None),
    (r"^6\.\s*Specific skills", "Specific skills acquired", "learning_outcomes"),
    (r"^7\.\s*Objectives", "Objectives", "learning_outcomes"),
    (r"^8\.\s*Contents", "Contents", "contents"),
    (r"^9\.\s*Corroboration", "Corroboration of the contents with the expectations of the employers", None),
    (r"^10\.\s*Evaluation", "Evaluation", "assessment"),
]
DROP = re.compile(r"^(2\.2 Holder|2\.3 Holder|Date\b|Signature|Head of|Director of|Dean\b|Date of approval|Date of the department)", re.I)
STAFF = re.compile(r"\b(Lecturer|Professor|Assoc\.?\s*Prof|Assistant|Prof\.|Ph\.?D\.?|PhD)\b[^\n]*", re.I)


def load_pages(http: PoliteClient, url: str) -> list[str]:
    cache = HERE / "raw_cache" / "fichas_pages.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    with pdfplumber.open(http.get_file(url)) as d:
        pages = [(p.extract_text() or "") for p in d.pages]
    cache.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    return pages


def build(text: str, e: dict) -> tuple[str, dict]:
    found = {b: False for b in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    out = [f"# {e['nombre_asignatura']} ({e['codigo_asignatura']})", ""]
    cur = None
    skip_next_cont = False
    for ln in text.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if s.startswith("SUBJECT DESCRIPTION"):
            continue
        if re.fullmatch(r"[A-Za-z ]+", s) and all(len(w) <= 2 for w in s.split()):   # texto vertical del margen del PDF
            continue
        hit = False
        for pat, title, blk in SECTION:
            if re.match(pat, s, re.I):
                cur = (title, blk)
                if title:
                    out += ["", f"## {title}", ""]
                hit = True
                break
        if hit:
            skip_next_cont = False
            continue
        if cur is None or cur[0] is None:
            continue
        if DROP.match(s):
            skip_next_cont = s.startswith(("2.2 Holder", "2.3 Holder"))
            continue
        if skip_next_cont and re.match(r"^(seminar|laboratory|project)", s, re.I):
            skip_next_cont = False
            continue
        if re.match(r"^Bibliography\b", s, re.I):
            out += ["", "### Bibliography", ""]
            found["bibliography"] = True
            continue
        out.append(s)
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    for pat, title, blk in SECTION:
        if blk and title:
            m = re.search(rf"^## {re.escape(title)}\n+((?:(?!^## ).*\n?)*)", md, re.M)
            body = m.group(1).strip() if m else ""
            if blk == "prerequisites":
                body = re.sub(r"4\.[12][^\n]*", "", body).replace("-", "").strip()
            if body and len(body) > 3:
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
    pages = None
    failed = 0
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
            if pages is None:
                pages = load_pages(http, e["url_guia_docente"])
            ini, fin = (int(x) for x in e["paginas_pdf"].split("-"))
            md, found = build("\n".join(pages[ini - 1:fin]), e)
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
