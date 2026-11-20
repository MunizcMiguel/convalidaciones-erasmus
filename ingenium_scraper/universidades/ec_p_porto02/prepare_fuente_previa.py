"""Paso previo (una sola vez): copia a fuente_previa/ los datos que el usuario ya habia extraido de SIGARRA (FEUP)
(carpeta padre del proyecto: OfertaFEUP_Ingegneria_Meccanica_Details.json), SIN datos de profesorado
(se descartan 'Teaching Staff - Responsibilities', 'Teaching - Hours' y 'Cycles of Study/Courses'; de esta ultima
solo se conserva el curso (ano) en el que L.EM imparte cada UC)."""
import json
import re
from pathlib import Path

PARENT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "fuente_previa"
OUT.mkdir(exist_ok=True)
DROP = {"Teaching Staff - Responsibilities", "Teaching - Hours", "Cycles of Study/Courses"}
src = json.loads((PARENT / "OfertaFEUP_Ingegneria_Meccanica_Details.json").read_text(encoding="utf-8"))
out = []
for d in src:
    m = re.search(r"\bL\.EM\s+\d+\s+Syllabus\s+(\d+)\s+-\s+([\d,]+)", d["sections"].get("Cycles of Study/Courses", ""))
    out.append({"code": d["code"], "abbreviation": d.get("abbreviation"), "name": d["name"], "credits": d["credits"],
                "link": d["link"], "ects": m.group(2) if m else d["credits"], "instance": d.get("instance"), "year_lem": int(m.group(1)) if m else None,
                "sections": {k: v for k, v in d["sections"].items() if k not in DROP}})
(OUT / "feup_fichas.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(out), "fichas")
