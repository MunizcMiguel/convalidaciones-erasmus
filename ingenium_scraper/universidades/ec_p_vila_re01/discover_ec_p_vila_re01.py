"""Fase 1 - UTAD (P VILA-RE01): Licenciatura em Engenharia Mecanica (1.º ciclo, 180 ECTS, Escola de Ciencias e Tecnologia).
Plan de estudos oficial: Aviso n.º 22542/2023 (Diario da Republica 2.ª serie, 23-nov-2023), PDF de 3 paginas. Las fichas de UC no son publicas (portal del estudiante con login) -> sin_guia, parcial.
Uso: python universidades/ec_p_vila_re01/discover_ec_p_vila_re01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_p_vila_re01"
UNIVERSIDAD = "Universidade de Trás-os-Montes e Alto Douro (UTAD)"
GRADO = "Licenciatura em Engenharia Mecânica (Mechanical Engineering, 1.º ciclo)"
URL_PLAN = "https://files.diariodarepublica.pt/2s/2023/11/227000000/0023800240.pdf"
URL_CURSO = "https://www.utad.pt/estudar/en/cursos/mechanical-engineering/"
ROW = re.compile(r"^(?P<n>.+?)\s*(?:\. ?)+\s*(?P<area>[A-Z]{2,3}) (?P<sem>\d)\.º Semestre(?:\. ?)+\s*(?P<rest>[\d –]+)$")


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf_path = c.get_file(URL_PLAN)
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    entries, seen, year = [], set(), None
    for line in text.split("\n"):
        m = re.fullmatch(r"\((\d)\.º ano\)", line.strip())
        if m:
            year = int(m.group(1))
            continue
        m = ROW.match(line.strip())
        if not m or year is None:
            continue
        name = re.sub(r"\s+", " ", m["n"]).strip()
        ects = float(m["rest"].split()[-1])
        code = slug(name)
        assert code not in seen, code
        seen.add(code)
        sem = int(m["sem"])
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=name,
            curso_semestre=f"{year}.º ano / {sem}.º semestre ({m['area']})", curso=year, semestre=(year - 1) * 2 + sem, creditos_ects=ects,
            caracter="tfg" if name.lower().startswith("projeto") else "obligatoria", idioma_pagina="pt", url_guia_docente=None, tipo_fuente="sin_guia"))
    tot = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="plan alterado 2023/24 (Aviso 22542/2023)", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0, estrategia_fuente="PDF del Diário da República con el plan de estudios (cuadros 2-4, por año); sin fichas públicas",
        generado_por="discover_ec_p_vila_re01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Titulación elegida: Engenharia Mecânica (licenciatura, UTAD, código DGES 9123; ficha {URL_CURSO}); el Excel solo trae Grado en Ingeniería de Organización Industrial para este destino (2 plazas) y UTAD no tiene grado de Organización Industrial: Mecánica es la más afín (el plan incluye Gestão Industrial). "
               f"{len(entries)} UC, suma {tot:g} ECTS (plan 180). PARCIAL: la web de UTAD (utad.pt/estudar, WordPress) solo trae ficha de curso sin plan ni fichas de UC; las fichas de UC están en inforestudante.utad.pt/nonio (requiere login: regla de parada, no se accede). "
               "Todas las filas son sin_guia; sin Fase 2. Código = slug del nombre (el DR no da código). No incluye optativas si el plan no las lista (el DR publicado no contiene cuadro de optativas). Idioma: portugués."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "UC", tot, "ECTS")


if __name__ == "__main__":
    main()
