#!/usr/bin/env python3
"""Fase 2 — Universidad de La Rioja: guía docente HTML (aps.unirioja.es/GuiasDocentes/servlet/agetguiahtml?2026-27,803G,{codigo}) -> Markdown.

El `<body class="cuerpoHtml">` es una secuencia plana de `h2/h3/div/table`: cabecera (título, datos de la asignatura), «Departamentos
responsables» y «Profesorado previsto» (nombres, correos, despachos: se descartan) y luego Descripción de los contenidos, Requisitos previos,
Contexto, Competencias (generales/específicas), Resultados del aprendizaje, ODS (imágenes: se descartan), Temario, Bibliografía, Metodología,
Organización, Evaluación. Se conserva todo salvo lo descartado.
Uso: python universidades/es_rioja/scraper_es_rioja.py [--sample N | --all | --codes C...]
"""
from __future__ import annotations

import argparse
import re
import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

warnings.filterwarnings("ignore")
HERE = Path(__file__).parent
SLUG = "es_rioja"
DROP_H2 = ("Departamentos responsables", "Profesorado previsto", "Objetivos de desarrollo sostenible")


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
        if n in ("script", "style", "img"):
            continue
        if n in ("h3", "h4", "h5"):
            out.append(f"\n\n### {ch.get_text(' ', strip=True)}\n\n")
        elif n == "table":
            rows = [[re.sub(r"\s+", " ", c.get_text(" ", strip=True)).replace("|", "/") for c in tr.find_all(["td", "th"])] for tr in ch.find_all("tr")]
            rows = [r for r in rows if any(r)]
            if rows:
                w0 = max(map(len, rows))
                keep = [j for j in range(w0) if any(j < len(r) and r[j] for r in rows)]
                rows = [[r[j] if j < len(r) else "" for j in keep] for r in rows]
                w = len(keep)
                head = "| " + " | ".join(rows[0]) + " |"
                out.append("\n\n" + "\n".join([head, "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]]) + "\n\n")
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
        elif n.name:
            tmp = BeautifulSoup("<div></div>", "lxml").div
            tmp.append(n.__copy__())
            html_md(tmp, out)
    t = "".join(out).replace("\xa0", " ")
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    soup = BeautifulSoup(http.get_text(e["url_guia_docente"], encoding="utf-8"), "lxml")
    body = soup.body
    if body is None or not soup.find("h1") or f"\n{code}\n" not in "\n" + body.get_text("\n", strip=True)[:1500] + "\n":
        raise GuideError("la guía no corresponde a la asignatura o está vacía")
    # datos básicos (antes del primer h2)
    pre = []
    for ch in body.children:
        if getattr(ch, "name", None) == "h2":
            break
        pre.append(ch.get_text("\n", strip=True) if getattr(ch, "name", None) else str(ch))
    pre = "\n".join(pre)
    info = {k: v for k, v in re.findall(r"(Carácter|Duración|Horas presenciales|Horas estimadas de trabajo autónomo|Idiomas en que se imparte la asignatura|"
                                          r"Idiomas del material de lectura o audiovisual|Materia|Módulo):\n([^\n]+)", pre)}
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/periodo: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}"]
    md += [f"- {k}: {v}" for k, v in info.items()]
    md += [f"- Fuente: {e['url_guia_docente']}", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    secs, cur = [], None
    for ch in body.children:
        n = getattr(ch, "name", None)
        if n == "h2":
            cur = [ch.get_text(" ", strip=True), []]
            secs.append(cur)
        elif cur is not None and n:
            cur[1].append(ch)
    for title, nodes in secs:
        if title.startswith(DROP_H2):
            continue
        text = to_md(nodes)
        if not text:
            continue
        md += [f"## {title}", "", text, ""]
        t = title.lower()
        if t.startswith("descripción de los contenidos") or t == "temario":
            blocks["contents"] |= len(text) > 40
        elif t.startswith("resultados del aprendizaje") or t == "competencias":
            blocks["learning_outcomes"] |= len(text) > 40
        elif t == "evaluación":
            blocks["assessment"] = len(text) > 40
        elif t == "bibliografía":
            blocks["bibliography"] = len(text) > 40
        elif t.startswith("requisitos previos"):
            blocks["prerequisites"] = len(text) > 80 and "no se precisan" not in text.lower() and "ninguno" not in text.lower()
    if not (blocks["contents"] or blocks["learning_outcomes"]):
        raise GuideError("guía sin contenidos ni resultados de aprendizaje")
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def sample_codes(rows):
    """Diversa: 1.º básica (Matemáticas I), 2.º/3.º obligatorias de ingeniería, una optativa, prácticas externas y TFG."""
    pick = []
    for pat in (r"^Matemáticas I$", r"Resistencia de materiales", r"Teoría de mecanismos", r"Máquinas fluidomecánicas", r"Prácticas externas", r"Trabajo fin"):
        for c, r in rows.items():
            if re.search(pat, r["nombre_asignatura"], re.I) and c not in pick:
                pick.append(c)
                break
    for c, r in rows.items():
        if r["caracter"] == "optativa" and c not in pick:
            pick.append(c)
            break
    return pick


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    codes = [c for c, r in rows.items() if r["tipo_fuente"] != "sin_guia"] if a.all else (a.codes or sample_codes(rows)[: a.sample or 5])
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
