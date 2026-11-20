"""Fase 1 - Universitatea din Petrosani (UPET), Facultatea de Inginerie Mecanica si Electrica.
Grado: Tehnologia constructiilor de masini (Machine building technology), licenta 4 anos/240 ECTS, dominio Inginerie industriala:
es el programa mas proximo a Ingenieria Mecanica de la facultad (el resto: Mining machinery and equipment, Electromechanical, ...).
Fuente: plan de invatamant PDF (www.upet.ro/documente/planuri/ime/2025/TCM.pdf), enlazado desde /en/bachelor-programs/.
Las fichas de disciplina estan en carpetas de SharePoint (upet-my.sharepoint.com), cuyo robots.txt las veta -> todas sin_guia; sin Fase 2.
Uso: python universidades/ec_ro_petrosa01/discover_ec_ro_petrosa01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_ro_petrosa01"
UNIVERSIDAD = "Universitatea din Petroșani - Faculty of Mechanical and Electrical Engineering"
GRADO = "Tehnologia construcțiilor de mașini (Machine building technology), licență"
URL_PLAN = "https://www.upet.ro/documente/planuri/ime/2025/TCM.pdf"
URL_PROG = "https://www.upet.ro/en/bachelor-programs/"
URL_FISE = "https://upet-my.sharepoint.com/:f:/g/personal/site_upet_ro/EsVsp9v2_gdGrXYiOC11i78BRi4_Rht7Q51co01x5bFfWQ?e=SKAQnH"
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4}
TIPO = {"DF": "fundamental", "DS": "de especialidad", "DC": "complementaria"}


def num(x):
    try:
        return float(str(x).replace(",", "."))
    except ValueError:
        return None


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    try:
        c.get_text(URL_FISE)
        sp = "accesible (revisar)"
    except RobotsBlocked:
        sp = "BLOQUEADO por robots.txt"
    except FetchError as e:
        sp = f"no accesible ({str(e)[:60]})"
    entries, seen = [], set()
    with pdfplumber.open(c.get_file(URL_PLAN)) as pdf:
        for pg in pdf.pages:
            for t in pg.extract_tables():
                year = None
                for r in t:
                    if not r or len(r) < 21:
                        continue
                    m = re.fullmatch(r"ANUL ([IV]+)", (r[1] or "").strip())
                    if m:
                        year = ROMAN[m.group(1)]
                        continue
                    cm = re.search(r"\dBB\d[A-Z]{2}\d{2}", r[2] or "")
                    if not year or not cm or cm.group(0) in seen:
                        continue
                    code = cm.group(0)
                    seen.add(code)
                    c1, c2 = num(r[12]), num(r[13])
                    sem = (year - 1) * 2 + (1 if c1 is not None else 2)
                    cred = c1 if c1 is not None else c2
                    name = re.sub(r"\s+", " ", r[1] or "").strip()
                    if (r[2] or "").strip() != code:  # celda del nombre desbordada sobre la del codigo: se toma la linea del texto
                        ln = next((l for l in (pg.extract_text() or "").splitlines() if code in l), "")
                        mm = re.match(r"^\d+\s+(.+?)\s+" + code, ln)
                        name = mm.group(1) if mm else name
                    entries.append(CatalogEntry(
                        universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                        curso_semestre=f"Anul {year} / Semestrul {sem}", curso=year, semestre=sem, creditos_ects=cred,
                        caracter=("optativa" if re.search(r"opțion|opţion", name, re.I) else "obligatoria"),
                        idioma_pagina="ro", url_guia_docente=None, tipo_fuente="sin_guia"))
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/2026", url_plan_estudios=URL_PLAN,
        ects_totales_plan=240.0, estrategia_fuente="Plan de invatamant en PDF (tablas por año, pdfplumber extract_tables); fichas de disciplina fuera de alcance",
        generado_por="discover_ec_ro_petrosa01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Tehnologia construcțiilor de mașini (licență, 4 años, 240 ECTS, domeniu Inginerie industrială, Facultatea de Inginerie Mecanică și Electrică), el programa más cercano a Ingeniería Mecánica "
               f"(otras opciones de la facultad: Mining machinery and equipment, Electromechanical, Equipment for industrial processes). Plan 2025-2026, {len(entries)} disciplinas, suma de créditos {tot:g}. "
               f"PARCIAL: todas las filas son sin_guia. Las fișe ale disciplinelor están en carpetas SharePoint (upet-my.sharepoint.com): {sp}; sin acceso automatizado ni Fase 2. "
               "Códigos oficiales del plan (p. ej. 2BB1OF01 = facultad 2, ing. industrial B, TCM B, año/semestre, O=obligatoria, F/S/C=tipo, nº). Las disciplinas opcionales figuran con nombre genérico "
               "('Disciplina opţională OP 21'); las alternativas reales están en el anexo del plan. Las disciplinas facultativas (28 créditos extra) no se catalogan. Idioma del plan: rumano."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    by_y = {}
    for e in entries:
        by_y[e.curso] = by_y.get(e.curso, 0) + (e.creditos_ects or 0)
    print(len(entries), "filas; ECTS", tot, by_y, "sharepoint:", sp)


if __name__ == "__main__":
    main()
