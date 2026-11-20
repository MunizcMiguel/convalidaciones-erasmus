# es_jaen — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica, UJA, Escuela Politécnica Superior de Jaén (primer centro del RUCT 2501880; también se imparte en la EPS de Linares, no incluida: optativas distintas). Curso 2026-27.
- Catálogo: `https://eps.ujaen.es/grados/grado-en-ingenieria-mecanica/asignaturas-y-profesorado` (HTML estático): 10 tablas (curso × cuatrimestre) + 2 de optativas. Cada nombre enlaza a la ficha. Código oficial de 8 dígitos. 49 filas: FB 60, OB 138, TFG 12 = RUCT; 90 ECTS optativos ofertados (se cursan 30). Los huecos "Optativa 1-5" de 4.º no tienen código y se ignoran; "Prácticas externas" (13413012) aparece en dos cuatrimestres → se toma la primera.
- Robots: eps.ujaen.es (robots estándar, no veta /grados/), uvirtual.ujaen.es sin robots.txt (404).
- Guía: `https://uvirtual.ujaen.es/pub/es/informacionacademica/catalogofichasdocentesasignaturas/p/2026-27/4/134A/{codigo}/es/2026-27-{codigo}_es.html` — **la URL acaba en .html pero el servidor devuelve un PDF** (con texto). Versión inglesa "Syllabus" ignorada.
- Plantilla: apartados en mayúsculas; se descartan PROFESORADO (nombres, correos, teléfonos, despachos), cláusulas, contingencia, necesidades específicas, igualdad y ODS; se quitan cabecera/pie de página y los enlaces de tutorías/horarios.
- Cuatro asignaturas comunes (Electrotecnia, Ciencia e ingeniería de materiales, Elasticidad y resistencia de materiales, Automática industrial) enlazan la ficha de otro grado de la EPS (código distinto, mismo nombre): se aceptan si el nombre coincide.

## Fase 2
`scraper_es_jaen.py` (--sample/--all/--codes). 49/49 guías.
