#!/usr/bin/env python3
"""Genera config/universities_es.json a partir del RUCT (Registro de Universidades,
Centros y Títulos del Ministerio): todas las universidades españolas con un
Grado en Ingeniería Mecánica en vigor, con sus créditos oficiales, centros y web.

    python config/discover_targets_es.py [--titulo "Ingeniería Mecánica"]

Es la fuente de verdad de "qué universidades hay que cubrir" y de los ECTS
oficiales contra los que se valida cada catálogo (ya no depende de un agente).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlencode, urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402

BASE = "https://www.educacion.gob.es"
ENC = "iso-8859-15"
OUT = Path(__file__).parent / "universities_es.json"
# El RUCT no publica la web de estas tres universidades; se indica aquí a mano.
WEB_FALLBACK = {"Universidad de Valladolid": "https://www.uva.es", "Universidad de Zaragoza": "https://www.unizar.es",
                "Universitat de Girona": "https://www.udg.edu"}


def slugify(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\b(universidad|universitat|universidade|de|del|la|les|el|d|i|y|euskal herriko unibertsitatea)\b", " ", s)
    return "es_" + re.sub(r"[^a-z0-9]+", "_", s).strip("_")[:28]


def field(text: str, label: str) -> str | None:
    m = re.search(re.escape(label) + r"\s*:?\s*\n\s*([^\n]+)", text)
    return m.group(1).strip() if m else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--titulo", default="Ingeniería Mecánica")
    a = ap.parse_args()
    http = PoliteClient(Path(__file__).parent / "raw_cache_ruct", min_delay=0.8, max_delay=1.6)

    # 1) listado paginado (la búsqueda necesita la sesión del formulario)
    form = http.get_text(f"{BASE}/ruct/consultaestudios?actual=estudios", encoding=ENC, force=True)
    action = BeautifulSoup(form, "lxml").find("form")["action"]
    data = {"consulta": "1", "codigoEstudio": "", "codigoUniversidad": "", "descripcionEstudio": a.titulo, "codigoTipo": "G",
            "codigoSubTipo": "", "codigoRama": "", "ambito": "", "codigoEstado": "", "situacion": "", "buscarHistorico": "N",
            "action:listaestudios": "Consultar"}
    html = http.get_text(BASE + action, encoding=ENC, method="POST", force=True, content=urlencode(data, encoding=ENC),
                         headers={"Content-Type": "application/x-www-form-urlencoded"})
    rows, seen_pages = [], set()
    while True:
        soup = BeautifulSoup(html, "lxml")
        for tr in soup.select("table tr"):
            tds = tr.find_all("td")
            link = tr.find("a", href=re.compile("estudio.action"))
            if len(tds) >= 5 and link:
                rows.append({"codigo_ruct": tds[0].get_text(strip=True), "titulo": tds[1].get_text(" ", strip=True),
                             "universidad": tds[2].get_text(" ", strip=True), "nivel": tds[3].get_text(" ", strip=True),
                             "estado": " ".join(tds[4].get_text(" ", strip=True).split()), "url": urljoin(BASE + "/ruct/", link["href"])})
        nxt = [x["href"] for x in soup.select(".pagelinks a") if re.search(r"d-\d+-p=(\d+)", x["href"])]
        nxt = [u for u in nxt if u not in seen_pages]
        if not nxt:
            break
        seen_pages.add(nxt[0])
        html = http.get_text(urljoin(BASE + "/ruct/", nxt[0]), encoding=ENC, force=True)
    rows = list({r["codigo_ruct"]: r for r in rows}.values())
    # solo el título exacto (descarta "Ingeniería Electromecánica", dobles grados, etc.)
    # admite sufijos oficiales: "(Rama Industrial)", "/ Bachelor in Mechanical Engineering", "por la Universidad ..."
    exact = re.compile(r"^Graduado o Graduada en " + re.escape(a.titulo) + r"\s*(?:\([^)]*\))?\s*(?:/[^/]*?)?\s*(?:por .*)?$", re.I)
    rows = [r for r in rows if exact.match(" ".join(r["titulo"].split()))]
    print(f"{len(rows)} títulos '{a.titulo}' en el RUCT")

    # 2) ficha de cada título: créditos oficiales, situación y centros
    unis: dict[str, dict] = {}
    for r in rows:
        page = http.get_text(r["url"], encoding=ENC)
        soup = BeautifulSoup(page, "lxml")
        text = soup.get_text("\n", strip=True)
        cred = {k: field(text, lab) for k, lab in [("basica", "Nº Créditos de Formación Básica"), ("obligatorios", "Nº Créditos Obligatorios"),
                                                   ("optativos", "Nº Créditos Optativos"), ("practicas", "Nº Créditos en Prácticas Externas"),
                                                   ("tfg", "Nº Créditos Trabajo Fin de Grado/Master"), ("total", "Créditos Totales")]}
        cred = {k: (float(v.replace(",", ".")) if v and re.fullmatch(r"[\d.,]+", v) else None) for k, v in cred.items()}
        centros, cod_uni = [], None
        for c in soup.find_all("a", href=re.compile("centro.action")):
            m = re.search(r"codigoUniversidad=(\d+)", c["href"])
            cod_uni = cod_uni or (m.group(1) if m else None)
            centros.append(c.get_text(" ", strip=True))
        extinguido = bool(re.search(r"extinguid|a extinguir|en extinci", text, re.I))
        u = unis.setdefault(r["universidad"], {"slug": slugify(r["universidad"]), "name": r["universidad"], "country": "ES", "lang": "es",
                                               "grupo": "es", "codigo_universidad_ruct": cod_uni, "domain": None, "titulos": []})
        u["codigo_universidad_ruct"] = u["codigo_universidad_ruct"] or cod_uni
        u["titulos"].append({"codigo_ruct": r["codigo_ruct"], "titulo": r["titulo"], "nivel": r["nivel"], "estado": r["estado"],
                             "en_extincion": extinguido, "creditos": cred, "centros": sorted(set(centros)), "url_ruct": r["url"]})

    # 3) web oficial de cada universidad
    for u in unis.values():
        if not u["codigo_universidad_ruct"]:
            u["web"] = WEB_FALLBACK.get(u["name"])
            u["domain"] = re.sub(r"^https?://(www\.)?", "", u["web"]).split("/")[0] if u["web"] else None
            continue
        page = http.get_text(f"{BASE}/ruct/universidad.action?codigoUniversidad={u['codigo_universidad_ruct']}&actual=universidades", encoding=ENC)
        soup = BeautifulSoup(page, "lxml")
        web = next((x["href"] for x in soup.find_all("a", href=re.compile(r"^https?://"))
                    if not re.search(r"gob\.es|boe\.es|administracion\.gob|europa\.eu|w3\.org", x["href"])), None)
        if not web:
            m = re.search(r"(?:www\.)[\w.-]+\.[a-z]{2,}", soup.get_text(" "))
            web = "https://" + m.group(0) if m else None
        web = web or WEB_FALLBACK.get(u["name"])
        u["web"] = web
        u["domain"] = re.sub(r"^https?://(www\.)?", "", web).split("/")[0] if web else None

    out = sorted(unis.values(), key=lambda x: x["name"])
    slugs = [u["slug"] for u in out]
    assert len(slugs) == len(set(slugs)), "slugs duplicados: " + str([s for s in slugs if slugs.count(s) > 1])
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(out)} universidades -> {OUT.name}; sin web: {[u['name'] for u in out if not u['domain']]}")
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
