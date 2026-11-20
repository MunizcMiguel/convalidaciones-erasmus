#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Univerza v Ljubljani, Fakulteta za strojništvo (FS).

Fuente: PDF «Erasmus+ programme curriculum 2026/27» (ERASMUS-1.pdf, en inglés, 38 págs.): índice (p. 2)
con códigos de asignatura y una ficha por página (p. 3-38). Son asignaturas de MÁSTER (código NNNN-M);
ver notas del catálogo.

Uso: python universidades/ec_si_ljublja01/discover_ec_si_ljublja01.py
"""
from __future__ import annotations

import difflib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_si_ljublja01"
UNIVERSIDAD = "Univerza v Ljubljani (Fakulteta za strojništvo)"
PDF = "https://www.fs.uni-lj.si/wp-content/uploads/2026/06/ERASMUS-1.pdf"
PLAN = "https://www.fs.uni-lj.si/en/study/international-exchange-students/programme-information/"
GRADO = "Mechanical Engineering (2nd cycle, Erasmus+ subjects, Research and Development programme)"


def norm(s: str) -> str:
    return re.sub(r"[^a-z]+", " ", s.lower()).strip()


def split_head(text: str) -> tuple[str, float, list[str]]:
    """(título, ECTS, líneas restantes). Soporta títulos partidos en 2-3 líneas."""
    lines = text.split("\n")
    m = re.match(r"^(.*?)\s*(\d+)\s*ECTS\s*(.*)$", lines[0])
    if m:
        return (m.group(1) + " " + m.group(3)).strip(), float(m.group(2)), lines[1:]
    m = re.match(r"^(\d+)\s*ECTS\s*(.*)$", lines[1])
    if m:
        tail = m.group(2)
        k = 2
        if not tail and not lines[2].startswith("Lecturer"):
            tail, k = lines[2], 3
        return (lines[0] + " " + tail).strip(), float(m.group(1)), lines[k:]
    raise ValueError("cabecera no reconocida: " + lines[0])


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    path = http.get_file(PDF)
    with pdfplumber.open(path) as d:
        pages = [(p.extract_text() or "") for p in d.pages]
    index = pages[1]
    # índice: dos columnas (winter | summer) -> cada línea con 'Nombre (NNNN-M)'
    idx = []   # (nombre, código, semestre)
    for line in index.split("\n"):
        for k, m in enumerate(re.finditer(r"\s*([^()]+?)\s*\((\d{4}-M)\)", line)):
            idx.append((m.group(1).strip(), m.group(2), k))
    entries = []
    used = set()
    for pno in range(3, len(pages) + 1):
        txt = pages[pno - 1]
        title, ects, _ = split_head(txt)
        cands = [(difflib.SequenceMatcher(None, norm(title), norm(n)).ratio(), n, c, s) for n, c, s in idx if c not in used]
        score, n, code, sem = max(cands)
        assert score > 0.6, (title, n, score)
        used.add(code)
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
            curso_semestre=f"{'Winter' if sem == 0 else 'Summer'} semester 2026/27 (Erasmus+ subject list)",
            curso=None, semestre=None, creditos_ects=ects, caracter="optativa", idioma_pagina="en",
            url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{pno}-{pno}"))
    assert len(entries) == len(used) == len(set(e.codigo_asignatura for e in entries))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="master", curso_academico="2026/27",
        url_plan_estudios=PLAN, ects_totales_plan=None,
        estrategia_fuente="PDF compartido en inglés de la facultad: índice (p.2) + una ficha por página (p.3-38).",
        generado_por="discover_ec_si_ljublja01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("PARCIAL respecto a la tarea (grado). Única fila Erasmus de Ljubljana = Máster Universitario en Ingeniería Industrial (ISCED 0715, 2 plazas). "
               "Grado afín: Mechanical Engineering (UN, 'Research and Development Programme', 180 ECTS, 3 años; también existe la versión profesional PAP), pero sus fichas "
               "de asignatura no son públicas en inglés: el plan 2026/27 (UNI_PREDMETNIK2627.pdf) solo lista asignaturas y los 'Zbornik' (RRP/PAP) solo describen el programa (12 págs.) "
               "y no hay sitio de catálogo de syllabi localizado. Lo único con fichas completas en inglés son las 36 asignaturas de MÁSTER Mechanical Engineering que el FS ofrece a "
               "estudiantes Erasmus+ (PDF ERASMUS-1.pdf, 5 ECTS cada una, códigos NNNN-M; ERASMUS-2.pdf, para 2027/28-2028/29, repite el mismo contenido): se recogen esas fichas como catálogo "
               "con nivel='master' porque coincide con la fila Uniovi (Máster). Sin curso/semestre de plan (son optativas ofertadas por semestre: Winter/Summer). "
               "Las fichas traen Lecturer (se elimina), horas, Objectives, Programme, Prerequisites, Learning outcomes, Assessment y Literature."))
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(entries)} asignaturas; HTTP {http.stats}")


if __name__ == "__main__":
    main()
