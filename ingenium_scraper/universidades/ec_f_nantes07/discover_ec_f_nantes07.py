#!/usr/bin/env python3
"""Fase 1 — École Centrale de Nantes, cycle ingénieur (spécialité Mécanique, formación por apprentissage), años 1-3.
Fuente: 3 PDF 'Programme ingénieur, spécialité Mécanique 2025-2026' (EI1, EI2, EI3; www.ec-nantes.fr, robots permite): cada curso = una o varias páginas
que empiezan por 'INGÉNIEUR, SPÉCIALITÉ MÉCANIQUE / {n}e année - UEnnn / Título [ACRÓNIMO]'. paginas_pdf derivado por el script.
Uso: python universidades/ec_f_nantes07/discover_ec_f_nantes07.py"""
import io, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "ec_f_nantes07", "École Centrale de Nantes"
GRADO = "Diplôme d'ingénieur Centrale Nantes, spécialité Mécanique (apprentissage)"
PDFS = {y: f"https://www.ec-nantes.fr/ingenieur-de-specialite/mecanique/syllabus-ei{y}-spe-meca" for y in (1, 2, 3)}
START = re.compile(r"^INGÉNIEUR, SPÉCIALITÉ MÉCANIQUE$")

http = PoliteClient(cache_dir=HERE / "raw_cache")
entries, seen = [], {}
for y, url in PDFS.items():
    pdf = pdfplumber.open(io.BytesIO(http.get_bytes(url)))
    texts = [(pg.extract_text() or "").split("\n") for pg in pdf.pages]
    # créditos de UE (tabla resumen)
    ue_cred = {}
    for L in texts[:3]:
        for i, l in enumerate(L):
            m = re.match(r"^(UE\d{3}) (\d+)$", l)
            if m:
                ue_cred[m.group(1)] = float(m.group(2))
    starts = [i for i, L in enumerate(texts) if len(L) > 2 and START.match(L[0]) and re.match(r"^\S+ année - UE\d{3}$", L[1])]
    for n, i in enumerate(starts):
        end = (starts[n + 1] if n + 1 < len(starts) else len(texts)) - 1
        ue = L = texts[i][1].split("- ")[1]
        title_line = texts[i][2]
        j = 3
        while not re.search(r"\[[A-Z0-9_]+\]$", title_line) and j < 5:
            title_line += " " + texts[i][j]; j += 1
        m = re.match(r"^(.*?) \[([A-Z0-9_]+)\]$", title_line.strip())
        title, code = (m.group(1), m.group(2)) if m else (title_line.strip(), f"{ue}_{n}")
        if code in seen:
            code = f"{code}_{ue}"
        seen[code] = 1
        blob = "\n".join(l for k in range(i, end + 1) for l in texts[k])
        mm = re.search(r"Fran[cç]ais|Anglais|English", blob.split("LANGUE DU COURS")[-1][:200]) if "LANGUE DU COURS" in blob else None
        idioma = "en" if mm and mm.group(0) in ("Anglais", "English") else "fr"
        ects = None
        t = blob.split("LANGUE DU COURS")[-1] if "LANGUE DU COURS" in blob else ""
        cm = re.search(r"(?:Fran[cç]ais|Anglais|English)\s+(\d+(?:[.,]\d+)?)\s+\d+ hrs", t)
        if cm:
            ects = float(cm.group(1).replace(",", "."))
        entries.append(CatalogEntry(universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
            curso_semestre=f"Año {y} (EI{y}) · {ue} (UE de {ue_cred.get(ue, '?'):g} ECTS en total)" if ue in ue_cred else f"Año {y} (EI{y}) · {ue}",
            curso=y, semestre=None, creditos_ects=ects, caracter="practicas" if "ENTRE" in code or "PFE" in code else ("optativa" if "option" in blob[:600].lower() else None),
            idioma_pagina=idioma, url_guia_docente=url, tipo_fuente="pdf_compartido", paginas_pdf=f"{i + 1}-{end + 1}"))
from collections import Counter
_ue = lambda e: re.search(r"(UE\d{3})", e.curso_semestre).group(1) + f"-{e.curso}"
_cnt = Counter(_ue(e) for e in entries)
for k, e in enumerate(entries):
    m = re.search(r"UE de (\d+) ECTS", e.curso_semestre)
    if e.creditos_ects is None and m and _cnt[_ue(e)] == 1:
        entries[k] = e.model_copy(update={"creditos_ects": float(m.group(1))})
assert len({e.codigo_asignatura for e in entries}) == len(entries)
meta = CatalogMeta(universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=PDFS[1], ects_totales_plan=None,
    estrategia_fuente="3 PDF de programa (EI1-EI3) con una ficha por curso (pdfplumber).", generado_por="discover_ec_f_nantes07.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
    notas=(f"Centrale Nantes: solo cycle ingénieur (3 años, no hay Licence/Bachelor equivalente examinado); se toma la spécialité Mécanique (apprentissage, FISA), 1.º-3.er año. {len(entries)} cursos. "
           "Los créditos ECTS se dan a nivel de UE (varios cursos por UE): creditos_ects solo se rellena si la ficha del curso lo trae (suele ser '-') o si la UE tiene un único curso; el total de UE aparece en curso_semestre. "
           "EI3 incluye opciones (Conception, Simulation et Dimensionnement / Usine du Futur). Sin semestre en la fuente."))
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), http.stats)
for e in entries[:6] + entries[-3:]: print(e.curso, e.creditos_ects, e.codigo_asignatura, e.nombre_asignatura[:40], e.paginas_pdf, e.idioma_pagina, e.curso_semestre)
