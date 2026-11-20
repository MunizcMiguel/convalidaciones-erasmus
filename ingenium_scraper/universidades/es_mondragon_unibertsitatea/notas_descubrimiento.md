# Notas — Mondragon Unibertsitatea (Grado en Ingeniería Mecánica, plan 2017)
- Fuente: https://mondragon.edu/grado-ingenieria-mecanica/plan-estudios/2017 (HTML estático, robots permite). 8 tablas (semestre) con enlace PDF por asignatura: `https://www.mondragon.edu/ikasketak/MGEP/M2GM-2500197/2017/{curso}/{CODIGO}-es.pdf`. Código = el de la ficha.
- 64 asignaturas: básica 60 / obligatoria 108 / TFG 12 = RUCT; optativas ofertadas 132 (4.º) frente a 60 exigidas.
- Trampa: las fichas son de ediciones antiguas (p. ej. «Curso 2019/2020»), no 2026-27; la cabecera de cada Markdown indica la edición. Algunas llevan anexos de adaptación (covid, euskera) que se cortan. Idioma de docencia en cabecera (EUSKARA/CASTELLANO), el texto de la ficha -es está en castellano.
## Fase 2
- `scraper_es_mondragon_unibertsitatea.py`: pdfplumber; apartados en mayúsculas; los de actividades/evaluación se repiten por resultado de aprendizaje y se concatenan bajo un único encabezado; se descarta PROFESORES, cabecera de página y pie TCPDF. Las tablas salen como líneas de texto.
- 64/64 Markdown. Revisados GMC201, GMA203, GMR201 (el TFG no tiene actividades/evaluación en la ficha: hecho, no fallo). Prerrequisitos casi siempre «no se requiere».
