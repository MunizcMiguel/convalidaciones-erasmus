# ec_a_wien02 — TU Wien

**Titulación:** Bachelorstudium Maschinenbau (E 033 245), 180 ECTS, 6 semestres, alemán. 50 módulos, 50 Markdown, catálogo `parcial` (nivel módulo, sin semestre).

## Fase 1
- Fuente: Studienplan 2026 (rev1), PDF con texto, anexo 'A Modulbeschreibungen', localizado en https://www.tuwien.at/tu-wien/organisation/zentrale-bereiche/studienabteilung/studienplaene (el discover elige el más reciente). Un bloque por módulo: título, 'Regelarbeitsaufwand: N ECTS', Lernergebnisse, Inhalt, Erwartete Vorkenntnisse, Verpflichtende Voraussetzungen, Lehr- und Lernformen y lista 'Lehrveranstaltungen des Moduls'.
- NO se usa TISS (guías por LVA): tiss.tuwien.ac.at/robots.txt dice Allow /course/ pero la página redirige a /admin/authentifizierung (login); además PoliteClient marca su robots.txt como bloqueado (Disallow: / global).
- Código: no hay código oficial; MB-{slug del título}. Páginas: rango por módulo derivado del texto (los módulos empiezan a mitad de página).
- Obligatorios+tesis suman 160 ECTS; Aufbaumodule y Berufsfeldorientierung se eligen entre varios (por eso la suma total supera 180). Sin semestre por módulo (curso/semestre null).
- Trampas: la lista de LVAs puede ir seguida de notas; el título es la línea anterior a 'Regelarbeitsaufwand'; el último módulo debe cortarse tras su lista de LVAs (sigue el anexo del plan).

## Fase 2
- scraper_ec_a_wien02.py (usa wien_parse.py): Markdown con Learning outcomes, Contents, Expected prior knowledge, Mandatory prerequisites, Teaching methods and assessment, Courses of the module. Sin profesorado (el PDF no lo contiene). No hay bibliografía en la fuente (bibliography=false).
