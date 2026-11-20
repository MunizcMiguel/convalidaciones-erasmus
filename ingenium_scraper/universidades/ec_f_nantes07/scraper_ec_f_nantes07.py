#!/usr/bin/env python3
"""Fase 2 — Centrale Nantes spécialité Mécanique: PDF compartido por año -> Markdown por curso. CLI: --sample N | --all | --codes C1 C2"""
import argparse, io, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "ec_f_nantes07"
SAMPLE = ["MECA2_MATER", "MECA3_MEF", "MECA2_THERM", "MECA1_DSOLI", "MECA3_ENTRE", "MECA3_MATCOMPCSD"]
SECTIONS = {"Objectifs": "Objectifs", "Plan de l'enseignement": "Plan de l'enseignement", "Contrôle des connaissances": "Contrôle des connaissances",
            "Évaluation": "Évaluation", "Pré-requis": "Pré-requis", "Prérequis": "Prérequis", "Bibliographie": "Bibliographie",
            "Objectifs de Développement Durable (ODD) couverts par cet enseignement": "Objectifs de Développement Durable (ODD)"}
STAFF = re.compile(r"^(Responsable\(s\) du cours|Intervenant|Enseignant|Équipe pédagogique)", re.I)
FOOT = re.compile(r"^PROGRAMME INGÉNIEUR, SPÉCIALITÉ MÉCANIQUE - .* \d+$")


def to_md(title, code, pages):
    lines = []
    for k, pg in enumerate(pages):
        L = pg.split("\n")
        if k == 0:
            L = L[3:] if re.search(r"\[[A-Z0-9_]+\]$", L[2]) else L[4:]  # quitar cabecera (año/UE/título)
        lines += [l for l in L if not FOOT.match(l)]
    out = [f"# {title} [{code}]"]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    table_from = next((i for i, l in enumerate(lines) if l.startswith("COURS TRAVAUX DEVOIRS")), None)
    body = lines if table_from is None else lines[:table_from]
    tail = [] if table_from is None else lines[table_from:]
    for l in body:
        if STAFF.match(l):
            continue
        if l in SECTIONS:
            out.append(f"## {SECTIONS[l]}")
            if l == "Objectifs": blocks["learning_outcomes"] = True
            if l == "Plan de l'enseignement": blocks["contents"] = True
            if l in ("Contrôle des connaissances", "Évaluation"): blocks["assessment"] = True
            if l.startswith("Pré"): blocks["prerequisites"] = True
            if l == "Bibliographie": blocks["bibliography"] = True
        else:
            out.append(re.sub(r"^[•·▪] ?", "- ", l))
    if tail:
        out.append("## Volumen y créditos\n" + " ".join(tail))
    return "\n".join(out), blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)["asignaturas"]
    rows = cat
    if a.codes:
        rows = [r for r in cat if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        rows = [r for c in SAMPLE for r in cat if r["codigo_asignatura"] == c][:a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdfs, bad = {}, 0
    for r in rows:
        try:
            u = r["url_guia_docente"]
            if u not in pdfs:
                p = pdfplumber.open(io.BytesIO(http.get_bytes(u)))
                pdfs[u] = [(pg.extract_text() or "") for pg in p.pages]
            ini, fin = map(int, r["paginas_pdf"].split("-"))
            body, blocks = to_md(r["nombre_asignatura"], r["codigo_asignatura"], pdfs[u][ini - 1:fin])
            write_markdown(SLUG, r, body, blocks)
            print("ok", r["codigo_asignatura"], r["nombre_asignatura"])
        except Exception as e:
            bad += 1
            print("FAIL", r["codigo_asignatura"], type(e).__name__, e)
    sys.exit(1 if bad else 0)


main()
