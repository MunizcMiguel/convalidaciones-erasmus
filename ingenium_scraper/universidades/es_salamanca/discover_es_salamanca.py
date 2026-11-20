#!/usr/bin/env python3
"""Fase 1 — Universidad de Salamanca, Grado en Ingeniería Mecánica (E.P.S. de Zamora; plan 2010, código UXXI 265).

Fuente: Guías académicas de la USAL (guias.usal.es). El nodo del título (`/node/250991`, «Curso 2026/2027») lista por curso las asignaturas
(`ul.asignatura-curso`: enlace al nodo, carácter y créditos); cada nodo de asignatura es la guía HTML (código UXXI, curso, periodicidad,
idioma en «1. Datos de la asignatura»). Hay además el plan (2026) [UXXI 410] (RD 822/2021, nodo 262751) que solo publica 1.º (9 asignaturas) y
dos centros más (E.T.S. Ingeniería Industrial de Béjar); se usa el plan 2010 de Zamora, el único con los 4 cursos publicados.
Uso: python universidades/es_salamanca/discover_es_salamanca.py
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
SLUG, UNI = "es_salamanca", "Universidad de Salamanca"
GRADO = "Grado en Ingeniería Mecánica"
O = "https://guias.usal.es"
TIT = O + "/node/250991"
CAR = {"BÁSICA": "formacion_basica", "OBLIGATORIA": "obligatoria", "OPTATIVA": "optativa", "PROYECTO FIN DE CARRERA": "tfg",
       "TRABAJO FIN DE GRADO": "tfg"}
RUCT = {"formacion_basica": 60, "obligatoria": 150, "tfg": 12}
CURSO = {"Primer": 1, "Segundo": 2, "Tercer": 3, "Cuarto": 4}


def datos(soup):
    """Pares etiqueta/valor de «1. Datos de la asignatura»."""
    h4 = soup.find("h4", string=re.compile(r"1\. Datos"))
    box = h4.parent.find_next_sibling("div", class_="datos-epigrafe-asig")
    L = box.get_text("\n", strip=True).split("\n")
    return {L[i]: L[i + 1] for i in range(0, len(L) - 1) if L[i] in ("Código", "Plan", "ECTS", "Carácter", "Curso", "Periodicidad", "Idioma")}


if __name__ == "__main__":
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(TIT), "lxml")
    entries = []
    for ul in soup.select("ul.asignatura-curso"):
        hh = ul.find_previous("h2").get_text(" ", strip=True)
        m = re.match(r"Asignaturas de (Primer|Segundo|Tercer|Cuarto) Curso", hh)
        if not m:
            continue
        curso = CURSO[m.group(1)]
        for li in ul.find_all("li"):
            a = li.find("a", href=re.compile(r"^/node/\d+"))
            mm = re.search(r"- ([A-ZÁÉÍÓÚÑ ]+?) - ([\d.]+) Créditos", li.get_text(" ", strip=True))
            g = BeautifulSoup(http.get_text(O + a["href"]), "lxml")
            d = datos(g)
            per = d.get("Periodicidad", "")
            sem = {"Primer Semestre": 1, "Segundo Semestre": 2}.get(per)
            entries.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=d["Código"], nombre_asignatura=a.get_text(" ", strip=True).capitalize(),
                curso_semestre=f"Curso {curso} / {per or 'sin periodicidad'}", curso=curso, semestre=(curso - 1) * 2 + sem if sem else None,
                creditos_ects=float(mm.group(2)), caracter=CAR[mm.group(1).strip()], idioma_pagina="es", url_guia_docente=O + a["href"], tipo_fuente="html"))
    assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
    s = {}
    for e in entries:
        s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
    print(len(entries), s)
    assert all(s[k] == v for k, v in RUCT.items()), s
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=TIT, ects_totales_plan=240.0,
        estrategia_fuente="HTML de guias.usal.es: nodo del título con listas por curso + guía HTML por asignatura (código, periodicidad, idioma en la sección 1).",
        generado_por="discover_es_salamanca.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"{len(entries)} asignaturas del plan 2010 [UXXI 265] en la E.P.S. de Zamora (primer centro del RUCT; el otro es la E.T.S. de Ingeniería Industrial de Béjar, nodo 247528). "
               f"El plan (2026) [UXXI 410] (RD 822/2021, el que admite nuevo ingreso; nodo 262751 en Zamora) solo publica 1.º (9 asignaturas), por lo que se usa el plan 2010, el único completo. "
               f"ECTS por carácter {json.dumps(s)}: básica 60, obligatorias 150 y TFG 12 = RUCT; se ofertan {s['optativa']:g} ECTS optativos (RUCT 18). "
               f"El TFG figura como «Proyecto fin de carrera». Optativas colocadas en 4.º (así las agrupa la guía)."),
    )
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(http.stats)
