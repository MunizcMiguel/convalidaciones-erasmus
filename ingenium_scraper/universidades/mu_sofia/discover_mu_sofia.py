"""Fase 1 (Descubrimiento) - Medical University of Sofia (MU-Sofia, Bulgaria).

Resultado esperado: estado "n/a". MU-Sofia es una universidad de ciencias de la salud;
este script demuestra, a partir de las fuentes oficiales, que no imparte ningun grado
de primer ciclo de ingenieria/tecnologia y deja la evidencia en el catalogo.

Fuentes oficiales (todas via PoliteClient, cacheadas en raw_cache/):
  1. Paginas "Специалности" (especialidades) de cada facultad/colegio/filial, en bulgaro:
     https://mu-sofia.bg/obuchenie/specialnosti/<unidad>/   (enlazadas entre si en el menu)
  2. "Приложение 1. Акредитирани професионални направления и специалности ..." (PDF de
     acreditacion de programas, enlazado desde /nauka/akreditacii/progr-akreditacia/):
     lista oficial de los campos profesionales (clasificador bulgaro de 2002: 5.x =
     Ciencias tecnicas / ingenieria, 7.x = Salud y deporte) acreditados a la universidad.

Criterio: hay grado de ingenieria si (a) algun campo profesional acreditado es 5.x, o
(b) algun nombre de especialidad contiene un termino de ingenieria/tecnologia medica.

Uso (desde la raiz del proyecto):  python universidades/mu_sofia/discover_mu_sofia.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pdfplumber  # noqa: E402
from bs4 import BeautifulSoup  # noqa: E402

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
UNIVERSIDAD = "Medical University of Sofia (MU-Sofia)"
SLUG = "mu_sofia"
URL_INDICE = "https://mu-sofia.bg/obuchenie/specialnosti/fakultet-medicina/"
URL_ACREDITACION = "https://mu-sofia.bg/nauka/akreditacii/progr-akreditacia/"

# Campo profesional bulgaro 5.x = "Технически науки" (ingenieria). Terminos que delatarian
# un grado de ingenieria / tecnologia medica en el nombre de una especialidad.
RE_INGENIERIA = re.compile(r"ИНЖЕНЕР|БИОМЕДИЦИНСК|МЕДИЦИНСКА ТЕХНИКА|ТЕХНИКА|ЕЛЕКТРОН|МЕХАТРОН", re.I)
RE_ESPECIALIDAD = re.compile(r"^СПЕЦИАЛНОСТ\s*[„\"“]\s*(.+?)\s*[”\"“]\s*(?:[-–]?\s*(.*))?$", re.I)
# Medicina / Dental: cabecera sin comillas, "СПЕЦИАЛНОСТ МЕДИЦИНА - ОБРАЗОВАТЕЛНО-..." o "ФАКУЛТЕТ ДЕНТАЛНА МЕДИЦИНА - ..."
RE_ESPECIALIDAD_SC = re.compile(r"^(?:СПЕЦИАЛНОСТ|ФАКУЛТЕТ)\s+([^„\"“]+?)\s*[-–]\s*(ОБРАЗОВАТЕЛНО.*)$", re.I)
RE_GRADO = re.compile(r"СТЕПЕН\s*[„\"“]\s*([^”\"“]+?)\s*[”\"“]", re.I)
RE_CAMPO = re.compile(r"^(\d\.\d)\.\s+(.+?)(?:\s+\d{2}\.\d{2}\.\d{4}.*)?$")


def soup_main(html: str) -> BeautifulSoup:
    s = BeautifulSoup(html, "lxml")
    for x in s(["script", "style", "nav", "header", "footer"]):
        x.decompose()
    return s.find("main") or s.find("article") or s.body


def unidades(http: PoliteClient) -> list[str]:
    """URLs de las paginas de especialidades de cada unidad, tomadas del menu de la pagina indice."""
    s = BeautifulSoup(http.get_text(URL_INDICE), "lxml")
    urls: list[str] = []
    for a in s.find_all("a", href=True):
        url = urljoin(URL_INDICE, a["href"])
        if re.fullmatch(r"https://mu-sofia\.bg/obuchenie/specialnosti/[^/]+/", url) and url not in urls:
            urls.append(url)
    if len(urls) < 5:
        raise RuntimeError(f"Menu de especialidades inesperado: {urls}")
    return urls


def especialidades(http: PoliteClient, url: str) -> list[dict]:
    html = http.get_text(url)
    titulo = BeautifulSoup(html, "lxml").title.get_text(strip=True)
    unidad = re.split(r"\s+[-–]\s+Медицински Университет", titulo)[0].strip()  # "<Unidad> - Медицински Университет София"
    lineas = [l.strip() for l in soup_main(html).get_text("\n").splitlines() if l.strip()]
    texto = " ".join(lineas)
    # El Colegio Medico solo da "Professional Bachelor" (3 anos), dicho en la introduccion.
    grado_unidad = "професионален бакалавър" if re.search(r"професионален\s+бакалавър", texto, re.I) else None
    out = []
    for i, l in enumerate(lineas):
        m = RE_ESPECIALIDAD.match(l) or RE_ESPECIALIDAD_SC.match(l)
        if not m:
            continue
        resto = (m.group(2) or "") + " " + (lineas[i + 1] if i + 1 < len(lineas) else "")
        g = RE_GRADO.search(l) or RE_GRADO.search(resto)
        grado = g.group(1).lower() if g else grado_unidad
        out.append({"unidad": unidad, "especialidad": m.group(1), "grado": grado, "url": url,
                    "ingenieria": bool(RE_INGENIERIA.search(m.group(1)))})
    return out


def campos_acreditados(http: PoliteClient) -> tuple[str, list[dict]]:
    s = BeautifulSoup(http.get_text(URL_ACREDITACION), "lxml")
    pdf_url = next(urljoin(URL_ACREDITACION, a["href"]) for a in s.find_all("a", href=True)
                   if a["href"].lower().endswith(".pdf") and "Акредитирани професионални направления" in a.get_text())
    campos: dict[str, list[str]] = {}
    with pdfplumber.open(http.get_file(pdf_url)) as pdf:
        for pg in pdf.pages:
            for l in (pg.extract_text() or "").splitlines():
                m = RE_CAMPO.match(l.strip())
                if m:
                    # el nombre del campo comparte linea con el de la especialidad; nos quedamos con
                    # la variante mas corta tras cortar en " - " (p. ej. "7.5. Здравни грижи")
                    campos.setdefault(m.group(1), []).append(re.split(r"\s+[-–]\s*|\s+\d", m.group(2))[0].strip())
    if not campos:
        raise RuntimeError("No se encontraron campos profesionales en el PDF de acreditacion")
    return pdf_url, [{"codigo": c, "nombre": min(ns, key=len)} for c, ns in sorted(campos.items())]


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")
    esp = [e for u in unidades(http) for e in especialidades(http, u)]
    pdf_url, campos = campos_acreditados(http)

    campos_ing = [c for c in campos if c["codigo"].startswith("5.")]
    esp_ing = [e for e in esp if e["ingenieria"]]
    hay_ingenieria = bool(campos_ing or esp_ing)
    primer_ciclo = [e for e in esp if e["grado"] and "бакалавър" in e["grado"]]

    hoy = time.localtime()
    y = hoy.tm_year if hoy.tm_mon >= 9 else hoy.tm_year - 1
    lista = "; ".join(f"{e['especialidad']} [{e['grado'] or '?'}] ({e['unidad']})" for e in esp)
    notas = (
        ("Se detectaron posibles grados de ingenieria: " + json.dumps(campos_ing + esp_ing, ensure_ascii=False)
         + " -> revisar manualmente." if hay_ingenieria else
         "n/a: MU-Sofia no ofrece ningun grado de ingenieria/tecnologia. Los campos profesionales acreditados "
         f"(PDF oficial de acreditacion) son solo {', '.join(c['codigo'] + ' ' + c['nombre'] for c in campos)} "
         "(area 7 'Salud y deporte'); ninguno es 5.x 'Ciencias tecnicas'. Ninguna de las "
         f"{len(esp)} especialidades publicadas ({len(primer_ciclo)} de primer ciclo: bakalavar o professional "
         "bakalavar) contiene terminos de ingenieria. Las mas 'tecnicas' (Rentgenov laborant, Zabotehnik, "
         "Meditsinski laborant del Colegio Medico) son grados profesionales sanitarios (campo 7.5), no de "
         "ingenieria. ")
        + f"Especialidades: {lista}. Fuentes: {URL_INDICE} (+ paginas hermanas) y {pdf_url}"
    )

    catalog = Catalog(
        meta=CatalogMeta(
            universidad=UNIVERSIDAD, slug=SLUG,
            nombre_grado="(ninguno: sin grado de ingenieria)" if not hay_ingenieria else "(revisar)",
            curso_academico=f"{y}-{(y + 1) % 100:02d}", url_plan_estudios=URL_INDICE,
            ects_totales_plan=None,
            estrategia_fuente="HTML estatico (paginas oficiales de especialidades por facultad, bulgaro) + PDF "
                              "oficial de campos profesionales acreditados",
            generado_por="discover_mu_sofia.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
            estado="parcial" if hay_ingenieria else "n/a", notas=notas,
        ),
        asignaturas=[],
    )
    (HERE / "catalogo_urls.json").write_text(
        json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    (HERE / "evidencia_programas.json").write_text(json.dumps(
        {"campos_profesionales_acreditados": campos, "pdf_acreditacion": pdf_url, "especialidades": esp},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(esp)} especialidades, campos {[c['codigo'] for c in campos]}, ingenieria={hay_ingenieria} "
          f"-> estado {catalog.meta.estado}. HTTP {http.stats}")


if __name__ == "__main__":
    main()
