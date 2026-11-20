# ec_tr_zonguld01 — Zonguldak Bülent Ecevit Üniversitesi (Mechanical Engineering)

- Hint `erasmus.beun.edu.tr/factsheet.html` = web Erasmus (correcta; no es el catálogo). El catálogo es el **OBP (Öğrenci Bilgi Paketi) `https://obs.beun.edu.tr/oibs/bologna/`**, el mismo OBS/Proliz que Gazi (ver `ec_tr_ankara02`); robots.txt 404 → permite.
- Grado: Faculty of Engineering → Mechanical Engineering (curSunit=38, programa diurno; «Evening» = 43, no usado), currículo «2024 ve sonrası». Lista de grados: `unitSelection.aspx?type=lis&lang=en`; plan: `progCourses.aspx?lang=en&curSunit=38`; ficha: `progCourseDetails.aspx?curCourse={id}&lang=en` (id en `prolizOpenCourseDetails(id)`).
- 110 asignaturas; ECTS obligatorios por semestre (según las tablas «Total ECTS» del plan): 29, 25, 30, 30, 30, 30, 30, 23 = **227 en total, no 240** (el plan de la universidad suma 227 con las tablas de semestre; las optativas ofertadas son 311 ECTS y las obligatorias 169 — el reparto exacto de cupos no está en las tablas). Se deja `ects_totales_plan` = 227 tal como lo da el plan.
- Idioma: instrucción turca («Language of Instruction: Turkish») pero títulos y texto de las fichas en inglés en la interfaz `lang=en` → idioma de página `en`.

## Fase 2
- Scraper copiado de Gazi (`scraper_ec_tr_ankara02.py`, plantilla OBS/Proliz) con otro slug y muestra (MM111, MM217, MM352, MM402, MM441); se eliminan Course Coordinator, Name of Lecturers y Assistants. 110/110 escritos; 3 con algún bloque ausente en origen.
