# es_jaume_castellon — notas de descubrimiento
- Título: Grau en Enginyeria Mecànica (UJI, ESTCE; RUCT 2502271, RD 822/2021). Curso 2026-27.
- Fuente: SIA de la UJI (`ujiapps.uji.es/sia/rest/publicacion/estudio/{id}`), HTML estático con `div.asignatura` (código - nombre, «Curs N - Semestre S - Tipus», ECTS). Hay dos planes: estudio **275** = plan 2026 (nuevo, RD 822/2021) que solo publica 1.º (10 asignaturas, 60 ECTS básicos = RUCT); estudio **222** = plan anterior, con los 4 cursos (47 asignaturas). Se usa el 222 porque es el único con el grado completo; los 10 de 1.º del 222 están en extinción y no publican evaluación («consultar aula virtual»).
- ECTS plan 222: básica 72, obligatorias 133,5, optativas ofertadas 66, prácticas 6, TFG 12. No casa con el RUCT (60/144/18/6/12) salvo prácticas y TFG, por ser el plan antiguo.
- robots.txt: ujiapps.uji.es permite `/sia/`, prohíbe el resto; la guía unificada `e-ujier.uji.es/pls/...` está vetada (host entero) y NO se usa; el cambio de idioma `/upo/...` está vetado, así que el texto sale en catalán (idioma "ca"; el SIA no ofrece español sin ese cambio).
- Guía = cinco subpáginas bajo `/sia/rest/publicacion/2026/estudio/222/asignatura/{COD}/`: `temario`, `metodologia`, `evaluacion`, `actividades` (actividades, competencias, resultados de aprendizaje), `reqmatricula` (cuadro de requisitos de matrícula = prerrequisitos). Contenido en `div.contenido > div.pagina-asignatura-seccion`. `/profesores` no se descarga.
- Trampas: restos de Word (`[if gte mso 9]...`, `[if !supportLists]`) dentro del HTML se eliminan; algunas fichas tienen 17 000+ caracteres de temario; bibliografía = enlace a catálogo de biblioteca (bibliography=false siempre).

## Fase 2
`scraper_es_jaume_castellon.py`: 47/47 Markdown (235 peticiones). Sin evaluación: 10 (1.º en extinción). Prerrequisitos solo cuando hay cuadro de matrícula con contenido.
