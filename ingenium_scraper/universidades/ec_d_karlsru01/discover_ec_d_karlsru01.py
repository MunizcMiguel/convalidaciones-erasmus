"""Fase 1 - KIT (Karlsruher Institut fuer Technologie, NO Hochschule Karlsruhe) - Bachelor Maschinenbau (B.Sc., SPO 2015).
Fuente: Modulhandbuch oficial (PDF compartido, aleman, Stand 28.02.2025) en www.mach.kit.edu. Una fila por Modul (nivel modulo, no Teilleistung).
Uso: python universidades/ec_d_karlsru01/discover_ec_d_karlsru01.py
"""
from __future__ import annotations
import io, json, re, sys, time, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_karlsru01"
UNI = "Karlsruher Institut für Technologie (KIT)"
GRADO = "Maschinenbau (B.Sc.), SPO 2015"
URL_PLAN = "https://www.mach.kit.edu/"
PDF = "https://www.mach.kit.edu/download/MHB/82-604-H-20165_v1_2025-02-28_de.pdf"
MOD = re.compile(r"^M\s?[\d.]+\s+Modul:\s+(.+?)\s+\[(M-[A-Z]+-\d+)\]\s*$")
CHROME = re.compile(r"^(\d+\s+MODULE\s+Modul:|Bachelorstudiengang Maschinenbau \(B\.Sc\.\), Stand|Modulhandbuch gültig ab|•\s*$)")


def get_lines(client: PoliteClient) -> list[tuple[int, str]]:
    r = pypdf.PdfReader(io.BytesIO(client.get_bytes(PDF)))
    out = []
    for pn, p in enumerate(r.pages, 1):
        for l in unicodedata.normalize("NFC", p.extract_text() or "").split("\n"):
            if CHROME.match(l.strip()):
                continue
            out.append((pn, l.rstrip()))
    return out


def modules(lines: list[tuple[int, str]]) -> list[dict]:
    idx = [i for i, (_, l) in enumerate(lines) if MOD.match(l.strip())]
    out = []
    for k, i in enumerate(idx):
        j = idx[k + 1] if k + 1 < len(idx) else len(lines)
        m = MOD.match(lines[i][1].strip())
        for t in range(i + 1, j):  # el modulo termina donde empiezan las Teilleistungen (T x.y)
            if re.match(r"^T\s?[\d.]+\s+Teilleistung:", lines[t][1].strip()):
                j = t
                break
        out.append(dict(code=m.group(2), name=m.group(1).strip(), body=[l for _, l in lines[i + 1:j]], p0=lines[i][0], p1=lines[j - 1][0]))
    return out


def field(body: list[str], label: str) -> str | None:
    for n, l in enumerate(body):
        if l.strip() == label and n + 1 < len(body):
            return body[n + 1].strip()
    return None


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    mods = modules(get_lines(c))
    entries, seen = [], set()
    for m in mods:
        if m["code"] in seen:
            continue
        seen.add(m["code"])
        lp = field(m["body"], "Leistungspunkte")
        try:
            ects = float(lp.replace(",", ".")) if lp else None
        except ValueError:
            ects = None
        lang = (field(m["body"], "Sprache") or "Deutsch")
        part = " ".join(l.strip() for l in m["body"][:8] if l.strip().startswith("Bestandteil von"))
        opt = bool(re.search(r"Wahlpflicht|Schwerpunkt|Zusatzleistung|Wahlbereich|Profil", m["name"] + " " + part))
        entries.append(CatalogEntry(
            universidad=UNI, nombre_grado=GRADO, codigo_asignatura=m["code"], nombre_asignatura=m["name"],
            curso_semestre="Semestre no indicado en el Modulhandbuch", curso=None, semestre=None, creditos_ects=ects,
            caracter="optativa" if opt else "obligatoria", idioma_pagina="de" if lang.startswith("Deutsch") else "en",
            url_guia_docente=PDF, tipo_fuente="pdf_compartido", paginas_pdf=f"{m['p0']}-{m['p1']}"))
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="SS 2025", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="Modulhandbuch PDF compartido (520 págs.) parseado con pypdf; módulo = línea 'M x.y Modul: NOMBRE [M-...]'",
        generado_por="discover_ec_d_karlsru01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="ok",
        notas=("KIT (D KARLSRU01), universidad distinta de Hochschule Karlsruhe (ec_d_karlsru05/hka). Excel: Máster Ing. Industrial (ISCED 0715, 2 plazas); se toma "
               "el grado de Maschinenbau B.Sc. (SPO 2015, 6 semestres, 180 LP), equivalente de primer ciclo a la Mecánica. Fichas a nivel de MÓDULO (no de Teilleistung/asignatura); "
               "los módulos listados son los 'Modul' del PDF: Pflicht (Höhere Mathematik, Werkstoffkunde, Technische Mechanik, Thermodynamik, MKL, Fertigungsprozesse…) más Wahlpflicht "
               "y Zusatzleistungen. Sin semestre por módulo (el Studienplan lo da aparte). 'optativa' = Wahlpflicht/Schwerpunkt/Zusatz según nombre y 'Bestandteil von'. "
               "El Modulhandbuch no incluye bibliografía; la Erfolgskontrolle suele remitir a las Teilleistungen. Se elimina 'Verantwortung' (profesorado). "
               "Los Schwerpunkt-Module con mucho detalle y las Teilleistungen (T-MACH) quedan dentro del texto del módulo. robots.txt de www.mach.kit.edu permite /download/."))
    cat = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(len(entries), "filas; ECTS", sum(e.creditos_ects or 0 for e in entries))


if __name__ == "__main__":
    main()
