---
{
 "course_code": "EELTS.Ii20.03455.26",
 "course_name": "Basics of digital control",
 "institution_slug": "ec_pl_krakow02",
 "source_url": "https://sylabusy.agh.edu.pl/en/document/f8736f2c-9990-44d9-b865-1a3101e5a341.html",
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
 "content_sha256": "754939da47bc1b69cdf2e2dcf19f3adeccddf86b968a02ef649ca3b4a7ad678e"
}
---

# Basics of digital control

## Basic information

- **Field of study**: Electrical Engineering
- **Major**: -
- **Organisational unit**: Faculty of Electrical Engineering, Automatics, Computer Science and Biomedical Engineering
- **Study level**: First-cycle (engineer) programme
- **Form of study**: Full-time studies
- **Profile**: General academic

- **Didactic cycle**: 2026/2027
- **Course code**: EELTS.Ii20.03455.26
- **Lecture languages**: Polish
- **Mandatoriness**: Obligatory
- **Block**: General Modules
- **Course related to scientific research**: Yes

- **Period**: Semester 6
- **Method of verification of the learning outcomes**: Completing the classes; Activities and hours; Lectures: 28 Laboratory classes: 28
- **Number of ECTS credits**: 4

## Goals

- **C1**: Zapoznanie się z zasadami projektowania (warstwa fizyczna) i pisania algorytmów regulacji (warstwa informatyczna) systemów cyfrowych.
- **C2**: Analiza układów dyskretnych, dyskretyzacja układów ciągłych, wdrażanie układów regulacji cyfrowej w oparciu o platformę Arduino i oprogramowanie Simulink.

## Course's learning outcomes

| Code | Outcomes in terms of | Learning outcomes prescribed to a field of study | Methods of verification |
|---|---|---|---|
| Knowledge – Student knows and understands: |  |  |  |
| W1 | Student zna i rozumie znaczenie wszystkich specjalistycznych pojęć omawianych w ramach modułu kształcenia „Podstawy regulacji cyfrowej” | ELT1A_W01 | Activity during classes, Test, Essays written during classes |
| W2 | Student ma wiedzę w zakresie matematyki, obejmującą algebrę, analizę , równania różniczkowe i różnicowe, niezbędną do opisu i analizy obiektów i procesów technicznych, zarówno ciągłych jak i dyskretnych | ELT1A_W01 | Activity during classes, Test, Essays written during classes |
| W3 | Student utrwala wiedzę w zakresie podstaw sterowania obiektami liniowmi - ciągłymi i dyskretnymi, ze szczególnym naciskiem na problematykę współpracy układów dyskretno-ciagłych | ELT1A_W07 | Activity during classes, Test, Essays written during classes |
| W4 | Student ma pogłębioną wiedzę z zakresu specjalistycznych zagadnień dotyczących sterowania cyfrowego, implementacji regulatorów cyfrowych i przetwarzania sygnałów w wersji cyfrowej dla potrzeb regulacji . | ELT1A_W10 | Activity during classes, Test, Essays written during classes |
| Skills – Student can: |  |  |  |
| U1 | Student potrafi stosować poznane metody i modele matematyczne, a także techniki komputerowe do analizy i oceny działania układów dynamicznych; potrafi ocenić jakość regulacji i zbadać przyczyny powstawania błędów w układzie regulacji dyskretno-ciągłej | ELT1A_U03 | Activity during classes, Execution of laboratory classes, Essays written during classes, Completion of laboratory classes |
| U2 | Student potrafi projektować liniowe układy regulacji automatycznej na podstawie oceny ich działania w stanach ustalonych i dynamicznych ; potrafi dobrać strukturę i parametry regulatora cyfrowego do sterowania obiektem ciągłym liniowym ; jako narzędzie projektowe wykorzystuje metodę badań symulacyjnych | ELT1A_U09 | Activity during classes, Execution of laboratory classes, Essays written during classes, Completion of laboratory classes |
| U3 | Student potrafi zaimplementować algorytm regulatora konwencjonalnego na procesorze sygnałowym ( np. współpracującym z platformą programową Simulink); potrafi przeskalować zmienne programowe i dopasować cyfrowe sygnały wyjściowe z procesora dla potrzeb sterowania rzeczywistym obiektem | ELT1A_U09 | Activity during classes, Execution of laboratory classes, Essays written during classes, Completion of laboratory classes |
| Social competences – Student is ready to: |  |  |  |
| K1 | Student rozumie potrzebę i zna możliwości ciągłego dokształcania się oraz podnoszenia swoich kompetencji zawodowych wraz z szybkim rozwojem techniki | ELT1A_K01 | Activity during classes |

## Student workload

- **Activity form**: Average amount of hours* needed to complete each activity form
- **Lectures**: 28
- **Laboratory classes**: 28
- **Preparation for classes**: 10
- **Realization of independently performed tasks**: 20
- **Preparation of project, presentation, essay, report**: 15
- **Student workload**: Hours 101
- **Workload involving teacher**: Hours 56

* hour means 45 minutes

## Program content

| No. | Program content | Course's learning outcomes | Activities |
|---|---|---|---|
| 1. | W ramach modułu student zdobywa wiedzę ogólną w zakresie projektowania regulatorów cyfrowych do sterowania obiektami ciągłymi. WYKŁADY obejmują kolejne zagadnienia tematyczne 1. Wykład wprowadzający w problematykę współpracy układów dyskretno-ciągłych. Omówienie elementów układu regulacji cyfrowej, rodzaju sygnałów oraz układów do ich przetwarzania. Systemy czasu rzeczywistego: próbkowanie, zadania programu sterującego. 2. Porównanie : układ dyskretny – układ ciągły, w tym modele matematyczne tych układów w dziedzinie czasu i częstotliwości. Z jednej strony równanie różnicowe z drugiej równanie różniczkowe; modele transmitancyjne - interpretacja zmiennej „z” i zmiennej „s”, transmitancje widmowe 3. Porównanie jakościowe cech układów ciągłych i dyskretnych i próba jednolitego opisu współpracujących układów – ciągłego i dyskretnego. Elementy próbkujące i podtrzymujące, czyli modele przetwarzania (A/C) i (C/A) w projekcie inżynierskim: przykład doboru elementów i regulatora w komputerowym układzie sterowania. 4. Dyskretne reprezentacje dynamiki układu ciągłego; reprezentacje dokładne oraz przybliżone metody dyskretyzacji, w tym transformacje w dziedzinie czasu i częstotliwości. Obraz właściwości układu ciągłego po dyskretyzacji, dokładność opisu i znaczenie okresu próbkowania. 5. Analiza prostych układów regulacji dyskretno-ciągłych. Regulacja poprzez zmianę wzmocnienia regulatora i czasu próbkowania. 6. Analiza stabilności układów dyskretno-ciągłych jako podstawowe wymaganie stawiane układom regulacji automatycznej. 7. Konwencjonalne regulatory cyfrowe PID . Zagadnienia doboru struktury i parametrów regulatorów - wskaźniki jakości. 8. Implementacja cyfrowych algorytmów sterowania obiektami ciągłymi – przykład projektowy. Analiza dokładności regulacji. Badanie przebiegu sygnałów między okresami próbkowania. Badanie wpływu niedokładności realizacji algorytmów oraz opóźnień czasowych w przetwarzaniu danych, na jakość procesu regulacji. 9. Dobór czasu próbkowania dla układów regulacji cyfrowej. | W1, W2, W3, W4, K1 | Lectures |
| 2. | Ćwiczenia laboratoryjne realizowane są w pracowni komputerowej i laboratorium cyfrowego sterowania układami napędowymi. W ramach ćwiczeń student samodzielnie rozwiązuje problemy sygnalizowane na wykładzie. Następnie pod kierunkiem prowadzącego wykonuje konkretne zadanie metodą symulacyjną – projekt oraz ćwiczenie laboratoryjne, w którym programuje algorytm regulacji dla zadanego obiektu ciągłego. LABORATORIUM Bloki tematyczne laboratorium: 1. Badanie odpowiedzi impulsowych i skokowych układów dyskretnych – przetwarzanie cyfrowe; rozpoznawanie cech układu na podstawie modelu matematycznego 2. Badanie charakterystyk częstotliwościowych układów dyskretnych , ich praktyczna interpretacja 3. Dyskretyzacja procesów ciągłych, konsekwencje w dziedzinie czasu i częstotliwości, porównanie stosowanych metod. 4. Badanie charakterystyk czasowych regulatora PID ; zastosowanie regulatora do sterowania obiektem ciągłym 5. Synteza regulatora dyskretnego PID do sterowania obiektem ciągłym II rzędu – projekt indywidualny każdego studenta 6. Dobór czasu próbkowania dla układu regulacji cyfrowej. 7. Projekt regulatora konwencjonalnego PID i jego implementacja na platformie Arduino do sterowania obiektem ciągłym z wykorzystaniem przetwornika (A/C) oraz układu PWM do generowania sygnałów sterujących. 8. Badanie charakterystyk czasowych sygnałów sterującego i sterowanego w układzie regulacji z regulatorem PI z nasyceniem. Omówienie struktury korekcyjnej typu „antiwind-up”. Implementacja na platformie Arduino. | U1, U2, U3 | Laboratory classes |

## Extended information/Additional elements

### Teaching methods and techniques :

Lectures, Group work, Lecture

| Activities | Methods of verification | Credit conditions |
|---|---|---|
| Lectures | Activity during classes, Test, Essays written during classes |  |
| Lab. classes | Activity during classes, Execution of laboratory classes, Essays written during classes, Completion of laboratory classes |  |

### Rules of participation in given classes, indicating whether student presence at the lecture is obligatory

Lectures: Studenci uczestniczą w zajęciach poznając kolejne treści nauczania zgodnie z syllabusem przedmiotu. Studenci winni na bieżąco zadawać pytania i wyjaśniać wątpliwości. Rejestracja audiowizualna wykładu wymaga zgody prowadzącego. Laboratory classes: Studenci wykonują ćwiczenia laboratoryjne zgodnie z materiałami udostępnionymi przez prowadzącego. Student jest zobowiązany do przygotowania się w przedmiocie wykonywanego ćwiczenia, co może zostać zweryfikowane kolokwium w formie ustnej lub pisemnej. Zaliczenie zajęć odbywa się na podstawie zaprezentowania rozwiązania postawionego problemu. Zaliczenie modułu jest możliwe po zaliczeniu wszystkich zajęć laboratoryjnych.

## Literature

Obligatory

- 1. J.Ackermann : Sampled-data Control Systems, Springer 1996
- 2. K.J.Astrom, B.Wittenmark : Computer-controlled Systems, PrenticeHall 1997
- 3. G. Sieklucki: Automatyka napędu, Wyd. AGH, 2009
- 4. J.Brzózka : Regulatory dyskretne w automatyce, MIKOM 2002
- 5. A.Dzieliński, T.Kaczorek i in. : Podstawy sterowania, WNT 2005

Optional

- Nie podano dodatkowych publikacji

## Scientific research and publications

Publications

- Grzegorz SIEKLUCKI, Tadeusz ORZECHOWSKI Cyfrowe pośrednie sterowanie polowo zorientowane (IFOC) silnikiem indukcyjnym — Digital indirect field oriented control (IFOC) of induction motor // Elektrotechnika i Elektronika : półrocznik Akademii Górniczo-Hutniczej im. Stanisława Staszica w Krakowie ; ISSN 1640-7202. — Tytuł poprz.: Elektrotechnika. — 2009 t. 28 z. 1–2, s. 32–38. — Bibliogr. s. 38, Streszcz.. — tekst: https://journals.bg.agh.edu.pl/ELEKTROTECHNIKA/28-1-2/elektro06.pdf
- Adam Pracownik, Grzegorz SIEKLUCKI, Maciej TONDOS Cyfrowy obserwator LQ w układzie 2-masowym — Digital LQ observer in two-mass system // Elektrotechnika i Elektronika : półrocznik Akademii Górniczo-Hutniczej im. Stanisława Staszica w Krakowie ; ISSN 1640-7202. — Tytuł poprz.: Elektrotechnika. — 2010 t. 29 z. 1–2, s. 14–19. — Bibliogr. s. 19, Streszcz.. — tekst: https://journals.bg.agh.edu.pl/ELEKTROTECHNIKA/29-1-2/Elektro_1-2-2010_03.pdf
- Józef GROMBA, Grzegorz SIEKLUCKI, Sylwester SOBIERAJ Czasy realizacji algorytmów PID2DOF w sterownikach serii S7 — Speed of the PID algorithm written in Structured Control Language (SCL)// Przegląd Elektrotechniczny / Stowarzyszenie Elektryków Polskich ; ISSN [phone]. — 2019 R. 95 nr 9, s. 193–197. — Bibliogr. s. 197, Streszcz., Abstr.. — tekst: http://pe.org.pl/articles/2019/9/41.pdf
- Grzegorz SIEKLUCKI, Barbara BISZTYGA, Rajmund SYKULSKI, Antoni ZDROJEWSKI, Tadeusz ORZECHOWSKI Discrete-time switching state-space controller of DC drive // Archives of Control Sciences ; ISSN 1230-2384. — 2013 vol. 23 no. 3, s. 333–349. — Bibliogr. s. 348–349
