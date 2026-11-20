"""Fase 2 - Hochschule Osnabrueck Maschinenbau: cada ficha del Modulhandbuch (PDF compartido) -> Markdown.

Uso: python universidades/ec_d_osnabru02__elec/scraper_ec_d_osnabru02__elec.py [--sample N | --all | --codes C1 C2]
Se elimina desde «Am Modul beteiligte Personen» (Modulpromotor*in y Lehrende: nombres de docentes).
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
from discover_ec_d_osnabru02__elec import URL_PLAN, modules, page_lines  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_osnabru02__elec"
SAMPLE = ["11B2312", "11B2321", "11B0617", "11B0002", "11B0094", "11B2302"]
NL = chr(10)
H2 = {"Allgemeine Informationen zum Modul", "Modulinhalte", "Arbeitsaufwand, Lehr- und Lernformen", "Voraussetzungen für die Vergabe von ECTS-Leistungspunkten",
      "Voraussetzungen für die Teilnahme", "Kompetenzorientierte Lernergebnisse", "Literatur", "Verwendbarkeit nach Studiengängen"}
H3 = {"Kurzbeschreibung", "Lehr-Lerninhalte", "Gesamtarbeitsaufwand", "Lehr- und Lernformen", "Dozentengebundenes Lernen", "Dozentenungebundenes Lernen",
      "Weitere Erläuterungen", "Benotete Prüfungsleistung", "Unbenotete Prüfungsleistung", "Bemerkung zur Prüfungsart", "Prüfungsdauer und Prüfungsumfang",
      "Empfohlene Vorkenntnisse", "Wissensverbreiterung", "Wissensvertiefung", "Wissensverständnis", "Nutzung und Transfer", "Kommunikation und Kooperation"}


def build(m: dict, block: list[str]) -> tuple[str, dict]:
    body = [f"# {m['title']}", ""]
    if m["en"]:
        body += [f"*{m['en']}*", ""]
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    cur, buf = None, []
    secs = []
    for l in block:
        s = l.strip()
        if s == "Am Modul beteiligte Personen":
            break
        if s in H2 or s in H3:
            if cur is not None:
                secs.append((cur, buf))
            cur, buf = s, []
        elif cur is not None and s:
            buf.append(s)
        elif s and cur is None:
            pass
    if cur is not None:
        secs.append((cur, buf))
    for name, content in secs:
        text = " ".join(content).strip()
        if name == "Lehr-Lerninhalte" and text and text != "-":
            found["contents"] = True
        if name == "Kurzbeschreibung" and text and not found["contents"] and len(text) > 200:
            found["contents"] = True
        if name in ("Wissensverbreiterung", "Wissensvertiefung", "Wissensverständnis", "Nutzung und Transfer", "Kommunikation und Kooperation") and text:
            found["learning_outcomes"] = True
        if name in ("Benotete Prüfungsleistung", "Unbenotete Prüfungsleistung") and text and text != "-":
            found["assessment"] = True
        if name == "Literatur" and text and text != "-":
            found["bibliography"] = True
        if name in ("Voraussetzungen für die Teilnahme", "Empfohlene Vorkenntnisse") and text and text != "-":
            found["prerequisites"] = True
        body += [("## " if name in H2 else "### ") + name, "", *(content or ["-"]), ""]
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
    with pdfplumber.open(client.get_file(URL_PLAN)) as pdf:
        lines = page_lines(pdf)
    mods = {m["code"]: m for m in modules(lines)}
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in mods:
            print(f"SKIP {c}")
            continue
        try:
            m = mods[c]
            block = [t for _, t in lines[m["hdr"]:m["end"]]]
            md, found = build(m, block)
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} sin: {[k for k, v in found.items() if not v]}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
