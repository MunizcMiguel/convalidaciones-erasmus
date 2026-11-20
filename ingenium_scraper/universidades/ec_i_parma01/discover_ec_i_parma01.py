"""Fase 1 - Universita di Parma - Laurea in Ingegneria Meccanica (L-9, triennale; CdS 3011 + 3111 desde 2025).

Fuente: export del Excel oficial "Offerta Formativa 2025-2026" de UNIPR (hoja 'Insegnamenti e coperture'),
preparado en fuente_previa/ por prepare_fuente_previa.py. corsi.unipr.it responde 405 a PoliteClient, por eso
NO se accede a la web desde el pipeline (ver notas_descubrimiento.md).
Uso: python universidades/ec_i_parma01/discover_ec_i_parma01.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_parma01"
UNIVERSIDAD = "Università degli Studi di Parma"
GRADO = "Ingegneria Meccanica (Laurea, L-9)"
URL_PLAN = "https://corsi.unipr.it/en/ugov/degree/3011"
URL_FICHA = "https://corsi.unipr.it/en/ugov/degreecourse/{id}"
CARACTER = {"Base": "obligatoria", "Caratterizzante": "obligatoria", "Affine/Integrativa": "obligatoria",
            "A scelta dello studente": "optativa", "Lingua/Prova Finale": "tfg", "Altro": "obligatoria"}


def main() -> None:
    plan = json.loads((HERE / "fuente_previa" / "unipr_plan.json").read_text(encoding="utf-8"))
    fichas = json.loads((HERE / "fuente_previa" / "unipr_fichas.json").read_text(encoding="utf-8"))
    by: dict[str, list[dict]] = {}
    for r in plan:
        by.setdefault(r["code"], []).append(r)
    entries = []
    for code, rows in by.items():
        names = {(r["name_en"] or r["name_it"]).strip().lower() for r in rows}
        assert len(names) == 1, (code, names)
        r = next((x for x in rows if fichas.get(str(x["id"]), {}).get("sections")), rows[0])
        has = bool(fichas.get(str(r["id"]), {}).get("sections"))
        year = int(r["year"])
        per = (r["periodo"] or "").strip()
        sem = None
        if per.startswith("II°"):
            sem = (year - 1) * 2 + 2
        elif per.startswith("I°"):
            sem = (year - 1) * 2 + 1
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code,
            nombre_asignatura=(r["name_en"] or r["name_it"]).strip(),
            curso_semestre=f"Curso {year} / {per or 'n/d'}", curso=year, semestre=sem,
            creditos_ects=float(r["cfu"]), caracter=CARACTER.get(r["ambito"], "obligatoria") if r["ambito"] else None,
            idioma_pagina="en", url_guia_docente=URL_FICHA.format(id=r["id"]) if has else None,
            tipo_fuente="html" if has else "sin_guia"))
    entries.sort(key=lambda e: (e.curso or 0, e.codigo_asignatura))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/26", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0,
        estrategia_fuente="Excel oficial Offerta Formativa 2025-26 (export JSON previo) + fichas HTML de corsi.unipr.it ya descargadas por el usuario",
        generado_por="discover_ec_i_parma01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación: Laurea (triennale) in Ingegneria Meccanica, L-9: CdS 3011 (cohortes 2023 y 2024, cursos 2.º-3.º) y CdS 3111 "
               "(nuevo ordenamiento 2025, 1.er curso). Se descartó el CdS 5016 (Laurea Magistrale, LM-33; deducido de los datos, no verificado en la web). "
               "El Excel solo lista los insegnamenti ofertados con cobertura en 2025/26 y mezcla curricula (GEN, 261, 398, 399): son los cursos únicos "
               "por código, no el plan completo de 180 ECTS (la suma de ECTS del catálogo no equivale al plan). corsi.unipr.it devuelve HTTP 405 a "
               "PoliteClient (filtro anti-bot): el pipeline no la consulta; las fichas proceden de la descarga previa del usuario (versión inglesa; "
               "'sin_guia' = ficha sin contenido publicado). Idioma de docencia según el Excel: mayoría italiano."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas;", sum(e.tipo_fuente == "html" for e in entries), "con ficha;", "ECTS", sum(e.creditos_ects or 0 for e in entries))


if __name__ == "__main__":
    main()
