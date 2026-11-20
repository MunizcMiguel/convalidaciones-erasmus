"""Fase 2 - Gdynia Maritime (B.Sc. Electrotechnics): bloque de cada asignatura de los PDF 'courses in English' -> Markdown.
Uso: python universidades/ec_pl_gdynia01/scraper_ec_pl_gdynia01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))

from discover_ec_pl_gdynia01 import PDFS, parse_pdf  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, safe_name, write_markdown  # noqa: E402

SLUG = "ec_pl_gdynia01"
HERE = Path(__file__).parent
SAMPLE = ["UMG-ENGLISH", "UMG-FUNDAMENTALS_OF_ELECTROTECHNICS_I", "UMG-ELECTRICAL_MACHINES_I", "UMG-POWER_CONDITIONING_SYSTEMS", "UMG-COMPUTER_AREA_NETWORK"]


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
        pick = [r for r in rows if r["codigo_asignatura"] in SAMPLE]
        rows = (pick + [r for r in rows if r not in pick])[: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    parsed = {term: {("UMG-" + safe_name(i["title"]).upper()): i for i in parse_pdf(http.get_file(u))} for term, u in PDFS.items()}
    fails = 0
    for r in rows:
        term = "summer" if "(summer)" in r["curso_semestre"] else "fall"
        code = r["codigo_asignatura"].removesuffix("_summer").removesuffix("_fall")
        it = parsed[term].get(code)
        if not it or not it["desc"]:
            print(f"FAIL {r['codigo_asignatura']}: sin descripcion")
            fails += 1
            continue
        body = (f"# {it['title']}\n\n- ECTS: {it['ects']}\n- Plan semester: {it['sem']} ({term} term)\n\n## Course description\n\n{it['desc']}")
        write_markdown(SLUG, r, body, {"contents": True, "learning_outcomes": False, "assessment": False,
                                       "bibliography": False, "prerequisites": False})
        print(f"ok   {r['codigo_asignatura']}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
