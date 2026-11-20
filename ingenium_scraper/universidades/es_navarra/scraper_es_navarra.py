#!/usr/bin/env python3
"""Fase 2 — Universidad de Navarra: la ficha `asignatura.unav.edu/{id}/` devuelve un PDF «Guía docente 2026-27» -> Markdown.
Secciones en mayúsculas: PRESENTACIÓN, RESULTADOS DE APRENDIZAJE (un bloque por titulación; se conserva solo INGENIERÍA MECÁNICA), PROGRAMA,
ACTIVIDADES FORMATIVAS, METODOLOGÍAS DOCENTES, EVALUACIÓN, HORARIOS DE ATENCIÓN (se descarta), BIBLIOGRAFÍA. «Profesores de la asignatura» se descarta.
Uso: python universidades/es_navarra/scraper_es_navarra.py [--sample N | --all | --codes C...]"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "es_navarra"
SAMPLE = ["calculo-a", "fisicaing", "tfg-mec"]
MAIN = ["PRESENTACIÓN", "RESULTADOS DE APRENDIZAJE", "PROGRAMA", "CONTENTS OF THE COURSE", "ACTIVIDADES FORMATIVAS", "METODOLOGÍAS DOCENTES", "EVALUACIÓN",
        "HORARIOS DE ATENCIÓN", "BIBLIOGRAFÍA"]
DROP = {"HORARIOS DE ATENCIÓN"}


def scrape_course(http, e):
    with pdfplumber.open(http.get_file(e["url_guia_docente"])) as d:
        lines = "\n".join((p.extract_text() or "") for p in d.pages).split("\n")
    if not lines or not any(l.startswith("Guía docente") for l in lines[:3]):
        raise RuntimeError("no es una guía docente")
    head, secs, cur, pos = [], {}, None, -1
    skip_prof = False
    for l in lines:
        l = {"PROGRAMA DE LA ASIGNATURA": "PROGRAMA", "PROGRAM": "PROGRAMA", "INTRODUCTION": "PRESENTACIÓN", "ASSESSMENT": "EVALUACIÓN",
             "HORARIO DE ATENCIÓN": "HORARIOS DE ATENCIÓN"}.get(l, l)
        if l == "ORDINARY ASSESSMENT" and "EVALUACIÓN" not in secs:
            l = "EVALUACIÓN"
        if l in MAIN and l not in secs:
            pos = MAIN.index(l)
            cur = l
            secs[cur] = []
            skip_prof = False
            continue
        if l.startswith("Profesores de la asignatura"):
            skip_prof = True
            continue
        if skip_prof and cur is None or (skip_prof and cur == "PRESENTACIÓN" and not re.match(r"^[A-ZÁÉÍÓÚÑ ]{5,}$", l)):
            continue
        (secs[cur] if cur else head).append(l)
    if not any(k in secs for k in ("PROGRAMA", "CONTENTS OF THE COURSE", "RESULTADOS DE APRENDIZAJE", "EVALUACIÓN")):
        raise RuntimeError("guía sin programa ni resultados")
    # resultados: conservar solo el bloque de Ingeniería Mecánica
    ra, keep, any_deg = [], False, False
    for l in secs.get("RESULTADOS DE APRENDIZAJE", []):
        if re.fullmatch(r"INGENIERÍA [A-ZÁÉÍÓÚÑ ]+", l):
            any_deg = True
            keep = l == "INGENIERÍA MECÁNICA"
            continue
        if keep or not any_deg:
            ra.append(l)
    if "RESULTADOS DE APRENDIZAJE" in secs:
        secs["RESULTADOS DE APRENDIZAJE"] = ra
    # presentación: quitar lista de titulaciones salvo la de Mecánica
    pres, out, intit = secs.get("PRESENTACIÓN", []), [], False
    for l in pres:
        if l.startswith("Titulación (Módulo/Materia)"):
            intit = True
            continue
        if intit and l.endswith(":") and not l.startswith("Ingeniería"):
            intit = False
        if intit and not l.startswith("Ingeniería Mecánica") and re.match(r"^(Ingeniería|[A-ZÁÉÍÓÚÑa-záéíóúñ/ ]+\))", l) and "Mecánica" not in l:
            continue
        out.append(l)
    secs["PRESENTACIÓN"] = [l for l in out if not re.fullmatch(r"INGENIERÍA [A-ZÁÉÍÓÚÑ ]+", l)]  # titulaciones sueltas (guías sin resultados)
    title = head[0] if head else e["nombre_asignatura"]
    md = [f"# {title} ({e['codigo_asignatura']})", "", f"- Titulación: {e['nombre_grado']} · {e['universidad']}", f"- Fuente: {e['url_guia_docente']}", ""]
    for k in MAIN:
        if k in secs and k not in DROP and "\n".join(secs[k]).strip():
            md += [f"## {k.capitalize()}", "", "\n".join(secs[k]).strip(), ""]
    g = lambda k: len("\n".join(secs.get(k, [])).strip())  # noqa: E731
    pres_t = "\n".join(secs.get("PRESENTACIÓN", []))
    blocks = dict(contents=g("PROGRAMA") + g("CONTENTS OF THE COURSE") > 20, learning_outcomes=g("RESULTADOS DE APRENDIZAJE") > 20, assessment=g("EVALUACIÓN") > 20,
                  bibliography=g("BIBLIOGRAFÍA") > 20, prerequisites=bool(re.search(r"(?i)requisitos|conocimientos previos|prerrequisito", pres_t)))
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    extra = [c for c in rows if rows[c]["curso"] == 3][:1] + [c for c in rows if rows[c]["curso"] == 4][:1]
    codes = list(rows) if a.all else (a.codes or ([c for c in SAMPLE if c in rows] + extra)[: a.sample or 5])
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
