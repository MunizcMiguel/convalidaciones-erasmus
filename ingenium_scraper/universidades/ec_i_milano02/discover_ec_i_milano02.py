"""Fase 1 (parcial, regla de parada) - Politecnico di Milano - Laurea in Ingegneria Meccanica (L-9, Bovisa/Piacenza).

Comprueba con PoliteClient los hosts implicados y deja un catalogo parcial vacio con el veredicto.
Uso: python universidades/ec_i_milano02/discover_ec_i_milano02.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_milano02"
PROBES = {
    "www.polimi.it": "https://www.polimi.it/robots.txt",
    "www.mecheng.polimi.it": "https://www.mecheng.polimi.it/robots.txt",
    "onlineservices.polimi.it": "https://onlineservices.polimi.it/robots.txt",
    "www4.ceda.polimi.it": "https://www4.ceda.polimi.it/robots.txt",
}


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    verdict = {}
    for host, url in PROBES.items():
        try:
            c.get_text(url)
            verdict[host] = "permite"
        except RobotsBlocked:
            verdict[host] = "BLOQUEADO (Disallow en robots.txt)"
        except Exception as e:  # noqa: BLE001
            verdict[host] = f"error: {type(e).__name__}"
    print(verdict)
    meta = CatalogMeta(
        universidad="Politecnico di Milano", slug=SLUG, nombre_grado="Ingegneria Meccanica (Laurea, L-9)",
        curso_academico="2025/26", url_plan_estudios="https://www.mecheng.polimi.it/laurea-triennale/",
        ects_totales_plan=180.0,
        estrategia_fuente="Sin extracción: las fichas de insegnamento están en hosts bloqueados/no resolubles; el plan se sirve por una app con sesión y AJAX",
        generado_por="discover_ec_i_milano02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación: Laurea in Ingegneria Meccanica (L-9), 180 CFU, sedes Bovisa y Piacenza (CdS k_corso_la=534/535). Veredictos robots.txt: "
               + "; ".join(f"{h}: {v}" for h, v in verdict.items())
               + ". El plan de estudios de la web de la escuela es una imagen (PNG); el Manifesto (onlineservices.polimi.it, robots con Crawl-delay 5) "
                 "carga la tabla de insegnamenti por AJAX con sesión (no está en el HTML), y las schede insegnamento viven en www4.ceda.polimi.it "
                 "(robots.txt Disallow total → RobotsBlocked) / www11.ceda.polimi.it (sin resolución DNS desde esta red). Regla de parada: catálogo vacío, sin Fase 2. "
                 "Las guías se publican en italiano e inglés. No verificado: asignaturas concretas del plan."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
