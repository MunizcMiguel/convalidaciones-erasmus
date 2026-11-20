---
{
 "course_code": "IGENI-EC0973SI",
 "course_name": "Commande Basée-Vision",
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
 "content_sha256": "0b76372b6b42c4689d9de39d1c2176cd4c5dc2fac6f25ca150c9c74123bbb25e"
}
---

# Commande Basée-Vision [IGENI-EC0973SI]
Code EC IGENI-EC0973SI
Code UE IGENI-UE0907SI
## Présentation
Nom de l’EC Commande Basée-Vision
Format Heures
CM 8 H
TD H
TP 8 H
Projet encadré H
Projet en autonomie H
Total 16 heures
## Acquis d’apprentissage visés
À l’issue de l’EC, les étudiants seront capables, dans leur futur métier, d’implémenter des techniques
d’asservissement visuel basées sur des approches 2D et 3D en robotique, en utilisant des données issues de caméras
pour commander les mouvements de robots manipulateurs, en montrant qu’ils peuvent garantir la précision et la
stabilité dans des environnements dynamiques.
At the end of the course unit, students will be able, in their future careers, to implement visual servoing techniques
based on 2D and 3D approaches in robotics, using camera data to control the movements of robotic manipulators,
demonstrating their ability to ensure precision and stability in dynamic environments.
## Modalités d’évaluation
Formule d’évaluation (1*DS1+1*TP1)/2
## Langue d’enseignement
Langue Français/French
## Objectifs de la formation visés
Domaine cognitif :
 Comprendre les principes fondamentaux de l’asservissement visuel en robotique, incluant les approches 2D
et 3D.
 Identifier les différences entre les techniques d’asservissement visuel en position (PBVS) et en image (IBVS),
et comprendre leur impact sur les performances robotiques.
 Acquérir des notions de modèle d’interaction (Jacobienne d’interaction) entre l’espace image et l’espace
réel (3D) : cas d’étude d’un point.
Domaine pragmatique :
 Savoir implémenter des algorithmes d’asservissement visuel, à partir de librairies existantes, dans des
environnements de simulation
 Réaliser des tests pour valider les algorithmes d’asservissement visuel et évaluer leur efficacité dans le suivi
de trajectoires ou la manipulation d’objets.
 Intégrer des capteurs de vision dans un système robotique et les exploiter pour des applications de
commande dynamique du robot.
Domaine affectif :
 Être conscient des enjeux liés à l’utilisation de l’asservissement visuel dans des environnements industriels,
notamment en termes de précision, sécurité et robustesse.
 Développer une attitude critique et une réflexion sur les choix méthodologiques et technologiques dans la
conception des systèmes de commande basés sur la vision.
 Avoir conscience des implications pratiques des décisions techniques pour la stabilité et la performance des
systèmes robotiques en environnement dynamique.
Cognitive domain:
 Understand the fundamental principles of visual servoing in robotics, including 2D and 3D approaches.
 Identify the differences between position visual servoing (PBVS) and image visual servoing (IBVS) techniques,
and understand their impact on robotic performance.
 Acquire notions of interaction model (Jacobian interaction) between image space and real space (3D): case
study of a point.
Pragmatic domain:
- Know how to implement visual servoing algorithms, from existing libraries, in simulation environments
- Carry out tests to validate visual servoing algorithms and evaluate their effectiveness in tracking trajectories
or manipulating objects.
- Integrate vision sensors into a robotic system and use them for dynamic robot control applications.
Affective domain:
- Be aware of the issues related to the use of visual servoing in industrial environments, particularly in terms of
precision, safety and robustness.
- Develop a critical attitude and reflection on the methodological and technological choices in the design of
vision-based control systems.
- Be aware of the practical implications of technical decisions for the stability and performance of robotic
systems in dynamic environments.
## Contenus
Cours introductif général (1h)
- Vue générale de l’apprentissage et des objectifs du cours
- Présentation des Apprentissages Par Problème (APP)
- Introduction aux principes de la commande basée vision et à ses applications en robotique
APP 1 : Introduction à l’asservissement visuel (2h)
1.1 Principes fondamentaux de l’asservissement visuel : définitions et concepts clés
1.2 Différences entre l’asservissement en image (IBVS) et en position (PBVS)
1.3 Configurations possibles des systèmes de vision pour l’asservissement visuel
APP 2 : Techniques d’asservissement visuel 3D (2h)
3.1 Approches d’asservissement visuel 3D : principes et intégration des coordonnées spatiales
3.2 Suivi de trajectoires basé sur l’asservissement visuel 3D : conception et implémentation
3.3 Exemple de formalisation d’une matrice d’interaction (lien image-3D) d’un point
APP 3 : Techniques d’asservissement visuel 2D (2h)
2.1 Asservissement visuel basé sur des caractéristiques 2D : principes et algorithmes
2.2 Mise en œuvre de l’asservissement visuel 2D pour le suivi de trajectoires
2.3 Analyse des limites et des performances des approches 2D
2.4 Comparaison des performances des techniques 3D par rapport aux approches 2D : précision, robustesse et
applications
Cours de restructuration (1h)
- Synthèse globale des APPs et des concepts abordés
- Discussions et réponses aux questions soulevées lors des phases de retour des APPs
- Évaluation des acquis d’apprentissage visés (AAVs) et perspectives d’applications professionnelles
TP n°1 : Implémentation de l’asservissement visuel 3D (4h TP)
Utilisation de Matlab/Simulink pour programmer un asservissement visuel 3D (Toolbox de P. Corke)
Test de suivi de 4 points (carré comme feature)
Tests de point de départ différents, de taille de feature différentes,
TP n°2 : Implémentation de l’asservissement visuel 2D (4h TP)
Utilisation de Matlab/Simulink pour programmer un asservissement visuel 2D (Toolbox de P. Corke)
Test d’un programme sous forme de schéma block (Simulink)
Test de configuration différentes de l’asservissement visuel 2D (différents départ, taille de feature,…)
Test de la robustesse de l’asservissement visuel 2D : Mauvaise initialisation de la profondeur, perte de la vision,…
General introduction course (1h)
- Overview of the learning and course objectives
- Presentation of Problem-Based Learning (PBL)
- Introduction to the principles of vision-based control and its applications in robotics
PBL 1: Introduction to visual servoing (2h)
1.1 Fundamental principles of visual servoing: definitions and key concepts
1.2 Differences between image servoing (IBVS) and position servoing (PBVS)
1.3 Possible configurations of vision systems for visual servoing
PBL 2: 3D visual servoing techniques (2h)
3.1 3D visual servoing approaches: principles and integration of spatial coordinates
3.2 Trajectory tracking based on 3D visual servoing: design and implementation
3.3 Example of formalization of an interaction matrix (image-3D relationship) of a point
PBL 3: 2D visual servoing techniques (2h)
2.1 Visual servoing based on 2D features: principles and algorithms
2.2 Implementation of 2D visual servoing for trajectory tracking
2.3 Analysis of the limits and performances of 2D approaches
2.4 Comparison of the performances of 3D techniques compared to 2D approaches: precision, robustness and
applications
Restructuration course (1h)
- Overall synthesis of APPs and concepts covered
- Discussions and answers to questions raised during the APPs feedback phases
- Assessment of targeted learning outcomes (AAVs) and prospects for professional applications
PT n°1: Implementation of 3D visual servoing (4h)
Use of Matlab/Simulink to program a 3D visual servoing (Toolbox by P. Corke)
4-point tracking test (square as a feature)
Tests of different starting points, different feature sizes,
PT n°2: Implementation of 2D visual servoing (4h)
Using Matlab/Simulink to program a 2D visual servoing (Toolbox by P. Corke)
Testing a program in the form of a block diagram (Simulink)
Testing different configurations of the 2D visual servoing (different starts, feature size, etc.)
Testing the robustness of the 2D visual servoing: Bad initialization of depth, loss of vision, etc.
Apprentissage par Problème et par Projet (APP) :
Chaque APP est structuré en trois phases :
1. Phase aller (1h) : Travail en petit groupe tutoré par un enseignant pour introduire la problématique
2. Travail personnel individuel (≈ 4h) : Étude autonome pour approfondir les notions et résoudre les
problématiques posées
3. Phase retour (1h) : Travail en petit groupe avec un enseignant pour présenter les résultats, discuter et
valider les apprentissages
 Séances en petit groupe, encadrées par un tuteur, pour favoriser les échanges et la réflexion collaborative.
 Utilisation de carnets d’apprentissage pour documenter les activités, les analyses et les apprentissages visés.
 Cours de restructuration (1h) pour synthétiser les concepts clés et répondre aux questions soulevées lors des
APPs.
Problem-Based and Project-Based Learning (PBL):
Each PBL is structured in three phases:
1. Outbound phase (1 hour): Work in a small group tutored by a teacher to introduce the problem
2. Individual personal work (≈ 4 hours): Independent study to deepen the concepts and resolve the problems
posed
3. Return phase (1 hour): Work in a small group with a teacher to present the results, discuss and validate the
learning
- Small group sessions, supervised by a tutor, to encourage exchanges and collaborative reflection.
- Use of learning notebooks to document the activities, analyses and targeted learning.
- Restructuring course (1 hour) to summarize the key concepts and answer the questions raised during the PBLs.
## Prérequis
- Introduction à la robotique
- Notions de modèle géométrique
- Principe de planification et de commande dans les espaces robotique (articulaire,
opérationnel)
- Connaissance des principes de commande automatique (PID,…)
Prérequis
- Introduction to robotics
- Concepts of kinematic model
- Principle of planning and control in robotic spaces (Joint, operational)
- Knowledge of automatic control principles (PID,…)
## Travail personnel hors présentiel
Volume horaire 12 Heures
- Travail de groupe en collaboration : Discussions, échange, argumentation
- Travail en autonomie pour préparer les séances retours
- présentation de synthèse de travail de groupe
Type de travail
- Collaborative group work: Discussions, exchange, argumentation
- Independent work to prepare the feedback sessions
- Presentation of group work summary
## Ressources bibliographiques
1. Peter I. Corke. 1997. Visual Control of Robots: High-Performance Visual Serving. John Wiley & Sons, Inc., USA.
2. Online resources given during the PBL sessions:
a. Cours de Alessandro De Luca : http://www.diag.uniroma1.it/deluca/rob2_en/17_VisualServoing.pdf
b. Cours de François Chaumette (GdR Robotique) : https://www.gdr-
robotique.org/cours_de_robotique/online/Chaumette_Visual-Servoing/Chaumette_Visual-Servoing.pdf
c. Cours de Philippe Martinet (GdR Robotique) : https://www.gdr-
robotique.org/cours_de_robotique/online/Martinet_Visual-Servoings/Martinet_Visual-Servoings_slides.pdf,
d. Cours de Jaques Gangloff (GdR Robotique) : https://www.gdr-
robotique.org/cours_de_robotique/?id=42d45e5762b80afd925329f86b992718
