#!/usr/bin/env python3
"""Fase 1 — UPCT, Grado en Ingeniería Mecánica (ETSII, código 5081).

Fuente: estudios.upct.es (Laravel + Vue): `POST /obtenerPlan {cod_estudio, any_anyaca}` con el token CSRF de la página del plan.
Las guías las sirve campusvirtual.upct.es/uxxiportal/servlets/public/guiaDocenteServlet (PDF), cuyo robots.txt las prohíbe
(PoliteClient lanza RobotsBlocked): estado "parcial", sin Fase 2. industriales.upct.es/guia-docente también está vetado.
Uso: python universidades/es_politecnica_cartagena/discover_es_politecnica_cartagena.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_politecnica_cartagena", "Universidad Politécnica de Cartagena"
GRADO = "Grado en Ingeniería Mecánica"
PLAN_URL = "https://estudios.upct.es/grado/5081/plan-de-estudios"
GUIA = "https://campusvirtual.upct.es/uxxiportal/servlets/public/guiaDocenteServlet?anyAnyaca={a}&assCodnum={c}&idioma=es&modalidad=P"
ANYO = "2026-27"
RUCT = {"basica": 60, "obligatorios": 138, "tfg": 12, "optativos": 30}

http = PoliteClient(cache_dir=HERE / "raw_cache")
html = http.get_bytes(PLAN_URL, force=True).decode("utf-8")  # force: hace falta la cookie de sesión que casa con el token
tok = re.search(r"X-CSRF-TOKEN'\] = '([^']+)'", html).group(1)
d = json.loads(http.get_bytes("https://estudios.upct.es/obtenerPlan", method="POST", headers={"X-CSRF-TOKEN": tok, "Accept": "application/json"},
                              json={"cod_estudio": "5081", "any_anyaca": ANYO}))
# ¿Está vetado el host de las guías?
guia_bloqueada = False
try:
    http._rules_for("https://campusvirtual.upct.es").can_fetch(GUIA) or (_ for _ in ()).throw(RobotsBlocked("veto"))
except RobotsBlocked:
    guia_bloqueada = True

entries, fuera = [], []
for sec in ("planes", "optativas"):
    for curso, rows in d[sec].items():
        for a in rows:
            if a["estado"] != "V":  # 'N' = no vigente / sin docencia en el curso
                fuera.append(a["ass_codnum"])
                continue
            nombre = a["nombre"].strip().capitalize()
            if a["cod_tipo"].startswith("O"):
                car = "optativa"
            elif "TRABAJO FIN DE GRADO" in a["nombre"].upper():
                car = "tfg"
            elif int(curso) == 1:
                car = "formacion_basica"
            else:
                car = "obligatoria"
            dur = a["dur"]
            sem = {"C1": 1, "C2": 2}.get(dur)
            entries.append(CatalogEntry(
                universidad=UNI, nombre_grado=GRADO, codigo_asignatura=a["ass_codnum"], nombre_asignatura=nombre,
                curso_semestre=f"Curso {curso} / " + {"C1": "Cuatrimestre 1", "C2": "Cuatrimestre 2", "A": "Anual", "I": "Intercambio"}.get(dur, dur),
                curso=int(curso), semestre=(int(curso) - 1) * 2 + sem if sem else None, creditos_ects=float(a["credects"]), caracter=car,
                idioma_pagina="es", url_guia_docente=GUIA.format(a=a["ultimaGuia"] or ANYO, c=a["ass_codnum"]), tipo_fuente="pdf"))
assert len({e.codigo_asignatura for e in entries}) == len(entries), "duplicados"
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
assert s["formacion_basica"] == 60 and s["tfg"] == 12 and s["obligatoria"] == 138, s
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico=ANYO, url_plan_estudios=PLAN_URL, ects_totales_plan=240.0,
    estrategia_fuente="API interna de estudios.upct.es (POST /obtenerPlan con token CSRF) -> plan por cursos y optativas con código, ECTS y cuatrimestre.",
    generado_por="discover_es_politecnica_cartagena.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
    estado="parcial" if guia_bloqueada else "ok",
    notas=(f"{len(entries)} asignaturas vigentes (excluidas {len(fuera)} con estado 'N', sin docencia en 2026-27). ECTS por carácter {json.dumps(s)}: básica 60, obligatorias 138 y TFG 12 = RUCT (60/138/30/12); "
           f"se ofertan {s['optativa']:g} ECTS optativos (RUCT 30). Carácter inferido de cod_tipo: O* = optativa; el resto, básica en 1.º y obligatoria en 2.º-4.º (validado por la suma). "
           f"PARCIAL: las guías están en campusvirtual.upct.es (UXXI), vetado por robots.txt; la web de la escuela industriales.upct.es/guia-docente también. No se descarga nada de esos hosts; sin Fase 2. "
           f"Las URLs de guía son informativas."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, "bloqueada:", guia_bloqueada, http.stats)
