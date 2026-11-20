"""Fase 1 - Aalborg Universitet (DK ALBORG01) - BSc in Engineering, Applied Industrial Electronics (Esbjerg, English).

Fuente: studieordninger.aau.dk (curriculum 2025, volumen 2026/2027, id 6606): tablas de modulos por semestre,
con enlace a moduler.aau.dk. Se catalogan los semestres 1-4 comunes y la especializacion Industrial Electronics (5-6).
Uso (desde la raiz):  python universidades/ec_dk_alborg01/discover_ec_dk_alborg01.py
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
SLUG = "ec_dk_alborg01"
UNIVERSIDAD = "Aalborg Universitet"
GRADO = "BSc in Engineering (Applied Industrial Electronics), Esbjerg"
AY = "2026-2027"
URL_PLAN = "https://studieordninger.aau.dk/2026/56/6606"
ECTS_PLAN = 180.0


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(URL_PLAN), "lxml")
    tables = [t for t in soup.find_all("table") if "moduler.aau.dk" in str(t)]
    rows, seen, skipped = [], set(), []
    for ti, tb in enumerate(tables):
        head = " ".join(tr.get_text(" ", strip=True) for tr in tb.find_all("tr")[:2])
        if "IT and Cyber Systems" in head and "Specialization: IT and Cyber" in head:
            skipped.append(head[:80])
            continue  # especializacion alternativa (no Industrial Electronics)
        sem = None
        for tr in tb.find_all("tr"):
            tds = tr.find_all(["td", "th"])
            txt = tds[0].get_text(" ", strip=True) if tds else ""
            ms = re.fullmatch(r"(\d+)\s+Semester", txt)
            if ms:
                sem = int(ms.group(1))
                continue
            a = tr.find("a", href=True)
            if not a or sem is None or len(tds) < 7:
                continue
            mc = re.search(r"\(([^()]+)\)\s*$", txt)
            code = mc.group(1) if mc else a["href"].rsplit("/", 1)[-1]
            nombre = re.sub(r"\s*\([^()]+\)\s*$", "", re.sub(r"\s+", " ", txt))
            if code in seen:
                continue
            seen.add(code)
            tipo = tds[1].get_text(strip=True)
            car = "tfg" if nombre.lower().startswith("bachelor project") else "obligatoria"
            rows.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=f"Semester {sem} ({tipo})", curso=(sem + 1) // 2, semestre=sem,
                creditos_ects=float(tds[2].get_text(strip=True)), caracter=car,
                idioma_pagina="en", url_guia_docente=a["href"], tipo_fuente="html"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico=AY,
        url_plan_estudios=URL_PLAN, ects_totales_plan=ECTS_PLAN,
        estrategia_fuente="HTML estatico de studieordninger.aau.dk (tablas por semestre) + fichas de moduler.aau.dk",
        generado_por="discover_ec_dk_alborg01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Applied Industrial Electronics (BSc in Engineering, campus Esbjerg, docencia en inglés), "
               "la más afín a Electrónica Industrial y Automática / Eléctrica (el resto de grados de electrónica de Aalborg, "
               "p. ej. Electronic Systems Engineering, se imparten en danés). Catalogados semestres 1-4 comunes y la "
               "especialización Industrial Electronics (5-6); se omite la alternativa 'IT and Cyber Systems' "
               "(solo difiere en módulos de 5.º-6.º). Código = código oficial del módulo AAU. "
               f"Suma ECTS={total:g}."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(f"{len(rows)} asignaturas; ECTS={total:g}; omitidas={skipped}")


if __name__ == "__main__":
    main()
