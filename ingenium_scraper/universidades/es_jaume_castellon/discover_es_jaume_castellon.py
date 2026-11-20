#!/usr/bin/env python3
"""Fase 1 — Universitat Jaume I, Grau en Enginyeria Mecànica (ESTCE).

Fuente: SIA (ujiapps.uji.es/sia, publicación pública). Plan 222 (el antiguo, con los 4 cursos publicados y docencia en 2026-27);
el plan nuevo de 2026 (estudio 275, RD 822/2021) solo publica 1.º (10 asignaturas) — ver notas.
Uso: python universidades/es_jaume_castellon/discover_es_jaume_castellon.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_jaume_castellon", "Universitat Jaume I de Castelló"
GRADO = "Grau en Enginyeria Mecànica"
ESTUDIO = 222
URL = f"https://ujiapps.uji.es/sia/rest/publicacion/estudio/{ESTUDIO}"
BASE = "https://ujiapps.uji.es"
CAR = {"formació bàsica": "formacion_basica", "obligatòria": "obligatoria", "optativa": "optativa",
       "projecte final": "tfg", "pràctiques": "practicas"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries = []
for div in soup.select("div.asignatura"):
    a = div.select_one("p.titulo a")
    code, nombre = [x.strip() for x in a.get_text(" ", strip=True).split(" - ", 1)]
    info = div.select_one("div.infoasignatura p").get_text(" ", strip=True)
    m = re.match(r"Curs (\d) - (?:Semestre (\d)|(.+?)) - (.+)$", info)
    curso, sem, otro, car = int(m.group(1)), m.group(2), m.group(3), m.group(4).strip().lower()
    ects = float(div.select_one("tr.cantidad td").get_text(strip=True).replace(",", "."))
    entries.append(CatalogEntry(
        universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
        curso_semestre=f"Curso {curso} / " + (f"Semestre {sem}" if sem else otro),
        curso=curso, semestre=(curso - 1) * 2 + int(sem) if sem else None, creditos_ects=ects,
        caracter=CAR[car], idioma_pagina="ca", url_guia_docente=BASE + a["href"], tipo_fuente="html"))

assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL,
    ects_totales_plan=240.0,
    estrategia_fuente="SIA de la UJI (HTML): lista del estudio 222 con código, curso, semestre, carácter y ECTS; la guía se compone de las subpáginas del SIA (temario, metodología, evaluación, actividades/competencias, requisitos).",
    generado_por="discover_es_jaume_castellon.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas del plan 222 (plan anterior al de 2026, en extinción; es el único con los 4 cursos publicados). "
           f"El RUCT 2502271 (RD 822/2021, plan 2026, estudio SIA 275) solo tiene publicado 1.º (10 asignaturas, 60 ECTS básicos = RUCT). "
           f"ECTS por carácter del plan 222: {json.dumps(s)}; obligatorias+básica {s['obligatoria']+s['formacion_basica']:g}, optativas ofertadas {s['optativa']:g}, "
           f"prácticas {s['practicas']:g}, TFG {s['tfg']:g}. No coincide con el desglose RUCT 60/144/18/6/12 (el plan viejo tiene 72 básicos y 66 optativos ofertados de los que se cursan 18); "
           f"coinciden prácticas (6) y TFG (12). Las guías de 1.º del plan 222 no publican evaluación ('en extinción: ver aula virtual'). "
           f"La guía completa (e-ujier.uji.es/pls) está bloqueada por robots.txt y no se usa; solo se usan las subpáginas /sia/ (permitidas). Catalán (la alternancia a español pasa por /upo/, bloqueada)."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, http.stats)
