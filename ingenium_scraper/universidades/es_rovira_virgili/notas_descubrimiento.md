# es_rovira_virgili — notas de descubrimiento
- Título: Grado en Ingeniería Mecánica (URV, ETSEQ Tarragona; RUCT 2501675, plan 2010). Curso 2026-27.
- Fuente: Guía docente URV `https://guiadocent.urv.cat/docnet/guia_docent/index.php?centre=20&ensenyament=2022&consulta=assignatures&idioma=cast` (HTML; tablas anidadas por curso con Código, Nombre, Periodo, Tipo, Cr.totales). Hay un solo plan. 54 asignaturas; básica 60, obligatorias 141, TFG 12 = RUCT; ofertadas 42 ECTS optativos + 12 de prácticas externas optativas (RUCT: 27 optativos cursados).
- Guía: página por asignatura (`&assignatura={codigo}&idioma=cast`) con solo datos identificativos (coordinador, profesores y correos: se descartan) y descripción general; cada apartado es otra página `&fitxa_apartat=N` (55 Competencias, 56 Resultados, 57 Contenidos, 58 Planificación, 59 Metodologías, 60 Atención personalizada, 61 Evaluación, 62 Fuentes, 63 Recomendaciones). Maquetación con tablas anidadas: el contenido son las tablas hermanas posteriores a la tabla de navegación.
- robots.txt: guiadocent.urv.cat sin veto (www.urv.cat solo veta /frases y /crm).
- Trampas: tablas de maquetación (DWLayoutTable) → se aplanan; la evaluación es una tabla con celdas anidadas (competencias) → se unen con «;»; guía no publicada en castellano (Laboratorio de máquinas térmicas) o sin apartados (2 de movilidad) → «omitida».

## Fase 2
`scraper_es_rovira_virgili.py`: 51/54 Markdown (3 omitidas: sin guía publicada). Se descargan 7 apartados por asignatura (no Planificación ni Atención personalizada). Ausente a veces: Recomendaciones (prerrequisitos).
