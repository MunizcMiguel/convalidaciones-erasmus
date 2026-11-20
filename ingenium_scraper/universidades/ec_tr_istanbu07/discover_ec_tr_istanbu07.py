"""Fase 1 - Yildiz Technical University (TR ISTANBU07): Kimya Muhendisligi (Chemical Engineering, lisans, %100 Ingilizce, 240 AKTS).
Sistema Bologna de la universidad: http://www.bologna.yildiz.edu.tr (Yii, HTML por GET, sin robots.txt; ojo: el host sin "www" falla por TLS y no se usa).
 Plan: index.php?r=program/view&id=398&aid=23 (tablas por semestre, filas Kodu/Onk./Ders Adi/.../AKTS con enlace course/view); ficha: index.php?r=course/view&id=..&aid=23&pid=36
Uso: python universidades/ec_tr_istanbu07/discover_ec_tr_istanbu07.py
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
SLUG = "ec_tr_istanbu07"
UNIVERSIDAD = "Yıldız Teknik Üniversitesi (Yildiz Technical University) - Kimya-Metalurji Fakültesi"
GRADO = "Kimya Mühendisliği (Chemical Engineering), lisans, %100 İngilizce"
BASE = "http://www.bologna.yildiz.edu.tr/"
URL_PLAN = BASE + "index.php?r=program/view&id=398&aid=23"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=2, timeout=30)
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    entries, seen, skipped, dup = [], set(), [], 0
    for tb in s.find_all("table"):
        if tb.find("tr", class_="table_semester_heading") is None:
            continue
        year = sem = None
        pool = ""
        for tr in tb.find_all("tr"):
            if "table_semester_heading" in (tr.get("class") or []):
                ht = tr.get_text(" ", strip=True)
                m = re.match(r"(\d)\.\s*Y[ıi]l\s*-\s*(Güz|Bahar)", ht)
                if m:
                    year, sem, pool = int(m.group(1)), (1 if m.group(2) == "Güz" else 2), ""
                    semtxt = m.group(2)
                else:
                    year = sem = None
                    pool = ht
                continue
            tds = tr.find_all("td")
            if len(tds) < 8:
                continue
            a = tds[0].find("a", href=True)
            code = tds[0].get_text(strip=True)
            name = re.sub(r"\s+", " ", tds[2].get_text(" ", strip=True))
            ects = float(tds[7].get_text(strip=True).replace(",", ".") or 0)
            if not a or "id=&" in a["href"] or not code:
                skipped.append(f"{pool or f'Y{year}S{sem}'}:{code} {name[:40]} ({ects:g})")
                continue
            if code in seen:
                dup += 1
                continue
            seen.add(code)
            if pool:
                car = "practicas" if "KOOP" in pool else "optativa"
                cs, cu, se = pool, None, None
            else:
                car, cs, cu, se = "obligatoria", f"Yıl {year} / {semtxt} (Semestre {(year - 1) * 2 + sem})", year, (year - 1) * 2 + sem
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=cs, curso=cu, semestre=se, creditos_ects=ects,
                caracter=car, idioma_pagina="tr", url_guia_docente=urljoin(BASE, a["href"].replace("&amp;", "&")), tipo_fuente="html"))
    tot = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    nopt = sum(1 for e in entries if e.caracter != "obligatoria")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="vigente en el Bologna Bilgi Sistemi (Yeni)", url_plan_estudios=URL_PLAN, ects_totales_plan=240.0,
        estrategia_fuente="HTML del Bologna Bilgi Sistemi de YTU: tablas por semestre en program/view + ficha HTML por asignatura en course/view",
        generado_por="discover_ec_tr_istanbu07.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Titulación elegida: Kimya Mühendisliği (Chemical Engineering, programa %100 inglés id 398): el Excel solo trae Grado en Ingeniería Química Industrial para este destino (1 plaza, ISCED 0711), equivalente directo. "
               f"{len(entries)} filas, obligatorias suman {tot:g} ECTS + {nopt} asignaturas de las bolsas de optativas/KOOP (sin semestre; el plan completo suma 240), {dup} repeticiones descartadas. Huecos sin ficha/código (grupos de optativas): {skipped}. La ficha está en turco (el sistema no ofrece versión inglesa estática; «Dersin Dili» indica el idioma de impartición). "
               "El host sin www (bologna.yildiz.edu.tr) falla por certificado; se usa http://www.bologna.yildiz.edu.tr, el enlace oficial de www.yildiz.edu.tr/en. Hint del Excel (relint.uva.es) es un PDF de otra universidad."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas", tot, "ECTS; huecos:", skipped, "dup", dup)


if __name__ == "__main__":
    main()
