"""Fase 1 - University of Pardubice (CZ PARDUB01) - Faculty of Electrical Engineering and Informatics, Bachelor's Degree Program (courses in English).
Fuente: «List of courses for Erasmus+/Exchange students (ECTS Catalogue)» de www.upce.cz (HTML, robots permite), tabla «Bachelor's Degree Program»;
cada fila enlaza la ficha de IS/STAG (portal.upce.cz, sin robots.txt).
Uso (desde la raiz): python universidades/ec_cz_pardub01/discover_ec_cz_pardub01.py
"""
from __future__ import annotations

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
SLUG = "ec_cz_pardub01"
UNIVERSIDAD = "University of Pardubice (Univerzita Pardubice)"
GRADO = "Bachelor's programme, Faculty of Electrical Engineering and Informatics - courses in English"
URL = "https://www.upce.cz/en/study/exchange-programmes/ects-catalogue/courses-eletrical-faculty.html"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL), "lxml")
    table = None
    for t in soup.find_all("table"):
        pre = t.find_previous(["h2", "h3", "h4", "strong", "p"])
        if pre and "Bachelor" in pre.get_text():
            table = t
            break
    assert table is not None, "tabla Bachelor no encontrada"
    rows, seen = [], set()
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        a = tr.find("a", href=True)
        if len(tds) < 5 or not a:
            continue
        nombre = re.sub(r"\s+", " ", tds[0].get_text(" ", strip=True))
        code = re.sub(r"\s+", "", tds[1].get_text(strip=True))
        if code in seen:
            continue
        seen.add(code)
        ects = re.search(r"[\d.]+", tds[2].get_text())
        sem = re.sub(r"\s+", " ", tds[3].get_text(" ", strip=True))
        lang = tds[4].get_text(strip=True)
        rows.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
            curso_semestre=f"Offered: {sem}", curso=None, semestre=None, creditos_ects=float(ects.group(0)) if ects else None,
            caracter="tfg" if re.search(r"bachelor.?s? (thesis|project)|diploma", nombre, re.I) else "optativa",
            idioma_pagina="en" if lang.lower().startswith("english") else "cs", url_guia_docente=a["href"], tipo_fuente="html"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2026-2027",
        url_plan_estudios=URL, ects_totales_plan=None,
        estrategia_fuente="Catálogo ECTS de intercambio (HTML estático) + ficha IS/STAG por asignatura (HTML, versión inglesa)",
        generado_por="discover_ec_cz_pardub01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: grado (Bachelor's) de la Facultad de Ingeniería Eléctrica e Informática (FEI): el Excel de Pardubice solo tiene "
               "Electrónica Industrial y Automática, Informática en Tecnologías de la Información, Telecomunicación y Doble Grado Teleco+Datos; la FEI "
               "(Electrical Engineering and Informatics) es la afín a EIA, que es la titulación con más plazas (2). "
               "Fuente = lista oficial de cursos en inglés para estudiantes de intercambio (nivel Bachelor), NO el plan de estudios del grado "
               "(el portal STAG público solo tiene los programas checos); por eso es una oferta de cursos sueltos, sin curso/semestre del plan ni total de ECTS "
               f"del grado ('parcial'). Código = abreviatura STAG 'KATEDRA/CODIGO'. Suma ECTS={total:g}."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(len(rows), "asignaturas; ECTS", total)


if __name__ == "__main__":
    main()
