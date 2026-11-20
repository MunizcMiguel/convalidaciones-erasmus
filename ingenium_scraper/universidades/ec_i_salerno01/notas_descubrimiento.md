# ec_i_salerno01 — Università degli Studi di Salerno (Ingegneria Meccanica L-9, 06123/II123)

## Fase 1
- Fuente: catálogo Cineca `unisa.coursecatalogue.cineca.it` (API JSON `/api/v1`; robots permite). Flujo: `/corsi?anno=` -> `/corso/{coorte}/{cod}` -> `/insegnamento?...` (ver docs/PLATAFORMAS.md, entrada ec_i_ancona01).
- Cohortes combinadas (2024 (06123) año 3, 2025 (II123) año 2, 2026 (II123) año 1): solo hay syllabus del A.A. 2026/27, así que cada curso se toma de la cohorte que lo cursa en 2026/27.
- Grado = Laurea in Ingegneria Meccanica (06123 hasta la cohorte 2024; II123 'L-9 R' desde 2025). Códigos oficiales: II123xxxxx (plan nuevo, años 1-2) y 06123xxxxx/06126xxxxx (plan anterior, año 3). ECTS 180; ofertados 210 (el año 3 incluye optativas a elegir). Sin ficha: Statistica per l'ingegneria, Disegno, Ricerca operativa.
- 31 filas en el catálogo; 28 con guía (Markdown). Las filas sin_guia no tienen syllabus publicado (optativas, libre elección, tirocinio, prova finale, etc.).

## Fase 2
- `scraper_ec_i_salerno01.py` = plantilla Cineca (1 GET a la API por asignatura, idioma en si la versión inglesa está completa; si no, italiano). Bloques detectados también por títulos de sección propios (HEAD_PATTERNS). Profesorado eliminado.
- Muestra de 5 y `--all` revisadas contra el JSON de origen (final de cada campo presente en el Markdown; particiones idénticas fusionadas).
