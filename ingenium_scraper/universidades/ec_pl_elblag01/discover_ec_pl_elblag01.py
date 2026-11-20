"""Fase 1 - ANS Elbląg (Akademia Nauk Stosowanych w Elblągu / PWSZ Elbląg), Institute of Technology.
Grado: Mechanical Engineering (Mechanika i budowa maszyn, licencjat/inżynier).
Fuente: lista 'List of courses conducted in English' de study.ans-elblag.pl (HTML); cada fila enlaza a una ficha Word (.doc/.docx).
El plan completo en polaco está en USOSweb (usosweb.ans-elblag.pl), vetado por robots.txt -> catálogo PARCIAL.
Uso: python universidades/ec_pl_elblag01/discover_ec_pl_elblag01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_elblag01"
UNIVERSIDAD = "Akademia Nauk Stosowanych w Elblągu (University of Applied Sciences in Elbląg) - Institute of Technology"
GRADO = "Mechanical Engineering (Mechanika i budowa maszyn)"
URL_LISTA = "https://study.ans-elblag.pl/list-of-courses/"
BASE = "https://study.ans-elblag.pl/"  # la página declara <base href="https://study.ans-elblag.pl/">


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60]


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_LISTA), "lxml")
    entries, seen = [], set()
    for t in s.select("table.table"):
        for tr in t.find_all("tr"):
            tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            a = tr.find("a", href=True)
            if len(tds) < 5 or not a or "mechanical engineering" not in tds[2].lower():
                continue
            name = re.sub(r"\s*\(.*\)\s*$", "", tds[0]).strip()
            code = slugify(name)
            if code in seen:
                continue
            seen.add(code)
            sem = tds[1].lower()
            sem_n = 1 if sem == "winter" else 2 if sem == "summer" else None
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=f"{tds[1]} semester (curso no indicado) / {tds[3]} h", curso=None, semestre=None,
                creditos_ects=float(tds[4].replace(",", ".")), caracter=None, idioma_pagina="en",
                url_guia_docente=quote(urljoin(BASE, a["href"]), safe=":/"), tipo_fuente="html"))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    tot = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/2026", url_plan_estudios=URL_LISTA,
        ects_totales_plan=None, estrategia_fuente="HTML estático: tabla 'List of courses conducted in English' (Erasmus+) filtrada por 'Field of study' = mechanical engineering; fichas en Word (.doc/.docx)",
        generado_por="discover_ec_pl_elblag01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Grado: Mechanical Engineering (Mechanika i budowa maszyn, Instytut Politechniczny; especialidades Technology and Operation of Machines y 3D Modelling). "
               f"PARCIAL: solo las {len(entries)} asignaturas que la universidad ofrece en inglés a estudiantes Erasmus+ para 'mechanical engineering' (suma {tot:g} ECTS; "
               "una, Sustainable Development, es compartida con Civil Engineering). No es el plan completo ni se conoce el curso/semestre absoluto (solo winter/summer). "
               "El plan de estudios completo y las fichas en polaco están en USOSweb (usosweb.ans-elblag.pl), cuyo robots.txt veta el acceso automatizado: no se usa. "
               "ans-elblag.pl (web principal) permite, pero la página del grado no publica plan ni fichas. Las fichas son Word: .docx con python-docx y .doc con antiword."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS", tot)


if __name__ == "__main__":
    main()
