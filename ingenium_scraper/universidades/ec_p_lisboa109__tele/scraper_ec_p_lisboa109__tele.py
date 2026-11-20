#!/usr/bin/env python3
"""Fase 2 · Scraper — Universidade de Lisboa (IST), Licenciatura em Engenharia Mecânica (LEMec21).

Por asignatura, 1 GET a la API pública de Fénix (`/api/fenix/v1/courses/{id}`, la misma URL que
`url_guia_docente`). La ficha trae `competences[]` (program, bibliographicReferences; HTML),
`evaluationMethod` (HTML, a veces con tablas) y `teachers` (se descarta: privacidad).

Uso (desde la raíz del proyecto):
    python universidades/ec_p_lisboa109__tele/scraper_ec_p_lisboa109__tele.py --sample 5
    python universidades/ec_p_lisboa109__tele/scraper_ec_p_lisboa109__tele.py --codes MA222
    python universidades/ec_p_lisboa109__tele/scraper_ec_p_lisboa109__tele.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, Comment, NavigableString, Tag  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_p_lisboa109__tele"

SAMPLE = [
    "CDI18112",    # Cálculo Diferencial e Integral I — año 1, matemáticas
    "MA222",       # Mecânica Aplicada II — año 2, núcleo mecánico (evaluación con tabla/fórmula)
    "MMat112",     # Mecânica dos Materiais — año 2
    "MF222",       # Mecânica dos Fluidos I — año 3
    "PI123610",    # Projecto Integrador de 1.º Ciclo — año 3, proyecto final
    "Rel3610",     # Relatividade — año 2, atípica (3 ECTS)
]

STAFF = re.compile(r"(?i)^\s*(docente|professor|regente|coordenad|contact|e-?mail|gabinete|hor[aá]rio de atendimento)")


def inline(node, depth: int = 0) -> str:
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    inner = "".join(inline(c, depth) for c in node.children)
    if node.name in ("b", "strong"):
        return f"**{inner.strip()}**" if inner.strip() else ""
    if node.name in ("i", "em"):
        return f"*{inner.strip()}*" if inner.strip() else ""
    if node.name == "br":
        return "\n"
    return inner


def table_md(t: Tag) -> str:
    rows = []
    for tr in t.find_all("tr"):
        cells = [re.sub(r"\s+", " ", c.get_text(" ", strip=True)).replace("|", "/") for c in tr.find_all(["td", "th"])]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    n = max(len(r) for r in rows)
    if n == 1:                                   # tabla de una columna (maquetación): párrafos
        return "\n\n".join(r[0] for r in rows if r[0])
    rows = [r + [""] * (n - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(["---"] * n) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def html_to_md(html: str | None) -> str:
    if not html or not html.strip():
        return ""
    soup = BeautifulSoup(html, "lxml")
    root = soup.body or soup
    out: list[str] = []

    def walk(el: Tag, indent: str = "") -> None:
        for ch in el.children:
            if isinstance(ch, Comment):
                continue
            if isinstance(ch, NavigableString):
                t = re.sub(r"\s+", " ", str(ch)).strip()
                if t:
                    out.append(indent + t)
                continue
            if ch.name == "table":
                out.append(table_md(ch))
            elif ch.name in ("ul", "ol"):
                for i, li in enumerate(ch.find_all("li", recursive=False), 1):
                    mark = "-" if ch.name == "ul" else f"{i}."
                    out.append(f"{indent}{mark} " + re.sub(r"\s+", " ", inline(li)).strip())
            elif ch.name in ("p", "div", "span", "td", "tr", "tbody", "font", "center", "section"):
                if ch.find(["table", "ul", "ol", "p", "div"]):
                    walk(ch, indent)
                else:
                    txt = re.sub(r"[ \t\r\f\v]+", " ", inline(ch))
                    for ln in txt.split("\n"):
                        if ln.strip():
                            out.append(ln.strip())
            elif ch.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                out.append("#### " + re.sub(r"\s+", " ", inline(ch)).strip())
            elif ch.name == "br":
                continue
            else:
                txt = re.sub(r"\s+", " ", inline(ch)).strip()
                if txt:
                    out.append(txt)

    walk(root)
    return "\n\n".join(o for o in out if o and not STAFF.match(o)).strip()


def build_markdown(c: dict, entry: dict) -> tuple[str, dict[str, bool]]:
    comps = c.get("competences") or []
    program = "\n\n".join(x for x in (html_to_md(p.get("program")) for p in comps) if x)
    biblio_items = []
    for p in comps:
        for b in p.get("bibliographicReferences") or []:
            if isinstance(b, str):
                biblio_items.append(f"- {b.strip()}")
                continue
            parts = [re.sub(r"\s+", " ", str(b.get(k) or "")).strip() for k in ("author", "title", "reference", "year")]
            line = ", ".join(x for x in parts if x)
            if b.get("type"):
                line += f" ({'main' if b['type'] == 'MAIN' else str(b['type']).lower()})"
            if line:
                biblio_items.append("- " + line)
    biblio = "\n".join(dict.fromkeys(biblio_items))
    evaluation = html_to_md(c.get("evaluationMethod"))
    if not (program or biblio or evaluation):
        raise ValueError("ficha vacía en la API")
    found = {"contents": bool(program), "learning_outcomes": False, "assessment": bool(evaluation),
             "bibliography": bool(biblio), "prerequisites": False}
    out = [f"# {entry['nombre_asignatura']} ({entry['codigo_asignatura']})", "", "## Informação geral", "",
           f"- **Licenciatura:** {entry['nombre_grado']}",
           f"- **Ano / Semestre:** {entry['curso']} / {entry['semestre']}",
           f"- **ECTS:** {entry['creditos_ects']:g}",
           f"- **Período lectivo:** {c.get('academicTerm', '')}"]
    if program:
        out += ["", "## Programa", "", program]
    if evaluation:
        out += ["", "## Método de avaliação", "", evaluation]
    if biblio:
        out += ["", "## Bibliografia", "", biblio]
    return "\n".join(out).strip() + "\n", found


def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--sample", type=int, default=None)
    grp.add_argument("--all", action="store_true")
    grp.add_argument("--codes", nargs="+")
    args = ap.parse_args()
    cat = load_catalog(SLUG)
    if cat is None:
        print("Falta catalogo_urls.json: ejecuta discover_ec_p_lisboa109__tele.py", file=sys.stderr)
        return 2
    rows = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    codes = list(rows) if args.all else (args.codes or SAMPLE[: args.sample or 5])
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    failed = 0
    for code in codes:
        e = rows.get(code)
        if e is None:
            print(f"{code}: FAIL no está en el catálogo")
            failed += 1
            continue
        if e["tipo_fuente"] == "sin_guia":
            print(f"{code}: skip sin_guia")
            continue
        try:
            md, found = build_markdown(http.get_json(e["url_guia_docente"]), e)
            p = write_markdown(SLUG, e, md, found)
            miss = [k for k, v in found.items() if not v]
            print(f"{code}: ok [pt] {len(md)} chars -> {p.name}" + (f" | faltan: {', '.join(miss)}" if miss else ""))
        except (FetchError, ValueError) as ex:
            print(f"{code}: FAIL {type(ex).__name__}: {ex}")
            failed += 1
    print("HTTP:", http.stats)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
