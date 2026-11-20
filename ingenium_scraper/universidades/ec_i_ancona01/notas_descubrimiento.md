# ec_i_ancona01 — Università Politecnica delle Marche (Ingegneria Meccanica, L-9)

## Fase 1
- Titulación: Laurea in Ingegneria Meccanica (L-9). Hay dos códigos Cineca: IT05 (cohortes hasta 2024) e IT25 (L-9 R, cohortes 2025-26, mismo plan reformado). Magistrale IM29 descartada.
- Fuente: catálogo Cineca `univpm.coursecatalogue.cineca.it` (API JSON `/api/v1`, robots permite). Mismo flujo que unich: `/corsi?anno=` -> `/corso/{coorte}/{cod}` -> `/insegnamento?...`.
- Trampa: solo hay syllabus del A.A. 2026/27 (los anteriores devuelven vacío). Cada curso 1-3 sale de la cohorte que cursa ese año en 2026/27: año 1 = cohorte 2026 (IT25), año 2 = 2025 (IT25), año 3 = 2024 (IT05). Se omiten grupos 'revisione 2026' / 'offerti da altri corsi' (duplicados).
- El año de cada actividad no viene en la actividad (`annoCorso` ausente): se toma de `anni[].anno`.
- ECTS: 180; 22 de las 37 filas tienen guía; las 15 sin_guia son optativas (OL) y lenguas sin syllabus publicado, y OFA (0 ECTS).
- Idioma: ficha en inglés cuando está completa (19), si no italiano.

## Fase 2
- `scraper_ec_i_ancona01.py` = scraper_unich adaptado (1 GET a la API por asignatura). Muchas fichas de Ancona usan secciones propias (`altri_testi`: 'LEARNING OUTCOMES - ...', 'DEVELOPMENT OF THE EXAMINATION - ...'), por eso los bloques se detectan también por el título de sección (HEAD_PATTERNS).
- Muestra de 5 y `--all` (22 ficheros) revisados: sin texto perdido (se comprobó que el final de cada campo fuente está en el Markdown); particiones pares/impares idénticas se fusionan. Profesorado eliminado (redact_staff).
