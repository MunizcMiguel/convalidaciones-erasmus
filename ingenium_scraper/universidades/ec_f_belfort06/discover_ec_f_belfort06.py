#!/usr/bin/env python3
"""Fase 1 — Université de technologie de Belfort-Montbéliard (UTBM): catálogo PARCIAL vacío (regla de parada). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS (robots/DNS/HTTP) y escribe el catálogo con el motivo.
Uso: python universidades/ec_f_belfort06/discover_ec_f_belfort06.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://www.utbm.fr/formations/ingenieur/specialite-mecanique/', 'https://guideuv.utbm.fr/']
http = PoliteClient(cache_dir=HERE / "raw_cache")
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:120]}")
meta = CatalogMeta(universidad='Université de technologie de Belfort-Montbéliard (UTBM)', slug='ec_f_belfort06', nombre_grado="Diplôme d'ingénieur UTBM, spécialité Mécanique (cycle ingénieur)", curso_academico="2026-27",
    url_plan_estudios='https://www.utbm.fr/formations/ingenieur/specialite-mecanique/', ects_totales_plan=None,
    estrategia_fuente="Sin fuente de guías accesible (regla de parada).", generado_por="discover_ec_f_belfort06.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas='UTBM no ofrece Licence/Bachelor en génie mécanique: solo cycle ingénieur (spécialité Mécanique, y Mécanique et ergonomie / Mécanique et transports en apprentissage). La ficha de cada UV está en guideuv.utbm.fr (enlazado desde la página de la especialidad), cuyo host no resuelve por DNS (getaddrinfo failed) desde esta red; no hay otra ruta pública en www.utbm.fr (404). www.utbm.fr robots.txt permite. Catálogo parcial vacío; sin Fase 2. Reintentar si guideuv vuelve a resolver.' + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
