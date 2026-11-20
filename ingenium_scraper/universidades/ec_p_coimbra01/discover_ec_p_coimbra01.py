"""Fase 1 - Universidade de Coimbra (P COIMBRA01) - Licenciatura em Engenharia Eletrotecnica e de Computadores (LEEC, FCTUC).

Fuente: apps.uc.pt/courses (plan de estudos HTML estatico, id programa 8922, rama 21062).
Uso (desde la raiz):  python universidades/ec_p_coimbra01/discover_ec_p_coimbra01.py
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
SLUG = "ec_p_coimbra01"
UNIVERSIDAD = "Universidade de Coimbra"
GRADO = "Licenciatura em Engenharia Eletrotécnica e de Computadores (LEEC)"
AY = "2025-2026"
URL_PLAN = f"https://apps.uc.pt/courses/PT/programme/8922/{AY}?id_branch=21062"
ECTS_PLAN = 180.0
CARACTER = {"obrigat": "obligatoria", "opcion": "optativa", "optativ": "optativa"}


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    html = http.get_text(URL_PLAN)
    soup = BeautifulSoup(html, "lxml")
    rows = []
    seen = set()
    for tr in soup.select("table.sp-table tr"):
        tds = tr.find_all("td")
        a = tr.find("a", href=True)
        if len(tds) < 6 or not a:
            continue
        m_code = re.search(r"<!--\s*<td>\s*(\d+)\s*</td>\s*-->", str(tr))
        m_id = re.search(r"/unit/(\d+)/", a["href"])
        if not m_id:
            continue
        code = m_code.group(1) if m_code else f"UC{m_id.group(1)}"
        if code in seen:
            continue
        seen.add(code)
        nombre = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        curso = int(tds[1].get_text(strip=True))
        reg = tds[2].get_text(" ", strip=True)
        sm = re.match(r"(\d)", reg)
        semestre = (curso - 1) * 2 + int(sm.group(1)) if sm and "emestre" in reg else None
        tipo = tds[3].get_text(" ", strip=True).lower()
        car = next((v for k, v in CARACTER.items() if tipo.startswith(k)), tipo or None)
        ects = float(tds[5].get_text(strip=True))
        url = a["href"].replace("/courses/PT/unit/", "/courses/EN/unit/")
        rows.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
            curso_semestre=f"Ano {curso} / {reg}", curso=curso, semestre=semestre, creditos_ects=ects,
            caracter=car, idioma_pagina="en", url_guia_docente=url, tipo_fuente="html"))
    total = sum(r.creditos_ects or 0 for r in rows)
    oblig = sum(r.creditos_ects or 0 for r in rows if r.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico=AY,
        url_plan_estudios=URL_PLAN, ects_totales_plan=ECTS_PLAN,
        estrategia_fuente="HTML estatico de apps.uc.pt/courses: tabla sp-table del plan; ficha EN por unidad",
        generado_por="discover_ec_p_coimbra01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: LEEC (grado, 180 ECTS, FCTUC/DEEC) por ser la más afín a Electrónica Industrial y Automática "
               "y a Ingeniería Eléctrica (filas Uniovi: EIA 4 plazas, Eléctrica, Organización Industrial 2, Informática); no hay otro grado de ingeniería industrial en "
               "la UC. Código = código oficial UC (comentario HTML de la tabla). Fichas en inglés (la docencia es en portugués). "
               f"Suma ECTS listados={total:g} (obligatorias={oblig:g}; 9 optativas de 3.º, 6 ECTS cada una, de las que se eligen las necesarias hasta 180; TFG sustituido por Projeto I/II)."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    codes = [r.codigo_asignatura for r in rows]
    assert len(codes) == len(set(codes))
    print(f"{len(rows)} asignaturas; ECTS listados={total:g}; obligatorias={oblig:g}")


if __name__ == "__main__":
    main()
