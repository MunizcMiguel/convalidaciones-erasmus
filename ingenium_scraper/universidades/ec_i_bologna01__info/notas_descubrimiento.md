# ec_i_bologna01__info

**Titulación:** Laurea in Ingegneria informatica (L-8, CdS 6668), plan A.A. 2026/27 cohorte 2025: https://corsi.unibo.it/laurea/IngegneriaInformatica/insegnamenti/piano/2026/6668/000/000/2025. Estado `parcial`: 28 filas, 14 con ficha EN, 14 sin_guia (idoneidad inglés, prueba final, tirocini y asignaturas cuya ficha no se localiza); 14 Markdown únicos (códigos repetidos entre filas comparten fichero).

## Fase 1
- Copia parametrizada de `ec_i_bologna01` (corsi.unibo.it HTML estático + búsqueda por codiceMateria en www.unibo.it). Cambia el piano URL, el codiceCorso y los annoAccademico probados (varios años porque la ficha depende del A.A. publicado).
- Trampa: la URL del piano usa el CdS nuevo (6668/6721), no el antiguo código de 4 cifras; las URL adivinadas (9066, 0928) dan 500/404: hay que sacar la URL de la página `/insegnamenti` del curso.

## Fase 2
- `scraper_ec_i_bologna01__info.py` idéntico al de `ec_i_bologna01`. `--all` ejecutado; muestras revisadas (secciones Learning outcomes, Course contents, Readings, Teaching methods, Assessment, Teaching tools; sin datos de docentes).
