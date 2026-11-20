"""Fase 1 (Descubrimiento) - Hochschule Karlsruhe (HKA) - Maschinenbau B.Eng. (MABB).

Fuente: Modulhandbuch oficial (un unico PDF compartido, en aleman) enlazado desde
https://www.h-ka.de/mabb, complementado con la Studien- und Pruefungsordnung (SPO)
para (a) los modulos "Schwerpunkt 1/2" que no tienen ficha en el Modulhandbuch y
(b) los ECTS de cualquier modulo cuya ficha no los indique.

Uso (desde la raiz del proyecto):  python universidades/hka/discover_hka.py
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
SLUG = "hka"
GRADO = "Maschinenbau (B.Eng.)"
URL_PLAN = "https://www.h-ka.de/mabb"
ECTS_PLAN = 210.0

RE_HEADING = re.compile(r"^(MABB\d{3}[A-D]?)\s*[–-]\s*(.+?)\s*$")
RE_TOC = re.compile(r"^(MABB\d{3}[A-D]?)\s*[–-]\s*(.+?)\s*\.{5,}\s*(\d+)\s*$")
RE_ECTS = re.compile(r"Modulumfang \(ECTS\):\s*(\d+(?:[.,]\d+)?)")
RE_SEM = re.compile(r"Einordnung \(Semester\):\s*(\d+)")
# Filas de las tablas de la SPO: "MABB110 Höhere Mathematik 1 1 5 6 ..." (Sem SWS CP).
# Nombre codicioso a proposito: los nombres pueden acabar en cifra ("... Engineering 2 6 4 6").
RE_SPO_SCHWERPUNKT = re.compile(r"^(MABB\d{3})\s+(Schwerpunkt \d)\s+(\d)\s+(\d+)\s+s\.")
RE_SPO_ROW = re.compile(r"^(MABB\d{3}[A-D]?)\s+(\S.*)\s+(\d)\s+(\d+)\s+(\d+)(?:\s|$)")


def find_pdf_links(http: PoliteClient) -> tuple[str, str]:
    """Localiza en la pagina del grado los PDF del Modulhandbuch y de la SPO."""
    soup = BeautifulSoup(http.get_text(URL_PLAN), "lxml")
    mhb = spo = None
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.lower().endswith(".pdf"):
            continue
        if mhb is None and "Modulhandbuch" in href:
            mhb = urljoin(URL_PLAN, href)
        if spo is None and "_SPO_" in href:
            spo = urljoin(URL_PLAN, href)
    if not mhb or not spo:
        raise RuntimeError(f"No se encontraron los enlaces PDF (mhb={mhb}, spo={spo})")
    return mhb, spo


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


def parse_spo(pages: list[list[str]]) -> tuple[dict[str, dict], list[dict]]:
    """Devuelve ({codigo: {sem, ects}} de las tablas, [modulos Schwerpunkt])."""
    rows: dict[str, dict] = {}
    schwerpunkte: list[dict] = []
    for lines in pages:
        for line in lines:
            line = line.strip()
            ms = RE_SPO_SCHWERPUNKT.match(line)
            if ms:
                schwerpunkte.append({"codigo": ms.group(1), "nombre": ms.group(2),
                                     "semestre": int(ms.group(3)), "ects": float(ms.group(4))})
                continue
            mr = RE_SPO_ROW.match(line)
            if mr:
                rows.setdefault(mr.group(1), {"semestre": int(mr.group(3)), "ects": float(mr.group(5))})
    return rows, schwerpunkte


def caracter(codigo: str, nombre: str) -> str:
    if re.search(r"[A-D]$", codigo):
        return f"optativa (Vertiefung {codigo[-1]})"
    n = nombre.lower()
    if "wahlpflicht" in n or "schwerpunkt" in n:
        return "optativa"
    if "praxissemester" in n:
        return "practicas"
    if "bachelor-thesis" in n:
        return "tfg"
    return "obligatoria"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    url_mhb, url_spo = find_pdf_links(http)
    mhb_pages = pdf_lines(http.get_file(url_mhb))
    spo_pages = pdf_lines(http.get_file(url_spo))

    mods, toc, curso_academico = parse_modulhandbuch(mhb_pages)
    spo_rows, schwerpunkte = parse_spo(spo_pages)

    # --- comprobaciones cruzadas con el indice del propio PDF ---
    if set(toc) != {m["codigo"] for m in mods}:
        raise RuntimeError(f"Indice y cabeceras no coinciden: {set(toc) ^ {m['codigo'] for m in mods}}")
    for m in mods:
        if toc[m["codigo"]] != m["pag_ini"]:
            raise RuntimeError(f"{m['codigo']}: indice dice pag {toc[m['codigo']]}, cabecera en {m['pag_ini']}")

    avisos: list[str] = []
    entries: list[CatalogEntry] = []
    for m in mods:
        ects, sem = m["ects"], m["semestre"]
        spo = spo_rows.get(m["codigo"])
        if ects is None and spo:
            ects = spo["ects"]
            avisos.append(f"{m['codigo']}: ECTS tomados de la SPO (la ficha no los indica)")
        elif spo and ects is not None and spo["ects"] != ects:
            avisos.append(f"{m['codigo']}: ECTS Modulhandbuch={ects} vs SPO={spo['ects']}")
        if sem is None and spo:
            sem = spo["semestre"]
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO,
            codigo_asignatura=m["codigo"], nombre_asignatura=m["nombre"],
            curso_semestre=f"{sem}. Semester" if sem else "",
            curso=(sem + 1) // 2 if sem else None, semestre=sem,
            creditos_ects=ects, caracter=caracter(m["codigo"], m["nombre"]),
            idioma_pagina="de", url_guia_docente=url_mhb, tipo_fuente="pdf_compartido",
            paginas_pdf=f"{m['pag_ini']}-{m['pag_fin']}",
        ))
    for s in schwerpunkte:  # solo existen en la SPO: sin ficha de modulo
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO,
            codigo_asignatura=s["codigo"], nombre_asignatura=s["nombre"],
            curso_semestre=f"{s['semestre']}. Semester",
            curso=(s["semestre"] + 1) // 2, semestre=s["semestre"],
            creditos_ects=s["ects"], caracter="optativa",
            idioma_pagina="de", url_guia_docente=None, tipo_fuente="sin_guia",
        ))
    entries.sort(key=lambda e: e.codigo_asignatura)

    # --- validaciones ---
    codes = [e.codigo_asignatura for e in entries]
    if len(codes) != len(set(codes)):
        raise RuntimeError("Codigos duplicados")
    if any(e.creditos_ects is None or e.semestre is None for e in entries):
        raise RuntimeError("Modulo sin ECTS o semestre")
    comunes = sum(e.creditos_ects for e in entries if not re.search(r"[A-D]$", e.codigo_asignatura))
    por_vert = {L: sum(e.creditos_ects for e in entries if e.codigo_asignatura.endswith(L)) for L in "ABCD"}
    for L, v in por_vert.items():
        if comunes + v != ECTS_PLAN:
            raise RuntimeError(f"Itinerario Vertiefung {L}: {comunes + v} ECTS != {ECTS_PLAN}")
    total = sum(e.creditos_ects for e in entries)

    notas = (
        f"{len(entries)} modulos; suma bruta {total:g} ECTS = {comunes:g} comunes + 4 Vertiefungen "
        f"alternativas (A-D) de {por_vert['A']:g} ECTS cada una; el estudiante cursa una -> {ECTS_PLAN:g} ECTS. "
        "MABB450/MABB650 (Schwerpunkt 1/2) y MABB710 (Wahlpflicht) son contenedores de libre eleccion; "
        "450/650 solo constan en la SPO (sin ficha). paginas_pdf = paginas fisicas del PDF (1-indexadas; "
        "pagina impresa + 1). " + ("Avisos: " + "; ".join(avisos) + ". " if avisos else "") +
        f"SPO: {url_spo}"
    )
    catalog = Catalog(
        meta=CatalogMeta(
            universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor",
            curso_academico=curso_academico, url_plan_estudios=URL_PLAN, ects_totales_plan=ECTS_PLAN,
            estrategia_fuente="PDF compartido (Modulhandbuch MABB, aleman) + tabla de la SPO (PDF) para Schwerpunkt y ECTS ausentes",
            generado_por="discover_hka.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
            estado="ok", notas=notas,
        ),
        asignaturas=entries,
    )
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {len(entries)} modulos, {total:g} ECTS brutos ({ECTS_PLAN:g} por itinerario) -> {out}")
    for a in avisos:
        print("AVISO:", a)
    print("HTTP stats:", http.stats)


if __name__ == "__main__":
    main()
