"""Fase 1 (parcial) - Rzeszow University of Technology (PRz), Inzynieria mechaniczna, studia pierwszego stopnia (7 sem., 210 ECTS), cycle 2023/24.
Fuente: 'Program studiow' oficial (PDF, en polaco) en bip.prz.edu.pl; tabla de asignaturas por semestre (sec. 3.1). No hay guias docentes por
asignatura publicas localizadas (el PDF solo trae descripciones parciales de contenido), asi que todas las filas son sin_guia.
Solo se extraen las filas de plan completas en una linea (los nombres partidos en varias lineas / bloques optativos se omiten: ver notas).
Uso: python universidades/ec_pl_rzeszow01/discover_ec_pl_rzeszow01.py
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
SLUG = "ec_pl_rzeszow01"
URL = ("https://bip.prz.edu.pl/download/5LfDxsXGkfBBFcJVISJSgXL35qVUFHe3NpcVFHO2t7Z111OVxZdCVEO0IsZn54dDJjI2JvQ1x1S3Z1X3ApcWdgTnQvXEFpNVInTRZkfmJuJ2ojYmtuVm1_d08OKxctOi1Efig,"
       "5zShFZYVhZcAp1FV50U19RHlRNUChnR1FOVGNeCkBXWy0fTAcrGlk5Vw/53a_program_studiow_kierunek_inzynieria_mechaniczna_studia_i_stopnia_cykl_23_24.pdf")
GRADO = "Inżynieria mechaniczna (studia pierwszego stopnia, stacjonarne)"
UNIV = "Politechnika Rzeszowska (Rzeszow University of Technology)"
ROW = re.compile(r"^(\d) ([A-Z]{2}) (.+?) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) ([TN])$")


def slug(s: str) -> str:
    s = s.lower().translate(str.maketrans("ąćęłńóśźż", "acelnoszz"))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


ERASMUS_URL = ("https://dwm.prz.edu.pl/fcp/2GBUKOQtTKlQhbx08SlkTVgJQX2o8DAoHNiwFE1xVT29PFRYqCl5tDXdVGnoV/56/code_4DlgUIg9YPBJhAAQqEk1UB0FcAyQ/"
               "aktualnosci/przedmioty_erasmus/wbmil_aktualizacja_2026.pdf")
ERASMUS_PAGE = "https://dwm.prz.edu.pl/en/erasmus/student/courses-in-english"


def erasmus_rows(c: PoliteClient) -> list[dict]:
    """Oferta Erasmus (inglés) de la Facultad de Ingeniería Mecánica y Aeronáutica: tabla No./Subject/ECTS/Description/Remarks."""
    rows: list[dict] = []
    with pdfplumber.open(c.get_file(ERASMUS_URL)) as pdf:
        for pn, pg in enumerate(pdf.pages, 1):
            for t in pg.extract_tables():
                for r in t:
                    r = [(x or "").strip() for x in r] + [""] * 5
                    if r[0].isdigit():
                        rows.append(dict(no=int(r[0]), name=r[1], ects=r[2], desc=r[3], rem=r[4], p0=pn, p1=pn))
                    elif rows and any(r[:5]):
                        cur = rows[-1]
                        cur["p1"] = pn
                        cur["name"] = (cur["name"] + " " + r[1]).strip()
                        cur["desc"] = (cur["desc"] + "\n" + r[3]).strip()
                        cur["rem"] = (cur["rem"] + " " + r[4]).strip()
    return rows


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    with pdfplumber.open(c.get_file(URL)) as pdf:
        text = "\n".join((pdf.pages[i].extract_text() or "") for i in range(3, 5))
    text = text.split("3.2 Wykaz")[0]
    entries, omitidas, seen = [], 0, set()
    for l in text.split("\n"):
        m = ROW.match(l.strip())
        if not m:
            continue
        sem, unit, name = int(m.group(1)), m.group(2), m.group(3).strip()
        if name.count("(") != name.count(")") or name.startswith("(") or name[0].islower() or name.endswith("/"):
            omitidas += 1  # nombre partido en varias líneas: no se reconstruye
            continue
        ects = float(m.group(9))
        code = f"S{sem}-{slug(name)}"
        if code in seen:
            continue
        seen.add(code)
        entries.append(CatalogEntry(
            universidad=UNIV, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name, curso_semestre=f"Curso {(sem + 1) // 2} / semestre {sem}",
            curso=(sem + 1) // 2, semestre=sem, creditos_ects=ects, caracter="tfg" if "dyplomowa" in name.lower() and "seminarium" not in name.lower() else (
                "practicas" if "praktyka" in name.lower() else "obligatoria"), idioma_pagina="pl", url_guia_docente=None, tipo_fuente="sin_guia"))
    tot = sum(e.creditos_ects or 0 for e in entries)
    er = erasmus_rows(c)
    for r in er:
        nm = re.sub(r"\s+", " ", r["name"])
        m = re.match(r"^\d+(?:[.,]\d+)?", r["ects"])
        entries.append(CatalogEntry(
            universidad=UNIV, nombre_grado=GRADO, codigo_asignatura=f"ERA{r['no']:02d}-{slug(nm)}", nombre_asignatura=nm,
            curso_semestre="Oferta Erasmus en inglés WBMiL 2026 (sin curso/semestre)", curso=None, semestre=None,
            creditos_ects=float(m.group(0).replace(",", ".")) if m else None, caracter="optativa", idioma_pagina="en",
            url_guia_docente=ERASMUS_URL, tipo_fuente="pdf_compartido", paginas_pdf=f"{r['p0']}-{r['p1']}"))
    meta = CatalogMeta(
        universidad=UNIV, slug=SLUG, nombre_grado=GRADO, curso_academico="2023/24 (cycle 23/24)", url_plan_estudios=URL, ects_totales_plan=210.0,
        estrategia_fuente="PDF del programa de estudios (BIP PRz), tabla del plan sec. 3.1 con pdfplumber", generado_por="discover_ec_pl_rzeszow01.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Titulación: Inżynieria mechaniczna (Mechanical Engineering), grado de 7 semestres y 210 ECTS, en polaco (PRz no ofrece Mechanical Engineering BSc en inglés: "
               f"su oferta en inglés de grado es otra). Fuente: programa de estudios cycle 2023/24 (puede diferir del plan vigente 2026/27). {len(entries)} filas con ECTS suma {tot:g}; "
               f"se omiten {omitidas} filas con nombre partido en varias líneas, los bloques optativos (Przedmiot wybieralny...), los bloques temáticos de especialidad (3.2) y varias asignaturas "
               "con código de unidad en otra línea, por lo que la suma queda por debajo de 210. No se localizaron guías por asignatura públicas (karty przedmiotów): todas sin_guia, sin Fase 2. "
               "El PDF trae contenidos de algunas asignaturas pero no fichas completas. Las filas S{n}-... son el plan 23/24 (sin_guia). Además se añaden las filas ERAnn-... (pdf_compartido): oferta Erasmus en inglés 2026 de la Facultad de Ingeniería Mecánica y Aeronáutica (dwm.prz.edu.pl/fcp/..., robots permite; descripción breve + ECTS por asignatura; no es un plan por cursos, mezcla aeronáutica y mecánica, ECTS no suman 210). No hay portal público de sílabos completos de PRz."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS", tot, "omitidas", omitidas)


if __name__ == "__main__":
    main()
