---
{
 "course_code": "computer_systems_design",
 "course_name": "Computer Systems Design",
 "institution_slug": "ec_i_napoli01",
 "source_url": "https://ingegneria-elettronica.dieti.unina.it/images/allegati/GdS_-_Laurea_-_2022-23.pdf",
 "source_language": "it",
 "ects_catalog": 9.0,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-20T06:10:40",
 "content_sha256": "d11161bc067288417c2fddf2dacf514361bb27f4d6a9c4387a7f5665d5faf2f5"
}
---

# Computer Systems Design

- SSD ING-INF/05
- DENOMINAZIONE DEL CORSO DI STUDIO:
- CORSO DI LAUREA IN INGEGNERIA ELETTRONICA
- ANNO ACCADEMICO: 2022-2023

## Informazioni generali

- ANNO DI CORSO (I, II, III): III
- SEMESTRE (I, II): II
- CFU: 9

## Insegnamenti propedeutici

Nessuna propedeuticità.

## Prerequisiti

Conoscenza dell’architettura di un calcolatore, dei sistemi operativi e delle reti di comunicazione.

## Obiettivi formativi

Il corso si pone l’obiettivo di fornire gli elementi metodologici, progettuali e tecnologici per la realizzazione di sistemi di
elaborazione con riferimento alle architetture pipelined, multi-computer, multi-processore, multi-core e multi-threading. Il
corso affronta inoltre il funzionamento e dimensionamento dei sistemi di memoria gerarchici, il progetto e la
programmazione delle unità di I/O (parallele, seriali, DMA e PIC) con i relativi protocolli di comunicazione, e le
problematiche di implementazione dei meccanismi di base per la virtualizzazione delle risorse hardware (meccanismi di
gestione dei processi, macchine virtuali e hypervisor). Il corso presenta, infine, le principali tecniche per la realizzazione di
sistemi pervasivi, autonomici, IoT e di edge computing, nonché le architetture cloud.
La parte applicativa del corso è dedicata al progetto di driver di I/O e allo sviluppo di sistemi operanti in ambito industriale.
Le attività vengono svolte con riferimento ad applicazioni sviluppate e valutate sperimentalmente mediante architetture
che prevedono l’impiego di nodi di elaborazione dotati di processori RISC e di diversi dispositivi di I/O opportunamente
configurabili.
Con riferimento agli aspetti tecnologici, sono illustrate le architetture di sistemi commerciali per l’implementazione di
applicazioni industriali basate su System on Chip o su nodi di elaborazione ottenuti per integrazione di componenti
configurabili.

## Risultati di apprendimento attesi (descrittori di Dublino)

Conoscenza e capacità di comprensione
Lo studente deve dimostrare di conoscere e comprendere le problematiche relative al progetto di sistemi di elaborazione,
con particolare riferimento alla gestione degli hazard derivanti dall’impiego di tecniche di parallelismo interno ed esterno
per l’aumento delle prestazioni, al dimensionamento delle memorie, e all’orchestrazione di diversi sottosistemi operanti in
concorrenza fra loro e comunicanti mediante diverse interfacce di I/O.
Deve inoltre dimostrare di saper individuare, fra i diversi approcci presentati al corso, quelli che meglio si adattano a
specifiche applicazioni o condizioni operative.
Capacità di applicare conoscenza e comprensione
Lo studente deve dimostrare di essere in grado di progettare e sviluppare il software di base (driver assembly) necessario
per consentire la comunicazione fra diversi sottosistemi mediante i dispositivi di I/O presentati al corso, anche in presenza
di accessi concorrenti a dati comuni, nonché di scheduler per la gestione della concorrenza. Deve inoltre essere in grado di
completare il ciclo di sviluppo di applicazioni di media complessità, che richiedano l’utilizzo di uno o più nodi di elaborazione,
di diversi dispositivi di I/O, di sensori/attuatori, sui dispositivi hardware in dotazione.

## Programma-Syllabus

Richiami ed approfondimenti sui sistemi di elaborazione: Sistemi general purpose ed embedded. Processori RISC e CISC.
Unità di controllo cablata e microprogrammata. Meccanismi di gestione delle interruzioni. Introduzione al parallelismo e
al pipelining. Richiami sul processore Motorola 68000. Il processore MIPS: modello di programmazione e pipeline. Il
processore ARM. Architetture e applicazioni dei DSP.
Pipelining e hazard: Tecniche di gestione dei conflitti sui dati, dei salti e delle interruzioni in una architettura pipelined.
Architetture superscalari.
Sistemi multiprocessore e multicomputer: Architetture parallele, speed up ed efficienza. Algoritmi per la coerenza della
memoria.
Periferiche di I/O e driver: Architettura e funzionamento di periferiche parallele, seriali, DMA e PIC, e sviluppo di driver per
la loro programmazione.
La gerarchia della memoria: Architettura, indirizzamento e dimensionamento di una cache. Memoria virtuale. Memorie
statiche e dinamiche.
Bus e reti di interconnessione: I bus di sistema. Protocolli di comunicazione. Reti di interconnessione: switch multistadio.
Progetto e sviluppo di sistemi basati su microcontrollori: Principi di progetto di sistemi di elaborazione per applicazioni
industriali basati su microcontrollori. Architetture e impiego dei System on a Chip (SoC). Dispostivi commerciali e industriali
programmabili. Ambienti di progettazione, di simulazione e analisi di sistemi di elaborazione.
Virtualizzazione e cloud computing. Tecniche di virtualizzazione e hypervisor. Introduzione ai sistemi cloud: modelli di
servizio e applicazioni.
IoT/Edge computing. Architetture e applicazioni di sistemi IoT e di edge computing. Sviluppo di sistemi edge di tipo
commerciale e integrazione di reti di sensori.

## Materiale didattico

-  Libro di testo: Conte, Mazzeo, Mazzocca, Prinetto. Architettura dei calcolatori. Edizioni CittàStudi. 2014. ISBN:
9788825173642.
-  Dispense e presentazioni fornite dai docenti relative ad argomenti teorici e applicativi trattati al corso.
-  Manuali e datasheet dei dispositivi utilizzati per l’implementazione delle applicazioni.

## Modalità di svolgimento dell'insegnamento

Il corso prevede circa il 70% di lezioni frontali in cui vengono affrontati gli argomenti teorici, mentre il restante 30% è
riservato a lezioni pratiche ed esercitazioni riguardanti lo sviluppo di driver di I/O e l’utilizzo degli ambienti di sviluppo.
La parte applicativa del corso si avvale di strumenti di sviluppo professionali di cui è disponibile una licenza ad uso gratuito
e di board di sviluppo (dotate di un microcontrollore ARM e di diversi dispositivi di I/O) che vengono distribuiti agli studenti
per l’implementazione dei propri progetti.

## Verifica di apprendimento e criteri di valutazione

Modalità di esame:
L'esame si articola in prova
scritta e orale x
solo scritta
solo orale
discussione di elaborato progettuale x
altro
In caso di prova scritta i quesiti sono (*)
A risposta multipla
A risposta libera x
Esercizi numerici
(*) È possibile rispondere a più opzioni
La verifica dell’apprendimento prevede una prova scritta consistente in esercizi di progetto di sistemi basati su dispositivi
di I/O e una prova orale orientata alla verifica della comprensione dei concetti teorici del corso e alla discussione degli
esercizi implementati su board di sviluppo.
