#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Munster Technological University (MTU), Cork.
Bachelor of Engineering (Honours) in Mechanical Engineering (MT 836, Akari CR_EMECH_8).

RESULTADO: catálogo PARCIAL (sin asignaturas). Motivo:
  * La ficha oficial del grado (www.mtu.ie/courses/mt836/, permitida por robots.txt)
    NO contiene el plan de estudios: solo un enlace "View Modules" hacia
    https://mtu.akarisoftware.com/index.cfm/page/course/coursecode/CR_EMECH_8
  * mtu.akarisoftware.com (Akari Curriculum: plan + descriptores de módulo) responde
    403 Forbidden a CUALQUIER ruta cuando el User-Agent se identifica como bot
    (incluido /robots.txt). Es un bloqueo de acceso automatizado -> regla STOP:
    no se descarga nada de ese host y no hay Fase 2.

Este script solo lee la ficha del grado en www.mtu.ie y extrae de ella los metadatos
del programa y la URL/código Akari. No inventa códigos, nombres ni créditos.

Uso (desde la raíz del proyecto):
    python universidades/mtu/discover_mtu.py
    python universidades/mtu/discover_mtu.py --probe-akari   # 1 petición: ¿sigue el 403?
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
PLAN_URL = "https://www.mtu.ie/courses/mt836/"
UNIVERSIDAD = "Munster Technological University"
SLUG = "mtu"
AKARI_HREF = re.compile(r"^https?://mtu\.akarisoftware\.com/index\.cfm/page/course/coursecode/([A-Z0-9_]+)/?$")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def parse_course_page(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style"]):
        t.decompose()
    lines = [norm(x) for x in soup.get_text("\n").split("\n")]
    lines = [x for x in lines if x]

    def after(label: str) -> str:
        """Valor que sigue a una etiqueta de la ficha ('Course Code' -> 'MT 836')."""
        i = lines.index(label)
        return lines[i + 1]

    h1 = norm(soup.find("h1").get_text())
    # El tipo de título es la línea que sigue al <h1> ("Bachelor of Engineering (Honours)")
    award = lines[lines.index(h1) + 1]
    if not award.lower().startswith(("bachelor", "master", "higher", "certificate")):
        raise RuntimeError(f"Línea de título inesperada tras el h1: {award!r}")

    akari = [(a["href"], AKARI_HREF.match(a["href"])) for a in soup.find_all("a", href=True)]
    akari = [(h, m.group(1)) for h, m in akari if m]
    if len({h for h, _ in akari}) != 1:
        raise RuntimeError(f"Se esperaba 1 enlace Akari 'View Modules', hay: {akari}")

    art = soup.find(id="modules")
    glance = []
    for h in soup.find_all(["h2", "h3", "h4"]):
        if "at a glance" in norm(h.get_text()).lower():
            ul = h.find_next("ul")
            glance = [norm(li.get_text()) for li in ul.find_all("li")] if ul else []
    cao = next((x for x in lines if re.search(r"CAO Points in (\d{4})", x)), "")
    year = re.search(r"CAO Points in (\d{4})", cao)

    return {
        "titulo": h1,
        "award": award,
        "nombre_grado": f"{award} in {h1}",
        "modo": after("Type of Programme"),
        "duracion": after("Duration"),
        "nfq": after("Course NFQ Level"),
        "codigo_cao": after("Course Code"),
        "campus": after("Location(s)"),
        "akari_url": akari[0][0],
        "akari_code": akari[0][1],
        "modules_section_has_list": bool(art and art.find(["table", "ul", "ol"])),
        "first_year_at_a_glance": glance,
        "anio_cao": int(year.group(1)) if year else None,
    }


def probe_akari(url: str) -> str:
    """Una única petición (sin caché de errores) para comprobar si el host sigue vetando al bot."""
    http = PoliteClient(cache_dir=HERE / "raw_cache", max_retries=0)
    try:
        http.get_bytes(url, force=True)
        return "ACCESIBLE (200): el bloqueo ha desaparecido; revisar notas y rehacer Fase 1."
    except FetchError as e:
        return f"BLOQUEADO: {e}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-akari", action="store_true",
                    help="comprueba (1 petición) si mtu.akarisoftware.com sigue devolviendo 403")
    args = ap.parse_args()

    # robots.txt de www.mtu.ie: 'User-agent: *' -> Crawl-delay: 10
    http = PoliteClient(cache_dir=HERE / "raw_cache", min_delay=10.0, max_delay=12.0)
    info = parse_course_page(http.get_text(PLAN_URL))

    if info["modules_section_has_list"]:
        raise RuntimeError("La ficha de www.mtu.ie ahora trae una lista/tabla de módulos: "
                           "rehacer el descubrimiento a partir de ella.")

    y = info["anio_cao"]
    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=info["nombre_grado"],
        nivel="bachelor",
        curso_academico=f"{y}/{(y + 1) % 100:02d}" if y else "desconocido",
        url_plan_estudios=info["akari_url"],
        ects_totales_plan=None,  # la ficha de www.mtu.ie no publica los ECTS totales
        estrategia_fuente=(
            "Ficha HTML del grado en www.mtu.ie (solo metadatos) -> enlace 'View Modules' a Akari "
            f"Curriculum ({info['akari_url']}). Akari devuelve 403 a clientes automatizados: "
            "plan y descriptores NO descargados (regla STOP)."),
        generado_por="discover_mtu.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial",
        notas=(
            f"Programa: {info['nombre_grado']} · {info['codigo_cao']} · {info['nfq']} · {info['modo']} · "
            f"{info['duracion']} · {info['campus']} · código Akari {info['akari_code']}. "
            f"Ficha: {PLAN_URL}. Catálogo vacío: la única fuente con códigos/ECTS/descriptores "
            "(mtu.akarisoftware.com) rechaza con 403 Forbidden todo User-Agent identificado como bot. "
            "Sin Fase 2. La ficha solo da una lista informal de 1.º sin códigos ni créditos: "
            + "; ".join(info["first_year_at_a_glance"])),
    )
    catalog = Catalog(meta=meta, asignaturas=[])
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{info['nombre_grado']} ({info['codigo_cao']}, {info['nfq']}, {info['campus']})")
    print(f"Akari: {info['akari_url']}")
    print(f"Catálogo PARCIAL, 0 asignaturas -> {out}")
    print(f"HTTP: {http.stats}")
    if args.probe_akari:
        print("Akari:", probe_akari(info["akari_url"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
