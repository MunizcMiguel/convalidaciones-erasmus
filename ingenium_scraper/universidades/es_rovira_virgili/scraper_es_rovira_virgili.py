#!/usr/bin/env python3
"""Fase 2 — URV: guía docente HTML (guiadocent.urv.cat/docnet/guia_docent) -> Markdown.

Cada asignatura es una página (`...&assignatura={codigo}&idioma=cast`) que solo muestra datos identificativos (con coordinador/
profesorado/correos: se descartan) y la descripción general; los apartados son páginas aparte `&fitxa_apartat=N`:
55 Competencias · 56 Resultados de aprendizaje · 57 Contenidos · 58 Planificación · 59 Metodologías · 60 Atención personalizada ·
61 Evaluación · 62 Fuentes de información · 63 Recomendaciones. Se descargan 55, 56, 57, 59, 61, 62, 63 (58 y 60 solo son horas/tutorías).
El contenido de cada apartado son las tablas hermanas que siguen a la tabla de navegación («Competencias Resultados de aprendizaje ...»).
Uso: python universidades/es_rovira_virgili/scraper_es_rovira_virgili.py [--sample N | --all | --codes C...]
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
SLUG = "es_rovira_virgili"
APARTADOS = [(55, "Competencias"), (56, "Resultados de aprendizaje"), (57, "Contenidos"), (59, "Metodologías"),
             (61, "Evaluación"), (62, "Fuentes de información"), (63, "Recomendaciones")]
SAMPLE = None  # se fija tras leer el catálogo (ver sample_codes)


class GuideError(Exception):
    pass


class NoGuide(GuideError):
    """La guía no existe publicada (no es un fallo del scraper)."""


def direct_rows(table):
    rows = table.find_all("tr", recursive=False)
    for tb in table.find_all("tbody", recursive=False):
        rows += tb.find_all("tr", recursive=False)
    return rows


def html_md(el, out, depth=0):
    for ch in el.children:
        if isinstance(ch, NavigableString):
            t = re.sub(r"\s+", " ", str(ch))
            if t.strip():
                out.append(t)
            continue
        n = ch.name
        if n in ("script", "style"):
            continue
        if n == "table" and (drows := direct_rows(ch)) and any(len(r.find_all(["td", "th"], recursive=False)) >= 2 for r in drows):
            rows = [[re.sub(r"\s+", " ", c.get_text("; " if c.find("table") else " ", strip=True)).replace("|", "/")
                     for c in r.find_all(["td", "th"], recursive=False)] for r in drows]
            rows = [[c for c in r] for r in rows if any(r)]
            w0 = max(map(len, rows))
            keep = [j for j in range(w0) if any(j < len(r) and r[j] for r in rows)]  # quitar columnas vacías
            rows = [[r[j] if j < len(r) else "" for j in keep] for r in rows]
            if not rows or not rows[0]:
                continue
            w = max(map(len, rows))
            rows = [r + [""] * (w - len(r)) for r in rows]
            head = "| " + " | ".join(rows[0]) + " |"
            sep = "|" + "---|" * w
            body = [("| " + " | ".join(r) + " |") for r in rows[1:]]
            out.append("\n\n" + "\n".join([head, sep] + body) + "\n\n")
        elif n in ("ul", "ol"):
            out.append("\n")
            for li in ch.find_all("li", recursive=False):
                sub = []
                html_md(li, sub, depth + 1)
                out.append("  " * depth + "- " + re.sub(r"\s+", " ", "".join(sub)).strip() + "\n")
            out.append("\n")
        elif n == "br":
            out.append("\n")
        elif n in ("p", "div", "section", "tr", "table", "td", "h1", "h2", "h3", "h4"):
            out.append("\n\n")
            html_md(ch, out, depth)
            out.append("\n\n")
        else:
            html_md(ch, out, depth)


def to_md(nodes) -> str:
    out: list[str] = []
    for n in nodes:
        if isinstance(n, NavigableString):
            out.append(str(n))
        elif n.name:
            tmp = BeautifulSoup("<div></div>", "lxml").div
            tmp.append(n.__copy__())
            html_md(tmp, out)
    t = "".join(out).replace("\xa0", " ")
    t = re.sub(r"(?m)^DWLayoutTable$\n*", "", t)
    t = re.sub(r"[ \t]*\n[ \t]*", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def nav_table(soup):
    navs = [tb for tb in soup.find_all("table") if tb.get_text(" ", strip=True).startswith("Competencias Resultados de aprendizaje")]
    if not navs:
        raise NoGuide("guía sin apartados publicados (p. ej. movilidad)")
    return navs[-1]


def apartado(http, base, num):
    soup = BeautifulSoup(http.get_text(f"{base}&fitxa_apartat={num}"), "lxml")
    for x in soup(["script", "style"]):
        x.decompose()
    nav = nav_table(soup)
    nodes = []
    for sib in nav.next_siblings:
        if getattr(sib, "name", None) and sib.get_text(" ", strip=True).startswith("(*)La Guía docente"):
            break
        nodes.append(sib)
    return re.sub(r"\(\*\)La Guía docente.*", "", to_md(nodes), flags=re.S).strip()


def descripcion(http, base):
    soup = BeautifulSoup(http.get_text(base), "lxml")
    for x in soup(["script", "style"]):
        x.decompose()
    c = soup.find("div", id="contingut")
    L = c.get_text("\n", strip=True).split("\n")
    try:
        i = next(k for k, l in enumerate(L) if l.startswith("Descripción general"))
        j = next(k for k in range(i, len(L)) if L[k] == "Competencias")
    except StopIteration:  # algunas guías (movilidad, laboratorio) no tienen descripción general
        return "", "\n".join(L[:60])
    return "\n\n".join(L[i + 1:j]), "\n".join(L[:60])


def scrape_course(http, e):
    code = e["codigo_asignatura"]
    base = e["url_guia_docente"]
    desc, head = descripcion(http, base)
    if "no está publicada en este idioma" in head:
        raise NoGuide("guía no publicada en castellano")
    if code not in head:
        raise GuideError("la guía no corresponde a la asignatura")
    md = [f"# {e['nombre_asignatura']} ({code})", "",
          f"- Titulación: {e['nombre_grado']} · {e['universidad']}",
          f"- Curso/periodo: {e['curso_semestre']}",
          f"- Créditos: {e['creditos_ects']} ECTS · Carácter: {e['caracter']}",
          f"- Fuente: {base}", ""]
    blocks = dict(contents=False, learning_outcomes=False, assessment=False, bibliography=False, prerequisites=False)
    if desc.strip():
        md += ["## Descripción general", "", desc, ""]
    got = {}
    for num, title in APARTADOS:
        text = apartado(http, base, num)
        got[num] = text
        if text:
            md += [f"## {title}", "", text, ""]
    ok = lambda n, k=25: len(got.get(n, "")) > k  # noqa: E731
    blocks["learning_outcomes"] = ok(56) or ok(55)
    blocks["contents"] = ok(57)
    blocks["assessment"] = ok(61)
    blocks["bibliography"] = ok(62)
    blocks["prerequisites"] = ok(63)
    if not (blocks["contents"] or blocks["learning_outcomes"]):
        raise GuideError("guía sin contenidos ni resultados de aprendizaje")
    return write_markdown(SLUG, e, "\n".join(md), blocks), blocks


def sample_codes(rows):
    """Diversa: 1.º básica (Cálculo/Física), 2.º y 3.º obligatorias de ingeniería, una optativa, prácticas y TFG."""
    pick = []
    for pat in (r"CÁLCULO|MATEM", r"INGENIERÍA TÉRMICA I$", r"MECÁNICA DE FLUIDOS|HIDRÁULICA", r"DISEÑO DE MÁQUINAS|DISEÑO MEC", r"PRÁCTICAS EXTERNAS", r"TRABAJO FIN"):
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
        except NoGuide as ex:
            print(f"omitida {c} {e['nombre_asignatura']}: {ex}")
        except Exception as ex:  # noqa: BLE001
            print(f"FALLO  {c} {e['nombre_asignatura']}: {ex}")
            fail += 1
    print(f"{ok} ok, {fail} fallos")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
