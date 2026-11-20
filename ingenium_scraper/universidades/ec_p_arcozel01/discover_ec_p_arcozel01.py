#!/usr/bin/env python3
"""Fase 1 — Instituto Politécnico do Cávado e do Ave (IPCA), Barcelos: catálogo PARCIAL vacío (regla de parada). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS (robots/DNS/HTTP) y escribe el catálogo con el motivo.
Uso: python universidades/ec_p_arcozel01/discover_ec_p_arcozel01.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://www.ipca.pt/robots.txt', 'https://ipca.pt/robots.txt', 'https://www.ipca.pt/']
http = PoliteClient(cache_dir=HERE / "raw_cache")
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:120]}")
meta = CatalogMeta(universidad='Instituto Politécnico do Cávado e do Ave (IPCA), Barcelos', slug='ec_p_arcozel01', nombre_grado='Licenciatura em Engenharia Mecânica (IPCA/EST, a confirmar)', curso_academico="2026-27",
    url_plan_estudios='https://www.ipca.pt/', ects_totales_plan=None,
    estrategia_fuente="Sin fuente de guías accesible (regla de parada).", generado_por="discover_ec_p_arcozel01.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas='Regla de parada por TLS: todos los accesos a ipca.pt y www.ipca.pt (https y http) fallan con SSL CERTIFICATE_VERIFY_FAILED (unable to get local issuer certificate); no se desactiva la verificación ni se rodea. No se pudo leer robots.txt ni la oferta formativa; la titulación equivalente prevista es la Licenciatura (1.er ciclo) en Engenharia Mecânica de la EST, no verificada. Catálogo parcial vacío; sin Fase 2. Reintentar si IPCA corrige la cadena de certificados.' + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
