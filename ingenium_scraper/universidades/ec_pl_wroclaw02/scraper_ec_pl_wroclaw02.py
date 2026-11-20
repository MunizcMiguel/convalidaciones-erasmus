"""Fase 2 - PWr W10: PDF compartido de fichas (SUBJECT CARD) -> raw_markdown/{codigo}.md
Uso: python universidades/ec_pl_wroclaw02/scraper_ec_pl_wroclaw02.py [--sample N | --all | --codes C1 C2]
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

HERE = Path(__file__).parent
SLUG = "ec_pl_wroclaw02"
SAMPLE = ["FZP001067", "MAP001091", "MMM031250", "MMR031001", "HMH100035BK"]
H2 = ["PREREQUISITES RELATING TO KNOWLEDGE, SKILLS AND OTHER COMPETENCES", "SUBJECT OBJECTIVES", "SUBJECT EDUCATIONAL EFFECTS", "PROGRAMME CONTENT",
      "TEACHING TOOLS USED", "PRIMARY AND SECONDARY LITERATURE", "PRIMARY LITERATURE", "SECONDARY LITERATURE"]
CUT = ("MATRIX OF CORRELATION", "SUBJECT SUPERVISOR")  # matriz de correlación y responsable (personal): se descartan
_pages: dict[str, list[str]] = {}


def card_text(path: Path, rng: str) -> str:
    key = str(path)
    if key not in _pages:
        with pdfplumber.open(path) as pdf:
            _pages[key] = [(pg.extract_text() or "") for pg in pdf.pages]
    a, b = (int(x) for x in rng.split("-"))
    return "\n".join(_pages[key][a - 1:b])


def to_markdown(text: str, name: str) -> tuple[str, dict]:
    lines = [l.rstrip() for l in text.split("\n") if not re.fullmatch(r"\s*\d+/\d+\s*", l)]
    out, skip = [], False
    for l in lines:
        s = l.strip()
        if any(s.startswith(c) for c in CUT):
            break
        if s in ("Faculty of Mechanical Engineering", "SUBJECT CARD"):
            continue
        if s in H2:
            out.append("\n## " + s.capitalize() + "\n")
        elif re.match(r"EVALUATION OF SUBJECT EDUCATIONAL EFFECTS ACHIEVEMENT", s):
            out.append("\n## " + s.capitalize() + "\n")
        elif re.match(r"Form of classes [–-] ", s):
            out.append("\n### " + s + "\n")
        elif re.match(r"(Lecture|Classes|Laboratory|Project|Seminar)\s*$", s) and False:
            out.append(s)
        else:
            out.append(s)
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    body = f"# {name}\n\n" + body
    low = body.lower()
    found = {
        "contents": "## programme content" in low, "learning_outcomes": "## subject educational effects" in low or "## subject objectives" in low,
        "assessment": "## evaluation of subject educational effects" in low, "bibliography": "literature" in low and bool(re.search(r"\[\d+\]", body)),
        "prerequisites": bool(re.search(r"## prerequisites[^\n]*\n+(?!\s*## )\S", body, re.I)),
    }
    return body, found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)["asignaturas"]
    if a.codes:
        sel = [e for e in cat if e["codigo_asignatura"] in a.codes]
    elif a.all:
        sel = cat
    else:
        sel = [e for e in cat if e["codigo_asignatura"] in SAMPLE][: a.sample if a.sample is not None else 5]
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"], "sin_guia")
            continue
        try:
            body, found = to_markdown(card_text(c.get_file(e["url_guia_docente"]), e["paginas_pdf"]), e["nombre_asignatura"])
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
