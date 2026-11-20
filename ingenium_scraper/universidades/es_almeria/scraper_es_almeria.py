#!/usr/bin/env python3
"""Fase 2 — Universidad de Almería: guías docentes PDF (www.ual.es/guia_academica/{cod}/{curso}/CAS) -> Markdown.

Estructura del PDF (títulos en mayúsculas): ASIGNATURA · PLAN/ES DONDE SE IMPARTE · PROFESOR/A RESPONSABLE (se descarta) ·
PROFESORADO (se descarta) · ELEMENTOS DE INTERÉS (justificación, requisitos) · RESULTADOS DEL PROCESO DE FORMACIÓN ·
PLANIFICACIÓN (temario) · metodologías · Diversidad Funcional (texto estándar, se descarta) · PROCEDIMIENTO DE EVALUACIÓN · RECURSOS.
Uso: python universidades/es_almeria/scraper_es_almeria.py [--sample N | --all | --codes C...]
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
SLUG = "es_almeria"
# 1º mates, 1º dibujo, 2º mecánica, 3º diseño, 3º optativa electrónica, 4º prácticas, 4º TFG
SAMPLE = ["44101101", "44101109", "29102224", "29103211", "43104216", "29104224", "29104227"]

EI = "ELEMENTOS DE INTERÉS PARA EL APRENDIZAJE DE LA ASIGNATURA"
RES = "RESULTADOS DEL PROCESO DE FORMACIÓN Y DE APRENDIZAJE"
TOP = {"ASIGNATURA": None, "PLAN/ES DONDE SE IMPARTE": None, "PROFESOR/A RESPONSABLE O COORDINADOR/A": None,
       "PROFESORADO": None, EI: "Elementos de interés", RES: "Resultados del proceso de formación y de aprendizaje",
       "PLANIFICACIÓN": "Planificación", "PROCEDIMIENTO DE EVALUACIÓN": "Procedimiento de evaluación",
       "RECURSOS": "Recursos"}
SUB = ["Justificación de los contenidos", "Materia con la que se relaciona en el Plan de Estudios",
       "Conocimientos necesarios para abordar la asignatura", "Requisitos previos recogidos en la memoria de la Titulación",
       "Competencias", "Competencias básicas", "Competencias transversales de la UAL", "Competencias específicas",
       "Conocimientos o contenidos", "Habilidades o destrezas", "Actitudes o valores", "Temario",
       "Actividades Formativas y Metodologías Docentes", "Sistemas de evaluación", "Criterios",
       "Bibliografía básica", "Bibliografía complementaria", "Bibliografía", "Metodologías docentes", "Actividades formativas"]


def _norm(l: str) -> str:
    return re.sub(r"[\s.:]", "", l).lower()


SUBN = {_norm(s): s for s in SUB}
_FOOT = re.compile(r"^Fecha ficha docente:.*Página \d+ de \d+$")


class GuideError(Exception):
    pass


def lines_of(data: bytes) -> list[str]:
    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for pg in pdf.pages:
            out += (pg.extract_text(x_tolerance=1.2) or "").split("\n")
    return [l.strip() for l in out if l.strip() and not _FOOT.match(l.strip())]


def split_top(lines):
    head, secs, cur = [], {}, None
    for l in lines:
        if l in TOP:
            cur = l
            secs[cur] = []
        elif cur is None:
            head.append(l)
        else:
            secs[cur].append(l)
    return head, secs


def render(body: list[str]) -> str:
    md, skip = [], False
    for l in body:
        k = _norm(l)
        if k == "diversidadfuncional":
            skip = True
            continue
        if k in SUBN and len(l) < 70:
            skip = False
            md += ["", f"### {SUBN[k]}", ""]
            continue
        if skip or l.startswith("Enlace catálogo biblioteca"):
            continue
        if re.match(r"^[••�\-]\s", l) or re.match(r"^[••�]", l):
            md.append("- " + re.sub(r"^[••�\-]\s*", "", l))
        else:
            md.append(l)
    return "\n".join(md).strip()


def section_text(md: str, title: str) -> str:
    m = re.search(rf"### {re.escape(title)}\n\n(.*?)(?=\n### |\Z)", md, re.S)
    return m.group(1).strip() if m else ""


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    data = http.get_bytes(e["url_guia_docente"])
    if not data.startswith(b"%PDF"):
        raise GuideError("no es un PDF")
    lines = lines_of(data)
    head, secs = split_top(lines)
    if code not in "".join("\n".join(secs.get("ASIGNATURA", []) + head).split()):
        raise GuideError("el PDF no corresponde a la asignatura")
    info = secs.get("ASIGNATURA", [])
    mine, grab = [], False
    for l in secs.get("PLAN/ES DONDE SE IMPARTE", []):
        if l.startswith("Plan:"):
            grab = "Ingeniería Mecánica" in l and "Doble" not in l
        if grab:
            mine.append(l)
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    if info:
        md += ["## Datos de la asignatura", ""] + [f"- {l}" for l in info] + [""]
    if mine:
        md += ["### Plan donde se imparte", ""] + [f"- {l}" for l in mine] + [""]
    texts = {}
    for k, title in TOP.items():
        if title is None or k not in secs:
            continue
        body = render(secs[k])
        if body:
            texts[k] = body
            md += [f"## {title}", "", body, ""]
    pl = texts.get("PLANIFICACIÓN", "")
    res = texts.get(RES, "")
    tem = section_text(pl, "Temario") or section_text(res, "Conocimientos o contenidos")
    ei = texts.get(EI, "")
    pre = section_text(ei, "Requisitos previos recogidos en la memoria de la Titulación") or \
        section_text(ei, "Conocimientos necesarios para abordar la asignatura")
    bl = {"contents": len(tem) > 20, "learning_outcomes": len(res) > 40,
          "assessment": len(texts.get("PROCEDIMIENTO DE EVALUACIÓN", "")) > 40,
          "bibliography": bool(re.search(r"^- ", texts.get("RECURSOS", ""), re.M)),
          "prerequisites": len(pre) > 3}
    if not (bl["contents"] or bl["learning_outcomes"]):
        raise GuideError("guía sin contenidos ni resultados")
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
