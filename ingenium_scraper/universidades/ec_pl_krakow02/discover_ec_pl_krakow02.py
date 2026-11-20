"""Fase 1 - AGH University of Krakow (PL KRAKOW02) - Electrical Engineering (Elektrotechnika), first-cycle (engineer), full-time.
Fuente: sylabusy.agh.edu.pl (HTML) - pagina del plan con 7 tablas semestrales; cada fila trae data-syllabus-id (UUID).
El codigo oficial ("Course code") se lee de la ficha /en/document/{uuid}.html.
Uso (desde la raiz): python universidades/ec_pl_krakow02/discover_ec_pl_krakow02.py
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
SLUG = "ec_pl_krakow02"
UNIVERSIDAD = "AGH University of Krakow"
GRADO = "Electrical Engineering (Elektrotechnika), First-cycle (engineer) programme"
BASE = "https://sylabusy.agh.edu.pl"
URL_PLAN = BASE + "/en/1/2/22/1/4/16/12"


def doc_url(uid: str) -> str:
    return f"{BASE}/en/document/{uid}.html"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL_PLAN), "lxml")
    rows, seen, sin_codigo = [], set(), 0
    for sem, tb in enumerate(soup.select("table"), start=1):
        for tr in tb.select("tbody tr"):
            btn = tr.select_one("[data-syllabus-id]")
            if not btn:
                continue
            tds = tr.find_all("td", recursive=False)
            uid = btn["data-syllabus-id"]
            if uid in seen:
                continue
            seen.add(uid)
            nombre = re.sub(r"\s+", " ", btn.get_text(" ", strip=True))
            ects_txt = tds[2].get_text(strip=True)
            ects = float(ects_txt) if re.fullmatch(r"\d+(\.\d+)?", ects_txt) else None
            mand = tds[4].get_text(strip=True).lower()
            doc = BeautifulSoup(http.get_text(doc_url(uid)), "lxml")
            lab = doc.find("dt", string=re.compile(r"^\s*Course code\s*$"))
            code = lab.find_next("dd").get_text(strip=True) if lab else None
            if not code:
                code, sin_codigo = uid, sin_codigo + 1
            tfg = bool(re.search(r"diploma|thesis", nombre, re.I))
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=f"Semester {sem} ({tds[4].get_text(strip=True)})", curso=(sem + 1) // 2, semestre=sem,
                creditos_ects=ects, caracter="tfg" if tfg else ("obligatoria" if mand.startswith("oblig") else "optativa"),
                idioma_pagina="pl", url_guia_docente=doc_url(uid), tipo_fuente="html"))
    # codigos duplicados (misma ficha en dos itinerarios): sufijo de semestre
    cnt: dict[str, int] = {}
    for r in rows:
        cnt[r.codigo_asignatura] = cnt.get(r.codigo_asignatura, 0) + 1
    for r in rows:
        if cnt[r.codigo_asignatura] > 1:
            r.codigo_asignatura = f"{r.codigo_asignatura}_s{r.semestre}"
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2026-2027",
        url_plan_estudios=URL_PLAN, ects_totales_plan=210.0,
        estrategia_fuente="HTML estatico de sylabusy.agh.edu.pl: tablas semestrales del plan + fichas /en/document/{uuid}.html",
        generado_por="discover_ec_pl_krakow02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Electrical Engineering (Elektrotechnika), 1.er ciclo 'engineer' (7 semestres, 210 ECTS), facultad WEAIiIB: "
               "el Excel de AGH solo pide Electrónica Industrial y Automática (grado) y Máster en Ing. Industrial; la afín de primer ciclo con más "
               "contenido de Eléctrica/Electrónica es Electrical Engineering (Automatic Control and Robotics es la alternativa más cercana a EIA). "
               "Nombres de asignatura en inglés, pero el cuerpo de las fichas está en polaco (idioma 'pl'). Código = 'Course code' oficial de la ficha. "
               "Se omiten filas sin ficha enlazada (Physical Education, bloques de humanidades y lengua extranjera, 0-2 ECTS). Los itinerarios/optativas "
               f"incluidos en el plan se catalogan todos, por lo que la suma puede superar 210. Suma ECTS catalogados={total:g}. Filas sin código oficial: {sin_codigo}."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(f"{len(rows)} asignaturas; ECTS={total:g}; sin codigo={sin_codigo}")


if __name__ == "__main__":
    main()
