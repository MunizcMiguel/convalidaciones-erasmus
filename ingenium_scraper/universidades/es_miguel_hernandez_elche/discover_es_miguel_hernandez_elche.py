#!/usr/bin/env python3
"""Fase 1 — UMH, Grado en Ingeniería Mecánica (Escuela Politécnica Superior de Elche).

Fuente: endpoint JSON del portal umh.es (`/get_dataJson.py?item=:tit_g_143_S1&frm=DEFAULT&lang=ES`), el mismo que usa la web
para pintar la ficha; la lista `_x_inv_asignatura_pertenece_a_estudio` trae todas las asignaturas con curso, semestre, tipo y ECTS.
Uso: python universidades/es_miguel_hernandez_elche/discover_es_miguel_hernandez_elche.py
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_miguel_hernandez_elche", "Universidad Miguel Hernández de Elche"
GRADO = "Grado en Ingeniería Mecánica"
TIT = ":tit_g_143_S1"
API = "https://www.umh.es/get_dataJson.py?item={item}&frm=DEFAULT&lang=ES"
CAR = {"Básica": "formacion_basica", "Obligatoria": "obligatoria", "Optativa": "optativa", "Trabajo Fin Grado": "tfg"}
RUCT = {"formacion_basica": 60, "obligatoria": 150, "tfg": 12}


def num(v):
    return float(str(v[0]).lstrip("~f$").replace(",", "."))


def load(http, item):
    t = http.get_bytes(API.format(item=item)).decode("utf-8")
    return json.JSONDecoder().raw_decode(t[t.index("={") + 1:])[0]


if __name__ == "__main__":
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    d = load(http, TIT)
    entries = []
    for x in d["_x_inv_asignatura_pertenece_a_estudio"]:
        item = x["href"]  # ":asi_g_1801_S1"
        code = item.split("_")[2]
        curso, sem = x["_x_curso_asignatura"][0], x["_x_semestre"][0]
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=x["label"].strip().capitalize() if x["label"].isupper() else x["label"],
            curso_semestre=f"Curso {curso} / Semestre {sem}", curso=curso,
            semestre=(curso - 1) * 2 + sem if sem in (1, 2) else None, creditos_ects=num(x["_x_creditos_totales_asignatura"]),
            caracter=CAR[x["_x_tipo_asignatura"][0].lstrip("~$")], idioma_pagina="es",
            url_guia_docente=f"https://www.umh.es/contenido/Estudios/{item}/datos_es.html", tipo_fuente="api"))
    entries.sort(key=lambda e: (e.curso, e.semestre or 9, e.codigo_asignatura))
    assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
    s = {}
    for e in entries:
        s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
    assert all(s[k] == v for k, v in RUCT.items()), s
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios="https://www.umh.es/contenido/Estudios/:tit_g_143_S1/datos_es.html",
        ects_totales_plan=240.0,
        estrategia_fuente="JSON del portal umh.es (get_dataJson.py) del título :tit_g_143_S1; cada asignatura tiene su propio JSON (:asi_g_NNNN_S1).",
        generado_por="discover_es_miguel_hernandez_elche.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"{len(entries)} asignaturas, centro único (EPS Elche). ECTS por carácter {json.dumps(s)}: básica 60, obligatorias 150 y TFG 12 = RUCT; "
               f"se ofertan {s['optativa']:g} ECTS optativos y el RUCT exige 18 (prácticas 0). Total cursado 60+150+18+12=240. Código = número de la asignatura en el portal (asi_g_{{código}}_S1). "
               f"Guía de curso 2026 (validada 2026)."),
    )
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), s, http.stats)
