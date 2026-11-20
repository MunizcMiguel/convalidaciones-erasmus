# es_publica_navarra — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (UPNA, ETSIIIT; RUCT 2502737, RD 1393/2007). Curso 2026-27.
- Fuente: `https://www.unavarra.es/sites/grados/industriales/ingenieria-mecanica/plan-de-estudios.html` (HTML estático). Tablas «Código | Asignatura | Carácter | ECTS» por curso del plan **248** (acceso desde 2020-21, vigente) y tres tablas de optatividad (248 7xx/8xx); la misma página lista el plan 245 (anterior), que se ignora. No hay semestre en el plan (solo «Periodo» en la ficha).
- Validación: básica 60, obligatorias 138, TFG 18 = RUCT; 63 ECTS optativos ofertados (RUCT 24).
- Ficha: `https://www.unavarra.es/ficha-asignaturaDOA?idioma=es&codAsig={codigo}` (HTML; hay que decodificar como UTF-8). Cabecera con año, código, créditos, tipo, curso, periodo y PROFESORADO (descartado) + secciones `div > h3` hasta el enlace «Subir». Evaluación y Metodología son tablas (pesos %, carácter recuperable, nota mínima).
- 10 optativas devuelven «No hay datos para esta asignatura en el año académico en curso» → `sin_guia` (decidido en el discover).
- robots.txt de www.unavarra.es: veta bots con nombre (ClaudeBot, anthropic-ai, GPTBot...) pero no al agente del proyecto ni `/ficha-asignaturaDOA`.
- Trampas: no hay apartado de requisitos previos en la plantilla (prerequisites casi siempre false).

## Fase 2
`scraper_es_publica_navarra.py`: 43/43 Markdown (los 10 `sin_guia` omitidos). Evaluación, resultados, contenidos y bibliografía en todos.
