"""Fase 2 - Staffordshire (BEng EEE): descripcion del modulo (modal de la ficha del curso) -> Markdown.
Uso: python universidades/ec_uk_staffor02/scraper_ec_uk_staffor02.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

SLUG = "ec_uk_staffor02"
HERE = Path(__file__).parent
URL = "https://www.staffs.ac.uk/course/electrical-electronic-engineering-beng"
SAMPLE = ["ENGG43003", "ELEC43014", "ELEC53006", "ENGG63002", "ELEC63004"]


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
        pick = [r for r in rows if r["codigo_asignatura"] in SAMPLE] or rows
        rows = (pick + [r for r in rows if r not in pick])[: a.sample]
    soup = BeautifulSoup(PoliteClient(cache_dir=HERE / "raw_cache").get_text(URL), "lxml")
    modals = {m["data-modal"]: m for m in soup.select("div.modal[data-modal]")}
    fails = 0
    for r in rows:
        slug = r["url_guia_docente"].split("#modal=")[1]
        m = modals.get(slug)
        if m is None:
            print(f"FAIL {r['codigo_asignatura']}: modal no encontrado"); fails += 1; continue
        paras = [p.get_text(" ", strip=True) for p in m.select(".modal__content p")]
        desc = [p for p in paras if p and not p.startswith("Module code")]
        if not desc:
            print(f"FAIL {r['codigo_asignatura']}: sin descripcion"); fails += 1; continue
        body = (f"# {r['nombre_asignatura']}\n\n- Module code: {r['codigo_asignatura']}\n- Credits: {r['creditos_ects']*2:g} UK credits ({r['creditos_ects']:g} ECTS)\n"
                f"- Level: {r['curso_semestre']}\n\n## Module description\n\n" + "\n\n".join(desc))
        write_markdown(SLUG, r, body, {"contents": True, "learning_outcomes": False, "assessment": False,
                                       "bibliography": False, "prerequisites": False})
        print(f"ok   {r['codigo_asignatura']}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
