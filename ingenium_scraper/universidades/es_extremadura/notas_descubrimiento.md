# es_extremadura — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (Rama Industrial), UEx, Escuela de Ingenierías Industriales (Badajoz); RUCT 2500928. Curso 2026-27.
- Catálogo: `https://eii.unex.es/titulaciones/0818/` (WordPress): tablas "Curso 1..4" + "Asignaturas optativas" con nombre, carácter, ECTS y semestre. El enlace de cada nombre lleva `?subjectid={codigo}` (código oficial de 6 dígitos); la ficha de la asignatura contiene el enlace "Plan docente" al PDF `.../wp-content/uploads/sites/8/{año}/{mes}/plan0818-{codigo}-2026-27.pdf` (la carpeta mes/año varía → se lee de cada ficha; el discover hace 1+52 peticiones). 52 filas; FB 66, OB 138, TFG 12 = RUCT; 102 ECTS optativos ofertados, se cursan 24.
- Robots: eii.unex.es y www.unex.es solo vetan /wp-admin/.
- Guía: PDF de "Plan docente" con texto, pero fuentes subconjunto mal codificadas: `(cid:NN)` = carácter chr(NN+29) (se decodifica); en algunos PDF las palabras salen sin espacios (se usa `x_tolerance=1.5` y se comparan los títulos sin espacios); números de página pegados al final del título ("Resultados de aprendizaje6").
- Se descartan: Profesorado/coordinación (nombres, despachos, correos), matriz de competencias (texto rotado ilegible) y matriz de metodologías (X).
- **6 PDF ilegibles** (fuente con codificación propia, texto basura; requerirían OCR): 501059 Matemáticas II, 501333 Tecnología Energética, 501099 Organización Industrial, 501336 Estructuras Metálicas y de Hormigón, 501340 Metalurgia y Siderurgia, 501335 Cimentaciones y Arquitectura Industrial. Quedan en el catálogo con su URL pero sin Markdown.
- La plantilla no tiene apartado de requisitos/prerrequisitos → `prerequisites=false` en todas.

## Fase 2
`scraper_es_extremadura.py` (--sample/--all/--codes): 46 de 52 guías.
