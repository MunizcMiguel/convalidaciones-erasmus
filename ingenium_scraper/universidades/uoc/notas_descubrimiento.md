# University of Crete (UoC) – Materials Science and Engineering (Πτυχίο, currículo «ΕΜΥ») – notas de descubrimiento (Fase 1)

## Grado elegido y por qué

- La Universidad de Creta **no tiene Ingeniería Mecánica**. (La Technical University of Crete, tuc.gr, es otra institución y queda fuera de alcance.)
- Su Escuela de Ciencias e Ingeniería (Σχολή Θετικών και Τεχνολογικών Επιστημών) tiene Física, Química, Matemáticas, Informática, Biología y **Τμήμα Επιστήμης και Μηχανικής Υλικών (ΤΕΜΥ) – Department of Materials Science and Engineering** (antes «Materials Science and Technology», ΤΕΤΥ). Es el único grado de ingeniería de la UoC y el más cercano a Mecánica: Mechanics of Materials (+ laboratorio), Mechanical Design, Transport Phenomena, Fluid Dynamics, Rheology, y un grupo de optativas «Mechanical Engineering and Materials Technology».
- Grado de primer ciclo: Πτυχίο, 4 años, **240 ECTS**. Desde 2024-25 rige el currículo nuevo con códigos **ΕΜΥ**; el antiguo (ΕΤΥ) sigue en la web para estudiantes anteriores: no usarlo.

## Fuentes (todas en `www.materials.uoc.gr`, WordPress)

| Qué | URL | Uso |
|---|---|---|
| Página «Οργάνωση Σπουδών» vía REST | `/wp-json/wp/v2/pages/2352` | enlace al Οδηγός Σπουδών más reciente (sección «Οδηγοί Σπουδών», enlace «Έτους 2025») |
| Οδηγός Σπουδών 2025 (PDF, griego, 95 pp., «Ακ. Έτος 2025-2026») | `/wp-content/uploads/2025/10/Π2.1_Οδηγός_Σπουδών_ΠΠΣ.pdf` | **Πίνακας Ι** (pp. 10-12): plan oficial — código, nombre griego, horas Θ-Α-Ε, Υ/Ε, ECTS, prerrequisitos, semestre de las obligatorias, grupos de optativas. También la regla de 240 ECTS |
| Página «Resources for Undergraduates» vía REST | `/wp-json/wp/v2/pages/14063` | enlace «Courses' Outlines (Engineering)» |
| **Courses' Outlines (Engineering)** (PDF, inglés, 183 pp., 2025) | `/wp-content/uploads/2026/07/new_courses-outline_en_eng.pdf` | guía docente de los 67 cursos ΕΜΥ: una ficha por curso con la plantilla oficial HQA/ΜΟΔΙΠ |

- robots.txt de `www.materials.uoc.gr`: responde 200 con cuerpo vacío → todo permitido. (`www.uoc.gr` bloquea ClaudeBot y pide Crawl-delay 10 al resto; no se usa.) No hace falta ningún otro host.
- Alternativas descartadas: (a) el custom post type `course` de la API REST (`/wp-json/wp/v2/course`) tiene una página HTML por curso, pero **en griego**, sin ECTS ni semestre estructurados y con evaluación reducida a una lista; (b) el PDF `courses_outlines_en_tech.pdf` es del currículo antiguo ΕΤΥ; (c) `course_outline_TEMY.zip` (2024) son DOCX en griego. Se prefiere el PDF inglés oficial y completo (regla del brief).

## Cómo se construye el catálogo (`discover_uoc.py`)

1. REST → URL del Οδηγός más reciente y del PDF de outlines (no hay URLs de PDF tecleadas).
2. Πίνακας Ι con `pdfplumber.find_tables()`; cada fila se compacta (fuera `None`/vacíos) y debe tener 8 valores. Las filas cabecera «Χ’ Εξάμηνο» fijan el semestre; tras la cabecera «Μαθήματα Επιλογής» las filas son optativas (semestre no fijado) y las filas de una sola celda son el grupo de optativas.
3. Del PDF de outlines: índice (código ΕΜΥ, título inglés) y, en el cuerpo, la página donde aparece la línea de título `ΕΜΥ - 101 Physics I…` (debe repetir el título del índice, para no confundirla con códigos citados en prerrequisitos) y el campo `SEMESTER` de la fila `COURSE CODE`.
4. `paginas_pdf = inicio-fin`: fin = página anterior al inicio del curso siguiente, **o esa misma página si el curso siguiente empieza a media página** (lo decide si antes de su título hay contenido que no sea separador de semestre/grupo o número de página). Muchos cursos comparten página con el siguiente.
5. Validación: códigos únicos; 6 semestres × 30 ECTS obligatorios = 180; 180 + 60 optativos = 240 (cifra leída del Οδηγός); todas las fichas del PDF tienen fila en Πίνακας Ι; rangos dentro del PDF.

### Resultado

71 filas: 30 obligatorias (180 ECTS), TFG `EMY-440` (12 ECTS, cuenta como optativa), 36 optativas (180 ECTS ofertados; el alumno cursa 60 ECTS de optativas incluido el TFG, semestres 7-8) y 4 filas `sin_guia`: Πρακτική Άσκηση Ι/ΙΙ (`PRA-001/002`, 10 ECTS cada una, de los que solo 5 cuentan para el título) y Δημοσίευση Ι/ΙΙ (`9I1/9I2`, 5 ECTS, publicación científica). Oferta total 402 ECTS frente a 240 exigidos.

- **Códigos**: `EMY-` + número de Πίνακας Ι; letras griegas transliteradas (`ΠΡΑ – 001`→`PRA-001`, `9Ι1`→`9I1`), porque `safe_name()` borra caracteres no latinos.
- **Nombres**: título inglés del índice del PDF de outlines (griego para las filas `sin_guia`). `idioma_pagina = en` (las 67 fichas), `el` en las 4 sin guía.
- **Semestre de optativas**: del campo `SEMESTER` de la ficha (7th/8th; una dice «8h»). TFG: semestre 7 (Πίνακας Ι), la ficha dice «7th and 8th».

## Estructura de una ficha (plantilla HQA, en inglés)

`ΕΜΥ - nnn Título` y cinco secciones fijas: **(1) GENERAL** (tabla etiqueta/valor: SCHOOL, ACADEMIC UNIT, LEVEL, COURSE CODE + SEMESTER, COURSE TITLE, actividades docentes con horas/créditos, COURSE TYPE, PREREQUISITE COURSES, LANGUAGE…, ERASMUS, URL), **(2) LEARNING OUTCOMES** («Learning outcomes» + «General Competences»), **(3) SYLLABUS**, **(4) TEACHING and LEARNING METHODS – EVALUATION** (DELIVERY, ICT, TEACHING METHODS con tabla de carga de trabajo, STUDENT PERFORMANCE EVALUATION), **(5) ATTACHED BIBLIOGRAPHY**. Sin nombres de profesores en la plantilla.

## Trampas

- La columna izquierda de la plantilla lleva **instrucciones para el autor** («if credits are awarded for separate components…», «Consult Appendix A…», la lista completa de competencias generales sin marcar, la lista de métodos de evaluación posibles…). No son contenido: hay que quitarlas sin quitar valores que se les parecen (p. ej. COURSE TYPE «GENERAL BACKGROUND» vs. la pista «general background, …»; «- Working independently» elegido por el autor vs. la misma frase en la lista).
- Mezcla de letras griegas y latinas en los códigos (`EΜY`, `ΕMΥ`, `ΕΜΥ`): las regex aceptan ambas.
- Etiquetas partidas en dos filas («LANGUAGE OF INSTRUCTION and» / «EXAMINATIONS:»), con punto final («DELIVERY.») o reescritas por el autor (EMY-413 pone el título en lugar de «COURSE TITLE»).
- En algunas fichas (p. ej. EMY-440) la celda valor empieza 4 pt por encima de la etiqueta y pdfplumber la mete en otra fila.
- Una cabecera usa guion largo: «(4) TEACHING and LEARNING METHODS – EVALUATION» (EMY-405).
- Subíndices de fórmulas (AB2, H2O, CH3NH3PbBr3) quedan en otra línea con la tolerancia vertical por defecto.
- Discrepancia de ECTS: la ficha de **EMY-461 y EMY-462 dice 6 créditos**, el Οδηγός (fuente del catálogo) dice 5. El catálogo usa el Οδηγός.

## Fase 2 – scraper (`scraper_uoc.py`)

- Un único PDF (caché) para todo; por curso se procesan `paginas_pdf`, recortando la primera página por debajo del título del curso y la última por encima del título del siguiente.
- Por página: tablas de primer nivel con `find_tables()` (fila a fila; celdas con tablas anidadas → tabla Markdown) y texto fuera de tablas con `extract_text_lines()`, ordenados por altura. Tolerancia vertical 5 pt para no separar los subíndices.
- Conversión guiada por la plantilla: secciones (1)-(5) → `##`; «Learning outcomes»/«General Competences» y los campos de (4) → `###`; (1) GENERAL → tabla «Field | Value» + tabla «Teaching activity | Weekly teaching hours | Credits» (fila «Total» con los totales); filas de celdas cortas consecutivas (carga de trabajo) → una tabla, también cuando un salto de página la corta en dos; celdas de texto consecutivas → un bloque con los saltos de línea originales; viñetas `•`/`▪` → `- `, viñeta de segundo nivel `o` → `  - `.
- Se eliminan las instrucciones de la plantilla (texto fijo en `TEMPLATE`, comparación sensible a mayúsculas e insensible a espacios/comas; fragmentos cortos en `SHORT_TEMPLATE`), números de página y separadores de semestre/grupo.
- `blocks_found`: contents/learning_outcomes/bibliography = la sección tiene contenido tras limpiar; assessment = STUDENT PERFORMANCE EVALUATION con valor; prerequisites = valor distinto de vacío o «-».

### Validación

- Muestra fija (`--sample 5`): EMY-111 (Matemáticas I), EMY-101 (Física I, teoría+lab, tabla anidada), EMY-342 (Mechanics of Materials), EMY-446 (Fluid Dynamics, optativa), EMY-440 (TFG). Comparadas con el PDF: completas; las tablas de carga y los porcentajes de evaluación se conservan.
- Control automático adicional (no incluido en el entregable): bolsa de palabras de cada rango recortado del PDF frente al Markdown. En los 67 cursos solo faltan las palabras de la plantilla, números de página y el título del curso siguiente.
- `--all`: **67 Markdown de 71 filas** (4 `sin_guia`), exit 0, re-ejecución solo desde caché. Revisión manual extra de EMY-347 (el más corto), EMY-348 / EMY-101 (los más largos), EMY-403, EMY-413, EMY-543 (valor partido por salto de página) y EMY-011 (líneas numeradas «(4) …» dentro del texto): correctos tras los ajustes.
- Bloques ausentes (hechos, no fallos): `prerequisites` falso en 26 cursos (la ficha pone «-» o nada); `assessment` falso en **EMY-342**, cuya ficha deja vacío STUDENT PERFORMANCE EVALUATION (también DELIVERY).
- Problema de `common/util.scrub_pii` (no corregido aquí, fuera de esta carpeta): falsos positivos. «Study at home. Problem solving…» se convierte en `[email]` (EMY-346, EMY-404, en la tabla de carga) y la cita «Anal. Chem. 79 (2007) 4215» en `[phone]` (EMY-243).
