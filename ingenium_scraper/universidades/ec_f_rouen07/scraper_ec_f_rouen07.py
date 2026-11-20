"""Fase 2 - ESIGELEC MTech EES: cada modulo del Course Outline (PDF compartido) -> Markdown.
Uso: python universidades/ec_f_rouen07/scraper_ec_f_rouen07.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).parent))
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402
import discover_ec_f_rouen07 as disc  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_rouen07"
SAMPLE = ["MSTSI14", "MSTEE11", "MSTSEE22", "MSTSEE36", "MSTPRDP", "MSTCCAWT", "MSTPM"]
HEADS = {"objectives": "Objectives", "list of topics": "Topics", "prerequisites": "Prerequisites", "pre-requisites": "Prerequisites",
         "assessment": "Assessment", "evaluation": "Assessment", "bibliography": "Bibliography", "references": "Bibliography",
         "teaching methods": "Teaching methods", "learning outcomes": "Learning outcomes", "content": "Content"}


def to_markdown(m: dict) -> tuple[str, dict]:
    md = [f"# {m['title']}", "", f"Module code: {m['code']}", f"Duration: {m['hours']:g} h", ""]
    cur = None
    body, n_obj = [], 0
    for l in m["body"]:
        if re.match(r"\s*Objectives\s*:?\s*$", l, re.I):
            n_obj += 1
            if n_obj == 2:  # empieza otro modulo sin 'Module Code' (idiomas): se descarta
                while body and (not body[-1].strip().startswith(("•", "")) and len(body[-1].strip()) < 70):
                    body.pop()
                break
        if "Module Code" in l:  # modulo no listado (idiomas) pegado al final: se descarta junto a su titulo
            if body:
                body.pop()
            break
        body.append(l)
    for l in body:
        s = l.strip()
        if not s or re.fullmatch(r"\d+", s) or re.match(r"(ESIGELEC$|Technop|Avenue Galil|76801|Phone:|www\.esigelec)", s):
            continue
        key = s.rstrip(":").lower()
        if key in HEADS:
            cur = HEADS[key]
            md += ["", f"## {cur}", ""]
            continue
        if s.startswith(("•", "")):
            md.append("- " + s.lstrip("• ").strip())
        elif md[-1].startswith("- ") and s[:1].islower():
            md[-1] += " " + s
        else:
            md.append(s)
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(h):
        r = re.search(rf"## {h}\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(r and r.group(1).strip())
    found = {"contents": has("Topics") or has("Content"), "learning_outcomes": has("Objectives") or has("Learning outcomes"),
             "assessment": has("Assessment"), "bibliography": has("Bibliography"), "prerequisites": has("Prerequisites")}
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
    mods = {m["code"]: m for m in reversed(disc.modules(disc.get_pages(client)))}
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia" or c not in mods:
            print(f"SKIP {c}"); continue
        try:
            md, found = to_markdown(mods[c])
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} chars {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1; print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
