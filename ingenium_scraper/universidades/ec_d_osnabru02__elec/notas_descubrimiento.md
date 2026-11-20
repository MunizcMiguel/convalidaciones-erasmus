# ec_d_osnabru02__elec – Hochschule Osnabrück – Elektrotechnik B.Sc. (StO 2025)

- Fuente: https://www.hs-osnabrueck.de/fileadmin/Modulhandbuch/BET/StO2025_Stand2026-08-20_Elektrotechnik.pdf
- Misma plataforma/plantilla que `ec_d_osnabru02` (Modulhandbuch PDF único, fichas 11Bnnnn); URL localizada por búsqueda (patrón `Modulhandbuch/{COD}/StO{año}_Stand{fecha}_...`). Segunda titulación afín (familia elec).
- Reutiliza `discover`/`scraper` de `ec_d_osnabru02` parametrizados (URL y título); ver sus notas para estructura de ficha y trampas.
- Fase 1: 67 módulos (ECTS brutos; catálogo de módulos, sin plan por semestres).

## Fase 2
- `scraper_ec_d_osnabru02__elec.py --all`: 67 Markdown de 67 filas, 0 fallos; los 5 bloques presentes. Revisión puntual de una ficha (Analogelektronik/otros) fiel. Docentes eliminados.
- Defecto menor heredado: apartados vacíos con «-»; tablas de horas como líneas de texto.
