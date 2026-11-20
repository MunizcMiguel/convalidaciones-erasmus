#!/usr/bin/env python3
"""Fase 1 — UNED, Grado en Ingeniería Mecánica (ETSI Industriales), PLAN 2024 (RD 822/2021, el que admite alumnos nuevos).
Fuente: ficha del grado en www.uned.es (HTML estático): una tabla por curso con código, nombre, carácter y créditos; semestre por filas «SEMESTRE n».
Guía: PDF público `PDFGuiaPublica?codigoAsignatura=…&curso=2027`. Uso: python universidades/es_nacional_educacion_a_distanc/discover_es_nacional_educacion_a_distanc.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_nacional_educacion_a_distanc", "Universidad Nacional de Educación a Distancia"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.uned.es/universidad/inicio/estudios/grados/grado-en-ingenieria-mecanica.html"
PDF = "https://www.uned.es/universidad/pdf/GuiasAsignaturasGrados/PDFGuiaPublica?codigoAsignatura={c}&curso=2027&codigoTitulacion=6803&language=es&esMaster=false"
CAR = {"FORMACIÓN BÁSICA": "formacion_basica", "OBLIGATORIAS": "obligatoria", "OPTATIVAS": "optativa", "TRABAJO FINAL OBLIGATORIO": "tfg"}
CURSO = {"PRIMER": 1, "SEGUNDO": 2, "TERCER": 3, "CUARTO": 4}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries, seen = [], set()
tabs = soup.select("table.tabla_asignaturas.hidden-xs")
for t in tabs[:4]:  # las 4 primeras tablas (cursos 1-4) son el Plan 2024; las siguientes, Plan 2009 (comprobado con los títulos)
    curso = sem = None
    for tr in t.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if not cells:
            continue
        a = tr.find("a", href=re.compile("codAsignatura"))
        m = re.match(r"(PRIMER|SEGUNDO|TERCER|CUARTO) CURSO", cells[0])
        if m and not a:
            curso = CURSO[m[1]]
            continue
        ms = re.search(r"SEMESTRE (\d)", " ".join(cells))
        if ms and not a:
            sem = int(ms[1]) + (curso - 1) * 2 if curso else None
            continue
        if a and cells[2] in CAR:
            code = re.search(r"codAsignatura=([\d-]+)", a["href"])[1]  # algunos códigos UNED terminan en guion, p. ej. «6890210-»
            nombre, car, ects = cells[1], CAR[cells[2]], float(cells[3].replace(",", "."))
            if code in seen:
                continue
            seen.add(code)
            if re.search(r"(?i)trabajo fin|proyecto fin", nombre):
                car = "tfg"
            entries.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre.title() if nombre.isupper() else nombre,
                curso_semestre=f"Curso {curso} / Semestre {sem}", curso=curso, semestre=sem, creditos_ects=ects, caracter=car, idioma_pagina="es",
                url_guia_docente=PDF.format(c=code), tipo_fuente="pdf"))
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático de la ficha del grado (plan 2024); PDF de guía pública por asignatura.",
    generado_por="discover_es_nacional_educacion_a_distanc.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas del Plan 2024 (la ficha lista también el Plan 2009, no usado, y asignaturas extinguidas). ECTS por carácter (ofertados) {json.dumps(s)} "
           "frente al RUCT (básica 60, obligatorios 148, optativos 20, TFG 12): se ofertan más optativas de las 20 exigidas. Centro único (ETSI Industriales). "
           "Semestre = semestre absoluto calculado desde la fila «SEMESTRE n» de cada curso."))
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=entries).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
