"""Fase 1 - Le Havre Normandie Universite - Licence Sciences pour l'Ingenieur, parcours Mecanique (L3).
Fuente: Syllabus L3 Mecanique (PDF, UFR ST) enlazado desde la ficha de la formacion. L1-L2 no tienen syllabus publico.
Uso: python universidades/ec_f_le_havr11/discover_ec_f_le_havr11.py
"""
from __future__ import annotations
import io, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_le_havr11"
UNI = "Le Havre Normandie Université"
GRADO = "Licence Sciences pour l'Ingénieur - parcours Mécanique (L3)"
URL_PLAN = "https://www.univ-lehavre.fr/fr/formations/licence-sciences-pour-lingenieur-mecanique/"
PDF = "https://www.univ-lehavre.fr/wp-content/uploads/2023/07/UFR-ST-L3-Mecanique-Syllabus.pdf"


def slug(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def get_pages(client: PoliteClient) -> list[str]:
    r = pypdf.PdfReader(io.BytesIO(client.get_bytes(PDF)))
    return [p.extract_text() or "" for p in r.pages]


def segments(pages: list[str]) -> list[dict]:
    """Una UE = linea corta seguida de una linea que empieza por 'OBJECTIFS'. Devuelve nombre, semestre, pagina, lineas."""
    lines = []  # (page_no, semestre, texto)
    sem = None
    for pn, t in enumerate(pages, 1):
        for l in t.split("\n"):
            m = re.match(r"Semestre (\d)", l.strip())
            if m:
                sem = int(m.group(1))
            lines.append((pn, sem, l.rstrip()))
    # normaliza: "Titulo OBJECTIFS ..." en una sola linea -> dos lineas; titulo partido en dos lineas (parentesis sin cerrar) -> una
    norm = []
    for pn, sm, l in lines:
        m = re.match(r"^(\S[^:]{2,50}?)\s+(OBJECTIFS.*)$", l)
        if m and not l.upper().startswith("OBJECTIFS"):
            norm += [(pn, sm, m.group(1)), (pn, sm, m.group(2))]
        else:
            norm.append((pn, sm, l))
    lines = norm
    for i in range(1, len(lines)):
        if lines[i][2].count(")") > lines[i][2].count("(") and lines[i - 1][2].count("(") > lines[i - 1][2].count(")"):
            lines[i] = (lines[i][0], lines[i][1], lines[i - 1][2].strip() + " " + lines[i][2].strip())
            lines[i - 1] = (lines[i - 1][0], lines[i - 1][1], "")
    heads = [i for i in range(len(lines) - 1)
             if lines[i + 1][2].lstrip().upper().startswith("OBJECTIFS") and lines[i][2].strip()
             and not lines[i][2].lstrip().upper().startswith("OBJECTIFS") and len(lines[i][2]) < 90]
    out = []
    for k, i in enumerate(heads):
        j = heads[k + 1] if k + 1 < len(heads) else len(lines)
        body = [x[2] for x in lines[i + 1:j]]
        out.append(dict(name=lines[i][2].strip(), sem=lines[i][1], page=lines[i][0], page_end=lines[j - 1][0], body=body))
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    pages = get_pages(c)
    entries, seen = [], set()
    for s in segments(pages):
        code = f"L3-S{s['sem']}-" + slug(s["name"])
        if code in seen:
            continue
        seen.add(code)
        ects = None
        for l in s["body"]:
            m = re.match(r"^\s*(\d{1,2})\s+\d+\s+(?:\d+|1/\d)", l)
            if m and int(m.group(1)) <= 12:
                ects = float(m.group(1)); break
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=s["name"],
            curso_semestre=f"L3 / Semestre {s['sem']}", curso=3, semestre=s["sem"], creditos_ects=ects, caracter="obligatoria",
            idioma_pagina="fr", url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{s['page']}-{s['page_end']}"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0, estrategia_fuente="Syllabus L3 Mecanique (PDF compartido, UFR ST) parseado con pypdf",
        generado_por="discover_ec_f_le_havr11.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: Licence Sciences pour l'Ingénieur parcours Mécanique (180 ECTS, 3 años), la más afín a Grado en Ingeniería de "
               "Tecnologías Industriales (4 plazas en el Excel). PARCIAL: el único syllabus público con descriptivos por UE es el de L3 (S5-S6); "
               "L1-L2 solo tienen un esquema de maquette (nombres de UE sin descriptivo) y no se incluyen. Las UE de L3 suman menos de 60 ECTS porque "
               "parte son UE de personalización/preprofesionalización sin descriptivo. Cada descriptivo es breve: objetivos de aprendizaje, "
               "prerrequisitos, bibliografía y reparto de evaluación (coeficientes CC/parcial/examen) en una fila de números. Idioma: francés "
               "(UE de inglés incluidas). robots.txt de univ-lehavre.fr permite el acceso."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS", sum(e.creditos_ects or 0 for e in entries))


if __name__ == "__main__":
    main()
