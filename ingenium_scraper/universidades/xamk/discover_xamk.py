#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — South-Eastern Finland University of Applied Sciences (Xamk).

Resultado: catálogo PARCIAL (stop rule del brief).

1. Las titulaciones se leen del sitemap oficial de programas (www.xamk.fi/sitemap-education*.xml).
   No existe "Insinööri (AMK), konetekniikka" (Mechanical Engineering) en la oferta actual: el
   script lo comprueba y elige la titulación de grado más cercana, Insinööri (AMK) energiatekniikka
   (240 op, con base de konetekniikka), leyendo su ficha en www.xamk.fi.
2. Los planes y las guías (opintojaksot) solo se publican en el opinto-opas de Peppi
   (opinto-opas.xamk.fi). Ese host responde con un desafío anti-bot en JavaScript
   ("Tarkistetaan selainta": cookie calculada por JS + recarga) en TODAS las rutas, incluida /api/,
   y 403 en /robots.txt. El script lo detecta y NO lo elude: catálogo con estado "parcial" y sin filas.

Uso (desde la raíz del proyecto):
    python universidades/xamk/discover_xamk.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
UNIVERSIDAD = "South-Eastern Finland University of Applied Sciences (Xamk)"
SLUG = "xamk"
SITEMAPS = ["https://www.xamk.fi/sitemap-education.xml", "https://www.xamk.fi/sitemap-education-en.xml"]
STUDY_GUIDE_HOST = "https://opinto-opas.xamk.fi"
# Orden de preferencia: konetekniikka (objetivo) y, si no existe, la titulación más cercana.
MECH = re.compile(r"konetekniikka|mechanical-engineering", re.I)
FALLBACK = re.compile(r"/koulutukset/insinoori-amk-energiatekniikka/?$")
CHALLENGE = re.compile(r"Tarkistetaan selainta|document\.cookie\s*=", re.I)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def sitemap_urls(http: PoliteClient) -> list[str]:
    urls: list[str] = []
    for sm in SITEMAPS:
        urls += re.findall(r"<loc>([^<]+)</loc>", http.get_text(sm))
    return urls


def parse_programme(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    title = norm(soup.find("h1").get_text())
    text = norm(soup.get_text(" "))
    m = re.search(r"laajuus\s+on\s+(\d+)\s+opintopistett", text, re.I)
    ects = float(m.group(1)) if m else None
    guides = []
    for a in soup.find_all("a", href=True):
        p = urlsplit(a["href"])
        if p.netloc == urlsplit(STUDY_GUIDE_HOST).netloc:
            clean = urlunsplit((p.scheme, p.netloc, p.path, "", ""))  # sin parámetros de seguimiento _ga/_gl
            if clean not in guides:
                guides.append(clean)
    return {"titulo": title, "ects": ects, "opinto_opas": guides}


def probe_study_guide(http: PoliteClient, urls: list[str]) -> list[tuple[str, str]]:
    """Comprueba (sin eludir nada) qué devuelve el opinto-opas. Devuelve [(url, veredicto)]."""
    out = []
    for u in [STUDY_GUIDE_HOST + "/robots.txt", STUDY_GUIDE_HOST + "/", STUDY_GUIDE_HOST + "/api/", *urls]:
        try:
            body = http.get_text(u)
            out.append((u, "desafío JS anti-bot" if CHALLENGE.search(body) else f"contenido ({len(body)} B)"))
        except FetchError as e:
            out.append((u, f"error: {e}"))
    return out


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    urls = sitemap_urls(http)
    mech = sorted({u for u in urls if MECH.search(u)})
    if mech:
        raise RuntimeError(f"Aparece una titulación de konetekniikka: {mech} — revisar la elección de grado")
    eng = sorted({u for u in urls if "/koulutukset/insinoori-amk-" in u})
    plan_url = next(u for u in urls if FALLBACK.search(u))
    prog = parse_programme(http.get_text(plan_url))
    if prog["ects"] != 240:
        raise RuntimeError(f"ECTS inesperados en {plan_url}: {prog['ects']}")
    if not prog["opinto_opas"]:
        raise RuntimeError("La ficha no enlaza el opinto-opas")

    verdicts = probe_study_guide(http, prog["opinto_opas"])
    blocked = all(v != "" and not v.startswith("contenido") for _, v in verdicts)
    if not blocked:
        raise RuntimeError(f"El opinto-opas ya no está bloqueado: {verdicts} — rehacer la Fase 1 con su API")

    nombre_grado = f"{prog['titulo']} (Bachelor of Engineering, Energy Technology)"
    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=nombre_grado,
        curso_academico="2026-2027",
        url_plan_estudios=plan_url,
        ects_totales_plan=prog["ects"],
        estrategia_fuente=("Ficha del programa en www.xamk.fi (WordPress, sitemap-education*.xml). Los planes y "
                           "guías docentes solo existen en el opinto-opas de Peppi (opinto-opas.xamk.fi, SPA con "
                           "API JSON), protegido por un desafío JavaScript anti-bot: no accesible sin eludirlo."),
        generado_por="discover_xamk.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="parcial",
        notas=("Xamk no oferta Insinööri (AMK) konetekniikka: no figura en el sitemap de programas "
               f"({len(eng)} ingenierías AMK en FI) y /koulutukset/insinoori-amk-konetekniikka/ da 404. "
               "Se elige la más cercana de 240 op: Insinööri (AMK) energiatekniikka (base de konetekniikka, "
               "kunnossapito, prosessitekniikka). Enlaces del plan en el opinto-opas: "
               + ", ".join(prog["opinto_opas"]) + ". Verificación del opinto-opas: "
               + "; ".join(f"{u} -> {v}" for u, v in verdicts)
               + ". Stop rule: no se eluden filtros anti-bot, sin filas de asignaturas y sin Fase 2."),
    )
    catalog = Catalog(meta=meta, asignaturas=[])
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{nombre_grado}: estado=parcial, 0 asignaturas, plan {prog['ects']:g} op -> {out}")
    for u, v in verdicts:
        print(f"  {u}: {v}")
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
