#!/usr/bin/env python3
"""Fase 2 — Nebrija: PDF bilingüe (ES/EN) por asignatura -> Markdown. Pág. 1 portada; datos generales + secciones numeradas '1. RESULTADOS...'.
Se elimina la línea «Profesor - Equipo docente» y su continuación. Uso: python universidades/es_antonio_nebrija/scraper_es_antonio_nebrija.py [--sample N | --all | --codes C...]"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "es_antonio_nebrija"
SAMPLE = ["calculo", "fisica-mecanica", "expresion-grafica-en-ingenieria", "fundamentos-de-programacion"]
FIELD = re.compile(r"^(Asignatura|Titulación|Carácter|Idioma|Modalidad|Número total|Curso|Semestre|Profesor)\b")


def scrape_course(http, e):
    pdf = http.get_file(e["url_guia_docente"])
    with pdfplumber.open(pdf) as d:
        pages = [(p.extract_text() or "") for p in d.pages[1:]]
    lines, skip = [], False
    for l in "\n".join(pages).split("\n"):
        if l.startswith("Profesor"):
            skip = True
            continue
        if skip:
            if FIELD.match(l) or re.match(r"^\d+\.\s", l) or l.startswith("GUÍA"):
                skip = False
            else:
                continue
        lines.append(l)
    text = "\n".join(lines).strip()
    text = re.sub(r"(?m)^(\d+(?:\.\d+)*\.)\s+(.+)$", lambda m: ("\n## " if m[1].count(".") == 1 else "\n### ") + m[0], text)
    if "RESULTADOS DE APRENDIZAJE" not in text.upper():
        raise RuntimeError("guía sin apartado de resultados de aprendizaje")
    md = f"# {e['nombre_asignatura']}\n\n- Titulación: {e['nombre_grado']} · {e['universidad']}\n- Fuente: {e['url_guia_docente']}\n- Nota: guía bilingüe ES/EN.\n\n{text}\n"
    up = text.upper()
    blocks = dict(contents="CONTENIDO" in up, learning_outcomes="RESULTADOS DE APRENDIZAJE" in up, assessment="EVALUACI" in up,
                  bibliography="BIBLIOGRAF" in up, prerequisites=bool(re.search(r"(?i)prerrequisito|requisitos previos|conocimientos previos", text)))
    return write_markdown(SLUG, e, md, blocks), blocks


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    codes = [c for c, r in rows.items() if r["tipo_fuente"] != "sin_guia"] if a.all else (a.codes or SAMPLE[: a.sample or 5])
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = 0
    for c in codes:
        e = rows.get(c)
        try:
            p, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} ({p.stat().st_size} B)" + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
