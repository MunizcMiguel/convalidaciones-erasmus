"""Fase 1 - VSB-Technical University of Ostrava, Faculty of Electrical Engineering and Computer Science (FEI) (FS).
No hay plan de estudios publico en ingles para el grado: la fuente oficial es el "Course catalogue for Erasmus+ students" de la FS
(JSF, HTML estatico). Se toman las asignaturas de nivel First Cycle (grado) del catalogo; no es el plan de un grado concreto.
Uso: python universidades/ec_cz_ostrava01__elec/discover_ec_cz_ostrava01__elec.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_cz_ostrava01__elec"
URL = "https://www.vsb.cz/en/study/exchange-students/erasmus-plus/courses/fei/"
GRADO = "ECTS course offer for Erasmus+ students - Faculty of Electrical Engineering and Computer Science (FEI) (first cycle courses)"
LANG = {"English": "en", "Czech": "cs"}


def attrs(html: str) -> dict:
    s = BeautifulSoup(html, "lxml")
    box = s.select_one("#ects")
    out = {}
    for th in box.select("th.subjectAttrsTitle"):
        td = th.find_next_sibling("td")
        out[th.get_text(" ", strip=True).rstrip(" *")] = re.sub(r"\s+", " ", td.get_text(" ", strip=True)) if td else ""
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL), "lxml")
    entries, seen, levels = [], set(), Counter()
    for a in s.find_all("a", href=re.compile("expandedSubjectId")):
        tds = a.find_parent("tr").find_all("td")
        code, name, cred, lang, sem = [t.get_text(" ", strip=True) for t in tds[:5]]
        url = urljoin(URL, a["href"])
        at = attrs(c.get_text(url))
        levels[at.get("Level of Course Unit", "?")] += 1
        if "First Cycle" not in at.get("Level of Course Unit", "") or code in seen:
            continue
        seen.add(code)
        yr = at.get("Year of Study", "")
        m = re.search(r"\d", yr)
        semn = [x.strip() for x in sem.split(",")]
        tipo = at.get("Type of Course Unit", "").lower()
        entries.append(CatalogEntry(
            universidad="VSB - Technical University of Ostrava, Faculty of Electrical Engineering and Computer Science (FEI)", nombre_grado=GRADO,
            codigo_asignatura=code, nombre_asignatura=name, curso_semestre=f"Año {yr or 'n/d'} / {sem}",
            curso=int(m.group()) if m and 1 <= int(m.group()) <= 6 else None, semestre=None,
            creditos_ects=float(cred), caracter="optativa" if "choice" in tipo or "optional" in tipo else ("obligatoria" if "compulsory" in tipo else None),
            idioma_pagina="en", url_guia_docente=url, tipo_fuente="html"))
        # nota: idioma_pagina es el de la ficha (inglés); la lengua de docencia puede ser checo
        if LANG.get(lang) == "cs":
            entries[-1].curso_semestre += " (docencia en checo)"
    meta = CatalogMeta(
        universidad="VSB - Technical University of Ostrava, Faculty of Electrical Engineering and Computer Science (FEI)", slug=SLUG, nombre_grado=GRADO, curso_academico="2026/2027",
        url_plan_estudios=URL, ects_totales_plan=None, estrategia_fuente="HTML del catálogo ECTS para Erasmus+ de la FS (JSF) + ficha por asignatura",
        generado_por="discover_ec_cz_ostrava01__elec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"No hay plan de estudios público en inglés del grado (la FS solo ofrece en inglés un catálogo ECTS para estudiantes de intercambio: {sum(levels.values())} fichas, "
               f"por nivel {dict(levels)}). Se incluyen las que incluyen First Cycle (también las mixtas First+Second Cycle) ({len(entries)}). Es la oferta de intercambio de la facultad, no el plan de Ingeniería Mecánica "
               "(Mechanical Engineering, bachelor en checo): no hay plan por cursos ni ECTS totales verificables. Año de estudio tal como lo declara la ficha (puede faltar). "
               "Las fichas son en inglés aunque algunas se impartan en checo."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas First Cycle de", sum(levels.values()), dict(levels))


if __name__ == "__main__":
    main()
