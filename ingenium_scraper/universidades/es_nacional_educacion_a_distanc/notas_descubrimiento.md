# Notas — UNED (Grado en Ingeniería Mecánica, Plan 2024)
- Fuente: https://www.uned.es/universidad/inicio/estudios/grados/grado-en-ingenieria-mecanica.html (robots permite). Tablas `table.tabla_asignaturas.hidden-xs`: las 4 primeras (cursos 1-4) son el Plan 2024 (RD 822/2021, el vigente); las siguientes son Plan 2009 y extinguidas (no usadas). Algunos códigos salen truncados en la celda («6890210-»): el código se toma del enlace `codAsignatura`.
- 64 asignaturas: básica 60 / obligatoria 148 / TFG 12 = RUCT; optativas ofertadas 120 vs 20 exigidas. Carácter del TFG en la web: «TRABAJO FINAL OBLIGATORIO».
- Guía: PDF público `…/pdf/GuiasAsignaturasGrados/PDFGuiaPublica?codigoAsignatura={c}&curso=2027&codigoTitulacion=6803&language=es&esMaster=false` (curso 2026/27). La página HTML reparte la guía en subpáginas por apartado, por eso se usa el PDF (1 petición).
## Fase 2
- `scraper_es_nacional_educacion_a_distanc.py`: pdfplumber; cuerpo tras el índice; apartados principales en orden fijo; se descartan Equipo docente, Horario de atención y Tutorización (nombres/correos/teléfonos). 
- 64/64 Markdown (ver informe). Revisados Mecánica I y TFG (el TFG no tiene bibliografía propia). Tablas como texto.
