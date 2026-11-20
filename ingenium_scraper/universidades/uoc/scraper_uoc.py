#!/usr/bin/env python3
"""Fase 2 · Scraper — University of Crete, Materials Science and Engineering (curriculum ΕΜΥ).

All syllabi live in ONE shared English PDF ("Courses' Outlines (Engineering)"), one course outline per
course following the official Greek HQA course-outline template:
  (1) GENERAL  (2) LEARNING OUTCOMES  (3) SYLLABUS  (4) TEACHING and LEARNING METHODS - EVALUATION
  (5) ATTACHED (or RECOMMENDED) BIBLIOGRAPHY
The template is a sequence of bordered tables whose left column carries fixed instructions for the
author ("if credits are awarded for separate components...", the checklist of general competences...).
Those instructions are template chrome, not course content, and are removed (see TEMPLATE below).

Per course: pages `paginas_pdf` of the catalog; the first page is cropped below the course heading and the
last page above the next course heading. Tables are read with pdfplumber; nested tables (workload,
assessment weights) are rendered as Markdown tables.

Usage (from the project root):
    python universidades/uoc/scraper_uoc.py --sample 5
    python universidades/uoc/scraper_uoc.py --codes EMY-101 EMY-440
    python universidades/uoc/scraper_uoc.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "uoc"

# Fixed, diverse pilot sample.
SAMPLE = [
    "EMY-111",  # Mathematics I — 1st sem., maths
    "EMY-101",  # Physics I — 1st sem., theory + lab, nested workload table, long assessment
    "EMY-342",  # Mechanics of Materials — 5th sem., core engineering
    "EMY-446",  # Fluid Dynamics — elective (Mechanical Engineering and Materials Technology group)
    "EMY-440",  # Undergraduate Thesis — atypical
    # reserve for --sample > 5
    "EMY-011",  # English I — heading and COURSE CODE on different pages, numbered "(4)" items inside
    "EMY-444",  # Photonic Materials — starts at the bottom of a page shared with EMY-442
    "EMY-462",  # last course of the PDF
]

# Subscripts (AB2, Α2Β3) sit ~3-4 pt below the baseline: a 5 pt tolerance keeps them on their line.
Y_TOL = 5
TABLE_SETTINGS = {"text_y_tolerance": Y_TOL}

RE_HEADING = re.compile(r"^[EΕ][MΜ][YΥ]\s*-\s*(\d{3})\s+\S")
RE_SECTION = re.compile(r"^\((\d)\)\s*(GENERAL|LEARNING OUTCOMES|SYLLABUS|TEACHING\s+and\s+LEARNING\s+METHODS\s*[-–]\s*"
                        r"EVALUATION|(?:ATTACHED|RECOMMENDED|SUGGESTED)\s+BIBLIOGRAPHY)\s*$", re.I)
RE_DIVIDER = re.compile(r"^(?:[A-Z]+ SEMESTER|COURSES OUTLINE|(?:List of )?Courses of Elective Direction|"
                        r"Materials Physics and Computational Materials Science|Materials Chemistry – Biomaterials|"
                        r"Mechanical Engineering and Materials Technology|General Interest|\d{1,3})$")

# Field labels of the template (canonical form) and the fragments they are split into in the PDF.
LABELS = [
    "SCHOOL", "ACADEMIC UNIT", "LEVEL OF STUDIES", "COURSE CODE", "SEMESTER", "COURSE TITLE",
    "INDEPENDENT TEACHING ACTIVITIES", "COURSE TYPE", "PREREQUISITE COURSES",
    "LANGUAGE OF INSTRUCTION and EXAMINATIONS", "IS THE COURSE OFFERED TO ERASMUS STUDENTS",
    "COURSE WEBSITE (URL)", "DELIVERY", "USE OF INFORMATION AND COMMUNICATIONS TECHNOLOGY",
    "TEACHING METHODS", "STUDENT PERFORMANCE EVALUATION",
]
# Instructions printed by the template (author guidance). Matched line by line, whitespace-insensitive.
TEMPLATE = """
if credits are awarded for separate components of the course, e.g. lectures, laboratory exercises, etc. If the
credits are awarded for the whole of the course, give the weekly teaching hours and the total credits
WEEKLY TEACHING HOURS CREDITS
Add rows if necessary. The organisation of teaching and the teaching methods used are described in detail at (d).
general background, special background, specialised general knowledge, skills development
and EXAMINATIONS:
IS THE COURSE OFFERED TO ERASMUS STUDENTS
The course learning outcomes, specific knowledge, skills and competences of an appropriate level, which the
students will acquire with the successful completion of the course are described.
Consult Appendix A
• Description of the level of learning outcomes for each qualifications cycle, according to the Qualifications
Framework of the European Higher Education Area
• Descriptors for Levels 6, 7 & 8 of the European Qualifications Framework for Lifelong Learning and Appendix B
• Guidelines for writing Learning Outcomes
Taking into consideration the general competences that the degree-holder must acquire (as these appear in the
Diploma Supplement and appear below), at which of the following does the course aim?
Search for, analysis and synthesis of data and information, with the use of the necessary technology
Adapting to new situations Decision-making Working independently Team work
Working in an international environment Working in an interdisciplinary environment
Production of new research ideas
Project planning and management Respect for difference and multiculturalism Respect for the natural environment
Showing social, professional and ethical responsibility and sensitivity to gender issues
Criticism and self-criticism Production of free, creative and inductive thinking …… Others… …….
Face-to-face, Distance learning, etc.
Use of ICT in teaching, laboratory education, communication with students
The manner and methods of teaching are described in detail. Lectures, seminars, laboratory practice, fieldwork,
study and analysis of bibliography, tutorials, placements, clinical practice, art workshop, interactive teaching,
educational visits, project, essay writing, artistic creativity, etc.
The student's study hours for each learning activity are given as well as the hours of non-directed study
according to the principles of the ECTS
Description of the evaluation procedure
Language of evaluation, methods of evaluation, summative or conclusive, multiple choice questionnaires,
short-answer questions, open-ended questions, problem solving, written work, essay/report, oral examination,
public presentation, laboratory work, clinical examination of patient, art interpretation, other
Specifically-defined evaluation criteria are given, and if and where they are accessible to students.
"""


def squash(s: str, lower: bool = True) -> str:
    """No whitespace, unified quotes (lower-case by default): robust substring tests against the template."""
    s = s.replace("’", "'").replace("‘", "'").replace("\xa0", " ")
    s = re.sub(r"\s+", "", s)
    return s.lower() if lower else s


def tsquash(s: str) -> str:
    """Template key: letters/digits only, British spelling, case kept. Case-sensitive on purpose: the
    instructions are in sentence case, so an upper-case value such as "GENERAL BACKGROUND" (COURSE TYPE)
    is not mistaken for the hint "general background, ..."."""
    s = s.replace("’", "'").replace("‘", "'")
    return re.sub(r"[\s,]+", "", s).replace("ization", "isation").replace("ized", "ised")


TEMPLATE_CS = tsquash(TEMPLATE)
LABEL_SQ = {squash(lb): lb for lb in LABELS}
LABELS_CS = squash(" ".join(LABELS + ["and EXAMINATIONS:", "ERASMUS STUDENTS"]), lower=False)
SHORT_TEMPLATE = {squash(x) for x in ("etc.", "ECTS", "WEEKLY", "TEACHING", "HOURS", "CREDITS",
                                      "TEACHING HOURS", "development", "students", "environment",
                                      "TECHNOLOGY", "COMMUNICATIONS", "EVALUATION", "procedure",
                                      "Appendix B", "……", "…….", "Others…", "etc", "Team work",
                                      "Decision-making", "EXAMINATIONS:", "ERASMUS STUDENTS", "issues", "i", "ssues",
                                      "Education Area", "Higher Education Area", "in detail.",
                                      "described in detail.", "total credits", "the total credits")}


def is_template_line(line: str) -> bool:
    sq = squash(line)
    if not sq:
        return True
    if sq in SHORT_TEMPLATE:
        return True
    cs = squash(line, lower=False)
    letters = [ch for ch in line if ch.isalpha()]
    mostly_upper = letters and sum(ch.isupper() for ch in letters) >= 0.6 * len(letters)
    if len(cs) >= 8 and mostly_upper and cs in LABELS_CS and sq.rstrip(":") not in LABEL_SQ:
        return True                    # tail of a label split over two rows ("COMMUNICATIONS TECHNOLOGY")
    ts = tsquash(line)
    return len(ts) >= 13 and ts in TEMPLATE_CS


class OutlineError(RuntimeError):
    pass


# ------------------------------------------------------------------ page geometry
def inside(inner, outer, tol: float = 1.0) -> bool:
    return (inner[0] >= outer[0] - tol and inner[1] >= outer[1] - tol and
            inner[2] <= outer[2] + tol and inner[3] <= outer[3] + tol)


def md_table(rows: list[list[str]]) -> str:
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    esc = [[c.replace("|", r"\|").replace("\n", " <br> ").strip() for c in r] for r in rows]
    out = ["| " + " | ".join(esc[0]) + " |", "|" + "---|" * width]
    out += ["| " + " | ".join(r) + " |" for r in esc[1:]]
    return "\n".join(out)


def compact(row: list) -> list[str]:
    """Drop empty/None cells and consecutive duplicates (merged cells repeat their text)."""
    out: list[str] = []
    for c in row:
        if c is None or not str(c).strip():
            continue
        c = str(c).strip()
        if out and out[-1] == c:
            continue
        out.append(c)
    return out


def nested_md(tbl) -> str:
    """Nested table -> Markdown table, without template hints (empty string if nothing is left)."""
    rows = []
    for r in tbl.extract():
        cells = [" ".join(clean_lines(c.split("\n"))) for c in compact(r)]
        if any(cells):
            rows.append(cells)
    return md_table(rows)


SUBHEADS = {squash("Learning outcomes"): "Learning outcomes", squash("General Competences"): "General Competences"}


def clean_lines(lines: list[str]) -> list[str]:
    """Remove template instructions. A cell made only of template fragments (e.g. the unticked
    checklist of general competences) is dropped whole, whatever the fragment length."""
    lines = [ln.strip() for ln in lines if ln.strip()]
    if len(lines) >= 3 and all(tsquash(ln) in TEMPLATE_CS or squash(ln) in SHORT_TEMPLATE for ln in lines) \
            and not any(squash(ln) in SUBHEADS for ln in lines):
        return []
    lines = [ln for ln in lines if squash(ln) in SUBHEADS or not is_template_line(ln)]
    if len(lines) == 1 and re.fullmatch(r"[a-z]", lines[0]):
        return []                      # stray glyph left over from a hyphenated template word
    return lines


def match_label(text: str) -> str | None:
    sq = squash(text).rstrip(":.")
    if len(sq) < 6:
        return LABEL_SQ.get(sq)
    if sq in LABEL_SQ:
        return LABEL_SQ[sq]
    upper = text.strip().upper() == text.strip()
    cands = [lb for s, lb in LABEL_SQ.items()
             if s.startswith(sq) and (len(sq) >= 0.4 * len(s) or (upper and len(sq) >= 8))]
    return cands[0] if len(cands) == 1 else None


def split_label(lines: list[str]) -> tuple[str | None, list[str]]:
    """If the cell starts with a template label (possibly split over lines), return (label, rest)."""
    lines = [ln.strip() for ln in lines if ln.strip()]
    for k in range(min(4, len(lines)), 0, -1):
        lb = match_label(" ".join(lines[:k]))
        if lb:
            return lb, lines[k:]
    return None, lines


# ------------------------------------------------------------------ extraction
class Item:
    """One vertical element of a page: ('text', line) | ('row', cells) | ('md', markdown)."""
    def __init__(self, top: float, kind: str, value):
        self.top, self.kind, self.value = top, kind, value


def page_items(page, y0: float, y1: float) -> list[Item]:
    tables = page.find_tables(TABLE_SETTINGS)
    top_tables = [t for t in tables if not any(o is not t and inside(t.bbox, o.bbox) and o.bbox != t.bbox
                                               for o in tables)]
    nested = [t for t in tables if t not in top_tables]
    items: list[Item] = []
    for t in top_tables:
        if t.bbox[3] <= y0 or t.bbox[1] >= y1:
            continue
        prev = None   # (Item, [boxes of non-empty cells])
        for r_obj, raw in zip(t.rows, t.extract()):
            rtop = r_obj.bbox[1]
            if rtop < y0 - 1 or rtop >= y1:
                continue
            cells: list = []
            boxes: list = []
            for cbox, txt in zip(r_obj.cells, raw):
                if cbox is None or txt is None:
                    continue
                boxes.append(cbox)
                inner = [n for n in nested if inside(n.bbox, cbox)]
                if inner and any(match_label(" ".join(compact(n.extract()[0])[:1])) for n in inner if n.extract()):
                    inner = []                 # a label boxed in its own table: treat the cell as text
                if inner and all(len(compact(r)) <= 1 for n in inner for r in n.extract()):
                    inner = []                 # one-column box around running text: not a real table
                if inner:
                    nested_txt = set()
                    for n in inner:
                        for r in n.extract():
                            cc = compact(r)
                            nested_txt.add(squash("".join(cc)))
                            nested_txt.update(squash(ln) for c in cc for ln in c.split("\n"))
                    nested_tok = {w for n in inner for r in n.extract() for c in r if c
                                  for w in re.findall(r"\w+", str(c).lower())}
                    keep = [ln for ln in str(txt).split("\n") if squash(ln) not in nested_txt
                            and not set(re.findall(r"\w+", ln.lower())) <= nested_tok]
                    cells.append(("mixed", keep, [m for m in (nested_md(n) for n in inner) if m]))
                else:
                    cells.append(("text", str(txt)))
            # Some outlines draw label and value cells with slightly different row lines, so pdfplumber
            # splits one visual row in two (value row a few points above the label row). Merge a row into
            # the previous one when their non-empty cells overlap vertically but not horizontally.
            pairs_cur = [(b, c) for b, c in zip(boxes, cells) if c_nonempty(c)]
            boxes = [b for b, _ in pairs_cur]
            if prev and boxes and prev[1] and \
                    any(b[1] < p[3] - 1 and p[1] < b[3] - 1 for b in boxes for p in prev[1]) and \
                    not any(b[0] < p[2] - 1 and p[0] < b[2] - 1 for b in boxes for p in prev[1]):
                pit, pboxes = prev
                pairs = sorted(list(zip(pboxes, pit.value)) + pairs_cur, key=lambda z: z[0][0])
                pit.value = [c for _, c in pairs]
                prev = (pit, [b for b, _ in pairs])
                continue
            it = Item(rtop, "row", [c for _, c in pairs_cur])
            items.append(it)
            prev = (it, boxes)
    # text outside the tables
    for ln in page.extract_text_lines(y_tolerance=Y_TOL):
        top, mid = ln["top"], (ln["top"] + ln["bottom"]) / 2
        if top < y0 - 1 or top >= y1:
            continue
        if any(t.bbox[1] - 1 <= mid <= t.bbox[3] + 1 and t.bbox[0] - 2 <= ln["x0"] <= t.bbox[2] for t in top_tables):
            continue
        items.append(Item(top, "text", ln["text"].strip()))
    items.sort(key=lambda it: it.top)
    return items


def c_nonempty(c) -> bool:
    return bool(str(c[1]).strip()) if c[0] == "text" else bool(c[1] or c[2])


def heading_top(page, code: str | None = None) -> list[tuple[float, str]]:
    """(top, code) of every course heading line on the page."""
    out = []
    for ln in page.extract_text_lines(y_tolerance=Y_TOL):
        m = RE_HEADING.match(ln["text"].strip())
        if m and (code is None or m.group(1) == code):
            out.append((ln["top"], m.group(1)))
    return out


def course_items(pdf, code3: str, first: int, last: int) -> tuple[list[Item], str]:
    items: list[Item] = []
    heading = ""
    for pno in range(first, last + 1):
        page = pdf.pages[pno - 1]
        y0, y1 = 0.0, float(page.height) + 1
        heads = heading_top(page)
        if pno == first:
            own = [t for t, c in heads if c == code3]
            if not own:
                raise OutlineError(f"heading of {code3} not found on page {first}")
            y0 = own[0]
        others = [t for t, c in heads if c != code3 and t > y0]
        if others:
            y1 = min(others)
            if pno != last:
                raise OutlineError(f"next course starts on page {pno} before the end of the range")
        page_its = page_items(page, y0, y1)
        if pno == first:
            heading = next((it.value for it in page_its if it.kind == "text" and RE_HEADING.match(it.value)), "")
        items += page_its
    return items, heading


# ------------------------------------------------------------------ Markdown
RE_BULLET = re.compile("^[•●▪◦■‣]\s*")
NO_VALUE = {"-", "–", "--", "none", "no", "n/a", "nan"}


RE_SUB_BULLET = re.compile(r"^o\s+(?=[A-ZΑ-Ω])")   # Word's second-level bullet "o" (Courier)


def lines_md(lines: list[str]) -> str:
    return "\n".join(RE_SUB_BULLET.sub("  - ", RE_BULLET.sub("- ", ln)) for ln in lines)


def merge_tables(parts: list[str]) -> list[str]:
    """A table cut by a page break comes out as two consecutive Markdown tables with the same number
    of columns; the second 'header' is really a data row, so it is appended to the first table."""
    out: list[str] = []
    for p in parts:
        if out and p.startswith("|") and out[-1].startswith("|"):
            prev_lines, cur_lines = out[-1].split("\n"), p.split("\n")
            ncol = lambda ln: ln.count(" | ") + 1
            if ncol(prev_lines[0]) == ncol(cur_lines[0]) and not cur_lines[0].startswith(("| Field |", "| Teaching activity |")):
                out[-1] = "\n".join(prev_lines + [cur_lines[0]] + cur_lines[2:])
                continue
        out.append(p)
    return out


def to_markdown(items: list[Item], heading: str) -> tuple[str, dict]:
    parts: list[str] = []
    found = {"contents": False, "learning_outcomes": False, "assessment": False,
             "bibliography": False, "prerequisites": False}
    section = 0
    sec_content = {k: 0 for k in range(0, 6)}
    kv: list[list[str]] = []        # pending key/value rows (GENERAL)
    acts: list[list[str]] = []      # pending teaching-activity rows
    text_run: list[str] = []        # consecutive free-text lines (one Markdown block)
    grid: list[list[str]] = []      # consecutive rows of short cells (first row = header)

    def flush():
        if text_run:
            parts.append(lines_md(text_run))
            text_run.clear()
        if grid:
            parts.append(md_table(grid))
            grid.clear()
        if kv:
            parts.append(md_table([["Field", "Value"]] + kv))
            kv.clear()
        if acts:
            parts.append(md_table([["Teaching activity", "Weekly teaching hours", "Credits"]] + acts))
            acts.clear()

    for it in items:
        if it.kind == "text":
            txt = it.value
            if RE_HEADING.match(txt) and txt == heading:
                continue
            if RE_DIVIDER.match(txt) or (is_template_line(txt) and squash(txt) not in SUBHEADS):
                continue
            m = RE_SECTION.match(txt)
            if m:
                flush()
                section = int(m.group(1))
                parts.append(f"## ({section}) {m.group(2).strip()}")
                continue
            if squash(txt) in SUBHEADS:
                flush()
                parts.append(f"### {SUBHEADS[squash(txt)]}")
                continue
            if kv or acts:
                flush()
            text_run.append(txt)
            sec_content[section] += 1
            continue
        # ---- table row: label detection on the raw first cell, then template cleaning
        cells = []
        for c in it.value:
            raw = str(c[1]).split("\n") if c[0] == "text" else list(c[1])
            nmd = [] if c[0] == "text" else c[2]
            cells.append((raw, nmd))
        cells = [(r, n) for r, n in cells if any(x.strip() for x in r) or n]
        if not cells:
            continue
        label, rest0 = split_label(cells[0][0])
        if label:
            cells[0] = (rest0, cells[0][1])
        cleaned = []
        for k, (raw, nmd) in enumerate(cells):
            lines = clean_lines(raw)
            if not lines and not nmd:
                continue
            # merged cells repeat a label / long text: keep the first copy only
            if cleaned and cleaned[-1][0] == lines and not nmd and (len(" ".join(lines)) > 20 or match_label(" ".join(lines))):
                continue
            cleaned.append((lines, nmd))
        if label and cleaned and match_label(" ".join(cleaned[0][0])) == label:
            cleaned = cleaned[1:]              # label repeated in a second cell
        nmds = [m for _, n in cleaned for m in n]
        if label:
            if label == "COURSE CODE":
                vals = [" ".join(c[0]) for c in cleaned]
                if len(vals) >= 3 and match_label(vals[1]) == "SEMESTER":
                    flush_text = text_run and flush()
                    kv.append(["COURSE CODE", vals[0]])
                    kv.append(["SEMESTER", " ".join(vals[2:])])
                    continue
            if label == "INDEPENDENT TEACHING ACTIVITIES":
                if text_run:
                    flush()
                continue
            values = [lines_md(c[0]) for c in cleaned if c[0]]
            v = " ".join(values).strip()
            if label == "PREREQUISITE COURSES" and v and squash(v) not in {squash(x) for x in NO_VALUE}:
                found["prerequisites"] = True
            if section == 1 and not nmds and all(len(x) < 400 for x in values):
                if text_run:
                    flush()
                kv.append([label, " ".join(values)])
                continue
            if not values and not nmds:
                continue                       # field left empty in the source
            flush()
            if label == "STUDENT PERFORMANCE EVALUATION" and (v or nmds):
                found["assessment"] = True
            parts.append(f"### {label}")
            if len(values) >= 2 and not nmds and all("\n" not in x and len(x) < 80 for x in values):
                grid.append(values)            # e.g. "Activity | Semester workload" + following rows
            else:
                parts.extend(values + nmds)
            if section:
                sec_content[section] += 1
            continue
        if not cleaned:
            continue
        texts = [lines_md(c[0]) for c in cleaned if c[0]]
        if section == 1 and len(cleaned) == 1 and not nmds and kv and \
                not re.fullmatch(r"[\d.,+x ]*", texts[0]):
            kv[-1][1] = (kv[-1][1] + "\n" + texts[0]).strip()   # value continued after a page break
            continue
        if section == 1 and len(cleaned) == 2 and not nmds and \
                not re.fullmatch(r"[\d.,+x ]*", " ".join(cleaned[1][0])):
            if text_run:
                flush()
            kv.append([" ".join(c[0]) for c in cleaned])   # field whose label the author rewrote
            continue
        if section == 1 and len(cleaned) >= 2 and not nmds and all(len(c[0]) == 1 and len(c[0][0]) < 80 for c in cleaned):
            if text_run:
                flush()
            row = [c[0][0] for c in cleaned]
            if all(re.fullmatch(r"[\d.,+x ]+", x) for x in row):   # totals row of the template
                row = ["Total"] + row
            acts.append(row)
            continue
        if section == 1 and len(cleaned) == 1 and not nmds and re.fullmatch(r"[\d.,+x ]+", texts[0]):
            acts.append(["Total", "", texts[0]])
            continue
        flat = [" ".join(c[0]) for c in cleaned if c[0]]
        if (len(flat) >= 2 or (grid and flat)) and not nmds and \
                all(len(c[0]) <= (6 if grid else 3) for c in cleaned) and \
                all(len(t) < (200 if grid else 80) for t in flat):
            if text_run:
                parts.append(lines_md(text_run))
                text_run.clear()
            grid.append(flat)                  # row of short cells -> Markdown table
            sec_content[section] += 1
            continue
        if len(texts) == 1 and not nmds and squash(texts[0]) in SUBHEADS:
            flush()
            parts.append(f"### {SUBHEADS[squash(texts[0])]}")
            continue
        sec_content[section] += 1
        if len(cleaned) == 1 and not nmds:
            # one free-text cell: some outlines put every printed line in its own table row,
            # so consecutive cells are joined into one block (line breaks kept)
            if kv or acts or grid:
                flush()
            text_run.extend(cleaned[0][0])
            continue
        flush()
        parts.extend(texts + nmds)
    flush()
    found["learning_outcomes"] = sec_content[2] > 0
    found["contents"] = sec_content[3] > 0
    found["bibliography"] = sec_content[5] > 0
    md = f"# {heading}\n\n" + "\n\n".join(merge_tables([p for p in parts if p.strip()]))
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md, found


# ------------------------------------------------------------------ main
def scrape(http: PoliteClient, pdf, entry: dict) -> tuple[str, dict]:
    code3 = entry["codigo_asignatura"].split("-")[1]
    a, b = map(int, entry["paginas_pdf"].split("-"))
    items, heading = course_items(pdf, code3, a, b)
    if not heading:
        raise OutlineError("course heading not found")
    return to_markdown(items, heading)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    ap.add_argument("--debug", action="store_true", help="print the Markdown instead of saving it")
    args = ap.parse_args()

    cat = load_catalog(SLUG)
    if not cat:
        print("catalogo_urls.json missing: run discover_uoc.py first", file=sys.stderr)
        return 2
    rows = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    if args.all:
        todo = list(rows)
    elif args.codes:
        todo = args.codes
    else:
        todo = SAMPLE[: args.sample or 5]

    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdfs: dict[str, object] = {}
    failed = 0
    for code in todo:
        e = rows.get(code)
        if e is None:
            print(f"{code}: FAIL not in catalog")
            failed += 1
            continue
        if e["tipo_fuente"] == "sin_guia":
            print(f"{code}: skip (sin_guia)")
            continue
        try:
            url = e["url_guia_docente"]
            if url not in pdfs:
                pdfs[url] = pdfplumber.open(http.get_file(url))
            md, found = scrape(http, pdfs[url], e)
            if args.debug:
                print(md)
            else:
                out = write_markdown(SLUG, e, md, found)
                miss = [k for k, v in found.items() if not v]
                print(f"{code}: ok {len(md)} chars -> {out.name}" + (f" (missing: {', '.join(miss)})" if miss else ""))
        except (FetchError, OutlineError, ValueError) as ex:
            print(f"{code}: FAIL {ex}")
            failed += 1
    for p in pdfs.values():
        p.close()
    print("HTTP:", http.stats)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
