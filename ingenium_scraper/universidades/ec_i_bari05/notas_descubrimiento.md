# ec_i_bari05 — Politecnico di Bari (Ingegneria Meccanica L-9, LT31/LT31-R)

## Fase 1
- Fuente: catálogo Cineca `poliba.coursecatalogue.cineca.it` (API JSON `/api/v1`; robots permite). Flujo: `/corsi?anno=` -> `/corso/{coorte}/{cod}` -> `/insegnamento?...` (ver docs/PLATAFORMAS.md, entrada ec_i_ancona01).
- Cohortes combinadas (2024 LT31 año 3, 2025 LT31-R año 2, 2026 LT31-R año 1): solo hay syllabus del A.A. 2026/27, así que cada curso se toma de la cohorte que lo cursa en 2026/27.
- Grado = Laurea in Ingegneria Meccanica (LT31 'D.M. 270/04' hasta la cohorte 2024; LT31-R 'L-9 R' desde 2025). ECTS 180; ofertados 171 (año 3 con solo 4 asignaturas con guía: tirocinio, prova finale, inglés y Meccanica razionale sin syllabus). Muchas fichas del año 1 (cursos de 'base' compartidos) son largas porque agregan varios grupos/docentes.
- 23 filas en el catálogo; 19 con guía (Markdown). Las filas sin_guia no tienen syllabus publicado (optativas, libre elección, tirocinio, prova finale, etc.).

## Fase 2
- `scraper_ec_i_bari05.py` = plantilla Cineca (1 GET a la API por asignatura, idioma en si la versión inglesa está completa; si no, italiano). Bloques detectados también por títulos de sección propios (HEAD_PATTERNS). Profesorado eliminado.
- Muestra de 5 y `--all` revisadas contra el JSON de origen (final de cada campo presente en el Markdown; particiones idénticas fusionadas).
