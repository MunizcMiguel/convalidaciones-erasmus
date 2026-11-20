"""Fase 2 - Aalto (BSc Electrical Engineering): course-unit de la API Sisu (JSON con HTML ligero) -> Markdown.
Uso: python universidades/ec_sf_espoo12/scraper_ec_sf_espoo12.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import html as htmllib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString, Tag  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

SLUG = "ec_sf_espoo12"
HERE = Path(__file__).parent
PERIOD = "aalto-LV-75"
SECTIONS = [  # campo JSON, titulo, clave de bloque
    ("outcomes", "Learning outcomes", "learning_outcomes"),
    ("content", "Content", "contents"),
    ("prerequisites", "Prerequisites", "prerequisites"),
    ("recommendedFormalPrerequisites", "Recommended prerequisites", None),
    ("additional", "Additional information", None),
    ("literature", "Literature", "bibliography"),
    ("learningMaterial", "Learning material", "bibliography"),
]
SAMPLE_PATTERNS = ["^MS-A|Calculus|Differential", "Physics|PHYS", "Circuit|Electric|Signal", "Programming|ELEC-A", "Bachelor.?s (thesis|project)|Capstone"]


def tr(d):
    d = d or {}
    return d.get("en") or d.get("fi") or d.get("sv") or ""


def html_md(s: str) -> str:
    soup = BeautifulSoup(htmllib.unescape(s) if "&lt;" in s else s, "lxml")
    out: list[str] = []

    def rec(node: Tag, bullet: str = "") -> None:
        for ch in node.children:
            if isinstance(ch, NavigableString):
                t = re.sub(r"\s+", " ", str(ch)).strip()
                if t:
                    out.append(t)
            elif ch.name in ("ul", "ol"):
                for li in ch.find_all("li", recursive=False):
                    out.append("- " + re.sub(r"\s+", " ", li.get_text(" ", strip=True)))
            elif ch.name in ("h1", "h2", "h3", "h4"):
                out.append("### " + ch.get_text(" ", strip=True))
            elif ch.name == "table":
                rows = [[re.sub(r"\s+", " ", c.get_text(" ", strip=True)) for c in tr_.find_all(["td", "th"])] for tr_ in ch.find_all("tr")]
                rows = [r for r in rows if any(r)]
                if rows:
                    w = max(map(len, rows))
                    rows = [r + [""] * (w - len(r)) for r in rows]
                    out.append("\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]]))
            elif ch.name in ("p", "div", "span", "strong", "em", "a", "br", "body", "html"):
                if ch.name in ("p",):
                    t = re.sub(r"\s+", " ", ch.get_text(" ", strip=True))
                    if t:
                        out.append(t)
                else:
                    rec(ch)
            else:
                t = re.sub(r"\s+", " ", ch.get_text(" ", strip=True))
                if t:
                    out.append(t)

    rec(soup)
    return "\n\n".join(out)


def pick_version(versions):
    hit = [v for v in versions if PERIOD in (v.get("curriculumPeriodIds") or [])]
    return (hit or sorted(versions, key=lambda v: (v.get("validityPeriod") or {}).get("startDate") or ""))[-1]


def to_markdown(cu: dict, entry: dict) -> tuple[str, dict]:
    out = [f"# {entry['nombre_asignatura']}", f"- **Code**: {entry['codigo_asignatura']}", f"- **Credits**: {entry['creditos_ects']:g} ECTS" if entry.get("creditos_ects") is not None else "",
           f"- **Programme module path**: {entry['curso_semestre']}"]
    found = {k: False for k in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    for field, title, key in SECTIONS:
        v = cu.get(field)
        text = tr(v) if isinstance(v, dict) else ""
        body = html_md(text).strip() if text else ""
        if not body:
            continue
        out.append(f"## {title}\n\n{body}")
        if key:
            found[key] = True
    # evaluacion: la escala de notas y la descripcion de metodos de finalizacion si existen
    ev = []
    for cm in cu.get("completionMethods") or []:
        d = tr(cm.get("description")) if isinstance(cm.get("description"), dict) else ""
        if d:
            ev.append(html_md(d))
    if cu.get("gradeScaleId"):
        ev.append(f"Grade scale: {cu['gradeScaleId']}")
    real = [e for e in ev if not e.startswith("Grade scale")]
    if ev:
        out.append("## Assessment\n\n" + "\n\n".join(ev))
        found["assessment"] = bool(real)
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
                if re.search(pat, r["nombre_asignatura"] + " " + r["codigo_asignatura"], re.I) and r["codigo_asignatura"] not in seen:
                    pick.append(r)
                    seen.add(r["codigo_asignatura"])
                    break
        rows = (pick + [r for r in rows if r["codigo_asignatura"] not in seen])[: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for r in rows:
        try:
            cu = pick_version(http.get_json(r["url_guia_docente"]))
            md, found = to_markdown(cu, r)
            write_markdown(SLUG, r, md, found)
            print(f"ok   {r['codigo_asignatura']} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {r['codigo_asignatura']}: {e}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
