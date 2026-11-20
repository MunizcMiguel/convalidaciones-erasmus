# ec_i_beneven02__info — Sannio: Laurea in Ingegneria Informatica, L-8, cdsCod 863/800 — 2.ª titulación (informática) de Sannio; la ya extraída es Elettronica e Biomedica.

Ver `catalogo_urls.json > meta.notas`.

## Fase 1
- Plataforma Cineca (`coursecatalogue.cineca.it/api/v1`), idéntica a `ec_i_beneven02`: copia parametrizada de su `discover_*.py` cambiando solo `COHORTES` (cdsCod por cohorte). Una sola cohorte por curso del A.A. publicado (ver notas).
- Resultado: 30 filas, 24 con ficha publicada, 6 sin_guia.

## Fase 2
- `scraper_ec_i_beneven02__info.py` = scraper de `ec_i_beneven02` sin cambios de lógica (ficha JSON -> Markdown con secciones; sin datos de docentes). `--all` ejecutado: 24 Markdown.
- Revisadas fichas pequeñas frente a la fuente (secciones General information / Contents / Reference texts / Learning objectives); sin truncados apreciables.
