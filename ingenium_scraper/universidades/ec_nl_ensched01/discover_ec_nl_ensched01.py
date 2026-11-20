"""Fase 1 - University of Twente - BSc Technical Computer Science (Computer Science & Engineering), curriculum 2025-26 (HTML estatico).
Las fichas de cada curso estan en el catalogo Osiris (SPA JavaScript, sin HTML) -> parcial, filas sin_guia, sin Fase 2.
Uso: python universidades/ec_nl_ensched01/discover_ec_nl_ensched01.py
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_nl_ensched01"
UNI = "University of Twente"
GRADO = "BSc Technical Computer Science (Computer Science & Engineering)"
URL_PLAN = "https://www.utwente.nl/en/tcs/education-programme/tcscurriculum-2/"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    for z in s(["script", "style", "nav", "header", "footer"]):
        z.decompose()
    lines = [l for l in s.get_text("\n", strip=True).split("\n") if l.strip()]
    phase, quart, entries, seen = None, None, [], set()
    i = 0
    mod_name = None
    while i < len(lines):
        l = lines[i]
        m = re.match(r"B(\d) phase", l)
        if m:
            phase = int(m.group(1))
        elif re.fullmatch(r"20\d{7}", l) and i + 1 < len(lines):
            code, name = l, lines[i + 1]
            j = i + 2
            ec = None
            if j < len(lines) and re.fullmatch(r"(\d+)\s*EC", lines[j]):
                ec = float(re.match(r"(\d+)", lines[j]).group(1)); j += 1
            if j < len(lines) and re.fullmatch(r"[1-4][AB]", lines[j]):
                quart = lines[j]; j += 1
            if ec is None:
                mod_name = name  # fila de modulo (15 EC) sin ECTS propios
            elif code not in seen:
                seen.add(code)
                curso = phase
                entries.append(CatalogEntry(
                    universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                    curso_semestre=f"B{phase} / {quart or ''} / {mod_name or ''}".strip(), curso=curso, semestre=None, creditos_ects=ec,
                    caracter="obligatoria", idioma_pagina="en", url_guia_docente=None, tipo_fuente="sin_guia"))
            i = j
            continue
        i += 1
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML estático de la tabla de currículo del programa (módulos de 15 EC y study units)",
        generado_por="discover_ec_nl_ensched01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Excel: Grado Ing. Informática en Tecnologías de la Información (1 plaza) y Doble Grado Informática+Datos, ISCED 0710; no hay Mecánica/Industrial, así que se toma "
               "el único grado de Informática de ingeniería de Twente más afín: BSc Technical Computer Science (diploma 'Computer Science & Engineering', 180 EC; la alternativa "
               "BSc Computer Science con Business IT es de perfil más de gestión). PARCIAL: la página del currículo solo da código, nombre, EC y cuartil de cada study unit; "
               "las fichas de contenido, resultados y evaluación están en el catálogo Osiris (utwente.osiris-student.nl), una SPA que no sirve HTML y para la que "
               "no se encontró un endpoint documentado; no se usa navegador ni se adivinan APIs. Filas 'sin_guia'. El currículo está organizado en módulos de 15 EC (el proyecto del "
               f"módulo se enseña con 3-4 study units); suma de las study units listadas: {tot:g} EC (el plan completo incluye electivas y minor/bachelor thesis sin listar aquí). "
               "robots.txt de www.utwente.nl permite el acceso."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas", tot)


if __name__ == "__main__":
    main()
