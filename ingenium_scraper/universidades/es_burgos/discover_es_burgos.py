#!/usr/bin/env python3
"""Fase 1 — Universidad de Burgos, Grado en Ingeniería Mecánica (Escuela Politécnica Superior).

Fuente: página "Guías docentes" del grado en www.ubu.es: 4 tablas (una por curso; la última incluye optativas y TFG)
con código, nombre ES/EN, ECTS, tipo y semestre; el código enlaza a la guía PDF servida por ubuvirtual.ubu.es
(`get_guiadocente.php?asignatura={codigo}&cursoacademico=2026`).
Uso: python universidades/es_burgos/discover_es_burgos.py
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
SLUG, UNI = "es_burgos", "Universidad de Burgos"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.ubu.es/grado-en-ingenieria-mecanica/informacion-basica/guias-docentes"
RUCT = {"basica": 66, "obligatorios": 144, "optativos": 12, "tfg": 18, "total": 240}
CAR = {"básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries = []
for ti, table in enumerate(soup.find_all("table"), start=1):
    heads = [th.get_text(" ", strip=True) for th in table.find_all("th")]
    if not heads or not heads[0].startswith("C"):
        continue
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) != 5:
            continue
        a = tds[0].find("a", href=re.compile("get_guiadocente"))
        code = tds[0].get_text(strip=True)
        nombre = tds[1].get_text("\n", strip=True).split("\n")[0].strip()
        tipo = re.sub(r"\s*\(.*\)", "", tds[3].get_text(strip=True)).lower()
        sem_txt = tds[4].get_text(strip=True)
        m = re.match(r"(\d)", sem_txt)
        sem_rel = int(m.group(1)) if m else None
        caracter = "tfg" if nombre.lower().startswith("trabajo fin de grado") else CAR[tipo]
        if caracter == "optativa" and nombre.lower().startswith("prácticas en empresa"):
            caracter = "optativa"
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
            curso_semestre=f"Curso {ti} / Semestre {sem_txt}" if sem_rel else f"Curso {ti} / anual-sin semestre",
            curso=ti, semestre=(ti - 1) * 2 + sem_rel if sem_rel else None,
            creditos_ects=float(tds[2].get_text(strip=True).replace(",", ".")), caracter=caracter, idioma_pagina="es",
            url_guia_docente=a["href"] if a else None, tipo_fuente="pdf" if a else "sin_guia"))

assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
sin = [e.codigo_asignatura for e in entries if not e.url_guia_docente]
assert s["formacion_basica"] == RUCT["basica"] and s["obligatoria"] == RUCT["obligatorios"] and s["tfg"] == RUCT["tfg"], s
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL,
    ects_totales_plan=240.0,
    estrategia_fuente="HTML estático de ubu.es (tablas por curso en la página Guías docentes); guía = PDF por asignatura en ubuvirtual.ubu.es.",
    generado_por="discover_es_burgos.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"Centro único: Escuela Politécnica Superior (el mismo grado tiene doble grado con Electrónica Industrial, no incluido). "
           f"{len(entries)} asignaturas. ECTS por carácter {json.dumps(s)}: básica {s['formacion_basica']:g}, obligatorias "
           f"{s['obligatoria']:g} y TFG {s['tfg']:g} coinciden con el RUCT (66/144/18); se ofertan {s['optativa']:g} ECTS optativos y "
           f"se cursan 12 (RUCT 12). Total cursado 66+144+12+18=240. Optativas colocadas en curso 4 (así las agrupa la tabla). "
           f"Sin guía: {', '.join(sin) or 'ninguna'}."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, "sin guía:", sin, http.stats)
