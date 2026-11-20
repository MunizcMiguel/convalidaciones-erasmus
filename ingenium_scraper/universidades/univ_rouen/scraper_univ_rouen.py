#!/usr/bin/env python3
"""Fase 2 · Scraper — Université de Rouen Normandie, Licence Mécanique, parcours Mécanique-Énergétique.

Cada fila del catálogo es una UE (o una opción de UE au choix) del catálogo ODF Ametys
(formation.univ-rouen.fr). Por fila:
  1. página de la UE -> metadatos (ECTS, semestre, horas) + "Liste des enseignements"
  2. página de cada élément listado -> Description, Objectifs, Pré-requis,
     Contrôle des connaissances, Compétences visées, horas...
     (si la UE no lista éléments, la propia página de la UE es la ficha)
  3. solo L2 y L3: los PDF oficiales "*_L{n}_prog.pdf" (enlazados desde la página del parcours)
     aporta el reparto de evaluación (% CC / % TP) y horas por UE, porque las fichas
     ODF de L2 y L3 solo publican horas.

Uso (desde la raíz del proyecto):
    python universidades/univ_rouen/scraper_univ_rouen.py --sample 5
    python universidades/univ_rouen/scraper_univ_rouen.py --codes L5MCAVC2 LBVZT6JH
    python universidades/univ_rouen/scraper_univ_rouen.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from bs4 import BeautifulSoup, Comment, NavigableString, Tag  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "univ_rouen"
PDF_LINK_RE = re.compile(r'href="([^"]*_L(\d)_prog\.pdf[^"]*)"')

# Muestra fija y diversa: L1 física/mates, L2 mecánica, L3 núcleo mecánico, L3 con prácticas (stage),
# opción de UE au choix (L1) y opción de especialización (L2, página sin éléments).
SAMPLE = [
    "L5MCAVC2",  # UE1 Mécanique du point — L1 S2, física básica (2 éléments)
    "L5MCBD8Q",  # UE3 Mécanique — L2 S3, mecánica de sólidos
    "LBVZT6JH",  # UE2 Mécanique des solides déformables — L3 S6, núcleo ingeniería mecánica
    "LBVZT9VP",  # UE4 Méthodes et communication — L3 S6, incluye Stage (4 ECTS), atípica
    "L850MBB6",  # Astrophysique et HMS — L1 S1, opción de UE au choix
    # reserva si --sample > 5
    "L5MCBYNV",  # RdM & transferts thermiques — L2 S4, opción sin éléments
    "L5MCAQLS",  # Bases de l'analyse mathématique — L1 S1, matemáticas
    "LBVZSXNZ",  # Ingénierie mathématique — L3 S5
]

# Títulos de sección (normalizados) -> bloque
BLOCKS = {
    "description": "contents",
    "contenu": "contents",
    "programme": "contents",
    "objectifs": "learning_outcomes",
    "competences visees": "learning_outcomes",
    "controle des connaissances": "assessment",
    "modalites d'evaluation": "assessment",
    "bibliographie": "bibliography",
    "pre-requis obligatoires": "prerequisites",
    "pre-requis recommandes": "prerequisites",
}
KEEP_OTHER = {"heures d'enseignement", "lieu(x)", "campus", "en bref", "informations complementaires", "langue(s) d'enseignement",
              "methodes d'enseignement", "modalites pedagogiques"}
SKIP_TITLES = {"liste des enseignements"}  # se vuelca como subsecciones por élément
DROP_TITLES = {"contact", "contacts", "responsable", "responsables", "intervenants", "enseignants"}
META_SKIP = {"composante"}


def fold(s: str) -> str:
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip().lower().replace("’", "'")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


# ------------------------------------------------------------------ HTML -> Markdown (richtext Ametys)
def inline(node) -> str:
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", str(node).replace("\xa0", " "))
    if not isinstance(node, Tag) or node.name in ("script", "style"):
        return ""
    if node.name == "br":
        return "\n"
    s = "".join(inline(c) for c in node.children)
    if node.name in ("strong", "b") and s.strip():
        return f"**{s.strip()}** " if s.endswith(" ") else f"**{s.strip()}**"
    if node.name == "a":
        href = node.get("href", "")
        if href.startswith("http") and s.strip() and s.strip() != href:
            return f"[{s.strip()}]({href})"
    return s  # <em> se descarta como cursiva: Ametys la usa de forma decorativa


def clean(s: str) -> str:
    lines = [re.sub(r" {2,}", " ", ln).strip() for ln in s.split("\n")]
    return "\n".join(ln for ln in lines if ln).strip()


def table_md(t: Tag) -> str:
    rows = []
    for tr in t.find_all("tr"):
        cells = [clean(inline(c)).replace("\n", " <br> ").replace("|", r"\|") for c in tr.find_all(["td", "th"])]
        if any(cells):
            rows.append(cells)
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + " --- |" * w]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def list_md(lst: Tag, indent: str = "") -> str:
    out = []
    n = 1
    for li in lst.find_all("li", recursive=False):
        mark = f"{n}. " if lst.name == "ol" else "- "
        n += 1
        txt = clean("".join(inline(c) for c in li.children if not (isinstance(c, Tag) and c.name in ("ul", "ol"))))
        out.append(indent + mark + txt.replace("\n", " "))
        for sub in li.find_all(["ul", "ol"], recursive=False):
            out.append(list_md(sub, indent + "  "))
    return "\n".join(o for o in out if o.strip())


def rich_md(root: Tag) -> str:
    parts: list[str] = []
    buf: list = []

    def flush():
        t = clean("".join(inline(x) for x in buf))
        buf.clear()
        if t:
            parts.append(t.replace("\n", "  \n"))

    for c in root.children:
        if isinstance(c, Tag) and c.name in ("ul", "ol"):
            flush(); parts.append(list_md(c))
        elif isinstance(c, Tag) and c.name == "table":
            flush(); parts.append(table_md(c))
        elif isinstance(c, Tag) and re.fullmatch(r"h[1-6]", c.name):
            flush(); parts.append(f"**{clean(inline(c))}**")
        elif isinstance(c, Tag) and c.name in ("p", "div", "blockquote"):
            flush()
            if c.find(["ul", "ol", "table", "p", "div"]):
                parts.append(rich_md(c))
            else:
                t = clean(inline(c))
                if t:
                    parts.append(t.replace("\n", "  \n"))
        else:
            buf.append(c)
    flush()
    return "\n\n".join(p for p in parts if p.strip())


# ------------------------------------------------------------------ página ODF -> secciones
def parse_page(html: str) -> tuple[str, list[tuple[str, str]], list[tuple[str, str]], list[tuple[str, str]]]:
    """(título, metadatos [(etiqueta, valor)], secciones [(título, md)], éléments [(título, url)])."""
    soup = BeautifulSoup(html, "lxml")
    title = norm(soup.select_one("h1").get_text(" "))
    main = soup.select_one(".ametys-main-content")
    if main is None:
        raise ValueError("sin .ametys-main-content")
    meta = []
    for it in main.select(".ametys-benefits-alt__item"):
        lab = norm(it.select_one(".ametys-benefits-alt__item-title").get_text(" "))
        val = norm(it.select_one(".ametys-benefits-alt__item-text").get_text(" "))
        if fold(lab) not in META_SKIP and val:
            meta.append((lab, val))
    sections: list[tuple[str, str]] = []
    elems: list[tuple[str, str]] = []
    cols = main.select(".ametys-courses-single-two-columns-content__body, "
                       ".ametys-courses-single-two-columns-content__sidebar")
    for col in cols:
        for sec in col.find_all("section", recursive=False):
            h = sec.select_one("h2.ametys-section-sub-title, h2.ametys-section-title, h3.ametys-richtext-title-4")
            if h is None:
                raise ValueError(f"sección sin título: {norm(sec.get_text(' '))[:80]!r}")
            st = norm(h.get_text(" "))
            key = fold(st)
            if key in DROP_TITLES:
                continue
            if key in SKIP_TITLES:
                for a in sec.select("h2.ametys-accordion__item-title a[href]"):
                    elems.append((norm(a.get_text(" ")), a["href"]))
                continue
            if key not in BLOCKS and key not in KEEP_OTHER:
                raise ValueError(f"sección no contemplada: {st!r}")
            if key == "en bref":  # tabla etiqueta/valor (iconos en la 1.ª celda)
                items = []
                for tr in sec.select("table tr"):
                    th, tds = tr.find("th"), tr.find_all("td")
                    if th and tds:
                        items.append(f"- **{norm(th.get_text(' '))}** : {norm(tds[-1].get_text(' '))}")
                if items:
                    sections.append((st, "\n".join(items)))
                continue
            parts = sec.select_one("ul.ametys-coursepart")
            if parts is not None:  # horas: tabla
                rows = ["| Type | Intitulé | Heures |", "| --- | --- | --- |"]
                for li in parts.find_all("li", recursive=False):
                    g = lambda c: norm(li.select_one(c).get_text(" ")) if li.select_one(c) else ""  # noqa: E731
                    rows.append(f"| {g('.ametys-coursepart__item-title')} | {g('.ametys-coursepart__item-text')} "
                                f"| {g('.ametys-coursepart__item-badge')} |")
                sections.append((st, "\n".join(rows)))
                continue
            body = sec.select_one(".ametys-limited-content__body")
            if body is None:
                body = sec.select_one(".ametys-richtext")
                h.extract()
            md = rich_md(body) if body is not None else ""
            if md:
                sections.append((st, md))
    return title, meta, sections, elems


# ------------------------------------------------------------------ PDF de programa (L2, L3)
PDF_YEARS = (2, 3)  # L1 ya publica fichas completas en HTML; su PDF mezcla opciones de 2 facultades
_DETAIL = re.compile(r"^\(|^\d+(?:[.,]\d+)?\s*(?:h\b|semaine)")


def prog_pdf_blocks(http: PoliteClient, plan_url: str) -> dict:
    """{(curso, semestre relativo 1|2, nº UE): [(nombre, [detalles])]} de los PDF "*_L{n}_prog.pdf"
    enlazados en la página del parcours (página 1: tabla a dos columnas, S impar | S par)."""
    html = http.get_text(plan_url)
    out: dict = {"_url": {}}
    for m in PDF_LINK_RE.finditer(html):
        year = int(m.group(2))
        if year not in PDF_YEARS or year in out["_url"]:
            continue
        url = urljoin(plan_url, m.group(1).replace("&amp;", "&"))
        out["_url"][year] = url
        with pdfplumber.open(http.get_file(url)) as pdf:
            p = pdf.pages[0]
            ws = p.extract_words()
            ue = [w for w in ws if w["text"] == "UE"]
            mid = max(w["x0"] for w in ue) - 3            # borde izquierdo de la 2.ª columna
            top = min(w["top"] for w in ue) - 2
            stops = [w["top"] for w in ws if w["text"] == "Lieu" and w["x0"] < 80]
            stops += [w["top"] for i, w in enumerate(ws[:-1]) if w["text"] == "CM" and ws[i + 1]["text"] == ":"]
            bot = min(stops + [p.height + 2]) - 2           # pie: "Lieu d'enseignement" o leyenda "CM : ..."
            for semrel, (a, b) in enumerate(((0, mid), (mid, p.width)), start=1):
                items = None
                for ln in (p.crop((a, top, b, bot)).extract_text() or "").splitlines():
                    ln = ln.strip()
                    if not ln:
                        continue
                    mm = re.match(r"UE\s*(\d+)\s*:\s*(.*?)\s*(\d+)?$", ln)
                    if mm:
                        items = [[f"UE {mm.group(1)} : {mm.group(2)}", [], mm.group(3)]]
                        out[(year, semrel, int(mm.group(1)))] = items
                    elif items is None:
                        raise ValueError(f"PDF L{year}: línea antes de la primera UE: {ln!r}")
                    elif _DETAIL.match(ln):
                        items[-1][1].append(ln)
                    elif re.match(r"^[a-zà-ÿ&]", ln) and not items[-1][1]:
                        # nombre partido en dos líneas ("thermiques", "& Mécanique des fluides"):
                        # los nombres de UE/élément empiezan siempre por mayúscula o cifra
                        items[-1][0] += " " + ln
                    else:
                        items.append([ln, [], None])
    return out


# ------------------------------------------------------------------ composición
def render(entry: dict, http: PoliteClient, pdfb: dict | None) -> tuple[str, dict[str, bool]]:
    url = entry["url_guia_docente"]
    title, meta, sections, elems = parse_page(http.get_text(url))
    found = {b: False for b in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    md = [f"# {title}", ""]
    md += [f"- **{k}** : {v}" for k, v in meta]
    md.append(f"- **Semestre (plan)** : {entry['curso_semestre']}")

    def add_sections(secs, level):
        for st, body in secs:
            b = BLOCKS.get(fold(st))
            if b:
                found[b] = True
            md.extend(["", f"{'#' * level} {st}", "", body])

    add_sections(sections, 2)
    for etitle, href in elems:
        et, emeta, esecs, sub = parse_page(http.get_text(urljoin(url, href)))
        if sub:
            raise ValueError(f"élément con sub-éléments: {et}")
        md.extend(["", f"## Élément : {et}", ""])
        md += [f"- **{k}** : {v}" for k, v in emeta]
        add_sections(esecs, 3)
    # L2/L3: reparto de evaluación, horas y coeficientes del PDF oficial del programa del año
    curso = entry.get("curso")
    um = re.match(r"UE\s*(\d+)\b", entry["nombre_asignatura"]) or re.search(r"\(UE\s*(\d+)\b", entry["curso_semestre"])
    if pdfb is not None and curso in PDF_YEARS and um:
        key = (curso, (entry["semestre"] - 1) % 2 + 1, int(um.group(1)))
        items = pdfb.get(key)
        if not items:
            raise ValueError(f"UE {key} no encontrada en el PDF de programa")
        md.extend(["", f"## Programme L{curso} (fiche PDF officielle) : modalités d'évaluation et volumes horaires", "",
                   f"Source : <{pdfb['_url'][curso]}>", "",
                   "Abréviations de la source : CM = cours magistral, TD = travaux dirigés, TP = travaux pratiques, "
                   "CC = contrôle continu.", ""])
        for i, (name, det, ects) in enumerate(items):
            ind = "" if i == 0 else "  "
            md.append(f"{ind}- **{name}**" + (f" ({ects} ECTS)" if ects else "")
                      + (" — " + " — ".join(det) if det else ""))
        if any("%" in d for _, det, _e in items for d in det):
            found["assessment"] = True
    return "\n".join(md), found


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    args = ap.parse_args()

    cat = load_catalog(SLUG)
    rows = cat["asignaturas"]
    by_code = {r["codigo_asignatura"]: r for r in rows}
    if args.all:
        todo = rows
    elif args.codes:
        missing = [c for c in args.codes if c not in by_code]
        if missing:
            sys.exit(f"Códigos no catalogados: {missing}")
        todo = [by_code[c] for c in args.codes]
    else:
        todo = [by_code[c] for c in SAMPLE[: args.sample]]

    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdfb = (prog_pdf_blocks(http, cat["meta"]["url_plan_estudios"])
            if any(r.get("curso") in PDF_YEARS for r in todo) else None)
    fails = 0
    for r in todo:
        code = r["codigo_asignatura"]
        if r["tipo_fuente"] == "sin_guia":
            print(f"{code}: skip (sin_guia)")
            continue
        try:
            body, found = render(r, http, pdfb)
            out = write_markdown(SLUG, r, body, found)
            miss = [k for k, v in found.items() if not v]
            print(f"{code}: ok -> {out.name} ({len(body)} chars; sin: {', '.join(miss) or '-'})")
        except (FetchError, ValueError, AttributeError) as e:
            fails += 1
            print(f"{code}: FAIL {type(e).__name__}: {e}")
    print("HTTP:", http.stats)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
