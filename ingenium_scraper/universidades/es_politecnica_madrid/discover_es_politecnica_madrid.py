#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universidad Politécnica de Madrid, Grado en Ingeniería Mecánica
(plan 56IM, ETS de Ingeniería y Diseño Industrial, RUCT 2502150).

Fuente del plan: API JSON pública de datos académicos de la UPM
    https://www.upm.es/wapi_upm/academico/comun/index.upm/v2/plan.json/56IM/asignaturas?anio=AAAABB
(un objeto por asignatura: código, nombre, curso, tipo, ECTS, ofertada, impartición por semestre).

Guías: un PDF por asignatura en la plataforma GAUSS (www.upm.es/comun_gauss/publico/guias/).
El campo `guia_pdf` de la API sigue dando para 2026-27 el patrón antiguo
({año}/{sem}/GA_{plan}_{cod}_{sem}_{año}.pdf), que devuelve 404: desde 2026-27 las guías se publican
como {año}/GA_{plan}_{cod}_ES_{año}.pdf. El script comprueba, asignatura por asignatura, la guía
2026-27 y, si no existe, la de 2025-26 (patrón antiguo, tomado de la API de ese año). Los 404 se
recuerdan en raw_cache/probe_404.json para que una segunda ejecución no toque la red.

Uso (desde la raíz del proyecto):
    python universidades/es_politecnica_madrid/discover_es_politecnica_madrid.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_politecnica_madrid"
UNIVERSIDAD = "Universidad Politécnica de Madrid"
PLAN = "56IM"
NOMBRE_GRADO = "Grado en Ingeniería Mecánica"
CENTRO = "Escuela Técnica Superior de Ingeniería y Diseño Industrial (ETSIDI)"
YEAR, YEAR_PREV = "2026-27", "2025-26"
API = "https://www.upm.es/wapi_upm/academico/comun/index.upm/v2/plan.json/{plan}/asignaturas?anio={anio}"
GUIA_NEW = "https://www.upm.es/comun_gauss/publico/guias/{year}/GA_{plan}_{code}_ES_{year}.pdf"
RUCT = {"basica": 60.0, "obligatorios": 66.0, "optativos": 102.0, "practicas": 0.0, "tfg": 12.0, "total": 240.0}

CARACTER = {"T": "formacion_basica", "B": "obligatoria", "O": "optativa", "P": "tfg"}
SEM = {"1S": 1, "2S": 2}
PROBE_FILE = HERE / "raw_cache" / "probe_404.json"


def api_url(year: str) -> str:
    return API.format(plan=PLAN, anio=year[:4] + year[5:])


def load_plan(http: PoliteClient, year: str) -> dict:
    return json.loads(http.get_bytes(api_url(year)).decode("utf-8"))


class Prober:
    """¿Existe este PDF? Lo descarga (queda en caché para el scraper) y recuerda los 404."""

    def __init__(self, http: PoliteClient):
        self.http = http
        self.missing: set[str] = set(json.loads(PROBE_FILE.read_text("utf-8"))) if PROBE_FILE.exists() else set()

    def exists(self, url: str) -> bool:
        if url in self.missing:
            return False
        try:
            data = self.http.get_bytes(url)
        except FetchError as e:
            if "HTTP 404" not in str(e):
                raise
            self.missing.add(url)
            PROBE_FILE.write_text(json.dumps(sorted(self.missing), indent=1), encoding="utf-8")
            return False
        if not data.startswith(b"%PDF"):
            raise RuntimeError(f"No es un PDF: {url}")
        return True


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    plan = load_plan(http, YEAR)
    plan_prev = load_plan(http, YEAR_PREV)
    prober = Prober(http)

    entries: list[CatalogEntry] = []
    no_ofertadas, origen = [], {YEAR: 0, YEAR_PREV: 0, "sin_guia": 0}
    for code, a in sorted(plan.items()):
        if a["codigo"] != code:
            raise RuntimeError(f"Clave y código no coinciden: {code}")
        if a["ofertada"] != "S":
            no_ofertadas.append(code)
            continue
        car = CARACTER.get(a["codigo_tipo_asignatura"])
        if car is None:
            raise RuntimeError(f"Tipo de asignatura no contemplado: {a['codigo_tipo_asignatura']!r} ({code})")
        curso = int(a["curso"])
        durs = sorted(a["imparticion"] or {})
        nombres_dur = [a["imparticion"][d]["nombre_duracion"] for d in durs]
        semestre = (curso - 1) * 2 + SEM[durs[0]] if len(durs) == 1 and durs[0] in SEM else None

        # Guía: 2026-27 (patrón nuevo) y, si no está publicada, 2025-26 (URLs de la API de ese año)
        url, year_guia = None, None
        cand = GUIA_NEW.format(year=YEAR, plan=PLAN, code=code)
        if prober.exists(cand):
            url, year_guia = cand, YEAR
        else:
            prev = (plan_prev.get(code) or {}).get("imparticion") or {}
            for d in sorted(prev):
                cand = prev[d].get("guia_pdf")
                if cand and prober.exists(cand):
                    url, year_guia = cand, YEAR_PREV
                    break
        origen[year_guia or "sin_guia"] += 1

        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD,
            nombre_grado=NOMBRE_GRADO,
            codigo_asignatura=code,
            nombre_asignatura=a["nombre"],
            curso_semestre=f"Curso {curso} / {', '.join(nombres_dur)}"
                           + (f" (guía {year_guia})" if year_guia and year_guia != YEAR else ""),
            curso=curso,
            semestre=semestre,
            creditos_ects=float(a["credects"].replace(",", ".")),
            caracter=car,
            idioma_pagina="es",
            url_guia_docente=url,
            tipo_fuente="pdf" if url else "sin_guia",
        ))

    # ---------- validación ----------
    codigos = [e.codigo_asignatura for e in entries]
    assert len(codigos) == len(set(codigos)), "Códigos duplicados"
    assert all(e.url_guia_docente or e.tipo_fuente == "sin_guia" for e in entries)
    suma: dict[str, float] = {}
    for e in entries:
        suma[e.caracter] = suma.get(e.caracter, 0) + e.creditos_ects
    assert suma["formacion_basica"] == RUCT["basica"], suma
    assert suma["obligatoria"] == RUCT["obligatorios"], suma
    assert suma["tfg"] == RUCT["tfg"], suma
    assert suma["optativa"] >= RUCT["optativos"], suma
    ofertado = sum(suma.values())
    sin = [e.codigo_asignatura for e in entries if e.tipo_fuente == "sin_guia"]

    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=NOMBRE_GRADO,
        curso_academico=YEAR,
        url_plan_estudios=api_url(YEAR),
        ects_totales_plan=RUCT["total"],
        estrategia_fuente=("API JSON pública de la UPM (wapi_upm, plan 56IM) para el plan de estudios; guías en PDF "
                           "por asignatura en GAUSS (www.upm.es/comun_gauss/publico/guias/), comprobadas una a una."),
        generado_por="discover_es_politecnica_madrid.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(f"Centro único: {CENTRO}. Plan 56IM (RUCT 2502150, RD 1393/2007), único título de la entrada. "
               f"{len(entries)} asignaturas ofertadas en {YEAR} ({len(no_ofertadas)} entradas de la API con "
               f"ofertada='N' quedan fuera: códigos duplicados sin docencia y nivelación de inglés). "
               f"ECTS ofertados {ofertado:g} frente a {RUCT['total']:g} del plan: formación básica "
               f"{suma['formacion_basica']:g}, obligatorias {suma['obligatoria']:g} y TFG {suma['tfg']:g} coinciden "
               f"con el RUCT; se ofertan {suma['optativa']:g} ECTS optativos y el estudiante cursa "
               f"{RUCT['optativos']:g} (la API clasifica como optativas las asignaturas de tecnología específica "
               f"de los itinerarios, las optativas cedidas por otros grados del centro, las prácticas en empresa, "
               f"17 'optativas de movilidad' de reconocimiento y la oferta en inglés). "
               f"Guías: {origen[YEAR]} de {YEAR}, {origen[YEAR_PREV]} de {YEAR_PREV} (la de {YEAR} no está "
               f"publicada; se indica en curso_semestre), {origen['sin_guia']} sin guía ({', '.join(sin)}). "
               f"semestre es null en asignaturas anuales/indefinidas o impartidas en ambos semestres."),
    )
    catalog = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{NOMBRE_GRADO} [{YEAR}]: {len(entries)} asignaturas, {ofertado:g} ECTS ofertados -> {out}")
    print("ECTS por carácter:", suma, "| guías:", origen)
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
