# Notas de descubrimiento - ec_d_karlsru01

- Universidad: Karlsruher Institut für Technologie (KIT)
- Titulación: Maschinenbau (B.Sc.), SPO 2015 (nivel bachelor, estado `ok`)
- Fuente: Modulhandbuch PDF (520 págs.) en www.mach.kit.edu: módulo = 'M x.y Modul: NOMBRE [M-…]'; se corta antes de las Teilleistungen (T x.y).
- URL principal: https://www.mach.kit.edu/download/MHB/82-604-H-20165_v1_2025-02-28_de.pdf
- Filas de catálogo: 34; Markdown generados: 34

## Justificación y trampas

KIT (D KARLSRU01), universidad distinta de Hochschule Karlsruhe (ec_d_karlsru05/hka). Excel: Máster Ing. Industrial (ISCED 0715, 2 plazas); se toma el grado de Maschinenbau B.Sc. (SPO 2015, 6 semestres, 180 LP), equivalente de primer ciclo a la Mecánica. Fichas a nivel de MÓDULO (no de Teilleistung/asignatura); los módulos listados son los 'Modul' del PDF: Pflicht (Höhere Mathematik, Werkstoffkunde, Technische Mechanik, Thermodynamik, MKL, Fertigungsprozesse…) más Wahlpflicht y Zusatzleistungen. Sin semestre por módulo (el Studienplan lo da aparte). 'optativa' = Wahlpflicht/Schwerpunkt/Zusatz según nombre y 'Bestandteil von'. El Modulhandbuch no incluye bibliografía; la Erfolgskontrolle suele remitir a las Teilleistungen. Se elimina 'Verantwortung' (profesorado). Los Schwerpunkt-Module con mucho detalle y las Teilleistungen (T-MACH) quedan dentro del texto del módulo. robots.txt de www.mach.kit.edu permite /download/.

## Fase 2

`scraper_ec_d_karlsru01.py` (`--sample N`, `--all`, `--codes`): 34 Markdown de 34 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
