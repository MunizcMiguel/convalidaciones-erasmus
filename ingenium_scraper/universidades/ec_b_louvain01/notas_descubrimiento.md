# Notas de descubrimiento - ec_b_louvain01

- Universidad: Université catholique de Louvain (UCLouvain)
- Titulación: Bachelor in Engineering (Bachelier en sciences de l'ingénieur, orientation ingénieur civil) - FSA1BA (nivel bachelor, estado `ok`)
- Fuente: HTML del programa por bloque anual + fichas HTML /en-cours-2025-<código> (inglés).
- URL principal: https://uclouvain.be/en-prog-2025-fsa1ba-programme_annual_blocks
- Filas de catálogo: 45; Markdown generados: 45

## Justificación y trampas

Excel (UCLouvain): solo Máster Ing. Industrial / Grado Org. Industrial (ISCED 0410), 2+0 plazas. Se elige el Bachelor in Engineering (FSA1BA, ingeniero civil, 180 ECTS), único grado de ingeniería generalista afín a Industrial/Mecánica (la Mecánica se especializa en el máster). Las 45 UE listadas suman 183 ECTS (>180 porque la 3.ª bloque incluye UE alternativas/de elección que el parser etiqueta como obligatorias; no se distinguen con fiabilidad). Los bloques anuales son 1.º-3.º. El idioma de las fichas: inglés (las UE se imparten en francés salvo indicación). Se omite el profesorado.

## Fase 2

`scraper_ec_b_louvain01.py` (`--sample N`, `--all`, `--codes`): 45 Markdown de 45 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
