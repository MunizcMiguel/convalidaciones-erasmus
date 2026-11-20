# ec_d_gelsenk02 – Westfälische Hochschule Gelsenkirchen – Maschinenbau B.Eng.

## Fuente
- Páginas: `https://www.w-hs.de/hochschule/fachbereiche/maschinenbau-umwelt-und-gebaeudetechnik/der-fachbereich/pruefungsamt-maschinenbau/modulhandbuecher/` (Prüfungsamt) enlaza los PDF sin extensión `.pdf`.
- Usado: `https://www.w-hs.de/fileadmin/Oeffentlich/Fachbereich-1/Studiengaenge/MB_BA/1A_ModulhandbuchBachelorMB_2024.11.15` (Stand 15.11.2024, 107 págs., texto extraíble; cubre grundständig, praxisintegrierend y Teilzeit).
- No usado: `.../Pruefungsamt/MB/ModulhandbuchBachelorMBReakkreditierung_2026_10_01` (plan nuevo desde 01.10.2026): sus fichas tienen el título de módulo como imagen (sin texto), no extraíble sin OCR.
- No accesible: `winweb.w-hs.de` (sistema antiguo de módulos) agota el tiempo de conexión desde esta red; no se usa.
- robots.txt de www.w-hs.de: PoliteClient no encontró bloqueo.

## Estructura
- 52 módulos de 6 ECTS (PP Praxisphase 14, BA 10). Ficha: título, tabla «Kennnummer Workload Credits Studiensemester Häufigkeit Dauer» y apartados 1-12 (1 LV, 2 Lernergebnisse, 3 Inhalte, 4 Lehrformen, 5 Voraussetzungen, 6 Prüfungsformen, 7-8 requisitos, 9 Verwendung, 10 Stellenwert, 11 Modulbeauftragter (se elimina), 12 Literatur).
- Código = Kennnummer (abreviatura: MA1, TM2, «FV 1»). Semestre = el del grado grundständig; hay erratas aparentes en el PDF (TM3 = 1.º, TD1/TD2 = 4.º) copiadas tal cual; «Ab dem 3.» → 3; HLW/PVW sin semestre.
- La ficha no distingue obligatorio/optativo → caracter solo tfg/practicas. Los 52 módulos suman 324 ECTS porque incluyen optativos y itinerarios (el plan exige 180).
- Trampas: pie de página «WHS FB1 – ... Stand 15.11.2024 N» a eliminar; títulos con diacríticos descompuestos (NFC); palabras partidas por el PDF («Somme rsemester»).

## Fase 2
- `scraper_ec_d_gelsenk02.py --all`: 52 de 52 Markdown, 0 fallos. Revisados contra el PDF: TM2, MWS (Metallische Werkstoffe), SM y BA.
- Bloques ausentes: bibliography en varios (solo «Vorlesungsskript» sin referencias), prerequisites cuando pone «Keine».
