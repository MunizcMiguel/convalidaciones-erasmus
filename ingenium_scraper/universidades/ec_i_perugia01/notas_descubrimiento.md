# ec_i_perugia01 — Università degli Studi di Perugia (Ingegneria Meccanica L-9)

## Fase 1
- Titulación: Corso di laurea in Ingegneria meccanica (L-9, idcorso 8439; existe también Ingegneria industriale 8440). Regolamento 2025/26 (coorte 2025).
- El catálogo Cineca de UniPG (unipg.coursecatalogue.cineca.it) está vetado por robots.txt y Esse3 es un área de login: no se usan. La fuente es el portal público www.unipg.it (robots permite), oferta formativa: listado `...archivio/offerta-formativa-2025-26?view=elenco&...&idcorso=8439&tab=INS` (h4 por año + tabla) y ficha `&idins={id}` (tabla th/td). El idins cambia por año académico (2026-27 tiene otros idins).
- 30 filas (años 1-3 + grupo de optativas); 25 con ficha. Los CFU del listado suman más de 180 porque incluyen variantes por currículo (Energia/Produzione..., filas "+") y optativas. Código = 'Codice insegnamento'; si se repite entre idins, sufijo con el idins.
- Idioma: italiano (la ficha está en el idioma de impartición); hay PDF de programas por asignatura en ing.unipg.it (no usados).

## Fase 2
- `scraper_ec_i_perugia01.py`: 1 GET por ficha; cursos integrados (varias tablas con título de módulo) se renderizan como `## Modulo: X`. Se omiten Docente responsabile/Docenti/Ore y se filtran líneas de contacto/recibimiento.
- 25 Markdown comprobados contra el HTML de origen (final de cada campo presente). Años 2-3 del regolamento 2025 aún sin ficha para 5 filas (Tecnologia meccanica, Impianti industriali, Engineering economy, Fondamenti di bioingegneria, Lingua inglese B1).
