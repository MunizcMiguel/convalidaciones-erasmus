#!/usr/bin/env python3
"""Fase 1 — Mondragon Unibertsitatea, Grado en Ingeniería Mecánica (Escuela Politécnica Superior, plan 2017).
Fuente: https://mondragon.edu/grado-ingenieria-mecanica/plan-estudios/2017 (HTML estático): una tabla por semestre con enlace PDF por asignatura.
Uso: python universidades/es_mondragon_unibertsitatea/discover_es_mondragon_unibertsitatea.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_mondragon_unibertsitatea", "Mondragon Unibertsitatea"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://mondragon.edu/grado-ingenieria-mecanica/plan-estudios/2017"
CAR = {"FB": "formacion_basica", "OB": "obligatoria", "OP": "optativa"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries, seen = [], set()
for t in soup.find_all("table"):
    h = t.find_previous(["h2", "h3", "h4", "h5", "strong"])
    ht = h.get_text(" ", strip=True) if h else ""
    m = re.match(r"(\d)\D*Curso\D+(\d)\D*semestre", ht, re.I)
    if not m:
        continue
    curso, sem = int(m[1]), int(m[2])
    for tr in t.find_all("tr"):
        td = tr.find_all("td")
        a = tr.find("a", href=re.compile(r"M2GM.*\.pdf"))
        if len(td) < 4 or not a:
            continue
        code = re.search(r"/([A-Z0-9]+)-es\.pdf", a["href"])[1]
        nombre, tipo, ects = td[1].get_text(" ", strip=True), td[2].get_text(strip=True), float(td[3].get_text(strip=True).replace(",", "."))
        car = "tfg" if re.search(r"(?i)trabajo fin|proyecto fin", nombre) else CAR[tipo]
        assert code not in seen, code
        seen.add(code)
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre, curso_semestre=f"Curso {curso} / Semestre {sem}",
            curso=curso, semestre=sem, creditos_ects=ects, caracter=car, idioma_pagina="es", url_guia_docente=a["href"], tipo_fuente="pdf"))
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático del plan 2017 en mondragon.edu: tablas por semestre; PDF por asignatura (variante -es).",
    generado_por="discover_es_mondragon_unibertsitatea.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas del plan 2017 (EPS, campus de Arrasate; página «plan-estudios/2017»; la web no indica el año de la edición de las fichas). "
           f"ECTS por carácter (ofertados) {json.dumps(s)} frente al RUCT (básica 60, obligatorios 108, optativos 60, TFG 12): en 4.º se ofertan optativas por encima de las 60 exigidas. "
           "Código = el de la ficha PDF (p. ej. GMC201). La columna idioma de la web indica E/C/I por grupo; se toma siempre la versión -es."))
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=entries).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
