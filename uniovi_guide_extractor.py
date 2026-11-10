#!/usr/bin/env python3
import re
import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup, Tag

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

META_LABELS = {
    "Código asignatura": "codigo",
    "Curso": "curso",
    "Temporalidad": "temporalidad",
    "Materia": "materia",
    "Carácter": "caracter",
    "Créditos": "creditos",
    "Pertenece al itinerario Bilingüe": "itinerario_bilingue",
}

SECTION_ALIASES = {
    "Coordinación": "coordinacion",
    "Profesorado": "profesorado",
    "Contextualización": "contextualizacion",
    "Requisitos": "requisitos",
    "Competencias y resultados del aprendizaje": "competencias_resultados_aprendizaje",
    "Contenidos": "contenidos",
    "Metodología y plan de trabajo": "metodologia_plan_trabajo",
    "Evaluación del aprendizaje": "evaluacion_aprendizaje",
    "Bibliografía": "bibliografia",
}

SKIP_SUBJECT_LINES = {"Atrás", "Relacionados", "Estudia"}

JSON_ALL_DEFAULT = "GuiasDocentesAll.json"

DDL = """
CREATE TABLE IF NOT EXISTS asignaturas (
    codigo TEXT PRIMARY KEY,
    nombre TEXT,
    url TEXT,
    curso TEXT,
    semestre INTEGER,
    temporalidad TEXT,
    materia TEXT,
    caracter TEXT,
    creditos TEXT,
    itinerario_bilingue TEXT,
    periodo_academico TEXT,
    guia_docente_id TEXT,
    texto_renderizado TEXT,
    texto_guia TEXT
);

CREATE TABLE IF NOT EXISTS actividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_asignatura TEXT,
    actividad TEXT,
    horas TEXT,
    FOREIGN KEY(codigo_asignatura) REFERENCES asignaturas(codigo)
);

CREATE TABLE IF NOT EXISTS bloques_texto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_asignatura TEXT,
    apartado TEXT,
    titulo_original TEXT,
    texto_plano TEXT,
    FOREIGN KEY(codigo_asignatura) REFERENCES asignaturas(codigo)
);
"""


def clean_text(s: str) -> str:
    s = s.replace("\xa0", " ")
    s = s.replace("\u00ad", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n[ \t]+\n", "\n\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def split_lines(text: str) -> List[str]:
    return [clean_text(x) for x in text.splitlines() if clean_text(x)]


def fetch_page(url: str) -> Tuple[str, BeautifulSoup]:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return response.text, soup


def extract_asignatura_id(html: str) -> Optional[str]:
    match = re.search(r"_es_uniovi_sies_web_UnioviSiesWebPortlet_asignaturaId=(\d+)", html)
    return match.group(1) if match else None


def extract_portlet_base(html: str) -> Optional[str]:
    match = re.search(
        r'(https?://www\.uniovi\.es/estudia/grados/[^?"\']+)\?[^"\']*serveGuiasDocentes',
        html,
    )
    return match.group(1) if match else None


def find_subject_container(soup: BeautifulSoup) -> Optional[Tag]:
    label = soup.find(string=re.compile(r"^\s*Código asignatura\s*$", re.I))
    if not label:
        return None

    node = label.parent
    for _ in range(12):
        if node is None:
            break
        text = node.get_text("\n", strip=True)
        if "Actividades" in text and "Periodo Académico" in text:
            return node
        node = node.parent
    return None


def extract_subject_name(container: Tag) -> Optional[str]:
    lines = split_lines(container.get_text("\n"))
    for index, line in enumerate(lines):
        if line != "Código asignatura" or index == 0:
            continue
        for candidate in reversed(lines[:index]):
            if candidate in META_LABELS or candidate in SKIP_SUBJECT_LINES:
                continue
            if candidate.startswith("goto "):
                continue
            return candidate
    return None


def extract_metadata(container: Tag) -> Dict[str, str]:
    lines = split_lines(container.get_text("\n"))
    meta: Dict[str, str] = {}
    for index, line in enumerate(lines):
        if line in META_LABELS and index + 1 < len(lines):
            meta[META_LABELS[line]] = lines[index + 1]
    return meta


def extract_activities(container: Tag) -> List[Dict[str, str]]:
    text = container.get_text("\n", strip=False)
    match = re.search(r"Actividades(.*?)Periodo Académico", text, re.S | re.I)
    if not match:
        return []

    activities: List[Dict[str, str]] = []
    for line in split_lines(match.group(1)):
        line = re.sub(r"^[*•\-\s]+", "", line).strip()
        item = re.match(r"^(.*?)\s*\((.*?)\)\s*$", line)
        if item:
            activities.append({
                "actividad": clean_text(item.group(1)),
                "horas": clean_text(item.group(2)),
            })
    return activities


def portlet_url(portlet_base: str, params: Dict[str, str]) -> str:
    return f"{portlet_base}?{urlencode(params)}"


def fetch_guias_list(portlet_base: str, asignatura_id: str) -> List[Dict[str, Any]]:
    url = portlet_url(portlet_base, {
        "p_p_id": "es_uniovi_sies_web_UnioviSiesWebPortlet",
        "p_p_lifecycle": "2",
        "p_p_state": "normal",
        "p_p_mode": "view",
        "p_p_resource_id": "serveGuiasDocentes",
        "p_p_cacheability": "cacheLevelPage",
        "_es_uniovi_sies_web_UnioviSiesWebPortlet_asignaturaId": asignatura_id,
    })
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def pick_guia(guias: List[Dict[str, Any]], periodo: Optional[str]) -> Dict[str, Any]:
    if not guias:
        raise ValueError("No hay guías docentes disponibles para esta asignatura.")

    if periodo:
        for guia in guias:
            if guia.get("periodoAcademico") == periodo:
                return guia
        available = ", ".join(g["periodoAcademico"] for g in guias)
        raise ValueError(f"Periodo '{periodo}' no encontrado. Disponibles: {available}")

    return guias[0]


def fetch_guide_html(portlet_base: str, guia_docente_id: str) -> str:
    url = portlet_url(portlet_base, {
        "p_p_id": "es_uniovi_sies_web_UnioviSiesWebPortlet",
        "p_p_lifecycle": "0",
        "p_p_state": "exclusive",
        "p_p_mode": "view",
        "_es_uniovi_sies_web_UnioviSiesWebPortlet_mvcRenderCommandName": "/GuiaDocente",
        "_es_uniovi_sies_web_UnioviSiesWebPortlet_guiaDocenteId": guia_docente_id,
    })
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def section_content(soup: BeautifulSoup, section: Tag) -> str:
    target = section.get("data-target", "")
    if target:
        collapse = soup.select_one(target)
        if collapse:
            return clean_text(collapse.get_text("\n", strip=False))

    parent_card = section.find_parent("div", class_="card")
    if parent_card:
        sibling = parent_card.find_next_sibling("div", class_="collapse")
        if sibling:
            return clean_text(sibling.get_text("\n", strip=False))

    return ""


def split_sections_from_html(guide_html: str) -> Dict[str, Dict[str, str]]:
    soup = BeautifulSoup(guide_html, "html.parser")
    sections: Dict[str, Dict[str, str]] = {}

    for section in soup.select("div.seccion"):
        title = clean_text(section.get_text(" ", strip=True))
        alias = SECTION_ALIASES.get(title)
        if not alias:
            continue
        sections[alias] = {
            "heading": title,
            "texto_plano": section_content(soup, section),
        }

    return sections


def infer_code_from_url(url: str) -> Optional[str]:
    match = re.search(r"/([A-Z0-9]+-\d-\d+)/?$", url)
    return match.group(1) if match else None


def parse_uniovi_guide(
    url: str,
    periodo: Optional[str] = None,
    plan_item: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    html, soup = fetch_page(url)

    container = find_subject_container(soup)
    if container is None:
        raise ValueError("No se encontró el bloque de metadatos de la asignatura.")

    subject_name = extract_subject_name(container)
    metadata = extract_metadata(container)
    activities = extract_activities(container)
    subject_block = clean_text(container.get_text("\n", strip=False))

    asignatura_id = extract_asignatura_id(html)
    portlet_base = extract_portlet_base(html)
    if not asignatura_id or not portlet_base:
        raise ValueError("No se pudo localizar la configuración del portlet SIES en la página.")

    guias = fetch_guias_list(portlet_base, asignatura_id)
    guia = pick_guia(guias, periodo)
    guide_html = fetch_guide_html(portlet_base, guia["guiaDocenteId"])
    guide_text = clean_text(BeautifulSoup(guide_html, "html.parser").get_text("\n", strip=False))
    sections = split_sections_from_html(guide_html)

    return {
        "url": url,
        "subject_name": subject_name or (plan_item or {}).get("asignatura"),
        "metadata": metadata,
        "activities": activities,
        "sections": sections,
        "periodo_academico": guia.get("periodoAcademico"),
        "guia_docente_id": guia.get("guiaDocenteId"),
        "asignatura_id": asignatura_id,
        "subject_block": subject_block,
        "guide_text": guide_text,
        "plan": plan_item or {},
    }


def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(DDL)

    cur.execute("PRAGMA table_info(asignaturas)")
    columns = {row[1] for row in cur.fetchall()}
    for column, col_type in (
        ("periodo_academico", "TEXT"),
        ("guia_docente_id", "TEXT"),
        ("texto_renderizado", "TEXT"),
        ("semestre", "INTEGER"),
        ("texto_guia", "TEXT"),
    ):
        if column not in columns:
            cur.execute(f"ALTER TABLE asignaturas ADD COLUMN {column} {col_type}")

    conn.commit()


def clear_database(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("DELETE FROM bloques_texto")
    cur.execute("DELETE FROM actividades")
    cur.execute("DELETE FROM asignaturas")
    conn.commit()


def save_to_sqlite(
    parsed: Dict[str, Any],
    db_path: str,
    conn: Optional[sqlite3.Connection] = None,
) -> None:
    own_conn = conn is None
    if own_conn:
        conn = sqlite3.connect(db_path)
        ensure_schema(conn)

    cur = conn.cursor()
    meta = parsed["metadata"]
    plan = parsed.get("plan") or {}
    codigo = meta.get("codigo") or plan.get("codigo") or infer_code_from_url(parsed["url"])

    curso = meta.get("curso") or plan.get("curso")
    semestre = plan.get("semestre")
    if semestre is None and meta.get("temporalidad"):
        t = meta["temporalidad"].lower()
        if "primer" in t:
            semestre = 1
        elif "segundo" in t:
            semestre = 2

    cur.execute(
        """
        INSERT OR REPLACE INTO asignaturas (
            codigo, nombre, url, curso, semestre, temporalidad, materia, caracter,
            creditos, itinerario_bilingue, periodo_academico, guia_docente_id,
            texto_renderizado, texto_guia
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            codigo,
            parsed.get("subject_name") or plan.get("asignatura"),
            parsed.get("url"),
            curso,
            semestre,
            meta.get("temporalidad"),
            meta.get("materia"),
            meta.get("caracter") or plan.get("caracter"),
            meta.get("creditos") or plan.get("creditos"),
            meta.get("itinerario_bilingue") or plan.get("itinerario_bilingue"),
            parsed.get("periodo_academico"),
            parsed.get("guia_docente_id"),
            parsed.get("subject_block"),
            parsed.get("guide_text"),
        ),
    )

    cur.execute("DELETE FROM actividades WHERE codigo_asignatura = ?", (codigo,))
    for act in parsed.get("activities", []):
        cur.execute(
            "INSERT INTO actividades (codigo_asignatura, actividad, horas) VALUES (?, ?, ?)",
            (codigo, act.get("actividad"), act.get("horas")),
        )

    cur.execute("DELETE FROM bloques_texto WHERE codigo_asignatura = ?", (codigo,))
    for apartado, payload in parsed.get("sections", {}).items():
        cur.execute(
            "INSERT INTO bloques_texto (codigo_asignatura, apartado, titulo_original, texto_plano) VALUES (?, ?, ?, ?)",
            (codigo, apartado, payload.get("heading"), payload.get("texto_plano")),
        )

    conn.commit()
    if own_conn:
        conn.close()


def load_plan(path: str) -> List[Dict[str, Any]]:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("El JSON del plan debe ser una lista de asignaturas.")
    return data


def import_plan_to_sqlite(
    plan_path: str,
    db_path: str,
    periodo: Optional[str] = None,
    fresh: bool = False,
    limit: Optional[int] = None,
    json_all_path: str = JSON_ALL_DEFAULT,
) -> Dict[str, Any]:
    plan = load_plan(plan_path)
    if limit is not None:
        plan = plan[:limit]

    conn = sqlite3.connect(db_path)
    ensure_schema(conn)
    if fresh:
        clear_database(conn)

    ok: List[Dict[str, Any]] = []
    guias: List[Dict[str, Any]] = []
    errors: List[Dict[str, str]] = []

    total = len(plan)
    for index, item in enumerate(plan, start=1):
        url = item.get("link")
        codigo = item.get("codigo", "?")
        nombre = item.get("asignatura", codigo)
        print(f"[{index}/{total}] {codigo} - {nombre}", flush=True)

        if not url:
            errors.append({"codigo": codigo, "error": "Sin enlace en el plan"})
            continue

        try:
            parsed = parse_uniovi_guide(url, periodo=periodo, plan_item=item)
            save_to_sqlite(parsed, db_path, conn=conn)
            guias.append(parsed)
            ok.append({
                "codigo": parsed["metadata"].get("codigo") or codigo,
                "nombre": parsed.get("subject_name"),
                "apartados": len(parsed.get("sections", {})),
                "actividades": len(parsed.get("activities", [])),
            })
        except Exception as exc:
            errors.append({"codigo": codigo, "url": url, "error": str(exc)})
            print(f"  ERROR: {exc}", flush=True)

    conn.close()

    if guias:
        export_guias_all(
            guias,
            json_all_path,
            periodo=periodo or guias[0].get("periodo_academico"),
            fuente_plan=plan_path,
        )

    return {
        "importadas": len(ok),
        "errores": len(errors),
        "ok": ok,
        "fallos": errors,
        "json_all": json_all_path if guias else None,
    }


def guide_codigo(parsed: Dict[str, Any]) -> str:
    meta = parsed.get("metadata") or {}
    plan = parsed.get("plan") or {}
    return meta.get("codigo") or plan.get("codigo") or infer_code_from_url(parsed.get("url", "")) or ""


def export_json(parsed: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(parsed, handle, ensure_ascii=False, indent=2)


def export_guias_all(
    guias: List[Dict[str, Any]],
    path: str,
    *,
    periodo: Optional[str] = None,
    fuente_plan: Optional[str] = None,
) -> None:
    payload = {
        "periodo_academico": periodo,
        "fuente_plan": fuente_plan,
        "total": len(guias),
        "guias": guias,
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def merge_guia_into_json_all(parsed: Dict[str, Any], path: str) -> None:
    codigo = guide_codigo(parsed)
    existing: Dict[str, Any] = {"guias": []}
    try:
        with open(path, encoding="utf-8") as handle:
            loaded = json.load(handle)
        if isinstance(loaded, dict) and isinstance(loaded.get("guias"), list):
            existing = loaded
        elif isinstance(loaded, list):
            existing = {"guias": loaded}
    except FileNotFoundError:
        pass

    guias = [g for g in existing.get("guias", []) if guide_codigo(g) != codigo]
    guias.append(parsed)
    guias.sort(key=lambda g: guide_codigo(g))

    export_guias_all(
        guias,
        path,
        periodo=parsed.get("periodo_academico") or existing.get("periodo_academico"),
        fuente_plan=existing.get("fuente_plan"),
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Extractor de guías docentes Uniovi")
    parser.add_argument("url", nargs="?", default=None, help="URL de una asignatura")
    parser.add_argument(
        "--plan",
        default=None,
        help="JSON con la lista de asignaturas (p. ej. gimeca_plan_estudios.json)",
    )
    parser.add_argument("--db", default="uniovi_guias.sqlite", help="SQLite de salida")
    parser.add_argument("--json", default=None, help="JSON de salida (solo modo URL)")
    parser.add_argument(
        "--json-all",
        default=JSON_ALL_DEFAULT,
        help=f"JSON agregado con todas las guías (por defecto: {JSON_ALL_DEFAULT})",
    )
    parser.add_argument(
        "--periodo",
        default=None,
        help="Periodo académico, p. ej. 2025-2026 (por defecto el más reciente)",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Vaciar la base de datos antes de importar el plan",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Importar solo las N primeras asignaturas del plan",
    )
    args = parser.parse_args()

    if args.plan:
        result = import_plan_to_sqlite(
            args.plan,
            args.db,
            periodo=args.periodo,
            fresh=args.fresh,
            limit=args.limit,
            json_all_path=args.json_all,
        )
        print(json.dumps({
            "modo": "plan",
            "plan": args.plan,
            "db": args.db,
            "json_all": result.get("json_all"),
            "periodo": args.periodo,
            "importadas": result["importadas"],
            "errores": result["errores"],
            "fallos": result["fallos"],
        }, ensure_ascii=False, indent=2))
        return

    if not args.url:
        parser.error("Indica una URL o usa --plan con un JSON de asignaturas.")

    parsed = parse_uniovi_guide(args.url, periodo=args.periodo)
    save_to_sqlite(parsed, args.db)
    merge_guia_into_json_all(parsed, args.json_all)

    if args.json:
        export_json(parsed, args.json)

    print(json.dumps({
        "codigo": parsed["metadata"].get("codigo") or infer_code_from_url(args.url),
        "nombre": parsed.get("subject_name"),
        "periodo": parsed.get("periodo_academico"),
        "n_actividades": len(parsed.get("activities", [])),
        "apartados": list(parsed.get("sections", {}).keys()),
        "db": args.db,
        "json": args.json,
        "json_all": args.json_all,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
