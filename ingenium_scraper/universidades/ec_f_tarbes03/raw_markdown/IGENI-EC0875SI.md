---
{
 "course_code": "IGENI-EC0875SI",
 "course_name": "Communication des systèmes informatiques",
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
 "content_sha256": "5a53aa22a0d165c18feecbffcf7249375352ba41b3cb75d1ff8a54b8c025c795"
}
---

# Communication des systèmes informatiques [IGENI-EC0875SI]
Code EC IGENI-EC0875SI
Code UE IGENI-UE0807SI
## Présentation
Format Heures
CM 6 H
TD H
TP 5 H
Projet encadré H
Projet en autonomie H
Total 11 heures
## Acquis d’apprentissage visés
À l’issue de cet enseignement, l’étudiant sera capable de :
1. Décrire les principes fondamentaux de la communication entre systèmes informatiques, en s'appuyant sur
le modèle OSI.
2. Identifier les caractéristiques et fonctions des différentes couches du modèle OSI, notamment les couches
physique, liaison de données et transport.
3. Expliquer le fonctionnement des protocoles de communication courants (I2C, SPI, CAN, UART,
TCP/IP…) et leurs domaines d'application.
4. Analyser un échange de données numériques, en décomposant une trame binaire selon sa structure (bits
de contrôle, données, adresse…).
5. Interpréter des signaux électriques transmis sur une liaison physique, à l’aide d’outils comme un
oscilloscope ou un analyseur logique.
6. Mettre en œuvre une communication simple entre deux dispositifs électroniques, en configurant
correctement les paramètres matériels et logiciels.
7. Diagnostiquer des problèmes de communication liés à la couche physique ou aux couches basses du
modèle OSI (erreurs de synchronisation, de format, de tension, etc.).
8. Communiquer oralement ou par écrit sur les notions de communication informatique, en utilisant un
vocabulaire technique adapté à un public débutant ou semi-averti.
At the end of this course, the student will be able to:
1. Describe the fundamental principles of communication between computer systems, based on the OSI
model.
2. Identify the characteristics and functions of the different layers of the OSI model, particularly the physical,
data link, and transport layers.
3. Explain the operation of common communication protocols (I2C, SPI, CAN, UART, TCP/IP…) and their
application domains.
4. Analyze a digital data exchange by breaking down a binary frame according to its structure (control bits,
data, address, etc.).
5. Interpret electrical signals transmitted over a physical link using tools such as an oscilloscope or logic
analyzer.
6. Implement a simple communication between two electronic devices by correctly configuring hardware
and software parameters.
7. Diagnose communication issues related to the physical layer or the lower layers of the OSI model
(synchronization errors, format issues, voltage problems, etc.).
8. Communicate orally or in writing about computer communication concepts, using appropriate technical
vocabulary for a beginner or semi-technical audience.
## Modalités d’évaluation
Formule d’évaluation (1*RAP1)/1
## Langue d’enseignement
Langue Français/French
## Objectifs de la formation visés
sfitcejbO
À l'issue de cet enseignement, l'élève :
 Disposera des connaissances fondamentales concernant les bases de la communication de données entre
systèmes intelligents ;
 Sera capable d’expliquer à un public débutant les notions de transfert de données suivant un modèle du
type OSI, en utilisant un vocabulaire technique approprié ;
 Sera capable d’analyser et d’interpréter les signaux électriques transitant sur une liaison physique (ex :
I2C, CAN) ;
 Maîtrisera les principes de codage, d'encapsulation et de décodage des données sur des réseaux simples ;
 Saura mettre en œuvre et diagnostiquer une communication entre composants matériels.
At the end of this course, the student will:
 Possess fundamental knowledge of the basics of data communication between intelligent systems;
 Be able to explain data transfer concepts based on a model such as the OSI model to a beginner audience,
using appropriate technical vocabulary;
 Be able to analyze and interpret electrical signals transmitted over a physical link (e.g., I2C, CAN);
 Master the principles of data encoding, encapsulation, and decoding over simple networks;
 Be capable of implementing and diagnosing communication between hardware components.
## Contenus
Séance 1 (2h) : Introduction à la communication numérique et au modèle OSI
 Enjeux de la communication dans les systèmes intelligents (embarqué, IoT, réseau)
 Présentation du modèle OSI et de ses 7 couches
 Focus sur les couches basses : physique, liaison de données
 Introduction au concept de trame et au codage des données (NRZ, Manchester…)
Séance 2 (2h) : Protocoles de communication et transmission physique
 Étude de protocoles matériels : UART, I2C, SPI
 Structure des trames, synchronisation, signaux sur les lignes physiques
 Problématiques : collisions, synchronisation, erreurs, redondance (CRC)
Séance 3 (2h) : Couches hautes, transport et sécurité
 Survol des couches 3 à 7 : routage (IP), transport (TCP/UDP), application (HTTP, MQTT)
 Contrôle de flux, accusés de réception, numérotation des paquets
 Notions de chiffrement, intégrité et authentification (SSL/TLS, certificats)
Travaux Pratiques (2 x 3h)
TP1 (3h) : Communication série - UART et I2C
 Mise en œuvre d’une liaison UART entre microcontrôleurs
 Observation des trames via oscilloscope ou analyseur logique
 Transmission et réception de données codées
 Introduction à l’I2C : échanges maître/esclave, analyse d'une trame I2C
TP2 (3h) : Réseaux embarqués - Introduction au bus CAN
 Configuration d’un réseau CAN simple entre deux dispositifs
 Observation de trames CAN (identifiants, données, bit de contrôle)
 Détection et interprétation d’erreurs de transmission
 Discussion sur l'intérêt du CAN en milieux industriels ou automobiles
Session 1 (2h): Introduction to Digital Communication and the OSI Model
 Communication challenges in intelligent systems (embedded, IoT, network)
 Presentation of the OSI model and its 7 layers
 Focus on the lower layers: physical, data link
 Introduction to the concept of data frames and encoding methods (NRZ, Manchester, etc.)
Session 2 (2h): Communication Protocols and Physical Transmission
 Study of hardware protocols: UART, I2C, SPI
 Frame structure, synchronization, signal transmission on physical lines
 Key issues: collisions, synchronization, errors, redundancy (CRC)
Session 3 (2h): Upper Layers, Transport and Security
 Overview of layers 3 to 7: routing (IP), transport (TCP/UDP), application (HTTP, MQTT)
 Flow control, acknowledgments, packet numbering
 Introduction to encryption, integrity, and authentication (SSL/TLS, certificates)
Lab Sessions (2 x 3h)
Lab 1 (3h): Serial Communication – UART and I2C
 Implementation of a UART link between microcontrollers
 Observation of data frames using an oscilloscope or logic analyzer
 Transmission and reception of encoded data
 Introduction to I2C: master/slave communication, analysis of an I2C frame
Lab 2 (3h): Embedded Networks – Introduction to the CAN Bus
 Configuration of a simple CAN network between two devices
 Observation of CAN frames (identifiers, data, control bits)
 Detection and interpretation of transmission errors
 Discussion on the relevance of CAN in industrial or automotive environment
Méthode d'Apprentissage Actif par l'Enseignement
 Phase 1 : L'Exploration en Groupe (Acquisition)
 Phase 2 : La Restitution et l'Enseignement par les Pairs
 Phase 3 : La Régulation et l'Approfondissement par l'Enseignant
 Phase 4 : La Capitalisation du Savoir
Active Learning Method through Teaching
 Phase 1: Group Exploration (Acquisition)
 Phase 2: Restitution and Teaching by Peers
 Phase 3: Regulation and Refinement by the Teacher
 Phase 4: Capitalisation of Knowledge
## Prérequis
 Savoir créer un programme informatique simple (en C, Python, ou autre)
 Connaître les bases de l’électronique : tension, courant, signaux numériques,
liaisons série/parallèle
 Savoir utiliser un oscilloscope est un plus
Prérequis
 Know how to create a simple computer program (in C, Python, or other)
 Know the basics of electronics: voltage, current, digital signals, serial/parallel links
 Know how to use an oscilloscope is a plus
## Travail personnel hors présentiel
Volume horaire 15 Heures
 Travail de compréhension et restitution
 Étude de cas technique
 Mini-projet logiciel
 Lecture critique ou veille technologique
Type de travail
 Understanding and reporting
 Technical case study
 Software mini-project
 Critical reading or technology watch
## Ressources bibliographiques
Ouvrages fondamentaux sur les réseaux et le modèle OSI
 "Réseaux – Notions fondamentales" – Jean-Yves Migeon (Dunod)
 "Réseaux informatiques" – Andrew S. Tanenbaum & David Wetherall (Pearson)
 "Les réseaux pour les nuls" – Doug Lowe (First Interactive)
Protocoles matériels et communication embarquée
 "Systèmes embarqués et interfaces" – Michel Gourgues (Dunod)
 "Protocoles de communication pour l’embarqué" – Frédéric Pétrot, Alain Greiner (Éditions Ellipses)
 "Bus de terrain industriels" – Jean-Philippe Gorce (Éditions Cépaduès)
