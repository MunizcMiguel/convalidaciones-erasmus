"""Fase 2 - Konya Teknik Universitesi, Makine Muhendisligi: bloque 'Dersin Adi' del PDF compartido de contenidos -> raw_markdown/{codigo}.md
Uso: python universidades/ec_tr_konya05/scraper_ec_tr_konya05.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402
from discover_ec_tr_konya05 import best_block, parse_blocks  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_konya05"
SAMPLE = ["1210102", "1210302", "1210602", "1210776", "1210734"]


def block_to_markdown(b: dict, title: str) -> tuple[str, dict]:
    lines = b["text"].split("\n")
    info = lines[2].strip() if len(lines) > 2 else ""
    m = re.match(r"^(\d+)\s+(\d{7,8})(?:\s*/\s*(\d{7,8}))?\s+(.+?)\s+(\d+)\s*$", info)
    rest = lines[3:]
    md = [f"# {title}"]
    if m:
        md.append("## Course information\n\n| Term | Course code (NÖ/İÖ) | Theory / practice hours | ECTS (in the content document) |\n|---|---|---|---|\n"
                  f"| {m.group(1)} | {m.group(2)}{('/' + m.group(3)) if m.group(3) else ''} | {m.group(4)} | {m.group(5)} |")
    # "Dersin Amacı": desde la linea que empieza por 'Dersin' hasta la cabecera de la tabla semanal / 'Ders İçeriği'
    k = next((i for i, l in enumerate(rest) if re.match(r"^(HAFTA|Ders İçeriği|HAFTA DERS)", l)), len(rest))
    aim = [re.sub(r"^Dersin\s+", "", l) for l in rest[:k]]
    aim = [re.sub(r"^Amacı\s*", "", l) for l in aim]
    aim_txt = " ".join(x.strip() for x in aim if x.strip())
    if aim_txt:
        md.append("## Dersin Amacı (course aim)\n\n" + aim_txt)
    content = [re.sub(r"^Ders İçeriği\s+", "", l) for l in rest[k:]]
    content_txt = "\n".join(content).strip()
    if content_txt:
        md.append("## Ders içeriği / haftalık plan (course contents, weekly plan; KAYNAK = references)\n\n" + content_txt)
    body = "\n\n".join(md)
    low = body.lower()
    found = {"contents": bool(content_txt), "learning_outcomes": False, "assessment": "ara sınav" in low and False, "bibliography": "kaynak" in low and len(content_txt) > 0,
             "prerequisites": False}
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
        sel = [e for e in cat if e["codigo_asignatura"] in SAMPLE][: (a.sample if a.sample is not None else 5)]
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf_url = next((e["url_guia_docente"] for e in cat if e.get("url_guia_docente")), None)
    blocks = best_block(parse_blocks(c.get_file(pdf_url))) if pdf_url else {}
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"], "sin_guia")
            continue
        try:
            b = blocks[e["codigo_asignatura"]]
            body, found = block_to_markdown(b, e["nombre_asignatura"])
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
