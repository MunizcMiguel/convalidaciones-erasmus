# Notas de descubrimiento — Università "G. d'Annunzio" Chieti-Pescara (`unich`)

## Grado elegido

UdA **no imparte Ingegneria Meccanica**. Sus grados de primer ciclo (laurea triennale) en ingeniería
en el catálogo 2025/26 son:

| cdsCod | Grado | Clase |
| --- | --- | --- |
| L460R | Ingegneria Biomedica | **L-9 Ingegneria industriale** |
| 801TR (2025) / 802T (2026) | Ingegneria delle Costruzioni / Ingegneria Edile e dell'Ambiente Costruito | L-23 (ingeniería civil/edificación) |

Se elige **Ingegneria Biomedica (L460R)**: es la única laurea de UdA en la clase L-9, la misma clase
ministerial que Ingegneria Meccanica, y su núcleo es de ingeniería industrial (Analisi I/II, Fisica I/II,
Scienza delle Costruzioni, Scienza e Tecnologia dei Materiali, Elettrotecnica, Biomeccanica
computazionale, "Tecnologie e sistemi di lavorazione e protesi"). Ingegneria delle Costruzioni (L-23)
es ingeniería civil. Grado de 180 ECTS, 3 años, sede Pescara, Dipartimento di Ingegneria e Geologia.

## Hosts y robots.txt

| Host | Uso | robots.txt / acceso |
| --- | --- | --- |
| `unich.coursecatalogue.cineca.it` | catálogo + API JSON (fuente única) | `/robots.txt` no existe: la SPA devuelve su `index.html` (200), que no contiene reglas -> todo permitido. Sin bloqueos, sin 403/429. |
| `www.unich.it` | portal institucional | 403 con desafío Cloudflare ("Just a moment…") incluso para `/robots.txt`. **No se usa.** |
| `unich.esse3.cineca.it` | Esse3 | 403 Cloudflare. **No se usa.** |

(La comprobación inicial de robots.txt de los tres hosts se hizo con una petición httpx directa a
`/robots.txt`; todo el contenido posterior se obtuvo solo con `PoliteClient`.)

## Fuente: API JSON del catálogo Cineca

El catálogo es una SPA Angular; en `main.*.js` aparecen los endpoints (`apiUrlV1 = "/api/v1"`):

1. `GET /api/v1/corsi?anno=2025&minimal=true` — grados por grupo; se localiza `cdsCod == "L460R"` -> `cod = 7340`.
2. `GET /api/v1/corso/2025/7340` — ficha del grado con `percorsi[] -> anni[] -> insegnamenti[] (grupos "Obbligatori"/"A scelta") -> attivita[]`.
   Cada actividad trae `adCod` (código Esse3, p. ej. `TO001A`), `cod` (id de actividad por currículo, p. ej. `30043_L460R-2525_48222_489879`), `crediti`, `annoCorso`, `aa` (año de impartición), `tafDes_it`, `tipo_ins_cod` (OBB/OPZ), `frazioni` (periodo).
3. `GET /api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=2025&af_percorso={af_percorso_id}&corso_cod=7340&corso_aa=2025` — la ficha ("scheda insegnamento").
   Página humana equivalente: `https://unich.coursecatalogue.cineca.it/corsi/2025/7340/insegnamenti/{aa}/{cod}/2025/{af_percorso_id}?coorte=2025`.

### Cohorte

Se cataloga la **cohorte 2025** (primera del grado; el endpoint `corso/2024/7340` da 404). Años 1 y 2
= A.A. 2025/26 y 2026/27, con syllabus publicado; el año 3 = A.A. 2027/28 aún no se ha impartido y
la API devuelve la ficha sin `testiTotali` -> `sin_guia`. La cohorte 2026 (nuevo ordinamento, mismo
plan casi idéntico) solo tendría syllabus del año 1. Como el grado es nuevo, todas las asignaturas que
realmente se imparten en 2026/27 (años 1-2) quedan cubiertas.

### Catálogo

- 34 filas = unión de los tres `percorsi`: `003 CORSO GENERICO` (parte común, `comune: true`),
  `A057 GENERAL BIOMEDICAL ENGINEERING` y `A058 MEDTECH`.
- Clave (`codigo_asignatura`) = `adCod`. Si un mismo `adCod` aparece como actividades distintas
  (distinto `cod` porque cambian créditos o tipología según currículo) se sufija con
  `af_percorso_cod`: `TO001B_A057/_A058`, `TO0037_A057` (12 ECTS) / `_A058` (9 ECTS),
  `TO0049_A057` (15) / `_A058` (18).
- ECTS: cada currículo suma exactamente 180 ECTS de "Obbligatori" (validado en el script). Ese total
  incluye `TO0025 A SCELTA DELLO STUDENTE` (12 ECTS), un hueco de libre elección que se cubre con
  optativas del grupo "A scelta" (TO0018, TO0032, TO0050-TO0055) -> por eso el catálogo suma 280 ECTS
  ofertados. TO0025 se marca `sin_guia` (no es una asignatura).
- `caracter`: derivado de `tafDes_it`/`tipo_ins_cod`/nombre (formacion_basica, obligatoria, optativa,
  libre_eleccion, practicas = TIROCINIO, tfg = PROVA FINALE).
- `semestre`: absoluto si todas las partes (fracciones/módulos) caen en el mismo semestre; `null` para
  anuales o corsi integrati repartidos en dos semestres (el detalle está en `curso_semestre` y en el
  Markdown).
- `url_guia_docente` = URL del endpoint JSON (tipo_fuente `api`).
- 17 filas `sin_guia`: todo el año 3 (incl. TIROCINIO, PROVA FINALE y optativas), el hueco TO0025 y
  `TO0040 ELETTROTECNICA BIOMEDICA` (año 2, 2.º semestre 2026/27, aún sin ficha).

### Estructura de una ficha

`testiTotali[]` contiene uno o varios "testi":
- ficha simple: una entrada con `chiave_cod: null`;
- **particiones** de alumnos (matricole pari/dispari; `chiave_domPartCod`): TO001A, TO002, TO0036 — textos casi idénticos;
- **corsi integrati (C.I.)**: entrada común (`chiave_cod: null`) + una por módulo (`chiave_udCod`, campos con prefijo `mod_`).

Campos por sección, cada uno en `_it` y `_en` (HTML de un editor WYSIWYG: `p`, `br`, `span`, `b`,
`ul/li`, `h3`; sin tablas): `contenuti`, `programmazione_estesa`, `obiettivi_formativi`,
`prerequisiti`, `metodi_didattici_est`, `verifica_apprendimento`, `testi`, `altro`,
`obiettivi_svil_sos_des` (+ `elenco_obiettivi_svil_sos`) y `altri_testi` ("Lingua insegnamento").
`ordineTesti` da el orden de las secciones en la web.

### Idioma

Las fichas son bilingües. `idioma_pagina = "en"` si todos los campos con texto italiano tienen versión
inglesa no vacía y que parece inglés (heurística de palabras funcionales; bibliografía y textos < 60
caracteres solo se exigen no vacíos); si no, `"it"`. Resultado: 13 `en`, 4 `it`
(TO001B ×2: en un módulo los campos `_it`/`_en` del programa están intercambiados; TO0034: verifica
EN reducida a "Written"; TO0036: prerequisitos EN sin traducir).

### Trampas

- `www.unich.it` y Esse3 detrás de Cloudflare: no usar.
- `/robots.txt` del catálogo devuelve la SPA (HTML), no un robots real.
- Los `cod` cambian de formato entre cohortes (`L460R-2525` en 2025, `L460R2026` en 2026); no construirlos, leerlos del plan.
- Los nombres en `des_en` llevan espacios iniciales (" BIOMEDICAL ENGINEERING").
- Las fichas JSON incluyen `docenti`/`responsabili` con nombres: no se vuelcan.
- Algunos textos pegados desde PDF traen saltos de línea duros y restos ("Codice Descrizione 4 Istruzione di qualità…" dentro del programa de TO001A): son del origen.

## Fase 2

`scraper_unich.py`: 1 GET por asignatura (el mismo endpoint de `url_guia_docente`, ya en caché tras el
descubrimiento) -> Markdown en el idioma de `idioma_pagina` (respaldo al italiano por campo si faltara
el inglés, anotado al final del fichero).

Estructura del Markdown: `#` nombre (código); `## Informazioni generali / General information`
(curso, currículo, año, A.A., periodo, CFU, horas, SSD, tipo, ámbito, tipo de examen, frecuencia) y
tabla de módulos si es C.I.; después las secciones en el orden de `ordineTesti`. En fichas con
módulos/particiones, un `##` por módulo/partición con sus secciones en `###`; las particiones con texto
idéntico se fusionan en un único bloque con ambos títulos. Los módulos listados sin texto publicado
llevan una nota explícita (TO0042 y TO0044: módulo TO0014 "Scienza e tecnologia dei biomateriali",
2.º semestre 2026/27).

`blocks_found`: contents = Contenuti o Programma esteso; learning_outcomes = Obiettivi formativi;
assessment = Modalità di verifica; bibliography = Testi di riferimento; prerequisites = Prerequisiti.

Privacidad: no se vuelcan `docenti`/`responsabili`/`titolari`; se eliminan líneas de horario de
recepción ("Office hours…", "Ricevimento…"); las menciones en texto libre de personas que la propia
ficha lista como personal se sustituyen por `[docente]` (TO005B, TO007 y una URL personal en TO0034);
`write_markdown` quita emails y teléfonos.

### Validación

- `--sample 5` (TO001A particiones/en, TO0034 C.I. con 3 módulos/it, TO0041 núcleo ingeniería/en,
  TO001B_A057 módulos con idiomas cruzados/it, TO0042 C.I. MedTech con módulo sin publicar): revisados
  a mano contra el JSON; además un comprobador automático verifica que **todas las palabras de cada
  campo fuente aparecen en orden en el Markdown** (17/17 OK; las únicas diferencias son las
  redacciones de privacidad intencionadas y una línea de horario de recepción en TO0042).
- `--all`: 17 Markdown escritos de 34 filas (17 `sin_guia` omitidas), 0 fallos, exit 0; re-ejecutar
  solo usa la caché.
- Spot-check extra: TO005A (el más corto), TO0044 (el más largo, C.I. con módulo sin publicar),
  TO0036 (it por prerequisitos sin traducir): correctos.
- Ningún bloque falta en las 17 fichas (los 5 bloques presentes en todas).
- Pendiente: cuando se publiquen las fichas del año 3 (2027/28), TO0040 y el módulo TO0014, borrar sus
  entradas de `raw_cache` y re-ejecutar ambos scripts.
