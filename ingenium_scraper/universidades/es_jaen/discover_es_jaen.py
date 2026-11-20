#!/usr/bin/env python3
"""Fase 1 — Universidad de Jaén, Grado en Ingeniería Mecánica (Escuela Politécnica Superior de Jaén).

Fuente: página "Asignaturas y profesorado" del grado en eps.ujaen.es (HTML estático): una tabla por cuatrimestre y curso
(Código | Asignatura | Tipo | ECTS) y el listado de optativas (Código | Asignatura | Mención | ECTS); el nombre enlaza a la ficha
(PDF) en uvirtual.ujaen.es (`.../catalogofichasdocentesasignaturas/p/2026-27/4/134A/{codigo}/es/2026-27-{codigo}_es.html`).
Uso: python universidades/es_jaen/discover_es_jaen.py
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
SLUG, UNI = "es_jaen", "Universidad de Jaén"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://eps.ujaen.es/grados/grado-en-ingenieria-mecanica/asignaturas-y-profesorado"
CURSOS = {"primer": 1, "segundo": 2, "tercer": 3, "cuarto": 4}
CAR = {"FB": "formacion_basica", "OB": "obligatoria"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries, saltadas, dups = [], [], []
for table in soup.find_all("table"):
    h2 = table.find_previous("h2").get_text(" ", strip=True).lower()
    h3 = table.find_previous("h3").get_text(" ", strip=True).lower()
    optativas = h2.startswith("listado de optativas")
    curso = 4 if optativas else CURSOS[h2.split()[0]]
    cuat = 1 if h3.startswith("primer") else 2
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 4:
            continue
        code = tds[0].get_text(strip=True)
        a = tds[1].find("a", href=True)
        nombre = a.get_text(" ", strip=True) if a else re.sub(r"\(.*", "", tds[1].get_text(" ", strip=True)).strip()
        if not re.fullmatch(r"\d{8}", code):
            saltadas.append(f"{code} ({nombre})")  # huecos "Optativa n" sin asignatura concreta
            continue
        if code in {e.codigo_asignatura for e in entries}:
            dups.append(f"{code} ({nombre}, repetida en cuatrimestre {cuat})")
            continue
        extra = tds[2].get_text(" ", strip=True)
        if optativas:
            caracter, nota = "optativa", f" · {extra}"
        elif nombre.lower().startswith("trabajo fin de grado"):
            caracter, nota = "tfg", ""
        else:
            caracter, nota = CAR[extra], ""
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
            curso_semestre=f"Curso {curso} / Cuatrimestre {cuat}{nota}", curso=curso, semestre=(curso - 1) * 2 + cuat,
            creditos_ects=float(tds[3].get_text(strip=True).replace(",", ".")), caracter=caracter, idioma_pagina="es",
            url_guia_docente=a["href"] if a else None, tipo_fuente="pdf" if a else "sin_guia"))

s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
assert s["formacion_basica"] == 60 and s["obligatoria"] == 138 and s["tfg"] == 12, s
sin = [e.codigo_asignatura for e in entries if not e.url_guia_docente]
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL,
    ects_totales_plan=240.0,
    estrategia_fuente="HTML estático de eps.ujaen.es (tablas por curso/cuatrimestre + listado de optativas); guía = ficha en PDF en uvirtual.ujaen.es.",
    generado_por="discover_es_jaen.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"Centro: Escuela Politécnica Superior (Jaén), primero listado en el RUCT; el grado también se imparte en la EPS de Linares "
           f"(no incluida: oferta de optativas distinta). {len(entries)} asignaturas. ECTS ofertados {json.dumps(s)}: básica 60, "
           f"obligatorias 138 y TFG 12 coinciden con el RUCT; se ofertan {s['optativa']:g} "
           f"ECTS optativos en menciones y se cursan 30 (RUCT 30). Total 60+138+30+12=240. Prácticas externas (si figuran) son optativas "
           f"(RUCT: 0 de prácticas). Huecos de optativa sin asignatura concreta ignorados: {', '.join(saltadas) or 'ninguno'}. "
           f"Repetidas en la web (se toma la primera): {', '.join(dups) or 'ninguna'}. "
           f"Sin guía: {', '.join(sin) or 'ninguna'}."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, "saltadas:", saltadas, "sin guía:", sin, http.stats)
