#!/usr/bin/env python3
"""Fase 1 — UDC, Grado en Ingeniería Mecánica (EPEF, Ferrol). Resultado: PARCIAL.

El host de guías (guiadocente.udc.es) resuelve DNS pero no acepta conexiones TCP desde esta red
(ConnectTimeout, 3 intentos en momentos distintos), así que no se pudo leer ni su robots.txt ni el plan.
Este script deja constancia: reintenta una vez con PoliteClient y, si sigue sin responder, escribe un
catálogo parcial vacío. Si el host responde en el futuro hay que escribir el parseo del plan.
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
URL = "https://guiadocente.udc.es/robots.txt"
try:
    PoliteClient(cache_dir=HERE / "raw_cache", timeout=15, max_retries=1).get_text(URL)
    estado_host = "RESPONDE: implementar parseo (no hecho)"
except Exception as e:
    estado_host = f"sin conexión: {str(e)[:80]}"
meta = CatalogMeta(
    universidad="Universidad de A Coruña", slug="es_a_coruna",
    nombre_grado="Grado en Ingeniería Mecánica (Escuela Politécnica de Ferrol)",
    curso_academico="2025-26", url_plan_estudios="https://guiadocente.udc.es/",
    ects_totales_plan=240.0, estrategia_fuente="No determinada: host de guías inaccesible.",
    generado_por="discover_es_a_coruna.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
    estado="parcial",
    notas=f"guiadocente.udc.es: {estado_host}. No es un bloqueo por robots: es un timeout de conexión. "
          "Sin plan no hay filas. RUCT: 60 básica/132 obl/36 opt/12 TFG. Fase 2 omitida.")
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.notas)
