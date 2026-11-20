"""Fase 1 - TU Wien - Bachelorstudium Maschinenbau (E 033 245, 6 semestres, 180 ECTS).

Fuente: Studienplan oficial (PDF con texto, anexo 'A Modulbeschreibungen') publicado en
https://www.tuwien.at/tu-wien/organisation/zentrale-bereiche/studienabteilung/studienplaene (programa: .../bachelorstudien/maschinenbau). TISS (guias por LVA) redirige a login: no se usa.
Uso: python universidades/ec_a_wien02/discover_ec_a_wien02.py
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import wien_parse as wp  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

SLUG = "ec_a_wien02"
UNIVERSIDAD = "Technische Universität Wien"
GRADO = "Bachelorstudium Maschinenbau (E 033 245)"
URL_PLAN = "https://www.tuwien.at/studium/studienangebot/bachelorstudien/maschinenbau"
URL_STUDIENPLAENE = "https://www.tuwien.at/tu-wien/organisation/zentrale-bereiche/studienabteilung/studienplaene"


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    page = c.get_text(URL_STUDIENPLAENE)
    links = [htmllib.unescape(h) for h in re.findall(r'href="([^"]+\.pdf)"', page)]
    cands = [h for h in links if re.search(r"BSc-Studienplaene_\d{4}/Bachelorstudium_Maschinenbau_\d{4}(?:_rev\d+)?\.pdf$", h)]
    url = urljoin(URL_STUDIENPLAENE, max(cands, key=lambda h: re.search(r"_(\d{4})(?:_rev(\d+))?\.pdf$", h).groups("0")))
    mods = wp.parse_modules(wp.load_pages(c.get_bytes(url)))
    entries, seen = [], set()
    for m in mods:
        code = "MB-" + slug(m["title"])
        if code in seen:
            continue
        seen.add(code)
        g = m["group"]
        caracter = "tfg" if "Bachelorabschluss" in m["title"] else "obligatoria" if g == "Pflichtmodule" else "optativa"
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=m["title"],
            curso_semestre=g or "n/d", curso=None, semestre=None, creditos_ects=m["ects"], caracter=caracter,
            idioma_pagina="de", url_guia_docente=url, tipo_fuente="pdf_compartido", paginas_pdf=f"{m['page_ini']}-{m['page_fin']}"))
    oblig = sum(e.creditos_ects or 0 for e in entries if e.caracter in ("obligatoria", "tfg"))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="Studienplan 2026 (rev1)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0, estrategia_fuente="Studienplan PDF, anexo A Modulbeschreibungen (pypdf; un bloque por módulo)",
        generado_por="discover_ec_a_wien02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Bachelorstudium Maschinenbau (E 033 245), 180 ECTS. {len(entries)} módulos; los obligatorios (Pflichtmodule + Bachelorabschlussmodul) suman {oblig:g} ECTS; "
               "de las Modulgruppen Aufbaumodule (14) y Berufsfeldorientierung (18) se eligen 2+2, por eso la suma total supera 180. "
               "Nivel de detalle: módulo (no LVA): el Studienplan da Lernergebnisse, Inhalt, Vorkenntnisse, Lehrformen y lista de LVAs; no hay bibliografía ni "
               "semestre por módulo (curso/semestre null). Las guías por LVA están en TISS (tiss.tuwien.ac.at/course/...), cuyo robots.txt permite /course/ pero "
               "redirige a /admin/authentifizierung (login): NO se usan; tiss.tuwien.ac.at/robots.txt se auto-veta (Disallow: /) y PoliteClient lo marca bloqueado. "
               "Códigos: no hay código oficial en el Studienplan; slug del título. Idioma: alemán."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos; ECTS obligatorios", oblig, "; url", url)


if __name__ == "__main__":
    main()
