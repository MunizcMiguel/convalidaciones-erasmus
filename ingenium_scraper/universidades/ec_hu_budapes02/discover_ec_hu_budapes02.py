"""Fase 1 (parcial) - BME Budapest, Faculty of Mechanical Engineering (GPK) - BSc in Mechanical Engineering (7 semestres, 210 ECTS).
Fuente: ficha del programa en xplore.bme.hu (WordPress; solo descripcion por bloques de creditos, sin lista de asignaturas).
Las fichas de asignatura viven en www.gpk.bme.hu (certificado TLS invalido: regla de parada), en el Moodle edu.gpk.bme.hu
(cursos que requieren login) y en Neptun (login). Catalogo parcial vacio, sin Fase 2.
Uso: python universidades/ec_hu_budapes02/discover_ec_hu_budapes02.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_hu_budapes02"
URL = "https://xplore.bme.hu/programme/bsc-in-mechanical-engineering/"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL), "lxml")
    txt = re.sub(r"\s+", " ", s.get_text(" ", strip=True))
    m = re.search(r"(\d+) semesters.{0,10}?(\d+) ECTS", txt)
    sem, ects = (m.group(1), m.group(2)) if m else ("?", "?")
    try:
        c.get_text("https://www.gpk.bme.hu/")
        tls = "accesible"
    except FetchError as e:
        tls = "inaccesible: " + str(e)[-90:]
    meta = CatalogMeta(
        universidad="Budapest University of Technology and Economics (BME) - Faculty of Mechanical Engineering", slug=SLUG,
        nombre_grado="BSc in Mechanical Engineering", curso_academico="2026/2027", url_plan_estudios=URL,
        ects_totales_plan=float(ects) if ects != "?" else None,
        estrategia_fuente="HTML de xplore.bme.hu (solo resumen por bloques); sin lista de asignaturas pública", generado_por="discover_ec_hu_budapes02.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: BSc in Mechanical Engineering (GPK), en inglés, {sem} semestres, {ects} ECTS. xplore.bme.hu (robots permite) solo da la distribución por "
               f"bloques de créditos (matemáticas 22, bases de ingeniería 40, etc.), no asignaturas. Enlaza como 'programme's website' al Moodle edu.gpk.bme.hu (cursos con login; "
               f"el índice público solo lista cursos del semestre por departamento, sin guías) y las fichas de asignatura de GPK están en www.gpk.bme.hu: {tls} "
               "(certificado TLS no verificable → regla de parada, no se desactiva la verificación). Neptun requiere login. Sin plan ni guías públicas accesibles: catálogo vacío, sin Fase 2. "
               "No verificado: si algún curso del Moodle permite acceso de invitado (no se probó)."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(sem, ects, tls)


if __name__ == "__main__":
    main()
