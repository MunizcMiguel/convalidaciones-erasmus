# ec_i_firenze01 — Università degli Studi di Firenze (Ingegneria Meccanica L-9, B049/B309)

## Fase 1
- Fuente: catálogo Cineca `unifi.coursecatalogue.cineca.it` (API JSON `/api/v1`; robots permite). Flujo: `/corsi?anno=` -> `/corso/{coorte}/{cod}` -> `/insegnamento?...` (ver docs/PLATAFORMAS.md, entrada ec_i_ancona01).
- Cohortes combinadas (2024 B049 año 3, 2025 B309 año 2, 2026 B309 año 1): solo hay syllabus del A.A. 2026/27, así que cada curso se toma de la cohorte que lo cursa en 2026/27.
- Grado = Laurea in Ingegneria Meccanica (B049 hasta la cohorte 2024; B309 'L-9 R' desde 2025). Hay 6 currículos (Energia, Meccanico, Robotico e Automatico/Elettrico; formativo/applicativo): el catálogo es la unión y una asignatura presente en varios currículos con los mismos créditos se funde en una sola fila (la columna curso_semestre lista los currículos). Ofertado 390 ECTS sobre 180 del plan (cada currículo tiene su propio conjunto de optativas). El año 1 tiene pocas fichas publicadas (7 de 9). Mayoría de fichas en inglés. Se eliminan líneas 'Orario di ricevimento' y emails que aparecen en 'Altre informazioni'.
- 56 filas en el catálogo; 47 con guía (Markdown). Las filas sin_guia no tienen syllabus publicado (optativas, libre elección, tirocinio, prova finale, etc.).

## Fase 2
- `scraper_ec_i_firenze01.py` = plantilla Cineca (1 GET a la API por asignatura, idioma en si la versión inglesa está completa; si no, italiano). Bloques detectados también por títulos de sección propios (HEAD_PATTERNS). Profesorado eliminado.
- Muestra de 5 y `--all` revisadas contra el JSON de origen (final de cada campo presente en el Markdown; particiones idénticas fusionadas).
