#!/usr/bin/env python3
"""Fase 2 · Scraper — Università Politecnica delle Marche, Ingegneria Meccanica (L-9).

Por asignatura, 1 GET a la API JSON del catálogo Cineca (/api/v1/insegnamento, la misma
URL que `url_guia_docente`). La ficha trae, por cada "testo" (asignatura, módulo de un
corso integrato o partición de alumnos pares/impares), campos HTML en italiano (_it) y en
inglés (_en) y un `ordineTesti` con el orden de las secciones en la web. Se usa el idioma
`idioma_pagina` del catálogo (en si la versión inglesa está completa; si no, it).

Uso (desde la raíz del proyecto):
    python universidades/ec_i_ancona01__elec/scraper_ec_i_ancona01__elec.py --sample 5
    python universidades/ec_i_ancona01__elec/scraper_ec_i_ancona01__elec.py --codes TO001A TO0034
    python universidades/ec_i_ancona01__elec/scraper_ec_i_ancona01__elec.py --all
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
SLUG = "ec_i_ancona01__elec"

# Muestra fija y diversa. El año 3 (A.A. 2027/28) y el TFG ("PROVA FINALE") aún no tienen
# syllabus publicado (sin_guia), así que la muestra cubre los años 1-2 y los casos atípicos.
SAMPLE = []   # se elige automáticamente (diversa) a partir del catálogo

SECTION = {  # clave de ordineTesti -> (campo, título it, título en, bloque)
    "CONTENUTI": ("contenuti", "Contenuti", "Contents", "contents"),
    "PROGR_EST": ("programmazione_estesa", "Programma esteso", "Extended programme", "contents"),
    "OBIETT_FORM": ("obiettivi_formativi", "Obiettivi formativi", "Learning objectives", "learning_outcomes"),
    "PREREQ": ("prerequisiti", "Prerequisiti", "Prerequisites", "prerequisites"),
    "METODI_DID": ("metodi_didattici_est", "Metodi didattici", "Teaching methods", None),
    "MOD_VER_APPR": ("verifica_apprendimento", "Modalità di verifica dell'apprendimento",
                     "Assessment methods", "assessment"),
    "TESTI_RIF": ("testi", "Testi di riferimento", "Reference texts", "bibliography"),
    "ALTRO": ("altro", "Altre informazioni", "Other information", None),
    "OB_SVIL_SOS": ("obiettivi_svil_sos_des", "Obiettivi Agenda 2030 per lo sviluppo sostenibile",
                    "2030 Agenda Sustainable Development Goals", None),
}
DEFAULT_ORDER = ["Lingua insegnamento", "CONTENUTI", "TESTI_RIF", "OBIETT_FORM", "PREREQ", "METODI_DID",
                 "ALTRO", "MOD_VER_APPR", "PROGR_EST", "OB_SVIL_SOS"]
L = {  # etiquetas de la cabecera
    "it": {"info": "Informazioni generali", "cds": "Corso di studio", "curr": "Percorso", "anno": "Anno di corso",
           "aa": "Anno accademico di erogazione", "per": "Periodo", "cfu": "CFU", "ore": "Ore", "ssd": "SSD",
           "tipo": "Tipo attività", "amb": "Ambito", "esa": "Tipo esame", "val": "Valutazione",
           "freq": "Frequenza", "lang": "Lingua insegnamento", "did": "Metodi didattici", "mod": "Moduli",
           "part": "Partizione", "modulo": "Modulo", "ci": "Corso integrato (parte comune)"},
    "en": {"info": "General information", "cds": "Degree programme", "curr": "Curriculum", "anno": "Year of study",
           "aa": "Academic year of delivery", "per": "Period", "cfu": "ECTS", "ore": "Hours", "ssd": "Scientific sector (SSD)",
           "tipo": "Type of activity", "amb": "Area", "esa": "Exam type", "val": "Grading",
           "freq": "Attendance", "lang": "Language of instruction", "did": "Teaching methods", "mod": "Modules",
           "part": "Partition", "modulo": "Module", "ci": "Integrated course (common part)"},
}
# Línea con datos de contacto/horario de recepción de un docente (privacidad).
_STAFF_LINE = re.compile(r"^\W*(?:ricevimento|orario di ricevimento|office hours|receiving hours|docente|"
                         r"lecturer|teacher|professor|prof\.)\b[^\n]{0,200}$", re.I)


class GuideError(RuntimeError):
    pass


# ------------------------------------------------------------------ HTML -> Markdown
BLOCK = {"p", "div", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "td", "th",
         "blockquote", "pre", "hr", "section"}
_WS = re.compile(r"[ \t\r\n\f\v ​   ]+")


def inline(node, bold: bool = False) -> str:
    if isinstance(node, Comment):
        return ""
    if isinstance(node, NavigableString):
        return _WS.sub(" ", str(node))
    if not isinstance(node, Tag) or node.name in ("script", "style"):
        return ""
    if node.name == "br":
        return "\n"
    is_b = node.name in ("b", "strong")
    s = "".join(inline(c, bold or is_b) for c in node.children)
    if node.name in BLOCK:
        return "\n" + s + "\n"
    if is_b and not bold and s.strip():
        return "\n".join(f"**{p.strip()}**" if p.strip() else p for p in s.split("\n"))
    if node.name in ("i", "em") and s.strip():
        return "\n".join(f"*{p.strip()}*" if p.strip() else p for p in s.split("\n"))
    if node.name == "a":
        href = (node.get("href") or "").strip()
        if href.startswith("http") and s.strip() and s.strip() != href:
            return f"[{s.strip()}]({href})"
    return s


def clean(s: str) -> str:
    lines = [re.sub(r" {2,}", " ", ln).strip() for ln in s.split("\n")]
    out: list[str] = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    return "\n".join(out).strip()


def blocks(root: Tag) -> list[str]:
    out: list[str] = []
    buf: list = []

    def flush():
        t = clean("".join(inline(x) for x in buf))
        buf.clear()
        if t:
            out.append(t.replace("\n\n", "\n").replace("\n", "  \n"))

    for c in root.children:
        if isinstance(c, Comment):
            continue
        if isinstance(c, NavigableString) or (isinstance(c, Tag) and c.name not in BLOCK
                                              and c.find(list(BLOCK)) is None):
            buf.append(c)
            continue
        flush()
        if c.name not in BLOCK:  # span/font que envuelve bloques
            out.extend(blocks(c))
        elif c.name in ("ul", "ol"):
            out.append(list_md(c))
        elif re.fullmatch(r"h[1-6]", c.name):
            t = clean(inline(c, True)).replace("\n", " ")
            if t:
                out.append(f"#### {t}")
        elif c.name == "hr":
            continue
        elif c.find(list(BLOCK)) is not None:
            out.extend(blocks(c))
        else:
            t = clean("".join(inline(x) for x in c.children))
            if t:
                out.append(("- " + t.replace("\n", " ")) if c.name == "li" else t.replace("\n", "  \n"))
    flush()
    return [b for b in out if b.strip()]


def list_md(lst: Tag, indent: str = "") -> str:
    ordered, n, out = lst.name == "ol", 1, []
    for li in lst.find_all("li", recursive=False):
        subs = [s for s in li.find_all(["ul", "ol"], recursive=False)]
        for s in subs:
            s.extract()
        txt = clean("".join(inline(x) for x in li.children)).replace("\n", " ")
        if txt:
            out.append(f"{indent}{f'{n}. ' if ordered else '- '}{txt}")
            n += 1
        for s in subs:
            out.append(list_md(s, indent + "   "))
    return "\n".join(x for x in out if x.strip())


def html_to_md(html: str | None) -> str:
    if not html or not html.strip():
        return ""
    soup = BeautifulSoup(html, "lxml")
    root = soup.body or soup
    parts = [p for p in blocks(root) if not _STAFF_LINE.match(p)]
    return "\n\n".join(parts).strip()


# ------------------------------------------------------------------ ficha -> Markdown
def g(d: dict, key: str, lang: str) -> str:
    """Campo bilingüe con respaldo al italiano si el inglés falta."""
    v = d.get(f"{key}_{lang}") if lang == "en" else None
    return (v or d.get(f"{key}_it") or "").strip()


def testo_field(t: dict, field: str, lang: str) -> tuple[str, bool]:
    """HTML del campo (con o sin prefijo mod_) en `lang`; respaldo it. Devuelve (md, fallback)."""
    for pref in ("", "mod_"):
        en, it = t.get(f"{pref}{field}_en"), t.get(f"{pref}{field}_it")
        if en is not None or it is not None:
            if lang == "en" and html_to_md(en):
                return html_to_md(en), False
            md_it = html_to_md(it)
            return md_it, bool(lang == "en" and md_it)
    return "", False


def altri_testi(t: dict, lang: str) -> list[tuple[str, str]]:
    """Campos libres de la ficha: variante clásica (altri_testi) o 'ugov' (altri_testi_ugov, p. ej. UnivAQ)."""
    out = []
    items = (t.get("altri_testi") or t.get("mod_altri_testi") or t.get("altri_testi_ugov")
             or t.get("mod_altri_testi_ugov") or [])
    for a in items:
        lab = (a.get(f"etichetta_{lang}") or a.get("etichetta_it") or a.get(f"ugov_etichetta_{lang}")
               or a.get("ugov_etichetta_it") or "").strip()
        md = (html_to_md(a.get(f"altri_testi_{lang}")) or html_to_md(a.get("altri_testi_it"))
              or html_to_md(a.get(f"ugov_altri_testi_{lang}")) or html_to_md(a.get("ugov_altri_testi_it")))
        if lab and md:
            out.append((lab, md))
    return out


def render_testo(t: dict, lang: str, found: dict[str, bool], level: str) -> tuple[str, list[str]]:
    lab = L[lang]
    order = sorted((t.get("ordineTesti") or {}).items(), key=lambda kv: kv[1])
    keys = [k for k, _ in order] or DEFAULT_ORDER
    keys += [k for k in SECTION if k not in keys]           # nunca perder una sección no listada
    parts, fallbacks, done_altri = [], [], False
    for k in keys:
        if k in SECTION:
            field, t_it, t_en, block = SECTION[k]
            md, fb = testo_field(t, field, lang)
            if k == "OB_SVIL_SOS" and t.get("elenco_obiettivi_svil_sos"):
                goals = ", ".join(x.strip() for x in t["elenco_obiettivi_svil_sos"] if x.strip())
                md = (md + "\n\n" if md else "") + ("SDG: " if lang == "en" else "Obiettivi: ") + goals
            if not md:
                continue
            if fb:
                fallbacks.append(t_en)
            if block:
                found[block] = True
            parts.append(f"{level} {t_en if lang == 'en' else t_it}\n\n{md}")
        elif not done_altri:                                   # 'Lingua insegnamento' y otros altri_testi
            done_altri = True
            for name, md in altri_testi(t, lang):
                parts.append(f"{level} {lab['lang'] if name == 'Lingua insegnamento' else name}\n\n{md}")
    return "\n\n".join(parts), fallbacks


def header(ins: dict, entry: dict, lang: str) -> str:
    lab = L[lang]
    rows = [
        (lab["cds"], f"{g(ins, 'corso_des', lang)} ({ins.get('cdsCod')})"),
        (lab["curr"], g(ins, "corso_percorso_des", lang)),
        (lab["anno"], str(ins.get("corso_anno") or entry.get("curso") or "")),
        (lab["aa"], f"{ins['aa']}/{int(ins['aa']) + 1}" if str(ins.get("aa", "")).isdigit() else ""),
        (lab["per"], g(ins, "periodo_didattico", lang) or "; ".join(dict.fromkeys(
            g(f, "periodo_didattico", lang) for f in ins.get("frazioni") or [] if g(f, "periodo_didattico", lang)))),
        (lab["cfu"], str(ins.get("crediti") or "")),
        (lab["ore"], "; ".join(f"{x.get('tipo_durata_des_' + lang) or x.get('tipo_durata_des_it')}: {x['valore']}"
                               for x in (ins.get("durata") or {}).get("tipo", []))),
        (lab["ssd"], ins.get("ssd") or ""),
        (lab["tipo"], g(ins, "tipo", lang)),
        (lab["amb"], g(ins, "ambito", lang)),
        (lab["esa"], g(ins, "tipoEsaDes", lang)),
        (lab["val"], g(ins, "valutazione", lang)),
        (lab["freq"], g(ins, "frequenza", lang)),
        (lab["did"], g(ins, "metodi_didattici", lang)),
    ]
    lines = [f"## {lab['info']}", ""] + [f"- **{k}:** {v}" for k, v in rows if v and v.strip()]
    mods = ins.get("moduli") or []
    if mods:
        lines += ["", f"### {lab['mod']}", "", f"| Cod. | {lab['modulo']} | {lab['cfu']} | {lab['per']} | {lab['ore']} |",
                  "| --- | --- | --- | --- | --- |"]
        for m in mods:
            lines.append(f"| {m.get('udCod') or m.get('cod')} | {g(m, 'des', lang)} | {m.get('crediti', '')} | "
                         f"{g(m, 'periodo_didattico', lang)} | {(m.get('durata') or {}).get('totale', '')} |")
    return "\n".join(lines)


LINE_PII = re.compile(r"(?i)^\s*(orario di ricevimento|ricevimento|e-?mail\s*:|contatti|contacts?\s*:|\[docente\]|.*(office hours|reception hours|orario di ricevimento|previo appuntamento|riceve (su|previo)))")

HEAD_PATTERNS = {
    "contents": "content|syllabus|programme|program|contenut|programma",
    "learning_outcomes": "learning outcome|learning objective|obiettiv|risultati di apprendimento|knowledge and understanding|conoscenza e comprensione",
    "assessment": "examination|assessment|evaluation|valutazion|esame|verifica",
    "bibliography": "reference|texts|bibliograph|testi|reading|material",
    "prerequisites": "prerequisit|propedeutic|requisit",
}


def build_markdown(ins: dict, entry: dict) -> tuple[str, dict[str, bool], list[str]]:
    lang = entry["idioma_pagina"] if entry["idioma_pagina"] in ("it", "en") else "it"
    lab = L[lang]
    found = {"contents": False, "learning_outcomes": False, "assessment": False,
             "bibliography": False, "prerequisites": False}
    testi = ins.get("testiTotali") or []
    if not testi:
        raise GuideError("sin testiTotali (syllabus no publicado)")
    mods = {m.get("udCod") or m.get("cod"): m for m in ins.get("moduli") or []}
    frz = {f.get("cod"): f for f in ins.get("frazioni") or []}

    out = [f"# {g(ins, 'des', lang)} ({ins.get('adCod')})", "", header(ins, entry, lang)]
    rendered, notes = [], []
    for t in testi:
        body, fb = render_testo(t, lang, found, "###")
        notes += fb
        if not body:
            continue
        key = t.get("chiave_cod")
        ud = t.get("chiave_udCod")
        if key is None:
            title = lab["ci"] if mods else None
        elif t.get("chiave_domPartCod"):                    # partición de alumnos (matricole pari/dispari…)
            f = frz.get(key, {})
            title = f"{lab['part']}: {g(f, 'des', lang) or key}"
        else:
            m = mods.get(ud, {})
            title = f"{lab['modulo']}: {g(m, 'des', lang) or ud} ({ud})"
        dup = next((r for r in rendered if r[1] == body), None)
        if dup is not None:                                   # partición idéntica: no repetir el texto
            dup[0].append(title)
            continue
        rendered.append(([title] if title else [], body))
    for titles, body in rendered:
        if titles:
            out += ["", "## " + " / ".join(titles)]       # secciones en nivel ###
        else:
            body = re.sub(r"(?m)^#### ", "### ", re.sub(r"(?m)^### ", "## ", body))  # ficha simple: un nivel menos
        out += ["", body]
    sin_texto = [u for u in mods if u not in {t.get("chiave_udCod") for t in testi}]
    for u in sin_texto:  # módulo listado sin syllabus publicado en la fuente
        out += ["", f"## {lab['modulo']}: {g(mods[u], 'des', lang) or u} ({u})", "",
                "> Syllabus not published in the source catalogue." if lang == "en"
                else "> Scheda dell'insegnamento non pubblicata nel catalogo."]
    if notes:
        msg = ("Note: the following sections are only available in Italian and are given in Italian: "
               if lang == "en" else "")
        if msg:
            out += ["", f"> {msg}{', '.join(sorted(set(notes)))}."]
    text = "\n".join(out)
    for blk, pat in HEAD_PATTERNS.items():          # secciones con títulos propios de cada universidad (altri_testi)
        if re.search(r"(?im)^#+ .*(" + pat + ")", text):
            found[blk] = True
    out = [ln for ln in "\n".join(out).split("\n") if not LINE_PII.match(ln)]   # horarios de tutoría / contactos
    return redact_staff("\n".join(out), ins).strip() + "\n", found, notes


def staff_tokens(ins: dict) -> set[str]:
    """Nombres y apellidos (>3 letras) de todo el personal listado en la ficha JSON."""
    people = []
    for holder in [ins, *(ins.get("frazioni") or []), *(ins.get("moduli") or [])]:
        for k in ("docenti", "responsabili", "titolari"):
            people += holder.get(k) or []
    return {tok for p in people for tok in re.findall(r"[^\W\d_]{4,}", p.get("des") or "")}


def redact_staff(md: str, ins: dict) -> str:
    """Sustituye las menciones a docentes del curso en texto libre (p. ej. 'Prof. Nombre Apellido',
    también dentro de URLs personales) por [docente]. Solo afecta a nombres que el propio JSON
    lista como personal del curso, en palabras que empiezan por mayúscula o dentro de URLs."""
    toks = staff_tokens(ins)
    if not toks:
        return md
    alt = "|".join(sorted((re.escape(t) for t in toks), key=len, reverse=True))
    word = re.compile(rf"(?<![\w])(?:(?:Prof(?:\.ssa|essor|essa)?\.?|Dott(?:\.ssa)?\.?|Dr\.?)\s+)?"
                      rf"(?:(?i:{alt}))(?:\s+(?i:{alt}))*(?![\w])")

    def repl(m: re.Match) -> str:
        s = m.group(0)
        core = re.sub(r"^\S+\s+", "", s) if re.match(r"(?i)prof|dott|dr", s) and " " in s else s
        return "[docente]" if core[:1].isupper() else s

    md = word.sub(repl, md)
    # URLs personales con el apellido de un docente (p. ej. https://www.apellido.org/...)
    url_tok = re.compile(rf"(https?://[^\s)>\]]*?)(?i:{alt})", re.I)
    return url_tok.sub(lambda m: m.group(1) + "[docente]", md)


# ------------------------------------------------------------------ main
def main() -> int:
    ap = argparse.ArgumentParser()
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--sample", type=int, default=None)
    grp.add_argument("--all", action="store_true")
    grp.add_argument("--codes", nargs="+")
    args = ap.parse_args()

    cat = load_catalog(SLUG)
    if cat is None:
        print("Falta catalogo_urls.json: ejecuta discover_ec_i_ancona01__elec.py", file=sys.stderr)
        return 2
    rows = {e["codigo_asignatura"]: e for e in cat["asignaturas"]}
    if args.all:
        codes = list(rows)
    elif args.codes:
        codes = args.codes
    else:
        guides=[c for c,e in rows.items() if e["tipo_fuente"]!="sin_guia"]
        n=args.sample or 5
        codes=[guides[int(i*(len(guides)-1)/max(n-1,1))] for i in range(n)] if len(guides)>n else guides

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
            ins = http.get_json(e["url_guia_docente"])
            md, found, notes = build_markdown(ins, e)
            p = write_markdown(SLUG, e, md, found)
            miss = [k for k, v in found.items() if not v]
            print(f"{code}: ok [{e['idioma_pagina']}] {len(md)} chars -> {p.name}"
                  + (f" | faltan: {', '.join(miss)}" if miss else "")
                  + (f" | it-fallback: {', '.join(notes)}" if notes else ""))
        except (FetchError, GuideError, KeyError, ValueError) as ex:
            print(f"{code}: FAIL {type(ex).__name__}: {ex}")
            failed += 1
    print("HTTP:", http.stats)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
