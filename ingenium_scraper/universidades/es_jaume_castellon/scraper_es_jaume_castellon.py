#!/usr/bin/env python3
"""Fase 2 — UJI: guía docente = subpáginas del SIA (ujiapps.uji.es/sia/...) -> Markdown.

Subpáginas usadas (todas bajo /sia/, permitido por robots.txt; la guía unificada e-ujier.uji.es/pls está bloqueada y NO se usa):
temario, metodologia, evaluacion, actividades (actividades formativas + competencias + resultados de aprendizaje), reqmatricula.
Cada una trae el contenido en `div.contenido > div.pagina-asignatura-seccion`. Profesorado (/profesores) no se descarga.
Bibliografía: solo enlace al catálogo de la biblioteca -> bibliography=False.
Uso: python universidades/es_jaume_castellon/scraper_es_jaume_castellon.py [--sample N | --all | --codes C...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_jaume_castellon"
SECTIONS = ["temario", "metodologia", "evaluacion", "actividades", "reqmatricula"]
# Àlgebra(1º,extinguida), Mecànica de Fluids(2º), Disseny de Màquines(3º), Pràctiques Externes, optativa, TFG
SAMPLE = ["EM1001", "EM1016", "EM1021", "EM1034", "EM1037", "EM1047"]


class GuideError(Exception):
    pass


def html_md(el, out: list[str], depth=0):
    for ch in el.children:
        if isinstance(ch, NavigableString):
            t = re.sub(r"\s+", " ", str(ch))
            if t.strip():
                out.append(t)
            continue
        n = ch.name
        if n in ("script", "style"):
            continue
        if n in ("h1", "h2", "h3", "h4", "h5"):
            out.append(f"\n\n{'#' * (int(n[1]) + 1)} {ch.get_text(' ', strip=True)}\n\n")
        elif n == "table":
            rows = [[re.sub(r"\s+", " ", c.get_text(" ", strip=True)).replace("|", "/") for c in tr.find_all(["td", "th"])] for tr in ch.find_all("tr")]
            rows = [r for r in rows if any(r)]
            if rows:
                w = max(map(len, rows))
                rows = [r + [""] * (w - len(r)) for r in rows]
                out.append("\n\n| " + " | ".join(rows[0]) + " |\n|" + "---|" * w + "\n" + "\n".join("| " + " | ".join(r) + " |" for r in rows[1:]) + "\n\n")
        elif n in ("ul", "ol"):
            out.append("\n")
            for li in ch.find_all("li", recursive=False):
                sub = []
                html_md(li, sub, depth + 1)
                out.append("  " * depth + "- " + re.sub(r"\s+", " ", "".join(sub)).strip() + "\n")
            out.append("\n")
        elif n == "br":
            out.append("\n")
        elif n in ("p", "div", "section", "tr"):
            out.append("\n\n")
            html_md(ch, out, depth)
            out.append("\n\n")
        else:
            html_md(ch, out, depth)


def to_md(node) -> str:
    out: list[str] = []
    html_md(node, out)
    t = "".join(out)
    t = re.sub(r"\[if [^\]]*\]>.*?<!\[endif\]\]?", "", t, flags=re.S)  # restos de Word (comentarios condicionales MSO)
    t = re.sub(r"<!\[endif\]\]?>?", "", t)
    t = re.sub(r"\[if !supportLists\]·?\[endif\]", "", t)
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return re.sub(r"(?m)^[•·]\s*", "- ", t).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    base = e["url_guia_docente"]
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {base}", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    for sec in SECTIONS:
        soup = BeautifulSoup(http.get_text(f"{base}/{sec}"), "lxml")
        cont = soup.select_one("div.contenido")
        if cont is None:
            raise GuideError(f"sin contenido en {sec}")
        body = []
        for s in cont.select("div.pagina-asignatura-seccion"):
            for pr in s.select("div.profesores, .profesorado"):
                pr.decompose()
            body.append(to_md(s))
        text = "\n\n".join(b for b in body if b)
        text = "\n".join(l for l in text.split("\n") if l.strip() != "Requisitos de asignatura")
        text = re.sub(r"(?m)^(##+ (.+))\n\n?\2$", r"\1", text)  # título repetido como línea suelta
        if not text.strip():
            continue
        md += [text, ""]
        low = text.lower()
        if sec == "temario":
            blocks["contents"] = len(text) > 40
        elif sec == "evaluacion":
            blocks["assessment"] = "%" in text or "criteris" in low
        elif sec == "actividades":
            blocks["learning_outcomes"] = "resultats d'aprenentatge" in low and len(text.split("Resultats d'aprenentatge")[-1]) > 30
        elif sec == "reqmatricula":
            blocks["prerequisites"] = bool(re.search(r"(?i)requisit|prerrequisit|haver superat|recomana", text)) and len(text) > 120
    if not blocks["contents"] and not blocks["learning_outcomes"]:
        raise GuideError("guía sin temario ni resultados de aprendizaje")
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


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
        if not e:
            print(f"FALLO {c}: no está en el catálogo")
            fail += 1
            continue
        try:
            p, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} ({p.stat().st_size} B)" + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c} {e['nombre_asignatura']}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
