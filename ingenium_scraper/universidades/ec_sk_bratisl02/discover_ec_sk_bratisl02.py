#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Univerzita Komenského v Bratislave (FMFI), Bachelor Applied Informatics (AIN).

Fuente: PDF de fichas «Course descriptions» del sistema AIS2 (ais2.uniba.sk/repo2/.../informacnelisty/2025-2026/FMFI/EN/AIN.pdf, en inglés):
un PDF compartido con una ficha por asignatura (inicio de ficha = página con «COURSE DESCRIPTION» / «STATE EXAM DESCRIPTION»).

Uso: python universidades/ec_sk_bratisl02/discover_ec_sk_bratisl02.py
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
SLUG = "ec_sk_bratisl02"
UNIVERSIDAD = "Univerzita Komenského v Bratislave (Comenius University Bratislava)"
PDF = "https://ais2.uniba.sk/repo2/repository/default/ais/informacnelisty/2025-2026/FMFI/EN/AIN.pdf"
PLAN = "https://fmph.uniba.sk/en/studies/study-programmes/"
GRADO = "Bachelor Applied Informatics (1-AIN), Faculty of Mathematics, Physics and Informatics"
START = re.compile(r"^(COURSE DESCRIPTION|STATE EXAM DESCRIPTION)", re.M)


def parse_head(text: str) -> tuple[str, str]:
    m = re.search(r"Course ID:\s*Course title:\s*\n(\S+)\s+(.+)", text)
    if not m:
        raise ValueError("sin Course ID")
    return m.group(1).strip(), m.group(2).strip()


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    path = http.get_file(PDF)
    with pdfplumber.open(path) as d:
        pages = [(p.extract_text() or "") for p in d.pages]
    starts = [i for i, t in enumerate(pages) if START.match(t.strip())]
    entries, seen = [], {}
    for k, s in enumerate(starts):
        e = (starts[k + 1] if k + 1 < len(starts) else len(pages)) - 1
        txt = "\n".join(pages[s:e + 1])
        code, title = parse_head(pages[s])
        if code in seen:
            continue
        seen[code] = 1
        cr = re.search(r"Number of credits:\s*([\d.,]+)", txt)
        sem = re.search(r"Recommended semester:\s*([\d.,\s/-]+)", txt)
        sems = [int(x) for x in re.findall(r"\d+", sem.group(1))] if sem else []
        sem1 = sems[0] if sems else None
        up = title.lower()
        car = "tfg" if ("state exam" in up or "bachelor thesis" in up or "bsc thesis" in up) and "introduction" not in up else None
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
            curso_semestre=f"Recommended semester: {sem.group(1).strip() if sem else 'n/a'} / A.Y. 2025/26",
            curso=((sem1 + 1) // 2) if sem1 and 1 <= sem1 <= 6 else None, semestre=sem1 if sem1 and 1 <= sem1 <= 8 else None,
            creditos_ects=float(cr.group(1).replace(",", ".")) if cr else None, caracter=car, idioma_pagina="en",
            url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{s + 1}-{e + 1}"))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/26",
        url_plan_estudios=PLAN, ects_totales_plan=180.0,
        estrategia_fuente="PDF compartido (AIS2) con todas las fichas del programa: cabecera por ficha 'COURSE DESCRIPTION'; campos por etiqueta de texto.",
        generado_por="discover_ec_sk_bratisl02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Comenius no tiene facultad de ingeniería (industrial/mecánica). Filas Erasmus: Grado Ing. Tecnologías Industriales (2 plazas) y Org. Industrial, ambas ISCED 0410 (negocios). "
               "Se elige la única titulación técnica con fichas públicas en inglés: Bachelor Applied Informatics (FMFI, 1-AIN, 180 ECTS); la Facultad de Gestión (FM UK) ofrece Management pero no se localizaron sus fichas públicas en inglés. "
               "El PDF reúne TODAS las fichas del programa (obligatorias, optativas, idiomas, seminarios y examen estatal); el carácter obligatoria/optativa no consta en la ficha (caracter=None salvo examen estatal/tesis). "
               "Curso = ceil(semestre recomendado/2); los semestres listan varias opciones en algunas optativas (se toma el primero). Sin código ECTS oficial distinto del Course ID de AIS (FMFI.xxx/1-AIN-nnn/aa). "
               "robots.txt de ais2.uniba.sk responde 403 (RFC 9309: 4xx = sin restricciones) y los PDF se sirven con 200; si se considerase bloqueo habría que tratar la fuente como parcial. "
               "Idioma de impartición: eslovaco/inglés según ficha. Los ECTS ofertados superan 180 por incluir optativas y asignaturas de otros bloques."))
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(entries)} asignaturas, {sum(e.creditos_ects or 0 for e in entries):g} ECTS ofertados; HTTP {http.stats}")


if __name__ == "__main__":
    main()
