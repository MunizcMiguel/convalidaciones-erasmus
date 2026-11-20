"""Fase 2 (Scraper) - Hochschule Karlsruhe (HKA) - Maschinenbau M.Sc. (MECB).

Convierte cada ficha de modulo del Modulhandbuch (un unico PDF compartido, en aleman)
en Markdown limpio: un encabezado por campo, listas como listas, modulos de varias
paginas cosidos sin pies de pagina y lineas partidas reunidas.

Uso (desde la raiz del proyecto):
    python universidades/ec_d_karlsru05__elec/scraper_ec_d_karlsru05__elec.py --sample 5
    python universidades/ec_d_karlsru05__elec/scraper_ec_d_karlsru05__elec.py --codes MECB110 MECB740
    python universidades/ec_d_karlsru05__elec/scraper_ec_d_karlsru05__elec.py --all
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import REQUIRED_BLOCKS, load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_karlsru05__elec"

# Muestra piloto fija y diversa:
SAMPLE = ["MECB110", "MECB330", "MECB410A", "MECB430", "MECB740"]

# ---------------------------------------------------------------- etiquetas (lista cerrada)
# clave -> (regex de la etiqueta, tipo). Tipos: meta (linea corta), section (encabezado propio),
# person (se descarta: dato personal), lv (abre un bloque de Lehrveranstaltung), marker (sin valor).
LABELS: list[tuple[str, str, str]] = [
    ("Modulbeschreibung", r"Modulbeschreibung", "marker"),
    ("SPO-Bezeichnung", r"SPO-Bezeichnung", "meta"),
    ("Modulverantwortliche", r"Modulverantwortliche(?:\(r\)|r)?", "person"),
    ("Modulumfang (ECTS)", r"Modulumfang \(ECTS\)", "meta"),
    ("Modulumfang (SWS)", r"Modulumfang \(SWS\)", "meta"),
    ("Einordnung (Semester)", r"Einordnung \(Semester\)", "meta"),
    ("Inhaltliche Voraussetzungen", r"Inhaltliche Voraussetzungen", "section"),
    ("Voraussetzungen nach SPO", r"Voraussetzungen nach SPO", "section"),
    ("Lernergebnisse und Kompetenzen", r"Lernergebnisse und Kompetenzen", "section"),
    ("Prüfungsleistungen", r"Prüfungsleistungen", "section"),
    ("Regelungen für das Wahlmodul", r"Regelungen für das Wahlmodul", "section"),
    ("Lehrveranstaltung", r"Lehrveranstaltung", "lv"),
    ("LV-Bezeichnung", r"LV-Bezeichnung", "meta"),
    ("Dozent/in", r"Dozent(?:/in|in)?", "person"),
    ("Umfang (SWS)", r"Umfang \(SWS\)", "meta"),
    ("Umfang (CP)", r"Umfang \(CP\)", "meta"),
    ("Turnus", r"Turnus", "meta"),
    ("Art und Modus", r"Art und Modus", "meta"),
    ("Lehrsprache", r"Lehrsprache", "meta"),
    ("Studieninhalte", r"Studieninhalte", "section"),
    ("Empfohlene Literatur", r"Empfohlene Literatur", "section"),
    ("Anmerkungen", r"Anmerkungen", "section"),
]
RE_LABELS = [(k, re.compile(rf"^{rx}\s*:\s*(.*)$"), t) for k, rx, t in LABELS]
RE_SPO_NOCOLON = re.compile(r"^SPO-Bezeichnung\s+(MECB.*)$")  # MECB320: sin dos puntos
RE_HEADING = re.compile(r"^(MECB\d{3}[A-D]?)\s*[–-]\s*(.+?)\s*$")
RE_FOOTER = re.compile(r"^Modulhandbuch MECB Stand:.*\d+\s*$")
RE_BULLET = re.compile(r"^([•▪■◦○●]|[-–]\s|o\s)\s*")

X_BODY = 77.0        # margen izquierdo del texto normal
X_INDENT = 85.0      # a partir de aqui la linea esta sangrada (viñeta o su continuacion)
RIGHT_MARGIN = 520.0  # margen derecho del cuerpo (las lineas completas acaban en ~518-520)
SPACE_W = 2.5
EMPTY = {"", "-", "–", "—", "keine", "Keine"}


@dataclass
class Line:
    text: str
    x0: float
    x1: float
    first_w: float  # ancho de la primera palabra (para decidir si es un salto de linea "blando")
    page: int


@dataclass
class Item:
    """Linea logica (ya reunida) de un campo."""
    text: str
    bullet: int = 0      # 0 = sin viñeta; 1, 2 = nivel
    cont: bool = False   # linea sangrada que pertenece a la viñeta anterior (salto manual)


@dataclass
class Field:
    key: str
    kind: str
    items: list[Item] = field(default_factory=list)

    def plain(self) -> str:
        return " ".join(i.text for i in self.items).strip()

    def has_content(self) -> bool:
        return self.plain() not in EMPTY


# ---------------------------------------------------------------- extraccion de lineas
def _char_index(text: str, chars: list[dict]) -> list[tuple[int, dict]]:
    """Empareja cada caracter no blanco del texto de la linea con su glifo (los espacios no tienen glifo)."""
    glyphs = [c for c in chars if c["text"].strip()]
    pos = [i for i, ch in enumerate(text) if not ch.isspace()]
    if len(glyphs) != len(pos):
        return []
    return list(zip(pos, glyphs))


def _merge_subscript(prev: dict, sub: dict) -> str:
    """Una linea en cuerpo pequeño es un subindice que pdfplumber saca aparte: se reinserta."""
    text = prev["text"]
    sub_txt = sub["text"].strip()
    pairs = _char_index(text, prev["chars"])
    if pairs:
        idx = next((i for i, c in pairs if c["x0"] >= sub["x0"] - 0.5), len(text))
        return f"{text[:idx].rstrip()}_{{{sub_txt}}}{text[idx:]}"
    return f"{text} _{{{sub_txt}}}"


def page_lines(page, page_no: int) -> list[Line]:
    raw = page.extract_text_lines(strip=True, return_chars=True)
    merged: list[dict] = []
    for ln in raw:
        if not ln["text"].strip():
            continue
        sizes = [c["size"] for c in ln["chars"] if c["text"].strip()]
        if merged and sizes and max(sizes) < 9.0:
            merged[-1] = {**merged[-1], "text": _merge_subscript(merged[-1], ln), "chars": []}
            continue
        merged.append(ln)
    out: list[Line] = []
    for ln in merged:
        text = ln["text"].strip()
        if RE_FOOTER.match(text):
            continue
        # ancho de la primera palabra (tras la viñeta, si la hay)
        mb = RE_BULLET.match(text)
        start = mb.end() if mb else 0
        word = text[start:].split()[0] if text[start:].split() else ""
        first_w = 0.0
        pairs = _char_index(ln["text"], ln["chars"]) if ln["chars"] else []
        if pairs and word:
            off = len(ln["text"]) - len(ln["text"].lstrip())
            w0 = off + text.index(word, start)
            gl = [c for i, c in pairs if w0 <= i < w0 + len(word)]
            if gl:
                first_w = gl[-1]["x1"] - gl[0]["x0"]
        if first_w == 0.0:
            first_w = 5.5 * max(1, len(word))
        out.append(Line(text=text, x0=ln["x0"], x1=ln["x1"], first_w=first_w, page=page_no))
    return out


def join_wrapped(a: str, b: str) -> str:
    """Une dos lineas fisicas de una misma linea logica, deshaciendo el guion de corte si es seguro."""
    m = re.search(r"([A-Za-zÄÖÜäöüß]{2,})-$", a)
    if m:
        first = b.split()[0] if b.split() else ""
        if first[:1].islower() and first.lower() not in {"und", "oder", "bzw.", "sowie", "u.", "o."}:
            return a[:-1] + b          # "An-" + "wendungen" -> "Anwendungen"
        if first[:1].isupper():
            return a + b               # "Springer-" + "Verlag" -> "Springer-Verlag"
    return a + " " + b


def match_label(text: str):
    for key, rx, kind in RE_LABELS:
        m = rx.match(text)
        if m:
            return key, kind, m.group(1).strip()
    m = RE_SPO_NOCOLON.match(text)
    if m:
        return "SPO-Bezeichnung", "meta", m.group(1).strip()
    return None


# ---------------------------------------------------------------- parseo
RE_REF_START = re.compile(r"^[A-ZÄÖÜ][\w'’-]+, [A-ZÄÖÜ]\.")   # "Hering, L., ..." = nueva referencia


RE_LV_CODE = re.compile(r"^MECB ?\d{3}[A-D]?\s*:")           # "MECB152: ..." abre siempre linea propia


def _new_reference(cur: "Field", text: str) -> bool:
    """En Literatur, una linea llena hasta el margen seguida de 'Apellido, N.' es otra referencia."""
    return (cur.key == "Empfohlene Literatur" and bool(RE_REF_START.match(text))
            and bool(re.search(r"[\d.)]$", cur.items[-1].text)))


def parse_module(lines: list[Line]) -> tuple[str, str, list[Field]]:
    while len(lines) > 1 and not RE_HEADING.match(lines[0].text) and any(RE_HEADING.match(l.text) for l in lines[:6]):
        lines = lines[1:]  # portada de Vertiefung ("Vertiefungsmodule zu ...") antes de la cabecera
    mh = RE_HEADING.match(lines[0].text)
    if not mh:
        raise ValueError(f"primera linea no es cabecera de modulo: {lines[0].text!r}")
    code, name = mh.group(1), re.sub(r"\s+", " ", mh.group(2))
    fields: list[Field] = []
    cur: Field | None = None
    prev: Line | None = None  # linea fisica anterior dentro del campo actual

    for ln in lines[1:]:
        lab = match_label(ln.text) if ln.x0 < X_INDENT else None
        if lab and cur is not None and lab[0] == cur.key and lab[1] == "section":
            # etiqueta repetida dentro de su propio campo (p. ej. "Studieninhalte:" x2): es texto,
            # pero en linea propia
            cur.items.append(Item(text=ln.text))
            prev = ln
            continue
        if lab:
            key, kind, value = lab
            cur = Field(key=key, kind=kind)
            fields.append(cur)
            prev = None
            if value:
                cur.items.append(Item(text=value))
                prev = ln
            continue
        if cur is None:
            raise ValueError(f"texto antes de la primera etiqueta: {ln.text!r}")
        mb = RE_BULLET.match(ln.text)
        indented = ln.x0 >= X_INDENT
        if mb and indented:
            level = 1 if ln.x0 < 125 else 2
            cur.items.append(Item(text=ln.text[mb.end():].strip(), bullet=level))
        elif (prev is not None and cur.items and prev.x1 + SPACE_W + ln.first_w > RIGHT_MARGIN
              and not ((cur.items[-1].bullet or cur.items[-1].cont) and not indented)
              and not _new_reference(cur, ln.text)
              and not (not indented and RE_LV_CODE.match(ln.text))):
            # la primera palabra no cabia en la linea anterior -> salto blando.
            # (una linea sin sangria nunca continua una viñeta: sus continuaciones van sangradas)
            cur.items[-1].text = join_wrapped(cur.items[-1].text, ln.text)
        elif indented and cur.items and (cur.items[-1].bullet or cur.items[-1].cont):
            cur.items.append(Item(text=ln.text, cont=True))
        elif indented and cur.items:
            # continuacion sangrada de un valor (p. ej. segunda linea de una enumeracion)
            cur.items[-1].text = join_wrapped(cur.items[-1].text, ln.text)
        else:
            cur.items.append(Item(text=ln.text))
        prev = ln
    return code, name, fields


# ---------------------------------------------------------------- Markdown
def _listlike(it: Item) -> bool:
    t = it.text
    return not it.bullet and not it.cont and not t.startswith("(") and not re.search(r"[.:!?]$", t)


def render_items(f: Field) -> str:
    items = f.items
    n = len(items)
    as_list = [False] * n
    if f.key == "Empfohlene Literatur" and n > 1:
        as_list = [not it.cont for it in items]   # cada linea logica es una referencia
    else:
        cand = []
        for i, it in enumerate(items):
            lead_in = i + 1 < n and items[i + 1].bullet > 0   # frase que introduce una lista con viñetas
            cand.append(_listlike(it) and not lead_in)
        i = 0
        while i < n:
            if cand[i]:
                j = i
                while j < n and cand[j]:
                    j += 1
                # el ultimo elemento de una enumeracion suele acabar en punto
                if j < n and not items[j].bullet and not items[j].cont and items[j].text[:1].islower() \
                        and items[j].text.endswith("."):
                    j += 1
                # "Nach ... sind die Studierenden in der Lage," + elementos en minuscula: frase introductoria
                if j - i >= 3 and items[i].text[:1].isupper() and all(
                        items[k].text[:1].islower() for k in range(i + 1, j)):
                    i += 1
                if j - i >= 2:
                    for k in range(i, j):
                        as_list[k] = True
                i = j
            else:
                i += 1
    out: list[str] = []
    prev_kind = None
    for it, lst in zip(items, as_list):
        if it.bullet:
            kind, s = "li", "  " * (it.bullet - 1) + "- " + it.text
        elif it.cont:
            kind, s = "li", "  " + it.text
        elif lst:
            kind, s = "li", "- " + it.text
        else:
            kind, s = "p", it.text
        if out and not (kind == "li" and prev_kind == "li"):
            out.append("")
        out.append(s)
        prev_kind = kind
    return "\n".join(out)


def render(code: str, name: str, fields: list[Field]) -> str:
    md: list[str] = [f"# {code} – {name}", ""]
    in_lv = False
    meta_open = False

    def close_meta():
        nonlocal meta_open
        if meta_open:
            md.append("")
            meta_open = False

    for f in fields:
        if f.kind == "person":
            continue
        if f.kind == "marker":
            close_meta()
            md.extend(["## Modulbeschreibung", ""])
            continue
        if f.kind == "lv":
            close_meta()
            in_lv = True
            md.extend([f"## Lehrveranstaltung: {f.plain()}", ""])
            continue
        if f.kind == "meta":
            md.append(f"- **{f.key}:** {f.plain()}")
            meta_open = True
            continue
        close_meta()
        md.extend([f"### {f.key}", "", render_items(f) if f.items else "-", ""])
    close_meta()
    return "\n".join(md).strip() + "\n"


# ---------------------------------------------------------------- control de fidelidad
def _alnum(s: str) -> str:
    return "".join(ch for ch in s if ch.isalnum())


def fidelity_check(fields: list[Field], body_md: str, code: str, name: str) -> str | None:
    """El Markdown debe contener, en orden, exactamente los caracteres alfanumericos de la fuente
    (menos los campos de personas). Detecta truncados, campos perdidos o reordenados."""
    src = [code, name]
    for f in fields:
        if f.kind == "person":
            continue
        src.append(f.key)
        src.extend(i.text for i in f.items)
    a, b = _alnum(" ".join(src)), _alnum(body_md)
    if a == b:
        return None
    k = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return f"fidelidad: difiere en pos {k}: fuente …{a[max(0, k - 20):k + 20]}… vs md …{b[max(0, k - 20):k + 20]}…"


def source_check(lines: list[Line], fields: list[Field], code: str, name: str) -> str | None:
    """Los campos parseados deben cubrir todo el texto de las paginas (salvo guiones de corte)."""
    raw = _alnum(" ".join(l.text for l in lines))
    parsed = [code, name]
    for f in fields:
        parsed.append(f.key if f.key != "Modulverantwortliche" and f.key != "Dozent/in" else "")
        parsed.extend(i.text for i in f.items)
    got = _alnum(" ".join(parsed))
    # las etiquetas de persona tienen variantes; se comparan longitudes con esa tolerancia
    n_person = sum(1 for f in fields if f.kind == "person")
    extra = 0 if RE_HEADING.match(lines[0].text) else 120  # portada de Vertiefung descartada
    if abs(len(raw) - len(got)) > 24 * n_person + extra:
        return f"cobertura: fuente {len(raw)} caracteres vs parseado {len(got)}"
    return None


# ---------------------------------------------------------------- por modulo
def blocks(fields: list[Field]) -> dict[str, bool]:
    def has(*keys: str) -> bool:
        return any(f.key in keys and f.has_content() for f in fields)
    return {
        "contents": has("Studieninhalte"),
        "learning_outcomes": has("Lernergebnisse und Kompetenzen"),
        "assessment": has("Prüfungsleistungen"),
        "bibliography": has("Empfohlene Literatur"),
        "prerequisites": has("Inhaltliche Voraussetzungen", "Voraussetzungen nach SPO"),
    }


def process(entry: dict, pdf) -> tuple[bool, str]:
    code = entry["codigo_asignatura"]
    rng = entry.get("paginas_pdf")
    if not rng:
        return False, "sin paginas_pdf en el catalogo"
    ini, fin = (int(x) for x in rng.split("-"))
    lines: list[Line] = []
    for n in range(ini, fin + 1):
        lines.extend(page_lines(pdf.pages[n - 1], n))
    if not lines:
        return False, "paginas sin texto"
    got_code, name, fields = parse_module(lines)
    if got_code != code:
        return False, f"cabecera {got_code} != catalogo {code}"
    if not any(f.kind == "marker" for f in fields):
        return False, "falta 'Modulbeschreibung:'"
    body = render(code, name, fields)
    err = source_check(lines, fields, code, name) or fidelity_check(fields, body, code, name)
    if err:
        return False, err
    bf = blocks(fields)
    out = write_markdown(SLUG, entry, body, bf)
    n_lv = sum(1 for f in fields if f.kind == "lv")
    found = ",".join(k for k, v in bf.items() if v) or "-"
    missing = [k for k in REQUIRED_BLOCKS if not bf[k]]
    msg = f"pags {rng}, {n_lv} LV, {out.stat().st_size} bytes, bloques: {found}"
    if missing:
        msg += f"  [AVISO: sin {','.join(missing)} en la fuente]"
    return True, msg


def main() -> int:
    ap = argparse.ArgumentParser(description="Scraper HKA (Modulhandbuch MECB -> Markdown)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=5, help="N modulos de la muestra piloto fija (por defecto 5)")
    g.add_argument("--all", action="store_true", help="todo el grado")
    g.add_argument("--codes", nargs="+", help="codigos concretos")
    args = ap.parse_args()
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")

    cat = load_catalog(SLUG)
    if not cat:
        print("ERROR: no existe catalogo_urls.json")
        return 2
    rows = {a["codigo_asignatura"]: a for a in cat["asignaturas"]}
    if args.all:
        codes = list(rows)
    elif args.codes:
        codes = args.codes
    else:
        rest = [c for c in rows if c not in SAMPLE]
        codes = (SAMPLE + rest)[: max(1, args.sample)]

    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdfs: dict[str, object] = {}
    failed = 0
    try:
        for code in codes:
            entry = rows.get(code)
            if entry is None:
                print(f"FALLO  {code}: no esta en el catalogo")
                failed += 1
                continue
            if entry.get("tipo_fuente") == "sin_guia":
                print(f"omitido {code}: sin_guia")
                continue
            try:
                url = entry["url_guia_docente"]
                if url not in pdfs:
                    pdfs[url] = pdfplumber.open(http.get_file(url))
                ok, msg = process(entry, pdfs[url])
            except Exception as e:  # noqa: BLE001 - un modulo roto no debe parar el resto
                ok, msg = False, f"{type(e).__name__}: {e}"
            print(f"{'ok    ' if ok else 'FALLO '} {code}: {msg}")
            failed += 0 if ok else 1
    finally:
        for p in pdfs.values():
            p.close()
    print(f"HTTP stats: {http.stats}; fallos: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
