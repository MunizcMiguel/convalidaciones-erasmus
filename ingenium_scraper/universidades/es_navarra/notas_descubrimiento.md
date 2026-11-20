# Notas — Universidad de Navarra (Grado en Ingeniería Mecánica, Tecnun)
- Fuente: https://www.unav.edu/web/grado-en-ingenieria-mecanica/plan-de-estudios (robots permite; asignatura.unav.edu sin robots.txt). Tablas por curso/semestre (índices 5-8; las 9-12 las duplican) con enlace a la ficha; en 1.º hay columnas en inglés intercaladas (se usan las de castellano). Carácter por emparejamiento de nombre con las tablas de módulos; 20 ECTS quedan `sin_clasificar` (nombres distintos). Faltan ~14 ECTS de optativas, que la página no enlaza.
- Sin código oficial: clave = id de la URL de la ficha (`asignatura.unav.edu/{id}/`; una ficha es directamente un PDF `…pdf`).
- La URL «.../{id}/» devuelve un **PDF** «Guía docente 2026-27» (openhtmltopdf), no HTML.
## Fase 2
- `scraper_es_navarra.py`: pdfplumber; secciones en mayúsculas; de RESULTADOS DE APRENDIZAJE se conserva solo el bloque «INGENIERÍA MECÁNICA» (la guía es común a varios grados); se descartan «Profesores de la asignatura» y HORARIOS DE ATENCIÓN. Incluye el programa también en inglés (sección «Contents of the course»). 
- Algunas guías (p. ej. Ingeniería de materiales II) no traen resultados de aprendizaje: hecho, no fallo.
