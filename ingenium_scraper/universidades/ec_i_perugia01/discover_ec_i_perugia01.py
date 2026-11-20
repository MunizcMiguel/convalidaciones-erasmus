#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Università degli Studi di Perugia, Laurea in Ingegneria Meccanica (L-9, idcorso 8439).

Fuente: portal de la oferta formativa de UniPG (www.unipg.it, Joomla; robots permite). El catálogo
Cineca (unipg.coursecatalogue.cineca.it) está vetado por robots.txt y no se usa.

  1. Listado:  .../archivio/offerta-formativa-2025-26?view=elenco&...&idcorso=8439&tab=INS
     -> <h4>N° Anno</h4> + tabla (Insegnamento, Curriculum, CFU, Periodo, Lingua), enlace con `idins`.
  2. Ficha:    el mismo URL + `&idins={id}` -> tabla th/td (Codice insegnamento, Contenuti, Obiettivi...).

Se usa el regolamento 2025/26 (coorte 2025): el único listado con las fichas de los 3 años ya
rellenas en mayor medida. La ficha trae el código oficial (GPxxxxxx); filas sin texto = sin_guia.

Uso (desde la raíz del proyecto):
    python universidades/ec_i_perugia01/discover_ec_i_perugia01.py
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
SLUG = "ec_i_perugia01"
UNIVERSIDAD = "Università degli Studi di Perugia"
BASE = "https://www.unipg.it"
PAGE = "/didattica/corsi-di-laurea-e-laurea-magistrale/archivio/offerta-formativa-2025-26"
QS = "view=elenco&ricerca=on&annoregolamento=2025&dipartimento=516600&lingua=&nomecorso=&tipocorso=&sede=4&classe=&cerca=&idcorso=8439"
LIST_URL = f"{BASE}{PAGE}?{QS}&tab=INS"
NOMBRE_GRADO = "Corso di laurea in Ingegneria meccanica (L-9)"
FIELDS = ("Contenuti", "Obiettivi formativi", "Programma esteso", "Testi di riferimento")


def ficha_url(idins: str) -> str:
    return f"{LIST_URL}&idins={idins}"


def parse_ficha(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    out = {}
    for tr in soup.select("tr"):
        th, td = tr.find("th"), tr.find("td")
        if th and td:
            out[th.get_text(" ", strip=True)] = td.get_text(" ", strip=True)
    return out


def caracter(tipo: str, nombre: str) -> str:
    t = (tipo or "").lower()
    if "prova finale" in nombre.lower():
        return "tfg"
    if "tirocinio" in nombre.lower():
        return "practicas"
    if "obbligatorio" in t:
        return "obligatoria"
    if "opzion" in t or "scelta" in t:
        return "optativa"
    return "obligatoria"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(LIST_URL), "lxml")
    entries, total = [], {}
    seen = set()
    for h4 in soup.find_all("h4"):
        titulo = h4.get_text(" ", strip=True)
        m = re.match(r"(\d)\D*\s*Anno", titulo)
        curso = int(m.group(1)) if m else None
        grupo = titulo
        tabla = h4.find_next("table")
        for tr in tabla.select("tr")[1:]:
            tds = tr.find_all("td")
            a = tr.find("a", href=True)
            if len(tds) < 4 or not a:
                continue
            idins = re.search(r"idins=(\d+)", a["href"]).group(1)
            if idins in seen:
                continue
            seen.add(idins)
            nombre = a.get_text(" ", strip=True)
            cfu = float(re.sub(r"[^\d.]", "", tds[2].get_text()) or 0)
            periodo = tds[3].get_text(" ", strip=True)
            lingua = tds[4].get_text(" ", strip=True).lower() if len(tds) > 4 else ""
            url = ficha_url(idins)
            try:
                ficha = parse_ficha(http.get_text(url))
            except FetchError:
                ficha = {}
            code = ficha.get("Codice insegnamento") or f"ID{idins}"
            texto = any(ficha.get(k) for k in FIELDS)
            sem = None
            if curso:
                if re.search(r"primo|1", periodo, re.I) and "annuale" not in periodo.lower():
                    sem = (curso - 1) * 2 + 1
                elif re.search(r"secondo|2", periodo, re.I) and "annuale" not in periodo.lower():
                    sem = (curso - 1) * 2 + 2
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=NOMBRE_GRADO,
                codigo_asignatura=code, nombre_asignatura=nombre,
                curso_semestre=f"{grupo} / {periodo} / {tds[1].get_text(' ', strip=True)} / idins {idins}",
                curso=curso, semestre=sem, creditos_ects=cfu,
                caracter=caracter(ficha.get("Tipo insegnamento", ""), nombre) if curso else "optativa",
                idioma_pagina="en" if lingua.startswith("ingl") else "it",
                url_guia_docente=url if texto else None,
                tipo_fuente="html" if texto else "sin_guia",
            ))
            if curso:
                total[curso] = total.get(curso, 0) + cfu

    codes = [e.codigo_asignatura for e in entries]
    dup = {c for c in codes if codes.count(c) > 1}
    if dup:                                     # mismo código en varios idins: sufijo con el idins
        for e in entries:
            if e.codigo_asignatura in dup:
                e.codigo_asignatura += "_" + e.curso_semestre.rsplit("idins ", 1)[1]
    assert len({e.codigo_asignatura for e in entries}) == len(entries)
    assert all(e.url_guia_docente or e.tipo_fuente == "sin_guia" for e in entries)
    n_sin = sum(e.tipo_fuente == "sin_guia" for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=NOMBRE_GRADO, nivel="bachelor",
        curso_academico="regolamento 2025/26 (coorte 2025)", url_plan_estudios=LIST_URL,
        ects_totales_plan=180.0,
        estrategia_fuente=("HTML del portal de oferta formativa de unipg.it: listado por año "
                           "(tab=INS) + ficha por idins (tabla th/td)."),
        generado_por="discover_ec_i_perugia01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(f"{len(entries)} filas; {n_sin} sin_guia (ficha sin Contenuti/Obiettivi/Programma/Testi). "
               f"CFU por curso del listado: {total} (el listado incluye también el grupo de optativas). "
               f"Código = 'Codice insegnamento' (GPxxxxxx) de la ficha. Catálogo Cineca de UniPG vetado "
               f"por robots.txt (no usado). Idioma: la ficha está en la lengua de impartición."),
    )
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{NOMBRE_GRADO}: {len(entries)} filas, sin_guia={n_sin}, CFU {total} -> {out}")
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
