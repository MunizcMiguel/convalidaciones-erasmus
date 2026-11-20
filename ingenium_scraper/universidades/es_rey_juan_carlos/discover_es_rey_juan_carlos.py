#!/usr/bin/env python3
"""Fase 1 — URJC, Grado en Ingeniería Mecánica (Móstoles).

Fuente: Guías Docentes de la URJC (servicios.urjc.es/guiasdocentes; gestion3.urjc.es redirige aquí). El grado aparece como dos
titulaciones SIAC: 2404 «(1º y 2º curso)» = plan RD 822/2021 en implantación, y 2286 «(3º y 4º curso)» = plan anterior para los
cursos superiores. Listado: POST getAsignaturasAlumnoAjax.jsp?codPlan=..&alumno=1&cursoAcademico=2026-27 (XML).
Guía: POST pdfGuia.jsp (txtCursoAcademico, txtTitulacion, txtAsignatura) -> PDF (con texto). Tipo, curso/semestre y ECTS se leen
de la sección «I.-Identificación» del PDF. Para que la caché de PoliteClient distinga POST distintos se añade `?a={codigo}` a la URL.
Uso: python universidades/es_rey_juan_carlos/discover_es_rey_juan_carlos.py
"""
import io
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_rey_juan_carlos", "Universidad Rey Juan Carlos"
GRADO = "Grado en Ingeniería Mecánica"
B = "https://servicios.urjc.es/guiasdocentes/"
ANYO = "2026-27"
PLANES = ["2404", "2286"]
CAR = {"formación básica": "formacion_basica", "obligatoria": "obligatoria", "optativa": "optativa", "prácticas externas": "practicas",
       "trabajo fin de grado": "tfg"}


def pdf_url(plan, code):
    return f"{B}pdfGuia.jsp?a={code}"


def fetch_pdf(http, plan, code):
    return http.get_bytes(pdf_url(plan, code), method="POST", data={"txtCursoAcademico": ANYO, "txtTitulacion": plan, "txtAsignatura": code})


def ident(data: bytes) -> dict:
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        txt = pdf.pages[1].extract_text() or ""
    out = {}
    for k, pat in {"tipo": r"Tipo\s+(.+)", "periodo": r"Período de impartición\s+(.+)", "ects": r"Nº de créditos\s+([\d.,]+)", "idioma": r"Idioma en el que se imparte\s+(.+)"}.items():
        m = re.search(pat, txt)
        out[k] = m.group(1).strip() if m else None
    return out


if __name__ == "__main__":
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    http.get_bytes(B, force=True)  # cookie de sesión
    entries, falta = [], []
    for plan in PLANES:
        xml = http.get_bytes(B + f"getAsignaturasAlumnoAjax.jsp?codPlan={plan}&alumno=1&cursoAcademico={ANYO}", method="POST").decode("utf-8")
        for code, nombre in re.findall(r"cod='(\d+)'>([^<]+)<", xml):
            try:
                data = fetch_pdf(http, plan, code)
            except FetchError:
                data = b""
            if not data.startswith(b"%PDF"):
                falta.append(code)
                continue
            i = ident(data)
            per = i["periodo"] or ""
            m = re.search(r"(\d)\s*curso(?:,\s*(\d)Q)?", per)
            curso = int(m.group(1)) if m else None
            sem = int(m.group(2)) if m and m.group(2) else None
            tipo = (i["tipo"] or "").lower()
            entries.append((plan, code, nombre.strip(), curso, sem, per, i["ects"], tipo, i["idioma"]))
    # Catálogo: 1.º-2.º del plan 2404 (RD 822/2021, en implantación) + 3.º-4.º del plan 2286 (lo que la URJC publica para los cursos
    # superiores). El listado 2286 también trae asignaturas de 1.º-2.º del plan antiguo (a extinguir): se descartan.
    out, descartadas = [], []
    for plan, code, nombre, curso, sem, per, ects, tipo, idioma in entries:
        if (plan == "2404" and curso in (1, 2)) or (plan == "2286" and curso in (3, 4)):
            nm = nombre.strip().capitalize()
            if tipo == "formación básica":
                car = "formacion_basica"
            elif re.search(r"trabajo fin de grado", nombre, re.I):
                car = "tfg"
            elif re.search(r"pr[aá]cticas externas", nombre, re.I):
                car = "practicas"
            elif tipo == "optativa":
                car = "optativa"
            else:
                car = "obligatoria"
            out.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nm, curso_semestre=f"Curso {curso} / {per}",
                curso=curso, semestre=(curso - 1) * 2 + sem if sem else None, creditos_ects=float(ects.replace(",", ".")), caracter=car,
                idioma_pagina="es", url_guia_docente=pdf_url(plan, code), tipo_fuente="pdf"))
        else:
            descartadas.append(code)
    assert len({e.codigo_asignatura for e in out}) == len(out), "duplicados"
    s = {}
    for e in out:
        s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
    print(len(out), s, "descartadas:", len(descartadas), "sin PDF:", falta)
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico=ANYO, url_plan_estudios=B, ects_totales_plan=240.0,
        estrategia_fuente="Guías Docentes URJC (servicios.urjc.es/guiasdocentes): listado XML por titulación SIAC (2404 y 2286) y guía = PDF por asignatura (POST pdfGuia.jsp); tipo, periodo y ECTS leídos de la sección I del PDF.",
        generado_por="discover_es_rey_juan_carlos.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"{len(out)} asignaturas: 1.º-2.º de la titulación 2404 (plan RD 822/2021 en implantación) + 3.º-4.º de la 2286 (plan anterior, aún vigente para los cursos superiores); "
               f"el listado 2286 incluye además {len(descartadas) - len(falta)} asignaturas de 1.º-2.º del plan antiguo, descartadas por duplicar el contenido del 2404, y {len(falta)} códigos 2286 cuya guía devuelve HTTP 500 (no publicada; su curso no se puede determinar) que se omiten: {', '.join(falta)}. "
               f"ECTS por carácter {json.dumps(s)} frente al RUCT 60 básica/144 obligatorias/12 optativas/12 prácticas/12 TFG: NO cuadra (la mezcla de planes y las guías no publicadas dejan huecos; optativas del plan nuevo y de 4.º todavía sin guía). Verificar a mano. "
               f"Idioma: castellano (2 asignaturas 'Idioma moderno' en otro idioma). Los cursos 3.º-4.º aparecen con el curso del PDF."),
    )
    cat = Catalog(meta=meta, asignaturas=out)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(http.stats)
