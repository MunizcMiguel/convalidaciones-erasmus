#!/usr/bin/env python3
"""Fase 2 — Dijon (uB): fichas HTML del catálogo ODF -> Markdown. CLI: --sample N | --all | --codes C1 C2"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "ec_f_dijon01"
SAMPLE_NAMES = ["UE52 - L3SPI-M5MG - Mécanique générale", "UE61 - L3SPI-M6MMC2 - Mécanique des milieux continus 2", "UE9 - L3SPI-M6ANGL - Anglais", "Option B: conception mécanique", "UE37 - Meca4A - Mécanique générale et du  solide"]
DROP = {"Ajouter à la sélection", "Télécharger", "Voir la page complète"}


def table_md(t):
    rows = [[c.get_text(" ", strip=True).replace("|", "/").replace(chr(10), " ") for c in tr.find_all(["th", "td"])] for tr in t.find_all("tr")]
    rows = [r for r in rows if r]
    if not rows:
        return ""
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * n]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def to_md(html):
    s = BeautifulSoup(html, "lxml")
    main = s.find("main")
    h1 = main.find("h1")
    md = [f"# {h1.get_text(' ', strip=True)}"]
    blocks = {"assessment": False, "contents": False, "learning_outcomes": False, "prerequisites": False, "bibliography": False}
    # quitar "Liste des enseignements" y los bloques de ELC hijos (cada ELC tiene su propia ficha)
    for el in main.find_all(["h2", "h3", "p", "ul", "table", "dl", "div"]):
        if el.name == "div" or el.find_parent("table"):
            continue
        if el.name in ("p", "ul", "dl") and el.find_parent(["ul", "dl"]):
            continue
        if el.name == "table":
            md.append(table_md(el))
            if "ametys-mcc" in (el.get("class") or []):
                blocks["assessment"] = True
            continue
        t = el.get_text(" ", strip=True)
        if not t or t in DROP or t == h1.get_text(" ", strip=True):
            continue
        if el.name == "ul":
            lis = [li.get_text(" ", strip=True) for li in el.find_all("li", recursive=False)]
            if lis[0] == "Accueil" or all(x in DROP for x in lis):
                continue
        if el.name == "h2":
            if t in ("ECTS", "Composante"):
                continue
            md.append("## " + t)
        elif el.name == "h3":
            md.append("### " + t)
        elif el.name == "ul":
            md.append("\n".join("- " + li.get_text(" ", strip=True) for li in el.find_all("li", recursive=False)))
        else:
            md.append(t)
    heads = " ".join(h.get_text(" ", strip=True).lower() for h in main.find_all(["h2", "h3"]))
    blocks["contents"] = any(k in heads for k in ("description", "contenu", "programme"))
    blocks["learning_outcomes"] = any(k in heads for k in ("objectif", "compétences", "acquis"))
    blocks["prerequisites"] = "pré" in heads
    blocks["bibliography"] = "bibliograph" in heads
    return "\n\n".join(md), blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = [r for r in cat["asignaturas"] if r.get("url_guia_docente") and r["tipo_fuente"] != "sin_guia"]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        pick = []
        for n in SAMPLE_NAMES:
            pick += [r for r in rows if r["nombre_asignatura"] == n][:1]
        rows = pick[:a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for r in rows:
        try:
            body, blocks = to_md(http.get_text(r["url_guia_docente"]))
            write_markdown(SLUG, r, body, {**blocks})
            print("ok", r["codigo_asignatura"], r["nombre_asignatura"])
        except Exception as e:
            bad += 1
            print("FAIL", r["codigo_asignatura"], type(e).__name__, e)
    sys.exit(1 if bad else 0)


main()
