#!/usr/bin/env python3
"""Fase 2 — UMH: JSON de la ficha de asignatura (umh.es/get_dataJson.py?item=:asi_g_NNNN_S1) -> Markdown.

El JSON contiene los campos de la ficha (`_x_*`); se descartan los de profesorado (`*_profesor*`, `*_responsable*`, `*colaborador*`).
Los textos largos (evaluación, metodología, bibliografía) vienen en HTML con entidades -> se convierten a Markdown.
Uso: python universidades/es_miguel_hernandez_elche/scraper_es_miguel_hernandez_elche.py [--sample N | --all | --codes C...]
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
SLUG = "es_miguel_hernandez_elche"
API = "https://www.umh.es/get_dataJson.py?item=:asi_g_{code}_S1&frm=DEFAULT&lang=ES"
# Cálculo(1º), Mecánica de Fluidos(2º), Teoría de Máquinas(2º), Proyectos(4º), optativa Ing. Acústica, TFG
SAMPLE = ["1225", "1789", "1808", "1801", "1819", "1821"]


class GuideError(Exception):
    pass


def val(v):
    """Valor de un campo `_x_*`: lista cuyo primer elemento puede llevar prefijo '~$' / '~f' / '~>'."""
    out = []
    for x in v or []:
        if x is None:
            continue
        if isinstance(x, dict):
            out.append(x.get("label", ""))
        else:
            out.append(re.sub(r"^~[$f>]", "", str(x)))
    return out


def html_text(s: str) -> str:
    s = re.sub(r"<!--.*?-->", "", s)
    soup = BeautifulSoup(s, "lxml")
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
            elif ch.name in ("p", "div", "ul", "ol", "tr", "h1", "h2", "h3", "h4"):
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


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    t = http.get_bytes(API.format(code=code)).decode("utf-8")
    try:
        d = json.JSONDecoder().raw_decode(t[t.index("={") + 1:])[0]
    except Exception as ex:  # noqa: BLE001
        raise GuideError(f"JSON ilegible: {ex}")
    if d.get("href") != f":asi_g_{code}_S1":
        raise GuideError("JSON de otra asignatura")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    ht = val(d.get("_x_horas_asignatura")), val(d.get("_x_horas_dirigidas")), val(d.get("_x_horas_autonomas"))
    if ht[0]:
        md += [f"- Horas: totales {ht[0][0]} · dirigidas {ht[1][0] if ht[1] else '?'} · autónomas {ht[2][0] if ht[2] else '?'}"
               f" (créditos teóricos {', '.join(val(d.get('_x_creditos_teoricos_asignatura'))) or '?'}, prácticos {', '.join(val(d.get('_x_creditos_practicos_asignatura'))) or '?'})", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)

    def section(title, parts):
        parts = [p for p in parts if p and p.strip()]
        if parts:
            md.extend([f"## {title}", "", "\n\n".join(parts), ""])
        return bool(parts)

    def bullets(key):
        return "\n".join(f"- {html_text(x)}" for x in val(d.get(key)))

    section("Descripción", [html_text(x) for x in val(d.get("_x_descripcion_asignatura"))])
    section("Interés profesional", [html_text(x) for x in val(d.get("_x_interes_profesional"))])
    blocks["prerequisites"] = section("Requisitos adicionales", [html_text(x) for x in val(d.get("_x_requisitos_adicionales"))])
    cp = [bullets("_x_asignatura_tiene_competencias_generales"), bullets("_x_asignatura_tiene_competencias_especificas"),
          bullets("_x_asignatura_tiene_competencias_profesionales")]
    section("Competencias generales", [cp[0]])
    section("Competencias específicas", [cp[1]])
    section("Competencias profesionales", [cp[2]])
    obj = bullets("_x_asignatura_tiene_objetivos")
    section("Objetivos / resultados de aprendizaje", [obj])
    blocks["learning_outcomes"] = bool(obj or any(cp))
    uni = sorted(d.get("_x_asignatura_tienen_unidades_didacticas") or [], key=lambda u: (val(u.get("_x_orden")) or [""])[0])
    cont = "\n".join(f"{i}. {u['label'].strip()}" for i, u in enumerate(uni, 1))
    blocks["contents"] = section("Contenidos (unidades didácticas)", [cont])
    section("Metodología", [html_text(x) for x in val(d.get("_x_metodologia_asignatura"))])
    ev = [html_text(x) for x in val(d.get("_x_evaluacion_asignatura"))]
    ev += [f"**Características de la prueba:** {html_text(x)}" for x in val(d.get("_x_caracteristicas_prueba"))]
    ev += [f"**Criterios de corrección:** {html_text(x)}" for x in val(d.get("_x_criterios_correccion"))]
    blocks["assessment"] = section("Evaluación", ev)
    bib = [("Básica", val(d.get("_x_bibliografia"))), ("Complementaria", val(d.get("_x_bibliografia_complementaria")))]
    bparts = [f"### {n}\n\n" + "\n".join(f"- {html_text(x)}" for x in v) for n, v in bib if v]
    blocks["bibliography"] = section("Bibliografía", bparts)
    sw = val(d.get("_x_software_asignatura"))
    section("Software", ["\n".join(f"- {x}" for x in sw)])
    if not (blocks["contents"] or blocks["learning_outcomes"] or blocks["assessment"]):
        raise GuideError("ficha vacía (sin contenidos, competencias ni evaluación)")
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
