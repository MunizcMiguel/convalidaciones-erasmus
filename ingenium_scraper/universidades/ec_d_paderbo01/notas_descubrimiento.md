# ec_d_paderbo01 – Universität Paderborn – Maschinenbau B.Sc. (6 sem., 180 LP)

## Fuente
- Modulhandbuch de la Fakultät für Maschinenbau (PDF, 191 págs., Stand 15.01.2026, SoSe 2026, carpeta `Alte_POen`):
  `https://mb.uni-paderborn.de/fileadmin-mb/fakultaet/Studiengaenge/Modulhandbuecher/Modulhandbuecher_SoSe_26/Alte_POen/Ba_MB_SS26.pdf`.
  Existe además el grado "Nachhaltiger Maschinenbau" (PO nueva, carpeta `Neue_POen`): no catalogado. Se tomó el Maschinenbau clásico.
- Host mb.uni-paderborn.de: PoliteClient lo sirve (robots.txt no bloquea). Sin plataforma web por módulo: todo en el PDF -> `pdf_compartido`.
- Idioma: alemán; muchas fichas llevan además versión inglesa del texto (en el mismo apartado, tras el alemán).

## Estructura
- Un módulo por tabla "Modulnummer: LP: Studiensem.: Turnus: Sprache:"; título DE (y EN) justo encima de "Workload". 56 módulos.
- Apartados numerados 1-13: 1 Modulstruktur (tabla de LV), 2 Wahlmöglichkeiten, 3 Teilnahmevoraussetzungen, 4 Inhalte, 5 Lernergebnisse, 6 Prüfungsleistung (tabla con pesos), 7-11 reglas, 12 Modulbeauftragte/r (nombre -> se elimina), 13 Sonstige Hinweise.
- Sin bibliografía en el handbook (bloque `bibliography` siempre false).
- Trampas: `pdfplumber` necesita `x_tolerance=1.5` (si no, pega las palabras); cabecera de página "N k. Studienjahr" y número de página al pie (se quitan); el anexo de la pág. 191 no es un módulo; el módulo "Sprachen" no tiene código (slug del nombre); casillas de (cid:52)/(cid:50) = [x]/[ ]; el final del bloque de un módulo arrastra el título "2.7 ..." del siguiente (se corta en el apartado 13); cabeceras DE+EN a veces con frases de intro encima.
- Suma bruta 390 LP porque están todos los módulos de las 7 Vertiefungen + Ingenieurinformatik + berufsbildende Anteile (alternativos); cada itinerario suma 180.
- `caracter` optativa = M.104.42xx-47xx (derivado del código); curso/semestre = primer semestre del rango.

## Fase 2
- `scraper_ec_d_paderbo01.py`: 56 de 56 Markdown, 0 fallos. Líneas de las tablas 1 y 6 se conservan tal cual (pesos de evaluación intactos). Listas con "•" -> "- ".
- Revisados a mano contra el PDF: M.104.1208, M.104.1205 (cola), M.104.1231, M.105.9451, M.104.4210 y A.104.4010. Defecto menor: los textos DE y EN de un mismo apartado quedan en párrafos seguidos, y los rótulos "Inhalte der Lehrveranstaltung X:" se mezclan en la línea.
- Bloques ausentes: bibliography (todos); M.104.4702 sin contenidos (módulo-catálogo vacío).
