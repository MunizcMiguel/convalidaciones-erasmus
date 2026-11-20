# Prompt maestro v2 · Extracción de guías docentes del consorcio INGENIUM

> Versión mejorada del prompt original. Los cambios y su motivo están al final.
> Pensado para pegarse en un entorno agéntico local abierto en la carpeta `ingenium_scraper/`.

## Objetivo

Construir una base de datos unificada con las guías docentes del Grado en Ingeniería Mecánica (o el grado de ingeniería equivalente más cercano) de las 10 universidades de la alianza INGENIUM. Los datos alimentarán un motor que compara asignaturas entre universidades para preparar Learning Agreements de Erasmus+, así que lo que importa es que el contenido sea fiel, completo y comparable.

## Principio de diseño

Los agentes LLM **escriben y reparan código**; no transportan datos. Todo dato que acabe en el catálogo o en la base de datos debe salir de un script determinista y reejecutable, nunca de un agente que lo copie a mano. Así el resultado es reproducible, no hay asignaturas inventadas y el curso que viene basta con volver a ejecutar los scripts. El único punto donde un LLM toca los datos es la Fase 3, y lo hace a través de una API externa con salida validada contra un esquema.

## Universidades (slug · dominio)

1. Universidad de Oviedo · `uniovi` · uniovi.es
2. University of Skövde · `his` · his.se
3. Karlsruhe University of Applied Sciences · `hka` · h-ka.de
4. Munster Technological University · `mtu` · mtu.ie
5. University of Crete · `uoc` · uoc.gr
6. Gheorghe Asachi Technical University of Iași · `tuiasi` · tuiasi.ro
7. Medical University of Sofia · `mu_sofia` · mu-sofia.bg — probablemente sin grados de ingeniería: comprobarlo y, si es así, registrar el catálogo con `estado: "n/a"` y la explicación.
8. University of Rouen Normandie · `univ_rouen` · univ-rouen.fr
9. South-Eastern Finland University of Applied Sciences (Xamk) · `xamk` · xamk.fi
10. University Gabriele d'Annunzio of Chieti-Pescara · `unich` · unich.it

Orden de despliegue: primero las tres piloto (`uniovi`, `his`, `hka`) hasta completar las cuatro fases; después el resto.

## Lo que ya existe (léelo antes de escribir nada)

- `common/http_client.py` — `PoliteClient`: pausa aleatoria de 1–3 s por host, reintentos con exponential backoff, respeto de robots.txt y caché en disco. Todo acceso a red pasa por aquí.
- `common/schema.py` — contratos de datos: `Catalog` (Fase 1) y `SyllabusExtraction` / `SyllabusRecord` (Fase 3).
- `common/util.py` — `write_markdown()` (cabecera de trazabilidad + anonimización determinista) y utilidades.
- `orchestrator.py`, `semantic_parser.py`, `qa_master_db.py` — las fases 3 y 4 y la orquestación ya están escritas. No las reescribas; si un contrato no encaja con una universidad, propón el cambio.

## Fase 1 · Descubrimiento (un agente por universidad, en paralelo)

Cada agente trabaja solo dentro de `universidades/{slug}/` y entrega:

- `discover_{slug}.py`: localiza el plan de estudios oficial y genera `catalogo_urls.json` validado con `Catalog`.
- `notas_descubrimiento.md`: qué fuente se usó, patrones de URL, cómo está estructurada una guía y qué trampas hay. Es el traspaso al agente de la Fase 2.

Criterios:

- Elegir la fuente más estructurada disponible, en este orden: API o JSON que alimenta la web, exportaciones, PDF de plan de estudios o Modulhandbuch, y solo al final el DOM. Muchas webs académicas son SPA con un endpoint JSON detrás; buscarlo antes de recurrir a Playwright.
- Preferir la versión oficial en inglés si existe y está completa; si no, el idioma local. Anotar el idioma por asignatura.
- Si todas las asignaturas viven en un único PDF, usar `tipo_fuente: "pdf_compartido"` y registrar el rango de páginas de cada una.
- Comprobar antes de terminar: sin códigos duplicados, suma de ECTS coherente con el total del grado, y tres guías de muestra que de verdad abren.

## Fase 2 · Scraper (un agente por universidad)

Entrega `scraper_{slug}.py --sample N | --all [--codes ...]`, que convierte cada guía en Markdown limpio y la guarda con `write_markdown()`, declarando en `blocks_found` qué bloques ha localizado (`contents`, `learning_outcomes`, `assessment`, y además `bibliography` y `prerequisites` cuando existan).

- Empezar con una muestra de 5 asignaturas **variadas** (cursos distintos, una optativa, el TFG): las guías atípicas son las que rompen los selectores.
- El agente abre los Markdown de la muestra y los compara con la fuente. No basta con que el script no falle: hay que confirmar que no se ha perdido ni truncado ningún bloque y que las tablas de evaluación conservan sus porcentajes.
- Conservar la estructura (títulos, listas, tablas) y eliminar menús, pies y navegación.
- Solo cuando la muestra esté al 100 % se lanza `--all`. Si una guía concreta no tiene un bloque en origen, eso es un dato (se anota), no un fallo del scraper.

## Fase 3 · Extracción semántica (API externa)

`python semantic_parser.py --unis ... --dry-run` para ver el volumen, luego `--limit 5` para revisar la calidad y, con el visto bueno humano, el lote completo. Los Markdown no se procesan en el chat del agente.

## Fase 4 · Consolidación y control de calidad

`python orchestrator.py consolidate` reconstruye `db/ingenium_syllabi.db` y `reports/anomalias.md`. `python orchestrator.py status` regenera `status_dashboard.md`.

## Reglas de operación

- **Puntos de aprobación humana:** antes de `scrape --all` de cada universidad y antes de cualquier ejecución de la Fase 3 que no sea `--dry-run` (cuesta dinero).
- **Cortesía con los servidores:** solo `PoliteClient`. Sin inicios de sesión ni técnicas para saltarse bloqueos. Si robots.txt prohíbe las páginas necesarias o el servidor devuelve 403/429 de forma persistente, parar e informar.
- **Privacidad (RGPD):** las guías contienen nombres y contactos del profesorado. Los correos y teléfonos se eliminan de forma determinista al guardar el Markdown, antes de que nada salga hacia la API; los nombres los omite el extractor. No se guarda ningún dato personal en `structured_data/` ni en la base de datos.
- **Aislamiento:** cada agente escribe solo en la carpeta de su universidad.
- **Informe final de cada agente:** qué grado eligió, cuántas asignaturas, suma de ECTS, estrategia de fuente y, sobre todo, lo que no pudo verificar.

---

## Qué cambia respecto al prompt original y por qué

| Cambio | Motivo |
|---|---|
| Los agentes generan scripts; los datos nunca pasan por un LLM en las fases 1, 2 y 4 | Evita asignaturas o créditos inventados, hace el proceso reproducible cada curso y reduce mucho el consumo de tokens |
| Prioridad a fuentes estructuradas (API/JSON/PDF) sobre el DOM | Más rápido, más estable y menos peticiones al servidor |
| Caché en disco de todo lo descargado | Reparar un selector no obliga a volver a descargar; menos riesgo de bloqueo por IP |
| Respeto de robots.txt y parada ante bloqueos | El original solo pedía pausas; conviene además no insistir donde no se permite |
| Anonimización determinista **antes** de la API externa | En el original la hacía el LLM, es decir, los datos personales ya habían salido hacia un tercero |
| Caché por hash en la Fase 3, `--dry-run` y `--limit` | No se paga dos veces por la misma guía y se conoce el volumen antes de gastar |
| Salida estructurada validada con pydantic | Un JSON «estricto» pedido solo por prompt falla de vez en cuando; validado por esquema, no |
| Esquema ampliado: prerrequisitos, tipo de asignatura, idioma de impartición, métodos docentes, horas de trabajo, resultados de aprendizaje tipificados con su código original, código ISCED-F, `missing_sections` y trazabilidad (URL, hash, fecha, modelo) | Son los campos que usa un coordinador para decidir una convalidación, y la trazabilidad permite auditar cada dato |
| `weight_percentage` admite nulo | Muchas guías no dan porcentajes; forzar un número obliga a inventarlo |
| Muestra piloto variada y revisada contra la fuente | Cinco asignaturas parecidas dan un 100 % engañoso |
| Puntos de aprobación explícitos | El original pedía aprobación solo al principio; lo caro y lo masivo llega después |
| Medical University of Sofia tratada como probable N/A | Es una universidad de ciencias de la salud |
| El estado se deduce de los archivos, no de un registro que mantenga un agente | El panel no puede quedar desincronizado de la realidad |
