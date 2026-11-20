# ec_cz_brno01 — VUT Brno, Fac. de Ingeniería Mecánica (FSI)

## Fase 1
- Titulación: **Fundamentals of Mechanical Engineering (B-STI-A)**, Bc., 3 años, en inglés. Es el grado en inglés más próximo a Mecánica (Mechanical Engineering en inglés solo existe como máster N-ENG-A; B-KSI-P y Mechatronics solo en checo).
- Fuente: `https://www.fme.vutbr.cz/en/studenti/programy/program/9646` (HTML estático, una `<table>` por curso/semestre con `caption` "N. year of study, winter|summer semester"). La web de FSI es ajena al `fce.vutbr.cz` (Civil) del hint.
- Código = columna "Abbreviation" (único, 48 filas); créditos = columna Cr.; Com. = Compulsory / Compulsory-optional(Elective).
- ECTS: obligatorias 161 + TFG (Bachelor Project, 6) = 167; optativas ofertadas 50 (se eligen 13 → 180).
- robots.txt (www.vut.cz y fme.vutbr.cz): sin veto en `/en/studenti/`.

## Fase 2
- Ficha: `/en/studenti/predmety/{id}` (HTML, `div.b-detail`; etiqueta en `p.b-detail__subtitle` / `h4`, valor en el `grid__cell` siguiente; las subsecciones "Lecture/Exercise" con su Syllabus llevan `###`).
- Se eliminan Supervisor y Teacher/Lecturer. No hay bibliografía en ninguna ficha (hecho de la fuente) → `bibliography: false` en todas.
- Las asignaturas de 0 ECTS (GEN1, GEN2, TEN1, TEN2) no traen la etiqueta de créditos.
- Resultado: 48/48 Markdown.
