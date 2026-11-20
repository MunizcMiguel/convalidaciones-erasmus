"""Fase 1 - Hochschule Osnabrueck - Bachelor Elektrotechnik (B.Sc., StO 2025, Stand 26.03.2026).

Fuente: Modulhandbuch PDF oficial (www.hs-osnabrueck.de/fileadmin/Modulhandbuch/BET/...): 67 fichas de modulo (catalogo del grado, con
Verwendbarkeit por titulacion), sin Studienverlaufsplan (semestre = null). Uso: python universidades/ec_d_osnabru02__elec/discover_ec_d_osnabru02__elec.py
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
SLUG = "ec_d_osnabru02__elec"
UNIVERSIDAD = "Hochschule Osnabrück"
GRADO = "Elektrotechnik (B.Sc.)"
URL_PLAN = "https://www.hs-osnabrueck.de/fileadmin/Modulhandbuch/BET/StO2025_Stand2026-08-20_Elektrotechnik.pdf"
FOOT = re.compile(r"^HOCHSCHULE OSNABRÜCK \| MODULHANDBUCH \d+$")
IDIOMA = {"deutsch": "de", "englisch": "en"}


def page_lines(pdf):
    out = []
    for i, pg in enumerate(pdf.pages, 1):
        for l in unicodedata.normalize("NFC", pg.extract_text(x_tolerance=1.5) or "").split(chr(10)):
            if not FOOT.match(l.strip()):
                out.append((i, l))
    return out


def modules(lines):
    starts = [j for j, (_, l) in enumerate(lines) if l.strip() == "Allgemeine Informationen zum Modul"]
    first_page = lines[starts[0]][0]
    toc = {re.sub(r"\s+", " ", l.strip()).upper(): l.strip() for pg, l in lines if 2 <= pg < first_page - 0 and l.strip() and l.strip() != "Inhaltsverzeichnis"}
    mods, prev_end = [], next(j for j, (pg, _) in enumerate(lines) if pg == first_page)
    for n, j in enumerate(starts):
        title_start = prev_end
        # ultima linea "Zurueck zum Inhaltsverzeichnis" antes de j (para n>0)
        if n:
            k = j
            while not lines[k][1].startswith("Zurück zum Inhaltsverzeichnis"):
                k -= 1
            title_start = k + 1
        block = [l.strip() for _, l in lines[title_start:j] if l.strip()]
        upper = [l for l in block if l == l.upper() and re.search(r"[A-ZÄÖÜ]", l)]
        key = re.sub(r"\s+", " ", " ".join(upper)).strip()
        title = toc.get(key.upper()) or key.title()
        en = " ".join(l for l in block if l not in upper)
        end = j
        while end < len(lines) and not lines[end][1].startswith("Zurück zum Inhaltsverzeichnis"):
            end += 1
        info = {}
        for _, l in lines[j:j + 14]:
            for lab in ("Modulkennung", "Unterrichtssprache", "ECTS-Leistungspunkte und Benotung"):
                if l.startswith(lab):
                    info[lab] = l[len(lab):].strip()
        mods.append(dict(start=title_start, hdr=j, end=end, page=lines[title_start][0] if block else lines[j][0], endpage=lines[min(end, len(lines) - 1)][0],
                         title=title, en=en, code=info["Modulkennung"], lang=info.get("Unterrichtssprache", "Deutsch"),
                         ects=float(info["ECTS-Leistungspunkte und Benotung"])))
    return mods


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    with pdfplumber.open(c.get_file(URL_PLAN)) as pdf:
        lines = page_lines(pdf)
    mods = modules(lines)
    entries, seen = [], set()
    for m in mods:
        assert m["code"] not in seen, m["code"]
        seen.add(m["code"])
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=m["code"], nombre_asignatura=m["title"],
            curso_semestre="semestre no indicado en el handbook", curso=None, semestre=None, creditos_ects=m["ects"],
            caracter="tfg" if m["title"].startswith("Bachelorarbeit") else None, idioma_pagina=IDIOMA.get(m["lang"].lower().split()[0], "de"),
            url_guia_docente=URL_PLAN, tipo_fuente="pdf_compartido", paginas_pdf=f"{m['page']}-{m['endpage']}"))
    total = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26 (StO 2025, Stand 26.03.2026)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0,
        estrategia_fuente="PDF compartido (Modulhandbuch Bachelor Elektrotechnik, alemán/inglés): una ficha por módulo con 'Modulkennung'",
        generado_por="discover_ec_d_osnabru02__elec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Grado: Elektrotechnik B.Sc. (StO 2025, Stand 20.08.2026; segunda titulación afín: familia eléctrica/electrónica, distinta de Maschinenbau) (Hochschule Osnabrück, Fakultät IuI; 6 sem. = 180 ECTS; Mechatronik tiene otro PDF y no se cataloga). "
               f"{len(entries)} módulos, {total:g} ECTS brutos: el handbook es un catálogo de módulos con Wahlpflichtmodule y módulos compartidos con otras titulaciones, no un plan por semestres; "
               "sin Studienverlaufsplan en el PDF (semestre/curso = null; no se distingue obligatorio/optativo). Código = Modulkennung (11Bnnnn). Idioma por módulo (Unterrichtssprache). "
               "Nombres de docentes («Am Modul beteiligte Personen») se eliminan en la Fase 2."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos, ECTS bruto", total)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.idioma_pagina, e.paginas_pdf)


if __name__ == "__main__":
    main()
