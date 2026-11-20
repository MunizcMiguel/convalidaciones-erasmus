# UPC — Grado en Ingeniería Mecánica (EPSEVG) · notas de descubrimiento

Estado: **parcial**. Catálogo completo (Fase 1); **sin Fase 2** por la regla de parada (robots.txt excluye la ruta de las guías).

## Título, centro y plan

- RUCT 2501218, "Graduado o Graduada en Ingeniería Mecánica por la UPC" (RD 1393/2007; único título en `config/universities_es.json`). Las guías lo llaman "Plan 2009".
- Centro elegido: Escuela Politécnica Superior de Ingeniería de Vilanova i la Geltrú (EPSEVG), el primero de la lista. También se imparte en EPSEM (Manresa), ESEIAAT (Terrassa) y EEBE (Barcelona Este), cada uno con su propia ficha `www.upc.edu/es/grados/ingenieria-mecanica-...` y sus propios códigos de asignatura.

## Fuente del catálogo

- `https://www.upc.edu/es/grados/ingenieria-mecanica-vilanova-i-la-geltru-epsevg` (ficha oficial del grado, castellano, HTML estático; robots.txt la permite).
- El plan está en `div#pla-estudis`: un `div.pla-estudis-quadrimestre` por cuatrimestre (`h3` "Primer cuatrimestre" … "Octavo cuatrimestre") y un `li` por asignatura:
  - clase CSS del `li` → carácter (`Obligatoria`, `Optativa`, `Proyecto`);
  - `a[data-id]` → código oficial de la asignatura (6 dígitos, 340xxx = EPSEVG);
  - `a[href]` → guía docente; `span.pull-right` → ECTS.
  - El último bloque (`id="llegenda"`) es la leyenda y se descarta.
- La web del centro (`https://epsevg.upc.edu/es/estudios/grado-en-ingenieria-mecanica`) incrusta el mismo widget pero con menos optativas (75 enlaces frente a 93); se usa la ficha central por ser la más completa.
- No se ha encontrado API/JSON público del plan (`api.upc.edu` y `guiadocent.upc.edu` no resuelven).

## Resultado

- 93 asignaturas, sin códigos duplicados: 31 obligatorias (186 ECTS), 61 optativas (363 ECTS ofertados), TFG (24 ECTS).
- Contra el RUCT (60 básica + 126 obligatorios + 30 optativos + 0 prácticas + 24 TFG = 240): la ficha no separa formación básica de obligatoria, así que 186 = 60 + 126; TFG 24; el estudiante elige 30 ECTS de la oferta optativa. 186 + 24 + 30 = 240 = carga lectiva de la ficha.
- Curso académico: 2026-27, leído de la ficha ("Nota de corte del curso 2026-2027"). La ficha no indica el curso de las guías enlazadas.
- Idioma: `es` (enlaces a la versión `/esp/` de la guía; existen también `/cat/` y `/eng/` según el patrón, no comprobado).

## Guías docentes y regla de parada

- Patrón: `https://www.upc.edu/content/grau/guiadocent/pdf/esp/{codigo}` → un PDF por asignatura, generado por la aplicación de guías de la UPC (PRISMA). Es la forma que enlaza la web de la EPSEVG.
- La ficha central escribe el enlace como `https://www.upc.edu/content/../grau/guiadocent/pdf/esp/{codigo}/{slug}.pdf`. Normalizado queda `/grau/guiadocent/...`, que **redirige** a `/content/grau/guiadocent/pdf/esp/{codigo}`.
- `https://www.upc.edu/robots.txt`, grupo `User-agent: *`: **`Disallow: */content/*`**. La ruta real de las guías queda excluida para robots. Por tanto: no se descargan guías, no hay `scraper_es_politecnica_catalunya.py` ni Markdown.
- Trampa: `PoliteClient` no detecta este bloqueo. `urllib.robotparser` no entiende comodines (`*/content/*` se trata como prefijo literal) y además solo se comprueba la URL pedida, no el destino de la redirección. `discover_*.py` hace su propia comprobación con comodines (RFC 9309) y fija `estado: "parcial"` a partir de ella; si la UPC retirase la regla, el script pondría `ok`.
- Incidencia: durante la exploración, antes de ver la redirección, se descargó UNA guía (340023, Física I) por la URL normalizada `/grau/...`. Al comprobar que el destino final era `/content/...` se borró de `raw_cache` y no se ha vuelto a pedir ninguna. De ese único vistazo: PDF con texto (5 páginas), secciones en mayúsculas — PROFESORADO, COMPETENCIAS DE LA TITULACIÓN…, METODOLOGÍAS DOCENTES, OBJETIVOS DE APRENDIZAJE, HORAS TOTALES DE DEDICACIÓN (tabla), CONTENIDOS, SISTEMA DE CALIFICACIÓN, BIBLIOGRAFÍA, RECURSOS — y pie "Fecha: … Página: n / N" en cada página.
- Si se obtiene permiso de la UPC (o una vía de datos abiertos), la Fase 2 sería un scraper de "PDF por asignatura" con pdfplumber, cortando por esos encabezados y eliminando PROFESORADO.

## Otros hosts mirados

- `epsevg.upc.edu`: robots.txt permite; solo enlaza a las mismas guías en `www.upc.edu/content/`.
- `apren.upc.edu`: página vacía ("apren2"), sin guías.
