# ENIT (Tarbes) — Titre d'ingénieur, semestres 5-10

- ENIT: solo Titre d'ingénieur (+ Bachelor SIEE no mecánico). Fuente: página `/fr/formations/diplome-d-ingenieur/je-me-forme/programme-formation-ingenieurs.html` (robots.txt solo veta `remise-des-diplomes`) con PDF por semestre `/_attachment/nouvel-article-75/IGENI-{L3-S05,L3-S06,M-S07..M-S10}.pdf?download=true` ("Syllabus Titre d'Ingénieur", con texto). También hay C1-S01..S04 (prépa), ALM-* (apprentissage): no incluidos → `parcial`.
- Cada UE tiene página(s) de presentación y cada EC la suya (`Code EC IGENI-ECxxxx`). Catálogo = EC + UE sin EC; 181 filas. ECTS solo a nivel de UE (copiado cuando la UE tiene un único EC).
- Trampas: `extract_text(x_tolerance=1.0)` necesario (sin él se pierden los espacios); etiquetas rotadas salen invertidas ("sunetnoC" = Contenus) → se convierten en encabezados o se descartan; nombres de profesores (distintos layouts) → se conserva solo código/nombre/horas en la cabecera; ficha bilingüe FR/EN; códigos repetidos entre filières (se añade sufijo con el semestre).

## Fase 2
`scraper_ec_f_tarbes03.py`: 181/181 Markdown. Bloques casi siempre presentes (plantilla uniforme); sin ausencias relevantes salvo `Contenus` en 2.
