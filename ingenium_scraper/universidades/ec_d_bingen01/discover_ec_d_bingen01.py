"""Fase 1 - Technische Hochschule Bingen - Maschinenbau (B.Eng.). Fuente: Modulhandbuch PDF compartido (127 pags., aleman, Stand 2026) en th-bingen.de.
Uso: python universidades/ec_d_bingen01/discover_ec_d_bingen01.py
"""
from __future__ import annotations
import io, json, re, sys, time, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_bingen01"
UNI = "Technische Hochschule Bingen"
GRADO = "Maschinenbau (B.Eng.)"
URL_PLAN = "https://www.th-bingen.de/studium/studiengaenge/maschinenbau/maschinenbau-b-eng/dokumente"
PDF = "https://www.th-bingen.de/fileadmin/studium/bachelor/maschinenbau/Modulhandbuch_Bachelor_Maschinenbau_26-09-28.pdf"
HEAD = re.compile(r"^(B-MB-[A-Z0-9]+)\s+(\S.*?)\s*$")
CHROME = re.compile(r"^\s*Technische Hochschule Bingen\s+Modulhandbuch")


def get_lines(client: PoliteClient) -> list[tuple[int, str]]:
    r = pypdf.PdfReader(io.BytesIO(client.get_bytes(PDF)))
    out = []
    for pn, p in enumerate(r.pages, 1):
        for l in unicodedata.normalize("NFC", p.extract_text() or "").split("\n"):
            if CHROME.match(l) or not l.strip():
                continue
            out.append((pn, l.rstrip()))
    return out


def modules(lines):
    idx = [i for i, (_, l) in enumerate(lines)
           if HEAD.match(l.strip()) and "...." not in l and i + 3 < len(lines) and any("Kennnummer" in lines[k][1] for k in range(i + 1, i + 4))]
    out = []
    for k, i in enumerate(idx):
        j = idx[k + 1] if k + 1 < len(idx) else len(lines)
        m = HEAD.match(lines[i][1].strip())
        out.append(dict(code=m.group(1), name=m.group(2).strip(), body=[l for _, l in lines[i + 1:j]], p0=lines[i][0], p1=lines[j - 1][0]))
    return out


def toc_groups(lines):
    """Grupo de cada modulo segun el indice (lineas 'Gruppe ...' seguidas de 'B-MB-XXXX Nombre ....')."""
    grp, out = None, {}
    for _, l in lines:
        t = l.strip()
        if t.startswith("Gruppe"):
            grp = t.split("....")[0].strip()
        m = HEAD.match(t)
        if m and "...." in t and grp:
            out.setdefault(m.group(1), grp)
    return out


def val(body, label, n=3):
    for i, l in enumerate(body[:40]):
        if l.strip() == label:
            return body[i + 1].strip()
    return None


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    lines = get_lines(c)
    mods = modules(lines)
    groups = toc_groups(lines)
    entries, seen = [], set()
    for m in mods:
        if m["code"] in seen:
            continue
        seen.add(m["code"])
        txt = "\n".join(m["body"][:40])
        lp = re.search(r"Leistungs-\s*\n\s*punkte\s*\n\s*(\d+(?:[.,]\d+)?)", txt)
        sem = re.search(r"(\d)\.\s*Semester", txt)
        wahl = bool(re.match(r"Gruppe IV(?![IVX])", groups.get(m["code"], "")))
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=m["code"], nombre_asignatura=re.sub(r"\s+", " ", m["name"]),
            curso_semestre=f"Semestre {sem.group(1)}" if sem else "Semestre no indicado", curso=(int(sem.group(1)) + 1) // 2 if sem else None,
            semestre=int(sem.group(1)) if sem else None, creditos_ects=float(lp.group(1).replace(",", ".")) if lp else None,
            caracter="optativa" if wahl else "obligatoria", idioma_pagina="de", url_guia_docente=PDF, tipo_fuente="pdf_compartido",
            paginas_pdf=f"{m['p0']}-{m['p1']}"))
    tot = sum(e.creditos_ects or 0 for e in entries if e.caracter == "obligatoria")
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2026-27", url_plan_estudios=URL_PLAN, ects_totales_plan=210.0,
        estrategia_fuente="Modulhandbuch PDF compartido parseado con pypdf; módulo = cabecera 'B-MB-XXXX Nombre' + tabla 'Kennnummer'",
        generado_por="discover_ec_d_bingen01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("Excel: Grado Org. Industrial (1 plaza), Grado Ing. Química Industrial y una fila sin titulación (ISCED 0413 gestión). TH Bingen no ofrece Org. Industrial ni Química; "
               "se toma Maschinenbau (B.Eng.), la titulación de Mecánica (prioridad), aunque Wirtschaftsingenieurwesen (Modulhandbuch aparte, Stand 21.11.2024) sería la alternativa "
               "para Org. Industrial y Verfahrens-/Prozesstechnik para Química Industrial. Plan de 7 semestres, 210 LP (dato no verificado en este PDF; los grupos VW son electivos de Vertiefung). "
               f"Obligatorios suman {tot:g} LP en el listado; se omiten datos del Modulbeauftragte. robots.txt de th-bingen.de: 404 (sin restricciones)."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; LP obligatorios", tot)


if __name__ == "__main__":
    main()
