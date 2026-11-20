# Notas de descubrimiento - ec_b_leuven01

- Universidad: KU Leuven - Faculty of Engineering Science
- Titulación: Bachelor in de ingenieurswetenschappen (Bachelor of Engineering Science, Leuven) (nivel bachelor, estado `ok`)
- Fuente: HTML del programa (onderwijsaanbod.kuleuven.be, misma plataforma que Thomas More) + fichas /syllabi/{n|e}/<código>.
- URL principal: https://onderwijsaanbod.kuleuven.be/opleidingen/e/SC_57861104
- Filas de catálogo: 103; Markdown generados: 103

## Justificación y trampas

Excel: Máster Ing. Telecomunicación (ISCED 0714, 2 plazas) en la Faculty of Engineering Science. KU Leuven no ofrece Ingeniería Mecánica como grado separado: el grado de ingeniería (1.er ciclo) es el Bachelor in de ingenieurswetenschappen (180 sp., académico, en neerlandés; fase 1 común, fases 2-3 con hoofdrichting/afstudeerrichting y minors: werktuigkunde, elektrotechniek, computerwetenschappen, bouwkunde, chemie, materialen, biomedisch). Es el único afín; el Bachelor of Engineering Technology es un grado profesional distinto (no elegido). El programa mezcla todas las orientaciones (148 filas), 'obligatoria' = 'Verplicht in fase' (puede ser obligatoria solo de una orientación); fase = curso. Obligatorias de una sola fase por fase: {1: 60.0, 2: 102.0, 3: 345.0}. Cada ficha en el idioma de impartición (las /e/ en inglés, el resto neerlandés; el HTML trae ambas traducciones). Se elimina el profesorado. robots.txt veta /archief, /pdf y años anteriores, no /syllabi/n|e.

## Fase 2

`scraper_ec_b_leuven01.py` (`--sample N`, `--all`, `--codes`): 103 Markdown de 103 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
