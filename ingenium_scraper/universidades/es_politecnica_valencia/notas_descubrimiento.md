# UPV — Grado en Ingeniería Mecánica (notas)

## Decisión de fuente (regla de parada parcial)
- Título RUCT 2502182 (RD 1393/2007), centros: Florida Universitària (adscrito, primero del RUCT), EPS Alcoy, ETSIADI.
- El plan y las guías del portal principal (www.upv.es) viven en `/pls/oalu/sic_pla.*`, `/pls/.../sic_asi.*` y `/policonsulta/c/GIM`; el robots.txt de www.upv.es los prohíbe (`Disallow: /pls/`, `/policonsulta/c/`) y PoliteClient lanza RobotsBlocked. No se descargó nada de ahí. Alcoy y ETSIADI dependen de ese portal: no recogidos.
- Se usa el centro Florida Universitària (primero del RUCT), cuyo portal propio permite el acceso (robots: `Allow: /`; guiasdocentes.floridauniversitaria.es no tiene robots.txt).

## Fase 1
- Fuente: https://www.floridauniversitaria.es/titulacion/grado-en-ingenieria-mecanica/ — pestaña "Plan de estudios por cursos" (un contenedor por curso; bloques por tipo; fila = nombre, semestre, ECTS, `data-asignatura`). La pestaña "Bloques curriculares" repite asignaturas y se ignora.
- Cada fila → POST `wp-content/themes/florida/theme/ajax/ws_asignatura.php` {id, nombre} → JSON con HTML de ficha: enlace "Ver guía docente" (PDF), idioma, créditos. Código = id del portal.
- 46 filas, 239,5 ECTS listados: básica 60, obligatorias 120 (común rama industrial + especialidad mecánica), TFG 12 (coinciden con RUCT 60/120/48/0/12); optativas listadas 47,5 + Prácticas externas (6 a 18 ECTS, creditos_ects=null).
- Filas-marcador "Intensificación (n asignaturas)" omitidas (las reales están en INTENSIFICACIÓN A/B). TFG y Prácticas externas no tienen ficha ni guía en el portal (`sin_guia`); 12708 Ciencias de Materiales I: el enlace del portal devuelve 404 (`sin_guia`).

## Fase 2
- Guía: PDF con texto (13–22 págs), `https://guiasdocentes.floridauniversitaria.es/2627_{curso}GIM-{Nombre}.pdf` (curso 2026-27). Portada + índice + secciones numeradas (1 Datos de identificación … 12 Consultas); se identifican por título (ES/EN) porque cambian entre guías.
- Se descartan: sección 1 (profesorado, email, despacho), 9 (actuaciones específicas), 12 (consultas/tutorías), cabecera/pie de página. Tablas con `find_tables` → Markdown (las de evaluación conservan porcentajes).
- 43/43 md de 46 filas (3 sin guía). 2 guías en inglés. Bloques: contents/learning_outcomes/assessment 43, bibliography 42, prerequisites 33 (heurística por texto: no hay sección propia).
- Bibliografía: tras un párrafo estándar de biblioteca hay "Bibliografía básica/complementaria".
- No verificado: lectura línea a línea de todas las guías; maquetación a dos columnas puede alterar el orden de algún párrafo en "Resumen".
