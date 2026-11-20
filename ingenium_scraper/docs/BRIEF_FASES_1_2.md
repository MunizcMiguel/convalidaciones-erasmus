# Worker brief — Phases 1 and 2 for one university

You are the Discovery (Phase 1) and Scraper Builder (Phase 2) worker for ONE university of the INGENIUM alliance, in an academic research project that builds a database of course syllabi to support Erasmus+ course-equivalence decisions. Your university, its slug and the target degree are given in your task message.

Project root: `F:\000. Desarrollo Apps\700. ERASMUS\ingenium_scraper` (bash: `/f/000. Desarrollo Apps/700. ERASMUS/ingenium_scraper`). Write ONLY inside `universidades/{slug}/`.

## Read first

- `common/http_client.py` — `PoliteClient`: 1–3 s pauses per host, exponential backoff, robots.txt-aware, disk cache. ALL network access in your scripts goes through it with `cache_dir=Path(__file__).parent / "raw_cache"`.
- `common/schema.py` — `Catalog`, `CatalogMeta`, `CatalogEntry`: the catalog contract.
- `common/util.py` — `write_markdown(slug, entry, body_md, blocks_found)`, `REQUIRED_BLOCKS`, `load_catalog`, `read_markdown`.
- Worked examples: `universidades/uniovi/` (HTML source) and `universidades/hka/` (one shared PDF): their `discover_*.py`, `scraper_*.py` and `notas_descubrimiento.md`.

## Stop rule — check before fetching any content

Check robots.txt of EVERY host involved: the programme pages and wherever the syllabi are actually served (often a different host: a PDF proxy, a course-catalogue platform). Two universities in this project were blocked this way (one by a `Disallow: /` robots.txt on the PDF host, one by a 403 bot filter on the catalogue platform). If the host serving the syllabi disallows or refuses automated access: do Phase 1 as far as allowed, set the catalog `estado: "parcial"`, do not fetch from that host, skip Phase 2 and report. No logins, no browser-User-Agent spoofing, no circumventing blocks. Use only PoliteClient for requests to university hosts (no curl / raw requests).

If the university offers no engineering degree at all, write a catalog with `estado: "n/a"`, an empty `asignaturas` list and the explanation in `meta.notas`, and report.

## Phase 1 — Discovery

Deliver in `universidades/{slug}/`:

1. `discover_{slug}.py` — deterministic; starts with `sys.path.insert(0, str(Path(__file__).resolve().parents[2]))`; parses the official study-plan source; builds and validates a `Catalog`; writes `catalogo_urls.json` (UTF-8, indent 2, `ensure_ascii=False`, `catalog.model_dump()`). Runnable from the project root as `python universidades/{slug}/discover_{slug}.py`; re-running hits only the cache.
2. `catalogo_urls.json`.
3. `notas_descubrimiento.md` — source used and why, URL patterns, how a syllabus is structured, traps.

Criteria:

- Target degree: first-cycle (bachelor-level) Mechanical Engineering. If it does not exist, choose the closest first-cycle engineering/technology degree, and say which and why. One degree only.
- Every catalog row comes from parsed source data. Never hand-type codes, names, credits or URLs. If the source has no official course code, derive a stable key deterministically and document how.
- Prefer the most structured source: API/JSON behind the site, exports, then study-plan or module-handbook PDFs, and DOM scraping last. If the site is a JS SPA, look for its JSON endpoints before resorting to Playwright (installed; last resort).
- Prefer an official English version of the syllabi when it exists and is complete; otherwise the local language. Record the language per row.
- If all courses live in one PDF: `tipo_fuente: "pdf_compartido"`, PDF URL in `url_guia_docente`, page range in `paginas_pdf` ("ini-fin", 1-indexed), derived by the script.
- Verify: no duplicate codes; ECTS sum consistent with the degree total (explain electives/tracks); every row has a URL or `tipo_fuente: "sin_guia"`.

## Phase 2 — Scraper (only if the stop rule did not trigger)

Deliver `universidades/{slug}/scraper_{slug}.py`:

- CLI `--sample N` (default 5), `--all`, `--codes C1 C2 ...`. `--sample` picks a fixed, DIVERSE set defined in the script (different years, a maths/science course, a core engineering course, an elective, the final thesis/project) — atypical syllabi are what break parsing.
- For each course: fetch the syllabus and convert it to Markdown that keeps structure (a heading per section, lists as lists, tables as tables — assessment tables must keep their percentages) and drops navigation, menus, headers and footers. Keep the original language; translation happens later.
- Save with `write_markdown`, passing `blocks_found` booleans for `contents`, `learning_outcomes`, `assessment`, `bibliography`, `prerequisites`.
- Skip `sin_guia` rows; print one line per course (ok / reason); exit non-zero if any failed; re-running hits only the cache.
- Privacy: `write_markdown` already strips emails and phone numbers. Also leave out names of lecturers, coordinators and staff (drop those fields/sections). Authors in the bibliography stay.

Validate — this is the important part: run `--sample 5`, then open each Markdown file and compare it against the source: nothing truncated, no section lost or merged into its neighbour, tables intact, no page chrome. Exit code 0 is not enough; fix and re-run until all 5 are faithful. A block truly absent in the source is a fact to report (set it false), not a failure.

Then, and only once the sample is faithful, run `--all` (the user has approved full runs). Afterwards spot-check 3 more files chosen from the ones that look most unusual (smallest, largest, missing blocks) and fix the script if they reveal a parsing problem. If the server starts answering 403/429 persistently during the full run, stop and report.

Append a "Fase 2" section to `notas_descubrimiento.md`.

## Environment

`python` is on PATH (3.11; httpx, bs4, lxml, pdfplumber, pypdf, pydantic, playwright available). You may use web search / web fetch to locate the right pages, but the final scripts must fetch everything themselves through PoliteClient. Do not leave temp files outside your folder.

## Report back (max 200 words)

Degree chosen (and why, if not Mechanical Engineering); number of courses; ECTS sum vs degree total; source strategy; hosts and their robots.txt verdict; how many Markdown files were written out of how many catalog rows; which blocks are commonly missing; language; anything you could not verify.
