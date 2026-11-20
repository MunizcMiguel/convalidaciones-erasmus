#!/usr/bin/env python3
"""Fase 2 · Scraper — Universidad Politécnica de Madrid, Grado en Ingeniería Mecánica (plan 56IM, ETSIDI).

Cada guía es un PDF de GAUSS ("Guía de Aprendizaje", generado por el sistema, con texto):
    https://www.upm.es/comun_gauss/publico/guias/2026-27/GA_56IM_{codigo}_ES_2026-27.pdf
La URL exacta (2026-27 o 2025-26 si la nueva no está publicada) viene del catálogo.

Estructura del PDF (encabezados en mayúsculas, una línea):
  cabecera (código, créditos, COORDINADOR/A -> se descarta, REQUISITOS, CONOCIMIENTOS PREVIOS)
  RESULTADOS · DESCRIPCIÓN · TEMARIO · ACTIVIDADES (rejilla semanal) · CRITERIOS DE EVALUACIÓN ·
  RECURSOS · OTRA INFORMACIÓN · OBJETIVOS DE DESARROLLO SOSTENIBLE
Cada página lleva cabecera "G.A. NOMBRE" y pie con firma electrónica (se quitan).
De la rejilla de ACTIVIDADES se descartan los números de semana y las cabeceras repetidas;
se conservan nombre de actividad, presencialidad/duración, ponderación y nota mínima.

Uso (desde la raíz del proyecto):
    python universidades/es_politecnica_madrid/scraper_es_politecnica_madrid.py --sample 5
    python universidades/es_politecnica_madrid/scraper_es_politecnica_madrid.py --codes 565000311
    python universidades/es_politecnica_madrid/scraper_es_politecnica_madrid.py --all
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_politecnica_madrid"

# Diversa: matemáticas 1.º (corta), química (44 págs.), inglés, optativa de 3.º, francés, optativa en inglés
SAMPLE = ["565000311", "565000314", "565000332", "565000354", "565000381", "565005801"]

TOP = ["RESULTADOS", "DESCRIPCIÓN", "TEMARIO", "ACTIVIDADES", "CRITERIOS DE EVALUACIÓN",
       "RECURSOS", "OTRA INFORMACIÓN", "OBJETIVOS DE DESARROLLO SOSTENIBLE"]
TITLES = {
    "RESULTADOS": "Competencias y resultados de aprendizaje",
    "DESCRIPCIÓN": "Descripción",
    "TEMARIO": "Temario",
    "ACTIVIDADES": "Actividades formativas y de evaluación",
    "CRITERIOS DE EVALUACIÓN": "Criterios de evaluación",
    "RECURSOS": "Recursos didácticos y bibliografía",
    "OTRA INFORMACIÓN": "Otra información",
    "OBJETIVOS DE DESARROLLO SOSTENIBLE": "Objetivos de Desarrollo Sostenible",
}

_FOOTER = re.compile(r"^PR/CL/\d")           # inicia el pie de página
_WEEKS = re.compile(r"^(?:\d{1,2} ){14}\d{1,2} E$")
_NOISE = re.compile(r"^(SEMANAS|TEMAS|METODOLOGÍA|PRESENCIALIDAD DURACIÓN TOTAL.*|RESULTADOS EVALUADOS|"
                    r"[A-Z]{1,3}\d* ?(?:[A-Z]{1,3}\d+ ?)+|T\d+(?: T\d+)*)$")
_RES_LINE = re.compile(r"^(?:(?:CG|CE|CT|CB|RA)\d+\s?)+$")  # listas de códigos de competencias en la rejilla


class GuideError(RuntimeError):
    pass


def page_lines(pdf: pdfplumber.PDF) -> list[str]:
    out: list[str] = []
    for pg in pdf.pages:
        lines = (pg.extract_text() or "").splitlines()
        if lines and lines[0].startswith("G.A. "):
            lines = lines[1:]
        for i, l in enumerate(lines):
            if _FOOTER.match(l.strip()):
                lines = lines[:i]
                break
        out.extend(lines)
    return out


def split_sections(lines: list[str]) -> tuple[list[str], dict[str, list[str]]]:
    head: list[str] = []
    secs: dict[str, list[str]] = {}
    cur = None
    for l in lines:
        s = l.strip()
        if s in TOP and (cur is None or TOP.index(s) >= TOP.index(cur) or s == cur):
            cur = s
            secs.setdefault(cur, [])
            continue
        (head if cur is None else secs[cur]).append(l)
    return head, secs


def clean_text(lines: list[str]) -> str:
    t = "\n".join(l.rstrip() for l in lines)
    t = re.sub(r"\(cid:\d+\)", "", t)
    t = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", t)  # control chars basura del PDF
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def clean_activities(lines: list[str]) -> str:
    keep: list[str] = []
    for l in lines:
        s = l.strip()
        if s.startswith("PLANIFICACIÓN SEMANAL"):  # rejilla de puntos por semana: sin valor para la equivalencia
            break
        if not s or _WEEKS.match(s) or _NOISE.match(s) or _RES_LINE.match(s):
            continue
        keep.append(s)
    # una línea por registro; las filas "Presencial 10h 00m ..." se mantienen como viñetas
    return clean_text([("- " + s if re.match(r"^(Presencial|No presencial)\b", s) else s) for s in keep])


def head_parts(head: list[str]) -> tuple[str, str]:
    """Devuelve (requisitos+conocimientos previos, resto útil). Se descarta COORDINADOR/A y su valor."""
    txt = [l.strip() for l in head]
    try:
        i = next(k for k, l in enumerate(txt) if l.startswith("REQUISITOS OBLIGATORIOS"))
    except StopIteration:
        return "", ""
    boiler = re.compile(r"^(REQUISITOS OBLIGATORIOS|ASIGNATURAS REQUERIDAS|CONOCIMIENTOS PREVIOS RECOMENDADOS|"
                        r"ASIGNATURAS RECOMENDADAS( OTRAS RECOMENDACIONES)?|OTRAS RECOMENDACIONES)$")
    prereq = [l for l in txt[i:] if l and not boiler.match(l)]
    return clean_text(prereq), ""


def is_empty(text: str) -> bool:
    t = re.sub(r"(?im)^(requisitos obligatorios|asignaturas requeridas|conocimientos previos recomendados|"
               r"asignaturas recomendadas otras recomendaciones|asignaturas recomendadas|otras recomendaciones)\s*$",
               "", text)
    return re.sub(r"[\s—\-–.]+", "", t) == ""


# ---- Formato antiguo (guías 2025-26 con numeración "1. Datos descriptivos ...", castellano o inglés) ----
_OLD_KEYS = [
    ("prereq", r"conocimientos previos|prior knowledge"),
    ("results", r"competencias y resultados|skills and learning"),
    ("contents", r"descripci[oó]n de la asignatura y temario|brief description"),
    ("assess", r"actividades y criterios|activities and assessment"),
    ("resources", r"recursos did[aá]cticos|teaching resources"),
    ("other", r"otra informaci[oó]n|other information"),
    ("skip", r"datos descriptivos|^description$|profesorado|faculty|cronograma|schedule"),
]
_OLD_TITLES = {"prereq": "Conocimientos previos recomendados", "results": "Competencias y resultados de aprendizaje",
               "contents": "Descripción y temario", "assess": "Actividades y criterios de evaluación",
               "resources": "Recursos didácticos y bibliografía", "other": "Otra información"}


_OLD_CHROME = re.compile(r"^(PR/CL/001|ANX-PR/CL/001-01.*|PROCESO DE COORDINACI[ÓO]N DE|GU[ÍI]A DE APRENDIZAJE.*|"
                         r"LAS ENSEÑANZAS|COORDINATION PROCESS OF|LEARNING GUIDE.*|LEARNING ACTIVITIES|"
                         r"E\.T\.S\. de Ingenier[ií]a y|Dise[ñn]o Industrial|Industrial)$")


def is_old_format(lines: list[str]) -> bool:
    return not any(l.strip() == "RESULTADOS" for l in lines) and any(
        re.match(r"^1\. (Datos descriptivos|Description)", l.strip()) for l in lines)


def old_lines(pdf: pdfplumber.PDF) -> list[str]:
    out: list[str] = []
    for pg in pdf.pages:
        ls = (pg.extract_text() or "").splitlines()
        skip_next = False
        for l in ls:
            if skip_next:
                skip_next = False
                continue
            if re.search(r"P[aá]gina \d+ de \d+\s*$|Page \d+ of \d+\s*$", l):
                skip_next = True  # segunda línea del pie ("2S_2025-26 Grado ...")
                continue
            if "...." in l:  # índice
                continue
            if _OLD_CHROME.match(l.strip()):  # cabecera repetida en cada página
                continue
            out.append(l)
    return out


def split_old(lines: list[str]) -> dict[str, list[str]]:
    secs: dict[str, list[str]] = {}
    last, cur = 0, None
    for l in lines:
        m = re.match(r"^(\d+)\. (.{3,80})$", l.strip())
        if m and int(m.group(1)) == last + 1:
            kind = next((k for k, pat in _OLD_KEYS if re.search(pat, m.group(2).lower())), None)
            if kind:
                last, cur = last + 1, kind
                secs.setdefault(cur, [])
                continue
        if cur and cur != "skip":
            secs[cur].append(l)
    return secs


def scrape_old(entry: dict, lines: list[str]) -> tuple[str, dict, str]:
    secs = split_old(lines)
    lang = "en" if any(re.match(r"^1\. Description", l.strip()) for l in lines) else "es"
    md, blocks = [], {"contents": False, "learning_outcomes": False, "assessment": False,
                      "bibliography": False, "prerequisites": False}
    for key in ("prereq", "results", "contents", "assess", "resources", "other"):
        body = clean_text(secs.get(key, []))
        if not body or (key == "prereq" and is_empty(body)):
            continue
        # subapartados "5.1. Título" -> encabezado de nivel 3 solo si son del mismo número que el apartado
        body = re.sub(r"(?m)^(\d)\.(\d)\. ([A-Za-zÁÉÍÓÚ].{2,70})$",
                      lambda m: f"### {m.group(3)}" if re.search(
                          r"descripci|temario|competencias|resultados|actividades|criterios|recursos|otra|skills|learning|"
                          r"syllabus|assessment|resources|brief|other|asignaturas previas|recommended|bibliograf",
                          m.group(3).lower()) and len(m.group(3)) < 70 and m.group(2) in "12" and
                      not re.match(r"[A-Z ]{4,}$", m.group(3)) else m.group(0), body)
        md += [f"## {_OLD_TITLES[key]}", "", body, ""]
        blocks[{"prereq": "prerequisites", "results": "learning_outcomes", "contents": "contents",
                "assess": "assessment"}.get(key, "bibliography" if key == "resources" else "_")] = True
    blocks.pop("_", None)
    if "bibliography" in blocks and not re.search(r"(?i)bibliograf|bibliograph", clean_text(secs.get("resources", []))):
        blocks["bibliography"] = False
    return "\n".join(md), blocks, lang


def scrape_course(http: PoliteClient, entry: dict) -> tuple[Path, dict]:
    code = entry["codigo_asignatura"]
    data = http.get_bytes(entry["url_guia_docente"])
    if not data.startswith(b"%PDF"):
        raise GuideError("la respuesta no es un PDF")
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        first = (pdf.pages[0].extract_text() or "")
        old = "LEARNING GUIDE" in first or "GUÍA DE APRENDIZAJE" in first and "G.A. " not in first[:6]
        lines = old_lines(pdf) if old else page_lines(pdf)
    if old:
        olines = lines
        if code not in "\n".join(olines[:60]):
            raise GuideError("el PDF no corresponde a la asignatura")
        body, blocks, lang = scrape_old(entry, olines)
        if not blocks["contents"]:
            raise GuideError("formato antiguo: sin descripción/temario")
        e2 = dict(entry, idioma_pagina=lang)
        md = [f"# {entry['nombre_asignatura']} ({code})", "",
              f"- Titulación: {entry['nombre_grado']} · {entry['universidad']}",
              f"- Curso/semestre: {entry['curso_semestre']}",
              f"- Créditos: {entry['creditos_ects']} ECTS · Carácter: {entry['caracter']}",
              f"- Fuente: {entry['url_guia_docente']}", "", body]
        return write_markdown(SLUG, e2, "\n".join(md), blocks), blocks
    head, secs = split_sections(lines)
    if code not in "\n".join(head):
        raise GuideError("el PDF no corresponde a la asignatura")
    missing = [s for s in ("RESULTADOS", "TEMARIO") if s not in secs]
    if "TEMARIO" not in secs and "DESCRIPCIÓN" not in secs:
        raise GuideError(f"faltan apartados: {missing}")

    prereq, _ = head_parts(head)
    md = [f"# {entry['nombre_asignatura']} ({code})", "",
          f"- Titulación: {entry['nombre_grado']} · {entry['universidad']}",
          f"- Curso/semestre: {entry['curso_semestre']}",
          f"- Créditos: {entry['creditos_ects']} ECTS · Carácter: {entry['caracter']}",
          f"- Fuente: {entry['url_guia_docente']}", ""]
    has_pre = bool(prereq) and not is_empty(prereq)
    if has_pre:
        md += ["## Requisitos y conocimientos previos", "", prereq, ""]
    blocks = {"contents": False, "learning_outcomes": False, "assessment": False,
              "bibliography": False, "prerequisites": has_pre}
    for key in TOP:
        if key not in secs:
            continue
        body = clean_activities(secs[key]) if key == "ACTIVIDADES" else clean_text(secs[key])
        if not body:
            continue
        md += [f"## {TITLES[key]}", "", body, ""]
        if key in ("TEMARIO", "DESCRIPCIÓN"):
            blocks["contents"] = True
        elif key == "RESULTADOS":
            blocks["learning_outcomes"] = True
        elif key in ("CRITERIOS DE EVALUACIÓN", "ACTIVIDADES"):
            if key == "CRITERIOS DE EVALUACIÓN" or re.search(r"\d+\s?%", body):
                blocks["assessment"] = True
        elif key == "RECURSOS" and re.search(r"(?im)^bibliograf", body):
            blocks["bibliography"] = True
    path = write_markdown(SLUG, entry, "\n".join(md), blocks)
    return path, blocks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    args = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    if args.all:
        codes = [c for c, r in rows.items() if r["tipo_fuente"] != "sin_guia"]
    elif args.codes:
        codes = args.codes
    else:
        codes = SAMPLE[: (args.sample or 5)]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = skip = 0
    for c in codes:
        e = rows.get(c)
        if e is None:
            print(f"FALLO  {c}: no está en el catálogo"); fail += 1; continue
        if e["tipo_fuente"] == "sin_guia":
            print(f"omite  {c} {e['nombre_asignatura']}: sin guía"); skip += 1; continue
        try:
            path, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} -> {path.name} ({path.stat().st_size} bytes)"
                  + (f" · bloques ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except (FetchError, GuideError, Exception) as ex:  # noqa: BLE001
            print(f"FALLO  {c} {e['nombre_asignatura']}: {ex}"); fail += 1
    print(f"{ok} ok, {fail} fallos, {skip} omitidas")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
