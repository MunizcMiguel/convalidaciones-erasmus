"""Fase 1 - TU Clausthal - Maschinenbau B.Sc. (6 semestres, 180 LP).

Fuente: Modulhandbuch del Bachelorstudiengang Maschinenbau (PDF compartido, Stand 13.06.2025, AFB 04.05.2021),
enlazado desde la pagina del grado en fakultaeten.tu-clausthal.de. Un modulo = bloque que empieza con la
tabla "1a. Modultitel (deutsch) / 1b. (englisch)". Uso: python universidades/ec_d_clausth01/discover_ec_d_clausth01.py
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
SLUG = "ec_d_clausth01"
UNIVERSIDAD = "Technische Universität Clausthal"
GRADO = "Maschinenbau (B.Sc.)"
URL_PLAN = "https://www.fakultaeten.tu-clausthal.de/fakultaet-fuer-ingenieur-und-wirtschaftswissenschaften/studium/bachelor-studiengaenge/maschinenbau"
PDF_URL = ("https://www.fakultaeten.tu-clausthal.de/fileadmin/Sites/Studiengaenge/Documents/Studiengaenge/Modulhandbuecher/"
           "Neu_in_2025-26/MHB_MB_B.Sc._13_06_2025.pdf")
SECTION_RX = re.compile(r"^(Studienrichtung .*|Wahlpflichtkatalog .*)$")


def slugify(s: str) -> str:
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def page_cells(pg):
    """Tablas de la pagina como filas de celdas [(texto, bbox)] (recorte por celda: extract_tables pierde texto desbordado)."""
    out = []
    for t in pg.find_tables():
        rows = {}
        for c in t.cells:
            txt = (pg.crop(c).extract_text(x_tolerance=1.5) or "").strip()
            rows.setdefault(round(c[1]), []).append((c[0], txt, c))
        out.append([[(x[1], x[2]) for x in sorted(rows[k])] for k in sorted(rows)])
    return out


def page_rows(pg):
    return [[[c[0] for c in r] for r in t] for t in page_cells(pg)]


def find_modules(pdf) -> list[dict]:
    """Un dict por modulo: pagina de inicio, titulo DE/EN, LP, idioma, seccion del handbook."""
    mods, section = [], "Pflichtmodule"
    for i, pg in enumerate(pdf.pages, 1):
        if i < 5:
            continue
        text = pg.extract_text(x_tolerance=1.5) or ""
        for l in text.split(chr(10)):
            if SECTION_RX.match(l.strip()) and "Wahlpflichtmodul" not in l:
                section = l.strip()
        if "1a. Modultitel (deutsch)" not in text:
            continue
        tabs = page_rows(pg)
        head = next(t for t in tabs if t and t[0] and t[0][0].startswith("1a. Modultitel"))
        de_c, en_c = [], []
        for r in head[1:]:
            if r and re.match(r"^[0-9]+[.]", r[0]):
                break
            if r and r[0]:
                t = r[0].replace(chr(10), " ")
                if de_c and t.startswith(de_c[-1]):
                    de_c[-1] = t
                else:
                    de_c.append(t)
            if len(r) > 1 and r[-1]:
                t = r[-1].replace(chr(10), " ")
                if en_c and t.startswith(en_c[-1]):
                    en_c[-1] = t
                else:
                    en_c.append(t)
        de = " ".join(de_c)
        en = " ".join(en_c)
        flat = [r for t in tabs for r in t]
        k = next(n for n, r in enumerate(flat) if r and r[0].startswith("6. Sprache"))
        row = [x.strip() for x in flat[k + 1] if x.strip()]
        lang = row[0]
        lp = next(x for x in row[1:] if re.fullmatch(r"\d+(?:[.,]\d+)?", x))
        mods.append(dict(page=i, de=de.strip(), en=en.strip(), lang=lang, lp=float(lp.replace(",", ".")), num="", section=section))
    return mods


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    c.get_text(URL_PLAN)  # pagina del grado (comprueba robots y origen del enlace)
    with pdfplumber.open(c.get_file(PDF_URL)) as pdf:
        npag = len(pdf.pages)
        mods = find_modules(pdf)
    entries, seen = [], set()
    for n, m in enumerate(mods):
        end = mods[n + 1]["page"] - 1 if n + 1 < len(mods) else npag
        code = m["num"] or slugify(m["de"])
        if code in seen:
            code += f"-{m['page']}"
        seen.add(code)
        sec = m["section"]
        if m["de"].startswith("Bachelorarbeit"):
            caracter = "tfg"
        elif m["de"].startswith("Industriepraktikum"):
            caracter = "practicas"
        elif sec.startswith("Wahlpflicht"):
            caracter = "optativa"
        else:
            caracter = "obligatoria"
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=m["de"],
            curso_semestre=f"{sec} (semestre no indicado en el handbook)", curso=None, semestre=None, creditos_ects=m["lp"],
            caracter=caracter, idioma_pagina="de", url_guia_docente=PDF_URL, tipo_fuente="pdf_compartido",
            paginas_pdf=f"{m['page']}-{end}"))
    assert len({e.codigo_asignatura for e in entries}) == len(entries)
    total = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26 (MHB Stand 13.06.2025)",
        url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="PDF compartido (Modulhandbuch Bachelor Maschinenbau, alemán): tablas pdfplumber por módulo (título DE/EN, LP, idioma)",
        generado_por="discover_ec_d_clausth01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Grado: Maschinenbau B.Sc. (AFB 2021; también existe un plan a tiempo parcial no catalogado). {len(entries)} módulos; suma bruta {total:g} LP > 180 porque incluye las tres "
               "Studienrichtungen alternativas (Allgemeiner Maschinenbau, Mechatronik, Biomechanik) y los catálogos Wahlpflicht (Maschinenbau / Industrieanwendung) de los que se elige parte. "
               "El handbook NO da semestre por módulo (solo el Modellstudienplan, un gráfico en otro PDF no analizado): curso/semestre = null. Los módulos no tienen código oficial en el PDF "
               "(campo 5 'Modulnummer' vacío): código = slug del título alemán. Idioma: alemán (títulos en inglés incluidos). Las guías incluyen bibliografía. "
               "paginas_pdf = páginas físicas del módulo."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos, LP bruto", total)
    for e in entries:
        print(e.codigo_asignatura, "|", e.creditos_ects, e.caracter, e.paginas_pdf)


if __name__ == "__main__":
    main()
