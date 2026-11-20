"""Fase 1 - University of Ruse - Bachelor Electrical Power Engineering (240 ECTS). Fuente: ECTS Information Package de la Facultad de Electrotecnia, Electronica y Automatica (PDF, ingles).
Uso: python universidades/ec_bg_rousse01__elec/discover_ec_bg_rousse01__elec.py"""
from __future__ import annotations
import json, re, sys, time, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pdfplumber  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_bg_rousse01__elec"
UNIVERSIDAD = "University of Ruse \"Angel Kanchev\""
GRADO = "Electrical Power Engineering (Bachelor)"
URL_PLAN = "https://www.uni-ruse.bg/en/education/students/ECTS-package"
PDF_URL = "https://www.uni-ruse.bg/en/education/students/ECTS%20packages/Faculty%20of%20Electrical%20Engineering,%20Electronics%20and%20Automation.pdf"
CUR_PAGES = (51, 52)  # indices 0-based de la tabla CURRICULUM (localizados por texto en find_curriculum)
CODE = r"S[BO]?\d{4,6}"
SKIP = {"S00523", "S00683", "S00760", "S03258", "S03290", "S03294"}  # alternativas de idioma extranjero (se conserva English)


def norm(c):
    c = c.replace("SO", "S0")
    return "S0" + c[3:] if c.startswith("S00") and len(c) == 7 else c
TERMS = {"First": 1, "Second": 2, "Third": 3, "Fourth": 4, "Fifth": 5, "Sixth": 6, "Seventh": 7, "Eighth": 8}
CHROME = re.compile(r"^(Faculty of Electrical Engineering, Electronics and Automation ERASMUS ECTS Information Package|\d{1,3})$")
HEADER = re.compile(rf"^({CODE}) (\S.*)$")
NL = chr(10)


def page_lines(pdf):
    out = []
    for i, pg in enumerate(pdf.pages, 1):
        for l in unicodedata.normalize("NFC", pg.extract_text(x_tolerance=1.5) or "").split(NL):
            if not CHROME.match(l.strip()):
                out.append((i, l.rstrip()))
    return out


def descriptions(lines, start_page):
    heads = [i for i, (p, l) in enumerate(lines) if p > start_page and HEADER.match(l) and i + 1 < len(lines) and re.search(r"credits:\s*\d", lines[i + 1][1])]
    out = {}
    for n, i in enumerate(heads):
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        for j in range(i + 1, end):
            s = lines[j][1].strip()
            if s in ("OF A BACHELOR IN", "CURRICULUM") or s.startswith(("PROFESSIONAL STANDARDS", "of the degree course", "of the Master")):
                end = j
                break
        code = norm(HEADER.match(lines[i][1]).group(1))
        if code not in out:
            out[code] = dict(idx=i, end=end, page=lines[i][0], endpage=lines[end - 1][0], title=HEADER.match(lines[i][1]).group(2).strip())
    return out


def curriculum(pdf):
    """[(codigo, termino)] leyendo las lineas de texto de las paginas CURRICULUM (dos columnas por linea: terminos impar/par)."""
    pages = [i for i, pg in enumerate(pdf.pages) if "of the degree course in" in (pg.extract_text() or "") and "ELECTRICAL POWER ENGINEERING" in (pg.extract_text() or "") and "CURRICULUM" in (pg.extract_text() or "")]
    assert pages, "CURRICULUM no encontrado"
    out, terms = [], None
    for i in (pages[0], pages[0] + 1):
        for l in (pdf.pages[i].extract_text() or "").split(NL):
            m = re.match(r"Code (\w+) term .*Code (\w+) term", l)
            if m:
                terms = (TERMS[m.group(1)], TERMS[m.group(2)])
                continue
            m = re.match(r"Code Eighth term", l)
            if m:
                terms = (8, 8)
                continue
            if terms is None:
                continue
            found = [(mm.start(), mm.group(0)) for mm in re.finditer(rf"(?<![\w-]){CODE}(?=\s)", l)]
            for k, (_, c) in enumerate(found):
                out.append((norm(c), terms[k] if len(terms) > k and len(found) > 1 else terms[0]))
    return out, pages[0] + 1


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    c.get_text(URL_PLAN)
    with pdfplumber.open(c.get_file(PDF_URL)) as pdf:
        lines = page_lines(pdf)
        cur, p0 = curriculum(pdf)
    desc = descriptions(lines, 0)
    entries, seen = [], set()
    for code, term in cur:
        if code in seen or code in SKIP:
            continue
        seen.add(code)
        d = desc.get(code)
        title = d["title"] if d else f"Course {code}"
        low = title.lower()
        caracter = "tfg" if "thesis" in low else ("practicas" if "practice" in low else None)
        ects = None
        if d:
            m = re.search(r"credits:\s*(\d+(?:[.,]\d+)?)", lines[d["idx"] + 1][1])
            ects = float(m.group(1).replace(",", ".")) if m else None
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=title,
            curso_semestre=f"Term {term}", curso=(term + 1) // 2, semestre=term, creditos_ects=ects, caracter=caracter, idioma_pagina="en",
            url_guia_docente=PDF_URL if d else None, tipo_fuente="pdf_compartido" if d else "sin_guia",
            paginas_pdf=f"{d['page']}-{d['endpage']}" if d else None))
    total = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="Paquete ECTS FEEA (datos antiguos; ver notas)", url_plan_estudios=URL_PLAN, ects_totales_plan=240.0,
        estrategia_fuente="PDF compartido (Erasmus ECTS Information Package FEEA, inglés): plan por términos (líneas de texto) + descripción por asignatura",
        generado_por="discover_ec_bg_rousse01__elec.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=(f"Segunda titulación de Ruse (familia eléctrica/electrónica). La Facultad de Electrotecnia, Electrónica y Automática ofrece Electrical Power Engineering, Electronics, Computer Control and Automation, etc.; "
               f"se elige Electrical Power Engineering (grado 4 años, 240 ECTS): máquinas eléctricas, redes, alta tensión, protecciones, automatización. {len(entries)} asignaturas, {total:g} ECTS brutos "
               "(los grupos A/B/C del 8.º término y los idiomas extranjeros son alternativos). Código oficial S0xxxx. Idioma: inglés. El plan del paquete ECTS puede estar desfasado."),
    )
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "asignaturas, ECTS bruto", total, "; sin descripción:", sum(e.tipo_fuente == "sin_guia" for e in entries))
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.semestre, e.tipo_fuente, e.paginas_pdf)


if __name__ == "__main__":
    main()
