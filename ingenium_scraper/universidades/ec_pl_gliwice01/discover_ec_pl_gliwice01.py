"""Fase 1 - Silesian University of Technology (PL GLIWICE01) - Industrial and Engineering Chemistry (bachelor, Faculty of Chemistry).
Fuente: listados «Erasmus_Eng_Sylabus» (invierno p=111528 / verano p=111550) de www.polsl.pl/rch (HTML estatico, robots permite).
Cada ficha: nombre, codigo, tipo (Bachelor), categoria y ECTS; el PDF del silabo esta en euslugi.polsl.pl, cuyo robots.txt
NO permite el acceso automatizado -> regla de parada: catalogo parcial, sin Fase 2.
Uso (desde la raiz): python universidades/ec_pl_gliwice01/discover_ec_pl_gliwice01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_gliwice01"
UNIVERSIDAD = "Silesian University of Technology (Politechnika Śląska)"
GRADO = "Industrial and Engineering Chemistry (Makro), Bachelor, Faculty of Chemistry"
PAGES = {"winter": "https://www.polsl.pl/rch/?p=111528", "summer": "https://www.polsl.pl/rch/?p=111550"}
CATEGORIA = "Industrial and Engineering Chemistry"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    rows, seen, cats = [], set(), Counter()
    for term, url in PAGES.items():
        soup = BeautifulSoup(http.get_text(url), "lxml")
        for d in soup.select("div.mn-document-download"):
            name_raw = d.select_one(".mn-document-name").get_text("\n", strip=True).split("\n")
            nombre = re.sub(r"\s+", " ", name_raw[0]).strip()
            code = re.sub(r"\s+", "", name_raw[-1]).replace(">", "_") if len(name_raw) > 1 else ""
            desc = d.select_one(".mn-document-desc").get_text("\n", strip=True)
            tipo = re.search(r"Type - (.+)", desc)
            cat = re.search(r"Subject category - (.+)", desc)
            ects = re.search(r"ECTS - ([\d.,]+)", desc)
            a = d.find("a", href=True)
            cats[(tipo.group(1).strip() if tipo else "?", cat.group(1).strip() if cat else "?")] += 1
            if not (tipo and "Bachelor" in tipo.group(1) and cat and CATEGORIA in cat.group(1)):
                continue
            if not code or code in seen:
                continue
            seen.add(code)
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=f"{term.capitalize()} term (curso no indicado)", curso=None, semestre=None,
                creditos_ects=float(ects.group(1).replace(",", ".")) if ects else None, caracter=None,
                idioma_pagina="en", url_guia_docente=a["href"], tipo_fuente="pdf"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2025-2026",
        url_plan_estudios=PAGES["winter"], ects_totales_plan=None,
        estrategia_fuente="HTML estatico de los listados Erasmus de la Facultad de Química (nombre, código, ECTS) + PDF por asignatura en euslugi.polsl.pl (robots lo veta)",
        generado_por="discover_ec_pl_gliwice01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: Industrial and Engineering Chemistry (Makro), bachelor en inglés de la Facultad de Química; es la equivalente de "
               "'Grado en Ingeniería Química Industrial' (3 de las 5 filas del Excel; el resto son Informática/Telecomunicación). "
               "Las filas son los silabos Erasmus publicados en inglés; no hay plan de estudios por curso/semestre (solo término invierno/verano), "
               "de modo que curso y semestre son null y los ECTS totales del plan no son verificables. "
               "STOP RULE: los PDF de cada silabo viven en euslugi.polsl.pl cuyo robots.txt no permite el acceso automatizado (RobotsBlocked); "
               "no se descargan y no hay Fase 2. www.polsl.pl declara Crawl-delay 60. "
               f"Suma ECTS de las filas catalogadas={total:g}. Categorías vistas (tipo, categoría): {dict(cats)}"))
    cat_ = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat_.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(rows), "asignaturas; ECTS", total)
    print(cats)


if __name__ == "__main__":
    main()
