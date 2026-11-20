#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Università di Napoli Federico II, Laurea in Ingegneria Elettronica (L-8).

Fuente: «Guida dello Studente» (PDF compartido, A.A. 2022/23) del CdS en ingegneria-elettronica.dieti.unina.it,
que incluye las 32 «Schede dell'insegnamento». El catálogo Cineca de unina no publica fichas (testiTotali vacío).

Uso: python universidades/ec_i_napoli01/discover_ec_i_napoli01.py
"""
from __future__ import annotations

import difflib
import io
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_napoli01"
UNIVERSIDAD = "Università degli Studi di Napoli Federico II"
PDF_URL = "https://ingegneria-elettronica.dieti.unina.it/images/allegati/GdS_-_Laurea_-_2022-23.pdf"
GRADO = "Laurea in Ingegneria Elettronica (L-8, Classe delle lauree in Ingegneria dell'informazione)"
ROMAN = {"I": 1, "II": 2, "III": 3}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def slugify(s: str) -> str:
    return norm(s).replace(" ", "_")


def pdf_pages(http: PoliteClient) -> list[str]:
    data = http.get_bytes(PDF_URL)
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        return [(p.extract_text() or "") for p in pdf.pages]


def find_schede(pages: list[str]) -> list[dict]:
    starts = []
    for i, t in enumerate(pages):
        if t.lstrip().startswith("SCHEDA DELL'INSEGNAMENTO"):
            lines = [l.strip() for l in t.split("\n") if l.strip()]
            name = lines[1].strip('"“”«»\u2018\u2019\ufffd ').strip()
            starts.append((i + 1, name, t))
    out = []
    for k, (p, name, t) in enumerate(starts):
        end = starts[k + 1][0] - 1 if k + 1 < len(starts) else len(pages)
        anno = re.search(r"ANNO DI CORSO[^:\n]*:\s*(I{1,3})\b", t)
        sem = re.search(r"SEMESTRE[^:\n]*:\s*(I{1,2})\b", t)
        cfu = re.search(r"CFU:\s*(\d+(?:[.,]\d+)?)", t)
        ssd = re.search(r"SSD\s+([A-Z\-]+/\d+)", t)
        out.append(dict(ini=p, fin=end, name=name, anno=anno and ROMAN[anno.group(1)], sem=sem and ROMAN[sem.group(1)],
                        cfu=cfu and float(cfu.group(1).replace(",", ".")), ssd=ssd and ssd.group(1)))
    return out


def obligatory_block(pages: list[str]) -> str:
    plan = pages[3] + "\n" + pages[4]
    a = plan.index("I anno")
    b = plan.index("Tabella A:")
    return norm(plan[a:b])


def is_in_block(name: str, block: str) -> bool:
    n = norm(name)
    if n in block:
        return True
    L = len(n)
    best = max((difflib.SequenceMatcher(None, n, block[i:i + L]).ratio() for i in range(0, max(1, len(block) - L))), default=0)
    return best >= 0.85


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pages = pdf_pages(http)
    schede = find_schede(pages)
    block = obligatory_block(pages)
    entries = []
    for s in schede:
        assert s["anno"] and s["cfu"], f"Faltan año/CFU en {s['name']}"
        oblig = is_in_block(s["name"], block)
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO,
            codigo_asignatura=slugify(s["name"]),
            nombre_asignatura=s["name"].title().replace("Iot", "IoT").replace("Computer Systems", "Computer Systems"),
            curso_semestre=f"Anno {s['anno']} / Semestre {s['sem'] or 'n.d.'} / A.A. 2022-23" + ("" if oblig else " / a scelta (Tabella A/B)"),
            curso=s["anno"], semestre=(s["anno"] - 1) * 2 + s["sem"] if s["sem"] else None,
            creditos_ects=s["cfu"], caracter="obligatoria" if oblig else "optativa", idioma_pagina="it",
            url_guia_docente=PDF_URL, tipo_fuente="pdf_compartido", paginas_pdf=f"{s['ini']}-{s['fin']}",
        ))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes)), "duplicados"
    ob = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="A.A. 2022/23 (Guida dello Studente publicada)",
        url_plan_estudios=PDF_URL, ects_totales_plan=180.0,
        estrategia_fuente="PDF compartido (Guida dello Studente del CdS): cada «SCHEDA DELL'INSEGNAMENTO» empieza en una página detectada por el script; año/semestre/CFU/SSD salen de la propia ficha; obligatoria/optativa se decide contrastando el nombre con el Manifesto (Piano di Studi, pp. 4-5).",
        generado_por="discover_ec_i_napoli01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Laurea triennale en Ingegneria Elettronica (L-8; Napoli no ofrece laurea 'industrial' como tal; la más afín a Electrónica Industrial y Automática de las filas Erasmus: EIA/Eléctrica/Química industrial/Máster Industrial; alternativas existentes: Ingegneria Elettrica DE4 y Automazione e Robotica DE2, de nueva implantación sin guías). "
               "El catálogo Cineca de unina (unina.coursecatalogue.cineca.it) lista el plan pero las fichas vienen vacías (testiTotali []), y la ficha pública vive en docenti.unina.it (no comprobada/JS). Se usa el PDF oficial de la Guida dello Studente del A.A. 2022/23: es la versión más reciente con schede que se localizó (no hay certeza de que el plan 2025/26 sea idéntico). "
               f"{len(entries)} schede = 17 obligatorias del plan + optativas de Tabla A/B; no hay código oficial: codigo_asignatura = slug del nombre. "
               f"No hay ficha de Lingua inglese, Laboratorio CAD, Prova finale ni tirocinio. Suma ECTS de obligatorias con ficha = {ob:g} de 180 (faltan los 15 CFU libres, 18 CFU de optativas de Tabla A, lengua, lab CAD y prueba final)."),
    )
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    for e in entries:
        print(e.curso, e.semestre, e.creditos_ects, e.caracter, e.paginas_pdf, e.codigo_asignatura)
    print(len(entries), "filas; ECTS obligatorias", ob, http.stats)


if __name__ == "__main__":
    main()
