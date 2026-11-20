"""Fase 1 - Ruhr-Universitaet Bochum (D BOCHUM01) - B.Sc. Elektrotechnik und Informationstechnik (PO 2020).

Fuente: Modulhandbuch oficial (PDF compartido, aleman) enlazado desde
https://ei.ruhr-uni-bochum.de/studium/pruefungsamt/pos-und-dokumente/ . Cada modulo empieza con 'Titel des Moduls:'.
Uso (desde la raiz):  python universidades/ec_d_bochum01/discover_ec_d_bochum01.py
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
SLUG = "ec_d_bochum01"
UNIVERSIDAD = "Ruhr-Universität Bochum"
GRADO = "Elektrotechnik und Informationstechnik (B.Sc., 1-Fach-Bachelor, PO 2020)"
URL_PLAN = "https://ei.ruhr-uni-bochum.de/studium/pruefungsamt/pos-und-dokumente/"
ECTS_PLAN = 180.0
RE_HEAD = re.compile(r"^(\d{5,7})\s+(\d+)\s*CP\b.*?(\d)\.\s+(?:Semester|und\s*\d\.)")


def find_pdf(http: PoliteClient) -> str:
    soup = BeautifulSoup(http.get_text(URL_PLAN), "lxml")
    for a in soup.find_all("a", href=True):
        if "Modulhandbuch_BaET_PO20" in a["href"]:
            return urljoin(URL_PLAN, a["href"])
    raise RuntimeError("Modulhandbuch BaET PO20 no encontrado")


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf_url = find_pdf(http)
    path = http.get_file(pdf_url)
    with pdfplumber.open(path) as pdf:
        pages = [(p.extract_text() or "").splitlines() for p in pdf.pages]
    starts = [i for i, ls in enumerate(pages) if ls and ls[0].startswith("Titel des Moduls:")]
    rows, notes = [], []
    for k, i in enumerate(starts):
        end = (starts[k + 1] - 1) if k + 1 < len(starts) else len(pages) - 1
        nombre = pages[i][0].split(":", 1)[1].strip()
        head = next((RE_HEAD.match(l.strip()) for l in pages[i][:12] if RE_HEAD.match(l.strip())), None)
        if not head:
            raise RuntimeError(f"cabecera no parseada: {nombre}")
        code, cp, sem = head.group(1), float(head.group(2)), int(head.group(3))
        text = "\n".join(pages[i])
        lang = "de"
        rows.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
            curso_semestre=f"{sem}. Semester", curso=(sem + 1) // 2, semestre=sem, creditos_ects=cp,
            caracter="tfg" if nombre.startswith("Bachelorarbeit") else
            ("optativa" if re.match(r"(Kernf|Technischer Wahl|Freier Wahl)", nombre) else "obligatoria"),
            idioma_pagina=lang, url_guia_docente=pdf_url, tipo_fuente="pdf_compartido",
            paginas_pdf=f"{i + 1}-{end + 1}"))
    total = sum(r.creditos_ects or 0 for r in rows)
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2025-2026",
        url_plan_estudios=URL_PLAN, ects_totales_plan=ECTS_PLAN,
        estrategia_fuente="Modulhandbuch PDF compartido (BaET PO 2020, SS 2026); un modulo por 'Titel des Moduls:'",
        generado_por="discover_ec_d_bochum01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: B.Sc. Elektrotechnik und Informationstechnik (ETIT, 180 ECTS), la más afín a Electrónica "
               "Industrial y Automática y a Telecomunicación (filas Uniovi: EIA, Telecomunicación 2 plazas, Informática). "
               "Docencia en alemán (algunos módulos alemán/inglés). Existe además el B.Sc. IT-Engineering (alemán e inglés, "
               "PO 2025) más cercano a Informática, no catalogado (una titulación por universidad). Los módulos agregados "
               "(Kernfächer 1-4, Technischer Wahlbereich, Freier Wahlbereich) son contenedores de asignaturas optativas "
               "cuya ficha individual no está en este Modulhandbuch. Páginas 'ini-fin' = páginas PDF 1-indexadas. "
               f"Suma ECTS={total:g}."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(rows)} módulos; ECTS={total:g}; PDF={pdf_url}")


if __name__ == "__main__":
    main()
