#!/usr/bin/env python3
"""Fase 1 — Universitat Rovira i Virgili, Grado en Ingeniería Mecánica (ETSEQ, plan 2010).

Fuente: Guía docente de la URV (guiadocent.urv.cat/docnet/guia_docent): listado `?centre=20&ensenyament=2022&consulta=assignatures&idioma=cast`
con una tabla por curso (Código, Nombre, Periodo, Tipo, Cr.totales); la guía es HTML por asignatura y apartados (`fitxa_apartat=N`).
Uso: python universidades/es_rovira_virgili/discover_es_rovira_virgili.py
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
SLUG, UNI = "es_rovira_virgili", "Universitat Rovira i Virgili"
GRADO = "Grado en Ingeniería Mecánica"
B = "https://guiadocent.urv.cat/docnet/guia_docent/index.php"
LIST = f"{B}?centre=20&ensenyament=2022&consulta=assignatures&idioma=cast"
CAR = {"formación básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa", "trabajo fin de grado": "tfg",
       "prácticas externas optativas": "practicas"}
ORD = {"primer": 1, "segundo": 2, "tercer": 3, "cuarto": 4}
RUCT = {"formacion_basica": 60, "obligatoria": 141, "tfg": 12}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(LIST), "lxml")
entries = []
for tr in soup.find_all("tr"):
    td = [c.get_text(" ", strip=True) for c in tr.find_all("td", recursive=False)]
    if len(td) < 5 or not td[0].isdigit():
        continue
    # el título de la tabla («Primer Curso», «Optativas»...) es el último texto de ese tipo antes de la fila
    head = tr.find_previous(string=re.compile(r"(Primer|Segundo|Tercer|Cuarto)\s+Curso|Optativ"))
    htxt = (head or "").replace(" ", " ").strip().lower()
    m = re.match(r"(primer|segundo|tercer|cuarto)", htxt)
    curso = ORD[m.group(1)] if m else 4
    code, nombre, per, tipo, ects = td[:5]
    sem = {"1Q": 1, "2Q": 2}.get(per[:2])
    entries.append(CatalogEntry(
        universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre.capitalize(),
        curso_semestre=f"Curso {curso} / {per}", curso=curso, semestre=(curso - 1) * 2 + sem if sem else None,
        creditos_ects=float(ects.replace(",", ".")), caracter=CAR[tipo.lower()], idioma_pagina="es",
        url_guia_docente=f"{B}?centre=20&ensenyament=2022&assignatura={code}&idioma=cast", tipo_fuente="html"))
assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s)
assert all(s[k] == v for k, v in RUCT.items()), s
by = {}
for e in entries:
    by[e.curso] = by.get(e.curso, 0) + 1
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=LIST, ects_totales_plan=240.0,
    estrategia_fuente="HTML de la Guía docente URV (tablas por curso en consulta=assignatures); guía HTML por asignatura, apartados vía fitxa_apartat.",
    generado_por="discover_es_rovira_virgili.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas, centro ETSEQ (Tarragona). Plan 2010 (RD 1393/2007), el único del grado. ECTS por carácter {json.dumps(s)}: básica 60, obligatorias 141 y TFG 12 = RUCT; "
           f"se ofertan {s['optativa']:g} ECTS optativos + {s['practicas']:g} de prácticas externas optativas (RUCT: 27 optativos y 0 prácticas obligatorias en el desglose; el RUCT cuenta 27 de optativas cursadas, "
           f"y las prácticas externas optativas computan dentro de ellas). Asignaturas por curso en el listado: {json.dumps(by)}. Optativas y prácticas colocadas según la tabla en que aparecen."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(by, http.stats)
