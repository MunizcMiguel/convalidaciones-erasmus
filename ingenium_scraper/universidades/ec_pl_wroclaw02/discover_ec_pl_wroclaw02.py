"""Fase 1 - Wroclaw University of Science and Technology (PWr), Faculty of Mechanical Engineering (W10).
Grado: I level (bachelor) "Mechanical Engineering and Machine Building", full-time, en ingles.
Fuente: PDF compartido con todas las fichas (SUBJECT CARD) publicado por la facultad en wm.pwr.edu.pl (karty_kursow/mbm_en_st_i.pdf).
Las fichas no traen curso/semestre. Uso: python universidades/ec_pl_wroclaw02/discover_ec_pl_wroclaw02.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_wroclaw02"
PDF_URL = ("https://wm.pwr.edu.pl/fcp/sGBUKOQtTKlQhbx08SlkFUBhQAykrCDILDWdbXxMbFmFBWxslAxt1FSVcVnRKCkI8VQIDJCUODBYAKg8TXAMIOAZK/"
           "_users/code_BAlkUKkpKNVI_VBV9XFNBFEZcFiw5Qx0O/w10/karty_kursow/mbm_en_st_i.pdf")
GRADO = "Mechanical Engineering and Machine Building (I level, full-time)"
UNIV = "Wroclaw University of Science and Technology - Faculty of Mechanical Engineering"
KIND = {"obligatory": "obligatoria", "optional": "optativa", "university-wide": "obligatoria"}


def pages_text(path: Path) -> list[str]:
    with pdfplumber.open(path) as pdf:
        return [(pg.extract_text() or "") for pg in pdf.pages]


def parse_cards(txts: list[str]) -> list[dict]:
    starts = [i for i, t in enumerate(txts) if "SUBJECT CARD" in t[:80]]
    cards = []
    for k, i in enumerate(starts):
        end = (starts[k + 1] if k + 1 < len(starts) else len(txts)) - 1
        h = txts[i]
        g = lambda pat: (re.search(pat, h).group(1).strip() if re.search(pat, h) else "")  # noqa: E731
        code = re.match(r"[A-Za-z0-9._/-]+", g(r"Subject code: (.*)"))
        ects_line = g(r"Number of ECTS points ([\d .]+)\n")
        cards.append({
            "name": g(r"Name in English: (.*)") or g(r"Name in Polish: (.*)"), "code": code.group() if code else "",
            "kind": g(r"Kind of subject: (.*)"), "ects": sum(float(x) for x in ects_line.split()) if ects_line else None,
            "field": g(r"Main field of study.*?: (.*)"), "level": g(r"Level and form of studies: (.*)"), "p0": i + 1, "p1": end + 1})
    return cards


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    txts = pages_text(c.get_file(PDF_URL))
    cards = parse_cards(txts)
    entries, seen = [], {}
    for cd in cards:
        if not cd["code"]:
            continue
        code = cd["code"]
        if code in seen:  # mismo código repetido: se desambigua con la página
            code = f"{code}_p{cd['p0']}"
        seen[code] = 1
        entries.append(CatalogEntry(
            universidad=UNIV, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=cd["name"],
            curso_semestre="n/d (la ficha no indica curso)", curso=None, semestre=None, creditos_ects=cd["ects"],
            caracter="tfg" if re.search(r"thesis", cd["name"], re.I) else KIND.get(cd["kind"].lower(), cd["kind"].lower() or None), idioma_pagina="en", url_guia_docente=PDF_URL,
            tipo_fuente="pdf_compartido", paginas_pdf=f"{cd['p0']}-{cd['p1']}"))
    tot = sum(e.creditos_ects or 0 for e in entries)
    bad = [e.codigo_asignatura for e in entries if not e.creditos_ects]
    meta = CatalogMeta(
        universidad=UNIV, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/2027", url_plan_estudios=PDF_URL, ects_totales_plan=None,
        estrategia_fuente="PDF compartido de fichas de asignatura (SUBJECT CARD) con texto; una ficha por rango de páginas", generado_por="discover_ec_pl_wroclaw02.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Mechanical Engineering and Machine Building, I level (bachelor), full-time, en inglés, W10 PWr (en el ámbito del convenio: la más próxima a Mecánica; "
               f"el PDF 'mech_en_st_i' es Mechatronics y no se usa). {len(entries)} fichas; suma ECTS {tot:g} (incluye optativas alternativas y fichas de varios itinerarios/especializaciones; "
               f"el plan completo no se publica aquí: no hay curso/semestre ni ECTS totales verificables). Fichas sin ECTS legible: {bad or 'ninguna'}. "
               "El PDF es la oferta de fichas de la facultad para el grado (puede no cubrir todo el plan)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "fichas; ECTS", tot, "sin ects:", bad)


if __name__ == "__main__":
    main()
