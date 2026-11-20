#!/usr/bin/env python3
"""Fase 1 - Ondokuz Mayıs Üniversitesi (TR SAMSUN01): catalogo PARCIAL vacio (regla de parada). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS y escribe el catalogo con el motivo.
Uso: python universidades/ec_tr_samsun01/discover_ec_tr_samsun01.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://ebs.omu.edu.tr/', 'https://erasmus.omu.edu.tr/en/course-catalogue/course-catalogue', 'https://erasmus.omu.edu.tr/uploads/English_Courses_for_2025-.pdf']
http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=15)
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:110]}")
meta = CatalogMeta(universidad='Ondokuz Mayıs Üniversitesi', slug='ec_tr_samsun01', nombre_grado='Elektrik-Elektronik Mühendisliği (Electrical-Electronics Engineering), lisans - no verificada', curso_academico="2025-26",
    url_plan_estudios='https://erasmus.omu.edu.tr/en/course-catalogue/course-catalogue', ects_totales_plan=None,
    estrategia_fuente="Sin fuente de guias accesible (regla de parada).", generado_por="discover_ec_tr_samsun01.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas='Excel: Grado en Ingeniería Electrónica Industrial y Automática (5 plazas, inglés B1, ISCED 0710). Titulación candidata: Elektrik-Elektronik Mühendisliği (no verificada). Regla de parada: el catálogo de OMU (ebs.omu.edu.tr) devuelve RobotsBlocked (robots.txt no permite el acceso automatizado) y obs.omu.edu.tr no resuelve. La web Erasmus (erasmus.omu.edu.tr, accesible) solo ofrece un PDF «English-taught courses & Erasmus common courses» (20 págs.) con código/título/ECTS en maquetación de dos columnas, sin planes por titulación ni fichas: no se cataloga. Sin Fase 2.' + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
