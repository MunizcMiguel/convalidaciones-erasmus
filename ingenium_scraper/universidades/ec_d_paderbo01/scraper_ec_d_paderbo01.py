"""Fase 2 - Paderborn Maschinenbau: cada modulo del Modulhandbuch (PDF compartido) -> Markdown.

Uso: python universidades/ec_d_paderbo01/scraper_ec_d_paderbo01.py [--sample N | --all | --codes C1 C2]
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
from discover_ec_d_paderbo01 import PDF_URL, SECTION, modules, page_lines  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_paderbo01"
SAMPLE = ["M.105.9451", "M.104.1208", "M.104.1217", "M.104.1210", "M.104.4210", "M.079.05102", "A.104.4010"]
SECT = re.compile(r"^(\d{1,2}) (Modulstruktur|Wahlmöglichkeiten|Teilnahmevoraussetzungen|Inhalte|Lernergebnisse|Prüfungsleistung|Studienleistung|"
                  r"Voraussetzungen für die (?:Teilnahme|Vergabe)|Gewichtung|Verwendung|Modulbeauftragte|Sonstige Hinweise)(.*)$")
RAW_SECTIONS = {"1", "6"}  # tablas: se conservan las lineas tal cual
DROP_SECTIONS = {"12"}  # Modulbeauftragte/r: nombre de docente


def clean_para(lines: list[str]) -> list[str]:
    out, buf = [], ""
    for l in lines:
        s = l.strip()
        if not s:
            continue
        if s.startswith(("•", "-", "–")) and len(s) > 2 and s[1] == " ":
            if buf:
                out.append(buf)
            buf = "- " + s[2:]
        elif buf and buf.endswith("-") and s[:1].islower():
            buf = buf[:-1] + s
        else:
            buf = (buf + " " + s).strip()
    if buf:
        out.append(buf)
    mark = re.compile(r"\s+(?=(?:Inhalte? der Lehrveranstaltung|Contents of the course|Content of the course|Teilnahmevoraussetzungen der Lehrveranstaltung|"
                      r"Prerequisites of course|Lernergebnisse der Lehrveranstaltung|Learning outcomes of the course)\b)")
    return [x for p in out for x in mark.sub("\x00", p).split("\x00")]


def build(entry: dict, block: list[str]) -> tuple[str, dict]:
    sections: list[tuple[str, str, list[str]]] = []
    head: list[str] = []
    cur = None
    for l in block:
        m = SECT.match(l.strip())
        if m and (not cur or int(m.group(1)) > int(cur[0]) or m.group(1) == "1"):
            cur = (m.group(1), (m.group(2) + m.group(3)).strip().rstrip(":"), [])
            sections.append(cur)
        elif cur:
            cur[2].append(l)
        else:
            head.append(l)
    body = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", ""]
    meta_line = " ".join(x.strip() for x in head if x.strip() and not x.startswith("Workload") and not SECTION.match(x.strip()))
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    for num, title, lines in sections:
        if num in DROP_SECTIONS:
            continue
        if num == "13":  # el final del bloque arrastra el encabezado del modulo siguiente ("2.7 Titulo")
            cut = next((i for i, l in enumerate(lines) if SECTION.match(l.strip())), len(lines))
            lines = lines[:cut]
        lines = [l.replace("(cid:52)", "[x]").replace("(cid:50)", "[ ]") for l in lines]
        txt_lines = [l for l in lines if l.strip()]
        body += [f"## {num} {title}", ""]
        if num in RAW_SECTIONS:
            body += [l.strip() + "  " for l in txt_lines]
        else:
            body += [p if p.startswith(("- ", "**")) else p for p in clean_para(lines)]
        body.append("")
        text = " ".join(txt_lines)
        if num == "4" and text.strip():
            found["contents"] = True
        if num == "5" and text.strip():
            found["learning_outcomes"] = True
        if num == "6" and re.search(r"\d+\s*%|Klausur|Hausarbeit|Referat|Portfolio|mündlich|Prüfung", text):
            found["assessment"] = True
        if num == "3" and text.strip() and not re.fullmatch(r"(keine|none|keine/none|-)\.?", text.strip(), re.I):
            found["prerequisites"] = True
        if re.search(r"Literatur|Lehrbuch|Bibliograph", text):
            found["bibliography"] = True
    return "\n".join(body), found


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
    mods = modules(lines)
    # mismo orden que el catalogo: reconstruir clave codigo -> indices
    by_page_name = {}
    for n, md in enumerate(mods):
        end = mods[n + 1]["start"] if n + 1 < len(mods) else len(lines)
        by_page_name[(md["page"], md["name"])] = [t for _, t in lines[md["start"]:end]]
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia":
            print(f"SKIP {c}")
            continue
        try:
            page = int(r["paginas_pdf"].split("-")[0])
            md_txt, found = build(r, by_page_name[(page, r["nombre_asignatura"])])
            write_markdown(SLUG, r, md_txt, found)
            print(f"ok {c} {len(md_txt)} {[k for k, v in found.items() if not v] or ''}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
