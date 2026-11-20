"""Fase 1 (parcial) - Jonkoping University (JU), School of Engineering (JTH).
JU no ofrece un grado en ingles de Ingenieria Mecanica: los grados (BSc, 180 hp) del School of Engineering en ingles son New Media Design y Sustainable
Supply Chain Management; los de ingenieria estan en sueco. Este script lee la pagina oficial de programas y escribe un catalogo parcial vacio con el motivo.
Uso: python universidades/ec_s_jonkopi01/discover_ec_s_jonkopi01.py
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
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_s_jonkopi01"
URL = "https://ju.se/en/about-us/school-of-engineering/study-at-the-school-of-engineering/programmes.html"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    t = re.sub(r"\s+", " ", BeautifulSoup(c.get_text(URL), "lxml").get_text(" ", strip=True))
    m = re.search(r"Bachelor Programmes (.*?) Master Programmes", t)
    bach = m.group(1).strip() if m else "?"
    meta = CatalogMeta(
        universidad="Jönköping University - School of Engineering (JTH)", slug=SLUG, nombre_grado="(sin grado en inglés equivalente a Ingeniería Mecánica)",
        curso_academico="2026/2027", url_plan_estudios=URL, ects_totales_plan=None, estrategia_fuente="HTML de la página de programas del School of Engineering",
        generado_por="discover_ec_s_jonkopi01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"La página oficial de programas del School of Engineering (ju.se, robots permite) lista como grados de 3 años (180 hp) en inglés solo: «{bach}». "
               "No hay Mechanical Engineering en inglés; los grados de ingeniería (högskoleingenjör) están en 'Programmes in Swedish' y no se localizó un enlace a un programa de maquinteknik/produktutveckling con plan de cursos. "
               "Sí existe la oferta de intercambio del JTH (lista Excel y páginas `/en/study-at-ju/courses/programme-course/{nombre}-{semestre}-{id}.html`), que no es el plan de un grado. "
               "Sin plan ni grado identificable: catálogo vacío, sin Fase 2. No verificado: contenido de los programas en sueco ni estructura de las fichas programme-course."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(bach)


if __name__ == "__main__":
    main()
