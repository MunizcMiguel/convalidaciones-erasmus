# Registro de plataformas de guías docentes

Una entrada por universidad ya resuelta. Antes de escribir un scraper nuevo, busca aquí si la plataforma de tu universidad ya está cubierta y parte de ese script. Al terminar, añade tu entrada al final (solo añadir; no edites las de otros).

Formato de cada entrada:

```
## {slug} — {universidad}
- Plataforma: ...
- Hosts: ... (veredicto de robots.txt)
- Patrón de URL de una guía: ...
- Tipo de fuente: API JSON | HTML | PDF por asignatura | PDF compartido
- Scraper de referencia: universidades/{slug}/scraper_{slug}.py
- Notas: ...
```

## uniovi — Universidad de Oviedo
- Plataforma: portal propio sobre Liferay (uniovi.es).
- Hosts: www.uniovi.es (robots.txt permite).
- Patrón de URL de una guía: `https://www.uniovi.es/estudia/grados/ingenieria/mecanica/-/fof/asignatura/{CODIGO}`; la guía se obtiene con dos peticiones más (asignaturaId → lista JSON → fragmento HTML).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/uniovi/scraper_uniovi.py
- Notas: la cookie de idioma de Liferay puede devolver la página en inglés; el scraper lo detecta y repite la petición.

## unich — Università di Chieti-Pescara (CINECA Course Catalogue)
- Plataforma: CINECA Course Catalogue (`*.coursecatalogue.cineca.it`), con API JSON pública detrás.
- Hosts: unich.coursecatalogue.cineca.it (sin robots.txt real; permite).
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/unich/scraper_unich.py
- Notas: útil si alguna universidad usa un catálogo de CINECA.

## hka / uoc / tuiasi — PDF compartido
- Tipo de fuente: un PDF (o uno por curso) con todas las fichas; el catálogo guarda el rango de páginas.
- Scrapers de referencia: universidades/hka/scraper_hka.py (PDF con texto), universidades/tuiasi/scraper_tuiasi.py (PDF que necesita OCR; solo Windows).

## es_politecnica_catalunya — Universitat Politècnica de Catalunya (EPSEVG)
- Plataforma: guías docentes UPC (PDF generado por PRISMA), enlazadas desde la ficha del grado en www.upc.edu (Plone/Genweb).
- Hosts: www.upc.edu — la ficha del grado está permitida, pero robots.txt tiene `Disallow: */content/*` y las guías viven en `/content/grau/guiadocent/` (BLOQUEADO; no se descargan). epsevg.upc.edu permite, pero solo enlaza a esas mismas guías.
- Patrón de URL de una guía: `https://www.upc.edu/content/grau/guiadocent/pdf/esp/{codigo}` (la ficha lo escribe `/content/../grau/guiadocent/pdf/esp/{codigo}/{slug}.pdf`, que redirige a la anterior).
- Tipo de fuente: PDF por asignatura (catálogo: HTML estático, `div#pla-estudis`).
- Scraper de referencia: ninguno (regla de parada); solo universidades/es_politecnica_catalunya/discover_es_politecnica_catalunya.py
- Notas: PoliteClient no detecta este bloqueo (robotparser sin comodines y no mira el destino de la redirección); el discover lo comprueba aparte. Vale para cualquier centro de la UPC (EPSEM, ESEIAAT, EEBE).

## es_carlos_iii_madrid — Universidad Carlos III de Madrid
- Plataforma: aplicación propia "cpa" (aplicaciones.uc3m.es), ficha HTML estática por asignatura.
- Hosts: www.uc3m.es (catálogo) y aplicaciones.uc3m.es (guías); PoliteClient no encontró bloqueo en robots.txt.
- Patrón de URL de una guía: `https://aplicaciones.uc3m.es/cpa/generaFicha?est={estudio}&plan={plan}&asig={codigo}&idioma=1` (1=castellano).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/es_carlos_iii_madrid/scraper_es_carlos_iii_madrid.py
- Notas: secciones `div.apartado` (panel-heading/panel-body). Reutilizable para otros grados UC3M cambiando est/plan.

## es_pais_vasco — Universidad del País Vasco / EHU
- Plataforma: portal Liferay de ehu.eus con contenido XSL de GAUR.
- Hosts: www.ehu.eus (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.ehu.eus/es/web/graduak/{slug-grado}/creditos-y-asignaturas?redirect=consultaAsignatura&anyo-academico=20260&ciclo=X&curso={n}&asignatura={codigo}`.
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/es_pais_vasco/scraper_es_pais_vasco.py
- Notas: la misma plantilla vale para cualquier grado de la EHU; la tabla "Docencia" (horas) se conserva, nombres de docentes se eliminan.

## es_zaragoza — Universidad de Zaragoza
- Plataforma: SIGMA DOA (sia.unizar.es) para las guías; estudios.unizar.es para el plan.
- Hosts: estudios.unizar.es y sia.unizar.es (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://sia.unizar.es/doa/consultaPublica/look[conpub]MostrarPubGuiaDocAs?entradaPublica=true&idiomaPais=es.ES&_anoAcademico=2026&_codAsignatura={codigo}`.
- Tipo de fuente: HTML (cp1252, pestañas Inglés/Castellano).
- Scraper de referencia: universidades/es_zaragoza/scraper_es_zaragoza.py
- Notas: apartados numerados de plantilla; algunas guías omiten el 2 (resultados de aprendizaje).

## es_politecnica_madrid — Universidad Politécnica de Madrid (ETSIDI)
- Plataforma: GAUSS (UPM) para las guías en PDF; API JSON `wapi_upm` para el plan.
- Hosts: www.upm.es (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.upm.es/comun_gauss/publico/guias/2026-27/GA_{plan}_{codigo}_ES_2026-27.pdf` (si no está publicada: `.../2025-26/2S/GA_{plan}_{codigo}_2S_2025-26.pdf`, formato antiguo).
- Tipo de fuente: PDF por asignatura (con texto).
- Scraper de referencia: universidades/es_politecnica_madrid/scraper_es_politecnica_madrid.py
- Notas: dos plantillas de PDF (nueva con encabezados en mayúsculas; antigua con secciones numeradas); ambas soportadas. Quitar el COORDINADOR/A de la cabecera y la sección Profesorado.

## es_politecnica_valencia — Universitat Politècnica de València (vía Florida Universitària)
- Plataforma: WordPress de Florida Universitària (centro adscrito) + PDFs de guías propios. El portal UPV (`www.upv.es/pls/…`, poliConsulta) está BLOQUEADO por robots.txt (`Disallow: /pls/`, `/policonsulta/c/`) y no se usa.
- Hosts: www.floridauniversitaria.es (Allow: /), guiasdocentes.floridauniversitaria.es (sin robots.txt).
- Patrón de URL de una guía: `https://guiasdocentes.floridauniversitaria.es/2627_{curso}GIM-{Nombre}.pdf` (el enlace exacto sale del POST `/wp-content/themes/florida/theme/ajax/ws_asignatura.php` con `id` de la fila del plan).
- Tipo de fuente: PDF por asignatura (con texto).
- Scraper de referencia: universidades/es_politecnica_valencia/scraper_es_politecnica_valencia.py
- Notas: sirve solo para Florida (no para ETSIADI/Alcoy, que dependen de www.upv.es). Algún enlace del portal da 404. Secciones numeradas, identificadas por título ES/EN.

## es_a_coruna — Universidade da Coruña (EPEF Ferrol)
- Plataforma: guiadocente.udc.es (GAIN, UDC) — no verificada.
- Hosts: guiadocente.udc.es inaccesible (ConnectTimeout desde esta red; robots.txt no leído). www.udc.es responde.
- Patrón de URL de una guía: no determinado.
- Tipo de fuente: desconocido. Catálogo `parcial`, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/es_a_coruna/discover_es_a_coruna.py, que documenta el fallo).
- Notas: reintentar desde otra red.

## es_almeria — Universidad de Almería (ESI)
- Plataforma: web del plan (Concrete5 + AngularJS) con API JSON propia; guías en PDF.
- Hosts: www.ual.es (robots.txt no veta `/guia_academica/` ni `/estudios/`) y campus.ual.es (API; sin robots.txt, 404).
- Patrón de URL de una guía: `https://www.ual.es/guia_academica/{cod_ass}/{curso}/CAS` (p. ej. 2026-27); catálogo: `https://campus.ual.es/ual/api/estudios/asignaturas/asignaturas/{idPlan}/es` (idPlan 2910 = Grado Ing. Mecánica).
- Tipo de fuente: PDF por asignatura (con texto; pdfplumber `x_tolerance=1.2`); catálogo por API JSON.
- Scraper de referencia: universidades/es_almeria/scraper_es_almeria.py
- Notas: sirve para cualquier grado de la UAL cambiando idPlan. Quitar PROFESOR/A, PROFESORADO y "Diversidad Funcional".

## es_burgos — Universidad de Burgos (EPS)
- Plataforma: web ubu.es (Drupal) con tablas por curso; guías PDF (TCPDF) servidas por el Moodle de la UBU (ubuvirtual).
- Hosts: www.ubu.es (robots.txt no veta las páginas del grado) y ubuvirtual.ubu.es (sin robots.txt).
- Patrón de URL de una guía: `https://ubuvirtual.ubu.es/mod/guiadocente/get_guiadocente.php?asignatura={codigo}&cursoacademico=2026`.
- Tipo de fuente: PDF por asignatura (con texto).
- Scraper de referencia: universidades/es_burgos/scraper_es_burgos.py
- Notas: apartados numerados cuya numeración varía entre guías → identificarlos por título. Bibliografía = enlace a Leganto.

## es_cadiz — Universidad de Cádiz (ESI)
- Plataforma: "Programas Docentes de Asignaturas" de la UCA (asignaturas.uca.es); catálogo en la web de la escuela (WordPress).
- Hosts: esingenieria.uca.es (robots solo veta /wp-admin/) y asignaturas.uca.es (sin robots.txt, 404).
- Patrón de URL de una guía: `https://asignaturas.uca.es/2026-27/{codigo}` (código de 8 dígitos).
- Tipo de fuente: HTML (ficha con un fieldset por apartado; requisitos en campos de formulario).
- Scraper de referencia: universidades/es_cadiz/scraper_es_cadiz.py
- Notas: sirve para cualquier titulación UCA (código = 2+4 dígitos del plan + 3 de asignatura). Algunas optativas sin programa publicado.

## es_extremadura — Universidad de Extremadura (EII Badajoz)
- Plataforma: WordPress de la escuela (eii.unex.es) con planes docentes en PDF.
- Hosts: eii.unex.es (robots.txt solo veta /wp-admin/).
- Patrón de URL de una guía: `https://eii.unex.es/wp-content/uploads/sites/8/{año}/{mes}/plan0818-{codigo}-2026-27.pdf` (se obtiene del enlace "Plan docente" de `https://eii.unex.es/titulaciones/0818/?subjectid={codigo}`).
- Tipo de fuente: PDF por asignatura (con texto; fuentes mal codificadas: `(cid:NN)` → chr(NN+29)).
- Scraper de referencia: universidades/es_extremadura/scraper_es_extremadura.py
- Notas: 6 de 52 PDF con codificación ilegible (necesitarían OCR). Vale para otros grados de la EII cambiando el id de titulación (0818 = Ing. Mecánica).

## es_jaen — Universidad de Jaén (EPS Jaén)
- Plataforma: web de la escuela (eps.ujaen.es) + catálogo de fichas docentes de uvirtual.ujaen.es (Universidad Virtual).
- Hosts: eps.ujaen.es y uvirtual.ujaen.es (sin veto en robots.txt para estas rutas; uvirtual sin robots.txt).
- Patrón de URL de una guía: `https://uvirtual.ujaen.es/pub/es/informacionacademica/catalogofichasdocentesasignaturas/p/2026-27/4/134A/{codigo}/es/2026-27-{codigo}_es.html` (4/134A = grado/título; devuelve un PDF aunque termine en .html).
- Tipo de fuente: PDF por asignatura (con texto).
- Scraper de referencia: universidades/es_jaen/scraper_es_jaen.py
- Notas: otros grados de la UJA cambian `134A` y el código; quitar la sección PROFESORADO (correos/teléfonos).

## es_laguna — Universidad de La Laguna (ESIT)
- Plataforma: Portal de Guías Docentes de la ULL (www.ull.es/apps/guias, Django).
- Hosts: www.ull.es (robots.txt restringe solo a bots con nombre y rutas con `?`; no afecta a rutas sin parámetros).
- Patrón de URL de una guía: `https://www.ull.es/apps/guias/guias/print_guide/{id}/` (PDF; el `id` sale de `/guias/view_guide/{id}/` en el listado del grado `.../guias/view_degree/{nombre del grado}/`, y cambia cada curso).
- Tipo de fuente: PDF por asignatura (con texto; la portada es la página 1).
- Scraper de referencia: universidades/es_laguna/scraper_es_laguna.py
- Notas: créditos/carácter solo en el PDF. Quitar el apartado 3 (Profesorado) y 11 (Cronograma). Vale para cualquier grado de la ULL.

## es_miguel_hernandez_elche — Universidad Miguel Hernández de Elche (EPS Elche)
- Plataforma: portal propio umh.es (plantillas JS "JsonML"); las fichas salen de un endpoint JSON.
- Hosts: www.umh.es (robots.txt solo veta bots con nombre; no afecta a `/get_dataJson.py`).
- Patrón de URL de una guía: `https://www.umh.es/get_dataJson.py?item=:asi_g_{codigo}_S1&frm=DEFAULT&lang=ES` (título: `item=:tit_g_143_S1`); página humana: `/contenido/Estudios/:asi_g_{codigo}_S1/datos_es.html` (vacía sin JS).
- Tipo de fuente: API JSON (respuesta `jsonArray["..."]={...}`).
- Scraper de referencia: universidades/es_miguel_hernandez_elche/scraper_es_miguel_hernandez_elche.py
- Notas: vale para cualquier titulación UMH cambiando el `item` del título. Campos `_x_*` con prefijos `~$`/`~f`/`~>`; quitar profesorado.

## es_politecnica_cartagena — Universidad Politécnica de Cartagena (ETSII)
- Plataforma: web de estudios estudios.upct.es (Laravel + Vue, API `POST /obtenerPlan`) + guías PDF de UXXI (campusvirtual.upct.es). 
- Hosts: estudios.upct.es (permite); campusvirtual.upct.es (BLOQUEADO por robots.txt) e industriales.upct.es (`/guia-docente/` y `/plan-de-estudios/` BLOQUEADOS).
- Patrón de URL de una guía: `https://campusvirtual.upct.es/uxxiportal/servlets/public/guiaDocenteServlet?anyAnyaca=2026-27&assCodnum={codigo}&idioma=es&modalidad=P` (no se descarga).
- Tipo de fuente: PDF por asignatura (catálogo: API JSON con CSRF).
- Scraper de referencia: ninguno (regla de parada); solo universidades/es_politecnica_cartagena/discover_es_politecnica_cartagena.py
- Notas: el discover sirve para cualquier grado UPCT cambiando `cod_estudio`.

## es_jaume_castellon — Universitat Jaume I de Castelló (ESTCE)
- Plataforma: SIA de la UJI (ujiapps.uji.es/sia, publicación pública, HTML).
- Hosts: ujiapps.uji.es (robots permite solo `/sia/`); e-ujier.uji.es (`/pls/` guía completa) BLOQUEADO; `/upo/` (cambio de idioma) bloqueado → solo catalán.
- Patrón de URL de una guía: `https://ujiapps.uji.es/sia/rest/publicacion/2026/estudio/{idEstudio}/asignatura/{COD}/{temario|metodologia|evaluacion|actividades|reqmatricula}` (222 = Grau Enginyeria Mecànica plan antiguo; 275 = plan 2026).
- Tipo de fuente: HTML (5 subpáginas por asignatura).
- Scraper de referencia: universidades/es_jaume_castellon/scraper_es_jaume_castellon.py
- Notas: vale para cualquier grado UJI cambiando el idEstudio; limpiar comentarios condicionales de Word.

## es_publica_navarra — Universidad Pública de Navarra (ETSIIIT)
- Plataforma: web unavarra.es (plan en HTML) + ficha DOA propia.
- Hosts: www.unavarra.es (robots.txt solo veta bots con nombre; permite estas rutas).
- Patrón de URL de una guía: `https://www.unavarra.es/ficha-asignaturaDOA?idioma=es&codAsig={codigo}` (sin parámetro de año: siempre el curso en vigor; si no hay oferta dice «No hay datos para esta asignatura…»).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/es_publica_navarra/scraper_es_publica_navarra.py
- Notas: secciones `h3`; quitar PROFESORADO de la cabecera; sirve para cualquier grado UPNA (código 3 dígitos plan + 3).

## es_rovira_virgili — Universitat Rovira i Virgili (ETSEQ)
- Plataforma: Guía docente URV (docnet, PHP).
- Hosts: guiadocent.urv.cat (sin veto en robots.txt); www.urv.cat (veta solo /frases y /crm).
- Patrón de URL de una guía: `https://guiadocent.urv.cat/docnet/guia_docent/index.php?centre=20&ensenyament=2022&assignatura={codigo}&idioma=cast` (+ `&fitxa_apartat=55..63` para cada apartado).
- Tipo de fuente: HTML (tablas anidadas; un apartado por página).
- Scraper de referencia: universidades/es_rovira_virgili/scraper_es_rovira_virgili.py
- Notas: centre=20 = ETSEQ; otras titulaciones URV cambian centre/ensenyament. Quitar coordinador/profesorado de la cabecera.

## es_rey_juan_carlos — Universidad Rey Juan Carlos (Móstoles)
- Plataforma: aplicación JSP «Guías Docentes» de la URJC; guías PDF (con texto).
- Hosts: servicios.urjc.es (sin veto; gestion3.urjc.es redirige aquí) y www.urjc.es (Crawl-delay 10).
- Patrón de URL de una guía: `POST https://servicios.urjc.es/guiasdocentes/pdfGuia.jsp` con `txtCursoAcademico=2026-27&txtTitulacion={2404|2286}&txtAsignatura={codigo}` (cookie de sesión de la portada; listado por POST `getAsignaturasAlumnoAjax.jsp?codPlan=..&alumno=1&cursoAcademico=..`).
- Tipo de fuente: PDF por asignatura.
- Scraper de referencia: universidades/es_rey_juan_carlos/scraper_es_rey_juan_carlos.py
- Notas: el mismo grado aparece partido en dos titulaciones (1º-2º y 3º-4º); PoliteClient cachea por URL, así que los POST necesitan `?a=codigo` para no colisionar; quitar marca de agua y apartado IX Profesorado.

## es_rioja — Universidad de La Rioja (ETSII)
- Plataforma: web unirioja.es (WordPress) + aplicación «GuiasDocentes» (servlet Java) en aps.unirioja.es.
- Hosts: www.unirioja.es y aps.unirioja.es (sin veto en robots.txt para estas rutas).
- Patrón de URL de una guía: `https://aps.unirioja.es/GuiasDocentes/servlet/agetguiahtml?2026-27,803G,{codigo}` (PDF: `agetguiapdf`; 803G = título).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/es_rioja/scraper_es_rioja.py
- Notas: vale para cualquier grado UR cambiando el código de título; quitar Profesorado previsto (correos/teléfonos).

## es_leon — Universidad de León (EIIIA)
- Plataforma: web unileon.es (Drupal) + visor de guías docentes propio (SPA Angular) con API JSON.
- Hosts: www.unileon.es, visor-guiadocente.unileon.es y guiadocenteapi.unileon.es (sin veto en robots.txt para estas rutas).
- Patrón de URL de una guía: `https://guiadocenteapi.unileon.es/snapshots/2026-2027/{codigo}` (código 7 dígitos 0708NNN); visor: `https://visor-guiadocente.unileon.es/snapshots/2026-2027/{codigo}`.
- Tipo de fuente: API JSON (elementos duplicados por idioma es/en).
- Scraper de referencia: universidades/es_leon/scraper_es_leon.py
- Notas: las guías de un plan nuevo solo existen para los cursos ya impartidos (3.º-4.º del Plan 2025 aún sin datos).

## es_malaga — Universidad de Málaga (Escuela de Ingenierías Industriales)
- Plataforma: web uma.es (Plone) + PDFs de guías del servidor «sara.uma.es».
- Hosts: www.uma.es (sin robots.txt; permite) y sara.uma.es (BLOQUEADO: robots.txt lo prohíbe).
- Patrón de URL de una guía: `https://sara.uma.es/ht/2026/ProgramasAsignaturas_Titulacion_5043_AsigUMA_{id}.pdf` (id de `/centers/subject/5043/{id}`; no se descarga).
- Tipo de fuente: PDF por asignatura (catálogo: HTML estático).
- Scraper de referencia: ninguno (regla de parada); solo universidades/es_malaga/discover_es_malaga.py
- Notas: vale para cualquier titulación UMA cambiando el código de título (5043 = Ing. Mecánica).

## es_salamanca — Universidad de Salamanca (E.P.S. de Zamora)
- Plataforma: guias.usal.es (Drupal, Guías académicas USAL).
- Hosts: guias.usal.es (sin veto en robots.txt para estas rutas).
- Patrón de URL de una guía: `https://guias.usal.es/node/{id}` (el nodo del título, p. ej. `/node/250991`, lista las asignaturas por curso en `ul.asignatura-curso`).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/es_salamanca/scraper_es_salamanca.py
- Notas: valido para cualquier titulación USAL; quitar «Datos del profesorado». Un mismo grado tiene un nodo por centro y por plan.

## es_alfonso_x_sabio — Universidad Alfonso X El Sabio (EIAD)
- Plataforma: PDF compartido en uax.com (`/download/8642/file/GMC_Guias_Docentes_plan_2020.pdf`).
- Hosts: www.uax.com (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: el mismo PDF; cada guía es un rango de páginas delimitado por portadas «GUÍA DE LA ASIGNATURA».
- Tipo de fuente: PDF compartido (con texto).
- Scraper de referencia: universidades/es_alfonso_x_sabio/scraper_es_alfonso_x_sabio.py
- Notas: otros grados UAX tienen su propio PDF `GXX_Guias_Docentes_plan_*.pdf`; quitar PROFESORES de la portada; códigos repetidos en el PDF.

## es_antonio_nebrija — Universidad Antonio de Nebrija (EPS)
- Plataforma: Gatsby/Griddo (www.nebrija.com); fichas en PDF bilingües.
- Hosts: www.nebrija.com (robots permite la ficha del grado y `/pdf/`; veta `/page-data/`).
- Patrón de URL de una guía: `https://www.nebrija.com/pdf/carreras-universitarias/grado-ingenieria-mecanica/pdf-asignaturas/{slug}.pdf`.
- Tipo de fuente: PDF por asignatura (con texto, ES/EN).
- Scraper de referencia: universidades/es_antonio_nebrija/scraper_es_antonio_nebrija.py
- Notas: el HTML estático solo trae el 1.º curso (resto por JS) → catálogo parcial; quitar «Profesor - Equipo docente».

## es_mondragon_unibertsitatea — Mondragon Unibertsitatea (EPS)
- Plataforma: mondragon.edu (Liferay) con PDF TCPDF por asignatura («Planificación de la asignatura»).
- Hosts: mondragon.edu / www.mondragon.edu (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.mondragon.edu/ikasketak/MGEP/M2GM-2500197/2017/{curso}/{CODIGO}-es.pdf` (la tabla del plan `…/grado-ingenieria-mecanica/plan-estudios/2017` los enlaza).
- Tipo de fuente: PDF por asignatura (con texto).
- Scraper de referencia: universidades/es_mondragon_unibertsitatea/scraper_es_mondragon_unibertsitatea.py
- Notas: ediciones de ficha antiguas (2019-20 en las vistas); quitar PROFESORES; apartados repetidos por resultado de aprendizaje.

## es_nacional_educacion_a_distanc — UNED (ETSI Industriales)
- Plataforma: portal uned.es con guías públicas en PDF generadas por la UNED.
- Hosts: www.uned.es (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.uned.es/universidad/pdf/GuiasAsignaturasGrados/PDFGuiaPublica?codigoAsignatura={cod}&curso=2027&codigoTitulacion=6803&language=es&esMaster=false` (la página HTML equivalente: `…/grado-en-ingenieria-mecanica/asignaturas.html?codTitulacion=6803&codAsignatura={cod}`).
- Tipo de fuente: PDF por asignatura (con texto).
- Scraper de referencia: universidades/es_nacional_educacion_a_distanc/scraper_es_nacional_educacion_a_distanc.py
- Notas: vale para cualquier grado UNED cambiando codTitulacion; quitar EQUIPO DOCENTE/HORARIO/TUTORIZACIÓN; la ficha mezcla Plan 2024 y 2009.

## es_navarra — Universidad de Navarra (Tecnun)
- Plataforma: unav.edu (Liferay) + «asignatura.unav.edu» (ficha por asignatura que se sirve como PDF).
- Hosts: www.unav.edu (permite); asignatura.unav.edu (sin robots.txt).
- Patrón de URL de una guía: `https://asignatura.unav.edu/{id}/` (devuelve un PDF «Guía docente 2026-27»); el id sale del plan `…/web/grado-en-ingenieria-mecanica/plan-de-estudios`.
- Tipo de fuente: PDF por asignatura (con texto), aunque la URL no acabe en .pdf.
- Scraper de referencia: universidades/es_navarra/scraper_es_navarra.py
- Notas: la guía es compartida por varios grados Tecnun: filtrar el bloque INGENIERÍA MECÁNICA de los resultados; quitar profesores y horarios de atención.

## es_catolica_santa_teresa_jesus_ — Universidad Católica de Ávila (UCAV)
- Plataforma: ucavila.es; plan de estudios en PDF (`/downloads/planes-Estudio/25-26/GIM.pdf`).
- Hosts: www.ucavila.es (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: no localizado (catálogo parcial, todo sin_guia).
- Tipo de fuente: desconocido; catálogo desde PDF de plan.
- Scraper de referencia: ninguno (solo universidades/es_catolica_santa_teresa_jesus_/discover_es_catolica_santa_teresa_jesus_.py)
- Notas: códigos NNNNNGT; ECTS cuadran con el RUCT.

## es_vigo — Universidade de Vigo (Escuela de Ingeniería Industrial)
- Plataforma: Docnet (secretaria.uvigo.gal/docnet-nuevo/guia_docent), ficha HTML con tablas anidadas; un apartado por subpágina.
- Hosts: secretaria.uvigo.gal (sin robots.txt, 404; permite).
- Patrón de URL de una guía: `https://secretaria.uvigo.gal/docnet-nuevo/guia_docent/?centre=312&ensenyament=V12G380V01&assignatura={codigo}&idioma=cast&any_academic=2026_27&idioma_assig=cast` (+ `&fitxa_apartat=1..9` para cada apartado; sin `idioma_assig` sale en gallego).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/es_vigo/scraper_es_vigo.py
- Notas: ~10 peticiones por asignatura; listado: `…&consulta=assignatures`; vale para cualquier título UVigo cambiando centre/ensenyament; quitar Coordinador/Correo-e/Profesorado del bloque identificativo.

## es_valladolid — Universidad de Valladolid (EII)
- Plataforma: guías PDF en apps.stic.uva.es (`/guias_docentes/uploads/{año}/455/{id}/1/Documento.pdf`).
- Hosts: apps.stic.uva.es e isa.eii.uva.es con certificado TLS inválido (BLOQUEADO a efectos prácticos: no se desactiva la verificación); www.uva.es permite.
- Patrón de URL de una guía: ver arriba (id de asignatura no derivable sin el listado).
- Tipo de fuente: PDF por asignatura. Catálogo parcial vacío; sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/es_valladolid/discover_es_valladolid.py).
- Notas: reintentar si corrigen el certificado.

## es_europea_madrid / es_francisco_vitoria / es_autonoma_barcelona / es_girona — sin fuente localizada
- Catálogo parcial vacío en cada una (ver `notas_descubrimiento.md`): UEM (título en extinción; PDF en universidadeuropea.com/myfiles/pr/{código}.pdf sin índice), UFV (solo folleto PDF), UAB (centro adscrito EUSS), UdG (fuente no localizada). Sin Fase 2. Scraper de referencia: ninguno (solo discover_{slug}.py).

## ec_d_ingolst01 — Technische Hochschule Ingolstadt (Maschinenbau B.Eng.)
- Plataforma: thi.de (TYPO3); Modulhandbuch por titulación en PDF (Word → PDF, con texto), uno compartido + otro de Wahlpflichtmodule (FW-Fächer).
- Hosts: www.thi.de (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.thi.de/fileadmin/daten/fakultaetM/Modulhandbuch/Bachelor_MB/MHBuch_MB_SPO_2023_24_Stand_{fecha}.pdf` (el enlace sale de la página del grado); rango de páginas por módulo.
- Tipo de fuente: PDF compartido.
- Scraper de referencia: universidades/ec_d_ingolst01/scraper_ec_d_ingolst01.py
- Notas: cada módulo empieza con "Modulkürzel:"; vale para otros Modulhandbücher de THI cambiando el PDF. Quitar Modulverantwortliche/Dozent.

## ec_i_parma01 — Università di Parma (Ingegneria Meccanica, L-9)
- Plataforma: portal de corsos `corsi.unipr.it` (ugov) + Excel "Offerta Formativa" publicado por la universidad.
- Hosts: corsi.unipr.it devuelve HTTP 405 a PoliteClient (BLOQUEADO a efectos prácticos; no se rodea). disti.unipr.it/www.unipr.it no usados.
- Patrón de URL de una guía: `https://corsi.unipr.it/en/ugov/degreecourse/{idInsegnamento}`.
- Tipo de fuente: HTML (fichas reutilizadas de una descarga previa del usuario; catálogo desde el Excel).
- Scraper de referencia: universidades/ec_i_parma01/scraper_ec_i_parma01.py (sin red; lee `fuente_previa/`).
- Notas: catálogo parcial (solo cursos ofertados 2025/26). El Excel mezcla CdS 3011/3111 (L-9) y 5016 (magistrale).

## ec_p_porto02 — Universidade do Porto (FEUP, Eng. Mecânica L.EM)
- Plataforma: SIGARRA (sigarra.up.pt/feup), fichas HTML por UC (versión PT/EN), detrás de Cloudflare.
- Hosts: sigarra.up.pt — robots.txt permite `*` (Content-Signal ai-train=no) pero la ficha da HTTP 403 a PoliteClient (BLOQUEADO; no se rodea).
- Patrón de URL de una guía: `https://sigarra.up.pt/feup/pt/ucurr_geral.ficha_uc_view?pv_ocorrencia_id={id}`.
- Tipo de fuente: HTML (fichas reutilizadas de una descarga previa del usuario).
- Scraper de referencia: universidades/ec_p_porto02/scraper_ec_p_porto02.py (sin red; lee `fuente_previa/`).
- Notas: el `Cycles of Study` de la ficha da el año por titulación (útil para otros cursos FEUP); la extracción previa perdió acentos en algunos textos.

## ec_ro_timisoa04 — Universitatea Politehnica Timișoara (Inginerie Mecanică)
- Plataforma: international.upt.ro (WordPress) con course catalogue Erasmus en Excel por facultad; fichas "Fișa disciplinei" en Word.
- Hosts: international.upt.ro (PoliteClient lo sirve; el enlace al Excel no está en el HTML estático).
- Patrón de URL de una guía: no hay URL por asignatura (catálogo único: `https://international.upt.ro/en/incoming-students/course-catalogue/`).
- Tipo de fuente: Excel + Word (reutilizados de una descarga previa del usuario).
- Scraper de referencia: universidades/ec_ro_timisoa04/scraper_ec_ro_timisoa04.py (sin red; lee `fuente_previa/`).
- Notas: códigos L431.AA.SS.xN (AA=cohorte, SS=semestre); mismo código en asignaturas distintas.

## ec_i_milano02 — Politecnico di Milano (Ingegneria Meccanica L-9)
- Plataforma: app "Manifesti degli Studi" (onlineservices.polimi.it, Java con sesión + AJAX) y schede insegnamento en www4.ceda.polimi.it.
- Hosts: www4.ceda.polimi.it robots.txt Disallow total → BLOQUEADO; www11.ceda.polimi.it no resuelve; onlineservices.polimi.it permite (Crawl-delay 5) pero sin tabla en el HTML; www.polimi.it / www.mecheng.polimi.it permiten.
- Patrón de URL de una guía: no accesible.
- Tipo de fuente: HTML (bloqueado). Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_i_milano02/discover_ec_i_milano02.py).
- Notas: el plan de estudios de la web de la escuela es una imagen.

## ec_i_bologna01 — Università di Bologna (Ingegneria meccanica L-9)
- Plataforma: corsi.unibo.it (plan didáctico, HTML estático) + www.unibo.it (ficha por insegnamento, Plone/portal propio, también en inglés).
- Hosts: corsi.unibo.it y www.unibo.it (robots.txt permite).
- Patrón de URL de una guía: https://www.unibo.it/en/study/course-units-transferable-skills-moocs/course-unit-catalogue/course-unit/{AAAA}/{idInterno} (IT: https://www.unibo.it/it/studiare/insegnamenti-competenze-trasversali-moocs/insegnamenti/insegnamento/{AAAA}/{idInterno}); el idInterno NO es el código del plan.
- Tipo de fuente: HTML (no enlazable desde el plan sin JS). Catálogo parcial con todas las filas sin_guia, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_i_bologna01/discover_ec_i_bologna01.py).
- Notas: la tabla del plan tiene td.code/td.title/td.info; las filas C.I. no tienen CFU.

## ec_d_hamburg03 — TU Hamburg (TUHH, Maschinenbau B.Sc.)
- Plataforma: studienplaene.tuhh.de (PHP propio) con Modulhandbuch por titulación y cohorte en PDF y HTML (DE/EN).
- Hosts: studienplaene.tuhh.de (robots permite); www.tuhh.de/robots.txt tiene Disallow: /robots.txt (PoliteClient lo marca bloqueado; las páginas de www.tuhh.de no se usan).
- Patrón de URL de una guía: https://studienplaene.tuhh.de/po/{COD}/mhb_{PROG}_kh_w{AA}_von_{AAAAMMDD}_v_0_en.html (un documento con todos los módulos; el enlace sale de index.php?stgart=B&stgB={PROG}&kid={cohorte}&Lang=en).
- Tipo de fuente: HTML compartido.
- Scraper de referencia: universidades/ec_d_hamburg03/scraper_ec_d_hamburg03.py
- Notas: sin temario/bibliografía ni semestre por módulo; tablas mHead/mContent; vale para otros programas TUHH cambiando stgB.

## ec_a_wien02 — TU Wien (Bachelor Maschinenbau)
- Plataforma: Studienpläne en PDF (tuwien.at/fileadmin, Typo3) con descripciones de módulo; guías por LVA en TISS (con login).
- Hosts: www.tuwien.at (robots permite /fileadmin/); tiss.tuwien.ac.at redirige a login en /course/ y su robots.txt se auto-veta (BLOQUEADO a efectos prácticos).
- Patrón de URL de una guía: https://www.tuwien.at/fileadmin/Assets/dienstleister/studienabteilung/BSc-Studienplaene_{AAAA}/Bachelorstudium_Maschinenbau_{AAAA}[_rev1].pdf (enlazado desde .../studienabteilung/studienplaene).
- Tipo de fuente: PDF compartido (nivel módulo).
- Scraper de referencia: universidades/ec_a_wien02/scraper_ec_a_wien02.py (+ wien_parse.py, reutilizable para otros Studienpläne TU Wien: 'Regelarbeitsaufwand' + 'Lehrveranstaltungen des Moduls').
- Notas: sin código oficial ni semestre; sin bibliografía.

## ec_d_berlin02 — TU Berlin (Maschinenbau B.Sc.)
- Plataforma: MOSES (moseskonto.tu-berlin.de, módulo transfer system), detrás de un handshake SSO Shibboleth con JavaScript.
- Hosts: www.tu.berlin permite; moseskonto.tu-berlin.de sin robots reales, pero solo sirve la página 'Web Login Service - Loading Session Information' sin JS (BLOQUEADO a efectos prácticos; no se usa navegador).
- Patrón de URL de una guía: `https://moseskonto.tu-berlin.de/moses/modultransfersystem/bolognamodule/beschreibung/anzeigen.html?number={n}&version={v}` (no accesible).
- Tipo de fuente: HTML (bloqueado). Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_d_berlin02/discover_ec_d_berlin02.py).
- Notas: la lista de módulos también está en el anexo de la StuPO 2017 (PDF static.tu.berlin), no analizado.

## ec_d_munchen02 — TU München (Maschinenwesen B.Sc.)
- Plataforma: TUMonline (campus.tum.de, SPA) para módulos; web tum.de (Typo3) con Studiengangsdokumentation en PDF.
- Hosts: www.tum.de permite (veta /typo3/ y /*/1000); campus.tum.de robots.txt `User-agent: * Disallow: /` → BLOQUEADO.
- Patrón de URL de una guía: no accesible (TUMonline).
- Tipo de fuente: HTML/SPA (bloqueado). Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_d_munchen02/discover_ec_d_munchen02.py).
- Notas: la Studiengangsdokumentation Teil A (PDF en tum.de/fileadmin) no contiene fichas de módulo.

## ec_d_karlsru05 — Hochschule Karlsruhe (Maschinenbau B.Eng.) — duplicado de `hka`
- Misma universidad y fuente que `hka` (Modulhandbuch MABB en PDF compartido, www.h-ka.de permite). Scripts copiados de hka con otro SLUG; 36 Markdown de 38 filas.
- Scraper de referencia: universidades/ec_d_karlsru05/scraper_ec_d_karlsru05.py

## ec_cz_brno01 — Brno University of Technology (FSI, Fundamentals of Mechanical Engineering B-STI-A)
- Plataforma: web de la facultad (fme.vutbr.cz, CMS propio del VUT) con ficha de programa y ficha de asignatura HTML.
- Hosts: www.fme.vutbr.cz (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.fme.vutbr.cz/en/studenti/predmety/{id}` (el id sale de los enlaces de `/en/studenti/programy/program/9646`).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_cz_brno01/scraper_ec_cz_brno01.py
- Notas: vale para otros grados de FSI/VUT cambiando el id del programa; sin bibliografía en las fichas; quitar Supervisor/Teacher.

## ec_d_paderbo01 — Universität Paderborn (Maschinenbau B.Sc.)
- Plataforma: web de la Fakultät für Maschinenbau (mb.uni-paderborn.de, TYPO3); Modulhandbuch en PDF (con texto) por titulación, un único PDF con todos los módulos.
- Hosts: mb.uni-paderborn.de (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://mb.uni-paderborn.de/fileadmin-mb/fakultaet/Studiengaenge/Modulhandbuecher/Modulhandbuecher_SoSe_26/Alte_POen/Ba_MB_SS26.pdf` (otros: `Neue_POen/Ba_NMB_V1_SS26.pdf`, etc.).
- Tipo de fuente: PDF compartido.
- Scraper de referencia: universidades/ec_d_paderbo01/scraper_ec_d_paderbo01.py
- Notas: `extract_text(x_tolerance=1.5)`; tabla "Modulnummer:" + apartados 1-13; quitar «12 Modulbeauftragte/r». Vale para otros Modulhandbücher de la misma facultad cambiando el PDF.

## ec_i_ancona01 — Università Politecnica delle Marche (Ingegneria Meccanica L-9)
- Plataforma: Cineca Course Catalogue (`univpm.coursecatalogue.cineca.it`), API JSON pública.
- Hosts: univpm.coursecatalogue.cineca.it (robots permite).
- Patrón de URL de una guía: `https://univpm.coursecatalogue.cineca.it/api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=..&af_percorso=..&corso_cod=..&corso_aa={coorte}`.
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_i_ancona01/scraper_ec_i_ancona01.py (plantilla Cineca reutilizable; HEAD_PATTERNS detecta bloques por título de sección).
- Notas: solo hay syllabus de A.A. 2026/27 → se combinan cohortes (2026 año 1, 2025 año 2, 2024 año 3; cds IT05 e IT25). Mismo discover valido para otros catálogos *.coursecatalogue.cineca.it cambiando host/cohortes.

## ec_i_bari05 — Politecnico di Bari (Ingegneria Meccanica L-9, LT31/LT31-R)
- Plataforma: Cineca Course Catalogue (`poliba.coursecatalogue.cineca.it`), API JSON pública.
- Hosts: poliba.coursecatalogue.cineca.it (robots permite).
- Patrón de URL de una guía: `https://poliba.coursecatalogue.cineca.it/api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=..&af_percorso=..&corso_cod=..&corso_aa={coorte}`.
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_i_bari05/scraper_ec_i_bari05.py
- Notas: Grado = Laurea in Ingegneria Meccanica (LT31 'D.M. 270/04' hasta la cohorte 2024; LT31-R 'L-9 R' desde 2025). ECTS 180; ofertados 171 (año 3 con solo 4 asignaturas con guía: tirocinio, prova finale, inglés y Meccanica razionale sin syllabus). Muchas fichas del año 1 (cursos de 'base' compartidos) son largas porque agregan varios grupos/docentes.

## ec_cz_praha10 — ČVUT Praga (Fac. de Ingeniería Mecánica, Bachelor of Mechanical Engineering)
- Plataforma: Bílá kniha (bilakniha.cvut.cz, HTML estático) con ficha por curso en inglés (sinopsis, temario, bibliografía).
- Hosts: bilakniha.cvut.cz (sin robots.txt; permite); www.fs.cvut.cz permite salvo /admin/, /login/…
- Patrón de URL de una guía: `https://bilakniha.cvut.cz/en/predmet{id}.html` (lista: `/en/f2-predmety.html`).
- Tipo de fuente: HTML. Catálogo parcial vacío: los planes de las especializaciones salen vacíos (y el archivo da 404), sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_cz_praha10/discover_ec_cz_praha10.py).
- Notas: si los planes aparecen, la ficha es trivial de convertir; otras facultades CVUT usan la misma Bílá kniha (`f{N}.html`).

## ec_i_cagliar01 — Università degli Studi di Cagliari (Ingegneria Meccanica e Gestionale L-9, 70/98 y 71/08)
- Plataforma: Cineca Course Catalogue (`unica.coursecatalogue.cineca.it`), API JSON pública.
- Hosts: unica.coursecatalogue.cineca.it (robots permite).
- Patrón de URL de una guía: `https://unica.coursecatalogue.cineca.it/api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=..&af_percorso=..&corso_cod=..&corso_aa={coorte}`.
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_i_cagliar01/scraper_ec_i_cagliar01.py
- Notas: UniCA no tiene grado puro de Mecánica: se usa Ingegneria Meccanica e Gestionale (currículos Meccanica y Gestionale, ambos incluidos). Catálogo PARCIAL: el endpoint /insegnamento devuelve 404 para el A.A. 2026/27 y para casi todas las fichas del A.A. 2025/26 de los años 1-2 (nueva ordinamento 2025, ficha no publicada); solo 12 de 32 asignaturas tienen syllabus (sobre todo año 3 y algunas de año 2). Ficha en inglés casi siempre. Una guía 404 se trata como sin_guia. Los códigos oficiales llevan '/', safe_name los convierte en '_'.

## ec_d_clausth01 — TU Clausthal (Maschinenbau B.Sc.)
- Plataforma: web de la Fakultät (fakultaeten.tu-clausthal.de, TYPO3) + Modulhandbuch PDF por titulación (plantilla con tablas numeradas 1a-31).
- Hosts: www.fakultaeten.tu-clausthal.de (PoliteClient no encontró bloqueo en robots.txt); studiengaenge.tu-clausthal.de sirve los mismos ficheros.
- Patrón de URL de una guía: `https://www.fakultaeten.tu-clausthal.de/fileadmin/Sites/Studiengaenge/Documents/Studiengaenge/Modulhandbuecher/Neu_in_2025-26/MHB_MB_B.Sc._13_06_2025.pdf` (otros grados: `MHB_*.pdf` en la misma carpeta).
- Tipo de fuente: PDF compartido (con texto).
- Scraper de referencia: universidades/ec_d_clausth01/scraper_ec_d_clausth01.py
- Notas: usar `find_tables()` + recorte por celda (no `extract_tables`); plantilla válida para todos los Modulhandbücher de la TU Clausthal. Sin código de módulo ni semestre.

## ec_cz_ostrava01 — VŠB-TU Ostrava (Fac. de Ingeniería Mecánica, catálogo ECTS Erasmus+)
- Plataforma: catálogo ECTS JSF de VŠB (www.vsb.cz/en/study/exchange-students/erasmus-plus/courses/{fs|...}/), HTML estático por facultad.
- Hosts: www.vsb.cz (robots.txt 404; permite); www.fs.vsb.cz permite salvo /akce/, /books/….
- Patrón de URL de una guía: `https://www.vsb.cz/en/study/exchange-students/erasmus-plus/courses/fs/?expandedSubjectId={id}&studyPlanId=-1&subjectBlockId={bloque}`.
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_cz_ostrava01/scraper_ec_cz_ostrava01.py
- Notas: no hay plan de grado, solo oferta Erasmus (catálogo parcial, filtrado a First Cycle); el scraper vale para otras facultades VŠB cambiando `/fs/`.

## ec_i_cosenza01 — Università della Calabria (Ingegneria Meccanica L-9, no verificada)
- Plataforma: Cineca Course Catalogue (`unical.coursecatalogue.cineca.it`) + API del portal (`storage.portale.unical.it/api/ricerca/cds/`, unicms).
- Hosts: unical.coursecatalogue.cineca.it BLOQUEADO por robots.txt; storage.portale.unical.it HTTP 403; www.unical.it permite pero la oferta formativa es JS.
- Patrón de URL de una guía: no accesible.
- Tipo de fuente: API JSON (bloqueada). Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_i_cosenza01/discover_ec_i_cosenza01.py).
- Notas: otros catálogos Cineca sí permiten (ver ec_i_ancona01); el veto es por universidad.

## ec_pl_elblag01 — ANS Elbląg (Mechanical Engineering / Mechanika i budowa maszyn)
- Plataforma: web Erasmus propia (study.ans-elblag.pl, HTML) con tabla de asignaturas en inglés y fichas Word; el plan completo está en USOSweb.
- Hosts: study.ans-elblag.pl (sin robots.txt; permite); ans-elblag.pl (permite); usosweb.ans-elblag.pl BLOQUEADO por robots.txt (no se usa).
- Patrón de URL de una guía: `https://study.ans-elblag.pl/assets/courses/ip/2025/{Nombre}.doc[x]` (el href relativo debe resolverse contra la raíz por el `<base>`; espacios → %20).
- Tipo de fuente: HTML (catálogo) + Word por asignatura.
- Scraper de referencia: universidades/ec_pl_elblag01/scraper_ec_pl_elblag01.py (python-docx para .docx, antiword para .doc)
- Notas: catálogo `parcial`: solo 8 asignaturas ofrecidas en inglés a Erasmus (32 ECTS); plantilla de ficha PWSZ con tablas (Learning outcome, Curriculum contents, Student workload).

## ec_d_bielefe02 — Hochschule Bielefeld, HSBI (Maschinenbau B.Eng.)
- Plataforma: hsbi.de (TYPO3/propio); SPO + Modulhandbuch en un PDF por titulación y versión (Anlage A = Studienplan, Anlage B = fichas).
- Hosts: www.hsbi.de (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.hsbi.de/media/hochschulverwaltung/dezernat-ii/studserv/pruefungsangelegenheiten/studiengangs-downloads/maschinenbau-(vollzeit-_-kooperativ)-bcn/...version-2025.pdf` (el enlace sale de `/studiengaenge/downloads/maschinenbau-bachelor`; las versiones antiguas dan 404).
- Tipo de fuente: PDF compartido (con texto).
- Scraper de referencia: universidades/ec_d_bielefe02/scraper_ec_d_bielefe02.py
- Notas: ficha = «Título KÜRZEL / Kennnummer:»; secciones 1-15; quitar «13 Modulbeauftragte/r». Plantilla común a otros grados de la HSBI.

## ec_hu_budapes02 — BME Budapest (GPK, BSc in Mechanical Engineering)
- Plataforma: xplore.bme.hu (WordPress, solo resumen); fichas de asignatura en www.gpk.bme.hu; Moodle edu.gpk.bme.hu y Neptun (login).
- Hosts: xplore.bme.hu y www.bme.hu permiten; www.gpk.bme.hu con certificado TLS inválido (BLOQUEADO a efectos prácticos); edu.gpk.bme.hu/Neptun requieren login.
- Patrón de URL de una guía: no accesible.
- Tipo de fuente: desconocido. Catálogo parcial vacío; sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_hu_budapes02/discover_ec_hu_budapes02.py).
- Notas: reintentar si arreglan el certificado de gpk.bme.hu.

## ec_i_firenze01 — Università degli Studi di Firenze (Ingegneria Meccanica L-9, B049/B309)
- Plataforma: Cineca Course Catalogue (`unifi.coursecatalogue.cineca.it`), API JSON pública.
- Hosts: unifi.coursecatalogue.cineca.it (robots permite).
- Patrón de URL de una guía: `https://unifi.coursecatalogue.cineca.it/api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=..&af_percorso=..&corso_cod=..&corso_aa={coorte}`.
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_i_firenze01/scraper_ec_i_firenze01.py
- Notas: Grado = Laurea in Ingegneria Meccanica (B049 hasta la cohorte 2024; B309 'L-9 R' desde 2025). Hay 6 currículos (Energia, Meccanico, Robotico e Automatico/Elettrico; formativo/applicativo): el catálogo es la unión y una asignatura presente en varios currículos con los mismos créditos se funde en una sola fila (la columna curso_semestre lista los currículos). Ofertado 390 ECTS sobre 180 del plan (cada currículo tiene su propio conjunto de optativas). El año 1 tiene pocas fichas publicadas (7 de 9). Mayoría de fichas en inglés. Se eliminan líneas 'Orario di ricevimento' y emails que aparecen en 'Altre informazioni'.

## ec_f_besanco01 — Université Marie et Louis Pasteur / Franche-Comté (Licence SPI Génie mécanique)
- Plataforma: catálogo ODF (Ametys) `formations.univ-fcomte.fr` (también usado por otras universidades francesas: plugins/odf-web).
- Hosts: formations.univ-fcomte.fr (robots permite; sitemap.xml con el árbol completo).
- Patrón de URL de una guía: `https://formations.univ-fcomte.fr/fr/index/formations/feuilleter-le-catalogue/licence-lmd-XA/.../{ELC}-{ID}.html` (el árbol sale de sitemap.xml); PDF por nodo: `/plugins/odf-web/odf/_content/{course|subprogram}-{slug}/…pdf`.
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_f_besanco01/scraper_ec_f_besanco01.py
- Notas: fichas casi siempre solo con ECTS/horas/MCC (sin temario) → catálogo parcial; mismo método vale para cualquier titulación ODF (sitemap + hojas).

## ec_i_salerno01 — Università degli Studi di Salerno (Ingegneria Meccanica L-9, 06123/II123)
- Plataforma: Cineca Course Catalogue (`unisa.coursecatalogue.cineca.it`), API JSON pública.
- Hosts: unisa.coursecatalogue.cineca.it (robots permite).
- Patrón de URL de una guía: `https://unisa.coursecatalogue.cineca.it/api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=..&af_percorso=..&corso_cod=..&corso_aa={coorte}`.
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_i_salerno01/scraper_ec_i_salerno01.py
- Notas: Grado = Laurea in Ingegneria Meccanica (06123 hasta la cohorte 2024; II123 'L-9 R' desde 2025). Códigos oficiales: II123xxxxx (plan nuevo, años 1-2) y 06123xxxxx/06126xxxxx (plan anterior, año 3). ECTS 180; ofertados 210 (el año 3 incluye optativas a elegir). Sin ficha: Statistica per l'ingegneria, Disegno, Ricerca operativa.

## ec_d_gelsenk02 — Westfälische Hochschule Gelsenkirchen (Maschinenbau B.Eng.)
- Plataforma: w-hs.de (TYPO3) con Modulhandbuch PDF por titulación en `fileadmin/Oeffentlich/Fachbereich-1/...` (enlaces sin `.pdf`); sistema antiguo winweb.w-hs.de (no accesible desde esta red).
- Hosts: www.w-hs.de (PoliteClient no encontró bloqueo en robots.txt); winweb.w-hs.de sin respuesta (timeout).
- Patrón de URL de una guía: `https://www.w-hs.de/fileadmin/Oeffentlich/Fachbereich-1/Studiengaenge/MB_BA/1A_ModulhandbuchBachelorMB_2024.11.15`.
- Tipo de fuente: PDF compartido (con texto). La edición 2026-10-01 trae los títulos como imagen.
- Scraper de referencia: universidades/ec_d_gelsenk02/scraper_ec_d_gelsenk02.py
- Notas: ficha «Kennnummer Workload Credits…» con apartados 1-12; quitar «11 Modulbeauftragter». Vale para otros handbooks del mismo Fachbereich.

## ec_f_besanco06 — SUPMICROTECH-ENSMM (Besançon, diplôme d'ingénieur)
- Plataforma: web Drupal de la escuela + «Programme de Formation» anual en PDF (con texto).
- Hosts: www.supmicrotech.fr (robots.txt permite; Crawl-delay 10).
- Patrón de URL de una guía: `https://www.supmicrotech.fr/sites/default/files/public/CONTENT/DOCUMENTS/programme_de_formation_initiale_2020-2021.pdf` (único PDF; módulo = cabecera `CODE : TITRE (Nh)`).
- Tipo de fuente: PDF compartido.
- Scraper de referencia: universidades/ec_f_besanco06/scraper_ec_f_besanco06.py
- Notas: 1.º-2.º año; 3.º (opciones) no catalogado; programa 2020-21. Quitar Responsable/Intervenants.

## ec_i_trento01 — Università degli Studi di Trento (Ingegneria industriale L-9, 0327G/0528G)
- Plataforma: Cineca Course Catalogue (`unitn.coursecatalogue.cineca.it`), API JSON pública.
- Hosts: unitn.coursecatalogue.cineca.it (robots permite).
- Patrón de URL de una guía: `https://unitn.coursecatalogue.cineca.it/api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=..&af_percorso=..&corso_cod=..&corso_aa={coorte}`.
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_i_trento01/scraper_ec_i_trento01.py
- Notas: UniTrento no tiene Ingegneria Meccanica triennale: se usa Ingegneria industriale (L-9) con sus tres currículos (Gestionale, Materiali per l'industria sostenibile, Robotica e meccatronica). Catálogo PARCIAL: ninguna asignatura del año 1 (cohorte 2026) tiene ficha publicada en el catálogo y varias del 2-3 tampoco (22 de 50 sin_guia: Fisica, Analisi, Disegno industriale, Sistemi meccanici e modelli, Tecnica delle costruzioni meccaniche...). Ya se eliminan líneas de horarios de tutoría y contactos.

## ec_d_osnabru02 — Hochschule Osnabrück (Maschinenbau B.Sc.)
- Plataforma: generador de Modulhandbücher de la HS Osnabrück (PDF por titulación en `www.hs-osnabrueck.de/fileadmin/Modulhandbuch/{COD}/`).
- Hosts: www.hs-osnabrueck.de (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.hs-osnabrueck.de/fileadmin/Modulhandbuch/BMB/StO2025_Stand2026-03-26_BSc_Maschinenbau.pdf` (BAF = Aircraft and Flight Eng., BME = Mechatronik, BMP = Maschinenbau im Praxisverbund, BVT = Energie-, Umwelt- und Verfahrenstechnik...).
- Tipo de fuente: PDF compartido (con texto).
- Scraper de referencia: universidades/ec_d_osnabru02/scraper_ec_d_osnabru02.py
- Notas: ficha «TÍTULO EN MAYÚSCULAS / Allgemeine Informationen zum Modul / Modulkennung»; quitar «Am Modul beteiligte Personen»; sin plan por semestres. Vale para cualquier titulación HSOS cambiando el PDF.

## ec_pl_radom01 — Casimir Pulaski Radom University / UTH Rad (Mechanical Engineering, inglés)
- Plataforma: WordPress de la Facultad de Mecánica (wm.uniwersytetradom.pl) con plan PDF y ZIP de syllabus PDF por titulación y modalidad en /programy-studiow/.
- Hosts: wm.uniwersytetradom.pl (robots.txt da 403, pero las páginas y /wp-content/uploads se sirven; sin bloqueo observado). uthrad.pl: TLS inválido (no usado).
- Patrón de URL de una guía: ZIP `https://wm.uniwersytetradom.pl/wp-content/uploads/sites/18/2025/05/Syllabusy-2025-2026-ME-I.zip`, miembro `Syllabusy/Full - time studies/{grupo}/{A3}_ME_O_I_ST.pdf` (catálogo: `url#miembro`).
- Tipo de fuente: PDF por asignatura dentro de un ZIP (con texto, maquetación a 2 columnas).
- Scraper de referencia: universidades/ec_pl_radom01/scraper_ec_pl_radom01.py
- Notas: otros grados de la facultad (Budownictwo, etc.) siguen el mismo patrón de plan+ZIP. Quitar Coordinator/correo.

## ec_f_dijon01 — Université de Bourgogne (Licence SPI parcours Mécanique)
- Plataforma: catálogo ODF (Ametys) `formations.ube.fr`, igual que ec_f_besanco01.
- Hosts: formations.ube.fr (robots permite, sitemap.xml); www.ube.fr (robots vacío).
- Patrón de URL de una guía: `https://formations.ube.fr/fr/offre-de-formation-2025-2026-2/licence-lmd-XA/licence-sciences-pour-l-ingenieur-LMGC20SA/mecanique-LMGEP01E/{ue}-{ID}.html` (salen del sitemap).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_f_dijon01/scraper_ec_f_dijon01.py
- Notas: fichas con ECTS/horas/MCC sin temario; solo L3 + 1 UE de L2 catalogadas.

## ec_pl_wroclaw02 — Politechnika Wrocławska (W10 Mechanical Engineering and Machine Building, I level)
- Plataforma: web de la facultad wm.pwr.edu.pl (CMS propio, `/fcp/…`) con un PDF de fichas por programa/nivel/forma de estudio; `syllabuskrk.pwr.edu.pl` no resuelve.
- Hosts: wm.pwr.edu.pl (robots veta solo /files/, /ajax/, ?i_cat; /fcp/ permitido).
- Patrón de URL de una guía: PDF compartido `…/w10/karty_kursow/{campo}_en_st_{i|ii}.pdf` (mbm = Mechanical Engineering and Machine Building, mech = Mechatronics, zip, mtr…).
- Tipo de fuente: PDF compartido (con texto), una "SUBJECT CARD" por rango de páginas.
- Scraper de referencia: universidades/ec_pl_wroclaw02/scraper_ec_pl_wroclaw02.py
- Notas: sin curso/semestre; varias fichas con campos vacíos en la fuente; quitar "SUBJECT SUPERVISOR". Vale para otros campos del W10 cambiando el PDF.

## ec_pl_rzeszow01 — Politechnika Rzeszowska (Inżynieria mechaniczna I stopnia)
- Plataforma: BIP de PRz (bip.prz.edu.pl) con el programa de estudios en PDF; dwm.prz.edu.pl solo Erasmus.
- Hosts: bip.prz.edu.pl (robots veta solo /files/ y /ajax/; /download/ permitido).
- Patrón de URL de una guía: no localizado (sin guías por asignatura públicas).
- Tipo de fuente: PDF compartido del plan (catálogo parcial, filas sin_guia).
- Scraper de referencia: ninguno (solo universidades/ec_pl_rzeszow01/discover_ec_pl_rzeszow01.py).
- Notas: URLs de /download/ llevan tokens largos; el plan tiene nombres partidos en varias líneas, parseo incompleto.

## ec_i_l_aquil01 — Università degli Studi dell'Aquila (Ingegneria industriale L-9, I3D/I3DR)
- Plataforma: Cineca Course Catalogue (`univaq.coursecatalogue.cineca.it`), API JSON pública.
- Hosts: univaq.coursecatalogue.cineca.it (robots permite).
- Patrón de URL de una guía: `https://univaq.coursecatalogue.cineca.it/api/v1/insegnamento?anno={aa}&insegnamento={cod}&ordinamento_aa=..&af_percorso=..&corso_cod=..&corso_aa={coorte}`.
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_i_l_aquil01/scraper_ec_i_l_aquil01.py
- Notas: UnivAQ solo ofrece Ingegneria Meccanica como magistrale (I4M); se usa el grado de primer ciclo Ingegneria industriale (I3D hasta la cohorte 2024; I3DR 'L-9 R' desde 2025), con varios currículos (Meccanica, Chimica, Gestionale, Elettrica, Biomedica...) fundidos en una unión; ofertado 501 ECTS sobre 180. Particularidad: esta ficha usa `altri_testi_ugov` (campos ugov_etichetta_*/ugov_altri_testi_*) para 'Learning outcomes' y 'Language'; el scraper (altri_testi) lo soporta. 12 filas sin_guia (Chimica, Fisica generale II, Meccanica applicata con laboratorio, Prova finale...).

## ec_f_grenobl22 — Grenoble (UGA, Licence Mécanique parcours GMP; Grenoble INP-UGA solo ofrece cycle ingénieur)
- Plataforma: catálogo ODF (Ametys) `formations.univ-grenoble-alpes.fr`.
- Hosts: formations.univ-grenoble-alpes.fr (robots permite; sitemap.xml); www.grenoble-inp.fr (robots permite, no usado).
- Patrón de URL de una guía: `https://formations.univ-grenoble-alpes.fr/fr/offre-de-formation/licence-XA/licence-mecanique-IAI546M7/{parcours}/ue-{slug}-{ID}.html`.
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_f_grenobl22/scraper_ec_f_grenobl22.py
- Notas: fichas ricas (Description, Compétences visées, Pré-requis, código Apogée); sin MCC. Ignorar el árbol `catalogue-2021`.

## ec_a_innsbru01 — Universität Innsbruck (Mechatronik B.Sc.; sin grado de Mecánica)
- Plataforma: uibk.ac.at (Django/filer); texto del Curriculum del grado en PDF (Mitteilungsblatt); fichas por LV en LFU:online (no usado).
- Hosts: www.uibk.ac.at (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.uibk.ac.at/media/filer_public/{xx}/{yy}/{uuid}/ba-mechatronik_stand-01102018.pdf` (enlace en `/de/studien/ba-mechatronik/2011w/`).
- Tipo de fuente: PDF compartido (con texto), descripción solo a nivel de módulo → catálogo `parcial`.
- Scraper de referencia: universidades/ec_a_innsbru01/scraper_ec_a_innsbru01.py
- Notas: § 7 «Pflicht- und Wahlmodule» (módulo, LV, Lernziele, Anmeldungsvoraussetzung); semestre desde «Empfohlener Studienverlauf». Sirve para otros curricula de Innsbruck con la misma plantilla.

## ec_sk_zilina01 — University of Žilina (Fac. de Ingeniería Mecánica)
- Plataforma: portal de formación vzdelavanie.uniza.sk (fichas y planes) + documentos de acreditación `OPIS-SPRAVA` en www.uniza.sk (HTML, fichas dentro).
- Hosts: vzdelavanie.uniza.sk BLOQUEADO (robots.txt `Disallow: /`); www.uniza.sk y fstroj.uniza.sk permiten.
- Patrón de URL de una guía: `https://www.uniza.sk/doc1/OPIS-SPRAVA/EN/{id}_OpisStudijnehoProgramu_EN.htm` (una página por programa; los ids probados eran doctorados).
- Tipo de fuente: HTML (descripción del programa con tabla de fichas). Catálogo parcial vacío; sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_sk_zilina01/discover_ec_sk_zilina01.py).
- Notas: si se localiza el id del grado en OPIS-SPRAVA, podría hacerse Fase 2 sin vzdelavanie.

## ec_f_nancy43 — Université de Lorraine (Licence SPI, orientación MGC)
- Plataforma: `formations.univ-lorraine.fr` (PrestaShop con contenido en pestañas JSON incrustado); sin guías por asignatura públicas localizadas.
- Hosts: formations.univ-lorraine.fr (robots permite salvo parámetros `?order=` etc.); formulconnect.univ-lorraine.fr (PDF de detalle → 404).
- Patrón de URL de una guía: no localizado.
- Tipo de fuente: desconocido. Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_f_nancy43/discover_ec_f_nancy43.py).
- Notas: la pestaña «Programme» solo tiene texto descriptivo; reintentar buscando el PDF de maquette de la FST.

## ec_a_graz09 — FH JOANNEUM Graz (Fahrzeugtechnik B.Sc.; sin grado de Mecánica)
- Plataforma: CMS propio de fh-joanneum.at (Alpine.js); página de Curriculum con acordeón por semestre y descripción breve por asignatura.
- Hosts: www.fh-joanneum.at (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.fh-joanneum.at/{grado}/bachelor/en/my-studies/curriculum/#course-{slug}` (misma página para todo el grado).
- Tipo de fuente: HTML (un documento por grado).
- Scraper de referencia: universidades/ec_a_graz09/scraper_ec_a_graz09.py
- Notas: `button.course-item` + `div#course-slug`; solo contenidos breves → catálogo `parcial`. Plantilla válida para otros grados FH JOANNEUM.

## ec_pl_sanok01 — Uczelnia Państwowa im. Jana Grodka w Sanoku (Mechanika i budowa maszyn)
- Plataforma: portal propio (up-sanok.edu.pl; ficheros bajo `/fcp/<token>/…/public/`).
- Hosts: up-sanok.edu.pl, instytut-techniczny.up-sanok.edu.pl, bip.up-sanok.edu.pl: todos cierran la conexión a PoliteClient (BLOQUEADO a efectos prácticos; no se rodea).
- Patrón de URL de una guía: no determinado.
- Tipo de fuente: desconocido (programa de estudios en PDF según búsqueda web). Catálogo `parcial` vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_pl_sanok01/discover_ec_pl_sanok01.py, que documenta el fallo).
- Notas: reintentar desde otra red.

## ec_s_lulea01 — Luleå University of Technology (Högskoleingenjör maskinteknik)
- Plataforma: ltu.se (Sitevision) con página de programa; ficha de curso en `/edu/course/{GRUPO}/{ID}?l=en`; kursplan como PDF dinámico de epok.ltu.se.
- Hosts: www.ltu.se permite; epok.ltu.se (`/epok/dynpdf/public/kursplan/`) BLOQUEADO por robots.txt.
- Patrón de URL de una guía: `https://epok.ltu.se/epok/dynpdf/public/kursplan/downloadPublicKursplan.pdf?kursKod={ID}&lasPeriod={n}&locale=en` (no se descarga).
- Tipo de fuente: PDF por asignatura (bloqueado). Catálogo parcial sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_s_lulea01/discover_ec_s_lulea01.py).
- Notas: la web de syllabuses `/en/education/syllabuses/course-syllabus?id={ID}` carga el contenido de epok; vale para cualquier programa LTU.

## ec_f_nantes07 — École Centrale de Nantes (ingénieur spécialité Mécanique)
- Plataforma: web ec-nantes.fr (CMS propio) con «Programme ingénieur» por año en PDF (con texto).
- Hosts: www.ec-nantes.fr (robots permite salvo /adminsite/, /action/*).
- Patrón de URL de una guía: `https://www.ec-nantes.fr/ingenieur-de-specialite/mecanique/syllabus-ei{1|2|3}-spe-meca` (PDF; ficha por curso en un rango de páginas).
- Tipo de fuente: PDF compartido (uno por año).
- Scraper de referencia: universidades/ec_f_nantes07/scraper_ec_f_nantes07.py
- Notas: solo cycle ingénieur; ECTS por UE; otras especialidades de Centrale Nantes usan `syllabus-ei{n}-spe-{x}` (no verificado).

## ec_uk_liverpo02 — Liverpool John Moores University (Mechanical Engineering BEng Hons)
- Plataforma: ljmu.ac.uk (portal de cursos + «module details») y prodcat.ljmu.ac.uk (Programme Specifications en PDF).
- Hosts: www.ljmu.ac.uk y cm-prod.ljmu.ac.uk BLOQUEADOS (RobotsBlocked, robots.txt tratado como deny-all); prodcat.ljmu.ac.uk permite pero solo contiene specs de programa.
- Patrón de URL de una guía: `https://prodcat.ljmu.ac.uk/KIS/{programa}-{id}.pdf` (programa; no hay ficha por módulo localizada).
- Tipo de fuente: PDF de programa (catálogo); fichas de módulo no accesibles → todo `sin_guia`.
- Scraper de referencia: ninguno (solo universidades/ec_uk_liverpo02/discover_ec_uk_liverpo02.py).
- Notas: créditos UK/2 ≈ ECTS; tabla «Level 4/5/6 Core|Option» leída con `find_tables()` y recorte por celda.

## ec_s_jonkopi01 — Jönköping University (School of Engineering)
- Plataforma: ju.se (Sitevision); páginas de curso `/en/study-at-ju/courses/programme-course/{slug}-{semestre}-{id}.html`; oferta de intercambio por facultad.
- Hosts: ju.se (robots solo veta rutas con parámetros de sesión/impresión).
- Patrón de URL de una guía: `https://ju.se/en/study-at-ju/courses/programme-course/{nombre}-{semestre}-{id}.html` (no explorado en detalle).
- Tipo de fuente: HTML (no verificado). Catálogo parcial vacío: sin grado en inglés de Ing. Mecánica; sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_s_jonkopi01/discover_ec_s_jonkopi01.py).
- Notas: grados en inglés del JTH: New Media Design y Sustainable Supply Chain Management.

## ec_i_perugia01 — Università degli Studi di Perugia (Ingegneria Meccanica L-9)
- Plataforma: portal de oferta formativa de www.unipg.it (Joomla), fichas HTML con tabla th/td por insegnamento. El catálogo Cineca (unipg.coursecatalogue.cineca.it) está vetado por robots.txt.
- Hosts: www.unipg.it (robots permite /didattica/); ing.unipg.it (permite); unipg.coursecatalogue.cineca.it BLOQUEADO.
- Patrón de URL de una guía: `https://www.unipg.it/didattica/corsi-di-laurea-e-laurea-magistrale/archivio/offerta-formativa-2025-26?view=elenco&ricerca=on&annoregolamento=2025&dipartimento=516600&sede=4&idcorso=8439&tab=INS&idins={idins}` (listado con `tab=INS` sin idins).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_i_perugia01/scraper_ec_i_perugia01.py
- Notas: idcorso 8439 = Ingegneria meccanica L-9; cursos integrados = varias tablas con encabezado de módulo; quitar Docente/Docenti/Ore.

## ec_ro_petrosa01 — Universitatea din Petroșani (Tehnologia construcțiilor de mașini)
- Plataforma: www.upet.ro (WordPress) con planes de învățământ en PDF; fichas de disciplina en carpetas SharePoint.
- Hosts: www.upet.ro (robots permite estas rutas); upet-my.sharepoint.com BLOQUEADO por robots.txt (no se usa).
- Patrón de URL de una guía: no accesible (carpetas SharePoint `…/:f:/g/personal/site_upet_ro/…`).
- Tipo de fuente: PDF (plan, tablas por año) + SharePoint (bloqueado). Catálogo `parcial` con todas las filas sin_guia, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_ro_petrosa01/discover_ec_ro_petrosa01.py; sirve para otros planes `…/documente/planuri/{facultad}/{año}/{SIGLA}.pdf`).
- Notas: el plan trae códigos oficiales y créditos por semestre; rumano.

## ec_uk_glasgow02 — University of Strathclyde (Mechanical & Aerospace Engineering, BEng Hons Mechanical Engineering)
- Plataforma: web strath.ac.uk (regulaciones académicas en PDF) + Module Description Forms en PDF del departamento.
- Hosts: www.strath.ac.uk (robots.txt sin reglas relevantes).
- Patrón de URL de una guía: `https://www.strath.ac.uk/media/departments/mechanicalengineering/mdf/{codigo}.pdf`; plan: `…/academicregulations26x2f27/engineeringug/2026-27_Mechanical_Engineering.pdf`.
- Tipo de fuente: PDF por asignatura (con texto). 13 de 30 MDF devuelven «Page not authorised» (HTML con HTTP 200) → sin_guia.
- Scraper de referencia: universidades/ec_uk_glasgow02/scraper_ec_uk_glasgow02.py
- Notas: créditos SCQF/2 = ECTS; vale para otros grados Strathclyde cambiando el PDF de regulaciones y la carpeta mdf del departamento; quitar Module Registrar y Lecturers.

## ec_p_lisboa109 — Universidade de Lisboa (IST, Engenharia Mecânica LEMec21)
- Plataforma: Fénix (IST), HTML del currículo + API REST pública `/api/fenix/v1`.
- Hosts: fenix.tecnico.ulisboa.pt (sin robots.txt, 404; permite). www.ulisboa.pt (Crawl-delay 10) no usado.
- Patrón de URL de una guía: `https://fenix.tecnico.ulisboa.pt/api/fenix/v1/courses/{id}` (id sale de `/degrees/{degreeId}/courses?academicTerm=2025/2026`; web: `/disciplinas/{acrónimo}/2025-2026/{n}-semestre`).
- Tipo de fuente: API JSON.
- Scraper de referencia: universidades/ec_p_lisboa109/scraper_ec_p_lisboa109.py
- Notas: sirve para cualquier grado del IST cambiando degreeId (lista en `/degrees?academicTerm=`). La API solo trae programa, bibliografía y método de evaluación; no objetivos ni requisitos. Estructura año/semestre solo en el HTML del currículo.

## ec_tr_ankara02 — Gazi University (Ankara, Mechanical Engineering (Eng))
- Plataforma: OBS «Bologna Bilgi Paketi» de Proliz (ASP.NET) en obs.gazi.edu.tr/oibs/bologna/ — la misma plataforma de otras universidades turcas (ver ec_tr_*).
- Hosts: obs.gazi.edu.tr (sin robots.txt, 404; permite); www.gazi.edu.tr permite.
- Patrón de URL de una guía: `https://obs.gazi.edu.tr/oibs/bologna/progCourseDetails.aspx?curCourse={id}&lang=en`; el id sale de `prolizOpenCourseDetails(id)` en `progCourses.aspx?lang=en&curSunit={ID}` (lista de programas: `unitSelection.aspx?type=lis&lang=en`).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_tr_ankara02/scraper_ec_tr_ankara02.py (+ discover; plantilla OBS/Proliz reutilizable cambiando BASE y curSunit).
- Notas: GET sin postback; plan por defecto = último currículo; quitar Course Coordinator / Name of Lecturers / Assistants.

## ec_f_tarbes03 — ENIT (Tarbes, Titre d'ingénieur)
- Plataforma: web enit.fr (Ametys) + PDF «Syllabus Titre d'Ingénieur» por semestre (con texto, bilingües FR/EN, texto rotado invertido).
- Hosts: www.enit.fr (robots solo veta /fr/index/remise-des-diplomes).
- Patrón de URL de una guía: `https://www.enit.fr/_attachment/nouvel-article-75/IGENI-{L3-S05|L3-S06|M-S07..S10}.pdf?download=true` (un PDF por semestre; ficha por EC/UE en un rango de páginas, `Code EC IGENI-ECxxxx`).
- Tipo de fuente: PDF compartido.
- Scraper de referencia: universidades/ec_f_tarbes03/scraper_ec_f_tarbes03.py
- Notas: `x_tolerance=1.0`; quitar profesores/coordinador; etiquetas rotadas invertidas; vale para los PDF C1/ALM cambiando el nombre.

## ec_bg_rousse01 — University of Ruse «Angel Kanchev» (CAD in Mechanical and Instrument Engineering, B.Sc.; sin grado «Mechanical Engineering»)
- Plataforma: www.uni-ruse.bg con «ECTS packages» por facultad en PDF (inglés); subdominios por facultad antiguos (cdo, fbm) caducados.
- Hosts: www.uni-ruse.bg (PoliteClient no encontró bloqueo en robots.txt).
- Patrón de URL de una guía: `https://www.uni-ruse.bg/en/education/students/ECTS%20packages/Faculty%20of%20Mechanical%20and%20Manufacturing%20Engineering.pdf` (un PDF por facultad; índice `/en/education/students/ECTS-package`).
- Tipo de fuente: PDF compartido (con texto).
- Scraper de referencia: universidades/ec_bg_rousse01/scraper_ec_bg_rousse01.py
- Notas: curriculum por términos (geometría de palabras) + descripciones «CÓDIGO Título / ECTS credits…»; quitar «Lecturers». Vale para las otras facultades de Ruse cambiando el PDF.

## ec_tr_bartin01 — Bartın Üniversitesi (Makine Mühendisliği)
- Plataforma: plan en PDF (cdn.bartin.edu.tr) + Bologna Bilgi Paketi en UBYS (ubys.bartin.edu.tr/AIS/OutcomeBasedLearning, ASP.NET MVC + SPA JS con endpoints AJAX POST e ids cifrados).
- Hosts: makine.bartin.edu.tr y cdn.bartin.edu.tr (sin restricción); ubys.bartin.edu.tr (robots solo veta /ECM/…, pero el contenido es SPA JS: no accesible con PoliteClient GET → BLOQUEADO a efectos prácticos); bubp.bartin.edu.tr (solo información institucional).
- Patrón de URL de una guía: no determinado (ids cifrados).
- Tipo de fuente: PDF (plan) + SPA (fichas). Catálogo `parcial` (45 filas sin_guia desde el PDF), sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_tr_bartin01/discover_ec_tr_bartin01.py; el parser del PDF de plan de dos columnas sirve para otros planes de Bartın).
- Notas: PDF «Ders Planı Örneği» FRM-0115 (Z/S T U K AKTS) común a todas las facultades de Bartın.

## ec_p_arcozel01 — Instituto Politécnico do Cávado e do Ave (IPCA)
- Plataforma: no determinada (www.ipca.pt inaccesible).
- Hosts: www.ipca.pt / ipca.pt — certificado TLS no verificable (CERTIFICATE_VERIFY_FAILED: unable to get local issuer certificate) → BLOQUEADO a efectos prácticos; robots.txt no leído.
- Patrón de URL de una guía: no determinado.
- Tipo de fuente: desconocido. Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_p_arcozel01/discover_ec_p_arcozel01.py).
- Notas: reintentar más adelante o desde otra red/almacén de certificados.

## ec_p_coimbra02 — Instituto Politécnico de Coimbra (ISEC, Eng. Mecânica)
- Plataforma: no determinada (isec.pt inaccesible).
- Hosts: www.isec.pt devuelve HTTP 400 a PoliteClient (BLOQUEADO a efectos prácticos; no se rodea); www.ipc.pt robots permite pero sin planes ni fichas.
- Patrón de URL de una guía: no determinado.
- Tipo de fuente: desconocido. Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_p_coimbra02/discover_ec_p_coimbra02.py).
- Notas: reintentar más adelante.

## ec_tr_duzce01 — Düzce Üniversitesi (Makine Mühendisliği)
- Plataforma: Eğitim Bilgi Sistemi propio (ebs.duzce.edu.tr, ASP.NET MVC), HTML servido por GET (Bootstrap, una tarjeta por apartado).
- Hosts: ebs.duzce.edu.tr (sin robots.txt, 404; permite). obs.duzce.edu.tr no sirve el módulo Bologna.
- Patrón de URL de una guía: `https://ebs.duzce.edu.tr/Ders/Index/{id}?bno=16&bot=18&yilNo=33` (plan: `/Bolum/OgretimProgrami/16?bot=18`; lista de grados `/Program/Index/2`).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_tr_duzce01/scraper_ec_tr_duzce01.py
- Notas: vale para otros programas de Düzce cambiando bölüm/bot; los pools de optativas se repiten por semestre; quitar Dersin Koordinatörü, Dersi Veren(ler) y la columna Sorumlu Personel; la UI inglesa exige cookie (no usar con la caché por URL).

## ec_p_lisboa03 — Universidade NOVA de Lisboa (FCT NOVA, Lic. Eng. Mecânica)
- Plataforma: Guia Académico NOVA (`guia.unl.pt`, ruta `/pt/2026/fct/program/1273`), enlazado desde la ficha del curso en www.fct.unl.pt.
- Hosts: www.fct.unl.pt (robots permite la ficha); guia.unl.pt y www.unl.pt con certificado TLS no verificable (CERTIFICATE_VERIFY_FAILED) → BLOQUEADO; no se desactiva la verificación.
- Patrón de URL de una guía: `https://guia.unl.pt/pt/2026/fct/program/1273` (plan; fichas de UC bajo `/course/{id}`, no verificado).
- Tipo de fuente: HTML (bloqueado). Catálogo parcial vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_p_lisboa03/discover_ec_p_lisboa03.py).
- Notas: mismo fallo de cadena de certificados que IPCA; reintentar desde otra red.

## ec_tr_konya05 — Konya Teknik Üniversitesi (Makine Mühendisliği)
- Plataforma: web de la facultad (www.ktun.edu.tr, /Dosyalar/1027/files/…) con plan por curso y «Ders İçerikleri» del departamento en PDF; el OBS (obs.ktun.edu.tr) no expone Bologna por GET.
- Hosts: www.ktun.edu.tr (robots.txt 404; permite).
- Patrón de URL de una guía: no hay ficha por asignatura; PDF compartido `…/Dosyalar/1027/files/KTUN_Makine_Muh__Bolumu_Ders_icerikleri_26_06_2020.pdf` con bloques «Dersin Adı» (emparejados con el plan por código NÖ).
- Tipo de fuente: PDF compartido (con texto; versión 2019/2020, anterior al plan 2024-25).
- Scraper de referencia: universidades/ec_tr_konya05/scraper_ec_tr_konya05.py
- Notas: 68 de 87 filas con bloque; sin resultados de aprendizaje/evaluación. El hint eurep.auth.gr es de otra universidad.

## ec_tr_kutahya01 — Kütahya Dumlupınar Üniversitesi (Makine Mühendisliği, Simav Teknoloji Fak.)
- Plataforma: no determinada (portal dpu.edu.tr; PDF de departamento en birimler.dpu.edu.tr según búsqueda web).
- Hosts: todos los de dpu.edu.tr rechazan la conexión (WinError 10061) / timeout / DNS desde esta red → BLOQUEADO a efectos prácticos.
- Patrón de URL de una guía: no determinado.
- Tipo de fuente: desconocido. Catálogo `parcial` vacío, sin Fase 2.
- Scraper de referencia: ninguno (solo universidades/ec_tr_kutahya01/discover_ec_tr_kutahya01.py, que documenta el fallo).
- Notas: reintentar desde otra red.

## ec_tr_sakarya01 — Sakarya Üniversitesi (Makine Mühendisliği)
- Plataforma: Eğitim Bilgi Sistemi propio (ebs.sakarya.edu.tr, ASP.NET MVC), HTML servido por GET.
- Hosts: ebs.sakarya.edu.tr (sin restricción observada); www.sakarya.edu.tr cierra la conexión a PoliteClient (no usado); obs./bologna. no resuelven.
- Patrón de URL de una guía: `https://ebs.sakarya.edu.tr/Ders/Detay/{id}` (plan por programa: `/Birim/DersPlan/{unidad}`; 290 = Makine Mühendisliği).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_tr_sakarya01/scraper_ec_tr_sakarya01.py
- Notas: vale para cualquier programa de Sakarya cambiando la unidad; tablas con ids `Ders-*`; quitar Dersin Koordinatörü/Dersi Verenler/Yardımcıları.

## ec_tr_zonguld01 — Zonguldak Bülent Ecevit Üniversitesi (Mechanical Engineering)
- Plataforma: OBS «Öğrenci Bilgi Paketi» de Proliz (obs.beun.edu.tr/oibs/bologna/), idéntica a la de Gazi (ec_tr_ankara02).
- Hosts: obs.beun.edu.tr (sin robots.txt, 404; permite); erasmus.beun.edu.tr y www.beun.edu.tr permiten.
- Patrón de URL de una guía: `https://obs.beun.edu.tr/oibs/bologna/progCourseDetails.aspx?curCourse={id}&lang=en` (plan: `progCourses.aspx?lang=en&curSunit=38`).
- Tipo de fuente: HTML.
- Scraper de referencia: universidades/ec_tr_zonguld01/scraper_ec_tr_zonguld01.py (copia de ec_tr_ankara02 con otro slug).
- Notas: el plan suma 227 ECTS en las tablas de semestre; títulos en inglés aunque la docencia es en turco.

## uniovi_giti / uniovi_gieia / uniovi_gie / uniovi_giqi / uniovi_gioi — Universidad de Oviedo (otros 5 grados de la EPI Gijón)
- Plataforma: SIES de uniovi.es (Liferay, portlet UnioviSiesWeb), idéntica a `uniovi` (Mecánica); ver universidades/uniovi/notas_descubrimiento.md.
- Hosts: www.uniovi.es (robots.txt solo veta /login, /group/, /web/guest/; permitido).
- Fichas: `https://www.uniovi.es/estudia/grados/ingenieria/{tecnologiasindustriales|electronicaindustrial|electrica|quimicaindustrial|organizacionindustrial}`; el código de plan (GITECI01, GIORGI01…) sale del href, no se escribe a mano.
- Tipo de fuente: HTML. Scripts de referencia: universidades/uniovi_{giti,gieia,gie,giqi,gioi}/{discover,scraper}_*.py (copias de uniovi con otro slug/URL; la muestra --sample se deriva del catálogo).
- Notas: algunas optativas de 4.º no tienen guía publicada en el curso vigente (el scraper las reporta como FALLO «sin guías docentes publicadas»); profesorado y coordinación excluidos.

## Segunda pasada ERASMUS (conv-t7, 2026-11)
- **ec_tr_kutahya01** — RESUELTA: OBS Bologna/Proliz (obs.dpu.edu.tr/oibs/bologna/, igual que Gazi/Zonguldak; plan `progCourses.aspx?lang=en&curSunit=90906313`, ficha `progCourseDetails.aspx?curCourse={id}&lang=en`). 96 filas/96 Markdown. Antes fallaba por red transitoria. El PDF de birimler.dpu.edu.tr está en /app/views/panel/ckfinder/ (robots lo veta).
- **ec_cz_praha10** — ČVUT Bílá kniha (bilakniha.cvut.cz/en/, sin robots): planes vacíos; se usa la oferta English de f2 (`f2-predmety.html` → `predmet{id}.html`, bloques `dl dt/dd`: Synopsis, Syllabus, Study Objective, Study materials, Requirements). Catálogo = cursos English con ficha no vacía; sin nivel grado/máster.
- **ec_i_cagliar01 / ec_i_trento01** — Cineca: si el `insegnamento` del A.A. objetivo da 404, probar el mismo curso con `anno` anterior (el endpoint a veces sí tiene la ficha); se anota el A.A. real en el Markdown («Anno accademico di erogazione»).
- **ec_i_bologna01** — sigue bloqueada: dati.unibo.it vetado por robots, el sitemap no trae fichas, el id interno de la ficha no sale en HTML estático.
- **ec_i_milano02** (fichas solo en www4.ceda.polimi.it, robots Disallow; dati/didattica.polimi.it sin DNS), **ec_f_belfort06** (guideuv.utbm.fr sin DNS), **ec_p_coimbra02** (isec.pt HTTP 400 persistente), **ec_pl_rzeszow01** (karty en /files/, vetado) — descartadas.

## uniovi_mii — Universidad de Oviedo (Máster Universitario en Ingeniería Industrial, EPI Gijón)
- Plataforma: SIES de uniovi.es (Liferay, portlet UnioviSiesWeb), igual que los grados `uniovi*`; ver universidades/uniovi/notas_descubrimiento.md.
- Hosts: www.uniovi.es (robots.txt solo veta /login, /group/, /web/guest/; permitido).
- Ficha: `https://www.uniovi.es/estudia/masteres/ingenieriayarquitectura/industrial` (los másteres cuelgan de `/estudia/masteres/{ingenieriayarquitectura|ciencias|...}/{slug}`); asignatura `.../-/fof/asignatura/MINGIND2-{curso}-{nnn}`.
- Tipo de fuente: HTML. Scripts: universidades/uniovi_mii/{discover,scraper}_uniovi_mii.py (copia de uniovi_giti).
- Notas: 62 asignaturas, incluye 18 Complementos de Formación con código `MINGIND2-C-nnn` (caracter `complementos`, fuera de los 120 ECTS; el regex de código debe admitir "C"). Las guías de Prácticas Externas y TFM están vacías en todos los cursos (solo ficha). Dobles másteres comparten asignaturas.

## uniovi_gitst / uniovi_dg_telecodatos / uniovi_mm_teleco — Universidad de Oviedo (Telecomunicación, Gijón)
- Plataforma: SIES de uniovi.es (Liferay), idéntica a `uniovi` (ver universidades/uniovi/notas_descubrimiento.md). Hosts: www.uniovi.es (robots permite).
- Fichas: `grados/ingenieria/telecomunicacion` (GITELE01), `grados/ingenieria/telecomunicaciondatos` (2GITSTIG, plan propio de 6 cursos con códigos y guías propios) y `masteres/ingenieriayarquitectura/telecomunicacion` (MINGTELE, incluye «Complementos de Formación» con código `-C-`).
- Tipo de fuente: HTML. Scripts: universidades/uniovi_{gitst,dg_telecodatos,mm_teleco}/{discover,scraper}_*.py. Config: config/universities_uniovi_teleco.json.
- Resultado: gitst 63/66 guías; dg_telecodatos 50/85 (las 35 sin guía son de 5.º-6.º curso, aún no publicadas); mm_teleco 23/26. Los TFG se ofertan por mención (ECTS ofertados > plan). Fase 3 pendiente.

## uniovi_giiti / uniovi_gcid / uniovi_dg_infdatos / uniovi_mm_inf — Universidad de Oviedo (Informática/Datos, Escuela de Ingeniería Informática)
- Plataforma: SIES de uniovi.es (Liferay, portlet UnioviSiesWeb), idéntica a `uniovi`/`uniovi_giti`; host www.uniovi.es (robots.txt solo veta /login, /group/, /web/guest/; permitido).
- Fichas: grados `https://www.uniovi.es/estudia/grados/ingenieria/{tecnologiasinformacion|datos|informaticadatos}`; máster `https://www.uniovi.es/estudia/masteres/ingenieriayarquitectura/informatica` (las URLs de asignatura y los endpoints serveGuiasDocentes/GuiaDocente cuelgan de la propia ficha).
- Códigos de plan: GIITIN01, GCINGD01, 2GITICID (doble grado: plan propio de 5 cursos, 348 ECTS, 63 asignaturas únicas con guías propias; no se deduplica contra los grados simples), MINFOR01 (máster; segmento `C` en los Complementos de Formación).
- Tipo de fuente: HTML. Scripts: universidades/{slug}/{discover,scraper}_*.py (copias de uniovi_giti; el doble grado y el máster relajan la regex de código/curso; el máster añade los caracteres «complementos_formacion» y TFM).
- Notas: asignaturas sin guía publicada en 2026-2027 se reportan como FALLO «sin guías docentes publicadas» (giiti 3, dg_infdatos 8 —todo 5.º curso—, máster 10 «Complementos de ...»; gcid 0). Resultados: giiti 40/43, gcid 44/44, dg 55/63, máster 21/31.

## uniovi_mm_mecatronica / _energia_elec / _automatizacion / _energetica / _integridad / _erasmus_mecatronica — másteres de la EPI Gijón (Universidad de Oviedo)
- Plataforma: SIES de uniovi.es (Liferay), igual que los grados `uniovi*`; fichas en `https://www.uniovi.es/estudia/masteres/ingenieriayarquitectura/{mecatronica|conversionenergia|automatizacion|energetica|integridadmateriales|erasmusmecatronica}`.
- Hosts: www.uniovi.es (robots.txt solo veta /buscador, /login, /group/, /web/guest/, /actualidad/duo; permitido).
- Patrón de guía: igual que grados (`…/-/fof/asignatura/{COD}` → `asignaturaId` → `serveGuiasDocentes` → `/GuiaDocente`); códigos `MMECAT03-1-001`, `MCEESP03-C-001`, `MINAUT02-2-003`, `MINGEN04-1-001`, `MIDMCE01-0-001`, `EMINMECA-1-001` (el 2.º token puede ser `C` = complementos de formación o `0`).
- Tipo de fuente: HTML. Scripts: universidades/uniovi_mm_*/{discover,scraper}_*.py (copias parametrizadas de uniovi_giti).
- Trampas: bloques de plan `cualquiera-temporalidad-…` (sin curso), carácter «Complementos de Formación», `meta.nivel="master"`; en los másteres impartidos en inglés la guía ES es solo un remite y hay que pedir `/en/` con otro cliente (cookie de idioma). Erasmus Mundus Mecatrónica: 27/37 guías publicadas vacías. Otros: `conversionenergiaextincion` (plan en extinción) e `integridadmateriales` («En extinción») existen; el Programa de Doctorado en Energía y Control de Procesos no tiene asignaturas y no se cataloga.
- Resultado: 22/22, 32/33, 21/22, 19/19, 13/13 y 10/37 Markdown. Fase 3 pendiente.

## ec_i_bologna01 — actualización (tercera pasada): resuelto
- Plataforma: igual que arriba. El id interno SÍ se obtiene por servidor: `…/course-unit-catalogue?codiceMateria={cod}&annoAccademico=2024&codiceCorso=0927&single=True&search=True` → enlace `course-unit/2024/{id}` (con 2025 sale vacío; validar que el h1 empiece por el código, si no es el curso integrado).
- Resultado: 36/44 filas con ficha EN, 36 Markdown. Scraper: universidades/ec_i_bologna01/scraper_ec_i_bologna01.py (reutilizable para otros corsi.unibo.it cambiando codiceCorso).

## ec_i_milano02 — actualización (tercera pasada): sigue parcial
- Fichas solo en www4.ceda.polimi.it (robots Disallow total); no hay alternativa pública (el PDF «Esperienza Studente» de ingindinf.polimi.it no lista asignaturas). Sin Fase 2.

## Reintento destinos sin guías (conv-retry, 2026-11-20)
- **ec_uk_liverpo02** (LJMU) — RESUELTA: Course Catalogue CourseLoop `coursecatalogue.ljmu.ac.uk/module/{año}/{CODE}` (robots Allow). Next.js: JSON completo en `__NEXT_DATA__` → `props.pageProps.pageContent` (description, unit_learning_outcomes, assessment_data con weight). 26/26 Markdown. `www.ljmu.ac.uk`/`cm-prod` vetados y `proformas.ljmu.ac.uk` 401: no se usan. Patrón reutilizable para otras universidades con CourseLoop.
- **ec_pl_rzeszow01** (PRz) — mejorada: sin portal de sílabos; el PDF «courses in English» de la facultad (dwm.prz.edu.pl/fcp/…/przedmioty_erasmus/wbmil_aktualizacion_2026.pdf, robots permite /fcp/) trae tabla Subject/ECTS/Description; 52 Markdown breves (solo contenidos). Karty en /files/ siguen vetadas.
- **ec_s_lulea01** (LTU) — sigue BLOQUEADA: `www.ltu.se/en/education/syllabuses/course-syllabus?id=CODE` es una app JS (Sitevision) sin contenido estático; la kursplan real es PDF de `epok.ltu.se/epok/dynpdf/…` (robots lo veta).

## Tanda Italia 2 (EIA/Eléctrica/Informática/Teleco; titulación no Mecánica)
- **ec_i_pavia01 / ec_i_modena01 / ec_i_beneven02** — Cineca Course Catalogue (`unipv|unimore|unisannio.coursecatalogue.cineca.it`, API JSON pública, robots permite). Plantilla de `ec_i_ancona01`. Trampa: en Pavia y Modena el endpoint `/api/v1/insegnamento` da 404 con `af_percorso=af_percorso_id` (=9999); funciona con `af_percorso=corso_percorso_id`. Cohortes 2024/2025/2026 combinadas (A.A. 2026/27). Titulaciones: Pavia Ing. Elettronica e Informatica (22 fichas/40 filas), Modena Ing. Elettronica (15/32), Sannio Ing. Elettronica e Biomedica (35/42).
- **ec_i_napoli01** — Cineca de unina con fichas vacías; se usa la Guida dello Studente 2022/23 (PDF compartido en ingegneria-elettronica.dieti.unina.it, robots permite): 32 schede de Ing. Elettronica (L-8), 32 Markdown, sin código oficial (slug del nombre).

## ec_p_coimbra01 — Universidade de Coimbra (LEEC, Eng. Eletrotécnica e de Computadores)
- Plataforma: apps.uc.pt/courses (portal «Cursos» de la UC), HTML estático; el buscador no da enlaces sin JS, se parte del id de programa.
- Hosts: apps.uc.pt (sin robots.txt, 404; permite); www.uc.pt solo veta rutas del portal.
- Patrón de URL de una guía: `https://apps.uc.pt/courses/EN/unit/{id}/{rama}/{curso}?common_core=true&type=ram&id={programa}` (plan: `/courses/PT/programme/8922/2025-2026?id_branch=21062`).
- Tipo de fuente: HTML (EN disponible). Scraper de referencia: universidades/ec_p_coimbra01/scraper_ec_p_coimbra01.py
- Notas: código oficial UC en comentario HTML de la fila (`<!--<td>01019327</td>-->`); `h2` por sección, `<p>` hermanos; omitir «Head Lecturer(s)». Vale para cualquier grado UC cambiando programa/rama. 36/36.

## ec_dk_alborg01 — Aalborg Universitet (BSc Applied Industrial Electronics, Esbjerg, en inglés)
- Plataforma: studieordninger.aau.dk (planes: tablas por semestre) + moduler.aau.dk (fichas), HTML estático.
- Hosts: moduler.aau.dk (robots solo sitemap), studieordninger.aau.dk (veta /pdf y /pdfcourses), www.en.aau.dk (Allow all).
- Patrón de URL de una guía: `https://moduler.aau.dk/course/{curso}/{codigo}`; plan: `https://studieordninger.aau.dk/2026/56/{id}` (6606 = Applied Industrial Electronics).
- Tipo de fuente: HTML. Scraper de referencia: universidades/ec_dk_alborg01/scraper_ec_dk_alborg01.py
- Notas: solo los grados «Esbjerg, English» se imparten en inglés (los de Aalborg son en danés). Las fichas no traen temario ni bibliografía (Learning objectives + Exam). 24/24, 180 ECTS.

## ec_d_bochum01 — Ruhr-Universität Bochum (B.Sc. Elektrotechnik und Informationstechnik)
- Plataforma: Modulhandbuch PDF único (TYPO3 de la facultad, ei.ruhr-uni-bochum.de, página «POs und Dokumente»).
- Hosts: ei/etit.ruhr-uni-bochum.de (robots permite /fileadmin); vvz.ruhr-uni-bochum.de desconecta (no usado).
- Patrón: un solo PDF `.../Ba_ETIT_PO20/Modulhandbuch_BaET_PO20_SS_2026_Stand_30.03.2026.pdf`; módulos delimitados por «Titel des Moduls:».
- Tipo de fuente: pdf_compartido. Scraper de referencia: universidades/ec_d_bochum01/scraper_ec_d_bochum01.py
- Notas: sin bibliografía; Kernfächer/Wahlbereiche son contenedores. 23/23, 180 ECTS.

## Tanda p3sur (Padova, Palermo, Roma, Molise, Catania, Pisa, Ljubljana, Komotini, Ioannina, Bratislava, Sofía, Oradea)
- **ec_i_padova01** — Università di Padova (Laurea Ingegneria Elettronica L-8 R, IN2911). Plataforma: Cineca Course Catalogue (`unipd.coursecatalogue.cineca.it`, API JSON, robots permite). Plantilla de `ec_i_pavia01` (generada con cohorte única 2025, sin filtro de A.A.: años 1-3 = 2025/26..2027/28; los años 3 sin ficha -> sin_guia). 29 filas / 14 Markdown (la mayoría de fichas del año 3 aún no publicadas).
- **ec_i_pisa01** — Università di Pisa (Laurea Ingegneria delle Telecomunicazioni L-8 R, ITCR-L). Cineca (`unipi.coursecatalogue.cineca.it`), misma plantilla, cohorte 2025. 26 filas / 12 Markdown.
- **ec_i_campoba01** — Università del Molise (Laurea Ingegneria Medica L-9 R, 421R; única de clase L-9 «industriale» en Molise). Cineca (`unimol.coursecatalogue.cineca.it`), cohorte 2025, tipo de curso «L2». 25 filas / 17 Markdown. Trampa: `des_en` vacío en el corso (nombre_grado sin paréntesis).
- **ec_i_roma01** — Sapienza (Laurea Ingegneria Informatica e Automatica L-8, curso 33501). Plataforma: `corsidilaurea.uniroma1.it` (Drupal, HTML estático, robots permite; `uniroma1.coursecatalogue.cineca.it` no es público). Plan: `/it/course/33501/attendance/lessons-plan` (`tr.activity`); ficha: `/attendance/lesson/<curr>/<año>/<sem>/<id>?channel=0` con acordeones `div.accordion-item` (h4 + `.accordion-content`); omitir «Docenti». Muchas fichas solo traen «Obiettivi formativi». 33 filas / 32 Markdown (1 sin_guia: «A scelta dello studente»).
- **ec_si_ljublja01** — Univerza v Ljubljani, Fak. za strojništvo. Plataforma: PDF compartido en inglés `wp-content/uploads/2026/06/ERASMUS-1.pdf` (índice p.2 + una ficha por página). Son asignaturas de MÁSTER (NNNN-M) para Erasmus+; el grado Mechanical Engineering (UN/PAP) no publica fichas de asignatura. Catálogo `parcial`, nivel «master», 36/36 Markdown.
- **ec_sk_bratisl02** — Comenius University Bratislava (FMFI, Bachelor Applied Informatics 1-AIN; no hay ingeniería industrial). Plataforma: PDF de fichas AIS2 `ais2.uniba.sk/repo2/repository/default/ais/informacnelisty/2025-2026/FMFI/EN/AIN.pdf` (179 págs., una ficha cada 1-3 págs., cabecera «COURSE DESCRIPTION»). Aviso: `ais2.uniba.sk/robots.txt` responde 403 (RFC 9309: sin restricciones) y los PDF dan 200. 96 filas / 96 Markdown.
- **ec_ro_oradea01** — Universitatea din Oradea (IETI, Electromechanics B.Eng., 240 créditos). Plataforma: `ieti.uoradea.ro` — plan en PDF (`curriculum/EM_EN_2026-2027.pdf`, filas `IETI-xxxx`) y fichas en PDF compartido de 289 págs. (`Bachelor_degree_programmes/2024_2025/FD_licenta_EM_EN_2024-2025.pdf`, «SUBJECT DESCRIPTION»), emparejadas por nombre normalizado (las fichas no llevan código). 76 filas / 49 Markdown (27 sin ficha). Ojo: texto vertical de márgenes en el PDF y epígrafes «6.Specific» sin espacio.
- **ec_g_ioannin01** — Univ. of Ioannina (CSE, Computer Science and Engineering, 240 ECTS; única fila Erasmus es un doctorado). Plataforma: PDF compartidos en inglés `cse.uoi.gr/wp-content/uploads/2025/09/2025-26_CSE-UOI_proptyxiaka-perigrammata_{core,elective}-courses_EN.pdf` (índice con páginas + «COURSE OUTLINE» por asignatura; robots permite, Crawl-delay 10). Plantilla ministerial griega: se eliminan las líneas presentes en ≥70 % de las fichas. 62 filas / 62 Markdown.
- **ec_i_palermo01** — Palermo (parcial, Ing. Meccanica L-9, CdS 2055): `www.unipa.it` da 503 persistente en las subpáginas del CdS y las fichas están en `offertaformativa.unipa.it` (JSF con sesión; robots ambiguo: Allow y Disallow `/` para `*`): regla de parada. 0 Markdown.
- **ec_i_catania01** — Catania (parcial, Ing. Industriale L-9 R, DIEEI): solo regolamenti en PDF; portal de syllabus no localizado; `unict.coursecatalogue.cineca.it` no es público. 0 Markdown.
- **ec_g_komotin01** — DUTH (parcial, ECE Xanthi): Οδηγός Σπουδών en PDF solo en griego (`ee.duth.gr`), sin parsear. 0 Markdown.
- **ec_bg_sofia20** — UCTM Sofía (parcial, Chemical Engineering): páginas «Bachelor/Curricula» en `uctm.edu/en` sin explorar a fondo; sin fichas localizadas. 0 Markdown.

## ec_f_angers01 — Université d'Angers (BUT GEII)
- Plataforma: Catálogo Ametys (formations.univ-angers.fr, 'odf-web') con PDF de programa por titulación.
- Hosts: formations.univ-angers.fr (robots permite). Las fichas de recurso solo traen horas/idioma.
- Patrón de URL de una guía: /fr/offre-de-formation/bachelor-universitaire-de-technologie-BUT/.../but-.../ue-.../r4-06-automatique-*.html
- Tipo de fuente: PDF compartido (solo programa); sin guía por asignatura
- Scraper de referencia: universidades/ec_f_angers01/discover_ec_f_angers01.py (sin scraper)
- Notas: Catálogo parcial BUT 1, filas sin_guia. Otros catálogos Ametys 'formations.univ-*.fr' tendrán la misma limitación en BUT; las Licences pueden traer descriptivos.

## ec_f_le_havr11 — Le Havre Normandie Université (Licence SPI Mécanique)
- Plataforma: WordPress univ-lehavre.fr; syllabus por curso en PDF (UFR ST).
- Hosts: www.univ-lehavre.fr (robots permite).
- Patrón de URL de una guía: https://www.univ-lehavre.fr/wp-content/uploads/2023/07/UFR-ST-L3-Mecanique-Syllabus.pdf (solo L3)
- Tipo de fuente: PDF compartido (UE por línea de título + 'OBJECTIFS D APPRENTISSAGE')
- Scraper de referencia: universidades/ec_f_le_havr11/scraper_ec_f_le_havr11.py
- Notas: Solo L3 tiene syllabus público; L1-L2 solo esquema de maquette. Texto con palabras partidas por el PDF.

## ec_f_poitier05 — ISAE-ENSMA Poitiers (diplôme d'ingénieur)
- Plataforma: WordPress ensma.fr; syllabus por año en PDF bilingüe FR/EN (una ficha por ECUE).
- Hosts: www.ensma.fr y ensma.fr (robots permite).
- Patrón de URL de una guía: https://ensma.fr/wp-content/uploads/2025/02/Syllabus-FISE-ENSMA-A2-2025-2026-previsionnel.pdf
- Tipo de fuente: PDF compartido
- Scraper de referencia: universidades/ec_f_poitier05/scraper_ec_f_poitier05.py
- Notas: Solo A2 localizado; ECTS por UE. Normalizar a NFC (diacríticos descompuestos). Códigos ECUE repetidos entre majeures.

## ec_f_rouen07 — ESIGELEC (Rouen)
- Plataforma: WordPress en.esigelec.fr; Course Outline de programas en inglés (PDF en CDN del proveedor web).
- Hosts: en.esigelec.fr (robots permite); en.vizzmedia.com (PDF, permite).
- Patrón de URL de una guía: https://en.vizzmedia.com/wp-content/uploads/2025/10/ESIGELEC-COURSE-OUTLINE-EES-2025-26.pdf
- Tipo de fuente: PDF compartido
- Scraper de referencia: universidades/ec_f_rouen07/scraper_ec_f_rouen07.py
- Notas: Nivel Master of Technology; los PDF de ingeniero (CONTENU-PEDAGOGIQUE) son de 1 página sin descriptivos.

## ec_f_marseil84 — Aix-Marseille Université (Licence Mécanique)
- Plataforma: Catálogo formations.univ-amu.fr (UE por parcours) + web de facultad sciences.univ-amu.fr.
- Hosts: formations.univ-amu.fr: robots.txt Disallow (BLOQUEADO); sciences.univ-amu.fr permite pero sin fichas.
- Patrón de URL de una guía: https://formations.univ-amu.fr/UE/3SMK/<código UE>?external=1 (no accesible)
- Tipo de fuente: HTML (bloqueado)
- Scraper de referencia: ninguno (solo discover_ec_f_marseil84.py, catálogo vacío)
- Notas: Regla de parada.

## ec_b_louvain01 — UCLouvain (Bachelor in Engineering, FSA1BA)
- Plataforma: Catálogo oficial uclouvain.be en inglés (HTML estático): programa por bloque anual + ficha por UE.
- Hosts: uclouvain.be (robots permite /en-cours-*, /en-prog-*).
- Patrón de URL de una guía: https://uclouvain.be/en-cours-2025-lepl1101 ; programa: https://uclouvain.be/en-prog-2025-fsa1ba-programme_annual_blocks
- Tipo de fuente: HTML
- Scraper de referencia: universidades/ec_b_louvain01/scraper_ec_b_louvain01.py
- Notas: Vale para cualquier programa UCLouvain cambiando el código (en-prog-AAAA-<sigle>). Las UE de máster (LMECA…) están en otros programas.

## ec_b_mechele14 — Thomas More Mechelen-Antwerpen (Bachelor Elektronica-ICT, Sint-Katelijne-Waver)
- Plataforma: Plataforma 'onderwijsaanbod' (Laravel) de Thomas More y KU Leuven: programa con tr.module-row + /syllabi/n/<código>.
- Hosts: onderwijsaanbod.thomasmore.be (robots veta /archief y /pdf; /syllabi permitido).
- Patrón de URL de una guía: https://onderwijsaanbod.thomasmore.be/syllabi/n/YT0662N
- Tipo de fuente: HTML
- Scraper de referencia: universidades/ec_b_mechele14/scraper_ec_b_mechele14.py
- Notas: La versión en inglés del programa está en /archief (vetada). Misma plataforma que ec_b_leuven01.

## ec_b_antwerp01 — Universiteit Antwerpen (Bachelor Electronics and ICT Engineering Technology)
- Plataforma: uantwerpen.be: página 'Study programme' con todos los cursos por Model Path.
- Hosts: www.uantwerpen.be (robots permite todo).
- Patrón de URL de una guía: https://www.uantwerpen.be/en/study/programmes/all-programmes/<programa>/bachelor/study-programme/?id=AAAA-<código> (devuelve la página del programa, sin ficha)
- Tipo de fuente: HTML (solo listado)
- Scraper de referencia: ninguno (solo discover_ec_b_antwerp01.py)
- Notas: Detalle de curso no accesible sin JS.

## ec_b_leuven01 — KU Leuven (Bachelor in de ingenieurswetenschappen)
- Plataforma: Plataforma 'onderwijsaanbod' (misma que Thomas More): programa + /syllabi/{n|e}/<código>.
- Hosts: onderwijsaanbod.kuleuven.be (robots veta /archief, /pdf y años anteriores; /syllabi/n|e permitido).
- Patrón de URL de una guía: https://onderwijsaanbod.kuleuven.be/syllabi/e/H01K9AE
- Tipo de fuente: HTML
- Scraper de referencia: universidades/ec_b_leuven01/scraper_ec_b_leuven01.py
- Notas: Reutilizable para cualquier programa KU Leuven cambiando SC_xxxx. El HTML trae las traducciones EN/NL; se conserva el idioma de la ficha.

## ec_nl_ensched01 — University of Twente (BSc Technical Computer Science)
- Plataforma: utwente.nl (currículo HTML) + catálogo Osiris (SPA).
- Hosts: www.utwente.nl (robots permite); utwente.osiris-student.nl sin robots, solo SPA JS.
- Patrón de URL de una guía: https://www.utwente.nl/en/tcs/education-programme/tcscurriculum-2/
- Tipo de fuente: HTML (solo listado)
- Scraper de referencia: ninguno (solo discover_ec_nl_ensched01.py)
- Notas: Las fichas están en Osiris (no HTML); sin endpoint documentado.

## ec_d_karlsru01 — KIT - Karlsruher Institut für Technologie (Maschinenbau B.Sc.) - NO es ec_d_karlsru05/hka
- Plataforma: mach.kit.edu: Modulhandbuch de la facultad en PDF (módulos + Teilleistungen).
- Hosts: www.mach.kit.edu (robots permite /download/).
- Patrón de URL de una guía: https://www.mach.kit.edu/download/MHB/82-604-H-20165_v1_2025-02-28_de.pdf
- Tipo de fuente: PDF compartido (nivel módulo)
- Scraper de referencia: universidades/ec_d_karlsru01/scraper_ec_d_karlsru01.py
- Notas: Plantilla KIT: 'M x.y Modul: ...[M-...]'. Los Teilleistungen (T-...) no se incluyen; sin semestre ni bibliografía por módulo.

## ec_d_rostock01 — Universität Rostock (Maschinenbau B.Sc.)
- Plataforma: Moduldatenbank QIS (pruefung.uni-rostock.de) + PDFs de SPSO en msf.uni-rostock.de.
- Hosts: pruefung.uni-rostock.de: robots.txt Disallow (BLOQUEADO); msf.uni-rostock.de permite pero sin fichas.
- Patrón de URL de una guía: (no accesible)
- Tipo de fuente: HTML (bloqueado)
- Scraper de referencia: ninguno (solo discover_ec_d_rostock01.py, catálogo vacío)
- Notas: Regla de parada.

## ec_d_bingen01 — TH Bingen (Maschinenbau B.Eng.)
- Plataforma: th-bingen.de (fileadmin): Modulhandbuch por titulación en PDF, plantilla con 'Kennnummer' y secciones numeradas.
- Hosts: www.th-bingen.de (robots.txt 404, sin restricciones).
- Patrón de URL de una guía: https://www.th-bingen.de/fileadmin/studium/bachelor/maschinenbau/Modulhandbuch_Bachelor_Maschinenbau_26-09-28.pdf
- Tipo de fuente: PDF compartido
- Scraper de referencia: universidades/ec_d_bingen01/scraper_ec_d_bingen01.py
- Notas: Vale para otros Modulhandbücher de TH Bingen (p. ej. Wirtschaftsingenieurwesen) ajustando el prefijo de código.

## ec_d_deggend01 — TH Deggendorf (Bachelor Künstliche Intelligenz)
- Plataforma: th-deg.de/Studierende/.../Modulhandbuecher: PDF por titulación ('Modul Nr. XX-nn').
- Hosts: www.th-deg.de (robots permite).
- Patrón de URL de una guía: https://www.th-deg.de/Studierende/Antraege-und-Organisatorisches/Modulhandbuecher/modulhandbuch_ki.pdf
- Tipo de fuente: PDF compartido
- Scraper de referencia: universidades/ec_d_deggend01/scraper_ec_d_deggend01.py
- Notas: Versión de 2022; plantilla común a los Modulhandbücher THD (otros: wi_bachelor, ias_bachelor...).

## ec_d_marburg01 — Philipps-Universität Marburg (B.Sc. Informatik)
- Plataforma: Online-Modulhandbuch del FB12 (www.mathematik.uni-marburg.de/modulhandbuch/AAAAS/<programa>/), HTML estático generado.
- Hosts: www.mathematik.uni-marburg.de (robots.txt 404, sin restricciones); www.uni-marburg.de veta /search y QIS.
- Patrón de URL de una guía: https://www.mathematik.uni-marburg.de/modulhandbuch/20262/BSc_Informatik/Informatik_Basismodule/Algorithmen_und_Datenstrukturen.html
- Tipo de fuente: HTML
- Scraper de referencia: universidades/ec_d_marburg01/scraper_ec_d_marburg01.py
- Notas: Otros programas FB12 (BSc_Data_Science, BSc_Mathematik...) usan la misma estructura. Sin semestre por módulo.

## ec_p_lisboa07 — ISCTE-IUL (Licenciatura em Engenharia de Telecomunicações e Informática)
- Plataforma: web del grado `iscte-iul.pt/programmes/degree/9098` (EN, HTML estático); cada UC en un modal con Objectives/Programme/Evaluation/Bibliography. `fenix.iscte-iul.pt` vetado por robots.
- Código = id del enlace «See more» (fenix-mais). Scraper: universidades/ec_p_lisboa07/scraper_ec_p_lisboa07.py. 28/28 Markdown.

## ec_p_vila_re01 — UTAD (Engenharia Mecânica) — parcial
- Plan solo en el Diário da República (Aviso 22542/2023, PDF) → 34 UC/180 ECTS `sin_guia`; fichas en inforestudante.utad.pt/nonio (login). 0 Markdown.

## ec_p_maia01 — ISMAI (Energias Renováveis) — parcial
- Plan HTML estático con códigos (35 UC); fichas vía callback WebForms (`VerFPUC`) no servido a PoliteClient. 0 Markdown.

## ec_p_porto05 — Instituto Politécnico do Porto — parcial vacío
- ipp.pt/isep.ipp.pt: SSL CERTIFICATE_VERIFY_FAILED (como Lisboa Nova). Sin catálogo.

## ec_tr_mersin04 — Toros University (Endüstri Mühendisliği)
- Plataforma: Bologna Bilgi Paketi `obsogrenci.toros.edu.tr/BLGNDersBilgiPaketi` (AngularJS, JSON por POST, público); `bologna.toros.edu.tr` solo lo incrusta. Patrón reutilizable para otras universidades con «BLGNDersBilgiPaketi» (omitir yilID para la versión más reciente).
- 84 filas (programa TR 115, currículo 2022-Devam); 53 Markdown (en turco); 31 sin contenido publicado.

## ec_tr_istanbu07 — Yıldız Technical University (Kimya Mühendisliği %100 İngilizce)
- Plataforma: Bologna Bilgi Sistemi propio `http://www.bologna.yildiz.edu.tr` (Yii, HTML por GET; sin www falla TLS). Valdría para otras titulaciones de YTU cambiando program id/aid. 235/235 Markdown (turco).

## ec_tr_kocaeli02 — Kocaeli Üniversitesi — parcial vacío
- Hosts oficiales con TLS legacy (UNSAFE_LEGACY_RENEGOTIATION) / EOF; obs/ebs no resuelven.

## ec_tr_elazig01 — Fırat Üniversitesi — parcial vacío
- Hosts con timeout/DNS desde esta red. Sin catálogo.

## ec_tr_samsun01 — Ondokuz Mayıs Üniversitesi — parcial vacío
- ebs.omu.edu.tr → RobotsBlocked; el PDF de cursos en inglés de erasmus.omu.edu.tr solo trae código/título/ECTS sin plan ni fichas.

## ec_uk_staffor02 — Staffordshire University (BEng Electrical and Electronic Engineering)
- Plataforma: ficha de curso en www.staffs.ac.uk (HTML; tablas `table--modules` por itinerario y año, descripción de cada módulo en modales `div.modal[data-modal]`).
- Hosts: www.staffs.ac.uk (robots veta solo /atoz/, /course/seed/, etc.; /course/ permitido).
- Patrón de URL: `https://www.staffs.ac.uk/course/electrical-electronic-engineering-beng` (una sola página; la «guía» es el modal del módulo).
- Tipo de fuente: HTML. Scraper de referencia: universidades/ec_uk_staffor02/scraper_ec_uk_staffor02.py
- Notas: solo descripción corta + código de módulo (sin LO/evaluación públicos); créditos UK/2 = ECTS. 16/16 (parcial por falta de detalle).

## ec_pl_krakow02 — AGH University of Krakow (Electrical Engineering, 1.er ciclo)
- Plataforma: sylabusy.agh.edu.pl (Symfony). Plan: `/en/1/2/22/1/4/16/12` (7 tablas semestrales, `data-syllabus-id`); ficha completa: `/en/document/{uuid}.html` (ruta FOS `preview_front_preview` sacada de `/js/routing.json`; el botón del plan la carga por AJAX).
- Hosts: sylabusy.agh.edu.pl (sin robots.txt; permite).
- Tipo de fuente: HTML. Scraper: universidades/ec_pl_krakow02/scraper_ec_pl_krakow02.py (reutilizable para cualquier programa de AGH cambiando la URL del plan).
- Notas: nombres en inglés pero cuerpo de la ficha en polaco; `#syllabus_content` con tablas; eliminar `.head-author/.head-teachers`. 115/115.

## ec_pl_gliwice01 — Silesian University of Technology (Industrial and Engineering Chemistry, BSc en inglés)
- Plataforma: listados «Erasmus_Eng_Sylabus» de www.polsl.pl/rch (WordPress/Elementor, `?p=111528` invierno, `?p=111550` verano) con nombre, código, ECTS y enlace a PDF.
- Hosts: www.polsl.pl (robots permite; Crawl-delay 60); **euslugi.polsl.pl** (donde viven los PDF) — robots.txt no permite el acceso automatizado → BLOQUEADO, sin Fase 2.
- Tipo de fuente: pdf (no descargados). Scraper: ninguno (solo discover_ec_pl_gliwice01.py). 29 filas, 0 Markdown.

## ec_pl_gdynia01 — Gdynia Maritime University (B.Sc. Electrotechnics, Marine Electrical Engineering)
- Plataforma: dos PDF oficiales «courses in English» (fall/summer) en umg.edu.pl/en/courses (Drupal); línea «Título ECTS Sem» + «Description:».
- Hosts: umg.edu.pl (robots solo veta rutas administrativas Drupal).
- Tipo de fuente: pdf_compartido. Scraper: universidades/ec_pl_gdynia01/scraper_ec_pl_gdynia01.py (importa el parser del discover).
- Notas: solo descripción corta (contents); código = 'UMG-'+slug del título. 46/46.

## ec_pl_gdansk02 — Gdańsk University of Technology (Mechanical Engineering, WIMiO)
- Plataforma: ECTS Catalog `ects.pg.edu.pl` (HTML estático): lista por semestre `/en/courses/{id}/subcourses/{id}/subjects` (`.data-table-semester .data-table__row`) + ficha PDF `/en/subjects/{id}/card.pdf` (texto, en inglés, con código `PG_…`).
- Hosts: ects.pg.edu.pl (sin robots.txt; permite).
- Tipo de fuente: pdf por asignatura. Scraper: universidades/ec_pl_gdansk02/scraper_ec_pl_gdansk02.py (reutilizable para otras carreras PG cambiando la URL del plan).
- Notas: la cohorte más nueva solo publica fichas de sem 1-2; se usa la cohorte 2023/24 (listado en `/en/courses?p=2`). 68/68.

## ec_pl_bydgosz01 — Kazimierz Wielki University, Bydgoszcz (ICT courses in English)
- Plataforma: catálogo Erasmus erasmus.ukw.edu.pl/en/courses/ (PHP propio): filtro POST (`idObszar`, token `sessTokenId`; 17 = ICT) + silabo PDF `/en/courses/syllabus/{id}/`.
- Hosts: erasmus.ukw.edu.pl (robots veta solo /admin, /src).
- Tipo de fuente: pdf. Scraper: universidades/ec_pl_bydgosz01/scraper_ec_pl_bydgosz01.py
- Notas: no hay plan de estudios público en inglés; el filtro no persiste en la paginación (se filtra por texto). Plantillas PDF heterogéneas; 1 silabo es .doc (OLE) no convertible. 9/10.

## ec_cz_pardub01 — University of Pardubice (FEI, Bachelor, courses in English)
- Plataforma: catálogo ECTS de intercambio en www.upce.cz (tabla «Bachelor's Degree Program») + fichas IS/STAG `portal.upce.cz/StagPortletsJSR168/CleanUrl?urlid=prohlizeni-predmet-sylabus&predmetZkrPrac=…&predmetZkrPred=…&predmetRok=2026&plang=en`.
- Hosts: www.upce.cz (permite), portal.upce.cz (sin robots.txt; permite).
- Tipo de fuente: HTML. Scraper: universidades/ec_cz_pardub01/scraper_ec_cz_pardub01.py (válido para cualquier STAG con ese portlet).
- Notas: secciones en `th.top` (variantes th+td en la misma fila o en la siguiente); se omiten «Guarantors and lecturers». 30/30.

## ec_ro_clujnap01 — Babeș-Bolyai University (Computer Science, English line)
- Plataforma: app de fichas de la Facultad `www.cs.ubbcluj.ro/apps/fise/viewSyllabi.php?an=2025&lang=en&specializare=IE` (HTML por semestre) + PDF «fișa disciplinei» `/files/curricula/2025/syllabus/…pdf`.
- Hosts: www.cs.ubbcluj.ro (robots solo veta /wp-admin).
- Tipo de fuente: pdf por asignatura. Scraper: universidades/ec_ro_clujnap01/scraper_ec_ro_clujnap01.py
- Notas: `specializare` IE=Computer Science EN, IIE=Information Engineering EN. Texto rotado de las etiquetas laterales y ligaduras f→X/P corregidos; la columna «Teaching methods» queda intercalada. 59/59.

## ec_s_linkopi01 — Linköping University (6CIEI Industrial Engineering and Management – International)
- Plataforma: Studieinfo de LiU. Programa `liu.se/studieinfo/program/{código}` (tablas por término con enlaces `/kurs/{CODE}/{ht|vt}-{año}`); ficha EN `https://studieinfo.liu.se/en/kurs/{CODE}/{term}` (h2: Intended learning outcomes, Course content, Examination, Course literature…).
- Hosts: liu.se y studieinfo.liu.se (robots permite).
- Tipo de fuente: HTML. Scraper: universidades/ec_s_linkopi01/scraper_ec_s_linkopi01.py (válido para cualquier programa LiU).
- Notas: no hay grado de 3 años: se catalogan términos 1-6 de un programa de 300 hp. 28/28; 5 fichas sin LO/contenido en la fuente.

## ec_sf_vaasa01 — University of Vaasa — BLOQUEADA/parcial
- Plataforma: Peppi (opas.peppi.uwasa.fi): SPA Angular con backend `https://opas.peppi.uwasa.fi/api/…` (rutas `educations`, `education/{id}`, `course`, `course/text`, `realizations`… en main.js, sin documentar; `/api/educations` → 404).
- Hosts: opas.peppi.uwasa.fi (index.html estático sin contenido), www.uwasa.fi (permite; solo PDFs de planes antiguos).
- Tipo de fuente: sin resolver. Catálogo vacío (parcial); queda reconstruir la API (parámetros `period`, `language`, ids de educación) a partir del bundle.

## ec_sf_espoo12 — Aalto University (Bachelor's Programme in Electrical Engineering, ELEC1)
- Plataforma: Sisu (CSC/Aalto), API pública JSON `https://sisu.aalto.fi/kori/api/`: `module-search?curriculumPeriodId=aalto-LV-75&universityId=aalto-yliopisto&moduleType=DegreeProgramme`, `modules/by-group-id?groupId=…` (árbol `rule`: ModuleRule/CourseUnitRule), `course-units/by-group-id?groupId=…` (outcomes, content, prerequisites, additional; HTML ligero).
- Hosts: sisu.aalto.fi (sin robots.txt; permite).
- Tipo de fuente: API JSON. Scraper: universidades/ec_sf_espoo12/scraper_ec_sf_espoo12.py (reutilizable para otras universidades Sisu cambiando universityId/periodo).
- Notas: periodos `aalto-LV-75`=2025-26. Evaluación y bibliografía están en las realizaciones (no incluidas). 98/98.

### ec_d_osnabru02__elec / __info / __m_mec (extra) — Hochschule Osnabrück: Elektrotechnik B.Sc., Technische Informatik B.Sc., Maschinenbau M.Sc.
Modulhandbuch PDF único por titulación (`fileadmin/Modulhandbuch/{BET|BTI|MMB}/StO2025_Stand..._*.pdf`), misma plantilla que `ec_d_osnabru02` (copiar y parametrizar URL). 67 / 58 / 41 fichas. Se localizan con búsqueda web por el patrón de carpeta.

### ec_d_karlsru05__m_mec (extra) — HKA Maschinenbau M.Sc. (MABM)
Modulhandbuch PDF (misma plantilla que MABB, `Modulhandbuecher_2026/..._Modulhandbuch_MABM.pdf`); parser MABB adaptado sin SPO. Portadas de Vertiefung antes de la ficha → se descartan; «Vertiefungsmodul n» sin ficha. 18 fichas.

### ec_d_ingolst01__info (extra) — THI Informatik B.Sc.
`www.thi.de/fileadmin/daten/fakultaetI/Modulhandbuecher/MHBuch_INF-B.pdf`; plantilla THI (Modulkürzel) como Maschinenbau, pero cabecera/pie de página distintos. 37 fichas.

### ec_d_bochum01__tele (extra) — RUB IT-Sicherheit/Informationstechnik B.Sc.
Modulhandbuch de informatik.rub.de (`MHB-BSc-ITS-SoSe-26.pdf`), plantilla «Titel des Moduls:»; sin código ni semestre en ficha (código = slug). 43 fichas.

### ec_d_karlsru05__elec (extra) — HKA Mechatronik B.Eng. (MECB)
`.../Modulhandbuecher_2026/20260401_Modulhandbuch_MECB.pdf` (nombre inferido por analogía con MABB/MABM y confirmado). Misma plantilla; parser derivado de `ec_d_karlsru05__m_mec`. 36 fichas.

### ec_a_graz09__mec (extra) — FH JOANNEUM Luftfahrt/Aviation B.Sc.
Misma plataforma HTML (página Curriculum, `button.course-item`) que `ec_a_graz09`; URL `/luftfahrt/bachelor/en/my-studies/curriculum/` (no `/aviation/`). Parcial: solo descripciones breves. 67 filas / 65 MD.

## ec_f_grenobl22__info / __elec — UGA Licence Informatique (parcours Informatique, Grenoble) y Licence EEA (2e-3e année)
- Plataforma: catálogo ODF/Ametys formations.univ-grenoble-alpes.fr (sitemap.xml + fichas UE HTML). Mismo scraper que ec_f_grenobl22 con otro BASE de parcours.
- Hosts: formations.univ-grenoble-alpes.fr (robots permite). Tipo: HTML. Notas: parcial (sin 1.er año); sin evaluación ni bibliografía públicas. info 15 UE, elec 61 UE.

## ec_p_lisboa109__info / __tele / __elec — IST Lisboa LEIC-A, LERC, LEEC21
- Plataforma: Fénix IST (currículo HTML + API /api/fenix/v1) igual que ec_p_lisboa109; solo cambian DEGREE_ID y /cursos/{acrónimo}/curriculo.
- Hosts: fenix.tecnico.ulisboa.pt (sin robots.txt). Tipo: API JSON. Notas: HASS sin guía; sin objetivos ni prerrequisitos en la API; LEIC-A 30/34, LERC 31/37, LEEC21 35/40 Markdown.

## ec_i_ancona01__elec — Ingegneria Elettronica e delle Tecnologie Digitali (L-8) (2.ª titulación de ec_i_ancona01)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_ancona01__elec/scraper_ec_i_ancona01__elec.py
- Notas: 10/28 con guía; 10 Markdown.

## ec_i_cagliar01__elec — Ingegneria Elettronica, Informatica e delle Telecomunicazioni (L-8) (2.ª titulación de ec_i_cagliar01)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_cagliar01__elec/scraper_ec_i_cagliar01__elec.py
- Notas: 20/47 con guía; 20 Markdown.

## ec_i_cagliar01__quim — Chimica (L-27) (2.ª titulación de ec_i_cagliar01)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_cagliar01__quim/scraper_ec_i_cagliar01__quim.py
- Notas: 5/28 con guía; 5 Markdown.

## ec_i_firenze01__tele — Ingegneria Elettronica (L-8) (2.ª titulación de ec_i_firenze01)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_firenze01__tele/scraper_ec_i_firenze01__tele.py
- Notas: 27/44 con guía; 27 Markdown.

## ec_i_beneven02__tele — Ingegneria Informatica (L-8) (2.ª titulación de ec_i_beneven02)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_beneven02__tele/scraper_ec_i_beneven02__tele.py
- Notas: 24/30 con guía; 24 Markdown.

## ec_i_salerno01__m_mec — Laurea Magistrale en Ingegneria Meccanica (LM-33) (2.ª titulación de ec_i_salerno01)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_salerno01__m_mec/scraper_ec_i_salerno01__m_mec.py
- Notas: 17/35 con guía; 17 Markdown.

## ec_i_trento01__m_mec — Laurea Magistrale Ingegneria civile, ambientale e meccanica (2.ª titulación de ec_i_trento01)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_trento01__m_mec/scraper_ec_i_trento01__m_mec.py
- Notas: 0/30 con guía; 0 Markdown.

## ec_i_modena01__info
Cineca (`coursecatalogue.cineca.it`) reutilizando el flujo de `ec_i_modena01`: solo cambia COHORTES. Laurea in Ingegneria Informatica (MO), L-8, cdsCod 20-212/20-312 — 2.ª titulación afín (informática) de Modena; la ya extraída es Ingegneria Elettronica. 31 filas, 20 Markdown.

## ec_i_beneven02__info
Cineca (`coursecatalogue.cineca.it`) reutilizando el flujo de `ec_i_beneven02`: solo cambia COHORTES. Laurea in Ingegneria Informatica, L-8, cdsCod 863/800 — 2.ª titulación (informática) de Sannio; la ya extraída es Elettronica e Biomedica. 30 filas, 24 Markdown.

## ec_i_cagliar01__info
Cineca (`coursecatalogue.cineca.it`) reutilizando el flujo de `ec_i_cagliar01`: solo cambia COHORTES. Laurea in Ingegneria Elettronica, Informatica e delle Telecomunicazioni, L-8, cds 70/94 (71/04 en 2025) — cubre informática y también teleco/electrónica; la ya extraída es Meccanica e Gestionale. 47 filas, 30 Markdown.

## ec_i_salerno01__info
Cineca (`coursecatalogue.cineca.it`) reutilizando el flujo de `ec_i_salerno01`: solo cambia COHORTES. Laurea in Ingegneria Informatica, L-8, cds 06127/IE127 — 2.ª titulación (informática); la ya extraída es Meccanica. 37 filas, 6 Markdown.

## ec_i_padova01__tele — Information Engineering L-8 (2.ª titulación de ec_i_padova01)
- Plataforma: Cineca Course Catalogue, API JSON pública (ver ec_i_ancona01).
- Hosts: el mismo catálogo del destino (robots permite).
- Tipo de fuente: API. Scraper: universidades/ec_i_padova01__tele/scraper_ec_i_padova01__tele.py
- Notas: 14/31 con guía; 14 Markdown.

## ec_i_bologna01__info
Unibo (corsi.unibo.it + ficha EN en www.unibo.it) reutilizando `ec_i_bologna01`: cambian URL del piano (CdS nuevo, sacado de /insegnamenti), codiceCorso y años de búsqueda. Laurea in Ingegneria informatica (L-8, CdS 6668), plan A.A. 2026/27 cohorte 2025. 28 filas, 14 con ficha, 14 Markdown.

## ec_i_bologna01__m_mec
Unibo (corsi.unibo.it + ficha EN en www.unibo.it) reutilizando `ec_i_bologna01`: cambian URL del piano (CdS nuevo, sacado de /insegnamenti), codiceCorso y años de búsqueda. Laurea Magistrale in Ingegneria meccanica (LM-33, CdS 6721, currículo 912; otros. 53 filas, 40 con ficha, 34 Markdown.

## ec_bg_rousse01__elec / __mec — Univ. of Ruse (Electrical Power Engineering; Industrial Engineering)
- Plataforma: ECTS Information Package por facultad (PDF compartido en www.uni-ruse.bg, ver ec_bg_rousse01). FEEA: plan por texto (códigos S0xxxx/SBxxxxx, normalizar SO→S0); FMME: parser geométrico existente cambiando el título del CURRICULUM.
- Notas: 55 filas cada uno; 55/55 y 51/55 Markdown (4 sin descripción). Sin learning_outcomes/bibliography/prerequisites.

## ec_tr_ankara02__elec / __quim — Gazi University (Electrical-Electronic Eng (Eng); Chemical Eng (Eng))
- Plataforma: OBS/Proliz igual que ec_tr_ankara02; solo cambia curSunit (1112123 / 114242258; listado en unitSelection.aspx?type=lis&lang=en). 174/174 y 204/204 Markdown.

## ec_dk_alborg01__m_mec — Aalborg (MSc Mechanical Engineering)
- studieordninger.aau.dk/2026/59/6801 (máster en /2026/59) + moduler.aau.dk; mismo scraper que ec_dk_alborg01. 34/34. Sin temario ni bibliografía.

## ec_uk_liverpo02__m_mec / __elec — LJMU (MEng Mechanical nivel 7; BEng Electrical and Electronic)
- Programme Specs `prodcat.ljmu.ac.uk/KIS/{32120-MG|32118-BGH}.pdf`, parseo por texto («[MODULE] CÓDIGO Título Approved … - N credit points», «Level N Core/Optional») + CourseLoop como ec_uk_liverpo02. 10/10 y 21/21.

## ec_tr_duzce01__elec — Düzce (Elektrik-Elektronik Müh., /Bolum/OgretimProgrami/15?bot=16)
- Plataforma EBS igual que ec_tr_duzce01; fichas en turco. Ver notas del slug para resultado de Fase 2.

## ec_cz_ostrava01__elec — VŠB Ostrava FEI (oferta Erasmus+ de la facultad de Electrotecnia/Informática)
- Mismo catálogo JSF que ec_cz_ostrava01 con `courses/fei/`. Catálogo parcial (oferta de intercambio, no plan).
