#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Democritus University of Thrace (Δημοκρίτειο Πανεπιστήμιο Θράκης): catálogo PARCIAL (sin red; documenta el estado de la investigación).

Uso: python universidades/ec_g_komotin01/discover_ec_g_komotin01.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
NOTAS = "PARCIAL. Filas Erasmus de Komotini (DUTH): Grado Ing. Electrónica Industrial y Automática (2 plazas), Org. Industrial (2) y Máster Conversión de Energía Eléctrica. Las ingenierías de DUTH están en Xanthi (Komotini es sede administrativa): Electrical and Computer Engineering (ee.duth.gr) es la más afín a EIA/Eléctrica, y Production and Management Engineering (pme.duth.gr) a Org. Industrial; se elige ECE. Ambos departamentos publican el 'Οδηγός Σπουδών 2025-2026' en PDF en griego (https://www.ee.duth.gr/wp-content/uploads/2025/10/Οδηγός-Σπουδών-2025-2026-GR.pdf) y lista de 'Μαθήματα'; no se verificó robots ni se parseó el plan por falta de presupuesto y por ser solo griego. 0 asignaturas, 0 Markdown. Siguiente paso: parsear el Οδηγός Σπουδών GR de ECE (PDF compartido) como en Bochum/Oradea."


def main() -> None:
    meta = CatalogMeta(
        universidad='Democritus University of Thrace (Δημοκρίτειο Πανεπιστήμιο Θράκης)', slug='ec_g_komotin01', nombre_grado='Electrical and Computer Engineering (Xanthi) — elegida, sin fichas obtenidas', curso_academico="2025/26",
        url_plan_estudios='https://www.ee.duth.gr/', ects_totales_plan=None,
        estrategia_fuente='No resuelta: guías de estudios en PDF en griego (ee.duth.gr, pme.duth.gr); sin versión inglesa por asignatura localizada.',
        generado_por="discover_ec_g_komotin01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial", notas=NOTAS)
    cat = Catalog(meta=meta, asignaturas=[])
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("catálogo parcial (0 asignaturas):", 'ec_g_komotin01')


if __name__ == "__main__":
    main()
