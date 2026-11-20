#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universidad de Zaragoza, Grado en Ingeniería Mecánica (EINA).

Fuente: portal oficial de titulaciones estudios.unizar.es (HTML estático, Yii).
  1. Ficha del estudio (/estudio/ver?id=149) -> enlace "Asignaturas del plan NNN"
     (de ahí salen el curso académico vigente, el centro y el plan).
  2. Tabla de asignaturas del plan (Curso | Periodo | Código | Nombre | Carácter | Créditos |
     situación | Lím. plazas | Idioma).
  3. Ficha de cada asignatura -> enlace "Formato web" de la guía docente (host sia.unizar.es).

Uso (desde la raíz del proyecto):
    python universidades/es_zaragoza/discover_es_zaragoza.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_zaragoza"
UNIVERSIDAD = "Universidad de Zaragoza"
BASE = "https://estudios.unizar.es"
ESTUDIO_URL = f"{BASE}/estudio/ver?id=149"  # 149 = Grado en Ingeniería Mecánica
RUCT = {"basica": 60.0, "obligatorios": 132.0, "optativos": 36.0, "practicas": 0.0, "tfg": 12.0, "total": 240.0}

CARACTER = {
    "formación básica": "formacion_basica",
    "obligatoria": "obligatoria",
    "optativa": "optativa",
    "trabajo fin de grado": "tfg",
}
IDIOMA = {"castellano": "es", "inglés": "en", "ingles": "en"}
HEADERS = ["Curso", "Periodo", "Código", "Nombre", "Carácter", "Créditos", "", "Lím. plazas opt",
           "Idioma de impartición"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def find_plan_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    out = []
    for a in soup.find_all("a", href=True):
        m = re.fullmatch(r"Asignaturas del plan (\d+)", norm(a.get_text()))
        if m and "/estudio/asignaturas" in a["href"]:
            out.append((m.group(1), urljoin(BASE, a["href"])))
    return out


def parse_plan(html: str) -> tuple[str, str, dict[str, str], list[dict]]:
    soup = BeautifulSoup(html, "lxml")
    grado = norm(soup.find("h1").get_text())
    centro = norm(soup.find("h2").get_text())
    table = soup.find("table")
    heads = [norm(th.get_text()) for th in table.find_all("th")]
    if heads != HEADERS:
        raise RuntimeError(f"Cabeceras inesperadas: {heads}")
    # datos del plan (Créditos, Regulación normativa...) como texto "clave : valor"
    info_txt = norm(soup.get_text(" "))
    info = {}
    for k in ("Créditos", "Regulación normativa"):
        m = re.search(re.escape(k) + r"\s*:\s*(RD [\d/]+|\d+(?:[.,]\d+)?)", info_txt)
        if m:
            info[k] = m.group(1)
    rows = []
    for tr in table.select("tr[data-key]"):
        tds = tr.find_all("td")
        tip = tds[1].find(class_="tooltiptext")
        periodo_largo = norm(tip.get_text()) if tip else ""
        if tip:
            tip.extract()
        a = tds[2].find("a", href=True)
        row = {
            "curso": int(norm(tds[0].get_text())),
            "periodo": norm(tds[1].get_text()),
            "periodo_largo": periodo_largo,
            "codigo": norm(tds[2].get_text()),
            "nombre": norm(tds[3].get_text()),
            "caracter_original": norm(tds[4].get_text()),
            "creditos": float(norm(tds[5].get_text()).replace(",", ".")),
            "situacion": norm(tds[6].get_text()),
            "idioma": norm(tds[8].get_text()),
            "url_ficha": urljoin(BASE, a["href"]),
        }
        if parse_qs(urlsplit(a["href"]).query)["asignatura_id"] != [row["codigo"]]:
            raise RuntimeError(f"El enlace no corresponde al código {row['codigo']}")
        rows.append(row)
    if soup.select("ul.pagination a"):
        raise RuntimeError("La tabla de asignaturas está paginada: revisar")
    return grado, centro, info, rows


def guia_web_url(ficha_html: str, codigo: str, anyo: str) -> str | None:
    """Enlace 'Formato web' de la guía docente en la ficha de la asignatura."""
    soup = BeautifulSoup(ficha_html, "lxml")
    for a in soup.find_all("a", href=True):
        if norm(a.get_text()) == "Formato web":
            q = parse_qs(urlsplit(a["href"]).query)
            if q.get("_codAsignatura") != [codigo] or q.get("_anoAcademico") != [anyo]:
                raise RuntimeError(f"{codigo}: enlace de guía inesperado {a['href']}")
            return a["href"]
    return None


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache", headers={"Accept-Language": "es-ES,es;q=0.9"})
    planes = find_plan_links(http.get_text(ESTUDIO_URL))
    if len(planes) != 1:
        raise RuntimeError(f"Se esperaba un único plan vigente y hay: {planes}")
    plan, plan_url = planes[0]
    anyo = parse_qs(urlsplit(plan_url).query)["anyo_academico"][0]
    curso_acad = f"{anyo}-{(int(anyo) + 1) % 100:02d}"
    grado, centro, info, rows = parse_plan(http.get_text(plan_url))
    rows.sort(key=lambda r: (r["curso"], r["periodo"] or "Z", r["codigo"]))

    entries, sin_guia, no_ofertadas = [], [], []
    for r in rows:
        car = CARACTER.get(r["caracter_original"].lower())
        if car is None:
            raise RuntimeError(f"Carácter no contemplado: {r['caracter_original']!r}")
        url = guia_web_url(http.get_text(r["url_ficha"]), r["codigo"], anyo)
        if url is None:
            sin_guia.append(r["codigo"])
        if r["situacion"]:
            no_ofertadas.append(f"{r['codigo']} {r['nombre']} ({r['situacion']})")
        sem = {"S1": 1, "S2": 2}.get(r["periodo"])  # "S1, S2" (grupos en ambos semestres) y "A" (anual) -> None
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD,
            nombre_grado=grado,
            codigo_asignatura=r["codigo"],
            nombre_asignatura=r["nombre"],
            curso_semestre=f"Curso {r['curso']} / {r['periodo_largo'] or 'periodo no definido'}",
            curso=r["curso"],
            semestre=(r["curso"] - 1) * 2 + sem if sem else None,
            creditos_ects=r["creditos"],
            caracter=car,
            idioma_pagina=IDIOMA.get(r["idioma"].lower(), "es"),
            url_guia_docente=url,
            tipo_fuente="html" if url else "sin_guia",
        ))

    # ---------- validación ----------
    codigos = [e.codigo_asignatura for e in entries]
    assert len(set(codigos)) == len(codigos), "Códigos duplicados"
    suma: dict[str, float] = {}
    for e in entries:
        suma[e.caracter] = suma.get(e.caracter, 0) + e.creditos_ects
    assert suma.get("formacion_basica") == RUCT["basica"], suma
    assert suma.get("obligatoria") == RUCT["obligatorios"], suma
    assert suma.get("tfg") == RUCT["tfg"], suma
    assert suma.get("optativa", 0) >= RUCT["optativos"], suma
    total_plan = float(info["Créditos"].replace(",", "."))
    assert total_plan == RUCT["total"], info
    practicas = [e for e in entries if e.nombre_asignatura.lower().startswith("prácticas externas")]

    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=grado,
        curso_academico=curso_acad,
        url_plan_estudios=plan_url,
        ects_totales_plan=total_plan,
        estrategia_fuente=("HTML estático de estudios.unizar.es: ficha del estudio -> tabla 'Asignaturas del plan' -> "
                           "ficha de cada asignatura, de la que se toma el enlace 'Formato web' de la guía docente "
                           "(aplicación SIGMA DOA en sia.unizar.es; HTML con pestañas Castellano/Inglés)."),
        generado_por="discover_es_zaragoza.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(f"Centro: {centro} (único centro en el RUCT). Plan {plan} ({info.get('Regulación normativa', '')}), "
               f"el único que el portal lista para el estudio 149 en {curso_acad}; sustituye al plan 434 y "
               f"corresponde al título RUCT 2502485. {len(entries)} asignaturas, {sum(suma.values()):g} ECTS "
               f"ofertados frente a {total_plan:g} del plan. Formación básica {suma['formacion_basica']:g}, "
               f"obligatorias {suma['obligatoria']:g} y TFG {suma['tfg']:g} coinciden con el desglose RUCT; "
               f"se ofertan {suma['optativa']:g} ECTS optativos de los que se cursan {RUCT['optativos']:g}. "
               f"El RUCT da 0 ECTS de prácticas: las {len(practicas)} asignaturas 'Prácticas externas' "
               f"({sum(e.creditos_ects for e in practicas):g} ECTS) son optativas y así constan. "
               f"Periodo 'Semestre 1, Semestre 2' = asignatura con grupos en ambos semestres (semestre=null). "
               f"No ofertadas este curso: {'; '.join(no_ofertadas) or 'ninguna'}. "
               f"Sin enlace de guía: {', '.join(sin_guia) or 'ninguna'}."),
    )
    catalog = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{grado} plan {plan} [{curso_acad}]: {len(entries)} asignaturas, {sum(suma.values()):g} ECTS -> {out}")
    print("ECTS por carácter:", json.dumps(suma, ensure_ascii=False), "| sin guía:", sin_guia)
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
