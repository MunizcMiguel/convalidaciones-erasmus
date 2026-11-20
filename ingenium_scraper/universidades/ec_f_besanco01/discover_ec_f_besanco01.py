#!/usr/bin/env python3
"""Fase 1 — Université Marie et Louis Pasteur (ex Univ. de Franche-Comté), Besançon.
Grado: Licence Sciences pour l'ingénieur, parcours Génie mécanique (UFR ST, 180 ECTS), parcours "Mécanique".
Fuente: sitemap.xml de formations.univ-fcomte.fr (catálogo ODF/Ametys): el árbol de URLs reproduce el plan
(licence > parcours/semestre > UE > ELC); cada hoja es una ficha HTML con ECTS, horas y MCC.
L1 = Portail 3 (S1) + Parcours SPI (S2); L2 = S3/S4 'Mécanique et génie mécanique'; L3 = Parcours Mécanique Sem 5/6 (ids MBGN*, versión más reciente).
Uso: python universidades/ec_f_besanco01/discover_ec_f_besanco01.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "ec_f_besanco01", "Université Marie et Louis Pasteur (ex Université de Franche-Comté), Besançon"
GRADO = "Licence Sciences pour l'ingénieur — Génie mécanique (parcours Mécanique), UFR ST"
SITEMAP = "https://formations.univ-fcomte.fr/sitemap.xml"
BASE = "licence-sciences-pour-l-ingenieur-genie-mecanique-ufr-st-M4QU6Q88"
# (segmento del árbol, semestre absoluto)
BRANCHES = [("portail-3-M372QKM9", 1), ("parcours-sciences-pour-l-ingenieur-M372PT4X", 2),
            ("s3-parcours-mecanique-et-genie-mecanique-MAXNTRTH", 3), ("s4-parcours-mecanique-et-genie-mecanique-MAXNTUYY", 4),
            ("parcours-mecanique-sem-5-MBGNP65D", 5), ("parcours-mecanique-sem-6-MBGNPA5F", 6)]

http = PoliteClient(cache_dir=HERE / "raw_cache")
urls = re.findall(r"<loc>([^<]+)</loc>", http.get_text(SITEMAP))
tree = [u for u in urls if BASE in u and u.endswith(".html")]
entries, seen = [], {}
for seg, sem in BRANCHES:
    mine = [u[:-5] for u in tree if f"/{BASE}/{seg}/" in u]
    for u in sorted(mine):
        if any(o != u and o.startswith(u + "/") for o in mine):
            continue  # contenedor (UE con ELC): solo hojas
        url = u + ".html"
        s = BeautifulSoup(http.get_text(url), "lxml")
        title = s.find("h1").get_text(" ", strip=True)
        txt = s.get_text(" ", strip=True)
        m = re.search(r"ECTS\s+([\d.,]+)\s+crédit", txt)
        cred = float(m.group(1).replace(",", ".")) if m else None
        code = re.search(r"-(M[A-Z0-9]{7})$", u).group(1)
        if code in seen:
            continue
        seen[code] = 1
        carac = "practicas" if "stage" in title.lower() else None
        entries.append(CatalogEntry(universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
            curso_semestre=f"Curso {(sem + 1) // 2} / Semestre {sem}", curso=(sem + 1) // 2, semestre=sem, creditos_ects=cred,
            caracter=carac, idioma_pagina="fr", url_guia_docente=url, tipo_fuente="html"))
assert len({e.codigo_asignatura for e in entries}) == len(entries)
por_sem = {}
for e in entries:
    por_sem[e.semestre] = por_sem.get(e.semestre, 0) + (e.creditos_ects or 0)
meta = CatalogMeta(universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios="https://formations.univ-fcomte.fr/plugins/odf-web/odf/_content/subprogram-licence-sciences-pour-l-ingenieur-genie-mecanique-fr-2-fr/Licence%20Sciences%20pour%20l'ing%C3%A9nieur%20G%C3%A9nie%20m%C3%A9canique,%20UFR%20ST.pdf",
    ects_totales_plan=180.0, estrategia_fuente="sitemap.xml del catálogo ODF (formations.univ-fcomte.fr) + fichas HTML por ELC.",
    generado_por="discover_ec_f_besanco01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas=(f"Licence SPI parcours Génie mécanique (Besançon, UFR ST); parcours 'Mécanique'. L1 = portail 3 + parcours SPI (semestres 1-2), L2 = parcours 'Mécanique et génie mécanique' (S3-S4), L3 = parcours Mécanique S5-S6 (ids MBGN*; hay también variantes MAXN* y LAS no incluidas). "
           f"{len(entries)} fichas (ELC/UE hoja). ECTS por semestre {json.dumps(por_sem)} (suma {sum(por_sem.values()):g}/180). "
           "PARCIAL: las fichas del catálogo solo contienen ECTS, horas CM/TD/TP y modalidades de control (MCC); NO hay temario, resultados de aprendizaje ni bibliografía. "
           "Las UE 'contenedor' (con ELC) no se listan; algunas UE de L1 (chimie, physique...) se listan como hoja."))
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), por_sem, http.stats)
