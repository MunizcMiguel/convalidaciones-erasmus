"""Fase 1 - Casimir Pulaski Radom University (UTH Rad), Faculty of Mechanical Engineering.
Grado: Mechanical Engineering, first-cycle (inzynier), full-time, docencia en ingles, plan 2025/2026.
Fuente: plan de estudios PDF + ZIP de syllabus PDF (uno por asignatura) publicados en wm.uniwersytetradom.pl/programy-studiow/.
Los dominios de la ficha Erasmus (erasmus.ujep.cz, checo) y uthrad.pl (certificado TLS invalido) NO sirven; el sitio real es uniwersytetradom.pl.
Uso: python universidades/ec_pl_radom01/discover_ec_pl_radom01.py
"""
from __future__ import annotations

import io
import json
import math
import re
import sys
import time
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_radom01"
UNIVERSIDAD = "Casimir Pulaski Radom University (UTH Rad) - Faculty of Mechanical Engineering"
GRADO = "Mechanical Engineering (first-cycle, full-time, English)"
BASE = "https://wm.uniwersytetradom.pl/wp-content/uploads/sites/18/2025/05/"
URL_PLAN = BASE + "Plan-studiow-2025-2026-ME-I-st.pdf"
URL_ZIP = BASE + "Syllabusy-2025-2026-ME-I.zip"
URL_PROG = "https://wm.uniwersytetradom.pl/programy-studiow/"
ROMAN = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7}


def member_map(zf: zipfile.ZipFile) -> dict[str, str]:
    out = {}
    for n in zf.namelist():
        if n.endswith(".pdf") and "/Full - time studies/" in n:
            out[Path(n).name.split("_")[0]] = n
    return out


def syl_info(zf: zipfile.ZipFile, member: str) -> dict:
    with pdfplumber.open(io.BytesIO(zf.read(member))) as pdf:
        t = "\n".join(p.extract_text(x_tolerance=1.5) or "" for p in pdf.pages)
    m = re.search(r"Semester\(s\)\s+([IVX0-9, ]+)", t)
    sems = []
    if m:
        for x in re.split(r"[,\s]+", m.group(1).strip()):
            if x:
                sems.append(ROMAN.get(x) or int(x))
    e = re.search(r"ECTS points per subject\s+([\d.]+)", t)
    lang = re.search(r"Language of instruction\s+(\w+)", t)
    eng = re.search(r"ME/O/I/ST/\S+\s+(?:o\s+)?C\s+(.+)", t)
    return {"sems": sems, "ects": float(e.group(1)) if e else None, "lang": lang.group(1) if lang else "",
            "name_syl": eng.group(1).strip() if eng else None}


def parse_plan(text: str):
    """(grupo, n, nombre) de cada fila del plan; el nombre termina en el primer token numerico."""
    group, rows = None, []
    for line in text.splitlines():
        g = re.match(r"^(A|B|C|F|G)\s?\.\s*Group|^(D\s?[12])\.\s*Group|^(E\s?[12])\.\s*Group|^(H)\s?\.\s*Group", line)
        if g:
            group = next(x for x in g.groups() if x).replace(" ", "")
            continue
        if line.startswith("SUM A+B"):
            break  # lo que sigue son leyendas y otras tablas
        if line.startswith("Sum of group"):
            continue
        m = re.match(r"^(\d+)(?:\s+|(?=[A-Za-z]))([A-Za-z0-9][^\n]*)$", line)
        if m and group:
            toks = m.group(2).split()
            i = next((k for k, tk in enumerate(toks) if re.fullmatch(r"[\d.,]+", tk)), len(toks))
            rest = toks[i:]
            while rest and re.fullmatch(r"[1-7]([.,][1-7])*", rest[0]):
                rest = rest[1:]  # semestres de examen / credito
            nums = [float(x.replace(",", ".")) for x in rest[:8] if re.fullmatch(r"[\d.]+", x)]
            plan_ects = nums[7] if len(nums) >= 8 else None  # horas, L, C, Lab, P, S, trabajo total, ECTS
            rows.append((group, int(m.group(1)), " ".join(toks[:i]), plan_ects))
    return rows


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    with pdfplumber.open(c.get_file(URL_PLAN)) as pdf:
        plan = "\n".join(p.extract_text() or "" for p in pdf.pages)
    zf = zipfile.ZipFile(c.get_file(URL_ZIP))
    mm = member_map(zf)
    entries, skipped, ects_fix = [], [], []
    for grp, n, name, plan_ects in parse_plan(plan):
        if grp in ("A", "B"):
            keys = [f"{grp}{n}"]
        elif grp == "C":
            keys = [f"C{n}a", f"C{n}b"] if f"C{n}a" in mm else [f"C{n}"]
        elif grp in ("D1", "D2", "E1"):
            keys = [grp]
        elif grp == "E2":
            keys = [f"E2{n}"]
        elif grp == "H":
            keys = [f"H.0{n}"]
        else:
            keys = []
        names = [x.strip() for x in name.split(" / ")] if grp == "C" and " / " in name else [name]
        for j, key in enumerate(keys):
            if key not in mm:
                skipped.append(key)
                continue
            info = syl_info(zf, mm[key])
            nm = names[j] if j < len(names) else names[0]
            if grp == "C" and info["name_syl"] and re.search(r"\b\w \w \w\b", nm):
                nm = info["name_syl"]  # texto del plan corrupto (superposicion en el PDF)
            sem = min(info["sems"]) if info["sems"] else None
            ects = info["ects"]
            if (ects is None or ects > 20 or (plan_ects is not None and ects != plan_ects and len(keys) == 1)) and plan_ects is not None:
                ects_fix.append(f"{key}: syllabus={info['ects']} plan={plan_ects}")
                ects = plan_ects
            carac = {"A": "obligatoria", "B": "obligatoria", "C": "optativa", "D1": "obligatoria", "D2": "optativa",
                     "E1": "obligatoria", "E2": "optativa", "H": "obligatoria"}[grp]
            if grp == "H" and n == 2:
                carac = "tfg"
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=key.replace(".", ""), nombre_asignatura=nm,
                curso_semestre=("Semestres " + ", ".join(map(str, info["sems"]))) if sem else "no indicado",
                curso=math.ceil(sem / 2) if sem else None, semestre=sem, creditos_ects=ects, caracter=carac,
                idioma_pagina="en" if info["lang"].lower() == "english" else info["lang"][:2].lower(),
                url_guia_docente=f"{URL_ZIP}#{mm[key]}", tipo_fuente="pdf"))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes)), ("duplicados", sorted({x for x in codes if codes.count(x) > 1}))
    fixed = sum(e.creditos_ects or 0 for e in entries if not e.codigo_asignatura.startswith("C"))
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025/2026", url_plan_estudios=URL_PROG,
        ects_totales_plan=210.0,
        estrategia_fuente="Plan de estudios PDF (nombres de las filas) + ZIP de syllabus PDF por asignatura (curso/semestre/ECTS/idioma leidos de cada syllabus)",
        generado_por="discover_ec_pl_radom01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Titulación: Mechanical Engineering (1.er ciclo, inżynier, 7 semestres, 210 ECTS, perfil general académico, docencia en inglés), Facultad de Ingeniería Mecánica; "
               "es el grado equivalente (la facultad ofrece además Mechanika i Budowa Maszyn, versión polaca). Solo modalidad full-time (la part-time tiene su propio plan). "
               "Los 9 bloques del grupo C (optativas) son pares 'A / B' del plan y se catalogan como dos filas C{n}a / C{n}b (opciones alternativas), por lo que la suma de ECTS de las filas excede 210. "
               f"Curso = ceil(semestre mínimo del syllabus / 2). Un syllabus por asignatura dentro de un ZIP (url_guia_docente = ZIP#miembro). Plan sin fichero: {skipped or 'ninguno'}; "
               f"F (prácticas, 0 ECTS en el plan) no se cataloga. Suma de ECTS de las filas no-C: {fixed:g}. "
               f"ECTS: del syllabus; si falta o contradice el plan se usa el del plan ({ects_fix or 'ningún caso'}). Syllabus de lengua extranjera E21 en alemán. "
               "Hints descartados: erasmus.ujep.cz (República Checa) y uthrad.pl (certificado TLS inválido)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS no-C", fixed, "total", sum(e.creditos_ects or 0 for e in entries), "sin fichero", skipped)
    for e in entries:
        print(e.codigo_asignatura, e.curso, e.semestre, e.creditos_ects, e.caracter, e.nombre_asignatura[:60])


if __name__ == "__main__":
    main()
