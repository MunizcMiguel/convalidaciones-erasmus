# Munster Technological University (mtu) — notas de descubrimiento

Bachelor of Engineering (Honours) in Mechanical Engineering — CAO **MT 836**, NFQ Level 8, 4 años, full-time, MTU Bishopstown Campus (Cork). Código de programa en Akari: **`CR_EMECH_8`**. Generado por `discover_mtu.py` (12-11-2026).

## Estado: PARCIAL — regla STOP activada, sin Fase 2
El plan de estudios y los descriptores de módulo solo viven en `mtu.akarisoftware.com`, y ese host **rechaza el acceso automatizado** (403 a nuestro bot). No se ha descargado nada de él. `catalogo_urls.json` tiene `estado: "parcial"` y `asignaturas: []`; no existe `scraper_mtu.py`.

## Hosts y veredicto
| Host | Qué sirve | robots.txt / acceso |
|---|---|---|
| `www.mtu.ie` | Ficha comercial del grado (`/courses/mt836/`) | robots.txt existe. Para `User-agent: *`: `Disallow: /search/`, `/search-t4/`, `/component-library/` y **`Crawl-delay: 10`**. `/courses/` permitido. (Veta por completo a los bots de entrenamiento de IA nombrados: GPTBot, ClaudeBot, CCBot…; nuestro bot cae en `*`.) El script usa `min_delay=10`. |
| `mtu.akarisoftware.com` | Akari Curriculum: plan por etapas/semestres + descriptor de cada módulo | **Bloqueado.** Con el User-Agent del proyecto (`IngeniumSyllabusBot/0.1 (academic research; polite crawler)`) devuelve `403 Forbidden` (página Apache) en TODAS las rutas: `/robots.txt`, la página del programa y una ruta inexistente. Con el UA por defecto de curl, `/robots.txt` da `404` → no hay robots.txt y el 403 es un filtro del servidor contra clientes que se identifican como bot/crawler. |
| `courses.mtu.ie`, `courses.cit.ie`, `modules.mtu.ie` | (hosts históricos) | Ya no resuelven en DNS. |

Peticiones hechas a Akari en total: 4 diagnósticas (robots.txt ×2, página del programa ×1, ruta inexistente ×1) + 1 del `--probe-akari`. Ningún contenido obtenido.

## Fuente usada
- `https://www.mtu.ie/courses/mt836/` (TerminalFour, HTML estático). De ella se parsean: título (`h1`), tipo de título (línea siguiente), `Type of Programme`, `Duration`, `Course NFQ Level`, `Course Code`, `Location(s)` y el enlace "View Modules" (único `<a>` a `mtu.akarisoftware.com/index.cfm/page/course/coursecode/{CODIGO}`).
- La sección `#modules` de la ficha **no lista módulos**: solo el botón a Akari. Lo único parecido es "First year at a glance": 9 nombres informales de 1.º sin código ni créditos (guardados en `meta.notas`, no como filas: convertirlos en filas exigiría inventar códigos y ECTS).
- La ficha no publica los ECTS totales → `ects_totales_plan: null` (lo habitual en un Level 8 de 4 años son 240, no verificado en fuente).
- `curso_academico` = "2026/27", derivado de "CAO Points in 2026" de la ficha.
- El sitemap `https://www.mtu.ie/sitemap-en.xml` lista las fichas `/courses/{codigo}/` pero ningún PDF de plan ni página de módulos. Variantes vistas: MT 836 (este, honours Level 8), MT 736 / `cremecn7` (Level 7, no honours), MT 830 (Common Entry Level 8 que desemboca en MT 836).

## Patrones de URL en Akari (conocidos, NO verificados por el bloqueo)
- Programa: `https://mtu.akarisoftware.com/index.cfm/page/course/coursecode/CR_EMECH_8`
- Módulo (patrón habitual de Akari, sin comprobar): `.../index.cfm/page/module/moduleId/{id}` o `.../page/module/moduleCode/{CODIGO}`.

## Trampas
- PoliteClient considera "permitido" un robots.txt que no devuelve 200, así que no detecta este bloqueo por sí solo: la petición de contenido falla después con `FetchError: HTTP 403 (no reintentable)`.
- La ficha de www.mtu.ie no es UTF-8 limpio (algún byte suelto cp1252); `get_text` cae a latin-1 sin problema para los campos usados.
- `discover_mtu.py` aborta a propósito si la sección `#modules` pasa a contener una lista/tabla (señal de que MTU ha publicado el plan en su web y hay que rehacer el descubrimiento).

## Cómo desbloquear (decisión del usuario)
1. Pedir permiso / lista blanca a MTU (Registrar's Office / Academic Affairs) o a Akari Software para el UA del proyecto, definiendo `SCRAPER_CONTACT`; después `python universidades/mtu/discover_mtu.py --probe-akari` indica si el 403 ha desaparecido.
2. Pedir a MTU el "programme schedule" y los descriptores en PDF/exportación.
3. Descarga manual por una persona desde el navegador, dejando los HTML en una carpeta local que un parser lea sin red.
No se ha probado (deliberadamente) cambiar el User-Agent por uno de navegador ni usar Playwright: sería saltarse el bloqueo.

## Fase 2
No ejecutada (regla STOP).
