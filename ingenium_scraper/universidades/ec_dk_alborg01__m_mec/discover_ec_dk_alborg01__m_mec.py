"""Fase 1 - Aalborg Universitet (DK ALBORG01) - BSc in Engineering, Applied Industrial Electronics (Esbjerg, English).

Fuente: studieordninger.aau.dk (curriculum 2025, volumen 2026/2027, id 6606): tablas de modulos por semestre,
con enlace a moduler.aau.dk. Se catalogan los semestres 1-4 comunes y la especializacion Industrial Electronics (5-6).
Uso (desde la raiz):  python universidades/ec_dk_alborg01__m_mec/discover_ec_dk_alborg01__m_mec.py
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
SLUG = "ec_dk_alborg01__m_mec"
UNIVERSIDAD = "Aalborg Universitet"
GRADO = "Mechanical Engineering (MSc in Engineering), Aalborg"
AY = "2026-2027"
URL_PLAN = "https://studieordninger.aau.dk/2026/59/6801"
ECTS_PLAN = 120.0


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL_PLAN), "lxml")
    rows, seen = [], set()
    for tb in soup.find_all("table"):
        if "moduler.aau.dk" not in str(tb):
            continue
        sem, spec = None, None
        for tr in tb.find_all("tr"):
            tds = tr.find_all(["td", "th"])
            txt = tds[0].get_text(" ", strip=True) if tds else ""
            if txt.startswith("Specialization:"):
                spec = txt.split(":", 1)[1].strip()
            ms = re.match(r"(\d+)(?:-\d+)?\s+Semester", txt)
            if ms:
                sem = int(ms.group(1))
                continue
            a = tr.find("a", href=True)
            if not a or len(tds) < 7 or "moduler.aau.dk" not in a["href"]:
                continue
            mc = re.search(r"\(([^()]+)\)\s*$", txt)
            code = mc.group(1) if mc else a["href"].rsplit("/", 1)[-1]
            if code in seen:
                continue
            seen.add(code)
            nombre = re.sub(r"\s*\([^()]+\)\s*$", "", re.sub(r"\s+", " ", txt))
            tipo = tds[1].get_text(strip=True)
            car = "tfg" if nombre.lower().startswith("master") and "thesis" in nombre.lower() else ("obligatoria" if sem else "optativa")
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=(f"Semester {sem}" if sem else "Elective") + f" ({tipo}; {spec or 'electivas de especialización'})", curso=(sem + 1) // 2 if sem else None, semestre=sem,
                creditos_ects=float(tds[2].get_text(strip=True)), caracter=car, idioma_pagina="en", url_guia_docente=a["href"], tipo_fuente="html"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="master", curso_academico=AY, url_plan_estudios=URL_PLAN, ects_totales_plan=ECTS_PLAN,
        estrategia_fuente="HTML estatico de studieordninger.aau.dk (tablas por semestre y especialización) + fichas de moduler.aau.dk",
        generado_por="discover_ec_dk_alborg01__m_mec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Máster de ingeniería mecánica de Aalborg: MSc in Engineering - Mechanical Engineering (campus Aalborg, inglés, 120 ECTS), curriculum 2026/27, "
               "con las especializaciones Design of Mechanical Systems, Manufacturing Technology y Biomechanical Engineering. Se catalogan los módulos únicos de las tres especializaciones "
               "y de las listas de optativas (los proyectos de semestre de 15-60 ECTS son opciones alternativas; la suma bruta supera 120). Código = código oficial AAU. "
               f"{len(rows)} módulos, suma bruta {total:g} ECTS. Fichas sin temario ni bibliografía (solo objetivos, tipo de docencia y examen), como en ec_dk_alborg01."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(f"{len(rows)} asignaturas; ECTS={total:g}")


if __name__ == "__main__":
    main()
