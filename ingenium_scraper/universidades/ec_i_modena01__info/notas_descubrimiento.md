# ec_i_modena01__info — Unimore: Laurea in Ingegneria Informatica (MO), L-8, cdsCod 20-212/20-312 — 2.ª titulación afín (informática) de Modena; la ya extraída es Ingegneria Elettronica.

Ver `catalogo_urls.json > meta.notas`.

## Fase 1
- Plataforma Cineca (`coursecatalogue.cineca.it/api/v1`), idéntica a `ec_i_modena01`: copia parametrizada de su `discover_*.py` cambiando solo `COHORTES` (cdsCod por cohorte). Una sola cohorte por curso del A.A. publicado (ver notas).
- Resultado: 31 filas, 20 con ficha publicada, 11 sin_guia.

## Fase 2
- `scraper_ec_i_modena01__info.py` = scraper de `ec_i_modena01` sin cambios de lógica (ficha JSON -> Markdown con secciones; sin datos de docentes). `--all` ejecutado: 20 Markdown.
- Revisadas fichas pequeñas frente a la fuente (secciones General information / Contents / Reference texts / Learning objectives); sin truncados apreciables.
