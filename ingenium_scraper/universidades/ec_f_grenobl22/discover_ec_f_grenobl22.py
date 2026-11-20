#!/usr/bin/env python3
"""Fase 1 — Grenoble: Licence Mécanique, parcours Génie mécanique et productique (2.º-3.er año), Université Grenoble Alpes.
NOTA: la titulación de grado es de la UGA (UFR PhITEM), campus de Grenoble; Grenoble INP-UGA (F GRENOBL22) solo ofrece cycle ingénieur (no examinado).
Fuente: sitemap.xml de formations.univ-grenoble-alpes.fr (catálogo ODF/Ametys, robots permite); hojas = fichas HTML de UE
(descripción, competencias, prerrequisitos, horas, ECTS, semestre, código Apogée).
Uso: python universidades/ec_f_grenobl22/discover_ec_f_grenobl22.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "ec_f_grenobl22", "Université Grenoble Alpes (UFR PhITEM) — Grenoble INP-UGA, Grenoble"
GRADO = "Licence Mécanique, parcours Génie mécanique et productique (2e et 3e année)"
SITEMAP = "https://formations.univ-grenoble-alpes.fr/sitemap.xml"
BASE = "offre-de-formation/licence-XA/licence-mecanique-IAI546M7/parcours-genie-mecanique-et-productique-2e-et-3e-annee-IAI5IME4"

http = PoliteClient(cache_dir=HERE / "raw_cache")
urls = re.findall(r"<loc>([^<]+)</loc>", http.get_text(SITEMAP))
leaves = sorted({u for u in urls if "/" + BASE + "/" in u and u.endswith(".html")})
entries, seen = [], {}
for url in leaves:
    s = BeautifulSoup(http.get_text(url), "lxml")
    main = s.find("main")
    title = re.sub(r"^U(?:E|ET)\s+", "", main.find("h1").get_text(" ", strip=True))
    txt = main.get_text("\n", strip=True)
    m = re.search(r"ECTS\s*\n?\s*([\d.,]+)\s+crédit", txt)
    cred = float(m.group(1).replace(",", ".")) if m else None
    sm = re.search(r"Période\s*\n?\s*Semestre\s+(\d)", txt)
    sem = int(sm.group(1)) if sm else None
    ap = re.search(r"Code d'export Apogée\s*\n?\s*([A-Z0-9]+)", txt)
    code = ap.group(1) if ap else url.rsplit("-", 1)[1][:-5]
    if code in seen:
        code = url.rsplit("-", 1)[1][:-5]
    seen[code] = 1
    lang = re.search(r"Langue\(s\) d'enseignement\s*\n?\s*([^\n]+)", txt)
    idioma = "en" if lang and "Anglais" in lang.group(1) and "Français" not in lang.group(1) else "fr"
    entries.append(CatalogEntry(universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
        curso_semestre=(f"Curso {(sem + 1) // 2} / Semestre {sem}" if sem else "Curso 2-3 (semestre no indicado)"), curso=((sem + 1) // 2 if sem else None), semestre=sem,
        creditos_ects=cred, caracter="practicas" if "stage" in title.lower() else None, idioma_pagina=idioma, url_guia_docente=url, tipo_fuente="html"))
assert len({e.codigo_asignatura for e in entries}) == len(entries)
por_sem = {}
for e in entries:
    por_sem[e.semestre] = por_sem.get(e.semestre, 0) + (e.creditos_ects or 0)
meta = CatalogMeta(universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios="https://formations.univ-grenoble-alpes.fr/fr/offre-de-formation/licence-XA/licence-mecanique-IAI546M7/parcours-genie-mecanique-et-productique-2e-et-3e-annee-IAI5IME4.html",
    ects_totales_plan=None, estrategia_fuente="sitemap.xml del catálogo ODF (formations.univ-grenoble-alpes.fr) + fichas HTML por UE.",
    generado_por="discover_ec_f_grenobl22.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas=(f"Grado elegido: Licence Mécanique de la UGA, parcours GMP (2.º-3.er año). La Licence es de la UGA, no de Grenoble INP-UGA (que solo imparte cycle ingénieur: Ense3, Phelma, Pagora, G-SCOP...; no examinado); "
           f"se usa porque es el equivalente de grado en Grenoble. {len(entries)} UE (ECTS por semestre {json.dumps(por_sem)}). PARCIAL: no se cataloga el 1.er año (portail SPI), ni el parcours 'Mécanique 3e année' ni 'Physique-Chimie-Mécanique international'; "
           "el parcours GMP tiene UE optativas/alternativas repartidas, por lo que la suma de ECTS no es un total de curso."))
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), por_sem, http.stats)
for e in entries: print(e.semestre, e.creditos_ects, e.codigo_asignatura, e.nombre_asignatura[:60])
