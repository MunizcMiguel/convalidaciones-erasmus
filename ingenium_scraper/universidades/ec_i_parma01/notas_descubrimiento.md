# ec_i_parma01 — Università degli Studi di Parma

**Titulación:** Laurea (triennale, L-9) in Ingegneria Meccanica, Dip. DISTI. CdS 3011 (cohortes 2023/2024) + CdS 3111 (ordenamiento 2025, 1.er curso). El CdS 5016 (misma denominación) parece la Magistrale (LM-33): descartado; **deducido de los datos, no confirmado en la web**.

## Fase 1
- Fuente: Excel oficial "Offerta Formativa 2025-2026" (hoja "Insegnamenti e coperture"), ya exportado a JSON por el usuario; `prepare_fuente_previa.py` lo filtra a 3011/3111 y elimina datos de profesorado → `fuente_previa/`.
- **Bloqueo:** `corsi.unipr.it` (robots.txt y fichas) devuelve HTTP 405 a PoliteClient (filtro por User-Agent). Regla de parada: no se rodea. El usuario había descargado antes las fichas con otro cliente; se reutilizan tal cual (no se vuelven a descargar).
- Catálogo `parcial`: 50 asignaturas únicas (por código) de las ofertadas en 2025/26 (1.º: 6, 2.º: 12, 3.º: 32); NO es el plan completo de 180 ECTS (el Excel solo lista cursos con cobertura, mezclando curricula 261/398/399/GEN). 39 tienen ficha; 11 `sin_guia` (la ficha no tiene contenido).
- URL de ficha: `https://corsi.unipr.it/en/ugov/degreecourse/{id}` (id interno del insegnamento; el mismo código tiene ids distintos por curriculum: se elige el que tiene ficha).
- Idioma de la ficha: inglés (versión EN del portal; muchas secciones conservan texto italiano). Idioma de docencia mayoritariamente italiano.

## Fase 2
- `scraper_ec_i_parma01.py` no usa red: convierte `fuente_previa/unipr_fichas.json` en Markdown (secciones Learning objectives, Prerequisites, Course unit content, Full programme, Teaching methods, Assessment, Bibliography). 39/39 escritos. Sin profesorado.
- Las listas con viñetas del origen llegan aplastadas en un párrafo (limitación de la extracción previa).
