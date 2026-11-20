#!/usr/bin/env python3
"""Fase 2 — UNED: PDF «Guía de estudio pública» por asignatura -> Markdown.
Se parte del cuerpo tras el índice; apartados principales en mayúsculas y en orden fijo; se descartan EQUIPO DOCENTE, HORARIO DE ATENCIÓN y
TUTORIZACIÓN EN CENTROS ASOCIADOS (nombres, correos, teléfonos). Uso: python universidades/es_nacional_educacion_a_distanc/scraper_es_nacional_educacion_a_distanc.py [--sample N | --all | --codes C...]"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "es_nacional_educacion_a_distanc"
SAMPLE = ["68031029", "68031087", "68033028", "68034163", "68023024"]
MAIN = ["PRESENTACIÓN Y CONTEXTUALIZACIÓN", "REQUISITOS Y/O RECOMENDACIONES PARA CURSAR LA ASIGNATURA", "EQUIPO DOCENTE", "HORARIO DE ATENCIÓN AL ESTUDIANTE",
        "TUTORIZACIÓN EN CENTROS ASOCIADOS", "COMPETENCIAS QUE ADQUIERE EL ESTUDIANTE", "RESULTADOS DE APRENDIZAJE", "CONTENIDOS", "METODOLOGÍA",
        "SISTEMA DE EVALUACIÓN", "BIBLIOGRAFÍA BÁSICA", "BIBLIOGRAFÍA COMPLEMENTARIA", "RECURSOS DE APOYO Y WEBGRAFÍA", "PRÁCTICAS DE LABORATORIO", "IGUALDAD DE GÉNERO"]
DROP = {"EQUIPO DOCENTE", "HORARIO DE ATENCIÓN AL ESTUDIANTE", "TUTORIZACIÓN EN CENTROS ASOCIADOS"}


def scrape_course(http, e):
    with pdfplumber.open(http.get_file(e["url_guia_docente"])) as d:
        txt = "\n".join((p.extract_text() or "") for p in d.pages)
    txt = re.sub(r"\(cid:\d+\)", "", txt)
    i = txt.find("NOMBRE DE LA ASIGNATURA")
    if i < 0:
        raise RuntimeError("no se encontró el cuerpo de la guía")
    lines = [l for l in txt[i:].split("\n") if not re.match(r"^UNED \d+ CURSO", l) and not re.search(r"CÓDIGO \d{7,8}-?$", l) and l.strip()]
    # unir encabezado partido en dos líneas
    j = 0
    while j < len(lines) - 1:
        if lines[j] == "REQUISITOS Y/O RECOMENDACIONES PARA CURSAR LA" and lines[j + 1] == "ASIGNATURA":
            lines[j:j + 2] = ["REQUISITOS Y/O RECOMENDACIONES PARA CURSAR LA ASIGNATURA"]
        j += 1
    head, secs, cur, pos = [], {}, None, -1
    for l in lines:
        if l in MAIN and MAIN.index(l) > pos:
            pos = MAIN.index(l)
            cur = l
            secs[cur] = []
            continue
        (secs[cur] if cur else head).append(l)
    if "CONTENIDOS" not in secs:
        raise RuntimeError("guía sin apartado CONTENIDOS")
    meta_lines = [l for l in head if re.match(r"(CURSO ACADÉMICO|DEPARTAMENTO|TÍTULO|Nº ET?CS|HORAS|IDIOMAS|- )", l)]
    md = [f"# {e['nombre_asignatura']} ({e['codigo_asignatura']})", "", f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Fuente: {e['url_guia_docente']}", "", "## Datos generales", "", "\n".join(meta_lines), ""]
    for k in MAIN:
        if k in secs and k not in DROP and "\n".join(secs[k]).strip():
            md += [f"## {k.capitalize()}", "", "\n".join(secs[k]).strip(), ""]
    g = lambda k: len("\n".join(secs.get(k, [])).strip())  # noqa: E731
    blocks = dict(contents=g("CONTENIDOS") > 20, learning_outcomes=g("RESULTADOS DE APRENDIZAJE") > 20 or g("COMPETENCIAS QUE ADQUIERE EL ESTUDIANTE") > 20,
                  assessment=g("SISTEMA DE EVALUACIÓN") > 20, bibliography=g("BIBLIOGRAFÍA BÁSICA") + g("BIBLIOGRAFÍA COMPLEMENTARIA") > 20,
                  prerequisites=g("REQUISITOS Y/O RECOMENDACIONES PARA CURSAR LA ASIGNATURA") > 20)
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    codes = list(rows) if a.all else (a.codes or [c for c in SAMPLE if c in rows][: a.sample or 5])
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = 0
    for c in codes:
        e = rows.get(c)
        try:
            p, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} ({p.stat().st_size} B)" + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
