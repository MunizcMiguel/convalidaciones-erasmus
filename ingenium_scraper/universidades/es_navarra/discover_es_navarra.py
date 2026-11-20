#!/usr/bin/env python3
"""Fase 1 — Universidad de Navarra, Grado en Ingeniería Mecánica (Tecnun, Escuela de Ingeniería, San Sebastián).
Fuente: https://www.unav.edu/web/grado-en-ingenieria-mecanica/plan-de-estudios (HTML estático): tablas por módulo (carácter) y tablas por curso/semestre con enlace a
la ficha PDF (asignatura.unav.edu devuelve un PDF). Uso: python universidades/es_navarra/discover_es_navarra.py"""
import json, re, sys, time, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_navarra", "Universidad de Navarra"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://www.unav.edu/web/grado-en-ingenieria-mecanica/plan-de-estudios"
norm = lambda s: re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s)).strip().lower()  # noqa: E731

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
tables = soup.find_all("table")
# carácter por módulo (tablas 0-4: Formación básica, común rama, especializado, formación personal y social, TFG)
car_by_name = {}
for ti, car in zip(range(5), ["formacion_basica", "obligatoria", "obligatoria", "obligatoria", "tfg"]):
    for tr in tables[ti].find_all("tr")[1:]:
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        name = tds[2] if len(tds) >= 4 else tds[0]
        car_by_name[norm(name)] = car
entries, seen = [], set()
for ti, curso in zip(range(5, 9), [1, 2, 3, 4]):
    t = tables[ti]
    hdr = [th.get_text(" ", strip=True) for th in t.find_all("tr")[0].find_all(["td", "th"])]
    # índices de las columnas de nombre en castellano (en 1.º hay columnas en inglés intercaladas)
    cols = [(i, 1 if "PRIMER" in h else 2) for i, h in enumerate(hdr) if h.startswith(("PRIMER", "SEGUNDO"))]
    for tr in t.find_all("tr")[1:]:
        tds = tr.find_all("td")
        for i, sem in cols:
            if i + 1 >= len(tds):
                continue
            a = tds[i].find("a", href=re.compile(r"asignatura\.unav\.edu"))
            txt = tds[i].get_text(" ", strip=True)
            if not a or not re.fullmatch(r"\d+([.,]\d+)?", tds[i + 1].get_text(strip=True) or "x"):
                continue
            slug = re.search(r"asignatura\.unav\.edu/([^/?#]+)", a["href"])[1]
            if slug in seen:
                continue
            seen.add(slug)
            nombre = re.sub(r"\s+", " ", unicodedata.normalize("NFKC", txt)).strip()
            car = car_by_name.get(norm(nombre)) or car_by_name.get(re.sub(r" i$", "", norm(nombre)))
            if re.search(r"(?i)proyecto fin de grado|trabajo fin", nombre):
                car = "tfg"
            entries.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=slug, nombre_asignatura=nombre, curso_semestre=f"Curso {curso} / Semestre {(curso - 1) * 2 + sem}",
                curso=curso, semestre=(curso - 1) * 2 + sem, creditos_ects=float(tds[i + 1].get_text(strip=True).replace(",", ".")), caracter=car or "sin_clasificar",
                idioma_pagina="es", url_guia_docente=a["href"], tipo_fuente="pdf"))
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
print(len(entries), s)
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL, ects_totales_plan=240.0,
    estrategia_fuente="HTML estático del plan en unav.edu: tablas por curso/semestre (columnas en castellano) con enlace a la ficha; carácter por emparejamiento de nombre con las tablas de módulos.",
    generado_por="discover_es_navarra.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"{len(entries)} asignaturas (Tecnun, San Sebastián; plan RD 822/2021). ECTS por carácter {json.dumps(s)} frente al RUCT (básica 68, obligatorias 146, optativas 14, TFG 12). "
           "Sin código oficial: clave = identificador de la URL de la ficha (asignatura.unav.edu/{id}/). El carácter sale de emparejar nombres con las tablas de módulos; "
           "las que no casan quedan como «sin_clasificar» (nombres distintos en las tablas de módulos). Faltan en el catálogo unos 14 ECTS de optativas, que la página del plan no enlaza como asignaturas. La web duplica las tablas por curso (dos paneles); se usa la primera."))
(HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=entries).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
