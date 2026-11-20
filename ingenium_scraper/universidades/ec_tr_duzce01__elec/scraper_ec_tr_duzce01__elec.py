"""Fase 2 - Duzce University: ficha del Egitim Bilgi Sistemi (/Ders/Index/{id}) -> raw_markdown/{codigo}.md
Uso: python universidades/ec_tr_duzce01__elec/scraper_ec_tr_duzce01__elec.py [--sample N | --all | --codes C1 C2]
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
SLUG = "ec_tr_duzce01__elec"
SAMPLE = ["FIZ111", "MM201", "MM302", "MM432", "MM499"]
SEP = chr(10) * 2
DROP_ROWS = re.compile(r"^(Dersin Koordinatörü|Dersi Veren)", re.I)
SKIP_HEADS = re.compile(r"Program Yeterlilik|Yeterlilikleri İlişkileri|Ders - Program")
BLOCKS = {
    "contents": ("dersin içeriği", "ders planı"),
    "learning_outcomes": ("öğrenme kazanım",),
    "assessment": ("değerlendirme yöntemi",),
    "bibliography": ("kaynaklar",),
    "prerequisites": ("ön koşul",),
}


def txt(el) -> str:
    for br in el.find_all("br"):
        br.replace_with("\n")
    t = el.get_text("\n").replace("\xa0", " ")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n"))).strip()


def table_md(t) -> str:
    rows = []
    for r in t.find_all("tr"):
        rows.append([re.sub(r"\s+", " ", c.get_text(" ", strip=True)).replace("|", "/") for c in r.find_all(["th", "td"])])
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    # quitar columnas con nombres de personal
    drop = {i for r in rows[:3] for i, h in enumerate(r) if re.search(r"Sorumlu Personel|Öğretim Elemanı", h, re.I)}
    rows = [[c for i, c in enumerate(r) if i not in drop] for r in rows]
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def render_chunk(frag: BeautifulSoup) -> str:
    out = []
    for t in frag.find_all("table"):
        if "ebs-bilgi-tablosu" in (t.get("class") or []):
            for tr in t.find_all("tr"):
                th, td = tr.find("th"), tr.find("td")
                if not th or not td:
                    continue
                label = re.sub(r"\s+", " ", th.get_text(" ", strip=True))
                if DROP_ROWS.match(label):
                    continue
                v = txt(td)
                out.append(f"### {label}{SEP}{v if v else '(boş)'}")
            t.decompose()
    for t in frag.find_all("table"):
        m = table_md(t)
        if m:
            out.append(m)
        t.decompose()
    rest = txt(frag)
    if rest:
        out.append(rest)
    return SEP.join(out)


def to_markdown(html: str, title: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    cont = s.select_one("div.ebs-yazdir-tam")
    if cont is None:
        raise ValueError("sin div.ebs-yazdir-tam")
    md = ["# " + title]
    for card in cont.find_all("div", class_="card", recursive=False):
        hd = card.select_one(".card-header")
        h = re.sub(r"\s+", " ", hd.get_text(" ", strip=True)) if hd else ""
        h = re.sub(r"\s*(Yazdır|Print)$", "", h).strip()
        bd = card.select_one(".card-body")
        if not h or bd is None or SKIP_HEADS.search(h):
            continue
        body_md = render_chunk(BeautifulSoup(str(bd), "lxml").body)
        if body_md:
            md.append(f"## {h}{SEP}{body_md}")
    out = SEP.join(md)
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
