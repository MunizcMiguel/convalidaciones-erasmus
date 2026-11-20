"""Fase 1 - Philipps-Universitaet Marburg - B.Sc. Informatik. Fuente: Online-Modulhandbuch del FB12 (www.mathematik.uni-marburg.de/modulhandbuch/20262/BSc_Informatik/), HTML estatico, aleman.
Uso: python universidades/ec_d_marburg01/discover_ec_d_marburg01.py
"""
from __future__ import annotations
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_marburg01"
UNI = "Philipps-Universität Marburg"
GRADO = "B.Sc. Informatik"
BASE = "https://www.mathematik.uni-marburg.de/modulhandbuch/20262/BSc_Informatik/"
URL_PLAN = BASE + "index.html"
LP_RE = re.compile(r"\(([^,()]+),\s*(\d+(?:[.,]\d+)?)\s*LP\)")


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    idx = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    areas = []
    for a in idx.find_all("a", href=True):
        h = a["href"]
        if h.startswith(BASE) and h.endswith("/index.html") and h != URL_PLAN and h not in [x[1] for x in areas]:
            areas.append((a.get_text(" ", strip=True), h))
    entries, seen, tot = [], set(), {}
    for area_name, ahref in areas:
        s = BeautifulSoup(c.get_text(ahref), "lxml")
        for a in s.find_all("a", href=True):
            h = a["href"]
            if not h.startswith(ahref.rsplit("/", 1)[0] + "/") or h.endswith("index.html") or not h.endswith(".html") or "nach_" in h or "alphabetisch" in h:
                continue
            if h in seen:
                continue
            seen.add(h)
            txt = a.get_text(" ", strip=True)
            m = LP_RE.search(txt)
            name = re.sub(r"\s*\(.*$", "", txt).strip() if m else txt
            ms = BeautifulSoup(c.get_text(h), "lxml")
            h1 = ms.find("h1")
            code_m = re.match(r"^([A-Z]{2,4}\s?\d{2,4}[a-zA-Z]?)\s*[—–-]\s*(.+)$", h1.get_text(" ", strip=True)) if h1 else None
            code = re.sub(r"\s+", "", code_m.group(1)) if code_m else re.sub(r"\W+", "_", name)[:40]
            lp = float(m.group(2).replace(",", ".")) if m else None
            optional = "Wahlpflicht" in area_name or (m and "Wahl" in m.group(1))
            if not optional and lp:
                tot[area_name] = tot.get(area_name, 0) + lp
            entries.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=f"{area_name} ({m.group(1) if m else ''})", curso=None, semestre=None, creditos_ects=lp,
                caracter="optativa" if optional else "obligatoria", idioma_pagina="de", url_guia_docente=h, tipo_fuente="html"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="WiSe 2026/27", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML estático del Online-Modulhandbuch (índices por Studienbereich + una página por módulo)",
        generado_por="discover_ec_d_marburg01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Excel: Grado Ing. Informática en TI (1.ª fila con ISCED 0610), Grado Ciencia e Ingeniería de Datos (2 plazas) y Doble Grado Informática+Datos. Solo hay Informática/Datos; "
               "se elige B.Sc. Informatik (180 LP, 6 semestres; Studienbereiche: Informatik Basis 45 LP, Weiterführende 36, Praxis 21, Mathematik 24, Wahlpflicht 24, Bachelorarbeit 12). "
               "Alternativa para la fila de Datos: B.Sc. Data Science (mismo Online-Modulhandbuch, /BSc_Data_Science/; muchos módulos comparten ficha). "
               f"Obligatorios (Basis/Weiterführend/Praxis/Mathematik/BA) por área: {tot}. Sin semestre por módulo (el Modulhandbuch no lo da). "
               "Se omite Modulverantwortliche(r). robots.txt de www.mathematik.uni-marburg.de: 404 (sin restricciones)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas", tot)


if __name__ == "__main__":
    main()
