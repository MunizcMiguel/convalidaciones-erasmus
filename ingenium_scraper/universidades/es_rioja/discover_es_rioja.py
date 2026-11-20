#!/usr/bin/env python3
"""Fase 1 — Universidad de La Rioja, Grado en Ingeniería Mecánica (ETSII; título 803G).

Fuente: página «Curso 2026-2027» del grado en www.unirioja.es: una tabla por curso (Per., Tipo, código, nombre, ECTS) con enlace a la guía
HTML en aps.unirioja.es (`agetguiahtml?2026-27,803G,{codigo}`), más una tabla de optativas por itinerario (Cº, Per., código, nombre, ECTS).
Uso: python universidades/es_rioja/discover_es_rioja.py
"""
import json
import re
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

warnings.filterwarnings("ignore")
HERE = Path(__file__).parent
SLUG, UNI = "es_rioja", "Universidad de La Rioja"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.unirioja.es/grados-y-dobles-grados/grado-en-ingenieria-mecanica/curso-2026-2027/"
CAR = {"básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa", "practicas externas": "practicas",
       "trabajo fin de grado": "tfg", "trabajo de fin de grado": "tfg"}
RUCT = {"formacion_basica": 60, "obligatoria": 132 + 0, "practicas": 6, "tfg": 12}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries, seen = [], set()
for tb in soup.find_all("table"):
    rows = tb.find_all("tr")
    first = rows[0].get_text(" ", strip=True)
    m = re.match(r"Curso: (\d)", first)
    optativas = first.startswith("Cº")
    if not (m or optativas):
        continue
    curso_tabla = int(m.group(1)) if m else None
    for tr in rows:
        a = tr.find("a", href=re.compile(r"agetguiahtml"))
        if not a:
            continue
        td = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        code = a["href"].rsplit(",", 1)[-1]
        if optativas:
            curso, per, nombre, ects, tipo = int(td[0][0]), td[1], td[3], td[5], "optativa"
        else:
            curso, per, tipo, nombre, ects = curso_tabla, td[0], td[1].lower(), td[3], td[5]
        if code in seen:
            continue
        seen.add(code)
        car = CAR[tipo.lower()]
        sem = {"1S": 1, "2S": 2}.get(per)
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre, curso_semestre=f"Curso {curso} / {per}",
            curso=curso, semestre=(curso - 1) * 2 + sem if sem else None, creditos_ects=float(ects.replace(",", ".")), caracter=car, idioma_pagina="es",
            url_guia_docente=a["href"], tipo_fuente="html"))
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático de la página del curso en unirioja.es (tablas por curso + optativas por itinerario); guía HTML en aps.unirioja.es.",
    generado_por="discover_es_rioja.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas (centro único, ETSII). ECTS por carácter {json.dumps(s)}. RUCT: básica 60, obligatorias 132, optativas 30, prácticas 6, TFG 12. "
           f"Las optativas están agrupadas por itinerario (construcción sostenible / tecnologías de fabricación y máquinas / general), se cursan 30 ECTS de las ofertadas. "
           f"Básica, obligatorias, prácticas y TFG coinciden con el RUCT; se ofertan {s['optativa']:g} ECTS optativos (RUCT 30)."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(http.stats)
