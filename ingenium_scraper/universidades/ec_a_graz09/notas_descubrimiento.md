# ec_a_graz09 – FH JOANNEUM (Graz) – Fahrzeugtechnik / Automotive Engineering B.Sc. (catálogo PARCIAL)

## Titulación elegida
- FH JOANNEUM (Department Engineering, Graz) no ofrece Ingeniería Mecánica (sus grados: Electronics and Computer Engineering, Aviation, Automotive Engineering...). El más afín es **Fahrzeugtechnik / Automotive Engineering** (B.Sc. in Engineering, 6 sem., 180 ECTS; Mecánica, Termodinámica, Motores, CAD, Resistencia de materiales).
- El `web_hint` del Excel (upf.edu) era de otra universidad (Pompeu Fabra); se ignoró.

## Fuente
- `https://www.fh-joanneum.at/fahrzeugtechnik/bachelor/en/my-studies/curriculum/` (HTML estático, inglés; PoliteClient no encontró bloqueo en robots.txt): un acordeón por semestre (`h4` «Nth semester») y un `button.course-item` por asignatura con cabecera «Título | Tipo | Coursecode: N», idioma de instrucción, ECTS, SWS y, en `div#course-{slug}`, una descripción de 1-3 líneas.
- Código = Coursecode oficial (180679xxx). 55 filas, 180 ECTS exactos. Dos asignaturas comparten nombre pero tienen códigos distintos (p. ej. «Chassis Engineering and Vehicle Dynamics» 501/502, «Scientific Work, Bachelor's Thesis» 602/603/604).
- Un único documento; las URL por asignatura son anclas `#course-slug`.

## Limitaciones (por eso `parcial`)
- Solo descripción breve de contenidos. No hay resultados de aprendizaje, evaluación, bibliografía ni prerrequisitos públicos (los detalles viven en el portal interno).
- La mayoría de asignaturas se imparten en alemán, aunque la ficha pública está en inglés.
- 180679603 sin descripción → `sin_guia`.

## Fase 2
- `scraper_ec_a_graz09.py --all`: 54 de 55 filas con Markdown (1 `sin_guia`), 0 fallos. Revisado contra la página: Engineering Mechanics 1 (Statics), Scientific Work Bachelor's Thesis, Internship; bloque presente en todas: contents.
