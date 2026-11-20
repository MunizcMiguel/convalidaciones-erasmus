#!/usr/bin/env python3
"""Fase 2 — ENIT: PDF 'Syllabus Titre d'Ingénieur' por semestre -> Markdown por EC/UE. CLI: --sample N | --all | --codes C1 C2"""
import argparse, io, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "ec_f_tarbes03"
SAMPLE = ["IGENI-EC0512", "IGENI-EC0521", "IGENI-EC0541", "IGENI-EC1012", "IGENI-EC0722", "IGENI-EC0561"]
# etiquetas rotadas del PDF (texto invertido): se descartan o se convierten en encabezado
JUNK = {"tamroF/eriaroH", "emuloV", "sédroba", "semèht", "xuapicnirP", "sfticejbo", "sfticejbO", "sésiv", "xuarénég", ")s(ecnetépmoC", "uo/te", "sneyom", "sedohtéM",
        "seuqigogadép", "sunetnoC", "enitnoc", "xuaropmet", "noitaulavé", "elleuqiruoc"}
HEADS = {"Acquis d’apprentissage visés": "Acquis d’apprentissage visés", "Modalités d’évaluation": "Modalités d’évaluation", "Langue d’enseignement": "Langue d’enseignement",
         "Ressources bibliographiques": "Ressources bibliographiques", "Travail personnel hors présentiel": "Travail personnel hors présentiel",
         "Objectifs de la formation visés": "Objectifs de la formation visés", "Thèmes et Objectifs de la formation visés": "Thèmes et objectifs de la formation visés",
         "Présentation de l’EC": "Présentation", "Présentation de l’UE": "Présentation"}
STAFF = re.compile(r"^(Coordinateur ENIT|Nom\(s\) ?du ?/ ?des ?enseignant|Enseignant|Intervenant)", re.I)
SKIP = re.compile(r"^Syllabus \((Français|English)\)|^Coefficient interne")


def to_md(title, code, pages):
    out = [f"# {title} [{code}]"]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    header = True  # bloque de cabecera: solo se conservan códigos, nombre y tabla de horas (se descartan nombres de profesores)
    KEEP = re.compile(r"^(Code ?(EC|UE) |Nom ?de ?l.(EC|UE) |Cr[ée]dits ?ECTS|Format Heures|CM|TD|TP|Projet encadré|Projet en autonomie|Total) ?")
    END_HEADER = ("Acquis d’apprentissage visés", "Thèmes et Objectifs de la formation visés", "Objectifs de la formation visés", "Modalités d’évaluation")
    for pg in pages:
        for l in pg:
            if STAFF.match(l):
                continue
            if l in END_HEADER:
                header = False
            if header:
                if not (KEEP.match(l) or l in ("Présentation de l’EC", "Présentation de l’UE")) or re.match(r"^(Coordinateur|Nom\(s\))", l):
                    continue
            if SKIP.match(l):
                continue
            toks = l.split()
            if toks and all(t in JUNK for t in toks):
                if "sunetnoC" in toks:
                    out.append("## Contenus"); blocks["contents"] = True
                continue
            if toks and toks[0] in JUNK:
                if toks[0] == "seuqigogadép":
                    out.append("## Méthodes et/ou moyens pédagogiques")
                l = " ".join(toks[1:])
            if l in HEADS:
                out.append(f"## {HEADS[l]}")
                if l.startswith("Acquis"): blocks["learning_outcomes"] = True
                if l.startswith("Modalités"): blocks["assessment"] = True
                if l.startswith("Ressources"): blocks["bibliography"] = True
                continue
            if l.startswith("Prérequis pour"):
                blocks["prerequisites"] = True
                out.append("## Prérequis")
                continue
            out.append(re.sub(r"^\s*[-•] ?", "- ", re.sub(r"^o ", "  - ", l)))
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
                pdfs[u] = [(pg.extract_text(x_tolerance=1.0, y_tolerance=3) or "").split("\n") for pg in p.pages]
            ini, fin = map(int, r["paginas_pdf"].split("-"))
            body, blocks = to_md(r["nombre_asignatura"], r["codigo_asignatura"], pdfs[u][ini - 1:fin])
            write_markdown(SLUG, r, body, blocks)
            print("ok", r["codigo_asignatura"], r["nombre_asignatura"])
        except Exception as e:
            bad += 1
            print("FAIL", r["codigo_asignatura"], type(e).__name__, e)
    sys.exit(1 if bad else 0)


main()
