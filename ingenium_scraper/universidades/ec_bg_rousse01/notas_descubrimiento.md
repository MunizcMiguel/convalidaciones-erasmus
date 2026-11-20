# ec_bg_rousse01 – University of Ruse «Angel Kanchev» – Computer Aided Design in Mechanical and Instrument Engineering (Bachelor, 4 años = 240 ECTS)

## Titulación elegida
- Ruse no tiene un grado «Mechanical Engineering». La Facultad de Ingeniería Mecánica y de Fabricación (FMME) ofrece 4 bachelors: Manufacturing Equipment and Technologies; **Computer Aided Design in Mechanical and Instrument Engineering**; Materials Technology and Material Science; Industrial Engineering. Se elige el 2.º: titulación profesional «mechanical engineer», con Mecánica, Resistencia de materiales, Mecanismos y máquinas, Elementos de máquinas, Termotecnia, Metrología, etc.; especialización A (Mechanical Engineering) / B (Instrument Engineering) en los términos 6-7.
- Grado de 4 años (8 términos), 240 ECTS (no 180).

## Fuente
- «Erasmus ECTS Information Package» de la FMME: `https://www.uni-ruse.bg/en/education/students/ECTS%20packages/Faculty%20of%20Mechanical%20and%20Manufacturing%20Engineering.pdf` (221 págs., inglés; enlazado desde `https://www.uni-ruse.bg/en/education/students/ECTS-package`). Host www.uni-ruse.bg: PoliteClient no encontró bloqueo en robots.txt. El hint del Excel (erasmus.uni-ruse.bg) es solo el sitio Erasmus; los subdominios cdo/fbm antiguos devuelven 404.
- El PDF es antiguo (cifras de matrícula 2008/09): el plan vigente podría diferir. Pág. 87-88: CURRICULUM por términos (dos columnas); págs. siguientes: descripción de cada asignatura (`CÓDIGO Título` + `ECTS credits: N Weekly classes…` + Departments involved + Lecturers + Abstract + Course content + Teaching and assessment).

## Reglas
- Curriculum leído por geometría de palabras (código de 4 cifras a x≈67 / ≈300; ECTS = último número de la fila; término = cabecera «Nth term» previa en la misma columna). Excluidos Sports (1102, sin ECTS) y «Elective Foreign Language» (sin código).
- Descripciones: se toma la primera del PDF con ese código (las comunes se repiten entre grados); cabeceras con variantes («ЕСТS» con letras cirílicas, código con «:»).
- 58 asignaturas, 264 ECTS brutos (>240: las optativas de los grupos A/B son alternativas). Sin descripción: 3331 y 3312 (Specialized practice, 2 ECTS) → `sin_guia`.
- Los nombres de la ficha tienen erratas de origen («Higer mathematics», «Mathematcs»), se copian tal cual.

## Fase 2
- `scraper_ec_bg_rousse01.py --all`: 56 de 58 filas con Markdown (2 sin_guia), 0 fallos. Se eliminan «Lecturers» (nombres, tel., correos). Revisado contra el PDF: 2071 (Mechanics 1), 2402, 3356 (Diploma Project) y las variantes con «Teaching and learning methods» (2068).
- Siempre ausentes: learning_outcomes (solo «Abstract»), bibliography y prerequisites; assessment = tipo de examen + «Teaching and assessment».
