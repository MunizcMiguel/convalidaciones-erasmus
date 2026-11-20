# Worker brief — Spanish universities (addendum)

Read `docs/BRIEF_FASES_1_2.md` first: it is the full brief (deliverables, stop rule, validation, report). This file adds what is specific to the Spanish wave. Where they differ, this file wins.

## Target

The degree is fixed: **Grado en Ingeniería Mecánica** as registered in the RUCT. Your university's entry in `config/universities_es.json` (find it by slug) gives the official title, the teaching centres and the official credit breakdown (formación básica / obligatorios / optativos / prácticas / TFG / total). Use it:

- If the degree is taught at several centres, take the first-listed main centre and name the others in `meta.notas`.
- If the entry lists two titles (an older RD 1393/2007 plan and a newer RD 822/2021 one), take the plan currently admitting new students and say which.
- Validate your catalog against the official credit breakdown and explain any difference in `meta.notas`.

## Reuse before you write

Spanish universities share a handful of syllabus platforms. Before writing a scraper, read `docs/PLATAFORMAS.md`. If your university's guides are served by a platform already listed there, start from the reference scraper named in that entry (copy it into your folder and adapt it) instead of writing a new one. When you finish, append ONE entry to `docs/PLATAFORMAS.md` for your university: platform or vendor if identifiable, hosts, URL pattern for a course guide, source type (JSON API / HTML / PDF per course / shared PDF), and the path of your scraper. Append only; do not edit other entries. That file is the one exception to "write only inside your folder".

## Spanish specifics

- Language: take the Spanish (castellano) version of the guide. If a course is published only in Catalan, Galician or Basque, take that and record the language per row. Ignore English versions unless Spanish is missing.
- Guides nearly always include "Profesorado", "Coordinador/a", "Tutorías" or "Datos del profesorado" sections with names, emails, offices and office hours: drop those sections entirely.
- Use the current academic year (2026-27) if its guides are published; otherwise the most recent year that is, and say so.
- Typical section names to map to the five blocks: Contenidos / Temario / Programa (contents); Competencias y resultados de aprendizaje (learning_outcomes); Evaluación / Sistema de evaluación (assessment); Bibliografía (bibliography); Requisitos / Conocimientos previos / Recomendaciones (prerequisites).

## Working economically

Your context is limited and so is the user's usage budget. Do not print whole HTML pages, PDFs or JSON dumps into the conversation: inspect them with short Python snippets that print only what you need (a list of headings, the first 40 lines, the keys of a JSON object). Keep exploration focused: once you have found the source, stop exploring and write the script.

## Report back (max 150 words)

Centre and plan chosen; courses in catalog; ECTS vs the RUCT breakdown; platform and hosts with their robots.txt verdict; Markdown files written out of catalog rows; blocks commonly missing; anything not verified.

## Robots.txt: ahora lo aplica el cliente

`PoliteClient` entiende los comodines de robots.txt (`*`, `$`), comprueba cada redirección y respeta `Crawl-delay`. Si lanza `RobotsBlocked`, el servidor no admite el acceso automatizado a esa ruta: es una parada (aplica la regla de parada del brief), no algo que reintentar, rodear ni saltar con otro cliente HTTP. Usa siempre `PoliteClient` para hablar con servidores de universidades.

## Si retomas el trabajo de otro agente

Un agente anterior pudo quedarse a medias por un límite de uso. Mira primero qué hay en `universidades/{slug}/` (catálogo, scripts, notas, caché y Markdown ya generados), reutilízalo, borra ficheros de prueba sueltos (`_x.py`, `_tmp`...) y continúa desde ahí en lugar de empezar de cero.
