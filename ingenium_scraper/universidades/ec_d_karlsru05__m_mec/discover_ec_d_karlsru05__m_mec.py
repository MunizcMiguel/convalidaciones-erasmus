"""Fase 1 (Descubrimiento) - Hochschule Karlsruhe (HKA) - Maschinenbau B.Eng. (MABM).

Fuente: Modulhandbuch oficial (un unico PDF compartido, en aleman) enlazado desde
https://www.h-ka.de/mabb, complementado con la Studien- und Pruefungsordnung (SPO)
para (a) los modulos "Schwerpunkt 1/2" que no tienen ficha en el Modulhandbuch y
(b) los ECTS de cualquier modulo cuya ficha no los indique.

Uso (desde la raiz del proyecto):  python universidades/ec_d_karlsru05__m_mec/discover_ec_d_karlsru05__m_mec.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
UNIVERSIDAD = "Hochschule Karlsruhe – University of Applied Sciences (HKA)"
SLUG = "ec_d_karlsru05__m_mec"
GRADO = "Maschinenbau (M.Sc.)"
URL_PLAN = "https://www.h-ka.de/fileadmin/Hochschule_Karlsruhe_HKA/Bilder_FK-MMT/Dokumente/Modulhandbuecher/Modulhandbuecher_2026/20260401_Modulhandbuch_MABM.pdf"
ECTS_PLAN = 90.0

RE_HEADING = re.compile(r"^(MABM\d{3}[A-D]?)\s*[–-]\s*(.+?)\s*$")
RE_TOC = re.compile(r"^(MABM\d{3}[A-D]?)\s*[–-]\s*(.+?)\s*\.{5,}\s*(\d+)\s*$")
RE_ECTS = re.compile(r"Modulumfang \(ECTS\):\s*(\d+(?:[.,]\d+)?)")
RE_SEM = re.compile(r"Einordnung \(Semester\):\s*(\d+)")
# Filas de las tablas de la SPO: "MABM110 Höhere Mathematik 1 1 5 6 ..." (Sem SWS CP).
# Nombre codicioso a proposito: los nombres pueden acabar en cifra ("... Engineering 2 6 4 6").
RE_SPO_SCHWERPUNKT = re.compile(r"^(MABM\d{3})\s+(Schwerpunkt \d)\s+(\d)\s+(\d+)\s+s\.")
RE_SPO_ROW = re.compile(r"^(MABM\d{3}[A-D]?)\s+(\S.*)\s+(\d)\s+(\d+)\s+(\d+)(?:\s|$)")


def pdf_lines(path: Path) -> list[list[str]]:
    with pdfplumber.open(path) as pdf:
        return [(p.extract_text() or "").splitlines() for p in pdf.pages]


def parse_modulhandbuch(pages: list[list[str]]) -> tuple[list[dict], dict[str, int], str]:
    """Devuelve (modulos, toc{codigo: pagina_pdf}, curso_academico)."""
    full = "\n".join("\n".join(ls) for ls in pages[:6])
    m = re.search(r"gültig\s+ab\s+dem\s+\d{2}\.\d{2}\.(\d{4})", full)
    if not m:
        raise RuntimeError("No se pudo leer la fecha de validez de la SPO en el Modulhandbuch")
    y = int(m.group(1))
    curso_academico = f"{y}-{(y + 1) % 100:02d}"

    # Indice: la pagina impresa (pie) = pagina PDF - 1 (la portada no esta numerada)
    toc: dict[str, int] = {}
    for lines in pages[:6]:
        for line in lines:
            mt = RE_TOC.match(line.strip())
            if mt:
                toc[mt.group(1)] = int(mt.group(3)) + 1

    mods: list[dict] = []
    for idx, lines in enumerate(pages):
        if not any(l.strip().startswith("Modulbeschreibung") for l in lines):
            continue
        mh = next((RE_HEADING.match(l.strip()) for l in lines[:3] if RE_HEADING.match(l.strip())), None)
        if not mh:
            raise RuntimeError(f"Pagina {idx + 1}: 'Modulbeschreibung' sin cabecera de modulo")
        text = "\n".join(lines)
        me, ms = RE_ECTS.search(text), RE_SEM.search(text)
        mods.append({
            "codigo": mh.group(1),
            "nombre": re.sub(r"\s+", " ", mh.group(2)),
            "ects": float(me.group(1).replace(",", ".")) if me else None,
            "semestre": int(ms.group(1)) if ms else None,
            "pag_ini": idx + 1,
        })
    for i, mod in enumerate(mods):
        mod["pag_fin"] = (mods[i + 1]["pag_ini"] - 1) if i + 1 < len(mods) else len(pages)
    return mods, toc, curso_academico



def caracter(codigo, nombre):
    n = nombre.lower()
    if "master-thesis" in n:
        return "tfg"
    if "wahlpflicht" in n or "vertiefungsmodul" in n:
        return "optativa"
    return "obligatoria"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pages = pdf_lines(http.get_file(URL_PLAN))
    mods, toc, curso = parse_modulhandbuch(pages)
    faltan = sorted(set(toc) - {m["codigo"] for m in mods})  # Vertiefungsmodul 1-5: contenedores sin ficha propia
    if {m["codigo"] for m in mods} - set(toc):
        raise RuntimeError("Fichas fuera del indice")
    entries = []
    for m in mods:
        sem = m["semestre"]
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=m["codigo"], nombre_asignatura=m["nombre"],
            curso_semestre=f"{sem}. Semester" if sem else "", curso=(sem + 1) // 2 if sem else None, semestre=sem,
            creditos_ects=m["ects"], caracter=caracter(m["codigo"], m["nombre"]), idioma_pagina="de",
            url_guia_docente=URL_PLAN, tipo_fuente="pdf_compartido", paginas_pdf=f"{m['pag_ini']}-{m['pag_fin']}"))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    total = sum(e.creditos_ects or 0 for e in entries)
    notas = (f"Titulación elegida: Master Maschinenbau (M.Sc., MABM; 3 semestres, 90 ECTS) de la HKA, familia M-mec (máster de ingeniería mecánica); ya hay B.Eng. MABB en el slug original. "
             f"{len(entries)} módulos, {total:g} ECTS brutos: dos Vertiefungen alternativas (DPE y KKU) con módulos genéricos 'Vertiefungsmodul n' y catálogo Wahlpflicht. "
             f"Contenedores genéricos sin ficha propia (omitidos): {faltan}. Solo alemán. Sin SPO (ECTS/semestre de la propia ficha). Docentes/contactos se eliminan en la Fase 2.")
    cat = Catalog(meta=CatalogMeta(universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="master", curso_academico=curso,
        url_plan_estudios=URL_PLAN, ects_totales_plan=ECTS_PLAN, estrategia_fuente="PDF compartido (Modulhandbuch MABM, alemán)",
        generado_por="discover_ec_d_karlsru05__m_mec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok", notas=notas), asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "modulos", total, "ECTS")
    for e in entries:
        print(e.codigo_asignatura, e.nombre_asignatura, e.creditos_ects, e.semestre, e.paginas_pdf)


if __name__ == "__main__":
    main()
