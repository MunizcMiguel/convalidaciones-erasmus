# HIS — Högskolan i Skövde · notas de descubrimiento (Fase 1)

## Programa
**Högskoleingenjör i maskinteknik (MAHIG), 180 hp** — "Bachelor Programme in Mechanical Engineering".
Es el programa de admisión actual (HT2026, HT2027). El antiguo "Maskiningenjör (MAING)" está en
extinción y su URL en his.se ya muestra el contenido de MAHIG.

## BLOQUEO: robots.txt de pdfproxy.his.se
Todos los kursplaner y la utbildningsplan son PDF servidos por `https://pdfproxy.his.se/`, cuyo
robots.txt dice:

    User-agent: *
    Disallow: /
    (Allow solo para Googlebot y Bingbot)

Por la regla del proyecto, **no se ha descargado ningún kursplan** y Fase 2 no debe hacerlo sin
permiso explícito de HIS (o descarga manual por una persona). No he encontrado ninguna fuente
alternativa permitida: www.his.se solo tiene páginas HTML para cursos "fristående" (sueltos), no para
los cursos de programa; no hay API/JSON pública detectada.

**Trampa en `common/http_client.py`:** ese robots.txt empieza con BOM UTF-8 y `urllib.robotparser`
no reconoce entonces la primera línea `User-agent`, así que `PoliteClient._allowed()` devuelve True
por error para pdfproxy.his.se (y student.his.se). Durante la exploración se descargó así, sin querer,
1 PDF (utbildningsplan 24507/SV) antes de advertirlo, más 6 intentos fallidos (HTTP 500) a `.../24507/EN`;
el PDF se borró de la caché y el script no lo usa. Convendría hacer `.lstrip("﻿")` en el cliente común.

## Fuente usada
`https://www.his.se/utbildning/ingenjor-och-teknik/hogskoleingenjor-i-maskinteknik-mahig`
(HTML estático renderizado en servidor, permitido por robots.txt de www.his.se). Una sola petición.

- `section.faq-block` con `<h2>Kursupplägg</h2>` → `dl.faq > dt/dd`: listas `<ul><li>Nombre, 7,5 hp</li>`
  bajo encabezados `År N – hösttermin/vårtermin` (años 1-2) y `h3` fördjupning + `h4` Hösttermin/Vårtermin (año 3).
  De aquí salen nombre, hp, año, termin e itinerario de las 27 filas.
- `section.program-occation-more-info` (una por convocatoria de admisión) → `div.program-course-semester`
  ("Termin 1, Höst 2026") + `div.program-semester-courses a[href]`: enlaces a kursplan PDF. Solo están
  publicados los terminer 1-3 de la convocatoria HT2026 (11 cursos); el script elige la convocatoria con más enlaces.
- Los nombres difieren entre ambos bloques ("Mekanik 1" vs "Mekanik I", "Ritteknik och CAD" vs "Ritteknik & CAD",
  "Organisation och ledarskap" vs "... I G1N"); se casan por clave normalizada dentro del mismo termin y el script
  falla si un enlace no casa de forma única. `nombre_asignatura` usa el nombre del enlace (el oficial) cuando existe.

## Patrones de URL
- Kursplan: `https://pdfproxy.his.se/coursesyllabus/{id}/SV` — `{id}` es un id interno de versión del
  kursplan, NO el código de curso; no es derivable, hay que leerlo de la página del programa.
- Utbildningsplan: `https://pdfproxy.his.se/programmesyllabus/{id}/SV` (HT2026: 24672; HT2027: 24673).
- `/EN` en programmesyllabus devolvió HTTP 500 para MAHIG; no se ha comprobado `/EN` en coursesyllabus
  (host bloqueado por robots). La página del programa solo enlaza versiones SV. Idioma registrado: `sv`.

## Limitaciones del catálogo (estado = "parcial")
- **Sin códigos oficiales**: la web no los publica (están en los PDF). `codigo_asignatura` es una clave
  provisional `MAHIG-T<termin>-<SLUG>`; Fase 2 debería sustituirla por el código real (formato HIS tipo `MT522G`).
- 11 de 27 filas con URL; 16 `sin_guia` (terminer 4-6 aún no publicados para HT2026, más 2 "Valfri kurs"
  de libre elección que nunca tendrán kursplan propio).
- ECTS: 232,5 hp en filas = 120 comunes (años 1-2) + 3 fördjupningar alternativas de 30 hp en otoño de 3º
  (82,5 hp únicos; FEM compartida por Produktutveckling y Konstruktionsteknik) + 7,5 valfri + 22,5 examensarbete.
  Ruta de un estudiante = 180 hp (validado por itinerario en el script).
- La lista de la utbildningsplan (rev. 2.1) llama "Programmering I" a lo que la web llama "Programmering för ingenjörer".

## Estructura del kursplan (NO verificada sobre muestras, por el bloqueo)
Formato estándar de kursplan sueco en PDF de texto (2-4 páginas): cabecera con nombre, hp, kurskod, nivel,
fecha de validez; secciones numeradas habituales: Innehåll (contenidos), Mål / lärandemål (resultados),
Examinationsformer (evaluación, con moment y hp), Förkunskapskrav, Betyg, Kurslitteratur (a veces en anexo
separado). Tómese como hipótesis a confirmar.
