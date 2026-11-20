"""Fase 1 - FH JOANNEUM (Graz) - Bachelor Fahrzeugtechnik / Automotive Engineering (B.Sc. in Engineering, 6 sem., 180 ECTS).

FH JOANNEUM no tiene un grado de Ingenieria Mecanica en Graz (Department Engineering: Electronics and Computer Engineering, Aviation, Automotive
Engineering...); el mas afin es Fahrzeugtechnik (Mecanica, Termodinamica, Motores, CAD, Resistencia de materiales...).
Fuente: pagina de Curriculum en ingles (HTML, acordeon por semestre con codigo, ECTS, SWS, idioma y descripcion de cada asignatura).
Uso: python universidades/ec_a_graz09__mec/discover_ec_a_graz09__mec.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_a_graz09__mec"
UNIVERSIDAD = "FH JOANNEUM University of Applied Sciences (Graz)"
GRADO = "Luftfahrt / Aviation (B.Sc.)"
URL_PLAN = "https://www.fh-joanneum.at/luftfahrt/bachelor/en/my-studies/curriculum/"
TYPES = {"IL": "Lecture/Practical", "VO": "Lecture", "SE": "Seminar", "UE": "Exercise", "LB": "Laboratory", "PR": "Practical", "PT": "Project"}


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def parse(html: str):
    """Devuelve [{sem, code, title, kind, lang, ects, sws, anchor, soup_node}] en orden de documento."""
    s = BeautifulSoup(html, "lxml")
    out, sem = [], None
    for el in s.find_all(["h4", "button"]):
        if el.name == "h4":
            m = re.match(r"(\d+)(?:st|nd|rd|th) semester", clean(el.get_text()), re.I)
            if m:
                sem = int(m.group(1))
            continue
        if "course-item" not in (el.get("class") or []):
            continue
        head = clean(el.select_one(".course-item__header").get_text(" "))
        m = re.match(r"(.+?) \| (.+?) \| Coursecode: (\d+)$", head)
        if not m:
            raise RuntimeError("cabecera de curso no reconocida: " + head)
        title, kind, code = m.group(1), m.group(2), m.group(3)
        lang = clean((el.find("small") or el).get_text(" ")).replace("Language of instruction", "").strip()
        nums = [clean(h.get_text()) for h in el.select(".infos h5")]
        anchor = el.get("aria-controls")
        desc_node = s.find(id=anchor) if anchor else None
        out.append(dict(sem=sem, code=code, title=title, kind=kind, lang=lang, ects=float(nums[0]) if nums else None,
                        sws=nums[1] if len(nums) > 1 else None, anchor=anchor, desc=clean(desc_node.get_text(" ")) if desc_node else ""))
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    courses = parse(c.get_text(URL_PLAN))
    entries, seen = [], set()
    for k in courses:
        assert k["code"] not in seen, k["code"]
        seen.add(k["code"])
        low = k["title"].lower()
        caracter = "tfg" if "bachelor" in low and "thesis" in low and "exam" not in low else ("practicas" if "internship" in low else None)
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=k["code"], nombre_asignatura=k["title"],
            curso_semestre=f"Semester {k['sem']} (instrucción en {k['lang'] or 'n/d'})", curso=(k["sem"] + 1) // 2 if k["sem"] else None, semestre=k["sem"],
            creditos_ects=k["ects"], caracter=caracter, idioma_pagina="en", url_guia_docente=f"{URL_PLAN}#{k['anchor']}" if k["anchor"] else URL_PLAN,
            tipo_fuente="html" if k["desc"] else "sin_guia"))
    total = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="vigente (página consultada 2026-11)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0,
        estrategia_fuente="HTML estático: acordeón por semestre en la página de Curriculum (inglés); un bloque 'course-item' por asignatura con descripción breve",
        generado_por="discover_ec_a_graz09__mec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Segunda titulación del destino (familia mec; la primera es Fahrzeugtechnik): Luftfahrt / Aviation (B.Sc. in Engineering, Graz, 6 sem., 180 ECTS), la más afín a mecánica/aeronáutica tras Automotive (Aeronautical Engineering, Engineering Foundations, Technological Foundations). Los semestres 5-6 tienen itinerarios alternativos (Aviation Licenses / Aviation Industry), por eso la suma bruta supera 180 ECTS. {len(entries)} asignaturas, {total:g} ECTS. "
               "Parcial: la fuente publicada es la descripción breve (1-3 líneas de contenidos) de cada asignatura en la página del Curriculum; no hay guía docente completa (resultados de aprendizaje, evaluación, bibliografía) pública. "
               "Idioma de la ficha: inglés; la mayoría se imparten en alemán (indicado en curso_semestre). Código = Coursecode oficial. Solo existen datos de los 6 semestres tal como los lista la página; "
               "los semestres 5-6 incluyen prácticas (Internship) y Bachelor's Thesis."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "asignaturas, ECTS", total)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.semestre, e.tipo_fuente)


if __name__ == "__main__":
    main()
