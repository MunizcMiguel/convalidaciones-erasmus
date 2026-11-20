#!/usr/bin/env python3
"""Fase 2 — Universidad de Extremadura: "Plan docente" PDF (eii.unex.es/wp-content/uploads/...plan0818-{codigo}-2026-27.pdf) -> Markdown.

PDF con texto, pero con la fuente codificada: pdfplumber devuelve `(cid:NN)` donde NN+29 es el código del carácter real
(p. ej. (cid:68)(cid:71)(cid:82) = "ado"); se decodifican. Estructura (títulos exactos en una línea):
Identificación y características · Profesorado (se descarta) · Competencias (matriz rotada, ilegible: se descarta) ·
Contenidos (descripción breve) · Temario de la asignatura · Actividades formativas · Metodologías docentes (matriz de X, se descarta) ·
Resultados de aprendizaje · Sistemas de evaluación · Bibliografía (básica y complementaria) · Otros recursos.
Uso: python universidades/es_extremadura/scraper_es_extremadura.py [--sample N | --all | --codes C...]
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_extremadura"
# Física I (1º), Matemáticas I (1º), Resistencia de Materiales (2º), Diseño de Máquinas (3º), Proyecto Fin de Grado, Ing. de Vehículos (opt.), Prácticas en empresa
SAMPLE = ["501050", "501052", "501063", "501329", "501342", "501338", "502498"]

HEADS = [("ident", "Identificación y características de la asignatura"), ("comp", "Competencias"), ("cont", "Contenidos"),
         ("tema", "Temario de la asignatura"), ("act", "Actividades formativas"), ("met", "Metodologías docentes"),
         ("res", "Resultados de aprendizaje"), ("eval", "Sistemas de evaluación"),
         ("bib", "Bibliografía (básica y complementaria)"), ("otros", "Otros recursos y materiales docentes complementarios")]
TITLES = {"ident": "Identificación", "cont": "Contenidos", "tema": "Temario", "act": "Actividades formativas",
          "res": "Resultados de aprendizaje", "eval": "Sistemas de evaluación", "bib": "Bibliografía",
          "otros": "Otros recursos y materiales docentes"}
_CID = re.compile(r"\(cid:(\d+)\)")


class GuideError(Exception):
    pass


def decode(s: str) -> str:
    return _CID.sub(lambda m: chr(int(m.group(1)) + 29), s)


def get_lines(data: bytes) -> list[str]:
    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for pg in pdf.pages:
            for l in (pg.extract_text(x_tolerance=1.5) or "").split("\n"):
                l = decode(l).strip()
                if l and not re.fullmatch(r"\d{1,2}", l):  # número de página suelto
                    out.append(l)
    return out


def split(lines):
    secs, cur, nxt = {}, None, 0
    for l0 in lines:
        l = re.sub(r"(?<=[a-z)])\d{1,2}$", "", l0)  # n.º de página pegado al título
        for i in range(nxt, len(HEADS)):  # cada título se toma una vez y en orden
            k, h = HEADS[i]
            if re.sub(r"\s", "", l).startswith("Competencias") and k == "comp" and i == nxt:
                cur, nxt = k, i + 1
                secs[k] = []
                break
            if re.sub(r"\s", "", l) == re.sub(r"\s", "", h) and k != "comp":
                cur, nxt = k, i + 1
                secs[k] = []
                break
        else:
            if cur:
                secs[cur].append(l0)
    return secs


def ident_clean(lines: list[str]) -> list[str]:
    # fuera Profesorado/coordinación (nombres, despachos, correos)
    out, skip = [], False
    for l in lines:
        if re.match(r"^Profesor", l) or l.startswith("Nombre Despacho"):
            skip = True
        if re.match(r"^(Área de|conocimiento|Departamento)", l):
            skip = False
        if skip or l.startswith("coordinador") or l.startswith("(si hay más") or "@" in l:
            continue
        out.append(l)
    return out


def fmt(lines: list[str]) -> str:
    out = []
    for l in lines:
        if re.match(r"^[-•–]\s*", l):
            out.append("- " + re.sub(r"^[-•–]\s*", "", l))
        elif re.match(r"^(Denominación del tema \d+|Contenidos del tema \d+|Actividades prácticas|Criterios de evaluación|"
                      r"Actividades de evaluación|Descripción de las actividades de evaluación|Bibliografía Básica|"
                      r"Bibliografía Complementaria|Breve descripción del contenido)\s*:?$", l):
            out += ["", f"**{l.rstrip(':')}**", ""]
        else:
            out.append(l)
    return "\n".join(out).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    data = http.get_bytes(e["url_guia_docente"])
    if not data.startswith(b"%PDF"):
        raise GuideError("no es un PDF")
    lines = get_lines(data)
    secs = split(lines)
    if code not in "\n".join(secs.get("ident", [])):
        raise GuideError("el PDF no corresponde a la asignatura")
    if "tema" not in secs and "cont" not in secs:
        raise GuideError("sin contenidos ni temario")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    texts = {}
    for k in ("ident", "cont", "tema", "act", "res", "eval", "bib", "otros"):
        if k not in secs:
            continue
        ls = ident_clean(secs[k]) if k == "ident" else secs[k]
        body = fmt(ls)
        if not body:
            continue
        texts[k] = body
        md += [f"## {TITLES[k]}", "", body, ""]
    bl = {"contents": len(texts.get("tema", "")) + len(texts.get("cont", "")) > 40,
          "learning_outcomes": len(texts.get("res", "")) > 20,
          "assessment": len(texts.get("eval", "")) > 40,
          "bibliography": len(texts.get("bib", "")) > 60,
          "prerequisites": False}
    # requisitos: la plantilla no tiene apartado propio; sólo si el texto los menciona como encabezado
    bl["prerequisites"] = bool(re.search(r"(?im)^(requisitos|prerrequisitos|conocimientos previos)", "\n".join(texts.values())))
    return write_markdown(SLUG, e, "\n".join(md), bl), bl


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    if a.all:
        codes = [c for c, r in rows.items() if r["tipo_fuente"] != "sin_guia"]
    else:
        codes = a.codes or SAMPLE[: a.sample or 5]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = 0
    for c in codes:
        e = rows.get(c)
        if not e:
            print(f"FALLO {c}: no está en el catálogo")
            fail += 1
            continue
        try:
            p, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} ({p.stat().st_size} B)"
                  + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c} {e['nombre_asignatura']}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
