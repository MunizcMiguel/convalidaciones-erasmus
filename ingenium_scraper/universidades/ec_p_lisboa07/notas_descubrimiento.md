# ec_p_lisboa07 — ISCTE-IUL (Licenciatura em Engenharia de Telecomunicações e Informática, LETI)

## Fase 1
- Excel: Teleco (Grado TSTT 2 plazas, doble Teleco+Datos, máster); ISCTE no tiene Mecánica/Eléctrica pura → LETI (180 ECTS, 3 años).
- Fuente única: `https://www.iscte-iul.pt/programmes/degree/9098` (versión EN, robots permite; sin Fénix: `fenix.iscte-iul.pt` está vetado por robots, `fenix-mais.iscte-iul.pt` no se usa porque la página del grado ya trae todo).
- Plan: `#study_plan`, un `tab-pane-N` por curso con `tr.yearsemester-info` (nombre, semestre, ECTS) y `data-bs-target="#CourseInfoModal-N"`. Cada modal trae 4 pestañas (objectives/programme/evaluation/bibliography) y el nombre del profesorado (se descarta). Código = id de UC del enlace «See more» (`fenix-mais.../courses/{codigo}-{id}`).
- 28 filas (plan 2026/27; los 180 ECTS incluyen optativas de 3.º y competencias transversales que no tienen modal). Idioma: inglés.

## Fase 2
- `scraper_ec_p_lisboa07.py`: parsea los modales de la página (1 GET cacheado). 28/28 Markdown; prerequisites=false siempre (la web no los publica).
