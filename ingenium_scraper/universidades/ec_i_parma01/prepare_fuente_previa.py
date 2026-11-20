"""Paso previo (una sola vez): copia los datos que el usuario ya habia extraido (carpeta padre del proyecto)
a fuente_previa/, SIN datos de profesorado, y solo para el grado triennale Ingegneria Meccanica (CdS 3011 y 3111).
Origen: 'Offerta Formativa 2025-2026 - per pubblicazione.xlsx' (export OfertaUNIPr_Ingegneria_Meccanica.json) y
fichas de corsi.unipr.it/en/ugov/degreecourse/{id} (OfertaUNIPr_Ingegneria_Meccanica_Details.json)."""
import json
from pathlib import Path

PARENT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent / "fuente_previa"
KEEP_SECTIONS = ["Learning objectives", "Prerequisites", "Course unit content", "Full programme", "Bibliography",
                 "Teaching methods", "Assessment methods and criteria"]
rows = json.loads((PARENT / "OfertaUNIPr_Ingegneria_Meccanica.json").read_text(encoding="utf-8"))["filas"]
keys = {"cds": "Cod. Corso di Studio", "ord": "Cod. Ord. Did.", "reg": "Cod. Reg Did.", "cur": "Cod. Curriculum Curriculum code",
        "cur_name": "Curriculum Curriculum name", "id": "Id. Insegnamento", "code": "Codice Insegnamento Component code",
        "name_it": "Nome Insegnamento Component title (original)", "name_en": "Nome Insegnamento Inglese Component title in English",
        "ambito": "Des. Tipo Af Insegnamento", "ssd": "Cod. Settore", "cfu": "Crediti (CFU) ECTS/CFU credits",
        "year": "Anno Corso Insegnamento Course year for course unit", "lang": "Lingua Insegnamento Teaching language",
        "periodo": "Periodo Insegnamento Semester of teaching", "exam": "Tipo esame Exam type"}
plan = [{k: r.get(v) for k, v in keys.items()} for r in rows if r["Cod. Corso di Studio"] in ("3011", "3111")]
ids = {str(p["id"]) for p in plan}
det = json.loads((PARENT / "OfertaUNIPr_Ingegneria_Meccanica_Details.json").read_text(encoding="utf-8"))
fichas = {str(d["id"]): {"discipline": d.get("discipline"), "hours": d.get("hours"), "credits": d.get("credits"),
                         "language": d.get("language"), "semester_info": d.get("semester_info"),
                         "sections": {k: v for k, v in d["sections"].items() if k in KEEP_SECTIONS}}
          for d in det if str(d["id"]) in ids}
(OUT / "unipr_plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "unipr_fichas.json").write_text(json.dumps(fichas, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(plan), "filas plan;", len(fichas), "fichas")
