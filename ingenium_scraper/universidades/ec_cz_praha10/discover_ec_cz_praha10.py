"""Fase 1 (segunda pasada) - ČVUT Praga, Fac. Ingeniería Mecánica (FS, f2): OFERTA Erasmus en inglés de la facultad.
Fuente: Bílá kniha (HTML estático, sin robots.txt). Los planes de grado salen vacíos, así que no se ata al grado: se toman los cursos de
/en/f2-predmety.html con idioma English y ficha con contenido (Synopsis/Syllabus/Objective/Materials/Requirements). Sin nivel (grado/máster) en la fuente.
Uso: python universidades/ec_cz_praha10/discover_ec_cz_praha10.py
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
SLUG = "ec_cz_praha10"
BASE = "https://bilakniha.cvut.cz/en/"
UNI = "Czech Technical University in Prague - Faculty of Mechanical Engineering"
GRADO = "Oferta Erasmus+ en inglés de la Fac. de Ingeniería Mecánica (sin plan de grado atado)"
CONTENT = ("Synopsis:", "Syllabus of lectures:", "Syllabus of tutorials:", "Study Objective:", "Study materials:", "Requirements:")


def has_content(html: str) -> bool:
    s = BeautifulSoup(html, "lxml")
    dd = {dt.get_text(strip=True): d.get_text(strip=True) for dt, d in zip(s.select("dl dt"), s.select("dl dd"))}
    return any(dd.get(k) for k in CONTENT)


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(BASE + "f2-predmety.html"), "lxml")
    rows = []
    for tr in s.select("table tr"):
        a = tr.find("a", href=re.compile(r"^predmet"))
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if a and len(tds) > 6 and tds[4] == "English":
            rows.append((tds, a["href"]))
    entries, vacias, seen = [], 0, set()
    for i, (t, href) in enumerate(rows):
        code = t[0]
        if code in seen:
            continue
        seen.add(code)
        try:
            ok = has_content(c.get_text(BASE + href))
        except Exception as ex:  # noqa: BLE001
            print("ERR", code, ex)
            continue
        if not ok:
            vacias += 1
            continue
        try:
            ects = float(t[6])
        except ValueError:
            ects = None
        entries.append(CatalogEntry(universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=t[1],
                                    curso_semestre=f"n/d ({t[3]})", creditos_ects=ects, idioma_pagina="en",
                                    url_guia_docente=BASE + href, tipo_fuente="html"))
        if i % 50 == 0:
            print(i, len(rows), len(entries), flush=True)
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/2027", url_plan_estudios=BASE + "f2-predmety.html",
        ects_totales_plan=None, estrategia_fuente="Bílá kniha: lista de cursos de la facultad f2 filtrada a English con ficha con contenido",
        generado_por="discover_ec_cz_praha10.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"NO es un plan de grado: Bílá kniha publica los planes de Bachelor of Mechanical Engineering vacíos (<ul></ul>) y el archivo da 404, "
               f"así que no se puede atar de forma determinista al grado. Se trata como la oferta Erasmus+ en inglés de la facultad (igual que Ostrava): "
               f"{len(rows)} cursos English de /en/f2-predmety.html (impartidos por varios departamentos de FS, no solo Mecánica; sin distinción grado/máster), "
               f"de los que {len(entries)} tienen ficha con contenido y {vacias} están vacíos y se omiten. Sin curso/semestre. ECTS de la lista. "
               "Hay que revisar a mano qué cursos son de 1.er ciclo y afines a Mecánica antes de usarlos para convalidar."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("filas", len(entries), "vacias", vacias, "de", len(rows))


if __name__ == "__main__":
    main()
