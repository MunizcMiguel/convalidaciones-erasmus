#!/usr/bin/env python3
"""Fase 2 — UGA Licence Mécanique (GMP): fichas HTML de UE (catálogo ODF/Ametys) -> Markdown. CLI: --sample N | --all | --codes C1 C2"""
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup
from common.http_client import PoliteClient
from common.util import load_catalog, write_markdown

HERE = Path(__file__).parent
SLUG = "ec_f_grenobl22__info"
SAMPLE = ["IGT8HCJN", "PAX5MPAB", "PAX6MEAK", "PAMP6TAA", "ELP329", "IGT8FM08"]
SKIP_SECTIONS = ("diplômes intégrant", "lieu(x) ville", "campus")
NOISE = {"Lire plus", "Ajouter à la sélection", "Télécharger la fiche PDF", "Télécharger"}
PII_HEAD = ("responsable", "contact", "enseignant", "intervenant", "équipe pédagogique")


def table_md(t):
    rows = [[c.get_text(" ", strip=True).replace("|", "/") for c in tr.find_all(["th", "td"])] for tr in t.find_all("tr")]
    rows = [r for r in rows if r]
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * n] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def to_md(html):
    main = BeautifulSoup(html, "lxml").find("main")
    title = main.find("h1").get_text(" ", strip=True)
    md = [f"# {title}"]
    facts = main.find("section", class_="g-py-40")
    if facts:
        items = []
        for h in facts.find_all("h2"):
            val = h.find_next_sibling()
            v = " ".join(val.get_text(" ", strip=True).split()) if val else ""
            if not v:
                nxt = h.parent.get_text(" ", strip=True).replace(h.get_text(" ", strip=True), "", 1).strip()
                v = nxt
            items.append(f"- **{h.get_text(' ', strip=True)}** : {v}")
        md.append("\n".join(items))
    found = []
    for sec in main.find_all("section"):
        if sec is facts or sec.find_parent("section") is not None and sec.find_parent("section") is not main:
            continue
        head = sec.find(["h2", "h3"])
        if head is None or sec is facts:
            continue
        h = head.get_text(" ", strip=True)
        hl = h.lower()
        if hl.startswith(SKIP_SECTIONS) or hl.startswith(PII_HEAD) or h == title:
            continue
        found.append(hl)
        if sec.find("table"):
            body = "\n\n".join(table_md(t) for t in sec.find_all("table"))
        else:
            lines = [l for l in sec.get_text("\n", strip=True).split("\n") if l not in NOISE]
            lines = [l for l in lines if l != h]
            # etiquetas repetidas (p. ej. "TP\nTP\n28h") -> "TP 28h"
            out, i = [], 0
            while i < len(lines):
                if i + 1 < len(lines) and lines[i] == lines[i + 1] and len(lines[i]) < 12:
                    i += 1
                    continue
                out.append(lines[i]); i += 1
            if hl.startswith("heures"):
                body = "\n".join(f"- {a} {b}" for a, b in zip(out[::2], out[1::2])) if len(out) % 2 == 0 else "\n".join("- " + x for x in out)
            else:
                body = "\n".join(out)
        md.append(f"## {h}\n\n{body}" if sec.find("h2") and not hl.startswith("heures") else f"### {h}\n\n{body}")
    joined = " | ".join(found)
    blocks = dict(contents="description" in joined or "contenu" in joined or "programme" in joined,
                  learning_outcomes=any(k in joined for k in ("compétences", "objectif", "acquis")),
                  assessment=any(k in joined for k in ("contrôle", "évaluation", "modalités")),
                  bibliography="bibliograph" in joined, prerequisites="pré-requis" in joined or "prérequis" in joined)
    return "\n\n".join(md), blocks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    rows = [r for r in load_catalog(SLUG)["asignaturas"] if r.get("url_guia_docente") and r["tipo_fuente"] != "sin_guia"]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        rows = [r for c in SAMPLE for r in rows if r["codigo_asignatura"] == c][:a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for r in rows:
        try:
            body, blocks = to_md(http.get_text(r["url_guia_docente"]))
            write_markdown(SLUG, r, body, blocks)
            print("ok", r["codigo_asignatura"], r["nombre_asignatura"])
        except Exception as e:
            bad += 1
            print("FAIL", r["codigo_asignatura"], type(e).__name__, e)
    sys.exit(1 if bad else 0)


main()
