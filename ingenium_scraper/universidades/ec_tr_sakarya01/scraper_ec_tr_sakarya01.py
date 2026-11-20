"""Fase 2 - Sakarya University: ficha del EBS (/Ders/Detay/{id}) -> raw_markdown/{codigo}.md
Uso: python universidades/ec_tr_sakarya01/scraper_ec_tr_sakarya01.py [--sample N | --all | --codes C1 C2]
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
SLUG = "ec_tr_sakarya01"
SAMPLE = ["MAT 111", "MKM 201", "MKM 305", "MKM 405", "MKM 499"]
SEP = chr(10) * 2
DROP_LABELS = re.compile(r"^(Dersin Koordinatörü|Dersi Verenler|Dersin Yardımcıları|Destekleyen Eğitmen)", re.I)
SECTIONS = [  # (id de tabla, titulo)
    ("Ders-Ogrenme-Ciktilari", "Ders Öğrenme Çıktıları (learning outcomes)"),
    ("Ders-Akisi", "Ders Akışı (weekly topics)"),
    ("Ders-Kaynaklari", "Kaynaklar (references)"),
    ("Ders-Degerlendirme-Sistemi", "Değerlendirme Sistemi (assessment)"),
    ("Ders-Akts-Is-Yuku", "AKTS / İş Yükü (workload)"),
]
BLOCKS = {
    "contents": ("dersin içeriği", "ders akışı"),
    "learning_outcomes": ("öğrenme çıktıları",),
    "assessment": ("değerlendirme sistemi",),
    "bibliography": ("kaynaklar",),
    "prerequisites": ("ön koşul",),
}


def cell(c) -> str:
    for br in c.find_all("br"):
        br.replace_with("\n")
    t = c.get_text("\n").replace("\xa0", " ")
    t = "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n"))
    return re.sub(r"\n{2,}", "\n", t).strip().replace("|", "/").replace("\n", " <br> ")


def table_md(t) -> str:
    rows = [[cell(c) for c in r.find_all(["th", "td"])] for r in t.find_all("tr") if r.find_parent("table") is t]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def to_markdown(html: str, title: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    d = s.find(id="dersDetay")
    if d is None:
        raise ValueError("sin #dersDetay")
    md = ["# " + title]
    tables = d.find_all("table")
    if tables and tables[0].get("id") is None or (tables and not re.search(r"Detay|Ders-", tables[0].get("id") or "")):
        md.append("## Ders bilgileri (course information)" + SEP + table_md(tables[0]))
    det = next((t for t in tables if (t.get("id") or "").endswith("-Detay")), None)
    if det is not None:
        for tr in det.find_all("tr"):
            tds = tr.find_all("td", recursive=False)
            if len(tds) < 2:
                continue
            label = re.sub(r"\s+", " ", tds[0].get_text(" ", strip=True))
            if DROP_LABELS.match(label):
                continue
            v = re.sub(r"\n{3,}", "\n\n", tds[1].get_text("\n").strip())
            v = "\n".join(re.sub(r"[ \t\xa0]+", " ", l).strip() for l in v.split("\n")).strip()
            if v:
                md.append(f"### {label}{SEP}{v}")
    for tid, h in SECTIONS:
        ts = [t for t in d.find_all("table") if t.get("id") == tid]
        if not ts:
            continue
        t = max(ts, key=lambda x: len(x.find_all("tr")))
        m = table_md(t)
        rows = [[cell(c) for c in r.find_all(["th", "td"])] for r in t.find_all("tr") if r.find_parent("table") is t]
        has_data = any(any(x for x in r[1:]) for r in rows[1:])
        if m and has_data:  # tablas solo con cabecera (fichas vacías en origen) no cuentan como bloque
            md.append(f"## {h}{SEP}{m}")
    out = SEP.join(md)
    low = out.lower()
    found = {k: any(x in low for x in v) for k, v in BLOCKS.items()}
    found["prerequisites"] = "ön koşul dersleri" in low and bool(re.search(r"ön koşul dersleri\s*\n+[^#\n]", out, re.I))
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
