"""Fase 1 - Duzce University (Duzce Universitesi), Muhendislik Fakultesi: Makine Muhendisligi (Mechanical Engineering), Normal Ogretim.
Plataforma: Egitim Bilgi Sistemi (ebs.duzce.edu.tr), HTML servido por GET: plan en /Bolum/OgretimProgrami/{bolum}?bot={bot} (una tabla por semestre,
anio 2025-2026 por defecto) y ficha en /Ders/Index/{id}?bno=..&bot=..&yilNo=...
Se usa la interfaz turca por defecto (la variante en ingles depende de una cookie y rompe la cache por URL); el contenido de las fichas esta en turco.
Uso: python universidades/ec_tr_duzce01/discover_ec_tr_duzce01.py
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

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_duzce01"
UNIVERSIDAD = "Düzce Üniversitesi - Mühendislik Fakültesi"
GRADO = "Makine Mühendisliği (Mechanical Engineering), Normal Öğretim"
BASE = "https://ebs.duzce.edu.tr/"
URL_PLAN = BASE + "Bolum/OgretimProgrami/16?bot=18"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    s = BeautifulSoup(c.get_text(URL_PLAN), "lxml")
    years = {o.get("value"): o.get_text(strip=True) for o in s.find("select", attrs={"name": "yil"}).find_all("option")} if s.find("select", attrs={"name": "yil"}) else {}
    entries, seen, tot_sem, skipped, dup_pool = [], set(), {}, [], 0
    tables = [t for t in s.find_all("table") if t.find("th") and "Kodu" in t.get_text()]
    year_no = None
    for sem, t in enumerate(tables, start=1):
        for tr in t.find_all("tr"):
            tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            a = tr.find("a", href=True)
            if len(tds) < 7 or not a:
                continue
            code = re.sub(r"\s+", "", tds[0])
            name = tds[1]
            if not code or tds[0].strip() == name or re.match(r"(?i)(PF|İBSPF)", code) or re.search(r"Seçmelisi|Seçmeli Dersler|Ders Grubu", name):
                skipped.append(f"S{sem}:{name}")  # huecos de grupo electivo y formacion pedagogica (no son asignaturas del grado)
                continue
            if code in seen:  # el mismo pool de optativas se repite en los semestres 5-8
                dup_pool += 1
                continue
            m = re.search(r"yilNo=(\d+)", a["href"])
            year_no = year_no or (m.group(1) if m else None)
            key = code
            seen.add(key)
            ects = float(tds[6].replace(",", "."))
            tot_sem[sem] = tot_sem.get(sem, 0) + (ects if tds[2].lower().startswith("evet") else 0)
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=key, nombre_asignatura=name,
                curso_semestre=f"Curso {(sem + 1) // 2} / Yarıyıl {sem}", curso=(sem + 1) // 2, semestre=sem, creditos_ects=ects,
                caracter="obligatoria" if tds[2].lower().startswith("evet") else "optativa", idioma_pagina="tr",
                url_guia_docente=urljoin(BASE, a["href"]), tipo_fuente="html"))
    # Comprobacion de enlaces: algunas fichas del plan dan 404 en origen -> sin_guia. El resultado se guarda en guias_404.json
    # (una re-ejecucion lo reutiliza; con --verify se vuelve a comprobar). Las fichas OK quedan en la cache de PoliteClient.
    f404 = HERE / "guias_404.json"
    if f404.exists() and "--verify" not in sys.argv:
        dead = set(json.loads(f404.read_text(encoding="utf-8")))
    else:
        dead = set()
        for e in entries:
            try:
                if "ebs-yazdir-tam" not in c.get_text(e.url_guia_docente):  # página vacía (sin ficha)
                    dead.add(e.codigo_asignatura)
            except FetchError as ex:
                if "HTTP 404" in str(ex):
                    dead.add(e.codigo_asignatura)
        f404.write_text(json.dumps(sorted(dead), ensure_ascii=False, indent=1), encoding="utf-8")
    for e in entries:
        if e.codigo_asignatura in dead:
            e.url_guia_docente, e.tipo_fuente = None, "sin_guia"
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    comp = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    el = sum(e.creditos_ects for e in entries if e.caracter == "optativa")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico=years.get(year_no or "", "2025 - 2026"), url_plan_estudios=URL_PLAN,
        ects_totales_plan=240.0, estrategia_fuente="HTML del EBS: una tabla por semestre en la página del programa + ficha HTML por asignatura",
        generado_por="discover_ec_tr_duzce01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Titulación: Makine Mühendisliği (Normal Öğretim; también existe İkinci Öğretim y «Makine ve İmalat Mühendisliği», no usados). Currículo yilNo={year_no} ({years.get(year_no or '', '?')}). "
               f"{len(entries)} filas: obligatorias {comp:g} ECTS, optativas ofertadas {el:g} ECTS (el alumno elige parte de ellas; total del grado 240). "
               f"Omitidos (huecos de grupo electivo/formación pedagógica, sin ficha de asignatura): {skipped}. Los pools de optativas se repiten en los semestres 5-8: {dup_pool} repeticiones descartadas, cada optativa figura en el primer semestre donde aparece. "
               f"{len(dead)} filas con enlace roto en origen (404 o página sin ficha) quedan sin_guia: {sorted(dead)}. "
               "Hint cdn.duzce.edu.tr/translate.goog = documentos Erasmus, no el catálogo; el catálogo real es ebs.duzce.edu.tr (obs.duzce.edu.tr no sirve el módulo Bologna). "
               "Idioma de las fichas: turco (UI turca por defecto; la UI inglesa requiere cookie)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; obligatorias", comp, "optativas", el, "sem comp", tot_sem, "| año", year_no, years.get(year_no or ""))


if __name__ == "__main__":
    main()
