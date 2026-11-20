# Université de Rouen Normandie: Licence Mécanique, parcours Mécanique-Énergétique. Notas de descubrimiento

## Elección del grado
Rouen no tiene un grado que se llame literalmente "Mechanical Engineering". Se revisaron los candidatos en el catálogo oficial ODF (`formation.univ-rouen.fr`, sitemap con 37 441 URL):

- **BUT Génie Mécanique et Productique (IUT)**: **no existe en la Université de Rouen Normandie.** El catálogo solo tiene, entre los BUT técnicos, Chimie, GCGP, GEII, Mesures Physiques (Rouen y Évreux), MTEE, Packaging, R&T, etc. El BUT GMP de la región lo imparte el IUT du Havre, que pertenece a otra universidad. Además el host `iut.univ-rouen.fr` no resuelve.
- **ESITech, "Premier cycle des études d'ingénieur"**: es un ciclo preparatorio orientado a **salud** (biología, anatomía, farmacia), que alimenta las especialidades ESITech Génie biologique y Génie physique/physique pour la santé. No tiene contenido mecánico.
- **Licence Mécanique (L5MEP09P)**, con dos parcours: *Mécanique-Énergétique* (LBVZSTJE) y *Maîtrise de l'énergie, génie thermique* (L5MEP0CX, un L3 orientado a térmica y edificación). Su referente SISE es "Mécanique, génie mécanique".

**Elegido: Licence Mécanique, parcours Mécanique-Énergétique (180 ECTS, 3 años).** Es el título de primer ciclo más parecido a un grado de ingeniería mecánica: en L3 incluye MMC, mecánica de sólidos deformables, mecánica de fluidos, vibraciones, termodinámica y máquinas térmicas, CAO, cálculo científico y prácticas en empresa. Además, el catálogo ODF publica una ficha por asignatura. Limitación: es una licence generalista de ciencias, no una titulación de ingeniería. L1 y L2 son el *Portail Physique-Mécanique-Physique,Chimie* (PMPC), común con las licences de Física y Física-Química.

## Hosts y robots.txt
| Host | robots.txt | Uso |
| --- | --- | --- |
| `formation.univ-rouen.fr` (catálogo ODF Ametys, HTML y PDF) | `User-agent: *` sin `Disallow` (solo Sitemap) → permitido | Única fuente: plan, fichas y PDF de programa |
| `www.univ-rouen.fr` | `Disallow:` vacío → permitido | No se usa |
| `esitech.univ-rouen.fr` | vacío → permitido | No se usa |
| `iut.univ-rouen.fr` | DNS no resuelve | No aplica |

No hubo ningún 403 ni 429 (unas 120 peticiones en total).

## Fuente del catálogo (Fase 1)
- Página del parcours: `https://formation.univ-rouen.fr/fr/catalogue-de-l-offre-de-formation/licence-lmd-XA/licence-mecanique-L5MEP09P/licence-mecanique-mecanique-energetique-LBVZSTJE.html`. El plan completo está en HTML estático. No hay una API JSON pública. El sitemap y el PDF Ametys de la ficha no aportan más estructura que el HTML.
- Estructura: un `div.tab-pane[id^=tab-content-]` por año, con `<h3>` como título del año. Dentro hay un `div.tab-pane[id^=semester-]` por semestre, cuya etiqueta "Semestre n" (número absoluto, 1–6) está en el enlace `#semester-…`. Cada semestre contiene un acordeón `li.ametys-accordion__item`: la UE muestra el título, un enlace y "6 crédits" en `.ametys-accordion__item-text`, y los éléments (EC) van anidados en `div.collapse > … > ul`.
- **Granularidad**: una fila por **UE**, porque es la unidad que lleva ECTS (los éléments casi nunca los llevan). En las UE de elección hay un hijo "1 choix…" que contiene un `li.ametys-accordion__item--container` con el texto "Au choix : n parmi m" y las opciones en un `<ul>` hijo directo, sin `collapse`. En ese caso se crea una fila por opción (6 ECTS cada una), con `caracter=optativa`, salvo "1 parmi 1", que se marca `obligatoria`.
- **Código**: es el identificador ODF/ROF que Ametys añade al final del slug de la URL (`…-L5MCAVC2.html` → `L5MCAVC2`; algunas opciones de otras facultades usan `ELPnnn`). No es un código inventado, pero tampoco es el código Apogée de la UE.
- **curso_academico**: el catálogo no indica el curso académico. Se deriva de la fecha de descarga de la página del plan guardada en caché, con la regla septiembre–agosto (→ 2026-2027).
- Resultado: **42 filas = 28 UE obligatorias (168 ECTS) + 14 opciones de 2 UE au choix** (L1 S1 UE5 "Personnalisée", 1 entre 11 opciones de varias facultades; L2 S4 UE5 "Spécialisation", 1 entre 3: Électronique, RdM & transferts thermiques, Chimie). Un estudiante cursa 168 + 6 + 6 = **180 = total del parcours**. El script comprueba que cada semestre suma 30 ECTS. Las 42 filas tienen URL y no hay códigos duplicados.
- Idioma: `fr` en todas las filas. No existe versión inglesa: el sitemap no contiene `/en/`.

## Estructura de una ficha (HTML Ametys)
- Dentro de `.ametys-main-content`:
  - Cabecera con metadatos `.ametys-benefits-alt__item`: Niveau d'étude, ECTS, Composante, Période.
  - Cuerpo `.ametys-courses-single-two-columns-content__body`, formado por `<section>`, cada una con `h2.ametys-section-sub-title` y `.ametys-limited-content__body` (richtext).
  - Barra lateral `…__sidebar` con "Lieu(x)", "Campus" y "En bref" (una tabla th/td).
- Secciones y bloque al que corresponden: Description → contents; Objectifs y Compétences visées → learning_outcomes; Contrôle des connaissances → assessment; Pré-requis obligatoires → prerequisites. "Heures d'enseignement" es la lista `ul.ametys-coursepart` (CM/TD/TP con horas). "Bibliographie" no aparece en ninguna ficha del parcours.
- Las páginas de UE solo tienen metadatos y horas, más la sección "Liste des enseignements" con los enlaces a los éléments. El contenido real está en las páginas de los éléments.

## Trampas
- **Las fichas de L2 y L3 están vacías**: solo traen las horas, sin descripción, objetivos ni evaluación. Las de L1 (PMPC) están completas. Algunas opciones de L1 de otras facultades también están vacías.
- La página del parcours enlaza unos PDF de programa por año (`/_resource/UFR ST/Prog Licences/{PMPC_L1,PMPC_L2,ME_L3}_prog.pdf`). La página 1 de cada uno es una tabla a dos columnas (semestre impar a la izquierda, par a la derecha) con, por UE y élément, el **reparto de evaluación (% CC / % TP)**, las horas y los coeficientes. Es el único sitio donde se publica la evaluación de L2 y L3.
- Las UE compartidas (Portail PMPC) enlazan sus éléments con la ruta de otra licence (`licence-physique-…/ue…/anglais-….html`). El contenido es el mismo objeto Ametys.
- "Ouvert aux étudiants en échange : Non" aparece en algunas opciones de L1 de otras facultades.

## Fase 2: scraper
- `scraper_univ_rouen.py`: por cada fila descarga la página de la UE o de la opción y, después, cada élément de "Liste des enseignements". La salida tiene `# UE`, luego los metadatos y las secciones de la UE (`##`), y luego un `## Élément : …` por élément con sus secciones (`###`). Las horas se convierten en una tabla Markdown. El richtext se convierte en párrafos, listas y tablas.
- **Complemento PDF (solo L2 y L3)**: los enlaces `*_L{n}_prog.pdf` se localizan en la página del parcours. El script recorta la página 1 en dos columnas: el borde es el x0 del "UE" de la columna derecha; el límite superior es la primera "UE"; el inferior, el pie ("Lieu d'enseignement" o la leyenda "CM : …"). Después parte el texto por "UE n :" y lo asigna a la fila por (año, semestre relativo, nº de UE). En las opciones de L2 S4, el nº de UE se toma del `curso_semestre`. El resultado se añade como `## Programme L{n} (fiche PDF officielle)` en forma de lista jerárquica: UE → élément — (% CC, % TP) — horas | coef. Los nombres partidos en dos líneas se unen cuando la línea siguiente empieza por minúscula o "&". L1 no se complementa porque sus fichas HTML ya están completas y su PDF mezcla opciones de varias facultades.
- **Se descarta**: navegación, cabecera y pie del sitio, "Composante", los botones "Lire plus" y las secciones de contacto o responsables (por diseño, aunque no aparece ninguna en estas páginas). Los nombres de responsables solo figuran en el pie de los PDF, que queda fuera del recorte.
- **Validación**:
  - `--sample 5` con L5MCAVC2 (L1, física), L5MCBD8Q (L2, mecánica), LBVZT6JH (L3, sólidos deformables), LBVZT9VP (L3, con Stage) y L850MBB6 (opción au choix). Se revisaron a mano frente a la fuente.
  - Después `--all`: **42/42 Markdown**, exit 0.
  - Comprobación automática: todos los tokens de todas las secciones de las 118 páginas HTML usadas aparecen en el Markdown correspondiente (0 secciones con pérdidas), y no hay contenido del cuerpo fuera de las `<section>`.
  - Revisión manual adicional de los casos raros: L850MPFN (opción de la UFR LSH, secciones a nivel de UE, "En bref"), L5MCBYNV (opción sin éléments, con el bloque PDF de UE5 "1 choix parmi") y LBVZSVDG (nombre de UE partido en dos líneas en el PDF).
- **Bloques (42 filas)**:
  - Por bloque: contents 12, learning_outcomes 12, prerequisites 12, assessment 33, bibliography 0.
  - Las 9 UE obligatorias de L1 y las opciones L850MBB6 y L850MPFN tienen los 4 bloques principales. L850MNHF tiene todos menos assessment.
  - L2 y L3 (22 filas: 9 UE y 3 opciones en L2, 10 UE en L3): solo assessment, que viene del PDF.
  - Las otras 8 opciones de L1 de otras facultades no tienen ningún bloque (solo horas).
  - `bibliography` no aparece en ninguna ficha.
- Las horas de algunos éléments difieren ligeramente entre la ficha ODF y el PDF de programa. Se conservan ambas tal como figuran en cada fuente.
