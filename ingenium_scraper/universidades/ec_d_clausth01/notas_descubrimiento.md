# ec_d_clausth01 – TU Clausthal – Maschinenbau B.Sc. (6 sem., 180 LP)

## Fuente
- Página del grado: `https://www.fakultaeten.tu-clausthal.de/fakultaet-fuer-ingenieur-und-wirtschaftswissenschaften/studium/bachelor-studiengaenge/maschinenbau` (enlaza el handbook).
- Modulhandbuch (PDF, 125 págs., Stand 13.06.2025, AFB 04.05.2021): `.../fileadmin/Sites/Studiengaenge/Documents/Studiengaenge/Modulhandbuecher/Neu_in_2025-26/MHB_MB_B.Sc._13_06_2025.pdf` (mismo host). PoliteClient no encontró bloqueo en robots.txt. Un único PDF -> `pdf_compartido`.
- Idioma: alemán (títulos de LV también en inglés). El handbook incluye bibliografía.
- El Modellstudienplan (gráfico, otro PDF) da los semestres pero no es parseable de forma determinista: curso/semestre = null.

## Estructura
- Un módulo = bloque de 2-5 páginas que empieza con la tabla `1a. Modultitel (deutsch) | 1b. (englisch)`. 50 módulos: Pflicht (26), tres Studienrichtungen (Allg. Maschinenbau 3, Mechatronik 3, Biomechanik 3; se elige una) y dos Wahlpflichtkataloge (Maschinenbau 7, Industrieanwendung 8).
- El campo 5 «Modulnummer» está vacío -> código = slug del título alemán. Suma bruta 248 LP (alternativos); un itinerario = 180.
- Campos: 1 título, 2 uso, 3 responsable (se elimina), 4 facultad, 6-9 idioma/LP/duración/oferta, 10 objetivos, tabla de LV (11-17; Dozent y LV-Nr se eliminan), 18a-22a por LV (requisitos, contenidos, medios, literatura, otros), 23-28 tabla de evaluación, 29-31 examen (30a Prüfer se elimina).
## Trampas
- `extract_tables()` pierde texto que desborda la celda y trocea celdas altas: se usa `find_tables()` y el texto de cada celda recortada (`page.crop(cell)`). Las etiquetas 18a-22a están centradas verticalmente en una celda alta: el valor es la celda de la derecha que se solapa en vertical con la etiqueta.
- Los títulos largos ocupan varias filas de celdas (parciales + completa): se fusionan.
- Bloques por LV («Zu Nr. N») se conservan con sufijo `(zu Nr. N)` en el encabezado.

## Fase 2
- `scraper_ec_d_clausth01.py --all`: 50 de 50 Markdown, 0 fallos. Revisados contra el PDF: ingenieurmathematik-i, maschinenelemente, praktikum-mess-und-regelungstechnik (y rarezas de formato de las 6 de la muestra).
- Bloques ausentes: prerequisites en algunos (campo «keine»/vacío). Defecto menor: bachelorarbeit conserva texto con «Dozenten» (cita genérica, sin nombres).
