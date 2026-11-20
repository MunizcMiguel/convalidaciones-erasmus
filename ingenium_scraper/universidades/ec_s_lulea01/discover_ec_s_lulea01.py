"""Fase 1 (parcial) - Lulea University of Technology (LTU) - Hogskoleingenjor maskinteknik (BSc in Engineering, Mechanical Engineering; 180 hp, 3 anos).
Fuente: pagina del programa en www.ltu.se (HTML estatico; las listas de cursos van en <dialog> por bloque tematico, sin curso/semestre).
Las guias (kursplan) las sirve epok.ltu.se (PDF dinamico), cuyo robots.txt las prohibe -> regla de parada: filas sin_guia, sin Fase 2.
Uso: python universidades/ec_s_lulea01/discover_ec_s_lulea01.py
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
SLUG = "ec_s_lulea01"
URL = "https://www.ltu.se/utbildning/program/timeg-hogskoleingenjor-maskinteknik"
SYLL_HOST = "https://epok.ltu.se/epok/dynpdf/public/kursplan/downloadPublicKursplan.pdf"
GRADO = "Högskoleingenjör maskinteknik (BSc in Engineering, Mechanical Engineering, 180 hp)"
UNIV = "Luleå tekniska universitet (Luleå University of Technology)"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL), "lxml")
    entries, seen = [], set()
    for a in s.find_all("a", href=re.compile(r"^/utbildning/kurs/[a-z0-9]+/([a-z0-9]+)-")):
        m = re.match(r"^/utbildning/kurs/[a-z0-9]+/([a-z]\d{4}[a-z])-", a["href"])
        t = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        h = re.match(r"^(.*?)\s+(\d+(?:[.,]\d+)?) hp$", t)
        if not m or not h:
            continue
        code = m.group(1).upper()
        if code in seen:
            continue
        seen.add(code)
        name = h.group(1)
        entries.append(CatalogEntry(
            universidad=UNIV, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name, curso_semestre="n/d (la página del programa agrupa por bloque temático)",
            curso=None, semestre=None, creditos_ects=float(h.group(2).replace(",", ".")), caracter="tfg" if name.lower().startswith("examensarbete") else None,
            idioma_pagina="sv", url_guia_docente=None, tipo_fuente="sin_guia"))
    # comprobar el veredicto de robots del host de las guías
    rules = c._rules_for("https://epok.ltu.se")
    permitido = rules.can_fetch(SYLL_HOST + "?kursKod=M0015T&lasPeriod=227&locale=en")
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIV, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/2027", url_plan_estudios=URL, ects_totales_plan=180.0,
        estrategia_fuente="HTML estático de la página del programa en ltu.se (enlaces a cursos con 'N hp')", generado_por="discover_ec_s_lulea01.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Högskoleingenjör maskinteknik (3 años, 180 hp = 180 ECTS), grado equivalente a Ing. Mecánica (la civilingenjör maskinteknik, TCMAA, es de 5 años y 300 hp). "
               f"{len(entries)} cursos enlazados en la página del programa, suma {tot:g} hp (incluye cursos optativos/alternativos de los bloques; curso/semestre no se publican ahí). "
               f"Plan de estudios y kursplan: la guía (objetivos, contenido, evaluación) solo se sirve como PDF dinámico desde epok.ltu.se; robots.txt de ese host {'permite' if permitido else 'PROHÍBE'} la ruta "
               "/epok/dynpdf/public/kursplan/ → regla de parada: filas sin_guia, sin Fase 2. La ficha de curso en www.ltu.se (/edu/course/{ID}?l=en, en inglés) solo tiene datos de matrícula y prerrequisitos. "
               "Fichas del bloque 'Valfria kurser' no listadas con enlace: no verificado."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "cursos; hp", tot, "epok permitido:", permitido)


if __name__ == "__main__":
    main()
