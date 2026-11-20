#!/usr/bin/env python3
"""Fase 1 — Universidade de Vigo, Grado en Ingeniería Mecánica (Escuela de Ingeniería Industrial, centro 312; también se imparte en el CUD Marín).
Fuente: Docnet (secretaria.uvigo.gal/docnet-nuevo/guia_docent), listado «Asignaturas» del título V12G380V01 en castellano (HTML estático).
Uso: python universidades/es_vigo/discover_es_vigo.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_vigo", "Universidad de Vigo"
GRADO = "Grado en Ingeniería Mecánica"
BASE = "https://secretaria.uvigo.gal/docnet-nuevo/guia_docent/"
URL = BASE + "?centre=312&ensenyament=V12G380V01&consulta=assignatures&idioma=cast"
GUIA = BASE + "?centre=312&ensenyament=V12G380V01&assignatura={c}&idioma=cast&any_academic=2026_27&idioma_assig=cast"
CAR = {"FB": "formacion_basica", "OB": "obligatoria", "OP": "optativa"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries, seen, curso = [], set(), 0
for tr in soup.find_all("tr"):
    if tr.find("tr") or tr.find("table"):
        continue
    cells = [c.get_text(" ", strip=True).replace("\xa0", " ") for c in tr.find_all(["td", "th"])]
    if len(cells) == 1 and (m := re.fullmatch(r"(\d) Curso", cells[0])):
        curso = int(m[1])
        continue
    if len(cells) >= 5 and re.fullmatch(r"V12G380V01\d{3}", cells[0]) and cells[0] not in seen:
        code, nombre, cuat, tipo, ects = cells[:5]
        seen.add(code)
        sem = {"1c": 1, "2c": 2}.get(cuat.strip())
        car = "tfg" if re.search(r"(?i)trabajo de fin de grado", nombre) else ("practicas" if re.search(r"(?i)^pr[aá]cticas en empresa", nombre) else CAR[tipo])
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre, curso_semestre=f"Curso {curso} / {cuat}",
            curso=curso, semestre=((curso - 1) * 2 + sem) if sem else None, creditos_ects=float(ects.replace(",", ".")), caracter=car, idioma_pagina="es",
            url_guia_docente=GUIA.format(c=code), tipo_fuente="html"))
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático de Docnet (listado de asignaturas del título V12G380V01, castellano); ficha HTML por asignatura.",
    generado_por="discover_es_vigo.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas, Escuela de Ingeniería Industrial (centro 312); el Grado también se imparte en el CUD de la Escuela Naval Militar de Marín (no incluido). "
           f"ECTS por carácter (ofertados) {json.dumps(s)} frente al RUCT (básica 60, obligatorios 126, optativos 42, TFG 12): la web ofrece más optativas de las 42 exigidas. "
           "El nombre de la asignatura mantiene el formato «Materia: Asignatura». Semestre derivado de «1c/2c» (Oficina técnica: «1c 2c» → null). Las guías pueden estar en gallego/castellano: se pide idioma=cast."))
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=entries).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
