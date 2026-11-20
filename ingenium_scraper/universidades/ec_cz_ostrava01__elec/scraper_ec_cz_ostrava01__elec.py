"""Fase 2 - VSB Ostrava FS: ficha ECTS HTML por asignatura -> raw_markdown/{codigo}.md
Uso: python universidades/ec_cz_ostrava01__elec/scraper_ec_cz_ostrava01__elec.py [--sample N | --all | --codes C1 C2]
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
SLUG = "ec_cz_ostrava01__elec"
SAMPLE = []
DROP = {"name of lecturer(s)", "personal id", "name", "course unit code", "number of ects credits allocated"}
BLOCKS = {
    "contents": ("course contents", "summary"),
    "learning_outcomes": ("learning outcomes",),
    "assessment": ("assesment", "assessment"),
    "bibliography": ("recommended or required reading", "required reading", "recommended reading"),
    "prerequisites": ("prerequisites",),
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


def to_markdown(html: str, title: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    box = s.select_one("#ects")
    if box is None:
        raise ValueError("sin #ects")
    md = ["# " + title]
    present = {}
    for th in box.select("th.subjectAttrsTitle"):
        name = th.get_text(" ", strip=True).rstrip(" *")
        td = th.find_next_sibling("td")
        if td is None:  # títulos de sección: el valor está en la fila siguiente
            nxt = th.find_parent("tr").find_next_sibling("tr")
            td = nxt.find("td", class_="subjectAttrsValue") if nxt and not nxt.find("th") else None
        txt = clean(inline(td)) if td else ""
        low = name.lower()
        if low in DROP:
            continue
        if txt:
            present[low] = True
            md.append("## " + name + "\n\n" + txt)
    found = {k: any(any(x in p for x in v) for p in present) for k, v in BLOCKS.items()}
    return "\n\n".join(md), found


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
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"], "sin_guia")
            continue
        try:
            body, found = to_markdown(c.get_text(e["url_guia_docente"]), e["nombre_asignatura"])
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
