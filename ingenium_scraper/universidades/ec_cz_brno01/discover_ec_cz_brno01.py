"""Fase 1 - Brno University of Technology (VUT), Faculty of Mechanical Engineering (FSI).
Grado: Fundamentals of Mechanical Engineering (B-STI-A), bachelor, 3 años, en inglés.
Fuente: ficha del programa en www.fme.vutbr.cz (HTML estático, una tabla por curso/semestre).
Uso: python universidades/ec_cz_brno01/discover_ec_cz_brno01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_cz_brno01"
UNIVERSIDAD = "Brno University of Technology (VUT) - Faculty of Mechanical Engineering"
GRADO = "Fundamentals of Mechanical Engineering (B-STI-A)"
URL_PLAN = "https://www.fme.vutbr.cz/en/studenti/programy/program/9646"
CARACTER = {"compulsory": "obligatoria", "compulsory-optional": "optativa", "elective": "optativa"}


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    entries, seen = [], set()
    for t in s.find_all("table"):
        cap = t.find("caption")
        m = re.match(r"(\d)\. year of study, (winter|summer) semester", cap.get_text(" ", strip=True)) if cap else None
        if not m:
            continue
        year, sem = int(m.group(1)), m.group(2)
        for tr in t.select("tbody tr"):
            tds = tr.find_all("td")
            a = tds[1].find("a") if len(tds) > 4 else None
            if not a:
                continue
            code = tds[0].get_text(strip=True)
            if (code, year, sem) in seen:
                continue
            seen.add((code, year, sem))
            com = tds[4].get_text(strip=True)
            caracter = CARACTER.get(com.lower(), com.lower())
            name = a.get_text(" ", strip=True)
            if re.search(r"thesis|bachelor(.s)? project", name, re.I):
                caracter = "tfg"
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=f"Curso {year} / {'winter' if sem == 'winter' else 'summer'} semester", curso=year,
                semestre=(year - 1) * 2 + (1 if sem == "winter" else 2),
                creditos_ects=float(tds[3].get_text(strip=True)), caracter=caracter,
                idioma_pagina=tds[2].get_text(strip=True) or "en",
                url_guia_docente=urljoin(URL_PLAN, a["href"]), tipo_fuente="html"))
    codes = [e.codigo_asignatura for e in entries]
    dup = {k for k in codes if codes.count(k) > 1}
    by_com = {}
    for e in entries:
        by_com[e.caracter] = by_com.get(e.caracter, 0) + (e.creditos_ects or 0)
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/2027", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0, estrategia_fuente="HTML estático de la ficha del programa (tablas 'N. year of study, winter/summer semester') + ficha HTML por asignatura",
        generado_por="discover_ec_cz_brno01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Titulación: Fundamentals of Mechanical Engineering (B-STI-A), Bc., 3 años, docencia en inglés, FSI VUT Brno; es el grado en inglés más "
               f"cercano a Ingeniería Mecánica (Mechanical Engineering en inglés es solo máster N-ENG-A; B-KSI-P Mechanical Engineering Design y Mechatronics "
               f"existen solo en checo). Se cubren los 3 cursos. Suma de ECTS de todas las filas: {tot:g} (por tipo: {by_com}); las obligatorias suman 167 y "
               f"el resto hasta 180 sale de las optativas ofertadas (se ofrecen 50 ECTS, por eso la suma total excede 180). Códigos duplicados: {sorted(dup) or 'ninguno'}."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS", tot, by_com, "dup", dup)


if __name__ == "__main__":
    main()
