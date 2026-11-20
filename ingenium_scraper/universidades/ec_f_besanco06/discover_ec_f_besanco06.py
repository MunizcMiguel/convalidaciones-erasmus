#!/usr/bin/env python3
"""Fase 1 — SUPMICROTECH-ENSMM (Besançon), diplôme d'ingénieur (spécialité Mécanique): único público = cycle ingénieur.
Fuente: PDF compartido "Programme de Formation 2025-2026" (el más reciente publicado en www.supmicrotech.fr, robots permite).
Cada módulo: cabecera 'CODE : TITRE (Nh)' + tabla 'Responsable Total CM TD TP AA Conf ECTS'. Se catalogan 1.º y 2.º año (págs. 5-27);
el 3.er año (opciones, págs. 28-72) tiene maquetación irregular y se deja fuera.
Uso: python universidades/ec_f_besanco06/discover_ec_f_besanco06.py"""
import io, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber
from common.http_client import PoliteClient
from common.schema import Catalog, CatalogEntry, CatalogMeta

HERE = Path(__file__).parent
SLUG, UNI = "ec_f_besanco06", "SUPMICROTECH-ENSMM (École Nationale Supérieure de Mécanique et des Microtechniques), Besançon"
GRADO = "Diplôme d'ingénieur ENSMM (cycle ingénieur, spécialité Mécanique) — 1.er y 2.º año"
PDF = "https://www.supmicrotech.fr/sites/default/files/public/CONTENT/DOCUMENTS/Programme%20de%20Formation%20Initiale%202025-2026%20vf.pdf"
FIRST, LAST = 5, 27
HEAD = re.compile(r"^([A-Z][A-Z0-9]{1,8}) ?: ?(.*?) ?\((\d+(?:,\d+)?) ?h\)$")
SECTIONS = [(5, "1ère année : Semestre BLEU", 1, 1), (11, "1ère année : Semestre JAUNE", 1, 2), (17, "2ème année : Tronc commun", 2, 3),
            (19, "2ème année : Parcours Ingénierie des Systèmes", 2, 3), (23, "2ème année : Parcours Ingénierie des Produits", 2, 3)]

http = PoliteClient(cache_dir=HERE / "raw_cache")
pdf = pdfplumber.open(io.BytesIO(http.get_bytes(PDF)))
lines = []
for i in range(FIRST - 1, LAST):
    for l in (pdf.pages[i].extract_text() or "").split("\n"):
        lines.append((i + 1, l))
heads = [k for k, (_, l) in enumerate(lines) if HEAD.match(l)]
entries, seen = [], {}
for n, k in enumerate(heads):
    pg, l = lines[k]
    code, title, hours = HEAD.match(l).groups()
    title = title or code  # cabecera sin intitulado en la fuente (p. ej. SHS1)
    end = heads[n + 1] if n + 1 < len(heads) else len(lines)
    pg_end = lines[end - 1][0]
    ects = None
    for _, t in lines[k + 1:k + 5]:
        m = re.search(r"(?:^|\s)(\d+)\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)$", t)
        if m:
            ects = float(m.group(2)); break
    sec = [s for s in SECTIONS if s[0] <= pg][-1]
    key = code
    if key in seen:  # mismo código en otro parcours
        key = f"{code}-{re.sub(r'[^A-Za-z]', '', sec[1].split(':')[-1])[:12]}"
    seen[key] = 1
    entries.append(CatalogEntry(universidad=UNI, nombre_grado=GRADO, codigo_asignatura=key, nombre_asignatura=title.strip().capitalize() if title.isupper() else title.strip(),
        curso_semestre=f"{sec[1]} (Curso {sec[2]} / Semestre {sec[3]}) · {hours} h", curso=sec[2], semestre=sec[3], creditos_ects=ects,
        caracter=None, idioma_pagina="fr", url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{pg}-{pg_end}"))
assert len({e.codigo_asignatura for e in entries}) == len(entries)
sin_ects = [e.codigo_asignatura for e in entries if e.creditos_ects is None]
meta = CatalogMeta(universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=PDF, ects_totales_plan=None,
    estrategia_fuente="PDF compartido 'Programme de Formation 2025-2026' (pdfplumber); cabecera de módulo + tabla de horas/ECTS.",
    generado_por="discover_ec_f_besanco06.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
    notas=(f"ENSMM solo ofrece cycle ingénieur (3 años tras CPGE/L3; no hay Licence). {len(entries)} módulos de 1.º y 2.º año (págs {FIRST}-{LAST}). "
           "PARCIAL: (1) programa 2025-26 (publicado en www.supmicrotech.fr/fr/formation-initiale); (2) el 3.er año (tronc commun + 8 opciones UEOBMS/CROC/IMM/ISP/MAS/MIND/MSF/SMR, págs 28-72) no se cataloga: está organizado por UE de opción con maquetación irregular, sin cabecera 'CODE : TITRE (Nh)' homogénea; "
           "(3) los parcours Systèmes y Produits de 2.º año comparten semestre 3, por eso las filas de ambos tienen semestre 3. "
           f"Sin ECTS leído: {', '.join(sin_ects) or 'ninguno'}. Se eliminan los nombres de responsables/intervenientes."))
cat = Catalog(meta=meta, asignaturas=entries)
(HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
print(len(entries), "sin ECTS:", sin_ects)
for e in entries: print(e.codigo_asignatura, e.nombre_asignatura[:40], e.creditos_ects, e.paginas_pdf)
