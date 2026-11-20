"""Fase 1 - Thomas More (Sint-Katelijne-Waver, Mechelen-Antwerpen) - Bachelor Elektronica-ICT (professionele bachelor, 180 sp.).
Fuente: programa del onderwijsaanbod (HTML) + una ficha /syllabi/n/<codigo> por OPO. Idioma: neerlandes (algunas fichas /e/ en ingles).
Uso: python universidades/ec_b_mechele14/discover_ec_b_mechele14.py
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_b_mechele14"
UNI = "Thomas More Mechelen-Antwerpen (Sint-Katelijne-Waver)"
GRADO = "Bachelor Elektronica-ICT (Sint-Katelijne-Waver)"
URL_PLAN = "https://onderwijsaanbod.thomasmore.be/opleidingen/n/SC_51844890"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    entries, seen, tot = [], set(), {}
    for tr in s.select("tr.module-row"):
        a = tr.select_one("td.module-title a[href]")
        cr = tr.select_one("td.stage-credits strong")
        if not a or not cr:
            continue
        m = re.search(r"/syllabi/n/([A-Za-z0-9_]+)$", a["href"])
        if not m:
            continue
        code = re.sub(r"N$", "", m.group(1))
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
            caracter="obligatoria" if obl else "optativa", idioma_pagina="nl", url_guia_docente=a["href"], tipo_fuente="html"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML del programa (onderwijsaanbod.thomasmore.be) + ficha HTML por opleidingsonderdeel (/syllabi/n/<codigo>)",
        generado_por="discover_ec_b_mechele14.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Excel: Grado Electrónica Industrial y Automática (4 plazas) y Teleco (0). Thomas More no tiene Mecánica en este destino; se elige la professionele bachelor "
               "Elektronica-ICT de Sint-Katelijne-Waver (campus De Nayer, 180 sp.; el programa en inglés está en /archief y robots lo veta), la más afín a Electrónica Industrial. "
               "El programa lista fases 1-3 (curso = fase) con todas las tracks/optativas mezcladas; 'obligatoria' = marcada 'Verplicht in fase'. "
               f"Obligatorias por fase (solo las de una única fase): {tot}. Idioma: neerlandés (la base cita materiales en inglés). El profesorado se elimina. "
               "Los ECTS son los 'studiepunten' (1 sp. = 1 ECTS). robots.txt de onderwijsaanbod.thomasmore.be veta /archief y /pdf, no /syllabi."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas", tot)


if __name__ == "__main__":
    main()
