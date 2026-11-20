"""Fase 1 - ESIGELEC (Rouen) - Master of Technology Electronic Embedded Systems (EES), course outline 2025-26 (PDF en ingles).
Uso: python universidades/ec_f_rouen07/discover_ec_f_rouen07.py
"""
from __future__ import annotations
import io, json, re, sys, time, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_rouen07"
UNI = "ESIGELEC School of Engineering (Rouen)"
GRADO = "Master of Technology - Electronic Embedded Systems (EES)"
URL_PLAN = "https://en.esigelec.fr/courses/"
PDF = "https://en.vizzmedia.com/wp-content/uploads/2025/10/ESIGELEC-COURSE-OUTLINE-EES-2025-26.pdf"
MOD = re.compile(r"Module Code:\s*(\S+)\s+Duration:\s*([\d.,]+)\s*h", re.I)


def get_pages(client: PoliteClient) -> list[str]:
    r = pypdf.PdfReader(io.BytesIO(client.get_bytes(PDF)))
    return [unicodedata.normalize("NFC", p.extract_text() or "") for p in r.pages]


def modules(pages: list[str]) -> list[dict]:
    """Lineas con marca de pagina; cada modulo = linea de titulo + 'Module Code: X Duration: Nh' ... hasta el siguiente titulo."""
    lines = [(pn, l.rstrip()) for pn, t in enumerate(pages, 1) for l in t.split("\n")]
    idx = [i for i, (_, l) in enumerate(lines) if MOD.search(l)]
    out = []
    for k, i in enumerate(idx):
        # el titulo es la linea previa no vacia (puede ser el fin de la pagina anterior)
        j = i - 1
        while j >= 0 and (not lines[j][1].strip() or re.fullmatch(r"\s*\d+\s*", lines[j][1])):
            j -= 1
        title = lines[j][1].strip()
        # titulo partido en dos lineas? (la linea anterior sin punto y corta, con mayuscula y en minusculas siguientes) se deja tal cual
        nxt = idx[k + 1] if k + 1 < len(idx) else len(lines)
        # el titulo del siguiente modulo es su linea previa: se recorta
        end = nxt - 1
        while end > i and (not lines[end][1].strip() or re.fullmatch(r"\s*\d+\s*", lines[end][1])):
            end -= 1
        if k + 1 < len(idx):
            end -= 1  # titulo del siguiente
            while end > i and (not lines[end][1].strip() or re.fullmatch(r"\s*\d+\s*", lines[end][1])):
                end -= 1
        m = MOD.search(lines[i][1])
        out.append(dict(code=m.group(1), hours=float(m.group(2).replace(",", ".")), title=title,
                        body=[l for _, l in lines[i + 1:end + 1]], p0=lines[j][0], p1=lines[end][0]))
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    pages = get_pages(c)
    entries, seen = [], set()
    full = "\n".join(pages)
    for m in modules(pages):
        if m["code"] in seen:
            continue
        seen.add(m["code"])
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=m["code"], nombre_asignatura=m["title"],
            curso_semestre="Master of Technology (S1-S3, ver notas)", curso=None, semestre=None, creditos_ects=None, caracter="obligatoria",
            idioma_pagina="en", url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{m['p0']}-{m['p1']}"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, nivel="master", curso_academico="2025-26", url_plan_estudios=URL_PLAN,
        ects_totales_plan=None, estrategia_fuente="Course Outline EES 2025-26 (PDF compartido en ingles) parseado con pypdf; modulo = 'Module Code: X Duration: Nh'",
        generado_por="discover_ec_f_rouen07.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Destino ESIGELEC: Excel pide Grado Teleco y Grado Electrónica Industrial y Automática (2+2 plazas). ESIGELEC solo ofrece diploma de ingeniero "
               "(francés, 'CONTENU-PEDAGOGIQUE' de 1 página sin descriptivos), programas de intercambio EES/SEDT (tablas de horas/ECTS por bloque, sin "
               "descriptivos) y el Master of Technology en inglés. Se elige el Master of Technology Electronic Embedded Systems (la más afín a "
               "Electrónica Industrial y Automática): es el único con descriptivos por módulo (objetivos + temas). PARCIAL: nivel máster, no grado; "
               "los ECTS se dan por bloque en una tabla 'Snapshot' (no por módulo) y no se extraen; sin bibliografía ni evaluación por módulo. "
               "Semestres 1-3 de 30 ECTS + prácticas en S4. El PDF está en en.vizzmedia.com (host del proveedor web enlazado desde en.esigelec.fr/courses/); "
               "robots.txt de en.esigelec.fr y de vizzmedia permiten el acceso con PoliteClient."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas")


if __name__ == "__main__":
    main()
