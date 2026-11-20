#!/usr/bin/env python3
"""Fase 2 — Universidad de Burgos: guías docentes PDF (ubuvirtual.ubu.es/mod/guiadocente/get_guiadocente.php) -> Markdown.

Plantilla PDF (TCPDF, con texto): apartados numerados 1..14 ("N. Título"):
1 Denominación · 2 Materia/módulo · 3 Departamento · 4.a Profesorado y 4.b Coordinación (se descartan) · 5 Curso y semestre ·
6 Tipo · 7 ECTS · 8 Competencias/resultados · 9 Programa (9.1 objetivos, 9.2 unidades/contenidos, 9.3 enlace a Leganto) ·
10 Metodología · 11 Sistemas de evaluación · 12 Recursos · 13 Calendarios (se descarta) · 14 Idioma.
Cada página lleva cabecera (UNIVERSIDAD DE BURGOS + departamento) y pie ("- n -"), que se quitan.
La bibliografía es solo un enlace a Leganto (no se puede leer): bibliography=False salvo que el texto contenga referencias.
Uso: python universidades/es_burgos/scraper_es_burgos.py [--sample N | --all | --codes C...]
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_burgos"
# Cálculo (1º), Ampliación (1º), Térmica I (2º), Diseño Máquinas II (4º), Equilibrado (optativa), Prácticas, TFG
SAMPLE = ["6302", "6307", "6312", "6333", "6339", "6343", "6342"]
DROP = {"4", "13"}  # profesorado/coordinación y calendarios
_SEC = re.compile(r"^(\d{1,2})(\.[ab])?\.?\s+(\S.*)$")
_SUB = re.compile(r"^(\d{1,2}\.\d)-\s*(.*)$")
_PAGE = re.compile(r"^- \d+ -$")


class GuideError(Exception):
    pass


def get_lines(data: bytes) -> list[str]:
    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for pg in pdf.pages:
            ls = [l.strip() for l in (pg.extract_text() or "").split("\n")]
            clean, skip_next = [], False
            for l in ls:
                if skip_next:  # línea de departamento tras la cabecera
                    skip_next = False
                    continue
                if l == "UNIVERSIDAD DE BURGOS":
                    skip_next = True
                    continue
                if not l or _PAGE.match(l) or l.startswith("Powered by TCPDF"):
                    continue
                clean.append(l)
            out += clean
    return out


_TITLES = re.compile(r"^(Denominaci|Materia o m|Departamento|Profesor|Coordinador|Curso y semestre|Tipo de la asignatura|"
                     r"Requisitos|Número de cr|Competencias|Programa|Metodolog|Sistemas de evaluaci|Recursos de aprendizaje|"
                     r"Calendarios|Idioma)", re.I)


def sections(lines):
    """Cada apartado empieza por 'N. Título' con un título de la plantilla (la numeración cambia entre guías)."""
    head, secs, cur = [], [], None
    for l in lines:
        m = _SEC.match(l)
        if m and _TITLES.match(m.group(3)):
            t = m.group(3)
            key = "DROP" if re.match(r"(Profesor|Coordinador|Calendarios)", t, re.I) else ("1" if t.lower().startswith("denominaci") else m.group(1))
            cur = [key, l, []]
            secs.append(cur)
        elif cur is None:
            head.append(l)
        else:
            cur[2].append(l)
    return head, secs


def render_body(lines: list[str]) -> str:
    out = []
    for l in lines:
        m = _SUB.match(l)
        if m:
            out += ["", f"### {m.group(1)} {m.group(2)}".strip(), ""]
        elif re.match(r"^[•\-–] ", l):
            out.append("- " + l[2:])
        else:
            out.append(l)
    return "\n".join(out).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    data = http.get_bytes(e["url_guia_docente"])
    if not data.startswith(b"%PDF"):
        raise GuideError("no es un PDF")
    lines = get_lines(data)
    head, secs = sections(lines)
    if len(secs) < 8 or code not in "\n".join(lines[:60]):
        raise GuideError(f"estructura inesperada ({len(secs)} apartados) o no corresponde a la asignatura")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    blocks = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False,
              "prerequisites": False}
    allbody = []
    for num, title, body in secs:
        if num in ("DROP", "1"):
            continue
        b = render_body(body)
        t = re.sub(r":$", "", title)
        md += [f"## {t}", ""] + ([b, ""] if b else [])
        tl = title.lower()
        if tl[3:].startswith("competencias") or "competencias //" in tl:
            blocks["learning_outcomes"] |= len(b) > 40
        if re.search(r"^\d+\.\s*programa", tl):
            blocks["contents"] |= bool(re.search(r"unidades docentes|contenidos", b, re.I)) and len(b) > 80
        if "sistemas de evaluaci" in tl:
            blocks["assessment"] |= len(b) > 40
        if re.search(r"^\d+\.\s*requisitos", tl):
            blocks["prerequisites"] |= len(b) > 3
        allbody.append((num, b))
    full = "\n".join(b for _, b in allbody)
    blocks["bibliography"] = bool(re.search(r"\(\d{4}\)|ISBN|Ed\.|Editorial", full))
    if not blocks["learning_outcomes"] and not blocks["contents"]:
        raise GuideError("guía sin competencias ni programa")
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    if a.all:
        codes = [c for c, r in rows.items() if r["tipo_fuente"] != "sin_guia"]
    else:
        codes = a.codes or SAMPLE[: a.sample or 5]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = 0
    for c in codes:
        e = rows.get(c)
        if not e:
            print(f"FALLO {c}: no está en el catálogo")
            fail += 1
            continue
        try:
            p, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} ({p.stat().st_size} B)"
                  + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c} {e['nombre_asignatura']}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
