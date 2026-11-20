#!/usr/bin/env python3
"""Fase 2 · Scraper — Sapienza Roma, Ingegneria Informatica e Automatica (L-8).

Una GET por ficha (/attendance/lesson/.../<id>?channel=0) en corsidilaurea.uniroma1.it (HTML estático).
Se convierte el bloque <main> a Markdown: h3 título, h4 secciones, listas y tablas.
Se eliminan 'Docente coordinatore', 'Docenti' y 'Stampa PDF'.

Uso: python universidades/ec_i_roma01/scraper_ec_i_roma01.py --sample 5 | --all | --codes C1 C2
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString, Tag  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_roma01"
SAMPLE = [
    "1044385",   # Sistemi di controllo — año 2, automática
    "1016596",   # Elettronica — año 3
    "10629103",  # Fondamenti di matematica — año 1, matemáticas
    "1017398",   # Economia e organizzazione aziendale — año 3
    "AAF1001",   # Prova finale — TFG
]
NL = chr(10)
DROP = re.compile(r"^(docente|docenti|stampa pdf)", re.I)
BLOCKS = {
    "contents": r"programma dell|programme|contenuti",
    "learning_outcomes": r"obiettivi formativi|risultati di apprendimento",
    "assessment": r"modalit. di esame|valutazione",
    "bibliography": r"testi di riferimento|bibliograf",
    "prerequisites": r"prerequisiti",
}


def inline(el) -> str:
    txt = el.get_text(" ") if isinstance(el, Tag) else str(el)
    txt = re.sub(r"[ \t\r\f\v\xa0]+", " ", txt)
    txt = re.sub(r" ?\n ?", "\n", txt)
    return re.sub(r"\n{2,}", "\n\n", txt).strip()


def convert(node: Tag, out: list[str]) -> None:
    for ch in node.children:
        if isinstance(ch, NavigableString):
            t = str(ch).strip()
            if t:
                out.append(t)
            continue
        n = ch.name
        if n in ("script", "style", "button", "nav", "form"):
            continue
        if n == "h3":
            out.append("\n# " + inline(ch) + "\n")
        elif n in ("h4", "h5"):
            out.append("\n## " + inline(ch) + "\n")
        elif n in ("ul", "ol"):
            for i, li in enumerate(ch.find_all("li", recursive=False), 1):
                out.append(f"{i}. " if n == "ol" else "- ")
                out[-1] += inline(li)
            out.append("")
        elif n == "table":
            rows = [[inline(c) for c in tr.find_all(["th", "td"])] for tr in ch.find_all("tr")]
            rows = [r for r in rows if r]
            if rows:
                w = max(len(r) for r in rows)
                rows = [r + [""] * (w - len(r)) for r in rows]
                out.append("| " + " | ".join(rows[0]) + " |")
                out.append("|" + "---|" * w)
                out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                out.append("")
        elif n in ("p", "div", "section", "article", "span", "dl", "dt", "dd", "strong", "b", "em"):
            if n in ("p", "dt", "dd") or not ch.find(["h3", "h4", "h5", "ul", "ol", "table", "p", "div"]):
                t = inline(ch)
                if t:
                    out.append(t + "\n")
            else:
                convert(ch, out)
        else:
            convert(ch, out)


def build(html: str, e: dict) -> tuple[str, dict]:
    main = BeautifulSoup(html, "lxml").find("main")
    if main is None:
        raise ValueError("sin <main>")
    for br in main.find_all("br"):
        br.replace_with("\n")
    h3 = main.find("h3")
    out = ["# " + (inline(h3) if h3 else e["nombre_asignatura"]) + "\n"]
    heads = []
    for item in main.select("div.accordion-item"):
        h = item.select_one(".accordion-title h4")
        body = item.select_one(".accordion-content")
        title = inline(h) if h else ""
        if not title or DROP.match(title) or body is None:
            continue
        sec: list[str] = []
        convert(body, sec)
        text = NL.join(x for x in sec if x.strip()).strip()
        if not text:
            continue
        heads.append(title)
        out.append("## " + title + NL + NL + text + NL)
    md = re.sub(NL + "{3,}", NL + NL, NL.join(out)).strip() + NL
    found = {k: any(re.search(p, x, re.I) for x in heads) for k, p in BLOCKS.items()}
    if not heads:
        raise ValueError("ficha sin secciones")
    return md, found


def fetch(http: PoliteClient, url: str) -> str:
    try:
        return http.get_text(url + "?channel=0", encoding="utf-8")
    except FetchError:
        return http.get_text(url, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    codes = list(rows) if a.all else a.codes or SAMPLE[: a.sample or 5]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    failed = 0
    for c in codes:
        e = rows.get(c)
        if e is None:
            print(f"{c}: FAIL no está en el catálogo"); failed += 1; continue
        if e["tipo_fuente"] == "sin_guia":
            print(f"{c}: skip sin_guia"); continue
        try:
            md, found = build(fetch(http, e["url_guia_docente"]), e)
            p = write_markdown(SLUG, e, md, found)
            miss = [k for k, v in found.items() if not v]
            print(f"{c}: ok {len(md)} chars -> {p.name}" + (f" | faltan: {', '.join(miss)}" if miss else ""))
        except (FetchError, ValueError) as ex:
            print(f"{c}: FAIL {type(ex).__name__}: {ex}"); failed += 1
    print("HTTP:", http.stats)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
