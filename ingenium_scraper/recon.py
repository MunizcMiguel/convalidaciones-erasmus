#!/usr/bin/env python3
"""Fase 0 · Reconocimiento automático (sin LLM).

Para cada universidad comprueba, con el mismo cliente que usarán los scrapers,
si su web principal admite acceso automatizado: robots.txt, respuesta de la
portada y señales de filtro antibots. Sirve para no gastar un agente en una
universidad que va a acabar bloqueada.

    python recon.py --grupo es          # escribe reports/recon.json y reports/recon.md

Solo mira el dominio principal. Las guías pueden vivir en otro host (una
plataforma de catálogo, un proxy de PDF): esa comprobación sigue siendo
obligatoria para el agente de la Fase 1 (regla de parada del brief).
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

from common.http_client import FetchError, PoliteClient
from common.util import ROOT, universities

CHALLENGE = re.compile(r"just a moment|cf-chl|checking your browser|enable javascript and cookies|captcha|incapsula|akamai", re.I)


def probe(u: dict) -> dict:
    web = (u.get("web") or f"https://www.{u['domain']}").replace("http://", "https://")  # el RUCT aún lista http://
    http = PoliteClient(ROOT / "reports" / "recon_cache" / u["slug"], max_retries=1, timeout=25)
    r = {"slug": u["slug"], "name": u["name"], "web": web, "robots": "?", "portada": "?", "veredicto": "?"}
    try:
        allowed = http._allowed(web)
        r["robots"] = "permite" if allowed else "prohíbe"
        if not allowed:
            r["veredicto"] = "bloqueada (robots.txt)"
            return r
        html = http.get_text(web, force=True)
        r["portada"] = f"200 ({len(html) // 1000} kB)"
        if CHALLENGE.search(html[:6000]) and len(html) < 20000:
            r["veredicto"] = "sospecha de filtro antibots"
        else:
            r["veredicto"] = "accesible"
    except FetchError as e:
        r["portada"] = str(e)[:60]
        r["veredicto"] = "bloqueada (403/filtro)" if "403" in str(e) else "error de acceso"
    except Exception as e:  # noqa: BLE001 — el reconocimiento no debe abortar por una universidad
        r["portada"] = type(e).__name__
        r["veredicto"] = "error de acceso"
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--grupo", default="es")
    a = ap.parse_args()
    unis = universities(a.grupo)
    with ThreadPoolExecutor(max_workers=12) as ex:  # hosts distintos: una petición o dos a cada uno
        res = list(ex.map(probe, unis))
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    (out / "recon.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = [f"# Reconocimiento de acceso · grupo {a.grupo}", "", f"Generado: {time.strftime('%Y-%m-%d %H:%M')}", "",
             "| Universidad | Web | robots.txt | Portada | Veredicto |", "|---|---|---|---|---|"]
    lines += [f"| {r['name']} (`{r['slug']}`) | {r['web']} | {r['robots']} | {r['portada']} | {r['veredicto']} |" for r in res]
    (out / "recon.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    from collections import Counter
    print(dict(Counter(r["veredicto"] for r in res)))
    for r in res:
        if r["veredicto"] != "accesible":
            print(f"  {r['slug']:<32} {r['veredicto']:<28} {r['portada']}")


if __name__ == "__main__":
    main()
