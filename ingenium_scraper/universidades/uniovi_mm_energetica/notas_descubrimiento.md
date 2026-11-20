# uniovi_mm_energetica — notas de descubrimiento

Máster Universitario en Ingeniería Energética. Plataforma SIES de uniovi.es (Liferay, portlet UnioviSiesWeb), la misma que `uniovi` (Mecánica) y `uniovi_giti`: ver `../uniovi/notas_descubrimiento.md` para el flujo asignatura → `asignaturaId` → `serveGuiasDocentes` → fragmento `/GuiaDocente`.

## Fase 1
- Fuente: `https://www.uniovi.es/estudia/masteres/ingenieriayarquitectura/energetica` (HTML estático, `#asignaturasAccordion`, igual que en los grados). robots.txt de www.uniovi.es solo veta /buscador, /login, /group/, /web/guest/, /actualidad/duo: todo permitido. Único host.
- Diferencias frente a grados: (a) el bloque de plan puede ser `cualquiera-temporalidad-…` (sin curso fijo) y el código lleva `-C-` (Complementos de Formación) o `-0-` en lugar de un nº de curso → `curso`/`semestre` quedan `null` cuando no hay curso; (b) nuevo carácter «Complementos de Formación» → `complementos_formacion`; «Trabajo Fin de Carrera» = TFM → `tfg`; (c) `meta.nivel = "master"`.
- Resultado: 19 asignaturas, curso académico vigente más reciente con guías = ver `meta.curso_academico`. ECTS: 60 ECTS: oblig. 30 + TFM 12 cuadran; optativas ofertadas 36 (se cursan 18).
- Notas: Sin huecos. Las guías traen tablas de horas grandes (p. ej. 1-001) que se conservan como tablas Markdown.
- Script: `discover_uniovi_mm_energetica.py` (copia parametrizada del de `uniovi_giti`); catálogo en `catalogo_urls.json` validado con `Catalog` (sin duplicados, todas las filas con URL, desglose oficial de obligatorias/TFM/prácticas comprobado).

## Fase 2 (`scraper_uniovi_mm_energetica.py`)
- Misma base que `scraper_uniovi_giti.py`: Markdown con `# nombre`, «Datos de la asignatura» y un `##` por apartado; sin Coordinación/Profesorado. `--sample N` se deriva del catálogo (obligatoria de 1.º, complemento, obligatoria final, optativa, TFM, prácticas).
- Novedad para másteres impartidos en inglés: si los apartados de la guía española están vacíos o solo contienen el aviso «asignatura impartida en inglés, seleccione EN», se pide la versión `/en/` con un **segundo cliente** (cookies aparte, por la cookie de idioma de Liferay) y se escribe esa versión, con la línea «Idioma de la guía: inglés» y `source_language: en`. Los títulos de apartado siguen en español.
- Resultado: 19 Markdown de 19 filas. Validado leyendo muestras (texto completo, tablas de horas intactas, sin chrome de página). Bloques ausentes comunes: bibliografía en Prácticas/TFM; contenidos en TFM.
- Huecos / bloqueos: Sin huecos. Las guías traen tablas de horas grandes (p. ej. 1-001) que se conservan como tablas Markdown.
- Sin 403/429 ni reintentos en la descarga completa. Fase 3 NO ejecutada (por orden del usuario).
