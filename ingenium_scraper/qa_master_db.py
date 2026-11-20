#!/usr/bin/env python3
"""Fase 4 · Consolidación en SQLite + informe de anomalías.

    python qa_master_db.py            # reconstruye db/ingenium_syllabi.db y reports/anomalias.md

La base de datos se reconstruye entera en cada ejecución a partir de los JSON
(los JSON son la fuente de verdad; la BD es un derivado desechable).
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows

import json
import re
import sqlite3
import time
from collections import Counter

from pydantic import ValidationError

from common.schema import Catalog, SyllabusRecord
from common.util import ROOT, REQUIRED_BLOCKS, load_catalog, read_markdown, safe_name, uni_dir, universities

DB = ROOT / "db" / "ingenium_syllabi.db"
# Lo que no debería sobrevivir a la anonimización: correos y secciones de profesorado
PII_RESIDUAL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+|^#+\s*(?:Profesorado|Profesores|Equipo docente|Coordinador(?:/a|a)?|Tutorías).*$", re.M | re.I)
REPORT = ROOT / "reports" / "anomalias.md"

DDL = """
CREATE TABLE institution (slug TEXT PRIMARY KEY, name TEXT, country TEXT, degree TEXT, academic_year TEXT, status TEXT, groups TEXT);
CREATE TABLE catalog_course (
  institution_slug TEXT, course_code TEXT, name TEXT, year INTEGER, semester INTEGER, ects REAL,
  course_type TEXT, language TEXT, source_url TEXT, source_type TEXT,
  has_markdown INTEGER, has_structured INTEGER, PRIMARY KEY (institution_slug, course_code));
CREATE TABLE course (
  id INTEGER PRIMARY KEY, institution_slug TEXT, course_code TEXT, name_original TEXT, name_en TEXT,
  ects REAL, semester TEXT, year_of_study INTEGER, course_type TEXT, languages TEXT,
  workload_total REAL, workload_contact REAL, isced_f TEXT, assessment_rules TEXT, source_url TEXT, source_language TEXT,
  extractor_model TEXT, extracted_at TEXT, UNIQUE (institution_slug, course_code));
CREATE TABLE learning_outcome (course_id INTEGER, pos INTEGER, type TEXT, code TEXT, text TEXT);
CREATE TABLE topic (course_id INTEGER, pos INTEGER, text TEXT);
CREATE TABLE assessment (course_id INTEGER, pos INTEGER, method TEXT, weight REAL);
CREATE TABLE prerequisite (course_id INTEGER, pos INTEGER, text TEXT);
CREATE TABLE teaching_method (course_id INTEGER, pos INTEGER, text TEXT);
CREATE TABLE bibliography (course_id INTEGER, pos INTEGER, text TEXT);
CREATE INDEX ix_lo ON learning_outcome(course_id); CREATE INDEX ix_topic ON topic(course_id);
"""


def _hay_ruta_de_100(weights: list[float]) -> bool:
    """True si algún subconjunto de pesos suma 100 (±1): las guías con rutas alternativas
    (evaluación continua / global / convocatoria extraordinaria) suman 100 por ruta y
    no son una anomalía. Limitación: un error real que contenga un subconjunto de 100 no se marca."""
    sums = {0.0}
    for w in weights:
        sums |= {round(x + w, 2) for x in sums}
    return any(abs(x - 100) <= 1 for x in sums if x > 0)


def build() -> list[tuple[str, str, str, str]]:
    """Devuelve la lista de anomalías: (universidad, asignatura, tipo, detalle)."""
    DB.parent.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(DDL)
    issues: list[tuple[str, str, str, str]] = []

    for u in universities():
        slug = u["slug"]
        raw = load_catalog(slug)
        if raw is None:
            con.execute("INSERT INTO institution VALUES (?,?,?,?,?,?,?)", (slug, u["name"], u["country"], None, None, "pendiente", ",".join(u["grupos"])))
            continue
        try:
            cat = Catalog.model_validate(raw)
        except ValidationError as e:
            issues.append((slug, "-", "catalogo_invalido", str(e).splitlines()[0] + f" ({e.error_count()} errores)"))
            con.execute("INSERT INTO institution VALUES (?,?,?,?,?,?,?)", (slug, u["name"], u["country"], None, None, "catalogo_invalido", ",".join(u["grupos"])))
            continue
        m = cat.meta
        con.execute("INSERT INTO institution VALUES (?,?,?,?,?,?,?)", (slug, u["name"], u["country"], m.nombre_grado, m.curso_academico, m.estado, ",".join(u["grupos"])))

        # --- créditos oficiales del RUCT (solo universidades españolas)
        oficiales = {t["creditos"].get("total") for t in u.get("titulos", []) if t.get("creditos")} - {None}
        if oficiales and m.ects_totales_plan is not None and m.ects_totales_plan not in oficiales:
            issues.append((slug, "-", "ects_plan_vs_ruct", f"catálogo declara {m.ects_totales_plan:g}; el RUCT registra {sorted(oficiales)}"))

        dup = [c for c, n in Counter(a.codigo_asignatura for a in cat.asignaturas).items() if n > 1]
        for c in dup:
            issues.append((slug, c, "codigo_duplicado", "aparece más de una vez en el catálogo"))

        seen = set()
        for a in cat.asignaturas:
            if a.codigo_asignatura in seen:
                continue
            seen.add(a.codigo_asignatura)
            stem = safe_name(a.codigo_asignatura)
            md = uni_dir(slug) / "raw_markdown" / f"{stem}.md"
            js = uni_dir(slug) / "structured_data" / f"{stem}.json"
            con.execute("INSERT INTO catalog_course VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                        (slug, a.codigo_asignatura, a.nombre_asignatura, a.curso, a.semestre, a.creditos_ects, a.caracter,
                         a.idioma_pagina, a.url_guia_docente, a.tipo_fuente, md.exists(), js.exists()))
            if not a.url_guia_docente or a.tipo_fuente == "sin_guia":
                issues.append((slug, a.codigo_asignatura, "sin_guia", a.nombre_asignatura))
            if a.creditos_ects is None:
                issues.append((slug, a.codigo_asignatura, "ects_ausente_catalogo", a.nombre_asignatura))
            if a.url_guia_docente and a.tipo_fuente != "sin_guia" and not md.exists():
                issues.append((slug, a.codigo_asignatura, "guia_no_descargada", f"{a.nombre_asignatura} (enlace sin guía publicada o error de descarga; ver logs/)"))
            if md.exists():
                head, body = read_markdown(md)
                if PII_RESIDUAL.search(body):
                    issues.append((slug, a.codigo_asignatura, "posible_dato_personal", PII_RESIDUAL.search(body).group(0)[:40]))
                missing = [b for b in REQUIRED_BLOCKS if not head.get("blocks_found", {}).get(b)]
                if missing:
                    issues.append((slug, a.codigo_asignatura, "bloques_no_localizados", ", ".join(missing)))
                if len(body) < 400:
                    issues.append((slug, a.codigo_asignatura, "markdown_muy_corto", f"{len(body)} caracteres"))
            if not js.exists():
                continue
            try:
                r = SyllabusRecord.model_validate(json.loads(js.read_text(encoding="utf-8")))
            except ValidationError as e:
                issues.append((slug, a.codigo_asignatura, "json_invalido", str(e).splitlines()[0]))
                continue
            cur = con.execute(
                "INSERT INTO course (institution_slug, course_code, name_original, name_en, ects, semester, year_of_study, course_type,"
                " languages, workload_total, workload_contact, isced_f, assessment_rules, source_url, source_language, extractor_model, extracted_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (slug, r.course_code, r.course_name_original, r.course_name_en, r.ects, r.semester, r.year_of_study, r.course_type,
                 ",".join(r.language_of_instruction), r.workload_hours_total, r.workload_hours_contact, r.isced_f_code, r.assessment_rules,
                 r.source_url, r.source_language, r.extractor_model, r.extracted_at))
            cid = cur.lastrowid
            con.executemany("INSERT INTO learning_outcome VALUES (?,?,?,?,?)", [(cid, i, o.type, o.code, o.text) for i, o in enumerate(r.learning_outcomes)])
            con.executemany("INSERT INTO assessment VALUES (?,?,?,?)", [(cid, i, s.method, s.weight_percentage) for i, s in enumerate(r.assessment_methods)])
            for table, items in (("topic", r.syllabus_topics), ("prerequisite", r.prerequisites),
                                 ("teaching_method", r.teaching_methods), ("bibliography", r.bibliography)):
                con.executemany(f"INSERT INTO {table} VALUES (?,?,?)", [(cid, i, t) for i, t in enumerate(items)])

            # --- controles de coherencia sobre el JSON extraído
            if r.ects is not None and a.creditos_ects is not None and abs(r.ects - a.creditos_ects) > 0.01:
                issues.append((slug, a.codigo_asignatura, "ects_inconsistente", f"catálogo {a.creditos_ects} vs guía {r.ects}"))
            weights = [s.weight_percentage for s in r.assessment_methods if s.weight_percentage is not None]
            if weights and len(weights) == len(r.assessment_methods) and abs(sum(weights) - 100) > 1 and not _hay_ruta_de_100(weights):
                issues.append((slug, a.codigo_asignatura, "pesos_evaluacion", f"suman {sum(weights):g} %"))
            if not r.syllabus_topics:
                issues.append((slug, a.codigo_asignatura, "sin_temario", ""))
            if not r.learning_outcomes:
                issues.append((slug, a.codigo_asignatura, "sin_resultados_aprendizaje", ""))
            if r.missing_sections:
                issues.append((slug, a.codigo_asignatura, "secciones_ausentes_en_guia", ", ".join(r.missing_sections)))
    con.commit()
    con.close()
    return issues


def write_report(issues: list[tuple[str, str, str, str]]) -> None:
    REPORT.parent.mkdir(exist_ok=True)
    lines = [f"# Informe de anomalías · INGENIUM syllabi", "", f"Generado: {time.strftime('%Y-%m-%d %H:%M')} · {len(issues)} anomalías", ""]
    if issues:
        lines += ["## Resumen por tipo", "", "| Tipo | Nº |", "|---|---|"]
        lines += [f"| {t} | {n} |" for t, n in Counter(i[2] for i in issues).most_common()]
        for slug in sorted({i[0] for i in issues}):
            lines += ["", f"## {slug}", "", "| Asignatura | Tipo | Detalle |", "|---|---|---|"]
            lines += [f"| {c} | {t} | {d.replace('|', '/')} |" for s, c, t, d in issues if s == slug]
    else:
        lines.append("Sin anomalías detectadas.")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    issues = build()
    write_report(issues)
    print(f"BD: {DB}\nInforme: {REPORT} ({len(issues)} anomalías)")


if __name__ == "__main__":
    main()
