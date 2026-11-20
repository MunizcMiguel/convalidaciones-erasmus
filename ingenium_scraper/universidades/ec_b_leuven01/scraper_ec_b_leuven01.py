"""Fase 2 - KU Leuven Ingenieurswetenschappen: ficha HTML por OPO -> Markdown (neerlandes).
Uso: python universidades/ec_b_leuven01/scraper_ec_b_leuven01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_b_leuven01"
SAMPLE = ["H01A0B", "H01K9A", "H01A4B", "H01A2B", "H01G9A"]
HEAD = {"Doelstellingen opleidingsonderdeel": "Doelstellingen (leerdoelen)", "Course Objectives": "Course objectives",
        "Begintermen": "Begintermen (vereisten)", "Entry requirements": "Entry requirements",
        "Onderwijsleeractiviteiten": "Onderwijsleeractiviteiten", "Learning activities": "Learning activities",
        "Inhoud": "Inhoud", "Content": "Content", "Toelichting onderwijstaal": "Toelichting onderwijstaal",
        "Studiemateriaal": "Studiemateriaal", "Course materials": "Course materials", "Toelichting werkvorm": "Toelichting werkvorm",
        "Format": "Format", "Evaluatieactiviteiten": "Evaluatieactiviteiten", "Evaluation": "Evaluation",
        "Evaluation activities": "Evaluation activities", "Assessment activities": "Assessment activities", "Toelichting": "Toelichting evaluatie", "Explanation": "Explanation",
        "Toelichting bij herkansen": "Toelichting bij herkansen", "Information about retaking exams": "Information about retaking exams",
        "Examenmoment": "Examenmoment", "Beoordelingsschaal": "Beoordelingsschaal", "Marking scale": "Marking scale"}
SKIP_UNTIL = {"Plaats in het onderwijsaanbod", "Is included in these programmes", "Toleranties", "Tolerances", "Translations",
              "Volgtijdelijkheidsvoorwaarden", "Course prerequisites", "Wat betekenen de symbolen hieronder?"}
RESUME = set(HEAD)


def to_markdown(entry: dict, html: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    for z in s(["script", "style", "nav", "header", "footer", "button"]):
        z.decompose()
    lines = [re.sub(r"[ \t\xa0]+", " ", l).strip() for l in s.get_text("\n", strip=True).split("\n")]
    lines = [l for l in lines if l]
    # nombres del profesorado: lineas entre el codigo '(B-TM-...)' y los 'studiepunten' del encabezado, y 'Docenten'
    names = set()
    try:
        a = next(i for i, l in enumerate(lines) if re.match(r"\(B-KUL-\w+\)", l))
        b = next(i for i, l in enumerate(lines) if "studiepunten" in l or "ECTS" in l or "credits" in l.lower())
        for l in lines[a + 1:b]:
            for part in re.split(r"[|]", l):
                part = part.strip(" ()")
                if part and part not in ("Coördinator", "Coordinator"):
                    names.add(part)
    except StopIteration:
        pass
    md = [f"# {entry['nombre_asignatura']}", "", f"Studiepunten (ECTS): {entry['creditos_ects']:g}" if entry.get("creditos_ects") else ""]
    skip, strict, seen_blocks, cur, buf = False, False, set(), None, []

    def flush():
        nonlocal buf, cur
        if cur is not None:
            txt = "\n".join(buf).strip()
            key = (cur, hashlib.md5(txt.encode()).hexdigest())
            if txt and key not in seen_blocks:
                seen_blocks.add(key)
                md.extend(["", f"## {cur}", "", txt])
        buf = []

    start = next((i for i, l in enumerate(lines) if l in ("Doelstellingen opleidingsonderdeel", "Course Objectives") and i > 5), 0)
    for l in lines[start:]:
        if l.startswith("Follow ") or l.startswith("Volg "):
            break
        if l in SKIP_UNTIL or l.startswith("Course prerequisites"):
            flush(); cur = None; skip = True; strict = True; continue
        if l in HEAD and (not strict or l in ("Learning activities", "Onderwijsleeractiviteiten")):
            flush(); cur = HEAD[l]; skip = False; strict = False; continue
        if skip or cur is None:
            continue
        if l in names or l == "|" or re.fullmatch(r"(counter_\d|Alle blokken openklappen)", l):
            continue
        if re.match(r"(Beschikbaar|Docenten?)$", l):
            continue
        buf.append(re.sub(r"^-\s+", "- ", l))
    flush()
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(h):
        r = re.search(rf"## {re.escape(h)}\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(r and r.group(1).strip() and r.group(1).strip().lower() not in ("geen", "geen."))
    found = {"contents": has("Inhoud") or has("Content") or has("Onderwijsleeractiviteiten") or has("Learning activities"),
             "learning_outcomes": has("Doelstellingen (leerdoelen)") or has("Course objectives"),
             "assessment": has("Assessment activities") or has("Evaluatieactiviteiten") or has("Evaluation") or has("Evaluation activities"),
             "bibliography": has("Studiemateriaal") or has("Course materials"),
             "prerequisites": has("Begintermen (vereisten)") or has("Entry requirements")}
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
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia":
            print(f"SKIP {c}"); continue
        try:
            md, found = to_markdown(r, client.get_text(r["url_guia_docente"]))
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} chars {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1; print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
