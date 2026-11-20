"""Fase 1 - Technische Hochschule Ingolstadt (THI) - Maschinenbau (B.Eng.).

Fuente: Modulhandbuch oficial WS 2026/27 (PDF compartido, aleman) enlazado desde la pagina del
grado en www.thi.de, mas el PDF de Wahlpflichtmodule (FW-Faecher) para los electivos asignados a MB-B.
Uso: python universidades/ec_d_ingolst01/discover_ec_d_ingolst01.py
"""
from __future__ import annotations

import io
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pypdf  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_ingolst01"
UNIVERSIDAD = "Technische Hochschule Ingolstadt (THI)"
GRADO = "Maschinenbau (B.Eng.)"
URL_PLAN = "https://www.thi.de/en/mechanical-engineering/degree-programmes/mechanical-engineering-beng/"
BASE = "https://www.thi.de"
ECTS_PLAN = 210.0

HDR = re.compile(r"^(MB-B \(SPO|FW-F.cher|MHB:)")
SEC = re.compile(r"^\d+(\.\d+)*\s+\S")


def page_lines(page_text: str) -> list[str]:
    """Quita la cabecera de pagina (2 lineas + numero) y devuelve lineas no vacias."""
    ls = [l.rstrip() for l in page_text.split("\n")]
    i = 0
    while i < min(6, len(ls)) and not re.fullmatch(r"\s*\d+\s*", ls[i]):
        i += 1
    ls = ls[i + 1:] if i < min(6, len(ls)) else ls
    return [l for l in ls if l.strip()]


def parse_pdf(data: bytes, url: str, electives: bool) -> list[dict]:
    r = pypdf.PdfReader(io.BytesIO(data))
    texts = [p.extract_text() or "" for p in r.pages]
    starts = [i for i, t in enumerate(texts) if "Modulkürzel:" in t]
    out = []
    for k, s in enumerate(starts):
        end = (starts[k + 1] - 1) if k + 1 < len(starts) else len(texts) - 1
        full = "\n".join(texts[s:end + 1])
        ls = page_lines(texts[s])
        j = next(n for n, l in enumerate(ls) if "Modulkürzel:" in l)
        title = " ".join(l.strip() for l in ls[:j] if not SEC.match(l.strip()))
        title = re.sub(r"-\s+(?=[a-zäöü])", "", title).strip() if False else title.strip()
        m = re.search(r"Modulkürzel:\s*(.+?)\s*(?:SPO-Nr\.|Art des Moduls)", "\n".join(ls[j:]), re.S)
        code = re.sub(r"-\n\s*", "", m.group(1)).replace("\n", "").replace(" ", "")
        ects = re.search(r"(\d+(?:[.,]\d+)?)\s*ECTS", full)
        zone = full[:full.find("Modulverantwortliche")]
        if electives:
            if "Maschinenbau Bachelor (MB-B)" not in zone:
                continue
            sem, art = None, "optativa"
        else:
            mm = re.search(r"Maschinenbau\s+(Pflichtfach|Wahlpflichtfach\w*)\s+(\d+)", zone)
            art = "obligatoria" if mm and mm.group(1) == "Pflichtfach" else "optativa"
            sem = int(mm.group(2)) if mm else None
        lang = "de"
        if re.search(r"Unterrichtssprache[^\n]*\n\s*Englisch", full) or "The students" in full or "Learning outcomes" in full:
            lang = "en"
        out.append(dict(code=code, name=title, ects=float(ects.group(1).replace(",", ".")) if ects else None,
                        sem=sem, art=art, lang=lang, url=url, pages=f"{s + 1}-{end + 1}"))
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    page = c.get_text(URL_PLAN)
    links = sorted(set(re.findall(r'href="([^"]+\.pdf)"', page)))
    mhb = next(l for l in links if "Bachelor_MB/MHBuch_MB_SPO" in l)
    fw = next(l for l in links if "Wahlpflichtmodule" in l)
    mhb_u, fw_u = BASE + mhb, BASE + fw
    core = parse_pdf(c.get_bytes(mhb_u), mhb_u, False)
    elec = parse_pdf(c.get_bytes(fw_u), fw_u, True)
    entries, seen = [], set()
    for d in core + elec:
        if d["code"] in seen:
            continue
        seen.add(d["code"])
        sem = d["sem"]
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=d["code"], nombre_asignatura=d["name"],
            curso_semestre=(f"Semestre {sem}" if sem else "Wahlpflicht (sem. a elegir)"),
            curso=((sem + 1) // 2 if sem else None), semestre=sem, creditos_ects=d["ects"], caracter=d["art"],
            idioma_pagina=d["lang"], url_guia_docente=d["url"], tipo_fuente="pdf_compartido", paginas_pdf=d["pages"]))
    obl = sum(e.creditos_ects or 0 for e in entries if e.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="WS 2026/27", url_plan_estudios=URL_PLAN,
        ects_totales_plan=ECTS_PLAN, estrategia_fuente="Modulhandbuch PDF compartido (2 PDF: obligatorios + FW-Faecher), parseado con pypdf",
        generado_por="discover_ec_d_ingolst01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Grado Maschinenbau B.Eng. (7 semestres, 210 ECTS; SPO WS 2023/24). Obligatorios (Pflichtfach) suman {obl:g} ECTS; "
               "el resto hasta 210 son electivos de Studienrichtung, FW-Faecher (PDF aparte; se incluyen los asignados a MB-B), "
               "practicas y Bachelorarbeit, que no tienen ficha en el Modulhandbuch o dependen de la eleccion. Los semestres de "
               "los electivos no estan fijados. Idioma: aleman."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(core), "obligatorios/tronco;", len(elec), "electivos MB-B;", len(entries), "filas; ECTS obligatorios", obl)


if __name__ == "__main__":
    main()
