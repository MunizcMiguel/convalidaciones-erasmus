# École Centrale de Nantes — ingénieur spécialité Mécanique (apprentissage), EI1-EI3

- Solo cycle ingénieur (3 años). Fuente: 3 PDF "Programme ingénieur, spécialité Mécanique 2025-2026" en `https://www.ec-nantes.fr/ingenieur-de-specialite/mecanique/syllabus-ei{1,2,3}-spe-meca` (devuelven PDF con texto; robots.txt permite). El enlace sale de las páginas de formación (el HTML `/ingenieur-de-specialite/mecanique` da 404); el patrón EI1/EI2 se dedujo del EI3 hallado por búsqueda.
- Ficha por curso: páginas que empiezan por `INGÉNIEUR, SPÉCIALITÉ MÉCANIQUE / {n}e année - UEnnn / Título [ACRÓNIMO]`; sections Objectifs, Plan de l'enseignement, Contrôle des connaissances, Évaluation, tabla final de horas (ECTS por curso suele ser "-"; los ECTS están por UE en el cuadro inicial). Código = acrónimo (MECA3_MEF).
- 48 cursos. Trampas: varios cursos por UE (ECTS de UE en `curso_semestre`; se copia a `creditos_ects` solo si la UE tiene un único curso); sin semestre; se eliminan "Responsable(s) du cours"; LowTech sin objetivos en la fuente.

## Fase 2
`scraper_ec_f_nantes07.py` (pdfplumber): 48/48 Markdown. Bloques: contents 45, learning_outcomes 47, assessment 48, prerequisites 8, bibliography 0.
