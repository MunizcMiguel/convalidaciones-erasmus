"""Fase 1 - Gdynia Maritime University (PL GDYNIA01) - B.Sc. Electrotechnics (Faculty of Marine Electrical Engineering), courses in English.
Fuente: dos PDF oficiales de la facultad (fall / summer semester) en umg.edu.pl/en/courses: «PROGRAMME of STUDIES, B.Sc., Section: Electrotechnics»,
con titulo, ECTS, semestre del plan y descripcion de cada asignatura (pdf_compartido).
Uso (desde la raiz): python universidades/ec_pl_gdynia01/discover_ec_pl_gdynia01.py
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
from common.util import safe_name  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_gdynia01"
UNIVERSIDAD = "Gdynia Maritime University (Akademia Morska w Gdyni)"
GRADO = "B.Sc. Electrotechnics (Faculty of Marine Electrical Engineering)"
PDFS = {
    "fall": "https://umg.edu.pl/en/sites/default/files/2025-12/electrical_engineering-fall_semester-2025.pdf",
    "summer": "https://umg.edu.pl/en/sites/default/files/2025-12/electrical_engineering-summer_semester-2025.pdf",
}
URL_PLAN = "https://umg.edu.pl/en/courses"
TITLE_RE = re.compile(r"^(?P<t>[A-Z][^\n]*?)\s+(?P<ects>\d+)\s+(?P<sem>\d)$")
NOISE = re.compile(r"^(MARINE ELECTRICAL ENGINEERING FACULTY|RN \d\d-\d\d.*|PROGRAMME of STUDIES|Faculty of Marine.*|B\.Sc\. Programme|Section: .*|"
                   r"Fall \(winter\) semester|Summer semester|\(.*\d{4}.*\)|\(September-January\)|\(February-June\)|ECTS Sem\.?|Course title/description( ECTS sem)?|points|BD \d.*)$")


def parse_pdf(path: Path) -> list[dict]:
    """Devuelve [{title, ects, sem, desc, page}] en orden."""
    items: list[dict] = []
    with pdfplumber.open(path) as pdf:
        for pno, page in enumerate(pdf.pages, start=1):
            for line in (page.extract_text() or "").splitlines():
                line = line.strip()
                if not line or NOISE.match(line):
                    continue
                m = TITLE_RE.match(line)
                if m and not line.startswith("Description") and (not items or items[-1]["desc"] != "" or True):
                    items.append({"title": m["t"].strip(), "ects": int(m["ects"]), "sem": int(m["sem"]), "desc": "", "page": pno})
                elif items:
                    items[-1]["desc"] += (" " if items[-1]["desc"] else "") + line
    for it in items:
        it["desc"] = re.sub(r"^Description:?\.?\s*", "", it["desc"]).strip()
    return items


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    rows, seen = [], set()
    for term, url in PDFS.items():
        items = parse_pdf(http.get_file(url))
        for it in items:
            code = "UMG-" + safe_name(it["title"]).upper()
            if code in seen:
                code += f"_{term}"
            seen.add(code)
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=it["title"],
                curso_semestre=f"Semester {it['sem']} ({term})", curso=(it["sem"] + 1) // 2, semestre=it["sem"],
                creditos_ects=float(it["ects"]), caracter="obligatoria", idioma_pagina="en", url_guia_docente=url,
                tipo_fuente="pdf_compartido", paginas_pdf=f"{it['page']}-{it['page']}"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2025-2026",
        url_plan_estudios=URL_PLAN, ects_totales_plan=None,
        estrategia_fuente="Dos PDF de la facultad (fall/summer) con título, ECTS, semestre y descripción por asignatura",
        generado_por="discover_ec_pl_gdynia01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: B.Sc. Electrotechnics (Faculty of Marine Electrical Engineering): el Excel pide Ing. Eléctrica / Electrónica "
               "Industrial y Automática (grado) y másteres; es la única titulación eléctrica de primer ciclo de la universidad con oferta en inglés "
               "(la Faculty of Marine Engineering y Navigation son mecánica naval/náutica). "
               "El PDF 'courses in English' es un resumen: título, ECTS (del semestre, sin el desglose del plan completo), semestre del plan (1-7) y una descripción corta; "
               "no hay resultados de aprendizaje, evaluación ni bibliografía. Código = 'UMG-' + slug del título (sin código oficial). "
               "ECTS totales del plan no verificables (el PDF lista solo los cursos ofrecidos en inglés). "
               f"Suma ECTS={total:g}. Páginas PDF: la del bloque de cada asignatura (puede continuar en la siguiente)."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(len(rows), "asignaturas; ECTS", total)


if __name__ == "__main__":
    main()
