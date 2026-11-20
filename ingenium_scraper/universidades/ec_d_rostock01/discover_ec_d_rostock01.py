"""Fase 1 - Universitaet Rostock - Bachelor Maschinenbau (B.Sc.). BLOQUEADO: la Moduldatenbank (pruefung.uni-rostock.de) tiene robots.txt Disallow.
Uso: python universidades/ec_d_rostock01/discover_ec_d_rostock01.py
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_rostock01"
UNI = "Universität Rostock"
GRADO = "Maschinenbau (B.Sc.)"
URL_PLAN = "https://www.msf.uni-rostock.de/studium/bachelorstudiengaenge/maschinenbau/"
CAT_URL = "https://pruefung.uni-rostock.de/qisserver/rds?state=change&type=3&moduleParameter=studiengaenge&nextdir=change"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    c.get_text(URL_PLAN)  # pagina de la facultad: permitida
    try:
        c.get_text(CAT_URL)
        verdict = "pruefung.uni-rostock.de PERMITE (revisar: el script esperaba bloqueo)"
    except RobotsBlocked:
        verdict = "pruefung.uni-rostock.de robots.txt NO permite (RobotsBlocked)"
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="Moduldatenbank (QIS/HISinOne, pruefung.uni-rostock.de) — inaccesible por robots.txt",
        generado_por="discover_ec_d_rostock01.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("Excel: Informática en TI (4 plazas), Tecnologías Industriales, Dobles Grados y Másteres (Industrial, Informática). Por la prioridad Mecánica/Industrial se toma el "
               "Bachelor Maschinenbau (B.Sc., 6 semestres, 180 LP) de la Facultad MSF, la titulación más afín a Tecnologías Industriales/Ingeniería Industrial. PARCIAL SIN ASIGNATURAS: "
               "las fichas de módulo viven solo en la Moduldatenbank (QIS, pruefung.uni-rostock.de) y "
               f"su robots.txt prohíbe el acceso ({verdict}); regla de parada, no se rodea. En www.msf.uni-rostock.de solo hay el Studien- und Prüfungsplan (SPSO 2023, "
               "PDF con un diagrama de nombres de módulo sin LP por módulo) y las Prüfungsordnungen; no son guías docentes. Los PDFs antiguos de Modulbeschreibungen (Technische Mechanik 1/2, 2013) "
               "están obsoletos y no se usan. Informática no se exploró (el catálogo sería el mismo bloqueado)."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("parcial vacío:", verdict)


if __name__ == "__main__":
    main()
