"""Fase 1 - Konya Teknik Universitesi (KTUN), Muhendislik ve Doga Bilimleri Fakultesi: Makine Muhendisligi (Normal Ogretim).
Hint de la ficha Erasmus (eurep.auth.gr) = fact sheet alojado por una universidad griega; el sitio real es www.ktun.edu.tr.
Fuentes (PDF en www.ktun.edu.tr/Dosyalar/1027/files/): plan 2024-25 NO (codigos, creditos, semestre) + 'Ders Icerikleri' del departamento
(un PDF compartido de 102 paginas con un bloque 'Dersin Adi' por asignatura; version 2019/2020, bilingue TR/EN solo en cabecera).
La plataforma Bologna (obs.ktun.edu.tr) no expone el catalogo por GET (404).
Uso: python universidades/ec_tr_konya05/discover_ec_tr_konya05.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_tr_konya05"
UNIVERSIDAD = "Konya Teknik Üniversitesi - Mühendislik ve Doğa Bilimleri Fakültesi"
GRADO = "Makine Mühendisliği (Mechanical Engineering), Normal Öğretim"
URL_PLAN = "https://www.ktun.edu.tr/Dosyalar/1027/files/2024-25%20%C3%96%C4%9Fretim%20Plan%C4%B1%20(Normal%20%C3%96%C4%9Fretim)(1).pdf"
URL_ICERIK = "https://www.ktun.edu.tr/Dosyalar/1027/files/KTUN_Makine_Muh__Bolumu_Ders_icerikleri_26_06_2020.pdf"
PAGE_HEAD = re.compile(r"^(MAKİNA MÜHENDİSLİĞİ BÖLÜMÜ Doküman No MM-DI-01|DERS İÇERİKLERİ|Revizyon Tarihi .*|DEPARTMENT OF MECHANICAL Revizyon No 01|ENGINEERING Sayfa No \d+/\d+|COURSE CONTENTS)$")


def parse_blocks(pdf_path) -> list[dict]:
    """Bloques 'Dersin Adi' del PDF compartido: [{name, code_no, code_io, page_ini, page_fin, text}]."""
    lines = []  # (pagina, linea)
    with pdfplumber.open(pdf_path) as pdf:
        for i, p in enumerate(pdf.pages, start=1):
            for ln in (p.extract_text(x_tolerance=1.5) or "").splitlines():
                if PAGE_HEAD.match(ln.strip()):
                    continue
                lines.append((i, ln))
    starts = [k for k, (_, ln) in enumerate(lines) if ln.startswith("Dersin Adı")]
    blocks = []
    for n, k in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        seg = lines[k:end]
        txt = "\n".join(ln for _, ln in seg)
        m = re.search(r"Dönemi Dersin Kodu[^\n]*\n(\d+)\s+(\d{7})(?:/(\d{7}))?\s+(.+?)\s+(\d+)\s*$", txt.split("\n", 3)[1] + "\n" + (txt.split("\n", 3)[2] if len(txt.split("\n", 3)) > 2 else ""), re.M)
        hdr = txt.split("\n")
        name = re.sub(r"^Dersin Adı\s*", "", hdr[0]).strip()
        mm = re.match(r"^(\d+)\s+(\d{7})(?:\s*/\s*(\d{7}))?\s+(.+?)\s+(\d+)\s*$", hdr[2].strip()) if len(hdr) > 2 else None
        if not mm:
            continue
        blocks.append({"name": name, "sem": int(mm.group(1)), "code": mm.group(2), "code_io": mm.group(3), "ects": float(mm.group(5)),
                       "page_ini": seg[0][0], "page_fin": seg[-1][0], "text": txt})
    return blocks


def best_block(blocks: list[dict]) -> dict[str, dict]:
    """Un bloque por codigo: prefiere '(2018 ve sonrası)'; si no, el último."""
    out: dict[str, dict] = {}
    for b in blocks:
        cur = out.get(b["code"])
        new_ok = "2018 ve sonrası" in b["name"] or "2018 ve sonras" in b["name"]
        if cur is None or new_ok or ("2018 ve sonras" not in cur["name"]):
            out[b["code"]] = b
    return out


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    plan_pdf = c.get_file(URL_PLAN)
    blocks = best_block(parse_blocks(c.get_file(URL_ICERIK)))
    with pdfplumber.open(plan_pdf) as pdf:
        text = "\n".join(p.extract_text() or "" for p in pdf.pages)
    entries, seen, sem, group, no_block, tot_sem = [], set(), None, "", [], {}
    for ln in text.splitlines():
        h = re.match(r"^(\d)\. SINIF (\d)\. Yarıyıl \((\w+)\)(?:\s*-\s*(.*))?", ln)
        if h:
            sem, group = int(h.group(2)), (h.group(4) or "")
            continue
        m = re.match(r"^(\d{7,8}) (.+?) (\d) (\d) ([\d,.]+) (\d+)(?:\s|$)", ln)
        stj = re.match(r"^(\d{7}) (.+?Stajı) (\d+)$", ln)  # staj: solo AKTS
        if stj:
            m = type("M", (), {"group": lambda self, i, g=(None, stj.group(1), stj.group(2), None, None, None, stj.group(3)): g[i]})()
        if not m or not sem or m.group(1) in seen:
            continue
        code = m.group(1)
        seen.add(code)
        b = blocks.get(code)
        ects = float(m.group(6))
        elective = bool(group) and "eçmeli" in group
        tot_sem[sem] = tot_sem.get(sem, 0) + (0 if elective else ects)
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD, nombre_grado=GRADO, codigo_asignatura=code, nombre_asignatura=m.group(2).strip(),
            curso_semestre=f"Curso {(sem + 1) // 2} / Yarıyıl {sem}", curso=(sem + 1) // 2, semestre=sem, creditos_ects=ects,
            caracter="optativa" if elective else "obligatoria", idioma_pagina="tr",
            url_guia_docente=URL_ICERIK if b else None, tipo_fuente="pdf_compartido" if b else "sin_guia",
            paginas_pdf=f"{b['page_ini']}-{b['page_fin']}" if b else None))
        if not b:
            no_block.append(code)
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes))
    tot = sum(e.creditos_ects for e in entries)
    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado=GRADO, curso_academico="2024/2025 (plan) / contenidos 2019-2020", url_plan_estudios=URL_PLAN,
        ects_totales_plan=240.0, estrategia_fuente="Plan 2024-25 PDF (líneas 'código nombre T U crédito AKTS' bajo cada 'N. SINIF M. Yarıyıl') + PDF compartido de contenidos (bloques 'Dersin Adı') emparejados por código NÖ",
        generado_por="discover_ec_tr_konya05.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok" if len(no_block) < len(entries) / 2 else "parcial",
        notas=(f"Titulación: Makine Mühendisliği (NÖ), 8 semestres. {len(entries)} filas con código del plan; {len(entries) - len(no_block)} emparejadas con un bloque del PDF de contenidos "
               f"(con versión '2018 ve sonrası' si existe) → pdf_compartido con rango de páginas; sin bloque (sin_guia): {no_block}. "
               f"AKTS de las filas no optativas por semestre: {tot_sem} (suma de todas las filas {tot:g}; los huecos de optativas del plan ('Teknik Seçmeli Ders I', etc.) llevan código solo si el plan lo da). "
               "Aviso: el PDF de contenidos es de 2019/2020, anterior al plan 2024-25; el AKTS del bloque puede diferir del plan (se usa el del plan). "
               "Hint eurep.auth.gr (fact sheet en universidad griega) descartado. obs.ktun.edu.tr/oibs/bologna da 404."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; con bloque", len(entries) - len(no_block), "sin bloque", no_block, "| bloques", len(blocks), "| sem comp", tot_sem)


if __name__ == "__main__":
    main()
