"""Fase 2 - TH Bingen Maschinenbau B.Eng.: cada modulo del Modulhandbuch (PDF compartido) -> Markdown.
Uso: python universidades/ec_d_bingen01/scraper_ec_d_bingen01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402
import discover_ec_d_bingen01 as disc  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_bingen01"
SAMPLE = ["B-MB-MAT1", "B-MB-TEM1", "B-MB-MAE1", "B-MB-FEME", "B-MB-ROBO", "B-MB-PSPM"]
SEC = re.compile(r"^(\d{1,2})\s+(Lernergebnisse|Inhalte|Lehrform(?:en)?|Lehr- und Lernformen|Teilnahmevoraussetzungen|Pr[uü]fungsformen|Voraussetzungen f[uü]r die Vergabe.*|Verwendung des Moduls|Stellenwert der Note.*|Modulbeauftragte.*|Sonstige Informationen|Lehrveranstaltungen)\s*$")
TITLES = {"Lernergebnisse": "Lernergebnisse (Learning outcomes)", "Inhalte": "Inhalte (Contents)", "Teilnahmevoraussetzungen": "Teilnahmevoraussetzungen (Prerequisites)",
          "Prüfungsformen": "Prüfungsformen (Assessment)", "Pruefungsformen": "Prüfungsformen (Assessment)", "Sonstige Informationen": "Sonstige Informationen und Literatur"}


def to_markdown(m: dict) -> tuple[str, dict]:
    body = m["body"]
    head_end = next((i for i, l in enumerate(body) if SEC.match(l.strip()) and "Lehrveranstaltungen" not in l), len(body))
    hdr = "\n".join(body[:head_end])
    lp = re.search(r"Leistungs-\s*\n\s*punkte\s*\n\s*(\S+)", hdr)
    ab = re.search(r"Arbeitsbelastung\s*\n\s*([^\n]+)", hdr)
    sem = re.findall(r"(\d)\.\s*Semester\s*\n\s*\((\S+)\)", hdr)
    md = [f"# {m['name']}", "", f"Modul-Code: {m['code']}"]
    if lp:
        md.append(f"Leistungspunkte: {lp.group(1)}")
    if ab:
        md.append(f"Arbeitsbelastung: {ab.group(1).strip()}")
    if sem:
        md.append("Studiensemester: " + "; ".join(f"{a}. Semester ({b})" for a, b in sem))
    sec, cur, skip = [], None, False
    for l in body[head_end:]:
        s = l.strip()
        mm = SEC.match(s)
        if mm:
            name = mm.group(2)
            skip = name.startswith("Modulbeauftragte") or name == "Lehrveranstaltungen"
            cur = None if skip else [TITLES.get(name, name), []]
            if cur:
                sec.append(cur)
            continue
        if skip or not cur or not s:
            continue
        cur[1].append(s)
    for t, ls in sec:
        txt = []
        for s in ls:
            if re.match(r"^[-•]\s", s):
                txt.append("- " + s[2:].strip())
            elif txt and txt[-1].startswith("- ") and l_cont(s):
                txt[-1] += " " + s
            else:
                txt.append(s)
        md += ["", f"## {t}", "", "\n".join(txt)]
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(h):
        r = re.search(rf"## {re.escape(h)}.*?\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(r and r.group(1).strip() and not re.match(r"(keine|formal: keine)\.?\s*$", r.group(1).strip(), re.I))
    found = {"contents": has("Inhalte"), "learning_outcomes": has("Lernergebnisse"), "assessment": has("Prüfungsformen"),
             "bibliography": "Literatur" in out and bool(re.search(r"Literatur:?\s*\n-", out)), "prerequisites": has("Teilnahmevoraussetzungen")}
    return out, found


def l_cont(s: str) -> bool:
    return not re.match(r"^(Literatur|Sprache|Formal|Inhaltlich)\b", s)


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
