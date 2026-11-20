"""Fase 1 - Universidade do Porto, FEUP - Licenciatura em Engenharia Mecanica (L.EM, 180 ECTS).

Fuente: fichas de SIGARRA (sigarra.up.pt/feup) ya descargadas por el usuario, copiadas por prepare_fuente_previa.py
a fuente_previa/ (SIGARRA responde 403 a PoliteClient: ver notas_descubrimiento.md).
Uso: python universidades/ec_p_porto02/discover_ec_p_porto02.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_p_porto02"
UNIVERSIDAD = "Universidade do Porto - Faculdade de Engenharia (FEUP)"
GRADO = "Licenciatura em Engenharia Mecânica (L.EM)"
URL_PLAN = "https://sigarra.up.pt/feup/pt/"  # portal FEUP; URL exacto del plan L.EM no verificado (403)


def main() -> None:
    fichas = json.loads((HERE / "fuente_previa" / "feup_fichas.json").read_text(encoding="utf-8"))
    entries = []
    for f in fichas:
        sem_txt = (f["instance"] or "")
        sem_in_year = 1 if "1S" in sem_txt else 2 if "2S" in sem_txt else None
        year = f["year_lem"]
        sem = (year - 1) * 2 + sem_in_year if year and sem_in_year else None
        is_core = f["code"].startswith("L.EM")
        lang = (f["sections"].get("Teaching language") or "").strip() or "n/d"
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=f["code"], nombre_asignatura=f["name"],
            curso_semestre=f"Curso {year or '?'} / {'1S' if sem_in_year == 1 else '2S' if sem_in_year == 2 else '?'} ({lang})",
            curso=year, semestre=sem, creditos_ects=float(f["ects"].replace(",", ".")),
            caracter="obligatoria" if is_core else "optativa", idioma_pagina="en",
            url_guia_docente=f["link"], tipo_fuente="html"))
    entries.sort(key=lambda e: (e.curso or 9, e.semestre or 9, e.codigo_asignatura))
    core = sum(e.creditos_ects or 0 for e in entries if e.codigo_asignatura.startswith("L.EM"))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/26", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0,
        estrategia_fuente="Fichas SIGARRA (versión EN) descargadas previamente por el usuario; curso/semestre de la ficha",
        generado_por="discover_ec_p_porto02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación: Licenciatura em Engenharia Mecânica (L.EM), 1.er ciclo, 3 años. Las {sum(e.codigo_asignatura.startswith('L.EM') for e in entries)} UC L.EM "
               f"suman {core:g} ECTS de 180; el resto son UC transversales de 1,5 ECTS (CTLGE01, AADL01, ...) y optativas no incluidas. "
               "SIGARRA devuelve HTTP 403 (Cloudflare) a PoliteClient aunque robots.txt permite User-agent *: regla de parada, el pipeline no la consulta. "
               "Las fichas proceden de la extracción previa del usuario: algunas palabras portuguesas pierden caracteres acentuados (decodificación con errors=ignore). "
               "Idioma de la ficha: inglés (idioma de docencia indicado en curso_semestre; casi todas en portugués). La plataforma lleva Content-Signal ai-train=no (uso del contenido para entrenar IA reservado)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS L.EM", core)


if __name__ == "__main__":
    main()
