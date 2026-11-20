---
{
 "course_code": "PEM",
 "course_name": "Programmation Embarquée / Programming embedded systems",
 "institution_slug": "ec_f_poitier05",
 "source_url": "https://ensma.fr/wp-content/uploads/2025/02/Syllabus-FISE-ENSMA-A2-2025-2026-previsionnel.pdf",
 "source_language": "fr",
 "ects_catalog": null,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": false,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-20T08:23:48",
 "content_sha256": "3cd69be650e98814af290f5961936dccb8b91b7344357bd6e8993594136e13ce"
}
---

# Programmation Embarquée / Programming embedded systems

UE: A2 / Semestre 4 (UE4-2c, 9 ECTS la UE)

## Learning outcomes (Compétences attendues)

- Détecter les problèmes potentiels lors du ciblage des programmes embarqués sur différentes architectures
matérielles, nécessite les connaissances de :
◦ Grandes familles de calculateurs et leurs différences (32 vs 64 bits, utilisation de la pile d’appel, FPU,
architectures vectorielles) ;
◦ L’impact de l’architecture sur la représentation mémoire (tailles de représentation entiers, alignement sur les
mots mémoire, etc.)
◦ L’impact des optimisations locales sur la durée d’exécution (mémoires caches, RAM, pipeline, prefetch, etc.)
◦ Connaître les spécificités des processeurs multicœurs et pluricœurs
- Connaissance du fonctionnement bas niveau des programmes sur différentes architectures (8, 32, 64 bits
notamment pour architectures ARM, x86, etc.)

## Prerequisites (Pré-requis)

- Informatique Numérique (S1)
- Introduction aux Systèmes Embarqués (S1)
- Ingéniérie des Systèmes critiques (S3)

## Content (Contenu)

- Architectures matérielles
◦ Le goulot d’étranglement de la mémoire des architectures Harvard/von Neumann à nos jours (banques SDRAM)
et mémoires cache
◦ Le partitionnement mémoire par mémoire virtuelle
◦ Structure interne d’un processeur
- Architectures parallèles
◦ Hyper-threading
◦ Multicoeur
◦ Architecture MPSoC hétérogènes
◦ Pluricoeur
- Architectures logicielles
◦ RTOS vs GPOS
- Code bas niveau
◦ Compilation vers code assembleur et code machine
◦ Fonctionnement de la pile et du tas
◦ Différences architectures 32 bits et 64 bits
◦ Option de compilation et optimisation du code produit

## Bibliography (Bibliographie)

- E. Grolleau, J. Hugues, Y. Ouhammou, H. Bauer, « Introduction aux systèmes embarqués temps réel, Conception
et mise en œuvre », Dunod, 2018
- F. Cottet, E. Grolleau, S. Gérard, J. Hugues, Y. Ouhammou, S. Tucci -Piergiovanni, « Systèmes temps réel
embarqués - 2e édition, Spécification, conception, implémentation et validation temporelle », Dunod, 2014

## Learning outcomes (EN)

- Detect problems when porting a program on an embedded target
◦ Major computer families and their differences (32 vs. 64 bits, use of call stack, FPU, vector arc hitectures) ;
◦ The impact of architecture on memory representation (integer representation sizes, alignment on memory words,
etc.).
◦ The impact of local optimizations on runtime (caches, RAM, pipeline, prefetch, etc.).
◦ Knowledge of the specific features of multicore and multi-core processors.
- Knowledge of low -level program operation on different architectures (8, 32, 64 -bit, especially for ARM, x86
architectures, etc.).

## Prerequisites (Pré-requis)

Digital Information (S1), Introduction to Embedded Systems (S 1), Model -based system
engineering for critical systems (S3)

## Content (EN)

- Hardware architectures
- Parallel architectures (Hyper-threading, multicore, heterogeneous MPSoCs, manycore)
- Software architectures: RTOS vs GPOS
- Low-level code
Recommended reading:
- E. Grolleau, J. Hugues, Y. Ouhammou, H. Bauer, « Introduction aux systèmes embarqués temps réel, Conception
et mise en œuvre », Dunod, 2018
- F. Cottet, E. Grolleau, S. Gérard, J. Hugues, Y. Ouhammou, S. Tucci -Piergiovanni, « Systèm es temps réel
embarqués - 2e édition, Spécification, conception, implémentation et validation temporelle », Dunod, 2014
