#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Πανεπιστήμιο Ιωαννίνων (University of Ioannina), Computer Science and Engineering (grado, 240 ECTS).

Fuentes (inglés, cse.uoi.gr, robots permite todo con Crawl-delay 10): dos PDF compartidos de 2025-26 con los
«Course outlines» de grado: obligatorias (core, 124 págs.) y optativas (elective, 85 págs.). El índice (págs. 2-3)
da código, título y página inicial de cada ficha (la página impresa coincide con la del PDF).

Uso: python universidades/ec_g_ioannin01/discover_ec_g_ioannin01.py
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
SLUG = "ec_g_ioannin01"
UNIVERSIDAD = "University of Ioannina (Πανεπιστήμιο Ιωαννίνων)"
BASE = "https://www.cse.uoi.gr/wp-content/uploads/2025/09/"
PDFS = [("core", BASE + "2025-26_CSE-UOI_proptyxiaka-perigrammata_core-courses_EN.pdf"),
        ("elective", BASE + "2025-26_CSE-UOI_proptyxiaka-perigrammata_elective-courses_EN.pdf")]
PLAN = "https://www.cse.uoi.gr/"
GRADO = "Computer Science and Engineering (Diploma, 4 years / 240 ECTS, undergraduate programme)"
GREEK = str.maketrans({"Μ": "M", "Υ": "Y", "Ε": "E", "Ι": "I", "Κ": "K", "Η": "H", "Ν": "N", "Τ": "T", "Ο": "O", "Ρ": "P", "Χ": "X", "Α": "A", "Β": "B", "Ζ": "Z"})
TOC = re.compile(r"^(M[YE]\w*\d+)\.?\s+(.+?)\s*\.{3,}\s*(\d+)\s*$")


def toc(pages: list[str]) -> list[tuple[str, str, int]]:
    rows = []
    prev = ""
    for t in pages[1:3]:
        for ln in t.split("\n"):
            s = (prev + " " + ln.strip()).strip() if prev else ln.strip()
            s = s.translate(GREEK)
            m = TOC.match(s)
            if m:
                rows.append((m.group(1), m.group(2).strip(), int(m.group(3))))
                prev = ""
            else:
                prev = ln.strip() if "..." not in ln and not re.match(r"^Undergraduate", ln) else ""
    return rows


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    entries, seen = [], set()
    for kind, url in PDFS:
        with pdfplumber.open(http.get_file(url)) as d:
            pages = [(p.extract_text() or "") for p in d.pages]
        rows = toc(pages)
        assert len(rows) > 20, (kind, len(rows))
        for k, (code, title, start) in enumerate(rows):
            end = (rows[k + 1][2] - 1) if k + 1 < len(rows) else len(pages)
            txt = "\n".join(pages[start - 1:end])
            if "COURSE OUTLINE" not in txt:
                raise AssertionError(f"{code}: p.{start} no es una ficha")
            sem = re.search(r"SEMESTER\s+(\S+)", txt)
            sem_s = sem.group(1) if sem else ""
            semn = int(re.match(r"\d+", sem_s).group()) if re.match(r"\d+", sem_s) else None
            ects = None
            ls = txt.split("\n")
            for i, ln in enumerate(ls[:50]):
                if "total credits" in ln:
                    for nx in ls[i + 1:i + 3]:
                        m = re.search(r"(\d+(?:[.,]\d+)?)\s*$", nx.strip())
                        if m and not nx.startswith("Add rows"):
                            ects = float(m.group(1).replace(",", "."))
                            break
                    break
            low = title.lower()
            car = "tfg" if "thesis" in low else "optativa" if kind == "elective" else "obligatoria"
            if code in seen:
                continue
            seen.add(code)
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
                curso_semestre=f"Semester {sem_s or 'n/a'} / {kind} / A.Y. 2025-26",
                curso=((semn + 1) // 2) if semn and semn <= 10 else None, semestre=semn if semn and semn <= 10 else None,
                creditos_ects=ects, caracter=car, idioma_pagina="en", url_guia_docente=url,
                tipo_fuente="pdf_compartido", paginas_pdf=f"{start}-{end}"))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/26",
        url_plan_estudios=PLAN, ects_totales_plan=240.0,
        estrategia_fuente="Dos PDF compartidos en inglés (core y elective) con índice (código, título, página) y una ficha 'COURSE OUTLINE' por asignatura.",
        generado_por="discover_ec_g_ioannin01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Única fila Erasmus de Ioannina: Programa de Doctorado en Energía y Control de Procesos (ISCED 0719): no existe equivalente de grado industrial/mecánico en esta tanda. "
               "Se elige Computer Science and Engineering (Escuela de Ingeniería, diploma de 4 años = 240 ECTS (8 semestres; el código MYY802 es del semestre 8)) por tener fichas de grado completas en inglés; "
               "no se exploraron otros departamentos (p. ej. Materials Science and Engineering, más cercano a energía/procesos) por falta de fichas en inglés localizadas en el presupuesto. "
               "Semestre = el de la ficha (>=6 en optativas -> curso None); ECTS leídos de la tabla de horas/créditos de cada ficha (pueden ser decimales). "
               "La lengua de impartición es el griego; las fichas están en inglés. Los ECTS 'ofertados' incluyen optativas, por eso superan los de un itinerario."))
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(entries)} asignaturas ({sum(e.caracter == 'optativa' for e in entries)} optativas); HTTP {http.stats}")


if __name__ == "__main__":
    main()
