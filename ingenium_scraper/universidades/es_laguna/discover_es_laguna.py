#!/usr/bin/env python3
"""Fase 1 — Universidad de La Laguna, Grado en Ingeniería Mecánica (Escuela Superior de Ingeniería y Tecnología).

Fuente: Portal de Guías Docentes de la ULL (www.ull.es/apps/guias). La página del grado
(`/guias/view_degree/Grado en Ingeniería Mecánica/`) lista, por curso y cuatrimestre (y "Anuales"), "código - nombre" con enlace a
`/guias/view_guide/{id}/` (id interno del curso 2026-27). Los créditos y el carácter no están en el listado: se leen del apartado
"1. Datos descriptivos" del PDF de la propia guía (`/guias/print_guide/{id}/`), que es la URL de guía del catálogo.
Uso: python universidades/es_laguna/discover_es_laguna.py
"""
import io
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_laguna", "Universidad de La Laguna"
GRADO = "Grado en Ingeniería Mecánica"
BASE = "https://www.ull.es"
URL = f"{BASE}/apps/guias/guias/view_degree/Grado%20en%20Ingenier%C3%ADa%20Mec%C3%A1nica/"

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
curso_acad = re.search(r"\((\d{4}) - (\d{4})\)", soup.find("h1").get_text() if soup.find("h1") else soup.get_text())
curso_acad = f"{curso_acad.group(1)}-{curso_acad.group(2)[2:]}" if curso_acad else "2026-27"

rows, curso, cuat = [], None, None
for el in soup.find_all(["div", "strong", "a"]):
    cls = el.get("class") or []
    t = el.get_text(" ", strip=True)
    if el.name == "div" and "panel-heading" in cls and re.fullmatch(r"Curso \d", t):
        curso = int(t.split()[1])
    elif el.name == "strong" and t in ("Primer cuatrimestre", "Segundo cuatrimestre", "Anuales"):
        cuat = t
    elif el.name == "a" and re.match(r"\d{9} - ", t) and curso:
        m = re.match(r"(\d{9}) - (.+)", t)
        gid = re.search(r"view_guide/(\d+)", el["href"]).group(1)
        rows.append((m.group(1), m.group(2).strip(), curso, cuat, gid))


def datos(pdf_bytes: bytes) -> dict:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        txt = chr(10).join((pg.extract_text(x_tolerance=1.5) or "") for pg in pdf.pages[:2])
    d = {}
    for k in ("Código", "Carácter", "Duración", "Créditos ECTS", "Idioma"):
        m = re.search(rf"{k}: ([^\n]+?)(?: Código:|\n|$)", txt)
        if m:
            d[k] = m.group(1).strip()
    return d


def caracter(txt: str, nombre: str) -> str:
    t = txt.lower()
    if "trabajo fin" in t or nombre.lower().startswith("trabajo fin"):
        return "tfg"
    if "prácticas" in t or nombre.lower().startswith("prácticas externas"):
        return "practicas"
    if "básica" in t:
        return "formacion_basica"
    if "optativ" in t:
        return "optativa"
    if "obligatori" in t:
        return "obligatoria"
    raise ValueError(f"carácter desconocido: {txt!r}")


entries = []
for code, nombre, cu, cu4, gid in rows:
    pdf_url = f"{BASE}/apps/guias/guias/print_guide/{gid}/"
    d = datos(http.get_bytes(pdf_url))
    assert d.get("Código") == code, (code, d)
    rel = {"Primer cuatrimestre": 1, "Segundo cuatrimestre": 2}.get(cu4)
    idioma = "es"
    entries.append(CatalogEntry(
        universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
        curso_semestre=f"Curso {cu} / {cu4}", curso=cu, semestre=(cu - 1) * 2 + rel if rel else None,
        creditos_ects=float(d["Créditos ECTS"].replace(",", ".")), caracter=caracter(d["Carácter"], nombre),
        idioma_pagina=idioma, url_guia_docente=pdf_url, tipo_fuente="pdf"))

assert len({e.codigo_asignatura for e in entries}) == len(entries)
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico=curso_acad, url_plan_estudios=URL,
    ects_totales_plan=240.0,
    estrategia_fuente="HTML del Portal de Guías de la ULL (listado por curso/cuatrimestre); créditos y carácter leídos del PDF de cada guía (print_guide).",
    generado_por="discover_es_laguna.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"Centro: Escuela Superior de Ingeniería y Tecnología (único en el RUCT). Plan 2020. {len(entries)} asignaturas. "
           f"ECTS ofertados por carácter: {json.dumps(s)}. RUCT: 60 básica / 144 obligatorias / 12 optativas / 12 prácticas / 12 TFG. "
           f"Las optativas ofertadas (códigos 3394039xx, 3394049xx) superan los 12 ECTS que se cursan. 'Anuales' = sin semestre."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, http.stats)
