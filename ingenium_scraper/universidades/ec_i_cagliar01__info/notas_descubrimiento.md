# ec_i_cagliar01__info — Cagliari: Laurea in Ingegneria Elettronica, Informatica e delle Telecomunicazioni, L-8, cds 70/94 (71/04 en 2025) — cubre informática y también teleco/electrónica; la ya extraída es Meccanica e Gestionale.

Ver `catalogo_urls.json > meta.notas`.

## Fase 1
- Plataforma Cineca (`coursecatalogue.cineca.it/api/v1`), idéntica a `ec_i_cagliar01`: copia parametrizada de su `discover_*.py` cambiando solo `COHORTES` (cdsCod por cohorte). Una sola cohorte por curso del A.A. publicado (ver notas).
- Resultado: 47 filas, 30 con ficha publicada, 17 sin_guia.

## Fase 2
- `scraper_ec_i_cagliar01__info.py` = scraper de `ec_i_cagliar01` sin cambios de lógica (ficha JSON -> Markdown con secciones; sin datos de docentes). `--all` ejecutado: 30 Markdown.
- Revisadas fichas pequeñas frente a la fuente (secciones General information / Contents / Reference texts / Learning objectives); sin truncados apreciables.
