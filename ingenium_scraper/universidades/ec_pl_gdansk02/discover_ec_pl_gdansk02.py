"""Fase 1 - Gdansk University of Technology (PL GDANSK02) - Mechanical Engineering (WIMiO), first-cycle, English, specialization Design and Production Engineering.
Fuente: ECTS Catalog (ects.pg.edu.pl, HTML estatico, sin robots.txt -> permitido): lista de asignaturas por semestre + ficha PDF por asignatura
(ects.pg.edu.pl/en/subjects/{id}/card.pdf). El codigo oficial "PG_xxxxxxxx" se lee de la ficha.
Uso (desde la raiz): python universidades/ec_pl_gdansk02/discover_ec_pl_gdansk02.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_gdansk02"
UNIVERSIDAD = "Gdańsk University of Technology (Politechnika Gdańska)"
GRADO = "Mechanical Engineering, first-cycle (engineer), specialization Design and Production Engineering"
URL_PLAN = "https://ects.pg.edu.pl/en/courses/16309/subcourses/16310/subjects"  # cohorte 2023/2024: ya tiene fichas de los 7 semestres


def card_header(path: Path) -> dict:
    with pdfplumber.open(path) as pdf:
        t = pdf.pages[0].extract_text() or ""
    code = re.search(r"Subject name and code\s+(.+?),\s*(PG_\w+)", t)
    lang = re.search(r"Language of instruction\s+(\w+)", t)
    return {"code": code.group(2) if code else None, "lang": lang.group(1) if lang else None}


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL_PLAN), "lxml")
    rows, seen, langs, nocode = [], set(), {}, 0
    for blk in soup.select(".data-table-semester"):
        sem = int(re.search(r"Semester:\s*(\d+)", blk.select_one("h3").get_text(" ", strip=True)).group(1))
        for tr in blk.select(".data-table__row"):
            cells = tr.select(".cell")
            nombre = re.sub(r"\s+", " ", cells[0].get_text(" ", strip=True))
            vals = [x.get_text(strip=True) for x in cells[1].select(".cell__inner")]
            ects = float(vals[0]) if vals and re.fullmatch(r"\d+(\.\d+)?", vals[0]) else None
            a = cells[2].find("a", href=True)
            if not a:
                continue
            url = a["href"]
            hdr = card_header(http.get_file(url))
            code = hdr["code"] or "PGSUBJ_" + url.split("/subjects/")[1].split("/")[0]
            nocode += hdr["code"] is None
            langs[hdr["lang"]] = langs.get(hdr["lang"], 0) + 1
            if code in seen:
                continue
            seen.add(code)
            low = nombre.lower()
            car = "tfg" if re.search(r"diploma|bachelor.?s thesis|thesis", low) else ("practicas" if "internship" in low or "practice" in low else "obligatoria")
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=f"Semester {sem}", curso=(sem + 1) // 2, semestre=sem, creditos_ects=ects, caracter=car,
                idioma_pagina="en", url_guia_docente=url, tipo_fuente="pdf"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2023-2024 (cohorte de inicio; fichas 2023/24-2026/27)",
        url_plan_estudios=URL_PLAN, ects_totales_plan=None,
        estrategia_fuente="HTML estatico del ECTS Catalog de la PG (listas por semestre) + ficha PDF por asignatura (texto)",
        generado_por="discover_ec_pl_gdansk02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Mechanical Engineering (Faculty of Mechanical Engineering and Ship Technology), grado de ingeniería de 7 semestres impartido en inglés; "
               "las 2 filas del Excel son Ing. Química Industrial y Grado en Ing. de Tecnologías Industriales: la más afín a Tecnologías Industriales y de prioridad "
               "Mecánica es Mechanical Engineering (la alternativa Chemical Technology existe pero es en polaco/menos afín). Se cataloga la especialización única "
               "'Design and Production Engineering' (incluye el tronco común) de la COHORTE 2023/2024: la cohorte 2026/27 solo tiene fichas publicadas para los semestres 1-2. "
               f"Código = 'PG_…' oficial de la ficha. Idiomas de las fichas (Language of instruction): {langs}. Fichas sin código: {nocode}. Suma ECTS={total:g}; "
               "el total oficial del plan (≈210 ECTS, 7 semestres) no se pudo comprobar en la fuente: la suma incluye bloques optativos/idioma si figuran como filas."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(len(rows), "asignaturas; ECTS", total, langs, "sin codigo", nocode)


if __name__ == "__main__":
    main()
