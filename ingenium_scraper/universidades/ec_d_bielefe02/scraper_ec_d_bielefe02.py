"""Fase 2 - HSBI Maschinenbau: cada ficha de Anlage B (Modulhandbuch, PDF compartido) -> Markdown.

Uso: python universidades/ec_d_bielefe02/scraper_ec_d_bielefe02.py [--sample N | --all | --codes C1 C2]
Se elimina «13 Modulbeauftragte/r» (nombre de docente).
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
from discover_ec_d_bielefe02 import modules, page_lines, pdf_url  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_bielefe02"
SAMPLE = ["1148", "1091", "1214", "1291", "1134", "1232"]
NL = chr(10)
SECT = re.compile(r"^(\d{1,2}) (Lehrveranstaltung|Qualifikationsniveau|Lernergebnisse|Inhalte|Lehrformen|Teilnahmevoraussetzungen|Prüfungsformen|"
                  r"Art und Umfang|Prüfungssprache|Voraussetzung für die Vergabe|Verwendung des Moduls|Stellenwert|Modulbeauftragte|"
                  r"Sonstige Informationen|Sprache)\b(.*)$")


def build(entry: dict, block: list[str]) -> tuple[str, dict]:
    body = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", ""]
    head, secs, cur, expect = [], [], None, 1
    for l in block:
        m = SECT.match(l.strip())
        if m and int(m.group(1)) == expect:
            if m.group(2) == "Lehrveranstaltung":  # el resto de la linea es la cabecera de la tabla de horas
                cur = [1, "Lehrveranstaltung", [m.group(3).strip()] if m.group(3).strip() else []]
            else:
                cur = [int(m.group(1)), (m.group(2) + m.group(3)).strip().rstrip(":"), []]
            secs.append(cur)
            expect += 1
        elif cur:
            cur[2].append(l.rstrip())
        else:
            head.append(l.rstrip())
    # cabecera: titulo + tabla Kennnummer/Workload/Credits/Semester
    head = [h for h in head[1:] if h.strip()]
    body += ["## Kopfdaten", "", *[h for h in head], ""]
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    for num, title, lines in secs:
        if num == 13:  # Modulbeauftragte/r
            continue
        content = [x for x in lines if x.strip()]
        text = " ".join(content)
        if num == 4 and text:
            found["contents"] = True
        if num == 3 and text:
            found["learning_outcomes"] = True
        if num == 7 and text:
            found["assessment"] = True
        if num == 6 and not re.fullmatch(r"(Formal:\s*(keine)?\s*)?(Inhaltlich:\s*(keine)?)?", text.strip(), re.I) and text.strip():
            found["prerequisites"] = True
        if num == 14 and text and not re.search(r"Literatur wird zu Beginn der Veranstaltung bekannt gegeben[.]?\s*$", text) or (
                num == 14 and "Literatur" in text and len(text) > 90):
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
    url = pdf_url(client)
    with pdfplumber.open(client.get_file(url)) as pdf:
        lines = page_lines(pdf)
    # quita el numero de pagina al pie de cada pagina
    cleaned = []
    for n, (pg, l) in enumerate(lines):
        last = n + 1 == len(lines) or lines[n + 1][0] != pg
        if last and re.fullmatch(r"\d{1,3}", l.strip()):
            continue
        cleaned.append((pg, l))
    lines = cleaned
    mods = {m["code"]: (m, lines[m["idx"]:]) for m in modules(lines)}
    order = list(mods)
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in mods:
            print(f"SKIP {c}")
            continue
        try:
            m, rest = mods[c]
            nxt = mods[order[order.index(c) + 1]][0]["idx"] if order.index(c) + 1 < len(order) else len(lines)
            block = [t for _, t in lines[m["idx"]:nxt]]
            md, found = build(r, block)
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} sin: {[k for k, v in found.items() if not v]}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
