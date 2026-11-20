---
{
 "course_code": "EELTS.Ii40.06333.26",
 "course_name": "AVR Microcontrollers in Engineering Applications",
 "institution_slug": "ec_pl_krakow02",
 "source_url": "https://sylabusy.agh.edu.pl/en/document/0d595662-79f7-4d86-953a-610990118b5b.html",
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
 "content_sha256": "44268d88ba2295e0d569d57bca750eaaca7c273b4253633b00e9827e94413c04"
}
---

# AVR Microcontrollers in Engineering Applications

## Basic information

- **Field of study**: Electrical Engineering
- **Major**: -
- **Organisational unit**: Faculty of Electrical Engineering, Automatics, Computer Science and Biomedical Engineering
- **Study level**: First-cycle (engineer) programme
- **Form of study**: Full-time studies
- **Profile**: General academic

- **Didactic cycle**: 2026/2027
- **Course code**: EELTS.Ii40.06333.26
- **Lecture languages**: Polish
- **Mandatoriness**: Elective
- **Block**: General Modules
- **Course related to scientific research**: Yes

- **Period**: Semester 7
- **Method of verification of the learning outcomes**: Completing the classes; Activities and hours; Lectures: 28 Laboratory classes: 20
- **Number of ECTS credits**: 4

## Goals

- **C1**: Moduł pozwala na zapoznanie się z mikrokontrolerami AVR ATxmega i możliwościami ich zastosowań w sterowaniu i technice pomiarowej.

## Course's learning outcomes

| Code | Outcomes in terms of | Learning outcomes prescribed to a field of study | Methods of verification |
|---|---|---|---|
| Knowledge – Student knows and understands: |  |  |  |
| W1 | Ma wiedzę dotyczącą architektury mikrokontrolerów rodziny AVR | ELT1A_W07 | Test |
| W2 | Ma wiedzę na temat działania i obsługi urządzeń peryferyjnych (portów uniwersalnych wejść/wyjść, przetworników A/C, C/A, liczników/czasomierzy) dostępnych w mikrokontrolerach AVR | ELT1A_W05, ELT1A_W07 | Test |
| W3 | Ma wiedzę na temat działania podstawowych szeregowych interfejsów komunikacyjnych w mikrokontrolerach AVR: USART, I2C (TWI), SPI | ELT1A_W05, ELT1A_W07 | Test |
| W4 | Zna technikę dołączania urządzeń zewnętrznych do mikrokontrolera i podstawy projektowania interfejsów wejść i wyjść | ELT1A_W07 | Test |
| W5 | Zna podstawowe techniki programowej obsługi szeregowych interfejsów komunikacyjnych | ELT1A_W05 | Test |
| W6 | Zna podstawowe sposoby wykorzystania wbudowanych urządzeń peryferyjnych do pomiaru podstawowych wielkości (napięcie, okres (częstotliwość), wypełnienie itp.) | ELT1A_W05 | Test |
| W7 | Ma wiedzę dotyczącą organizacji oprogramowania mikrokontrolerów 8-bitowych i sposobów jego testowania i uruchamiania | ELT1A_W05 | Test |
| Skills – Student can: |  |  |  |
| U1 | Umie programowo obsłużyć urządzenia peryferyjne mikrokontrolera (porty I/O, liczniki/czasomierze, przetworniki A/C i C/A) | ELT1A_U09 | Execution of laboratory classes, Report |
| U2 | Umie zaprojektować sprzęt prostych interfejsów do obsługi wybranych sygnałów wejściowych i wyjściowych cyfrowych oraz analogowych | ELT1A_U09 | Execution of laboratory classes, Report |
| U3 | Umie zaprojektować oprogramowanie dla mikrokontrolera obsługujące podstawowe urządzenia oraz uruchomić i przetestować je korzystając ze zintegrowanych środowisk programistycznych | ELT1A_U09 | Execution of laboratory classes, Report |
| U4 | Umie ocenić przydatność danego mikrokontrolera do rozwiązania danego zadania i opracować proste interfejsy wejść/wyjść | ELT1A_U09 | Execution of laboratory classes, Report |
| Social competences – Student is ready to: |  |  |  |
| K1 | Potrafi w kreatywny sposób wykorzystywać możliwości współczesnych mikrokontrolerów | ELT1A_K01, ELT1A_K02 | Test |
| K2 | Potrafi korzystać z materiałów i wiedzy dostępnej na specjalistycznych portalach internetowych | ELT1A_K01, ELT1A_K02 | Test |

## Student workload

- **Activity form**: Average amount of hours* needed to complete each activity form
- **Lectures**: 28
- **Laboratory classes**: 20
- **Preparation for classes**: 15
- **Realization of independently performed tasks**: 30
- **Examination or final test/colloquium**: 2
- **Contact hours**: 3
- **Preparation of project, presentation, essay, report**: 15
- **Student workload**: Hours 113
- **Workload involving teacher**: Hours 48

* hour means 45 minutes

## Program content

| No. | Program content | Course's learning outcomes | Activities |
|---|---|---|---|
| 1. | Budowa i podstawowe parametry mikrokontrolerów AVR. Architektura 8-bitowych mikrokontrolerów rodziny AVR. Parametry elektryczne układów. Przegląd dostępnych urządzeń peryferyjnych. Procesor i mapa pamięci mikrokontrolerów na przykładzie układów rodziny AVR ATmega i ATxmega. | W1, K2 | Lectures |
| 2. | Budowa i obsługa portów uniwersalnych wejść/wyjść. Budowa podsystemu uniwersalnych wejść/wyjść (PORT) na przykładzie mikrokontrolerów ATxmega. Programowanie konfiguracji końcówki jako wyjścia i/lub wejścia o wymaganych własnościach. Przegląd rejestrów do obsługi podsystemu PORT. Przykłady obsługi podsystemu PORT w języku C. | W1, W2, W4, W5, W7, U1, U3, U4, K1, K2 | Lectures, Laboratory classes |
| 3. | System przerwań i system zdarzeń w mikrokontrolerach ATxmega. Źródła przerwań, wektor przerwań. Priorytety przerwań. Kontroler przerwań PMIC. Przegląd rejestrów do obsługi przerwań. Zasady pisania funkcji obsługi przerwań. System zdarzeń EVSYS. | W1, W2, U1, U4, K1, K2 | Lectures, Laboratory classes |
| 4. | Budowa i obsługa peryferiów analogowych (ADC, DAC, AC). Budowa przetworników A/C (ADC) i C/A (DAC) oraz komparatora analogowego (AC) stosowanych w mikrokontrolerach AVR ATxmega. Przegląd rejestrów do obsługi. Przerwania generowane przez te urządzenia. Przykłady programowej obsługi ADC, DAC i AC bez i z wykorzystaniem przerwań i/lub systemu zdarzeń. | W1, W2, W4, W6, W7, U1, U2, U3, U4, K1, K2 | Lectures, Laboratory classes |
| 5. | Budowa i obsługa podsystemu liczników/czasomierzy. Budowa podsystemu uniwersalnych liczników czasomierzy stosowanych w mikrokontrolerach rodziny ATxmega. Źródła sygnału zegarowego dla liczników. Konfiguracja podsystemu liczników/czasomierzy w trybie porównania i przechwytywania. Przerwania od podsystemu czasomierzy. | W1, W2, W4, W6, W7, U1, U2, U3, U4, K1, K2 | Lectures, Laboratory classes |
| 6. | Zastosowania podsystemu liczników/czasomierzy w trybie porównania. Wykorzystanie liczników/czasomierzy do generowania impulsów o zadanym czasie oraz przebiegów prostokątnych o zadanej częstotliwości, wypełnieniu i przesunięciu. Przykłady obsługi liczników/czasomierzy w trybie porównania. | W1, W2, W6, W7, U1, U3, K1, K2 | Lectures, Laboratory classes |
| 7. | Zastosowania podsystemu liczników/czasomierzy w trybie przechwytywania. Wykorzystanie liczników/czasomierzy do pomiaru czasu trwania impulsu, okresu i wypełnienia przebiegu prostokątnego, przesunięcia między dwoma przebiegami. Przykład zastosowania liczników/czasomierzy do pomiaru parametrów przebiegów prostokątnych. | W1, W2, W6, W7, U1, U3, K1, K2 | Lectures, Laboratory classes |
| 8. | Podstawowe informacje o szeregowych interfejsach komunikacyjnych. Charakterystyka standardów transmisji USART, I2C (TWI) i SPI. Budowa kontrolerów USART, TWI i SPI w mikrokontrolerach rodziny ATxmega. Rejestry i obsługa programowa poszczególnych interfejsów. Wykorzystanie i obsługa przerwań generowanych przez kontrolery USART, TWI i SPI. | W1, W3, W5, W7, K1, K2 | Lectures |
| 9. | Budowa i obsługa podsystemu generatora zegarowego, zarządzania energią i resetowania. Budowa generatora sygnału zegarowego i podsystemu zarządzania energią mikrokontrolerów serii ATxmega. Dystrybucja sygnału zegarowego do poszczególnych bloków układu. Układ resetowania mikrokontrolera. Programowe możliwości obniżania zużycia energii. | W1, W2, W7, U4, K1, K2 | Lectures, Laboratory classes |
| 10. | Podsystem pamięci Flash i EEPROM. Organizacja pamięci programu Flash i pamięci nieulotnej EEPROM w mikrokontrolerach AVR. Konfiguracja sekcji pamięci Flash. Zabezpieczanie zawartości pamięci Flash. Obsługa pamięci EEPROM. | W1, W7, U1, U4, K1, K2 | Lectures, Laboratory classes |
| 11. | Przegląd dostępnych mikrokontrolerów AVR. (2 godz.) Przegląd uniwersalnych mikrokontrolerów rodziny AVR ATtiny, AVR ATmega i AVR ATxmega. | W1, W2, W3, W7, U4, K1, K2 | Lectures |

## Extended information/Additional elements

### Teaching methods and techniques :

Lectures, Discussion

| Activities | Methods of verification | Credit conditions |
|---|---|---|
| Lectures | Test | Patrz "Warunki i sposób zaliczenia poszczególnych form zajęć" i "Zasady udziału w zajęciach" |
| Lab. classes | Execution of laboratory classes, Report | Patrz "Warunki i sposób zaliczenia poszczególnych form zajęć" i "Zasady udziału w zajęciach" |

### Rules of participation in given classes, indicating whether student presence at the lecture is obligatory

Lectures: Studenci uczestniczą w zajęciach poznając kolejne treści nauczania zgodnie z syllabusem przedmiotu. Studenci winni na bieżąco zadawać pytania i wyjaśniać wątpliwości. Rejestracja audiowizualna wykładu wymaga zgody prowadzącego. Laboratory classes: Studenci wykonują ćwiczenia laboratoryjne zgodnie z materiałami udostępnionymi przez prowadzącego. Student jest zobowiązany do przygotowania się w przedmiocie wykonywanego ćwiczenia, co może zostać zweryfikowane kolokwium w formie ustnej lub pisemnej. Zaliczenie zajęć odbywa się na podstawie zaprezentowania rozwiązania postawionego problemu. Zaliczenie modułu jest możliwe po zaliczeniu wszystkich zajęć laboratoryjnych.

## Literature

Obligatory

- Dokumentacja elektroniczna mikrokontrolerów rodziny AVR ATxmega (www.microchip.com).
- Francuz T.: AVR. Układy peryferyjne, Wyd. Helion, 2014.
- Francuz T.: Język C dla mikrokontrolerów AVR. Od podstaw do zaawansowanych aplikacji, Wyd. Helion, 2015.

Optional

- Dokumentacja elektroniczna mikrokontrolerów rodzin AVR ATmega i AVR ATtiny (www.microchip.com).
- Baranowski R.: Mikrokontrolery AVR ATmega w praktyce, Wyd. BTC, 2005.

## Scientific research and publications

Publications

- Algorytmy zamiany odczytów czasowych liczników energii na wirtualne odczyty zdarzeniowe — Algorithms for conversion the time-driven energy meters readings to virtual event-driven readings / Zbigniew MIKOŚ, Marcin JACHIMSKI, Grzegorz WRÓBEL, Grzegorz HAYDUK, Paweł KWASNOWSKI // Zeszyty Naukowe Wydziału Elektrotechniki i Automatyki Politechniki Gdańskiej ; ISSN 2353-1290. — Tytuł poprz.: Zeszyty Naukowe Wydziału Elektrycznego Politechniki Gdańskiej ; ISSN: 1425-5766. — 2016 nr 49, s. 69–74. — Bibliogr. s. 73, Streszcz.. — MKM 2016 : XLVIII Międzyuczelniana Konferencja Metrologów : Kraków, 5–7 września 2016
- Środowisko ISaGRAF do tworzenia rozproszonych aplikacji sterowania i regulacji — [ISaGRAF environment for distributed control and regulation application development] / Zbigniew MIKOŚ, Grzegorz WRÓBEL, Grzegorz HAYDUK, Paweł KWASNOWSKI, Marcin JACHIMSKI, Henryk Zygmunt // W: Systemy czasu rzeczywistego : postępy badań i zastosowania : praca zbiorowa / pod red. Zbigniewa Zielińskiego. — Warszawa : Wydawnictwo Komunikacji i Łączności, 2009. — ISBN: 978-83-206-1746-7. — S. 43-62. — Bibliogr. s. 62
