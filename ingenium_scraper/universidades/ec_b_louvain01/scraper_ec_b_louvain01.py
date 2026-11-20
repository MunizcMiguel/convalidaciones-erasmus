"""Fase 2 - UCLouvain Bachelor in Engineering (FSA1BA): ficha HTML por UE -> Markdown.
Uso: python universidades/ec_b_louvain01/scraper_ec_b_louvain01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_b_louvain01"
SAMPLE = ["LEPL1101", "LEPL1201", "LEPL1401", "LEPL1501", "LEPL1503", "LMECA1100", "LFSAB1503", "LEPL1109"]
SECTIONS = {"Main themes": "Main themes", "Learning outcomes": "Learning outcomes", "Content": "Content", "Teaching methods": "Teaching methods",
            "Evaluation methods": "Evaluation methods", "Online resources": "Online resources", "Bibliography": "Bibliography",
            "Teaching materials": "Teaching materials", "Other infos": "Other information", "Prerequisites": "Prerequisites", "Prerequisite": "Prerequisites",
            "Contribution of the course to the program objectives": "Contribution to program objectives",
            "Specific learning outcomes of the course": "Specific learning outcomes"}
STOP = {"Faculty or entity", "Programmes / formations proposant cette unité d'enseignement (UE)", "Programmes / formations proposant cette unité d'enseignement"}


def to_markdown(entry: dict, html: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    m = s.find("main") or s.body
    for z in m(["script", "style", "nav", "form"]):
        z.decompose()
    lines = [l for l in m.get_text("\n", strip=True).split("\n") if l.strip()]
    md = [f"# {entry['nombre_asignatura']}", ""]
    # cabecera: creditos/horas/quarter/idioma; se salta 'Teacher(s)' hasta 'Language'
    i, cur = 0, None
    head = []
    while i < len(lines) and lines[i] != "Main themes" and lines[i] not in SECTIONS:
        if lines[i].startswith("Teacher"):
            while i < len(lines) and not lines[i].startswith("Language"):
                i += 1
            continue
        head.append(lines[i]); i += 1
    md += [f"- {h}" for h in head[1:6] if h.strip()] + [""]
    while i < len(lines):
        l = lines[i]
        if l in STOP or l.startswith("Programmes / formations"):
            break
        if l in SECTIONS:
            cur = SECTIONS[l]; md += ["", f"## {cur}", ""]
        else:
            md.append(l if not l.startswith(("•", "-")) else "- " + l.lstrip("•- "))
        i += 1
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(h):
        r = re.search(rf"## {h}\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(r and r.group(1).strip() and not re.match(r"(?i)\s*(no|none|n/a)\.?\s*$", r.group(1).strip()))
    found = {"contents": has("Content") or has("Main themes"), "learning_outcomes": has("Specific learning outcomes") or has("Learning outcomes"),
             "assessment": has("Evaluation methods"), "bibliography": has("Bibliography"), "prerequisites": has("Prerequisites")}
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
