#!/usr/bin/env python3
"""Fase 1 — Universidad de Cádiz, Grado en Ingeniería Mecánica (Escuela Superior de Ingeniería, Puerto Real/Cádiz).

Fuente: página "Asignaturas del Grado en Ingeniería Mecánica" de la ESI (esingenieria.uca.es, WordPress): tablas por curso
(CÓDIGO | ASIGNATURA | SEMESTRE | CRÉDITOS | tipo FB/OB/OP/TFG) más 4 tablas de optativas por itinerario; cada código enlaza
a la guía en asignaturas.uca.es/{curso}/{codigo}.
Uso: python universidades/es_cadiz/discover_es_cadiz.py
"""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG, UNI = "es_cadiz", "Universidad de Cádiz"
GRADO = "Grado en Ingeniería Mecánica"
URL = "https://esingenieria.uca.es/docencia/grados/gim/asignaturas/"
CAR = {"FB": "formacion_basica", "OB": "obligatoria", "OP": "optativa", "TFG": "tfg"}

http = PoliteClient(cache_dir=HERE / "raw_cache")
soup = BeautifulSoup(http.get_text(URL), "lxml")
entries, dup = [], []
for table in soup.find_all("table"):
    rows = table.find_all("tr")
    heads = [c.get_text(" ", strip=True) for c in rows[0].find_all(["td", "th"])]
    if not heads or heads[0] != "CÓDIGO":
        continue
    prev = table.find_previous(["h2", "h3", "h4"])
    grupo = prev.get_text(" ", strip=True) if prev else ""
    for tr in rows[1:]:
        tds = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(tds) < 5 or not re.fullmatch(r"\d{8}", tds[0]):
            continue
        code, nombre, sem, cred, tipo = tds[:5]
        if code in {e.codigo_asignatura for e in entries}:
            dup.append(code)
            continue
        a = tr.find("a", href=True)
        sem = int(sem)
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=nombre,
            curso_semestre=f"Curso {(sem + 1) // 2} / Semestre {sem}" + (f" ({grupo})" if "Itinerario" in grupo else ""),
            curso=(sem + 1) // 2, semestre=sem, creditos_ects=float(cred.replace(",", ".")), caracter=CAR[tipo],
            idioma_pagina="es", url_guia_docente=a["href"] if a else None, tipo_fuente="html" if a else "sin_guia"))

assert len({e.codigo_asignatura for e in entries}) == len(entries)
s = {}
for e in entries:
    s[e.caracter] = s.get(e.caracter, 0) + e.creditos_ects
assert s["formacion_basica"] + s["obligatoria"] == 186 and s["tfg"] == 18, s  # 66+120 vs RUCT 60+126
sin = [e.codigo_asignatura for e in entries if not e.url_guia_docente]
meta = CatalogMeta(
    universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL,
    ects_totales_plan=240.0,
    estrategia_fuente="HTML de esingenieria.uca.es (tablas por curso e itinerario); guía = HTML en asignaturas.uca.es.",
    generado_por="discover_es_cadiz.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"Centro: Escuela Superior de Ingeniería (el RUCT cita también la ETS de Ingeniería de Algeciras; no incluida). "
           f"{len(entries)} asignaturas. ECTS ofertados {json.dumps(s)}: básica+obligatorias = 186 y TFG 18 coinciden con el RUCT (60+126+18), "
           f"pero la web reparte 66 FB y 120 OB (una asignatura de 6 ECTS figura como FB en la web y como obligatoria en el RUCT); se ofertan {s['optativa']:g} ECTS optativos en 4 itinerarios (Diseño de Máquinas, Estructuras, Fabricación, "
           f"Multidisciplinar) y se cursan 36 (RUCT 36). Total cursado 60+126+36+18=240. Duplicados entre itinerarios: "
           f"{', '.join(dup) or 'ninguno'}. Sin guía: {', '.join(sin) or 'ninguna'}."),
)
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), s, "dup:", dup, "sin guía:", sin, http.stats)
