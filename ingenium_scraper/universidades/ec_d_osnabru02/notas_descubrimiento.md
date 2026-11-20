# ec_d_osnabru02 – Hochschule Osnabrück – Maschinenbau B.Sc. (StO 2025)

## Fuente
- Modulhandbuch PDF (328 págs., Stand 26.03.2026, Prüfungsordnung 01.09.2025): `https://www.hs-osnabrueck.de/fileadmin/Modulhandbuch/BMB/StO2025_Stand2026-03-26_BSc_Maschinenbau.pdf` (patrón común `fileadmin/Modulhandbuch/{COD}/StO{año}_Stand{fecha}_{Nombre}.pdf`; URL localizada por búsqueda, no desde la web de la facultad). Host www.hs-osnabrueck.de: PoliteClient no encontró bloqueo en robots.txt.
- Grado: Maschinenbau B.Sc. (6 sem., 180 ECTS). Variantes no catalogadas: Maschinenbau im Praxisverbund, Fahrzeugtechnik, Aircraft and Flight Engineering, Mechatronik.
- El PDF es un catálogo de 77 módulos (Pflicht + Wahlpflicht + módulos compartidos); NO hay plan por semestres → semestre/curso = null y sin obligatorio/optativo. Suma bruta 435 ECTS.

## Estructura de una ficha
- Título en MAYÚSCULAS (1-2 líneas) + título inglés + «Allgemeine Informationen zum Modul» (Modulkennung 11Bnnnn, Unterrichtssprache, ECTS) + Modulinhalte (Kurzbeschreibung, Lehr-Lerninhalte) + Arbeitsaufwand (horas) + Prüfungsleistung + Voraussetzungen + Kompetenzorientierte Lernergebnisse + Literatur + Verwendbarkeit nach Studiengängen + «Am Modul beteiligte Personen» (nombres: se elimina) + «Zurück zum Inhaltsverzeichnis».
- Título con mayúsculas/minúsculas correctas tomado del Inhaltsverzeichnis (pp. 2-4). Idioma por módulo (de/en).
- Pie de página «HOCHSCHULE OSNABRÜCK | MODULHANDBUCH N» a eliminar; NFC.

## Fase 2
- `scraper_ec_d_osnabru02.py --all`: 77 de 77 Markdown, 0 fallos; los 5 bloques presentes en todos. Revisados contra el PDF: 11B2312 (Einführung in den Maschinenbau) y 11B2351 (Additive Fertigung), más la estructura de las demás de la muestra.
- Defecto menor: apartados vacíos de la fuente salen con «-»; tablas de horas (Dozentengebundenes Lernen) como líneas de texto.
