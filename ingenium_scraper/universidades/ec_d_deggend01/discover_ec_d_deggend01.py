"""Fase 1 - TH Deggendorf - Bachelor Kuenstliche Intelligenz (Fak. Angewandte Informatik). Fuente: Modulhandbuch PDF compartido (136 pags., aleman, Stand 10.03.2022).
Uso: python universidades/ec_d_deggend01/discover_ec_d_deggend01.py
"""
from __future__ import annotations
import io, json, re, sys, time, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_deggend01"
UNI = "Technische Hochschule Deggendorf"
GRADO = "Künstliche Intelligenz (Bachelor, Fak. Angewandte Informatik)"
URL_PLAN = "https://th-deg.de/exchange-students"
PDF = "https://www.th-deg.de/Studierende/Antraege-und-Organisatorisches/Modulhandbuecher/modulhandbuch_ki.pdf"
HEAD = re.compile(r"^\s*([A-Z]{2,4}-\d{2,3})\s+(\S.*?)\s*$")


def get_lines(client: PoliteClient) -> list[tuple[int, str]]:
    r = pypdf.PdfReader(io.BytesIO(client.get_bytes(PDF)))
    out = []
    for pn, p in enumerate(r.pages, 1):
        for l in unicodedata.normalize("NFC", p.extract_text() or "").split("\n"):
            if l.strip() and not re.fullmatch(r"\s*\d{1,3}\s*", l):
                out.append((pn, l.rstrip()))
    return out


def modules(lines):
    idx = [i for i, (_, l) in enumerate(lines) if HEAD.match(l) and "...." not in l and i + 2 < len(lines)
           and (lines[i + 1][1].strip().startswith("Modul Nr.") or lines[i + 2][1].strip().startswith("Modul Nr."))]
    out = []
    for k, i in enumerate(idx):
        j = idx[k + 1] if k + 1 < len(idx) else len(lines)
        m = HEAD.match(lines[i][1])
        nm = m.group(2) + ("" if lines[i + 1][1].strip().startswith("Modul Nr.") else " " + lines[i + 1][1].strip())
        out.append(dict(code=m.group(1), name=re.sub(r"\s+", " ", nm).title() if nm.isupper() else re.sub(r"\s+", " ", nm),
                        body=[l for _, l in lines[i + 1:j]], p0=lines[i][0], p1=lines[j - 1][0]))
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    entries, seen = [], set()
    for m in modules(get_lines(c)):
        if m["code"] in seen:
            continue
        seen.add(m["code"])
        txt = "\n".join(m["body"][:30])
        sem = re.search(r"^Semester\s+(\d)", txt, re.M)
        ects = re.search(r"^ECTS\s+(\d+(?:[.,]\d+)?)", txt, re.M)
        art = re.search(r"^Art der Lehrveranstaltungen\s+(.+)$", txt, re.M)
        lang = re.search(r"^Unterrichts-/Lehrsprache\s+(\S+)", txt, re.M)
        optional = bool(art and re.search(r"Wahl", art.group(1)))
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=m["code"], nombre_asignatura=m["name"],
            curso_semestre=f"Semestre {sem.group(1)}" if sem else "Semestre no indicado", curso=(int(sem.group(1)) + 1) // 2 if sem else None,
            semestre=int(sem.group(1)) if sem else None, creditos_ects=float(ects.group(1).replace(",", ".")) if ects else None,
            caracter="optativa" if optional else "obligatoria", idioma_pagina="en" if lang and lang.group(1).lower().startswith("engl") else "de",
            url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{m['p0']}-{m['p1']}"))
    tot = sum(e.creditos_ects or 0 for e in entries if e.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2021-22 (Stand 10.03.2022)", url_plan_estudios=URL_PLAN, ects_totales_plan=210.0,
        estrategia_fuente="Modulhandbuch PDF compartido parseado con pypdf; módulo = 'KI-nn TÍTULO' + 'Modul Nr. KI-nn'",
        generado_por="discover_ec_d_deggend01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Excel: Grado Ciencia e Ingeniería de Datos (2 plazas), Doble Grado Informática+Datos y Teleco+Datos, todos ISCED 0610 (TIC). THD no tiene un grado de Ciencia de Datos "
               "con Modulhandbuch actual; se elige Bachelor Künstliche Intelligenz (Fak. Angewandte Informatik, PO 06.11.2018, 7 semestres, 210 ECTS), el más afín a Datos; alternativas "
               "Wirtschaftsinformatik (WI) e Interaktive Systeme/IoT. AVISO: el Modulhandbuch es de marzo de 2022 (puede haber módulos nuevos; no se localizó versión posterior). "
               f"Obligatorios suman {tot:g} ECTS en el listado. Se omiten Modulverantwortliche y Lehrende. robots.txt de www.th-deg.de permite /Studierende/."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS oblig.", tot)


if __name__ == "__main__":
    main()
