# ec_i_napoli01 — Federico II: Ingegneria Elettronica (L-8)

## Fase 1
- Cineca (`unina.coursecatalogue.cineca.it`) lista el plan pero `testiTotali` viene vacío en todas las fichas → no sirve.
- Fuente usada: Guida dello Studente A.A. 2022/23 (PDF, 106 págs., `ingegneria-elettronica.dieti.unina.it/images/allegati/GdS_-_Laurea_-_2022-23.pdf`), `tipo_fuente: pdf_compartido`. Cada «SCHEDA DELL'INSEGNAMENTO» ocupa 2-3 páginas (rango derivado detectando la cabecera). Año/semestre/CFU/SSD salen de la ficha; obligatoria/optativa por contraste con el Piano di Studi (págs. 4-5).
- Sin código oficial: `codigo_asignatura` = slug del nombre (los typos del PDF se conservan: «telecomincazioni», «elettromagnatica»).
- 32 schede; no hay ficha de Lingua inglese, Laboratorio CAD ni Prova finale. Es el A.A. 2022/23: puede haber cambios en el plan 2025/26.

## Fase 2
- `scraper_ec_i_napoli01.py`: texto por páginas con pdfplumber; cabeceras en mayúsculas → `##`; se eliminan docente/teléfono/email y los pies de página. El cuadro de modalidad de examen (casillas) queda aplanado con una «x» tras la opción marcada.
- 32/32 Markdown.
