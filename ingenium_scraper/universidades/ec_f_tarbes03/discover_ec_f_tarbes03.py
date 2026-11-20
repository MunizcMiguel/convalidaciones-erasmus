#!/usr/bin/env python3
"""Fase 1 — ENIT (École Nationale d'Ingénieurs de Tarbes), Titre d'ingénieur (cycle ingénieur L3→M2, semestres 5-10, formación initiale).
Fuente: página 'Programme de formation ingénieurs' de enit.fr (robots permite): un PDF 'Syllabus Titre d'Ingénieur' por semestre
(IGENI-L3-S05/S06, IGENI-M-S07..S10) con una ficha por UE y por EC (elemento constitutivo). Catálogo = EC (y UE sin EC); paginas_pdf derivado.
No incluidos: semestres 1-4 (cycle préparatoire C1, bachelor) ni la vía apprentissage (IGENI-ALM-*).
Uso: python universidades/ec_f_tarbes03/discover_ec_f_tarbes03.py"""
import io, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "ec_f_tarbes03", "École Nationale d'Ingénieurs de Tarbes (ENIT, INP Toulouse), Tarbes"
GRADO = "Titre d'ingénieur ENIT (cycle ingénieur, semestres 5-10; orientación mecánica/producción)"
BASE = "https://www.enit.fr/_attachment/nouvel-article-75/"
PLAN = "https://www.enit.fr/fr/formations/diplome-d-ingenieur/je-me-forme/programme-formation-ingenieurs.html"
SEMS = [("L3-S05", 5), ("L3-S06", 6), ("M-S07", 7), ("M-S08", 8), ("M-S09", 9), ("M-S10", 10)]
http = PoliteClient(cache_dir=HERE / "raw_cache")


def txt(pg):
    return (pg.extract_text(x_tolerance=1.0, y_tolerance=3) or "").split("\n")


def field(lines, pat):
    for l in lines:
        m = re.match(pat, l)
        if m:
            return m.group(1).strip()


def name_of(L, kind):
    for i, l in enumerate(L):
        m = re.match(rf"^Nom ?de ?l.{kind} (.+)$", l)
        if m:
            return m.group(1).strip()
    for i, l in enumerate(L):
        if re.match(rf"^Pr[ée]sentation ?de ?l.{kind}", l) and i + 1 < len(L) and not L[i + 1].startswith("Nom"):
            return L[i + 1].strip()


entries, seen = [], {}
for fn, sem in SEMS:
    url = f"{BASE}IGENI-{fn}.pdf?download=true"
    pdf = pdfplumber.open(io.BytesIO(http.get_bytes(url)))
    pages = [txt(pg) for pg in pdf.pages]
    info = []  # (page_idx, kind, code, ue, name, ects)
    for i, L in enumerate(pages):
        head = L[1:6]
        ec = field(head, r"^Code ?EC (IGENI-\S+)")
        ue = field(head, r"^Code ?UE (IGENI-\S+)")
        if ec:
            info.append((i, "EC", ec, ue, name_of(L, "EC"), None))
        elif ue:
            info.append((i, "UE", ue, ue, name_of(L, "UE"), field(L, r"^Cr[ée]dits ?ECTS (\d+(?:[.,]\d+)?)")))
    ue_credit = {k[3]: float(k[5].replace(",", ".")) for k in info if k[1] == "UE" and k[5]}
    ue_name = {k[3]: k[4] for k in info if k[1] == "UE"}
    ecs_per_ue = {}
    for k in info:
        if k[1] == "EC":
            ecs_per_ue[k[3]] = ecs_per_ue.get(k[3], 0) + 1
    rows = [k for k in info if k[1] == "EC" or ecs_per_ue.get(k[3], 0) == 0]
    for n, k in enumerate(rows):
        nxt = [x for x in info if x[0] > k[0] and (x[1] == "EC" or x[3] != k[3] or k[1] == "UE")]
        end_idx = (nxt[0][0] if nxt else len(pages)) - 1
        # un EC termina antes de la siguiente página-ficha (EC o UE)
        after = [x[0] for x in info if x[0] > k[0]]
        end_idx = (after[0] if after else len(pages)) - 1
        code = k[2]
        if code in seen:
            code = f"{code}_{fn}"
        seen[code] = 1
        title = k[4] or code
        ects = ue_credit.get(k[3]) if (k[1] == "UE" or ecs_per_ue.get(k[3]) == 1) else None
        uen = ue_name.get(k[3]) or ""
        entries.append(CatalogEntry(universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title.title() if title.isupper() else title,
            curso_semestre=f"Curso {(sem + 1) // 2} / Semestre {sem} · {k[3]} {uen.title()} (UE de {ue_credit.get(k[3], '?')} ECTS)",
            curso=(sem + 1) // 2, semestre=sem, creditos_ects=ects, caracter=None, idioma_pagina="fr", url_guia_docente=url,
            tipo_fuente="pdf_compartido", paginas_pdf=f"{k[0] + 1}-{end_idx + 1}"))
assert len({e.codigo_asignatura for e in entries}) == len(entries)
meta = CatalogMeta(universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=PLAN, ects_totales_plan=None,
    estrategia_fuente="6 PDF 'Syllabus Titre d'Ingénieur' por semestre (pdfplumber x_tolerance=1.0): fichas EC/UE.", generado_por="discover_ec_f_tarbes03.py",
    generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas=(f"ENIT solo ofrece Titre d'ingénieur (generalista con orientación mecánica/producción) más un Bachelor SIEE (no mecánico); se cubren los semestres 5-10 de formación inicial ({len(entries)} EC/UE). "
           "PARCIAL: no se cubren S1-S4 (cycle préparatoire), la vía apprentissage (IGENI-ALM-*) ni el Bachelor; los PDF 2025-26 mezclan opciones/filières (sufijos GI, TC, TG), por lo que no hay un 'plan único'. "
           "ECTS a nivel de UE: creditos_ects solo si la UE tiene un único EC. Texto con artefactos de etiquetas rotadas (se filtran en la Fase 2)."))
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), http.stats)
for e in entries[:5] + entries[-3:]: print(e.semestre, e.creditos_ects, e.codigo_asignatura, e.nombre_asignatura[:40], e.paginas_pdf)
