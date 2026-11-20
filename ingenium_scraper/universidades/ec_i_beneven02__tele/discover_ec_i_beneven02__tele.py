#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Università degli Studi del Sannio (Benevento), Laurea in Ingegneria Elettronica e Biomedica (L-8).

Fuente: catálogo Cineca (unisannio.coursecatalogue.cineca.it), API JSON pública /api/v1 (misma plataforma que unich; ver docs/PLATAFORMAS.md).

Uso (desde la raíz del proyecto):
    python universidades/ec_i_beneven02__tele/discover_ec_i_beneven02__tele.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import FetchError, PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "ec_i_beneven02__tele"
UNIVERSIDAD = "Università degli Studi del Sannio"
HOST = "https://unisannio.coursecatalogue.cineca.it"
API = HOST + "/api/v1"
COHORTES = [['2024', '863'], ['2025', '800'], ['2026', '800']]
AA = "2026"                  # A.A. (año inicial) cuyos syllabus se recogen; "" = sin filtro
COORTE = COHORTES[0][0]

SEM = {"S1": 1, "S2": 2}
TEXT_KEYS = ("contenuti", "obiettivi_formativi", "prerequisiti", "programmazione_estesa", "testi",
             "verifica_apprendimento", "metodi_didattici_est", "altro")


def insegnamento_url(act: dict) -> str:
    q = {"anno": act["aa"], "insegnamento": act["cod"], "ordinamento_aa": act["ordinamento_aa"],
         "af_percorso": act["af_percorso_id"], "corso_cod": act["corso_cod"], "corso_aa": act["_coorte"]}
    return f"{API}/insegnamento?{urlencode(q)}"


def page_url(act: dict) -> str:
    """URL legible por humanos de la ficha en la SPA (solo informativa)."""
    return (f"{HOST}/corsi/{act['_coorte']}/{act['corso_cod']}/insegnamenti/{act['aa']}/{act['cod']}/"
            f"{act['ordinamento_aa']}/{act['af_percorso_id']}?coorte={act['_coorte']}")


def _txt(html: str | None) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "").replace("&nbsp;", " ")).strip()


def text_fields(ins: dict) -> list[tuple[str, str, str]]:
    """(campo, texto_it, texto_en) de todas las entradas de testiTotali (insegnamento o módulos)."""
    out = []
    for t in ins.get("testiTotali") or []:
        for k in TEXT_KEYS:
            for pref in ("", "mod_"):
                it, en = _txt(t.get(f"{pref}{k}_it")), _txt(t.get(f"{pref}{k}_en"))
                if it or en:
                    out.append((k, it, en))
    return out


_IT_WORDS = re.compile(r"\b(il|della|delle|degli|che|per|sono|con|nel|dei|lo|gli|una|alla)\b", re.I)
_EN_WORDS = re.compile(r"\b(the|and|of|to|is|are|with|for|which|this|students?)\b", re.I)


def looks_english(text: str) -> bool:
    return len(_EN_WORDS.findall(text)) > len(_IT_WORDS.findall(text))


def lang_of(fields: list[tuple[str, str, str]]) -> str:
    """'en' si cada campo con texto italiano tiene versión inglesa no vacía y que parece
    inglés (más palabras funcionales inglesas que italianas); la bibliografía ('testi') y
    los textos muy cortos (< 60 caracteres, p. ej. 'Italiano') solo se exigen no vacíos.
    Si no, 'it' (la versión original, siempre completa)."""
    if not fields:
        return "it"
    for k, it, en in fields:
        if it and not en:
            return "it"
        if k != "testi" and len(it) >= 60 and not looks_english(en):
            return "it"
    return "en"


def semestre_de(act: dict, ins: dict) -> int | None:
    cods = {f.get("periodo_didattico_cod") for f in act.get("frazioni") or []}
    cods |= {act.get("periodo_didattico_cod")}
    cods |= {m.get("periodo_didattico_cod") for m in ins.get("moduli") or []}
    cods |= {f.get("periodo_didattico_cod") for f in ins.get("frazioni") or []}
    sems = {SEM[c] for c in cods if c in SEM}
    return sems.pop() if len(sems) == 1 else None


def caracter_de(act: dict) -> str:
    des, taf, tipo = act["des_it"].upper(), act.get("tafDes_it") or "", act.get("tipo_ins_cod")
    if "PROVA FINALE" in des:
        return "tfg"
    if "TIROCINIO" in des:
        return "practicas"
    if tipo == "OPZ":
        return "optativa"
    if taf == "A scelta dello studente":
        return "libre_eleccion"
    if taf.startswith("Base"):
        return "formacion_basica"
    return "obligatoria"


def main() -> None:
    http = PoliteClient(cache_dir=HERE / "raw_cache")

    acts: dict[str, dict] = {}            # cod de actividad -> actividad
    curr_of: dict[str, set[str]] = {}
    grupo_of: dict[str, str] = {}
    pds_des: dict[str, str] = {}
    for coorte, cds_cod in COHORTES:
        grupos = http.get_json(f"{API}/corsi?anno={coorte}&minimal=true")
        subs = [s for g in grupos for sg in g["subgroups"] for c in sg["cds"] for s in c["cdsSub"]
                if s["cdsCod"] == cds_cod]
        if len(subs) != 1:
            raise RuntimeError(f"{cds_cod}: {len(subs)} coincidencias en la lista de {coorte}")
        cod_corso = subs[0]["cod"]
        corso = http.get_json(f"{API}/corso/{coorte}/{cod_corso}")[0]
        if corso["tipo_corso_cod"] not in ("L", "L2", "LM", "LM6"):
            raise RuntimeError("No es una laurea triennale")
        if coorte == COORTE:
            nombre_grado = f"Laurea in {corso['des_it'].strip().title()} ({corso['des_en'].strip().title()}), "                            f"classe {corso['classe_cod']} {corso['classe_it']}"
            ects_total = float(corso["crediti"])
            first_cod = cod_corso
        for p in corso["percorsi"]:
            pds_des[p["pdsCod"]] = p["des_it"]
            for anno in p["anni"]:
                for g in anno.get("insegnamenti", []):
                    if re.match(r"(?i)\W*(revisione|af non opzionate)", g["label_it"]) or "offerti da altri corsi" in g["label_it"]:
                        continue    # duplicados (revisiones) y optativas ofrecidas por otros grados
                    for a in g.get("attivita") or []:
                        if str(anno.get("anno")) not in ("1", "2", "3", "4") or (AA and a["aa"] != AA):
                            continue
                        a.setdefault("annoCorso", anno["anno"])
                        a["_coorte"] = coorte
                        acts.setdefault(a["cod"], a)
                        curr_of.setdefault(a["cod"], set()).add(p["pdsCod"])
                        grupo_of[a["cod"]] = g["label_it"]
    cod_corso = first_cod

    # Clave estable: adCod (código oficial Esse3) si es único; si el mismo adCod aparece
    # como actividades distintas (créditos distintos según currículo), adCod + "_" + af_percorso_cod.
    by_ad: dict[str, list[str]] = {}
    for c, a in acts.items():
        by_ad.setdefault(a["adCod"], []).append(c)

    entries, sums = [], {}
    for ad, cods in sorted(by_ad.items()):
        for c in sorted(cods, key=lambda c: acts[c]["af_percorso_cod"]):
            a = acts[c]
            key = ad if len(cods) == 1 else f"{ad}_{a['af_percorso_cod']}"
            url = insegnamento_url(a)
            try:
                try:
                    ins = http.get_json(url)
                except Exception:
                    ins = {}
            except FetchError:      # 404: ficha no publicada -> sin_guia
                ins = {}
            fields = text_fields(ins)
            has_guide = any(it or en for _, it, en in fields)
            sem = semestre_de(a, ins)
            curso = int(a["annoCorso"])
            currs = sorted(curr_of[c])
            currs_txt = ", ".join(pds_des[x] for x in currs)
            car = caracter_de(a)
            if car == "libre_eleccion" or (a.get("crediti") or 0) == 0:
                has_guide = False       # hueco de libre elección: no es una asignatura
            entries.append(CatalogEntry(
                universidad=UNIVERSIDAD,
                nombre_grado=nombre_grado,
                codigo_asignatura=key,
                nombre_asignatura=a["des_it"].strip(),
                curso_semestre=(f"Anno {curso} / {'Semestre ' + str(sem) if sem else 'periodo n.d.'}"
                                f" / A.A. {a['aa']}/{int(a['aa']) + 1} / {grupo_of[c]} / {currs_txt}"),
                curso=curso,
                semestre=(curso - 1) * 2 + sem if sem else None,
                creditos_ects=float(a["crediti"]),
                caracter=car,
                idioma_pagina=lang_of(fields) if has_guide else "it",
                url_guia_docente=url,
                tipo_fuente="api" if has_guide else "sin_guia",
            ))
            for pc in currs:
                sums.setdefault(pc, {}).setdefault(grupo_of[c], 0)
                sums[pc][grupo_of[c]] += float(a["crediti"])

    # ---------- validación ----------
    codes = [e.codigo_asignatura for e in entries]
    assert len(codes) == len(set(codes)), "Códigos duplicados"
    assert all(e.url_guia_docente or e.tipo_fuente == "sin_guia" for e in entries)
    tot_cur = {pc: round(sum(v.values()), 1) for pc, v in sums.items()}
    n_sin = sum(e.tipo_fuente == "sin_guia" for e in entries)
    n_en = sum(e.idioma_pagina == "en" and e.tipo_fuente != "sin_guia" for e in entries)
    ofertado = sum(e.creditos_ects for e in entries)

    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=nombre_grado,
        curso_academico="A.A. 2026/27 (años 1-3 de cohortes 2026, 2025 y 2024)",
        url_plan_estudios=f"{HOST}/corsi/{COORTE}/{cod_corso}",
        ects_totales_plan=ects_total,
        estrategia_fuente=("API JSON pública del catálogo Cineca (SPA Angular): /api/v1/corsi -> "
                           "/api/v1/corso/{coorte}/{cod} (plan por currículo) -> /api/v1/insegnamento "
                           "(ficha con campos HTML _it/_en por sección, también por módulo)."),
        generado_por="discover_ec_i_beneven02__tele.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(f"Titulación elegida: Laurea triennale en Ingegneria Elettronica e Biomedica (L-8; cdsCod 866 ordinamento 2023 para la cohorte 2024 y 803 ordinamento 2025 para 2025-26), la más afín a Electrónica Industrial y Automática (filas Erasmus de Sannio: Tecnologías Industriales 4 plazas, EIA, Informática TI, Teleco; Sannio no tiene laurea industrial/eléctrica/automática: solo Informatica, Energetica, Civile y Elettronica e Biomedica; la magistrale queda fuera). Solo hay syllabus publicado del A.A. 2026/27, así que el año 1 sale de la cohorte 2026, el 2 de la 2025 y el 3 de la 2024. Se omiten los grupos 'revisione' y 'offerti da altri corsi' (duplicados). {len(entries)} filas = unión de los currículos {', '.join(f'{k} {v}' for k, v in pds_des.items())}. "
               f"ECTS ofertados por currículo (obligatorias + optativas de todos los grupos): {tot_cur}; plan = {ects_total:g} ECTS "
               f"(las optativas/libres se eligen entre las ofertadas, por eso la suma ofertada supera el total). "
               f"Códigos = adCod de Esse3 (sufijo af_percorso si hay varios con distintos créditos). "
               f"{n_sin} filas sin_guia (sin syllabus publicado o hueco de libre elección); {n_en} fichas con versión inglesa completa "
               f"(idioma 'en'); el resto 'it'. url_guia_docente = endpoint JSON; página humana: "
               f"{HOST}/corsi/{COORTE}/{cod_corso}/insegnamenti/<aa>/<cod>/<ord>/<percorso>?coorte={COORTE}."),
    )
    catalog = Catalog(meta=meta, asignaturas=entries)
    Catalog.model_validate(catalog.model_dump())
    out = HERE / "catalogo_urls.json"
    out.write_text(json.dumps(catalog.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{nombre_grado}: {len(entries)} filas, {ofertado:g} ECTS ofertados (plan {ects_total:g}); "
          f"sin_guia={n_sin}, en={n_en} -> {out}")
    print("ECTS por currículo/grupo:", json.dumps(sums, ensure_ascii=False))
    print("HTTP:", http.stats)


if __name__ == "__main__":
    main()
