"""Fase 2 - TU Clausthal Maschinenbau: cada modulo del Modulhandbuch (PDF compartido, tablas) -> Markdown.

Uso: python universidades/ec_d_clausth01/scraper_ec_d_clausth01.py [--sample N | --all | --codes C1 C2]
Se leen las celdas reales de las tablas (pdfplumber find_tables + recorte por celda: extract_tables pierde texto desbordado).
Se descartan Modulverantwortliche, Zustaendige Fakultaet, Dozent(in), LV-Nr y Verantwortliche Pruefer (nombres de personal).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from discover_ec_d_clausth01 import PDF_URL, page_cells  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_clausth01"
SAMPLE = ["ingenieurmathematik-i", "technische-mechanik-ii", "maschinenelemente", "produktionstechnik", "bachelorarbeit", "industriepraktikum"]
NL = chr(10)
LABEL = re.compile(r"^(\d{1,2})([a-z]?)[.]\s*(Verwendbarkeit|Modulverantwortliche|Lern-|Empf|Inhalte|Medienformen|Literatur|Sonstiges|"
                   r"Prüfungsform|Verantwortliche|Verbindliche|Sprache|Zuständige|Modulnummer)")
NUMBERED = re.compile(r"^\d{1,2}[a-z]?[.]")
TITLES = {"Inhalte": "Inhalte", "Empf": "Empfohlene Voraussetzungen", "Medienformen": "Medienformen", "Literatur": "Literatur",
          "Sonstiges": "Sonstiges", "Prüfungsform": "Prüfungsform / Voraussetzung für die Vergabe von LP",
          "Verbindliche": "Verbindliche Prüfungsvorleistungen"}
DROP_WORDS = {"Modulverantwortliche", "Zuständige", "Modulnummer", "Verantwortliche"}


def lines(cell: str) -> str:
    return NL.join(re.sub(r"\s+", " ", x).strip() for x in cell.split(NL) if x.strip())


def build(entry: dict, pdf, ini: int, fin: int) -> tuple[str, dict]:
    secs: list[tuple[str, list[str]]] = []
    found = {"contents": False, "learning_outcomes": False, "assessment": False, "bibliography": False, "prerequisites": False}
    current = None
    buf: list[str] = []
    lv_rows, ex_rows = [], []
    suffix = ""
    extra: dict = {}

    def emit(title, body):
        body = [x for x in body if x]
        if body:
            secs.append((title, body))

    def close():
        nonlocal current, buf
        if current and not current.startswith("__"):
            emit(current, buf)
        current, buf = None, []

    for pno in range(ini, fin + 1):
        for trows in page_cells(pdf.pages[pno - 1]):
            consumed = set()
            allc = [c for r in trows for c in r]
            for r in trows:  # etiqueta con valor en celda alta a su derecha (se solapa en vertical): el valor no esta en su fila
                for txt, bb in r:
                    m0 = LABEL.match(txt)
                    if m0 and m0.group(3) in TITLES and not any(t2.strip() and not LABEL.match(t2) and b2[0] > bb[0] and b2[1] < bb[3] - 1 and b2[3] > bb[1] + 1 and b2 != bb
                                                                for t2, b2 in r):
                        cy = (bb[1] + bb[3]) / 2
                        for t2, b2 in allc:
                            if t2.strip() and not LABEL.match(t2) and b2[0] >= bb[2] - 1 and b2[1] <= cy <= b2[3] and (t2, b2) not in consumed:
                                consumed.add((t2, b2))
                                extra[(txt, bb)] = extra.get((txt, bb), []) + [t2]
            for r in trows:
                cs = []
                for txt, bb in r:
                    if (txt, bb) in consumed:
                        continue
                    cs.append(txt + (NL + NL.join(extra.get((txt, bb), [])) if False else ""))
                    if (txt, bb) in extra:
                        cs.append(NL.join(extra[(txt, bb)]))
                ne = [c for c in cs if c.strip()]
                if not ne:
                    continue
                if ne[0].startswith("1a. Modultitel"):
                    continue
                if len(ne) > 1 and all(NUMBERED.match(c) for c in ne) and ne[0].split(".")[0] in ("3", "6", "23"):
                    # fila de cabeceras de columnas (3./4./5., 6./7./8./9., 23.-28.): decide la seccion
                    if ne[0].startswith("3."):
                        close()
                        current = "__drop__"
                    elif ne[0].startswith("6."):
                        close()
                        current = "Sprache / LP / Dauer / Angebot"
                    elif ne[0].startswith("23."):
                        close()
                        current = "__ex__"
                    continue
                m = LABEL.match(ne[0])
                if m:
                    word, val = m.group(3), ne[1:]
                    if word == "Lern-":
                        close()
                        current = "Lern-/Qualifikationsziele"
                        found["learning_outcomes"] = True
                    elif word == "Verwendbarkeit":
                        close()
                        current = "Verwendbarkeit"
                    elif word == "Sprache":
                        close()
                        current = "Sprache / LP / Dauer / Angebot"
                    elif word in DROP_WORDS:
                        close()
                        current = "__drop__"
                        if word == "Verantwortliche":
                            current = None
                    elif word in TITLES:
                        close()
                        text = [lines(v) for v in val]
                        title = f"{TITLES[word]} {suffix}".strip()
                        if word == "Inhalte" and text:
                            found["contents"] = True
                        if word == "Literatur" and text:
                            found["bibliography"] = True
                        if word == "Empf" and text and not re.fullmatch(r"(keine|-)[.]?", " ".join(text).strip(), re.I):
                            found["prerequisites"] = True
                        if word == "Prüfungsform" and text:
                            found["assessment"] = True
                        emit(title, text)
                    continue
                if re.fullmatch(r"Zu Nr[.] (\d+):", ne[0]):
                    close()
                    suffix = "(" + ne[0].replace("Zu", "zu").rstrip(":") + ")"
                    continue
                if ne[0].startswith("Lehrveranstaltungen") and len(ne) == 1:
                    close()
                    current = "__lv__"
                    continue
                if ne[0].startswith("Studien-/Prüfungsleistung"):
                    close()
                    current = "__ex__"
                    continue
                if ne[0] in ("Prüfungsvorleistungen", "für die Vergabe von LP"):
                    continue
                if current == "__lv__":
                    if re.fullmatch(r"\d+", ne[0]) and len(ne) >= 4:
                        title = re.sub(r"\s+", " ", ne[1])
                        lv_rows.append(f"| {ne[0]} | {title} | {ne[-3]} | {ne[-2]} | {re.sub(chr(10), ' ', ne[-1])} |")
                    elif ne[0].startswith("Summe") and len(ne) >= 3:
                        lv_rows.append(f"| Summe | | | {ne[-2]} | {ne[-1]} |")
                    continue
                if current == "__ex__":
                    if re.fullmatch(r"\d+", ne[0]):
                        ex_rows.append("| " + " | ".join(re.sub(r"\s+", " ", c) for c in ne) + " |")
                    continue
                if current == "__drop__":
                    continue
                if current:
                    buf.append(NL.join(lines(c) for c in ne))
    close()
    if lv_rows:
        secs.insert(0, ("Lehrveranstaltungen", ["| Nr | Lehrveranstaltung | Art | SWS | Arbeitsaufwand (Präsenz/Eigenstudium) |", "|---|---|---|---|---|", *lv_rows]))
    if ex_rows:
        secs.append(("Studien-/Prüfungsleistung", ["| Nr | Lehrveranstaltung | Art | LP | Benotung | Anteil Modulnote |", "|---|---|---|---|---|---|", *ex_rows]))
        found["assessment"] = True
    body = [f"# {entry['nombre_asignatura']}", ""]
    for title, content in secs:
        body += [f"## {title}", "", *content, ""]
    return NL.join(body), found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    codes = a.codes or (list(rows) if a.all else [c for c in SAMPLE if c in rows][: a.sample])
    client = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    with pdfplumber.open(client.get_file(PDF_URL)) as pdf:
        for c in codes:
            r = rows.get(c)
            if not r or r["tipo_fuente"] == "sin_guia":
                print(f"SKIP {c}")
                continue
            try:
                ini, fin = (int(x) for x in r["paginas_pdf"].split("-"))
                md, found = build(r, pdf, ini, fin)
                write_markdown(SLUG, r, md, found)
                print(f"ok {c} {len(md)} sin: {[k for k, v in found.items() if not v]}")
            except Exception as e:  # noqa: BLE001
                fails += 1
                print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
