"""Fase 1 - LJMU - MEng (Hons) Mechanical Engineering (Level 7 / master-level modules) (Programme Specification KIS 32120-MG, prodcat.ljmu.ac.uk). Modulos por nivel desde el texto del PDF; fichas en coursecatalogue.ljmu.ac.uk/module/2025/{code}.
Uso: python universidades/ec_uk_liverpo02__m_mec/discover_ec_uk_liverpo02__m_mec.py"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_uk_liverpo02__m_mec"
UNIVERSIDAD = "Liverpool John Moores University"
GRADO = "MEng (Hons) Mechanical Engineering (Level 7 / master-level modules)"
URL_SPEC = "https://prodcat.ljmu.ac.uk/KIS/32120-MG.pdf"
LEVELS = (7,)
ECTS_TOTAL = 60.0
NIVEL = "master"
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
        generado_por="discover_ec_uk_liverpo02__m_mec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=('Máster integrado MEng Mechanical Engineering de LJMU (4 años, 480 créditos UK); se catalogan los módulos de nivel 7 (año de máster: core 80 + 40 créditos UK de optativas). Los niveles 4-6 coinciden con el BEng ya extraído.' + f" {len(entries)} módulos, core {core:g} ECTS equiv. (créditos UK/2). Año de prácticas y de estudio en el extranjero no catalogados. Fichas: coursecatalogue.ljmu.ac.uk (robots Allow /), mismo scraper que ec_uk_liverpo02. Idioma: inglés."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({e.codigo_asignatura for e in entries}) == len(entries)
    print(len(entries), "módulos; core", core)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.curso_semestre)


if __name__ == "__main__":
    main()
