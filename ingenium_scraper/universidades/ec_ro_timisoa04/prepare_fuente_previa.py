"""Paso previo (una sola vez): une, SIN profesorado, el catalogo Erasmus de la Facultad de Mecanica de UPT
('Course_catalogue_Faculty of Mechanical Engineering_2025-2026.xlsx', hoja Bachelor, programa Mechanical Engineering,
codigos L431) con las secciones de las fichas (Fisa disciplinei) que el usuario extrajo de los Word de la facultad
(OfertaUPT_Ingegneria_Meccanica_Details.json). Salida: fuente_previa/upt_cursos.json."""
import glob
import json
import re
from pathlib import Path

import openpyxl

PARENT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "fuente_previa" / "upt_cursos.json"
wb = openpyxl.load_workbook(glob.glob(str(PARENT / "Course_catalogue*.xlsx"))[0], data_only=True)
ws = wb["Bachelor 2025-2026 "]
det = json.loads((PARENT / "OfertaUPT_Ingegneria_Meccanica_Details.json").read_text(encoding="utf-8"))
norm = lambda s: re.sub(r"\W+", " ", (s or "").lower()).strip()  # noqa: E731
rows = []
for r in range(3, ws.max_row + 1):
    code = ws.cell(r, 6).value
    if not (code and str(code).startswith("L431")):
        continue
    raw = str(ws.cell(r, 5).value or "").strip()
    cand = [d for d in det if d["code"] == str(code).strip()]
    match = next((d for d in cand if norm(d["name_en"]) in norm(raw) or norm(raw) in norm(d["name_en"])), None)
    name = (match["name_en"] if match else raw).strip()
    lang = str(ws.cell(r, 14).value or "").strip()
    rows.append({"code": str(code).strip(), "name": name, "name_raw": raw, "year": int(ws.cell(r, 7).value),
                 "semester": int(ws.cell(r, 8).value), "ects": float(ws.cell(r, 9).value),
                 "hours": {"course": ws.cell(r, 10).value, "seminar": ws.cell(r, 11).value, "lab": ws.cell(r, 12).value, "project": ws.cell(r, 13).value},
                 "teaching_language": "en" if lang.startswith("English") else "ro" if lang.startswith("ROMANIAN") else None,
                 "sections": match["sections"] if match else {}})
OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(rows), "filas;", sum(bool(r["sections"].get("Objectives")) for r in rows), "con ficha")
