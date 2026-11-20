# es_almeria — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (Plan 2010), Escuela Superior de Ingeniería, RUCT 2501729. Curso 2026-27 (el que devuelve la API).
- Fuente del catálogo: la web del plan (`www.ual.es/estudios/grados/presentacion/plandeestudios/2910`) es una SPA AngularJS que carga
  `https://campus.ual.es/ual/api/estudios/asignaturas/asignaturas/2910/es` (JSON: cod_ass, nom_ass, cod_curso, cod_duracion, cod_caracter, cred_ects, estadoass).
  Se filtran las filas `estadoass == "V"` (vigentes): 42 de 51. campus.ual.es no tiene robots.txt (404); www.ual.es no veta `/guia_academica/` ni `/estudios/`.
- Caracteres: T=básica (60), B=obligatoria (144), B/O="Optativa/Obligatoria" (36 ofertados: itinerario de electrónica, se cursan 12; se marca `optativa`), E=prácticas (12), P=TFG (12). 60+144+12+12+12=240; RUCT 150 obl+6 opt = 156 = 144+12.
- Código: `cod_ass` oficial (8 dígitos; prefijo 29/43/44 según el departamento/plan de origen).
- Guía: PDF por asignatura `https://www.ual.es/guia_academica/{cod_ass}/{curso}/CAS` (CAS castellano). Con texto; pdfplumber necesita `x_tolerance=1.2` (si no pega las palabras).
- Estructura PDF: títulos en mayúsculas. Se descartan PROFESOR/A RESPONSABLE, PROFESORADO, "Diversidad Funcional" (boilerplate) y el pie "Fecha ficha docente...". En ASIGNATURA/PLAN solo queda el plan de Ingeniería Mecánica (las guías listan también dobles grados y otros grados).
- Trampas: las guías compartidas entre grados; viñetas "•" que salen como U+FFFD; bibliografía a veces solo un enlace al catálogo de la biblioteca (Expresión Gráfica) -> `bibliography=false`.

## Fase 2
`scraper_es_almeria.py` (CLI --sample/--all/--codes). Muestra de 7 revisada contra el PDF; ver resultado de `--all` en el informe.
