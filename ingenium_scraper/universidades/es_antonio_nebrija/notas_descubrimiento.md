# Notas — Universidad Antonio de Nebrija (Grado en Ingeniería Mecánica) — PARCIAL
- Fuente: https://www.nebrija.com/carreras-universitarias/grado-ingenieria-mecanica/ (robots permite). Solo el 1.º curso (2 semestres, 10 asignaturas, 60 ECTS) está en el HTML estático; 2.º-4.º se pintan por JS y `/page-data/…` está vetado por robots.txt (no se usa navegador ni se rodea). No validable contra RUCT (72/144/0/12/12).
- Sin código oficial: clave = slug del nombre. Solo 4 de las 10 tienen enlace PDF en la ficha (`/pdf/carreras-universitarias/grado-ingenieria-mecanica/pdf-asignaturas/{slug}.pdf`); el resto `sin_guia`.
- PDF bilingüe ES/EN, pág. 1 portada, secciones 1-4 (resultados, contenidos, evaluación, bibliografía). Incluye «Profesor - Equipo docente» → eliminado.
## Fase 2
- `scraper_es_antonio_nebrija.py`: 4/4 Markdown. Revisado Física mecánica (secciones completas, sin nombres de profesorado). Pendiente: cursos 2-4 (requeriría el listado completo, p. ej. otro origen).
