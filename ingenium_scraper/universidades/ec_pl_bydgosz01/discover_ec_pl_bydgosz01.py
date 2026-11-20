"""Fase 1 - Kazimierz Wielki University, Bydgoszcz (PL BYDGOSZ01) - ICT / Computer Science courses in English (Institute of Informatics).
Fuente: catalogo Erasmus erasmus.ukw.edu.pl/en/courses/ (HTML; robots permite). El filtro «Study area = ICT (061)» es un formulario POST
con token de sesion (uso normal del buscador); el resultado se pagina en /courses/num/{n}/. Cada asignatura enlaza un silabo PDF
(/en/courses/syllabus/{id}/).
Uso (desde la raiz): python universidades/ec_pl_bydgosz01/discover_ec_pl_bydgosz01.py
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
SLUG = "ec_pl_bydgosz01"
UNIVERSIDAD = "Kazimierz Wielki University in Bydgoszcz"
GRADO = "Computer Science / ICT (Institute of Informatics) - courses in English for exchange students"
BASE = "https://erasmus.ukw.edu.pl/en/"
LIST = BASE + "courses/"
ICT_AREA = "17"  # «Information and Communication Technologies (ICTs) (061)»


def parse_list(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for blk in soup.select("div.col-md-9"):
        a = blk.find("a", href=re.compile(r"syllabus/(\d+)/"))
        txt = re.sub(r"\s+", " ", blk.get_text(" ", strip=True))
        mt = re.search(r"Title of course:\s*(.+?)\s*(?:Teacher\(s\):|Language of instruction:)", txt)
        if not a or not mt or "Information and Communication Technologies" not in txt:
            continue  # el filtro del servidor no persiste entre paginas: se conserva solo el area ICT
        title = mt.group(1)
        mc = re.search(r"\s*[\(\[]code:?\s*([^)\]]+)[\)\]]\s*$|\s*\[([^\]]+)\]\s*$", title)
        official = (mc.group(1) or mc.group(2)).strip() if mc else None
        if mc:
            title = title[: mc.start()].strip()
        ects = re.search(r"ECTS:\s*([\d.]+)", txt)
        # los campos ECTS/ISCED/Hours cuelgan del bloque hermano
        sib = " ".join(re.sub(r"\s+", " ", s.get_text(" ", strip=True)) for s in blk.find_next_siblings("div", limit=2))
        ects = ects or re.search(r"ECTS:\s*([\d.]+)", sib)
        out.append({"id": re.search(r"syllabus/(\d+)/", a["href"]).group(1), "title": title, "code": official,
                    "ects": float(ects.group(1)) if ects else None,
                    "winter": "Winter (autumn) semester: YES" in txt, "summer": "Summer (spring) semester: YES" in txt})
    return out


def fetch_list(http: PoliteClient) -> list[dict]:
    soup = BeautifulSoup(http.get_text(LIST), "lxml")
    data = {i["name"]: i.get("value", "") for i in soup.find("form").find_all("input", attrs={"type": "hidden"})}
    data.update({"idObszar": ICT_AREA, "idWydzial": "-1", "idSemestr": "-1"})
    items, seen = [], set()
    pages = [http.get_bytes(LIST, method="POST", data=data).decode("utf-8", "replace")]
    for n in range(1, 10):  # paginacion: courses/num/{n}/ (el filtro vive en la sesion)
        if f"courses/num/{n}/" not in pages[-1]:
            break
        pages.append(http.get_text(f"{LIST}num/{n}/"))
        if not parse_list(pages[-1]):
            break
    for html in pages:
        for it in parse_list(html):
            if it["id"] not in seen:
                seen.add(it["id"])
                items.append(it)
    return items


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    items = fetch_list(http)
    rows = []
    for it in items:
        code = it["code"] or f"UKW-{it['id']}"
        term = "/".join(t for t, f in (("winter", it["winter"]), ("summer", it["summer"])) if f) or "n/d"
        rows.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=it["title"],
            curso_semestre=f"Offered: {term}", curso=None, semestre=None, creditos_ects=it["ects"], caracter="optativa",
            idioma_pagina="en", url_guia_docente=f"{BASE}courses/syllabus/{it['id']}/", tipo_fuente="pdf"))
    total = sum(r.creditos_ects or 0 for r in rows)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2025-2026",
        url_plan_estudios=LIST, ects_totales_plan=None,
        estrategia_fuente="Catálogo Erasmus de la UKW (HTML, filtro POST por área ISCED 061 + paginación) + silabo PDF por asignatura",
        generado_por="discover_ec_pl_bydgosz01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: Computer Science / Informática (Institute of Informatics, Faculty of Mechanical Engineering): el Excel de UKW solo contiene "
               "Grado en Ingeniería Informática en Tecnologías de la Información y Doble Grado Informática+Datos. UKW no publica plan de estudios con guías en inglés; "
               "lo único público son las asignaturas ofertadas en inglés a estudiantes de intercambio (catálogo Erasmus). Se catalogan las del área ICT (061): "
               "es una oferta de cursos sueltos, sin curso/semestre del plan ni total de ECTS del grado (por eso 'parcial'); el nivel (grado/máster) lo da cada silabo. "
               "Código = código oficial entre corchetes si existe, si no 'UKW-{id del silabo}'. "
               f"Suma ECTS={total:g}."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(len(rows), "asignaturas; ECTS", total)


if __name__ == "__main__":
    main()
