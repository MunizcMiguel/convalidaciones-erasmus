"""Fase 1 - Uczelnia Panstwowa im. Jana Grodka w Sanoku (antes PWSZ Sanok), Instytut Techniczny: Mechanika i budowa maszyn (Mechanical Engineering).
Sitio oficial: up-sanok.edu.pl (confirmado por busqueda web; el hint de la ficha Erasmus era correcto, pero el servidor no responde).
Todos los hosts probados cierran la conexion sin respuesta ("Server disconnected without sending a response") a PoliteClient
-> regla de parada: catalogo parcial vacio, sin Fase 2 (no se cambia el User-Agent ni se rodea el filtro).
Uso: python universidades/ec_pl_sanok01/discover_ec_pl_sanok01.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_sanok01"
HOSTS = ["https://up-sanok.edu.pl/robots.txt", "https://up-sanok.edu.pl/en/erasmus-plus",
         "https://instytut-techniczny.up-sanok.edu.pl/robots.txt", "https://www.up-sanok.edu.pl/", "https://bip.up-sanok.edu.pl/"]


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=2, timeout=15)
    result = []
    for u in HOSTS:
        try:
            c.get_text(u)
            result.append(f"{u}: OK")
        except FetchError as e:
            result.append(f"{u}: {type(e).__name__} {str(e).split(': ', 1)[-1][:80]}")
    meta = CatalogMeta(
        universidad="Uczelnia Państwowa im. Jana Grodka w Sanoku (ex PWSZ Sanok) - Instytut Techniczny",
        slug=SLUG, nombre_grado="Mechanika i budowa maszyn (Mechanical Engineering), 1.er ciclo", curso_academico="2025/2026",
        url_plan_estudios="https://up-sanok.edu.pl/", estrategia_fuente="No accesible: el servidor cierra la conexión a PoliteClient",
        generado_por="discover_ec_pl_sanok01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación equivalente: Mechanika i budowa maszyn (Instytut Techniczny; programas en instytut-techniczny.up-sanok.edu.pl, p. ej. program_studiow_mibm_*.pdf según búsqueda web). "
               "PARCIAL VACÍO por la regla de parada: todos los hosts de up-sanok.edu.pl (incluidos robots.txt, portada, /en, bip e instituto) responden 'Server disconnected without sending a response' a PoliteClient "
               "(filtro de bots/WAF); no se cambia el User-Agent ni se rodea. Resultados de la prueba: " + "; ".join(result) + ". Reintentar desde otra red o con contacto institucional."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("parcial vacio;", *result, sep="\n")


if __name__ == "__main__":
    main()
