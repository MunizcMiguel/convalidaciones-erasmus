# ec_i_trento01 — Università degli Studi di Trento (Ingegneria industriale L-9, 0327G/0528G)

## Fase 1
- Fuente: catálogo Cineca `unitn.coursecatalogue.cineca.it` (API JSON `/api/v1`; robots permite). Flujo: `/corsi?anno=` -> `/corso/{coorte}/{cod}` -> `/insegnamento?...` (ver docs/PLATAFORMAS.md, entrada ec_i_ancona01).
- Cohortes combinadas (2024 (0327G) año 3, 2025 y 2026 (0528G) años 2 y 1): solo hay syllabus del A.A. 2026/27, así que cada curso se toma de la cohorte que lo cursa en 2026/27.
- UniTrento no tiene Ingegneria Meccanica triennale: se usa Ingegneria industriale (L-9) con sus tres currículos (Gestionale, Materiali per l'industria sostenibile, Robotica e meccatronica). Catálogo PARCIAL: ninguna asignatura del año 1 (cohorte 2026) tiene ficha publicada en el catálogo y varias del 2-3 tampoco (22 de 50 sin_guia: Fisica, Analisi, Disegno industriale, Sistemi meccanici e modelli, Tecnica delle costruzioni meccaniche...). Ya se eliminan líneas de horarios de tutoría y contactos.
- 50 filas en el catálogo; 28 con guía (Markdown). Las filas sin_guia no tienen syllabus publicado (optativas, libre elección, tirocinio, prova finale, etc.).

## Fase 2
- `scraper_ec_i_trento01.py` = plantilla Cineca (1 GET a la API por asignatura, idioma en si la versión inglesa está completa; si no, italiano). Bloques detectados también por títulos de sección propios (HEAD_PATTERNS). Profesorado eliminado.
- Muestra de 5 y `--all` revisadas contra el JSON de origen (final de cada campo presente en el Markdown; particiones idénticas fusionadas).

## Segunda pasada
- Mismo fallback (anno 2025 y 2024 si el 2026 da 404): ninguna de las 22 filas sin_guia tiene ficha en años anteriores. Sigue 28 con guía / 22 sin_guia.
