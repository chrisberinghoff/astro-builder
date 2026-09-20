#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selektor.py — Schritt-2-Referenzschnitt.

Liest aus <klient>_chart_data.md den maschinenlesbaren @@SELEKTOR-Block,
leitet nach Plan §5 die benoetigten Blockschluessel ab, zieht NUR diese Bloecke
aus blocks/ und schreibt eine kompakte <klient>_referenz.md.

PFLICHT-Vollstaendigkeitspruefung: fuer JEDEN Faktor und JEDEN Aspekt wird
protokolliert, welche Bloecke gezogen wurden. Fehlt ein abgeleiteter Block in
blocks/ -> HARTER Fehler mit Namen (nie stilles Weglassen). Lieber ein Block zu
viel.

GRENZLAGEN (5°-Haus-Regel, s. radix.haus_und_grenzlage): Steht ein Faktor 5° oder
weniger VOR der naechsten Hausspitze, faerbt er das Folgehaus mit. Schritt 1 haengt
dann `nebenhaus=<N> abstand=<Grad>` an die FAKTOR-Zeile; der Selektor zieht BEIDE
Hausbloecke und schreibt die Gewichtungsstufe als Deutungsanweisung in die
referenz.md (Abstand <= 2° -> Nebenhaus fuehrt; 2°-5° -> Nebenhaus als Nebenton).
Ohne `nebenhaus=` verhaelt sich alles wie zuvor.

FAKTORNAMEN: kanonisch sind die zehn Planeten und die fuenf Spezialfaktoren
CHIRON, LILITH, MONDKNOTEN, PHOLUS, GLUECKSPUNKT. Gaengige Schreibweisen loest
FAKTOR_ALIAS auf (KNOTEN/NORDKNOTEN -> MONDKNOTEN, VERMOEGEN -> GLUECKSPUNKT ...).
Die Knotenachse wird IMMER ueber die Nordknoten-Zeile gefuehrt — eine eigene
SUEDKNOTEN-Zeile wird uebersprungen und protokolliert, weil die Referenz
achsenbasiert ist (MONDKNOTEN_HAUS_6 = ☊6/☋12) und eine zweite Zeile mit haus=12
die GESPIEGELTE Achse zoege. Ein Faktorname, der sich nicht aufloesen laesst, ist
seit 30.07.2026 ein HARTER Fehler (vorher fiel er lautlos durch, s. Kommentar bei
FAKTOR_ALIAS).

FUEHRT-FELD (seit 2026-09-06): Traegt eine FAKTOR-Zeile `fuehrt=ja`, fuehrt
dieser Faktor laut Themenliste ein Kapitel. Zwei Wirkungen: (a) bei der SONNE
wandert das Sonnenzeichen-Kapitel in die gelesene Gruppe 'Sonnenzeichen' statt
in die ueberspringbare 'Sonnenzeichen-Hintergrund'; (b) der Grenzlagen-Warnblock
sagt je Faktor, ob beide Haeuser auszudeuten sind oder ob beide nur angegeben
werden (Registerzeile). Ohne das Feld verhaelt sich alles wie zuvor — das Feld
ist optional und additiv.
Die Methoden-Segmente der Spezialfaktoren (_ALLG/_SEC_*) bleiben seit dem
2026-09-19 (W59, Chris-Entscheidung Frage 16) AUCH bei `fuehrt=ja` in der
ueberspringbaren 'Spezialfaktor-Methodik'. Vorher zog `fuehrt=ja` sie in die
gelesene Gruppe — 87 bis 135 Zeilen je Faktor, gebraucht wurden drei bis vier
Saetze. Das chart-spezifische Material (Zeichen, Haus, Aspekte) steht ohnehin
immer in der gelesenen Gruppe.

GRENZLAGEN-ZEILEN (seit 2026-09-19, W35 und F19): Je grenzlagigem Faktor stehen
im ⚠-Block fertige Zeilen zum Uebernehmen — die Signatur-WORTFORM fuer den
Klartext (echte Umlaute, keine Gradzahl, fuehrendes Haus vorn), die Notation
fuer den Fachmodus, die Beleg-Angabe (die EINZIGE Stelle mit Gradzahl) und fuer
einen nicht fuehrenden Faktor die Hausangabe seiner Registerzeile. Der Wortlaut
fuer den nicht fuehrenden Faktor haengt vom Typ ab: Heisst die Datei
`<klient>_Transit_chart_data.md`, gibt es kein Rechenschaftskapitel (das
Register „Mitlaufendes" fuehrt Kontakte, nicht Faktoren).

FEHLSTELLEN (eindeutig seit 2026-09-19, W36): Ein angeforderter Aspekt, fuer den
die Bibliothek keinen Block fuehrt (Spezialfaktor mit Spezialfaktor, Achse mit
Achse, ausserhalb des Systems), IST eine Fehlstelle. Sie bricht nicht ab: Die
referenz.md wird geschrieben, ihr Kopf zaehlt die Fehlstelle, der Abschnitt
„⚠ FEHLSTELLEN" nennt sie samt Anweisung (aus den Nachbarbloecken deuten, in der
Referenzdatei-Liste melden), das Auswahl-Protokoll schreibt „FEHLSTELLE" und die
Schlusszeile zaehlt sie. Vorher stand im selben Lauf „nicht als Block gefuehrt"
neben „Fehlstellen: 0" und „keine Fehlstelle". Hart bleibt, was die Bibliothek
fuehren MUESSTE und nicht hat (FEHLT … in …).

NUR-LISTE-MODUS (seit 2026-09-19, W40): `--liste` sagt, welche
Bibliotheksdateien und wie viele Bloecke das Chart braucht, und nennt die
Fehlstellen — ohne Bibliothek und ohne eine referenz.md zu schreiben. Gedacht
fuer die Referenzdatei-Liste am Ende von Schritt 1 (dieselben harten Proben wie
der volle Lauf: leere Aspektebene, unbekannter Faktor). Mit der Bibliothek als
zweitem Argument prueft er zusaetzlich, ob jeder Block da ist.

@@SELEKTOR-Blockformat (Schritt 1 schreibt ihn ins chart_data.md):
    @@SELEKTOR
    FAKTOR SONNE zeichen=Krebs haus=11 nebenhaus=12 abstand=3.22 fuehrt=ja
    FAKTOR MOND zeichen=Krebs haus=12 fuehrt=ja
    ...
    FAKTOR MONDKNOTEN zeichen=Wassermann haus=6
    FAKTOR PHOLUS zeichen=Fische haus=7 nebenhaus=8 abstand=4.17
    FAKTOR GLUECKSPUNKT zeichen=Fische haus=7
    ACHSE AC zeichen=Loewe
    ACHSE MC zeichen=Widder
    ASPEKT SONNE MOND
    ASPEKT MARS AC
    ...
    @@ENDE

Aufruf:  python3 selektor.py <chart_data.md> [blocks_dir] [out.md]
         python3 selektor.py <chart_data.md> --liste [blocks_bundle.txt]
         python3 selektor.py --selbsttest      (ohne Bibliothek, konstruierte Werte)
"""
import os
import re
import sys

PLANETS = ['SONNE', 'MOND', 'MERKUR', 'VENUS', 'MARS', 'JUPITER', 'SATURN',
           'URANUS', 'NEPTUN', 'PLUTO']
PSET = set(PLANETS)
MARK_RE = re.compile(r'^@@BLOCK key=(\S+)@@$')

# --- Faktornamen: Schreibweisen -> kanonischer Blockschluessel ---------------
# Grund (Vorfall 30.07.2026): parse_chart normalisierte FAKTOR-Zeilen nur mit
# norm(); `FAKTOR KNOTEN` blieb also 'KNOTEN' und lag weder in PSET noch in
# SPEZFILE. Der Faktor fiel LAUTLOS durch — keine Bloecke, keine Fehlstelle,
# keine Warnung. Die komplette Mondknoten-Deutung (Zeichen UND Haus) fehlte im
# Referenzschnitt, und der Lauf meldete trotzdem "keine Fehlstelle". Seither:
# (a) Aliasse werden aufgeloest, (b) ein unbekannter Faktorname ist ein HARTER
# Fehler wie eine Fehlstelle.
FAKTOR_ALIAS = {
    'KNOTEN': 'MONDKNOTEN', 'NORDKNOTEN': 'MONDKNOTEN',
    'MONDKNOTENACHSE': 'MONDKNOTEN', 'KNOTENACHSE': 'MONDKNOTEN',
    'AUFSTEIGENDER MONDKNOTEN': 'MONDKNOTEN', 'DRACHENKOPF': 'MONDKNOTEN',
    'SCHWARZER MOND': 'LILITH', 'LILITH (SCHWARZER MOND)': 'LILITH',
    'PARS FORTUNAE': 'GLUECKSPUNKT', 'VERMOEGEN': 'GLUECKSPUNKT',
    'GLUECKSPUNKT (PARS FORTUNAE)': 'GLUECKSPUNKT',
    'ASZENDENT': 'AC', 'DESZENDENT': 'DC',
    'MEDIUM COELI': 'MC', 'IMUM COELI': 'IC', 'IMMUM COELI': 'IC',
}

# Faktoren, die KEINE eigene Deutung bekommen, weil sie der Spiegelpol eines
# bereits gefuehrten Faktors sind. Der Suedknoten wird ueber die Nordknoten-
# Zeile mitgedeutet: die Mondknoten-Referenz ist achsenbasiert (MONDKNOTEN_HAUS_6
# behandelt ☊6/☋12). Eine eigene Suedknoten-Zeile mit haus=12 zoege
# MONDKNOTEN_HAUS_12 — also die GESPIEGELTE Achse und damit die falsche Deutung.
SPIEGEL_FAKTOREN = {
    'SUEDKNOTEN': 'MONDKNOTEN', 'ABSTEIGENDER MONDKNOTEN': 'MONDKNOTEN',
    'DRACHENSCHWANZ': 'MONDKNOTEN',
}

# Grenzlagen-Schwellen (Grad vor der naechsten Hausspitze).
GRENZ_ORB = 5.0      # bis hierher gilt ueberhaupt Grenzlage (= radix.HAUS_ORB)
SCHWELLE_ORB = 2.0   # bis hierher fuehrt das Nebenhaus die Deutung

STEM = {'WIDDER': 'Widder', 'STIER': 'Stier', 'ZWILLINGE': 'Zwillinge',
        'KREBS': 'Krebs', 'LOEWE': 'Loewe', 'JUNGFRAU': 'Jungfrau',
        'WAAGE': 'Waage', 'SKORPION': 'Skorpion', 'SCHUETZE': 'Schuetze',
        'STEINBOCK': 'Steinbock', 'WASSERMANN': 'Wassermann', 'FISCHE': 'Fische'}
ASPSTEM = {'SONNE': 'Sonne', 'MOND': 'Mond', 'MERKUR': 'Merkur', 'VENUS': 'Venus',
           'MARS': 'Mars', 'JUPITER': 'Jupiter', 'SATURN': 'Saturn',
           'URANUS': 'Uranus', 'NEPTUN': 'Neptun', 'PLUTO': 'Pluto'}

F02, F03, F04, F01 = ('02_Sonne_und_Mond_in_Zeichen.txt',
                      '03_Merkur_Venus_Mars_in_Zeichen.txt',
                      '04_Jupiter_Saturn_Generationsplaneten.txt',
                      '01_Planeten_Grundprinzipien.txt')
F05 = '05_Aszendent_MC_Deszendent_Tabellen.txt'
SPEZFILE = {'CHIRON': 'Chiron_Haus_Zeichen_Aspekte.txt',
            'LILITH': 'Lilith_SchwarzerMond_Haus_Zeichen_Aspekte.txt',
            'MONDKNOTEN': 'Mondknotenachse_Haus_Zeichen_Aspekte.txt',
            'PHOLUS': 'Pholus_Haus_Zeichen_Aspekte.txt',
            'GLUECKSPUNKT': 'Glueckspunkt_Haus_Zeichen_Aspekte.txt'}
ZEICHENFILE = {'SONNE': F02, 'MOND': F02, 'MERKUR': F03, 'VENUS': F03,
               'MARS': F03, 'JUPITER': F04, 'SATURN': F04,
               'URANUS': F01, 'NEPTUN': F01, 'PLUTO': F01}


def norm(s):
    s = (s or '').strip().upper()
    for a, b in (('Ö', 'OE'), ('Ü', 'UE'), ('Ä', 'AE'), ('ß', 'SS')):
        s = s.replace(a, b)
    return s


def norm_faktor(t):
    """Kanonischer Faktorname fuer FAKTOR-Zeilen (Zeichen-/Hausbloecke).

    Anders als norm_token (das fuer ASPEKT-Zeilen alle Knoten-Schreibweisen auf
    'KNOTEN' zusammenzieht, weil resolve_aspect diesen Token erwartet) liefert
    diese Funktion den Schluessel, unter dem PSET/SPEZFILE nachschlagen —
    fuer die Knotenachse also 'MONDKNOTEN'.
    """
    t = norm(t)
    return FAKTOR_ALIAS.get(t, t)


def norm_token(t):
    t = norm(t)
    if t in ('KNOTEN', 'MONDKNOTEN', 'NORDKNOTEN', 'SUEDKNOTEN', 'AUFSTEIGENDER MONDKNOTEN'):
        return 'KNOTEN'
    if t in ('ASZENDENT', 'AC'):
        return 'AC'
    if t in ('DESZENDENT', 'DC'):
        return 'DC'
    if t in ('MC', 'MEDIUM COELI'):
        return 'MC'
    if t in ('IC', 'IMUM COELI', 'IMMUM COELI'):
        return 'IC'
    return t


def haus_file(n):
    n = int(n)
    return 'Haus_0%d_Planeten.txt' % n if 1 <= n <= 6 else 'Haus_%d.txt' % n


def aspekt_file(pl):
    return ASPSTEM[pl] + '_Aspekte.txt'


def _gradmin(deg):
    """Dezimalgrad -> N°NN′ (fuer Signatur/Beleg im Klartext-Modus)."""
    try:
        d = float(deg)
    except (TypeError, ValueError):
        return '?'
    g = int(d)
    m = int(round((d - g) * 60))
    if m == 60:
        g, m = g + 1, 0
    return '%d°%02d′' % (g, m)


def grenz_stufe(abstand):
    """Gewichtungsstufe der Grenzlage als Klartext-Deutungsanweisung.

    <= SCHWELLE_ORB (2°): der Faktor sitzt praktisch auf der Spitze -> das
    Nebenhaus fuehrt die Deutung. Darueber bis GRENZ_ORB (5°): das rechnerische
    Haus fuehrt, das Nebenhaus klingt als deutlicher Nebenton mit.
    """
    try:
        a = float(abstand)
    except (TypeError, ValueError):
        return 'fuehrend', 'Abstand nicht angegeben — beide Haeuser gleichrangig deuten'
    if a <= SCHWELLE_ORB:
        return 'nebenhaus_fuehrt', (
            'Schwellenlage (%.2f° vor der Spitze): das NEBENHAUS fuehrt die '
            'Deutung, das rechnerische Haus klingt mit' % a)
    return 'nebenton', (
        'Grenzlage (%.2f° vor der Spitze): das rechnerische Haus fuehrt, das '
        'Nebenhaus als deutlicher Nebenton' % a)


# 2026-09-19 (W35): Bausteine der fertigen Grenzlagen-Zeilen. Echte Umlaute,
# weil die Zeilen 1:1 in die Analyse gehen (T34-18d Nr. 22: „fuehrt" stand so in
# einer Signatur). Dativ fuer die Signatur („im zwoelften Haus"), Nominativ fuer
# die Registerzeile („zwoelftes/elftes Haus, Schwellenlage").
_ORD_DATIV = {1: 'ersten', 2: 'zweiten', 3: 'dritten', 4: 'vierten',
              5: 'fünften', 6: 'sechsten', 7: 'siebten', 8: 'achten',
              9: 'neunten', 10: 'zehnten', 11: 'elften', 12: 'zwölften'}
_ORD_NOM = {1: 'erstes', 2: 'zweites', 3: 'drittes', 4: 'viertes',
            5: 'fünftes', 6: 'sechstes', 7: 'siebtes', 8: 'achtes',
            9: 'neuntes', 10: 'zehntes', 11: 'elftes', 12: 'zwölftes'}
FAKTOR_ANZEIGE = {'SONNE': 'Sonne', 'MOND': 'Mond', 'MERKUR': 'Merkur',
                  'VENUS': 'Venus', 'MARS': 'Mars', 'JUPITER': 'Jupiter',
                  'SATURN': 'Saturn', 'URANUS': 'Uranus', 'NEPTUN': 'Neptun',
                  'PLUTO': 'Pluto', 'CHIRON': 'Chiron', 'LILITH': 'Lilith',
                  'MONDKNOTEN': 'Mondknoten', 'SUEDKNOTEN': 'Südknoten',
                  'PHOLUS': 'Pholus', 'GLUECKSPUNKT': 'Glückspunkt'}


def _ord(n, tafel):
    """Hausnummer -> Ordinalwort; Unlesbares bleibt als Zahl mit Punkt stehen."""
    try:
        return tafel[int(n)]
    except (KeyError, TypeError, ValueError):
        return '%s.' % n


def _ordnung(g):
    """(fuehrendes Haus, zweites Haus, Stufenwort). Schwellenlage (<= 2°): das
    Nebenhaus fuehrt; Grenzlage (2°–5°) und fehlender Abstand: das rechnerische."""
    if g['stufe'] == 'nebenhaus_fuehrt':
        return g['nebenhaus'], g['haus'], 'Schwellenlage'
    return g['haus'], g['nebenhaus'], 'Grenzlage'


def signatur_notation(g):
    """Fertige Signatur-WORTFORM fuer den Klartext-Standard (Schritt 2 uebernimmt sie 1:1).

    Seit 2026-09-19 (W35) in Worten, mit echten Umlauten und OHNE Gradzahl, wie
    es das Typmodul fuer den Klartext verlangt („Saturn im zwoelften Haus, dicht
    an der Schwelle aus dem elften"). Vorher lieferte die Funktion die Notation
    mit Grad („Haus 11/12 (Grenzlage, 3°13′ vor Spitze 12; Haus 11 fuehrt, 12
    klingt mit)") — Gradzahl und ASCII-Umlaut in einer Zeile, die 1:1 in die
    Signatur ging. Das fuehrende Haus steht vorn: bei Schwellenlage das
    Nebenhaus („dicht an der Schwelle aus dem …"), bei Grenzlage das
    rechnerische Haus („nahe an der Schwelle zum …"). Fachmodus:
    fachmodus_notation(); die Gradzahl steht nur im Beleg: beleg_notation().
    """
    fh, zh, stufe = _ordnung(g)
    name = FAKTOR_ANZEIGE.get(g['faktor'], g['faktor'].capitalize())
    if stufe == 'Schwellenlage':
        return '%s im %s Haus, dicht an der Schwelle aus dem %s' % (
            name, _ord(fh, _ORD_DATIV), _ord(zh, _ORD_DATIV))
    return '%s im %s Haus, nahe an der Schwelle zum %s' % (
        name, _ord(fh, _ORD_DATIV), _ord(zh, _ORD_DATIV))


def fachmodus_notation(g):
    """Signatur im Fachmodus (Typmodul): „Haus 12/11, Schwellenlage" — fuehrendes
    Haus vorn, ohne Gradzahl. Neu 2026-09-19 (W35)."""
    fh, zh, stufe = _ordnung(g)
    return 'Haus %s/%s, %s' % (fh, zh, stufe)


def beleg_notation(g):
    """Hausangabe fuer das Staende-Segment des Belegs — die EINZIGE Stelle mit
    Gradzahl: „12./11. Haus (Schwellenlage, 1°47′ vor Spitze 12)". Form wie der
    Klartext-Beleg („…, 9. Haus"); inhaltsprobe P2 liest das fuehrende Haus vorn.
    Neu 2026-09-19 (W35)."""
    fh, zh, stufe = _ordnung(g)
    grad = _gradmin(g['abstand'])
    if grad == '?':
        return ('%s./%s. Haus (%s, Abstand fehlt — abstand= im '
                '@@SELEKTOR-Block nachtragen)' % (fh, zh, stufe))
    return '%s./%s. Haus (%s, %s vor Spitze %s)' % (fh, zh, stufe, grad,
                                                    g['nebenhaus'])


def register_notation(g):
    """Hausangabe der Registerzeile eines NICHT fuehrenden Faktors (Typmodul,
    Rechenschaftskapitel): „zwoelftes/elftes Haus, Schwellenlage". Neu
    2026-09-19 (W35)."""
    fh, zh, stufe = _ordnung(g)
    return '%s/%s Haus, %s' % (_ord(fh, _ORD_NOM), _ord(zh, _ORD_NOM), stufe)


def typ_aus_pfad(pfad):
    """'transit' fuer <klient>_Transit_chart_data.md, sonst None.

    Neu 2026-09-19 (F19): Der Wortlaut fuer einen nicht fuehrenden
    grenzlagigen Faktor haengt vom Typ ab — im Transit gibt es kein
    Rechenschaftskapitel. Erkannt wird am Kuerzel, das der Kern jedem
    Nicht-Standard-Typ direkt nach dem Klientennamen vorschreibt.
    """
    name = os.path.basename(pfad or '')
    return 'transit' if re.search(r'_transit_chart_data', name, re.I) else None


# ---------------------------------------------------------------- Eingabe
def parse_chart(text):
    """-> dict: faktoren [{name,zeichen,haus,nebenhaus,abstand}], achsen, aspekte,
    spiegel [(rohname, kanonisch)]"""
    faktoren, achsen, aspekte, spiegel, hinweise = [], {}, [], [], []
    inblock = False
    for ln in text.split('\n'):
        s = ln.strip()
        if s == '@@SELEKTOR':
            inblock = True
            continue
        if s == '@@ENDE':
            inblock = False
            continue
        if not inblock or not s or s.startswith('#'):
            continue
        parts = s.split()
        kw = parts[0].upper()
        if kw == 'FAKTOR':
            roh = norm(' '.join(p for p in parts[1:] if '=' not in p))
            # ACHSEN-RETTUNG (neu 2026-09-06, Pruefbericht Transit 1.8):
            # Das Schluesselwort ACHSE stand in keinem Modul; das Blockformat
            # des Datenblatt-Moduls zeigt nur FAKTOR- und ASPEKT-Zeilen. Wer
            # `FAKTOR AC zeichen=Stier` schrieb, lief in den harten Abbruch
            # "UNBEKANNTE FAKTOREN". Solche Zeilen werden jetzt als ACHSE
            # gelesen — nicht still, sondern mit sichtbarem Hinweis samt der
            # richtigen Zeile, damit der Block korrigiert wird.
            if norm_token(roh) in ('AC', 'MC', 'DC', 'IC'):
                ax = norm_token(roh); z = None
                for q in parts[2:]:
                    if q.lower().startswith('zeichen='):
                        z = norm(q.split('=', 1)[1])
                achsen[ax] = z
                hinweise.append(
                    'FAKTOR %s ... -> als ACHSE gelesen. Richtig waere: '
                    'ACHSE %s zeichen=%s' % (ax, ax, z or '<Zeichen>'))
                continue
            if roh in SPIEGEL_FAKTOREN:
                # Spiegelpol: wird ueber die Gegen-Zeile als Achse mitgedeutet.
                # Eigene Bloecke wuerden die Achse gespiegelt ziehen (s. o.).
                #
                # SEIT 2026-09-06 (Pruefbericht EA 1.1): Uebersprungen werden nur
                # die BLOECKE. Grenzlage und `fuehrt=ja` gehen NICHT mehr
                # verloren — im EA fuehrt der Suedknoten ein eigenes Kapitel und
                # muss dann in BEIDEN Haeusern gedeutet werden. Vorher fiel er
                # lautlos aus dem ⚠-Grenzlagenblock, obwohl das Datenblatt-Modul
                # die Zwei-Haeuser-Deutung fuer jeden fuehrenden Faktor verlangt.
                sp = {'name': norm_faktor(roh), 'zeichen': None, 'haus': None,
                      'nebenhaus': None, 'abstand': None, 'fuehrt': False,
                      'spiegel_von': SPIEGEL_FAKTOREN[roh]}
                for p in parts[2:]:
                    pl = p.lower()
                    if pl.startswith('zeichen='):
                        sp['zeichen'] = norm(p.split('=', 1)[1])
                    elif pl.startswith('nebenhaus='):
                        sp['nebenhaus'] = p.split('=', 1)[1]
                    elif pl.startswith('haus='):
                        sp['haus'] = p.split('=', 1)[1]
                    elif pl.startswith('abstand='):
                        sp['abstand'] = p.split('=', 1)[1]
                    elif pl.startswith('fuehrt='):
                        sp['fuehrt'] = p.split('=', 1)[1].strip().lower() in (
                            'ja', 'j', 'true', '1')
                spiegel.append((roh, SPIEGEL_FAKTOREN[roh]))
                faktoren.append(sp)
                continue
            name = norm_faktor(roh)
            zeichen = haus = nebenhaus = abstand = None
            fuehrt = False
            for p in parts[2:]:
                pl = p.lower()
                if pl.startswith('zeichen='):
                    zeichen = norm(p.split('=', 1)[1])
                elif pl.startswith('nebenhaus='):
                    nebenhaus = p.split('=', 1)[1]
                elif pl.startswith('haus='):
                    haus = p.split('=', 1)[1]
                elif pl.startswith('abstand='):
                    abstand = p.split('=', 1)[1]
                elif pl.startswith('fuehrt='):
                    fuehrt = p.split('=', 1)[1].strip().lower() in (
                        'ja', 'j', 'true', '1')
            faktoren.append({'name': name, 'zeichen': zeichen, 'haus': haus,
                             'nebenhaus': nebenhaus, 'abstand': abstand,
                             'fuehrt': fuehrt})
        elif kw == 'ACHSE':
            ax = norm_token(parts[1])
            z = None
            for p in parts[2:]:
                if p.lower().startswith('zeichen='):
                    z = norm(p.split('=', 1)[1])
            achsen[ax] = z
        elif kw == 'ASPEKT':
            if len(parts) >= 3:
                aspekte.append((norm_token(parts[1]), norm_token(parts[2])))
    # LEERE ASPEKTEBENE (neu 2026-09-15, Pruefbericht Geburtshoroskop
    # Schritt 3+4). Die ASPEKT-Zeilen sind der einzige Weg, auf dem
    # Aspektbloecke aus der Bibliothek in die referenz.md kommen. Fehlen sie,
    # schreibt Schritt 2 SAEMTLICHE Aspektdeutungen ohne Quelltexte — und
    # nichts faellt auf: Die Pflicht-Vollstaendigkeitspruefung prueft, ob jeder
    # ANGEFORDERTE Block existiert, und bei null Anforderungen ist sie trivial
    # gruen. Im Prueffall vom 15.09. ist genau das passiert; gemerkt hat es
    # erst Schritt 3, zwei Konversationen spaeter.
    if not aspekte and re.search(r'^\|\s*Faktor\s*\|\s*Aspekt\s*\|', text,
                                 re.M):
        hinweise.append(
            'KEINE ASPEKT-ZEILE im @@SELEKTOR-Block, obwohl die chart_data '
            'Aspekttabellen fuehrt. Erwartet wird je gedeutetem Paar eine '
            'Zeile der Form "ASPEKT <A> <B>" (nur die beiden Faktornamen, '
            'ohne Aspektart und ohne Orb).')
    return {'faktoren': faktoren, 'achsen': achsen, 'aspekte': aspekte,
            'spiegel': spiegel, 'unbekannt': [], 'hinweise': hinweise}


# ---------------------------------------------------------------- Bloecke laden
FILE_RE = re.compile(r'^@@FILE=(.+)@@$')


def _parse_blocks(text):
    """block-markierter Text -> dict key->text (Marker entfernt)."""
    blocks, key, buf = {}, None, []
    for ln in text.split('\n'):
        m = MARK_RE.match(ln)
        if m:
            if key is not None:
                blocks[key] = '\n'.join(buf).strip('\n')
            key, buf = m.group(1), []
        else:
            buf.append(ln)
    if key is not None:
        blocks[key] = '\n'.join(buf).strip('\n')
    return blocks


def load_blocks(path):
    return _parse_blocks(open(path, encoding='utf-8').read())


def load_bundle(path):
    """Bündel (@@FILE=name@@-getrennt) -> dict dateiname -> {key->text}."""
    out, cur, buf = {}, None, []
    for ln in open(path, encoding='utf-8').read().split('\n'):
        m = FILE_RE.match(ln)
        if m:
            if cur is not None:
                out[cur] = _parse_blocks('\n'.join(buf))
            cur, buf = m.group(1), []
        else:
            buf.append(ln)
    if cur is not None:
        out[cur] = _parse_blocks('\n'.join(buf))
    return out


# ---------------------------------------------------------------- Ableitung
SPEZSET = ('CHIRON', 'LILITH', 'PHOLUS', 'GLUECKSPUNKT')


def resolve_aspect(a, b):
    """-> (srcfile, key, note) oder (None,None,note) fuer nicht-block-gefuehrt."""
    # Planet–Planet: kanonisch nach Planetenordnung
    if a in PSET and b in PSET:
        x, y = sorted([a, b], key=PLANETS.index)
        return aspekt_file(x), '%s_%s' % (x, y), None
    # Mondknoten mit Planet oder Achse -> reichere Achsendatei
    if 'KNOTEN' in (a, b):
        other = b if a == 'KNOTEN' else a
        if other in PSET or other in ('AC', 'MC'):
            return SPEZFILE['MONDKNOTEN'], 'MONDKNOTEN_' + other, None
        if other in ('DC', 'IC'):
            ax2 = 'AC' if other == 'DC' else 'MC'
            return SPEZFILE['MONDKNOTEN'], 'MONDKNOTEN_' + ax2, 'für %s an der Achse gekippt' % other
        return None, None, 'nicht als Block geführt (%s-%s)' % (a, b)
    # Spezialfaktor (Chiron/Lilith/Pholus/Glückspunkt) mit Planet oder Achse
    for sp in SPEZSET:
        if sp in (a, b):
            other = b if a == sp else a
            if other in PSET or other in ('AC', 'MC'):
                return SPEZFILE[sp], '%s_%s' % (sp, other), None
            if other in ('DC', 'IC'):
                ax2 = 'AC' if other == 'DC' else 'MC'
                return SPEZFILE[sp], '%s_%s' % (sp, ax2), 'für %s gekippt' % other
            return None, None, 'nicht als Block geführt (%s-%s)' % (a, b)
    # Planet mit Achse
    pl = a if a in PSET else (b if b in PSET else None)
    ax = b if a in PSET else a
    if pl and ax in ('AC', 'MC'):
        return aspekt_file(pl), '%s_%s' % (pl, ax), None
    if pl and ax == 'DC':
        return aspekt_file(pl), '%s_AC' % pl, 'für DC an der Horizontachse gekippt gelesen'
    if pl and ax == 'IC':
        return aspekt_file(pl), '%s_MC' % pl, 'für IC am MC gekippt gelesen'
    return None, None, 'nicht als Block geführt (Achse-Achse/außersystemisch)'


def build_requests(chart):
    """-> (requests, protocol, grenzlagen)   request=(gruppe, srcfile, key, note)"""
    req, prot, grenz = [], [], []
    haeuser = set()

    def add(gruppe, src, key, note=None):
        req.append((gruppe, src, key, note))

    # Grundlagen 01 (alle Prinzip-Segmente GRUNDLAGEN_* immer; Wildcard =
    # robust gegen kuenftige Aenderung der Segmentzahl in 01)
    add('Grundlagen', F01, 'GRUNDLAGEN_*')

    fak_by = {f['name']: f for f in chart['faktoren']}
    # Sonnenzeichen-Doppelquelle
    if 'SONNE' in fak_by and fak_by['SONNE']['zeichen']:
        sz = fak_by['SONNE']['zeichen']
        gruppe_sz = ('Sonnenzeichen' if fak_by['SONNE'].get('fuehrt')
                     else 'Sonnenzeichen-Hintergrund')
        add(gruppe_sz, STEM[sz] + '_Sonnenzeichen.txt', 'SONNENZEICHEN_' + sz)

    for f in chart['faktoren']:
        nm, z, h = f['name'], f['zeichen'], f['haus']
        nh, ab = f.get('nebenhaus'), f.get('abstand')
        got = []
        if nh:
            stufe, text = grenz_stufe(ab)
            grenz.append({'faktor': nm, 'haus': h, 'nebenhaus': nh,
                          'abstand': ab, 'stufe': stufe, 'text': text,
                          'fuehrt': bool(f.get('fuehrt')),
                          'spiegel_von': f.get('spiegel_von')})
        if f.get('spiegel_von'):
            # Blockanfragen bewusst NICHT stellen: Die Deutung kommt gespiegelt
            # ueber den Gegenpol. Die Grenzlage oben ist der Teil, der bleibt.
            prot.append('%-14s -> keine eigenen Bloecke (Spiegelpol von %s); '
                        'Grenzlage bleibt im ⚠-Block%s'
                        % (nm, f['spiegel_von'],
                           ', FUEHRT ein Thema' if f.get('fuehrt') else ''))
            continue
        if nm in PSET:
            if z:
                add('Planet-in-Zeichen', ZEICHENFILE[nm], '%s_IN_%s' % (nm, z))
                got.append('%s_IN_%s' % (nm, z))
            if h:
                add('Planet-in-Haus', haus_file(h), '%s_HAUS_%s' % (nm, h))
                got.append('%s_HAUS_%s' % (nm, h))
                haeuser.add(int(h))
            if nh:
                add('Planet-in-Haus', haus_file(nh), '%s_HAUS_%s' % (nm, nh),
                    'Grenzlage aus Haus %s' % h)
                got.append('%s_HAUS_%s [Grenzlage]' % (nm, nh))
                haeuser.add(int(nh))
        elif nm in SPEZFILE:
            src = SPEZFILE[nm]
            # Die vier Methoden-Segmente eines Spezialfaktors (Quellenlage,
            # Umlaufzeiten, Deutungsregeln) sind in JEDEM Lauf identisch und
            # haben keinen Bezug zum konkreten Chart — bei fuenf
            # Spezialfaktoren rund 700 Zeilen. Sie stehen deshalb seit dem
            # 2026-09-06 in einer EIGENEN Gruppe ganz am Ende der referenz.md
            # und sind dort ueberspringbar wie die GRUNDLAGEN_*-Segmente
            # (Werkzeug-Modul, Punkt 2).
            # 2026-09-19 (W59, Frage 16 = Option 1): auch bei `fuehrt=ja`.
            # Vorher wanderte die Methodik eines fuehrenden Faktors in die
            # gelesene Gruppe — 87 bis 135 Zeilen je Faktor, von denen die
            # Laeufe drei bis vier Saetze brauchten. Das chart-spezifische
            # Material (IN_<Zeichen>, HAUS_<n>, Aspekte) steht immer in der
            # gelesenen Gruppe.
            gruppe_meth = 'Spezialfaktor-Methodik'
            for suf in ('ALLG', 'SEC_HAUS', 'SEC_ZEICHEN', 'SEC_ASPEKT'):
                add(gruppe_meth, src, '%s_%s' % (nm, suf))
            if z:
                add('Spezialfaktor', src, '%s_IN_%s' % (nm, z))
                got.append('%s_IN_%s' % (nm, z))
            if h:
                add('Spezialfaktor', src, '%s_HAUS_%s' % (nm, h))
                got.append('%s_HAUS_%s' % (nm, h))
                if nm == 'MONDKNOTEN':
                    haeuser.add(int(h))
            if nh:
                add('Spezialfaktor', src, '%s_HAUS_%s' % (nm, nh),
                    'Grenzlage aus Haus %s' % h)
                got.append('%s_HAUS_%s [Grenzlage]' % (nm, nh))
                if nm == 'MONDKNOTEN':
                    haeuser.add(int(nh))
        else:
            # Weder Planet noch bekannter Spezialfaktor: FRUEHER fiel dieser
            # Faktor lautlos durch (keine Bloecke, keine Fehlstelle). Jetzt
            # harter Fehler — eine geschluckte Deutung faellt sonst erst beim
            # Korrekturlesen des fertigen PDFs auf, wenn ueberhaupt.
            chart.setdefault('unbekannt', []).append(nm)
            prot.append('FAKTOR %-13s -> UNBEKANNT (keine Bloecke gezogen!)' % nm)
            continue
        prot.append('FAKTOR %-13s -> %s' % (nm, ', '.join(got) or '(nur ALLG/SEC)'))

    # Haus-Allgemein je belegtem Haus (Grenzlagen-Nebenhaeuser eingeschlossen)
    for n in sorted(haeuser):
        add('Haus-Allgemein', haus_file(n), 'HAUS_%d_ALLG' % n)

    # Achsen
    ac = chart['achsen']
    if ac.get('AC'):
        add('Achsen', F05, 'ASZENDENT_' + ac['AC'])
        prot.append('ACHSE AC (%s) -> ASZENDENT_%s' % (ac['AC'], ac['AC']))
    if 'MC' in ac:
        add('Achsen', F05, 'MC_IN_ZEICHEN')
        prot.append('ACHSE MC -> MC_IN_ZEICHEN')
    if 'DC' in ac:
        add('Achsen', F05, 'DESZENDENT_TABELLE')
    if 'IC' in ac:
        add('Achsen', F04, 'IC_IN_ZEICHEN')

    # Aspekte
    # 2026-09-19 (W36): Ein angeforderter Aspekt ohne Bibliotheksblock IST
    # eine Fehlstelle. Vorher stand er nur als „nicht als Block gefuehrt" im
    # Protokoll, waehrend Kopf und Schlusszeile „Fehlstellen: 0" bzw. „keine
    # Fehlstelle" meldeten. Jetzt sammelt chart['ohne_block'] sie fuer Kopf,
    # ⚠-Abschnitt und Schlusszeile (kein Abbruch, s. main()).
    ohne = chart['ohne_block'] = []
    for a, b in chart['aspekte']:
        src, key, note = resolve_aspect(a, b)
        if key:
            add('Aspekte', src, key, note)
            prot.append('ASPEKT %s-%s -> %s%s' % (a, b, key, ' [' + note + ']' if note else ''))
        else:
            ohne.append((a, b, note))
            prot.append('ASPEKT %s-%s -> FEHLSTELLE: %s' % (a, b, note))
    return req, prot, grenz


# ---------------------------------------------------------------- Assemblage
# Reihenfolge der Abschnitte in der referenz.md. 'Spezialfaktor-Methodik'
# steht bewusst GANZ HINTEN, direkt vor dem Auswahl-Protokoll: Der Abschnitt
# ist ueberspringbar (s. build_requests), und was uebersprungen werden darf,
# gehoert ans Ende, damit der Schnitt ohne Suchen moeglich ist.
GRUPPEN = ['Planet-in-Zeichen', 'Planet-in-Haus', 'Haus-Allgemein', 'Achsen',
           'Spezialfaktor', 'Sonnenzeichen', 'Aspekte',
           'Sonnenzeichen-Hintergrund', 'Grundlagen', 'Spezialfaktor-Methodik']

# Gruppen, die Schritt 2 ueberspringen DARF (nicht muss). Der Kopf der
# referenz.md weist sie mit Zeilenzahl aus, damit die Ersparnis sichtbar ist.
#
# SEIT 2026-09-06 (Pruefbericht EA 1.9/4.1 und Rubrik 2): Die drei
# ueberspringbaren Gruppen stehen jetzt tatsaechlich am ENDE der GRUPPEN-Liste —
# vorher stand `Grundlagen` an erster Stelle, obwohl Modul und Quellkommentar
# behaupteten, sie stuenden hinten. `Sonnenzeichen-Hintergrund` ist neu: Das
# Sonnenzeichen-Kapitel der Bibliothek (Thema, Motivation, Psychologie,
# Lernaufgabe, Lebensziel, Symbol) ist rund 400 Zeilen Buchtext ueber das ZEICHEN
# und in jedem Lauf mit demselben Sonnenzeichen identisch; die chart-spezifische
# Stellung traegt der getrennte Block SONNE_IN_<Zeichen>. Fuehrt die Sonne ein
# Thema (`fuehrt=ja`), bleibt das Kapitel in der normal zu lesenden Gruppe
# `Sonnenzeichen` — dort traegt es die Deutung tatsaechlich mit.
UEBERSPRINGBAR = ('Sonnenzeichen-Hintergrund', 'Grundlagen',
                  'Spezialfaktor-Methodik')


# Zeichen-Tabellen, aus denen nur die eigene Zeile gebraucht wird.
# key -> (Feld in chart['achsen'], Zeilen-Praefix)
ZEICHENTABELLEN = {
    'MC_IN_ZEICHEN':      ('MC', 'MC in %s'),
    'IC_IN_ZEICHEN':      ('IC', 'IC in %s'),
    'DESZENDENT_TABELLE': ('DC', 'Deszendent %s'),
}


def _zeichen_norm(s):
    """Versalien, Umlaute aufgeloest — fuer den Vergleich Chart gegen Bibliothek."""
    s = (s or '').upper()
    for a, b in (('\u00c4', 'AE'), ('\u00d6', 'OE'), ('\u00dc', 'UE'),
                 ('\u00e4', 'AE'), ('\u00f6', 'OE'), ('\u00fc', 'UE'),
                 ('\u00df', 'SS')):
        s = s.replace(a, b)
    return s


def _zeichenschnitt(text, praefix_muster, zeichen):
    """Kopf des Blocks + die EINE Zeile des eigenen Zeichens.

    Gibt (neuer_text, gespart_zeilen) zurueck. Wird die Zeile nicht gefunden,
    kommt der Text unveraendert zurueck — ein Schnitt, der nicht sicher ist,
    findet nicht statt.
    """
    if not zeichen:
        return text, 0
    ziel = _zeichen_norm(praefix_muster % zeichen)
    zeilen = text.split('\n')
    treffer = [i for i, z in enumerate(zeilen)
               if _zeichen_norm(z.strip()).startswith(ziel)]
    if len(treffer) != 1:
        return text, 0
    # Kopf = alles vor der ERSTEN Zeile, die dem Muster irgendeines Zeichens folgt
    stamm = _zeichen_norm(praefix_muster.split('%s')[0].strip())
    erste = None
    for i, z in enumerate(zeilen):
        if _zeichen_norm(z.strip()).startswith(stamm) and ':' in z:
            erste = i
            break
    if erste is None or erste > treffer[0]:
        return text, 0
    behalten = zeilen[:erste] + [zeilen[treffer[0]]]
    gespart = len(zeilen) - len(behalten)
    if gespart <= 0:
        return text, 0
    return '\n'.join(behalten).rstrip() + '\n', gespart


def select(chart_text, blocks_ref):
    """blocks_ref = Verzeichnis blocks/ ODER Bündeldatei blocks_bundle.txt."""
    chart = parse_chart(chart_text)
    req, prot, grenz = build_requests(chart)
    bundle = None if os.path.isdir(blocks_ref) else load_bundle(blocks_ref)
    cache = {}

    def blocks_of(src):
        if bundle is not None:
            return bundle.get(src, {})
        if src not in cache:
            p = os.path.join(blocks_ref, src)
            cache[src] = load_blocks(p) if os.path.exists(p) else {}
        return cache[src]

    missing, seen, ordered = [], set(), []
    for gruppe, src, key, note in req:
        bl = blocks_of(src)
        if key.endswith('*'):                       # Wildcard-Praefix
            matched = sorted(k for k in bl if k.startswith(key[:-1]))
            if not matched:
                missing.append((src, key))
            for k in matched:
                if (src, k) not in seen:
                    seen.add((src, k))
                    ordered.append((gruppe, src, k, note, bl[k]))
            continue
        if key not in bl:
            missing.append((src, key))
            continue
        if (src, key) not in seen:
            seen.add((src, key))
            _txt = bl[key]
            if key in ZEICHENTABELLEN:
                _feld, _muster = ZEICHENTABELLEN[key]
                _txt, _gespart = _zeichenschnitt(
                    _txt, _muster, chart['achsen'].get(_feld))
                if _gespart:
                    prot.append('ZEICHENSCHNITT %s (%s) -> %d Zeilen gespart'
                                % (key, chart['achsen'].get(_feld), _gespart))
                else:
                    prot.append('ZEICHENSCHNITT %s -> nicht geschnitten '
                                '(Zeile nicht eindeutig), ganzer Block' % key)
            ordered.append((gruppe, src, key, note, _txt))
    return chart, req, prot, ordered, missing, grenz


# 2026-09-19 (F19): Was mit einem NICHT fuehrenden grenzlagigen Faktor
# geschieht, haengt vom Typ ab. Im Transit gibt es kein Rechenschaftskapitel —
# das Register „Mitlaufendes" fuehrt Kontakte, nicht Faktoren (T12-18c Nr. 10);
# die Anweisung „Zeile im Rechenschaftskapitel" lief dort ins Leere.
# Schluessel: typ_aus_pfad(); None = Geburtshoroskop, EA, Ultimativ.
# Je Typ: (Marke der Faktorzeile, Absatz im Kopf des ⚠-Blocks, Etikett der
# fertigen Hausangabe).
NICHT_FUEHREND = {
    None: (
        ' [fuehrt kein Thema — Zeile im Rechenschaftskapitel, beide Haeuser, '
        'keine Ausdeutung]',
        '  - Er fuehrt KEINES -> seine Zeile im Rechenschaftskapitel traegt '
        'beide Haeuser\n'
        '    mit der Stufe (fertige Hausangabe je Faktor unten). Ausgedeutet '
        'wird dort nichts.\n',
        'Registerzeile, Hausangabe (1:1)'),
    'transit': (
        ' [fuehrt kein Thema — im Transit keine eigene Zeile (kein '
        'Rechenschaftskapitel; das Register „Mitlaufendes" fuehrt Kontakte, '
        'nicht Faktoren). Wo der Punkt genannt wird: beide Haeuser mit der '
        'Stufe, keine Ausdeutung]',
        '  - Er fuehrt KEINES -> im Transit gibt es kein Rechenschaftskapitel; '
        'das Register\n'
        '    „Mitlaufendes" fuehrt Kontakte, nicht Faktoren. Wo der Punkt '
        'genannt wird\n'
        '    (Registerzeile eines Kontakts, Signatur, Beleg), stehen beide '
        'Haeuser mit der\n'
        '    Stufe (fertige Hausangabe je Faktor unten). Ausgedeutet wird '
        'nichts.\n',
        'Hausangabe, wo der Punkt genannt wird (1:1)'),
}


def assemble_md(chart, ordered, prot, missing, grenz=None, typ=None):
    """typ: None (Geburtshoroskop, EA, Ultimativ) oder 'transit' — s.
    typ_aus_pfad() und NICHT_FUEHREND (neu 2026-09-19, F19)."""
    marke_nf, kopf_nf, etikett_nf = NICHT_FUEHREND.get(typ, NICHT_FUEHREND[None])
    ohne = chart.get('ohne_block', [])
    out = ['# Referenzschnitt (Schritt 2) — nur chart-relevante Bloecke', '']
    # 2026-09-19 (W36): Fehlstellen zaehlen auch die angeforderten Aspekte ohne
    # Bibliotheksblock — vorher stand hier 0, waehrend das Protokoll „nicht als
    # Block gefuehrt" meldete.
    out.append('> Maschinell aus blocks/ gezogen. Bloecke: %d. '
               'Fehlstellen: %d.' % (len(ordered), len(missing) + len(ohne))
               + (' Davon %d angeforderte(r) Aspekt(e) ohne Bibliotheksblock '
                  '— s. ⚠ FEHLSTELLEN.' % len(ohne) if ohne else ''))
    # Ueberspringbare Abschnitte mit ihrem Umfang ausweisen. Ohne diese Zeile
    # ist beim Lesen nicht zu sehen, was der Schnitt kostet — und was er
    # sparen wuerde. Zahlen aus dem tatsaechlich gezogenen Schnitt, nicht
    # geschaetzt.
    _z = {}
    for gruppe, _s, _k, _n, text in ordered:
        _z[gruppe] = _z.get(gruppe, 0) + len(text.split('\n')) + 2
    _skip = [(g, _z[g]) for g in UEBERSPRINGBAR if _z.get(g)]
    if _skip:
        out.append('>')
        out.append('> UEBERSPRINGBAR (s. Werkzeug-Modul, Punkt 2): %s. '
                   'Zusammen rund %d Zeilen.'
                   % (' · '.join('%s ~%d Zeilen' % (g, n) for g, n in _skip),
                      sum(n for _, n in _skip)))
        out.append('> Sie tragen Methoden-, Zeichen- und Grundlagenwissen, das '
                   'in jedem Lauf identisch ist und')
        out.append('> keinen Bezug zum konkreten Chart hat. Chart-spezifische '
                   'Bloecke (Zeichen, Haus,')
        out.append('> Aspekt, Spezialfaktor-Staende) werden IMMER voll '
                   'gelesen.')
        if _z.get('Spezialfaktor-Methodik'):
            # 2026-09-19 (W59, Frage 16 = Option 1)
            out.append('> Die Methoden-Vorreden der Spezialfaktoren sind auch '
                       'bei `fuehrt=ja` ueberspringbar: das chart-')
            out.append('> spezifische Material eines fuehrenden Spezialfaktors '
                       'steht unter "Spezialfaktor" und "Aspekte".')
    out.append('')
    if ohne:
        # 2026-09-19 (W36): eindeutige Meldung samt Anweisung — vorher stand
        # nirgends, was mit einer solchen Fehlstelle geschieht (G12-18 Nr. 10).
        out.append('\n' + '=' * 70)
        out.append('## ⚠ FEHLSTELLEN — angeforderte Aspekte ohne '
                   'Bibliotheksblock')
        out.append('=' * 70)
        out.append(
            'Fuer diese ASPEKT-Zeilen fuehrt die Bibliothek keinen Block '
            '(Spezialfaktor mit\nSpezialfaktor, Achse mit Achse oder '
            'ausserhalb des Systems). Jede ist eine Fehlstelle,\nkein '
            'Abbruch: aus den Nachbarbloecken deuten — die Staende beider '
            'Faktoren und,\nbei einem Spezialfaktor, seine Aspekt-Vorrede '
            '(<FAKTOR>_SEC_ASPEKT unter\n"Spezialfaktor-Methodik"; fuer diese '
            'Deutung dort nachlesen) — und in der\nReferenzdatei-Liste '
            'melden.\n')
        for a, b, note in ohne:
            out.append('- ASPEKT %s-%s — %s' % (a, b, note))
        out.append('')
    if grenz:
        out.append('\n' + '=' * 70)
        out.append('## ⚠ GRENZLAGEN — Pflichtanweisung fuer die Deutung')
        out.append('=' * 70)
        out.append(
            'Diese Faktoren stehen 5° oder weniger VOR einer Hausspitze. Was '
            'daraus folgt,\nhaengt seit dem Kern-Umbau vom 2026-09-04 davon ab, '
            'ob der Faktor ein Thema FUEHRT:\n'
            '\n'
            '  - Er FUEHRT ein Thema  -> er wird in BEIDEN Haeusern gedeutet, in '
            'der unten\n'
            '    genannten Rangfolge. Die Hausdeutung des Nebenhauses darf dann '
            'nicht\n'
            '    wegfallen; sie faellt sonst bei der Deckungsprobe (a) auf wie '
            'eine fehlende\n'
            '    Zeichenebene.\n'
            + kopf_nf +   # 2026-09-19 (F19): typabhaengig, s. NICHT_FUEHREND
            '\n'
            'Bis zum 2026-09-06 stand hier pauschal „werden in BEIDEN Haeusern '
            'gedeutet" —\ndas war gegenueber dem Kern veraltet und wies bei '
            'jedem Lauf eine Pflicht an,\ndie fuer nicht fuehrende Faktoren '
            'nicht gilt.\n'
            '\n'
            'Beide Hausbloecke stehen unten unter "Planet-in-Haus" bzw. '
            '"Spezialfaktor". Je\nFaktor stehen fertige Zeilen dabei (seit '
            '2026-09-19 in Worten, mit echten Umlauten):\ndie Signatur-Wortform '
            'wird 1:1 in den Kapitelkopf uebernommen, im Fachmodus\ndie '
            'Notation daneben. Die Gradzahl steht NUR in der Beleg-Angabe; im '
            'Fliesstext\nerscheint KEINE Gradzahl. Die Hausnummer darf '
            'dort stehen\n(Klartext-Modul, Anker-Regel: "DARF stehen — beim '
            'ersten Mal mit dem\nLebensbereich dahinter"). Bis zum 2026-09-06 '
            'stand hier "weder Hausnummer\nnoch Gradzahl" — das widersprach '
            'dem Klartext-Modul (Pruefbericht Transit 1.7).\n')
        for g in grenz:
            marke = (' [FUEHRT ein Thema — beide Haeuser deuten]'
                     if g.get('fuehrt') else marke_nf)
            out.append('- **%s**: Haus %s → Haus %s. %s.%s'
                       % (g['faktor'].capitalize(), g['haus'], g['nebenhaus'],
                          g['text'], marke))
            # 2026-09-19 (W35): Wortform statt Notation mit Grad; die Gradzahl
            # nur noch in der Beleg-Angabe.
            out.append('  Signatur (Klartext, 1:1): `%s`' % signatur_notation(g))
            out.append('  Fachmodus: `%s` · Beleg (einzige Stelle mit '
                       'Gradzahl): `%s`'
                       % (fachmodus_notation(g), beleg_notation(g)))
            if not g.get('fuehrt'):
                out.append('  %s: `%s`' % (etikett_nf, register_notation(g)))
            if g.get('spiegel_von'):
                out.append('  ACHTUNG Spiegelpol: Deutungstext kommt gespiegelt '
                           'ueber %s (eigene Bloecke wuerden die Achse '
                           'verkehrt herum ziehen). Die Haus- und '
                           'Zeichenangabe oben gilt trotzdem und ist bei einem '
                           'fuehrenden Faktor auszudeuten.'
                           % g['spiegel_von'].capitalize())
        out.append('')
    for g in GRUPPEN:
        items = [o for o in ordered if o[0] == g]
        if not items:
            continue
        out.append('\n' + '=' * 70)
        out.append('## %s' % g)
        out.append('=' * 70)
        for gruppe, src, key, note, text in items:
            hdr = '### [%s]  Quelle: %s' % (key, src)
            if note:
                hdr += '   — %s' % note
            out.append('\n' + hdr)
            out.append(text)
    out.append('\n' + '=' * 70)
    out.append('## Auswahl-Protokoll (Faktor/Aspekt -> Block)')
    out.append('=' * 70)
    out.extend(prot)
    return '\n'.join(out) + '\n'


def referenzliste(chart_text, blocks_ref=None):
    """Nur-Liste-Modus (neu 2026-09-19, W40): was das Chart aus der Bibliothek
    braucht — ohne Bibliothek und ohne referenz.md.

    Fuer die Referenzdatei-Liste am Ende von Schritt 1. Liest nur den
    @@SELEKTOR-Block und leitet die Anfragen ab wie der volle Lauf
    (build_requests); die Bibliothek ist optional und dient nur der Probe, ob
    jeder Block da ist.

    -> dict: dateien {Bibliotheksdatei: [Blockschluessel, ...]} (Wildcards wie
       'GRUNDLAGEN_*' als ein Eintrag), fehlstellen [(A, B, Grund)] (angeforderte
       Aspekte ohne Block), fehlt [(Datei, Schluessel)] (nur mit blocks_ref,
       sonst None), chart (das geparste Datenblatt mit 'hinweise' und
       'unbekannt').
    """
    chart = parse_chart(chart_text)
    req, _prot, _grenz = build_requests(chart)
    dateien = {}
    for _gruppe, src, key, _note in req:
        keys = dateien.setdefault(src, [])
        if key not in keys:
            keys.append(key)
    fehlt = None
    if blocks_ref is not None:
        fehlt = select(chart_text, blocks_ref)[4]
    return {'dateien': dateien, 'fehlstellen': list(chart.get('ohne_block', [])),
            'fehlt': fehlt, 'chart': chart}


AUFRUF = (
    'Aufruf:\n'
    '  python3 selektor.py <klient>[_KUERZEL]_chart_data.md blocks_bundle.txt '
    '<klient>[_KUERZEL]_referenz.md\n'
    '      Referenzschnitt (Schritt 2): schreibt die referenz.md. Alle drei '
    'Argumente angeben.\n'
    '  python3 selektor.py <klient>[_KUERZEL]_chart_data.md --liste '
    '[blocks_bundle.txt]\n'
    '      Nur-Liste-Modus (Ende Schritt 1): welche Bibliotheksdateien das '
    'Chart braucht und\n'
    '      welche angeforderten Aspekte keinen Block haben; schreibt nichts. '
    'Mit der Bibliothek\n'
    '      prueft er zusaetzlich, ob jeder Block da ist.\n'
    '  python3 selektor.py --selbsttest\n'
    '      Selbsttest ohne Bibliothek (konstruierte Werte).')


def _pruefe_hart(chart):
    """Harte Abbrueche, die fuer beide Modi gelten (leere Aspektebene,
    unbekannter Faktor). Aus main() herausgezogen am 2026-09-19 (W40), damit der
    Nur-Liste-Modus dieselben Proben faehrt; Wortlaut unveraendert."""
    leer = [h for h in chart.get('hinweise', [])
            if h.startswith('KEINE ASPEKT-ZEILE')]
    if leer:
        print('LEERE ASPEKTEBENE (harter Fehler — frueher lief das lautlos '
              'durch):')
        print('   Der @@SELEKTOR-Block traegt keine einzige ASPEKT-Zeile, die '
              'chart_data aber Aspekttabellen.')
        print('   Ohne sie zieht dieser Lauf KEINEN Aspektblock aus der '
              'Bibliothek; Schritt 2 schriebe alle')
        print('   Aspektdeutungen ohne Quelltexte. Je gedeutetem Paar eine '
              'Zeile ergaenzen:')
        print('       ASPEKT SONNE MOND')
        print('       ASPEKT MARS AC')
        print('   Nur die beiden Faktornamen — keine Aspektart, kein Orb.')
        sys.exit(1)
    unbek = chart.get('unbekannt', [])
    if unbek:
        print('UNBEKANNTE FAKTOREN (harter Fehler — frueher fielen sie lautlos durch):')
        for nm in unbek:
            print('   UNBEKANNT %s — weder Planet noch Spezialfaktor.' % nm)
        print('   Erlaubt sind: %s' % ', '.join(PLANETS))
        print('   sowie:        %s' % ', '.join(sorted(SPEZFILE)))
        print('   Aliasse:      %s' % ', '.join(
            '%s->%s' % (k, v) for k, v in sorted(FAKTOR_ALIAS.items())))
        print('   Spiegelpole (bewusst uebersprungen): %s'
              % ', '.join(sorted(SPIEGEL_FAKTOREN)))
        sys.exit(1)


def _melde_ohne_block(ohne):
    """Angeforderte Aspekte ohne Bibliotheksblock melden (2026-09-19, W36)."""
    print('FEHLSTELLEN OHNE BIBLIOTHEKSBLOCK (kein Abbruch): %d angeforderte(r) '
          'Aspekt(e)' % len(ohne))
    for a, b, note in ohne:
        print('   FEHLSTELLE ASPEKT %s-%s — %s' % (a, b, note))
    print('   Aus den Nachbarbloecken deuten (Staende beider Faktoren, bei einem '
          'Spezialfaktor seine')
    print('   Aspekt-Vorrede <FAKTOR>_SEC_ASPEKT) und in der Referenzdatei-Liste '
          'melden.')


def _main_liste(chart_path, blocks_ref=None):
    """Nur-Liste-Modus auf der Kommandozeile (2026-09-19, W40)."""
    text = open(chart_path, encoding='utf-8').read()
    r = referenzliste(text, blocks_ref)
    chart = r['chart']
    for h in chart.get('hinweise', []):
        print('   HINWEIS %s' % h)
    _pruefe_hart(chart)
    print('Referenzdateien, die dieses Chart braucht (Nur-Liste-Modus — '
          'schreibt keine referenz.md):')
    for src in sorted(r['dateien']):
        n = len(r['dateien'][src])
        print('   %s — %d %s' % (src, n, 'Block' if n == 1 else 'Bloecke'))
    print('   Zusammen: %d Dateien, %d Bloecke (Wildcards als ein Eintrag).'
          % (len(r['dateien']), sum(len(k) for k in r['dateien'].values())))
    if r['fehlstellen']:
        _melde_ohne_block(r['fehlstellen'])
    else:
        print('Fehlstellen ohne Bibliotheksblock: keine.')
    if r['fehlt'] is None:
        print('Bibliothek nicht geprueft (kein zweites Argument): ob jeder Block '
              'da ist, zeigt erst der volle Lauf.')
    elif r['fehlt']:
        print('FEHLSTELLEN (harter Fehler):')
        for src, key in r['fehlt']:
            print('   FEHLT %s in %s' % (key, src))
        sys.exit(1)
    else:
        print('Bibliothek geprueft: jeder angeforderte Block ist da.')


def _selbsttest():
    """Selbsttest ohne Bibliothek (neu 2026-09-19): W35, W36, W59, F19, W40.
    Konstruierte Staende — kein echter Mensch, keine echten Daten."""
    blk = '\n'.join([
        '@@SELEKTOR',
        'FAKTOR SONNE zeichen=Widder haus=1 fuehrt=ja',
        'FAKTOR MOND zeichen=Stier haus=11 nebenhaus=12 abstand=1.50 fuehrt=ja',
        'FAKTOR SATURN zeichen=Jungfrau haus=6 nebenhaus=7 abstand=3.25',
        'FAKTOR CHIRON zeichen=Stier haus=2 fuehrt=ja',
        'FAKTOR SUEDKNOTEN zeichen=Widder haus=4 nebenhaus=5 abstand=4.00',
        'ACHSE AC zeichen=Widder',
        'ASPEKT SONNE MOND',
        'ASPEKT CHIRON LILITH',
        'ASPEKT AC MC',
        '@@ENDE'])
    chart = parse_chart(blk)
    req, prot, grenz = build_requests(chart)
    g = dict((x['faktor'], x) for x in grenz)
    # W35: Wortform, echte Umlaute, keine Gradzahl; fuehrendes Haus vorn
    assert signatur_notation(g['MOND']) == \
        'Mond im zwölften Haus, dicht an der Schwelle aus dem elften'
    assert signatur_notation(g['SATURN']) == \
        'Saturn im sechsten Haus, nahe an der Schwelle zum siebten'
    assert signatur_notation(g['SUEDKNOTEN']) == \
        'Südknoten im vierten Haus, nahe an der Schwelle zum fünften'
    assert fachmodus_notation(g['MOND']) == 'Haus 12/11, Schwellenlage'
    assert beleg_notation(g['MOND']) == \
        '12./11. Haus (Schwellenlage, 1°30′ vor Spitze 12)'
    assert register_notation(g['SATURN']) == 'sechstes/siebtes Haus, Grenzlage'
    for x in grenz:
        for zeile in (signatur_notation(x), fachmodus_notation(x),
                      register_notation(x)):
            assert '°' not in zeile, zeile
            for ascii_umlaut in ('fuehr', 'Sued', 'zwoelf', 'fuenf', 'Glueck'):
                assert ascii_umlaut not in zeile, zeile
    # W59: Methodik eines fuehrenden Spezialfaktors bleibt ueberspringbar
    gruppe = dict((k, gr) for gr, _src, k, _n in req)
    assert gruppe['CHIRON_ALLG'] == 'Spezialfaktor-Methodik'
    assert gruppe['CHIRON_IN_STIER'] == 'Spezialfaktor'
    # W36: angeforderter Aspekt ohne Block = Fehlstelle, eindeutig gemeldet
    assert [(a, b) for a, b, _n in chart['ohne_block']] == \
        [('CHIRON', 'LILITH'), ('AC', 'MC')]
    assert sum('-> FEHLSTELLE:' in p for p in prot) == 2
    md = assemble_md(chart, [], prot, [], grenz)
    assert 'Fehlstellen: 2.' in md and '## ⚠ FEHLSTELLEN' in md
    assert 'Fehlstellen: 0' not in md
    # F19: Wortlaut fuer den nicht fuehrenden Faktor je Typ
    md_t = assemble_md(chart, [], prot, [], grenz, typ='transit')
    assert 'Zeile im Rechenschaftskapitel' in md and 'Mitlaufendes' not in md
    assert 'Mitlaufendes' in md_t and 'Zeile im Rechenschaftskapitel' not in md_t
    assert typ_aus_pfad('/x/muster_Transit_chart_data.md') == 'transit'
    assert typ_aus_pfad('muster_chart_data.md') is None
    assert typ_aus_pfad('muster_EA_chart_data.md') is None
    # W40: Nur-Liste-Modus ohne Bibliothek
    r = referenzliste(blk)
    assert r['fehlt'] is None and 'Sonne_Aspekte.txt' in r['dateien']
    assert 'SONNE_MOND' in r['dateien']['Sonne_Aspekte.txt']
    assert len(r['fehlstellen']) == 2
    print('[selektor-Selbsttest bestanden: Grenzlagen-Wortform (W35), '
          'Fehlstellen (W36), Methodik (W59), Typ-Wortlaut (F19), '
          'Nur-Liste-Modus (W40)]')


def main():
    # 2026-09-19 (W40): Optionen erkennen statt jedes Argument als Pfad zu
    # lesen — `--liste` ist neu, und ein Tippfehler (`--list`) oder `--help`
    # lief vorher als Dateipfad in einen FileNotFoundError.
    args = sys.argv[1:]
    optionen = [a for a in args if a.startswith('-')]
    pos = [a for a in args if not a.startswith('-')]
    unbek = [o for o in optionen if o not in ('--liste', '--hilfe', '--help',
                                              '-h', '--selbsttest')]
    will_hilfe = any(o in ('--hilfe', '--help', '-h') for o in optionen)
    if '--selbsttest' in optionen and not unbek:
        _selbsttest()
        return
    if '--hilfe' in optionen and not unbek:
        # `--hilfe [<name>]`: Aufrufzeilen UND Schnittstellen (D3, 2026-09-20);
        # `--help`/`-h` zeigen wie bisher nur die Aufrufzeilen.
        print(AUFRUF)
        _hilfe_cli()
        sys.exit(0)
    if unbek or will_hilfe or not pos:
        if unbek:
            print('Unbekannte Option: %s' % ', '.join(unbek))
        elif not pos and not will_hilfe:
            print('Kein Datenblatt angegeben.')
        print(AUFRUF)
        sys.exit(0 if (will_hilfe and not unbek) else 2)
    chart_path = pos[0]
    if '--liste' in optionen:
        _main_liste(chart_path, pos[1] if len(pos) > 1 else None)
        return
    blocks_dir = pos[1] if len(pos) > 1 else 'blocks'
    out_path = pos[2] if len(pos) > 2 else \
        os.path.basename(chart_path).replace('chart_data', 'referenz')
    typ = typ_aus_pfad(chart_path)
    text = open(chart_path, encoding='utf-8').read()
    chart, req, prot, ordered, missing, grenz = select(text, blocks_dir)
    print('Faktoren :', len(chart['faktoren']),
          '| Aspekte:', len(chart['aspekte']),
          '| Bloecke gezogen:', len(ordered),
          '| Grenzlagen:', len(grenz))
    if typ == 'transit':
        print('   TYP Transit (Dateiname) — Grenzlagen-Wortlaut ohne '
              'Rechenschaftskapitel')
    for g in grenz:
        print('   GRENZLAGE %-12s Haus %s -> %s  (%s)'
              % (g['faktor'], g['haus'], g['nebenhaus'], g['stufe']))
    for h in chart.get('hinweise', []):
        print('   HINWEIS %s' % h)
    for roh, ziel in chart.get('spiegel', []):
        print('   SPIEGELPOL %-12s -> uebersprungen, wird ueber %s als Achse '
              'mitgedeutet' % (roh, ziel))
    _pruefe_hart(chart)
    if missing:
        print('FEHLSTELLEN (harter Fehler):')
        for src, key in missing:
            print('   FEHLT %s in %s' % (key, src))
        sys.exit(1)
    open(out_path, 'w', encoding='utf-8').write(
        assemble_md(chart, ordered, prot, missing, grenz, typ=typ))
    # 2026-09-19 (W36): Die Schlusszeile zaehlt die Fehlstellen ohne
    # Bibliotheksblock mit — nie mehr „keine Fehlstelle" neben „nicht als Block
    # gefuehrt".
    ohne = chart.get('ohne_block', [])
    if ohne:
        _melde_ohne_block(ohne)
        print('Geschrieben:', out_path, '— %d Fehlstelle(n) ohne '
              'Bibliotheksblock, s. oben und ⚠ FEHLSTELLEN in der referenz.md'
              % len(ohne))
    else:
        print('OK — geschrieben:', out_path, '(keine Fehlstelle)')


# ---------------------------------------------------------------------------
# hilfe() — Schnittstellen-Auskunft ohne Quelltext-Lektuere.
# Neu 2026-09-20 (Aufraeumlauf D, Block D3; K5/W61: Schnittstellen wurden je Lauf
# aus dem Quelltext nachgelesen, 50-110 KB je Lauf). Derselbe Block steht
# wortgleich in jedem Builder. Er liest Signaturen und Docstrings zur LAUFZEIT —
# er kann also nicht veralten. Was hilfe() nicht sagt, fehlt im Docstring der
# Funktion und wird DORT ergaenzt, nie hier.
# ---------------------------------------------------------------------------

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


if __name__ == '__main__':
    main()
