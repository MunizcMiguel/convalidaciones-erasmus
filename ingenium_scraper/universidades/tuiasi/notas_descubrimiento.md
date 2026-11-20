# TUIASI – Inginerie Mecanică (licență) – notas de descubrimiento (Fase 1)

## Grado elegido
- **Inginerie Mecanică (IM)**, programa de licenciatura de la Facultatea de Mecanică (mec.tuiasi.ro), 4 años / 240 ECTS, en rumano, "cursuri cu frecvență". Es exactamente el grado objetivo (la facultad tiene además CA, AR, ISPA, SET, MIAIA, MCT, RBT, que no se toman).

## Hosts y robots.txt
- `https://mec.tuiasi.ro/robots.txt`: solo `Disallow: /wp-admin/` -> permitido. Sirve las páginas, la API JSON de WordPress (`/wp-json/...`) y todos los PDF (`/wp-content/uploads/...`).
- `https://www.tuiasi.ro/robots.txt`: solo `/wp-admin/` y un JSON de plugin -> permitido (no se usa para el catálogo).
- No hubo 403/429. Todo pasa por `PoliteClient` (caché en `raw_cache/`).

## Fuentes
1. **Plan de estudios 2025-2026 (años I-IV)**: `Anexa-B.1.1.1.b-Plan-invatamant-IM-2025-2026-ANI-I-IV_PSUL.pdf` (dossier de reacreditación ARACIS del programa, "PSUL"), localizado de forma determinista con la API JSON de WordPress `GET /wp-json/wp/v2/media?search=Plan-invatamant-IM-2025-2026`. Es byte a byte idéntico a `04_PI_IM_Licenta_2025-2026.pdf` publicado en 2025/09. Tablas con capa de texto limpia -> `pdfplumber.extract_tables()` (21 columnas: categoría DI/DO/DL, nº, nombre, código, categoría formativa, y por semestre C S L P Pr SI Ev K).
2. **Fichas ("fișa disciplinei")**: 4 PDF compartidos, uno por año, enlazados desde `https://mec.tuiasi.ro/fise-discipline-psul/`: `FD_an{1..4}_IM_PSUL.pdf` (101, 87, 109 y 137 págs.; 28-33 MB cada uno). `tipo_fuente = "pdf_compartido"`, `paginas_pdf` derivado por el script.

### Por qué 2025-2026 y no 2026-2027
- La página "Fișe discipline 2026/2027" (`/fise-discipline-2026-2027/`) lista los PDF de todos los programas pero **solo enlaza los de SET**; los de IM aparecen como texto sin enlace (y la API de medios no tiene ningún `FD_IM_*2026-2027*`).
- El plan 2026-2027 de 1er año cambia los códigos (`IM.AM.101`…) y no hay fichas para ellos. El conjunto plan 2025-26 + fichas PSUL es coherente (mismos códigos, mismo orden) -> `curso_academico = "2025-26"`.
- Las fichas sueltas por asignatura que hay en otras páginas (`/fise-discipline-mct-anul-1/`, ISPA, AR…) son de otros programas (aunque compartan códigos `MTC.*` de tronco común); no se usan.

## Cómo se construye el catálogo (`discover_tuiasi.py`)
- Filas del plan: una por asignatura; los grupos de optativas (DO) tienen la fila del grupo con nº y las alternativas sin nº: heredan nº, semestre, horas y créditos del grupo (en el año I los créditos del grupo 15 están en la 2ª fila, no en la 1ª).
- Año = primer dígito del número de 3 cifras del código (la cabecera de la pág. 4 del plan dice "ANUL II" para el 3er año: errata, no se usa).
- Fichas: empieza ficha en cada página cuya franja superior contiene `2.1.2 Codul disciplinei <código>`; fin = página anterior a la siguiente ficha.
- **Emparejamiento por orden**, año a año: el propio anexo dice que las fichas van "în ordinea din planul de învățământ", y los códigos escritos en las fichas tienen erratas (`IM.413.DO.DS-1` repetido para la 3ª optativa, `IM.414…` para las de 415, `IM.416.DO.DS-21`, `MTC.418` para Inginerie economică (419), `IM.315` por `MTC.315`, `MCT.117` por `MTC.117`…). El script exige igual nº de fichas que de filas (o anclaje del último par si faltan al final) y aborta si discrepan más de 1/4 de los códigos; las discrepancias se listan en `meta.notas`. Se comprobó a mano con OCR del título de las fichas dudosas del año IV.
- Código del catálogo = **código del plan** (normalizado: espacios/puntos sobrantes, p. ej. `MTC. 406.DI.DD` -> `MTC.406.DI.DD`). Única colisión: `DF.DI.L.1.01` lo usan dos asignaturas del módulo pedagógico (Psihologia educației y Pedagogie 1) -> se añade `_nr<nº crt.>` (`DF.DI.L.1.01_nr18`, `DF.DI.L.1.01_nr20`).
- ECTS = K del semestre; si la asignatura tiene créditos en ambos semestres (MTC.319, MTC.421, ambas facultativas) se suman y `curso_semestre` indica `Semestrul 1+2`.
- `caracter`: DI -> obligatoria (o `practicas` / `tfg` por nombre), DO -> `optativa (grupo A.N, elegir 1 de k)`, DL -> facultativa.
- **Sin ficha**: `MTC.422.DL.DC` Prezentare publică (facultativa, año IV): el PDF del año IV termina en MTC.421 -> `sin_guia`. (El índice de la pág. 1 de ese PDF lista además las facultativas del año III: errata del anexo.)

## Verificación de ECTS
- DI (incl. prácticas y "Elaborarea proiectului de diplomă") + 1 optativa por grupo DO = **240** = total del plan (el script lo exige).
- Las DL (facultativas: módulo pedagógico, idiomas extra, etc.) suman créditos adicionales fuera de los 240. El examen de diploma (10 ECTS) se añade a los 240 y no tiene ficha.

## Estructura de una ficha (plantilla PO.DID.04 L-F2)
1 Date despre program · 2 Date despre disciplină (2.1 nombre RO/EN, 2.1.2 código, 2.2/2.3 titulares, 2.4-2.7 año/semestre/evaluación/tipo) · 3 Timpul total estimat (horas) · 4 Precondiții · 5 Condiții · 6 Obiectiv general · 7 Rezultatele învățării (tabla con etiquetas giradas 90°: Cunoștințe / Aptitudini / Responsabilitate și autonomie) · 8 Metode de predare · 9 Conținuturi (9.1 Curs, 9.2a Seminar, 9.2b Laborator, 9.2c Proiect, con bibliografías dentro de la tabla) · 10 Evaluare (tabla con criterios, métodos y ponderaciones %, 10.6 condiciones) · bloque de firmas (fechas y nombres).

## Trampas
- **Capa de texto rota**: en los PDF de fichas, los tramos de texto con diacríticos rumanos están dibujados como **contornos vectoriales** (miles de `curve` por página, sin caracteres): `extract_text()` pierde aproximadamente la mitad de las palabras (p. ej. "FI A DISCIPLINEI", nombres de asignatura ausentes). El plan de estudios no tiene este problema. Ver Fase 2 para la solución (OCR local).
- Páginas de "Fișe discipline" por programa: unas enlazan PDF por año, otras fichas sueltas; las del 2026-27 de IM no están enlazadas.
- Códigos con espacios, puntos finales y prefijos inconsistentes (MTC/MCT/IM) entre plan y fichas.

# Fase 2 – Scraper (`scraper_tuiasi.py`)

## Problema: capa de texto incompleta
En los 4 PDF de fichas los tramos con diacríticos están dibujados como contornos (curvas), sin caracteres. `pdfplumber`/`pypdf` solo recuperan aproximadamente la mitad de las palabras. No hay motor OCR instalado (ni tesseract ni paquetes Python); sí está el **OCR integrado de Windows** (`Windows.Media.Ocr`, idiomas en-US y es-ES; no hay rumano). Se usa sin descargar nada, desde `ocr_windows.ps1` (PowerShell + WinRT). **El scraper solo funciona en Windows.**

## Estrategia (determinista y local; la única red es la descarga cacheada de los PDF vía PoliteClient)
1. Render de cada página con pypdfium2 (vía pdfplumber) **borrando antes las líneas finas de las tablas** (rects < 2 pt): si no, el OCR pierde las letras con descendente (p, g) que tocan el borde de la celda.
2. Tres pasadas de OCR cacheadas en `raw_cache/ocr/` (`<hash>_pNNN[_d200|_rot].json`): 300 ppp (principal), 200 ppp (solo rellena huecos: a 300 ppp el motor omite a menudo la palabra corta "și", que a 200 ppp sí ve) y 300 ppp girada 90° para las páginas con texto vertical (etiquetas Cunoștințe / Aptitudini / Responsabilitate…). Las imágenes temporales se borran.
3. Fusión palabra a palabra con la capa de texto del PDF: si los caracteres reales cubren ≥85 % del ancho de la palabra OCR, se usa el texto real (exacto: códigos, cifras, ISBN, nombres sin diacríticos); si no, la lectura OCR con reparaciones deterministas (`ä→ă`, `å→â`, `$i`/`ii`/`'i`/`5i`… aislados → `și`, `$`/`}`/`»`/`+` dentro de palabra → `ș`, `!`/`(` entre letras → `ț`).
4. Estructura desde los vectores: `find_tables` de pdfplumber sobre la página **sin curvas ni caracteres** (solo rectángulos/líneas) da las celdas; cada palabra se asigna a su celda por su centro. Tablas → tablas Markdown (celdas combinadas = celda vacía, saltos de línea `<br>`); una tabla que continúa en la página siguiente con el mismo nº de columnas se une. Texto libre → párrafos; viñetas `-`/`•` → listas; títulos `N. Date despre…/Obiectiv…/Conținuturi/Evaluare…` → `##`.
5. Se descarta: pie `Formular PO.DID.04 L-F2 E3R0`, superíndices (altura de línea < 7 pt), filas 2.2/2.3 (titulares), y **todo lo que sigue** a `Data completării` / `Titular…` / `Data avizării` / `Decan` / separador `____` de notas al pie (bloque de firmas con nombres de personal y notas de la plantilla). Los autores de la bibliografía se conservan.
6. `blocks_found`: contents = "Conținuturi"; learning_outcomes = "Rezultatele învățării"/"Competențe…"/"Cunoștințe"; assessment = "Evaluare" + algún "%"; bibliography = "Bibliografie"; prerequisites = "Precondiții" (la sección existe aunque diga "Nu este cazul" o esté vacía).

## Validación de la muestra (5 fichas, comparadas con la página renderizada)
`MTC.101.DI.DF` (Analiză matematică, año I), `MTC.202.DI.DD` (Rezistența materialelor 1, año II), `IM.313.DO.DS-2` (optativa año III), `IM.311.DI.DS` (Practica de specialitate), `MCT.409.DI.DS` (Elaborarea proiectului de diplomă). Secciones 1-10 completas y en orden, tablas de evaluación con sus porcentajes (incl. subcolumna de pesos internos), tablas partidas entre páginas unidas, bibliografía completa, sin pies ni firmas.
Errores corregidos durante la validación: un filtro de notas al pie por regex borraba una línea de bibliografía ("001-2004 Project Management Institute…") → sustituido por el corte en el separador `____`; títulos de sección como `#`; restos de puntuación ", ," de la capa de texto; orden de las reparaciones de `ț`.

## Limitaciones conocidas (calidad del texto, no de estructura)
- Las palabras que solo existen como contornos salen del OCR en-US: diacríticos a veces perdidos o aproximados (`t` por `ț`, `s` por `ș`, `i` por `î`), y ocasionalmente letras mal leídas (`cunoytințelor`, `IO` por `10`). Ninguna sección se pierde; la traducción posterior las tolera, pero no es texto literal.
- La palabra "și" aún falta en algunos puntos (sobre todo en las etiquetas giradas: "Responsabilitate autonomie").
- Las viñetas gráficas de algunas listas no se reconocen (los ítems quedan como líneas `<br>` dentro de la celda).
- Llamadas a nota al pie pegadas a etiquetas de la plantilla ("1.5 Ciclul de studii1", "4<br>2.6 Tipul de evaluare").

## Ejecución completa (`--all`)
- **94 Markdown escritos de 95 filas** (la 95ª, `MTC.422.DL.DC` Prezentare publică, es `sin_guia`). 0 fallos, 0 peticiones de red (todo en caché), log en `logs/scraper_all.txt`.
- Tras la primera pasada, 5 fichas marcaban un bloque ausente; revisadas contra el PDF: en `IM.310.DI.DS`, `IM.312.DO.DS-1/-2` e `IM.414.DO.DS-3` la ficha **no tiene el título "9. Conținuturi"** (empieza directamente por la tabla "9.1 Curs"), y `IM.416.DO.DS-1` da los pesos de evaluación sin el signo % ("0", "100"). Se ajustó la detección (`9.1 Curs` cuenta como contenidos; columna "Pondere" cuenta como evaluación) y se regeneraron esas 5. Resultado: los 5 bloques presentes en las 94 fichas.
- Revisión adicional de las más atípicas: la más pequeña (`MTC.321.DL.DC`, examen del módulo pedagógico: tabla de contenidos realmente vacía en el original), `MCT.408.DI.DS` (práctica para el proyecto) y la más grande (`IM.414.DO.DS-3`, 27 KB: una sola ficha larga, sin invadir la siguiente). Sin problemas de estructura; solo los defectos de OCR descritos (p. ej. "%" leído como "00", etiqueta girada "Cunoștințe" ausente en alguna ficha).
- Re-ejecutar `discover_tuiasi.py` o el scraper no hace ninguna petición de red (caché de PDF + caché de OCR).
