# UPM — Grado en Ingeniería Mecánica (notas)

## Fase 1
- Plan 56IM (RUCT 2502150, RD 1393/2007), ETSIDI (único centro). Fuente: API JSON pública `https://www.upm.es/wapi_upm/academico/comun/index.upm/v2/plan.json/56IM/asignaturas?anio=202627`.
- 127 asignaturas ofertadas en 2026-27 (14 con ofertada='N' excluidas) = 614 ECTS ofertados vs 240. Básica 60, obligatorias 66 y TFG 12 coinciden con el RUCT; 476 ECTS de optativas ofertadas (se cursan 102: itinerarios, optativas cedidas, prácticas, movilidad, oferta en inglés).
- Guías en PDF por asignatura en GAUSS, comprobadas una a una: 58 de 2026-27, 5 de 2025-26 (la nueva no está publicada), 64 `sin_guia` (incluye TFG, prácticas y bolsas de movilidad). Lista en `meta.notas`.

## Fase 2
- Guía: `https://www.upm.es/comun_gauss/publico/guias/2026-27/GA_56IM_{codigo}_ES_2026-27.pdf` (2025-26: `.../2025-26/2S/GA_56IM_{codigo}_2S_2025-26.pdf`). PDF con texto (pdfplumber), 9–44 págs.
- Formato nuevo (2026-27): encabezados en mayúsculas (RESULTADOS, DESCRIPCIÓN, TEMARIO, ACTIVIDADES, CRITERIOS DE EVALUACIÓN, RECURSOS, OTRA INFORMACIÓN, ODS). Se descartan cabecera por página ("G.A. ..."), pie con firma electrónica, rejilla de semanas, "PLANIFICACIÓN SEMANAL" y el COORDINADOR/A (nombre + email). De ACTIVIDADES se conservan nombre, presencialidad/duración, ponderación y nota mínima.
- Formato antiguo (las 5 guías 2025-26): secciones numeradas 1–9 ("1. Datos descriptivos", "2. Profesorado"…). Se descartan Datos, Profesorado y Cronograma. Las tablas de evaluación salen con columnas desordenadas (texto de celdas multilínea) pero con pesos y notas mínimas intactos. Una guía (565005801, 2025-26) solo existe en inglés: `source_language=en`.
- Trampa: `(cid:N)` y NULs en el texto de algún PDF → se eliminan.
- 63/63 md. Bloques: contents/learning_outcomes/assessment/bibliography 63, prerequisites 53 (ausente cuando "—").
- No verificado: fidelidad línea a línea de las tablas de evaluación del formato antiguo; menciones residuales a "el coordinador" en texto libre (sin nombres).
