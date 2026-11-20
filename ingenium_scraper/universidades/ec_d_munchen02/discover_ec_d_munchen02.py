"""Fase 1 (parcial, regla de parada) - Technische Universität München - Maschinenwesen / Mechanical Engineering (B.Sc.).

Sondea con PoliteClient los hosts implicados y deja un catalogo parcial vacio con el veredicto.
Uso: python universidades/ec_d_munchen02/discover_ec_d_munchen02.py
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
SLUG = "ec_d_munchen02"
PROBES = {'www.tum.de ficha del grado': 'https://www.tum.de/en/studies/degree-programs/detail/mechanical-engineering-bachelor-of-science-bsc', 'campus.tum.de (TUMonline) robots.txt': 'https://campus.tum.de/robots.txt'}
NOTAS = "Titulación: Maschinenwesen B.Sc. (Mechanical Engineering), 6 semestres, 180 CP, School of Engineering and Design (Garching). La web de TUM permite el rastreo y enlaza la Studiengangsdokumentation Teil A (PDF, 34 págs.: objetivos y estructura del programa, sin fichas de módulo), la FPSO y la EFV. Las descripciones de módulo están en TUMonline (campus.tum.de/tumonline), cuyo robots.txt dice 'User-agent: * Disallow: /' (y es una SPA con login para varias funciones): regla de parada, catálogo vacío, sin Fase 2. No se localizó otro Modulhandbuch público fuera de TUMonline."


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    verdict = {}
    for name, url in PROBES.items():
        try:
            t = c.get_text(url)
            verdict[name] = "responde (%d bytes)" % len(t)
            if "Loading Session Information" in t or "Web Login Service" in t:
                verdict[name] += " pero es un arranque de sesion SSO con JavaScript (sin contenido)"
        except RobotsBlocked:
            verdict[name] = "robots.txt no permite"
        except Exception as e:  # noqa: BLE001
            verdict[name] = "error: " + type(e).__name__
    print(verdict)
    meta = CatalogMeta(
        universidad="Technische Universität München", slug=SLUG, nombre_grado="Maschinenwesen / Mechanical Engineering (B.Sc.)", curso_academico="2025/26",
        url_plan_estudios="https://www.tum.de/en/studies/degree-programs/detail/mechanical-engineering-bachelor-of-science-bsc", ects_totales_plan=180.0,
        estrategia_fuente="Sin extraccion (regla de parada): los módulos viven en TUMonline (campus.tum.de), cuyo robots.txt prohíbe todo (Disallow: / para *)",
        generado_por="discover_ec_d_munchen02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=NOTAS + " Sondeo del %s: " % time.strftime("%Y-%m-%d") + "; ".join(f"{k}: {v}" for k, v in verdict.items()))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
