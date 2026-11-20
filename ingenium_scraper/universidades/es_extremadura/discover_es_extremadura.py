#!/usr/bin/env python3
"""Fase 1 — Universidad de Extremadura, Grado en Ingeniería Mecánica (rama Industrial; Escuela de Ingenierías Industriales, Badajoz).

Fuente: ficha del título en eii.unex.es (WordPress): tablas "Curso 1..4" y "Asignaturas optativas" con nombre, carácter, ECTS y
semestre; cada nombre enlaza a `?subjectid={codigo}`, y la ficha de esa asignatura contiene el enlace "Plan docente" al PDF
(`plan0818-{codigo}-2026-27.pdf`, la carpeta de subida varía, por eso se lee de cada ficha).
Uso: python universidades/es_extremadura/discover_es_extremadura.py
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
SLUG, UNI = "es_extremadura", "Universidad de Extremadura"
GRADO = "Grado en Ingeniería Mecánica (Rama Industrial)"
URL = "https://eii.unex.es/titulaciones/0818/"
CAR = {"formación básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa",
       "trabajo de fin de grado": "tfg", "proyecto fin de grado": "tfg"}

def nice(n: str) -> str:
    if not n.isupper():
        return n
    small = {"DE", "DEL", "LA", "LAS", "LOS", "EL", "Y", "E", "EN", "A", "PARA", "POR", "CON"}
    w = n.lower().split()
    return " ".join(x if (i and x.upper() in small) else x.capitalize() for i, x in enumerate(w))


http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries, sin = [], []
for table in soup.find_all("table"):
    h = table.find_previous(["h2", "h3", "h4"])
    ht = h.get_text(" ", strip=True) if h else ""
    m = re.match(r"Curso (\d)", ht)
    if not m and not ht.startswith("Asignaturas optativas"):
        continue
    curso = int(m.group(1)) if m else 4
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        a = tr.find("a", href=re.compile(r"subjectid=\d+"))
        if len(tds) < 4 or not a:
            continue
        code = re.search(r"subjectid=(\d+)", a["href"]).group(1)
        nombre = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
        tipo = re.sub(r"\s+", " ", tds[1].get_text(" ", strip=True)).lower()
        sem_txt = re.sub(r"\s+", " ", tds[3].get_text(" ", strip=True)).strip()
        sm = re.match(r"(Primer|Segundo)", sem_txt, re.I)
        rel = 1 if sm and sm.group(1).lower() == "primer" else 2 if sm else None
        caracter = "tfg" if nombre.lower().startswith("proyecto fin de grado") else CAR[tipo]
        # ficha de la asignatura -> enlace "Plan docente"
        page = BeautifulSoup(http.get_text(f"{URL}?subjectid={code}"), "lxml")
        pa = next((x for x in page.find_all("a", href=True) if x.get_text(strip=True) == "Plan docente"), None)
        if pa is None:
            sin.append(code)
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nice(nombre),
            curso_semestre=f"Curso {curso} / {sem_txt}", curso=curso,
            semestre=(curso - 1) * 2 + rel if rel else None,
            creditos_ects=float(tds[2].get_text(strip=True).replace(",", ".")), caracter=caracter, idioma_pagina="es",
            url_guia_docente=pa["href"] if pa else None, tipo_fuente="pdf" if pa else "sin_guia"))

assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
assert s["formacion_basica"] == 66 and s["obligatoria"] == 138 and s["tfg"] == 12, s
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL,
    ects_totales_plan=240.0,
    estrategia_fuente="HTML de eii.unex.es (tablas por curso + optativas); guía = PDF 'Plan docente' enlazado en la ficha de cada asignatura.",
    generado_por="discover_es_extremadura.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"Centro: Escuela de Ingenierías Industriales (Badajoz). {len(entries)} asignaturas. ECTS ofertados {json.dumps(s)}: "
           f"básica 66, obligatorias 138 y TFG 12 coinciden con el RUCT; se ofertan {s['optativa']:g} ECTS optativos y se cursan 24 "
           f"(RUCT 24). Total cursado 66+138+24+12=240. Optativas en curso 4. Sin plan docente: {', '.join(sin) or 'ninguno'}."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, "sin guía:", sin, http.stats)
