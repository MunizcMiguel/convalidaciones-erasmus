# UC3M — Grado en Ingeniería Mecánica (notas)

## Fase 1
- Plan: RUCT 2500048 (RD 1393/2007, renovado), Escuela Politécnica Superior (Leganés), estudio 221 / plan 446. Único centro.
- Fuente: pestaña "Programa" de https://www.uc3m.es/grado/mecanica (HTML estático, tablas por curso/cuatrimestre + optativas). Código = id de asignatura de la ficha.
- 65 filas = 294 ECTS ofertados. RUCT: básica 60 / obligatorias 156 / TFG 12 / optativas 12 / total 240. Coinciden básica, obligatorias y TFG; optativas ofertadas 66 (se cursan 12). Prácticas Externas (6) es optativa (RUCT prácticas=0).
- 3 filas obligatorias `sin_guia` (9 ECTS): Habilidades: Humanidades I/II y Habilidades profesionales interpersonales (bolsas de créditos). Clave derivada `SG-{curso}{cuatrimestre}-{nombre}`.
- Trampa: la web sitúa todas las optativas en curso 4 / cuatrimestre 2 aunque no sea real.

## Fase 2
- Guía: `https://aplicaciones.uc3m.es/cpa/generaFicha?est=221&plan=446&asig={codigo}&idioma=1` (HTML estático, 1 GET). idioma=1 = castellano (también para asignaturas impartidas en inglés). Curso 2026/27.
- Secciones `div.apartado` (panel-heading + panel-body, texto preformateado o `ul`). El scraper las pasa a `##` y las evaluaciones a tabla.
- Se descartan datos de profesorado; "Actividades formativas… régimen de tutorías" se conserva (es metodología, sin nombres).
- Resultado: 62/62 md (3 sin_guia omitidas). Bloques: contents/learning_outcomes/assessment 62, bibliography 61, prerequisites 53 (ausente en 9 guías: la fuente no tiene "Requisitos").
- Re-ejecutable desde caché (0 peticiones de red).
