# Notas de descubrimiento — Universidad Alfonso X El Sabio (Grado en Ingeniería Mecánica)

- Fuente: PDF compartido `https://www.uax.com/download/8642/file/GMC_Guias_Docentes_plan_2020.pdf` (403 págs., 53 guías del plan 2020, EIAD). Hallado por búsqueda web; uax.com permite el acceso (robots) y el PDF se descarga con PoliteClient. El curso académico de la edición no figura en el PDF.
- Cada guía empieza en una portada «GUÍA DE LA ASIGNATURA / código nombre / CURSO nº periodo / ECTS n carácter / PROFESORES…»; el rango de páginas se deriva de las portadas. La portada de 'Advanced Technologies…' tiene el nombre en dos líneas.
- Trampas: códigos repetidos (0441843 ×2, 0341815 y 0341816 reutilizados para Motores/Regulación y Project Management/PFG; el segundo se sufija `-2`); erratas ('SEGFUNDO', 0241820 como curso 1º); ECTS con coma o punto.
- ECTS: básica 66 / obligatoria 144 / optativa 57 (ofertadas) / TFG 12 vs RUCT 60/150/18/12: básica+obligatoria = 210 coincide; el PDF clasifica 6 ECTS como básica de forma distinta.
- Plan 2020 del título RUCT 2501331; solo un centro.

## Fase 2
- `scraper_es_alfonso_x_sabio.py`: texto con pdfplumber; se descarta lo que sigue a PROFESORES en la portada (nombres), los pies de página y la sección ADENDA (vacía). Secciones numeradas 1-9 reconocidas por título.
- 53/53 Markdown. Verificado el de Mecánica (todas las secciones, evaluación con porcentajes). Ausentes frecuentes: requisitos previos (la guía dice «No se han establecido»); Prácticas en Empresa sin bibliografía. Nota: tablas del cronograma salen como líneas de texto, no tabla Markdown.
