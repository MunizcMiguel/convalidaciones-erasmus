# ec_cz_ostrava01 — VŠB-TU Ostrava, Fac. de Ingeniería Mecánica (parcial)

## Fase 1
- No hay plan de estudios público en inglés del grado (Mechanical Engineering es bachelor en checo). Fuente: "Course catalogue for Erasmus+ students" de la FS: `https://www.vsb.cz/en/study/exchange-students/erasmus-plus/courses/fs/` (JSF, HTML estático; 77 fichas). robots.txt de www.vsb.cz: 404 (permite).
- Se incluyen las 44 fichas cuyo "Level of Course Unit" contiene First Cycle (35 solo 1.er ciclo + 11 mixtas, menos duplicados de código); se excluyen 31 de Second Cycle. Es oferta de intercambio, no el plan: sin ECTS totales, sin curso/semestre fiables (Year of Study casi siempre vacío). Estado `parcial`.
- Códigos oficiales `NNN-NNNN/NN` (el sufijo es la versión).

## Fase 2
- Ficha: `?expandedSubjectId={id}&studyPlanId=-1&subjectBlockId={bloque}`; `div#ects` con tabla de `th.subjectAttrsTitle`; los títulos de sección (Summary, Course Contents...) tienen el valor en la fila siguiente. Se eliminan lecturer/Personal ID y código/créditos (ya en cabecera).
- 44/44 Markdown. Bibliografía y evaluación presentes pero con texto pobre ("Tasks are not Defined" en alguna). Idioma de la ficha: inglés (algunas asignaturas se imparten en checo).
