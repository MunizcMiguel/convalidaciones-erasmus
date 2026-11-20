#!/usr/bin/env python3
"""Fase 1 — Université de Bourgogne (Dijon), Licence Sciences pour l'ingénieur parcours Mécanique (UFR ST).
Fuente: sitemap.xml de formations.ube.fr (catálogo ODF/Ametys, robots permite): árbol licence > parcours Mécanique > UE; hojas = fichas HTML.
Se catalogan las UE hoja de L3 (S5-S6, nodos propios de Mécanique) y 'ue37-meca4a' (S4). L1-L2 son parcours genéricos de física/mates/informática.
Uso: python universidades/ec_f_dijon01/discover_ec_f_dijon01.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "ec_f_dijon01", "Université de Bourgogne (uB), Dijon"
GRADO = "Licence Sciences pour l'ingénieur, parcours Mécanique (UFR Sciences et Techniques)"
SITEMAP = "https://formations.ube.fr/sitemap.xml"
BASE = "licence-sciences-pour-l-ingenieur-LMGC20SA/mecanique-LMGEP01E"

http = PoliteClient(cache_dir=HERE / "raw_cache")
urls = re.findall(r"<loc>([^<]+)</loc>", http.get_text(SITEMAP))
tree = sorted({u[:-5] for u in urls if BASE in u and u.endswith(".html")})
def rel(u):
    return u.split(BASE + "/", 1)[1] if BASE + "/" in u else ""
def sem_of(u):
    r = rel(u)
    if not r or r.startswith(("parcours-", "module-mineure", "ue-mineure")):
        return None
    if r.startswith(("ue-obligatoires-s6", "ue-a-choix-1-option-parmi-2")) or "-m6" in r.split("/")[0] or "m6" in r.split("/")[-1][:20]:
        return 6
    return 5
leaves = []
for u in tree:
    if rel(u) and not any(o != u and o.startswith(u + "/") for o in tree):
        s = sem_of(u)
        if s:
            leaves.append((u, s))
        elif re.search(r"ue37-meca4a", u):
            leaves.append((u, 4))
entries, seen = [], {}
for u, sem in leaves:
    url = u + ".html"
    s = BeautifulSoup(http.get_text(url), "lxml")
    title = s.find("h1").get_text(" ", strip=True)
    txt = s.get_text(" ", strip=True)
    m = re.search(r"ECTS\s+([\d.,]+)\s+crédit", txt)
    cred = float(m.group(1).replace(",", ".")) if m else None
    code = re.search(r"-([A-Z0-9]{8})$", u).group(1)
    if code in seen:
        continue
    seen[code] = 1
    carac = "optativa" if "option" in rel(u).lower() else None
    entries.append(CatalogEntry(universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
        curso_semestre=f"Curso {(sem + 1) // 2} / Semestre {sem}", curso=(sem + 1) // 2, semestre=sem, creditos_ects=cred,
        caracter=carac, idioma_pagina="fr", url_guia_docente=url, tipo_fuente="html"))
assert len({e.codigo_asignatura for e in entries}) == len(entries)
por_sem = {}
for e in entries:
    por_sem[e.semestre] = por_sem.get(e.semestre, 0) + (e.creditos_ects or 0)
por_sem = {}
for e in entries:
    por_sem[e.semestre] = por_sem.get(e.semestre, 0) + (e.creditos_ects or 0)
meta = CatalogMeta(universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26",
    url_plan_estudios="https://formations.ube.fr/fr/offre-de-formation/licence-lmd-XA/licence-sciences-pour-l-ingenieur-LMGC20SA/mecanique-LMGEP01E.html",
    ects_totales_plan=180.0, estrategia_fuente="sitemap.xml del catálogo ODF (formations.ube.fr) + fichas HTML por UE.",
    generado_por="discover_ec_f_dijon01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas=(f"Licence SPI parcours Mécanique (no hay Licence 'génie mécanique'; BUT GMP está en IUT Le Creusot, no incluido). {len(entries)} fichas de UE hoja: L3 (S5-S6) + ue37-meca4a (S4). "
           f"ECTS listados por semestre {json.dumps(por_sem)} (las opciones suman más de 30). PARCIAL: L1-L2 son troncos genéricos (física/mates/informática/chimie) no catalogados; "
           "el árbol tiene variantes duplicadas (parcours-a-choix de varias cohortes) y no se garantiza que el parcours Mécanique S3-S4 esté completo; "
           "las fichas pueden carecer de temario."))
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), por_sem, http.stats)
