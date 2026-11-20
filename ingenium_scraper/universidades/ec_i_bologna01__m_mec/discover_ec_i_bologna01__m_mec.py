"""Fase 1 (parcial) - Universita di Bologna - Laurea in Ingegneria meccanica (L-9, sede Bologna, CdS 0927).

Fuente: piano didattico oficial en corsi.unibo.it (HTML estatico). Las fichas (www.unibo.it, version EN/IT) existen, pero su URL
lleva un id interno que NO esta en el HTML del plan (la busqueda por codiceMateria es dinamica), asi que las filas quedan sin_guia.
Uso: python universidades/ec_i_bologna01__m_mec/discover_ec_i_bologna01__m_mec.py
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
SLUG = "ec_i_bologna01__m_mec"
UNIVERSIDAD = "Alma Mater Studiorum - Università di Bologna"
GRADO = 'Ingegneria meccanica (Laurea Magistrale, LM-33, Bologna)'
URL_PLAN = 'https://corsi.unibo.it/magistrale/IngegneriaMeccanica-Bologna/insegnamenti/piano/2026/6721/912/000/2026'
TIPO = {"A": "obligatoria", "B": "obligatoria", "C": "obligatoria", "D": "optativa", "E": "tfg", "F": "obligatoria", "S": "practicas"}
YEARS = {"Primo": 1, "Secondo": 2, "Terzo": 3}


SEARCH = "https://www.unibo.it/en/study/course-units-transferable-skills-moocs/course-unit-catalogue"


def resolve_id(c: PoliteClient, code: str) -> str | None:
    """codiceMateria -> URL de la ficha EN. La búsqueda se resuelve en servidor con annoAccademico=2024 + codiceCorso=0927
    (con 2025 devuelve vacío); el primer enlace course-unit/AAAA/id del resultado es la ficha."""
    for q in tuple(f"?codiceMateria={code}&annoAccademico={y}&codiceCorso=6721&single=True&search=True" for y in ('2026', '2025', '2024')):
        html = c.get_text(SEARCH + q)
        seen_u = []
        for m in re.finditer(r"course-unit-catalogue/course-unit/(\d{4})/(\d+)", html):
            u = f"{SEARCH}/course-unit/{m.group(1)}/{m.group(2)}"
            if u in seen_u:
                continue
            seen_u.append(u)
            h1 = BeautifulSoup(c.get_text(u), "lxml").find("h1")  # la ficha lleva «{código} - {título}»; una ficha de otro código = curso integrado, no vale
            if h1 and h1.get_text(strip=True).startswith(code + " "):
                return u
    return None


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    entries, seen = [], set()
    for h3 in s.find_all("h3"):
        m = re.match(r"(Primo|Secondo|Terzo) Anno", h3.get_text(" ", strip=True))
        if not m:
            continue
        year = YEARS[m.group(1)]
        # recorrer hasta el siguiente h3
        node = h3
        while True:
            node = node.find_next(["h3", "table"])
            if node is None or node.name == "h3":
                break
            for tr in node.select("tbody tr"):
                tds = tr.find_all("td")
                if len(tds) < 6:
                    continue
                code = tds[0].get_text(strip=True)
                title = re.sub(r"\s+", " ", tds[1].get_text(" ", strip=True)).strip()
                mm = re.match(r"^(\d{4,6})\s+(.*)$", title)
                if not code and mm:
                    code, title = mm.group(1), mm.group(2)
                cfu = tds[5].get_text(strip=True)
                if not code or not cfu or not re.fullmatch(r"\d+(?:[.,]\d+)?", cfu):
                    continue  # corsos integrados (C.I.) sin CFU propios / filas de cabecera
                key = (code, year)
                if key in seen:
                    continue
                seen.add(key)
                per = tds[2].get_text(strip=True)
                tipo = tds[3].get_text(strip=True)
                title = re.sub(r"\s*-\s*non attivo.*$", "", title)
                entries.append(CatalogEntry(
                    universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
                    curso_semestre=f"Curso {year} / periodo {per or 'n/d'}", curso=year,
                    semestre=(year - 1) * 2 + int(per) if per in ("1", "2") else None,
                    creditos_ects=float(cfu.replace(",", ".")), caracter=TIPO.get(tipo), idioma_pagina="it",
                    url_guia_docente=None, tipo_fuente="sin_guia"))
    miss = []
    for e in entries:
        u = resolve_id(c, e.codigo_asignatura)
        if u:
            e.url_guia_docente, e.tipo_fuente, e.idioma_pagina = u, "html", "en"
        else:
            miss.append(e.codigo_asignatura)
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/26", url_plan_estudios=URL_PLAN,
        ects_totales_plan=120.0, estrategia_fuente="HTML estático del piano didattico de corsi.unibo.it (tablas por curso)",
        nivel="master", generado_por="discover_ec_i_bologna01__m_mec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok" if not miss else "parcial",
        notas=('Titulación elegida (MÁSTER): Laurea Magistrale in Ingegneria meccanica (LM-33, Bologna, CdS 6721), 120 CFU, 2 años; se toma el currículo 912 del plan A.A. 2026/27 cohorte 2026 (hay otros currículos 913, B82, B83). Fichas EN de www.unibo.it por búsqueda codiceMateria+codiceCorso. CFU ofertados superan 120 por optativas.'
               f"{len(entries)} filas, {tot:g} CFU sumando obligatorias y optativas ofertadas (superan 180 por las optativas alternativas). "
               "Fichas EN en www.unibo.it/en/study/course-units-transferable-skills-moocs/course-unit-catalogue/course-unit/{AAAA}/{idInterno}; "
               "el idInterno se obtiene de la búsqueda por codiceMateria (HTML servido en servidor con annoAccademico=AAAA&codiceCorso=CdS). "
               f"Sin ficha encontrada: {', '.join(miss) or 'ninguna'}. Algunas fichas pueden seguir en italiano."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; CFU", tot)


if __name__ == "__main__":
    main()
