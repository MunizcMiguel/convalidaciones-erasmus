#!/usr/bin/env python3
"""Fase 2 · Scraper — Universidad de Oviedo, Grado en Ingeniería Electrónica Industrial y Automática.

Por asignatura (3 GET sin sesión, ver notas_descubrimiento.md):
  1. página de asignatura  -> asignaturaId + metadatos (materia, actividades con horas…)
  2. JSON serveGuiasDocentes -> guiaDocenteId del curso académico vigente
  3. fragmento HTML /GuiaDocente (versión española) -> Markdown

Uso (desde la raíz del proyecto):
    python universidades/uniovi_gieia/scraper_uniovi_gieia.py --sample 5
    python universidades/uniovi_gieia/scraper_uniovi_gieia.py --codes GIMECA01-1-001 GIMECA01-4-024
    python universidades/uniovi_gieia/scraper_uniovi_gieia.py --all
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
SLUG = "uniovi_gieia"
BASE = "https://www.uniovi.es/estudia/grados/ingenieria/electronicaindustrial"  # versión española (referencia)
PORTLET = "es_uniovi_sies_web_UnioviSiesWebPortlet"

# Muestra piloto fija y diversa (cursos 1-4, básica, troncal mecánica, optativa, TFG).
SAMPLE: list[str] = []  # se rellena desde el catálogo (pick_sample)

# id del collapse (data-target) -> bloque de blocks_found
BLOCK_BY_ID = {
    "requisitos-detail": "prerequisites",
    "competenciasResultadosAprendizaje-detail": "learning_outcomes",
    "contenidos-detail": "contents",
    "evaluacion-detail": "assessment",
    "bibliografia-detail": "bibliography",
}
# Apartados con datos personales: no se vuelcan al Markdown.
DROP_IDS = {"coordinadores-detail", "profesorado-detail"}
DROP_TITLES = {"coordinacion", "profesorado"}
EXPECTED_IDS = {"contextualizacion-detail", "metodologia-detail", *BLOCK_BY_ID}
META_SKIP = {"código asignatura"}  # ya va en la cabecera


_ENGLISH_PAGE = re.compile(r"<html[^>]*\blang=\"en|\(\d+ Hours\)")
# Línea suelta con nombre de docente dentro del texto libre ("Coordinador de la asignatura: …").
_STAFF_LINE = re.compile(r"^[\W_]*(?:coordinador(?:a|es)?|profesor(?:a|es|as|ado)?|responsable|docentes?)\b"
                         r"[^.:\n|]{0,60}:[^\n|]{0,200}$", re.I)


class GuideError(RuntimeError):
    pass


# ------------------------------------------------------------------ URLs
def guias_list_url(asignatura_id: str) -> str:
    return (f"{BASE}?p_p_id={PORTLET}&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view"
            f"&p_p_resource_id=serveGuiasDocentes&p_p_cacheability=cacheLevelPage"
            f"&_{PORTLET}_asignaturaId={asignatura_id}")


def guia_url(guia_id: str) -> str:
    return (f"{BASE}?p_p_id={PORTLET}&p_p_lifecycle=0&p_p_state=exclusive&p_p_mode=view"
            f"&_{PORTLET}_mvcRenderCommandName=%2FGuiaDocente&_{PORTLET}_guiaDocenteId={guia_id}")


# ------------------------------------------------------------------ HTML -> Markdown
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
                out.append(f"**{txt}**" if in_cell else f"### {txt}")
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
    return _WS.sub(" ", s).strip()


def _fold(s: str) -> str:
    import unicodedata
    return "".join(ch for ch in unicodedata.normalize("NFD", norm(s).lower()) if unicodedata.category(ch) != "Mn")


def course_metadata(page_html: str) -> list[tuple[str, str]]:
    """Filas 'etiqueta: valor' de la página de asignatura (materia, actividades…)."""
    soup = BeautifulSoup(page_html, "lxml")
    meta: list[tuple[str, str]] = []
    for lab in soup.select("div.asignatura div.row > div.fof-title"):
        val = lab.find_next_sibling("div")
        if val is None:
            continue
        label = norm(lab.get_text())
        if label.lower() in META_SKIP:
            continue
        items = [norm(li.get_text()) for li in val.find_all("li")]
        value = "; ".join(i for i in items if i) if items else norm(val.get_text())
        if label and value:
            meta.append((label, value))
    return meta


def parse_guide(fragment_html: str) -> tuple[list[tuple[str, str, str]], set[str]]:
    """-> ([(id_contenido, título, markdown)], ids presentes en el HTML)."""
    soup = BeautifulSoup(fragment_html, "lxml")
    acc = soup.find(id="guiaDocenteAccordion")
    if acc is None:
        raise GuideError("no hay #guiaDocenteAccordion en el fragmento")
    sections: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for head in acc.select("div.seccion"):
        title = norm(head.get_text())
        target = (head.get("data-target") or "").lstrip("#")
        body = soup.find(id=target) if target else None
        if body is None:
            raise GuideError(f"apartado '{title}' sin contenedor ({target!r})")
        seen.add(target)
        if target in DROP_IDS or _fold(title) in DROP_TITLES:
            continue
        sections.append((target, title, html_to_md(body)))
    return sections, seen


def scrape_course(http: PoliteClient, entry: dict, academic_year: str) -> tuple[Path, dict, str]:
    code = entry["codigo_asignatura"]
    page = http.get_text(entry["url_guia_docente"])
    if _ENGLISH_PAGE.search(page):
        # Liferay recuerda el idioma por cookie: si la página se cacheó tras visitar /en/
        # sale en inglés. Se vuelve a pedir una vez (este cliente nunca visita /en/).
        page = http.get_text(entry["url_guia_docente"], force=True)
    m = re.search(rf"_{PORTLET}_asignaturaId=(\d+)", page)
    if not m:
        raise GuideError("no se encuentra asignaturaId en la página de asignatura")
    guias = http.get_json(guias_list_url(m.group(1)))
    if not guias:
        raise GuideError("la asignatura no tiene guías docentes publicadas")
    chosen = next((g for g in guias if g.get("periodoAcademico") == academic_year), None)
    note = ""
    if chosen is None:  # sin guía del curso vigente: la más reciente publicada
        chosen = max(guias, key=lambda g: str(g.get("periodoAcademico", "")))
        note = f"sin guía {academic_year}; usada {chosen.get('periodoAcademico')}"
    if chosen.get("codigoAsignatura") not in (None, code):
        raise GuideError(f"la guía es de otra asignatura ({chosen.get('codigoAsignatura')})")
    fragment = http.get_text(guia_url(str(chosen["guiaDocenteId"])))
    sections, seen = parse_guide(fragment)
    missing = EXPECTED_IDS - seen
    if missing:
        raise GuideError(f"faltan apartados en el HTML: {sorted(missing)}")

    md: list[str] = [f"# {entry['nombre_asignatura']}", ""]
    md.append(f"Guía docente {chosen.get('periodoAcademico')} · Universidad de Oviedo · "
              f"Grado en Ingeniería Electrónica Industrial y Automática · {code}")
    meta = course_metadata(page)
    if meta:
        md += ["", "## Datos de la asignatura", ""]
        md += [f"- **{k}:** {v}" for k, v in meta]
    found = {b: False for b in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    total = 0
    for target, title, body in sections:
        md += ["", f"## {title}", "", body if body else "_(Apartado vacío en la guía.)_"]
        total += len(body)
        if target in BLOCK_BY_ID:
            found[BLOCK_BY_ID[target]] = len(re.sub(r"\W", "", body)) >= 3
    if total < 200:
        raise GuideError("la guía está prácticamente vacía")
    text = "\n".join(md)
    # GDPR: filas de tabla "Coordinador/a | nombre" o "Profesor/a | nombre" pegadas por el profesorado
    text = re.sub(r"(?im)^\|\s*\*\*(?:coordinador|profesor)[^\n]*\n", "", text)
    path = write_markdown(SLUG, entry, text, found)
    return path, found, note


def pick_sample(catalog: dict, n: int) -> list[str]:
    """Muestra fija y diversa derivada del catálogo: básica 1.º, obligatoria 2.º y 3.º, optativa 4.º, TFG; reserva: prácticas/otras."""
    rows = catalog["asignaturas"]
    def first(pred, skip=()):
        return next((r["codigo_asignatura"] for r in rows if pred(r) and r["codigo_asignatura"] not in skip), None)
    out: list[str] = []
    for pred in (lambda r: r["caracter"] == "formacion_basica" and r["curso"] == 1,
                 lambda r: r["caracter"] == "obligatoria" and r["curso"] == 2,
                 lambda r: r["caracter"] == "obligatoria" and r["curso"] == 3,
                 lambda r: r["caracter"] == "optativa" and r["curso"] == 4,
                 lambda r: r["caracter"] == "tfg",
                 lambda r: r["caracter"] == "practicas",
                 lambda r: r["caracter"] == "formacion_basica" and r["curso"] == 1,
                 lambda r: r["caracter"] == "obligatoria" and r["curso"] == 4):
        c = first(pred, out)
        if c:
            out.append(c)
    return out[:n]


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
        codes = pick_sample(catalog, max(1, args.sample))

    http = PoliteClient(cache_dir=HERE / "raw_cache", headers={"Accept-Language": "es-ES,es;q=0.9"})
    ok = failed = skipped = 0
    for code in codes:
        entry = by_code.get(code)
        if entry is None:
            print(f"FALLO  {code}: no está en el catálogo")
            failed += 1
            continue
        if entry.get("tipo_fuente") == "sin_guia":
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
