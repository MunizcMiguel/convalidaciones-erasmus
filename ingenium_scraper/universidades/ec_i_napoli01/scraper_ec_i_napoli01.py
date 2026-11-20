#!/usr/bin/env python3
"""Fase 2 · Scraper — Napoli Federico II, Ingegneria Elettronica (L-8). PDF compartido (Guida dello Studente 2022/23).

Uso: python universidades/ec_i_napoli01/scraper_ec_i_napoli01.py --sample 5 | --all | --codes C1 C2
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_napoli01"
SAMPLE = ["analisi_matematica_i", "fondamenti_di_circuiti", "elettronica_i", "controlli_automatici", "computer_systems_design"]

HEAD = {  # etiqueta del PDF -> (título md, bloque)
    "INFORMAZIONI GENERALI - ATTIVITA": ("Informazioni generali", None),
    "INSEGNAMENTI PROPEDEUTICI": ("Insegnamenti propedeutici", "prerequisites"),
    "EVENTUALI PREREQUISITI": ("Prerequisiti", "prerequisites"),
    "OBIETTIVI FORMATIVI": ("Obiettivi formativi", "learning_outcomes"),
    "RISULTATI DI APPRENDIMENTO ATTESI": ("Risultati di apprendimento attesi (descrittori di Dublino)", "learning_outcomes"),
    "PROGRAMMA-SYLLABUS": ("Programma-Syllabus", "contents"),
    "MATERIALE DIDATTICO": ("Materiale didattico", "bibliography"),
    "MODALITA DI SVOLGIMENTO": ("Modalità di svolgimento dell'insegnamento", None),
    "VERIFICA DI APPRENDIMENTO": ("Verifica di apprendimento e criteri di valutazione", "assessment"),
}
DROP = re.compile(r"^(DOCENTE|TELEFONO|EMAIL|E-MAIL|CANALI?)\b[^\n]*$", re.I)


def key_of(line: str):
    u = re.sub(r"[^A-Z\- ]", "", line.upper().replace("\u00c0", "A"))
    u = re.sub(r"\s+", " ", u).strip()
    for k in HEAD:
        if u.startswith(k):
            return k
    return None


def to_markdown(entry: dict, text: str) -> tuple[str, dict]:
    lines = [l.rstrip() for l in text.replace("\u2022", "- ").replace("\uf0b7", "- ").split("\n")]
    out, blocks, section, in_docente = [f"# {entry['nombre_asignatura']}", ""], {}, None, False
    for l in lines:
        s = l.strip()
        if not s or re.fullmatch(r"\d{1,3}", s):          # vacío / pie con nº de página
            continue
        if s.startswith("SCHEDA DELL") or s.startswith('"') and s.endswith('"') and s.upper() == s:
            continue
        if re.match(r"INFORMAZIONI GENERALI\s*-\s*DOCENTE", s.upper()):
            in_docente = True
            continue
        k = key_of(s)
        if k:
            in_docente = False
            title, blk = HEAD[k]
            section = k
            out += ["", f"## {title}", ""]
            if blk:
                blocks.setdefault(blk, False)
            continue
        if in_docente or DROP.match(s):
            continue
        if re.match(r"(SSD\b|DENOMINAZIONE DEL CORSO|CORSO DI LAUREA|ANNO ACCADEMICO)", s.upper()):
            out.append(f"- {s}")
            continue
        if section is None:
            continue
        if section == "INFORMAZIONI GENERALI - ATTIVITA":
            out.append(f"- {s}")
        else:
            out.append(re.sub(r"^[\u25cf\u25aa\u2013\-] ?", "- ", s) if s[0] in "\u25cf\u25aa" else s)
            blk = HEAD[section][1]
            if blk:
                blocks[blk] = True
    body = "\n".join(out)
    body = re.sub(r"\n{3,}", "\n\n", body)
    full = {b: blocks.get(b, False) for b in ("contents", "learning_outcomes", "assessment", "bibliography", "prerequisites")}
    return body, full


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, nargs="?", const=5)
    g.add_argument("--all", action="store_true")
    g.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = [e.model_dump() if hasattr(e, "model_dump") else e for e in cat.asignaturas] if hasattr(cat, "asignaturas") else cat["asignaturas"]
    if a.all:
        sel = rows
    elif a.codes:
        sel = [r for r in rows if r["codigo_asignatura"] in a.codes]
    else:
        n = a.sample or 5
        sel = [r for r in rows if r["codigo_asignatura"] in SAMPLE][:n]
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    data = http.get_bytes(rows[0]["url_guia_docente"])
    fails = 0
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for r in sel:
            if r["tipo_fuente"] == "sin_guia":
                print(f"{r['codigo_asignatura']}: skip sin_guia")
                continue
            ini, fin = map(int, r["paginas_pdf"].split("-"))
            text = "\n".join((pdf.pages[i - 1].extract_text() or "") for i in range(ini, fin + 1))
            body, blocks = to_markdown(r, text)
            if len(body) < 600:
                print(f"{r['codigo_asignatura']}: FALLO texto escaso")
                fails += 1
                continue
            p = write_markdown(SLUG, r, body, blocks)
            print(f"{r['codigo_asignatura']}: ok [it] {len(body)} chars -> {p.name} blocks={blocks}")
    print("HTTP:", http.stats)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
