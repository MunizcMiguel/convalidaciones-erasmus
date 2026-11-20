#!/usr/bin/env python3
"""Fase 2 — USAL: guía de asignatura HTML (guias.usal.es/node/{id}) -> Markdown.

La guía es una secuencia de pares `div.cab-epigrafe` (título numerado: 1. Datos de la asignatura, Datos del profesorado, 2. Recomendaciones
previas, 3. Objetivos, 4. Competencias, 5. Contenidos, 6. Metodologías, 7. Distribución de las metodologías, 8. Recursos, 9. Evaluación) y
`div.datos-epigrafe-*` con el contenido. «Datos del profesorado» (nombre, despacho, tutorías, correo, teléfono) se descarta; «1. Datos» se resume
en la cabecera (código, plan, periodicidad, idioma).
Uso: python universidades/es_salamanca/scraper_es_salamanca.py [--sample N | --all | --codes C...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_salamanca"


class GuideError(Exception):
    pass


def html_md(el, out, depth=0):
    for ch in el.children:
        if isinstance(ch, NavigableString):
            t = re.sub(r"\s+", " ", str(ch).replace("\xa0", " "))
            if t.strip():
                out.append(t)
            continue
        n = ch.name
        if n in ("script", "style"):
            continue
        if n in ("h4", "h5", "h6"):
            out.append(f"\n\n### {ch.get_text(' ', strip=True)}\n\n")
        elif n == "table":
            rows = [[re.sub(r"\s+", " ", c.get_text(" ", strip=True)).replace("|", "/") for c in tr.find_all(["td", "th"])] for tr in ch.find_all("tr")]
            rows = [r for r in rows if any(r)]
            if rows:
                w0 = max(map(len, rows))
                keep = [j for j in range(w0) if any(j < len(r) and r[j] for r in rows)]
                rows = [[r[j] if j < len(r) else "" for j in keep] for r in rows]
                head = "| " + " | ".join(rows[0]) + " |"
                out.append("\n\n" + "\n".join([head, "|" + "---|" * len(keep)] + ["| " + " | ".join(r) + " |" for r in rows[1:]]) + "\n\n")
        elif n in ("ul", "ol"):
            out.append("\n")
            for li in ch.find_all("li", recursive=False):
                sub = []
                html_md(li, sub, depth + 1)
                out.append("  " * depth + "- " + re.sub(r"\s+", " ", "".join(sub)).strip() + "\n")
            out.append("\n")
        elif n == "br":
            out.append("\n")
        elif n in ("p", "div", "section", "tr"):
            out.append("\n\n")
            html_md(ch, out, depth)
            out.append("\n\n")
        else:
            html_md(ch, out, depth)


def to_md(node) -> str:
    out: list[str] = []
    html_md(node, out)
    t = "".join(out)
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    soup = BeautifulSoup(http.get_text(e["url_guia_docente"]), "lxml")
    for x in soup(["script", "style"]):
        x.decompose()
    h4 = soup.find("h4", string=re.compile(r"1\. Datos"))
    if h4 is None or code not in h4.parent.find_next_sibling("div").get_text(" ", strip=True):
        raise GuideError("la guía no corresponde a la asignatura o no tiene la estructura esperada")
    d = h4.parent.find_next_sibling("div", class_="datos-epigrafe-asig").get_text("\n", strip=True).split("\n")
    info = {d[i]: d[i + 1] for i in range(len(d) - 1) if d[i] in ("Plan", "Periodicidad", "Idioma", "Área", "Departamento")}
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']} (E.P.S. de Zamora)",
          f"- Curso/periodo: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}"]
    md += [f"- {k}: {v}" for k, v in info.items()]
    md += [f"- Fuente: {e['url_guia_docente']}", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    title = None
    for sib in h4.parent.next_siblings:
        cls = getattr(sib, "get", lambda *_: None)("class") or []
        if "cab-epigrafe" in cls:
            title = sib.get_text(" ", strip=True)
            title = re.sub(r"\s*\(Fecha última modificación.*$", "", title)
        elif title and any(c.startswith("datos-epigrafe") for c in cls):
            if "profesorado" in title.lower() or "datos-epigrafe-prof" in cls or title.startswith("1."):
                continue
            text = to_md(sib)
            if not text:
                continue
            md += [f"## {title}", "", text, ""]
            t = title.lower()
            if t.startswith("5."):
                blocks["contents"] = len(text) > 30
            elif t.startswith("4."):
                blocks["learning_outcomes"] = len(text) > 30
            elif t.startswith("9."):
                blocks["assessment"] = len(text) > 30
            elif t.startswith("8."):
                blocks["bibliography"] = len(text) > 30
            elif t.startswith("2."):
                blocks["prerequisites"] = len(text) > 30 and not re.search(r"(?i)^\W*(ninguna?|no (hay|se))", text.split("\n")[-1])
    if not (blocks["contents"] or blocks["learning_outcomes"]):
        raise GuideError("guía sin contenidos ni competencias")
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def sample_codes(rows):
    pick = []
    for pat in (r"^Matem[aá]ticas i$", r"^Mec[aá]nica de fluidos", r"^Teor[ií]a de mecanismos", r"^Dise[ñn]o y c[aá]lculo de m[aá]quinas", r"pr[aá]cticas", r"proyecto fin"):
        for c, r in rows.items():
            if re.search(pat, r["nombre_asignatura"], re.I) and c not in pick:
                pick.append(c)
                break
    for c, r in rows.items():
        if r["caracter"] == "optativa" and c not in pick:
            pick.append(c)
            break
    return pick


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    rows = {r["codigo_asignatura"]: r for r in load_catalog(SLUG)["asignaturas"]}
    codes = [c for c, r in rows.items() if r["tipo_fuente"] != "sin_guia"] if a.all else (a.codes or sample_codes(rows)[: a.sample or 5])
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = 0
    for c in codes:
        e = rows.get(c)
        if not e:
            print(f"FALLO {c}: no está en el catálogo")
            fail += 1
            continue
        try:
            p, b = scrape_course(http, e)
            miss = [k for k, v in b.items() if not v]
            print(f"ok     {c} {e['nombre_asignatura']} ({p.stat().st_size} B)" + (f" · ausentes: {','.join(miss)}" if miss else ""))
            ok += 1
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c} {e['nombre_asignatura']}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
