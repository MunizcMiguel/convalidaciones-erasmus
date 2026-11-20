#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universidad Carlos III de Madrid, Grado en Ingeniería Mecánica
(RUCT 2500048, estudio 221, plan 446, Escuela Politécnica Superior, Leganés).

Fuente: la pestaña "Programa" de la ficha oficial del grado (https://www.uc3m.es/grado/mecanica),
HTML estático con una tabla por curso/cuatrimestre más una tabla de optativas. Cada fila enlaza
la ficha de la asignatura en la aplicación "cpa" (aplicaciones.uc3m.es/cpa/generaFicha), cuyo
parámetro `asig` es el código oficial de la asignatura.

Uso (desde la raíz del proyecto):
    python universidades/es_carlos_iii_madrid/discover_es_carlos_iii_madrid.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_carlos_iii_madrid"
UNI = "Universidad Carlos III de Madrid"
GRADO = "Grado en Ingeniería Mecánica"
PLAN_URL = "https://www.uc3m.es/grado/mecanica"
ECTS_PLAN = 240.0
# Desglose oficial RUCT (config/universities_es.json, título 2500048)
RUCT = {"formacion_basica": 60.0, "obligatoria": 156.0, "optativa": 12.0, "tfg": 12.0}
TIPOS = {"FB": "formacion_basica", "O": "obligatoria", "P": "optativa", "TFG": "tfg"}


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").upper()


def academic_year(http: PoliteClient, url: str) -> str:
    """Curso académico que sirve la aplicación de fichas (se lee de una ficha real)."""
    soup = BeautifulSoup(http.get_text(url), "lxml")
    m = re.search(r"(\d{4})/(\d{4})", soup.find("div", class_="anio").get_text())
    return f"{m.group(1)}-{m.group(2)}"


def main() -> int:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(PLAN_URL), "lxml")
    block = soup.find("div", class_="programaAsignatura")
    if block is None:
        raise SystemExit("No se encuentra el bloque del programa (div.programaAsignatura)")

    rows: list[CatalogEntry] = []
    skipped: list[str] = []
    for table in block.find_all("table"):
        h3 = table.find_previous("h3")
        m = re.match(r"Curso (\d) - Cuatrimestre (\d)", h3.get_text(" ", strip=True))
        curso, cuat = int(m.group(1)), int(m.group(2))
        caption = table.caption.get_text(" ", strip=True) if table.caption else ""
        es_optativas = caption.lower().startswith("optativas")
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue
            nombre = tds[0].get_text(" ", strip=True)
            ects_txt = tds[1].get_text(" ", strip=True).replace(",", ".")
            tipo = tds[2].get_text(" ", strip=True)
            if not re.fullmatch(r"\d+(\.\d+)?", ects_txt):
                skipped.append(nombre)  # fila-marcador "Optativas: Recomendado 12 créditos"
                continue
            a = tds[0].find("a", href=True)
            mcode = re.search(r"generaFicha\?.*?asig=(\d+)", a["href"]) if a else None
            if mcode:
                code, url, fuente = mcode.group(1), a["href"], "html"
            else:
                # Cursos de Humanidades / habilidades: bolsa de créditos sin asignatura ni ficha única.
                # Clave estable derivada: SG-{curso}{cuatrimestre}-{NOMBRE normalizado}
                code, url, fuente = f"SG-{curso}{cuat}-{slugify(nombre)}", None, "sin_guia"
            rows.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=f"Curso {curso} / Cuatrimestre {cuat}" + (" (optativa)" if es_optativas else ""),
                curso=curso, semestre=(curso - 1) * 2 + cuat, creditos_ects=float(ects_txt),
                caracter=TIPOS.get(tipo, tipo.lower()), idioma_pagina="es",
                url_guia_docente=url, tipo_fuente=fuente,
            ))

    codes = [r.codigo_asignatura for r in rows]
    dup = {c for c in codes if codes.count(c) > 1}
    if dup:
        raise SystemExit(f"Códigos duplicados: {dup}")

    by = defaultdict(float)
    for r in rows:
        by[r.caracter] += r.creditos_ects
    for k in ("formacion_basica", "obligatoria", "tfg"):
        if abs(by[k] - RUCT[k]) > 1e-6:
            raise SystemExit(f"ECTS {k}: catálogo {by[k]} != RUCT {RUCT[k]}")
    total = sum(by.values())
    sin_guia = [r for r in rows if r.tipo_fuente == "sin_guia"]
    first_url = next(r.url_guia_docente for r in rows if r.url_guia_docente)

    notas = (
        f"Centro: Escuela Politécnica Superior (Leganés), único centro del título RUCT 2500048 (RD 1393/2007; "
        f"estudio 221, plan 446). {len(rows)} filas, {total:g} ECTS ofertados frente a 240 del plan: formación básica "
        f"{by['formacion_basica']:g}, obligatorias {by['obligatoria']:g}, TFG {by['tfg']:g} (coinciden con el RUCT: 60/156/12) "
        f"y {by['optativa']:g} ECTS optativos ofertados de los que el estudiante cursa 12 (RUCT: 12). "
        f"Prácticas Externas (6 ECTS) es una optativa, coherente con prácticas=0 en el RUCT. "
        f"{len(sin_guia)} filas obligatorias sin guía única (tipo_fuente sin_guia, "
        f"{sum(r.creditos_ects for r in sin_guia):g} ECTS): {', '.join(r.nombre_asignatura for r in sin_guia)}; "
        f"son bolsas de créditos que se cubren eligiendo cursos de un catálogo transversal, con clave derivada "
        f"SG-{{curso}}{{cuatrimestre}}-{{nombre}}. La página sitúa todas las optativas en Curso 4 / Cuatrimestre 2; "
        f"el cuatrimestre real de cada optativa puede variar. Guías en castellano (idioma=1) también para las "
        f"asignaturas impartidas solo en inglés. Fila-marcador omitida: {'; '.join(skipped)}."
    )
    catalog = Catalog(
        meta=CatalogMeta(
            universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico=academic_year(http, first_url),
            url_plan_estudios=PLAN_URL, ects_totales_plan=ECTS_PLAN,
            estrategia_fuente=("HTML estático: tablas de la pestaña 'Programa' de la ficha oficial del grado en www.uc3m.es "
                               "(una por curso/cuatrimestre + optativas). Guía = ficha HTML por asignatura en "
                               "aplicaciones.uc3m.es/cpa/generaFicha?est=221&plan=446&asig={codigo}&idioma=1."),
            generado_por=Path(__file__).name, generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
            estado="ok", notas=notas,
        ),
        asignaturas=rows,
    )
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(rows)} asignaturas -> {out}")
    print({k: v for k, v in by.items()}, "total", total, "| sin_guia", len(sin_guia), "| red/caché", http.stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
