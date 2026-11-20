"""Parser compartido (discover + scraper) del Studienplan 'Bachelorstudium Maschinenbau' de la TU Wien (PDF con texto).

La seccion 'A Modulbeschreibungen' contiene, para cada modulo: titulo, 'Regelarbeitsaufwand: N ECTS', Lernergebnisse,
Inhalt, Erwartete Vorkenntnisse, Verpflichtende Voraussetzungen, Lehr- und Lernformen y la lista 'Lehrveranstaltungen des Moduls:'.
"""
from __future__ import annotations

import io
import re

import pypdf

LVA = re.compile(r"^\d+,\d/\d+,\d\s+[A-Z]{2}\s+\S")
GROUP = re.compile(r"^(Pflichtmodule|Modulgruppe\b.*|Wahlmodule.*|Freie Wahlf.cher.*|Transferable Skills.*|Berufsfeldorientierung.*)$")
PAGENO = re.compile(r"^\d{1,3}$")


def load_pages(data: bytes) -> list[str]:
    return [p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(data)).pages]


def parse_modules(pages: list[str]) -> list[dict]:
    start_pg = next(i for i, t in enumerate(pages) if t.lstrip().startswith("A Modulbeschreibungen"))
    lines: list[tuple[str, int]] = []  # (linea, pagina 1-indexed)
    for i in range(start_pg, len(pages)):
        for l in pages[i].splitlines():
            s = l.strip()
            if s and not PAGENO.match(s):
                lines.append((s, i + 1))
    idx = [k for k, (s, _) in enumerate(lines) if s.startswith("Regelarbeitsaufwand:")]
    heads = []  # (indice de la linea de titulo, grupo)
    group = ""
    for k in idx:
        j = k - 1
        grp_lines = []
        while j > 0 and GROUP.match(lines[j - 1][0]):
            grp_lines.append(lines[j - 1][0])
            j -= 1
        # lines[k-1] es el titulo; los de grupo estan justo antes
        title_i = k - 1
        j = title_i
        while j - 1 >= 0 and GROUP.match(lines[j - 1][0]):
            group = lines[j - 1][0]
            j -= 1
        heads.append((title_i, j, group))
    mods = []
    for n, k in enumerate(idx):
        title_i, first_i, grp = heads[n]
        end = heads[n + 1][1] if n + 1 < len(idx) else len(lines)
        if n + 1 == len(idx):  # ultimo modulo: cortar tras su lista de LVA (despues viene el anexo del plan)
            j = next(j for j in range(k, len(lines)) if lines[j][0] == "Lehrveranstaltungen des Moduls:") + 1
            while j < len(lines) and LVA.match(lines[j][0]):
                j += 1
            end = j
        body = [s for s, _ in lines[k:end]]
        ects = float(re.search(r"(\d+,\d+|\d+)\s*ECTS", lines[k][0]).group(1).replace(",", "."))
        mods.append({"title": lines[title_i][0], "group": grp, "ects": ects, "body": body,
                     "page_ini": lines[first_i][1], "page_fin": lines[end - 1][1]})
    return mods
