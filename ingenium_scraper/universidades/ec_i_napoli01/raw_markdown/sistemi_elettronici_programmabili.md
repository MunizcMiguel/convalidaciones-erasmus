---
{
 "course_code": "sistemi_elettronici_programmabili",
 "course_name": "Sistemi Elettronici Programmabili",
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
 "fetched_at": "2026-11-20T06:10:39",
 "content_sha256": "aa12ff8be73c41767d272c0ac2b0f66ac109244468118ba23d5b3c1868acdf1f"
}
---

# Sistemi Elettronici Programmabili

- SSD ING-INF/01
- DENOMINAZIONE DEL CORSO DI STUDIO:
- CORSO DI LAUREA TRIENNALE IN INGEGNERIA ELETTRONICA
- ANNO ACCADEMICO 2022-23

## Informazioni generali

- ANNO DI CORSO (I, II, III): III
- SEMESTRE (I, II): II
- CFU: 9

## Insegnamenti propedeutici

Nessuna propedeuticità.

## Prerequisiti

Conoscenza di base di matematica, fisica, chimica ed elettrotecnica.

## Obiettivi formativi

L’insegnamento è rivolto (i) allo studio di elementi di fisica dei semiconduttori, (ii) all’analisi del funzionamento dei principali
dispositivi elettronici a semiconduttore, i.e., diodo, transistore bipolare, condensatore MOS, MOSFET; (iii) al progetto dei
suddetti dispositivi elettronici. Pertanto l’obiettivo consta nel fornire agli studenti le nozioni e competenze necessarie alla
comprensione dei meccanismi fisici e delle problematiche, nonché dei trade-off, progettuali dei dispositivi.

## Risultati di apprendimento attesi (descrittori di Dublino)

Conoscenza e capacità di comprensione
Al termine del processo di apprendimento lo studente:
-  conosce le tecniche di progettazione di semplici sistemi digitali,
-  comprende lo schema a blocchi di un circuito digitale,
-  conosce i costrutti del linguaggio HDL Verilog necessari per la descrizione di un circuito digitale,
-  conosce i costrutti del linguaggio HDL Verilog necessari per la realizzazione di un testbench,
-  comprende il funzionamento di un testbench,
-  conosce le tecniche di progetto utili alla realizzazione di circuiti digitali che implementano operazioni aritmetiche,
-  conosce la struttura di un componente FPGA (Field Programmable Gate Array),
-  comprende il datasheet di un FPGA.
Capacità di applicare conoscenza e comprensione
Al termine del processo di apprendimento lo studente:
-  è in grado di progettare/creare lo schema a blocchi di un circuito digitale sulla base delle specifiche date,
-  comprende come suddividere un circuito di media complessità in sezioni combinatorie, sequenziali, aritmetiche, e
basate su Finite State Machine (FSM) per la gestione dell’intero sistema,
-  è in grado di descrivere un circuito digitale in linguaggio HDL Verilog
-  è in grado di ideare e realizzare un testbench in linguaggio HDL Verilog
-  è in grado di implementare un circuito digitale su di uno specifico dispositivo FPGA.
Autonomia di giudizio, Abilità comunicative, Capacità di apprendimento
In relazione a tutte le capacità descritte in precedenza, lo studente acquisisce la capacità di descrivere per iscritto, anche
utilizzando linguaggi standard, le scelte progettuali. E’ in grado di giustificare le scelte progettuali effettuate e può studiare
circuiti di media complessità ed i datasheet di un FPGA apprendendo le possibilità progettuali aggiuntive.

## Programma-Syllabus

Flusso di progetto per circuiti digitali da implementare su FPGA.
Classificazione e caratteristiche delle FPGA in commercio.
Package degli FPGA: dimensionamento termico e classificazione in funzione del costo e delle dimensioni.
Il linguaggio per la descrizione dell’hardware HDL Verilog.
Descrizione di circuiti combinatori in linguaggio Verilog. I testbench in linguaggio Verilog.
Addizionatori implementati su FPGA.
Circuiti aritmetici implementati in linguaggio Verilog. Circuiti sequenziali implementati in linguaggio Verilog.
Temporizzazione dei circuiti sequenziali sincroni. Influenza della temporizzazione su prestazioni ed affidabilità dei circuiti
sequenziali sincroni.
Descrizione circuitale in linguaggio Verilog di macchine a stati finiti con riferimento alla topologia di Mealy, Moore e Mealy
sincronizzata. Codifica dello stato per macchine a stati finiti e tolleranza ai guasti. Macchine a memoria finita. Realizzazione
di circuiti combinatori e sequenziali su FPGA disponibili in laboratorio.
Potenza dissipata dei circuiti implementati su FPGA, stima e simulazione.
Tensioni di alimentazione dei circuiti programmabili, evoluzione storica.
Uscite abilitate o three-state. Reiezione del rumore.
Effetti dovuti a induttanze parassite ed alle linee di trasmissione.
Logiche veloci per trasferimento dati e per collegamento su backplane.

## Materiale didattico

E. Napoli “Progetto di sistemi elettronici digitali basati su dispositivi FPGA”, ed. Esculapio, 2011.

## Modalità di svolgimento dell'insegnamento

Lo svolgimento dell’insegnamento prevede lezioni frontali (50%) ed esercitazioni ed esperimenti in laboratorio (50%).

## Verifica di apprendimento e criteri di valutazione

a) Modalità di esame:
L'esame si articola in prova
scritta e orale 
solo scritta
solo orale
discussione di elaborato progettuale 
altro (discussione esercitazioni)
In caso di prova scritta i quesiti sono (*)
A risposta multipla
A risposta libera 
Esercizi numerici
b) Modalità di valutazione:
La valutazione tiene conto delle risposte per iscritto data al questionario durante l’esame e delle scelte effettuate per
l’implementazione dell’elaborato progettuale. Il peso delle due componenti è 60% per la prova scritta e 40% per la
discussione dell’elaborato.
