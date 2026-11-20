"""Fase 1 - University of Ruse "Angel Kanchev" - Bachelor Computer Aided Design in Mechanical and Instrument Engineering (4 anios, 240 ECTS).

La Facultad de Ingenieria Mecanica y de Fabricacion (FMME) de Ruse ofrece cuatro grados: Manufacturing Equipment and Technologies, Computer Aided
Design in Mechanical and Instrument Engineering, Materials Technology and Material Science e Industrial Engineering. El mas parecido a Ingenieria
Mecanica (titulo profesional "mechanical engineer": diseno de maquinas, resistencia de materiales, mecanismos, elementos de maquinas...) es Computer Aided
Design in Mechanical and Instrument Engineering.
Fuente: "Erasmus ECTS Information Package" de la FMME (PDF de 221 paginas, ingles): plan de estudios por terminos + descripcion de cada asignatura.
Uso: python universidades/ec_bg_rousse01__mec/discover_ec_bg_rousse01__mec.py
"""
from __future__ import annotations

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
SLUG = "ec_bg_rousse01__mec"
UNIVERSIDAD = "University of Ruse \"Angel Kanchev\""
GRADO = "Industrial Engineering (Bachelor)"
URL_PLAN = "https://www.uni-ruse.bg/en/education/students/ECTS-package"
PDF_URL = "https://www.uni-ruse.bg/en/education/students/ECTS%20packages/Faculty%20of%20Mechanical%20and%20Manufacturing%20Engineering.pdf"
TERMS = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5, "Sixth": 6, "Seventh": 7, "Eighth": 8}
CHROME = re.compile(r"^(Faculty of MME Erasmus ECTS Information Package|Erasmus ECTS Information Package Faculty of MME|\d{1,3})$")
HEADER = re.compile(r"^(\d{4}):? (\S.*)$")


def page_lines(pdf):
    out = []
    for i, pg in enumerate(pdf.pages, 1):
        for l in unicodedata.normalize("NFC", pg.extract_text(x_tolerance=1.5) or "").split(chr(10)):
            if not CHROME.match(l.strip()):
                out.append((i, l.rstrip()))
    return out


def descriptions(lines):
    """codigo -> dict(idx, end, page, endpage, title): primera descripcion del documento (las comunes se repiten entre grados)."""
    heads = [i for i, (_, l) in enumerate(lines) if HEADER.match(l) and i + 1 < len(lines) and re.search(r"credits:\s*\d", lines[i + 1][1])]
    out = {}
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        # una descripcion termina antes de una portada de grado ("OF A BACHELOR IN") u otras secciones
        for j in range(i + 1, end):
            if lines[j][1].strip() in ("OF A BACHELOR IN", "CURRICULUM") or lines[j][1].startswith("Career prospects"):
                end = j
                break
        code = HEADER.match(lines[i][1]).group(1)
        if code not in out:
            out[code] = dict(idx=i, end=end, page=lines[i][0], endpage=lines[end - 1][0], title=HEADER.match(lines[i][1]).group(2).strip(), ects_line=lines[i + 1][1])
    return out


def curriculum(pdf):
    """[(codigo, ects, termino)] de la tabla CURRICULUM del grado, leida por geometria (dos columnas: terminos impar/par)."""
    pages = []
    for i, pg in enumerate(pdf.pages):
        t = pg.extract_text(x_tolerance=1.5) or ""
        if "INDUSTRIAL ENGINEERING" in t and "MANUFACTURING" not in t and "CURRICULUM" in t and "First term" in t:
            pages.append(i)
    assert pages, "tabla CURRICULUM no encontrada"
    p0 = pages[0]
    out = []
    for i in range(p0, p0 + 2):  # la tabla ocupa dos paginas (cursos 1-3 y 4)
        pg = pdf.pages[i]
        mid = pg.width / 2
        ws = pg.extract_words(x_tolerance=1.5)
        heads = [(w["top"], w["x0"] < mid, TERMS[w["text"]]) for w in ws if w["text"] in TERMS and any(v["text"] == "term" and abs(v["top"] - w["top"]) < 2 for v in ws)]
        for w in ws:
            if not re.fullmatch(r"\d{4}", w["text"]) or w["text"] == "1102":
                continue
            left = w["x0"] < mid
            if w["x0"] > (95 if left else mid + 95):  # el codigo esta al inicio de la columna
                continue
            row = [v for v in ws if abs(v["top"] - w["top"]) < 2 and ((v["x0"] < mid) == left)]
            nums = [v for v in row if re.fullmatch(r"\d{1,2}", v["text"]) and v["x0"] > w["x0"] + 150]
            ects = float(nums[-1]["text"]) if nums else None
            term = [t for (top, isleft, t) in heads if isleft == left and top < w["top"]]
            out.append((w["text"], ects, term[-1] if term else None))
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    c.get_text(URL_PLAN)
    with pdfplumber.open(c.get_file(PDF_URL)) as pdf:
        lines = page_lines(pdf)
        cur = curriculum(pdf)
    desc = descriptions(lines)
    entries, seen = [], set()
    for code, ects, term in cur:
        if code in seen:
            continue
        seen.add(code)
        d = desc.get(code)
        title = d["title"] if d else None
        if not title:
            title = f"Course {code}"
        low = title.lower()
        caracter = "tfg" if "diploma work" in low else ("practicas" if "practice" in low else None)
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
            curso_semestre=f"Term {term}" if term else "Term n/d", curso=(term + 1) // 2 if term else None, semestre=term, creditos_ects=ects,
            caracter=caracter, idioma_pagina="en", url_guia_docente=PDF_URL if d else None, tipo_fuente="pdf_compartido" if d else "sin_guia",
            paginas_pdf=f"{d['page']}-{d['endpage']}" if d else None))
    total = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="Paquete ECTS de la FMME (datos 2008/09-posteriores; ver notas)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=240.0,
        estrategia_fuente="PDF compartido (Erasmus ECTS Information Package FMME, inglés): plan por términos (geometría de palabras) + descripciones por asignatura",
        generado_por="discover_ec_bg_rousse01__mec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Ruse no tiene un grado llamado Mechanical Engineering: la Facultad de Ingeniería Mecánica y de Fabricación ofrece 4 grados (Manufacturing Equipment and Technologies; Computer Aided Design in Mechanical and Instrument Engineering; "
               f"Materials Technology and Material Science; Industrial Engineering). Se elige el 2.º (titulación profesional «mechanical engineer»; diseño de máquinas, mecánica, resistencia, elementos de máquinas). Grado de 4 años = 8 términos = 240 ECTS "
               f"(no 180); {len(entries)} asignaturas, {total:g} ECTS brutos: las optativas de los grupos A/B (Mechanical vs Instrument Engineering, términos 6-7) son alternativas. Excluidos: Sports (código 1102, 1 h sin ECTS) y 'Elective Foreign Language' (sin código). "
               "Código = código oficial de 4 cifras. El paquete ECTS es antiguo (cifras de matrícula de 2008/09): el plan vigente puede diferir. Las descripciones se enlazan por código y se toma la primera del PDF (las asignaturas comunes se repiten entre grados). "
               "Idioma: inglés. Domain erasmus.uni-ruse.bg (hint del Excel) es solo el sitio Erasmus; los paquetes ECTS están en www.uni-ruse.bg."))
    assert len({e.codigo_asignatura for e in entries}) == len(entries)
    cat = Catalog(meta=meta, asignaturas=entries)
    cat.meta.notas = ("Segunda titulación de Ruse (familia mecánica/industrial), distinta de CAD in Mechanical and Instrument Engineering: Industrial Engineering de la FMME (4 años, 240 ECTS; mecánica, resistencia de materiales, termotecnia, tecnologías de fabricación, diseño de máquinas, mecatrónica, control). "
                      f"{len(entries)} asignaturas, {total:g} ECTS brutos (alternativas/optativas incluidas); sin descripción en el PDF: 4 (sin_guia). Mismo PDF y mismas reglas que ec_bg_rousse01. Excluidos Sports y Foreign Language sin código. Idioma: inglés. Paquete ECTS posiblemente desfasado.")
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "asignaturas, ECTS bruto", total, "; sin descripción:", sum(e.tipo_fuente == "sin_guia" for e in entries))
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.semestre, e.tipo_fuente, e.paginas_pdf)


if __name__ == "__main__":
    main()
