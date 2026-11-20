"""Fase 1 (parcial, regla de parada) - Technische Universität Berlin - Maschinenbau (B.Sc.).

Sondea con PoliteClient los hosts implicados y deja un catalogo parcial vacio con el veredicto.
Uso: python universidades/ec_d_berlin02/discover_ec_d_berlin02.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_berlin02"
PROBES = {'www.tu.berlin robots.txt': 'https://www.tu.berlin/robots.txt', 'MOSES lista de modulos (studiengang=37)': 'https://moseskonto.tu-berlin.de/moses/modultransfersystem/studiengaenge/anzeigen.html?studiengang=37', 'MOSES ficha de modulo': 'https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/beschreibung/anzeigen.html?number=50166&version=3'}
NOTAS = "Titulación: Maschinenbau B.Sc. (StuPO 2017, 180 LP: 156 en módulos, 12 prácticas, 12 tesis). Las descripciones de módulo están en MOSES (moseskonto.tu-berlin.de/moses/modultransfersystem/...studiengang=37 y .../bolognamodule/beschreibung/anzeigen.html?number=..&version=..), pero ambas URLs devuelven solo la página 'Web Login Service - Loading Session Information' (handshake Shibboleth que requiere JavaScript/cookies); salvarlo implicaría un navegador automatizado, prohibido. www.tu.berlin permite el rastreo salvo parámetros (declara Content-Signal ai-train=no). La StuPO (PDF en static.tu.berlin, Maschinenbau_B.Sc._2017.pdf) tiene un anexo con la lista de módulos pero no se analizó. Sin Fase 2."


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    verdict = {}
    for name, url in PROBES.items():
        try:
            t = c.get_text(url)
            verdict[name] = "responde (%d bytes)" % len(t)
            if "Loading Session Information" in t or "Web Login Service" in t:
                verdict[name] += " pero es un arranque de sesion SSO con JavaScript (sin contenido)"
        except RobotsBlocked:
            verdict[name] = "robots.txt no permite"
        except Exception as e:  # noqa: BLE001
            verdict[name] = "error: " + type(e).__name__
    print(verdict)
    meta = CatalogMeta(
        universidad="Technische Universität Berlin", slug=SLUG, nombre_grado="Maschinenbau (B.Sc.)", curso_academico="2025/26",
        url_plan_estudios="https://www.tu.berlin/en/studying/study-programs/all-programs-offered/study-course/mechanical-engineering-b-sc", ects_totales_plan=180.0,
        estrategia_fuente="Sin extraccion (regla de parada): las fichas viven en MOSES (moseskonto.tu-berlin.de), que exige un arranque de sesion SSO con JavaScript",
        generado_por="discover_ec_d_berlin02.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=NOTAS + " Sondeo del %s: " % time.strftime("%Y-%m-%d") + "; ".join(f"{k}: {v}" for k, v in verdict.items()))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
