#!/usr/bin/env python3
"""Fase 2 — ENSMM: PDF compartido 'Programme de Formation 2025-26' -> Markdown por módulo. CLI: --sample N | --all | --codes C1 C2"""
import argparse, io, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "ec_f_besanco06"
SAMPLE = ["MATH1", "FAB1", "CDS", "SHS1", "DYN1", "LV1"]
HEAD = re.compile(r"^([A-Z][A-Z0-9]{1,8}) ?: ?(.*?) ?\((\d+(?:,\d+)?) ?h\)$")
STOP = re.compile(r"^\d(?:ère|ème) année|^Unités d.enseignement|^Page \d+ / \d+$|^UE[A-Z]\d+ :|^\d+ heures d.enseignement")
NUMROW = re.compile(r"(?:^|\s)(\d+(?:\s+\d+){5}\s+\d+)$")


def module_lines(pdf, first, last):
    lines = []
    for i in range(first - 1, last):
        lines += (pdf.pages[i].extract_text() or "").split("\n")
    return lines


def to_md(code, chunk):
    out, i = [], 0
    title = HEAD.match(chunk[0])
    out.append(f"# {code} — {title.group(2) or code} ({title.group(3)} h)")
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    i = 1
    # tabla de horas: cabecera + fila numérica (se descartan nombres de responsables)
    while i < len(chunk) and not chunk[i].startswith(("Mode d", "Détail")):
        l = chunk[i]
        if l.startswith("Responsable Total"):
            j = i + 1
            while j < len(chunk) and not NUMROW.search(chunk[j]):
                j += 1
            if j < len(chunk):
                out.append("| Total | CM | TD | TP | AA | Conf | ECTS |\n|---|---|---|---|---|---|---|\n| "
                           + " | ".join(NUMROW.search(chunk[j]).group(1).split()) + " |")
            i = j + 1
            continue
        i += 1
    rest = chunk[i:]
    name_only = re.compile(r"^(?:[A-ZÉ]\.\s?)+[A-ZÉÈ'\- ]+$|^Responsables? ?:|^Intervenants? ?:")
    for l in rest:
        l = l.rstrip()
        if name_only.match(l):
            continue
        l = re.sub(r"\s*\((?:[A-ZÉ]\.\s?)+[A-ZÉÈ'\-]+(?:[ ,/]+(?:[A-ZÉ]\.\s?)*[A-ZÉÈ'\-]+)*\)", "", l)
        if l.startswith("Mode d’évaluation") or l.startswith("Mode d'évaluation"):
            blocks["assessment"] = True
            out.append("## Mode d’évaluation\n" + l.split(":", 1)[1].strip())
        elif l.startswith("Détail du programme"):
            blocks["contents"] = True
            out.append("## Détail du programme")
        elif re.match(r"^o\s", l):
            out.append("  - " + l[2:])
        elif l.startswith("- "):
            out.append(l)
        else:
            out.append(l)
    body = "\n".join(out)
    body = re.sub(r"\n(?=- |  - )", "\n", body)
    return body, blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = cat["asignaturas"]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        rows = [r for c in SAMPLE for r in rows if r["codigo_asignatura"] == c][:a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf = pdfplumber.open(io.BytesIO(http.get_bytes(rows[0]["url_guia_docente"])))
    lines = module_lines(pdf, 5, 27)
    heads = [k for k, l in enumerate(lines) if HEAD.match(l)]
    # mismos criterios que el discover: un módulo por cabecera, en orden; se emparejan por orden con el catálogo completo
    order = [r["codigo_asignatura"] for r in cat["asignaturas"]]
    assert len(order) == len(heads), (len(order), len(heads))
    span = {}
    for n, k in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        chunk = lines[k:end]
        for z, l in enumerate(chunk[1:], 1):
            if STOP.match(l):
                chunk = chunk[:z]
                break
        span[order[n]] = chunk
    bad = 0
    for r in rows:
        try:
            body, blocks = to_md(r["codigo_asignatura"], span[r["codigo_asignatura"]])
            write_markdown(SLUG, r, body, blocks)
            print("ok", r["codigo_asignatura"], r["nombre_asignatura"])
        except Exception as e:
            bad += 1
            print("FAIL", r["codigo_asignatura"], type(e).__name__, e)
    sys.exit(1 if bad else 0)


main()
