#!/usr/bin/env python3
"""Fase 2 — Universidad de León: JSON de la API del visor de guías docentes -> Markdown.

`GET https://guiadocenteapi.unileon.es/snapshots/2026-2027/{codigo}` -> {"data": {...}}. Las listas (contents, evaluations, learningAims,
methodologies, recommendations, sources, i18n) traen cada elemento duplicado por idioma (`lang` es/en): se toma `es` (si una lista no tiene
elementos `es`, se usa lo que haya y se anota). Campos de profesorado (professor, professorEmail, assistants) y de firma (pdf*) se descartan.
  contents: description = título del bloque, comments = temas (HTML) · evaluations: name, value = peso %, description, comments ·
  learningAims: degree = código, description · methodologies: name, description, value/valueAlt = horas presenciales/no presenciales ·
  recommendations: name = código de la asignatura recomendada · sources: description (HTML) · i18n: description, comments (recomendaciones).
Uso: python universidades/es_leon/scraper_es_leon.py [--sample N | --all | --codes C...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_leon"
SAMPLE = ["0708301", "0708310", "0708306"]  # se completa con la lista de catálogo en sample_codes


class GuideError(Exception):
    pass


def html_text(s) -> str:
    if not s:
        return ""
    soup = BeautifulSoup(str(s), "lxml")
    out: list[str] = []

    def walk(el):
        for ch in el.children:
            if isinstance(ch, NavigableString):
                out.append(re.sub(r"\s+", " ", str(ch)))
            elif ch.name == "br":
                out.append("\n")
            elif ch.name == "li":
                out.append("\n- ")
                walk(ch)
            elif ch.name in ("p", "div", "ul", "ol", "h1", "h2", "h3", "h4", "tr"):
                out.append("\n")
                walk(ch)
                out.append("\n")
            elif ch.name in ("td", "th"):
                walk(ch)
                out.append(" | ")
            else:
                walk(ch)

    walk(soup.body or soup)
    t = "".join(out).replace("\xa0", " ")
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    return re.sub(r"\n{2,}", "\n\n", t).strip()


def pick(lst):
    es = [x for x in lst or [] if x.get("lang") == "es"]
    return es or list(lst or [])


def num(v):
    try:
        f = float(v)
        return f"{f:g}"
    except (TypeError, ValueError):
        return ""


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    raw = json.loads(http.get_bytes(e["url_guia_docente"]))
    d = raw.get("data")
    if not d or d.get("course") != code:
        raise GuideError("la API no devuelve datos de esta asignatura")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/periodo: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS (teóricos {num(d.get('credits_theory'))}, prácticos {num(d.get('credits_practice'))}) · Carácter: {e['caracter']}",
          f"- Idioma de impartición: {d.get('language') or '?'} · Curso académico: {d.get('term')}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)

    def section(title, body):
        body = [b for b in body if b and b.strip()]
        if body:
            md.extend([f"## {title}", ""] + ["\n\n".join(body), ""])
        return bool(body)

    i18n = pick(d.get("i18n"))
    section("Descripción", [html_text(x.get("description")) for x in i18n])
    rec = [html_text(x.get("comments")) for x in i18n]
    recs = [f"- {x.get('name')}: {html_text(x.get('description'))}" for x in pick(d.get("recommendations"))]
    blocks["prerequisites"] = section("Recomendaciones / asignaturas previas", rec + ["\n".join(recs)] if recs else rec)
    aims = []
    for x in sorted(pick(d.get("learningAims")), key=lambda x: (str(x.get("degree")), int(x.get("sequence") or 0))):
        t = html_text(x.get("description"))
        if t:
            aims.append(f"- {x['degree'] + ': ' if x.get('degree') else ''}{t}")
    blocks["learning_outcomes"] = section("Resultados de aprendizaje / competencias", ["\n".join(aims)])
    cont = []
    for x in sorted(pick(d.get("contents")), key=lambda x: int(x.get("sequence") or 0)):
        title, body = html_text(x.get("description")), html_text(x.get("comments"))
        if title or body:
            cont.append((f"### {title}\n\n" if title else "") + body)
    blocks["contents"] = section("Contenidos", cont)
    met = []
    for x in sorted(pick(d.get("methodologies")), key=lambda x: int(x.get("sequence") or 0)):
        met.append(f"- **{x.get('name') or ''}** ({num(x.get('value'))} h presenciales, {num(x.get('valueAlt'))} h no presenciales): {html_text(x.get('description'))}")
    section("Metodología", ["\n".join(met)])
    ev = []
    for x in sorted(pick(d.get("evaluations")), key=lambda x: int(x.get("sequence") or 0)):
        ev.append(f"### {x.get('name') or 'Prueba'} — {num(x.get('value'))}%\n\n" + "\n\n".join(t for t in (html_text(x.get("description")), html_text(x.get("comments"))) if t))
    blocks["assessment"] = section("Evaluación", ev)
    src = [f"- {html_text(x.get('description')).replace(chr(10), ' ')}" for x in pick(d.get("sources")) if html_text(x.get("description"))]
    blocks["bibliography"] = section("Bibliografía", ["\n".join(src)])
    if not (blocks["contents"] or blocks["learning_outcomes"]):
        raise GuideError("guía sin contenidos ni resultados de aprendizaje")
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def sample_codes(rows):
    cand = [c for c, r in rows.items() if r["tipo_fuente"] != "sin_guia"]
    pick_ = []
    for pat in (r"ALGEBRA", r"INFORM", r"F[IÍ]SICA", r"MEC[AÁ]NICA|MATERIALES", r"EXPRESI"):
        for c in cand:
            if re.search(pat, rows[c]["nombre_asignatura"], re.I) and c not in pick_:
                pick_.append(c)
                break
    for c in cand:
        if rows[c]["caracter"] == "optativa" and c not in pick_:
            pick_.append(c)
            break
    return pick_


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
