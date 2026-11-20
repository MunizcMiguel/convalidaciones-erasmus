"""Fase 2 - TH Deggendorf KI B.Sc.: cada modulo del Modulhandbuch (PDF compartido) -> Markdown.
Uso: python universidades/ec_d_deggend01/scraper_ec_d_deggend01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402
import discover_ec_d_deggend01 as disc  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_deggend01"
SAMPLE = ["KI-01", "KI-02", "KI-09", "KI-21", "KI-25", "KI-36"]
LABELS = {"Qualifikationsziele des Moduls": "Qualifikationsziele (Learning outcomes)", "Inhalt": "Inhalt (Contents)",
          "Lehr- und Lernmethoden": "Lehr- und Lernmethoden", "Besonderes": "Besonderes", "Empfohlene Literaturliste": "Literatur (Bibliography)",
          "Zugangs- bzw. empfohlene Voraussetzungen": "Voraussetzungen (Prerequisites)", "Verwendbarkeit in diesem und in anderen": "Verwendbarkeit",
          "Studiengängen": None, "Voraussetzungen für die Teilnahme": "Voraussetzungen (Prerequisites)"}
HDR_KEEP = ("Semester", "Dauer des Moduls", "Häufigkeit des Moduls", "Art der Lehrveranstaltungen", "Niveau", "SWS", "ECTS", "Workload",
            "Prüfungsarten", "Dauer der Modulprüfung", "Gewichtung der Note", "Unterrichts-/Lehrsprache", "Kursnummer und Kursname")
PERSON = re.compile(r"^\s*(Prof\.|Dr\.|Herr|Frau|[A-Z]\.\s?[A-Z])")


def to_markdown(m: dict) -> tuple[str, dict]:
    body = m["body"]
    first = next((i for i, l in enumerate(body) if l.strip() in LABELS or l.strip().startswith("Qualifikationsziele")), len(body))
    md = [f"# {m['name']}", "", f"Modul-Code: {m['code']}", ""]
    for l in body[:first]:
        s = l.strip()
        if any(s.startswith(k) for k in HDR_KEEP) and not PERSON.match(s):
            md.append(f"- {s}")
        elif md[-1].startswith("- ") and s.startswith(("Selbststudium", "Gesamt")):
            md.append(f"  - {s}")
    sec, cur = [], None
    for l in body[first:]:
        s = l.strip()
        key = s if s in LABELS else ("Qualifikationsziele des Moduls" if s.startswith("Qualifikationsziele des Moduls") else None)
        if key:
            if LABELS.get(key):
                cur = [LABELS[key], []]; sec.append(cur)
            continue
        if cur is None or PERSON.match(s) and cur[0] == "Besonderes":
            continue
        t = re.sub(r"^[o•]\s+", "- ", s)
        cur[1].append(t)
    for t, ls in sec:
        txt = "\n".join(ls).strip()
        if txt:
            md += ["", f"## {t}", "", txt]
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(h):
        r = re.search(rf"## {re.escape(h)}.*?\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(r and r.group(1).strip() and r.group(1).strip().lower() not in ("keine", "keine."))
    found = {"contents": has("Inhalt"), "learning_outcomes": has("Qualifikationsziele"), "assessment": "- Prüfungsarten" in out,
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
