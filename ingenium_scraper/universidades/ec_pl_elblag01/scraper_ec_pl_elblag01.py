"""Fase 2 - ANS Elbląg: fichas Word (.doc con antiword, .docx con python-docx) -> raw_markdown/{codigo}.md
Uso: python universidades/ec_pl_elblag01/scraper_ec_pl_elblag01.py [--sample N | --all | --codes C1 C2]
Requiere `antiword` en PATH (o /mingw64/bin/antiword) solo para las fichas .doc.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import docx  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402
from docx.table import Table  # noqa: E402
from docx.text.paragraph import Paragraph  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_pl_elblag01"
SAMPLE = ["applied_thermodynamics", "3d_scaning", "engineering_materials_i", "sustainable_development", "welding_processes_and_technology"]
STAFF = re.compile(r"coordinator|lecturer|teacher|instructor|supervisor|consultation", re.I)
BLOCKS = {
    "contents": ("curriculum contents", "course contents", "contents"),
    "learning_outcomes": ("learning outcome",),
    "assessment": ("assessment", "grading", "method of assessment", "verification"),
    "bibliography": ("literature", "bibliography", "reading list"),
    "prerequisites": ("entry requirements", "prerequisites"),
}


def norm(t: str) -> str:
    t = t.replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", "\n".join(l.strip() for l in t.split("\n"))).strip()


def blocks_docx(path: Path):
    d = docx.Document(str(path))
    for ch in d.element.body.iterchildren():
        if ch.tag.endswith("}p"):
            t = norm(Paragraph(ch, d).text)
            if t:
                yield ("p", t)
        elif ch.tag.endswith("}tbl"):
            rows = []
            for r in Table(ch, d).rows:
                cells, last = [], None
                for c in r.cells:
                    if c._tc is last:  # celda combinada
                        continue
                    last = c._tc
                    cells.append(norm(c.text))
                rows.append(cells)
            yield ("t", rows)


def blocks_doc(path: Path):
    exe = shutil.which("antiword") or "/mingw64/bin/antiword"
    xml = subprocess.run([exe, "-x", "db", str(path)], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    s = BeautifulSoup(xml, "lxml-xml")
    for el in s.find("chapter").find_all(["para", "informaltable"], recursive=False) if s.find("chapter") else []:
        if el.name == "para" and not el.find("informaltable"):
            t = norm(el.get_text("\n"))
            if t:
                yield ("p", t)
        else:
            for tb in el.find_all("tgroup"):
                rows = [[norm(e.get_text("\n")) for e in r.find_all("entry")] for r in tb.find_all("row")]
                yield ("t", rows)


def cell_md(t: str) -> str:
    return t.replace("\n", "<br>").replace("|", "/")


def to_markdown(path: Path, title: str) -> tuple[str, dict]:
    gen = blocks_doc(path) if path.suffix.lower() == ".doc" else blocks_docx(path)
    md = ["# " + title]
    for kind, v in gen:
        if kind == "p":
            md.append(v)
            continue
        rows = []
        for r in v:
            r = [x for x in r]
            if r and any(STAFF.search(x) and len(x) < 60 for x in r[:1]):
                continue
            if not any(x for x in r):
                continue
            if r and r[0].lower().startswith("to be completed"):
                r = r[1:]
            rows.append(r)
        if not rows:
            continue
        w = max(len(r) for r in rows)
        if w == 1:
            md.append("\n\n".join(("## " if (len(r[0]) < 40 and r[0].isupper()) else "") + r[0] for r in rows))
            continue
        rows = [r + [""] * (w - len(r)) for r in rows]
        md.append("\n".join(["| " + " | ".join(cell_md(x) for x in rows[0]) + " |", "|" + "---|" * w]
                            + ["| " + " | ".join(cell_md(x) for x in r) + " |" for r in rows[1:]]))
    body = "\n\n".join(md)
    low = body.lower()
    found = {k: any(x in low for x in v) for k, v in BLOCKS.items()}
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
    bad = 0
    for e in sel:
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print("SKIP", e["codigo_asignatura"], "sin_guia")
            continue
        try:
            p = Path(c.get_file(e["url_guia_docente"]))
            suffix = Path(e["url_guia_docente"]).suffix
            link = p.with_suffix(suffix)
            if not link.exists():
                shutil.copyfile(p, link)
            body, found = to_markdown(link, e["nombre_asignatura"])
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
