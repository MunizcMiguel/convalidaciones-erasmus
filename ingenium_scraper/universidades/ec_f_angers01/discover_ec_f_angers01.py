"""Fase 1 - Universite d'Angers - BUT Genie electrique et informatique industrielle (GEII).
Fuente: PDF del programa en formations.univ-angers.fr (catalogo Ametys). Solo BUT 1 (tronco comun, S1-S2) y
las matieres de cada parcours no tienen ficha con contenidos publica -> catalogo 'parcial', sin Fase 2.
Uso: python universidades/ec_f_angers01/discover_ec_f_angers01.py
"""
from __future__ import annotations
import io, json, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_angers01"
UNI = "Université d'Angers"
GRADO = "BUT Génie électrique et informatique industrielle (GEII)"
PDF = ("https://formations.univ-angers.fr/plugins/odf-web/odf/_content/program-but-genie-electrique-et-informatique-industrielle/"
       "BUT%20_%20G%C3%A9nie%20%C3%A9lectrique%20et%20informatique%20industrielle.pdf")
URL_PLAN = "https://formations.univ-angers.fr/fr/offre-de-formation/bachelor-universitaire-de-technologie-BUT/sciences-technologies-sante-STS/but-genie-electrique-et-informatique-industrielle-KQAM9WWM.html"
LINE = re.compile(r"^(?P<n>.+?) Mati[eè]re(?P<h>(?: [\d,]+h)*)\s*$")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower().encode("ascii", "ignore").decode()).strip("-")[:60]


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    r = pypdf.PdfReader(io.BytesIO(c.get_bytes(PDF)))
    text = "\n".join(p.extract_text() or "" for p in r.pages)
    start = text.index("BUT 1 | Génie électrique et informatique industrielle\nBUT 1")
    end = text.index("BUT 2 - BUT 3 |", start + 100)
    sem, seen, entries = None, {}, []
    for ln in text[start:end].split("\n"):
        ln = ln.strip()
        m = re.match(r"Semestre (\d)", ln)
        if m:
            sem = int(m.group(1)); continue
        m = LINE.match(ln)
        if not m or sem is None:
            continue
        name = m.group("n").strip()
        if re.match(r"(Portefolio|Heures tuteur|SA[EÉ])", name):
            continue
        key = name.lower()
        if key in seen:
            continue
        seen[key] = 1
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura="BUT1-" + slug(name), nombre_asignatura=name,
            curso_semestre=f"BUT 1 / Semestre {sem}", curso=1, semestre=sem, creditos_ects=None, caracter="obligatoria",
            idioma_pagina="fr", url_guia_docente=None, tipo_fuente="sin_guia"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0, estrategia_fuente="PDF del programa (catalogo Ametys) parseado con pypdf; solo el tronco BUT 1",
        generado_por="discover_ec_f_angers01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Titulación elegida: BUT GEII (3 años, 180 ECTS, IUT de Angers), la más afín a Grado en Ingeniería Electrónica Industrial y "
               "Automática (2 plazas del Excel, la de más filas con Tecnologías Industriales); Angers no tiene grado de Mecánica ni licence EEA "
               "localizada en el catálogo. PARCIAL: las fichas de cada recurso en formations.univ-angers.fr solo traen horas CM/TD/TP e idioma "
               "(sin contenidos, resultados de aprendizaje, evaluación ni ECTS por asignatura), y el PDF del programa solo da horas y créditos por UE. "
               "Por eso solo se listan las matières del tronco común BUT 1 (S1-S2) sin guía; BUT 2-3 (parcursos AII, ESE, EME) no se desglosa. "
               "robots.txt de formations.univ-angers.fr permite el acceso."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas")


if __name__ == "__main__":
    main()
