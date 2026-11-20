#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — University of Chemical Technology and Metallurgy, Sofia (UCTM): catálogo PARCIAL (sin red; documenta el estado de la investigación).

Uso: python universidades/ec_bg_sofia20/discover_ec_bg_sofia20.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
NOTAS = "PARCIAL. Filas Erasmus de UCTM (Sofía): Grado Ing. Química Industrial (2 plazas) y Máster Ing. Industrial. UCTM es universidad química/metalúrgica, sin grado de Mecánica/Industrial: la titulación afín sería Chemical Engineering (bachelor, 4 años). En uctm.edu/en hay páginas 'Bachelor' y 'Curricula' (https://uctm.edu/en/component/sppagebuilder/?view=page&id=504) que no se exploraron en profundidad; no se localizaron fichas de asignatura públicas en inglés ni se verificó robots.txt. 0 asignaturas, 0 Markdown. Siguiente paso: abrir la página de Curricula, identificar el plan de Chemical Engineering y comprobar si los syllabus (búlgaro) son públicos."


def main() -> None:
    meta = CatalogMeta(
        universidad='University of Chemical Technology and Metallurgy, Sofia (UCTM)', slug='ec_bg_sofia20', nombre_grado='Bachelor Chemical Engineering — sin identificar plan, sin fichas obtenidas', curso_academico="2025/26",
        url_plan_estudios='https://uctm.edu/en/about/curriculum', ects_totales_plan=None,
        estrategia_fuente="No resuelta: uctm.edu publica 'Curricula' (sppagebuilder id=504) y páginas 'Bachelor' sin fichas de asignatura accesibles; sitio en búlgaro/inglés parcial.",
        generado_por="discover_ec_bg_sofia20.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial", notas=NOTAS)
    cat = Catalog(meta=meta, asignaturas=[])
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("catálogo parcial (0 asignaturas):", 'ec_bg_sofia20')


if __name__ == "__main__":
    main()
