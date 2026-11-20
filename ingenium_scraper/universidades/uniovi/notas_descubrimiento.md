# Universidad de Oviedo (uniovi) — notas de descubrimiento

Grado en Ingeniería Mecánica, EPI Gijón, plan `GIMECA01`. Generado por `discover_uniovi.py` (12-11-2026).

## Fuente del catálogo
- `https://www.uniovi.es/estudia/grados/ingenieria/mecanica` (ficha oficial del grado, Liferay, portlet `es_uniovi_sies_web_UnioviSiesWebPortlet`).
- El plan está en el **HTML estático** (sin JS): `#asignaturasAccordion` > `div.collapse` con id `{primero|segundo|tercero|cuarto}-temporalidad-{primer|segundo}-semestre`, cada uno con una `table.table-striped` (Asignatura | Créditos | Carácter | Itinerario Bilingüe | Detalle). El código de asignatura sale del `href`.
- No he encontrado API/JSON del plan completo; el único JSON es por asignatura (ver abajo). robots.txt solo veta `/login`, `/group/`, `/web/guest/`: todo lo usado está permitido.
- Resultado: 54 asignaturas, 336 ECTS ofertados. Plan 240 = 60 básica + 126 obligatorias + 42 optativas + 12 TFG; básica/obligatorias/TFG cuadran exactamente; se ofertan 138 ECTS optativos (23 asignaturas de 4.º, menciones) de los que se cursan 42. Coincide al 100 % (códigos, nombres, ECTS, URLs) con el antiguo `../gimeca_plan_estudios.json`.
- El título de la página dice "Grado en Ingeniería Mecánica (PARS)"; el script quita el sufijo "(PARS)".

## Cómo llegar a la guía docente (3 pasos, todo GET sin sesión)
`url_guia_docente` del catálogo es la **página de asignatura**: `{BASE}/-/fof/asignatura/{CODIGO}` (p. ej. `GIMECA01-4-012`). Esa página solo trae metadatos (Código, Curso, Temporalidad, Materia, Carácter, Créditos, Itinerario Bilingüe, Actividades con horas); la guía se carga por AJAX:
1. En el HTML de la página buscar `_es_uniovi_sies_web_UnioviSiesWebPortlet_asignaturaId=(\d+)` (id interno, p. ej. 69990; NO es derivable del código).
2. Lista JSON de guías por curso académico:
   `{BASE}?p_p_id=es_uniovi_sies_web_UnioviSiesWebPortlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=serveGuiasDocentes&p_p_cacheability=cacheLevelPage&_es_uniovi_sies_web_UnioviSiesWebPortlet_asignaturaId={ID}`
   -> `[{"guiaDocenteId","asignaturaId","periodoAcademicoId","periodoAcademico":"2026-2027","codigoAsignatura"}, ...]` (hoy: 2026-2027 … 2023-2024). Elegir por `periodoAcademico`, no por posición.
3. Fragmento HTML de la guía:
   `{BASE}?p_p_id=es_uniovi_sies_web_UnioviSiesWebPortlet&p_p_lifecycle=0&p_p_state=exclusive&p_p_mode=view&_es_uniovi_sies_web_UnioviSiesWebPortlet_mvcRenderCommandName=%2FGuiaDocente&_es_uniovi_sies_web_UnioviSiesWebPortlet_guiaDocenteId={GID}`

`BASE` = `https://www.uniovi.es/estudia/grados/ingenieria/mecanica` (ES) o `https://www.uniovi.es/en/estudia/grados/ingenieria/mecanica` (EN). Son 3 peticiones por asignatura e idioma (pasos 1-2 son comunes; el paso 3 se repite con /en/).

## Estructura de la guía (fragmento del paso 3)
`#guiaDocenteAccordion`; cada apartado es un `div.seccion` (título) con `data-target="#xxx-detail"`, y el contenido está en el `div.collapse` con ese id. **Usar siempre `data-target`**: en "Profesorado" el collapse NO está dentro del mismo `div.card` que el título.

| Título (`div.seccion`) | id del contenido | Uso |
|---|---|---|
| Coordinación | `#coordinadores-detail` | — |
| Profesorado | `#profesorado-detail` | — |
| Contextualización | `#contextualizacion-detail` | contexto |
| Requisitos | `#requisitos-detail` | prerrequisitos |
| Competencias y resultados del aprendizaje | `#competenciasResultadosAprendizaje-detail` | learning outcomes |
| Contenidos | `#contenidos-detail` | temario |
| Metodología y plan de trabajo | `#metodologia-detail` | métodos + tabla de horas (suele haber `<table>`) |
| Evaluación del aprendizaje | `#evaluacion-detail` | evaluación |
| Bibliografía | `#bibliografia-detail` | bibliografía |

El interior es HTML libre pegado por el profesorado (p, listas, tablas, a veces estilos de Word): convertir a markdown conservando tablas. ECTS/semestre/carácter no están en la guía, sino en la página de asignatura y en el catálogo.

## Idiomas
- Los títulos de apartado salen siempre en español, también con `/en/`.
- Con `/en/` el **contenido** sale en inglés solo si el profesorado lo ha rellenado; si no, devuelve el mismo texto español. Muestras: `GIMECA01-1-001` Cálculo (itinerario bilingüe) -> inglés real; `GIMECA01-4-012` (no bilingüe) y `GIMECA01-4-024` TFG (marcado bilingüe) -> idéntico al español. Fase 2 debe bajar ES y EN y comparar texto de los apartados para saber si hay traducción (no fiarse de la columna "Itinerario Bilingüe": 32 de 54 marcadas "Sí").
- También existe `/ast/` (asturiano), no explorado.
- El catálogo marca `idioma_pagina="es"` en todas las filas.

## Trampas
- La página de asignatura sin los pasos 2-3 no contiene el texto de la guía.
- La caché de PoliteClient usa la URL exacta como clave: construir las URLs siempre con el mismo orden de parámetros.
- El TFG tiene Coordinación/Profesorado vacíos y texto genérico de plantilla ("en el caso de asignaturas compartidas…").
- Solo he abierto 3 asignaturas (1-001, 4-012, 4-024); no está verificado que las otras 51 tengan guía 2026-2027 publicada ni cuántas tienen versión inglesa.
- `raw_cache` usa nombres hash; el consola de Windows necesita `PYTHONIOENCODING=utf-8` solo para imprimir, los ficheros salen en UTF-8.

## Fase 2 — scraper (`scraper_uniovi.py`, 12-11-2026)

**Enfoque.** Por asignatura, 3 GET (página de asignatura → `asignaturaId`; JSON `serveGuiasDocentes` → `guiaDocenteId` del curso `meta.curso_academico`, elegido por `periodoAcademico`; fragmento `/GuiaDocente` en español). El Markdown lleva `# nombre`, un bloque "Datos de la asignatura" (curso, temporalidad, materia, carácter, créditos, actividades con horas, sacados de la página de asignatura) y un `##` por apartado de la guía, localizando el contenido siempre por `data-target`. Conversor HTML→Markdown propio (bs4, sin dependencias nuevas): párrafos, negrita/cursiva, listas anidadas, enlaces y tablas con `colspan`/`rowspan` (celdas multipárrafo unidas con `<br>`, columnas vacías eliminadas). No se vuelcan "Coordinación" ni "Profesorado"; además se elimina cualquier párrafo suelto del tipo "Coordinador/Profesor…: nombre" (aparece p. ej. al final de la bibliografía de 3-007). `blocks_found` = el apartado correspondiente tiene texto (Requisitos→prerequisites, Competencias y resultados→learning_outcomes, Contenidos→contents, Evaluación→assessment, Bibliografía→bibliography). Falla (exit ≠ 0) si falta el acordeón, algún apartado esperado o la guía está casi vacía; si no hay guía del curso vigente usa la más reciente y lo avisa en la línea de salida.

**Muestra piloto (`--sample 5`).** `GIMECA01-1-001` Cálculo (1.º, básica), `GIMECA01-2-001` Resistencia de Materiales (2.º, obligatoria), `GIMECA01-3-007` Cálculo y Diseño de Máquinas (3.º, obligatoria), `GIMECA01-4-012` Diseño de Sistemas Mecánicos (4.º, optativa), `GIMECA01-4-024` TFG. Las 5 con los 5 bloques presentes; 8,9–16,4 kB por fichero. Validación: comparación palabra a palabra del texto del acordeón (sin Coordinación/Profesorado) contra el Markdown → 0 palabras perdidas salvo los datos personales eliminados; nº de filas de tabla idéntico; lectura manual de los 5 ficheros.

**Peculiaridades.**
- El TFG sí tiene "Contenidos" (un párrafo genérico, sin temario) y su evaluación es descriptiva, sin porcentajes. Conserva frases de plantilla "(en el caso de asignaturas compartidas…)".
- Las tablas con porcentajes suelen estar en "Metodología y plan de trabajo" (horas por modalidad); en "Evaluación" los porcentajes vienen casi siempre en listas/prosa, no en tabla.
- Los subtítulos internos son `<p><strong>` o `<u>`, no `<h*>`: quedan como párrafos en negrita/planos, no como encabezados. Los atributos `style` vienen neutralizados como `estiloFake`.
- Listas mal anidadas en origen (p. ej. 2-001: `<ol>` que se reinicia, numeración manual "4." en `<p>`): se reproducen tal cual. Erratas del origen ("BLOQUE3") también.
- **Idioma por cookie**: Liferay recuerda el idioma; la página del TFG cacheada en Fase 1 (tras visitar `/en/`) tenía los valores en inglés ("Fourth", "0 Hours") con `<html lang="en-US">`. El scraper lo detecta y vuelve a pedir esa página una vez (`force=True`); además envía `Accept-Language: es` y nunca visita `/en/`. No comparar ES/EN con el mismo cliente sin limpiar cookies.
- Solo se baja la versión española (referencia); la inglesa no se compara en esta fase.
- Coste de la tirada completa: 3 peticiones × 54 = 162 (menos las 15 ya en caché) a 1–3 s → unos 5–6 min. No verificado: que las 49 asignaturas restantes tengan guía 2026-2027 ni guías con imágenes/fórmulas (`<img>` se vuelca como `[imagen]`).
