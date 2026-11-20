#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Università degli Studi di Palermo: catálogo PARCIAL (sin red; documenta el estado de la investigación).

Uso: python universidades/ec_i_palermo01/discover_ec_i_palermo01.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
NOTAS = "PARCIAL. Filas Erasmus de Palermo: Ing. Química Industrial (2 plazas), Org. Industrial y Tecnologías Industriales -> titulación elegida: Laurea in Ingegneria Meccanica (L-9, CdS 2055, Scuola Politecnica), la más afín a Tecnologías Industriales (la rama Mecánica/Industrial tiene prioridad). No se obtuvo plan ni fichas: (1) www.unipa.it/robots.txt permite todo, la portada del CdS cargó una vez (enlaces ?pagina=pianodistudi y ?pagina=insegnamenti) pero esas subpáginas devuelven HTTP 503 de forma persistente a PoliteClient; (2) offertaformativa.unipa.it (donde residen las schede insegnamento) es una app JSF con estado de sesión y su robots.txt contiene un grupo 'User-agent: * / Allow: /' y otro final 'User-agent: * / Disallow: /' (ambiguo), por lo que se aplica la regla de parada y no se rastrea. Siguiente paso posible: obtener el plan del CdS 2055 desde un PDF oficial (manifesto/SUA) o pedir permiso/endpoint a Unipa. 0 asignaturas, 0 Markdown."


def main() -> None:
    meta = CatalogMeta(
        universidad='Università degli Studi di Palermo', slug='ec_i_palermo01', nombre_grado='Laurea in Ingegneria Meccanica (L-9, corso 2055) — elegida, sin fichas obtenidas', curso_academico="2025/26",
        url_plan_estudios='https://www.unipa.it/dipartimenti/ingegneria/cds/ingegneriameccanica2055/', ects_totales_plan=None,
        estrategia_fuente='No resuelta: páginas del CdS en www.unipa.it (503 persistente a las 2.ª-3.ª peticiones) y fichas en offertaformativa.unipa.it (aplicación JSF/Seam con estado de sesión).',
        generado_por="discover_ec_i_palermo01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial", notas=NOTAS)
    cat = Catalog(meta=meta, asignaturas=[])
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("catálogo parcial (0 asignaturas):", 'ec_i_palermo01')


if __name__ == "__main__":
    main()
