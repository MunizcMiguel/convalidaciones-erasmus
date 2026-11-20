#!/usr/bin/env python3
"""Fase 2 — Universidad de La Laguna: guías docentes PDF (www.ull.es/apps/guias/guias/print_guide/{id}/) -> Markdown.

PDF generado con ReportLab (con texto). Apartados numerados: 1 Datos descriptivos · 2 Requisitos de matrícula y calificación ·
3 Profesorado (nombres, teléfonos, correos, tutorías: se descarta) · 4 Contextualización · 5 Competencias · 6 Contenidos ·
7 Metodología y volumen de trabajo · 8 Bibliografía / Recursos · 9 Sistema de evaluación y calificación · 10 Resultados de aprendizaje ·
11 Cronograma (se descarta). Los listados internos también usan "1. ..." por eso los apartados se reconocen por título y orden.
Cada página repite "Última modificación: ... Página n de m"; la primera lleva una cabecera de 7 líneas.
Uso: python universidades/es_laguna/scraper_es_laguna.py [--sample N | --all | --codes C...]
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
SLUG = "es_laguna"
# Física I (1º), Fundamentos Matemáticos (1º), Mecánica de Máquinas (2º), Ingeniería Térmica (2º), Tecnología Mecánica (3º),
# optativa, Prácticas Externas, TFG
SAMPLE = ["339401101", "339401104", "339402202", "339402203", "339403104", "339403901", "339404202", "339404203"]

SECS = [("1", r"Datos descriptivos"), ("2", r"Requisitos de matrícula"), ("3", r"Profesorado"), ("4", r"Contextualización"),
        ("5", r"Competencias"), ("6", r"Contenidos"), ("7", r"Metodología"), ("8", r"Bibliograf"),
        ("9", r"Sistema de evaluaci"), ("10", r"Resultados de [Aa]prendizaje"), ("11", r"Cronograma")]
DROP = {"3", "11"}
_PAGE = re.compile(r"^Última modificación: .* Página \d+ de \d+$")


class GuideError(Exception):
    pass


def get_lines(data: bytes) -> list[str]:
    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for pg in pdf.pages:
            for l in (pg.extract_text(x_tolerance=1.5) or "").split("\n"):
                l = l.strip()
                if l and not _PAGE.match(l):
                    out.append(l)
    return out


def split(lines):
    head, secs, cur, k = [], {}, None, 0
    for l in lines:
        if k < len(SECS):
            num, pat = SECS[k]
            m = re.match(rf"^{num}\. ({pat}.*)$", l)
            if m:
                cur = num
                secs[cur] = [m.group(1)]
                k += 1
                continue
        if cur is None:
            head.append(l)
        else:
            secs[cur].append(l)
    return head, secs


def fmt(lines: list[str]) -> str:
    out = []
    for l in lines:
        if re.match(r"^[•\-–] ", l):
            out.append("- " + l[2:])
        else:
            out.append(l)
    return "\n".join(out).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    data = http.get_bytes(e["url_guia_docente"])
    if not data.startswith(b"%PDF"):
        raise GuideError("no es un PDF")
    head, secs = split(get_lines(data))
    if len(secs) < 9 or f"Código: {code}" not in "\n".join(secs.get("1", [])):
        raise GuideError(f"estructura inesperada ({len(secs)} apartados) o no corresponde a la asignatura")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    bodies = {}
    for num, _ in SECS:
        if num in DROP or num not in secs:
            continue
        title, *body = secs[num]
        if num == "1":  # fuera horario/web/centro repetido
            body = [l for l in body if not re.match(r"^- (Horario|Dirección web)", l)]
        b = fmt(body)
        bodies[num] = b
        md += [f"## {num}. {title}", ""] + ([b, ""] if b else [])
    req = bodies.get("2", "")
    bl = {"contents": len(bodies.get("6", "")) > 40,
          "learning_outcomes": len(bodies.get("10", "")) > 20 or len(bodies.get("5", "")) > 40,
          "assessment": len(bodies.get("9", "")) > 40,
          "bibliography": len(bodies.get("8", "")) > 30,
          "prerequisites": len(req) > 5 and not re.fullmatch(r"(?i)(ninguno|no (hay|existen?|se exige).{0,70}|ninguna.{0,20})\.?", req.strip())}
    if not (bl["contents"] or bl["learning_outcomes"]):
        raise GuideError("guía sin contenidos ni competencias")
    return write_markdown(SLUG, e, "\n".join(md), bl), bl


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
