---
{
 "course_code": "IB_RN",
 "course_name": "Rechnernetze",
 "institution_slug": "ec_d_ingolst01__info",
 "source_url": "https://www.thi.de/fileadmin/daten/fakultaetI/Modulhandbuecher/MHBuch_INF-B.pdf",
 "source_language": "de",
 "ects_catalog": 7.0,
 "blocks_found": {
  "contents": true,
  "learning_outcomes": true,
  "assessment": true,
  "bibliography": true,
  "prerequisites": true
 },
 "fetched_at": "2026-11-20T12:29:03",
 "content_sha256": "aeeaacf28a4d9c697f47076150f85c31446d7182ac6f583eda2e4cbd5e571934"
}
---

# Rechnernetze

50 Rechnernetze
Modulkürzel: IB_RN SPO-Nr.: 11
Zuordnung zum Curriculum:
Studiengang u. -richtung Art des Moduls Studiensemester Informatik (SPO WS 18/19) Pflichtfach 2
Modulattribute: Unterrichtssprache Moduldauer Angebotshäufigkeit
Deutsch 1 Semester nur Sommersemester
Leistungspunkte / SWS: 7 ECTS / 6 SWS
Arbeitsaufwand: Kontaktstunden: 117 h
Selbststudium: 58 h
Gesamtaufwand: 175 h
Lehrveranstaltungen des
Moduls:
11.1: Rechnernetze 11.2: Praktikum Rechnernetze

## Lehrformen des Moduls

11.1: SU/Ü - seminaristischer Unterricht/Übung 11.2: Pr - Praktikum Verwendbarkeit für andere Studiengänge:
Die Verwendbarkeit für andere Studiengänge kann der Fächeranerkennungsliste der Fakultät I entnommen werden.

## Prüfungsleistungen

11.1: schrP90 - schriftliche Prüfung, 90 Minuten 11.2: LN - ohne/mit Erfolg teilgenommen
Weitere Erläuterungen:
Das Bestehen von 11.2 ist Voraussetzung für die Teilnahme an 11.1.
Prüfungsvorleistung: Erfolgreiches Bestehen des integrierten Praktikums mittels Durchführung von mi ndestens 7 Versuchen. Findet das Praktikum im Online-Betrieb statt, genügt die erfolgreiche Durchführung von 4 Versuchen.
Voraussetzungen gemäß SPO:
keine

## Empfohlene Voraussetzungen

Vertrautheit mit heute üblichen netzwerkfähigen Endgeräten (PC, Tablet, DSL -Router, WLAN Access Point, Smart Watch, Alexa, Drucker)

## Angestrebte Lernergebnisse

Nach dem Besuch der Vorlesung sind die Studierenden in der Lage,  Grundlagen der Rechner- und Datenkommunikation, deren Protokolle und Methoden zu verstehen  das Dienste- und Schichten-Konzept des TCP/IP-Architekturmodells und die grundlegende Verteilung der Funktionen zu erklären  die wesentlichen Funktionen der Sicherungsschicht (Framing, Fehlersicherung ) zu beschreiben  die Prinzipien und Parameter zum Mehrfachzugriff in Lokalen Netzen (Ethernet / WLAN) zu beschreiben und Leistungsabschätzungen damit durchzuführen  die Protokoll-Mechanismen für die Sicherung einer Daten-Paket-Übertragung (Sliding Window) zu erklären 51  IP-Adressbereiche zu strukturieren und Subnetze zu bilden  die Grundfunktionen eines Routers zu nennen  die klassischen Routingprotokolle zu erklären und können die Algorithmen zur Erstellung der Routingtabellen anwenden  die Mechanismen des Transportprotokolls TCP im Detail zu beschreiben und können das Verhalten e iner TCP-Verbindung anhand der Systemparameter ingenieurmäßig ableiten und bewerten  sich selbständig vertiefende Spezialkenntnisse anzueignen, wie auch aufbauende Lehrveranstaltungen zu besuchen Nach dem Besuch des Praktikums  haben die Studierenden schwerpunktmäßig die in der Vorlesung erworbenen theoretischen Kenntnisse selbst erprobt und z.T. selbst implementiert.  haben die Studierenden in einer vorgegebenen Simulationsumgebung für Ausbildungszwecke Module zu Kernfunktionen der Rechnerkommunikation in C++ selbst implementiert und erprobt.  haben die Studierenden an realen, aktuellen Systemen der Rechnerkommunikation (Schnelle Ethernet- Switche, Router, Hubs) selbst gearbeitet und Aufbau und Funktion einfacher Lokaler Netze selbst durchgeführt.  beherrschen die Studierenden die Grundfunktionen im Ethernet und den typischen Komponenten di eser Netze.  haben die Studierenden moderne, komplexe Ethernet-Switche für große Enterprise-Netze kennengelernt, diese selbst administriert und damit größere Netze selbst aufgesetzt. Dabei haben sie sich auch intensiv mit den Protokollen befasst, die für große Ethernet-Netze erforderlich sind (z.B. Spanning Tree, Virtuelle-LAN)  sind den Studierenden die wesentlichen Elemente einer Datenkommunikation im LAN bekannt und selbst erprobt. Die Konfiguration einfacher Netze sollte jetzt von den Absolventen durchgeführt werden können.

## Inhalt

Vorlesung:
 Grundlegendes Verständnis der Rechner- und Datenkommunikation mit Schwerpunkt Paketvermittlung, Architektur-/Schichten-Modell: Protokoll / Dienst  Grundlagen der Bitübertragung: Grundlagen und Relevante Eigenschaften eines Mediums; Bitrate / Baudrate / Leitungscodierung / Modulationsverfahren  Grundlagen der Sicherungsschicht: Methoden zur Abgrenzung eines Datenpaketes (Framing); Fehlers icherung mit Zyklischen Codes (CRC); Mehrfachzugriff in Lokalen Netzen; Elemente für Ether net-Netze (Hub / Switch / VLAN); Wireless LAN / Wi-Fi / Anforderungen und Zugriffsverfahren, Protokoll-Varianten von 802.11; Protokoll-Mechanismen für die Sicherung und Steuerung einer Daten-Paket-Übertragung (Sliding Window)  Grundlagen der Vermittlungsschicht (IP): IP-Adressen: Struktur und Aufbau, IP-Subnetze, ARP (IPv4); Routing-Grundfunktionen und Struktur eines Routers, Routingprotokolle, Algorithmen dazu; Struktur der IPv6-Adressen  Grundlagen der Transportschicht (TCP / UDP): Multiplexen in der Transp ortschicht und NAT  Eigenschaften UDP  Eigenschaften TCP und Verhalten einer TCP-Verbindung (Datentransfer und Fehlersicherung, Fluss- Kontrolle, TCP-Stau-Kontrolle, Abschätzen des Durchsatzes einer TCP-Verbindung)
Praktikum:
 Übungen an einer Simulationsumgebung für Protokolle. Dies umfasst die Implementierung und den Test von Basisfunktionen wie z.B. Framing / Bitstuffing, Berechnung des Zyklischen Prüfcodes zur Fe hlererkennung (CRC)  Übungen an und mit realen, aktuellen Systemen der Rechnerkom munikation (Schnelle Ethernet- Switche, Router, Hubs): Aufbau einfacher Lokaler Netze (Hantieren mit unterschiedlichen Netzwerk - Kabeln und Verbindungstypen); Funktionen im Ethernet: (Adresszuordnung (ARP), Funktionen und Lei stungsfähigkeit der Vernetzungssysteme Hub und Switch); Administration moderner, komplexer Ethernet-Switche für große Enterprise-Netze; Protokolle und Funktionen für den Betrieb großer Ethernet - 52
Netze: Spanning Tree und Virtuelle LAN; Einfaches Routing zwischen VLAN und Design und Konfigur ation von einem gerouteten Netz mit vollwertigen Routern.

## Literatur

 SCHREINER, Rüdiger, 2019. Computernetzwerke: von den Grundlagen zur Funktion und Anwendung  [online]. München: Hanser PDF e-Book. ISBN 978-3-446-46010-2. Verfügbar unter:
https://doi.org/10.3139/9783446460102.  KUROSE, James F. und Keith W ROSS, 2014 . Computernetzwerke : der Top-Down-Ansatz . 6. Auflage.
Hallbergmoos: Pearson Studium. ISBN 978-3-86894-237-8 ; 978-3-86326-686-8  TANENBAUM, Andrew S. und David WETHERALL, 2012. Computernetzwerke. 5. Auflage. München [u.a.] : Pearson Studium - IT. ISBN 978-3-86894-137-1 ; 3-86894-137-1 siehe Vorlesung Rechnernetze  Ohne Autor. Empfehlungen der IETF (Spezifikationen zum Internet) [online]. [Zugriff am: 25.09.2023].
Verfügbar unter: https://www.ietf.org/rfc/

## Anmerkungen

Keine Anmerkungen
