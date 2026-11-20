# Notas de descubrimiento - ec_f_le_havr11

- Universidad: Le Havre Normandie Université
- Titulación: Licence Sciences pour l'Ingénieur - parcours Mécanique (L3) (nivel bachelor, estado `parcial`)
- Fuente: Syllabus L3 Mécanique (PDF compartido, UFR ST): pypdf; UE = línea de título + línea 'OBJECTIFS D'APPRENTISSAGE'. Texto con espacios partidos ('Pré-req uis') que limita la detección de prerrequisitos/bibliografía. Los coeficientes de evaluación quedan como fila numérica cruda.
- URL principal: https://www.univ-lehavre.fr/wp-content/uploads/2023/07/UFR-ST-L3-Mecanique-Syllabus.pdf
- Filas de catálogo: 18; Markdown generados: 18

## Justificación y trampas

Titulación elegida: Licence Sciences pour l'Ingénieur parcours Mécanique (180 ECTS, 3 años), la más afín a Grado en Ingeniería de Tecnologías Industriales (4 plazas en el Excel). PARCIAL: el único syllabus público con descriptivos por UE es el de L3 (S5-S6); L1-L2 solo tienen un esquema de maquette (nombres de UE sin descriptivo) y no se incluyen. Las UE de L3 suman menos de 60 ECTS porque parte son UE de personalización/preprofesionalización sin descriptivo. Cada descriptivo es breve: objetivos de aprendizaje, prerrequisitos, bibliografía y reparto de evaluación (coeficientes CC/parcial/examen) en una fila de números. Idioma: francés (UE de inglés incluidas). robots.txt de univ-lehavre.fr permite el acceso.

## Fase 2

`scraper_ec_f_le_havr11.py` (`--sample N`, `--all`, `--codes`): 18 Markdown de 18 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
