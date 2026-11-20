# ec_pl_elblag01 — ANS Elbląg (Institute of Technology / Mechanical Engineering)

- Hints de la ficha Erasmus (`study.ans-elblag.pl`) sí son el sitio Erasmus oficial de la universidad (Akademia Nauk Stosowanych w Elblągu, antes PWSZ). Web principal: `ans-elblag.pl` (robots permite todo salvo /wp-admin/).
- Grado: Mechanical Engineering = «Mechanika i budowa maszyn» (Instytut Politechniczny; especialidades Technology and Operation of Machines, 3D Modelling).
- **Plan completo y fichas en polaco: en USOSweb (`usosweb.ans-elblag.pl`) → robots.txt veta el acceso (PoliteClient: RobotsBlocked). Regla de parada.** La página del grado en ans-elblag.pl no publica plan ni fichas; `irk.ans-elblag.pl` es solo reclutamiento.
- Fuente usable: `https://study.ans-elblag.pl/list-of-courses/` (sin robots.txt, 404): tabla «List of courses conducted in English» con columnas Subject / Semester / Field of study / Hours / ECTS y enlace a ficha Word. Se filtran las filas con «mechanical engineering» en Field of study → 8 asignaturas (32 ECTS). Catálogo `parcial`: oferta Erasmus, sin curso del plan.
- Trampa: la página declara `<base href="https://study.ans-elblag.pl/">`; los href son `assets/courses/ip/2025/…` y resolverlos contra `/list-of-courses/` da 403. Hay que resolver contra la raíz y codificar los espacios (%20).
- Códigos: no hay código oficial de ficha utilizable (el código C.x interno se repite en la plantilla); se usa slug del nombre en inglés.

## Fase 2
- Fichas Word: `.docx` con python-docx (párrafos y tablas en orden de documento, celdas combinadas deduplicadas); `.doc` (2 de 8) con `antiword -x db` (DocBook XML; en Windows está en `/mingw64/bin/antiword` de Git Bash) y bs4. Las tablas se mantienen como tablas Markdown.
- Se eliminan filas de coordinador/lecturer/teacher/consultation (nombres con titulación). Verificado con grep: sin «Ph.D./D.Sc./Prof.» en los 8 Markdown.
- 8/8 escritos. Bloques: contents, learning_outcomes, assessment, bibliography, prerequisites presentes (la evaluación va en la tabla «Assessment method»). Año/semestre del plan vacío en la plantilla.
- No verificado: contraste frente a los Word originales abiertos en Word (solo texto extraído); 2.º-4.º curso no identificables.
