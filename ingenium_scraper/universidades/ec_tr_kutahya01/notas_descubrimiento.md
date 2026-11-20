# ec_tr_kutahya01 — Kütahya Dumlupınar Üniversitesi (Makine Mühendisliği)

- Hint `yuob.dpu.edu.tr/en` = oficina internacional de la propia DPU (dominio correcto). Dominio oficial `dpu.edu.tr` y subdominios (`birimler`, `obs`, `muhendislik`…).
- **Bloqueo de red**: todos los hosts de `dpu.edu.tr` rechazan la conexión (WinError 10061) o expiran, y algunos subdominios ni resuelven (DNS). Regla de parada → catálogo `parcial` vacío, sin Fase 2.
- La búsqueda web indica que Makine Mühendisliği se imparte en la Simav Teknoloji Fakültesi y que los PDF de departamento están en `birimler.dpu.edu.tr/app/views/panel/ckfinder/userfiles/…`; no se pudo verificar nada de esto.
- Pendiente: reintentar desde otra red; si responde, buscar el Bologna (OBS/«Bilgi Paketi») o el plan PDF de Simav Teknoloji Fakültesi.

## Segunda pasada (RESUELTA)
- Los hosts de dpu.edu.tr ya responden. OBS Bologna/Proliz: obs.dpu.edu.tr/oibs/bologna/ (sin robots.txt, 404). Lista de programas: unitSelection.aspx?type=lis&lang=en. Programa: Mechanical Engineering, Simav Teknoloji Fak. (curUnit=22, curSunit=90906313, diurno, currículo 2024; 8 semestres). El PDF de birimler.dpu.edu.tr cuelga de /app/views/panel/ckfinder/, vetado por robots: no se usa.
- Discover/scraper = copia del de Zonguldak con otro host/curSunit. 96 filas (42 obligatorias + 54 optativas), 96 Markdown. Docencia en turco, fichas en inglés.
