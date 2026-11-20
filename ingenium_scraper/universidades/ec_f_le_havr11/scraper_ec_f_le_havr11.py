"""Fase 2 - Le Havre L3 SPI Mecanique: cada UE del syllabus (PDF compartido) -> Markdown.
Uso: python universidades/ec_f_le_havr11/scraper_ec_f_le_havr11.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402
import discover_ec_f_le_havr11 as disc  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_le_havr11"
SAMPLE = ["L3-S5-hydraulique", "L3-S5-resistance-des-materiaux-2", "L3-S5-anglais-3", "L3-S5-conception-mecanique-1",
          "L3-S6-materiaux-2-caracteristiques-et-procedes", "L3-S6-instrumentation",
          "L3-S6-projet-ou-stage-court-fin-sem-3-semaines-1-5j-hebdo"]
NUMS = re.compile(r"^\s*(\d{1,2}(?:\s+\d{1,3}){0,3}(?:\s+1/\d)*(?:\s+\d)*)\s*$")


def to_markdown(name: str, body: list[str]) -> tuple[str, dict]:
    cut = next((i for i, l in enumerate(body) if re.match(r"^\s*\d{2,3} \d{2,3} \d{2,3}\s*$", l)), len(body))
    txt = " ".join(l.strip() for l in body[:cut])
    txt = re.sub(r"\s+", " ", txt)
    # fila numerica final (ECTS, horas CM/TD/TP, coeficientes de evaluacion)
    m = re.search(r"((?:\d{1,3}\s+){1,5}(?:1/\d\s+)*(?:2/3\s+|1/2\s+)?(?:\d\s*)*|\d+ [A-Za-zé/]+ \d \d)\s*$", txt)
    nums = ""
    mm = re.search(r"\s(\d{1,2}(?: \d{1,3}){1,3}(?: (?:1/\d|\d))*)\s*(?:(?:\d{2,3} ){1,3}\d{2,3})?$", txt)
    if mm:
        nums = mm.group(1); txt = txt[:mm.start()].strip()
    txt = re.sub(r"^OBJECTIFS D.APPRENTISSAGE\s*:?\s*", "", txt, flags=re.I)
    objectives, prereq, biblio = txt, "", ""
    pm = re.search(r"(?:Pr[ée]-?requis|Prérequis)\s*:?\s*", txt, re.I)
    bm = re.search(r"Bibliographie\s*:?\s*", txt, re.I)
    if bm:
        biblio = txt[bm.end():].strip()
        txt_nb = txt[:bm.start()]
    else:
        txt_nb = txt
    if pm and (not bm or pm.start() < bm.start()):
        prereq = txt_nb[pm.end():].strip()
        objectives = txt_nb[:pm.start()].strip(" -")
    elif pm and bm and pm.start() > bm.start():
        prereq = txt[pm.end():].strip(); biblio = txt[bm.end():pm.start()].strip()
        objectives = txt[:bm.start()].strip(" -")
    else:
        objectives = txt_nb.strip(" -")
    md = [f"# {name}", "", "## Objectifs d'apprentissage et contenu", "", objectives]
    if prereq:
        md += ["", "## Prérequis", "", prereq]
    if biblio:
        md += ["", "## Bibliographie", "", biblio]
    if nums:
        md += ["", "## Crédits, volumes horaires et évaluation (ligne du tableau du syllabus)", "",
               f"Valeurs brutes: {nums} (ECTS, heures CM/TD/TP, coefficients CC / partiel / examen terminal, dans l'ordre du tableau).", ""]
    found = {"contents": bool(objectives), "learning_outcomes": bool(objectives), "assessment": bool(nums),
             "bibliography": bool(biblio), "prerequisites": bool(prereq)}
    return "\n".join(md) + "\n", found


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
    segs = {}
    for s in disc.segments(disc.get_pages(client)):
        segs.setdefault(f"L3-S{s['sem']}-" + disc.slug(s["name"]), s)
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in segs:
            print(f"SKIP {c}"); continue
        try:
            md, found = to_markdown(r["nombre_asignatura"], segs[c]["body"])
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} chars {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1; print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
