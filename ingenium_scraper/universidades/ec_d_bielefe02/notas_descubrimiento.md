# ec_d_bielefe02 – Hochschule Bielefeld (HSBI) – Maschinenbau B.Eng. (Vollzeit/kooperativ, 7 sem., 210 CP)

## Fuente
- Página de descargas del grado: `https://www.hsbi.de/studiengaenge/downloads/maschinenbau-bachelor`; el script extrae de ella el enlace «Studiengangsprüfungsordnung und Modulhandbuch Bachelor Maschinenbau Version 2025» (PDF de 204 págs., host www.hsbi.de; PoliteClient no encontró bloqueo en robots.txt). La URL «Version 12 (Fassung 2024)» que sale en buscadores da 404.
- Anlage A (págs. ~8-27) = Studienplan por Profilschwerpunkt (Energietechnik, Konstruktion y Entwicklung, Materialtechnik, Produktion und Logistik...); Anlage B (desde pág. 29) = Modulhandbuch, una ficha por módulo (1-2 págs.) que empieza con `Título KÜRZEL` + `Kennnummer: Workload: Credits: ...`. 91 módulos.
- Variantes no catalogadas: Maschinenbau praxisintegriert (Minden) y berufsbegleitend (otros PDF).

## Reglas
- Código = Kennnummer (4 dígitos). Semestre = primero en que el módulo aparece en cualquiera de los Studienplan (Anlage A); `obligatoria` = aparece en algún Studienplan (puede ser obligatorio solo de un Profilschwerpunkt); `optativa` = solo en el pool del handbook. Suma bruta 475 CP (>210) por esos pools/itinerarios.
- Títulos largos se parten en 2-3 líneas («... freies Wahl-» / «WM» / «pflichtmodul»): se recomponen.
- Los contenedores 9013-9016 (Wahlpflichtmodul ... / freies Wahlpflichtmodul) no tienen contenidos ni resultados de aprendizaje.
- Idioma: alemán. La bibliografía casi nunca está («Literatur wird zu Beginn der Veranstaltung bekannt gegeben»).

## Fase 2
- `scraper_ec_d_bielefe02.py --all`: 91 de 91 Markdown, 0 fallos. Secciones 1-15 de la plantilla; se elimina «13 Modulbeauftragte/r». Se quita el nº de página al pie.
- Revisados contra el PDF: Dynamik (1048), Produktionstechnik (1214), Einführung Maschinenbau (1053) y los contenedores 9016; el resto por muestreo de estructura.
- Defecto menor: la tabla de horas «1 Lehrveranstaltung» queda como líneas de texto, no como tabla Markdown.
