# Universidad de Oviedo — Grado en Ingeniería en Tecnologías y Servicios de Telecomunicación (`uniovi_gitst`) — notas de descubrimiento

Fase 1 y 2 (scripts `discover_uniovi_gitst.py`, `scraper_uniovi_gitst.py`, copias del ejemplo `uniovi_giti`). Fase 3 pendiente por orden del usuario.

## Fuente
- Plataforma SIES de uniovi.es (Liferay, portlet UnioviSiesWeb), idéntica a `uniovi` (Mecánica): ver ../uniovi/notas_descubrimiento.md para la estructura de la ficha, la cadena página de asignatura -> asignaturaId -> JSON serveGuiasDocentes -> fragmento /GuiaDocente, y las trampas (cookie de idioma, caché por URL exacta). robots.txt de www.uniovi.es solo veta /login, /group/, /web/guest/: permitido. Único cliente HTTP: PoliteClient.
- Ficha: `https://www.uniovi.es/estudia/grados/ingenieria/telecomunicacion`; el plan está en el HTML estático (`#asignaturasAccordion`), prefijo de código `GITELE01`. Todo sale parseado; nada tecleado a mano.
- 66 asignaturas, 426 ECTS ofertados frente a 240 del plan: básica 60 y obligatorias 108 cuadran exacto; optativas ofertadas 204 (se cursan 60); TFG ofertado 54 = tres TFG de 12 ECTS (uno por mención: Sistemas Electrónicos, Sistemas de Telecomunicación, Telemática) más tres de 6 ECTS para la segunda mención (el plan exige 12).

## Fase 2
- Mismo conversor HTML→Markdown que `uniovi` (sin Coordinación/Profesorado; correos y teléfonos eliminados). El encabezado usa el `nombre_grado` del catálogo. `--sample` se deriva del catálogo (1.º, curso intermedio, último curso, optativa, TFG, prácticas/complementos).
- Resultado de `--all` (curso 2026-2027): 63 Markdown de 66. Sin guía publicada (curso 2026-2027): GITELE01-4-017 Diseño Asistido por Computador, 4-019 Ingeniería Acústica, 4-025 Dispositivos en Redes Industriales (optativas de 4.º). Los 5 bloques presentes en las 63.
- Los «FALLO» del scraper («sin guías docentes publicadas») son huecos reales del origen, no errores de parseo: el script sale con código ≠ 0 por ellos. Revisados los ficheros más pequeños (TFG) y más grandes: sin chrome de página ni secciones perdidas; solo Es.
- No comparada la versión inglesa (`/en/`); solo español.
