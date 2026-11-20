#!/usr/bin/env python3
"""Fase 1 — Université de Lorraine (Nancy/Metz): catálogo PARCIAL vacío (regla de parada). Ver notas_descubrimiento.md.
Comprueba por PoliteClient las URLs de CHECKS (robots/DNS/HTTP) y escribe el catálogo con el motivo.
Uso: python universidades/ec_f_nancy43/discover_ec_f_nancy43.py"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogMeta

HERE = Path(__file__).parent
CHECKS = ['https://formations.univ-lorraine.fr/fr/licence/1630-licence-sciences-pour-l-ingenieur.html', 'https://formulconnect.univ-lorraine.fr/files/00ef08bd-eac0-4a4d-8107-58a9ff9d9f24-licence_sciences_pour_l_ingénieur.pdf']
http = PoliteClient(cache_dir=HERE / "raw_cache")
res = []
for u in CHECKS:
    try:
        http.get_bytes(u); res.append(f"{u}: OK")
    except Exception as e:
        res.append(f"{u}: {type(e).__name__}: {str(e)[:120]}")
meta = CatalogMeta(universidad='Université de Lorraine (Nancy/Metz)', slug='ec_f_nancy43', nombre_grado="Licence Sciences pour l'ingénieur, orientation MGC (Mécanique Génie Civil), parcours Ingénierie Mécanique et Matériaux (Metz)", curso_academico="2026-27",
    url_plan_estudios='https://formations.univ-lorraine.fr/fr/licence/1630-licence-sciences-pour-l-ingenieur.html', ects_totales_plan=None,
    estrategia_fuente="Sin fuente de guías accesible (regla de parada).", generado_por="discover_ec_f_nancy43.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas="La titulación de grado equivalente es la Licence SPI (orientación MGC, parcours Ingénierie Mécanique et Matériaux, site de Metz; también BUT GMP en varios IUT, no examinados). La ficha pública (formations.univ-lorraine.fr, PrestaShop; robots permite salvo parámetros ?order= etc.) solo describe el programa en prosa (pestaña Programme: L1-L3, 30 ECTS/semestre) sin lista de UE ni guías por asignatura; el PDF 'Détail des enseignements' de formulconnect.univ-lorraine.fr devuelve 404; la FST (fst.univ-lorraine.fr) no se exploró en profundidad. Catálogo parcial vacío; sin Fase 2." + " Comprobaciones: " + " | ".join(res))
cat = Catalog(meta=meta, asignaturas=[])
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(meta.estado, res)
