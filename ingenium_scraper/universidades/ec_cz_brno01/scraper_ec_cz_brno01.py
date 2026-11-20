"""Fase 2 - VUT Brno FSI (B-STI-A): ficha HTML por asignatura -> raw_markdown/{codigo}.md
Uso: python universidades/ec_cz_brno01/scraper_ec_cz_brno01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_cz_brno01"
SAMPLE = ["1M-A", "5KS-A", "6B-A", "6MB-A", "3ST-A", "TEN1"]
DROP = {"supervisor", "teacher / lecturer", "teacher", "lecturer"}  # personal docente
BLOCKS = {
    "contents": ("syllabus",),
    "learning_outcomes": ("aims", "learning outcomes"),
    "assessment": ("rules for evaluation", "assessment", "examination"),
    "bibliography": ("literature", "recommended"),
    "prerequisites": ("entry knowledge", "prerequisites"),
}


def inline(node) -> str:
    out = []
    for ch in node.children:
        if isinstance(ch, NavigableString):
            out.append(str(ch))
        elif ch.name == "br":
            out.append("\n")
        elif ch.name in ("ul", "ol"):
            out.append("\n" + "\n".join("- " + re.sub(r"\s+", " ", li.get_text(" ", strip=True)) for li in ch.find_all("li")) + "\n")
        elif ch.name == "table":
            out.append("\n" + table_md(ch) + "\n")
        elif ch.name in ("p", "div"):
            out.append("\n" + inline(ch) + "\n")
        else:
            out.append(inline(ch))
    return "".join(out)


def table_md(t) -> str:
    rows = [[re.sub(r"\s+", " ", c.get_text(" ", strip=True)) for c in r.find_all(["th", "td"])] for r in t.find_all("tr")]
    rows = [r for r in rows if r]
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def clean(txt: str) -> str:
    lines = [re.sub(r"[ \t\xa0]+", " ", l).strip() for l in txt.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def to_markdown(html: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    d = s.select_one("div.b-detail")
    if d is None:
        raise ValueError("sin div.b-detail")
    title = d.select_one(".b-detail__title")
    md = ["# " + (title.get_text(" ", strip=True) if title else "")]
    annot = d.select_one(".b-detail__annot")
    if annot:
        md.append(" | ".join(i.get_text(" ", strip=True) for i in annot.select(".b-detail__annot-item")))
    ab = d.select_one(".b-detail__abstract")
    abstract = clean(inline(ab)) if ab else ""
    if abstract:
        md.append("## Course summary\n\n" + abstract)
    # etiquetas: p.b-detail__subtitle o h4; su valor es el grid__cell siguiente
    in_units = False
    for lab in d.select("p.b-detail__subtitle, h4"):
        name = lab.get_text(" ", strip=True)
        low = name.lower()
        cell = lab.find_parent("div", class_="grid__cell")
        val = cell.find_next_sibling("div", class_="grid__cell") if cell else None
        txt = clean(inline(val)) if val else ""
        if low == "type of course unit":
            in_units = True
            continue
        if low in DROP or not txt:
            continue
        md.append(("### " if in_units else "## ") + name + "\n\n" + txt)
    body = "\n\n".join(md)
    # programas que incluyen la asignatura
    low = body.lower()
    found = {k: any(f"## {x}" in low for x in v) for k, v in BLOCKS.items()}
    found["contents"] = found["contents"] or bool(abstract)
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
        n = a.sample if a.sample is not None else 5
        sel = [e for e in cat if e["codigo_asignatura"] in SAMPLE][:n]
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"], "sin_guia")
            continue
        try:
            body, found = to_markdown(c.get_text(e["url_guia_docente"]))
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
