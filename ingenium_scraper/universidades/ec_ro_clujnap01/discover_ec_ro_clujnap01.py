"""Fase 1 - Babes-Bolyai University, Cluj-Napoca (RO CLUJNAP01) - Computer Science (teaching in English), Faculty of Mathematics and Computer Science.
Fuente: www.cs.ubbcluj.ro/apps/fise/viewSyllabi.php?an=2025&lang=en&specializare=IE (HTML, una tabla por semestre, con codigo, ECTS, tipo y enlace al PDF
de la «fisa disciplinei»). robots.txt solo veta /wp-admin/.
Uso (desde la raiz): python universidades/ec_ro_clujnap01/discover_ec_ro_clujnap01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_ro_clujnap01"
UNIVERSIDAD = "Babeș-Bolyai University, Cluj-Napoca"
GRADO = "Computer Science (teaching in English), Bachelor"
URL = "https://www.cs.ubbcluj.ro/apps/fise/viewSyllabi.php?an=2025&lang=en&specializare=IE"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL), "lxml")
    rows, seen, groups = [], {}, set()
    for sem, tb in enumerate(soup.find_all("table"), start=1):
        group = ""
        for tr in tb.find_all("tr"):
            cells = [re.sub(r"\s+", " ", c.get_text(" ", strip=True)) for c in tr.find_all(["td", "th"])]
            a = tr.find("a", href=True)
            if len(cells) == 1:
                group = cells[0]
                groups.add(group)
                continue
            if not a or len(cells) < 5:
                continue
            code = cells[1]
            seen[code] = seen.get(code, 0) + 1
            if seen[code] > 1:
                code = f"{code}_s{sem}"
            tipo = cells[4].lower()
            car = "obligatoria" if tipo.startswith("compul") else ("tfg" if re.search(r"thesis|diploma|license", cells[0], re.I) else "optativa")
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=cells[0],
                curso_semestre=f"Semester {sem} ({group})", curso=(sem + 1) // 2, semestre=sem,
                creditos_ects=float(cells[2]) if re.fullmatch(r"[\d.]+", cells[2]) else None, caracter=car,
                idioma_pagina="en" if cells[3].lower().startswith("english") else cells[3][:2].lower(),
                url_guia_docente=urljoin(URL, a["href"]), tipo_fuente="pdf"))
    total = sum(r.creditos_ects or 0 for r in rows)
    obl = sum(r.creditos_ects or 0 for r in rows if r.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2025-2026",
        url_plan_estudios=URL, ects_totales_plan=180.0,
        estrategia_fuente="HTML estático del listado de fichas (viewSyllabi.php) + PDF 'fișa disciplinei' por asignatura",
        generado_por="discover_ec_ro_clujnap01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Computer Science (teaching in English), grado de 3 años/180 ECTS: el Excel solo tiene Informática en TI, Ciencia e Ingeniería de Datos "
               "y Doble Grado Informática+Datos (ISCED 0612); la Informática en inglés es la afín a Informática en TI (alternativas: Information Engineering en inglés, "
               "Artificial Intelligence). Código = código oficial UBB 'MLE…'. Suma ECTS catalogados="
               f"{total:g} (obligatorios {obl:g}; el resto son paquetes optativos/itinerarios entre los que el alumno elige). Grupos vistos: {sorted(groups)}."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(len(rows), "asignaturas; ECTS", total, "obl", obl, sorted(groups))


if __name__ == "__main__":
    main()
