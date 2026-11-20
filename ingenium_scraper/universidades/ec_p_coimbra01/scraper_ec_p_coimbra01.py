"""Fase 2 - Universidade de Coimbra (LEEC): ficha EN de apps.uc.pt -> Markdown.
Uso: python universidades/ec_p_coimbra01/scraper_ec_p_coimbra01.py [--sample N | --all | --codes C1 C2]
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

SLUG = "ec_p_coimbra01"
HERE = Path(__file__).parent
SKIP_H2 = {"head lecturer(s)", "lecturer(s)", "teachers", "docente(s)", "regente(s)", "docentes", "other lecturer(s)"}
BLOCKS = {
    "contents": ("syllabus", "conteúdos programáticos", "conteudos programaticos"),
    "learning_outcomes": ("learning outcomes", "objetivos"),
    "assessment": ("assessment methods", "métodos de avaliação", "metodos de avaliacao"),
    "bibliography": ("bibliography", "bibliografia"),
    "prerequisites": ("recommended prerequisites", "pré-requisitos", "pre-requisitos"),
}
# Fijo y diverso (codigos UC): mates 1.º, circuitos 2.º, control 3.º, proyecto, optativa, comp. transversales
SAMPLE = ["01019327", "01000377", "01016253", "01016264", "01000489"]


def cell_md(el) -> str:
    out = []
    for ch in el.children:
        if getattr(ch, "name", None) == "br":
            out.append("\n")
        elif getattr(ch, "name", None) in ("ul", "ol"):
            for li in ch.find_all("li"):
                out.append("\n- " + re.sub(r"\s+", " ", li.get_text(" ", strip=True)))
            out.append("\n")
        elif getattr(ch, "name", None) == "table":
            out.append("\n" + table_md(ch) + "\n")
        elif getattr(ch, "name", None):
            out.append(cell_md(ch))
        else:
            out.append(str(ch))
    return "".join(out)


def table_md(t) -> str:
    rows = [[re.sub(r"\s+", " ", c.get_text(" ", strip=True)) for c in tr.find_all(["th", "td"])] for tr in t.find_all("tr")]
    rows = [r for r in rows if r]
    if not rows:
        return ""
    w = max(map(len, rows))
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def parse(html: str, entry: dict) -> tuple[str, dict]:
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("h1") or soup.find("title")
    name = entry["nombre_asignatura"]
    md = [f"# {name}", ""]
    meta = {}
    for d in soup.select("div.uk-width-1-3\@m div"):
        s = d.find("strong")
        sp = d.find("span")
        if s and sp:
            meta[s.get_text(strip=True)] = sp.get_text(" ", strip=True)
    for k in ("Code", "Year", "Academic year", "Language of Instruction", "Mode of Delivery", "Duration", "ECTS Credits", "Type", "Level", "Subject Area"):
        if meta.get(k):
            md.append(f"- **{k}:** {meta[k]}")
    md.append("")
    found = {b: False for b in BLOCKS}
    main = soup.select_one("div.course-detail-content")
    if main is None:
        raise RuntimeError("sin course-detail-content")
    for h in main.find_all("h2"):
        ht = re.sub(r"\s+", " ", h.get_text(" ", strip=True))
        if ht.lower() in SKIP_H2:
            continue
        parts = []
        for sib in h.next_siblings:
            if getattr(sib, "name", None) == "h2":
                break
            if getattr(sib, "name", None):
                if sib.name == "table":
                    parts.append("\n\n" + table_md(sib) + "\n\n")
                else:
                    parts.append("\n\n" + cell_md(sib) + "\n\n")
            else:
                parts.append(str(sib))
        body = re.sub(r"[ \t\xa0]+", " ", "".join(parts))
        body = re.sub(r"\n\s*\n+", "\n\n", re.sub(r"[ \t]*\n[ \t]*", "\n", body)).strip()
        if not body:
            continue
        md += [f"## {ht}", "", body, ""]
        for b, keys in BLOCKS.items():
            if ht.lower() in keys:
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
    if a.all:
        codes = list(ents)
    elif a.codes:
        codes = a.codes
    else:
        n = a.sample or 5
        codes = [c for c in SAMPLE if c in ents][:n]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for c in codes:
        e = ents[c]
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print(f"{c}: sin_guia")
            continue
        try:
            body, found = parse(http.get_text(e["url_guia_docente"]), e)
            if len(body) < 300:
                raise RuntimeError("ficha casi vacia")
            write_markdown(SLUG, e, body, found)
            print(f"{c}: ok {e['nombre_asignatura']} ({len(body)} chars) {[k for k,v in found.items() if not v]}")
        except Exception as ex:  # noqa: BLE001
            fails += 1
            print(f"{c}: FALLO {ex}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
