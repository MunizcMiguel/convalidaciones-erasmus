# Universidad de Oviedo — Máster Universitario en Ingeniería Industrial (uniovi_mii)

EPI Gijón, plan `MINGIND2` (título "(PARS)" en la web; el script quita el sufijo). Fases 1-2 hechas el 20-11-2026; Fase 3 pendiente por orden del usuario.

## Fuente (Fase 1)
- Ficha: `https://www.uniovi.es/estudia/masteres/ingenieriayarquitectura/industrial` (localizada desde `/estudia/masteres/ingenieriayarquitectura`). Misma plataforma SIES/Liferay que los grados (ver `../uniovi/notas_descubrimiento.md`): plan en HTML estático `#asignaturasAccordion`, página de asignatura `{ficha}/-/fof/asignatura/{COD}`, y guía por AJAX (asignaturaId → JSON `serveGuiasDocentes` → fragmento `/GuiaDocente`). robots.txt de www.uniovi.es solo veta `/login`, `/group/`, `/web/guest/`.
- `discover_uniovi_mii.py` es copia de `uniovi_giti` con dos cambios: URL, y soporte del código `MINGIND2-C-nnn`.
- 62 asignaturas: 8 obligatorias de 1.er sem. + 7 de 2.º (60 ECTS), 29 optativas (curso 2), Prácticas Externas (6), TFM (18) y **18 Complementos de Formación** (códigos `MINGIND2-C-001…018`, 6 ECTS c/u, 108 ECTS, caracter `complementos`, curso 1).
- ECTS: 60 obl. + 36 optativos exigidos + 6 prácticas + 18 TFM = 120. Se ofertan 144 ECTS optativos (de los que se cursan 36). Los complementos son asignaturas de nivelación para quien accede desde otras titulaciones; **no cuentan** en los 120 (el script los excluye de la comprobación de ECTS y lo anota en `meta.notas`).
- Itinerarios/especialidades: no hay tabla de itinerarios en la ficha (la columna "Itinerario Bilingüe" es "No" en las muestras). Las optativas se agrupan por módulos temáticos (Sistemas Mecánicos, Organización, Energía, Sistemas Robóticos…) según los textos de las guías; el catálogo incluye todas, sin etiquetar módulo.
- Dobles másteres (Ing. Industrial + Ing. Energética, + Diplôme d'Ingénieur / Laurea Magistrale): comparten estas mismas asignaturas; no hay catálogo aparte.

## Trampas
- Código con "C" en la posición del curso (complementos): el regex original `\d+` lo rechazaba.
- Cada complemento figura en el bloque de curso 1 (semestre 1 o 2 de la tabla), con `curso=1`.
- Las guías 2026-2027 de **Prácticas Externas (2-029) y TFM (2-030) están publicadas pero vacías en todos los cursos** (solo "Coordinación/Profesorado" sin contenido). Se escribe Markdown solo con la ficha (`Datos de la asignatura`) y los 5 `blocks_found` a False. Un TFM/prácticas sin guía real no sirve para equivalencias salvo por créditos.
- Idioma ES únicamente (no se compara EN).

## Fase 2 — scraper (`scraper_uniovi_mii.py`)
Copia de `scraper_uniovi_giti.py` con: otra `BASE`, muestra derivada del catálogo para máster (obl. 1.er y 2.º sem., optativa 2.º, prácticas, TFM) y selección de guía por candidatos: curso vigente primero y, si es un esqueleto vacío (<200 caracteres), los años anteriores; si todos están vacíos escribe solo la ficha (no es fallo). Sigue sin volcar Coordinación/Profesorado.

Resultado `--all`: 62/62 Markdown (160 peticiones, 0 reintentos, sin 403/429). Bloques ausentes: `prerequisites` en 1-015 (Tecnologías del Transporte); los 5 en 2-029 y 2-030. Validación: 3 guías de la muestra comparadas palabra a palabra con el HTML fuente (0 palabras perdidas); revisadas 2-001, 2-026, 2-030; sin nombres de docentes. No verificado: imágenes/fórmulas (se vuelcan como `[imagen]`).
