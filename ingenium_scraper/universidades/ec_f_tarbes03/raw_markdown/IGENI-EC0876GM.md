---
{
 "course_code": "IGENI-EC0876GM",
 "course_name": "Robotisation en fabrication mécanique",
 "institution_slug": "ec_f_tarbes03",
 "source_url": "https://www.enit.fr/_attachment/nouvel-article-75/IGENI-M-S08.pdf?download=true",
 "source_language": "fr",
 "ects_catalog": null,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-18T08:57:36",
 "content_sha256": "6ad935dcaa84877cc00606a426a82e949eb79a1bf9612c184c041d910ce394ff"
}
---

# Robotisation en fabrication mécanique [IGENI-EC0876GM]
Code EC IGENI-EC0876GM
Code UE IGENI-UE0807GM
## Présentation
Nom de l’EC Robotisation en fabrication mécanique
Format Heures
CM 4 H
TD 4 H
TP 4 H
Projet encadré H
Projet en autonomie H
Total 12 heures
## Acquis d’apprentissage visés
L’objectif de cet enseignement est de fournir aux étudiants les méthodes et outils nécessaires à la mise en œuvre
d’une fabrication robotisée performante. Il s’agit notamment d’aborder les caractéristiques des robots industriels,
les techniques de programmation associées, ainsi que les méthodes d’évaluation de leurs performances dans
différents contextes de production : usinage, parachevement et assemblage. En lien avec des applications
industrielles concrètes, le comportement de la cellule robotisée est analysé afin de mieux comprendre son
influence sur la qualité des pièces produites, et d’optimiser le choix des trajectoires ainsi que les paramètres de
commande du procédé.
À l’issue de cette formation, l’étudiant sera en mesure d’identifier et de comparer différentes stratégies de
fabrication robotisée, d’en évaluer les bénéfices potentiels, et de prendre en compte les contraintes techniques et
organisationnelles liées à leur mise en œuvre en milieu industriel.
The aim of this course is to provide students with the methods and tools needed to implement high-performance
robotized manufacturing. In particular, it covers the characteristics of industrial robots, associated programming
techniques, and methods for evaluating their performance in different production contexts: machining, finishing
and assembly. Based on real-life industrial applications, the behavior of the robotic cell is analyzed to better
understand its influence on the quality of the parts produced, and to optimize the choice of trajectories and
process control parameters.
On completion of this course, students will be able to identify and compare different robotized manufacturing
strategies, evaluate their potential benefits, and take into account the technical and organizational constraints
linked to their implementation in an industrial environment.
## Modalités d’évaluation
Formule d’évaluation (1*TP1)/1
## Langue d’enseignement
Langue English friendly
## Objectifs de la formation visés
L’usinage robotisé représente une alternative flexible et économique aux machines-outils conventionnelles, notamment
pour les grandes pièces ou les matériaux complexes. Toutefois, son déploiement industriel reste freiné par plusieurs
verrous scientifiques. Le principal défi réside dans la faible rigidité intrinsèque des robots industriels, qui entraîne des
déformations structurelles significatives sous l'effet des efforts de coupe, impactant directement la précision
géométrique et l’état de surface. À cela s’ajoutent les vibrations auto-entretenues (chatter), plus difficiles à maîtriser en
raison des variations de raideur selon la position du bras robotisé dans l’espace de travail. La dynamique propre du
robot, couplée aux lois de commande souvent conçues pour des tâches de manutention et non d’usinage, limite
également les capacités d’adaptation en temps réel aux conditions de coupe. Sur le plan de la modélisation, il devient
nécessaire de développer des jumeaux numériques intégrant à la fois la cinématique non linéaire, la flexibilité
articulaire et les interactions outil-matière. Enfin, l’identification en ligne des paramètres d’usinage optimaux, tenant
compte des zones de raideur variable et des phénomènes de résonance, constitue un enjeu majeur pour assurer une
qualité constante et prédictive du procédé robotisé.
L’objectif de cet enseignement est de reprendre l’ensemble de ces verrous et de donner les clefs aux étudiants.
Robotic machining represents a flexible, cost-effective alternative to conventional machine tools, particularly for large
parts or complex materials. However, its industrial deployment remains hampered by a number of scientific obstacles.
The main challenge lies in the low intrinsic rigidity of industrial robots, which leads to significant structural deformation
under the effect of cutting forces, directly impacting geometric precision and surface finish. Added to this are self-
sustaining vibrations (chatter), which are more difficult to control due to variations in stiffness depending on the position
of the robotic arm in the workspace. The robot's own dynamics, coupled with control laws often designed for handling
rather than machining tasks, also limit its ability to adapt in real time to cutting conditions. In terms of modeling, it is
becoming necessary to develop digital twins integrating non-linear kinematics, joint flexibility and tool-material
interactions. Finally, the on-line identification of optimal machining parameters, taking into account variable stiffness
zones and resonance phenomena, is a major challenge to ensure consistent and predictive quality of the robotized
process.
The aim of this course is to take up all these issues and provide students with the keys.
## Contenus
Les robots industriels adoptent différentes configurations mécaniques en fonction des applications :
 Robots articulés (6 axes) pour usinage 3D complexe et soudage FSW
 Robots SCARA pour assemblage haute précision dans l'électronique
 Robots parallèles (Delta) pour opérations rapides de pick-and-place
 Robots collaboratifs équipés de capteurs de force pour le parachèvement
Tâche Configuration robotique Exemple d'application
Usinage Robot articulé + broche motorisée Fraisage de pièces aéronautiques
Soudage FSW Robot lourd (50kg+ de charge utile) Assemblage de réservoirs spatiaux
Polissage Cobot + effecteur adaptatif Finition de pièces moulées
Opérations de fabrication robotisées
Les cellules robotisées modernes intègrent :
 Opérations hybrides combinant usinage et contrôle qualité inline
 Soudage par friction malaxage (FSW) pour assemblages métallurgiques sans fusion
 Parachèvement intelligent avec systèmes de vision 3D et IA
 Chargement/Déchargement de machines-outils avec gestion automatique des outils
Programmation des robots
Méthodes clés :
1. Programmation hors-ligne avec logiciels comme NX CAM pour simulation préalable
2. Enseignement direct via pendulets tactiles pour ajustements fins
3. Programmation adaptative utilisant des capteurs de force/torque pour l'usinage
4. Bibliothèques de mouvements pré-optimisées pour le FSW
Exemple de workflow :
text
Mise en œuvre d'une fabrication robotisée
Processus d'intégration :
1. Analyse des contraintes process (temps cycle, précision)
2. Conception de cellules modulaires avec interfaces standardisées
3. Intégration de systèmes de vision et capteurs IoT
4. Validation par jumeau numérique avant déploiement
Points critiques :
 Adéquation robot/effecteur (couple, vitesse) pour le FSW
 Gestion des vibrations en usinage robotisé
 Sécurisation des flux matières dans les cellules
Comportements attendus
 Précision : ≤ 0.05mm pour opérations de finition
 Robustesse : Fonctionnement 24/7 avec MTBF > 4000 heures
 Adaptabilité : Reconfiguration rapide pour petites séries
 Sûreté : Arrêt d'urgence en < 200ms pour cobots
Étude de cas : Parachèvement et soudage FSW
Application Airbus :
 Robot KUKA KR 1000 Titan équipé d'outil FSW
 Soudage de longerons d'aile en Al-Li à 3m/min
 Réduction de 70% des défauts comparé au soudage TIG
Solution Proxinnov :
 Cellule de polissage robotisé avec compensation thermique
 Gain de productivité : 40% sur pièces composites
TP d'application
La plateforme intègre :
 Robots ABB IRB 6700 pour usinage lourd
 Cellule FSW avec robot Yaskawa Motoman HP500
 Système de mesure tridimensionnel Zeiss
Déroulé type :
1. Modélisation cinématique inverse d'un robot 6 axes
2. Programmation de trajectoires d'usinage sur pièce complexe
3. Mise en œuvre de paramètres FSW (rotation 800-1500 RPM, avance 2-5mm/s)
4. Analyse métallographique des joints soudés
Cette approche pédagogique permet d'aborder les interactions robot/procédé critiques pour l'industrie aérospatiale et
énergétique . Les travaux pratiques exploitent les capacités uniques de la plateforme COMPOSITADOUR pour la
fabrication additive robotisée
Industrial robots come in a variety of mechanical configurations, depending on the application:
 Articulated robots (6 axes) for complex 3D machining and FSW welding
 SCARA robots for high-precision assembly in electronics
 Parallel robots (Delta) for fast pick-and-place operations
 Collaborative robots equipped with force sensors for finishing operations
Robotic manufacturing operations
Modern robotic cells integrate :
 Hybrid operations combining machining and inline quality control
 Friction stir welding (FSW) for non-melting metallurgical assemblies
 Intelligent completion with 3D vision and AI systems
 Machine tool loading/unloading with automatic tool management
Robot programming
Key methods:
1. Off-line programming with software such as NX CAM for preliminary simulation
2. Direct teaching via touch pendulums for fine adjustments
3. Adaptive programming using force/torque sensors for machining
4. Pre-optimized motion libraries for FSW
Example workflow:
text
Implementing robotic manufacturing
Integration process :
1. Analysis of process constraints (cycle time, precision)
2. Design of modular cells with standardized interfaces
3. Integration of vision systems and IoT sensors
4. Validation by digital twin before deployment
Critical points:
 Robot/effector suitability (torque, speed) for FSW
 Vibration management in robotic machining
 Securing material flows in cells
Expected behaviors
 Accuracy: ≤ 0.05mm for finishing operations
 Robustness: 24/7 operation with MTBF > 4000 hours
 Adaptability: Rapid reconfiguration for short production runs
 Safety: Emergency stop in < 200ms for cobots
Case study : Completion and FSW welding
Application Airbus:
 Robot KUKA KR 1000 Titan equipped with FSW tool
 Welding of Al-Li wing spars at 3m/min
 70% reduction in defects compared with TIG welding
Solution Proxinnov:
 Robotic polishing cell with thermal compensation
 Productivity gain: 40% on composite parts
Application TP
The platform integrates :
 ABB IRB 6700 robots for heavy-duty machining
 FSW cell with Yaskawa Motoman HP500 robot
 Zeiss three-dimensional measuring system
Typical sequence :
1. Inverse kinematic modeling of a 6-axis robot
2. Programming machining trajectories on a complex part
3. Implementation of FSW parameters (rotation 800-1500 RPM, feed 2-5mm/s)
4. Metallographic analysis of welded joints
This pedagogical approach addresses critical robot/process interactions for the aerospace and energy industries.
Practical work exploits the unique capabilities of the COMPOSITADOUR platform for robotized additive manufacturing.
Ce enseignement a pour objectif d’être au plus proche des besoins industriels. A cet effet, l’intervention est réalisée n
partenariat avec un indsutriel impliqué dans la maquette pédgogique.
The aim of this course is to be as close as possible to the needs of industry. To this end, the course is run in partnership
with an industrial partner involved in the pedagogical model.
## Prérequis
Méthodes de fabrication (tournage, fraisage, perçage... Outils coupants, paramètres de
coupe, outillage), Mise en oeuvre des machines-outils à commande numérique,
programmation en commande numérique, Fabrication assistée par Ordinateur (FAO)
Prérequis
Manufacturing methods (turning, milling, drilling... Cutting tools, cutting parameters,
tooling), CNC machine-tool operation, CNC programming, Computer-aided manufacturing
(CAM)
## Travail personnel hors présentiel
Volume horaire 4 Heures
Révision des cours
Rédaction du rapport
Type de travail
Course review
Report writing
## Ressources bibliographiques
Cliquez ici et entrez les ressources bibliographiques
