# ec_i_salerno01__info — Salerno: Laurea in Ingegneria Informatica, L-8, cds 06127/IE127 — 2.ª titulación (informática); la ya extraída es Meccanica.

Ver `catalogo_urls.json > meta.notas`.

## Fase 1
- Plataforma Cineca (`coursecatalogue.cineca.it/api/v1`), idéntica a `ec_i_salerno01`: copia parametrizada de su `discover_*.py` cambiando solo `COHORTES` (cdsCod por cohorte). Una sola cohorte por curso del A.A. publicado (ver notas).
- Resultado: 37 filas, 6 con ficha publicada, 31 sin_guia.

## Fase 2
- `scraper_ec_i_salerno01__info.py` = scraper de `ec_i_salerno01` sin cambios de lógica (ficha JSON -> Markdown con secciones; sin datos de docentes). `--all` ejecutado: 6 Markdown.
- Revisadas fichas pequeñas frente a la fuente (secciones General information / Contents / Reference texts / Learning objectives); sin truncados apreciables.
