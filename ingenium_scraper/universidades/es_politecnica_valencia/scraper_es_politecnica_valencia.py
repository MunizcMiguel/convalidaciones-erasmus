#!/usr/bin/env python3
"""Fase 2 · Scraper — UPV / Florida Universitària, Grado en Ingeniería Mecánica.

Cada guía es un PDF con texto en guiasdocentes.floridauniversitaria.es (URL desde el catálogo):
portada, índice (página 2) y secciones numeradas:
  1 Datos de identificación (PROFESORADO: se descarta) · 2 Resumen · 3 Competencias del título ·
  4 Competencias transversales · 5 Resultados de aprendizaje · 6 Contenidos · 7 Actividades formativas ·
  8 Evaluación · 9 Propuesta de actuaciones específicas (se descarta) · 10 Bibliografía ·
  11 Normas específicas · 12 Consultas y atención al alumnado (profesorado: se descarta).
Las guías de optativas/idiomas llevan menos secciones (y alguna está en inglés), así que las
secciones se identifican por su título (ES/EN), no por su número. Las tablas se extraen con
pdfplumber y se escriben como tablas Markdown.

Uso (desde la raíz del proyecto):
    python universidades/es_politecnica_valencia/scraper_es_politecnica_valencia.py --sample 5
    python universidades/es_politecnica_valencia/scraper_es_politecnica_valencia.py --codes 12706
    python universidades/es_politecnica_valencia/scraper_es_politecnica_valencia.py --all
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_politecnica_valencia"

# Diversa: 1.º básica, 2.º matemáticas/estadística, 3.º técnica, optativa en inglés, 4.º obligatoria, optativa 4.º
SAMPLE = ["12706", "12700", "12719", "13280", "12714", "12749"]

# (clave, regex del título en minúsculas)
SECTIONS = [
    ("skip", r"datos de identificaci[oó]n|identification data"),
    ("summary", r"resumen de la asignatura|course summary"),
    ("competencies", r"competencias del t[ií]tulo|degree competencies"),
    ("transversal", r"competencias transversales|transversal competencies"),
    ("results", r"resultados de aprendizaje|learning outcomes"),
    ("contents", r"contenidos?|content"),
    ("activities", r"actividades formativas|educational activities"),
    ("assessment", r"evaluaci[oó]n del aprendizaje|learning assessment"),
    ("skip", r"propuesta de actuaciones|specific action"),
    ("biblio", r"bibliograf[ií]a|(annotated )?bibliography"),
    ("rules", r"normas espec[ií]ficas|subject-specific"),
    ("skip", r"consultas y atenci[oó]n|consultation and student"),
]
TITLES = {"summary": "Resumen de la asignatura", "competencies": "Competencias del título",
          "transversal": "Competencias transversales", "results": "Resultados de aprendizaje de la asignatura",
          "contents": "Contenidos", "activities": "Actividades formativas y metodología",
          "assessment": "Evaluación del aprendizaje", "biblio": "Bibliografía",
          "rules": "Normas específicas de la asignatura"}
ORDER = ["summary", "competencies", "transversal", "results", "contents", "activities", "assessment", "biblio", "rules"]

_HEAD = re.compile(r"^(\d{1,2})\.\s*(.*)$")
_PREREQ = re.compile(r"conocimientos? previos?|requisitos?|prerrequisitos?|prerequisites?|haber (?:cursado|superado)", re.I)


class GuideError(RuntimeError):
    pass


def kind_of(title: str) -> str | None:
    t = title.strip().lower()
    for k, pat in SECTIONS:
        if re.match(pat, t):
            return k
    return None


def md_table(rows: list[list[str | None]]) -> str:
    rows = [[re.sub(r"\s+", " ", (c or "")).replace("|", "/").strip() for c in r] for r in rows if r]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def page_chunks(page) -> list[str]:
    """Texto y tablas de la página en orden vertical; las tablas pasan a Markdown."""
    tables = sorted(page.find_tables(), key=lambda t: t.bbox[1])
    chunks: list[str] = []
    y = 0.0
    for t in tables:
        x0, top, x1, bottom = t.bbox
        if top - y > 2:
            chunks.append(page.crop((0, y, page.width, top)).extract_text() or "")
        chunks.append("\n" + md_table(t.extract()) + "\n")
        y = bottom
    if page.height - y > 2:
        chunks.append(page.crop((0, y, page.width, page.height)).extract_text() or "")
    return chunks


def doc_lines(pdf: pdfplumber.PDF) -> list[str]:
    out: list[str] = []
    for i, pg in enumerate(pdf.pages):
        if i < 2:  # portada e índice
            continue
        txt = "\n".join(page_chunks(pg))
        for l in txt.splitlines():
            s = l.strip()
            if re.match(r"^Gu[ií]a docente\s*:", s) or re.match(r"^(Teaching|Course) guide\s*:", s, re.I):
                continue
            if re.match(r"^FLORIDA UNIVERSIT[ÀA]RIA\s*-.*(P[aá]gina|Page) \d+ (de|of) \d+$", s):
                continue
            if re.match(r"^\|.*UNIVERSIT[ÀA]RIA\s*-.*\|$", s):  # pie partido por la detección de tablas
                continue
            out.append(l.rstrip())
    return out


def split_sections(lines: list[str]) -> dict[str, list[str]]:
    secs: dict[str, list[str]] = {}
    cur, last = None, 0
    i = 0
    while i < len(lines):
        l = lines[i].strip()
        m = _HEAD.match(l)
        if m and not l.startswith("|"):
            n, title = int(m.group(1)), m.group(2).strip()
            if not title and i + 1 < len(lines):  # "8." al pie de página, el título va en la siguiente
                title = lines[i + 1].strip()
                if kind_of(title):
                    i += 1
            k = kind_of(title)
            if k and last < n <= last + 3:
                last, cur = n, k
                secs.setdefault(k, [])
                i += 1
                continue
        if cur and cur != "skip" and not re.fullmatch(r"\d{1,2}\.", l):
            secs[cur].append(lines[i])
        i += 1
    return secs


def lang_of(text: str) -> str:
    low = " " + re.sub(r"[^a-záéíóúñ ]", " ", text.lower()) + " "
    es = sum(low.count(f" {w} ") for w in ("el", "la", "de", "los", "las", "y", "que", "en", "del"))
    en = sum(low.count(f" {w} ") for w in ("the", "of", "and", "to", "in", "is", "for", "with"))
    return "en" if en > es else "es"


def clean(lines: list[str]) -> str:
    t = "\n".join(lines)
    t = re.sub(r"\(cid:\d+\)", "", t)
    t = re.sub("[" + chr(0) + "-" + chr(8) + chr(11) + chr(12) + chr(14) + "-" + chr(31) + "]", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def scrape_course(http: PoliteClient, entry: dict) -> tuple[Path, dict]:
    code = entry["codigo_asignatura"]
    data = http.get_bytes(entry["url_guia_docente"])
    if not data.startswith(b"%PDF"):
        raise GuideError("la respuesta no es un PDF")
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        lines = doc_lines(pdf)
    secs = split_sections(lines)
    if "contents" not in secs and "summary" not in secs:
        raise GuideError(f"sin contenidos ni resumen; secciones: {sorted(secs)}")
    body = {k: clean(v) for k, v in secs.items()}
    body = {k: v for k, v in body.items() if v}
    lang = lang_of(" ".join(body.values()))
    md = [f"# {entry['nombre_asignatura']} ({code})", "",
          f"- Titulación: {entry['nombre_grado']} · {entry['universidad']}",
          f"- Curso/semestre: {entry['curso_semestre']}",
          f"- Créditos: {entry['creditos_ects']} ECTS · Carácter: {entry['caracter']}",
          f"- Fuente: {entry['url_guia_docente']}", ""]
    for k in ORDER:
        if k in body:
            md += [f"## {TITLES[k]}", "", body[k], ""]
    alltxt = "\n".join(body.get(k, "") for k in ("summary", "rules", "contents"))
    blocks = {
        "contents": "contents" in body or "summary" in body,
        "learning_outcomes": any(k in body for k in ("results", "competencies", "transversal")),
        "assessment": "assessment" in body,
        "bibliography": bool(re.search(r"bibliograf[ií]a (b[aá]sica|complementaria)|basic bibliography|(19|20)\d\d", body.get("biblio", ""), re.I)),
        "prerequisites": bool(_PREREQ.search(alltxt)),
    }
    path = write_markdown(SLUG, dict(entry, idioma_pagina=lang), "\n".join(md), blocks)
    return path, blocks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    args = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    if args.all:
        codes = list(rows)
    elif args.codes:
        codes = args.codes
    else:
        codes = SAMPLE[: (args.sample or 5)]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = skip = 0
    for c in codes:
        e = rows.get(c)
        if e is None:
            print(f"FALLO  {c}: no está en el catálogo"); fail += 1; continue
        if e["tipo_fuente"] == "sin_guia":
            print(f"omite  {c} {e['nombre_asignatura']}: sin guía"); skip += 1; continue
        try:
            path, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} -> {path.name} ({path.stat().st_size} bytes)"
                  + (f" · bloques ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except (FetchError, GuideError) as ex:
            print(f"FALLO  {c} {e['nombre_asignatura']}: {ex}"); fail += 1
    print(f"{ok} ok, {fail} fallos, {skip} omitidas")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
