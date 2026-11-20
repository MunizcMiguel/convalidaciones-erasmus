# ec_p_porto02 — Universidade do Porto (FEUP)

**Titulación:** Licenciatura em Engenharia Mecânica (L.EM), 1.er ciclo, 3 años, 180 ECTS (código FEUP `L.EM###`). El MIEM (mestrado integrado) no se usa.

## Fase 1
- Fuente: fichas de UC de SIGARRA (`https://sigarra.up.pt/feup/pt/ucurr_geral.ficha_uc_view?pv_ocorrencia_id=…`, versión EN) ya extraídas por el usuario; `prepare_fuente_previa.py` las copia a `fuente_previa/` sin profesorado y conserva el curso (año) en L.EM sacado de "Cycles of Study".
- **Bloqueo:** `sigarra.up.pt/robots.txt` permite `User-agent: *` (aunque veta ClaudeBot, etc. y declara `Content-Signal: ai-train=no`), pero la ficha devuelve **HTTP 403** a PoliteClient (Cloudflare). Regla de parada: no se rodea. Por eso `url_plan_estudios` es solo el portal (no verificado).
- 47 filas: 31 UC L.EM (L.EM001–031: 12 de 1.º, 12 de 2.º, 7 de 3.º… ver catálogo) = 175,5 ECTS (faltan ~4,5 ECTS de optativas/área no listadas) + 16 UC transversales/optativas de 1,5 ECTS (FEUP003, AADL01, CP01…). Catálogo `parcial`.
- Idioma docente casi siempre portugués; la ficha usada es la versión inglesa del portal (objetivos, programa, etc. traducidos; títulos de bibliografía en portugués).

## Fase 2
- `scraper_ec_p_porto02.py` no usa red: Markdown desde `fuente_previa/feup_fichas.json` (Objectives, Learning outcomes, Pre-requirements, Program, Working method, Teaching methods, Evaluation, Assessment Components con porcentajes, literatura…). 47/47. Sin docentes, horarios ni contactos.
- Defecto heredado de la extracción previa: palabras portuguesas pierden letras acentuadas en algunas secciones (p. ej. «Organizao e Gesto»). No se puede corregir sin volver a descargar.
