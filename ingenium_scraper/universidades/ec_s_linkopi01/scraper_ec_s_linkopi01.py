"""Fase 2 - Linköping (6CIEI): ficha de curso de Studieinfo (version en inglesa) -> Markdown.
Uso: python universidades/ec_s_linkopi01/scraper_ec_s_linkopi01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, Tag  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

SLUG = "ec_s_linkopi01"
HERE = Path(__file__).parent
WANTED = [  # titulo del h2 -> clave de bloque
    ("Intended learning outcomes", "learning_outcomes"), ("Course content", "contents"), ("Teaching and working methods", None),
    ("Examination", "assessment"), ("Grades", None), ("Course literature", "bibliography"),
]
SAMPLE_PATTERNS = ["^Matematisk|Mathematic|Calculus|Linear", "Industrial|Operations|Production", "Statistic|Mechanics|Thermo|Physics", "Project|Economics|Management", "Degree|Thesis"]


def clean(s: str) -> str:
    return re.sub(r"[ \t\xa0]+", " ", s).strip()


def node_md(n) -> str:
    if isinstance(n, str):
        return clean(n)
    if not isinstance(n, Tag):
        return ""
    if n.name in ("h3", "h4"):
        return f"### {clean(n.get_text(' ', strip=True))}"
    if n.name == "table":
        rows = [[clean(c.get_text(" ", strip=True)) for c in tr.find_all(["td", "th"])] for tr in n.find_all("tr")]
        rows = [r for r in rows if any(r)]
        if not rows:
            return ""
        w = max(map(len, rows))
        rows = [r + [""] * (w - len(r)) for r in rows]
        return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])
    if n.name in ("ul", "ol"):
        return "\n".join(f"- {clean(li.get_text(' ', strip=True))}" for li in n.find_all("li"))
    if n.name in ("script", "style", "button", "a") and not n.get_text(strip=True):
        return ""
    # contenedores: se recorre su contenido para conservar listas/tablas
    kids = [node_md(c) for c in n.children]
    kids = [k for k in kids if k]
    if n.name in ("div", "section", "article"):
        return "\n\n".join(kids)
    return clean(n.get_text(" ", strip=True))


def to_markdown(html: str, entry: dict) -> tuple[str, dict]:
    soup = BeautifulSoup(html, "lxml")
    main = soup.find("main") or soup
    out = [f"# {entry['nombre_asignatura']}"]
    if entry.get("creditos_ects"):
        out.append(f"- **Credits**: {entry['creditos_ects']:g} hp (ECTS)")
    found = {k: False for k in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    done = set()
    for h2 in main.find_all("h2"):
        title = clean(h2.get_text(" ", strip=True))
        for want, key in WANTED:
            if title == want and want not in done:
                parts = []
                for sib in h2.next_siblings:
                    if isinstance(sib, Tag) and sib.name == "h2":
                        break
                    parts.append(node_md(sib))
                body = "\n\n".join(p for p in parts if p).strip()
                if not body:
                    continue
                done.add(want)
                out.append(f"## {want}\n\n{body}")
                if key:
                    found[key] = True
    # requisitos previos: seccion "Prerequisites" o "Entry requirements" si existe como h2
    for h2 in main.find_all("h2"):
        if re.match(r"(Prerequisites|Entry requirements|Recommended prior)", clean(h2.get_text()), re.I):
            body = clean(h2.find_next_sibling().get_text(" ", strip=True)) if h2.find_next_sibling() else ""
            if body:
                out.append(f"## {clean(h2.get_text())}\n\n{body}")
                found["prerequisites"] = True
            break
    if not done:
        raise ValueError("sin secciones de silabo")
    return "\n\n".join(o for o in out if o), found


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
        pick, seen = [], set()
        for pat in SAMPLE_PATTERNS:
            for r in rows:
                if re.search(pat, r["nombre_asignatura"], re.I) and r["codigo_asignatura"] not in seen:
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
