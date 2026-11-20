#!/usr/bin/env python3
"""Fase 1 — Universidad Europea de Madrid, Grado en Ingeniería Mecánica: catálogo PARCIAL (sin asignaturas).
El título RUCT está «a extinguir»; las guías son PDF en universidadeuropea.com/myfiles/pr/{codigo}.pdf, pero no se localizó el listado de asignaturas del Grado en Ingeniería Mecánica (la búsqueda solo devolvió guías de otros grados).
Comprueba los hosts relevantes con PoliteClient y escribe un catálogo parcial vacío con las notas. Uso: python universidades/es_europea_madrid/discover_es_europea_madrid.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_europea_madrid", "Universidad Europea de Madrid"
HOSTS = ['https://madrid.universidadeuropea.es/', 'https://universidadeuropea.com/']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=25)
veredictos = []
for h in HOSTS:
    try:
        veredictos.append(f"{h}: " + ("robots permite" if http._allowed(h) else "robots PROHÍBE"))
    except Exception as e:  # noqa: BLE001
        veredictos.append(f"{h}: error {type(e).__name__}")
print(veredictos)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado="Grado en Ingeniería Mecánica", curso_academico="2026-27", url_plan_estudios="https://madrid.universidadeuropea.es/", ects_totales_plan=240.0,
    estrategia_fuente="Sin catálogo: no se localizó una fuente estructurada del plan.", generado_por="discover_es_europea_madrid.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas="PARCIAL sin asignaturas. Título RUCT 2501350 en extinción (TITULACIÓN A EXTINGUIR); guías PDF en universidadeuropea.com/myfiles/pr/{código}.pdf sin índice localizado para este grado. RUCT: básica 60, obligatorios 138, optativos 24, prácticas 6, TFG 12.")
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=[]).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
