"""Fase 2 - TUHH Maschinenbau: extrae cada modulo del Modulhandbuch HTML (ingles) a Markdown.

Uso: python universidades/ec_d_hamburg03/scraper_ec_d_hamburg03.py [--sample N | --all | --codes C1 C2]
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
SLUG = "ec_d_hamburg03"
SAMPLE = ["M0850", "M1802", "M2095", "M0680", "M-001", "M0577", "M2063"]
SKIP_LABELS = {"Module Responsible"}  # nombres de docentes fuera
HEADINGS = {"Admission Requirements", "Recommended Previous Knowledge", "Educational Objectives", "Workload in Hours",
            "Credit points", "Course achievement", "Examination", "Examination duration and scale"}
SUB = {"Knowledge", "Skills", "Social Competence", "Autonomy"}
PRO = {"Professional Competence", "Personal Competence"}


def cell_md(td) -> str:
    for li in td.find_all("li"):
        li.insert_before("\n- ")
        li.unwrap()
    for tbl in td.find_all("table"):
        rows = []
        for tr in tbl.find_all("tr"):
            cells = [re.sub(r"\s+", " ", c.get_text(" ", strip=True)) for c in tr.find_all(["th", "td"])]
            rows.append("| " + " | ".join(cells) + " |")
            if tr.find("th"):
                rows.append("|" + "---|" * len(cells))
        tbl.replace_with("\n" + "\n".join(rows) + "\n")
    txt = td.get_text(" ")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r" *\n *", "\n", txt)
    return re.sub(r"\n{3,}", "\n\n", txt).strip()


def build(entry: dict, head, content) -> tuple[str, dict]:
    body = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", ""]
    lv = head.find("table", class_="mLvTable")
    if lv:
        body += ["## Courses", "", "| Title | Type | Hrs/wk | CP |", "|---|---|---|---|"]
        for tr in lv.find_all("tr", class_="mLvRow"):
            body.append("| " + " | ".join(td.get_text(" ", strip=True) for td in tr.find_all("td")) + " |")
        body.append("")
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    for tr in content.find_all("tr"):
        l, r = tr.find("td", class_="l"), tr.find("td", class_="r")
        if not l or r is None:
            continue
        label = l.get_text(" ", strip=True)
        if label in SKIP_LABELS or label.startswith("Assignment for the Following Curricula"):
            continue
        text = cell_md(r)
        if label in PRO:
            body += ["", f"### {label}"]
        elif label in SUB:
            body += ["", f"#### {label}", "", text] if text else []
            found["learning_outcomes"] = found["learning_outcomes"] or bool(text)
        elif label == "Educational Objectives":
            body += ["", f"## {label}", "", text]
            found["learning_outcomes"] = True
        else:
            body += ["", f"## {label}", "", text or "-"]
            if label in ("Admission Requirements", "Recommended Previous Knowledge") and text.strip() not in ("", "None"):
                found["prerequisites"] = True
            if label.startswith("Examination") or label == "Course achievement":
                found["assessment"] = found["assessment"] or bool(text.strip())
    return "\n".join(body), found


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
    url = next(iter(rows.values()))["url_guia_docente"]
    s = BeautifulSoup(client.get_text(url), "lxml")
    mods = {}
    for head in s.select("table.mHead"):
        m = re.match(r"Module\s+(M-?\d+):", head.find("h2").get_text(" ", strip=True))
        mods.setdefault(m.group(1), (head, head.find_next("table", class_="mContent")))
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in mods:
            print(f"SKIP {c}")
            continue
        try:
            md, found = build(r, *mods[c])
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
