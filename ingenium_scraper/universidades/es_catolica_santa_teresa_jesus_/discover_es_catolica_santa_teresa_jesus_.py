#!/usr/bin/env python3
"""Fase 1 — Universidad Católica de Ávila (UCAV), Grado en Ing. Mecánica (Facultad de Ciencias y Artes).
Fuente: PDF del plan de estudios 2025/26 (4 págs.) en ucavila.es. No se localizó ninguna URL pública de guías docentes -> catálogo PARCIAL, todas sin_guia, sin Fase 2.
Uso: python universidades/es_catolica_santa_teresa_jesus_/discover_es_catolica_santa_teresa_jesus_.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_catolica_santa_teresa_jesus_", "Universidad Católica Santa Teresa de Jesús de Ávila"
GRADO = "Grado en Ingeniería Mecánica"
PDF = "https://www.ucavila.es/downloads/planes-Estudio/25-26/GIM.pdf"
CAR = {"Básica": "formacion_basica", "Obligatoria": "obligatoria", "Optativa": "optativa"}
RUCT = {"formacion_basica": 62, "obligatoria": 151, "tfg": 12}

http = PoliteClient(cache_dir=HERE / "raw_cache")
with pdfplumber.open(http.get_file(PDF)) as d:
    text = "\n".join((p.extract_text() or "") for p in d.pages)
entries, seen = [], set()
curso = 0
for l in text.split("\n"):
    if re.match(r"^(PRIMER|SEGUNDO|TERCER|CUARTO) CURSO$", l):
        curso += 1
    m = re.match(r"^(\d{5}GT) (.+) (Básica|Obligatoria|Optativa) (\d+) ([12])$", l)
    if not m or m[1] in seen:
        continue
    seen.add(m[1])
    code, name, car, ects, sem = m.groups()
    car = "tfg" if re.search(r"(?i)trabajo fin de grado", name) else CAR[car]
    entries.append(CatalogEntry(
        universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name.strip(), curso_semestre=f"Curso {curso} / Semestre {(curso - 1) * 2 + int(sem)}",
        curso=curso, semestre=(curso - 1) * 2 + int(sem), creditos_ects=float(ects), caracter=car, idioma_pagina="es", url_guia_docente=None, tipo_fuente="sin_guia"))
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=PDF, ects_totales_plan=240.0,
    estrategia_fuente="PDF del plan de estudios 2025/26 (texto): filas «código asignatura carácter ECTS semestre».",
    generado_por="discover_es_catolica_santa_teresa_jesus_.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas=(f"PARCIAL: {len(entries)} asignaturas con código (ECTS por carácter {json.dumps(s)}). El PDF lista además 3 plazas genéricas «Optativa del Grupo A/B/C/D» (15 ECTS; no son asignaturas concretas) "
           "y los grupos de optativas, que no se incluyen. Con las 15 ECTS de optativas, básica 62 + obligatoria 151 + optativas 15 + TFG 12 = 240 = RUCT. "
           "No se encontró URL pública de guías docentes (la búsqueda solo dio el plan en PDF), así que todo es sin_guia y no hay Fase 2."))
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=entries).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
