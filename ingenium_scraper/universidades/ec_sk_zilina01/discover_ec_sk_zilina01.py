"""Fase 1 (parcial) - University of Zilina (UNIZA), Faculty of Mechanical Engineering (SjF). Regla de parada.
Las fichas de asignatura y los planes por semestre se sirven desde vzdelavanie.uniza.sk, cuyo robots.txt tiene `Disallow: /` (verificado aqui con
PoliteClient). Este script solo registra ese veredicto y escribe un catalogo parcial vacio.
Uso: python universidades/ec_sk_zilina01/discover_ec_sk_zilina01.py
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
SLUG = "ec_sk_zilina01"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    veredictos = {}
    for host in ("https://vzdelavanie.uniza.sk", "https://www.uniza.sk", "https://fstroj.uniza.sk"):
        r = c._rules_for(host)
        veredictos[host] = "deny_all" if r.deny_all else ("Disallow: /" if not r.can_fetch(host + "/vzdelavanie/index.php") else "permite")
    try:
        c.get_text("https://vzdelavanie.uniza.sk/vzdelavanie/index.php?lang=en")
        bloqueo = "no bloqueado"
    except RobotsBlocked as e:
        bloqueo = str(e)
    meta = CatalogMeta(
        universidad="University of Zilina - Faculty of Mechanical Engineering", slug=SLUG, nombre_grado="Bachelor study, Faculty of Mechanical Engineering (programa concreto no determinado)",
        curso_academico="2026/2027", url_plan_estudios="https://www.uniza.sk/index.php/en/study/study-options/bachelor-study", ects_totales_plan=None,
        estrategia_fuente="Ninguna: fuente de fichas bloqueada por robots.txt", generado_por="discover_ec_sk_zilina01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=(f"Regla de parada. Veredictos de robots.txt: {veredictos}. Intento de acceso a la plataforma de fichas/planes: {bloqueo}. "
               "Los documentos 'Description of the study programme' de www.uniza.sk/doc1/OPIS-SPRAVA/EN/{id}_OpisStudijnehoProgramu_EN.htm (permitidos) que se probaron (ids 188, 323, 326) son programas de doctorado de la SjF, no el grado. "
               "Por la información de las hojas informativas de la SjF (PDF fstroj.uniza.sk/images/pdf/akreditacia/SjF-BC-2025-2026-eng.pdf, solo vista en búsqueda, no descargada) los grados de la facultad son tipo "
               "Mechanical Engineering Technologies / Computer Design and Simulation, sin verificar. No se identificó el grado ni su plan: catálogo vacío, sin Fase 2."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(veredictos, bloqueo)


if __name__ == "__main__":
    main()
