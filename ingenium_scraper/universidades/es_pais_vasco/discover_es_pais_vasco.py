#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — UPV/EHU, Grado en Ingeniería Mecánica (RUCT 2502396),
Escuela de Ingeniería de Bilbao.

Fuente: la página oficial "Créditos y asignaturas" del grado (portal Liferay de ehu.eus, HTML
generado por XSL a partir de GAUR). Una tabla por curso y periodo (Anual / Cuatrimestre 1 / 2);
cada fila enlaza a la ficha de la asignatura, que contiene la guía docente.

Uso (desde la raíz del proyecto):
    python universidades/es_pais_vasco/discover_es_pais_vasco.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_pais_vasco"
UNI = "Universidad del País Vasco / Euskal Herriko Unibertsitatea"
GRADO = "Grado en Ingeniería Mecánica"
PLAN_URL = "https://www.ehu.eus/es/web/graduak/grado-ingenieria-mecanica-bizkaia/creditos-y-asignaturas"
# Desglose oficial del RUCT (config/universities_es.json, título 2502396)
RUCT = {"basica": 66.0, "obligatorios": 138.0, "optativos": 24.0, "practicas": 0.0, "tfg": 12.0, "total": 240.0}

CARACTER = {"básicas": "basica", "obligatoria": "obligatoria", "optativa": "optativa",
            "trabajo fin de grado": "tfg", "prácticas": "practicas"}
NO_IMPARTE = re.compile(r"\s*\*\*\s*No se imparten? en el curso actual\s*$", re.I)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def parse_plan(html: str):
    soup = BeautifulSoup(html, "lxml")
    rows, not_taught, summary, years = [], [], {}, set()
    for table in soup.find_all("table"):
        cap = norm(table.caption.get_text()) if table.caption else ""
        if cap == "Asignaturas del grado":  # tabla resumen de créditos por curso
            head = [norm(th.get_text(" ")) for th in table.find("tr").find_all(["th", "td"])]
            for tr in table.find_all("tr"):
                cells = [norm(c.get_text(" ")) for c in tr.find_all(["th", "td"])]
                if cells and cells[0] == "Total":
                    summary = {h: (0.0 if v == "--" else float(v.replace(",", ".")))
                               for h, v in zip(head[1:], cells[1:])}
            continue
        m_per = re.match(r"Asignaturas (Anual|Cuatrimestre (\d))$", cap)
        if not m_per:
            continue
        h2 = table.find_previous("h2")
        m_cur = re.match(r"Curso (\d)", norm(h2.get_text()))
        if not m_cur:
            raise SystemExit(f"Tabla '{cap}' sin cabecera de curso")
        curso = int(m_cur.group(1))
        cuatri = int(m_per.group(2)) if m_per.group(2) else None
        for tr in table.find("tbody").find_all("tr"):
            a = tr.find("a", href=re.compile("consultaAsignatura"))
            cells = [norm(c.get_text(" ")) for c in tr.find_all(["th", "td"])]
            if not a or len(cells) < 5:
                raise SystemExit(f"Fila inesperada en '{cap}': {cells}")
            url = urljoin(PLAN_URL, a["href"])
            q = parse_qs(urlsplit(url).query)
            code = q["asignatura"][0]
            years.add(q["anyo-academico"][0])
            name = cells[0]
            if NO_IMPARTE.search(name):
                name = NO_IMPARTE.sub("", name)
                not_taught.append(f"{code} {name}")
            # La ficha se pide en la versión castellana del portal (/es/): GAUR devuelve la guía en
            # castellano también para las asignaturas impartidas solo en euskera o en inglés
            # (comprobado sobre las 41 guías en la Fase 2).
            lang = "es"
            rows.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
                curso_semestre=f"Curso {curso} / {m_per.group(1)}",
                curso=curso, semestre=(curso - 1) * 2 + cuatri if cuatri else None,
                creditos_ects=float(cells[1].replace(",", ".")),
                caracter=CARACTER[cells[2].lower()],
                idioma_pagina=lang, url_guia_docente=url, tipo_fuente="html",
            ))
    return rows, not_taught, summary, years


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    rows, not_taught, summary, years = parse_plan(http.get_text(PLAN_URL))

    codes = [r.codigo_asignatura for r in rows]
    if len(codes) != len(set(codes)):
        raise SystemExit("Códigos duplicados en el plan")
    if len(years) != 1:
        raise SystemExit(f"Años académicos mezclados: {years}")
    y = int(next(iter(years))[:4])
    curso_acad = f"{y}-{(y + 1) % 100:02d}"

    by: dict[str, float] = {}
    for r in rows:
        by[r.caracter] = by.get(r.caracter, 0.0) + r.creditos_ects
    opt_need = RUCT["optativos"]
    total_plan = by.get("basica", 0) + by.get("obligatoria", 0) + by.get("tfg", 0) + opt_need
    checks = {
        "basica": by.get("basica", 0) == RUCT["basica"],
        "obligatoria": by.get("obligatoria", 0) == RUCT["obligatorios"],
        "tfg": by.get("tfg", 0) == RUCT["tfg"],
        "optativa_oferta>=exigida": by.get("optativa", 0) >= opt_need,
        "total": total_plan == RUCT["total"],
        "resumen_web": bool(summary) and summary.get("Total") == RUCT["total"],
    }
    notas = (
        "Centro elegido: Escuela de Ingeniería de Bilbao (primer centro del RUCT); el mismo título se imparte "
        "también en la Escuela de Ingeniería de Gipuzkoa y en la Escuela de Ingeniería de Vitoria-Gasteiz, "
        "cuyas ofertas no se han recogido. Plan único RD 1393/2007 (RUCT 2502396). "
        f"Créditos del catálogo por carácter: básica {by.get('basica', 0):g}, obligatoria "
        f"{by.get('obligatoria', 0):g}, optativa ofertada {by.get('optativa', 0):g} (se exigen {opt_need:g}), "
        f"TFG {by.get('tfg', 0):g}; suma del catálogo {sum(by.values()):g} ECTS frente a 240 del título porque "
        f"se listan todas las optativas ofertadas. Básica + obligatoria + {opt_need:g} optativos + TFG = "
        f"{total_plan:g}; coincide con el RUCT (66/138/24/0/12/240): "
        f"{'sí' if all(checks.values()) else 'NO ' + str(checks)}. "
        "No hay asignatura de prácticas externas en el plan publicado (RUCT: 0). "
        "Optativas marcadas 'No se imparten en el curso actual' (se mantienen en el catálogo): "
        f"{'; '.join(not_taught) or 'ninguna'}. "
        "Código de asignatura = código oficial GAUR (parámetro 'asignatura' de la URL y campo 'Código' de la "
        "ficha). Idioma por fila: 'es' en todas (la versión castellana del portal sirve la guía en castellano "
        "incluso para las asignaturas impartidas solo en euskera o inglés). Las asignaturas anuales llevan "
        "semestre nulo."
    )
    catalog = Catalog(
        meta=CatalogMeta(
            universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico=curso_acad,
            url_plan_estudios=PLAN_URL, ects_totales_plan=RUCT["total"],
            estrategia_fuente="HTML estático (portal Liferay ehu.eus, contenido XSL de GAUR): tablas por curso y "
                              "periodo en 'Créditos y asignaturas'; cada fila enlaza a la ficha con la guía docente",
            generado_por="discover_es_pais_vasco.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
            estado="ok", notas=notas,
        ),
        asignaturas=rows,
    )
    (HERE / "catalogo_urls.json").write_text(
        json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(rows)} asignaturas · {sum(by.values()):g} ECTS en catálogo · por carácter {by} · "
          f"curso {curso_acad} · comprobaciones {checks} · red={http.stats['network']} caché={http.stats['cache']}")
    if not all(checks.values()):
        raise SystemExit("El catálogo no cuadra con el desglose del RUCT")


if __name__ == "__main__":
    main()
