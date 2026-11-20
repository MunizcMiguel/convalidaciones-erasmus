# ec_uk_liverpo02 – Liverpool John Moores University – BEng (Hons) Mechanical Engineering (catálogo PARCIAL, sin Fase 2)

## Titulación
- BEng (Hons) Mechanical Engineering (código 32120BGH; 3 años, 360 créditos UK ≈ 180 ECTS; créditos UK / 2). Niveles 4/5/6 = cursos 1/2/3. Existe año opcional de prácticas (5111MECH) y de estudio en el extranjero (5112MECH): no catalogados.

## Fuente del catálogo
- Programme Specification (PDF, 7 págs.): `https://prodcat.ljmu.ac.uk/KIS/32120-3500006811.pdf` (programa 32120-3500006811 v03.01). Host prodcat.ljmu.ac.uk: PoliteClient lo permite. Tabla «Level N / Core | Option | Award Requirements»; el script lee las celdas con `find_tables()` + recorte y concatena las continuaciones de tabla de la página siguiente (Level 5 salta de página en medio del título «Materials and / Processes»).
- 26 módulos: L4 7 core (60 ECTS), L5 7 core (60), L6 3 core (40) + 9 opcionales (se eligen 40 créditos UK = 20 ECTS). Core = 160 ECTS equiv.; con las opciones elegidas, 180.
- Otros PDF de prodcat (`KIS/36777.pdf` Programme Information 2022.01 con códigos *MDLBHG; `KIS/42120.pdf` con foundation year) son de otras variantes y no se usan.

## Bloqueo (regla de parada)
- `www.ljmu.ac.uk` y `cm-prod.ljmu.ac.uk`: PoliteClient lanza `RobotsBlocked` (incluso para robots.txt → trato deny-all), y de ahí cuelgan la página del curso y los «module details». No se rodea.
- En prodcat.ljmu.ac.uk solo se localizaron Programme Specifications, no module specifications (buscadores no devuelven ninguna ficha de módulo).
- Resultado: `estado: parcial`, 26 filas `sin_guia`, sin scraper ni Markdown.

## No verificado
- Qué módulos del nivel 6 se ofertan cada año; duración (anual/semestral) y semestre de cada módulo; si hay module specifications públicas en prodcat con una URL no localizada.

## Fase 2 (2026-11-20) — RESUELTA por otra vía
- Las module specifications están en el Course Catalogue de LJMU (CourseLoop): `https://coursecatalogue.ljmu.ac.uk/module/2025/{CODE}` (robots: `Allow: /`). Es una app Next.js: todo el contenido va en `<script id="__NEXT_DATA__">` → `props.pageProps.pageContent` (overview, description, learning_experiences, unit_learning_outcomes, assessment_data con peso %, learning_activity). El script comprueba `pageContent.code == code`.
- `proformas.ljmu.ac.uk/{CODE}.pdf` (visto en buscadores) responde 401: no se usa. Se omite `module_leader`.
- `discover_*.py` ahora fija `url_guia_docente` = catálogo/2025 y `tipo_fuente: html`, `estado: ok`. `scraper_ec_uk_liverpo02.py`: 26/26 Markdown (en inglés). Bloques: contents/learning_outcomes/assessment presentes; bibliography y prerequisites vacíos en todas (el catálogo no los publica). Créditos UK/2 = ECTS aprox.
