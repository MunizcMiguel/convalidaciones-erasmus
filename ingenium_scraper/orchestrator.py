#!/usr/bin/env python3
"""Orquestador del pipeline INGENIUM syllabi.

En ejecución NO hay ningún LLM en el bucle de las fases 1, 2 y 4: el orquestador
lanza scripts deterministas (uno por universidad, en paralelo) y deduce el estado
mirando los archivos del disco. El LLM solo interviene en la Fase 3 (API externa).

    python orchestrator.py status                         # regenera status_dashboard.md
    python orchestrator.py discover --unis uniovi his hka # Fase 1: discover_{slug}.py
    python orchestrator.py scrape --unis uniovi --sample 5# Fase 2: muestra piloto
    python orchestrator.py scrape --unis uniovi --all     # Fase 2: grado completo
    python orchestrator.py parse --unis uniovi --dry-run  # Fase 3: semantic_parser.py
    python orchestrator.py consolidate                    # Fase 4: SQLite + anomalías
    python orchestrator.py run --unis uniovi his hka      # 1 -> 2 (muestra) y se detiene

Contrato que debe cumplir cada universidad (universidades/{slug}/):
    discover_{slug}.py                 -> escribe catalogo_urls.json (common.schema.Catalog)
    scraper_{slug}.py --sample N|--all [--codes C1 C2]
                                       -> escribe raw_markdown/{codigo}.md con common.util.write_markdown
                                          y sale con código != 0 si alguna guía falla
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import ValidationError

from common.schema import Catalog
from common.util import ROOT, REQUIRED_BLOCKS, load_catalog, read_markdown, uni_dir, universities

DASHBOARD = ROOT / "status_dashboard.md"
PILOT_SAMPLE = 5


# ------------------------------------------------------------------ estado
def uni_state(u: dict) -> dict:
    """Estado de una universidad deducido solo del sistema de archivos."""
    slug, d = u["slug"], uni_dir(u["slug"])
    st = {"slug": slug, "name": u["name"], "country": u["country"], "grupos": "+".join(u["grupos"]), "degree": "", "n": 0, "ects": None,
          "f1": "pendiente", "f2": "pendiente", "f3": "pendiente", "md": 0, "md_ok": 0, "json": 0, "nota": u.get("note", "")}
    raw = load_catalog(slug)
    if raw is not None:
        try:
            cat = Catalog.model_validate(raw)
            st["degree"], st["n"] = cat.meta.nombre_grado, len(cat.asignaturas)
            st["expected"] = sum(1 for a in cat.asignaturas if a.url_guia_docente and a.tipo_fuente != "sin_guia")
            st["ects"] = sum(a.creditos_ects or 0 for a in cat.asignaturas)
            st["f1"] = {"ok": "hecho", "parcial": "parcial", "n/a": "N/A"}[cat.meta.estado]
            if cat.meta.notas:
                st["nota"] = cat.meta.notas
        except ValidationError as e:
            st["f1"], st["nota"] = "ERROR", f"catálogo inválido ({e.error_count()} errores)"
    mds = list((d / "raw_markdown").glob("*.md"))
    st["md"] = len(mds)
    st["md_ok"] = sum(1 for p in mds if all(read_markdown(p)[0].get("blocks_found", {}).get(b) for b in REQUIRED_BLOCKS))
    st["json"] = len(list((d / "structured_data").glob("*.json")))
    if st["f1"] == "N/A":
        st["f2"] = st["f3"] = "N/A"
        return st
    has_scraper = (d / f"scraper_{slug}.py").exists()
    exp = st.get("expected", st["n"])
    if exp and st["md"] >= exp:
        st["f2"] = "hecho"
    elif exp and st["md"] > PILOT_SAMPLE:
        st["f2"] = f"{st['md']}/{exp} guías"
    elif st["md"]:
        st["f2"] = f"muestra {st['md_ok']}/{st['md']} ok"
    elif has_scraper:
        st["f2"] = "scraper escrito"
    if st["md"] and st["json"] >= st["md"]:
        st["f3"] = "hecho"
    elif st["json"]:
        st["f3"] = f"{st['json']}/{st['md']} JSON"
    return st


def write_dashboard() -> list[dict]:
    states = [uni_state(u) for u in universities()]
    rows = ["# Panel de estado · INGENIUM syllabi", "", f"Actualizado: {time.strftime('%Y-%m-%d %H:%M')}", "",
            "| # | Universidad | Grupo | Titulación | Asignaturas | ECTS | F1 Catálogo | F2 Markdown | F3 JSON |",
            "|---|---|---|---|---|---|---|---|---|"]
    for i, s in enumerate(states, 1):
        ects = f"{s['ects']:g}" if s["ects"] is not None else "–"
        rows.append(f"| {i} | {s['name']} (`{s['slug']}`) | {s['grupos']} | {s['degree'] or '–'} | {s['n'] or '–'} | {ects} "
                    f"| {s['f1']} | {s['f2']} | {s['f3']} |")
    notes = [f"- **{s['slug']}**: {s['nota']}" for s in states if s["nota"]]
    if notes:
        rows += ["", "## Notas", ""] + notes
    rows += ["", "## Leyenda", "",
             "- **F1**: `catalogo_urls.json` generado y validado contra el esquema.",
             f"- **F2**: guías en `raw_markdown/` frente a las que tienen enlace en el catálogo. «muestra a/b ok» = b guías piloto, a de ellas con los bloques clave ({', '.join(REQUIRED_BLOCKS)}).",
             "- **F3**: JSON estructurado en `structured_data/` (API externa).",
             "- Anomalías detalladas: `reports/anomalias.md` (tras `python orchestrator.py consolidate`)."]
    DASHBOARD.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return states


# ------------------------------------------------------------------ ejecución
def run_script(slug: str, script: str, args: list[str]) -> tuple[str, int]:
    path = uni_dir(slug) / script
    if not path.exists():
        return slug, -1
    logdir = uni_dir(slug) / "logs"
    logdir.mkdir(exist_ok=True)
    log = logdir / f"{Path(script).stem}_{time.strftime('%Y%m%d_%H%M%S')}.log"
    with log.open("w", encoding="utf-8") as f:
        rc = subprocess.run([sys.executable, str(path), *args], cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode
    return slug, rc


def run_phase(slugs: list[str], script_tpl: str, args: list[str], label: str) -> bool:
    """Una universidad por hilo: son hosts distintos, así que el paralelismo no
    concentra peticiones en ningún servidor (cada script se limita a sí mismo)."""
    print(f"== {label}: {', '.join(slugs)}")
    ok = True
    with ThreadPoolExecutor(max_workers=max(1, len(slugs))) as ex:
        for slug, rc in ex.map(lambda s: run_script(s, script_tpl.format(slug=s), args), slugs):
            msg = "ok" if rc == 0 else ("falta el script" if rc == -1 else f"ERROR (código {rc}, ver logs/)")
            print(f"   {slug}: {msg}")
            ok &= rc == 0
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    all_slugs = [u["slug"] for u in universities()]
    pilots = [u["slug"] for u in universities() if u.get("pilot")]

    def add_unis(p):
        p.add_argument("--unis", nargs="*", default=pilots, choices=all_slugs, metavar="SLUG",
                       help=f"por defecto las piloto: {' '.join(pilots)}")

    sub.add_parser("status")
    add_unis(sub.add_parser("discover"))
    p = sub.add_parser("scrape"); add_unis(p)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--sample", type=int, default=PILOT_SAMPLE); g.add_argument("--all", action="store_true")
    p = sub.add_parser("parse"); add_unis(p)
    p.add_argument("--limit", type=int); p.add_argument("--dry-run", action="store_true")
    sub.add_parser("consolidate")
    add_unis(sub.add_parser("run"))
    a = ap.parse_args()

    rc = 0
    if a.cmd == "discover":
        rc = 0 if run_phase(a.unis, "discover_{slug}.py", [], "Fase 1 · descubrimiento") else 1
    elif a.cmd == "scrape":
        args = ["--all"] if a.all else ["--sample", str(a.sample)]
        rc = 0 if run_phase(a.unis, "scraper_{slug}.py", args, f"Fase 2 · scraping ({' '.join(args)})") else 1
    elif a.cmd == "parse":
        cmd = [sys.executable, str(ROOT / "semantic_parser.py"), "--unis", *a.unis]
        cmd += (["--limit", str(a.limit)] if a.limit else []) + (["--dry-run"] if a.dry_run else [])
        rc = subprocess.run(cmd, cwd=ROOT).returncode
    elif a.cmd == "consolidate":
        rc = subprocess.run([sys.executable, str(ROOT / "qa_master_db.py")], cwd=ROOT).returncode
    elif a.cmd == "run":
        # Se detiene tras la muestra piloto: el scraping completo y la Fase 3 (que cuesta dinero)
        # requieren una orden explícita.
        if run_phase(a.unis, "discover_{slug}.py", [], "Fase 1 · descubrimiento"):
            run_phase(a.unis, "scraper_{slug}.py", ["--sample", str(PILOT_SAMPLE)], "Fase 2 · muestra piloto")
        print("Siguiente paso manual: revisar status_dashboard.md y lanzar `scrape --all` y `parse`.")

    for s in write_dashboard():
        print(f"{s['slug']:<11} F1={s['f1']:<9} F2={s['f2']:<18} F3={s['f3']:<10} asignaturas={s['n']}")
    print(f"Panel: {DASHBOARD}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
