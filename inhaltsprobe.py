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
ENGLISCHE Analyse nach Werkzeuge-Modul A3 — englische Faktor- und Zeichennamen,
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

Die siebzehn Proben
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
                     Sonnenbogen, progressiver Mond, Finsternis gegen `zusatz`
                     (nur PRUEFEN).
P2  Beleg-Staende    Segment 1 jedes Normal-Belegs und jedes Instrument-Segment:
                     Zeichen und Haus gegen den @@SELEKTOR-Block (bei Grenzlage das
                     fuehrende Haus vorn), Gradminute gegen die Staendetabelle.
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
                     Ressourcen-Bauform, Zugang) ohne Wurzel und Widerstand.
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
                     2026-09-22).
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
                     Verbindungs-Rangzeile (2026-09-24). Nur PRUEFEN; englisch mit
                     eigenen Wortlisten (seit 2026-09-22).
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

Selbsttest: `python3 inhaltsprobe.py --selbsttest` laeuft gegen einen KONSTRUIERTEN
Fall ohne reales Geburtsdatum, ohne Uhrzeit, ohne Namen, ohne Staende eines realen
Charts (Datenschutz-Guardrail des Kerns) — einmal fehlerfrei, einmal mit je einem
eingebauten Fehler je Probe P1–P6 und P11–P15 und je einem Treffer fuer P8, P9,
P10 und P17, einmal mit Zugang-Kapitel; P16 und die Satzmuster von P17 als
Einzelproben; dazu ein Transit-Fall mit konstruierter events.json
(Daten aus Julianischen Tageszahlen gerechnet, kein Datum im Quelltext), fehlerfrei,
mit eingebauten Fehlern und ohne events.json. Eine Probe, die ihren Testfehler nicht
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
# Englische Sprachfassung (Werkzeuge-Modul A3; Klartext-Modul, Aktivierung): die
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
# englische Aspektwoerter (Sprachfassung, 2026-09-16d): Werkzeuge-Modul A3 nennt
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
                 # englischen Namen aus T12-18 (Werkzeuge A3 traegt sie noch nicht).
                 "mitlaufendes": ("running alongside", "also running"),
                 "der stand heute": ("where things stand", "as things stand"),
                 # 2026-09-22 (W57-Nachzug): `Getriebe` hatte keinen englischen Namen —
                 # eine englische Analyse verlor damit THEMA 1 (P3), und P14 prueste den
                 # Kopfblock des Getriebe-Kapitels nicht. `gearing` ist der Name fuer eine
                 # NEUE englische Fassung (einwortig wie Auftakt/Rechenschaft/Instrument),
                 # die drei uebrigen stehen fuer schon geschriebene Faelle.
                 "getriebe": ("gearing", "the gearing", "the mechanism", "mechanism")}
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
    ⚼ Anderthalbquadrat — und der Wort-Trenner des Datenblatt-Moduls
    (`–Anderthalbquadrat–`, Halbgeviertstriche).

    Zeilenregex woertlich aus `build._ressourcen_zeilen()` (sechsspaltige Form des
    Datenblatt-Moduls, Spalte 6 "zugleich" seit 15.09.2026 optional):
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
    # zugelassen, wie ihn das Datenblatt-Modul fuer die Untergrund-Tabelle nennt.
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
_ZUSATZ_SEG_ANFANG_RE = re.compile(r"^\W*(?:Sonnenbogen|solar[\s-]*arc|progressiv\w*|progressed|Finsternis|eclipse)", re.I)

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
        setzt der Textlauf; deshalb nur PRUEFEN."""
        p.geprueft += 1
        transit_gesehen.append(stelle)
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
    fuehrt das Nebenhaus, Grenzlage (2°–5°) das rechnerische Haus (Datenblatt-Modul)."""
    h, nh, ab = f.get("haus"), f.get("nebenhaus"), f.get("abstand")
    if not nh:
        return h, None
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
    re.compile(r"(?<![\wäöüß])(?P<n>%s)-?jährig" % _ZAHL, re.I),
    re.compile(r"(?<![\wäöüß])(?:du\s+bist|bist\s+du)\s+(?:jetzt\s+|heute\s+|gerade\s+|nun\s+)?"
               r"(?P<n>%s)(?=\s*(?:[.,;:!?–—)]|$)|\s+Jahre\b|\s+und\b)" % _ZAHL, re.I),
)
_P11_LEBENSJAHR = re.compile(
    r"(?<![\wäöüß])(?:(?P<z>\d{1,3})\.\s*Lebensjahr|(?:das|dem|dein|deinem|deines|ins|im|bis|und|"
    r"um\s+das)\s+(?P<w>%s)(?=\s*(?:,|und\b|oder\b|bis\b|–|Lebensjahr|wenn\b|\.|$)))" % _ORDWORT,
    re.I)
_P11_DEKADE = re.compile(r"(?<![\wäöüß])(?:(?P<wo>Anfang|Mitte|Ende)|um\s+die)\s+(?P<z>%s)(?![\wäöüß])"
                         % _ZEHNER_W, re.I)

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
            for rx in ALTER:
                for m in rx.finditer(satz):
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
    if p.geprueft == 0:
        p.hinweise.append("keine Datums- oder Altersangabe im Fließtext")
    return p.abschluss()

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

_ELEMENT_RE = re.compile(r"(?<![\wäöüß])(?:(Feuer|Erde|Luft|Wasser)(?:zeichen\w*|element\w*)?"
                         r"|(Erd)(?:zeichen\w*|element\w*))(?![\wäöüß])")
_MODUS_RE = re.compile(r"(?<![\wäöüß])([Kk]ardinal|[Ff]ix|[Vv]eränderlich|[Bb]eweglich)"
                       r"(?:e|en|er|es|em)?(?![\wäöüß])")
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
    ("einzig", re.compile(r"(?<![\wäöüß])einzig(?:e|en|er|es|em)?(?![\wäöüß])"
                          r"(?=\s+(?:[\wäöüß]+\s+){0,2}%s)"
                          r"|(?<![\wäöüß])nur\s+(?:ein|eine|einen|einem|einer)\s+"
                          r"(?=(?:einzig\w*\s+)?%s)" % (_EINZIG_NOMEN, _EINZIG_NOMEN), re.I)),
    ("kein_anderer", re.compile(r"(?<![\wäöüß])(?:kein(?:e|en|em|er)?\s+(?:andere[rnms]?|weitere[rnms]?)"
                                r"|sonst\s+kein\w*)(?![\wäöüß])", re.I)),
    ("x_von_y", re.compile(r"(?<![\wäöüß])(?P<x>%s|eine[rns]?|ein)\s+von\s+(?P<y>%s)(?![\wäöüß])"
                           % (_ZAHL, _ZAHL), re.I)),
    ("haelfte", re.compile(r"(?<![\wäöüß])(?:(?P<vgl>mehr|weniger)\s+als\s+)?die\s+Hälfte"
                           r"(?![\wäöüß])(?!\s+(?:eines\s+)?Grad)"
                           r"|(?<![\wäöüß])(?P<drittel>ein|zwei)\s+Drittel(?![\wäöüß])(?!\s+(?:eines\s+)?Grad)"
                           r"|(?<![\wäöüß])(?P<proz>\d{1,3})\s*(?:%|Prozent)(?![\wäöüß])", re.I)),
    # Grundzahl ab zwei, oder „nur/genau … eine" — der unbestimmte Artikel allein
    # („eine Verbindung, die von selbst hält") ist keine Zaehlaussage.
    ("n_verbindungen", re.compile(
        r"(?<![\wäöüß])(?:(?P<n>zwei|drei|vier|fünf|fuenf|sechs|sieben|acht|neun|zehn|elf|zwölf|"
        r"zwoelf|\d{1,2})|(?:nur|genau|bloß|lediglich|gerade\s+einmal|nicht\s+mehr\s+als)\s+"
        r"(?P<ein>eine[rnm]?|ein))\s+(?:[\wäöüß]+\s+)?Verbindung(?:en)?(?![\wäöüß])", re.I)),
    # 2026-09-24 (Pruefberichte vom 24.09.): „alle zwölf Jahre", „etwa alle neun Jahre"
    # nennen eine Umlaufzeit (Strukturbild §7; keine Probe prueft sie), keine Zaehlung
    # im Chart — sie kamen in jedem Lauf als PRUEFEN und stimmten jedes Mal.
    ("alle_n", re.compile(r"(?<![\wäöüß])alle\s+(?:%s)(?![\wäöüß])"
                          r"(?!\s+(?:(?:bis|oder)\s+\S+\s+)?(?:Jahr|Monat|Woche|Tag)\w*)"
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


def _rang_befund(art, m, satz, rz, typ, vorher="", eigen=None):
    """None, wenn die Rangzeile die Aussage traegt; sonst der Befundtext.
    vorher: der Satz davor (Bezug von „Das ist die engste Verbindung …").
    eigen: die Planeten im eigenen Zeichen aus Strukturbild §3 (`_eigenes_zeichen()`,
    None: §3 fehlt), Fundstelle fuer „der Planet, der keinem anderen folgt" (2026-09-24)."""
    if not rz:
        return ("Rang-, Zähl- oder Einzigkeitsaussage — das Datenblatt hat keine Rangzeilen "
                "(Strukturbild §10, seit 2026-09-19); die Zahl von Hand gegen die Tabellen halten")
    if typ == "transit" and re.search(r"laufend|Transit|Kontakt|Stichtag", satz):
        return ("Rangwort über Transit-Kontakte — die Rangzeilen gelten der Radix; gegen "
                "Jetzt-Liste und events.json halten")
    g = m.groupdict()
    fak = [f for _, _, f in _faktoren_im_satz(satz)]
    fak_v = [f for _, _, f in _faktoren_im_satz(vorher)] if vorher else []
    me = _ELEMENT_RE.search(satz)
    mm = _MODUS_RE.search(satz)
    if not (me or mm) and art in ("einzig", "kein_anderer", "x_von_y", "haelfte") and vorher \
            and re.search(r"Planet|Faktor|Element|Zeichen", satz):
        me, mm = _ELEMENT_RE.search(vorher), _MODUS_RE.search(vorher)
    element = ({"Erd": "Erde"}.get(me.group(1) or me.group(2), me.group(1) or me.group(2))
               if me else None)
    modus = ({"beweglich": "veränderlich"}.get(mm.group(1).lower(), mm.group(1).lower())
             if mm else None)

    def liste(schl):
        return [e for e in rz.get(schl, {}).get("eintraege", []) if "rang" in e]

    def zaehlungen():
        """Welche Zaehlung meint der Satz? Keine Angabe: beide muessen es tragen."""
        if re.search(r"gewichtet", satz):
            return ["gewichtet"]
        if re.search(r"gezählt|von\s+zehn|Planet", satz):
            return ["gezaehlt"]
        if re.search(r"Faktor|Punkt|Stelle", satz):
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
            falsch = []
            for a, e in werte:
                traeger = [kanon(n_) for n_, _ in e["traeger"]]
                ok = (not traeger) if null else (
                    len(traeger) == 1 and (not fak or traeger[0] in fak or len(set(fak)) > 1))
                if not ok:
                    falsch.append("%s-%s: %s — %d Träger" % (fam, a, _rang_txt(e).split(". ", 1)[1],
                                                            len(traeger)))
            if not falsch:
                return None
            gilt = [a for a, e in werte if "%s-%s:" % (fam, a) not in " ".join(falsch)]
            return ("Rangzeile %s%s" % ("; ".join(falsch), " — gilt nur %s; die Zählung nennen"
                                        % gilt[0] if gilt else ""))
        if re.match(r"\s*(?:[\wäöüß]+\s+)?(?:Verbindung|Aspekt)", satz[m.end():], re.I):
            # „Jupiter mit einer einzigen Verbindung" — der Faktor steht davor oder im
            # selben Satzglied dahinter; „eine einzige Verbindung: die zwischen Neptun
            # und Pluto" zaehlt keine Verbindungen eines Faktors.
            vor = [f for a_, e_, f in _faktoren_im_satz(satz) if a_ < m.start()]
            glied = re.split(r"[:;—–]", satz[m.end():], 1)[0]
            nach = [f for _, _, f in _faktoren_im_satz(glied)]
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
            schl = (["verbindungen-gewichtet"] if re.search(r"verschalt|dicht|Verkehr|vernetzt|gewichtet",
                                                            satz)
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
    for ch, bewegung, text in _fliesstext(chapters):
        ist_getriebe = (_ist_kicker(ch, "Getriebe")
                        or _kapitelart(ch, typ, chapters) == "Getriebe-Kapitel")
        saetze = _saetze_pos(text)
        for i, (_a, _e, satz) in enumerate(saetze):
            if not _hat_referent(satz):
                continue
            treffer = sorted(((m.start(), m.end(), art, m) for art, rx in MUSTER
                              for m in rx.finditer(satz)), key=lambda t: (t[0], -t[1]))
            belegt = []
            for a, e, art, m in treffer:
                if any(not (e <= x or a >= y) for x, y in belegt):
                    continue
                belegt.append((a, e))
                p.geprueft += 1
                befund = _rang_befund(art, m, satz, rz, typ, saetze[i - 1][2] if i else "",
                                      eigen=eigen)
                if befund:
                    if ist_getriebe and befund.startswith(("Zählaussage", "Count statement")):
                        getriebe_zahlen += 1
                        continue
                    p.pruefen.append("%s · %s: „%s“ — „%s“: %s"
                                     % (_bezeichnung(ch), bewegung, _kurz(satz, 140),
                                        _ws(m.group(0)), befund))
    if getriebe_zahlen:
        p.hinweise.append("Getriebe-Kapitel: %d Verhältniszahl(en) nicht als PRÜFEN gemeldet — "
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
# (3) ACHSENPAAR — AC/DC und MC/IC stehen einander immer gegenüber; ein Satz, der
#     beide Enden nennt („über deinen Deszendenten … deinem Aszendenten
#     gegenüber"), behauptet damit keinen Aspekt. Solche Paarungen zaehlen nicht.
_ACHSENPAARE = {frozenset(("AC", "DC")), frozenset(("MC", "IC"))}
# (4) ZUSATZ-SEGMENTE im Transit-Beleg („Sonnenbogen-Merkur ☿ Quadrat □ R-Neptun ♆")
#     decken die gleichnamige Konstellation im Text; P1 prueft ihr Datum.
_ZUSATZ_KONTAKT_RE = re.compile(
    r"(?:Sonnenbogen|solar[\s-]*arc)[\s-]+(?P<t>" + _FAKTOR_RE + r")(?![\wäöüÄÖÜß])"
    r"(?P<mitte>.*?)(?<![\wäöüÄÖÜß])R-\s*(?P<r>" + _FAKTOR_RE + r"|Knoten)(?![\wäöüÄÖÜß])",
    re.I | re.S)


def _konstellationen(satz, vorher=""):
    """Konstellationen eines Fliesstext-Satzes (s. Kommentar oben) ->
    [(Faktoren davor, Art, Faktoren danach, Treffer)]; Art ist bei einem Aspektwort
    die Aspektart (str), bei einem Bild das Tupel der Arten, fuer die es steht —
    leer, wenn es fuer keine bestimmte steht."""
    fak = _faktoren_im_satz(satz)
    marker = [(m, _art(m.group(1)) if m.group(1) else _ASP_GLYPH.get(m.group(2)))
              for m in ASPEKT_RE.finditer(satz)]
    for m in _BILD_RE.finditer(satz):
        if not any(m.start() < x.end() and x.start() < m.end() for x, _ in marker):
            marker.append((m, _bild_arten(m.group(0)) or ()))
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
    for _i, (m, art) in enumerate(marker):
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
        if not davor and len(danach) >= 2 and (re.match(r"\s*(?:zwischen|between)\b", satz[m.end():])
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
        if not danach and len(set(davor)) >= 2 and not vor_schnitt:     # (9): nur leiser
            danach = [davor[-1]]
            davor = [f for f in davor[:-1] if f != danach[0]]
        if davor and danach:
            out.append((davor, art, danach, m))
            vorige_davor = davor
    return out

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
            for davor, art, danach, m in _konstellationen(satz, saetze[i - 1][2] if i else ""):
                if (art, m.start()) in gesehen:
                    continue
                gesehen.add((art, m.start()))
                paarungen = [(x, y) for x in reversed(davor) for y in danach
                             if _paar_ok(x, y, typ)]                        # (3), (7)
                if not paarungen:           # „Pluto … zu sich selbst": Zyklus, kein Radix-Aspekt
                    continue
                p.geprueft += 1
                if any(gedeckt(x, art, y) for x, y in paarungen):
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
        if "Deutungsort" not in zeile or re.match(r"^\s*(?:Zählmenge|\*\*|>)", zeile):
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
        ort = mz.group("ort").strip()
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
# Die Vergleiche laufen ueber casefold(), und casefold() macht aus „ß" „ss": „heißt"
# traf „heisst" nie, „außerhalb" nie „ausserhalb" (2026-09-25 — „der Deszendent
# heißt" kam deshalb als Handelnder). Alle Vergleichslisten werden ebenso gefaltet.
(_P17_PRAEP, _P17_OBLIQ, _P17_NOM, _P17_PRONOMEN, _P17_BINDER, _P17_ANKERVERBEN, _P17_ADVERB,
 _P17_ZAHL, _P17_OBJEKT, _P17_SUBJEKT_PRONOMEN, _P17_HABEN, _P17_WERDEN, _P17_REL) = (
    frozenset(w.casefold() for w in _l) for _l in (
        _P17_PRAEP, _P17_OBLIQ, _P17_NOM, _P17_PRONOMEN, _P17_BINDER, _P17_ANKERVERBEN,
        _P17_ADVERB, _P17_ZAHL, _P17_OBJEKT, _P17_SUBJEKT_PRONOMEN, _P17_HABEN, _P17_WERDEN,
        _P17_REL))
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
    while j >= 0 and tok[j].casefold() in _P17_ADVERB:
        j -= 1
    return j

def _p17_ist_verbwort(t):
    """Kann das Wort ein Verb sein? Kleingeschrieben und kein Funktionswort (Artikel,
    Praeposition, Pronomen, Konjunktion, Adverb, Zahlwort) — 2026-09-25."""
    tl = t.casefold()
    return (t[:1].islower() and t.isalpha() and len(t) > 1 and tl not in _P17_PRAEP
            and tl not in _P17_OBLIQ and tl not in _P17_NOM and tl not in _P17_PRONOMEN
            and tl not in _P17_BINDER and tl not in _P17_ADVERB and tl not in _P17_ZAHL
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
                                             or _p17_ist_adjektiv(tok[k - 1]))
        if (tl in _P17_PRAEP or tl in _P17_OBLIQ or tl in _P17_NOM or t[:1].isupper()
                or tl in ("und", "oder", "sowie") or tl in _P17_ADVERB
                or tl in _P17_ZAHL or tl in _P17_OBJEKT
                or _P17_ORDINAL_RE.match(t) or adjektiv):
            k, n = k + 1, n + 1
            continue
        return tl
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
        verb = _p17_folgeverb(tok, i)
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
    proben = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17]

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

Du bleibst, wo andere längst gegangen sind. Und ein Letztes, das schwerer zuzugeben ist: Manchmal bleibst du aus Bequemlichkeit.

### Was da arbeitet

Dein Mond im Stier im zweiten Haus, im Trigon zu Saturn — eine Verbindung, die von selbst hält — braucht keine Bewegung, um sich sicher zu fühlen. Was Saturn dazugibt, ist Form: Das Gefühl bekommt einen Rahmen, in dem es bleiben kann. Dieses Kapitel läuft in der Kurzform: Ein einzelner harmonischer Aspekt liefert kein Material für Wurzel und Widerstand.

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
                   ev("Saturn", "Quadrat", "Merkur", (75, 190), 0.9340, 30, 230),
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
        and not _ZUSATZ_SEG_ANFANG_RE.match("T-Saturn ♄ Quadrat □ R-Mond ☽ — exakt 01.03.2027"), \
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
    for nr in ("P11", "P12", "P13", "P14", "P15"):
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
        ("P16", "aussagelos"), ("P1", "teilweise übersprungen")] and \
        "events.json" in r6["uebersprungen"][1][2], "Lauf 6: %s" % r6["uebersprungen"]
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
    berichte.append("Lauf 8 (Transit, Deutungsort über dem Deckel): erkannt, 8b gemeldet")

    if not still:
        print("\n".join(berichte))
        print("[Selbsttest bestanden: Einzelproben der Muster; Lauf 1 ohne Befund (nur der "
              "Getriebe-Beleg teilweise übersprungen), Lauf 2 findet je Probe den eingebauten Fehler, "
              "Lauf 3 liest das Zugang-Kapitel; Transit: Lauf 4 sauber mit events.json, Lauf 5 und 5b "
              "finden die eingebauten Fehler, Lauf 6 ohne events.json nur teilweise übersprungen; "
              "Lauf 7 dieselbe Analyse mit dem Kicker `Getriebe` und der neuen Zählung, 7b ohne ihn; "
              "Lauf 8 Deutungsort über dem Deckel; P16 und P17 als Einzelproben]")
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
LESEFORMATE = """Woran die Proben den Text erkennen (Stand 2026-09-24).

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
  TT.MM.JJJJ`, `progressiver Mond → Haus n — TT.MM.JJJJ`. Datum IMMER TT.MM.JJJJ,
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

DEUTUNGSORT (Ressourcen-Block) — P15.
  Zeile `… — Deutungsort: Thema n` | `Ressource n` | `Was trägt`; im Transit auch
  „Was dich durch diese Zeit trägt" (Abschnitt `###`) und `Mitlaufendes (Deckel)`
  für Kontakte über dem Deckel von sechs — dort genügt eine Zeile im Kapitel
  `Mitlaufendes`, die beide Faktoren nennt. Ein anderer Ort ist PRÜFEN.
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

STRUKTURBILD §3 (chart_data) — P12.
  Die Zeilen „- Enddispositoren (im eigenen Zeichen, …): …" und „- Im eigenen Zeichen
  ohne Zulauf (…): …", Namen durch Komma getrennt; Klammern („(Ketten von …)") zählen
  nicht. Wer dort steht, folgt keinem anderen. Die Einzahl („der Planet, der keinem
  anderen folgt", „als einziger") ist gedeckt, wenn der Satz alle nennt; die
  Eigenschaft („dein Mond … folgt keinem anderen", „richtet sich nach keinem
  anderen"), wenn der genannte dort steht. Fehlen beide Zeilen, meldet P12 „§3
  nicht gefunden".
"""


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
