# ec_i_bologna01__m_mec

**Titulación:** Laurea Magistrale in Ingegneria meccanica (LM-33, CdS 6721, currículo 912; otros: 913, B82, B83), plan A.A. 2026/27: https://corsi.unibo.it/magistrale/IngegneriaMeccanica-Bologna/insegnamenti/piano/2026/6721/912/000/2026. Estado `parcial`: 53 filas, 40 con ficha EN, 13 sin_guia (idoneidad inglés, prueba final, tirocini y asignaturas cuya ficha no se localiza); 34 Markdown únicos (códigos repetidos entre filas comparten fichero).

## Fase 1
- Copia parametrizada de `ec_i_bologna01` (corsi.unibo.it HTML estático + búsqueda por codiceMateria en www.unibo.it). Cambia el piano URL, el codiceCorso y los annoAccademico probados (varios años porque la ficha depende del A.A. publicado).
- Trampa: la URL del piano usa el CdS nuevo (6668/6721), no el antiguo código de 4 cifras; las URL adivinadas (9066, 0928) dan 500/404: hay que sacar la URL de la página `/insegnamenti` del curso.

## Fase 2
- `scraper_ec_i_bologna01__m_mec.py` idéntico al de `ec_i_bologna01`. `--all` ejecutado; muestras revisadas (secciones Learning outcomes, Course contents, Readings, Teaching methods, Assessment, Teaching tools; sin datos de docentes).
