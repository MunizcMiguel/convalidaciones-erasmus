"""Fase 1 - Toros University (TR MERSIN04): Endustri Muhendisligi (Industrial Engineering, lisans, 240 ECTS).
Bologna Bilgi Paketi: https://obsogrenci.toros.edu.tr/BLGNDersBilgiPaketi/ (AngularJS; JSON por POST, publico, robots sin reglas).
 GetMufredat {programId,diller} -> curriculos; MufredatDerslerListele {mufredatId,diller,yilID} -> asignaturas (obligatorias en .dersler, optativas en .dersgruplari[].dersGruplariDersleri).
Ficha: /BLGNDersBilgiPaketi/DersBilgileri?mufDersID=..&dersGrubuDersID=..&dersID=..&programID=..&dilID=2&yilID=..
Uso: python universidades/ec_tr_mersin04/discover_ec_tr_mersin04.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_mersin04"
UNIVERSIDAD = "Toros Üniversitesi (Toros University) - Mühendislik Fakültesi"
GRADO = "Endüstri Mühendisliği (Industrial Engineering), lisans"
B = "https://obsogrenci.toros.edu.tr"
PROGRAM = 115  # Endustri Muhendisligi (TR). Los programas EN (116-118) solo exponen curriculos antiguos (2013-2019) que el servidor no lista (HTTP 500)
SRC_PAGE = f"https://bologna.toros.edu.tr/tr/derece/114/program/{PROGRAM}"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=1, timeout=30)
    post = lambda p, d: json.loads(c.get_bytes(B + p, method="POST", json=d))  # noqa: E731
    page = c.get_text(f"{B}/BLGNDersBilgiPaketi/SubIcerik?lang=en&programID={PROGRAM}")
    years = json.loads(BeautifulSoup(page, "lxml").find(id="jsonYillar")["value"])
    yil = next(y for y in years if y.get("selected"))
    mufs = post("/BLGNDersBilgiPaketi/GetMufredat", {"programId": PROGRAM, "diller": "en"})["Data"]
    cur = max(mufs, key=lambda m: m["ID"])
    data = post("/BLGNDersBilgiPaketi/MufredatDerslerListele", {"mufredatId": cur["ID"], "diller": "en", "yilID": yil["ID"]})["Data"]["MufredatDersler"]
    entries, seen = [], set()

    def add(code, name, ects, sem, year, car, dersid, mufid, grid):
        if code in seen:
            return
        seen.add(code)
        url = f"{B}/BLGNDersBilgiPaketi/DersBilgileri?mufDersID={mufid}&dersGrubuDersID={grid}&dersID={dersid}&programID={PROGRAM}&dilID=2&yilID={yil['ID']}"
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
            curso_semestre=f"Yıl {year} / Yarıyıl {sem}" if sem else f"Yıl {year}", curso=year, semestre=sem, creditos_ects=float(ects), caracter=car,
            idioma_pagina="en", url_guia_docente=url, tipo_fuente="html"))

    for y in data:
        sem = y["yariYil"]
        for d in y["dersler"] or []:
            if sem:
                add(d["j_dersKodu"].strip(), d["j_dersAdiEng"] or d["j_dersAdi"], d["ectsKredi"], sem, (sem + 1) // 2, "obligatoria", d["dersID"], d["ID"], 0)
        for g in y["dersgruplari"] or []:
            m = re.match(r"(\d)\. DÖNEM", g.get("dersGrubuAdi") or "")
            gsem = int(m.group(1)) if m else None
            gyear = g.get("sinif") or ((gsem + 1) // 2 if gsem else 1)
            for d in g["dersGruplariDersleri"] or []:
                add(d["j_derskodu"].strip(), d["j_dersEng"] or d["j_ders"], d["d_ects"], gsem, gyear, "optativa", d["dersID"], 0, d["ID"])
    comp = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    nopt = sum(1 for e in entries if e.caracter == "optativa")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico=f"{yil['value']} - {cur['mufredatAdi']}", url_plan_estudios=SRC_PAGE, ects_totales_plan=240.0,
        estrategia_fuente="JSON del Bologna Bilgi Paketi (obsogrenci.toros.edu.tr): GetMufredat + MufredatDerslerListele; ficha por POST GetDers*",
        generado_por="discover_ec_tr_mersin04.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Titulación elegida: Endüstri Mühendisliği (Industrial Engineering): el Excel solo trae Grado en Ingeniería de Organización Industrial para este destino (2 plazas, inglés B1) y es el equivalente directo. "
               f"Se usa el programa TR (id {PROGRAM}) con currículo vigente id {cur['ID']} (2022-Devam, el más reciente); los programas en inglés (116-118) solo listan currículos 2013-2019 y el servidor devuelve HTTP 500 al listarlos. Los nombres de las asignaturas vienen en inglés (j_dersAdiEng); "
               f"las fichas se piden con dilID=2 (EN) y pueden quedar en turco si el departamento no las tradujo. {len(entries)} filas: obligatorias {comp:g} ECTS + {nopt} optativas ofertadas (grupos «N. DÖNEM SERBEST/ALAN SEÇMELİ»; el semestre de cada grupo sale de su nombre). El listado del plan no devuelve el semestre 8 obligatorio (puede faltar). Fase 2: 53 de 84 asignaturas tienen ficha publicada; las otras 31 (casi todas optativas) no tienen contenido en la plataforma en ningún año."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; obligatorias ECTS", comp, "optativas", nopt)


if __name__ == "__main__":
    main()
