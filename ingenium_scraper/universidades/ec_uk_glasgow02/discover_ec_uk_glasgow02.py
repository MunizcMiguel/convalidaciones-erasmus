"""Fase 1 - University of Strathclyde (UK GLASGOW02), Dept. of Mechanical and Aerospace Engineering.
Grado: BEng with Honours in Mechanical Engineering (4 anos; 480 creditos SCQF = 240 ECTS). Fuente: regulaciones academicas 2026/27 (PDF con texto) que
listan los modulos obligatorios por curso. Cada modulo tiene un Module Description Form (PDF) en /media/departments/mechanicalengineering/mdf/{codigo}.pdf.
Uso: python universidades/ec_uk_glasgow02/discover_ec_uk_glasgow02.py
"""
from __future__ import annotations

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
SLUG = "ec_uk_glasgow02"
REG = "https://www.strath.ac.uk/media/1newwebsite/documents/academicregulations26x2f27/engineeringug/2026-27_Mechanical_Engineering.pdf"
MDF = "https://www.strath.ac.uk/media/departments/mechanicalengineering/mdf/{code}.pdf"
GRADO = "BEng (Hons) Mechanical Engineering"
UNIV = "University of Strathclyde - Department of Mechanical and Aerospace Engineering"
YEARS = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5}
ROW = re.compile(r"^([A-Z]{0,3}\d{3,5}) (.+?) ([1-5]) (\d+)$")


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    with pdfplumber.open(c.get_file(REG)) as pdf:
        text = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
    year, sub, entries, seen = 0, None, [], set()
    for line in text.split("\n"):
        s = line.strip()
        m = re.match(r"^\d\. (First|Second|Third|Fourth|Fifth) Year", s)
        if m:
            year, sub = YEARS[m.group(1)], None
            continue
        if year >= 5:
            break  # 5.º curso = MEng
        if s == "Aero-Mechanical Engineering":
            sub = "aero"
        elif s in ("Mechanical Engineering", "Mechanical Engineering with International Study"):
            sub = "mech"
        elif s == "Compulsory Modules":
            sub = None
        r = ROW.match(s)
        if not r or sub == "aero" or not year:
            continue
        code, title, level, cr = r.group(1), r.group(2).strip(), int(r.group(3)), int(r.group(4))
        if code in seen:
            continue
        seen.add(code)
        entries.append(CatalogEntry(
            universidad=UNIV, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title, curso_semestre=f"Curso {year}", curso=year, semestre=None,
            creditos_ects=cr / 2, caracter="tfg" if "individual project" in title.lower() else "obligatoria", idioma_pagina="en",
            url_guia_docente=MDF.format(code=code), tipo_fuente="pdf"))
    # comprobar qué MDF son públicos: los no autorizados devuelven una página HTML "Page not authorised" con HTTP 200
    sin = []
    for e in entries:
        if not c.get_bytes(e.url_guia_docente).startswith(b"%PDF"):
            e.tipo_fuente, e.url_guia_docente = "sin_guia", None
            sin.append(e.codigo_asignatura)
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIV, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/27", url_plan_estudios=REG, ects_totales_plan=240.0,
        estrategia_fuente="PDF de regulaciones académicas 2026/27 (texto) + Module Description Form en PDF por módulo", generado_por="discover_ec_uk_glasgow02.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: BEng with Honours in Mechanical Engineering (4 años; 120 créditos SCQF por curso = 60 ECTS, se usa créditos/2 como ECTS; plan de 240 ECTS). "
               f"{len(entries)} módulos obligatorios de los cursos 1-4 (suma {tot:g} ECTS de 240); faltan los módulos optativos (Elective Module(s): 20 créditos en 1.º, 10 en 2.º) y las listas de optativas, "
               "que las regulaciones no detallan. Se excluye el 5.º curso (MEng) y los módulos propios de Aero-Mechanical. Los MDF públicos se comprueban aquí: los que devuelven «Page not authorised» (acceso restringido, no se intenta sortear) quedan sin_guia: " + ", ".join(sin) + ". "
               "robots.txt de www.strath.ac.uk sin reglas relevantes. Códigos tal como figuran en las regulaciones; cohorte 2026/27."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos; ECTS", tot)
    from collections import Counter
    print(Counter(e.curso for e in entries))


if __name__ == "__main__":
    main()
