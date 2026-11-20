"""Fase 1 - Linköping University (S LINKOPI01) - Civilingenjörsprogram i industriell ekonomi - internationell (6CIEI),
Master of Science in Industrial Engineering and Management - International (300 hp), terminos 1-6 (nivel de grado, 180 hp).
Fuente: Studieinfo de LiU (liu.se/studieinfo/program/6ciei, HTML, robots permite): una tabla por termino (cohorte HT 2023) con codigo, nombre, hp, nivel y
O/V/F; cada curso enlaza su ficha en studieinfo.liu.se/en/kurs/{codigo}/{termino} (version en ingles).
Uso (desde la raiz): python universidades/ec_s_linkopi01/discover_ec_s_linkopi01.py
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
SLUG = "ec_s_linkopi01"
UNIVERSIDAD = "Linköping University"
GRADO = "Industrial Engineering and Management - International (6CIEI), terms 1-6 (first cycle)"
URL_PLAN = "https://liu.se/studieinfo/program/6ciei"
COURSE_BASE = "https://studieinfo.liu.se/en"
MAX_TERM = 6


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL_PLAN), "lxml")
    rows, seen, skipped = [], set(), 0
    for tb in soup.find_all("table"):
        pre = tb.find_previous(["h2", "h3", "h4", "h5"])
        mt = re.match(r"Termin (\d+)\s+(HT|VT)\s+(\d{4})", pre.get_text(" ", strip=True)) if pre else None
        if not mt or int(mt.group(1)) > MAX_TERM:
            continue
        cap = tb.find("caption")
        if cap and cap.get_text(strip=True):  # tablas de inriktning/profil (itinerarios): fuera
            skipped += 1
            continue
        term = int(mt.group(1))
        for tr in tb.find_all("tr"):
            tds = tr.find_all("td")
            a = tr.find("a", href=re.compile(r"/kurs/"))
            if len(tds) < 6 or not a:
                continue
            code = tds[0].get_text(strip=True)
            if code in seen:
                continue
            seen.add(code)
            hp = re.search(r"[\d.,]+", tds[2].get_text())
            vof = tds[5].get_text(strip=True)
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=re.sub(r"\s+", " ", tds[1].get_text(" ", strip=True)),
                curso_semestre=f"Termin {term} {mt.group(2)} {mt.group(3)} ({tds[3].get_text(strip=True)}, {vof})", curso=(term + 1) // 2, semestre=term,
                creditos_ects=float(hp.group(0).replace(",", ".")) if hp else None,
                caracter={"O": "obligatoria", "V": "optativa", "F": "optativa"}.get(vof, None),
                idioma_pagina="en", url_guia_docente=COURSE_BASE + a["href"], tipo_fuente="html"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2023-2024 (cohorte HT 2023)",
        url_plan_estudios=URL_PLAN, ects_totales_plan=300.0,
        estrategia_fuente="HTML estático de Studieinfo (tablas por término) + ficha de curso en inglés (studieinfo.liu.se/en/kurs/…)",
        generado_por="discover_ec_s_linkopi01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Civilingenjörsprogram i industriell ekonomi - internationell (Industrial Engineering and Management, 5 años/300 hp, no existe grado de 3 años): "
               "equivale al Grado en Ing. de Organización Industrial y al Máster en Ing. Industrial del Excel (ISCED 0710). Se catalogan solo los términos 1-6 (primer ciclo, "
               "180 hp) del recorrido de la cohorte HT 2023, parte común/obligatoria; se omiten las tablas de inriktning/perfil (itinerarios técnicos optativos): "
               f"{skipped} tablas. Código = código oficial LiU; hp = ECTS. Suma ECTS catalogados={total:g} (los hp con asterisco se cuentan enteros; las asignaturas V/F son optativas y aparecen en las tablas comunes)."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(len(rows), "asignaturas; ECTS", total, "tablas omitidas", skipped)


if __name__ == "__main__":
    main()
