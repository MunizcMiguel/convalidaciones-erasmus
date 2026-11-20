#!/usr/bin/env python3
"""Fase 2 · Scraper — Universidad Carlos III de Madrid, Grado en Ingeniería Mecánica (estudio 221, plan 446).

Cada guía es una ficha HTML estática de la aplicación "cpa" (1 GET, sin sesión):
    https://aplicaciones.uc3m.es/cpa/generaFicha?est=221&plan=446&asig={codigo}&idioma=1
Cabecera de datos + paneles `div.apartado` (título en .panel-heading, cuerpo en .panel-body).
Los cuerpos son texto plano preformateado (`div.tarea`, `textarea`) o listas `ul`.

Uso (desde la raíz del proyecto):
    python universidades/es_carlos_iii_madrid/scraper_es_carlos_iii_madrid.py --sample 5
    python universidades/es_carlos_iii_madrid/scraper_es_carlos_iii_madrid.py --codes 14195 14213
    python universidades/es_carlos_iii_madrid/scraper_es_carlos_iii_madrid.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup, NavigableString, Tag  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_carlos_iii_madrid"

# Muestra piloto fija y diversa.
SAMPLE = [
    "14181",  # Cálculo I — 1.º, formación básica (matemáticas), con bibliografía complementaria y recursos electrónicos
    "14195",  # Mecánica de Estructuras — 2.º, obligatoria troncal
    "14208",  # Cálculo y diseño de máquinas — 4.º, obligatoria
    "18434",  # Energía en el Transporte — optativa (impartida en inglés), con requisitos
    "14213",  # Trabajo Fin de Grado — atípica (matriz de evaluación, sin pesos)
    # reserva si se pide --sample > 5
    "14220",  # Prácticas Externas
    "14155",  # Técnicas de búsqueda y uso de la información (1,5 ECTS)
    "14186",  # Fundamentos químicos de la ingeniería
]

# Campos de cabecera con datos personales: no se vuelcan.
DROP_META = ("coordinador", "profesor", "tutor")
BLOCKS = ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s).strip()


def block_of(title: str) -> str | None:
    t = norm(title)
    if t.startswith("requisitos"):
        return "prerequisites"
    if t.startswith(("objetivos", "resultados del proceso", "competencias")):
        return "learning_outcomes"
    if t.startswith("descripcion de contenidos"):
        return "contents"
    if t.startswith("sistema de evaluacion"):
        return "assessment"
    if t.startswith("bibliografia"):
        return "bibliography"
    return None


def clean(s: str) -> str:
    return re.sub(r"[ \t\xa0\r\n]+", " ", s).strip()


_BULLET = re.compile(r"^(?:[-•·▪■●◦–—*]|o(?=\t))[ \t\xa0]+(?=\S)")


def text_to_md(text: str) -> str:
    """Texto plano preformateado -> Markdown: conserva los saltos de línea; viñetas como listas."""
    out: list[str] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = raw.strip(" \t\xa0")
        if not stripped:
            if out and out[-1] != "":
                out.append("")
            continue
        m = _BULLET.match(stripped)
        if m:
            if out and out[-1] != "" and not out[-1].startswith("- "):
                out.append("")
            out.append("- " + clean(stripped[m.end():]))
            continue
        line = clean(stripped)
        if re.fullmatch(r"[-=_*~#\s]{3,}", line):  # separadores: se convertirían en títulos o reglas
            continue
        if line[0] in "#>+":
            line = "\\" + line
        if out and out[-1].startswith("- "):
            out.append("")  # texto tras una lista: párrafo nuevo, no continuación del ítem
        elif out and out[-1] != "":
            out[-1] += "  "  # salto de línea duro dentro del párrafo
        out.append(line)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out)


def link(a: Tag, base: str) -> str:
    txt = clean(a.get_text(" "))
    href = (a.get("href") or "").strip()
    if not href:
        return txt
    href = re.sub(r"\?time=\d+$", "", urljoin(base, href))  # ?time= es un anti-caché que cambia en cada petición
    if not txt or txt == href:
        return f"<{href}>" if " " not in href else href
    return f"[{txt}]({href})"


def inline(el: Tag, base: str) -> str:
    """Texto en línea de un nodo, con los enlaces en formato Markdown."""
    parts: list[str] = []
    for c in el.children:
        if isinstance(c, NavigableString):
            parts.append(str(c))
        elif c.name == "a":
            parts.append(link(c, base))
        elif c.name == "br":
            parts.append(" ")
        elif c.name != "img":
            parts.append(inline(c, base))
    return clean("".join(parts))


def weights_table(ul: Tag) -> str | None:
    """`<li>Peso porcentual del Examen/Prueba Final&nbsp;60</li>` -> tabla con los porcentajes."""
    rows = []
    for li in ul.find_all("li", recursive=False):
        m = re.fullmatch(r"(Peso porcentual .*?)[\s\xa0:]+(\d+(?:[.,]\d+)?)", li.get_text(" ").strip(), re.S)
        if not m:
            return None
        rows.append((clean(m.group(1)), m.group(2)))
    if not rows:
        return None
    return "\n".join(["| Concepto | Peso (%) |", "|---|---|"] + [f"| {c} | {p} |" for c, p in rows])


def body_to_md(body: Tag, base: str) -> str:
    chunks: list[str] = []
    for c in body.children:
        if isinstance(c, NavigableString):
            t = clean(str(c))
            if t:  # rótulo suelto entre listas, p. ej. "Recursos Electrónicos *"
                chunks.append(f"**{t.rstrip(' *')}**" if len(t) < 80 else t)
            continue
        if c.name in ("br", "img", "script", "style"):
            continue
        if c.name == "textarea" or (c.name == "div" and "tarea" in (c.get("class") or [])):
            md = text_to_md(c.get_text())
            if md:
                chunks.append(md)
        elif c.name in ("ul", "ol"):
            tbl = weights_table(c)
            if tbl:
                chunks.append(tbl)
            else:
                items = [i for i in (inline(li, base) for li in c.find_all("li", recursive=False)) if i]
                if items:
                    chunks.append("\n".join(f"- {i}" for i in items))
        elif c.name == "a":
            if clean(c.get_text(" ")):
                chunks.append(link(c, base))
        elif c.name == "table":
            rows = [[clean(td.get_text(" ")).replace("|", "\\|") for td in tr.find_all(["th", "td"])] for tr in c.find_all("tr")]
            rows = [r for r in rows if r]
            if rows:
                w = max(len(r) for r in rows)
                rows = [r + [""] * (w - len(r)) for r in rows]
                chunks.append("\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
                                        + ["| " + " | ".join(r) + " |" for r in rows[1:]]))
        else:
            if c.find(["ul", "ol", "textarea", "table"]) or c.find("div", class_="tarea"):
                md = body_to_md(c, base)
            else:
                md = inline(c, base)
            if md:
                chunks.append(md)
    return "\n\n".join(chunks)


def parse(html: str, entry: dict) -> tuple[str, dict[str, bool]]:
    soup = BeautifulSoup(html, "lxml")
    base = entry["url_guia_docente"]
    general = soup.find("div", class_="contenedor_general")
    panels = soup.select("div.apartado")
    if general is None or not panels:
        raise ValueError("ficha sin apartados (guía no publicada)")
    head = general.find("div", class_="container-fluid", recursive=False) or general
    centers = [c for c in (clean(c.get_text(" ")) for c in head.find_all("center")) if c]
    year = next((c for c in centers if norm(c).startswith("curso academico")), None)
    title = next((c for c in centers if re.search(r"\(\d+\)$", c)), None)
    degree = next((c for c in centers if "Plan:" in c), None)
    if not title or f"({entry['codigo_asignatura']})" not in title:
        raise ValueError(f"la ficha no corresponde al código ({title!r})")
    if not year:
        raise ValueError("ficha sin curso académico")

    md: list[str] = [f"# {title}", ""]
    meta = [year]
    if degree:
        meta.append("Titulación: " + degree)
    for strong in head.find_all("strong"):
        label = clean(strong.get_text(" ")).rstrip(":").strip()
        if norm(label).startswith(DROP_META):
            continue
        value = clean("".join(str(s) for s in strong.next_siblings if isinstance(s, NavigableString)))
        if label and value:
            meta.append(f"{label}: {value}")
    md += [f"- {m}" for m in meta] + [""]

    found = dict.fromkeys(BLOCKS, False)
    for p in panels:
        hd = p.find("div", class_="panel-heading")
        bd = p.find("div", class_="panel-body")
        ttl = clean(hd.get_text(" ")) if hd else ""
        if not ttl or bd is None:
            raise ValueError("apartado sin título o sin cuerpo")
        body = body_to_md(bd, base)
        if not body:
            continue
        md += [f"## {ttl}", "", body, ""]
        b = block_of(ttl)
        if b:
            found[b] = True

    # Pie: dirección web de la asignatura o del departamento (si existe)
    for bold in general.find_all("b"):
        if norm(bold.get_text()).startswith("direccion web"):
            a = bold.find_next_sibling("a")
            if a and a.get("href"):
                md += ["## Dirección web para más información", "", link(a, base), ""]
    return "\n".join(md), found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    args = ap.parse_args()

    cat = load_catalog(SLUG)
    if not cat:
        print("Falta catalogo_urls.json: ejecuta antes discover_es_carlos_iii_madrid.py")
        return 2
    by_code = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    if args.all:
        codes = list(by_code)
    elif args.codes:
        codes = args.codes
    else:
        codes = SAMPLE[: (args.sample or 5)]

    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ok = fail = skip = denied = 0
    for code in codes:
        e = by_code.get(code)
        if e is None:
            print(f"{code}: FALLO no está en el catálogo")
            fail += 1
            continue
        if e["tipo_fuente"] == "sin_guia" or not e.get("url_guia_docente"):
            print(f"{code}: omitida (sin_guia) — {e['nombre_asignatura']}")
            skip += 1
            continue
        try:
            body, found = parse(http.get_text(e["url_guia_docente"]), e)
            write_markdown(SLUG, e, body, found)
            missing = [k for k, v in found.items() if not v]
            print(f"{code}: ok — {e['nombre_asignatura']} ({len(body)} car.)"
                  + (f" | sin: {', '.join(missing)}" if missing else ""))
            ok += 1
            denied = 0
        except (FetchError, ValueError, AttributeError) as ex:
            print(f"{code}: FALLO {ex}")
            fail += 1
            if re.search(r"HTTP (403|429)", str(ex)):
                denied += 1
                if denied >= 3:
                    print("El servidor responde 403/429 de forma persistente: se detiene la ejecución.")
                    break
    print(f"ok={ok} fallos={fail} omitidas={skip} | red/caché {http.stats}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
