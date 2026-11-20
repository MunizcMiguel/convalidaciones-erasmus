"""Fase 1 - UCLouvain - Bachelor in Engineering (Ingenieur civil, FSA1BA), catalogo oficial en ingles (programa por bloque anual).
Uso: python universidades/ec_b_louvain01/discover_ec_b_louvain01.py
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_b_louvain01"
UNI = "Université catholique de Louvain (UCLouvain)"
GRADO = "Bachelor in Engineering (Bachelier en sciences de l'ingénieur, orientation ingénieur civil) - FSA1BA"
URL_PLAN = "https://uclouvain.be/en-prog-2025-fsa1ba-programme_annual_blocks"
COURSE = "https://uclouvain.be/en-cours-2025-{code}"
CODE = re.compile(r"^[A-Z]{4,5}\d{4}[A-Z]?$")


def parse_program(html: str) -> list[dict]:
    s = BeautifulSoup(html, "lxml")
    m = s.find("main") or s.body
    for z in m(["script", "style", "nav"]):
        z.decompose()
    lines = [l for l in m.get_text("\n", strip=True).split("\n") if l.strip()]
    block, kind, out = None, None, []
    i = 0
    while i < len(lines):
        l = lines[i]
        mb = re.match(r"(\d)(?:st|nd|rd|th) annual unit", l)
        if mb:
            block = int(mb.group(1))
        elif re.match(r"(Obligatory|Mandatory) Courses|Compulsory", l, re.I):
            kind = "obligatoria"
        elif re.match(r"(Optional|Elective)|Options?\b|Minor|Focus|Major", l, re.I) and len(l) < 80:
            kind = "optativa"
        if CODE.match(l) and i + 5 < len(lines):
            j = i + 1
            title = lines[j]; lang = lines[j + 1]
            q = lines[j + 2]; hrs = lines[j + 3]
            cr = re.match(r"([\d.,]+)\s*$", lines[j + 4])
            if cr is None and re.match(r"[\d.,]+", lines[j + 4]):
                cr = re.match(r"([\d.,]+)", lines[j + 4])
            if cr and re.match(r"(q\d|.*q\d)", q, re.I):
                out.append(dict(code=l, title=title, lang=lang, q=q, hrs=hrs, ects=float(cr.group(1).replace(",", ".")), block=block, kind=kind or "obligatoria"))
                i = j + 4
        i += 1
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    rows, seen = parse_program(c.get_text(URL_PLAN)), set()
    entries = []
    for r in rows:
        if r["code"] in seen:
            continue
        seen.add(r["code"])
        q = re.search(r"q(\d)", r["q"], re.I)
        bloc = r["block"] or None
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=r["code"], nombre_asignatura=r["title"],
            curso_semestre=f"Bloque anual {bloc} / {r['q']}" if bloc else r["q"], curso=bloc, semestre=None, creditos_ects=r["ects"],
            caracter=r["kind"], idioma_pagina="en", url_guia_docente=COURSE.format(code=r["code"].lower()), tipo_fuente="html"))
    tot = sum(e.creditos_ects or 0 for e in entries if e.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML estático del programa por bloque anual (uclouvain.be, en inglés) + una ficha HTML por UE",
        generado_por="discover_ec_b_louvain01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Excel (UCLouvain): solo Máster Ing. Industrial / Grado Org. Industrial (ISCED 0410), 2+0 plazas. Se elige el Bachelor in Engineering (FSA1BA, ingeniero civil, 180 ECTS), "
               f"único grado de ingeniería generalista afín a Industrial/Mecánica (la Mecánica se especializa en el máster). Las {len(entries)} UE listadas suman {tot:g} ECTS (>180 porque la 3.ª "
               "bloque incluye UE alternativas/de elección que el parser etiqueta como obligatorias; no se distinguen con fiabilidad). Los bloques anuales son 1.º-3.º. "
               "El idioma de las fichas: inglés (las UE se imparten en francés salvo indicación). Se omite el profesorado."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS obligatorios", tot)


if __name__ == "__main__":
    main()
