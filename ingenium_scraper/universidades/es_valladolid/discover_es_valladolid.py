#!/usr/bin/env python3
"""Fase 1 — Universidad de Valladolid, Grado en Ingeniería Mecánica: catálogo PARCIAL (sin asignaturas).
Las guías docentes (plan 455) están en https://apps.stic.uva.es/guias_docentes/uploads/{año}/455/{id}/1/Documento.pdf, pero el certificado TLS de apps.stic.uva.es (y de isa.eii.uva.es) no valida (hostname mismatch / CERTIFICATE_VERIFY_FAILED).
Comprueba los hosts relevantes con PoliteClient y escribe un catálogo parcial vacío con las notas. Uso: python universidades/es_valladolid/discover_es_valladolid.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_valladolid", "Universidad de Valladolid"
HOSTS = ['https://www.uva.es/', 'https://apps.stic.uva.es/', 'https://isa.eii.uva.es/']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=25)
veredictos = []
for h in HOSTS:
    try:
        veredictos.append(f"{h}: " + ("robots permite" if http._allowed(h) else "robots PROHÍBE"))
    except Exception as e:  # noqa: BLE001
        veredictos.append(f"{h}: error {type(e).__name__}")
print(veredictos)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado="Grado en Ingeniería Mecánica", curso_academico="2026-27", url_plan_estudios="https://www.eii.uva.es/alumnos/futuros/tripticos/455.pdf", ects_totales_plan=240.0,
    estrategia_fuente="Sin catálogo: el listado de asignaturas y las guías están en hosts con TLS inválido; no se desactiva la verificación.", generado_por="discover_es_valladolid.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas="PARCIAL sin asignaturas. apps.stic.uva.es (guías PDF) falla con CERTIFICATE_VERIFY_FAILED (nombre de host no coincide) y no se desactiva la verificación TLS; los PDF de plan en www.uva.es hallados por búsqueda devuelven 404. www.uva.es permite el acceso. RUCT: básica 60, obligatorios 135, optativos 27, prácticas 6, TFG 12. Reintentar si el host corrige su certificado.")
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=[]).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
