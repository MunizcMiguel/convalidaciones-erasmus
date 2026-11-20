# es_rioja — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (UR, ETSII; RUCT 2502128, código interno 803G). Curso 2026-27.
- Fuente: `https://www.unirioja.es/grados-y-dobles-grados/grado-en-ingenieria-mecanica/curso-2026-2027/` (HTML estático): tablas «Curso: Nº» (Per., Tipo, código, nombre, enlaces «Versión PDF», ECTS) y tabla de optativas por itinerario (Cº, Per., código, nombre, ECTS, marcas de itinerario). Validación: básica 60, obligatorias 132, prácticas 6, TFG 12 = RUCT; 51 ECTS optativos ofertados (se cursan 30).
- Guía: `https://aps.unirioja.es/GuiasDocentes/servlet/agetguiahtml?2026-27,803G,{codigo}` (HTML UTF-8; también `agetguiapdf`). robots.txt de www.unirioja.es sin veto para estas rutas; aps.unirioja.es no veta (PoliteClient lo acepta).
- Estructura: `body.cuerpoHtml` plano (h2/h3/div/table). Secciones: datos de la asignatura, Departamentos responsables y Profesorado previsto (con nombres, teléfonos, correos y despachos: se descartan), Descripción de contenidos, Requisitos previos, Contexto, Competencias (generales/específicas), Resultados del aprendizaje, ODS (imágenes: se descartan), Temario, Bibliografía (tabla), Metodología, Organización (tablas de horas), Evaluación (tabla con pesos).
- Español; hay versión «English friendly» sin usar.

## Fase 2
`scraper_es_rioja.py`: 45/45 Markdown. Los requisitos previos suelen decir «No se precisan» (prerequisites=false).
