# Besançon (UMLP, ex Univ. Franche-Comté) — Licence SPI, parcours Génie mécanique (Mécanique)

- Fuente: `https://formations.univ-fcomte.fr/sitemap.xml` (robots.txt: sin restricciones). Cada URL del árbol ODF/Ametys es nodo del plan; las hojas son fichas HTML por ELC/UE (ECTS, horas CM/TD/TP, MCC). El ID final (`M372PU8M`) es estable y se usa como código.
- Ramas usadas: S1 portail-3, S2 parcours SPI, S3/S4 "Mécanique et génie mécanique", S5/S6 "Parcours Mécanique" (ids MBGN*). Existen variantes MAXN* (cohorte anterior) y LAS no incluidas. 56 hojas, 30 ECTS por semestre = 180.
- Trampa: la titulación es una Licence SPI genérica (no existe "Licence Génie mécanique" separada); la web también publica PDF del plan (sin enlaces por UE).
- Limitación: solo 1 de 56 fichas (Chimie) tiene Description/Objectifs; el resto solo ECTS+horas+MCC → catálogo `parcial`.

## Fase 2
`scraper_ec_f_besanco01.py`: HTML → Markdown (quita miga de pan y botones). 56/56 escritos. Bloques: assessment en ~53; contents/learning_outcomes casi siempre ausentes (hecho de la fuente).
