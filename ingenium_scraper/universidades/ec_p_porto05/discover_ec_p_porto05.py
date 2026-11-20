#!/usr/bin/env python3
"""Fase 1 - Instituto Politecnico do Porto (P PORTO05): catalogo PARCIAL vacio (regla de parada por TLS). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS y escribe el catalogo con el motivo.
Uso: python universidades/ec_p_porto05/discover_ec_p_porto05.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://www.ipp.pt/international', 'https://www.isep.ipp.pt/', 'https://www.isep.ipp.pt/Course/Course/26']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=15)
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:120]}")
meta = CatalogMeta(universidad='Instituto Politécnico do Porto (ISEP)', slug='ec_p_porto05', nombre_grado='Licenciatura em Engenharia e Gestão Industrial (ISEP) - no verificada', curso_academico="2025-26",
    url_plan_estudios='https://www.isep.ipp.pt/', ects_totales_plan=None,
    estrategia_fuente="Sin fuente accesible (regla de parada por TLS).", generado_por="discover_ec_p_porto05.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas='Excel: Grado en Ingeniería de Organización Industrial (2 plazas) y Máster Teleco para este destino. IPP es una federación de escuelas; la más afín a Organización Industrial es el ISEP (Engenharia e Gestão Industrial, a confirmar: no se pudo leer ninguna página). Regla de parada por TLS: www.ipp.pt y www.isep.ipp.pt fallan con SSL CERTIFICATE_VERIFY_FAILED (unable to get local issuer certificate); no se desactiva la verificación. No se leyó plan ni fichas. Catálogo parcial vacío; sin Fase 2. Reintentar si se corrige la cadena de certificados (mismo problema que Lisboa Nova y Arcozelo).' + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
