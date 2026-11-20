# ec_d_hamburg03 — TU Hamburg (TUHH)

**Titulación:** Maschinenbau / Mechanical Engineering (B.Sc., 7 semestres, 210 CP, código MBBS). Catálogo `parcial` (sin semestres ni contenidos en la fuente), 50 módulos, 50 Markdown.

## Fase 1
- Fuente: Modulhandbuch HTML en inglés (un único documento, ~800 KB) enlazado desde https://studienplaene.tuhh.de/index.php?stgart=B&stgB=MBBS&kid=54&Lang=en (cohorte WiSe 2026/27): po/MB/mhb_MBBS_kh_w26_von_20260601_v_0_en.html (también PDF y versión alemana). El discover localiza el enlace en la página.
- robots.txt: studienplaene.tuhh.de permite (solo veta /error/ y /deleted/). www.tuhh.de/robots.txt se auto-veta (Disallow: /robots.txt) y PoliteClient lo informa como bloqueado; no se usó ninguna página de www.tuhh.de.
- Estructura: una `table.mHead` (h2 'Module Mxxxx: nombre' + tabla de cursos) seguida de `table.mContent` (filas td.l/td.r). 64 bloques → 50 módulos únicos (los módulos se repiten entre especializaciones). h1 = bloque: Core Qualification (156 CP), 7 Specializations, Thesis (M-001).
- Trampas: código M-001 (guion) para la tesis; el semestre NO figura en el Modulhandbuch (curso/semestre null); los CP suman más de 210 porque se elige una especialización.

## Fase 2
- scraper_ec_d_hamburg03.py: tabla de cursos + Admission Requirements, Recommended Previous Knowledge, Educational Objectives (Knowledge/Skills/Social/Autonomy), Workload, Credit points, Course achievement, Examination. Se omite Module Responsible (docente) y la asignación a currículos.
- Hechos de la fuente: NO hay contenidos/temario ni bibliografía en el Modulhandbuch (contents=false, bibliography=false en todos); la descripción por curso (Lehrveranstaltungen) se publica aparte y no se localizó.
