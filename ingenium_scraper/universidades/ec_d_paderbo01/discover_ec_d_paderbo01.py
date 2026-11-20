"""Fase 1 - Universitat Paderborn - Bachelor Maschinenbau (B.Sc., 6 semestres, 180 LP).

Fuente: Modulhandbuch oficial de la Fakultat fur Maschinenbau (PDF compartido, Stand 15.01.2026, plan PO "alte").
Un modulo = pagina con la tabla "Modulnummer: LP: Studiensem.: ...". Uso: python universidades/ec_d_paderbo01/discover_ec_d_paderbo01.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_paderbo01"
UNIVERSIDAD = "Universität Paderborn"
GRADO = "Maschinenbau (B.Sc.)"
PDF_URL = ("https://mb.uni-paderborn.de/fileadmin-mb/fakultaet/Studiengaenge/Modulhandbuecher/"
           "Modulhandbuecher_SoSe_26/Alte_POen/Ba_MB_SS26.pdf")
URL_PLAN = "https://mb.uni-paderborn.de/"

HDR = re.compile(r"^(?P<code>[AM]\.[\d.]+(?: / \.\d+(?: \(\w+\))?)?)?\s*(?P<wl>\d{2,3})\s+(?P<lp>\d{1,2})\s+(?P<rest>.*)$")
NOISE = re.compile(r"^(\d+ \d\. Studienjahr|\d+ Abschlussmodul|\d+)$")
SECTION = re.compile(r"^\d+(\.\d+)+ ")


def page_lines(pdf):
    """[(pagina_1idx, linea)] sin cabecera/pie de pagina."""
    out = []
    for i, pg in enumerate(pdf.pages, 1):
        txt = pg.extract_text(x_tolerance=1.5) or ""
        if txt.startswith("6 Englischsprachiges Lehrangebot"):  # anexo final, no es un modulo
            continue
        for l in txt.split("\n"):
            if not NOISE.match(l.strip()):
                out.append((i, l))
    return out


def is_noise_title(l: str) -> bool:
    return bool(SECTION.match(l)) or l.endswith((".", ":", "/")) or len(l.split()) > 9 or l.startswith("Vertiefungsrichtung")


def modules(lines):
    """Devuelve dicts con indice de inicio del bloque, nombre, codigo, LP, semestre."""
    found = []
    for j, (pg, l) in enumerate(lines):
        if not l.startswith("Modulnummer:"):
            continue
        k = j
        while k > 0 and not lines[k][1].startswith("Workload"):
            k -= 1
        title_lines = []
        t = k - 1
        while t >= 0 and len(title_lines) < 2 and not is_noise_title(lines[t][1]):
            title_lines.append(lines[t][1].strip())
            t -= 1
        title_lines.reverse()
        # DE / EN: si hay dos lineas validas, la primera es el nombre aleman; con una sola es el aleman
        name = title_lines[0] if title_lines else ""
        start = k - len(title_lines)
        m = None
        for q in range(j + 1, min(j + 5, len(lines))):
            m = HDR.match(lines[q][1].strip())
            if m:
                break
        assert m, f"cabecera sin LP en pag {pg}"
        found.append(dict(start=start, page=lines[start][0], name=name, code=m["code"], wl=int(m["wl"]), lp=int(m["lp"]), rest=m["rest"]))
    return found


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf_path = c.get_file(PDF_URL)
    with pdfplumber.open(pdf_path) as pdf:
        lines = page_lines(pdf)
        npag = len(pdf.pages)
    mods = modules(lines)
    entries, seen = [], {}
    for n, md in enumerate(mods):
        nxt = mods[n + 1] if n + 1 < len(mods) else None
        end_page = (nxt["page"] if nxt else npag)
        code = md["code"] or "SLUG-" + re.sub(r"[^a-z0-9]+", "-", md["name"].lower()).strip("-")
        code = code.split(" / ")[0]
        if code in seen:
            code = f"{code}-{seen[code] + 1}"
        seen[code.split("-")[0] if code.startswith("SLUG") else code] = seen.get(code, 0) + 1
        sem_txt = re.sub(r"\s*(Sommer-|Winter-|Sommersemester|Wintersemester|Sommer|Winter).*$", "", md["rest"]).strip()
        ms = re.match(r"(\d)", sem_txt)
        sem = int(ms.group(1)) if ms else None
        caracter = "tfg" if code.startswith("A.") else ("optativa" if re.match(r"M\.104\.4[2-7]\d\d|M\.048\.55201", code) else "obligatoria")
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=md["name"],
            curso_semestre=f"Semester {sem_txt}", curso=(sem + 1) // 2 if sem else None, semestre=sem,
            creditos_ects=float(md["lp"]), caracter=caracter, idioma_pagina="de", url_guia_docente=PDF_URL,
            tipo_fuente="pdf_compartido", paginas_pdf=f"{md['page']}-{end_page}"))
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes)), "codigos duplicados"
    total = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26 (Modulhandbuch SoSe 2026)",
        url_plan_estudios=PDF_URL, ects_totales_plan=180.0,
        estrategia_fuente="PDF compartido (Modulhandbuch Bachelor Maschinenbau, alemán, algunas guías bilingües DE/EN); un módulo por tabla 'Modulnummer'",
        generado_por="discover_ec_d_paderbo01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Grado: Maschinenbau B.Sc. (plan 'alte PO'; existe además 'Nachhaltiger Maschinenbau' con PO nueva, no catalogado). {len(entries)} módulos; suma bruta {total:g} LP > 180 porque "
               "incluye los módulos alternativos de las Vertiefungsrichtungen (Energie- und Verfahrenstechnik, Fertigungstechnik, Kunststofftechnik, Leichtbau, Mechatronik, Produktentwicklung, "
               "Werkstoffeigenschaften), Ingenieurinformatik y berufsbildende Anteile, y los Wahlpflichtmodule; cada estudiante cursa un itinerario de 180 LP. paginas_pdf = rango de páginas físicas donde "
               "puede aparecer el módulo (la última página puede compartirse con el inicio del siguiente). 'caracter' optativa = módulos M.104.42xx-47xx (Basis-/Wahlpflichtmodule), derivado del código. "
               "Código oficial M.xxx.xxxx; 'Sprachen' sin código oficial → slug del nombre. Semestre = el primero del rango indicado en la ficha."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos, LP bruto", total)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.semestre, e.paginas_pdf, e.caracter)


if __name__ == "__main__":
    main()
