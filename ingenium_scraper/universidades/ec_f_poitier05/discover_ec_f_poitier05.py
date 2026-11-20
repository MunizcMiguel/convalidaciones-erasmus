"""Fase 1 - ISAE-ENSMA (Poitiers) - Diplome d'ingenieur FISE, 2e annee (Syllabus A2 2025/26, PDF bilingue FR/EN).
Uso: python universidades/ec_f_poitier05/discover_ec_f_poitier05.py
"""
from __future__ import annotations
import io, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_poitier05"
UNI = "ISAE-ENSMA (École nationale supérieure de mécanique et d'aérotechnique), Poitiers"
GRADO = "Diplôme d'ingénieur ISAE-ENSMA (FISE) - 2e année (syllabus A2)"
URL_PLAN = "https://www.ensma.fr/formation-ingenieur-statut-etudiant/enseignement/"
PDF = "https://ensma.fr/wp-content/uploads/2025/02/Syllabus-FISE-ENSMA-A2-2025-2026-previsionnel.pdf"


def get_pages(client: PoliteClient) -> list[str]:
    r = pypdf.PdfReader(io.BytesIO(client.get_bytes(PDF)))
    return [p.extract_text() or "" for p in r.pages]


def sheets(pages: list[str]) -> list[dict]:
    starts = [i for i, t in enumerate(pages) if "Code ECUE" in t]
    out = []
    for k, s in enumerate(starts):
        end = (starts[k + 1] - 1) if k + 1 < len(starts) else len(pages) - 1
        t = pages[s]
        head, _, _ = t.partition("Code ECUE")
        hl = [l.strip() for l in head.split("\n") if l.strip()]
        # la ficha empieza tras el contenido de la pagina previa si la hoja comparte pagina: tomamos las 2 ultimas lineas (FR / EN)
        names = hl[-2:] if len(hl) >= 2 else hl
        m = re.search(r"Course code:\s*(\S+)\s+UE \(Cr[^)]*\)\s*:\s*(UE[\w-]+)\s*\((\d+)\s*ECTS\)", t) or \
            re.search(r"Course code:\s*(\S+)", t)
        if not m:
            continue
        sem = re.search(r":\s*(\d)\S*\s+(?:semestre|trimestre)", t)
        typ = re.search(r"Type de cours[\s\S]*?:\s*([^\n]+)", t)
        out.append(dict(code=m.group(1), name=names[0], name_en=names[-1], ue=m.group(2) if m.lastindex and m.lastindex >= 3 else None,
                        ue_ects=float(m.group(3)) if m.lastindex and m.lastindex >= 3 else None,
                        sem=int(sem.group(1)) if sem else None, ue_raw=m.group(2) if m.lastindex and m.lastindex >= 3 else None, typ=typ.group(1).strip() if typ else "",
                        ini=s + 1, fin=end + 1))
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    pages = get_pages(c)
    entries, seen = [], set()
    for s in sheets(pages):
        code = s["code"]
        if code in seen:
            code = f"{code}-{s['ue'] or s['ini']}"
        if code in seen:
            code = f"{code}-p{s['ini']}"
        seen.add(code)
        s["code"] = code
        sem = s["sem"] or (int(re.match(r"UE(\d)", s["ue"]).group(1)) if s["ue"] and re.match(r"UE\d", s["ue"]) else None)
        abs_sem = sem  # semestres 3-4 = 2.o curso del ciclo ingeniero (A2)
        car = "optativa" if re.search(r"Optionnel|Elective|Option", s["typ"], re.I) else "obligatoria"
        if s["ue"] and re.match(r"UE4-[23][abc]", s["ue"]):
            car = "optativa"  # majeure (itinerario a elegir)
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=s["code"],
            nombre_asignatura=f"{s['name']} / {s['name_en']}" if s["name_en"] != s["name"] else s["name"],
            curso_semestre=f"A2 / Semestre {sem} ({s['ue'] or 'UE ?'}, {s['ue_ects']:g} ECTS la UE)" if s["ue_ects"] else f"A2 / Semestre {sem}",
            curso=2, semestre=abs_sem, creditos_ects=None, caracter=car, idioma_pagina="fr",
            url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{s['ini']}-{s['fin']}"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, nivel="master", curso_academico="2025-26", url_plan_estudios=URL_PLAN,
        ects_totales_plan=None, estrategia_fuente="Syllabus A2 FISE 2025/26 (PDF compartido bilingue FR/EN) parseado con pypdf; una ficha por ECUE",
        generado_por="discover_ec_f_poitier05.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("ENSMA solo ofrece el diploma de ingeniero (ciclo de 5 años, sin grado de Mecánica separado); los destinos del Excel son de "
               "Máster Universitario en Ingeniería Industrial / Integridad y Durabilidad de Materiales (1+1 plazas), por lo que se toma el "
               "diploma FISE; es el único equivalente (2.º ciclo universitario según las fichas: 'Second cycle universitaire'). PARCIAL: solo se "
               "ha localizado el syllabus público de 2.ª año (A2, previsional 2025/26, 53 fichas); A1 y A3 (con especialidades) no tienen PDF "
               "localizado (el catálogo de cursos más antiguo es de 2016). Los ECTS se dan por UE (cabecera de la ficha), no por asignatura. "
               "Fichas bilingües FR/EN; se conserva el texto francés e inglés. Se omiten coordinadores/profesorado."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas")


if __name__ == "__main__":
    main()
