# Notas de descubrimiento - ec_d_bingen01

- Universidad: Technische Hochschule Bingen
- Titulación: Maschinenbau (B.Eng.) (nivel bachelor, estado `ok`)
- Fuente: Modulhandbuch PDF (127 págs.): cabecera 'B-MB-XXXX Nombre' + 'Kennnummer'; grupos del índice (Gruppe IV = optativas).
- URL principal: https://www.th-bingen.de/fileadmin/studium/bachelor/maschinenbau/Modulhandbuch_Bachelor_Maschinenbau_26-09-28.pdf
- Filas de catálogo: 78; Markdown generados: 78

## Justificación y trampas

Excel: Grado Org. Industrial (1 plaza), Grado Ing. Química Industrial y una fila sin titulación (ISCED 0413 gestión). TH Bingen no ofrece Org. Industrial ni Química; se toma Maschinenbau (B.Eng.), la titulación de Mecánica (prioridad), aunque Wirtschaftsingenieurwesen (Modulhandbuch aparte, Stand 21.11.2024) sería la alternativa para Org. Industrial y Verfahrens-/Prozesstechnik para Química Industrial. Plan de 7 semestres, 210 LP (dato no verificado en este PDF; los grupos VW son electivos de Vertiefung). Obligatorios suman 217 LP en el listado; se omiten datos del Modulbeauftragte. robots.txt de th-bingen.de: 404 (sin restricciones).

## Fase 2

`scraper_ec_d_bingen01.py` (`--sample N`, `--all`, `--codes`): 78 Markdown de 78 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
