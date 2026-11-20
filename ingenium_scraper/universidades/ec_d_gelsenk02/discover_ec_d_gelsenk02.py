"""Fase 1 - Westfaelische Hochschule Gelsenkirchen - Bachelor Maschinenbau (B.Eng.), Modulhandbuch Stand 15.11.2024.

Fuente: PDF compartido del Fachbereich Maschinenbau, Umwelt- und Gebaeudetechnik (www.w-hs.de), enlazado desde la pagina de Modulhandbuecher del
Pruefungsamt. La edicion 2026-10-01 (Reakkreditierung) lleva los titulos de modulo como imagen (sin texto) y no se usa.
Uso: python universidades/ec_d_gelsenk02/discover_ec_d_gelsenk02.py
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
SLUG = "ec_d_gelsenk02"
UNIVERSIDAD = "Westfälische Hochschule Gelsenkirchen"
GRADO = "Maschinenbau (B.Eng.)"
URL_PLAN = "https://www.w-hs.de/hochschule/fachbereiche/maschinenbau-umwelt-und-gebaeudetechnik/der-fachbereich/pruefungsamt-maschinenbau/modulhandbuecher/"
PDF_URL = "https://www.w-hs.de/fileadmin/Oeffentlich/Fachbereich-1/Studiengaenge/MB_BA/1A_ModulhandbuchBachelorMB_2024.11.15"
FOOT = re.compile(r"^WHS FB1 .*Stand 15\.11\.2024 \d+$")
CODE = re.compile(r"^(.+?) (\d+) h (\d+) ECTS")


def page_lines(pdf):
    out = []
    for i, pg in enumerate(pdf.pages, 1):
        for l in unicodedata.normalize("NFC", pg.extract_text(x_tolerance=1.5) or "").split(chr(10)):
            if not FOOT.match(l.strip()):
                out.append((i, l))
    return out


def modules(lines):
    mods = []
    for j, (pg, l) in enumerate(lines):
        if not l.startswith("Kennnummer Workload"):
            continue
        title = lines[j - 1][1].strip()
        if title == "Modulbeschreibungen":
            title = lines[j - 2][1].strip()
        for k in range(j + 1, j + 4):
            m = CODE.match(lines[k][1].strip())
            if m:
                break
        else:
            raise RuntimeError(f"cabecera sin codigo en pag {pg}")
        sem_line = lines[k + 1][1].strip()
        ms = re.search(r"(?:^|Ab dem )(\d+)\.?\s", sem_line)
        mods.append(dict(idx=j - 1 if lines[j - 1][1].strip() != "Modulbeschreibungen" else j - 2, hdr=j, page=pg, title=title,
                         code=m.group(1).strip(), wl=int(m.group(2)), cr=int(m.group(3)), sem=int(ms.group(1)) if ms else None, sem_line=sem_line))
    return mods


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    c.get_text(URL_PLAN)
    with pdfplumber.open(c.get_file(PDF_URL)) as pdf:
        npag = len(pdf.pages)
        lines = page_lines(pdf)
    mods = modules(lines)
    entries, seen = [], set()
    for n, m in enumerate(mods):
        if n + 1 < len(mods):
            nx = mods[n + 1]
            end = nx["page"] if lines[nx["idx"] - 1][0] == nx["page"] else nx["page"] - 1
        else:
            end = npag
        end = max(end, m["page"])
        assert m["code"] not in seen, m["code"]
        seen.add(m["code"])
        caracter = "tfg" if m["title"].startswith("Bachelorarbeit") else ("practicas" if m["title"].startswith("Praxisphase") else None)
        sem = m["sem"] if m["sem"] and m["sem"] <= 8 else None
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=m["code"], nombre_asignatura=m["title"],
            curso_semestre=m["sem_line"], curso=(sem + 1) // 2 if sem else None, semestre=sem, creditos_ects=float(m["cr"]), caracter=caracter,
            idioma_pagina="de", url_guia_docente=PDF_URL, tipo_fuente="pdf_compartido", paginas_pdf=f"{m['page']}-{end}"))
    total = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2024-25 (Modulhandbuch Stand 15.11.2024)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0,
        estrategia_fuente="PDF compartido (Modulhandbuch Bachelor Maschinenbau, alemán): una ficha por módulo con tabla 'Kennnummer Workload Credits'",
        generado_por="discover_ec_d_gelsenk02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Grado: Maschinenbau B.Eng. (Fachbereich Maschinenbau, Umwelt- und Gebäudetechnik, Institut für Maschinenbau; grundständig 6 sem. = 180 ECTS, también variantes duales/Teilzeit de 8 sem. en el mismo PDF). "
               f"{len(entries)} módulos, {total:g} ECTS brutos (incluye módulos optativos/de itinerario: el plan exige 180). Código = Kennnummer (abreviatura, p. ej. TM1). 'Studiensemester' del handbook = semestre del grado grundständig "
               "(null donde pone otra cosa). caracter solo se marca para tfg/practicas: el PDF no distingue obligatorio/optativo en la ficha. Existe una edición 2026-10-01 (Reakkreditierung, plan nuevo) con los títulos "
               "de módulo como imagen sin texto (no extraíble sin OCR): no catalogada. Los módulos de «winweb.w-hs.de» (sistema antiguo) no responden desde esta red y no se usaron."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos, ECTS bruto", total)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.semestre, e.paginas_pdf)


if __name__ == "__main__":
    main()
