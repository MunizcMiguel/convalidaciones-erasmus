#!/usr/bin/env python3
"""Fase 1 — Universidad Francisco de Vitoria, Grado en Ingeniería Mecánica: catálogo PARCIAL (sin asignaturas).
Solo se localizó un folleto PDF (recursos.ufv.es) con texto desordenado y el BOE; no hay guías docentes públicas halladas.
Comprueba los hosts relevantes con PoliteClient y escribe un catálogo parcial vacío con las notas. Uso: python universidades/es_francisco_vitoria/discover_es_francisco_vitoria.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_francisco_vitoria", "Universidad Francisco de Vitoria"
HOSTS = ['https://www.ufv.es/', 'https://recursos.ufv.es/']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=25)
veredictos = []
for h in HOSTS:
    try:
        veredictos.append(f"{h}: " + ("robots permite" if http._allowed(h) else "robots PROHÍBE"))
    except Exception as e:  # noqa: BLE001
        veredictos.append(f"{h}: error {type(e).__name__}")
print(veredictos)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado="Grado en Ingeniería Mecánica", curso_academico="2026-27", url_plan_estudios="https://recursos.ufv.es/pdf/Grado-Ingenieria-Mecanica-UFV.pdf", ects_totales_plan=240.0,
    estrategia_fuente="Sin catálogo: el folleto tiene texto desordenado y no incluye códigos ni guías.", generado_por="discover_es_francisco_vitoria.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas="PARCIAL sin asignaturas. Sin URL pública de guías docentes localizada; el folleto de recursos.ufv.es no es parseable de forma fiable. RUCT (RD 822/2021): básica 60, obligatorios 156, optativos 6, prácticas 6, TFG 12.")
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=[]).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
