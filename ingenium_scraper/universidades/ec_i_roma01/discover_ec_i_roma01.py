#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Sapienza Università di Roma, Laurea in Ingegneria Informatica e Automatica (L-8).

Fuente: catálogo corsidilaurea.uniroma1.it (HTML estático, Drupal). Plan: /it/course/33501/attendance/lessons-plan
(filas tr.activity con código, nombre, SSD, idioma, año, semestre, CFU y enlace a la ficha).

Uso: python universidades/ec_i_roma01/discover_ec_i_roma01.py
"""
from __future__ import annotations

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
SLUG = "ec_i_roma01"
UNIVERSIDAD = "Sapienza Università di Roma"
HOST = "https://corsidilaurea.uniroma1.it"
PLAN = f"{HOST}/it/course/33501/attendance/lessons-plan"
GRADO = "Laurea in Ingegneria Informatica e Automatica (L-8)"


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def num(s: str) -> int | None:
    m = re.search(r"\d+", s or "")
    return int(m.group()) if m else None


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    soup = BeautifulSoup(http.get_text(PLAN, encoding="utf-8"), "lxml")
    anio_ref = soup.find(string=re.compile(r"Curricula per l.anno"))
    curso_acad = re.search(r"anno (\d{4})", anio_ref or "")
    aa = int(curso_acad.group(1)) if curso_acad else 2026
    rows: dict[str, dict] = {}
    for tr in soup.select("tr.activity"):
        a = tr.select_one("span.activity-name a")
        tds = tr.find_all("td")
        if a is None or len(tds) < 4:
            continue
        code_el = tr.select_one("span.activity-code")
        name = a.get_text(" ", strip=True)
        code = code_el.get_text(strip=True) if code_el else ""
        key = code or slugify(name)
        meta = tr.select_one("strong").get_text(" ", strip=True) if tr.select_one("strong") else ""
        ssd = re.search(r"\[([^\]]+)\]", meta)
        lang = re.findall(r"\[([A-Z]{3})\]", meta)
        curso, sem = num(tds[1].get_text()), num(tds[2].get_text())
        cfu = float(num(tds[3].get_text()) or 0)
        curr = tr.find_parent("table")
        cap = curr.find_previous(string=re.compile(r"^\s*(Automatica|Informatica)\s*$")) if curr else None
        row = rows.setdefault(key, dict(name=name, href=urljoin(HOST, a["href"]), curso=curso, sem=sem, cfu=cfu,
                                        ssd=ssd.group(1) if ssd else "", lang=lang[-1] if lang else "ITA", curr=set()))
        row["curr"].add(cap.strip() if cap else "")
    entries = []
    for key, r in rows.items():
        up = r["name"].upper()
        car = "tfg" if "PROVA FINALE" in up else "libre_eleccion" if "SCELTA" in up else "obligatoria"
        sin = car == "libre_eleccion" or r["cfu"] == 0
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=key,
            nombre_asignatura=r["name"],
            curso_semestre=f"Anno {r['curso']} / Semestre {r['sem']} / A.A. {aa}/{aa+1} / SSD {r['ssd']} / {', '.join(sorted(c for c in r['curr'] if c)) or 'comune'}",
            curso=r["curso"], semestre=((r["curso"] - 1) * 2 + r["sem"]) if r["curso"] and r["sem"] else None,
            creditos_ects=r["cfu"], caracter=car, idioma_pagina="en" if r["lang"] == "ENG" else "it",
            url_guia_docente=None if sin else r["href"], tipo_fuente="sin_guia" if sin else "html"))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO,
        curso_academico=f"A.A. {aa}/{aa+1}", url_plan_estudios=PLAN, ects_totales_plan=180.0,
        estrategia_fuente="HTML estático de corsidilaurea.uniroma1.it: tabla de insegnamenti (tr.activity) -> ficha por insegnamento (/attendance/lesson/<curriculum>/<año>/<sem>/<id>?channel=0).",
        generado_por="discover_ec_i_roma01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Laurea triennale en Ingegneria Informatica e Automatica (L-8, curso 33501, currículos Automatica e Informatica). "
               "Las filas Erasmus de Roma Sapienza son Ciencia e Ingeniería de Datos (2 plazas), dobles Informática+Datos y Teleco+Datos y un Máster Industrial: "
               "no hay Mecánica/Industrial en grado; se elige la laurea de Informática/Automática (la más afín a Datos/Informática; Telecomunicaciones es otra laurea, 33497). "
               "Ingeniería de Datos como tal solo existe en máster. Unión de ambos currículos; ECTS ofertados por currículo no verificados contra 180. "
               "Se omiten las fichas de 'A scelta dello studente' (sin_guia). Cada insegnamento puede tener varios canales (profesores); se toma el canal 0. "
               "Idioma: italiano (la UI en inglés no traduce el contenido)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(cat.model_dump())
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(entries)} filas, {sum(e.creditos_ects for e in entries):g} ECTS, sin_guia={sum(e.tipo_fuente=='sin_guia' for e in entries)}; HTTP {http.stats}")


if __name__ == "__main__":
    main()
