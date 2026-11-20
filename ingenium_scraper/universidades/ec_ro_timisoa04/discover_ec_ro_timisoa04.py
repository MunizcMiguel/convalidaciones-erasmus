"""Fase 1 - Universitatea Politehnica Timisoara (UPT) - Inginerie Mecanica / Mechanical Engineering (licenta, 4 anos).

Fuente: Course catalogue Erasmus 2025-26 de la Facultad de Mecanica (Excel, hoja Bachelor, codigos L431) + fichas
(Fisa disciplinei) de los Word de la facultad, unidos por prepare_fuente_previa.py en fuente_previa/upt_cursos.json.
Uso: python universidades/ec_ro_timisoa04/discover_ec_ro_timisoa04.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_ro_timisoa04"
UNIVERSIDAD = "Universitatea Politehnica Timișoara (UPT)"
GRADO = "Inginerie Mecanică / Mechanical Engineering (licență)"
URL_CATALOGO = "https://international.upt.ro/en/incoming-students/course-catalogue/"


def main() -> None:
    cursos = json.loads((HERE / "fuente_previa" / "upt_cursos.json").read_text(encoding="utf-8"))
    seen: set[str] = set()
    codes_used: dict[str, int] = {}
    entries = []
    for c in cursos:
        code, name = c["code"], c["name"].strip()
        key = f"{code}|{name.lower()}"
        if key in seen:
            continue  # fila repetida
        seen.add(key)
        codes_used[code] = codes_used.get(code, 0) + 1
        if codes_used[code] > 1:
            code = f"{code}-{hashlib.md5(name.lower().encode()).hexdigest()[:4]}"  # mismo codigo, otra asignatura
        has = bool(c["sections"].get("Objectives") or c["sections"].get("Lecture Program"))
        low = name.lower()
        caracter = "tfg" if ("diplom" in low and "practic" not in low) else "optativa" if "-0" in c["code"].split(".")[-1] else "obligatoria"
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
            curso_semestre=f"Curso {c['year']} / Semestre {c['semester']} (docencia: {c['teaching_language'] or 'n/d'})",
            curso=c["year"], semestre=c["semester"], creditos_ects=c["ects"], caracter=caracter, idioma_pagina="ro",
            url_guia_docente=URL_CATALOGO if has else None, tipo_fuente="html" if has else "sin_guia"))
    entries.sort(key=lambda e: (e.semestre or 0, e.codigo_asignatura))
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/26", url_plan_estudios=URL_CATALOGO,
        ects_totales_plan=240.0,
        estrategia_fuente="Excel Course catalogue Erasmus (Facultatea de Mecanică) + fichas Fișa disciplinei (Word) ya extraídas por el usuario",
        generado_por="discover_ec_ro_timisoa04.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Inginerie Mecanică (Mechanical Engineering), licență, 4 años/240 ECTS, códigos L431. Es la hoja Bachelor del catálogo Erasmus de la Facultad de Mecánica: "
               f"incluye optativas (sufijo -0x) y mezcla cohortes (L431.21-25), por lo que los {tot:g} ECTS de {len(entries)} filas superan los 240 del plan. "
               "No se localizó en international.upt.ro el enlace de descarga del Excel (la página del catálogo no lo expone en el HTML estático; no se usó navegador): "
               "url_guia_docente apunta a la página del catálogo. Los datos proceden de la descarga previa del usuario (Excel + Word de la facultad). "
               "Las fichas están en rumano (unas 33 asignaturas se imparten en inglés, indicado en curso_semestre); las filas sin ficha (proyecto/examen de diploma, etc.) son sin_guia. "
               "Objetivos/programa son resúmenes cortos extraídos de plantillas Word; 'Evaluation' incluye la tabla 10.x de la ficha."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas;", sum(e.tipo_fuente == "html" for e in entries), "con ficha; ECTS", tot)


if __name__ == "__main__":
    main()
