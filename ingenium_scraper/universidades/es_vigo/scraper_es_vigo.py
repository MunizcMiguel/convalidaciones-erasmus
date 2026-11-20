#!/usr/bin/env python3
"""Fase 2 — Universidad de Vigo: ficha Docnet (HTML con tablas anidadas) -> Markdown.
Se toma el texto desde «DATOS IDENTIFICATIVOS» hasta el pie; las tablas hoja se convierten en tablas Markdown; del bloque identificativo se eliminan
Coordinador/a, Correo-e, Profesorado y Web (nombres, correos). Uso: python universidades/es_vigo/scraper_es_vigo.py [--sample N | --all | --codes C...]"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "es_vigo"
SAMPLE = ["V12G380V01104", "V12G380V01402", "V12G380V01306", "V12G380V01933", "V12G380V01991"]
SECS = ["Descripción general", "Resultados de Formación y Aprendizaje", "Contenidos", "Planificación", "Metodología docente", "Atención personalizada",
        "Evaluación", "Bibliografía. Fuentes de información", "Recomendaciones"]
IDENT_DROP = ("Coordinador", "Correo-e", "Profesorado", "Web")
ALT = {"Descrición xeral": "Descripción general", "Contidos": "Contenidos", "Avaliación": "Evaluación"}


def tbl_md(t):
    rows = []
    for tr in t.find_all("tr"):
        cells = [re.sub(r"\s+", " ", c.get_text(" ", strip=True)).replace("|", "/") for c in tr.find_all(["td", "th"])]
        if any(cells):
            rows.append(cells)
    if len(rows) < 2 or max(len(r) for r in rows) < 2:
        return None
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n\n| " + " | ".join(rows[0]) + " |\n|" + "---|" * w + "\n" + "\n".join("| " + " | ".join(r) + " |" for r in rows[1:]) + "\n\n"


NAMES = {1: "Competencias (Resultados de Formación y Aprendizaje)", 2: "Resultados previstos en la materia", 3: "Contenidos", 4: "Planificación", 5: "Metodologías",
         6: "Atención personalizada", 7: "Evaluación", 8: "Fuentes de información (bibliografía)", 9: "Recomendaciones"}
LABELS = {"DATOS IDENTIFICATIVOS", "Resultados de Formación y Aprendizaje", "Resultados previstos en la materia", "Contenidos", "Planificación", "Metodologías",
          "Atención personalizada", "Evaluación", "Fuentes de información", "Recomendaciones"}


def page_lines(http, url):
    soup = BeautifulSoup(http.get_text(url), "lxml")
    for x in soup(["script", "style"]):
        x.decompose()
    for t in soup.find_all("table"):
        if t.find("table") or t.find("a", class_="seccio") or t.find("a", href=re.compile("idioma_assig=(gal|cast|eng)$")):
            continue
        md = tbl_md(t)
        if md:
            t.replace_with(soup.new_string(md))
    text = soup.get_text("\n")
    i = text.find("DATOS IDENTIFICATIVOS")
    if i < 0:
        raise RuntimeError("no es una ficha de asignatura")
    lines = [l.strip() for l in text[i:].split("\n") if l.strip()]
    end = next((k for k, l in enumerate(lines) if l in ("Universidad de Vigo", "Universidade de Vigo")), len(lines))
    lines = lines[:end]
    k = next((k for k, l in enumerate(lines) if l in LABELS and l != "DATOS IDENTIFICATIVOS"), None)
    if k is None:
        raise RuntimeError("menú de apartados no encontrado")
    while k < len(lines) and lines[k] in LABELS:
        k += 1
    return lines, k


def scrape_course(http, e):
    url = e["url_guia_docente"]
    lines, k = page_lines(http, url)
    ident = [l for l in lines[:next((j for j, l in enumerate(lines) if l in LABELS and l != "DATOS IDENTIFICATIVOS"), len(lines))] if l != "DATOS IDENTIFICATIVOS"]
    desc = lines[k:]
    keep, skip = [], False
    for l in ident:
        if l.startswith(IDENT_DROP):
            skip = True
            continue
        if skip and l in ("Web", "Descritores", "Descriptores", "Idioma", "Lengua Impartición", "Departamento", "Prerrequisitos"):
            skip = False
        if not skip:
            keep.append(l)
    md = [f"# {e['nombre_asignatura']} ({e['codigo_asignatura']})", "", f"- Titulación: {e['nombre_grado']} · {e['universidad']}", f"- Fuente: {url}", "",
          "## Datos identificativos", "", "\n".join(keep), "", "## Descripción general", "", "\n".join(desc), ""]
    secs = {}
    for n in range(1, 10):
        try:
            ls, kk = page_lines(http, url + f"&fitxa_apartat={n}")
        except Exception:  # noqa: BLE001
            continue
        body = "\n".join(ls[kk:]).strip()
        if body:
            secs[n] = body
            md += [f"## {NAMES[n]}", "", body, ""]
    if not secs:
        raise RuntimeError("ficha sin apartados")
    g = lambda n: len(secs.get(n, ""))  # noqa: E731
    blocks = dict(contents=g(3) > 15, learning_outcomes=g(2) + g(1) > 15, assessment=g(7) > 15, bibliography=g(8) > 15, prerequisites=g(9) > 15)
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
            print(f"ok     {c} {e['nombre_asignatura'][:40]} ({p.stat().st_size} B)" + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
