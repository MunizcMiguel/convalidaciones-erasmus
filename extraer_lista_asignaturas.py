#!/usr/bin/env python3
import json
import re
import unicodedata
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.uniovi.es"
URL = "https://www.uniovi.es/estudia/grados/ingenieria/mecanica"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}


def normalizar(txt: str) -> str:
    txt = unicodedata.normalize("NFKD", txt)
    txt = "".join(c for c in txt if not unicodedata.combining(c))
    txt = txt.lower().strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt


def detectar_semestre(texto: str) -> Optional[int]:
    t = normalizar(texto)
    if "primer semestre" in t or "1er semestre" in t or "1º semestre" in t:
        return 1
    if "segundo semestre" in t or "2º semestre" in t or "2do semestre" in t:
        return 2
    return None


def find_plan_panel(soup: BeautifulSoup) -> Tag:
    for link in soup.select("a.nav-link"):
        label = normalizar(link.get_text(" ", strip=True))
        if "plan" in label and "estudio" in label:
            href = link.get("href", "")
            if href.startswith("#"):
                panel = soup.select_one(href)
                if panel:
                    return panel

    panel = soup.select_one("div.tab-pane[id^='plan-de-estudios-']")
    if panel:
        return panel

    raise ValueError('No se encontró la pestaña "Plan de estudios".')


def extraer_plan_estudios(url: str = URL) -> List[Dict[str, Any]]:
    response = requests.get(url, headers=HEADERS, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    panel = find_plan_panel(soup)

    curso: Optional[str] = None
    semestre: Optional[int] = None
    resultados: List[Dict[str, Any]] = []

    for element in panel.descendants:
        if not getattr(element, "name", None):
            continue

        classes = element.get("class") or []

        if element.name == "div" and "curso" in classes and "h4" in classes:
            curso = element.get_text(" ", strip=True)
            continue

        if element.name == "div" and "temporalidad" in classes:
            semestre = detectar_semestre(element.get_text(" ", strip=True))
            continue

        if element.name != "tr":
            continue

        cells = element.find_all("td")
        if not cells:
            continue

        link_tag = element.find("a", href=True)
        if not link_tag or "/-/fof/asignatura/" not in link_tag["href"]:
            continue

        href = link_tag["href"]
        textos = [cell.get_text(" ", strip=True) for cell in cells]

        resultados.append({
            "curso": curso,
            "semestre": semestre,
            "asignatura": textos[0],
            "creditos": int(textos[1]) if len(textos) > 1 and textos[1].isdigit() else textos[1] if len(textos) > 1 else None,
            "caracter": textos[2] if len(textos) > 2 else None,
            "itinerario_bilingue": textos[3] if len(textos) > 3 else None,
            "codigo": href.rstrip("/").split("/")[-1],
            "link": urljoin(BASE_URL, href),
        })

    unicos: Dict[str, Dict[str, Any]] = {}
    for item in resultados:
        unicos[item["codigo"]] = item

    data = list(unicos.values())
    data.sort(key=lambda x: (
        x["curso"] or "",
        x["semestre"] if x["semestre"] is not None else 99,
        normalizar(x["asignatura"]),
    ))
    return data


if __name__ == "__main__":
    data = extraer_plan_estudios()

    print(json.dumps(data, ensure_ascii=False, indent=2))

    with open("gimeca_plan_estudios.json", "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
