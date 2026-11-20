"""Fase 2 - RUB Elektrotechnik und Informationstechnik: Modulhandbuch PDF compartido -> Markdown por modulo.
Uso: python universidades/ec_d_bochum01/scraper_ec_d_bochum01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

SLUG = "ec_d_bochum01"
HERE = Path(__file__).parent
SAMPLE = ["149034", "149041", "149100", "149054", "149823"]  # ET1, ET4 (teorica), Systemtheorie 2, Praxismodul 2, Bachelorarbeit
H2 = {
    "Lernziele (learning outcomes)": "Lernziele (learning outcomes)",
    "Inhalt": "Inhalt",
    "Lehrformen": "Lehrformen",
    "Prüfungsformen": "Prüfungsformen",
    "Voraussetzungen für die Vergabe von Credits": "Voraussetzungen für die Vergabe von Credits",
    "Verwendung des Moduls": "Verwendung des Moduls",
    "Literatur": "Literatur",
    "Literatur und Lernmaterialien": "Literatur",
}
RE_SEITE = re.compile(r"^Seite \d+ von \d+$")
RE_STELLEN = re.compile(r"^Stellenwert der Note")
BLOCKS = {
    "contents": "Inhalt",
    "learning_outcomes": "Lernziele (learning outcomes)",
    "assessment": "Prüfungsformen",
    "bibliography": "Literatur",
    "prerequisites": "Teilnahmevoraussetzungen",
}


def fix(l: str) -> str:
    l = l.replace("\u2022", "- ").replace("\uf0b7", "- ").replace("\u25aa", "- ")
    return re.sub(r"^[•·▪●]\s*", "- ", l)


def to_md(pages: list[list[str]], entry: dict) -> tuple[str, dict]:
    lines = [fix(l) for ls in pages for l in ls if not RE_SEITE.match(l.strip())]
    out = [f"# {entry['nombre_asignatura']}", ""]
    mode = "head"  # head | skip | body
    head = []
    found = {b: False for b in BLOCKS}
    for l in lines:
        s = l.strip()
        if s.startswith("Titel des Moduls:"):
            continue
        if s.startswith("Modulbeauftragte/r und hauptamtlich Lehrende"):
            mode = "skip"
            continue
        if mode == "skip":
            if s in H2:
                mode = "body"
            else:
                continue
        if s in H2:
            mode = "body"
            out += ["", f"## {H2[s]}", ""]
            for b, k in BLOCKS.items():
                if H2[s] == k:
                    found[b] = True
            continue
        if RE_STELLEN.match(s):
            out += ["", "## Stellenwert der Note für die Endnote", ""]
            mode = "body"
            continue
        if mode == "head":
            head.append(s)
        else:
            out.append(l.rstrip())
    if any("Teilnahmevoraussetzungen" in h for h in head):
        found["prerequisites"] = True
    out[2:2] = ["## Moduldaten", "", "\n".join(head), ""]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    return text, found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, nargs="?", const=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    ents = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    codes = list(ents) if a.all else a.codes or [c for c in SAMPLE if c in ents][: a.sample or 5]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdfs: dict[str, list[list[str]]] = {}
    fails = 0
    for c in codes:
        e = ents[c]
        if e["tipo_fuente"] == "sin_guia":
            print(f"{c}: sin_guia")
            continue
        try:
            url = e["url_guia_docente"]
            if url not in pdfs:
                with pdfplumber.open(http.get_file(url)) as pdf:
                    pdfs[url] = [(p.extract_text() or "").splitlines() for p in pdf.pages]
            ini, fin = map(int, e["paginas_pdf"].split("-"))
            body, found = to_md(pdfs[url][ini - 1:fin], e)
            if len(body) < 300:
                raise RuntimeError("ficha casi vacia")
            write_markdown(SLUG, e, body, found)
            print(f"{c}: ok {e['nombre_asignatura']} ({len(body)} chars) falta={[k for k, v in found.items() if not v]}")
        except Exception as ex:  # noqa: BLE001
            fails += 1
            print(f"{c}: FALLO {ex}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
