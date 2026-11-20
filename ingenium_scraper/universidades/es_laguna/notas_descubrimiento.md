# es_laguna — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (ULL), Escuela Superior de Ingeniería y Tecnología (único centro; RUCT 2501898), plan 2020. Curso 2026-27.
- Plataforma: Portal de Guías Docentes de la ULL (`www.ull.es/apps/guias/`, Django). robots.txt de www.ull.es: las reglas (`Disallow: /*?`, `/portal/agenda/`, Crawl-delay 10) van a una lista de bots con nombre; el resto de agentes no está restringido. No se usan URLs con `?`.
- Catálogo: `/apps/guias/guias/view_degree/Grado%20en%20Ingenier%C3%ADa%20Mec%C3%A1nica/` — acordeones "Curso N" > "Primer/Segundo cuatrimestre"/"Anuales" con `código - nombre` y enlace `/guias/view_guide/{id}/` (id interno que **cambia cada curso**: p. ej. Física I = 45585 en 2026-27, 42728 era la guía anterior). El listado no da créditos ni carácter: se leen del apartado 1 del PDF de cada guía (`/guias/print_guide/{id}/`), por eso el discover hace 1 + 38 peticiones. 38 filas: FB 60, OB 144, prácticas externas 12, TFG 12 = RUCT; 24 ECTS optativos ofertados (se cursan 12).
- Guía: PDF ReportLab (con texto). La página 1 es solo la portada (los datos empiezan en la 2). Apartados 1-11 numerados; los listados internos también numeran "1. …", por eso los apartados se reconocen por título y en orden. Se descartan 3 (Profesorado: nombres, teléfonos, correos, tutorías) y 11 (cronograma).
- Idioma: castellano (algunas asignaturas indican 0,3 ECTS en inglés; no hay versión en inglés separada).

## Fase 2
`scraper_es_laguna.py` (--sample/--all/--codes).
