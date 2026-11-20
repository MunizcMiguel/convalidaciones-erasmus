#!/usr/bin/env python3
"""Fase 1 — Universidad de Málaga, Grado en Ingeniería Mecánica (Escuela de Ingenierías Industriales, título 5043).

Fuente: programación docente del grado en www.uma.es (`/centers/subjects_center/escuela-de-ingenierias-industriales/5043/`, HTML estático,
una tabla: Código, Asignatura, Curso, Semestre, Carácter, Créditos; cada fila enlaza a `/centers/subject/5043/{id}`).
Las guías son PDF en sara.uma.es (`/ht/2026/ProgramasAsignaturas_Titulacion_5043_AsigUMA_{id}.pdf`), host cuyo robots.txt lo prohíbe todo
(PoliteClient: RobotsBlocked): catálogo `parcial`, sin Fase 2.
Uso: python universidades/es_malaga/discover_es_malaga.py
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
SLUG, UNI = "es_malaga", "Universidad de Málaga"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.uma.es/centers/subjects_center/escuela-de-ingenierias-industriales/5043/"
PDF = "https://sara.uma.es/ht/2026/ProgramasAsignaturas_Titulacion_5043_AsigUMA_{i}.pdf"
CAR = {"formación básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa", "trabajo fin de grado": "tfg", "trabajo fin de estudios": "tfg",
       "prácticas externas": "practicas", "prácticas en empresa": "practicas"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
guia_bloqueada = not http._rules_for("https://sara.uma.es").can_fetch(PDF.format(i="50668"))
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries = []
for tr in soup.find("table").find_all("tr"):
    td = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
    a = tr.find("a", href=re.compile(r"/centers/subject/5043/\d+"))
    if len(td) < 6 or not a:
        continue
    code, nombre, curso, sem, car, ects = td[:6]
    sid = a["href"].rstrip("/").rsplit("/", 1)[-1]
    sm = re.match(r"(\d)", sem)
    entries.append(CatalogEntry(
        universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre, curso_semestre=f"Curso {curso} / {sem}",
        curso=int(curso), semestre=(int(curso) - 1) * 2 + int(sm.group(1)) if sm else None, creditos_ects=float(ects.replace(",", ".")),
        caracter=CAR.get(car.lower(), car.lower()), idioma_pagina="es", url_guia_docente=PDF.format(i=sid), tipo_fuente="pdf"))
assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s, "bloqueada:", guia_bloqueada)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático de la programación docente del grado en www.uma.es (tabla única); guía = PDF por asignatura en sara.uma.es.",
    generado_por="discover_es_malaga.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial" if guia_bloqueada else "ok",
    notas=(f"{len(entries)} asignaturas. ECTS por carácter {json.dumps(s)} frente al RUCT 60 básica/138 obligatorias/30 optativas/12 TFG: básica, obligatorias y TFG coinciden; se ofertan 96 ECTS optativos (se cursan 30). "
           f"PARCIAL: las guías PDF se sirven desde sara.uma.es, cuyo robots.txt prohíbe el acceso automatizado (RobotsBlocked); no se descarga nada de ese host. Sin Fase 2. "
           f"Las URLs de guía son informativas (patrón sara.uma.es/ht/2026/ProgramasAsignaturas_Titulacion_5043_AsigUMA_{{id}}.pdf, id = el de /centers/subject/5043/{{id}}). "
           f"Centro único (Escuela de Ingenierías Industriales)."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(http.stats)
