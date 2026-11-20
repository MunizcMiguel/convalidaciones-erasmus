"""Fase 2 - FH JOANNEUM Fahrzeugtechnik: cada asignatura de la pagina de Curriculum (HTML) -> Markdown.

Uso: python universidades/ec_a_graz09__mec/scraper_ec_a_graz09__mec.py [--sample N | --all | --codes C1 C2]
Solo hay descripcion breve de contenidos; sin profesorado en la fuente.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from discover_ec_a_graz09__mec import URL_PLAN, parse  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_a_graz09__mec"
SAMPLE = ["220587103", "220587104", "220587108"]
NL = chr(10)


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
    courses = {k["code"]: k for k in parse(client.get_text(URL_PLAN))}
    fails = 0
    for c in codes:
        r, k = rows.get(c), courses.get(c)
        if not r or not k or r["tipo_fuente"] == "sin_guia":
            print(f"omitido {c}: sin_guia")
            continue
        try:
            body = [f"# {k['title']} ({k['code']})", "",
                    f"- Type: {k['kind']}", f"- Language of instruction: {k['lang']}", f"- ECTS: {k['ects']}", f"- SWS: {k['sws']}", f"- Semester: {k['sem']}", "",
                    "## Description (Curriculum)", "", k["desc"], ""]
            found = {"contents": bool(k["desc"]), "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
            write_markdown(SLUG, r, NL.join(body), found)
            print(f"ok {c} {len(k['desc'])} caracteres")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
