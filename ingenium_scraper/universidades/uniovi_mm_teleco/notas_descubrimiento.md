# Universidad de Oviedo — Máster Universitario en Ingeniería de Telecomunicación (`uniovi_mm_teleco`) — notas de descubrimiento

Fase 1 y 2 (scripts `discover_uniovi_mm_teleco.py`, `scraper_uniovi_mm_teleco.py`, copias del ejemplo `uniovi_giti`). Fase 3 pendiente por orden del usuario.

## Fuente
- Plataforma SIES de uniovi.es (Liferay, portlet UnioviSiesWeb), idéntica a `uniovi` (Mecánica): ver ../uniovi/notas_descubrimiento.md para la estructura de la ficha, la cadena página de asignatura -> asignaturaId -> JSON serveGuiasDocentes -> fragmento /GuiaDocente, y las trampas (cookie de idioma, caché por URL exacta). robots.txt de www.uniovi.es solo veta /login, /group/, /web/guest/: permitido. Único cliente HTTP: PoliteClient.
- Ficha: `https://www.uniovi.es/estudia/masteres/ingenieriayarquitectura/telecomunicacion`; el plan está en el HTML estático (`#asignaturasAccordion`), prefijo de código `MINGTELE`. Todo sale parseado; nada tecleado a mano.
- 26 asignaturas, 147 ECTS ofertados frente a 120 del plan: obligatorias 90, prácticas externas 3 y TFM 24 cuadran; optativas ofertadas 12 (se cursan 3); 18 ECTS de «Complementos de Formación» (códigos `MINGTELE-C-nnn`, no computan en el plan, caracter=`complementos_formacion`). Los códigos tienen `1`/`2`/`C` en la posición de curso; el script solo valida el curso cuando es numérico. La URL de ficha y de guía usa `masteres/ingenieriayarquitectura/telecomunicacion` en lugar de `grados/...`.

## Fase 2
- Mismo conversor HTML→Markdown que `uniovi` (sin Coordinación/Profesorado; correos y teléfonos eliminados). El encabezado usa el `nombre_grado` del catálogo. `--sample` se deriva del catálogo (1.º, curso intermedio, último curso, optativa, TFG, prácticas/complementos).
- Resultado de `--all` (curso 2026-2027): 23 Markdown de 26. Sin guía publicada: MINGTELE-2-003 Sistemas de Información Contable…, 2-004 Dirección y Gestión de Empresas de Telecomunicaciones, 2-006 Proyectos y Métodos de I+D+i (optativas). Bibliografía ausente en 1 guía (bloque false).
- Los «FALLO» del scraper («sin guías docentes publicadas») son huecos reales del origen, no errores de parseo: el script sale con código ≠ 0 por ellos. Revisados los ficheros más pequeños (TFG) y más grandes: sin chrome de página ni secciones perdidas; solo Es.
- No comparada la versión inglesa (`/en/`); solo español.
