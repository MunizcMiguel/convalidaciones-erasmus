#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universitatea din Oradea (Fac. de Inginerie Electrică și Tehnologia Informației), Electromechanics (B.Eng.).

Fuentes (inglés, sitio ieti.uoradea.ro):
 - Plan: PDF «Curriculum» EM_EN_2026-2027.pdf (código IETI-xxxx, nombre, créditos, año/semestre; 4 págs.).
 - Fichas: PDF compartido FD_licenta_EM_EN_2024-2025.pdf (289 págs., «SUBJECT DESCRIPTION», una o varias págs. por asignatura).
 El enlace plan -> ficha se hace por nombre normalizado (las fichas no llevan código).

Uso: python universidades/ec_ro_oradea01/discover_ec_ro_oradea01.py
"""
from __future__ import annotations

import difflib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_ro_oradea01"
UNIVERSIDAD = "Universitatea din Oradea (Fac. Electrical Engineering and Information Technology)"
BASE = "https://ieti.uoradea.ro/images/zEN/Programmes/"
CURR = BASE + "curriculum/EM_EN_2026-2027.pdf"
FICHAS = BASE + "Bachelor_degree_programmes/2024_2025/FD_licenta_EM_EN_2024-2025.pdf"
PLAN = "https://ieti.uoradea.ro/index.php/en/programmes-mm/bachelor-degree-study-programmes"
GRADO = "Electromechanics (B.Eng., Electrical Engineering field, 4 years / 240 credits)"
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8}
ROW = re.compile(r"^(IETI-\d+)\s+(.+?)\s+(FD|SD|DD|CD)\s+(?:\d+|-)\s+(?:\d+|-)\s+(?:\d+|-)\s+(?:\d+|-)\s+\d+\s+(Ex|Vp|A/R|C|V)\s+(\d+)\s+\d+\s*$")


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def pages_text(http: PoliteClient, url: str, cache: Path) -> list[str]:
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    with pdfplumber.open(http.get_file(url)) as d:
        pages = [(p.extract_text() or "") for p in d.pages]
    cache.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    return pages


def sheets(pages: list[str]) -> list[dict]:
    """Una ficha empieza en la página cuyo texto comienza por 'SUBJECT DESCRIPTION'."""
    starts = [i for i, t in enumerate(pages) if t.strip().startswith("SUBJECT DESCRIPTION")]
    out = []
    for k, s in enumerate(starts):
        e = (starts[k + 1] if k + 1 < len(starts) else len(pages)) - 1
        t = pages[s]
        m = re.search(r"2\.1 Name of the subject\s+(.+)", t)
        y = re.search(r"2\.4 Year of\s+(\d)\s+2\.5\s+(\d)", t)
        out.append(dict(name=m.group(1).strip() if m else "", ini=s + 1, fin=e + 1,
                        year=int(y.group(1)) if y else None, sem=int(y.group(2)) if y else None))
    return out


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    cur = pages_text(http, CURR, HERE / "raw_cache" / "curriculum_pages.json")
    fich = pages_text(http, FICHAS, HERE / "raw_cache" / "fichas_pages.json")
    sh = sheets(fich)
    rows, year, sem, bloque = [], None, None, None
    for t in cur:
        for ln in t.split("\n"):
            s = ln.strip()
            m = re.match(r"Year of study (I|II|III|IV)\b", s)
            if m:
                year = ROMAN[m.group(1)]
            m = re.match(r"Sem\. ([IVX]+)\b", s)
            if m:
                sem = ROMAN[m.group(1)]
                bloque = "OBLIGATORII"
            if s in ("OBLIGATORII", "FACULTATIVE") or (s.startswith("OP") and s.endswith("ALE")):
                bloque = s
            m = ROW.match(s)
            if m and year and sem and bloque != "FACULTATIVE":
                rows.append(dict(code=m.group(1), name=m.group(2), tipo=m.group(3), cred=float(m.group(5)),
                                 year=year, sem=sem, bloque=bloque))
    # emparejamiento global (mejor puntuación primero) plan -> ficha
    uniq, seen = [], set()
    for r in rows:
        if r["code"] not in seen:
            seen.add(r["code"])
            uniq.append(r)
    pairs = sorted(((difflib.SequenceMatcher(None, norm(r["name"]), norm(x["name"])).ratio() + (0.05 if x["year"] == r["year"] else 0), ri, si)
                    for ri, r in enumerate(uniq) for si, x in enumerate(sh) if x["name"]), reverse=True)
    assign, used_r, used_s = {}, set(), set()
    for sc, ri, si in pairs:
        if sc < 0.85:
            break
        if ri in used_r or si in used_s:
            continue
        assign[ri] = si
        used_r.add(ri)
        used_s.add(si)
    entries = []
    for ri, r in enumerate(uniq):
        ok = ri in assign
        best = (0, assign.get(ri))
        x = sh[best[1]] if ok else None
        low = r["name"].lower()
        car = ("tfg" if "diploma" in low or "graduation" in low else "practicas" if "practice" in low or "internship" in low
               else "optativa" if r["bloque"] and r["bloque"].startswith("OP") else "obligatoria")
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=r["code"], nombre_asignatura=r["name"],
            curso_semestre=f"Year {r['year']} / Semester {r['sem']} / {r['bloque']} / type {r['tipo']}",
            curso=r["year"], semestre=r["sem"], creditos_ects=r["cred"], caracter=car, idioma_pagina="en",
            url_guia_docente=FICHAS if ok else None, tipo_fuente="pdf_compartido" if ok else "sin_guia",
            paginas_pdf=f"{x['ini']}-{x['fin']}" if ok else None))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    n_sin = sum(e.tipo_fuente == "sin_guia" for e in entries)
    tot = sum(e.creditos_ects for e in entries if e.caracter != "optativa")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/27 (plan) / 2024/25 (fichas)",
        url_plan_estudios=PLAN, ects_totales_plan=240.0,
        estrategia_fuente="Dos PDF en inglés de ieti.uoradea.ro: plan (curriculum) y PDF compartido de fichas; enlace por nombre normalizado + año.",
        generado_por="discover_ec_ro_oradea01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok" if n_sin <= len(entries) // 5 else "parcial",
        notas=("Filas Erasmus de Oradea: Grado Ing. Tecnologías Industriales (2 plazas), Máster Ing. Energética e Ing. Industrial (sin plazas). "
               "Se elige Electromechanics (B.Eng., 240 créditos / 4 años, Facultad IETI): la titulación con plan y fichas en inglés más afín a Tecnologías Industriales/Mecánica "
               "(incluye Elements of mechanical engineering, Strength of materials and mechanisms, Electrical machines, Technological methods). "
               "No se exploró la Facultad de Ingeniería de Gestión y Tecnológica (posible Mechanical Engineering): no verificado. "
               f"Plan = curriculum 2026/27; fichas = PDF 2024/25 (289 págs.). Créditos locales (240 en 4 años; se omiten FACULTATIVE). Suma de créditos de filas no optativas: {tot:g}. "
               f"{n_sin} filas sin ficha emparejada (sin_guia): asignaturas nuevas o renombradas desde 2024/25. Códigos IETI-xxxx del plan; las fichas carecen de código y se unen por nombre (umbral 0,85)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(entries)} filas ({len(sh)} fichas en el PDF), sin_guia={n_sin}, créditos no optativos={tot:g}; HTTP {http.stats}")


if __name__ == "__main__":
    main()
