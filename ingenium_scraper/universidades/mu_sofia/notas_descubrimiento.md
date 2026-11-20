# Medical University of Sofia (MU-Sofia) — notas de descubrimiento

**Resultado: `estado: "n/a"`.** MU-Sofia no imparte ningún grado de ingeniería ni de tecnología (tampoco ingeniería biomédica ni técnica médica). Catálogo con `asignaturas: []`; Fase 2 no aplica.

## Fuentes (todas vía PoliteClient, en `raw_cache/`)

1. **Páginas oficiales "Специалности" (especialidades)**, en búlgaro, una por unidad, enlazadas desde el menú de `https://mu-sofia.bg/obuchenie/specialnosti/fakultet-medicina/`:
   `fakultet-medicina/`, `fakultet-dentalna-medicina/`, `farmacevtichen-fakultet/`, `fakultet-obstestveno-zdrave/`, `medicinski-kolezh/`, `filial-vraca/` (bajo `https://mu-sofia.bg/obuchenie/specialnosti/`).
   Se prefirió la versión búlgara: la inglesa (`/en/admission/...`) está incompleta (la de Salud Pública sale en búlgaro y la de Medicina describe solo el plan de 6 años).
2. **PDF oficial de acreditación de programas** — "Приложение 1. Акредитирани професионални направления и специалности…", enlazado desde `https://mu-sofia.bg/nauka/akreditacii/progr-akreditacia/` (`/wp-content/uploads/2023/02/AKPN-i-spetz-ot-RP-v-MU-Sofia-1.2.23.pdf`). Da los campos profesionales acreditados según el clasificador búlgaro (5.x = Ciencias técnicas / ingeniería; 7.x = Salud y deporte).

robots.txt de `mu-sofia.bg`: solo `Disallow: /wp-admin/` → todo lo usado está permitido. No se accedió a otros hosts.

## Evidencia (generada por `discover_mu_sofia.py` → `evidencia_programas.json`)

Campos profesionales acreditados: **7.1 Medicina, 7.2 Medicina dental, 7.3 Farmacia, 7.4 Salud pública, 7.5 Cuidados de salud.** Ninguno 5.x.

Especialidades publicadas (26; 18 de primer ciclo):

| Unidad | Especialidad (traducción) | Grado |
|---|---|---|
| Facultad de Medicina | Medicina | máster integrado |
| Facultad de Medicina Dental | Medicina dental | máster integrado |
| Facultad de Farmacia | Farmacia; Evaluación de tecnologías sanitarias con farmacoeconomía | máster |
| Facultad de Salud Pública | Salud pública y gestión sanitaria; Gestión de cuidados de salud; Medicina del trabajo y capacidad laboral | bachelor + máster |
| Facultad de Salud Pública | Gestión estratégica de la actividad farmacéutica | máster |
| Facultad de Salud Pública | Matrona; Enfermería; Asistente médico; Kinesiterapia | bachelor |
| Filial Vratsa | Matrona; Enfermería; Asistente médico | bachelor |
| Colegio Médico "Y. Filaretova" | Técnico de laboratorio médico; Técnico de radiología; Protésico dental; Rehabilitador; Auxiliar de farmacia; Inspector de salud pública; Masajista (personas con discapacidad visual); Cosmético médico | professional bachelor (3 años) |

Los programas más "técnicos" (Técnico de radiología, Protésico dental, Técnico de laboratorio) son grados profesionales sanitarios del campo 7.5, no de ingeniería; "Evaluación de tecnologías sanitarias" es un máster de farmacoeconomía. Ninguno es asimilable a Ingeniería Mecánica ni sirve como "grado de ingeniería más cercano".

## Cómo decide el script

- Recorre el menú de especialidades (no hay URLs de unidad tecleadas a mano), extrae las cabeceras `СПЕЦИАЛНОСТ „…" - ОБРАЗОВАТЕЛНО-КВАЛИФИКАЦИОННА СТЕПЕН „…"` (Medicina y Dental van sin comillas: segundo regex) y el grado; el Colegio Médico declara "професионален бакалавър" en la introducción.
- Parsea los códigos de campo del PDF (`^\d\.\d\.`). El nombre del campo comparte línea con el de la especialidad en la tabla; se elige la variante más corta tras cortar en " - ".
- `n/a` si no hay campos 5.x ni términos de ingeniería (ИНЖЕНЕР, БИОМЕДИЦИНСК, ТЕХНИКА, ЕЛЕКТРОН, МЕХАТРОН) en los nombres; si los hubiera, pondría `parcial` y pediría revisión manual.
- Re-ejecución: solo caché (9 recursos).

## Trampas

- El PDF se titula "…от регулираните професии" (profesiones reguladas) pero incluye también campos no regulados (7.4, Kinesiterapia), por lo que se considera la lista completa; las páginas HTML lo corroboran.
- Algunos enlaces del menú apuntan a la misma URL con otro texto ("Е-Портал"): el nombre de la unidad se toma del `<title>` de la propia página.
- Sin comprobar: posibles programas de posgrado/doctorado técnicos (irrelevantes para primer ciclo).
