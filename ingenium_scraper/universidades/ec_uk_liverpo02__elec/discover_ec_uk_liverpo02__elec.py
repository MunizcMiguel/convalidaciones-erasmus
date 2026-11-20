"""Fase 1 - LJMU - BEng (Hons) Electrical and Electronic Engineering (Programme Specification KIS 32118-BGH, prodcat.ljmu.ac.uk). Modulos por nivel desde el texto del PDF; fichas en coursecatalogue.ljmu.ac.uk/module/2025/{code}.
Uso: python universidades/ec_uk_liverpo02__elec/discover_ec_uk_liverpo02__elec.py"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_uk_liverpo02__elec"
UNIVERSIDAD = "Liverpool John Moores University"
GRADO = "BEng (Hons) Electrical and Electronic Engineering"
URL_SPEC = "https://prodcat.ljmu.ac.uk/KIS/32118-BGH.pdf"
LEVELS = (4, 5, 6)
ECTS_TOTAL = 180.0
NIVEL = "bachelor"
TOK = re.compile(r"Level (\d) (Core|Optional)|\[MODULE\] (\d{4}[A-Z]{3,5}) (.*?) Approved [\d.]+ - (\d+) credit")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    with pdfplumber.open(c.get_file(URL_SPEC)) as pdf:
        t = " ".join(re.sub(r"\s+", " ", p.extract_text() or "") for p in pdf.pages)
    entries, seen, lvl, kind = [], set(), None, None
    for m in TOK.finditer(t):
        if m.group(1):
            lvl, kind = int(m.group(1)), m.group(2)
            continue
        code, title, cr = m.group(3), m.group(4).strip(), int(m.group(5))
        if lvl not in LEVELS or code in seen or title.startswith(("Sandwich Year", "Study Year Abroad")):
            continue
        seen.add(code)
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
            curso_semestre=f"Level {lvl} ({kind.lower()})", curso=lvl - 3, semestre=None, creditos_ects=cr / 2,
            caracter="obligatoria" if kind == "Core" else "optativa", idioma_pagina="en",
            url_guia_docente=f"https://coursecatalogue.ljmu.ac.uk/module/2025/{code}", tipo_fuente="html"))
    core = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel=NIVEL, curso_academico="2025-26 (Programme Specification 2022.01)", url_plan_estudios=URL_SPEC,
        ects_totales_plan=ECTS_TOTAL, estrategia_fuente="Programme Specification PDF (prodcat.ljmu.ac.uk, texto): módulos por nivel core/optional + fichas CourseLoop",
        generado_por="discover_ec_uk_liverpo02__elec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=('BEng (Hons) Electrical and Electronic Engineering de LJMU (3 años, 360 créditos UK = 180 ECTS): electrónica digital/analógica, máquinas y sistemas de potencia, instrumentación y control, proyecto.' + f" {len(entries)} módulos, core {core:g} ECTS equiv. (créditos UK/2). Año de prácticas y de estudio en el extranjero no catalogados. Fichas: coursecatalogue.ljmu.ac.uk (robots Allow /), mismo scraper que ec_uk_liverpo02. Idioma: inglés."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({e.codigo_asignatura for e in entries}) == len(entries)
    print(len(entries), "módulos; core", core)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.curso_semestre)


if __name__ == "__main__":
    main()
