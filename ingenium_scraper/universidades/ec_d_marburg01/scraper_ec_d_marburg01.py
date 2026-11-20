"""Fase 2 - Marburg B.Sc. Informatik: pagina HTML por modulo del Online-Modulhandbuch -> Markdown.
Uso: python universidades/ec_d_marburg01/scraper_ec_d_marburg01.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bs4 import BeautifulSoup  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_d_marburg01"
SAMPLE = ["CS210", "CS110", "CS130", "CS160", "CS180"]
SECTION = {"Inhalt": "Inhalt (Contents)", "Qualifikationsziele": "Qualifikationsziele (Learning outcomes)", "Voraussetzungen": "Voraussetzungen (Prerequisites)",
           "Verwendbarkeit": "Verwendbarkeit", "Literatur": "Literatur (Bibliography)"}
META = {"Niveaustufe, Verpflichtungsgrad": "Niveau/Verpflichtungsgrad", "Lehr- und Lernformen,\nArbeitsaufwand": "Lehrformen / Arbeitsaufwand",
        "Leistungspunkte,\nVoraussetzungen zum Erwerb": "Leistungspunkte / Voraussetzungen zum Erwerb (Assessment)", "Sprache,\nBenotung": "Sprache / Benotung",
        "Dauer des Moduls,\nHäufigkeit": "Dauer / Häufigkeit"}


def to_markdown(entry: dict, html: str) -> tuple[str, dict]:
    s = BeautifulSoup(html, "lxml")
    root = s.find("section", class_="content") or s.find("main") or s.body
    for z in root(["script", "style", "nav", "form"]):
        z.decompose()
    lines = [re.sub(r"\s+", " ", l).strip() for l in root.get_text("\n", strip=True).split("\n")]
    lines = [l for l in lines if l]
    try:
        i0 = lines.index("Hauptinhalt") + 1
    except ValueError:
        i0 = 0
    end = next((i for i, l in enumerate(lines) if l.startswith("Bitte beachten Sie")), len(lines))
    body = lines[i0:end]
    title = body[0] if body else entry["nombre_asignatura"]
    # etiquetas compuestas (dos lineas separadas por coma)
    joined, i = [], 1
    while i < len(body):
        l = body[i]
        if l.endswith(",") and i + 1 < len(body) and (l + "\n" + body[i + 1]) in META:
            joined.append(l + "\n" + body[i + 1]); i += 2; continue
        joined.append(l); i += 1
    md = [f"# {entry['nombre_asignatura']}", "", f"Modul: {title}", ""]
    cur, buf, drop = None, [], False
    def flush():
        nonlocal buf, cur
        if cur and buf:
            md.extend(["", f"## {cur}", "", "\n".join(buf)])
        buf = []
    for l in joined:
        if l in META or l in SECTION or l.startswith("Modulverantwortliche"):
            flush()
            if l.startswith("Modulverantwortliche"):
                cur, drop = None, True
                continue
            drop = False
            cur = META.get(l) or SECTION[l]
            continue
        if drop or cur is None:
            continue
        buf.append(("- " + l) if cur in ("Qualifikationsziele (Learning outcomes)", "Inhalt (Contents)") and not l.endswith(":") and len(l) > 3 and False else l)
    flush()
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(h):
        r = re.search(rf"## {re.escape(h)}.*?\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(r and r.group(1).strip() and not re.match(r"keine\.?$", r.group(1).strip(), re.I))
    found = {"contents": has("Inhalt"), "learning_outcomes": has("Qualifikationsziele"), "assessment": has("Leistungspunkte"),
             "bibliography": has("Literatur"), "prerequisites": has("Voraussetzungen (Prerequisites)")}
    return out, found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=5)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--codes", nargs="+")
    a = ap.parse_args()
    cat = load_catalog(SLUG)
    rows = {r["codigo_asignatura"]: r for r in cat["asignaturas"]}
    codes = a.codes or (list(rows) if a.all else [c for c in SAMPLE if c in rows][: a.sample])
    client = PoliteClient(cache_dir=HERE / "raw_cache")
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia":
            print(f"SKIP {c}"); continue
        try:
            md, found = to_markdown(r, client.get_text(r["url_guia_docente"]))
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} chars {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1; print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
