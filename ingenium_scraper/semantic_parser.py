#!/usr/bin/env python3
"""Fase 3 · Extractor semántico (API externa, fuera del chat del agente).

Lee universidades/{slug}/raw_markdown/*.md, llama a la API de Google Gemini con salida
estructurada (JSON validado contra common.schema.SyllabusExtraction) y escribe
universidades/{slug}/structured_data/{codigo}.json.

Ahorro de tokens:
  - Caché por hash: si el Markdown no ha cambiado (mismo sha256, mismo modelo y
    misma versión de esquema), NO se vuelve a llamar a la API.
  - El Markdown ya llega anonimizado (emails/teléfonos) desde la Fase 2.
  - --dry-run estima el volumen antes de gastar nada; --limit prueba con pocas.

Uso:
    python semantic_parser.py --unis uniovi his hka --dry-run
    python semantic_parser.py --unis uniovi --limit 5
    python semantic_parser.py --all

Variables de entorno (.env): LLM_API_KEY (obligatoria), LLM_MODEL, LLM_CONCURRENCY.
"""
from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from common.schema import SyllabusExtraction, SyllabusRecord
from common.util import ROOT, load_catalog, read_markdown, safe_name, uni_dir, universities

SCHEMA_VERSION = "1.1"
DEFAULT_MODEL = "gemini-2.5-flash"  # cámbialo en .env (LLM_MODEL); `--list-models` muestra los disponibles para tu clave

SYSTEM_PROMPT = """You extract structured data from university course syllabi (course guides, module descriptions) for an Erasmus+ course-equivalence database. The reader of your output is a matching engine that compares courses across universities, so faithful, comparable content matters more than polish.

The syllabus arrives as Markdown in its original language (Spanish, Swedish, German, French, Italian, Greek, Romanian, Bulgarian, Finnish or English). Write every extracted field in English, except course_name_original, which keeps the original title verbatim.

How to fill the fields:
- course_name_original: the course title exactly as written, without the course code.
- learning_outcomes: one entry per outcome, translated faithfully. Classify type as knowledge, skill or competence when the text makes it clear, otherwise unspecified. Keep the original competence code (e.g. CE12, RA3) in `code` when there is one.
- syllabus_topics: the taught content, taken only from the syllabus's contents section (not from the learning outcomes), translated into English, as a flat list in the order given, one topic or unit per entry. When the contents are written as prose, list the topics the prose names. Keep technical specificity ("Mohr's circle for plane stress", not "stress analysis basics").
- assessment_methods: each assessed component with its weight in percent. Give a weight when the syllabus states it or when it follows unambiguously from a stated formula (0.4·A + 0.6·B gives 40 and 60). When the weighting is conditional (max/min of alternatives, different paths) or not given, use null — do not distribute 100% yourself.
- assessment_rules: the grading formula, minimum marks and resit arrangements as stated, condensed into at most four sentences (the formula and the key conditions, not every procedural detail); null if the syllabus gives none.
- prerequisites: required or recommended prior courses or knowledge.
- teaching_methods: lectures, labs, seminars, project work, etc.
- workload_hours_total / workload_hours_contact: only if stated.
- language_of_instruction: ISO 639-1 codes, only if stated or unambiguous.
- bibliography: one reference per entry, as given (authors of textbooks are bibliographic data and stay).
- isced_f_code: the 4-digit ISCED-F 2013 detailed field code only (e.g. "0715" for mechanics and metal trades, "0541" for mathematics), or null if unclear.
- missing_sections: name any of these blocks that the syllabus does not contain: learning_outcomes, syllabus_topics, assessment_methods, bibliography, prerequisites.

Only report what the syllabus says. When a piece of information is absent, use null or an empty list and list the block in missing_sections; an honest gap is useful to the reviewers, an invented value corrupts the comparison.

Privacy (GDPR): the output must contain no names of lecturers, coordinators or staff, and no email addresses, phone numbers or office locations. Leave them out entirely."""


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))  # admite valores entre comillas


def pending_jobs(slugs: list[str], model: str, limit: int | None) -> list[dict]:
    names = {u["slug"]: u["name"] for u in universities()}
    jobs = []
    for slug in slugs:
        cat = load_catalog(slug)
        if not cat:
            continue
        by_file = {safe_name(a["codigo_asignatura"]): a for a in cat["asignaturas"]}
        n = 0
        for md in sorted((uni_dir(slug) / "raw_markdown").glob("*.md")):
            head, body = read_markdown(md)
            out = uni_dir(slug) / "structured_data" / (md.stem + ".json")
            if out.exists():
                old = json.loads(out.read_text(encoding="utf-8"))
                if (old.get("source_sha256") == head.get("content_sha256")
                        and old.get("extractor_model") == model and old.get("schema_version") == SCHEMA_VERSION):
                    continue  # caché: nada ha cambiado
            jobs.append({"slug": slug, "institution": names[slug], "meta": cat["meta"],
                         "entry": by_file.get(md.stem, {}), "head": head, "body": body, "out": out})
            n += 1
            if limit and n >= limit:
                break
    return jobs


async def extract_one(client, model: str, job: dict, sem: asyncio.Semaphore) -> tuple[bool, str]:
    from google.genai import errors, types

    entry, head = job["entry"], job["head"]
    user = (f"Institution: {job['institution']}\nDegree: {job['meta'].get('nombre_grado', '')}\n"
            f"Course code: {head.get('course_code', '')}\nCatalogue ECTS: {head.get('ects_catalog')}\n\n"
            f"<syllabus>\n{job['body']}\n</syllabus>")
    async with sem:
        try:
            resp = await client.aio.models.generate_content(
                model=model,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=SyllabusExtraction,  # salida estructurada validada por esquema
                    max_output_tokens=16000,
                    # extracción guiada por esquema: el "razonamiento" interno no aporta y se factura como salida
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
        except errors.ClientError as e:   # 4xx: clave inválida, modelo inexistente, cuota (429)...
            return False, f"API {e.code}: {e.message}"
        except errors.ServerError as e:   # 5xx tras agotar los reintentos del SDK
            return False, f"servidor {e.code}: {e.message}"
        except errors.APIError as e:
            return False, f"API: {e.message}"
    cand = resp.candidates[0] if resp.candidates else None
    finish = getattr(getattr(cand, "finish_reason", None), "name", "SIN_RESPUESTA")
    if cand is None or finish != "STOP":
        return False, f"salida no válida (finish_reason={finish})"
    try:
        parsed = resp.parsed if isinstance(resp.parsed, SyllabusExtraction) else SyllabusExtraction.model_validate_json(resp.text)
    except ValueError as e:
        return False, f"JSON no conforme al esquema: {str(e).splitlines()[0]}"
    record = SyllabusRecord(
        **parsed.model_dump(),
        institution=job["institution"], institution_slug=job["slug"],
        degree=job["meta"].get("nombre_grado", ""),
        course_code=head.get("course_code") or entry.get("codigo_asignatura", job["out"].stem),
        academic_year=job["meta"].get("curso_academico", ""),
        source_url=head.get("source_url"), source_language=head.get("source_language") or "",
        source_sha256=head.get("content_sha256", ""),
        extracted_at=time.strftime("%Y-%m-%dT%H:%M:%S"), extractor_model=model, schema_version=SCHEMA_VERSION,
    )
    job["out"].parent.mkdir(parents=True, exist_ok=True)
    job["out"].write_text(json.dumps(record.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    u = resp.usage_metadata
    return True, f"in={u.prompt_token_count} out={u.candidates_token_count}"


def make_client():
    from google import genai
    from google.genai import types

    # El SDK reintenta 429/5xx con exponential backoff
    return genai.Client(api_key=os.environ["LLM_API_KEY"],
                        http_options=types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=5)))


async def run(jobs: list[dict], model: str, concurrency: int) -> int:
    client = make_client()
    sem = asyncio.Semaphore(concurrency)
    errors_log = ROOT / "reports" / "semantic_parser_errors.jsonl"
    errors_log.parent.mkdir(exist_ok=True)
    fails = 0

    async def one(job):
        nonlocal fails
        ok, info = await extract_one(client, model, job, sem)
        tag = f"{job['slug']}/{job['out'].stem}"
        if ok:
            print(f"  ok   {tag}  {info}")
        else:
            fails += 1
            print(f"  FAIL {tag}  {info}")
            with errors_log.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"course": tag, "error": info, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}, ensure_ascii=False) + "\n")

    await asyncio.gather(*(one(j) for j in jobs))
    return fails


def main() -> int:
    load_env()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--unis", nargs="*", help="slugs (por defecto: ninguno; usa --all)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--limit", type=int, help="máximo de asignaturas por universidad (para pruebas)")
    ap.add_argument("--list-models", action="store_true", help="lista los modelos disponibles para tu clave y termina")
    ap.add_argument("--dry-run", action="store_true", help="no llama a la API; muestra el volumen pendiente")
    a = ap.parse_args()
    if a.list_models:
        if not os.environ.get("LLM_API_KEY"):
            print("Falta LLM_API_KEY (ponla en .env)", file=sys.stderr)
            return 2
        client = make_client()  # mantener la referencia: si se libera, el SDK cierra la conexión
        for m in client.models.list():
            if "generateContent" in (m.supported_actions or []):
                print(m.name)
        return 0
    slugs = [u["slug"] for u in universities()] if a.all else (a.unis or [])
    if not slugs:
        ap.error("indica --unis ... o --all")
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    jobs = pending_jobs(slugs, model, a.limit)
    chars = sum(len(j["body"]) for j in jobs)
    print(f"Modelo: {model} | pendientes: {len(jobs)} guías | ~{chars // 3:,} tokens de entrada (estimación burda: 3 caracteres/token)")
    if a.dry_run or not jobs:
        return 0
    if not os.environ.get("LLM_API_KEY"):
        print("Falta LLM_API_KEY (ponla en .env)", file=sys.stderr)
        return 2
    fails = asyncio.run(run(jobs, model, int(os.environ.get("LLM_CONCURRENCY", "4"))))
    print(f"Terminado: {len(jobs) - fails} ok, {fails} con error")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
