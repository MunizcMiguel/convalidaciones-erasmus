#!/usr/bin/env python3
"""Fase 1 — Instituto Politécnico de Coimbra (ISEC): catálogo PARCIAL vacío (regla de parada). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS (robots/DNS/HTTP) y escribe el catálogo con el motivo.
Uso: python universidades/ec_p_coimbra02/discover_ec_p_coimbra02.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://www.isec.pt/robots.txt', 'https://www.isec.pt/', 'https://www.ipc.pt/robots.txt']
http = PoliteClient(cache_dir=HERE / "raw_cache")
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:120]}")
meta = CatalogMeta(universidad='Instituto Politécnico de Coimbra (ISEC)', slug='ec_p_coimbra02', nombre_grado='Licenciatura em Engenharia Mecânica (ISEC, Instituto Superior de Engenharia de Coimbra)', curso_academico="2026-27",
    url_plan_estudios='https://www.isec.pt/', ects_totales_plan=None,
    estrategia_fuente="Sin fuente de guías accesible (regla de parada).", generado_por="discover_ec_p_coimbra02.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas='El grado equivalente es la Licenciatura em Engenharia Mecânica del ISEC (unidad del IPC). Regla de parada: el host isec.pt responde HTTP 400 a PoliteClient (robots.txt incluido; no se rodea con otro cliente/UA) y la web institucional www.ipc.pt (robots permite) no aloja planes ni fichas (FUC). Búsquedas web no devolvieron el plan ni las FUC de ISEC. Catálogo parcial vacío; sin Fase 2.' + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
