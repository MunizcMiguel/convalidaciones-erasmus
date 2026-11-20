#!/usr/bin/env python3
"""Fase 1 — Universidad Pública de Navarra, Grado en Ingeniería Mecánica (ETS Ingeniería Industrial, Informática y de Telecomunicación).

Fuente: página del plan de estudios en unavarra.es (HTML estático): tablas por curso del plan 248 (acceso desde 2020-21, el vigente)
+ tablas de optatividad. La ficha es `ficha-asignaturaDOA?idioma=es&codAsig={codigo}` (HTML).
Uso: python universidades/es_publica_navarra/discover_es_publica_navarra.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_publica_navarra", "Universidad Pública de Navarra"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.unavarra.es/sites/grados/industriales/ingenieria-mecanica/plan-de-estudios.html"
FICHA = "https://www.unavarra.es/ficha-asignaturaDOA?idioma=es&codAsig={c}"
CAR = {"básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa", "tfg": "tfg"}
RUCT = {"formacion_basica": 60, "obligatoria": 138, "tfg": 18}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
tables = [t for t in soup.find_all("table") if t.find("tr") and t.find("tr").get_text(" ", strip=True).startswith(("Código", "Códigos"))]
plan248 = []
for t in tables:
    first = t.find_all("tr")[1].find_all("td")[0].get_text(strip=True)
    if first.startswith("248"):
        plan248.append(t)
entries = []
curso = 0
for t in plan248:
    rows = [[c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])] for tr in t.find_all("tr")[1:]]
    if t.find_all("tr")[0].get_text(" ", strip=True).startswith("Códigos"):
        curso = 4  # optatividad: se cursa en 4.º
    else:
        curso += 1
    for r in rows:
        if len(r) < 4 or not r[0].isdigit():
            continue
        code, nombre, car, ects = r[0], r[1], r[2].lower(), float(r[3].replace(",", "."))
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre.capitalize(),
            curso_semestre=f"Curso {curso}", curso=curso, semestre=None, creditos_ects=ects, caracter=CAR[car], idioma_pagina="es",
            url_guia_docente=FICHA.format(c=code), tipo_fuente="html"))
assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
# optativas sin oferta en el curso en vigor: la ficha dice "No hay datos para esta asignatura en el año académico en curso"
for e in entries:
    if "No hay datos para esta asignatura" in http.get_text(e.url_guia_docente, encoding="utf-8"):
        e.url_guia_docente, e.tipo_fuente = None, "sin_guia"
sin = [e.codigo_asignatura for e in entries if e.tipo_fuente == "sin_guia"]
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(s)
assert all(s[k] == v for k, v in RUCT.items()), s
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático del plan de estudios de unavarra.es: tablas por curso (plan 248) y de optatividad; ficha HTML por asignatura.",
    generado_por="discover_es_publica_navarra.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas del plan 248 (acceso desde 2020-21; la página lista también el plan 245, anterior, que no se usa). Centro único. "
           f"ECTS por carácter {json.dumps(s)}: básica 60, obligatorias 138 y TFG 18 = RUCT; se ofertan {s['optativa']:g} ECTS optativos y el RUCT exige 24 (total 60+138+24+18=240). "
           f"Las optativas se colocan en 4.º. Sin ficha en 2026-27 (sin_guia, optativas no ofertadas): {', '.join(sin) or 'ninguna'}. El semestre no está en el plan: solo en la cabecera de la ficha ('Periodo'), que se copia al Markdown; semestre=null en el catálogo."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), http.stats)
