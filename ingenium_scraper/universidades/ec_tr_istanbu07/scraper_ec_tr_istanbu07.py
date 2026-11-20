"""Fase 2 - Yildiz Technical University (Kimya Muhendisligi): ficha HTML del Bologna Bilgi Sistemi -> raw_markdown/{codigo}.md
Uso: python universidades/ec_tr_istanbu07/scraper_ec_tr_istanbu07.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import unicodedata
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_istanbu07"
SAMPLE = ["FIZ1001", "MAT1071", "KMM2602", "KMM3532", "KMM4000"]
SEP = "\n\n"
DROP = re.compile(r"^(Dersin Koordinatörü|Dersi\s+Veren|Asistan|Ders Öğrenim Çıktısı & Program|Dersi Sunan Akademik Birim)", re.I)


def fold(x: str) -> str:
    return unicodedata.normalize("NFKD", x.replace("ı", "i").replace("İ", "I")).encode("ascii", "ignore").decode().lower()


def txt(el) -> str:
    for br in el.find_all("br"):
        br.replace_with("\n")
    t = el.get_text("\n").replace("\xa0", " ")
    t = "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def cell(el) -> str:
    return txt(el).replace("|", "/").replace("\n", " <br> ")


def grid(rows) -> str:
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    return "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]])


def to_markdown(html: str, row: dict) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    tabs = [t for t in s.find_all("table") if t.find_parent("table") is None]
    if not tabs:
        raise ValueError("sin tablas")
    md = [f"# {row['codigo_asignatura']} — {row['nombre_asignatura']}", f"ECTS: {row['creditos_ects']:g} · {row['curso_semestre']}"]
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    for t in tabs:
        trs = t.find_all("tr")
        if not trs:
            continue
        first = [c.get_text(" ", strip=True) for c in trs[0].find_all(["th", "td"])]
        if any(x.startswith("DÖÇ") for x in first):
            lo = s.find(id="learningoutcomes")
            items = [txt(li) for li in lo.find_all("li")] if lo else []
            if items:
                md.append("## Ders Öğrenim Çıktıları (learning outcomes)" + SEP + "\n".join(f"{i}. {x}" for i, x in enumerate(items, 1)))
                found["learning_outcomes"] = True
            continue  # matriz de resultados de aprendizaje/programa (no se guarda)
        if first and first[0] == "Ders Adı":
            continue  # cabecera (nombre/codigo/horas): ya en el titulo
        if all(r.find("th") and r.find("td") and len(r.find_all(["th", "td"])) == 2 for r in trs):  # pares etiqueta/valor
            for r in trs:
                label = r.find("th").get_text(" ", strip=True)
                if DROP.match(label):
                    continue
                v = txt(r.find("td"))
                if label.startswith("Dersin Türü"):
                    v = v.split("@")[0].strip()
                if not v:
                    continue
                md.append(f"## {label}{SEP}{v}")
                low = fold(label)
                if low.startswith("dersin icerigi"):
                    found["contents"] = True
                elif "ogrenim ciktilari" in low:
                    found["learning_outcomes"] = True
                elif low.startswith("ders kitabi"):
                    found["bibliography"] = True
                elif low.startswith("onkosullar") and v.lower() != "yok":
                    found["prerequisites"] = True
            continue
        rows = [[cell(c) for c in r.find_all(["th", "td"])] for r in trs]
        rows = [r for r in rows if any(r)]
        if len(rows) < 2:
            if rows and rows[0] and len(rows[0]) == 2:
                md.append(f"## {rows[0][0]}{SEP}{rows[0][1]}")
            continue
        h = " ".join(rows[0])
        title = "Haftalık Konular (weekly topics)" if h.startswith("Hafta") else "Ölçme ve Değerlendirme (assessment)" if "Katkı" in h else "İş Yükü (workload)" if "Süresi" in h else "Table"
        md.append(f"## {title}{SEP}{grid(rows)}")
        if h.startswith("Hafta"):
            found["contents"] = True
        if "Katkı" in h:
            found["assessment"] = True
    # Ders Ogrenim Ciktilari: cada resultado va en una fila th/td o lista; ya recogido arriba
    return SEP.join(md), found


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
    fail = 0
    for r in rows:
        try:
            body, found = to_markdown(http.get_text(r["url_guia_docente"]), r)
            write_markdown(SLUG, r, body, found)
            print("ok", r["codigo_asignatura"], {k: v for k, v in found.items() if not v} or "")
        except Exception as e:  # noqa: BLE001
            fail += 1
            print("FAIL", r["codigo_asignatura"], type(e).__name__, str(e)[:100])
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
