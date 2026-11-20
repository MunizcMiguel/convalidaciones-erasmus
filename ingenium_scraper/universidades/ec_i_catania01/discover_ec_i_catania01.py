#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Università degli Studi di Catania: catálogo PARCIAL (sin red; documenta el estado de la investigación).

Uso: python universidades/ec_i_catania01/discover_ec_i_catania01.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
NOTAS = "PARCIAL. Única fila Erasmus de Catania: Grado en Ing. de Organización Industrial (ISCED 0720, 2 plazas). Titulación elegida: Laurea in Ingegneria Industriale (L-9 R, DIEEI, curricula Elettrica y Meccanica; existe también Ingegneria Gestionale L-9 R, más afín a Org. Industrial pero se prioriza Industrial/Mecánica; confirmar con el equipo). El Regolamento didattico 2026/27 (RD L-9 Ind) es PDF de gestión, sin fichas de asignatura; no se localizó dentro del presupuesto el sitio de syllabus por insegnamento. El host unict.coursecatalogue.cineca.it no existe como catálogo público (PoliteClient lo trata como robots no permite); Catania no usa la plantilla Cineca de Padova/Pisa/Molise. 0 asignaturas, 0 Markdown. Siguiente paso: localizar el portal 'Syllabus' de Unict (dieei.unict.it / studiare.unict.it) y comprobar robots."


def main() -> None:
    meta = CatalogMeta(
        universidad='Università degli Studi di Catania', slug='ec_i_catania01', nombre_grado='Laurea in Ingegneria Industriale (L-9 R, DIEEI; curricula Elettrica y Meccanica) — elegida, sin fichas obtenidas', curso_academico="2025/26",
        url_plan_estudios='https://www.unict.it/it/didattica/lauree-e-lauree-magistrali/offerta-formativa-2026-2027', ects_totales_plan=None,
        estrategia_fuente='No resuelta: el plan está en PDF de regolamento (dieei.unict.it) y los syllabus se publican en una plataforma de ateneo no localizada.',
        generado_por="discover_ec_i_catania01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial", notas=NOTAS)
    cat = Catalog(meta=meta, asignaturas=[])
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("catálogo parcial (0 asignaturas):", 'ec_i_catania01')


if __name__ == "__main__":
    main()
