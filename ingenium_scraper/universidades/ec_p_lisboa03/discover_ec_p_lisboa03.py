#!/usr/bin/env python3
"""Fase 1 — Universidade NOVA de Lisboa — FCT NOVA: catálogo PARCIAL vacío (regla de parada). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS (robots/DNS/HTTP) y escribe el catálogo con el motivo.
Uso: python universidades/ec_p_lisboa03/discover_ec_p_lisboa03.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://www.fct.unl.pt/ensino/curso/licenciatura-em-engenharia-mecanica', 'https://guia.unl.pt/robots.txt', 'https://guia.unl.pt/pt/2026/fct/program/1273']
http = PoliteClient(cache_dir=HERE / "raw_cache")
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:120]}")
meta = CatalogMeta(universidad='Universidade NOVA de Lisboa — FCT NOVA', slug='ec_p_lisboa03', nombre_grado='Licenciatura em Engenharia Mecânica (FCT NOVA)', curso_academico="2026-27",
    url_plan_estudios='https://www.fct.unl.pt/ensino/curso/licenciatura-em-engenharia-mecanica', ects_totales_plan=None,
    estrategia_fuente="Sin fuente de guías accesible (regla de parada).", generado_por="discover_ec_p_lisboa03.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas='El grado equivalente es la Licenciatura em Engenharia Mecânica de la FCT NOVA (la ficha en www.fct.unl.pt, robots permite, enlaza al Guia Académico https://guia.unl.pt/pt/2026/fct/program/1273). Regla de parada por TLS: guia.unl.pt y www.unl.pt fallan con SSL CERTIFICATE_VERIFY_FAILED (unable to get local issuer certificate); no se desactiva la verificación. No se leyó el plan ni las fichas. Catálogo parcial vacío; sin Fase 2. Reintentar si se corrige la cadena de certificados.' + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
