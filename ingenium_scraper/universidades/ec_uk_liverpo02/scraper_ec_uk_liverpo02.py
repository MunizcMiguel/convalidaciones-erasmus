"""Fase 2 - LJMU BEng Mechanical Engineering: module specifications del Course Catalogue (CourseLoop).
Cada pagina /module/2025/{code} lleva el JSON completo en <script id="__NEXT_DATA__"> (props.pageProps.pageContent).
Uso: python universidades/ec_uk_liverpo02/scraper_ec_uk_liverpo02.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_uk_liverpo02"
SAMPLE = ["4301MECH", "4304MECH", "5302MECH", "5307MECH", "6301MECH"]  # L4 mates/mecánica, L5, proyecto L6


def html_md(frag: str) -> str:
    """Fragmento HTML -> Markdown (parrafos, listas, tablas, negritas)."""
    if not frag or not isinstance(frag, str):
        return ""
    soup = BeautifulSoup(frag, "lxml")

    def inline(n) -> str:
        if isinstance(n, NavigableString):
            return str(n)
        if n.name == "br":
            return "\n"
        t = "".join(inline(c) for c in n.children)
        if n.name in ("b", "strong") and t.strip():
            return f"**{t.strip()}** "
        return t

    def block(n, depth=0) -> list[str]:
        out: list[str] = []
        for c in n.children:
            if isinstance(c, NavigableString):
                if str(c).strip():
                    out.append(str(c).strip())
            elif c.name in ("ul", "ol"):
                for i, li in enumerate(c.find_all("li", recursive=False), 1):
                    lead = f"{i}." if c.name == "ol" else "-"
                    sub = [x for x in li.find_all(["ul", "ol"], recursive=False)]
                    txt = "".join(inline(x) for x in li.children if x not in sub).strip()
                    out.append("  " * depth + f"{lead} {re.sub(chr(10)+'+', ' ', txt)}")
                    for sl in sub:
                        out.extend(block(BeautifulSoup(str(sl), "lxml").body, depth + 1))
                out.append("")
            elif c.name == "table":
                rows = [[re.sub(r"\s+", " ", td.get_text(" ", strip=True)) for td in tr.find_all(["th", "td"])] for tr in c.find_all("tr")]
                rows = [r for r in rows if r]
                if rows:
                    w = max(len(r) for r in rows)
                    rows = [r + [""] * (w - len(r)) for r in rows]
                    out.append("| " + " | ".join(rows[0]) + " |")
                    out.append("|" + "---|" * w)
                    out.extend("| " + " | ".join(r) + " |" for r in rows[1:])
                    out.append("")
            elif c.name in ("p", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6", "body", "html"):
                if c.find(["ul", "ol", "table"]):
                    out.extend(block(c, depth))
                else:
                    t = inline(c).strip()
                    if t:
                        out.append(re.sub(r"[ \t]*\n[ \t]*", "\n", t))
                        out.append("")
            else:
                t = inline(c).strip()
                if t:
                    out.append(t)
        return out

    body = soup.body or soup
    return re.sub(r"\n{3,}", "\n\n", "\n".join(block(body))).strip()


def build(pc: dict, e: dict) -> tuple[str, dict]:
    sec: list[str] = []
    cp = pc.get("credit_points")
    sec.append(f"# {pc.get('title') or e['nombre_asignatura']} ({pc.get('code')})\n")
    meta = [f"- Level: {pc.get('level')}", f"- Credits: {cp} UK credits (≈ {float(cp)/2:g} ECTS)" if cp else None,
            f"- Catalogue version: {pc.get('version_name')}"]
    uo = pc.get("unit_offering") or []
    if uo:
        meta.append(f"- Teaching period: {uo[0].get('teaching_period')} ({uo[0].get('duration')}); language of instruction: {uo[0].get('language_of_instruction')}")
    sec.append("\n".join(m for m in meta if m))
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}

    def add(title: str, md: str) -> bool:
        if md.strip():
            sec.append(f"\n## {title}\n\n{md.strip()}")
            return True
        return False

    add("Overview", html_md(pc.get("overview")))
    add("Aim", html_md(pc.get("aim")))
    found["contents"] = add("Content / description", html_md(pc.get("description")) or html_md(pc.get("content")))
    add("Learning and teaching strategy", html_md(pc.get("learning_experiences")))
    add("Other learning experiences", html_md(pc.get("other_learning_experiences")))
    la = pc.get("learning_activity") or []
    add("Learning activities", "\n".join(f"- {a.get('type')}: {a.get('duration_number')} hours" for a in la))
    lo = sorted(pc.get("unit_learning_outcomes") or [], key=lambda x: x.get("order") or 0)
    found["learning_outcomes"] = add("Learning outcomes", "\n".join(f"- {o.get('code')}: {html_md(o.get('description')) }" for o in lo))
    ad = pc.get("assessment_data") or []
    if ad:
        rows = ["| Assessment | Type | Weight (%) | Individual/Group | Learning outcomes | Description |", "|---|---|---|---|---|---|"]
        for a in ad:
            rows.append("| " + " | ".join(str(x if x is not None else "").replace("\n", " ").replace("|", "/") for x in (
                a.get("name"), a.get("assessment_type"), a.get("weight"), a.get("individual"), a.get("learning_outcomes"), re.sub(r"<[^>]+>", " ", a.get("description") or "").strip())) + " |")
        found["assessment"] = add("Assessment", "\n".join(rows))
    if not found["assessment"]:
        found["assessment"] = add("Assessment", html_md(pc.get("assessment")))
    found["prerequisites"] = add("Prerequisites", html_md(pc.get("pre_requisites")))
    add("Exclusions", html_md(pc.get("exclusions")))
    biblio = html_md(pc.get("learning_and_teaching_resources")) or html_md(pc.get("learning_materials"))
    found["bibliography"] = add("Learning and teaching resources", biblio)
    add("Other notes", html_md(pc.get("other_notes")))
    return "\n".join(sec), found


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    if a.codes:
        codes = a.codes
    elif a.all:
        codes = list(rows)
    else:
        n = a.sample or 5
        codes = [c for c in SAMPLE if c in rows]
        for c in rows:  # completa hasta n con diversidad por curso
            if len(codes) >= n:
                break
            if c not in codes:
                codes.append(c)
        codes = codes[:max(n, 1)]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    bad = 0
    for code in codes:
        e = rows.get(code)
        if not e or e["tipo_fuente"] == "sin_guia":
            print(code, "SKIP sin guia"); continue
        try:
            h = http.get_text(e["url_guia_docente"])
            m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h, re.S)
            pc = json.loads(m.group(1))["props"]["pageProps"]["pageContent"]
            if pc.get("code") != code:
                raise ValueError(f"código distinto: {pc.get('code')}")
            body, found = build(pc, e)
            p = write_markdown(SLUG, e, body, found)
            print(code, "ok", p.name, {k: int(v) for k, v in found.items()})
        except Exception as ex:  # noqa: BLE001
            bad += 1
            print(code, "FALLO", type(ex).__name__, str(ex)[:120])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
