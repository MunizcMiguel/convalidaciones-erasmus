# ec_i_milano02 — Politecnico di Milano

**Titulación:** Laurea in Ingegneria Meccanica (L-9), 180 CFU, Bovisa/Piacenza. **Catálogo parcial vacío; sin Fase 2** (regla de parada).

- Hosts: www.polimi.it y www.mecheng.polimi.it permiten; onlineservices.polimi.it (app Manifesti) permite pero la tabla de insegnamenti se carga por AJAX con sesión y no está en el HTML; las schede viven en www4.ceda.polimi.it (robots.txt Disallow total, PoliteClient lanza RobotsBlocked) y www11.ceda.polimi.it (DNS no resuelve).
- El plan de la web de la escuela es una imagen PNG.
- Para reintentar: habría que replicar las llamadas AJAX de onlineservices (no inspeccionadas) y encontrar una vía no bloqueada para las fichas; no se hizo.

## Segunda pasada (descartada)
- Fichas solo en www4.ceda.polimi.it (robots Disallow total); dati.polimi.it y didattica.polimi.it no resuelven DNS; www.polimi.it y www.mecheng.polimi.it permiten pero no exponen fichas ni plan en HTML. Sin vía permitida → `parcial` vacío.

## Tercera pasada (sigue `parcial`, 2026-11-20)
- Sin cambios en la regla de parada: las fichas solo existen en www4.ceda.polimi.it (robots Disallow total). Búsqueda web: no hay plan ni programas de asignatura en HTML/PDF de www.polimi.it, mecheng.polimi.it o ingindinf.polimi.it.
- Único PDF público útil (ingindinf.polimi.it/fileadmin/…/Esperienza_Studente_MEC_LT.pdf, permitido, 21 págs.): guía orientativa del grado (modalidades, stage 16 CFU, movilidad); NO incluye lista de insegnamenti ni programas. Descartado como fuente de catálogo.
