#!/usr/bin/env python3
"""Fase 1 · Descubrimiento — Università "G. d'Annunzio" di Chieti-Pescara (UdA),
Laurea triennale in Ingegneria Biomedica (L460R, classe L-9 Ingegneria industriale).

UdA no imparte Ingegneria Meccanica. Se elige Ingegneria Biomedica porque es su único
grado de primer ciclo en la clase L-9 "Ingegneria industriale" (la misma clase que
Ingegneria Meccanica en Italia); la otra opción, Ingegneria delle Costruzioni / Edile
(L-23), es ingeniería civil.

Fuente: el catálogo de cursos de Cineca (unich.coursecatalogue.cineca.it), una SPA
Angular que se alimenta de una API JSON pública en /api/v1 (descubierta en el bundle
main.*.js). www.unich.it y unich.esse3.cineca.it responden 403 (desafío Cloudflare) a
clientes automatizados y no se usan.

  1. /api/v1/corsi?anno=AAAA&minimal=true       -> lista de grados, localiza cdsCod L460R
  2. /api/v1/corso/{coorte}/{cod}                -> plan por currículo (percorsi) y año
  3. /api/v1/insegnamento?anno=…&insegnamento=… -> ficha de cada asignatura (syllabus IT+EN)

Cohorte: 2025 (primera cohorte del grado). Sus años 1 y 2 se imparten en 2025/26 y
2026/27, con syllabus publicado; el año 3 se impartirá en 2027/28 y aún no tiene
syllabus (esas filas quedan como `sin_guia` hasta que se publiquen: basta re-ejecutar
con la caché borrada). La cohorte 2026 (nuevo ordinamento) solo tendría el año 1.

Uso (desde la raíz del proyecto):
    python universidades/unich/discover_unich.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from common.http_client import PoliteClient  # noqa: E402
from common.schema import Catalog, CatalogEntry, CatalogMeta  # noqa: E402

HERE = Path(__file__).parent
SLUG = "unich"
UNIVERSIDAD = "Università degli Studi \"G. d'Annunzio\" Chieti-Pescara"
HOST = "https://unich.coursecatalogue.cineca.it"
API = HOST + "/api/v1"
CDS_COD = "L460R"          # Ingegneria Biomedica (laurea triennale)
COORTE = "2025"            # cohorte de referencia (ver docstring)

SEM = {"S1": 1, "S2": 2}
TEXT_KEYS = ("contenuti", "obiettivi_formativi", "prerequisiti", "programmazione_estesa", "testi",
             "verifica_apprendimento", "metodi_didattici_est", "altro")


def insegnamento_url(act: dict) -> str:
    q = {"anno": act["aa"], "insegnamento": act["cod"], "ordinamento_aa": act["ordinamento_aa"],
         "af_percorso": act["af_percorso_id"], "corso_cod": act["corso_cod"], "corso_aa": COORTE}
    return f"{API}/insegnamento?{urlencode(q)}"


def page_url(act: dict) -> str:
    """URL legible por humanos de la ficha en la SPA (solo informativa)."""
    return (f"{HOST}/corsi/{COORTE}/{act['corso_cod']}/insegnamenti/{act['aa']}/{act['cod']}/"
            f"{act['ordinamento_aa']}/{act['af_percorso_id']}?coorte={COORTE}")


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

    # 1) grado en la lista de la cohorte
    grupos = http.get_json(f"{API}/corsi?anno={COORTE}&minimal=true")
    subs = [s for g in grupos for sg in g["subgroups"] for c in sg["cds"] for s in c["cdsSub"]
            if s["cdsCod"] == CDS_COD]
    if len(subs) != 1:
        raise RuntimeError(f"{CDS_COD}: {len(subs)} coincidencias en la lista de {COORTE}")
    cod_corso = subs[0]["cod"]

    # 2) plan
    corso = http.get_json(f"{API}/corso/{COORTE}/{cod_corso}")[0]
    if corso["tipo_corso_cod"] != "L":
        raise RuntimeError("No es una laurea triennale")
    nombre_grado = f"Laurea in {corso['des_it'].strip().title()} ({corso['des_en'].strip().title()}), " \
                   f"classe {corso['classe_cod']} {corso['classe_it']}"
    ects_total = float(corso["crediti"])

    acts: dict[str, dict] = {}            # cod de actividad (único por currículo) -> actividad
    curr_of: dict[str, set[str]] = {}
    grupo_of: dict[str, str] = {}
    for p in corso["percorsi"]:
        for anno in p["anni"]:
            for g in anno["insegnamenti"]:
                for a in g["attivita"]:
                    acts.setdefault(a["cod"], a)
                    curr_of.setdefault(a["cod"], set()).add(p["pdsCod"])
                    grupo_of[a["cod"]] = g["label_it"]
    pds_des = {p["pdsCod"]: p["des_it"] for p in corso["percorsi"]}

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
            ins = http.get_json(url)
            fields = text_fields(ins)
            has_guide = any(it or en for _, it, en in fields)
            sem = semestre_de(a, ins)
            curso = int(a["annoCorso"])
            currs = sorted(curr_of[c])
            currs_txt = ", ".join(pds_des[x] for x in currs)
            car = caracter_de(a)
            if car == "libre_eleccion":
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
    # Cada currículo completo = obligatorias del currículo + las comunes ("003 CORSO GENERICO")
    comun = [p["pdsCod"] for p in corso["percorsi"] if p.get("comune")]
    for p in corso["percorsi"]:
        if p.get("comune"):
            continue
        obb = sums[p["pdsCod"]].get("Obbligatori", 0)
        assert obb == ects_total, f"{p['pdsCod']}: obligatorias {obb} != {ects_total}"
    n_sin = sum(e.tipo_fuente == "sin_guia" for e in entries)
    n_en = sum(e.idioma_pagina == "en" and e.tipo_fuente != "sin_guia" for e in entries)
    ofertado = sum(e.creditos_ects for e in entries)

    meta = CatalogMeta(
        universidad=UNIVERSIDAD,
        slug=SLUG,
        nombre_grado=nombre_grado,
        curso_academico=f"cohorte {COORTE}/{int(COORTE) + 1} (años 1-3 = A.A. 2025/26, 2026/27, 2027/28)",
        url_plan_estudios=f"{HOST}/corsi/{COORTE}/{cod_corso}",
        ects_totales_plan=ects_total,
        estrategia_fuente=("API JSON pública del catálogo Cineca (SPA Angular): /api/v1/corsi -> "
                           "/api/v1/corso/{coorte}/{cod} (plan por currículo) -> /api/v1/insegnamento "
                           "(ficha con campos HTML _it/_en por sección, también por módulo)."),
        generado_por="discover_unich.py",
        generado_en=time.strftime("%Y-%m-%dT%H:%M:%S"),
        estado="ok",
        notas=(f"Ingegneria Meccanica no existe en UdA; se usa Ingegneria Biomedica (L-9 Ingegneria "
               f"industriale, misma clase que Meccanica). {len(entries)} filas = unión de los currículos "
               f"{', '.join(f'{k} {v}' for k, v in pds_des.items())} ({comun} = parte común). Cada currículo "
               f"suma {ects_total:g} ECTS de 'Obbligatori' (incluye un hueco 'A SCELTA DELLO STUDENTE' "
               f"de 12 ECTS que se cubre con optativas del grupo 'A scelta'); {ofertado:g} ECTS ofertados en "
               f"total. Códigos = adCod de Esse3; si un adCod tiene créditos distintos según currículo "
               f"se sufija con el código de currículo. {n_sin} filas sin_guia (año 3 = A.A. 2027/28 aún sin "
               f"syllabus publicado, y el hueco de libre elección). {n_en} fichas con versión inglesa completa "
               f"(idioma 'en'); el resto 'it'. url_guia_docente = endpoint JSON; la página humana es "
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
