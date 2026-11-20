# ec_a_innsbru01 – Universität Innsbruck (LFUI/UMIT TIROL) – Mechatronik B.Sc. (catálogo PARCIAL)

## Titulación elegida
- Innsbruck no tiene Ingeniería Mecánica. Grado afín de primer ciclo: **Bachelorstudium Mechatronik** (B.Sc., 6 sem., 180 ECTS-AP, programa conjunto con la UMIT TIROL; contiene Mecánica, CAD, Máquinas, Resistencia, Termodinámica, Control). Existe también Bau- und Umweltingenieurwissenschaften (descartado: civil). Los másteres (Mechatronik M.Sc.) quedan fuera.

## Fuente
- Ficha del grado: `https://www.uibk.ac.at/de/studien/ba-mechatronik/2011w/`; enlaza el PDF «ba-mechatronik_stand-01102018.pdf» (texto del Curriculum, 27 págs.; el script elige el Stand más reciente enlazado). Host www.uibk.ac.at: PoliteClient no encontró bloqueo en robots.txt.
- El curriculum describe cada **módulo** (no cada asignatura): § 7 lista las LV (VO/UE/VU/PR/SE) con contenido en 1-5 líneas, SSt y ECTS-AP, más «Lernziele des Moduls» y «Anmeldungsvoraussetzung/en». § 8/Anhang: «Empfohlener Studienverlauf» por semestre (de ahí el semestre).
- No hay guías docentes por asignatura públicas fuera de LFU:online (portal de cursos; no usado). Catálogo marcado `parcial` por esto y porque el texto del curriculum es la versión informativa (la vinculante está en el Mitteilungsblatt; hay modificaciones de 2022 no localizadas).

## Reglas
- 30 módulos: P1-P24 (Pflicht, 150 ECTS-AP), P25-A1/A2 (Pflicht de la especialización, 10 c/u), W1, W2-A1/A2, W3 (Wahl). Códigos = los del propio Studienverlauf (P25-A* es el número siguiente a P24, deducido del máximo). Suma bruta 195 (alternativos).
- Título: cabecera de 1-3 líneas («… Material- / und …», números de módulo en la 2.ª línea); se limpia «ECTS-», «SSt Univ.», «AP».
- ECTS = columna 2 de la línea «Summe SSt ECTS»; los módulos Wahl sin Summe salen del texto «Umfang von N ECTS-AP».

## Fase 2
- `scraper_ec_a_innsbru01.py --all`: 30 de 30 Markdown, 0 fallos (lecciones + contenido, Lernziele, requisitos). Revisado contra el PDF: P8 (Mechanik 1); estructura de P1, P18, P24, P25-A1, W3.
- Siempre ausentes: assessment y bibliography (el curriculum solo da reglas generales de evaluación en § 9-10, no por módulo). Las cifras SSt/ECTS de cada LV quedan en el flujo de texto sin tabular.
