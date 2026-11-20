"""Fase 1 - Staffordshire University (UK STAFFOR02) - BEng (Hons) Electrical and Electronic Engineering (pathway Electrical).
Fuente: ficha de curso www.staffs.ac.uk/course/electrical-electronic-engineering-beng (HTML; tablas de modulos + modales con descripcion).
Uso (desde la raiz): python universidades/ec_uk_staffor02/discover_ec_uk_staffor02.py
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
SLUG = "ec_uk_staffor02"
UNIVERSIDAD = "Staffordshire University"
GRADO = "BEng (Hons) Electrical and Electronic Engineering (pathway Electrical)"
URL = "https://www.staffs.ac.uk/course/electrical-electronic-engineering-beng"
PATHWAY_ID = "pathway-beng-hons-full-time-electrical-and-electronic-engineering-with-electrical"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL), "lxml")
    sec = soup.find("section", id=PATHWAY_ID)
    modals = {m["data-modal"]: m for m in soup.select("div.modal[data-modal]")}
    rows, seen = [], set()
    for tb in sec.select("table.table--modules"):
        cap = tb.find("caption").get_text(" ", strip=True)
        my = re.search(r"Year (\d)\s+(compulsory|optional)", cap, re.I)
        year, tipo = int(my.group(1)), my.group(2).lower()
        for tr in tb.select("tbody tr"):
            a = tr.find("a", attrs={"data-modal-trigger": True})
            if not a:
                continue
            slug = a["data-modal-trigger"]
            nombre = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
            cred = float(re.search(r"(\d+)", tr.select_one(".table--modules__credits").get_text()).group(1))
            mc = re.search(r"Module code:\s*([A-Z]{3,5}\d{4,6})", modals[slug].get_text(" ", strip=True)) if slug in modals else None
            code = mc.group(1) if mc else slug
            if code in seen:
                continue
            seen.add(code)
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=f"Year {year} ({tipo})", curso=year, semestre=None, creditos_ects=cred / 2,
                caracter="tfg" if "project" in nombre.lower() and year == 3 else ("obligatoria" if tipo == "compulsory" else "optativa"),
                idioma_pagina="en", url_guia_docente=f"{URL}#modal={slug}", tipo_fuente="html"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2026-2027",
        url_plan_estudios=URL, ects_totales_plan=180.0,
        estrategia_fuente="HTML estatico de la ficha del curso: tablas por año y modales con la descripcion de cada modulo",
        generado_por="discover_ec_uk_staffor02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: BEng (Hons) Electrical and Electronic Engineering, itinerario 'with Electrical' (el Excel pide Grado en "
               "Ingeniería Eléctrica y Electrónica Industrial y Automática; Staffordshire no ofrece Mecánica en esos acuerdos, los otros dos son másteres). "
               "Se cataloga solo el itinerario Electrical (años 1-3; el itinerario Electronic & Telecommunications comparte año 1). "
               "Código = 'Module code' del modal. Créditos UK 120/año → ECTS = créditos/2 (20 UK = 10 ECTS). "
               "Sin ficha oficial por módulo en abierto: solo la descripción corta del modal (sin resultados de aprendizaje ni evaluación). "
               f"Suma ECTS={total:g} (el plan son 180 ECTS: la web solo lista 100 créditos UK en el año 2, faltan 10 ECTS que la fuente no publica; el año de prácticas opcional no se cataloga)."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(rows), "asignaturas; ECTS", total, [(r.curso, r.nombre_asignatura) for r in rows][:30])


if __name__ == "__main__":
    main()
