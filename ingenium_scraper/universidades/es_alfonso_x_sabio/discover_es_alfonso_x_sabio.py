#!/usr/bin/env python3
"""Fase 1 — Universidad Alfonso X el Sabio, Grado en Ingeniería Mecánica (plan 2020, EIAD Villanueva de la Cañada).
Fuente: PDF compartido con todas las guías (403 págs.); cada guía empieza en una portada «GUÍA DE LA ASIGNATURA».
Uso: python universidades/es_alfonso_x_sabio/discover_es_alfonso_x_sabio.py"""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_alfonso_x_sabio", "Universidad Alfonso X El Sabio"
GRADO = "Grado en Ingeniería Mecánica"
PDF = "https://www.uax.com/download/8642/file/GMC_Guias_Docentes_plan_2020.pdf"
CAR = {"FORMACIÓN BÁSICA": "formacion_basica", "OBLIGATORIA": "obligatoria", "OPTATIVA": "optativa"}
RUCT = {"formacion_basica": 60, "obligatoria": 150}


def cover(text):
    """Devuelve (codigo, nombre, curso, periodo, ects, caracter) de una portada o None."""
    lines = text.split("\n")
    if "GUÍA DE LA ASIGNATURA" not in "\n".join(lines[:4]):
        return None
    i = next(k for k, l in enumerate(lines) if "GUÍA DE LA ASIGNATURA" in l)
    head = []
    for l in lines[i + 1:]:
        if l.startswith("PROFESORES"):
            break
        head.append(l.strip())
    s = " ".join(head)
    m = re.match(r"(.*?)\s*CURSO\s+(\d)º\s+(.*?)\s+ECTS\s+([\d.,]+)\s+(.+)$", s)
    if not m:
        return None
    pre, curso, periodo, ects, car = m.groups()
    mc = re.search(r"\b(\d{7})\b", pre)
    if not mc:
        return None
    name = re.sub(r"\s+", " ", pre.replace(mc.group(1), " ")).strip()
    return mc.group(1), name, int(curso), periodo.strip().lower(), float(ects.replace(",", ".")), car.strip().upper()


def main():
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf = http.get_file(PDF)
    starts = []
    with pdfplumber.open(pdf) as d:
        total = len(d.pages)
        for n, pg in enumerate(d.pages, 1):
            c = cover((pg.extract_text() or "")[:600])
            if c:
                starts.append((n, c))
    entries, seen = [], {}
    for k, (n, (code, name, curso, periodo, ects, car)) in enumerate(starts):
        fin = starts[k + 1][0] - 1 if k + 1 < len(starts) else total
        seen[code] = seen.get(code, 0) + 1
        key = code if seen[code] == 1 else f"{code}-{seen[code]}"
        sem = None
        if "primer" in periodo:
            sem = curso * 2 - 1
        elif "segundo" in periodo or "segfundo" in periodo:
            sem = curso * 2
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=key, nombre_asignatura=name,
            curso_semestre=f"Curso {curso} / {periodo}", curso=curso, semestre=sem, creditos_ects=ects,
            caracter="tfg" if "Proyecto Fin de Grado" in name else CAR[car], idioma_pagina="es",
            url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{n}-{fin}"))
    assert len({e.codigo_asignatura for e in entries}) == len(entries)
    s = {}
    for e in entries:
        s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
    print(len(entries), s)
    dups = [c for c, v in seen.items() if v > 1]
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=PDF, ects_totales_plan=240.0,
        estrategia_fuente="PDF compartido con todas las guías del plan 2020; las portadas «GUÍA DE LA ASIGNATURA» delimitan cada guía (rango de páginas derivado).",
        generado_por="discover_es_alfonso_x_sabio.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"{len(entries)} guías del plan 2020 (EIAD, campus de Villanueva de la Cañada); el PDF no indica el curso académico de la edición. "
               f"ECTS por carácter {json.dumps(s)} frente al RUCT (básica 60, obligatorias 150, optativas 18, TFG 12): se ofertan más optativas de las 18 exigidas; básica+obligatoria = 210 como en el RUCT, aunque el PDF clasifica 6 ECTS como básica que el RUCT cuenta como obligatorios. "
               f"El PDF repite códigos en distintas asignaturas ({', '.join(dups) or 'ninguno'}): el segundo se sufija «-2». "
               "Códigos y datos tal como figuran en las portadas (hay erratas del PDF, p. ej. 0241820 figura como curso 1º)."))
    (HERE / "catalogo_urls.json").write_text(json.dumps(Catalog(meta=meta, asignaturas=entries).model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
