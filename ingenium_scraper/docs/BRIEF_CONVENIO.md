# Worker brief — destinos Erasmus+ de Mecánica de Uniovi (addendum)

Lee primero `docs/BRIEF_FASES_1_2.md` (entregables, regla de parada, validación, informe) y `docs/PLATAFORMAS.md`. Este fichero añade lo propio de esta tanda; donde difieran, manda este.

## Qué se pide

Las universidades de `config/universities_convenio.json` (buscar por `slug`) son destinos Erasmus+ reales del Grado en Ingeniería Mecánica de la Universidad de Oviedo. Para cada una hay que encontrar **la titulación de grado equivalente a Ingeniería Mecánica** (Mechanical Engineering / Maschinenbau / Ingegneria Meccanica / Génie mécanique / Inżynieria mechaniczna…), su plan de estudios y las guías docentes de sus asignaturas, y dejar el Markdown limpio listo para la Fase 3.

- Si hay varias titulaciones afines (p. ej. Mechanical Engineering y Mechatronics), toma la más parecida a Mecánica y nómbrala en `meta.notas`. Es grado (1.er ciclo), no máster. En Italia, la Laurea (triennale), no la Magistrale.
- Cursos 2.º-4.º son los que importan para convalidar; cubre el plan completo si es viable. Si solo hay datos de algunos cursos, dilo en `meta.notas`.
- `codigo_asignatura`: el oficial si existe; si no, un slug estable del nombre.

## Sitio real de la universidad

El campo `web_hint_no_fiable` / `domain_hint_no_fiable` sale de la ficha Erasmus que enlazaba el Excel y **a menudo no es el sitio de la facultad** (a veces ni de la misma universidad). Identifica tú el sitio oficial por el nombre y el código Erasmus (`erasmus_code`) y comprueba que corresponde a la universidad correcta. Las que tienen `existing: true` (hka, mtu, univ_rouen, tuiasi) ya tienen trabajo hecho en `universidades/{slug}/`: no las repitas; ignóralas.

## Idioma

Prefiere la versión en inglés de la guía si existe; si no, la del idioma local. Anota el idioma por fila. Elimina siempre secciones de profesorado, contactos, despachos y horarios de tutoría.

## Lo que NO se hace

- No entrar en áreas con login, ni usar navegadores automatizados para saltarse filtros, ni cambiar el user-agent, ni desactivar la verificación TLS. `PoliteClient` es el único cliente HTTP. Si lanza `RobotsBlocked` o hay 403/desafío JS/certificado inválido: regla de parada (catálogo `parcial` con notas y pasa a la siguiente).
- Si la titulación no tiene guías públicas, `parcial` con el motivo. No inventes datos.

## Economía

Una universidad a la vez, sin subagentes. Presupuesto aproximado: ~15 llamadas de herramienta sin avanzar y la dejas `parcial`. No imprimas HTML/PDF/JSON enteros. Antes de escribir un scraper busca en `docs/PLATAFORMAS.md` si la plataforma ya está resuelta (CINECA, Moodle de catálogos, PDFs de módulos tipo Modulhandbuch, etc.). Añade UNA entrada por universidad al final de `docs/PLATAFORMAS.md`.

## Informe (máx. 200 palabras)

Por universidad: titulación elegida, nº de asignaturas, nº de Markdown, bloqueos/`parcial` y lo no verificado.
