#!/usr/bin/env python3
"""Explorador comparativo de asignaturas · construye explorer/index.html

    python build_explorer.py            # embeddings + áreas (con caché) + HTML
    python build_explorer.py --no-api   # solo reutiliza la caché (sin llamar a Gemini)

Pasos (todo con caché por hash, así que re-ejecutar solo llama a la API para lo nuevo):
  1. Lee las asignaturas de db/ingenium_syllabi.db (salida de la Fase 3).
  2. Embeddings (gemini-embedding-001, 768 dim) de nombre + temario + resultados de aprendizaje.
  3. Clasificación en un área temática de lista cerrada (Gemini Flash).
  4. Para cada asignatura, sus vecinas más parecidas en OTRA universidad (similitud coseno).
  5. Escribe un único HTML con los datos incrustados (explorer/template.html -> explorer/index.html).
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import argparse
import hashlib
import json
import math
import os
import sqlite3
import time

import semantic_parser as sp
from common.util import ROOT

DB = ROOT / "db" / "ingenium_syllabi.db"
OUT = ROOT / "explorer"
CACHE = OUT / "cache"
EMB_MODEL = "gemini-embedding-001"
EMB_DIM = 768
AREA_MODEL = os.environ.get("LLM_MODEL", "gemini-2.5-flash")
TOP_K = 25          # vecinas guardadas por asignatura
# El coseno de gemini-embedding-001 entre asignaturas de ingeniería está muy comprimido (par al azar: mediana 0,835;
# mejor vecina de cada asignatura: mediana 0,947, p95 0,966). El "índice de coincidencia" reescala el coseno:
# 0 % = un par al azar, 100 % = el nivel de la mejor vecina típica. NO es una probabilidad.
IDX_LO, IDX_HI = 0.835, 0.966
MIN_IDX = 0.50      # por debajo no se guardan (el deslizante del HTML empieza en este valor)

AREAS = [
    "Mathematics", "Physics", "Chemistry", "Computer science & programming",
    "Mechanics (statics, dynamics, mechanisms, vibrations)", "Strength of materials & structures",
    "Fluid mechanics & hydraulics", "Thermodynamics, heat transfer & energy",
    "Materials science & metallurgy", "Manufacturing & production processes",
    "Machine design, CAD & graphics", "Electrical & electronics", "Automation, control & robotics",
    "Industrial organization, quality & management", "Economics, business & law",
    "Environment & sustainability", "Transport & vehicles", "Projects, internships & thesis",
    "Languages & humanities", "Other",
]

# slug -> (ciudad, lat, lon). El punto es la sede del grado, no el rectorado.
COORDS = {
    "uniovi": ("Gijón", 43.52, -5.62), "es_alfonso_x_sabio": ("Villanueva de la Cañada", 40.45, -3.99),
    "es_almeria": ("Almería", 36.83, -2.40), "es_antonio_nebrija": ("Madrid", 40.46, -3.72),
    "es_burgos": ("Burgos", 42.35, -3.69), "es_cadiz": ("Cádiz", 36.53, -6.29),
    "es_carlos_iii_madrid": ("Leganés", 40.33, -3.76), "es_extremadura": ("Badajoz", 38.88, -7.00),
    "es_jaen": ("Jaén", 37.79, -3.78), "es_jaume_castellon": ("Castellón", 39.99, -0.07),
    "es_laguna": ("La Laguna", 28.48, -16.32), "es_leon": ("León", 42.60, -5.57),
    "es_miguel_hernandez_elche": ("Elche", 38.27, -0.69), "es_mondragon_unibertsitatea": ("Mondragón", 43.06, -2.49),
    "es_nacional_educacion_a_distanc": ("Madrid (UNED)", 40.44, -3.73), "es_pais_vasco": ("Bilbao", 43.26, -2.95),
    "es_politecnica_madrid": ("Madrid", 40.40, -3.70), "es_politecnica_valencia": ("Valencia", 39.48, -0.34),
    "es_publica_navarra": ("Pamplona", 42.79, -1.64), "es_rey_juan_carlos": ("Móstoles", 40.34, -3.88),
    "es_rioja": ("Logroño", 42.46, -2.43), "es_rovira_virgili": ("Tarragona", 41.12, 1.25),
    "es_salamanca": ("Salamanca", 40.96, -5.66), "es_zaragoza": ("Zaragoza", 41.68, -0.89),
    "es_politecnica_catalunya": ("Vilanova i la Geltrú", 41.22, 1.73), "es_malaga": ("Málaga", 36.72, -4.48),
    "es_politecnica_cartagena": ("Cartagena", 37.60, -0.99), "es_valladolid": ("Valladolid", 41.66, -4.71),
    "es_girona": ("Girona", 41.96, 2.83), "es_vigo": ("Vigo", 42.17, -8.69), "es_navarra": ("Pamplona", 42.80, -1.67),
    "hka": ("Karlsruhe", 49.01, 8.39), "tuiasi": ("Iași", 47.16, 27.59), "unich": ("Chieti-Pescara", 42.38, 14.19),
    "uoc": ("Heraklion", 35.31, 25.07), "univ_rouen": ("Rouen", 49.44, 1.09), "his": ("Skövde", 58.39, 13.85),
    "mtu": ("Cork", 51.89, -8.53), "xamk": ("Kouvola", 60.87, 26.70),
}


def sha(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def load_courses() -> list[dict]:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    inst = {r["slug"]: dict(r) for r in con.execute("select * from institution")}
    courses = []
    for r in con.execute("select * from course order by institution_slug, year_of_study, semester, course_code"):
        c = dict(r)
        cid = c["id"]
        for table, key in (("topic", "topics"), ("teaching_method", "methods"), ("prerequisite", "prereq"), ("bibliography", "bib")):
            c[key] = [x[0] for x in con.execute(f"select text from {table} where course_id=? order by pos", (cid,))]
        c["outcomes"] = [dict(x) for x in con.execute("select type, code, text from learning_outcome where course_id=? order by pos", (cid,))]
        c["assess"] = [dict(x) for x in con.execute("select method, weight from assessment where course_id=? order by pos", (cid,))]
        c["uni_name"] = inst[c["institution_slug"]]["name"]
        c["country"] = inst[c["institution_slug"]]["country"]
        courses.append(c)
    return courses


def emb_text(c: dict) -> str:
    parts = [c["name_en"] or c["name_original"] or ""]
    if c["topics"]:
        parts.append("Topics: " + "; ".join(c["topics"][:20]))
    if c["outcomes"]:
        parts.append("Learning outcomes: " + " ".join(o["text"] for o in c["outcomes"][:8])[:1200])
    return "\n".join(parts)[:3500]


def load_cache(name: str) -> dict:
    p = CACHE / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def save_cache(name: str, data: dict) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def embed_all(client, courses: list[dict], use_api: bool) -> dict[str, list[float]]:
    from google.genai import types
    cache = load_cache("embeddings.json")
    todo = {}
    for c in courses:
        t = emb_text(c)
        h = sha(f"{EMB_MODEL}|{EMB_DIM}|{t}")
        c["_eh"] = h
        if h not in cache:
            todo[h] = t
    print(f"Embeddings: {len(cache)} en caché, {len(todo)} pendientes")
    if todo and use_api:
        items = list(todo.items())
        for i in range(0, len(items), 50):
            batch = items[i:i + 50]
            for attempt in range(5):
                try:
                    res = client.models.embed_content(
                        model=EMB_MODEL, contents=[t for _, t in batch],
                        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY", output_dimensionality=EMB_DIM))
                    break
                except Exception as e:  # noqa: BLE001
                    print("  reintento embeddings:", str(e)[:100])
                    time.sleep(5 * (attempt + 1))
            else:
                raise SystemExit("Embeddings: demasiados fallos")
            for (h, _), emb in zip(batch, res.embeddings):
                v = emb.values
                n = math.sqrt(sum(x * x for x in v)) or 1.0
                cache[h] = [round(x / n, 5) for x in v]
            save_cache("embeddings.json", cache)
            print(f"  {min(i + 50, len(items))}/{len(items)}")
    return cache


def classify_all(client, courses: list[dict], use_api: bool) -> dict[str, str]:
    from google.genai import types
    cache = load_cache("areas.json")
    key = lambda c: sha(f"{AREA_MODEL}|{'|'.join(AREAS)}|{c['name_en']}|{';'.join(c['topics'][:6])}")  # noqa: E731
    todo = [c for c in courses if key(c) not in cache]
    print(f"Áreas: {len(cache)} en caché, {len(todo)} pendientes")
    if todo and use_api:
        schema = types.Schema(type="ARRAY", items=types.Schema(
            type="OBJECT", properties={"i": types.Schema(type="INTEGER"), "area": types.Schema(type="STRING", enum=AREAS)},
            required=["i", "area"]))
        for b in range(0, len(todo), 40):
            batch = todo[b:b + 40]
            listing = "\n".join(f"{i}. {c['name_en']} — {'; '.join(c['topics'][:6])[:300]}" for i, c in enumerate(batch))
            prompt = ("Classify each university course into exactly one area from the allowed list, "
                      "based on its name and main topics. Return a JSON array of {i, area}.\n\n" + listing)
            for attempt in range(5):
                try:
                    res = client.models.generate_content(
                        model=AREA_MODEL, contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema, temperature=0))
                    out = json.loads(res.text)
                    break
                except Exception as e:  # noqa: BLE001
                    print("  reintento áreas:", str(e)[:100])
                    time.sleep(5 * (attempt + 1))
            else:
                raise SystemExit("Áreas: demasiados fallos")
            for o in out:
                if 0 <= o["i"] < len(batch):
                    cache[key(batch[o["i"]])] = o["area"]
            save_cache("areas.json", cache)
            print(f"  {min(b + 40, len(todo))}/{len(todo)}")
    return {c["id"]: cache.get(key(c), "Other") for c in courses}


def neighbours(courses: list[dict], emb: dict[str, list[float]]) -> dict[int, list[list[int]]]:
    import numpy as np
    idx = [i for i, c in enumerate(courses) if c["_eh"] in emb]
    mat = np.array([emb[courses[i]["_eh"]] for i in idx], dtype=np.float32)
    sims = mat @ mat.T
    inst = np.array([courses[i]["institution_slug"] for i in idx])
    out: dict[int, list[list[int]]] = {}
    for r, i in enumerate(idx):
        row = sims[r].copy()
        row[inst == inst[r]] = -1  # solo otras universidades
        top = np.argsort(-row)[:TOP_K * 6]
        best: dict[str, tuple[float, int]] = {}
        for t in top:  # una sola asignatura (la mejor) por universidad: es lo que el mapa pinta
            v = min(1.0, (float(row[t]) - IDX_LO) / (IDX_HI - IDX_LO))
            if v < MIN_IDX:
                break
            s = inst[t]
            if s not in best:
                best[s] = (v, idx[t])
        out[i] = [[j, int(round(v * 1000))] for v, j in sorted(best.values(), reverse=True)[:TOP_K]]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-api", action="store_true")
    a = ap.parse_args()
    sp.load_env()
    courses = load_courses()
    print(f"{len(courses)} asignaturas")
    client = None if a.no_api else sp.make_client()
    emb = embed_all(client, courses, not a.no_api)
    areas = classify_all(client, courses, not a.no_api)
    nb = neighbours(courses, emb)

    import build_extraction as bx
    COORDS.update({k: v for k, v in bx.EXTRA_COORDS.items() if k not in COORDS})
    insts = {}
    for c in courses:
        s = c["institution_slug"]
        if s not in insts:
            city = COORDS.get(s)
            if not city:
                print("  ¡sin coordenadas!", s)
            insts[s] = {"slug": s, "name": c["uni_name"], "country": c["country"],
                        "city": city[0] if city else "", "lat": city[1] if city else None, "lon": city[2] if city else None}
    # agrupación institución -> grados (para la barra lateral del explorador)
    for s, it in insts.items():
        nm = it["name"]
        if s.startswith("uniovi"):
            it["g"], it["gname"] = "uniovi", "Universidad de Oviedo"
            it["deg"] = nm.split(" - ", 1)[1] if " - " in nm else "Grado en Ingeniería Mecánica (GIMECA/GIOI)"
        else:
            base = s.split("__")[0]
            it["g"] = base
            if "__" in s and " – " in nm:
                it["gname"], it["deg"] = nm.split(" – ", 1)
            else:
                it["gname"], it["deg"] = nm, "Grado principal"
    for it in insts.values():  # el nombre de la institución es el del grupo base si existe
        b = insts.get(it["g"])
        if b and it["g"] != it["slug"]:
            it["gname"] = b["gname"]
    slim = []
    for i, c in enumerate(courses):
        slim.append({
            "u": c["institution_slug"], "code": c["course_code"], "name": c["name_original"], "en": c["name_en"],
            "ects": c["ects"], "sem": c["semester"], "yr": c["year_of_study"], "type": c["course_type"],
            "lang": c["languages"], "area": areas[c["id"]], "isced": c["isced_f"], "src": c["source_url"],
            "wl": c["workload_total"], "wc": c["workload_contact"], "rules": c["assessment_rules"],
            "topics": c["topics"], "methods": c["methods"], "prereq": c["prereq"], "bib": c["bib"],
            "lo": [[o["type"], o["code"], o["text"]] for o in c["outcomes"]],
            "as": [[x["method"], x["weight"]] for x in c["assess"]],
            "nb": nb.get(i, []),
        })
    data = {"generated": time.strftime("%Y-%m-%d"), "min_sim": int(MIN_IDX * 1000), "areas": AREAS,
            "insts": sorted(insts.values(), key=lambda x: (x["country"], x["name"])), "courses": slim}
    tpl = (OUT / "template.html").read_text(encoding="utf-8")
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    import build_extraction as bx  # botón «Extraction State» (no usa API)
    html = bx.inject(bx.build(), html)
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"Escrito {OUT / 'index.html'} ({len(html) // 1024} kB)")


if __name__ == "__main__":
    main()
