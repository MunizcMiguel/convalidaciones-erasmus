# ec_cz_praha10 — ČVUT Praga, Fac. de Ingeniería Mecánica (parcial, sin Fase 2)

- Titulación: Bachelor of Mechanical Engineering (programa 1242186598205 de Bílá kniha); grado en checo.
- Fuente: https://bilakniha.cvut.cz/en/ (HTML estático; sin robots.txt, 404). Hay 17 especializaciones (`specializaceB071XXX-1242186598205.html`) pero **todas con `<ul></ul>` vacío** en el HTML (periodo 2026/27); archive.json lista periodos hasta LS 2022/23 pero `/2023-ls/en/...` da 404.
- Existe `/en/f2-predmety.html` con 3574 cursos de la facultad (722 en inglés) y fichas `/en/predmet{id}.html` con Synopsis/Syllabus/Study materials, pero ninguna enlaza a un plan (sección "part of the following study plans" vacía), por lo que no se puede asociar de forma determinista al grado. No se hace selección manual.
- Estado: `parcial`, 0 filas, sin Fase 2. Pendiente de verificar: si el plan de estudios está en PDF en www.fs.cvut.cz (no explorado) o si Bílá kniha publica los planes más adelante.

## Segunda pasada (oferta English de FS)
- Planes de grado siguen vacíos en Bílá kniha → no se ata al grado. Catálogo = 722 cursos English de /en/f2-predmety.html filtrados a ficha con contenido: 502 filas (220 vacías omitidas). Sin curso/semestre ni nivel grado/máster (hay cursos de varios departamentos: control, energía, procesos…); requiere revisión manual antes de convalidar. `estado: parcial`.
- Fase 2: scraper_ec_cz_praha10.py (bloques `dl dt/dd`; sin profesorado), 502/502 Markdown. Sin bloque assessment (no existe en la fuente).
