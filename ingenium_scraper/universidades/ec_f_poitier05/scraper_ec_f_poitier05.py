"""Fase 2 - ISAE-ENSMA FISE A2: cada ficha ECUE del syllabus (PDF compartido) -> Markdown (FR + EN).
Uso: python universidades/ec_f_poitier05/scraper_ec_f_poitier05.py [--sample N | --all | --codes C1 C2]
"""
from __future__ import annotations
import argparse, io, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pypdf  # noqa: E402
from common.http_client import PoliteClient  # noqa: E402
from common.util import load_catalog, write_markdown  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_f_poitier05"
SAMPLE = ["CSN", "AER", "SDM", "ANG", "MPR", "PID", "VIB", "CAO", "CS1"]
SEC = [("Compétences attendues", "Learning outcomes (Compétences attendues)", "learning_outcomes"),
       ("Expected competencies", "Learning outcomes (EN)", None),
       ("Pré-requis", "Prerequisites (Pré-requis)", "prerequisites"), ("Prerequisites", "Prerequisites (EN)", None),
       ("Contenu", "Content (Contenu)", "contents"), ("Content", "Content (EN)", None),
       ("Bibliographie", "Bibliography (Bibliographie)", "bibliography"), ("Bibliography", "Bibliography (EN)", None)]
LAB = re.compile(r"^(Comp[ée]tences attendues|Expected competencies|Pr[ée]-?requis|Prerequisites|Contenu|Content|Bibliographie|Bibliography)\s*:\s*(.*)$", re.I)


def to_markdown(entry: dict, text: str) -> tuple[str, dict]:
    import unicodedata
    lines = [l.rstrip() for l in unicodedata.normalize("NFC", text).split("\n")]
    # cabecera: valores utiles (evaluacion, idioma, tipo); se descarta departamento, coordinadores, periodo, horas
    head_end = next((i for i, l in enumerate(lines) if LAB.match(l.strip())), len(lines))
    head = "\n".join(lines[:head_end])
    vals = [re.sub(r"\s+", " ", v).strip() for v in re.split(r"(?m)^\s*:\s?", head)[1:]]
    vals = [v for v in vals if v and not re.match(r"^\d+h\d+$", v)]
    evm = langm = typm = None
    li = None
    for k_, v_ in enumerate(vals):
        if re.match(r'(Fran.{1,3}ais|Anglais|English|French)', v_):
            li = k_
            break
    print('DBG', li, len(vals)) if False else None
    if li is not None and li >= 1:
        evm, langm = vals[li - 1], vals[li]
        typm = vals[li + 1] if li + 1 < len(vals) else None
        if re.match(r"\d+\S* (ann|ye)", evm):  # no hay campo de evaluacion en la ficha
            evm = None
    body_lines = lines[head_end:]
    body_lines = [l for l in body_lines if not re.match(r"^\s*\d+\s*$", l)]
    md = [f"# {entry['nombre_asignatura']}", "", f"UE: {entry['curso_semestre']}"]
    if evm:
        md.append("Assessment (Evaluation): " + evm)
    if langm:
        md.append("Language of instruction: " + langm)
    if typm:
        md.append("Type: " + typm)
    md.append("")
    cur = None
    for l in body_lines:
        s = l.strip()
        m = LAB.match(s)
        if m:
            key = m.group(1).lower()
            title = next(t for k, t, _ in SEC if k.lower() == ("pré-requis" if key.startswith("pr") and "requis" in key else key)) if any(k.lower() == key for k, _, _ in SEC) else m.group(1)
            if key.startswith("pr") and "requis" in key:
                title = "Prerequisites (Pré-requis)"
            md += ["", f"## {title}", ""]
            if m.group(2):
                md.append(m.group(2))
            cur = title
            continue
        if not s:
            md.append("")
            continue
        md.append(("- " + s.lstrip("•o ").strip()) if s[0] in "•" else s)
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n"
    def has(t):
        m = re.search(rf"## {re.escape(t)}\n\n(.*?)(?=\n## |\Z)", out, re.S)
        return bool(m and m.group(1).strip() and not re.match(r"(aucune?|none|néant)\.?$", m.group(1).strip(), re.I))
    found = {"contents": has("Content (Contenu)") or has("Content (EN)"),
             "learning_outcomes": has("Learning outcomes (Compétences attendues)") or has("Learning outcomes (EN)"),
             "assessment": bool(evm), "bibliography": has("Bibliography (Bibliographie)") or has("Bibliography (EN)"),
             "prerequisites": has("Prerequisites (Pré-requis)") or has("Prerequisites (EN)")}
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
    pdf = None
    fails = 0
    for c in codes:
        r = rows.get(c)
        if not r or r["tipo_fuente"] == "sin_guia":
            print(f"SKIP {c}"); continue
        try:
            if pdf is None:
                pdf = [p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(client.get_bytes(r["url_guia_docente"]))).pages]
            ini, fin = map(int, r["paginas_pdf"].split("-"))
            md, found = to_markdown(r, "\n".join(pdf[ini - 1:fin]))
            # quita el titulo repetido y la linea 'Code ECUE...' de la cabecera
            write_markdown(SLUG, r, md, found)
            print(f"ok {c} {len(md)} chars {found}")
        except Exception as e:  # noqa: BLE001
            fails += 1; print(f"FAIL {c}: {e!r}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
