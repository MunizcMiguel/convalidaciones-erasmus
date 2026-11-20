#!/usr/bin/env python3
"""Fase 2 — UPNA: ficha HTML `ficha-asignaturaDOA?idioma=es&codAsig=NNNNNN` -> Markdown.

La ficha tiene una cabecera (año, código, asignatura, créditos, tipo, curso, periodo, departamento, PROFESORADO -> se descarta)
y secciones `<div><h3>Título</h3> ... </div>` (Módulo/Materia, Descripción/Contenidos, Competencias genéricas/específicas,
Resultados aprendizaje, Metodología, Evaluación, Temario, Programa de prácticas experimentales, Bibliografía, ODSs, Idiomas, Lugar).
Uso: python universidades/es_publica_navarra/scraper_es_publica_navarra.py [--sample N | --all | --codes C...]
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
SLUG = "es_publica_navarra"
# Matemáticas I(1º), Mecánica(2º), Teoría de máquinas(3º), Tecnología de fabricación, optativa Automoción, TFG
SAMPLE = ["248101", "248207", "248304", "248309", "248710", "248890"]


class GuideError(Exception):
    pass


def html_md(el, out, depth=0):
    for ch in el.children:
        if isinstance(ch, NavigableString):
            t = re.sub(r"\s+", " ", str(ch))
            if t.strip():
                out.append(t)
            continue
        n = ch.name
        if n in ("script", "style"):
            continue
        if n in ("h4", "h5", "h6"):
            out.append(f"\n\n#### {ch.get_text(' ', strip=True)}\n\n")
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


def to_md(nodes) -> str:
    out: list[str] = []
    for n in nodes:
        if isinstance(n, NavigableString):
            out.append(str(n))
        else:
            tmp = BeautifulSoup("<div></div>", "lxml").div
            tmp.append(n.__copy__())
            html_md(tmp, out)
    t = "".join(out).replace("\xa0", " ")
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    soup = BeautifulSoup(http.get_text(e["url_guia_docente"], encoding="utf-8"), "lxml")
    for x in soup(["script", "style"]):
        x.decompose()
    txt = soup.get_text("\n", strip=True)
    if f"Código:\n{code}" not in txt:
        raise GuideError("la ficha no corresponde a la asignatura")
    periodo = re.search(r"Periodo:\n([^\n]+)", txt)
    anyo = re.search(r"Año Académico:\s*(\d{4}/\d{4})", txt)
    idi = None
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/periodo: {e['curso_semestre']} · {periodo.group(1) if periodo else '?'}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Año académico de la ficha: {anyo.group(1) if anyo else '?'}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    found = {}
    for h3 in soup.find_all("h3"):
        title = h3.get_text(" ", strip=True)
        if title in ("Módulo/Materia", "Descripción/Contenidos", "Competencias genéricas", "Competencias específicas", "Resultados aprendizaje",
                     "Metodología", "Evaluación", "Temario", "Programa de prácticas experimentales", "Bibliografía", "ODSs", "Idiomas",
                     "Lugar de impartición") and title not in found:
            body = []
            for sib in h3.next_siblings:
                if getattr(sib, "name", None) == "a" and sib.get_text(strip=True) == "Subir":
                    break
                body.append(sib)
            text = re.sub(r"(?m)^Subir$", "", to_md(body)).strip()
            found[title] = text
    for title, text in found.items():
        if text:
            md += [f"## {title}", "", text, ""]
    ok = lambda k: len(found.get(k, "")) > 20  # noqa: E731
    blocks["contents"] = ok("Temario") or ok("Descripción/Contenidos")
    blocks["learning_outcomes"] = ok("Resultados aprendizaje") or ok("Competencias específicas")
    blocks["assessment"] = ok("Evaluación")
    blocks["bibliography"] = ok("Bibliografía")
    blocks["prerequisites"] = bool(re.search(r"(?i)prerrequisito|requisitos previos|conocimientos previos|se recomienda haber", "\n".join(found.values())))
    if not (blocks["contents"] or blocks["learning_outcomes"]):
        raise GuideError("ficha sin contenidos ni resultados de aprendizaje")
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
