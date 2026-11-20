# es_cadiz — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (UCA), Escuela Superior de Ingeniería (el RUCT 2503077 cita también la ETS de Ingeniería de Algeciras; no incluida). Curso 2026-27.
- Catálogo: `https://esingenieria.uca.es/docencia/grados/gim/asignaturas/` (WordPress, HTML estático): tablas por curso (CÓDIGO | ASIGNATURA | SEMESTRE | CRÉDITOS | FB/OB/OP/TFG) + 4 tablas de optativas por itinerario (Diseño de Máquinas, Estructuras, Fabricación, Multidisciplinar). Cada código enlaza a `https://asignaturas.uca.es/2026-27/{codigo}`. 50 filas, sin duplicados.
- Créditos: la web da FB 66 + OB 120 (RUCT: 60 + 126; la suma 186 coincide) + TFG 18; 102 ECTS optativos ofertados, se cursan 36.
- Robots: esingenieria.uca.es (solo veta /wp-admin/), asignaturas.uca.es (404 = sin restricciones).
- Guía: ficha HTML única, un `<fieldset>` por apartado (legend = título). Los apartados "Requisitos y recomendaciones" guardan el texto en campos `<input value>`/`<textarea>`. "Bibliografía" anida las tablas básica/recomendada (hay fieldsets duplicados que se ignoran). Se descartan Profesorado, Idiomas, Movilidad, Inteligencia artificial y "Sistema de evaluación" (se conserva su hijo "Procedimientos de evaluación", con ponderaciones).
- Trampas: bloque "Inclusión o accesibilidad" (boilerplate) no se copia; la guía de algunas optativas no tiene programa publicado (21720040 Mecánica Analítica → sin temario ni resultados → no se genera).

## Fase 2
`scraper_es_cadiz.py` (--sample/--all/--codes).
