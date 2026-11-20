# Notas de descubrimiento - ec_d_marburg01

- Universidad: Philipps-Universität Marburg
- Titulación: B.Sc. Informatik (nivel bachelor, estado `ok`)
- Fuente: HTML estático del Online-Modulhandbuch (índice por Studienbereich + página por módulo, sección.content).
- URL principal: https://www.mathematik.uni-marburg.de/modulhandbuch/20262/BSc_Informatik/index.html
- Filas de catálogo: 108; Markdown generados: 108

## Justificación y trampas

Excel: Grado Ing. Informática en TI (1.ª fila con ISCED 0610), Grado Ciencia e Ingeniería de Datos (2 plazas) y Doble Grado Informática+Datos. Solo hay Informática/Datos; se elige B.Sc. Informatik (180 LP, 6 semestres; Studienbereiche: Informatik Basis 45 LP, Weiterführende 36, Praxis 21, Mathematik 24, Wahlpflicht 24, Bachelorarbeit 12). Alternativa para la fila de Datos: B.Sc. Data Science (mismo Online-Modulhandbuch, /BSc_Data_Science/; muchos módulos comparten ficha). Obligatorios (Basis/Weiterführend/Praxis/Mathematik/BA) por área: {'Informatik Basismodule': 45.0, 'Informatik Weiterführende Module': 36.0, 'Praxismodule': 21.0, 'Mathematik Basis- und Weiterführende Module': 24.0, 'Bachelorarbeit': 12.0}. Sin semestre por módulo (el Modulhandbuch no lo da). Se omite Modulverantwortliche(r). robots.txt de www.mathematik.uni-marburg.de: 404 (sin restricciones).

## Fase 2

`scraper_ec_d_marburg01.py` (`--sample N`, `--all`, `--codes`): 108 Markdown de 108 filas, validados en una muestra y revisados bloque a bloque (bloques ausentes en la fuente quedan en false en `blocks_found`).
