"""Fase 2 - THI Maschinenbau: extrae cada modulo del Modulhandbuch (PDF compartido) a Markdown.

Uso: python universidades/ec_d_ingolst01/scraper_ec_d_ingolst01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pypdf  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_ingolst01"
SAMPLE = ["MA1_MB", "MA2_MB", "Konstr1_MB", "WT1_MB", "TM1_MB", "BA_MB", "CAD_MB", "FWM_CAD_Aufbau_MB"]
LABELS = ["Angestrebte Lernergebnisse", "Inhalt", "Literatur", "Empfohlene Voraussetzungen", "Prüfungsleistungen",
          "Erläuterungen zu den Prüfungsleistungen", "Anmerkungen", "Lehrformen des Moduls", "Medienformen",
          "Besonderes", "Voraussetzungen für die Teilnahme"]
LABEL_RE = re.compile(r"^(" + "|".join(re.escape(l) for l in LABELS) + r"):\s*(.*)$")
RE_NUM = re.compile(r"^\s*\d+\s*$")
_pdf_cache: dict[str, list[str]] = {}


def page_lines(text: str) -> list[str]:
    ls = [l.rstrip() for l in text.split("\n")]
    for i in range(min(6, len(ls))):
        if RE_NUM.match(ls[i]):
            ls = ls[i + 1:]
            break
    return [l for l in ls if l.strip()]


def pages_of(client: PoliteClient, url: str) -> list[list[str]]:
    if url not in _pdf_cache:
        r = pypdf.PdfReader(io.BytesIO(client.get_bytes(url)))
        _pdf_cache[url] = [p.extract_text() or "" for p in r.pages]
    return [page_lines(t) for t in _pdf_cache[url]]


def to_markdown(entry: dict, lines: list[str]) -> tuple[str, dict]:
    # quitar cabecera de seccion (5.x ...) antes del titulo y profesorado
    k = next(i for i, l in enumerate(lines) if "Modulkürzel:" in l)
    lines = lines[max(k - 3, 0):] if False else lines
    out_lines, skip = [], False
    for l in lines:
        s = l.strip()
        if s.startswith("Modulverantwortliche"):
            skip = True
            continue
        if skip:
            if s.startswith("Leistungspunkte"):
                skip = False
            else:
                continue
        out_lines.append(s)
    joined = []
    for s in out_lines:
        if joined and joined[-1].endswith("Erläuterungen zu den"):
            joined[-1] += " " + s
        else:
            joined.append(s)
    out_lines = joined
    if out_lines and out_lines[0] == entry["nombre_asignatura"]:
        out_lines = out_lines[1:]
    # fusionar lineas de continuacion
    merged: list[str] = []
    for s in out_lines:
        m_label = LABEL_RE.match(s)
        starts_new = bool(m_label) or s.startswith(("•", "o ", "–", "- ")) or re.match(r"^[A-ZÄÖÜ][\wäöüß ()/-]{2,40}(?::\s|:$)", s) \
            or s.startswith(("Zuordnung", "Studiengang", "Modulattribute", "Leistungspunkte", "Arbeitsaufwand", "Kontaktstunden",
                             "Selbststudium", "Gesamtaufwand", "Lehrveranstaltungen", "Modulkürzel", "Maschinenbau", "Deutsch", "Englisch"))
        if merged and not starts_new and not merged[-1].endswith(":"):
            prev = merged[-1]
            merged[-1] = (prev[:-1] + s) if re.search(r"[a-zäöüß]-$", prev) and s[:1].islower() else prev + " " + s
        else:
            merged.append(s)
    body, cur = [f"# {entry['nombre_asignatura']}", ""], None
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    for s in merged:
        m = LABEL_RE.match(s)
        if m and m.group(1) in ("Angestrebte Lernergebnisse", "Inhalt", "Literatur", "Empfohlene Voraussetzungen",
                                  "Prüfungsleistungen", "Erläuterungen zu den Prüfungsleistungen", "Anmerkungen", "Lehrformen des Moduls"):
            cur = m.group(1)
            body += ["", f"## {cur}", ""]
            if m.group(2):
                body.append(m.group(2))
            continue
        if s.startswith("•"):
            s = "- " + s.lstrip("• ").strip()
        elif s.startswith("o "):
            s = "  - " + s[2:]
        if cur is None and body[-1] != "" and not s.startswith("- "):
            pass
        body.append(s)
    md = "\n".join(body)
    md = re.sub(r"\n{3,}", "\n\n", md)
    def has(h):
        m = re.search(rf"## {h}\n\n(.*?)(?=\n## |\Z)", md, re.S)
        return bool(m and m.group(1).strip() and m.group(1).strip().lower() not in ("keine", "keine."))
    found["learning_outcomes"] = has("Angestrebte Lernergebnisse")
    found["contents"] = has("Inhalt")
    found["assessment"] = has("Prüfungsleistungen")
    found["bibliography"] = has("Literatur") and "ISBN" in md or has("Literatur")
    found["prerequisites"] = has("Empfohlene Voraussetzungen")
    return md, found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    if a.codes:
        codes = a.codes
    elif a.all:
        codes = list(rows)
    else:
        codes = [c for c in SAMPLE if c in rows][: a.sample]
    client = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia":
            print(f"SKIP {c}")
            continue
        try:
            ini, fin = map(int, r["paginas_pdf"].split("-"))
            pgs = pages_of(client, r["url_guia_docente"])[ini - 1: fin]
            lines = [l for p in pgs for l in p]
            md, found = to_markdown(r, lines)
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} chars {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
