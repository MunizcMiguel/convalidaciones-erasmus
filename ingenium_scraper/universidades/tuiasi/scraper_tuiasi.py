"""Fase 2 (Scraper) - TUIASI - Inginerie Mecanica (licenta), fichas "fisa disciplinei".

Las fichas viven en 4 PDF compartidos (uno por ano). Esos PDF tienen la mayor parte del
texto con diacriticos rumanos dibujado como CONTORNOS VECTORIALES (sin capa de texto): la
extraccion directa pierde ~la mitad de las palabras. Estrategia hibrida, determinista y local:

  1. Cada pagina se renderiza a 300 ppp (pypdfium2 via pdfplumber) borrando antes las lineas
     finas de las tablas (si no, el OCR pierde las letras con descendente que tocan el borde).
  2. OCR con el motor integrado de Windows (ocr_windows.ps1, en-US; no hay motor rumano).
     Las paginas con texto girado 90 grados (etiquetas "Cunostinte/Aptitudini...") se OCR-ean
     tambien giradas. Resultado cacheado en raw_cache/ocr/ (re-ejecutar no repite el OCR).
  3. Fusion palabra a palabra: si la capa de texto del PDF cubre completa la palabra que ve
     el OCR, se usa la capa de texto (exacta, con diacriticos); si no, la lectura OCR con
     reparaciones deterministas de diacriticos (a-dieresis -> a-breve, $i -> si...).
  4. La estructura sale de los vectores: celdas de tabla detectadas por pdfplumber con los
     rectangulos del PDF (ignorando los contornos de glifos); cada palabra va a su celda.
     Tablas -> tablas Markdown; texto libre -> parrafos; titulos de seccion -> "##".
  5. Se descartan: pie "Formular PO.DID...", notas al pie de la plantilla, filas de titulares
     (2.2/2.3) y el bloque final de firmas/fechas (nombres de personal).

Uso (desde la raiz del proyecto):
    python universidades/tuiasi/scraper_tuiasi.py --sample 5
    python universidades/tuiasi/scraper_tuiasi.py --codes MTC.101.DI.DF IM.309.DI.DS
    python universidades/tuiasi/scraper_tuiasi.py --all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from PIL import ImageDraw  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "tuiasi"
OCR_DIR = HERE / "raw_cache" / "ocr"
PS_SCRIPT = HERE / "ocr_windows.ps1"

# Muestra piloto fija y diversa
SAMPLE = [
    "MTC.101.DI.DF",    # ano 1, matematicas (Analiza matematica), etiquetas giradas en 7.
    "MTC.202.DI.DD",    # ano 2, troncal de ingenieria (Rezistenta materialelor 1)
    "IM.313.DO.DS-2",   # ano 3, optativa (Instalatii frigorifice si termice)
    "IM.311.DI.DS",     # ano 3, practicas (Practica de specialitate) - ficha atipica
    "MCT.409.DI.DS",    # ano 4, proyecto de diploma
]

# ---------------------------------------------------------------- reparacion de OCR
_OCR_FIX = [
    (re.compile(r"(?<=[a-zăâîäå])[!(](?=[a-zăâîäå])"), "ț"),
    (re.compile(r"ä"), "ă"), (re.compile(r"Ä"), "Ă"), (re.compile(r"å"), "â"), (re.compile(r"Å"), "Â"),
    (re.compile(r"(?<![\w$'])(\$i|L'i|'i|5i|9i|Yi|Kyi)(?!\w)"), "și"), (re.compile(r"(?<![\w$])ii(?!\w)"), "și"),
    (re.compile(r"(?<=[a-zăâî])[»+](?=[a-zăâîț])"), "ș"),
    (re.compile(r"(?<![\w$])tn(?=\w|$)"), "în"),
    (re.compile(r"(?<=[A-Za-zăâîșț])[$}](?=[A-Za-zăâîșț])"), "ș"),
    (re.compile(r"(?<![\w])[$}](?=[a-zăâîșț])"), "ș"),
    (re.compile(r"(?<=[A-Za-zăâî])[$}](?![\w])"), "ș"),
]


def fix_ocr(t: str) -> str:
    for rx, rep in _OCR_FIX:
        t = rx.sub(rep, t)
    return t


# ---------------------------------------------------------------- tipos
@dataclass
class W:
    text: str
    x0: float
    top: float
    x1: float
    bottom: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.top + self.bottom) / 2


@dataclass
class Block:
    kind: str                 # "text" | "table"
    top: float
    lines: list[str] = field(default_factory=list)          # text
    rows: list[list[str]] = field(default_factory=list)     # table
    page: int = 0


# ---------------------------------------------------------------- OCR
# Pasadas de OCR: (sufijo, ppp, girada). La de 300 ppp es la principal; la de 200 ppp solo
# rellena huecos (el motor omite a veces palabras cortas como "si" a 300 ppp y las ve a 200).
PASSES = {"main": ("", 300, False), "lo": ("_d200", 200, False), "rot": ("_rot", 300, True)}


def _cache_key(pdf_path: Path, page_no: int, kind: str) -> Path:
    h = hashlib.sha1(str(pdf_path.name).encode()).hexdigest()[:12]
    return OCR_DIR / f"{h}_p{page_no:03d}{PASSES[kind][0]}.json"


def _render(page, kind: str):
    _, dpi, rot = PASSES[kind]
    sc = dpi / 72.0
    im = page.to_image(resolution=dpi).original.convert("L")
    d = ImageDraw.Draw(im)
    for r in page.rects:   # borrar lineas finas de tabla
        if min(r["width"], r["height"]) < 2:
            d.rectangle([r["x0"] * sc - 1, r["top"] * sc - 1, r["x1"] * sc + 1, r["bottom"] * sc + 1], fill=255)
    for ln in page.lines:
        d.rectangle([ln["x0"] * sc - 1, ln["top"] * sc - 1, ln["x1"] * sc + 1, ln["bottom"] * sc + 1], fill=255)
    return im.rotate(-90, expand=True) if rot else im


def ensure_ocr(pdf_path: Path, pdf, pages: list[int]) -> None:
    """OCR de las paginas (1-indexadas) que no esten en cache; incluye version girada si hace falta."""
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    todo: list[tuple[Path, Path]] = []
    for pn in pages:
        page = pdf.pages[pn - 1]
        kinds = ["main", "lo"] + (["rot"] if any(not c.get("upright", True) for c in page.chars) else [])
        for kind in kinds:
            out = _cache_key(pdf_path, pn, kind)
            if out.exists():
                continue
            png = out.with_suffix(".png")
            _render(page, kind).save(png)
            todo.append((png, out))
    if not todo:
        return
    lst = OCR_DIR / "_lista.tsv"
    lst.write_text("\n".join(f"{p.resolve()}\t{o.resolve()}" for p, o in todo), encoding="utf-8")
    try:
        subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(PS_SCRIPT), str(lst.resolve())],
                       check=True, capture_output=True, timeout=600)
    finally:
        for p, _ in todo:
            p.unlink(missing_ok=True)
        lst.unlink(missing_ok=True)
    for _, o in todo:
        if not o.exists():
            raise RuntimeError(f"OCR no produjo {o.name}")


def load_ocr(pdf_path: Path, pn: int, kind: str, pw: float, ph: float) -> list[list[W]]:
    """Lineas OCR como listas de palabras en coordenadas PDF (puntos, origen arriba-izq.)."""
    _, dpi, rot = PASSES[kind]
    sc = dpi / 72.0
    p = _cache_key(pdf_path, pn, kind)
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    lines = data.get("lines") or []
    if isinstance(lines, dict):
        lines = [lines]
    out: list[list[W]] = []
    for ln in lines:
        words = ln.get("words") or []
        if words and isinstance(words[0], str):     # ConvertTo-Json aplana listas de 1 elemento
            words = [words]
        ws: list[W] = []
        for t, x, y, w, h in words:
            x0, y0, x1, y1 = x / sc, y / sc, (x + w) / sc, (y + h) / sc
            if rot:   # imagen girada -90: (x', y') -> original (x = y', y = H - x')
                x0, x1, y0, y1 = y0, y1, ph - x1, ph - x0
            ws.append(W(str(t), x0, y0, x1, y1))
        if ws:
            out.append(ws)
    return out


# ---------------------------------------------------------------- fusion OCR + capa de texto
def _overlap(a: W, b: W) -> float:
    """Fraccion del ancho de b solapada con a (si comparten franja vertical)."""
    if min(a.bottom, b.bottom) - max(a.top, b.top) <= 0.3 * (b.bottom - b.top):
        return 0.0
    return max(0.0, min(a.x1, b.x1) - max(a.x0, b.x0)) / max(1e-6, b.x1 - b.x0)


def merge_words(page, ocr_lines: list[list[W]], lo_lines: list[list[W]], rot_lines: list[list[W]]) -> list[W]:
    chars = [c for c in page.chars if c["text"].strip() and c.get("upright", True)]
    used: set[int] = set()
    out: list[W] = []
    main_words = [w for ln in ocr_lines for w in ln]
    gap_fill = [w for ln in lo_lines for w in ln if not any(_overlap(m, w) > 0.2 for m in main_words)]
    for line in ocr_lines + [gap_fill]:
        for w in line:
            inside = [i for i, c in enumerate(chars)
                      if w.x0 - 1 <= (c["x0"] + c["x1"]) / 2 <= w.x1 + 1 and w.top - 1 <= (c["top"] + c["bottom"]) / 2 <= w.bottom + 1]
            txt = fix_ocr(w.text)
            if inside:
                cs = sorted((chars[i] for i in inside), key=lambda c: c["x0"])
                cover = sum(c["x1"] - c["x0"] for c in cs) / max(1e-6, w.x1 - w.x0)
                tl = "".join(c["text"] for c in cs)
                if cover >= 0.85 and len(tl) >= len(w.text) - 1:
                    txt = tl
                used.update(inside)
            out.append(W(txt, w.x0, w.top, w.x1, w.bottom))
    # texto de la capa PDF que el OCR no vio (cifras sueltas, simbolos), salvo superindices
    rest = [c for i, c in enumerate(chars) if i not in used and c.get("size", 10) >= 7.5]
    for wd in _chars_to_words(rest):
        if re.search(r"\w", wd.text):   # sin restos de puntuacion sueltos (", ,")
            out.append(wd)
    # texto girado: solo palabras OCR de la pasada girada que caen sobre caracteres no verticales
    rchars = [c for c in page.chars if c["text"].strip() and not c.get("upright", True)]
    if rchars and rot_lines:
        for line in rot_lines:
            for w in line:
                if any(w.x0 - 2 <= (c["x0"] + c["x1"]) / 2 <= w.x1 + 2 and w.top - 2 <= (c["top"] + c["bottom"]) / 2 <= w.bottom + 2
                       for c in rchars):
                    out.append(W(fix_ocr(w.text), w.x0, w.top, w.x1, w.bottom))
    return out


def _chars_to_words(chars: list[dict]) -> list[W]:
    chars = sorted(chars, key=lambda c: (round(c["top"]), c["x0"]))
    words: list[W] = []
    for c in chars:
        if words and abs(c["top"] - words[-1].top) < 2 and 0 <= c["x0"] - words[-1].x1 < 1.5:
            w = words[-1]
            words[-1] = W(w.text + c["text"], w.x0, min(w.top, c["top"]), c["x1"], max(w.bottom, c["bottom"]))
        else:
            words.append(W(c["text"], c["x0"], c["top"], c["x1"], c["bottom"]))
    return words


def to_lines(words: list[W], vertical: bool = False) -> list[str]:
    """Agrupa palabras en lineas (por solape vertical) y las ordena."""
    if vertical:   # texto girado (se lee de abajo arriba): una "linea" por columna
        words = sorted(words, key=lambda w: (round(w.cx / 4), -w.bottom))
        return [" ".join(w.text for w in words)] if words else []
    ws = sorted(words, key=lambda w: (w.cy, w.x0))
    lines: list[list[W]] = []
    for w in ws:
        if lines:
            last = lines[-1]
            ref_top = min(x.top for x in last)
            ref_bot = max(x.bottom for x in last)
            h = ref_bot - ref_top
            if w.cy <= ref_bot - 0.3 * h and w.cy >= ref_top:
                last.append(w)
                continue
        lines.append([w])
    out = []
    for ln in lines:
        ln.sort(key=lambda w: w.x0)
        out.append(re.sub(r"\s+", " ", " ".join(w.text for w in ln)).strip())
    return [x for x in out if re.search(r"\w", x)]   # sin lineas de solo puntuacion (", ,")


# ---------------------------------------------------------------- layout
TABLE_SETTINGS = {"vertical_strategy": "lines", "horizontal_strategy": "lines",
                  "snap_tolerance": 3, "join_tolerance": 3, "intersection_tolerance": 3}


def page_blocks(page, words: list[W], page_no: int) -> list[Block]:
    vec = page.filter(lambda o: o.get("object_type") not in ("curve", "char"))
    tables = vec.find_tables(TABLE_SETTINGS)
    rchars = [c for c in page.chars if c["text"].strip() and not c.get("upright", True)]
    blocks: list[Block] = []
    assigned: set[int] = set()
    for t in tables:
        x0, top, x1, bottom = t.bbox
        if (x1 - x0) < 40 or (bottom - top) < 8:
            continue
        rows_out: list[list[str]] = []
        for row in t.rows:
            cells_txt: list[str] = []
            for cell in row.cells:
                if cell is None:
                    cells_txt.append("")
                    continue
                cx0, ctop, cx1, cbot = cell
                ids = [i for i, w in enumerate(words)
                       if i not in assigned and cx0 <= w.cx <= cx1 and ctop <= w.cy <= cbot]
                assigned.update(ids)
                cw = [words[i] for i in ids]
                vertical = bool(cw) and any(cx0 <= (c["x0"] + c["x1"]) / 2 <= cx1 and ctop <= (c["top"] + c["bottom"]) / 2 <= cbot
                                            for c in rchars) and (cx1 - cx0) < 40
                cells_txt.append("<br>".join(to_lines(cw, vertical=vertical)))
            if any(cells_txt):
                rows_out.append(cells_txt)
        if rows_out:
            blocks.append(Block("table", top, rows=rows_out, page=page_no))
    free = [w for i, w in enumerate(words) if i not in assigned]
    # lineas sueltas -> bloques de texto (uno por linea; se agrupan despues)
    for ln_words in _group_lines(free):
        txt = re.sub(r"\s+", " ", " ".join(w.text for w in sorted(ln_words, key=lambda w: w.x0))).strip()
        h = max(w.bottom for w in ln_words) - min(w.top for w in ln_words)
        if txt:
            blocks.append(Block("text", min(w.top for w in ln_words), lines=[txt], page=page_no))
            blocks[-1].rows = [[f"{h:.1f}"]]   # altura de linea (para detectar notas al pie)
    blocks.sort(key=lambda b: b.top)
    return blocks


def _group_lines(words: list[W]) -> list[list[W]]:
    ws = sorted(words, key=lambda w: (w.cy, w.x0))
    lines: list[list[W]] = []
    for w in ws:
        if lines:
            last = lines[-1]
            ref_top, ref_bot = min(x.top for x in last), max(x.bottom for x in last)
            if ref_top <= w.cy <= ref_bot:
                last.append(w)
                continue
        lines.append([w])
    return lines


# ---------------------------------------------------------------- Markdown
RE_FOOTER = re.compile(r"^Formular\s+P\s*O\s*\.?\s*D\s*[Il1]\s*D", re.I)
RE_SECTION = re.compile(r"^(\d{1,2})\s*\.\s*(Date despre|Timpul total|Precondi|Condi|Obiectiv|Competen|Rezultatele|Metode|Con[tț]inutur|Evaluare|Coroborarea|Standard|Bibliografi)", re.I)
RE_SIGN_START = re.compile(r"^(Data complet|Data [îi]ntocmir|Data aviz|Data aprob|Titular|Semn[aă]tura|Director de departament|Decan)", re.I)
RE_STAFF_ROW = re.compile(r"^2\s*\.\s*[23]\b.*Titular|^Titular", re.I)


def md_cell(s: str) -> str:
    return s.replace("|", "\\|").strip()


def render_markdown(blocks: list[Block]) -> str:
    out: list[str] = []
    para: list[str] = []
    stop = False

    def flush():
        if para:
            out.append(" ".join(para) if not any(p.lstrip().startswith(("-", "•", "*")) for p in para) else "\n".join(_listify(para)))
            out.append("")
            para.clear()

    prev_table: list[list[str]] | None = None
    for b in blocks:
        if stop:
            break
        if b.kind == "text":
            t = b.lines[0]
            h = float(b.rows[0][0]) if b.rows else 10
            if RE_FOOTER.search(t):
                continue
            if RE_SIGN_START.search(t) or re.match(r"^_{4,}", t):
                # bloque de firmas (nombres de personal) o separador de notas al pie de la
                # plantilla: lo que sigue no es contenido de la ficha
                stop = True
                continue
            if h < 7.0:   # superindices / llamadas sueltas
                continue
            prev_table = None
            if RE_SECTION.match(t) or re.fullmatch(r"FI[SȘŞ]?\s*A DISCIPLINEI", t, re.I):
                flush()
                out.append(("## " if RE_SECTION.match(t) else "# ") + t)
                out.append("")
                continue
            if para and (re.match(r"^[-•*]\s", t) or para[-1].endswith((".", ":", ";"))) or re.match(r"^\d+(\.\d+)*\.?\s", t):
                if re.match(r"^[-•*]\s", t):
                    para.append(t)
                    continue
                flush()
            para.append(t)
        else:
            flush()
            rows = [r for r in b.rows if not RE_STAFF_ROW.search(r[0] if r else "")]
            if any(RE_SIGN_START.search(c) for r in rows for c in r if c):
                rows = rows[:next(i for i, r in enumerate(rows) if any(RE_SIGN_START.search(c) for c in r if c))]
                stop = True
            if not rows:
                continue
            ncol = len(rows[0])
            if prev_table is not None and len(prev_table[0]) == ncol and out and out[-1] == "":
                # continuacion de tabla en la pagina siguiente
                out.pop()
                out.extend("| " + " | ".join(md_cell(c) for c in r) + " |" for r in rows)
                out.append("")
                prev_table = rows
                continue
            out.append("| " + " | ".join(md_cell(c) for c in rows[0]) + " |")
            out.append("|" + "---|" * ncol)
            out.extend("| " + " | ".join(md_cell(c) for c in r) + " |" for r in rows[1:])
            out.append("")
            prev_table = rows
    flush()
    md = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def _listify(lines: list[str]) -> list[str]:
    items: list[str] = []
    for ln in lines:
        m = re.match(r"^[-•*]\s*(.*)$", ln)
        if m:
            items.append("- " + m.group(1))
        elif items:
            items[-1] += " " + ln
        else:
            items.append(ln)
    return items


def detect_blocks(md: str) -> dict[str, bool]:
    def has(rx: str) -> bool:
        return re.search(rx, md, re.I | re.M) is not None
    return {
        # algunas fichas no llevan el titulo "9. Continuturi" y empiezan directamente por la tabla 9.1 Curs
        "contents": has(r"Con[tț]inutur") or has(r"9\.\s*1\.?\s*Curs"),
        "learning_outcomes": has(r"Rezultatele [îi]nv[aă][tț][aă]rii|Competen[tț]e (specifice|profesionale|transversale)|Cuno[sș]tin[tț]e"),
        # pesos con "%" o columna "Pondere" (IM.416.DO.DS-1 da los pesos sin el signo %)
        "assessment": has(r"Evaluare") and ("%" in md or has(r"Pondere")),
        "bibliography": has(r"Bibliografi"),
        "prerequisites": has(r"Precondi[tț]ii"),
    }


# ---------------------------------------------------------------- main
def scrape(entry: dict, http: PoliteClient, pdf_cache: dict) -> tuple[bool, str]:
    url = entry["url_guia_docente"]
    path = http.get_file(url)
    if url not in pdf_cache:
        pdf_cache.clear()
        pdf_cache[url] = pdfplumber.open(path)
    pdf = pdf_cache[url]
    ini, fin = (int(x) for x in entry["paginas_pdf"].split("-"))
    pages = list(range(ini, fin + 1))
    ensure_ocr(path, pdf, pages)
    blocks: list[Block] = []
    for pn in pages:
        page = pdf.pages[pn - 1]
        pw, ph = page.width, page.height
        words = merge_words(page, load_ocr(path, pn, "main", pw, ph), load_ocr(path, pn, "lo", pw, ph),
                            load_ocr(path, pn, "rot", pw, ph))
        blocks.extend(page_blocks(page, words, pn))
    md = render_markdown(blocks)
    found = detect_blocks(md)
    if len(md) < 500:
        return False, f"Markdown demasiado corto ({len(md)} car.)"
    write_markdown(SLUG, entry, md, found)
    missing = [k for k, v in found.items() if not v]
    return True, f"{len(md)} car." + (f"; sin: {', '.join(missing)}" if missing else "")


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=None)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    if not cat:
        sys.exit("Falta catalogo_urls.json: ejecute discover_tuiasi.py")
    rows = cat["asignaturas"]
    by_code = {r["codigo_asignatura"]: r for r in rows}
    if a.all:
        sel = rows
    elif a.codes:
        sel = [by_code[c] for c in a.codes]
    else:
        n = a.sample or 5
        sel = [by_code[c] for c in SAMPLE[:n]]
    sel = sorted(sel, key=lambda r: (r.get("url_guia_docente") or "", r.get("paginas_pdf") or ""))
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    pdf_cache: dict = {}
    failed = 0
    for r in sel:
        code = r["codigo_asignatura"]
        if r["tipo_fuente"] == "sin_guia":
            print(f"SKIP {code}: sin_guia")
            continue
        try:
            ok, msg = scrape(r, http, pdf_cache)
        except Exception as e:  # noqa: BLE001
            ok, msg = False, f"{type(e).__name__}: {e}"
        failed += not ok
        print(f"{'OK  ' if ok else 'FAIL'} {code}: {msg}", flush=True)
    print(f"HTTP: {http.stats}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
