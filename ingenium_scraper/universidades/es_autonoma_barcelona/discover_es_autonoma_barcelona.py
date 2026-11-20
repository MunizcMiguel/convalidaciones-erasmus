#!/usr/bin/env python3
"""Fase 1 — Universidad Autónoma de Barcelona, Grado en Ingeniería Mecánica: catálogo PARCIAL (sin asignaturas).
El título lo imparte el centro adscrito EUSS (Sarrià); no se localizó listado de asignaturas ni guías públicas (la búsqueda solo dio informes de calidad).
Comprueba los hosts relevantes con PoliteClient y escribe un catálogo parcial vacío con las notas. Uso: python universidades/es_autonoma_barcelona/discover_es_autonoma_barcelona.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_autonoma_barcelona", "Universidad Autónoma de Barcelona"
HOSTS = ['https://www.uab.cat/', 'https://www.euss.cat/']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=25)
veredictos = []
for h in HOSTS:
    try:
        veredictos.append(f"{h}: " + ("robots permite" if http._allowed(h) else "robots PROHÍBE"))
    except Exception as e:  # noqa: BLE001
        veredictos.append(f"{h}: error {type(e).__name__}")
print(veredictos)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado="Grado en Ingeniería Mecánica", curso_academico="2026-27", url_plan_estudios="https://www.uab.cat/", ects_totales_plan=240.0,
    estrategia_fuente="Sin catálogo: no se localizó una fuente de plan o guías del centro adscrito.", generado_por="discover_es_autonoma_barcelona.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas="PARCIAL sin asignaturas. Centro: Escuela Universitaria Salesiana de Sarrià (adscrita). RUCT (RD 822/2021): básica 60, obligatorios 120, optativos 48, TFG 12. Pendiente localizar guías en euss.cat o en la guía docente de la UAB.")
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=[]).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
