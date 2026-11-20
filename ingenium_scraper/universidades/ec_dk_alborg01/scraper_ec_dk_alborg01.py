"""Fase 2 - Aalborg (Applied Industrial Electronics): ficha de moduler.aau.dk -> Markdown.
Uso: python universidades/ec_dk_alborg01/scraper_ec_dk_alborg01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString, Tag  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

SLUG = "ec_dk_alborg01"
HERE = Path(__file__).parent
SKIP_H2 = {"organisation", "search in modules", "related links"}
SKIP_ROWS = ("responsible",)  # personal docente
SAMPLE = ["MATCAL1345GB", "25E-AIE1-1", "25E-AIE4-1", "25E-EN6-4", "25E-AIE6-1"]
BLOCKS = {
    "contents": ("content", "contents", "subject content", "content of the module", "course content"),
    "learning_outcomes": ("learning objectives",),
    "assessment": ("exams", "exam"),
    "bibliography": ("literature", "reading list", "bibliography"),
    "prerequisites": ("recommended prerequisites", "prerequisites", "prerequisite for enrollment for the exam"),
}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def table_md(t: Tag) -> str:
    rows = []
    for tr in t.find_all("tr"):
        cells = [clean(c.get_text(" ", strip=True)) for c in tr.find_all(["td", "th"])]
        if cells and not cells[0].lower().startswith(SKIP_ROWS):
            rows.append(cells)
    if not rows:
        return ""
    w = max(map(len, rows))
    rows = [r + [""] * (w - len(r)) for r in rows]
    if w == 2 and False:
        pass
    hdr = ["", ""] if w == 2 else rows[0]
    body = rows if w == 2 else rows[1:]
    return "\n".join(["| " + " | ".join(hdr) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in body])


def render(el, depth=0) -> str:
    if isinstance(el, NavigableString):
        return clean(str(el)) if clean(str(el)) else ""
    n = el.name
    if n in ("h3", "h4", "h5"):
        return "\n\n" + "#" * (int(n[1]) ) + " " + clean(el.get_text(" ", strip=True)) + "\n\n"
    if n == "table":
        return "\n\n" + table_md(el) + "\n\n"
    if n in ("ul", "ol"):
        out = []
        for i, li in enumerate(el.find_all("li", recursive=False), 1):
            out.append(("- " if n == "ul" else f"{i}. ") + clean(li.get_text(" ", strip=True)))
        return "\n\n" + "\n".join(out) + "\n\n"
    if n in ("p", "div", "section"):
        if n == "div" and el.find(["h3", "h4", "table", "ul", "ol", "p"]):
            return "".join(render(c, depth + 1) for c in el.children)
        return "\n\n" + clean(el.get_text(" ", strip=True)) + "\n\n"
    return clean(el.get_text(" ", strip=True))


def parse(html: str, entry: dict) -> tuple[str, dict]:
    soup = BeautifulSoup(html, "lxml")
    md = [f"# {entry['nombre_asignatura']}", ""]
    found = {b: False for b in BLOCKS}
    for h2 in soup.select("h2.headline"):
        title = clean(h2.get_text(" ", strip=True))
        if title.lower() in SKIP_H2:
            continue
        body = []
        for sib in h2.next_siblings:
            if getattr(sib, "name", None) == "h2":
                break
            body.append(render(sib))
        text = re.sub(r"\n{3,}", "\n\n", "".join(body)).strip()
        if not text:
            continue
        md += [f"## {title}", "", text, ""]
        if title.lower().startswith("recommended prerequisite"):
            found["prerequisites"] = True
        for m in re.finditer(r"^#{3,4} (.+)$", text, re.M):
            for b, keys in BLOCKS.items():
                if clean(m.group(1)).lower() in keys:
                    found[b] = True
    return "\n".join(md), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, nargs="?", const=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    ents = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    codes = list(ents) if a.all else a.codes or [c for c in SAMPLE if c in ents][: a.sample or 5]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for c in codes:
        e = ents[c]
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print(f"{c}: sin_guia")
            continue
        try:
            body, found = parse(http.get_text(e["url_guia_docente"]), e)
            if len(body) < 400:
                raise RuntimeError("ficha casi vacia")
            write_markdown(SLUG, e, body, found)
            print(f"{c}: ok {e['nombre_asignatura']} ({len(body)} chars) falta={[k for k, v in found.items() if not v]}")
        except Exception as ex:  # noqa: BLE001
            fails += 1
            print(f"{c}: FALLO {ex}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
