# ec_d_karlsru05 – Hochschule Karlsruhe (HKA) – Maschinenbau B.Eng. (MABB)

Es la MISMA universidad y titulación que el slug `hka` (INGENIUM), ya resuelto y validado a mano en su momento.
Aquí se reutilizan sin cambios la lógica de `universidades/hka/discover_hka.py` y `scraper_hka.py` (solo cambia SLUG)
y la caché de red de `hka` (mismas 3 URLs: página del grado, Modulhandbuch MABB 2026 y SPO V8). Detalles de fuente,
estructura de la ficha y trampas: ver `universidades/hka/notas_descubrimiento.md`.

## Fase 2
- `scraper_ec_d_karlsru05.py --all`: 36 Markdown de 38 filas (MABB450/650 son `sin_guia`: contenedores de Schwerpunkt). 0 fallos.
- Salida idéntica a la de `hka` (código idéntico, mismo PDF). No se repitió la revisión manual de muestra; se confía en la de `hka`.
- Solo alemán. Sin bloques: MABB710 (contenedor, sin contenidos/resultados), MABB720 sin resultados de aprendizaje.
