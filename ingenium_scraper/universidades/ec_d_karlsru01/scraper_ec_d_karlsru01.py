"""Fase 2 - KIT Maschinenbau B.Sc.: cada Modul del Modulhandbuch (PDF compartido) -> Markdown.
Uso: python universidades/ec_d_karlsru01/scraper_ec_d_karlsru01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402
import discover_ec_d_karlsru01 as disc  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_karlsru01"
SAMPLE = ["M-MATH-102859", "M-MACH-102572", "M-MACH-102563", "M-MACH-102565", "M-MACH-102820", "M-MACH-104494"]
LABELS = ["Leistungspunkte", "Notenskala", "Turnus", "Dauer", "Sprache", "Level", "Version", "Pflichtbestandteile", "Wahlinformationen",
          "Erfolgskontrolle(n)", "Voraussetzungen", "Qualifikationsziele", "Inhalt", "Zusammensetzung der Modulnote", "Anmerkungen",
          "Arbeitsaufwand", "Lehr- und Lernformen", "Empfehlungen", "Literaturhinweise", "Literatur", "Wahlpflichtbestandteile", "Zusatzleistungen",
          "Modellierte Voraussetzungen", "Bestandteil von", "Verantwortung", "Einrichtung", "Modulbestandteile"]
SECTIONS = {"Qualifikationsziele": "Qualifikationsziele (Learning outcomes)", "Inhalt": "Inhalt (Contents)", "Erfolgskontrolle(n)": "Erfolgskontrolle (Assessment)",
            "Voraussetzungen": "Voraussetzungen (Prerequisites)", "Literatur": "Literatur", "Literaturhinweise": "Literatur", "Empfehlungen": "Empfehlungen",
            "Arbeitsaufwand": "Arbeitsaufwand", "Lehr- und Lernformen": "Lehr- und Lernformen", "Zusammensetzung der Modulnote": "Zusammensetzung der Modulnote",
            "Anmerkungen": "Anmerkungen", "Pflichtbestandteile": "Pflichtbestandteile", "Wahlpflichtbestandteile": "Wahlpflichtbestandteile",
            "Wahlinformationen": "Wahlinformationen", "Modulbestandteile": "Modulbestandteile"}
META_KEYS = ["Leistungspunkte", "Turnus", "Dauer", "Sprache", "Level"]
DROP = ("Verantwortung", "Einrichtung", "Bestandteil von", "Notenskala", "Version", "Modellierte Voraussetzungen")


def to_markdown(m: dict) -> tuple[str, dict]:
    body = [l.rstrip() for l in m["body"]]
    md = [f"# {m['name']}", "", f"Modul-Code: {m['code']}", ""]
    meta, sec, cur, buf = {}, [], None, []
    i = 0
    # cabecera: saltar 'Verantwortung:' (nombres), 'Einrichtung:' y su continuacion hasta la primera etiqueta de la lista
    while i < len(body):
        l = body[i].strip()
        key = l.split(":")[0] if ":" in l and l.split(":")[0] in LABELS else l
        if l in LABELS or key in ("Verantwortung", "Einrichtung", "Bestandteil von"):
            break
        i += 1
    cur_key = None
    for l in body[i:]:
        s = l.strip()
        if not s:
            continue
        key = s.split(":")[0] if s.split(":")[0] in ("Verantwortung", "Einrichtung", "Bestandteil von") else s
        if key in LABELS:
            cur_key = key
            if key in SECTIONS:
                sec.append([SECTIONS[key], []])
            continue
        if cur_key in DROP or key in DROP:
            continue
        if cur_key in META_KEYS:
            meta.setdefault(cur_key, []).append(s); continue
        if cur_key in ("Pflichtbestandteile", "Wahlpflichtbestandteile", "Wahlinformationen", "Modulbestandteile"):
            s = re.sub(r"(\d+(?:[.,]\d+)? LP)\s+.*$", r"", s)  # quita el apellido del docente
        if cur_key in SECTIONS and sec:
            sec[-1][1].append(("- " + s.lstrip("•-– ").strip()) if s[0] in "•–" else s)
    if meta:
        md += ["| " + " | ".join(k for k in META_KEYS if k in meta) + " |", "|" + "---|" * len([k for k in META_KEYS if k in meta]),
               "| " + " | ".join(" ".join(meta[k]) for k in META_KEYS if k in meta) + " |", ""]
    for t, ls in sec:
        txt = "\n".join(ls).strip()
        if txt:
            md += [f"## {t}", "", re.sub(r"(?<![\n-])\n(?![\n-])", " ", txt) if False else txt, ""]
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(h):
        r = re.search(rf"## {re.escape(h)}.*?\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(r and r.group(1).strip() and r.group(1).strip().lower() not in ("keine", "keine."))
    found = {"contents": has("Inhalt"), "learning_outcomes": has("Qualifikationsziele"), "assessment": has("Erfolgskontrolle"),
             "bibliography": has("Literatur"), "prerequisites": has("Voraussetzungen")}
    return out, found


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
    mods = {m["code"]: m for m in disc.modules(disc.get_lines(client))}
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in mods:
            print(f"SKIP {c}"); continue
        try:
            md, found = to_markdown(mods[c])
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} chars {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1; print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
