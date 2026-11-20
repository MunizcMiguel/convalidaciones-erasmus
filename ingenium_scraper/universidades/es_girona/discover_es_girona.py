#!/usr/bin/env python3
"""Fase 1 — Universitat de Girona, Grado en Ingeniería Mecánica: catálogo PARCIAL (sin asignaturas).
No se localizó el plan de estudios ni las guías docentes de la UdG con la búsqueda web; no se exploró más allá de robots.txt por límite de llamadas.
Comprueba los hosts relevantes con PoliteClient y escribe un catálogo parcial vacío con las notas. Uso: python universidades/es_girona/discover_es_girona.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_girona", "Universitat de Girona"
HOSTS = ['https://www.udg.edu/']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=25)
veredictos = []
for h in HOSTS:
    try:
        veredictos.append(f"{h}: " + ("robots permite" if http._allowed(h) else "robots PROHÍBE"))
    except Exception as e:  # noqa: BLE001
        veredictos.append(f"{h}: error {type(e).__name__}")
print(veredictos)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado="Grado en Ingeniería Mecánica", curso_academico="2026-27", url_plan_estudios="https://www.udg.edu/", ects_totales_plan=240.0,
    estrategia_fuente="Sin catálogo: fuente no localizada.", generado_por="discover_es_girona.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas="PARCIAL sin asignaturas: fuente de plan/guías no localizada (UdG, EPS). RUCT: básica 60, obligatorios 130, optativos 35, TFG 15. Pendiente explorar las fichas del grado en udg.edu.")
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=[]).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
