"""Fase 1 - Bartin University (Bartin Universitesi), Muhendislik, Mimarlik ve Tasarim Fakultesi: Makine Muhendisligi (Mechanical Engineering).
Fuente: plan de estudios PDF (2024 en adelante) enlazado desde makine.bartin.edu.tr/egitimogretim/lisans.html.
Las fichas de asignatura estan en el Bologna Bilgi Paketi de UBYS (ubys.bartin.edu.tr/AIS/OutcomeBasedLearning), una SPA JS con ids cifrados
y endpoints AJAX: no se usa (sin navegador automatizado) -> todas sin_guia, catalogo parcial, sin Fase 2.
Uso: python universidades/ec_tr_bartin01/discover_ec_tr_bartin01.py
"""
from __future__ import annotations

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
SLUG = "ec_tr_bartin01"
UNIVERSIDAD = "Bartın Üniversitesi - Mühendislik, Mimarlık ve Tasarım Fakültesi"
GRADO = "Makine Mühendisliği (Mechanical Engineering), lisans"
URL_PLAN = "https://cdn.bartin.edu.tr/makine/b9d8b3ac-1aa9-4f72-afb0-2d03e77f9ef1/makine-muhendisligi-2024-sonrasi-ders-plani.pdf"
URL_PAGINA = "https://makine.bartin.edu.tr/egitimogretim/lisans.html"
URL_BOLOGNA = "https://ubys.bartin.edu.tr/AIS/OutcomeBasedLearning/Home/Index?culture=en-US"
COURSE = re.compile(r"([A-ZİÇŞĞÜÖ]{2,5}\d{3})\s+(.+?)\s+([ZS])\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
PLACEHOLDER = re.compile(r"((?:Seçmeli|Bölüm Seçmeli|Fakülte Seçmeli|Serbest)[^\d\n]*?)\s+S\s+(?:\d+\s+\d+\s+\d+\s+)?(\d+)\b")


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    entries, seen, tot_sem, placeholders = [], set(), {}, []
    with pdfplumber.open(c.get_file(URL_PLAN)) as pdf:
        text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    sems = (0, 0)
    for line in text.splitlines():
        m = re.search(r"(\d)\. YARIYIL \(\w+\)\s+(\d)\. YARIYIL", line)
        if m:
            sems = (int(m.group(1)), int(m.group(2)))
            continue
        m = re.search(r"(\d)\. Yarıyılda Alınması Gereken AKTS Toplamı (\d+)(?:\s+(\d)\. Yarıyılda Alınması Gereken AKTS Toplamı (\d+))?", line)
        if m:
            tot_sem[int(m.group(1))] = float(m.group(2))
            if m.group(3):
                tot_sem[int(m.group(3))] = float(m.group(4))
            continue
        if not sems[0]:
            continue
        for k, mm in enumerate(COURSE.finditer(line)):
            code, name, zs, t, u, kr, akts = mm.groups()
            sem = sems[min(k, 1)]
            if code in seen:
                continue
            seen.add(code)
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name.strip(),
                curso_semestre=f"Curso {(sem + 1) // 2} / Yarıyıl {sem}", curso=(sem + 1) // 2, semestre=sem, creditos_ects=float(akts),
                caracter="obligatoria" if zs == "Z" else "optativa", idioma_pagina="tr", url_guia_docente=None, tipo_fuente="sin_guia"))
        for mm in PLACEHOLDER.finditer(line):
            placeholders.append(f"S{sems[0]}/{sems[1]}: {mm.group(1).strip()} ({mm.group(2)})")
    comp = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    tot = sum(tot_sem.values())
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2024/2025 (plan para ingresados desde 2024)", url_plan_estudios=URL_PAGINA,
        ects_totales_plan=tot or None, estrategia_fuente="Plan de estudios PDF (texto a dos columnas por semestre, regex por fila de curso); fichas fuera de alcance",
        generado_por="discover_ec_tr_bartin01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Makine Mühendisliği (lisans, 4 años). Plan PDF 2024-sonrası: {len(entries)} asignaturas con código (obligatorias {comp:g} ECTS); los cupos de seleccionables sin código se cuentan en el total por semestre "
               f"({tot_sem}, total {tot:g}) y no se catalogan como filas: {placeholders}. "
               "PARCIAL: todas sin_guia. Las fichas están en el Bologna Bilgi Paketi (ubys.bartin.edu.tr/AIS/OutcomeBasedLearning, ASP.NET MVC con SPA JS, ids cifrados y endpoints AJAX POST "
               "como GetCurriculumDetail); no se usa navegador automatizado ni se reproducen llamadas internas. bubp.bartin.edu.tr solo da información institucional y reenvía a UBYS. "
               "robots.txt de ubys solo veta /ECM/…; el motivo de parada es técnico (SPA). Hint erasmusen.bartin.edu.tr = web Erasmus (sin catálogo). Idioma: turco."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; obligatorias", comp, "total plan", tot, tot_sem, "\n", placeholders)


if __name__ == "__main__":
    main()
