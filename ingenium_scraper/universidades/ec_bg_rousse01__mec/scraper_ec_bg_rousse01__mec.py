"""Fase 2 - University of Ruse (CAD in Mechanical and Instrument Engineering): cada descripcion del ECTS Information Package FMME -> Markdown.

Uso: python universidades/ec_bg_rousse01__mec/scraper_ec_bg_rousse01__mec.py [--sample N | --all | --codes C1 C2]
Se eliminan «Lecturers:» (nombres, telefonos, correos) y «Departments involved» se conserva (departamento, sin personas).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from discover_ec_bg_rousse01__mec import PDF_URL, descriptions, page_lines  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_bg_rousse01__mec"
SAMPLE = ["1668", "2531", "3361", "3366", "3396", "3379"]
NL = chr(10)
SECT = re.compile(r"^(Departments? involved|Departament involved|Lecturers?|Lectures|Abstracts?|Annotation|Course contents?|Teaching and assess{1,2}e?ment|"
                  r"Teaching and learning methods)\s*:\s*(.*)$", re.I)
DROP = re.compile(r"^(Lecturers?|Lectures)$", re.I)


def build(entry: dict, d: dict, block: list[str]) -> tuple[str, dict]:
    body = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", ""]
    facts = re.sub(r"^[ЕE][СC][ТT]S credits:", "ECTS credits:", block[1].strip())
    body += [f"- {facts}", ""]
    cur, secs = None, []
    for l in block[2:]:
        s = l.strip()
        if s.startswith("Assessment:") and cur is None:
            body.insert(len(body) - 1, f"- {s}")
            continue
        m = SECT.match(s)
        if m:
            cur = [m.group(1).strip().capitalize(), [m.group(2)] if m.group(2) else []]
            secs.append(cur)
        elif cur is not None and s:
            cur[1].append(s)
        elif s and cur is None:
            body.insert(len(body) - 1, f"- {s}")
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    for name, content in secs:
        if DROP.match(name):
            continue
        text = " ".join(content).strip()
        title = {"Teaching and assessement": "Teaching and assessment", "Departament involved": "Departments involved"}.get(name, name)
        if name.lower().startswith("course content") and text:
            found["contents"] = True
        if name.lower().startswith("teaching and assess") and text:
            found["assessment"] = True
        if name.lower().startswith(("abstract", "annotation")) and text:
            found["learning_outcomes"] = False  # los resumenes describen objetivos generales, no resultados de aprendizaje formales
        if re.search(r"\b(literature|bibliography|textbooks?)\b", text, re.I):
            found["bibliography"] = True
        body += [f"## {title}", "", *content, ""]
    found["assessment"] = found["assessment"] or any(x.startswith("- Assessment:") for x in body)  # tipo de evaluacion de la cabecera
    return NL.join(body), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    codes = a.codes or (list(rows) if a.all else [c for c in SAMPLE if c in rows][: a.sample])
    client = PoliteClient(cache_dir=HERE / "raw_cache")
    with pdfplumber.open(client.get_file(PDF_URL)) as pdf:
        lines = page_lines(pdf)
    desc = descriptions(lines)
    fails = 0
    for c in codes:
        r, d = rows.get(c), desc.get(c)
        if not r or not d or r["tipo_fuente"] == "sin_guia":
            print(f"omitido {c}: sin_guia")
            continue
        try:
            block = [t for _, t in lines[d["idx"]:d["end"]]]
            md, found = build(r, d, block)
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} sin: {[k for k, v in found.items() if not v]}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
