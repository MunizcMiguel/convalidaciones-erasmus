"""Fase 1 - TU Hamburg (TUHH) - Maschinenbau / Mechanical Engineering (B.Sc., 7 semestres, 210 CP).

Fuente: Modulhandbuch oficial (HTML ingles, un unico documento con todos los modulos) enlazado desde
https://studienplaene.tuhh.de/index.php?stgart=B&stgB=MBBS&kid=54&Lang=en (cohorte WiSe 2026/27).
Uso: python universidades/ec_d_hamburg03/discover_ec_d_hamburg03.py
"""
from __future__ import annotations

import html as htmllib
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_hamburg03"
UNIVERSIDAD = "Technische Universität Hamburg (TUHH)"
GRADO = "Maschinenbau / Mechanical Engineering (B.Sc.)"
URL_PLAN = "https://studienplaene.tuhh.de/index.php?stgart=B&stgB=MBBS&kid=54&Lang=en"
ECTS_PLAN = 210.0


def module_blocks(s: BeautifulSoup):
    """Itera (seccion_h1, tabla_mHead, tabla_mContent) en orden de documento."""
    section = ""
    for el in s.find_all(["h1", "table"]):
        if el.name == "h1":
            section = el.get_text(" ", strip=True)
        elif el.name == "table" and "mHead" in (el.get("class") or []):
            content = el.find_next("table", class_="mContent")
            yield section, el, content


def mech_assignment(content) -> str:
    for tr in content.find_all("tr"):
        l = tr.find("td", class_="l")
        if l and l.get_text(strip=True).startswith("Assignment for the Following Curricula"):
            txt = tr.find("td", class_="r").get_text(" ", strip=True)
            m = re.search(r"(?<![\w-])Mechanical Engineering: ([^:]+): (Elective Compulsory|Compulsory|Elective)", txt)
            return f"{m.group(1)}: {m.group(2)}".strip() if m else ""
    return ""


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    page = c.get_text(URL_PLAN)
    links = [htmllib.unescape(h) for h in re.findall(r'href="([^"]+)"', page)]
    rel = next(h for h in links if re.search(r"po/MB/mhb_MBBS_kh_w\d+_von_\d+_v_\d+_en\.html$", h))
    url = urljoin(URL_PLAN, rel)
    s = BeautifulSoup(c.get_text(url), "lxml")
    entries, seen = [], set()
    for section, head, content in module_blocks(s):
        m = re.match(r"Module\s+(M-?\d+):\s*(.+)$", head.find("h2").get_text(" ", strip=True))
        code, name = m.group(1), m.group(2).strip()
        if code in seen:
            continue
        seen.add(code)
        cp = None
        for tr in content.find_all("tr"):
            l = tr.find("td", class_="l")
            if l and l.get_text(strip=True) == "Credit points":
                cp = float(re.sub(r"[^\d.,]", "", tr.find("td", class_="r").get_text()).replace(",", "."))
        assign = mech_assignment(content)
        caracter = "tfg" if section == "Thesis" else ("optativa" if "Elective" in assign or section.startswith("Specialization") else "obligatoria")
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
            curso_semestre=f"{section}" + (f" ({assign})" if assign else ""), curso=None, semestre=None,
            creditos_ects=cp, caracter=caracter, idioma_pagina="en", url_guia_docente=url, tipo_fuente="html"))
    core = sum(e.creditos_ects or 0 for e in entries if e.curso_semestre.startswith("Core Qualification"))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="WiSe 2026/27", url_plan_estudios=URL_PLAN,
        ects_totales_plan=ECTS_PLAN, estrategia_fuente="Modulhandbuch HTML inglés único (studienplaene.tuhh.de), una tabla por módulo",
        generado_por="discover_ec_d_hamburg03.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Maschinenbau (Bachelor of Science, 7 semestres, 210 CP; código TUHH MBBS). {len(entries)} módulos: Core Qualification ({core:g} CP), "
               "7 especializaciones (se cursa una) y Thesis; por eso los CP de todas las filas superan 210. El Modulhandbuch NO asigna semestre a cada módulo "
               "(curso/semestre = null) ni incluye contenidos/programa ni bibliografía: solo objetivos, carga de trabajo, créditos, examen y asignación a currículos; "
               "las fichas de curso (Lehrveranstaltungen) se publican aparte y no se localizaron. Catálogo parcial por eso. robots.txt de studienplaene.tuhh.de permite; "
               "www.tuhh.de/robots.txt se auto-veta (Disallow: /robots.txt) y PoliteClient lo informa como bloqueado, pero no se usó ninguna página de www.tuhh.de. "
               "Idioma: inglés (existe versión alemana)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos; CP core", core, "; url", url)


if __name__ == "__main__":
    main()
