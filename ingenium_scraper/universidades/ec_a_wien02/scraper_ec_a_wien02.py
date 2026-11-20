"""Fase 2 - TU Wien Maschinenbau: cada modulo del Studienplan (PDF) -> Markdown.

Uso: python universidades/ec_a_wien02/scraper_ec_a_wien02.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1]))
sys.path.insert(0, str(HERE))

import wien_parse as wp  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

SLUG = "ec_a_wien02"
SAMPLE = ["MB-mathematik-1", "MB-mechanik-2", "MB-konstruktion", "MB-bachelorabschlussmodul", "MB-simulationstechnik", "MB-formula-student-i"]
LABELS = ["Regelarbeitsaufwand", "Lernergebnisse", "Inhalt", "Erwartete Vorkenntnisse", "Verpflichtende Voraussetzungen",
          "Angewendete Lehr- und Lernformen und geeignete Leistungsbeurteilung", "Lehrveranstaltungen des Moduls"]
LABEL_RE = re.compile(r"^(" + "|".join(re.escape(l) for l in LABELS) + r"):\s*(.*)$")
SUBLABEL = re.compile(r"^(Fachkompetenzen|Fachliche und methodische Kompetenzen|Kognitive und praktische Kompetenzen|"
                      r"Überfachliche Kompetenzen|Sozial- und Selbstkompetenzen):\s*(.*)$")
HEADS = {"Lernergebnisse": "Learning outcomes (Lernergebnisse)", "Inhalt": "Contents (Inhalt)",
         "Erwartete Vorkenntnisse": "Expected prior knowledge (Erwartete Vorkenntnisse)",
         "Verpflichtende Voraussetzungen": "Mandatory prerequisites (Verpflichtende Voraussetzungen)",
         "Angewendete Lehr- und Lernformen und geeignete Leistungsbeurteilung": "Teaching methods and assessment (Lehr- und Lernformen, Leistungsbeurteilung)",
         "Lehrveranstaltungen des Moduls": "Courses of the module (ECTS/SWS, type, title)"}


def build(entry: dict, body: list[str]) -> tuple[str, dict]:
    out, cur, buf = [f"# {entry['nombre_asignatura']}", "", f"- ECTS: {entry['creditos_ects']:g}", f"- Group: {entry['curso_semestre']}"], None, []
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}

    def flush():
        nonlocal buf
        if cur and cur in HEADS:
            out.extend(["", f"## {HEADS[cur]}", ""])
            if cur == "Lehrveranstaltungen des Moduls":
                out.extend(f"- {l}" for l in buf if l)
            else:
                text = ""
                for l in buf:
                    sub = SUBLABEL.match(l)
                    if l.startswith(("•", "–", "- ")):
                        text += "\n- " + l.lstrip("•–- ").strip()
                    elif sub:
                        text += f"\n\n**{sub.group(1)}:** {sub.group(2)}"
                    elif text.endswith("-") and l[:1].islower() and re.search(r"[a-zäöüß]-$", text):
                        text = text[:-1] + l
                    else:
                        text += " " + l
                out.append(text.strip())
            found_key = {"Lernergebnisse": "learning_outcomes", "Inhalt": "contents", "Verpflichtende Voraussetzungen": "prerequisites",
                         "Erwartete Vorkenntnisse": "prerequisites",
                         "Angewendete Lehr- und Lernformen und geeignete Leistungsbeurteilung": "assessment"}.get(cur)
            if found_key and any(buf) and " ".join(buf).strip().lower() not in ("keine.", "keine"):
                found[found_key] = True
        buf = []

    for l in body:
        m = LABEL_RE.match(l)
        if m:
            flush()
            cur = m.group(1)
            if m.group(2) and cur != "Regelarbeitsaufwand":
                buf.append(m.group(2))
        elif cur:
            buf.append(l)
    flush()
    return "\n".join(out), found


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
    url = next(iter(rows.values()))["url_guia_docente"]
    mods = {}
    for m in wp.parse_modules(wp.load_pages(client.get_bytes(url))):
        mods["MB-" + wp_slug(m["title"])] = m
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or c not in mods:
            print(f"SKIP {c}")
            continue
        try:
            md, found = build(r, mods[c]["body"])
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


def wp_slug(s: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


if __name__ == "__main__":
    sys.exit(main())
