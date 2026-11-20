#!/usr/bin/env python3
"""Fase 2 · Scraper — Universidad de Zaragoza, Grado en Ingeniería Mecánica (plan 662, EINA).

Una petición GET por asignatura: la guía docente "Formato web" de la aplicación SIGMA DOA
(sia.unizar.es). La página trae dos pestañas (Inglés `#pillen`, Castellano `#pilles`);
se toma la castellana y se convierte a Markdown apartado por apartado.

Uso (desde la raíz del proyecto):
    python universidades/es_zaragoza/scraper_es_zaragoza.py --sample 5
    python universidades/es_zaragoza/scraper_es_zaragoza.py --codes 29716 29732
    python universidades/es_zaragoza/scraper_es_zaragoza.py --all
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
SLUG = "es_zaragoza"

# Muestra fija y diversa: matemáticas de 1.º, troncal de 2.º, troncal de 3.º con laboratorio,
# optativa de 4.º, prácticas externas (guía atípica con tabla y encabezados propios) y TFG.
SAMPLE = ["29761", "29716", "29732", "29760", "29744", "29726"]

# Apartados fijos de la plantilla (por su número) -> bloque
BLOCK_BY_NUM = {"2": "learning_outcomes", "3": "contents", "5": "assessment", "7": "bibliography"}
# El apartado 2 (resultados de aprendizaje) falta en alguna guía (p. ej. 29767): es un hecho de la fuente, no un fallo.
REQUIRED_NUMS = {"1", "3", "4", "5"}
_SECTION_TITLE = re.compile(r"^(\d+(?:\.\d+)*)\.\s+\S")
_PREREQ = re.compile(r"conocimientos? previos?|requisitos?|recomienda|recomendable|recomendaci[oó]n|"
                     r"haber (?:cursado|superado)|es necesario (?:tener|haber|conocer)|se requiere", re.I)
META_SKIP = {"Asignatura"}  # ya va en el título


class GuideError(RuntimeError):
    pass


# ------------------------------------------------------------------ HTML -> Markdown
# (conversor tomado de universidades/uniovi/scraper_uniovi.py)
# Línea suelta con nombre de docente dentro del texto libre ("Coordinador de la asignatura: …").
_STAFF_LINE = re.compile(r"^[\W_]*(?:coordinador(?:a|es)?|profesor(?:a|es|as|ado)?|responsable|docentes?)\b"
                         r"[^.:\n|]{0,60}:[^\n|]{0,200}$", re.I)



BLOCK_TAGS = {"p", "div", "ul", "ol", "li", "table", "h1", "h2", "h3", "h4", "h5", "h6",
              "blockquote", "pre", "hr", "dl", "dt", "dd", "section", "article", "center",
              "tbody", "thead", "tfoot", "tr", "td", "th"}
SKIP_TAGS = {"script", "style", "head", "title", "meta", "link", "noscript", "o:p"}
_WS = re.compile(r"[ \t\r\n\f\v ​   ]+")
_BULLET = re.compile(r"^(?:[·•▪◦●○■□➢➤►✓✔]|o(?=\s{2,}| ))\s*")


def _esc(text: str) -> str:
    return text.replace("*", r"\*").replace("_", r"\_") if ("*" in text or "_" in text) else text


def _wrap(mark: str, s: str) -> str:
    """Envuelve en **/* dejando los espacios fuera (Markdown no admite '** texto **')."""
    core = s.strip()
    if not core or not re.search(r"\w", core):
        return s
    lead = s[: len(s) - len(s.lstrip())]
    trail = s[len(s.rstrip()):]
    return f"{lead}{mark}{core}{mark}{trail}"


def inline(node, in_bold: bool = False, in_em: bool = False) -> str:
    """Contenido en línea de un nodo (sin saltos de bloque; <br> -> '\n')."""
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return _esc(_WS.sub(" ", str(node)))
    if not isinstance(node, Tag) or node.name in SKIP_TAGS:
        return ""
    name = node.name
    if name == "br":
        return "\n"
    if name == "img":
        alt = (node.get("alt") or "").strip()
        return f"[imagen: {alt}]" if alt else "[imagen]"
    bold = name in ("b", "strong")
    em = name in ("i", "em")
    s = "".join(inline(c, in_bold or bold, in_em or em) for c in node.children)
    if name in BLOCK_TAGS:  # bloque dentro de contexto en línea (p. ej. <p> dentro de <td>)
        return "\n" + s + "\n"
    if bold and not in_bold:
        return "\n".join(_wrap("**", part) for part in s.split("\n"))
    if em and not in_em:
        return "\n".join(_wrap("*", part) for part in s.split("\n"))
    if name == "a":
        href = (node.get("href") or "").strip()
        txt = s.strip()
        if href.startswith("mailto:") or not href or href.startswith(("#", "javascript:")):
            return s
        if not txt:
            return ""
        if txt.replace("\\_", "_") == href:
            return f"<{href}>"
        return f"[{txt}]({href})"
    if name == "sub":
        return f"<sub>{s}</sub>" if s.strip() else s
    if name == "sup":
        return f"<sup>{s}</sup>" if s.strip() else s
    return s


def _clean_inline(s: str) -> str:
    """Normaliza espacios de un texto en línea; conserva los '\n' significativos."""
    lines = [re.sub(r" {2,}", " ", ln).strip() for ln in s.split("\n")]
    out: list[str] = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    while out and not out[-1]:
        out.pop()
    s = "\n".join(out)
    s = re.sub(r"(?<=[^\s*])\*\*\*\*(?=[^\s*])", "", s)  # '**a****b**' -> negritas contiguas
    return re.sub(r" {2,}", " ", s).strip()


def _has_block_child(tag: Tag) -> bool:
    return any(isinstance(c, Tag) and c.name in BLOCK_TAGS for c in tag.children)


def _cell_text(cell: Tag) -> str:
    """Celda de tabla -> una sola línea (párrafos y listas separados por <br>)."""
    parts: list[str] = []
    for blk in blocks(cell, depth=0, in_cell=True):
        for ln in blk.split("\n"):
            ln = ln.strip()
            if ln:
                parts.append(ln)
    return " <br> ".join(parts).replace("|", r"\|")


def table_md(table: Tag) -> str:
    rows = []
    for tr in table.find_all("tr"):
        if tr.find_parent("table") is not table:
            continue
        rows.append([c for c in tr.find_all(["td", "th"], recursive=False)])
    grid: list[list[str]] = []
    pending: dict[int, list] = {}  # col -> [filas restantes, texto] (rowspan)
    for cells in rows:
        row: list[str] = []
        col = 0
        it = iter(cells)
        cell = next(it, None)
        while cell is not None or any(c >= col for c in pending):
            if col in pending:
                pending[col][0] -= 1
                row.append("")
                if pending[col][0] <= 0:
                    del pending[col]
                col += 1
                continue
            if cell is None:
                if not any(c > col for c in pending):
                    break
                row.append("")
                col += 1
                continue
            txt = _cell_text(cell)

            def _span(attr: str) -> int:
                try:
                    return max(1, min(60, int(str(cell.get(attr, "1")).strip() or 1)))
                except ValueError:
                    return 1
            cs, rs = _span("colspan"), _span("rowspan")
            for k in range(cs):
                row.append(txt if k == 0 else "")
                if rs > 1:
                    pending[col] = [rs - 1, ""]
                col += 1
            cell = next(it, None)
        grid.append(row)
    grid = [r for r in grid if any(c.strip() for c in r)]
    if not grid:
        return ""
    width = max(len(r) for r in grid)
    for r in grid:
        r.extend([""] * (width - len(r)))
    # quitar columnas totalmente vacías (separadores de Word)
    keep = [j for j in range(width) if any(r[j].strip() for r in grid)]
    grid = [[r[j] for j in keep] for r in grid]
    if len(keep) == 1:  # tabla de maquetación de una sola columna -> párrafos
        return "\n\n".join(r[0].replace(" <br> ", "\n\n").replace(r"\|", "|") for r in grid)
    lines = ["| " + " | ".join(grid[0]) + " |", "|" + " --- |" * len(keep)]
    lines += ["| " + " | ".join(r) + " |" for r in grid[1:]]
    return "\n".join(lines)


def list_md(lst: Tag, indent: str = "") -> str:
    ordered = lst.name == "ol"
    try:
        n = int(lst.get("start", 1))
    except (TypeError, ValueError):
        n = 1
    out: list[str] = []
    for child in lst.children:
        if isinstance(child, NavigableString):
            continue
        if child.name in ("ul", "ol"):  # lista anidada directamente (HTML inválido pero frecuente)
            sub = list_md(child, indent + "  ")
            if sub:
                out.append(sub)
            continue
        if child.name != "li":
            txt = _clean_inline(inline(child))
            if txt:
                out.append(f"{indent}- " + txt.replace("\n", " "))
            continue
        marker = f"{n}. " if ordered else "- "
        buf: list = []
        first = True
        pieces: list[str] = []

        def flush():
            nonlocal first
            txt = _clean_inline("".join(inline(x) for x in buf)).replace("\n", " ")
            buf.clear()
            if txt:
                txt = _BULLET.sub("", txt)
                pieces.append(f"{indent}{marker}{txt}" if first else f"{indent}{' ' * len(marker)}{txt}")
                first = False

        for c in child.children:
            if isinstance(c, Tag) and c.name in ("ul", "ol"):
                flush()
                sub = list_md(c, indent + " " * len(marker))
                if sub:
                    pieces.append(sub)
            elif isinstance(c, Tag) and c.name == "table":
                flush()
                t = table_md(c)
                if t:
                    pieces.append("\n" + t + "\n")
            elif isinstance(c, Tag) and c.name in ("p", "div") :
                flush()
                buf.append(c)
                flush()
            else:
                buf.append(c)
        flush()
        if pieces:
            out.extend(pieces)
            if ordered:
                n += 1
    return "\n".join(out)


def blocks(root: Tag, depth: int = 0, in_cell: bool = False) -> list[str]:
    """Lista de bloques Markdown (párrafos, listas, tablas, encabezados) de `root`."""
    out: list[str] = []
    buf: list = []

    def flush():
        txt = _clean_inline("".join(inline(x) for x in buf))
        buf.clear()
        if not txt:
            return
        m = _BULLET.match(txt)
        if m and "\n" not in txt:  # viñeta "falsa" de Word (·, o, ) -> elemento de lista
            out.append("- " + txt[m.end():].strip())
        else:
            out.append(txt.replace("\n", "  \n"))

    for c in root.children:
        if isinstance(c, Comment):
            continue
        if isinstance(c, NavigableString):
            buf.append(c)
            continue
        name = c.name
        if name in SKIP_TAGS:
            continue
        if name not in BLOCK_TAGS:
            if c.find(list(BLOCK_TAGS - {"td", "th", "tr", "tbody", "thead", "tfoot"})) is not None:
                flush()  # <span>/<font> que envuelve bloques: descender
                out.extend(blocks(c, depth, in_cell))
            else:
                buf.append(c)
            continue
        flush()
        if name in ("ul", "ol"):
            md = list_md(c)
            if md:
                out.append(md)
        elif name == "table":
            md = _cell_text(c) if in_cell else table_md(c)  # tabla anidada -> texto plano
            if md:
                out.append(md)
        elif re.fullmatch(r"h[1-6]", name):
            txt = _clean_inline(inline(c, in_bold=True)).replace("\n", " ")
            if txt:
                out.append(f"**{txt}**" if in_cell else f"#### {txt}")
        elif name == "hr":
            continue
        elif name == "pre":
            txt = c.get_text().strip("\n")
            if txt.strip():
                out.append("```\n" + txt + "\n```")
        elif _has_block_child(c):
            out.extend(blocks(c, depth, in_cell))
        else:  # p, div, li suelto, td suelto, blockquote… con contenido en línea
            txt = _clean_inline("".join(inline(x) for x in c.children))
            if txt:
                m = _BULLET.match(txt)
                if m and "\n" not in txt:
                    out.append("- " + txt[m.end():].strip())
                elif name in ("li", "dd"):
                    out.append("- " + txt.replace("\n", " "))
                else:
                    out.append(txt.replace("\n", "  \n"))
    flush()
    return out


def html_to_md(root: Tag) -> str:
    parts = blocks(root)
    out: list[str] = []
    for p in parts:
        # elementos de lista consecutivos (viñetas falsas) sin línea en blanco entre ellos
        if out and p.startswith("- ") and "\n" not in p and re.match(r"^\s*(- |\d+\. )", out[-1].split("\n")[-1]):
            out[-1] += "\n" + p
        else:
            out.append(p)
    out = [p for p in out if not _STAFF_LINE.match(p)]
    return "\n\n".join(out).strip()


# ------------------------------------------------------------------ extracción
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def _first_element(tag: Tag) -> Tag | None:
    return next((c for c in tag.children if isinstance(c, Tag)), None)


def _meta_value(div: Tag) -> str:
    """Valor de un campo de la cabecera; los <br> separan valores (varios planes)."""
    for br in div.find_all("br"):
        br.replace_with("\n")
    return "; ".join(p for p in (norm(x) for x in div.get_text().split("\n")) if p)


def parse_guide(html: str) -> tuple[str, list[tuple[str, str]], list[tuple[str, str, str]]]:
    """-> (título 'código - nombre', metadatos [(clave, valor)], apartados [(número, título, cuerpo_md)])."""
    soup = BeautifulSoup(html, "lxml")
    pane = soup.find(id="pilles")
    if pane is None:
        raise GuideError("no hay pestaña en castellano (#pilles)")
    root = pane.find(id="accordiones") or pane
    title = ""
    meta: list[tuple[str, str]] = []
    sections: list[list] = []  # [num, título, [nodos]]
    pending_key: str | None = None
    for child in list(root.children):
        if isinstance(child, Comment):
            continue
        if isinstance(child, NavigableString):
            if child.strip() and sections:
                sections[-1][2].append(child)
            continue
        classes = child.get("class") or []
        if child.name == "h2" and not sections:
            t = norm(child.get_text())
            if re.match(r"^\d{5} - ", t):
                title = t
            continue
        if child.name == "div" and "col-md-4" in classes and not sections:
            pending_key = norm(child.get_text()).rstrip(":").strip()
            continue
        if child.name == "div" and "col-md-8" in classes and not sections and pending_key:
            val = _meta_value(child)
            if val and pending_key not in META_SKIP:
                meta.append((pending_key, val))
            pending_key = None
            continue
        first = _first_element(child) if child.name == "div" and "col-md-12" in classes else None
        if first is not None and first.name == "h3":
            head = norm(first.get_text())
            m = _SECTION_TITLE.match(head)
            if m:
                first.extract()
                sections.append([m.group(1), head, [child]])
                continue
            if not sections:  # "Información del Plan Docente" / "Curso Académico": cabecera de plantilla
                continue
        if sections:  # contenido fuera de sitio (HTML mal cerrado): no se pierde, va al apartado abierto
            sections[-1][2].append(child)
    out = []
    for num, head, nodes in sections:
        body = "\n\n".join(x for x in (html_to_md(n) if isinstance(n, Tag) else norm(str(n)) for n in nodes) if x)
        out.append((num, head, body))
    return title, meta, out


def scrape_course(http: PoliteClient, entry: dict, academic_year: str) -> tuple[Path, dict, str]:
    code = entry["codigo_asignatura"]
    html = http.get_text(entry["url_guia_docente"], encoding="cp1252")
    title, meta, sections = parse_guide(html)
    if not title.startswith(code + " - "):
        raise GuideError(f"la guía no es de la asignatura {code}: {title!r}")
    nums = {n for n, _, _ in sections}
    if REQUIRED_NUMS - nums:
        raise GuideError(f"faltan apartados de la plantilla: {sorted(REQUIRED_NUMS - nums)}")
    year = dict(meta).get("Año académico", "")
    y0 = academic_year.split("-")[0]
    note = "" if year.startswith(y0) else f"guía del curso {year or '?'} (se esperaba {academic_year})"

    md: list[str] = [f"# {title}", "", f"Guía docente {year} · Universidad de Zaragoza · {entry['nombre_grado']}"]
    if meta:
        md += ["", "## Información del Plan Docente", ""]
        md += [f"- **{k}:** {v}" for k, v in meta]
    found = {b: False for b in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    total = 0
    for num, head, body in sections:
        level = "##" if "." not in num else "###"
        md += ["", f"{level} {head}", "", body if body else "_(Apartado vacío en la guía.)_"]
        total += len(body)
        filled = len(re.sub(r"\W", "", body)) >= 3 and not re.match(r"^\W*(?:no hay|sin) (?:relaci[oó]n )?bibliogr", body, re.I)
        if num in BLOCK_BY_NUM:
            found[BLOCK_BY_NUM[num]] = filled
        elif num == "1" and _PREREQ.search(body):
            found["prerequisites"] = True  # no hay apartado propio: las recomendaciones van en "1. Información básica"
    if total < 200:
        raise GuideError("la guía está prácticamente vacía")
    path = write_markdown(SLUG, entry, "\n".join(md), found)
    return path, found, note


# ------------------------------------------------------------------ CLI
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=5, metavar="N", help="muestra piloto fija (por defecto 5)")
    g.add_argument("--all", action="store_true", help="todas las asignaturas del catálogo")
    g.add_argument("--codes", nargs="+", metavar="C", help="códigos concretos")
    args = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    catalog = load_catalog(SLUG)
    if not catalog:
        print("ERROR: no existe catalogo_urls.json (ejecutar antes la Fase 1)")
        return 2
    by_code = {a["codigo_asignatura"]: a for a in catalog["asignaturas"]}
    year = catalog["meta"]["curso_academico"]
    if args.all:
        codes = list(by_code)
    elif args.codes:
        codes = args.codes
    else:
        codes = SAMPLE[: max(1, args.sample)]

    http = PoliteClient(cache_dir=HERE / "raw_cache", headers={"Accept-Language": "es-ES,es;q=0.9"})
    ok = failed = skipped = 0
    for code in codes:
        entry = by_code.get(code)
        if entry is None:
            print(f"FALLO  {code}: no está en el catálogo")
            failed += 1
            continue
        if entry.get("tipo_fuente") == "sin_guia" or not entry.get("url_guia_docente"):
            print(f"OMITE  {code}: sin_guia")
            skipped += 1
            continue
        try:
            path, found, note = scrape_course(http, entry, year)
        except (FetchError, GuideError, ValueError, KeyError) as e:
            print(f"FALLO  {code} {entry['nombre_asignatura']}: {e}")
            failed += 1
            continue
        absent = [k for k, v in found.items() if not v]
        extra = (f" · bloques ausentes: {','.join(absent)}" if absent else "") + (f" · {note}" if note else "")
        print(f"ok     {code} {entry['nombre_asignatura']} -> {path.name} ({path.stat().st_size} bytes){extra}")
        ok += 1
    print(f"\n{ok} ok, {failed} fallos, {skipped} omitidas · red={http.stats['network']} "
          f"caché={http.stats['cache']} reintentos={http.stats['retries']}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
