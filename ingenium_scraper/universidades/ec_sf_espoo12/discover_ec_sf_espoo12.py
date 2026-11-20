"""Fase 1 - Aalto University (SF ESPOO12) - Bachelor's Programme in Electrical Engineering (ELEC1), 180 ECTS, School of Electrical Engineering.
Fuente: API publica JSON de Sisu (sisu.aalto.fi/kori/api, sin robots.txt -> permitido): arbol de reglas del programa (modulos -> unidades de curso) y
ficha de cada course-unit (outcomes, content, ...). Todo via PoliteClient.
Uso (desde la raiz): python universidades/ec_sf_espoo12/discover_ec_sf_espoo12.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_sf_espoo12"
UNIVERSIDAD = "Aalto University (School of Electrical Engineering)"
GRADO = "Bachelor's Programme in Electrical Engineering (ELEC1)"
API = "https://sisu.aalto.fi/kori/api/"
PROGRAMME_GROUP = "aalto-DP-203001"
PERIOD = "aalto-LV-75"  # 2025-2026
URL_PLAN = "https://sisu.aalto.fi/kori/api/modules/by-group-id?groupId=" + PROGRAMME_GROUP + "&universityId=aalto-yliopisto"


def tr(d: dict | None) -> str:
    """Texto multilingue: en, si no fi, si no sv."""
    d = d or {}
    return d.get("en") or d.get("fi") or d.get("sv") or ""


def lang_of(d: dict | None) -> str:
    d = d or {}
    return "en" if d.get("en") else ("fi" if d.get("fi") else "sv")


def course_url(group: str) -> str:
    return f"{API}course-units/by-group-id?groupId={group}&universityId=aalto-yliopisto"


def pick_version(versions: list[dict]) -> dict | None:
    if not versions:
        return None
    hit = [v for v in versions if PERIOD in (v.get("curriculumPeriodIds") or [])]
    return (hit or sorted(versions, key=lambda v: (v.get("validityPeriod") or {}).get("startDate") or ""))[-1]


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")

    def module(group: str):
        j = http.get_json(f"{API}modules/by-group-id?groupId={group}&universityId=aalto-yliopisto")
        return j[0] if j else None

    leaves: list[tuple[str, list[str]]] = []

    def walk(rule: dict, path: list[str]) -> None:
        t = rule.get("type")
        if t == "ModuleRule":
            m = module(rule["moduleGroupId"])
            if m:
                walk(m["rule"], path + [tr(m.get("name")) or m.get("code") or "?"])
        elif t == "CourseUnitRule":
            leaves.append((rule["courseUnitGroupId"], path))
        else:
            for k in ("rules", "rule"):
                v = rule.get(k)
                for x in (v if isinstance(v, list) else [v] if isinstance(v, dict) else []):
                    walk(x, path)

    root = module(PROGRAMME_GROUP)
    walk(root["rule"], [])
    rows, seen, skipped = [], set(), 0
    for group, path in leaves:
        if group in seen:
            continue
        seen.add(group)
        cu = pick_version(http.get_json(course_url(group)))
        if cu is None or not cu.get("code"):
            skipped += 1
            continue
        pth = " > ".join(path)
        low = pth.lower()
        car = "optativa" if re.search(r"elective|minor|vapaasti", low) else ("tfg" if re.search(r"bachelor.?s thesis|kandidaatintyö", tr(cu.get("name")).lower()) else "obligatoria")
        cr = (cu.get("credits") or {}).get("min")
        rows.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=cu["code"], nombre_asignatura=tr(cu.get("name")),
            curso_semestre=pth[:200], curso=None, semestre=None, creditos_ects=float(cr) if cr is not None else None, caracter=car,
            idioma_pagina=lang_of(cu.get("content") or cu.get("outcomes")), url_guia_docente=course_url(group), tipo_fuente="api"))
    # codigos repetidos (misma unidad en dos modulos) ya deduplicados por groupId; por si dos groupId comparten codigo
    cnt: dict[str, int] = {}
    for r in rows:
        cnt[r.codigo_asignatura] = cnt.get(r.codigo_asignatura, 0) + 1
        if cnt[r.codigo_asignatura] > 1:
            r.codigo_asignatura += f"_{cnt[r.codigo_asignatura]}"
    total = sum(r.creditos_ects or 0 for r in rows)
    langs = {x: sum(1 for r in rows if r.idioma_pagina == x) for x in {r.idioma_pagina for r in rows}}
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, nivel="bachelor", curso_academico="2025-2026",
        url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="API JSON pública de Sisu (kori/api): árbol de reglas del programa + course-units/by-group-id",
        generado_por="discover_ec_sf_espoo12.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación elegida: Bachelor's Programme in Electrical Engineering (ELEC1, 180 ECTS; la fila del Excel es el Máster en Ing. de Telecomunicación, "
               "pero el máster de Aalto es de 2.º ciclo y el grado afín —Eléctrica/Electrónica/Telecom— es este). Se incluyen los 4 majors "
               "(Automation and Robotics, Information Technology, Electronics and Electrophysics, Electrical Energy Engineering), estudios generales, lengua y optativas; "
               "por eso la suma de ECTS catalogados supera 180 (el alumno elige un major). Sin curso/semestre en la fuente (curso=null): "
               "curso_semestre guarda la ruta de módulos. Versión de cada unidad: la válida en 2025-26 (aalto-LV-75) o, si no, la más reciente. "
               f"Idioma de los textos (en/fi/sv): {langs}. Unidades sin código/versión omitidas: {skipped}. Suma ECTS={total:g}."))
    cat = Catalog(meta=meta, asignaturas=rows)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    assert len({r.codigo_asignatura for r in rows}) == len(rows)
    print(len(rows), "asignaturas; ECTS", total, langs, "omitidas", skipped)


if __name__ == "__main__":
    main()
