# ec_p_coimbra01 — Universidade de Coimbra (LEEC, FCTUC)

- Titulación: Licenciatura em Engenharia Eletrotécnica e de Computadores (180 ECTS), la más afín a EIA/Eléctrica (objetivo no es Mecánica).
- Fuente: https://apps.uc.pt/courses/PT/programme/8922/2025-2026?id_branch=21062 (tabla HTML `sp-table`, sin JS). El buscador /courses?... no devuelve enlaces en HTML estático; se parte del id de programa.
- Ficha: `/courses/EN/unit/{id}/21062/2025-2026?...` (EN disponible; docencia en portugués). Código oficial UC en un comentario HTML `<!--<td>01019327</td>-->` de la fila.
- robots: apps.uc.pt sin robots.txt (404); www.uc.pt solo veta portal. Sin bloqueos.
- Estructura de ficha: `h2` por sección (Prerequisites, Teaching Methods, Learning Outcomes, Work Placement, Syllabus, Head Lecturer, Assessment Methods, Bibliography) con `<p>` hermanos. Se omite Head Lecturer. Los `<p>` separados por `\r` se convierten en párrafos.
- Plan: 36 UCs; 156 ECTS obligatorios + 9 optativas de 6 ECTS (3.º sem. 6) a elegir.

## Fase 2
36/36 Markdown, ids del catálogo. Todos los bloques presentes en la muestra.
