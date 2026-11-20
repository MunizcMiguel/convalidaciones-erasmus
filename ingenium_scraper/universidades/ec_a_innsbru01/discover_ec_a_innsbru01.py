"""Fase 1 - Universitaet Innsbruck - Bachelorstudium Mechatronik (B.Sc., 6 sem., 180 ECTS-AP; programa conjunto LFUI/UMIT TIROL).

La Universitaet Innsbruck NO tiene un grado de Ingenieria Mecanica; el mas afin (primer ciclo, con Mecanica, Maquinas, CAD, Resistencia, Termodinamica,
Control) es Mechatronik. Fuente: texto del Curriculum (Mitteilungsblatt, Stand 01.10.2018) enlazado desde la ficha del grado: PDF de 27 paginas con
los modulos (lecciones, ECTS, Lernziele) y el Empfohlener Studienverlauf. No hay guias por asignatura publicas fuera de LFU:online.
Uso: python universidades/ec_a_innsbru01/discover_ec_a_innsbru01.py
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_a_innsbru01"
UNIVERSIDAD = "Universität Innsbruck (LFUI) / UMIT TIROL"
GRADO = "Mechatronik (B.Sc.)"
URL_PLAN = "https://www.uibk.ac.at/de/studien/ba-mechatronik/2011w/"
FOOT = re.compile(r"^– \d+ –$")
HEAD = re.compile(r"^(?:(\d+)\. )?(Pflichtmodul|Wahlmodul)(?: (A\d))?:?")


def pdf_url(c: PoliteClient) -> str:
    t = c.get_text(URL_PLAN)
    cand = [urljoin(URL_PLAN, html.unescape(h)) for h in re.findall(r'href="([^"]+)"', t) if re.search(r"ba-mechatronik_stand-\d+\.pdf$", h)]
    # el Stand mas reciente: ddmmaaaa -> aaaammdd
    def key(u):
        d = re.search(r"stand-(\d{2})(\d{2})(\d{4})", u)
        return d.group(3) + d.group(2) + d.group(1)
    return max(cand, key=key)


def page_lines(pdf):
    out = []
    for i, pg in enumerate(pdf.pages, 1):
        for l in unicodedata.normalize("NFC", pg.extract_text(x_tolerance=1.5) or "").split(chr(10)):
            if not FOOT.match(l.strip()):
                out.append((i, l.rstrip()))
    return out


def clean_title(parts: list[str]) -> str:
    s = " ".join(parts)
    s = re.sub(r"\bECTS-", " ", s)
    s = re.sub(r"\bSSt Univ\.", " ", s)
    s = re.sub(r"\bAP\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"-\s+(?!und |oder |bzw)(?=[a-zäöü])", "", s)  # guion de corte de linea
    return s


def modules(lines):
    s7 = next(i for i, (_, l) in enumerate(lines) if l.startswith("§ 7 Pflicht- und Wahlmodule"))
    e7 = next(i for i in range(s7 + 1, len(lines)) if re.match(r"^§ \d+ ", lines[i][1]))
    heads = []
    for i in range(s7, e7):
        l = lines[i][1].strip()
        m = HEAD.match(l)
        if not m or "Absolvierung des Pflichtmoduls" in l or l.startswith(("Pflichtmodul A1 oder", "Pflichtmodule")):
            continue
        if "SSt Univ." not in " ".join(x[1] for x in lines[i:i + 3]):
            continue  # no es una cabecera de modulo (frase del texto)
        k, parts, num = i, [], m.group(1)
        while k < i + 4:
            t = lines[k][1].strip()
            mm = re.match(r"^(\d+)\. SSt Univ\.", t)
            if mm and not num:
                num = mm.group(1)
            if not mm:
                parts.append(re.sub(r"^\d+\. ", "", t) if k == i and m.group(1) else t)
            if re.search(r"\bAP$", t):
                break
            k += 1
        title = clean_title(parts)
        title = re.sub(r"^(Pflichtmodul|Wahlmodul)( A\d)?:? ?", "", title)
        if m.group(2) == "Wahlmodul":
            title = "Wahlmodul " + title + (f" ({m.group(3)})" if m.group(3) and m.group(3) not in title else "")
        heads.append(dict(idx=i, kind=m.group(2), spec=m.group(3), num=num, title=title, body=k + 1))
    return heads, e7


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    url = pdf_url(c)
    with pdfplumber.open(c.get_file(url)) as pdf:
        lines = page_lines(pdf)
    heads, e7 = modules(lines)
    maxnum = max(int(h["num"]) for h in heads if h["kind"] == "Pflichtmodul" and not h["spec"] and h["num"])
    # semestre: primera aparicion del codigo de modulo (P12, P25-A1, W1...) en el Empfohlener Studienverlauf
    plan_start = next(i for i, (_, l) in enumerate(lines) if l.startswith("Empfohlener Studienverlauf"))
    sem, cur = {}, 0
    for _, l in lines[plan_start:]:
        ms = re.match(r"^(\d)\. Semester \(", l)
        if ms:
            cur = int(ms.group(1))
        for tag in re.findall(r"\b(P\d+(?:-A\d)?|W\d(?:-A\d)?)\b", l):
            sem.setdefault(tag, cur)
    entries, seen = [], set()
    for n, h in enumerate(heads):
        end = heads[n + 1]["idx"] if n + 1 < len(heads) else e7
        block = [l for _, l in lines[h["idx"]:end]]
        if h["kind"] == "Pflichtmodul":
            code = f"P{h['num']}" if not h["spec"] else f"P{maxnum + 1}-{h['spec']}"
        else:
            code = "W1" if (not h["spec"] and h["num"] == "1") else (f"W2-{h['spec']}" if h["spec"] else "W3")
        assert code not in seen, code
        seen.add(code)
        ects = None
        for l in block:
            ms = re.match(r"^Summe\s+([\d,]+)\s+([\d,]+)\b", l.strip())
            if ms:
                ects = float(ms.group(2).replace(",", "."))
        if ects is None:
            text = " ".join(block)
            mo = re.search(r"(?:Umfang von|Ausmaß von)\s+(?:insgesamt\s+)?([\d,]+) ECTS-AP", text) or re.search(r"([\d,]+) ECTS-AP", text)
            ects = float(mo.group(1).replace(",", ".")) if mo else None
        s = sem.get(code)
        caracter = "tfg" if h["title"].startswith("Bachelorarbeit") else ("obligatoria" if h["kind"] == "Pflichtmodul" else "optativa")
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=h["title"],
            curso_semestre=(f"Semester {s} (empfohlener Studienverlauf)" if s else "Semester nicht angegeben"), curso=(s + 1) // 2 if s else None, semestre=s,
            creditos_ects=ects, caracter=caracter, idioma_pagina="de", url_guia_docente=url, tipo_fuente="pdf_compartido",
            paginas_pdf=f"{lines[h['idx']][0]}-{lines[end - 1][0]}"))
    total = sum(e.creditos_ects or 0 for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="Curriculum 2011W, Stand 01.10.2018", url_plan_estudios=URL_PLAN,
        ects_totales_plan=180.0,
        estrategia_fuente="PDF compartido (texto del Curriculum, alemán): bloques '§ 7 Pflicht- und Wahlmodule'; semestre desde 'Empfohlener Studienverlauf'",
        generado_por="discover_ec_a_innsbru01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Innsbruck NO ofrece un grado de Ingeniería Mecánica: se toma el grado afín de primer ciclo Mechatronik (B.Sc., 180 ECTS-AP, 6 sem., programa conjunto LFUI/UMIT TIROL; Mecánica, CAD, Maquinaria, Resistencia, Termodinámica, Control). "
               f"{len(entries)} módulos (24 Pflichtmodule P1-P24 + P25-A1/A2 según especialización + Wahlmodule W1, W2-A1/A2, W3), {total:g} ECTS brutos (alternativos A1/A2 y Wahl; un estudiante cursa 180). "
               "Parcial: la fuente accesible es el texto del Curriculum, con descripción breve por módulo (Lehrveranstaltungen con contenido en una línea y Lernziele), NO guías docentes por asignatura "
               "(las fichas LV están en LFU:online, no usado). Códigos P/W = los del propio Studienverlauf del curriculum (P25 = n.º de Pflichtmodul siguiente a P24). Stand 01.10.2018; la web indica que el currículo 2011W sigue vigente con modificaciones posteriores (2022) cuyo PDF no se localizó. Idioma: alemán."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "módulos, ECTS bruto", total)
    for e in entries:
        print(e.codigo_asignatura, "|", e.nombre_asignatura, "|", e.creditos_ects, e.semestre, e.caracter, e.paginas_pdf)


if __name__ == "__main__":
    main()
