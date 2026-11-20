"""Fase 1 - Ruhr-Universitaet Bochum (D BOCHUM01) - B.Sc. IT-Sicherheit / Informationstechnik (PO 2022).

Fuente: Modulhandbuch oficial (PDF compartido, aleman, Stand SoSe 2026) de la Fakultaet fuer Informatik: https://informatik.rub.de/wp-content/uploads/2026/03/MHB-BSc-ITS-SoSe-26.pdf
Cada modulo empieza con 'Titel des Moduls:'. Sin codigo oficial en el PDF: codigo = slug del titulo.
Uso (desde la raiz): python universidades/ec_d_bochum01__tele/discover_ec_d_bochum01__tele.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_bochum01__tele"
UNIVERSIDAD = "Ruhr-Universität Bochum"
GRADO = "IT-Sicherheit / Informationstechnik (B.Sc., PO 2022)"
URL_PLAN = "https://informatik.rub.de/wp-content/uploads/2026/03/MHB-BSc-ITS-SoSe-26.pdf"
ECTS_PLAN = 180.0
RE_CP = re.compile(r"(" + chr(92) + "d+)" + chr(92) + "s*CP")


def slug(t: str) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    path = http.get_file(URL_PLAN)
    with pdfplumber.open(path) as pdf:
        pages = [(p.extract_text() or "").splitlines() for p in pdf.pages]
    starts = [i for i, ls in enumerate(pages) if ls and ls[0].startswith("Titel des Moduls:")]
    rows, seen = [], set()
    for k, i in enumerate(starts):
        end = (starts[k + 1] - 1) if k + 1 < len(starts) else len(pages) - 1
        nombre = pages[i][0].split(":", 1)[1].strip()
        head = chr(10).join(pages[i][:8])
        m = RE_CP.search(head)
        cp = float(m.group(1)) if m else None
        code = slug(nombre)
        if code in seen:
            code += f"-p{i + 1}"
        seen.add(code)
        text = chr(10).join(pages[i])
        lang = "en" if re.search(r"Unterrichtssprache\s+Englisch", text) else "de"
        rows.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
            curso_semestre="semestre no indicado en la ficha", curso=None, semestre=None, creditos_ects=cp,
            caracter="tfg" if nombre.startswith("Bachelorarbeit") else None,
            idioma_pagina=lang, url_guia_docente=URL_PLAN, tipo_fuente="pdf_compartido", paginas_pdf=f"{i + 1}-{end + 1}"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="SoSe 2026 (PO 2022, Stand 11.03.26)",
        url_plan_estudios=URL_PLAN, ects_totales_plan=ECTS_PLAN,
        estrategia_fuente="Modulhandbuch PDF compartido (B.Sc. ITS PO 2022); un modulo por 'Titel des Moduls:'",
        generado_por="discover_ec_d_bochum01__tele.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida para la familia telecomunicación (segunda titulación del destino; la primera es B.Sc. ETIT): B.Sc. IT-Sicherheit / Informationstechnik "
               "(PO 2022, 180 ECTS; Pflichtbereich con Computernetze, Netzsicherheit, Signale und Systeme, Kryptographie, Technische Informatik). "
               f"{len(rows)} fichas de módulo (Pflicht + Vertiefungsmodule ofertados), suma bruta {total:g} ECTS (los Vertiefungsmodule son a elegir). "
               "El PDF no incluye código oficial: codigo_asignatura = slug del título; semestre no indicado en las fichas (null). Alemán (algunos módulos en inglés)."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(rows)} módulos; ECTS={total:g}")
    for r in rows:
        print(r.codigo_asignatura, r.creditos_ects, r.paginas_pdf, r.idioma_pagina)


if __name__ == "__main__":
    main()
