"""Fase 1 - Hochschule Bielefeld (HSBI) - Maschinenbau B.Eng. (Vollzeit/kooperativ, 7 semestres, 210 CP).

Fuente: "Studiengangspruefungsordnung und Modulhandbuch Bachelor Maschinenbau Version 2025" (PDF compartido): Anlage A = Studienplan por
Profilschwerpunkt; Anlage B = Modulhandbuch (una ficha por modulo con 'Kennnummer:'). Enlace tomado de la pagina de descargas del grado.
Uso: python universidades/ec_d_bielefe02/discover_ec_d_bielefe02.py
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_bielefe02"
UNIVERSIDAD = "Hochschule Bielefeld (HSBI)"
GRADO = "Maschinenbau (B.Eng.)"
URL_PLAN = "https://www.hsbi.de/studiengaenge/downloads/maschinenbau-bachelor"
SEMS = {"ERSTES": 1, "ZWEITES": 2, "DRITTES": 3, "VIERTES": 4, "FÜNFTES": 5, "SECHSTES": 6, "SIEBTES": 7}
PLAN_ROW = re.compile(r"^(\d{4})\s+(.+?)\s+[A-ZÄÖÜ0-9/]{1,10}\s+\d\s+\d\s+\d\s+\d\s+\d\s+(\d+)$")
HDR = re.compile(r"^(\d{4})\s+(\d+)\s+(\d+)\s+(.*)$")


def pdf_url(c: PoliteClient) -> str:
    t = c.get_text(URL_PLAN)
    for h in re.findall(r'href="([^"]+)"', t):
        h = html.unescape(h)
        if "bachelor-maschinenbau-version-2025" in h:
            return urljoin(URL_PLAN, h)
    raise RuntimeError("enlace del Modulhandbuch no encontrado")


def page_lines(pdf):
    return [(i, l) for i, pg in enumerate(pdf.pages, 1) for l in (pg.extract_text(x_tolerance=1.5) or "").split(chr(10))]


def plan_semesters(lines) -> dict[str, int]:
    """codigo de modulo -> primer semestre en el que aparece en alguno de los Studienplan (Anlage A)."""
    sem, out = None, {}
    for _, l in lines:
        if l.strip() == "Anlage B":
            break
        m = re.match(r"^(ERSTES|ZWEITES|DRITTES|VIERTES|FÜNFTES|SECHSTES|SIEBTES) SEMESTER", l)
        if m:
            sem = SEMS[m.group(1)]
            continue
        m = PLAN_ROW.match(l.strip())
        if m and sem:
            out[m.group(1)] = min(out.get(m.group(1), 9), sem)
    return out


def modules(lines):
    start = next(i for i, (_, l) in enumerate(lines) if l.strip() == "Anlage B")
    mods = []
    for j in range(start, len(lines) - 2):
        if lines[j + 1][1].startswith("Kennnummer:"):
            pass
        else:
            continue
        # el titulo es la linea previa (puede ocupar dos si es largo y no termina en abreviatura)
        title = lines[j][1].strip()
        pieces, idx = [title], j
        while len(pieces) < 3 and idx > 0:
            cur, prev = pieces[0], lines[idx - 1][1].strip()
            if cur[:1].islower() or re.fullmatch(r"[A-ZÄÖÜ0-9/]{1,10}", cur) or prev.endswith("-"):
                pieces.insert(0, prev)
                idx -= 1
            else:
                break
        pieces = [x for x in pieces if not re.fullmatch(r"[A-ZÄÖÜ0-9/]{1,10}", x)] if len(pieces) > 1 else pieces
        title = ""
        for x in pieces:
            title = title[:-1] + x if title.endswith("-") else (title + " " + x).strip()
        k = j + 2
        while k < j + 5 and not HDR.match(lines[k][1].strip()):
            k += 1
        m = HDR.match(lines[k][1].strip())
        mods.append(dict(idx=j, page=lines[j][0], title=title, code=m.group(1), wl=int(m.group(2)), cr=int(m.group(3)), rest=m.group(4)))
    return mods


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    url = pdf_url(c)
    with pdfplumber.open(c.get_file(url)) as pdf:
        npag = len(pdf.pages)
        lines = page_lines(pdf)
    mods = modules(lines)
    plan = plan_semesters(lines)
    entries, seen = [], set()
    for n, m in enumerate(mods):
        if n + 1 < len(mods):
            nx = mods[n + 1]
            end = nx["page"] if lines[nx["idx"] - 1][0] == nx["page"] else nx["page"] - 1
        else:
            end = npag
        end = max(end, m["page"])
        code = m["code"]
        assert code not in seen, code
        seen.add(code)
        name = re.sub(r"\s+[A-ZÄÖÜ][A-ZÄÖÜ0-9/]{1,9}$", "", m["title"]).strip()  # quita el kuerzel final (p. ej. 'DYN')
        sem = plan.get(code)
        if sem is None:
            ms = re.match(r"(\d)\. Semester", m["rest"])
            sem = int(ms.group(1)) if ms else None
        caracter = "tfg" if name.startswith("Bachelorarbeit") else ("obligatoria" if code in plan else "optativa")
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
            curso_semestre=(f"Semester {sem}" if sem else "Wahlpflicht (sin semestre fijo)"), curso=(sem + 1) // 2 if sem else None, semestre=sem,
            creditos_ects=float(m["cr"]), caracter=caracter, idioma_pagina="de", url_guia_docente=url, tipo_fuente="pdf_compartido",
            paginas_pdf=f"{m['page']}-{end}"))
    total = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26 (Version 2025)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=210.0,
        estrategia_fuente="PDF compartido (SPO + Modulhandbuch Bachelor Maschinenbau Version 2025, alemán); semestre desde el Studienplan (Anlage A), fichas desde Anlage B",
        generado_por="discover_ec_d_bielefe02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Grado: Maschinenbau B.Eng. Vollzeit/kooperativ de la HSBI (campus Bielefeld; existen además variantes praxisintegriert y berufsbegleitend en otros PDF, no catalogadas). "
               f"{len(entries)} módulos; suma bruta {total:g} CP > 210 porque el handbook incluye todos los Wahlpflichtmodule de los Profilschwerpunkte (Energietechnik, etc.) y módulos "
               "de otros itinerarios (p. ej. Berufspädagogik). Semestre = primer semestre del Studienplan (Anlage A) donde aparece el módulo; los no incluidos en el Studienplan se marcan optativa "
               "y sin semestre (se toma el que indique la ficha si lo hay). Código = Kennnummer oficial (4 dígitos). paginas_pdf = páginas físicas. Idioma: alemán."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos, CP bruto", total)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.semestre, e.caracter, e.paginas_pdf)


if __name__ == "__main__":
    main()
