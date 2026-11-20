#!/usr/bin/env python3
"""Fase 2 — URJC: guía docente PDF (servicios.urjc.es/guiasdocentes/pdfGuia.jsp, POST) -> Markdown.

Plantilla del PDF (con texto; página 1 = portada): I Identificación · II Presentación (II.B en inglés: se descarta) ·
III Resultados de aprendizaje · IV Contenido (IV.A Temario, IV.B Actividades formativas) · V Tiempo de trabajo · VI Metodología ·
VII Método de evaluación (A actividades y ponderación, B dispensa; C-E son texto legal común: se descartan) · VIII Recursos y materiales ·
IX Profesorado (se descarta). Cada página lleva una marca de agua girada (SOLRAC/NAUJ/…, hash, fecha de firma), la cabecera con el título
y el pie «Vicerrectorado … Página N»: se quitan. La URL lleva `?a={codigo}` solo para que la caché distinga los POST.
Uso: python universidades/es_rey_juan_carlos/scraper_es_rey_juan_carlos.py [--sample N | --all | --codes C...]
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
SLUG = "es_rey_juan_carlos"
ANYO = "2026-27"
# Física(1º), Expresión gráfica II(2º), Ingeniería de fluidos(2º), Teoría de máquinas(3º), Ingeniería de superficies(4º), Prácticas, TFG
SAMPLE = ["2404004", "2404012", "2404019", "2286023", "2286037", "2286039", "2286040"]
_NOISE = [r"^SOLRAC$", r"^NAUJ$", r"^YER$", r"^DADISREVINU$", r"^B1103082Q$", r"^\.[0-9a-f]{32}$", r"^:hsaH$", r"^\|$", r"^\d\d:\d\d$",
          r"^\d{4}/\d\d/\d\d$", r"^:amrif$", r"^ahceF$", r"^Vicerrectorado de Calidad.*P[aá]gina \d+$"]
_NOISE_RE = re.compile("|".join(_NOISE))
_TOP = re.compile(r"^(I|II|III|IV|V|VI|VII|VIII|IX)(\.[A-E])?\.?-\s*(Identificaci|Presentaci|Resultados de Aprendizaje|Contenido|Temario|Actividades formativas|"
                  r"Tiempo de trabajo|Metodolog|M[eé]todo de evaluaci|Descripci[oó]n de las actividades|Evaluaci[oó]n del alumnado con dispensa|Revisi[oó]n y reclamaci|"
                  r"Alumnado con discapacidad|Conducta acad|Recursos y materiales|Profesorado)")


class GuideError(Exception):
    pass


def get_lines(data: bytes) -> list[str]:
    out = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for n, pg in enumerate(pdf.pages):
            if n == 0:  # portada
                continue
            ls = [l.strip() for l in (pg.extract_text() or "").split("\n")]
            ls = [l for l in ls if l and not _NOISE_RE.match(l)]
            if ls:  # primera línea = título repetido
                ls = ls[1:]
            out += ls
    return out


def sections(lines):
    secs, cur = [], None
    for l in lines:
        if _TOP.match(l):
            cur = [l, []]
            secs.append(cur)
        elif cur is not None:
            cur[1].append(l)
    return secs


def render(body: list[str]) -> str:
    out = []
    for l in body:
        if re.match(r"^[•▪●-]\s+", l):
            out.append("- " + re.sub(r"^[•▪●-]\s+", "", l))
        elif l.lower() == "null":
            continue
        else:
            out.append(l)
    return "\n".join(out).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    plan = code[:4]
    data = http.get_bytes(e["url_guia_docente"], method="POST", data={"txtCursoAcademico": ANYO, "txtTitulacion": plan, "txtAsignatura": code})
    if not data.startswith(b"%PDF"):
        raise GuideError("no es un PDF")
    secs = sections(get_lines(data))
    if len(secs) < 8:
        raise GuideError(f"estructura inesperada ({len(secs)} apartados)")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/periodo: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {e['url_guia_docente']} (POST, curso {ANYO})", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    allbody = []
    for title, body in secs:
        t = title.lower()
        if ("presentaci" in t and "ingl" in t) or "profesorado" in t or t.startswith("i.-") or re.match(r"^vii\.[cde]", t):
            continue
        txt = render(body)
        level = "###" if re.match(r"^(iv|vii)\.[a-e]", t) else "##"
        clean = re.sub(r"^[IVX]+(\.[A-E])?\.?-\s*", "", title).strip()
        md += [f"{level} {clean}", ""] + ([txt, ""] if txt else [])
        allbody.append(txt)
        if t.startswith("iii.-"):
            blocks["learning_outcomes"] = len(txt) > 30
        elif t.startswith("iv.a"):
            blocks["contents"] = len(txt) > 30
        elif t.startswith("vii.a"):
            blocks["assessment"] = len(txt) > 30
        elif t.startswith("viii."):
            blocks["bibliography"] = len(txt) > 30 and txt.strip().lower() != "null"
    blocks["prerequisites"] = bool(re.search(r"(?i)conocimientos? previos?|requisitos? previos?|se recomienda haber|es conveniente haber|prerrequisit", "\n".join(allbody)))
    if not (blocks["contents"] or blocks["learning_outcomes"]):
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
    http.get_bytes("https://servicios.urjc.es/guiasdocentes/", force=True)  # cookie de sesión
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
