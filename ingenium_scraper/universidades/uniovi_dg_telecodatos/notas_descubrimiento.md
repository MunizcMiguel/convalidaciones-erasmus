# Universidad de Oviedo — Doble Grado en Ingeniería en Tecnologías y Servicios de Telecomunicación / Grado en Ciencia e Ingeniería de Datos (`uniovi_dg_telecodatos`) — notas de descubrimiento

Fase 1 y 2 (scripts `discover_uniovi_dg_telecodatos.py`, `scraper_uniovi_dg_telecodatos.py`, copias del ejemplo `uniovi_giti`). Fase 3 pendiente por orden del usuario.

## Fuente
- Plataforma SIES de uniovi.es (Liferay, portlet UnioviSiesWeb), idéntica a `uniovi` (Mecánica): ver ../uniovi/notas_descubrimiento.md para la estructura de la ficha, la cadena página de asignatura -> asignaturaId -> JSON serveGuiasDocentes -> fragmento /GuiaDocente, y las trampas (cookie de idioma, caché por URL exacta). robots.txt de www.uniovi.es solo veta /login, /group/, /web/guest/: permitido. Único cliente HTTP: PoliteClient.
- Ficha: `https://www.uniovi.es/estudia/grados/ingenieria/telecomunicaciondatos`; el plan está en el HTML estático (`#asignaturasAccordion`), prefijo de código `2GITSTIG`. Todo sale parseado; nada tecleado a mano.
- 85 asignaturas, 546 ECTS ofertados frente a 378 del plan (6 cursos): básica 84 y obligatorias 198 cuadran exacto; optativas ofertadas 216 (se cursan 72); TFG ofertado 48 (cuatro TFG de 12; el plan exige 24). El doble grado NO se compone de asignaturas de los dos grados: tiene plan, códigos (`2GITSTIG-curso-n`) y guías propios en su ficha, así que el catálogo se obtiene de su propia tabla y no hay duplicados que deduplicar. 50 de las 85 comparten nombre con el grado `uniovi_gitst`, pero son otras asignaturas/guías (otro código) y no se reutilizan descargas.

## Fase 2
- Mismo conversor HTML→Markdown que `uniovi` (sin Coordinación/Profesorado; correos y teléfonos eliminados). El encabezado usa el `nombre_grado` del catálogo. `--sample` se deriva del catálogo (1.º, curso intermedio, último curso, optativa, TFG, prácticas/complementos).
- Resultado de `--all` (curso 2026-2027): 50 Markdown de 85. Las 35 sin guía publicada son todas de 5.º y 6.º curso (optativas, Prácticas Externas, Seguridad y Legislación en la Gestión de los Datos y los 4 TFG): el doble grado aún no imparte esos cursos. Para las que comparten nombre con el grado de Teleco (p. ej. Procesado de Señal, Proyectos y Normativa de Telecomunicación) existe guía equivalente en uniovi_gitst. Los 5 bloques presentes en las 50.
- Los «FALLO» del scraper («sin guías docentes publicadas») son huecos reales del origen, no errores de parseo: el script sale con código ≠ 0 por ellos. Revisados los ficheros más pequeños (TFG) y más grandes: sin chrome de página ni secciones perdidas; solo Es.
- No comparada la versión inglesa (`/en/`); solo español.
