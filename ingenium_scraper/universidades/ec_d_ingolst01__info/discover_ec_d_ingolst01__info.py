"""Fase 1 - Technische Hochschule Ingolstadt (THI) - Maschinenbau (B.Eng.).

Fuente: Modulhandbuch oficial WS 2026/27 (PDF compartido, aleman) enlazado desde la pagina del
grado en www.thi.de, mas el PDF de Wahlpflichtmodule (FW-Faecher) para los electivos asignados a MB-B.
Uso: python universidades/ec_d_ingolst01__info/discover_ec_d_ingolst01__info.py
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
SLUG = "ec_d_ingolst01__info"
UNIVERSIDAD = "Technische Hochschule Ingolstadt (THI)"
GRADO = "Informatik (B.Sc.)"
URL_PLAN = "https://www.thi.de/fileadmin/daten/fakultaetI/Modulhandbuecher/MHBuch_INF-B.pdf"
BASE = "https://www.thi.de"
ECTS_PLAN = 210.0

HDR = re.compile(r"^(MB-B \(SPO|FW-F.cher|MHB:)")
SEC = re.compile(r"^\d+(\.\d+)*\s+\S")


def page_lines(page_text: str) -> list[str]:
    """Quita cabecera ('Informatik (SPO ...) Modulhandbuch') y numero de pagina final."""
    ls = [l.rstrip() for l in page_text.split(chr(10)) if l.strip()]
    if ls and "Modulhandbuch" in ls[0]:
        ls = ls[1:]
    if ls and re.fullmatch(r"\s*\d+\s*", ls[-1]):
        ls = ls[:-1]
    return ls


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
        title = re.sub(r"^\d+\s+", "", title.strip())
        m = re.search(r"Modulkürzel:\s*(.+?)\s*(?:SPO-Nr\.|Art des Moduls)", "\n".join(ls[j:]), re.S)
        code = re.sub(r"-\n\s*", "", m.group(1)).replace("\n", "").replace(" ", "")
        ects = re.search(r"(\d+(?:[.,]\d+)?)\s*ECTS", full)
        zone = full[:full.find("Modulverantwortliche")]
        mm = re.search(r"Informatik \(SPO[^)]*\)\s+(Pflichtfach|Wahlpflichtfach\w*)\s+(\d+)", zone)
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
    mods = parse_pdf(c.get_bytes(URL_PLAN), URL_PLAN, False)
    entries, seen = [], set()
    for d in mods:
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
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="SPO WS 18/19 (Stand 31.01.2025)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=ECTS_PLAN, estrategia_fuente="Modulhandbuch PDF compartido (Informatik B.Sc.), parseado con pypdf",
        generado_por="discover_ec_d_ingolst01__info.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Titulación: Informatik B.Sc. (THI, Fakultät Informatik; 7 semestres, 210 ECTS), familia info, distinta de Maschinenbau B.Eng. {len(entries)} módulos; "
               f"obligatorios (Pflichtfach) suman {obl:g} ECTS; el resto son Wahlpflicht/prácticas/Bachelorarbeit. Idioma: alemán salvo módulos marcados en inglés. "
               "Docentes (Modulverantwortliche) se eliminan en la Fase 2."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "modulos; ECTS obligatorios", obl)
    for e in entries:
        print(e.codigo_asignatura, e.nombre_asignatura, e.creditos_ects, e.semestre, e.paginas_pdf)


if __name__ == "__main__":
    main()
