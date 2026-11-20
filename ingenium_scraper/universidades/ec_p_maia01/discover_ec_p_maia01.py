"""Fase 1 - Instituto Superior da Maia / Universidade da Maia (P MAIA01): Licenciatura em Energias Renovaveis (1.º ciclo, ramo unico).
Plan de estudios en HTML estatico (codigo - nombre, semestre, ECTS). Las fichas (FPUC) se cargan por callback ASP.NET (WebForms) que el servidor
no sirve a PoliteClient (devuelve la pagina completa; el sitio marca ms-isBot) -> sin_guia, parcial. No se rodea.
Uso: python universidades/ec_p_maia01/discover_ec_p_maia01.py
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
SLUG = "ec_p_maia01"
UNIVERSIDAD = "Instituto Superior da Maia (ISMAI) / Universidade da Maia"
GRADO = "Licenciatura em Energias Renováveis (1.º ciclo)"
URL_PLAN = "https://www.ismai.pt/pt/ensino/oferta-formativa/licenciaturas/energias-renovaveis"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=2, timeout=30)
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    entries, seen = [], set()
    for tr in s.find_all("tr"):
        first = tr.find("td", class_="firstColumn")
        if first is None:
            continue
        txt = re.sub(r"\s+", " ", first.get_text(" ", strip=True))
        m = re.match(r"^(\d+) - (.+)$", txt)
        trtxt = re.sub(r"\s+", " ", tr.get_text(" ", strip=True))
        ym = re.search(r"(\d)º Ano", trtxt)
        sem = re.search(r"(\d)º Semestre", trtxt)
        ects = tr.find("td", class_="thirdcolumn")
        if not (m and ym and sem and ects):
            continue
        code = m.group(1)
        if code in seen:
            continue
        seen.add(code)
        year, sm = int(ym.group(1)), int(sem.group(1))
        name = m.group(2).strip()
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
            curso_semestre=f"{year}º Ano / {sm}º Semestre", curso=year, semestre=(year - 1) * 2 + sm, creditos_ects=float(ects.get_text(strip=True).replace(",", ".")),
            caracter="tfg" if name.lower() == "projeto" else "obligatoria", idioma_pagina="pt", url_guia_docente=None, tipo_fuente="sin_guia"))
    tot = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/26 (plan vigente en la web)", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML estático de la página del grado (tabla de plan de estudios con código ISMAI); fichas (FPUC) solo vía callback WebForms no servido",
        generado_por="discover_ec_p_maia01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación elegida: Energias Renováveis (único 1.º ciclo de ingeniería/energía de ISMAI; el Excel trae Grado en Ingeniería Eléctrica (2 plazas) e Informática TI/Informática+Datos (sin plazas); ISMAI no tiene grado eléctrico y Energias Renováveis (Electrotecnia, Máquinas Elétricas, Redes de Distribuição, Termodinâmica) es la más afín a Eléctrica; "
               f"también existe Licenciatura em Informática, descartada por prioridad). {len(entries)} UC, suma {tot:g} ECTS (plan 180). PARCIAL: la ficha programática de cada UC se pide con VerFPUC() -> WebForm callback (POST con __CALLBACKID); PoliteClient recibe la página completa en vez del JSON "
               "(el sitio marca el cliente como bot, ms-isBot) y no se emula navegador ni se rodea. Todas sin_guia; sin Fase 2. Hint del Excel (ubu.es) era un factsheet de otra universidad. Idioma pt."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "UC", tot, "ECTS")


if __name__ == "__main__":
    main()
