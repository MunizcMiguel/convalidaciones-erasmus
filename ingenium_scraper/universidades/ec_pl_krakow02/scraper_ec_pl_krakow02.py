"""Fase 2 - AGH Krakow (Electrical Engineering): ficha /en/document/{uuid}.html -> Markdown.
Uso: python universidades/ec_pl_krakow02/scraper_ec_pl_krakow02.py [--sample N | --all | --codes C1 C2]
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

SLUG = "ec_pl_krakow02"
HERE = Path(__file__).parent
SKIP_LABELS = ("course coordinator", "lecturer", "coordinator")  # personal docente
BLOCKS = {
    "contents": ("program content",),
    "learning_outcomes": ("course's learning outcomes", "learning outcomes"),
    "assessment": ("extended information", "assessment"),
    "bibliography": ("literature",),
    "prerequisites": ("prerequisites", "entry requirements", "additional requirements"),
}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def table_md(t: Tag) -> str:
    if len(t.find_all("tr")) == 1 and t.select_one(".row_header"):  # cabecera Period / verificacion / ECTS
        items = []
        for td in t.find_all("td"):
            parts = [clean(x.get_text(" ", strip=True)) for x in td.find_all("div")]
            parts = [x for x in parts if x]
            if parts:
                items.append(f"- **{parts[0]}**: " + "; ".join(parts[1:]))
        return "\n".join(items)
    rows = []
    for tr in t.find_all("tr"):
        cells = [clean(c.get_text(" ", strip=True)).replace("|", "/") for c in tr.find_all(["td", "th"])]
        if not cells or cells[0].lower().startswith(SKIP_LABELS):
            continue
        rows.append(cells)
    if not rows:
        return ""
    w = max(map(len, rows))
    rows = [r + [""] * (w - len(r)) for r in rows]
    if w == 2:  # clave/valor
        return "\n".join(f"- **{r[0]}**: {r[1]}" for r in rows if r[0] or r[1])
    first_is_head = t.find("th") is not None or t.find("thead") is not None
    hdr = rows[0] if first_is_head else [""] * w
    body = rows[1:] if first_is_head else rows
    return "\n".join(["| " + " | ".join(hdr) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in body])


def convert(node: Tag) -> list[str]:
    out: list[str] = []
    for ch in node.children:
        if isinstance(ch, NavigableString):
            if clean(str(ch)):
                out.append(clean(str(ch)))
            continue
        n = ch.name
        if n in ("h1", "h2", "h3", "h4"):
            t = clean(ch.get_text(" ", strip=True))
            if t:
                out.append("#" * {"h1": 2, "h2": 2, "h3": 3, "h4": 4}[n] + " " + t)
        elif n == "table":
            out.append(table_md(ch))
        elif n == "dl":
            items = []
            for dt in ch.find_all("dt"):
                dd = dt.find_next_sibling("dd")
                k = clean(dt.get_text(" ", strip=True))
                if k.lower().startswith(SKIP_LABELS) or dd is None:
                    continue
                items.append(f"- **{k}**: {clean(dd.get_text(' ', strip=True))}")
            out.append("\n".join(items))
        elif n in ("ul", "ol"):
            out.append("\n".join(f"- {clean(li.get_text(' ', strip=True))}" for li in ch.find_all("li")))
        elif n in ("script", "style", "button", "nav"):
            continue
        elif n == "p":
            out.append(clean(ch.get_text(" ", strip=True)))
        else:
            out.extend(convert(ch))
    return [o for o in out if o]


def to_markdown(html: str, entry: dict) -> tuple[str, dict]:
    soup = BeautifulSoup(html, "lxml")
    root = soup.select_one("#syllabus_content")
    if root is None:
        raise ValueError("sin #syllabus_content")
    for e in root.select(".syllabus-title, .pdf-hidden, .d-print-none, .head-author, .head-teachers, .head-title-main"):
        e.decompose()
    parts = convert(root)
    while parts and clean(parts[0]).lower() in (entry["nombre_asignatura"].lower(), "course description sheet"):
        parts.pop(0)
    md = f"# {entry['nombre_asignatura']}\n\n" + "\n\n".join(parts)
    heads = [h.lower() for h in re.findall(r"^#{2,4} (.+)$", md, re.M)]
    found = {k: any(any(v in h for v in vs) for h in heads) for k, vs in BLOCKS.items()}
    # bloque con encabezado pero sin cuerpo = ausente
    for k, key in (("bibliography", "literature"), ("contents", "program content")):
        m = re.search(rf"^#{{2,4}} [^\n]*{key}[^\n]*\n+(.*?)(?=^#{{2,4}} |\Z)", md, re.M | re.S | re.I)
        if m and not m.group(1).strip():
            found[k] = False
    return md, found


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
        # diverso: sem 1 (mates/fisica), 2, 4, 6, 7 (proyecto/diploma)
        pick, seen = [], set()
        for sem, pat in ((1, "math|physics|algebra"), (2, "."), (4, "electr|circuit|machine"), (6, "power|control|automat"), (7, "diploma|project|thesis")):
            for r in rows:
                if r["semestre"] == sem and re.search(pat, r["nombre_asignatura"], re.I) and r["codigo_asignatura"] not in seen:
                    pick.append(r)
                    seen.add(r["codigo_asignatura"])
                    break
        rows = (pick + [r for r in rows if r["codigo_asignatura"] not in seen])[: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for r in rows:
        try:
            md, found = to_markdown(http.get_text(r["url_guia_docente"]), r)
            write_markdown(SLUG, r, md, found)
            print(f"ok   {r['codigo_asignatura']} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {r['codigo_asignatura']}: {e}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
