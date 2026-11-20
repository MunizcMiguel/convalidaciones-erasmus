#!/usr/bin/env python3
"""Fase 2 — Universidad de Cádiz: programas docentes HTML (asignaturas.uca.es/{curso}/{codigo}) -> Markdown.

La ficha es una página única con un <fieldset> por apartado (legend = título): Requisitos y recomendaciones (los textos están en
campos de formulario), Profesorado (se descarta), Idiomas/Movilidad (se descartan), Resultados del proceso de formación y
aprendizaje, Resultados de aprendizaje, Actividades y metodologías docentes, Sistema de evaluación (+ Procedimientos de evaluación),
Temario, Bibliografía (básica/recomendada), Comentarios, Inteligencia artificial (política, se descarta).
Los apartados vacíos sólo aparecen con su rejilla/etiquetas; se detectan por falta de filas de datos.
Uso: python universidades/es_cadiz/scraper_es_cadiz.py [--sample N | --all | --codes C...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_cadiz"
# Álgebra (1º), Expresión Gráfica (1º), Química (2º), Mecánica de Fluidos (2º), Tecnologías de Fabricación (3º), TFG, optativa, optativa
SAMPLE = ["21720001", "21720010", "21720007", "21720012", "21720032", "21720050", "21720035", "21720048"]
DROP = {"profesorado", "idiomas", "movilidad", "inteligencia artificial", "sistema de evaluación",
        "bibliografía básica", "bibliografía recomendada"}
INFO = ["Tipo asignatura", "Módulo", "Materia", "Duración", "Curso", "Idioma", "Créd. Teoría", "Créd. Prácticas", "Créd. ECTS"]


class GuideError(Exception):
    pass


def cell(td) -> str:
    return re.sub(r"\s+", " ", td.get_text(" ", strip=True)).replace("|", "/")


def table_md(t) -> str:
    rows = []
    for tr in t.find_all("tr"):
        cs = [cell(c) for c in tr.find_all(["th", "td"])]
        if cs and any(cs):
            rows.append(cs)
    if len(rows) < 2:  # solo cabecera -> vacío
        return ""
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * n]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def fieldset_md(f) -> str:
    parts = []
    for t in f.find_all("table"):
        m = table_md(t)
        if m:
            sub = t.find_previous(["h4", "h5", "legend", "label"])
            parts.append(m)
    if not parts:
        # campos de formulario con texto (requisitos, recomendaciones)
        for inp in f.find_all(["input", "textarea"]):
            val = (inp.get("value") if inp.name == "input" else inp.get_text()) or ""
            val = re.sub(r"\s+", " ", BeautifulSoup(val, "lxml").get_text(" ", strip=True)).strip()
            if inp.get("type") in ("hidden", "file", "checkbox", "radio") or not val:
                continue
            lab = inp.find_previous("label")
            parts.append(f"**{cell(lab) if lab else 'Texto'}**: {val}")
    return "\n\n".join(parts)


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    html = http.get_text(e["url_guia_docente"])
    soup = BeautifulSoup(html, "lxml")
    for x in soup(["script", "style"]):
        x.decompose()
    cont = soup.find(id="contenido")
    if cont is None or code not in cont.get_text()[:600]:
        raise GuideError("ficha no encontrada o no corresponde a la asignatura")
    text = cont.get_text("\n", strip=True)
    info = []
    for k in INFO:
        m = re.search(rf"\n{re.escape(k)}:\n([^\n]+)", text)
        if m:
            info.append(f"- {k}: {m.group(1)}")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/semestre: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']}", ""]
    if info:
        md += ["## Datos de la asignatura", ""] + info + [""]
    blocks = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False,
              "prerequisites": False}
    seen = set()
    for f in cont.find_all("fieldset"):
        leg = f.find("legend")
        if leg is None:
            continue
        title = re.sub(r"\s+", " ", leg.get_text(" ", strip=True))
        low = title.lower()
        if low in DROP or low in seen:
            continue
        if low == "bibliografía":
            # contiene subtablas "básica" y "recomendada"; se renderiza por tablas con su rótulo
            subs = []
            for t in f.find_all("table"):
                m = table_md(t)
                if m:
                    lab = "básica" if "basica" in (t.get("id") or "") else "recomendada"
                    subs.append(f"### Bibliografía {lab}\n\n{m}")
            body = "\n\n".join(subs)
        elif low == "procedimientos de evaluación":
            body = fieldset_md(f)
        else:
            body = fieldset_md(f)
        seen.add(low)
        if not body:
            continue
        md += [f"## {title}", "", body, ""]
        if low.startswith("requisitos"):
            vals = re.findall(r"\*\*(?:Requisitos previos|Recomendaciones)\*\*: (.+)", body)
            blocks["prerequisites"] = any(v.strip(" .").lower() not in ("ninguno", "no", "-", "ninguna", "no hay") for v in vals)
        elif low.startswith("resultados"):
            blocks["learning_outcomes"] = True
        elif low == "temario":
            blocks["contents"] = True
        elif low == "procedimientos de evaluación":
            blocks["assessment"] = True
        elif low == "bibliografía":
            blocks["bibliography"] = True
    if not (blocks["contents"] or blocks["learning_outcomes"]):
        raise GuideError("ficha sin temario ni resultados (programa no publicado)")
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


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
