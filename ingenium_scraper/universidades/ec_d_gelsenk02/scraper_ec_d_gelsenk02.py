"""Fase 2 - Westfaelische Hochschule Gelsenkirchen Maschinenbau: cada ficha del Modulhandbuch (PDF compartido) -> Markdown.

Uso: python universidades/ec_d_gelsenk02/scraper_ec_d_gelsenk02.py [--sample N | --all | --codes C1 C2]
Se elimina «11 Modulbeauftragter und hauptamtlich Lehrender» (nombres de docentes).
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
from discover_ec_d_gelsenk02 import PDF_URL, modules, page_lines  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_gelsenk02"
SAMPLE = ["MA1", "TM2", "KL1", "BA", "FV 1", "MSR1"]
NL = chr(10)
SECT = re.compile(r"^(\d{1,2}) (Lehrveranstaltungen|Lernergebnisse|Inhalte|Lehrformen|Teilnahmevoraussetzungen|Prüfungsformen|"
                  r"Voraussetzungen für die Vergabe|Voraussetzungen für die Teilnahme|Verwendung des Moduls|Stellenwert|"
                  r"Modulbeauftragter|Sonstige Informationen)(.*)$")


def build(entry: dict, block: list[str]) -> tuple[str, dict]:
    body = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", ""]
    head, secs, cur, expect = [], [], None, 1
    for l in block:
        m = SECT.match(l.strip())
        if m and int(m.group(1)) == expect:
            rest = m.group(3).strip()
            cur = [int(m.group(1)), m.group(2) + (" " + rest if m.group(2) not in ("Lehrveranstaltungen",) and rest and not rest.startswith(("Kontaktzeit",)) else ""), []]
            if m.group(2) == "Lehrveranstaltungen" and rest:
                cur[2].append(rest)
            secs.append(cur)
            expect += 1
        elif cur:
            cur[2].append(l.rstrip())
        else:
            head.append(l.rstrip())
    head = [h for h in head[1:] if h.strip()]  # sin el titulo
    body += ["## Kopfdaten", "", *head, ""]
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    for num, title, lines in secs:
        if num == 11:
            continue
        content = [x for x in lines if x.strip()]
        text = " ".join(content).strip()
        if num == 3 and text:
            found["contents"] = True
        if num == 2 and text:
            found["learning_outcomes"] = True
        if num == 6 and text:
            found["assessment"] = True
        if num == 5 and text and not re.fullmatch(r"(keine|-|gemäß BPO)[.]?", text, re.I):
            found["prerequisites"] = True
        if num == 12 and re.search(r"\(\d{4}\)|Verlag|Auflage|ISBN|Springer|Hanser", text):
            found["bibliography"] = True
        body += [f"## {num} {title}", "", *content, ""]
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
    mods = modules(lines)
    order = [m["code"] for m in mods]
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in order:
            print(f"SKIP {c}")
            continue
        try:
            i = order.index(c)
            end = mods[i + 1]["idx"] if i + 1 < len(mods) else len(lines)
            block = [t for _, t in lines[mods[i]["hdr"]:end]]  # desde la cabecera de tabla (el titulo ya esta en el catalogo)
            block = ["TITULO"] + block
            md, found = build(r, block)
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} sin: {[k for k, v in found.items() if not v]}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
