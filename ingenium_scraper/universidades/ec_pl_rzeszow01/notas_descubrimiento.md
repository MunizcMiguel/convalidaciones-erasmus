# ec_pl_rzeszow01 — Politechnika Rzeszowska (parcial, sin Fase 2)
- Titulación: Inżynieria mechaniczna, 1.er ciclo, 7 sem., 210 ECTS, en polaco (dwm.prz.edu.pl solo da el Erasmus; el BSc en inglés de PRz es otro).
- Fuente: "Program studiów" cycle 23/24 (Uchwała Senatu 53/2022), PDF en bip.prz.edu.pl/download/… (robots solo veta /files/ y /ajax/). El plan (sec. 3.1, páginas 4-5) es texto con filas `semestre unidad nombre W C L P suma ECTS T/N`.
- Se extraen solo filas completas en una línea: 36 filas, 143 ECTS; 10 omitidas por nombre partido; los bloques optativos y de especialidad (3.2) no se incluyen. Código derivado: `S{semestre}-{slug del nombre}`. Plan 23/24, puede no ser el vigente.
- Sin fichas por asignatura públicas localizadas (el PDF solo trae contenidos de algunas): todas `sin_guia`, sin Fase 2. Pendiente: buscar portal de sílabos de PRz (no verificado).

## Segunda pasada (descartada)
- Facultad: wbmil.prz.edu.pl (robots: veta /files/ y /ajax/). /kierunki/inzynieria-mechaniczna y /dla-studentow/plany-studiow no enlazan karty de asignatura en HTML; los documentos del plan van por /files/ (vetado) o por bip.prz.edu.pl (solo «Program studiów»). Búsqueda web sin portal público de sílabos de PRz. Siguen 36 filas `sin_guia`.

## Tercera pasada (2026-11-20) — oferta Erasmus en inglés
- `https://dwm.prz.edu.pl/en/erasmus/student/courses-in-english` enlaza PDFs por facultad; el de la Facultad de Ingeniería Mecánica y Aeronáutica es `…/fcp/…/przedmioty_erasmus/wbmil_aktualizacja_2026.pdf` (robots de dwm solo veta /files/ y /ajax/; /fcp/ permitido). 15 págs., tabla `No./Subject/ECTS/Description/Remarks`; las filas continúan entre páginas (filas con No. vacío = continuación). 52 asignaturas (mezcla mecánica y aeronáutica), 193 ECTS ofertados; sin curso/semestre ni código oficial («courses don't have individual codes»): código `ERAnn-{slug}`.
- Se añaden al catálogo (tipo `pdf_compartido`, `paginas_pdf` por fila); las 36 filas del plan 23/24 siguen `sin_guia`. `scraper_ec_pl_rzeszow01.py`: 52/52 Markdown (descripción de contenidos + remarks; sin resultados de aprendizaje, evaluación ni bibliografía, que el PDF no trae). Son descripciones breves, no guías completas.
- No explorado: PDFs de otras facultades (wmt.prz.edu.pl, etc.).
