---
{
 "course_code": "IGENI-EC0924",
 "course_name": "FAO Surfacique",
 "institution_slug": "ec_f_tarbes03",
 "source_url": "https://www.enit.fr/_attachment/nouvel-article-75/IGENI-M-S09.pdf?download=true",
 "source_language": "fr",
 "ects_catalog": null,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-18T08:57:44",
 "content_sha256": "197bffd3954f4bdede190d54fca8ba4b6fc09208255c3064b72db92c59699374"
}
---

# FAO Surfacique [IGENI-EC0924]
Code EC IGENI-EC0924
Code UE IGENI-UE0902
## Présentation
Nom de l’EC FAO Surfacique
Format Heures
CM 4 H
TD 4 H
TP 16 H
Projet encadré H
Projet en autonomie H
Total 24 heures
## Acquis d’apprentissage visés
À l’issue du module, l’étudiant sera capable de concevoir des gammes de fabrication pour des pièces complexes,
en garantissant la faisabilité technique (accessibilité outil, rigidité machine) et la performance économique (coût
matière, productivité).
At the end of the module, the student will be able to design manufacturing process plans for complex parts,
ensuring both technical feasibility (tool accessibility, machine rigidity) and economic performance (material cost,
productivity).
## Modalités d’évaluation
Formule d’évaluation (1*PJ1+1*RAP1)/2
## Langue d’enseignement
Langue English friendly
## Objectifs de la formation visés
L’objectif de cet enseignement est de maîtriser les méthodes de conception et de fabrication de formes gauches
(surfaces complexes non développables) en intégrant des contraintes industrielles critiques : tolérances géométriques
serrées (ISO 1101) et exigences d’état de surface (rugosité Ra < 0,8 µm, absence de réveil de matière). Les étudiants
apprendront à modéliser géométriquement ces surfaces (NURBS, maillages STL) via des logiciels de CFAO (CATIA,
PowerMill), puis à générer des trajectoires d’outil optimisées pour l’usinage 5 axes.
Deux stratégies clés seront approfondies :
 L’usinage en bout (fraise en position normale à la surface), idéal pour les cavités profondes et les angles
fermés.
 L’usinage roulant (orientation dynamique de l’outil), adapté aux profils aérodynamiques ou biomédicaux.
Une attention particulière sera portée aux interactions procédé/qualité : analyse des défauts induits par les vibrations
(marquage en balayage), compensation thermique des machines, et influence des paramètres de coupe sur
l’écrouissage superficiel.
Ces concepts seront appliqués lors de la réalisation d’une pièce projet (exemple : pale de turbine ou implant
orthopédique), où les étudiants devront :
Définir un plan de tolérancement fonctionnel en lien avec le cahier des charges.
Choisir une stratégie d’usinage équilibrant temps-cycle, usure outil et finition.
Valider expérimentalement la qualité via une machine à mesurer tridimensionnelle (MMT) et un profilomètre 3D.
Course Objective
This course aims to master the methods for designing and manufacturing non-developable surfaces (complex, non-
flattenable geometries) while integrating critical industrial constraints: tight geometric tolerances (ISO 1101) and
surface finish requirements (roughness Ra < 0.8 µm, absence of material pull-up). Students will learn to geometrically
model these surfaces (NURBS, STL meshes) using CAD/CAM software (CATIA, PowerMill) and generate optimized
toolpaths for 5-axis machining.
Key Strategies
 End milling (tool perpendicular to the surface): Ideal for deep cavities and tight corners.
 Contour milling (dynamic tool orientation): Suited for aerodynamic profiles or biomedical implants.
Process-Quality Interactions
Special attention will be given to:
 Vibration-induced defects (e.g., chatter marks)
 Machine thermal compensation
 Impact of cutting parameters on surface work-hardening
Project Implementation
Students will apply these concepts to a project piece (e.g., turbine blade or orthopedic implant), requiring them to:
1. Define a functional tolerance plan aligned with specifications.
2. Select a machining strategy balancing cycle time, tool wear, and finish quality.
3. Validate quality experimentally using a coordinate measuring machine (CMM) and 3D profilometer.
## Contenus
1. Modèles CAO de surfaces gauches
Bézier :
- Définition mathématique via points de contrôle (équation polynomiale)
- Applications : design automobile (carrosseries), aéronautique (profils d'aile)
- Limites : difficulté de contrôle local sur la courbe
B-splines :
- Généralisation des Bézier avec vecteurs de nœuds pour un contrôle localisé
- Avantage : modification d'un segment sans affecter toute la surface
NURBS (Non-Uniform Rational B-Splines) :
- Modèle standard en CAO (CATIA, Siemens NX)
- Capacité à représenter formes analytiques (cercles) et surfaces libres
- Gestion des poids associés aux points de contrôle pour ajustement fin
2. Techniques CAO pour surfaces gauches (CATIA V5)
Outils principaux :
- Générateur de formes : Multi-Sections, Sweep, Blend
- Repair Assistant : Correction des discontinuités (G0 à G3)
- Connect Checker : Analyse des écarts entre surfaces
Bonnes pratiques :
- Utilisation de continuité G2/G3 pour transitions fluides (design aérodynamique)
- Optimisation des maillages via Simplification pour FAO
3. Stratégies d'usinage (3 à 5 axes)
Optimisation :
- Z-Level pour poches profondes
- Fraisage roulant 5 axes (outil tangentiel) pour intégrité métallurgique
4. Techniques FAO 5 axes (CATIA V5)
Workflow :
1. Définition des axes machines (tournage/fraisage)
2. Calcul de trajectoire :
- Contournage libre avec contrôle de l'angle de lead/lag
- Avoidance automatique des collisions (module Prismatic Machining)
3. Post-processing : Adaptation aux contrôleurs machines (ex : FANUC)
Cas critique :
- Usinage de turbines en Inconel avec compensation thermique intégrée
5. Étude de cas : Pièce "projet"
Exemple : Pale de turbine
- Étape 1 : Modélisation NURBS dans Generative Shape Design
- Étape 2 : Stratégie Swarf Machining (5 axes) pour flancs convexes
- Étape 3 : Vérification par Analyse de tolérancement (écarts < 5µm)
Résultats :
- Réduction de 40% du temps d'usinage vs. 3+2 axes
- Rugosité Ra < 0.8 µm sans polissage
6. Projet FAO surfacique
Maquette pédagogique :
- Phase 3 axes :
- Surfaçage avec Z-Level Roughing
- Détourage profilé (tolérance ±0.05 mm)
- Phase 5 axes :
- Multi-Axis Pocket pour cavités complexes
- Simulation des efforts de coupe via Abaqus
Livrables :
- Rapport comparatif temps/qualité entre méthodes
- Bibliothèque d'outils CATIA réutilisable (fraise boule, torique)
1. CAD Models of Non-Developable Surfaces
Bézier:
 Mathematical definition via control points (polynomial equations).
 Applications: Automotive design (bodywork), aerospace (wing profiles).
 Limitations: Difficulty in localized curve control.
B-splines:
 Generalization of Bézier curves with knot vectors for localized control.
 Advantage: Segment modification without affecting the entire surface.
NURBS (Non-Uniform Rational B-Splines):
 Industry-standard CAD model (CATIA, Siemens NX).
 Ability to represent analytical shapes (circles) and freeform surfaces.
 Weight management for control points to fine-tune adjustments.
2. CAD Techniques for Non-Developable Surfaces (CATIA V5)
Primary Tools:
 Shape Generator: Multi-Sections, Sweep, Blend.
 Repair Assistant: Correct discontinuities (G0 to G3).
 Connect Checker: Analyze gaps between surfaces.
Best Practices:
 Use G2/G3 continuity for smooth transitions (aerodynamic design).
 Optimize meshes via Simplification for CAM.
3. Machining Strategies (3 to 5 Axis)
Optimization:
 Z-Level for deep pockets.
 5-Axis Contour Milling (tangential tool) for metallurgical integrity.
4. 5-Axis CAM Techniques (CATIA V5)
Workflow:
1. Machine Axis Definition (turning/milling).
2. Toolpath Calculation:
  - Free Contouring with lead/lag angle control.
  - Automatic collision avoidance (Prismatic Machining module).
3. Post-Processing: Adaptation to machine controllers (e.g., FANUC).
Critical Case:
 Machining Inconel turbines with integrated thermal compensation.
5. Case Study: "Project" Part
Example: Turbine Blade
 Step 1: NURBS modeling in Generative Shape Design.
 Step 2: Swarf Machining strategy (5-axis) for convex flanks.
 Step 3: Tolerance analysis verification (<5µm deviations).
Results:
 40% reduction in machining time vs. 3+2 axis.
 Ra roughness <0.8 µm without polishing.
6. Surface CAM Project
Pedagogical Mock-Up:
 3-Axis Phase:
  - Facing with Z-Level Roughing.
  - Profile cutting (±0.05 mm tolerance).
 5-Axis Phase:
  - Multi-Axis Pocket for complex cavities.
  - Cutting force simulation via Abaqus.
Deliverables:
 Comparative time/quality report between methods.
 Reusable CATIA tool library (ball nose, toroidal cutters).
## Méthodes et/ou moyens pédagogiques
Cet enseignement se base sur une démarche projet. Les élèves doivent créer une pièce, établir gamme de fabrication
et la programmation, réaliser l’usinage et enfin identifier les éventuelles différences entre programmation et réalité.
This course is based on a project-based approach. Students are required to design a part, define the manufacturing
process and programming, carry out the machining, and finally identify any discrepancies between the programming
and the actual outcome.
## Prérequis
Méthodes de fabrication (tournage, fraisage, perçage... Outils coupants, paramètres de
coupe, outillage), Mise en oeuvre des machines-outils à commande numérique,
programmation en commande numérique, Fabrication assistée par Ordinateur (FAO 2,5 et
3 axes).
Prérequis
Manufacturing methods (turning, milling, drilling... cutting tools, cutting parameters,
tooling), operation of CNC machine tools, CNC programming, Computer-Aided
Manufacturing (CAM for 2.5- and 3-axis machining).
## Travail personnel hors présentiel
Volume horaire 10 Heures
Finaliser la programmation
Réaliser le rapport
Type de travail
Finalize the programming
Write the report
## Ressources bibliographiques
- Modélisation et construction de surface pour la CFAO, Jean-Claude LEON, Bibliothèque ENIT 516.3 LEO.
- B-splines, R.H. BARTELS, Bibliothèque ENIT 516.3 BAR.
- L'utilisation des courbes et surfaces en CAO, Pierre Bézier, Bibliothèque ENIT 516.3 BEZ.
- Fabrication assistée par ordinateur, Alain BERNARD, Lavoisier, 2003.
- L'usinage 5 axes, Eric GALLET et Christophe DESPLATZ, Publications CETIM, 2004.
