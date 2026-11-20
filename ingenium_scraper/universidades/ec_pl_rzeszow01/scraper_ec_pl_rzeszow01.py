"""Fase 2 - PRz: oferta Erasmus en inglés (WBMiL 2026), PDF compartido; un Markdown por asignatura ERAnn-*.
Las filas S{n}-... (plan 23/24 en polaco) son sin_guia y se omiten.
Uso: python universidades/ec_pl_rzeszow01/scraper_ec_pl_rzeszow01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402
from discover_ec_pl_rzeszow01 import erasmus_rows, slug  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_rzeszow01"
SAMPLE = ["ERA47-theoretical-mechanics-i", "ERA34-mechanics-of-materials", "ERA14-dynamics-of-machines", "ERA49-thermodynamics", "ERA52-diploma-seminar"]


def tidy(t: str) -> str:
    """Une líneas partidas por el PDF; conserva viñetas '- ' y párrafos."""
    out: list[str] = []
    for ln in (x.strip() for x in t.splitlines()):
        if not ln:
            continue
        if ln.startswith(("- ", "• ", "– ")) or not out:
            out.append(ln)
        else:
            out[-1] += " " + ln
    return "\n\n".join(re.sub(r"^[•–] ", "- ", x) for x in out)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"] if r["tipo_fuente"] != "sin_guia"}
    codes = a.codes or (list(rows) if a.all else [c for c in SAMPLE if c in rows][: a.sample or 5])
    src = {f"ERA{r['no']:02d}-{slug(re.sub(chr(92)+'s+', ' ', r['name']))}": r for r in erasmus_rows(PoliteClient(cache_dir=HERE / "raw_cache"))}
    bad = 0
    for code in codes:
        e, r = rows.get(code), src.get(code)
        if not e or not r:
            bad += 1; print(code, "FALLO no está en catálogo/PDF"); continue
        desc = tidy(r["desc"])
        if not desc:
            bad += 1; print(code, "FALLO descripción vacía"); continue
        body = f"# {e['nombre_asignatura']}\n\n- ECTS: {r['ects']}\n- Source: Erasmus incoming course offer, Faculty of Mechanical Engineering and Aeronautics (2026), pp. {e['paginas_pdf']}\n\n## Course description\n\n{desc}\n"
        if r["rem"].strip():
            body += f"\n## Remarks\n\n{tidy(r['rem'])}\n"
        write_markdown(SLUG, e, body, {"contents": True, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False})
        print(code, "ok", len(desc))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
