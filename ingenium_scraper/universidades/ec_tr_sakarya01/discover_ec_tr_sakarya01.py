"""Fase 1 - Sakarya University (Sakarya Universitesi), Muhendislik Fakultesi: Makine Muhendisligi (Mechanical Engineering), lisans.
Hint de la ficha Erasmus (erasmus.sakarya.edu.tr) = web Erasmus; el catalogo (Egitim Bilgi Sistemi) esta en ebs.sakarya.edu.tr.
Plan: https://ebs.sakarya.edu.tr/Birim/DersPlan/290 (HTML, una tabla por semestre) ; ficha: /Ders/Detay/{id} (HTML por GET).
Uso: python universidades/ec_tr_sakarya01/discover_ec_tr_sakarya01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_sakarya01"
UNIVERSIDAD = "Sakarya Üniversitesi (Sakarya University) - Mühendislik Fakültesi"
GRADO = "Makine Mühendisliği (Mechanical Engineering), lisans"
BASE = "https://ebs.sakarya.edu.tr/"
URL_PLAN = BASE + "Birim/DersPlan/290"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    entries, seen, sem, tot_sem, skipped, dup = [], set(), None, {}, [], 0
    for el in s.find_all(True):
        txt = el.get_text(" ", strip=True) if el.name in ("h1", "h2", "h3", "h4", "h5", "h6", "div", "span") and len(el.get_text(strip=True)) < 40 else ""
        m = re.fullmatch(r"(\d)\. Yarıyıl Ders Planı", txt)
        if m:
            sem = int(m.group(1))
            continue
        if txt == "Üniversite Ortak Ders Listesi":
            sem = None
            continue
        if el.name != "table" or sem is None:
            continue
        rows = el.find_all("tr")
        if not rows or [x.get_text(strip=True) for x in rows[0].find_all(["th", "td"])][:2] != ["Kodu", "Ders"]:
            continue
        for tr in rows[1:]:
            tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            a = tr.find("a", href=True)
            if len(tds) < 7 or not a:
                continue
            code = re.sub(r"\s+", " ", tds[0]).strip()
            if not code:  # hueco de grupo electivo sin código
                skipped.append(f"S{sem}:{tds[1][:40]} ({tds[6]})")
                continue
            if code in seen:
                dup += 1
                continue
            seen.add(code)
            ects = float(tds[6].replace(",", "."))
            comp = tds[2].lower().startswith("zorunlu")
            tot_sem[sem] = tot_sem.get(sem, 0) + (ects if comp else 0)
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=re.sub(r"\s+", " ", tds[1]).strip(),
                curso_semestre=f"Curso {(sem + 1) // 2} / Yarıyıl {sem}", curso=(sem + 1) // 2, semestre=sem, creditos_ects=ects,
                caracter="obligatoria" if comp else "optativa", idioma_pagina="en" if tds[3].lower().startswith("ingiliz") else "tr",
                url_guia_docente=urljoin(BASE, a["href"]), tipo_fuente="html"))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    comp = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    el_ = sum(e.creditos_ects for e in entries if e.caracter == "optativa")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="vigente en el EBS (2025-2026 aprox.)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=240.0, estrategia_fuente="HTML del EBS: una tabla por semestre en /Birim/DersPlan/290 + ficha HTML por asignatura en /Ders/Detay/{id}",
        generado_por="discover_ec_tr_sakarya01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Titulación: Makine Mühendisliği (lisans, Mühendislik Fakültesi, unidad EBS 290), 8 semestres. {len(entries)} filas ({dup} repeticiones de optativas entre semestres descartadas): "
               f"obligatorias {comp:g} ECTS (por semestre {tot_sem}) + optativas ofertadas {el_:g} ECTS; el plan completo suma 240 (resumen del EBS: fakülte zorunlu 42 + bölüm zorunlu 140 + bölüm seçmeli 28 + üniversite ortak 12 AKTS... "
               "verificar). Las asignaturas de la lista «Üniversite Ortak» no se catalogan salvo que figuren en las tablas de semestre. Idioma: turco. Hint erasmus.sakarya.edu.tr es la web Erasmus (el «English course catalogue» de esa web es de otras titulaciones)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("huecos", skipped); print(len(entries), "filas; obligatorias", comp, "optativas", el_, "sem", tot_sem, "dup", dup)


if __name__ == "__main__":
    main()
