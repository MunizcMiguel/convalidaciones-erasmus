---
{
 "course_code": "EELTS.Ii20.03207.26",
 "course_name": "Computer-based control circuits",
 "institution_slug": "ec_pl_krakow02",
 "source_url": "https://sylabusy.agh.edu.pl/en/document/59b902f4-bdfe-43b4-8e4e-b9e6b2f70a6d.html",
 "source_language": "pl",
 "ects_catalog": 4.0,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": false
 },
 "fetched_at": "2026-11-20T08:22:53",
 "content_sha256": "0e83a72b711059cc163c84bcdbc8f589c556140bd3f847f73074debf8e252cd7"
}
---

# Computer-based control circuits

## Basic information

- **Field of study**: Electrical Engineering
- **Major**: -
- **Organisational unit**: Faculty of Electrical Engineering, Automatics, Computer Science and Biomedical Engineering
- **Study level**: First-cycle (engineer) programme
- **Form of study**: Full-time studies
- **Profile**: General academic

- **Didactic cycle**: 2026/2027
- **Course code**: EELTS.Ii20.03207.26
- **Lecture languages**: Polish
- **Mandatoriness**: Obligatory
- **Block**: General Modules
- **Course related to scientific research**: Yes

- **Period**: Semester 6
- **Method of verification of the learning outcomes**: Exam; Activities and hours; Lectures: 28 Laboratory classes: 14 Project classes: 14
- **Number of ECTS credits**: 4

## Goals

- **C1**: Celem przedmiotu jest przekazanie wiedzy z zakresu dyskretnego sterowania układami dynamicznymi. W ramach zajęć studenci zapoznają się z różnymi technikami dyskretyzacji, budową układów regulacji cyfrowej oraz budową i działaniem regulatorów realizowanych jako programy komputerowe. Sterują również układami rzeczywistymi z wykorzystaniem połączenia Arduino-Simulink.

## Course's learning outcomes

| Code | Outcomes in terms of | Learning outcomes prescribed to a field of study | Methods of verification |
|---|---|---|---|
| Knowledge – Student knows and understands: |  |  |  |
| W1 | ma podstawową wiedzę w zakresie metodyki i technik programowania oraz stosowania technik komputerowych w działalności inżynierskiej | ELT1A_W05 | Test |
| W2 | ma elementarną wiedzę w zakresie podstaw sterowania i automatyki | ELT1A_W07 | Test |
| W3 | ma podstawową wiedzę w zakresie możliwości wykorzystywania techniki mikroprocesorowej w urządzeniach energetyki i automatyki, zna podstawowe pojęcia związane z mikroprocesorami i mikrokomputerami | ELT1A_W05 | Execution of a project, Test |
| Skills – Student can: |  |  |  |
| U1 | potrafi stosować poznane zasady fizyki oraz metody i modele matematyczne, a także techniki komputerowe do opisu, analizy i oceny działania elementów i układów elektrotechnicznych | ELT1A_U03 | Execution of laboratory classes, Report |
| U2 | potrafi dobrać, zaprogramować, uruchomić i przetestować układ mikroprocesorowy dla zastosowań przemysłowych | ELT1A_U09 | Execution of laboratory classes, Report, Completion of laboratory classes |
| U3 | potrafi projektować i dokonywać analizy i symulacji prostych układów regulacji automatycznej dla oceny ich działania w stanach ustalonych i dynamicznych | ELT1A_U09 | Execution of a project, Execution of laboratory classes, Completion of laboratory classes |
| Social competences – Student is ready to: |  |  |  |
| K1 | rozumie potrzebę i zna możliwości ciągłego dokształcania się oraz podnoszenia swoich kompetencji zawodowych | ELT1A_K01 | Examination |

## Student workload

- **Activity form**: Average amount of hours* needed to complete each activity form
- **Lectures**: 28
- **Laboratory classes**: 14
- **Project classes**: 14
- **Preparation for classes**: 14
- **Realization of independently performed tasks**: 12
- **Examination or final test/colloquium**: 2
- **Preparation of project, presentation, essay, report**: 16
- **Student workload**: Hours 100
- **Workload involving teacher**: Hours 56

* hour means 45 minutes

## Program content

| No. | Program content | Course's learning outcomes | Activities |
|---|---|---|---|
| 1. | 1. Wykład wprowadzający w problematykę współpracy układów dyskretno-ciągłych. Omówienie elementów układu regulacji zamkniętej; rodzaje sygnałów oraz układy do ich przetwarzania. 2. Porównanie: układ dyskretny – układ ciągły, w tym modele matematyczne tych układów w dziedzinie czasu i częstotliwości. Z jednej strony równanie różnicowe z drugiej równanie różniczkowe; odpowiedzi impulsowe i modele transmitancyjne; interpretacja zmiennej „z” i zmiennej „s”, charakterystyki częstotliwościowe układów a transmitancje widmowe. 3. Porównanie jakościowe cech układów ciągłych i dyskretnych i próba jednolitego opisu współpracujących układów – ciągłego i dyskretnego. Elementy próbkujące i podtrzymujące, czyli modele przetwarzania (A/C) i (C/A) w projekcie inżynierskim – aspekty praktyczne: charakterystyki czasowe i częstotliwościowe, znaczenie okresu próbkowania. 4. Dyskretne reprezentacje dynamiki układu ciągłego; reprezentacje dokładne oraz przybliżone metody dyskretyzacji, przykłady dyskretyzacji w dziedzinie czasu i częstotliwości. Właściwości układu ciągłego po dyskretyzacji, dokładność opisu i wybór okresu próbkowania. 5. Stało- i zmiennoprzecinkowe przetwarzanie sygnałów – formaty danych, podział procesorów, zasady doboru elementów układu regulacji dla zadanych kryteriów. 6. Cyfrowe układy sterowania – przykład obliczeniowy, który prowadzi do powstania cyklu granicznego oraz statyzmu układu regulacji. Metoda funkcji opisującej w analizie cyklu granicznego układu o stałoprzecinkowym przetwarzaniu sygnałów. Zapas stabilności. 7. Przegląd regulatorów i ich zastosowania – regulatory konwencjonalne PID, regulatory stanu. Wskaźniki jakości regulacji. | W1, W3, U1, K1 | Lectures |
| 2. | 1. Powtórka z dynamiki układów ciągłych- przykładowe charakterystyki czasowe i częstotliwościowe elementów automatyki. 2. Dyskretyzacja układów ciągłych – badania porównawcze pracy układów ciągłych i dyskretnych. 3. Dyskretyzacja elementu oscylacyjnego – wpływ czasu próbkowania na odpowiedzi skokowe układu, wykorzystanie różnych metod dyskretyzacji, badania porównawcze. 4. Układ regulacji cyfrowej PID1DOF i PID2DOF – modelowanie. 5. Realizacja praktyczna regulatorów PI2DOF w oparciu o platformę Arduino programowaną z poziomu programu Matlab-Simulink. | W1, W2, U2, U3 | Laboratory classes |
| 3. | Projekt obliczeniowo-symulacyjny – Zadana jest struktura i obiekt regulacji. Należy: wyznaczyć elementy układu regulacji ciągłej (wzmacniacze i układy pomiarowe), uzupełnienie o przetworniki AC i CA, dobór procesora sterującego. Optymalizacja parametryczna regulatorów, dobór czasu próbkowania, dyskretyzacja regulatorów, obliczenie ograniczeń regulatorów. Symulacyjne porównanie sterowania ciągłego i dyskretnego. Uzupełnienie struktury o kwantyzatory, które symulują przetwarzanie stałoprzecinkowe, i wyznaczenie poziomu kwantyzacji sygnałów przy której uwidacznia się zjawisko statyzmu i cyklu granicznego | W3, U2, U3 | Project classes |

## Extended information/Additional elements

### Teaching methods and techniques :

Lectures, Group work, Lecture

| Activities | Methods of verification | Credit conditions |
|---|---|---|
| Lectures | Examination | Pozytywna ocena z egzaminu |
| Lab. classes | Execution of laboratory classes, Test, Report, Completion of laboratory classes |  |
| Project classes | Execution of a project, Report |  |

### Rules of participation in given classes, indicating whether student presence at the lecture is obligatory

Lectures: Studenci uczestniczą w zajęciach poznając kolejne treści nauczania zgodnie z syllabusem przedmiotu. Studenci winni na bieżąco zadawać pytania i wyjaśniać wątpliwości. Rejestracja audiowizualna wykładu wymaga zgody prowadzącego. Laboratory classes: Studenci wykonują ćwiczenia laboratoryjne zgodnie z materiałami udostępnionymi przez prowadzącego. Student jest zobowiązany do przygotowania się w przedmiocie wykonywanego ćwiczenia, co może zostać zweryfikowane kolokwium w formie ustnej lub pisemnej. Zaliczenie zajęć odbywa się na podstawie zaprezentowania rozwiązania postawionego problemu. Zaliczenie modułu jest możliwe po zaliczeniu wszystkich zajęć laboratoryjnych. Project classes: Studenci wykonują prace praktyczne mające na celu uzyskanie kompetencji zakładanych przez syllabus. Ocenie podlega sposób wykonania projektu oraz efekt końcowy.

## Literature

Obligatory

- *Byrski W.* Obserwacja i sterowanie w systemach dynamicznych Uczelniane Wydaw. AGH, 2007.
- *Grabowski P.* Ćwiczenia komputerowe z teorii sterowania. Kraków : Wydaw. AGH, 1996.
- *Szymkat M. *Komputerowe wspomaganie w projektowaniu układów regulacji Warszawa: WNT, 1993.
- *Åström, K., Wittenmark, B.* Computer-Controlled Systems, NJ, Prentice Hall, 1997
- *Sieklucki G.* Automatyka napędu. Kraków : Wydaw. AGH, 2009.
- Karl Johan Åström, Tore Hägglund PID Controllers: Theory, Design, and Tuning, Publisher ISA, 1995

Optional

- Nie podano dodatkowych publikacji

## Scientific research and publications

Publications

- *Sieklucki G.* Automatyka napędu. Kraków : Wydaw. AGH, 2009.
- Grzegorz SIEKLUCKI, Tadeusz ORZECHOWSKI Cyfrowe pośrednie sterowanie polowo zorientowane (IFOC) silnikiem indukcyjnym // Elektrotechnika i Elektronika : półrocznik Akademii Górniczo-Hutniczej im. Stanisława Staszica w Krakowie ; ISSN 1640-7202. — Tytuł poprz.: Elektrotechnika. — 2009 t. 28 z. 1–2, s. 32–38.
- Grzegorz SIEKLUCKI, Tadeusz ORZECHOWSKI Dyskretne obserwatory momentu obciążenia w napędach elektrycznych — Discrete-time load torque observers in electric drives / // Automatyka : półrocznik Akademii Górniczo-Hutniczej im. Stanisława Staszica w Krakowie ; ISSN 1429-3447. — 2010 t. 14 z. 1, s. 113–132. — Bibliogr. s. 131–132, Streszcz., Summ.. — tekst: http://journals.bg.agh.edu.pl/AUTOMATYKA/2010-01/Auto08pdf
- Adam Pracownik, Grzegorz SIEKLUCKI, Maciej TONDOS Optimization of a digital controller and observer in a two-mass system – the LQ problem — Optymalizacja cyfrowego regulatora i obserwatora w układzie 2-masowym : problem LQ // Przegląd Elektrotechniczny = Electrical Review / Stowarzyszenie Elektryków Polskich ; ISSN [phone]. — 2012 R. 88 nr 2, s. 341–348.
- Józef GROMBA, Grzegorz SIEKLUCKI, Sylwester SOBIERAJ Czasy realizacji algorytmów PID2DOF w sterownikach serii S7 — Speed of the PID algorithm written in Structured Control Language (SCL) // Przegląd Elektrotechniczny / Stowarzyszenie Elektryków Polskich ; ISSN [phone]. — 2019 R. 95 nr 9, s. 193–197. — Bibliogr. s. 197, Streszcz., Abstr.. — tekst: http://pe.org.pl/articles/2019/9/41.pdf
