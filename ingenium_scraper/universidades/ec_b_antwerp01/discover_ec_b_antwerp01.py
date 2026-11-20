"""Fase 1 - Universiteit Antwerpen - Bachelor of Electronics and ICT Engineering Technology (180 ECTS, Fac. Applied Engineering).
Fuente: pagina 'Study programme' (HTML, 2026-27, 3 model paths). Las fichas por curso (?id=...) NO se sirven con contenido (misma pagina) -> parcial.
Uso: python universidades/ec_b_antwerp01/discover_ec_b_antwerp01.py
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_b_antwerp01"
UNI = "Universiteit Antwerpen"
GRADO = "Bachelor of Electronics and ICT Engineering Technology"
URL_PLAN = "https://www.uantwerpen.be/en/study/programmes/all-programmes/electronics-ict-engineering-programmes/bachelor/study-programme/"


def field(sec, label):
    for sp in sec.select("div.spec"):
        lab = sp.select_one("div.label")
        if lab and lab.get_text(strip=True).rstrip(":") == label:
            return sp.select_one("div.value").get_text(" ", strip=True)
    return None


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    root = s.select_one("div.managedContent")
    year, part, kind, entries, seen = None, None, None, [], set()
    for el in root.find_all(["h3", "h4", "section"]):
        if el.name == "h3":
            txt = el.get_text(" ", strip=True)
            if re.fullmatch(r"\d{4}-\d{4}", txt):
                year, part = txt, None
            m = re.match(r"Model Path part (\d)", txt)
            if m:
                part = int(m.group(1))
        elif el.name == "h4" and not el.find_parent("section", class_="course"):
            kind = el.get_text(" ", strip=True) or kind
        elif el.name == "section" and "course" in el.get("class", []) and year == "2026-2027":
            code = field(el, "Course code")
            h5 = el.select_one("h5")
            if not code or not h5 or code in seen:
                continue
            seen.add(code)
            name = re.sub(r"^\d+-", "", h5.get_text(" ", strip=True)).strip()
            sem = re.match(r"(\d)E", field(el, "Semester") or "")
            sem = int(sem.group(1)) if sem else None
            e = field(el, "ECTS-credits")
            lang = (field(el, "Language of instruction") or "").lower()
            optional = bool(kind and re.search(r"Minor|Option|Elective", kind, re.I))
            entries.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=f"Model path part {part} / {'sem ' + str(sem) if sem else 'sem ?'} / {kind or ''}".strip(), curso=part,
                semestre=((part - 1) * 2 + sem) if part and sem else None, creditos_ects=float(re.match(r"[0-9.,]+", e).group(0).replace(",", ".")) if e and re.match(r"[0-9.,]+", e) else None,
                caracter="optativa" if optional else "obligatoria", idioma_pagina={"dutch": "nl", "english": "en"}.get(lang, "nl"),
                url_guia_docente=None, tipo_fuente="sin_guia"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML del programa de estudios (uantwerpen.be, 'Model Path' parts 1-3, 2026-27)",
        generado_por="discover_ec_b_antwerp01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Excel: Grado en Ingeniería en Tecnologías y Servicios de Telecomunicación (2 plazas, sin web de información). La titulación más afín en UAntwerpen es el "
               "Bachelor of Electronics and ICT Engineering Technology (Fac. Applied Engineering, Groenenborger, 180 ECTS, impartido en neerlandés; hay también "
               "'Industrial Sciences: Electronics-ICT' y ofertas Engineering Sciences). PARCIAL: la página del programa lista código, semestre, ECTS e idioma de cada curso, pero la "
               "ficha detallada (enlace ?id=2026-CÓDIGO&lang=en) devuelve la misma página del programa sin contenidos (se probó con PoliteClient; el detalle parece cargarse por "
               "JavaScript), por lo que las filas son 'sin_guia' y no hay Fase 2. robots.txt de www.uantwerpen.be permite todo. "
               "Se incluyen solo los cursos del curso 2026-27; los minors se marcan optativos; 'curso' = Model Path part (1-3)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS suma", sum(e.creditos_ects or 0 for e in entries))


if __name__ == "__main__":
    main()
