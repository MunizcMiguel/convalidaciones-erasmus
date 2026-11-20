#!/usr/bin/env python3
"""Fase 1 — Universidad de León, Grado en Ingeniería Mecánica (Escuela de Ingenierías Industrial, Informática y Aeroespacial).

Fuente: página «Plan de estudios» del grado en www.unileon.es: tablas por curso de dos planes, Plan (2010) y Plan (2025, RD 822/2021 = el que
admite estudiantes nuevos). Se toma el Plan (2025). La guía docente sale de la API del visor
(`https://guiadocenteapi.unileon.es/snapshots/2026-2027/{codigo}`, JSON; el visor https://visor-guiadocente.unileon.es es una SPA Angular).
Para 3.º y 4.º del Plan (2025) aún no hay guía publicada (la API no devuelve `data`): `sin_guia`.
Uso: python universidades/es_leon/discover_es_leon.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_leon", "Universidad de León"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.unileon.es/estudiantes/oferta-academica/grados/grado-en-ingenieria-mecanica/plan-estudios"
API = "https://guiadocenteapi.unileon.es/snapshots/2026-2027/{c}"
CAR = {"FB": "formacion_basica", "OB": "obligatoria", "OP": "optativa"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries = []
for tb in soup.find_all("table"):
    head = tb.find_previous(string=re.compile(r"Curso \dº, Plan \(\d{4}\)|Trabajo fin de grado, Plan \(\d{4}\)"))
    m = re.search(r"(Curso (\d)º|Trabajo fin de grado), Plan \((\d{4})\)", head or "")
    if not m or m.group(3) != "2025":
        continue
    curso = int(m.group(2)) if m.group(2) else 4
    for tr in tb.find_all("tr"):
        td = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(td) < 5 or not re.match(r"^\d{7}$", td[0]):
            continue
        code, nombre, per, tipo, ects = td[:5]
        sem = {"S1": 1, "S2": 2}.get(per)
        try:
            data = json.loads(http.get_bytes(API.format(c=code))).get("data")
        except (FetchError, ValueError):
            data = None
        has = bool(data and (data.get("contents") or data.get("learningAims")))
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre.capitalize(), curso_semestre=f"Curso {curso} / {per}",
            curso=curso, semestre=(curso - 1) * 2 + sem if sem else None, creditos_ects=float(ects.replace(",", ".")), caracter=CAR[tipo], idioma_pagina="es",
            url_guia_docente=API.format(c=code) if has else None, tipo_fuente="api" if has else "sin_guia"))
assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
sin = [e.codigo_asignatura for e in entries if e.tipo_fuente == "sin_guia"]
print(len(entries), s, "sin guía:", len(sin))
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML de la página Plan de estudios de unileon.es (tablas por curso, Plan 2025) + API JSON del visor de guías (guiadocenteapi.unileon.es).",
    generado_por="discover_es_leon.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas del Plan (2025) (RD 822/2021, el que admite nuevo ingreso; la página lista también el Plan (2010) con 52 asignaturas y guías 2026-27 completas, que NO se usa). "
           f"ECTS por carácter {json.dumps(s)}: formación básica {s['formacion_basica']:g} (RUCT 60: una básica de 2.º cuenta 6 ECTS más), obligatorias {s['obligatoria']:g} (RUCT 132), "
           f"optativas ofertadas {s['optativa']:g} (RUCT 36). El Trabajo fin de grado (12 ECTS) NO aparece en la tabla del Plan (2025). Básica+obligatoria = 192 = RUCT 60+132. "
           f"{len(sin)} asignaturas de 3.º-4.º del Plan (2025) no tienen guía 2026-27 publicada (sin_guia). Centro único."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(http.stats)
