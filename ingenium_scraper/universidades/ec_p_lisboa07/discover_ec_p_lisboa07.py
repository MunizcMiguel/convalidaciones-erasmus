"""Fase 1 - ISCTE-IUL (P LISBOA07): Licenciatura em Engenharia de Telecomunicaciones e Informatica (LETI, 180 ECTS).
Fuente unica: www.iscte-iul.pt/programmes/degree/9098 (HTML, en ingles): tablas por año + modales con objetivos/programa/evaluacion/bibliografia.
(fenix.iscte-iul.pt esta vetado por robots; fenix-mais solo se usa para el enlace «See more» que da el codigo.)
Uso: python universidades/ec_p_lisboa07/discover_ec_p_lisboa07.py
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
SLUG = "ec_p_lisboa07"
UNIVERSIDAD = "ISCTE - Instituto Universitário de Lisboa"
GRADO = "Telecommunications and Computer Engineering (Licenciatura, LETI)"
URL_PLAN = "https://www.iscte-iul.pt/programmes/degree/9098"


def load():
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    return BeautifulSoup(c.get_text(URL_PLAN), "lxml")


def main() -> None:
    s = load()
    sp = s.find(id="study_plan")
    entries, seen = [], set()
    for pane in sp.find_all(class_="tab-pane"):
        if pane.find_parent(class_="modal") or not re.fullmatch(r"tab-pane-\d", pane.get("id") or ""):
            continue
        year = int(pane["id"][-1]) + 1
        for tr in pane.select("tr.yearsemester-info"):
            name = tr.find("a", class_="curricular-course-text").get_text(" ", strip=True)
            sem = int(tr.select("td")[1].get_text(strip=True))
            ects = float(tr.select_one(".ects-value").get_text(strip=True))
            mid = tr["data-bs-target"].lstrip("#")
            modal = s.find(id=mid)
            a = modal.select_one(".m-modal-course__read_more a[href]")
            href = a["href"] if a else None
            code = href.rstrip("/").rsplit("/", 1)[-1].rsplit("-", 1)[0] if href else re.sub(r"\W+", "_", name.lower())
            kind = modal.select_one(".caption").get_text(strip=True).lower()
            if code in seen:
                code = f"{code}_{mid.split('-')[-1]}"
            seen.add(code)
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=f"Year {year} / Semester {sem}", curso=year, semestre=(year - 1) * 2 + sem, creditos_ects=ects,
                caracter="obligatoria" if kind.startswith("mandatory") else "optativa", idioma_pagina="en",
                url_guia_docente=f"{URL_PLAN}#{mid}", tipo_fuente="html"))
    tot = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/2027 (plan vigente en la web)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0, estrategia_fuente="HTML de la página del grado: tabla por curso + modal por UC (objetivos, programa, evaluación, bibliografía) en inglés",
        generado_por="discover_ec_p_lisboa07.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Telecommunications and Computer Engineering (LETI), única licenciatura de telecomunicaciones de ISCTE; el Excel solo trae Telecomunicación "
               "(Grado TSTT, doble Teleco+Datos y máster) para este destino (2 plazas, ISCED 0710). Se descarta Computer Engineering. "
               f"{len(entries)} filas, suma {tot:g} ECTS de filas (los 180 incluyen 18 de optativas y 6 de competencias transversales que no tienen fila propia si no figuran en las tablas por curso). "
               "Código = identificador de la UC en fenix-mais (parte previa al id numérico) tomado del enlace «See more»; la ficha completa (FUC) no se descarga: el modal de la página del grado ya trae los 4 bloques. "
               "Plan 2026/27: puede diferir ligeramente de cohortes anteriores."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas", tot, "ECTS", [(e.codigo_asignatura, e.caracter) for e in entries if e.caracter != "obligatoria"])


if __name__ == "__main__":
    main()
