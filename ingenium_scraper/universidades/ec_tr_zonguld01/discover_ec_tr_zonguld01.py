"""Fase 1 - Gazi University (Ankara), Faculty of Engineering: Mechanical Engineering (Eng) = Makine Muhendisligi (Ingilizce).
Plataforma: OBS "Bologna Bilgi Paketi" (Proliz) - obs.gazi.edu.tr/oibs/bologna/. El plan de cada programa (progCourses.aspx) es HTML estatico
con una tabla por semestre y enlaces `prolizOpenCourseDetails(id)` -> progCourseDetails.aspx?curCourse={id}.
Uso: python universidades/ec_tr_zonguld01/discover_ec_tr_zonguld01.py
"""
from __future__ import annotations

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
SLUG = "ec_tr_zonguld01"
UNIVERSIDAD = "Zonguldak Bülent Ecevit Üniversitesi (BEUN) - Faculty of Engineering"
GRADO = "Mechanical Engineering / Makine Mühendisliği (Normal Öğretim)"
BASE = "https://obs.beun.edu.tr/oibs/bologna/"
CUR_SUNIT = "38"
LANG = "en"
IDIOMA = "en"
NOTAS_EXTRA = ("Hint de la ficha Erasmus (erasmus.beun.edu.tr) = web Erasmus; el catálogo Bologna (OBP) está en obs.beun.edu.tr/oibs/bologna/ (mismo sistema OBS/Proliz que Gazi). "
               "Programa Mechanical Engineering (curSunit=38, diurno; hay también «Evening» 43, no usado). Currículo «2024 ve sonrası». Docencia en turco (instrucción 'Turkish'), "
               "pero título y texto de las fichas están en inglés en la interfaz inglesa del OBS (idioma de página = en).")


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    url_plan = f"{BASE}progCourses.aspx?lang={LANG}&curSunit={CUR_SUNIT}"
    h = c.get_text(url_plan)
    s = BeautifulSoup(h, "lxml")
    sel = s.find("select", attrs={"name": "cmbYillar"})
    cur = next((o.get_text(" ", strip=True) for o in sel.find_all("option") if o.get("selected")), "") if sel else ""
    entries, sem, seen, sem_tot, placeholders = [], None, set(), {}, []
    for tr in s.select("table tr"):
        tds = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        txt = " ".join(tds)
        m = re.search(r"(\d+)\.\s*Semester Course Plan|(\d+)\.\s*Yar[ıi]y[ıi]l", txt)
        if m and len([t for t in tds if t]) == 1:
            sem = int(m.group(1) or m.group(2))
            continue
        if "Total ECTS" in tds and sem:
            sem_tot[sem] = float(tds[tds.index("Total ECTS") + 1])
            continue
        a = tr.find("a", onclick=re.compile(r"prolizOpenCourseDetails"))
        if not a or not sem or len(tds) < 7:
            continue
        cid = re.search(r"prolizOpenCourseDetails\((\d+)\)", a["onclick"]).group(1)
        code, name, tpl, kind, ects, grp = tds[1], tds[2], tds[3], tds[4], tds[5], tds[6]
        if tpl.strip() == "-" and grp.strip():  # marcador de grupo electivo (p. ej. "SOCIAL ELECTIVE COURSE"), sin ficha
            placeholders.append(f"{code} ({name}, {ects} ECTS, S{sem})")
            continue
        key = code
        if key in seen:
            key = f"{code}-s{sem}"
        seen.add(key)
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=key, nombre_asignatura=name,
            curso_semestre=f"Curso {(sem + 1) // 2} / Semestre {sem}", curso=(sem + 1) // 2 if (sem + 1) // 2 <= 6 else None, semestre=sem,
            creditos_ects=float(ects), caracter="obligatoria" if kind.lower().startswith("comp") else "optativa",
            idioma_pagina=IDIOMA, url_guia_docente=f"{BASE}progCourseDetails.aspx?curCourse={cid}&lang={LANG}", tipo_fuente="html"))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    comp = sum(e.creditos_ects for e in entries if e.caracter == "obligatoria")
    el = sum(e.creditos_ects for e in entries if e.caracter == "optativa")
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2026/2027", url_plan_estudios=url_plan,
        ects_totales_plan=float(sum(sem_tot.values())) or None,
        estrategia_fuente="HTML del plan (progCourses.aspx, OBS Bologna/Proliz): una tabla por semestre; ficha por asignatura en progCourseDetails.aspx?curCourse={id}",
        generado_por=f"discover_{SLUG}.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Currículo mostrado por defecto: «{cur[:90]}». ECTS por semestre según el plan: {sem_tot} (total {sum(sem_tot.values()):g}). "
               f"Filas obligatorias {comp:g} ECTS + optativas ofertadas {el:g} ECTS (el alumno cursa solo una parte). Marcadores de grupo electivo sin ficha (no catalogados): {placeholders or 'ninguno'}. "
               f"Código = código de asignatura del plan (sufijo -sN si se repite). {NOTAS_EXTRA}"))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; comp", comp, "elec", el, "sem_tot", sem_tot, "| plan:", cur[:60], "| placeholders", placeholders)


if __name__ == "__main__":
    main()
