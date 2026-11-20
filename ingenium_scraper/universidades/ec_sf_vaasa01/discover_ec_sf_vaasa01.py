"""Fase 1 - University of Vaasa (SF VAASA01) - Industrial Engineering and Management (BSc, tuotantotalous): catalogo PARCIAL, sin asignaturas.
Las guias de curso viven en la SPA Angular de Peppi (opas.peppi.uwasa.fi: index.html sin contenido, datos por API backend no documentada
/api/...; los endpoints probados /api/educations... responden 404) y los planes en PDF antiguos sin fichas por asignatura. No se encontro una fuente
estatica o JSON publica estable dentro del presupuesto de exploracion; no se usa navegador automatizado ni se adivinan endpoints. Se escribe el catalogo vacio
con el motivo (regla de parada/presupuesto).
Uso (desde la raiz): python universidades/ec_sf_vaasa01/discover_ec_sf_vaasa01.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_sf_vaasa01"
URL_GUIDE = "https://opas.peppi.uwasa.fi/en"
URL_PROGRAMMES = "https://www.uwasa.fi/en/education/bachelors-programmes"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    html = http.get_text(URL_GUIDE)  # verifica que la guia sigue siendo una SPA sin contenido estatico
    spa = "<app-root" in html and "Opinto-opas" in html
    http.get_text(URL_PROGRAMMES)
    meta = CatalogMeta(
        universidad="University of Vaasa (Vaasan yliopisto)", slug=SLUG,
        nombre_grado="Industrial Engineering and Management (BSc, Industrial Management), School of Technology and Innovations",
        nivel="bachelor", curso_academico="2025-2026", url_plan_estudios=URL_PROGRAMMES, ects_totales_plan=180.0,
        estrategia_fuente="Sin fuente estática/JSON localizada: guía de estudios en SPA Angular de Peppi",
        generado_por="discover_ec_sf_vaasa01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: Industrial Engineering and Management / Industrial Management (grado en ingeniería de organización industrial del Excel, "
               "ISCED 0710; el máster de Vaasa en Industrial Management es de 2.º ciclo). Las guías de curso están en opas.peppi.uwasa.fi, una SPA Angular "
               f"(index.html vacío{', confirmado' if spa else ''}); su backend /api/ usa rutas no documentadas (educations, education/{{id}}, course…; "
               "las rutas probadas devolvieron 404) y www.uwasa.fi solo publica PDF de planes antiguos (2019-2020) sin fichas por asignatura. "
               "Presupuesto de exploración agotado sin una fuente fiable: catálogo vacío, sin Fase 2. Pendiente: reconstruir la API de Peppi con las rutas "
               "del bundle main.js (o usar el módulo de Peppi 'study-guide') si se quiere cubrir Vaasa."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("0 asignaturas (parcial); SPA confirmada:", spa)


if __name__ == "__main__":
    main()
