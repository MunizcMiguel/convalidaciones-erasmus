# ec_i_bologna01 — Università di Bologna

**Titulación:** Laurea in Ingegneria meccanica (L-9, sede Bologna, CdS 0927), 180 CFU, en italiano. Catálogo parcial: 44 filas desde el piano didattico (A.A. 2025/26, cohorte 2024); todas sin_guia; sin Fase 2.

## Fase 1
- Fuente: https://corsi.unibo.it/laurea/IngegneriaMeccanica-Bologna/insegnamenti/piano/2025/0927/000/000/2024 (HTML estático; tablas por curso con código, periodo, tipo A-F, SSD, CFU). Los cursos integrados (C.I.) sin CFU propios se omiten.
- robots.txt de corsi.unibo.it y www.unibo.it: permiten (solo vetan rutas modello*, test-*).
- Fichas: existen y PoliteClient las sirve en inglés, p. ej. https://www.unibo.it/en/study/course-units-transferable-skills-moocs/course-unit-catalogue/course-unit/2025/513968 (Analisi matematica T-A: secciones Learning outcomes, Course contents, Readings/Bibliography, Teaching methods, Assessment). PERO el id interno de la URL (513968) no es el código del plan (28622) y no aparece en el HTML estático; la búsqueda por codiceMateria carga por JS. Sin navegador no hay tabla código→id: todas las filas quedan sin_guia.
- Los CFU suman 249 porque incluyen optativas alternativas (tipo D); 1.º curso 57 CFU.
- Idea para retomar: descubrir el id desde el sitemap https://www.unibo.it/sitemap.xml.gz o desde algún endpoint JSON del buscador (no inspeccionado).

## Segunda pasada (vías probadas, sigue `parcial`)
- dati.unibo.it (datos abiertos): robots.txt lo veta a PoliteClient (RobotsBlocked) → no se usa.
- sitemap.xml.gz de www.unibo.it (10 576 URLs): no contiene ninguna ficha `course-unit`/`insegnamento`.
- corsi.unibo.it/.../insegnamenti (con y sin ?year&code): HTML sin ids internos; `.../insegnamenti/insegnamento/2025/{codigo}` da 404.
- La búsqueda `unibo.it/.../insegnamenti?codiceMateria=…` devuelve la página sin resultados (se rellenan por JS).
- La ficha por id sí contiene «28622 - Mathematical Analysis T-A», pero adivinar ids por rango sería rastreo ciego no determinista. Descartada.

## Tercera pasada (resuelta, 2026-11-20)
- Clave: la búsqueda `…/en/study/course-units-transferable-skills-moocs/course-unit-catalogue?codiceMateria={cod}&annoAccademico=2024&codiceCorso=0927&single=True&search=True` SÍ se resuelve en servidor (la nota anterior erraba: con annoAccademico=2025+codiceCorso devuelve vacío; con 2024 devuelve el enlace `course-unit/2024/{id}`). `discover_ec_i_bologna01.py` ahora resuelve código→id y solo acepta la ficha cuyo `<h1>` empieza por «{código} - » (si no, es el curso integrado padre: 28628 devolvía la ficha de 28626).
- 36 de 44 filas con ficha (html, EN; el contenido de varias sigue en inglés traducido o mixto); sin ficha: idoneidad inglés, prueba final, 2 tirocini y 3 asignaturas de 3.º (Scienza dei materiali, Fisica matematica, Metodi numerici: sin ficha localizable en AY 2024/25) y Disegno meccanico T (integrada en 65905).
- Fase 2: `scraper_ec_i_bologna01.py` (--sample/--all/--codes). 36 Markdown; secciones Learning outcomes, Course contents, Readings, Teaching methods, Assessment methods, Teaching tools; se omiten Teacher y Office hours. Falta bibliografía en 1 ficha.
