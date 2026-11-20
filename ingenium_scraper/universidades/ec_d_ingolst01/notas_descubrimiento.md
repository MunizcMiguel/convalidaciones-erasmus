# ec_d_ingolst01 — Technische Hochschule Ingolstadt (THI)

**Titulación:** Maschinenbau (B.Eng.), 7 semestres, 210 ECTS (SPO WS 2023/24). Es el grado equivalente a Ingeniería Mecánica.

## Fase 1
- Fuente: Modulhandbuch WS 2026/27 (PDF compartido, alemán) enlazado desde `https://www.thi.de/en/mechanical-engineering/degree-programmes/mechanical-engineering-beng/` (el discover lo localiza en el HTML: `.../Bachelor_MB/MHBuch_MB_SPO_2023_24_Stand_2026-07-16.pdf`) y PDF de Wahlpflichtmodule `.../FW-Faecher_Modulhandbuch_WS26_27.pdf` (solo se incluyen los módulos asignados a "Maschinenbau Bachelor (MB-B)").
- Reutiliza el trabajo previo del usuario (`OfertaTHI_Maschinenbau_Details.json`, mismo PDF), pero el pipeline vuelve a leer el PDF oficial vía PoliteClient para que sea reproducible. El JSON previo asignaba semestre 5 por error a casi todos; aquí el semestre sale de "Studiensemester" de cada ficha.
- robots.txt de www.thi.de: sin bloqueo para la página del grado ni `/fileadmin/` (PoliteClient no lanzó RobotsBlocked).
- Código: "Modulkürzel" oficial (puede partirse en dos líneas con guion). Un módulo = 2-3 páginas; rango = desde su página hasta la anterior al siguiente módulo.
- 64 filas: 39 del Modulhandbuch principal (32 con semestre; 7 Wahlpflicht de Studienrichtung sin semestre fijo) + 25 electivos FW. Obligatorios suman 180 ECTS; el resto de los 210 son electivos/optativos de la Studienrichtung, FW y FW-Wahlpflicht (a elegir) — no se pueden sumar sin elección.
- Trampas: cabecera de página ("MB-B (SPO…", "MHB:…", nº) se elimina; títulos de sección "5.x" encabezan algunas páginas.

## Fase 2
- `scraper_ec_d_ingolst01.py`: pypdf, texto por páginas → Markdown con `##` por etiqueta (Angestrebte Lernergebnisse, Inhalt, Literatur, Prüfungsleistungen…). Se eliminan "Modulverantwortliche(r)" y "Dozent(in)".
- 64/64 Markdown. Hay módulos en inglés (detectados por "The students"). La tabla de asignación a titulaciones de los electivos FW se conserva aplastada en una línea (ruido leve). Bibliografía con cortes de línea residuales; no se pierde contenido.
- No hay peso porcentual de evaluación (solo tipo y duración de examen) — es un hecho de la fuente.
