#!/usr/bin/env python3
"""Fase 1 - Fırat Üniversitesi (Firat University) (TR ELAZIG01): catalogo PARCIAL vacio (regla de parada). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS y escribe el catalogo con el motivo.
Uso: python universidades/ec_tr_elazig01/discover_ec_tr_elazig01.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://www.firat.edu.tr/robots.txt', 'https://obs.firat.edu.tr/', 'https://kimya.firat.edu.tr/']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=15)
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:110]}")
meta = CatalogMeta(universidad='Fırat Üniversitesi (Firat University)', slug='ec_tr_elazig01', nombre_grado='Kimya Mühendisliği (Chemical Engineering), lisans - no verificada', curso_academico="2025-26",
    url_plan_estudios='https://www.firat.edu.tr', ects_totales_plan=None,
    estrategia_fuente="Sin fuente de guias accesible (regla de parada).", generado_por="discover_ec_tr_elazig01.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas='Excel: Grado en Ingeniería Química Industrial (2 plazas, inglés B1, ISCED 0711); web_informacion es un PDF factsheet de la oficina Erasmus. Titulación candidata (no verificada): Kimya Mühendisliği (Mühendislik Fakültesi). Regla de parada: www.firat.edu.tr, obs.firat.edu.tr y kimya.firat.edu.tr agotan el tiempo de conexión (timed out) y bologna/ebs.firat.edu.tr no resuelven por DNS; el catálogo de asignaturas no es alcanzable. No se leyó plan ni fichas; sin Fase 2. Reintentar más tarde.' + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
