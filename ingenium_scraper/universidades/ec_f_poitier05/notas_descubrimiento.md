# Notas de descubrimiento - ec_f_poitier05

- Universidad: ISAE-ENSMA (École nationale supérieure de mécanique et d'aérotechnique), Poitiers
- Titulación: Diplôme d'ingénieur ISAE-ENSMA (FISE) - 2e année (syllabus A2) (nivel master, estado `parcial`)
- Fuente: Syllabus FISE A2 (PDF compartido bilingüe FR/EN): una ficha por ECUE ('Code ECUE'); NFC necesario (el PDF usa diacríticos descompuestos); los códigos se repiten entre majeures (se desambiguan con -UE).
- URL principal: https://ensma.fr/wp-content/uploads/2025/02/Syllabus-FISE-ENSMA-A2-2025-2026-previsionnel.pdf
- Filas de catálogo: 53; Markdown generados: 53

## Justificación y trampas

ENSMA solo ofrece el diploma de ingeniero (ciclo de 5 años, sin grado de Mecánica separado); los destinos del Excel son de Máster Universitario en Ingeniería Industrial / Integridad y Durabilidad de Materiales (1+1 plazas), por lo que se toma el diploma FISE; es el único equivalente (2.º ciclo universitario según las fichas: 'Second cycle universitaire'). PARCIAL: solo se ha localizado el syllabus público de 2.ª año (A2, previsional 2025/26, 53 fichas); A1 y A3 (con especialidades) no tienen PDF localizado (el catálogo de cursos más antiguo es de 2016). Los ECTS se dan por UE (cabecera de la ficha), no por asignatura. Fichas bilingües FR/EN; se conserva el texto francés e inglés. Se omiten coordinadores/profesorado.

## Fase 2

`scraper_ec_f_poitier05.py` (`--sample N`, `--all`, `--codes`): 53 Markdown de 53 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
