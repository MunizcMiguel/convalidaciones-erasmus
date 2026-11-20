"""Fase 2 - UBB Cluj (Computer Science, English): «Syllabus» (fisa disciplinei) PDF -> Markdown.
Uso: python universidades/ec_ro_clujnap01/scraper_ec_ro_clujnap01.py [--sample N | --all | --codes C1 C2]
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

SLUG = "ec_ro_clujnap01"
HERE = Path(__file__).parent
# texto rotado (etiquetas laterales de la plantilla) que pdfplumber devuelve invertido
ROTATED = re.compile(r"^(egdelwonK|sllikS|lanoisseforP|laitnesse/lanoisseforP|seicnetepmoc|lasrevsnarT|ytilibisnopseR.*|dna|:ymonotua|lanoitcnuF|laitnesse)$")
PERSONAL = re.compile(r"^(2\.[23]\.? ?(Course|Seminar)[^\n]*coordinator\b.*|.*\bcoordinator\b.*(Prof|Lect|Assoc|Assist|Dr\.).*)$", re.I)
# secciones numeradas de la fisa: 1. ... 11.
SECTION = re.compile(r"^(\d{1,2}(?:\.[12])?)\.?\s+((?:Information regarding|Total estimated|Prerequisites|Conditions|Spec[ie]fic competen|Learning outcomes|Objectives of|Content|Corroborat|Evaluation|Labels)[^\n]*)$", re.I)
BLOCKS = {
    "contents": re.compile(r"^8\. Content", re.I),
    "learning_outcomes": re.compile(r"^(6\.|7\.)", re.I),
    "assessment": re.compile(r"^10\. Evaluation", re.I),
    "bibliography": None,
    "prerequisites": re.compile(r"^4\. Prerequisites", re.I),
}
SAMPLE_PATTERNS = ["Mathematical analysis", "Programming fundamentals", "Data structures", "Databases|Operating", "Artificial|Machine|Distributed|Software", "thesis|license|diploma"]


def fix_font(text: str) -> str:
    """La fuente del PDF mapea la ligadura 'f' a 'X'/'P' (efXicient, SpeciPic, Xinal): se revierte entre minusculas."""
    text = re.sub(r"(?<=[a-z])[XP](?=[a-z])", "f", text)
    return re.sub(r"X(?=[a-z]{2,})", "f", text)


def to_markdown(text: str, entry: dict) -> tuple[str, dict]:
    text = fix_font(text)
    out = [f"# {entry['nombre_asignatura']}"]
    cur_title, found = "", {k: False for k in BLOCKS}
    sec_text: dict[str, list[str]] = {}
    order: list[str] = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or ROTATED.match(ln) or PERSONAL.match(ln):
            continue
        if ln.upper() == "SYLLABUS" or re.match(r"^University year \d{4}", ln):
            continue
        m = SECTION.match(ln)
        if m:
            cur_title = ln
            order.append(ln)
            sec_text[cur_title] = []
            continue
        if cur_title:
            sec_text[cur_title].append(ln)
    for t in order:
        body = "\n".join(sec_text[t]).strip()
        out.append(f"## {t}\n\n{body}" if body else f"## {t}")
        for k, rx in BLOCKS.items():
            if rx is not None and rx.match(t) and body and body not in ("-", "n/a"):
                found[k] = True
    found["assessment"] = found["assessment"] or bool(re.search(r"Percentage of final grade|Evaluation criteria", "\n".join(out)))
    found["bibliography"] = bool(re.search(r"^Bibliography\s*$\n+\S", "\n".join(out), re.M))
    return "\n\n".join(out), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = [r for r in cat["asignaturas"] if r["tipo_fuente"] != "sin_guia"]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        pick, seen = [], set()
        for pat in SAMPLE_PATTERNS:
            for r in rows:
                if re.search(pat, r["nombre_asignatura"], re.I) and r["codigo_asignatura"] not in seen:
                    pick.append(r)
                    seen.add(r["codigo_asignatura"])
                    break
        rows = (pick + [r for r in rows if r["codigo_asignatura"] not in seen])[: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for r in rows:
        try:
            with pdfplumber.open(http.get_file(r["url_guia_docente"])) as pdf:
                text = "\n".join((p.extract_text() or "") for p in pdf.pages)
            md, found = to_markdown(text, r)
            write_markdown(SLUG, r, md, found)
            print(f"ok   {r['codigo_asignatura']} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {r['codigo_asignatura']}: {e}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
