#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universidade de Lisboa (Instituto Superior Técnico),
Licenciatura Bolonha em Engenharia Mecânica (LEMec21, 180 ECTS).

La Universidade de Lisboa es una federación de escuelas; la titulación equivalente a Ingeniería
Mecánica es la del IST (Fénix, fenix.tecnico.ulisboa.pt; sin robots.txt: 404).

  1. Estructura: página pública del currículo `/cursos/leic-a/curriculo?year={id A.A.}` (HTML, un bloque
     por "Ano N, Semestre M" con nombre, créditos y enlace `disciplina-curricular/{id}`).
  2. Guías: API pública `/api/fenix/v1/degrees/{id}/courses?academicTerm=2025/2026` (acrónimo, créditos,
     id de la ejecución) y `/api/fenix/v1/courses/{id}` (programa, bibliografía, evaluación).
  Las filas del currículo se emparejan con la API por nombre normalizado (sin acentos/espacios).
  Curso académico de referencia: 2025/2026 (último completo; 2026/27 aún sin evaluación publicada).

Uso (desde la raíz del proyecto):
    python universidades/ec_p_lisboa109__info/discover_ec_p_lisboa109__info.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_p_lisboa109__info"
UNIVERSIDAD = "Universidade de Lisboa (Instituto Superior Técnico)"
HOST = "https://fenix.tecnico.ulisboa.pt"
API = HOST + "/api/fenix/v1"
DEGREE_ID = "2761663971474"          # LEMec21 (de /degrees?academicTerm=2025/2026)
TERM = "2025/2026"
CURRICULO = HOST + "/cursos/leic-a/curriculo"
NOMBRE_GRADO = "Licenciatura em Engenharia Informática e de Computadores - Alameda (LEIC-A)"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    deg = http.get_json(f"{API}/degrees/{DEGREE_ID}?academicTerm={TERM}")
    assert deg["acronym"] == "LEIC-A" and deg["type"].startswith("Licenciatura")

    # --- año académico de la página del currículo
    page0 = http.get_text(CURRICULO)
    m = re.search(r'href="\?year=(\d+)">' + re.escape(TERM) + "<", page0)
    if not m:
        raise RuntimeError("no encuentro el A.A. 2025/2026 en el selector del currículo")
    curr_url = f"{CURRICULO}?year={m.group(1)}"
    soup = BeautifulSoup(http.get_text(curr_url), "lxml")

    # --- API: cursos del grado en el A.A.
    api_courses = http.get_json(f"{API}/degrees/{DEGREE_ID}/courses?academicTerm={TERM}")
    by_name: dict[str, list[dict]] = {}
    for c in api_courses:
        by_name.setdefault(norm(c["name"]), []).append(c)

    entries, unmatched, total = [], [], 0.0
    for h4 in soup.find_all("h4"):
        mm = re.match(r"Ano (\d), Semestre (\d)", h4.get_text(" ", strip=True))
        if not mm:
            continue
        ano, sem = int(mm.group(1)), int(mm.group(2))
        for row in h4.find_all_next("div", class_="row"):
            nxt = row.find_previous("h4")
            if nxt is not h4:
                break
            a = row.find("a", href=re.compile("disciplina-curricular"))
            if not a:
                continue
            name = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
            cr = re.search(r"([\d.]+)\s*Cr", row.get_text(" ", strip=True))
            credits = float(cr.group(1)) if cr else None
            cid = a["href"].rsplit("/", 1)[1]
            hit = by_name.get(norm(name))
            if hit:
                c = hit[0]
                code, url = c["acronym"], f"{API}/courses/{c['id']}"
                tipo = "api"
            else:
                code, url, tipo = f"DC{cid}", None, "sin_guia"
                unmatched.append(name)
            total += credits or 0
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=NOMBRE_GRADO,
                codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=f"Ano {ano} / Semestre {sem} / {TERM}",
                curso=ano, semestre=(ano - 1) * 2 + sem, creditos_ects=credits,
                caracter="obligatoria", idioma_pagina="pt",
                url_guia_docente=url, tipo_fuente=tipo,
            ))
    codes = [e.codigo_asignatura for e in entries]
    dup = {c for c in codes if codes.count(c) > 1}
    for e in entries:                                  # mismo acrónimo en dos filas del currículo
        if e.codigo_asignatura in dup:
            e.codigo_asignatura += f"_{e.curso}{e.semestre}"
    assert len({e.codigo_asignatura for e in entries}) == len(entries), "códigos duplicados"
    assert all(e.url_guia_docente or e.tipo_fuente == "sin_guia" for e in entries)
    n_sin = sum(e.tipo_fuente == "sin_guia" for e in entries)

    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=NOMBRE_GRADO, nivel="bachelor",
        curso_academico=TERM, url_plan_estudios=curr_url, ects_totales_plan=None,
        estrategia_fuente=("HTML del currículo de Fénix (estructura año/semestre/créditos) + API pública "
                           "Fénix /api/fenix/v1 (cursos del grado y ficha por curso), emparejados por nombre."),
        generado_por="discover_ec_p_lisboa109__info.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial",
        notas=(f"Segunda titulación afín (familia info) del destino P LISBOA109 (IST): Licenciatura em Engenharia Informática e de Computadores - Alameda (LEIC-A), 1.er ciclo. {len(entries)} filas, suma créditos {total:g}; {n_sin} sin_guia. Fichas pt vía API Fénix (solo programa, bibliografía, evaluación). Parcial: optativas/ramas pueden duplicar créditos."),
    )
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{NOMBRE_GRADO}: {len(entries)} filas, {total:g} créditos, sin_guia={n_sin} -> {out}")
    if unmatched:
        print("sin emparejar:", unmatched)
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
