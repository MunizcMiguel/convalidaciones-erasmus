#!/usr/bin/env python3
"""Fase 1 · Descubrimiento (PARCIAL, regla de parada) — Università della Calabria (UniCal), Laurea in Ingegneria Meccanica (L-9) — no confirmada.

Los syllabus de UniCal se publican en unical.coursecatalogue.cineca.it (robots.txt lo veta) y la lista de grados la sirve la API storage.portale.unical.it (HTTP 403 a PoliteClient). www.unical.it permite, pero su lista de grados se carga por JS desde esa API.

Comprueba de forma determinista, con PoliteClient, qué hosts bloquean el acceso automatizado y
escribe un catálogo `parcial` sin filas (no se inventa ninguna asignatura).

Uso (desde la raíz del proyecto):
    python universidades/ec_i_cosenza01/discover_ec_i_cosenza01.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import FetchError, PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
PROBES = ['https://unical.coursecatalogue.cineca.it/api/v1/corsi?anno=2025&minimal=true', 'https://storage.portale.unical.it/api/ricerca/cds/?page_size=1000&coursetype=L,LM5,LM6&lang=en', 'https://www.unical.it/robots.txt']


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    verdicts = {}
    for url in PROBES:
        try:
            n = len(http.get_bytes(url))
            verdicts[url] = f"OK ({n} bytes)"
        except RobotsBlocked:
            verdicts[url] = "BLOQUEADO por robots.txt"
        except FetchError as ex:
            verdicts[url] = f"BLOQUEADO/ERROR: {str(ex)[:90]}"
        print(url, "->", verdicts[url])
    meta = CatalogMeta(
        universidad="Università della Calabria (UniCal)", slug="ec_i_cosenza01", nombre_grado="Laurea in Ingegneria Meccanica (L-9) — no confirmada", nivel="bachelor",
        curso_academico="n/d", url_plan_estudios="https://dimeg.unical.it/didattica/offerta-formativa/lauree-triennali-e-a-ciclo-unico/", ects_totales_plan=180.0,
        estrategia_fuente="Catálogo Cineca bloqueado (robots) y API del portal bloqueada (403): sin fuente accesible.",
        generado_por="discover_ec_i_cosenza01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial",
        notas="Parcial por regla de parada: el host que sirve los syllabus (unical.coursecatalogue.cineca.it) prohíbe el acceso automatizado por robots.txt y la API del portal responde 403; no se rodea. Titulación esperada: Ingegneria Meccanica (L-9, DIMEG), no verificada. Sin Fase 2. Veredictos de las sondas: " + json.dumps(verdicts, ensure_ascii=False),
    )
    cat = Catalog(meta=meta, asignaturas=[])
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("catálogo parcial ->", out)


if __name__ == "__main__":
    main()
