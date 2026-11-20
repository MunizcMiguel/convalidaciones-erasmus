# Notas de descubrimiento - ec_b_mechele14

- Universidad: Thomas More Mechelen-Antwerpen (Sint-Katelijne-Waver)
- Titulación: Bachelor Elektronica-ICT (Sint-Katelijne-Waver) (nivel bachelor, estado `ok`)
- Fuente: HTML del programa (onderwijsaanbod.thomasmore.be, filas tr.module-row) + fichas /syllabi/n/<código>N (neerlandés).
- URL principal: https://onderwijsaanbod.thomasmore.be/opleidingen/n/SC_51844890
- Filas de catálogo: 74; Markdown generados: 74

## Justificación y trampas

Excel: Grado Electrónica Industrial y Automática (4 plazas) y Teleco (0). Thomas More no tiene Mecánica en este destino; se elige la professionele bachelor Elektronica-ICT de Sint-Katelijne-Waver (campus De Nayer, 180 sp.; el programa en inglés está en /archief y robots lo veta), la más afín a Electrónica Industrial. El programa lista fases 1-3 (curso = fase) con todas las tracks/optativas mezcladas; 'obligatoria' = marcada 'Verplicht in fase'. Obligatorias por fase (solo las de una única fase): {1: 99.0, 2: 150.0, 3: 96.0}. Idioma: neerlandés (la base cita materiales en inglés). El profesorado se elimina. Los ECTS son los 'studiepunten' (1 sp. = 1 ECTS). robots.txt de onderwijsaanbod.thomasmore.be veta /archief y /pdf, no /syllabi.

## Fase 2

`scraper_ec_b_mechele14.py` (`--sample N`, `--all`, `--codes`): 74 Markdown de 74 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
