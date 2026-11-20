#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universitat Politècnica de València, Grado en Ingeniería Mecánica
(RUCT 2502182). Centro elegido: Florida Universitària (primer centro del RUCT; centro adscrito).

Por qué no el portal principal de la UPV: el plan de estudios y las guías de www.upv.es viven bajo
/pls/ (sic_pla.*, sic_asi.*) y /policonsulta/, y su robots.txt los prohíbe (Disallow: /pls/,
/policonsulta/c/). No se descarga nada de ahí.

Fuente usada (robots.txt de floridauniversitaria.es: Allow: /; guiasdocentes.floridauniversitaria.es
no tiene robots.txt):
  1. https://www.floridauniversitaria.es/titulacion/grado-en-ingenieria-mecanica/
     HTML estático; pestaña "Plan de estudios por cursos": un contenedor por curso con bloques por
     tipo de asignatura y una fila por asignatura (nombre, semestre, ECTS, data-asignatura=id).
  2. POST .../wp-content/themes/florida/theme/ajax/ws_asignatura.php {id, nombre} -> JSON con el HTML
     de la ficha: enlace "Ver guía docente" (PDF por asignatura), curso, idioma y créditos.
El código de asignatura es el id numérico del propio portal (data-asignatura).

Uso (desde la raíz del proyecto):
    python universidades/es_politecnica_valencia/discover_es_politecnica_valencia.py
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
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_politecnica_valencia"
UNIVERSIDAD = "Universitat Politècnica de València (Florida Universitària)"
NOMBRE_GRADO = "Grado en Ingeniería Mecánica"
PLAN_URL = "https://www.floridauniversitaria.es/titulacion/grado-en-ingenieria-mecanica/"
AJAX = "https://www.floridauniversitaria.es/wp-content/themes/florida/theme/ajax/ws_asignatura.php"
RUCT = {"basica": 60.0, "obligatorios": 120.0, "optativos": 48.0, "practicas": 0.0, "tfg": 12.0, "total": 240.0}
ORD = {"primer": 1, "segundo": 2, "tercer": 3, "cuarto": 4}
ZW = dict.fromkeys(map(ord, "​‌‍﻿"))


def clean(s: str) -> str:
    return re.sub(r"\s+", " ", s.translate(ZW)).strip()


def caracter(title: str) -> str:
    t = clean(title).lower()
    if "básica" in t or "basica" in t:
        return "formacion_basica"
    if "trabajo fin" in t:
        return "tfg"
    if "optativa" in t or "intensificaci" in t:
        return "optativa"
    return "obligatoria"  # común a la rama industrial, especialidad mecánica, formación obligatoria


def parse_plan(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    order = {id(t): i for i, t in enumerate(soup.find_all(True))}
    stop = next(b for b in soup.find_all("button") if "bloques curriculares" in clean(b.get_text()).lower())
    limit = order[id(stop)]
    rows: list[dict] = []
    for cont in soup.find_all("div", class_="titulaciones__plan-de-estudios"):
        if order[id(cont)] > limit:  # "Bloques curriculares": otra vista de las mismas asignaturas
            break
        lab = cont.find_previous(string=re.compile(r"(primer|segundo|tercer|cuarto) curso", re.I))
        year = ORD[re.search(r"(primer|segundo|tercer|cuarto)", lab, re.I).group(1).lower()]
        for blk in cont.select("div.titulaciones__plan-de-estudios__tipos__item"):
            title = clean(blk.find(True).get_text(" "))
            for r in blk.select("div.titulaciones__plan-de-estudios__tipos__item__asignaturas__item"):
                sp = r.find_all("span")
                ws = r.select_one(".ws-asignatura")
                rows.append({
                    "curso": year, "bloque": title, "nombre": clean(r.select_one(".ws-nombre").get_text()),
                    "sem": clean(sp[1].get_text()), "ects": (float(clean(sp[2].get_text()).replace(",", ".")) if re.fullmatch(r"[\d.,]+", clean(sp[2].get_text())) else None),
                    "ects_txt": clean(sp[2].get_text()),
                    "id": ws.get("data-asignatura") if ws else None,
                })
    return rows


def main() -> int:
    t0 = time.time()
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    plan = parse_plan(http.get_text(PLAN_URL))
    entries: list[CatalogEntry] = []
    sin_id, errores, seen = [], [], set()
    placeholders = []
    for r in plan:
        if not r["id"] and re.match(r"intensificaci", r["nombre"], re.I):  # fila-marcador: el bloque INTENSIFICACIÓN A/B lista las reales
            placeholders.append(r["nombre"])
            continue
        base = dict(universidad=UNIVERSIDAD, nombre_grado=NOMBRE_GRADO, nombre_asignatura=r["nombre"],
                    curso=r["curso"], creditos_ects=r["ects"], caracter=caracter(r["bloque"]))
        sem = int(r["sem"]) if r["sem"].isdigit() else None
        sem_txt = f"Semestre {r['sem']}" if sem else "Anual"
        track = f" · {clean(r['bloque'])}" if "intensificaci" in r["bloque"].lower() else ""
        base["curso_semestre"] = f"Curso {r['curso']} / {sem_txt}{track}"
        base["semestre"] = (r["curso"] - 1) * 2 + sem if sem else None
        if not r["id"]:
            code = "SG-" + re.sub(r"\W+", "-", r["nombre"].lower()).strip("-")[:40]
            sin_id.append(r["nombre"])
            entries.append(CatalogEntry(**base, codigo_asignatura=code, idioma_pagina="es", tipo_fuente="sin_guia"))
            continue
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        url, lang = None, "es"
        try:
            j = json.loads(http.get_bytes(AJAX, method="POST", data={"id": r["id"], "nombre": r["nombre"]}))
            html = j.get("content", "")
            m = re.search(r'href="(https://guiasdocentes\.floridauniversitaria\.es/[^"]+\.pdf)"', html)
            url = m.group(1) if m else None
            if url:  # el enlace del portal a veces está roto: se comprueba (y queda en caché para el scraper)
                try:
                    http.get_bytes(url)
                except FetchError as e:
                    errores.append(f"{r['id']} {r['nombre']}: PDF no disponible ({str(e)[:40]})")
                    url = None
            im = re.search(r"Idioma:\s*([A-Za-zñÑáéíóú]+)", BeautifulSoup(html, "lxml").get_text(" "))
            lang = {"castellano": "es", "inglés": "en", "ingles": "en", "valenciano": "ca", "catalán": "ca"}.get(
                (im.group(1) if im else "castellano").lower(), "es")
        except (FetchError, ValueError) as e:
            errores.append(f"{r['id']} {r['nombre']}: {e}")
        entries.append(CatalogEntry(**base, codigo_asignatura=r["id"], idioma_pagina=lang,
                                    url_guia_docente=url, tipo_fuente="pdf" if url else "sin_guia"))

    suma: dict[str, float] = {}
    for e in entries:
        suma[e.caracter] = suma.get(e.caracter, 0) + (e.creditos_ects or 0)
    total = sum(suma.values())
    sg = [f"{e.codigo_asignatura} {e.nombre_asignatura}" for e in entries if e.tipo_fuente == "sin_guia"]
    notas = (
        "Centro: Florida Universitària (primer centro del título RUCT 2502182, RD 1393/2007; centro adscrito a la UPV); "
        "los otros centros del RUCT son la EPS de Alcoy y la ETSIADI (no recogidos). El plan y las guías del portal "
        "www.upv.es (/pls/…, /policonsulta/) están prohibidos por su robots.txt (Disallow: /pls/), por eso se usa el "
        "portal propio del centro. Se toma la pestaña 'Plan de estudios por cursos' (la pestaña 'Bloques curriculares' "
        "repite las mismas asignaturas con otra ordenación y se ignora). "
        f"{len(entries)} filas, {total:g} ECTS ofertados frente a 240 del plan; por carácter: "
        + ", ".join(f"{k} {v:g}" for k, v in sorted(suma.items()))
        + ". RUCT: básica 60 / obligatorios 120 / optativos 48 / prácticas 0 / TFG 12. "
        "Obligatorias = bloques 'Común a la rama industrial' + 'Especialidad Mecánica' (60+60 = 120, coincide con el RUCT). "
        "Básica 60 y TFG 12 coinciden. Optativas listadas: las dos intensificaciones (A Mecánica, B Electromecánica; "
        "alternativas entre sí), lenguas extranjeras, informática aplicada, optativas de 4.º y Prácticas externas "
        "(ECTS variables, no sumadas). "
        f"Filas-marcador omitidas: {placeholders}. Prácticas externas figura con ECTS variables ('6 a 18'): creditos_ects=null. "
        f"Filas sin guía: {sg or 'ninguna'}. Errores de red: {errores or 'ninguno'}. Código = id numérico del portal."
    )
    cat = Catalog(
        meta=CatalogMeta(
            universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=NOMBRE_GRADO, curso_academico="2026-27",
            url_plan_estudios=PLAN_URL, ects_totales_plan=240.0,
            estrategia_fuente="HTML estático del portal de Florida Universitària (plan por cursos) + POST AJAX por "
                              "asignatura que devuelve el enlace al PDF de la guía en guiasdocentes.floridauniversitaria.es.",
            generado_por="discover_es_politecnica_valencia.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
            estado="ok", notas=notas),
        asignaturas=entries,
    )
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes)), "códigos duplicados"
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(entries)} asignaturas -> {out} | {suma} total {total:g} | sin_guia {len(sg)} | errores {len(errores)} "
          f"| red/caché {http.stats} | {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
