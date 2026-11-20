"""Vuelca el listado SIES de destinos Erasmus+ (xls de Uniovi) a db/destinos_sies.json y .db.

Una fila por (destino, titulación Uniovi). Se excluye la columna `responsable` (nombre de profesorado, GDPR).
Enlaza cada destino con su slug del pipeline por el código Erasmus (config/universities_convenio.json).
Uso: python ingest_sies.py [ruta.xls]
"""
import json, re, sqlite3, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
XLS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "destinosErasmus_SIES_25-26_enviar_profes.xls"
norm = lambda s: re.sub(r"\s+", "", str(s)).upper()

conv = json.loads((ROOT / "config" / "universities_convenio.json").read_text(encoding="utf-8"))
slug_of = {norm(c["erasmus_code"]): c["slug"] for c in conv}

df = pd.read_excel(XLS)
df.columns = [str(c).split("\n")[0].strip() for c in df.columns]
KEEP = {"oferta": "titulacion_uniovi", "ACUERDO/CUPO": "acuerdo_cupo", "PLAZAS TOTALES": "plazas_totales",
        "prioridad": "prioridad", "institucion": "institucion", "codigoinstitucion": "codigo_erasmus",
        "curso": "curso_destino", "idioma1": "idioma1", "nivelIdioma1": "nivel_idioma1", "idioma2": "idioma2",
        "nivelIdioma2": "nivel_idioma2", "duracion": "duracion", "inicio": "inicio", "fin": "fin",
        "doble Titulacion UNIOVI + destino": "doble_titulacion", "tipo Permiso TFG": "permiso_tfg",
        "tipo Permiso Practicas": "permiso_practicas", "Titulaciones preferentes": "titulaciones_preferentes",
        "Información (fact sheet o página web de la universidad de destino con la información de nominations deadline, applications deadline, requisitos de idioma, pre-requisitos, etc.)": "web_informacion",
        "códigos ISCED": "isced"}
cols = {}
for c in df.columns:
    for k, v in KEEP.items():
        if c.startswith(k[:40]) and v not in cols.values():
            cols[c] = v
df = df[list(cols)].rename(columns=cols)
df = df[df["institucion"].notna()].copy()
df["slug"] = df["codigo_erasmus"].map(lambda c: slug_of.get(norm(c)))
df = df.astype(object).where(df.notna(), None)
rows = json.loads(df.to_json(orient="records", force_ascii=False))
out = ROOT / "db"
out.mkdir(exist_ok=True)
(out / "destinos_sies.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
con = sqlite3.connect(out / "destinos_sies.db")
df.to_sql("destinos_sies", con, if_exists="replace", index=False)
con.close()
print(f"{len(rows)} filas · {df['codigo_erasmus'].nunique()} destinos · {df['slug'].notna().sum()} filas enlazadas a un slug del pipeline")
