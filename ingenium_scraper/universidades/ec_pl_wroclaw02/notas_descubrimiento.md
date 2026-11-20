# ec_pl_wroclaw02 — PWr Wrocław, Fac. de Ingeniería Mecánica (W10)

## Fase 1
- Titulación: **Mechanical Engineering and Machine Building**, I level (bachelor), full-time, en inglés. (El PDF "mech_en_st_i.pdf" de la misma carpeta es Mechatronics, no se usa; "mbm_en_st_ii" es el máster.)
- Fuente: PDF compartido de la facultad `wm.pwr.edu.pl/fcp/.../w10/karty_kursow/mbm_en_st_i.pdf` (292 páginas, 76 fichas "SUBJECT CARD", texto). robots.txt de wm.pwr.edu.pl solo veta /files/, /ajax/ y `?i_cat`; `/fcp/` permitido. `syllabuskrk.pwr.edu.pl` (portal de sílabos) no resuelve DNS desde esta red.
- Código = "Subject code" (el primero si hay dos entre paréntesis; el bloque de humanidades repite código → sufijo `_p{página}`). Las fichas no traen curso ni semestre ni plan; ECTS = suma de los ECTS por forma de clase (2 fichas, bloques de idiomas y deportes, sin ECTS legibles). Suma 261: incluye optativas alternativas e itinerarios; ECTS totales del plan no verificables. Estado `parcial` por eso.
- Una ficha "MASTER THESIS" figura en este PDF de nivel I (se marca tfg; posible error de la facultad).

## Fase 2
- pdfplumber por rango de páginas; se descartan numeración de página, matriz de correlación efectos–objetivos y "SUBJECT SUPERVISOR" (personal). Títulos de sección en `##`.
- 76/76 Markdown. 25 de 76 fichas (p. ej. MAP001091, universitarias) vienen vacías en la fuente en objetivos/efectos (comprobado con pypdf): hecho de la fuente. Bibliografía y prerrequisitos faltan en bastantes.
