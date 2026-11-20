# ec_tr_sakarya01 — Sakarya Üniversitesi (Makine Mühendisliği)

- Hint `erasmus.sakarya.edu.tr` = web Erasmus (correcta pero sin catálogo de la titulación; su «English Course Catalogue»/«Department catalogs» son anuncios). El catálogo está en el **Eğitim Bilgi Sistemi `https://ebs.sakarya.edu.tr`** (HTML por GET; `www.sakarya.edu.tr` corta la conexión a PoliteClient, `obs.`/`bologna.` no resuelven).
- Grado: Mühendislik Fakültesi → Makine Mühendisliği Bölümü (unidad EBS 290): `https://ebs.sakarya.edu.tr/Birim/DersPlan/290` (acreditado MÜDEK hasta 2027). Programas turcos, 8 semestres, 240 ECTS.
- Plan: tablas «Kodu | Ders | Tür | Dil | T+U | Kredi | AKTS» bajo cabeceras «N. Yarıyıl Ders Planı» (los semestres 7 y 8 tienen dos tablas: obligatorias y optativas); cada fila enlaza `/Ders/Detay/{id}`. 112 asignaturas con código (200 ECTS obligatorios + 287 ofertados de optativas). Los huecos de grupo («Formasyon Seçmeli», «Teknik Seçmeli (Akış/Isıl Tasarım)», «Üniversite Ortak Seçmeli», «Disiplinlerarası Seçmeli»…) no tienen código ni ficha y se listan en `meta.notas`.
- Ficha: `#dersDetay` con tablas por id (`{nombre}-Detay` label/valor, `Ders-Ogrenme-Ciktilari`, `Ders-Akisi`, `Ders-Kaynaklari`, `Ders-Degerlendirme-Sistemi`, `Ders-Akts-Is-Yuku`, y matrices de programa que se omiten). Idioma: turco.
- Trampa: la página incluye un árbol de navegación enorme (300-600 KB) → se trabaja solo con `#dersDetay`.

## Fase 2
- `scraper_ec_tr_sakarya01.py`: elimina Dersin Koordinatörü, Dersi Verenler, Dersin Yardımcıları y Destekleyen Eğitmen; tablas de resultados de aprendizaje (con métodos de enseñanza/medición), plan semanal, referencias, evaluación (con porcentajes) y carga de trabajo conservadas. 112/112 escritos. «Ön koşul» vacío en muchas fichas = hecho del origen (prerequisites=false).
