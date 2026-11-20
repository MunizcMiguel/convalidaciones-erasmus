---
{
 "course_code": "elettronica_per_iot",
 "course_name": "Elettronica Per IoT",
 "institution_slug": "ec_i_napoli01",
 "source_url": "https://ingegneria-elettronica.dieti.unina.it/images/allegati/GdS_-_Laurea_-_2022-23.pdf",
 "source_language": "it",
 "ects_catalog": 6.0,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-20T06:10:38",
 "content_sha256": "5348e1f51b5467782d048b2daf6f4db5d7060d537079b45fd0bf945bf80c26c5"
}
---

# Elettronica Per IoT

- SSD ING-INF/01
- DENOMINAZIONE DEL CORSO DI STUDIO:
- CORSO DI LAUREA IN INGEGNERIA ELETTRONICA
- ANNO ACCADEMICO: 2022-23

## Informazioni generali

- ANNO DI CORSO (I, II, III): III
- SEMESTRE (I, II): I
- CFU: 6

## Insegnamenti propedeutici

Elettronica I

## Prerequisiti

Nessun prerequisito

## Obiettivi formativi

Il corso di Elettronica per IoT si pone come obiettivo l'apprendimento dei concetti fondamentali relativi ai sistemi elettronici
utilizzati nell’ambito dell’Internet of Things. Gli studenti sono posti in condizione di analizzare la struttura di semplici nodi
sensoriali basati su microcontrollori, partendo da una schematizzazione a blocchi del nodo fino a giungere alla rete internet
che collega questi ultimi a sistemi connessi per la raccolta/elaborazione dei dati (cloud). Sono, quindi, forniti gli strumenti
teorici per l’analisi e la sintesi di firmware per: (i) l’implementazione di algoritmi utili all’interfacciamento di circuiti a
microcontrollore con sensori analogici e digitali; (ii) elaborazione dei dati raccolti in forma numerica; (iii) comunicazione
tramite protocolli digitali di sistemi a microcontrollori con periferiche esterne utili alla connessione alla rete internet.
Vengono, altresì, introdotti i concetti base per l’implementazione di elaborazioni real-time tramite RTOS. Il corso prevede,
infine, una parte di sintesi circuitale dove verificare il corretto funzionamento hardware/firmware di semplici applicazioni
di nodi sensoriali IoT.

## Risultati di apprendimento attesi (descrittori di Dublino)

Conoscenza e capacità di comprensione
A seguito del superamento dell’esame, lo studente possiede concetti essenziali sulla struttura di semplici sistemi a
microcontrollori e sull’architettura di un nodo sensoriale per applicazioni IoT: dalla rilevazione di grandezze fisiche tramite
sensori fino all’immissione di questi ultimi sulla rete internet. Conosce le specifiche circuitali e le tecniche di
programmazione fondamentali per l’utilizzo delle più comuni periferiche integrate nei moderni microcontrollori con
architettura ARM a 32 bit (input/output digitali, input analogici, periferiche PWM, periferiche di comunicazione seriali,
etc.). Conosce le tecniche di interrogazione delle periferiche (i) cicliche (polling); (ii) temporizzate basate su contatori binari
(iii) guidate da eventi (event-driven); (iv) basate su meccanismi tipici dei sistemi operativi real-time (RTOS). In ultimo, lo
studente possiede una conoscenza di base dei protocolli propri dell’IoT con cui può avvenire lo scambio di dati tra un sistema
elettronico a microcontrollore e la rete internet.
Capacità di applicare conoscenza e comprensione
A seguito del superamento dell’esame, lo studente possiede concetti essenziali sulla realizzazione di semplici sistemi a
microcontrollori utili alla implementazione circuitale e firmware di nodi sensoriali per la rete IoT. Ai fini del superamento
dell’esame, quindi, lo studente deve essere in grado di illustrare le specifiche teoriche e tecniche che sono alla base dei
sistemi a microcontrollore per applicazioni IoT. Deve in particolare dimostrare di essere in grado di analizzare semplici
routine firmware per l’interfacciamento con sensori esterni, elaborare i dati raccolti e inviarli opportunamente alla rete
internet tramite uno dei protocolli IoT studiati durante il corso. Deve essere inoltre in grado di implementare firmware per
assolvere a particolari funzioni richieste in un contesto IoT.
Lo studente deve anche essere in grado di analizzare alcuni aspetti tecnici dei componenti elettronici utilizzati nell’ambito
dell’IoT, partendo dai datasheet ed individuando le specifiche rilevanti al fine di una corretta progettazione
hardware/firmware.

## Programma-Syllabus

Definizione di IoT, applicazioni IoT, infrastruttura IoT e concetto di nodo IoT. Cenni di Smart City, Smart Building, Smart
Home, Smart Agricolture, Smart Mobility, Manufacturing 4.0. Microcontrollore: definizione, architettura e differenza con
microprocessore. Ciclo di sviluppo del firmware. Architetture ARM: storia, CISC vs RISC. Famiglia di microcontrollori STM32.
Ambienti di sviluppo (IDE) per microcontrollori STM32. Digital Input e Output per STM32: GPIO Design, registri GPIO e
settings/funzionalità. Ingressi analogici: definizione, ADC e caso studio dei micro STM32. Modalità di funzionamento,
frequenza di campionamento, tecniche di polling, interrupt e DMA. Utilizzo dell'ADC con la tecnica del polling. Utilizzo di
sensori analogici. Conversione D/A: cenni di funzionamento. Utilizzo del DAC. Segnali "pseudo-analogici" PWM: dal segnale
digitale al segnale analogico, filtraggio. Segnali PWM. Introduzione ai protocolli seriali: utilizzo dello shift register. Serial
Peripheral Interface (SPI). Moduli SPI nei micro STM32. Utilizzo di sensori SPI. Introduzione al protocollo I2C: specifiche di
comunicazione, confronto con il protocollo SPI. Utilizzo di sensori I2C. Introduzione al protocollo UART. Diagrammi
temporali e differenze con il protocollo USART. Interrupt, Timers e Tasks. Programmazione event-driven e time-driven.
Introduzione al concetto di interrupt come evoluzione del polling. Concetto di interrupt prioritised, masked e nested.
Latenza. Introduzione ai Real-Time Operating System (RTOS). Concetto di programmazione parallela. Thread, Mutex,
Semaphore, Queue, Mail. Keil RTX e CMSIS-RTOS. Scheduler dei processi: Pre-emptive, Round-Robin, Co-operative.
Protocolli e standards per l'IoT: architetture di una rete IoT, protocolli dati e protocolli di rete. Cenni al modello OSI ed
TCP/IP. Introduzione al protocollo TCP/IP. Overview degli IoT data protocols. Specifiche ed implementazione del protocollo
MQTT. Overview dei protocolli di rete per IoT: reti a raggio corto; a medio raggio; a lungo raggio. Confronto tra le diverse
tecnologie: WiFi, Bluetooth, BLE, Cellular, LoRA. Circuiti elettronici per la connessione wireless alla rete internet.
Introduzione ai servizi Cloud per applicazione IoT: Overview. Concetto di rete di sensori IoT. Casi studio basati su sistemi
cloud per IoT: realizzazione della configurazione back-end, user-app, azioni e data visualization.

## Materiale didattico

-  “Fast and Effective Embedded Systems Design: Applying the ARM mbed” di Rob Toulson, Tim Wilmshurst.
-  “Microcontrollers hardware and firmware for 8-bit and 32-bit devices” di Franco Zappa, Società Editrice Esculapio.
Slide utilizzate durante le lezioni.

## Modalità di svolgimento dell'insegnamento

Il docente utilizzerà: a) lezioni frontali per circa il 70% delle ore totali, b) esercitazioni volte ad (i) applicare ed approfondire
gli aspetti teorici, sull’utilizzo delle tecniche firmware per l’utilizzo dei sistemi a microcontrollore; (ii) applicare ed
approfondire gli aspetti tecnici per la realizzazione hardware di sistemi embedded a microcontrollore, l’interfacciamento
con sensori e con la rete internet.

## Verifica di apprendimento e criteri di valutazione

a) Modalità di esame:
L'esame si articola in prova
scritta e orale
solo scritta
solo orale
discussione di elaborato progettuale
altro X
In caso di prova scritta i quesiti sono (*)
A risposta multipla
A risposta libera
Esercizi numerici
b) Modalità di valutazione:
Gli esami di accertamento e di valutazione consistono:
- in una prova al calcolatore, volta ad accertare la capacità di analisi e sintesi di uno dei seguenti aspetti: (i) firmware per
applicazioni IoT basate su microcontrollori; (ii) schemi, componenti e circuiti elettronici di sistemi embedded a
microcontrollore per IoT.
- in una prova orale, volta ad accertare la comprensione dei metodi teorici per l’analisi e la sintesi di sistemi elettronici a
microcontrollori per IoT sia da un punto di vista firmware che hardware.
Il voto finale è la media aritmetica dei voti conseguiti nelle due prove.
Ai fine del superamento dell’esame con votazione minima di 18/30 è necessario che le conoscenze/competenze della
materia siano almeno ad un livello elementare, sia per la parte di analisi/scrittura firmware che per quella orale. Agli
studenti che abbiano acquisito competenze eccellenti sia nella prova al calcolatore che in quella orale può essere attribuita
la lode.
