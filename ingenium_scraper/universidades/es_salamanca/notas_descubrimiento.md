# es_salamanca — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (USAL), RUCT 1500736 (RD 822/2021). Se toma el centro primero del RUCT: **E.P.S. de Zamora** (el otro es la E.T.S. de Ingeniería Industrial de Béjar, nodos 247528/262031). Curso 2026-27.
- Planes: hay un plan (2026) [UXXI 410] (nodo 262751 en Zamora) que solo publica 1.º (9 asignaturas) y el plan 2010 [UXXI 265] (nodo 250991) con los cuatro cursos. Se usa el plan 2010, el único completo (desviación del criterio «plan que admite nuevo ingreso», documentada en el catálogo).
- Fuente: `https://guias.usal.es/node/250991` (Drupal, «Curso 2026/2027»; robots.txt sin veto): `ul.asignatura-curso` por curso con enlace al nodo, carácter y créditos. 56 asignaturas; básica 60, obligatorias 150 y TFG 12 («Proyecto fin de carrera») = RUCT; 57 ECTS optativos ofertados (RUCT 18). Las optativas figuran en 4.º. Código = «Código» UXXI de «1. Datos de la asignatura» (106NNN); el nodo (`/node/{id}`) es la guía.
- Guía: HTML `https://guias.usal.es/node/{id}`: `div.cab-epigrafe` (título numerado) + `div.datos-epigrafe-*`. Secciones 2 Recomendaciones previas, 3 Objetivos, 4 Competencias, 5 Contenidos, 6-7 Metodologías, 8 Recursos (bibliografía), 9 Evaluación. Se descarta «Datos del profesorado» (nombre, despacho, tutorías, correo, teléfono). Algunas guías tienen vacías las secciones 7 y 9 en el origen (7 sin evaluación).

## Fase 2
`scraper_es_salamanca.py`: 56/56 Markdown. Sin evaluación en 7, sin bibliografía en 2, sin contenidos en 1; requisitos previos ausentes en 5.
