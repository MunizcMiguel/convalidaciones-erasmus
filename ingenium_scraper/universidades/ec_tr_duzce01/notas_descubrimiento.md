# ec_tr_duzce01 — Düzce Üniversitesi (Makine Mühendisliği)

- Hints: `cdn.duzce.edu.tr/File/GetFile/…` y `w3-api-duzce-edu-tr.translate.goog/…` = documentos de la oficina internacional (no catálogo). `obs.duzce.edu.tr/oibs/bologna/` devuelve «Sistem Mesajı» (no hay módulo Bologna ahí). El catálogo real es el **Eğitim Bilgi Sistemi `https://ebs.duzce.edu.tr`** (enlazado desde `www.duzce.edu.tr`; sin robots.txt, 404).
- Grado: Makine Mühendisliği (Mühendislik Fakültesi), Normal Öğretim, 240 ECTS, 8 semestres. Programas: `/Program/Index/2` (lista de grados) → `/Bolum/OgretimProgrami/16?bot=18` (Normal Öğretim; `bot=217` = İkinci Öğretim; 274 = Makine ve İmalat Müh., no usada).
- Plan: una tabla HTML por semestre (columnas Kodu, Ders Adı, Zorunlu mu?, Ortalama, T+U, Kredi, AKTS), enlace a `/Ders/Index/{id}?bno=16&bot=18&yilNo=33` (yilNo 33 = 2025-2026; 34 = 2026-2027 aparece en el selector pero el listado enlaza 33). GET sin sesión.
- Trampas: (1) los semestres 5-8 repiten el mismo pool de optativas (MM4xx, US2xx, MS3xx…) → se catalogan una vez, en el primer semestre en que aparecen; (2) huecos de grupo electivo sin código ni ficha («Bölüm Seçmelisi», «Mesleki Ders Grubu», «Fakülte Seçmelisi», «SecÜni») y filas de formación pedagógica (PF*, İBSPF*) se omiten; (3) algunas fichas son casi vacías en origen (p. ej. MM201 solo tiene evaluación; MM499 casi nada) → bloques ausentes = hecho a reportar; (4) la UI en inglés depende de cookie (`/Ceviri/DilGuncelle?dil=en-US`) y rompe la caché por URL → se usa la UI turca; las fichas están en turco.
- ECTS: obligatorias 186 + huecos electivos omitidos (hasta 240); por semestre las obligatorias suman 30,32,30,30,25,23,6,10 (el resto son cupos de optativas). 127 filas.

## Fase 2
- `scraper_ec_tr_duzce01.py`: `div.ebs-yazdir-tam > div.card` (cabecera h4/h5 + `card-body`); tablas «ebs-bilgi-tablosu» (th/td) pasan a subsecciones; se eliminan Dersin Koordinatörü, Dersi Veren(ler) y la columna «Sorumlu Personel» de la tabla de evaluación (la evaluación conserva Vize/Final y porcentajes); se omite la matriz de competencias del programa.

## Resultado de la Fase 2 (revisión)
- El servidor del EBS devolvió **HTTP 404 intermitentes** durante la primera pasada (47 fichas «404» que en una segunda pasada respondieron bien: probable limitación de ritmo/caché del servidor). Tras reintentar, solo 3 filas siguen rotas en origen y quedan `sin_guia` (MM203, MM207: 404; MM462: página sin ficha); lista en `guias_404.json` (el discover la reutiliza; `--verify` vuelve a comprobar). 124 de 127 filas convertidas a Markdown.
- Muchas fichas son casi vacías en origen (p. ej. MM201, MM314, MM443: solo cabecera y/o evaluación): los `blocks_found` en false reflejan el origen, no un fallo del script.
- Si el scraper devuelve 404 aislados en una pasada, volver a ejecutarlo: los éxitos están en caché y los 404 no.
