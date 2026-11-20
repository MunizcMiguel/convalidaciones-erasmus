#!/usr/bin/env python3
"""Fase 1 — Universidad de Almería, Grado en Ingeniería Mecánica (Plan 2010, ESI).

Fuente: API JSON pública que alimenta la web del plan (campus.ual.es/ual/api/estudios/asignaturas/asignaturas/2910/es).
Guía: PDF por asignatura en www.ual.es/guia_academica/{cod_ass}/{curso}/CAS.
Uso: python universidades/es_almeria/discover_es_almeria.py
"""
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "es_almeria", "Universidad de Almería"
GRADO = "Grado en Ingeniería Mecánica (Plan 2010)"
API = "https://campus.ual.es/ual/api/estudios/asignaturas/asignaturas/2910/es"
PLAN_URL = "https://www.ual.es/estudios/grados/presentacion/plandeestudios/2910"
RUCT = {"basica": 60, "obligatorios": 150, "optativos": 6, "practicas": 12, "tfg": 12, "total": 240}
CAR = {"T": "formacion_basica", "B": "obligatoria", "B/O": "optativa", "E": "practicas", "P": "tfg"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
data = http.get_json(API)
curso = data["anyaca_actual"]
rows = [a for a in data["asignaturas"] if a["estadoass"] == "V"]
excl = [a for a in data["asignaturas"] if a["estadoass"] != "V"]
entries = []
for a in rows:
    cod = str(a["cod_ass"])
    cu = int(str(a["cod_curso"])[0])
    dur = a["cod_duracion"]
    sem = {"1Q": 1, "2Q": 2}.get(dur)
    sem_abs = (cu - 1) * 2 + sem if sem else None
    entries.append(CatalogEntry(
        universidad=UNI, nombre_grado=GRADO, codigo_asignatura=cod, nombre_asignatura=a["nom_ass"].strip(),
        curso_semestre=f"Curso {cu} / {dur}", curso=cu, semestre=sem_abs, creditos_ects=float(a["cred_ects"]),
        caracter=CAR[a["cod_caracter"]], idioma_pagina="es",
        url_guia_docente=f"https://www.ual.es/guia_academica/{cod}/{curso}/CAS", tipo_fuente="pdf"
    ))
assert len({e.codigo_asignatura for e in entries}) == len(entries)
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
assert s["formacion_basica"] == 60 and s["obligatoria"] == 144 and s["tfg"] == 12 and s["practicas"] == 12, s
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico=curso, url_plan_estudios=PLAN_URL,
    ects_totales_plan=240.0,
    estrategia_fuente="API JSON del portal (campus.ual.es/ual/api/estudios, la que consume la web AngularJS del plan); guía = PDF por asignatura.",
    generado_por="discover_es_almeria.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"Único centro: Escuela Superior de Ingeniería. {len(entries)} asignaturas vigentes (estadoass=V) de {len(data['asignaturas'])} "
           f"devueltas; excluidas {len(excl)} extinguidas/solo examen. ECTS ofertados por carácter: {json.dumps(s)}. "
           f"Básica 60, obligatorias 144 y TFG 12 coinciden con el plan; prácticas externas 12 (el RUCT las cuenta aparte: 12). "
           f"RUCT: obligatorias 150 + optativas 6 = 156; aquí obligatorias 144 + 36 ECTS 'B/O' (Optativa/Obligatoria, itinerario "
           f"de electrónica; se cursan 12) = 156 -> 144+12 = 156 coincide. 'B/O' se marca 'optativa'. "
           f"Curso/semestre: 1Q/2Q = cuatrimestres. Año {curso} (el actual de la API)."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, http.stats)
