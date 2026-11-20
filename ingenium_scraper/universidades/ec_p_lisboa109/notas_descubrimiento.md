# ec_p_lisboa109 — Universidade de Lisboa (IST, Licenciatura em Engenharia Mecânica LEMec21)

## Fase 1
- ULisboa es una federación de escuelas; la titulación equivalente a Ingeniería Mecánica es la del Instituto Superior Técnico (Licenciatura Bolonha, 3 años, 180 ECTS; el Mestrado MEMec21 queda fuera).
- Fuente: Fénix (fenix.tecnico.ulisboa.pt; no tiene robots.txt, 404). Estructura (año/semestre/créditos) del HTML `/cursos/lemec21/curriculo?year={id}` (bloques `h4 "Ano N, Semestre M"`, filas con enlace `disciplina-curricular/{id}`); guías por la API pública `/api/fenix/v1/degrees/847186594103310/courses?academicTerm=2025/2026` y `/api/fenix/v1/courses/{id}`. Emparejamiento por nombre normalizado.
- A.A. de referencia 2025/2026. 36 filas; suma de créditos de las filas 189 porque HASS I/HASS II (3 ECTS, optativas de Humanidades y Ciencias Sociales) aparecen en los semestres 1 y 2 (mismo id) y son 4 filas sin_guia (no tienen ejecución en la API).
- Códigos = acrónimo de Fénix (con sufijo si se repite). Idioma: portugués (la API no sirve versión inglesa).

## Fase 2
- `scraper_ec_p_lisboa109.py`: 1 GET a la API por curso. La API solo da `program`, `bibliographicReferences` (lista de dicts), `evaluationMethod` (HTML) y `teachers` (descartado). No hay objetivos de aprendizaje ni requisitos previos: faltan en las 32 fichas (learning_outcomes, prerequisites) y alguna carece de evaluación (p. ej. Mecânica dos Fluidos I, Relatividade). La página web de cada curso (/disciplinas/{acrónimo}/...) podría tener objetivos, no se ha usado.
- 32 Markdown comprobados contra el JSON (final de program/evaluationMethod presente).
