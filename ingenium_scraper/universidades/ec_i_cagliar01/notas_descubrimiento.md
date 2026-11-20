# ec_i_cagliar01 — Università degli Studi di Cagliari (Ingegneria Meccanica e Gestionale L-9, 70/98 y 71/08)

## Fase 1
- Fuente: catálogo Cineca `unica.coursecatalogue.cineca.it` (API JSON `/api/v1`; robots permite). Flujo: `/corsi?anno=` -> `/corso/{coorte}/{cod}` -> `/insegnamento?...` (ver docs/PLATAFORMAS.md, entrada ec_i_ancona01).
- Cohortes combinadas (2023 y 2024 (70/98) y 2025 (71/08), A.A. 2025/26): solo hay syllabus del A.A. 2026/27, así que cada curso se toma de la cohorte que lo cursa en 2026/27.
- UniCA no tiene grado puro de Mecánica: se usa Ingegneria Meccanica e Gestionale (currículos Meccanica y Gestionale, ambos incluidos). Catálogo PARCIAL: el endpoint /insegnamento devuelve 404 para el A.A. 2026/27 y para casi todas las fichas del A.A. 2025/26 de los años 1-2 (nueva ordinamento 2025, ficha no publicada); solo 12 de 32 asignaturas tienen syllabus (sobre todo año 3 y algunas de año 2). Ficha en inglés casi siempre. Una guía 404 se trata como sin_guia.
- 32 filas en el catálogo; 12 con guía (Markdown). Las filas sin_guia no tienen syllabus publicado (optativas, libre elección, tirocinio, prova finale, etc.).

## Fase 2
- `scraper_ec_i_cagliar01.py` = plantilla Cineca (1 GET a la API por asignatura, idioma en si la versión inglesa está completa; si no, italiano). Bloques detectados también por títulos de sección propios (HEAD_PATTERNS). Profesorado eliminado.
- Muestra de 5 y `--all` revisadas contra el JSON de origen (final de cada campo presente en el Markdown; particiones idénticas fusionadas).

## Segunda pasada
- Fallback en discover: si `/insegnamento` del A.A. 2025/26 da 404, se prueba el mismo curso con `anno` 2024 y 2023. Recuperadas 5 fichas del A.A. 2024/25 (70/0050-M, 70/0053-M, 70/0086-M, IN/0091, IN/0188; el Markdown indica «Anno accademico di erogazione: 2024/2025»). Ahora 17 con guía y 15 sin_guia (de 32). Resto (Chimica, Fisica 1/2, Meccanica applicata…) sin ficha publicada en ningún A.A.
