# ingenium_scraper

Extracción y normalización de las guías docentes de Ingeniería Mecánica (o grado equivalente) de las 10 universidades de la alianza INGENIUM. Carpeta independiente: no usa ni modifica nada del portal de convalidaciones que hay en la carpeta superior.

## Estructura

```
ingenium_scraper/
├── PROMPT_MAESTRO_v2.md      Prompt mejorado para lanzar agentes sobre este proyecto
├── orchestrator.py           Lanza las fases en paralelo y genera status_dashboard.md
├── semantic_parser.py        Fase 3: Markdown -> JSON estructurado (API externa)
├── qa_master_db.py           Fase 4: SQLite + informe de anomalías
├── status_dashboard.md       Panel de estado (generado)
├── config/universities.json  Las 10 universidades (slug, dominio, piloto sí/no)
├── common/
│   ├── http_client.py        PoliteClient: pausas 1-3 s, backoff, robots.txt, caché en disco
│   ├── schema.py             Contratos de datos (catálogo y JSON de asignatura)
│   └── util.py               write_markdown(), anonimización, rutas
├── universidades/{slug}/
│   ├── discover_{slug}.py    Fase 1 (determinista)
│   ├── catalogo_urls.json    Catálogo de asignaturas con enlace a la guía
│   ├── notas_descubrimiento.md  Cómo es la fuente; traspaso a la Fase 2
│   ├── scraper_{slug}.py     Fase 2 (determinista)  [pendiente]
│   ├── raw_cache/            Descargas en bruto (no se sube a git)
│   ├── raw_markdown/         Una guía por archivo, en Markdown limpio y anonimizado
│   ├── structured_data/      Un JSON por asignatura
│   └── logs/
├── db/ingenium_syllabi.db    Base de datos consolidada (generada)
└── reports/anomalias.md      Informe de control de calidad (generado)
```

## Cómo se usa

Desde esta carpeta:

```bash
python orchestrator.py status
```

```bash
python orchestrator.py discover --unis uniovi his hka
```

```bash
python orchestrator.py scrape --unis uniovi --sample 5
```

```bash
python orchestrator.py parse --unis uniovi --dry-run
```

```bash
python orchestrator.py consolidate
```

`scrape --all` descarga el grado completo. `parse` sin `--dry-run` llama a la API externa y cuesta dinero; antes hay que copiar `.env.example` a `.env` y poner la clave.

## Dónde interviene un LLM

| Fase | En tiempo de diseño | En ejecución |
|---|---|---|
| 1 Descubrimiento | Un agente escribe `discover_{slug}.py` | Solo Python |
| 2 Scraping | Un agente escribe y valida `scraper_{slug}.py` | Solo Python |
| 3 Extracción semántica | — | API externa, salida validada por esquema |
| 4 Consolidación y QA | — | Solo Python |

Los datos nunca pasan por el chat de un agente, así que no consumen cuota local y no pueden ser alterados por un modelo, salvo en la Fase 3, que queda registrada (modelo, fecha y hash de la fuente en cada JSON).

## Esquema del JSON de asignatura

Definido en `common/schema.py` (`SyllabusRecord`). Respecto al esquema inicial añade: `year_of_study`, `course_type`, `language_of_instruction`, `prerequisites`, `teaching_methods`, `workload_hours_total`, `workload_hours_contact`, `isced_f_code`, `missing_sections`, resultados de aprendizaje tipificados (`knowledge` / `skill` / `competence`) con su código original, y trazabilidad (`source_url`, `source_sha256`, `extracted_at`, `extractor_model`, `schema_version`). El peso de cada método de evaluación puede ser nulo cuando la guía no lo indica.
