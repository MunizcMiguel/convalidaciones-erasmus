#!/usr/bin/env python3
"""Fase 2 — Mondragon: PDF TCPDF por asignatura («Planificación de la asignatura») -> Markdown.
Apartados en mayúsculas: DATOS GENERALES, PROFESORES (se descarta), CONOCIMIENTOS PREVIOS REQUERIDOS, COMPETENCIAS, RESULTADOS DE APRENDIZAJE,
ACTIVIDADES FORMATIVAS, SISTEMAS DE EVALUACIÓN, CONTENIDOS, RECURSOS DIDÁCTICOS Y BIBLIOGRAFÍA. Se cortan los anexos de adaptación (euskera, covid).
Uso: python universidades/es_mondragon_unibertsitatea/scraper_es_mondragon_unibertsitatea.py [--sample N | --all | --codes C...]"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "es_mondragon_unibertsitatea"
SAMPLE = ["GMC201", "GMQ302", "GMR201", "GMM201", "GMA203"]  # se completa con el TFG abajo
SECS = [("DATOS GENERALES", "Datos generales"), ("PROFESORES", None), ("CONOCIMIENTOS PREVIOS REQUERIDOS", "Conocimientos previos requeridos"),
        ("COMPETENCIAS", "Competencias"), ("RESULTADOS DE APRENDIZAJE", "Resultados de aprendizaje"), ("ACTIVIDADES FORMATIVAS", "Actividades formativas"),
        ("SISTEMAS DE EVALUACIÓN", "Sistemas de evaluación"), ("CONTENIDOS", "Contenidos"), ("RECURSOS DIDÁCTICOS Y BIBLIOGRAFÍA", "Recursos didácticos y bibliografía")]
CUT = re.compile(r"TESTUINGURUA|AURREIKUSITAKO|EGOKITZAPEN|IKASGAIAN EGINDAKO|ADAPTACI", re.I)


def scrape_course(http, e):
    with pdfplumber.open(http.get_file(e["url_guia_docente"])) as d:
        lines = "\n".join((p.extract_text() or "") for p in d.pages).split("\n")
    code = e["codigo_asignatura"]
    sec, out, order, curso = None, {}, [], None
    for l in lines:
        if l.startswith("Curso:") and "Planificación" in l:
            curso = l.split("-")[0].replace("Curso:", "").strip()
            continue
        if "Powered by TCPDF" in l or l.startswith("Goi Eskola Politeknikoa |") or re.match(rf"^\[{code}\].*\d/\d$", l):
            continue
        hit = next((k for k, _ in SECS if l == k or l.startswith(k + " ") and k in ("SISTEMAS DE EVALUACIÓN", "ACTIVIDADES FORMATIVAS", "RESULTADOS DE APRENDIZAJE") and l.split(k)[1].strip() in ("P MECANISMOS DE RECUPERACIÓN", "HL HNL HT", "DE ENAEE ECTS")), None)
        if hit and not (hit == "RESULTADOS DE APRENDIZAJE" and l != hit and False):
            sec = hit
            if hit not in order:
                order.append(hit)
            out.setdefault(hit, [])
            if l != hit and hit == "SISTEMAS DE EVALUACIÓN":
                out[hit].append("(Columnas: actividad y peso · mecanismos de recuperación)")
            continue
        if l.startswith("RESULTADOS DE APRENDIZAJE DE ENAEE"):
            sec = "RESULTADOS DE APRENDIZAJE"
            out.setdefault(sec, []).append("Resultados ENAEE (con ECTS):")
            if sec not in order:
                order.append(sec)
            continue
        if sec == "RECURSOS DIDÁCTICOS Y BIBLIOGRAFÍA" and CUT.search(l):
            break
        if sec:
            out[sec].append(l)
    if "CONTENIDOS" not in out and "RESULTADOS DE APRENDIZAJE" not in out:
        raise RuntimeError("estructura no reconocida")
    md = [f"# {e['nombre_asignatura']} ({code})", "", f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Edición de la ficha: curso {curso or '?'}", f"- Fuente: {e['url_guia_docente']}", ""]
    names = dict(SECS)
    for k in order:
        if names.get(k) is None:
            continue
        if k == "DATOS GENERALES":
            body = "\n".join(l for l in out[k] if l.strip())
        else:
            body = "\n".join(out[k]).strip()
        md += [f"## {names[k]}", "", body, ""]
    g = lambda k: len("\n".join(out.get(k, [])).strip())  # noqa: E731
    pre = "\n".join(out.get("CONOCIMIENTOS PREVIOS REQUERIDOS", []))
    blocks = dict(contents=g("CONTENIDOS") > 20, learning_outcomes=g("RESULTADOS DE APRENDIZAJE") > 20 or g("COMPETENCIAS") > 20,
                  assessment=g("SISTEMAS DE EVALUACIÓN") > 20, bibliography=g("RECURSOS DIDÁCTICOS Y BIBLIOGRAFÍA") > 20,
                  prerequisites=bool(pre.strip()) and "No se requiere" not in pre)
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    tfg = [c for c, r in rows.items() if r["caracter"] == "tfg"]
    sample = list(dict.fromkeys([c for c in SAMPLE if c in rows] + tfg))
    codes = list(rows) if a.all else (a.codes or sample[: a.sample or 5])
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = 0
    for c in codes:
        e = rows.get(c)
        try:
            p, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} ({p.stat().st_size} B)" + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
