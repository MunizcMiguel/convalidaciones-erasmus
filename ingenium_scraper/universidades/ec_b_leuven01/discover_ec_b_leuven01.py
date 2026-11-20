"""Fase 1 - KU Leuven (Fac. Engineering Science) - Bachelor in de ingenieurswetenschappen (programa 2024-25 o posterior, 180 sp.).
Fuente: programa del onderwijsaanbod (HTML) + una ficha /syllabi/{n|e}/<codigo> por OPO (misma plataforma que Thomas More). Idioma: neerlandes o ingles segun el curso.
Uso: python universidades/ec_b_leuven01/discover_ec_b_leuven01.py
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_b_leuven01"
UNI = "KU Leuven - Faculty of Engineering Science"
GRADO = "Bachelor in de ingenieurswetenschappen (Bachelor of Engineering Science, Leuven)"
URL_PLAN = "https://onderwijsaanbod.kuleuven.be/opleidingen/e/SC_57861104"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    entries, seen, tot = [], set(), {}
    for tr in s.select("tr.module-row"):
        a = tr.select_one("td.module-title a[href]")
        cr = tr.select_one("td.stage-credits strong")
        if not a or not cr:
            continue
        m = re.search(r"/syllabi/([ne])/([A-Za-z0-9_]+)$", a["href"])
        if not m:
            continue
        code = m.group(2)[:-1]
        lang = "en" if m.group(1) == "e" else "nl"
        if code in seen:
            continue
        seen.add(code)
        fases = [int(x) for x in re.findall(r"\d", tr.get("data-fases", ""))]
        stage_txt = " ".join(x.get("data-text", "") for x in tr.select("td.stage [data-text]"))
        obl = "Verplicht" in stage_txt
        fase = fases[0] if fases else None
        try:
            ects = float(cr.get_text(strip=True).replace(",", "."))
        except ValueError:
            ects = None
        if obl and ects and len(fases) == 1:
            tot[fase] = tot.get(fase, 0) + ects
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=a.get_text(" ", strip=True),
            curso_semestre=f"Fase {fase}" if fase else "Fase ?", curso=fase, semestre=None, creditos_ects=ects,
            caracter="obligatoria" if obl else "optativa", idioma_pagina=lang, url_guia_docente=a["href"], tipo_fuente="html"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML del programa (onderwijsaanbod.kuleuven.be) + ficha HTML por opleidingsonderdeel (/syllabi/{n|e}/<codigo>)",
        generado_por="discover_ec_b_leuven01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Excel: Máster Ing. Telecomunicación (ISCED 0714, 2 plazas) en la Faculty of Engineering Science. KU Leuven no ofrece Ingeniería Mecánica como grado separado: "
               "el grado de ingeniería (1.er ciclo) es el Bachelor in de ingenieurswetenschappen (180 sp., académico, en neerlandés; fase 1 común, fases 2-3 con "
               "hoofdrichting/afstudeerrichting y minors: werktuigkunde, elektrotechniek, computerwetenschappen, bouwkunde, chemie, materialen, biomedisch). Es el único afín; "
               "el Bachelor of Engineering Technology es un grado profesional distinto (no elegido). El programa mezcla todas las orientaciones (148 filas), "
               "'obligatoria' = 'Verplicht in fase' (puede ser obligatoria solo de una orientación); fase = curso. "
               f"Obligatorias de una sola fase por fase: {tot}. Cada ficha en el idioma de impartición (las /e/ en inglés, el resto neerlandés; el HTML trae ambas traducciones). "
               "Se elimina el profesorado. robots.txt veta /archief, /pdf y años anteriores, no /syllabi/n|e."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas", tot)


if __name__ == "__main__":
    main()
