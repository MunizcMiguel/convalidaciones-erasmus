"""Fase 1 - Aix-Marseille Universite - Licence Mecanique (3SMK). BLOQUEADO: catalogo de formaciones con robots.txt Disallow.
Uso: python universidades/ec_f_marseil84/discover_ec_f_marseil84.py
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common.http_client import PoliteClient, RobotsBlocked  # noqa: E402
from common.schema import Catalog, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_marseil84"
UNI = "Aix-Marseille Université"
GRADO = "Licence Mécanique (3SMK)"
URL_PLAN = "https://sciences.univ-amu.fr/fr/formation/licences/licence-mecanique"
CAT_URL = "https://formations.univ-amu.fr/fr/licence/3SMK"


def main() -> None:
    c = PoliteClient(cache_dir=HERE / "raw_cache")
    c.get_text(URL_PLAN)  # pagina de la facultad: permitida
    try:
        c.get_text(CAT_URL)
        verdict = "formations.univ-amu.fr PERMITE (revisar: el script esperaba bloqueo)"
    except RobotsBlocked:
        verdict = "formations.univ-amu.fr robots.txt NO permite (RobotsBlocked)"
    meta = CatalogMeta(
        universidad=UNI, slug=SLUG, nombre_grado=GRADO, curso_academico="2025-26", url_plan_estudios=URL_PLAN, ects_totales_plan=180.0,
        estrategia_fuente="Catálogo oficial formations.univ-amu.fr (UE por parcours) — inaccesible por robots.txt",
        generado_por="discover_ec_f_marseil84.py", generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"), estado="parcial",
        notas=("El Excel no da titulación Uniovi para Aix-Marseille (solo ISCED 0714 Electrónica/automática y 0715 Mecánica, 2 plazas), así que se toma la "
               "Licence Mécanique de la Faculté des Sciences (grado de 3 años, 180 ECTS; L1 común con Matemáticas/Física/Informática, un único parcours en L2-L3), "
               "la más afín a Ingeniería Mecánica/Industrial. PARCIAL SIN ASIGNATURAS: las UE y sus fichas viven en formations.univ-amu.fr, cuyo robots.txt "
               f"prohíbe el acceso ({verdict}); regla de parada, no se rodea. sciences.univ-amu.fr solo ofrece una ficha-resumen y una plaquette en PDF sin fichas de UE. "
               "Existen también Parcours Ingénierie mécanique (Licence SPI) en el mismo catálogo, igualmente bloqueado."))
    cat = Catalog(meta=meta, asignaturas=[])
    (HERE / "catalogo_urls.json").write_text(json.dumps(cat.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print("parcial vacío:", verdict)


if __name__ == "__main__":
    main()
