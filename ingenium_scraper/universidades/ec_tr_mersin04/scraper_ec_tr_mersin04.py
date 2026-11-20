"""Fase 2 - Toros University (Endustri Muhendisligi): JSON del Bologna Bilgi Paketi -> raw_markdown/{codigo}.md
Para cada asignatura se prueba dilID 2 (EN) y luego 1 (TR) en GetDersGenel sin yilID (el servidor devuelve el año más reciente con contenido).
Se omite dersinOgretimUyesi (profesorado). Uso: python universidades/ec_tr_mersin04/scraper_ec_tr_mersin04.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json  # noqa: E402

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_mersin04"
B = "https://obsogrenci.toros.edu.tr/BLGNDersBilgiPaketi/"
SAMPLE = ["MAT101", "INE111", "INE221", "INE205", "INE495"]
SEP = "\n\n"


def clean(v) -> str:
    if v is None:
        return ""
    t = BeautifulSoup(str(v), "lxml").get_text("\n")
    t = "\n".join(re.sub(r"[ \t\xa0]+", " ", l).strip() for l in t.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def cell(v) -> str:
    return clean(v).replace("|", "/").replace("\n", " <br> ")


def table(head, rows) -> str:
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(cell(x) for x in r) + " |" for r in rows])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="*")
    a = ap.parse_args()
    rows = load_catalog(SLUG)["asignaturas"]
    if a.codes:
        rows = [r for r in rows if r["codigo_asignatura"] in a.codes]
    elif not a.all:
        rows = [r for r in rows if r["codigo_asignatura"] in SAMPLE][: a.sample]
    http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=2, timeout=30)

    def post(ep, qs, dil):
        return json.loads(http.get_bytes(B + ep, method="POST", json={"param": qs, "dilID": int(dil)}))

    fail = 0
    for r in rows:
        q = {k: v[0] for k, v in parse_qs(urlparse(r["url_guia_docente"]).query).items()}
        base = {k: q[k] for k in ("mufDersID", "dersGrubuDersID", "dersID", "programID")}
        got = None
        for dil in ("2", "1"):  # sin yilID el servidor devuelve la versión más reciente con contenido (campo yilID de la respuesta)
            qs = dict(base, dilID=dil)
            try:
                g = post("GetDersGenel", qs, dil).get("Bilgiler")
            except Exception:
                g = None
            if g and (g.get("amaci") or g.get("icerigi")):
                y = str(g.get("yilID"))
                qs = dict(qs, yilID=y)
                got = (qs, dil, y, g)
                break
        if not got:
            print("FAIL", r["codigo_asignatura"], "sin ficha en ningún año"); fail += 1; continue
        qs, dil, y, g = got
        oc = post("GetDersOgrenmeCikti", qs, dil).get("Bilgiler") or []
        wk = post("GetDersHaftalikIcerik", qs, dil).get("Bilgiler") or []
        ev = post("GetDersDegerlendirme", qs, dil).get("Bilgiler") or []
        wl = post("GetDersIsYuku", qs, dil).get("Bilgiler") or []
        lang = "en" if dil == "2" else "tr"
        r = dict(r, idioma_pagina=lang)
        md = [f"# {r['codigo_asignatura']} — {r['nombre_asignatura']}", f"ECTS: {r['creditos_ects']:g} · Year {r['curso']} · Semester {r['semestre']} · {r['caracter']} · content year id {y}"]
        pre = clean(g.get("dersinOnKosuluOlanDersler"))
        if pre:
            md.append("## Prerequisites" + SEP + pre)
        for key, h in (("amaci", "Objectives of the course"), ("icerigi", "Course content"), ("onerilenDigerHususlar", "Recommended optional programme components"), ("kitapMalzemeKaynak", "Recommended or required reading"), ("stajDurumu", "Internship status")):
            t = clean(g.get(key))
            if t:
                md.append(f"## {h}" + SEP + t)
        if oc:
            md.append("## Learning outcomes" + SEP + "\n".join(f"{o.get('sira')}. {clean(o.get('aciklama'))}" for o in sorted(oc, key=lambda o: o.get("sira") or 0)))
        if wk:
            md.append("## Weekly course contents" + SEP + table(["Week", "Subjects", "Practice", "Laboratory"], [[w.get("haftaNo"), w.get("kapsam"), w.get("uygulama"), w.get("laboratuvar")] for w in sorted(wk, key=lambda w: w.get("haftaNo") or 0)]))
        evr = []
        for grp in ev:
            for d in grp.get("dersDegerlendirme") or []:
                evr.append([grp.get("aciklama_eng") or grp.get("aciklama"), d.get("aciklama_eng") or d.get("aciklama"), d.get("sayi"), f"{d.get('yuzdeKatSayisi')}%"])
            if grp.get("toplam") is not None and grp.get("dersDegerlendirme"):
                evr.append([grp.get("aciklama_eng") or grp.get("aciklama"), "Subtotal", "", f"{grp.get('toplam')}%"])
        if evr:
            md.append("## Course assessment" + SEP + table(["Group", "Activity", "Number", "Contribution"], evr))
        if wl:
            md.append("## Course workload" + SEP + table(["Activity", "Number", "Hours each", "Total hours"], [[w.get("aciklama_eng") or w.get("aciklama"), w.get("sayi"), w.get("sure"), (w.get("sayi") or 0) * (w.get("sure") or 0)] for w in wl]) + f"\n\nTotal workload (hours): {max((w.get('genelToplamSaat') or 0) for w in wl)}")
        body = SEP.join(md)
        blocks = {"contents": bool(clean(g.get("icerigi")) or wk), "learning_outcomes": bool(oc), "assessment": bool(evr), "bibliography": bool(clean(g.get("kitapMalzemeKaynak"))), "prerequisites": bool(pre)}
        write_markdown(SLUG, r, body, blocks)
        print("ok", r["codigo_asignatura"], lang, y, {k: v for k, v in blocks.items() if not v} or "")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
