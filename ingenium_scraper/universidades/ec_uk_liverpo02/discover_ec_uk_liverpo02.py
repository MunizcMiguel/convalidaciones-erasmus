"""Fase 1 - Liverpool John Moores University - BEng (Hons) Mechanical Engineering (3 anios, 360 creditos UK = 180 ECTS).

Fuente: Programme Specification oficial (PDF, prodcat.ljmu.ac.uk, programa 32120-3500006811 v03.01), tabla de modulos por nivel (4, 5, 6; core / option).
Las fichas de modulo (module specifications) NO son accesibles: las paginas de www.ljmu.ac.uk estan vetadas por robots.txt para PoliteClient
(incluido robots.txt, que se trata como deny-all) -> regla de parada; todas las filas quedan `sin_guia`.
Uso: python universidades/ec_uk_liverpo02/discover_ec_uk_liverpo02.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_uk_liverpo02"
UNIVERSIDAD = "Liverpool John Moores University"
GRADO = "Mechanical Engineering BEng (Hons)"
URL_SPEC = "https://prodcat.ljmu.ac.uk/KIS/32120-3500006811.pdf"
URL_PLAN = "https://www.ljmu.ac.uk/study/courses/undergraduates/2025/32120bgh-mechanical-engineering-beng-hons"
MOD = re.compile(r"(\d{4}MECH)\s+(.+?)\s*\((\d+)\s*credits\)")


def cell_text(pg, bbox) -> str:
    return (pg.crop(bbox).extract_text(x_tolerance=1.2) or "").replace(chr(10), " ")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    robots = "permitido"
    try:
        c.get_text(URL_PLAN)
    except RobotsBlocked:
        robots = "BLOQUEADO"
    entries, seen = [], set()
    texts: dict[tuple[int, str], str] = {}  # (nivel, core/option) -> texto (las tablas continuan en la pagina siguiente sin cabecera)
    order: list[tuple[int, str]] = []
    level = None
    with pdfplumber.open(c.get_file(URL_SPEC)) as pdf:
        for pg in pdf.pages:
            for t in pg.find_tables():
                rows = {}
                for cell in t.cells:
                    rows.setdefault(round(cell[1]), []).append((cell[0], cell))
                grid = [[x[1] for x in sorted(rows[k])] for k in sorted(rows)]
                first = cell_text(pg, grid[0][0])
                lm = re.match(r"Level\s*([456])", first.replace(" ", ""))
                if lm and len(grid) >= 3:
                    level = int(lm.group(1))
                    cells = [("core", grid[2][0])] + ([("option", grid[2][1])] if len(grid[2]) > 1 else [])
                elif level and MOD.search(re.sub(r"\s+", " ", " ".join(cell_text(pg, x) for r in grid for x in r))):
                    cells = [("core", grid[0][0])] + ([("option", grid[0][1])] if len(grid[0]) > 1 else [])  # continuacion de la tabla del nivel
                else:
                    continue
                for kind, cell in cells:
                    key = (level, kind)
                    if key not in texts:
                        order.append(key)
                    texts[key] = texts.get(key, "") + " " + re.sub(r"\s+", " ", cell_text(pg, cell))
    for level, kind in order:
        for m in MOD.finditer(texts[(level, kind)]):
            code, title, cr = m.group(1), m.group(2).strip(), int(m.group(3))
            if code in seen:
                continue
            seen.add(code)
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
                curso_semestre=f"Level {level} ({kind}); duración anual/semestre no indicada en la especificación", curso=level - 3,
                semestre=None, creditos_ects=cr / 2, caracter="obligatoria" if kind == "core" else "optativa", idioma_pagina="en",
                url_guia_docente=f"https://coursecatalogue.ljmu.ac.uk/module/2025/{code}", tipo_fuente="html"))
    total_core = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26 (Programme Specification v03.01)", url_plan_estudios=URL_SPEC,
        ects_totales_plan=180.0, estrategia_fuente="Programme Specification PDF (prodcat.ljmu.ac.uk): tabla de módulos por nivel con core/option",
        generado_por="discover_ec_uk_liverpo02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Grado: BEng (Hons) Mechanical Engineering (código 32120BGH; 360 créditos UK = 180 ECTS; créditos UK/2 = ECTS aprox., convención europea habitual). {len(entries)} módulos: niveles 4/5/6 = cursos 1/2/3; "
               f"core {total_core:g} ECTS equiv.; en el nivel 6 se eligen 40 créditos UK de opcionales. Existe año de prácticas (módulo 5111MECH) y de estudio en el extranjero (5112MECH) no catalogados. "
               f"Fichas de módulo (module specifications) servidas por el Course Catalogue de LJMU (CourseLoop, coursecatalogue.ljmu.ac.uk, robots Allow /): URL /module/2025/{{code}} con JSON en __NEXT_DATA__ (www.ljmu.ac.uk, cm-prod y proformas.ljmu.ac.uk siguen vetados/401, no se usan). "
               "Fase 2: scraper_ec_uk_liverpo02.py. Códigos = códigos oficiales de módulo LJMU (nnnnMECH). Semestre no indicado. Idioma: inglés."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos; core ECTS equiv", total_core, "; robots www.ljmu.ac.uk:", robots)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.curso, e.caracter)


if __name__ == "__main__":
    main()
