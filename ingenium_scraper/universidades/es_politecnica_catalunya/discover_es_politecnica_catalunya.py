#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Universitat Politècnica de Catalunya (UPC),
Grado en Ingeniería Mecánica (RUCT 2501218), centro EPSEVG (Vilanova i la Geltrú).

Fuente: la ficha oficial del grado en www.upc.edu (versión en castellano). El plan
de estudios viene en el HTML estático, en `div#pla-estudis`: un
`div.pla-estudis-quadrimestre` por cuatrimestre (h3 "Primer cuatrimestre"...), con un
`li` por asignatura: clase CSS = carácter, `a[data-id]` = código oficial de la
asignatura (PRISMA), `a[href]` = guía docente en PDF, `span.pull-right` = ECTS.

AVISO (regla de parada): las guías se sirven en
`https://www.upc.edu/content/grau/guiadocent/pdf/esp/{codigo}` y el robots.txt de
www.upc.edu contiene `Disallow: */content/*` para todos los agentes. Este script
NO descarga ninguna guía: solo lee la ficha del grado y el robots.txt. El catálogo
se marca `estado: "parcial"` y no hay Fase 2.

Uso (desde la raíz del proyecto):
    python universidades/es_politecnica_catalunya/discover_es_politecnica_catalunya.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "es_politecnica_catalunya"
UNIVERSIDAD = "Universitat Politècnica de Catalunya"
HOST = "https://www.upc.edu"
PLAN_URL = HOST + "/es/grados/ingenieria-mecanica-vilanova-i-la-geltru-epsevg"
ROBOTS_URL = HOST + "/robots.txt"
RUCT = {"basica": 60.0, "obligatorios": 126.0, "optativos": 30.0, "practicas": 0.0, "tfg": 24.0, "total": 240.0}

ORDINAL = {"primer": 1, "segundo": 2, "tercer": 3, "cuarto": 4, "quinto": 5, "sexto": 6, "séptimo": 7, "octavo": 8}
CARACTER = {"Obligatoria": "obligatoria", "Optativa": "optativa", "Proyecto": "tfg", "Projecte": "tfg"}
# href de la ficha: https://www.upc.edu/content/../grau/guiadocent/pdf/esp/340023/fisica-i.pdf
GUIDE_HREF = re.compile(r"^https://www\.upc\.edu/content/\.\./grau/guiadocent/pdf/esp/(\d{5,7})/[^/]+\.pdf$")
# Forma canónica: es a donde redirige el href anterior y la que enlaza la web de la EPSEVG
GUIDE_URL = HOST + "/content/grau/guiadocent/pdf/esp/{codigo}"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def robots_rule_matches(rule: str, path: str) -> bool:
    """Coincidencia de una regla de robots.txt con comodines (* y $), RFC 9309."""
    rx = "".join(".*" if c == "*" else ("$" if c == "$" else re.escape(c)) for c in rule)
    return re.match(rx, path) is not None


def guides_disallowed(robots_txt: str, path: str) -> list[str]:
    """Reglas Disallow del grupo `User-agent: *` que afectan a `path`."""
    hits: list[str] = []
    agents: list[str] = []
    in_rules = False
    for line in robots_txt.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = (x.strip() for x in line.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if in_rules:
                agents, in_rules = [], False
            agents.append(v)
        elif k in ("disallow", "allow"):
            in_rules = True
            if k == "disallow" and v and "*" in agents and robots_rule_matches(v, path) and v not in hits:
                hits.append(v)
    return hits


def parse_plan(html: str) -> tuple[float, str, list[dict]]:
    soup = BeautifulSoup(html, "lxml")
    texto = norm(soup.get_text(" "))
    m = re.search(r"Carga lectiva\s+(\d+)\s+créditos ECTS", texto)
    if not m:
        raise RuntimeError("No se encuentra la carga lectiva en la ficha")
    ects_total = float(m.group(1))
    m = re.search(r"Nota de corte del curso (\d{4})-\d{2}(\d{2})", texto)
    if not m:
        raise RuntimeError("No se encuentra el curso académico en la ficha")
    curso_academico = f"{m.group(1)}-{m.group(2)}"

    plan = soup.find(id="pla-estudis")
    if plan is None:
        raise RuntimeError("No se encuentra #pla-estudis: ¿ha cambiado la página?")
    rows: list[dict] = []
    for bloque in plan.find_all("div", class_="pla-estudis-quadrimestre"):
        if bloque.get("id") == "llegenda":
            continue
        titulo = norm(bloque.find("h3").get_text())
        m = re.match(r"^(\w+) cuatrimestre$", titulo, re.I)
        if not m or m.group(1).lower() not in ORDINAL:
            raise RuntimeError(f"Cabecera de cuatrimestre inesperada: {titulo!r}")
        sem = ORDINAL[m.group(1).lower()]
        for li in bloque.select("ul.pla-estudis-assignatures > li"):
            a = li.find("a", attrs={"data-id": True})
            clases = [c for c in li.get("class", []) if c in CARACTER]
            if a is None or len(clases) != 1:
                raise RuntimeError(f"Fila de asignatura inesperada: {li}")
            hm = GUIDE_HREF.match(a.get("href", ""))
            if not hm or hm.group(1) != a["data-id"]:
                raise RuntimeError(f"Enlace de guía inesperado: {a.get('href')!r}")
            rows.append({
                "codigo": a["data-id"],
                "nombre": norm(a.get_text()),
                "creditos": float(norm(li.find("span", class_="pull-right").get_text()).replace(",", ".")),
                "caracter": CARACTER[clases[0]],
                "sem": sem,
                "titulo_sem": titulo,
            })
    return ects_total, curso_academico, rows


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    ects_total, curso_academico, rows = parse_plan(http.get_text(PLAN_URL))

    dup = [c for c, n in Counter(r["codigo"] for r in rows).items() if n > 1]
    if dup:
        raise RuntimeError(f"Códigos duplicados: {dup}")

    sample_path = GUIDE_URL.format(codigo=rows[0]["codigo"])[len(HOST):]
    reglas = guides_disallowed(http.get_text(ROBOTS_URL), sample_path)

    suma: dict[str, float] = defaultdict(float)
    for r in rows:
        suma[r["caracter"]] += r["creditos"]
    n_opt = sum(1 for r in rows if r["caracter"] == "optativa")
    plan_ects = suma["obligatoria"] + suma["tfg"] + RUCT["optativos"]
    cuadra = ects_total == RUCT["total"] and plan_ects == RUCT["total"]

    notas = (
        "Centro elegido: Escuela Politécnica Superior de Ingeniería de Vilanova i la Geltrú (EPSEVG), el primero "
        "de la lista del RUCT; el mismo título (RUCT 2501218, RD 1393/2007, plan 2009, único título listado) se imparte "
        "también en la EPSEM (Manresa), la ESEIAAT (Terrassa) y la EEBE (Barcelona Este), con planes de asignaturas "
        "propios. "
        f"ECTS: obligatorias {suma['obligatoria']:g} (la ficha no distingue formación básica de obligatoria; el RUCT da "
        f"{RUCT['basica']:g} básicos + {RUCT['obligatorios']:g} obligatorios = {RUCT['basica'] + RUCT['obligatorios']:g}), "
        f"TFG {suma['tfg']:g} (RUCT {RUCT['tfg']:g}); el estudiante cursa {RUCT['optativos']:g} ECTS optativos, que elige "
        f"entre una oferta de {n_opt} optativas ({suma['optativa']:g} ECTS; RUCT prácticas 0: si hay prácticas externas "
        f"cuentan como optativas). Obligatorias + TFG + {RUCT['optativos']:g} optativos = {plan_ects:g}; ficha "
        f"{ects_total:g}; RUCT {RUCT['total']:g}" + (" (cuadra). " if cuadra else " (NO CUADRA: revisar). ") +
        "El semestre de las optativas es el que indica la ficha (la mayoría agrupadas en el 7.º cuatrimestre). "
        "El curso académico se toma de la propia ficha ('Nota de corte del curso'); la ficha no dice de qué curso "
        "son las guías enlazadas. "
        + ("REGLA DE PARADA: las guías docentes (un PDF por asignatura) se sirven en "
           + GUIDE_URL.format(codigo="{codigo}") + " y el robots.txt de www.upc.edu excluye esa ruta para todos los "
           f"agentes ({', '.join('Disallow: ' + r for r in reglas)}). El href de la ficha "
           "(/content/../grau/guiadocent/...) se normaliza a /grau/guiadocent/..., que no casa con la regla, pero "
           "redirige a la ruta /content/ excluida. No se descargan guías; no hay Fase 2: catálogo completo, sin Markdown."
           if reglas else "robots.txt no excluye la ruta de las guías.")
    )

    meta = CatalogMeta(
        universidad=UNIVERSIDAD, slug=SLUG, nombre_grado="Grado en Ingeniería Mecánica",
        curso_academico=curso_academico, url_plan_estudios=PLAN_URL, ects_totales_plan=ects_total,
        estrategia_fuente="HTML estático: ficha del grado en www.upc.edu (div#pla-estudis). Guías: un PDF por asignatura "
                          "en www.upc.edu/content/grau/guiadocent (ruta excluida por robots.txt).",
        generado_por=Path(__file__).name, generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial" if reglas else "ok", notas=notas,
    )
    entries = [CatalogEntry(
        universidad=UNIVERSIDAD, nombre_grado=meta.nombre_grado,
        codigo_asignatura=r["codigo"], nombre_asignatura=r["nombre"],
        curso_semestre=f"Curso {(r['sem'] + 1) // 2} / {r['titulo_sem']}",
        curso=(r["sem"] + 1) // 2, semestre=r["sem"], creditos_ects=r["creditos"], caracter=r["caracter"],
        idioma_pagina="es", url_guia_docente=GUIDE_URL.format(codigo=r["codigo"]), tipo_fuente="pdf",
    ) for r in rows]
    catalog = Catalog(meta=meta, asignaturas=entries)
    (HERE / "catalogo_urls.json").write_text(
        json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{len(entries)} asignaturas · curso {curso_academico} · estado {meta.estado}")
    for k in ("obligatoria", "optativa", "tfg"):
        print(f"  {k}: {sum(1 for r in rows if r['caracter'] == k)} asignaturas, {suma[k]:g} ECTS")
    print(f"  obligatorias + TFG + {RUCT['optativos']:g} optativos = {plan_ects:g} (ficha {ects_total:g}, RUCT {RUCT['total']:g})")
    print(f"  robots.txt sobre {sample_path}: {reglas or 'permitido'}")
    print(f"  red={http.stats['network']} caché={http.stats['cache']}")


if __name__ == "__main__":
    main()
