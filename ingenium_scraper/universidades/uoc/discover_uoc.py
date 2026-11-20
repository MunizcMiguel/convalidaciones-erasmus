#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — University of Crete (Πανεπιστήμιο Κρήτης),
Department of Materials Science and Engineering (Τμήμα Επιστήμης και Μηχανικής Υλικών, ΤΕΜΥ),
first-cycle degree (Πτυχίο, 4 years, 240 ECTS), curriculum "ΕΜΥ" (in force since 2024-25).

The University of Crete has no Mechanical Engineering degree; this is its closest first-cycle
engineering degree (see notas_descubrimiento.md).

Sources (all on www.materials.uoc.gr, a WordPress site; robots.txt is empty -> allowed):
  1. WP REST page 2352 "Οργάνωση Σπουδών" -> link to the current study guide (Οδηγός Σπουδών, newest year).
  2. Study guide PDF, "Πίνακας Ι" -> official plan: code, Greek name, hours, Y/E, ECTS, prerequisites,
     semester for compulsory courses, elective groups.
  3. WP REST page 14063 "Resources for Undergraduates" -> link "Courses' Outlines (Engineering)":
     ONE shared English PDF with the outline (syllabus) of every ΕΜΥ course.
     Its table of contents gives the English titles; its body gives the start page and the
     SEMESTER field (used for electives, which Table I does not place in a semester).

Usage (from the project root):
    python universidades/uoc/discover_uoc.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "uoc"
UNIVERSIDAD = "University of Crete (Πανεπιστήμιο Κρήτης)"
GRADO = ("Materials Science and Engineering — Πτυχίο Τμήματος Επιστήμης και Μηχανικής Υλικών "
         "(first cycle, 240 ECTS, curriculum ΕΜΥ)")
WP = "https://www.materials.uoc.gr/wp-json/wp/v2/pages/"
PAGE_ORGANOSI = 2352      # "Οργάνωση Σπουδών" (Greek, links to study guides)
PAGE_RESOURCES = 14063    # "Resources for Undergraduates" (English, links to course outlines)
URL_PLAN_HUMAN = "https://www.materials.uoc.gr/proptychiaka/organosi-spoudon/"

# Greek -> Latin for codes (safe file names; Greek capitals that look Latin in the source).
TRANSLIT = str.maketrans({"Ε": "E", "Μ": "M", "Υ": "Y", "Π": "P", "Ρ": "R", "Α": "A", "Ι": "I"})
SEM_GR = {"Α": 1, "Β": 2, "B": 2, "Γ": 3, "Δ": 4, "Ε": 5, "ΣΤ": 6, "Ζ": 7, "Η": 8}
RE_SEM_HDR = re.compile(r"^(ΣΤ|[ΑΒBΓΔΕΖΗ])’\s*Εξάμηνο$")
RE_CODE_T1 = re.compile(r"^(?:\d{3}|[ΠP][ΡP][ΑA]\s*[–-]\s*\d{3}|9[ΙI]\d)$")
RE_TOC = re.compile(r"^([EΕ][MΜ][YΥ])\s*-\s*(\d{3})\s+(.+?)\s*\.{3,}\s*(\d+)\s*$")
RE_TOC_GROUP = re.compile(r"^(.+?)\s*\.{3,}\s*\d+\s*$")
RE_BODY_CODE = re.compile(r"COURSE CODE\s+[EΕ][MΜ][YΥ]\s*-\s*(\d{3})\s+SEMESTER\s+(.+)$")
RE_HEADING = re.compile(r"^[EΕ][MΜ][YΥ]\s*-\s*(\d{3})\s+\S")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


def join_name(cell: str) -> str:
    """Multi-line PDF cell -> one line; keeps hyphenated compounds ('Νανοδομές-\\nΥπερμοριακή')."""
    parts = [p.strip() for p in cell.split("\n") if p.strip()]
    out = ""
    for p in parts:
        out = out + p if out.endswith("-") else (out + " " + p if out else p)
    return norm(out)


def wp_links(http: PoliteClient, page_id: int) -> list[tuple[str, str, str]]:
    """(section heading, link text, href) of a WP page, in document order."""
    d = http.get_json(f"{WP}{page_id}")
    soup = BeautifulSoup(d["content"]["rendered"], "lxml")
    out, heading = [], ""
    for el in soup.find_all(["h1", "h2", "h3", "h4", "a"]):
        if el.name != "a":
            heading = norm(el.get_text())
        elif el.get("href"):
            out.append((heading, norm(el.get_text()), el["href"]))
    return out


def find_sources(http: PoliteClient) -> tuple[str, int, str]:
    guides = [(int(m.group(1)), href) for h, t, href in wp_links(http, PAGE_ORGANOSI)
              if h == "Οδηγοί Σπουδών" and (m := re.fullmatch(r"Έτους (\d{4})", t))]
    if not guides:
        raise RuntimeError("Study-guide links not found on the 'Οργάνωση Σπουδών' page")
    year, guide_url = max(guides)
    outl = [href for _, t, href in wp_links(http, PAGE_RESOURCES)
            if "Outlines" in t and "Engineering" in t and href.lower().endswith(".pdf")]
    if len(outl) != 1:
        raise RuntimeError(f"'Courses' Outlines (Engineering)' link not found unambiguously: {outl}")
    return guide_url, year, outl[0]


# --------------------------------------------------------------------------- study guide, Table I
def parse_table1(pdf_path: Path) -> tuple[str, list[dict], float]:
    rows: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        cover = "\n".join((pdf.pages[i].extract_text() or "") for i in range(2))
        m = re.search(r"Ακ\.\s*Έτος\s*(\d{4})\s*-\s*(\d{4})", cover)
        if not m:
            raise RuntimeError("Academic year not found on the study-guide cover")
        curso_acad = f"{m.group(1)}-{m.group(2)}"
        # Table I lives on the pages after the heading "Πίνακας Ι" and before section 4.
        start = next(i for i, p in enumerate(pdf.pages) if "Πίνακας Ι:" in (p.extract_text() or ""))
        sem: int | None = None
        group: str | None = None
        in_electives = False
        for page in pdf.pages[start:start + 4]:
            for t in page.find_tables():
                for raw in t.extract():
                    cells = [c for c in raw if c not in (None, "")]
                    if not cells:
                        continue
                    first = join_name(cells[0])
                    hdr = [join_name(c) for c in cells]
                    sem_hdr = next((RE_SEM_HDR.match(h) for h in hdr if RE_SEM_HDR.match(h)), None)
                    if sem_hdr:
                        sem, in_electives, group = SEM_GR[sem_hdr.group(1)], False, None
                        continue
                    if "Μαθήματα Επιλογής" in hdr and any("Κωδικός" in h for h in hdr):
                        sem, in_electives, group = None, True, None   # list of electives
                        continue
                    if len(cells) == 1 and in_electives and not RE_CODE_T1.match(first):
                        group = first                                  # elective group heading
                        continue
                    if not RE_CODE_T1.match(first):
                        continue
                    if len(cells) != 8:
                        raise RuntimeError(f"Unexpected Table I row: {raw}")
                    code, name, th, ex, lab, ye, ects, prereq = cells
                    ye = ye.translate(TRANSLIT)  # Greek Υ / Ε -> Y / E
                    if ye not in ("Y", "E"):
                        raise RuntimeError(f"Unexpected Y/E value in {raw}")
                    rows.append({
                        "code_raw": norm(code), "name_el": join_name(name),
                        "hours": f"{th}-{ex}-{lab}", "ye": ye,
                        "ects_raw": ects, "ects": float(re.sub(r"\*+$", "", ects)),
                        "prereq": norm(prereq), "sem": sem if not in_electives else None,
                        "group": group,
                    })
        # ECTS rule for the degree (section 5): total and the share from the department
        text = "\n".join((p.extract_text() or "") for p in pdf.pages[start:start + 8])
        mt = re.search(r"τουλάχιστον\s+(\d+)\s+μονάδων\s+ECTS\s+συνολικά", text)
        if not mt:
            raise RuntimeError("Degree ECTS total not found in the study guide")
    return curso_acad, rows, float(mt.group(1))


# --------------------------------------------------------------------------- English outlines PDF
RE_DIVIDER = re.compile(r"^(?:[A-Z]+ SEMESTER|COURSES OUTLINE|(?:List of )?Courses of Elective Direction|\d{1,3})$")


def is_divider(line: str, groups: set[str]) -> bool:
    """Document-structure line (semester / elective-group heading, page number), not course content."""
    line = norm(line)
    return line in groups or bool(RE_DIVIDER.match(line))


def parse_outlines(pdf_path: Path) -> tuple[dict[str, dict], set[str], int]:
    """{code3: {name_en, toc_page, start, end, semester_raw}}, group headings, n_pages."""
    with pdfplumber.open(pdf_path) as pdf:
        texts = [(p.extract_text() or "") for p in pdf.pages]
    n = len(texts)
    body0 = next(i for i, t in enumerate(texts) if "COURSES OUTLINE" in t)
    toc: dict[str, dict] = {}
    groups: set[str] = set()
    for t in texts[:body0]:
        for line in t.splitlines():
            line = line.strip()
            m = RE_TOC.match(line)
            if m:
                toc[m.group(2)] = {"name_en": norm(m.group(3)), "toc_page": int(m.group(4))}
            elif (g := RE_TOC_GROUP.match(line)):
                groups.add(norm(g.group(1)))
    # Body: start page (0-based) of each course = page with its heading "ΕΜΥ - 101 Title"
    # (the "COURSE CODE" row may fall on the next page). The heading must repeat the TOC title,
    # which rules out codes quoted inside a cell (prerequisites...).
    starts: dict[str, int] = {}
    sem_raw: dict[str, str] = {}
    lead: dict[str, bool] = {}   # True if the course heading is the first content line of its page
    for i in range(body0, n):
        lines = [ln.strip() for ln in texts[i].splitlines() if ln.strip()]
        for j, line in enumerate(lines):
            m = RE_HEADING.match(line)
            if m and m.group(1) in toc and m.group(1) not in starts:
                code = m.group(1)
                title = norm(line[m.end(1):]).lower()
                if not title.startswith(toc[code]["name_en"].lower()[:12]):
                    continue
                starts[code] = i
                before = [ln for ln in lines[:j] if not is_divider(ln, groups)]
                lead[code] = not before
            mc = RE_BODY_CODE.search(line)
            if mc:
                if mc.group(1) in sem_raw:
                    raise RuntimeError(f"Course {mc.group(1)} appears twice in the outlines PDF")
                sem_raw[mc.group(1)] = norm(mc.group(2))
    if set(starts) != set(toc) or set(sem_raw) != set(toc):
        raise RuntimeError(f"TOC/body mismatch: {set(starts) ^ set(toc)} {set(sem_raw) ^ set(toc)}")
    order = sorted(starts, key=lambda c: starts[c])
    out: dict[str, dict] = {}
    for k, code in enumerate(order):
        if k + 1 < len(order):
            nxt = order[k + 1]
            end = starts[nxt] - 1 if lead[nxt] else starts[nxt]
        else:
            end = n - 1
        out[code] = {**toc[code], "start": starts[code] + 1, "end": end + 1, "semester_raw": sem_raw[code]}
    return out, groups, n


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    guide_url, guide_year, outline_url = find_sources(http)
    curso_acad, t1, ects_total = parse_table1(http.get_file(guide_url))
    outlines, _groups, n_pages = parse_outlines(http.get_file(outline_url))

    entries: list[CatalogEntry] = []
    sin_guia = []
    for r in t1:
        raw = r["code_raw"]
        num = re.fullmatch(r"\d{3}", raw)
        if num:
            code = f"EMY-{raw}"
        else:
            code = re.sub(r"\s*[–-]\s*", "-", raw).translate(TRANSLIT)   # ΠΡΑ – 001 -> PRA-001, 9Ι1 -> 9I1
        o = outlines.get(raw) if num else None
        sem = r["sem"]
        if sem is None and o:
            ms = re.match(r"(\d)", o["semester_raw"])   # "7th", "8h" (sic), "7th and 8th"
            sem = int(ms.group(1)) if ms else None
        if raw == "440":
            caracter = "tfg"
        elif code.startswith("PRA"):
            caracter = "practicas"
        elif r["ye"] == "Y":
            caracter = "obligatoria"
        else:
            caracter = "optativa"
        curso_sem = (f"Semester {sem}" if sem else "Semester not fixed") + \
            (f" / elective group: {r['group']}" if r["group"] else "") + \
            (f" / outline SEMESTER field: {o['semester_raw']}" if o and r["sem"] is None else "")
        entry = CatalogEntry(
            universidad=UNIVERSIDAD,
            nombre_grado=GRADO,
            codigo_asignatura=code,
            nombre_asignatura=o["name_en"] if o else r["name_el"],
            curso_semestre=curso_sem,
            curso=(sem + 1) // 2 if sem else None,
            semestre=sem,
            creditos_ects=r["ects"],
            caracter=caracter,
            idioma_pagina="en" if o else "el",
            url_guia_docente=outline_url if o else None,
            tipo_fuente="pdf_compartido" if o else "sin_guia",
            paginas_pdf=f"{o['start']}-{o['end']}" if o else None,
        )
        if not o:
            sin_guia.append(f"{code} {r['name_el']} ({r['ects_raw']} ECTS)")
        entries.append(entry)

    # ---------- validation ----------
    codes = [e.codigo_asignatura for e in entries]
    dup = {c for c in codes if codes.count(c) > 1}
    assert not dup, f"Duplicate codes: {dup}"
    assert all(e.url_guia_docente or e.tipo_fuente == "sin_guia" for e in entries)
    missing_in_plan = set(outlines) - {e.codigo_asignatura[4:] for e in entries if e.codigo_asignatura.startswith("EMY-")}
    assert not missing_in_plan, f"Outlines without a Table I row: {missing_in_plan}"
    by_sem: dict[int, float] = {}
    for e in entries:
        if e.caracter in ("obligatoria",):
            by_sem[e.semestre] = by_sem.get(e.semestre, 0) + e.creditos_ects
    assert sorted(by_sem) == [1, 2, 3, 4, 5, 6] and all(v == 30 for v in by_sem.values()), by_sem
    comp = sum(by_sem.values())
    tfg = sum(e.creditos_ects for e in entries if e.caracter == "tfg")
    elect = sum(e.creditos_ects for e in entries if e.caracter == "optativa" and e.tipo_fuente != "sin_guia")
    extra = sum(e.creditos_ects for e in entries if e.tipo_fuente == "sin_guia")
    offered = sum(e.creditos_ects for e in entries)
    assert comp + 60 == ects_total, (comp, ects_total)
    assert tfg + elect >= 60
    pages = [tuple(map(int, e.paginas_pdf.split("-"))) for e in entries if e.paginas_pdf]
    assert all(1 <= a <= b <= n_pages for a, b in pages)

    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=GRADO,
        nivel="bachelor",
        curso_academico=curso_acad,
        url_plan_estudios=guide_url,
        ects_totales_plan=ects_total,
        estrategia_fuente=(
            f"PDF: official study guide {guide_year} (Οδηγός Σπουδών, Greek), 'Πίνακας Ι' parsed with pdfplumber "
            "tables (code, Greek name, hours, Y/E, ECTS, prerequisites, semester). The guide link is found via the "
            "WordPress REST API (page 'Οργάνωση Σπουδών'). Syllabi: ONE shared English PDF 'Courses' Outlines "
            "(Engineering)' (official HQA course-outline template per course), linked from the REST page "
            "'Resources for Undergraduates'; page ranges derived from its TOC + 'COURSE CODE' rows."),
        generado_por="discover_uoc.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(
            "University of Crete has no Mechanical Engineering degree (that exists at other Greek universities; the "
            "Technical University of Crete is a different institution, out of scope). Chosen: first-cycle degree of the "
            "Department of Materials Science and Engineering (renamed from 'Materials Science and Technology'; new "
            "curriculum ΕΜΥ since 2024-25), UoC's only engineering degree (the other departments of its School of "
            "Sciences and Engineering are Physics, Chemistry, Mathematics, Computer Science, Biology); it includes "
            "Mechanics of Materials, "
            "Mechanical Design, Transport Phenomena, Fluid Dynamics and a 'Mechanical Engineering and Materials "
            f"Technology' elective group. {len(entries)} rows: {len([e for e in entries if e.caracter == 'obligatoria'])} "
            f"compulsory ({comp:g} ECTS, 30 per semester 1-6), thesis EMY-440 ({tfg:g} ECTS, counted as elective), "
            f"{len([e for e in entries if e.caracter == 'optativa' and e.tipo_fuente != 'sin_guia'])} electives "
            f"({elect:g} ECTS offered; the student takes 60 ECTS of electives incl. the thesis in semesters 7-8), plus "
            f"{len(sin_guia)} rows without outline (sin_guia: {'; '.join(sin_guia)}). Offered total {offered:g} vs "
            f"{ects_total:g} required. Internships PRA-001/002 give 10 ECTS each but only 5 count towards the degree; "
            "9I1/9I2 'Δημοσίευση' (publication) 5 ECTS each. Elective semesters come from the outline's SEMESTER "
            "field (7th/8th). Codes: 'EMY-' + Table I number; Greek letters transliterated (ΠΡΑ->PRA, 9Ι1->9I1). "
            "Course names are the English titles of the outlines PDF TOC (Greek names for sin_guia rows)."),
    )
    catalog = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{GRADO} [{curso_acad}]: {len(entries)} rows, offered {offered:g} ECTS "
          f"(compulsory {comp:g} + thesis {tfg:g} + electives {elect:g} + other {extra:g}); plan {ects_total:g} -> {out}")
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
