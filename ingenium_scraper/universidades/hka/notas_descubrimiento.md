# HKA – Maschinenbau (B.Eng.), "MABB" – notas de descubrimiento (Fase 1)

## Fuente elegida
- Grado: **Maschinenbau B.Eng. (MABB)**, Fakultät MMT, 7 semestres, 210 ECTS. Es el bachelor general de Maschinenbau (con 4 Vertiefungen internas A–D); no se han tomado otros grados afines de la facultad.
- Página del grado: `https://www.h-ka.de/mabb`. Enlaza dos PDF que el script localiza por `href` (contiene `Modulhandbuch` / `_SPO_`):
  - **Modulhandbuch** (fuente principal, 74 págs., Stand 01.04.2026):
    `https://www.h-ka.de/fileadmin/Hochschule_Karlsruhe_HKA/Bilder_FK-MMT/Dokumente/Modulhandbuecher/Modulhandbuecher_2026/20260401_Modulhandbuch_MABB.pdf`
  - **SPO Version 8** (válida desde 01.09.2026, 14 págs.; tablas del plan en págs. 6–12):
    `https://www.h-ka.de/fileadmin/Hochschule_Karlsruhe_HKA/Bilder_FK-MMT/Dokumente/SPO/SPO_2026/HKA_FK-MMT_MABB_SPO_V8_2026-09-01.pdf`
- No se encontró base de datos web de módulos ni endpoints JSON: todo vive en un único PDF -> `tipo_fuente="pdf_compartido"`.
- **Idioma: solo alemán.** La versión inglesa de la página del grado (`/en/study/study-in-german/bachelor/mechanical-engineering/profile`) no enlaza ningún Modulhandbuch en inglés.
- robots.txt no bloqueó ninguna de las 3 URL usadas.

## Cómo se construye el catálogo
- Un módulo = página que contiene la línea `Modulbeschreibung:`; su primera línea es `MABBnnn[A-D] – Nombre` (código oficial, no hay códigos derivados).
- ECTS: `Modulumfang (ECTS): N CP`; semestre: `Einordnung (Semester): N. Semester`.
- `paginas_pdf` = página física del PDF (1-indexada) desde la cabecera del módulo hasta la página anterior a la siguiente cabecera. **Página impresa en el pie = página física − 1** (la portada no se numera). El script comprueba que coincide con el índice (Inhaltsverzeichnis, págs. 2–3).
- La SPO se usa para: (a) `MABB450`/`MABB650` (Schwerpunkt 1/2), que no tienen ficha -> `sin_guia`; (b) ECTS de `MABB640A`, cuya ficha dice `Modulumfang (SWS): 4` en vez de ECTS (se toman 6 CP de la Tabla 3A); (c) contraste de ECTS del resto.
- Total: 38 filas, 246 ECTS brutos = 198 comunes + 4 Vertiefungen × 12. Un estudiante cursa una Vertiefung (440X + 640X) -> 210.

## Estructura de una ficha de módulo (texto plano, sin tablas reales; una columna)
Bloque de módulo (etiquetas `Etiqueta:` al inicio de línea):
- `SPO-Bezeichnung`, `Modulverantwortliche(r)`, `Modulumfang (ECTS)`, `Einordnung (Semester)`
- `Inhaltliche Voraussetzungen` y `Voraussetzungen nach SPO` -> prerrequisitos (a menudo `-`)
- `Lernergebnisse und Kompetenzen` -> resultados de aprendizaje (a nivel de módulo)
- `Prüfungsleistungen` -> evaluación (a nivel de módulo; en módulos con varias LV se desglosa por código `MABBnn1:`, a veces con pesos tipo `MABB241 : MABB242 = 2 : 1`)

Después, uno o varios bloques de **Lehrveranstaltung** (58 LV en 36 módulos), cada uno con:
- `Lehrveranstaltung`, `LV-Bezeichnung` (MABBnn1, nn2…), `Dozent/in`, `Umfang (SWS)`, `Turnus`, `Art und Modus`, `Lehrsprache`
- `Studieninhalte` -> contenidos/temario
- `Empfohlene Literatur` -> bibliografía
- `Anmerkungen`

## Trampas
- **No hay campo de workload** (ni horas presenciales/autoestudio). Solo ECTS y SWS; la introducción (pág. 5) fija 1 CP = 30 h. No inventar horas: como mucho derivar total = ECTS × 30.
- Los ECTS son solo del módulo; las LV no llevan ECTS, solo SWS.
- Contenidos y bibliografía están **por LV**, no por módulo: hay que concatenar todos los bloques LV del rango de páginas.
- Los módulos ocupan 1–3 páginas y los bloques LV se cortan entre páginas; cada página termina con el pie `Modulhandbuch MABB Stand: 01.04.2026; SPO MABB Version 8 vom 12.02.2026 <n>` (eliminarlo).
- `pdfplumber.extract_tables()` devuelve "tablas" espurias (marcos); usar `extract_text()`.
- Viñetas perdidas en la extracción (listas quedan como líneas sueltas); algunas líneas de contenido contienen `:` y parecen etiquetas (p. ej. `WERKSTOFFKUNDE:`): reconocer solo la lista cerrada de etiquetas de arriba.
- Variantes de etiquetas: `SPO-Bezeichnung` sin dos puntos (MABB320), `Modulverantwortlicher`/`Dozentin`; `Einordnung (Semester): 2` sin "Semester"; `Modulumfang (ECTS): 6` sin "CP".
- Erratas en el campo `SPO-Bezeichnung` de la fuente (MABB440C dice "MABB440B", MABB640B dice "MABB640C", MABB610 dice "Entwicklungsprojekt"; MABB640A lista LV como MABB611A/612A). El catálogo usa el código de la **cabecera**, que coincide con el índice.
- Nombres repetidos: MABB440B y MABB640B se llaman ambos "Robotik und Produktion", y MABB440C/640C "Konstruktion" (la SPO los llama "… 1" / "… 2"). Distinguir por código.
- Nombres de cabecera difieren a veces de la SPO (p. ej. "CAD-CAM" vs "CAD/CAM", "Technische Mechanik Festigkeitslehre" vs "Technische Mechanik 2"). Se conserva el del Modulhandbuch.
- `MABB710 Wahlpflichtmodul` solo contiene reglas de elección (sin Lernergebnisse ni LV). `MABB450/650 Schwerpunkt` se rellenan con módulos de otras Vertiefungen/grados de la facultad MMT: no hay catálogo cerrado en estos documentos.
- Vertiefung A (Aeronautical Engineering): LV con títulos en inglés, pero la ficha está en alemán. `Lehrsprache` suele ser "deutsch" o "deutsch oder englisch".
- La SPO V8 aplica a quienes empiezan a partir del 01.09.2026; cohortes anteriores siguen la SPO V7 (2019), con otro Modulhandbuch (no catalogado).

## Fase 2 – scraper (`scraper_hka.py`)
- **Enfoque:** `pdfplumber.extract_text_lines()` (texto + geometría) sobre el rango `paginas_pdf` de cada módulo; se elimina el pie `Modulhandbuch MABB Stand: …` y se cose todo como un único flujo de líneas. Las etiquetas se reconocen con una **lista cerrada** (solo en líneas sin sangría). Salida: `# código – nombre`, `## Modulbeschreibung`, un `## Lehrveranstaltung: …` por LV; campos cortos como `- **Etiqueta:** valor`, campos largos como `### Etiqueta`.
- **Saltos de línea:** no hay sangría ni viñetas en muchas listas, así que se decide por geometría: una línea continúa la anterior solo si su primera palabra **no cabía** en la anterior (x1 + espacio + ancho > margen 520 pt). Guion de corte: se une sin guion si sigue minúscula (`An-`/`wendungen`), se conserva si sigue mayúscula (`Springer-`/`Verlag`, `STACK-`/`Aufgaben`) o `und/oder`.
- **Listas:** viñetas `•` (x0≈95) -> `- `; sus continuaciones van sangradas; una línea sin sangría nunca continúa una viñeta. Sin viñetas: rachas de ≥2 líneas lógicas que no acaban en `.:!?` -> lista; en `Empfohlene Literatur` cada línea lógica es una referencia.
- **Datos personales:** se descartan enteros `Modulverantwortliche(r)` y `Dozent/in` (incluida su segunda línea sangrada). Los autores de la bibliografía se conservan.
- **Autocontrol:** el script falla si la secuencia de caracteres alfanuméricos del Markdown no coincide con la de los campos parseados, o si lo parseado no cubre el texto de las páginas.
- **Muestra piloto:** `MABB110` (básica 1.º), `MABB310` (Thermodynamik, 3 págs.), `MABB440A` (Vertiefung A, 2 LV), `MABB150` (3 LV en 3 págs.), `MABB740` (Bachelor-Thesis). Las 5 revisadas a mano contra el texto del PDF.
- **Rarezas encontradas:**
  - MABB310: el subíndice de `h_{1+X}` sale como línea aparte en cuerpo pequeño; se reinserta como `ℎ_{1+𝑋}`. Símbolos de fórmula en cursiva matemática Unicode (𝑝, 𝑇…), se dejan tal cual.
  - MABB150: `Studieninhalte:` repetido dentro del propio campo (se deja como texto); `Experimentierlabor:` dentro de Lernergebnisse no es etiqueta.
  - Cortes de página en mitad de campo (p. ej. `Prüfungsleistungen:` al final de pág. 24 y su valor en la 25; título de LV al final de pág. 43).
  - MABB740: `Umfang (CP)` en vez de `Umfang (SWS)`; responsables genéricos ("Studiendekan").
  - `prerequisites` = false cuando ambos campos de Voraussetzungen valen `-` (MABB110, MABB150): el campo existe pero está vacío.
- **Limitación conocida:** si una línea llega casualmente hasta el margen derecho y la siguiente es un elemento nuevo sin viñeta, se unen (no se pierde texto). Visto en MABB150 (dos elementos de lista unidos: "…zu verstehen, geeignete Lösungsansätze…") y MABB440A ("Die Modulnote…" queda en el párrafo de MABB442A). Mitigado para `MABBnnn:` y para referencias `Apellido, N.`.
- **Sin verificar:** los otros 31 módulos (no se ha ejecutado `--all`). Etiquetas vistas solo en el inventario y no en la muestra: `Modulumfang (SWS)` (MABB640A), `Regelungen für das Wahlmodul` (MABB710, sin contenidos ni Lernergebnisse -> saldrá con aviso), `SPO-Bezeichnung` sin dos puntos (MABB320), `Dozentin`/`Modulverantwortlicher`. Otros tipos de viñeta o subniveles no aparecen en la muestra.
