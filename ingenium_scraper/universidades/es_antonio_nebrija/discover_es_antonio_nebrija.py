#!/usr/bin/env python3
"""Fase 1 — Universidad Antonio de Nebrija, Grado en Ingeniería Mecánica (EPS).
Fuente: ficha del grado en www.nebrija.com (Gatsby/Griddo). Solo el 1.º curso (2 semestres) está en el HTML estático; los cursos 2.º-4.º
se pintan por JS y el endpoint page-data está vetado por robots.txt -> catálogo PARCIAL (1.º curso). Guías: PDF bilingüe por asignatura.
Uso: python universidades/es_antonio_nebrija/discover_es_antonio_nebrija.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_antonio_nebrija", "Universidad Antonio de Nebrija"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.nebrija.com/carreras-universitarias/grado-ingenieria-mecanica/"
CAR = {"básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries = []
for card in soup.select("div[class*=semesterCard]"):
    title = card.get_text("|", strip=True).split("|")[0]
    sem = 1 if title.startswith("Primer") else 2
    toks = []  # recorre el DOM en orden: textos y enlaces PDF
    for n in card.descendants:
        if getattr(n, "name", None) == "a" and "pdf-asignaturas" in n.get("href", ""):
            toks.append(("pdf", n["href"]))
        elif isinstance(n, str) and n.strip():
            toks.append(("t", n.strip()))
    i = 0
    while i < len(toks):
        if toks[i][0] == "t" and i + 3 < len(toks) and toks[i + 1][0] == "t" and toks[i + 1][1].lower() in CAR and toks[i + 2][1].isdigit():
            nombre, car, ects = toks[i][1], toks[i + 1][1].lower(), float(toks[i + 2][1])
            pdf = None
            j = i + 3
            while j < len(toks) and toks[j][0] != "pdf" and not (j + 1 < len(toks) and toks[j + 1][1].lower() in CAR):
                j += 1
            if j < len(toks) and toks[j][0] == "pdf":
                pdf = toks[j][1]
            code = re.sub(r"[^a-z0-9]+", "-", __import__("unicodedata").normalize("NFKD", nombre.lower()).encode("ascii", "ignore").decode()).strip("-")[:60]
            entries.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre, curso_semestre=f"Curso 1 / Semestre {sem}",
                curso=1, semestre=sem, creditos_ects=ects, caracter=CAR[car], idioma_pagina="es",
                url_guia_docente=pdf, tipo_fuente="pdf" if pdf else "sin_guia"))
            i += 3
        else:
            i += 1
assert len({e.codigo_asignatura for e in entries}) == len(entries)
tot = sum(e.creditos_ects for e in entries)
print(len(entries), tot, [e.tipo_fuente for e in entries])
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático de la ficha del grado: tarjetas por semestre (solo 1.º curso); PDF bilingüe por asignatura.",
    generado_por="discover_es_antonio_nebrija.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas=(f"PARCIAL: {len(entries)} asignaturas ({tot:g} ECTS) de 1.º curso; los cursos 2.º-4.º no están en el HTML (se cargan por JS; "
           "/page-data/ vetado por robots.txt, no se usa navegador). No validable contra el RUCT (básica 72, obligatorias 144, prácticas 12, TFG 12). "
           "Código = slug del nombre (la web no da código). Solo las asignaturas con enlace PDF en la ficha tienen guía; el resto sin_guia. "
           "Las guías PDF son bilingües ES/EN (página 1 = portada)."))
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=entries).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
