"""Fase 2 - Università di Bologna, Ingegneria meccanica: fichas EN de www.unibo.it -> Markdown.
Uso: python universidades/ec_i_bologna01/scraper_ec_i_bologna01.py [--sample N | --all | --codes C ...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_bologna01"
SAMPLE = ["28622", "28030", "29227", "29780", "65896", "87476", "95245"]  # reemplazado por selección por curso si no existen
SECTIONS = {"Learning outcomes": "learning_outcomes", "Course contents": "contents", "Readings/Bibliography": "bibliography",
            "Teaching methods": "teaching_methods", "Assessment methods": "assessment", "Teaching tools": "teaching_tools"}
SKIP = {"Office hours"}  # Teacher / Office hours: profesorado, fuera
INFO_KEEP = ("Credits", "SSD", "Language")


def to_md(body) -> str:
    out = []
    for el in body.children:
        if getattr(el, "name", None) is None:
            t = str(el).strip()
            if t:
                out.append(t)
        elif el.name in ("ul", "ol"):
            for i, li in enumerate(el.find_all("li", recursive=False), 1):
                out.append(("- " if el.name == "ul" else f"{i}. ") + li.get_text(" ", strip=True))
        elif el.name == "table":
            rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])] for tr in el.find_all("tr")]
            if rows:
                out.append("| " + " | ".join(rows[0]) + " |\n|" + "---|" * len(rows[0]) + "\n" + "\n".join("| " + " | ".join(r) + " |" for r in rows[1:]))
        else:
            t = el.get_text("\n", strip=True)
            if t:
                out.append(t)
    return "\n\n".join(out)


def parse(html: str, entry: dict) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    core = s.find(id="u-content-core")
    if core is None:
        raise ValueError("sin u-content-core")
    info = []
    for li in core.find_all("li"):
        t = li.find("strong", class_="title")
        if t and t.get_text(strip=True).rstrip(":") in INFO_KEEP:
            info.append(f"- {t.get_text(strip=True).rstrip(':')}: {li.get_text(' ', strip=True).split(':', 1)[1].strip()}")
    parts = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", "\n".join(info)]
    found = {k: False for k in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    for h2 in core.find_all("h2"):
        name = h2.get_text(" ", strip=True)
        if name in SKIP or name not in SECTIONS:
            continue
        box = h2.parent
        # el cuerpo son los hermanos siguientes del h2 dentro del mismo contenedor
        sib = BeautifulSoup("<div></div>", "lxml").div
        for n in h2.next_siblings:
            if getattr(n, "name", None) == "h2":
                break
            sib.append(n.__copy__()) if hasattr(n, "__copy__") else None
        text = to_md(sib).strip()
        if not text:
            continue
        parts.append(f"## {name}\n\n{text}")
        found[SECTIONS[name]] = True
    return "\n\n".join(p for p in parts if p), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, nargs="?", const=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = [e if isinstance(e, dict) else e.model_dump() for e in cat["asignaturas"]] if isinstance(cat, dict) else [e.model_dump() for e in cat.asignaturas]
    rows = [r for r in rows if r["tipo_fuente"] != "sin_guia"]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        by = {}
        for r in rows:
            by.setdefault(r["curso"], []).append(r)
        pick = [by[k][0] for k in sorted(by)] + [by[2][-1], by[3][-1]] if {1, 2, 3} <= set(by) else rows
        rows = pick[: a.sample or 5] if a.sample else pick
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for r in rows:
        try:
            md, found = parse(c.get_text(r["url_guia_docente"]), r)
            write_markdown(SLUG, r, md, found)
            print("ok", r["codigo_asignatura"], {k: int(v) for k, v in found.items()})
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", r["codigo_asignatura"], ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
