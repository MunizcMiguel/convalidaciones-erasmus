# ec_i_modena01 — Università Modena e Reggio Emilia: Ingegneria Elettronica (L-8)

Ver `catalogo_urls.json > meta.notas` (titulación elegida y justificación).

## Fase 1
- Fuente: catálogo Cineca `unimore.coursecatalogue.cineca.it` (API JSON pública `/api/v1`, robots permite; mismo flujo que `ec_i_ancona01`): `corsi?anno=` → `corso/{coorte}/{cod}` → `insegnamento`.
- Se combinan las cohortes 2024 (año 3), 2025 (año 2) y 2026 (año 1) porque solo hay syllabus del A.A. 2026/27. Cambio de `cdsCod` entre ordenamientos antiguo/nuevo documentado en meta.notas.
- Trampa: parámetro `af_percorso` del endpoint `insegnamento`: en Pavia/Modena `af_percorso_id` vale 9999 y da 404; hay que usar `corso_percorso_id`. En Sannio sirve `af_percorso_id`. Las fichas 404 se tratan como `sin_guia`.
- Resultado: 32 filas (15 con ficha). Códigos = adCod de Esse3.

## Fase 2
- `scraper_ec_i_modena01.py` (plantilla Cineca de Ancona): ficha JSON → Markdown con secciones; idioma `en` si la versión inglesa está completa, si no `it`. Sin datos de docentes.
- `--sample 5` revisado frente a la ficha; `--all` ejecutado; las filas sin ficha publicada se omiten (sin_guia).
