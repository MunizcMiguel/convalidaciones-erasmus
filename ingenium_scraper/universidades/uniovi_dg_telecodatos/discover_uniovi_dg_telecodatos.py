#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universidad de Oviedo, Grado en Ingeniería de Tecnologías Industriales (plantilla: uniovi/discover_uniovi_dg_telecodatos.py).

Fuente: la ficha oficial del grado en uniovi.es (portlet Liferay "UnioviSiesWeb").
El plan de estudios viene en el HTML estático de esa página, dentro de
`#asignaturasAccordion`: un `div.collapse` por curso+semestre con una tabla
(Asignatura | Créditos | Carácter | Itinerario Bilingüe | Detalle).
No existe API/JSON del plan; sí hay un endpoint JSON por asignatura
(serveGuiasDocentes) que se usa aquí solo para conocer el curso académico vigente.

Uso (desde la raíz del proyecto):
    python universidades/uniovi_dg_telecodatos/discover_uniovi_dg_telecodatos.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
PLAN_URL = "https://www.uniovi.es/estudia/grados/ingenieria/telecomunicaciondatos"
PLAN_CODE = None  # se detecta del HTML del plan (p. ej. GIMECA01)
UNIVERSIDAD = "Universidad de Oviedo"
SLUG = "uniovi_dg_telecodatos"
PORTLET = "es_uniovi_sies_web_UnioviSiesWebPortlet"

ORDINAL = {"primero": 1, "segundo": 2, "tercero": 3, "cuarto": 4, "quinto": 5, "sexto": 6}
SEMESTRE = {"primer-semestre": 1, "segundo-semestre": 2}
CARACTER = {
    "formación básica": "formacion_basica",
    "obligatoria": "obligatoria",
    "optativa": "optativa",
    "trabajo fin de carrera": "tfg",
    "trabajo fin de grado": "tfg",
    "prácticas externas": "practicas",
    "complementos de formación": "complementos_formacion",
}
COURSE_HREF = re.compile(r"/-/fof/asignatura/([A-Z0-9]+-(?:\d+|C)-\d+)/?$")
COLLAPSE_ID = re.compile(r"^([a-z]+)-temporalidad-(.+)$")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def guias_list_url(asignatura_id: str) -> str:
    """Endpoint JSON con las guías docentes (una por curso académico) de una asignatura."""
    return (f"{PLAN_URL}?p_p_id={PORTLET}&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view"
            f"&p_p_resource_id=serveGuiasDocentes&p_p_cacheability=cacheLevelPage"
            f"&_{PORTLET}_asignaturaId={asignatura_id}")


def parse_plan(html: str) -> tuple[str, float, dict[str, float], list[dict]]:
    soup = BeautifulSoup(html, "lxml")

    # Nombre del grado: primer <h2> no vacío ("Grado en Ingeniería Mecánica (PARS)")
    titulo = next(norm(h.get_text()) for h in soup.find_all("h2") if norm(h.get_text()))
    nombre_grado = norm(re.sub(r"\(PARS\)", "", titulo))

    # ECTS totales y desglose por tipo
    total_el = soup.select_one(".ects-total .creditos-total")
    ects_total = float(norm(total_el.get_text()).replace(",", "."))
    bloque = norm(soup.select_one(".item-total-wrapper").parent.get_text(" "))
    desglose = {k.strip(): float(v.replace(",", "."))
                for k, v in re.findall(r"([A-Za-zÁÉÍÓÚáéíóúñ ]+?)\s+(\d+(?:[.,]\d+)?)(?=\s|$)", bloque)}

    acc = soup.find(id="asignaturasAccordion")
    if acc is None:
        raise RuntimeError("No se encuentra #asignaturasAccordion: ¿ha cambiado la página?")

    rows: list[dict] = []
    for col in acc.find_all("div", class_="collapse"):
        m = COLLAPSE_ID.match(col.get("id", ""))
        if not m or m.group(1) not in ORDINAL or m.group(2) not in SEMESTRE:
            raise RuntimeError(f"Bloque de plan con id inesperado: {col.get('id')!r}")
        curso, sem = ORDINAL[m.group(1)], SEMESTRE[m.group(2)]
        cabeceras = [norm(th.get_text()) for th in col.select("thead th")]
        if cabeceras[:4] != ["Asignatura", "Créditos", "Carácter", "Itinerario Bilingüe"]:
            raise RuntimeError(f"Cabeceras inesperadas en {col.get('id')}: {cabeceras}")
        for tr in col.select("tbody tr"):
            tds = tr.find_all("td")
            a = tds[0].find("a", href=True)
            hm = COURSE_HREF.search(a["href"])
            if not hm:
                raise RuntimeError(f"Enlace de asignatura inesperado: {a['href']}")
            codigo = hm.group(1)
            if codigo.split("-")[1].isdigit() and int(codigo.split("-")[1]) != curso:
                raise RuntimeError(f"{codigo}: el curso del código no coincide con el bloque {col.get('id')}")
            rows.append({
                "codigo": codigo,
                "nombre": norm(tds[0].get_text()),
                "creditos": float(norm(tds[1].get_text()).replace(",", ".")),
                "caracter_original": norm(tds[2].get_text()),
                "bilingue": norm(tds[3].get_text()),
                "curso": curso,
                "sem": sem,
                "url": a["href"],
            })
    return nombre_grado, ects_total, desglose, rows


def curso_academico_vigente(http: PoliteClient, course_url: str) -> str:
    """Curso académico más reciente con guía publicada (vía la 1.ª asignatura del plan)."""
    page = http.get_text(course_url)
    m = re.search(rf"_{PORTLET}_asignaturaId=(\d+)", page)
    if not m:
        raise RuntimeError(f"No se encuentra asignaturaId en {course_url}")
    guias = http.get_json(guias_list_url(m.group(1)))
    return max(g["periodoAcademico"] for g in guias)


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    nombre_grado, ects_total, desglose, rows = parse_plan(http.get_text(PLAN_URL))
    rows.sort(key=lambda r: (r["curso"], r["sem"], r["codigo"]))
    curso_acad = curso_academico_vigente(http, rows[0]["url"])

    entries = []
    for r in rows:
        car = CARACTER.get(r["caracter_original"].lower())
        if car is None:
            raise RuntimeError(f"Carácter no contemplado: {r['caracter_original']!r} ({r['codigo']})")
        entries.append(CatalogEntry(
            universidad=UNIVERSIDAD,
            nombre_grado=nombre_grado,
            codigo_asignatura=r["codigo"],
            nombre_asignatura=r["nombre"],
            curso_semestre=f"Curso {r['curso']} / Semestre {r['sem']}",
            curso=r["curso"],
            semestre=(r["curso"] - 1) * 2 + r["sem"],
            creditos_ects=r["creditos"],
            caracter=car,
            idioma_pagina="es",
            url_guia_docente=r["url"],
            tipo_fuente="html",
        ))

    # ---------- validación ----------
    codigos = [e.codigo_asignatura for e in entries]
    dup = {c for c in codigos if codigos.count(c) > 1}
    assert not dup, f"Códigos duplicados: {dup}"
    assert all(e.url_guia_docente for e in entries), "Fila sin URL"
    suma = {}
    for e in entries:
        suma[e.caracter] = suma.get(e.caracter, 0) + e.creditos_ects
    ofertado = sum(suma.values())
    # Los bloques no optativos deben cuadrar con el desglose oficial (claves normalizadas).
    dn = {k.lower(): v for k, v in desglose.items()}
    def of(*ks):
        return next((dn[k] for k in ks if k in dn), None)
    esperado = {"formacion_basica": of("formación básica"), "obligatoria": of("obligatorios", "obligatorias"),
                "tfg": of("trabajo fin de estudios"), "practicas": of("prácticas externas")}
    avisos = []
    for k, v in esperado.items():
        if v is None:
            if suma.get(k, 0):
                avisos.append(f"{k}: {suma[k]:g} ECTS sin dato oficial")
            continue
        if (suma.get(k, 0) < v) if k == "tfg" else (suma.get(k, 0) != v):
            avisos.append(f"ECTS {k}: catálogo {suma.get(k, 0):g} != plan {v:g}")
    opt = of("optativos", "optativas")
    if opt is not None and suma.get("optativa", 0) < opt:
        avisos.append("oferta de optativas inferior a la exigida")
    assert not avisos, "; ".join(avisos) + f" | desglose={desglose}"
    n_bil = sum(1 for r in rows if r["bilingue"].lower().startswith("s"))

    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=nombre_grado,
        curso_academico=curso_acad,
        url_plan_estudios=PLAN_URL,
        ects_totales_plan=ects_total,
        estrategia_fuente=("HTML estático: tabla del plan de estudios (#asignaturasAccordion) en la ficha "
                           "oficial del grado en uniovi.es (portlet Liferay UnioviSiesWeb). La guía se obtiene "
                           "desde la página de cada asignatura: asignaturaId -> JSON serveGuiasDocentes -> "
                           "fragmento HTML /GuiaDocente."),
        generado_por="discover_uniovi_dg_telecodatos.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(f"{len(entries)} asignaturas, {ofertado:g} ECTS ofertados frente a {ects_total:g} del plan: "
               f"se ofertan {suma.get('optativa', 0):g} ECTS optativos y el estudiante cursa "
               f"{opt if opt is not None else 0:g}. Formación básica {suma.get('formacion_basica', 0):g}, obligatorias "
               f"{suma.get('obligatoria', 0):g}, TFG ofertado {suma.get('tfg', 0):g} (varios TFG alternativos por mención; el plan exige {of('trabajo fin de estudios') or 0:g}), complementos de formación {suma.get('complementos_formacion', 0):g}; obligatorias y básica coinciden con el desglose oficial. "
               f"{n_bil} asignaturas pertenecen al itinerario bilingüe. url_guia_docente es la página de la "
               f"asignatura (ES); la versión inglesa de la guía se obtiene con el prefijo /en/ "
               f"(ver notas_descubrimiento.md)."),
    )
    catalog = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(catalog.model_dump())

    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{nombre_grado} [{curso_acad}]: {len(entries)} asignaturas, {ofertado:g} ECTS ofertados "
          f"(plan {ects_total:g}) -> {out}")
    print("ECTS por carácter:", json.dumps(suma, ensure_ascii=False), "| desglose oficial:",
          json.dumps(desglose, ensure_ascii=False))
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
