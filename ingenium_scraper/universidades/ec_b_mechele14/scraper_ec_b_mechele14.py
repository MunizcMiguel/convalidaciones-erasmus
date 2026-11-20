"""Fase 2 - Thomas More Elektronica-ICT: ficha HTML por OPO -> Markdown (neerlandes).
Uso: python universidades/ec_b_mechele14/scraper_ec_b_mechele14.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, hashlib, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_b_mechele14"
SAMPLE = ["YT0662", "YT0664", "YT0292", "YT0737", "YT0569"]
HEAD = {"Doelstellingen opleidingsonderdeel": "Doelstellingen (leerdoelen)", "Begintermen": "Begintermen (vereisten)",
        "Onderwijsleeractiviteiten": "Onderwijsleeractiviteiten", "Inhoud": "Inhoud", "Toelichting onderwijstaal": "Toelichting onderwijstaal",
        "Studiemateriaal": "Studiemateriaal", "Toelichting werkvorm": "Toelichting werkvorm", "Evaluatieactiviteiten": "Evaluatieactiviteiten",
        "Toelichting": "Toelichting evaluatie", "Toelichting bij herkansen": "Toelichting bij herkansen", "Examenmoment": "Examenmoment",
        "Beoordelingsschaal": "Beoordelingsschaal"}
SKIP_UNTIL = {"Plaats in het onderwijsaanbod", "Toleranties", "Translations", "Wat betekenen de symbolen hieronder?"}
RESUME = set(HEAD) | {"Onderwijsleeractiviteiten"}


def to_markdown(entry: dict, html: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    for z in s(["script", "style", "nav", "header", "footer", "button"]):
        z.decompose()
    lines = [re.sub(r"[ \t\xa0]+", " ", l).strip() for l in s.get_text("\n", strip=True).split("\n")]
    lines = [l for l in lines if l]
    # nombres del profesorado: lineas entre el codigo '(B-TM-...)' y los 'studiepunten' del encabezado, y 'Docenten'
    names = set()
    try:
        a = next(i for i, l in enumerate(lines) if re.match(r"\(B-TM-\w+\)", l))
        b = next(i for i, l in enumerate(lines) if "studiepunten" in l or l == "studiepunten")
        for l in lines[a + 1:b]:
            for part in re.split(r"[|]", l):
                part = part.strip(" ()")
                if part and part not in ("Coördinator", "Coordinator"):
                    names.add(part)
    except StopIteration:
        pass
    md = [f"# {entry['nombre_asignatura']}", "", f"Studiepunten (ECTS): {entry['creditos_ects']:g}" if entry.get("creditos_ects") else ""]
    skip, seen_blocks, cur, buf = False, set(), None, []

    def flush():
        nonlocal buf, cur
        if cur is not None:
            txt = "\n".join(buf).strip()
            key = (cur, hashlib.md5(txt.encode()).hexdigest())
            if txt and key not in seen_blocks:
                seen_blocks.add(key)
                md.extend(["", f"## {cur}", "", txt])
        buf = []

    start = next((i for i, l in enumerate(lines) if l == "Doelstellingen opleidingsonderdeel"), 0)
    for l in lines[start:]:
        if l.startswith("Follow ") or l.startswith("Volg "):
            break
        if l in SKIP_UNTIL:
            flush(); cur = None; skip = True; continue
        if l in HEAD:
            flush(); cur = HEAD[l]; skip = False; continue
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
    found = {"contents": has("Inhoud") or has("Onderwijsleeractiviteiten"), "learning_outcomes": has("Doelstellingen (leerdoelen)"),
             "assessment": has("Evaluatieactiviteiten"), "bibliography": has("Studiemateriaal"), "prerequisites": has("Begintermen (vereisten)")}
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
