#!/usr/bin/env python3
"""Fase 2 · Scraper — UPV/EHU, Grado en Ingeniería Mecánica (Escuela de Ingeniería de Bilbao).

Una petición GET por asignatura: la ficha "consultaAsignatura" del portal de grados de ehu.eus
(HTML generado por XSL desde GAUR) lleva la guía docente completa en acordeones:
    h2 Docencia       -> tabla de horas por tipo de enseñanza          (se conserva)
    h2 Guía docente   -> h3 por apartado + div.content2                 (se conserva)
    h2 Grupos         -> horarios, aulas y PROFESORADO                  (se descarta: datos personales)

Uso (desde la raíz del proyecto):
    python universidades/es_pais_vasco/scraper_es_pais_vasco.py --sample 5
    python universidades/es_pais_vasco/scraper_es_pais_vasco.py --codes 27680 27730
    python universidades/es_pais_vasco/scraper_es_pais_vasco.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, Comment, NavigableString, Tag  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_pais_vasco"

# Muestra piloto fija y diversa.
SAMPLE = [
    "25971",  # Cálculo — 1.º, básica, anual (matemáticas)
    "27680",  # Automatismos y Control — 2.º, obligatoria
    "27724",  # Diseño de Máquinas — 3.º, obligatoria troncal mecánica, con prerrequisitos
    "27727",  # Diseño Mecánico Mediante Elementos Finitos — 4.º, optativa
    "27730",  # Trabajo Fin de Grado — atípica
    # reserva si se pide --sample > 5
    "28278",  # Comunicación Científico-técnica Escrita en Euskera — solo euskera
    "26518",  # Inglés para Ingeniería Industrial — solo inglés
    "27687",  # Francés Técnico — no se imparte en el curso actual
]

# Secciones de primer nivel (h2 del acordeón)
KEEP_TOP = {"docencia", "guia docente"}
DROP_TOP = {"grupos", "tribunal", "tribunales", "profesorado"}
# Apartados (h3) de la guía que se descartan por contener datos personales
DROP_SUB = {"profesorado", "tutorias", "coordinador", "coordinadora", "coordinacion"}


def block_of(title_key: str) -> str | None:
    if title_key.startswith(("contenidos", "temario", "programa")):
        return "contents"
    if title_key.startswith(("competencias", "resultados de aprendizaje")):
        return "learning_outcomes"
    if title_key.startswith(("sistemas de evaluacion", "evaluacion", "convocatoria")):
        return "assessment"
    if title_key.startswith("bibliografia"):
        return "bibliography"
    if title_key.startswith(("requisitos", "prerrequisitos", "restricciones", "conocimientos previos", "recomendaciones")):
        return "prerequisites"
    return None


class GuideError(RuntimeError):
    pass


def key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).strip().lower()


# ------------------------------------------------------------------ HTML -> Markdown
_WS = re.compile(r"[ \t\r\n\f\v\xa0​]+")
_BULLET = re.compile(r"^(?:[-–—·•▪◦●○■□➢➤►✓✔*]+)\s*(?=\S)")
SKIP = {"script", "style", "noscript"}
BLOCKS = {"p", "div", "ul", "ol", "table", "h1", "h2", "h3", "h4", "h5", "h6", "dl", "blockquote", "pre"}
# Línea suelta con nombre de docente en texto libre ("Profesor responsable: …", "Coordinadora: …")
_STAFF_LINE = re.compile(r"^[\W_]*(?:coordinador(?:a|es)?|profesor(?:a|es|as|ado)?|responsable|docentes?|"
                         r"irakasle(?:a|ak)?|koordinatzaile(?:a)?)\b[^.:\n|]{0,60}:\s*\S[^\n|]{0,200}$", re.I)


def inline(node) -> str:
    """Texto en línea de un nodo; <br> -> '\n'."""
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return _WS.sub(" ", str(node))
    if not isinstance(node, Tag) or node.name in SKIP:
        return ""
    if node.name == "br":
        return "\n"
    s = "".join(inline(c) for c in node.children)
    if node.name == "a":
        href = (node.get("href") or "").strip()
        txt = s.strip()
        if txt and href.startswith("http") and href != txt:
            return f"[{txt}]({href})"
        return s
    if node.name in ("sub", "sup") and s.strip():
        return f"<{node.name}>{s}</{node.name}>"
    if node.name in BLOCKS or node.name == "li":
        return "\n" + s + "\n"
    return s


def text_lines(s: str) -> list[str]:
    return [ln for ln in (re.sub(r" {2,}", " ", x).strip() for x in s.split("\n")) if ln]


def para_md(s: str) -> str:
    """Texto libre de GAUR: cada línea va separada por <br><br>. Una línea por párrafo;
    las líneas con viñeta consecutivas se agrupan en una lista."""
    out: list[str] = []
    prev_item = False
    for ln in text_lines(s):
        if _STAFF_LINE.match(ln):
            continue
        item = bool(_BULLET.match(ln))
        if item:
            ln = "- " + _BULLET.sub("", ln)
        elif ln.startswith("#"):
            ln = "\\" + ln
        if out:
            out.append("\n" if (item and prev_item) else "\n\n")
        out.append(ln)
        prev_item = item
    return "".join(out)


def cell_md(td: Tag) -> str:
    return " <br> ".join(text_lines(inline(td))).replace("|", "\\|")


def table_md(table: Tag) -> str:
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if cells:
            rows.append([cell_md(c) for c in cells])
    if not rows:
        return ""
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    lines = []
    cap = table.find("caption")
    if cap and cap.get_text(strip=True):
        lines.append(f"**{_WS.sub(' ', cap.get_text()).strip()}**\n")
    lines.append("| " + " | ".join(rows[0]) + " |")
    lines.append("|" + "|".join([" --- "] * n) + "|")
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def list_md(lst: Tag, depth: int = 0) -> str:
    out = []
    ordered = lst.name == "ol"
    for i, li in enumerate(lst.find_all("li", recursive=False), 1):
        own = "".join(inline(c) for c in li.children if not (isinstance(c, Tag) and c.name in ("ul", "ol")))
        own = " ".join(text_lines(own))
        mark = f"{i}." if ordered else "-"
        if own:
            out.append("  " * depth + f"{mark} {own}")
        for sub in li.find_all(["ul", "ol"], recursive=False):
            s = list_md(sub, depth + (1 if own else 0))
            if s:
                out.append(s)
    return "\n".join(out)


def blocks_md(container: Tag, h_level: int) -> str:
    """Convierte el contenido de un apartado; los h4/h5 internos pasan a nivel h_level."""
    parts: list[str] = []
    buf: list[str] = []

    def flush():
        if buf:
            md = para_md("".join(buf))
            if md:
                parts.append(md)
            buf.clear()

    for ch in container.children:
        if isinstance(ch, Tag) and ch.name in SKIP:
            continue
        if isinstance(ch, Tag) and ch.name in BLOCKS:
            flush()
            if ch.name in ("ul", "ol"):
                md = list_md(ch)
            elif ch.name == "table":
                md = table_md(ch)
            elif re.fullmatch(r"h[1-6]", ch.name):
                t = " ".join(text_lines(inline(ch)))
                md = "#" * h_level + " " + t if t else ""
            elif ch.name == "dl":
                md = dl_md(ch)
            elif ch.name == "p":
                md = para_md(inline(ch))
            else:  # div, blockquote, pre
                md = blocks_md(ch, h_level)
            if md:
                parts.append(md)
        else:
            buf.append(inline(ch))
    flush()
    return "\n\n".join(parts)


def dl_md(dl: Tag) -> str:
    out, cur, vals = [], None, []
    for ch in dl.find_all(["dt", "dd"]):
        t = " ".join(text_lines(inline(ch)))
        if ch.name == "dt":
            if cur is not None:
                out.append(f"- **{cur}:** {', '.join(v for v in vals if v)}")
            cur, vals = t, []
        else:
            vals.append(t)
    if cur is not None:
        out.append(f"- **{cur}:** {', '.join(v for v in vals if v)}")
    return "\n".join(out)


def heading_text(h: Tag) -> str:
    h = BeautifulSoup(str(h), "lxml").find(h.name)
    for sp in h.find_all("span"):
        sp.decompose()  # "Alternar navegación" (sr-only) y código visible solo al imprimir
    return _WS.sub(" ", h.get_text()).strip()


def has_text(md: str) -> bool:
    return bool(re.search(r"\w", re.sub(r"^#+ .*$", "", md, flags=re.M)))


# ------------------------------------------------------------------ ficha -> Markdown
def parse_guide(html: str, entry: dict) -> tuple[str, dict[str, bool]]:
    soup = BeautifulSoup(html, "lxml")
    root = soup.find("div", class_="xsl-content")
    if root is None:
        raise GuideError("sin contenedor xsl-content")
    title_h = next((h for h in root.find_all("h2") if not h.get("class")), None)
    if title_h is None:
        raise GuideError("sin título de asignatura")
    title = heading_text(title_h)
    dl = root.find("dl")
    code = None
    if dl:
        for dt in dl.find_all("dt"):
            if key(dt.get_text()) == "codigo":
                code = dt.find_next_sibling("dd").get_text(strip=True)
    if code != entry["codigo_asignatura"]:
        raise GuideError(f"la ficha es de otra asignatura (código {code})")

    blocks = dict.fromkeys(("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites"), False)
    out = [f"# {title}"]
    if dl:
        out.append(dl_md(dl))
        # Los prerrequisitos de matrícula aparecen como campo "Restricciones" de la cabecera
        blocks["prerequisites"] = any(block_of(key(dt.get_text())) == "prerequisites" for dt in dl.find_all("dt"))
    guide_sections = 0
    tops = [h for h in root.find_all("h2") if "toggler-header" in (h.get("class") or [])]
    for h2 in tops:
        t = heading_text(h2)
        k = key(t)
        body = h2.find_next_sibling()
        if body is None or body.name != "div":
            continue
        if k in DROP_TOP:
            continue
        if k not in KEEP_TOP:
            print(f"    aviso {entry['codigo_asignatura']}: sección no prevista '{t}' (se conserva)")
        subs = [h for h in body.find_all("h3") if "toggler-header" in (h.get("class") or [])]
        if not subs:
            md = blocks_md(body, 3)
            if has_text(md):
                out.append(f"## {t}\n\n{md}")
            continue
        for h3 in subs:
            st = heading_text(h3)
            sk = key(st)
            sb = h3.find_next_sibling()
            if sk in DROP_SUB or sb is None or sb.name != "div":
                continue
            md = blocks_md(sb, 3)
            if not has_text(md):
                continue  # apartado vacío en la fuente
            guide_sections += 1
            out.append(f"## {st}\n\n{md}")
            b = block_of(sk)
            if b:
                blocks[b] = True
    if guide_sections == 0:
        raise GuideError("ficha sin guía docente publicada")
    return "\n\n".join(out) + "\n", blocks


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    args = ap.parse_args()

    cat = load_catalog(SLUG)
    if not cat:
        print("Falta catalogo_urls.json: ejecuta antes discover_es_pais_vasco.py")
        return 2
    by_code = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    if args.all:
        codes = list(by_code)
    elif args.codes:
        codes = args.codes
    else:
        codes = SAMPLE[: (args.sample or 5)]

    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = failed = skipped = 0
    for code in codes:
        e = by_code.get(code)
        if e is None:
            print(f"FALLO {code}: no está en el catálogo")
            failed += 1
            continue
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print(f"omitida {code} {e['nombre_asignatura']}: sin_guia")
            skipped += 1
            continue
        try:
            md, blocks = parse_guide(http.get_text(e["url_guia_docente"]), e)
            path = write_markdown(SLUG, e, md, blocks)
            missing = [b for b, v in blocks.items() if not v]
            print(f"ok    {code} {e['nombre_asignatura']} -> {path.name} ({len(md)} car.)"
                  + (f" · sin: {', '.join(missing)}" if missing else ""))
            ok += 1
        except (GuideError, FetchError) as ex:
            print(f"FALLO {code} {e['nombre_asignatura']}: {ex}")
            failed += 1
    print(f"\n{ok} ok · {failed} fallos · {skipped} omitidas · red={http.stats['network']} caché={http.stats['cache']}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
