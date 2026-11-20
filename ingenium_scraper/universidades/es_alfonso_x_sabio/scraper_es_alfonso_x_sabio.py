#!/usr/bin/env python3
"""Fase 2 — UAX: guías dentro del PDF compartido (rango de páginas del catálogo) -> Markdown.
Secciones numeradas 1 OBJETIVOS ... 8 SISTEMA Y CRITERIOS DE EVALUACIÓN, 9 BIBLIOGRAFÍA, 10 ADENDA. La portada lista PROFESORES (se descarta).
Uso: python universidades/es_alfonso_x_sabio/scraper_es_alfonso_x_sabio.py [--sample N | --all | --codes C...]"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "es_alfonso_x_sabio"
# Física(1º), Mecánica(2º), Teoría de Máquinas(3º), Biomecánica(optativa), Technical English, TFG
SAMPLE = ["0141812", "0241817", "0341811", "0341819", "0141817", "0341816"]
HEAD = re.compile(r"^(\d{1,2}) ([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ ,Y/]{4,})$")
KNOWN = {"OBJETIVOS", "REQUISITOS PREVIOS", "COMPETENCIAS", "RESULTADOS DE APRENDIZAJE", "DESCRIPCIÓN DE LOS CONTENIDOS", "ACTIVIDADES FORMATIVAS",
         "CRONOGRAMA", "SISTEMA Y CRITERIOS DE EVALUACIÓN", "BIBLIOGRAFÍA", "ADENDA"}


class GuideError(Exception):
    pass


def scrape_course(pdf, e):
    a, b = map(int, e["paginas_pdf"].split("-"))
    lines = []
    with pdfplumber.open(pdf) as d:
        for n in range(a, b + 1):
            t = d.pages[n - 1].extract_text() or ""
            ls = t.split("\n")
            if n == a:  # portada: nada tras PROFESORES (nombres)
                k = next((i for i, l in enumerate(ls) if l.startswith("PROFESORES")), len(ls))
                ls = ls[:k]
                continue_head = False
                ls = [l for l in ls if not l.startswith(("GRADO EN", "PLAN DE ESTUDIOS", "GUÍA DE LA ASIGNATURA"))]
                lines += ["@@COVER@@"] + ls + ["@@ENDCOVER@@"]
                continue
            ls = [l for l in ls if not re.fullmatch(r"- \d+ -|\d+", l.strip())]
            lines += ls
    cover, body, sec, secs, order = [], [], None, {}, []
    inc = False
    for l in lines:
        if l == "@@COVER@@":
            inc = True
            continue
        if l == "@@ENDCOVER@@":
            inc = False
            continue
        if inc:
            cover.append(l)
            continue
        m = HEAD.match(l)
        if m and m[2] in KNOWN:
            sec = m[2]
            order.append(sec)
            secs[sec] = []
            continue
        if sec:
            secs[sec].append(l)
    if "OBJETIVOS" not in secs:
        raise GuideError("no se localizó el apartado 1")
    md = [f"# {e['nombre_asignatura']} ({e['codigo_asignatura']})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/periodo: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']} (págs. {e['paginas_pdf']})", ""]
    for s in order:
        if s == "ADENDA":
            continue
        txt = "\n".join(secs[s]).strip()
        if s == "CRONOGRAMA":
            txt = re.sub(r"(?m)^Actividad Sesión Descripción Evaluación$", "", txt).strip()
        md += [f"## {s.capitalize()}", "", txt, ""]
    g = lambda k: len("\n".join(secs.get(k, [])).strip())  # noqa: E731
    pre = "\n".join(secs.get("REQUISITOS PREVIOS", [])).strip()
    blocks = dict(contents=g("DESCRIPCIÓN DE LOS CONTENIDOS") > 20, learning_outcomes=g("RESULTADOS DE APRENDIZAJE") > 20,
                  assessment=g("SISTEMA Y CRITERIOS DE EVALUACIÓN") > 20, bibliography=g("BIBLIOGRAFÍA") > 20,
                  prerequisites=len(pre) > 5 and not re.match(r"(?i)no se (han )?establecido|ninguno|no hay", pre))
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    codes = list(rows) if a.all else (a.codes or SAMPLE[: a.sample or 5])
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf = http.get_file(next(iter(rows.values()))["url_guia_docente"])
    ok = fail = 0
    for c in codes:
        e = rows.get(c)
        try:
            p, b = scrape_course(pdf, e)
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
