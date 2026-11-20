"""Fase 2 - Zonguldak BEUN: ficha OBS Bologna (progCourseDetails.aspx) -> raw_markdown/{codigo}.md
Plataforma OBS/Proliz, reutilizable para otras universidades turcas con el mismo sistema (cambiar SLUG y SAMPLE).
Uso: python universidades/ec_tr_zonguld01/scraper_ec_tr_zonguld01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_zonguld01"
SEP = chr(10) * 2
SAMPLE = ["MM111", "MM217", "MM352", "MM402", "MM441"]
DROP_LABELS = re.compile(r"^(Course Coordinator|Name of Lecturers?|Assistants?|Ders Koordinat|Dersi Veren|Yardımcılar)", re.I)
BLOCKS = {
    "contents": ("course content", "weekly detailed course contents", "ders içeriği"),
    "learning_outcomes": ("learning outcomes", "öğrenme çıktı"),
    "assessment": ("assessment methods", "değerlendirme"),
    "bibliography": ("recommended or required reading", "önerilen"),
    "prerequisites": ("prerequisites", "önkoşul"),
}


def clean(t: str) -> str:
    t = t.replace("\xa0", " ")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n"))).strip()


def table_md(t) -> str:
    rows = []
    for r in t.find_all("tr"):
        cells = [re.sub(r"\s+", " ", c.get_text(" ", strip=True)).replace("|", "/") for c in r.find_all(["th", "td"])]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def value_md(td) -> str:
    inner = td.find("table")
    if inner is not None:
        return table_md(inner)
    for br in td.find_all("br"):
        br.replace_with("\n")
    return clean(td.get_text("\n"))


def to_markdown(html: str, title: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    md = ["# " + title]
    info = s.find(id="grdDers")
    if info is not None:
        md.append("## Course information\n\n" + table_md(info))
    dl = s.find(id="dlDers")
    if dl is not None:
        top = dl.select_one("table.table")
        for tr in [r for r in top.find_all("tr") if r.find_parent("table") is top]:
            tds = tr.find_all("td", recursive=False)
            if len(tds) >= 2:
                label = re.sub(r"\s+", " ", tds[0].get_text(" ", strip=True))
                if DROP_LABELS.match(label):
                    continue
                v = value_md(tds[1])
                if v and v.lower() != "none":
                    md.append(f"### {label}\n\n{v}")
                elif label.lower().startswith("prereq") or "prerequisite" in label.lower():
                    md.append(f"### {label}\n\n{v or 'None'}")
            elif len(tds) == 1 and tds[0].get_text(strip=True):
                inner = tds[0].select("div.panel")
                if inner:  # paneles anidados (lectura recomendada, categoria del curso...)
                    for pn in inner:
                        hd = pn.select_one(".panel-heading")
                        body = SEP.join(x for x in (table_md(t) for t in pn.find_all("table")) if x)
                        if hd and body:
                            md.append("## " + re.sub(r"\s+", " ", hd.get_text(" ", strip=True)) + SEP + body)
                else:
                    md.append("#### " + re.sub(r"\s+", " ", tds[0].get_text(" ", strip=True)))
    if dl is not None:  # paneles hermanos dentro de dlDers (lectura recomendada, categoria del curso)
        for pn in dl.select("div.panel")[1:]:
            hd = pn.select_one(".panel-heading")
            body = SEP.join(x for x in (table_md(t) for t in pn.find_all("table")) if x)
            if hd and body:
                md.append("## " + re.sub(r"\s+", " ", hd.get_text(" ", strip=True)) + SEP + body)
    for panel in s.select("div.panel"):
        if panel.find(id="dlDers") or panel.find(id="grdDers") or panel.find_parent(id="dlDers"):
            continue
        head = panel.select_one(".panel-heading")
        h = re.sub(r"\s+", " ", head.get_text(" ", strip=True)) if head else ""
        if not h or h.startswith("Contribution of Learning Outcomes"):
            continue
        parts = [table_md(t) for t in panel.find_all("table")]
        body = "\n\n".join(p for p in parts if p)
        if not body:
            sp = [clean(x.get_text("\n")) for x in panel.find_all("span") if x.get("id") and not x.get("id").endswith("_h")]
            body = "\n\n".join(x for x in sp if x and x != h)
        if body:
            md.append(f"## {h}\n\n{body}")
    out = "\n\n".join(md)
    low = out.lower()
    found = {k: any(x in low for x in v) for k, v in BLOCKS.items()}
    return out, found


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
            body, found = to_markdown(c.get_text(e["url_guia_docente"]), e["nombre_asignatura"])
            write_markdown(SLUG, e, body, found)
            print("ok  ", e["codigo_asignatura"], len(body), {k: v for k, v in found.items() if not v} or "")
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print("FAIL", e["codigo_asignatura"], type(ex).__name__, ex)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
