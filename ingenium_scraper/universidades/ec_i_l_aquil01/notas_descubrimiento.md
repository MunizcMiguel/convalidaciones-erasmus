# ec_i_l_aquil01 — Università degli Studi dell'Aquila (Ingegneria industriale L-9, I3D/I3DR)

## Fase 1
- Fuente: catálogo Cineca `univaq.coursecatalogue.cineca.it` (API JSON `/api/v1`; robots permite). Flujo: `/corsi?anno=` -> `/corso/{coorte}/{cod}` -> `/insegnamento?...` (ver docs/PLATAFORMAS.md, entrada ec_i_ancona01).
- Cohortes combinadas (2024 (I3D) año 3, 2025 y 2026 (I3DR) años 2 y 1): solo hay syllabus del A.A. 2026/27, así que cada curso se toma de la cohorte que lo cursa en 2026/27.
- UnivAQ solo ofrece Ingegneria Meccanica como magistrale (I4M); se usa el grado de primer ciclo Ingegneria industriale (I3D hasta la cohorte 2024; I3DR 'L-9 R' desde 2025), con varios currículos (Meccanica, Chimica, Gestionale, Elettrica, Biomedica...) fundidos en una unión; ofertado 501 ECTS sobre 180. Particularidad: esta ficha usa `altri_testi_ugov` (campos ugov_etichetta_*/ugov_altri_testi_*) para 'Learning outcomes' y 'Language'; el scraper (altri_testi) lo soporta. 12 filas sin_guia (Chimica, Fisica generale II, Meccanica applicata con laboratorio, Prova finale...).
- 56 filas en el catálogo; 44 con guía (Markdown). Las filas sin_guia no tienen syllabus publicado (optativas, libre elección, tirocinio, prova finale, etc.).

## Fase 2
- `scraper_ec_i_l_aquil01.py` = plantilla Cineca (1 GET a la API por asignatura, idioma en si la versión inglesa está completa; si no, italiano). Bloques detectados también por títulos de sección propios (HEAD_PATTERNS). Profesorado eliminado.
- Muestra de 5 y `--all` revisadas contra el JSON de origen (final de cada campo presente en el Markdown; particiones idénticas fusionadas).
