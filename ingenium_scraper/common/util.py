"""Utilidades compartidas: rutas, nombres de archivo, Markdown con cabecera y anonimización."""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNIS_DIR = ROOT / "universidades"
CONFIG = ROOT / "config" / "universities.json"

# Bloques que toda guía docente debería tener (Fase 2 valida que el scraper no los pierda)
REQUIRED_BLOCKS = ("contents", "learning_outcomes", "assessment")


def universities(grupo: str | None = None) -> list[dict]:
    """Universidades de todos los grupos (INGENIUM + España). `grupo` filtra: "ingenium" | "es" | "convenio".

    Una universidad presente en ambos (Oviedo) conserva su slug original y pertenece a los dos grupos.
    """
    unis = json.loads(CONFIG.read_text(encoding="utf-8"))
    for u in unis:
        u.setdefault("grupos", ["ingenium"])
    es_file = CONFIG.with_name("universities_es.json")
    if es_file.exists():
        by_domain = {u["domain"]: u for u in unis}
        for e in json.loads(es_file.read_text(encoding="utf-8")):
            if e.get("domain") in by_domain:
                first = by_domain[e["domain"]]
                first["grupos"] = sorted(set(first["grupos"]) | {"es"})
                first["titulos"] = e.get("titulos", [])
                continue
            e["grupos"] = ["es"]
            unis.append(e)
    # destinos Erasmus+ de Uniovi (SIES 25-26 y 26-27); un fichero por tanda: universities_convenio*.json
    for conv_file in sorted(CONFIG.parent.glob("universities_convenio*.json")):
        by_slug = {u["slug"]: u for u in unis}
        for e in json.loads(conv_file.read_text(encoding="utf-8")):
            if e["slug"] in by_slug:
                by_slug[e["slug"]]["grupos"] = sorted(set(by_slug[e["slug"]]["grupos"]) | {"convenio"})
                by_slug[e["slug"]]["erasmus_code"] = e["erasmus_code"]
                continue
            e["grupos"] = e.get("grupos") or ["convenio"]
            unis.append(e)
    # otros grados/másteres de Uniovi con destinos en común (lado Uniovi); un fichero por tanda
    for uo_file in sorted(CONFIG.parent.glob("universities_uniovi*.json")):
        for e in json.loads(uo_file.read_text(encoding="utf-8")):
            e["grupos"] = ["uniovi_epi"]
            unis.append(e)
    return [u for u in unis if grupo is None or grupo in u["grupos"]]


def uni_dir(slug: str) -> Path:
    return UNIS_DIR / slug


def safe_name(code: str) -> str:
    """Código de asignatura -> nombre de archivo estable y seguro."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", code.strip()).strip("_") or "sin_codigo"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_catalog(slug: str) -> dict | None:
    p = uni_dir(slug) / "catalogo_urls.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# ---------------------------------------------------------------- Markdown
def write_markdown(slug: str, entry: dict, body_md: str, blocks_found: dict[str, bool]) -> Path:
    """Guarda raw_markdown/{codigo}.md con cabecera de trazabilidad.

    `blocks_found` = {"contents": True, "learning_outcomes": True, "assessment": False, ...}
    lo rellena cada scraper para que el control de calidad sepa qué bloques se localizaron.
    """
    body_md = scrub_pii(body_md).strip() + "\n"
    head = {
        "course_code": entry["codigo_asignatura"],
        "course_name": entry["nombre_asignatura"],
        "institution_slug": slug,
        "source_url": entry.get("url_guia_docente"),
        "source_language": entry.get("idioma_pagina"),
        "ects_catalog": entry.get("creditos_ects"),
        "blocks_found": blocks_found,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "content_sha256": sha256(body_md),
    }
    out = uni_dir(slug) / "raw_markdown" / f"{safe_name(entry['codigo_asignatura'])}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("---\n" + json.dumps(head, ensure_ascii=False, indent=1) + "\n---\n\n" + body_md, encoding="utf-8")
    return out


def read_markdown(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    return json.loads(m.group(1)), m.group(2)


# ---------------------------------------------------------------- RGPD
# Anonimización DETERMINISTA, aplicada antes de guardar el Markdown y, por tanto,
# antes de enviar nada a una API externa (minimización de datos).
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
# Solo formas ofuscadas explícitas ([at], (at)...): un " at " suelto es inglés corriente
_EMAIL_OBF = re.compile(r"[\w.+-]+\s*(?:\[at\]|\(at\)|\[arroba\]|\(arroba\))\s*[\w-]+(?:\s*(?:\.|\[dot\]|\(dot\))\s*[\w-]+)+", re.I)
_PHONE = re.compile(r"(?<![\w/.-])(?:\+|00)?\d[\d\s()./-]{7,}\d(?![\w/-])")
# Un número solo se trata como teléfono si va precedido de una etiqueta de teléfono
# o de un prefijo internacional: así no se tocan citas, ISBN, DOI ni rangos de páginas.
_PHONE_LABEL = re.compile(r"(?:tel|tél|phone|telefon|teléfono|telefono|τηλ|fax|mobile|móvil|cell|number|número|numero)\W{0,15}$", re.I)
# Nombres de personal precedidos de tratamiento (Prof., Prof.ssa, Dr., Dott.ssa...)
_TITLED_NAME = re.compile(
    r"(?<![\w./@-])"  # no dentro de una palabra, URL o correo
    r"(?:(?i:(?:prof|conf|ș\.l|ş\.l|s\.l|lect|asist)\.\s*(?:univ\.\s*)?dr\.(?:\s*(?:ing|habil)\.)*)"  # rumano: Prof.dr.ing., Conf.univ.dr.
    r"|(?:Prof|Dr|Dott|Ing|Univ\.-Prof)\.(?:ssa)?|Dra\.|Professor(?:in)?|Profesor(?:a)?|Professore(?:ssa)?)"
    # nombre + apellido como mínimo: "Ing. Caminos" (abreviatura de un colegio profesional) no se toca
    r"\s+(?:(?:Dr|Dott|Ing)\.\s+)?(?:[A-ZÀ-ÖØ-Þ][\w'’-]*\.?\s+){1,3}[A-ZÀ-ÖØ-Þ][\w'’-]+")


def scrub_pii(text: str) -> str:
    text = _EMAIL.sub("[email]", text)
    text = _EMAIL_OBF.sub("[email]", text)
    text = _TITLED_NAME.sub("[docente]", text)

    def _phone(m: re.Match) -> str:
        s = m.group(0)
        digits = re.sub(r"\D", "", s)
        before = text[max(0, m.start() - 25):m.start()]
        if not (8 <= len(digits) <= 15):
            return s
        if s.lstrip().startswith(("+", "00")) or _PHONE_LABEL.search(before):
            return "[phone]"
        return s

    return _PHONE.sub(_phone, text)
