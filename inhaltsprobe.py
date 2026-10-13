#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inhaltsprobe — haelt eine fertige `<klient>_analyse.md` gegen ihre
`<klient>_chart_data.md`.

Warum es dieses Modul gibt (Startprompt `claude/STARTPROMPT_Inhaltsprobe_2026-09-16.md`,
Chris-Auftrag vom 16.09.2026): Rund dreissig inhaltliche Gegenproben stehen in
Datenblatt-, Klartext-, Innere-Arbeit- und Typmodul. Alle laufen in demselben Lauf,
der den Text gerade geschrieben hat, still und ohne Ergebniszeile — und keine
Funktion haelt die Analyse gegen das Datenblatt. `build.verify()` prueft Struktur
und Layout, `build.aspekt_heimat()` die Themenliste gegen die Aspekttabellen: beides
INNERHALB einer Datei, nie zwischen den beiden. Der "erfundene Aspekt" (liest sich
praezise und ist falsch) hatte bis zu diesem Modul keine einzige Pruefung.

Die Inhaltsprobe prueft, sie beurteilt nicht: Ob eine Deutung trifft, kann kein
Skript sagen. Was sie meldet, ist falsch oder regelwidrig, mit Stelle. Sie kostet
null Token je Lauf und laeuft in Schritt 2 (nach dem Schreiben) und in Schritt 3+4
(vor dem Rendern) — s. `lade.SCHRITTE`.

Sprachfassung (2026-09-16d, Reparatur nach dem Pruefbericht Geburtshoroskop
Schritt 3+4 vom selben Tag, Klasse 1 Nr. 1.2): Die Probe liest seither auch die
ENGLISCHE Analyse (Modul Sprachfassung) — englische Faktor- und Zeichennamen,
Aspektwoerter (beide Schreibweisen: semi-sextile/semisextile), Hausangaben
("4th house", "fourth house", "11th/10th house"), die Kicker Prelude / Account /
Closing Word / Core Themes / Fields of Conflict / Life Tasks, den Typ aus einer
englischen H1 ("Birth Chart"), die englischen Bewegungs-Wortlaute des
Geburtshoroskops und uebersetzte Wortlisten fuer P8/P9. Die chart_data bleibt
deutsch; deshalb entfaellt bei einer englischen Analyse allein der Titelvergleich
in P3 (Hinweiszeile).

Zugang-Kicker (2026-09-16, Reparatur nach dem Pruefbericht Geburtshoroskop
Schritt 1+2 vom selben Tag, Klasse 1 Nr. 1.2 und 1.3): Ein Zugang-Kapitel traegt
seit dem Typmodul-Stand vom 16.09. den Kicker `Zugang <Bereich>` (`Zugang Beruf`,
`Zugang Partnerschaft`) — `build.parse_analyse()` fuehrt den Kicker als
Kapitelschluessel und wies zwei Kapitel `Zugang` als „Kapitel doppelt" ab. Die
Probe erkannte den Zugang bis dahin nur am nackten Kicker und las ein Kapitel
`Zugang Beruf` als Normal-Beleg: P2 meldete Segment 1 als FEHLER, P1 vierzehnmal
PRUEFEN. Seither zaehlt jeder Kicker, der mit `Zugang` (englisch `Access`) beginnt,
als Zugang (`_ist_zugang()`); der nackte Kicker gilt fuer aeltere Analysen weiter.

Schnittstelle
-------------
    inhaltsprobe.pruefe(analyse_pfad, chart_data_pfad, typ=None, events_pfad=None) -> dict
    inhaltsprobe.bericht(analyse_pfad, chart_data_pfad, typ=None, events_pfad=None) -> str
    python3 inhaltsprobe.py <analyse.md> <chart_data.md> [--typ geburt|transit]
                            [--events <klient>_Transit_events.json]
    python3 inhaltsprobe.py --selbsttest

`events_pfad` / `--events` (2026-09-19, W24): die events.json des Transit-Laufs
(`transit.py … --json <pfad>`, Schema in `transit.run()`). Mit ihr haelt P1 jedes
Transit-Segment gegen die Rechnung, P5 nimmt die Soll-Menge des Registers aus
`build.kontakt_heimat()`, P11 und P13 zaehlen ihre Daten, Lebensalter und Kontakte
als Fundstelle. Ohne sie prueft P1 nur die Form der Transit-Segmente und meldet den
Abgleich als „teilweise übersprungen" mit Grund; P5 nimmt die Soll-Menge dann aus dem
Block TRANSIT-RECHENSCHAFT der chart_data. Eine events.json, die sich nicht lesen
laesst, ist wie eine unlesbare Analyse: Abbruch mit Rueckgabewert 2.

`typ` wird aus der H1 der Analyse abgeleitet (Dokumenttyp links vom " — "); der
Parameter ueberstimmt. Ein unbekannter Typ laeuft mit den typunabhaengigen Proben,
die typabhaengigen werden als uebersprungen gemeldet — nie geraten.

Rueckgabewert der CLI: 0 ohne FEHLER, 1 mit FEHLER, 2 wenn eine der beiden Dateien
nicht lesbar ist (SchemaError aus `build.parse_analyse()`, fehlende Datei).

Wiederverwendet, nicht nachgebaut: `build.parse_analyse()` (Kapitel mit kicker,
title, signatur, beleg, blocks), `build.lies_deckblatt()` (Leitsatz),
`selektor.parse_chart()` (Faktoren, Zeichen, Haeuser, Achsen aus dem
`@@SELEKTOR`-Block), `selektor.norm()` / `norm_faktor()` (Namensnormalisierung).
Die Regexe fuer Aspekttabellen und Themenliste sind woertlich aus
`build.aspekt_heimat()` und `build._ressourcen_zeilen()` uebernommen — dort sind sie
verschachtelt und nicht importierbar; die Fundstelle steht jeweils im Kommentar,
damit eine spaetere Aenderung an einer Stelle die andere findet. `build.py` selbst
wird nicht geaendert.

Zwei Schweregrade, sonst nichts
-------------------------------
FEHLER   eindeutig, mechanisch entscheidbar (Aspekt nicht in der Tabelle, Orb
         weicht ab, falscher Fuehrer, fehlende Bewegung, fehlende Registerzeile,
         Leitsatz nicht im Schlusswort).
PRUEFEN  ein Treffer, der ein Auge braucht (Wortlisten, Stufe im Beleg, Titel
         weicht von der Themenliste ab, Suedknoten-Aspekt als Spiegel).
Dazu AUSSAGELOS: Findet eine Probe nichts, was sie pruefen koennte — keine
Beleg-Segmente, keine Themenliste, kein Rechenschaftskapitel —, meldet sie das
ausdruecklich und nie "bestanden". Der stille Freispruch ist der Fehler, der in
`aspekt_heimat()` zweimal gebaut wurde (06.09. und 14.09.); er wird hier nicht ein
drittes Mal gebaut. UEBERSPRUNGEN heisst: bewusst nicht gelaufen (Typ unbekannt,
kein Rechenschaftskapitel im Typ, englische Analyse bei P11/P12) — mit Grund.
TEILWEISE UEBERSPRUNGEN (2026-09-19, W44): Was eine laufende Probe bewusst nicht
prueft (der Getriebe-Beleg in P1, der Abgleich gegen events.json ohne `--events`),
steht mit Grund unter der Probe und zaehlt in die Schlusszeile „s übersprungen" —
vorher stand es nur als Hinweis, und die Schlusszeile meldete „0 übersprungen".

Die achtzehn Proben
-------------------
P1  Beleg-Aspekte    jedes Aspekt-Segment eines Normal-Belegs (Faktor A, Aspektart,
                     Faktor B, Orb) muss so in einer der vier Aspekttabellen stehen,
                     Orb auf 1' genau; Stufe (voll/einseitig/neben) nur PRUEFEN.
                     Instrument- und Zugang-Beleg: nur die Aspektangaben hinter den
                     Staenden; Getriebe-Beleg (Struktur-Format) teilweise
                     uebersprungen (zaehlt in die Schlusszeile). Eine Zeile der
                     vier Aspekttabellen, die sich nicht lesen laesst (fremde
                     Glyphe, Orb nicht N°NN′), ist ein FEHLER mit Grund — vorher
                     lief sie still vorbei (2026-09-19, F2); gelesen werden alle
                     Glyphen aus ASPEKTE, darunter ∠ Halbquadrat und ⚼
                     Anderthalbquadrat, und der Wort-Trenner –Wort–.
                     TRANSIT (2026-09-19, W24, W10): das Segment
                     `T-X Aspekt R-Y — exakt TT.MM.JJJJ, …` wird auf seine Form
                     geprueft und mit events.json gegen die Rechnung: Kontakt
                     vorhanden, jedes Exaktdatum ein Nulldurchgang (exakt_gesamt),
                     „nicht exakt" nur ohne Nulldurchgang im Fenster, „Annäherung
                     bis x′ am D" gegen `annaeherung`, „am Stichtag Orb 0,57°"
                     gegen `orb_stichtag` (halbe Rundungsbreite), jedes weitere
                     Datum in irgendeinem Feld des Kontakts, der Jetzt-Liste oder
                     der Stationen des Transiters (sonst PRUEFEN). Im Lagebild
                     („Der Stand heute") traegt jedes Kontakt-Segment den Orb am
                     Stichtag in Dezimalgrad statt der Pflicht zum Exaktdatum.
                     Sonnenbogen, progressiver Mond, Finsternis gegen `zusatz`,
                     Profektion mit ihrem Geburtstag (nur PRUEFEN).
P2  Beleg-Staende    Segment 1 jedes Normal-Belegs und jedes Instrument-Segment:
                     Zeichen und Haus gegen den @@SELEKTOR-Block (bei Grenzlage das
                     fuehrende Haus vorn, bei `fuehrung=offen` seit 2026-09-30 das
                     rechnerische), Gradminute gegen die Staendetabelle. Offene
                     Fuehrung (K9): die Signatur des Kapitels, das er fuehrt, sagt
                     „gleich stark" (nur PRUEFEN); einen Satz zur Geburtszeit
                     verlangt sie seit 2026-10-01 nicht mehr — P11 meldet ihn.
P3  Kapitel/Themen   die nummerierten Themenkapitel in Dokumentreihenfolge
                     gegen die THEMA-Zeilen (seit 2026-09-19, L7: `Kapitel n` ist
                     das Kapitel zu `THEMA n`; in Analysen alter Form, die das
                     Getriebe-Kapitel als `Kapitel 1` fuehren, beginnen sie bei
                     `Kapitel 2` — s. `_zaehlung_ab()`): gleiche Zahl, an
                     jeder Stelle der Fuehrer aus fuehrt= in Segment 1 des Belegs
                     UND in der Signatur; Titel nur PRUEFEN. (Nur Geburtshoroskop —
                     das Kapitel-Skelett der anderen Typen ist hier nicht hinterlegt.)
P4  Bewegungsfolge   je Themenkapitel die ###-Zwischentitel gegen WORTLAUTE[typ]:
                     volle Folge sieben in fester Reihenfolge; Kurzform (form=kurz,
                     Zugang) ohne Wurzel und Widerstand; form=ressource: beides.
P5  Rechenschaft     jeder Faktor des @@SELEKTOR-Blocks, der kein Thema fuehrt,
                     braucht eine Zeile im Kapitel `Rechenschaft`, die mit seinem
                     Namen beginnt; eine Zeile fuer einen Fuehrer: PRUEFEN. Achsen
                     zaehlen nicht, der Suedknoten mit eigener FAKTOR-Zeile schon.
                     TRANSIT (2026-09-19, W43): das Register heisst `Mitlaufendes`;
                     jeder primaere Wirkorb-Kontakt im Fenster, der kein Thema
                     FUEHRT, braucht eine Zeile, die Transiter und Ziel nennt (und,
                     wo sie ein Aspektwort traegt, das richtige); klingt er in einem
                     Kapitel mit, nennt die Zeile das Kapitel (sonst PRUEFEN).
                     Soll-Menge mit events.json aus build.kontakt_heimat(), ohne sie
                     aus dem Block TRANSIT-RECHENSCHAFT (+ mitklingende Kontakte aus
                     `aspekte=` als PRUEFEN).
                     KAPITELANGABEN (2026-10-13, Strang 3 des Wartungslaufs „Proben
                     fuer Zeit, Naehe, Register und Fundstellen“): Jede Zeile nennt
                     jedes Kapitel, dessen THEMA den Faktor in `klingt=` oder
                     `aspekte=` traegt und dessen Signatur oder Lesetext ihn nennt —
                     Achsen eingeschlossen; eine Angabe „klingt … in Kapitel n“,
                     deren Kapitel den Faktor nicht nennt, ist leer; der Satz „Mit
                     dem <Faktor> haben Kapitel … zu tun“ gilt gegen dieselbe Menge.
                     Im Transit braucht ein `klingt=`-Kontakt, den sein Kapitel in
                     einem Satz nennt, die Kapitelangabe, und eine Angabe ohne Satz
                     und ohne `aspekte=` ist leer. Nur PRUEFEN.
P6  Leitsatz         LEITSATZ aus @@DECKBLATT im Schlusswort (wortgleich nach
                     Leerraum-Normalisierung, ersatzweise vier Fuenftel der Woerter
                     in Reihenfolge); genau EINE THEMA-Zeile mit leitachse=ja.
P7  Signatur         der Fuehrer steht in der Signatur — eigene Ergebniszeile,
                     inhaltlich in P3 mitgeprueft.
P8  Wortlisten       ueber den Fliesstext aller Kapitel ausser Auftakt und
                     Rechenschaft, nie ueber Signatur und Beleg: Dritte (Innere
                     Arbeit, Prinzip 13), Vergangenheits-Indikativ (Prinzip 5),
                     Fachbegriffe, Gradzahlen und Hausnummern in Ziffern
                     (Klartext-Verbotsscan; Liste aus `restyle.VERBOTEN`). Nur PRUEFEN.
P9  Zwei Saetze      der Nichtwissens-Satz in jeder Wurzel-Bewegung ("weiss ich
                     nicht" oder "steht in keinem Horoskop"); die
                     Verwerfungs-ERLAUBNIS ausserhalb von Auftakt und erstem
                     Themenkapitel. Nur PRUEFEN. Der Transit-Auftakt `Zur Lesart`
                     zaehlt als Auftakt (2026-09-19, W23 — auch fuer P8 und P10).
P10 Wortscan        die vier Listen der Inneren Arbeit, Probe 9 — Superlative
                     (Prinzip 8), Klinisches (Guardrail Pathologisierung),
                     Bestaetigung und Optimierung (Prinzipien 12 und 14), Zeit
                     als Frist oder Ereignis (Prinzip 15). Seit dem 2026-09-17
                     hier statt als Modelltext im Modul: Die Listen waren mit
                     Ausnahmeklauseln gegen ihre eigenen Fehlalarme gewachsen
                     (IC-Fuegung, "am dichtesten verschaltet"), und zwei weitere
                     Fehlalarm-Klassen standen offen — "Zerstoerung" traf
                     "Stoerung", "solltest du" traf die von Prinzip 12 VERLANGTE
                     Lassen-Formulierung. Beides ist hier eine Zeile. Nur
                     PRUEFEN. Der Superlativ-Deckel (einer je gedeutetem
                     Kapitel, mindestens drei) zaehlt nur die Treffer dieser Liste; „zum tiefsten Punkt" gilt als IC-Fuegung
                     wie die volle Form (2026-09-19, W29). Dazu die ZEITFORM der
                     Widerstands-Bewegung (2026-09-19, W4): Perfekt und Praeteritum
                     („Er hat dich geschützt", „It has spared you") — das Argument
                     kommt aus der Form, nicht aus der Geschichte.
P11 Zahlen-Deckung   (2026-09-19, U1 a) jedes Tagesdatum, jeder Monat, jede
                     Jahreszeit mit Jahr, jede Jahreszahl und jedes Lebensalter im
                     Fliesstext braucht eine Fundstelle in der chart_data (im
                     Transit auch in events.json: Exaktdaten, `fortsetzung`,
                     `fruehere_durchgaenge` mit Alter). Ein Alter gilt als gedeckt,
                     wenn es als Alter dasteht oder ±1,5 Jahre an einem
                     Zyklusfenster (Strukturbild §7) eines im Satz (oder im Satz
                     davor) genannten Faktors liegt; „das n. Lebensjahr" ist Alter
                     n−1. Nur PRUEFEN; englisch mit eigenen Wortlisten (seit
                     2026-09-22). Seit 2026-10-01 dazu jeder Satz zur
                     Geburtsminute — erlaubt ist nur EINER im Auftakt, wenn der
                     Zeitscan „Gegenprobe-Blatt fällig“ meldet.
P12 Rangwoerter      (2026-09-19, U1 b) „die engste", „eine der engsten", „die
                     zweitengste", „die meisten Verbindungen", „einzige", „kein
                     anderer", „x von y", „mehr als die Hälfte", „n Verbindungen",
                     „alle n": wo die Rangzeilen des Strukturbilds (§10, `RANG …`)
                     stehen, gegen sie gehalten — Gleichstand, falsche Zaehlung
                     (gezaehlt/gewichtet), falscher Rang, gewichtete Dichte als
                     Anzahl; ohne Rangzeilen jede Aussage PRUEFEN. Achsen-Spiegel
                     (Knoten △ AC / Knoten ⚹ DC) belegen EINEN Rang. „folgt
                     keinem anderen" steht gegen Strukturbild §3 (Planeten im
                     eigenen Zeichen) — in der Einzahl alle, als Eigenschaft der
                     genannte (2026-09-25); „alle n Jahre" ist eine Umlaufzeit und
                     zaehlt nicht; spricht das Rangwort von Verbindungen, gilt die
                     Verbindungs-Rangzeile (2026-09-24). Seit 2026-09-29 (K1):
                     Klartext-Namen der Modi („die Kraft, zu halten“), ungefaehre
                     Haelften („fast/gut/rund die Hälfte“), „einzigen
                     Verbindungen“ im Plural gegen die Zahl der genannten Partner;
                     „eine einzige Figur“ direkt hinter ist/sind/bilden/ergeben/
                     wird/als („… bilden eine einzige Figur“; nicht nach einer
                     Ortsangabe: „In deinem Bild ist …“) und „alle vier Ecken“
                     zaehlen nicht.
                     Seit 2026-10-12 (W1): Einzigkeit ueber ein Element oder einen
                     Modus in beiden Sprachen („die einzige im Feuer“, „die
                     einzige in einem Zeichen der Anpassung“, „the only one in
                     fire“, „the only carrier of fire“, auch „single“/„sole“),
                     gegen die Zaehlung, die der Satz nennt („zehn Hauptkräfte“,
                     „ten main forces“ = gezaehlt); still nur, wenn dort 1 steht
                     und der genannte Planet der Traeger ist (LESEFORMATE).
                     Nur PRUEFEN; englisch mit eigenen Wortlisten (seit 2026-09-22).
P13 Beleg-Deckung    (2026-09-19, U1 c; Klartext-Regel, Chris-Entscheidung Frage
                     4 = 1) jede im Fliesstext benannte Konstellation — Aspektwort
                     oder Bild der Uebersetzungstabelle zwischen zwei Faktoren —
                     steht im Beleg dieses oder eines anderen Kapitels oder in der
                     Aspekttabelle; im Transit auch als Kontakt der Rechnung. Nur
                     PRUEFEN.
P14 Kopfblock        (2026-09-19, W10, W43) jedes Kapitel gegen die
                     Kopfblock-Tabelle (KOPFBLOCK): fehlt Signatur oder Beleg, wo
                     sie Pflicht sind (Themen-, Getriebe-, Instrument-, Zugang-
                     Kapitel, Lagebild „Der Stand heute"; Signatur der
                     Bündel-Kapitel), oder traegt ein Bündel-Kapitel einen Beleg:
                     FEHLER. Im Lagebild traegt Segment 1 die Staende des zuerst
                     genannten Ziels (sonst PRUEFEN). Traegt kein Kapitel einen
                     Kopfblock (Fachmodus), laeuft P14 nicht.
P15 Ressourcen-Tiefe (2026-09-19, W37) je Zeile des Ressourcen-Blocks am
                     Deutungsort (Thema n, Ressource n, Was trägt) die Saetze ueber
                     den Aspekt: volle und einseitige mindestens drei, Nebenaspekte
                     mindestens einer (Transit: jeder Kontakt drei). Gezaehlt ab
                     dem Satz, der beide Faktoren nennt (oder zwei Saetzen, die
                     sie zusammen nennen), bis zu einem Satz nur ueber andere
                     Faktoren. Transit: Deutungsort `Mitlaufendes (Deckel)` fuer
                     Kontakte ueber dem Deckel von sechs — dort genuegt eine Zeile
                     im Kapitel `Mitlaufendes`, die beide Faktoren nennt
                     (2026-09-24). Nur PRUEFEN.
P16 Laenge           (2026-09-24, vorher Skript im Klartext-Modul) die Woerter der
                     gedeuteten Kapitel (Kapitel mit Bewegungsfolge, Getriebe,
                     Instrument; nicht das Lagebild): faellt das Mittel der letzten
                     drei unter 60 % der ersten drei, FEHLER — ausser form=kurz,
                     form=ressource oder duenn=ja erklaert es (Hinweis). Unter vier
                     gedeuteten Kapiteln AUSSAGELOS.
P17 Subjekt          (2026-09-24, Innere Arbeit Pruefung 1) Planet, Achse, Zeichen,
                     Haus mit Ordnungszahl oder „die Seele" als Satzsubjekt: in den
                     Bewegungen 1 und 3–6 jede Subjekt-Stellung, ohne Bewegungsfolge
                     (Getriebe, Instrument, Pflichtteile) nur mit Handlungsverb;
                     Bewegung 2 und 7 bleiben frei (Anker). Seit 2026-09-25 auch
                     der Relativsatz mit handelndem Verb („Saturn, der … trägt").
                     Nur PRUEFEN; englische Fassung uebersprungen.
P18 Satzarten        (2026-10-04, Wartungslauf Satzarten-Probe; Chris-Entscheidung
                     nach den Pruefberichten vom 03./04.10.) Aussagen der Satzarten,
                     in denen seit dem 02.10. Sachfehler standen, gegen Datenblatt
                     und events.json: Leere („dort steht nichts", „ist leer",
                     „allein von X besetzt"), Herrscher (§3, Domizil), Kapitel-,
                     Titel- und Abschnittsverweise, Buendel-Signatur, Modulwoerter
                     im Lesetext, „steht in der Aspekttabelle", Rang neben einem
                     gedeuteten Untergrund-Aspekt (bis 2026-10-13, s. u.), „alles
                     andere"; im Transit
                     Zeitangaben („ab", „beginnt", „zum ersten Mal genau",
                     Zeichenwechsel), Gleichzeitigkeit, Station, Anzahl und der
                     Wiederholungshinweis kontaktgenau. Seit 2026-10-13 (Strang 1
                     des Wartungslaufs „Proben fuer Zeit, Naehe, Register und
                     Fundstellen“) dazu: Grenze („bis <Zeit>“, „von … bis …“,
                     „über das Ende dieses Fensters hinaus“), Wechsel in Zeichen
                     und Haus, Abstand und Reihenfolge („eine Woche nach“, „im
                     Gefolge“, „Dazwischen“, Sonnenbogen), Buendel aus Laeufer- und
                     Zielliste in Fliesstext und Signatur, Genau („genau <Zeiten>“,
                     „folgt“, „geht über“), Kapitelzeit gegen die @@ZEITLEISTE,
                     Dauer („fast die ganzen zwei Jahre“), Zugleich mit einem
                     Laeufer und „In dieselben Wochen“ — auch im Kapitel „Die Zeit“
                     einer Vertiefung. Seit 2026-10-13 (Strang 2) ausserhalb der
                     Zeit-Kapitel die Naehe-, Lage- und Rangwoerter nach Chris'
                     Schwellen: „genau am“, „am selben Punkt wie“, „exakt im
                     <Aspekt>“ bis 1° Orb, „genau dort, wo … sich berühren“ bis 1°
                     zur Hausspitze, Absolutformeln, „eng beieinander“ (Konjunktion
                     je Paar), „mitten in der Ballung“ (kein Randglied), die leere
                     Haelfte „liegt im …“, „der Knotenachse gegenüber“, und der
                     Rang mit „deines ganzen Bildes“ samt jedem Untergrund-Aspekt;
                     dazu „enger als jede andere“, „sonst nirgends“. Nur PRUEFEN und nur bei
                     WIDERSPRUCH zu den Daten — was sich nicht pruefen laesst,
                     bleibt still; jeder Hinweis nennt den Datenwert. Englische
                     Fassung uebersprungen; ohne events.json die Transit-Satzarten
                     teilweise uebersprungen. Lesart: hilfe('LESEFORMATE').
P19 Wiederholung     (2026-10-11, Chris-Entscheidung 2026-10-11: „höchstens zweimal
                     gleich“) Ein Satz, der wortgleich mehr als zweimal im Dokument
                     steht, oder ein Satzanfang, der an derselben Stelle (Bewegung)
                     in mehr als zwei Kapiteln steht. Ausgenommen sind die Wegweiser,
                     die gleich bleiben (WEGWEISER_RE), und die Register (Rechenschaft,
                     im Transit „Mitlaufendes“). Nur PRUEFEN; in einer englischen Fassung nur der wortgleiche Satz.
                     Dieselbe Zaehlung fuer andere Builder: wiederholungen().

Selbsttest: `python3 inhaltsprobe.py --selbsttest` laeuft gegen einen KONSTRUIERTEN
Fall ohne reales Geburtsdatum, ohne Uhrzeit, ohne Namen, ohne Staende eines realen
Charts (Datenschutz-Guardrail des Kerns) — einmal fehlerfrei, einmal mit je einem
eingebauten Fehler je Probe P1–P6 und P11–P15 und je einem Treffer fuer P8, P9,
P10 und P17, einmal mit Zugang-Kapitel; P16 und die Satzmuster von P17 als
Einzelproben; dazu ein Transit-Fall mit konstruierter events.json
(Daten aus Julianischen Tageszahlen gerechnet, kein Datum im Quelltext), fehlerfrei,
mit eingebauten Fehlern und ohne events.json. P18 laeuft auf denselben konstruierten
Faellen mit erfundenen Saetzen (Lauf 12, 13 und 15): je Satzart eine stimmige Fassung, die
still bleiben muss, und eine, die den Daten widerspricht und mit dem Datenwert
gemeldet werden muss. Eine Probe, die ihren Testfehler nicht
findet, ist nicht fertig. Der Selbsttest ist Teil des Moduls und laeuft bei jedem
spaeteren Umbau wieder.

Phase 1 (2026-09-16): Bau des Werkzeugs. Der Aufruf in den Modulen (Datenblatt-,
Klartext-, Design-Render-Modul) ist Phase 2 und kommt erst, wenn die Probe in
mindestens einem echten Prueflauf je Schritt ohne Fehlalarm gelaufen ist.
"""

import os
import re
import sys

_HIER = os.path.dirname(os.path.abspath(__file__))
for _p in (_HIER, "/home/claude"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import build                       # noqa: E402  (Ladeweg: lade("build", "selektor", "inhaltsprobe"))
import selektor                    # noqa: E402

try:                               # restyle traegt die Verbotsliste des Klartext-Moduls
    import restyle as _restyle     # noqa: E402
    VERBOTEN_FACHBEGRIFFE = list(_restyle.VERBOTEN)
except Exception:                  # pragma: no cover — Fallback: Stand restyle.py 2026-09-16
    VERBOTEN_FACHBEGRIFFE = ['°', '′', 'Orb', 'Bogenminute', 'Grad Abstand', 'einseitig',
                             'Nebenaspekt', 'Domizil', 'Exil', 'Exaltation', 'Cazimi',
                             'Apex', 'Dispositor', 'Endherrscher', 'AC-Herrscher',
                             'Chart-Herrscher', 'T-Quadrat']

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

# Die verbindlichen ###-Wortlaute der Bewegungsfolge, abgeschrieben aus den
# Typmodulen am 2026-09-16:
#   geburt    claude/Projektanweisung_Modul_Geburtshoroskop.md, "Die Bewegungsfolge"
#   transit   claude/Projektanweisung_Erweiterung_Transit.md, "Die Bewegungsfolge"
# EA und Ultimativ sind seit dem 2026-09-23 ausgemustert (Chris-Ansage; ihre
# Wortlaute sind entfallen, `AUSGEMUSTERTE_TYPEN` bricht mit Meldung ab).
# Bewegung 1, 2, 4, 5 und 6 sind ueber alle Typen gleich; 3 und 7 typspezifisch
# (Chris-Entscheidung 2026-09-04, Variante B2). Ein Eintrag darf ein Tupel sein:
# dann ist jeder seiner Wortlaute an dieser Stelle gueltig.
_B1 = "Woran du es merkst"
_B2 = "Was da arbeitet"
_B4 = "Der Teil von dir, der das nicht aufgeben will"
_B5 = "Die zwei Formen und das Dazwischen"
_B6 = "Womit du arbeiten kannst"
# Englische Sprachfassung (Modul Sprachfassung; Klartext-Modul, Aktivierung): die
# Wortlaute der englischen Analyse des Pruefflaufs vom 2026-09-16d; fuer den
# Transit seit dem 2026-09-22 (W57).
_E1 = "How you notice it"
_E2 = "What is at work"
_E4 = "The part of you that does not want to give this up"
_E5 = "The two forms and the in-between"
_E6 = "What you can work with"
WORTLAUTE = {
    "geburt":  ((_B1, _E1), (_B2, _E2),
                ("Wie so etwas zur Regel wird", "How something like this becomes a rule"),
                (_B4, _E4), (_B5, _E5), (_B6, _E6),
                ("Wohin das gehört", "Where this belongs")),
    "transit": ((_B1, _E1), (_B2, _E2), ("Warum das alt ist", "Why this is old"),
                (_B4, _E4), (_B5, _E5), (_B6, _E6), ("Zeit", "Time")),
    # 2026-09-22 (Prüflauf Transit 1+2 englisch): englische Spalte der Transit-Wortlaute
    # (W57).
}
TYPEN = ("geburt", "transit")
# 2026-09-23b (Wartungslauf zu den Pruefberichten vom 23.09., Z-23.09. Nr. 3):
# EA und Ultimativ sind ausgemustert. Ein Aufruf mit diesem Typ — per --typ oder
# aus der H1 — bricht mit Meldung ab, statt still mit halben Proben zu laufen.
AUSGEMUSTERTE_TYPEN = ("ea", "ultimativ")

# Jeder Wortlaut, den irgendein Typ kennt — zum Erkennen, OB ein Kapitel eine
# Bewegungsfolge traegt (erstes Themenkapitel, P9), unabhaengig vom Typ.
def _alle_wortlaute():
    out = set()
    def _add(seq):
        for w in seq:
            if isinstance(w, tuple):
                out.update(w)
            else:
                out.add(w)
    for t, v in WORTLAUTE.items():
        if isinstance(v, dict):
            for seq in v.values():
                _add(seq)
        else:
            _add(v)
    return out
ALLE_WORTLAUTE = _alle_wortlaute()

# Faktornamen, wie sie in Beleg, Signatur und Register geschrieben werden, und ihr
# kanonischer Schluessel (derselbe wie in selektor.parse_chart(): Versalien, ASCII).
# Reihenfolge: laengere Schreibweisen zuerst, damit "Mondknotenachse" nicht als
# "Mond" gelesen wird.
_FAKTOR_SCHREIBWEISEN = (
    # englische Schreibweisen (Sprachfassung, 2026-09-16d) — laengere zuerst
    ("Part of Fortune", "GLUECKSPUNKT"), ("North Node", "MONDKNOTEN"),
    ("north node", "MONDKNOTEN"), ("Lunar Node", "MONDKNOTEN"), ("lunar node", "MONDKNOTEN"),
    ("nodal axis", "MONDKNOTEN"), ("South Node", "SUEDKNOTEN"), ("south node", "SUEDKNOTEN"),
    ("Ascendant", "AC"), ("Descendant", "DC"), ("Midheaven", "MC"),
    ("Sun", "SONNE"), ("Moon", "MOND"), ("Mercury", "MERKUR"), ("Neptune", "NEPTUN"),
    ("Mondknotenachse", "MONDKNOTEN"), ("Knotenachse", "MONDKNOTEN"),
    ("Mondknoten", "MONDKNOTEN"), ("Nordknoten", "MONDKNOTEN"),
    ("aufsteigender Knoten", "MONDKNOTEN"), ("aufsteigenden Knoten", "MONDKNOTEN"),
    ("Südknoten", "SUEDKNOTEN"), ("Suedknoten", "SUEDKNOTEN"),
    ("absteigender Knoten", "SUEDKNOTEN"), ("absteigenden Knoten", "SUEDKNOTEN"),
    ("Sonne", "SONNE"), ("Mond", "MOND"), ("Merkur", "MERKUR"), ("Venus", "VENUS"),
    ("Mars", "MARS"), ("Jupiter", "JUPITER"), ("Saturn", "SATURN"),
    ("Uranus", "URANUS"), ("Neptun", "NEPTUN"), ("Pluto", "PLUTO"),
    ("Chiron", "CHIRON"), ("Lilith", "LILITH"), ("Pholus", "PHOLUS"),
    ("Glückspunkt", "GLUECKSPUNKT"), ("Glueckspunkt", "GLUECKSPUNKT"),
    ("Pars Fortunae", "GLUECKSPUNKT"),
    ("Aszendent", "AC"), ("Deszendent", "DC"), ("Medium Coeli", "MC"),
    ("Himmelsmitte", "MC"), ("Imum Coeli", "IC"), ("Immum Coeli", "IC"),
    ("AC", "AC"), ("MC", "MC"), ("DC", "DC"), ("IC", "IC"),
)
_FAKTOR_RE = "(?:%s)" % "|".join(re.escape(s) for s, _ in _FAKTOR_SCHREIBWEISEN)
# Ein Faktorname im Text: mit Wortgrenzen, optional gefolgt von "(AC)"-Klammer.
FAKTOR_RE = re.compile(r"(?<![\wäöüÄÖÜß-])(" + _FAKTOR_RE + r")(?![\wäöüÄÖÜß])"
                       r"(?:\s*\((?:AC|MC|DC|IC)\))?")
_FAKTOR_KANON = {s.casefold(): k for s, k in _FAKTOR_SCHREIBWEISEN}
ACHSEN = ("AC", "MC", "DC", "IC")

def kanon(name):
    """Schreibweise -> kanonischer Schluessel ('Aszendent (AC)' -> 'AC')."""
    n = re.sub(r"\s*\((?:AC|MC|DC|IC)\)\s*$", "", name.strip())
    k = _FAKTOR_KANON.get(n.casefold())
    return k or selektor.norm_faktor(n)

# Anzeigename je Schluessel (fuer Meldungen).
ANZEIGE = {"SONNE": "Sonne", "MOND": "Mond", "MERKUR": "Merkur", "VENUS": "Venus",
           "MARS": "Mars", "JUPITER": "Jupiter", "SATURN": "Saturn", "URANUS": "Uranus",
           "NEPTUN": "Neptun", "PLUTO": "Pluto", "MONDKNOTEN": "Mondknoten",
           "SUEDKNOTEN": "Südknoten", "CHIRON": "Chiron", "LILITH": "Lilith",
           "PHOLUS": "Pholus", "GLUECKSPUNKT": "Glückspunkt",
           "AC": "AC", "MC": "MC", "DC": "DC", "IC": "IC"}

# Aspektarten: Wort, Glyphe, Spiegelbild an einer Achse (AC/DC, MC/IC, Nord-/Suedknoten).
ASPEKTE = (("Anderthalbquadrat", "⚼"), ("Halbquadrat", "∠"), ("Halbsextil", "⚺"),
           ("Konjunktion", "☌"), ("Opposition", "☍"), ("Quadrat", "□"),
           ("Trigon", "△"), ("Sextil", "⚹"), ("Quincunx", "⚻"))
_ASP_WORT = {w: w for w, _ in ASPEKTE}
# englische Aspektwoerter (Sprachfassung, 2026-09-16d): der Anker hiess anfangs
# `semisextile`, die englische Analyse schreibt `semi-sextile` — beide gelten,
# ebenso beide Schreibweisen von semi-square und sesquiquadrate/sesquisquare.
_ASP_WORT_EN = {"conjunction": "Konjunktion", "opposition": "Opposition",
                "square": "Quadrat", "trine": "Trigon", "sextile": "Sextil",
                "quincunx": "Quincunx", "inconjunct": "Quincunx",
                "semi-sextile": "Halbsextil", "semisextile": "Halbsextil",
                "semi-square": "Halbquadrat", "semisquare": "Halbquadrat",
                "sesquiquadrate": "Anderthalbquadrat", "sesquisquare": "Anderthalbquadrat"}
_ASP_WORT.update(_ASP_WORT_EN)
_ASP_GLYPH = {g: w for w, g in ASPEKTE}
# Alternation: laengere Woerter zuerst, damit "semi-sextile" nicht als "sextile" liest.
_ASP_WOERTER = sorted(_ASP_WORT, key=len, reverse=True)
ASPEKT_RE = re.compile(r"(?<![\wäöüÄÖÜß-])(%s)(?![\wäöüÄÖÜß])|([%s])"
                       % ("|".join(re.escape(w) for w in _ASP_WOERTER),
                          "".join(g for _, g in ASPEKTE)))

def _art(wort):
    """Aspektwort (deutsch oder englisch) -> deutsche Aspektart."""
    return _ASP_WORT.get(wort, _ASP_WORT.get((wort or "").casefold(), wort))
SPIEGEL_ASPEKT = {"Konjunktion": "Opposition", "Opposition": "Konjunktion",
                  "Trigon": "Sextil", "Sextil": "Trigon", "Quadrat": "Quadrat",
                  "Quincunx": "Halbsextil", "Halbsextil": "Quincunx",
                  "Halbquadrat": "Anderthalbquadrat", "Anderthalbquadrat": "Halbquadrat"}
SPIEGEL_FAKTOR = {"AC": "DC", "DC": "AC", "MC": "IC", "IC": "MC",
                  "MONDKNOTEN": "SUEDKNOTEN", "SUEDKNOTEN": "MONDKNOTEN"}

ZEICHEN = ("Widder", "Stier", "Zwillinge", "Krebs", "Löwe", "Loewe", "Jungfrau", "Waage",
           "Skorpion", "Schütze", "Schuetze", "Steinbock", "Wassermann", "Fische")
# englische Zeichennamen -> deutscher Kanon (Sprachfassung, 2026-09-16d)
_ZEICHEN_EN = {"Aries": "Widder", "Taurus": "Stier", "Gemini": "Zwillinge", "Cancer": "Krebs",
               "Leo": "Löwe", "Virgo": "Jungfrau", "Libra": "Waage", "Scorpio": "Skorpion",
               "Sagittarius": "Schütze", "Capricorn": "Steinbock", "Aquarius": "Wassermann",
               "Pisces": "Fische"}
ZEICHEN_RE = "(?:%s)" % "|".join(ZEICHEN + tuple(_ZEICHEN_EN))

def _zeichen_norm(z):
    return selektor.norm(_ZEICHEN_EN.get(z, z))

_ORD_EN = {"first": "1", "second": "2", "third": "3", "fourth": "4", "fifth": "5",
           "sixth": "6", "seventh": "7", "eighth": "8", "ninth": "9", "tenth": "10",
           "eleventh": "11", "twelfth": "12"}
_ORD_EN_RE = "|".join(_ORD_EN)
ZEICHEN_GLYPHEN = "♈♉♊♋♌♍♎♏♐♑♒♓"
GRAD_RE = r"(\d{1,3})°\s*(\d{1,2})[′']"
# Haus-Schreibweisen: "4. Haus", "4./3. Haus", "Haus 4", "Haus 4/3"
# englisch: "4th house", "4th/3rd house", "fourth house", "eleventh/tenth house"
HAUS_RE = (r"(?:(?P<h1>\d{1,2})\.(?:\s*/\s*(?P<h2>\d{1,2})\.)?\s*Haus"
           r"|Haus(?:es)?\s+(?P<h3>\d{1,2})(?:\s*/\s*(?P<h4>\d{1,2}))?"
           r"|(?P<h5>\d{1,2})(?:st|nd|rd|th)(?:\s*/\s*(?P<h6>\d{1,2})(?:st|nd|rd|th))?\s+house"
           r"|(?P<h7>" + _ORD_EN_RE + r")(?:\s*/\s*(?P<h8>" + _ORD_EN_RE + r"))?\s+house)")
# Segment 1 eines Normal-Belegs / Staende-Teil eines Instrument-Segments:
# "Sonne ☉ 10°00′ Widder ♈, 1. Haus" (Form nach Klartext-Modul, Beleg-Format; konstruierte Werte).
STAENDE_RE = re.compile(
    r"^\s*(?P<faktor>" + _FAKTOR_RE + r")(?:\s*\((?:AC|MC|DC|IC)\))?[^\d°]{0,4}?"
    r"(?P<g>\d{1,3})°\s*(?P<m>\d{1,2})[′']\s*(?P<zeichen>" + ZEICHEN_RE + r")"
    r"\s*[" + ZEICHEN_GLYPHEN + r"]?\s*(?:,\s*(?P<haus>" + HAUS_RE + r"))?")

STUFEN = ("voll", "einseitig", "neben", "untergrund")

# ---------------------------------------------------------------------------
# Kleine Helfer
# ---------------------------------------------------------------------------

def _ws(s):
    """Leerraum normalisieren."""
    return re.sub(r"\s+", " ", (s or "")).strip()

def _min(g, m):
    return int(g) * 60 + int(m)

def _orb_txt(minuten):
    return "%d°%02d′" % (minuten // 60, minuten % 60)

def _kicker_nr(kicker):
    m = re.match(r"^(?:Kapitel|Chapter)\s+(\d+)\s*$", kicker or "", re.I)
    return int(m.group(1)) if m else None

# Wort-Kicker der englischen Fassung (Sprachfassung, 2026-09-16d); jeder deutsche
# Name gilt weiter, die englischen Namen zaehlen als derselbe Kicker.
_KICKER_ALIAS = {"auftakt": ("prelude", "zur lesart", "on reading this"),
                 "schlusswort": ("closing word", "closing words"),
                 "rechenschaft": ("account",), "instrument": ("instrument",),
                 "hauptthemen": ("core themes", "main themes"),
                 "konfliktfelder": ("fields of conflict",), "lebensaufgaben": ("life tasks",),
                 "zugang": ("access",),
                 # 2026-09-19 (W43, W10): Register und Lagebild des Transits; die
                 # englischen Namen aus T12-18 (heute in hilfe('ENGLISCH')).
                 "mitlaufendes": ("running alongside", "also running"),
                 "der stand heute": ("where things stand", "as things stand"),
                 # 2026-09-22 (W57-Nachzug): `Getriebe` hatte keinen englischen Namen —
                 # eine englische Analyse verlor damit THEMA 1 (P3), und P14 prueste den
                 # Kopfblock des Getriebe-Kapitels nicht. Seit 2026-09-26
                 # (Chris-Entscheidung) ist `Inner Workings` der Name fuer eine NEUE
                 # englische Fassung; die uebrigen stehen fuer schon geschriebene Faelle.
                 "getriebe": ("inner workings", "the inner workings", "gearing",
                              "the gearing", "the mechanism", "mechanism")}
# 2026-09-22: `on reading this` (Auftakt), `also running` (Register) und `as things
# stand` (Lagebild) sind die Wortlaute des ersten englischen Transits; die schon
# hinterlegten `prelude` / `running alongside` / `where things stand` gelten weiter.
# Mehrere englische Namen je Kicker sind hier die Regel, nicht die Ausnahme (s. o.
# `closing word`/`closing words`, `core themes`/`main themes`): Der Kicker steht im
# PDF, und welcher Wortlaut besser passt, entscheidet der Typ, nicht die Probe.
# 2026-09-19 (W23): Der Transit-Auftakt heisst `Zur Lesart` (Transit-Modul, Ablauf 2,
# Kapitelueberschriften). P8, P9 und P10 erkannten den Auftakt nur am Kicker
# `Auftakt` — der Fehlalarm zur Verwerfungs-Erlaubnis erzwang in T34-18c eine
# Rueckfrage. Seither gilt `Zur Lesart` als derselbe Kicker (Alias oben).

def _kurz(s, n=110):
    s = _ws(s)
    return s if len(s) <= n else s[:n - 1] + "…"

def _ist_kicker(ch, *namen):
    k = (ch.get("kicker") or "").strip().casefold()
    erlaubt = set()
    for n in namen:
        n = n.casefold()
        erlaubt.add(n)
        erlaubt.update(_KICKER_ALIAS.get(n, ()))
    return k in erlaubt

def _ist_zugang(ch):
    """Zugang-Kapitel: Kicker `Zugang <Bereich>` (Typmodul Geburtshoroskop seit
    2026-09-16, Pruefbericht Schritt 1+2, 1.2 — je Zugang ein eigener Kicker, weil
    `build.parse_analyse()` den Kicker als Schluessel fuehrt). Der nackte Kicker
    `Zugang` (aeltere Analysen) und die englischen Namen aus _KICKER_ALIAS gelten
    weiter, ebenfalls mit oder ohne Bereich."""
    k = (ch.get("kicker") or "").strip().casefold()
    for n in ("zugang",) + _KICKER_ALIAS["zugang"]:
        if k == n or k.startswith(n + " "):
            return True
    return False

# Getriebe-Kapitel und Kapitelzaehlung (2026-09-19, L7)
# Bis zum 2026-09-18 trug das Getriebe-Kapitel des Geburtshoroskops den Kicker
# `Kapitel 1`, die Themen begannen bei `Kapitel 2`: jeder Querverweis auf THEMA n
# musste von Hand um eins verschoben werden (31 Stellen im Typmodul). Seit dem
# Typmodul-Stand vom 2026-09-19 traegt es den Wort-Kicker `Getriebe`, und
# `Kapitel n` ist das Kapitel zu `THEMA n`. BEIDE Formen muessen laufen — aeltere
# Analysen werden weiter geprueft —, deshalb erkennt die Probe die Form am
# DOKUMENT und nicht am Typ: steht irgendwo der Kicker `Getriebe`, gilt die neue
# Zaehlung.
_TYPEN_MIT_GETRIEBE = ("geburt",)

def _zaehlung_ab(chapters, typ):
    """Nummer des ersten nummerierten Kapitels, das ein THEMA deutet (1 oder 2)."""
    if typ == "transit":
        return 1                    # kein Getriebe-Kapitel; `Kapitel 1` ist THEMA 1
    if any(_ist_kicker(ch, "Getriebe") for ch in (chapters or ())):
        return 1                    # neue Form (L7)
    return 2                        # alte Form: `Kapitel 1` ist das Getriebe-Kapitel

def _getriebe_kapitel(ch, typ, chapters=None):
    """Ist DIESES Kapitel das Getriebe-Kapitel?

    Neue Form: Wort-Kicker `Getriebe` (gilt in jedem Typ). Alte Form: `Kapitel 1`
    in einem Typ mit Getriebe-Kapitel, solange im Dokument kein Kicker `Getriebe`
    steht. Ohne `chapters` (Aufruf ohne Dokument) gilt die alte Form.
    """
    if _ist_kicker(ch, "Getriebe"):
        return True
    return (typ in _TYPEN_MIT_GETRIEBE
            and _kicker_nr(ch.get("kicker")) == 1
            and _zaehlung_ab(chapters, typ) == 2)

def _saetze(text):
    return [s for s in re.split(r"(?<=[.!?…])\s+(?=[„\"(A-ZÄÖÜ])", text) if s.strip()]

def _satz_mit(text, pos):
    start = 0
    for s in _saetze(text):
        i = text.find(s, start)
        if i < 0:
            continue
        if i <= pos < i + len(s):
            return s
        start = i + len(s)
    return text

class _Probe:
    """Ergebnis einer Probe."""
    def __init__(self, nr, name):
        self.nr, self.name = nr, name
        self.fehler, self.pruefen, self.hinweise = [], [], []
        # 2026-09-19 (W44): bewusst nicht Geprueftes INNERHALB einer Probe
        # (Getriebe-Beleg, Abgleich ohne events.json). Zaehlt in die Zusammenfassung
        # "s übersprungen" — vorher stand es nur als Hinweis, und die Schlusszeile
        # meldete "0 übersprungen".
        self.teilweise = []
        self.geprueft = 0
        self.status = None          # OK | FEHLER | PRUEFEN | AUSSAGELOS | UEBERSPRUNGEN
        self.grund = ""
        self.einheit = "Stellen"

    def uebersprungen(self, grund):
        self.status, self.grund = "UEBERSPRUNGEN", grund
        return self

    def aussagelos(self, grund):
        self.status, self.grund = "AUSSAGELOS", grund
        return self

    def abschluss(self):
        if self.status in ("UEBERSPRUNGEN", "AUSSAGELOS"):
            return self
        if self.fehler:
            self.status = "FEHLER"
        elif self.pruefen:
            self.status = "PRUEFEN"
        else:
            self.status = "OK"
        return self

    def als_dict(self):
        return {"nr": self.nr, "name": self.name, "status": self.status,
                "geprueft": self.geprueft, "einheit": self.einheit,
                "fehler": list(self.fehler), "pruefen": list(self.pruefen),
                "hinweise": list(self.hinweise), "teilweise": list(self.teilweise),
                "grund": self.grund}

# ---------------------------------------------------------------------------
# Datenblatt lesen
# ---------------------------------------------------------------------------

_AH_NAME = build._AH_NAME            # '(?:AC|MC|DC|IC|[A-ZÄÖÜ][a-zäöüß]+)'

def _tabellen_lesen(txt, unlesbar=None):
    """Alle Aspektzeilen der vier Tabellen als Liste von dicts.

    unlesbar: optional eine Liste; jede Tabellenzeile in einem der vier
    Abschnitte, die weder Kopf- noch Trennzeile ist und sich nicht lesen laesst,
    kommt als (Abschnitt, Zeile, Grund) hinein (2026-09-19, F2). Vorher lief sie
    STILL vorbei: Mit `∡` statt `⚼` in der Untergrund-Tabelle meldete P1 zwei
    FEHLER auf einen korrekten Beleg (G12-18, Klasse 1 Nr. 1.1). Gelesen werden
    in der Aspektspalte die Glyphen aus ASPEKTE — darunter ∠ Halbquadrat und
    ⚼ Anderthalbquadrat — und der Wort-Trenner des Moduls Radixrechnung
    (`–Anderthalbquadrat–`, Halbgeviertstriche).

    Zeilenregex woertlich aus `build._ressourcen_zeilen()` (sechsspaltige Form des
    Moduls Radixrechnung, Spalte 6 "zugleich" seit 15.09.2026 optional):
        | Faktor | ☌ Konjunktion | Faktor | 0°41′ | konj | … |
    — dort nur mit den harmonischen Glyphen (`_HARMONISCH`); hier mit ALLEN
    Aspektglyphen und dem Aspektwort als Alternative, dazu die Spalten 5 und 6.
    Die Ueberschriften und der Ueberschriften-Schnitt (`\\n#{2,3} `) stammen aus
    `build.aspekt_heimat()`; die Stufenzuordnung aus `build._STAERKE_KOPF`.
    Achsen-Spiegelzeilen aus Spalte 6 ("Opposition DC") werden als eigene Eintraege
    mit `spiegel=True` gefuehrt.
    """
    glyphen = "".join(g for _, g in ASPEKTE)
    # 2026-09-19 (F2): Wort-Trenner `–Wort–` (U+2013) in der Aspektspalte
    # zugelassen, wie ihn das Modul Radixrechnung fuer die Untergrund-Tabelle nennt.
    zeile = re.compile(
        r"\|\s*(%s)\s*\|\s*([%s])?\s*[–—-]?\s*([A-Za-zÄÖÜäöüß]*)\s*[–—-]?\s*\|\s*(%s)\s*\|"
        r"\s*(\d{1,3}°\d{2}′)\s*\|(?:\s*([^|]*)\|)?(?:\s*([^|]*)\|)?"
        % (_AH_NAME, glyphen, _AH_NAME))
    koepfe = [(k, s) for k, s in build._STAERKE_KOPF] + [("### Hauptaspekte", "voll"),
                                                          ("### Untergrund-Aspekte", "untergrund")]
    out = []
    for kopf, stufe in koepfe:
        if kopf not in txt:
            continue
        teil = txt.split(kopf, 1)[1]
        schnitt = re.search(r"\n#{2,3} ", teil)
        if schnitt:
            teil = teil[:schnitt.start()]
        for z in teil.splitlines():
            m = zeile.match(z)
            if not m:
                if unlesbar is not None and _tabellenzeile_mit_inhalt(z):
                    unlesbar.append((kopf, _ws(z), _grund_unlesbar(z)))
                continue
            a, g, w, b, orb = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            if a in ("Aspekt", "Faktor", "Punkt"):
                continue
            art = _ASP_WORT.get(w) if w else None
            if art is None and g:
                art = _ASP_GLYPH.get(g)
            if art is None:
                if unlesbar is not None:
                    unlesbar.append((kopf, _ws(z), "Aspektart nicht erkannt"))
                continue
            gr, mi = orb.split("°")
            mins = _min(gr, mi.rstrip("′"))
            eintrag = {"a": kanon(a), "b": kanon(b), "art": art, "orb": mins,
                       "orb_txt": orb, "stufe": stufe, "zeile": _ws(z), "spiegel": False}
            out.append(eintrag)
            zugleich = (m.group(7) or "").strip()
            mz = re.match(r"^(%s)\s+(%s)$" % ("|".join(w for w, _ in ASPEKTE), _FAKTOR_RE),
                          zugleich)
            if mz:
                out.append({"a": eintrag["a"], "b": kanon(mz.group(2)), "art": mz.group(1),
                            "orb": mins, "orb_txt": orb, "stufe": stufe,
                            "zeile": _ws(z), "spiegel": True})
    return out

def _tabellenzeile_mit_inhalt(z):
    """Traegt die Zeile Tabelleninhalt, der gelesen werden muesste? Nein bei
    Leerzeilen, Prosa, Trennzeilen (`|---|`), Kopfzeilen und Leerzeilen der
    Tabelle (`| _keine_ |`, `| — |`). (2026-09-19, F2)"""
    s = z.strip()
    if not s.startswith("|"):
        return False
    if re.match(r"^\|[\s:|\-–—]*$", s):
        return False
    zellen = [c.strip() for c in s.strip("|").split("|")]
    if zellen and zellen[0] in ("Faktor", "Aspekt", "Punkt"):
        return False
    return any(c not in ("", "_keine_", "keine", "Keine", "—", "-", "–") for c in zellen)

def _grund_unlesbar(z):
    """Sagt, WAS an einer Tabellenzeile nicht lesbar ist (2026-09-19, F2)."""
    zellen = [c.strip() for c in z.strip().strip("|").split("|")]
    erlaubt = " ".join(g for _, g in ASPEKTE)
    if len(zellen) >= 4:
        fremd = sorted({c for c in zellen[1] if not (c.isalpha() or c in " -–—" or
                                                    c in "".join(g for _, g in ASPEKTE))})
        if fremd:
            return ("unbekanntes Zeichen %s in der Aspektspalte — erlaubt sind %s mit dem "
                    "Aspektwort oder der Wort-Trenner –Wort–"
                    % (", ".join("„%s“" % c for c in fremd), erlaubt))
        if not re.fullmatch(r"\d{1,3}°\d{2}′", zellen[3]):
            return "Orb „%s“ nicht in der Form N°NN′ (Grad, U+00B0; Bogenminuten zweistellig, U+2032)" % zellen[3]
        return ("Faktorname nicht lesbar („%s“ / „%s“) — erwartet ist der nackte Name "
                "(Sonne, Mondknoten, AC …)" % (zellen[0], zellen[2]))
    return ("Zeilenform nicht erkannt — erwartet: | Faktor | <Glyphe> <Aspektwort> | "
            "Faktor | N°NN′ | Farbe | zugleich |")

def _staende_lesen(txt):
    """Staendetabelle (`## Staende`): Faktor -> (Minuten, Zeichen). None, wenn nicht
    sicher lesbar (dann wird die Gradminuten-Probe uebersprungen und gesagt)."""
    m = re.search(r"\n## St[äa]nde", txt)
    if not m:
        return None
    teil = txt[m.end():]
    schnitt = re.search(r"\n## ", teil)
    if schnitt:
        teil = teil[:schnitt.start()]
    zeile = re.compile(r"^\|\s*(%s)\s*\|\s*(\d{1,3})°(\d{1,2})[′']\s*\|\s*(%s)"
                       % (_AH_NAME, ZEICHEN_RE))
    out = {}
    for z in teil.splitlines():
        mm = zeile.match(z)
        if mm:
            out[kanon(mm.group(1))] = (_min(mm.group(2), mm.group(3)),
                                       selektor.norm(mm.group(4)))
    # LEERES dict STATT None, WENN DIE TABELLE DA IST (geaendert 2026-09-17,
    # Klasse-2-Entscheidungslauf, Wiederholungstaeter aus drei Laufabschnitten).
    # Vorher war "keine ## Staende-Ueberschrift" von "Ueberschrift da, aber kein
    # Zeilenformat erkannt" nicht zu unterscheiden; der zweite Fall lief als
    # stiller Hinweis durch, und drei Prueflaeufe haben deshalb nach einer
    # MODULREGEL fuer das Tabellenformat gefragt. Jetzt sagt die Probe das
    # Format selbst — die Regel wird nicht gebraucht.
    return out

def _themenliste_lesen(txt):
    """THEMA-Zeilen als Liste von dicts (nr, titel, fuehrt, fuehrt_roh, form,
    leitachse, roh). Einstieg, Schluss und Zerlegung woertlich aus
    `build.aspekt_heimat()` (Einstiegsmarke seit 2026-09-16 `THEMA \\d+ \\|`)."""
    _erste = re.search(r"THEMA \d+ \|", txt)
    if not _erste:
        return []
    tl = "\n" + txt[_erste.start():]
    for schluss in ("RECHENSCHAFT", "REGISTER:", "GESTRICHEN:"):
        tl = tl.split(schluss)[0]
    out = []
    nummern = re.findall(r"\nTHEMA (\d+) \|", tl)
    for nr, blk in zip(nummern, re.split(r"\nTHEMA \d+ \|", tl)[1:]):
        def feld(name):
            m = re.search(r"(?:^|\|)\s*%s=(.*?)(?=\s*\|\s*[a-z_]+=|\s*$)" % name, blk, re.S)
            return _ws(m.group(1)) if m else None
        fuehrt_roh = feld("fuehrt") or ""
        mf = FAKTOR_RE.match(fuehrt_roh)
        out.append({"nr": int(nr), "titel": feld("titel"), "fuehrt_roh": fuehrt_roh,
                    "fuehrt": kanon(mf.group(1)) if mf else None,
                    "form": (feld("form") or "voll").casefold(),
                    "leitachse": (feld("leitachse") or "").casefold().startswith("ja"),
                    "teil": (feld("teil") or "").casefold(), "roh": _ws(blk)})
    return out

# ---------------------------------------------------------------------------
# Beleg zerlegen
# ---------------------------------------------------------------------------

def _segmente(beleg):
    return [s.strip() for s in (beleg or "").split(" · ") if s.strip()]

def _staende_segment(seg):
    """-> dict(faktor, minuten, zeichen, haus1, haus2) oder None."""
    m = STAENDE_RE.match(seg)
    if not m:
        return None
    h1 = m.group("h1") or m.group("h3") or m.group("h5") or _ORD_EN.get(m.group("h7") or "")
    h2 = m.group("h2") or m.group("h4") or m.group("h6") or _ORD_EN.get(m.group("h8") or "")
    return {"faktor": kanon(m.group("faktor")), "minuten": _min(m.group("g"), m.group("m")),
            "zeichen": _zeichen_norm(m.group("zeichen")),
            "haus1": h1, "haus2": h2, "roh": seg}

def _aspekt_eintraege(text, faktor_a=None):
    """Zerlegt einen Text in Aspektangaben.

    Normal-Segment (faktor_a=None): Faktor A ist der erste Faktorname des Segments,
    dahinter genau eine Aspektart, dann Faktor B und "Orb N°NN′".
    Instrument-Segment (faktor_a gesetzt): kommagetrennte Angaben hinter den
    Staenden, jede "Aspektart Faktor Orb" — Faktor A ist die Funktion des Segments.
    Rueckgabe: Liste von dicts (a, art, b, orb, orb_sicher, stufe, roh, mehrfach).
    """
    out = []
    # Aspektangaben im Text; Wort und unmittelbar folgende Glyphe ("Trigon △") sind
    # EINE Angabe, nicht zwei.
    starts = []
    for t in ASPEKT_RE.finditer(text):
        art = _art(t.group(1)) if t.group(1) else _ASP_GLYPH.get(t.group(2))
        if starts and t.group(2) and t.start() - starts[-1][1] <= 3 and starts[-1][2] == art:
            continue
        starts.append((t.start(), t.end(), art, t))
    if not starts:
        return out
    if faktor_a is None:
        # Normalformat: genau EINE Aspektbeziehung je Segment; Faktor A steht vor
        # der Aspektart (mit oder ohne eigene Staende dazwischen).
        s, e, art, t = starts[0]
        ma = FAKTOR_RE.search(text[:s])
        a = kanon(ma.group(1)) if ma else None
        out.append(_eintrag(a, t, text[s:], len(starts) > 1))
    else:
        # Instrument-Format: Angabe fuer Angabe, jede beginnt mit der Aspektart;
        # Faktor A ist die Funktion des Segments.
        for i, (s, e, art, t) in enumerate(starts):
            ende = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            out.append(_eintrag(faktor_a, t, text[s:ende], False))
    return out

def _eintrag(a, t, rest, mehrfach):
    art = _art(t.group(1)) if t.group(1) else _ASP_GLYPH.get(t.group(2))
    nach = rest[t.end() - t.start():]
    # Glyphe hinter dem Wort ueberspringen
    nach = re.sub(r"^\s*[%s]" % "".join(g for _, g in ASPEKTE), "", nach)
    mb = FAKTOR_RE.search(nach)
    b = kanon(mb.group(1)) if mb else None
    tail = nach[mb.end():] if mb else nach
    mo = re.search(r"\bOrb\s*" + GRAD_RE, tail)
    orb, sicher = None, True
    if mo:
        orb = _min(mo.group(1), mo.group(2))
    else:
        grade = re.findall(GRAD_RE, tail)
        hat_zeichen = re.search(r"(?<![\wäöüß])" + ZEICHEN_RE + r"(?![\wäöüß])", tail)
        if grade and not hat_zeichen and len(grade) == 1:
            orb = _min(*grade[-1])
        elif grade:
            orb, sicher = _min(*grade[-1]), False
    stufe = None
    ms = re.search(r"(?<![\wäöüß])(voll|einseitig|Nebenaspekt|neben|full|one-sided|minor)(?![\wäöüß-])", rest)
    if ms:
        stufe = {"Nebenaspekt": "neben", "full": "voll", "one-sided": "einseitig",
                 "minor": "neben"}.get(ms.group(1), ms.group(1))
    return {"a": a, "art": art, "b": b, "orb": orb, "orb_sicher": sicher,
            "stufe": stufe, "roh": _ws(rest), "mehrfach": mehrfach}

def _beleg_form(ch, typ, chapters=None):
    """'struktur' | 'instrument' | 'zugang' | 'normal' | None (kein Beleg).

    `chapters` (2026-09-19, L7) sagt, ob die Analyse das Getriebe-Kapitel als
    `Getriebe` oder als `Kapitel 1` fuehrt; ohne sie gilt die alte Form.
    """
    if not ch.get("beleg"):
        return None
    if _ist_kicker(ch, "Instrument"):
        return "instrument"
    if _ist_zugang(ch):
        return "zugang"
    # 2026-09-19 (L7): Der Wort-Kicker `Getriebe` ist der Struktur-Beleg, in jedem
    # Typ; die Nummer 1 nur dort, wo sie schon vorher dafuer stand.
    if _ist_kicker(ch, "Getriebe"):
        return "struktur"
    segs = _segmente(ch["beleg"])
    if typ == "geburt" and _getriebe_kapitel(ch, typ, chapters):
        return "struktur"
    if segs and _staende_segment(segs[0]) is None:
        # Segment 1 sind keine Staende: Struktur-Format, wenn kein Aspekt darin
        # steht oder es das Getriebe-Kapitel ist; sonst ein Normal-Beleg
        # mit kaputtem Segment 1, den P2 meldet.
        # 2026-09-19 (L7): „das erste nummerierte Kapitel" war das Getriebe-Kapitel
        # nur in der alten Form. In der neuen ist `Kapitel 1` das erste THEMA — ein
        # kaputtes Segment 1 gehoert dort gemeldet und nicht uebersprungen. In
        # Typen ohne Getriebe-Kapitel bleibt die Nummer 1 die alte Notbremse.
        erstes = (_getriebe_kapitel(ch, typ, chapters)
                  or (typ not in _TYPEN_MIT_GETRIEBE and _kicker_nr(ch["kicker"]) == 1))
        if not ASPEKT_RE.search(ch["beleg"]) or erstes:
            return "struktur"
    return "normal"

# ---------------------------------------------------------------------------
# Transit-Kontakte und events.json (2026-09-19, W24, W10, W43)
# Schema: log/SCHNITTSTELLE_events_json.md des Wartungslaufs A. Ein Kontakt-Segment
# sieht so aus (Transit-Modul, „Signatur, Beleg und ihre Darstellung"):
#   T-<Faktor> <Glyphe> <Aspekt> <Glyphe> R-<Faktor> <Glyphe> — exakt TT.MM.JJJJ, …
# Im Lagebild traegt es zusaetzlich den Orb am Stichtag in Dezimalgrad
# („am Stichtag Orb 0,57°") wie die Anhangtabelle. Die Namen aus events.json
# laufen durch kanon(): `Knoten` (laufender wahrer Mondknoten) wird MONDKNOTEN,
# `Glückspunkt` GLUECKSPUNKT — dieselben Schluessel wie im Beleg.
# ---------------------------------------------------------------------------
_KONTAKT_SEG_RE = re.compile(
    r"(?<![\wäöüÄÖÜß])T-\s*(?P<t>" + _FAKTOR_RE + r"|Knoten)(?![\wäöüÄÖÜß])(?P<mitte>.*?)"
    r"(?<![\wäöüÄÖÜß])R-\s*(?P<r>" + _FAKTOR_RE + r"|Knoten)(?![\wäöüÄÖÜß])"
    r"(?:\s*\((?:AC|MC|DC|IC)\))?", re.S)
_DATUM_DE_RE = re.compile(r"(?<![\d.])(\d{1,2})\.(\d{1,2})\.(\d{4}|\d{2})(?![\d])")
_DATUM_ISO_RE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
_TAIL_RE = re.compile(
    r"(?P<nichtexakt>(?:im\s+Fenster\s+)?(?:nicht\s+(?:mehr\s+)?exakt|kein\w*\s+Exakt\w*|nie\s+exakt)"
    r"|(?:not|no|never)\s+exact\w*)"
    r"|(?P<exakt>exakt\w*|exact\w*)"
    r"|(?P<annae>Ann(?:ä|ae)herung\w*|approach\w*)"
    r"|(?P<wirkorb>Wirkorb\w*|effective\s+orb)"
    r"|(?P<station>Stillst(?:a|ä)nd\w*|Station\w*)"
    r"|(?P<stichtag>Stichtag\w*|reference\s+date)"
    r"|(?P<datum>(?<![\d.])\d{1,2}\.\d{1,2}\.(?:\d{4}|\d{2})(?![\d])|(?<!\d)\d{4}-\d{2}-\d{2}(?!\d))"
    r"|(?P<bogen>\d+(?:[.,]\d+)?\s*[′'](?!\d))", re.I)
# Orb am Stichtag in Dezimalgrad: „am Stichtag Orb 0,57°", „Orb am Stichtag 0.57°",
# „Stichtag-Orb 0,57°" — nie in Gradminuten (dann folgt eine Ziffer auf °).
_STICHTAG_ORB_RE = re.compile(
    r"(?:(?:am\s+)?Stichtag\w*[\s\-–]*Orb|Orb\s+am\s+Stichtag|(?:at\s+the\s+)?reference\s+date\s*orb|orb\s+at\s+the\s+reference\s+date)\s*:?\s*"
    r"(\d{1,2}(?:[.,](\d{1,4}))?)\s*°(?!\s*\d)", re.I)
# Zusatz-Zeitmasse im Beleg (W46; das Beleg-Format dafuer setzt der Textlauf).
_ZUSATZ_SEG_RE = re.compile(r"Sonnenbogen|solar[\s-]*arc|progressiv\w*|progressed|Finsternis|eclipse", re.I)  # 2026-09-22: englische Zusatz-Segmente (solar arc, progressed, eclipse)
# 2026-09-23b (Wartungslauf zu den Pruefberichten vom 23.09.; Transit 1+2 K1-5,
# Transit 3+4 Inhalt P1): Die Zusatz-Segmente tragen selbst ein R-Ziel
# („Finsternis auf R-Mond — TT.MM.JJJJ", „Sonnenbogen-Merkur … R-Neptun — exakt …",
# LESEFORMATE). `_TRANSIT_KONTAKT_RE` sah darin einen Transitkontakt, das Segment
# lief als Normalsegment und meldete „kein Aspekt im Segment" (2 PRUEFEN, 0
# zutreffend). Ein Segment, das mit dem Zeitmass BEGINNT, ist ein Zusatz-Segment.
_ZUSATZ_SEG_ANFANG_RE = re.compile(r"^\W*(?:Sonnenbogen|solar[\s-]*arc|progressiv\w*|progressed|Finsternis|eclipse"
                                   r"|(?:Jahres)?profektion|(?:annual\s+)?profection)", re.I)
# 2026-09-28 (Klasse-2-Nachtrag): Jahresprofektion als viertes Zusatz-Segment
# („Jahresprofektion → Zwillinge ♊, Jahresherr Merkur ☿ — ab dem 37. Geburtstag"),
# erkannt nur am Segmentanfang; der Geburtstag gegen zusatz.profektion[].alter.
_PROFEKTION_ALTER_RE = re.compile(r"(\d{1,3})\.\s*Geburtstag|(\d{1,3})(?:st|nd|rd|th)\s+birthday", re.I)

def _datum_iso(s):
    """'TT.MM.JJJJ' / 'TT.MM.JJ' / 'JJJJ-MM-TT' -> 'JJJJ-MM-TT' (None, wenn keines)."""
    m = _DATUM_ISO_RE.search(s or "")
    if m:
        return "%s-%s-%s" % m.groups()
    m = _DATUM_DE_RE.search(s or "")
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000
        return "%04d-%02d-%02d" % (y, mo, d)
    return None

def _kontakt_aus_segment(seg):
    """Ein Transit-Kontakt im Beleg -> dict(t, art, r, tail) mit kanonischen
    Schluesseln, oder None. `tail` ist der Text hinter dem Ziel."""
    m = _KONTAKT_SEG_RE.search(seg or "")
    if not m:
        return None
    ma = ASPEKT_RE.search(m.group("mitte"))
    art = None
    if ma:
        art = _art(ma.group(1)) if ma.group(1) else _ASP_GLYPH.get(ma.group(2))
    return {"t": kanon(m.group("t")), "art": art, "r": kanon(m.group("r")),
            "tail": seg[m.end():]}

def _kontakt_tail_lesen(tail):
    """Liest Exaktdaten, Annaeherungen, sonstige Daten und den Stichtag-Orb aus dem
    Text hinter dem Ziel. Ein Stichwort gilt fuer alle folgenden Daten bis zum
    naechsten Stichwort („exakt TT.MM.JJJJ, TT.MM.JJJJ, wieder TT.MM.JJJJ")."""
    out = {"exakt": [], "annaeherung": [], "andere": [], "nicht_exakt": False,
           "nicht_exakt_fenster": False, "annae_min": None, "annae_dez": 0,
           "stichtag_orb": None, "stichtag_dez": 0}
    modus = None
    for m in _TAIL_RE.finditer(tail or ""):
        if m.group("nichtexakt"):
            out["nicht_exakt"] = True
            if (m.group("nichtexakt").lower().startswith("im")
                    or re.match(r"\s*im\s+Fenster", tail[m.end():m.end() + 20])):
                out["nicht_exakt_fenster"] = True
            modus = "sonst"
        elif m.group("exakt"):
            modus = "exakt"
        elif m.group("annae"):
            modus = "annaeherung"
        elif m.group("wirkorb"):
            modus = "Wirkorb"
        elif m.group("station"):
            modus = "Station"
        elif m.group("stichtag"):
            modus = "Stichtag"
        elif m.group("bogen"):
            if modus == "annaeherung" and out["annae_min"] is None:
                zahl = re.sub(r"[′'\s]", "", m.group("bogen")).replace(",", ".")
                out["annae_min"] = float(zahl)
                out["annae_dez"] = len(zahl.partition(".")[2])
        elif m.group("datum"):
            d = _datum_iso(m.group("datum"))
            if modus == "exakt":
                out["exakt"].append(d)
            elif modus == "annaeherung":
                out["annaeherung"].append(d)
            else:
                out["andere"].append((d, modus or "ohne Stichwort"))
    ms = _STICHTAG_ORB_RE.search(tail or "")
    if ms:
        out["stichtag_orb"] = float(ms.group(1).replace(",", "."))
        out["stichtag_dez"] = len(ms.group(2) or "")
    return out

def _json_strings(obj, out):
    """Alle Zeichenketten eines JSON-Baums (fuer Datumsfelder)."""
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _json_strings(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _json_strings(v, out)
    return out

def _json_daten(obj):
    """Menge aller ISO-Tagesdaten (JJJJ-MM-TT) eines JSON-Baums."""
    return {s for s in _json_strings(obj, []) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)}

def _events_laden(pfad):
    """events.json von `transit.py --json <pfad>` lesen; laut, wenn es nicht geht."""
    import json
    try:
        with open(pfad, encoding="utf-8") as f:
            daten = json.load(f)
    except OSError as e:
        raise InhaltsprobeFehler("events.json nicht lesbar: %s (%s) — Pfad prüfen. Ohne "
                                 "--events läuft die Probe weiter, hält Transit-Belege "
                                 "dann aber nur auf ihre Form." % (pfad, e))
    except ValueError as e:
        raise InhaltsprobeFehler("events.json ist kein gültiges JSON: %s (%s) — die Datei "
                                 "aus `transit.py <chart_data> … --json <pfad>` nehmen."
                                 % (pfad, _kurz(str(e), 120)))
    if not isinstance(daten, dict) or not isinstance(daten.get("events"), list):
        raise InhaltsprobeFehler("%s trägt keinen Schlüssel 'events' (Liste) — ist das die "
                                 "Ausgabe von `transit.py --json`?" % pfad)
    return daten

def _ev_index(daten):
    """{(Transiter, Aspektart, Ziel) kanonisch: [Ereignis, …]} ueber alle Passagen."""
    idx = {}
    for e in (daten or {}).get("events", []):
        k = (kanon(e.get("transit") or ""), e.get("aspekt"), kanon(e.get("ziel") or ""))
        idx.setdefault(k, []).append(e)
    return idx

def _ev_jetzt(daten, k):
    """Eintraege von jetzt.im_orb zu einem Kontakt."""
    return [j for j in ((daten or {}).get("jetzt") or {}).get("im_orb", [])
            if (kanon(j.get("transit") or ""), j.get("aspekt"), kanon(j.get("ziel") or "")) == k]

def _ev_exakt(evs):
    """Alle Nulldurchgaenge der Passagen eines Kontakts (exakt_gesamt; bei einer
    events.json von vor dem 2026-09-19 exakt samt Vorlauf/Fortsetzung)."""
    out = set()
    for e in evs:
        if e.get("exakt_gesamt") is not None:
            out.update(e.get("exakt_gesamt") or [])
        else:
            out.update(e.get("exakt") or [])
            out.update(e.get("exakt_nach_fenster") or [])
            out.update(((e.get("vorlauf") or {}).get("exakt")) or [])
    return out

def _ev_annaeherung(evs):
    """{Datum: Orb in Grad} aller Annaeherungen ohne Nulldurchgang (Passage,
    Vorlauf, Fortsetzung) — seit W1 getrennt von `exakt`."""
    out = {}
    for e in evs:
        for quelle in (e, e.get("vorlauf") or {}, e.get("fortsetzung") or {}):
            for d, orb in (quelle.get("annaeherung") or []):
                out[d] = orb
    return out

# ---------------------------------------------------------------------------
# Typ und Kapitelklassen
# ---------------------------------------------------------------------------

def typ_aus_h1(doctype):
    d = (doctype or "").casefold()
    if "ultimativ" in d or "ultimate" in d or "complete" in d:
        return "ultimativ"
    if "transit" in d or "jahresvorschau" in d or "year ahead" in d:
        return "transit"
    if ("evolution" in d or "seelen" in d or d.startswith("ea") or " ea" in d
            or "soul" in d):
        return "ea"
    if "geburtshoroskop" in d or "geburt" in d or "birth chart" in d or "natal" in d:
        return "geburt"
    return None

def sprache(parsed):
    """'en' oder 'de' — an den ###-Wortlauten erkannt, sonst an der H1
    (Sprachfassung, 2026-09-16d). Entscheidet nur, ob der Titelvergleich in P3
    laeuft: die Themenliste der chart_data ist deutsch, eine englische Analyse
    traegt uebersetzte Titel, und ein Vergleich waere jedes Mal ein Fehlalarm."""
    en = {w[1] for w in WORTLAUTE["geburt"]}
    de = {w[0] for w in WORTLAUTE["geburt"]}
    subs = [s for ch in parsed["chapters"] for s in _subheads(ch)]
    if any(s in en for s in subs):
        return "en"
    if any(s in de for s in subs):
        return "de"
    d = (parsed.get("doctype") or "").casefold()
    return "en" if re.search(r"\b(?:chart|birth|natal|soul|transits?)\b", d) else "de"

def _subheads(ch):
    return [_ws(b["text"]) for b in ch["blocks"] if b.get("type") == "subhead"]

def _hat_bewegungen(ch):
    return any(s in ALLE_WORTLAUTE for s in _subheads(ch))

def _themenkapitel(chapters, typ):
    """Kapitel mit Bewegungsfolge, in Dokumentreihenfolge.
    geburt: Kicker `Kapitel n` ab der ersten Themennummer (`_zaehlung_ab()`: 1 in
    der neuen Form, 2 in einer Analyse, die das Getriebe-Kapitel als `Kapitel 1`
    fuehrt — 2026-09-19, L7), dazu `Zugang <Bereich>`. Andere Typen: jedes
    Kapitel, das einen bekannten Bewegungs-Wortlaut traegt, plus jedes `Kapitel n`."""
    out = []
    ab = _zaehlung_ab(chapters, typ)
    for ch in chapters:
        n = _kicker_nr(ch["kicker"])
        if typ == "geburt":
            if (n is not None and n >= ab) or _ist_zugang(ch):
                out.append(ch)
        else:
            if n is not None or _ist_zugang(ch) or _hat_bewegungen(ch):
                out.append(ch)
    return out

def _bezeichnung(ch):
    return "%s · %s" % (ch.get("kicker") or "—", _kurz(ch.get("title"), 50))

# ---------------------------------------------------------------------------
# Die Proben
# ---------------------------------------------------------------------------

def _p1_beleg_aspekte(chapters, typ, tabelle, events=None, unlesbar=None):
    """events: gelesene events.json (dict) oder None; unlesbar: Liste aus
    `_tabellen_lesen(txt, unlesbar)` (beide Parameter 2026-09-19, W24 und F2)."""
    p = _Probe("P1", "Beleg-Aspekte")
    p.einheit = "Segmente"
    # 2026-09-19 (F2): eine Tabellenzeile, die die Probe nicht lesen kann, ist ein
    # FEHLER des Datenblatts — sonst erscheint ein korrekter Beleg als „nicht in
    # der Tabelle", und build.aspekt_heimat() laeuft ueber eine zu kleine Menge grün.
    for kopf, z, grund in (unlesbar or []):
        p.fehler.append("Aspekttabelle „%s“: Zeile nicht lesbar — %s: „%s“. Die Probe "
                        "kann sie gegen keinen Beleg halten; die Zeile im Datenblatt "
                        "berichtigen" % (kopf.lstrip("# "), grund, _kurz(z, 100)))
    # Ohne Aspekttabellen ist im Geburtshoroskop nichts zu pruefen. Im TRANSIT
    # schon: Dort wird die FORM des Kontakt-Segments geprueft (eine Aspektbeziehung,
    # Exaktdaten), und die haengt nicht an den Radix-Tabellen (neu 2026-09-18).
    if not tabelle and typ != "transit":
        if unlesbar:
            return p.abschluss()
        return p.aussagelos("keine Aspektzeile in den vier Aspekttabellen gefunden")
    if not tabelle:
        p.hinweise.append("Keine Radix-Aspekttabellen in der chart_data — im Transit "
                          "wird nur die FORM der Kontakt-Segmente geprüft")
    index = {}
    for e in tabelle:
        index.setdefault(frozenset([e["a"], e["b"]]), []).append(e)

    def naechste(a, b, art):
        kand = [e for e in tabelle if a in (e["a"], e["b"]) or b in (e["a"], e["b"])]
        if not kand:
            return "keine Tabellenzeile mit %s oder %s" % (ANZEIGE.get(a, a), ANZEIGE.get(b, b))
        kand.sort(key=lambda e: (-(a in (e["a"], e["b"]) and b in (e["a"], e["b"])),
                                 e["art"] != art, e["orb"]))
        e = kand[0]
        return "nächste Zeile: %s%s" % (e["zeile"], " (Spiegelzeile)" if e["spiegel"] else "")

    def pruefe_eintrag(ort, e):
        p.geprueft += 1
        stelle = "%s: „%s“" % (ort, _kurz(e["roh"], 90))
        if e["mehrfach"]:
            p.pruefen.append("%s — mehr als eine Aspektangabe im Segment (Beleg-Format: "
                             "genau EINE je Segment); geprüft wurde die erste" % stelle)
        if not e["a"] or not e["b"] or not e["art"]:
            p.pruefen.append("%s — nicht als „Faktor Aspektart Faktor Orb“ lesbar" % stelle)
            return
        a, b, art = e["a"], e["b"], e["art"]
        # Suedknoten steht nicht in der Aspektrechnung: Spiegel des Nordknoten-Aspekts
        spiegel_hinweis = None
        if "SUEDKNOTEN" in (a, b):
            a2 = "MONDKNOTEN" if a == "SUEDKNOTEN" else a
            b2 = "MONDKNOTEN" if b == "SUEDKNOTEN" else b
            art2 = SPIEGEL_ASPEKT.get(art, art)
            treffer = [t for t in index.get(frozenset([a2, b2]), []) if t["art"] == art2]
            if treffer:
                p.pruefen.append("%s — Südknoten-Aspekt, in der Tabelle steht nur der "
                                 "Spiegel %s (der Südknoten geht nicht in die "
                                 "Aspektrechnung)" % (stelle, treffer[0]["zeile"]))
                return
            p.fehler.append("%s — Paar nicht in den Aspekttabellen, auch nicht als "
                            "Spiegel des Nordknotens; %s" % (stelle, naechste(a, b, art)))
            return
        zeilen = index.get(frozenset([a, b]), [])
        gleiche_art = [t for t in zeilen if t["art"] == art]
        if not zeilen:
            # nur ueber die Achsen-Spiegelung ableitbar?
            for x, y in ((a, b), (b, a)):
                if y in SPIEGEL_FAKTOR and y in ACHSEN:
                    alt = index.get(frozenset([x, SPIEGEL_FAKTOR[y]]), [])
                    alt = [t for t in alt if t["art"] == SPIEGEL_ASPEKT.get(art)]
                    if alt:
                        spiegel_hinweis = alt[0]
            if spiegel_hinweis:
                p.pruefen.append("%s — keine Tabellenzeile; nur als Achsen-Spiegel von "
                                 "%s ableitbar (Spalte „zugleich“ fehlt)"
                                 % (stelle, spiegel_hinweis["zeile"]))
                return
            p.fehler.append("%s — Paar %s/%s nicht in den Aspekttabellen; %s"
                            % (stelle, ANZEIGE.get(a, a), ANZEIGE.get(b, b), naechste(a, b, art)))
            return
        if not gleiche_art:
            p.fehler.append("%s — Aspektart %s stimmt nicht; Tabelle: %s"
                            % (stelle, art, "; ".join(t["zeile"] for t in zeilen)))
            return
        if e["orb"] is None:
            p.pruefen.append("%s — kein Orb im Segment; Tabelle: %s" % (stelle, gleiche_art[0]["zeile"]))
            return
        passend = [t for t in gleiche_art if abs(t["orb"] - e["orb"]) <= 1]
        if not passend:
            if not e["orb_sicher"]:
                p.pruefen.append("%s — Orb nicht eindeutig lesbar (Position oder Orb?); "
                                 "Tabelle: %s" % (stelle, gleiche_art[0]["zeile"]))
            else:
                p.fehler.append("%s — Orb %s weicht ab; Tabelle: %s"
                                % (stelle, _orb_txt(e["orb"]), gleiche_art[0]["zeile"]))
            return
        if not e["orb_sicher"]:
            p.hinweise.append("%s — Orb ohne Schlüsselwort gelesen, stimmt mit der Tabelle" % stelle)
        if e["stufe"] and passend[0]["stufe"] not in (e["stufe"],):
            p.pruefen.append("%s — Beleg nennt Stufe „%s“, Tabelle führt „%s“"
                             % (stelle, e["stufe"], passend[0]["stufe"]))

    ev_idx = _ev_index(events) if events is not None else None
    transit_gesehen = []

    def pruefe_transit_segment(stelle, seg, eintr, lagebild=False):
        """Transit-Beleg: Form pruefen, nicht gegen die Radix-Tabellen halten.

        Der Kontakt traegt statt des Orbs die Exaktdaten (Transit-Modul). Ein
        Tabellenabgleich waere sinnlos und faellt gelegentlich zufaellig aus:
        Die Radix-Aspekttabellen des Transit-Datenblatts fuehren Radix-Paare,
        nicht Transit-Kontakte. Zustaendig ist dort build.kontakt_heimat_bericht().
        Geprueft wird: genau EINE Aspektbeziehung, und Exaktdaten vorhanden —
        im Lagebild statt der Exaktdaten der Orb am Stichtag (W10). Mit events.json
        zusaetzlich die Sache selbst (2026-09-19, W24): Kontakt vorhanden,
        Exaktdaten = Nulldurchgaenge, Annaeherungen, Stichtag-Orb, sonstige Daten.
        """
        p.geprueft += 1
        transit_gesehen.append(stelle)
        if len(eintr) > 1:
            p.fehler.append("%s — %d Aspektbeziehungen im Segment; ab Segment 2 gilt "
                            "auch im Transit genau EINE" % (stelle, len(eintr)))
            return
        k = _kontakt_aus_segment(seg)
        lesung = _kontakt_tail_lesen(k["tail"]) if k else None
        if lagebild:
            if lesung is None or lesung["stichtag_orb"] is None:
                p.pruefen.append("%s — Lagebild-Segment ohne Orb am Stichtag; Beleg-Format "
                                 "des Lagebilds: je Kontakt „am Stichtag Orb 0,57°“ in "
                                 "Dezimalgrad wie in der Anhangtabelle: „%s“"
                                 % (stelle, _kurz(seg, 90)))
        elif not _TRANSIT_EXAKT_RE.search(seg) and not (
                lesung and (lesung["nicht_exakt"] or lesung["annaeherung"])):
            p.pruefen.append("%s — kein Exaktdatum; das Transit-Segment trägt statt "
                             "des Orbs die Exaktdaten (Transit-Modul, „Signatur, "
                             "Beleg und ihre Darstellung“), ein Kontakt ohne "
                             "Nulldurchgang „nicht exakt, Annäherung bis x′ am "
                             "TT.MM.JJJJ“: „%s“" % (stelle, _kurz(seg, 90)))
        if events is None or k is None:
            return
        schluessel = (k["t"], k["art"], k["r"])
        name = "T-%s %s R-%s" % (ANZEIGE.get(k["t"], k["t"]), k["art"] or "?",
                                 ANZEIGE.get(k["r"], k["r"]))
        evs = ev_idx.get(schluessel, [])
        if not evs:
            andere = sorted({a for (t, a, r) in ev_idx if t == k["t"] and r == k["r"]})
            p.fehler.append("%s — Kontakt %s steht nicht in events.json%s"
                            % (stelle, name, "; dort mit diesem Ziel nur: " + ", ".join(andere)
                               if andere else " (auch mit keiner anderen Aspektart)"))
            return
        exakt = _ev_exakt(evs)
        im_fenster = set(d for e in evs for d in (e.get("exakt_im_fenster") or []))
        annae = _ev_annaeherung(evs)
        for d in lesung["exakt"]:
            if d in exakt:
                continue
            nah = [x for x in sorted(exakt) if abs(_tage(x, d)) <= 1]
            p.fehler.append("%s — exakt %s ist kein Nulldurchgang von %s; events.json: %s%s"
                            % (stelle, _de(d), name,
                               ", ".join(_de(x) for x in sorted(exakt)) or "keiner",
                               " — %s ist eine Annäherung ohne Nulldurchgang" % _de(d)
                               if d in annae else
                               " — %s liegt einen Tag daneben (Zeitzone? events.json gibt "
                               "Ortstage in `zeitzone`)" % _de(nah[0]) if nah else ""))
        if lesung["exakt"] and not lagebild:
            fehlt = sorted(im_fenster - set(lesung["exakt"]))
            if fehlt:
                p.pruefen.append("%s — im Fenster auch exakt %s; ein Mehrfachkontakt nennt "
                                 "alle Exaktdaten (Transit-Modul)"
                                 % (stelle, ", ".join(_de(x) for x in fehlt)))
        if lesung["nicht_exakt"]:
            if im_fenster:
                p.fehler.append("%s — der Beleg sagt „nicht exakt“, events.json kennt "
                                "Nulldurchgänge im Fenster: %s"
                                % (stelle, ", ".join(_de(x) for x in sorted(im_fenster))))
            elif exakt and not lesung["nicht_exakt_fenster"]:
                p.pruefen.append("%s — „nicht exakt“, aber außerhalb des Fensters exakt "
                                 "(Vorlauf/Fortsetzung): %s — gemeint „im Fenster nicht "
                                 "exakt“?" % (stelle, ", ".join(_de(x) for x in sorted(exakt))))
        for d in lesung["annaeherung"]:
            if d not in annae:
                p.fehler.append("%s — Annäherung am %s steht nicht in events.json "
                                "(`annaeherung` von Passage, Vorlauf, Fortsetzung: %s)%s"
                                % (stelle, _de(d),
                                   ", ".join(_de(x) for x in sorted(annae)) or "keine",
                                   " — %s ist ein Nulldurchgang" % _de(d) if d in exakt else ""))
            elif lesung["annae_min"] is not None and \
                    abs(lesung["annae_min"] - annae[d] * 60.0) > \
                    0.5 * 10 ** -lesung["annae_dez"] + 0.01:      # halbe Rundungsbreite des Belegs
                p.pruefen.append("%s — Annäherung bis %s′, events.json: %s′ am %s"
                                 % (stelle, ("%.1f" % lesung["annae_min"]).replace(".", ","),
                                    ("%.1f" % (annae[d] * 60.0)).replace(".", ","), _de(d)))
        if lesung["stichtag_orb"] is not None:
            soll = [e.get("orb_stichtag") for e in evs if e.get("orb_stichtag") is not None]
            tafel = [j.get("orb_grad") for j in _ev_jetzt(events, schluessel)
                     if j.get("orb_grad") is not None]
            if not soll and not tafel:
                p.hinweise.append("%s — Stichtag-Orb nicht prüfbar: events.json ohne "
                                  "`orb_stichtag` (Stand vor 2026-09-19?) und Kontakt nicht "
                                  "in jetzt.im_orb" % stelle)
            else:
                tol = (0.5 * 10 ** -lesung["stichtag_dez"] if lesung["stichtag_dez"] else 0.5)
                ok = any(abs(lesung["stichtag_orb"] - v) <= tol + 0.00006 for v in soll) or \
                    any(abs(lesung["stichtag_orb"] - v) <= tol + 1e-9 for v in tafel)
                if not ok:
                    p.fehler.append("%s — Orb am Stichtag %s° weicht ab; events.json: "
                                    "orb_stichtag %s%s"
                                    % (stelle, (("%%.%df" % lesung["stichtag_dez"]) %
                                                lesung["stichtag_orb"]).replace(".", ","),
                                       ", ".join(("%.4f°" % v).replace(".", ",") for v in soll)
                                       or "—",
                                       " (Anhangtabelle %s)" % ", ".join(
                                           ("%.2f°" % v).replace(".", ",") for v in tafel)
                                       if tafel else ""))
        bekannt = set(exakt) | set(annae) | _json_daten(evs) | \
            _json_daten(_ev_jetzt(events, schluessel)) | \
            {s.get("datum") for s in (events.get("stations") or [])
             if kanon(s.get("transit") or "") == k["t"]}
        for d, art in lesung["andere"]:
            if d not in bekannt:
                p.pruefen.append("%s — %s %s steht bei %s in keinem Feld von events.json "
                                 "(Wirkorb-Perioden, Erfassungsspanne, Vorlauf, Fortsetzung, "
                                 "Stationen des Transiters, Jetzt-Liste)"
                                 % (stelle, art, _de(d), name))

    def pruefe_zusatz_segment(stelle, seg):
        """Sonnenbogen, progressiver Mond, Finsternis im Transit-Beleg (W24/W46):
        jedes Datum gegen `zusatz` der events.json. Das Beleg-Format dieser Masse
        setzt der Textlauf; deshalb nur PRUEFEN. Die Profektion (2026-09-28)
        traegt statt eines Datums den Geburtstag, mit dem ihr Jahr beginnt."""
        p.geprueft += 1
        transit_gesehen.append(stelle)
        if re.match(r"^\W*(?:Jahres)?profektion|^\W*(?:annual\s+)?profection", seg, re.I):
            jahre = [int(m.group(1) or m.group(2)) for m in _PROFEKTION_ALTER_RE.finditer(seg)]
            if events is None or not jahre:
                return
            z = events.get("zusatz") or {}
            soll = {x.get("alter") for x in z.get("profektion", [])}
            for j in jahre:
                if j not in soll:
                    p.pruefen.append("%s — %d. Geburtstag nicht in zusatz.profektion[].alter "
                                     "der events.json" % (stelle, j))
            return
        daten = [_datum_iso(m.group(0)) for m in _TAIL_RE.finditer(seg) if m.group("datum")]
        if events is None or not daten:
            return
        z = events.get("zusatz") or {}
        if not z:
            p.hinweise.append("%s — events.json ohne `zusatz` (transit.py ohne --geburt): "
                              "Datum nicht prüfbar" % stelle)
            return
        s = seg.casefold()
        if "sonnenbogen" in s or "solar arc" in s or "solar-arc" in s:
            soll = {x.get("exakt") for x in z.get("sonnenbogen", [])}
            welche = "zusatz.sonnenbogen[].exakt"
        elif "finsternis" in s or "eclipse" in s:
            soll = {x.get("datum") for x in z.get("finsternisse", [])}
            welche = "zusatz.finsternisse[].datum"
        else:
            soll = {x.get("datum") for x in z.get("prog_mond_wechsel", [])} | \
                {x.get("datum") for x in z.get("prog_mond", [])}
            welche = "zusatz.prog_mond_wechsel[].datum / prog_mond[].datum"
        for d in daten:
            if d not in soll:
                p.pruefen.append("%s — Datum %s nicht in %s der events.json"
                                 % (stelle, _de(d), welche))

    for ch in chapters:
        form = _beleg_form(ch, typ, chapters)
        if form is None:
            continue
        bez = _bezeichnung(ch)
        segs = _segmente(ch["beleg"])
        if form == "struktur":
            # 2026-09-19 (W44): zaehlt in die Zusammenfassung „s übersprungen".
            p.teilweise.append("Getriebe-Beleg (Struktur-Format) nicht gegen die "
                               "Aspekttabellen gehalten: %s" % bez)
            continue
        if form == "normal":
            for i, seg in enumerate(segs[1:], start=2):
                if typ == "transit" and (_ZUSATZ_SEG_ANFANG_RE.match(seg) or (
                        _ZUSATZ_SEG_RE.search(seg) and not _TRANSIT_KONTAKT_RE.search(seg))):
                    pruefe_zusatz_segment("%s, Segment %d" % (bez, i), seg)
                    continue
                eintr = _aspekt_eintraege(seg)
                if not eintr:
                    p.pruefen.append("%s, Segment %d: „%s“ — kein Aspekt im Segment (Normalformat: "
                                     "jedes Segment ab dem zweiten genau EINE Aspektbeziehung)"
                                     % (bez, i, _kurz(seg, 90)))
                    continue
                if typ == "transit" and _TRANSIT_KONTAKT_RE.search(seg):
                    pruefe_transit_segment("%s, Segment %d" % (bez, i), seg, eintr,
                                           lagebild=_ist_kicker(ch, "Der Stand heute"))
                    continue
                for e in eintr:
                    pruefe_eintrag("%s, Segment %d" % (bez, i), e)
        elif form == "instrument":
            for i, seg in enumerate(segs, start=1):
                st = _staende_segment(seg)
                if st is None:
                    ma = FAKTOR_RE.match(seg)
                    a = kanon(ma.group(1)) if ma else None
                else:
                    a = st["faktor"]
                teile = seg.split(" — ", 1)
                rest = teile[1] if len(teile) > 1 else seg
                for e in _aspekt_eintraege(rest, faktor_a=a):
                    pruefe_eintrag("%s, Segment %d (%s)" % (bez, i, ANZEIGE.get(a, a) if a else "?"), e)
        elif form == "zugang":
            muster = re.compile(r"(" + _FAKTOR_RE + r")(?:\s*\((?:AC|MC|DC|IC)\))?\s*[☉☽☿♀♂♃♄♅♆♇☊☋⚷⚸⊗]?\s*"
                                r"(%s)\s*[%s]?\s*(%s)(?:\s*\((?:AC|MC|DC|IC)\))?[^,·]*?(?:Orb\s*)?"
                                r"(\d{1,3})°\s*(\d{1,2})[′']"
                                % ("|".join(re.escape(w) for w in _ASP_WOERTER),
                                   "".join(g for _, g in ASPEKTE), _FAKTOR_RE))
            for i, seg in enumerate(segs, start=1):
                for m in muster.finditer(seg):
                    e = {"a": kanon(m.group(1)), "art": _art(m.group(2)), "b": kanon(m.group(3)),
                         "orb": _min(m.group(4), m.group(5)), "orb_sicher": True,
                         "stufe": None, "roh": m.group(0), "mehrfach": False}
                    pruefe_eintrag("%s, Segment %d" % (bez, i), e)
    if transit_gesehen and events is None:
        # 2026-09-19 (W24): ohne events.json bleibt es bei der Form — gesagt, nicht still.
        p.teilweise.append("%d Transit-Segment(e) nur auf ihre Form geprüft — Abgleich gegen "
                           "events.json (Kontakt, Exaktdaten, Annäherungen, Stichtag-Orb) "
                           "übersprungen: keine events.json übergeben (`--events <pfad>` bzw. "
                           "pruefe(…, events_pfad=…))" % len(transit_gesehen))
    if p.geprueft == 0:
        if p.fehler:
            return p.abschluss()
        return p.aussagelos("kein Aspekt-Segment in einem Normal-, Instrument- oder Zugang-Beleg gefunden")
    return p.abschluss()

def _de(iso):
    """'JJJJ-MM-TT' -> 'TT.MM.JJJJ' (die Form des Belegs)."""
    t = (iso or "").split("-")
    return "%s.%s.%s" % (t[2], t[1], t[0]) if len(t) == 3 else (iso or "")

def _tage(a, b):
    """Abstand zweier ISO-Daten in Tagen (b - a); 9999 bei unlesbarem Datum."""
    from datetime import date
    try:
        return (date.fromisoformat(b) - date.fromisoformat(a)).days
    except (TypeError, ValueError):
        return 9999



def _erwartete_haeuser(f):
    """(fuehrendes Haus, Nebenhaus) aus einer FAKTOR-Zeile — Schwellenlage (<= 2°)
    fuehrt das Nebenhaus, Grenzlage (2°–5°) das rechnerische Haus (Datenblatt-Modul).
    Bei `fuehrung=offen` (seit 2026-09-30, K9) fuehrt keins; vorn steht das
    rechnerische Haus."""
    h, nh, ab = f.get("haus"), f.get("nebenhaus"), f.get("abstand")
    if not nh:
        return h, None
    if f.get("fuehrung") == "offen":
        return h, nh
    try:
        a = float(ab) if ab is not None else 99.0
    except ValueError:
        a = 99.0
    return (nh, h) if a <= selektor.SCHWELLE_ORB else (h, nh)

def _p2_beleg_staende(chapters, typ, chart, staende):
    p = _Probe("P2", "Beleg-Stände")
    p.einheit = "Stände-Segmente"
    fak = {f["name"]: f for f in chart.get("faktoren", [])}
    achsen = chart.get("achsen", {})
    if staende is None:
        p.hinweise.append("Keine `## Stände`-Überschrift in der chart_data — "
                          "Gradminuten übersprungen")
    elif not staende:
        p.pruefen.append(
            "Ständetabelle gefunden, aber KEINE Zeile lesbar — Gradminuten "
            "ungeprüft. Erwartetes Zeilenformat: "
            "`| <Faktor> | <NN>°<NN>′ | <Zeichen> | …` mit nacktem Faktornamen "
            "in der ersten Zelle (kein Symbol, kein Zusatz), Gradminuten mit ° "
            "und ′ oder ' in der zweiten. Entweder die Tabelle anpassen oder "
            "diesen Hinweis ausdrücklich abhaken.")

    def pruefe(ort, st):
        p.geprueft += 1
        f = st["faktor"]
        stelle = "%s: „%s“" % (ort, _kurz(st["roh"], 80))
        if f in ACHSEN:
            soll = achsen.get(f)
            if soll is None:
                p.pruefen.append("%s — Achse %s hat keine ACHSE-Zeile im @@SELEKTOR-Block" % (stelle, f))
            elif soll != st["zeichen"]:
                p.fehler.append("%s — Zeichen %s, @@SELEKTOR sagt %s" % (stelle, st["zeichen"], soll))
        else:
            fz = fak.get(f)
            if fz is None:
                p.pruefen.append("%s — %s hat keine FAKTOR-Zeile im @@SELEKTOR-Block"
                                 % (stelle, ANZEIGE.get(f, f)))
            else:
                if fz.get("zeichen") and fz["zeichen"] != st["zeichen"]:
                    p.fehler.append("%s — Zeichen %s, @@SELEKTOR sagt %s"
                                    % (stelle, st["zeichen"], fz["zeichen"]))
                soll1, soll2 = _erwartete_haeuser(fz)
                if st["haus1"] is None:
                    if soll1:
                        p.pruefen.append("%s — kein Haus im Segment; @@SELEKTOR: Haus %s%s"
                                         % (stelle, soll1, "/" + soll2 if soll2 else ""))
                else:
                    if soll1 and st["haus1"] != soll1:
                        if fz.get("fuehrung") == "offen":      # 2026-09-30, K9
                            p.fehler.append("%s — Haus %s vorn, @@SELEKTOR verlangt %s vorn "
                                            "(offene Führung: das rechnerische Haus vorn, "
                                            "gleich stark, Nebenhaus %s)"
                                            % (stelle, st["haus1"], soll1, soll2))
                        else:
                            p.fehler.append("%s — führendes Haus %s, @@SELEKTOR verlangt %s%s vorn"
                                            % (stelle, st["haus1"], soll1,
                                               " (Grenzlage, Nebenhaus %s)" % soll2 if soll2 else ""))
                    elif st["haus2"] and not soll2:
                        p.fehler.append("%s — Beleg nennt ein Nebenhaus %s, @@SELEKTOR kennt keine "
                                        "Grenzlage" % (stelle, st["haus2"]))
                    elif st["haus2"] and soll2 and st["haus2"] != soll2:
                        p.fehler.append("%s — Nebenhaus %s, @@SELEKTOR sagt %s"
                                        % (stelle, st["haus2"], soll2))
        if staende is not None:
            tab = staende.get(f)
            if tab is None:
                p.hinweise.append("%s — nicht in der Ständetabelle, Gradminute nicht geprüft" % stelle)
            else:
                # 2026-09-23 (Pruefbericht Geburtshoroskop 3+4 vom 22.09.c, Inhalt
                # Nr. 1): 1′ lief bis dahin still durch — genau so stand ein
                # abgeschnittener statt des gerundeten Werts an fuenf Stellen im Text,
                # und erst der Zweitleser fand es. Der Beleg uebernimmt den Wert der
                # Staendetabelle; 1′ ist deshalb PRUEFEN, mehr bleibt FEHLER.
                _abw = abs(tab[0] - st["minuten"])
                if _abw > 1:
                    p.fehler.append("%s — %s, Ständetabelle sagt %s"
                                    % (stelle, _orb_txt(st["minuten"]), _orb_txt(tab[0])))
                elif _abw == 1:
                    p.pruefen.append("%s — %s, Ständetabelle sagt %s: 1′ daneben — "
                                     "abgeschnitten statt gerundet? Der Beleg übernimmt "
                                     "den Wert der Ständetabelle"
                                     % (stelle, _orb_txt(st["minuten"]), _orb_txt(tab[0])))
                if tab[1] != st["zeichen"]:
                    p.fehler.append("%s — Zeichen %s, Ständetabelle sagt %s"
                                    % (stelle, st["zeichen"], tab[1]))

    for ch in chapters:
        form = _beleg_form(ch, typ, chapters)
        if form not in ("normal", "instrument"):
            continue
        bez = _bezeichnung(ch)
        segs = _segmente(ch["beleg"])
        if form == "normal":
            st = _staende_segment(segs[0]) if segs else None
            if st is None:
                p.fehler.append("%s, Segment 1: „%s“ — nicht als Stände des führenden Faktors lesbar "
                                "(Faktor Gradminute Zeichen, Haus)" % (bez, _kurz(segs[0] if segs else "", 80)))
                continue
            pruefe("%s, Segment 1" % bez, st)
        else:
            for i, seg in enumerate(segs, start=1):
                st = _staende_segment(seg)
                if st is None:
                    p.fehler.append("%s, Segment %d: „%s“ — Instrument-Segment nicht als Stände lesbar"
                                    % (bez, i, _kurz(seg, 80)))
                    continue
                pruefe("%s, Segment %d" % (bez, i), st)
    # 2026-09-30 (K9, Chris-Entscheidung): offene Fuehrung — keins der beiden
    # Haeuser fuehrt; die Signatur eines Kapitels, das er fuehrt, traegt „gleich
    # stark" (Wortform aus dem ⚠-Block) — nur PRUEFEN. Den Satz zur Geburtszeit
    # verlangt die Probe seit 2026-10-01 nicht mehr (Chris-Entscheidung, F1).
    offen = {n for n, f in fak.items() if f.get("fuehrung") == "offen"}
    if offen:
        for ch in chapters:
            form = _beleg_form(ch, typ, chapters)
            if form not in ("normal", "instrument"):
                continue
            segs = _segmente(ch["beleg"])
            if form == "normal":
                sts = [_staende_segment(segs[0])] if segs else []
            else:
                sts = [_staende_segment(sg) for sg in segs]
            for i, st in enumerate(x for x in sts if x):
                n = st["faktor"]
                if n not in offen:
                    continue
                if form == "normal" and i == 0 and \
                        "gleich stark" not in (ch.get("signatur") or ""):
                    p.pruefen.append(
                        "%s — %s führt das Kapitel mit offener Führung; die Signatur "
                        "sagt nicht „gleich stark“ (Wortform aus dem ⚠-Block der "
                        "referenz.md): „%s“" % (_bezeichnung(ch), ANZEIGE.get(n, n),
                                               _kurz(ch.get("signatur"), 70)))
    if p.geprueft == 0 and not p.fehler:
        return p.aussagelos("kein Stände-Segment gefunden")
    return p.abschluss()

def _fuehrer_im_beleg(ch):
    segs = _segmente(ch.get("beleg"))
    st = _staende_segment(segs[0]) if segs else None
    if st:
        return st["faktor"]
    if segs:
        m = FAKTOR_RE.match(segs[0])
        return kanon(m.group(1)) if m else None
    return None

def _name_in_text(schluessel, text):
    """Steht der Faktor (in einer seiner Schreibweisen) im Text?"""
    # KOMPOSITUM ZAEHLT (geaendert 2026-09-17, Klasse-2-Entscheidungslauf).
    # Die Rueckschau schloss einen vorangehenden BINDESTRICH aus, womit
    # "Fische-Sonne" als "Sonne fehlt" galt — eine Form, die der
    # Klartext-Standard ausdruecklich zulaesst. Im Prueflauf vom 16.09. war das
    # ein P7-FEHLER ohne Fehler.
    for s, k in _FAKTOR_SCHREIBWEISEN:
        if k != schluessel:
            continue
        # GEBEUGTE ACHSENNAMEN ZAEHLEN (neu 2026-09-18). "zum Aszendenten" ist
        # dieselbe Angabe wie "Aszendent"; die harte Rueckschau meldete sie als
        # "Faktor fehlt" — derselbe Fehlalarm-Typ wie "Fische-Sonne" am 16.09.
        # Nur fuer Namen auf -ent (Aszendent, Deszendent), sonst nichts gelockert.
        _endung = r"(?:en|es|s)?" if s.endswith("ent") else ""
        if re.search(r"(?<![\wäöüÄÖÜß])" + re.escape(s) + _endung + r"(?![\wäöüÄÖÜß])",
                     text or ""):
            return True
    # "Knoten" allein gilt fuer den Mondknoten
    if schluessel == "MONDKNOTEN" and re.search(r"(?<![\wäöüß])Knoten(?:achse)?(?![\wäöüß])", text or ""):
        return True
    return False

def _kontakt_faktoren(roh):
    """Die beiden Faktoren eines Transit-Kontakts aus `fuehrt=`.

    Das Transit-Modul schreibt seit dem 2026-09-18: `fuehrt=T-Saturn \u25a1 R-Sonne`.
    -> (a, b) kanonisch, oder (None, None), wenn die Form nicht lesbar ist.
    """
    teile = re.findall(r"[TR]-\s*(" + _FAKTOR_RE + r")", roh or "")
    if len(teile) != 2:
        return None, None
    return kanon(teile[0]), kanon(teile[1])


def _p3_p7_kapitel_themen(chapters, typ, themen, sprache_analyse="de"):
    p3 = _Probe("P3", "Kapitel gegen Themenliste")
    p7 = _Probe("P7", "Signatur nennt den Führer")
    p3.einheit = p7.einheit = "Kapitel"
    if typ not in ("geburt", "transit"):
        grund = ("Kapitel-Skelett des Typs %s ist in dieser Probe nicht hinterlegt "
                 "(Geburtshoroskop und Transit)" % (typ or "unbekannt"))
        return p3.uebersprungen(grund), p7.uebersprungen(grund), {}
    if not themen:
        return p3.aussagelos("keine THEMA-Zeile in der chart_data gefunden"), \
               p7.aussagelos("keine THEMA-Zeile in der chart_data gefunden"), {}
    # 2026-09-19 (L7): Wo die Themenzaehlung beginnt, sagt `_zaehlung_ab()` — im
    # Transit immer bei 1, im Geburtshoroskop bei 1 (Getriebe-Kapitel mit
    # Wort-Kicker) oder bei 2 (Analyse alter Form: `Kapitel 1` ist das Getriebe).
    _ab = _zaehlung_ab(chapters, typ)
    kap = [ch for ch in chapters if (_kicker_nr(ch["kicker"]) or 0) >= _ab]
    zuordnung = {}
    if len(kap) != len(themen):
        # Der haeufigste Grund fuer genau ein fehlendes Kapitel: Das
        # Getriebe-Kapitel traegt seinen Wort-Kicker `Getriebe` nicht, die Probe
        # liest die Analyse deshalb in der alten Form und verliert THEMA 1.
        wink = ""
        if typ != "transit" and _ab == 2 and len(kap) == len(themen) - 1:
            wink = (" — trägt das Getriebe-Kapitel den Wort-Kicker `Getriebe`? Ohne ihn "
                    "zählt die Probe `Kapitel 1` als Getriebe-Kapitel (alte Form) und "
                    "beginnt die Themen bei `Kapitel 2`")
        p3.fehler.append("Zahl: %d nummerierte Themenkapitel (Kapitel %d ff.), aber %d "
                         "THEMA-Zeilen%s" % (len(kap), _ab, len(themen), wink))
    for i, (ch, th) in enumerate(zip(kap, themen)):
        p3.geprueft += 1
        p7.geprueft += 1
        zuordnung[id(ch)] = th
        bez = _bezeichnung(ch)
        if typ == "transit":
            # fuehrt= traegt hier den KONTAKT. Geprueft wird, ob die Signatur BEIDE
            # Faktoren nennt; der Beleg-Fuehrer-Vergleich entfaellt, weil Segment 1
            # im Transit die Staende des getroffenen Radix-Punktes traegt.
            ka, kb = _kontakt_faktoren(th["fuehrt_roh"])
            if not ka:
                p3.fehler.append("THEMA %d: fuehrt= trägt keinen lesbaren Kontakt "
                                 "(erwartet `T-<Faktor> <Aspekt> R-<Faktor>`): „%s“"
                                 % (th["nr"], _kurz(th["fuehrt_roh"], 60)))
                continue
            fehlt = [x for x in (ka, kb) if not _name_in_text(x, ch.get("signatur"))]
            if fehlt:
                p7.fehler.append("%s ↔ THEMA %d: Signatur nennt %s nicht („%s“)"
                                 % (bez, th["nr"],
                                    " und ".join(ANZEIGE.get(x, x) for x in fehlt),
                                    _kurz(ch.get("signatur"), 70)))
            # Der Kapitel-Schluessel heisst `title`, nicht `titel` — build.parse_analyse()
            # gibt ihn so zurueck (stand als eigener Befund in der Sammelliste).
            if sprache_analyse == "de" and th["titel"] \
                    and _ws(th["titel"]).casefold() != _ws(ch.get("title")).casefold():
                p3.pruefen.append("%s ↔ THEMA %d: Titel weicht vom Arbeitstitel ab "
                                  "(„%s“ gegen „%s“)"
                                  % (bez, th["nr"], _kurz(ch.get("title"), 50),
                                     _kurz(th["titel"], 50)))
            continue
        soll = th["fuehrt"]
        if soll is None:
            p3.fehler.append("THEMA %d: fuehrt= trägt keinen lesbaren Faktor („%s“)"
                             % (th["nr"], _kurz(th["fuehrt_roh"], 60)))
            continue
        ist = _fuehrer_im_beleg(ch)
        if ist != soll:
            p3.fehler.append("%s ↔ THEMA %d: Beleg-Segment 1 führt %s, Themenliste sagt %s"
                             % (bez, th["nr"], ANZEIGE.get(ist, ist) if ist else "—", ANZEIGE.get(soll, soll)))
        if not _name_in_text(soll, ch.get("signatur")):
            p7.fehler.append("%s ↔ THEMA %d: Signatur nennt %s nicht („%s“)"
                             % (bez, th["nr"], ANZEIGE.get(soll, soll), _kurz(ch.get("signatur"), 70)))
        if sprache_analyse != "de":
            if i == 0:
                p3.hinweise.append("Titelvergleich entfällt: Analyse auf Englisch, Themenliste "
                                   "deutsch — geprüft werden Führer, Zahl und Reihenfolge")
        elif th["titel"] and _ws(th["titel"]).casefold() != _ws(ch["title"]).casefold():
            p3.pruefen.append("%s ↔ THEMA %d: Titel weicht ab — Themenliste: „%s“"
                              % (bez, th["nr"], _kurz(th["titel"], 70)))
    for ch in kap[len(themen):]:
        p3.fehler.append("%s: Kapitel ohne THEMA-Zeile" % _bezeichnung(ch))
    for th in themen[len(kap):]:
        p3.fehler.append("THEMA %d „%s“: Thema ohne Kapitel" % (th["nr"], _kurz(th["titel"], 60)))
    return p3.abschluss(), p7.abschluss(), zuordnung

def _folge_variante(wortlaute, kurz):
    """Sollfolge: volle sieben oder Kurzform ohne Bewegung 3 und 4."""
    return [w for i, w in enumerate(wortlaute) if not (kurz and i in (2, 3))]

def _passt(subs, soll):
    if len(subs) != len(soll):
        return False
    for s, w in zip(subs, soll):
        if isinstance(w, tuple):
            if s not in w:
                return False
        elif s != w:
            return False
    return True

def _p4_bewegungsfolge(chapters, typ, zuordnung):
    p = _Probe("P4", "Bewegungsfolge")
    p.einheit = "Kapitel"
    if typ not in WORTLAUTE:
        return p.uebersprungen("Typ %s hat keine Wortlaute in WORTLAUTE" % (typ or "unbekannt"))
    saetze = WORTLAUTE[typ] if isinstance(WORTLAUTE[typ], dict) else {typ: WORTLAUTE[typ]}
    kapitel = _themenkapitel(chapters, typ)
    if not kapitel:
        return p.aussagelos("kein Themenkapitel mit Bewegungsfolge gefunden")
    for ch in kapitel:
        bez = _bezeichnung(ch)
        subs = _subheads(ch)
        th = zuordnung.get(id(ch))
        form = th["form"] if th else None
        zugang = _ist_zugang(ch)
        if not subs:
            if typ == "geburt":
                p.fehler.append("%s: keine ###-Bewegung — Themenkapitel ohne Bewegungsfolge" % bez)
            else:
                p.pruefen.append("%s: kein ###-Zwischentitel — Getriebe-Kapitel oder fehlende Folge?" % bez)
            continue
        p.geprueft += 1
        # zulaessige Sollfolgen je form=
        varianten = []
        for teil, wl in saetze.items():
            voll = _folge_variante(wl, False)
            kurz = _folge_variante(wl, True)
            ohne_wurzel = [w for i, w in enumerate(wl) if i != 2]
            if zugang:
                varianten += [(teil, "Zugang ohne Wurzel und Widerstand", kurz),
                              (teil, "Zugang ohne Wurzel", ohne_wurzel)]
            elif form == "kurz":
                varianten.append((teil, "form=kurz", kurz))
            elif form == "ressource":
                varianten += [(teil, "form=ressource (Kurzform)", kurz),
                              (teil, "form=ressource (volle Folge)", voll)]
            elif form == "voll":
                varianten.append((teil, "form=voll", voll))
            else:   # form unbekannt (keine Zuordnung zur Themenliste)
                varianten += [(teil, "volle Folge", voll), (teil, "Kurzform", kurz)]
        if any(_passt(subs, v[2]) for v in varianten):
            continue
        # Befund formulieren: fehlend / ueberzaehlig / vertauscht, gegen die
        # naechstliegende Sollfolge (groesste Schnittmenge mit den Zwischentiteln)
        def _flach(folge):
            return set(x for w in folge for x in (w if isinstance(w, tuple) else (w,)))
        bekannte = set()                       # Wortlaute DIESES Typs
        for wl in saetze.values():
            bekannte |= _flach(wl)
        fremd = [s for s in subs if s not in ALLE_WORTLAUTE]
        anderer_typ = [s for s in subs if s not in bekannte and s in ALLE_WORTLAUTE]
        best = max(varianten, key=lambda v: len(set(subs) & _flach(v[2])))
        soll_set = _flach(best[2])
        fehlend = [w[0] if isinstance(w, tuple) else w for w in best[2]
                   if not any((s in w) if isinstance(w, tuple) else (s == w) for s in subs)]
        ueberz = [s for s in subs if s not in soll_set and s in bekannte]
        teile = []
        if fremd:
            teile.append("unbekannter Zwischentitel: " + ", ".join("„%s“" % s for s in fremd))
        if anderer_typ:
            teile.append("Wortlaut eines anderen Typs: " + ", ".join("„%s“" % s for s in anderer_typ))
        if fehlend:
            teile.append("fehlt: " + ", ".join("„%s“" % s for s in fehlend))
        if ueberz:
            teile.append("überzählig: " + ", ".join("„%s“" % s for s in ueberz))
        if not teile:
            teile.append("Reihenfolge vertauscht: " + " → ".join(subs))
        p.fehler.append("%s (%s): %s" % (bez, best[1] + ("" if len(saetze) == 1 else ", " + best[0]),
                                          "; ".join(teile)))
    return p.abschluss()

def _register_eintraege(ch):
    """Die Zeilen des Rechenschaftskapitels als Liste von Texten (ohne Listennummer)."""
    out = []
    for b in ch["blocks"]:
        if b.get("type") == "subhead":
            continue
        t = b["text"]
        if b.get("type") == "li":
            out.append(_ws(t))
            continue
        # nummerierte Liste, die parse_analyse als einen Absatz gelesen hat, und
        # Zeilen ohne Nummer: an Zeilenanfang und an "n. " trennen
        for stueck in re.split(r"\n|(?:(?<=\s)|^)\d{1,2}\.\s+(?=[A-ZÄÖÜ])", t):
            if stueck.strip():
                out.append(_ws(stueck))
    return out

# --- P5: Kapitelangaben im Register (2026-10-13, Strang 3 des Wartungslaufs „Proben
# fuer Zeit, Naehe, Register und Fundstellen“; Startprompt
# `claude/STARTPROMPT_Probenlauf_2026-10-13.md`). Warum: Die Zweitleser vom 12.10.
# fanden in den Rechenschaftszeilen Kapitelangaben, die fehlten (ein Faktor klingt
# in einem Kapitel mit, weil sein Aspekt dort `aspekte=` traegt, und die Zeile nennt
# das Kapitel nicht), Achsen-Zeilen, die nie geprueft wurden (P5 nahm Achsen aus),
# und eine Angabe, deren Kapitel den Faktor gar nicht nennt. Regel (Datenblatt-
# Modul, Rechenschaftsregel): „bei einem Mitklinger zusaetzlich, in welchem Kapitel
# er vorkommt“. Gelesen wird beidseitig:
#   SOLL  Kapitel n, wenn THEMA n den Faktor in `klingt=` (je Eintrag der erste
#         Faktor; was in Klammern steht, beschreibt ihn nur) oder in `aspekte=`
#         (beide Enden) traegt UND das Kapitel ihn in Signatur oder Lesetext nennt
#         (der Beleg zaehlt nicht — er ist Datenzeile, kein Vorkommen fuer den Leser).
#   IST   jede Kapitelnummer der Zeile; nennt die Zeile „klingt … in Kapitel n“ und
#         das Kapitel nennt den Faktor nicht, ist die Angabe leer.
# Dazu der Satz des Instrument-Kapitels „Mit dem MC haben Kapitel 2 und 5 zu tun“
# gegen dieselbe Soll-Menge. Nur PRUEFEN, jeder Hinweis mit dem Datenwert.
_P5_KAP_LISTE_RE = re.compile(r"(?<![\wäöüÄÖÜß])(?:Kapiteln|Kapitels|Kapitel|Chapters?)\s+(?P<l>\d{1,2}(?:\s*"
                              r"(?:,|und|sowie|oder|and|&)\s*(?:(?:Kapiteln|Kapitel|Chapters?)\s+)?\d{1,2})*)(?!\d)")
_P5_KLINGT_RE = re.compile(r"(?<![\wäöüÄÖÜß])(?:[Kk]lingt|[Kk]lingen|mitklingt|mitklingen|[Ee]choes|[Ee]choed)"
                           r"(?![\wäöüÄÖÜß])")
_P5_ACHSE_ALIAS = {
    "IC": re.compile(r"(?<![\wäöüÄÖÜß])(?:Himmelstiefe|tiefste[nr]?\s+Punkt\s+deines\s+(?:Bildes|Horoskops))"),
    "MC": re.compile(r"(?<![\wäöüÄÖÜß])höchste[nr]?\s+Punkt\s+deines\s+(?:Bildes|Horoskops)"),
    # die Knotenachse nennt beide Enden („die Achse führt vom Vertrauten weg“)
    "SUEDKNOTEN": re.compile(r"(?<![\wäöüÄÖÜß])(?:Knotenachse|südliche[nr]?\s+(?:Mond)?[Kk]noten)")}
_P5_HABEN_KAPITEL_RE = re.compile(
    r"[Mm]it\s+(?:dem|der|deinem|deiner)\s+(?P<f>%s)\w*\s+(?:haben|hat)\s+(?:auch\s+)?"
    r"(?P<l>(?:die\s+)?Kapitel\s+\d{1,2}(?:\s*(?:,|und|sowie)\s*(?:Kapitel\s+)?\d{1,2})*)\s+(?:\w+\s+)?zu\s+tun"
    % _FAKTOR_RE)


def _p5_klingt_nummern(text):
    """Die Kapitelnummern NUR aus dem Satzteil, der mit „klingt …“ beginnt (bis „;“
    oder Satzende) — „…; ausgeführt im Kapitel Instrument, gezählt in Kapitel 1“
    behauptet kein Mitklingen in Kapitel 1."""
    out = set()
    for m in _P5_KLINGT_RE.finditer(text or ""):
        rest = re.split(r"[;.](?:\s|$)", text[m.start():], 1)[0]
        out |= _p5_kap_nummern(rest)
    return out


def _p5_kap_nummern(text):
    """Alle Kapitelnummern eines Textes („Kapitel 3 und Kapitel 5“, „Kapiteln 2, 4 und 7“)."""
    out = set()
    for m in _P5_KAP_LISTE_RE.finditer(text or ""):
        out |= {int(x) for x in re.findall(r"\d{1,2}", m.group("l"))}
    return out


def _p5_kapitel_texte(chapters):
    """Kapitelnummer -> Lesetext (Signatur und Fliesstext; ohne Beleg, ohne Zwischentitel)."""
    out = {}
    for ch in chapters:
        n = _kicker_nr(ch.get("kicker"))
        if n:
            out[n] = "\n".join([ch.get("signatur") or ""] +
                               [b.get("text") or "" for b in ch["blocks"] if b.get("type") != "subhead"])
    return out


def _p5_nennt(f, text):
    """Nennt der Text den Faktor (Schreibweisen der Probe, auch gebeugt — „Plutos
    Kraft“, „deines Mondes“ —, dazu „Himmelstiefe“ und „der tiefste/hoechste Punkt
    deines Bildes“ fuer IC und MC, „Knotenachse“ fuer den Suedknoten)?"""
    if _name_in_text(f, text) or any(k == f for _a, _e, k in _faktoren_im_satz(text or "")):
        return True
    rx = _P5_ACHSE_ALIAS.get(f)
    return bool(rx and rx.search(text or ""))


def _p5_eintraege(wert):
    """Die kommagetrennten Eintraege eines THEMA-Feldes; ein Komma in Klammern trennt nicht."""
    out, tiefe, cur = [], 0, []
    for c in wert or "":
        if c == "(":
            tiefe += 1
        elif c == ")":
            tiefe = max(0, tiefe - 1)
        if c == "," and tiefe == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    out.append("".join(cur).strip())
    return [x for x in out if x]


def _p5_traeger(themen):
    """Faktor -> {THEMA-Nr: [(Feld, Eintrag)]} aus `klingt=` und `aspekte=`."""
    out = {}
    for th in themen or []:
        roh = th.get("roh") or ""
        for feld in ("klingt", "aspekte"):
            for eintrag in _p5_eintraege(_thema_feld(roh, feld)):
                fs = [f for _a, _e, f in _faktoren_im_satz(re.sub(r"\([^()]*\)", " ", eintrag))]
                for f in (fs[:1] if feld == "klingt" else list(dict.fromkeys(fs[:2]))):
                    out.setdefault(f, {}).setdefault(th["nr"], []).append((feld, eintrag))
    return out


def _p5_kontakt_satz(k, text):
    """Der erste Satz des Textes, der Transiter UND Ziel des Kontakts nennt (beim
    Selbst-Transit den Namen zweimal oder „eigen…“/„Rückkehr“), sonst None."""
    t, _art, r = k
    for satz in _saetze(text or ""):
        if not (_p5_nennt(t, satz) and _p5_nennt(r, satz)):
            continue
        if t == r:
            n = sum(len(re.findall(r"(?<![\wäöüÄÖÜß])" + re.escape(sw) + r"(?![\wäöüÄÖÜß])", satz))
                    for sw, kk in _FAKTOR_SCHREIBWEISEN if kk == t)
            if n < 2 and not re.search(r"R(?:ü|ue)ckkehr|Wiederkehr|zurück|(?<![\wäöüÄÖÜß])[Ee]igen", satz):
                continue
        return satz
    return None


def _p5_kapitelangaben(p, chapters, themen, eintraege, typ, fuehrer):
    """Kapitelangaben der Rechenschaftszeilen und des Satzes „Mit dem <Faktor> haben
    Kapitel … zu tun“ gegen Themenliste und Kapiteltext (s. Kommentar oben)."""
    ab = _zaehlung_ab(chapters, typ)
    kap_txt = _p5_kapitel_texte(chapters)
    traeger = _p5_traeger(themen)

    def soll_von(f):
        tr = {nr + (ab - 1): v for nr, v in traeger.get(f, {}).items()}
        nennt = {k for k, t in kap_txt.items() if _p5_nennt(f, t)}
        return {k for k in tr if k in nennt}, nennt, tr

    def grund(f, k, tr):
        return "THEMA %d %s" % (k - (ab - 1), "; ".join("%s=: %s" % (fd, _kurz(e, 50)) for fd, e in tr[k][:2]))

    for e in eintraege:
        m = FAKTOR_RE.match(re.sub(r"^(?:[Dd](?:er|ie|as)|[Tt]he)\s+", "", e))
        if not m:
            continue
        f = kanon(m.group(1))
        if f in fuehrer:
            continue
        ist = _p5_kap_nummern(e)
        soll, nennt, tr = soll_von(f)
        fehlt = sorted(soll - ist)
        if fehlt:
            p.pruefen.append("%s — die Registerzeile nennt %s nicht, obwohl %s dort mitklingt (%s; das "
                             "Kapitel nennt %s): „%s“"
                             % (ANZEIGE.get(f, f), ", ".join("Kapitel %d" % k for k in fehlt),
                                ANZEIGE.get(f, f), " · ".join(grund(f, k, tr) for k in fehlt),
                                ANZEIGE.get(f, f), _kurz(e, 90)))
        if _P5_KLINGT_RE.search(e):
            leer = sorted(k for k in _p5_klingt_nummern(e) if k in kap_txt and k not in nennt)
            if leer:
                p.pruefen.append("%s — die Registerzeile nennt %s, aber dort steht %s weder in der Signatur "
                                 "noch im Text: „%s“"
                                 % (ANZEIGE.get(f, f), ", ".join("Kapitel %d" % k for k in leer),
                                    ANZEIGE.get(f, f), _kurz(e, 90)))
    for ch in chapters:
        if _ist_kicker(ch, "Rechenschaft"):
            continue
        for b in ch["blocks"]:
            for m in _P5_HABEN_KAPITEL_RE.finditer(b.get("text") or ""):
                f = kanon(m.group("f"))
                ist = _p5_kap_nummern(m.group("l"))
                soll, nennt, tr = soll_von(f)
                fehlt = sorted(soll - ist)
                leer = sorted(k for k in ist if k in kap_txt and k not in nennt)
                if fehlt or leer:
                    p.pruefen.append("%s: „%s“ — %s"
                                     % (_bezeichnung(ch), _kurz(m.group(0), 110), "; ".join(
                                         (["es fehlt %s (%s; das Kapitel nennt %s)"
                                           % (", ".join("Kapitel %d" % k for k in fehlt),
                                              " · ".join(grund(f, k, tr) for k in fehlt), ANZEIGE.get(f, f))]
                                          if fehlt else []) +
                                         (["%s nennt %s nicht" % (", ".join("Kapitel %d" % k for k in leer),
                                                                  ANZEIGE.get(f, f))] if leer else []))))


def _p5_rechenschaft(chapters, chart, themen, typ=None, txt=None, events=None,
                     chart_data_pfad=None, events_pfad=None, sprache_analyse="de"):
    """Geburtshoroskop: Faktor-Register im Kapitel `Rechenschaft`.
    Transit (2026-09-19, W43): Kontakt-Register im Kapitel `Mitlaufendes` —
    s. `_p5_mitlaufendes()`; die Zusatzparameter braucht nur dieser Zweig."""
    p = _Probe("P5", "Rechenschafts-Register")
    p.einheit = "Faktoren"
    rech = [ch for ch in chapters if _ist_kicker(ch, "Rechenschaft")]
    if typ == "transit" or (typ is None and not rech
                            and any(_ist_kicker(ch, "Mitlaufendes") for ch in chapters)):
        return _p5_mitlaufendes(p, chapters, themen, txt or "", events,
                                chart_data_pfad, events_pfad, sprache_analyse)
    if not rech:
        # 2026-09-19 (W43): Die alte Begruendung „der Transit führt sein Register in
        # der chart_data" war falsch — es steht unter `Mitlaufendes` in der Analyse.
        return p.uebersprungen("kein Kapitel mit Kicker „Rechenschaft“ (das Register des "
                               "Transits heißt „Mitlaufendes“ und wird mit Typ transit geprüft)")
    if not chart.get("faktoren"):
        return p.aussagelos("keine FAKTOR-Zeile im @@SELEKTOR-Block")
    if not themen:
        return p.aussagelos("keine THEMA-Zeile in der chart_data — Führer nicht bestimmbar")
    fuehrer = {t["fuehrt"] for t in themen if t["fuehrt"]}
    eintraege = _register_eintraege(rech[0])
    if not eintraege:
        return p.aussagelos("Rechenschaftskapitel ohne Zeilen")

    def hat_zeile(schluessel):
        # Die Zeile beginnt mit dem Namen; ein Artikel davor ("Der Glückspunkt, …")
        # wird geduldet, mehr nicht.
        for e in eintraege:
            m = FAKTOR_RE.match(re.sub(r"^(?:[Dd](?:er|ie|as)|[Tt]he)\s+", "", e))
            if m and kanon(m.group(1)) == schluessel:
                return e
        return None

    for f in chart["faktoren"]:
        name = f["name"]
        if name in ACHSEN:
            continue
        p.geprueft += 1
        z = hat_zeile(name)
        if name in fuehrer:
            if z:
                p.pruefen.append("%s führt ein Thema und hat trotzdem eine Registerzeile: „%s“"
                                 % (ANZEIGE.get(name, name), _kurz(z, 80)))
        elif not z:
            p.fehler.append("%s führt kein Thema und hat keine Zeile im Rechenschaftskapitel, "
                            "die mit seinem Namen beginnt" % ANZEIGE.get(name, name))
    # 2026-10-13 (Strang 3): Kapitelangaben beidseitig, Achsen eingeschlossen
    if sprache_analyse == "de":
        _p5_kapitelangaben(p, chapters, themen, eintraege, typ, fuehrer)
    return p.abschluss()

def _kontakte_in(text):
    """Alle Kontakte `T-X <Aspekt> R-Y` eines Textes (Themenliste, Block
    TRANSIT-RECHENSCHAFT; Glyphe oder Aspektwort) -> [(T, Aspektart, R)] kanonisch
    (2026-09-19, W43)."""
    out = []
    for m in re.finditer(r"T-\s*(?:%s|Knoten)[^·|\n]*?R-\s*(?:%s|Knoten)(?![\wäöüÄÖÜß])"
                         % (_FAKTOR_RE, _FAKTOR_RE), text or ""):
        k = _kontakt_aus_segment(m.group(0))
        if k and k["art"]:
            out.append((k["t"], k["art"], k["r"]))
    return out

def _thema_feld(roh, name):
    """Wert eines Feldes einer THEMA-Zeile (`aspekte=`, `fuehrt=` …) oder ''."""
    m = re.search(r"(?:^|\|)\s*%s=(.*?)(?=\s*\|\s*[a-z_]+=|\s*$)" % name, roh or "", re.S)
    return _ws(m.group(1)) if m else ""

def _kontakt_name(k):
    return "T-%s %s R-%s" % (ANZEIGE.get(k[0], k[0]), k[1], ANZEIGE.get(k[2], k[2]))

# Ziel einer Registerzeile in Prosa (2026-09-23c): der Faktor hinter
# „dein…"/„your" — auch mit EINEM Adjektiv („deinem eigenen Jupiter", „deinem
# natalen Mond") und einem Vorsatz mit Bindestrich („deiner Fische-Sonne") — oder
# hinter zu/zum/zur/über/auf/to („zur Venus") oder als zweites Ziel hinter
# und/sowie/oder („zu deiner Sonne und Venus"). „dein laufender Jupiter" zaehlt
# nicht, das ist der Transiter. Gelesen wird nur der KOPF der Zeile, vor dem
# ersten Gedankenstrich, Komma, Semikolon oder der ersten Klammer; was dahinter
# steht („…, der Herrscherin deines Aszendenten"), ist Erlaeuterung
# (Zweitleser 2026-09-23c).
_PROSA_ZIEL_VOR_RE = re.compile(
    r"(?:(?<![\wäöüÄÖÜß])(?:dein(?:em|er|en|es|e)?|your)\s+"
    r"(?:(?!(?:laufend|transitierend|running|transiting)\w*\s)[\wäöüÄÖÜß]+\s+)?"
    r"|(?<![\wäöüÄÖÜß])(?:zu|zum|zur|über|ueber|auf|to|und|sowie|oder|and|or)\s+"
    r"(?:de[mnr]\s+|the\s+)?)"
    r"(?:[\wäöüÄÖÜß]+-)?$", re.I)


def _prosa_ziele(z):
    """Die Faktoren, die im Kopf einer Registerzeile als Radix-Ziel stehen -> set."""
    kopf = re.split(r"\s[—–]\s|[,;(]", z or "", 1)[0]
    return {f for a, _e, f in _faktoren_im_satz(kopf)
            if _PROSA_ZIEL_VOR_RE.search(kopf[max(0, a - 40):a])}

def _registerzeile(k, zeilen):
    """Die Registerzeile, die den Kontakt k nennt: Transiter UND Ziel; traegt die
    Zeile ein Aspektwort, muss es passen; beim Selbst-Transit (Saturn □ Saturn,
    Knotenrueckkehr) der Name zweimal oder „Rückkehr"/„eigen…"."""
    t, art, r = k
    for z in zeilen:
        if not (_name_in_text(t, z) and _name_in_text(r, z)):
            continue
        # SEITE PRUEFEN, nicht nur Anwesenheit (2026-09-22, Klasse-2-Punkt 4).
        # Traegt die Zeile die Praefixe T-/R-, muss der Transiter hinter T- und
        # das Ziel hinter R- stehen. Ohne Praefixe bleibt es bei der alten
        # Pruefung - eine Zeile in Prosa soll nicht durchfallen.
        _t_seite = {kanon(m) for m in re.findall(r"\bT-\s?([A-Za-zÄÖÜäöüß]+)", z)}
        _r_seite = {kanon(m) for m in re.findall(r"\bR-\s?([A-Za-zÄÖÜäöüß]+)", z)}
        if _t_seite and _r_seite and not (t in _t_seite and r in _r_seite):
            continue
        # ZIEL PRUEFEN AUCH IN PROSA (2026-09-23c; Pruefberichte Transit 1+2 vom
        # 23.09.b und 3+4 vom 23.09.c: 4 PRUEFEN, keines zutreffend). Ohne
        # Praefixe nahm die Probe die ERSTE Zeile mit beiden Namen — beim
        # vertauschten Paar („Mondknoten im Sextil zu deinem Jupiter" fuer
        # T-Jupiter ⚹ R-Mondknoten) und beim Selbst-Transit (die Zeile desselben
        # Transiters an einem anderen Ziel) eine fremde. In Prosa steht das
        # Radix-Ziel hinter „dein…"/„your"; nennt die Zeile so ein Ziel, muss r
        # darunter sein. Eine Zeile ohne solches Ziel wird geprueft wie bisher.
        if not (_t_seite and _r_seite):
            _ziele = set(_r_seite) or _prosa_ziele(z)
            _ziele |= {SPIEGEL_FAKTOR[x] for x in _ziele if x in SPIEGEL_FAKTOR}
            if _ziele and r not in _ziele:
                continue
        if t == r:
            # 2026-10-13 (Strang 3): Steht vor dem ersten Namen ein ANDERER Transiter, ist
            # es dessen Zeile („Uranus im Sextil zu deinem Neptun: …; Raum für das eigene
            # Tempo“ ist nicht Neptun ⚹ Neptun, auch wenn „eigene“ darin steht).
            _fs = [f for _a, _e, f in _faktoren_im_satz(z)]
            if _fs and _fs[0] != t and _fs[0] in ("JUPITER", "SATURN", "URANUS", "NEPTUN", "PLUTO",
                                                  "CHIRON", "MONDKNOTEN", "PHOLUS", "MARS"):
                continue
            n = sum(len(re.findall(r"(?<![\wäöüÄÖÜß])" + re.escape(s) + r"(?![\wäöüÄÖÜß])", z))
                    for s, kk in _FAKTOR_SCHREIBWEISEN if kk == t)
            if t == "MONDKNOTEN":
                n += len(re.findall(r"(?<![\wäöüÄÖÜß])Knoten(?![\wäöüÄÖÜß])", z))
            if n < 2 and not re.search(r"R(?:ü|ue)ckkehr|Wiederkehr|"   # „eigen" als Wort,
                                       r"(?<![\wäöüÄÖÜß])[Ee]igen(?:e[mnrs]?)?"  # nicht in „zeigen"
                                       r"(?![\wäöüÄÖÜß])", z):              # (2026-09-23c)
                continue
        arten = {(_art(m.group(1)) if m.group(1) else _ASP_GLYPH.get(m.group(2)))
                 for m in ASPEKT_RE.finditer(z)}
        if arten and art not in arten:
            continue
        return z
    return None

# Block TRANSIT-RECHENSCHAFT (Ultimativ: SAMMELKAPITEL) der chart_data: Anfang und
# Ende wie build._TR_BLOCK_START / build._TR_BLOCK_ENDE und dessen Leseweise in
# kontakt_heimat() (seit 2026-09-19, W9) — der Rest der Kopfzeile gehoert zum Block,
# die Grenze gilt ab der Folgezeile. Hier nachgebildet, damit die Probe auch mit
# einer aelteren build-Fassung dieselbe Zeilenmenge liest.
_TR_START_RE = re.compile(r"^[ \t>*-]*(?:TRANSIT-RECHENSCHAFT|SAMMELKAPITEL)\s*:", re.M)
_TR_ENDE_RE = re.compile(r"^(?:#{1,6} |@@|THEMA \d+ \||[ \t>*-]*(?:GESTRICHEN|RECHENSCHAFT|"
                         r"REGISTER|SAMMELKAPITEL|TRANSIT-RECHENSCHAFT)\s*:)", re.M)

def _tr_block(txt):
    """Der Text des Blocks TRANSIT-RECHENSCHAFT (samt Rest der Kopfzeile) oder ''."""
    out = []
    for m in _TR_START_RE.finditer(txt or ""):
        rest = txt[m.end():]
        nl = rest.find("\n")
        kopf, folge = (rest, "") if nl < 0 else (rest[:nl], rest[nl:])
        e = _TR_ENDE_RE.search(folge)
        out.append(kopf + (folge[:e.start()] if e else folge))
    return "\n".join(out)

def _p5_klingt_transit(p, k, z, klingend, aspekte_nr, kap_txt):
    """Transit-Register (2026-10-13, Strang 3): Ein `klingt=`-Kontakt, den sein Kapitel
    nennt, braucht die Kapitelangabe; eine Angabe „klingt … in Kapitel n“, deren
    Kapitel den Kontakt weder nennt noch unter `aspekte=` fuehrt, ist leer. Chris-
    Entscheidung 2026-10-13 (Fragenblock des Wartungslaufs, Frage b: „ja“): klingt= heisst
    im Kapitel erwaehnt, nicht gedeutet; die Registerzeile traegt die Kapitelangabe, wenn
    das Kapitel den Kontakt nennt; auf der Uhr steht er nicht. Nur PRUEFEN, mit dem Satz
    bzw. dem Kapitel als Datenwert."""
    nrs = _p5_kap_nummern(z)
    if k in klingend:
        n = klingend[k]
        satz = _p5_kontakt_satz(k, kap_txt.get(n, ""))
        if satz and n not in nrs:
            p.pruefen.append("%s — klingt in Kapitel %d mit (`klingt=` von THEMA %d; das Kapitel nennt ihn: "
                             "„%s“), die Registerzeile nennt das Kapitel nicht: „%s“"
                             % (_kontakt_name(k), n, n, _kurz(satz, 90), _kurz(z, 80)))
    if not _P5_KLINGT_RE.search(z):
        return
    leer = sorted(n for n in _p5_klingt_nummern(z) if n in kap_txt and n not in aspekte_nr.get(k, set())
                  and not _p5_kontakt_satz(k, kap_txt[n]))
    if leer:
        p.pruefen.append("%s — die Registerzeile nennt %s, aber dort steht kein Satz mit %s und %s "
                         "(und THEMA %s führt ihn nicht unter `aspekte=`): „%s“"
                         % (_kontakt_name(k), ", ".join("Kapitel %d" % n for n in leer),
                            ANZEIGE.get(k[0], k[0]), ANZEIGE.get(k[2], k[2]),
                            ", ".join(str(n) for n in leer), _kurz(z, 80)))


def _p5_mitlaufendes(p, chapters, themen, txt, events, chart_data_pfad, events_pfad,
                     sprache_analyse="de"):
    """P5 im Transit (2026-09-19, W43): das Register `Mitlaufendes` gegen die
    Kontakte, die dort stehen muessen — jeder primaere Wirkorb-Kontakt im Fenster,
    der kein Thema FUEHRT (Transit-Modul, Struktur 5: „auch der, der in einem
    Kapitel mitklingt … dann nennt die Zeile zusätzlich das Kapitel").
    Soll-Menge mit events.json aus `build.kontakt_heimat()` (dieselbe Menge wie die
    Heimat-Probe in Schritt 1); ohne events.json aus der chart_data: die Zeilen
    des Blocks TRANSIT-RECHENSCHAFT (sicher im Register) und die `aspekte=`-Kontakte
    der Themenliste (ob primaer, sagt erst events.json — dort nur PRUEFEN)."""
    p.einheit = "Kontakte"
    reg = [ch for ch in chapters if _ist_kicker(ch, "Mitlaufendes")]
    if not reg:
        alt = [ch for ch in chapters if _ist_kicker(ch, "Rechenschaft")]
        if alt:
            p.pruefen.append("Das Register heißt „%s“ — im Transit seit 2026-09-14 "
                             "„Mitlaufendes“ (Transit-Modul, Struktur 5); geprüft wird es "
                             "trotzdem" % alt[0]["kicker"])
            reg = alt
    if not reg:
        (p.fehler if sprache_analyse == "de" else p.pruefen).append(
            "kein Kapitel mit Kicker „Mitlaufendes“ — das Register des Transits "
            "fehlt (Transit-Modul, Struktur 5: jeder Wirkorb-Kontakt an einem "
            "primären Ziel, der kein Thema führt, bekommt dort eine Zeile)")
        return p.abschluss()
    zeilen = _register_eintraege(reg[0])
    if not zeilen:
        return p.aussagelos("Kapitel „Mitlaufendes“ ohne Zeilen")
    if not themen:
        return p.aussagelos("keine THEMA-Zeile in der chart_data — führende Kontakte nicht "
                            "bestimmbar")
    fuehrend, mitklingend = {}, {}
    for th in themen:
        kf = _kontakte_in(th.get("fuehrt_roh"))
        if kf:
            fuehrend[kf[0]] = th["nr"]
        for k in _kontakte_in(_thema_feld(th.get("roh"), "aspekte")):
            if k not in fuehrend:
                mitklingend.setdefault(k, th["nr"])
    # 2026-10-13 (Strang 3): `klingt=`-Kontakte je THEMA, `aspekte=` je THEMA (alle
    # Themen, nicht nur das erste) und der Lesetext je Kapitel — fuer die
    # Kapitelangabe der klingt=-Kontakte und fuer leere Angaben (_p5_klingt_transit).
    klingend, aspekte_nr = {}, {}
    for th in themen:
        for k in _kontakte_in(_thema_feld(th.get("roh"), "klingt")):
            if k not in fuehrend and k not in mitklingend:
                klingend.setdefault(k, th["nr"])
        for k in _kontakte_in(_thema_feld(th.get("roh"), "aspekte")):
            aspekte_nr.setdefault(k, set()).add(th["nr"])
    kap_txt = _p5_kapitel_texte(chapters)
    sicher, quelle = set(), ""
    if events is not None and chart_data_pfad and events_pfad:
        try:
            kh = build.kontakt_heimat(chart_data_pfad, events_pfad)
            sicher = {(kanon(t), a, kanon(z)) for t, a, z in kh["soll_keys"]}
            quelle = "build.kontakt_heimat()"
        except Exception as e:      # Fassung von build ohne soll_keys o. ae.
            p.hinweise.append("build.kontakt_heimat() nicht nutzbar (%s: %s) — Soll-Menge aus "
                              "events.json selbst gefiltert (primär, kein Spiegel, Wirkorb im "
                              "Fenster)" % (type(e).__name__, _kurz(str(e), 80)))
    if events is not None and not quelle:
        for e in events.get("events", []):
            if e.get("spiegel") or not e.get("primaer"):
                continue
            wf = e.get("wirkorb_im_fenster")
            if wf is None:
                wf = bool(e.get("exakt_im_fenster")) or (
                    any(q > 0 for q in (e.get("quartale") or []))
                    and (e.get("min_orb_grad") is not None)
                    and e["min_orb_grad"] <= (events.get("orb_wirk") or 1.5))
            if wf:
                sicher.add((kanon(e["transit"]), e["aspekt"], kanon(e["ziel"])))
        quelle = "events.json"
    unsicher = set()
    if events is None:
        tr = _tr_block(txt)
        sicher = set(_kontakte_in(tr))
        unsicher = set(mitklingend) - sicher
        p.hinweise.append("ohne events.json: Soll-Menge aus der chart_data — %d Kontakte aus "
                          "TRANSIT-RECHENSCHAFT (müssen ins Register), %d mitklingende aus "
                          "`aspekte=` (nur PRÜFEN: ob primär, sagt erst events.json)"
                          % (len(sicher), len(unsicher)))
        if not tr:
            p.hinweise.append("kein Block TRANSIT-RECHENSCHAFT in der chart_data "
                              "(build.transit_rechenschaft_block())")
    _mitklingend_ohne_zeile = []
    for k in sorted(sicher | unsicher):
        if k in fuehrend:
            continue
        p.geprueft += 1
        z = _registerzeile(k, zeilen)
        if not z:
            if k in sicher and k in mitklingend:
                # SAMMELZEILE (2026-09-22, Klasse-2-Punkt 4): Der Kontakt klingt
                # nachweislich in einem Kapitel mit - die Probe weiss also, wo er
                # gedeutet ist, und nur die Registerzeile fehlt. Das ist EIN
                # Befund ueber die Registerfuehrung, nicht n Befunde ueber n
                # Kontakte; 29 Einzelzeilen in einem Lauf haben die echten
                # Meldungen zugedeckt.
                _mitklingend_ohne_zeile.append((k, mitklingend[k]))
            elif k in sicher:
                # englische Fassung: Namen und Aspektwoerter sind uebersetzt, eine
                # nicht gefundene Zeile kann an der Schreibweise liegen — PRUEFEN.
                (p.fehler if sprache_analyse == "de" else p.pruefen).append(
                    "%s — primärer Wirkorb-Kontakt im Fenster, führt kein Thema, "
                    "und keine Zeile im Kapitel „%s“ nennt ihn (Transiter und Ziel)"
                    % (_kontakt_name(k), reg[0]["kicker"]))
            else:
                p.pruefen.append("%s — klingt mit in Kapitel %d, keine Registerzeile; ohne "
                                 "events.json nicht entscheidbar, ob das Ziel primär ist — "
                                 "wenn ja, fehlt die Zeile" % (_kontakt_name(k), mitklingend[k]))
        elif k in mitklingend and not re.search(r"(?:Kapitel|Chapter)\s+%d(?!\d)" % mitklingend[k], z):  # 2026-09-22: englisches „Chapter" (W57)
            p.pruefen.append("%s — die Registerzeile nennt das Kapitel %d nicht, in dem der "
                             "Kontakt mitklingt (Transit-Modul, Struktur 5): „%s“"
                             % (_kontakt_name(k), mitklingend[k], _kurz(z, 80)))
        elif sprache_analyse == "de":
            _p5_klingt_transit(p, k, z, klingend, aspekte_nr, kap_txt)
    if _mitklingend_ohne_zeile:
        _liste = ", ".join("%s (Kap. %d)" % (_kontakt_name(k), nr)
                           for k, nr in sorted(_mitklingend_ohne_zeile,
                                               key=lambda x: x[1]))
        (p.fehler if sprache_analyse == "de" else p.pruefen).append(
            "%d primäre Wirkorb-Kontakte klingen in einem Kapitel mit, haben aber "
            "keine Zeile im Kapitel „%s“ (Transit-Modul, Struktur 5: die Zeile "
            "nennt zusätzlich das Kapitel) — %s"
            % (len(_mitklingend_ohne_zeile), reg[0]["kicker"], _kurz(_liste, 400)))
    for k, nr in sorted(fuehrend.items(), key=lambda x: x[1]):
        z = _registerzeile(k, zeilen)
        if z:
            p.pruefen.append("%s führt Thema %d und hat trotzdem eine Registerzeile: „%s“"
                             % (_kontakt_name(k), nr, _kurz(z, 80)))
    if p.geprueft == 0 and not p.fehler and not p.pruefen:
        return p.aussagelos("keine Kontakte für das Register gefunden (%s)"
                            % (quelle or "chart_data ohne TRANSIT-RECHENSCHAFT und ohne "
                               "mitklingende Kontakte"))
    return p.abschluss()

def _p6_leitsatz(chapters, chart_data_pfad, themen):
    p = _Probe("P6", "Leitsatz und Leitachse")
    p.einheit = "Prüfungen"
    try:
        deck = build.lies_deckblatt(chart_data_pfad)
        leitsatz = _ws(deck.get("LEITSATZ"))
    except Exception as e:      # DeckblattError, fehlender Block
        leitsatz = None
        p.fehler.append("@@DECKBLATT nicht lesbar: %s" % _kurz(str(e), 120))
    schluss = [ch for ch in chapters if _ist_kicker(ch, "Schlusswort")]
    if leitsatz:
        p.geprueft += 1
        if not schluss:
            p.fehler.append("kein Kapitel mit Kicker „Schlusswort“ — Leitsatz nicht verankert")
        else:
            text = _ws(" ".join(b["text"] for b in schluss[0]["blocks"] if b.get("type") != "subhead"))
            def woerter(s):
                return [w for w in re.findall(r"[\wäöüÄÖÜß]+", s.casefold())]
            if leitsatz.casefold() in text.casefold():
                pass
            else:
                lw, tw = woerter(leitsatz), woerter(text)
                # laengste gemeinsame Teilfolge (in Reihenfolge), vier Fuenftel noetig
                i = j = 0
                # gierig ist hier zu schwach; echte LCS ueber DP
                n, m = len(lw), len(tw)
                prev = [0] * (m + 1)
                for a in lw:
                    cur = [0] * (m + 1)
                    for k in range(1, m + 1):
                        cur[k] = prev[k - 1] + 1 if a == tw[k - 1] else max(prev[k], cur[k - 1])
                    prev = cur
                anteil = prev[m] / float(n) if n else 0.0
                if anteil >= 0.8:
                    p.hinweise.append("Leitsatz im Schlusswort verankert (Wortfolge %d %%)" % round(anteil * 100))
                else:
                    p.fehler.append("Leitsatz nicht im Schlusswort: „%s“ (Wortfolge nur %d %%)"
                                    % (_kurz(leitsatz, 90), round(anteil * 100)))
    if not themen:
        p.pruefen.append("keine THEMA-Zeile — leitachse=ja nicht prüfbar")
    else:
        p.geprueft += 1
        n = sum(1 for t in themen if t["leitachse"])
        if n != 1:
            p.fehler.append("leitachse=ja steht bei %d Themen, verlangt ist genau eines%s"
                            % (n, " (" + ", ".join("THEMA %d" % t["nr"] for t in themen if t["leitachse"]) + ")" if n else ""))
    if p.geprueft == 0 and not p.fehler:
        return p.aussagelos("weder Leitsatz noch Themenliste lesbar")
    return p.abschluss()

# Wortlisten fuer P8 — Quellen im Kommentar; alles nur PRUEFEN.
# Dritte: Innere Arbeit, Prinzip 13 / Dritte-Probe (Nr. 8): "dein Partner", "deine
# Mutter", "dein Vater", "deine Kinder", "dein Chef" — hier mit Beugung und den
# naechstliegenden Formen (Partnerin, Eltern, Kind, Chefin).
DRITTE_RE = re.compile(r"(?<![\wäöüß])dein(?:e|em|er|es|en)?\s+"
                       r"(Partner(?:in|s)?|Mutter|Vater(?:s)?|Eltern|Kind(?:er|es|ern)?|Chef(?:in|s)?)"
                       r"(?![\wäöüß])", re.I)
# Vergangenheits-Indikativ: Innere Arbeit, Prinzip 5 und Guardrail ("du hast frueh
# gelernt, dass") sowie Wortscan Nr. 9, Liste "Zeit" ("damals hast du", "damals ist").
VERGANGENHEIT = ("du hast früh gelernt", "du hast gelernt", "hast du gelernt", "damals hast du",
                 "damals ist", "damals war", "als Kind hast du", "als Kind warst du",
                 "du bist aufgewachsen", "bist du aufgewachsen", "du wurdest", "dir wurde",
                 "in deiner Kindheit", "du hast erlebt", "du hast erfahren")
# Englische Fassung der drei Listen (Sprachfassung, 2026-09-16d): Uebersetzung der
# deutschen Eintraege, keine eigene Entscheidung — Chris kann sie hier nachziehen.
VERGANGENHEIT_EN = ("you learned early", "you learned", "you have learned", "back then you",
                    "at that time you", "as a child you", "you grew up", "in your childhood",
                    "you experienced", "you have experienced", "you were raised",
                    "you were brought up")
DRITTE_EN_RE = re.compile(r"(?<![\w])your\s+(partner|mother|father|parents|child(?:ren)?|"
                          r"boss|husband|wife)(?![\w])", re.I)
VERGANGENHEIT_RE = re.compile("|".join(r"(?<![\wäöüß])" + re.escape(w) + r"(?![\wäöüß])"
                                       for w in VERGANGENHEIT + VERGANGENHEIT_EN), re.I)
# Aspekt-Wertung: Klartext-Modul, Abschnitt Pruefung, Stand 2026-09-14 — "voll" und
# "einseitig" nur als Wortpaar oder unmittelbar bei einer Gradangabe. `restyle.VERBOTEN`
# fuehrt "einseitig" noch als nacktes Wort (Stand vor dem 14.09.); es wird hier in
# der Wertungs-Form gesucht, nicht als Wort.
WERTUNG_RE = re.compile(r"\d{1,3}°\s*\d{1,2}[′']\s*,?\s*(?:voll|einseitig|full|one-sided)\b"
                        r"|,?\s*(?:voll|einseitig|full|one-sided)\s*,?\s*\d{1,3}°\s*\d{1,2}[′']"
                        r"|\bvoll\s*/\s*einseitig\b|\bfull\s*/\s*one-sided\b")
GRADZAHL_RE = re.compile(r"\d{1,3}\s*°|\d{1,3}\s*[′']|(?<![\wäöüß])\d{1,3}\s*Grad(?![\wäöüß])"
                         r"|(?<![\w])\d{1,3}\s*degrees?(?![\w])")
HAUSZIFFER_RE = re.compile(r"(?<![\wäöüß])\d{1,2}\.\s*Haus(?![\wäöüß])"
                           r"|(?<![\wäöüß])H[äa]us(?:es|er|ern)?\s+\d{1,2}(?![\wäöüß])"
                           r"|(?<![\w])\d{1,2}(?:st|nd|rd|th)\s+house(?![\w])"
                           r"|(?<![\w])house\s+\d{1,2}(?![\w])", re.I)
# englische Fachbegriffe: Uebersetzung der Klartext-Verbotsliste (restyle.VERBOTEN)
FACHBEGRIFFE_EN = ["orb", "minute of arc", "minutes of arc", "arc minute", "arcminute",
                   "degrees apart", "minor aspect", "domicile", "detriment", "exaltation",
                   "cazimi", "apex", "dispositor", "final dispositor", "chart ruler",
                   "T-square"]
FACHBEGRIFF_EN_RE = re.compile("|".join(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])"
                                        for w in FACHBEGRIFFE_EN), re.I)

def _fachbegriff_re():
    woerter = [w for w in VERBOTEN_FACHBEGRIFFE if w not in ("°", "′", "einseitig", "voll")]
    return re.compile("|".join(r"(?<![\wäöüÄÖÜß])" + re.escape(w) + r"(?![\wäöüÄÖÜß])" for w in woerter))
FACHBEGRIFF_RE = _fachbegriff_re()

def _p8_wortlisten(chapters):
    p = _Probe("P8", "Wortlisten")
    p.einheit = "Absätze"
    listen = (("Dritte", DRITTE_RE), ("Dritte", DRITTE_EN_RE),
              ("Vergangenheits-Indikativ", VERGANGENHEIT_RE),
              ("Fachbegriff", FACHBEGRIFF_RE), ("Fachbegriff", FACHBEGRIFF_EN_RE),
              ("Aspekt-Wertung", WERTUNG_RE),
              ("Gradzahl", GRADZAHL_RE), ("Hausnummer in Ziffern", HAUSZIFFER_RE))
    for ch in chapters:
        if _ist_kicker(ch, "Auftakt", "Rechenschaft"):
            continue
        bewegung = "—"
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bewegung = _ws(b["text"])
                continue
            p.geprueft += 1
            t = b["text"]
            for name, rx in listen:
                gesehen = set()
                for m in rx.finditer(t):
                    satz = _satz_mit(t, m.start())
                    key = (name, satz)
                    if key in gesehen:
                        continue
                    # Der Nichtwissens-Satz der Wurzel-Bewegung ("Where you learned
                    # that I do not know") ist kein Vergangenheits-Indikativ — er ist
                    # sein Gegenteil (Innere Arbeit, Prinzip 5).
                    if name == "Vergangenheits-Indikativ" and NICHTWISSEN_RE.search(satz):
                        continue
                    gesehen.add(key)
                    p.pruefen.append("%s · %s · %s: „%s“ — Treffer „%s“"
                                     % (name, _bezeichnung(ch), bewegung, _kurz(satz, 140), m.group(0)))
    if p.geprueft == 0:
        return p.aussagelos("kein Fließtext-Absatz gefunden")
    return p.abschluss()

# Ein Transit-Kontakt im Beleg: T-<Faktor> <Aspekt> R-<Faktor> — exakt <Daten>.
_TRANSIT_KONTAKT_RE = re.compile(r"(?<![\w\u00e4\u00f6\u00fc\u00df])[TR]-\s*[A-Z\u00c4\u00d6\u00dc]")
_TRANSIT_EXAKT_RE = re.compile(r"(?:exakt|exact)\w*\s*:?\s*\d{1,2}\.\d{1,2}\.\d{4}", re.I)

NICHTWISSEN_RE = re.compile(r"wei(?:ß|ss) ich nicht|(?:steht|stehen) in keinem Horoskop|in keinem Horoskop"
                            r"|I do not know|I don't know|no chart contains|in no chart"
                            r"|no horoscope contains|in no horoscope"
                            # 2026-09-22 (W57-Nachzug, erster englischer Transit): Der
                            # Nichtwissens-Satz wird englisch auch als Grenze des Charts
                            # gesagt („a chart cannot", „is yours to say") und nicht nur
                            # als Wissenslücke des Sprechers. P9 meldet nur das FEHLEN
                            # des Satzes — eine zu enge Liste erzeugt hier Fehlalarm,
                            # keine uebersehene Aussage.
                            r"|(?:a|the|no) (?:chart|horoscope) (?:can|cannot|can't|does not|doesn't|won't)"
                            r"|(?:can|could)not be read (?:from|out of) (?:a|the) (?:chart|horoscope)"
                            r"|is yours to say|yours to answer|not for (?:a|the) (?:chart|horoscope) to"
                            r"|(?:a|the) (?:chart|horoscope) has no", re.I)
# englisch eng gefasst (Kapitel-Bezug), damit "gets discarded" in normaler Verwendung
# nicht mitzaehlt — dieselbe Fehlalarm-Klasse wie "verwerf" (Klasse-2-Liste 16.09.c, Nr. 6)
# DEUTSCH EBENSO ENG GEFASST (geaendert 2026-09-17, Klasse-2-Entscheidungslauf,
# Wiederholungstaeter). "verwerf|verwirf" traf jede normale Verwendung — vor
# allem den Klartext-Standardsatz selbst und jedes "einen Gedanken verwerfen".
# Gesucht ist die ERLAUBNIS, nicht das Verb: ein Modalausdruck davor oder ein
# ausdruecklicher Kapitelbezug. Dieselbe Enge, die die englische Seite am
# 2026-09-16 bekommen hat.
VERWERF_RE = re.compile(r"(?:darfst|kannst|darf|kann)\s+(?:du\s+)?"
                        r"(?:[\wäöüÄÖÜß]+\s+){0,3}verwerfen"
                        r"|verwirf\s+(?:es|ihn|sie|das|dieses|jenes)"
                        r"|(?:Kapitel|Band|Abschnitt)[^.]{0,40}verwerfen"
                        r"|discard (?:the|this|it)|free to discard|may discard"
                        r"|put (?:the|this) chapter aside|set (?:the|this) chapter aside"
                        r"|skip (?:the|this) chapter"
                        # 2026-09-22 (W57-Nachzug): die vier Wortlaute, die die
                        # Innere Arbeit, Pruefung 2, fuer die englische Fassung
                        # nennt — vorher las die Probe nur die ersten sieben.
                        r"|do(?:es)? not (?:recognise|recognize) yourself"
                        r"|do not apply to (?:everyone|every|all)"
                        r"|does not apply to (?:everyone|every|all)"
                        r"|leave it where it is"
                        r"|if this does ?n(?:o|')t fit", re.I)

# ---------------------------------------------------------------------------
# P10 — Wortscan der Inneren Arbeit (Probe 9 des Moduls), seit 2026-09-17 hier
# ---------------------------------------------------------------------------
# Die Ausnahmen sind KEINE neuen Setzungen, sondern die im Modul schon
# dokumentierten, plus die zwei Fehlalarm-Klassen, die dort offen standen:
#   tiefst…   + "Punkt des/im Horoskops|Bildes|Charts"  -> Fachname des IC
#              (Modul seit 2026-09-14, dort als lauffaehige Vorschau notiert)
#   dichtest… + "verschaltet" / "am dichtesten verschaltet"
#              (Modul seit 2026-09-15, gleiche Klasse)
#   Stoerung  nicht in "Zerstoerung"/"zerstoerung" (Klasse-2-Liste 16.09.d Nr. 4)
#   "solltest du" nicht im Lassen-Satz, den Prinzip 12 gerade verlangt
#              (Klasse-2-Liste 16.09.e Nr. 6, acht Fehlalarme in einem Lauf)
# Der SUPERLATIV-DECKEL steht seit dem 2026-09-17 auf DREI je Dokument, und der
# Auftakt zaehlt nicht mit (Chris-Entscheidung: "superlative sind auch nicht so
# schlimm, uebertreib es nicht mit der regel"). Vorher: genau EINER im ganzen
# Dokument — und die Pflichtformulierung des Auftakts ("ausdruecklich als die
# staerkste", Typmodul) verbrauchte ihn, weshalb der Konflikt in zwei
# Laufabschnitten als Befund stand.
# 2026-09-19 (W29, Chris-Entscheidung Frage 9 = 1): Der Deckel gilt NUR fuer die
# Treffer dieser Wortliste — andere Superlative ("die meisten", "am weitesten",
# "hoechsten") zaehlen nicht mit; so rechnet `_p10_wortscan()` seit jeher
# (`supertreffer` sammelt allein SUPERLATIV_RE). Die IC-Fuegung gilt auch in der
# KURZFORM: "zum tiefsten Punkt" (ohne "des Horoskops") ist derselbe Fachname, wie
# ihn ein Text beim zweiten Vorkommen schreibt (G12-17 Nr. 10, G12-18 Nr. 9). Ein
# Treffer bleibt "tiefst… Punkt" mit einem ANDEREN Bezug ("der tiefste Punkt
# deines Lebens"): Ausgenommen ist "tiefst… Punkt" ohne Genitiv-/im-Anschluss oder
# mit Horoskop/Bild/Chart/Radix.
# 2026-09-22 (Chris-Entscheidung): Der Deckel SKALIERT mit der Kapitelzahl —
# drei je Dokument war fuer ein Geburtshoroskop mit elf gedeuteten Kapiteln
# unerreichbar, und dreimal stand genau das als Befund (17.09.b Nr. 5,
# 18.09.c Nr. 15, 22.09.b Nr. 11): dreizehn sachlich RICHTIGE Rangsaetze gegen
# einen Deckel von drei. Gezaehlt werden die gedeuteten Kapitel — die mit
# Signatur; Auftakt, Teiler, Rechenschafts- und Sammelkapitel und Schlusswort
# tragen keine und zaehlen deshalb weiter nicht mit. DREI bleibt die
# Untergrenze, damit ein kurzes Dokument nicht schaerfer geprueft wird als
# frueher.
SUPERLATIV_DECKEL = 3


def _superlativ_deckel(chapters) -> int:
    """Wie viele Superlative dieses Dokument tragen darf: einer je gedeutetem
    Kapitel, mindestens SUPERLATIV_DECKEL."""
    gedeutet = sum(1 for ch in chapters
                   if (ch.get("signatur") or "").strip())
    return max(SUPERLATIV_DECKEL, gedeutet)


SUPERLATIV_RE = re.compile(
    r"tiefst\w*\b(?!\s+Punkt\b(?!\s+(?:des|der|deines|deiner|im|in)\s)"
    r"|\s+Punkt\s+(?:des|im|deines|in\s+deinem)\s+(?:Horoskop|Bild|Chart|Radix))"
    r"|dichtest\w*\b(?!\s+verschaltet)|\bam\s+dichtesten\b(?!\s+verschaltet)"
    r"|prägendst\w*|markantest\w*|stärkst\w*|größt\w*|wichtigst\w*"
    r"|zentralst\w*|entscheidendst\w*", re.I)
KLINISCH_RE = re.compile(
    r"(?<!Zer)(?<!zer)[Ss]törung\w*|Trauma\w*|traumatisiert\w*|Symptom\w*"
    r"|Diagnose\w*|Syndrom\w*|pathologisch\w*|dysfunktional\w*|neurotisch\w*"
    r"|narzisstisch\w*|Depression\w*|Bindungsangst\w*")
BESTAETIGUNG_RE = re.compile(
    r"es ist kein Zufall|nicht umsonst|darin lebst du|das passt genau zu"
    r"|deshalb bist du|solltest du|musst du lernen|arbeite an dir"
    r"|dein Potenzial|das Beste aus dir", re.I)
# VERNEINUNG UNMITTELBAR VOR DEM KLINISCHEN WORT ist kein Treffer (neu
# 2026-09-18). Gesucht ist das Wort in BEHAUPTENDER Verwendung. Der Abstand ist
# bewusst kurz (24 Zeichen), damit eine Verneinung irgendwo im Satz nicht die
# ganze Zeile freikauft.
KLINISCH_VERNEINT_RE = re.compile(
    r"(?:kein|keine|keiner|keinem|keinen|nicht|nie|niemals|weder|statt)"
    r"[^.!?]{0,24}$", re.I)
# Der Lassen-Satz von Prinzip 12 ist der Grund, warum "solltest du" ueberhaupt
# vorkommt. Er ist kein Treffer.
LASSEN_RE = re.compile(r"\bnicht\b|\blassen\b|\bunterlassen\b|\bweglassen\b"
                       r"|\bsein\s+lassen\b|\bzu\s+lassen\b|\blässt\b", re.I)
FRIST_RE = re.compile(
    r"du hast noch|spätestens|bis dahin musst|damals hast du|damals ist"
    r"|wird sich entscheiden|steht bevor", re.I)

# ---------------------------------------------------------------------------
# Zeitform-Probe der Widerstands-Bewegung (2026-09-19, W4; Chris-Entscheidung
# Frage 7 = 1). Die Bewegung „Der Teil von dir, der das nicht aufgeben will"
# schrieb in acht von zehn Laeufen Vergangenheit im Indikativ („Er hat dich
# geschützt", „It has spared you", „Das war einmal so") — das Argument aus der
# GESCHICHTE, das Prinzip 4 bis dahin selbst vorgab. Gesucht wird nur in dieser
# Bewegung, und nur die finite Vergangenheit: haben + Partizip II im selben
# Satzteil, sein + Partizip der Veraenderungsverben, Praeteritum der Hilfs- und
# Modalverben und einiger Verben, mit denen das Argument erzaehlt wird. Nicht
# gemeldet: Konjunktiv II (haette, waere, wuerde, koennte — Umlaut), „sollte" und
# „wollte" (meist Konjunktiv), Zustandspassiv („du bist so gebaut"), „zu" +
# Infinitiv („hat nichts zu verlieren"), ein gebeugtes Adjektiv mitten im Satzteil
# („hat einen verlässlichen Instinkt" — das Partizip steht am Ende des Satzteils),
# Saetze, die P8 schon meldet. Nur PRUEFEN.
# ---------------------------------------------------------------------------
WIDERSTAND_RE = re.compile(r"^(?:Der Teil von dir, der|The part of you that)", re.I)
_PARTIZIP_RE = re.compile(
    r"^(?:(?:auf|ab|an|aus|bei|ein|mit|nach|vor|weg|zu|zurück|zurueck|los|fest|hin|her|"
    r"dar|um|durch|über|ueber|unter|wieder|heraus|hinaus|voran|zusammen|hoch|frei|fort)?"
    r"ge[a-zäöüß]{2,}(?:t|en)|[a-zäöüß]{2,}iert|(?:be|er|ver|zer|ent|emp|miss)[a-zäöüß]{2,}(?:t|en))$")
_KEIN_PARTIZIP = {"gegen", "genau", "gerade", "gern", "gerne", "genug", "gemeinsam", "gesamt",
                  "gestern", "gelegentlich", "geradezu", "gewiss", "gewöhnlich", "gesund",
                  "geheim", "gering", "gerecht", "geduldig", "gefährlich", "besonders",
                  "bereits", "bereit", "bevor", "entweder", "eben", "ebenso", "vergeblich",
                  "vielleicht", "verschieden", "verschiedenen", "bekannt", "entgegen",
                  "bestimmt", "berechtigt", "bequem", "bescheiden", "ernst", "erst"}
_HABEN_RE = re.compile(r"(?<![\wäöüß])(?:hat|hast|habe|haben|habt)(?![\wäöüß])", re.I)
_SEIN_PARTIZIP = (r"(?:gewesen|geworden|worden|gekommen|gegangen|geblieben|entstanden|"
                  r"aufgewachsen|gewachsen|passiert|geschehen|gelungen|gescheitert|gefolgt)")
_SEIN_PERFEKT_RE = re.compile(
    r"(?<![\wäöüß])(?:ist|bist|sind|seid)(?![\wäöüß])(?:\s+[\wäöüß]+){0,6}?\s+"
    + _SEIN_PARTIZIP + r"(?![\wäöüß])"
    r"|(?<![\wäöüß])" + _SEIN_PARTIZIP + r"\s+(?:ist|bist|sind|seid)(?![\wäöüß])", re.I)
_PRAETERITUM_RE = re.compile(
    r"(?<![\wäöüß])(?:war|warst|waren|wart|hatte|hattest|hatten|hattet|wurde|wurdest|wurden|"
    r"wurdet|konnte|konntest|konnten|musste|musstest|mussten|durfte|durftest|durften|gab|"
    r"gaben|ging|gingen|kam|kamen|blieb|blieben|hielt|hielten|trug|trugen|half|halfen|"
    r"schützte|schützten|bewahrte|bewahrten|lernte|lerntest|lernten|funktionierte|"
    r"funktionierten|sorgte|sorgten|brachte|brachten|rettete|retteten|ersparte|ersparten|"
    r"sicherte|sicherten|verhinderte|verhinderten)(?![\wäöüß])", re.I)
# „-ed" ohne die Woerter auf „-eed" (need, proceed, exceed); „have to" ist kein Perfekt.
_EN_PERFEKT_RE = re.compile(
    r"\b(?:has|have|'ve)(?!\s+to\b)\s+(?:\w+\s+){0,2}?(?:been|(?!\w*eed\b)\w{2,}ed|kept|made|"
    r"done|given|taken|held|brought|taught|got|gotten|known|shown|seen|won|lost|built|left|"
    r"felt|found|paid|meant|become|grown|come|gone)\b", re.I)
_EN_PRAETERITUM_RE = re.compile(
    r"\b(?:was|were|had|did|used to)\b"
    r"|\b(?:it|this|that|he|she|they|you|which|who)(?:\s+\w+ly)?\s+(?:(?!\w*eed\b)\w{2,}ed|"
    r"made|kept|gave|held|brought|taught|got|felt|built|found|paid|meant|went|came|took|knew|"
    r"saw|became|grew|won|lost)\b"
    r"|\b(?:this|that|the|your)\s+\w+\s+(?:made|kept|gave|held|brought|taught|spared|"
    r"protected|carried|saved|served|helped|worked)\b", re.I)

def _zeitform_treffer(satz, sprache_analyse="de"):
    """Der erste Treffer finiter Vergangenheit in einem Satz der Widerstands-
    Bewegung, oder None (s. Kommentarblock oben). Deutsch und Englisch getrennt:
    „was", „war", „hat" sind in der jeweils anderen Sprache gewoehnliche Woerter."""
    if sprache_analyse == "en":
        m = _EN_PERFEKT_RE.search(satz) or _EN_PRAETERITUM_RE.search(satz)
        return m.group(0) if m else None
    m = _PRAETERITUM_RE.search(satz) or _SEIN_PERFEKT_RE.search(satz)
    if m:
        return m.group(0)
    for teil in re.split(r"[,;:–—()]|\s(?:und|oder|aber|sondern|denn)\s", satz):
        if not _HABEN_RE.search(teil):
            continue
        woerter = re.findall(r"[\wäöüß]+", teil)
        # Das Partizip steht am Ende des Satzteils („Er hat dich geschützt.") oder
        # vor dem Hilfsverb am Ende („…, weil er dich geschützt hat"). Ein gebeugtes
        # Adjektiv mitten im Satzteil („hat einen verlässlichen Instinkt") ist keins.
        i = len(woerter) - (2 if len(woerter) >= 2 and _HABEN_RE.fullmatch(woerter[-1]) else 1)
        if i < 0:
            continue
        w = woerter[i]
        if w in _KEIN_PARTIZIP or not _PARTIZIP_RE.match(w):
            continue
        if i and woerter[i - 1].lower() == "zu":
            continue
        return "%s … %s" % (_HABEN_RE.search(teil).group(0), w)
    return None

def _p10_wortscan(chapters, sprache_analyse="de"):
    p = _Probe("P10", "Wortscan (Innere Arbeit, Probe 9)")
    p.einheit = "Absätze"
    supertreffer = []
    listen = (("Klinisches", KLINISCH_RE), ("Bestätigung/Optimierung", BESTAETIGUNG_RE),
              ("Zeit als Frist", FRIST_RE))
    for ch in chapters:
        bewegung = "—"
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bewegung = _ws(b["text"])
                continue
            if b.get("type") != "p":
                continue
            p.geprueft += 1
            t = b["text"]
            for m in SUPERLATIV_RE.finditer(t):
                if _ist_kicker(ch, "Auftakt"):
                    continue
                supertreffer.append((ch, bewegung, m.group(0),
                                     _satz_mit(t, m.start())))
            # 2026-09-19 (W4): Zeitform der Widerstands-Bewegung.
            if WIDERSTAND_RE.match(bewegung):
                for satz in _saetze(t):
                    if VERGANGENHEIT_RE.search(satz) or NICHTWISSEN_RE.search(satz):
                        continue            # meldet P8 bzw. ist der Nichtwissens-Satz
                    w = _zeitform_treffer(satz, sprache_analyse)
                    if w:
                        p.pruefen.append(
                            "Zeitform (Widerstand) · %s · %s: „%s“ — Vergangenheit im "
                            "Indikativ („%s“); das Argument des Widerstands kommt aus der "
                            "Form, nicht aus der Geschichte (Innere Arbeit, Prinzip 4 und "
                            "Prüfung 4)" % (_bezeichnung(ch), bewegung, _kurz(satz, 140), w))
            for name, rx in listen:
                gesehen = set()
                for m in rx.finditer(t):
                    satz = _satz_mit(t, m.start())
                    if (name == "Bestätigung/Optimierung"
                            and m.group(0).lower().startswith("solltest")
                            and LASSEN_RE.search(satz or "")):
                        continue
                    if (name == "Klinisches"
                            and KLINISCH_VERNEINT_RE.search(t[:m.start()])):
                        continue
                    key = (name, satz, m.group(0))
                    if key in gesehen:
                        continue
                    gesehen.add(key)
                    p.pruefen.append("%s · %s · %s: „%s“ — Treffer „%s“"
                                     % (name, _bezeichnung(ch), bewegung,
                                        _kurz(satz, 140), m.group(0)))
    deckel = _superlativ_deckel(chapters)
    if len(supertreffer) > deckel:
        p.pruefen.append(
            "Superlative: %d Treffer, Deckel %d (einer je gedeutetem Kapitel, "
            "mindestens %d; Auftakt zählt nicht mit) — %s"
            % (len(supertreffer), deckel, SUPERLATIV_DECKEL,
               "; ".join("%s: „%s“" % (_bezeichnung(c), w)
                         for c, _bw, w, _sz in supertreffer)))
    if p.geprueft == 0:
        return p.aussagelos("kein Fließtext-Absatz gefunden")
    return p.abschluss()

def _p9_zwei_saetze(chapters, typ):
    p = _Probe("P9", "Zwei Sätze")
    p.einheit = "Kapitel"
    # (a) Nichtwissens-Satz je Wurzel-Bewegung
    wurzeln = set()
    if typ in WORTLAUTE:
        v = WORTLAUTE[typ]
        for wl in (v.values() if isinstance(v, dict) else [v]):
            w = wl[2]
            wurzeln.update(w if isinstance(w, tuple) else (w,))
    else:
        p.hinweise.append("Typ %s ohne Wortlaute — Nichtwissens-Satz nicht geprüft" % (typ or "unbekannt"))
    kapitel = [ch for ch in chapters if _hat_bewegungen(ch)]
    for ch in kapitel:
        if not wurzeln:
            break
        aktuell, text_wurzel, hat_wurzel = None, [], False
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                aktuell = _ws(b["text"])
                if aktuell in wurzeln:
                    hat_wurzel = True
                continue
            if aktuell in wurzeln:
                text_wurzel.append(b["text"])
        if hat_wurzel:
            p.geprueft += 1
            if not NICHTWISSEN_RE.search(" ".join(text_wurzel)):
                p.pruefen.append("%s · Wurzel-Bewegung ohne Nichtwissens-Satz („weiß ich nicht“ / "
                                 "„steht in keinem Horoskop“)" % _bezeichnung(ch))
    # (b) Verwerfungs-Erlaubnis nur im Auftakt und im ersten Themenkapitel
    erstes = kapitel[0] if kapitel else None
    for ch in chapters:
        if _ist_kicker(ch, "Auftakt") or ch is erstes:
            continue
        bewegung = "—"
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bewegung = _ws(b["text"])
                continue
            for m in VERWERF_RE.finditer(b["text"]):
                p.pruefen.append("Verwerfungs-Erlaubnis außerhalb des ersten Themenkapitels · %s · %s: „%s“"
                                 % (_bezeichnung(ch), bewegung, _kurz(_satz_mit(b["text"], m.start()), 140)))
                break
    if p.geprueft == 0 and not kapitel:
        return p.aussagelos("kein Kapitel mit Bewegungsfolge gefunden")
    return p.abschluss()

# ===========================================================================
# Neue Proben P11–P15 (Wartungslauf A, 2026-09-19)
#   P11 Zahlen-Deckung              U1 (a)     nur PRUEFEN
#   P12 Rang- und Einzigkeitswörter U1 (b)     nur PRUEFEN
#   P13 Text-Beleg-Deckung          U1 (c)     nur PRUEFEN
#   P14 Kopfblock                   W10, W43
#   P15 Ressourcen-Tiefe            W37        nur PRUEFEN
# Grundlage: Ursachenanalyse im Pruefbericht Transit Schritt 3+4 vom 18.09.b —
# 78 Inhaltsbefunde in zehn Laeufen, keiner von der Probe gefunden; die Klassen A
# (Rang- und Zaehlaussagen), C (Zeit- und Zahlenangaben ohne Quelle) und D
# (Beleg-Deckung) sind 44 davon. Chris-Entscheidungen: Frage 18 = 1 (U1),
# Frage 4 = 1 (Beleg-Deckung nach der Klartext-Regel). Die Proben pruefen, sie
# beurteilen nicht: Ein Treffer heisst „ansehen", nie „falsch".
# ===========================================================================

_MONATE = {"januar": 1, "jänner": 1, "jaenner": 1, "februar": 2, "märz": 3, "maerz": 3,
           "april": 4, "mai": 5, "juni": 6, "juli": 7, "august": 8, "september": 9,
           "oktober": 10, "november": 11, "dezember": 12}
_MONAT_RE = (r"(?:Januar|Jänner|Jaenner|Februar|März|Maerz|April|Mai|Juni|Juli|August|"
             r"September|Oktober|November|Dezember)")
_JAHR_RE = r"(?:19|20|21)\d\d"
_NICHT_TRENNEN_RE = re.compile(r"(?:%s|Haus|Hauses|Lebensjahr\w*|Jahrhundert\w*|Mal|Quartal\w*)\b"
                               % _MONAT_RE)
_ABKUERZUNG_RE = re.compile(r"(?:^|[\s(])(?:[zdhuaosB]|ca|bzw|vgl|etc|usw|Nr|evtl|ggf|bspw|inkl|"
                            r"sog|Abs|Dr|St)$")

def _saetze_pos(text):
    """[(anfang, ende, satz)] — wie `_saetze()`, trennt aber nicht hinter einer
    Ordinalzahl vor Monat/Haus/Lebensjahr („3. Mai", „im 12. Haus") und nicht
    hinter gaengigen Abkuerzungen („z. B."). Fuer die Proben P11–P15."""
    out, start = [], 0
    for m in re.finditer(r"([.!?…])([“”\"»«’)]*)(\s+)(?=[„\"»(A-ZÄÖÜ])", text):
        vorher = text[start:m.start(1)]
        if m.group(1) == ".":
            if re.search(r"(?:^|[\s(])\d{1,2}$", vorher) and _NICHT_TRENNEN_RE.match(text, m.end()):
                continue
            if _ABKUERZUNG_RE.search(vorher):
                continue
        out.append((start, m.end(2), text[start:m.end(2)]))
        start = m.end()
    if text[start:].strip():
        out.append((start, len(text), text[start:]))
    return out

def _fliesstext(chapters):
    """(Kapitel, Bewegung, Absatztext) fuer jeden Absatz- und Listenblock —
    Signatur und Beleg gehoeren nicht dazu (build.parse_analyse() fuehrt sie
    getrennt)."""
    for ch in chapters:
        bewegung = "—"
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bewegung = _ws(b["text"])
                continue
            yield ch, bewegung, b["text"]

def _satz_an(saetze, pos):
    for a, e, s in saetze:
        if a <= pos < e:
            return s
    return saetze[-1][2] if saetze else ""

# --- Zahlwoerter (Alter, „x von y") ----------------------------------------
_EINER_W = r"(?:ein|zwei|drei|vier|fünf|fuenf|sechs|sieben|acht|neun)"
_ZEHNER_W = r"(?:zwanzig|dreißig|dreissig|vierzig|fünfzig|fuenfzig|sechzig|siebzig|achtzig|neunzig)"
_ZAHLWORT = (r"(?:%sund%s|%s|zehn|elf|zwölf|zwoelf|dreizehn|vierzehn|fünfzehn|fuenfzehn|"
             r"sechzehn|siebzehn|achtzehn|neunzehn|zwei|drei|vier|fünf|fuenf|sechs|sieben|"
             r"acht|neun|hundert)" % (_EINER_W, _ZEHNER_W, _ZEHNER_W))
_ZAHL = r"(?:\d{1,3}|%s)" % _ZAHLWORT
_ORDWORT = (r"(?:(?:%sund)?%sst|hundertst|(?:drei|vier|fünf|fuenf|sech|sieb|acht|neun)zehnt|"
            r"erst|zweit|dritt|viert|fünft|fuenft|sechst|siebent|siebt|acht|neunt|zehnt|elft|"
            r"zwölft|zwoelft)(?:e|en|er|es|em)" % (_EINER_W, _ZEHNER_W))
_EINER_WERT = {"ein": 1, "eins": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "fuenf": 5,
               "sechs": 6, "sieben": 7, "acht": 8, "neun": 9}
_ZEHNER_WERT = {"zwanzig": 20, "dreißig": 30, "dreissig": 30, "vierzig": 40, "fünfzig": 50,
                "fuenfzig": 50, "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90}
_TEEN_WERT = {"zehn": 10, "elf": 11, "zwölf": 12, "zwoelf": 12, "dreizehn": 13, "vierzehn": 14,
              "fünfzehn": 15, "fuenfzehn": 15, "sechzehn": 16, "siebzehn": 17, "achtzehn": 18,
              "neunzehn": 19, "hundert": 100}

# ---------------------------------------------------------------------------
# Englische Sprachfassung, Zahl- und Zeitwoerter (2026-09-22, W57-Nachzug).
# P11 und P12 uebersprangen eine englische Analyse ganz; damit lief in der
# englischen Fassung KEINE Zahlenprobe. Die Tafeln unten spiegeln die deutschen
# Zeile fuer Zeile — gleiche Gruppennamen, gleiche Musterarten, gleiche
# Reihenfolge —, damit der Rumpf beider Proben unveraendert bleibt und nur die
# Tafel gewechselt wird. EA und Ultimativ bleiben aussen vor (Chris-Ansage
# 2026-09-22: werden vorerst nicht mehr gefahren).
_EINER_WERT_EN = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                  "six": 6, "seven": 7, "eight": 8, "nine": 9}
_ZEHNER_WERT_EN = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
                   "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_TEEN_WERT_EN = {"ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
                 "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
                 "nineteen": 19, "hundred": 100}
_ORD_WERT_EN = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
                "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11,
                "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15,
                "sixteenth": 16, "seventeenth": 17, "eighteenth": 18, "nineteenth": 19,
                "twentieth": 20}
_EINER_W_EN = r"(?:one|two|three|four|five|six|seven|eight|nine)"
_ZEHNER_W_EN = r"(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
# laengere Formen zuerst, damit "twenty-one" nicht als "twenty" endet
_ZAHLWORT_EN = (r"(?:%s[-\s]%s|%s|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
                r"seventeen|eighteen|nineteen|%s|hundred)"
                % (_ZEHNER_W_EN, _EINER_W_EN, _ZEHNER_W_EN, _EINER_W_EN))
_ZAHL_EN = r"(?:\d{1,3}|%s)" % _ZAHLWORT_EN

def _zahl_wert(w):
    """Grundzahl (Ziffern oder Wort bis 100) -> int oder None."""
    w = (w or "").casefold().strip()
    if w.isdigit():
        return int(w)
    for tafel in (_EINER_WERT, _TEEN_WERT, _ZEHNER_WERT,
                  _EINER_WERT_EN, _TEEN_WERT_EN, _ZEHNER_WERT_EN):
        if w in tafel:
            return tafel[w]
    m = re.fullmatch(r"(ein|zwei|drei|vier|fünf|fuenf|sechs|sieben|acht|neun)und(\w+)", w)
    if m and m.group(2) in _ZEHNER_WERT:
        return _EINER_WERT[m.group(1)] + _ZEHNER_WERT[m.group(2)]
    # englisch: „twenty-one", „forty five" (2026-09-22)
    m = re.fullmatch(r"(twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[-\s](\w+)", w)
    if m and m.group(2) in _EINER_WERT_EN:
        return _ZEHNER_WERT_EN[m.group(1)] + _EINER_WERT_EN[m.group(2)]
    return None

def _ordinal_wert(w):
    """Ordnungszahl („dreizehnte", „13.") -> int oder None."""
    w = (w or "").casefold().strip().rstrip(".")
    if w.isdigit():
        return int(w)
    stamm = re.sub(r"(?:e|en|er|es|em)$", "", w)
    besonders = {"erst": 1, "dritt": 3, "siebt": 7, "siebent": 7, "acht": 8}
    if stamm in besonders:
        return besonders[stamm]
    if stamm.endswith("t") and _zahl_wert(stamm[:-1]):
        return _zahl_wert(stamm[:-1])
    if stamm.endswith("st") and _zahl_wert(stamm[:-2]):
        return _zahl_wert(stamm[:-2])
    return None

# --- P11 Zahlen-Deckung ------------------------------------------------------
_JAHRESZEIT_MONATE = {"frühjahr": (3, 4, 5), "frühling": (3, 4, 5), "sommer": (6, 7, 8),
                      "herbst": (9, 10, 11), "winter": (12, 1, 2), "anfang": (1, 2, 3, 4),
                      "beginn": (1, 2, 3, 4), "mitte": (5, 6, 7, 8), "ende": (9, 10, 11, 12),
                      "jahresanfang": (1, 2, 3), "jahresbeginn": (1, 2, 3),
                      "jahresmitte": (5, 6, 7, 8), "jahresende": (10, 11, 12),
                      "jahreswechsel": (12, 1)}
_JAHRESZEIT_RE = (r"(?:(?:Früh|Spät|Hoch)(?:sommer|herbst|winter)|Frühjahr|Frühling|Sommer|"
                  r"Herbst|Winter|Jahresanfang|Jahresbeginn|Jahresmitte|Jahresende|"
                  r"Jahreswechsel|Anfang|Beginn|Mitte|Ende)")
# Englische Monats-, Jahreszeit- und Zeitraumwoerter (2026-09-22, W57-Nachzug).
# Nur die vollen Monatsnamen: "Mar", "Jan" und "Sept" als Abkuerzung treffen in
# englischer Prosa auch Eigennamen, und die Analysen schreiben den Monat aus.
_MONATE_EN = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
              "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
              "december": 12}
_MONAT_EN_RE = (r"(?:January|February|March|April|May|June|July|August|September|"
                r"October|November|December)")
_JAHRESZEIT_MONATE_EN = {"spring": (3, 4, 5), "summer": (6, 7, 8), "autumn": (9, 10, 11),
                         "fall": (9, 10, 11), "winter": (12, 1, 2),
                         "early": (1, 2, 3, 4), "mid": (5, 6, 7, 8), "late": (9, 10, 11, 12),
                         "the start of": (1, 2, 3), "the beginning of": (1, 2, 3),
                         "the middle of": (5, 6, 7, 8), "the end of": (10, 11, 12),
                         "the turn of the year": (12, 1)}
# "early summer 2027", "mid-2027", "the end of 2026", "the turn of the year"
_JAHRESZEIT_EN_RE = (r"(?:(?:early|mid|late|high)[-\s]?(?:spring|summer|autumn|fall|winter)"
                     r"|the\s+turn\s+of\s+the\s+year"
                     r"|the\s+(?:start|beginning|middle|end)\s+of"
                     r"|spring|summer|autumn|fall|winter|early|mid|late)")

def _jz_kandidaten(jz_roh, j, tafel):
    """(Jahr, Monat)-Kandidaten einer Zeitangabe wie „Frühsommer 2027" / „early
    summer 2027". Normalisiert die Verstaerker beider Sprachen weg und legt fuer
    Winter und Jahreswechsel die Nachbarjahre dazu."""
    jz = re.sub(r"\s+", " ", (jz_roh or "").casefold().strip())
    for vor in ("früh", "spät", "hoch"):
        if jz.startswith(vor) and jz[len(vor):] in ("sommer", "herbst", "winter"):
            jz = jz[len(vor):]
    m = re.fullmatch(r"(?:early|mid|late|high)[-\s]?(spring|summer|autumn|fall|winter)", jz)
    if m:
        jz = m.group(1)
    monate = tafel.get(jz, tuple(range(1, 13)))
    kand = {(j, mo) for mo in monate}
    if jz in ("winter", "jahreswechsel", "the turn of the year"):
        kand |= {(j + 1, mo) for mo in (1, 2)} | {(j - 1, 12)}
    return kand

_P11_MUSTER_EN = (
    ("iso", re.compile(r"(?<!\d)(?P<j>\d{4})-(?P<m>\d{2})-(?P<t>\d{2})(?!\d)")),
    # die Belegzeile bleibt auch englisch TT.MM.JJJJ (W57, Nachtrag 2026-09-22)
    ("numerisch", re.compile(r"(?<![\d.])(?P<t>\d{1,2})\.(?P<m>\d{1,2})\.(?P<j>\d{4}|\d{2})(?![\d])")),
    ("monatsspanne", re.compile(
        r"(?<!\w)(?:(?P<t1>\d{1,2})\s+)?(?P<m1>%s)\s*(?:to|and|or|through|until|–|-|/)\s*"
        r"(?:(?P<t2>\d{1,2})\s+)?(?P<m2>%s)\s+(?P<j>%s)(?!\d)" % (_MONAT_EN_RE, _MONAT_EN_RE, _JAHR_RE))),
    # "5 June 2026", "June 5, 2026", "June 2026"
    ("monat", re.compile(r"(?<!\w)(?:(?P<t>\d{1,2})\s+)?(?P<m>%s)\s+(?P<j>%s)(?!\d)"
                         % (_MONAT_EN_RE, _JAHR_RE))),
    ("monat_us", re.compile(r"(?<!\w)(?P<m>%s)\s+(?P<t>\d{1,2})(?:st|nd|rd|th)?\s*,\s*(?P<j>%s)(?!\d)"
                            % (_MONAT_EN_RE, _JAHR_RE))),
    ("jahreszeit", re.compile(r"(?<!\w)(?P<jz>%s)[-\s]+(?:of\s+)?(?P<j>%s)"
                              r"(?:\s*/\s*(?P<j2>\d{2}|%s))?(?!\d)"
                              % (_JAHRESZEIT_EN_RE, _JAHR_RE, _JAHR_RE))),
    ("tag_ohne_jahr", re.compile(r"(?<!\w)(?P<t>\d{1,2})\s+(?P<m>%s)(?!\w)" % _MONAT_EN_RE)),
    ("jahr", re.compile(r"(?<![\d.,/-])(?P<j>%s)(?:\s*/\s*(?P<j2>%s|\d{2}))?(?![\d]|s\b)" % (_JAHR_RE, _JAHR_RE))),
    ("monat_ohne_jahr", re.compile(r"(?<!\w)(?P<m>%s)(?!\w)" % _MONAT_EN_RE)),
)
_P11_ALTER_EN = (
    re.compile(r"(?<!\w)at\s+the\s+age\s+of\s+(?:about\s+|around\s+|roughly\s+|just\s+)?"
               r"(?P<n>%s)(?!\w)" % _ZAHL_EN, re.I),
    re.compile(r"(?<!\w)when\s+you\s+(?:were|are|turn|turned)\s+(?:about\s+|around\s+|just\s+)?"
               r"(?P<n>%s)(?:\s+years?\s+old)?(?!\w)" % _ZAHL_EN, re.I),
    re.compile(r"(?<!\w)(?P<n>%s)\s+years?\s+old(?!\w)" % _ZAHL_EN, re.I),
    re.compile(r"(?<!\w)(?:you\s+(?:are|were)|are\s+you)\s+(?:now\s+|today\s+|just\s+)?"
               r"(?P<n>%s)(?=\s*(?:[.,;:!?–—)]|$)|\s+years?\b|\s+and\b)" % _ZAHL_EN, re.I),
    # "at 43", "at forty-three" — eng gefasst, weil "at" sonst jede Zahl im Satz zieht
    re.compile(r"(?<!\w)at\s+(?:about\s+|around\s+|roughly\s+|just\s+)?(?P<n>%s)"
               r"(?=\s*(?:[.,;:!?–—)]|$)|\s+years?\b|\s+(?:and|or|to|again|then)\b)" % _ZAHL_EN, re.I),
)

_P11_MUSTER = (
    ("iso", re.compile(r"(?<!\d)(?P<j>\d{4})-(?P<m>\d{2})-(?P<t>\d{2})(?!\d)")),
    ("numerisch", re.compile(r"(?<![\d.])(?P<t>\d{1,2})\.(?P<m>\d{1,2})\.(?P<j>\d{4}|\d{2})(?![\d])")),
    ("monatsspanne", re.compile(
        r"(?<![\wäöüß])(?:(?P<t1>\d{1,2})\.\s*)?(?P<m1>%s)\s*(?:bis|und|oder|–|-|/)\s*"
        r"(?:(?P<t2>\d{1,2})\.\s*)?(?P<m2>%s)\s+(?P<j>%s)(?![\d])" % (_MONAT_RE, _MONAT_RE, _JAHR_RE))),
    ("monat", re.compile(r"(?<![\wäöüß])(?:(?P<t>\d{1,2})\.\s*)?(?P<m>%s)\s+(?P<j>%s)(?![\d])"
                         % (_MONAT_RE, _JAHR_RE))),
    ("jahreszeit", re.compile(r"(?<![\wäöüß])(?P<jz>%s)\s+(?:des\s+Jahres\s+|von\s+|des\s+)?"
                              r"(?P<j>%s)(?:\s*/\s*(?P<j2>\d{2}|%s))?(?![\d])"
                              % (_JAHRESZEIT_RE, _JAHR_RE, _JAHR_RE))),
    ("tag_ohne_jahr", re.compile(r"(?<![\wäöüß.])(?P<t>\d{1,2})\.\s*(?P<m>%s)(?![\wäöüß])"
                                 % _MONAT_RE)),
    ("jahr", re.compile(r"(?<![\d.,/-])(?P<j>%s)(?:\s*/\s*(?P<j2>%s|\d{2}))?(?![\d]|er\b|ern\b|ers\b)"
                        % (_JAHR_RE, _JAHR_RE))),
    ("monat_ohne_jahr", re.compile(r"(?<![\wäöüß])(?P<m>%s)(?![\wäöüß])" % _MONAT_RE)),
)
_P11_ALTER = (
    re.compile(r"(?<![\wäöüß])mit\s+(?:gut\s+|knapp\s+|etwa\s+|rund\s+)?(?P<n>%s)(?:\s+Jahren)?"
               r"(?=\s*(?:[.,;:!?–—)]|$)|\s+Jahren\b|\s+(?:und|oder|bis|wieder|erneut|zum|zur|"
               r"noch|schon|erstmals|zuletzt|dann)\b)" % _ZAHL, re.I),
    re.compile(r"(?<![\wäöüß])als\s+du\s+(?:gut\s+|knapp\s+|etwa\s+|rund\s+)?(?P<n>%s)"
               r"(?:\s+Jahre\s+alt)?\s+(?:warst|bist|wirst)\b" % _ZAHL, re.I),
    re.compile(r"(?<![\wäöüß])im\s+Alter\s+von\s+(?:gut\s+|knapp\s+|etwa\s+|rund\s+)?(?P<n>%s)"
               r"(?![\wäöüß])" % _ZAHL, re.I),
    re.compile(r"(?<![\wäöüß])(?P<n>%s)\s+Jahre\s+alt\b" % _ZAHL, re.I),
    # 2026-10-01b (Pruefbericht Transit 1+2 vom 01.10., K1): attributiv vor einem
    # Nomen, das keine Person ist („im zwölfjährigen Umlauf“), ist es eine Dauer, kein
    # Lebensalter; „als Zwölfjährige“, „ein zwölfjähriges Kind“ bleiben Alter.
    # Nur die klein geschriebene, attributive Form zaehlt als Dauer; „als
    # Zwölfjähriger …“ (gross, substantiviert) bleibt Alter, ebenso vor einer Person.
    re.compile(r"(?<![\wäöüß])(?!(?-i:[a-zäöü0-9])[\wäöüß-]*?(?-i:jährig)(?:e|em|en|er|es)\s+"
               r"(?!(?:Kind|Kinder|Kindern|Kindes|Mädchen|Junge|Jungen|Bub|Knabe|Sohn|Tochter|"
               r"Bruder|Schwester|Enkel\w*|Neffe|Nichte|Mensch|Menschen|Frau|Mann|Person|"
               r"Schüler\w*|Jugendliche\w*|Teenager|Ich|Selbst)(?![\wäöüß]))(?-i:[A-ZÄÖÜ]))"
               r"(?P<n>%s)-?jährig" % _ZAHL, re.I),
    re.compile(r"(?<![\wäöüß])(?:du\s+bist|bist\s+du)\s+(?:jetzt\s+|heute\s+|gerade\s+|nun\s+)?"
               r"(?P<n>%s)(?=\s*(?:[.,;:!?–—)]|$)|\s+Jahre\b|\s+und\b)" % _ZAHL, re.I),
)
# 2026-10-01b (Pruefbericht Transit 1+2 vom 01.10., K1): die Reihe „als du X und Y
# warst“ lief an P11 vorbei (drei Stellen, sechs Alter ungeprueft) — das Einzelmuster
# verlangt „warst“ direkt hinter der Zahl. Jedes Glied wird einzeln geprueft; getrennt
# wird nur an Komma und freistehendem „und“/„oder“, nie im Zahlwort („achtundfünfzig“).
_P11_Q = r"(?:(?:gut|knapp|etwa|rund|about|around|roughly|just)\s+)?"
_P11_ALTER_LISTE = re.compile(
    r"(?<![\wäöüß])als\s+du\s+"
    r"(?P<liste>%s%s(?:\s*,\s*%s%s)*\s+(?:und|oder)\s+%s%s)(?:\s+Jahre\s+alt)?\s+"
    r"(?:warst|bist|wirst)\b" % (_P11_Q, _ZAHL, _P11_Q, _ZAHL, _P11_Q, _ZAHL), re.I)
_P11_ALTER_LISTE_EN = re.compile(
    r"(?<!\w)when\s+you\s+(?:were|are|turn|turned)\s+"
    r"(?P<liste>%s%s(?:\s*,\s*%s%s)*,?\s+(?:and|or)\s+%s%s)(?:\s+years?\s+old)?(?!\w)"
    % (_P11_Q, _ZAHL_EN, _P11_Q, _ZAHL_EN, _P11_Q, _ZAHL_EN), re.I)
_P11_Q_RE = re.compile(_P11_Q, re.I)
_P11_LISTE_TRENNER = re.compile(r"\s*,\s*(?:(?:und|oder|and|or)\s+)?|\s+(?:und|oder|and|or)\s+",
                                re.I)
_P11_LEBENSJAHR = re.compile(
    r"(?<![\wäöüß])(?:(?P<z>\d{1,3})\.\s*Lebensjahr|(?:das|dem|dein|deinem|deines|ins|im|bis|und|"
    r"um\s+das)\s+(?P<w>%s)(?=\s*(?:,|und\b|oder\b|bis\b|–|Lebensjahr|wenn\b|\.|$)))" % _ORDWORT,
    re.I)
_P11_DEKADE = re.compile(r"(?<![\wäöüß])(?:(?P<wo>Anfang|Mitte|Ende)|um\s+die)\s+(?P<z>%s)(?![\wäöüß])"
                         % _ZEHNER_W, re.I)
# 2026-09-30 (Klasse-2-Entscheidungslauf, Punkt 8; Pruefbericht Geburtshoroskop 1+2
# vom 29.09.d, Archiv 23.09. und 25.09.): „um die zweiundvierzig" — die Form, die
# das Typmodul fuer die zeitliche Einordnung selbst vorgibt — lief an P11 vorbei;
# _P11_DEKADE kennt nur Zehner („um die dreißig"). Im Pruffall pruefte P11 3 von
# 11 Altersangaben. Ein folgendes Substantiv („um die zwölf Monate") ist keine
# Altersangabe, ein Zehner bleibt bei _P11_DEKADE.
# 2026-10-09 (Klasse-2-Sammelliste Z. 385 und 1012, Chris-Freigabe): Gezaehlt wird
# genau n, nicht mehr n ± 1 — zusammen mit den ±1,5 Jahren am Zyklusfenster
# (_alter_gedeckt) ergab das ±2,5 Jahre, und „um die zweiundvierzig" gegen ein Fenster
# ~43,9 blieb still. „Um die …" am Satzanfang zaehlt jetzt mit ([Uu]m), bewusst ohne
# re.I: Mit re.I traefe der Grossbuchstaben-Riegel (?!\s+[A-ZÄÖÜ]) auch jedes klein
# geschriebene Folgewort, und fast jede Altersangabe fiele heraus.
_P11_UM_DIE = re.compile(r"(?<![\wäöüß])[Uu]m\s+die\s+(?P<n>%s)(?![\wäöüß])(?!\s+[A-ZÄÖÜ])"
                         % _ZAHL)

def _zahlen_index(txt, events=None):
    """Fundstellen der chart_data (und der events.json): Tage, Monate, Jahre,
    exakte Lebensalter, Zyklusfenster je Faktor (Strukturbild §7)."""
    idx = {"tage": set(), "monate": set(), "jahre": set(), "alter": set(),
           "zyklen": {}, "zyklen_alle": []}

    def tag(j, m, t=None):
        j, m = int(j), int(m)
        if j < 100:
            j += 2000
        idx["jahre"].add(j)
        idx["monate"].add((j, m))
        if t is not None:
            idx["tage"].add((j, m, int(t)))
    texte = [txt or ""]
    if events is not None:
        texte.append("\n".join(_json_strings(events, [])))
    for t in texte:
        for m in _DATUM_ISO_RE.finditer(t):
            tag(m.group(1), m.group(2), m.group(3))
        for m in re.finditer(r"(?<![\d-])(\d{4})-(\d{2})(?![\d-])", t):
            tag(m.group(1), m.group(2))
        for m in _DATUM_DE_RE.finditer(t):
            tag(m.group(3), m.group(2), m.group(1))
        for m in re.finditer(r"(?:(\d{1,2})\.\s*)?(%s)\s+(%s)(?![\d])" % (_MONAT_RE, _JAHR_RE), t):
            tag(m.group(3), _MONATE[m.group(2).casefold()], m.group(1))
        for m in re.finditer(r"(?<![\d.,])(%s)(?![\d])" % _JAHR_RE, t):
            idx["jahre"].add(int(m.group(1)))
    txt = txt or ""
    for m in re.finditer(r"\bAlter(?:\s+der\s+Person|\s+heute)?\s*(?:\([^)\n]*\))?\s*[:*]*\s*"
                         r"(\d{1,3})(?![\d.,])", txt):
        idx["alter"].add(int(m.group(1)))
    for m in re.finditer(r"(?<![\d.,])(\d{1,3})\s+Jahre\b", txt):
        idx["alter"].add(int(m.group(1)))

    def _alter_json(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("alter", "min_orb_alter") and isinstance(v, int):
                    idx["alter"].add(v)
                else:
                    _alter_json(v)
        elif isinstance(o, list):
            for v in o:
                _alter_json(v)
    if events is not None:
        _alter_json(events)
    m7 = re.search(r"\n#{2,4}\s*7\s*·[^\n]*", txt)
    if m7:
        teil = txt[m7.end():]
        schnitt = re.search(r"\n#{2,4} |\n@@", teil)
        teil = teil[:schnitt.start()] if schnitt else teil
    else:
        teil = "\n".join(z for z in txt.splitlines()
                         if re.search(r"R(?:ü|ue)ckkehr|Quadrat|Opposition", z) and "~" in z)
    for z in teil.splitlines():
        werte = [float(w.replace(",", ".")) for w in re.findall(r"~\s*(\d{1,3}(?:[.,]\d+)?)", z)]
        if not werte:
            continue
        idx["zyklen_alle"] += werte
        mf = re.match(r"^\s*[-*]\s*(%s)\s*:" % _FAKTOR_RE, z)
        if mf:
            idx["zyklen"].setdefault(kanon(mf.group(1)), []).extend(werte)
    return idx

# Faktorname im Fliesstext: gebeugt („des Mondes", „Saturns", „zum Aszendenten",
# „des Mondknotens") und in Bindestrich-Zusammensetzungen; Komposita ohne
# Bindestrich („Mondlicht", „Sonnenseite") zaehlen nicht.
_FLIESS_FAKTOR_RE = re.compile(r"(?<![\wäöüÄÖÜß])(%s|Knoten)(?:es|s|en|n)?(?![\wäöüÄÖÜß])"
                               % _FAKTOR_RE)
_FLIESS_WINKEL_RE = re.compile(r"(?<![\wäöüß])(?:(tiefst|höchst|hoechst)\w*\s+Punkt\w*"
                               r"|(Fu(?:ß|ss)punkt|Scheitelpunkt)\w*)", re.I)

def _faktoren_im_satz(satz):
    """Kanonische Faktoren eines Fliesstext-Satzes, auch gebeugt und in
    Zusammensetzungen („Fische-Sonne", „Saturn-Rückkehr", „deines Mondes",
    „zum Aszendenten"); `Knoten` allein zaehlt als Mondknoten, „tiefste(r) Punkt"
    und „Fußpunkt" als IC, „höchste(r) Punkt" und „Scheitelpunkt" als MC.
    -> [(anfang, ende, Schluessel)] in Textreihenfolge."""
    out = []
    for m in _FLIESS_FAKTOR_RE.finditer(satz or ""):
        out.append((m.start(), m.end(), kanon(m.group(1))))
    for m in _FLIESS_WINKEL_RE.finditer(satz or ""):
        tief = (m.group(1) or "").lower() == "tiefst" or bool(m.group(2)) and \
            m.group(2).lower().startswith("fu")
        out.append((m.start(), m.end(), "IC" if tief else "MC"))
    out.sort()
    return out

def _alter_gedeckt(n, faktoren, idx, spanne=1.5):
    """Lebensalter n gedeckt? Exakt (Alter-Angaben, fruehere Durchgaenge) oder
    innerhalb ±1,5 Jahren eines Zyklusfensters (§7). Nennt der Satz (oder der
    Satz davor) Faktoren, zaehlen NUR deren Fenster — ein Knoten-Alter wird nicht
    von einem zufaellig nahen Lilith-Fenster gedeckt; ohne Faktor zaehlt jedes."""
    if n in idx["alter"]:
        return True
    werte = [w for f in faktoren for w in idx["zyklen"].get(f, [])] if faktoren \
        else idx["zyklen_alle"]
    return any(abs(n - w) <= spanne + 1e-9 for w in werte)

def _p11_zahlen(chapters, txt, events=None, sprache_analyse="de"):
    p = _Probe("P11", "Zahlen-Deckung (Daten und Lebensalter)")
    p.einheit = "Angaben"
    # 2026-09-22 (W57-Nachzug): englische Tafeln statt Uebersprung. Die Muster
    # tragen dieselben Gruppennamen wie die deutschen, deshalb bleibt der Rumpf
    # unveraendert; gewechselt werden nur Musterliste, Monats- und Zeitraumtafel.
    englisch = (sprache_analyse != "de")
    MUSTER = _P11_MUSTER_EN if englisch else _P11_MUSTER
    ALTER = _P11_ALTER_EN if englisch else _P11_ALTER
    MON = _MONATE_EN if englisch else _MONATE
    JZM = _JAHRESZEIT_MONATE_EN if englisch else _JAHRESZEIT_MONATE
    if englisch:
        p.hinweise.append("englische Fassung — geprüft mit den englischen Monats-, Zeitraum- "
                          "und Zahlwörtern; „Lebensjahr“-Formen der deutschen Fassung entfallen")
    idx = _zahlen_index(txt, events)
    quelle = "chart_data und events.json" if events is not None else "chart_data"
    for ch, bewegung, text in _fliesstext(chapters):
        saetze = _saetze_pos(text)
        belegt = []                      # schon verbrauchte Spannen (laengere Muster zuerst)

        def frei(a, e):
            return all(e <= x or a >= y for x, y in belegt)

        def melde(stelle_txt, was, pos):
            p.pruefen.append("%s · %s: „%s“ — %s „%s“ ohne Fundstelle in %s"
                             % (_bezeichnung(ch), bewegung, _kurz(_satz_an(saetze, pos), 140),
                                was, stelle_txt, quelle))
        for art, rx in MUSTER:
            for m in rx.finditer(text):
                if not frei(m.start(), m.end()):
                    continue
                belegt.append((m.start(), m.end()))
                g = m.groupdict()
                p.geprueft += 1
                if art in ("iso", "numerisch"):
                    j = int(g["j"]) + (2000 if len(g["j"]) == 2 else 0)
                    ok = (j, int(g["m"]), int(g["t"])) in idx["tage"]
                    was = "Datum"
                elif art == "monatsspanne":
                    j = int(g["j"])
                    ok = True
                    for mm, tt in ((g["m1"], g["t1"]), (g["m2"], g["t2"])):
                        mo = MON[mm.casefold()]
                        ok = ok and (((j, mo, int(tt)) in idx["tage"]) if tt else
                                     ((j, mo) in idx["monate"] or (j - 1, mo) in idx["monate"]))
                    was = "Zeitraum"
                elif art in ("monat", "monat_us"):
                    mo = MON[g["m"].casefold()]
                    ok = ((int(g["j"]), mo, int(g["t"])) in idx["tage"]) if g["t"] else \
                        (int(g["j"]), mo) in idx["monate"]
                    was = "Datum" if g["t"] else "Monat"
                elif art == "jahreszeit":
                    j = int(g["j"])
                    kandidaten = _jz_kandidaten(g["jz"], j, JZM)
                    ok = bool(kandidaten & idx["monate"])
                    was = "Zeitangabe"
                elif art == "tag_ohne_jahr":
                    mo, tt = MON[g["m"].casefold()], int(g["t"])
                    ok = any((x[1], x[2]) == (mo, tt) for x in idx["tage"])
                    was = "Datum"
                elif art == "jahr":
                    jahre = [int(g["j"])]
                    if g.get("j2"):
                        jahre.append(int(g["j2"]) if len(g["j2"]) == 4 else int(g["j"][:2] + g["j2"]))
                    ok = all(j in idx["jahre"] for j in jahre)
                    was = "Jahreszahl"
                else:                    # monat_ohne_jahr
                    mo = MON[g["m"].casefold()]
                    ok = any(x[1] == mo for x in idx["monate"])
                    was = "Monat"
                if not ok:
                    melde(m.group(0), was, m.start())
        for i_s, (s_a, s_e, satz) in enumerate(saetze):
            fak = [f for _, _, f in _faktoren_im_satz(satz)] or \
                ([f for _, _, f in _faktoren_im_satz(saetze[i_s - 1][2])] if i_s else [])
            funde = []
            listen = []                  # 2026-10-01b: Reihe „als du X und Y warst“
            for m in (_P11_ALTER_LISTE_EN if englisch else _P11_ALTER_LISTE).finditer(satz):
                listen.append((m.start(), m.end()))
                for glied in _P11_LISTE_TRENNER.split(m.group("liste")):
                    glied = _P11_Q_RE.sub("", glied.strip(), count=1).strip()
                    n = _zahl_wert(glied)
                    if n is not None and (n >= 5 or glied.isdigit()):
                        funde.append(("%s (%s)" % (m.group(0), glied), n, n))
            for rx in ALTER:
                for m in rx.finditer(satz):
                    if any(a_ <= m.start() < e_ for a_, e_ in listen):
                        continue             # schon als Glied der Reihe gezaehlt
                    n = _zahl_wert(m.group("n"))
                    if n is not None and (n >= 5 or m.group("n").isdigit()):
                        funde.append((m.group(0), n, n))
            if "Lebensjahr" in satz:
                for m in _P11_LEBENSJAHR.finditer(satz):
                    n = int(m.group("z")) if m.group("z") else _ordinal_wert(m.group("w"))
                    if n and n >= 2:
                        funde.append((m.group(0), n - 1, n - 1))      # n. Lebensjahr = Alter n-1
            for m in _P11_DEKADE.finditer(satz):
                z = _ZEHNER_WERT[m.group("z").casefold()]
                wo = (m.group("wo") or "").casefold()
                lo, hi = {"anfang": (z, z + 3), "mitte": (z + 4, z + 6),
                          "ende": (z + 7, z + 9)}.get(wo, (z - 2, z + 2))
                funde.append((m.group(0), lo, hi))
            for m in _P11_UM_DIE.finditer(satz):
                if m.group("n").casefold() in _ZEHNER_WERT:
                    continue
                n = _zahl_wert(m.group("n"))
                if n is not None and n >= 5:
                    funde.append((m.group(0), n, n))         # 2026-10-09: genau n (s. _P11_UM_DIE)
            gesehen = set()
            for roh, lo, hi in funde:
                if (roh, lo) in gesehen:
                    continue
                gesehen.add((roh, lo))
                p.geprueft += 1
                if any(_alter_gedeckt(n, fak, idx) for n in range(lo, hi + 1)):
                    continue
                bekannt = sorted(idx["alter"])
                zyk = sorted({round(w, 1) for f in fak for w in idx["zyklen"].get(f, [])})
                p.pruefen.append("%s · %s: „%s“ — Altersangabe „%s“ (Alter %s) ohne Fundstelle in %s"
                                 "%s%s" % (_bezeichnung(ch), bewegung, _kurz(satz, 140), roh,
                                           lo if lo == hi else "%d–%d" % (lo, hi), quelle,
                                           "; dort Alter: " + ", ".join(map(str, bekannt[:8]))
                                           if bekannt else "",
                                           "; Zyklusfenster der Faktoren im Satz: " +
                                           ", ".join("~%g" % w for w in zyk) if zyk else ""))
    _p11_geburtsminute(p, chapters, txt)                    # 2026-10-01
    if p.geprueft == 0:
        p.hinweise.append("keine Datums- oder Altersangabe im Fließtext")
    return p.abschluss()


# 2026-10-01 (Chris-Entscheidung, Klasse-2-Sammelliste; Wartungslauf zu den
# Pruefberichten vom 30.09.): Ein Satz zur Geburtsminute steht im Text nur beim AC
# mit Gegenprobe-Blatt — EINER, im Auftakt, der auf das Blatt zeigt (Strukturbild §3,
# Zeitscan). Jeder andere ist ein PRUEFEN. „frühere Geburten“ (Plural) und Minuten
# ohne Bezug auf Geburt, Zeichen, Haus oder Achse („zehn Minuten später“ in einer
# Übung) zaehlen nicht.
_GM_STARK_RE = re.compile(
    r"(?<![\wäöüÄÖÜß])(?:(?:früher|später)e[rnms]?\s+Geburt(?![\wäöüÄÖÜß])|Geburtsminute"
    r"|Geburts(?:zeit|uhrzeit)\w*\s+(?:[\wäöüÄÖÜß]+\s+){0,3}?(?:entscheid|kipp|wechsel)"
    r"|(?:entscheid|kipp)\w*\s+(?:[\wäöüÄÖÜß]+\s+){0,3}?(?:die|deine)\s+Geburts(?:zeit|uhrzeit)"
    r"|(?:earlier|later)\s+birth(?![\w])|birth\s+minute)", re.I)
_GM_MINUTEN_RE = re.compile(r"(?<![\wäöüÄÖÜß])(?:Minuten?|Sekunden|minutes?)\s+"
                            r"(?:früher|später|eher|earlier|later)(?![\wäöüÄÖÜß])", re.I)
_GM_KONTEXT_RE = re.compile(r"geboren|Geburt|Zeichen|Haus|Häuser|Aszendent|Himmelsmitte|"
                            r"Spitze|Achse|born|birth|sign|house|ascendant", re.I)


def _p11_geburtsminute(p, chapters, txt):
    """PRUEFEN je Satz zur Geburtsminute im Fliesstext; meldet der Zeitscan der
    chart_data „Gegenprobe-Blatt fällig“, bleibt EIN Satz im Auftakt still."""
    frei = 1 if "Gegenprobe-Blatt fällig" in (txt or "") else 0
    for ch, bewegung, text in _fliesstext(chapters):
        for _a, _e, satz in _saetze_pos(text):
            if not (_GM_STARK_RE.search(satz) or (_GM_MINUTEN_RE.search(satz)
                                                  and _GM_KONTEXT_RE.search(satz))):
                continue
            if frei and _ist_kicker(ch, "Auftakt"):
                frei -= 1
                continue
            p.pruefen.append(
                "%s · %s: „%s“ — Satz zur Geburtsminute im Text; seit 2026-10-01 steht "
                "dazu im PDF nur beim AC mit Gegenprobe-Blatt EIN Satz im Auftakt, der "
                "auf das Blatt zeigt (Strukturbild §3, Zeitscan)"
                % (_bezeichnung(ch), bewegung, _kurz(satz, 140)))

# --- P12 Rang- und Einzigkeitswörter -----------------------------------------
# Rangzeilen des Strukturbilds (§10, seit 2026-09-19, U2). Die Muster stehen
# WOERTLICH wie `radix.RANG_ZEILE_RE` / `radix.RANG_EINTRAG_RE` (Schnittstelle:
# log/SCHNITTSTELLE_rangzeilen.md des Wartungslaufs A) — radix wird hier nicht
# importiert, weil Schritt 2 es nicht laedt (lade.SCHRITTE["2"]). Der Selbsttest
# vergleicht beide Fassungen, wo radix importierbar ist; aendert sich das Format,
# schlaegt er an.
RANG_ZEILE_RE = re.compile(
    r'^- RANG (?P<schluessel>[a-z0-9-]+) \[(?P<menge>[^\]]*)\]: '
    r'(?P<eintraege>.*)$', re.M)
RANG_EINTRAG_RE = {
    'aspekt': re.compile(
        r'^(?P<rang>\d+)\. (?P<a>\S+) (?P<aspekt>\S+) (?P<b>\S+) '
        r'(?P<orb>\d+°\d{2}′) \((?P<staerke>[a-z]+)(?:, (?P<zusatz>[^)]*))?\)$'),
    'verbindung': re.compile(
        r'^(?P<rang>\d+)\. (?P<faktor>\S+) (?P<wert>\d+(?:\.\d+)?)'
        r'(?: \(Aspekttabelle (?P<aspekttabelle>\d+)\))?$'),
    'verteilung': re.compile(
        r'^(?P<rang>\d+)\. (?P<name>\S+) (?P<wert>\d+(?:\.\d+)?) von '
        r'(?P<summe>\d+(?:\.\d+)?) = (?P<prozent>\d+) % '
        r'\((?P<traeger>[^)]*)\)$'),
}

def _rangzeilen_lesen(text):
    """Wie radix.rangzeilen_lesen(): {schluessel: {'menge', 'eintraege'}}; ein
    unlesbarer Eintrag kommt als {'roh': text}, nie still verworfen."""
    out = {}
    for m in RANG_ZEILE_RE.finditer(text or ""):
        schl = m.group("schluessel")
        fam = ("aspekt" if schl.startswith("engste-") else
               "verbindung" if schl.startswith("verbindungen-") else "verteilung")
        eintraege = []
        roh = m.group("eintraege").strip()
        for teil in ([] if roh in ("", "—") else roh.split(" · ")):
            e = RANG_EINTRAG_RE[fam].match(teil)
            if not e:
                eintraege.append({"roh": teil})
                continue
            d = e.groupdict()
            d["rang"] = int(d["rang"])
            if fam == "aspekt":
                g, mi = d["orb"].split("°")
                d["orb_min"] = int(g) * 60 + int(mi.rstrip("′"))
            elif fam == "verbindung":
                d["wert"] = (float(d["wert"]) if schl.endswith("gewichtet") or "." in d["wert"]
                             else int(d["wert"]))
                d["aspekttabelle"] = int(d["aspekttabelle"]) if d["aspekttabelle"] else None
            else:
                d["wert"], d["summe"] = float(d["wert"]), float(d["summe"])
                d["prozent"] = int(d["prozent"])
                tr = []
                for t in ([] if d["traeger"] in ("", "—") else d["traeger"].split(", ")):
                    n, _, gw = t.partition(" ×")
                    tr.append((n, float(gw) if gw else 1.0))
                d["traeger"] = tr
            eintraege.append(d)
        out[schl] = {"menge": m.group("menge"), "eintraege": eintraege}
    return out

# 2026-09-30 (K1): auch der Genitiv („Träger des Wassers“, „des Feuers“)
_ELEMENT_RE = re.compile(r"(?<![\wäöüß])(?:(Feuer|Erde|Luft|Wasser)(?:s|zeichen\w*|element\w*)?"
                         r"|(Erd)(?:zeichen\w*|element\w*))(?![\wäöüß])")
_MODUS_RE = re.compile(r"(?<![\wäöüß])([Kk]ardinal|[Ff]ix|[Vv]eränderlich|[Bb]eweglich)"
                       r"(?:e|en|er|es|em)?(?![\wäöüß])"
                       # 2026-09-29 (K1): die Klartext-Namen der Modi
                       r"|Kraft,?\s+(anzufangen|zu\s+halten|sich\s+anzupassen)(?![\wäöüß])")
_MODUS_KLAR = {"anzufangen": "kardinal", "zu halten": "fix",
               "sich anzupassen": "veränderlich"}


def _modus_name(mm):
    """Kanonischer Modus eines _MODUS_RE-Treffers (Fachwort oder Klartext-Name)."""
    if mm.group(1):
        return {"beweglich": "veränderlich"}.get(mm.group(1).lower(), mm.group(1).lower())
    return _MODUS_KLAR[" ".join(mm.group(2).split())]


# 2026-10-12 (Nacharbeiten Englisch, W1): Element und Modus der EINZIGKEITSAUSSAGE, in
# beiden Sprachen gleich — „die einzige im Feuer“, „der einzige Träger des Feuers“, „die
# einzige in einem Zeichen der Anpassung“; „the only one in fire“, „the only carrier of
# fire“, „the only one in a sign of adaptation“, auch mit „single“ und „sole“. Die
# Zeichen-Form der Modi steht bewusst NICHT in _MODUS_RE: dort liest sie P18 mit und
# meldete „…, alles andere in Zeichen des Anfangs und des Haltens“ (Zweitpruefung).
# Englisch liest nur diese Aussage ein Element; die uebrigen englischen Rang- und
# Anteilswoerter („half“, „all four“ …) nicht — Grenze des Auftrags.
_MODUS_ZEICHEN_RE = re.compile(r"(?<![\wäöüß])Zeichen\s+(der\s+Anpassung|des\s+Anfang(?:en)?s"
                               r"|des\s+Haltens)(?![\wäöüß])")
_MODUS_ZEICHEN = {"der Anpassung": "veränderlich", "des Anfangs": "kardinal",
                  "des Anfangens": "kardinal", "des Haltens": "fix"}
_ELEMENT_EN_RE = re.compile(r"(?<!\w)(fire|earth|air|water|fiery|earthy|airy|watery)"
                            r"(?:\s+(?:signs?|element))?(?!\w)", re.I)
_ELEMENT_EN = {"fire": "Feuer", "fiery": "Feuer", "earth": "Erde", "earthy": "Erde",
               "air": "Luft", "airy": "Luft", "water": "Wasser", "watery": "Wasser"}
_MODUS_EN_RE = re.compile(r"(?<!\w)(cardinal|fixed|mutable)(?!\w)"
                          r"|(?<!\w)power,?\s+to\s+(begin|hold|adapt)(?!\w)"
                          r"|(?<!\w)signs?\s+of\s+(beginning|holding|adaptation)(?!\w)", re.I)
_MODUS_EN = {"cardinal": "kardinal", "fixed": "fix", "mutable": "veränderlich",
             "begin": "kardinal", "hold": "fix", "adapt": "veränderlich",
             "beginning": "kardinal", "holding": "fix", "adaptation": "veränderlich"}
# Was zwischen dem Einzigkeitswort und der Praeposition vor dem Element oder Modus stehen
# darf — „die einzige Kraft im Feuer“, „die einzige deiner Kräfte, die im Feuer steht“,
# „the only one of your ten main forces in fire“, „the only force that stands in fire“.
# Sonst gehoert das Element zu etwas anderem: „the only planet in a square to your Moon in
# water“, „einen einzigen tiefen Atemzug Luft“ (Zweitpruefung).
_EM_ZWISCHEN_DE = frozenset((
    "kraft", "kräfte", "kräften", "hauptkraft", "hauptkräfte", "hauptkräften", "planet",
    "planeten", "träger", "faktor", "faktoren", "deiner", "deinen", "von", "unter", "den",
    "zehn", "die", "der", "das", "welche", "welcher", "welches"))
_EM_ZWISCHEN_EN = frozenset((
    "one", "ones", "planet", "planets", "force", "forces", "main", "carrier", "carriers",
    "factor", "factors", "of", "your", "the", "ten", "among", "that", "which", "who",
    "stands", "stand", "lies", "lie", "sits", "sit", "is", "are"))
_EM_VOR_RE = re.compile(r"(?<![\wäöüß])(?:im|ins|in|des|der|vom|of)\s+(?:(?:a|an|the|your|der|dem|"
                        r"den|des|einem|einer|eines|deinem|deiner|deines)\s+)?$", re.I)


def _em_treffer(text, englisch=False):
    """(anfang, element, modus) des ERSTEN Element- oder Modus-Ausdrucks im Text, kanonisch
    deutsch („Feuer“, „veränderlich“), der jeweils andere None; None ohne Treffer.
    englisch: die englischen Muster (2026-10-12, W1)."""
    t = text or ""
    if englisch:
        kand = [(x.start(), "e", x) for x in (_ELEMENT_EN_RE.search(t),) if x] + \
               [(x.start(), "m", x) for x in (_MODUS_EN_RE.search(t),) if x]
    else:
        kand = [(x.start(), "e", x) for x in (_ELEMENT_RE.search(t),) if x] + \
               [(x.start(), "m", x) for x in (_MODUS_RE.search(t),) if x] + \
               [(x.start(), "z", x) for x in (_MODUS_ZEICHEN_RE.search(t),) if x]
    if not kand:
        return None
    a0, art_, x = min(kand, key=lambda k: k[0])
    if art_ == "e":
        if englisch:
            return a0, _ELEMENT_EN[x.group(1).lower()], None
        w = x.group(1) or x.group(2)
        return a0, {"Erd": "Erde"}.get(w, w), None
    if art_ == "z":
        return a0, None, _MODUS_ZEICHEN[" ".join(x.group(1).split())]
    if englisch:
        return a0, None, _MODUS_EN[next(g for g in x.groups() if g).lower()]
    return a0, None, _modus_name(x)


def _element_modus(text, englisch=False):
    """(element, modus) des ersten Element- oder Modus-Ausdrucks im Text (_em_treffer);
    (None, None) ohne Treffer."""
    t = _em_treffer(text, englisch)
    return (None, None) if t is None else (t[1], t[2])


def _em_hinter(hinter, englisch=False):
    """(element, modus) im Satzglied HINTER einem Einzigkeitswort — nur, wenn direkt davor
    eine Praeposition steht (hoechstens mit Artikel, _EM_VOR_RE) und dazwischen nur Woerter
    aus _EM_ZWISCHEN_DE bzw. _EM_ZWISCHEN_EN, hoechstens acht; sonst (None, None)
    (2026-10-12, W1)."""
    t = _em_treffer(hinter, englisch)
    if t is None:
        return None, None
    vor = hinter[:t[0]]
    mv = _EM_VOR_RE.search(vor)
    if not mv:
        return None, None
    erlaubt = _EM_ZWISCHEN_EN if englisch else _EM_ZWISCHEN_DE
    zwischen = re.findall(r"[\wäöüÄÖÜß’'-]+", vor[:mv.start()])
    if len(zwischen) > 8 or any(w.casefold() not in erlaubt for w in zwischen):
        return None, None
    return t[1], t[2]


# Pronomen vor dem Einzigkeitswort — deutsch mit Genus (2026-10-12, W1)
_EINZIG_PRONOMEN_GENUS = {"er": "m", "sie": "f", "dieser": "m", "diese": "f", "jener": "m",
                          "jene": "f"}


def _einzig_bezug(pron, vorher, englisch=False):
    """Kandidaten eines Pronomens vor dem Einzigkeitswort: ALLE Faktoren des Vorsatzes,
    deutsch nach dem Genus des Pronomens (Faktoren ohne Genus, etwa MC und IC, passen immer);
    englisch ohne Filter. Still bleibt die Probe nur, wenn alle der Traeger sind — anders als
    `_pronomen_bezug()`, das ohne Genus nur den letzten Faktor nimmt (Zweitpruefung
    2026-10-12: „Mars squares Saturn. … it is the only one in fire.“ blieb still)."""
    fs = list(dict.fromkeys(f for _a, _e, f in _faktoren_im_satz(vorher or "")))
    g = None if englisch else _EINZIG_PRONOMEN_GENUS.get((pron or "").casefold())
    return [f for f in fs if g is None or _GENUS.get(f, g) == g]


# Die Einzigkeitsaussage ueber ein Element oder einen Modus in ihrer englischen Form —
# oeffnet P12 einen Satz ohne Faktor („It is the only one in fire.“), wie im Deutschen
# das Element selbst („Er ist die einzige im Feuer.“) es tut (2026-10-12, W1).
_EINZIG_EM_EN_RE = re.compile(
    r"(?<!\w)(?:the\s+(?:only|single|sole)|only\s+one)\s+(?:(?:%s)\s+)*?(?:in|of)\s+"
    r"(?:(?:a|an|the|your)\s+)?(?:%s|%s)" % ("|".join(sorted(_EM_ZWISCHEN_EN)),
                                         _ELEMENT_EN_RE.pattern, _MODUS_EN_RE.pattern), re.I)
_REFERENT_RE = re.compile(
    r"(?<![\wäöüß])(?:Planet\w*|Punkt\w*|Aspekt\w*|Verbindung\w*|Kontakt\w*|Faktor\w*|"
    r"Zeichen|Element\w*|Häuser\w*|Haus|Hauses|Figur\w*|Stellium\w*|Achse\w*|Winkel\w*|"
    r"Konstellation\w*|Transit\w*|Quadrant\w*|Hemisphäre\w*)(?![\wäöüß])")
# 2026-09-19 (U1 b): gesucht wird die AUSSAGE, nicht das Wort — „die meisten
# Menschen", „wo du am wenigsten sicher bist" und „eine Verbindung, die hält"
# (unbestimmter Artikel) sind keine Rang- oder Zaehlaussagen ueber das Chart.
_ANZAHLWORT = r"(?:beiden|zwei|drei|vier|fünf|fuenf|sechs|sieben|acht|neun|zehn|\d{1,2})"
_CHART_NOMEN = (r"(?:Verbindung|Aspekt|Kontakt|Planet|Faktor|Punkt|Träger|Verkehr|Winkel"
                r"|Konjunktion|Opposition|Quadrat|Trigon|Sextil)")
_CHART_VERB = r"(?:verbunden|verschaltet|vernetzt|angebunden|besetzt|aspektiert|beteiligt)"
# Woran eine Einzigkeitsaussage erkennbar ist: Sie zaehlt etwas aus dem Chart.
_EINZIG_NOMEN = (r"(?:Planet|Punkt|Aspekt|Verbindung|Kontakt|Faktor|Zeichen|Element"
                 r"|Haus|Häuser|Figur|Träger|Winkel|Konjunktion|Opposition|Quadrat"
                 r"|Trigon|Sextil|Quincunx|Halbsextil|Stellium|Hauptkraft|Hauptkräfte)\w*")
# 2026-10-12 (W1): Element oder Modus hinter „einzig…“ und einer Praeposition, dazwischen nur
# Woerter aus _EM_ZWISCHEN_DE — „die einzige im Feuer“, „die einzige Kraft in einem Zeichen
# der Anpassung“, „die einzige deiner Kräfte, die im Feuer steht“
_EINZIG_EM_DE = (r"(?:(?:Kraft|Kräfte|Kräften|Hauptkraft|Hauptkräfte|Hauptkräften|Planet|Planeten"
                 r"|Träger|Faktor|Faktoren|deiner|deinen|von|unter|den|zehn|die|der|das|welche[rs]?)"
                 r"\s*,?\s+){0,6}?(?:im|ins|in|des|der|vom)\s+(?:(?:der|dem|den|des|einem|einer|eines"
                 r"|deinem|deiner|deines)\s+)?"
                 r"(?:(?:Feuer|Erde|Luft|Wasser)(?:s|zeichen\w*|element\w*)?|Erd(?:zeichen|element)\w*"
                 r"|(?:kardinal|fix|veränderlich|beweglich)(?:e|en|er|es|em)?"
                 r"|Kraft,?\s+(?:anzufangen|zu\s+halten|sich\s+anzupassen)"
                 r"|Zeichen\s+(?:der\s+Anpassung|des\s+Anfang(?:en)?s|des\s+Haltens))(?![\wäöüß])")
_RANG_MUSTER = (
    ("engste", re.compile(
        r"(?<![\wäöüß])(?:(?P<eine>(?:eine[rnms]?|einer)\s+der\s+(?:(?P<n>%s)\s+)?engst\w*)"
        r"|(?:die|den|der)\s+(?P<n2>%s)\s+engst\w*"
        r"|(?P<ord>zweit|dritt|viert)?engst(?:e|en|er|es|em)?"
        r"|am\s+engsten)(?![\wäöüß])" % (_ANZAHLWORT, _ANZAHLWORT), re.I)),
    ("meiste", re.compile(
        r"(?<![\wäöüß])(?P<mit>mit\s+(?=die\s))?(?:die|den|der)\s+meisten(?=\s+(?:[\wäöüß]+\s+){0,2}?%s)"
        r"|(?<![\wäöüß])am\s+meisten(?=\s+(?:[\wäöüß]+\s+)?%s)"
        r"|(?<![\wäöüß])meist(?:verbunden|verschaltet|vernetzt)\w*"
        r"|(?<![\wäöüß])am\s+(?:dichtesten|stärksten|häufigsten)\s+(?:verschaltet|verbunden|vernetzt)\w*"
        % (_CHART_NOMEN, _CHART_VERB), re.I)),
    ("wenigste", re.compile(
        r"(?<![\wäöüß])(?:die|den|der)\s+wenigsten(?=\s+(?:[\wäöüß]+\s+){0,2}?%s)"
        r"|(?<![\wäöüß])am\s+wenigsten(?=\s+(?:[\wäöüß]+\s+)?%s)"
        r"|(?<![\wäöüß])am\s+(?:schwächsten|dünnsten|losesten)\s+"
        r"(?:verschaltet|verbunden|vernetzt|angebunden)\w*" % (_CHART_NOMEN, _CHART_VERB), re.I)),
    # 2026-09-22 (Prueflauf Geburtshoroskop 1+2 vom 2026-09-22b, Nr. 8): Der
    # erste Zweig traf „einzig" OHNE jede Bedingung und meldete damit reine
    # Bilder als Einzigkeitsaussage — „einen einzigen Strom", „die einzige
    # Bewegung, die traegt": 20 von 40 PRUEFEN-Zeilen eines Laufs ohne jeden
    # Zahlengehalt. Verlangt wird jetzt dasselbe Chart-Nomen wie im zweiten
    # Zweig, hoechstens zwei Woerter dahinter.
    # 2026-10-12 (Nacharbeiten Englisch, W1): oder hinter einer Praeposition ein Element
    # oder ein Modus (_EINZIG_EM_DE) — „die einzige im Feuer“ fiel vorher ganz durch und
    # waere auch falsch still geblieben.
    ("einzig", re.compile(r"(?<![\wäöüß])einzig(?:e|en|er|es|em)?(?![\wäöüß])"
                          r"(?=\s+(?:(?:[\wäöüß]+\s+){0,2}%s|%s))"
                          r"|(?<![\wäöüß])nur\s+(?:ein|eine|einen|einem|einer)\s+"
                          r"(?=(?:einzig\w*\s+)?%s)" % (_EINZIG_NOMEN, _EINZIG_EM_DE, _EINZIG_NOMEN),
                          re.I)),
    ("kein_anderer", re.compile(r"(?<![\wäöüß])(?:kein(?:e|en|em|er)?\s+(?:andere[rnms]?|weitere[rnms]?)"
                                r"|sonst\s+kein\w*)(?![\wäöüß])", re.I)),
    ("x_von_y", re.compile(r"(?<![\wäöüß])(?P<x>%s|eine[rns]?|ein)\s+von\s+(?P<y>%s)(?![\wäöüß])"
                           % (_ZAHL, _ZAHL), re.I)),
    ("haelfte", re.compile(r"(?<![\wäöüß])(?:(?P<vgl>mehr|weniger)\s+als\s+"
                           r"|(?P<ca>fast|knapp|beinahe|nahezu|gut|rund|etwa|ungefähr)\s+)?die\s+Hälfte"
                           r"(?![\wäöüß])(?!\s+(?:eines\s+)?Grad)"
                           r"|(?<![\wäöüß])(?P<drittel>ein|zwei)\s+Drittel(?![\wäöüß])(?!\s+(?:eines\s+)?Grad)"
                           r"|(?<![\wäöüß])(?P<proz>\d{1,3})\s*(?:%|Prozent)(?![\wäöüß])", re.I)),
    # Grundzahl ab zwei, oder „nur/genau … eine" — der unbestimmte Artikel allein
    # („eine Verbindung, die von selbst hält") ist keine Zaehlaussage.
    ("n_verbindungen", re.compile(
        r"(?<![\wäöüß])(?:(?P<n>zwei|drei|vier|fünf|fuenf|sechs|sieben|acht|neun|zehn|elf|zwölf|"
        r"zwoelf|\d{1,2})|(?:nur|genau|bloß|lediglich|gerade\s+einmal|nicht\s+mehr\s+als)\s+"
        r"(?P<ein>eine[rnm]?|ein))\s+"
        # 2026-09-30 (K1): „die nächsten zwei Jahre Verbindungen zu pflegen“ — eine
        # Zeitspanne zaehlt keine Verbindungen
        r"(?:(?!(?:Jahr|Monat|Woche|Tag|Quartal|Stunde)\w*\s)[\wäöüß]+\s+)?"
        r"Verbindung(?:en)?(?![\wäöüß])", re.I)),
    # 2026-09-24 (Pruefberichte vom 24.09.): „alle zwölf Jahre", „etwa alle neun Jahre"
    # nennen eine Umlaufzeit (Strukturbild §7; keine Probe prueft sie), keine Zaehlung
    # im Chart — sie kamen in jedem Lauf als PRUEFEN und stimmten jedes Mal.
    ("alle_n", re.compile(r"(?<![\wäöüß])alle\s+(?:%s)(?![\wäöüß])"
                          r"(?!\s+(?:(?:bis|oder)\s+\S+\s+)?(?:Jahr|Monat|Woche|Tag)\w*)"
                          # 2026-09-29 (K1): Teile einer Figur („alle vier Ecken“)
                          r"(?!\s+(?:Ecken|Enden|Seiten|Glieder|Spitzen)(?![\wäöüß]))"
                          % _ZAHLWORT, re.I)),
)

# Englische Rang-, Zaehl- und Einzigkeitswoerter (2026-09-22, W57-Nachzug).
# Gesucht ist wie im Deutschen die AUSSAGE ueber das Chart, nicht das Wort: ohne
# Referenten im Satz (Faktor, Zeichen, Element, Aspektwort oder ein Nomen aus
# _REFERENT_EN_RE) zaehlt kein Treffer. Die Musterarten heissen wie die deutschen,
# damit `_rang_befund()` unveraendert bleibt.
_REFERENT_EN_RE = re.compile(
    r"(?<!\w)(?:planets?|points?|aspects?|connections?|contacts?|factors?|signs?|"
    r"elements?|houses?|house|figures?|stelliums?|stellia|axes|axis|angles?|"
    r"constellations?|transits?|quadrants?|hemispheres?|chart)(?!\w)", re.I)
_ANZAHLWORT_EN = r"(?:both|two|three|four|five|six|seven|eight|nine|ten|\d{1,2})"
_CHART_NOMEN_EN = (r"(?:connection|aspect|contact|planet|factor|point|carrier|angle"
                   r"|conjunction|opposition|square|trine|sextile)s?")
_CHART_VERB_EN = r"(?:connected|wired|linked|networked|tied|occupied|aspected|involved)"
_ORDWORT_EN = (r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth"
               r"|\d{1,2}(?:st|nd|rd|th))")
_RANG_MUSTER_EN = (
    # "one of the closest", "the two tightest", "the second closest", "closest of all"
    ("engste", re.compile(
        r"(?<!\w)(?:(?P<eine>one\s+of\s+the\s+(?:(?P<n>%s)\s+)?(?:closest|tightest|narrowest))"
        r"|the\s+(?P<n2>%s)\s+(?:closest|tightest|narrowest)"
        r"|the\s+(?P<ord>%s)\s+(?:closest|tightest|narrowest)"
        r"|(?:closest|tightest|narrowest)(?:\s+of\s+(?:all|them\s+all))?)(?!\w)"
        % (_ANZAHLWORT_EN, _ANZAHLWORT_EN, _ORDWORT_EN), re.I)),
    ("meiste", re.compile(
        r"(?<!\w)(?:with\s+)?the\s+most(?=\s+(?:\w+\s+){0,2}?%s)"
        r"|(?<!\w)most\s+(?:%s)\b"
        r"|(?<!\w)the\s+most\s+(?:densely|tightly|heavily)\s+(?:%s)\b"
        % (_CHART_NOMEN_EN, _CHART_VERB_EN, _CHART_VERB_EN), re.I)),
    ("wenigste", re.compile(
        r"(?<!\w)the\s+(?:fewest|least)(?=\s+(?:\w+\s+){0,2}?%s)"
        r"|(?<!\w)least\s+(?:%s)\b"
        r"|(?<!\w)the\s+(?:least|most\s+loosely|most\s+weakly|most\s+thinly)\s+(?:%s)\b"
        % (_CHART_NOMEN_EN, _CHART_VERB_EN, _CHART_VERB_EN), re.I)),
    ("einzig", re.compile(
        r"(?<!\w)the\s+(?:only|single|sole)(?!\w)"
        r"|(?<!\w)only\s+one\s+(?=(?:other\s+)?(?:%s|sign|element|house))"
        % _CHART_NOMEN_EN, re.I)),
    ("kein_anderer", re.compile(
        r"(?<!\w)(?:no\s+other(?:\s+\w+)?|nothing\s+else\s+in\s+(?:your|the)\s+chart"
        r"|none\s+of\s+the\s+others?)(?!\w)", re.I)),
    ("x_von_y", re.compile(r"(?<!\w)(?P<x>%s)\s+of\s+(?:the\s+|your\s+)?(?P<y>%s)(?!\w)"
                           % (_ZAHL_EN, _ZAHL_EN), re.I)),
    ("haelfte", re.compile(
        r"(?<!\w)(?:(?P<vgl>more|less|fewer)\s+than\s+)?(?:a\s+|one\s+|the\s+)?half(?!\w)"
        r"(?!\s+(?:a\s+)?degree)"
        r"|(?<!\w)(?P<drittel>a|one|two)\s+thirds?(?!\w)(?!\s+(?:of\s+a\s+)?degree)"
        r"|(?<!\w)(?P<proz>\d{1,3})\s*(?:%|per\s?cent)(?!\w)", re.I)),
    ("n_verbindungen", re.compile(
        r"(?<!\w)(?:(?P<n>two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d{1,2})"
        r"|(?:only|just|exactly|no\s+more\s+than)\s+(?P<ein>one))"
        r"\s+(?:\w+\s+)?connections?(?!\w)", re.I)),
    ("alle_n", re.compile(r"(?<!\w)all\s+(?:of\s+)?(?:the\s+|your\s+)?(?:%s)(?!\w)" % _ZAHLWORT_EN, re.I)),
)

# 2026-09-24 (Pruefberichte vom 24.09., alle vier Geburtshoroskop-Laeufe und Transit
# 1+2): Das Bild „der Planet, der keinem anderen folgt" schreibt das Klartext-Modul
# fuer den Endherrscher vor; P12 meldete es als Einzigkeit ohne Rangzeile — bis zu drei
# PRUEFEN je Geburtshoroskop, alle zutreffend. Die Fundstelle ist Strukturbild §3: Wer
# im eigenen Zeichen steht (Enddispositoren und „ohne Zulauf"), folgt keinem anderen.
# Gedeckt ist der Satz, wenn er alle diese Planeten nennt — bei „Er …" am Satzanfang
# zaehlt der Bezug des Pronomens dazu, ohne eigenen Faktor der ganze Vorsatz. Stehen
# dort mehrere und nennt der Satz nicht alle, bleibt PRUEFEN — mit der Liste aus §3
# (Transit 1+2 vom 24.09., Inhalt Nr. 7: „der Planet, der keinem anderen folgt" bei
# zwei Endstellen). Gilt nur fuer den Treffer, der selbst „folgt" traegt.
# 2026-09-25 (Pruefberichte vom 25.09.): Einzahl und Eigenschaft getrennt. „der
# Planet, der keinem anderen folgt", „als einziger", „nur er" behaupten Einzigkeit —
# gedeckt nur, wenn der Satz ALLE Planeten aus §3 nennt (so bisher). „dein Mond …
# folgt keinem anderen" sagt eine Eigenschaft des genannten Planeten — gedeckt, wenn
# er in §3 steht; vorher blieb auch das PRUEFEN, sobald §3 mehrere fuehrte (vier
# Laeufe, jedes Mal richtig). Dazu die Variante „richtet sich nach keinem anderen",
# die gegen die Element-Rangzeile lief (Geburtshoroskop 1+2b und 3+4b vom 25.09.).
_FOLGT_KEINEM_RE = re.compile(
    r"(?<![\wäöüß])(?:keinem\s+anderen(?:\s+[\wäöüß]+)?\s+folg\w*"
    r"|folg\w*\s+(?:[\wäöüß]+\s+){0,2}keinem\s+anderen"
    r"|richte\w*\s+sich\s+(?:[\wäöüß]+\s+)?nach\s+keinem\s+anderen"
    r"|sich\s+nach\s+keinem\s+anderen(?:\s+[\wäöüß]+)?\s+richte\w*"
    r"|follows?\s+no\s+other)", re.I)
# Einzahl: der Text VOR „keinem anderen" endet auf „der Planet, der …" bzw. traegt
# „als einzige(r)", „der/die einzige", „nur er/sie"
_FOLGT_EINZAHL_RE = re.compile(
    r"(?<![\wäöüß])(?:der|die|das)\s+(?:einzige[nr]?\s+)?(?:Planet|Kraft|Faktor|Stelle|"
    r"Punkt|Instanz|Endstelle|Endpunkt|Herrscher|Endherrscher)\s*,\s*(?:der|die|das)\s+"
    r"(?:[\wäöüß]+\s+){0,4}$"
    r"|(?<![\wäöüß])(?:als\s+einzige[rsn]?|(?:der|die|das)\s+einzige[rn]?)(?![\wäöüß])"
    r"(?:\s+[\wäöüß]+){0,6}\s*$"
    r"|(?<![\wäöüß])(?:nur|allein)\s+(?:er|sie)\s+(?:[\wäöüß]+\s+){0,2}$"
    r"|(?<![\wäöüß])(?:the\s+only|only)\s+(?:[\w]+\s+){0,4}$", re.I)
_EIGENES_ZEICHEN_RE = re.compile(
    r"^- (?:Enddispositoren \(im eigenen Zeichen[^)]*\)|Im eigenen Zeichen ohne Zulauf "
    r"\([^)]*\)):[ \t]*(?P<liste>[^\n]*)$", re.M)


def _eigenes_zeichen(txt):
    """Strukturbild §3 der chart_data: die Planeten im eigenen Zeichen
    (Enddispositoren und „ohne Zulauf") -> set kanonischer Namen, leer, wenn keiner
    dort steht; None, wenn keine der beiden Zeilen im Text steht (§3 fehlt)."""
    out, gefunden = set(), False
    for m in _EIGENES_ZEICHEN_RE.finditer(txt or ""):
        gefunden = True
        liste = re.sub(r"\([^)]*\)", "", m.group("liste"))     # „(Ketten von …)" weg
        for teil in liste.split(","):
            k = kanon(teil.strip().rstrip(".").strip())
            if k in ANZEIGE:
                out.add(k)
    return out if gefunden else None

# 2026-09-30 (K1, Wartungslauf zu den Pruefberichten vom 29./30.09.): Fundstellen
# fuer zwei Aussagen, die P12 bis dahin ohne Rangzeile meldete, obwohl das
# Strukturbild sie traegt — die Leere eines Quadranten oder einer Hemisphaere (§8,
# Zeile „- Betonung:“, Eintraege „… ⟵ leer“) und das Haus, dessen Herrscher im
# eigenen Haus steht (§3, Hausherrscher-Zeilen mit „⟵ … im eigenen Haus“).
_P12_ZAHL = {"eins": 1, "ein": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "fuenf": 5,
             "sechs": 6, "sieben": 7, "acht": 8, "neun": 9, "zehn": 10, "elf": 11,
             "zwölf": 12, "zwoelf": 12}
_P12_ORDINAL = {"erst": 1, "zweit": 2, "dritt": 3, "viert": 4, "fünft": 5, "fuenft": 5,
                "sechst": 6, "siebt": 7, "siebent": 7, "acht": 8, "neunt": 9, "zehnt": 10,
                "elft": 11, "zwölft": 12, "zwoelft": 12}
_P12_ORDINAL_RE = "(%s)(?:e|en|es|er|em)?" % "|".join(sorted(_P12_ORDINAL, key=len, reverse=True))
_P12_BEREICH = {(1, 3): "Quadrant I", (4, 6): "Quadrant II", (7, 9): "Quadrant III",
                (10, 12): "Quadrant IV", (7, 12): "Hemisphäre über dem Horizont",
                (1, 6): "Hemisphäre unter dem Horizont", (10, 3): "Hemisphäre östlich",
                (4, 9): "Hemisphäre westlich"}
_SELBSTVERWALTUNG_RE = re.compile(
    r"(?<![\wäöüß])(?:verwalte\w*\s+sich|aus\s+sich\s+(?:selbst\s+)?heraus"
    r"|(?:im|in\s+seinem|in\s+ihrem)\s+eigenen\s+(?:Haus|Feld)|regier\w*\s+sich\s+selbst)",
    re.I)


def _p12_nummer(wort):
    w = (wort or "").casefold()
    if w.isdigit():
        return int(w)
    if w in _P12_ZAHL:
        return _P12_ZAHL[w]
    mo = re.fullmatch(_P12_ORDINAL_RE, w)
    return _P12_ORDINAL[mo.group(1)] if mo else None


def _p12_bereich(text):
    """Quadrant oder Hemisphaere, ueber den der Text spricht — in der Schreibweise
    von Strukturbild §8 („Quadrant II", „Hemisphäre über dem Horizont") — oder None."""
    t = text or ""
    mq = re.search(r"Quadrant\w*\s+(IV|I{1,3})(?![\wäöüß])", t)
    if mq:
        return "Quadrant " + mq.group(1)
    mq = re.search(r"(?<![\wäöüß])(erst|zweit|dritt|viert)\w*\s+Quadrant", t, re.I)
    if mq:
        return "Quadrant " + ("I", "II", "III", "IV")[_P12_ORDINAL[mq.group(1).casefold()] - 1]
    for rx in (r"Häuser\w*\s+(\w+)\s*(?:bis|–|-)\s*(\w+)",
               r"(?<![\wäöüß])(\w+)\s+bis\s+(\w+)\s+Haus"):
        mh = re.search(rx, t, re.I)
        if mh:
            a_, b_ = _p12_nummer(mh.group(1)), _p12_nummer(mh.group(2))
            if (a_, b_) in _P12_BEREICH:
                return _P12_BEREICH[(a_, b_)]
    for rx, name in ((r"über\s+dem\s+Horizont|oberhalb\s+des\s+Horizonts",
                      "Hemisphäre über dem Horizont"),
                     (r"unter\s+dem\s+Horizont|unterhalb\s+des\s+Horizonts",
                      "Hemisphäre unter dem Horizont"),
                     (r"östlich\w*\s+(?:Hälfte|Seite|Hemisphäre)|Osthälfte", "Hemisphäre östlich"),
                     (r"westlich\w*\s+(?:Hälfte|Seite|Hemisphäre)|Westhälfte", "Hemisphäre westlich")):
        if re.search(rx, t, re.I):
            return name
    return None


def _p12_hausnummern(text):
    """Hausnummern, die ein Text nennt („dein zweites Haus", „Haus 2", „2. Haus")."""
    out = set()
    for mo in re.finditer(r"(?<![\wäöüß])%s\s+(?:Haus|Hauses|Feld|Feldes)(?![\wäöüß])"
                          % _P12_ORDINAL_RE, text or "", re.I):
        out.add(_P12_ORDINAL[mo.group(1).casefold()])
    for mo in re.finditer(r"(?:Haus|Feld)\s+(\d{1,2})(?!\d)|(\d{1,2})\.\s+(?:Haus|Feld)",
                          text or ""):
        out.add(int(mo.group(1) or mo.group(2)))
    return {h for h in out if 1 <= h <= 12}


def _struktur_p12(txt):
    """{'leer': {…} | None, 'eigenes_haus': {Haus: Herrscher} | None} aus
    Strukturbild §8 und §3 der chart_data; None heisst: der Abschnitt fehlt."""
    out = {"leer": None, "eigenes_haus": None}
    m8 = re.search(r"### 8 · Verteilung.*?(?=\n### |\Z)", txt or "", re.S)
    if m8:
        out["leer"] = set()
        mb = re.search(r"^- Betonung:\s*(.*)$", m8.group(0), re.M)
        for teil in (mb.group(1).split(";") if mb else []):
            teil = teil.strip().rstrip(".").strip()
            if teil.endswith("⟵ leer"):
                out["leer"].add(teil[:-len("⟵ leer")].strip())
        for mq in re.finditer(r"(IV|I{1,3}) \(Häuser [^)]*\) 0(?!\d)", m8.group(0)):
            out["leer"].add("Quadrant " + mq.group(1))
    m3 = re.search(r"### 3 · Herrscherketten.*?(?=\n### |\Z)", txt or "", re.S)
    if m3:
        out["eigenes_haus"] = {}
        for mz in re.finditer(r"^\s*- Haus\s+(\d+) \([^)]*\) → (\S+) in [^\n]*⟵[^\n]*"
                              r"im eigenen Haus", m3.group(0), re.M):
            out["eigenes_haus"][int(mz.group(1))] = mz.group(2)
    return out

def _hat_referent(satz):
    """Spricht der Satz ueber das Chart? Nur dann ist ein Rangwort eine Aussage,
    die eine Zahl braucht („die engste Verbindung deines Bildes" — nicht „deine
    engsten Freunde")."""
    return bool(_REFERENT_RE.search(satz) or _REFERENT_EN_RE.search(satz)
                or _faktoren_im_satz(satz) or _ELEMENT_RE.search(satz)
                or _MODUS_RE.search(satz) or ASPEKT_RE.search(satz)
                or re.search(r"(?<![\wäöüß])%s(?![\wäöüß])" % ZEICHEN_RE, satz))

def _rang_txt(e):
    if "a" in e:
        return "%d. %s %s %s %s" % (e["rang"], e["a"], e["aspekt"], e["b"], e["orb"])
    if "faktor" in e:
        return "%d. %s %g" % (e["rang"], e["faktor"], e["wert"])
    return "%d. %s %g von %g = %d %% (%s)" % (e["rang"], e["name"], e["wert"], e["summe"],
                                             e["prozent"], ", ".join(n for n, _ in e["traeger"]))

def _achs_norm(f):
    """Achsen-Spiegel auf ein Ende (DC -> AC, IC -> MC) — fuer Rangvergleiche."""
    return {"DC": "AC", "IC": "MC"}.get(f, f)

def _rang_paar(e):
    return frozenset((_achs_norm(kanon(e["a"])), _achs_norm(kanon(e["b"]))))

def _rang_einmal(ls):
    """Achsen-Spiegel mit gleichem Orb (Mondknoten Trigon AC / Mondknoten Sextil DC)
    sind EIN Kontakt und belegen einen Rang, nicht zwei."""
    out, gesehen = [], set()
    for e in ls:
        art = e["aspekt"]
        if kanon(e["a"]) in ("DC", "IC") or kanon(e["b"]) in ("DC", "IC"):
            art = SPIEGEL_ASPEKT.get(art, art)
        k = (_rang_paar(e), art, e["orb_min"])
        if k not in gesehen:
            gesehen.add(k)
            out.append(e)
    return out

def _paare_von(fak):
    return {frozenset((_achs_norm(a), _achs_norm(b))) for i, a in enumerate(fak)
            for b in fak[i + 1:] if _achs_norm(a) != _achs_norm(b)}

# Wie ein Satz die Zaehlmenge „nur Planetenpaare" benennen kann — technisch
# („Planetenpaar") und im Klartext („deiner zehn Hauptkraefte"). Chris-
# Entscheidung 2026-09-22: Ein Rang- oder Superlativsatz NENNT seine Zaehlmenge;
# diese Probe muss sie deshalb lesen koennen.
_P12_PLANETENMENGE_RE = re.compile(
    r"Planetenpaar"
    r"|zwischen\s+(?:zwei\s+)?(?:deiner\s+)?(?:zehn\s+)?Planeten"
    r"|unter\s+(?:den|deinen)\s+(?:zehn\s+)?Planeten"
    r"|Planeten\s+untereinander"
    r"|(?:deiner|den|die|zwei)\s+zehn\s+Hauptkräfte(?:n)?"
    r"|zwischen\s+zwei\s+(?:deiner\s+)?(?:zehn\s+)?Hauptkräfte(?:n)?", re.I)


# 2026-09-29 (K2): Aufzaehlung, die gleich hinter einer Zahl beginnt.
_AUFZ_LUECKE_RE = re.compile(r"\s*(?:,|und|sowie|oder)\s+(?:(?:zu|zum|zur|mit|mein\w*|"
                             r"dein\w*|der|die|das|dem|den|des)\s+)*", re.I)


def _aufzaehlung_danach(satz, pos, objekte=False):
    """Faktoren der Aufzaehlung, die gleich hinter `pos` beginnt: hoechstens
    ein Wort davor („drei Kräfte: …“), oder hinter einem Doppelpunkt oder
    Gedankenstrich. Objekte („zu Mars und zu Venus“) nur mit `objekte` — sonst
    sind sie Partner, nicht die gezaehlten Kraefte. [] ohne solche Aufzaehlung."""
    fs = [(a, e, f) for a, e, f in _faktoren_im_satz(satz) if a >= pos]
    if not fs:
        return []
    art_ = r"(?:(?:mein\w*|dein\w*|der|die|das|dem|den|des)\s+)?"
    luecke = satz[pos:fs[0][0]]
    ok = (re.fullmatch(r"\s*(?:[\wäöüß]+\s*)?[:—–,]?\s*" + art_, luecke, re.I)
          or re.search(r"[:—–]\s*" + art_ + r"$", luecke, re.I))
    if objekte:
        ok = ok or re.fullmatch(r"\s*(?:[\wäöüß]+\s*)?[:—–,]?\s*(?:zu|zum|zur|mit)\s+" + art_,
                                luecke, re.I)
    elif _OBJEKT_VOR_RE.search(satz[max(0, fs[0][0] - 30):fs[0][0]]):
        ok = False
    if not ok:
        return []
    out = [fs[0][2]]
    for (_a0, e0, _f0), (a1, _e1, f1) in zip(fs, fs[1:]):
        if not _AUFZ_LUECKE_RE.fullmatch(satz[e0:a1]):
            break
        out.append(f1)
    return out


_P12_TEILMENGE_RE = re.compile(
    r"(?<![\wäöüß])(?:unter\s+(?:(?:ihren|seinen|deren|dessen|diesen|den|deinen)\s+"
    r"(?:[\wäöüß]+\s+)?(?:Gliedern|Ecken|Mitgliedern|Beteiligten)|ihnen|diesen\s+(?:drei|"
    r"vier|fünf|sechs)\w*|den\s+(?:drei|vier|fünf|sechs)en)"
    r"|innerhalb\s+(?:der|dieser|des|dieses|ihrer|seiner|deiner)\s+[\wäöüß]+"
    r"|in\s+(?:dieser|der|seiner|ihrer)\s+(?:Ballung|Figur|Gruppe|Konstellation|Kette))"
    r"(?![\wäöüß])", re.I)


def _rang_befund(art, m, satz, rz, typ, vorher="", eigen=None, struktur=None, englisch=False):
    """None, wenn die Rangzeile die Aussage traegt; sonst der Befundtext.
    englisch: der Satz stammt aus einer englischen Fassung — dann liest die
    Einzigkeitsaussage Element und Modus englisch, und die Zaehlung kennt die
    englischen Woerter (2026-10-12, W1).
    vorher: der Satz davor (Bezug von „Das ist die engste Verbindung …").
    eigen: die Planeten im eigenen Zeichen aus Strukturbild §3 (`_eigenes_zeichen()`,
    None: §3 fehlt), Fundstelle fuer „der Planet, der keinem anderen folgt" (2026-09-24).
    struktur: `_struktur_p12()` — leere Bereiche aus §8 und Haeuser, deren Herrscher im
    eigenen Haus steht, aus §3 (2026-09-30)."""
    if not rz:
        return ("Rang-, Zähl- oder Einzigkeitsaussage — das Datenblatt hat keine Rangzeilen "
                "(Strukturbild §10, seit 2026-09-19); die Zahl von Hand gegen die Tabellen halten")
    if typ == "transit" and re.search(r"laufend|Transit|Kontakt|Stichtag", satz):
        return ("Rangwort über Transit-Kontakte — die Rangzeilen gelten der Radix; gegen "
                "Jetzt-Liste und events.json halten")
    # 2026-09-29 (Klasse-2-Entscheidungslauf K2, Chris: Frage 2 = a): Eine
    # Zahl, die genau die gleich danach genannten Kraefte zaehlt („alle drei:
    # Mond, Mars und Pluto“), ist keine Zaehlung des Bildes. Bei „n Verbindungen“
    # nur die Teilmenge („zwei leise Verbindungen, zu Mars und zu Venus“) — die
    # Gesamtzahl bleibt eine Aussage ueber das Bild. Ob die Paare stimmen, prueft P13.
    if art in ("alle_n", "n_verbindungen"):
        _w = m.groupdict().get("n") if art == "n_verbindungen" else m.group(0).split()[-1]
        _n = _zahl_wert(_w) if _w else None
        _teil = re.match(r"\S+\s+[\wäöüß]+\s+Verbindung", m.group(0), re.I)
        if _n and _n >= 2 and (art == "alle_n" or _teil) and _n == len(set(
                _aufzaehlung_danach(satz, m.end(), objekte=(art == "n_verbindungen")))):
            return None
    g = m.groupdict()
    fak = [f for _, _, f in _faktoren_im_satz(satz)]
    fak_v = [f for _, _, f in _faktoren_im_satz(vorher)] if vorher else []
    # 2026-09-30 (Wartungslauf zu den Pruefberichten vom 29./30.09., K1): Zwei
    # Aussagen in einem Satz, durch Semikolon getrennt — Element, Modus und
    # Zaehlweise gelten fuer das Glied, in dem das Rangwort steht. Vorher hielt die
    # Probe einen Anteil im zweiten Glied („…; die Hälfte aller Planeten steht in der
    # Kraft, …“) gegen das Element des ersten und „Die meisten Verbindungen, gezählt
    # …; gewichtet …“ gegen die gewichtete Zeile.
    # Nennt das Glied nichts, gilt weiter der ganze Satz.
    _k0 = satz.rfind(";", 0, m.start()) + 1
    _k1 = satz.find(";", m.end())
    klausel = satz[_k0:] if _k1 < 0 else satz[_k0:_k1]
    # 2026-10-01 (Pruefbericht Geburtshoroskop 1+2 vom 30.09., K1): Ein Rang INNERHALB
    # einer Gruppe („unter ihren Gliedern … die meisten Verbindungen“ — so verlangt
    # es die Figur-Regel) meint eine Teilmenge; die
    # Rangzeilen tragen nur die Gesamtmenge. Kein Befund — „unter allen Planeten“ und
    # „unter den zehn Planeten“ bleiben geprueft.
    if art in ("engste", "meiste", "wenigste") and _P12_TEILMENGE_RE.search(klausel):
        return None
    me = _ELEMENT_RE.search(klausel)
    mm = _MODUS_RE.search(klausel)
    if not (me or mm) and klausel != satz:
        me, mm = _ELEMENT_RE.search(satz), _MODUS_RE.search(satz)
    if not (me or mm) and art in ("einzig", "kein_anderer", "x_von_y", "haelfte") and vorher \
            and re.search(r"Planet|Faktor|Element|Zeichen", satz):
        me, mm = _ELEMENT_RE.search(vorher), _MODUS_RE.search(vorher)
    element = ({"Erd": "Erde"}.get(me.group(1) or me.group(2), me.group(1) or me.group(2))
               if me else None)
    modus = _modus_name(mm) if mm else None
    # 2026-10-12 (Nacharbeiten Englisch, W1): Bei der Einzigkeit gilt zuerst das Element
    # oder der Modus HINTER dem Einzigkeitswort (_em_hinter) — im Glied bis Semikolon,
    # Doppelpunkt, Gedankenstrich oder einem Komma, hinter dem kein Relativsatz beginnt.
    # Deutsch sonst wie bisher das ganze Glied; englisch NUR dieser Ausdruck.
    if art == "einzig":
        _hinter = re.split(r"[;:]|\s[—–]\s|[—–]|,(?!\s*(?:die|der|das|welche\w*|that|which|who)"
                           r"(?![\wäöüß]))", satz[m.end():len(satz) if _k1 < 0 else _k1],
                           maxsplit=1, flags=re.I)[0]
        _em = _em_hinter(_hinter, englisch)
        if _em != (None, None) or englisch:
            element, modus = _em

    def liste(schl):
        return [e for e in rz.get(schl, {}).get("eintraege", []) if "rang" in e]

    def zaehlungen():
        """Welche Zaehlung meint der Satz? Keine Angabe: beide muessen es tragen."""
        # 2026-09-29 (Klasse-2-Entscheidungslauf K1, GH12-29b Nr. 5): „Gewichtet
        # gezählt, …" und „Gewichtet, …" am Satzanfang gelten fuer den ganzen
        # Satz — vorher fiel das eine auf „gezählt" durch, das andere auf
        # „Planet". „Gewichtet ist X der am dichtesten verschaltete …" bleibt
        # wie bisher (das Adverb gilt dort dem Rang, nicht jedem Satzglied).
        # 2026-10-12 (W1): Bei der Einzigkeit („einzig“, „kein anderer“) nennt auch
        # „Hauptkraft“/„zehn Hauptkräfte“ die Zählmenge der Planeten — eine Teilmenge der zehn
        # ist gezählt wie gewichtet dieselbe; bei Anteilen nicht, dort bleibt es wie bisher
        # (Zweitprüfung: „Gewichtet steht die Hälfte deiner zehn Hauptkräfte …“). Englisch
        # dieselben Wörter.
        _einz = art in ("einzig", "kein_anderer")
        _en_gew = r"(?<!\w)weighted(?!\w)"
        _en_gez = r"(?<!\w)(?:counted|of\s+ten|planets?" + (r"|main\s+forces?" if _einz else "") + r")(?!\w)"
        _en_fak = r"(?<!\w)factors?(?!\w)"
        _de_gez = r"gezählt|von\s+zehn|Planet" + (r"|Hauptkr[aä]ft" if _einz else "")
        s_ = (klausel if re.search(r"gewichtet|gezählt|von\s+zehn|Planet|Faktor|Punkt|Stelle"
                                   + (r"|Hauptkr[aä]ft" if _einz else "")
                                   + ("|" + "|".join((_en_gew, _en_gez, _en_fak)) if englisch else ""),
                                   klausel, re.I) else satz)             # 2026-09-30 (K1)
        # Bei der Einzigkeit geht die genannte Planetenmenge vor „gewichtet“: Unter den zehn
        # ist der Träger gezählt wie gewichtet derselbe („Gewichtet, ist Saturn unter deinen
        # zehn Hauptkräften die einzige im Feuer“ — Zweitprüfung).
        if _einz and (re.search(r"Planet|Hauptkr[aä]ft", s_)
                      or englisch and re.search(r"(?<!\w)(?:planets?|main\s+forces?)(?!\w)", s_, re.I)):
            return ["gezaehlt"]
        if re.search(r"^\W*Gewichtet(?:\s+gezählt)?\s*,|[Gg]ewichtet\s+gezählt", s_):
            return ["gewichtet"]
        if re.search(r"gewichtet", s_):
            return ["gewichtet"]
        if englisch and re.search(_en_gew, s_, re.I):
            return ["gewichtet"]
        if re.search(_de_gez, s_):
            return ["gezaehlt"]
        if englisch and re.search(_en_gez, s_, re.I):
            return ["gezaehlt"]
        if re.search(r"Faktor|Punkt|Stelle", s_):
            return ["gewichtet"]
        if englisch and re.search(_en_fak, s_, re.I):
            return ["gewichtet"]
        return ["gezaehlt", "gewichtet"]

    def verteilung(name, fam, zl=None):
        return [(a, next((e for e in liste("%s-%s" % (fam, a)) if e["name"] == name), None))
                for a in (zl or zaehlungen())]

    if art == "engste":
        n = g.get("n") or g.get("n2")
        grenze = (2 if n.lower() == "beiden" else _zahl_wert(n)) if n else None
        eine = bool(g.get("eine")) or bool(g.get("n2"))
        k = {"zweit": 2, "dritt": 3, "viert": 4}.get((g.get("ord") or "").lower(), 1)
        # 2026-09-22: Bis dahin traf das Muster nur drei Formulierungen. Ein
        # Satz „das engste Planetenpaar" und die Klartext-Form „zwischen zwei
        # deiner zehn Hauptkraefte" wurden gegen `engste-aspekte` gehalten —
        # also gegen die falsche Menge — und korrekte Saetze mussten
        # umgeschrieben werden (Prueflaeufe Geburtshoroskop 1+2 vom 2026-09-22,
        # Nr. 9, und 2026-09-22b, Nr. 6).
        schl = ("engste-aspekte-planeten" if _P12_PLANETENMENGE_RE.search(satz)
                else "engste-aspekte")
        # Einschraenkungen aus den drei Woertern hinter dem Rangwort
        # („die engste harmonische Verbindung", „die zweitengste volle Reibung",
        # „die engste Winkel-Spannung", „die engste Konjunktion").
        nach = re.findall(r"[\wäöüÄÖÜß-]+", satz[m.end():])[:3]
        arten = {_art(w) for w in nach if w in _ASP_WORT}
        filt = []
        if arten:
            filt.append(("nur " + "/".join(sorted(arten)), lambda e: e["aspekt"] in arten))
        if any(w.lower().startswith("harmonisch") for w in nach):
            filt.append(("harmonisch", lambda e: e["aspekt"] in ("Trigon", "Sextil")))
        if any(re.match(r"(?:Winkel-)?(?:Spannung|Reibung)|spannungsvoll", w, re.I) for w in nach):
            filt.append(("Spannung", lambda e: e["aspekt"] in ("Quadrat", "Opposition",
                                                               "Halbquadrat", "Anderthalbquadrat")))
        if any(w.lower().startswith("winkel") for w in nach):
            filt.append(("an einem Winkel", lambda e: kanon(e["a"]) in ACHSEN or kanon(e["b"]) in ACHSEN))
        if any(w.lower() in ("voll", "volle", "vollen", "voller", "volles", "vollem") for w in nach):
            filt.append(("voll", lambda e: e["staerke"] == "voll"))
        ls = _rang_einmal([e for e in liste(schl) if all(f(e) for _, f in filt)])
        beschr = schl + (" (%s)" % ", ".join(n_ for n_, _ in filt) if filt else "")

        def rang(e):
            return 1 + sum(1 for x in ls if x["orb_min"] < e["orb_min"])
        paare = _paare_von(fak) or _paare_von(fak + fak_v)
        treffer = [e for e in ls if _rang_paar(e) in paare]
        oben = [e for e in ls if rang(e) == k]
        if not treffer:
            if not paare:
                return ("Rangaussage ohne benanntes Paar in diesem oder dem vorigen Satz — "
                        "Rangzeile %s, Rang %d: %s"
                        % (beschr, k, "; ".join(_rang_txt(e) for e in oben) or "—"))
            return ("kein Paar dieses Satzes unter den Rängen der Rangzeile %s — Rang %d: %s"
                    % (beschr, k, "; ".join(_rang_txt(e) for e in oben) or "—"))
        e = min(treffer, key=rang)
        r = rang(e)
        if eine:
            if grenze is None or r <= grenze:
                return None
            return ("%s steht auf Rang %d der Rangzeile %s — „eine der %d engsten“ trägt "
                    "nur Rang %d oder besser" % (_rang_txt(e).split(". ", 1)[1], r, beschr,
                                                   grenze, grenze))
        gleich = [x for x in ls if rang(x) == r and x is not e]
        if r == k and not gleich:
            return None
        if r == k:
            return ("Gleichstand auf Rang %d der Rangzeile %s (%s) — richtig ist „eine der "
                    "engsten“" % (k, beschr, "; ".join(_rang_txt(x) for x in [e] + gleich)))
        return ("%s steht auf Rang %d der Rangzeile %s — Rang %d: %s"
                % (_rang_txt(e).split(". ", 1)[1], r, beschr, k,
                   "; ".join(_rang_txt(x) for x in oben) or "—"))
    _kop = re.search(r"(?<![\wäöüß])(ist|sind|bildet|bilden|ergibt|ergeben|wird|"
                     r"werden|als)\s+eine\s+$", satz[:m.start()], re.I)
    if art == "einzig" and _kop \
            and re.match(r"\w*\s+Figur(?![\wäöüß])(?!\s+zu\s)", satz[m.start():]) \
            and not (_kop.group(1).lower() in ("ist", "sind") and re.match(
                r"\s*(?:in|im|bei|beim|auf|an|am)\s",
                re.split(r"[.;:,]", satz[:_kop.start()])[-1], re.I)):
        # 2026-09-29 (K1): „es ist eine einzige Figur“ — die Gleichsetzung
        # traegt §6 (Figur-Entscheidung); „trägt eine einzige Figur“ bleibt PRUEFEN.
        return None
    if art in ("einzig", "kein_anderer"):
        if art == "kein_anderer" and any(x.start() <= m.start() < x.end()
                                         for x in _FOLGT_KEINEM_RE.finditer(satz)):  # 2026-09-24, §3
            ziel = set(fak)
            pm = _PRONOMEN_ANFANG_RE.match(satz)
            if pm:
                ziel |= set(_pronomen_bezug(pm.group(1), "", vorher) or fak_v[-1:])
            elif not ziel:
                ziel |= set(fak_v)
            dort = ((", ".join(ANZEIGE.get(x, x) for x in sorted(eigen)) or "keiner")
                    if eigen is not None else "— (§3 nicht gefunden)")
            # 2026-09-25: Einzahl gegen Eigenschaft (s. _FOLGT_EINZAHL_RE)
            if _FOLGT_EINZAHL_RE.search(satz[max(0, m.start() - 90):m.start()]):
                if eigen and eigen <= ziel:
                    return None
                return ("„folgt keinem anderen“ in der Einzahl („der Planet, der …“, „als "
                        "einziger“) — Strukturbild §3, im eigenen Zeichen: %s; der Satz nennt "
                        "%s. Stehen dort mehrere, alle nennen oder die Einzahl auflösen"
                        % (dort, ", ".join(ANZEIGE.get(x, x) for x in sorted(ziel))
                           or "keinen Planeten"))
            vor_f = [f for a_, _e, f in sorted(_faktoren_im_satz(satz)) if a_ < m.start()]
            wer = set(vor_f[-1:]) or ziel       # der genannte Planet davor, sonst der Bezug
            if eigen and wer and wer <= eigen:
                return None
            return ("„folgt keinem anderen“ — %s steht nicht unter den Planeten im eigenen "
                    "Zeichen (Strukturbild §3: %s)"
                    % (", ".join(ANZEIGE.get(x, x) for x in sorted(wer)) or "kein genannter Planet",
                       dort))
        null = art == "einzig" and re.search(r"kein\w*\s+$", satz[max(0, m.start() - 12):m.start()])
        if element or modus:
            name, fam = (element, "elemente") if element else (modus, "modi")
            werte = [(a, e) for a, e in verteilung(name, fam) if e]
            if not werte:
                return "keine Rangzeile für %s gefunden" % name
            # 2026-10-12 (W1): Still nur, wenn der genannte Planet der Träger ist — nennt
            # der Satz mehrere Faktoren, müssen sie genau der Träger sein. Vorher genügte bei
            # zwei Faktoren irgendeiner („Neben Venus ist Saturn die einzige im Feuer“, „Venus
            # ist die einzige im Feuer und Saturn die einzige …“ blieben still). Ohne Faktor
            # im Satz holt ein Pronomen vor dem Einzigkeitswort („er“, „sie“, „dieser“,
            # „it“, „this“, „That …“) seinen Bezug aus dem Vorsatz; mehrere Kandidaten
            # müssen alle der Träger sein. Ohne Faktor und ohne Pronomen genügt die Zählung 1.
            # Eine Achse neben einem Planeten („Saturn … am MC“) ist kein zweiter Kandidat:
            # In der gezählten Zeile steht nie eine Achse (Zweitprüfung).
            genannt, pron = (set(fak) - set(ACHSEN)) or set(fak), None
            if not genannt:
                _vp = satz[:m.start()]
                _pm = (re.search(r"(?<!\w)(it|he|she|this)(?!\w)|^\W*(That)(?!\w)", _vp, re.I)
                       if englisch else
                       re.search(r"(?<![\wäöüß])(er|sie|dieser|diese|jener|jene)(?![\wäöüß])", _vp, re.I))
                if _pm:
                    pron = next(g for g in _pm.groups() if g)
                    _kand = set(_einzig_bezug(pron, vorher, englisch))
                    genannt = (_kand - set(ACHSEN)) or _kand
            falsch = []
            for a, e in werte:
                traeger = [kanon(n_) for n_, _ in e["traeger"]]
                ok = (not traeger) if null else (
                    len(traeger) == 1 and (genannt == {traeger[0]} if (genannt or pron) else True))
                if ok:
                    continue
                _rt = _rang_txt(e).split(". ", 1)[1]
                if not null and len(traeger) == 1 and genannt:
                    falsch.append("%s-%s: %s — der Satz nennt %s" % (
                        fam, a, _rt, ", ".join(ANZEIGE.get(x, x) for x in sorted(genannt))))
                elif not null and len(traeger) == 1 and pron:
                    falsch.append("%s-%s: %s — „%s“ findet im Satz davor keinen Planeten"
                                  % (fam, a, _rt, pron))
                else:
                    falsch.append("%s-%s: %s — %d Träger" % (fam, a, _rt, len(traeger)))
            if not falsch:
                return None
            gilt = [a for a, e in werte if "%s-%s:" % (fam, a) not in " ".join(falsch)]
            return ("Rangzeile %s%s" % ("; ".join(falsch), " — gilt nur %s; die Zählung nennen"
                                        % gilt[0] if gilt else ""))
        # 2026-09-30 (K1): „Die Häuser sieben bis neun tragen keinen einzigen Planeten“
        # — die Leere eines Quadranten oder einer Hemisphäre steht in Strukturbild §8
        if null:
            _ber = _p12_bereich(klausel)
            if _ber:
                _leer = (struktur or {}).get("leer")
                if _leer is None:
                    return "Leere-Aussage über %s — Strukturbild §8 nicht gefunden" % _ber
                if _ber in _leer:
                    return None
                return ("Leere-Aussage über %s — Strukturbild §8 nennt leer: %s"
                        % (_ber, ", ".join(sorted(_leer)) or "keinen Bereich"))
        # 2026-09-30 (K1): „Dein zweites Haus verwaltet sich aus sich heraus“ + „kein
        # anderer“ — der Hausherrscher im eigenen Haus steht in Strukturbild §3
        if art == "kein_anderer" and _SELBSTVERWALTUNG_RE.search(satz + " " + (vorher or "")):
            _eh = (struktur or {}).get("eigenes_haus")
            if _eh is None:
                return ("„keinen anderen“ bei einem Haus, das sich selbst verwaltet — "
                        "Strukturbild §3 (Hausherrscher) nicht gefunden")
            _gen = _p12_hausnummern(satz) or _p12_hausnummern(vorher or "")
            if _eh and (not _gen or _gen <= set(_eh)):
                return None
            return ("„keinen anderen“ bei einem Haus, das sich selbst verwaltet — Strukturbild "
                    "§3 nennt im eigenen Haus: %s"
                    % (", ".join("Haus %d (%s)" % (h_, _eh[h_]) for h_ in sorted(_eh))
                       or "keinen Hausherrscher"))
        if re.match(r"\s*(?:[\wäöüß]+\s+)?(?:Verbindung|Aspekt)", satz[m.end():], re.I):
            # „Jupiter mit einer einzigen Verbindung" — der Faktor steht davor oder im
            # selben Satzglied dahinter; „eine einzige Verbindung: die zwischen Neptun
            # und Pluto" zaehlt keine Verbindungen eines Faktors.
            vor = [f for a_, e_, f in _faktoren_im_satz(satz) if a_ < m.start()]
            glied = re.split(r"[:;—–]", satz[m.end():], 1)[0]
            nach = [f for _, _, f in _faktoren_im_satz(glied)]
            if re.match(r"\s*(?:[\wäöüß]+\s+)?(?:Verbindungen|Aspekte)(?![\wäöüß])",
                        satz[m.end():], re.I):
                # 2026-09-29 (K1, GH12-29c Nr. 3): Plural — so viele Verbindungen,
                # wie das Satzglied Partner nennt; Traeger davor oder im Vorsatz.
                # Traeger: der Faktor davor im Satz, sonst der Bezug des
                # Possessivs („ihre“ weiblich, „seine“ maennlich) im Vorsatz;
                # still nur, wenn JEDER Kandidat die Zahl traegt (Zweitpruefung).
                pm_ = re.search(r"(?<![\wäöüß])(ihr\w*|sein\w*)\s+$", satz[:m.start()], re.I)
                traeger = vor[-1:] or (
                    _pronomen_bezug("sie" if pm_.group(1).lower().startswith("ihr") else "er",
                                    "", vorher) if pm_ else list(dict.fromkeys(reversed(fak_v))))
                def _traegt(t_):
                    n_ = len(set(nach) - {t_})
                    gz_ = next((e for e in liste("verbindungen-gezaehlt")
                                if kanon(e["faktor"]) == t_), None)
                    return gz_ is not None and n_ in (gz_["wert"], gz_["aspekttabelle"]
                                                      or gz_["wert"])
                if traeger and all(_traegt(t_) for t_ in traeger):
                    return None
                return ("Einzigkeitsaussage im Plural — der Satz nennt %d Partner; Rangzeile "
                        "verbindungen-gezaehlt des Faktors davor bzw. im Vorsatz halten"
                        % len(set(nach)))
            f = vor[-1] if vor else (nach[0] if nach else None)
            gz = next((e for e in liste("verbindungen-gezaehlt") if f and kanon(e["faktor"]) == f), None)
            if gz is not None:
                if 1 in (gz["wert"], gz["aspekttabelle"] or gz["wert"]):
                    return None
                return ("Rangzeile verbindungen-gezaehlt: %s %s%s — nicht eine"
                        % (ANZEIGE.get(f, f), gz["wert"], " (Aspekttabelle %d)" % gz["aspekttabelle"]
                           if gz["aspekttabelle"] else ""))
        return "Einzigkeitsaussage ohne passende Rangzeile — gegen Tabellen und Strukturbild halten"
    if art == "x_von_y":
        x = _zahl_wert(m.group("x")) or (1 if m.group("x").lower().startswith("ein") else None)
        y = _zahl_wert(m.group("y"))
        if (element or modus) and x is not None and y is not None:
            name, fam = (element, "elemente") if element else (modus, "modi")
            werte = [(a, e) for a, e in verteilung(name, fam, ["gezaehlt", "gewichtet"]) if e]
            if any(abs(e["wert"] - x) < 1e-9 and abs(e["summe"] - y) < 1e-9 for _, e in werte):
                return None
            return "Rangzeilen: %s" % "; ".join("%s-%s %s" % (fam, a, _rang_txt(e).split(". ", 1)[1])
                                                for a, e in werte)
        return ("Zählaussage ohne passende Rangzeile (Hemisphären und Quadranten stehen in "
                "Strukturbild §8) — von Hand prüfen")
    if art in ("meiste", "wenigste"):
        eine = bool(g.get("mit"))           # „mit die meisten": einer der ersten drei Ränge
                                            # („der Faktor mit den meisten" bleibt Rang 1 allein)
        # 2026-09-24 (Geburtshoroskop 1+2 vom 24.09., Nr. 2.2; 3+4b): Spricht das
        # Rangwort selbst von Verbindungen („am dichtesten verschaltete", „die meisten
        # Verbindungen"), gilt die Verbindungs-Rangzeile — auch wenn anderswo im Satz ein
        # Element steht („…, und die Luft in dir hat keinen anderen Planeten als ihn").
        verbindung = (re.search(r"verschalt|verbunden|vernetzt|angebunden", m.group(0), re.I)
                      or re.match(r"\s+(?:[\wäöüß]+\s+){0,2}?(?:Verbindung|Aspekt|Kontakt|Verkehr)",
                                  satz[m.end():], re.I))
        if (element or modus) and not verbindung:
            name, fam = (element, "elemente") if element else (modus, "modi")
            schl = ["%s-%s" % (fam, a) for a in zaehlungen()]
            gemeint = [name]
        else:
            gemeint = fak or fak_v
            if not gemeint:
                return "Rangaussage ohne Faktor in diesem oder dem vorigen Satz — von Hand prüfen"
            # 2026-09-30 (K1): im Glied des Rangworts; ein ausdrückliches „gezählt“
            # geht vor, und „dicht gefolgt“ ist kein Dichtemaß
            if re.search(r"gezählt", klausel) and not re.search(r"gewichtet", klausel, re.I):
                schl = ["verbindungen-gezaehlt"]
            else:
                schl = (["verbindungen-gewichtet"]
                        if re.search(r"verschalt|dicht(?!\s+gefolgt)|Verkehr|vernetzt|gewichtet",
                                     klausel, re.I)
                        else ["verbindungen-gezaehlt"])
        falsch = []
        for s_ in schl:
            ls = liste(s_)
            if not ls:
                falsch.append("Rangzeile %s fehlt im Datenblatt" % s_)
                continue
            ziel = ls[0]["rang"] if art == "meiste" else ls[-1]["rang"]
            oben = [e for e in ls if e["rang"] == ziel]
            namen = {kanon(e.get("faktor") or e.get("name") or "") for e in oben} | \
                {e.get("name") for e in oben}
            if eine and art == "meiste":
                vorn = {kanon(e.get("faktor") or e.get("name") or "") for e in ls if e["rang"] <= 3} | \
                    {e.get("name") for e in ls if e["rang"] <= 3}
                if any(x in vorn for x in gemeint):
                    continue
            elif len(oben) == 1 and any(x in namen for x in gemeint):
                continue
            falsch.append("Rangzeile %s — %s Rang: %s" % (s_, "erster" if art == "meiste" else "letzter",
                                                          "; ".join(_rang_txt(e) for e in oben)))
        return "; ".join(falsch) if falsch else None
    if art == "haelfte":
        if not (element or modus):
            return "Anteilsaussage ohne Element oder Modus — von Hand prüfen"
        name, fam = (element, "elemente") if element else (modus, "modi")
        vgl = (m.group("vgl") or "").lower()

        def ok(pz):
            if m.group("proz"):
                return abs(pz - int(m.group("proz"))) <= 1
            if m.group("drittel"):
                return abs(pz - (33 if m.group("drittel").lower() == "ein" else 67)) <= 3
            ca = (m.groupdict().get("ca") or "").lower()      # 2026-09-29 (K1)
            if ca in ("fast", "knapp", "beinahe", "nahezu"):
                return 40 <= pz < 50
            if ca == "gut":
                return 50 < pz <= 60
            if ca:
                return 45 <= pz <= 55
            return pz > 50 if vgl == "mehr" else pz < 50 if vgl == "weniger" else pz == 50
        werte = [(a, e) for a, e in verteilung(name, fam) if e]
        passt = [a for a, e in werte if ok(e["prozent"])]
        if werte and len(passt) == len(werte):
            return None
        return ("Rangzeilen %s: %s%s" % (name, "; ".join("%s %d %%" % (a, e["prozent"]) for a, e in werte),
                                         " — gilt nur %s; die Zählung nennen" % passt[0] if passt else ""))
    if art == "n_verbindungen":
        # 2026-09-25 (Geburtshoroskop 1+2 vom 25.09., 1.2): Ein Wort zwischen Zahl und
        # „Verbindung" („drei weitere", „zwei leise") zaehlt eine Teilmenge, die keine
        # Rangzeile traegt. Vorher lief der Satz gegen die Gesamtzahl und bekam bei
        # zufaellig gleichem Wert „gewichtete Dichte als Anzahl gelesen" — ein falscher
        # Grund; der richtige ist die Zaehlregel des Typmoduls.
        if g.get("n") and re.match(r"\S+\s+[\wäöüß]+\s+Verbindung", m.group(0), re.I):
            return ("Zählaussage über eine Teilmenge („%s“) — keine Rangzeile trägt sie; "
                    "außerhalb des Getriebes bleiben Zählungen im Beleg (Typmodul, "
                    "„Zählungen IM Fließtext“)" % _ws(m.group(0)))
        n = _zahl_wert(g["n"]) if g.get("n") else 1
        vor = [f for a_, e_, f in _faktoren_im_satz(satz) if a_ < m.start()]
        f = vor[-1] if vor else (fak[0] if fak else (fak_v[-1] if fak_v else None))
        if f is None or n is None:
            return "Zählaussage ohne Faktor — von Hand prüfen"
        gz = next((e for e in liste("verbindungen-gezaehlt") if kanon(e["faktor"]) == f), None)
        gw = next((e for e in liste("verbindungen-gewichtet") if kanon(e["faktor"]) == f), None)
        if gz and n in (gz["wert"], gz["aspekttabelle"] or gz["wert"]):
            return None
        if gw and abs(gw["wert"] - n) < 1e-9:
            return ("gewichtete Dichte als Anzahl gelesen — %s gezählt %s%s, gewichtet %g"
                    % (ANZEIGE.get(f, f), gz["wert"] if gz else "?",
                       " (Aspekttabelle %d)" % gz["aspekttabelle"] if gz and gz["aspekttabelle"] else "",
                       gw["wert"]))
        return ("Rangzeile verbindungen-gezaehlt: %s %s%s — eine Teilmenge (nur die harmonischen, "
                "nur die engen …) von Hand zählen"
                % (ANZEIGE.get(f, f), gz["wert"] if gz else "—",
                   " (Aspekttabelle %d)" % gz["aspekttabelle"] if gz and gz["aspekttabelle"] else ""))
    return "Zählaussage — von Hand gegen Tabellen und Strukturbild halten"

def _p12_rang(chapters, txt, typ=None, sprache_analyse="de"):
    p = _Probe("P12", "Rang- und Einzigkeitswörter")
    p.einheit = "Aussagen"
    # 2026-09-22 (W57-Nachzug): englische Musterliste statt Uebersprung. Die Arten
    # heissen wie im Deutschen, deshalb bleibt `_rang_befund()` unveraendert.
    englisch = (sprache_analyse != "de")
    MUSTER = _RANG_MUSTER_EN if englisch else _RANG_MUSTER
    if englisch:
        p.hinweise.append("englische Fassung — geprüft mit den englischen Rang- und Zählwörtern")
    rz = _rangzeilen_lesen(txt)
    if not rz:
        p.hinweise.append("Datenblatt ohne Rangzeilen (Strukturbild §10, seit 2026-09-19) — jede "
                          "Aussage bleibt PRÜFEN; die Zahl von Hand gegen die Tabellen halten")
    for schl, v in sorted(rz.items()):
        for e in v["eintraege"]:
            if "roh" in e:
                p.pruefen.append("Rangzeile %s: Eintrag nicht lesbar „%s“ — von Hand verändert?"
                                 % (schl, _kurz(e["roh"], 80)))
    # 2026-09-22 (Prueflauf Geburtshoroskop 1+2 vom 2026-09-22b, Nr. 7): Im
    # GETRIEBE-Kapitel sind Verhaeltniszahlen ausdruecklich erlaubt (Typmodul,
    # „Das Strukturkapitel"), und Hemisphaeren-, Quadranten- und
    # Herrscherketten-Zahlen stehen in Strukturbild §3 und §8 — die Meldung
    # sagte das selbst und meldete trotzdem. Das waren planbar rund ein Dutzend
    # PRUEFEN je Lauf, die jedes Mal von Hand weggelesen wurden. Sie werden
    # jetzt gezaehlt und in EINER Hinweiszeile genannt; geprueft sind sie
    # weiterhin, und jede ANDERE Art von Befund meldet das Getriebe-Kapitel
    # unveraendert.
    getriebe_zahlen = 0
    eigen = _eigenes_zeichen(txt)                                   # 2026-09-24, §3
    struktur = _struktur_p12(txt)                                   # 2026-09-30, §3 und §8
    for ch, bewegung, text in _fliesstext(chapters):
        ist_getriebe = (_ist_kicker(ch, "Getriebe")
                        or _kapitelart(ch, typ, chapters) == "Getriebe-Kapitel"
                        # 2026-09-29 (Klasse-2-Entscheidungslauf K2, Chris: Frage
                        # 2 = a): Im Register des Geburtshoroskops (Typmodul,
                        # Rechenschaftskapitel) zaehlt die Probe wie im Getriebe.
                        or _kapitelart(ch, typ, chapters) == "Rechenschaft")
        saetze = _saetze_pos(text)
        for i, (_a, _e, satz) in enumerate(saetze):
            # 2026-10-12 (W1): Englisch öffnet die Einzigkeit über ein Element oder einen
            # Modus den Satz auch ohne Faktor („It is the only one in fire.“) — dann zählt
            # nur sie, keine andere Art im Satz (die übrigen lesen englisch kein Element).
            nur_einzig = False
            if not _hat_referent(satz):
                if not (englisch and _EINZIG_EM_EN_RE.search(satz)):
                    continue
                nur_einzig = True
            treffer = sorted(((m.start(), m.end(), art, m) for art, rx in MUSTER
                              for m in rx.finditer(satz) if not nur_einzig or art == "einzig"),
                             key=lambda t: (t[0], -t[1]))
            belegt = []
            for a, e, art, m in treffer:
                if any(not (e <= x or a >= y) for x, y in belegt):
                    continue
                belegt.append((a, e))
                # 2026-10-13 (Strang 2): Formen, die P18 genauer haelt — „keine andere
                # Verbindung … so eng wie“ (Rang 1 ohne Gleichstand) und „zu einem einzigen
                # Punkt“ (Naehe bis 1°); P12 hielt sie als Zaehlung bzw. Einzigkeit gegen
                # die falsche Rangzeile
                if not englisch and (
                        (art == "kein_anderer" and any(x.start() <= a < x.end()
                                                       for x in _P18_STRIKT_RE.finditer(satz)))
                        or (art == "einzig" and re.match(r"einzig\w*\s+Punkt", satz[a:], re.I)
                            and re.search(r"zu\s+einem\s+$", satz[max(0, a - 12):a], re.I))):
                    continue
                p.geprueft += 1
                befund = _rang_befund(art, m, satz, rz, typ, saetze[i - 1][2] if i else "",
                                      eigen=eigen, struktur=struktur, englisch=englisch)
                if befund:
                    if ist_getriebe and befund.startswith(("Zählaussage", "Count statement")):
                        getriebe_zahlen += 1
                        continue
                    p.pruefen.append("%s · %s: „%s“ — „%s“: %s"
                                     % (_bezeichnung(ch), bewegung, _kurz(satz, 140),
                                        _ws(m.group(0)), befund))
    if getriebe_zahlen:
        p.hinweise.append("Getriebe-Kapitel und Register: %d Verhältniszahl(en) nicht als PRÜFEN gemeldet — "
                          "dort ausdrücklich erlaubt (Typmodul), Hemisphären, Quadranten und "
                          "Herrscherketten stehen in Strukturbild §3 und §8" % getriebe_zahlen)
    if p.geprueft == 0:
        p.hinweise.append("keine Rang-, Zähl- oder Einzigkeitsaussage im Fließtext")
    return p.abschluss()

# --- P13 Text-Beleg-Deckung --------------------------------------------------
# Klartext-Modul, Pruefung „Beleg-Deckung" (Chris-Entscheidung Frage 4 = 1): Eine im
# Fliesstext benannte Konstellation steht im Beleg dieses oder eines anderen
# Kapitels oder in der Aspekttabelle — im Transit auch als Kontakt der Rechnung
# (events.json, Report, Themenliste). Erkannt wird eine Konstellation an einem
# Aspektwort („dein Mond … im Trigon zu Saturn") oder an einem Bild der
# Uebersetzungstabelle des Klartext-Moduls („verschmilzt mit", „fließt mühelos
# mit", „reibt sich an", „steht … gegenüber", „eine Verbindung zu") mit je einem
# Faktor davor und danach im selben Satz; bei Nachstellung („Merkur steht deinem
# Glückspunkt gegenüber") die zwei Faktoren davor, bei „Er/Sie/Es …" am
# Satzanfang ohne Faktor davor der letzte Faktor des Vorsatzes. Ein Aspektwort
# muss mit seiner Aspektart gedeckt sein; „verschmilzt" mit einer Konjunktion,
# „fließt mühelos" mit einem Trigon oder Sextil; jedes andere Bild mit irgendeiner
# Aspektart (es sagt die Art nicht sicher). Verneintes („kein Quadrat") zaehlt
# nicht, ebenso wenig ein Faktor „zu sich selbst" ausserhalb des Transits
# (Zyklusaussage, Strukturbild §7). Stehen mehrere
# Faktoren davor oder danach, genuegt EINE gedeckte Paarung — lieber still als
# falsch; gemeldet wird, was sich mit keiner Paarung decken laesst.
_VERNEINUNG_RE = re.compile(r"(?<![\wäöüß])(?:kein\w*|nicht|ohne|weder|no|not|without|neither)"
                            r"(?![\wäöüß])", re.I)
_REPORT_KONTAKT_RE = re.compile(
    r"(?m)^\s*(?:\[[^\]\n]*\]\s*)?(Jupiter|Saturn|Uranus|Neptun|Pluto|Knoten|Chiron|Mars)\s+"
    r"(Konjunktion|Opposition|Quadrat|Trigon|Sextil|Quincunx|Halbsextil)\s+(\S+)")

_BILD_RE = re.compile(
    r"(?<![\wäöüß])(?:verschm(?:ilzt|elzen|olzen)\w*|am\s+selben\s+Punkt\s+wie"
    r"|einen\s+(?:einzigen\s+)?Strom|(?-i:gegenüber)|Zerreißprobe|zwischen\s+zwei\s+Polen?"
    r"|reib(?:t|en)\s+sich\s+an|dräng(?:t|en)\s+gegen|in\s+Spannung\s+(?:zu|mit)"
    r"|fließ(?:t|en)\s+mühelos|(?:eine|die)\s+Gelegenheit\s+(?:zu|mit)"
    # 2026-09-29 (K6): das Sextil-Bild „öffnet dir eine Tür zu …“; seit 2026-09-30
    # (K4) auch gebeugt — „öffnen einander eine Tür“, „öffnet sich ihm eine Tür“,
    # „öffnet sich von X her eine Tür“: Marker ist das Verb, „eine Tür“ steht
    # hoechstens vier Woerter dahinter; ein Faktor in „von … her“ steht dann hinter
    # dem Marker und wird Partner.
    r"|öffne[tn](?:\s+sich)?(?=(?:\s+[\wäöüÄÖÜß-]+){0,4}?\s+eine\s+Tür(?![\wäöüÄÖÜß]))"
    r"|passt\s+nicht\s+(?:mit|zu)|leiser\s+Reiz|Suchbewegung"
    r"|(?:Verbindung|Kontakt)\s+(?:zu|mit|zwischen)|verbunden\s+mit)(?![\wäöüß])", re.I)
# nur Personalpronomen: „Dasselbe Quadrat trifft deinen Merkur" meint den Aspekt,
# nicht den letzten Faktor des Vorsatzes
_PRONOMEN_ANFANG_RE = re.compile(r"^\W*(Er|Sie|Es|It|He|She)(?![\wäöüß])")
# 2026-09-23b (Wartungslauf zu den Pruefberichten vom 23.09.; Geburtshoroskop 1+2
# Nr. 8, Transit 1+2 K1-3): Das Pronomen bekam seinen Bezug ohne Genus und nur am
# Satzanfang. „Sie verschmilzt mit Merkur" hinter einem Vorsatz, der auf Jupiter
# endete, wurde Jupiter–Merkur; „Er läuft über deinen Aszendenten und steht im
# Quadrat zu deinem Uranus" wurde AC–Uranus, und die Aufzaehlung erbte den AC.
# (a) Ein deutsches Pronomen sucht seinen Bezug nach dem Genus (er maskulin, sie
#     feminin, es neutrum; MC und IC passen zu jedem: „das MC", „die Himmelsmitte",
#     „der tiefste Punkt"). Kandidaten: das Subjekt des vorigen Glieds, sonst der
#     erste und der letzte passende Faktor davor (am Satzanfang im Vorsatz). Passt
#     keiner, bleibt es beim bisherigen Kandidaten. It/He/She: wie bisher.
# (b) Steht „er"/„sie" im Glied VOR Faktoren, die nur als Objekt dastehen („über
#     deinen Aszendenten", „zu deinem Uranus"), ist es das Subjekt des Markers:
#     Sein Bezug kommt als Kandidat dazu. Das Paar mit dem Objekt bleibt stehen —
#     eine gedeckte Paarung genuegt, die Probe wird nur leiser, nie strenger.
#     (a) und (b) greifen deshalb NUR, wenn hinter dem Marker ein Faktor steht
#     (`danach` nicht leer), und sie ERGAENZEN die bisherigen Kandidaten, statt
#     sie zu ersetzen. Sonst machte die Nachstell-Regel („X trifft Y im
#     Quadrat.") aus zwei Bezugs-Kandidaten ein neues, falsches Paar (Befund des
#     Zweitlesers im Wartungslauf 2026-09-23b: „Er bildet dabei mit deinem Mond
#     ein Quadrat.“ hinter einem Vorsatz mit Saturn und AC wurde Saturn–AC).
_GENUS = {"SONNE": "f", "VENUS": "f", "LILITH": "f",
          "MOND": "m", "MERKUR": "m", "MARS": "m", "JUPITER": "m", "SATURN": "m",
          "URANUS": "m", "NEPTUN": "m", "PLUTO": "m", "MONDKNOTEN": "m",
          "SUEDKNOTEN": "m", "CHIRON": "m", "PHOLUS": "m", "GLUECKSPUNKT": "m",
          "AC": "m", "DC": "m"}          # MC, IC fehlen absichtlich: jedes Genus
_PRONOMEN_GENUS = {"er": "m", "sie": "f", "es": "n"}
_SUBJEKT_PRONOMEN_RE = re.compile(r"(?<![\wäöüÄÖÜß])(?:er|sie|Er|Sie)(?![\wäöüÄÖÜß])")
_OBJEKT_VOR_RE = re.compile(
    r"(?<![\wäöüÄÖÜß])(?:deinen|deinem|deiner|deines|über|zu|zum|zur|an|am|auf|durch|"
    r"mit|ins|im|in|gegen|vom|von|bei|beim|um)\s+(?:\w+\s+)?$", re.I)


def _pronomen_bezug(pron, satz_vor, vorher, vorige_davor=None):
    """Bezugsfaktoren eines Personalpronomens (s. Kommentar oben, a) -> Liste
    kanonischer Faktoren; leer, wenn keiner passt."""
    g = _PRONOMEN_GENUS.get(pron.casefold())
    if g is None:                               # It/He/She: wie bisher
        fv = _faktoren_im_satz(vorher)
        return [fv[-1][2]] if fv else []

    def passt(f):
        return _GENUS.get(f, g) == g            # MC/IC: jedes Genus
    if vorige_davor:
        kand = [f for f in vorige_davor if passt(f)]
        if kand:
            return list(dict.fromkeys(kand))
    fs = [f for _a, _e, f in _faktoren_im_satz(satz_vor)] or \
        [f for _a, _e, f in _faktoren_im_satz(vorher)]
    kand = [f for f in fs if passt(f)]
    return list(dict.fromkeys(kand[:1] + kand[-1:]))
_FENSTER = 90                # Zeichen: so weit darf ein Faktor vom Aspektwort/Bild stehen

def _bild_arten(wort):
    """Aspektarten, fuer die ein Bild steht — None: jede (s. Kommentar oben)."""
    w = wort.casefold()
    if w.startswith("verschm"):
        return ("Konjunktion",)
    if w.startswith("fließ") or w.startswith("fliess"):
        return ("Trigon", "Sextil")
    return None

# Wo ein Satz in zwei eigenstaendige Aussagen zerfaellt. Bewusst nur die
# beiordnenden Faelle — ein Relativsatz oder ein Gedankenstrich verbindet
# haeufig genau die Faktoren, um die es geht.
_SATZGLIED_RE = re.compile(r",\s+(?:und|aber|doch|oder|sondern)\s|;\s")
# 2026-09-23 (Pruefberichte Geburtshoroskop 3+4 vom 22.09.c, 1+2 vom 22.09.c und
# 23.09., Transit 1+2 vom 22.09.c): drei Satzformen, aus denen P13 ein Paar baute,
# das der Satz nicht behauptet.
# (1) AUFZAEHLUNG — „ein Trigon zu Saturn und ein Quadrat zu Mars": Der zweite
#     Marker steht direkt hinter „und/sowie/oder/," (+ Artikel/Praeposition); er
#     teilt das Subjekt des ersten, sein „davor" ist nicht der Partner des ersten.
_AUFZAEHLUNG_RE = re.compile(          # „als auch" seit 2026-09-24
    r"(?:,|(?<![\wäöüß])(?:und|sowie|oder|als\s+auch|and|or)(?![\wäöüß]))\s+"
    r"(?:(?:ein|eine|einen|einem|einer|das|die|den|dem|der|zu|zum|zur|mit|im|in|"
    r"a|an|the|to|with)\s+)*$", re.I)
# (2) RELATIVSATZ — „im Trigon zum Mond, der seinerseits Saturn quadriert": Das
#     „danach" eines Markers endet am Relativsatz, sonst wird der Faktor darin
#     zum Partner des Subjekts (Merkur–Saturn statt Merkur–Mond).
_RELATIV_RE = re.compile(r",\s+(?:der|die|das|dessen|deren|welche[rsmn]?|which|who|whose)"
                         r"(?![\wäöüß])", re.I)
# (5) NEUES GLIED (2026-09-23b, Transit 1+2 K1-3, vierter Fall) — „Saturn steht dabei
#     im Quadrat, der Mondknoten im Trigon zu deiner Venus": Artikel + Faktor direkt
#     hinter dem Komma eroeffnen ein Glied mit eigenem Subjekt, keinen Relativsatz.
#     Das „danach" des Markers endet dort (nur wenn noch ein Marker folgt), sonst
#     wird das Subjekt des naechsten Glieds zum Partner des vorigen (Saturn–Mondknoten).
#     Enger gefasst nach dem Zweitleser (2026-09-23b): Der Artikel muss zum Genus
#     des Faktors im NOMINATIV passen (der + maskulin, die + feminin, das + MC/IC —
#     „der Sonne" ist Dativ, eine Apposition, kein neues Subjekt), vor dem Faktor
#     darf hoechstens ein Partizip stehen („der transitierende Mondknoten"; nie
#     „das deinen Mond trifft", „das der Mond spuert"), und bis zum naechsten
#     Marker steht kein Komma.
_GLIED_ANFANG_RE = re.compile(
    r",\s+(der|die|das)\s+(?:\w+end(?:e|en|er)\s+)?(%s|Knoten)(?![\wäöüÄÖÜß])"
    % _FAKTOR_RE)


def _neues_glied(satz, pos, naechster_marker):
    """(5): Beginnt am Komma bei `pos` ein Glied mit eigenem Subjekt?"""
    mg = _GLIED_ANFANG_RE.match(satz, pos)
    if not mg or "," in satz[mg.end():naechster_marker]:
        return False
    g = _GENUS.get(kanon(mg.group(2)))          # None: MC/IC, jedes Genus
    return {"der": "m", "die": "f"}.get(mg.group(1), "n") == g or \
        (g is None and mg.group(1) == "das")
# (6) RELATIVSATZ, AUCH MIT PRAEPOSITION (2026-09-23c; Pruefberichte Transit 1+2
#     vom 23.09.b und 3+4 vom 23.09.c): Das Pronomen am Satzanfang ist Subjekt
#     des Hauptsatzes. Steht ein Marker in einem Relativsatz, der dahinter
#     beginnt („Er ist die Spitze einer Figur, in der dein Mond und die Ballung
#     aus Venus und Saturn im Sextil stehen und beide im Quincunx zu Merkur"),
#     traegt (a) das Pronomen nicht hinein — vorher wurde sein Bezug (Merkur)
#     Partner des Merkur im Relativsatz. Ein Komma zwischen Relativsatz und
#     Marker schliesst ihn; Artikel + Faktor („, in der Sonne", „, der Mond")
#     ist kein Relativsatz. Wie bei (b) wird die Probe dadurch nur leiser.
_RELATIV_PRAEP_RE = re.compile(
    r",\s+(?:(?:in|an|auf|aus|bei|mit|nach|von|vor|zu|über|ueber|unter|hinter|"
    r"neben|zwischen|durch|für|fuer|gegen|um|ohne|seit|with|to|on|at|from|by|for)\s+)?"
    r"(?:der|die|das|dem|den|denen|deren|dessen|welche[rsmn]?|which|who|whom|whose)"
    r"(?![\wäöüÄÖÜß])(?!\s+(?:%s|Knoten)(?![\wäöüÄÖÜß]))" % _FAKTOR_RE, re.I)


def _im_relativsatz(satz, pos):
    """(6): Steht `pos` in einem Relativsatz, der davor beginnt und bis dahin
    nicht durch Komma oder Semikolon geschlossen ist?"""
    for r in _RELATIV_PRAEP_RE.finditer(satz, 0, pos):
        if not re.search(r"[,;]", satz[r.end():pos]):
            return True
    return False
# (7) SELBSTPAAR NUR BEI TRANSITERN (2026-09-23c): Ein Faktor mit sich selbst
#     ist nur im Transit und nur bei einem laufenden Planeten eine
#     Konstellation (Saturn-Rückkehr, Knotenwiederkehr). „Merkur … Merkur" kann
#     es nicht geben — so ein Paar entsteht nur aus einem falsch aufgeloesten
#     Bezug (dieselben Pruefberichte: „Merkur Quincunx Merkur").
# (8) AUFZAEHLUNG OHNE SUBJEKT (2026-09-24; Pruefberichte Geburtshoroskop 1+2 und
#     3+4b vom 24.09., Z-23.09.c Nr. 2): Fand der erste Marker einer Aufzaehlung
#     kein Subjekt („…; er steht im Sextil zu A und im Sextil zu B" — das Pronomen
#     steht hinter dem Semikolon, nicht am Satzanfang), bekam der zweite Marker das
#     Objekt des ersten als Partner (A–B). Jetzt bekommt er keinen Partner mehr aus
#     dem ersten Glied; ein Subjekt findet er nur noch ueber „zwischen" oder ein
#     Pronomen am Satzanfang.
# (9) NEBENSATZ (2026-09-24; Pruefberichte Transit 1+2 und 3+4 vom 24.09., Z-23.09.c
#     Nr. 2): Komma + unterordnende Konjunktion („, während A und B einander
#     gegenüberstehen", „, weil …") eroeffnet einen Satz mit eigenem Subjekt. Seine
#     Faktoren zaehlen nicht zum „danach" eines Markers, bis zum naechsten Komma oder
#     Semikolon; was dahinter steht („…, wenn man so will, zu deinem Mars"), zaehlt
#     wieder. Vorher wurde ein Faktor daraus zum Partner (A Sextil B statt Subjekt
#     Sextil A). „sowohl … , als auch" ist kein Nebensatz. Stand vor dem Schnitt ein Faktor
#     hinter dem Marker, paart die Nachstellung danach nicht nach vorn („A und B
#     stehen beide im Quadrat, weil C sie trifft" ergaebe sonst A–B; Befund des
#     Zweitpruefers 2026-09-24). Beide Regeln nehmen falsche Paare weg; (9) bildet
#     keine neuen, (8) nur ueber „zwischen" oder ein Pronomen am Satzanfang.
_NEBENSATZ_RE = re.compile(
    r",\s+(?:während|waehrend|weil|obwohl|obgleich|wenn|falls|sobald|solange|sofern|"
    r"als(?!\s+auch(?![\wäöüÄÖÜß]))|da|indem|nachdem|bevor|ehe|seitdem|damit|sodass|so\s+dass|"
    r"wobei|wohingegen|dass|"
    r"while|whereas|because|although|though|when|since|before|after|until|unless)"
    r"(?![\wäöüÄÖÜß])", re.I)
_SELBST_TRANSITER = {"MARS", "JUPITER", "SATURN", "URANUS", "NEPTUN", "PLUTO",
                     "CHIRON", "MONDKNOTEN"}


def _paar_ok(x, y, typ):
    """(3), (7): Achsenpaare nie; ein Faktor mit sich selbst nur im Transit und
    nur, wenn er transitieren kann."""
    if frozenset((x, y)) in _ACHSENPAARE:
        return False
    return x != y or (typ == "transit" and x in _SELBST_TRANSITER)


# (10) SELBSTPAAR NUR MIT RADIX-MARKE AUF EINER SEITE (2026-09-25, T20): Ein Satz
#      traegt Y–Y nur, wenn Y einmal als Radixpunkt steht („R-", „dein …") und
#      einmal ohne diese Marke (der Laufende; ein Pronomen am Satzanfang zaehlt
#      so). Zweimal markiert („T-Neptun ⚹ R-Mars — im Sextil zu deinem Mars") oder
#      zweimal unmarkiert („Er steht Chiron gegenueber, Chiron in den Zwillingen")
#      ist derselbe Radixpunkt zweimal — kein Paar, die Probe wird nur leiser.
_RADIX_MARKE_RE = re.compile(r"(?<![\wäöüÄÖÜß])(?:R-\s*|(?:dein\w*|your)\s+"
                             r"(?:[\wäöüÄÖÜß-]+\s+)?)$", re.I)


def _selbstpaar_im_satz(satz, x):
    """(10): Traegt der Satz das Selbstpaar x–x?"""
    marken = {bool(_RADIX_MARKE_RE.search(satz[max(0, a - 40):a]))
              for a, _e, f in _faktoren_im_satz(satz) if f == x}
    if _PRONOMEN_ANFANG_RE.match(satz):
        marken.add(False)
    return marken == {True, False}
# (3) ACHSENPAAR — AC/DC und MC/IC stehen einander immer gegenüber; ein Satz, der
#     beide Enden nennt („über deinen Deszendenten … deinem Aszendenten
#     gegenüber"), behauptet damit keinen Aspekt. Solche Paarungen zaehlen nicht.
#     Seit 2026-10-01 auch die Knotenachse (Pruefbericht Geburtshoroskop 1+2 vom
#     30.09., K1: ein Satz, der beide Enden der Knotenachse nennt, wurde
#     Mondknoten–Südknoten).
_ACHSENPAARE = {frozenset(("AC", "DC")), frozenset(("MC", "IC")),
                frozenset(("MONDKNOTEN", "SUEDKNOTEN"))}
# (4) ZUSATZ-SEGMENTE im Transit-Beleg („Sonnenbogen-Merkur ☿ Quadrat □ R-Neptun ♆")
#     decken die gleichnamige Konstellation im Text; P1 prueft ihr Datum.
_ZUSATZ_KONTAKT_RE = re.compile(
    r"(?:Sonnenbogen|solar[\s-]*arc)[\s-]+(?P<t>" + _FAKTOR_RE + r")(?![\wäöüÄÖÜß])"
    r"(?P<mitte>.*?)(?<![\wäöüÄÖÜß])R-\s*(?P<r>" + _FAKTOR_RE + r"|Knoten)(?![\wäöüÄÖÜß])",
    re.I | re.S)


# (11) TRANSIT-BILD „über" (2026-09-29, Wartungslauf zu den Pruefberichten vom
#      29.09., Transit 3+4 Klasse 1): „Saturn geht über deine Sonne" ist die
#      Konjunktion eines Transits — bis dahin erkannte P13 den Satz gar nicht als
#      Konstellation. Marker ist „über" direkt vor „dein…"/„R-" und einem Faktor,
#      nur im Transit (im Geburtshoroskop meint „über Uranus" eine Herrscherkette).
#      ELLIPSE: „…, im Oktober 2027 über deinen Mars" — ein zweites „über" hinter
#      Komma oder „und" und hoechstens einer Zeitangabe teilt das Subjekt des
#      ersten (sonst wurde Venus Partner von Mars). Gedeckt ist ein Transit-Kontakt
#      weiter auch durch die Rechnung (Chris-Entscheidung 2026-09-29, Frage 2 = B:
#      ein echter Transit darf nebenbei ohne Beleg-Zeile genannt werden); die
#      Erkennung faengt erfundene oder falsch benannte Konjunktionen.
_UEBER_RE = re.compile(r"(?<![\wäöüÄÖÜß])über(?=\s+(?:dein\w*\s+|R-\s*)(?:[\wäöüÄÖÜß-]+\s+)?"
                       r"(?:%s|Knoten)(?![\wäöüÄÖÜß]))" % _FAKTOR_RE)
# (24) HERRSCHAFTSFORMEL (2026-10-01b, Wartungslauf zu den Pruefberichten vom 01.10.,
#      Transit 1+2 K1): „…, dem Planeten, der über deinem Mond steht“ ist die
#      Klartext-Formel fuer eine Herrschaft (Klartext-Modul, Uebersetzungstabelle;
#      Transit-Modul, „Die Herrscherfunktion des Transitplaneten wird genannt“), keine
#      Beruehrung — P13 meldete eine Konjunktion, die der Satz nicht behauptet. Kein
#      Marker ist deshalb „über“ in genau dieser Form: „Planet, der“ / „Planeten, die“
#      (dazwischen hoechstens „auch“, „zugleich“, „außerdem“, „zudem“, „ja“),
#      Dativ-Possessiv, Faktor, „steht“/„stehen“; der beherrschte Faktor ist dann kein
#      Partner im Satz. „Saturn, der jetzt über deinem Mond steht“, „…, der ab März über
#      deinem Mond steht“ und „geht über deinen Mond“ bleiben Bild.
_HERRSCHAFT_VOR_RE = re.compile(r"(?<![\wäöüÄÖÜß])Planet(?:en)?\s*,\s*(?:der|die|welcher|"
                                r"welche)\s+(?:(?:auch|zugleich|außerdem|zudem|ja)\s+)?$")
_HERRSCHAFT_NACH_RE = re.compile(r"\s+dein(?:em|er)\s+(?:[\wäöüÄÖÜß-]+\s+)?(?:%s|Knoten)"
                                 r"(?![\wäöüÄÖÜß])(?=\s+(?:[\wäöüÄÖÜß]+\s+)?(?:steht|stehen)"
                                 r"(?![\wäöüÄÖÜß]))" % _FAKTOR_RE)


def _herrschaft_ueber(satz, m):
    """(24) Ist das „über“ an `m` die Herrschaftsformel „der Planet, der über deinem X
    steht“? -> Ende des beherrschten Faktors oder None."""
    if not _HERRSCHAFT_VOR_RE.search(satz[max(0, m.start() - 50):m.start()]):
        return None
    h = _HERRSCHAFT_NACH_RE.match(satz, m.end())
    return h.end() if h else None


_ZEIT_WORT = (r"(?:Januar|Februar|März|Maerz|April|Mai|Juni|Juli|August|September|Oktober|"
              r"November|Dezember|Frühjahr|Fruehjahr|Frühling|Sommer|Herbst|Winter|"
              r"Jahresanfang|Jahresmitte|Jahresende)")
_ELLIPSE_RE = re.compile(
    r"(?:,|(?<![\wäöüß])(?:und|sowie|dann|danach))\s+"
    r"(?:(?:im|am|ab|bis|seit|um|gegen|Anfang|Mitte|Ende|noch|erst|schon|später|wieder|"
    r"einmal|erneut)\s+)*(?:%s\s+)?(?:\d{4}\s+)?"
    r"(?:(?:noch|erst|schon|einmal|erneut|wieder)\s+)*$" % _ZEIT_WORT, re.I)


# (12) DOPPELPUNKT (2026-09-29, K1; GH12-29 Nr. 11): Stehen vor einem Doppelpunkt
#      nur Objekte und dahinter kein Faktor oder ein eigenes Paar mit Subjekt („Die Verbindungen zum Aszendenten und zu Jupiter reiben: Im
#      Quadrat zu …“ wurde AC–Jupiter), sind sie kein Partner dahinter; ein
#      Subjekt davor („Deine Sonne hat einen Gegenspieler: im Quadrat zu …“) bleibt.
# (13) MARKER IM NEBENSATZ (2026-09-29, K1; GH12-29c Nr. 4): Steht der Marker
#      selbst in einem Nebensatz („Chiron …, während das Sextil zu Mars …“),
#      zaehlen Faktoren vor der Konjunktion nicht zu seinem „davor“ — (9) regelte
#      nur den Nebensatz HINTER dem Marker. Beginnt der Nebensatz mit er/sie/es
#      („…, während sie im Quadrat zu Saturn steht“), meint das den Faktor davor;
#      ebenso ein Objektpronomen im Nebensatz („…, weil Pluto im Quadrat zu ihm steht“).
# (14) JE (2026-09-29, K1; GH12-29b Nr. 6): „bildet zu A, B und C je ein Sextil“,
#      „A und B … bilden zum Mondknoten je ein Quincunx“ — die Glieder hinter
#      „zu/zum/zur/mit“ sind Partner des Subjekts davor (sonst des Subjekts des
#      vorigen Markers), je Glied einzeln, nie untereinander; das Subjekt darf auch hinter
#      der Liste stehen („Zu A, B und C bildet dein Mars je …“). Ohne Subjekt: kein Paar.
# (15) ZWISCHEN (2026-09-29, K1; GH12-29b Nr. 6, GH12-29c Nr. 4): „zwischen A und
#      B“ bindet genau A und B, auch wenn davor ein Faktor steht („das Quincunx
#      zwischen Saturn und dem MC“ wurde IC–Saturn); „zwischen A und B, zwischen
#      C und D“ sind zwei Paare, nicht A–C. Steht davor ein Subjekt und vor dem
#      Marker kein bestimmter Artikel („Mars bildet ein Quadrat zwischen Sonne und
#      Mond“), steht es zu beiden Enden; „das Quincunx zwischen A und B“ nennt das Paar.
# (16) EINERSEITS/ANDERERSEITS (2026-09-29, K1; GH12-29c Nr. 4): „A und B
#      verschmelzen auf der einen Seite, C und D auf der anderen“ — das zweite
#      Paar ist eine Ellipse, kein Partner des ersten (vorher B–C); es wird selbst
#      geprueft (C–D).
# (17) OBJEKTPRONOMEN (2026-09-29, K1; GH12-29 Nr. 11): Stehen vor einem Marker
#      nur die Objekte des vorigen und dahinter „ihm/ihr/ihnen“ („im Trigon zu
#      Uranus und zu Neptun, die beide in leichter Verbindung mit ihm stehen“),
#      ist der Partner das Subjekt des vorigen Markers (vorher Uranus–Neptun);
#      „dir/dich“ meint den Leser — kein Paar. Ohne Pronomen paart die
#      Nachstellung wie bisher („…, die beide in Opposition stehen“).
# Alle nehmen Paare weg oder binden ein Paar an die Woerter, die es nennen.
_JE_RE = re.compile(r"(?<![\wäöüÄÖÜß])je\s+(?:ein(?:e|en|em|er)?\s+)?$", re.I)
_LISTE_RE = re.compile(r"\s*(?:,|und|sowie|oder)\s+(?:(?:zu|zum|zur|mit|mein\w*|dein\w*|"
                       r"der|die|das|dem|den|des)\s+)*", re.I)
_ZW_GRUPPE_RE = re.compile(
    r"(?<![\wäöüÄÖÜß])(?:zwischen|between)\s+(?P<x>.+?)\s+(?:und|and)\s+(?P<y>.+?)"
    r"(?=\s*[,;.:]|\s*$|\s+(?:zwischen|between)(?![\wäöüÄÖÜß]))", re.I)
# (18) ZUEINANDER (2026-09-29, K1; GH12-29b Nr. 6): „A und B stehen im Sextil
#      zueinander und bilden zum Y je ein …“ — „zueinander“ schliesst das Paar
#      vor dem Marker; Y gehoert zum naechsten Marker (vorher A–Y, B–Y im Sextil).
_ZUEINANDER_RE = re.compile(r"\s*(?:[\wäöüÄÖÜß]+\s+)?(?:zueinander|miteinander|"
                            r"untereinander)(?![\wäöüÄÖÜß])", re.I)
# (20) MARKER IM RELATIVSATZ (2026-10-01, Pruefbericht Geburtshoroskop 1+2 vom
#      30.09., K1): „Pholus, der hier im Trigon mitklingt, steht in Kapitel 4 Mars
#      gegenüber“ wurde Pholus–Mars im Trigon. Steht der Marker
#      in einem Relativsatz, endet sein „danach“ am Komma, das ihn schliesst — der
#      Faktor des Hauptsatzes dahinter ist nicht sein Partner.
# (21) GRUPPE VOR „UND + PRAEDIKAT“ (2026-10-01, ebd.): „Venus und Uranus bilden ein
#      Sextil und zeigen gemeinsam auf deinen Mars“ wurde Venus–Mars im Sextil. Steht
#      vor dem Marker eine Gruppe aus mindestens zwei Faktoren und folgt ihm direkt
#      „und“ mit einem Wort, das kein Faktor, Artikel, Possessiv und keine Praeposition
#      ist, gehoert der Aspekt der Gruppe selbst (Nachstellung, wie „zueinander“ (18)).
#      Ein folgendes „…, beide im Quincunx zu ihm“ paart dann wie (17) mit der Gruppe,
#      wenn vor ihm nur Objekte stehen („auf deinen Mars“).
# (22) „A UND B … ZU IHM“ AM ERSTEN MARKER (2026-10-01, ebd.): „Und Venus und Jupiter
#      stehen beide im Quincunx zu ihm“ wurde Venus–Jupiter. Wie (17), nur ohne
#      vorigen Marker: Partner ist der Faktor des Vorsatzes mit passendem Genus („ihm“
#      maskulin, „ihr“ feminin; MC/IC passen immer); findet sich keiner, kein Paar.
#      „ihnen“ und „dir/dich“ tragen kein Paar.
def _gruppe_koordiniert(satz, davor_pos):
    """(21), (22): Stehen vor dem Marker mindestens zwei verschiedene Faktoren, die
    nur durch „und“, „sowie“, „oder“ oder Komma verbunden sind („Venus und Jupiter“)?
    Ein Hauptsatz-Subjekt vor einem Nebensatz („Dein Mond bleibt wachsam, weil Pluto
    …“) ist keine Gruppe."""
    if len({f for _a, _e, f in davor_pos}) < 2:
        return False
    return all(_LISTE_RE.fullmatch(satz[davor_pos[k][1]:davor_pos[k + 1][0]])
               for k in range(len(davor_pos) - 1))


_UND_PRAEDIKAT_RE = re.compile(
    r"\s+(?:und|sowie)\s+(?!(?:zu|zum|zur|mit|im|in|ins|an|am|auf|der|die|das|dem|den|"
    r"des|ein\w*|mein\w*|dein\w*|sein\w*|ihr\w*)(?![\wäöüÄÖÜß]))(?P<w>[\wäöüÄÖÜß-]+)", re.I)
_ZW_NACH_RE = re.compile(r"\s*(?:[\wäöüÄÖÜß]+\s+){0,2}?(?:zwischen|between)"
                         r"(?![\wäöüÄÖÜß])", re.I)
_OBJ_PRONOMEN_RE = re.compile(r"(?<![\wäöüÄÖÜß])(?:ihm|ihr|ihn|ihnen|sie|him|her|them)"
                              r"(?![\wäöüÄÖÜß])", re.I)                     # (13)
_JE_OBJ_RE = re.compile(r"(?<![\wäöüÄÖÜß])(?:zu|zum|zur|mit)\s+(?:(?:der|die|das|dem|den|"
                        r"des|mein\w*|dein\w*)\s+)?$", re.I)             # (14)
_EINE_SEITE_RE = re.compile(r"auf\s+der\s+einen\s+Seite|einerseits|zum\s+einen", re.I)
_ANDERE_SEITE_RE = re.compile(r"auf\s+der\s+anderen|andererseits|zum\s+anderen", re.I)


def _zwischen_paare(text):
    """(15): Paare aus „zwischen X und Y“ — je genau ein Faktor auf jeder Seite."""
    out = []
    for g in _ZW_GRUPPE_RE.finditer(text or ""):
        fx = [f for _a, _e, f in _faktoren_im_satz(g.group("x"))]
        fy = [f for _a, _e, f in _faktoren_im_satz(g.group("y"))]
        if len(set(fx)) == 1 and len(set(fy)) == 1:
            out.append((fx[0], fy[0]))
    return out


def _konstellationen(satz, vorher="", typ=None):
    """Konstellationen eines Fliesstext-Satzes (s. Kommentar oben) ->
    [(Faktoren davor, Art, Faktoren danach, Treffer)]; Art ist bei einem Aspektwort
    die Aspektart (str), bei einem Bild das Tupel der Arten, fuer die es steht —
    leer, wenn es fuer keine bestimmte steht. typ='transit' erkennt dazu das
    Transit-Bild „über" (11, seit 2026-09-29)."""
    fak = _faktoren_im_satz(satz)
    if typ == "transit":                                                # (24)
        _hs = [(m.start(), _herrschaft_ueber(satz, m)) for m in _UEBER_RE.finditer(satz)]
        _hs = [(a_, e_) for a_, e_ in _hs if e_ is not None]
        if _hs:                       # der beherrschte Faktor ist kein Partner
            fak = [x for x in fak if not any(a_ <= x[0] < e_ for a_, e_ in _hs)]
    marker = [(m, _art(m.group(1)) if m.group(1) else _ASP_GLYPH.get(m.group(2)))
              for m in ASPEKT_RE.finditer(satz)]
    for m in _BILD_RE.finditer(satz):
        if not any(m.start() < x.end() and x.start() < m.end() for x, _ in marker):
            marker.append((m, _bild_arten(m.group(0)) or ()))
    ueber = set()
    if typ == "transit":
        for m in _UEBER_RE.finditer(satz):
            if not any(m.start() < x.end() and x.start() < m.end() for x, _ in marker):
                if _herrschaft_ueber(satz, m) is not None:              # (24)
                    marker.append((m, "HERRSCHAFT"))    # kein Paar, traegt das Subjekt
                else:
                    marker.append((m, ("Konjunktion",)))
                ueber.add(m.start())
    out = []
    # 2026-09-22 (Prueflauf Geburtshoroskop 1+2 vom 2026-09-22b, Nr. 10): Traegt
    # ein Satz ZWEI Aspektangaben, holte sich jeder Marker alle Faktoren im
    # Fenster — auch die, die zum anderen Marker gehoeren. Daraus entstand ein
    # drittes Paar, das im Satz nicht steht; drei korrekte Saetze mussten
    # umgeschrieben werden. Das Fenster endet jetzt am Nachbarmarker. Ein
    # Faktor ZWISCHEN zwei Markern gehoert weiter zu beiden — dort steht er
    # wirklich in beiden Konstellationen.
    marker.sort(key=lambda t: t[0].start())
    vorige_davor = None
    vorige_danach = None                                             # (17)
    for _i, (m, art) in enumerate(marker):
        if art == "HERRSCHAFT":                                         # (24)
            vorige_davor = list(vorige_davor or []) or _p13_satzsubjekt(satz, m.start(),
                                                                        vorher)
            vorige_danach = []
            continue
        if _VERNEINUNG_RE.search(satz[max(0, m.start() - 25):m.start()]):
            continue
        # Zwei Grenzen statt nur des Fensters (2026-09-22, Prueflauf
        # Geburtshoroskop 1+2 vom 2026-09-22b, Nr. 10): Traegt ein Satz ZWEI
        # Aspektangaben, holte sich jeder Marker alle Faktoren im Fenster —
        # auch die des anderen Markers. Aus „Uranus steht im Quadrat zur
        # Sonne, und Pluto traegt das Trigon zum Mond" entstanden vier Paare
        # statt zwei; drei korrekte Saetze mussten deshalb umgeschrieben
        # werden.
        #   1. der HAUPTSATZ-Schnitt („, und", „, aber", „;"): Was hinter ihm
        #      steht, ist eine eigene Aussage. Relativsaetze („…, der
        #      seinerseits Saturn quadriert") werden NICHT geschnitten — dort
        #      traegt der Faktor davor die zweite Konstellation wirklich mit.
        #   2. der Nachbarmarker: ueber ihn hinaus reicht kein Fenster.
        vor_grenze, nach_grenze = 0, len(satz)
        for ms in _SATZGLIED_RE.finditer(satz):
            if ms.end() <= m.start():
                vor_grenze = max(vor_grenze, ms.end())
            elif ms.start() >= m.end():
                nach_grenze = min(nach_grenze, ms.start())
                break
        if _i:
            vor_grenze = max(vor_grenze, marker[_i - 1][0].end())
        if _i + 1 < len(marker):
            nach_grenze = min(nach_grenze, marker[_i + 1][0].start())
        _gruppe = None
        _dp = satz.rfind(":", vor_grenze, m.start())                   # (12)
        _hinter = [(a, f) for a, _e, f in fak if _dp < a < nach_grenze
                   and a - m.end() <= _FENSTER] if _dp >= 0 else []
        if _dp >= 0 and (not _hinter or (len({f for _a, f in _hinter}) >= 2 and any(
                not _OBJEKT_VOR_RE.search(satz[max(0, a - 30):a]) for a, _f in _hinter)))\
                and all(_OBJEKT_VOR_RE.search(satz[max(0, a - 30):a])
                        for a, _e, _f in fak if vor_grenze <= a < _dp):
            vor_grenze = _dp + 1
        for _mn in _NEBENSATZ_RE.finditer(satz, vor_grenze, m.start()):  # (13)
            _mk = re.compile(r"[,;]").search(satz, m.end(), nach_grenze)
            if not re.search(r"[,;]", satz[_mn.end():m.start()]) and not re.match(
                    r"\s+(?:er|sie|es|he|she|it)(?![\wäöüÄÖÜß])", satz[_mn.end():], re.I) \
                    and not _OBJ_PRONOMEN_RE.search(satz, _mn.end(),
                                                    _mk.start() if _mk else nach_grenze):
                vor_grenze = max(vor_grenze, _mn.start())
        if _im_relativsatz(satz, m.start()):                            # (20)
            _rk = re.compile(r"[,;]").search(satz, m.end(), nach_grenze)
            if _rk:
                nach_grenze = _rk.start()
        for mr in _RELATIV_RE.finditer(satz, m.end(), nach_grenze):   # (2)
            if any(a >= m.end() and e <= mr.start() for a, e, _f in fak):
                nach_grenze = mr.start()
                break
            if _i + 1 < len(marker) and _neues_glied(satz, mr.start(),
                                                     marker[_i + 1][0].start()):  # (5)
                nach_grenze = mr.start()
                break
        ns_spannen = []                                                  # (9)
        for mn in _NEBENSATZ_RE.finditer(satz, m.end(), nach_grenze):
            mk = re.compile(r"[,;]").search(satz, mn.end(), nach_grenze)
            ns_spannen.append((mn.start(), mk.start() if mk else nach_grenze))
        vor_schnitt = any(s_ <= a < t_ and a - m.end() <= _FENSTER
                          for a, e, _f in fak for s_, t_ in ns_spannen)  # (9): Partner entfernt?
        davor_pos = [(a, e, f) for a, e, f in fak if a >= vor_grenze and e <= m.start()
                     and m.start() - e <= _FENSTER]
        davor = [f for _a, _e, f in davor_pos]
        danach = [f for a, e, f in fak if a >= m.end() and e <= nach_grenze
                  and a - m.end() <= _FENSTER
                  and not any(s_ <= a < t_ for s_, t_ in ns_spannen)]     # (9)
        _zw_ende = m.group(0).casefold().endswith("zwischen")          # (15)
        if _zw_ende or _ZW_NACH_RE.match(satz[m.end():]):
            _zw_bis = marker[_i + 1][0].start() if _i + 1 < len(marker) else len(satz)
            _zw_bis = min(_zw_bis, satz.find(";", m.end()) % (len(satz) + 1))
            _gruppen = _zwischen_paare(("zwischen " if _zw_ende else "")
                                       + satz[m.end():_zw_bis])
            _sub15 = [f for a, _e, f in davor_pos
                      if not _OBJEKT_VOR_RE.search(satz[max(0, a - 30):a])]
            if _gruppen and _sub15 and not _zw_ende and not re.search(
                    r"(?<![\wäöüÄÖÜß])(?:der|die|das|dem|den|des)\s+(?:[\wäöüÄÖÜß]+\s+)?$",
                    satz[max(0, m.start() - 30):m.start()], re.I):
                # „Mars bildet ein Quadrat zwischen Sonne und Mond“: das Subjekt
                # steht zu beiden Enden (Zweitpruefung) — wie vor (15).
                _enden = list(dict.fromkeys(f for g_ in _gruppen for f in g_))
                out.append((_sub15, art, _enden, m))
                vorige_davor, vorige_danach = _sub15, _enden
                continue
            if _gruppen:
                for _x, _y in _gruppen:
                    out.append(([_x], art, [_y], m))
                vorige_davor, vorige_danach = [_gruppen[-1][0]], [_gruppen[-1][1]]
                continue
        if not danach and _JE_RE.search(satz[max(0, m.start() - 14):m.start()]):  # (14)
            _o = next((k for k, (a, _e, _f) in enumerate(davor_pos)
                       if _JE_OBJ_RE.search(satz[max(0, a - 30):a])), None)
            if _o is not None:
                _u = _o                    # die Objektliste endet am ersten Nicht-Glied
                while _u + 1 < len(davor_pos) and _LISTE_RE.fullmatch(
                        satz[davor_pos[_u][1]:davor_pos[_u + 1][0]]):
                    _u += 1
                _kand = davor_pos[:_o] + davor_pos[_u + 1:]
                _subj = [f for a, _e, f in _kand
                         if not _OBJEKT_VOR_RE.search(satz[max(0, a - 30):a])] \
                    or [f for _a, _e, f in _kand]
                _objs = [f for _a, _e, f in davor_pos[_o:_u + 1]]
                if not _subj and _i:
                    _subj = list(vorige_davor or [])
                if _subj and _objs:
                    for _ob in _objs:          # je Glied ein eigener Aspekt
                        out.append((_subj, art, [_ob], m))
                    vorige_davor, vorige_danach = _subj, _objs
                continue
        if danach and _ZUEINANDER_RE.match(satz[m.end():]):               # (18)
            danach = []
        if danach and _gruppe_koordiniert(satz, davor_pos):              # (21)
            _ud = _UND_PRAEDIKAT_RE.match(satz, m.end())
            if _ud and not _faktoren_im_satz(_ud.group("w")):
                danach = []
        if danach and len(set(f for _a, _e, f in davor_pos)) >= 2:       # (16)
            _k = satz.find(",", m.end(), nach_grenze)
            if _k >= 0 and not any(m.end() <= a < _k for a, _e, _f in fak) and (
                    _EINE_SEITE_RE.search(satz[m.end():_k])
                    or _ANDERE_SEITE_RE.search(satz[_k:nach_grenze])):
                danach = []
                _rest = list(dict.fromkeys(f for a, _e, f in fak if _k < a < nach_grenze))
                if len(_rest) == 2:                  # das Paar der Ellipse selbst
                    out.append(([_rest[0]], art, [_rest[1]], m))
        if danach and davor_pos and all(_OBJEKT_VOR_RE.search(satz[max(0, a - 30):a])
                                        for a, _e, _f in davor_pos):       # (b)
            pm = None
            for pm in _SUBJEKT_PRONOMEN_RE.finditer(satz, vor_grenze, davor_pos[0][0]):
                pass
            if pm is not None and not any(pm.end() <= r.start() < m.start()
                                          for r in _RELATIV_RE.finditer(satz)):
                bezug = _pronomen_bezug(pm.group(0), satz[:pm.start()], vorher,
                                        vorige_davor if _i else None)
                davor = davor + [f for f in bezug if f not in davor]
        if _i:                                                          # (1), (8)
            v_ende = marker[_i - 1][0].end()
            if _AUFZAEHLUNG_RE.search(satz[v_ende:m.start()]) and any(
                    a >= v_ende and e <= m.start() for a, e, _f in fak):
                davor = list(vorige_davor or [])
            elif m.start() in ueber or marker[_i - 1][0].start() in ueber:   # (11)
                # Neben einem „über"-Marker traegt das Subjekt des vorigen Markers
                # weiter („Saturn geht über deinen Mond und steht im Quadrat zu
                # deinem Mars"): Es kommt als Kandidat dazu, die Probe wird nur
                # leiser. Die Ellipse zwischen zwei „über" ersetzt das „davor".
                _pf = [(a, e) for a, e, _f in fak if a >= v_ende and e <= m.start()]
                if (m.start() in ueber and marker[_i - 1][0].start() in ueber and _pf
                        and _ELLIPSE_RE.search(satz[_pf[-1][1]:m.start()])):
                    davor = list(vorige_davor or [])
                else:
                    davor = davor + [f for f in (vorige_davor or []) if f not in davor]
        if not davor and len(danach) >= 2 and (re.match(r"\s*(?:zwischen|between)\b", satz[m.end():])  # nur ohne Gruppe (15)
                                               or m.group(0).casefold().endswith("zwischen")):
            davor, danach = [danach[0]], danach[1:]
        if not davor and vorher and _PRONOMEN_ANFANG_RE.match(satz):      # (a)
            fv = _faktoren_im_satz(vorher)
            kand = [fv[-1][2]] if fv else []
            if danach:
                kand = list(dict.fromkeys(kand + _pronomen_bezug(
                    _PRONOMEN_ANFANG_RE.match(satz).group(1), "", vorher)))
            if _im_relativsatz(satz, m.start()):                           # (6)
                # Kein Paar — aber die Aufzaehlung (1) des naechsten Markers erbt,
                # was (a) gesetzt haette; sonst wurde der Partner dieses Markers
                # Subjekt des naechsten (Zweitleser 2026-09-23c).
                if kand:
                    vorige_davor = kand
                continue
            davor = kand
        _p17 = None if danach else re.match(
            r"\s*(?:[\wäöüÄÖÜß]+\s+){0,2}?(?P<p>ihm|ihr|ihnen|ihn|dir|dich)(?![\wäöüÄÖÜß])",
            satz[m.end():nach_grenze])
        if _p17 and _i and (set(davor) <= set(vorige_danach or ()) or (   # (17)
                not vorige_danach and davor_pos and all(                     # (21)
                    _OBJEKT_VOR_RE.search(satz[max(0, a - 30):a]) for a, _e, _f in davor_pos))):
            if _p17.group("p") in ("dir", "dich"):
                continue
            danach = [f for f in (vorige_davor or []) if f not in davor]
        elif _p17 and not _i and _gruppe_koordiniert(satz, davor_pos):   # (22)
            if _p17.group("p") in ("dir", "dich", "ihnen"):
                continue
            _g22 = "f" if _p17.group("p") == "ihr" else "m"
            danach = list(dict.fromkeys(
                f for _a, _e, f in _faktoren_im_satz(vorher or "")
                if _GENUS.get(f, _g22) == _g22 and f not in davor))
            if not danach:
                continue
        if not danach and len(set(davor)) >= 2 and not vor_schnitt:     # (9): nur leiser
            danach = [davor[-1]]
            davor = [f for f in davor[:-1] if f != danach[0]]
            _gruppe = davor + danach       # (18): Subjekt des Satzes ist die ganze Gruppe
        if davor and danach:
            out.append((davor, art, danach, m))
            vorige_davor, vorige_danach = davor, danach
            if _gruppe:
                vorige_davor, vorige_danach = _gruppe, []
    return out

# (19) WEITERE PAARUNGEN FUER EINE SONST UNGEDECKTE KONSTELLATION (2026-09-30,
#      Wartungslauf zu den Pruefberichten vom 29./30.09., K2): In vier Berichten
#      meldete P13 richtige Saetze, weil der Traeger einer Aufzaehlung im Paar fehlte.
#      Erst wenn keine Paarung gedeckt ist, kommen weitere Kandidaten dazu — die
#      Probe wird damit nur leiser, nie strenger:
#      (a) GENITIV hinter dem Aspektwort („das Sextil der Venus zu Jupiter“): der
#          Genitiv-Faktor mit jedem Faktor dahinter;
#      (b) „… zu sich selbst“ direkt hinter dem Marker: der Faktor davor mit sich
#          selbst (nur im Transit; `_paar_ok()` laesst es sonst nicht zu);
#      (c) das SUBJEKT des Satzes — der erste Faktor ohne Praeposition, ohne
#          Objekt-Possessiv und ohne Artikel, der nicht zum Nominativ passt, oder der
#          Bezug eines Personalpronomens am Satzanfang — mit jedem Faktor dahinter:
#          die Beiordnung („… und steht im Quincunx zu …“), die Folge („…, dann im
#          Quadrat zu … und zuletzt im Quadrat zu …“) und der lange Satz, dessen
#          Subjekt jenseits des Fensters steht;
#      (d) im Transit die Transiter des Kapitels (Kontakte seines Belegs) mit jedem
#          Faktor dahinter („…, wenige Tage später das Trigon zu deinem Neptun“).
#      (c) und (d) nur, wenn vor dem Marker kein eigenes Subjekt steht — jeder Faktor
#      davor ist Objekt („zu deinem Saturn“, „an deiner Venus“). Sonst wuerde ein
#      falsch benannter Planet („Dazu kommt Pluto im Quadrat zu deiner Sonne“ in einem
#      Saturn-Kapitel) vom richtigen gedeckt (Selbsttest Lauf 5).
_P13_PRAEP_VOR_RE = re.compile(
    r"(?<![\wäöüÄÖÜß])(?:zwischen|bei|beim|nach|vor|hinter|neben|unter|aus|für|ohne|seit|"
    r"samt|außer|statt|trotz|wegen|dank|gegenüber)\s+(?:(?:der|die|das|dem|den|des|"
    r"ein\w*|dein\w*|sein\w*|ihr\w*)\s+)?(?:[\wäöüÄÖÜß-]+\s+)?$", re.I)
_P13_ARTIKEL_VOR_RE = re.compile(
    r"(?<![\wäöüÄÖÜß])(der|die|das|dem|den|des)\s+(?:[\wäöüÄÖÜß-]+\s+)?$", re.I)
_P13_BEIORDNUNG_RE = re.compile(
    r"\s*(?:,\s*)?(?:(?:und|sowie|oder)\s+)?(?:(?:der|die|das|dem|den|des|dein\w*)\s+)?",
    re.I)
_P13_GENITIV_RE = re.compile(r"\s+(?:der|des|deiner|deines)\s+(?:[\wäöüÄÖÜß-]+\s+)?", re.I)
_P13_SELBST_RE = re.compile(r"\s+(?:zu|mit)\s+sich(?:\s+selbst)?(?![\wäöüÄÖÜß])", re.I)
_P13_NOMINATIV = {"m": ("der",), "f": ("die",), "n": ("das",)}


def _p13_satzsubjekt(satz, bis, vorher=""):
    """(19c) Das Subjekt des Satzes vor Position `bis` -> [Faktor] oder []."""
    pm = _PRONOMEN_ANFANG_RE.match(satz)
    if pm:
        return _pronomen_bezug(pm.group(1), "", vorher) if vorher else []
    ende_objekt = None                  # Ende des letzten uebersprungenen Objekts
    for a, e, f in sorted(_faktoren_im_satz(satz)):
        if a >= bis:
            break
        vor = satz[max(0, a - 30):a]
        weg = bool(_OBJEKT_VOR_RE.search(vor) or _P13_PRAEP_VOR_RE.search(vor))
        if not weg and ende_objekt is not None \
                and _P13_BEIORDNUNG_RE.fullmatch(satz, ende_objekt, a):
            weg = True                  # „zwischen Venus und Pluto“: auch das zweite Glied
        ma = _P13_ARTIKEL_VOR_RE.search(vor)
        if not weg and ma and ma.group(1).lower() not in _P13_NOMINATIV.get(
                _GENUS.get(f), ("der", "die", "das")):
            weg = True                  # „der Sonne“, „dem Mond“: kein Nominativ
        if not weg:
            return [f]
        ende_objekt = e
    return []


# (23) GLIEDER EINER OBJEKT-REIHE (2026-10-01b, Wartungslauf zu den Pruefberichten
#      vom 01.10., Transit 1+2 K1): „… die Reibung an Venus und Pluto, mit einem
#      Stillstand nahe am Quadrat zu deinem Pluto“ (Satzform nachgebaut) wurde als
#      Pluto–Pluto gemeldet. Das zweite Glied hinter „und“ trug keine Praeposition,
#      galt als Subjekt, und (19) kam nicht zum Zug. Jetzt ist ein Faktor auch dann
#      Objekt, wenn er mit „und“/„sowie“/„oder“ an ein Objekt angereiht ist (ein
#      Glied hinter blossem Komma nur, wenn die Reihe mit einem dieser Woerter
#      weitergeht: „an Venus, Mars und Pluto“) UND zwischen ihm und dem Marker ein
#      Komma steht. Ohne Komma ist er das Subjekt einer Ellipse („zu deinem Merkur und
#      Pluto im Quadrat zu deiner Sonne“), „, und“ beginnt einen neuen Hauptsatz
#      („…, und Pluto steht im Quadrat …“) — beide bleiben Subjekt; sonst deckte (19)
#      einen falsch benannten Planeten (Gegenpruefung im Wartungslauf).
#      Die Probe wird damit nur leiser, nie strenger (wie (19)).
_P13_REIHE_UND_RE = re.compile(r"\s+(?:und|sowie|oder)\s+(?:(?:der|die|das|dem|den|des|"
                               r"dein\w*|zu|zum|zur|an|am|mit)\s+)?", re.I)
_P13_REIHE_KOMMA_RE = re.compile(r"\s*,\s*(?:(?:der|die|das|dem|den|des|dein\w*|zu|zum|zur|"
                                 r"an|am|mit)\s+)?", re.I)


def _p13_objekt_stellen(satz, bis):
    """(19), (23): {Anfang: Ende} der Faktoren vor `bis`, die als Objekt dastehen —
    hinter einer Praeposition oder einem Objekt-Possessiv (Ende None), oder angereiht
    an ein solches Objekt (Ende des Glieds; zaehlt nur mit Komma vor dem Marker)."""
    obj, offen, vorig = {}, [], None       # vorig: Ende des vorigen Reihen-Glieds
    for a, e, _f in sorted(_faktoren_im_satz(satz)):
        if e > bis:
            break
        vor = satz[max(0, a - 30):a]
        if _OBJEKT_VOR_RE.search(vor) or _P13_PRAEP_VOR_RE.search(vor):
            obj[a] = None
            offen, vorig = [], e
        elif vorig is not None and _P13_REIHE_UND_RE.fullmatch(satz, vorig, a):
            obj[a] = e
            obj.update(offen)
            offen, vorig = [], e
        elif vorig is not None and _P13_REIHE_KOMMA_RE.fullmatch(satz, vorig, a):
            offen.append((a, e))
            vorig = e
        else:
            offen, vorig = [], None
    return obj


def _p13_reihe_dabei(satz, m, davor):
    """(23) Steht ein Faktor von `davor` nur als angereihtes Glied vor dem Marker?"""
    obj = _p13_objekt_stellen(satz, m.start())
    pos = {f: a for a, e, f in sorted(_faktoren_im_satz(satz)) if e <= m.start()}
    return any(obj.get(pos.get(f)) is not None for f in davor)


def _p13_nur_objekte(satz, m, davor):
    """(19) Steht jeder Faktor von `davor` vor dem Marker als Objekt? Ein Faktor, der
    im Satz nicht vor dem Marker steht (Bezug eines Pronomens), gilt als Subjekt.
    Seit 2026-10-01b zaehlt auch ein angereihtes Glied als Objekt (23)."""
    pos = {}
    for a, e, f in sorted(_faktoren_im_satz(satz)):
        if e <= m.start():
            pos[f] = a                  # die letzte Stelle vor dem Marker
    obj = _p13_objekt_stellen(satz, m.start())
    for f in davor:
        a = pos.get(f)
        if a is None or a not in obj:
            return False
        if obj[a] is not None and "," not in satz[obj[a]:m.start()]:
            return False                # (23): angereiht, aber ohne Komma vor dem Marker
    return True


def _p13_weitere_paare(satz, m, davor, danach, typ, vorher="", transiter=()):
    """(19) Weitere Paarungen [(x, y)] fuer eine sonst ungedeckte Konstellation."""
    out = []
    nach_pos = [(a, f) for a, _e, f in sorted(_faktoren_im_satz(satz)) if a >= m.end()]
    if nach_pos and _P13_GENITIV_RE.fullmatch(satz, m.end(), nach_pos[0][0]):   # (a)
        out += [(nach_pos[0][1], y) for y in danach if y != nach_pos[0][1]]
    if typ == "transit" and _P13_SELBST_RE.match(satz, m.end()):                 # (b)
        out += [(x, x) for x in davor]
    if _p13_nur_objekte(satz, m, davor):
        _subj = _p13_satzsubjekt(satz, m.start(), vorher)
        for s_ in _subj:                                                        # (c)
            out += [(s_, y) for y in danach if y != s_]
        if typ == "transit" and not (_subj and _p13_reihe_dabei(satz, m, davor)):  # (d)
            out += [(t_, y) for t_ in transiter for y in danach if y != t_]
    return list(dict.fromkeys(out))


def _p13_beleg_deckung(chapters, typ, tabelle, txt, events=None):
    p = _Probe("P13", "Text-Beleg-Deckung")
    p.einheit = "Konstellationen"
    paare = {(frozenset((e["a"], e["b"])), e["art"]) for e in tabelle}
    kontakte = set()
    for ch in chapters:
        form = _beleg_form(ch, typ, chapters)
        if not ch.get("beleg") or form == "struktur":
            continue
        for seg in _segmente(ch["beleg"]):
            k = _kontakt_aus_segment(seg)
            if k and k["art"]:
                kontakte.add((k["t"], k["art"], k["r"]))
                continue
            z = _ZUSATZ_KONTAKT_RE.search(seg)                           # (4)
            if z:
                ma = ASPEKT_RE.search(z.group("mitte"))
                if ma:
                    z_art = _art(ma.group(1)) if ma.group(1) else _ASP_GLYPH.get(ma.group(2))
                    kontakte.add((kanon(z.group("t")), z_art, kanon(z.group("r"))))
                    continue
            if form == "instrument":        # alle Angaben gehoeren zur Funktion des Segments
                st = _staende_segment(seg)
                fa = st["faktor"] if st else None
                eintr = _aspekt_eintraege(seg.split(" — ", 1)[-1], faktor_a=fa) if fa else []
            else:
                eintr = _aspekt_eintraege(seg)
            for e in eintr:
                if e["a"] and e["b"] and e["art"]:
                    paare.add((frozenset((e["a"], e["b"])), e["art"]))
    # Kontakte der Rechnung (Themenliste, TRANSIT-RECHENSCHAFT, Report, events.json) —
    # im Transit.
    kontakte.update(_kontakte_in(txt))
    for m in _REPORT_KONTAKT_RE.finditer(txt or ""):
        kontakte.add((kanon(m.group(1)), m.group(2), kanon(m.group(3))))
    if events is not None:
        kontakte.update(_ev_index(events).keys())

    paare_art = {fs for fs, _ar in paare}
    # (19d) die Transiter je Kapitel aus den Kontakten seines Belegs
    kap_transiter = {}
    if typ == "transit":
        for ch in chapters:
            ts_ = set()
            for seg in _segmente(ch.get("beleg") or ""):
                k_ = _kontakt_aus_segment(seg)
                if k_ and k_.get("t"):
                    ts_.add(k_["t"])
            kap_transiter[id(ch)] = tuple(sorted(ts_))
    kontakte_art = {frozenset((t, r)) for t, _ar, r in kontakte}

    def gedeckt(a, art, b):
        """art: Aspektart (str), Tupel erlaubter Arten (Bild) oder () — dann
        gedeckt, wenn IRGENDEIN Aspekt das Paar verbindet."""
        arten = (art,) if isinstance(art, str) else tuple(art or ())

        def spiegel(ars):
            return tuple(SPIEGEL_ASPEKT.get(x, x) for x in ars)
        kand = [(a, arten, b)]
        if "SUEDKNOTEN" in (a, b):          # Suedknoten: Spiegel des Nordknoten-Aspekts
            kand.append(("MONDKNOTEN" if a == "SUEDKNOTEN" else a, spiegel(arten),
                         "MONDKNOTEN" if b == "SUEDKNOTEN" else b))
        for x, y in ((a, b), (b, a)):       # Achsen-Spiegel: zum DC = Gegenaspekt zum AC
            if y in ACHSEN:
                kand.append((x, spiegel(arten), SPIEGEL_FAKTOR[y]))
        for x, ars, y in kand:
            if not ars:
                if frozenset((x, y)) in paare_art or frozenset((x, y)) in kontakte_art:
                    return True
            elif any((frozenset((x, y)), ar) in paare or (x, ar, y) in kontakte
                     or (y, ar, x) in kontakte for ar in ars):
                return True
        return False
    for ch, bewegung, text in _fliesstext(chapters):
        saetze = _saetze_pos(text)
        for i, (_a, _e, satz) in enumerate(saetze):
            gesehen = set()
            for davor, art, danach, m in _konstellationen(satz, saetze[i - 1][2] if i else "",
                                                          typ=typ):
                _schl = (str(art), m.start(), tuple(davor), tuple(danach))   # (15)
                if _schl in gesehen:
                    continue
                gesehen.add(_schl)
                paarungen = [(x, y) for x in reversed(davor) for y in danach
                             if _paar_ok(x, y, typ)                         # (3), (7)
                             and (x != y or _selbstpaar_im_satz(satz, x))]  # (10)
                if not paarungen:           # „Pluto … zu sich selbst": Zyklus, kein Radix-Aspekt
                    continue
                p.geprueft += 1
                if any(gedeckt(x, art, y) for x, y in paarungen):
                    continue
                if any(gedeckt(x2, art, y2) for x2, y2 in _p13_weitere_paare(      # (19)
                        satz, m, davor, danach, typ, saetze[i - 1][2] if i else "",
                        kap_transiter.get(id(ch), ())) if _paar_ok(x2, y2, typ)):
                    continue
                x, y = paarungen[0]
                if isinstance(art, str):
                    was = "%s %s %s steht in keinem Beleg und nicht in den Aspekttabellen" % (
                        ANZEIGE.get(x, x), art, ANZEIGE.get(y, y))
                elif art:
                    anders = sorted({e["art"] for e in tabelle
                                     if frozenset((e["a"], e["b"])) == frozenset((x, y))})
                    was = ("das Bild „%s“ steht für %s; %s–%s steht so in keinem Beleg und "
                           "nicht in den Aspekttabellen%s"
                           % (_ws(m.group(0)), " oder ".join(art), ANZEIGE.get(x, x),
                              ANZEIGE.get(y, y), " (Tabelle: %s)" % ", ".join(anders)
                              if anders else ""))
                else:
                    was = ("das Bild „%s“ verknüpft %s und %s — das Paar steht mit keiner "
                           "Aspektart in einem Beleg oder in den Aspekttabellen"
                           % (_ws(m.group(0)), ANZEIGE.get(x, x), ANZEIGE.get(y, y)))
                p.pruefen.append("%s · %s: „%s“ — %s%s" % (
                    _bezeichnung(ch), bewegung, _kurz(satz, 140), was,
                    " (auch nicht als Kontakt in Rechnung, Themenliste oder events.json)"
                    if typ == "transit" else ""))
    if p.geprueft == 0:
        p.hinweise.append("keine Konstellation mit Aspektwort im Fließtext")
    return p.abschluss()

# --- P14 Kopfblock -----------------------------------------------------------
# Die Kopfblock-Tabelle der Probe (2026-09-19, W10, W43) — Quelle: Design-Render-
# Modul, „Welches Kapitel welchen Kopfblock trägt", Klartext-Modul „Kopfblöcke",
# Transit-Modul Struktur 2–7 und Ablauf 2 (Kicker). Kapitelart -> (Signatur, Beleg).
# Vorher prueften P3/P7 nur „Kapitel N"; das Lagebild kam in vier von vier
# Transit-Laeufen ohne Kopfblock aus Schritt 2 und stoppte Schritt 3.
KOPFBLOCK = {
    "Auftakt": (False, False),           # Auftakt, Zur Lesart (Transit), Prelude
    "Rechenschaft": (False, False),
    "Mitlaufendes": (False, False),      # Register des Transits (W43)
    "Schlusswort": (False, False),
    "Teiler": (False, False),            # Teil I–III, Vertiefung, Zweiter Teil
    "Getriebe-Kapitel": (True, True),    # Kicker `Getriebe` (alt: Kapitel 1), Struktur-Beleg
    "Instrument": (True, True),          # ein Segment je Funktion
    "Themenkapitel": (True, True),       # auch Ressourcen-Kapitel
    "Zugang": (True, True),              # ein Segment je zugeordnetem Haus
    "Bündel-Kapitel": (True, False),     # Hauptthemen, Konfliktfelder, Lebensaufgaben
    "Lagebild": (True, True),            # Der Stand heute (Transit)
}
_TEILER_KICKER = {"teil i", "teil ii", "teil iii", "vertiefung", "erster teil", "zweiter teil",
                  "dritter teil", "part i", "part ii", "part iii", "first part", "second part",
                  "third part"}

def _kapitelart(ch, typ, chapters=None):
    """Kapitelart nach der Kopfblock-Tabelle, oder None (unbekannter Kicker).

    `chapters` (2026-09-19, L7) entscheidet, ob `Kapitel 1` das Getriebe-Kapitel
    ist (Analyse alter Form) oder das erste Themenkapitel (neue Form, in der das
    Getriebe-Kapitel den Wort-Kicker `Getriebe` traegt).
    """
    if _ist_kicker(ch, "Auftakt"):
        return "Auftakt"
    for art in ("Rechenschaft", "Mitlaufendes", "Schlusswort", "Instrument"):
        if _ist_kicker(ch, art):
            return art
    if (ch.get("kicker") or "").strip().casefold() in _TEILER_KICKER:
        return "Teiler"
    if _ist_kicker(ch, "Hauptthemen", "Konfliktfelder", "Lebensaufgaben"):
        return "Bündel-Kapitel"
    if _ist_zugang(ch):
        return "Zugang"
    if _ist_kicker(ch, "Der Stand heute"):
        return "Lagebild"
    # 2026-09-19 (L7): erst der Wort-Kicker, dann die Nummer der alten Form.
    if _getriebe_kapitel(ch, typ, chapters):
        return "Getriebe-Kapitel"
    if _kicker_nr(ch.get("kicker")) is not None:
        return "Themenkapitel"
    return None

def _p14_kopfblock(chapters, typ):
    p = _Probe("P14", "Kopfblock (Signatur und Beleg je Kapitelart)")
    p.einheit = "Kapitel"
    if not any((ch.get("signatur") or "").strip() or (ch.get("beleg") or "").strip()
               for ch in chapters):
        # Fachmodus (Kern): Aspektnamen, Grade und Termini im Fliesstext, KEIN
        # Signatur/Beleg-Kopf — dort ist das Fehlen die Regel, kein Fehler.
        return p.uebersprungen("kein Kapitel trägt Signatur oder Beleg — Fachmodus oder "
                               "Analyse ohne Klartext-Kopfblöcke; die Kopfblock-Tabelle gilt "
                               "nur im Klartext-Modus")
    for ch in chapters:
        bez = _bezeichnung(ch)
        art = _kapitelart(ch, typ, chapters)
        if art is None:
            p.hinweise.append("%s: Kicker „%s“ steht nicht in der Kopfblock-Tabelle der Probe — "
                              "nicht geprüft" % (bez, ch.get("kicker") or "—"))
            continue
        p.geprueft += 1
        sig_soll, bel_soll = KOPFBLOCK[art]
        sig = bool((ch.get("signatur") or "").strip())
        bel = bool((ch.get("beleg") or "").strip())
        fehlt = [n for n, soll, ist in (("Signatur", sig_soll, sig), ("Beleg", bel_soll, bel))
                 if soll and not ist]
        if fehlt:
            p.fehler.append("%s: %s %s — die Kopfblock-Tabelle verlangt für %s Signatur%s; "
                            "direkt unter die Kapitel-H2 setzen („**Signatur:** …“%s)"
                            % (bez, " und ".join(fehlt), "fehlen" if len(fehlt) > 1 else "fehlt",
                               art, " und Beleg" if bel_soll else " ohne Beleg",
                               ", „**Beleg:** …“" if bel_soll else ""))
        zuviel = [n for n, soll, ist in (("Signatur", sig_soll, sig), ("Beleg", bel_soll, bel))
                  if ist and not soll]
        if zuviel and art == "Bündel-Kapitel":
            # Design-Render-Modul, Kopfblock-Tabelle: „trägt eines der drei
            # Bündel-Kapitel einen Beleg, ebenfalls [ein Fehler in Schritt 2]".
            p.fehler.append("%s: trägt einen Beleg — die Bündel-Kapitel tragen nur eine "
                            "Signatur (sie machen kein neues Material auf); den Beleg streichen"
                            % bez)
        elif zuviel:
            p.pruefen.append("%s: trägt %s — laut Kopfblock-Tabelle hat %s %s"
                             % (bez, " und ".join(zuviel), art,
                                "nur eine Signatur" if sig_soll else "keinen Kopfblock"))
        if art == "Lagebild" and bel:
            segs = _segmente(ch["beleg"])
            st = _staende_segment(segs[0]) if segs else None
            kontakte = [k for k in (_kontakt_aus_segment(s) for s in segs[1:]) if k]
            if not kontakte:
                p.pruefen.append("%s: Lagebild-Beleg ohne Kontakt-Segment (T-… R-…) — Format: "
                                 "Segment 1 die Stände des zuerst genannten Ziels, je weiteres "
                                 "Segment ein Kontakt mit Orb am Stichtag" % bez)
            elif st and st["faktor"] != kontakte[0]["r"]:
                p.pruefen.append("%s: Segment 1 trägt die Stände von %s, der zuerst genannte "
                                 "Kontakt trifft %s — Beleg-Format des Lagebilds: Segment 1 = "
                                 "Stände des zuerst genannten Ziels"
                                 % (bez, ANZEIGE.get(st["faktor"], st["faktor"]),
                                    ANZEIGE.get(kontakte[0]["r"], kontakte[0]["r"])))
    if p.geprueft == 0:
        return p.aussagelos("kein Kapitel mit einem Kicker aus der Kopfblock-Tabelle")
    return p.abschluss()

# --- P15 Ressourcen-Tiefe ----------------------------------------------------
# Typmodul Geburtshoroskop, „Der Deutungsort", und Innere Arbeit, Pruefung 12:
# volle und einseitige Aspekte brauchen am Deutungsort mindestens DREI Saetze,
# Nebenaspekte mindestens EINEN; im Transit jeder Kontakt der Zaehlmenge drei
# (Transit-Modul, Teil 3). Maschinell geht nur eine Naeherung (G12-18, Rubrik 4):
# Anker ist ein Satz, der beide Faktoren nennt — oder zwei aufeinanderfolgende
# Saetze, die zusammen beide nennen („… dieser Mond. Er verschmilzt mit Saturn").
# Ab dem Anker zaehlt jeder Folgesatz derselben Bewegung (im Pflichtteil „Was
# trägt" desselben Absatzes: je Ressource ein Absatz), solange er einen der
# beiden oder keinen Faktor nennt — ein Satz allein ueber andere Faktoren beendet
# die Zaehlung. Massgeblich ist der laengste solche Lauf am Deutungsort. Nur
# PRUEFEN (W37).
_RESSOURCE_ZEILE_RE = re.compile(
    r"^\s*(?:[-*]\s+)?(?:T-\s*)?(?P<a>%s|Knoten)\s*(?P<g>[☌△⚹])\s*(?:R-\s*)?(?P<b>%s|Knoten)"
    r"(?:\s*\((?:AC|MC|DC|IC)\))?(?P<rest>.*?)Deutungsort\s*:\s*(?P<ort>.*)$"
    % (_FAKTOR_RE, _FAKTOR_RE))

def _abschnitte(ch):
    """Die Absaetze eines Kapitels, gruppiert nach ###-Bewegung: [[Absatz, …], …]."""
    out, akt = [], []
    for b in ch["blocks"]:
        if b.get("type") == "subhead":
            if akt:
                out.append(akt)
            akt = []
            continue
        akt.append(b["text"])
    if akt:
        out.append(akt)
    return out

# 2026-09-22 (W57-Nachzug, erster englischer Transit): Der Pflichtteil hiess dort
# „What Will Carry You Through"; die Probe suchte nur „What carries" und meldete
# darum alle zwoelf Ressourcen mit Deutungsort „Was traegt" als PRUEFEN. Gesucht ist
# der TITEL des Pflichtteils, nicht eine feste Formel — deshalb beide Verbformen und
# die uebliche Einschubstelle („you", „us") dazwischen.
_WAS_TRAEGT_KOPF_RE = re.compile(
    r"Was dich durch diese Zeit trägt"
    r"|What\s+(?:carries|will\s+carry)\b(?:\s+\w+){0,3}\s*(?:through|you|us)?", re.I)
_WAS_TRAEGT_INLINE_RE = re.compile(
    r"Was trägt\s*:"
    r"|What\s+(?:carries|will\s+carry)\b(?:\s+\w+){0,3}\s*:", re.I)

def _was_traegt_bloecke(chapters):
    """Absaetze des Pflichtteils: „Was trägt:" im Hauptthemen-Kapitel bis zum
    Kapitelende, im Transit `### Was dich durch diese Zeit trägt` bis zum
    naechsten Zwischentitel. None, wenn es ihn nicht gibt."""
    for ch in chapters:
        bl = ch["blocks"]
        for i, b in enumerate(bl):
            t = _ws(b["text"]).lstrip("„\"»")
            if b.get("type") == "subhead" and _WAS_TRAEGT_KOPF_RE.match(t):
                out = []
                for b2 in bl[i + 1:]:
                    if b2.get("type") == "subhead":
                        break
                    out.append(b2["text"])
                return out
            if b.get("type") != "subhead" and _WAS_TRAEGT_INLINE_RE.match(t):
                return [b2["text"] for b2 in bl[i:] if b2.get("type") != "subhead"]
    return None

def _saetze_am_ort(a, b, gruppen):
    """(laengster Lauf, Ankersatz) — s. Kommentar oben. gruppen: Liste von
    Absatzlisten; gezaehlt wird nie ueber eine Gruppe hinaus."""
    best, anker = 0, None
    paar = {a, b}
    for gruppe in gruppen:
        saetze = [s for text in gruppe for _x, _y, s in _saetze_pos(text)]
        fs = [{x for _, _, x in _faktoren_im_satz(s)} for s in saetze]
        for i, s in enumerate(saetze):
            zwei = (i + 1 < len(saetze) and fs[i] & paar and fs[i + 1] & paar
                    and paar <= (fs[i] | fs[i + 1]))
            if not (paar <= fs[i] or zwei):
                continue
            n = 1
            for f2 in fs[i + 1:]:
                if f2 and not (f2 & paar):
                    break
                n += 1
            if n > best:
                best, anker = n, s
    return best, anker

def _p15_ressourcen(chapters, typ, txt, zuordnung):
    p = _Probe("P15", "Ressourcen-Tiefe (Sätze am Deutungsort)")
    p.einheit = "Einträge"
    m = re.search(r"\n##\s+Ressourcen\b[^\n]*", "\n" + (txt or ""))
    if not m:
        return p.aussagelos("kein Abschnitt „## Ressourcen“ in der chart_data")
    teil = ("\n" + txt)[m.end():]
    schnitt = re.search(r"\n## |\n@@", teil)
    teil = teil[:schnitt.start()] if schnitt else teil
    kap_zu_thema = {th["nr"]: ch for ch in chapters for th in [zuordnung.get(id(ch))] if th}
    ab = _zaehlung_ab(chapters, typ)        # 2026-09-19 (L7)
    # Ohne Zuordnung aus P3 (EA, Ultimativ): das Kapitel mit dem Titel der
    # THEMA-Zeile, erst danach die Kapitelnummer (Thema n = Kapitel n + ab - 1).
    for th in _themenliste_lesen(txt):
        if th["nr"] not in kap_zu_thema and th.get("titel"):
            ch = next((c for c in chapters if _ws(c.get("title")).casefold()
                       == _ws(th["titel"]).casefold()), None)
            if ch is not None:
                kap_zu_thema[th["nr"]] = ch
    for zeile in teil.splitlines():
        # 2026-10-01 (Klasse-2-Entscheidungslauf, T4): Eine Zeile `Nachzug:` und ein
        # Nachzug-Vermerk in Klammern im Ortsfeld („Was trägt (Nachzug: vorher
        # Thema 2)“) sind Chronik, kein Deutungsort — P15 pruefte gegen den alten Ort.
        if "Deutungsort" not in zeile or re.match(
                r"^\s*(?:Zählmenge|\*\*|>|(?:[-*]\s+)?Nachzug\s*:)", zeile):
            continue
        mz = _RESSOURCE_ZEILE_RE.match(zeile)
        if not mz:
            if re.search(r"Deutungsort\s*:", zeile):
                p.pruefen.append("Ressourcen-Block: Zeile nicht lesbar „%s“ — erwartet „A △ B "
                                 "N°NN′ voll — Deutungsort: Thema n“ (Transit: „T-A △ R-B … — "
                                 "Deutungsort: …“)" % _kurz(zeile, 90))
            continue
        p.geprueft += 1
        a, b = kanon(mz.group("a")), kanon(mz.group("b"))
        ms = re.search(r"(?<![\wäöüß])(voll|einseitig|neben)(?![\wäöüß])", mz.group("rest"))
        stufe = ms.group(1) if ms else None
        soll = 1 if stufe == "neben" else 3
        name = "%s %s %s" % (ANZEIGE.get(a, a), mz.group("g"), ANZEIGE.get(b, b))
        ort = re.sub(r"\s*\(\s*Nachzug\b[^)]*\)", "", mz.group("ort")).strip()
        mo = re.search(r"(Thema|Ressource)\s+(\d+)", ort)
        if mo:
            n = int(mo.group(2))
            ch = kap_zu_thema.get(n) or next((c for c in chapters
                                              if _kicker_nr(c.get("kicker")) == n + ab - 1), None)
            if ch is None:
                p.pruefen.append("%s — Deutungsort %s: kein Kapitel zu diesem Thema gefunden"
                                 % (name, mo.group(0)))
                continue
            gruppen = _abschnitte(ch)
            wo = "%s (%s)" % (mo.group(0), ch.get("kicker"))
        elif re.search(r"Was\s+(?:dich\s+durch\s+diese\s+Zeit\s+)?trägt", ort):
            bloecke = _was_traegt_bloecke(chapters)
            gruppen = [[x] for x in (bloecke or [])]
            if bloecke is None:
                p.pruefen.append("%s — Deutungsort „Was trägt“, aber kein Pflichtteil „Was trägt:“ "
                                 "im Hauptthemen-Kapitel (Transit: „### Was dich durch diese Zeit "
                                 "trägt“ im Schlusswort)" % name)
                continue
            wo = "„Was trägt“"
        elif re.search(r"Mitlaufendes\s*\(\s*Deckel\s*\)|(?:Also\s+running|Running\s+alongside)"
                       r"\s*\(\s*cap\s*\)", ort, re.I):
            # 2026-09-24 (Klasse-2-Entscheidungslauf T10): Kontakte ueber dem Deckel von
            # sechs (Transit-Modul, „Der Deckel") stehen mit ihrer Zeile im Kapitel
            # `Mitlaufendes`. Gezaehlt wird dort kein Satz — die Zeile muss nur beide
            # Faktoren nennen. Bis dahin kannte P15 keine Schreibweise dafuer und meldete
            # jeden solchen Eintrag als unbekannten Deutungsort (Transit 18.09. bis 24.09.).
            if typ != "transit":
                p.pruefen.append("%s — Deutungsort „%s“ gibt es nur im Transit (Deckel)"
                                 % (name, _kurz(ort, 40)))
                continue
            reg = [c for c in chapters if _ist_kicker(c, "Mitlaufendes")]
            if not reg:
                p.pruefen.append("%s — Deutungsort „Mitlaufendes (Deckel)“, aber kein Kapitel "
                                 "„Mitlaufendes“" % name)
                continue
            _n, _anker = _saetze_am_ort(a, b, [g for c in reg for g in _abschnitte(c)])
            if _anker is None:
                p.pruefen.append("%s — über dem Deckel, aber keine Zeile im Kapitel "
                                 "„Mitlaufendes“ nennt beide Faktoren" % name)
            continue
        elif not ort:
            p.pruefen.append("%s — ohne Deutungsort (kein Eintrag ohne Deutungsort; wer keinen "
                             "bekommt, geht in „Was trägt“)" % name)
            continue
        else:
            p.pruefen.append("%s — Deutungsort „%s“ unbekannt (erwartet: Thema n, Ressource n, "
                             "Was trägt; im Transit auch Mitlaufendes (Deckel))" % (name, _kurz(ort, 40)))
            continue
        n_saetze, anker = _saetze_am_ort(a, b, gruppen)
        # Achsen-Spiegel (build seit 2026-09-19, F18): „Venus △ AC … (zugleich Sextil
        # DC)" ist EINE Gabe — der Text darf sie am anderen Ende der Achse deuten.
        msp = re.search(r"zugleich\s+\S+\s+(AC|MC|DC|IC)\b", mz.group("rest"))
        if msp:
            n2, anker2 = _saetze_am_ort(a if b in ACHSEN else b, msp.group(1), gruppen)
            if n2 > n_saetze:
                n_saetze, anker = n2, anker2
        if anker is None:
            p.pruefen.append("%s (%s) — am Deutungsort %s nennt kein Satz beide Faktoren; der "
                             "Aspekt ist dort nicht als Anker gedeutet" % (name, stufe or "Transit", wo))
        elif n_saetze < soll:
            p.pruefen.append("%s (%s) — am Deutungsort %s %d Satz/Sätze ab „%s“, verlangt sind "
                             "mindestens %d" % (name, stufe or "Transit", wo, n_saetze,
                                                _kurz(anker, 70), soll))
    if p.geprueft == 0 and not p.pruefen:
        return p.aussagelos("Ressourcen-Block ohne lesbare Zeile mit Deutungsort")
    return p.abschluss()


# ---------------------------------------------------------------------------
# P16 Laengen-Gegenprobe (2026-09-24, Klasse-2-Entscheidungslauf T3)
# ---------------------------------------------------------------------------
# Bis zum 2026-09-24 stand die Probe als Skript im Klartext-Modul, das jeder Lauf
# abtippte, mit einer eigenen Kickerliste: Sie zaehlte das Lagebild des Transits
# („Der Stand heute") mit, das Datenblatt-Modul nicht — im Transit-Prueflauf vom
# 24.09. ergab das 0,79 gegen 0,66. Hier gilt EINE Definition, die des
# Datenblatt-Moduls (Schritt 2, Schnittgrenze): gedeutet sind die Kapitel mit
# Bewegungsfolge (`Kapitel n`, Zugang) sowie Getriebe- und Instrument-Kapitel;
# Auftakt, Lagebild, Rechenschaft bzw. Mitlaufendes, Buendel-Kapitel und
# Schlusswort zaehlen nicht. Gezaehlt werden die Woerter der Absaetze und
# Zwischentitel, nicht Signatur und Beleg. Faellt das Mittel der letzten drei
# gedeuteten Kapitel unter LAENGE_SCHWELLE des Mittels der ersten drei, ist das ein
# FEHLER — ausser eines der letzten drei traegt form=kurz oder form=ressource
# (Themenliste) oder ist ein Zugang mit duenn=ja (ZUGANG-Block); dann steht die
# Erklaerung als Hinweis da. Unter vier gedeuteten Kapiteln sind erste und letzte
# drei dieselben: AUSSAGELOS.
LAENGE_SCHWELLE = 0.60

def _ist_gedeutet(ch):
    return (_kicker_nr(ch.get("kicker")) is not None or _ist_zugang(ch)
            or _ist_kicker(ch, "Getriebe", "Instrument"))

def _woerter(ch):
    return sum(len(_ws(b.get("text")).split()) for b in (ch.get("blocks") or ()))

def _zugang_duenn(ch, txt):
    """Traegt die ZUGANG-Zeile dieses Zugangs duenn=ja? Bereich aus dem Kicker
    (`Zugang Beruf` -> beruf); ohne Bereich genuegt irgendeine Zeile mit duenn=ja."""
    k = _ws(ch.get("kicker"))
    bereich = k.split(" ", 1)[1].casefold() if " " in k else ""
    for zeile in re.findall(r"(?m)^ZUGANG\s+\d+\s*\|.*(?:\n[ \t]+\|.*)*", txt or ""):
        if re.search(r"duenn\s*=\s*ja", zeile, re.I) and (not bereich or bereich in zeile.casefold()):
            return True
    return False

def _p16_laenge(chapters, typ, txt, themen, zuordnung):
    p = _Probe("P16", "Längen-Gegenprobe (letzte drei gegen erste drei gedeutete Kapitel)")
    p.einheit = "gedeutete Kapitel"
    ged = [(ch, _woerter(ch)) for ch in chapters if _ist_gedeutet(ch)]
    p.geprueft = len(ged)
    if len(ged) < 4:
        return p.aussagelos("%d gedeutete Kapitel — unter vier sind die ersten und die letzten "
                            "drei dieselben" % len(ged))
    erste = sum(w for _c, w in ged[:3]) / 3.0
    letzte = sum(w for _c, w in ged[-3:]) / 3.0
    if erste <= 0:
        return p.aussagelos("die ersten drei gedeuteten Kapitel tragen keinen Fließtext")
    q = letzte / erste
    p.hinweise.append(("erste drei im Mittel %d Wörter, letzte drei %d, Verhältnis %.2f "
                       "(Schwelle %.2f)" % (round(erste), round(letzte), q, LAENGE_SCHWELLE)
                       ).replace(".", ",")
                      + " — " + ", ".join("%s %d" % (_ws(c.get("kicker")), w) for c, w in ged))
    if q >= LAENGE_SCHWELLE:
        return p.abschluss()
    ab = _zaehlung_ab(chapters, typ)
    nach_nr = {t["nr"]: t for t in (themen or ())}
    erkl = []
    for ch, _w in ged[-3:]:
        th = (zuordnung or {}).get(id(ch))
        if th is None and _kicker_nr(ch.get("kicker")) is not None:
            th = nach_nr.get(_kicker_nr(ch.get("kicker")) - ab + 1)
        if th and th.get("form") in ("kurz", "ressource"):
            erkl.append("%s: form=%s" % (_ws(ch.get("kicker")), th["form"]))
        elif _ist_zugang(ch) and _zugang_duenn(ch, txt):
            erkl.append("%s: duenn=ja" % _ws(ch.get("kicker")))
    if erkl:
        p.hinweise.append("Abfall erklärt durch " + "; ".join(erkl))
    else:
        p.fehler.append("die letzten drei gedeuteten Kapitel haben im Mittel %d %% der ersten drei "
                        "(Schwelle %d %%) — die hinteren Kapitel werden nachgeschrieben, nicht "
                        "wegdiskutiert (Datenblatt-Modul, Schritt 2)"
                        % (round(q * 100), round(LAENGE_SCHWELLE * 100)))
    return p.abschluss()

# ---------------------------------------------------------------------------
# P17 Subjekt-Probe (2026-09-24, Klasse-2-Entscheidungslauf E5, Chris-Entscheidung)
# ---------------------------------------------------------------------------
# Innere Arbeit, Prinzip 1 und Pruefung 1: Die Person ist Subjekt des Satzes, nicht
# der Planet. Bis zum 2026-09-24 lief die Probe nur von Hand; in den Transit-
# Prueflaeufen vom 23.09.b und 24.09. fand der Lauf je 13 bis 14 Treffer, die kein
# Werkzeug meldete. Gesucht werden Planeten, Achsen, Zeichen, ein Haus mit
# Ordnungszahl und „die Seele" in Subjekt-Stellung: am Satz- oder Gliedanfang (auch
# hinter „;", „:", Gedankenstrich, Konjunktion), hinter einem Artikel oder
# Relativpronomen, das keiner Praeposition folgt, und hinter einem Verb
# (Umstellung: „wird Saturn zum Aufseher", „sitzen Mond und Jupiter"). Nicht hinter
# einer Praeposition oder einem Dativ-, Genitiv- oder Akkusativ-Artikel; „der" vor
# einem weiblichen Namen ist Dativ. Aufzaehlungen erben die Stellung ihres ersten
# Glieds („zu Sonne, Mond und Saturn"). Die Probe versteht keine Grammatik — jeder
# Treffer ist PRUEFEN.
# Zonen (Regel: Innere Arbeit, Pruefung 1):
#   streng        Bewegungen 1, 3, 4, 5 und 6 der Themenkapitel: jede
#                 Subjekt-Stellung ist ein Treffer.
#   Anker         Bewegung 2 („Was da arbeitet") und 7 (Rahmen bzw. „Zeit"): nichts,
#                 dort stehen die Anker.
#   Grundfassung  alles ohne Bewegungswortlaut — Getriebe, Instrument, die
#                 Pflichtteile („Was trägt", „Was dich durch diese Zeit trägt"),
#                 Auftakt, Lagebild, Register: Der Anker darf Subjekt sein, solange er
#                 verortet („steht", „bildet", „läuft über" — _P17_ANKERVERBEN);
#                 gemeldet wird jedes andere Verb („Saturn verlangt", „dein Mond im
#                 Widder braucht").
# Englische Analysen: uebersprungen (die Muster sind deutsch).
# 2026-09-25 (Wartungslauf zu den Pruefberichten vom 25.09.): In allen acht Laeufen
# kamen verortende Saetze als Handelnde — ein Adverb galt als Verb („steht auch
# Saturn"), ein Pluralverb auf -en als Adjektiv („Jupiter und Neptun stehen knapp"),
# „heißt" traf die Ankerliste wegen casefold() nie, das Bild „wo die Sonne untergeht"
# und das Objekt in „Du hast deine Sonne …" zaehlten mit. Umgekehrt uebersah die
# Probe den handelnden Relativsatz („Saturn, der die Verantwortung trägt").
_P17_NAMEN = frozenset((
    "Sonne", "Mond", "Merkur", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptun",
    "Pluto", "Chiron", "Lilith", "Mondknoten", "Nordknoten", "Südknoten", "Knoten",
    "Aszendent", "Deszendent", "AC", "MC", "DC", "IC", "Seele",
    "Widder", "Stier", "Zwillinge", "Krebs", "Löwe", "Jungfrau", "Waage", "Skorpion",
    "Schütze", "Steinbock", "Wassermann", "Fische"))
# „der" vor diesen Namen ist Dativ oder Genitiv, nie Nominativ
_P17_WEIBLICH = frozenset(("Sonne", "Venus", "Lilith", "Seele", "Waage", "Jungfrau",
                           "Zwillinge", "Fische"))
_P17_ORDINAL_RE = re.compile(r"^(?:\d{1,2}\.|erste|zweite|dritte|vierte|fünfte|sechste|"
                             r"siebte|achte|neunte|zehnte|elfte|zwölfte)$")
_P17_PRAEP = frozenset((
    "zu", "zum", "zur", "mit", "von", "vom", "bei", "beim", "an", "am", "ans", "auf", "aufs",
    "aus", "in", "im", "ins", "über", "unter", "vor", "vorm", "hinter", "neben", "zwischen",
    "gegen", "durch", "für", "um", "nach", "seit", "ohne", "bis", "wie", "als", "samt",
    "nahe", "entlang", "gegenüber", "trotz", "wegen", "statt", "innerhalb", "außerhalb",
    "dank", "laut", "je", "pro", "unterm", "überm", "hinterm"))
_P17_OBLIQ = frozenset((
    "dem", "den", "des", "deinem", "deinen", "deines", "deiner", "einem", "einen", "eines",
    "einer", "diesem", "diesen", "seinem", "seinen", "seines", "seiner", "ihrem", "ihren",
    "ihres", "ihrer", "jedem", "jeden", "keinem", "keinen", "keines", "keiner", "unserem",
    "unseren", "unseres", "unserer",
    "demselben", "denselben", "desselben", "derselben", "jenem", "jenen", "solchem",
    "solchen"))
_P17_NOM = frozenset((
    "der", "die", "das", "ein", "eine", "dein", "deine", "jeder", "jede", "jedes", "dieser",
    "diese", "dieses", "kein", "keine", "sein", "seine", "ihr", "ihre", "welcher", "welche",
    "welches", "unser", "unsere",
    "derselbe", "dieselbe", "dasselbe", "dieselben", "jener", "jene", "jenes", "solcher",
    "solche", "solches"))
_P17_PRONOMEN = frozenset((
    "du", "dich", "dir", "ich", "mich", "mir", "er", "sie", "es", "wir", "uns", "euch", "ihn",
    "ihm", "ihnen", "man", "sich", "jemand", "niemand", "etwas", "nichts", "alles"))
_P17_BINDER = frozenset((
    "und", "oder", "aber", "denn", "doch", "sondern", "weil", "wenn", "dass", "ob",
    "während", "obwohl", "sobald", "solange", "bevor", "nachdem", "damit", "sodass", "wo",
    "wohin", "woher", "falls", "indem", "sowie", "was", "wer", "da"))
_P17_BRUCH = frozenset((";", ":", "—", "–", "(", "„", "“", "\"", "»", "«"))
# Verben, mit denen ein Anker nur VERORTET (Stellung, Lauf, Struktur, Zugehoerigkeit).
# In der Grundfassung darf ein Name damit Subjekt sein; jedes andere Verb dahinter
# macht ihn zum Handelnden („Saturn verlangt", „dein Mond im Stier braucht") und wird
# gemeldet. Bewusst eine Erlaubt- statt einer Verbotsliste: Handlungsverben gibt es zu
# viele, als dass eine Liste sie faende.
_P17_ANKERVERBEN = frozenset((
    "steht", "stehen", "stand", "standen", "liegt", "liegen", "lag", "lagen", "sitzt",
    "sitzen", "saß", "saßen", "befindet", "befinden", "bildet", "bilden", "bildete",
    "bildeten", "läuft", "laufen", "lief", "liefen", "wandert", "wandern", "wanderte",
    "zieht", "ziehen", "zog", "trifft", "treffen", "traf", "berührt", "berühren",
    "berührte", "kreuzt", "kreuzen", "erreicht", "erreichen", "erreichte", "kehrt",
    "kehren", "kehrte", "geht", "gehen", "ging", "kommt", "kommen", "kam", "wird",
    "werden", "wurde", "wurden", "ist", "sind", "war", "waren", "wäre", "hat", "haben",
    "hatte", "hatten", "heißt", "heißen", "bedeutet", "bedeuten", "gehört", "gehören",
    "zählt", "zählen", "folgt", "folgen", "herrscht", "herrschen", "regiert", "regieren",
    "verwaltet", "verwalten", "disponiert", "teilt", "teilen", "fällt", "fallen", "fiel",
    "wechselt", "wechseln", "klingt", "klingen", "zeigt", "zeigen", "beschreibt",
    "beschreiben", "markiert", "verbindet", "verbinden", "bleibt", "bleiben", "blieb",
    "rückt", "rücken", "nähert", "nähern", "entfernt", "steigt", "steigen", "beginnt",
    "beginnen", "endet", "enden", "schließt", "schließen", "reicht", "reichen",
    "überquert", "passiert", "durchläuft", "verlässt", "betritt", "streift",
    "quadriert", "opponiert",
    # 2026-09-25 (Pruefberichte vom 25.09.): Horizont-Verben („wo die Sonne
    # untergeht" ist das Bild des Horizonts, kein Handeln), zusammengesetzte Formen
    # und die Partizipien der Ankerverben („hat … gestanden")
    "aufgeht", "aufgehen", "aufging", "aufgingen", "untergeht", "untergehen",
    "unterging", "untergingen", "gegenübersteht", "gegenüberstehen", "gegenüberstand",
    "gegenüberliegt", "gegenüberliegen", "zusammenläuft", "zusammenlaufen",
    "zusammentrifft", "zusammentreffen", "vorbeizieht", "vorbeiziehen", "zurückläuft",
    "zurücklaufen", "wären", "hätte", "hätten", "würde", "würden",
    "gestanden", "gelegen", "gesessen", "befunden", "gebildet", "gelaufen", "gewandert",
    "gezogen", "getroffen", "gekreuzt", "gekehrt", "gegangen", "gekommen", "geworden",
    "gewesen", "gehabt", "geheißen", "gezählt", "gefolgt", "geherrscht", "geteilt",
    "gefallen", "gewechselt", "geklungen", "gezeigt", "beschrieben", "verbunden",
    "geblieben", "gerückt", "genähert", "gestiegen", "begonnen", "geendet", "geschlossen",
    "gereicht", "durchlaufen", "verlassen", "betreten", "gestreift", "aufgegangen",
    "untergegangen"))
# 2026-09-25 (Pruefberichte vom 25.09., P17 in allen acht Laeufen): Adverbien und
# Partikeln zwischen Verb und Name oder hinter dem Namen („steht auch Saturn", „steht
# allein Venus", „dein Mars genau auf …") galten als Verb und machten den Namen zum
# Handelnden — 2 bis 8 PRUEFEN je Lauf, keines zutreffend. Sie werden uebersprungen.
_P17_ADVERB = frozenset((
    "auch", "nur", "allein", "dagegen", "hingegen", "jedoch", "zudem", "außerdem",
    "ebenfalls", "ebenso", "gleichfalls", "noch", "schon", "bereits", "erst", "gerade",
    "genau", "knapp", "ganz", "fast", "beinahe", "nahezu", "kaum", "sogar", "selbst",
    "wiederum", "also", "dann", "dort", "hier", "jetzt", "nun", "heute", "damals",
    "zugleich", "gleichzeitig", "derzeit", "zuerst", "zuletzt", "wieder", "immer", "oft",
    "manchmal", "stets", "nie", "niemals", "nicht", "zwar", "eben", "etwa", "vielleicht",
    "wohl", "ja", "nämlich", "eigentlich", "besonders", "insbesondere", "ausgerechnet",
    "vorn", "vorne", "hinten", "oben", "unten", "mitten", "weit", "exakt", "ungefähr",
    "rund", "sehr", "so", "mehr", "weniger", "meist", "meistens", "deshalb", "daher",
    "darum", "trotzdem", "dennoch", "dazu", "dabei", "davon", "darin", "darauf",
    "daneben", "dahinter", "darüber", "darunter", "danach", "davor", "dafür", "sonst",
    "zusammen", "gemeinsam", "einzig", "lediglich", "bloß", "direkt", "unmittelbar",
    "zeitgleich", "tatsächlich", "wirklich", "dicht", "eng", "schließlich", "letztlich",
    "ohnehin", "längst", "bald", "später", "früher", "vorher", "nachher", "somit",
    "folglich", "rückläufig"))
# Zahl- und Mengenwoerter („bilden die engste Verbindung zwischen zwei …") sind kein Verb
_P17_ZAHL = frozenset((
    "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf",
    "zwölf", "beide", "beiden", "alle", "allen", "aller", "viele", "vielen", "einige",
    "einigen", "mehrere", "mehreren", "wenige", "wenigen", "manche", "manchen"))
# Objekt-Pronomen hinter dem Namen („Uranus steht ihm gegenüber", „weil Saturn dir
# Halt gibt") — das Verb steht dahinter
_P17_OBJEKT = frozenset(("ihm", "ihr", "ihn", "ihnen", "dir", "dich", "mir", "mich", "uns",
                         "euch", "sich", "es", "einander"))
# Subjekt im selben Glied VOR dem Namen („Du hast deine Sonne am Deszendenten") —
# dann ist der Name Objekt
_P17_SUBJEKT_PRONOMEN = frozenset(("du", "ich", "wir", "man", "er"))
# Hilfsverben: hinter „hat"/„wird" entscheidet das Partizip bzw. der Infinitiv am
# Gliedende („Merkur hat es geprüft", „wird Saturn Geduld verlangen"); fehlt es,
# entscheidet das Hilfsverb selbst („wird Saturn zum Aufseher"). „ist … verschaltet"
# ist Zustand und bleibt Anker.
_P17_HABEN = frozenset(("hat", "haben", "hatte", "hatten", "hätte", "hätten"))
_P17_WERDEN = frozenset(("wird", "werden", "wurde", "wurden", "würde", "würden"))
_P17_REL = frozenset(("der", "die", "das", "welcher", "welche", "welches"))
# 2026-09-27 (Klasse-2-Entscheidungslauf, E4, Chris-Freigabe): Die Aspektbilder der
# Uebersetzungstabelle des Klartext-Moduls fuer Konjunktion, Quadrat und Trigon
# („verschmilzt mit", „reibt sich an", „fließt mühelos mit") verorten — sie nennen die
# Beziehung zweier Faktoren, kein Handeln am Leser. Vorher meldete P17 genau die Saetze,
# die die Tabelle vorschreibt, als Handeln (Geburtshoroskop 1+2 vom 25.09. und 26.09.b).
# Gemeldet bleiben die Bilder, die auf den Leser wirken („setzt dich unter Druck",
# „drängt gegen", „zwingt zu", „bietet dir").
_P17_ANKERVERBEN = _P17_ANKERVERBEN | frozenset((
    "verschmilzt", "verschmelzen", "verschmolz", "verschmolzen",
    "reibt", "reiben", "rieb", "rieben", "gerieben",
    "fließt", "fließen", "floss", "flossen", "geflossen"))
# Die Vergleiche laufen ueber casefold(), und casefold() macht aus „ß" „ss": „heißt"
# traf „heisst" nie, „außerhalb" nie „ausserhalb" (2026-09-25 — „der Deszendent
# heißt" kam deshalb als Handelnder). Alle Vergleichslisten werden ebenso gefaltet.
(_P17_PRAEP, _P17_OBLIQ, _P17_NOM, _P17_PRONOMEN, _P17_BINDER, _P17_ANKERVERBEN, _P17_ADVERB,
 _P17_ZAHL, _P17_OBJEKT, _P17_SUBJEKT_PRONOMEN, _P17_HABEN, _P17_WERDEN, _P17_REL) = (
    frozenset(w.casefold() for w in _l) for _l in (
        _P17_PRAEP, _P17_OBLIQ, _P17_NOM, _P17_PRONOMEN, _P17_BINDER, _P17_ANKERVERBEN,
        _P17_ADVERB, _P17_ZAHL, _P17_OBJEKT, _P17_SUBJEKT_PRONOMEN, _P17_HABEN, _P17_WERDEN,
        _P17_REL))
# 2026-09-28 (Pruefberichte vom 28.09.: Geburtshoroskop 1+2 Klasse 1, Transit 1+2
# Klasse 2 — gleiche Ursache): P17 nahm ein Wort, das kein Verb sein kann, als Verb.
# „steht zusätzlich Uranus" — das Adverb fehlte in der Liste; „die Jungfrau Merkurs
# eigenes Zeichen ist" — das Beiwort hinter dem Genitiv galt als Verb (nicht das „ist"
# am Satzende, wie der Bericht vermutete). Adverbien erkennt die Probe jetzt auch an
# der Endung (auf -lich, -weise, -mals, -falls, -dings, -wärts endet kein finites
# Verb), und ein Beiwort hinter einem Namen im Genitiv („Merkurs", „Mondes") gehoert
# zum folgenden Nomen.
_P17_ADVERB = _P17_ADVERB | frozenset(w.casefold() for w in (
    "zusätzlich", "erneut", "weiterhin", "inzwischen", "mittlerweile", "zunächst",
    "überdies", "ferner", "anfangs", "sofort", "zwischendurch", "vorübergehend",
    "anschließend", "kurzzeitig", "zeitweilig"))
_P17_ADVERB_ENDUNG = ("lich", "weise", "mals", "falls", "dings", "wärts")
# 2026-09-29 (Pruefberichte vom 29.09.: Geburtshoroskop 1+2 c Klasse 1 und 1+2 a,
# Transit 1+2 Klasse 1 — Z-28.09. Nr. 3): zwei Luecken, dasselbe Symptom, ein
# verortender Satz kam als Handeln. (1) „hängen" (Herrscherkette, Anbindung: „über
# Uranus hängen Sonne, Venus und Mars am selben Kreis", „Pluto hängt an nur zwei
# Leitungen") fehlte in der Ankerliste. (2) Im Nebensatz steht das finite Verb am
# Gliedende; ein Beiwort ohne Adverb-Endung zwischen Name und Verb („wenn auch
# Saturn harmonisch zu deinem Mond steht") galt als Verb. Hinter einer
# unterordnenden Konjunktion entscheidet jetzt das Verb am Gliedende
# (_p17_nebensatz_verb) — das faengt umgekehrt auch „weil Saturn im Stier steht und
# dich prüft" (vorher entschied „steht").
_P17_ANKERVERBEN = _P17_ANKERVERBEN | frozenset(w.casefold() for w in (
    "hängt", "hängen", "hing", "hingen", "gehangen", "zusammenhängt", "zusammenhängen"))
_P17_SUBJUNKTION = frozenset(w.casefold() for w in (
    "weil", "wenn", "dass", "ob", "während", "obwohl", "obgleich", "sobald", "solange",
    "bevor", "nachdem", "damit", "sodass", "wo", "wohin", "woher", "falls", "indem", "da",
    "was", "seitdem", "sofern", "soweit", "wobei", "ehe"))

def _p17_ist_adverb(t):
    """Adverb aus der Liste oder an der Endung erkennbar (2026-09-28)."""
    tl = t.casefold()
    return tl in _P17_ADVERB or (t[:1].islower() and len(tl) > 5
                                 and tl.endswith(_P17_ADVERB_ENDUNG))

def _p17_genitiv(t):
    """Name im Genitiv („Merkurs", „Saturns", „Mondes", „Krebses") — ein Beiwort
    dahinter gehoert zum folgenden Nomen (2026-09-28)."""
    return (t[:1].isupper() and len(t) > 3 and t.endswith("s")
            and (t[:-1] in _P17_NAMEN or (t.endswith("es") and t[:-2] in _P17_NAMEN)))

_P17_TOKEN_RE = re.compile(r"\d{1,2}\.(?=\s+Haus\b)|[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*"
                           r"|[;:—–,(„“\"»«]")

def _p17_name(tok):
    """Kopf eines Tokens, wenn es ein gesuchter Name ist: `Widder-Mond` -> Mond;
    `Saturn-Rückkehr` -> None (der Name ist Bestimmungswort, nicht Kopf)."""
    teile = tok.split("-")
    return teile[-1] if teile[-1] in _P17_NAMEN else None

def _p17_ist_adjektiv(tok):
    t = tok.casefold()
    return (tok[:1].islower() and len(t) > 3 and t.endswith(("e", "en", "er", "es", "em"))
            and t not in _P17_PRAEP and t not in _P17_OBLIQ and t not in _P17_NOM
            and t not in _P17_BINDER and t not in _P17_PRONOMEN) or bool(_P17_ORDINAL_RE.match(tok))

def _p17_ohne_adverb(tok, j):
    """Index des ersten Worts ab j rueckwaerts, das kein Adverb ist (2026-09-25)."""
    while j >= 0 and _p17_ist_adverb(tok[j]):
        j -= 1
    return j

def _p17_ist_verbwort(t):
    """Kann das Wort ein Verb sein? Kleingeschrieben und kein Funktionswort (Artikel,
    Praeposition, Pronomen, Konjunktion, Adverb, Zahlwort) — 2026-09-25."""
    tl = t.casefold()
    return (t[:1].islower() and t.isalpha() and len(t) > 1 and tl not in _P17_PRAEP
            and tl not in _P17_OBLIQ and tl not in _P17_NOM and tl not in _P17_PRONOMEN
            and tl not in _P17_BINDER and not _p17_ist_adverb(t) and tl not in _P17_ZAHL
            and not _P17_ORDINAL_RE.match(t))

def _p17_subjekt_davor(tok, i):
    """Steht im selben Glied vor dem Namen ein Subjekt-Pronomen („Du hast deine
    Sonne …", „wenn du deine Sonne …")? Dann ist der Name Objekt (2026-09-25)."""
    k = i - 1
    while k >= 0 and tok[k] not in _P17_BRUCH and tok[k] != "," \
            and tok[k].casefold() not in _P17_BINDER:
        if tok[k].casefold() in _P17_SUBJEKT_PRONOMEN:
            return True
        k -= 1
    return False

def _p17_nach_hilfsverb(tok, k, hilfs):
    """Hinter „hat"/„wird" (Token k oder davor) entscheidet das letzte Wort des
    Glieds, wenn es ein Partizip oder Infinitiv ist; sonst das Hilfsverb selbst."""
    e = k + 1
    while e < len(tok) and tok[e] not in _P17_BRUCH and tok[e] != ",":
        e += 1
    letzt = tok[e - 1] if e - 1 > k else ""
    lt = letzt.casefold()
    if letzt and _p17_ist_verbwort(letzt) and (lt.endswith(("en", "ern", "eln", "t"))
                                               or lt.startswith("ge")):
        return lt
    return hilfs

def _p17_relativverb(tok, i):
    """Name mit Relativsatz („Saturn, der die Verantwortung trägt, …"): das Verb am
    Gliedende, wenn es handelt; sonst None. Ein Subjekt-Pronomen im Relativsatz
    („die Sonne, die du bist") macht das Relativpronomen zum Objekt (2026-09-25)."""
    if i + 3 >= len(tok) or tok[i + 1] != "," or tok[i + 2].casefold() not in _P17_REL:
        return None
    k = i + 3
    while k < len(tok) and tok[k] not in _P17_BRUCH and tok[k] != ",":
        k += 1
    glied = tok[i + 3:k]
    if not glied or any(t.casefold() in _P17_SUBJEKT_PRONOMEN for t in glied):
        return None
    verb = glied[-1]
    if verb.casefold() in _P17_HABEN | _P17_WERDEN and len(glied) > 1 \
            and _p17_ist_verbwort(glied[-2]):
        verb = glied[-2]                    # „der dich geprägt hat" -> geprägt
    vl = verb.casefold()
    if not _p17_ist_verbwort(verb) or vl in _P17_ANKERVERBEN:
        return None
    return vl

def _p17_kandidaten(satz):
    """[(Name, Token-Index, Art)] fuer jeden Namen in Subjekt-Stellung; Art: start
    (Satz-/Gliedanfang), artikel, verb:<Verb davor> (Umstellung, auch vor einem
    Artikel: „steht deine Sonne"), reihe (erbt vom Glied davor), relativ:<Verb>
    (Name mit handelndem Relativsatz). Adverbien davor werden uebersprungen, ein
    Subjekt-Pronomen im selben Glied davor macht den Name zum Objekt."""
    tok = _P17_TOKEN_RE.findall(satz)
    namen = []                              # (i, name, ist_kandidat, art)
    for i, t in enumerate(tok):
        name = _p17_name(t)
        if name is None and t == "Haus" and i > 0 and _P17_ORDINAL_RE.match(tok[i - 1]):
            name = "Haus"
        if name is None:
            continue
        # Reihe: „zu Sonne, Mond und Saturn" — erbt die Stellung des vorigen Namens,
        # wenn zwischen beiden nur Komma, und/oder und hoechstens zwei Woerter stehen
        if namen and i - namen[-1][0] <= 4 and tok[i - 1] in (",", "und", "oder", "sowie"):
            _i0, _n0, kand0, a0 = namen[-1]
            namen.append((i, name, kand0, a0 if a0.startswith("verb:") else "reihe"))
            continue
        j = i - 1
        if name == "Haus":
            j -= 1                          # die Ordnungszahl gehoert zum Namen
        # Adjektive nur zwischen Artikel bzw. Praeposition und Name ueberspringen
        # („der laufende Jupiter", „mit ganzer Seele") — sonst ist das Wort davor ein
        # Verb auf -en („sitzen Mond und Jupiter") und bleibt stehen
        k = j
        while k >= 0 and _p17_ist_adjektiv(tok[k]) and i - k <= 3:
            k -= 1
        if k != j and k >= 0 and (tok[k].casefold() in _P17_NOM or tok[k].casefold() in _P17_OBLIQ
                                  or tok[k].casefold() in _P17_PRAEP):
            j = k
        # 2026-09-25: Adverbien davor ueberspringen („steht auch Saturn", „steht allein
        # Venus") — bis dahin galt das Adverb als vorangestelltes Verb
        j = _p17_ohne_adverb(tok, j)
        if j < 0 or tok[j] in _P17_BRUCH or tok[j] == ",":
            kand, art = True, "start"
        else:
            vor = tok[j].casefold()
            if vor in _P17_PRAEP or vor in _P17_OBLIQ or vor in _P17_PRONOMEN:
                kand, art = False, ""
            elif vor in _P17_NOM:
                davor = tok[j - 1].casefold() if j > 0 else ""
                if davor in _P17_PRAEP or (vor == "der" and name in _P17_WEIBLICH):
                    kand, art = False, ""
                else:
                    kand, art = True, "artikel"
                    # 2026-09-25: Steht vor dem Artikel ein Verb („steht deine Sonne",
                    # „bildet dein Merkur"), ist das die Umstellung — dieses Verb
                    # entscheidet, nicht das erste Wort hinter dem Namen
                    v = _p17_ohne_adverb(tok, j - 1)
                    if v >= 0 and _p17_ist_verbwort(tok[v]):
                        art = "verb:" + tok[v].casefold()
            elif vor in _P17_BINDER:
                kand, art = True, "start"
            elif tok[j][:1].isupper():
                kand, art = False, ""       # Apposition oder Satzanfang eines Nomens
            else:
                kand, art = True, "verb:" + tok[j].casefold()
        if kand and _p17_subjekt_davor(tok, i):     # 2026-09-25: „Du hast deine Sonne …"
            kand, art = False, ""
        namen.append((i, name, kand, art))
    out = [(n, i, a) for i, n, k, a in namen if k]
    # 2026-09-25: Relativsatz mit dem Namen als Bezugswort und handelndem Verb
    # („Saturn, der die Verantwortung trägt", „eine Venus, die … übersetzt") —
    # bis dahin von keiner Stellung erfasst (Geburtshoroskop 1+2 vom 25.09., 1.4)
    for i, name, _k, _a in namen:
        verb = _p17_relativverb(tok, i)
        if verb:
            out.append((name, i, "relativ:" + verb))
    return out, tok

def _p17_folgeverb(tok, i):
    """Das erste Verb-Wort hinter dem Namen: ueberspringt Praepositionalgruppen
    („dein Mond im Widder fühlt"), Artikel, Adverbien, Zahlwoerter und
    Objekt-Pronomen, hoechstens acht Woerter weit. (2026-09-25) Ein Ankerverb gilt
    sofort; ein Wort auf -en usw. ist nur hinter Artikel, Praeposition, Zahl oder
    Adjektiv ein Adjektiv („im stillen Wasser") — direkt hinter einem Namen ist es
    das Verb („Jupiter und Neptun stehen"); hinter „hat"/„wird" entscheidet das
    Partizip bzw. der Infinitiv am Gliedende."""
    k, n = i + 1, 0
    while k < len(tok) and n < 8:
        t = tok[k]
        tl = t.casefold()
        if t in _P17_BRUCH or t == ",":
            return None
        if tl in _P17_HABEN or tl in _P17_WERDEN:
            return _p17_nach_hilfsverb(tok, k, tl)
        if tl in _P17_ANKERVERBEN:
            return tl
        vl = tok[k - 1].casefold()
        adjektiv = _p17_ist_adjektiv(t) and (vl in _P17_NOM or vl in _P17_OBLIQ
                                             or vl in _P17_PRAEP or vl in _P17_ZAHL
                                             or _p17_ist_adjektiv(tok[k - 1])
                                             or _p17_genitiv(tok[k - 1]))
        if (tl in _P17_PRAEP or tl in _P17_OBLIQ or tl in _P17_NOM or t[:1].isupper()
                or tl in ("und", "oder", "sowie") or _p17_ist_adverb(t)
                or tl in _P17_ZAHL or tl in _P17_OBJEKT
                or _P17_ORDINAL_RE.match(t) or adjektiv):
            k, n = k + 1, n + 1
            continue
        return tl
    return None

def _p17_nebensatz_verb(tok, i):
    """Steht der Name in einem Nebensatz mit Verb am Ende („wenn auch Saturn
    harmonisch zu deinem Mond steht", „weil dein Mond und Venus … stehen")? Dann das
    Verb am Gliedende (bei „hat"/„wird" das Partizip bzw. der Infinitiv davor), sonst
    None. Rueckwaerts werden Artikel, Beiwoerter, Adverbien und die Glieder einer
    Aufzaehlung von Namen uebersprungen; das Glied endet am Satzzeichen oder an einem
    Komma, hinter dem keine Aufzaehlung weitergeht (2026-09-29)."""
    j = i - 1
    while j >= 0:
        t = tok[j]
        tl = t.casefold()
        if (_p17_name(t) or t == "Haus" or t == "," or tl in ("und", "oder", "sowie")
                or tl in _P17_NOM or _p17_ist_adverb(t) or _p17_ist_adjektiv(t)
                or _P17_ORDINAL_RE.match(t)):
            j -= 1
            continue
        break
    if j < 0 or tok[j].casefold() not in _P17_SUBJUNKTION:
        return None
    e = i + 1
    while e < len(tok) and tok[e] not in _P17_BRUCH:
        if tok[e] == ",":
            nxt = tok[e + 1] if e + 1 < len(tok) else ""
            if not (_p17_name(nxt) or nxt.casefold() in _P17_NOM):
                break
        e += 1
    if e - 1 <= i:
        return None
    letzt = tok[e - 1]
    lt = letzt.casefold()
    if (lt in _P17_HABEN or lt in _P17_WERDEN) and e - 2 > i and _p17_ist_verbwort(tok[e - 2]):
        return tok[e - 2].casefold()
    if lt in _P17_ANKERVERBEN or _p17_ist_verbwort(letzt):
        return lt
    return None

def _p17_handelt(tok, i, art):
    """Grundfassung: Handelt der Name? Ja, wenn das Verb davor (Umstellung) oder das
    erste Verb dahinter kein verortendes ist. (2026-09-25) Bei „hat"/„wird" davor
    entscheidet das Partizip bzw. der Infinitiv am Gliedende; ein Relativsatz-Treffer
    handelt immer — Kandidat wird er nur mit handelndem Verb."""
    if art.startswith("relativ:"):
        return True
    if art.startswith("verb:"):
        verb = art[5:]
        if verb in _P17_HABEN or verb in _P17_WERDEN:
            verb = _p17_nach_hilfsverb(tok, i, verb)
    else:
        # 2026-09-29: im Nebensatz entscheidet das Verb am Gliedende
        verb = _p17_nebensatz_verb(tok, i) or _p17_folgeverb(tok, i)
    return bool(verb) and verb not in _P17_ANKERVERBEN

def _p17_zone(bewegung, typ):
    if not bewegung:
        return "grund"
    t = _ws(bewegung).casefold()
    for idx, eintrag in enumerate(WORTLAUTE.get(typ) or ()):
        namen = eintrag if isinstance(eintrag, tuple) else (eintrag,)
        if any(t == n.casefold() for n in namen):
            return "anker" if idx in (1, 6) else "streng"
    return "grund"

def _p17_subjekt(chapters, typ, sprache_analyse="de"):
    p = _Probe("P17", "Subjekt-Probe (Planet, Zeichen, Haus oder Seele als Satzsubjekt)")
    p.einheit = "Sätze"
    if sprache_analyse == "en":
        return p.uebersprungen("englische Fassung — die Muster der Subjekt-Probe sind deutsch")
    if typ not in TYPEN:
        return p.uebersprungen("Typ unbekannt — die Bewegungswortlaute fehlen")
    for ch in chapters:
        bewegung = None
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bewegung = _ws(b["text"])
                continue
            zone = _p17_zone(bewegung, typ)
            if zone == "anker":
                continue
            for _a, _e, satz in _saetze_pos(b["text"]):
                p.geprueft += 1
                kand, tok = _p17_kandidaten(satz)
                if zone == "grund":
                    kand = [(n, i, a) for n, i, a in kand if _p17_handelt(tok, i, a)]
                if not kand:
                    continue
                wer = ", ".join(dict.fromkeys(n for n, _i, _a in kand))
                p.pruefen.append("%s · %s: „%s“ — %s als Satzsubjekt (%s)" % (
                    _ws(ch.get("kicker")), bewegung or _ws(ch.get("title")), _kurz(satz, 110), wer,
                    "außerhalb von Thema und Rahmen" if zone == "streng"
                    else "als Handelnder, nicht als Anker"))
    if p.geprueft == 0:
        return p.aussagelos("kein Fließtext außerhalb der Anker-Bewegungen")
    return p.abschluss()

# ---------------------------------------------------------------------------
# Hauptaufrufe
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# P18 Satzarten (2026-10-04, Wartungslauf „Satzarten-Probe“)
# ---------------------------------------------------------------------------
# Warum es P18 gibt: In den fuenf Pruefdurchgaengen vom 03./04.10. fanden die
# Zweitleser in Schritt 3+4 28 Sachfehler im Text, alle Ausrutscher; der schlanke
# Faktenleser, der zehn davon allein fand, laeuft nur in den Pruefdurchgaengen.
# Chris-Entscheidung 2026-10-04: eine Probe nach SATZARTEN, die als Programm laeuft
# und schon in Schritt 2 greift. Geprueft wird jede Satzart, in der seit dem 02.10.
# ein Sachfehler stand und die sich gegen Datenblatt, Analyse oder events.json
# halten laesst (Startprompt `STARTPROMPT_Satzarten_Probe_2026-10-04.md`).
#
# Zwei Regeln tragen die ganze Probe:
# (a) NUR PRUEFEN, nie FEHLER — und nur, wenn die Daten der Aussage WIDERSPRECHEN.
#     Eine Aussage, die sich nicht pruefen laesst (Bezug unklar, Zeitangabe ohne
#     Kontakt, Pronomen ohne Bezug), bleibt still. Fehlalarme sind das eigentliche
#     Fehlerpotential: Jeder zwingt einen Lauf, einen richtigen Satz umzuschreiben.
# (b) Jeder Hinweis nennt den Datenwert, der widerspricht („Haus 1: Sonne,
#     Merkur"), damit der Lauf nicht suchen muss.
#
# Die Satzarten (Kennwort vorn in jedem Hinweis):
#   Leere          „ist leer", „dort steht nichts", „kein Planet steht im …",
#                  „allein von X besetzt" — gegen ALLE Faktoren der Staendetabelle
#                  (Achsen nur, wenn der Satz sie nennt; Suedknoten getrennt genannt,
#                  er allein loest nichts aus — Chris-Entscheidung 2026-10-04).
#                  „dort" zeigt auf das zuletzt genannte Glied (meist das Haus —
#                  naechstliegende Lesart der Pruefberichte vom 04.10.); nennt der
#                  Satz selbst Zeichen UND Haus als Bereich, zaehlt nur, wer in beiden
#                  steht. Was der Satz selbst nennt, zieht er ab („sonst nichts").
#   Herrscher      „Verwalter des n. Hauses", „verwaltet dein n. Haus", „sein Haus",
#                  „im eigenen Haus", „auf eigenem Boden", „im eigenen Zeichen"
#                  — gegen Strukturbild §3 und die Domizile.
#   Kapitelverweis „Kapitel n zeigt X und Y" — ein PAAR, das in Kapitel n weder unter
#                  aspekte= noch unter verweis= steht, wohl aber in einem anderen; dazu
#                  Titel („Kapitel n, „…“") und Abschnitte („der Abschnitt „X“") gegen
#                  die Ueberschriften.
#   Signatur       Buendel-Kapitel „Zusammengefuehrt aus Kapitel …": jeder Absatz,
#                  dessen Faktoren nur Kapitel ausserhalb der Liste fuehren.
#   Modulwort      Werkstattwoerter der Module im Lesetext („Pflichtteil" u. a.).
#   Dokument       „steht in der Aspekttabelle" — gegen die Tabellen der chart_data
#                  (Untergrund nur mit gedeutet=ja).
#   Rang           seit 2026-10-13 (Strang 2, Chris-Entscheidung a4): mit „deines
#                  ganzen Bildes“, „alle Faktoren gezählt“, „unter allen gerechneten“
#                  zaehlt JEDER Untergrund-Aspekt, auch ungedeutet; ohne Zusatz gilt die
#                  Rangzeile (P12) — die Regel vom 04.10. (gedeuteter Untergrund neben
#                  „die engste Verbindung“) entfaellt. Dazu „enger als jede andere“,
#                  „sonst nirgends“, „keine so eng wie“: Rang 1 ohne Gleichstand.
#   Anteil         „alles andere haelt fest" — gegen die Modus-/Element-Zaehlung.
#   Naehe (2026-10-13, Strang 2; Abschnitt vor _p18_daten): „genau am/auf“, „am selben
#                  Punkt wie“, „zu einem Punkt“, „gradgenau/exakt im <Aspekt>“, „genau
#                  gegenüber“, „genau dort, wo … sich berühren“, Absolutformeln, „eng
#                  beieinander“, „mitten in der Ballung“, die leere Haelfte „liegt im …“,
#                  „der Knotenachse gegenüber“ — gegen Orben, Laengen, Hausspitzen, §6, §8.
#   Transit:
#   Zeit           „ab <Zeit> steht T …", „beginnt im …", „zum ersten Mal genau im …",
#                  „ab <Zeit> steht T in <Zeichen>" — gegen Wirkorb-Beginn,
#                  Exaktdaten und Zeichenaufenthalt der events.json.
#   Zugleich       „zugleich", „gleichzeitig", „in denselben Wochen" — gegen die
#                  Ueberlappung der Wirkorb-Zeiten.
#   Station        „genau … stillstehen" — gegen den Stationsort (Orb ueber 30′).
#   Anzahl         „n andere Planeten an dieselben Punkte", „n Beruehrungen im
#                  engen Wirkbereich" — gegen THEMA-Zeile bzw. Jetzt-Liste.
#   Wiederholung   „zuletzt …, als du n warst" — gegen die frueheren Durchgaenge
#                  GENAU DIESES Kontakts (P11 haelt das Alter nur gegen alle Alter);
#                  seit 2026-10-07 bei Aspekten mit zwei Haelften auch die Stellung;
#                  seit 2026-10-07b auch die Verneinung („seit deiner Geburt nie").
# Was nur ein Leser pruefen kann (falsche Praemissen, Deutung, „so eng wie kaum
# sonst"), bleibt draussen.

_P18_PLANETEN = ("SONNE", "MOND", "MERKUR", "VENUS", "MARS", "JUPITER", "SATURN",
                 "URANUS", "NEPTUN", "PLUTO")
_P18_PUNKTE = ("MONDKNOTEN", "CHIRON", "LILITH", "PHOLUS")
_P18_TRANSITER = ("JUPITER", "SATURN", "URANUS", "NEPTUN", "PLUTO", "CHIRON", "MONDKNOTEN",
                  "MARS")
# Domizile, modern UND klassisch (Wassermann/Saturn, Fische/Jupiter, Skorpion/Mars):
# „auf eigenem Boden" ist mit beiden Rechnungen gedeckt — die Probe wird nur leiser.
_P18_DOMIZIL = {"SONNE": ("LOEWE",), "MOND": ("KREBS",), "MERKUR": ("ZWILLINGE", "JUNGFRAU"),
                "VENUS": ("STIER", "WAAGE"), "MARS": ("WIDDER", "SKORPION"),
                "JUPITER": ("SCHUETZE", "FISCHE"), "SATURN": ("STEINBOCK", "WASSERMANN"),
                "URANUS": ("WASSERMANN",), "NEPTUN": ("FISCHE",), "PLUTO": ("SKORPION",)}
_P18_ZEICHEN_ANZEIGE = {selektor.norm(z): z for z in ZEICHEN if z not in ("Loewe", "Schuetze")}
_P18_ZEICHEN_HERR = {"WIDDER": "MARS", "STIER": "VENUS", "ZWILLINGE": "MERKUR", "KREBS": "MOND",
                     "LOEWE": "SONNE", "JUNGFRAU": "MERKUR", "WAAGE": "VENUS",
                     "SKORPION": "PLUTO", "SCHUETZE": "JUPITER", "STEINBOCK": "SATURN",
                     "WASSERMANN": "URANUS", "FISCHE": "NEPTUN"}
_P18_ELEMENT = {"Feuer": ("WIDDER", "LOEWE", "SCHUETZE"), "Erde": ("STIER", "JUNGFRAU", "STEINBOCK"),
                "Luft": ("ZWILLINGE", "WAAGE", "WASSERMANN"),
                "Wasser": ("KREBS", "SKORPION", "FISCHE")}
_P18_MODUS = {"kardinal": ("WIDDER", "KREBS", "WAAGE", "STEINBOCK"),
              "fix": ("STIER", "LOEWE", "SKORPION", "WASSERMANN"),
              "veränderlich": ("ZWILLINGE", "JUNGFRAU", "SCHUETZE", "FISCHE")}

_P18_ORD = {"erst": 1, "zweit": 2, "dritt": 3, "viert": 4, "fünft": 5, "fuenft": 5,
            "sechst": 6, "siebt": 7, "siebent": 7, "acht": 8, "neunt": 9, "zehnt": 10,
            "elft": 11, "zwölft": 12, "zwoelft": 12}
_P18_ORD_RE = (r"(?:erst|zweit|dritt|viert|fünft|fuenft|sechst|siebent|siebt|acht|neunt|zehnt|"
               r"elft|zwölft|zwoelft)(?:e|en|em|er|es)")
_P18_GRENZ = r"(?<![\wäöüÄÖÜß])"
_P18_ENDE = r"(?![\wäöüÄÖÜß])"


def _p18_ord_wert(wort):
    w = (wort or "").casefold()
    for stamm in sorted(_P18_ORD, key=len, reverse=True):
        if w.startswith(stamm):
            return _P18_ORD[stamm]
    return None


# Hausangaben im Fliesstext: „im fünften Haus", „im zweiten und im fünften Haus",
# „vierten bis sechsten Haus", „5. Haus", „Haus 5", „Häuser 4–6".
_P18_HAUS_RE = re.compile(
    _P18_GRENZ + r"(?:(?P<o1>%s)\s+(?:(?P<verb>und|bis|oder)\s+(?:(?:im|in|dem|des|das|ins|deinem|"
    r"dein|deines)\s+)?(?P<o2>%s)\s+)?(?:Haus|Hauses|Häuser|Häusern)"
    r"|(?P<n1>\d{1,2})\.\s*(?:(?P<nverb>und|bis|–|-)\s*(?P<n2>\d{1,2})\.\s*)?(?:Haus|Hauses|Häuser)"
    r"|(?:Haus|Hauses|Häuser|Häusern)\s+(?P<h1>\d{1,2})(?:\s*(?:(?P<hverb>bis|–|-|und)\s*)"
    r"(?P<h2>\d{1,2}))?(?![\d.]))" % (_P18_ORD_RE, _P18_ORD_RE) + _P18_ENDE, re.I)


def _p18_haeuser_in(text):
    """Hausnummern einer Textstelle -> [(anfang, ende, {Haeuser})]."""
    out = []
    for m in _P18_HAUS_RE.finditer(text or ""):
        g = m.groupdict()
        if g["o1"]:
            a, b, verb = _p18_ord_wert(g["o1"]), _p18_ord_wert(g["o2"]), g["verb"]
        elif g["n1"]:
            a, b, verb = int(g["n1"]), int(g["n2"]) if g["n2"] else None, g["nverb"]
        else:
            a, b, verb = int(g["h1"]), int(g["h2"]) if g["h2"] else None, g["hverb"]
        if not a or not 1 <= a <= 12 or (b is not None and not 1 <= b <= 12):
            continue
        if b is None:
            hs = {a}
        elif verb and verb.lower() in ("bis", "–", "-") and b >= a:
            hs = set(range(a, b + 1))
        else:
            hs = {a, b}
        out.append((m.start(), m.end(), hs))
    return out


# Lebensbereiche (Klartext-Modul, „Häusernummer → Lebensbereich") — nur fuer die
# Bereichs- und Viertel-Angaben ohne Nummer („das Viertel von Auftreten, Besitz
# und Sprache", „der Bereich … — Herkunft, Ausdruck, Alltag —").
_P18_BEREICH_WORT = (
    (1, r"Auftreten\w*|Auftritt\w*"),
    (2, r"Selbstwert\w*|Besitz\w*|Werten?|Werte\b"),
    (3, r"Nahumfeld\w*|Sprache\w*|Sprechen\w*|Lernen\w*|Alltagskontakt\w*|Geschwister\w*"),
    (4, r"Herkunft\w*|Wurzeln?|Zuhause|Familie\w*"),
    (5, r"Ausdruck\w*|Spiel\w*|Schöpferkraft\w*|Kinder\w*"),
    (6, r"Alltag\w*|Arbeit\w*|Gesundheit\w*"),
    (7, r"Partnerschaft\w*|Gegenüber\w*|Begegnung\w*"),
    (8, r"Bindung\w*|Geteilte[mns]?|Krise\w*|Verwandlung\w*"),
    (9, r"Sinnsuche\w*|Weite|Weltbild\w*|Ferne"),
    (10, r"Beruf\w*|Öffentlichkeit\w*|Laufbahn\w*"),
    (11, r"Freundeskreis\w*|Zukunft\w*|Ziele|Zielen"),
    (12, r"Rückzug\w*|Verborgene[mns]?|Unbewusste[mns]?"),
)
_P18_BEREICH_RE = [(h, re.compile(_P18_GRENZ + r"(?:%s)" % rx + _P18_ENDE)) for h, rx in
                   _P18_BEREICH_WORT]
_P18_QUADRANT = {1: (1, 2, 3), 2: (4, 5, 6), 3: (7, 8, 9), 4: (10, 11, 12)}


def _p18_quadrant_von(h):
    return next(q for q, hs in _P18_QUADRANT.items() if h in hs)


_P18_VIERTEL_RE = re.compile(_P18_GRENZ + r"(?:(?P<ord>erst|zweit|dritt|viert)\w*\s+)?"
                             r"(?:Viertel|Quadranten?)" + _P18_ENDE, re.I)
_P18_HEMI_RE = re.compile(
    _P18_GRENZ + r"(?:(?P<oben>oberhalb\s+des\s+Horizonts|über\s+dem\s+Horizont|obere[nr]?\s+Hälfte)"
    r"|(?P<unten>unterhalb\s+des\s+Horizonts|unter\s+dem\s+Horizont|untere[nr]?\s+Hälfte)"
    r"|(?P<ost>östliche[nr]?\s+(?:Hälfte|Seite))|(?P<west>westliche[nr]?\s+(?:Hälfte|Seite)))", re.I)
# Zeichen auch gebeugt („in den Fischen", „im Löwen", „des Skorpions")
_P18_ZEICHEN_IM_RE = re.compile(
    _P18_GRENZ + r"(?:im|in\s+(?:der|den|dem)|in)\s+(?P<z>%s)(?:n|en|s|es)?" % ZEICHEN_RE + _P18_ENDE)
_P18_ZEICHENLISTE_RE = re.compile(
    _P18_GRENZ + r"in\s+(?P<liste>(?:%s)(?:n|s)?(?:\s*,\s*(?:%s)(?:n|s)?)*\s+(?:oder|und)\s+(?:%s)(?:n|s)?)"
    % (ZEICHEN_RE, ZEICHEN_RE, ZEICHEN_RE) + _P18_ENDE)
_P18_ELEMENT_IM_RE = re.compile(_P18_GRENZ + r"(?:Zeichen\s+des|im\s+Element|in\s+den\s+Zeichen\s+des)\s+"
                                r"(?P<e>Feuers|Wassers|Feuer|Wasser|Luft|Erde)" + _P18_ENDE)


def _p18_region(text):
    """Bereich einer Textstelle -> (Haeuser, Zeichen, Beschreibung) oder None.
    Vorrang: Viertel mit Ordnungszahl, Viertel/Bereich mit Lebensbereichen,
    Hausnummern, Hemisphaere, Zeichen, Element."""
    t = text or ""
    haeuser, zeichen, teile = set(), set(), []
    worte = sorted({h for h, rx in _P18_BEREICH_RE if rx.search(t)})
    mv = _P18_VIERTEL_RE.search(t)
    if mv:
        if mv.group("ord"):
            q = {"erst": 1, "zweit": 2, "dritt": 3, "viert": 4}[mv.group("ord").lower()]
        else:
            qs = {_p18_quadrant_von(h) for h in worte} | \
                 {_p18_quadrant_von(h) for _a, _e, hs in _p18_haeuser_in(t) for h in hs}
            if len(qs) != 1:
                return None                         # Viertel nicht eindeutig
            q = qs.pop()
        hs = _P18_QUADRANT[q]
        return set(hs), set(), "Häuser %d–%d" % (hs[0], hs[-1])
    hn = [hs for _a, _e, hs in _p18_haeuser_in(t)]
    if hn:
        for hs in hn:
            haeuser |= hs
    elif worte and re.search(_P18_GRENZ + r"(?:Bereich|Häuser|Felder)" + _P18_ENDE, t):
        haeuser |= set(worte)
    if not haeuser:
        mh = _P18_HEMI_RE.search(t)
        if mh:
            haeuser |= (set(range(7, 13)) if mh.group("oben") else set(range(1, 7)) if mh.group("unten")
                        else {10, 11, 12, 1, 2, 3} if mh.group("ost") else set(range(4, 10)))
    ml = _P18_ZEICHENLISTE_RE.search(t)
    if ml:
        zeichen |= {selektor.norm(z) for z in re.findall(ZEICHEN_RE, ml.group("liste"))}
    for m in _P18_ZEICHEN_IM_RE.finditer(t):
        zeichen.add(_zeichen_norm(m.group("z")))
    me = _P18_ELEMENT_IM_RE.search(t)
    if me:
        zeichen |= set(_P18_ELEMENT[me.group("e").rstrip("s")])
    if not haeuser and not zeichen:
        return None
    if haeuser:
        h = sorted(haeuser)
        teile.append(("Haus %d" % h[0]) if len(h) == 1 else
                     ("Häuser %d–%d" % (h[0], h[-1]) if h == list(range(h[0], h[-1] + 1))
                      else "Häuser " + ", ".join(map(str, h))))
    if zeichen:
        teile.append(", ".join(_P18_ZEICHEN_ANZEIGE.get(z, z) for z in sorted(zeichen)))
    return haeuser, zeichen, " und ".join(teile)


def _p18_staende(txt):
    """Staendetabelle MIT Hausspalte -> {Faktor: (Zeichen, [Haus, Nebenhaus])}.
    „2/3" (Grenzlage) und „11/10" (Schwellenlage) tragen beide Haeuser — eine
    Grenzlage zaehlt als zwei Hausdeutungen (Datenblatt-Modul)."""
    m = re.search(r"\n## St[äa]nde", txt or "")
    if not m:
        return {}
    teil = txt[m.end():]
    s = re.search(r"\n## ", teil)
    teil = teil[:s.start()] if s else teil
    zeile = re.compile(r"^\|\s*(%s)\s*\|\s*\d{1,3}°\s*\d{1,2}[′']\s*\|\s*(%s)\s*[%s]?\s*\|\s*([^|]*)\|"
                       % (_AH_NAME, ZEICHEN_RE, ZEICHEN_GLYPHEN))
    out = {}
    for z in teil.splitlines():
        mm = zeile.match(z)
        if mm:
            hs = [int(x) for x in re.findall(r"\d{1,2}", mm.group(3))][:2]
            out[kanon(mm.group(1))] = (_zeichen_norm(mm.group(2)), hs)
    return out


def _p18_hausherrscher(txt):
    """Strukturbild §3 -> ({Haus: (Spitzenzeichen, Herrscher)}, {Faktoren „im eigenen
    Haus"}). Gelesen wird die moderne Liste („Haus 10 (Steinbock) → Saturn …")."""
    herr, eigen = {}, set()
    for m in re.finditer(r"^\s*-\s*Haus\s+(\d{1,2})\s*\(([^)]+)\)\s*→\s*(%s)(?![\wäöüÄÖÜß])(.*)$"
                         % _FAKTOR_RE, txt or "", re.M):
        n = int(m.group(1))
        if n in herr:
            continue                                # erste (moderne) Liste gilt
        herr[n] = (m.group(2).strip(), kanon(m.group(3)))
        if "im eigenen Haus" in m.group(4):
            eigen.add(kanon(m.group(3)))
    return herr, eigen


# Strukturbild §6: „leere Spitze 25°00′ Widder, Haus 1; dort: nichts" und
# „Gegenpunkt der Spitze …, Haus n; dort: …" — was AM PUNKT steht. Der Leere-Hinweis
# nennt es mit, damit der Lauf sieht, dass der Satz den Punkt meinen kann und nur das
# „dort" auf Haus oder Zeichen zielt.
_P18_LEERPUNKT_RE = re.compile(
    r"(?:leere\s+Spitze|Gegenpunkt\s+der\s+Spitze)\s+\d{1,2}°\s*\d{1,2}[′']\s+(?P<z>%s),\s+Haus\s+"
    r"(?P<h1>\d{1,2})(?:/(?P<h2>\d{1,2}))?;\s*dort:\s*(?P<dort>[^\n]+)" % ZEICHEN_RE)


def _p18_leerpunkte(txt):
    """§6 -> [(Zeichen, {Haeuser}, „dort"-Wert)]."""
    out = []
    for m in _P18_LEERPUNKT_RE.finditer(txt or ""):
        hs = {int(m.group("h1"))} | ({int(m.group("h2"))} if m.group("h2") else set())
        out.append((_zeichen_norm(m.group("z")), hs, m.group("dort").strip()))
    return out


def _p18_thema_mengen(themen):
    """Je THEMA n: Faktoren (fuehrt, klingt, aspekte, verweis) und Paare (aspekte,
    verweis) -> {n: {'fuehrt': set, 'faktoren': set, 'aspekte': set(frozenset),
    'verweis': set(frozenset), 'kontakte': [(T, Art, R)]}}. Geburtshoroskop:
    „Mond △ Saturn"; Transit: „T-Saturn □ R-Sonne" (dann beide Seiten)."""
    out = {}
    for t in themen or []:
        roh = t.get("roh") or ""
        d = {"fuehrt": set(), "faktoren": set(), "aspekte": set(), "verweis": set(),
             "kontakte": []}
        for feld in ("fuehrt", "klingt", "aspekte", "verweis"):
            wert = _thema_feld(roh, feld)
            if not wert:
                continue
            for k in _kontakte_in(wert):
                d["kontakte"].append((k[0], k[1], k[2]) + (feld,))
                d["faktoren"] |= {k[0], k[2]}
                if feld in ("aspekte", "verweis", "fuehrt"):
                    d["aspekte" if feld != "verweis" else "verweis"].add(frozenset((k[0], k[2])))
                if feld == "fuehrt":
                    d["fuehrt"].add(k[0])
            fs = [f for _a, _e, f in _faktoren_im_satz(re.sub(r"[TR]-\s*", "", wert))]
            d["faktoren"] |= set(fs)
            if feld == "fuehrt" and fs and not d["fuehrt"]:
                d["fuehrt"].add(fs[0])
            if feld in ("aspekte", "verweis"):
                for teil in re.split(r"\s*,\s*", wert):
                    ft = [f for _a, _e, f in _faktoren_im_satz(re.sub(r"[TR]-\s*", "", teil))]
                    if len(ft) == 2:
                        d[feld].add(frozenset(ft))
        out[t["nr"]] = d
    return out


def _p18_kapitel_nr(chapters, typ):
    """Kapitelnummer -> THEMA-Nummer (neue Zaehlung: gleich; alte: n-1)."""
    ab = _zaehlung_ab(chapters, typ)
    return (lambda n: n - (ab - 1))


# Klartext-Namen fuer Faktoren, wo der Text sie statt des Namens setzt (Klartext-
# Modul, Uebersetzungstabelle; Instrument-Kapitel „Die Sonne — der Kern"). Nur
# zweifelsfreie Formen — „Kern" allein (der Kern des Netzes) zaehlt nicht.
_P18_ALIAS = (
    (re.compile(_P18_GRENZ + r"(?:dein(?:em|en|es)?|deiner)\s+(?:Wesens)?[Kk]erns?" + _P18_ENDE), "SONNE"),
    (re.compile(_P18_GRENZ + r"(?:dein(?:em|en|es)?)\s+Wesenskern\w*" + _P18_ENDE), "SONNE"),
    (re.compile(_P18_GRENZ + r"[Dd]ie\s+Richtung\s+deines\s+Bildes" + _P18_ENDE), "MONDKNOTEN"),
)


def _p18_faktoren(text, alias=True):
    """Faktoren einer Textstelle in Textreihenfolge (wie _faktoren_im_satz), auf
    Wunsch mit den Klartext-Namen -> [(anfang, ende, Schluessel)]."""
    out = list(_faktoren_im_satz(text))
    if alias:
        for rx, f in _P18_ALIAS:
            for m in rx.finditer(text or ""):
                if not any(a <= m.start() < e for a, e, _f in out):
                    out.append((m.start(), m.end(), f))
    out.sort()
    return out


def _p18_namen(fs):
    return ", ".join(ANZEIGE.get(f, f) for f in fs)


def _p18_satzliste(chapters):
    """Alle Fliesstext-Saetze mit Ort: [(Kapitel, Bewegung, Absatz-Index, Satz-Index im
    Absatz, Satz)] — der Bezug eines Pronomens oder eines „dort" endet am Absatz."""
    out = []
    for i_b, (ch, bewegung, text) in enumerate(_fliesstext(chapters)):
        for i_s, (_a, _e, s) in enumerate(_saetze_pos(text)):
            out.append((ch, bewegung, i_b, i_s, s))
    return out

def _p18_melde(p, ort, satz, art, befunde):
    """EIN Hinweis je Satz und Satzart; mehrere Befunde stehen hintereinander."""
    if befunde:
        p.pruefen.append("%s: „%s“ — %s: %s" % (ort, _kurz(satz, 140), art,
                                                 " · ".join(dict.fromkeys(befunde))))
    return len(befunde)


# --- Leere ------------------------------------------------------------------
# „Dort steht nichts" bezieht sich auf den Ort, der zuletzt genannt ist (Haus,
# Zeichen) — im selben Satz davor, sonst im Satz davor. Die naechstliegende Lesart
# entscheidet, wie in den Pruefberichten vom 04.10.: Nennt der Satz davor Zeichen
# und Haus einer freien Ecke, meint „Dort steht nichts." dieses Haus und Zeichen.
# Eine Aussage ueber einen PUNKT („Dieser Punkt selbst ist leer", „Der Punkt
# selbst ist unbesetzt") bleibt still: Was an einem Punkt steht, rechnet §6 („dort:
# nichts"), und das traegt der Satz.
_P18_DORT_NICHTS_RE = re.compile(
    _P18_GRENZ + r"(?:[Dd]ort|[Dd]arin)\s+(?:steht|stehen|sitzt|sitzen|liegt|liegen|befindet\s+sich"
    r"|befinden\s+sich|ist|sind)\s+(?:sonst\s+|also\s+|aber\s+|selbst\s+)?(?:nichts|niemand"
    r"|kein(?:e|er|en)?(?:\s+(?:einzige[rn]?\s+)?(?P<nomen>Planet|Faktor|Punkt|Kraft|Hauptkraft)\w*)?)"
    + _P18_ENDE)
# Hinter „nichts"/„kein" ohne Nomen muss die Aussage enden — sonst ist es eine Wendung
# („darin liegt keine Schwäche", „dort steht nichts im Weg").
_P18_LEER_ENDE_RE = re.compile(r"\s*(?:[.,;:!?)\]—–]|$|(?:außer|als|sonst|mehr|weiter)(?![\wäöüß]))")
# Grenzen, an denen ein neuer Ort beginnen kann: „…, und die freie Stelle liegt im …"
_P18_ORT_GRENZE_RE = re.compile(r"[;:]|\s[—–]\s|,\s+(?:und|aber|doch|während|wobei|wo)\s+")
# Vergleich statt Leere: „Kein Planet steht so nah an deinem MC wie …"
_P18_VERGLEICH_RE = re.compile(_P18_GRENZ + r"(?:so\s+[\wäöüß]+\s+(?:[\wäöüß]+\s+){0,4}wie|näher|enger|mehr|"
                               r"weiter|höher|tiefer|stärker|früher|später|länger)" + _P18_ENDE)
_P18_IST_LEER_RE = re.compile(_P18_GRENZ + r"(?:ist|sind|bleibt|bleiben)\s+(?:ganz\s+|völlig\s+|vollständig"
                              r"\s+|dagegen\s+|also\s+)?(?:leer|unbesetzt|unbewohnt)" + _P18_ENDE)
_P18_KEIN_RE = re.compile(
    _P18_GRENZ + r"(?:[Kk]ein(?:e|er|en)?\s+(?:einzige[rn]?\s+)?(?P<n1>Planet|Faktor|Punkt|Achse|Hauptkraft)\w*"
    r"(?:\s+und\s+kein(?:e|er|en)?\s+(?P<n1b>Achse|Planet|Punkt|Faktor)\w*)?"
    r"(?:\s+(?:deines|in\s+deinem)\s+Bild(?:es)?)?\s+(?:steht|stehen|sitzt|liegt|liegen)"
    r"|(?:steht|stehen|sitzt|liegt)\s+kein(?:e|er|en)?\s+(?:(?:deiner|der)\s+)?(?:zehn\s+)?"
    r"(?P<n2>Planet|Faktor|Punkt|Hauptkr)\w*)" + _P18_ENDE)
_P18_ALLEIN_RE = re.compile(
    _P18_GRENZ + r"(?:allein|nur|ausschließlich|einzig)\s+(?:von\s+|mit\s+)?(?:dein\w*\s+)?(?P<f>%s)"
    r"(?:s|en|n)?\s+besetzt" % _FAKTOR_RE + _P18_ENDE)
_P18_PUNKT_NOMEN_RE = re.compile(_P18_GRENZ + r"(?:Punkt\w*|Ecke|Spitze|Bogen|Bogens)" + _P18_ENDE)
_P18_KLAUSEL_GRENZE_RE = re.compile(r"[;:]|\s[—–]\s(?=[a-zäöü]+\s)|,\s+(?:und|aber|doch|während)\s+"
                                    r"(?=(?:das|die|der|dein\w*|im|in|zugleich)\s)")


def _p18_umfang(satz):
    """Welche Faktoren meint eine Leere-Aussage? 'planeten' (die zehn), 'planeten+achsen',
    sonst 'alle' (Planeten und Spezialpunkte; Achsen nicht, Suedknoten getrennt)."""
    planeten = re.search(_P18_GRENZ + r"(?:Planet\w*|Hauptkr\w*|zehn\s+Kr\w*)" + _P18_ENDE, satz)
    achsen = re.search(_P18_GRENZ + r"Achse\w*" + _P18_ENDE, satz)
    if planeten:
        return "planeten+achsen" if achsen else "planeten"
    return "alle"


def _p18_belegung(d, haeuser, zeichen, umfang, ohne=()):
    """(Faktoren im Bereich, Suedknoten im Bereich?). Nennt der Satz Haus UND Zeichen
    („im Löwen im fünften Haus"), zaehlt nur, wer in beiden steht — die engere Lesart:
    ein Hinweis kommt nur bei Widerspruch. Grenzlage: beide Haeuser. Faktoren, die der
    Satz selbst nennt („dort steht sonst nichts", „leer bis auf …"), zaehlen nicht."""
    erlaubt = set(_P18_PLANETEN)
    if umfang == "alle":
        erlaubt |= set(_P18_PUNKTE)
    if umfang == "planeten+achsen":
        erlaubt |= set(ACHSEN)
    drin, sk = [], False
    for f, (z, hs) in d["staende"].items():
        im_haus = bool(haeuser and set(hs) & haeuser)
        im_zeichen = bool(zeichen and z in zeichen)
        if not ((im_haus and im_zeichen) if (haeuser and zeichen) else (im_haus or im_zeichen)):
            continue
        if f == "SUEDKNOTEN":
            sk = True
        elif f in erlaubt and f not in ohne:
            drin.append(f)
    return drin, sk


def _p18_belegung_txt(d, drin, sk, haeuser):
    teile = []
    for f in drin:
        z, hs = d["staende"][f]
        teile.append("%s%s" % (ANZEIGE.get(f, f), " (%s)" % "/".join(map(str, hs))
                               if haeuser and len(hs) > 1 else ""))
    return ", ".join(teile) + ("; dazu der Südknoten" if sk else "")


def _p18_ort_txt(hs, zs, wo):
    """„Jungfrau in Haus 4" fuer die Schnittmenge, sonst die Beschreibung des Bereichs."""
    if hs and zs:
        h = sorted(hs)
        haus = ("Haus %d" % h[0]) if len(h) == 1 else ("Häuser " + ", ".join(map(str, h)))
        return "%s in %s" % (" oder ".join(_P18_ZEICHEN_ANZEIGE.get(z, z) for z in sorted(zs)), haus)
    return wo


def _p18_letzter_ort(text):
    """Worauf zeigt ein „dort"? Auf den zuletzt genannten Ort: im letzten Abschnitt
    (Grenzen: ;, :, Gedankenstrich, „, und …"), der Haus oder Zeichen nennt, das Glied,
    das zuletzt steht — „im Widder, im ersten Haus, … Dort steht nichts." meint das
    erste Haus (naechstliegende Lesart, Pruefbericht vom 04.10.). Spricht der Text
    danach von der Ecke selbst („… — sie selbst bleibt frei, dort …"), meint „dort" den Punkt:
    None. -> (Haeuser, Zeichen, Beschreibung, (alle Haeuser, alle Zeichen des Abschnitts))
    oder None — die vollen Mengen braucht der Abgleich mit dem Punkt aus §6."""
    t = text or ""
    grenzen = [(m.start(), m.end()) for m in _P18_ORT_GRENZE_RE.finditer(t)]
    anfaenge = [0] + [e for _s, e in grenzen]
    enden = [s for s, _e in grenzen] + [len(t)]
    for a, e in reversed(list(zip(anfaenge, enden))):
        st = t[a:e]
        reg = _p18_region(st)
        if not reg:
            continue
        hs, zs, wo = reg
        voll = (set(hs), set(zs))
        h_end = max([x_e for _x, x_e, _h in _p18_haeuser_in(st)] or [-1])
        z_end = max([m.end() for m in _P18_ZEICHEN_IM_RE.finditer(st)] +
                    [m.end() for m in _P18_ZEICHENLISTE_RE.finditer(st)] or [-1])
        if hs and zs and h_end >= 0 and z_end >= 0:
            if h_end > z_end:
                zs, ende = set(), h_end
            else:
                hs, ende = set(), z_end
        else:
            ende = max(h_end, z_end)
        rest = st[ende:] + t[e:] if ende >= 0 else t[e:]
        if re.search(_P18_GRENZ + r"(?:sie|er|es|diese[rs]?)(?:\s+selbst)?\s+(?:ist|bleibt)\s+(?:ganz\s+|also\s+)?"
                     r"(?:leer|frei|unbesetzt)" + _P18_ENDE, rest) or _P18_PUNKT_NOMEN_RE.search(rest):
            return None                             # „dort" meint die Ecke selbst
        if hs and not zs:
            h = sorted(hs)
            wo = ("Haus %d" % h[0]) if len(h) == 1 else (
                "Häuser %d–%d" % (h[0], h[-1]) if h == list(range(h[0], h[-1] + 1))
                else "Häuser " + ", ".join(map(str, h)))
        elif zs and not hs:
            wo = ", ".join(_P18_ZEICHEN_ANZEIGE.get(z, z) for z in sorted(zs))
        return hs, zs, wo, voll
    return None


def _p18_am_punkt(d, hs, zs, satz, vorher):
    """Zusatz „(am Punkt selbst laut §6: …)", wenn der Satz (oder der davor) von einer
    Ecke, Spitze oder einem Punkt spricht und §6 dort einen leeren Punkt fuehrt."""
    if not re.search(_P18_GRENZ + r"(?:Ecke|Spitze|Gegenpunkt\w*|Punkt\w*)" + _P18_ENDE,
                     satz + " " + (vorher or "")):
        return ""
    werte = [dort for z, phs, dort in d.get("leerpunkte") or []
             if (not zs or z in zs) and (not hs or phs & hs)]
    return " (am Punkt selbst laut §6: %s)" % " / ".join(dict.fromkeys(werte)) if werte else ""


def _p18_leere(p, d, satz, vorher, ort):
    """Leere- und Abwesenheitsaussagen eines Satzes."""
    befunde = []
    genannt = {f for _a, _e, f in _p18_faktoren(satz)}
    for m in _P18_DORT_NICHTS_RE.finditer(satz):
        if not m.group("nomen") and not _P18_LEER_ENDE_RE.match(satz[m.end():]):
            continue                                # Wendung, keine Leere-Aussage
        davor = satz[:m.start()]
        reg, aus_vorher = _p18_letzter_ort(davor), False
        if not reg and not davor.strip(" ,;:—–").strip():
            reg, aus_vorher = _p18_letzter_ort(vorher), True
        if not reg:
            continue
        hs, zs, wo, (hs_voll, zs_voll) = reg
        p.geprueft += 1
        ohne = genannt | ({f for _a, _e, f in _p18_faktoren(vorher)} if aus_vorher else set())
        drin, sk = _p18_belegung(d, hs, zs, _p18_umfang(satz), ohne)
        if drin:
            befunde.append("„%s“ — %s: %s%s" % (m.group(0), _p18_ort_txt(hs, zs, wo),
                                                _p18_belegung_txt(d, drin, sk, hs),
                                                _p18_am_punkt(d, hs_voll, zs_voll, satz, vorher)))
    for m in _P18_IST_LEER_RE.finditer(satz):
        anfang = max([x.end() for x in _P18_KLAUSEL_GRENZE_RE.finditer(satz, 0, m.start())] or [0])
        klausel = satz[anfang:m.start()]
        if _P18_PUNKT_NOMEN_RE.search(klausel) or not re.search(
                _P18_GRENZ + r"(?:Viertel|Quadrant\w*|Hälfte|Seite|Bereich\w*|Häuser|Haus|Hauses|"
                r"Zeichen|Element\w*|Feld\w*)" + _P18_ENDE, klausel):
            continue
        reg = _p18_region(klausel)
        if not reg:
            continue
        hs, zs, wo = reg
        p.geprueft += 1
        drin, sk = _p18_belegung(d, hs, zs, _p18_umfang(satz), genannt)
        if drin:
            befunde.append("„%s“ — %s: %s%s" % (m.group(0), _p18_ort_txt(hs, zs, wo),
                                                _p18_belegung_txt(d, drin, sk, hs),
                                                _p18_am_punkt(d, hs, zs, satz, vorher)))
    for m in _P18_KEIN_RE.finditer(satz):
        ende = min([x.start() for x in _P18_KLAUSEL_GRENZE_RE.finditer(satz, m.end())] or [len(satz)])
        anfang = max([x.end() for x in _P18_KLAUSEL_GRENZE_RE.finditer(satz, 0, m.start())] or [0])
        if _P18_VERGLEICH_RE.search(satz[m.end():ende]):
            continue                                # Vergleich („so nah … wie"), keine Leere
        reg = _p18_region(satz[anfang:ende])
        if not reg:
            continue
        nomen = " ".join(x for x in (m.group("n1"), m.group("n1b"), m.group("n2")) if x)
        umfang = ("planeten+achsen" if re.search("Achse", nomen) and re.search("Planet", nomen) else
                  "planeten" if re.search("Planet|Hauptkr", nomen) else "alle")
        hs, zs, wo = reg
        p.geprueft += 1
        drin, sk = _p18_belegung(d, hs, zs, umfang, genannt)
        if drin:
            befunde.append("„%s“ — %s: %s" % (_kurz(m.group(0), 40), _p18_ort_txt(hs, zs, wo),
                                              _p18_belegung_txt(d, drin, sk, hs)))
    for m in _P18_ALLEIN_RE.finditer(satz):
        anfang = max([x.end() for x in re.finditer(r"[;:]", satz[:m.start()])] or [0])
        reg = _p18_region(satz[anfang:m.start()])
        if not reg:
            continue
        hs, zs, wo = reg
        p.geprueft += 1
        drin, sk = _p18_belegung(d, hs, zs, _p18_umfang(satz))
        andere = [f for f in drin if f not in genannt]
        if andere:
            befunde.append("„%s“ — %s: %s" % (m.group(0), _p18_ort_txt(hs, zs, wo),
                                              _p18_belegung_txt(d, drin, sk, hs)))
    return _p18_melde(p, ort, satz, "Leere", befunde)


# --- Herrscher ----------------------------------------------------------------
_P18_ORDLISTE = r"(?P<hl>%s(?:\s+(?:und|sowie)\s+(?:des\s+|deines\s+|dem\s+|das\s+)?%s)*)" % (
    _P18_ORD_RE, _P18_ORD_RE)
_P18_VERWALTER_RE = re.compile(
    _P18_GRENZ + r"(?:Verwalter(?:in)?|Herrscher(?:in)?|Herr(?:in)?)\s+(?:deines|des|dieses|deiner)\s+"
    + _P18_ORDLISTE + r"\s+(?:Hauses|Häuser)" + _P18_ENDE)
_P18_VERWALTET_RE = re.compile(
    _P18_GRENZ + r"verwaltet\s+(?:(?P<nach>er|sie|%s)\s+)?(?:in\s+deinem\s+Bild\s+|zugleich\s+|auch\s+"
    r"|außerdem\s+|dazu\s+|selbst\s+)*(?:dein|das|den)\s+" % _FAKTOR_RE
    + r"(?P<hl>%s(?:\s+und\s+(?:dein\s+|das\s+)?%s)*)\s+Haus" % (_P18_ORD_RE, _P18_ORD_RE) + _P18_ENDE)
_P18_ACHSE_HAUS = {"MC": 10, "AC": 1, "DC": 7, "IC": 4}
_P18_VERWALTER_ACHSE_RE = re.compile(
    _P18_GRENZ + r"(?:(?:Verwalter(?:in)?|Herrscher(?:in)?|Herr(?:in)?)\s+(?:deines|des)\s+"
    r"(?P<a1>MC|IC|Aszendenten|Deszendenten)|verwaltet\s+(?:in\s+deinem\s+Bild\s+)?(?:dein|das)\s+"
    r"(?P<a2>MC|IC))" + _P18_ENDE)
_P18_SEIN_HAUS_RE = re.compile(
    _P18_GRENZ + r"(?:das\s+)?(?P<o>%s)\s+Haus\s+ist\s+(?P<pron>sein|ihr)(?:\s+eigenes)?\s+Haus" % _P18_ORD_RE
    + _P18_ENDE, re.I)
_P18_EIGENES_HAUS_RE = re.compile(_P18_GRENZ + r"im\s+eigenen\s+(?:(?P<o>%s)\s+)?Haus" % _P18_ORD_RE
                                  + _P18_ENDE)
_P18_EIGENER_BODEN_RE = re.compile(_P18_GRENZ + r"auf\s+eigenem\s+(?:Boden|Grund)" + _P18_ENDE)
_P18_EIGENES_ZEICHEN_RE = re.compile(_P18_GRENZ + r"im\s+eigenen\s+Zeichen" + _P18_ENDE)
_P18_KEIN_BEREICH_RE = re.compile(
    _P18_GRENZ + r"(?P<f>%s)\s+verwaltet\s+(?:in\s+deinem\s+Bild\s+)?(?:keinen|kein)\s+(?:Bereich|Haus)"
    % _FAKTOR_RE + _P18_ENDE)


def _p18_klausel(satz, pos):
    """(anfang, ende) der Klausel um pos — Grenzen: Satzanfang/-ende, Semikolon,
    Doppelpunkt, Gedankenstrich."""
    a = max([x.end() for x in re.finditer(r"[;:]|\s[—–]\s", satz[:pos])] or [0])
    mm = re.search(r"[;:]|\s[—–]\s", satz[pos:])
    return a, (pos + mm.start()) if mm else len(satz)


def _p18_bezug_pronomen(pron, satzliste, i, satz, bis, ohne_achsen=True):
    """Bezugsfaktor eines Pronomens (er/sie/sein/ihr): der ERSTE Faktor passenden Genus
    im Satz vor dem Pronomen (bis 'bis') — das Subjekt des Satzes —, sonst aus dem
    naechsten Satz davor im selben Absatz, der einen passenden Faktor nennt, aber nur,
    wenn es dort genau EINEN gibt: „Mars reibt sich an deinem Mond. Er …" ist offen
    (Mars oder Mond) und bleibt still. Achsen verwalten kein Haus und zaehlen fuer
    Herrscher-Aussagen nicht. None, wenn keiner eindeutig passt."""
    g = {"er": "m", "sein": "m", "seine": "m", "seinem": "m", "seinen": "m", "sie": "f", "ihr": "f",
         "ihre": "f", "ihrem": "f", "ihren": "f"}.get((pron or "").casefold())
    if g is None:
        return None

    def passt(f):
        return _GENUS.get(f) == g and not (ohne_achsen and f in ACHSEN)
    kand = [f for _a, _e, f in _faktoren_im_satz(satz[:bis]) if passt(f)]
    if kand:
        return kand[0]
    _ch, _bw, i_b, _i_s, _s = satzliste[i]
    for k in range(i - 1, max(-1, i - 4), -1):
        if satzliste[k][2] != i_b:
            break
        kand = list(dict.fromkeys(f for _a, _e, f in _faktoren_im_satz(satzliste[k][4]) if passt(f)))
        if kand:
            return kand[0] if len(kand) == 1 else None
    return None


_P18_PRAEP_VOR_RE = re.compile(
    _P18_GRENZ + r"(?:[Nn]eben|[Mm]it|zu|zum|zur|an|am|über|bei|beim|von|vom|gegenüber|unter|vor|hinter|"
    r"zwischen|aus|nach|um|gegen|durch|ohne|für|wie)\s+(?:dein\w*\s+|de[mnrs]\s+|die\s+|das\s+)?$")


def _p18_besitzer(satz, pos, satzliste, i, ende=None):
    """Wer ist gemeint? Eine Apposition direkt davor („Saturn, der Verwalter des
    zehnten Hauses"); ein Pronomen am Klauselanfang, dann sein Bezug; sonst der ERSTE
    Faktor der Klausel vor pos, der nicht hinter einer Praeposition steht (das Subjekt:
    „Als Verwalter deines Auftretens ist dein Mars zugleich der Herr …", „Neben
    Saturn steht Mars … auf eigenem Boden"). Steht jeder Faktor hinter einer
    Praeposition („Mit deinem Mars stehst du auf eigenem Boden"), bleibt es offen.
    Achsen verwalten kein Haus."""
    a, _e = _p18_klausel(satz, pos)
    ap = re.search(r"(?P<f>%s)(?:s|es|en|n)?\s*,\s*(?:der|die)\s+(?:[\wäöüß]+\s+)?$" % _FAKTOR_RE,
                   satz[a:pos])
    if ap and kanon(ap.group("f")) not in ACHSEN:
        return kanon(ap.group("f"))
    mp = re.match(r"\W*(?:und\s+|aber\s+|doch\s+|zugleich\s+|dazu\s+)?(Er|Sie|er|sie)(?![\wäöüß])",
                  satz[a:pos])
    if mp:
        return _p18_bezug_pronomen(mp.group(1), satzliste, i, satz, a)
    vor = [(x, f) for x, _y, f in _faktoren_im_satz(satz[a:pos]) if f not in ACHSEN]
    frei = [f for x, f in vor if not _P18_PRAEP_VOR_RE.search(satz[a:a + x])]
    if frei:
        return frei[0]
    if vor:
        return None
    mp = re.search(_P18_GRENZ + r"(?:und|,)\s+(er|sie)\s+$", satz[a:pos])
    if mp:
        return _p18_bezug_pronomen(mp.group(1), satzliste, i, satz, a)
    return None


def _p18_herrscher(p, d, satz, satzliste, i, ort):
    herr, eigen = d["herrscher"], d["eigen_haus"]
    if not herr:
        return 0
    befunde = []

    def pruefe_haus(f, n, roh):
        if f is None or n not in herr:
            return
        p.geprueft += 1
        z, h = herr[n]
        if h != f:
            wo = [k for k, (_z, hh) in sorted(herr.items()) if hh == f]
            befunde.append("„%s“ — Haus %d (%s) → %s (Strukturbild §3)%s"
                           % (roh, n, z, ANZEIGE.get(h, h),
                              "; %s verwaltet %s" % (ANZEIGE.get(f, f), ", ".join("Haus %d" % k for k in wo))
                              if wo else "; %s verwaltet kein Haus" % ANZEIGE.get(f, f)))
    klassisch = re.compile(_P18_GRENZ + r"(?:klassisch\w*|traditionell\w*|antik\w*|alte[nrs]?|"
                           r"früher\w*)" + _P18_ENDE)
    for m in _P18_VERWALTER_RE.finditer(satz):
        if klassisch.search(satz[max(0, m.start() - 30):m.end()]):
            continue
        nach = re.match(r"\s*(?:ist|:)\s+(?:dein\w*\s+)?(%s)" % _FAKTOR_RE, satz[m.end():])
        f = kanon(nach.group(1)) if nach else _p18_besitzer(satz, m.start(), satzliste, i)
        for o in re.findall(_P18_ORD_RE, m.group("hl")):
            pruefe_haus(f, _p18_ord_wert(o), m.group(0))
    for m in _P18_VERWALTET_RE.finditer(satz):
        if klassisch.search(satz[max(0, m.start() - 30):m.end()]):
            continue
        vorn = re.search(_P18_GRENZ + r"(er|sie)\s+(?:[\wäöüß]+\s+)?$", satz[:m.start()])
        if m.group("nach") and m.group("nach").casefold() not in ("er", "sie"):
            f = kanon(m.group("nach"))
        elif m.group("nach") or vorn:
            f = _p18_bezug_pronomen((m.group("nach") or vorn.group(1)), satzliste, i, satz,
                                    m.start() if m.group("nach") else vorn.start())
        else:
            f = _p18_besitzer(satz, m.start(), satzliste, i)
        for o in re.findall(_P18_ORD_RE, m.group("hl")):
            pruefe_haus(f, _p18_ord_wert(o), m.group(0))
    for m in _P18_VERWALTER_ACHSE_RE.finditer(satz):
        achse = m.group("a1") or m.group("a2")
        n = _P18_ACHSE_HAUS[{"Aszendenten": "AC", "Deszendenten": "DC"}.get(achse, achse)]
        nach = re.match(r"\s*(?:ist|:)\s+(?:dein\w*\s+)?(%s)" % _FAKTOR_RE, satz[m.end():])
        f = kanon(nach.group(1)) if nach else _p18_besitzer(satz, m.start(), satzliste, i)
        pruefe_haus(f, n, m.group(0))
    for m in _P18_SEIN_HAUS_RE.finditer(satz):
        f = _p18_bezug_pronomen(m.group("pron"), satzliste, i, satz, m.start())
        pruefe_haus(f, _p18_ord_wert(m.group("o")), m.group(0))
    for m in _P18_KEIN_BEREICH_RE.finditer(satz):
        f = kanon(m.group("f"))
        wo = [k for k, (_z, hh) in sorted(herr.items()) if hh == f]
        if wo:
            befunde.append("„%s“ — %s verwaltet %s (Strukturbild §3)"
                           % (m.group(0), ANZEIGE.get(f, f), ", ".join("Haus %d" % k for k in wo)))
    for m in _P18_EIGENES_HAUS_RE.finditer(satz):
        f = _p18_besitzer(satz, m.start(), satzliste, i)
        if f is None or f not in d["staende"] or f in eigen:
            continue
        _z, hs = d["staende"][f]
        if m.group("o") and _p18_ord_wert(m.group("o")) not in hs:
            continue                               # P2/Stand-Fehler, nicht diese Probe
        wo = ["Haus %d (%s) → %s" % (n, herr[n][0], ANZEIGE.get(herr[n][1], herr[n][1]))
              for n in hs if n in herr]
        befunde.append("„%s“ — %s steht in %s; %s (Strukturbild §3, „im eigenen Haus“: %s)"
                       % (m.group(0), ANZEIGE.get(f, f), "/".join("Haus %d" % n for n in hs),
                          "; ".join(wo), _p18_namen(sorted(eigen)) or "keiner"))
    for m in _P18_EIGENER_BODEN_RE.finditer(satz):
        f = _p18_besitzer(satz, m.start(), satzliste, i)
        if f is None or f not in d["staende"] or f not in _P18_DOMIZIL:
            continue
        z, hs = d["staende"][f]
        if z in _P18_DOMIZIL[f] or f in eigen:
            continue
        herr_z = _P18_ZEICHEN_HERR.get(z)
        befunde.append("„%s“ — %s in %s (Herrscher: %s), Haus %s; zu Hause ist %s in %s"
                       % (m.group(0), ANZEIGE.get(f, f), _P18_ZEICHEN_ANZEIGE.get(z, z),
                          ANZEIGE.get(herr_z, herr_z), "/".join(map(str, hs)), ANZEIGE.get(f, f),
                          " und ".join(_P18_ZEICHEN_ANZEIGE.get(x, x) for x in _P18_DOMIZIL[f])))
    for m in _P18_EIGENES_ZEICHEN_RE.finditer(satz):
        a, _e = _p18_klausel(satz, m.start())
        fs = [f for _x, _y, f in _faktoren_im_satz(satz[a:m.start()]) if f in _P18_DOMIZIL]
        # „die beide" direkt davor gilt den zwei letzten Faktoren, ein Relativpronomen
        # („der …") dem einen davor, sonst gilt es dem Subjekt der Klausel
        if re.search(_P18_GRENZ + r"(?:die\s+)?beide\s+$", satz[a:m.start()]) and len(fs) >= 2:
            fs = fs[-2:]
        elif re.search(_P18_GRENZ + r"(?:der|die|das)\s+(?:[\wäöüß]+\s+){0,2}$", satz[a:m.start()]) and fs:
            fs = fs[-1:]
        elif fs:
            fs = fs[:1]
        if not fs:
            pr = re.match(r"\W*(?:und\s+)?(Er|Sie|er|sie)(?![\wäöüß])", satz[a:m.start()])
            f = _p18_bezug_pronomen(pr.group(1), satzliste, i, satz, a) if pr else None
            fs = [f] if f in _P18_DOMIZIL else []
        for f in dict.fromkeys(fs):
            if f not in d["staende"]:
                continue
            z, _hs = d["staende"][f]
            if z not in _P18_DOMIZIL[f]:
                befunde.append("„%s“ — %s steht in %s; zu Hause ist %s in %s"
                               % (m.group(0), ANZEIGE.get(f, f), _P18_ZEICHEN_ANZEIGE.get(z, z),
                                  ANZEIGE.get(f, f),
                                  " und ".join(_P18_ZEICHEN_ANZEIGE.get(x, x) for x in _P18_DOMIZIL[f])))
    return _p18_melde(p, ort, satz, "Herrscher", befunde)


# --- Kapitelverweis -------------------------------------------------------------
_P18_KAPITEL_RE = re.compile(_P18_GRENZ + r"Kapitel(?:s)?\s+(?P<n>\d{1,2})" + _P18_ENDE)
_P18_KAPITEL_LISTE_RE = re.compile(_P18_GRENZ + r"Kapitel(?:s|n)?\s+\d{1,2}(?:\s*(?:,|und|oder|bis)\s*"
                                   r"(?:Kapitel\s+)?\d{1,2})*" + _P18_ENDE)


_P18_KAPITEL_TITEL_RE = re.compile(_P18_GRENZ + r"Kapitel(?:s)?\s+(?P<n>\d{1,2})\s*(?:,|:|\(|—|–)?\s*"
                                   r"„(?P<t>[^“”\"„]{2,90})[“”\"]")
_P18_ABSCHNITT_RE = re.compile(_P18_GRENZ + r"Abschnitt(?:s|e|en)?\s+„(?P<t>[^“”\"„]{2,60})[“”\"]")


def _p18_titel_norm(t):
    t = re.sub(r"[—–\-]", " ", (t or "").casefold())
    t = re.sub(r"[^\wäöüß ]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _p18_titel_passt(soll, ist):
    soll, ist = _p18_titel_norm(soll), _p18_titel_norm(ist)
    return bool(soll and ist) and (soll == ist or soll.startswith(ist) or ist.startswith(soll))


def _p18_titelpruefung(p, chapters, satz):
    """„Kapitel 3, „Was hält, wenn nichts drängt“" — der Titel muss der Ueberschrift
    von Kapitel 3 entsprechen (Anfang genuegt: ein Titel mit Gedankenstrich darf gekuerzt stehen)."""
    befunde = []
    for m in _P18_KAPITEL_TITEL_RE.finditer(satz):
        n = int(m.group("n"))
        ch = next((c for c in chapters if _kicker_nr(c.get("kicker")) == n), None)
        if ch is None or not ch.get("title"):
            continue
        p.geprueft += 1
        if _p18_titel_passt(ch["title"], m.group("t")):
            continue
        anders = next((c for c in chapters if _p18_titel_passt(c.get("title"), m.group("t"))), None)
        befunde.append("Kapitel %d heißt „%s“%s" % (n, ch["title"], "; „%s“ ist %s" % (
            anders["title"], anders.get("kicker")) if anders else ""))
    return befunde


def _p18_abschnittpruefung(p, chapters, satz):
    """„der Abschnitt „X“ im Kapitel Y" (auch „im Kapitel Y der Abschnitt „X“") — den
    Abschnitt muss es im genannten Kapitel geben (ohne Kapitelangabe: irgendwo im
    Dokument)."""
    befunde = []
    namen = [c["kicker"] for c in chapters if c.get("kicker") and not _kicker_nr(c["kicker"])]
    kap_rx = r"Kapitel(?:s)?\s+(\d{1,2}|%s)" % "|".join(re.escape(k) for k in namen) if namen else \
        r"Kapitel(?:s)?\s+(\d{1,2})"
    for m in _P18_ABSCHNITT_RE.finditer(satz):
        mk = re.search(kap_rx, satz[m.end():m.end() + 60]) or re.search(
            kap_rx + r"(?:\W+[\wäöüß]+){0,3}\W*$", satz[max(0, m.start() - 60):m.start()])
        ziel = None
        if mk:
            w = mk.group(1)
            ziel = next((c for c in chapters if (w.isdigit() and _kicker_nr(c.get("kicker")) == int(w))
                         or c.get("kicker") == w), None)
        kandidaten = [ziel] if ziel is not None else chapters
        p.geprueft += 1
        if any(_p18_titel_passt(a, m.group("t")) for c in kandidaten for a in _p18_abschnitte(c)):
            continue
        if ziel is not None:
            abschn = _p18_abschnitte(ziel)
            befunde.append("Abschnitt „%s“ — im Kapitel %s: %s" % (
                m.group("t"), ziel.get("kicker"),
                ", ".join("„%s“" % a for a in dict.fromkeys(abschn)) or "keine benannten Abschnitte"))
        else:
            befunde.append("Abschnitt „%s“ — kein Abschnitt dieses Namens im Dokument" % m.group("t"))
    return befunde


def _p18_kapitelverweis(p, d, satz, ort, eigenes, chapters=None):
    """„Kapitel n zeigt X und Y", „davon erzählt Kapitel n" — gegen die THEMA-Zeile n;
    dazu Titel („Kapitel 3, „Was hält, wenn nichts drängt“") und Abschnitte („der
    Abschnitt „X“ im Kapitel Y") gegen die Ueberschriften.
    Ein Paar wird je Satzteil (Grenze: Semikolon) mit genau EINER Kapitelangabe
    geprueft (auch als Liste: „Kapitel 2 und 3"): Ein Hinweis kommt nur, wenn die zwei
    Faktoren in keinem genannten Kapitel unter aspekte= oder verweis= stehen, nicht
    beide unter dessen Faktoren, wohl aber in einem ANDEREN Kapitel unter aspekte=.
    Ein einzelner Faktor bleibt still (ein Kapitel kann ihn als Seitenblick nennen),
    ebenso ein Vergleich („Saturn steht wie dein Mars im sechsten Haus").
    eigenes: das Kapitel, in dem der Satz steht — ein „hier" im Satzteil zeigt dorthin."""
    befunde = []
    if chapters:
        befunde += _p18_titelpruefung(p, chapters, satz)
        befunde += _p18_abschnittpruefung(p, chapters, satz)
    for teil in (satz.split(";") if d["thema"] else []):
        listen = list(_P18_KAPITEL_LISTE_RE.finditer(teil))
        if len(listen) != 1:
            continue
        nummern = {int(x) for x in re.findall(r"\d{1,2}", listen[0].group(0))}
        for mb in re.finditer(r"(\d{1,2})\s+bis\s+(?:(?:zum\s+)?Kapitel(?:n|s)?\s+)?(\d{1,2})", listen[0].group(0)):
            nummern |= set(range(int(mb.group(1)), int(mb.group(2)) + 1))
        if eigenes in nummern:
            continue
        ths = [(n, d["thema"].get(d["kap2thema"](n))) for n in sorted(nummern)]
        ths = [(n, t) for n, t in ths if t is not None]
        if not ths:
            continue
        rest = teil[:listen[0].start()] + " " + teil[listen[0].end():]
        fpos = [(a, e, f) for a, e, f in _p18_faktoren(rest) if f != "SUEDKNOTEN"]
        fs = list(dict.fromkeys(f for _a, _e, f in fpos))
        if len(fs) != 2:
            continue
        if re.search(_P18_GRENZ + r"(?:[Aa]nders\s+als|im\s+Gegensatz|[Nn]icht\s+wie|[Ww]ährend\s+Kapitel|"
                     r"dieses\s+Kapitel|hier)" + _P18_ENDE, teil):
            continue                                # Gegenueberstellung oder das eigene Kapitel
        if any(re.search(r"(?<![,\s])\s+wie\s+(?:dein\w*\s+|der\s+|die\s+|das\s+)?$", rest[:a]) and
               any(a2 < a for a2, _e2, f2 in fpos if f2 != f) for a, _e, f in fpos):
            continue                                # Vergleich („Saturn steht wie dein Mars …"), kein Paar
        p.geprueft += 1
        paar = frozenset(fs)
        alle_f = set().union(*(t["faktoren"] for _n, t in ths))
        alle_a = set().union(*(t["aspekte"] for _n, t in ths))
        alle_v = set().union(*(t["verweis"] for _n, t in ths))
        if paar in alle_a or paar in alle_v or all(f in alle_f for f in fs):
            continue
        anderswo = sorted(k for k, t in d["thema"].items() if paar in t["aspekte"])
        hier = eigenes is not None and d["kap2thema"](eigenes) in anderswo and \
            re.search(_P18_GRENZ + r"(?:hier|dieses\s+Kapitel|[Aa]nders\s+als|im\s+Gegensatz|"
                      r"[Nn]icht\s+wie|[Ww]ährend\s+Kapitel)" + _P18_ENDE, teil)
        if anderswo and not hier:
            befunde.append("%s: %s–%s nicht in der THEMA-Zeile; gedeutet in Kapitel %s (aspekte=)"
                           % ("Kapitel " + " und ".join(str(n) for n, _t in ths),
                              ANZEIGE.get(fs[0], fs[0]), ANZEIGE.get(fs[1], fs[1]),
                              ", ".join(str(d["thema2kap"](k)) for k in anderswo)))
    return _p18_melde(p, ort, satz, "Kapitelverweis", befunde)


# --- Signatur der Buendel-Kapitel ----------------------------------------------
_P18_BUENDEL = ("Hauptthemen", "Konfliktfelder", "Lebensaufgaben")


def _p18_signatur_kapitel(sig):
    """Kapitelnummern einer Buendel-Signatur („Kapitel 2, Kapitel 4 und Kapitel 5",
    „Kapiteln 1 bis 6") -> set oder None (keine Liste)."""
    if not sig:
        return None
    out = set()
    for m in re.finditer(r"Kapitel(?:n|s)?\s+(\d{1,2})\s+bis\s+(?:(?:zum\s+)?Kapitel(?:n|s)?\s+)?(\d{1,2})", sig):
        out |= set(range(int(m.group(1)), int(m.group(2)) + 1))
    for m in _P18_KAPITEL_LISTE_RE.finditer(sig):
        out |= {int(x) for x in re.findall(r"\d{1,2}", m.group(0))}
    return out or None


def _p18_signatur(p, d, chapters):
    """Buendel-Kapitel (Hauptthemen, Konfliktfelder, Lebensaufgaben) mit einer
    Kapitelliste in der Signatur: Ein Absatz, dessen Faktoren (auch im Klartext-Namen,
    „die Richtung deines Bildes") Kapitel FUEHREN, von denen keines in der Liste steht,
    zeigt eine Luecke der Signatur — es sei denn, der Absatz verweist selbst auf ein
    Kapitel der Liste („das ist die Reibung aus Kapitel 3")."""
    befunde = 0
    fuehrt_kap = {}
    for k, t in d["thema"].items():
        for f in t["fuehrt"]:
            fuehrt_kap.setdefault(f, set()).add(d["thema2kap"](k))
    for ch in chapters:
        if not _ist_kicker(ch, *_P18_BUENDEL):
            continue
        liste = _p18_signatur_kapitel(ch.get("signatur"))
        if not liste:
            continue
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                continue
            fs = list(dict.fromkeys(f for _a, _e, f in _p18_faktoren(b["text"])))
            kap = set()
            for f in fs:
                kap |= fuehrt_kap.get(f, set())
            if not kap:
                continue
            p.geprueft += 1
            verweis = {int(x) for mm in _P18_KAPITEL_LISTE_RE.finditer(b["text"])
                       for x in re.findall(r"\d{1,2}", mm.group(0))}
            if kap & liste or verweis & liste:
                continue
            p.pruefen.append(
                "%s · Signatur: „%s“ — Signatur: der Absatz „%s“ nennt %s (führt Kapitel %s) — die "
                "Signatur nennt Kapitel %s" % (_bezeichnung(ch), _kurz(ch.get("signatur"), 100),
                                                _kurz(b["text"], 60), _p18_namen(fs),
                                                ", ".join(map(str, sorted(kap))),
                                                ", ".join(map(str, sorted(liste)))))
            befunde += 1
    return befunde


# --- Modulwort -----------------------------------------------------------------
# Werkstattwoerter der Module, die im Lesetext nichts zu suchen haben — der Leser
# kennt sie nicht, das Dokument fuehrt sie nirgends. Bewusst NICHT darunter, weil
# das Dokument sie selbst fuehrt: Signatur, Beleg (Auftakt erklaert beide),
# Leitachse, Register, Rechenschaft, Getriebe, Instrument, Untergrund, Anhang.
# Abgleich mit P8 (Fachbegriffe der Astrologie) und P10 (Superlativ, Klinisches …):
# keines dieser Woerter steht dort.
_P18_MODULWORT_RE = re.compile(
    _P18_GRENZ + r"(?:Pflichtteil\w*|Pflichtabschnitt\w*|Kopfbl[oö]ck\w*|Bewegungsfolge\w*|Themenliste\w*"
    r"|Datenblatt\w*|Strukturbild\w*|Rangzeile\w*|Zählmenge\w*|Kicker\w*|Bauform\w*|Kurzform\w*"
    r"|Ressourcen-?[Bb]lock\w*|Mitklinger\w*|Typmodul\w*|Selektor\w*|Bibliotheksblock\w*"
    r"|Referenzdatei\w*|Deutungsort\w*|(?:Aspekt|Kontakt)-?[Hh]eimat\w*|Heimat-?[Pp]robe\w*"
    r"|Bündel-?[Kk]apitel\w*|in\s+der\s+kurzen\s+Form)" + _P18_ENDE)


def _p18_abschnitte(ch):
    """Abschnittsnamen eines Kapitels: ###-Zwischentitel und Etiketten wie „Was trägt:"
    — als eigener kurzer Absatz oder am Satzanfang im Absatz („… Bildes. Was trägt: Der
    Mond …")."""
    out = list(_subheads(ch))
    for b in ch["blocks"]:
        t = _ws(b.get("text", ""))
        if b.get("type") == "subhead":
            continue
        if re.fullmatch(r"[A-ZÄÖÜ][^:.!?]{2,40}:", t):
            out.append(t[:-1])
            continue
        for m in re.finditer(r"(?:^|(?<=[.!?]\s))([A-ZÄÖÜ][\wäöüß]*(?:\s+[\wäöüß]+){0,4}):\s", t):
            out.append(m.group(1))
    return out


def _p18_modulwort(p, chapters, satz, ort):
    n = 0
    for m in _P18_MODULWORT_RE.finditer(satz):
        if m.group(0).startswith("in") and not re.search(
                _P18_GRENZ + r"(?:Kapitel\w*|läuft|laufen|Bewegung\w*)" + _P18_ENDE, satz):
            continue                                # „in der kurzen Form" als gewoehnliches Deutsch
        p.geprueft += 1
        zusatz = ""
        namen = [ch["kicker"] for ch in chapters if ch.get("kicker") and not _kicker_nr(ch["kicker"])]
        mk = re.search(r"Kapitel(?:s)?\s+(%s)" % "|".join(re.escape(k) for k in namen), satz) if namen else None
        if mk:
            ziel = next((ch for ch in chapters if ch.get("kicker") == mk.group(1)), None)
            abschn = _p18_abschnitte(ziel) if ziel else []
            zusatz = ("; Abschnitte im Kapitel %s: %s" % (mk.group(1), ", ".join("„%s“" % s for s in abschn))
                      if abschn else "; das Kapitel %s hat keine benannten Abschnitte" % mk.group(1))
        p.pruefen.append("%s: „%s“ — Modulwort: „%s“ ist ein Werkstattwort der Module; der Leser "
                         "findet es weder als Kapitel noch als Abschnitt%s"
                         % (ort, _kurz(satz, 140), m.group(0), zusatz))
        n += 1
    return n


# --- Aussagen ueber das Dokument ------------------------------------------------
_P18_TABELLE_RE = re.compile(_P18_GRENZ + r"(?P<neg>nicht\s+)?(?:(?:vollständig\s+)?[Ii]n\s+der\s+Aspekttabelle"
                             r"|[Ii]n\s+den\s+Tabellen|[Aa]uf\s+der\s+Aspektseite)" + _P18_ENDE)
_P18_ZWISCHEN_RE = re.compile(_P18_GRENZ + r"zwischen\s+(?:dein\w*\s+)?(?P<a>%s)\w*\s+und\s+(?:dein\w*\s+)?"
                              r"(?P<b>%s)" % (_FAKTOR_RE, _FAKTOR_RE) + _P18_ENDE)


# 2026-10-06 (FFU aus dem Pruefbericht Geburtshoroskop 3+4 vom 05.10.): „Beide stehen
# vollstaendig in der Aspekttabelle." nannte die Paare nur im Satz davor — die Probe
# fand im Satz selbst kein Paar und schwieg. Jetzt gilt: Nennt die Klausel kein Paar
# und verweist mit „beide", „sie", „diese" oder „es" zurueck, nimmt die Probe die
# Paare des Satzes davor (nur im selben Absatz, wie `vorher`). Still bleiben eine
# Verneinung in derselben Klausel („In der Aspekttabelle stehen beide nicht") und
# Saetze ueber die UEBRIGEN Verbindungen („Alle anderen stehen in der Aspekttabelle").
_P18_RUECKVERWEIS_RE = re.compile(_P18_GRENZ + r"(?:[Bb]eide|[Ss]ie|[Dd]iese|[Ee]s)" + _P18_ENDE)
_P18_DOK_STILL_RE = re.compile(_P18_GRENZ + r"(?:nicht|kein\w*|übrig\w*|ander\w*|weiter\w*|sonstig\w*|"
                               r"restlich\w*)" + _P18_ENDE)


def _p18_dokument(p, d, satz, ort, vorher=""):
    """„… in der Aspekttabelle: <Paare>" — jedes Paar muss in den
    Tabellen stehen, die das Dokument zeigt (voll, einseitig, neben; Untergrund nur
    mit gedeutet=ja). Ein „nicht in der Aspekttabelle" bleibt still.
    Seit 2026-10-06: Ohne Paar in der Klausel und mit Rueckverweis („Beide stehen
    vollstaendig in der Aspekttabelle.") gelten die Paare des Satzes davor."""
    n = 0
    for m in _P18_TABELLE_RE.finditer(satz):
        if m.group("neg"):
            continue
        hinten = satz[m.end():]
        dp = re.match(r"\s*(?:[\wäöüß]+\s+){0,3}?[\wäöüß]*\s*:", hinten)
        if dp:
            bereich = hinten[dp.end():]
        else:
            a, _e = _p18_klausel(satz, m.start())
            bereich = satz[a:m.start()]
        paare = [(kanon(x.group("a")), kanon(x.group("b"))) for x in _P18_ZWISCHEN_RE.finditer(bereich)]
        paare += [(fa[0], fb[0]) for fa, _art, fb, _t in _konstellationen(bereich) if fa and fb]
        if not paare and vorher:
            ka, ke = _p18_klausel(satz, m.start())
            klausel = satz[ka:ke]
            if _P18_RUECKVERWEIS_RE.search(klausel) and not _P18_DOK_STILL_RE.search(klausel):
                paare = [(kanon(x.group("a")), kanon(x.group("b"))) for x in _P18_ZWISCHEN_RE.finditer(vorher)]
                paare += [(fa[0], fb[0]) for fa, _art, fb, _t in _konstellationen(vorher) if fa and fb]
        befunde = []
        for a_, b_ in dict.fromkeys(paare):
            paar = frozenset((a_, b_))
            zeilen = [z for z in d["tabelle"] if frozenset((z["a"], z["b"])) == paar]
            if not zeilen:
                continue
            p.geprueft += 1
            sichtbar = [z for z in zeilen if z["stufe"] != "untergrund" or
                        re.search(r"\|\s*ja\s*\|\s*$", z["zeile"])]
            if not sichtbar:
                z = zeilen[0]
                befunde.append("%s %s %s %s steht nur im Untergrund und ist nicht gedeutet "
                               "(gedeutet=nein) — nicht in der Aspekttabelle des Dokuments"
                               % (ANZEIGE.get(z["a"], z["a"]), z["art"], ANZEIGE.get(z["b"], z["b"]),
                                  z["orb_txt"]))
        n += _p18_melde(p, ort, satz, "Dokument", befunde)
    return n


# --- Rang mit gedeutetem Untergrund -----------------------------------------------
# 2026-10-13 (Strang 2, Chris-Entscheidung a4, Fragenblock des Wartungslaufs: „ja“):
# Die Regel vom 04.10. — „die engste Verbindung“ ohne Zusatz zaehlt den GEDEUTETEN
# Untergrund mit — entfaellt. Ohne Zusatz gilt die Rangzeile §10 (P12); mit „deines
# ganzen Bildes“, „alle Faktoren gezählt“, „unter allen gerechneten“ zaehlt JEDER
# gerechnete Untergrund-Aspekt (_p18_rang_ganz, Abschnitt „P18 Naehe, Lage und Rang“).


# --- Anteil: „alles andere" -----------------------------------------------------
_P18_ALLES_ANDERE_RE = re.compile(_P18_GRENZ + r"(?:alles\s+(?:andere|übrige)|alle\s+(?:anderen|übrigen)"
                                  r"(?:\s+(?:Planeten|Kräfte|Hauptkräfte))?|der\s+(?:ganze\s+)?Rest)"
                                  + _P18_ENDE)
_P18_MODUS_VERB = (("fix", r"hält\s+fest|halten\s+fest|festhält|festhalten|hält|halten|beharrt|beharren"),
                   ("kardinal", r"fängt\s+an|fangen\s+an|anfangen|ansetzen|setzt\s+an|setzen\s+an|beginnt|beginnen"),
                   ("veränderlich", r"passt\s+sich\s+an|passen\s+sich\s+an|anpassen|wandelt\s+sich"))


def _p18_modus_im(text):
    for name, rx in _P18_MODUS_VERB:
        if re.search(_P18_GRENZ + r"(?:%s)" % rx + _P18_ENDE, text or ""):
            return name
    mm = _MODUS_RE.search(text or "")
    return _modus_name(mm) if mm else None


def _p18_anteil(p, d, satz, ort):
    n = 0
    for m in _P18_ALLES_ANDERE_RE.finditer(satz):
        nach = satz[m.end():m.end() + 40]
        x = _p18_modus_im(nach)
        y = _p18_modus_im(satz[:m.start()])
        if not x or not y or x == y:
            continue
        pl = {f: z for f, (z, _h) in d["staende"].items() if f in _P18_PLANETEN}
        if not pl:
            continue
        p.geprueft += 1
        rest = sorted(f for f, z in pl.items() if z not in _P18_MODUS[x] and z not in _P18_MODUS[y])
        if rest:
            zaehl = {mo: [f for f, z in pl.items() if z in zs] for mo, zs in _P18_MODUS.items()}
            p.pruefen.append("%s: „%s“ — Anteil: „%s … %s“ — %s Planeten: %s"
                             % (ort, _kurz(satz, 140), m.group(0), x,
                                "zehn" if len(pl) == 10 else str(len(pl)),
                                " · ".join("%s %d (%s)" % (mo, len(fs), _p18_namen(fs))
                                           for mo, fs in zaehl.items() if fs)))
            n += 1
    return n

# --- Transit: Kontakte im Satz ---------------------------------------------------
# Wer laeuft, wer wird getroffen? Ein Faktor ist ZIEL, wenn er als Radixpunkt
# markiert ist („dein …", „R-") oder hinter einer Praeposition steht („zu Mars",
# „über deinen Mars"); ein Glied einer Aufzaehlung („zu Mars und Venus") teilt die
# Rolle des Glieds davor. Sonst ist ein Planet, der laufen kann, LAEUFER. Ein Ziel
# gehoert zur zuletzt davor genannten Laeufer-Gruppe („Saturn und Uranus … zu deinem
# Mars" — beide). So wird „Uranus läuft im Trigon zu deinem Mars, Saturn kam in die
# Nähe deiner Venus" zu Uranus–Mars und Saturn–Venus, nicht zu Uranus–Venus.
_P18_TEILSATZ_RE = re.compile(r"[;:]|\s[—–]\s|,\s+(?:und|aber|doch|sondern|während|bevor|nachdem|wenn|als)\s")
_P18_LISTE_ZW_RE = re.compile(r"^\s*(?:,|und|sowie|oder)\s*(?:(?:zu|zum|zur|an|am|mit|über|auf|dein\w*|der|die|"
                              r"das|dem|den|des)\s+)*$", re.I)
_P18_BILD_DANACH_RE = re.compile(r"\s*(?:gegenüber|im\s+(?:Quadrat|Trigon|Sextil|Quincunx|Halbsextil)|"
                                 r"(?:im|in\s+einem)\s+schrägen\s+Winkel|in\s+Spannung|"
                                 r"in\s+Konjunktion|über\s+dein)", re.I)
_P18_WIEDER_RE = re.compile(_P18_GRENZ + r"(?:wieder|erneut|zurück|abermals|noch\s+einmal|nochmals"
                            r"|zum\s+(?:zweiten|dritten|letzten)\s+Mal|zweite[nr]?\s+(?:Durchgang|Mal)"
                            r"|kehrt|kehren)" + _P18_ENDE, re.I)


def _p18_teilsatz(satz, pos):
    """(anfang, ende) des Teilsatzes um pos — Grenzen: Semikolon, Doppelpunkt,
    Gedankenstrich, Komma vor „und/aber/doch/sondern/während/…": „…, und ab dem
    Herbst steht Saturn …" gehoert nicht zu dem, was davor ueber Jupiter steht."""
    a = max([x.end() for x in _P18_TEILSATZ_RE.finditer(satz[:pos])] or [0])
    mm = _P18_TEILSATZ_RE.search(satz, pos)
    return a, mm.start() if mm else len(satz)


# Bilder der Aspektarten (Klartext-Modul, Uebersetzungstabelle) — der Zeitfilter
# prueft nur die Kontakte der Art, die der Satz nennt.
_P18_ASPEKT_BILD = (
    ("Konjunktion", re.compile(_P18_GRENZ + r"(?:verschmilzt|verschmelzen|verschmolz\w*|einen\s+einzigen\s+Strom|"
                               r"am\s+selben\s+Punkt|über\s+(?:dein\w*|den|die|das)(?![\wäöüß]))")),
    ("Opposition", re.compile(_P18_GRENZ + r"(?:gegenüber\w*|Zerreißprobe\w*|zwischen\s+zwei\s+Pole)")),
    ("Quadrat", re.compile(_P18_GRENZ + r"(?:reibt\s+sich|reiben\s+sich|rieb\s+sich|rieben\s+sich|gerieben|unter\s+Druck|"
                           r"drängt\s+gegen|drängen\s+gegen|Reibung\w*)")),
    ("Trigon", re.compile(_P18_GRENZ + r"(?:fließt|fließen|floss|flossen|harmonisch\w*|weiche[nmr]?\s+Winkel\w*)"
                          + _P18_ENDE)),
    ("Sextil", re.compile(_P18_GRENZ + r"(?:Tür|Türen|Anregung\w*|harmonisch\w*|weiche[nmr]?\s+Winkel\w*)"
                          + _P18_ENDE)),
    ("Quadrat", re.compile(_P18_GRENZ + r"harte[nmr]?\s+Winkel\w*" + _P18_ENDE)),
    ("Opposition", re.compile(_P18_GRENZ + r"harte[nmr]?\s+Winkel\w*" + _P18_ENDE)),
    ("Quincunx", re.compile(_P18_GRENZ + r"(?:passt\s+nicht|passen\s+nicht|nachjustier\w*|Nachjustieren|"
                            r"schräge[nmr]?\s+Winkel)")),
)
# Ein laufender Planet hinter einem blossen Komma beginnt eine neue Gruppe, wenn ihm
# eine Zeit oder ein Verb folgt („…, Pluto seit Juni").
_P18_NEUE_GRUPPE_RE = re.compile(
    r"\s+(?:seit|ab|von|bis|zuerst|dann|danach|zuletzt|steht|stand|stehen|standen|geht|ging|gehen|läuft|lief"
    r"|laufen|kommt|kam|kommen|tritt|trat|wandert|wanderte|bleibt|blieb|reibt|rieb|fließt|floss|öffnet"
    r"|öffnete|verschmilzt|folgt|folgte|zieht|zog|berührt|berührte|wird|wurde|kehrt|kehrte|erreicht"
    r"|erreichte|Anfang|Mitte|Ende|%s|(?:19|20|21)\d\d)" % _MONAT_RE + _P18_ENDE)


def _p18_rollen(text):
    """[(anfang, ende, Faktor, Rolle)] mit Rolle 'L' (laeuft) oder 'Z' (Ziel). Ein
    Genitiv ohne Artikel („Saturns langsamer Gang", „unter Jupiters Schutz")
    ist weder das eine noch das andere und faellt heraus; „deines Mondes" bleibt Ziel.
    Ein laufender Planet hinter „mit/von", dem gleich ein Aspektbild zu einem
    Radixpunkt folgt („mit Saturn gegenüber deinem Mond"), laeuft. Ein
    laufender Planet hinter einem blossen Komma, dem eine Zeit oder ein Verb folgt,
    beginnt eine neue Gruppe („… an deinem Mars, Pluto seit Juni")."""
    out = []
    for a, e, f in _faktoren_im_satz(text):
        token = text[a:e]
        davor = text[max(0, a - 40):a]
        if re.search(r"(?:s|es)$", token) and not re.search(r"s$", ANZEIGE.get(f, f)) and \
                not re.search(_P18_GRENZ + r"(?:des|deines|eines)\s+$", davor):
            continue
        zw = text[out[-1][1]:a] if out else ""
        neu = bool(out) and f in _P18_TRANSITER and re.fullmatch(r"\s*,\s*", zw) and \
            (_P18_NEUE_GRUPPE_RE.match(text[e:e + 40]) or
             (out[-1][3] == "Z" and _P18_BILD_DANACH_RE.match(text[e:e + 50])))   # 2026-10-13
        # 2026-10-13: „… zum Merkur und Neptun im Quadrat zu deinem Mond“, „…, Saturn im
        # März …“ — ein Transiter mit eigenem Aspektbild oder eigener Zeit beginnt eine
        # neue Gruppe, auch hinter „und“
        neu = neu or (bool(out) and f in _P18_TRANSITER and out[-1][3] == "Z" and
                      re.fullmatch(r"\s*(?:,\s*)?(?:und|sowie)?\s*", zw) and
                      (_P18_BILD_DANACH_RE.match(text[e:e + 50]) or
                       re.match(r"\s+im\s+(?:%s|Frühjahr|Sommer|Herbst|Winter)" % _MONAT_RE, text[e:e + 30])))
        if out and _P18_LISTE_ZW_RE.match(zw) and not neu:
            rolle = out[-1][3]
        elif neu:
            rolle = "L"
        elif _RADIX_MARKE_RE.search(davor):
            rolle = "Z"
        elif _OBJEKT_VOR_RE.search(davor):
            rolle = "L" if f in _P18_TRANSITER and _P18_BILD_DANACH_RE.match(text[e:e + 50]) else "Z"
        elif f in _P18_TRANSITER:
            rolle = "L"
        else:
            rolle = "Z"
        out.append((a, e, f, rolle))
    return out


def _p18_gruppen(text):
    """Laeufer-Gruppen mit ihren Zielen: [(anfang, ende_des_abschnitts, [Laeufer], [Ziele])].
    Ziele VOR dem ersten Laeufer gehoeren zur ersten Gruppe („Im Sextil zu deinem
    Mars stand Saturn")."""
    rollen = _p18_rollen(text)
    gruppen, vorab = [], []
    for a, e, f, r in rollen:
        if r == "L":
            if gruppen and gruppen[-1][3] == [] and _P18_LISTE_ZW_RE.match(text[gruppen[-1][4]:a]):
                gruppen[-1][2].append(f)
                gruppen[-1][4] = e
            else:
                gruppen.append([a, None, [f], [], e])
                if len(gruppen) == 1 and vorab:
                    gruppen[0][3].extend(vorab)
                    vorab = []
        elif gruppen:
            gruppen[-1][3].append(f)
        else:
            vorab.append(f)
    for i, g in enumerate(gruppen):
        g[1] = gruppen[i + 1][0] if i + 1 < len(gruppen) else len(text)
    return [(g[0], g[1], g[2], g[3]) for g in gruppen]


def _p18_kontakte(text, index, pos=None, seg=None):
    """Kontakte (T, Z) einer Textstelle, die der Index (events.json) fuehrt. Mit pos:
    nur die Laeufer-Gruppe, zu der die Stelle pos gehoert — mit seg (Anfang des
    Kommaabschnitts um pos): die Gruppe, die im Abschnitt VOR pos beginnt („Saturn
    steht ab …"), sonst die erste danach („…, ab März steht Uranus …"); ohne
    seg die letzte davor (steht pos vor der ersten Gruppe, die erste).
    -> ([(T, Z)], [Laeufer der Gruppe(n)])"""
    gruppen = _p18_gruppen(text)
    if pos is not None and gruppen:
        vor = [g for g in gruppen if g[0] <= pos]
        if seg is not None:
            im_seg = [g for g in vor if g[0] >= seg]
            nach = [g for g in gruppen if g[0] > pos]
            gruppen = [im_seg[-1]] if im_seg else [nach[0]] if nach else [vor[-1]]
        else:
            gruppen = [vor[-1]] if vor else [gruppen[0]]
    paare, laeufer = [], []
    for _a, _e, ls, zs in gruppen:
        laeufer += ls
        for t in ls:
            for z in zs:
                if z != t and (t, z) in index:
                    paare.append((t, z))
    return list(dict.fromkeys(paare)), list(dict.fromkeys(laeufer))


def _p18_laeufer_vor(text, bis):
    """Der zuletzt genannte Laeufer vor `bis` (Bezug von „er")."""
    ls = [f for a, _e, f, r in _p18_rollen(text[:bis]) if r == "L"]
    return ls[-1] if ls else None


def _p18_ev_index_spiegel(events):
    """Nur die Spiegel-Ziele (Kontakt zur Gegenachse: DC zum AC, IC zum MC) — fuer das
    Buendel „im Quadrat zu deinem MC und deinem IC“ (2026-10-13)."""
    idx = {}
    for e in (events or {}).get("events", []) or []:
        if e.get("spiegel"):
            idx.setdefault((kanon(e.get("transit", "")), kanon(e.get("ziel", ""))), []).append(e)
    return idx


def _p18_ev_index(events):
    """events.json -> {(Transiter, Ziel): [Kontakte]} (ohne Spiegel-Ziele)."""
    idx = {}
    for e in (events or {}).get("events", []) or []:
        if e.get("spiegel"):
            continue
        idx.setdefault((kanon(e.get("transit", "")), kanon(e.get("ziel", ""))), []).append(e)
    return idx


# --- Transit: Zeitangaben ---------------------------------------------------------
_P18_ZEITPHRASE_RE = re.compile(
    _P18_GRENZ + r"(?:(?P<wo>Anfang|Mitte|Ende)\s+(?:des\s+)?)?(?:(?P<mon>%s)\s+(?P<j1>(?:19|20|21)\d\d)"
    r"|(?:dem\s+|des\s+)?(?P<jz>(?:Früh|Spät|Hoch)(?:sommer|herbst|winter)|Frühjahr\w*|Frühling\w*|"
    r"Sommer\w*|Herbst\w*|Winter\w*)\s+(?:des\s+Jahres\s+)?(?P<j2>(?:19|20|21)\d\d)(?:/(?P<j2b>\d\d))?"
    r"|(?P<j3>(?:19|20|21)\d\d))(?!\d)" % _MONAT_RE)


def _p18_zeiten(text):
    """Zeitangaben einer Textstelle -> [(anfang, ende, von, bis, roh)] (ISO-Daten)."""
    import calendar
    out = []
    for m in _P18_ZEITPHRASE_RE.finditer(text or ""):
        wo = (m.group("wo") or "").casefold()
        if m.group("mon"):
            j, mo = int(m.group("j1")), _MONATE[m.group("mon").casefold()]
            letzt = calendar.monthrange(j, mo)[1]
            t1, t2 = {"": (1, letzt), "anfang": (1, 10), "mitte": (11, 20), "ende": (21, letzt)}[wo]
            von, bis = "%04d-%02d-%02d" % (j, mo, t1), "%04d-%02d-%02d" % (j, mo, t2)
        elif m.group("jz"):
            j = int(m.group("j2"))
            jz = re.sub(r"(?:es|s)$", "", m.group("jz").casefold())
            for vor in ("früh", "spät", "hoch"):
                if jz.startswith(vor) and jz[len(vor):] in ("sommer", "herbst", "winter"):
                    jz = jz[len(vor):]
            mos = _JAHRESZEIT_MONATE.get(jz)
            if not mos:
                continue
            if jz == "winter" and m.group("j2b"):       # „Winter 2026/27“ (2026-10-13)
                von, bis = "%04d-12-01" % j, "%04d-02-28" % (j + 1)
            elif jz == "winter":
                von, bis = "%04d-12-01" % (j - 1), "%04d-02-28" % j
            else:
                von = "%04d-%02d-01" % (j, mos[0])
                bis = "%04d-%02d-%02d" % (j, mos[-1], calendar.monthrange(j, mos[-1])[1])
        else:
            j = int(m.group("j3"))
            mos = {"anfang": (1, 4), "mitte": (5, 8), "ende": (9, 12)}.get(wo, (1, 12))
            von = "%04d-%02d-01" % (j, mos[0])
            bis = "%04d-%02d-%02d" % (j, mos[1], calendar.monthrange(j, mos[1])[1])
        out.append((m.start(), m.end(), von, bis, m.group(0)))
    return out


def _p18_plus(iso, tage):
    from datetime import date, timedelta
    return (date.fromisoformat(iso) + timedelta(days=tage)).isoformat()


def _p18_perioden(evs):
    """Alle Wirkorb-Perioden der Kontakte, Vorlauf eingeschlossen -> sortiert [(von, bis)]."""
    out = []
    for e in evs:
        out += [tuple(x) for x in ((e.get("vorlauf") or {}).get("wirkorb_perioden") or [])]
        out += [tuple(x) for x in (e.get("wirkorb_perioden") or [])]
    return sorted(set(out))


def _p18_exakt(evs):
    out = []
    for e in evs:
        out += list(e.get("exakt_gesamt") or e.get("exakt") or [])
        out += list(e.get("exakt_vor_start") or [])
        out += list((e.get("vorlauf") or {}).get("exakt") or [])
    return sorted(set(out))


def _p18_kontakt_txt(t, z, evs=None):
    arten = sorted({e.get("aspekt") for e in evs or [] if e.get("aspekt")})
    return "%s%s %s" % (ANZEIGE.get(t, t), (" " + "/".join(arten)) if arten else "", ANZEIGE.get(z, z))


def _p18_aspektarten(klausel):
    """Aspektarten einer Textstelle: Name, Glyphe oder Bild (Klartext-Modul,
    Uebersetzungstabelle; „geht über" = Konjunktion)."""
    arten = {_art(m.group(1)) if m.group(1) else _ASP_GLYPH.get(m.group(2))
             for m in ASPEKT_RE.finditer(klausel or "")}
    for art, rx in _P18_ASPEKT_BILD:
        if rx.search(klausel or ""):
            arten.add(art)
    arten.discard(None)
    return arten


def _p18_aspekt_filter(evs, klausel):
    """Nennt die Klausel eine Aspektart (Name oder Bild), gelten nur die Kontakte
    dieser Art — keiner, wenn der Kontakt sie nicht hat (kein Rueckfall auf alle:
    „Saturn geht über deinen Mars" prueft nicht das Trigon zu deiner Venus)."""
    arten = _p18_aspektarten(klausel)
    if not arten:
        return evs
    return [e for e in evs if e.get("aspekt") in arten]


def _p18_nah(evs, von, bis, monate=12):
    """Nur die Kontakte, deren Wirkorb-Zeit hoechstens `monate` vor/nach der Zeitangabe
    liegt — ein Sextil im einen Jahr ist nicht das im uebernaechsten."""
    out = []
    for e in evs:
        ps = _p18_perioden([e])
        if not ps:
            continue
        if ps[-1][1] >= _p18_plus(von, -31 * monate) and ps[0][0] <= _p18_plus(bis, 31 * monate):
            out.append(e)
    return out


_P18_AB_RE = re.compile(_P18_GRENZ + r"(?:[Aa]b|[Ss]eit)\s+(?=(?:dem\s+|des\s+|Anfang\s+|Mitte\s+|Ende\s+)?"
                        r"(?:%s|Frühjahr|Frühling|Sommer|Herbst|Winter|Früh\w+|Spät\w+|(?:19|20|21)\d\d))"
                        % _MONAT_RE)
_P18_BEGINNT_RE = re.compile(_P18_GRENZ + r"(?:beginnt|beginnen|begann|begannen|begonnen|setzt\s+\w*\s*ein"
                             r"|setzte\s+\w*\s*ein|fängt\s+\w*\s*an)" + _P18_ENDE)
_P18_ERSTMALS_RE = re.compile(_P18_GRENZ + r"(?:zum\s+ersten\s+Mal|erstmals)\s+(?:genau|exakt)" + _P18_ENDE)
_P18_NICHT_BEGINN_RE = re.compile(_P18_GRENZ + r"(?:dicht\w*|verdicht\w*|Höhepunkt\w*|am\s+stärksten|"
                                  r"am\s+engsten|genau|exakt|nacheinander\s+\w+\s+genau)" + _P18_ENDE)
_P18_NACHEINANDER_RE = re.compile(_P18_GRENZ + r"(?:nacheinander|der\s+Reihe\s+nach|einer\s+nach\s+dem\s+"
                                  r"anderen)" + _P18_ENDE)
_P18_ZEICHEN_STEHT_RE = re.compile(
    _P18_GRENZ + r"(?:(?P<t1>Jupiter|Saturn|Uranus|Neptun|Pluto|Chiron|Mars)\s+(?:steht|wandert|läuft|geht|"
    r"wechselt|tritt|ist)|(?:steht|wandert|läuft|geht|wechselt|tritt|ist)\s+(?P<t2>Jupiter|Saturn|Uranus|"
    r"Neptun|Pluto|Chiron|Mars))\s+(?:[\wäöüß]+\s+){0,3}?(?:in\s+(?:die|den|das|der)|im|in)\s+(?P<z>%s)"
    % ZEICHEN_RE + _P18_ENDE)


_P18_BIS_VOR_RE = re.compile(r"(?:^|\s)[Bb]is\s+(?:(?:in\s+(?:den|die|das)|zum|zur|Anfang|Mitte|Ende)\s+)*$")
_P18_ZEITLISTE_NACH_RE = re.compile(
    r"\s*(?:und|oder|bzw\.|,)\s*(?:seit\s+|ab\s+)?(?:dem\s+|des\s+)?(?:Anfang\s+|Mitte\s+|Ende\s+)?"
    r"(?:%s|Frühjahr|Frühling|Sommer|Herbst|Winter|(?:19|20|21)\d\d)" % _MONAT_RE)


# „beginnt" fuer eine Teilstrecke („die rückläufige Strecke", „die dichte Phase",
# „die zweite Welle") ist nicht der Beginn des Kontakts.
_P18_PHASE_RE = re.compile(_P18_GRENZ + r"(?:rückläufig\w*|direktläufig\w*|Strecke\w*|Phase\w*|Welle\w*|"
                           r"Runde\w*|Abschnitt\w*|Durchgang\w*|Durchlauf\w*|Teil|Rest\w*|"
                           r"zweite\w*|dritte\w*|letzte\w*|dicht\w*|Höhepunkt\w*)" + _P18_ENDE)
_P18_IM_FENSTER_RE = re.compile(_P18_GRENZ + r"(?:im\s+Fenster|in\s+diesem\s+Fenster|im\s+Zeitraum\s+dieses|"
                                r"in\s+diesen\s+(?:zwei\s+|beiden\s+)?Jahren)" + _P18_ENDE)


def _p18_zeiten_ohne_bis(text):
    """Zeitangaben ohne die, die ein Ende nennen („bis Anfang April")."""
    return [z for z in _p18_zeiten(text) if not _P18_BIS_VOR_RE.search(text[max(0, z[0] - 25):z[0]])]


def _p18_spanne(e):
    ps = _p18_perioden([e])
    return (ps[0][0], max(y for _x, y in ps)) if ps else None


def _p18_massgeblich(evs, von, bis):
    """Die Kontakte, deren Wirkorb-Zeit [von − 15 Tage, bis + 31 Tage] schneidet —
    ein Trigon im einen Jahr ist nicht das Quadrat im naechsten."""
    out = []
    for e in evs:
        sp = _p18_spanne(e)
        if sp and sp[0] <= _p18_plus(bis, 31) and sp[1] >= _p18_plus(von, -15):
            out.append(e)
    return out


def _p18_absatz_nennt(absatz, t, x, y, von):
    """Nennt ein Satzteil des Absatzes, in dem der Laeufer t laeuft, eine Zeit VOR der
    Angabe (Ende vor von − 15 Tagen), die in [x − 15, y + 15] faellt? Dann erzaehlt der
    Text diese fruehere Strecke selbst („Im Juni steht Saturn schon … ; ab März des
    Folgejahres …")."""
    for s in absatz or []:
        for teil in re.split(r"[;:]|\s[—–]\s", s):
            if t not in [f for _a, _e, f, r in _p18_rollen(teil) if r == "L"]:
                continue
            for _a, _e, tv, tb, _r in _p18_zeiten(teil):
                if tb < _p18_plus(von, -15) and tv <= _p18_plus(y, 15) and tb >= _p18_plus(x, -15):
                    return True
    return False


def _p18_zeit(p, d, satz, ort, absatz=None):
    """Zeitangaben zu einem genannten Kontakt (Transit). Die Stichworte:
    „ab/seit <Zeit>": Massgeblich sind die Kontakte der genannten Aspektart, deren
      Wirkorb-Zeit die Angabe beruehrt. Gemeldet, wenn so ein Kontakt am Stichtag im
      Wirkorb steht und <Zeit> mehr als zwei Monate danach liegt, oder wenn er seit
      Beginn der Rueckschau schon VOR <Zeit> einen Wirkorb-Durchgang hatte, den der
      Absatz nicht selbst erzaehlt („läuft schon"); beruehrt keiner die Angabe und
      beginnt der naechste mehr als einen Monat danach: „erst ab". Nicht bei
      „wieder", „erneut", „zurück", „dicht", nicht bei „seit <Jahr> und <Jahr>" (je
      Laeufer eine Zeit). „Ab <Zeit> steht Saturn im Krebs" (ohne Kontakt im
      Satzteil): der Zeichenaufenthalt.
    „beginnt/begann im …": der frueheste Wirkorb-Beginn der genannten Kontakte (je
      Kontakt der, der der Angabe am naechsten liegt); eine „bis"-Angabe ist kein Beginn.
    „zum ersten Mal genau im …": das erste Exaktdatum — je Kommaabschnitt („im März
      … zu deinem Mars, im Mai … zu deiner Venus"), der Laeufer notfalls aus dem
      Abschnitt davor."""
    befunde = []
    stichtag = d["stichtag"] or d["start"]
    unten = d.get("lookback") or d["start"] or ""
    absatz = absatz or [satz]
    for m in _P18_AB_RE.finditer(satz):
        hinten = satz[m.end():m.end() + 40]
        zt = _p18_zeiten(hinten)
        if not zt or zt[0][0] > 12:
            continue
        _a0, e0, von, bis, roh = zt[0]
        if _P18_ZEITLISTE_NACH_RE.match(hinten[e0:]):
            continue
        # 2026-10-13 (Strang 1): Folgt der Zeit ein Haus („ab März 2031 durch dein viertes
        # Haus“), meint die Angabe den Hausdurchgang — den prueft _p18_wechsel(); vorher
        # band diese Stelle sie an den Zeichenaufenthalt (Fehlalarm im Transit vom 12.10.).
        if _P18_HAUS_ORD_RE.search(satz[m.end() + e0:m.end() + e0 + 60]):
            continue
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        if _P18_WIEDER_RE.search(klausel) or _P18_NICHT_BEGINN_RE.search(satz[max(a, m.start() - 30):e]):
            continue
        mz = _P18_ZEICHEN_STEHT_RE.search(klausel)
        if mz and d["zeichen"] and not [f for _x, _y, f, r in _p18_rollen(klausel) if r == "Z"]:
            t, z = kanon(mz.group("t1") or mz.group("t2")), _zeichen_norm(mz.group("z"))
            auf = [x for x in d["zeichen"] if kanon(x.get("transit", "")) == t and
                   _zeichen_norm(x.get("zeichen", "")) == z and x.get("von", "") > (d["start"] or "")]
            if auf:
                p.geprueft += 1
                beginn = min(x["von"] for x in auf)
                if beginn < _p18_plus(von, -15) or beginn > _p18_plus(bis, 31):
                    befunde.append("„ab %s“ — %s steht ab %s in %s (Zeichenaufenthalt, events.json)"
                                   % (roh, ANZEIGE.get(t, t), _de(beginn), _P18_ZEICHEN_ANZEIGE.get(z, z)))
            continue
        seg = max([a] + [x.end() for x in re.finditer(r",", satz[:m.start()]) if x.end() > a])
        kont, _ls = _p18_kontakte(klausel, d["ev"], pos=m.start() - a, seg=seg - a)
        pruef = []
        for t, z in kont:
            alle = _p18_aspekt_filter(d["ev"][(t, z)], klausel)
            if alle:
                pruef.append((t, z, alle, _p18_massgeblich(alle, von, bis)))
        if not pruef:
            continue
        p.geprueft += 1
        if _P18_NACHEINANDER_RE.search(klausel):
            def _beginn(x):
                ps_ = [a_ for a_, b_ in _p18_perioden(x[3] or x[2]) if b_ >= _p18_plus(stichtag, -90)]
                return ps_[0] if ps_ else "9999"
            pruef = [min([x for x in pruef if x[3]] or pruef, key=_beginn)]
        for t, z, alle, mass in pruef:
            if not mass:
                spaeter = [x for x, _y in _p18_perioden(_p18_nah(alle, von, bis)) if x > bis]
                if spaeter and spaeter[0] > _p18_plus(bis, 31):
                    befunde.append("„ab %s“ — %s: Wirkorb erst ab %s"
                                   % (roh, _p18_kontakt_txt(t, z, alle), _de(spaeter[0])))
                continue
            ps = _p18_perioden(mass)
            arten = {x.get("aspekt") for x in mass}
            im_orb = [x for x in (d["jetzt"].get("im_orb") or []) if x.get("aspekt") in arten and
                      (kanon(x.get("transit", "")), kanon(x.get("ziel", ""))) == (t, z)]
            jetzt = [x for x in im_orb if x.get("im_wirkorb")]
            frueher = [(x, y) for x, y in ps if unten <= x < _p18_plus(von, -15) and
                       y >= _p18_plus(stichtag, -90) and not _p18_absatz_nennt(absatz, t, x, y, von)]
            orb_txt = ("am Stichtag Orb %s°%s" % (("%.2f" % im_orb[0]["orb_grad"]).replace(".", ","),
                                                   "" if im_orb[0].get("im_wirkorb") else
                                                   " (außerhalb des Wirkorbs)")) if im_orb else ""
            durchgehend = [(x, y) for x, y in frueher if y >= von]
            if (jetzt and von > _p18_plus(stichtag, 60)) or durchgehend:
                befunde.append("„ab %s“ — %s läuft schon: Wirkorb %s%s"
                               % (roh, _p18_kontakt_txt(t, z, mass),
                                  ", ".join("%s–%s" % (_de(x), _de(y)) for x, y in (durchgehend or ps)[:3]),
                                  ", " + orb_txt if orb_txt else ""))
            elif frueher:
                wieder = [x for x, _y in ps if x >= _p18_plus(von, -15)]
                befunde.append("„ab %s“ — %s: im Wirkorb schon %s%s%s"
                               % (roh, _p18_kontakt_txt(t, z, mass),
                                  ", ".join("%s–%s" % (_de(x), _de(y)) for x, y in frueher[:2]),
                                  "; " + orb_txt if orb_txt else "",
                                  "; wieder ab %s" % _de(wieder[0]) if wieder else ""))
    for m in _P18_BEGINNT_RE.finditer(satz):
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        if _P18_WIEDER_RE.search(klausel) or _P18_PHASE_RE.search(klausel):
            continue
        zt = _p18_zeiten_ohne_bis(klausel)
        kont, _ls = _p18_kontakte(klausel, d["ev"])
        if not zt or not kont:
            continue
        _a0, _e0, von, bis, roh = zt[0]
        starts = []
        for k in kont:                              # je Kontakt der Beginn, der der Angabe am naechsten liegt
            evs = _p18_aspekt_filter(d["ev"][k], klausel)
            ps = [x for x, _y in _p18_perioden(evs)]
            ps += [x.get("wirkorb_von_gesamt") for x in evs if x.get("wirkorb_von_gesamt")]
            ps += [(x.get("vorlauf") or {}).get("wirkorb_von") for x in evs
                   if (x.get("vorlauf") or {}).get("wirkorb_von")]
            if ps:
                starts.append((min(ps, key=lambda x: abs(_tage(von, x))), k, evs))
        if not starts:
            continue
        p.geprueft += 1
        x, k, evs = min(starts, key=lambda s: s[0])  # der Prozess beginnt mit dem fruehesten
        if not von <= x <= bis:
            befunde.append("„%s“ (%s) — %s: Wirkorb ab %s"
                           % (m.group(0), roh, _p18_kontakt_txt(k[0], k[1], evs), _de(x)))
    for m in _P18_ERSTMALS_RE.finditer(satz):
        a, e = _p18_teilsatz(satz, m.start())
        sa = max([a] + [x.end() for x in re.finditer(r",", satz[:m.start()]) if x.end() > a])
        se = satz.find(",", m.end())
        se = e if se < 0 or se > e else se
        abschnitt = satz[sa:se]
        zt = _p18_zeiten_ohne_bis(abschnitt)
        if not zt:
            continue
        rollen = _p18_rollen(abschnitt)
        ls = [f for _x, _y, f, r in rollen if r == "L"]
        zs = [f for _x, _y, f, r in rollen if r == "Z"]
        if not ls:
            ls = [f for _x, _y, f, r in _p18_rollen(satz[a:sa]) if r == "L"][-1:]
        kont = [(t, z) for t in ls for z in zs if z != t and (t, z) in d["ev"]]
        _a0, _e0, von, bis, roh = min(zt, key=lambda x: abs(x[0] - (m.start() - sa)))
        for t, z in dict.fromkeys(kont):
            evs = _p18_aspekt_filter(d["ev"][(t, z)], abschnitt)
            ex = _p18_exakt(evs)
            if _P18_IM_FENSTER_RE.search(satz[a:e]):
                ex = [x for x in ex if x >= (d["start"] or "")]
            if not ex:
                continue
            p.geprueft += 1
            if not von <= ex[0] <= bis:
                befunde.append("„%s“ (%s) — %s: zum ersten Mal exakt am %s"
                               % (m.group(0), roh, _p18_kontakt_txt(t, z, evs), _de(ex[0])))
    return _p18_melde(p, ort, satz, "Zeit", befunde)


# --- Transit: Gleichzeitigkeit ----------------------------------------------------
_P18_ZUGLEICH_RE = re.compile(_P18_GRENZ + r"(?:zugleich|gleichzeitig|zur\s+selben\s+Zeit|"
                              r"in\s+denselben\s+(?:Wochen|Monaten|Tagen)|alle\s+(?:drei|vier|beide)\s+"
                              r"(?:zusammen|auf\s+einmal))" + _P18_ENDE)
_P18_VON_BIS_RE = re.compile(_P18_GRENZ + r"(?:von|zwischen)\s+(?P<a>(?:Anfang\s+|Mitte\s+|Ende\s+)?(?:%s)"
                             r"(?:\s+(?:19|20|21)\d\d)?)\s+(?:bis|und)\s+(?P<b>(?:Anfang\s+|Mitte\s+|Ende\s+)?"
                             r"(?:%s)\s+(?:19|20|21)\d\d)" % (_MONAT_RE, _MONAT_RE))


def _p18_tage_liste(von, bis):
    from datetime import date, timedelta
    try:
        a, b = date.fromisoformat(von), date.fromisoformat(bis)
    except ValueError:
        return []
    return [(a + timedelta(n)).isoformat() for n in range((b - a).days + 1)]


_P18_GEBURT_RE = re.compile(_P18_GRENZ + r"(?:[Ii]n\s+deinem\s+Geburtsbild|[Bb]ei\s+deiner\s+Geburt|"
                            r"[Ii]m\s+Grundhoroskop|[Ii]m\s+Radix|[Vv]on\s+Geburt\s+an|seit\s+deiner\s+Geburt)"
                            + _P18_ENDE)


def _p18_zugleich(p, d, satz, ort, kapitel_kontakte):
    """„A, B und C zugleich" — die Tage, an denen jeder genannte Laeufer an einem Ziel
    des Satzes (sonst an den Zielen der THEMA-Zeile des Kapitels) im Wirkorb steht.
    Gemeldet: kein gemeinsamer Tag, oder bei einem genannten Zeitraum („von März
    bis Juni <Jahr>") weniger als ein Viertel davon."""
    if not _P18_ZUGLEICH_RE.search(satz) or _P18_GEBURT_RE.search(satz):
        return 0                                    # Aussagen ueber das Geburtsbild laufen nicht
    if _P18_KOPULA_ZUGLEICH_RE.search(satz):
        return 0                                    # „ist zugleich ein …“ = ebenfalls (2026-10-13)
    gruppen = _p18_gruppen(satz)
    laeufer = list(dict.fromkeys(t for _a, _e, ls, _zs in gruppen for t in ls))
    if len(laeufer) < 2:
        return 0
    je = {}
    for t in laeufer:
        ks = [(t, z) for _a, _e, ls, zs in gruppen if t in ls for z in zs if (t, z) in d["ev"]]
        if not ks:
            ks = [(t, z) for (tt, _art, z, _f) in kapitel_kontakte if tt == t and (t, z) in d["ev"]]
        if not ks:
            return 0                                # ein Laeufer ohne Kontakt: nicht pruefbar
        je[t] = list(dict.fromkeys(ks))
    rahmen = None
    mvb = _P18_VON_BIS_RE.search(satz)
    if mvb:
        zb = _p18_zeiten(mvb.group("b"))
        jahr_b = zb[-1][3][:4] if zb else None
        za = _p18_zeiten(mvb.group("a")) or (_p18_zeiten(mvb.group("a") + " " + jahr_b) if jahr_b else [])
        if za and zb:
            rahmen = (za[0][2], zb[-1][3])
    von, bis = rahmen or (d["start"], d["ende"])
    tage = _p18_tage_liste(von, bis) if von and bis else []
    if not tage:
        return 0
    p.geprueft += 1

    def aktiv(t, tag):
        return any(x <= tag <= y for k in je[t] for x, y in _p18_perioden(d["ev"][k]))
    gemeinsam = [tag for tag in tage if all(aktiv(t, tag) for t in je)]
    if gemeinsam and (rahmen is None or len(gemeinsam) >= 0.25 * len(tage)):
        return 0
    ziele = sorted({z for ks in je.values() for _t, z in ks})
    if gemeinsam:
        spannen, start = [], gemeinsam[0]
        for x, y in zip(gemeinsam, gemeinsam[1:] + [None]):
            if y is None or _tage(x, y) > 1:
                spannen.append((start, x))
                start = y
        wann = "nur " + ", ".join("%s–%s" % (_de(a_), _de(b_)) if a_ != b_ else _de(a_) for a_, b_ in spannen) + \
               " (%d von %d Tagen)" % (len(gemeinsam), len(tage))
    else:
        wann = "an keinem Tag" + (" zwischen %s und %s" % (_de(von), _de(bis)) if rahmen else " im Fenster")
    return _p18_melde(p, ort, satz, "Zugleich", ["%s gleichzeitig im Wirkorb (an %s): %s"
                                                  % (_p18_namen(list(je)), _p18_namen(ziele), wann)])


# --- Transit: Station ---------------------------------------------------------------
_P18_STILL_RE = re.compile(_P18_GRENZ + r"(?:still(?:zu)?steh\w*|stillsteh\w*|Stillstand\w*|Station\w*|"
                           r"bleibt\s+stehen)" + _P18_ENDE, re.I)
_P18_GENAU_RE = re.compile(_P18_GRENZ + r"(?:genau|exakt|punktgenau)" + _P18_ENDE)
_P18_STATION_ORB = 0.5


def _p18_station(p, d, satz, ort, vorher):
    """„genau … stillstehen" — der Stationsort gegen die Ziele des Satzes (sonst alle
    Ziele der Station): Liegt der naechste mehr als 0°30′ daneben, ist „genau" falsch.
    „genau" zaehlt nur im selben Kommaabschnitt und hoechstens sechs Woerter vom
    Stillstand entfernt („kommt zum Stillstand, …, und im Mai wird es noch einmal
    genau" bleibt still); erkannt auch das getrennte „steht … still"."""
    befunde = []
    treffer = [m.span() for m in _P18_STILL_RE.finditer(satz)]
    for m in re.finditer(r"(?<![\wäöüß])still(?=[\s.,;:!?)]|$)", satz):
        a, _e = _p18_klausel(satz, m.start())
        ka = satz.rfind(",", a, m.start())
        if re.search(_P18_GRENZ + r"(?:steht|stand|stehen|standen)" + _P18_ENDE,
                     satz[(ka + 1 if ka >= 0 else a):m.start()]):
            treffer.append(m.span())
    for s0, e0 in sorted(set(treffer)):
        a, e = _p18_klausel(satz, s0)
        ka = satz.rfind(",", a, s0)
        kb = satz.find(",", e0)
        abschnitt_a, abschnitt_e = (ka + 1 if ka >= 0 else a), (kb if 0 <= kb < e else e)
        abschnitt = satz[abschnitt_a:abschnitt_e]
        nah = [g for g in _P18_GENAU_RE.finditer(abschnitt)
               if len(re.findall(r"[\wäöüß]+", abschnitt[g.end():s0 - abschnitt_a] if g.end() <= s0 - abschnitt_a
                                 else abschnitt[e0 - abschnitt_a:g.start()])) <= 6]
        if not nah:
            continue
        ls = [f for _x, _y, f, r in _p18_rollen(abschnitt) if r == "L"]
        t = ls[-1] if ls else None
        if t is None and re.search(_P18_GRENZ + r"(?:er|sie)" + _P18_ENDE, abschnitt):
            t = _p18_laeufer_vor(satz, abschnitt_a) or _p18_laeufer_vor(vorher, len(vorher))
        zt = _p18_zeiten(abschnitt) or _p18_zeiten(satz[a:e]) or _p18_zeiten(satz)
        if t is None or not zt:
            continue
        _a0, _e0, von, bis, roh = zt[0]
        st = [s for s in d["stationen"] if kanon(s.get("transit", "")) == t and
              _p18_plus(von, -10) <= s.get("datum", "") <= _p18_plus(bis, 10)]
        if not st:
            continue
        s = st[0]
        ziele = {f for _x, _y, f, r in _p18_rollen(satz) if r == "Z" and f != t}
        det = [x for x in (s.get("nahe_detail") or []) if not x.get("spiegel")]
        gen = [x for x in det if kanon(x.get("ziel", "")) in ziele] or det
        if not gen:
            continue
        p.geprueft += 1
        if min(x["orb"] for x in gen) > _P18_STATION_ORB:
            befunde.append("%s %s am %s auf %s — %s (genau heißt: Orb höchstens 0°30′)"
                           % (ANZEIGE.get(t, t), s.get("richtung", ""), _de(s.get("datum")), s.get("stand", ""),
                              ", ".join("%s %s %s" % (x["aspekt"], ANZEIGE.get(kanon(x["ziel"]), x["ziel"]),
                                                      _orb_txt(round(x["orb"] * 60))) for x in gen)))
    return _p18_melde(p, ort, satz, "Station", befunde)


# --- Transit: Anzahl ------------------------------------------------------------------
_P18_ANDERE_RE = re.compile(_P18_GRENZ + r"(?P<n>zwei|drei|vier|fünf|sechs)\s+(?:andere|weitere)\s+"
                            r"(?:laufende\s+)?(?:Planeten|Kräfte|Transite)" + _P18_ENDE)
_P18_WIRKBEREICH_RE = re.compile(
    _P18_GRENZ + r"(?P<n>zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|\d{1,2})\s+(?:Berührungen|Kontakte|"
    r"Transite)\s+(?:[\wäöüß]+\s+){0,3}?im\s+(?:engen\s+)?(?:Wirkbereich|Wirkorb)" + _P18_ENDE)
_P18_PRIMAER_RE = re.compile(r"(?<![\wäöüß])(?:primär\w*|verfolgt\w*|Hauptziel\w*)")


def _p18_anzahl(p, d, satz, ort, kapitel_kontakte):
    """„n andere Planeten an dieselben Punkte" — gegen die THEMA-Zeile des Kapitels;
    „n Berührungen im engen Wirkbereich" (am Stichtag) — gegen die Jetzt-Liste."""
    befunde = []
    for m in _P18_ANDERE_RE.finditer(satz):
        soll = _zahl_wert(m.group("n"))
        if not re.search(r"(?:dieselben|diese|deine)\s+(?:beiden\s+|zwei\s+|drei\s+)?(?:Punkte|Stellen|Planeten)",
                         satz[m.end():]) or not kapitel_kontakte:
            continue
        vor = satz[:m.start()]
        rollen = _p18_rollen(vor)
        ziele = {f for _a, _e, f, r in rollen if r == "Z"}
        alt = {f for _a, _e, f, r in rollen if r == "L"}
        if not ziele:
            continue
        ist = sorted({t for (t, _art, z, _f) in kapitel_kontakte if z in ziele and t not in alt})
        p.geprueft += 1
        if ist and len(ist) != soll:
            befunde.append("„%s“ — die THEMA-Zeile des Kapitels führt an %s: %s"
                           % (m.group(0), _p18_namen(sorted(ziele)),
                              "; ".join("%s (%s)" % (ANZEIGE.get(t, t), ", ".join(
                                  "%s %s" % (art, ANZEIGE.get(z, z)) for (tt, art, z, _f) in kapitel_kontakte
                                  if tt == t and z in ziele)) for t in ist)))
    for m in _P18_WIRKBEREICH_RE.finditer(satz):
        zt = _p18_zeiten(satz)
        stichtag = d["stichtag"]
        if not stichtag or not (any(von <= stichtag <= bis for _a, _e, von, bis, _r in zt) or re.search(
                _P18_GRENZ + r"(?:[Hh]eute|[Jj]etzt|[Dd]erzeit|[Gg]erade|[Aa]m\s+Stichtag)" + _P18_ENDE, satz)):
            continue
        soll = _zahl_wert(m.group("n"))
        alle = [x for x in (d["jetzt"].get("im_orb") or []) if x.get("im_wirkorb") and not x.get("spiegel")]
        prim = [x for x in alle if x.get("primaer")]
        p.geprueft += 1
        scope = bool(_P18_PRIMAER_RE.search(satz))
        if (scope and soll == len(prim)) or (not scope and soll == len(alle)):
            continue
        befunde.append("„%s“ — am Stichtag im Wirkorb: %d (%s), davon an den primären Zielen %d%s"
                       % (m.group(0), len(alle), ", ".join("%s %s %s" % (x["transit"], x["aspekt"], x["ziel"])
                                                          for x in alle), len(prim),
                          "" if scope else " — die Zählmenge im Satz nennen"))
    return _p18_melde(p, ort, satz, "Anzahl", befunde)


# --- Transit: Wiederholungshinweis --------------------------------------------------
# 2026-10-07: auch am Satzanfang („Zuletzt stand …“) — vorher fiel jeder Satz, der mit
# „Zuletzt“, „Davor“ … beginnt, ungeprüft durch (zwei der vier falschen Saetze vom 05.–07.10.).
_P18_ZULETZT_RE = re.compile(_P18_GRENZ + r"(?:[Zz]uletzt|[Dd]avor|[Dd]as\s+letzte\s+Mal|"
                             r"[Bb]eim\s+letzten\s+Mal|[Ss]chon\s+einmal|[Vv]orher)" + _P18_ENDE)

# 2026-10-07 (FFU Transit 3+4, Wiederholungshinweis): Seit dem transit.py-Stand vom
# 2026-10-04 fuehrt `fruehere_durchgaenge` nur Durchgaenge derselben Haelfte des
# Umlaufs. Bei jedem Aspekt ausser Konjunktion und Opposition liegt zwischen zwei
# solchen Durchgaengen immer einer aus der anderen Haelfte — „zuletzt stand Jupiter
# im Trigon zu …, als du fuenfzehn warst" ist dann falsch, auch wenn das Alter stimmt.
# Der Satzteil muss die Stellung nennen („so wie jetzt", Transit-Modul, Bewegung
# „Zeit", Wiederholungshinweis); gleichwertig gelten die Formen in _P18_STELLUNG_RE.
# „Dieselbe Frage stand zuletzt an" (Innere Arbeit, Prinzip 15) nennt weder Aspekt
# noch Stand und braucht keine, solange der Satzteil kein Aspektwort traegt.
# Nicht erfasst (unveraendert): Selbst-Transite — _p18_kontakte() fuehrt T == Z nicht;
# seit 2026-10-09 bleibt ein Rueckkehr-Satzteil ohne eigenes Paar still (_P18_RUECKKEHR_RE).
_P18_EINE_HAELFTE = {"Konjunktion", "Opposition"}
_P18_STELLUNG_RE = re.compile(
    r"(?:[Ss]o\s+)?[Ww]ie\s+jetzt"
    r"|[Ii]n\s+(?:derselben|dieser|der\s+gleichen|gleicher)\s+Stellung"
    r"|[Aa]us\s+(?:derselben|dieser|der\s+gleichen)\s+Richtung"
    r"|[Vv]on\s+(?:derselben|dieser|der\s+gleichen)\s+Seite"
    r"|[Vv]o(?:m|n\s+den)\s+[A-ZÄÖÜ][\wäöüß]+\s+aus(?![\wäöüß])"
    r"|[Ii]m\s+selben\s+Abschnitt\s+seiner\s+Runde"
    r"|[Ii]n\s+derselben\s+Hälfte")
_P18_FRAGE_RE = re.compile(r"(?:[Dd]ieselbe|[Dd]ie\s+gleiche|[Dd]iese)\s+Frage")
# 2026-10-09 (Klasse-2-Sammelliste Z. 669, 694, 702, 719, 875; Chris-Freigabe): Ein
# Satzteil ueber eine Rueckkehr — meist die Knotenrueckkehr, ein Selbst-Transit, den
# _p18_kontakte() nicht fuehrt — fand kein eigenes Paar und fiel auf den Satzteil oder
# Satz davor bzw. den fuehrenden Kontakt des Kapitels zurueck; der Hinweis nannte das
# Alter eines fremden Kontakts und verleitete dazu, eine richtige Zahl zu ersetzen.
# Traegt der Satzteil „Rückkehr", „Wiederkehr" oder „kehrt … zurück" (auch „zurückkehrt",
# „Knotenrückkehr") und kein eigenes Paar aus Transiter und Ziel, bleibt er still —
# Regel (a) oben: Bezug unklar, also still. „wiederkehrend" zaehlt nicht.
_P18_RUECKKEHR_RE = re.compile(
    r"(?:R(?:ü|ue)ckkehr|Wiederkehr)(?:en)?(?![\wäöüÄÖÜß])"
    r"|(?<![\wäöüÄÖÜß])zur(?:ü|ue)ck(?:ge)?kehr\w*"
    r"|(?<![\wäöüÄÖÜß])kehr(?:t|en|te|ten)(?![\wäöüÄÖÜß])(?:\s+[\wäöüÄÖÜß-]+){0,8}?"
    r"\s+zur(?:ü|ue)ck(?![\wäöüÄÖÜß])", re.I)


def _p18_stellung_genannt(teil):
    """Nennt der Satzteil die Stellung — oder spricht er nur von „derselben Frage“,
    ohne Aspektwort? (s. Kommentar oben)"""
    if _P18_STELLUNG_RE.search(teil):
        return True
    return bool(_P18_FRAGE_RE.search(teil)) and not ASPEKT_RE.search(teil)


def _p18_frueher_index(events):
    idx = {}
    for f in (events or {}).get("fruehere_durchgaenge", []) or []:
        idx.setdefault((kanon(f.get("transit", "")), kanon(f.get("ziel", ""))), []).append(f)
    return idx


def _p18_alter_im_satz(satz):
    out, listen = [], []
    for m in _P11_ALTER_LISTE.finditer(satz):
        listen.append((m.start(), m.end()))
        for glied in _P11_LISTE_TRENNER.split(m.group("liste")):
            g = _P11_Q_RE.sub("", glied.strip(), count=1).strip()
            n = _zahl_wert(g)
            if n is not None:
                out.append((g, n))
    for m in _P11_ALTER[1].finditer(satz):
        if any(a <= m.start() < e for a, e in listen):
            continue
        n = _zahl_wert(m.group("n"))
        if n is not None:
            out.append((m.group("n"), n))
    return out


def _p18_wiederholung(p, d, satz, vorher, ort, kapitel_kontakte):
    """„… stand zuletzt so zu deiner Venus, als du dreißig warst" — das Alter muss bei
    DIESEM Kontakt unter den frueheren Durchgaengen stehen (events.json; seit dem
    transit.py-Stand vom 2026-10-04 nur Durchgaenge derselben Haelfte des Umlaufs),
    ±1 Jahr. Je Satzteil (Grenze: Semikolon): Kontakt aus dem Satzteil, sonst aus dem
    Satzteil oder Satz davor — nennt der Satzteil einen eigenen Laeufer ohne Ziel
    („…; Jupiter zuletzt, als du …"), mit dem Ziel davor —, sonst der fuehrende Kontakt
    des Kapitels; die Aspektart aus dem Satzteil, sonst aus der THEMA-Zeile. Nennt der
    Satzteil mehrere Ziele, muss das Alter zu einem davon passen. Seit 2026-10-07: Hat ein
    Kontakt nur Aspekte mit zwei Haelften (alles ausser Konjunktion und Opposition), muss
    der Satzteil die Stellung nennen (_p18_stellung_genannt), auch wenn das Alter stimmt.
    Seit 2026-10-09: Ein Satzteil mit „Rückkehr“, „Wiederkehr“ oder „kehrt … zurück“ ohne
    eigenes Paar bleibt still (_P18_RUECKKEHR_RE) — kein Rueckfall auf andere Kontakte."""
    if not d["frueher"] or not _P18_ZULETZT_RE.search(satz):
        return 0
    befunde = []
    teile = satz.split(";")
    for i_t, teil in enumerate(teile):
        alter = _p18_alter_im_satz(teil)
        if not alter:
            continue
        paare, ls = _p18_kontakte(teil, d["frueher"])
        if not paare and _P18_RUECKKEHR_RE.search(teil):
            continue                                 # 2026-10-09: Rueckkehr ohne eigenes Paar — still
        davor = teile[i_t - 1] if i_t else vorher
        if not paare and davor:
            paare_d, _l = _p18_kontakte(davor, d["frueher"])
            if ls:
                paare = [(t, z) for t in ls for _t, z in paare_d if (t, z) in d["frueher"]]
                if not paare and paare_d:
                    continue                         # anderer Laeufer ohne gefuehrten Kontakt: offen
            else:
                paare = paare_d
        arten = {_art(m.group(1)) if m.group(1) else _ASP_GLYPH.get(m.group(2)) for m in ASPEKT_RE.finditer(teil)}
        arten.discard(None)
        if not paare:
            fuehrt = [(t, art, z) for (t, art, z, f) in kapitel_kontakte if f == "fuehrt"]
            paare = [(t, z) for (t, _a, z) in fuehrt if (not ls or t in ls) and (t, z) in d["frueher"]]
            if not arten:
                arten = {a for (_t, a, _z) in fuehrt}
        paare = list(dict.fromkeys(paare))
        if not paare or len({t for t, _z in paare}) > 1:
            continue                                 # Bezug nicht eindeutig
        je, zwei_haelften = [], []
        for t, z in paare:
            eintraege = d["frueher"][(t, z)]
            arten_k = arten or {art for (tt, art, zz, _f) in kapitel_kontakte if (tt, zz) == (t, z)}
            gefiltert = [f for f in eintraege if not arten_k or f.get("aspekt") in arten_k] or eintraege
            arten_g = {f.get("aspekt") for f in gefiltert} - {None}
            if arten_g and not (arten_g & _P18_EINE_HAELFTE):
                zwei_haelften.append("%s %s %s" % (ANZEIGE.get(t, t), "/".join(sorted(arten_g)),
                                                   ANZEIGE.get(z, z)))
            bekannt = set()
            for f in gefiltert:
                for dg in f.get("durchgaenge") or []:
                    bekannt |= {x.get("alter") for x in dg.get("exakt") or [] if x.get("alter") is not None}
                    if dg.get("min_orb_alter") is not None:
                        bekannt.add(dg["min_orb_alter"])
            je.append(("/".join("%s %s %s" % (ANZEIGE.get(t, t), f.get("aspekt"), ANZEIGE.get(z, z))
                                for f in gefiltert), bekannt))
        p.geprueft += 1
        if zwei_haelften and not _p18_stellung_genannt(teil):
            befunde.append("ohne Stellung — %s: zwischen diesem Durchgang und heute lag einer aus "
                           "der anderen Hälfte des Umlaufs, „zuletzt“ stimmt so nicht; die Stellung "
                           "nennen („so wie jetzt“, Transit-Modul, Wiederholungshinweis)"
                           % ", ".join(dict.fromkeys(zwei_haelften)))
        falsch = [(roh, n) for roh, n in alter if not any(abs(n - a) <= 1 for _k, b in je for a in b)]
        if not falsch:
            continue
        wo = [("Alter " + ", ".join(map(str, sorted(b)))) if b else "keiner seit der Geburt" for _k, b in je]
        alt_txt = ", ".join("„%s“ (%d)" % (r, n) for r, n in falsch)
        if len(je) == 1:
            befunde.append("%s — %s; frühere Durchgänge in derselben Hälfte des Umlaufs: %s"
                           % (alt_txt, je[0][0], wo[0]))
        else:
            befunde.append("%s — frühere Durchgänge in derselben Hälfte des Umlaufs: %s"
                           % (alt_txt, " · ".join("%s: %s" % (k, w) for (k, _b), w in zip(je, wo))))
    return _p18_melde(p, ort, satz, "Wiederholung", befunde)




# --- Transit: verneinter Wiederholungshinweis --------------------------------------
# 2026-10-07b (Auswertung der Pruefberichte vom 07.10., zweite Runde): Ein Transit-Text
# schrieb „Keine dieser Verbindungen gab es seit deiner Geburt" — zwei der Verbindungen
# hatte es aus der ANDEREN Haelfte des Umlaufs schon gegeben. `fruehere_durchgaenge` fuehrt
# seit dem transit.py-Stand vom 2026-10-04 nur dieselbe Haelfte; eine leere Liste heisst
# nicht, dass es den Aspekt seit der Geburt nie gab. Die Verneinung frueherer Durchgaenge
# („… gab es seit deiner Geburt nicht", „zum ersten Mal in deinem Leben") braucht deshalb
# bei Aspekten mit zwei Haelften die Stellung (_p18_stellung_genannt), und sie ist falsch,
# sobald in derselben Haelfte schon ein Durchgang lief. Bezug: Kontakte im Satzteil; ohne
# sie bei einem Plural („dieser Verbindungen") alle Kontakte des Kapitels, sonst der
# Satzteil oder Satz davor, sonst der fuehrende Kontakt (wie in _p18_wiederholung). Ohne „seit deiner Geburt"/„in deinem Leben" bleibt die
# Probe still — „wird zum ersten Mal genau" meint die laufende Passage.
_P18_NIE_ANKER_RE = re.compile(
    _P18_GRENZ + r"(?:seit\s+deiner\s+Geburt|in\s+deinem\s+(?:ganzen\s+|bisherigen\s+)?Leben)"
    + _P18_ENDE, re.I)
_P18_NIE_VERNEINUNG_RE = re.compile(
    _P18_GRENZ + r"(?:kein(?:e|er|en|em|es)?|nicht|nie|niemals|zum\s+ersten\s+Mal|erstmals"
    r"|das\s+erste\s+Mal)" + _P18_ENDE, re.I)
_P18_NIE_BEZUG_RE = re.compile(
    _P18_GRENZ + r"(?:Verbindung\w*|Durchg[aä]ng\w*|Kontakt\w*|Runde\w*|Berührung\w*|Rückkehr"
    r"|stand|standen|gab\s+es|gegeben)" + _P18_ENDE, re.I)
_P18_NIE_PLURAL_RE = re.compile(
    _P18_GRENZ + r"(?:Verbindungen|Durchgänge|Kontakte|Berührungen|Runden)" + _P18_ENDE, re.I)


def _p18_nie_seit_geburt(p, d, satz, vorher, ort, kapitel_kontakte):
    """„Keine dieser Verbindungen gab es seit deiner Geburt", „… zum ersten Mal in deinem
    Leben" — die Verneinung frueherer Durchgaenge (s. Kommentar oben). PRUEFEN, wenn ein
    gemeinter Kontakt in derselben Haelfte schon einen frueheren Durchgang hat (mit Alter),
    oder wenn er nur Aspekte mit zwei Haelften hat und der Satzteil die Stellung nicht
    nennt — die andere Haelfte fuehrt der Report nicht."""
    if not d["frueher"] or not _P18_NIE_ANKER_RE.search(satz):
        return 0
    befunde = []
    teile = satz.split(";")
    for i_t, teil in enumerate(teile):
        if not (_P18_NIE_ANKER_RE.search(teil) and _P18_NIE_VERNEINUNG_RE.search(teil)
                and (_P18_NIE_BEZUG_RE.search(teil) or ASPEKT_RE.search(teil))):
            continue
        paare, _ls = _p18_kontakte(teil, d["frueher"])
        if not paare and _P18_NIE_PLURAL_RE.search(teil):      # „Keine dieser Verbindungen …“
            paare = [(t, z) for (t, _a, z, _f) in kapitel_kontakte if (t, z) in d["frueher"]]
        davor = teile[i_t - 1] if i_t else vorher
        if not paare and davor:
            paare, _l = _p18_kontakte(davor, d["frueher"])
        arten = {_art(m.group(1)) if m.group(1) else _ASP_GLYPH.get(m.group(2))
                 for m in ASPEKT_RE.finditer(teil)}
        arten.discard(None)
        if not paare:
            paare = [(t, z) for (t, _a, z, f) in kapitel_kontakte
                     if f == "fuehrt" and (t, z) in d["frueher"]]
        paare = list(dict.fromkeys(paare))
        if not paare:
            continue
        p.geprueft += 1
        stellung = _p18_stellung_genannt(teil)
        gewesen, zwei = [], []
        for t, z in paare:
            arten_k = arten or {art for (tt, art, zz, _f) in kapitel_kontakte if (tt, zz) == (t, z)}
            eintraege = d["frueher"][(t, z)]
            gefiltert = [f for f in eintraege if not arten_k or f.get("aspekt") in arten_k] or eintraege
            for f in gefiltert:
                name = "%s %s %s" % (ANZEIGE.get(t, t), f.get("aspekt"), ANZEIGE.get(z, z))
                alter = set()
                for dg in f.get("durchgaenge") or []:
                    alter |= {x.get("alter") for x in dg.get("exakt") or [] if x.get("alter") is not None}
                    if dg.get("min_orb_alter") is not None:
                        alter.add(dg["min_orb_alter"])
                if f.get("durchgaenge"):
                    gewesen.append("%s (Alter %s)" % (name, ", ".join(map(str, sorted(alter))) or "?"))
                elif f.get("aspekt") not in _P18_EINE_HAELFTE and not stellung:
                    zwei.append(name)
        if gewesen:
            befunde.append("verneint frühere Durchgänge, aber in derselben Hälfte des Umlaufs lief "
                           "schon einer — %s" % ", ".join(dict.fromkeys(gewesen)))
        if zwei:
            befunde.append("verneint frühere Durchgänge ohne Stellung — %s: der Report führt nur "
                           "Durchgänge derselben Hälfte des Umlaufs; aus der anderen kann es seit "
                           "der Geburt schon einen gegeben haben. Die Stellung nennen („so wie "
                           "jetzt“) oder den Satz streichen (Transit-Modul, Wiederholungshinweis)"
                           % ", ".join(dict.fromkeys(zwei)))
    return _p18_melde(p, ort, satz, "Wiederholung", befunde)


# --- Transit: Grenze, Wechsel, Abstand, Buendel, Genau, Kapitelzeit, Dauer --------
# 2026-10-13 (Wartungslauf „Proben fuer Zeit, Naehe, Register und Fundstellen“,
# Strang 1; Startprompt `claude/STARTPROMPT_Probenlauf_2026-10-13.md`). Warum: Nach den
# Proben von Schritt 2 standen in jedem Transit-Text und in „Die Zeit“ der Vertiefung
# noch Fehler in Zeitangaben, die nur ein Zweitleser fand (Auswertung der
# Pruefberichte vom 13.10., W4 und W5; Sammelliste: „keine Probe fuer Zeitraum- und
# Reihenfolgeaussagen ueber mehrere Kontakte“). Die Satzarten:
#   Grenze      „bis <Zeit>“ (das Ende des Kontakts, Fortsetzung eingeschlossen),
#               „von <Zeit> bis <Zeit>“ (eine Wirkorb-Strecke), „über das Ende dieses
#               Fensters hinaus“ (am Fensterende im Wirkorb), dazu Haus und Zeichen.
#   Wechsel     „rückt/wechselt/tritt <Zeit> in den <Zeichen>/ins <n>. Haus“ und
#               „ab <Zeit> <T> in deinem <n>. (Haus)“ — gegen Zeichenaufenthalt und
#               Hausdurchgang; kein Spielraum.
#   Abstand     „(etwa) einen Tag/eine Woche nach/vor/später …“, „neben“, „im
#               Gefolge“, „dazwischen“ — Exaktdaten gegen Exaktdaten (Sonnenbogen:
#               `zusatz.sonnenbogen`).
#   Buendel     „A, B und C im Trigon zu X und Y“ in Signatur und Fliesstext: JEDES
#               Paar braucht den Kontakt der genannten Art (P13 laesst ein Buendel
#               durch, sobald EIN Paar gedeckt ist).
#   Genau       „genau <Zeit>, <Zeit> und <Zeit>“, „folgt <Zeit>“, „geht <Zeit> über
#               deinen X“ — jede Zeit traegt ein Exaktdatum.
#   Kapitelzeit „<n> Kapitel“ in einer Zeit, „Kapitel n“ in einer Zeit oder „diese
#               Monate“, „Auftakt von Kapitel n“ — gegen die `@@ZEITLEISTE` (dicht=)
#               und die Wirkorb-Zeiten der THEMA-Kontakte.
#   Dauer       „fast die ganzen zwei Jahre“, „das ganze Fenster“, „den größten Teil“
#               — Anteil eines Hausdurchgangs oder Zeichenaufenthalts am Fenster.
# Dieselben zwei Regeln wie oben: nur PRUEFEN, nur bei WIDERSPRUCH, jeder Hinweis mit
# dem Datenwert; was sich nicht lesen laesst (Pronomen ohne Bezug, kein Kontakt im
# Satzteil), bleibt still.
# Schwellen (Chris-Entscheidung 2026-10-13, Fragenblock des Wartungslaufs, Frage d1: „ja“): Anfang/Mitte/Ende
# eines Monats 1.–10./11.–20./21.–Monatsende, eines Jahres Januar–April/Mai–August/
# September–Dezember (wie _p18_zeiten); „ein Tag“ 1, „eine Woche“ 6–8, „gut eine Woche“
# 8–10, „knapp eine Woche“ 5–7, „etwa eine Woche“ 5–9 Tage; kein Spielraum bei
# Exaktdaten, Haus- und Zeichenwechseln. „fast ganz“ heisst mindestens P18_FAST_GANZ.

P18_FAST_GANZ = 0.90
P18_GANZ = 0.98
P18_GROESSTER_TEIL = 0.5

_P18_ZEIT_ALT = (r"(?:Anfang\s+|Mitte\s+|Ende\s+)?(?:%s|Frühjahr\w*|Frühling\w*|Sommer\w*|Herbst\w*|"
                 r"Winter\w*|Früh\w+|Spät\w+|Hoch\w+|(?:19|20|21)\d\d)" % _MONAT_RE)
_P18_BIS_RE = re.compile(_P18_GRENZ + r"[Bb]is\s+(?:(?:in\s+(?:den|die|das)|ins|zum|zur)\s+)?"
                         r"(?=" + _P18_ZEIT_ALT + r")")
_P18_VON_VOR_RE = re.compile(r"(?:(?:[Vv]on|[Zz]wischen|[Ss]eit)\s+(?:dem\s+|der\s+)?|(?:^|[,;:(]\s*|\s—\s)(?:dann\s+)?)"
                             + _P18_ZEIT_ALT + r"(?:\s+(?:19|20|21)\d\d)?(?:\s+und)?\s*$")
_P18_REL_HAUS_RE = re.compile(r",\s+(?:der|die|das|dem|den|durch\s+das|durch\s+den|in\s+dem|in\s+das|wo)\s|"
                              r"Haus|Bereich|Feld")
_P18_UEBER_FENSTER_RE = re.compile(_P18_GRENZ + r"über\s+(?:das\s+Ende\s+(?:dieses|des)\s+Fensters|"
                                   r"(?:das|dieses)\s+Fenster|den\s+Rechenhorizont)\s+hinaus" + _P18_ENDE)
_P18_HAUS_ORD_RE = re.compile(_P18_GRENZ + r"(?:(?:in|durch)\s+(?:dein(?:em|en)?|das|den)|im|ins)\s+"
                              r"(?P<o>%s)(?:(?P<haus>\s+Haus\w*)|(?=\s*(?:[,.;:!?)]|$|\s[—–]\s|\s+(?:und|oder|bis|"
                              r"ab|seit|dann)\s)))" % _P18_ORD_RE + _P18_ENDE)
_P18_IN_ZEICHEN_RE = re.compile(_P18_GRENZ + r"(?:in\s+(?:den|die|das)|ins)\s+(?P<z>%s)" % ZEICHEN_RE
                                + _P18_ENDE)
_P18_IN_HAUS_RE = re.compile(_P18_GRENZ + r"(?:ins|in\s+(?:das|dein|deinen))\s+(?P<o>%s)\s+Haus"
                             % _P18_ORD_RE + _P18_ENDE)
_P18_WECHSEL_RE = re.compile(_P18_GRENZ + r"(?:rückt|rücken|rückte|wechselt|wechseln|wechselte|tritt|treten|"
                             r"trat|zieht|ziehen|zog|wandert|wandern|wanderte|kommt|kommen|kam|gelangt|gelangen)"
                             + _P18_ENDE)
_P18_HAELFTE_RE = re.compile(_P18_GRENZ + r"(?P<n>erst|zweit)en?\s+(?P<mon>%s)hälfte(?:\s+(?P<j>(?:19|20|21)"
                             r"\d\d))?" % _MONAT_RE, re.I)
_P18_GENITIV_LAEUFER_RE = re.compile(_P18_GRENZ + r"(?P<t>Jupiter|Saturn|Uranus|Neptun|Pluto|Chiron)s\s+"
                                     r"(?:%s)" % "|".join(w for w, _g in ASPEKTE) + _P18_ENDE)


def _p18_perioden_gesamt(evs):
    """Wirkorb-Perioden samt Vorlauf UND Fortsetzung -> sortiert [(von, bis)]."""
    out = list(_p18_perioden(evs))
    for e in evs:
        out += [tuple(x) for x in ((e.get("fortsetzung") or {}).get("wirkorb_perioden") or [])]
    return sorted(set(out))


def _p18_ende_gesamt(evs, fenster_ende=None):
    """(Ende des letzten Wirkorbs, offen?) — offen, wenn die Fortsetzung den
    Rechenhorizont erreicht und das Ende also nicht bekannt ist; ebenso, wenn eine
    aeltere events.json keine Fortsetzung fuehrt und der Wirkorb am Fensterende
    abbricht (Gegenpruefung 2026-10-13)."""
    ends = [y for _x, y in _p18_perioden_gesamt(evs)]
    ends += [e.get("wirkorb_bis_gesamt") for e in evs if e.get("wirkorb_bis_gesamt")]
    offen = any((e.get("fortsetzung") or {}).get("horizont_erreicht") for e in evs)
    ende = max(ends) if ends else None
    if not offen and ende and fenster_ende and ende >= fenster_ende and \
            not any("fortsetzung" in e or "wirkorb_bis_gesamt" in e for e in evs):
        offen = True
    return ende, offen


_P18_MONAT_NACKT_RE = re.compile(_P18_GRENZ + r"(?:(?P<wo>Anfang|Mitte|Ende)\s+)?(?P<mon>%s)(?!\s+(?:19|20|21)\d\d)"
                                 % _MONAT_RE + _P18_ENDE)


def _p18_zeiten_plus(text, jahr_text=None):
    """_p18_zeiten, dazu die Monatshaelften („in der ersten Märzhälfte 2031“) und
    Monate ohne Jahr in einer Aufzaehlung („im März und im Oktober 2031“) — das Jahr
    aus der naechsten Jahreszahl dahinter, sonst der davor."""
    import calendar
    out = list(_p18_zeiten(text))
    for m in _P18_MONAT_NACKT_RE.finditer(text or ""):
        if any(a <= m.start() < e for a, e, _v, _b, _r in out):
            continue
        hinter = re.search(r"(?:19|20|21)\d\d", text[m.end():m.end() + 60])
        davor = re.findall(r"(?:19|20|21)\d\d", text[max(0, m.start() - 80):m.start()])
        mo = _MONATE[m.group("mon").casefold()]
        # Gegenpruefung 2026-10-13: Jahreswechsel — „im November und im Februar 2032“ ist
        # November 2031, „im Dezember 2031 und im März“ ist März 2032.
        z_hinter = [z for z in _p18_zeiten(text[m.end():m.end() + 60]) if z[2][5:7] == z[3][5:7]]
        z_davor = [z for z in _p18_zeiten(text[max(0, m.start() - 80):m.start()]) if z[2][5:7] == z[3][5:7]]
        if hinter:
            j = int(hinter.group(0))
            if z_hinter and int(z_hinter[0][2][:4]) == j and mo > int(z_hinter[0][2][5:7]):
                j -= 1
        elif davor:
            j = int(davor[-1])
            if z_davor and int(z_davor[-1][2][:4]) == j and mo < int(z_davor[-1][2][5:7]):
                j += 1
        else:
            continue
        letzt = calendar.monthrange(j, mo)[1]
        t1, t2 = {"": (1, letzt), "anfang": (1, 10), "mitte": (11, 20),
                  "ende": (21, letzt)}[(m.group("wo") or "").casefold()]
        out.append((m.start(), m.end(), "%04d-%02d-%02d" % (j, mo, t1), "%04d-%02d-%02d" % (j, mo, t2),
                    m.group(0)))
    for m in _P18_HAELFTE_RE.finditer(text or ""):
        j = m.group("j")
        if not j:
            jj = re.findall(r"(?:19|20|21)\d\d", text) or re.findall(r"(?:19|20|21)\d\d", jahr_text or "")
            if not jj:
                continue
            j = jj[0]
        j, mo = int(j), _MONATE[m.group("mon").casefold()]
        letzt = calendar.monthrange(j, mo)[1]
        t1, t2 = (1, 15) if m.group("n").casefold() == "erst" else (16, letzt)
        out = [z for z in out if not (z[0] >= m.start() and z[1] <= m.end())]
        out.append((m.start(), m.end(), "%04d-%02d-%02d" % (j, mo, t1), "%04d-%02d-%02d" % (j, mo, t2),
                    m.group(0)))
    return sorted(out)


def _p18_laeufer_plus(text):
    """Laeufer eines Textes wie _p18_rollen, dazu der Genitiv vor einem Aspektwort
    („Saturns Quadrat zu deinem Merkur“)."""
    ls = [f for _a, _e, f, r in _p18_rollen(text) if r == "L"]
    ls += [kanon(m.group("t")) for m in _P18_GENITIV_LAEUFER_RE.finditer(text or "")]
    return list(dict.fromkeys(ls))


def _p18_ziele(text):
    return list(dict.fromkeys(f for _a, _e, f, r in _p18_rollen(text) if r == "Z"))


def _p18_lz(text, d):
    """(Laeufer, Ziele) eines Textes. Rueckfall, wenn die Rollen keinen Laeufer finden
    („… mit Chiron, der im Sextil zu Mond und Venus steht“): ein Transiter unter
    den Zielen, den die Rechnung mit einem der anderen Ziele fuehrt."""
    ls, zs = _p18_laeufer_plus(text), _p18_ziele(text)
    if not ls:
        kand = [f for f in zs if f in _P18_TRANSITER and
                any((f, z) in d["ev"] for z in zs if z != f)]
        if kand:
            ls = kand[:1]
            zs = [z for z in zs if z not in ls]
    return ls, zs


def _p18_ohne_floskeln(text):
    """Text ohne die Wendungen, die ein Aspektbild vortaeuschen („über das Ende dieses
    Fensters hinaus“ ist keine Konjunktion)."""
    return _P18_UEBER_FENSTER_RE.sub(" ", text or "")


def _p18_kontakte_von(d, laeufer, ziele, klausel):
    """[(T, Z, evs)] fuer jedes Paar Laeufer x Ziel, das die Rechnung fuehrt — gefiltert
    nach der Aspektart, die die Klausel nennt."""
    out = []
    for t in laeufer:
        for z in ziele:
            if z == t and not re.search(r"(?:dein\w*|R-)\s+%s" % re.escape(ANZEIGE.get(t, t)), klausel or ""):
                continue
            evs = _p18_aspekt_filter(d["ev"].get((t, z), []), _p18_ohne_floskeln(klausel))
            if evs:
                out.append((t, z, evs))
    return out


def _p18_zeitraum_txt(von, bis):
    return "%s–%s" % (_de(von), _de(bis))


_P18_SAMMEL_RE = re.compile(_P18_GRENZ + r"(?:in\s+(?:zwei|drei|vier|fünf|mehreren|einigen)\s+Wellen|nacheinander|"
                            r"der\s+Reihe\s+nach|einer\s+nach\s+dem\s+anderen|insgesamt|zusammengenommen|"
                            r"zusammen\s+genommen|alles\s+in\s+allem)" + _P18_ENDE, re.I)
_P18_LAEUFIG_RE = re.compile(_P18_GRENZ + r"(?:rückläufig\w*|direktläufig\w*|Rückläufigkeit|Stillstand\w*|"
                             r"Station\w*)" + _P18_ENDE, re.I)
_P18_HAUS_NACH_ZEIT_RE = re.compile(r"\s*(?:(?:durch|in)\s+(?:dein(?:em|en)?|das|den)\s+|im\s+|ins\s+)"
                                    r"(?P<o>%s)\s+Haus" % _P18_ORD_RE)


def _p18_grenze_paare(d, satz, a, m_start, nxt):
    """(Paare, Ziele_im_Segment?) einer „bis“-Stelle: Ziele im Segment vor dem ersten
    Laeufer des Segments gehoeren zur letzten Laeufergruppe davor; jede weitere Gruppe
    im Segment bringt ihre eigenen Paare mit („Saturn steht bis … deinem Merkur
    gegenüber und Uranus im Trigon zu deinem Mond“ — das „bis“ gilt in der Ellipse
    fuer beide). Ohne Ziel im Segment die Ziele davor, wenn kein Relativsatz und kein
    Haus dazwischen steht („…, das er bis zum Herbst durchquert“ meint das Haus)."""
    segment = satz[m_start:nxt]
    vorn = satz[a:m_start]
    gr_vorn = [g for g in _p18_gruppen(vorn) if g[2]]
    ls_vorn = gr_vorn[-1][2] if gr_vorn else []
    rollen = _p18_rollen(segment)
    erste_l = next((i for i, r in enumerate(rollen) if r[3] == "L"), len(rollen))
    ziele_vor = [r[2] for r in rollen[:erste_l] if r[3] == "Z"]
    paare = []
    if not ls_vorn and ziele_vor:
        ls_lz, _zs = _p18_lz(vorn + " " + segment, d)
        ls_vorn = ls_lz
        ziele_vor = [z for z in ziele_vor if z not in ls_lz]
    paare += [(t, z) for t in ls_vorn for z in ziele_vor if z != t]
    if erste_l < len(rollen):
        for _ga, _ge, ls_g, zs_g in _p18_gruppen(segment[rollen[erste_l][0]:]):
            paare += [(t, z) for t in ls_g for z in zs_g if z != t]
    im_segment = bool(paare)
    if not paare:
        zs = _p18_ziele(vorn)
        if not ls_vorn:                             # „die Welle der Opposition von Saturn zu …“
            ls_vorn, zs = _p18_lz(vorn, d)
        letzt = max((r[1] for r in _p18_rollen(vorn) if r[3] == "Z"), default=0)
        if zs and ls_vorn and not _P18_REL_HAUS_RE.search(vorn[letzt:]):
            paare = [(t, z) for t in ls_vorn for z in zs if z != t]
    return list(dict.fromkeys(paare)), im_segment, ls_vorn


def _p18_grenze(p, d, satz, ort):
    """„bis <Zeit>“, „von <Zeit> bis <Zeit>“, „über das Ende dieses Fensters hinaus“.
    Mehrere Ziele hinter EINEM „bis“ werden je Paar geprueft — „bis März im Quadrat
    zu Merkur und Mond“ ist falsch, wenn das Quadrat zum Merkur im Januar endet (so
    werteten es die Zweitleser vom 12.10.) —, als Sammelaussage nur mit einem Sammelwort („in
    drei Wellen“, „nacheinander“). Eine Teilstrecke („die zweite Welle … bis …“)
    braucht nur EIN Wirkorb-Ende in der Zeit; ein Haus direkt hinter der Zeit macht
    das „bis“ zur Aussage ueber den Hausdurchgang (Gegenpruefung 2026-10-13)."""
    befunde = []
    treffer = list(_P18_BIS_RE.finditer(satz))
    for i, m in enumerate(treffer):
        zt = _p18_zeiten_plus(satz[m.end():m.end() + 40], satz)
        if not zt or zt[0][0] > 2:
            continue
        _a0, e0, von, bis, roh = zt[0]
        if _P18_ZEITLISTE_NACH_RE.match(satz[m.end() + e0:m.end() + e0 + 40]):
            continue
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        nxt = treffer[i + 1].start() if i + 1 < len(treffer) and treffer[i + 1].start() < e else e
        segment = satz[m.start():nxt]
        mvon = _P18_VON_VOR_RE.search(satz[max(a, m.start() - 70):m.start()])
        vorn = satz[a:m.start()]
        paare, im_segment, ls_vorn = _p18_grenze_paare(d, satz, a, m.start(), nxt)
        ls = list(dict.fromkeys([t for t, _z in paare] or ls_vorn or _p18_laeufer_plus(segment)))
        mh_direkt = _P18_HAUS_NACH_ZEIT_RE.match(satz[m.end() + e0:m.end() + e0 + 50])
        kont = []
        if not mh_direkt:
            kont = []
            for t, z in paare:
                evs = _p18_aspekt_filter(d["ev"].get((t, z), []), _p18_ohne_floskeln(klausel))
                if evs:
                    kont.append((t, z, evs))
        if kont and not _p18_aspektarten(_p18_ohne_floskeln(klausel)):
            # ohne Aspektwort nur eindeutige Paare (eine Aspektart je Paar)
            kont = [k for k in kont if len({x.get("aspekt") for x in k[2]}) == 1]
        if not kont:
            mh = mh_direkt or _P18_HAUS_ORD_RE.search(segment) or _P18_HAUS_ORD_RE.search(vorn)
            if mh and ls and d.get("haeuser_durch"):
                h = _p18_ord_wert(mh.group("o"))
                hs = [x for x in d["haeuser_durch"] if kanon(x.get("transit", "")) == ls[0]
                      and x.get("haus") == h]
                if hs:
                    p.geprueft += 1
                    ende = max(x["bis"] for x in hs)
                    weiter = any(x.get("laeuft_weiter") for x in hs)
                    if weiter and bis >= (d["ende"] or ""):
                        continue
                    if not (von <= ende <= bis):
                        befunde.append("„bis %s“ — %s in Haus %d bis %s%s (Hausdurchgang)"
                                       % (roh, ANZEIGE.get(ls[0], ls[0]), h, _de(ende),
                                          ", läuft über das Fenster hinaus" if weiter else ""))
            continue
        if _P18_LAEUFIG_RE.search(vorn):
            continue                                # Lauf-Phase (Station, Rueckläufigkeit): eigene Satzart
        p.geprueft += 1
        if mvon:
            # Zeitraum „(von) X bis Y“: der Kontakt steht irgendwann darin im Wirkorb
            zv = _p18_zeiten_plus(_ws(mvon.group(0)) + " bis " + roh)
            v1 = zv[0][2] if zv and zv[0][0] < len(_ws(mvon.group(0))) else None
            if v1:
                for t, z, evs in kont:
                    ps = _p18_perioden_gesamt(evs)
                    if ps and not any(x <= bis and y >= v1 for x, y in ps):
                        befunde.append("„%s bis %s“ — %s: Wirkorb %s"
                                       % (_ws(mvon.group(0)), roh, _p18_kontakt_txt(t, z, evs),
                                          ", ".join(_p18_zeitraum_txt(x, y) for x, y in ps[:4])))
                continue
        if _P18_PHASE_RE.search(vorn):
            # Teilstrecke: EIN Wirkorb-Ende in der Zeit genuegt
            for t, z, evs in kont:
                ps = _p18_perioden_gesamt(evs)
                if ps and not any(von <= y <= bis for _x, y in ps):
                    befunde.append("„bis %s“ — %s: keine Wirkorb-Strecke endet darin (%s)"
                                   % (roh, _p18_kontakt_txt(t, z, evs),
                                      ", ".join(_p18_zeitraum_txt(x, y) for x, y in ps[:4])))
            continue
        einzeln = not _P18_SAMMEL_RE.search(klausel)
        if einzeln:
            pruef = [(t, z, evs) for t, z, evs in kont]
        else:                                       # Sammelaussage: das letzte Ende zaehlt
            pruef = [(kont[0][0], kont[0][1], [x for _t, _z, evs in kont for x in evs])]
        for t, z, evs in pruef:
            ende, offen = _p18_ende_gesamt(evs, d.get("ende"))
            if not ende:
                continue
            if offen and bis >= ende:
                continue
            if not (von <= ende <= bis):
                wer = _p18_kontakt_txt(t, z, evs) if einzeln else "die genannten Kontakte (%s)" % ", ".join(
                    _p18_kontakt_txt(t_, z_, e_) for t_, z_, e_ in kont)
                if not einzeln:
                    letzte = max(kont, key=lambda k: _p18_ende_gesamt(k[2], d.get("ende"))[0] or "")
                    wer += ", zuletzt %s" % _p18_kontakt_txt(*letzte)
                befunde.append("„bis %s“ — %s: Wirkorb bis %s%s"
                               % (roh, wer, _de(ende), " (Rechenhorizont, läuft weiter)" if offen else ""))
    for m in _P18_UEBER_FENSTER_RE.finditer(satz):
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        ls, zs = _p18_lz(klausel, d)
        kont = _p18_kontakte_von(d, ls, zs, klausel)
        ende_f = d["ende"] or ""
        if not kont or not ende_f:
            continue
        p.geprueft += 1
        rueckkehr = bool(_P18_WIEDER_RE.search(klausel))
        for t, z, evs in kont:
            ps = _p18_perioden_gesamt(evs)
            # Gegenpruefung 2026-10-13: Mit einem Wiederkehr-Wort („kehrt … zurück“,
            # „wieder“) genuegt eine Strecke NACH dem Fensterende; sonst heisst „über das
            # Ende hinaus“, dass der Kontakt am Fensterende im Wirkorb steht.
            if ps and not (any(y >= ende_f for _x, y in ps) if rueckkehr
                           else any(x <= ende_f <= y for x, y in ps)):
                vorher_p = [q for q in ps if q[1] <= ende_f]
                spaeter = [x for x, _y in ps if x > ende_f]
                befunde.append("„%s“ — %s: am Fensterende (%s) nicht im Wirkorb — Wirkorb %s%s"
                               % (_ws(m.group(0)), _p18_kontakt_txt(t, z, evs), _de(ende_f),
                                  _p18_zeitraum_txt(*vorher_p[-1]) if vorher_p else "erst danach",
                                  "; wieder ab %s" % _de(spaeter[0]) if spaeter else ""))
    return _p18_melde(p, ort, satz, "Grenze", befunde)


def _p18_wechsel_daten(d, t, art, wert):
    """[(von, bis, angeschnitten)] der Zeichenaufenthalte (art 'z') bzw. Hausdurchgaenge
    (art 'h') des Laeufers t."""
    if art == "z":
        rows = [x for x in d["zeichen"] if kanon(x.get("transit", "")) == t and
                _zeichen_norm(x.get("zeichen", "")) == wert]
    else:
        rows = [x for x in d.get("haeuser_durch") or [] if kanon(x.get("transit", "")) == t
                and x.get("haus") == wert]
    return [(x.get("von"), x.get("bis"), bool(x.get("angeschnitten")) or x.get("von") == d["start"])
            for x in rows]


def _p18_wechsel(p, d, satz, ort):
    """„rückt/wechselt/tritt <Zeit> in den <Zeichen>/ins <n>. Haus“; „ab <Zeit> <T> in deinem
    <n>. Haus“ — der Eintritt liegt in der genannten Zeit, ohne Spielraum."""
    befunde = []
    for m in _P18_WECHSEL_RE.finditer(satz):
        a, e = _p18_teilsatz(satz, m.start())
        vor = satz[a:m.start()]
        nach = satz[m.end():e]
        # Gegenpruefung 2026-10-13: Der Laeufer steht im eigenen Satzteil des Verbs
        # („Während Jupiter noch im Krebs steht, wechselt der progressive Mond …“ ist
        # nicht Jupiter); progressive Faktoren und Sonnenbogen sind keine Transite.
        if re.search(r"progressiv\w*|Sonnenbogen", satz[max(a, m.start() - 40):m.end() + 40]):
            continue
        vor_eigen = vor[vor.rfind(",") + 1:]
        ls = [f for _x, _y, f, r in _p18_rollen(vor_eigen) if r == "L"][-1:]
        if not ls:
            erst = _p18_rollen(nach[:40])
            ls = [erst[0][2]] if erst and erst[0][3] == "L" else []
        if not ls:
            mrel = re.match(r"\s*(?:(?:Der|Die)\s+laufende\s+)?(?P<f>%s)\s*,\s*(?:der|die|das)\s" % _P18_T_NAME, vor)
            ls = [kanon(mrel.group("f"))] if mrel else []
        if not ls:
            continue
        t = ls[0]
        zt = [z for z in _p18_zeiten(nach) if not _P18_BIS_VOR_RE.search(nach[max(0, z[0] - 25):z[0]])]
        zt_vor = _p18_zeiten(vor)
        ziele = [("z", _zeichen_norm(x.group("z")), x.start()) for x in _P18_IN_ZEICHEN_RE.finditer(nach)]
        ziele += [("h", _p18_ord_wert(x.group("o")), x.start()) for x in _P18_IN_HAUS_RE.finditer(nach)]
        for art, wert, pos in ziele:
            # die letzte Zeit vor dem Ziel, sonst die vor dem Verb, sonst die erste danach
            # (Gegenpruefung 2026-10-13: „… im März in dein viertes und im Juli zurück in
            # dein drittes Haus“)
            zeit = [z for z in zt if z[0] < pos][-1:] or zt_vor[-1:] or [z for z in zt if z[0] > pos][:1]
            if not zeit:
                continue
            _a0, _e0, von, bis, roh = zeit[0]
            rows = _p18_wechsel_daten(d, t, art, wert)
            if not rows:
                continue
            if d["ende"] and von > d["ende"]:
                continue
            if d["start"] and bis < d["start"] and all(ang for _v, _b, ang in rows):
                continue                            # vor dem Fenster: dazu sagen die Daten nichts
            p.geprueft += 1
            if any(v and von <= v <= bis and not ang for v, _b, ang in rows):
                continue
            was = (_P18_ZEICHEN_ANZEIGE.get(wert, wert) if art == "z" else "Haus %d" % wert)
            wo = "Zeichenaufenthalt" if art == "z" else "Hausdurchgang"
            if all(ang for _v, _b, ang in rows):
                befunde.append("„%s … %s“ — %s steht schon ab Fensteranfang (%s) in %s (%s)"
                               % (roh, _ws(m.group(0)), ANZEIGE.get(t, t), _de(d["start"]), was, wo))
            else:
                befunde.append("„%s“ — %s in %s ab %s (%s)"
                               % (roh, ANZEIGE.get(t, t), was,
                                  ", ".join(_de(v) for v, _b, ang in rows if not ang), wo))
    # „ab <Zeit> <T> in deinem <n>.“ (auch ohne Verb: „…, ab Mitte März Saturn in deinem vierten“)
    for m in _P18_AB_RE.finditer(satz):
        zt = _p18_zeiten(satz[m.end():m.end() + 40])
        if not zt or zt[0][0] > 12:
            continue
        _a0, e0, von, bis, roh = zt[0]
        rest = satz[m.end() + e0:m.end() + e0 + 70]
        mh = re.match(r"\s*(?:(?:steht|stehen|läuft|laufen|ist|sind|wandert|geht|bleibt)\s+)?(?:(?:der\s+|die\s+)?"
                      r"(?P<t>Jupiter|Saturn|Uranus|Neptun|Pluto|Chiron|Mars|Mondknoten)\s+)?(?:(?:steht|läuft|"
                      r"ist|wandert|geht)\s+)?(?:in\s+deinem|im|durch\s+dein(?:en)?)\s+(?P<o>%s)"
                      r"(?:\s+Haus|(?=\s*(?:[,.;:!?)]|$|\s[—–]\s|\s+(?:und|oder)\s)))" % _P18_ORD_RE, rest)
        if not mh:
            continue
        a, _e = _p18_teilsatz(satz, m.start())
        t = kanon(mh.group("t")) if mh.group("t") else \
            ([f for _x, _y, f, r in _p18_rollen(satz[a:m.start()]) if r == "L"][-1:] or [None])[0]
        h = _p18_ord_wert(mh.group("o"))
        if not t or not h:
            continue
        rows = _p18_wechsel_daten(d, t, "h", h)
        if not rows:
            continue
        p.geprueft += 1
        if any(v and von <= v <= bis and not ang for v, _b, ang in rows):
            continue
        if all(ang for _v, _b, ang in rows) and von <= (d["start"] or ""):
            continue                                # beginnt vor dem Fenster: kein Widerspruch
        befunde.append("„ab %s“ — %s in Haus %d ab %s (Hausdurchgang)"
                       % (roh, ANZEIGE.get(t, t), h, ", ".join(_de(v) for v, _b, _ang in rows)))
    return _p18_melde(p, ort, satz, "Wechsel", befunde)


# Abstand: Zahl, Einheit, Richtung
_P18_ABSTAND_RE = re.compile(
    _P18_GRENZ + r"(?P<vor>etwa|rund|ungefähr|gut|knapp|nur|kaum)?\s*(?P<n>ein(?:en)?|eine|zwei|drei|vier|fünf|sechs|"
    r"sieben|acht|neun|zehn|elf|zwölf|dreizehn|vierzehn|\d{1,2})(?:\s+(?:oder|bis)\s+(?P<n2>zwei|drei|vier|fünf|"
    r"sechs|sieben|acht|neun|zehn|\d{1,2}))?\s+(?P<einheit>Tag(?:e|en)?|Woche(?:n)?)\s+(?P<richtung>nach|vor|"
    r"später|früher|danach|davor|darauf|vorher|neben)" + _P18_ENDE, re.I)
_P18_GEFOLGE_RE = re.compile(_P18_GRENZ + r"mit\s+(?:der|dem|deiner|deinem)?\s*(?P<f>%s)\s+(?:im\s+Gefolge|dicht\s+"
                             r"dahinter|knapp\s+dahinter|hinterher)" % _FAKTOR_RE + _P18_ENDE)
_P18_DAZWISCHEN_RE = re.compile(r"^\W*Dazwischen\s+(?!liegt\s+der\s+Normalfall)(?P<v>\w+)")
_P18_ERSTER_DURCHGANG_RE = re.compile(_P18_GRENZ + r"(?:nach|vor)\s+dem\s+(?P<o>ersten|zweiten|dritten|letzten)\s+"
                                      r"(?:genauen\s+)?(?:Durchgang|Mal)" + _P18_ENDE)
_P18_KONTAKT_ZU_RE = re.compile(_P18_GRENZ + r"(?:nach|vor|neben)\s+dem\s+(?:Kontakt|Quadrat|Trigon|Sextil|"
                                r"Quincunx|Durchgang|Übergang|Konjunktion|Opposition)\s+(?:zu|über|mit)\s+"
                                r"(?:dein(?:em|er|en)?\s+)?(?P<z>%s)" % _FAKTOR_RE + _P18_ENDE)
_P18_SONNENBOGEN_RE = re.compile(_P18_GRENZ + r"Sonnenbogen" + _P18_ENDE)


def _p18_zahl(w):
    w = (w or "").casefold()
    if w.isdigit():
        return int(w)
    return {"ein": 1, "einen": 1, "eine": 1}.get(w) or _zahl_wert(w)


def _p18_abstand_spanne(vor, n, n2, einheit):
    """(min, max) Tage nach Chris' Entscheidung d1 (Kopf dieses Abschnitts)."""
    vor = (vor or "").casefold()
    woche = einheit.casefold().startswith("woche")
    lo_n, hi_n = n, (n2 or n)
    if woche:
        lo, hi = 7 * lo_n - 1, 7 * hi_n + 1
        if vor == "gut":
            lo, hi = 7 * lo_n + 1, 7 * hi_n + 3
        elif vor in ("knapp", "kaum"):
            lo, hi = 7 * lo_n - 2, 7 * hi_n
        elif vor in ("etwa", "rund", "ungefähr"):
            lo, hi = 7 * lo_n - 2, 7 * hi_n + 2
    else:
        lo, hi = lo_n, hi_n
        if vor in ("etwa", "rund", "ungefähr"):
            lo, hi = max(0, lo_n - 1), hi_n + 1
        elif vor == "gut":
            hi = hi_n + 1
        elif vor in ("knapp", "kaum"):
            lo = max(0, lo_n - 1)
    return lo, hi


def _p18_exakte(d, t, z, klausel=None):
    evs = _p18_aspekt_filter(d["ev"].get((t, z), []), klausel) if klausel is not None else d["ev"].get((t, z), [])
    return _p18_exakt(evs), evs


def _p18_sonnenbogen_daten(d, satz):
    sb = ((d.get("zusatz") or {}).get("sonnenbogen") or [])
    fs = [f for _a, _e, f in _faktoren_im_satz(satz)]
    out = []
    for x in sb:
        pk, zk = kanon(x.get("punkt", "")), kanon(x.get("ziel", ""))
        if pk in fs and zk in fs and x.get("exakt"):
            out.append(x["exakt"])
    return sorted(set(out))


def _p18_in_zeiten(daten, zeiten):
    if not zeiten:
        return daten
    return [x for x in daten if any(v <= x <= b for _a, _e, v, b, _r in zeiten)]


def _p18_abstand(p, d, satz, ort, vorher, chapter_fuehrt, frueher=None):
    """Abstand und Reihenfolge zweier Ereignisse (Exaktdaten)."""
    befunde = []
    zeiten = _p18_zeiten_plus(satz)
    abst = list(_P18_ABSTAND_RE.finditer(satz))
    for i_m, m in enumerate(abst):
        n = _p18_zahl(m.group("n"))
        if not n:
            continue
        n2 = _p18_zahl(m.group("n2")) if m.group("n2") else None
        lo, hi = _p18_abstand_spanne(m.group("vor"), n, n2, m.group("einheit"))
        richtung = m.group("richtung").casefold()
        vorzeichen = 0 if richtung == "neben" else (-1 if richtung in ("vor", "früher", "davor", "vorher") else 1)
        a, e = _p18_teilsatz(satz, m.start())
        hinten = satz[m.end():m.end() + 80]
        # Bezug
        bezug, bez_txt = [], ""
        mk = _P18_KONTAKT_ZU_RE.match(satz[m.end() - len(m.group("richtung")):m.end() + 60])
        me = _P18_ERSTER_DURCHGANG_RE.match(satz[m.end() - len(m.group("richtung")):m.end() + 60])
        ls_satz = _p18_laeufer_plus(satz) or _p18_laeufer_plus(vorher)[-1:]
        if mk:
            zb = kanon(mk.group("z"))
            for t in ls_satz or ([chapter_fuehrt[0]] if chapter_fuehrt else []):
                ex, _evs = _p18_exakte(d, t, zb)
                if ex:
                    bezug, bez_txt = ex, "%s–%s" % (ANZEIGE.get(t, t), ANZEIGE.get(zb, zb))
                    break
        elif me and chapter_fuehrt:
            t, art, z = chapter_fuehrt
            ex = [x for x in _p18_exakt([x for x in d["ev"].get((t, z), []) if x.get("aspekt") == art])]
            ex_z = _p18_in_zeiten(ex, [zz for zz in zeiten if zz[0] < m.start()]) or ex
            o = me.group("o").casefold()
            idx = {"ersten": 0, "zweiten": 1, "dritten": 2, "letzten": -1}[o]
            if ex:
                try:
                    bezug, bez_txt = [ex_z[idx] if o != "letzten" else ex[-1]], "%s %s %s" % (
                        ANZEIGE.get(t, t), art, ANZEIGE.get(z, z))
                except IndexError:
                    bezug = []
        elif richtung in ("später", "früher", "danach", "darauf", "vorher", "davor"):
            # Gegenpruefung 2026-10-13: Bezug ist, was im SELBEN Satz davor steht
            # („… im Trigon zu deinem Mond und drei Tage danach im Quadrat …“); nur ohne
            # Ziel dort der Satz davor. Das Pronomen („er“) nimmt den letzten Laeufer.
            vorn = satz[:m.start()]
            ls_v = _p18_laeufer_plus(vorn) or _p18_laeufer_plus(vorher)[-1:]
            zs_v = _p18_ziele(vorn)
            if not zs_v:
                vorn, ls_v, zs_v = vorher, _p18_laeufer_plus(vorher), _p18_ziele(vorher)
            for t in ls_v:
                for z in zs_v:
                    ex, _evs = _p18_exakte(d, t, z, vorn)
                    bezug += ex
            bezug = sorted(set(bezug))
            bez_txt = "der Satzteil davor"
        if not bezug:
            continue
        # Gegenstand — bis zum naechsten Glied einer Aufzaehlung („zwei Tage später …,
        # knapp eine Woche später …“)
        ende_t = min(e, abst[i_m + 1].start()) if i_m + 1 < len(abst) else e
        teil = satz[m.end():ende_t] if richtung in ("später", "früher", "danach", "darauf", "vorher", "davor") \
            else satz
        gegen = []
        if _P18_SONNENBOGEN_RE.search(satz):
            gegen = _p18_sonnenbogen_daten(d, satz)
            geg_txt = "Sonnenbogen"
        else:
            ls = _p18_laeufer_plus(teil) or ls_satz
            zs = [z for z in _p18_ziele(teil) if not (mk and z == kanon(mk.group("z")))] or \
                 [z for z in _p18_ziele(satz) if not (mk and z == kanon(mk.group("z")))]
            for t in ls:
                for z in zs:
                    ex, _evs = _p18_exakte(d, t, z, teil)
                    gegen += ex
            geg_txt = "%s–%s" % ("/".join(ANZEIGE.get(t, t) for t in ls), "/".join(ANZEIGE.get(z, z) for z in zs))
        gegen = _p18_in_zeiten(sorted(set(gegen)), [zz for zz in zeiten if not (m.start() <= zz[0] <= m.end())])
        if not gegen:
            continue
        p.geprueft += 1
        falsch = []
        for g in gegen:
            # jeder Bezug im Umkreis zaehlt; gemeldet wird nur, wenn KEINER passt
            nah = sorted((r for r in bezug if abs(_tage(r, g)) <= 45), key=lambda r: abs(_tage(r, g)))
            if not nah:
                continue
            werte = [(abs(_tage(r, g)) if vorzeichen == 0 else _tage(r, g) * vorzeichen) for r in nah]
            if any(lo <= w <= hi for w in werte):
                continue
            r = nah[0]
            delta = _tage(r, g)
            falsch.append("%s: %s (Bezug %s: %s, %+d Tage)" % (geg_txt, _de(g), bez_txt, _de(r), delta))
        if falsch:
            befunde.append("„%s“ (%d–%d Tage %s) — %s" % (_ws(m.group(0)), lo, hi, richtung,
                                                        " · ".join(falsch[:4])))
    # „mit der Venus im Gefolge“: der Folgende liegt jedes Mal NACH dem Fuehrenden
    for m in _P18_GEFOLGE_RE.finditer(satz):
        fz = kanon(m.group("f"))
        ls = _p18_laeufer_plus(satz) or ([chapter_fuehrt[0]] if chapter_fuehrt else [])
        if not ls:
            continue
        t = ls[0]
        ex_f, _e1 = _p18_exakte(d, t, fz)
        # Gegenpruefung 2026-10-13: der Fuehrende ist der Kontakt, den der Satz davor
        # nennt („im Quadrat zu deinem Merkur, mit dem Mond im Gefolge“), erst ohne
        # ihn der fuehrende Kontakt des Kapitels
        vorn = satz[:m.start()]
        ziele_v = [z for z in _p18_ziele(vorn) if z != fz]
        if ziele_v:
            fz0 = ziele_v[-1]
            fuehr = _p18_exakte(d, t, fz0, vorn)[0]
        elif chapter_fuehrt and chapter_fuehrt[0] == t and chapter_fuehrt[2] != fz:
            fz0 = chapter_fuehrt[2]
            fuehr = _p18_exakt([x for x in d["ev"].get((t, chapter_fuehrt[2]), [])
                                if x.get("aspekt") == chapter_fuehrt[1]])
        else:
            continue
        fuehr = _p18_in_zeiten(fuehr, zeiten)
        if not ex_f or not fuehr:
            continue
        p.geprueft += 1
        falsch = []
        for r in fuehr:
            g = min(ex_f, key=lambda x: abs(_tage(r, x)))
            if abs(_tage(r, g)) <= 30 and _tage(r, g) <= 0:
                falsch.append("%s–%s %s vor %s–%s %s" % (ANZEIGE.get(t, t), ANZEIGE.get(fz, fz), _de(g),
                                                         ANZEIGE.get(t, t), ANZEIGE.get(fz0, fz0), _de(r)))
        if falsch:
            befunde.append("„%s“ — Reihenfolge: %s" % (_ws(m.group(0)), " · ".join(falsch[:3])))
    # „Dazwischen geht …“: die Exaktdaten liegen zwischen denen des Satzes davor
    md = _P18_DAZWISCHEN_RE.match(satz)
    if md and (vorher or frueher):
        bezug = []
        for s_ in ([vorher] if vorher else []) + list(reversed(frueher or [])):
            for t in _p18_laeufer_plus(s_):
                for z in _p18_ziele(s_):
                    ex, _evs = _p18_exakte(d, t, z, s_)
                    bezug += _p18_in_zeiten(ex, _p18_zeiten_plus(s_)) or ex
            if len(set(bezug)) >= 2:
                break
        gegen, perioden = [], []
        ls_d = _p18_laeufer_plus(satz) or _p18_laeufer_plus(vorher or "")[-1:]   # „Dazwischen steht er …“
        for t in ls_d:
            for z in _p18_ziele(satz):
                ex, evs = _p18_exakte(d, t, z, satz)
                gegen += _p18_in_zeiten(ex, zeiten) if zeiten else []
                perioden += _p18_perioden_gesamt(evs)
        kontakt = bool(ls_d and _p18_ziele(satz))
        if len(bezug) >= 2 and zeiten and not gegen and kontakt and \
                any(z[3] < min(bezug) or z[2] > max(bezug) for z in zeiten):
            p.geprueft += 1
            befunde.append("„Dazwischen“ — %s liegt nicht zwischen %s (Exaktdaten des Satzes davor)"
                           % (", ".join(z[4] for z in zeiten if z[3] < min(bezug) or z[2] > max(bezug)),
                              _p18_zeitraum_txt(min(bezug), max(bezug))))
        elif len(bezug) >= 2 and (gegen or (not zeiten and perioden)):
            p.geprueft += 1
            lo_b, hi_b = min(bezug), max(bezug)
            if zeiten:
                aussen = [g for g in gegen if not (lo_b <= g <= hi_b)]
                if aussen:
                    befunde.append("„Dazwischen“ — %s außerhalb %s (Exaktdaten des Satzes davor)"
                                   % (", ".join(_de(g) for g in sorted(aussen)), _p18_zeitraum_txt(lo_b, hi_b)))
            elif not any(x <= hi_b and y >= lo_b for x, y in perioden):
                # ohne Zeitangabe (Gegenpruefung 2026-10-13): irgendein Wirkorb dazwischen genuegt
                befunde.append("„Dazwischen“ — kein Wirkorb zwischen %s (Exaktdaten des Satzes davor); "
                               "Wirkorb %s" % (_p18_zeitraum_txt(lo_b, hi_b), ", ".join(
                                   _p18_zeitraum_txt(x, y) for x, y in perioden[:3])))
    return _p18_melde(p, ort, satz, "Abstand", befunde)


_P18_T_NAME = r"(?:Jupiter|Saturn|Uranus|Neptun|Pluto|Chiron|Mondknoten|Knoten)"
_P18_T_LISTE = (r"(?:(?:der|die)\s+(?:laufende\s+)?)?%s(?:\s*,\s*(?:(?:der|die)\s+(?:laufende\s+)?)?%s)*"
                r"(?:\s+und\s+(?:(?:der|die)\s+(?:laufende\s+)?)?%s)?" % (_P18_T_NAME, _P18_T_NAME, _P18_T_NAME))
_P18_BUENDEL_RE = re.compile(
    _P18_GRENZ + r"(?P<ls>%s)\s+(?:(?:steht|stehen|läuft|laufen)\s+)?"
    r"(?:(?P<a1>im\s+(?:Trigon|Quadrat|Sextil|Quincunx|Halbsextil))\s+(?:zu|zum|zur)|"
    r"(?P<a2>in\s+(?:Konjunktion|Opposition))\s+(?:zu|zum|zur|mit)|(?P<a3>gegenüber))\s+" % _P18_T_LISTE)
# 2026-10-13 (Gegenpruefung): die haeufigste Wortstellung, Ziele VOR „gegenüber“
_P18_BUENDEL_GEGEN_RE = re.compile(
    _P18_GRENZ + r"(?P<ls>%s)\s+(?:steht|stehen|stand|standen)\s+(?P<zs>(?:(?:dein\w*|der|dem|den)\s+)?"
    r"[\wäöüÄÖÜß-]+(?:\s*(?:,|und)\s*(?:(?:dein\w*|der|dem|den)\s+)?[\wäöüÄÖÜß-]+){1,5})\s+gegenüber"
    % _P18_T_LISTE + _P18_ENDE)
_P18_ZIELLISTE_ZW_RE = re.compile(r"^\s*(?:,|und|sowie)\s*(?:(?:zu|zum|zur|mit)\s+)?(?:(?:dein\w*|der|dem|den)\s+)?$")
_P18_ZIELLISTE_ANF_RE = re.compile(r"^\s*(?:(?:dein\w*|der|dem|den)\s+)?$")


def _p18_zielliste(text, ganz):
    """[(Schluessel, Ende)] der Zielaufzaehlung am Anfang von `text`: Faktoren, getrennt
    nur durch Komma/„und“ (mit Artikel oder „dein…“); sie endet am naechsten Laeufer mit
    eigenem Aspektbild („…, Uranus im Trigon …“) oder an allem anderen."""
    out, pos = [], 0
    for a_, e_, f in _faktoren_im_satz(text):
        zw = text[pos:a_]
        if not (_P18_ZIELLISTE_ANF_RE.match(zw) if not out else _P18_ZIELLISTE_ZW_RE.match(zw)):
            break
        if out and f in _P18_TRANSITER and (_P18_BILD_DANACH_RE.match(text[e_:e_ + 50]) or
                                            _P18_NEUE_GRUPPE_RE.match(text[e_:e_ + 40])):
            break                                   # „…, Uranus steht im Trigon …“: der naechste Laeufer
        out.append((f, e_))
        pos = e_
    return out


def _p18_buendel(p, d, text, ort, ist_signatur=False):
    """„A, B und C im Trigon zu X und Y“, „A und B stehen X und Y gegenüber“ — eine
    Aufzaehlung von Laeufern und eine von Zielen um EIN Aspektwort: Jedes Paar braucht
    den Kontakt dieser Art in der Rechnung (P13 laesst ein Buendel durch, sobald EIN
    Paar gedeckt ist). Gelesen werden nur diese festen Formen, mehrere je Satz; ein
    Paar, das als Radix-Aspekt dieser Art in den Tabellen steht, bleibt still (die
    Aussage kann das Geburtsbild meinen), ebenso der Suedknoten, wenn der
    Mondknoten-Kontakt besteht, und alles in Klammern. Der Kontakt zur Gegenachse
    (DC, IC) zaehlt mit seinem Spiegel-Eintrag (Gegenpruefung 2026-10-13)."""
    befunde = []
    if _P18_GEBURT_RE.search(text or ""):
        return 0
    rein = re.sub(r"\([^()]*\)", " ", text or "")
    buendel = []
    pos = 0
    while True:
        m = _P18_BUENDEL_RE.search(rein, pos)
        if not m:
            break
        zl = _p18_zielliste(rein[m.end():m.end() + 160], rein)
        wort = m.group("a1") or m.group("a2") or m.group("a3")
        buendel.append((m.group("ls"), wort, [f for f, _e in zl]))
        pos = m.end() + (zl[-1][1] if zl else 0)       # ein zweites Buendel im selben Satz
    for m in _P18_BUENDEL_GEGEN_RE.finditer(rein):
        fs = _faktoren_im_satz(m.group("zs"))
        teile = [t for t in re.split(r"\s*(?:,|\bund\b)\s*", m.group("zs")) if t.strip()]
        if len(fs) == len(teile):                   # jedes Glied ist ein Faktor
            buendel.append((m.group("ls"), "gegenüber", [f for _a, _e, f in fs]))
    for ls_txt, wort, zs in buendel:
        ls = [kanon(x) for x in re.findall(_P18_T_NAME, ls_txt)]
        if len(ls) < 2 and len(zs) < 2:
            continue
        art = "Opposition" if wort == "gegenüber" else _art(wort.split()[-1])
        geprueft = False
        for t in ls:
            for z in zs:
                if z == t:
                    continue
                if not any(k[0] == t for k in d["ev"]):
                    continue
                geprueft = True
                alle = d["ev"].get((t, z), []) + d.get("ev_spiegel", {}).get((t, z), [])
                if z == "SUEDKNOTEN" and d["ev"].get((t, "MONDKNOTEN")):
                    continue
                if any(x.get("aspekt") == art for x in alle):
                    continue
                if any(r["art"] == art and {r["a"], r["b"]} == {t, z} for r in d["tabelle"]):
                    continue
                andere = sorted({x.get("aspekt") for x in alle if x.get("aspekt")})
                befunde.append("%s %s %s: kein solcher Kontakt in der Rechnung%s"
                               % (ANZEIGE.get(t, t), art, ANZEIGE.get(z, z),
                                  " (nur %s)" % ", ".join(andere) if andere else ""))
        if geprueft:
            p.geprueft += 1
    return _p18_melde(p, ort, text, "Bündel", list(dict.fromkeys(befunde)))


_P18_GENAU_LISTE_RE = re.compile(_P18_GRENZ + r"(?:genau|exakt)\s+(?=(?:im\s+|am\s+|in\s+der\s+)?" + _P18_ZEIT_ALT +
                                 r"|(?:im\s+|in\s+der\s+)?(?:erst|zweit)en?\s+\w+hälfte)")
_P18_FOLGT_RE = re.compile(_P18_GRENZ + r"(?:folgt|folgen|folgte)" + _P18_ENDE)
_P18_GEHT_UEBER_RE = re.compile(_P18_GRENZ + r"(?:geht|gehen|läuft|laufen|zieht|ziehen)\s+(?:(?:der\s+|die\s+|das\s+)?"
                                r"(?P<t>%s)\s+)?(?P<zw>(?:(?:im|am|Anfang|Mitte|Ende)\s+(?:%s|Frühjahr|Sommer|Herbst|"
                                r"Winter)(?:\s+(?:19|20|21)\d\d)?\s+)?(?:(?:einmal|zweimal|dreimal|mehrmals|noch\s+einmal|"
                                r"erneut|wieder)\s+)?)über\s+(?:dein(?:en|e|em)?|den|die|das)\s+(?P<z>%s)"
                                % (_FAKTOR_RE, _MONAT_RE, _FAKTOR_RE) + _P18_ENDE)


def _p18_genau(p, d, satz, ort, kapitel_kontakte):
    """„genau Anfang März 2031, Ende Juli 2031 und Mitte November 2031“: jede Zeit
    traegt ein Exaktdatum des Kontakts; „folgt <Zeit>“ ebenso; „geht im <Zeit> über
    deinen X“: ein Nulldurchgang in der Zeit."""
    befunde = []
    for m in list(_P18_GENAU_LISTE_RE.finditer(satz)) + list(_P18_FOLGT_RE.finditer(satz)):
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        if _P18_STILL_RE.search(klausel):
            continue                                # Station: eigene Satzart
        if m.re is _P18_FOLGT_RE and not _P18_GENAU_RE.search(satz):
            continue                                # „folgt“ ohne „genau“ im Satz kann den Beginn meinen (2026-10-13)
        hinten = satz[m.end():e]
        zeiten = [z for z in _p18_zeiten_plus(hinten) if z[0] <= 70]
        if m.re is _P18_FOLGT_RE:
            zeiten = [z for z in _p18_zeiten_plus(klausel, satz)]
        if not zeiten:
            continue
        ls_k = _p18_laeufer_plus(klausel)
        ls = ls_k or _p18_laeufer_plus(satz[:a])[-1:]
        zs = _p18_ziele(klausel)
        mp = re.search(_P18_GRENZ + r"mit\s+(?:seinen|ihren)\s+(?:eigenen\s+)?(?P<art>Quadrat|Trigon|Sextil|Quincunx|"
                       r"Opposition|Konjunktion)(?:e|en)?" + _P18_ENDE, klausel)
        alle_eigenen = bool(ls_k and mp)
        if not zs and ls:
            zs = [z for (tt, art_, z, _f) in kapitel_kontakte if tt in ls and (not mp or art_ == mp.group("art"))]
        if not ls or not zs:
            continue
        ex_alle = []
        for t in ls:
            for z in zs:
                if mp:
                    ex = _p18_exakt([x for x in d["ev"].get((t, z), []) if x.get("aspekt") == mp.group("art")])
                else:
                    ex, _evs = _p18_exakte(d, t, z, klausel if _p18_aspektarten(klausel) else None)
                ex_alle += [(x, t, z) for x in ex]
        if not ex_alle:
            continue
        p.geprueft += 1
        for _a0, _e0, von, bis, roh in zeiten:
            if d["start"] and bis < (d.get("lookback") or d["start"]):
                continue
            if not any(von <= x <= bis for x, _t, _z in ex_alle):
                nah = min(ex_alle, key=lambda q: min(abs(_tage(von, q[0])), abs(_tage(bis, q[0]))))
                befunde.append("„%s“ — kein Exaktdatum in %s; nächstes: %s–%s %s"
                               % (roh, _p18_zeitraum_txt(von, bis), ANZEIGE.get(nah[1], nah[1]),
                                  ANZEIGE.get(nah[2], nah[2]), _de(nah[0])))
        if m.re is _P18_FOLGT_RE and (_p18_ziele(klausel) or alle_eigenen):
            aussen = [(x, t, z) for x, t, z in ex_alle
                      if any(abs(_tage(von, x)) <= 31 for _a0, _e0, von, _b, _r in zeiten)
                      and not any(von <= x <= bis for _a0, _e0, von, bis, _r in zeiten)]
            if aussen:
                befunde.append("„%s“ — %s" % (_ws(m.group(0)), " · ".join(
                    "%s–%s exakt %s" % (ANZEIGE.get(t, t), ANZEIGE.get(z, z), _de(x)) for x, t, z in aussen[:3])))
    for m in _P18_GEHT_UEBER_RE.finditer(satz):
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        vor_z = [z for z in _p18_zeiten(satz[a:m.start()])]
        nach_z = [z for z in _p18_zeiten(satz[m.end():m.end() + 30]) if z[0] <= 12]
        zw_z = _p18_zeiten(m.group("zw") or "")
        zeiten = zw_z[:1] or vor_z[-1:] or nach_z[:1]
        if not zeiten:
            continue
        t = kanon(m.group("t")) if m.group("t") else \
            ([f for _x, _y, f, r in _p18_rollen(satz[a:m.start()]) if r == "L"][-1:] or
             [f for _x, _y, f, r in _p18_rollen(satz[m.end():e]) if r == "L"][:1] or [None])[0]
        z = kanon(m.group("z"))
        if not t or t == z:
            continue
        evs = [x for x in d["ev"].get((t, z), []) if x.get("aspekt") == "Konjunktion"]
        if not evs:
            continue
        ex = _p18_exakt(evs)
        p.geprueft += 1
        for _a0, _e0, von, bis, roh in zeiten:
            if not any(von <= x <= bis for x in ex):
                ann = [aa for x in evs for aa in (x.get("annaeherung") or [])]
                befunde.append("„über“ (%s) — %s Konjunktion %s: kein Nulldurchgang in %s%s%s"
                               % (roh, ANZEIGE.get(t, t), ANZEIGE.get(z, z), _p18_zeitraum_txt(von, bis),
                                  "; Annäherung bis %s° am %s" % (str(round(ann[0][1], 2)).replace(".", ","),
                                                                  _de(ann[0][0])) if ann else "",
                                  "; exakt %s" % ", ".join(_de(x) for x in ex[:3]) if ex else "; nie exakt"))
    return _p18_melde(p, ort, satz, "Genau", befunde)


_P18_KAPITEL_VERB_RE = re.compile(_P18_GRENZ + r"(?:laufen|läuft|stehen|steht|liegen|liegt|überlagern|überlagert|"
                                  r"überschneiden|überschneidet|kreuzen|gehören|gehört|teilen|teilt|drängen|"
                                  r"nebeneinander|gleichzeitig|zugleich|parallel)" + _P18_ENDE)
_P18_KAPITEL_LAUF_RE = re.compile(
    _P18_GRENZ + r"(?:(?:läuft|laufen|kommt|kommen|tritt|treten|steht|stehen)\s+(?:auch\s+|zugleich\s+|parallel\s+|"
    r"noch\s+|schon\s+|bereits\s+|dann\s+|wieder\s+)*(?:das\s+|die\s+)?Kapitel(?:s|n)?\s+\d{1,2}|"
    r"(?:brauchen|braucht|gehören|gehört)\s+(?:\w+\s+){0,5}?(?:das\s+|die\s+)?Kapitel(?:s|n)?\s+\d{1,2}|"
    r"Kapitel(?:s|n)?\s+\d{1,2}(?:\s*(?:,|und|oder)\s*(?:Kapitel\s+)?\d{1,2})*\s+(?:läuft|laufen|kommt|kommen|"
    r"tritt|treten|steht|stehen|ist|sind|liegt|liegen)\s+(?:auch\s+|zugleich\s+|parallel\s+|mit|dicht|im\s+"
    r"Vordergrund|dazu))" + _P18_ENDE)
_P18_N_KAPITEL_RE = re.compile(_P18_GRENZ + r"(?P<n>zwei|drei|vier|fünf|sechs|sieben|acht|\d)\s+(?:der\s+)?"
                               r"(?:Kapitel|Kapiteln|Themen)" + _P18_ENDE)
_P18_DIESE_ZEIT_RE = re.compile(_P18_GRENZ + r"(?:diese[n]?\s+(?:Monate|Wochen|Zeit|Jahre)|in\s+dieser\s+Zeit|"
                                r"in\s+diesen\s+(?:Monaten|Wochen|Jahren))" + _P18_ENDE)
_P18_AUFTAKT_RE = re.compile(_P18_GRENZ + r"(?:Auftakt|Beginn|Start)\s+(?:von\s+|des\s+)?Kapitel(?:s)?\s+"
                             r"(?P<n>\d{1,2})" + _P18_ENDE)


def _p18_zl_quartale(d, von, bis):
    """Die Quartalsnummern der Zeitleiste, die [von, bis] beruehren."""
    qb = list(d.get("quartal_grenzen") or [])
    if len(qb) > 1 and d["ende"] and qb[-1] > d["ende"]:
        qb = qb[:-1]                                # die letzte Grenze schliesst das Fenster
    out = []
    for i, a in enumerate(qb):
        b = qb[i + 1] if i + 1 < len(qb) else _p18_plus(d["ende"] or "9999-12-30", 1)
        if a <= bis and b > von:
            out.append(i + 1)
    return out


def _p18_kapitelzeit(p, d, satz, ort, eigenes):
    """Kapitel in einer Zeit — gegen die `@@ZEITLEISTE` (dicht=) und die Wirkorb-Zeiten
    der THEMA-Kontakte."""
    befunde = []
    dicht = d.get("dicht") or {}
    if not dicht:
        return 0
    zeiten = _p18_zeiten(satz)
    # (a) „<n> Kapitel“ in einer Zeit
    for m in _P18_N_KAPITEL_RE.finditer(satz):
        n = _p18_zahl(m.group("n"))
        a, e = _p18_teilsatz(satz, m.start())
        zt = _p18_zeiten(satz[a:e]) or zeiten
        if not n or not zt or re.match(r"\s*(?:davon|von\s+ihnen)", satz[m.end():m.end() + 12]):
            continue
        # Gegenpruefung 2026-10-13: „zwei der sechs Kapitel“, „die nächsten drei Kapitel
        # erzählen …“ — gezaehlt wird nur „<n> Kapitel laufen/stehen/…“ in einer Zeit
        if re.search(r"(?:der|die|den|nächsten|folgenden|ersten|letzten|beiden|übrigen|anderen|vorigen)\s+$",
                     satz[max(0, m.start() - 15):m.start()]):
            continue
        if not _P18_KAPITEL_VERB_RE.search(satz):
            continue
        qs = sorted({q for z in zt for q in _p18_zl_quartale(d, z[2], z[3])})
        if not qs:
            continue
        kap = sorted({k for q in qs for k in dicht.get(q, ())})
        p.geprueft += 1
        if len(kap) != n:
            befunde.append("„%s“ (%s) — dicht in Q%s: Kapitel %s (%d)"
                           % (_ws(m.group(0)), ", ".join(z[4] for z in zt), "–Q".join(map(str, (qs[0], qs[-1])))
                              if len(qs) > 1 else qs[0], ", ".join(map(str, kap)), len(kap)))
    # (b) „Kapitel n“ in einer Zeit oder in „diesen Monaten“
    for m in _P18_KAPITEL_LISTE_RE.finditer(satz):
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        if not _P18_KAPITEL_LAUF_RE.search(satz[max(a, m.start() - 40):min(e, m.end() + 40)]):
            continue                                # Verweis, keine Aussage über die Zeit (2026-10-13)
        nrs = [int(x) for x in re.findall(r"\d{1,2}", m.group(0))]
        zt = _p18_zeiten(klausel)
        if zt:
            qs = sorted({q for z in zt for q in _p18_zl_quartale(d, z[2], z[3])})
            woher = ", ".join(z[4] for z in zt)
        elif _P18_DIESE_ZEIT_RE.search(klausel) and eigenes and eigenes in d.get("kap_dicht", {}):
            qs = sorted(d["kap_dicht"][eigenes])
            woher = "Kapitel %d (Q%s)" % (eigenes, ",".join(map(str, qs)))
        else:
            continue
        if not qs:
            continue
        for n in nrs:
            if n == eigenes or n not in d.get("kap_dicht", {}):
                continue
            p.geprueft += 1
            if not set(d["kap_dicht"][n]) & set(qs):
                befunde.append("Kapitel %d in %s — dicht nur in Q%s"
                               % (n, woher, ",".join(map(str, sorted(d["kap_dicht"][n])))))
    # (c) „Auftakt von Kapitel n“
    for m in _P18_AUFTAKT_RE.finditer(satz):
        n = int(m.group("n"))
        th = d["thema"].get(d["kap2thema"](n))
        if not th:
            continue
        a_, _e = _p18_teilsatz(satz, m.start())
        zt = _p18_zeiten(satz[a_:m.start()]) or _p18_zeiten(satz[:m.start()])
        if not zt:
            continue                                # ohne eigene Zeitangabe keine Aussage (2026-10-13)
        von = zt[-1][2]
        fruehe = []
        for (t, art, z, feld) in th["kontakte"]:
            if feld not in ("fuehrt", "aspekte"):
                continue
            ps = _p18_perioden([x for x in d["ev"].get((t, z), []) if x.get("aspekt") == art])
            if ps:
                fruehe.append((ps[0][0], t, art, z))
        if not fruehe:
            continue
        p.geprueft += 1
        x, t, art, z = min(fruehe)
        if x < _p18_plus(von, -31):
            befunde.append("„%s“ (%s) — Kapitel %d läuft schon: %s %s %s im Wirkorb ab %s"
                           % (_ws(m.group(0)), zt[-1][4], n, ANZEIGE.get(t, t), art, ANZEIGE.get(z, z), _de(x)))
    return _p18_melde(p, ort, satz, "Kapitelzeit", befunde)


_P18_DAUER_RE = re.compile(_P18_GRENZ + r"(?P<q>fast\s+(?:die\s+)?ganze[n]?|die\s+ganze[n]?|das\s+ganze|den\s+größten\s+Teil"
                           r"(?:\s+der|\s+des)?)\s+(?:zwei\s+Jahre|Fenster\w*|Jahre|Zeit)" + _P18_ENDE)


def _p18_dauer(p, d, satz, ort):
    befunde = []
    if not d["start"] or not d["ende"]:
        return 0
    gesamt = _tage(d["start"], d["ende"]) + 1
    for m in _P18_DAUER_RE.finditer(satz):
        a, e = _p18_teilsatz(satz, m.start())
        klausel = satz[a:e]
        ls = _p18_laeufer_plus(klausel)
        # Gegenpruefung 2026-10-13: ALLE genannten Häuser bzw. Zeichen zusammen („die
        # ganzen zwei Jahre im dritten und dann im vierten Haus“)
        hs = [_p18_ord_wert(x.group("o")) for x in _P18_HAUS_ORD_RE.finditer(klausel)]
        zs = [_zeichen_norm(x.group("z")) for x in re.finditer(
            _P18_GRENZ + r"(?:im|in\s+der|in\s+den)\s+(?P<z>%s)" % ZEICHEN_RE + _P18_ENDE, klausel)]
        if not ls or not (hs or zs):
            continue
        t = ls[0]
        rows = [r for h in hs for r in _p18_wechsel_daten(d, t, "h", h)] if hs else \
            [r for z in zs for r in _p18_wechsel_daten(d, t, "z", z)]
        if not rows:
            continue
        tage = sum(max(0, _tage(max(v, d["start"]), min(b, d["ende"])) + 1) for v, b, _ang in rows if v and b)
        anteil = min(1.0, tage / float(gesamt))
        q = m.group("q").lower()
        soll = P18_FAST_GANZ if q.startswith("fast") else (P18_GROESSTER_TEIL if "größten" in q else P18_GANZ)
        p.geprueft += 1
        if (q.startswith("fast") and not (P18_FAST_GANZ <= anteil < 1.0 + 1e-9)) or \
                (not q.startswith("fast") and anteil < soll):
            befunde.append("„%s“ — %s in %s: %d von %d Tagen des Fensters (%d %%)"
                           % (_ws(m.group(0)), ANZEIGE.get(t, t),
                              (" und ".join("Haus %d" % h for h in hs)) if hs else
                              " und ".join(_P18_ZEICHEN_ANZEIGE.get(z, z) for z in zs),
                              tage, gesamt, round(100 * anteil)))
    return _p18_melde(p, ort, satz, "Dauer", befunde)


_P18_DIESELBEN_RE = re.compile(r"^\W*(?:In\s+(?:die|den)selben\s+(?:Wochen|Monate|Monaten|Tage|Tagen)|"
                               r"Zur\s+selben\s+Zeit)" + _P18_ENDE)
_P18_KOPULA_ZUGLEICH_RE = re.compile(_P18_GRENZ + r"(?:ist|sind|war|waren|bleibt|bleiben|wird|werden)\s+"
                                     r"zugleich\s+(?:ein|eine|einer|der|die|das|dein\w*|auch|selbst)" + _P18_ENDE)


def _p18_dieselben(p, d, satz, ort, frueher, kapitel_kontakte):
    """„In dieselben Wochen fallen …“ — die Kontakte des Satzes ueberlappen die
    Wirkorb-Zeit der Kontakte des naechsten Satzes davor, der welche nennt; „… und
    zugleich im Trigon zu deinem X“ mit EINEM Laeufer — gegen dessen uebrige Ziele im
    Kapitel."""
    befunde = []
    md = _P18_DIESELBEN_RE.search(satz)
    if md and not _P18_GEBURT_RE.search(satz):
        gegen = _p18_kontakte_von(d, _p18_laeufer_plus(satz), _p18_ziele(satz), satz)
        bezug = []
        for s in reversed(frueher or []):
            bezug = _p18_kontakte_von(d, _p18_laeufer_plus(s), _p18_ziele(s), s)
            if bezug:
                break
        if gegen and bezug:
            ref = _p18_perioden_gesamt([x for _t, _z, evs in bezug for x in evs])
            # nur die Strecken nahe beieinander (ein Kontakt kehrt Jahre spaeter wieder)
            p.geprueft += 1
            def luecke(x, y, rx, ry):                # Tage zwischen zwei Strecken, 0 bei Ueberlappung
                return max(0, _tage(ry, x), _tage(y, rx))
            for t, z, evs in gegen:
                ps = _p18_perioden_gesamt(evs)
                nah = [(x, y) for x, y in ps if any(luecke(x, y, rx, ry) <= 120 for rx, ry in ref)]
                if nah and not any(luecke(x, y, rx, ry) == 0 for x, y in nah for rx, ry in ref):
                    befunde.append("„%s“ — %s: Wirkorb %s, der Satz davor (%s): %s"
                                   % (_ws(md.group(0)), _p18_kontakt_txt(t, z, evs),
                                      ", ".join(_p18_zeitraum_txt(x, y) for x, y in nah[:2]),
                                      _p18_namen(list(dict.fromkeys(q[0] for q in bezug))),
                                      ", ".join(_p18_zeitraum_txt(rx, ry) for rx, ry in ref
                                                if any(luecke(x, y, rx, ry) <= 120 for x, y in nah))[:120]))
    mz = re.search(_P18_GRENZ + r"(?:zugleich|gleichzeitig)" + _P18_ENDE, satz)
    if mz and not _P18_GEBURT_RE.search(satz) and not _P18_KOPULA_ZUGLEICH_RE.search(satz):
        laeufer = _p18_laeufer_plus(satz[:mz.start()])
        if len(laeufer) == 1 and len(_p18_laeufer_plus(satz)) == 1:
            t = laeufer[0]
            nach = satz[mz.end():]
            zs = _p18_ziele(nach)
            if re.search(_P18_GRENZ + r"(?:zurückkehrt|zurückkehren|Rückkehr|kehrt\s+\w+\s+zurück|an\s+seinen\s+eigenen"
                         r"\s+Platz|an\s+seine\s+eigene\s+Stelle)", satz[:mz.start()]) and (t, t) in d["ev"]:
                andere = [(t, "Konjunktion")]       # „… zurückkehrt und zugleich …“: die Rueckkehr
            else:
                andere = [(z, art) for (tt, art, z, _f) in kapitel_kontakte if tt == t and z not in zs]
                andere += [(z, None) for z in _p18_ziele(satz[:mz.start()]) if z not in zs]
            kont = _p18_kontakte_von(d, [t], zs, nach)
            if kont and andere:
                ref = []
                for z, art in andere:
                    ref += [q for q in d["ev"].get((t, z), []) if art is None or q.get("aspekt") == art]
                rp = _p18_perioden_gesamt(ref)
                if rp:
                    p.geprueft += 1
                    ueber = [k for k in kont if any(x <= ry and y >= rx for x, y in _p18_perioden_gesamt(k[2])
                                                    for rx, ry in rp)]
                    if not ueber:
                        tt, z, evs = kont[0]
                        befunde.append("„%s“ — %s und %s an %s: kein gemeinsamer Tag im Wirkorb"
                                       % (_ws(mz.group(0)), _p18_kontakt_txt(tt, z, evs), ANZEIGE.get(t, t),
                                          _p18_namen(list(dict.fromkeys(z_ for z_, _a in andere)))))
    return _p18_melde(p, ort, satz, "Zugleich", befunde)


# --- P18: Zusammenbau -----------------------------------------------------------

# ---------------------------------------------------------------------------
# P18 Naehe, Lage und Rang im Geburtshoroskop (2026-10-13, Strang 2 des Wartungslaufs
# „Proben fuer Zeit, Naehe, Register und Fundstellen“). In den Geburtshoroskopen vom 10.
# bis 12.10. ersetzten die Zweitleser je Lauf mehrere Saetze, deren Lage-, Naehe- oder
# Rangwort mehr sagte als die Daten; keine Probe sah sie.
#
# Chris-Entscheidung 2026-10-13 (Fragenblock des Wartungslaufs, Fragen a1–a4: „ja“):
# a1  „genau am/auf“, „exakt“, „gradgenau“, „auf den Grad“, „am selben Punkt wie“, „zu
#     einem Punkt“ tragen hoechstens 1° Orb (P18_NAEHE_ORB); „genau dort, wo … sich
#     berühren“ hoechstens 1° Abstand zur Hausspitze. „fast/nahezu genau“ ist frei.
# a2  „eng/dicht beieinander“ verlangt eine Konjunktion zwischen JEDEM Paar der genannten
#     Faktoren; „mitten in der Ballung“ trifft kein Randglied — das erste oder letzte
#     Glied nach der Laenge in JEDEM Stellium aus §6, das den Faktor enthaelt.
# a3  Absolutformeln („so eng, wie es überhaupt vorkommen kann“, „enger geht es
#     nicht“) bekommen immer einen Hinweis mit Orb und Rang; „kaum enger“ nur, wenn der
#     Orb ueber 1° liegt oder das Paar nicht auf Rang 1 der Rangzeile steht.
# a4  „deines ganzen Bildes“, „alle Faktoren gezählt“, „unter allen gerechneten …“
#     zaehlen JEDEN gerechneten Untergrund-Aspekt mit, auch ungedeutete; ohne diesen
#     Zusatz zaehlt der Rang ohne Untergrund (Rangzeile §10, P12) — die Regel vom
#     04.10., die neben „die engste Verbindung“ den gedeuteten Untergrund mitzaehlte,
#     entfaellt. Nennt der Satz den Untergrund, ist er ausgenommen.
# Dazu zwei Lagewoerter, die die Daten nur auf eine Weise tragen: Die leere Haelfte und
# der leere Bogen „liegen“ nicht in einem Zeichen oder Haus — dort liegt nur ihre Mitte
# (Strukturbild §8); einer Achse steht kein Faktor „gegenüber“, er steht einem Ende
# gegenueber. Wie ueberall in P18: nur PRUEFEN, nur bei Widerspruch, mit dem Datenwert;
# was sich nicht lesen laesst (kein Paar, kein Stellium), bleibt still. Nicht im Transit
# und nicht im Kapitel „Die Zeit“ einer Vertiefung — dort heisst „genau“ das Exaktdatum.
# ---------------------------------------------------------------------------
P18_NAEHE_ORB = 60                       # a1: hoechstens 1° — in Bogenminuten
_P18_Z12 = ("WIDDER", "STIER", "ZWILLINGE", "KREBS", "LOEWE", "JUNGFRAU", "WAAGE", "SKORPION",
            "SCHUETZE", "STEINBOCK", "WASSERMANN", "FISCHE")


def _p18_laengen(txt):
    """{Faktor: Laenge in Grad} aus der Staendetabelle (Grad und Zeichen)."""
    out = {}
    for f, (mi, z) in (_staende_lesen(txt or "") or {}).items():
        if z in _P18_Z12:
            out[f] = _P18_Z12.index(z) * 30 + mi / 60.0
    return out


def _p18_spitzen(txt):
    """Die zwoelf Hausspitzen in Grad — eine Tabelle „## … Hausspitzen …“ („| 1 | 7°54′ Löwe |“
    oder „| 1 (AC) | 16°35′ | Waage | … |“), sonst die Liste `cusps = [...]` des Rechenblocks;
    None, wenn keins von beiden vollstaendig lesbar ist."""
    sp = {}
    m = re.search(r"\n## [^\n]*Hausspitzen[^\n]*\n(.*?)(?=\n## |\Z)", txt or "", re.S)
    if m:
        for mm in re.finditer(r"^\|\s*(\d{1,2})(?:\s*\([^)|]*\))?\s*\|\s*(\d{1,2})°\s*(\d{1,2})[′']\s*\|?\s*(%s)"
                              % ZEICHEN_RE, m.group(1), re.M):
            z, h = _zeichen_norm(mm.group(4)), int(mm.group(1))
            if z in _P18_Z12 and 1 <= h <= 12:
                sp[h] = _P18_Z12.index(z) * 30 + int(mm.group(2)) + int(mm.group(3)) / 60.0
    if sorted(sp) == list(range(1, 13)):
        return [sp[h] for h in range(1, 13)]
    mc = re.search(r"(?<![\w])cusps\s*=\s*\[([^\]]*)\]", txt or "", re.I)
    if mc:
        try:
            ws = [float(x) % 360.0 for x in mc.group(1).split(",") if x.strip()]
        except ValueError:
            ws = []
        if len(ws) == 12:
            return ws
    return None


def _p18_bogen(a, b):
    """Kleinster Abstand zweier Laengen in Grad."""
    x = abs(a - b) % 360.0
    return min(x, 360.0 - x)


def _p18_grad_txt(grad):
    """Bogen in Grad als „4°14′“."""
    mi = int(round(grad * 60))
    return "%d°%02d′" % (mi // 60, mi % 60)


def _p18_lage_txt(lon):
    """„9°41′ Krebs“ aus einer Laenge in Grad."""
    mi = int(round((lon % 360.0) * 60)) % (360 * 60)
    z, rest = divmod(mi, 1800)
    return "%d°%02d′ %s" % (rest // 60, rest % 60, _P18_ZEICHEN_ANZEIGE.get(_P18_Z12[z], _P18_Z12[z]))


def _p18_haus_von(lon, spitzen):
    for h in range(12):
        a, b = spitzen[h], spitzen[(h + 1) % 12]
        if (lon - a) % 360.0 < (b - a) % 360.0:
            return h + 1
    return None


def _p18_stellien(txt):
    """[(Name, [Faktoren])] aus Strukturbild §6 („- Stellium in Krebs: Mars, Merkur, …“);
    ein Zusatz hinter dem Gedankenstrich („— dieselbe Gruppe wie …“) gehoert nicht dazu."""
    out = []
    for m in re.finditer(r"^- Stellium in ([^:\n]+):\s*([^\n]*)$", txt or "", re.M):
        glieder = re.split(r"\s+[—–]\s+", m.group(2), maxsplit=1)[0]
        fs = [kanon(x.strip()) for x in glieder.split(",") if x.strip()]
        out.append((m.group(1).strip(), [f for f in fs if f]))
    return out


def _p18_reihe(lons):
    """Glieder einer Gruppe nach der Laenge, geschnitten an der groessten Luecke — eine
    Gruppe ueber 0° Widder bleibt zusammen. lons: [(Laenge, Faktor)] -> [Faktor]."""
    xs = sorted(lons)
    n = len(xs)
    if n < 2:
        return [f for _l, f in xs]
    _g, i = max(((xs[(j + 1) % n][0] - xs[j][0]) % 360.0, j) for j in range(n))
    return [xs[(i + 1 + j) % n][1] for j in range(n)]


def _p18_rang_eintrag(d, z, schl):
    """(Eintraege der Rangzeile, Eintrag der Tabellenzeile oder None)."""
    roh = [e for e in d["rangzeilen"].get(schl, {}).get("eintraege", []) if "rang" in e]
    paar = frozenset((_achs_norm(z["a"]), _achs_norm(z["b"])))
    return roh, next((x for x in roh if _rang_paar(x) == paar and x["orb_min"] == z["orb"]), None)


def _p18_rangtext(d, z, schl="engste-aspekte"):
    """Rang einer Tabellenzeile, wie ihn die Rangzeile §10 druckt — als Text fuer den Hinweis."""
    if z["stufe"] == "untergrund":
        return "Untergrund (ohne Rang in der Rangzeile)"
    roh, e = _p18_rang_eintrag(d, z, schl)
    if not roh:
        return "ohne Rangzeile %s" % schl
    if not e:
        return "nicht unter den ersten %d Rängen der Rangzeile %s" % (max(x["rang"] for x in roh), schl)
    gleich = [x for x in _rang_einmal(roh) if x["orb_min"] == e["orb_min"] and _rang_paar(x) != _rang_paar(e)]
    return "Rang %d der Rangzeile %s%s" % (e["rang"], schl, (" (gleichauf: %s)" % "; ".join(
        _rang_txt(x).split(". ", 1)[1] for x in gleich)) if gleich else "")


def _p18_rang_nr(d, z, schl="engste-aspekte"):
    """Rang der Zeile, wie ihn die Rangzeile §10 druckt; None ohne Eintrag."""
    _roh, e = _p18_rang_eintrag(d, z, schl)
    return e["rang"] if e else None


def _p18_zeile_txt(z):
    return "%s %s %s %s" % (ANZEIGE.get(z["a"], z["a"]), z["art"], ANZEIGE.get(z["b"], z["b"]), z["orb_txt"])


def _p18_formel_zeilen(d, satz, vorher, pos):
    """Die Tabellenzeilen, denen eine Formel an `pos` gilt: Art aus dem Text kurz davor
    (Name oder Bild), beide Faktoren im Satz — sonst einer im Satz, einer im Satz davor,
    sonst beide im Satz davor, sonst einer im Satz; das Paar mit dem Faktor naechst vor der
    Formel zuerst. Achsen-Spiegelzeilen zaehlen mit („gegenüber dem IC“ = Opposition IC)."""
    arten = _p18_aspektarten(satz[max(0, pos - 90):pos])
    fs = _p18_faktoren(satz)
    im = {f for _a, _e, f in fs}
    davor = {f for _a, _e, f in _p18_faktoren(vorher or "")}
    zeilen = [z for z in d["tabelle"] if not arten or z["art"] in arten]
    kand = [z for z in zeilen if z["a"] in im and z["b"] in im]
    if not kand:
        kand = [z for z in zeilen if (z["a"] in im and z["b"] in davor) or (z["b"] in im and z["a"] in davor)]
    if not kand and not im:
        kand = [z for z in zeilen if z["a"] in davor and z["b"] in davor]
    if not kand and arten:
        kand = [z for z in zeilen if z["a"] in im or z["b"] in im]

    def naehe(z):
        ps = [a for a, _e, f in fs if f in (z["a"], z["b"]) and a < pos]
        return -(max(ps) if ps else -10 ** 6)
    return sorted(kand, key=lambda z: (naehe(z), z["spiegel"], z["orb"]))


def _p18_rang_schl(satz):
    return "engste-aspekte-planeten" if _P12_PLANETENMENGE_RE.search(satz) else "engste-aspekte"


# --- Absolutformeln (a3) ------------------------------------------------------------
_P18_ABSOLUT_RE = re.compile(
    _P18_GRENZ + r"(?:wie\s+es\s+(?:[\wäöüß]+\s+){0,6}?überhaupt\s+(?:vorkommt|vorkommen\s+kann|möglich\s+ist|"
    r"geht|gibt|sein\s+kann)"
    r"|so\s+eng\s*,?\s+wie\s+(?:es\s+)?(?:nur\s+)?(?:irgend\s+)?(?:möglich|denkbar)"
    r"|enger\s+(?:geht|ginge)\s+es\s+(?:gar\s+|überhaupt\s+)?nicht"
    r"|(?:enger|genauer)\s+(?:kann|könnte)\s+(?:eine\s+Verbindung|ein\s+Aspekt|ein\s+Winkel|es|sie|er)\s+"
    r"(?:gar\s+|überhaupt\s+)?nicht\s+(?:sein|werden|stehen|ausfallen)"
    r"|wie\s+es\s+(?:enger|genauer)\s+nicht\s+(?:geht|sein\s+kann))" + _P18_ENDE, re.I)
_P18_SO_ENG_RE = re.compile(_P18_GRENZ + r"(?:so|ebenso)\s+(?:eng|genau|exakt|dicht|nah)" + _P18_ENDE, re.I)
_P18_KAUM_ENGER_RE = re.compile(
    _P18_GRENZ + r"(?:kaum\s+enger\s+(?:sein\s+)?(?:kann|könnte|ginge|geht|wäre)"
    r"|enger\s+(?:geht|ginge)\s+es\s+kaum"
    r"|(?:enger|genauer)\s+(?:kann|könnte)\s+(?:eine\s+Verbindung|ein\s+Aspekt|es|sie|er)\s+kaum\s+"
    r"(?:sein|stehen|ausfallen))" + _P18_ENDE, re.I)


def _p18_absolut(p, d, satz, vorher, ort):
    n = 0
    schl = _p18_rang_schl(satz)
    for m in _P18_ABSOLUT_RE.finditer(satz):
        w = m.group(0).casefold()
        if w.startswith("wie") and "überhaupt" in w and \
                not _P18_SO_ENG_RE.search(satz[max(0, m.start() - 120):m.start()]):
            continue
        # „so eng wie möglich“ nur, wenn davor eine Aspektart steht — sonst eine Anleitung
        if w.startswith("so") and not _p18_aspektarten(satz[max(0, m.start() - 90):m.start()]):
            continue
        p.geprueft += 1
        zs = _p18_formel_zeilen(d, satz, vorher, m.start())
        wert = ("%s, %s" % (_p18_zeile_txt(zs[0]), _p18_rangtext(d, zs[0], schl)) if zs else
                "kein Paar im Satz lesbar; Rangzeile %s, Rang 1: %s" % (schl, "; ".join(
                    _rang_txt(e) for e in d["rangzeilen"].get(schl, {}).get("eintraege", [])
                    if "rang" in e and e["rang"] == 1) or "—"))
        p.pruefen.append("%s: „%s“ — Absolutformel: „%s“ sagt mehr, als ein Orb tragen kann — %s; "
                         "Orb oder Rang nennen" % (ort, _kurz(satz, 140), m.group(0), wert))
        n += 1
    for m in _P18_KAUM_ENGER_RE.finditer(satz):
        zs = _p18_formel_zeilen(d, satz, vorher, m.start())
        if not zs:
            continue
        p.geprueft += 1
        # die guenstigste Lesart: traegt EIN Paar des Satzes die Formel, bleibt es still
        if any(z["orb"] <= P18_NAEHE_ORB and _p18_rang_nr(d, z, schl) == 1 for z in zs):
            continue
        z = zs[0]
        p.pruefen.append("%s: „%s“ — Absolutformel: „%s“ — %s, %s (trägt die Formel nur bis 1° und auf "
                         "Rang 1)" % (ort, _kurz(satz, 140), m.group(0), _p18_zeile_txt(z),
                                      _p18_rangtext(d, z, schl)))
        n += 1
    return n


# --- Rang mit dem ganzen Untergrund (a4) und strenge Rangwoerter ----------------------
_P18_ALLE_GEZAEHLT_RE = re.compile(
    _P18_GRENZ + r"(?:(?:dein(?:es|em)?|des|im)\s+ganzen\s+(?:Bild(?:es|s)?|Horoskops?|Geburtsbild(?:es|s)?)"
    r"|alle[n]?\s+(?:Faktoren|Punkte|Verbindungen|Aspekte)\s+(?:gezählt|mitgezählt|mitgerechnet)"
    r"|unter\s+allen\s+(?:gerechneten|berechneten)|alle\s+(?:gerechneten|berechneten))" + _P18_ENDE, re.I)
_P18_STRIKT_RE = re.compile(
    _P18_GRENZ + r"(?:enger\s+als\s+(?:jede|jeder|jedes|alle)\s+(?:andere[nrs]?\s+)?"
    r"(?:Verbindung|Aspekt|Kontakt|Paar|Winkel)\w*"
    r"|so\s+(?:eng|genau|dicht)\s*,?\s+wie\s+(?:es\s+)?(?:[\wäöüß]+\s+){0,8}?(?:sonst\s+nirgends|nirgends\s+sonst"
    r"|sonst\s+nirgendwo)"
    r"|(?:sonst\s+nirgends|nirgends\s+sonst)\s+(?:[\wäöüß]+\s+){0,4}?so\s+(?:eng|genau|dicht)"
    r"|keine\s+(?:andere\s+|weitere\s+)?(?:(?:Verbindung|davon)\s+)?(?:[\wäöüß]+\s+){0,3}?(?:ist\s+)?so\s+eng\s+wie"
    r"|kein\s+(?:anderer\s+|weiterer\s+)?(?:Aspekt|Kontakt|Winkel)\s+(?:[\wäöüß]+\s+){0,3}?(?:ist\s+)?"
    r"so\s+eng\s+wie)" + _P18_ENDE, re.I)
_P18_RANG_KONTEXT_RE = re.compile(_P18_GRENZ + r"(?:Verbindung|Aspekt|Kontakt|Winkel)\w*" + _P18_ENDE)
_P18_HART = ("Quadrat", "Opposition", "Halbquadrat", "Anderthalbquadrat")


def _p18_rang_filter(nachtext):
    """Einschraenkungen aus den Woertern hinter einem Rangwort bis zum Gliedende (wie P12):
    Aspektart, harmonisch, Spannung, Achse/Winkel, voll -> [Pruefung(art, a, b, stufe)]."""
    glied = re.split(r"[,;:.!?]|\s[—–]\s", nachtext or "", maxsplit=1)[0]
    worte = re.findall(r"[\wäöüÄÖÜß-]+", glied)[:8]
    arten = {_art(w) for w in worte if w in _ASP_WORT}
    out = []
    if arten:
        out.append(lambda art, a, b, st: art in arten)
    if any(w.lower().startswith("harmonisch") for w in worte):
        out.append(lambda art, a, b, st: art in ("Trigon", "Sextil"))
    if any(re.match(r"(?:Winkel-)?(?:Spannung|Reibung)|spannungsvoll", w, re.I) for w in worte):
        out.append(lambda art, a, b, st: art in _P18_HART)
    if any(re.fullmatch(r"(?:Achse|Achsen|Winkel|Winkeln)", w, re.I) for w in worte):
        out.append(lambda art, a, b, st: a in ACHSEN or b in ACHSEN)
    if any(w.lower() in ("voll", "volle", "vollen", "voller", "volles", "vollem") for w in worte):
        out.append(lambda art, a, b, st: st == "voll")
    return out


def _p18_rang_basis(d, satz, vorher, filt=()):
    """(Rangzeilen-Schluessel, Liste, Untergrund-Zeilen nach a4, Eintrag des Paars oder None,
    Paare). Untergrund: mit „deines ganzen Bildes“ u. a. JEDER gerechnete (auch ungedeutet),
    sonst keiner; nennt der Satz den Untergrund, keiner. filt: _p18_rang_filter()."""
    planeten = bool(_P12_PLANETENMENGE_RE.search(satz))
    schl = _p18_rang_schl(satz)
    ls = _rang_einmal([e for e in d["rangzeilen"].get(schl, {}).get("eintraege", []) if "rang" in e
                       and all(f(e["aspekt"], kanon(e["a"]), kanon(e["b"]), e.get("staerke")) for f in filt)])
    ganz = bool(_P18_ALLE_GEZAEHLT_RE.search(satz)) and not re.search(r"Untergrund", satz, re.I)
    ug = [z for z in d["tabelle"] if ganz and z["stufe"] == "untergrund" and
          (not planeten or (z["a"] in _P18_PLANETEN and z["b"] in _P18_PLANETEN))
          and all(f(z["art"], z["a"], z["b"], "untergrund") for f in filt)]
    fak = [f for _a, _e, f in _faktoren_im_satz(satz)]
    paare = _paare_von(fak) or _paare_von(fak + [f for _a, _e, f in _faktoren_im_satz(vorher or "")])
    treffer = [e for e in ls if _rang_paar(e) in paare]
    e = min(treffer, key=lambda x: x["orb_min"]) if treffer else None
    return schl, ls, ug, e, paare


def _p18_teilmenge(satz, m):
    """Rang innerhalb einer Gruppe („innerhalb dieser Ballung“, „unter ihren Gliedern“) — P12."""
    k0 = satz.rfind(";", 0, m.start()) + 1
    k1 = satz.find(";", m.end())
    return bool(_P12_TEILMENGE_RE.search(satz[k0:] if k1 < 0 else satz[k0:k1]))


def _p18_rang_ganz(p, d, satz, vorher, ort):
    """a4: „die (zweit)engste … deines ganzen Bildes“ — der Rang mit JEDEM gerechneten
    Untergrund-Aspekt. Nur, wenn die Rangzeile die Aussage traegt (sonst meldet P12)."""
    if not d["rangzeilen"] or not _P18_ALLE_GEZAEHLT_RE.search(satz) or re.search(r"Untergrund", satz, re.I):
        return 0
    n = 0
    for m in _RANG_MUSTER[0][1].finditer(satz):
        if _p18_teilmenge(satz, m):
            continue
        g = m.groupdict()
        nw = g.get("n") or g.get("n2")
        grenze = (2 if nw.lower() == "beiden" else _zahl_wert(nw)) if nw else None
        eine = bool(g.get("eine")) or bool(g.get("n2"))
        k = {"zweit": 2, "dritt": 3, "viert": 4}.get((g.get("ord") or "").lower(), 1)
        schl, ls, ug, e, _paare = _p18_rang_basis(d, satz, vorher, _p18_rang_filter(satz[m.end():]))
        if not e:
            continue                                     # P12 meldet
        r = 1 + sum(1 for x in ls if x["orb_min"] < e["orb_min"])
        gleich_basis = [x for x in ls if x["orb_min"] == e["orb_min"] and x is not e]
        if (eine and grenze is not None and r > grenze) or (not eine and (r != k or gleich_basis)):
            continue                                     # P12 meldet
        p.geprueft += 1
        enger = [z for z in ug if z["orb"] < e["orb_min"]]
        gleich = [z for z in ug if z["orb"] == e["orb_min"]]
        r_ganz = r + len(enger)
        if (eine and (grenze is None or r_ganz <= grenze)) or (not eine and r_ganz == k and not gleich):
            continue
        p.pruefen.append("%s: „%s“ — Rang: „%s“ zählt jeden gerechneten Untergrund-Aspekt mit — %s; "
                         "damit steht %s %s %s %s auf Rang %d%s (die Rangzeile %s zählt den Untergrund "
                         "nicht)" % (ort, _kurz(satz, 140), _P18_ALLE_GEZAEHLT_RE.search(satz).group(0),
                                     "; ".join(_p18_zeile_txt(z) for z in enger + gleich), e["a"], e["aspekt"],
                                     e["b"], e["orb"], e["rang"] + len(enger),
                                     " (gleichauf)" if gleich and not enger else "", schl))
        n += 1
    return n


def _p18_rang_strikt(p, d, satz, vorher, ort):
    """„enger als jede andere Verbindung“, „so eng, wie es … sonst nirgends vorkommt“,
    „keine so eng wie diese“ — Rang 1 ohne Gleichstand; den Untergrund nach a4; die
    Einschraenkungen hinter dem Wort („… zu einer deiner Achsen“) und ein Rang innerhalb
    einer Gruppe wie bei P12."""
    if not d["rangzeilen"]:
        return 0
    n = 0
    for m in _P18_STRIKT_RE.finditer(satz):
        if m.group(0).casefold().startswith("kein") and not _P18_RANG_KONTEXT_RE.search(satz):
            continue
        if _p18_teilmenge(satz, m):
            continue
        schl, ls, ug, e, paare = _p18_rang_basis(d, satz, vorher, _p18_rang_filter(satz[m.end():]))
        if not ls or not paare:
            continue
        if not e:
            # das Paar steht in der Aspekttabelle, aber unter keinem der genannten Raenge
            roh = [x for x in d["rangzeilen"].get(schl, {}).get("eintraege", []) if "rang" in x]
            zs = [z for z in d["tabelle"] if not z["spiegel"] and z["stufe"] != "untergrund"
                  and frozenset((_achs_norm(z["a"]), _achs_norm(z["b"]))) in paare]
            if not zs or not roh:
                continue
            p.geprueft += 1
            p.pruefen.append("%s: „%s“ — Rang: „%s“ — %s steht nicht unter den ersten %d Rängen der "
                             "Rangzeile %s (Rang 1: %s)"
                             % (ort, _kurz(satz, 140), m.group(0), _p18_zeile_txt(min(zs, key=lambda z: z["orb"])),
                                max(x["rang"] for x in roh), schl,
                                "; ".join(_rang_txt(x) for x in roh if x["rang"] == 1) or "—"))
            n += 1
            continue
        p.geprueft += 1
        vor = [x for x in ls if x["orb_min"] < e["orb_min"]]
        gl = [x for x in ls if x["orb_min"] == e["orb_min"] and x is not e]
        ug_vor = [z for z in ug if z["orb"] <= e["orb_min"]]
        if not vor and not gl and not ug_vor:
            continue
        teile = []
        if vor or gl:
            teile.append("Rangzeile %s: %s" % (schl, "; ".join(_rang_txt(x) for x in (vor + gl)[:3])))
        if ug_vor:
            teile.append("mit dem Untergrund („%s“): %s" % (_P18_ALLE_GEZAEHLT_RE.search(satz).group(0),
                                                            "; ".join(_p18_zeile_txt(z) for z in ug_vor)))
        p.pruefen.append("%s: „%s“ — Rang: „%s“ verlangt Rang 1 ohne Gleichstand — %s %s %s %s; %s"
                         % (ort, _kurz(satz, 140), m.group(0), e["a"], e["aspekt"], e["b"], e["orb"],
                            " · ".join(teile)))
        n += 1
    return n


# --- Subjekt einer Lagewendung ----------------------------------------------------------
_P18_KOORD_RE = re.compile(r"\s*(?:,|und|sowie)\s*(?:(?:dein\w*|der|die|das|den|dem)\s+)?", re.I)
_P18_EINSCHUB_RE = re.compile(r",\s*(?:wie|weil|da|wenn|als|obwohl|während|was|der|die|das|dem|den|deren|dessen)"
                              r"(?![\wäöüß])[^,]*,", re.I)
_P18_PRONOMEN_ANF_RE = re.compile(r"^\W*(?:und\s+)?(?:er|sie|es)(?![\wäöüß])", re.I)
_P18_LAGEVERB_RE = re.compile(_P18_GRENZ + r"(?:steht|stehen|stand|standen|sitzt|sitzen|saß|saßen|liegt|liegen|"
                              r"lag|lagen|befindet|befinden|thront|thronen|ruht|ruhen)" + _P18_ENDE, re.I)


def _p18_ohne_einschub(text):
    """Einschuebe „, wie …,“ / „, der …,“ durch Leerzeichen ersetzt (Positionen bleiben)."""
    return _P18_EINSCHUB_RE.sub(lambda mm: " " * len(mm.group(0)), text or "")


def _p18_subjekte(satz, a, pos, ende, vorher, ohne=()):
    """Die Faktoren, denen eine Wendung an `pos` gilt: die Gruppe direkt davor im Teilsatz
    [a, pos) — durch „und“/Komma verbunden, ein Einschub („, wie …,“, „, der …,“) zaehlt
    nicht; sonst der erste Faktor dahinter im Teilsatz [pos, ende); sonst, bei einem Pronomen
    am Teilsatzanfang, der letzte Faktor des Satzes davor. [] heisst: nicht sicher lesbar."""
    vor_text = _p18_ohne_einschub(satz[a:pos])
    fs = [(x, e, f) for x, e, f in _p18_faktoren(vor_text) if f not in ohne]
    if fs:
        gruppe = [fs[-1]]
        for vorig in reversed(fs[:-1]):
            if _P18_KOORD_RE.fullmatch(vor_text[vorig[1]:gruppe[0][0]]):
                gruppe.insert(0, vorig)
            else:
                break
        return list(dict.fromkeys(f for _x, _e, f in gruppe))
    nach = [f for _x, _e, f in _p18_faktoren(satz[pos:ende]) if f not in ohne]
    if nach:
        return [nach[0]]
    if _P18_PRONOMEN_ANF_RE.match(satz[a:pos]):
        fv = [f for _x, _e, f in _p18_faktoren(vorher or "") if f not in ohne]
        if fv:
            return [fv[-1]]
    return []


# --- Naehe bis 1° (a1) ---------------------------------------------------------------
_P18_GENAU_WORT = r"(?:genau|exakt|punktgenau|gradgenau|auf\s+den\s+Grad(?:\s+genau)?)"
_P18_ARTIKEL = r"(?:(?:dem|deinem|deiner|deinen|der|den|die|das|dein|deine)\s+)?"
_P18_UNGEFAEHR_RE = re.compile(r"(?:fast|nahezu|beinahe|ziemlich|annähernd|ungefähr|nicht|nicht\s+ganz|"
                               r"so\s+gut\s+wie)\s+$", re.I)
_P18_NAH_KONJ_RE = re.compile(
    _P18_GRENZ + r"(?:" + _P18_GENAU_WORT + r"\s+(?:am|an|auf)\s+"
    r"|(?:am|an)\s+(?:selben|demselben|gleichen)\s+(?:Punkt|Grad|Fleck)\s+wie\s+"
    r"|an\s+(?:derselben|der\s+gleichen|der\s+selben)\s+Stelle\s+wie\s+)" + _P18_ARTIKEL, re.I)
_P18_NAH_ASPEKT_RE = re.compile(
    _P18_GRENZ + _P18_GENAU_WORT + r"\s+(?:im|in\s+(?:einem|einer|der))\s+(?P<art>Konjunktion|Opposition|"
    r"Quadrat|Trigon|Sextil|Quincunx|Halbsextil|Halbquadrat|Anderthalbquadrat)" + _P18_ENDE, re.I)
_P18_NAH_GEGEN_RE = re.compile(_P18_GRENZ + _P18_GENAU_WORT + r"\s+gegenüber(?:steht|stehen|stand|standen|liegt|"
                               r"liegen)?" + _P18_ENDE, re.I)
_P18_NAH_PUNKT_RE = re.compile(_P18_GRENZ + r"(?:verschmilzt|verschmelzen|verschmolzen|verschmolz)\s+"
                               r"(?:[\wäöüß]+\s+){0,4}?zu\s+einem\s+(?:einzigen\s+)?Punkt" + _P18_ENDE, re.I)
_P18_NAH_SPITZE_RE = re.compile(
    _P18_GRENZ + r"(?:(?:genau|exakt)\s+(?:dort|da|an\s+der\s+Stelle)\s*,?\s+wo\s+(?:sich\s+)?"
    r"(?:(?:diese|die|zwei|beide)\s+)?(?:beiden\s+|zwei\s+)?(?:Bereiche|Häuser|Felder|Lebensbereiche|Räume)"
    r"(?:\s+(?:von|des|der)\s+[\wäöüß]+(?:\s+und\s+(?:von\s+|des\s+|der\s+)?[\wäöüß]+)?)?\s+"
    r"(?:sich\s+)?(?:berühren|aneinandergrenzen|aneinanderstoßen|treffen|begegnen|überlappen)"
    r"|(?:genau|exakt)\s+auf\s+der\s+(?:Hausspitze|(?:Grenze|Schwelle|Spitze)(?=\s+(?:[\wäöüß]+\s+){0,4}?"
    r"(?:Haus|Hauses|Häuser|Häusern)(?![\wäöüß]))))" + _P18_ENDE, re.I)
_P18_ZIELLISTE_NAH_RE = re.compile(r"\s*(?:,|und|sowie)\s*(?:(?:zu|zum|zur|mit)\s+)?" + _P18_ARTIKEL + r"$", re.I)


def _p18_ungefaehr(satz, pos):
    return bool(_P18_UNGEFAEHR_RE.search(satz[max(0, pos - 25):pos]))


def _p18_ziel_nach(satz, pos, weit=4, mit_ende=False):
    """Faktor, der an `pos` beginnt (hoechstens `weit` Zeichen Luft); mit_ende: (Faktor, Ende)."""
    for a, e, f in _p18_faktoren(satz):
        if pos <= a <= pos + weit:
            return (f, e) if mit_ende else f
    return (None, pos) if mit_ende else None


def _p18_nah_zielliste(satz, pos):
    """[(Faktor, Ende)] ab `pos`: das erste Ziel und die mit „und“/Komma angereihten."""
    ziel, ende = _p18_ziel_nach(satz, pos, mit_ende=True)
    if not ziel:
        return []
    out = [(ziel, ende)]
    for a, e, f in _p18_faktoren(satz):
        if a < ende:
            continue
        if _P18_ZIELLISTE_NAH_RE.match(satz[out[-1][1]:a]):
            out.append((f, e))
        else:
            break
    return out


def _p18_zeilen_paar(d, art, x, y):
    return [z for z in d["tabelle"] if z["art"] == art and {z["a"], z["b"]} == {x, y}]


def _p18_nah_zeilen(d, art, ziel, satz, vorher):
    """Zeilen der Art `art` zwischen dem Ziel und einem anderen Faktor des Satzes (sonst
    des Satzes davor); ohne Ziel: zwischen zwei Faktoren des Satzes (sonst einer davor)."""
    im = [f for _a, _e, f in _p18_faktoren(satz)]
    davor = [f for _a, _e, f in _p18_faktoren(vorher or "")]
    zeilen = [z for z in d["tabelle"] if z["art"] == art]
    if ziel:
        for menge in (im, davor):
            ks = [z for z in zeilen if (z["a"] == ziel and z["b"] in menge and z["b"] != ziel)
                  or (z["b"] == ziel and z["a"] in menge and z["a"] != ziel)]
            if ks:
                return ks
        return []
    ks = [z for z in zeilen if z["a"] in im and z["b"] in im]
    if not ks:
        ks = [z for z in zeilen if (z["a"] in im and z["b"] in davor) or (z["b"] in im and z["a"] in davor)]
    return ks


def _p18_nah_melde(p, ort, satz, wort, ks):
    """Lesart „irgendein Paar“: still, wenn EINE Zeile die Wendung traegt."""
    p.geprueft += 1
    if not ks or any(z["orb"] <= P18_NAEHE_ORB for z in ks):
        return 0
    p.pruefen.append("%s: „%s“ — Nähe: „%s“ trägt höchstens 1° — %s"
                     % (ort, _kurz(satz, 140), wort.strip(), "; ".join(_p18_zeile_txt(z) for z in ks)))
    return 1


def _p18_nah_je_subjekt(p, d, ort, satz, wort, art, subjekte, ziele, abstand=False):
    """Lesart „jedes genannte Paar“: Subjekte und Ziele sind sicher gelesen, also traegt JEDES
    Paar die Wendung. Ohne Zeile der Art: mit abstand=True (Konjunktion) der Laengenabstand,
    sonst still (P13 haelt erfundene Aspekte)."""
    p.geprueft += 1
    weit = []
    for s in subjekte:
        for t in ziele:
            if s == t:
                continue
            ks = _p18_zeilen_paar(d, art, s, t)
            if ks:
                if all(z["orb"] > P18_NAEHE_ORB for z in ks):
                    weit.append("; ".join(_p18_zeile_txt(z) for z in ks))
            elif abstand and s in d["lon"] and t in d["lon"] and \
                    _p18_bogen(d["lon"][s], d["lon"][t]) * 60 > P18_NAEHE_ORB:
                weit.append("keine Konjunktion %s–%s (Abstand %s)" % (
                    ANZEIGE.get(s, s), ANZEIGE.get(t, t), _p18_grad_txt(_p18_bogen(d["lon"][s], d["lon"][t]))))
    if not weit:
        return 0
    p.pruefen.append("%s: „%s“ — Nähe: „%s“ trägt höchstens 1° — %s"
                     % (ort, _kurz(satz, 140), wort.strip(), "; ".join(weit)))
    return 1


def _p18_naehe_orb(p, d, satz, vorher, ort):
    n = 0
    for m in _P18_NAH_KONJ_RE.finditer(satz):
        if _p18_ungefaehr(satz, m.start()):
            continue
        ziel, z_ende = _p18_ziel_nach(satz, m.end(), mit_ende=True)
        if not ziel:
            continue
        a, b = _p18_teilsatz(satz, m.start())
        # eine Lage, kein Hinsehen: „steht/sitzt/liegt“ im Satz davor oder im Teilsatz, oder
        # die Wendung als Einschub direkt hinter dem Faktor („Neptun — genau an deinem Saturn —“)
        if not (_P18_LAGEVERB_RE.search(satz[:m.start()]) or _P18_LAGEVERB_RE.search(satz[m.start():b])
                or any(re.fullmatch(r"\s*[—–,]\s*", satz[e_:m.start()]) for _a, e_, _f in _p18_faktoren(satz[:m.start()]))):
            continue
        wort = satz[m.start():z_ende]
        subj = _p18_subjekte(satz, a, m.start(), b, vorher, ohne={ziel})
        if subj:
            n += _p18_nah_je_subjekt(p, d, ort, satz, wort, "Konjunktion", subj, [ziel], abstand=True)
        else:
            ks = _p18_nah_zeilen(d, "Konjunktion", ziel, satz, vorher)
            if ks:
                n += _p18_nah_melde(p, ort, satz, wort, ks)
    for m in _P18_NAH_ASPEKT_RE.finditer(satz):
        if _p18_ungefaehr(satz, m.start()):
            continue
        art = m.group("art").capitalize()
        a, b = _p18_teilsatz(satz, m.start())
        mz = re.match(r"\s+(?:zu|mit)\s+" + _P18_ARTIKEL, satz[m.end():], re.I)
        ziele = [f for f, _e in _p18_nah_zielliste(satz, m.end() + mz.end())] if mz else []
        subj = _p18_subjekte(satz, a, m.start(), b, vorher, ohne=set(ziele)) if ziele else []
        if ziele and subj:
            n += _p18_nah_je_subjekt(p, d, ort, satz, m.group(0), art, subj, ziele)
        else:
            ks = _p18_nah_zeilen(d, art, ziele[0] if ziele else None, satz, vorher)
            if ks:
                n += _p18_nah_melde(p, ort, satz, m.group(0), ks)
    for m in _P18_NAH_GEGEN_RE.finditer(satz):
        if _p18_ungefaehr(satz, m.start()):
            continue
        a, _b = _p18_teilsatz(satz, m.start())
        vor = list(dict.fromkeys(f for _x, _e, f in _p18_faktoren(satz[a:m.start()])))
        if len(vor) >= 2:
            ks = [z for z in d["tabelle"] if z["art"] == "Opposition" and z["a"] in vor and z["b"] in vor]
            if ks:
                p.geprueft += 1
                weit = [z for z in ks if z["orb"] > P18_NAEHE_ORB]
                if weit:
                    p.pruefen.append("%s: „%s“ — Nähe: „%s“ trägt höchstens 1° — %s"
                                     % (ort, _kurz(satz, 140), m.group(0), "; ".join(_p18_zeile_txt(z) for z in weit)))
                    n += 1
                continue
        ks = _p18_nah_zeilen(d, "Opposition", None, satz, vorher)
        if ks:
            n += _p18_nah_melde(p, ort, satz, m.group(0), ks)
    for m in _P18_NAH_PUNKT_RE.finditer(satz):
        a, b = _p18_teilsatz(satz, m.start())
        im_teil = list(dict.fromkeys(f for _x, _e, f in _p18_faktoren(satz[a:b])))
        if len(im_teil) >= 2:
            ks = [z for z in d["tabelle"] if z["art"] == "Konjunktion" and z["a"] in im_teil and z["b"] in im_teil]
            if ks:
                p.geprueft += 1
                weit = [z for z in ks if z["orb"] > P18_NAEHE_ORB]
                if weit:
                    p.pruefen.append("%s: „%s“ — Nähe: „%s“ trägt höchstens 1° — %s"
                                     % (ort, _kurz(satz, 140), m.group(0), "; ".join(_p18_zeile_txt(z) for z in weit)))
                    n += 1
                continue
        ks = _p18_nah_zeilen(d, "Konjunktion", None, satz, vorher)
        if ks:
            n += _p18_nah_melde(p, ort, satz, m.group(0), ks)
    if d.get("spitzen"):
        for m in _P18_NAH_SPITZE_RE.finditer(satz):
            a, b = _p18_teilsatz(satz, m.start())
            subj = [f for f in _p18_subjekte(satz, a, m.start(), b, vorher) if f in d["lon"]]
            if not subj:
                continue
            p.geprueft += 1
            weit = []
            for f in subj:
                ab, h = min((_p18_bogen(d["lon"][f], s), i + 1) for i, s in enumerate(d["spitzen"]))
                if ab * 60 > P18_NAEHE_ORB + 0.5:
                    weit.append("%s %s, nächste Hausspitze %d (%s), Abstand %s"
                                % (ANZEIGE.get(f, f), _p18_lage_txt(d["lon"][f]), h,
                                   _p18_lage_txt(d["spitzen"][h - 1]), _p18_grad_txt(ab)))
            if weit:
                p.pruefen.append("%s: „%s“ — Nähe: „%s“ trägt höchstens 1° bis zur Hausspitze — %s"
                                 % (ort, _kurz(satz, 140), m.group(0), "; ".join(weit)))
                n += 1
    return n


# --- Beieinander und Ballung (a2) ----------------------------------------------------
_P18_BEIEINANDER_RE = re.compile(_P18_GRENZ + r"(?:eng|dicht)\s+beieinander\w*" + _P18_ENDE, re.I)
_P18_MITTEN_RE = re.compile(
    _P18_GRENZ + r"mitten\s+(?:in|innerhalb)\s+(?:(?P<nomen>(?:der|einer|dieser|deiner|seiner|ihrer|dem|einem|"
    r"diesem)\s+(?:[\wäöüß-]+\s+){0,2}?(?P<w>Ballung|Stellium|Gruppe|Häufung|Ansammlung)\w*)"
    r"|(?P<pron>ihr|ihm|ihnen))" + _P18_ENDE, re.I)


def _p18_konj(d, x, y):
    return any(z["art"] == "Konjunktion" and {z["a"], z["b"]} == {x, y} for z in d["tabelle"])


def _p18_beieinander(p, d, satz, ort):
    n = 0
    for m in _P18_BEIEINANDER_RE.finditer(satz):
        a, b = _p18_teilsatz(satz, m.start())
        fs = []
        for teil in (_p18_ohne_einschub(satz[a:m.start()]), _p18_ohne_einschub(satz[:m.start()]),
                     satz[m.end():b]):
            fs = list(dict.fromkeys(f for _x, _e, f in _p18_faktoren(teil)))
            if len(fs) >= 2:
                break
        if len(fs) < 2:
            continue
        p.geprueft += 1
        fehlt = []
        for i, x in enumerate(fs):
            for y in fs[i + 1:]:
                if not _p18_konj(d, x, y):
                    ab = (" (Abstand %s)" % _p18_grad_txt(_p18_bogen(d["lon"][x], d["lon"][y]))
                          if x in d["lon"] and y in d["lon"] else "")
                    fehlt.append("%s–%s%s" % (ANZEIGE.get(x, x), ANZEIGE.get(y, y), ab))
        if fehlt:
            p.pruefen.append("%s: „%s“ — Beieinander: „%s“ verlangt eine Konjunktion je Paar — keine "
                             "Konjunktion: %s" % (ort, _kurz(satz, 140), m.group(0), "; ".join(fehlt)))
            n += 1
    return n


def _p18_stellium_genannt(d, st, text):
    """Die Stellien aus `st`, die der Text nennt (Zeichen oder Hausnummer); [] ohne Nennung."""
    zs = {_zeichen_norm(mz.group("z")) for mz in _P18_ZEICHEN_IM_RE.finditer(text or "")}
    hs = set()
    for _a, _e, h in _p18_haeuser_in(text or ""):
        hs |= set(h)
    out = []
    for name, gl in st:
        mh = re.fullmatch(r"Haus\s+(\d{1,2})", name)
        if (mh and int(mh.group(1)) in hs) or (not mh and _zeichen_norm(name) in zs):
            out.append((name, gl))
    return out


def _p18_ballung(p, d, satz, vorher, ort):
    n = 0
    for m in _P18_MITTEN_RE.finditer(satz):
        umfeld = satz[:m.start()] + " " + (vorher or "")
        if m.group("pron") and not re.search(r"Ballung|Stellium", umfeld):
            continue
        # „mitten in einer Gruppe (von Menschen)“ ist keine Ballung — nur mit Ballung/Stellium davor
        if m.group("w") and m.group("w").casefold() not in ("ballung", "stellium") and \
                not re.search(r"Ballung|Stellium", umfeld):
            continue
        a, b = _p18_teilsatz(satz, m.start())
        for f in _p18_subjekte(satz, a, m.start(), b, vorher):
            st = [(name, gl) for name, gl in d["stellien"] if f in gl]
            st = _p18_stellium_genannt(d, st, satz[m.end():b]) or st
            if not st or not all(g in d["lon"] for _n, gl in st for g in gl):
                continue
            p.geprueft += 1
            reihen = [(name, _p18_reihe([(d["lon"][g], g) for g in gl])) for name, gl in st]
            if any(r[0] != f and r[-1] != f for _n, r in reihen):
                continue

            def lage(g, r):
                # das Zeichen nur, wenn die Gruppe ueber eine Zeichengrenze reicht
                t = _p18_lage_txt(d["lon"][g])
                return t if len({int(d["lon"][x] // 30) for x in r}) > 1 else t.split(" ")[0]
            p.pruefen.append("%s: „%s“ — Ballung: „%s“ — %s ist Randglied: %s"
                             % (ort, _kurz(satz, 140), m.group(0), ANZEIGE.get(f, f), " · ".join(
                                 "Stellium in %s: %s" % (name, ", ".join("%s %s" % (ANZEIGE.get(g, g), lage(g, r))
                                                                         for g in r)) for name, r in reihen)))
            n += 1
    return n


# --- Leere Haelfte, leerer Bogen; Knotenachse ------------------------------------------
_P18_LEERFLAECHE_RE = re.compile(_P18_GRENZ + r"(?:leere|freie)[nrs]?\s+(?P<w>Hälfte|Bogens?|Halbkreis(?:es)?)"
                                 + _P18_ENDE, re.I)
_P18_IN_DER_VOR_RE = re.compile(r"(?:\bin|\bim|\bins|\bauf|\baus|\bvon|\bzur|\bzum|\bbis)\s+(?:der|dem|den|einer|"
                                r"einem|dieser|diesem|deiner|deinem|ihrer|seiner)?\s*(?:ganz\s+|großen\s+)?$", re.I)
_P18_LIEGT_RE = re.compile(_P18_GRENZ + r"(?:liegt|liegen|lag|lagen|steht|stehen|fällt|fallen|befindet|befinden)"
                           + _P18_ENDE)
_P18_ORT = (r"(?:im|in\s+(?:der|den|dem)|ins)\s+(?:(?:%s)(?:n|en|s|es)?%s|%s\s+Haus%s"
            r"|(?:Feld|Bereich|Haus)(?:es|s)?\s+(?:des|der|von|deines|deiner)\s+[\wäöüß]+"
            r"|Zeichen\s+(?:des|der)\s+(?:%s)(?:n|en|s|es)?%s)"
            % (ZEICHEN_RE, _P18_ENDE, _P18_ORD_RE, _P18_ENDE, ZEICHEN_RE, _P18_ENDE))
_P18_ORTSANGABE_RE = re.compile(_P18_GRENZ + _P18_ORT)
_P18_ORT_VORAN_RE = re.compile(r"(?:^|[,;:]\s*)" + _P18_ORT + r"\s+(?:liegt|liegen|lag|lagen)\s+"
                               r"(?:die|der|deine|dein|eine|ein)\s+$", re.I)
_P18_MITTE_LEER_RE = re.compile(r"Mitte der leeren Hälfte\s+(\d{1,2}°\d{2}′\s+%s(?:\s*[^\s,;)]{1,2})?"
                                r"(?:,\s*Haus\s+[\d/=]+)?)" % ZEICHEN_RE)
_P18_SCHUESSEL_RE = re.compile(r"(?:Schüssel|Spanne)\s+(\d{1,3})°(\d{2})′\s+von\s+([A-ZÄÖÜ][a-zäöüß]+)\s+\([^)]*\)"
                               r"\s+bis\s+([A-ZÄÖÜ][a-zäöüß]+)")
_P18_MUSTER_RE = re.compile(r"Muster nach Jones:\s*([A-ZÄÖÜ][\wäöüß]+)")


def _p18_leere_mitte(d):
    """Mitte der leeren Haelfte als Text: aus §8, sonst aus der Schuessel in §8 (Mitte der
    Schuessel + 180°, auch beim Eimer — der Henkel zaehlt nicht); None ohne Schuessel."""
    if d.get("mitte_leer"):
        return "%s (§8)" % d["mitte_leer"]
    sch = d.get("schuessel")
    if sch and sch[1] in d["lon"]:
        mitte = (d["lon"][sch[1]] + sch[0] / 2.0 + 180.0) % 360.0
        h = _p18_haus_von(mitte, d["spitzen"]) if d.get("spitzen") else None
        return "%s%s (aus der Schüssel in §8)" % (_p18_lage_txt(mitte), ", Haus %d" % h if h else "")
    return None


def _p18_leere_flaeche(p, d, satz, ort):
    if re.search(_P18_GRENZ + r"(?:Mitte|Mittelpunkt\w*|Zentrum)" + _P18_ENDE, satz):
        return 0
    n = 0
    for m in _P18_LEERFLAECHE_RE.finditer(satz):
        mo_voran = _P18_ORT_VORAN_RE.search(satz[:m.start()])
        if not mo_voran and _P18_IN_DER_VOR_RE.search(satz[max(0, m.start() - 30):m.start()]):
            continue
        rest = satz[m.end():]
        mo = mo_voran or _P18_ORTSANGABE_RE.search(rest)
        if not mo_voran and (not mo or not _P18_LIEGT_RE.search(rest) or _p18_faktoren(rest[:mo.start()]) or
                             re.search(r"Rand|reicht|zwischen", rest[:mo.start()])):
            continue
        pl = sorted((d["lon"][f], f) for f in _P18_PLANETEN if f in d["lon"])
        if len(pl) < 3:
            continue
        p.geprueft += 1
        k = len(pl)
        g, i = max(((pl[(j + 1) % k][0] - pl[j][0]) % 360.0, j) for j in range(k))
        mitte = (pl[i][0] + g / 2.0) % 360.0
        h = _p18_haus_von(mitte, d["spitzen"]) if d.get("spitzen") else None
        bogen = ("der leere Bogen umfasst %s (von %s %s bis %s %s); in einem Zeichen oder Haus liegt nur "
                 "seine Mitte: %s%s" % (_p18_grad_txt(g), ANZEIGE.get(pl[i][1], pl[i][1]), _p18_lage_txt(pl[i][0]),
                                        ANZEIGE.get(pl[(i + 1) % k][1], pl[(i + 1) % k][1]),
                                        _p18_lage_txt(pl[(i + 1) % k][0]), _p18_lage_txt(mitte),
                                        ", Haus %d" % h if h else ""))
        if m.group("w").casefold().startswith("hälfte"):
            mt = _p18_leere_mitte(d)
            wert = ("die leere Hälfte umfasst 180°; in einem Zeichen oder Haus liegt nur ihre Mitte: %s" % mt
                    if mt else "§8 nennt keine leere Hälfte (Muster: %s); %s" % (d.get("muster") or "—", bogen))
        else:
            wert = bogen
        p.pruefen.append("%s: „%s“ — Leere Fläche: „%s … %s“ — %s"
                         % (ort, _kurz(satz, 140), m.group(0), mo.group(0).strip(" ,;:"), wert))
        n += 1
    return n


_P18_ACHSE_GEGEN_RE = re.compile(_P18_GRENZ + r"(?:(?:der|die)\s+(?:Mond)?[Kk]notenachse\s+gegenüber"
                                 r"|gegenüber\s+der\s+(?:Mond)?[Kk]notenachse)" + _P18_ENDE, re.I)


def _p18_achse_gegenueber(p, d, satz, vorher, ort):
    n = 0
    for m in _P18_ACHSE_GEGEN_RE.finditer(satz):
        a, b = _p18_teilsatz(satz, m.start())
        # eine Lage („steht … gegenüber“), kein Verhaeltnis („verhält sich gegenüber …“)
        if not _P18_LAGEVERB_RE.search(satz[a:b]):
            continue
        for f in _p18_subjekte(satz, a, m.start(), b, vorher, ohne={"MONDKNOTEN", "SUEDKNOTEN"}):
            p.geprueft += 1
            zs = [z for z in d["tabelle"] if {z["a"], z["b"]} == {f, "MONDKNOTEN"} and not z["spiegel"]]
            opp = [z for z in zs if z["art"] == "Opposition"]
            konj = [z for z in zs if z["art"] == "Konjunktion"]
            wert = ("%s — gegenüber liegt der Nordknoten (Mondknoten); der Südknoten liegt auf derselben Seite"
                    % _p18_zeile_txt(opp[0]) if opp else
                    "%s — gegenüber liegt der Südknoten; der Nordknoten liegt auf derselben Seite"
                    % _p18_zeile_txt(konj[0]) if konj else
                    "%s steht weder in Opposition noch in Konjunktion zum Mondknoten%s"
                    % (ANZEIGE.get(f, f), (" (%s)" % "; ".join(_p18_zeile_txt(z) for z in zs)) if zs else ""))
            p.pruefen.append("%s: „%s“ — Knotenachse: einer Achse steht kein Faktor gegenüber, nur einem ihrer "
                             "Enden — %s" % (ort, _kurz(satz, 140), wert))
            n += 1
    return n


def _p18_naehe(p, d, satz, vorher, ort):
    """Strang 2 (2026-10-13): Naehe-, Lage- und Rangwoerter ausserhalb der Zeit-Kapitel."""
    return (_p18_absolut(p, d, satz, vorher, ort) + _p18_rang_ganz(p, d, satz, vorher, ort)
            + _p18_rang_strikt(p, d, satz, vorher, ort) + _p18_naehe_orb(p, d, satz, vorher, ort)
            + _p18_beieinander(p, d, satz, ort) + _p18_ballung(p, d, satz, vorher, ort)
            + _p18_leere_flaeche(p, d, satz, ort) + _p18_achse_gegenueber(p, d, satz, vorher, ort))


def _p18_daten(chapters, typ, txt, themen, tabelle, events):
    herr, eigen = _p18_hausherrscher(txt)
    thema = _p18_thema_mengen(themen)
    k2t = _p18_kapitel_nr(chapters, typ)
    ab = _zaehlung_ab(chapters, typ)
    d = {"staende": _p18_staende(txt), "herrscher": herr, "eigen_haus": eigen,
         "leerpunkte": _p18_leerpunkte(txt),
         "tabelle": tabelle or [], "thema": thema, "kap2thema": k2t,
         "thema2kap": (lambda n: n + (ab - 1)), "rangzeilen": _rangzeilen_lesen(txt),
         "ev": {}, "frueher": {}, "jetzt": {}, "stationen": [], "zeichen": [],
         "start": None, "ende": None, "stichtag": None,
         "haeuser_durch": [], "zusatz": {}, "quartal_grenzen": [], "dicht": {}, "kap_dicht": {}}
    # 2026-10-13 (Strang 2): Laengen, Hausspitzen, Stellien (§6) und die Mitte der leeren
    # Haelfte (§8) fuer die Naehe- und Lagewoerter
    m8 = _P18_MITTE_LEER_RE.search(txt or "")
    ms = _P18_SCHUESSEL_RE.search(txt or "")
    mm = _P18_MUSTER_RE.search(txt or "")
    d.update({"lon": _p18_laengen(txt), "spitzen": _p18_spitzen(txt), "stellien": _p18_stellien(txt),
              "mitte_leer": m8.group(1).strip() if m8 else None,
              "schuessel": ((int(ms.group(1)) + int(ms.group(2)) / 60.0, kanon(ms.group(3)), kanon(ms.group(4)))
                            if ms else None),
              "muster": mm.group(1) if mm else None,
              # zwei Bilder (Beziehungshoroskop): Staende je Person, die Tabelle fuehrt nur
              # Aspekte ZWISCHEN beiden — Naehe innerhalb eines Bildes laesst sich nicht halten
              "zwei_bilder": bool(re.search(r"\n## St[äa]nde\s*\n+### |^## Aspekte zwischen beiden",
                                            txt or "", re.M))})
    # 2026-10-13 (Strang 1): die dichten Kapitel je Quartal aus der @@ZEITLEISTE
    for mq in re.finditer(r"^Q(\d+)\s*\|\s*dicht=([\d,\s]*)", txt or "", re.M):
        ks = {int(x) for x in re.findall(r"\d+", mq.group(2))}
        d["dicht"][int(mq.group(1))] = ks
        for k in ks:
            d["kap_dicht"].setdefault(k, set()).add(int(mq.group(1)))
    if events:
        d.update({"ev": _p18_ev_index(events), "frueher": _p18_frueher_index(events),
                  "ev_spiegel": _p18_ev_index_spiegel(events),
                  "jetzt": events.get("jetzt") or {}, "stationen": events.get("stations") or [],
                  "zeichen": events.get("zeichenaufenthalt") or [],
                  "start": events.get("start"), "ende": events.get("end"),
                  "lookback": events.get("lookback_start"),
                  "stichtag": events.get("asof") or (events.get("jetzt") or {}).get("stichtag"),
                  "haeuser_durch": events.get("hausdurchgang") or [],
                  "zusatz": events.get("zusatz") or {},
                  "quartal_grenzen": events.get("quarter_bounds") or []})
    return d


def _p18_satzarten(chapters, typ, txt, themen, tabelle, events=None, sprache_analyse="de"):
    """P18 Satzarten (2026-10-04) — s. Kommentar am Abschnittsanfang. Nur PRUEFEN,
    nur bei Widerspruch zu den Daten, jeder Hinweis mit dem Datenwert."""
    p = _Probe("P18", "Satzarten (Leere, Herrscher, Verweise, Dokument, Rang, Anteil, Nähe, Absolutformel, "
                      "Beieinander, Ballung, leere Fläche, Knotenachse; "
                      "Transit: Zeit, Zugleich, Station, Anzahl, Wiederholung, Grenze, Wechsel, "
                      "Abstand, Bündel, Genau, Kapitelzeit, Dauer)")
    p.einheit = "Aussagen"
    if sprache_analyse != "de":
        return p.uebersprungen("englische Fassung — die Satzmuster sind deutsch")
    d = _p18_daten(chapters, typ, txt, themen, tabelle, events)
    transit = (typ == "transit")
    if transit and not events:
        p.teilweise.append("Transit-Satzarten (Zeit, Zugleich, Station, Anzahl, Wiederholung, Grenze, "
                           "Wechsel, Abstand, Bündel, Genau, Kapitelzeit, Dauer) — "
                           "ohne events.json nicht gegen die Rechnung gehalten (--events)")
    satzliste = _p18_satzliste(chapters)
    absaetze = {}
    for _ch, _bw, i_b, _i_s, s in satzliste:
        absaetze.setdefault(i_b, []).append(s)
    for i, (ch, bewegung, i_b, _i_s, satz) in enumerate(satzliste):
        vorher = satzliste[i - 1][4] if i and satzliste[i - 1][2] == i_b else ""
        ort = "%s · %s" % (_bezeichnung(ch), bewegung)
        eigenes = _kicker_nr(ch.get("kicker"))
        th = d["thema"].get(d["kap2thema"](eigenes)) if eigenes else None
        kapitel_kontakte = th["kontakte"] if th else []
        _p18_leere(p, d, satz, vorher, ort)
        _p18_herrscher(p, d, satz, satzliste, i, ort)
        _p18_kapitelverweis(p, d, satz, ort, eigenes, chapters)
        _p18_modulwort(p, chapters, satz, ort)
        _p18_dokument(p, d, satz, ort, vorher)
        _p18_anteil(p, d, satz, ort)
        # 2026-10-13 (Strang 1): die Zeit-Satzarten auch im Kapitel „Die Zeit“ einer
        # Vertiefung (dort laeuft die Probe mit typ='geburt' und der events.json)
        zeit_kap = transit or _ist_kicker(ch, "Die Zeit", "The Time")
        # 2026-10-13 (Strang 2): Naehe-, Lage- und Rangwoerter der Radix — nicht dort, wo
        # „genau“ das Exaktdatum meint
        if not zeit_kap and not d["zwei_bilder"]:
            _p18_naehe(p, d, satz, vorher, ort)
        if zeit_kap and events:
            _p18_zeit(p, d, satz, ort, absaetze.get(i_b))
            _p18_zugleich(p, d, satz, ort, kapitel_kontakte)
            _p18_station(p, d, satz, ort, vorher)
            _p18_anzahl(p, d, satz, ort, kapitel_kontakte)
            _p18_wiederholung(p, d, satz, vorher, ort, kapitel_kontakte)
            _p18_nie_seit_geburt(p, d, satz, vorher, ort, kapitel_kontakte)
            fuehrt_k = next(((t_, a_, z_) for (t_, a_, z_, f_) in kapitel_kontakte if f_ == "fuehrt"), None)
            frueher = [x[4] for x in satzliste[max(0, i - 6):i] if x[2] == i_b]
            _p18_grenze(p, d, satz, ort)
            _p18_wechsel(p, d, satz, ort)
            frueher_kap = [x[4] for x in satzliste[max(0, i - 8):i] if x[0] is ch]
            _p18_abstand(p, d, satz, ort, vorher, fuehrt_k, frueher_kap)
            _p18_buendel(p, d, satz, ort)
            _p18_genau(p, d, satz, ort, kapitel_kontakte)
            _p18_kapitelzeit(p, d, satz, ort, eigenes)
            _p18_dauer(p, d, satz, ort)
            _p18_dieselben(p, d, satz, ort, frueher, kapitel_kontakte)
    # 2026-10-13 (Strang 1): Buendel auch in der Signatur der Zeit-Kapitel
    if events:
        for ch in chapters:
            if (transit or _ist_kicker(ch, "Die Zeit", "The Time")) and ch.get("signatur"):
                _p18_buendel(p, d, _ws(ch["signatur"]), "%s · Signatur" % _bezeichnung(ch), True)
    _p18_signatur(p, d, chapters)
    if p.geprueft == 0 and not p.pruefen:
        p.hinweise.append("keine Aussage der geprüften Satzarten im Text gefunden")
    return p.abschluss()


# ---------------------------------------------------------------------------
# P19 Wiederholung (2026-10-11, Auswertung der Pruefberichte vom 11.10., Teil 2)
#
# Chris-Entscheidung 2026-10-11 (Pruefbericht Beziehung Design Paar, „Chris-Ansagen“;
# Antwort auf die Auswertung): Immer gleich wiederkehrende Saetze, die Inhalt von
# Kapiteln sind, sind im End-PDF nicht gut — kein Satz soll oefter als zweimal gleich
# vorkommen. Ausgenommen sind die WEGWEISER, die in jedem Kapitel gleich bleiben
# (Chris: „3, 4 , 5 und 7 bleiben gleich als Wegweiser“): die Anfaenge der zwei
# Formen und des Dazwischen, die Etiketten der Uebungen, „Gut genug ist es, wenn …“,
# im Geburtshoroskop „Die Schattenseite in einem Satz:“, „Zusammen ergibt das …“ und
# „Abrufen kannst du es, indem …“; dazu der Wiederholungssatz des Transits, dessen
# Wortlaut Chris am 07.10. festgelegt hat, und der Satz zum realen Problem des
# Kinder-Bausteins (Chris' Wortlaut vom 11.10.; Setzung dieses Laufs, Chris im Chat
# genannt). Nach der Leseprobe im selben Lauf dazu: die Formen der Ressourcen-Bauform
# („In der genutzten/verschleuderten Form“), die drei Formen des Transit-
# Wiederholungshinweises (auch „Zuletzt stand der Saturn …“) und der zweite Satz der
# Kinder-Vorlage („Dann sprich möglichst bald darüber mit einem Erwachsenen …“).
# „Gleich“ heisst: derselbe GANZE Satz irgendwo im Dokument, oder derselbe
# Satzanfang (das Etikett vor dem Doppelpunkt, sonst die ersten vier Woerter) an
# derselben Stelle (Bewegung) in mehr als zwei Kapiteln. So trifft die Probe die
# Formeln, nicht jedes „Dein Mond steht …“ in verschiedenen Zusammenhaengen.
# ---------------------------------------------------------------------------

WEGWEISER_RE = re.compile(
    r"^(?:In der reifen Form|In ihrer reifen Form|In der regressiven Form|"
    r"In ihrer regressiven Form|Dazwischen liegt der Normalfall|"
    r"Das Dazwischen ist der Normalfall|"
    r"Das (?:Erste|Zweite|Dritte|Vierte):|Was du nicht tun solltest:|"
    r"Was du lassen solltest:|Was ihr lassen solltet:|Was ihr nicht tun solltet:|"
    r"Etwas zu tun:|Etwas zu lassen:|Nicht tun:|Gemeinsam:|Für [A-ZÄÖÜ][\w’'-]*:|"
    r"Gut genug ist(?: es)?\b|Was gut genug ist:|"
    r"Die Schattenseite in einem Satz:|Zusammen ergibt das\b|Abrufen kannst du es\b|"
    r"In (?:der|ihrer) (?:genutzten|verschleuderten) Form\b|"
    r"Zuletzt stand (?:der |die |das )?[A-ZÄÖÜ]\w+ so wie jetzt\b|"
    r"Dieselbe Frage stand zuletzt an\b|Der Durchgang davor (?:in derselben Stellung )?lief\b|"
    r"Vorweg ein Satz, der nichts mit Astrologie zu tun hat\b|"
    r"Dann sprich möglichst bald darüber mit einem Erwachsenen\b)")
WIEDERHOLUNG_GRENZE = 2          # hoechstens zweimal gleich (Chris, 11.10.)


def _wh_satz(s):
    return " ".join(s.split()).strip()


def _wh_anfang(s):
    """Schluessel des Satzanfangs: das Etikett vor einem Doppelpunkt in den ersten
    sechs Woertern, sonst die ersten vier Woerter — klein, ohne Satzzeichen."""
    t = _wh_satz(s)
    vor = t.split(":", 1)[0] if ":" in t else None
    if vor is not None and len(vor.split()) <= 6:
        return vor.casefold() + ":"
    w = re.findall(r"[\wÄÖÜäöüß’'-]+", t)
    return " ".join(w[:4]).casefold() if len(w) >= 3 else None


def wiederholungen(einheiten, wegweiser=None, grenze=WIEDERHOLUNG_GRENZE,
                   satzanfaenge=True):
    """Die Zaehlung der Probe P19, auch fuer andere Builder (beziehung.probe, B21).

    einheiten  Liste von (kapitel, bewegung, text): kapitel ein Name fuer die
               Meldung (Kicker), bewegung der Titel der Bewegung oder None (Text
               ohne Bewegung: nur der wortgleiche Satz zaehlt), text ein Absatz.
    wegweiser  Regex der Satzanfaenge, die ausgenommen sind (Vorgabe WEGWEISER_RE).
    -> Liste von dicts {'art': 'satz'|'anfang', 'text', 'bewegung', 'orte': [kapitel],
       'anzahl'} — nur, was die Grenze ueberschreitet.
    """
    weg = WEGWEISER_RE if wegweiser is None else wegweiser
    saetze, anfaenge, folge = {}, {}, []
    for kap, bew, text in einheiten:
        for satz in _saetze(text):
            t = _wh_satz(satz)
            if len(t) < 12 or weg.match(t):
                continue
            if t not in saetze:
                folge.append(("satz", t))
            saetze.setdefault(t, []).append(kap)
            if satzanfaenge and bew:
                k = _wh_anfang(t)
                if k:
                    if (bew, k) not in anfaenge:
                        folge.append(("anfang", (bew, k)))
                    anfaenge.setdefault((bew, k), {"orte": [], "beispiel": t})
                    if kap not in anfaenge[(bew, k)]["orte"]:
                        anfaenge[(bew, k)]["orte"].append(kap)
    out = []
    for art, k in folge:
        if art == "satz" and len(saetze[k]) > grenze:
            out.append({"art": "satz", "text": k, "bewegung": None,
                        "orte": saetze[k], "anzahl": len(saetze[k])})
        elif art == "anfang" and len(anfaenge[k]["orte"]) > grenze:
            out.append({"art": "anfang", "text": anfaenge[k]["beispiel"], "bewegung": k[0],
                        "orte": anfaenge[k]["orte"], "anzahl": len(anfaenge[k]["orte"])})
    return out


def wiederholung_zeile(w):
    """Meldetext eines Treffers von wiederholungen() — gleich in P19 und B21."""
    orte = ", ".join(dict.fromkeys(w["orte"]))
    if w["art"] == "satz":
        return ("wortgleich %d-mal: „%s“ (%s) — höchstens zweimal; Wortlaut wechseln"
                % (w["anzahl"], _kurz(w["text"], 110), orte))
    return ("Satzanfang „%s …“ in %d Kapiteln an derselben Stelle („%s“: %s) — höchstens "
            "zweimal; Einleitung wechseln" % (_kurz(" ".join(w["text"].split()[:5]), 60),
                                             w["anzahl"], w["bewegung"], orte))


def _p19_wiederholung(chapters, typ, sprache_analyse="de"):
    p = _Probe("P19", "Wiederholung (höchstens zweimal gleich)")
    p.einheit = "Sätze"
    einheiten = []
    for ch in chapters:
        # 2026-10-13: auch das Register des Transits (`Mitlaufendes`) zaehlt nicht mit — seine
        # Zeilen sind ein Register wie die Rechenschaft (Pruefberichte Transit 2 und 3+4 vom
        # 12.10.: sieben Fehlalarme auf „Klingt in Kapitel n mit.“, in 3+4 eine Rueckfrage).
        if _ist_kicker(ch, "Rechenschaft", "Account", "Mitlaufendes"):
            continue
        bew = None
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bew = _ws(b["text"])
                continue
            if b.get("type") in ("p", "li") and b.get("text"):
                einheiten.append((ch.get("kicker") or _bezeichnung(ch), bew, b["text"]))
                p.geprueft += len(_saetze(b["text"]))
    englisch = sprache_analyse == "en"
    if englisch:
        p.hinweise.append("englische Fassung — nur der wortgleiche Satz geprüft, die "
                          "Wegweiser-Liste ist deutsch")
    for w in wiederholungen(einheiten, satzanfaenge=not englisch):
        p.pruefen.append(wiederholung_zeile(w))
    return p.abschluss()


class InhaltsprobeFehler(Exception):
    """Eingabe nicht lesbar (fehlende Datei, SchemaError der Analyse)."""

def pruefe(analyse_pfad, chart_data_pfad, typ=None, events_pfad=None):
    """Haelt die Analyse gegen die chart_data. -> dict (s. Docstring des Moduls).

    typ: 'geburt' | 'transit' | None (aus der H1 ableiten); 'ea' und
    'ultimativ' sind seit dem 2026-09-23 ausgemustert und brechen ab.
    events_pfad: die events.json des Transit-Laufs (`transit.py … --json <pfad>`),
    optional (2026-09-19, W24). Mit ihr haelt P1 die Transit-Segmente gegen die
    Rechnung (Kontakt, Exaktdaten, Annaeherungen, Stichtag-Orb), P5 nimmt die
    Soll-Menge des Registers daraus, P11 und P13 zaehlen ihre Daten und Kontakte
    als Fundstelle. Ohne sie: P1 „teilweise übersprungen" mit Grund."""
    for pf in (analyse_pfad, chart_data_pfad):
        if not os.path.isfile(pf):
            raise InhaltsprobeFehler("Datei nicht gefunden: %s" % pf)
    events = _events_laden(events_pfad) if events_pfad else None
    try:
        parsed = build.parse_analyse(analyse_pfad)
    except Exception as e:
        raise InhaltsprobeFehler("Analyse nicht lesbar (%s): %s" % (type(e).__name__, _kurz(str(e), 300)))
    txt = open(chart_data_pfad, encoding="utf-8").read()
    chapters = parsed["chapters"]

    if typ:
        typ = {"geburtshoroskop": "geburt"}.get(typ.casefold(), typ.casefold())
        if typ not in TYPEN and typ not in AUSGEMUSTERTE_TYPEN:
            raise InhaltsprobeFehler("Unbekannter --typ %r; bekannt: %s" % (typ, ", ".join(TYPEN)))
        typ_quelle = "Parameter"
    else:
        typ = typ_aus_h1(parsed.get("doctype"))
        typ_quelle = "H1 „%s“" % parsed.get("doctype") if typ else "H1 „%s“ nicht zuordenbar" % parsed.get("doctype")
    if typ in AUSGEMUSTERTE_TYPEN:
        raise InhaltsprobeFehler("Typ %r (%s) ist seit dem 2026-09-23 ausgemustert — "
                                 "geprueft werden Geburtshoroskop und Transit." % (typ, typ_quelle))

    chart = selektor.parse_chart(txt)
    unlesbar = []
    tabelle = _tabellen_lesen(txt, unlesbar)
    staende = _staende_lesen(txt)
    themen = _themenliste_lesen(txt)
    sprache_analyse = sprache(parsed)

    p1 = _p1_beleg_aspekte(chapters, typ, tabelle, events, unlesbar)
    p2 = _p2_beleg_staende(chapters, typ, chart, staende)
    p3, p7, zuordnung = _p3_p7_kapitel_themen(chapters, typ, themen, sprache_analyse)
    p4 = _p4_bewegungsfolge(chapters, typ, zuordnung)
    p5 = _p5_rechenschaft(chapters, chart, themen, typ, txt, events, chart_data_pfad, events_pfad,
                          sprache_analyse)
    p6 = _p6_leitsatz(chapters, chart_data_pfad, themen)
    p8 = _p8_wortlisten(chapters)
    p9 = _p9_zwei_saetze(chapters, typ)
    p10 = _p10_wortscan(chapters, sprache_analyse)
    # 2026-09-19: U1 (P11–P13), W10/W43 (P14), W37 (P15)
    p11 = _p11_zahlen(chapters, txt, events, sprache_analyse)
    p12 = _p12_rang(chapters, txt, typ, sprache_analyse)
    p13 = _p13_beleg_deckung(chapters, typ, tabelle, txt, events)
    p14 = _p14_kopfblock(chapters, typ)
    p15 = _p15_ressourcen(chapters, typ, txt, zuordnung)
    # 2026-09-24 (Klasse-2-Entscheidungslauf): T3 (P16), E5 (P17)
    p16 = _p16_laenge(chapters, typ, txt, themen, zuordnung)
    p17 = _p17_subjekt(chapters, typ, sprache_analyse)
    # 2026-10-04 (Wartungslauf Satzarten-Probe): P18
    p18 = _p18_satzarten(chapters, typ, txt, themen, tabelle, events, sprache_analyse)
    # 2026-10-11 (Chris-Entscheidung 2026-10-11): P19
    p19 = _p19_wiederholung(chapters, typ, sprache_analyse)
    proben = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18,
              p19]

    fehler = sum(len(p.fehler) for p in proben)
    pruefen_n = sum(len(p.pruefen) for p in proben)
    ueber = [(p.nr, p.status.lower(), p.grund) for p in proben if p.status in ("UEBERSPRUNGEN", "AUSSAGELOS")]
    # 2026-09-19 (W44): was INNERHALB einer Probe bewusst ungeprueft blieb, zaehlt mit.
    ueber += [(p.nr, "teilweise übersprungen", g) for p in proben for g in p.teilweise]
    return {
        "analyse": analyse_pfad, "chart_data": chart_data_pfad,
        "events": events_pfad,
        "typ": typ, "typ_quelle": typ_quelle, "doctype": parsed.get("doctype"),
        "proben": {p.nr: p.als_dict() for p in proben},
        "fehler": fehler, "pruefen": pruefen_n, "uebersprungen": ueber,
        "ok": fehler == 0,
    }

def _zeile(p):
    kopf = "%s %s:" % (p["nr"], p["name"])
    st = p["status"]
    if st == "UEBERSPRUNGEN":
        return ["%s übersprungen — %s" % (kopf, p["grund"])]
    if st == "AUSSAGELOS":
        return ["%s AUSSAGELOS — %s" % (kopf, p["grund"])]
    zaehl = "%d %s" % (p["geprueft"], p["einheit"])
    if st == "FEHLER":
        out = ["%s FEHLER (%d Fehler, %s%s)" % (kopf, len(p["fehler"]), zaehl,
                                                 ", %d PRÜFEN" % len(p["pruefen"]) if p["pruefen"] else "")]
    elif st == "PRUEFEN":
        out = ["%s %s, 0 Fehler, %d PRÜFEN" % (kopf, zaehl, len(p["pruefen"]))]
    else:
        out = ["%s %s, 0 Fehler" % (kopf, zaehl)]
    out += ["    FEHLER  " + f for f in p["fehler"]]
    out += ["    PRÜFEN  " + f for f in p["pruefen"]]
    out += ["    Übersprungen " + h for h in p.get("teilweise", [])]
    out += ["    Hinweis " + h for h in p["hinweise"]]
    return out

def bericht(analyse_pfad, chart_data_pfad, typ=None, events_pfad=None):
    """Der Prueftext: eine Zeile je Probe, je Befund eine eingerueckte Zeile,
    zuletzt `INHALTSPROBE: f FEHLER · p PRÜFEN · s übersprungen (Gründe)`.
    events_pfad: s. pruefe() — im Transit die events.json des Laufs."""
    return bericht_aus(pruefe(analyse_pfad, chart_data_pfad, typ, events_pfad))

def bericht_aus(r):
    """Prueftext aus einem Ergebnis von pruefe()."""
    zeilen = ["Inhaltsprobe — %s gegen %s%s (Typ: %s, aus %s)"
              % (os.path.basename(r["analyse"]), os.path.basename(r["chart_data"]),
                 " und %s" % os.path.basename(r["events"]) if r.get("events") else "",
                 r["typ"] or "unbekannt", r["typ_quelle"])]
    for nr in sorted(r["proben"], key=lambda x: int(x[1:])):
        zeilen += _zeile(r["proben"][nr])
    gruende = "; ".join("%s %s: %s" % (nr, art, g) for nr, art, g in r["uebersprungen"])
    zeilen.append("INHALTSPROBE: %d FEHLER · %d PRÜFEN · %d übersprungen%s"
                  % (r["fehler"], r["pruefen"], len(r["uebersprungen"]),
                     " (%s)" % gruende if gruende else ""))
    return "\n".join(zeilen)

# ---------------------------------------------------------------------------
# Selbsttest — KONSTRUIERTER Fall. Kein reales Geburtsdatum, keine Uhrzeit, kein
# Name, keine Staende eines realen Charts (Datenschutz-Guardrail des Kerns).
# ---------------------------------------------------------------------------

_TEST_CHART = """# Chart-Datenblatt — Prüffall

## Stände (konstruiert)

| Faktor | Grad | Zeichen | Haus | Lauf |
|---|---|---|---|---|
| Sonne | 10°00′ | Widder ♈ | 1 | direkt |
| Mond | 20°00′ | Stier ♉ | 2 | direkt |
| Merkur | 11°10′ | Widder ♈ | 1 | direkt |
| Mars | 5°00′ | Krebs ♋ | 4/3 | direkt |
| Saturn | 22°05′ | Jungfrau ♍ | 6 | direkt |
| AC | 0°00′ | Widder ♈ | 1 | — |
| MC | 0°00′ | Steinbock ♑ | 10 | — |
| DC | 0°00′ | Waage ♎ | 7 | — |
| IC | 0°00′ | Krebs ♋ | 4 | — |

## Aspekte (konstruiert)

### Volle Aspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Sonne | ☌ Konjunktion | Merkur | 1°10′ | konj |  |
| Mond | △ Trigon | Saturn | 2°05′ | blau |  |
| Mars | □ Quadrat | AC | 0°40′ | rot | Quadrat DC |

### Einseitige Aspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Mars | ☍ Opposition | MC | 0°40′ | rot | Konjunktion IC |

### Nebenaspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Sonne | ⚹ Sextil | Mond | 4°30′ | gruen |  |

### Untergrund-Aspekte

_keine_

## Strukturbild (konstruiert)

### 7 · Zyklusfenster (Einordnung, keine Prognose)
- Alter der Person: 41 Jahre.
  - Saturn: erste Saturn-Opposition ~14.7 [zurückliegend] · Saturn-Rückkehr ~29.5 [zurückliegend] · zweite Saturn-Opposition ~44.2 [bevorstehend]

### 10 · Rangzeilen (Zahlen für Rang-, Zähl- und Einzigkeitsaussagen)
- RANG engste-aspekte [Zeilen der Aspekttabelle, 5 Zeilen; Rang nach dem Orb in Bogenminuten]: 1. Mars Quadrat AC 0°40′ (voll, zugleich Quadrat DC) · 1. Mars Opposition MC 0°40′ (einseitig, zugleich Konjunktion IC) · 3. Sonne Konjunktion Merkur 1°10′ (voll) · 4. Mond Trigon Saturn 2°05′ (voll) · 5. Sonne Sextil Mond 4°30′ (neben)
- RANG engste-aspekte-planeten [nur Zeilen zwischen zwei Planeten, 3 Zeilen]: 1. Sonne Konjunktion Merkur 1°10′ (voll) · 2. Mond Trigon Saturn 2°05′ (voll) · 3. Sonne Sextil Mond 4°30′ (neben)
- RANG verbindungen-gezaehlt [jeder Aspekt zählt 1, ein Kontakt zu beiden Enden einer Achse je Ende]: 1. Mars 4 (Aspekttabelle 2) · 2. Sonne 2 · 2. Mond 2 · 4. Merkur 1 · 4. Saturn 1
- RANG verbindungen-gewichtet [voll 1, einseitig 0.5, Nebenaspekt 0.5]: 1. Mars 3 · 2. Sonne 1.5 · 2. Mond 1.5 · 4. Merkur 1 · 4. Saturn 1
- RANG elemente-gezaehlt [fünf Planeten des Prüffalls, je 1, Summe 5]: 1. Feuer 2 von 5 = 40 % (Sonne, Merkur) · 1. Erde 2 von 5 = 40 % (Mond, Saturn) · 3. Wasser 1 von 5 = 20 % (Mars) · 4. Luft 0 von 5 = 0 % (—)
- RANG elemente-gewichtet [alle Faktoren, Lichter und Achsen ×2; Summe 11]: 1. Feuer 5 von 11 = 45 % (Sonne ×2, Merkur, AC ×2) · 1. Erde 5 von 11 = 45 % (Mond ×2, Saturn, MC ×2) · 3. Wasser 1 von 11 = 9 % (Mars) · 4. Luft 0 von 11 = 0 % (—)
- RANG modi-gezaehlt [fünf Planeten des Prüffalls, je 1, Summe 5]: 1. kardinal 3 von 5 = 60 % (Sonne, Merkur, Mars) · 2. fix 1 von 5 = 20 % (Mond) · 2. veränderlich 1 von 5 = 20 % (Saturn)
- RANG modi-gewichtet [alle Faktoren, Lichter und Achsen ×2; Summe 11]: 1. kardinal 8 von 11 = 73 % (Sonne ×2, Merkur, Mars, AC ×2, MC ×2) · 2. fix 2 von 11 = 18 % (Mond ×2) · 3. veränderlich 1 von 11 = 9 % (Saturn)

## Themenliste

```
THEMA 1 | titel=Der Anfang, der sich selbst genügt
  | fuehrt=Sonne, Widder, Haus 1
  | klingt=Merkur Widder Haus 1
  | aspekte=Sonne ☌ Merkur, Sonne ⚹ Mond
  | rang=4 | form=voll
  | praxis=Einmal am Tag den ersten Impuls bemerken.
  | familie=Bemerken und Benennen
  | leitachse=ja

THEMA 2 | titel=Was hält, wenn nichts drängt
  | fuehrt=Mond, Stier, Haus 2
  | klingt=Saturn Jungfrau Haus 6
  | aspekte=Mond △ Saturn
  | rang=5 | form=kurz | grund=kein Aspektmaterial für Wurzel und Widerstand
  | praxis=Einmal in der Woche etwas stehen lassen, das fertig ist.
  | familie=Innehalten
```
RECHENSCHAFT: Merkur, Widder, Haus 1 — klingt mit in Kapitel 2. Mars, Krebs,
              Haus 4/3 (Grenzlage). Saturn, Jungfrau, Haus 6 — klingt mit in Kapitel 3.
GESTRICHEN:   keines.

## Ressourcen
Mond △ Saturn 2°05′ voll — Deutungsort: Thema 2

@@SELEKTOR
FAKTOR SONNE zeichen=Widder haus=1 fuehrt=ja
FAKTOR MOND zeichen=Stier haus=2 fuehrt=ja
FAKTOR MERKUR zeichen=Widder haus=1
FAKTOR MARS zeichen=Krebs haus=3 nebenhaus=4 abstand=1.5
FAKTOR SATURN zeichen=Jungfrau haus=6
ACHSE AC zeichen=Widder
ACHSE MC zeichen=Steinbock
ACHSE DC zeichen=Waage
ACHSE IC zeichen=Krebs
ASPEKT SONNE MERKUR
ASPEKT MOND SATURN
@@ENDE
@@DECKBLATT
LEITSATZ: Du fängst an, bevor jemand dich darum bittet — und das ist kein Fehler.
LEITACHSE: Der Anfang, der sich selbst genügt
TITELMOTIV: Ein einzelner Stein auf einem leeren Feld im ersten Licht.
PALETTE: Sandgelb, Grau, ein kühles Blau.
GLYPHEN: ☉ ♈ — die Sonne im Widder als der Anfang
@@ENDE
"""

_TEST_ANALYSE = """# Geburtshoroskop — Prüffall

## Auftakt · Wie dieses Horoskop zu lesen ist

Dieses Dokument beschreibt Anlagen, keine Tatsachen. Wenn du ein Kapitel liest und dich darin nicht wiederfindest, darfst du es verwerfen; das gilt für jedes Kapitel dieses Bandes. Am Ende steht eine Liste dessen, was gerechnet und nicht gedeutet wurde.

## Kapitel 1 · Was unter allem liegt

**Signatur:** Die Statik des Bildes — viel Feuer, wenig Wasser, ein kurzer Herrscherkreis

**Beleg:** Elemente Feuer 3 · Erde 1 · Luft 0 · Wasser 1 · Herrscherkreis Sonne → Mars → Mond → Venus

Das Bild ruht auf wenigen Kräften, die einander kaum stützen. Wasser trägt nur ein einziger Planet, dein Mars. Was fehlt, ersetzt die Anstrengung.

## Instrument · Wie du gebaut bist

**Signatur:** Die persönlichen Funktionen in ihrer Anlage — Sonne im Widder im ersten Haus, Mond im Stier im zweiten

**Beleg:** Sonne ☉ 10°00′ Widder ♈, 1. Haus — Konjunktion ☌ Merkur ☿ 1°10′, Sextil ⚹ Mond ☽ 4°30′ · Mond ☽ 20°00′ Stier ♉, 2. Haus — Trigon △ Saturn ♄ 2°05′

### Die Sonne — der Kern

Dein Wesen fängt an, bevor die Frage gestellt ist; die Sonne steht im Widder im ersten Haus. Was daraus unter Druck wird, steht in Kapitel 2.

### Der Mond — wie du fühlst

Dein Gefühl braucht Dauer, um sicher zu werden; der Mond steht im Stier im zweiten Haus. Es hält, was einmal da ist.

## Kapitel 2 · Der Anfang, der sich selbst genügt

**Signatur:** Die Sonne im Widder im ersten Haus, verschmolzen mit Merkur — mitklingend der Mond im Stier

**Beleg:** Sonne ☉ 10°00′ Widder ♈, 1. Haus · Sonne ☉ Konjunktion ☌ Merkur ☿ 11°10′ Widder ♈, 1. Haus, Orb 1°10′ · Sonne ☉ Sextil ⚹ Mond ☽ 20°00′ Stier ♉, 2. Haus, Orb 4°30′

### Woran du es merkst

Du hast angefangen, bevor die anderen fertig überlegt haben. Und ein Letztes, das schwerer zuzugeben ist: Es ärgert dich, wenn jemand vor dir anfängt. Wenn du das nicht kennst, leg das Kapitel weg; das gilt für alle folgenden Kapitel ebenso.

### Was da arbeitet

Deine Sonne im Widder im ersten Haus, verschmolzen mit Merkur — die engste Verbindung zwischen zwei Planeten in deinem Bild — sucht den ersten Schritt, weil dort die Kraft ist.

### Wie so etwas zur Regel wird

Regeln dieser Art entstehen in Umgebungen, in denen Warten teuer war. Wo du das gelernt hast, weiß ich nicht — das steht in keinem Horoskop.

### Der Teil von dir, der das nicht aufgeben will

Der Teil, der zuerst losgeht, hat ein gutes Argument: Wer zuerst geht, muss auf niemanden warten. Er rechnet mit alten Zahlen, aber er rechnet.

### Die zwei Formen und das Dazwischen

Die reife Form fängt an und lässt andere nachkommen. Die regressive Form fängt an, um nicht warten zu müssen, und fühlt sich dabei wie Fortschritt an. Dazwischen liegt der Normalfall: Du merkst es und gehst trotzdem los.

### Womit du arbeiten kannst

Einmal am Tag den ersten Impuls bemerken, ohne ihm zu folgen. Nicht tun: dich zum Warten zwingen. Gut genug ist, es einmal bemerkt zu haben.

### Wohin das gehört

Dieses Thema ist die Vorderseite von Kapitel 3. Es ist groß in deinem Bild, aber nicht das Ganze; was ein Text davon leisten kann, ist die Landkarte, nicht der Weg.

## Kapitel 3 · Was hält, wenn nichts drängt

**Signatur:** Der Mond im Stier im zweiten Haus, getragen von Saturn — mitklingend Saturn in der Jungfrau

**Beleg:** Mond ☽ 20°00′ Stier ♉, 2. Haus · Mond ☽ Trigon △ Saturn ♄ 22°05′ Jungfrau ♍, 6. Haus, Orb 2°05′

### Woran du es merkst

Du bleibst, wo andere längst gegangen sind. Schwerer auszusprechen ist dies: Manchmal bleibst du aus Bequemlichkeit.

### Was da arbeitet

Dein Mond im Stier im zweiten Haus, im Trigon zu Saturn — eine Verbindung, die von selbst hält — braucht keine Bewegung, um sich sicher zu fühlen. Was Saturn dazugibt, ist Form: Das Gefühl bekommt einen Rahmen, in dem es bleiben kann. Ein einzelner harmonischer Aspekt liefert kein Material für Wurzel und Widerstand, deshalb fehlen hier diese beiden Schritte.

### Die zwei Formen und das Dazwischen

Genutzt: Du hältst, was gehalten werden muss. Verschleudert: Du hältst auch, was gehen dürfte. Dazwischen liegt der Normalfall.

### Womit du arbeiten kannst

Einmal in der Woche etwas stehen lassen, das fertig ist. Nicht tun: daraus ein Projekt machen. Gut genug ist, es einmal getan zu haben.

### Wohin das gehört

Dies ist die Rückseite von Kapitel 2. Saturn kehrt um die dreißig an seinen Ort zurück; dieselbe Frage meldet sich dann noch einmal. Es ist eine ruhige Stelle in deinem Bild.

## Rechenschaft · Was sonst in deinem Bild steht

Gerechnet wurde das ganze Bild; gedeutet wurden zwei Themen. Was dazwischen liegt, steht hier.

1. Merkur, Widder, erstes Haus — das schnelle Wort. Klingt mit in Kapitel 2.
2. Mars, Krebs, viertes/drittes Haus in Grenzlage — die Kraft, die nach innen geht.
3. Saturn, Jungfrau, sechstes Haus — die Ordnung im Alltag. Klingt mit in Kapitel 3.

## Hauptthemen · Zwei Linien

**Signatur:** Zusammenführung der Kapitel 2 und 3

Anfangen und Halten sind die beiden Linien dieses Bildes. Was trägt: Der Mond im Trigon zu Saturn — was dir leicht zufällt und gerade deshalb brachliegen kann — hält, ohne dass du es merkst.

## Konfliktfelder · Wo es reibt

**Signatur:** Die Gegensatzpaare der Kapitel 2 und 3

Anfangen gegen Halten: Beides ist in dir angelegt, und beides will zuerst.

## Lebensaufgaben · Woran du wächst

**Signatur:** Was aus den Kapiteln 2 und 3 als Richtung bleibt

Den Anfang machen und dann bleiben, bis er trägt.

## Schlusswort · Was bleibt

Du fängst an, bevor jemand dich darum bittet — und das ist kein Fehler. Das ist der Satz, auf den dieses Horoskop hinausläuft. Was ein Text leisten kann, ist eine Landkarte; gehen musst du selbst.
"""

# Zugang-Kapitel fuer Lauf 3 des Selbsttests (2026-09-16): Kicker `Zugang <Bereich>`,
# Haus-Format im Beleg, Kurzform ohne Wurzel und Widerstand. Wird vor das
# Rechenschaftskapitel gesetzt.
_TEST_ZUGANG = """## Zugang Beruf · Wo die Arbeit hinzieht

**Signatur:** Beruf über die Häuser zehn, sechs und zwei — Saturn in der Jungfrau im sechsten verwaltet den Beruf, Merkur im Widder den Alltag; mitklingend der Mond im Stier im zweiten.

**Beleg:** MC 0°00′ Steinbock ♑ — Herrscher Saturn ♄ 22°05′ Jungfrau ♍, 6. Haus · 6. Haus (Spitze 0°00′ Jungfrau ♍) — Herrscher Merkur ☿ 11°10′ Widder ♈, 1. Haus · im 6. Haus: Saturn ♄ 22°05′ Jungfrau ♍ · im 2. Haus: Mond ☽ 20°00′ Stier ♉ · verwiesen: Mond ☽ Trigon △ Saturn ♄ 2°05′ (Kapitel 3), Mars ♂ Opposition ☍ MC 0°40′ (Rechenschaft)

### Woran du es merkst

Du arbeitest am liebsten dort, wo etwas fertig wird und bleibt. Und ein Letztes, das schwerer zuzugeben ist: Ein Lob für Tempo freut dich weniger als eines für Dauer.

### Was da arbeitet

Saturn in der Jungfrau im sechsten Haus verwaltet den Beruf und steht zugleich im Trigon zum Mond — die Arbeit und das, was dich hält, laufen in dieselbe Richtung. Dieses Kapitel ist ein Zugang: Es sortiert, was die Themenkapitel schon gedeutet haben, unter einer Frage.

### Die zwei Formen und das Dazwischen

Die reife Form baut, was Bestand hat. Die regressive Form bleibt, weil Gehen Mühe macht. Dazwischen liegt der Normalfall: Du bleibst zu lange und gehst dann doch.

### Womit du arbeiten kannst

Einmal im Monat aufschreiben, was an deiner Arbeit fertig geworden ist. Nicht tun: die Liste mit Vorsätzen füllen. Gut genug ist, wenn eine Zeile darauf steht.

### Wohin das gehört

Die Aspekte dieses Kapitels sind in Kapitel 3 gedeutet; hier stehen sie unter der Frage nach der Arbeit. Es ist eine Ordnung, kein neues Thema.

"""

# Transit-Pruefall fuer den Selbsttest (2026-09-19, W10, W23, W24, W43, U1). Die Daten
# stehen NICHT im Quelltext: `_transit_fall()` rechnet sie aus Julianischen
# Tageszahlen (Datenschutz-Guardrail: kein Datumsstring im Code). {dN} ist das Datum
# N Tage nach dem Fensteranfang (ISO), {eN} dasselbe im Beleg-Format TT.MM.JJJJ,
# {mN} Monat und Jahr in Worten.
_TEST_TRANSIT_CHART = """# Chart-Datenblatt — Prüffall Transit

## Stände (konstruiert)

| Faktor | Grad | Zeichen | Haus | Lauf |
|---|---|---|---|---|
| Sonne | 10°00′ | Widder ♈ | 1 | direkt |
| Mond | 20°00′ | Stier ♉ | 2 | direkt |
| Merkur | 11°10′ | Widder ♈ | 1 | direkt |
| Mars | 5°00′ | Krebs ♋ | 4 | direkt |
| AC | 0°00′ | Widder ♈ | 1 | — |
| MC | 0°00′ | Steinbock ♑ | 10 | — |

## Aspekte (konstruiert)

### Volle Aspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Sonne | ☌ Konjunktion | Merkur | 1°10′ | konj |  |

### Nebenaspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Sonne | ⚹ Sextil | Mond | 4°30′ | gruen |  |

## Transit-Rechnung (konstruiert, Auszug)

```text
Fenster {d0} bis {d730}, Stichtag {d45}
[P] Saturn  Quadrat     Sonne        exakt {d60}, {d200}, {d330}
[P] Saturn  Quadrat     Merkur       exakt {d75}, {d190}
[P] Jupiter Trigon      Mond         exakt {d150}
[P] Neptun  Sextil      Mars         exakt {d400}
[P] Knoten  Konjunktion Merkur       Annaeherung bis 1.8′ am {d250}
Frühere Durchgänge mit Datum und Alter
  [P] Saturn  Quadrat     Sonne        #1 {dF} (Alter 12)
```

## Themenliste

```
THEMA 1 | titel=Was unter Druck gerät
  | fuehrt=T-Saturn □ R-Sonne
  | aspekte=T-Saturn □ R-Merkur
  | form=voll | leitachse=ja
THEMA 2 | titel=Was leichter wird
  | fuehrt=T-Jupiter △ R-Mond
  | form=ressource | grund=der führende Kontakt ist harmonisch
```
TRANSIT-RECHENSCHAFT: 5 primaere Wirkorb-Kontakte im Fenster, 3 tragen ein Kapitel, 2 ohne Kapitel — hier einzeln benannt.

- T-Neptun ⚹ R-Mars — im Wirkorb, trägt kein Kapitel
- T-Mondknoten ☌ R-Merkur — im Wirkorb, ohne Nulldurchgang

## Ressourcen
T-Jupiter △ R-Mond    im Wirkorb    — Deutungsort: Thema 2

@@SELEKTOR
FAKTOR SONNE zeichen=Widder haus=1
FAKTOR MOND zeichen=Stier haus=2
FAKTOR MERKUR zeichen=Widder haus=1
FAKTOR MARS zeichen=Krebs haus=4
ACHSE AC zeichen=Widder
ACHSE MC zeichen=Steinbock
@@ENDE
@@DECKBLATT
LEITSATZ: Du darfst langsamer werden, ohne stehen zu bleiben — und genau dort wächst etwas.
LEITACHSE: Was unter Druck gerät
TITELMOTIV: Ein Weg, der im Nebel langsamer wird.
PALETTE: Grau, ein warmes Ocker.
GLYPHEN: ♄ □ ☉ — Saturn im Quadrat zur Sonne
@@ENDE
"""

_TEST_TRANSIT_ANALYSE = """# Transit-Horoskop — Prüffall

## Zur Lesart · Wie du mit diesem Teil arbeitest

Ein Transit beschreibt einen Prozess, keinen Termin. Wenn du ein Kapitel nicht wiedererkennst, darfst du es verwerfen; das gilt für jedes Kapitel dieses Bandes. Die stärkste, die größte und die wichtigste Linie stehen vorn, die zentralste zuletzt, und ruhige Strecken gehören dazu.

## Der Stand heute · Was gerade anliegt

**Signatur:** Saturn im Quadrat zu deiner Sonne, im Anmarsch Jupiter im Trigon zu deinem Mond

**Beleg:** Sonne ☉ 10°00′ Widder ♈, 1. Haus (Mond ☽ 20°00′ Stier ♉, 2. Haus) · T-Saturn ♄ Quadrat □ R-Sonne ☉ — am Stichtag Orb 0,57°, zulaufend; exakt {e60}, {e200}, {e330} · T-Jupiter ♃ Trigon △ R-Mond ☽ — am Stichtag Orb 2,40°, zulaufend; exakt {e150}

Am Stichtag steht Saturn im Quadrat zu deiner Sonne, und der Druck darauf nimmt zu. Jupiter rückt im Trigon zu deinem Mond heran; beides erzählen die folgenden Kapitel.

## Kapitel 1 · Was unter Druck gerät

**Signatur:** Saturn im Quadrat zu deiner Sonne — mitklingend Saturn im Quadrat zu deinem Merkur

**Beleg:** Sonne ☉ 10°00′ Widder ♈, 1. Haus · T-Saturn ♄ Quadrat □ R-Sonne ☉ — exakt {e60}, {e200}, {e330} · T-Saturn ♄ Quadrat □ R-Merkur ☿ — exakt {e75}, {e190}

### Woran du es merkst

Du merkst, dass Dinge länger dauern, als du geplant hast. Und ein Letztes, das schwerer zuzugeben ist: Es kränkt dich, wenn jemand bremst. Wenn du das nicht kennst, leg das Kapitel weg; das gilt für alle folgenden Kapitel ebenso.

### Was da arbeitet

Der laufende Saturn steht im Quadrat zu deiner Sonne im Widder im ersten Haus — eine Reibung, die dich bremst, wo du sonst losgehst. Dasselbe Quadrat trifft deinen Merkur und macht das Denken vorsichtiger.

### Warum das alt ist

Muster dieser Art entstehen dort, wo Tempo belohnt wurde. Wo du das gelernt hast, weiß ich nicht — das steht in keinem Horoskop.

### Der Teil von dir, der das nicht aufgeben will

Der Teil, der zuerst losgeht, hat ein gutes Argument: Wer schnell ist, muss nicht warten. Er rechnet mit einer Welt, die Tempo belohnt.

### Die zwei Formen und das Dazwischen

Die reife Form bremst, wo es sinnvoll ist. Die regressive Form rennt gegen die Wand und fühlt sich dabei wie Mut an. Dazwischen liegt der Normalfall: Du merkst die Bremse und gibst trotzdem Gas.

### Womit du arbeiten kannst

Einmal in der Woche eine Sache absichtlich langsam tun. Nicht tun: alles verschieben. Gut genug ist, es einmal bemerkt zu haben.

### Zeit

Der Prozess läuft vom {m60} bis in den {m330}; die dichten Wochen liegen um die drei Wendepunkte. Diese Frage stand zuletzt an, als du zwölf warst. Eine lange Laufzeit heißt nicht lange Schwere.

## Kapitel 2 · Was leichter wird

**Signatur:** Jupiter im Trigon zu deinem Mond

**Beleg:** Mond ☽ 20°00′ Stier ♉, 2. Haus · T-Jupiter ♃ Trigon △ R-Mond ☽ — exakt {e150}

### Woran du es merkst

Manches geht in diesen Monaten leichter als sonst. Und ein Letztes, das schwerer zuzugeben ist: Es ist dir fast peinlich, wenn etwas ohne Mühe gelingt.

### Was da arbeitet

Der laufende Jupiter steht im Trigon zu deinem Mond im Stier im zweiten Haus. Jupiter weitet, was der Mond braucht, und das Gefühl von Sicherheit wird größer. Das zeigt sich im Alltag daran, dass du weniger festhältst. Ein solcher Transit verspricht nichts; er macht etwas leichter erreichbar.

### Die zwei Formen und das Dazwischen

Genutzt: Du lässt dich tragen, wo es trägt. Verschleudert: Du lässt das Fenster verstreichen, weil nichts drückt. Dazwischen liegt der Normalfall: Du merkst es spät und nimmst es trotzdem.

### Womit du arbeiten kannst

Einmal im Monat etwas annehmen, ohne es zu verdienen. Nicht tun: daraus ein Projekt machen. Gut genug ist, es einmal benutzt zu haben.

### Zeit

Der Kontakt läuft über den {m150} und kommt wieder. Das Fenster schließt nichts.

## Mitlaufendes · Was sonst noch läuft

Hier steht, was im Fenster läuft und kein eigenes Kapitel bekommt.

1. Saturn im Quadrat zu deinem Merkur, bis in den {m190}: das Denken wird vorsichtiger. Klingt mit in Kapitel 1.

2. Neptun im Sextil zu deinem Mars, im {m400}: die Kraft wird weicher.

3. Der Mondknoten in Konjunktion mit deinem Merkur, im {m250}: eine Frage der Richtung im Denken.

## Schlusswort · Was am Ende anders sein könnte

### Was dich durch diese Zeit trägt

In diesen Monaten trägt etwas mit, auch wenn es sich nicht meldet: Jupiter läuft im Trigon zu deinem Mond. Du erkennst es daran, dass weniger Kraft nötig ist als sonst.

### Was erreichbar ist

Du darfst langsamer werden, ohne stehen zu bleiben — und genau dort wächst etwas. Mehr verspricht dieser Text nicht.
"""

def _jd_iso(jd):
    """Kalendertag (gregorianisch, UT) einer Julianischen Tageszahl, als JJJJ-MM-TT."""
    from datetime import date, timedelta
    return (date(2000, 1, 1) + timedelta(days=int(round(jd - 2451544.5)))).isoformat()

def _transit_fall():
    """-> (chart_data, analyse, events) des Transit-Pruefalls. Fensteranfang ist eine
    frei gewaehlte Julianische Tageszahl; alle Daten sind Tage danach."""
    jd0 = 2462867.5
    monate = ("Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August",
              "September", "Oktober", "November", "Dezember")
    tage = (-6000, -2500, 0, 20, 30, 45, 60, 75, 100, 110, 130, 150, 190, 200, 201, 230, 250,
            300, 330, 360, 400, 500, 520, 730)
    d = {n: _jd_iso(jd0 + n) for n in tage}
    werte = {}
    for n, iso in d.items():
        j, mo, t = iso.split("-")
        k = str(n) if n >= 0 else "M%d" % -n
        werte["d" + k] = iso
        werte["e" + k] = "%s.%s.%s" % (t, mo, j)
        werte["m" + k] = "%s %s" % (monate[int(mo) - 1], j)
    werte["dF"] = d[-6000]

    def ev(t, a, z, exakt, stichtag, von, bis, annae=(), primaer=True):
        ex = [d[x] for x in exakt]
        return {"transit": t, "aspekt": a, "ziel": z, "primaer": primaer, "spiegel": False,
                "exakt": ex, "exakt_im_fenster": ex, "exakt_vor_start": [], "exakt_gesamt": ex,
                "exakt_nach_fenster": [], "annaeherung": [[d[x], o] for x, o in annae],
                "fenster_von": d[von], "fenster_bis": d[bis], "weit_von": d[von],
                "weit_bis": d[bis], "perioden": [[d[von], d[bis]]],
                "wirkorb_perioden": [[d[von], d[bis]]], "min_orb_grad": 0.0 if ex else 0.0295,
                "min_orb_im_fenster": 0.0 if ex else 0.0295, "im_wirkorb": True,
                "wirkorb_im_fenster": True, "orb_stichtag": stichtag, "vorlauf": None,
                "fortsetzung": None, "beginn_abgeschnitten": False, "selbst_transit": False,
                "quartale": [1], "kontakte": len(ex), "mehrfach": len(ex) > 1,
                "wird_exakt": bool(ex)}
    events = {
        "start": d[0], "end": d[730], "asof": d[45], "months": 24, "lookback_start": d[0],
        "orb_wirk": 1.5, "orb_weit": 3.0, "zeitzone": "UT", "zusatz": {},
        "events": [ev("Saturn", "Quadrat", "Sonne", (60, 200, 330), 0.5712, 20, 360),
                   ev("Saturn", "Quadrat", "Merkur", (75, 190), 0.9340, 30, 190),   # Wirkorb-Ende = letzter Monat im Register (2026-10-13)
                   ev("Jupiter", "Trigon", "Mond", (150,), 2.3987, 110, 190),
                   ev("Neptun", "Sextil", "Mars", (400,), 2.8810, 300, 520),
                   ev("Knoten", "Konjunktion", "Merkur", (), 1.2034, 200, 300,
                      annae=((250, 0.0295),)),
                   ev("Pluto", "Trigon", "Venus", (500,), 2.9502, 400, 730, primaer=False)],
        "jetzt": {"stichtag": d[45], "orb_weit": 3.0, "orb_wirk": 1.5,
                  "im_orb": [{"transit": "Saturn", "ziel": "Sonne", "aspekt": "Quadrat", "orb_grad": 0.57},
                             {"transit": "Saturn", "ziel": "Merkur", "aspekt": "Quadrat", "orb_grad": 0.93},
                             {"transit": "Knoten", "ziel": "Merkur", "aspekt": "Konjunktion",
                              "orb_grad": 1.2},
                             {"transit": "Jupiter", "ziel": "Mond", "aspekt": "Trigon", "orb_grad": 2.4},
                             {"transit": "Neptun", "ziel": "Mars", "aspekt": "Sextil", "orb_grad": 2.88}]},
        "stations": [{"transit": "Saturn", "datum": d[130], "richtung": "wird rueckl."}],
        "fruehere_durchgaenge": [
            {"transit": "Saturn", "aspekt": "Quadrat", "ziel": "Sonne", "primaer": True,
             "selbst_transit": False,
             "durchgaenge": [{"nr": 1, "von": d[-6000], "bis": d[-6000],
                              "exakt": [{"datum": d[-6000], "alter": 12}], "annaeherung": [],
                              "min_orb_grad": 0.0, "min_orb_datum": d[-6000], "min_orb_alter": 12,
                              "ab_rechenbeginn": False}]}],
    }
    return (_TEST_TRANSIT_CHART.format(**werte), _TEST_TRANSIT_ANALYSE.format(**werte), events,
            werte)

def _selbsttest(still=False):
    """Konstruierte Faelle: Geburtshoroskop fehlerfrei, mit je einem Fehler je Probe,
    mit Zugang-Kapitel; Transit mit events.json fehlerfrei, mit eingebauten Fehlern,
    ohne Kopfblock im Lagebild und ohne events.json; zuletzt (2026-09-19, L7)
    dieselbe Geburts-Analyse in der neuen Form (Wort-Kicker `Getriebe`, `Kapitel n`
    = `THEMA n`) und einmal ohne diesen Kicker. Davor Einzelproben der Muster
    (Zeitform, Superlativ-Fuegung, Rangzeilen-Format wie in radix)."""
    import json
    import tempfile

    def lauf(chart, analyse, events=None, typ=None):
        d = tempfile.mkdtemp(prefix="inhaltsprobe_")
        pa, pc = os.path.join(d, "prueffall_analyse.md"), os.path.join(d, "prueffall_chart_data.md")
        open(pa, "w", encoding="utf-8").write(analyse)
        open(pc, "w", encoding="utf-8").write(chart)
        pe = None
        if events is not None:
            pe = os.path.join(d, "prueffall_Transit_events.json")
            with open(pe, "w", encoding="utf-8") as f:
                json.dump(events, f)
        return pruefe(pa, pc, typ, pe)

    def ersetze(text, alt, neu):
        assert text.count(alt) == 1, "Selbsttest-Marke nicht eindeutig: %r" % alt
        return text.replace(alt, neu)

    def befunde(r):
        return "\n".join(f for p in r["proben"].values() for f in p["fehler"] + p["pruefen"])

    def erwarte(r, erwartet, lauf_name):
        fehlt = []
        for nr, feld, marke in erwartet:
            treffer = r["proben"][nr][feld]
            if not any(marke in t for t in treffer):
                fehlt.append("%s: erwartet %s mit „%s“, gefunden: %s"
                             % (nr, feld.upper(), marke, treffer or "nichts"))
        assert not fehlt, "%s — eine Probe findet ihren Testfehler nicht:\n  %s" % (
            lauf_name, "\n  ".join(fehlt))

    berichte = []
    # 0) Einzelproben der Muster (2026-09-19)
    for satz, soll in (("Er hat dich oft geschützt.", True), ("Das war einmal so.", True),
                       ("Der Teil, der das eingerichtet hat, schützt dich.", True),
                       ("Er hat einen verlässlichen Instinkt.", False),
                       ("Er hat nichts zu verlieren.", False),
                       ("Er hat ein gutes Argument: Wer zuerst geht, muss nicht warten.", False)):
        assert bool(_zeitform_treffer(satz, "de")) == soll, "W4 Zeitform: %r" % satz
    for satz, soll in (("It has spared you many battles.", True), ("It spares you many battles.", False),
                       ("It knows what you need.", False), ("This order made everything possible.", True)):
        assert bool(_zeitform_treffer(satz, "en")) == soll, "W4 Zeitform (englisch): %r" % satz
    for satz, soll in (("Dein Gefühl fließt zum tiefsten Punkt.", False),
                       ("Zum tiefsten Punkt dagegen führt nichts.", False),
                       ("Am tiefsten Punkt deines Horoskops steht der Mond.", False),
                       ("Der tiefste Punkt deines Lebens liegt nicht hier.", True),
                       ("Was am tiefsten liegt, meldet sich zuletzt.", True)):
        assert bool(SUPERLATIV_RE.search(satz)) == soll, "W29 Superlativ: %r" % satz
    # P13-Satzformen (2026-09-23): Aufzaehlung, Relativsatz, Achsenpaar, Zusatz-Segment
    def _p13_paare(satz):
        return {frozenset((x, y)) for d, _a, n, _m in _konstellationen(satz)
                for x in d for y in n if x != y}
    for satz, soll in (
            ("Dein Mond hat ein Trigon zu Saturn und ein Quadrat zu Mars.",
             {("MOND", "SATURN"), ("MOND", "MARS")}),
            ("Dein Mars steht im Quadrat zu Pluto, im Trigon zu Jupiter und im Sextil zu Venus.",
             {("MARS", "PLUTO"), ("MARS", "JUPITER"), ("MARS", "VENUS")}),
            ("Dein Merkur steht im Trigon zum Mond, der seinerseits Saturn quadriert.",
             {("MERKUR", "MOND")}),
            ("Uranus steht im Quadrat zur Sonne, und Pluto trägt das Trigon zum Mond.",
             {("URANUS", "SONNE"), ("PLUTO", "MOND")}),
            ("Sonne und Venus stehen im Quadrat zu Mars.",
             {("SONNE", "MARS"), ("VENUS", "MARS")})):
        ist = _p13_paare(satz)
        assert ist == {frozenset(p) for p in soll}, "P13 Satzform: %r -> %r" % (satz, ist)
    assert frozenset(("DC", "AC")) in _ACHSENPAARE and frozenset(("MC", "IC")) in _ACHSENPAARE
    # 2026-09-29 (K6): „öffnet dir eine Tür zu“ ist ein Sextil-Bild
    assert _p13_paare("Dein Mars öffnet dir eine Tür zu deiner Venus.") == \
        {frozenset(("MARS", "VENUS"))}, "K6: Sextil-Bild"
    # 2026-09-30 (K4): das Sextil-Bild auch gebeugt
    for _s, _soll in (("Mond und Saturn öffnen einander eine Tür.", ("MOND", "SATURN")),
                      ("Deiner Venus öffnet sich von Jupiter her eine Tür.", ("VENUS", "JUPITER")),
                      ("Deinem Merkur öffnet sich eine Tür zu deinem Uranus.",
                       ("MERKUR", "URANUS"))):
        assert frozenset(_soll) in _p13_paare(_s), "K4 Sextil-Bild gebeugt: %r -> %r" % (
            _s, _p13_paare(_s))
    assert not _p13_paare("Wenn du das zulässt, öffnet sich eine Tür."), "K4: ohne Faktor still"
    # 2026-09-30 (K2): weitere Paarungen einer sonst ungedeckten Konstellation (19)
    def _w13(satz, marker, davor, danach, typ=None, vorher="", transiter=()):
        m_ = next(x for x in ASPEKT_RE.finditer(satz) if x.group(0) == marker) \
            if marker != "über" else _UEBER_RE.search(satz)
        return _p13_weitere_paare(satz, m_, davor, danach, typ, vorher, transiter)
    assert ("VENUS", "JUPITER") in _w13("Beim Mars ist das gedeutet, das Trigon der Venus zu "
                                        "Jupiter im Register.", "Trigon", ["MARS"],
                                        ["VENUS", "JUPITER"]), "K2 (a) Genitiv"
    assert ("SATURN", "SATURN") in _w13("Saturns Quadrat zu sich selbst wiederholt sich im "
                                        "Fenster zweimal.", "Quadrat", ["SATURN"], ["URANUS"],
                                        "transit"), "K2 (b) zu sich selbst"
    assert ("SATURN", "SATURN") not in _w13("Saturns Quadrat zu sich selbst wiederholt sich "
                                            "im Fenster zweimal.", "Quadrat", ["SATURN"],
                                            ["URANUS"]), "K2 (b) nur im Transit"
    _s13 = ("Saturn stand deiner Venus gegenüber, dann im Quadrat zu deinem Mond und "
            "zuletzt im Quadrat zu deinem Pluto.")
    _m13 = [x for x in ASPEKT_RE.finditer(_s13)][-1]
    assert ("SATURN", "PLUTO") in _p13_weitere_paare(_s13, _m13, ["MOND"], ["PLUTO"], "transit"), \
        "K2 (c) Folge: das Subjekt traegt weiter"
    assert ("URANUS", "MERKUR") in _w13("Er reibt sich an deiner Sonne und steht im Sextil zu "
                                        "deinem Merkur.", "Sextil", ["SONNE"], ["MERKUR"],
                                        "transit", "Uranus läuft durch dein drittes Haus."), \
        "K2 (c) Pronomen am Satzanfang"
    assert ("MONDKNOTEN", "MARS") in _w13(
        "Und der Mondknoten, der rückläufig durch dein fünftes Haus zieht, steht von Juni bis "
        "Dezember im Quadrat zu deiner Sonne und deinem Jupiter und geht im Januar über deinen "
        "Mars.", "über", ["SONNE", "JUPITER"], ["MARS"], "transit"), "K2 (c) Artikel-Subjekt"
    assert _p13_satzsubjekt("Das Quadrat zwischen Mond und Mars ist beim Mond gedeutet, "
                            "das Sextil der Venus zu Jupiter im Register.", 200) == [], \
        "K2 (c) Objekte hinter „zwischen“ und „beim“ sind kein Subjekt"
    assert ("SATURN", "NEPTUN") in _w13("Im Herbst wird das Quadrat zu deinem MC genau, wenige "
                                        "Tage später das Trigon zu deinem Neptun.",
                                        "Trigon", ["MC"], ["NEPTUN"], "transit", "",
                                        ("SATURN",)), "K2 (d) Transiter des Kapitels"
    assert _w13("Dazu kommt Pluto im Quadrat zu deiner Sonne.", "Quadrat", ["PLUTO"],
                ["SONNE"], "transit", "", ("SATURN",)) == [], \
        "K2 (c)/(d) nicht, wenn vor dem Marker ein eigenes Subjekt steht"
    _t13 = [{"a": "VENUS", "b": "JUPITER", "art": "Sextil"}, {"a": "MOND", "b": "MARS",
                                                              "art": "Quadrat"}]
    _k13 = {"kicker": "Rechenschaft", "title": "T", "signatur": "", "beleg": "",
            "blocks": [{"type": "para", "text": "Das Quadrat zwischen Mond und Mars ist beim "
                        "Mond gedeutet, das Sextil der Venus zu Jupiter im Register."}]}
    _p13k = _p13_beleg_deckung([_k13], "geburt", _t13, "")
    assert _p13k.status == "OK", ("K2 Genitiv im Lauf", _p13k.status, _p13k.pruefen)
    _t13b = [{"a": "VENUS", "b": "JUPITER", "art": "Trigon"}, {"a": "MOND", "b": "MARS",
                                                               "art": "Quadrat"}]
    _p13k = _p13_beleg_deckung([_k13], "geburt", _t13b, "")
    assert _p13k.status == "PRUEFEN", ("K2: falsche Art bleibt gemeldet", _p13k.pruefen)
    # 2026-09-23b: Pronomen mit Genus (a), Subjekt-Pronomen vor Objekt-Faktoren (b),
    # neues Glied hinter Komma (5)
    def _p13_mit_vorsatz(satz, vorher):
        return {frozenset((x, y)) for d, _a, n, _m in _konstellationen(satz, vorher)
                for x in d for y in n if x != y}
    _ist = _p13_mit_vorsatz("Sie verschmilzt mit Merkur, und so findet dein Lieben Worte.",
                            "Deine Venus steht im Trigon zu Jupiter.")
    assert frozenset(("VENUS", "MERKUR")) in _ist, "P13 Genus (a): %r" % _ist
    _ist = _p13_mit_vorsatz("Es verschmilzt mit Merkur.", "Deine Venus steht im Trigon zu Jupiter.")
    assert _ist == {frozenset(("JUPITER", "MERKUR"))}, "P13 (a), es ohne Genus-Treffer: %r" % _ist
    _ist = _p13_mit_vorsatz("Er läuft über deinen Aszendenten und steht dabei im Quadrat zu "
                            "deinem Uranus und im Trigon zu deiner Sonne.",
                            "Saturn wandert ab dem Frühjahr durch dein erstes Haus.")
    assert {frozenset(("SATURN", "URANUS")), frozenset(("SATURN", "SONNE"))} <= _ist, \
        "P13 Subjekt-Pronomen (b): %r" % _ist
    _ist = _p13_mit_vorsatz("Dein Merkur steht im Trigon zum Mond, der seinerseits Saturn "
                            "quadriert.", "Er denkt schnell.")
    assert _ist == {frozenset(("MERKUR", "MOND"))}, "P13 (b) greift ohne Pronomen: %r" % _ist
    _ist = _p13_paare("Saturn steht dabei im Quadrat, der Mondknoten im Trigon zu deiner Venus.")
    assert _ist == {frozenset(("MONDKNOTEN", "VENUS"))}, "P13 neues Glied (5): %r" % _ist
    _ist = _p13_paare("Saturn trifft deinen Mars im Quadrat, der Mondknoten deine Venus im Trigon.")
    assert _ist == {frozenset(("SATURN", "MARS")), frozenset(("MONDKNOTEN", "VENUS"))}, \
        "P13 neues Glied (5), Partner davor: %r" % _ist
    # Zweitleser 2026-09-23b: keine neuen Paare bei leerem danach, Relativsatz und
    # Apposition bleiben, wie sie waren
    for _s, _v in (("Er bildet dabei mit deinem Mond ein Quadrat.",
                    "Saturn läuft ab März über deinen Aszendenten."),
                   ("Er bildet dabei ein Quadrat.",
                    "Saturn wandert durch dein viertes Haus, in dem auch Pluto steht."),
                   ("Saturn wandert mit Pluto weiter, und er steht deinem Mond gegenüber.", "")):
        assert _p13_mit_vorsatz(_s, _v) == set(), "P13 leeres danach: %r" % _s
    for _s, _soll in (("Saturn bildet ein Quadrat, das deinen Mond trifft, und ein Trigon "
                       "zu deiner Venus.", {("SATURN", "MOND"), ("SATURN", "VENUS")}),
                      ("Uranus bildet ein Quadrat zu deinem Lebenslicht, der Sonne, und ein "
                       "Trigon zum Mond.", {("URANUS", "SONNE"), ("URANUS", "MOND")})):
        _ist = _p13_paare(_s)
        assert {frozenset(p) for p in _soll} <= _ist, "P13 (5) zu weit: %r -> %r" % (_s, _ist)
    _ist = _p13_mit_vorsatz("Sie bilden gemeinsam ein Quadrat zu deiner Sonne.",
                            "Mars und Saturn stehen in deinem zehnten Haus.")
    assert frozenset(("SATURN", "SONNE")) in _ist, "P13 Plural-Sie: %r" % _ist
    # 2026-09-23c (6): das Satzanfangs-Pronomen traegt nicht in einen Relativsatz,
    # (7): Selbstpaar nur bei einem Transiter; konstruierte Saetze
    _v6 = "Merkur ist der Planet, bei dem alles zusammenläuft: Er verwaltet deine Sonne."
    _s6 = ("Er ist zugleich die Spitze einer Figur, in der dein Mond und die Ballung aus "
           "Venus und Saturn im Sextil stehen und beide im Quincunx zu Merkur.")
    assert not [d for d, a, _n, _m in _konstellationen(_s6, _v6) if a == "Quincunx"], \
        "P13 (6): Pronomen im Relativsatz"
    _ist = _p13_mit_vorsatz("Er, der durch dein zwölftes Haus läuft, bildet ein Quadrat zu "
                            "deiner Venus.", "Saturn wandert ab März weiter.")
    assert frozenset(("SATURN", "VENUS")) in _ist, "P13 (6) greift trotz Komma: %r" % _ist
    assert not _paar_ok("MERKUR", "MERKUR", "transit") and _paar_ok("SATURN", "SATURN", "transit") \
        and not _paar_ok("SATURN", "SATURN", "geburt") and not _paar_ok("AC", "DC", "transit"), \
        "P13 (7) Selbstpaar"
    # (10), 2026-09-25 (T20): Selbstpaar nur mit Radix-Marke auf genau einer Seite
    assert not _selbstpaar_im_satz("T-Uranus △ R-Saturn — im Trigon zu deinem Saturn.", "SATURN") \
        and not _selbstpaar_im_satz("Er steht Chiron gegenüber, Chiron in den Zwillingen.", "CHIRON") \
        and _selbstpaar_im_satz("Saturn steht im Quadrat zu deinem Saturn.", "SATURN") \
        and _selbstpaar_im_satz("Er steht im Quadrat zu deinem Saturn.", "SATURN"), "P13 (10) Selbstpaar"
    # 2026-10-01 (Pruefbericht Geburtshoroskop 1+2 vom 30.09., K1): (3) Knotenachse,
    # (20) Marker im Relativsatz, (21) Gruppe vor „und + Praedikat“, (22) „zu ihm“ am
    # ersten Marker — konstruierte Saetze nach den gemeldeten
    assert not _paar_ok("MONDKNOTEN", "SUEDKNOTEN", "geburt"), "P13 (3) Knotenachse"
    _ist = _p13_paare("Pholus, der hier im Trigon mitklingt, steht in "
                      "Kapitel 4 Mars gegenüber.")
    assert frozenset(("PHOLUS", "MARS")) not in _ist, "P13 (20): %r" % _ist
    _ist = _p13_paare("Dein Mond, der im Trigon zu Venus steht, reibt sich an Saturn.")
    assert frozenset(("MOND", "VENUS")) in _ist, "P13 (20) zu weit: %r" % _ist
    _k21 = [(a, frozenset((x, y))) for d, a, n, _m in _konstellationen(
        "Venus und Uranus bilden ein Sextil und zeigen gemeinsam auf deinen Mars, beide im "
        "Quincunx zu ihm.") for x in d for y in n if x != y]
    assert set(_k21) == {("Sextil", frozenset(("VENUS", "URANUS"))),
                         ("Quincunx", frozenset(("MARS", "VENUS"))),
                         ("Quincunx", frozenset(("MARS", "URANUS")))}, "P13 (21): %r" % _k21
    _ist = _p13_paare("Saturn steht im Quadrat und trifft deinen Mars.")
    assert _ist == {frozenset(("SATURN", "MARS"))}, "P13 (21) nur mit Gruppe: %r" % _ist
    _ist = _p13_mit_vorsatz("Und Venus und Jupiter stehen beide im Quincunx zu ihm.",
                            "Dein Mars ist das Zentrum.")
    assert _ist == {frozenset(("VENUS", "MARS")), frozenset(("JUPITER", "MARS"))}, \
        "P13 (22): %r" % _ist
    assert _p13_mit_vorsatz("Venus und Jupiter stehen beide im Quincunx zu ihm.", "") == set(), \
        "P13 (22) ohne Vorsatz"
    # 2026-10-01b (23): ein angereihtes Glied ist Objekt — (19) findet den Transiter
    _s23 = ("Dann kommt im Winter die Reibung an Venus und Pluto, mit einem zweiten "
            "Stillstand nahe am Quadrat zu deinem Pluto.")
    _m23 = [x for x in ASPEKT_RE.finditer(_s23) if x.group(0) == "Quadrat"][0]
    assert ("SATURN", "PLUTO") in _p13_weitere_paare(_s23, _m23, ["VENUS", "PLUTO"],
                                                     ["PLUTO"], "transit", "", ("SATURN",)), \
        "P13 (23): Reihe hinter „an“"
    _s23s = ("Pluto reibt sich an deinem Merkur und Chiron, mit einem Stillstand nahe am "
             "Quadrat zu deiner Sonne.")
    _m23s = [x for x in ASPEKT_RE.finditer(_s23s) if x.group(0) == "Quadrat"][0]
    assert ("SATURN", "SONNE") not in _p13_weitere_paare(_s23s, _m23s, ["MERKUR", "CHIRON"],
                                                         ["SONNE"], "transit", "", ("SATURN",)), \
        "P13 (23): eigenes Subjekt — der Transiter des Kapitels deckt nicht"
    _s23k = "Saturn steht im Trigon zu deiner Sonne, Mars im Quadrat zu deiner Venus."
    _m23k = [x for x in ASPEKT_RE.finditer(_s23k) if x.group(0) == "Quadrat"][0]
    assert not _p13_nur_objekte(_s23k, _m23k, ["SONNE", "MARS"]), \
        "P13 (23): ein Komma allein reiht nicht an"
    for _s23e in ("Saturn steht im Quadrat zu deinem Merkur und Pluto im Quadrat zu "
                  "deiner Sonne.", "Der Druck liegt auf deinem Mond, und Pluto steht im "
                  "Quadrat zu deiner Sonne."):
        _m23e = [x for x in ASPEKT_RE.finditer(_s23e) if x.group(0) == "Quadrat"][-1]
        assert not _p13_nur_objekte(_s23e, _m23e, ["PLUTO"]), \
            "P13 (23): Ellipse/neuer Hauptsatz bleibt Subjekt: %r" % _s23e
    # 2026-10-01b (24): die Herrschaftsformel ist kein Konjunktionsbild
    assert not _konstellationen("Saturn ist in deinem Bild der Planet, der über deinem "
                                "Merkur steht.", typ="transit"), "P13 (24) Herrschaftsformel"
    assert [k for k in _konstellationen("Jupiter, der jetzt über deiner Venus steht, wird "
                                        "langsamer.", typ="transit")
            if k[3].group(0) == "über"], "P13 (24): ohne „Planet“ bleibt „über“ Bild"
    assert [k for k in _konstellationen("Jupiter ist der Planet, der ab März über deiner "
                                        "Venus steht.", typ="transit")
            if k[3].group(0) == "über"], "P13 (24): mit Zeitangabe bleibt „über“ Bild"
    _k24b = _konstellationen("Pluto ist der Planet, der über deinem Merkur steht, und steht "
                             "zugleich im Quadrat zu deiner Sonne.", typ="transit")
    assert [(d, n) for d, _a, n, _m in _k24b] == [(["PLUTO"], ["SONNE"])], \
        "P13 (24): das Subjekt traegt ueber die Herrschaftsformel weiter: %r" % _k24b
    _k24 = _konstellationen("Saturn, der Planet, der über deinem Merkur steht, bildet ein "
                            "Quadrat zu Mars.", typ="transit")
    assert [(d, n) for d, _a, n, _m in _k24] == [(["SATURN"], ["MARS"])], \
        "P13 (24): der beherrschte Faktor ist kein Partner: %r" % _k24
    # P11 (2026-10-01b, Gegenpruefung): „-jährig“ gross/vor Person bleibt Alter,
    # Zusatzwoerter vor jedem Glied der Reihe
    for _s11, _soll in (("als Zwölfjähriger Verantwortung zu tragen", 12),
                        ("dein zwölfjähriges Ich", 12), ("als zwölfjähriger Sohn", 12)):
        assert [_zahl_wert(m_.group("n")) for rx in _P11_ALTER for m_ in rx.finditer(_s11)] \
            == [_soll], "P11 -jährig als Alter: %r" % _s11
    assert not [m_ for rx in _P11_ALTER for m_ in rx.finditer("im zwölfjährigen Umlauf")], \
        "P11 -jährig als Dauer"
    _gl = [_P11_Q_RE.sub("", g_.strip(), count=1).strip() for m_ in _P11_ALTER_LISTE.finditer(
        "als du gut zwölf und knapp vierundzwanzig warst")
        for g_ in _P11_LISTE_TRENNER.split(m_.group("liste"))]
    assert [_zahl_wert(g_) for g_ in _gl] == [12, 24], "P11 Reihe mit Zusatzwort: %r" % _gl
    # 2026-10-01: P11 meldet Saetze zur Geburtsminute, ausser EINEM im Auftakt bei
    # faelligem Gegenprobe-Blatt
    def _gm(kicker, saetze, txt_gm=""):
        _pr = _Probe("P11", "Zahlen-Deckung")
        _p11_geburtsminute(_pr, [{"kicker": kicker, "title": "T", "blocks": [
            {"type": "p", "text": t} for t in saetze]}], txt_gm)
        return len(_pr.pruefen)
    _gm_ja = ("Dein Aszendent liegt so nah an einer Zeichengrenze, dass das beiliegende "
              "Blatt dir hilft, selbst zu prüfen, welches Zeichen zu dir passt.",
              "Bei knapp zwei Minuten früherer Geburt läge die Himmelsmitte im Krebs.",
              "Wärst du zwei Minuten früher geboren, stünde Saturn im zwölften Haus.",
              "Welches der beiden Häuser führt, kann die Geburtszeit nicht entscheiden.")
    _gm_nein = ("Notiere, was zehn Minuten später noch da ist.",
                "Aus früheren Geburten bringst du dieses Thema nicht mit.")
    assert _gm("Hauptthemen", _gm_ja[1:] + _gm_nein) == 3, "P11 Geburtsminute"
    assert _gm("Auftakt", _gm_ja[1:2], "- Zeitscan · AC: … Gegenprobe-Blatt fällig") == 0 \
        and _gm("Auftakt", _gm_ja[1:3], "Gegenprobe-Blatt fällig") == 1 \
        and _gm("Auftakt", _gm_ja[1:2]) == 1, "P11 Geburtsminute im Auftakt"
    # 2026-09-23c: P5 nimmt die Registerzeile mit dem richtigen Ziel
    _zl = ["Jupiter im Trigon zu deinem MC — der Weg nach außen zeigt sich (Kapitel 2).",
           "Mondknoten im Sextil zu deinem Jupiter — klingt mit in Kapitel 3.",
           "Jupiter im Sextil zu deinem Mondknoten — klingt mit in Kapitel 7.",
           "Jupiter im Trigon zu deinem Jupiter — klingt mit in Kapitel 2.",
           "Mondknoten im Sextil zu deinem MC — der Knoten zeigt nach außen.",
           "Mondknoten im Sextil zu deinem Mondknoten — klingt mit in Kapitel 7.",
           "Saturn-Rückkehr — klingt mit in Kapitel 4.",
           "Jupiter im Sextil zur Venus, der Herrscherin deines Aszendenten — Kapitel 3.",
           "Neptun im Trigon zu deinem natalen Mond und deiner Venus — Kapitel 5.",
           "Saturn □ R-Mond, dazu deine Sonne im Blick — Kapitel 6.",
           "Mondknoten über deinem Südknoten — die Knoten tauschen die Plätze.",
           "Jupiter im Trigon — neue Wege zeigen sich (Kapitel 2).",
           "Saturn im Quadrat zu deiner Sonne und Venus — Kapitel 4."]
    for _k, _soll in ((("JUPITER", "Sextil", "MONDKNOTEN"), 2),
                      (("MONDKNOTEN", "Sextil", "JUPITER"), 1),
                      (("JUPITER", "Trigon", "JUPITER"), 3),
                      (("MONDKNOTEN", "Sextil", "MONDKNOTEN"), 5),
                      (("JUPITER", "Trigon", "MC"), 0),
                      (("SATURN", "Konjunktion", "SATURN"), 6),
                      (("JUPITER", "Sextil", "VENUS"), 7),
                      (("NEPTUN", "Trigon", "MOND"), 8),
                      (("SATURN", "Quadrat", "MOND"), 9),
                      (("MONDKNOTEN", "Opposition", "MONDKNOTEN"), 10)):
        assert _registerzeile(_k, _zl) == _zl[_soll], "P5 Registerzeile: %r -> %r" % (
            _k, _registerzeile(_k, _zl))
    assert _registerzeile(("SATURN", "Quadrat", "VENUS"), _zl) == _zl[12], "P5 zweites Ziel"
    assert _registerzeile(("JUPITER", "Trigon", "JUPITER"), _zl[11:12]) is None, \
        'P5: „zeigen" gilt nicht als „eigen"'
    _ist = _p13_mit_vorsatz("Er öffnet ein Feld, in dem im Sextil zu deiner Venus und im "
                            "Trigon zu deinem Mars zwei Wege liegen.",
                            "Jupiter wandert ab dem Frühjahr weiter.")
    assert frozenset(("VENUS", "MARS")) not in _ist, "P13 (6) + Aufzählung (1): %r" % _ist
    # 2026-09-24: (8) Aufzaehlung ohne Subjekt, (9) Nebensatz; konstruierte Saetze
    _ist = _p13_paare("Dein Mars arbeitet leise; er steht im Trigon zu Saturn und im Trigon "
                      "zu Neptun.")
    assert frozenset(("SATURN", "NEPTUN")) not in _ist, "P13 (8) Aufzählung ohne Subjekt: %r" % _ist
    _s9 = ("Er läuft im Trigon zu deinem Mond — ein ruhiger Weg — und gibt deiner Venus ein "
           "Sextil, während Mond und Venus sich gegenüberstehen.")
    _v9 = "Jupiter wandert ab dem Sommer weiter."
    assert not [1 for d, a, n, _m in _konstellationen(_s9, _v9) if a == "Sextil"
                and "MOND" in set(d) | set(n)], "P13 (9) Nebensatz"
    assert frozenset(("JUPITER", "MOND")) in _p13_mit_vorsatz(_s9, _v9), "P13 (9) schneidet zu früh"
    assert _p13_paare("Dein Mars steht im Quadrat zu Saturn, während dein Mond ruhig bleibt.") == \
        {frozenset(("MARS", "SATURN"))}, "P13 (9) Hauptsatz vor dem Nebensatz"
    assert frozenset(("MARS", "SATURN")) not in _p13_paare(
        "Mars und Saturn stehen beide im Quadrat, weil Pluto sie trifft."), \
        "P13 (9) Nachstellung paart nach dem Schnitt nach vorn"
    assert frozenset(("SATURN", "URANUS")) in _p13_paare(
        "Dein Saturn steht im Quincunx, wenn man so will, zu deinem Uranus."), \
        "P13 (9) Spanne endet am Komma"
    assert {frozenset(("MARS", "VENUS")), frozenset(("MARS", "JUPITER"))} <= _p13_paare(
        "Dein Mars steht im Trigon sowohl zu Venus, als auch zu Jupiter."), \
        "P13 (9) „als auch“ ist kein Nebensatz"
    assert _p13_paare("Dein Mars steht sowohl im Trigon zu Venus, als auch im Sextil zu "
                      "Jupiter.") == {frozenset(("MARS", "VENUS")), frozenset(("MARS", "JUPITER"))}, \
        "P13 (1) „als auch“ reiht auf"
    # 2026-09-30 (K1): P12 — Glied des Rangworts, leerer Bereich (§8), Haus im eigenen
    # Haus (§3), Genitiv des Elements, Zeitspanne; konstruierte Werte
    _txt30 = ("### 3 · Herrscherketten, Rezeption, Hausherrscher\n"
              "- Hausherrscher (Spitzenzeichen → Herrscher → wo er steht; die vier "
              "Sonderfälle des Typmoduls stehen hinter ⟵):\n"
              "  - Haus  2 (Stier) → Venus in Stier, Haus 2  ⟵ im eigenen Haus\n"
              "  - Haus  3 (Zwillinge) → Merkur in Krebs, Haus 4\n"
              "### 8 · Verteilung (zehn klassische Planeten)\n"
              "- Quadranten: I (Häuser 1–3) 4 · II (Häuser 4–6) 3 · III (Häuser 7–9) 0 · "
              "IV (Häuser 10–12) 3\n"
              "- Betonung: Quadrant I (4 von 10) ⟵ betont; Quadrant III ⟵ leer.\n"
              "### 10 · Rangzeilen\n"
              "- RANG elemente-gezaehlt [zehn Planeten]: 1. Erde 4 von 10 = 40 % (Saturn, "
              "Venus, Mars, Jupiter) · 2. Wasser 3 von 10 = 30 % (Mond, Neptun, Pluto) · 3. Luft "
              "2 von 10 = 20 % (Merkur, Uranus) · 4. Feuer 1 von 10 = 10 % (Sonne)\n"
              "- RANG modi-gezaehlt [zehn Planeten]: 1. veränderlich 5 von 10 = 50 % (Merkur, "
              "Mars, Jupiter, Saturn, Neptun) · 2. fix 3 von 10 = 30 % (Sonne, Venus, Pluto) · "
              "3. kardinal 2 von 10 = 20 % (Mond, Uranus)\n"
              "- RANG verbindungen-gezaehlt [je 1]: 1. Jupiter 9 · 2. Saturn 8 · 3. Mond 6\n"
              "- RANG verbindungen-gewichtet [voll 1]: 1. Jupiter 5.5 · 1. Saturn 5.5 · "
              "3. Mond 4\n")
    _st30 = _struktur_p12(_txt30)
    assert _st30 == {"leer": {"Quadrant III"}, "eigenes_haus": {2: "Venus"}}, _st30

    def _p12_satz30(satz, vorher=""):
        out = []
        for art, rx in _RANG_MUSTER:
            for m_ in rx.finditer(satz):
                b = _rang_befund(art, m_, satz, _rangzeilen_lesen(_txt30), "geburt", vorher,
                                 eigen=_eigenes_zeichen(_txt30), struktur=_st30)
                if b:
                    out.append((art, b))
        return out
    for _s in ("Erde, Wasser und Luft tragen, gezählt, neun Planeten; die Hälfte aller "
               "Planeten steht in der Kraft, sich anzupassen.",
               "Die meisten Verbindungen hat, gezählt über alle Faktoren, dein Jupiter, dicht "
               "gefolgt von Saturn; gewichtet liegen beide gleichauf.",
               "Die Häuser sieben bis neun tragen keinen einzigen Planeten.",
               "Unter den Planeten ist deine Sonne der einzige Träger des Feuers.",
               "Dein zweites Haus verwaltet sich aus sich heraus und ist dafür auf keinen "
               "anderen angewiesen.",
               "Die nächsten zwei Jahre Verbindungen zu pflegen, lohnt sich."):
        assert _p12_satz30(_s) == [], "K1 P12: %r -> %r" % (_s, _p12_satz30(_s))
    for _s in ("Die Häuser zehn bis zwölf tragen keinen einzigen Planeten.",
               "Dein drittes Haus verwaltet sich aus sich heraus und ist dafür auf keinen "
               "anderen angewiesen.",
               "Erde, Wasser und Luft tragen, gezählt, neun Planeten; die Hälfte aller "
               "Planeten steht in der Kraft, anzufangen.",
               "Die meisten Verbindungen, gezählt über alle Faktoren, hat dein Saturn."):
        assert _p12_satz30(_s), "K1 P12 muss melden: %r" % _s
    # 2026-09-24: P12 — §3 als Fundstelle, Umlaufzeit, Verbindungs-Rangzeile
    _txt12 = ("- Enddispositoren (im eigenen Zeichen, und eine fremde Kette endet bei ihm): "
              "Saturn (Ketten von Sonne, Mond).\n"
              "- Im eigenen Zeichen ohne Zulauf (folgt keinem anderen, aber keine fremde Kette "
              "endet bei ihm — kein Enddispositor): Venus.\n"
              "- RANG verbindungen-gewichtet [voll 1]: 1. Merkur 4 · 2. Saturn 3\n"
              "- RANG verbindungen-gezaehlt [je 1]: 1. Saturn 5 · 2. Merkur 4\n"
              "- RANG elemente-gezaehlt [zehn Planeten]: 1. Erde 4 von 10 = 40 % (Saturn, Venus, "
              "Mars, Jupiter) · 2. Luft 1 von 10 = 10 % (Merkur)\n")
    assert _eigenes_zeichen(_txt12) == {"SATURN", "VENUS"}, _eigenes_zeichen(_txt12)
    assert _eigenes_zeichen("- RANG verbindungen-gezaehlt [je 1]: 1. Saturn 5") is None, \
        "P12 §3 fehlt: None"
    _rz12, _eig12 = _rangzeilen_lesen(_txt12), _eigenes_zeichen(_txt12)

    def _p12_satz(satz, vorher="", eigen=_eig12, txt_rz=_rz12):
        out = []
        for art, rx in _RANG_MUSTER:
            for m_ in rx.finditer(satz):
                b = _rang_befund(art, m_, satz, txt_rz, "geburt", vorher, eigen=eigen)
                if b:
                    out.append((art, b))
        return out
    assert _p12_satz("Saturn ist neben Venus der Planet, der keinem anderen folgt.") == [], \
        "P12 §3 gedeckt"
    assert _p12_satz("Er ist der Planet, der keinem anderen folgt, wie sonst nur deine Venus.",
                     "Saturn steht im Steinbock.") == [], "P12 §3 mit Vorsatz"
    assert [a for a, _b in _p12_satz("Saturn ist der Planet, der keinem anderen folgt.")] == \
        ["kein_anderer"], "P12 §3: zweite Endstelle ungenannt muss PRÜFEN bleiben"
    assert [a for a, _b in _p12_satz("Er ist der Planet, der keinem anderen folgt.",
                                     "Saturn steht im Trigon zu deiner Venus.")] == \
        ["kein_anderer"], "P12 §3: das Pronomen meint nur Saturn, nicht Venus"
    assert [a for a, _b in _p12_satz("Saturn folgt keinem anderen, und in der Luft steht kein "
                                     "anderer Planet als er.", eigen={"SATURN"})] == \
        ["kein_anderer"], "P12 §3 gilt nur für den Treffer mit „folgt“"
    assert _p12_satz("Jupiter kehrt alle zwölf Jahre an seinen Platz zurück, ein Planet "
                     "mit weitem Weg.") == [], "P12 Umlaufzeit"
    assert [a for a, _b in _p12_satz("Alle vier Planeten der Erde stehen im zehnten Haus.")] == \
        ["alle_n"], "P12 alle n ohne Zeitangabe bleibt"
    assert _p12_satz("Gewichtet ist dein Merkur der am dichtesten verschaltete Faktor deines "
                     "Bildes, und die Luft in dir hat keinen anderen Planeten als ihn.") == [], \
        "P12 Verbindungs-Rangzeile trotz Element im Satz"
    # 2026-09-29 (Klasse-2-Entscheidungslauf K1): P12-Satzformen der Pruefberichte
    _txt29 = ("- RANG verbindungen-gewichtet [voll 1]: 1. Sonne 6.5 · 2. Merkur 4 · 3. Lilith 1.5\n"
              "- RANG verbindungen-gezaehlt [je 1]: 1. Merkur 8 · 2. Sonne 7 · 3. Lilith 2\n"
              "- RANG modi-gezaehlt [zehn Planeten]: 1. kardinal 5 von 10 = 50 % (Sonne, Mond, "
              "Merkur, Venus, Mars) · 2. veränderlich 4 von 10 = 40 % (Jupiter, Saturn, Uranus, "
              "Neptun) · 3. fix 1 von 10 = 10 % (Pluto)\n"
              "- RANG modi-gewichtet [Lichter ×2]: 1. kardinal 7 von 12 = 58 % (Sonne ×2, Mond ×2, "
              "Merkur, Venus, Mars) · 2. veränderlich 4 von 12 = 33 % (Jupiter, Saturn, Uranus, "
              "Neptun) · 3. fix 1 von 12 = 8 % (Pluto)\n"
              "- RANG elemente-gewichtet [Lichter ×2]: 1. Luft 5.5 von 10.5 = 52 % (Sonne, Mond, "
              "Merkur, Venus, Mars) · 2. Wasser 5 von 10.5 = 47 % (Jupiter, Saturn, Uranus, "
              "Neptun, Pluto)\n")
    _rz29 = _rangzeilen_lesen(_txt29)
    for _s, _v in (("Gewichtet gezählt, hat deine Sonne die meisten Verbindungen.", ""),
                   ("Gewichtet, hat deine Sonne die meisten Verbindungen.", ""),
                   ("Die Kraft, zu halten, trägt ein einziger Planet, Pluto.", ""),
                   ("Fast die Hälfte deiner Kräfte steht im Wasser, gewichtet gezählt.", ""),
                   ("Ihre einzigen Verbindungen führen zur Sonne und zu Jupiter.",
                    "Deine Lilith steht im Skorpion."),
                   ("Es ist eine einzige Figur, nicht zwei.", ""),
                   ("Alle vier Ecken stehen in fixen Zeichen.", "")):
        assert _p12_satz(_s, _v, txt_rz=_rz29) == [], "K1 P12: %r" % _s
    # 2026-10-01 (K1): Rang in einer Teilmenge still, Gesamtmenge weiter geprueft
    assert _p12_satz("Unter den Gliedern dieser Gruppe trägt Lilith, gewichtet gezählt, die "
                     "meisten Verbindungen.", txt_rz=_rz29) == [], \
        "P12 Teilmenge"
    assert [a for a, _b in _p12_satz("Unter allen Planeten hat Lilith, gewichtet gezählt, die "
                                     "meisten Verbindungen.", txt_rz=_rz29)] == ["meiste"], \
        "P12 Gesamtmenge"
    assert [a for a, _b in _p12_satz("Ihre einzigen Verbindungen führen zur Sonne, zu "
                                     "Jupiter und zu Mars.", "Deine Lilith steht im Skorpion.",
                                     txt_rz=_rz29)] == ["einzig"], "K1 P12 Plural falsch"
    # Zweitpruefung: zwei Bezugskandidaten, nur einer traegt die Zahl -> melden;
    # „trägt eine einzige Figur“ ist eine Zaehlung, keine Gleichsetzung.
    assert _p12_satz("Ihre einzigen Verbindungen führen zur Sonne und zu Jupiter.",
                     "Die Venus steht gegenüber deiner Lilith.", txt_rz=_rz29), "K1 P12 Bezug"
    assert _p12_satz("Dein Bild trägt eine einzige Figur.", "", txt_rz=_rz29), "K1 P12 Figur"
    # Zweitpruefung II: Zaehlaussagen mit „einzige Figur“ bleiben PRUEFEN
    for _s in ("Dein Bild wird von einer einzigen Figur getragen.",
               "In deinem Bild ist genau eine einzige Figur zu finden.",
               "In deinem Bild ist eine einzige Figur zu finden.",
               "Übrig bleibt eine einzige Figur.",
               "In deinem Bild ist eine einzige Figur.",
               "In deinem Bild ist eine einzige Figur, ein T-Quadrat."):
        assert _p12_satz(_s, "", txt_rz=_rz29), "K1b P12 Figur: %r" % _s
    assert _p12_satz("Mars, Venus und Saturn bilden eine einzige Figur.", "",
                     txt_rz=_rz29) == [], "K1b P12 Gleichsetzung"
    # 2026-10-12 (Nacharbeiten Englisch, W1): Einzigkeit über ein Element oder einen
    # Modus, in beiden Sprachen gleich. Konstruierte Rangzeilen und Sätze (Saturn im
    # Widder als einziger im Feuer, Venus in den Zwillingen als einzige veränderlich);
    # gewichtet tragen Feuer und „veränderlich“ je zwei Träger — die genannte Zählmenge
    # („zehn Hauptkräfte“, „ten main forces“, „planets“) muss die gezählte Zeile wählen.
    _txtw1 = ("- RANG elemente-gezaehlt [zehn Planeten]: 1. Erde 4 von 10 = 40 % (Sonne, Mond, "
              "Merkur, Uranus) · 2. Luft 3 von 10 = 30 % (Venus, Mars, Jupiter) · 3. Wasser 2 von "
              "10 = 20 % (Neptun, Pluto) · 4. Feuer 1 von 10 = 10 % (Saturn)\n"
              "- RANG elemente-gewichtet [Lichter ×2]: 1. Erde 6 von 13 = 46 % (Sonne ×2, Mond ×2, "
              "Merkur, Uranus) · 2. Luft 3 von 13 = 23 % (Venus, Mars, Jupiter) · 3. Wasser 2.5 von "
              "13 = 19 % (Neptun, Pluto, Chiron ×0.5) · 4. Feuer 1.5 von 13 = 12 % (Saturn, "
              "Lilith ×0.5)\n"
              "- RANG modi-gezaehlt [zehn Planeten]: 1. kardinal 6 von 10 = 60 % (Saturn, Neptun, "
              "Sonne, Merkur, Mars, Uranus) · 2. fix 3 von 10 = 30 % (Mond, Jupiter, Pluto) · "
              "3. veränderlich 1 von 10 = 10 % (Venus)\n"
              "- RANG modi-gewichtet [Lichter ×2]: 1. kardinal 7.5 von 13 = 58 % (Saturn, Neptun, "
              "Sonne ×2, Merkur, Mars, Uranus, Lilith ×0.5) · 2. fix 4 von 13 = 31 % (Mond ×2, "
              "Jupiter, Pluto) · 3. veränderlich 1.5 von 13 = 12 % (Venus, Chiron ×0.5)\n")
    _rzw1 = _rangzeilen_lesen(_txtw1)

    def _p12_w1(satz, vorher="", englisch=False):
        out = []
        for art, rx in (_RANG_MUSTER_EN if englisch else _RANG_MUSTER):
            for m_ in rx.finditer(satz):
                b = _rang_befund(art, m_, satz, _rzw1, "geburt", vorher, englisch=englisch)
                if b:
                    out.append((art, b))
        return out
    assert _element_modus("in einem Zeichen der Anpassung") == (None, "veränderlich")
    assert _element_modus("in den Zeichen des Haltens") == (None, "fix")
    assert _element_modus("im Zeichen des Anfangs") == (None, "kardinal")
    assert _element_modus("one in a sign of adaptation", True) == (None, "veränderlich")
    assert _element_modus("the sole carrier of fire", True) == ("Feuer", None)
    assert _element_modus("in einem Zeichen der Anpassung", True) == (None, None), \
        "W1: englische Muster lesen kein Deutsch"
    assert _p18_modus_im("in Zeichen des Anfangs und des Haltens") is None, \
        "W1: die Zeichen-Form gehört nur der Einzigkeit, nicht P18"
    for _s, _v, _en in (
            # deutsch: stimmig — still
            ("Saturn steht im Widder und ist damit von den zehn Hauptkräften die einzige im Feuer.",
             "", False),
            ("Deine Venus ist von den zehn Hauptkräften die einzige in einem Zeichen der Anpassung.",
             "", False),
            ("Von den zehn Hauptkräften ist Venus die einzige Kraft in einem Zeichen der Anpassung.",
             "", False),
            ("Venus ist die einzige Hauptkraft in einem Zeichen der Anpassung.", "", False),
            ("Saturn ist von den zehn Hauptkräften die einzige Kraft, die im Feuer steht.", "", False),
            ("Unter den Planeten ist dein Saturn der einzige Träger des Feuers.", "", False),
            ("Er ist von den zehn Hauptkräften der einzige im Feuer.", "Saturn steht im Widder.",
             False),
            # englisch: dieselben Aussagen — still, auch mit „single“ und „sole“
            ("Saturn is the single one in fire among your ten main forces.", "", True),
            ("Venus is the sole one in a sign of adaptation among your ten main forces.", "", True),
            ("Saturn, in Aries, is the only carrier of fire among your planets.", "", True),
            ("Of your ten main forces, Venus is the single one in a mutable sign.", "", True),
            ("Saturn is the only force of your ten main forces that stands in fire.", "", True),
            ("It is the single one in fire among your planets.", "Saturn stands in Aries.", True),
            # eine Achse daneben; „gewichtet“ mit genannter Planetenmenge
            ("Saturn steht im Widder am MC und ist von den zehn Hauptkräften die einzige im Feuer.",
             "", False),
            ("Gewichtet, ist Saturn von den zehn Hauptkräften die einzige im Feuer.", "", False),
            ("Weighted, Saturn is the single one in fire among your ten main forces.", "", True)):
        assert _p12_w1(_s, _v, _en) == [], "W1 P12 still: %r -> %r" % (_s, _p12_w1(_s, _v, _en))
    for _s, _v, _en in (
            # falscher Planet, Zählung nicht 1, Träger nur als Partner, Pronomen mit falschem
            # oder doppeltem Bezug
            ("Merkur ist von den zehn Hauptkräften die einzige im Feuer.", "", False),
            ("Dein Merkur ist von den zehn Hauptkräften die einzige in einem Zeichen der Anpassung.",
             "", False),
            ("Merkur ist von den zehn Hauptkräften die einzige Kraft in einem Zeichen der Anpassung.",
             "", False),
            ("Merkur ist von den zehn Hauptkräften die einzige Kraft, die im Feuer steht.", "", False),
            ("Neptun ist von den zehn Hauptkräften die einzige im Wasser.", "", False),
            ("Neben Venus ist Mars von den zehn Hauptkräften die einzige im Feuer.", "", False),
            ("Mars bildet eine Opposition zu Saturn und ist von den zehn Hauptkräften die einzige im "
             "Feuer.", "", False),
            ("Von den zehn Hauptkräften ist er der einzige im Feuer.", "Merkur steht im dritten Haus.",
             False),
            ("Er ist von den zehn Hauptkräften der einzige im Feuer.",
             "Saturn steht im Widder, neben Merkur.", False),
            ("Dieser ist von den zehn Hauptkräften der einzige im Feuer.",
             "Merkur steht im dritten Haus.", False),
            ("Mercury is the single one in fire among your ten main forces.", "", True),
            ("Mercury is the sole one in a sign of adaptation among your ten main forces.", "", True),
            ("Neptune is the single one in water among your ten main forces.", "", True),
            ("Mars opposes Saturn and is the single one in fire among your ten main forces.", "",
             True),
            ("Of your ten main forces, it is the single one in fire.",
             "Mercury stands in the third house.", True),
            ("Of your ten main forces, it is the single one in fire.", "Mars opposes Saturn.", True),
            ("Jener ist von den zehn Hauptkräften der einzige im Feuer.",
             "Mars steht in Opposition zu Saturn.", False),
            # ohne genannte Zählmenge gelten beide Zeilen; gewichtet trägt das Feuer zwei
            ("Saturn ist die einzige Kraft im Feuer.", "", False),
            ("Saturn is the only force in fire.", "", True)):
        assert [a for a, _b in _p12_w1(_s, _v, _en)] == ["einzig"], \
            "W1 P12 muss melden: %r -> %r" % (_s, _p12_w1(_s, _v, _en))
    for _s, _en in (
            # vertauschte Zuordnung — beide Aussagen falsch
            ("Von den zehn Hauptkräften ist Venus die einzige im Feuer und Saturn die einzige in "
             "einem Zeichen der Anpassung.", False),
            ("Of your ten main forces, Venus is the single one in fire and Saturn the single one "
             "in a sign of adaptation.", True)):
        assert [a for a, _b in _p12_w1(_s, "", _en)] == ["einzig", "einzig"], \
            "W1 vertauschte Zuordnung: %r -> %r" % (_s, _p12_w1(_s, "", _en))
    # Anteile: „Hauptkräfte“ wählt dort keine Zählung (Gewichtet am Satzanfang ohne Komma;
    # gezählt 30 %, gewichtet 23 %)
    assert [a for a, _b in _p12_w1("Gewichtet stehen 30 Prozent deiner zehn Hauptkräfte in der "
                                   "Luft.")] == ["haelfte"], "W1: Anteil mit „Gewichtet“ bleibt PRÜFEN"
    # englisch öffnet die Einzigkeit über Element/Modus einen Satz ohne Faktor — nur sie
    assert _EINZIG_EM_EN_RE.search("It is the single one in fire.") and \
        not _hat_referent("It is the single one in fire."), "W1 Tor englisch"
    assert not _EINZIG_EM_EN_RE.search("The only thing that matters is fresh air."), \
        "W1 Tor: Element ohne Einzigkeitsform"
    # das Element zählt nur hinter einer Präposition, dazwischen nur erlaubte Wörter
    _allg = "Einzigkeitsaussage ohne passende Rangzeile — gegen Tabellen und Strukturbild halten"
    for _s in ("Mars is the only planet that faces Venus.",
               "Saturn is the only planet that brings air into your work.",
               "Saturn is the only planet in a square to your Moon in water."):
        assert [b for _a, b in _p12_w1(_s, "", True)] == [_allg], "W1: kein Element in %r" % _s
    assert _p12_w1("Du holst einen einzigen tiefen Atemzug Luft.") == [], "W1: Bild ohne Präposition"
    assert _p12_w1("Die einzige Wahl im Feuer der Begeisterung fällt dir leicht.") == [], \
        "W1: Bild mit Präposition, aber ohne Chart-Wort davor"
    # P13-Satzformen (Regeln 12 bis 18)
    for _s, _soll in (
            ("Die Verbindungen zum Aszendenten und zu Jupiter reiben: Im Quadrat zu ihnen "
             "steht nichts.", set()),
            ("Dein Mars bildet zu deiner Sonne, deinem Mond und deinem Merkur je ein Sextil.",
             {("MARS", "SONNE"), ("MARS", "MOND"), ("MARS", "MERKUR")}),
            ("Merkur und Venus stehen im Sextil zueinander und bilden zum Mondknoten je ein "
             "Quincunx.", {("MERKUR", "VENUS"), ("MERKUR", "MONDKNOTEN"),
                          ("VENUS", "MONDKNOTEN")}),
            ("Je ein leises Quincunx besteht zwischen Sonne und Chiron, zwischen Venus und "
             "Pluto.", {("SONNE", "CHIRON"), ("VENUS", "PLUTO")}),
            ("Am IC wirkt das Quincunx zwischen Saturn und dem MC.", {("SATURN", "MC")}),
            ("Chiron steht still am Rand, während das Sextil zu Mars den Weg öffnet.", set()),
            ("Merkur und Saturn verschmelzen auf der einen Seite, Chiron und Pholus auf der "
             "anderen.", {("MERKUR", "SATURN"), ("CHIRON", "PHOLUS")}),
            # Zweitpruefung: diese Formen muessen weiter paaren
            ("Deine Sonne bleibt ruhig, während sie im Quadrat zu Saturn steht.",
             {("SONNE", "SATURN")}),
            ("Dein Mond wirkt weich, obwohl er im Quadrat zu Pluto steht.", {("MOND", "PLUTO")}),
            ("Zu Sonne, Mond und Merkur bildet dein Mars je ein Sextil.",
             {("MARS", "SONNE"), ("MARS", "MOND"), ("MARS", "MERKUR")}),
            ("Mit Sonne und Mond bildet Saturn je ein Quadrat.",
             {("SATURN", "SONNE"), ("SATURN", "MOND")}),
            ("Mars bildet ein Quadrat zwischen Sonne und Mond.",
             {("MARS", "SONNE"), ("MARS", "MOND")}),
            ("Die Sonne steht im Quadrat zu Mars und zu Saturn, die beide in Opposition "
             "stehen.", {("SONNE", "MARS"), ("SONNE", "SATURN"), ("MARS", "SATURN")}),
            ("Deine Sonne hat einen Gegenspieler: im Quadrat zu Saturn.", {("SONNE", "SATURN")}),
            ("Saturn steht im Trigon zu Uranus und zu Neptun, die beide in leichter "
             "Verbindung mit ihm stehen.", {("SATURN", "URANUS"), ("SATURN", "NEPTUN")}),
            ("Saturn steht im Trigon zu deinem Uranus und zu deinem Neptun, und beide stehen "
             "in leichter Verbindung mit ihm.", {("SATURN", "URANUS"), ("SATURN", "NEPTUN")}),
            ("Uranus steht im Quadrat zur Sonne, während Pluto im Trigon zum Mond steht.",
             {("URANUS", "SONNE"), ("PLUTO", "MOND")})):
        _ist = _p13_paare(_s)
        assert _ist == {frozenset(p) for p in _soll}, "K1 P13: %r -> %r" % (_s, _ist)
    # Zweitpruefung II (2026-09-29): Nebensatz mit Objektpronomen, Doppelpunkt
    # mit Faktor hinter dem Marker, „je“ hinter einer Ortsangabe — geprueft,
    # nicht verschluckt.
    for _s, _soll in (
            ("Dein Mond bleibt wachsam, weil Pluto im Quadrat zu ihm steht.",
             {("MOND", "PLUTO")}),
            ("Dein Mars wird laut, wenn Uranus im Quadrat zu ihm steht.",
             {("MARS", "URANUS")}),
            ("Deine Sonne strahlt, obwohl Saturn sie im Quadrat bremst.",
             {("SONNE", "SATURN")}),
            ("Bei deinem Merkur ist das anders: Er steht im Trigon zu Uranus.",
             {("MERKUR", "URANUS")}),
            ("Bei deinem Mond liegt die Spannung: im Quadrat zu Pluto.",
             {("MOND", "PLUTO")}),
            ("Bei deinem Merkur ist das anders: Er steht im Trigon zu Uranus und "
             "zu Neptun.", {("MERKUR", "URANUS"), ("MERKUR", "NEPTUN")}),
            ("Bei deinem Mond liegt die Spannung: im Quadrat zu Pluto und zu Saturn.",
             {("MOND", "PLUTO"), ("MOND", "SATURN")}),
            ("Mit deinem Mond ist es so: Er reibt sich an Saturn und an Pluto.",
             {("MOND", "SATURN"), ("MOND", "PLUTO")}),
            ("Bei deinem Mond ist es anders: Saturn steht im Quadrat zu Pluto.",
             {("SATURN", "PLUTO")}),
            ("An deiner Sonne hängt viel: das Trigon zu Jupiter und das Quadrat "
             "zu Saturn.", {("SONNE", "JUPITER"), ("SONNE", "SATURN")})):
        _ist = _p13_paare(_s)
        assert _ist == {frozenset(p) for p in _soll}, "K1b P13: %r -> %r" % (_s, _ist)
    _je = [(tuple(d), tuple(n)) for d, _a, n, _m in _konstellationen(
        "Dein Mars am Aszendenten bildet zu Sonne und Mond je ein Sextil.")]
    assert _je == [(("MARS",), ("SONNE",)), (("MARS",), ("MOND",))], \
        "K1b P13 je: %r" % _je
    # 2026-09-29 (K2): benannte Aufzaehlung und Register
    _rz_k2 = _rangzeilen_lesen("- RANG verbindungen-gezaehlt [je 1]: 1. Merkur 8 · "
                               "2. Sonne 7 · 3. Pluto 5 · 4. Lilith 2\n")
    for _s in ("Alle drei stehen im Wasser: dein Mond, dein Mars und dein Pluto.",
               "Alle drei — Sonne, Mond und Merkur — stehen im Feuer.",
               "Pluto hat zwei leise Verbindungen, zu Mars und zu Venus.",
               "Pluto hat zwei leise Verbindungen: zu Mars und zu Venus."):
        assert _p12_satz(_s, txt_rz=_rz_k2) == [], "K2 Aufzählung: %r" % _s
    for _s in ("Alle drei stehen im Wasser: dein Mond und dein Mars.",
               "Drei weitere Verbindungen führen von deinem Mars weg.",
               # Zweitpruefung: Partner hinter „zu“ sind nicht die gezaehlten Kraefte,
               # und die Gesamtzahl bleibt eine Aussage ueber das Bild
               "Alle drei Luftplaneten stehen im Quadrat zu Saturn, Mars und Venus.",
               "Pluto hat zwei Verbindungen, zu Mars und zu Venus."):
        assert _p12_satz(_s, txt_rz=_rz_k2), "K2 muss melden: %r" % _s
    def _k2_kap(kicker, text):
        return {"kicker": kicker, "title": "T", "signatur": "", "beleg": "",
                "blocks": [{"type": "para", "text": text}]}
    for _k, _st in (("Kapitel 2", "PRUEFEN"), ("Rechenschaft", "OK")):
        _pk = _p12_rang([_k2_kap("Auftakt", "Dein Mond steht im Krebs."),
                         _k2_kap("Getriebe", "Dein Mond steht im Krebs."),
                         _k2_kap(_k, "Drei weitere Verbindungen führen von deinem "
                                     "Mars weg.")],
                        "- RANG verbindungen-gezaehlt [je 1]: 1. Merkur 8 · "
                        "2. Sonne 7 · 3. Lilith 2\n", "geburt")
        assert _pk.status == _st, "K2 Register: %s -> %s %r" % (_k, _pk.status, _pk.pruefen)
    # 2026-09-25: Eigenschaft gegen Einzahl, „richtet sich nach", Teilmenge
    assert _p12_satz("Deine Venus steht auf eigenem Boden und folgt keinem anderen.") == [], \
        "P12 §3 Eigenschaft: der genannte Planet steht in §3"
    assert _p12_satz("Ketten enden bei ihm, und er folgt keinem anderen, weil er im eigenen "
                     "Zeichen steht.", "Saturn steht im Steinbock.") == [], \
        "P12 §3 Eigenschaft mit Pronomen aus dem Vorsatz"
    assert _p12_satz("Deine Venus richtet sich nach keinem anderen Planeten.") == [], \
        "P12 §3 Variante „richtet sich nach keinem anderen“"
    _b12 = _p12_satz("Dein Mars folgt keinem anderen.")
    assert [a for a, _b in _b12] == ["kein_anderer"] and "steht nicht" in _b12[0][1], \
        "P12 §3 Eigenschaft: Planet außerhalb von §3 muss PRÜFEN bleiben (%s)" % _b12
    _b12 = _p12_satz("Als einzige deiner Kräfte folgt deine Venus keinem anderen.")
    assert [a for a, _b in _b12] == ["kein_anderer"] and "Einzahl" in _b12[0][1], \
        "P12 §3 Einzahl mit „als einzige“ (%s)" % _b12
    _b12 = _p12_satz("Saturn ist der Planet, der keinem anderen folgt.")
    assert "Einzahl" in _b12[0][1], "P12 §3 Einzahl-Meldung nennt die Einzahl (%s)" % _b12
    _b12 = _p12_satz("Drei weitere Verbindungen Saturns haben ihre Heimat in anderen Kapiteln.")
    assert [a for a, _b in _b12] == ["n_verbindungen"] and _b12[0][1].startswith(
        "Zählaussage über eine Teilmenge"), "P12 Teilmenge statt gewichteter Dichte (%s)" % _b12
    try:                            # 2026-09-24: §3-Leser gegen die echte radix-Ausgabe
        import radix as _rx3
        if hasattr(_rx3, "strukturbild_text"):
            _t3 = _rx3.strukturbild_text(_rx3.strukturbild(
                [{"name": "Sonne", "lon": 5.0}, {"name": "Mars", "lon": 10.0},
                 {"name": "Pluto", "lon": 215.0}, {"name": "Mond", "lon": 195.0},
                 {"name": "Venus", "lon": 100.0}, {"name": "AC", "lon": 0.0},
                 {"name": "MC", "lon": 270.0}, {"name": "DC", "lon": 180.0},
                 {"name": "IC", "lon": 90.0}], [i * 30.0 for i in range(12)]))
            assert _eigenes_zeichen(_t3) == {"MARS", "PLUTO"}, \
                "Strukturbild §3: Zeilenformat weicht von radix ab — _EIGENES_ZEICHEN_RE nachziehen"
            berichte.append("§3-Leser gleich radix.py")
    except ImportError:
        berichte.append("radix.py nicht importierbar — §3-Vergleich übersprungen")
    assert _ZUSATZ_SEG_ANFANG_RE.match("Finsternis auf R-Mond ☽ — 12.08.2026") and \
        _ZUSATZ_SEG_ANFANG_RE.match("Sonnenbogen-Merkur ☿ Quadrat □ R-Neptun ♆ — exakt 01.03.2027") \
        and not _ZUSATZ_SEG_ANFANG_RE.match("T-Saturn ♄ Quadrat □ R-Mond ☽ — exakt 01.03.2027") \
        and _ZUSATZ_SEG_ANFANG_RE.match("Jahresprofektion → Zwillinge ♊, Jahresherr Merkur ☿ — ab dem 37. Geburtstag") \
        and _ZUSATZ_SEG_ANFANG_RE.match("Annual profection → Gemini ♊, lord of the year Mercury ☿ — from the 37th birthday") \
        and not _ZUSATZ_SEG_ANFANG_RE.match("Merkur ☿ Quadrat □ Saturn ♄ 2°10′ (Jahresherr der Profektion)"), \
        "P1 Zusatz-Segment am Anfang"
    _z = _ZUSATZ_KONTAKT_RE.search("Sonnenbogen-Merkur ☿ Quadrat □ R-Neptun ♆ — exakt 01.03.2027")
    assert _z and kanon(_z.group("t")) == "MERKUR" and kanon(_z.group("r")) == "NEPTUN", \
        "P13 Zusatz-Segment nicht gelesen"
    # W29: der Deckel zaehlt nur die Wortliste — vier andere Superlative bleiben still
    _k = [{"kicker": "Kapitel 2", "title": "Probe", "blocks": [{"type": "p", "text":
          "Hier reicht es am weitesten. Die meisten Wochen sind ruhig. Am höchsten steht "
          "der Mond. Am längsten dauert der Winter."}]}]
    assert _p10_wortscan(_k).status == "OK", "W29: Deckel zählt fremde Superlative"
    # F2: Halbquadrat ∠, Anderthalbquadrat ⚼ und der Wort-Trenner werden gelesen,
    # eine fremde Glyphe nicht — und sie wird genannt, nicht still uebergangen
    _unl = []
    _tab = _tabellen_lesen("### Untergrund-Aspekte\n\n| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |\n"
                           "|---|---|---|---|---|---|\n| Mars | ∠ Halbquadrat | Sonne | 0°30′ | grau |  |\n"
                           "| Merkur | ⚼ Anderthalbquadrat | Saturn | 1°05′ | grau |  |\n"
                           "| Venus | –Anderthalbquadrat– | Mond | 1°10′ | grau |  |\n"
                           "| Merkur | ∡ Anderthalbquadrat | Mond | 1°20′ | grau |  |\n", _unl)
    assert [e["art"] for e in _tab] == ["Halbquadrat", "Anderthalbquadrat", "Anderthalbquadrat"] \
        and len(_unl) == 1 and "∡" in _unl[0][2], "F2: Tabellenzeilen %s / %s" % (_tab, _unl)
    try:                            # U1 b: Rangzeilen-Muster woertlich wie in radix.py
        import radix as _rx
        if hasattr(_rx, "RANG_ZEILE_RE"):
            assert RANG_ZEILE_RE.pattern == _rx.RANG_ZEILE_RE.pattern
            assert {k: v.pattern for k, v in RANG_EINTRAG_RE.items()} == \
                {k: v.pattern for k, v in _rx.RANG_EINTRAG_RE.items()}, \
                "RANG_EINTRAG_RE weicht von radix.RANG_EINTRAG_RE ab — Format nachziehen"
            berichte.append("Rangzeilen-Muster gleich radix.py")
    except ImportError:
        berichte.append("radix.py nicht importierbar — Mustervergleich übersprungen")
    assert _p14_kopfblock([{"kicker": "Kapitel 2", "title": "Probe", "signatur": "", "beleg": "",
                            "blocks": []}], "geburt").status == "UEBERSPRUNGEN", \
        "P14 meldet im Fachmodus (kein Kopfblock im ganzen Dokument) Fehler"
    # 2026-09-22 (W57-Nachzug): P11 und P12 LAUFEN jetzt auf einer englischen Analyse
    # (eigene Muster- und Zahlwortafeln). Die Zusicherung von vorher — beide
    # uebersprungen — ist damit umgedreht: Sie duerfen NICHT mehr uebersprungen
    # melden, und auf leerer Eingabe bleibt es aussagelos statt uebersprungen.
    for fn, args in ((_p11_zahlen, ([], "", None, "en")), (_p12_rang, ([], "", None, "en"))):
        assert fn(*args).status != "UEBERSPRUNGEN", \
            "%s überspringt eine englische Analyse noch" % fn.__name__
    assert _zahl_wert("forty-three") == 43 and _zahl_wert("twelve") == 12, \
        "englische Zahlwörter werden nicht gelesen"
    assert _MONATE_EN["june"] == 6 and (2027, 4) in _jz_kandidaten("spring", 2027, _JAHRESZEIT_MONATE_EN), \
        "englische Monats- oder Zeitraumtafel greift nicht"
    assert (2027, 4) in _jz_kandidaten("Frühjahr", 2027, _JAHRESZEIT_MONATE), \
        "deutsche Zeitraumtafel nach dem Umbau nicht mehr gleich"
    berichte.append("englische Tafeln P11/P12 aktiv")

    # 2026-09-24 (Klasse-2-Entscheidungslauf): P16 Laenge und P17 Subjekt als Einzelproben
    def _kap(kicker, n_woerter, bewegung=None, text=None):
        bl = [{"type": "subhead", "text": bewegung}] if bewegung else []
        return {"kicker": kicker, "title": "Probe", "signatur": "", "beleg": "",
                "blocks": bl + [{"type": "p", "text": text or " ".join(["Wort"] * n_woerter)}]}
    _k16 = [_kap("Getriebe", 400), _kap("Instrument", 400), _kap("Kapitel 1", 400),
            _kap("Kapitel 2", 200), _kap("Kapitel 3", 150), _kap("Kapitel 4", 150)]
    _p = _p16_laenge(_k16, "geburt", "", [], {})
    assert _p.status == "FEHLER" and "42 %" in _p.fehler[0], "P16 Abfall: %s %s" % (_p.status, _p.fehler)
    _th = [{"nr": 4, "form": "kurz"}]
    _p = _p16_laenge(_k16, "geburt", "", _th, {})
    assert _p.status == "OK" and any("form=kurz" in h for h in _p.hinweise), "P16 form=kurz: %s" % _p.hinweise
    _p = _p16_laenge([_kap("Der Stand heute", 1000)] + [_kap("Kapitel %d" % i, 300) for i in (1, 2, 3, 4)],
                     "transit", "", [], {})
    assert _p.status == "OK" and _p.geprueft == 4, "P16: das Lagebild zählt mit (%s)" % _p.geprueft
    assert _p16_laenge(_k16[:3], "geburt", "", [], {}).status == "AUSSAGELOS", "P16 unter vier Kapiteln"
    _zg = [_kap("Getriebe", 400), _kap("Kapitel 1", 400), _kap("Kapitel 2", 400), _kap("Kapitel 3", 100),
           _kap("Zugang Beruf", 100), _kap("Kapitel 4", 100)]
    _zg[3], _zg[4] = _zg[4], _zg[3]
    assert _p16_laenge(_zg, "geburt", "ZUGANG 1 | bereich=Beruf | haeuser=10\n  | duenn=ja", [], {}
                       ).status == "OK", "P16 duenn=ja erklärt den Abfall nicht"
    for _s in ("Der laufende Jupiter weckt etwas, das schon da ist.",
               "Das Muster, das Saturn hier anstößt, ist älter als er.",
               "In der regressiven Form wird Saturn zum Aufseher.",
               "Merkur hat es geprüft; Jupiter lässt es gelten.",
               "In deinem Bild sitzen Mond und Jupiter am selben Punkt.",
               "Ein Mond im Widder fühlt schnell.", "Und der schnelle Widder-Mond lernt die Geduld.",
               "Es geht leicht, denn Saturn scheint ihm recht zu geben.",
               "Das zwölfte Haus nimmt dich aus dem Lärm.", "Deine Seele will etwas anderes.",
               "Was Saturn dazugibt, ist Form."):
        assert _p17_kandidaten(_s)[0], "P17 übersieht: %r" % _s
    for _s in ("Du stehst im Quadrat zu deinem Saturn.", "Das zeigt sich am Trigon zu Sonne, Mond und Saturn.",
               "Die Saturn-Rückkehr kommt um die dreißig.", "Im zwölften Haus liegt vieles.",
               "Wenn du Saturn begegnest, wird es still.", "Du gehst mit ganzer Seele hinein.",
               "Es gehört zu der Sonne, die du bist.", "Die Opposition zwischen Mond und Saturn bleibt."):
        assert not _p17_kandidaten(_s)[0], "P17 Fehlalarm: %r" % _s
    for _s, _soll in (("Dein Mond steht im Stier im fünften Haus.", False),
                      ("Saturn läuft über deine Sonne.", False),
                      ("Am Stichtag steht Saturn im Quadrat zu deiner Sonne.", False),
                      ("Mond und Jupiter stehen am selben Punkt.", False),
                      ("Dein Mond im Widder fühlt schnell.", True), ("Chiron stellt die Berufungsfrage.", True),
                      ("Dann drückt Saturn auf deine Sonne.", True)):
        _k, _t = _p17_kandidaten(_s)
        assert any(_p17_handelt(_t, i, a) for _n, i, a in _k) == _soll, "P17 Grundfassung: %r" % _s
    # 2026-09-25: Adverb, Pluralverb, Umstellung vor dem Artikel, „derselbe", Horizont,
    # „heißt", Objekt-Pronomen, Hilfsverb, Relativsatz (konstruierte Saetze)
    for _s, _soll in (("Im Frühjahr steht auch Jupiter im Trigon zu deinem Merkur.", False),
                      ("Unter den Planeten steht allein Mars in einem solchen Zeichen.", False),
                      ("Uranus und Neptun stehen knapp vor dem Aszendenten.", False),
                      ("Mond und Saturn bilden die engste Verbindung zwischen zwei Kräften.", False),
                      ("Dazu steht dein Mars ganz am Ende des Zeichens.", False),
                      ("Gewichtet ist dein Mond am dichtesten verschaltet.", False),
                      ("Hier steht derselbe Mond vorn und Saturn am Ende.", False),
                      ("Es ist der Punkt, an dem die Sonne am Abend untergeht.", False),
                      ("Der Punkt, der Aszendent heißt, liegt im Osten.", False),
                      ("Neptun und Pluto stehen in weitem Winkel zu ihm.", False),
                      ("Deshalb braucht dein Mond Raum.", True), ("Auch Saturn verlangt Geduld.", True),
                      ("Mars und Venus verlangen Nähe.", True),
                      ("Im Sommer wird Saturn Geduld verlangen.", True),
                      ("Saturn, der die Verantwortung trägt, steht im Quadrat zum Mond.", True)):
        _k, _t = _p17_kandidaten(_s)
        assert any(_p17_handelt(_t, i, a) for _n, i, a in _k) == _soll, "P17 Grundfassung: %r" % _s
    # 2026-09-27 (Klasse-2-Entscheidungslauf, E4): Aspektbilder der Klartext-Tabelle verorten
    for _s, _soll in (("Deine Venus verschmilzt mit Merkur.", False),
                      ("Saturn reibt sich an deiner Sonne.", False),
                      ("Dein Mond fließt mühelos mit Jupiter.", False),
                      ("Saturn setzt dich unter Druck.", True)):
        _k, _t = _p17_kandidaten(_s)
        assert any(_p17_handelt(_t, i, a) for _n, i, a in _k) == _soll, "P17 Aspektbild: %r" % _s
    # 2026-09-28: Adverb an der Endung, Beiwort hinter Genitiv (konstruierte Saetze)
    for _s, _soll in (("Ab Ende Oktober steht zusätzlich Uranus im Quadrat zu ihm.", False),
                      ("Im Winter steht vorübergehend Mars im Trigon zu ihr.", False),
                      ("Weil die Jungfrau Merkurs eigenes Zeichen ist, steht er auf eigenem Boden.", False),
                      ("Ab Ende Oktober verlangt zusätzlich Uranus Geduld.", True),
                      ("Dann fordert unerbittlich Saturn seinen Preis.", True)):
        _k, _t = _p17_kandidaten(_s)
        assert any(_p17_handelt(_t, i, a) for _n, i, a in _k) == _soll, "P17 Adverb/Genitiv: %r" % _s
    # 2026-09-29: „hängen" verortet; im Nebensatz entscheidet das Verb am Gliedende
    for _s, _soll in (("Venus, Mars und Merkur hängen an ihr.", False),
                      ("Pluto hängt an nur zwei Leitungen.", False),
                      ("Über Uranus hängen Sonne, Venus und Mars am selben Kreis.", False),
                      ("Es wird ruhiger, wenn auch Saturn harmonisch zu deinem Mond und zu "
                       "deinem Merkur steht.", False),
                      ("Es wird ruhiger, wenn dein Saturn harmonisch zu deinem Mond steht.", False),
                      ("Es wird still, weil Sonne und Mond harmonisch zu Jupiter stehen.", False),
                      ("Es wird eng, wenn Saturn dir Grenzen setzt.", True),
                      ("Es wird eng, weil Saturn im Stier steht und dich prüft.", True)):
        _k, _t = _p17_kandidaten(_s)
        assert any(_p17_handelt(_t, i, a) for _n, i, a in _k) == _soll, "P17 Nebensatz/hängen: %r" % _s
    assert not _p17_kandidaten("Du hast deine Venus am Aszendenten.")[0], "P17: Objekt hinter „Du hast“"
    assert not _p17_kandidaten("Es gehört zu der Sonne, die du bist.")[0], "P17: Relativsatz mit „du“"
    berichte.append("P16 und P17 als Einzelproben")

    # 1) fehlerfrei
    r = lauf(_TEST_CHART, _TEST_ANALYSE)
    st = {nr: p["status"] for nr, p in r["proben"].items()}
    berichte.append("Lauf 1 (fehlerfrei): " + ", ".join("%s=%s" % kv for kv in st.items()))
    assert all(s == "OK" for s in st.values()), "Lauf 1 nicht sauber: %s\n%s" % (st, befunde(r))
    assert r["fehler"] == 0 and r["pruefen"] == 0
    # W44: der Getriebe-Beleg ist teilweise uebersprungen und zaehlt mit — sonst nichts
    assert [(nr, art) for nr, art, _g in r["uebersprungen"]] == [("P1", "teilweise übersprungen")], (
        "Lauf 1: Zusammenfassung „übersprungen“ unerwartet: %s" % r["uebersprungen"])
    for nr in ("P11", "P12", "P13", "P14", "P15", "P18"):
        assert r["proben"][nr]["geprueft"] > 0, "Lauf 1: %s hat nichts geprüft" % nr

    # 2) je ein Fehler je Probe P1–P6 und P11–P15 (P7 haengt an P3), je ein Treffer P8–P10
    a, c = _TEST_ANALYSE, _TEST_CHART
    a = ersetze(a, "Sonne ☉ Konjunktion ☌ Merkur ☿ 11°10′ Widder ♈, 1. Haus, Orb 1°10′",
                   "Sonne ☉ Konjunktion ☌ Merkur ☿ 11°10′ Widder ♈, 1. Haus, Orb 2°10′")      # P1 Orb
    a = ersetze(a, "**Beleg:** Mond ☽ 20°00′ Stier ♉, 2. Haus ·",
                   "**Beleg:** Mond ☽ 20°00′ Stier ♉, 3. Haus ·")                              # P2 Haus
    c = ersetze(c, "  | fuehrt=Mond, Stier, Haus 2", "  | fuehrt=Merkur, Widder, Haus 1")     # P3/P7 Fuehrer
    a = ersetze(a, "### Der Teil von dir, der das nicht aufgeben will\n\nDer Teil, der zuerst losgeht, "
                   "hat ein gutes Argument: Wer zuerst geht, muss auf niemanden warten. Er rechnet mit "
                   "alten Zahlen, aber er rechnet.\n\n", "")                                    # P4 Bewegung fehlt
    a = ersetze(a, "\n3. Saturn, Jungfrau, sechstes Haus — die Ordnung im Alltag. Klingt mit in Kapitel 3.",
                   "")                                                                          # P5 Zeile fehlt
    c = ersetze(c, "LEITSATZ: Du fängst an, bevor jemand dich darum bittet — und das ist kein Fehler.",
                   "LEITSATZ: Was dich trägt, meldet sich nicht — es ist trotzdem da.")          # P6 Leitsatz
    a = ersetze(a, "Du bleibst, wo andere längst gegangen sind.",
                   "Du bleibst, wo dein Partner längst gegangen ist.")                          # P8 Dritte
    a = ersetze(a, "Wo du das gelernt hast, weiß ich nicht — das steht in keinem Horoskop.",
                   "Die Prüfung daran ist deine Sache.")                                          # P9a Nichtwissen
    a = ersetze(a, "Es ist eine ruhige Stelle in deinem Bild.",
                   "Es ist eine ruhige Stelle in deinem Bild; auch dieses Kapitel darfst du verwerfen.")  # P9b
    a = ersetze(a, "Du bleibst, wo dein Partner längst gegangen ist.",
                   "Du bleibst, wo dein Partner längst gegangen ist. Das wirkt wie eine "
                   "Störung, und du solltest daran arbeiten. Eine Störung ist es nicht.")         # P10 klinisch + Optimierung
    # 2026-09-19: die neuen Proben
    c = ersetze(c, "### Untergrund-Aspekte\n\n_keine_",
                   "### Untergrund-Aspekte\n\n| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |\n"
                   "|---|---|---|---|---|---|\n| Merkur | ∡ Anderthalbquadrat | Saturn | 1°05′ | grau |  |")  # F2
    a = ersetze(a, "Saturn kehrt um die dreißig an seinen Ort zurück",
                   "Saturn kehrt mit zwölf Jahren an seinen Ort zurück")                        # P11 Alter
    a = ersetze(a, "die engste Verbindung zwischen zwei Planeten in deinem Bild",
                   "die engste Verbindung deines ganzen Bildes")                                # P12 Rang
    a = ersetze(a, "Genutzt: Du hältst, was gehalten werden muss.",
                   "Genutzt: Du hältst, was gehalten werden muss. Dein Mars im Quadrat zu "
                   "Saturn bremst dabei.")                                                       # P13 erfundener Aspekt
    a = ersetze(a, "**Signatur:** Was aus den Kapiteln 2 und 3 als Richtung bleibt\n\n", "")    # P14 Signatur fehlt
    a = ersetze(a, "**Signatur:** Die Gegensatzpaare der Kapitel 2 und 3\n",
                   "**Signatur:** Die Gegensatzpaare der Kapitel 2 und 3\n\n"
                   "**Beleg:** Sonne ☉ 10°00′ Widder ♈, 1. Haus\n")                             # P14 Buendel mit Beleg
    a = ersetze(a, "Was Saturn dazugibt, ist Form: Das Gefühl bekommt einen Rahmen, in dem es "
                   "bleiben kann. ", "")                                                         # P15 zu kurz
    a = ersetze(a, "Einmal am Tag den ersten Impuls bemerken, ohne ihm zu folgen.",
                   "Einmal am Tag den ersten Impuls bemerken, ohne ihm zu folgen. Dein Merkur will "
                   "das anders.")                                                                # P17 Subjekt
    r2 = lauf(c, a)
    erwarte(r2, (("P1", "fehler", "Orb 2°10′"), ("P1", "fehler", "unbekanntes Zeichen „∡“"),
                 ("P2", "fehler", "führendes Haus 3"), ("P3", "fehler", "Themenliste sagt Merkur"),
                 ("P4", "fehler", "fehlt: „Der Teil von dir"), ("P5", "fehler", "Saturn führt kein Thema"),
                 ("P6", "fehler", "Leitsatz nicht im Schlusswort"),
                 ("P7", "fehler", "Signatur nennt Merkur nicht"),
                 ("P8", "pruefen", "dein Partner"), ("P9", "pruefen", "Nichtwissens-Satz"),
                 ("P9", "pruefen", "Verwerfungs-Erlaubnis"), ("P10", "pruefen", "Störung"),
                 ("P11", "pruefen", "Altersangabe „mit zwölf“"),
                 ("P12", "pruefen", "steht auf Rang 3 der Rangzeile engste-aspekte"),
                 ("P13", "pruefen", "Mars Quadrat Saturn steht in keinem Beleg"),
                 ("P14", "fehler", "Lebensaufgaben · Woran du wächst: Signatur fehlt"),
                 ("P14", "fehler", "Konfliktfelder · Wo es reibt: trägt einen Beleg"),
                 ("P15", "pruefen", "Mond △ Saturn (voll) — am Deutungsort Thema 2"),
                 ("P17", "pruefen", "Merkur als Satzsubjekt (außerhalb von Thema und Rahmen)")), "Lauf 2")
    # Negativkontrollen des Wortscans: die Fehlalarm-Klassen, an denen die
    # Modulregel gewachsen ist, duerfen NICHT anschlagen.
    fehlt = []
    for _t in ("Zerstörung", "solltest du lassen", "dichtesten verschaltet",
               "tiefste Punkt des Horoskops",
               # neu 2026-09-18: verneintes klinisches Wort. Die Innere Arbeit
               # verlangt den Satz "das ist kein Leiden und keine Stoerung"
               # ausdruecklich; der Scan meldete ihn (drei Fehlalarme in einem
               # Lauf, dazu einer im Transit), und der Lauf schrieb die
               # regelkonforme Stelle um, damit die Probe schweigt.
               "keine Störung", "kein Leiden und keine"):
        if any(_t in t for t in r2["proben"]["P10"]["pruefen"]):
            fehlt.append("P10: Fehlalarm bei „%s“" % _t)
    st2 = {nr: p["status"] for nr, p in r2["proben"].items()}
    berichte.append("Lauf 2 (eingebaute Fehler): " + ", ".join("%s=%s" % kv for kv in st2.items()))
    assert not fehlt, "Eine Probe findet ihren Testfehler nicht:\n  " + "\n  ".join(fehlt)

    # 3) Zugang-Kapitel mit Kicker `Zugang <Bereich>` (2026-09-16): sauber ohne
    #    Befund — und der verwiesene Aspekt wird geprueft, nicht uebersprungen.
    a3 = ersetze(_TEST_ANALYSE, "## Rechenschaft · Was sonst in deinem Bild steht",
                 _TEST_ZUGANG + "## Rechenschaft · Was sonst in deinem Bild steht")
    r3 = lauf(_TEST_CHART, a3)
    st3 = {nr: p["status"] for nr, p in r3["proben"].items()}
    berichte.append("Lauf 3 (Zugang-Kapitel): " + ", ".join("%s=%s" % kv for kv in st3.items()))
    assert r3["fehler"] == 0 and r3["pruefen"] == 0 and \
        [nr for nr, _art, _g in r3["uebersprungen"]] == ["P1"], (
            "Lauf 3 nicht sauber: %s\n%s" % (st3, befunde(r3)))
    assert r3["proben"]["P1"]["geprueft"] == r["proben"]["P1"]["geprueft"] + 2, (
        "P1 hat die zwei verwiesenen Aspekte des Zugangs nicht geprueft")
    assert r3["proben"]["P4"]["geprueft"] == r["proben"]["P4"]["geprueft"] + 1, (
        "P4 hat das Zugang-Kapitel nicht als Themenkapitel gezaehlt")
    a3f = ersetze(a3, "Mond ☽ Trigon △ Saturn ♄ 2°05′ (Kapitel 3)", "Mond ☽ Trigon △ Saturn ♄ 3°05′ (Kapitel 3)")
    r3f = lauf(_TEST_CHART, a3f)
    assert any("Zugang Beruf" in t and "Orb 3°05′" in t for t in r3f["proben"]["P1"]["fehler"]), (
        "P1 findet den falschen Orb im Zugang-Beleg nicht: %s" % r3f["proben"]["P1"]["fehler"])

    # 4) Transit mit events.json, fehlerfrei (2026-09-19: W10, W23, W24, W43, U1)
    tc, ta, tev, w = _transit_fall()
    r4 = lauf(tc, ta, tev)
    st4 = {nr: p["status"] for nr, p in r4["proben"].items()}
    berichte.append("Lauf 4 (Transit mit events.json): " + ", ".join("%s=%s" % kv for kv in st4.items()))
    assert r4["typ"] == "transit" and r4["fehler"] == 0 and r4["pruefen"] == 0 and \
        [nr for nr, _art, _g in r4["uebersprungen"]] == ["P16"], \
        "Lauf 4 nicht sauber (nur P16 aussagelos, zwei Kapitel): %s\n%s\n%s" % (
            st4, befunde(r4), r4["uebersprungen"])
    assert r4["proben"]["P1"]["geprueft"] == 5 and r4["proben"]["P5"]["geprueft"] == 3 and \
        r4["proben"]["P14"]["geprueft"] == 6, "Lauf 4: Zählung P1/P5/P14 %s" % (
            [r4["proben"][n]["geprueft"] for n in ("P1", "P5", "P14")])
    # 4e) 2026-09-28: Profektions-Segment im Beleg — Geburtstag gegen zusatz.profektion[].alter
    _alt4e = "T-Saturn ♄ Quadrat □ R-Merkur ☿ — exakt %s, %s" % (w["e75"], w["e190"])
    ta4e = ersetze(ta, _alt4e, _alt4e + " · Jahresprofektion → Zwillinge ♊, Jahresherr "
                   "Merkur ☿ — ab dem 36. Geburtstag")
    _pr4e = {"alter": 36, "haus": 3, "zeichen": "Zwillinge", "herrscher": "Merkur", "modern": None}
    r4e = lauf(tc, ta4e, dict(tev, zusatz={"profektion": [_pr4e]}))
    assert r4e["fehler"] == 0 and r4e["pruefen"] == 0 and r4e["proben"]["P1"]["geprueft"] == 6, \
        "Lauf 4e: Profektions-Segment nicht still: %s" % befunde(r4e)
    p4e = lauf(tc, ta4e, dict(tev, zusatz={"profektion": [dict(_pr4e, alter=35)]}))["proben"]["P1"]
    assert len(p4e["pruefen"]) == 1 and "zusatz.profektion[].alter" in p4e["pruefen"][0], \
        "Lauf 4e: falscher Profektions-Geburtstag nicht gemeldet: %s" % p4e["pruefen"]
    # 4c) 2026-09-25 (T20): Registerzeile in Pflichtform und wiederholende
    #     Apposition bleiben still; ein echtes Selbstpaar ohne Kontakt nicht.
    ta4c = ersetze(ersetze(ta, "2. Neptun im Sextil zu deinem Mars",
                           "2. T-Neptun ⚹ R-Mars — im Sextil zu deinem Mars"),
                   "Hier steht, was im Fenster läuft und kein eigenes Kapitel bekommt.",
                   "Hier steht, was im Fenster läuft und kein eigenes Kapitel bekommt. "
                   "Er steht Mars gegenüber, Mars im Zeichen des Aufbruchs.")
    p4c = lauf(tc, ta4c, tev)["proben"]["P13"]
    assert not p4c["pruefen"], "Lauf 4c: P13 Selbstpaar: %s" % p4c["pruefen"]
    p4d = lauf(tc, ersetze(ta4c, "Er steht Mars gegenüber, Mars im Zeichen des Aufbruchs.",
                           "Saturn steht im Quadrat zu deinem Saturn."), tev)["proben"]["P13"]
    assert len(p4d["pruefen"]) == 1 and "Saturn Quadrat Saturn" in p4d["pruefen"][0], \
        "Lauf 4d: echtes Selbstpaar nicht gemeldet: %s" % p4d["pruefen"]

    # 4h) 2026-09-29 (Klasse-2-Entscheidungslauf T11): build.transit_beleg()
    #     schreibt die Belege des Prueffalls wortgleich; Lagebild und ein Kontakt
    #     ohne Nulldurchgang laufen durch P1 und P2 ohne Befund.
    _d4h = tempfile.mkdtemp(prefix="inhaltsprobe_")
    _c4h = os.path.join(_d4h, "t_Transit_chart_data.md")
    _e4h = os.path.join(_d4h, "t_Transit_events.json")
    open(_c4h, "w", encoding="utf-8").write(tc)
    with open(_e4h, "w", encoding="utf-8") as _f4h:
        json.dump(tev, _f4h)
    _k1 = ("Sonne ☉ 10°00′ Widder ♈, 1. Haus · T-Saturn ♄ Quadrat □ R-Sonne ☉ — exakt "
           "%s, %s, %s · T-Saturn ♄ Quadrat □ R-Merkur ☿ — exakt %s, %s"
           % (w["e60"], w["e200"], w["e330"], w["e75"], w["e190"]))
    _k2 = "Mond ☽ 20°00′ Stier ♉, 2. Haus · T-Jupiter ♃ Trigon △ R-Mond ☽ — exakt %s" % w["e150"]
    assert build.transit_beleg(_c4h, _e4h, thema=1) == _k1, "Lauf 4h: THEMA 1"
    assert build.transit_beleg(_c4h, _e4h, thema=2) == _k2, "Lauf 4h: THEMA 2"
    _lb4h = build.transit_beleg(_c4h, _e4h, kontakte=["T-Saturn □ R-Sonne",
                                                     "T-Jupiter △ R-Mond"], lagebild=True)
    _kn4h = build.transit_beleg(_c4h, _e4h, kontakte=["T-Mondknoten ☌ R-Merkur"])
    assert _kn4h.endswith("T-Mondknoten ☊ Konjunktion ☌ R-Merkur ☿ — nicht exakt, "
                          "Annäherung bis 1,8′ am %s" % w["e250"]), _kn4h
    _alt4h = ta.split("## Kapitel 1")[0].split("**Beleg:** ")[1].split("\n")[0]
    ta4h = ersetze(ersetze(ta, _alt4h, _lb4h), "**Beleg:** " + _k2,
                   "**Beleg:** " + _k2 + " · " + _kn4h.split(" · ", 1)[1])
    r4h = lauf(tc, ta4h, tev)
    assert not any(r4h["proben"][n][k] for n in ("P1", "P2") for k in ("fehler", "pruefen")) \
        and r4h["proben"]["P1"]["geprueft"] == 6, "Lauf 4h: %s" % befunde(r4h)

    # 4f) 2026-09-29: Transit-Bild „über" samt Ellipse (Frage 2 = B: die Rechnung
    #     deckt weiter). Ein berechneter Kontakt ohne Beleg bleibt still, eine
    #     erfundene Konjunktion wird gemeldet.
    p4f = lauf(tc, ersetze(ta, "und macht das Denken vorsichtiger.",
                           "und macht das Denken vorsichtiger. Im Winter geht Neptun über "
                           "deinen Mars, im Frühjahr über deine Venus."), tev)["proben"]["P13"]
    assert len(p4f["pruefen"]) == 2 and all("Konjunktion" in x for x in p4f["pruefen"]), \
        "Lauf 4f: erfundene Konjunktionen nicht gemeldet: %s" % p4f["pruefen"]
    p4g = lauf(tc, ersetze(ta, "und macht das Denken vorsichtiger.",
                           "und macht das Denken vorsichtiger. Dazu kommt Pluto im Trigon "
                           "zu deiner Venus."), tev)["proben"]["P13"]
    assert not p4g["pruefen"], "Lauf 4g: berechneter Kontakt gemeldet: %s" % p4g["pruefen"]
    _k4f = [(d, n) for d, _a, n, _m in _konstellationen(
        "Im Dezember geht der Mondknoten über deine Venus, im Oktober über deinen Mars.",
        typ="transit")]
    assert _k4f == [(["MONDKNOTEN"], ["VENUS"]), (["MONDKNOTEN"], ["MARS"])], _k4f
    assert not _konstellationen("Über deinen Mars läuft die Kette.", typ="geburt"), \
        "P13: „über“ ausserhalb des Transits als Konstellation gelesen"

    # 5) Transit mit eingebauten Fehlern
    a5 = ta
    a5 = ersetze(a5, "## Zur Lesart · Wie du", "## Vorwort · Wie du")                   # W23 (Gegenprobe)
    a5 = ersetze(a5, "Einmal im Monat etwas annehmen, ohne es zu verdienen.",
                 "Einmal im Monat etwas annehmen, ohne es zu verdienen. Jupiter macht vieles möglich.")  # P17 streng
    a5 = ersetze(a5, "beides erzählen die folgenden Kapitel.",
                 "beides erzählen die folgenden Kapitel. Saturn verlangt jetzt Geduld.")   # P17 Grundfassung
    a5 = ersetze(a5, "Orb 0,57°", "Orb 0,75°")                                              # W10 Stichtag-Orb
    a5 = ersetze(a5, "am Stichtag Orb 2,40°, zulaufend; exakt %s" % w["e150"],
                 "am Stichtag Orb 2,40°, zulaufend; exakt %s · T-Mondknoten ☊ Konjunktion ☌ "
                 "R-Merkur ☿ — am Stichtag Orb 1,20°; exakt %s" % (w["e150"], w["e250"]))  # W24 Annaeherung als exakt
    a5 = ersetze(a5, "R-Sonne ☉ — exakt %s, %s, %s · T-Saturn" % (w["e60"], w["e200"], w["e330"]),
                 "R-Sonne ☉ — exakt %s, %s, %s · T-Saturn" % (w["e60"], w["e201"], w["e330"]))  # W24 Datum
    a5 = ersetze(a5, "R-Mond ☽ — exakt %s\n\n### Woran" % w["e150"],
                 "R-Mond ☽ — exakt %s · T-Uranus ♅ Quadrat □ R-Mond ☽ — exakt %s\n\n### Woran"
                 % (w["e150"], w["e100"]))                                                   # W24 Kontakt fehlt
    a5 = ersetze(a5, "hat ein gutes Argument: Wer schnell ist, muss nicht warten.",
                 "hat dich oft geschützt.")                                                  # W4 Zeitform
    a5 = ersetze(a5, "und macht das Denken vorsichtiger.",
                 "und macht das Denken vorsichtiger. Dazu kommt Pluto im Quadrat zu deiner Sonne.")  # P13
    a5 = ersetze(a5, "Das Fenster schließt nichts.",
                 "Das Fenster schließt nichts. Eine ähnliche Frage stand im %s an, als du neun warst."
                 % w["mM2500"])                                                               # P11 Monat, Alter
    a5 = ersetze(a5, " Jupiter weitet, was der Mond braucht, und das Gefühl von Sicherheit wird "
                     "größer. Das zeigt sich im Alltag daran, dass du weniger festhältst. Ein solcher "
                     "Transit verspricht nichts; er macht etwas leichter erreichbar.", "")        # P15 zu kurz
    a5 = ersetze(a5, "\n\n2. Neptun im Sextil zu deinem Mars, im %s: die Kraft wird weicher." % w["m400"],
                 "")                                                                          # W43 Zeile fehlt
    a5 = ersetze(a5, "\n\n3. Der Mondknoten", "\n\n2. Der Mondknoten")
    a5 = ersetze(a5, " Klingt mit in Kapitel 1.", "")                                         # W43 Kapitel fehlt
    r5 = lauf(tc, a5, tev)
    erwarte(r5, (("P1", "fehler", "Orb am Stichtag 0,75° weicht ab"),
                 ("P1", "fehler", "ist eine Annäherung ohne Nulldurchgang"),
                 ("P1", "fehler", "exakt %s ist kein Nulldurchgang" % w["e201"]),
                 ("P1", "fehler", "Kontakt T-Uranus Quadrat R-Mond steht nicht in events.json"),
                 ("P5", "fehler", "T-Neptun Sextil R-Mars — primärer Wirkorb-Kontakt"),
                 ("P5", "pruefen", "nennt das Kapitel 1 nicht"),
                 ("P9", "pruefen", "Verwerfungs-Erlaubnis außerhalb des ersten Themenkapitels · Vorwort"),
                 ("P10", "pruefen", "Superlative: 4 Treffer"),
                 ("P10", "pruefen", "Zeitform (Widerstand)"),
                 ("P11", "pruefen", "Monat „%s“" % w["mM2500"]),
                 ("P11", "pruefen", "Altersangabe „als du neun warst“"),
                 ("P13", "pruefen", "Pluto Quadrat Sonne steht in keinem Beleg"),
                 ("P15", "pruefen", "Jupiter △ Mond (Transit) — am Deutungsort Thema 2"),
                 ("P17", "pruefen", "Jupiter als Satzsubjekt (außerhalb von Thema und Rahmen)"),
                 ("P17", "pruefen", "Saturn als Satzsubjekt (als Handelnder, nicht als Anker)")), "Lauf 5")
    st5 = {nr: p["status"] for nr, p in r5["proben"].items()}
    berichte.append("Lauf 5 (Transit, eingebaute Fehler): " + ", ".join("%s=%s" % kv for kv in st5.items()))
    # 5b) Lagebild ohne Kopfblock (W10) — ein Fehler, den bisher erst Schritt 3 fand
    a5b = ta.split("**Signatur:** Saturn im Quadrat zu deiner Sonne, im Anmarsch", 1)
    a5b = a5b[0] + "Am Stichtag" + a5b[1].split("\n\nAm Stichtag", 1)[1]
    r5b = lauf(tc, a5b, tev)
    erwarte(r5b, (("P14", "fehler", "Der Stand heute · Was gerade anliegt: Signatur und Beleg fehlen"),),
            "Lauf 5b")

    # 6) Transit ohne events.json: Form geprueft, Abgleich teilweise uebersprungen (W24, W44)
    r6 = lauf(tc, ta)
    st6 = {nr: p["status"] for nr, p in r6["proben"].items()}
    berichte.append("Lauf 6 (Transit ohne events.json): " + ", ".join("%s=%s" % kv for kv in st6.items()))
    assert r6["fehler"] == 0 and r6["pruefen"] == 0, "Lauf 6 nicht sauber: %s\n%s" % (st6, befunde(r6))
    assert [(nr, art) for nr, art, _g in r6["uebersprungen"]] == [
        ("P16", "aussagelos"), ("P1", "teilweise übersprungen"), ("P18", "teilweise übersprungen")] and \
        "events.json" in r6["uebersprungen"][1][2] and "events.json" in r6["uebersprungen"][2][2], \
        "Lauf 6: %s" % r6["uebersprungen"]
    # eine events.json, die es nicht gibt, bricht laut ab (Rueckgabewert 2 der CLI)
    d6 = tempfile.mkdtemp(prefix="inhaltsprobe_")
    pa6, pc6 = os.path.join(d6, "prueffall_analyse.md"), os.path.join(d6, "prueffall_chart_data.md")
    open(pa6, "w", encoding="utf-8").write(ta)
    open(pc6, "w", encoding="utf-8").write(tc)
    try:
        pruefe(pa6, pc6, None, os.path.join(d6, "fehlt_events.json"))
        raise AssertionError("fehlende events.json wurde nicht gemeldet")
    except InhaltsprobeFehler as e:
        assert "events.json nicht lesbar" in str(e), str(e)

    # 7) L7: die beiden Formen des Getriebe-Kapitels. Die Laeufe 1-3 pruefen die
    #    ALTE Form (Kicker `Kapitel 1` fuers Getriebe, Themen ab `Kapitel 2`);
    #    hier dieselbe Analyse in der NEUEN (Wort-Kicker `Getriebe`, `Kapitel n`
    #    = `THEMA n`, Typmodul seit 2026-09-19). Beide muessen sauber laufen.
    _alt = [{"kicker": "Kapitel 1", "title": "Was unter allem liegt"},
            {"kicker": "Kapitel 2", "title": "Ein Thema"}]
    _neu = [{"kicker": "Getriebe", "title": "Was unter allem liegt"},
            {"kicker": "Kapitel 1", "title": "Ein Thema"}]
    assert (_zaehlung_ab(_alt, "geburt"), _zaehlung_ab(_neu, "geburt"),
            _zaehlung_ab(_alt, "transit"), _zaehlung_ab(None, "geburt")) == (2, 1, 1, 2), \
        "L7: _zaehlung_ab erkennt die Form nicht"
    for _chs, _wo in ((_alt, "alte Form"), (_neu, "neue Form")):
        assert _kapitelart(_chs[0], "geburt", _chs) == "Getriebe-Kapitel" and \
            _kapitelart(_chs[1], "geburt", _chs) == "Themenkapitel", \
            "L7 (%s): _kapitelart verwechselt Getriebe- und Themenkapitel" % _wo
        assert _beleg_form(dict(_chs[0], beleg="Elemente Feuer 3 · Erde 1 · Luft 0 · "
                                "Wasser 1 · Herrscherkreis Sonne → Mars → Mond"),
                           "geburt", _chs) == "struktur", \
            "L7 (%s): Getriebe-Beleg nicht im Struktur-Format" % _wo
        assert _beleg_form(dict(_chs[1], beleg="Sonne ☉ 10°00′ Widder ♈, 1. Haus"),
                           "geburt", _chs) == "normal", \
            "L7 (%s): Beleg des ersten Themenkapitels nicht im Normalformat" % _wo
    a7 = ersetze(_TEST_ANALYSE, "## Kapitel 1 · Was unter allem liegt",
                 "## Getriebe · Was unter allem liegt")
    a7 = ersetze(a7, "## Kapitel 2 · Der Anfang", "## Kapitel 1 · Der Anfang")
    a7 = ersetze(a7, "## Kapitel 3 · Was hält", "## Kapitel 2 · Was hält")
    a7 = ersetze(a7, "steht in Kapitel 2.", "steht in Kapitel 1.")
    a7 = ersetze(a7, "Vorderseite von Kapitel 3.", "Vorderseite von Kapitel 2.")
    a7 = ersetze(a7, "Rückseite von Kapitel 2.", "Rückseite von Kapitel 1.")
    a7 = ersetze(a7, "Klingt mit in Kapitel 2.", "Klingt mit in Kapitel 1.")
    a7 = ersetze(a7, "Klingt mit in Kapitel 3.", "Klingt mit in Kapitel 2.")
    a7 = ersetze(a7, "Zusammenführung der Kapitel 2 und 3", "Zusammenführung der Kapitel 1 und 2")
    a7 = ersetze(a7, "Die Gegensatzpaare der Kapitel 2 und 3", "Die Gegensatzpaare der Kapitel 1 und 2")
    a7 = ersetze(a7, "Was aus den Kapiteln 2 und 3 als Richtung bleibt",
                 "Was aus den Kapiteln 1 und 2 als Richtung bleibt")
    z7 = ersetze(_TEST_ZUGANG, "(Kapitel 3)", "(Kapitel 2)")
    z7 = ersetze(z7, "sind in Kapitel 3 gedeutet", "sind in Kapitel 2 gedeutet")
    a7 = ersetze(a7, "## Rechenschaft · Was sonst in deinem Bild steht",
                 z7 + "## Rechenschaft · Was sonst in deinem Bild steht")
    c7 = ersetze(_TEST_CHART, "klingt mit in Kapitel 2.", "klingt mit in Kapitel 1.")
    c7 = ersetze(c7, "klingt mit in Kapitel 3.", "klingt mit in Kapitel 2.")
    r7 = lauf(c7, a7)
    st7 = {nr: p["status"] for nr, p in r7["proben"].items()}
    berichte.append("Lauf 7 (Getriebe-Kicker, neue Zählung): "
                    + ", ".join("%s=%s" % kv for kv in st7.items()))
    assert r7["fehler"] == 0 and r7["pruefen"] == 0 and \
        [nr for nr, _art, _g in r7["uebersprungen"]] == ["P1"], (
            "Lauf 7 nicht sauber: %s\n%s" % (st7, befunde(r7)))
    for nr in ("P1", "P3", "P4", "P14", "P15"):
        assert r7["proben"][nr]["geprueft"] == r3["proben"][nr]["geprueft"], (
            "Lauf 7: %s prüft %d Einheiten, in der alten Form (Lauf 3) %d"
            % (nr, r7["proben"][nr]["geprueft"], r3["proben"][nr]["geprueft"]))
    assert not r7["proben"]["P14"]["hinweise"], (
        "Lauf 7: P14 kennt einen Kicker nicht: %s" % r7["proben"]["P14"]["hinweise"])
    # 7b) neue Form, aber der Wort-Kicker fehlt: P3 meldet die Zahl UND nennt den
    #     Grund — sonst sucht der Lauf den Fehler in der Themenliste.
    r7b = lauf(c7, ersetze(a7, "## Getriebe · Was unter allem liegt",
                           "## Gesamtbild · Was unter allem liegt"))
    erwarte(r7b, (("P3", "fehler", "trägt das Getriebe-Kapitel den Wort-Kicker"),), "Lauf 7b")

    # 8) Transit: Deutungsort „Mitlaufendes (Deckel)“ (2026-09-24, T10)
    c8 = ersetze(tc, "T-Jupiter △ R-Mond    im Wirkorb    — Deutungsort: Thema 2",
                 "T-Jupiter △ R-Mond    im Wirkorb    — Deutungsort: Thema 2\n"
                 "T-Neptun ⚹ R-Mars    im Wirkorb    — Deutungsort: Mitlaufendes (Deckel)")
    r8 = lauf(c8, ta, tev)
    assert not r8["proben"]["P15"]["pruefen"] and r8["proben"]["P15"]["geprueft"] == 2, \
        "Lauf 8: Deckel-Eintrag nicht erkannt: %s" % r8["proben"]["P15"]["pruefen"]
    r8b = lauf(ersetze(c8, "T-Neptun ⚹ R-Mars    im Wirkorb    — Deutungsort: Mitlaufendes (Deckel)",
                       "T-Uranus △ R-Venus    im Wirkorb    — Deutungsort: Mitlaufendes (Deckel)"), ta, tev)
    erwarte(r8b, (("P15", "pruefen", "über dem Deckel, aber keine Zeile"),), "Lauf 8b")
    # 8c) Nachzug-Vermerk im Ortsfeld und eigene Nachzug-Zeile (2026-10-01, T4)
    r8c = lauf(ersetze(c8, "— Deutungsort: Mitlaufendes (Deckel)",
                       "— Deutungsort: Mitlaufendes (Deckel) (Nachzug: vorher Thema 2)\n"
                       "Nachzug: Deutungsort: Thema 2 → Mitlaufendes (Deckel)"), ta, tev)
    assert not r8c["proben"]["P15"]["pruefen"] and r8c["proben"]["P15"]["geprueft"] == 2, \
        "Lauf 8c: Nachzug als Ort gelesen: %s" % r8c["proben"]["P15"]["pruefen"]
    berichte.append("Lauf 8 (Transit, Deutungsort über dem Deckel): erkannt, 8b gemeldet, "
                    "8c Nachzug still")

    # 9) offene Fuehrung (2026-09-30, K9): die Sonne konstruiert offen zwischen
    #    Haus 1 und 2 — Beleg „1./2. Haus (gleich stark, …)", rechnerisch vorn
    c9 = ersetze(_TEST_CHART, "FAKTOR SONNE zeichen=Widder haus=1 fuehrt=ja",
                 "FAKTOR SONNE zeichen=Widder haus=1 nebenhaus=2 abstand=2.05 "
                 "fuehrung=offen fuehrt=ja")
    _alt9 = "Sonne ☉ 10°00′ Widder ♈, 1. Haus"
    assert _TEST_ANALYSE.count(_alt9) == 2, "Selbsttest-Marke Lauf 9"
    a9 = _TEST_ANALYSE.replace(_alt9, "Sonne ☉ 10°00′ Widder ♈, 1./2. Haus (gleich stark, "
                                      "2°03′ vor Spitze 2)")
    r9 = lauf(c9, a9)
    erwarte(r9, (("P2", "pruefen", "die Signatur sagt nicht „gleich stark“"),), "Lauf 9")
    assert not r9["proben"]["P2"]["fehler"], r9["proben"]["P2"]["fehler"]
    a9ok = ersetze(a9, "**Signatur:** Die Sonne im Widder im ersten Haus, verschmolzen mit "
                         "Merkur — mitklingend der Mond im Stier",
                   "**Signatur:** Sonne an der Schwelle zwischen dem ersten und dem zweiten "
                   "Haus, beide gleich stark, verschmolzen mit Merkur — mitklingend der Mond "
                   "im Stier")
    r9ok = lauf(c9, a9ok)
    assert not r9ok["proben"]["P2"]["pruefen"] and not r9ok["proben"]["P2"]["fehler"] \
        and not [t for t in r9ok["proben"]["P11"]["pruefen"] if "Geburtsminute" in t], (
        "Lauf 9 (sauber): %s" % befunde(r9ok))
    # 2026-10-01 (F1): der alte Pflichtsatz meldet jetzt P11
    r9s = lauf(c9, ersetze(a9ok, "die Sonne steht im Widder im ersten Haus.",
                           "die Sonne steht im Widder im ersten und zweiten Haus zugleich — "
                           "welches davon führt, kann deine Geburtszeit nicht entscheiden."))
    erwarte(r9s, (("P11", "pruefen", "Satz zur Geburtsminute"),), "Lauf 9s")
    r9f = lauf(c9, a9ok.replace("1./2. Haus (gleich stark", "2./1. Haus (gleich stark"))
    erwarte(r9f, (("P2", "fehler", "offene Führung: das rechnerische Haus vorn"),), "Lauf 9f")
    berichte.append("Lauf 9 (offene Führung): Signatur gemeldet, sauber still, Satz zur "
                    "Geburtszeit als P11, Reihenfolge als Fehler")

    # 10) „um die N" (2026-09-30, Klasse-2-Entscheidungslauf, Punkt 8): gedeckt
    #     vom Saturn-Fenster ~29.5 still und gezaehlt, ungedeckt gemeldet, ein
    #     folgendes Substantiv („um die zwölf Monate") keine Altersangabe.
    a10 = ersetze(_TEST_ANALYSE, "Saturn kehrt um die dreißig an seinen Ort zurück",
                  "Saturn kehrt um die neunundzwanzig an seinen Ort zurück")
    r10 = lauf(_TEST_CHART, a10)
    assert not r10["proben"]["P11"]["pruefen"], "Lauf 10: %s" % r10["proben"]["P11"]["pruefen"]
    assert r10["proben"]["P11"]["geprueft"] == r["proben"]["P11"]["geprueft"], (
        "Lauf 10: „um die neunundzwanzig“ nicht gezählt (%d gegen %d)"
        % (r10["proben"]["P11"]["geprueft"], r["proben"]["P11"]["geprueft"]))
    a10f = ersetze(_TEST_ANALYSE, "Saturn kehrt um die dreißig an seinen Ort zurück",
                   "Saturn kehrt um die siebenundvierzig an seinen Ort zurück, und um die "
                   "zwölf Monate später wird es ruhiger")
    r10f = lauf(_TEST_CHART, a10f)
    erwarte(r10f, (("P11", "pruefen", "Altersangabe „um die siebenundvierzig“"),), "Lauf 10f")
    assert not any("Altersangabe „um die zwölf" in t for t in r10f["proben"]["P11"]["pruefen"]), (
        "Lauf 10f: Zeitspanne als Alter gemeldet: %s" % r10f["proben"]["P11"]["pruefen"])
    berichte.append("Lauf 10 („um die N“): gedeckt still, ungedeckt gemeldet, Zeitspanne still")
    # 10g) 2026-10-09: „um die N" zaehlt genau N (nicht mehr N ± 1), „Um die …" auch am
    #      Satzanfang; ein folgendes Substantiv bleibt keine Altersangabe. Das Fenster
    #      ~43,9 steht als zusaetzliche Zeile in §7, die Saetze sind erfunden.
    c10g = ersetze(_TEST_CHART, "zweite Saturn-Opposition ~44.2 [bevorstehend]",
                   "zweite Saturn-Opposition ~44.2 [bevorstehend]\n"
                   "  - Uranus: Uranus-Opposition ~43.9 [bevorstehend]")
    _alt10 = "Saturn kehrt um die dreißig an seinen Ort zurück"
    r10g = lauf(c10g, ersetze(_TEST_ANALYSE, _alt10, _alt10 + ". Uranus steht seinem eigenen Stand "
                              "um die zweiundvierzig gegenüber"))
    erwarte(r10g, (("P11", "pruefen", "Altersangabe „um die zweiundvierzig“ (Alter 42)"),), "Lauf 10g")
    assert len(r10g["proben"]["P11"]["pruefen"]) == 1, ("Lauf 10g", r10g["proben"]["P11"]["pruefen"])
    r10h = lauf(c10g, ersetze(_TEST_ANALYSE, _alt10, _alt10 + ". Uranus steht seinem eigenen Stand "
                              "um die vierundvierzig gegenüber. Um die vierundvierzig steht Uranus "
                              "seinem eigenen Stand gegenüber. Um die zwölf Monate danach wird es ruhiger"))
    assert not r10h["proben"]["P11"]["pruefen"], ("Lauf 10h", r10h["proben"]["P11"]["pruefen"])
    assert r10h["proben"]["P11"]["geprueft"] == r["proben"]["P11"]["geprueft"] + 2, (
        "Lauf 10h: „Um die …“ am Satzanfang nicht gezählt oder „Um die zwölf Monate“ als Alter "
        "gezählt (%d gegen %d)" % (r10h["proben"]["P11"]["geprueft"], r["proben"]["P11"]["geprueft"]))
    berichte.append("Lauf 10g (um die N genau N, 2026-10-09): „um die zweiundvierzig“ gegen ~43,9 "
                    "gemeldet, „um die vierundvierzig“ still, „Um die …“ am Satzanfang gezählt und "
                    "still, „Um die zwölf Monate“ keine Altersangabe")

    # 11) Altersreihe (2026-10-01b, Pruefbericht Transit 1+2 vom 01.10., K1): jedes
    #     Glied von „als du X und Y warst“ gezaehlt und geprueft; „im …jährigen Umlauf“
    #     ist eine Dauer, kein Alter. Saetze konstruiert.
    a11 = ersetze(_TEST_ANALYSE, "Saturn kehrt um die dreißig an seinen Ort zurück",
                  "Saturn kehrt an seinen Ort zurück, als du neunundzwanzig und "
                  "vierundvierzig warst, im neunundzwanzigjährigen Umlauf")
    r11 = lauf(_TEST_CHART, a11)
    assert not r11["proben"]["P11"]["pruefen"], "Lauf 11: %s" % r11["proben"]["P11"]["pruefen"]
    assert r11["proben"]["P11"]["geprueft"] == r["proben"]["P11"]["geprueft"] + 1, (
        "Lauf 11: Reihe nicht je Glied gezählt oder „-jährigen Umlauf“ als Alter (%d gegen %d)"
        % (r11["proben"]["P11"]["geprueft"], r["proben"]["P11"]["geprueft"]))
    a11f = ersetze(_TEST_ANALYSE, "Saturn kehrt um die dreißig an seinen Ort zurück",
                   "Saturn kehrt an seinen Ort zurück, als du neunundzwanzig und "
                   "siebenundvierzig warst")
    r11f = lauf(_TEST_CHART, a11f)
    erwarte(r11f, (("P11", "pruefen", "(siebenundvierzig)“ (Alter 47)"),), "Lauf 11f")
    assert len(r11f["proben"]["P11"]["pruefen"]) == 1, r11f["proben"]["P11"]["pruefen"]
    berichte.append("Lauf 11 (Altersreihe): jedes Glied gezählt, ungedeckt gemeldet, "
                    "„-jährigen Umlauf“ kein Alter")

    # 12) P18 Satzarten (2026-10-04, Wartungslauf Satzarten-Probe): erfundene Saetze auf
    #     den konstruierten Prueffaellen — je Satzart ein Widerspruch zu den Daten
    #     (gemeldet, mit dem Datenwert) und eine stimmige Fassung (still). Vorweg die Muster.
    assert _p18_region("das Viertel von Auftreten, Besitz und Sprache")[0] == {1, 2, 3}
    assert _p18_region("liegt in den Zwillingen, im achten Haus")[:2] == ({8}, {"ZWILLINGE"})
    assert [hs for _a, _e, hs in _p18_haeuser_in("die Häuser 4–6")] == [{4, 5, 6}]
    assert not _p18_zeiten_ohne_bis("bis Anfang April 2031") and _p18_zeiten_ohne_bis("ab Anfang April 2031")
    for _s, _art in (("Saturn reibt sich an deiner Lilith", "Quadrat"),
                     ("Jupiter fließt mühelos mit deiner Lilith", "Trigon"),
                     ("Mars öffnet dir eine Tür zu deiner Lilith", "Sextil"),
                     ("Saturn steht deiner Venus gegenüber", "Opposition"),
                     ("Uranus geht über deinen Mond", "Konjunktion")):
        assert _art in _p18_aspektarten(_s), "P18 Aspektbild: %r" % _s
    _g18 = [(ls, zs) for _a, _e, ls, zs in
            _p18_gruppen("Uranus steht seit dem Herbst 2031 an deinem Mars, Pluto seit Juni 2032.")]
    assert _g18 == [(["URANUS"], ["MARS"]), (["PLUTO"], [])], "P18 neue Laeufer-Gruppe: %r" % _g18
    _g18 = [(ls, zs) for _a, _e, ls, zs in _p18_gruppen("Im Sextil zu deinem Mars stand Saturn zuletzt.")]
    assert _g18 == [(["SATURN"], ["MARS"])], "P18 Ziel vor dem Laeufer: %r" % _g18
    # 12a) Geburtshoroskop: §3, §6 und ein Untergrund kommen zum konstruierten Datenblatt
    c12 = ersetze(_TEST_CHART, "### Untergrund-Aspekte\n\n_keine_\n",
                  "### Untergrund-Aspekte\n\n| Faktor | Aspekt | Faktor | Orb | gedeutet |\n"
                  "|---|---|---|---|---|\n| Merkur | ∠ Halbquadrat | Saturn | 0°20′ | ja |\n"
                  "| Mond | ⚼ Anderthalbquadrat | Mars | 1°30′ | nein |\n")
    c12 = ersetze(c12, "## Strukturbild (konstruiert)\n",
                  "## Strukturbild (konstruiert)\n\n### 3 · Hausherrscher\n"
                  "- Hausherrscher (Spitzenzeichen → Herrscher → wo er steht):\n"
                  "  - Haus  1 (Widder) → Mars in Krebs, Haus 4/3\n"
                  "  - Haus  4 (Krebs) → Mond in Stier, Haus 2\n"
                  "  - Haus  6 (Jungfrau) → Merkur in Widder, Haus 1\n"
                  "  - Haus 10 (Steinbock) → Saturn in Jungfrau, Haus 6\n\n### 6 · Figuren\n"
                  "- T-Quadrat: Mars ☍ MC, Brennpunkt AC — leere Spitze 25°00′ Widder, Haus 1; dort: nichts\n")

    def _a12(arbeitet, wohin, getriebe, rechenschaft, wohin3):
        a_ = ersetze(_TEST_ANALYSE, "sucht den ersten Schritt, weil dort die Kraft ist.",
                     "sucht den ersten Schritt, weil dort die Kraft ist.\n\n" + "\n\n".join(arbeitet))
        a_ = ersetze(a_, "ist die Landkarte, nicht der Weg.", "ist die Landkarte, nicht der Weg.\n\n"
                     + "\n\n".join(wohin))
        a_ = ersetze(a_, "Was fehlt, ersetzt die Anstrengung.", "Was fehlt, ersetzt die Anstrengung.\n\n"
                     + "\n\n".join(getriebe)) if getriebe else a_
        a_ = ersetze(a_, "Was dazwischen liegt, steht hier.", "Was dazwischen liegt, steht hier.\n\n"
                     + "\n\n".join(rechenschaft))
        return ersetze(a_, "Es ist eine ruhige Stelle in deinem Bild.",
                       "Es ist eine ruhige Stelle in deinem Bild.\n\n" + "\n\n".join(wohin3))
    # stimmig, und dazu Wendungen, die nach einer Satzart aussehen und keine sind
    a12ok = _a12(["Die offene Ecke des Dreiecks fällt in den Widder und ins erste Haus; der Punkt "
                  "selbst ist unbesetzt.", "Das siebte Haus ist leer.",
                  "Saturn, der Verwalter des zehnten Hauses, hält den Rahmen.",
                  "Im ersten Haus stehen Sonne und Merkur, beide im Widder; dort steht sonst nichts.",
                  "Das vierte Haus ist leer bis auf Mars.",
                  "Kein Planet steht so nah an deinem AC wie deine Sonne im ersten Haus.",
                  "Dein Mars steht im Krebs, und darin liegt keine Schwäche, sondern eine Stärke.",
                  "Mars reibt sich an deinem Mond. Er ist zugleich der Verwalter deines ersten Hauses."],
                 ["Kapitel 3 zeigt, wie Mond und Saturn einander halten.",
                  "Anders als Kapitel 3 erzählt dieses Kapitel von Sonne und Merkur.",
                  "Mehr dazu steht in Kapitel 3, „Was hält, wenn nichts drängt“."], [],
                 ["In der Aspekttabelle findest du zwei Verbindungen: zwischen Sonne und Merkur "
                  "und zwischen Mond und Saturn."],
                 ["Mehr dazu sagt im Kapitel Hauptthemen der Abschnitt „Was trägt“."])
    # 2026-10-13 (a4): mit dem GEDEUTETEN Untergrund (0°20′, ja) bleibt „die engste Verbindung
    # zwischen zwei Planeten in deinem Bild“ still — ohne Zusatz gilt die Rangzeile
    r12 = lauf(c12, a12ok)["proben"]["P18"]
    assert r12["status"] == "OK" and r12["geprueft"] >= 6, ("Lauf 12: P18 nicht still", r12["geprueft"],
                                                            r12["pruefen"])
    a12 = _a12(["Die offene Ecke des Dreiecks fällt in den Widder und ins erste Haus; dort steht nichts.",
                "Das Viertel von Herkunft, Ausdruck und Alltag ist leer.",
                "Saturn, der Verwalter des vierten Hauses, hält den Rahmen.", "Dein Mond steht auf eigenem Boden.",
                "Das ist der Pflichtteil dieses Kapitels."],
               ["Kapitel 3 zeigt, wie Sonne und Merkur ineinandergreifen.",
                "Mehr dazu steht in Kapitel 3, „Der Anfang, der sich selbst genügt“."],
               ["Dein Wille fängt an — alles andere hält fest."],
               ["In der Aspekttabelle findest du drei Verbindungen: zwischen Sonne und Merkur, "
                "zwischen Mond und Saturn und zwischen Mond und Mars."],
               ["Mehr dazu sagt im Kapitel Hauptthemen der Abschnitt „Was fehlt“."])
    a12 = ersetze(a12, "**Signatur:** Zusammenführung der Kapitel 2 und 3", "**Signatur:** Zusammenführung von Kapitel 2")
    # 2026-10-13 (a4): erst „in deinem ganzen Bild“ zaehlt den Untergrund mit
    a12 = ersetze(a12, "zwischen zwei Planeten in deinem Bild", "zwischen zwei Planeten in deinem ganzen Bild")
    r12f = lauf(c12, a12)
    erwarte(r12f, (("P18", "pruefen", "„dort steht nichts“ — Haus 1: Sonne, Merkur (am Punkt selbst laut §6: nichts)"),
                   ("P18", "pruefen", "„ist leer“ — Häuser 4–6: Mars (4/3), Saturn"),
                   ("P18", "pruefen", "Haus 4 (Krebs) → Mond (Strukturbild §3); Saturn verwaltet Haus 10"),
                   ("P18", "pruefen", "Mond in Stier (Herrscher: Venus), Haus 2; zu Hause ist Mond in Krebs"),
                   ("P18", "pruefen", "Modulwort: „Pflichtteil“"),
                   ("P18", "pruefen", "Kapitel 3: Sonne–Merkur nicht in der THEMA-Zeile; gedeutet in Kapitel 2"),
                   ("P18", "pruefen", "Kapitel 3 heißt „Was hält, wenn nichts drängt“; „Der Anfang, der sich "
                                      "selbst genügt“ ist Kapitel 2"),
                   ("P18", "pruefen", "Abschnitt „Was fehlt“ — im Kapitel Hauptthemen: „Was trägt“"),
                   ("P18", "pruefen", "Anteil: „alles andere … fix“"),
                   ("P18", "pruefen", "Mond Anderthalbquadrat Mars 1°30′ steht nur im Untergrund"),
                   ("P18", "pruefen", "Merkur Halbquadrat Saturn 0°20′; damit steht Sonne Konjunktion Merkur "
                                      "1°10′ auf Rang 2"),
                   ("P18", "pruefen", "die Signatur nennt Kapitel 2")), "Lauf 12 (P18)")
    assert len(r12f["proben"]["P18"]["pruefen"]) == 12, r12f["proben"]["P18"]["pruefen"]
    assert all(z.split(" — ", 1)[1:] for z in r12f["proben"]["P18"]["pruefen"]), "P18 ohne Datenwert"
    berichte.append("Lauf 12 (P18 Geburtshoroskop): stimmige Sätze still, je Satzart der Widerspruch "
                    "gemeldet (Leere, Herrscher, Kapitelverweis, Titel, Abschnitt, Signatur, Modulwort, "
                    "Dokument, Rang, Anteil)")
    # 12b) 2026-10-06 (FFU 05.10.): Rueckverweis auf die Paare des Satzes davor. Konstruiert.
    _c12b = c12.replace("| 0°20′ | ja |", "| 0°20′ | nein |")

    def _p18_12b(rechenschaft):
        return lauf(_c12b, _a12([], [], [], rechenschaft, []))["proben"]["P18"]
    _r = _p18_12b(["Im Untergrund liegen Spannungen zwischen Mond und Mars und zwischen Merkur und Saturn. "
                   "Beide stehen vollständig in der Aspekttabelle."])
    _dok = [z for z in _r["pruefen"] if "— Dokument:" in z]
    assert len(_dok) == 1 and "Mond Anderthalbquadrat Mars 1°30′ steht nur im Untergrund" in _dok[0] \
        and "Merkur Halbquadrat Saturn 0°20′ steht nur im Untergrund" in _dok[0], ("Lauf 12b Beide", _r["pruefen"])
    _r = _p18_12b(["Im Untergrund liegt eine Spannung zwischen Mond und Mars. Sie steht in der Aspekttabelle."])
    assert [z for z in _r["pruefen"] if "— Dokument:" in z], ("Lauf 12b Sie", _r["pruefen"])
    for _still in ("Im Untergrund liegen Spannungen zwischen Mond und Mars und zwischen Merkur und Saturn. "
                   "In der Aspekttabelle stehen beide nicht.",
                   "Im Untergrund liegt eine Spannung zwischen Mond und Mars. "
                   "Alle anderen Verbindungen stehen in der Aspekttabelle.",
                   "Im Untergrund liegt eine Spannung zwischen Mond und Mars.\n\n"
                   "Sie steht vollständig in der Aspekttabelle."):
        _r = _p18_12b([_still])
        assert not [z for z in _r["pruefen"] if "— Dokument:" in z], ("Lauf 12b still", _still, _r["pruefen"])
    berichte.append("Lauf 12b (P18 Dokument, Rückverweis): „Beide/Sie … in der Aspekttabelle“ hält die Paare "
                    "des Satzes davor; Verneinung, „alle anderen“ und neuer Absatz bleiben still")
    # 13) P18 Transit: Zeit, Zugleich, Station, Anzahl, Wiederholung, Zeichenaufenthalt
    tc13, ta13, tev13, w13 = _transit_fall()
    for _x in tev13["jetzt"]["im_orb"]:
        _x.update(im_wirkorb=_x["orb_grad"] <= 1.5, primaer=True, spiegel=False)
    tev13["zeichenaufenthalt"] = [{"transit": "Saturn", "zeichen": "Krebs", "von": w13["d300"], "bis": w13["d730"]}]

    def _st13(orb):
        return [{"transit": "Saturn", "datum": w13["d130"], "richtung": "wird rückläufig", "stand": "Krebs 8°45'",
                 "nahe_detail": [{"ziel": "Sonne", "aspekt": "Quadrat", "orb": orb, "spiegel": False}]}]

    def _a13(saetze):
        return ersetze(ta13, "und macht das Denken vorsichtiger.",
                       "und macht das Denken vorsichtiger.\n\n" + "\n\n".join(saetze))
    ok13 = ["Ab %s steht Saturn im Quadrat zu deiner Sonne." % w13["m20"],
            "Saturn beginnt im %s im Quadrat zu deiner Sonne." % w13["m20"],
            "Saturn trifft deine Sonne im %s zum ersten Mal genau im Quadrat." % w13["m60"],
            "Saturn und Jupiter stehen zugleich an deinem Merkur und deinem Mond.",
            "Im %s kommt Saturn genau im Quadrat zu deiner Sonne zum Stillstand." % w13["m130"],
            "Am Stichtag liegen drei Kontakte im engen Wirkorb.",
            "Zuletzt stand Saturn so wie jetzt im Quadrat zu deiner Sonne, als du zwölf warst.",
            "Ab %s steht Saturn im Krebs." % w13["m300"],
            "Saturn beginnt im %s die rückläufige Strecke im Quadrat zu deiner Sonne." % w13["m110"],
            "Im %s kommt Saturn zum Stillstand, im Quadrat zu deiner Sonne, und im %s wird das Quadrat "
            "noch einmal genau." % (w13["m130"], w13["m200"]),
            "In deinem Geburtsbild stehen Neptun und Jupiter zugleich nah bei deinem Mars.",
            "Saturn stand zuletzt in derselben Stellung zu deiner Sonne, als du zwölf warst; "
            "Jupiter zuletzt, als du "
            "vierzig warst."]
    r13 = lauf(tc13, _a13(ok13), dict(tev13, stations=_st13(0.2)))["proben"]["P18"]
    assert r13["status"] == "OK" and r13["geprueft"] >= 8, ("Lauf 13: P18 nicht still", r13["geprueft"],
                                                            r13["pruefen"])
    r13f = lauf(tc13, _a13(["Ab %s steht Saturn im Quadrat zu deiner Sonne." % w13["m110"],
                            "Saturn beginnt im %s im Quadrat zu deiner Sonne." % w13["m110"],
                            "Saturn trifft deine Sonne im %s zum ersten Mal genau im Quadrat." % w13["m100"],
                            "Neptun und Jupiter stehen zugleich an deinem Mars und deinem Mond.",
                            ok13[4], "Am Stichtag liegen zwei Kontakte im engen Wirkorb.",
                            "Im Quadrat zu deiner Sonne war Saturn zuletzt, als du zwanzig warst.",
                            "Ab %s steht Saturn im Krebs." % w13["m110"]]), dict(tev13, stations=_st13(1.25)))
    erwarte(r13f, (("P18", "pruefen", "„ab %s“ — Saturn Quadrat Sonne läuft schon" % w13["m110"]),
                   ("P18", "pruefen", "„beginnt“ (%s) — Saturn Quadrat Sonne: Wirkorb ab %s" % (w13["m110"], w13["e20"])),
                   ("P18", "pruefen", "Saturn Quadrat Sonne: zum ersten Mal exakt am %s" % w13["e60"]),
                   ("P18", "pruefen", "Neptun, Jupiter gleichzeitig im Wirkorb (an Mars, Mond): an keinem Tag"),
                   ("P18", "pruefen", "Quadrat Sonne 1°15′ (genau heißt: Orb höchstens 0°30′)"),
                   ("P18", "pruefen", "am Stichtag im Wirkorb: 3"),
                   ("P18", "pruefen", "„zwanzig“ (20) — Saturn Quadrat Sonne; frühere Durchgänge in derselben "
                                      "Hälfte des Umlaufs: Alter 12"),
                   ("P18", "pruefen", "Saturn steht ab %s in Krebs (Zeichenaufenthalt" % w13["e300"])), "Lauf 13 (P18)")
    assert len(r13f["proben"]["P18"]["pruefen"]) == 8, r13f["proben"]["P18"]["pruefen"]
    berichte.append("Lauf 13 (P18 Transit): stimmige Sätze still, je Satzart der Widerspruch gemeldet "
                    "(Zeit: läuft schon, beginnt, zum ersten Mal genau, Zeichen; Zugleich, Station, "
                    "Anzahl, Wiederholung)")
    # 13c) 2026-10-07: Wiederholungshinweis ohne Stellung (Aspekt mit zwei Haelften)
    tev13c = json.loads(json.dumps(tev13))
    tev13c["fruehere_durchgaenge"].append(
        {"transit": "Knoten", "aspekt": "Konjunktion", "ziel": "Merkur", "primaer": True,
         "selbst_transit": False,
         "durchgaenge": [{"nr": 1, "von": w13["dM2500"], "bis": w13["dM2500"],
                          "exakt": [{"datum": w13["dM2500"], "alter": 18}], "annaeherung": [],
                          "min_orb_grad": 0.0, "min_orb_datum": w13["dM2500"], "min_orb_alter": 18,
                          "ab_rechenbeginn": False}]})
    falsch13c = ["Zuletzt stand Saturn im Quadrat zu deiner Sonne, als du zwölf warst.",
                 "Dieselbe Verbindung, Saturn im Quadrat zu deiner Sonne, lief zuletzt, als du zwölf warst."]
    still13c = ["Zuletzt stand Saturn so wie jetzt zu deiner Sonne, als du zwölf warst.",
                "Dieselbe Frage stand zuletzt an, als du zwölf warst.",
                "Zuletzt stand Saturn vom Krebs aus im Quadrat zu deiner Sonne, als du zwölf warst.",
                "Zuletzt stand der Mondknoten auf deinem Merkur, als du achtzehn warst."]
    r13c = lauf(tc13, _a13(falsch13c + still13c), dict(tev13c, stations=_st13(0.2)))["proben"]["P18"]
    _st13c = [z for z in r13c["pruefen"] if "ohne Stellung" in z]
    assert len(_st13c) == 2 and all(any(f[:40] in z for z in _st13c) for f in falsch13c), \
        ("Lauf 13c: ohne Stellung nicht gemeldet", r13c["pruefen"])
    assert not [z for z in r13c["pruefen"] for f in still13c if f[:40] in z], \
        ("Lauf 13c: stimmige Wiederholung gemeldet", r13c["pruefen"])
    berichte.append("Lauf 13c (P18 Wiederholung, Stellung): Quadrat ohne Stellung gemeldet, auch mit "
                    "richtigem Alter; „so wie jetzt“, „vom … aus“, „Dieselbe Frage“ und Konjunktion still")
    # 13d) 2026-10-07b: verneinter Wiederholungshinweis („seit deiner Geburt nie“)
    tev13d = json.loads(json.dumps(tev13c))
    tev13d["fruehere_durchgaenge"] += [
        {"transit": "Uranus", "aspekt": "Trigon", "ziel": "Mond", "primaer": True,
         "selbst_transit": False, "durchgaenge": []},
        {"transit": "Pluto", "aspekt": "Konjunktion", "ziel": "Mond", "primaer": True,
         "selbst_transit": False, "durchgaenge": []}]
    falsch13d = ["Uranus stand seit deiner Geburt noch nie im Trigon zu deinem Mond.",
                 "Der Mondknoten stand seit deiner Geburt nie auf deinem Merkur.",
                 "Keine dieser Verbindungen gab es seit deiner Geburt."]
    still13d = ["Uranus stand seit deiner Geburt noch nie so wie jetzt im Trigon zu deinem Mond.",
                "Pluto stand seit deiner Geburt nie auf deinem Mond.",
                "Seit deiner Geburt hat sich viel verändert.",
                "Im Juni wird das Trigon des Uranus zu deinem Mond zum ersten Mal genau."]
    r13d = lauf(tc13, _a13(falsch13d + still13d), dict(tev13d, stations=_st13(0.2)))["proben"]["P18"]
    _st13d = [z for z in r13d["pruefen"] if "verneint frühere Durchgänge" in z]
    assert len(_st13d) == 3 and all(any("„%s“" % f in z for z in _st13d) for f in falsch13d), \
        ("Lauf 13d: Verneinung nicht gemeldet", r13d["pruefen"])
    assert any("ohne Stellung — Uranus Trigon Mond" in z for z in _st13d), ("Lauf 13d: Stellung", _st13d)
    assert any("Konjunktion Merkur (Alter 18)" in z for z in _st13d), ("Lauf 13d: Alter", _st13d)
    assert not [z for z in _st13d for f in still13d if "„%s“" % f in z], \
        ("Lauf 13d: stimmige Verneinung gemeldet", _st13d)
    berichte.append("Lauf 13d (P18 Wiederholung, Verneinung): „seit deiner Geburt nie“ bei zwei Hälften "
                    "ohne Stellung gemeldet, ebenso bei einem früheren Durchgang derselben Hälfte und für "
                    "„Keine dieser Verbindungen“; mit „so wie jetzt“, bei Konjunktion ohne Durchgang, "
                    "ohne Verneinung und ohne „seit deiner Geburt“ still")
    # 13e) 2026-10-09: Rueckkehr-Satzteil ohne eigenes Paar bleibt still, statt auf den
    #      fuehrenden Kontakt des Kapitels (hier Saturn □ Sonne, Alter 12) zurueckzufallen;
    #      mit eigenem Paar und ohne Rueckkehr-Wort wird weiter gemeldet. Saetze erfunden.
    still13e = ["Die Knotenrückkehr stand zuletzt an, als du achtzehn warst.",
                "Zuletzt kehrte er an seinen Ausgangspunkt zurück, als du achtzehn warst.",
                "Die Wiederkehr dieser Achse stand zuletzt an, als du achtzehn warst."]
    falsch13e = ["Bei der Rückkehr dieses Quadrats stand Saturn zuletzt so wie jetzt zu deiner Sonne, "
                 "als du zwanzig warst.",
                 "Dieselbe Frage stand zuletzt an, als du zwanzig warst."]
    r13e = lauf(tc13, _a13(still13e + falsch13e), dict(tev13c, stations=_st13(0.2)))["proben"]["P18"]
    assert not [z for z in r13e["pruefen"] for s in still13e if s[:40] in z], \
        ("Lauf 13e: Rückkehr ohne eigenes Paar gemeldet", r13e["pruefen"])
    for f in falsch13e:
        assert any(f[:40] in z and "„zwanzig“ (20) — Saturn Quadrat Sonne" in z for z in r13e["pruefen"]), \
            ("Lauf 13e: falsches Alter nicht gemeldet", f, r13e["pruefen"])
    berichte.append("Lauf 13e (P18 Wiederholung, Rückkehr, 2026-10-09): „Rückkehr“, „Wiederkehr“, "
                    "„kehrt … zurück“ ohne eigenes Paar still; mit eigenem Paar und ohne Rückkehr-Wort "
                    "das falsche Alter weiter gemeldet")

    # Lauf 14 (P19 Wiederholung, 2026-10-11): Formel in drei Kapiteln am selben Ort
    # und ein wortgleicher Satz dreimal -> PRUEFEN; die Wegweiser und eine Formel in nur
    # zwei Kapiteln still. Saetze erfunden.
    _e14 = []
    for _k, _w, _v in (("Kapitel 1", "Abend", "Abends merkst du es."),
                       ("Kapitel 2", "Morgen", "Beim Aufstehen fällt es dir auf."),
                       ("Kapitel 3", "Mittag", "Zwischendurch spürst du es.")):
        _e14 += [(_k, "Woran du es merkst", "%s Und ein Letztes, das schwerer "
                  "zuzugeben ist: Am %s ist es dir manchmal recht." % (_v, _w)),
                 (_k, "Die zwei Formen und das Dazwischen", "In der reifen Form wird daraus am "
                  "%s Ruhe. In der regressiven Form wird daraus am %s Starre. Dazwischen liegt "
                  "der Normalfall." % (_w, _w)),
                 (_k, "Womit du arbeiten kannst", "Das Erste: einmal am %s bemerken. Was du nicht "
                  "tun solltest: dich am %s zwingen. Gut genug ist es, wenn du es am %s einmal "
                  "merkst." % (_w, _w, _w)),
                 (_k, "Wie so etwas zur Regel wird", "Prüf an dir, ob dir das bekannt vorkommt.")]
    _e14 += [("Kapitel 4", "Wohin das gehört", "Zur Größenordnung: Das ist kein Randthema."),
             ("Kapitel 5", "Wohin das gehört", "Zur Größenordnung: Das ist ein leises Thema.")]
    _w14 = wiederholungen(_e14)
    _arten = sorted((w["art"], w["text"][:20]) for w in _w14)
    assert _arten == [("anfang", "Prüf an dir, ob dir "), ("anfang", "Und ein Letztes, das"),
                      ("satz", "Prüf an dir, ob dir ")], ("Lauf 14: P19", _w14)
    assert all(not WEGWEISER_RE.match(w["text"]) for w in _w14), ("Lauf 14: Wegweiser gemeldet", _w14)
    assert wiederholungen(_e14, satzanfaenge=False) and all(
        w["art"] == "satz" for w in wiederholungen(_e14, satzanfaenge=False)), "Lauf 14: nur Satz"
    # Nachtrag nach der Leseprobe (2026-10-11): Ressourcen-Formen, Transit-Wiederholungshinweis
    # in drei Formen, zweiter Satz der Kinder-Vorlage; ein Etikett mit Zusatz ist kein Wegweiser.
    for _s in ("In der genutzten Form bleibt es leicht.", "In ihrer verschleuderten Form wird es laut.",
               "Zuletzt stand Jupiter so wie jetzt, als du fünfzehn warst.",
               "Zuletzt stand der Saturn so wie jetzt, als du neunundzwanzig warst.",
               "Dieselbe Frage stand zuletzt an, als du zwölf warst.",
               "Der Durchgang davor in derselben Stellung lief, als du acht warst.",
               "Dann sprich möglichst bald darüber mit einem Erwachsenen, dem du vertraust."):
        assert WEGWEISER_RE.match(_s), ("Lauf 14: Wegweiser nicht erkannt", _s)
    for _s in ("Das Zweite, allein: einmal bemerken.", "Zuletzt war es leichter als jetzt.",
               "Dieselbe Frage kommt wieder."):
        assert not WEGWEISER_RE.match(_s), ("Lauf 14: kein Wegweiser", _s)
    berichte.append("Lauf 14 (P19 Wiederholung, 2026-10-11): Formel in drei Kapiteln am selben Ort "
                    "und wortgleicher Satz dreimal gemeldet; Wegweiser und eine Formel in zwei "
                    "Kapiteln still; Ressourcen-Formen, Transit-Wiederholungshinweis und "
                    "Kinder-Vorlage ausgenommen, Etikett mit Zusatz nicht")
    # Lauf 14b (P19, 2026-10-13): Das Register `Mitlaufendes` zaehlt nicht mit, wie die
    # Rechenschaft — deutsch und englisch; dieselben Zeilen in einem Kapitel werden
    # gemeldet. Saetze erfunden.
    _z14b = [{"type": "p", "text": "Jupiter im Sextil zu deinem Mond, Mai 2027. Klingt in Kapitel 3 mit."},
             {"type": "p", "text": "Saturn im Trigon zu deiner Venus, Juni 2027. Klingt in Kapitel 3 mit."},
             {"type": "p", "text": "Uranus im Quadrat zu deinem Mars, Juli 2027. Klingt in Kapitel 3 mit."}]
    for _kick in ("Mitlaufendes", "Running alongside"):
        _p14b = _p19_wiederholung([{"kicker": _kick, "title": "T", "blocks": _z14b}], "transit")
        assert _p14b.status == "OK" and not _p14b.pruefen, ("Lauf 14b: Register gemeldet", _kick, _p14b.pruefen)
    _p14c = _p19_wiederholung([{"kicker": "Kapitel 3", "title": "T", "blocks": _z14b}], "transit")
    assert _p14c.pruefen, ("Lauf 14b: Wiederholung im Kapitel nicht gemeldet", _p14c.status)
    berichte.append("Lauf 14b (P19, 2026-10-13): das Register „Mitlaufendes“ zählt nicht mit, "
                    "deutsch und englisch; dieselben Zeilen in einem Kapitel gemeldet")

    # Lauf 15 (P18 Transit, 2026-10-13, Strang 1 des Wartungslaufs „Proben fuer Zeit,
    # Naehe, Register und Fundstellen“): Grenze, Wechsel, Abstand, Buendel (Fliesstext
    # und Signatur), Genau, Kapitelzeit, Dauer, Zugleich mit EINEM Laeufer und „In
    # dieselben Wochen“ — je Satzart eine stimmige Fassung (still) und eine
    # widerspruechliche (gemeldet, mit dem Datenwert). Saetze erfunden, Daten konstruiert.
    w = w13
    tev15 = json.loads(json.dumps(tev13))
    _vorlage15 = json.dumps(tev15["events"][0])

    def _ev15(t, a, z, ex, von, bis):
        e = json.loads(_vorlage15)
        exs = [w["d%d" % x] for x in ex]
        e.update({"transit": t, "aspekt": a, "ziel": z, "exakt": exs, "exakt_im_fenster": exs,
                  "exakt_gesamt": exs, "fenster_von": w["d%d" % von], "fenster_bis": w["d%d" % bis],
                  "weit_von": w["d%d" % von], "weit_bis": w["d%d" % bis],
                  "perioden": [[w["d%d" % von], w["d%d" % bis]]],
                  "wirkorb_perioden": [[w["d%d" % von], w["d%d" % bis]]],
                  "kontakte": len(exs), "mehrfach": len(exs) > 1})
        return e
    tev15["events"] += [_ev15("Neptun", "Quadrat", "Mond", (201,), 200, 230),
                        _ev15("Neptun", "Trigon", "Sonne", (500,), 500, 520)]
    tev15["hausdurchgang"] = [{"transit": "Saturn", "haus": 4, "von": w["d250"], "bis": w["d730"],
                               "laeuft_weiter": True}]
    tev15["zusatz"] = {"sonnenbogen": [{"punkt": "Mars", "aspekt": "Konjunktion", "ziel": "Mond",
                                        "exakt": w["d100"]}]}
    tev15["quarter_bounds"] = [w["d0"], w["d100"], w["d200"], w["d300"], _p18_plus(w["d730"], 1)]
    tev15["stations"] = _st13(0.2)
    tc15 = ersetze(tc13, "@@SELEKTOR", "@@ZEITLEISTE\nQ1 | dicht=1 | marke=\nQ2 | dicht=1,2 | marke=\n"
                   "Q3 | dicht=1 | marke=\nQ4 | dicht=1 | marke=\n@@ENDE\n\n@@SELEKTOR")

    def _a15(basis, saetze):
        return ersetze(basis, "und macht das Denken vorsichtiger.",
                       "und macht das Denken vorsichtiger.\n\n" + "\n\n".join(saetze))
    ok15 = ["Saturn steht bis in den %s im Quadrat zu deiner Sonne." % w["m360"],
            "Saturn rückt im %s in den Krebs." % w["m300"],
            "Ab %s steht Saturn in deinem vierten Haus." % w["m250"],
            "Im %s steht Saturn im Quadrat zu deinem Merkur, gut zwei Wochen nach dem Kontakt zu deiner "
            "Sonne." % w["m75"],
            "Im %s, rund sechs Wochen nach dem ersten Durchgang, erreicht dein Mars im Sonnenbogen "
            "deinen Mond." % w["m100"],
            "Im %s steht Saturn im Quadrat zu deiner Sonne, mit dem Merkur im Gefolge." % w["m60"],
            "Saturn steht im %s und im %s im Quadrat zu deiner Sonne. Dazwischen steht Saturn im Quadrat zu "
            "deinem Merkur, genau im %s und im %s." % (w["m60"], w["m330"], w["m75"], w["m190"]),
            "Saturn steht im Quadrat zu deiner Sonne und deinem Merkur.",
            "Saturn steht genau im %s, im %s und im %s im Quadrat zu deiner Sonne."
            % (w["m60"], w["m200"], w["m330"]),
            "Im %s laufen zwei Kapitel nebeneinander." % w["m150"],
            "Im %s läuft auch Kapitel 2 mit." % w["m150"],
            "Im %s ist der Auftakt von Kapitel 1." % w["m20"],
            "Saturn bleibt den größten Teil der Zeit im vierten Haus deines Bildes.",
            "Saturn steht im Quadrat zu deiner Sonne und zugleich im Quadrat zu deinem Merkur.",
            "Saturn steht im %s im Quadrat zu deiner Sonne. In dieselben Wochen steht Neptun im Quadrat zu "
            "deinem Mond." % w["m200"]]
    r15 = lauf(tc15, _a15(ta13, ok15), tev15)["proben"]["P18"]
    assert r15["status"] == "OK" and r15["geprueft"] >= 15, ("Lauf 15: P18 nicht still", r15["geprueft"],
                                                             r15["pruefen"])
    falsch15 = ["Saturn steht bis in den %s im Quadrat zu deiner Sonne." % w["m200"],
                "Jupiter steht im Trigon zu deinem Mond über das Ende dieses Fensters hinaus.",
                "Saturn rückt im %s in den Krebs." % w["m110"],
                "Ab %s steht Saturn in deinem vierten Haus." % w["m110"],
                "Im %s steht Saturn im Quadrat zu deinem Merkur, eine Woche nach dem Kontakt zu deiner "
                "Sonne." % w["m75"],
                "Im %s, gut eine Woche nach dem ersten Durchgang, erreicht dein Mars im Sonnenbogen "
                "deinen Mond." % w["m100"],
                "Im %s steht Saturn im Quadrat zu deiner Sonne, mit dem Merkur im Gefolge." % w["m200"],
                "Saturn steht im %s und im %s im Quadrat zu deiner Sonne. Dazwischen steht Saturn im Quadrat "
                "zu deinem Merkur, genau im %s und im %s." % (w["m200"], w["m330"], w["m75"], w["m190"]),
                "Saturn und Jupiter stehen im Quadrat zu deiner Sonne und deinem Merkur.",
                "Saturn steht genau im %s, im %s und im %s im Quadrat zu deiner Sonne."
                % (w["m60"], w["m150"], w["m330"]),
                "Im %s geht der Mondknoten über deinen Merkur." % w["m250"],
                "Im %s laufen drei Kapitel nebeneinander." % w["m150"],
                "Im %s läuft auch Kapitel 2 mit." % w["m330"],
                "Im %s ist der Auftakt von Kapitel 1." % w["m110"],
                "Saturn bleibt fast die ganzen zwei Jahre im vierten Haus deines Bildes.",
                "Neptun steht im Sextil zu deinem Mars und zugleich im Quadrat zu deinem Mond.",
                "Saturn steht im %s im Quadrat zu deinem Merkur. In dieselben Wochen steht Neptun im Quadrat "
                "zu deinem Mond." % w["m75"]]
    ta15f = ersetze(ta13, "**Signatur:** Saturn im Quadrat zu deiner Sonne — mitklingend",
                    "**Signatur:** Saturn und Jupiter im Quadrat zu deiner Sonne — mitklingend")
    r15f = lauf(tc15, _a15(ta15f, falsch15), tev15)
    erwarte(r15f, (("P18", "pruefen", "„bis %s“ — Saturn Quadrat Sonne: Wirkorb bis %s" % (w["m200"], w["e360"])),
                   ("P18", "pruefen", "Jupiter Trigon Mond: am Fensterende (%s) nicht im Wirkorb" % w["e730"]),
                   ("P18", "pruefen", "Wechsel: „%s“ — Saturn in Krebs ab %s (Zeichenaufenthalt)"
                    % (w["m110"], w["e300"])),
                   ("P18", "pruefen", "„ab %s“ — Saturn in Haus 4 ab %s (Hausdurchgang)" % (w["m110"], w["e250"])),
                   ("P18", "pruefen", "„eine Woche nach“ (6–8 Tage nach) — Saturn–Merkur: %s (Bezug Saturn–Sonne: "
                                      "%s, +15 Tage)" % (w["e75"], w["e60"])),
                   ("P18", "pruefen", "Sonnenbogen: %s (Bezug Saturn Quadrat Sonne: %s, +40 Tage)"
                    % (w["e100"], w["e60"])),
                   ("P18", "pruefen", "Reihenfolge: Saturn–Merkur %s vor Saturn–Sonne %s" % (w["e190"], w["e200"])),
                   ("P18", "pruefen", "„Dazwischen“ — %s, %s außerhalb" % (w["e75"], w["e190"])),
                   ("P18", "pruefen", "Jupiter Quadrat Sonne: kein solcher Kontakt in der Rechnung · "
                                      "Jupiter Quadrat Merkur: kein solcher Kontakt"),
                   ("P18", "pruefen", "Genau: „%s“ — kein Exaktdatum in" % w["m150"]),
                   ("P18", "pruefen", "Mondknoten Konjunktion Merkur: kein Nulldurchgang in"),
                   ("P18", "pruefen", "„drei Kapitel“ (%s) — dicht in Q2: Kapitel 1, 2 (2)" % w["m150"]),
                   ("P18", "pruefen", "Kapitel 2 in %s — dicht nur in Q2" % w["m330"]),
                   ("P18", "pruefen", "Kapitel 1 läuft schon: Saturn Quadrat Sonne im Wirkorb ab %s" % w["e20"]),
                   ("P18", "pruefen", "Saturn in Haus 4: 481 von 731 Tagen des Fensters (66 %)"),
                   ("P18", "pruefen", "Neptun Quadrat Mond und Neptun an Mars: kein gemeinsamer Tag im Wirkorb"),
                   ("P18", "pruefen", "„In dieselben Wochen“ — Neptun Quadrat Mond: Wirkorb")), "Lauf 15 (P18)")
    _p15 = r15f["proben"]["P18"]["pruefen"]
    assert any("· Signatur:" in z and "Bündel: Jupiter Quadrat Sonne: kein solcher Kontakt" in z for z in _p15), \
        ("Lauf 15: Bündel in der Signatur nicht gemeldet", _p15)
    assert len(_p15) == len(falsch15) + 1, ("Lauf 15: Zahl der Hinweise", len(_p15), _p15)
    berichte.append("Lauf 15 (P18 Transit, 2026-10-13, Strang 1): stimmige Sätze still, je Satzart der "
                    "Widerspruch mit Datenwert gemeldet (Grenze „bis“ und Fensterende, Wechsel in Zeichen "
                    "und Haus, Abstand mit Bezugskontakt und Sonnenbogen, Gefolge, Dazwischen, Bündel in "
                    "Fließtext und Signatur, Genau und „geht über“, Kapitelzeit dreifach, Dauer, Zugleich "
                    "mit einem Läufer, „In dieselben Wochen“)")
    # 15b) Gegenpruefung 2026-10-13: Lesarten, die vorher falsch meldeten, bleiben still
    #      — „Bis …“ am Satzanfang, Teilstrecke, Wechsel vor dem Fenster und mit fremdem
    #      Subjekt, zwei Ziele mit je eigener Zeit, „danach“ im selben Satz, Dazwischen
    #      ohne Zeit, „folgt“ ohne „genau“, Kapitel als Verweis, Dauer über zwei Häuser,
    #      Buendel an der Spiegelachse —, und die neuen Widersprueche werden gemeldet.
    tev15b = json.loads(json.dumps(tev15))
    tev15b["hausdurchgang"].append({"transit": "Saturn", "haus": 3, "von": w["d0"], "bis": w["d250"],
                                    "angeschnitten": True})
    tev15b["zeichenaufenthalt"].append({"transit": "Jupiter", "zeichen": "Stier", "von": w["d0"],
                                        "bis": w["d730"], "angeschnitten": True})
    _um = _ev15("Uranus", "Quadrat", "MC", (250,), 230, 300)
    _ui = _ev15("Uranus", "Quadrat", "IC", (250,), 230, 300)
    _ui["spiegel"] = True
    tev15b["events"] += [_um, _ui]
    ok15b = ["Bis in den %s steht Saturn im Quadrat zu deiner Sonne." % w["m360"],
             "Die zweite Welle des Quadrats von Saturn zu deiner Sonne reicht bis in den %s." % w["m360"],
             "Jupiter trat im %s in den Stier." % w["mM2500"],
             "Während Saturn noch im Quadrat zu deiner Sonne steht, wechselt der progressive Mond im %s "
             "in den Krebs." % w["m110"],
             "Saturn wechselt im %s in dein viertes Haus und im %s in den Krebs." % (w["m250"], w["m300"]),
             "Im %s steht Saturn im Quadrat zu deiner Sonne und gut zwei Wochen danach im Quadrat zu deinem "
             "Merkur." % w["m60"],
             "Saturn steht im %s und im %s im Quadrat zu deiner Sonne. Dazwischen steht Saturn im Quadrat zu "
             "deinem Merkur." % (w["m60"], w["m330"]),
             "Im %s folgt Jupiter im Trigon zu deinem Mond." % w["m110"],
             "Im %s kehrt die Frage aus Kapitel 2 zurück." % w["m330"],
             "Die nächsten zwei Kapitel erzählen, was im %s dazukommt." % w["m150"],
             "Saturn steht die ganzen zwei Jahre im dritten und dann im vierten Haus.",
             "Uranus steht im Quadrat zu deinem MC und deinem IC."]
    r15b = lauf(tc15, _a15(ta13, ok15b), tev15b)["proben"]["P18"]
    assert r15b["status"] == "OK", ("Lauf 15b: P18 nicht still", r15b["pruefen"])
    falsch15b = ["Bis in den %s steht Saturn im Quadrat zu deiner Sonne." % w["m200"],
                 "Die zweite Welle des Quadrats von Saturn zu deiner Sonne reicht bis in den %s." % w["m200"],
                 "Jupiter tritt im %s in den Stier." % w["m100"],
                 "Im %s steht Saturn im Quadrat zu deinem Merkur, mit der Sonne im Gefolge." % w["m75"],
                 "Saturn steht im %s im Quadrat zu deiner Sonne und im %s im Quadrat zu deinem Merkur. "
                 "Dazwischen steht Neptun im Quadrat zu deinem Mond." % (w["m60"], w["m75"]),
                 "Saturn und Jupiter stehen deiner Sonne und deinem Merkur gegenüber."]
    r15bf = lauf(tc15, _a15(ta13, falsch15b), tev15b)
    erwarte(r15bf, (("P18", "pruefen", "„bis %s“ — Saturn Quadrat Sonne: Wirkorb bis %s" % (w["m200"], w["e360"])),
                    ("P18", "pruefen", "keine Wirkorb-Strecke endet darin"),
                    ("P18", "pruefen", "Jupiter steht schon ab Fensteranfang (%s) in Stier" % w["e0"]),
                    ("P18", "pruefen", "Reihenfolge: Saturn–Sonne %s vor Saturn–Merkur %s" % (w["e60"], w["e75"])),
                    ("P18", "pruefen", "„Dazwischen“ — kein Wirkorb zwischen %s–%s" % (w["e60"], w["e75"])),
                    ("P18", "pruefen", "Saturn Opposition Sonne: kein solcher Kontakt in der Rechnung (nur Quadrat)")),
            "Lauf 15b (P18)")
    berichte.append("Lauf 15b (P18, Gegenprüfung 2026-10-13): „Bis …“ am Satzanfang, Teilstrecke, Wechsel vor "
                    "dem Fenster, fremdes Subjekt, zwei Ziele mit eigener Zeit, „danach“ im selben Satz, "
                    "Dazwischen ohne Zeit, „folgt“ ohne „genau“, Kapitel als Verweis, Dauer über zwei Häuser "
                    "und Spiegelachse still; dieselben Formen mit Widerspruch gemeldet")

    # Lauf 16 (P5 Kapitelangaben, 2026-10-13, Strang 3 des Wartungslaufs): die
    # Registerzeilen des Geburtshoroskops beidseitig gegen Themenliste und Kapiteltext,
    # Achsen eingeschlossen, dazu der Satz „Mit dem MC haben Kapitel … zu tun“; im
    # Transit die Kapitelangabe eines `klingt=`-Kontakts und eine leere
    # Angabe. Saetze erfunden, Daten konstruiert.
    c16 = ersetze(_TEST_CHART, "  | klingt=Merkur Widder Haus 1\n", "  | klingt=Merkur Widder Haus 1, MC Steinbock\n")
    c16 = ersetze(c16, "  | aspekte=Mond △ Saturn\n", "  | aspekte=Mond △ Saturn, Saturn △ MC\n")
    a16 = ersetze(_TEST_ANALYSE, "sucht den ersten Schritt, weil dort die Kraft ist.",
                  "sucht den ersten Schritt, weil dort die Kraft ist. Dein MC im Steinbock zeigt, wohin das will.")
    a16 = ersetze(a16, "Was Saturn dazugibt, ist Form:", "Saturn stützt leise dein MC. "
                  "Was Saturn dazugibt, ist Form:")
    a16 = ersetze(a16, "Es hält, was einmal da ist.", "Es hält, was einmal da ist. Mit dem MC haben "
                  "Kapitel 2 und Kapitel 3 zu tun.")
    a16 = ersetze(a16, "3. Saturn, Jungfrau, sechstes Haus — die Ordnung im Alltag. Klingt mit in Kapitel 3.",
                  "3. Saturn, Jungfrau, sechstes Haus — die Ordnung im Alltag. Klingt mit in Kapitel 3.\n\n"
                  "4. MC, Steinbock — das Ziel nach außen. Klingt mit in Kapitel 2 und Kapitel 3.")
    r16 = lauf(c16, a16)["proben"]["P5"]
    assert not r16["pruefen"] and not r16["fehler"], ("Lauf 16: P5 nicht still", r16)
    a16f = ersetze(a16, "Klingt mit in Kapitel 2 und Kapitel 3.", "Klingt mit in Kapitel 2.")
    a16f = ersetze(a16f, "das schnelle Wort. Klingt mit in Kapitel 2.",
                   "das schnelle Wort. Klingt mit in Kapitel 2 und Kapitel 3.")
    a16f = ersetze(a16f, "die Ordnung im Alltag. Klingt mit in Kapitel 3.", "die Ordnung im Alltag.")
    a16f = ersetze(a16f, "Mit dem MC haben Kapitel 2 und Kapitel 3 zu tun.",
                   "Mit dem MC haben Kapitel 2 zu tun.")
    r16f = lauf(c16, a16f)
    erwarte(r16f, (("P5", "pruefen", "MC — die Registerzeile nennt Kapitel 3 nicht, obwohl MC dort mitklingt "
                                     "(THEMA 2 aspekte=: Saturn △ MC"),
                   ("P5", "pruefen", "Merkur — die Registerzeile nennt Kapitel 3, aber dort steht Merkur weder"),
                   ("P5", "pruefen", "Saturn — die Registerzeile nennt Kapitel 3 nicht, obwohl Saturn dort "
                                     "mitklingt (THEMA 2 klingt=: Saturn Jungfrau Haus 6"),
                   ("P5", "pruefen", "„Mit dem MC haben Kapitel 2 zu tun“ — es fehlt Kapitel 3")),
            "Lauf 16 (P5)")
    assert len(r16f["proben"]["P5"]["pruefen"]) == 4, ("Lauf 16: Zahl", r16f["proben"]["P5"]["pruefen"])
    # Transit: klingt=-Kontakt mit Satz im Kapitel, Registerzeile ohne Kapitel; leere Angabe
    tc16 = ersetze(tc13, "  | aspekte=T-Saturn □ R-Merkur\n", "  | aspekte=T-Saturn □ R-Merkur\n"
                   "  | klingt=T-Neptun ⚹ R-Mars\n")
    ta16 = ersetze(ta13, "und macht das Denken vorsichtiger.", "und macht das Denken vorsichtiger. "
                   "Später steht Neptun im Sextil zu deinem Mars und nimmt dem Druck die Kante.")
    ta16 = ersetze(ta16, "2. Neptun im Sextil zu deinem Mars, im {m400}: die Kraft wird weicher.".format(**w13),
                   "2. Neptun im Sextil zu deinem Mars, im {m400}: die Kraft wird weicher. "
                   "Klingt in Kapitel 1 mit.".format(**w13))
    r16t = lauf(tc16, ta16, dict(tev13, stations=_st13(0.2)))["proben"]["P5"]
    assert not r16t["pruefen"] and not r16t["fehler"], ("Lauf 16: Transit-P5 nicht still", r16t)
    ta16f = ersetze(ta16, "die Kraft wird weicher. Klingt in Kapitel 1 mit.", "die Kraft wird weicher.")
    ta16f = ersetze(ta16f, "eine Frage der Richtung im Denken.", "eine Frage der Richtung im Denken. "
                    "Klingt in Kapitel 2 mit.")
    r16tf = lauf(tc16, ta16f, dict(tev13, stations=_st13(0.2)))
    erwarte(r16tf, (("P5", "pruefen", "T-Neptun Sextil R-Mars — klingt in Kapitel 1 mit (`klingt=` von THEMA 1; "
                                      "das Kapitel nennt ihn: „Später steht Neptun im Sextil zu deinem Mars"),
                    ("P5", "pruefen", "T-Mondknoten Konjunktion R-Merkur — die Registerzeile nennt Kapitel 2, "
                                      "aber dort steht kein Satz mit Mondknoten und Merkur")), "Lauf 16 (P5 Transit)")
    assert len(r16tf["proben"]["P5"]["pruefen"]) == 2, ("Lauf 16: Transit-Zahl", r16tf["proben"]["P5"]["pruefen"])
    berichte.append("Lauf 16 (P5 Kapitelangaben, 2026-10-13, Strang 3): stimmige Registerzeilen und "
                    "Instrument-Satz still; fehlende Kapitelangabe (klingt= und aspekte=, auch an einer "
                    "Achse), leere Kapitelangabe und unvollständiger „Mit dem MC haben Kapitel … zu "
                    "tun“ gemeldet; im Transit der klingt=-Kontakt ohne Kapitel und eine leere Angabe")

    # Lauf 17 (P18 Naehe, Lage und Rang, 2026-10-13, Strang 2 des Wartungslaufs): das
    # konstruierte Datenblatt aus Lauf 12 (Untergrund ungedeutet) bekommt Venus, Chiron und
    # den Mondknoten, zwei Aspektzeilen, gleiche Hausspitzen (je 0° eines Zeichens), zwei
    # Stellien in §6 und die Mitte der leeren Haelfte in §8. Saetze erfunden, je Absatz einer.
    c17 = ersetze(_c12b, "| Saturn | 22°05′ | Jungfrau ♍ | 6 | direkt |",
                  "| Saturn | 22°05′ | Jungfrau ♍ | 6 | direkt |\n| Venus | 19°00′ | Widder ♈ | 1 | direkt |\n"
                  "| Chiron | 29°30′ | Stier ♉ | 2 | direkt |\n| Mondknoten | 12°00′ | Waage ♎ | 7 | rückläufig |")
    c17 = ersetze(c17, "## Aspekte (konstruiert)", "## Eigene Koch-Hausspitzen\n\n| Haus | Spitze |\n|---|---|\n"
                  + "".join("| %d | 0°00′ %s |\n" % (i + 1, z) for i, z in enumerate(
                      ("Widder", "Stier", "Zwillinge", "Krebs", "Löwe", "Jungfrau", "Waage", "Skorpion",
                       "Schütze", "Steinbock", "Wassermann", "Fische")))
                  + "\n## Aspekte (konstruiert)")
    c17 = ersetze(c17, "| Mars | □ Quadrat | AC | 0°40′ | rot | Quadrat DC |",
                  "| Mars | □ Quadrat | AC | 0°40′ | rot | Quadrat DC |\n| Sonne | ☍ Opposition | Mondknoten | 2°00′ | rot |  |")
    c17 = ersetze(c17, "| Mars | ☍ Opposition | MC | 0°40′ | rot | Konjunktion IC |",
                  "| Mars | ☍ Opposition | MC | 0°40′ | rot | Konjunktion IC |\n"
                  "| Merkur | ☌ Konjunktion | Venus | 7°50′ | konj |  |")
    c17 = ersetze(c17, "leere Spitze 25°00′ Widder, Haus 1; dort: nichts\n",
                  "leere Spitze 25°00′ Widder, Haus 1; dort: nichts\n- Stellium in Widder: Merkur, Sonne, Venus\n"
                  "- Stellium in Haus 1: Merkur, Sonne, Venus\n\n### 8 · Verteilung\n- Muster nach Jones: Schüssel — "
                  "Spanne 162°05′ von Sonne (Widder, Haus 1) bis Saturn (Jungfrau, Haus 6); Mitte der leeren "
                  "Hälfte 1°02′ Steinbock, Haus 10.\n")
    _neu17 = ("— Nähe:", "— Absolutformel:", "— Rang: „", "— Beieinander:", "— Ballung:", "— Leere Fläche:",
              "— Knotenachse:")

    def _p18_17(saetze):
        r_ = lauf(c17, _a12(saetze, [], [], [], []))["proben"]["P18"]
        return [z for z in r_["pruefen"] if any(w in z for w in _neu17)]
    still17 = ["Mars steht genau am IC, am tiefsten Punkt deines Bildes.",
               "Mars steht gradgenau im Quadrat zu deinem Aszendenten.",
               "Merkur steht fast genau an deiner Sonne.",
               "Mars und MC stehen einander genau gegenüber.",
               "Mars steht im Quadrat zum AC, so eng, wie man es selten sieht.",
               "Mars steht im Quadrat zum AC, eine Verbindung, die kaum enger sein könnte.",
               "Sonne und Merkur stehen dicht beieinander.",
               "Merkur steht mitten in der Ballung im Widder.",
               "Die Mitte der freien Hälfte liegt im Steinbock.",
               "Saturn steht in der freien Hälfte, im sechsten Haus.",
               "Dein Mars steht dem Nordknoten gegenüber.",
               "Sonne und Merkur verschmelzen so eng, wie man es zwischen zwei Planeten sonst nirgends findet.",
               "Die Verbindung von Sonne und Merkur ist die engste zwischen zwei Planeten in deinem ganzen Bild, "
               "sieht man vom Untergrund ab.",
               "Chiron steht genau dort, wo diese beiden Bereiche sich berühren.",
               "Zwischen zwei Planeten ist keine Verbindung so eng wie die von Sonne und Merkur.",
               "Genau dort, wo du anfängst, steht deine Sonne.",
               "Die Sonne steht genau auf deinem Weg."]
    _r17 = _p18_17(still17)
    assert not _r17, ("Lauf 17: stimmige Sätze nicht still", _r17)
    melde17 = [("Merkur steht genau an deiner Sonne.", "Nähe: „genau an deiner Sonne“ trägt höchstens 1° — "
                                                       "Sonne Konjunktion Merkur 1°10′"),
               ("Merkur steht am selben Punkt wie deine Sonne.", "„am selben Punkt wie deine Sonne“"),
               ("Mond steht exakt im Trigon zu Saturn.", "„exakt im Trigon“ trägt höchstens 1° — Mond Trigon "
                                                         "Saturn 2°05′"),
               ("Mit Merkur verschmilzt die Sonne zu einem Punkt.", "„verschmilzt die Sonne zu einem Punkt“"),
               ("Dein Mars steht genau dort, wo diese beiden Bereiche sich berühren.",
                "Mars 5°00′ Krebs, nächste Hausspitze 4 (0°00′ Krebs), Abstand 5°00′"),
               ("Mond und Saturn stehen im Trigon, so eng, wie es überhaupt vorkommen kann.",
                "Absolutformel: „wie es überhaupt vorkommen kann“ sagt mehr, als ein Orb tragen kann — "
                "Mond Trigon Saturn 2°05′, Rang 4 der Rangzeile engste-aspekte"),
               ("Sonne und Merkur verschmelzen, und enger geht es nicht.", "Absolutformel: „enger geht es nicht“"),
               ("Sonne und Merkur bilden eine Konjunktion, die kaum enger sein könnte.",
                "„kaum enger sein könnte“ — Sonne Konjunktion Merkur 1°10′, Rang 3 der Rangzeile engste-aspekte"),
               ("Sonne und Merkur verschmelzen — die engste Verbindung zwischen zwei Planeten in deinem ganzen Bild.",
                "Rang: „deinem ganzen Bild“ zählt jeden gerechneten Untergrund-Aspekt mit — Merkur Halbquadrat "
                "Saturn 0°20′; damit steht Sonne Konjunktion Merkur 1°10′ auf Rang 2"),
               ("Sonne und Merkur verschmelzen so eng, wie sie in deinem ganzen Bild zwischen zwei Planeten sonst "
                "nirgends stehen.", "mit dem Untergrund („deinem ganzen Bild“): Merkur Halbquadrat Saturn 0°20′"),
               ("Mond und Saturn stehen im Trigon, enger als jede andere Verbindung in deinem Bild.",
                "„enger als jede andere Verbindung“ verlangt Rang 1 ohne Gleichstand — Mond Trigon Saturn 2°05′"),
               ("Mars steht im Quadrat zum AC, enger als jede andere Verbindung in deinem Bild.",
                "Mars Quadrat AC 0°40′; Rangzeile engste-aspekte: 1. Mars Opposition MC 0°40′"),
               ("Sonne, Merkur und Venus stehen eng beieinander.",
                "Beieinander: „eng beieinander“ verlangt eine Konjunktion je Paar — keine Konjunktion: "
                "Sonne–Venus (Abstand 9°00′)"),
               ("Venus steht mitten in der Ballung im Widder.",
                "Ballung: „mitten in der Ballung“ — Venus ist Randglied: Stellium in Widder: Sonne 10°00′, "
                "Merkur 11°10′, Venus 19°00′"),
               ("Die freie Hälfte deines Bildes liegt im Steinbock.",
                "nur ihre Mitte: 1°02′ Steinbock, Haus 10 (§8)"),
               ("Der leere Bogen deines Bildes liegt im zehnten Haus.",
                "der leere Bogen umfasst 197°55′ (von Saturn 22°05′ Jungfrau bis Sonne 10°00′ Widder); in einem "
                "Zeichen oder Haus liegt nur seine Mitte: 1°03′ Steinbock, Haus 10"),
               ("Die Sonne steht der Knotenachse gegenüber.",
                "Knotenachse: einer Achse steht kein Faktor gegenüber, nur einem ihrer Enden — Sonne Opposition "
                "Mondknoten 2°00′ — gegenüber liegt der Nordknoten")]
    _r17 = _p18_17([s for s, _w in melde17])
    fehlt17 = [w for _s, w in melde17 if not any(w in z for z in _r17)]
    assert not fehlt17 and len(_r17) == len(melde17), ("Lauf 17: Meldungen", fehlt17, len(_r17), _r17)
    assert all(z.split(" — ", 1)[1:] for z in _r17), "Lauf 17: Hinweis ohne Datenwert"
    # Lauf 17b (Gegenprüfung 2026-10-13): Satzanfang groß, Subjekt dahinter oder als Pronomen,
    # mehrere Subjekte und Ziele je Paar, „genau an“ ohne Konjunktion, Einschübe, Wendungen
    # ohne Lageaussage, Zeichen- und Untergrund-Formen, P12 bei „keine andere … so eng wie“
    still17b = ["Schreib so genau wie möglich auf, was Sonne und Merkur in dir auslösen.",
                "Wenn Merkur wankt, achte genau auf deine Sonne.",
                "Der Mond steht genau auf der Spitze dieses Dreiecks.",
                "Dein Mond fühlt sich mitten in einer Gruppe von Menschen wohl.",
                "Bei dir liegen, wie Mond und Saturn zeigen, Nähe und Krise eng beieinander.",
                "Saturn verhält sich gegenüber der Knotenachse wie ein Wächter.",
                "Deine Sonne steht nicht genau am Mondknoten, aber nah bei ihm.",
                "Anders als deine Sonne steht Chiron genau dort, wo diese beiden Bereiche sich berühren.",
                "Innerhalb dieser Ballung ist die Verbindung von Sonne und Merkur enger als jede andere Verbindung.",
                "Mars, der deinem MC genau gegenübersteht, hält den Rahmen."]
    _r17 = _p18_17(still17b)
    assert not _r17, ("Lauf 17b: stimmige Sätze nicht still", _r17)
    melde17b = [("Genau an deinem IC steht Venus.", "keine Konjunktion Venus–IC (Abstand 71°00′)"),
                ("Eng beieinander stehen Sonne, Merkur und Venus.", "keine Konjunktion: Sonne–Venus (Abstand 9°00′)"),
                ("Mitten in dieser Ballung steht deine Venus.", "Venus ist Randglied: Stellium in Widder"),
                ("Der Knotenachse gegenüber steht deine Sonne.", "Sonne Opposition Mondknoten 2°00′ — gegenüber "
                                                                  "liegt der Nordknoten"),
                ("Keine andere Verbindung deines Bildes ist so eng wie die von Mond und Saturn.",
                 "verlangt Rang 1 ohne Gleichstand — Mond Trigon Saturn 2°05′"),
                ("Unter allen gerechneten Verbindungen ist die von Sonne und Merkur zwischen zwei Planeten die "
                 "engste.", "Merkur Halbquadrat Saturn 0°20′; damit steht Sonne Konjunktion Merkur 1°10′ auf "
                            "Rang 2"),
                ("Mars und Venus stehen genau am IC.", "„genau am IC“ trägt höchstens 1° — keine Konjunktion "
                                                       "Venus–IC"),
                ("Mond steht exakt im Trigon zu Saturn und Mars.", "„exakt im Trigon“ trägt höchstens 1° — Mond "
                                                                  "Trigon Saturn 2°05′"),
                ("Die Sonne steht dem Mondknoten genau gegenüber, so wie Mars dem MC.",
                 "„genau gegenüber“ trägt höchstens 1° — Sonne Opposition Mondknoten 2°00′"),
                ("Die Sonne, die dem Mondknoten genau gegenübersteht, sucht ihren Weg.",
                 "„genau gegenübersteht“ trägt höchstens 1° — Sonne Opposition Mondknoten 2°00′"),
                ("Im Steinbock liegt die freie Hälfte deines Bildes.", "nur ihre Mitte: 1°02′ Steinbock, Haus 10 (§8)"),
                ("Die freie Hälfte deines Bildes steht im Zeichen des Steinbocks.", "„freie Hälfte … im Zeichen des "
                                                                                    "Steinbocks“"),
                ("Sonne und Merkur verschmelzen. Enger kann eine Verbindung gar nicht sein.",
                 "„Enger kann eine Verbindung gar nicht sein“ sagt mehr, als ein Orb tragen kann — Sonne "
                 "Konjunktion Merkur 1°10′"),
                ("Mond steht exakt im Anderthalbquadrat zu Mars.", "Mond Anderthalbquadrat Mars 1°30′"),
                ("Und die Sonne? Sie steht genau dort, wo diese beiden Bereiche sich berühren.",
                 "Sonne 10°00′ Widder, nächste Hausspitze 1 (0°00′ Widder), Abstand 10°00′"),
                ("Merkur — genau an deiner Sonne — hält die Form.", "„genau an deiner Sonne“ trägt höchstens 1° — "
                                                                    "Sonne Konjunktion Merkur 1°10′"),
                ("Sonne und Merkur verschmelzen zu einem einzigen Punkt.", "„verschmelzen zu einem einzigen Punkt“ "
                                                                           "trägt höchstens 1° — Sonne Konjunktion "
                                                                           "Merkur 1°10′")]
    r17b = lauf(c17, _a12([s for s, _w in melde17b], [], [], [], []))
    _r17 = [z for z in r17b["proben"]["P18"]["pruefen"] if any(w in z for w in _neu17)]
    fehlt17 = [w for _s, w in melde17b if not any(w in z for z in _r17)]
    assert not fehlt17 and len(_r17) == len(melde17b), ("Lauf 17b: Meldungen", fehlt17, len(_r17), _r17)
    _p12 = [z for z in r17b["proben"]["P12"]["pruefen"] if "Keine andere Verbindung" in z or "einzigen Punkt" in z]
    assert not _p12, ("Lauf 17b: P12 meldet Formen, die P18 hält", _p12)
    berichte.append("Lauf 17 (P18 Nähe, Lage und Rang, 2026-10-13, Strang 2): stimmige Sätze still („fast "
                    "genau“, bis 1°, Rang 1 ohne Untergrund, Untergrund genannt, Mitte der Hälfte, Glied in der "
                    "Mitte, figürliches „genau dort“); je Form der Widerspruch mit Datenwert gemeldet (Nähe über "
                    "1°, Hausspitze, Absolutformel, „kaum enger“, Rang mit dem ganzen Untergrund, „enger als "
                    "jede andere“ bei Rang 4 und bei Gleichstand, eng beieinander, Randglied, leere Hälfte und "
                    "leerer Bogen, Knotenachse); 17b nach der Gegenprüfung: Satzanfang groß, Subjekt dahinter, "
                    "als Pronomen und im Einschub, jedes Paar mehrerer Subjekte und Ziele, „genau an“ ohne "
                    "Konjunktion, Untergrund-Aspekt, „im Zeichen des …“ und vorangestellter Ort gemeldet; "
                    "Anleitung, Hinsehen, Dreiecksspitze, Menschengruppe, Einschub, Verhältnis-„gegenüber“, "
                    "Verneinung, Vergleichsglied, Teilmenge still; P12 still bei Formen, die P18 hält")

    if not still:
        print("\n".join(berichte))
        print("[Selbsttest bestanden: Einzelproben der Muster; Lauf 1 ohne Befund (nur der "
              "Getriebe-Beleg teilweise übersprungen), Lauf 2 findet je Probe den eingebauten Fehler, "
              "Lauf 3 liest das Zugang-Kapitel; Transit: Lauf 4 sauber mit events.json, Lauf 5 und 5b "
              "finden die eingebauten Fehler, Lauf 6 ohne events.json nur teilweise übersprungen; "
              "Lauf 7 dieselbe Analyse mit dem Kicker `Getriebe` und der neuen Zählung, 7b ohne ihn; "
              "Lauf 8 Deutungsort über dem Deckel; Lauf 9 offene Führung; Lauf 10 „um die N“; "
              "Lauf 11 Altersreihe; Lauf 12 und 13 P18 Satzarten mit erfundenen Sätzen; "
              "Lauf 14 und 14b P19 Wiederholung; Lauf 15 P18 Zeitangaben im Transit; "
              "Lauf 16 P5 Kapitelangaben im Register; Lauf 17 P18 Nähe, Lage und Rang; "
              "P16 und P17 als Einzelproben]")
    return True

def _main(argv):
    if "--selbsttest" in argv:
        _selbsttest()
        return 0
    args = [x for x in argv if not x.startswith("--")]
    typ = None
    if "--typ" in argv:
        i = argv.index("--typ")
        typ = argv[i + 1] if i + 1 < len(argv) else None
        args = [x for x in args if x != typ]
    events_pfad = None
    if "--events" in argv:          # 2026-09-19 (W24)
        i = argv.index("--events")
        events_pfad = argv[i + 1] if i + 1 < len(argv) else None
        if not events_pfad or events_pfad.startswith("--"):
            print("--events braucht einen Pfad: --events <klient>_Transit_events.json",
                  file=sys.stderr)
            return 2
        args = [x for x in args if x != events_pfad]
    if len(args) != 2:
        print("Aufruf: python3 inhaltsprobe.py <analyse.md> <chart_data.md> [--typ geburt|transit]"
              " [--events <events.json>]\n"
              "        python3 inhaltsprobe.py --selbsttest", file=sys.stderr)
        return 2
    try:
        r = pruefe(args[0], args[1], typ, events_pfad)
    except InhaltsprobeFehler as e:
        print("INHALTSPROBE: abgebrochen — %s" % e, file=sys.stderr)
        return 2
    print(bericht_aus(r))
    return 1 if r["fehler"] else 0


# ---------------------------------------------------------------------------
# hilfe() — Schnittstellen-Auskunft ohne Quelltext-Lektuere.
# Neu 2026-09-20 (Aufraeumlauf D, Block D3; K5/W61: Schnittstellen wurden je Lauf
# aus dem Quelltext nachgelesen, 50-110 KB je Lauf). Derselbe Block steht
# wortgleich in jedem Builder. Er liest Signaturen und Docstrings zur LAUFZEIT —
# er kann also nicht veralten. Was hilfe() nicht sagt, fehlt im Docstring der
# Funktion und wird DORT ergaenzt, nie hier.
# ---------------------------------------------------------------------------

# 2026-09-23 (Pruefberichte Transit 1+2 vom 22.09.c: 17 Aufrufe/28.843 B Quelltext;
# Geburtshoroskop 1+2 vom 23.09.: 15 Aufrufe/77.349 B): Die Modultexte sagen, WAS die
# Proben pruefen, nicht, WORAN sie es erkennen. Das steht hier, an einer Stelle:
# `inhaltsprobe.hilfe('LESEFORMATE')`. Wer einen Leser aendert, zieht diesen Text nach.
LESEFORMATE = """Woran die Proben den Text erkennen (Stand 2026-10-13).

THEMENLISTE (chart_data) — P3, P6, P7, P15; build.aspekt_heimat() liest gleich.
  Beginn an der ersten Zeile `THEMA <n> |`; Ende am ersten Vorkommen von
  `RECHENSCHAFT`, `REGISTER:` oder `GESTRICHEN:` — das blanke Wort genügt: Steht es
  in einer Auswahlbegründung hinter den THEMA-Zeilen, endet die Liste dort.
  Felder `name=wert`, getrennt durch ` | `. Gelesen: titel, fuehrt (der Faktor am
  Anfang des Werts; im Transit der Kontakt `T-X <Aspekt> R-Y`), form (Vorgabe voll),
  leitachse (beginnt mit „ja"), teil.

BELEG (analyse) — P1, P2, P13, P14.
  Segmente getrennt durch ` · `. Segment 1 = Stand: `Faktor Glyphe Gradminute Zeichen
  Glyphe, n. Haus` (Grenzlage: führendes Haus vorn). P2 hält Zeichen und Haus gegen @@SELEKTOR,
  die Gradminute gegen die Ständetabelle: 1′ Abweichung PRÜFEN, mehr FEHLER.
  Ab Segment 2 genau EINE Aspektbeziehung mit Wort UND Glyphe.
  Transit: `T-X Glyphe Aspekt Glyphe R-Y — exakt TT.MM.JJJJ, …` bzw. `— nicht exakt,
  Annäherung bis x′ am TT.MM.JJJJ`; im Lagebild `— am Stichtag Orb 0,57°`.
  Zusatz-Segmente: `Sonnenbogen-X … R-Y — exakt TT.MM.JJJJ`, `Finsternis auf R-Y —
  TT.MM.JJJJ`, `progressiver Mond → Haus n — TT.MM.JJJJ`, `Jahresprofektion →
  Zeichen, Jahresherr X — ab dem N. Geburtstag`. Datum IMMER TT.MM.JJJJ,
  auch in einer englischen Fassung.

REGISTER im Transit (`Mitlaufendes`) — P5.
  Eine Zeile deckt einen Kontakt, wenn sie Transiter UND Ziel nennt; trägt sie die
  Präfixe T-/R-, muss der Transiter hinter T- und das Ziel hinter R- stehen; trägt
  sie ein Aspektwort, muss es stimmen. Selbst-Transit: der Name zweimal oder
  „Rückkehr"/„Wiederkehr"/„eigen…". Klingt der Kontakt in einem Kapitel mit, nennt
  die Zeile `Kapitel n`. Mitklingende Kontakte ohne Zeile: EINE Sammelzeile (FEHLER).
  Soll-Menge mit events.json aus build.kontakt_heimat(); ohne sie aus dem Block
  `TRANSIT-RECHENSCHAFT:` (Ende an Überschrift, `@@`, `THEMA n |` oder
  `GESTRICHEN:`/`RECHENSCHAFT:`/`REGISTER:`).
  Seit 2026-10-13: Ein `klingt=`-Kontakt einer THEMA-Zeile, den sein Kapitel nennt (ein
  Satz mit Transiter und Ziel), trägt in seiner Zeile `Kapitel n`; nennt eine Zeile ein
  Kapitel, muss dort ein Satz mit beiden stehen.

RECHENSCHAFT im Geburtshoroskop — P5, seit 2026-10-13.
  Die Zeile beginnt mit dem Faktor (ein Artikel davor zählt nicht). Kapitelangaben sind
  alle `Kapitel n` / `Kapiteln n, m und k` der Zeile; ein Mitklingen behauptet nur der
  Satzteil ab „klingt …“ bis Semikolon oder Punkt. Soll ist jedes Kapitel, dessen
  THEMA-Zeile den Faktor unter `klingt=` (erster Faktor des Eintrags) oder `aspekte=`
  (einer der beiden) führt UND dessen Signatur oder Text ihn nennt — auch eine Achse;
  „Himmelstiefe“ und „tiefster/höchster Punkt deines Bildes“ gelten für IC und MC,
  „Knotenachse“ für den Südknoten. Dasselbe gilt für den Satz „Mit dem <Faktor> haben
  Kapitel … zu tun“ außerhalb der Rechenschaft. Wer ein Thema führt, ist ausgenommen.

DEUTUNGSORT (Ressourcen-Block) — P15.
  Zeile `… — Deutungsort: Thema n` | `Ressource n` | `Was trägt`; im Transit auch
  „Was dich durch diese Zeit trägt" (Abschnitt `###`) und `Mitlaufendes (Deckel)`
  für Kontakte über dem Deckel von sechs — dort genügt eine Zeile im Kapitel
  `Mitlaufendes`, die beide Faktoren nennt. Ein anderer Ort ist PRÜFEN. Eine Zeile
  `Nachzug:` und ein Klammervermerk „(Nachzug: …)“ im Ortsfeld sind kein Ort.
  Gezählt werden die Sätze ab dem Satz, der BEIDE Faktoren nennt (oder zwei Sätzen,
  die sie zusammen nennen), bis zu einem Satz nur über andere Faktoren.

KONSTELLATION IM TEXT — P13.
  Ein Aspektwort (auch Glyphe) oder ein Bild der Übersetzungstabelle zwischen zwei
  Faktoren im selben Satz, je höchstens 90 Zeichen entfernt. Geschnitten wird am
  Hauptsatz („, und", „, aber", „;"), am Nachbarmarker und am Relativsatz
  („…, der …"). Eine Aufzählung („ein Trigon zu A und ein Quadrat zu B") teilt das
  Subjekt. Die beiden Enden EINER Achse (AC/DC, MC/IC) bilden kein Paar. Verneintes
  zählt nicht. Eine gedeckte Paarung genügt. Ein Pronomen am Satzanfang („Er …",
  „Sie …") nimmt den letzten Faktor des Vorsatzes, dazu den ersten und letzten mit
  passendem Genus (MC und IC passen immer); steht „er"/„sie" im Glied vor
  Faktoren, die nur als Objekt dastehen („über deinen Aszendenten"), kommt sein
  Bezug als Subjekt dazu — beides nur, wenn hinter dem Aspektwort ein Faktor steht.
  Komma + Artikel + Faktor im Nominativ vor dem nächsten Aspektwort („…, der
  Mondknoten im Trigon …") beginnt ein neues Glied. Findet das erste Glied einer
  Aufzählung kein Subjekt, nimmt das zweite keinen Partner aus ihm. Die Faktoren eines
  Nebensatzes (Komma + „während", „weil", „als", „dass" …, bis zum nächsten Komma)
  zählen nicht hinter dem Aspektwort; stand dort einer, paart die Probe nicht nach vorn.
  Im Transit ist „über" vor „dein…"/„R-" und einem Faktor das Bild der Konjunktion
  („Saturn geht über deine Sonne"); ein zweites „über" hinter Komma oder „und" und
  höchstens einer Zeitangabe teilt das Subjekt („…, im Oktober über deinen Mars"),
  daneben trägt das Subjekt des vorigen Markers weiter (seit 2026-09-29). Kein Bild ist
  die Herrschaftsformel „der Planet, der über deinem Mond steht“ (seit 2026-10-01b).
  Ein Faktor, der mit „und“/„sowie“/„oder“ an ein Objekt angereiht ist („an Venus und
  Pluto“), ist selbst Objekt, nicht Subjekt des nächsten Markers (seit 2026-10-01b).
  Seit 2026-09-29 (K1) außerdem: Stehen vor einem Doppelpunkt nur Objekte, ist keins
  davon Partner eines Markers dahinter, wenn dort kein Faktor steht oder ein eigenes
  Paar mit Subjekt („…: Im Quadrat zu Saturn steht Mars“); sonst schon („Bei deinem
  Merkur ist das anders: Er steht im Trigon zu Uranus“). Steht der
  Marker selbst in einem Nebensatz, zählt nichts vor der Konjunktion, außer der Nebensatz
  beginnt mit „er“/„sie“/„es“ oder trägt ein Objektpronomen („…, weil Pluto im Quadrat zu
  ihm steht“).
  „zwischen A und B“ bindet genau A und B, auch mehrfach hintereinander; ein Subjekt
  davor steht zu beiden Enden, wenn vor dem Marker kein bestimmter Artikel steht.
  „je ein …“ paart jedes Glied hinter „zu/zum/zur/mit“ einzeln mit dem Subjekt davor
  oder dahinter (sonst dem des vorigen Markers), nie untereinander; „zueinander“ schließt
  das Paar vor dem Marker; „auf der einen Seite …, … auf der anderen“ ist eine
  Ellipse. Stehen vor einem Marker nur die Objekte des vorigen und dahinter
  „ihm“/„ihr“/„ihnen“, ist sein Partner das Subjekt des vorigen Markers; „dir“/„dich“
  bildet kein Paar.

GEDEUTETE KAPITEL — P16.
  Kicker `Kapitel n` (englisch `Chapter n`), `Zugang …`, `Getriebe`, `Instrument`
  samt ihren englischen Namen; nicht das Lagebild „Der Stand heute". Gezählt werden
  die Wörter der Absätze und Zwischentitel, nicht Signatur und Beleg. Ausnahmen aus
  `form=kurz`/`form=ressource` der THEMA-Zeile und `duenn=ja` der ZUGANG-Zeile.

SUBJEKT — P17.
  Satzsubjekt heißt: Name (Planet, Achse, Zeichen, „die Seele", ein Haus mit
  Ordnungszahl) am Satz- oder Gliedanfang, hinter Artikel oder Relativpronomen ohne
  Präposition davor, oder hinter einem Verb („wird Saturn zum Aufseher"). Die Zone
  kommt aus dem letzten `###`-Zwischentitel: Bewegung 1 und 3–6 streng, 2 und 7 frei,
  ohne Bewegungswortlaut nur mit einem Verb außerhalb von `_P17_ANKERVERBEN`.
  Adverbien davor zählen nicht („steht auch Saturn"); vor einem Artikel entscheidet
  das Verb davor („steht deine Sonne"); ein Subjekt-Pronomen im selben Glied davor
  macht den Namen zum Objekt („Du hast deine Sonne …"); ein Relativsatz mit
  handelndem Verb („Saturn, der die Verantwortung trägt") zählt in jeder Zone.
  Hinter einer unterordnenden Konjunktion („wenn", „weil", „dass" …) entscheidet
  das Verb am Gliedende („wenn auch Saturn harmonisch zu deinem Mond steht" —
  verortet; seit 2026-09-29).

STRUKTURBILD §3 (chart_data) — P12.
  Die Zeilen „- Enddispositoren (im eigenen Zeichen, …): …" und „- Im eigenen Zeichen
  ohne Zulauf (…): …", Namen durch Komma getrennt; Klammern („(Ketten von …)") zählen
  nicht. Wer dort steht, folgt keinem anderen. Die Einzahl („der Planet, der keinem
  anderen folgt", „als einziger") ist gedeckt, wenn der Satz alle nennt; die
  Eigenschaft („dein Mond … folgt keinem anderen", „richtet sich nach keinem
  anderen"), wenn der genannte dort steht. Fehlen beide Zeilen, meldet P12 „§3
  nicht gefunden".

EINZIGKEIT ÜBER ELEMENT ODER MODUS (gegen RANG elemente-/modi-…) — P12, seit 2026-10-12.
  Deutsch „die einzige im Feuer", „der einzige Träger des Feuers", „die einzige
  (Kraft) in einem Zeichen der Anpassung", „die einzige Kraft, die im Feuer steht";
  englisch „the only one in fire", „the only carrier of fire", „the only one in a sign
  of adaptation", auch mit „single" und „sole". Es gilt das Element oder der Modus
  hinter dem Einzigkeitswort, direkt nach einer Präposition (im, in, des, der, of …,
  höchstens mit Artikel); dazwischen nur Wörter wie Kraft, Hauptkräfte, Planet,
  Träger, deiner zehn, die/der (Relativsatz) bzw. one, force, planet, carrier, of your
  ten main forces, that stands. Das Glied endet an Semikolon, Doppelpunkt,
  Gedankenstrich und an einem Komma, hinter dem kein Relativsatz beginnt. Deutsch gilt
  sonst wie bisher das Element oder der Modus im Glied; englisch liest NUR diese
  Aussage ein Element oder einen Modus („half", „all four" … nicht). Die Zeichen-Form
  („Zeichen der Anpassung / des Anfangs / des Haltens") gilt nur hier, nicht in P18.
  Gehalten gegen die Zählung, die der Satz nennt — „Planet", „gezählt", „zehn
  Hauptkräfte", „planets", „counted", „ten main forces": gezählt; „gewichtet",
  „Faktor", „weighted", „factors": gewichtet; die Planetenmenge geht dabei vor
  „gewichtet" (unter den zehn ist der Träger in beiden Zählungen derselbe); nennt der
  Satz keine Menge, gegen beide. Still nur, wenn dort die Zählung 1 steht und der
  genannte Planet der Träger ist: Nennt der Satz mehrere Faktoren, müssen sie genau der
  Träger sein (eine Achse daneben zählt nicht mit); nennt er keinen, nimmt ein Pronomen
  vor dem Einzigkeitswort („er", „sie", „dieser", „jene", „it", „this", „That …") ALLE
  Faktoren des Satzes davor als Kandidaten — deutsch nach Genus —, und sie müssen alle
  der Träger sein; ohne Faktor und ohne Pronomen genügt die Zählung 1.

P18 SATZARTEN (analyse gegen chart_data und events.json) — nur PRÜFEN (2026-10-04).
  Gemeldet wird nur ein WIDERSPRUCH zu den Daten, nie eine Aussage, die sich nicht
  prüfen lässt; jeder Hinweis nennt den Datenwert. Gelesen: die Ständetabelle mit
  Hausspalte (Grenzlage „2/3" zählt beide Häuser, der Südknoten wird getrennt genannt
  und löst allein nichts aus), Strukturbild §3 (erste Liste „Haus  n (Zeichen) →
  Herrscher …"), §6 („leere Spitze …, Haus n; dort: …"), die Aspekttabellen
  (Untergrund nur mit gedeutet = ja), die Rangzeilen §10 und die THEMA-Felder
  fuehrt/klingt/aspekte/verweis; im Transit aus der events.json die Wirkorb-Perioden
  samt Vorlauf, die Exaktdaten, jetzt.im_orb, stations (nahe_detail),
  zeichenaufenthalt und fruehere_durchgaenge.
  Bezug: „dort" zeigt auf das zuletzt genannte Glied des letzten Ortes im Satz,
  sonst im Satz davor („im Widder, im ersten Haus … dort" = das erste Haus);
  nennt eine Aussage ihren Bereich selbst mit Zeichen UND Haus („Der Löwe im fünften
  Haus ist leer"), zählt nur, wer in beiden steht. Faktoren, die der Satz selbst
  nennt („dort steht sonst nichts", „leer bis auf …"), zählen nicht; ein Satz über
  einen PUNKT („Der Punkt selbst ist unbesetzt", „… — sie selbst bleibt frei, dort …") und
  eine Wendung („darin liegt keine Schwäche", „Kein Planet steht so nah … wie …")
  bleiben still. Wem eine Herrscher-Aussage gilt: der Apposition davor („Saturn, der
  Verwalter …"), sonst dem Pronomen am Klauselanfang (aus dem Satz davor nur, wenn
  dort genau EIN Faktor passt), sonst dem ersten Faktor, der nicht hinter einer
  Präposition steht; ein „klassischer Herrscher" wird nicht gegen §3 gehalten. Ein
  Kapitelverweis meldet nur ein PAAR, das im genannten Kapitel weder unter aspekte=
  noch unter verweis= steht, wohl aber in einem anderen; ein einzelner Faktor, ein
  Vergleich („steht wie dein Mars …") und eine Gegenüberstellung („Anders als
  Kapitel n …", „dieses Kapitel", „hier") bleiben still.
  Transit: Ziel ist, was „dein …"/„R-" trägt oder hinter einer Präposition steht;
  sonst läuft ein laufender Planet. „ab/seit <Zeit>" gilt dem Läufer im selben
  Kommaabschnitt davor, sonst dem ersten danach; geprüft wird nur die Aspektart, die
  der Satz nennt (Name oder Bild der Klartext-Tabelle), und nur der Kontakt, dessen
  Wirkorb-Zeit die Angabe berührt. Gemeldet wird „läuft schon", wenn der Kontakt am
  Stichtag im Wirkorb steht oder schon vor der Angabe durchgehend im Wirkorb ist, und
  „im Wirkorb schon … wieder ab …", wenn eine frühere Strecke seit der Rückschau
  höchstens drei Monate vor dem Stichtag endet und der Absatz sie nicht selbst
  erzählt. „beginnt" für eine Teilstrecke („die rückläufige Strecke", „die dichte
  Phase") ist kein Beginn; „genau … Stillstand" zählt nur im selben Kommaabschnitt
  und höchstens sechs Wörter auseinander; Sätze über das Geburtsbild („In deinem
  Geburtsbild stehen …") laufen nicht durch „zugleich".
  Wiederholung: Das Alter muss unter den früheren Durchgängen DIESES Kontakts stehen
  (dieselbe Hälfte des Umlaufs). Bei jedem Aspekt außer Konjunktion und Opposition
  nennt der Satz die Stellung („so wie jetzt", „in derselben Stellung", „vom <Zeichen>
  aus") — dazwischen lag immer ein Durchgang aus der anderen Hälfte; „Dieselbe Frage
  stand zuletzt an …" ohne Aspektwort braucht keine (seit 2026-10-07). Verneint ein
  Satz frühere Durchgänge („gab es seit deiner Geburt nicht", „zum ersten Mal in
  deinem Leben"), gilt dasselbe: Stellung nennen, denn die Liste führt nur dieselbe
  Hälfte — und lief dort schon einer, ist die Verneinung falsch (seit 2026-10-07b).
  Ein Satzteil über eine Rückkehr („Rückkehr", „Wiederkehr", „kehrt … zurück") ohne
  eigenes Paar aus Transiter und Ziel bleibt still — Selbst-Transite wie die
  Knotenrückkehr führt die Liste nicht (seit 2026-10-09).
  Seit 2026-10-13 (Transit und „Die Zeit“ einer Vertiefung): „bis <Zeit>“ und „von … bis
  …“ gelten je Paar aus Läufer und Ziel des Teilsatzes, eine Sammelform („in mehreren
  Wellen“, „nacheinander“) für alle zusammen. Monatsdrittel 1.–10. / 11.–20. / 21.–Ende,
  Jahresdrittel Januar–April / Mai–August / September–Dezember, „eine Woche“ 6–8 Tage,
  „gut eine Woche“ 8–10; an Exaktdaten und an Haus- und Zeichenwechseln keine Toleranz.
  Wechsel („rückt … in den Widder“, „ab … im fünften Haus“) gegen Zeichenaufenthalt und
  Hausdurchgang; Abstände („einen Tag nach“, „eine Woche später“, „im Gefolge“) gegen die
  Exaktdaten des Bezugskontakts; ein Bündel aus Läufer- und Zielliste verlangt JEDES
  Paar, auch in der Signatur; „genau <Zeiten>“ gegen die Exaktdaten; „n Kapitel laufen
  …“ gegen `dicht=` der @@ZEITLEISTE; „(fast) die ganzen n Jahre“ gegen die Summe der
  Hausdurchgänge.
  Seit 2026-10-13 (Geburtshoroskop und Vertiefung außerhalb der Zeit-Kapitel, nicht im
  Beziehungshoroskop; Groß- und Kleinschreibung zählen nicht): Wem eine Lagewendung gilt —
  den Faktoren direkt davor im Teilsatz, mit „und“/Komma verbunden (ein Einschub „, wie …,“
  oder „, der …,“ zählt nicht); sonst dem ersten Faktor dahinter im Teilsatz; sonst bei
  „er/sie/es“ am Teilsatzanfang dem letzten Faktor des Satzes davor. Dann muss JEDES dieser
  Paare stimmen; ist niemand so lesbar, genügt ein Paar des Satzes (sonst des Satzes davor).
  „genau am/an/auf X“ und „am selben Punkt wie X“ nur mit „steht/sitzt/liegt“ im Satz oder
  als Einschub hinter dem Faktor („Neptun — genau an deinem Saturn —“): Konjunktion bis 1°,
  ohne Konjunktion mit dem Abstand der Längen. „exakt/gradgenau/auf den Grad im <Aspekt> zu
  X (und Y)“ (auch Untergrund-Aspekte), „genau gegenüber(steht)“, „zu einem (einzigen)
  Punkt“: bis 1°. „fast/nahezu/nicht genau“ bleibt frei. „genau dort, wo diese beiden
  Bereiche/Häuser (von … und …) sich berühren“ und „genau auf der Hausspitze“ (oder Grenze,
  Schwelle, Spitze mit „Haus“ dahinter): bis 1° zur nächsten Hausspitze (Tabelle „## …
  Hausspitzen“, sonst `cusps = […]`).
  Absolutformeln („wie es überhaupt vorkommen kann“, „enger geht es nicht“, „so eng wie
  möglich“ hinter einer Aspektart) immer mit Orb und Rang, wie ihn §10 druckt (mit „zwischen
  zwei Planeten“ die Planetenzeile); „kaum enger“ nur, wenn kein Paar des Satzes bis 1° auf
  Rang 1 steht. Rang: Mit „deines ganzen Bildes“, „alle Faktoren gezählt“, „unter allen
  gerechneten“ zählt jeder Untergrund-Aspekt mit, auch ungedeutet; „Untergrund“ im Satz nimmt
  ihn aus; ohne Zusatz gilt die Rangzeile (P12). „enger als jede andere“, „sonst nirgends“,
  „keine (andere Verbindung …) so eng wie“: Rang 1 ohne Gleichstand, mit den Einschränkungen
  dahinter (Aspektart, harmonisch, Spannung, Achse, voll); ein Rang innerhalb einer Gruppe
  („innerhalb dieser Ballung“) bleibt still wie bei P12.
  „eng/dicht beieinander“: Konjunktion je Paar der Faktoren davor (sonst dahinter).
  „mitten in der Ballung / im Stellium“ („Gruppe“ und „in ihr“ nur mit „Ballung“ oder
  „Stellium“ im Satz oder davor): kein Randglied nach der Länge — im Stellium aus §6, das der
  Satz mit Zeichen oder Haus nennt, sonst in jedem, das den Faktor enthält.
  Die leere Hälfte, der leere Bogen, der „im <Zeichen|Haus|Feld des …|Zeichen des …> liegt“
  (auch „Im Widder liegt die leere Hälfte“), ohne „Mitte“ im Satz: gemeldet mit der Mitte —
  §8 „Mitte der leeren Hälfte …“, sonst aus der Schüssel in §8 (ihre Mitte + 180°, auch beim
  Eimer), beim Bogen die größte Lücke der zehn Planeten. „der Knotenachse gegenüber“ mit
  „steht/liegt“: mit der Opposition oder Konjunktion zum Mondknoten.
"""


# 2026-09-26 (Pruefberichte vom 26.09.: die englischen 1+2-Laeufe holten die
# englischen Wortlaute mit 5 bis 15 Aufrufen aus dem Quelltext, bis 76 KB):
# `inhaltsprobe.hilfe('ENGLISCH')` druckt sie in EINEM Aufruf. Der Text wird beim
# Import aus den Konstanten gebaut, nach denen die Proben lesen — er kann nicht
# veralten. Die Kicker einer NEUEN englischen Fassung stehen in KICKER_EN.
KICKER_EN = (("Auftakt (Geburtshoroskop)", "Prelude"),
             ("Zur Lesart (Transit)", "On Reading This"),
             ("Getriebe", "Inner Workings"), ("Instrument", "Instrument"),
             ("Kapitel <n>", "Chapter <n>"), ("Zugang <Bereich>", "Access <area>"),
             ("Der Stand heute", "As Things Stand"),
             ("Mitlaufendes", "Also Running"), ("Rechenschaft", "Account"),
             ("Hauptthemen", "Core Themes"),
             ("Konfliktfelder", "Fields of Conflict"),
             ("Lebensaufgaben", "Life Tasks"), ("Schlusswort", "Closing Word"))


def _alternativen(muster):
    """Die Alternativen der OBERSTEN Ebene eines Regex-Musters (Klammern
    zaehlen mit) — fuer ENGLISCH."""
    teile, tiefe, cur, i = [], 0, "", 0
    while i < len(muster):
        c = muster[i]
        if c == "\\" and i + 1 < len(muster):
            cur += muster[i:i + 2]
            i += 2
            continue
        if c == "(":
            tiefe += 1
        elif c == ")":
            tiefe -= 1
        if c == "|" and tiefe == 0:
            teile.append(cur)
            cur = ""
        else:
            cur += c
        i += 1
    teile.append(cur)
    return teile


def _englisch_text():
    L = ["Englische Fassung: die Wortlaute, nach denen die Proben lesen "
         "(Stand 2026-10-12; gebaut aus den Konstanten dieser Datei).", "",
         "KICKER einer neuen englischen Fassung (`## <Kicker> · <Titel>`):"]
    for de, en in KICKER_EN:
        L.append("  %-26s -> %s" % (de, en))
    L.append("  Weitere, die die Proben auch lesen: " + "; ".join(
        "%s: %s" % (k, ", ".join(v)) for k, v in sorted(_KICKER_ALIAS.items())))
    L.append("")
    L.append("BEWEGUNGEN (`### <Wortlaut>`, in dieser Reihenfolge):")
    for typ, folge in WORTLAUTE.items():
        L.append("  %s:" % typ)
        for w in folge:
            if isinstance(w, tuple):
                L.append("    %s  ->  %s" % (w[0], w[1]))
    L.append("")
    L.append("PFLICHTTEIL „Was trägt\": der Kopf im Transit, die Inline-Form im "
             "Geburtshoroskop — erkannt werden:")
    L.append("  Kopf:   " + _WAS_TRAEGT_KOPF_RE.pattern)
    L.append("  Inline: " + _WAS_TRAEGT_INLINE_RE.pattern
             + "   (Form: „What carries you: …\")")
    L.append("")
    L.append("NICHTWISSEN (Satz, den P9 verlangt) — englische Muster:")
    L.append("  " + " | ".join(t for t in _alternativen(NICHTWISSEN_RE.pattern)
                               if not re.search(r"[äöüß]|wei|steht|keinem", t)))
    L.append("VERWERFUNGS-ERLAUBNIS — englische Muster:")
    L.append("  " + " | ".join(t for t in _alternativen(VERWERF_RE.pattern)
                               if not re.search(r"[äöüÄÖÜß]|verw|darf|kann|Kapitel",
                                                t)))
    L.append("")
    L.append("FAKTORNAMEN, englisch erkannt: " + ", ".join(
        s for s, _k in _FAKTOR_SCHREIBWEISEN
        if re.fullmatch(r"[A-Za-z ]+", s) and s not in (
            "AC", "MC", "DC", "IC", "Venus", "Mars", "Jupiter", "Saturn",
            "Uranus", "Pluto", "Chiron", "Lilith", "Pholus")
        and not re.search(r"knoten|Knoten|punkt|Coeli|Himmel|zendent|Fortunae|"
                          r"Sonne|Mond|Merkur|Neptun$", s)))
    L.append("ASPEKT-ANKER im Fliesstext: square, trine, opposition, conjunction, "
             "sextile, quincunx, semisextile oder semi-sextile, semi-square, "
             "sesquiquadrate.")
    # 2026-10-12 (W1)
    L.append("ELEMENT UND MODUS (nur die Einzigkeit in P12: „the only one in fire“, „the "
             "only carrier of fire“, „the only one in a sign of adaptation“, auch „single“, "
             "„sole“): " + ", ".join(sorted(_ELEMENT_EN)) + "; cardinal, fixed, mutable; "
             "the power to begin / hold / adapt; sign of beginning / holding / adaptation. "
             "Zählmenge: „ten main forces“, „planets“, „counted“ = gezählt; „weighted“, "
             "„factors“ = gewichtet.")
    L.append("")
    L.append("SIGNATUR UND BELEG bleiben in der analyse.md DEUTSCH, samt Inhalt "
             "(Kopfzeilen **Signatur:** / **Beleg:**, Zeichen-, Aspekt- und "
             "Faktornamen, TT.MM.JJJJ) — P1, P2, P7 und P13 lesen sie dort. Das "
             "PDF zeigt sie englisch (chartdoc, Modul Sprachfassung).")
    L.append("P17 (Subjekt-Probe) liest nur deutsch: in einer englischen Fassung "
             "die Subjekt-Regel von Hand pruefen.")
    return "\n".join(L)


ENGLISCH = _englisch_text()


def hilfe(name=None, datei=None):
    """Schnittstellen-Auskunft dieses Builders — statt den Quelltext zu lesen.

    hilfe()               Uebersicht: jede oeffentliche Funktion mit Signatur und
                          erstem Docstring-Absatz, dazu Fehlerklassen und die
                          Konstanten (GROSSBUCHSTABEN) mit gekuerztem Wert.
    hilfe('<name>')       der VOLLE Docstring EINER Funktion oder Klasse —
                          Argumente, Rueckgabeschluessel, Fehlerfaelle; bei einer
                          Konstante ihr voller Wert; 'modul' = der Docstring der
                          Datei selbst.
    hilfe(datei='<pfad>') schreibt statt zu drucken (fuer lange Uebersichten).
    hilfe('LESEFORMATE')  woran die Proben den Text erkennen — Themenliste,
                          Beleg-Segmente, Register, Deutungsort, P13-Schnitte.
    hilfe('ENGLISCH')     die englischen Wortlaute (Kicker, Bewegungen,
                          Pflichtteil, Nichtwissen, Verwerfung, Faktornamen)
                          in einem Aufruf — seit 2026-09-26.
    Kommandozeile:        python3 <builder>.py --hilfe [<name>]
    Rueckgabe: None (gedruckt) bzw. der Pfad der geschriebenen Datei.
    """
    import inspect as _insp
    import sys as _sys
    _m = _sys.modules[__name__]
    _mn = (_m.__name__ if _m.__name__ != '__main__'
           else __file__.rsplit('/', 1)[-1].rsplit('.', 1)[0])

    def _erste(doc):
        return (doc.strip().split('\n\n')[0].replace('\n', ' ').strip()
                if doc else '(kein Docstring — Signatur gilt)')

    def _sig(o):
        try:
            return str(_insp.signature(o))
        except (TypeError, ValueError):
            return '(…)'

    L = []
    if name in ('modul', '__doc__'):
        L.append('%s.py' % _mn)
        L.append(_m.__doc__ or '(kein Modul-Docstring)')
    elif name:
        o = getattr(_m, name, None)
        if o is None:
            L.append("%s.py: kein Eintrag '%s'. Uebersicht: %s.hilfe()"
                     % (_mn, name, _mn))
        elif _insp.isfunction(o) or _insp.isclass(o):
            L.append('%s.%s%s' % (_mn, name, _sig(o)))
            L.append(_insp.getdoc(o) or '(kein Docstring — Signatur gilt)')
        elif isinstance(o, str) and '\n' in o:     # Lesetext (LESEFORMATE) als Text
            L.append('%s.%s:' % (_mn, name))
            L.append(o)
        else:
            L.append('%s.%s = %r' % (_mn, name, o))
    else:
        L.append('%s.py — Schnittstellen (Einzelheiten: %s.hilfe(\'<name>\'), '
                 'Datei-Docstring: hilfe(\'modul\'))' % (_mn, _mn))
        L.append(_erste(_m.__doc__))
        L.append('')
        L.append('FUNKTIONEN')
        for n, o in sorted(vars(_m).items()):
            if (n.startswith('_') or not _insp.isfunction(o)
                    or o.__module__ != _m.__name__):
                continue
            L.append('  %s%s' % (n, _sig(o)))
            L.append('      %s' % _erste(_insp.getdoc(o)))
        klassen = [(n, o) for n, o in sorted(vars(_m).items())
                   if _insp.isclass(o) and o.__module__ == _m.__name__
                   and not n.startswith('_')]
        if klassen:
            L.append('')
            L.append('KLASSEN / FEHLERKLASSEN')
            for n, o in klassen:
                L.append('  %s: %s' % (n, _erste(_insp.getdoc(o))))
        konst = [(n, o) for n, o in sorted(vars(_m).items())
                 if n.isupper() and not n.startswith('_')
                 and not callable(o) and not _insp.ismodule(o)]
        if konst:
            L.append('')
            L.append("KONSTANTEN (voller Wert: hilfe('<NAME>'))")
            for n, o in konst:
                r = repr(o).replace('\n', ' ')
                L.append('  %s = %s%s' % (n, r[:88], '…' if len(r) > 88 else ''))
    text = '\n'.join(L)
    if datei:
        with open(datei, 'w', encoding='utf-8') as f:
            f.write(text + '\n')
        return datei
    print(text)
    return None


def _hilfe_cli(argv=None):
    """`--hilfe [<name>]` auf der Kommandozeile: druckt hilfe() und gibt True."""
    import sys as _sys
    argv = list(_sys.argv[1:] if argv is None else argv)
    if '--hilfe' not in argv:
        return False
    i = argv.index('--hilfe')
    name = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith('-') \
        else None
    hilfe(name)
    return True


if __name__ == "__main__":
    if _hilfe_cli():          # python3 inhaltsprobe.py --hilfe [<name>]
        sys.exit(0)
    sys.exit(_main(sys.argv[1:]))
