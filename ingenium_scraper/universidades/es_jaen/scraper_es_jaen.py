#!/usr/bin/env python3
"""Fase 2 — Universidad de Jaén: fichas docentes PDF (uvirtual.ujaen.es/.../catalogofichasdocentesasignaturas/...) -> Markdown.

OJO: la URL acaba en `.html` pero el servidor devuelve un PDF (con texto). Estructura (títulos en mayúsculas):
FICHA IDENTIFICATIVA · PROFESORADO (coordinación y cuadro docente con correos/teléfonos/despachos: se descarta entero) ·
RESUMEN (conocimientos previos y recomendaciones, breve resumen, prerrequisitos) · DESCRIPCIÓN DE CONTENIDOS ·
METODOLOGÍAS DOCENTES Y ACTIVIDADES FORMATIVAS · SISTEMAS DE EVALUACIÓN · OBJETIVOS DE DESARROLLO SOSTENIBLE ·
BIBLIOGRAFÍA · COMPETENCIAS / RESULTADOS DEL PROCESO DE FORMACIÓN Y APRENDIZAJE · y cláusulas estándar (se descartan).
Cada página repite cabecera ("Guía Docente", "{código} - {nombre}", "Curso Académico") y pie ("{nombre} Página n de m").
Uso: python universidades/es_jaen/scraper_es_jaen.py [--sample N | --all | --codes C...]
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
SLUG = "es_jaen"
# Física I (1º), Matemáticas I (1º), Mecánica de fluidos (2º), Diseño de máquinas (3º), TFG, una optativa, prácticas externas
SAMPLE = ["13411005", "13411009", "13412016", "13412005", "13416001", "13413015", "13413012"]

TOP = ["FICHA IDENTIFICATIVA", "PROFESORADO", "RESUMEN", "DESCRIPCIÓN DE CONTENIDOS",
       "METODOLOGÍAS DOCENTES Y ACTIVIDADES FORMATIVAS", "SISTEMAS DE EVALUACIÓN", "OBJETIVOS DE DESARROLLO SOSTENIBLE",
       "BIBLIOGRAFÍA", "COMPETENCIAS / RESULTADOS DEL PROCESO DE FORMACIÓN Y APRENDIZAJE",
       "ESTUDIANTADO CON NECESIDADES ESPECÍFICAS DE APOYO EDUCATIVO", "PLAN DE CONTINGENCIA", "CLÁUSULAS",
       "COMPROMISO CON LA IGUALDAD Y LA PERSPECTIVA DE GÉNERO"]
KEEP = {"FICHA IDENTIFICATIVA": "Ficha identificativa", "RESUMEN": "Resumen", "DESCRIPCIÓN DE CONTENIDOS": "Descripción de contenidos",
        "METODOLOGÍAS DOCENTES Y ACTIVIDADES FORMATIVAS": "Metodologías docentes y actividades formativas",
        "SISTEMAS DE EVALUACIÓN": "Sistemas de evaluación", "BIBLIOGRAFÍA": "Bibliografía",
        "COMPETENCIAS / RESULTADOS DEL PROCESO DE FORMACIÓN Y APRENDIZAJE": "Competencias y resultados del proceso de formación y aprendizaje"}
_FOOT = re.compile(r"^.+ Página \d+ de \d+$")
_SUBH = {"Conocimientos previos y recomendaciones", "Breve resumen de la asignatura (según memoria RUCT)", "Prerrequisitos"}


class GuideError(Exception):
    pass


def get_lines(data: bytes) -> list[str]:
    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for pg in pdf.pages:
            for l in (pg.extract_text(x_tolerance=1.5) or "").split("\n"):
                l = l.strip()
                if not l or l == "Guía Docente" or l.startswith("Curso Académico ") or _FOOT.match(l):
                    continue
                if re.fullmatch(r"\d{8} - .+", l):  # cabecera "código - nombre"
                    continue
                out.append(l)
    return out


def split(lines):
    secs, cur = {}, None
    for l in lines:
        if l in TOP:
            cur = l
            secs[cur] = []
        elif cur:
            secs[cur].append(l)
    return secs


def fmt(lines: list[str]) -> str:
    out = []
    for l in lines:
        if l in _SUBH or re.match(r"^(RECOMENDACIONES Y ADAPTACIONES CURRICULARES):$", l):
            out += ["", f"### {l.rstrip(':').capitalize() if l.isupper() else l}", ""]
        elif re.match(r"^[•\-–]\s", l):
            out.append("- " + l[2:])
        else:
            out.append(l)
    return "\n".join(out).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    data = http.get_bytes(e["url_guia_docente"])
    if not data.startswith(b"%PDF"):
        raise GuideError("la respuesta no es un PDF")
    lines = get_lines(data)
    secs = split(lines)
    ident = "\n".join(secs.get("FICHA IDENTIFICATIVA", []))
    nm = re.search(r"Nombre: (.+)", ident)
    same_name = bool(nm) and nm.group(1).strip().lower() == e["nombre_asignatura"].strip().lower()
    # algunas asignaturas comunes enlazan la ficha de otro grado (otro código, mismo nombre): se acepta por nombre
    if f"Código: {code}" not in ident and not same_name:
        raise GuideError("la ficha no corresponde a la asignatura")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    texts = {}
    for k, title in KEEP.items():
        ls = secs.get(k)
        if not ls:
            continue
        if k == "FICHA IDENTIFICATIVA":  # fuera enlaces de tutorías/horarios/plataforma
            ls = [l for l in ls if not re.match(r"^(Tutorías:|Temporalidad|Plataforma de teleformación|https?://)", l)]
        body = fmt(ls)
        if body:
            texts[k] = body
            md += [f"## {title}", "", body, ""]
    res = texts.get("RESUMEN", "")
    pre = re.search(r"### (?:Conocimientos previos y recomendaciones|Prerrequisitos)\n\n(.+?)(?=\n###|\Z)", res, re.S)
    prereq_text = " ".join(m.strip() for m in re.findall(r"### (?:Conocimientos previos y recomendaciones|Prerrequisitos)\n\n(.+?)(?=\n###|\Z)", res, re.S))
    bl = {"contents": len(texts.get("DESCRIPCIÓN DE CONTENIDOS", "")) > 30,
          "learning_outcomes": len(texts.get("COMPETENCIAS / RESULTADOS DEL PROCESO DE FORMACIÓN Y APRENDIZAJE", "")) > 40,
          "assessment": len(texts.get("SISTEMAS DE EVALUACIÓN", "")) > 40,
          "bibliography": len(texts.get("BIBLIOGRAFÍA", "")) > 30,
          "prerequisites": bool(pre) and len(prereq_text) > 25 and not re.fullmatch(r"(?is)(no hay prerrequisitos\.?\s*)+", prereq_text.strip())}
    if not (bl["contents"] or bl["learning_outcomes"]):
        raise GuideError("ficha sin contenidos ni competencias")
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
