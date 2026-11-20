# ec_ro_timisoa04 — Universitatea Politehnica Timișoara (UPT)

**Titulación:** Inginerie Mecanică (Mechanical Engineering), licență, 4 años / 240 ECTS, Facultatea de Mecanică; códigos `L431.AA.SS.xN`.

## Fase 1
- Fuente: catálogo Erasmus de la Facultad (Excel "Course catalogue Faculty of Mechanical Engineering 2025-2026", hoja Bachelor, programa Mechanical Engineering) + fichas (Fișa disciplinei, Word) ya extraídas por el usuario. `prepare_fuente_previa.py` los une sin profesorado en `fuente_previa/upt_cursos.json` (año, semestre, ECTS, horas, idioma de docencia).
- Web: `international.upt.ro/en/incoming-students/course-catalogue/` accesible con PoliteClient, pero el enlace al Excel no aparece en el HTML estático (no se usó navegador). `url_guia_docente` = esa página. No se comprobó robots.txt de `international.upt.ro` más allá de que PoliteClient la sirve.
- 65 filas únicas (60 con ficha, 5 `sin_guia`: proyecto/examen de diploma, prácticas, etc.). Suman 249 ECTS (>240 porque incluye optativas alternativas y cohortes distintas L431.21–25). Catálogo `parcial` (fuente reutilizada; no verificada contra la web).
- Trampas: mismo código para asignaturas distintas (L431.23.06.D1) → sufijo con hash del nombre; filas duplicadas eliminadas; nombres en inglés/rumano mezclados.
- Idioma: fichas en rumano; ~33 asignaturas se imparten en inglés (campo `curso_semestre`).

## Fase 2
- `scraper_ec_ro_timisoa04.py` no usa red; Markdown desde `fuente_previa/`: Objectives, Lecture programme (con bibliografía), Practical programme, Evaluation. 60/60 escritos. Sin profesorado.
- Las secciones son resúmenes aplanados (tablas de la ficha convertidas a texto continuo; competencias y créditos de tiempo de estudio no incluidos). No hay "prerequisites".
