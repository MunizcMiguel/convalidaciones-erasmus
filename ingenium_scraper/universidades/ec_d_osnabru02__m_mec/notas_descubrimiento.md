# ec_d_osnabru02__m_mec – Hochschule Osnabrück – Maschinenbau M.Sc. (StO 2025)

- Fuente: https://www.hs-osnabrueck.de/fileadmin/Modulhandbuch/MMB/StO2025_Stand2026-03-02_MSc_Maschinenbau.pdf
- Misma plantilla que `ec_d_osnabru02` (carpeta MMB, fichas 11Mnnnn). Máster de ingeniería mecánica (familia M-mec).
- Reutiliza `discover`/`scraper` de `ec_d_osnabru02` parametrizados (URL y título); ver sus notas para estructura de ficha y trampas.
- Fase 1: 41 módulos (ECTS brutos; catálogo de módulos, sin plan por semestres).

## Fase 2
- `scraper_ec_d_osnabru02__m_mec.py --all`: 41 Markdown de 41 filas, 0 fallos; los 5 bloques presentes. Revisión puntual de una ficha (Analogelektronik/otros) fiel. Docentes eliminados.
- Defecto menor heredado: apartados vacíos con «-»; tablas de horas como líneas de texto.
