#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""beziehung.py — Rechnung, Datenblatt der Beziehung, Referenzschnitt, Doppelrad,
Seiten und Proben des Beziehungshoroskops (Erweiterung Beziehung, neu 2026-10-11).
Drei Arten (ARTEN): Paar, Eltern-Kind und seit 2026-10-14 Freundschaft — deren
Dokument heisst „Freundschaftshoroskop“ (DOKUMENTTYP, dateiname()).

Grundlage sind IMMER die Datenblaetter beider Personen aus der Pipeline — ihre
`factors`-Bloecke (ekliptikale Laengen samt Achsen) und Hausspitzen. Nichts wird
aus Staendetabellen gelesen und nichts aus Geburtsdaten neu gerechnet. Einzige
Ausnahme ist die Zeitprobe: Sie rechnet die Hausspitzen und Achsen EINER Person
fuer wenige Minuten frueher oder spaeter neu (pyswisseph, jd/lat/lon aus dem
Datenblatt), um zu zeigen, was innerhalb der Zeitunsicherheit kippt.

Was gerechnet wird (Startprompt `claude/STARTPROMPT_Beziehungshoroskop_einbauen_
2026-10-11.md`, Bau 1; Chris-Entscheidung 2026-10-11 zum Orbis):
  * Aspekte zwischen beiden Bildern mit Einzelseiten-Pruefung wie im Geburtsbild
    (radix.ASPEKT_ORB, voll / einseitig / Nebenaspekt, der Mondknoten erbt den
    Orbis des Partners). „eng" heisst: innerhalb des halben VOLLEN Orbis
    (ENG_ANTEIL * kleinerer Orbis, beim Nebenaspekt * fester Orbis). Die
    Tabelle zeigt alle, die Deutung stuetzt sich auf die engen.
  * Achsen-Spiegel: Trifft ein Faktor beide Enden einer Achse des anderen in
    derselben Stufe (Konjunktion/Opposition, Quadrat/Quadrat), ist das EINE
    Zeile — Fuehrung wie radix.aspektliste(): Konjunktion vor Opposition,
    AC vor DC, MC vor IC. Die Achsen beider zueinander stehen in einer eigenen
    Tabelle (nur AC und MC der bestellenden Person, die Gegenenden sind Spiegel).
  * Hausueberlagerung in beide Richtungen: jeder Faktor des einen in den
    Haeusern des anderen, mit Grenzlage (5°), Schwellenlage (2°, das Nebenhaus
    fuehrt) und offener Fuehrung — dieselben Stufen wie im Datenblatt-Modul
    (radix.haus_und_grenzlage, radix.fuehrendes_haus, radix.haus_spalte).
  * Rangzeilen in der Grammatik von radix.rangzeilen_lesen(): engste
    Verbindungen, enge und alle Verbindungen je Faktor, Ueberlagerung je Haus,
    Elemente und Modi beider nach derselben Zaehlung (radix.GEWICHT gewichtet,
    zehn Planeten gezaehlt) — jede mit ihrer Zaehlmenge.
  * Zeitprobe: welche Achsen-Aspekte, Achsenkontakte und Ueberlagerungen
    innerhalb von ±ZEIT_MINUTEN einer der beiden Geburtszeiten kippen; offene
    Fuehrung unter OFFEN_MINUTEN wie im Geburtsbild.
  * Fassungsabgleich: Geburtszeit und Fassung aus dem Kopf beider Datenblaetter
    stehen im Datenblatt der Beziehung; nennt der Auftrag eine andere Zeit, ist
    das ein ⚠ zum Anhalten.

Schnittstelle (Einzelheiten: hilfe('<name>')):
    lies_datenblatt(pfad) -> dict
    legende_beziehung(chartdoc) -> tuple            Quincunx-Zeile der Legende (Regel 5)
    kreuzaspekte(fa, fb) / achsenkontakte(fa, fb) / ueberlagerung(fx, cusps_y)
    zeitprobe(pa, pb) -> dict
    rechnung(a_pfad, b_pfad, art, ...) -> dict      alles Gerechnete
    datenblatt(a_pfad, b_pfad, ziel, art, ...) -> dict   baut die Datei
    lies_beziehung(pfad) -> dict                   liest sie wieder (Schritt 2)
    heimat_bericht(pfad) -> str                    eine Ergebniszeile
    referenzschnitt(pfad, bundle, ziel) -> dict    Bibliothek ohne Netzquellen
    doppelrad(pfad_oder_r, out_path, ...) -> str   PNG
    staende_page / kreuz_page (r, ...) -> str      HTML im Hausstil
    belege_en(analyse_pfad, namen) -> dict         englische Belege (Sprachfassung)
    probe(analyse_pfad, datenblatt_pfad) -> str    die Beziehung-Probe (Pruefmuster:
                                                   hilfe('probe'))
    dateiname(art, a, b, datum, teil, ...) -> str  Dateinamen samt PDF je Art und Sprache
    python3 beziehung.py --selbsttest | --hilfe [<name>]

Personen: A ist immer die bestellende Person (Anrede „du“; beim Paar und bei
Freundschaft „ihr“ fuer beide), B die zweite. Im Datenblatt, in Rangzeilen und Belegen steht ein Faktor
mit seiner Person: „Venus (<Vorname>)“, in Rangzeilen ohne Leerzeichen
„Venus(<Vorname>)“.

Datenschutz: Diese Datei traegt keine Namen, Geburtsdaten oder Geburtszeiten
realer oder erfundener Personen; der Selbsttest arbeitet mit konstruierten
Staenden und Platzhalternamen.
"""

import ast
import datetime
import hashlib
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import radix  # noqa: E402

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

ENG_ANTEIL = 0.5          # eng = innerhalb des halben vollen Orbis (Chris, 2026-10-11)
ZEIT_MINUTEN = radix.KIPP_SCHWELLE    # Zeitprobe: ± so viele Minuten (2)
OFFEN_MINUTEN = radix.FUEHRUNG_OFFEN  # offene Fuehrung unter so vielen Minuten (1)
ZEIT_SCHRITT = 0.05       # Minuten; Rasterweite, danach Bisektion
RANG_ENGSTE = 10
RANG_ENGSTE_PLANETEN = 5
ERWACHSEN = 18            # Paar und Freundschaft nur mit zwei Erwachsenen; Kinder-Regeln unter 18
# 2026-10-14c (Wartungslauf „Art Freundschaft“; Chris-Entscheidungen 14.10.: nur
# Erwachsene, Vorrang 11. und 3. Haus, eigener Name „Freundschaftshoroskop“, englisch
# gleich mit): Freundschaft liest sich wie das Paar — beide lesen („ihr“), beide gleich
# gewichtet, nur Erwachsene — und wie Eltern-Kind ohne romantische oder sexuelle
# Lesart (Referenzschnitt gefiltert, Romantik-Probe B11).
ARTEN = ('paar', 'eltern-kind', 'freundschaft')
ART_TITEL = {'paar': 'Paar', 'eltern-kind': 'Eltern-Kind', 'freundschaft': 'Freundschaft'}
IHR_ARTEN = ('paar', 'freundschaft')            # beide lesen: „ihr“, B9, B12, nur Erwachsene
OHNE_ROMANTIK = ('eltern-kind', 'freundschaft')  # Filter im Referenzschnitt, Romantik-Probe B11
DOKUMENTTYP = {'paar': 'Beziehungshoroskop', 'eltern-kind': 'Beziehungshoroskop',
               'freundschaft': 'Freundschaftshoroskop'}
DOKUMENTTYP_EN = {'paar': 'Relationship Horoscope', 'eltern-kind': 'Relationship Horoscope',
                  'freundschaft': 'Friendship Horoscope'}
KUERZEL = {'paar': 'Beziehung', 'eltern-kind': 'Beziehung', 'freundschaft': 'Freundschaft'}

PLANETEN = ('Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'Jupiter', 'Saturn',
            'Uranus', 'Neptun', 'Pluto')
PUNKTE = ('Mondknoten', 'Chiron', 'Lilith', 'Pholus')
ACHSEN = ('AC', 'MC', 'DC', 'IC')
FAKTOR_REIHE = PLANETEN + PUNKTE + ACHSEN
UEBERLAGERUNG_FAKTOREN = PLANETEN + PUNKTE + ('AC', 'MC')
KERN = ('Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'AC', 'MC')
HARMONISCH = ('Konjunktion', 'Trigon', 'Sextil')
GEGENACHSE = {'AC': 'DC', 'DC': 'AC', 'MC': 'IC', 'IC': 'MC'}
STUFE_RANG = {'voll': 0, 'einseitig': 1, 'neben': 2}
STUFE_TITEL = {'voll': 'Volle Aspekte', 'einseitig': 'Einseitige Aspekte',
               'neben': 'Nebenaspekte'}

ASPEKT_GLYPHE = {'Konjunktion': '☌', 'Opposition': '☍', 'Quadrat': '□',
                 'Trigon': '△', 'Sextil': '⚹', 'Quincunx': '⚻',
                 'Halbsextil': '⚺'}
GLYPHE_ASPEKT = {v: k for k, v in ASPEKT_GLYPHE.items()}
FAKTOR_GLYPHE = dict(radix.FAKTOR_GLYPHE)
ZEICHEN = list(radix.SIGN_NAMES)
ZEICHEN_GLYPHE = dict(zip(radix.SIGN_NAMES, radix.SIGN_GLYPHS))
ACHSEN_LANG = {'AC': 'Aszendent (AC)', 'MC': 'Medium Coeli (MC)',
               'DC': 'Deszendent (DC)', 'IC': 'Imum Coeli (IC)'}

# Die Bewegungsfolge (verbindliche ###-Wortlaute). Eltern-Kind: der Elternteil
# ist „du“ — dieselben Wortlaute wie im Geburtshoroskop. Paar: beide sind
# Leser, „ihr“ (Chris-Entscheidung 2026-10-11).
BEWEGUNGEN = {
    'eltern-kind': ('Woran du es merkst', 'Was da arbeitet',
                    'Wie so etwas zur Regel wird',
                    'Der Teil von dir, der das nicht aufgeben will',
                    'Die zwei Formen und das Dazwischen',
                    'Womit du arbeiten kannst', 'Wohin das gehört'),
    'paar': ('Woran ihr es merkt', 'Was da arbeitet',
             'Wie so etwas zur Regel wird',
             'Der Teil in euch, der das nicht aufgeben will',
             'Die zwei Formen und das Dazwischen',
             'Womit ihr arbeiten könnt', 'Wohin das gehört'),
}
BEWEGUNGEN['freundschaft'] = BEWEGUNGEN['paar']   # 2026-10-14c: beide lesen, wie beim Paar
BEWEGUNGEN_EN = ('How you notice it', 'What is at work',
                 'How something like this becomes a rule',
                 'The part of you that does not want to give this up',
                 'The two forms and the in-between',
                 'What you can work with', 'Where this belongs')

# Kapitelarten: Kicker -> (Signatur, Beleg, Bewegungsfolge)
KOPFBLOCK = {
    'Zur Lesart': (False, False, False),
    'Getriebe': (True, True, False),
    'Anlagen': (True, True, False),
    'Kapitel': (True, True, True),
    'Was trägt': (True, True, True),
    'Lernfelder': (True, False, False),
    'Rechenschaft': (False, False, False),
    'Schlusswort': (False, False, False),
}
KICKER_EN = {'On Reading This': 'Zur Lesart', 'Framework': 'Getriebe',
             'What You Bring': 'Anlagen', 'Chapter': 'Kapitel',
             'What Carries': 'Was trägt', 'Fields of Learning': 'Lernfelder',
             'Account': 'Rechenschaft', 'Closing Word': 'Schlusswort'}

# Woerter, die im Referenzschnitt fuer Eltern-Kind und (seit 2026-10-14c) Freundschaft
# einen Satz (Prosa) bzw. eine Zeile (Listen) entfernen: nichts Sexuelles, nichts
# Romantisches (Startprompt, Bau 3). Bewusst weit — ein Satz zu viel weg ist billiger
# als einer zu viel drin. 2026-10-14c: „Ehe“ nur gross geschrieben — die Konjunktion
# „ehe“ („ehe die Zeit reif ist“) nahm ganze Saetze mit.
FILTER_ELTERN_KIND = re.compile(
    r'erot|sexu|sinnlich|begehr|begierde|leidenschaft|\blust\b|lüstern|hure|'
    r'verführ|verlieb|liebhaber|geliebte|liebesbezieh|liebesleben|liebesglück|'
    r'romanz|romantisch|flirt|partnerwahl|wahl des partners|\bpartner|'
    r'anderen geschlecht|(?-i:\bEhen?\b)|ehepartner|bettgeflüster|intim|zärtlich|'
    r'hingabe|eroberer|anziehungskraft|befriedig',
    re.I)

# Woerter fuer Streit, Verletzung oder Angst. Bis 2026-10-11 trug jedes Kapitel,
# das sie beruehrt, den Satz zum realen Problem (B13); seit Chris' Entscheidung
# vom 11.10. (Nachtrag im Pruefbericht Beziehung Text Paar) steht er nur noch in
# „Zur Lesart“ und in hoechstens einem Themenkapitel — B13 nutzt die Liste nicht
# mehr; sie bleibt fuer Proben, die sie brauchen.
STREIT_RE = re.compile(
    r'\b[Ss]treit\w*|\bstritt\w*|\bgestritten\b|\b[Vv]erletz\w*|\bAngst\w*|'
    r'\bängst\w*|\b[Gg]ewalt\b|\bgewaltsam\w*|\bWut\b|\bwütend\w*|\b[Kk]ränk\w*|'
    r'\b[Dd]rohung\w*|\b(?:be|an)?droh(?:t|en|st|te|ten)\b|\b[Hh]erabsetz\w*|'
    r'\banschrei\w*|\bangeschrien\b|\bschrei(?:e|en|st|t)\b|\bgeschrien\b|'
    r'\b[Dd]emütig\w*|\bAngriff\w*')
# 2026-10-11 (Auswertung 11.10., Teil 2, F5/K-a): „kein Horoskop“ allein traf
# gewoehnliche Saetze („Ob zwei Menschen zusammenpassen, sagt es nicht; das kann
# kein Horoskop.“) und setzte sie in Chris' Stellen-Liste. Der Satz traegt nach
# dem Modul die Wendung „kein Thema für ein Horoskop“.
REALPROBLEM_RE = re.compile(
    r'kein Thema für ein Horoskop|nichts mit Astrologie zu tun|'
    r'nicht für ein Horoskop|no topic for a horoscope|'
    r'nothing to do with astrology', re.I)
VERWERF_RE = re.compile(
    r'überspring|verwerf|wiedererkennst|wiedererkennt|betrifft nicht jeden|'
    r'lass es liegen|lasst es liegen|trifft das nicht zu|kennst du das nicht|'
    r'kennt ihr das nicht|nicht wiederfindest|nicht wiederfindet|'
    r'legst das Kapitel|legt das Kapitel|lass das Kapitel|lasst das Kapitel|'
    r'Kapitel überspringen|leg es weg|legt es weg|leg das Kapitel weg|'
    r'legt das Kapitel weg|discard|skip this chapter|set this chapter aside|'
    r'put this chapter aside|does not apply to everyone|if this does not fit',
    re.I)
# 2026-10-11 (Auswertung 11.10., Teil 2, W4): dazu die Tabellenform des
# Klartext-Moduls fuer den Quincunx („passt nicht mit … zusammen“) und
# „nicht zusammenpassen“ — beide gingen im Eltern-Kind-Pruefffall durch.
PASSUNG_RE = re.compile(
    r'(?:passt|passen|gepasst)\s+(?:gut|nicht|perfekt|ideal|wunderbar)\s+'
    r'zusammen|füreinander bestimmt|seelenverwandt|Seelenverwandt|Traumpaar|'
    r'keine Zukunft|zum Scheitern|nicht zueinander passen|Trennung (?:ist|wäre)|'
    r'(?:passt|passen)\s+nicht\s+mit\s+[^.;:!?]{1,80}?\s+zusammen|'
    r'(?:passt|passen)\s+nicht\s+zueinander|nicht\s+zusammen(?:zu)?pass\w*|'
    r'(?:gute|schlechte) Partie|meant to be|soulmate', re.I)

# Pruefmuster der Probe als Konstanten (2026-10-14c, Wartungslauf „Art Freundschaft“,
# Punkt b): probe() prueft mit genau diesen Objekten, hilfe('probe') druckt ihre
# Muster — Chat 1 muss den Quelltext dafuer nicht mehr lesen (vorher 20 bis 41 KB je
# Lauf). Die Muster sind wortgleich die frueher in probe() stehenden.
# B9 Anrede: „du“ bei Paar und Freundschaft, das Nomen „Du“ ausgenommen …
B9_DU_RE = re.compile(r'\b(?:[Dd]u|[Dd]ich|[Dd]ir|[Dd]ein\w*)\b')
B9_DU_NOMEN_RE = re.compile(
    r'\b(?:im|ins|das|ein|dem|zum|vom|am|ans|ihr|sein|ihrem|seinem)\s+Du\b')
# … und „ihr“ bei Eltern-Kind (die dritte Person wird nicht angeredet)
B9_IHR_RE = re.compile(
    r'\b(?:[Ee]uch|[Ee]uer|[Ee]ure[nmrs]?)\b|\b[Ii]hr beide\b|'
    r'\b[Ii]hr (?:seid|habt|könnt|wollt|müsst|dürft|sollt|werdet|wisst|'
    r'merkt|kennt|braucht|lebt|spürt|teilt)\b')
# B10 dritte Person (Eltern-Kind); <VORNAME> steht fuer die nicht angeredete Person
B10_MUSTER = (
    r'diagnos|störung|trauma|therap|somatis|parentifiz|krank|symptom|\w+-kind\b|'
    r'faul|träg\b|bequem|stur|egoist|manipul|übertreib|'
    r'\b<VORNAME> (?:ist|wird|war)\b|'
    r'eines tages|später wird|sorg dafür|bring (?:ihr|ihm) bei|lass (?:sie|ihn) nicht|'
    r'verbiet|zwing|streng\w*|\borb\b|\d+°\d+′')


def _b10_re(vorname):
    """B10_MUSTER mit dem Vornamen der nicht angeredeten Person (Gross/klein egal)."""
    return re.compile(B10_MUSTER.replace('<VORNAME>', re.escape(vorname)), re.I)


# B11: romantische oder sexuelle Lesart (Eltern-Kind in jedem Alter und Freundschaft);
# bei einem Kind unter 18 dazu Alterswoerter
ROMANTIK_RE = re.compile(
    r'verliebt|verlieb|liebhaber|flirt|erot|sexu|sinnlich|begehr|leidenschaft|'
    r'romantisch|romanz|partnerwahl|liebesleben', re.I)
B11_KIND_RE = re.compile(
    ROMANTIK_RE.pattern + r'|\bjährig|\bJahre alt\b|'
    r'\b(?:zwölf|dreizehn|vierzehn|fünfzehn|sechzehn|siebzehn|elf|zehn|neun|acht|'
    r'sieben|sechs)\b(?! (?:Kapitel|Verbindungen|von))|\bAlter\b|Pubertät', re.I)
# B15 Rang, Zahl, Einzigkeit — und was vorher gestrichen wird (keine Rangaussage)
B15_RANG_RE = re.compile(
    r'(eng|dicht|stärk|schwäch|wenig)[a-zäöüß]*ste|einzig|die meisten|überhaupt vorkommt|'
    r'\b(zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|elf|zwölf|beide|[0-9]+) '
    r'(von|Verbindungen|Kontakte|Fäden|Planeten|Faktoren)|Hälfte|Drittel|'
    r'\b(?:zwei|drei|vier|fünf|sechs)mal\b')
B15_NICHT_RANG_RE = re.compile(
    r'\bein(?:e|en|em|er|es)? einzig\w*|\beine Hälfte\b|'
    r'\bHälfte (?:eines|des) Spiegels\b|\bein- oder zweimal\b|'
    r'\b(?:zwei|drei|vier|fünf|sechs)mal (?:in der Woche|im Monat|am Tag|'
    r'pro Woche|die Woche)\b')


def dateiname(art, a, b, datum, teil, englisch=False):
    """Dateiname im Klientenordner (Modul, „Dateinamen und Ablage“) — fuer jede Art.

    art      'paar' | 'eltern-kind' | 'freundschaft' (Gross/klein egal)
    a, b     Vornamen: a bestellt, b ist die zweite Person
    datum    'JJJJ-MM-TT' (Tag von Chat 1)
    teil     'chart_data' | 'analyse' | 'referenz' -> `<A>_<KÜRZEL>_<B>_<Datum>[_EN]_<teil>.md`
             (KÜRZEL `Beziehung`, bei Freundschaft `Freundschaft`); 'pdf' ->
             `<Dokumenttyp>_<A>_und_<B>_<Datum>.pdf`, englisch
             `<Document_Type>_<A>_and_<B>_<Datum>.pdf` (Leerzeichen als _).
    englisch die englische Fassung (`_EN` hinter dem Datum bzw. englischer PDF-Name)
    Ein Zusatz `_b`, `_c` fuer einen schon belegten Namen kommt danach von Hand.
    """
    art = (art or '').strip().lower().replace(' ', '-')
    if art not in ARTEN:
        raise BeziehungFehler('Art „%s“ unbekannt — erlaubt: %s.'
                              % (art, ', '.join(ART_TITEL[x] for x in ARTEN)))
    if teil == 'pdf':
        if englisch:
            return '%s_%s_and_%s_%s.pdf' % (DOKUMENTTYP_EN[art].replace(' ', '_'), a, b, datum)
        return '%s_%s_und_%s_%s.pdf' % (DOKUMENTTYP[art], a, b, datum)
    if teil not in ('chart_data', 'analyse', 'referenz'):
        raise BeziehungFehler("teil: 'chart_data', 'analyse', 'referenz' oder 'pdf'.")
    return '%s_%s_%s_%s%s_%s.md' % (a, KUERZEL[art], b, datum, '_EN' if englisch else '', teil)


class BeziehungFehler(Exception):
    """Eingabe, die das Beziehungshoroskop nicht tragen kann — der Lauf haelt an."""


# ---------------------------------------------------------------------------
# Kleinkram
# ---------------------------------------------------------------------------

def _gr(deg):
    return radix._gr(deg)


def _zahl(s):
    return float(str(s).replace(',', '.'))


def _sha8(pfad):
    with open(pfad, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def _slug(name):
    s = (name or '').strip().lower()
    for a, b in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss'),
                 ('é', 'e'), ('è', 'e'), ('á', 'a'), ('ó', 'o')):
        s = s.replace(a, b)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s or 'x'


def _tok(faktor, name):
    """Faktor mit Person ohne Leerzeichen (Rangzeilen-Grammatik)."""
    return '%s(%s)' % (faktor, (name or '?').replace(' ', '_'))


def _mit(faktor, name):
    return '%s (%s)' % (faktor, name)


def zeichen_von(lon):
    return ZEICHEN[int((lon % 360) // 30)]


def stand_text(lon, glyphen=False):
    z = zeichen_von(lon)
    return '%s %s%s' % (radix.gr_zeichen(lon), z,
                        (' ' + ZEICHEN_GLYPHE[z]) if glyphen else '')


def _genitiv(name):
    """Genitiv eines Vornamens: angehaengtes s, bei Namen auf s, ß, x, z ein
    Apostroph."""
    return name + ('’' if name and name[-1].lower() in 'sßxz' else 's')


def _fglyph(name):
    return FAKTOR_GLYPHE.get(name, '')


def _faktor_beleg(name):
    """Faktor fuer Belege: ausgeschrieben + Symbol; Pholus und Achsen ohne."""
    if name in ACHSEN:
        return ACHSEN_LANG[name]
    g = _fglyph(name)
    return name if (not g or len(g) != 1) else '%s %s' % (name, g)


# ---------------------------------------------------------------------------
# Datenblatt einer Person lesen
# ---------------------------------------------------------------------------

def _abschnitt(text, titel_re):
    m = re.search(r'^## ' + titel_re + r'[^\n]*\n', text, re.M)
    if not m:
        return ''
    rest = text[m.end():]
    e = re.search(r'^## |^@@', rest, re.M)
    return rest[:e.start()] if e else rest


# 2026-10-14 (Auswertung der Pruefberichte vom 14.10., F2): Die Funktion las jd und
# Koordinaten nur aus `JD_UT`/`LAT, LON` und zwei Kopfformen. Die Kopfzeile des
# Geruests („Koordinaten der Rechnung: <Breite>° N, <Länge>° O“, build.datenblatt_geruest)
# und das Tupel `JD_GEBURT, LAT, LON, ALTER = …` der Datenblaetter von Mitte September
# fielen durch — bei 17 von 20 Geburtshoroskop-Datenblaettern aus dem Oktober fehlten
# die Koordinaten, und die Zeitprobe lief still leer. Die Lesehilfen unten nehmen die
# Formate auf, die in den Datenblaettern der Pipeline seit September stehen; was sie
# nicht lesen, bleibt None und haelt in rechnung() an.
_MINUS = str.maketrans({'\u2212': '-', '\u2013': '-'})
# 2026-10-14b: Monatsnamen fuer ein Geburtsdatum „T. Monat JJJJ“ im Kopf
_MONATE = {'Januar': 1, 'Jänner': 1, 'Februar': 2, 'Feber': 2, 'März': 3, 'Maerz': 3,
           'April': 4, 'Mai': 5, 'Juni': 6, 'Juli': 7, 'August': 8, 'September': 9,
           'Oktober': 10, 'November': 11, 'Dezember': 12}


def _jd_lesen(text):
    """Julianisches Datum (UT) der Geburt aus einem Personen-Datenblatt -> float
    oder None. Reihenfolge: `JD_UT = …`, `JD_GEBURT = …` bzw. das Tupel
    `JD_GEBURT, LAT, LON[, …] = …` im Python-Block, dann die Kopfzeilen
    „Julianisches Datum (UT): …“, „JD (UT): …“ und „· JD …“."""
    for muster in (r'JD_UT\s*=\s*([0-9]+\.[0-9]+)',
                   r'JD_GEBURT\s*(?:,\s*[A-Z_]+\s*)*=\s*([0-9]+\.[0-9]+)',
                   r'Julianisch\w*\s+Datum[^\n]*?([0-9]{7}[.,][0-9]+)',
                   r'\bJD\s*\(UT\)[^\n0-9]*([0-9]{7}[.,][0-9]+)',
                   r'(?:^|·)\s*\**JD\**\s+([0-9]{7}[.,][0-9]+)'):
        m = re.search(muster, text, re.M)
        if m:
            return _zahl(m.group(1))
    return None


def _koord_aus_zeile(zeile):
    """(lat, lon) aus EINER Koordinatenzeile des Kopfes oder (None, None).

    Liest Grad mit Himmelsrichtung — dezimal („50,0000° N“) oder in Grad, Minuten
    und Sekunden („50°00′00″ N“) — und ein Dezimalpaar ohne Richtung („(50.00000,
    10.00000; …)“, „Dezimal 10.50 / -60.25“); Sued und West negativ. Von mehreren
    Schreibweisen derselben Koordinate gilt die genaueste; weichen sie um mehr als
    ihre Rundung voneinander ab, gilt keine."""
    z = zeile.replace('**', '').translate(_MINUS)
    kand = {'lat': [], 'lon': []}
    vorz = {'lat': None, 'lon': None}
    for m in re.finditer(r'(?<![\d.,])(\d{1,3})\s*°\s*(\d{1,2}(?:[.,]\d+)?)\s*[′\']'
                         r'(?:\s*(\d{1,2}(?:[.,]\d+)?)\s*[″"])?\s*([NSOEW])\b', z):
        w = (int(m.group(1)) + _zahl(m.group(2)) / 60.0
             + (_zahl(m.group(3)) / 3600.0 if m.group(3) else 0.0))
        h = m.group(4)
        k = 'lat' if h in 'NS' else 'lon'
        vorz[k] = -1.0 if h in 'SW' else 1.0
        kand[k].append((vorz[k] * w, (1 / 3600.0) if m.group(3) else (1 / 60.0)))
    for m in re.finditer(r'(?<![\d.,])(\d{1,3}[.,](\d+))\s*°?\s*([NSOEW])\b', z):
        h = m.group(3)
        k = 'lat' if h in 'NS' else 'lon'
        vorz[k] = -1.0 if h in 'SW' else 1.0
        kand[k].append((vorz[k] * _zahl(m.group(1)), 10.0 ** -len(m.group(2))))
    for m in re.finditer(r'(?<![\d.,])(-?\d{1,3}[.,](\d{2,}))\s*(?:/|,(?=\s))\s*'
                         r'(-?\d{1,3}[.,](\d{2,}))(?![\d°′])', z):
        for k, wert, nachk in (('lat', m.group(1), m.group(2)), ('lon', m.group(3),
                                                                 m.group(4))):
            w = _zahl(wert)
            if not wert.startswith('-') and vorz[k] is not None:
                w = vorz[k] * w
            kand[k].append((w, 10.0 ** -len(nachk)))
    aus = []
    for k in ('lat', 'lon'):
        if not kand[k]:
            return None, None
        best = min(kand[k], key=lambda x: x[1])
        if any(abs(w - best[0]) > max(r, best[1]) + 1e-6 for w, r in kand[k]):
            return None, None
        aus.append(best[0])
    if not (-90.0 <= aus[0] <= 90.0 and -180.0 <= aus[1] <= 180.0):
        return None, None
    return aus[0], aus[1]


def _koordinaten_lesen(text):
    """Breite und Laenge der Rechnung (Dezimalgrad, Nord und Ost positiv) aus einem
    Personen-Datenblatt -> (lat, lon) oder (None, None).

    Zuerst der Python-Block (`JD_GEBURT, LAT, LON[, …] = …`, `LAT, LON = …`,
    `LAT = …` mit `LON = …`), dann die Kopfzeilen „… / … Dezimalgrad“ und
    „dezimal …, …“, zuletzt die Koordinatenzeile des Kopfes — „Koordinaten der
    Rechnung: …“, sonst die erste Zeile oder Tabellenzeile, die mit „Koordinaten“
    oder „Ortskoordinaten“ beginnt, sonst die Zeile des Geburtsorts
    (_koord_aus_zeile). Andere Koordinaten im Text (etwa ein Vergleichsort in einer
    Gegenprobe) liest die Funktion nicht."""
    t = text.translate(_MINUS)
    m = re.search(r'JD_GEBURT\s*,\s*LAT\s*,\s*LON(?:\s*,\s*[A-Z_]+)*\s*=\s*[0-9]+\.[0-9]+'
                  r'\s*,\s*(-?[0-9]+(?:\.[0-9]+)?)\s*,\s*(-?[0-9]+(?:\.[0-9]+)?)', t)
    if not m:
        m = re.search(r'\bLAT\s*,\s*LON\s*=\s*(-?[0-9]+\.[0-9]+)\s*,\s*(-?[0-9]+\.[0-9]+)', t)
    if m:
        return _zahl(m.group(1)), _zahl(m.group(2))
    m1 = re.search(r'^\s*LAT\s*=\s*(-?[0-9]+\.[0-9]+)', t, re.M)
    m2 = re.search(r'^\s*LON\s*=\s*(-?[0-9]+\.[0-9]+)', t, re.M)
    if m1 and m2:
        return _zahl(m1.group(1)), _zahl(m2.group(1))
    m = re.search(r'(-?[0-9]+[.,][0-9]+)\s*/\s*(-?[0-9]+[.,][0-9]+)\s*Dezimalgrad', t)
    if not m:
        m = re.search(r'dezimal\s+(-?[0-9]+[.,][0-9]+)\s*,\s*(-?[0-9]+[.,][0-9]+)', t, re.I)
    if m:
        return _zahl(m.group(1)), _zahl(m.group(2))
    vorspann = t.split('\n## Stände', 1)[0]
    # Die erste vorhandene Beschriftung gilt, auch als Tabellenzeile („| Ortskoordinaten
    # (Setzung dieses Laufs) | 50,0000° N / 10,0000° O |“, Format von Mitte September);
    # die Zeile des Geburtsorts nur, wenn keine Koordinatenzeile da ist.
    for muster in (r'Koordinaten der Rechnung', r'(?:Orts)?[Kk]oordinaten', r'Geburtsort'):
        z = re.findall(r'^[ \t]*(?:[-|][ \t]*)?\**[ \t]*' + muster + r'[^:|\n]*[:|](.*)$',
                       vorspann, re.M)
        if z:
            return _koord_aus_zeile(z[0])
    return None, None


# 2026-10-15 (FFU, Auswertung der Pruefberichte vom 14.10., Teil d, Punkt 2): Woerter, die in
# der H1 eines Personen-Datenblatts den Dokumenttyp nennen, sind nie der Vorname. Die H1 von
# Mitte September „# Datenblatt — Geburtshoroskop <Vorname> <Nachname>“ gab „Geburtshoroskop“
# als Vornamen — ohne Meldung in Kopf, Spaltenkoepfen, PERSON_A und @@SELEKTOR. Gegengeprueft
# ueber alle Personen-Datenblaetter der Klientenordner (109 lesbare: 98 gleich, 11 vorher
# falsch, danach keins).
_DOKWORT_RE = re.compile(
    r'(?i)(horoskop|datenblatt|datengrundlage|^chart|^daten$|ultimativ|^modul|schritt|'
    r'leitfaden|^transit|^ea$|^ea-|^radix|^kombi|^standard|^evolution|^beziehung|'
    r'^freundschaft|^vertiefung)')


def _vorname_tok(s):
    """Das erste Wort aus `s`, das ein Vorname sein kann: gross geschrieben, mit
    Kleinbuchstaben, nur Buchstaben (Bindestrich und Apostroph innen erlaubt), kein Wort
    des Dokumenttyps (_DOKWORT_RE). Klammerzusaetze und alles hinter „·“ zaehlen nicht.
    -> str oder None."""
    s = re.sub(r'\([^)]*\)', ' ', s or '').split('·')[0].replace('**', ' ')
    for tok in re.split(r'[\s,„“"‚‘]+', s.strip()):
        if (tok and tok[:1].isupper() and any(c.islower() for c in tok)
                and re.fullmatch(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", tok)
                and not _DOKWORT_RE.search(tok)):
            return tok
    return None


def _vorname_lesen(text, vorspann, pfad):
    """Vorname eines Personen-Datenblatts (seit 2026-10-15): zuerst hinter dem LETZTEN
    Gedankenstrich der H1 („# Geburtshoroskop — Datenblatt — <Name>“), dann aus dem
    Namensfeld des Kopfes (Tabellenzeile „| Name | … |“ oder Zeile „Name: …“), zuletzt aus
    dem Dateinamen `<Vorname>_…_chart_data.md` — je das erste Wort, das _vorname_tok()
    gelten laesst. -> str oder None (rechnung() haelt dann an)."""
    h1 = re.search(r'^# [^\n]* — ([^\n—]+)$', text, re.M)
    if h1:
        v = _vorname_tok(h1.group(1))
        if v:
            return v
    z = (re.search(r'^\|[ \t]*\**Name\**[ \t]*\|([^|\n]+)\|', vorspann, re.M)
         or re.search(r'Name:\**[ \t]*([^\n]+)', vorspann))
    if z:
        v = _vorname_tok(z.group(1))
        if v:
            return v
    b = re.split(r'[_\s.]', os.path.basename(pfad))[0]
    return _vorname_tok(b[:1].upper() + b[1:])


def _offen_eigen_lesen(text, namen):
    """Faktoren mit OFFENER FUEHRUNG im eigenen Bild (seit 2026-10-15; FFU, Auswertung
    14.10. d, Punkt 1): die FAKTOR-Zeilen des @@SELEKTOR-Blocks mit `fuehrung=offen` —
    dieselbe Quelle, aus der die Konstellationstabelle des Geburtshoroskops „11=12“ setzt
    (radix.haus_spalte(offen=True)); den Block begrenzt wie selektor.parse_chart() die
    Zeile `@@SELEKTOR` und die naechste @@-Zeile. `namen` sind die Faktornamen des
    factors-Blocks; zurueck kommen die davon, deren Zeile `fuehrung=offen` traegt,
    sortiert. Ein Datenblatt von vor dem 2026-09-30 traegt keine — dann stehen die Haeuser
    wie in seinem eigenen Horoskop, ohne offene Fuehrung."""
    schl = {radix._offen_schluessel(n): n for n in namen}
    out, im_block = set(), False
    for ln in text.split('\n'):
        z = ln.strip()
        if z == '@@SELEKTOR':
            im_block = True
            continue
        if z.startswith('@@'):
            im_block = False
            continue
        if not im_block:
            continue
        m = re.match(r'(?i:faktor)\s+(\S+)\s.*\bfuehrung=offen\b', z)
        if m and schl.get(radix._offen_schluessel(m.group(1))):
            out.add(schl[radix._offen_schluessel(m.group(1))])
    return sorted(out)


def lies_datenblatt(pfad):
    """Liest ein Datenblatt (`<klient>_chart_data.md`) einer Person.

    -> dict mit 'pfad', 'datei', 'sha8', 'vorname', 'geschlecht'
       ('weiblich'|'männlich'|'divers'|None), 'geburtsdatum' (datetime.date
       oder None), 'geburtszeit', 'geburtsort', 'fassung', 'zeitunsicherheit'
       (je Wortlaut des Kopfes oder 'nicht angegeben'), 'jd', 'lat', 'lon'
       (float oder None), 'factors' (Liste wie im factors-Block, ohne
       Ausgemustertes), 'cusps' (zwoelf Laengen), 'leitachse' (Wortlaut der
       Themenzeile mit leitachse=ja oder None; rechnung() haelt ohne sie an),
       'kinder_baustein' (bool), 'offen_eigen' (seit 2026-10-15: die Faktoren mit
       `fuehrung=offen` im @@SELEKTOR-Block, _offen_eigen_lesen()),
       'hinweise' (Liste).

    Gelesen wird der Python-Block mit `factors = [...]` (beide Schreibweisen
    `CUSPS`/`cusps`); jd und Koordinaten ueber _jd_lesen() und _koordinaten_lesen()
    aus dem Block oder dem Kopf — alle Formate der Pipeline seit September (seit
    2026-10-14). Was dort nicht steht, bleibt None; rechnung() haelt dann an.
    Die uebrigen Kopfangaben (Geburtsdatum, -zeit, -ort, Fassung, Zeitunsicherheit)
    seit 2026-10-14b auch als Tabellenzeile („| Geburtsdatum | … |“, Format von Mitte
    September) und aus der Zeile „**Geburt:** TT.MM.JJJJ, <Zeit> · Geburtsort: …“;
    das Datum auch als „T. Monat JJJJ“, das Geschlecht auch gross geschrieben.
    Der Vorname seit 2026-10-15 ueber _vorname_lesen(): H1 ohne Woerter des Dokumenttyps,
    sonst das Namensfeld, sonst der Dateiname; ohne Vornamen „?“ und ANHALTEN in rechnung().
    BeziehungFehler bei einem Transit-Datenblatt (H1 nennt „Transit“): Seine
    Themenliste und Leitachse gehoeren zum Transit, nicht zum Geburtsbild
    (Chris-Entscheidung 2026-10-14: vorher Schritt 1 Geburtshoroskop).
    BeziehungFehler, wenn factors oder cusps fehlen oder nicht zwoelf Spitzen
    tragen — ohne sie gibt es keine Ueberlagerung.
    """
    text = open(pfad, encoding='utf-8').read()
    # 2026-10-14 (F2): Ein Transit-Datenblatt traegt die Themen des Transits —
    # seine „Leitachse“ ist ein Transit-Thema, und seine H1 hat zwei Gedankenstriche.
    _h1 = re.search(r'^# [^\n]*$', text, re.M)
    if _h1 and 'Transit' in _h1.group(0):
        raise BeziehungFehler(
            '%s ist ein Transit-Datenblatt — Themen und Leitachse gehören dort zum '
            'Transit, nicht zum Geburtsbild. Für das Beziehungshoroskop das '
            'Geburtshoroskop-Datenblatt der Person nehmen; gibt es keins, läuft vorher '
            'Schritt 1 des Geburtshoroskops (ohne Aufpreis, Chris-Entscheidung '
            '2026-10-14). Anhalten und Chris sagen.' % os.path.basename(pfad))
    out = {'pfad': pfad, 'datei': os.path.basename(pfad), 'sha8': _sha8(pfad),
           'hinweise': []}
    m = re.search(r'factors\s*=\s*(\[.*?\n\s*\])', text, re.S)
    if not m:
        raise BeziehungFehler('%s: kein factors-Block (factors = [...]).'
                              % out['datei'])
    try:
        fac = ast.literal_eval(m.group(1))
    except (ValueError, SyntaxError) as e:
        raise BeziehungFehler('%s: factors-Block nicht lesbar (%s).'
                              % (out['datei'], e))
    weg = [f['name'] for f in fac if f.get('name') in radix.AUSGEMUSTERT]
    if weg:
        out['hinweise'].append('ausgemustert, nicht gerechnet: ' + ', '.join(weg))
    fac = [dict(f) for f in fac if f.get('name') not in radix.AUSGEMUSTERT]
    for f in fac:
        if f.get('name') in ('Knoten', 'Nordknoten'):
            f['name'] = 'Mondknoten'
        f['lon'] = float(f['lon']) % 360.0
    namen = [f['name'] for f in fac]
    fehlt = [n for n in ('Sonne', 'Mond', 'AC', 'MC') if n not in namen]
    if fehlt:
        raise BeziehungFehler('%s: factors ohne %s.' % (out['datei'],
                                                        ', '.join(fehlt)))
    for ax, geg in (('AC', 'DC'), ('MC', 'IC')):
        if geg not in namen:
            lon = (fac[namen.index(ax)]['lon'] + 180.0) % 360.0
            fac.append({'name': geg, 'glyph': geg, 'lon': lon, 'retro': False})
    out['factors'] = fac
    # 2026-10-15 (FFU, Auswertung 14.10. d, Punkt 1): offene Fuehrung des eigenen Bildes
    out['offen_eigen'] = _offen_eigen_lesen(text, [f['name'] for f in fac])
    mc = re.search(r'(?im)^\s*cusps\s*=\s*(\[[^\]]*\])', text)
    if not mc:
        raise BeziehungFehler('%s: keine Hausspitzen (CUSPS = [...]).'
                              % out['datei'])
    cusps = [float(x) % 360.0 for x in ast.literal_eval(mc.group(1))]
    if len(cusps) != 12:
        raise BeziehungFehler('%s: %d statt zwoelf Hausspitzen.'
                              % (out['datei'], len(cusps)))
    out['cusps'] = cusps
    # jd, lat, lon (2026-10-14: alle Formate der Pipeline seit September)
    out['jd'] = _jd_lesen(text)
    out['lat'], out['lon'] = _koordinaten_lesen(text)
    # Kopf: der Abschnitt „## Kopf“, sonst alles vor den Staenden
    kopf = _abschnitt(text, r'Kopf') or text.split('\n## Stände', 1)[0]
    vorspann = text.split('\n## Stände', 1)[0]
    # 2026-10-14: der Name steht hinter dem LETZTEN Gedankenstrich der H1
    # („# Geburtshoroskop — Datenblatt — <Name>“); vorher hinter dem ersten.
    # 2026-10-15 (FFU, Auswertung 14.10. d, Punkt 2): Woerter des Dokumenttyps zaehlen
    # nicht („# Datenblatt — Geburtshoroskop <Vorname> <Nachname>“ gab „Geburtshoroskop“);
    # ohne Namen in der H1 das Namensfeld, zuletzt der Dateiname (_vorname_lesen()).
    out['vorname'] = _vorname_lesen(text, vorspann, pfad) or '?'
    # 2026-10-14b (FFU, Auswertung 14.10. c): auch gross geschrieben („Weiblich, Anrede …“).
    g = re.search(r'\b(weiblich|männlich|divers)\b', vorspann, re.I)
    out['geschlecht'] = g.group(1).lower() if g else None

    def _zeile(muster):
        # Listenzeilen des Kopfes: „- Geburtszeit: …“, „- **Geburtszeit:** …“; seit
        # 2026-10-14 auch ohne Spiegelstrich und als Teil einer Zeile mit „·“
        # („**Geburtsdatum:** … · **Geburtszeit:** … · JD …“, Format von Mitte September).
        # 2026-10-14b (FFU, Auswertung 14.10. c): auch als Tabellenzeile des Vorspanns
        # („| Geburtsdatum | … |“, ebenfalls Mitte September) und ohne Fettdruck hinter
        # „·“ („**Geburt:** … · Geburtsort: …“). Vorher stand dort „nicht angegeben“ —
        # beim Paar mit falschem ANHALTEN „kein Geburtsdatum“, bei Eltern-Kind still.
        z = re.search(r'^\s*-\s*\**' + muster + r'[^:\n]*:\**\s*([^\n]+)$', kopf,
                      re.M)
        if not z:
            z = re.search(r'(?:^|·)[ \t]*(?:-[ \t]*)?\*\*' + muster
                          + r'\b[^:\n·*]*:\**[ \t]*([^\n·]+)', kopf, re.M)
        if not z:
            z = re.search(r'^\|[ \t]*\**' + muster + r'\b[^|\n]*\|[ \t]*'
                          r'([^|\n]*[^|\s][^|\n]*?)[ \t]*\|', vorspann, re.M)
        if not z:
            z = re.search(r'·[ \t]*' + muster + r'\b[^:\n·*|]*:[ \t]*([^\n·]+)', vorspann)
        if not z:                           # schlichte Zeile „Geburtszeit: …“ (Mitte September)
            z = re.search(r'^[ \t]*' + muster + r'\b[^:\n·*|]*:[ \t]*([^\n]+)$', kopf, re.M)
        return z.group(1).replace('**', '').strip() if z else 'nicht angegeben'

    def _datum(s):
        # „TT.MM.JJJJ“ oder (2026-10-14b) „T. Monat JJJJ“ -> datetime.date, sonst None
        m = re.search(r'\b(\d{1,2})\.\s?(\d{1,2})\.\s?(\d{4})\b', s or '')
        t = None
        if m:
            t = (int(m.group(3)), int(m.group(2)), int(m.group(1)))
        else:
            m = re.search(r'\b(\d{1,2})\.\s*(%s)\s+(\d{4})\b' % '|'.join(_MONATE), s or '')
            if m:
                t = (int(m.group(3)), _MONATE[m.group(2)], int(m.group(1)))
        try:
            return datetime.date(*t) if t else None
        except ValueError:
            return None

    gd = re.search(r'Geburtsdatum:\**\s*(\d{1,2})\.(\d{1,2})\.(\d{4})', kopf)
    out['geburtsdatum'] = (datetime.date(int(gd.group(3)), int(gd.group(2)),
                                         int(gd.group(1))) if gd else None)
    # 2026-10-14b: Tabellenzeile, „T. Monat JJJJ“ und die Zeile „**Geburt:** …“
    geburt = re.search(r'\*\*Geburt:\**[ \t]*([^\n]+)', vorspann)
    if out['geburtsdatum'] is None:
        out['geburtsdatum'] = _datum(_zeile(r'Geburtsdatum'))
    if out['geburtsdatum'] is None and geburt:
        out['geburtsdatum'] = _datum(geburt.group(1).split('·')[0])
    out['geburtszeit'] = _zeile(r'Geburtszeit')
    if out['geburtszeit'] == 'nicht angegeben' and geburt:
        zt = re.match(r'[^·\n]*?\d{4}[ \t]*,[ \t]*([^·\n]+)', geburt.group(1))
        if zt:
            out['geburtszeit'] = zt.group(1).replace('**', '').strip()
    out['geburtsort'] = _zeile(r'Geburtsort')
    out['fassung'] = _zeile(r'Fassung')
    if out['fassung'] == 'nicht angegeben':          # „**Fassung 2**“, „- Fassung 2“
        fz = re.search(r'(?:^|·)[ \t]*(?:-[ \t]*)?\**Fassung[ \t]+(\d+)\b', kopf, re.M)
        if fz:
            out['fassung'] = fz.group(1)
    out['fassung'] = re.sub(r'^Fassung[ \t]+(?=\d)', '', out['fassung'])  # „| Fassung | Fassung 1 |“
    out['zeitunsicherheit'] = _zeile(r'Zeitunsicherheit')
    out['kinder_baustein'] = 'KINDER-BAUSTEIN' in vorspann
    # Leitachse aus der Themenliste
    th = _abschnitt(text, r'Themenliste')
    out['leitachse'] = None
    for blk in re.split(r'\n(?=THEMA \d+)', th):
        if re.search(r'leitachse\s*=\s*ja', blk):
            t = re.search(r'titel=([^\n|]+)', blk)
            fu = re.search(r'fuehrt=([^\n|]+)', blk)
            nr = re.match(r'THEMA (\d+)', blk.strip())
            out['leitachse'] = '%s%s%s' % (
                ('Thema %s: ' % nr.group(1)) if nr else '',
                t.group(1).strip() if t else '?',
                (' (führt: %s)' % fu.group(1).strip()) if fu else '')
            break
    return out


def alter_am(geburtsdatum, tag):
    """Volle Jahre am Tag `tag` (datetime.date) — None ohne Geburtsdatum."""
    if not geburtsdatum:
        return None
    a = tag.year - geburtsdatum.year
    if (tag.month, tag.day) < (geburtsdatum.month, geburtsdatum.day):
        a -= 1
    return a


# ---------------------------------------------------------------------------
# Aspekte zwischen beiden Bildern
# ---------------------------------------------------------------------------

def _orb_von(name, orbs=None):
    if orbs and name in orbs:
        return orbs[name]
    if name not in radix.HUBER_ORB:
        radix._orb_unbekannt(name)
    return radix.HUBER_ORB.get(name, 3)


def paar_aspekt(na, la, nb, lb, orbs=None):
    """Der Aspekt zwischen zwei Faktoren verschiedener Bilder oder None.

    Dieselbe Logik wie radix.huber_aspects() fuer ein Paar: Hauptaspekte
    (Konjunktion, Quadrat, Trigon, Opposition) voll bis zum kleineren,
    einseitig bis zum groesseren Orbis; Nebenaspekte (Halbsextil 2°, Sextil
    6°, Quincunx 3°) mit festem Orbis, auf beide Faktor-Orben gedeckelt; der
    Mondknoten erbt den Orbis des Partners. Dazu 'eng': Abweichung hoechstens
    ENG_ANTEIL mal der volle Orbis (beim Hauptaspekt der kleinere, beim
    Nebenaspekt der gedeckelte feste).

    -> {'angle', 'name', 'color', 'strength', 'orb' (ungerundet), 'eng',
        'eng_grenze'} oder None.
    """
    d = abs(la - lb) % 360.0
    if d > 180.0:
        d = 360.0 - d
    o1, o2 = _orb_von(na, orbs), _orb_von(nb, orbs)
    a_erbt, b_erbt = na in radix.KNOTEN_ERBT, nb in radix.KNOTEN_ERBT
    if a_erbt and not b_erbt:
        o1 = o2
    elif b_erbt and not a_erbt:
        o2 = o1
    for angle, color, neben in radix._ASPECT_DEFS:
        dev = abs(d - angle)
        if angle in radix._MAIN_ANGLES:
            if dev <= min(o1, o2):
                st = 'voll'
            elif dev <= max(o1, o2):
                st = 'einseitig'
            else:
                continue
            grenze = ENG_ANTEIL * min(o1, o2)
        else:
            lim = min(neben, o1, o2)
            if dev > lim:
                continue
            st = 'neben'
            grenze = ENG_ANTEIL * lim
        return {'angle': angle, 'name': radix._ANG_NAME[angle], 'color': color,
                'strength': st, 'orb': dev, 'eng': dev <= grenze + 1e-9,
                'eng_grenze': grenze}
    return None


def _spiegel_zusammenziehen(zeilen):
    """Achsen-Spiegel zu einer Zeile: derselbe Faktor zu beiden Enden einer
    Achse des anderen, gleiche Stufe, Konjunktion/Opposition oder
    Quadrat/Quadrat. Die Achse kann auf Seite a oder b stehen."""
    out, verbraucht = [], set()
    for i, z in enumerate(zeilen):
        if i in verbraucht:
            continue
        if z['b'] in ACHSEN and z['a'] not in ACHSEN:
            seite, achse, faktor = 'b', z['b'], z['a']
        elif z['a'] in ACHSEN and z['b'] not in ACHSEN:
            seite, achse, faktor = 'a', z['a'], z['b']
        else:
            out.append(z)
            continue
        gegen = GEGENACHSE[achse]
        treffer = None
        if z['name'] in ('Konjunktion', 'Opposition', 'Quadrat'):
            for j in range(i + 1, len(zeilen)):
                if j in verbraucht:
                    continue
                y = zeilen[j]
                if y['strength'] != z['strength']:
                    continue
                if seite == 'b' and (y['a'], y['b']) != (faktor, gegen):
                    continue
                if seite == 'a' and (y['a'], y['b']) != (gegen, faktor):
                    continue
                if (z['name'] == 'Quadrat' and y['name'] == 'Quadrat') or \
                        {z['name'], y['name']} == {'Konjunktion', 'Opposition'}:
                    treffer = (j, y)
                    break
        if treffer is None:
            out.append(z)
            continue
        j, y = treffer
        verbraucht.add(j)
        if z['name'] == 'Quadrat':
            fuehrt, zweit = (z, y) if achse in ('AC', 'MC') else (y, z)
        else:
            fuehrt, zweit = (z, y) if z['name'] == 'Konjunktion' else (y, z)
        r = dict(fuehrt)
        zachse = zweit['b'] if seite == 'b' else zweit['a']
        r['spiegel'] = '%s %s' % (zweit['name'], zachse)
        r['spiegel_seite'] = seite
        out.append(r)
    return out


def _sortiert(zeilen):
    return sorted(zeilen, key=lambda x: (STUFE_RANG.get(x['strength'], 9),
                                         x['orb'], FAKTOR_REIHE.index(x['a'])
                                         if x['a'] in FAKTOR_REIHE else 99,
                                         FAKTOR_REIHE.index(x['b'])
                                         if x['b'] in FAKTOR_REIHE else 99))


def _faktoren(fx):
    by = {f['name']: f for f in fx}
    return [by[n] for n in FAKTOR_REIHE if n in by] + \
        [f for f in fx if f['name'] not in FAKTOR_REIHE]



def _haus_eigen(p, name, lon):
    """Haus-Spalte eines Faktors im EIGENEN Bild ('7', '11/12', '11=12'): offene
    Fuehrung, wenn sein Datenblatt sie fuehrt (lies_datenblatt(): 'offen_eigen') — wie
    die Konstellationstabelle des Geburtshoroskops. Seit 2026-10-15 (FFU, Auswertung
    14.10. d, Punkt 1); vorher stand hier die Stufe allein, auf Staendeseite und in den
    Staenden des Datenblatts der Beziehung „12/11“ gegen „11=12“ im eigenen Horoskop."""
    return radix.haus_spalte(lon, p['cusps'], offen=name in set(p.get('offen_eigen') or ()))


def kreuzaspekte(fa, fb, orbs=None):
    """Alle Aspekte zwischen den Faktoren von A (Seite 'a') und B (Seite 'b').

    Achse–Achse-Paare stehen nicht hier (s. achsenkontakte()); Achsen-Spiegel
    sind zusammengezogen (Feld 'spiegel', z. B. 'Opposition DC'). Sortiert
    nach Stufe, dann Orb. -> Liste von dicts {'a', 'b', 'name', 'angle',
    'color', 'strength', 'orb', 'eng', 'eng_grenze', ggf. 'spiegel',
    'spiegel_seite'}.
    """
    roh = []
    for a in _faktoren(fa):
        for b in _faktoren(fb):
            if a['name'] in ACHSEN and b['name'] in ACHSEN:
                continue
            asp = paar_aspekt(a['name'], a['lon'], b['name'], b['lon'], orbs)
            if asp:
                asp.update({'a': a['name'], 'b': b['name']})
                roh.append(asp)
    return _sortiert(_spiegel_zusammenziehen(roh))


def achsenkontakte(fa, fb):
    """Die Achsen beider zueinander: AC und MC von A gegen AC, MC, DC, IC von B
    (die Gegenenden von A sind Spiegel und fehlen), Spiegel auf B-Seite
    zusammengezogen; Orbis der Achsen (je 5°). Gleiche Felder wie
    kreuzaspekte()."""
    roh = []
    pa = {f['name']: f for f in fa}
    pb = {f['name']: f for f in fb}
    for an in ('AC', 'MC'):
        for bn in ACHSEN:
            if an in pa and bn in pb:
                asp = paar_aspekt(an, pa[an]['lon'], bn, pb[bn]['lon'])
                if asp:
                    asp.update({'a': an, 'b': bn})
                    roh.append(asp)
    out, verbraucht = [], set()
    for i, z in enumerate(roh):
        if i in verbraucht:
            continue
        gegen = GEGENACHSE[z['b']]
        treffer = None
        for j in range(i + 1, len(roh)):
            y = roh[j]
            if j in verbraucht or y['a'] != z['a'] or y['b'] != gegen \
                    or y['strength'] != z['strength']:
                continue
            if (z['name'] == 'Quadrat' and y['name'] == 'Quadrat') or \
                    {z['name'], y['name']} == {'Konjunktion', 'Opposition'}:
                treffer = (j, y)
                break
        if treffer is None:
            out.append(z)
            continue
        j, y = treffer
        verbraucht.add(j)
        if z['name'] == 'Quadrat':
            fuehrt, zweit = (z, y) if z['b'] in ('AC', 'MC') else (y, z)
        else:
            fuehrt, zweit = (z, y) if z['name'] == 'Konjunktion' else (y, z)
        r = dict(fuehrt)
        r['spiegel'] = '%s %s' % (zweit['name'], zweit['b'])
        r['spiegel_seite'] = 'b'
        out.append(r)
    return _sortiert(out)


# ---------------------------------------------------------------------------
# Hausueberlagerung
# ---------------------------------------------------------------------------

def ueberlagerung(fx, cusps_y, offen=()):
    """Die Faktoren eines Bildes (fx) in den Haeusern des anderen (cusps_y).

    Faktoren: Planeten, Mondknoten, Chiron, Lilith, Pholus, AC und MC (DC und
    IC sind deren Gegenenden). Je Faktor 'haus' (rechnerisch), 'nebenhaus'
    und 'abstand_spitze' bei Grenzlage (5°), 'fuehrend' (Schwellenlage bis 2°:
    das Nebenhaus fuehrt), 'offen' (aus der Zeitprobe: keins der beiden
    Haeuser fuehrt), 'spalte' ('7', '11/12', '6=7') und 'stand'.
    """
    offen = set(offen or ())
    out = []
    for f in _faktoren(fx):
        if f['name'] not in UEBERLAGERUNG_FAKTOREN:
            continue
        h = radix.haus_und_grenzlage(f['lon'], cusps_y)
        out.append({
            'faktor': f['name'], 'lon': f['lon'],
            'stand': stand_text(f['lon']), 'haus': h['haus'],
            'nebenhaus': h['nebenhaus'], 'grenzlage': h['grenzlage'],
            'abstand_spitze': h['abstand_spitze'],
            'fuehrend': radix.fuehrendes_haus(f['lon'], cusps_y),
            'offen': f['name'] in offen and h['grenzlage'],
            'spalte': radix.haus_spalte(f['lon'], cusps_y,
                                        offen=f['name'] in offen),
        })
    return out


# ---------------------------------------------------------------------------
# Zeitprobe
# ---------------------------------------------------------------------------

def _swe():
    try:
        import swisseph as swe
        return swe
    except ImportError:
        return None


def _achsen_bei(swe, jd, lat, lon):
    cusps, ascmc = swe.houses(jd, lat, lon, b'K')
    asc, mc = ascmc[0] % 360.0, ascmc[1] % 360.0
    return ([c % 360.0 for c in cusps[:12]],
            {'AC': asc, 'MC': mc, 'DC': (asc + 180.0) % 360.0,
             'IC': (mc + 180.0) % 360.0})


def _erster_wechsel(zustand, basis, richtung, grenze, schritt=ZEIT_SCHRITT):
    """Kleinste Minutenzahl in `richtung` (+1 spaeter, -1 frueher) bis
    `grenze`, bei der zustand(t) != basis — per Raster und Bisektion; None,
    wenn nichts kippt."""
    t_alt = 0.0
    n = int(round(grenze / schritt))
    for k in range(1, n + 1):
        t = richtung * k * schritt
        if zustand(t) != basis:
            lo, hi = t_alt, t
            for _ in range(14):
                mid = (lo + hi) / 2.0
                if zustand(mid) != basis:
                    hi = mid
                else:
                    lo = mid
            return abs(hi)
        t_alt = t
    return None


def zeitprobe(pa, pb, minuten=ZEIT_MINUTEN, offen_minuten=OFFEN_MINUTEN,
              orbs=None):
    """Was innerhalb von ±`minuten` einer der beiden Geburtszeiten kippt —
    gemeldet wird nur, was die Deutung aendert.

    Je Person X (Achsen und Hausspitzen bei jd ± t neu gerechnet; die Faktoren
    der anderen Person fest — ihr Mond laeuft in zwei Minuten rund 0,02° und
    bleibt unberuecksichtigt):
      * Ueberlagerung: Wechsel des FUEHRENDEN Hauses (Schwellenlage 2°) — fuer
        die Faktoren der anderen Person in den Haeusern von X und fuer AC und
        MC von X in den Haeusern der anderen; unter `offen_minuten` ist die
        Fuehrung offen (beide Haeuser gleich stark, wie im Geburtsbild);
      * Aspekte zwischen den Achsen von X und den Faktoren der anderen Person
        und die Achsen beider zueinander: nur der Wechsel des Zustands „eng“
        (eine enge Verbindung entsteht oder faellt weg). Spiegelzeilen (AC/DC,
        MC/IC) mit demselben Wechsel stehen als eine Zeile da.
    Grundlage der Lage bei t = 0 ist die Rechnung mit jd/lat/lon; weichen ihre
    Spitzen von den CUSPS des Datenblatts um mehr als 0,01° ab, steht das als
    ⚠ da (Fassung pruefen).

    -> {'A': {'abweichung_spitzen', 'kippt': [...]} | None, 'B': …,
        'offen': {'A': set, 'B': set} (je Haus-Eigner die Faktoren der ANDEREN
        Person, bei AC/MC auch die eigenen in den Haeusern der anderen, mit
        offener Fuehrung), 'eng_kippt': set((a, b, aspekt)) in A/B-Orientierung,
        'ueb_kippt': set((person, faktor)), 'zeilen': [str], 'warnungen': [str]}
    """
    swe = _swe()
    out = {'A': None, 'B': None, 'offen': {'A': set(), 'B': set()},
           'eng_kippt': set(), 'ueb_kippt': set(), 'zeilen': [], 'warnungen': []}
    if swe is None:
        out['warnungen'].append('Zeitprobe nicht gerechnet: pyswisseph fehlt '
                                '(lade.ephemeriden()).')
        return out
    personen = {'A': pa, 'B': pb}
    for x, y in (('A', 'B'), ('B', 'A')):
        px, py = personen[x], personen[y]
        nx = px['vorname']
        if px.get('jd') is None or px.get('lat') is None:
            out['warnungen'].append('⚠ Zeitprobe für %s nicht gerechnet: jd oder '
                                    'Koordinaten fehlen im Datenblatt — die Achsen '
                                    'lassen sich nicht gegen die Geburtsdaten halten.'
                                    % nx)
            continue
        cache = {}

        def lage_c(t, _px=px):
            k = round(t, 7)
            if k not in cache:
                cache[k] = _achsen_bei(swe, _px['jd'] + t / 1440.0, _px['lat'],
                                       _px['lon'])
            return cache[k]
        c0 = lage_c(0.0)[0]
        abw = max(abs(((c0[i] - px['cusps'][i]) + 180.0) % 360.0 - 180.0)
                  for i in range(12))
        res = {'abweichung_spitzen': abw, 'kippt': []}
        out[x] = res
        if abw > 0.01:
            out['warnungen'].append(
                '⚠ Zeitprobe %s: die aus jd und Koordinaten gerechneten Spitzen '
                'weichen bis %s von den CUSPS des Datenblatts ab — Fassung prüfen.'
                % (nx, _gr(abw)))

        def melde(eintrag, fn):
            b0 = fn(0.0)
            for rr in (-1, 1):
                m = _erster_wechsel(fn, b0, rr, minuten)
                if m is not None:
                    e = dict(eintrag, richtung='später' if rr > 0 else 'früher',
                             minuten=m, von=b0, zu=fn(rr * (m + 1e-4)))
                    res['kippt'].append(e)
        # Ueberlagerung: Faktoren von y in den Haeusern von x
        for f in _faktoren(py['factors']):
            if f['name'] not in UEBERLAGERUNG_FAKTOREN:
                continue
            melde({'was': 'überlagerung', 'faktor': f['name'], 'person': y,
                   'haus_von': x},
                  lambda t, L=f['lon']: radix.fuehrendes_haus(L, lage_c(t)[0]))
        # AC und MC von x in den Haeusern von y
        for an in ('AC', 'MC'):
            melde({'was': 'überlagerung', 'faktor': an, 'person': x, 'haus_von': y},
                  lambda t, a=an: radix.fuehrendes_haus(lage_c(t)[1][a], py['cusps']))
        # eng-Zustand: Achsen von x gegen Faktoren und Achsen von y
        for an in ACHSEN:
            for f in _faktoren(py['factors']):
                if f['name'] in ACHSEN and an not in ('AC', 'MC'):
                    continue            # Achsen zueinander: nur AC/MC der Zeitperson

                def zst(t, a=an, F=f):
                    asp = paar_aspekt(a, lage_c(t)[1][a], F['name'], F['lon'], orbs)
                    return asp['name'] if (asp and asp['eng']) else None
                melde({'was': 'eng', 'achse': an, 'achse_von': x,
                       'faktor': f['name'], 'faktor_von': y}, zst)
    # Auswertung
    for x in ('A', 'B'):
        res = out[x]
        if not res:
            continue
        for k in res['kippt']:
            if k['was'] == 'überlagerung':
                out['ueb_kippt'].add((k['person'], k['faktor']))
                if k['minuten'] < offen_minuten:
                    out['offen'][k['haus_von']].add(k['faktor'])
            else:
                asp = k['von'] or k['zu']
                if k['achse_von'] == 'A':
                    out['eng_kippt'].add((k['achse'], k['faktor'], asp))
                else:
                    out['eng_kippt'].add((k['faktor'], k['achse'], asp))
    # Zeilen (Spiegel zusammengezogen)
    for x in ('A', 'B'):
        res = out[x]
        if not res:
            continue
        nx = personen[x]['vorname']
        gesehen = set()
        for k in sorted(res['kippt'], key=lambda k: (k['minuten'], k.get('achse', ''))):
            mm = ('%.2f' % k['minuten']).replace('.', ',')
            if k['was'] == 'überlagerung':
                wer = personen[k['person']]['vorname']
                von = personen[k['haus_von']]['vorname']
                out['zeilen'].append(
                    '%s: %s (%s) in den Häusern von %s — führendes Haus %s → %s bei %s '
                    'Minuten %s Geburt von %s' % (
                        'offen' if k['minuten'] < offen_minuten else 'kippt',
                        k['faktor'], wer, von, k['von'], k['zu'], mm, k['richtung'], nx))
                continue
            schl = (frozenset((k['achse'], GEGENACHSE[k['achse']])), k['faktor'],
                    k['richtung'], round(k['minuten'], 2))
            if schl in gesehen:
                continue
            gesehen.add(schl)
            gegen = [j for j in res['kippt'] if j['was'] == 'eng' and
                     j['achse'] == GEGENACHSE[k['achse']] and j['faktor'] == k['faktor']
                     and j['richtung'] == k['richtung'] and
                     abs(j['minuten'] - k['minuten']) < 0.005]
            achse = k['achse']
            von, zu = k['von'], k['zu']
            if gegen:
                achse = 'AC/DC' if k['achse'] in ('AC', 'DC') else 'MC/IC'
                g = gegen[0]
                erst, zweit = (k, g) if k['achse'] in ('AC', 'MC') else (g, k)
                if (erst['von'] or erst['zu']) != (zweit['von'] or zweit['zu']):
                    von = erst['von'] and '%s/%s' % (erst['von'], zweit['von'])
                    zu = erst['zu'] and '%s/%s' % (erst['zu'], zweit['zu'])
                else:
                    von, zu = erst['von'], erst['zu']
            text = ('%s eng → nicht mehr eng' % von) if von else ('%s wird eng' % zu)
            out['zeilen'].append(
                'kippt: %s (%s) – %s (%s) — %s bei %s Minuten %s Geburt von %s' % (
                    achse, nx, k['faktor'], personen[k['faktor_von']]['vorname'],
                    text, mm, k['richtung'], nx))
    return out


# ---------------------------------------------------------------------------
# Verteilung und Rangzeilen
# ---------------------------------------------------------------------------

def verteilung_beider(pa, pb):
    """Elemente und Modi beider nach derselben Zaehlung: gewichtet nach
    radix.GEWICHT ueber alle Faktoren des factors-Blocks (die massgebliche
    Zaehlung des Datenblatt-Moduls, §1) und gezaehlt ueber die zehn Planeten
    (die Zaehlung der Konstellationsseite). -> {'A': {'gewichtet', 'gezaehlt'},
    'B': {...}} mit den Rueckgaben von radix.verteilung()."""
    return {k: {'gewichtet': radix.verteilung(p['factors'], gewichtet=True),
                'gezaehlt': radix.verteilung(p['factors'], nur_planeten=True)}
            for k, p in (('A', pa), ('B', pb))}


def _wettkampf(werte):
    raenge = []
    for i, w in enumerate(werte):
        raenge.append(raenge[-1] if i and w == werte[i - 1] else i + 1)
    return raenge


def _minuten(deg):
    return radix._minuten(deg)


def rangzeilen(r):
    """Die RANG-Zeilen der Beziehung (Grammatik radix.rangzeilen_lesen()).

    Schluessel: engste-zwischen-beiden, engste-zwischen-planeten,
    verbindungen-eng-<a|b>, verbindungen-alle-<a|b> (die Familien „engste-“
    und „verbindungen-“ liest rangzeilen_lesen() als Aspekt- bzw.
    Zaehlzeilen),
    ueberlagerung-<b>-in-<a>, ueberlagerung-<a>-in-<b>,
    elemente-gewichtet-<a|b>, modi-gewichtet-<a|b>, elemente-gezaehlt-<a|b>,
    modi-gezaehlt-<a|b> — <a>/<b> sind die Vornamen in Kleinbuchstaben ohne
    Umlaut. Gleiche Rangzahl heisst Gleichstand. -> Liste von Zeilen.
    """
    na, nb = r['A']['vorname'], r['B']['vorname']
    sa, sb = _slug(na), _slug(nb)
    z = r['kreuz']
    # 2026-10-11 (Auswertung der Pruefberichte vom 11.10., Teil 2, F4;
    # Pruefbericht Beziehung Design Eltern-Kind, F2): Eine Verbindung mit eng*
    # (kippt in der Zeitprobe) traegt keine Rang- oder Zaehlaussage — so sagt es
    # der ⚠-Block desselben Datenblatts. Die Zeilen „verbindungen-eng-*“ zaehlten
    # sie trotzdem mit, und ein Text stuetzte „die meisten engen Verbindungen“
    # auf eine eng*-Zeile. Jetzt zaehlen dort nur feste enge Zeilen; in den
    # Listen „engste-*“ steht bei einer solchen Zeile „eng*“ statt „eng“.
    kipp = _kipp_ids(r) if (r.get('zeit') or {}).get('eng_kippt') else set()
    zeilen = sorted(z, key=lambda x: (_minuten(x['orb']),
                                      STUFE_RANG.get(x['strength'], 9),
                                      FAKTOR_REIHE.index(x['a']),
                                      FAKTOR_REIHE.index(x['b'])))

    def _asp(e, rang):
        zus = [('eng*' if id(e) in kipp else 'eng')] if e['eng'] else []
        if e.get('spiegel'):
            zus.append('zugleich ' + e['spiegel'])
        return '%d. %s %s %s %s (%s%s)' % (
            rang, _tok(e['a'], na), e['name'], _tok(e['b'], nb), _gr(e['orb']),
            e['strength'], (', ' + ', '.join(zus)) if zus else '')

    def _liste(zz, n):
        rg = _wettkampf([_minuten(x['orb']) for x in zz])
        return [_asp(e, k) for e, k in zip(zz, rg) if k <= n]

    def _zeile(schl, menge, eintraege):
        return '- RANG %s [%s]: %s' % (schl, menge, ' · '.join(eintraege) or '—')

    n_eng = sum(1 for x in z if x['eng'])
    L = ['### Rangzeilen (Zahlen für Rang-, Zähl- und Einzigkeitsaussagen)',
         '- Wer im Text „die engste“, „die einzige“, „die meisten“ oder „x von y“ '
         'schreibt, nimmt die Zahl aus einer dieser Zeilen und sagt, welche Zählung '
         'gemeint ist. In eckigen Klammern steht die Zählmenge; gleiche Rangzahl '
         'heißt Gleichstand. Maschinenlesbar über radix.rangzeilen_lesen().']
    L.append(_zeile('engste-zwischen-beiden',
                    'Zeilen der Tabelle „Aspekte zwischen beiden“, %d Zeilen, davon %d '
                    'eng: ein Achsen-Spiegel (Konjunktion/Opposition oder Quadrat zu '
                    'beiden Enden einer Achse) ist eine Zeile, Trigon/Sextil und '
                    'Quincunx/Halbsextil zu beiden Enden sind zwei (eine Berührung, '
                    'zweimal gezählt), die Achsen zueinander '
                    'stehen eigens; Rang nach dem Orb in Bogenminuten; die ersten %d '
                    'Ränge' % (len(z), n_eng, RANG_ENGSTE), _liste(zeilen, RANG_ENGSTE)))
    pl = [x for x in zeilen if x['a'] in PLANETEN and x['b'] in PLANETEN]
    L.append(_zeile('engste-zwischen-planeten',
                    'nur Zeilen zwischen zwei der zehn klassischen Planeten, %d Zeilen; '
                    'Rang nach dem Orb in Bogenminuten; die ersten %d Ränge'
                    % (len(pl), RANG_ENGSTE_PLANETEN),
                    _liste(pl, RANG_ENGSTE_PLANETEN)))

    def _je_faktor(seite, nur_eng):
        zaehl = {}
        for x in z:
            if nur_eng and (not x['eng'] or id(x) in kipp):
                continue
            k = x[seite]
            zaehl[k] = zaehl.get(k, 0) + 1
        folge = sorted(zaehl, key=lambda k: (-zaehl[k], FAKTOR_REIHE.index(k)
                                             if k in FAKTOR_REIHE else 99))
        rg = _wettkampf([zaehl[k] for k in folge])
        return ['%d. %s %d' % (k, f, zaehl[f]) for f, k in zip(folge, rg)]
    for seite, name, slug, ander in (('a', na, sa, nb), ('b', nb, sb, na)):
        L.append(_zeile('verbindungen-eng-%s' % slug,
                        'enge Zeilen der Tabelle je Faktor von %s, gezählt; ohne '
                        'eng* (kippt in der Zeitprobe); ein Achsen-Spiegel '
                        '(Konjunktion/Opposition, Quadrat/Quadrat) zählt einmal, '
                        'Trigon/Sextil und Quincunx/Halbsextil zu beiden Enden zweimal; '
                        'Faktoren ohne enge Zeile fehlen'
                        % name, _je_faktor(seite, True)))
        L.append(_zeile('verbindungen-alle-%s' % slug,
                        'alle Zeilen der Tabelle je Faktor von %s (voll, einseitig, '
                        'Nebenaspekt), gezählt' % name, _je_faktor(seite, False)))

    def _ueb(liste, wer, haus_von):
        zaehl, traeger = {}, {}
        for u in liste:
            h = u['fuehrend']
            zaehl[h] = zaehl.get(h, 0) + 1
            traeger.setdefault(h, []).append(u['faktor'])
        summe = sum(zaehl.values())
        folge = sorted(zaehl, key=lambda h: (-zaehl[h], h))
        rg = _wettkampf([zaehl[h] for h in folge])
        return ['%d. Haus-%d %d von %d = %d %% (%s)' % (
            k, h, zaehl[h], summe, int(100.0 * zaehl[h] / summe + 0.5),
            ', '.join(traeger[h])) for h, k in zip(folge, rg)]
    L.append(_zeile('ueberlagerung-%s-in-%s' % (sb, sa),
                    'Faktoren von %s (Planeten, Mondknoten, Chiron, Lilith, Pholus, AC, '
                    'MC) je führendem Haus von %s, gezählt' % (nb, na),
                    _ueb(r['ueb_b_in_a'], nb, na)))
    L.append(_zeile('ueberlagerung-%s-in-%s' % (sa, sb),
                    'Faktoren von %s je führendem Haus von %s, gezählt' % (na, nb),
                    _ueb(r['ueb_a_in_b'], na, nb)))

    def _vt(v, feld, trfeld, namen, gew):
        summe = round(sum(v[feld].values()), 1)
        folge = sorted(namen, key=lambda k: (-v[feld][k], namen.index(k)))
        rg = _wettkampf([v[feld][k] for k in folge])
        out = []
        for k, rang in zip(folge, rg):
            tr = ', '.join(n if (not gew or radix.GEWICHT.get(n, 1.0) == 1.0)
                           else '%s ×%g' % (n, radix.GEWICHT.get(n, 1.0))
                           for n in v[trfeld][k]) or '—'
            out.append('%d. %s %g von %g = %d %% (%s)' % (
                rang, k, v[feld][k], summe,
                int(100.0 * v[feld][k] / summe + 0.5) if summe else 0, tr))
        return out
    for key, name, slug in (('A', na, sa), ('B', nb, sb)):
        vt = r['verteilung'][key]
        for art, trf, namen in (('elemente', 'traeger', radix._ELEM_NAMES),
                                ('modi', 'traeger_modus', radix._MODUS_NAMES)):
            L.append(_zeile('%s-gewichtet-%s' % (art, slug),
                            'alle Faktoren von %s nach radix.GEWICHT (Lichter und '
                            'AC/MC doppelt, Spezialfaktoren halb, DC/IC nicht); '
                            'dieselbe Zählung für beide' % name,
                            _vt(vt['gewichtet'], art, trf, list(namen), True)))
            L.append(_zeile('%s-gezaehlt-%s' % (art, slug),
                            'zehn klassische Planeten von %s, je 1' % name,
                            _vt(vt['gezaehlt'], art, trf, list(namen), False)))
    return L


# ---------------------------------------------------------------------------
# Die ganze Rechnung
# ---------------------------------------------------------------------------

def _heute_berlin():
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.now(ZoneInfo('Europe/Berlin')).date()
    except Exception:                        # pragma: no cover
        return datetime.date.today()


def _ut_aus_jd(jd):
    """'HH:MM' (UT) aus einem julianischen Datum — fuer den Fassungsabgleich."""
    f = (jd + 0.5) % 1.0
    minuten = int(round(f * 1440.0)) % 1440
    return '%02d:%02d' % (minuten // 60, minuten % 60)


def rechnung(a_pfad, b_pfad, art, datum=None, eltern='A', beziehung=None,
             einwilligung=None, sprache='deutsch', auftrag_zeit=None,
             grundlage=None, orbs=None):
    """Die ganze Rechnung des Beziehungshoroskops — ohne Deutung.

    a_pfad, b_pfad  Datenblaetter: A = bestellende Person, B = zweite Person.
    art             'paar' | 'eltern-kind' | 'freundschaft' (seit 2026-10-14c;
                    Gross/klein egal).
    datum           Tag von Chat 1 (datetime.date oder 'JJJJ-MM-TT'); Vorgabe
                    heute in Berlin. Alter heute richten sich danach.
    eltern          bei Eltern-Kind: 'A' (Vorgabe: der Elternteil bestellt) oder
                    'B' (ein erwachsenes Kind bestellt; der Elternteil steht dann
                    in der dritten Person).
    beziehung, einwilligung, sprache  Wortlaute aus dem Auftrag.
    auftrag_zeit    {'A': 'HH:MM', 'B': 'HH:MM'}, nur wenn der Auftrag Geburtszeiten
                    nennt — Fassungsabgleich gegen den Kopf der Datenblaetter.
    grundlage       {'A': '…', 'B': '…'} optional: Vermerk, dass ein Datenblatt nur als
                    Grundlage dieses Beziehungshoroskops entstanden ist.

    Haelt an (BeziehungFehler): unbekannte Art; Paar oder Freundschaft mit einer
    Person unter 18; Eltern-Kind, in dem ein Kind unter 18 selbst bestellt.

    -> dict mit 'art', 'datum', 'A', 'B' (lies_datenblatt + 'alter'),
       'kreuz', 'achsen', 'ueb_b_in_a', 'ueb_a_in_b', 'zeit' (zeitprobe),
       'verteilung', 'rang' (Zeilen), 'warnungen', 'anhalten' (Liste),
       'kind' ('A'|'B'|None), 'kind_minderjaehrig' (bool), 'auftrag' (dict).
    """
    art = (art or '').strip().lower().replace(' ', '-')
    if art not in ARTEN:
        raise BeziehungFehler('Art „%s“ unbekannt — erlaubt: %s.'
                              % (art, ', '.join(ART_TITEL[x] for x in ARTEN)))
    if datum is None:
        datum = _heute_berlin()
    elif isinstance(datum, str):
        datum = datetime.date.fromisoformat(datum)
    pa, pb = lies_datenblatt(a_pfad), lies_datenblatt(b_pfad)
    for p in (pa, pb):
        p['alter'] = alter_am(p['geburtsdatum'], datum)
    r = {'art': art, 'datum': datum, 'A': pa, 'B': pb, 'warnungen': [],
         'anhalten': [], 'kind': None, 'kind_minderjaehrig': False,
         'auftrag': {'beziehung': beziehung or 'nicht angegeben',
                     'einwilligung': einwilligung or 'nicht angegeben',
                     'sprache': sprache, 'eltern': eltern,
                     'grundlage': grundlage or {}}}
    # 2026-10-14 (F2, Chris-Entscheidung 14.10.): ohne jd und Koordinaten fiele die
    # Zeitprobe still aus — anhalten statt ⚠-Zeile.
    for p in (pa, pb):
        if p['jd'] is None or p['lat'] is None or p['lon'] is None:
            r['anhalten'].append(
                '%s: julianisches Datum oder Koordinaten im Datenblatt nicht lesbar — '
                'ohne sie fällt die Zwei-Minuten-Prüfung aus. Chris fragen: vorher Schritt 1 '
                'des Geburtshoroskops für %s (ohne Aufpreis) oder die Werte im Kopf '
                'nachtragen.' % (p['vorname'], p['vorname']))
    # 2026-10-14 (F2, Chris-Entscheidung 14.10.): ohne Themenzeile mit leitachse=ja
    # fehlt dem Strukturvergleich das eigene Geburtsbild — anhalten statt leer.
    for p in (pa, pb):
        if p['leitachse'] is None:
            r['anhalten'].append(
                '%s: Datenblatt ohne Leitachse (keine Themenzeile mit leitachse=ja) — '
                'dem Strukturvergleich fehlt das eigene Geburtsbild. Chris fragen: vorher '
                'Schritt 1 des Geburtshoroskops für %s (ohne Aufpreis).'
                % (p['vorname'], p['vorname']))
    # 2026-10-15 (FFU, Auswertung 14.10. d, Punkt 2): ohne lesbaren Vornamen stuende „?“
    # in Kopf, Tabellen und Belegen — anhalten statt still weiter.
    for p in (pa, pb):
        if p['vorname'] == '?':
            r['anhalten'].append(
                '%s: kein Vorname lesbar — weder in der H1 noch im Namensfeld noch im '
                'Dateinamen (`<Vorname>_chart_data.md`). Chris fragen.' % p['datei'])
    if pa['vorname'] == pb['vorname']:
        r['anhalten'].append('Beide Datenblätter tragen denselben Vornamen „%s“ — '
                             'die Zuordnung in Belegen und Tabellen wäre '
                             'mehrdeutig.' % pa['vorname'])
    # Leseprobe 2026-10-11: eine unaufgeraeumte Vorlagenzeile traegt wörtlich
    # „liegt vor“ — sie gilt als nicht vermerkt (Modul, „Der Auftrag“).
    ew = (einwilligung or '').strip()
    if not ew or ew.lower() == 'nicht angegeben' or re.search(r'[|<\[]', ew):
        r['anhalten'].append('Einwilligung nicht vermerkt (leer oder Vorlagenzeile mit '
                             'mehreren Werten) — ohne Vermerk wird nichts geschrieben.')
    if art in IHR_ARTEN:
        # 2026-10-14c: Freundschaft wie das Paar nur mit zwei Erwachsenen (Chris 14.10.)
        for p in (pa, pb):
            if p['alter'] is None:
                r['anhalten'].append('%s: kein Geburtsdatum im Datenblatt — %s '
                                     'braucht zwei Erwachsene.'
                                     % (p['vorname'], 'das Paar' if art == 'paar'
                                        else 'die Freundschaft'))
            elif p['alter'] < ERWACHSEN:
                raise BeziehungFehler('%s nur mit zwei Erwachsenen: %s ist %d.'
                                      % (ART_TITEL[art], p['vorname'], p['alter']))
    else:
        if eltern not in ('A', 'B'):
            raise BeziehungFehler("eltern='A' oder 'B'.")
        kind = 'B' if eltern == 'A' else 'A'
        r['kind'] = kind
        ge, gk = r[eltern]['geburtsdatum'], r[kind]['geburtsdatum']
        if ge and gk and ge >= gk:
            # Leseprobe 2026-10-11: ein vertauschter Elternteil vertauscht
            # Mond-Schnitte und Elternachse — der Elternteil ist der Ältere.
            r['anhalten'].append('Elternteil %s ist nicht älter als %s — Zeile '
                                 '„Elternteil“ prüfen.' % (r[eltern]['vorname'],
                                                            r[kind]['vorname']))
        alt = r[kind]['alter']
        r['kind_minderjaehrig'] = alt is not None and alt < ERWACHSEN
        if kind == 'A' and r['kind_minderjaehrig']:
            raise BeziehungFehler('Ein Kind unter 18 bestellt nicht selbst — die '
                                  'Sorgeberechtigten bestellen, der Elternteil ist A.')
        if alt is None:
            r['anhalten'].append('Kind ohne Geburtsdatum im Datenblatt — ob die '
                                 'Regeln für unter 18 gelten, ist offen.')
    # Fassungsabgleich
    for k, p in (('A', pa), ('B', pb)):
        if p['jd'] is not None:
            ut = _ut_aus_jd(p['jd'])
            m = re.search(r'(\d{1,2}):(\d{2})\s*UT|UT\s*(\d{1,2}):(\d{2})',
                          p['geburtszeit'])
            if m:
                hh, mm = (m.group(1), m.group(2)) if m.group(1) else (m.group(3),
                                                                       m.group(4))
                if '%02d:%s' % (int(hh), mm) != ut:
                    r['anhalten'].append(
                        '%s: Geburtszeit im Kopf (%s UT) und julianisches Datum '
                        '(%s UT) widersprechen sich.' % (p['vorname'],
                                                         '%s:%s' % (hh, mm), ut))
        if auftrag_zeit and auftrag_zeit.get(k):
            soll = auftrag_zeit[k].strip()
            if soll not in p['geburtszeit']:
                r['anhalten'].append(
                    '%s: Der Auftrag nennt die Geburtszeit %s, das Datenblatt „%s“ '
                    '— anhalten und fragen.' % (p['vorname'], soll, p['geburtszeit']))
        for h in p['hinweise']:
            r['warnungen'].append('%s: %s' % (p['vorname'], h))
    r['kreuz'] = kreuzaspekte(pa['factors'], pb['factors'], orbs)
    r['achsen'] = achsenkontakte(pa['factors'], pb['factors'])
    r['zeit'] = zeitprobe(pa, pb, orbs=orbs)
    r['warnungen'] += r['zeit']['warnungen']
    r['ueb_b_in_a'] = ueberlagerung(pb['factors'], pa['cusps'],
                                    offen=r['zeit']['offen']['A'])
    r['ueb_a_in_b'] = ueberlagerung(pa['factors'], pb['cusps'],
                                    offen=r['zeit']['offen']['B'])
    r['verteilung'] = verteilung_beider(pa, pb)
    r['rang'] = rangzeilen(r)
    return r


# ---------------------------------------------------------------------------
# Datenblatt der Beziehung schreiben
# ---------------------------------------------------------------------------

def _anrede(r):
    na, nb = r['A']['vorname'], r['B']['vorname']
    if r['art'] in IHR_ARTEN:
        return ('%s — beide sind Leser: „ihr“; Sätze über einen von beiden nennen ihn '
                'beim Namen' % ART_TITEL[r['art']])
    eltern = r['auftrag']['eltern']
    kind = nb if eltern == 'A' else na
    elternteil = na if eltern == 'A' else nb
    if eltern == 'A':
        return ('Eltern-Kind — %s (Elternteil) ist „du“, %s (Kind) steht in der '
                'dritten Person' % (elternteil, kind))
    return ('Eltern-Kind — %s (Kind, erwachsen) ist „du“, %s (Elternteil) steht in '
            'der dritten Person' % (kind, elternteil))


def _kipp_ids(r):
    """ids der Tabellenzeilen, deren Zustand „eng“ in der Zeitprobe kippt."""
    idx = _kreuz_index(r)
    out = set()
    for k in (r.get('zeit') or {}).get('eng_kippt', ()):
        e = idx.get(k)
        if e is not None:
            out.add(id(e))
    return out


def eng_text(e, kipp_ids=()):
    """'eng', 'eng*' (kippt in der Zeitprobe), '(eng*)' (wird dort eng) oder ''."""
    if id(e) in kipp_ids:
        return 'eng*' if e['eng'] else '(eng*)'
    return 'eng' if e['eng'] else ''


def _aspekt_zeile_md(e, na, nb, kipp_ids=()):
    zus = []
    if e.get('spiegel'):
        zus.append('zugleich ' + e['spiegel'])
    return '| %s | %s %s | %s | %s | %s |' % (
        _faktor_beleg(e['a']), e['name'], ASPEKT_GLYPHE.get(e['name'], ''),
        _faktor_beleg(e['b']) + ((' (' + ', '.join(zus) + ')') if zus else ''),
        _gr(e['orb']), eng_text(e, kipp_ids))


def _schwaechstes_element(v):
    """Schwaechstes Element (gewichtet) aus einem Verteilungs-dict; bei Gleichstand
    alle am Ende der Rangfolge mit „gleichauf“ (2026-10-14b, Auswertung 14.10. c, F4:
    radix nimmt bei Gleichstand das erste — im Datenblatt eine falsche Einzigkeit)."""
    el = v['gewichtet']['elemente']
    tief = min(el[n] for n in radix._ELEM_NAMES)
    alle = [n for n in radix._ELEM_NAMES if el[n] == tief]
    return (' und '.join(alle) + ' gleichauf') if len(alle) > 1 else alle[0]


def rechnung_text(r):
    """Die gerechneten Abschnitte des Datenblatts der Beziehung (Markdown) —
    ⚠-Hinweise, Kopf, Staende, Spitzen, Aspekte zwischen beiden, Achsen
    zueinander, Ueberlagerung, Zeitprobe, Strukturvergleich, Kernanlagen und
    Leitachsen, Rangzeilen. Ohne Themenliste, Ressourcen, @@SELEKTOR und
    @@DECKBLATT (die baut datenblatt())."""
    pa, pb = r['A'], r['B']
    na, nb = pa['vorname'], pb['vorname']
    L = ['# Datenblatt der Beziehung — %s und %s' % (na, nb), '']
    L.append('## ⚠ Hinweise')
    L.append('')
    if r['anhalten']:
        for a in r['anhalten']:
            L.append('- **ANHALTEN:** %s' % a)
    else:
        L.append('- Anhalten: keine Stelle (Fassungsabgleich ohne Widerspruch).')
    for w in r['warnungen']:
        L.append('- %s' % w)
    zt = r['zeit']
    kipp_ids = _kipp_ids(r)
    if zt['zeilen']:
        n_eng = sum(1 for e in r['kreuz'] + r['achsen'] if id(e) in kipp_ids and e['eng'])
        n_neu = sum(1 for e in r['kreuz'] + r['achsen'] if id(e) in kipp_ids and not e['eng'])
        L.append('- Zeitprobe (±%d Minuten): %d enge Verbindung(en) verlieren „eng“ '
                 '(eng*), %d werden eng ((eng*)), %d Überlagerung(en) wechseln das '
                 'führende Haus — s. Abschnitt „Zeitprobe“. Eine Verbindung mit eng* '
                 'führt kein Thema und trägt keine Rang- oder Einzigkeitsaussage.'
                 % (ZEIT_MINUTEN, n_eng, n_neu, len(zt['ueb_kippt'])))
    else:
        L.append('- Zeitprobe (±%d Minuten): nichts kippt.' % ZEIT_MINUTEN)
    offen = sorted(['%s (%s) in den Häusern von %s' % (f, nb, na)
                    for f in zt['offen']['A']] +
                   ['%s (%s) in den Häusern von %s' % (f, na, nb)
                    for f in zt['offen']['B']])
    if offen:
        L.append('- ⚠ Führung offen (beide Häuser gleich stark): ' + '; '.join(offen))
    L.append('')
    L.append('## Kopf')
    L.append('')
    L.append('- %s: %s und %s' % (DOKUMENTTYP[r['art']], na, nb))
    L.append('- Art: %s' % ART_TITEL[r['art']])
    L.append('- Bestellt von: %s · Anrede: %s' % (na, _anrede(r)))
    if r['art'] == 'eltern-kind':
        kind = r[r['kind']]
        L.append('- Kind: %s, %s — %s' % (
            kind['vorname'], ('%d Jahre' % kind['alter']) if kind['alter'] is not None
            else 'Alter nicht angegeben',
            'unter 18: Regeln für ein minderjähriges Kind (Modul)'
            if r['kind_minderjaehrig'] else 'volljährig'))
    L.append('- Beziehung aus dem Auftrag: %s' % r['auftrag']['beziehung'])
    L.append('- Einwilligung: %s' % r['auftrag']['einwilligung'])
    L.append('- Sprache: %s' % r['auftrag']['sprache'])
    L.append('- Tag der Erstellung: %s' % r['datum'].strftime('%d.%m.%Y'))
    L.append('- Orbis: Huber-Radix-Orbis (radix.ASPEKT_ORB), Einzelseiten-Prüfung wie '
             'im Geburtsbild; eng = innerhalb des halben vollen Orbis (Chris-'
             'Entscheidung 2026-10-11); die Tabellen zeigen alle, die Deutung stützt '
             'sich auf die engen.')
    for k, p in (('A', pa), ('B', pb)):
        L.append('')
        L.append('### %s' % p['vorname'])
        L.append('')
        L.append('- Geschlecht: %s' % (p['geschlecht'] or 'nicht angegeben'))
        L.append('- Geburtsdatum: %s' % (p['geburtsdatum'].strftime('%d.%m.%Y')
                                         if p['geburtsdatum'] else 'nicht angegeben'))
        L.append('- Geburtszeit (Kopf ihres Datenblatts, wörtlich): %s' % p['geburtszeit'])
        L.append('- Geburtsort: %s' % p['geburtsort'])
        L.append('- Alter heute (%s): %s' % (
            r['datum'].strftime('%d.%m.%Y'),
            ('%d Jahre' % p['alter']) if p['alter'] is not None else 'nicht angegeben'))
        L.append('- Fassung (wörtlich): %s' % p['fassung'])
        L.append('- Zeitunsicherheit (wörtlich): %s' % p['zeitunsicherheit'])
        L.append('- Datenblatt: %s (SHA-1 %s)%s' % (
            p['datei'], p['sha8'],
            (' — ' + r['auftrag']['grundlage'][k]) if r['auftrag']['grundlage'].get(k)
            else ''))
        if p['kinder_baustein']:
            L.append('- Ihr Datenblatt trägt einen Kinder-Baustein; er gilt für ihr '
                     'eigenes Horoskop, nicht für dieses (Modul Beziehung).')
    # Staende
    L.append('')
    L.append('## Stände')
    for k, p, ueb, ander in (('A', pa, r['ueb_a_in_b'], pb),
                             ('B', pb, r['ueb_b_in_a'], pa)):
        L.append('')
        L.append('### %s' % p['vorname'])
        L.append('')
        L.append('| Faktor | Stand | Zeichen | Haus | Lauf | Haus bei %s |'
                 % ander['vorname'])
        L.append('|---|---|---|---|---|---|')
        ub = {u['faktor']: u for u in ueb}
        for f in _faktoren(p['factors']):
            n = f['name']
            if n in ACHSEN:
                haus = radix.haus_und_grenzlage(f['lon'], p['cusps'], name=n)['haus']
                lauf = '—'
            else:
                haus = _haus_eigen(p, n, f['lon'])
                lauf = 'rückläufig' if f.get('retro') else 'direkt'
            L.append('| %s | %s | %s | %s | %s | %s |' % (
                n, radix.gr_zeichen(f['lon']), zeichen_von(f['lon']), haus, lauf,
                ub[n]['spalte'] if n in ub else '—'))
    L.append('')
    L.append('## Hausspitzen (Koch)')
    L.append('')
    L.append('| Haus | %s | %s |' % (na, nb))
    L.append('|---|---|---|')
    for i in range(12):
        L.append('| %d | %s | %s |' % (i + 1, stand_text(pa['cusps'][i]),
                                      stand_text(pb['cusps'][i])))
    # Aspekte zwischen beiden
    z = r['kreuz']
    L.append('')
    L.append('## Aspekte zwischen beiden')
    L.append('')
    L.append('Linke Spalte %s, rechte Spalte %s. %d Verbindungen, davon %d eng. Ein '
             'Achsen-Spiegel (Konjunktion/Opposition oder Quadrat zu beiden Enden einer '
             'Achse) ist eine Zeile; Trigon/Sextil und Quincunx/Halbsextil zu beiden Enden '
             'stehen als zwei Zeilen — eine Berührung der Achse, zweimal gezählt.'
             % (na, nb, len(z), sum(1 for x in z if x['eng'])))
    for st in ('voll', 'einseitig', 'neben'):
        grp = [x for x in z if x['strength'] == st]
        L.append('')
        L.append('### %s (%d, davon %d eng)' % (STUFE_TITEL[st], len(grp),
                                                sum(1 for x in grp if x['eng'])))
        L.append('')
        if not grp:
            L.append('keine')
            continue
        L.append('| %s | Aspekt | %s | Orb | eng |' % (na, nb))
        L.append('|---|---|---|---|---|')
        for e in grp:
            L.append(_aspekt_zeile_md(e, na, nb, kipp_ids))
    L.append('')
    L.append('### Achsen zueinander (%d)' % len(r['achsen']))
    L.append('')
    if r['achsen']:
        L.append('| %s | Aspekt | %s | Orb | Stufe | eng |' % (na, nb))
        L.append('|---|---|---|---|---|---|')
        for e in r['achsen']:
            L.append('| %s | %s %s | %s%s | %s | %s | %s |' % (
                ACHSEN_LANG[e['a']], e['name'], ASPEKT_GLYPHE.get(e['name'], ''),
                ACHSEN_LANG[e['b']],
                (' (zugleich %s)' % e['spiegel']) if e.get('spiegel') else '',
                _gr(e['orb']), e['strength'], eng_text(e, kipp_ids)))
    else:
        L.append('keine')
    if kipp_ids:
        L.append('')
        L.append('eng* = eng, verliert das „eng“ innerhalb der Zeitprobe; (eng*) = nicht '
                 'eng, wird es dort (Abschnitt „Zeitprobe“).')
    # Ueberlagerung
    L.append('')
    L.append('## Überlagerung')
    for liste, wer, von in ((r['ueb_b_in_a'], nb, na), (r['ueb_a_in_b'], na, nb)):
        L.append('')
        L.append('### %s in den Häusern von %s' % (wer, von))
        L.append('')
        L.append('| Faktor | Stand | Haus | Lage |')
        L.append('|---|---|---|---|')
        for u in liste:
            if u['offen']:
                lage = 'Führung offen: %d und %d gleich stark' % (u['haus'], u['nebenhaus'])
            elif u['grenzlage'] and u['fuehrend'] != u['haus']:
                lage = 'Schwellenlage: %s vor Spitze %d, Haus %d führt' % (
                    _gr(u['abstand_spitze']), u['nebenhaus'], u['nebenhaus'])
            elif u['grenzlage']:
                lage = 'Grenzlage: %s vor Spitze %d, Haus %d führt, %d klingt mit' % (
                    _gr(u['abstand_spitze']), u['nebenhaus'], u['haus'], u['nebenhaus'])
            else:
                lage = '—'
            if not u['offen'] and ((('B' if wer == nb else 'A'), u['faktor'])
                                   in zt.get('ueb_kippt', ())):
                lage += ' · führendes Haus kippt in der Zeitprobe'
            L.append('| %s | %s | %s | %s |' % (u['faktor'], u['stand'], u['spalte'],
                                                lage))
    # Zeitprobe
    L.append('')
    L.append('## Zeitprobe')
    L.append('')
    L.append('- Schwelle: ±%d Minuten je Geburtszeit (radix.KIPP_SCHWELLE); offene '
             'Führung unter %d Minute (radix.FUEHRUNG_OFFEN). Gerechnet werden '
             'Achsen und Spitzen der Person, deren Zeit schwankt; die Faktoren der '
             'anderen gelten als fest.' % (ZEIT_MINUTEN, OFFEN_MINUTEN))
    for k, p in (('A', pa), ('B', pb)):
        res = zt[k]
        if res is None:
            L.append('- %s: nicht gerechnet.' % p['vorname'])
        else:
            L.append('- %s: Spitzen aus jd und Koordinaten gegen CUSPS des '
                     'Datenblatts: größte Abweichung %s.' % (
                         p['vorname'], _gr(res['abweichung_spitzen'])))
    if zt['zeilen']:
        for zz in zt['zeilen']:
            L.append('- %s' % zz)
    else:
        L.append('- Nichts kippt innerhalb der Schwelle.')
    # Strukturvergleich
    L.append('')
    L.append('## Strukturvergleich')
    L.append('')
    L.append('### Elemente und Modi (dieselbe Zählung für beide)')
    L.append('')
    va, vb = r['verteilung']['A'], r['verteilung']['B']
    L.append('| | %s gewichtet | %s gewichtet | %s gezählt | %s gezählt |'
             % (na, nb, na, nb))
    L.append('|---|---|---|---|---|')
    for feld, namen in (('elemente', radix._ELEM_NAMES), ('modi', radix._MODUS_NAMES)):
        for n in namen:
            L.append('| %s | %g | %g | %g | %g |' % (
                n, va['gewichtet'][feld][n], vb['gewichtet'][feld][n],
                va['gezaehlt'][feld][n], vb['gezaehlt'][feld][n]))
    L.append('')
    L.append('Gewichtet: alle Faktoren nach radix.GEWICHT; gezählt: zehn klassische '
             'Planeten, je 1. Schwächstes Element gewichtet: %s %s, %s %s.' % (
                 na, _schwaechstes_element(va), nb, _schwaechstes_element(vb)))
    L.append('')
    L.append('### Kernanlagen und Leitachsen')
    L.append('')
    for p in (pa, pb):
        fx = {f['name']: f for f in p['factors']}
        teile = []
        for n in ('Sonne', 'Mond'):
            teile.append('%s %s, Haus %s' % (n, stand_text(fx[n]['lon']),
                                            _haus_eigen(p, n, fx[n]['lon'])))
        for n in ('AC', 'MC'):
            teile.append('%s %s' % (n, stand_text(fx[n]['lon'])))
        L.append('- %s: %s' % (p['vorname'], ' · '.join(teile)))
        L.append('  - Leitachse ihres Datenblatts: %s' % (
            p['leitachse'] or 'keine Themenzeile mit leitachse=ja'))
    L.append('')
    L += r['rang']
    return '\n'.join(L) + '\n'


# --- Themenliste der Beziehung (vom Lauf geschrieben) -----------------------

_FNAME = r'(?:Sonne|Mond|Merkur|Venus|Mars|Jupiter|Saturn|Uranus|Neptun|Pluto|' \
         r'Mondknoten|Chiron|Lilith|Pholus|AC|MC|DC|IC)'
ASP_TOKEN_RE = re.compile(
    r'(?P<fa>' + _FNAME + r') \((?P<pa>[^()]+)\) (?P<g>[☌☍□△⚹⚻⚺]) '
    r'(?P<fb>' + _FNAME + r') \((?P<pb>[^()]+)\)')
UEB_TOKEN_RE = re.compile(
    r'(?P<f>' + _FNAME + r') \((?P<p>[^()]+)\) in Haus (?P<h>\d{1,2})'
    r'(?:[/=](?P<h2>\d{1,2}))? von (?P<q>[^\s,|]+)')


def _tok_schluessel(tok):
    """Ungeordneter Schluessel eines Verbindungs-Tokens — beide Faktoren samt
    Person und die Aspektglyphe — oder None (2026-10-14b)."""
    m = ASP_TOKEN_RE.fullmatch((tok or '').strip())
    if not m:
        return None
    return (frozenset({(m.group('fa'), m.group('pa').strip()),
                       (m.group('fb'), m.group('pb').strip())}), m.group('g'))


def lies_themen(text):
    """Liest die Themenliste der Beziehung (Abschnitt „## Themenliste der
    Beziehung“, Bloecke `THEMA n | titel=…` mit Feldern `| key=value`) und den
    Abschnitt „### Ohne Deutungs-Heimat“.

    -> {'themen': [{'nr', 'titel', 'fuehrt', 'aspekte' (Liste roher Tokens),
       'ueberlagerung', 'verweis', 'seite', 'form', 'praxis', 'leitachse'
       (bool), 'roh'}], 'ohne': [Zeilen], 'fehler': [str]}
    """
    out = {'themen': [], 'ohne': [], 'fehler': []}
    th = _abschnitt(text, r'Themenliste der Beziehung')
    if not th.strip():
        out['fehler'].append('kein Abschnitt „## Themenliste der Beziehung“')
        return out
    teile = re.split(r'\n(?=THEMA \d+\s*\|)', '\n' + th)
    for blk in teile:
        blk = blk.strip()
        if not blk.startswith('THEMA'):
            continue
        kopf = blk.split('\n### ', 1)[0]
        felder = {}
        for m in re.finditer(r'\|\s*([a-z]+)\s*=\s*([^|\n]*(?:\n(?!\s*\|)[^|\n]*)*)',
                             kopf):
            felder[m.group(1)] = m.group(2).strip()
        nr = int(re.match(r'THEMA (\d+)', blk).group(1))
        t = {'nr': nr, 'titel': felder.get('titel', ''),
             'fuehrt': felder.get('fuehrt', ''),
             'aspekte': [x.strip() for x in felder.get('aspekte', '').split(',')
                         if x.strip()],
             'ueberlagerung': [x.strip() for x in
                               felder.get('ueberlagerung', '').split(',') if x.strip()],
             'verweis': felder.get('verweis', ''),
             'seite': felder.get('seite', ''), 'form': felder.get('form', 'voll'),
             'praxis': felder.get('praxis', ''),
             'leitachse': felder.get('leitachse', '').lower() == 'ja',
             'roh': blk}
        # 2026-10-14b (Auswertung 14.10. c, F5): Die fuehrende Verbindung hat ihren Ort
        # im eigenen Thema — fehlt sie in aspekte=, zaehlt sie dort mit. Vorher meldete
        # die Heimat-Probe sie „ohne Ort“, und eine harmonische lief still in den
        # Ressourcen-Block mit Deutungsort „Was trägt“.
        kf = _tok_schluessel(t['fuehrt'])
        if kf and not any(_tok_schluessel(x) == kf for x in t['aspekte']):
            t['aspekte'].insert(0, t['fuehrt'].strip())
        out['themen'].append(t)
    m = re.search(r'^### Ohne Deutungs-Heimat[^\n]*\n(.*?)(?=^## |^### |^@@|\Z)', th,
                  re.M | re.S)
    if m:
        out['ohne'] = [z.strip()[2:].strip() for z in m.group(1).splitlines()
                       if z.strip().startswith('- ')]
    nrs = [t['nr'] for t in out['themen']]
    if nrs != list(range(1, len(nrs) + 1)):
        out['fehler'].append('THEMA-Nummern nicht lückenlos ab 1: %s' % nrs)
    if sum(1 for t in out['themen'] if t['leitachse']) != 1:
        out['fehler'].append('genau ein Thema braucht leitachse=ja')
    return out


def _asp_schluessel(fa, pa, fb, pb, na, nb, aspekt):
    """Ungeordneter Schluessel eines Kreuzaspekts: (Faktor A, Faktor B, Art)
    mit A/B nach Person."""
    if pa == na and pb == nb:
        return (fa, fb, aspekt)
    if pa == nb and pb == na:
        return (fb, fa, aspekt)
    return None


def _kreuz_index(r):
    """Schluessel -> Zeile, inkl. der Spiegel-Schreibweise (Faktor zur
    Gegenachse mit dem Spiegelaspekt) und der Achsenkontakte."""
    idx = {}
    for e in r['kreuz'] + r['achsen']:
        idx[(e['a'], e['b'], e['name'])] = e
        if e.get('spiegel'):
            asp, ax = e['spiegel'].split(' ', 1)
            if e.get('spiegel_seite') == 'a':
                idx[(ax, e['b'], asp)] = e
            else:
                idx[(e['a'], ax, asp)] = e
    return idx


def _ressourcen(r, themen):
    """Harmonische (Konjunktion, Trigon, Sextil) ENGE Kreuzaspekte mit einem
    Kernfaktor (Sonne, Mond, Merkur, Venus, Mars, AC, MC) auf mindestens einer
    Seite — ohne die Achsen zueinander (sie sind Struktur, Getriebe-Kapitel);
    Deutungsort: das Thema, in dessen aspekte= er steht, sonst „Was trägt“."""
    na, nb = r['A']['vorname'], r['B']['vorname']
    heim = {}
    for t in themen:
        for tok in t['aspekte']:
            m = ASP_TOKEN_RE.fullmatch(tok)
            if not m:
                continue
            k = _asp_schluessel(m.group('fa'), m.group('pa'), m.group('fb'),
                                m.group('pb'), na, nb,
                                GLYPHE_ASPEKT.get(m.group('g')))
            if k:
                heim.setdefault(k, []).append(t['nr'])
    idx = _kreuz_index(r)
    out = []
    for e in r['kreuz']:
        if not e['eng'] or e['name'] not in HARMONISCH:
            continue
        if e['a'] not in KERN and e['b'] not in KERN:
            continue
        orte = []
        for k, v in heim.items():
            if idx.get(k) is e:
                orte += v
        out.append({'zeile': e, 'deutungsort':
                    ('Thema %s' % ', '.join(str(x) for x in sorted(set(orte))))
                    if orte else 'Was trägt'})
    return out


def _ressourcen_text(r, res):
    na, nb = r['A']['vorname'], r['B']['vorname']
    L = ['## Ressourcen der Beziehung', '',
         'Zählmenge: jede ENGE Verbindung der Art Konjunktion, Trigon oder Sextil mit '
         'Sonne, Mond, Merkur, Venus, Mars, AC oder MC auf mindestens einer Seite, ohne '
         'die Achsen zueinander. '
         'Deutungsort: das Thema, in dessen aspekte= sie steht, sonst das Kapitel '
         '„Was trägt“ (gebaut, nicht von Hand).', '']
    if not res:
        L.append('keine')
    for x in res:
        e = x['zeile']
        L.append('- %s %s %s %s · %s · %s%s — Deutungsort: %s' % (
            _mit(e['a'], na), e['name'], ASPEKT_GLYPHE.get(e['name'], ''),
            _mit(e['b'], nb), _gr(e['orb']), e['strength'],
            (', zugleich %s' % e['spiegel']) if e.get('spiegel') else '',
            x['deutungsort']))
    return '\n'.join(L) + '\n'


def _maschinenblock(r):
    def _fl(fx):
        return '[\n' + ''.join("    {'name': %r, 'glyph': %r, 'lon': %.6f, 'retro': %r},\n"
                               % (f['name'], f.get('glyph') or _fglyph(f['name']),
                                  f['lon'], bool(f.get('retro')))
                               for f in _faktoren(fx)) + ']'
    pa, pb = r['A'], r['B']

    def _p(p):
        return {'vorname': p['vorname'], 'datei': p['datei'], 'sha8': p['sha8'],
                'geschlecht': p['geschlecht'], 'alter': p['alter'],
                'jd': p['jd'], 'lat': p['lat'], 'lon': p['lon'],
                # 2026-10-15: fuer die Staendeseite in Chat 2 (lies_beziehung)
                'offen_eigen': sorted(p.get('offen_eigen') or ())}
    offen = {'A': sorted(r['zeit']['offen']['A']), 'B': sorted(r['zeit']['offen']['B'])}
    eng_k = sorted(r['zeit'].get('eng_kippt', ()))
    ueb_k = sorted(r['zeit'].get('ueb_kippt', ()))
    return ('## Maschinenlesbar (beziehung.lies_beziehung)\n\n```python\n'
            'ART = %r\nELTERN = %r\nKIND_MINDERJAEHRIG = %r\nDATUM = %r\n'
            'PERSON_A = %r\nPERSON_B = %r\nOFFEN = %r\nENG_KIPPT = %r\nUEB_KIPPT = %r\n'
            'FACTORS_A = %s\nCUSPS_A = %r\nFACTORS_B = %s\nCUSPS_B = %r\n```\n'
            % (r['art'], r['auftrag']['eltern'] if r['art'] == 'eltern-kind' else None,
               r['kind_minderjaehrig'], r['datum'].isoformat(), _p(pa), _p(pb), offen,
               eng_k, ueb_k,
               _fl(pa['factors']), [round(c, 6) for c in pa['cusps']],
               _fl(pb['factors']), [round(c, 6) for c in pb['cusps']]))


def _selektor_block(r, themen, res):
    na, nb = r['A']['vorname'], r['B']['vorname']
    L = ['@@SELEKTOR', 'ART %s' % r['art'], 'PERSON A %s' % na, 'PERSON B %s' % nb]
    gesehen = set()
    idx = _kreuz_index(r)
    for t in themen:
        for tok in [t['fuehrt']] + t['aspekte']:
            m = ASP_TOKEN_RE.fullmatch(tok.strip()) if tok else None
            if not m:
                continue
            k = _asp_schluessel(m.group('fa'), m.group('pa'), m.group('fb'),
                                m.group('pb'), na, nb, GLYPHE_ASPEKT.get(m.group('g')))
            e = idx.get(k) if k else None
            if e is None or id(e) in gesehen:
                continue
            gesehen.add(id(e))
            L.append('PAAR %s %s aspekt=%s stufe=%s eng=%s herkunft=Thema-%d' % (
                e['a'], e['b'], e['name'], e['strength'], 'ja' if e['eng'] else 'nein',
                t['nr']))
    for x in res:
        e = x['zeile']
        if id(e) in gesehen:
            continue
        gesehen.add(id(e))
        L.append('PAAR %s %s aspekt=%s stufe=%s eng=%s herkunft=Was-trägt' % (
            e['a'], e['b'], e['name'], e['strength'], 'ja' if e['eng'] else 'nein'))
    for e in r['achsen']:
        if not e['eng'] or id(e) in gesehen:
            continue
        gesehen.add(id(e))
        L.append('PAAR %s %s aspekt=%s stufe=%s eng=ja herkunft=Getriebe' % (
            e['a'], e['b'], e['name'], e['strength']))
    ugesehen = set()
    for t in themen:
        for tok in t['ueberlagerung']:
            m = UEB_TOKEN_RE.fullmatch(tok)
            if not m:
                continue
            k = (m.group('f'), m.group('p'), int(m.group('h')))
            if k in ugesehen:
                continue
            ugesehen.add(k)
            von = 'A' if m.group('p') == na else ('B' if m.group('p') == nb else '?')
            L.append('UEBERLAGERUNG %s von=%s haus=%s herkunft=Thema-%d' % (
                m.group('f'), von, m.group('h') + (('/' + m.group('h2'))
                                                   if m.group('h2') else ''), t['nr']))
    for k, p in (('A', r['A']), ('B', r['B'])):
        fx = {f['name']: f for f in p['factors']}
        for n in ('Sonne', 'Mond', 'AC'):
            L.append('KERN %s %s zeichen=%s' % (k, n, zeichen_von(fx[n]['lon'])))
    L.append('@@ENDE')
    return '\n'.join(L) + '\n'


def datenblatt(a_pfad, b_pfad, ziel, art, themen='bz_themen.md',
               deckblatt='bz_deckblatt.md', datum=None, eltern='A', beziehung=None,
               einwilligung=None, sprache='deutsch', auftrag_zeit=None,
               grundlage=None):
    """Baut `<A>_Beziehung_<B>_<Datum>_chart_data.md` — gebaut, nie abgetippt.

    Rechnet alles (rechnung()), haengt die Themenliste des Laufs aus `themen`
    (falls vorhanden; Abschnitt „## Themenliste der Beziehung“ samt „###
    Ohne Deutungs-Heimat“), die gebauten Ressourcen, den maschinenlesbaren
    Block, den @@SELEKTOR-Block (aus Themenliste, Ressourcen und Kernanlagen)
    und — falls `deckblatt` existiert — den @@DECKBLATT-Block an. Nach jeder
    Aenderung an themen oder deckblatt einfach noch einmal aufrufen.

    Die uebrigen Argumente wie rechnung(). -> dict {'ziel', 'bytes', 'r',
    'themen' (lies_themen), 'ressourcen', 'mit_themen', 'mit_deckblatt'} und
    eine Ergebniszeile auf stdout. BeziehungFehler bei Anhalte-Gruenden steht
    NICHT hier: sie stehen als **ANHALTEN** im ⚠-Block und in r['anhalten'] —
    der Lauf liest sie und haelt an.
    """
    r = rechnung(a_pfad, b_pfad, art, datum=datum, eltern=eltern,
                 beziehung=beziehung, einwilligung=einwilligung, sprache=sprache,
                 auftrag_zeit=auftrag_zeit, grundlage=grundlage)
    teile = [rechnung_text(r)]
    th = {'themen': [], 'ohne': [], 'fehler': []}
    mit_themen = bool(themen and os.path.exists(themen))
    if mit_themen:
        ttxt = open(themen, encoding='utf-8').read().strip('\n')
        if not ttxt.startswith('## Themenliste der Beziehung'):
            raise BeziehungFehler('%s beginnt nicht mit „## Themenliste der Beziehung“.'
                                  % themen)
        if '@@' in ttxt:
            raise BeziehungFehler('%s trägt einen @@-Block — @@SELEKTOR baut das '
                                  'Skript, @@DECKBLATT steht in %s.' % (themen, deckblatt))
        th = lies_themen(ttxt)
        teile.append(ttxt + '\n')
    res = _ressourcen(r, th['themen'])
    teile.append(_ressourcen_text(r, res))
    teile.append(_maschinenblock(r))
    teile.append(_selektor_block(r, th['themen'], res))
    mit_deck = bool(deckblatt and os.path.exists(deckblatt))
    if mit_deck:
        d = open(deckblatt, encoding='utf-8').read().strip()
        if not (d.startswith('@@DECKBLATT') and d.endswith('@@ENDE')):
            raise BeziehungFehler('%s: erwartet @@DECKBLATT … @@ENDE.' % deckblatt)
        teile.append(d + '\n')
    text = '\n'.join(t.rstrip('\n') + '\n' for t in teile)
    with open(ziel, 'w', encoding='utf-8') as f:
        f.write(text)
    b = len(text.encode('utf-8'))
    print('%s %d B · %d Verbindungen, %d eng · Achsen zueinander %d · %s · %s · '
          'Anhalten: %s' % (
              os.path.basename(ziel), b, len(r['kreuz']),
              sum(1 for x in r['kreuz'] if x['eng']), len(r['achsen']),
              ('Themenliste %d Themen' % len(th['themen'])) if mit_themen
              else 'noch ohne Themenliste',
              'mit @@DECKBLATT' if mit_deck else 'noch ohne @@DECKBLATT',
              '; '.join(r['anhalten']) or 'nein'))
    for f in th['fehler']:
        print('  ! Themenliste: %s' % f)
    return {'ziel': ziel, 'bytes': b, 'r': r, 'themen': th, 'ressourcen': res,
            'mit_themen': mit_themen, 'mit_deckblatt': mit_deck}


# ---------------------------------------------------------------------------
# Datenblatt der Beziehung wieder lesen
# ---------------------------------------------------------------------------

def quellen_aus(datenblatt_pfad, themen='bz_themen.md', deckblatt='bz_deckblatt.md'):
    """Holt `bz_themen.md` und `bz_deckblatt.md` aus einem gesicherten
    Datenblatt der Beziehung zurueck — fuer den Neubau, wenn nach dem Halt der
    Arbeitsbereich fehlt (Modul, Chat 1, Schritt 5). Die Themenliste ist der
    Abschnitt „## Themenliste der Beziehung“ bis vor „## Ressourcen der
    Beziehung“, der Deckblatt-Block `@@DECKBLATT … @@ENDE`. Geschrieben wird nur,
    was das Datenblatt traegt. -> Liste der geschriebenen Pfade."""
    text = open(datenblatt_pfad, encoding='utf-8').read()
    out = []
    m = re.search(r'^## Themenliste der Beziehung\n.*?(?=^## Ressourcen der Beziehung|'
                  r'^## Maschinenlesbar|^@@|\Z)', text, re.M | re.S)
    if m and themen:
        open(themen, 'w', encoding='utf-8').write(m.group(0).rstrip() + '\n')
        out.append(themen)
    m = re.search(r'^@@DECKBLATT\n.*?^@@ENDE[^\n]*', text, re.M | re.S)
    if m and deckblatt:
        open(deckblatt, 'w', encoding='utf-8').write(m.group(0) + '\n')
        out.append(deckblatt)
    return out


def lies_beziehung(pfad):
    """Liest das Datenblatt der Beziehung und rechnet aus seinem
    maschinenlesbaren Block alles neu (dieselben Funktionen wie beim Bau —
    die Tabellen werden nie zurueckgelesen).

    -> dict wie rechnung() ('A', 'B' mit 'vorname', 'factors', 'cusps',
       'offen_eigen' (seit 2026-10-15; ein aelteres Datenblatt der Beziehung hat keins) …,
       'kreuz', 'achsen', 'ueb_b_in_a', 'ueb_a_in_b', 'verteilung', 'rang',
       'art', 'eltern', 'kind', 'kind_minderjaehrig', 'datum', 'zeit' mit
       'offen', 'eng_kippt' und 'ueb_kippt' aus der Zeitprobe des Baus — sie
       wird nicht neu gerechnet), dazu 'text', 'themen' (lies_themen),
       'ressourcen', 'deckblatt' (dict oder None).
    """
    text = open(pfad, encoding='utf-8').read()
    m = re.search(r'## Maschinenlesbar[^\n]*\n+```python\n(.*?)\n```', text, re.S)
    if not m:
        raise BeziehungFehler('%s: kein maschinenlesbarer Block.' % os.path.basename(pfad))
    ns = {}
    for zeile in re.split(r'\n(?=[A-Z_]+ = )', m.group(1)):
        k, v = zeile.split(' = ', 1)
        ns[k.strip()] = ast.literal_eval(v.strip())
    pa = dict(ns['PERSON_A'], factors=ns['FACTORS_A'], cusps=ns['CUSPS_A'])
    pb = dict(ns['PERSON_B'], factors=ns['FACTORS_B'], cusps=ns['CUSPS_B'])
    offen = ns.get('OFFEN', {'A': [], 'B': []})
    r = {'art': ns['ART'], 'eltern': ns.get('ELTERN'), 'A': pa, 'B': pb,
         'kind_minderjaehrig': ns.get('KIND_MINDERJAEHRIG', False),
         'datum': datetime.date.fromisoformat(ns['DATUM']), 'text': text,
         'zeit': {'offen': {'A': set(offen.get('A', [])),
                            'B': set(offen.get('B', []))},
                  'eng_kippt': set(tuple(x) for x in ns.get('ENG_KIPPT', [])),
                  'ueb_kippt': set(tuple(x) for x in ns.get('UEB_KIPPT', []))}}
    r['kind'] = (None if r['art'] != 'eltern-kind'
                 else ('B' if (r['eltern'] or 'A') == 'A' else 'A'))
    r['kreuz'] = kreuzaspekte(pa['factors'], pb['factors'])
    r['achsen'] = achsenkontakte(pa['factors'], pb['factors'])
    r['ueb_b_in_a'] = ueberlagerung(pb['factors'], pa['cusps'], offen=offen.get('A'))
    r['ueb_a_in_b'] = ueberlagerung(pa['factors'], pb['cusps'], offen=offen.get('B'))
    r['verteilung'] = verteilung_beider(pa, pb)
    r['rang'] = rangzeilen(r)
    r['themen'] = lies_themen(text)
    r['ressourcen'] = _ressourcen(r, r['themen']['themen'])
    r['deckblatt'] = None
    if '@@DECKBLATT' in text:
        try:
            import build
            r['deckblatt'] = build.lies_deckblatt(pfad)
        except Exception as e:                   # pragma: no cover
            r['deckblatt_fehler'] = str(e)
    return r


# ---------------------------------------------------------------------------
# Heimat-Probe der Beziehung
# ---------------------------------------------------------------------------

def heimat(pfad):
    """Jede ENGE Verbindung (Aspekte zwischen beiden und Achsen zueinander)
    braucht genau einen Deutungsort: ein Thema (aspekte=), „Was trägt“ (eine
    Ressource ohne Thema), das Getriebe-Kapitel (ein enger Kontakt der Achsen
    zueinander ohne Thema) oder eine Zeile unter „### Ohne Deutungs-Heimat“
    (dann in der Rechenschaft). Dazu: jedes aspekte=-Token und jedes
    ueberlagerung=-Token muss in der Rechnung stehen.

    -> {'eng', 'thema', 'was_traegt', 'getriebe', 'ohne_heimat', 'doppelt',
        'ohne_ort', 'unbekannt', 'nicht_eng', 'ueb_falsch', 'fehler'} — Listen
        von Texten.
    """
    r = lies_beziehung(pfad)
    na, nb = r['A']['vorname'], r['B']['vorname']
    idx = _kreuz_index(r)
    eng = [e for e in r['kreuz'] + r['achsen'] if e['eng']]
    thema = {}
    unbekannt, nicht_eng = [], []
    for t in r['themen']['themen']:
        for tok in t['aspekte']:
            m = ASP_TOKEN_RE.fullmatch(tok)
            k = (_asp_schluessel(m.group('fa'), m.group('pa'), m.group('fb'),
                                 m.group('pb'), na, nb, GLYPHE_ASPEKT.get(m.group('g')))
                 if m else None)
            e = idx.get(k) if k else None
            if e is None:
                unbekannt.append('Thema %d: %s' % (t['nr'], tok))
                continue
            if t['nr'] in thema.setdefault(id(e), []):
                continue                    # 2026-10-14b: zweimal im selben Thema ist EIN Ort
            thema[id(e)].append(t['nr'])
            if not e['eng']:
                nicht_eng.append('Thema %d: %s (%s, nicht eng)' % (t['nr'], tok,
                                                                    _gr(e['orb'])))
    ueb_falsch = []
    alle_ueb = {('B', u['faktor']): u for u in r['ueb_b_in_a']}
    alle_ueb.update({('A', u['faktor']): u for u in r['ueb_a_in_b']})
    for t in r['themen']['themen']:
        for tok in t['ueberlagerung']:
            m = UEB_TOKEN_RE.fullmatch(tok)
            if not m:
                ueb_falsch.append('Thema %d: Form „%s“ (erwartet: Mond (%s) in Haus 4 '
                                  'von %s)' % (t['nr'], tok, nb, na))
                continue
            von = 'A' if m.group('p') == na else ('B' if m.group('p') == nb else None)
            haus_von = m.group('q')
            u = alle_ueb.get((von, m.group('f')))
            soll_von = nb if von == 'A' else na
            if u is None or haus_von != soll_von:
                ueb_falsch.append('Thema %d: %s — nicht in der Überlagerung' % (t['nr'], tok))
                continue
            h, h2 = int(m.group('h')), m.group('h2')
            erlaubt = {u['haus'], u['fuehrend']} | ({u['nebenhaus']} if u['grenzlage']
                                                    else set())
            if h not in erlaubt or (h2 and int(h2) not in erlaubt):
                ueb_falsch.append('Thema %d: %s — gerechnet %s' % (t['nr'], tok, u['spalte']))
    ohne_zeilen = r['themen']['ohne']
    res_ids = {id(x['zeile']) for x in r['ressourcen'] if x['deutungsort'] == 'Was trägt'}
    ohne_heim = {}
    for z in ohne_zeilen:
        m = ASP_TOKEN_RE.search(z)
        if not m:
            continue
        k = _asp_schluessel(m.group('fa'), m.group('pa'), m.group('fb'), m.group('pb'),
                            na, nb, GLYPHE_ASPEKT.get(m.group('g')))
        e = idx.get(k) if k else None
        if e is not None:
            ohne_heim.setdefault(id(e), []).append(z)
    achs_ids = {id(e) for e in r['achsen']}
    out = {'eng': [], 'thema': [], 'was_traegt': [], 'getriebe': [], 'ohne_heimat': [],
           'doppelt': [], 'ohne_ort': [], 'unbekannt': unbekannt, 'nicht_eng': nicht_eng,
           'ueb_falsch': ueb_falsch, 'fehler': list(r['themen']['fehler'])}
    for e in eng:
        name = '%s %s %s %s' % (_mit(e['a'], na), ASPEKT_GLYPHE.get(e['name'], e['name']),
                                _mit(e['b'], nb), _gr(e['orb']))
        out['eng'].append(name)
        orte = (['Thema %s' % n for n in thema.get(id(e), [])]
                + (['Was trägt'] if id(e) in res_ids else [])
                + (['Ohne Deutungs-Heimat'] * len(ohne_heim.get(id(e), []))))
        if len(thema.get(id(e), [])) > 1 or (len(orte) > 1):
            out['doppelt'].append('%s: %s' % (name, ', '.join(orte)))
        if thema.get(id(e)):
            out['thema'].append(name)
        elif id(e) in res_ids:
            out['was_traegt'].append(name)
        elif id(e) in achs_ids:
            out['getriebe'].append(name)
        elif id(e) in ohne_heim:
            out['ohne_heimat'].append(name)
        else:
            out['ohne_ort'].append(name)
    return out


def heimat_bericht(pfad):
    """Die eine Ergebniszeile der Heimat-Probe der Beziehung, darunter je
    Befund eine eingerueckte Zeile."""
    h = heimat(pfad)
    L = ['BEZIEHUNG-HEIMAT: %d eng · %d mit Thema · %d in „Was trägt“ · %d im Getriebe · '
         '%d ohne Deutungs-Heimat (Rechenschaft) · %d doppelt · %d ohne Ort · '
         '%d unbekannt · %d Überlagerung falsch' % (
             len(h['eng']), len(h['thema']), len(h['was_traegt']), len(h['getriebe']),
             len(h['ohne_heimat']), len(h['doppelt']), len(h['ohne_ort']),
             len(h['unbekannt']), len(h['ueb_falsch']))]
    for k, lab in (('fehler', 'Themenliste'), ('doppelt', 'doppelt'),
                   ('ohne_ort', 'ohne Ort'), ('unbekannt', 'nicht in der Rechnung'),
                   ('ueb_falsch', 'Überlagerung'), ('nicht_eng', 'nicht eng (Hinweis)')):
        for x in h[k]:
            L.append('  %s: %s' % (lab, x))
    return '\n'.join(L)


# ---------------------------------------------------------------------------
# Referenzschnitt (Bibliothek ohne Netzquellen)
# ---------------------------------------------------------------------------

_PRINZIP_DATEI = '01_Planeten_Grundprinzipien.txt'


def _prinzip(bundle, faktor):
    """Archetyp, Schatten und PRINZIP eines Faktors aus der Bibliothek; Achsen:
    die allgemeine Beschreibung ihres Hauses (AC 1, MC 10). -> (schluessel, text)."""
    import selektor
    if faktor in ('AC', 'MC', 'DC', 'IC'):
        n = {'AC': 1, 'MC': 10, 'DC': 7, 'IC': 4}[faktor]
        k = 'HAUS_%d_ALLG' % n
        return k, bundle.get(selektor.haus_file(n), {}).get(k, '')
    if faktor in ('Chiron', 'Lilith', 'Pholus'):
        k = '%s_ALLG' % selektor.norm(faktor)
        return k, bundle.get(selektor.SPEZFILE[selektor.norm(faktor)], {}).get(k, '')
    kopf = {'Mondknoten': 'MONDKNOTEN'}.get(faktor, selektor.norm(faktor))
    for k, t in bundle.get(_PRINZIP_DATEI, {}).items():
        if not k.startswith('GRUNDLAGEN_'):
            continue
        m = re.search(r'^-{20,}\n%s[^\n]*\n-{20,}\n(.*?)(?=^-{20,}\n[A-ZÄÖÜ]|\Z)'
                      % re.escape(kopf), t, re.M | re.S)
        if m:
            body = m.group(1)
            teile = []
            for feld in ('Archetyp:', 'Schatten:'):
                z = re.search(r'^%s[^\n]*' % feld, body, re.M)
                if z:
                    teile.append(z.group(0))
            p = re.search(r'^PRINZIP:.*?(?=\n\n|\Z)', body, re.M | re.S)
            if p:
                teile.append(p.group(0))
            return 'PRINZIP_%s' % kopf, '\n'.join(teile)
    return 'PRINZIP_%s' % kopf, ''


# 2026-10-14c (Wartungslauf „Art Freundschaft“, Punkt a): Hilfen des satzweisen Filters
_DEKOR_RE = re.compile(r'^\s*[─━=\-_~·•*]{4,}\s*$')
_LISTE_RE = re.compile(r'^\s*(?:[-•*]\s|\d{1,2}[.)]\s)')
# Feldkopf am Zeilenanfang: in Versalien („THEMA:“, „KONJUNKTION AM NORDKNOTEN – …“)
# oder in gemischter Schreibung mit bis zu vier Woertern („Als Kind – …“, „Inneres
# Mutterbild:“, „Skorpion (Erhöhung):“, „Stier 1874/75–1887/88:“) — ohne Punkt im Kopf,
# sonst laese er ueber eine Satzgrenze („Begegnung. Ressource:“).
_KOPF_START_RE = re.compile(
    r'^\s*(?:[A-ZÄÖÜ][A-ZÄÖÜ0-9 /(),=☊☋-]*[A-ZÄÖÜ)]\s*(?::|\s–\s)'
    r'|[A-ZÄÖÜ][\wäöüß]+(?:[ -][\wÄÖÜäöüß/–()]+){0,3}\s*(?::|\s–\s))')
# Ueberschrift in Versalien ohne Doppelpunkt („FÜHLEN“, „MONDKNOTEN ☊“)
_VERSAL_ZEILE_RE = re.compile(r'^\s*[A-ZÄÖÜ][^a-zäöüß:]{1,60}$')
# Kopf einer Prosa-Einheit: „FELD – Titel␣␣“, „Feld – Titel: “ oder „FELD: “ / „Feld: “
_KOPF_TITEL_RE = re.compile(
    r'^\s*(?:[A-ZÄÖÜ]{2}[A-ZÄÖÜ0-9]*(?:\s[\wÄÖÜäöüß()/=☊☋-]+){0,10}'
    r'|[A-ZÄÖÜ][\wäöüß()/-]*(?:\s[\wÄÖÜäöüß()/-]+){0,4})\s–\s[^.!?:\n]{1,80}?(?:\s{2,}|:\s+)')
_KOPF_FELD_RE = re.compile(r'^\s*[A-ZÄÖÜ][\wÄÖÜäöüß()–/-]*(?:\s[\wÄÖÜäöüß()–/-]+){0,3}:\s+')
_FELD_VERSAL_RE = re.compile(r'^\s*([A-ZÄÖÜ][A-ZÄÖÜ ]*[A-ZÄÖÜ])(?=\s*(?::|\s–\s|\s\())')
_ABK = {'ca', 'bzw', 'vgl', 'usw', 'etc', 'evtl', 'ggf', 'bspw', 'inkl', 'sog', 'hrsg',
        'nr', 'jh', 'jhd', 'dr', 'prof', 'st', 'abb', 'bd', 'ff', 'chr'}
_GRENZE_RE = re.compile(r'([.!?…])(["“”»)]*)(\s+)(?=[A-ZÄÖÜ„"»(0-9])')
_UMBRUCH = (55, 95)       # Zeilenlaenge eines Umbruchs in der Bibliothek (Zeichen)


def _saetze_bibliothek(text):
    """Saetze eines Bibliothekstextes — ohne Grenze nach einer Abkuerzung („ca.“,
    „bzw.“) oder einem einzelnen Buchstaben („u. a.“, „M. Kelley“)."""
    out, start = [], 0
    for m in _GRENZE_RE.finditer(text):
        vor = re.search(r'([\wÄÖÜäöüß]+)$', text[start:m.start()])
        wort = vor.group(1) if vor else ''
        if m.group(1) == '.' and (len(wort) == 1 or wort.lower() in _ABK):
            continue
        out.append(text[start:m.end(2)])
        start = m.end()
    out.append(text[start:])
    return [s for s in out if s.strip()]


def _einheiten(zeilen):
    """Zeilen eines Absatzes -> Einheiten (Listen von Zeilen). Eine umbrochene Zeile
    (Laenge im Band _UMBRUCH) setzt sich in der naechsten fort, wenn sie mitten im
    Satz endet — auch vor einem Wort mit Doppelpunkt („Der besonders betonte /
    Umschlagpunkt: …“) — oder wenn die naechste nicht mit einem Feldkopf beginnt.
    Rahmen, Versalueberschriften, Listenzeilen und kurze Zeilen stehen fuer sich."""
    einheiten = []
    for i, z in enumerate(zeilen):
        v = zeilen[i - 1].rstrip() if i else ''
        if (i == 0 or not z.strip() or not v.strip() or _DEKOR_RE.match(z)
                or _DEKOR_RE.match(v) or _VERSAL_ZEILE_RE.match(z)
                or _VERSAL_ZEILE_RE.match(v) or _LISTE_RE.match(z)
                or not (_UMBRUCH[0] <= len(v) <= _UMBRUCH[1])):
            neu = True
        elif re.search(r'[.!?:;…]["“”»)]*$', v):
            neu = bool(_KOPF_START_RE.match(z))      # Umbruch an einer Satzgrenze
        elif re.search(r'(?:^|\s)[a-zäöüß][\wäöüß]*$|[,–—-]$', v):
            neu = False                  # mitten im Satz umbrochen („Der besonders betonte“)
        else:
            neu = bool(_KOPF_START_RE.match(z))      # Tabellenzeile („… Aszendent: Skorpion“)
        if neu:
            einheiten.append([z])
        else:
            einheiten[-1].append(z)
    return einheiten


def _verbinden(einheit):
    """Zeilen einer Einheit zu einem Text; „Dreiecks-“ / „Charakter“ ohne Leerzeichen."""
    out = einheit[0].strip()
    for z in einheit[1:]:
        z = z.strip()
        out += ('' if re.search(r'[A-Za-zÄÖÜäöüß]-$', out) else ' ') + z
    return out


def _filtern(text, filter_re=None):
    """Filter fuer Eltern-Kind und Freundschaft (FILTER_ELTERN_KIND): entfernt, was
    nichts Romantisches und nichts Sexuelles tragen darf. -> (text, Zahl der
    entfernten Stuecke).

    2026-10-14c (Pruefbericht Beziehung Text 14.10. b, Rubrik 2; Wartungslauf „Art
    Freundschaft“, Punkt a): satzweise statt zeilenweise. Vorher fiel jede Zeile unter
    90 Zeichen mit einem Treffer ganz weg — in der umbrochenen Prosa der Bibliothek
    blieben Satzreste stehen („Wegs oder Nebel und Flucht.“) und Abschnittskoepfe
    gingen verloren (FLUSS, SPANNUNG). Jetzt: Absaetze ohne Treffer bleiben, wie sie
    sind; sonst werden umbrochene Zeilen zu Einheiten zusammengefasst (_einheiten),
    der Kopf einer Einheit („FLUSS ZUR ACHSE – die tragende Hingabe␣␣“, „THEMA:“,
    „Als Kind – …:“) abgetrennt und nur die SAETZE (bei „ / “-Reihen die Glieder) mit
    Treffer entfernt; der Kopf bleibt, traegt er selbst den Treffer, nur sein Feldname
    in Versalien. „[…]“ markiert, dass am Anfang etwas fehlt, „[gefiltert]“ eine leer
    gewordene Einheit. Listen-, Bild- und Ueberschriftzeilen (Archetyp, Schatten,
    Gegenueberstellung „Fürsorge – Erotik“, Tabellenzeilen) fallen weiterhin ganz weg.
    Eine gekuerzte Einheit steht danach ohne Umbruch in EINER Zeile."""
    filter_re = FILTER_ELTERN_KIND if filter_re is None else filter_re
    n = 0
    out = []
    for teil in re.split(r'(\n[ \t]*\n)', text):
        if not teil.strip() or not filter_re.search(teil):
            out.append(teil)
            continue
        neu = []
        for einheit in _einheiten(teil.split('\n')):
            ganz = _verbinden(einheit)
            if not filter_re.search(ganz):
                neu.extend(einheit)                      # unberuehrt, im alten Umbruch
                continue
            feld = _FELD_VERSAL_RE.match(ganz)
            if feld and filter_re.search(feld.group(1)):
                feld = None                              # „IDEE DER PARTNERSCHAFT:“ faellt mit
            m = _KOPF_TITEL_RE.match(ganz) or _KOPF_FELD_RE.match(ganz)
            if len(einheit) == 1 and (
                    _DEKOR_RE.match(ganz) or _VERSAL_ZEILE_RE.match(ganz)
                    or re.match(r'(?i)(?:archetyp|schatten)\b', ganz) or _LISTE_RE.match(ganz)
                    or (not m and len(ganz) < 90 and not re.search(r'[.!?…]\s', ganz))):
                # Listen-, Bild- und Ueberschriftzeile ohne Feldkopf („Fürsorge – Erotik“,
                # Archetyp, Schatten): ganz weg; ein Feldname in Versalien bleibt stehen.
                n += 1
                if feld and not re.match(r'(?i)(?:archetyp|schatten)\b', ganz):
                    neu.append(feld.group(1) + ': [gefiltert]')
                continue
            kopf, rumpf = (ganz[:m.end()], ganz[m.end():]) if m else ('', ganz)
            kopf_weg = bool(kopf and filter_re.search(kopf))
            if kopf_weg:
                n += 1
                kopf = (feld.group(1) + ': ') if feld else ''
            rest, vorn_weg = [], False
            for i, satz in enumerate(_saetze_bibliothek(rumpf)):
                teile = re.split(r'\s+/\s+', satz)
                bleibt = [t.strip() for t in teile if not filter_re.search(t)]
                n += len(teile) - len(bleibt)
                if i == 0 and filter_re.search(teile[0]):
                    vorn_weg = True
                if bleibt:
                    rest.append(' / '.join(bleibt))
            if rest:
                neu.append(kopf + ('[…] ' if (kopf and (vorn_weg or kopf_weg)) else '')
                           + ' '.join(rest))
            elif kopf:
                neu.append(kopf.rstrip() + ' [gefiltert]')
            else:
                neu.append('[gefiltert]')
        out.append('\n'.join(neu))
    text_neu = ''.join(out)
    if n:
        text_neu = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', text_neu)
    return text_neu, n


def _mond_teil(text, abschnitt):
    """Aus einem MOND_IN_<ZEICHEN>-Block den Absatz „Als Kind – …“ (samt
    „Inneres Mutterbild“ und „Schwierige Lernaufgaben“) bzw. „Als Mutter – …“."""
    m = re.search(r'^(%s\s*–.*?)(?=\n\s*\n|\Z)' % re.escape(abschnitt), text, re.M | re.S)
    kopf = re.search(r'^MOND IN [^\n]+', text, re.M)
    return ((kopf.group(0) + '\n') if kopf else '') + (m.group(1) if m else '')


def referenzschnitt(pfad, bundle_pfad, ziel):
    """Baut `<A>_Beziehung_<B>_<Datum>_referenz.md` aus dem @@SELEKTOR-Block des
    Datenblatts der Beziehung — gebaut, nicht gelesen; die Bibliothek selbst
    liest der Lauf nie.

    Inhalt: je PAAR-Zeile der Paarblock (selektor.resolve_aspect; ein Paar
    gleicher Faktoren hat keinen Block: dann das Prinzip, „Grundton aus dem
    Prinzip“); je UEBERLAGERUNG-Zeile HAUS_n_ALLG (bei Grenzlage beide) und das
    Prinzip des Faktors; je KERN-Zeile SONNE_IN_x, MOND_IN_x und ASZENDENT_x.
    Eltern-Kind: Mond des Kindes nur „Als Kind …“, des Elternteils nur „Als
    Mutter …“ (fuer einen Vater sinngemaess). Eltern-Kind und (seit 2026-10-14c)
    Freundschaft: alle Paar-, Prinzip- und Kernbloecke durch den Filter (_filtern:
    nichts Sexuelles, nichts Romantisches, satzweise), gezaehlt; Hausbloecke und die
    Mond-Schnitte ungefiltert. Paar: kein Filter.
    Jeder Block steht einmal; ein Kopf nennt, wofuer er gebraucht wird.

    -> {'ziel', 'bytes', 'bloecke', 'fehlstellen', 'gefiltert'}; eine
    Ergebniszeile auf stdout.
    """
    import selektor
    text = open(pfad, encoding='utf-8').read()
    m = re.search(r'^@@SELEKTOR\n(.*?)\n@@ENDE', text, re.M | re.S)
    if not m:
        raise BeziehungFehler('%s: kein @@SELEKTOR-Block.' % os.path.basename(pfad))
    r = lies_beziehung(pfad)
    na, nb = r['A']['vorname'], r['B']['vorname']
    namen = {'A': na, 'B': nb}
    bundle = selektor.load_bundle(bundle_pfad)
    elternkind = r['art'] == 'eltern-kind'
    filter_art = r['art'] in OHNE_ROMANTIK          # 2026-10-14c: auch Freundschaft
    kind = r['kind']
    bloecke, reihen, fehl = {}, [], []
    gefiltert = [0]

    def nimm(schl, txt, wozu, filtern=filter_art):
        if not (txt or '').strip():
            fehl.append('%s — %s fehlt in der Bibliothek' % (wozu, schl))
            return
        if schl not in bloecke:
            if filtern and txt:
                txt, n = _filtern(txt)
                gefiltert[0] += n
            bloecke[schl] = {'text': txt, 'wozu': []}
            reihen.append(schl)
        if wozu not in bloecke[schl]['wozu']:
            bloecke[schl]['wozu'].append(wozu)
    for z in m.group(1).splitlines():
        teile = z.split()
        if not teile:
            continue
        if teile[0] == 'PAAR':
            fa, fb = teile[1], teile[2]
            felder = dict(x.split('=', 1) for x in teile[3:] if '=' in x)
            wozu = '%s %s %s (%s) — %s' % (_mit(fa, na), felder.get('aspekt', '?'),
                                          _mit(fb, nb), felder.get('stufe', '?'),
                                          felder.get('herkunft', '').replace('-', ' '))
            ta, tb = selektor.norm_token(fa), selektor.norm_token(fb)
            if fa in ACHSEN and fb in ACHSEN:
                for f in (fa, fb):
                    k, t = _prinzip(bundle, f)
                    nimm(k, t, wozu + ' · Achse zu Achse: Grundton aus den beiden Häusern',
                         filtern=False)
                continue
            if fa == fb:
                k, t = _prinzip(bundle, fa)
                nimm(k, t, wozu + ' · kein Paarblock: Grundton aus dem Prinzip')
                continue
            src, key, note = selektor.resolve_aspect(ta, tb)
            if src and key in bundle.get(src, {}):
                nimm(key, bundle[src][key], wozu + ((' · ' + note) if note else ''))
            else:
                fehl.append('%s — %s' % (wozu, note or 'kein Block'))
                for f in (fa, fb):
                    k, t = _prinzip(bundle, f)
                    nimm(k, t, wozu + ' · Fehlstelle: Grundton aus den Prinzipien')
        elif teile[0] == 'UEBERLAGERUNG':
            f = teile[1]
            felder = dict(x.split('=', 1) for x in teile[2:] if '=' in x)
            von = felder.get('von', '?')
            wer, bei = namen.get(von, '?'), namen.get('B' if von == 'A' else 'A', '?')
            haeuser = [int(x) for x in re.split(r'[/=]', felder.get('haus', '0')) if x]
            wozu = '%s in Haus %s von %s — %s' % (_mit(f, wer), felder.get('haus'), bei,
                                                  felder.get('herkunft', '').replace('-', ' '))
            for h in haeuser:
                k = 'HAUS_%d_ALLG' % h
                t = bundle.get(selektor.haus_file(h), {}).get(k)
                if t is None:
                    fehl.append('%s — %s fehlt' % (wozu, k))
                else:
                    nimm(k, t, wozu, filtern=False)
            k, t = _prinzip(bundle, f)
            nimm(k, t, wozu)
        elif teile[0] == 'KERN':
            wer, f = teile[1], teile[2]
            felder = dict(x.split('=', 1) for x in teile[3:] if '=' in x)
            zn = selektor.norm(felder.get('zeichen', ''))
            name = namen.get(wer, '?')
            if f == 'AC':
                k = 'ASZENDENT_%s' % zn
                t = bundle.get('05_Aszendent_MC_Deszendent_Tabellen.txt', {}).get(k)
            else:
                k = '%s_IN_%s' % (selektor.norm(f), zn)
                t = bundle.get(selektor.ZEICHENFILE[selektor.norm(f)], {}).get(k)
            if t is None:
                fehl.append('Kernanlage %s %s — %s fehlt' % (name, f, k))
                continue
            wozu = 'Kernanlage %s: %s in %s' % (name, f, felder.get('zeichen'))
            if f == 'Mond' and elternkind:
                teil = 'Als Kind' if wer == kind else 'Als Mutter'
                hinweis = '' if (teil == 'Als Kind' or r[wer].get('geschlecht') ==
                                 'weiblich') else ' (für einen Vater sinngemäß: wie er ' \
                                                  'versorgt und Geborgenheit gibt)'
                nimm('%s · %s · %s' % (k, teil, wer), _mond_teil(t, teil),
                     wozu + ' — nur „%s“%s' % (teil, hinweis), filtern=False)
            else:
                nimm('%s · %s' % (k, wer) if f != 'Sonne' else k, t, wozu)
    L = ['# Referenzschnitt der Beziehung — %s und %s' % (na, nb), '',
         '- Art: %s%s' % (ART_TITEL.get(r['art'], r['art']),
                          (' — Filter: nichts Sexuelles, nichts Romantisches; %d '
                           'Sätze oder Zeilen entfernt' % gefiltert[0])
                          if filter_art else ''),
         '- Quelle: nur die Bibliothek (blocks_bundle.txt), keine Netzquellen. Ein '
         'Paarblock beschreibt die Verbindung zweier Prinzipien IN EINEM Bild: '
         'zwischen zwei Menschen gilt er als Grundton (ALLGEMEIN, '
         'GEGENÜBERSTELLUNG); EINKLANG und MISSKLANG sind für das Horoskop eines '
         'Erwachsenen geschrieben und werden auf die Beziehung übertragen, nie '
         'wörtlich einer Person zugeschrieben.',
         '- Blöcke: %d · Fehlstellen: %d' % (len(reihen), len(fehl))]
    for f in fehl:
        L.append('  - ⚠ FEHLSTELLE: %s' % f)
    L.append('')
    for k in reihen:
        b = bloecke[k]
        L.append('### [%s]' % k)
        for w in b['wozu']:
            L.append('- für: %s' % w)
        L.append('')
        L.append(b['text'].strip('\n'))
        L.append('')
    out = '\n'.join(L) + '\n'
    with open(ziel, 'w', encoding='utf-8') as f:
        f.write(out)
    by = len(out.encode('utf-8'))
    print('%s %d B · %d Blöcke · %d Fehlstellen%s' % (
        os.path.basename(ziel), by, len(reihen), len(fehl),
        (' · gefiltert %d' % gefiltert[0]) if filter_art else ''))
    return {'ziel': ziel, 'bytes': by, 'bloecke': reihen, 'fehlstellen': fehl,
            'gefiltert': gefiltert[0]}


# ---------------------------------------------------------------------------
# Doppelrad
# ---------------------------------------------------------------------------

FARBE_B = '#5d4a86'       # Glyphen der zweiten Person im Aussenring (gedecktes Violett)


def doppelrad(quelle, out_path, palette=None, dpi=210, linien='eng'):
    """Zeichnet das Doppelrad als PNG: innen die bestellende Person (A) mit
    ihren Haeusern (Koch) und ihrem Achsenkreuz, aussen die zweite Person (B)
    in eigenem Ring und eigener Farbe (FARBE_B), ihre Achsen als Kuerzel.

    Die Hauslinien von A laufen durch beide Ringe bis an den Zeichenkreis —
    so steht jede Stellung von B sichtbar in einem Haus von A (die
    Ueberlagerung). In der Mitte die Linien zwischen beiden Bildern:
    linien='eng' (Vorgabe) nur die engen Verbindungen, 'alle' alle,
    None keine; Konjunktionen ohne Linie (wie radix.radix()). Beschriftung,
    Positionsmarken und Haarlinien wie radix.radix() (beschriftung_setzen,
    je Ring getrennt).

    quelle: Pfad des Datenblatts der Beziehung oder das dict aus
    lies_beziehung(). -> out_path.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge
    import numpy as np
    r = lies_beziehung(quelle) if isinstance(quelle, str) else quelle
    pal = dict(radix.DEFAULT_PALETTE)
    if palette:
        pal.update(palette)
    INK, RING, AXC = pal['ink'], pal['ring'], pal['rot']
    INK_B = pal.get('ink_b', FARBE_B)
    fa, fb = _faktoren(r['A']['factors']), _faktoren(r['B']['factors'])
    ca = r['A']['cusps']
    pos_a = {f['name']: f['lon'] for f in fa}
    pos_b = {f['name']: f['lon'] for f in fb}
    asc, mc = pos_a['AC'], pos_a['MC']

    def th(L):
        return (180 + (L - asc)) % 360

    def xy(L, rr):
        t = np.radians(th(L))
        return rr * np.cos(t), rr * np.sin(t)
    fig, ax = plt.subplots(figsize=(7, 7), dpi=dpi)
    ax.set_xlim(-1.16, 1.16)
    ax.set_ylim(-1.16, 1.16)
    ax.set_aspect('equal')
    ax.axis('off')
    R_OUT, R_SIGN, R_BIN, R_HOUSE, R_ASP = 1.0, 0.86, 0.70, 0.50, 0.42
    R_PLB, R_PLA, TIER = 0.80, 0.635, 0.066
    for k in range(12):
        t1 = th(30 * k)
        ax.add_patch(Wedge((0, 0), R_OUT, t1, t1 + 30, width=R_OUT - R_SIGN,
                           facecolor=pal['elements'][radix._ELEM_OF_SIGN[k]],
                           edgecolor='white', lw=1.2, zorder=1))
        gx, gy = xy(30 * k + 15, (R_OUT + R_SIGN) / 2)
        ax.text(gx, gy, radix.SIGN_GLYPHS[k], ha='center', va='center',
                fontsize=15, color=INK, zorder=3)
    for rr in (R_OUT, R_SIGN, R_HOUSE):
        ax.add_patch(plt.Circle((0, 0), rr, fill=False, ec=RING, lw=1.0, zorder=2))
    ax.add_patch(plt.Circle((0, 0), R_BIN, fill=False, ec=INK_B, lw=0.9, alpha=0.55,
                            zorder=2))
    ax.add_patch(plt.Circle((0, 0), R_ASP, fill=False, ec='#c9c9c9', lw=0.8, zorder=2))
    for g in range(0, 360, 5):
        d = 0.035 if g % 10 == 0 else 0.02
        x0, y0 = xy(g, R_SIGN)
        x1, y1 = xy(g, R_SIGN + d * 0.80)
        ax.plot([x0, x1], [y0, y1], color='#8a8a8a', lw=0.6, zorder=2)
    for k in range(12):
        c = ca[k]
        span = (ca[(k + 1) % 12] - c) % 360
        x0, y0 = xy(c, R_ASP)
        x1, y1 = xy(c, R_SIGN)
        ax.plot([x0, x1], [y0, y1], color=RING, lw=0.6, zorder=1.8)
        nx, ny = xy((c + span / 2) % 360, (R_HOUSE + R_ASP) / 2)
        ax.text(nx, ny, str(k + 1), ha='center', va='center', fontsize=8,
                color='#6f6f6f', zorder=3)
    for L, lab in [(asc, 'AC'), ((asc + 180) % 360, 'DC'), (mc, 'MC'),
                   ((mc + 180) % 360, 'IC')]:
        lx, ly = xy(L, R_OUT + 0.06)
        ax.text(lx, ly, lab, ha='center', va='center', fontsize=10, color=AXC,
                fontweight='bold', zorder=4)
        x0, y0 = xy(L, R_ASP)
        x1, y1 = xy(L, R_OUT)
        ax.plot([x0, x1], [y0, y1], color=AXC, lw=1.3, zorder=2)
    # Linien zwischen beiden Bildern
    if linien:
        for e in r['kreuz'] + r['achsen']:
            if e['color'] == 'konj' or (linien == 'eng' and not e['eng']):
                continue
            col = pal[e['color']]
            x0, y0 = xy(pos_a[e['a']], R_ASP)
            x1, y1 = xy(pos_b[e['b']], R_ASP)
            lw, al = (1.3, 0.85) if e['strength'] == 'voll' else \
                ((0.8, 0.5) if e['strength'] == 'einseitig' else (0.9, 0.7))
            ls = (0, (4, 3)) if e['strength'] == 'einseitig' else '-'
            ax.plot([x0, x1], [y0, y1], color=col, lw=lw, alpha=al, ls=ls, zorder=1.5)
    ax.apply_aspect()
    _p0 = ax.transData.transform((0.0, 0.0))
    _p1 = ax.transData.transform((1.0, 0.0))
    pt_je_einheit = (_p1[0] - _p0[0]) * 72.0 / fig.dpi

    def ring(fx, r0, rand, farbe, achsen_kuerzel):
        order = sorted(fx, key=lambda f: f['lon'])
        if not achsen_kuerzel:
            order = [f for f in order if f['name'] not in ACHSEN]
        zfs, ein = [], []
        for f in order:
            g = f.get('glyph') or radix.FAKTOR_GLYPHE.get(f['name'], '?')
            fs = 13 if len(g) == 1 else 8.0
            zfs.append((g, fs))
            ein.append({'lon': f['lon'], 'masse': radix._tinte_masse(g, fs, dpi),
                        'fest': f['name'] in ACHSEN, 'zeichen': len(g) == 1})
        setz = radix.beschriftung_setzen(ein, asc, (r0, r0 - TIER), pt_je_einheit)
        for f, (g, fs), e, sz in zip(order, zfs, ein, setz):
            rr = r0 - sz['stufe'] * TIER
            px, py = xy(sz['lon'], rr)
            if f['name'] not in ACHSEN:
                xa, ya = xy(f['lon'], rand - 0.002)
                xb, yb = xy(f['lon'], rand - 0.032)
                ax.plot([xa, xb], [ya, yb], color=farbe, lw=1.4,
                        solid_capstyle='butt', zorder=3.5)
                mx0, mx1, my0, my1 = e['masse']
                dx = px + (mx0 + mx1) / 2.0 / pt_je_einheit - xb
                dy = py + (my0 + my1) / 2.0 / pt_je_einheit - yb
                hx = ((mx1 - mx0) / 2.0 + 0.8) / pt_je_einheit
                hy = ((my1 - my0) / 2.0 + 0.8) / pt_je_einheit
                q = min(hx / abs(dx) if abs(dx) > 1e-9 else float('inf'),
                        hy / abs(dy) if abs(dy) > 1e-9 else float('inf'))
                if q < 1.0:
                    xd, yd = xb + (1.0 - q) * dx, yb + (1.0 - q) * dy
                    if math.hypot(xd - xb, yd - yb) > 0.004:
                        ax.plot([xb, xd], [yb, yd], color=farbe, lw=0.5, alpha=0.4,
                                zorder=3.2)
            ax.text(px, py, g, ha='center', va='center', fontsize=fs, color=farbe,
                    zorder=4, fontweight='bold' if f['name'] in ACHSEN else 'normal')
    ring(fa, R_PLA, R_BIN, INK, achsen_kuerzel=False)
    ring(fb, R_PLB, R_SIGN, INK_B, achsen_kuerzel=True)
    grund = pal.get('grund', 'white')
    fig.patch.set_facecolor(grund)
    ax.set_facecolor(grund)
    fig.savefig(out_path, bbox_inches='tight', facecolor=grund, dpi=dpi)
    plt.close(fig)
    return out_path


# 2026-10-14 (Auswertung der Pruefberichte vom 14.10., F3; Chris-Entscheidung 14.10.):
# Die Aspekt-Legende der Radseite kommt aus chartdoc.LEGEND_ROWS; deren Quincunx-Zeile
# („zwei Kräfte, die nicht zusammenpassen …“) liest sich zwischen zwei Menschen als
# Urteil über die Passung (Beziehungsmodul, „Über wen der Text spricht“, Regel 5).
QUINCUNX_LEGENDE = {'de': 'zwei Kräfte, die zu ständigem Nachjustieren zwingen.',
                    'en': 'two forces that call for constant readjustment.'}


def legende_beziehung(chartdoc_modul):
    """Setzt in chartdoc.LEGEND_ROWS die Quincunx-Erklärung des Beziehungsmoduls
    (Regel 5: „zwingt zu ständigem Nachjustieren“) — in der Vorlage gleich nach
    chartdoc.konfiguriere(), weil konfiguriere() die Legende der Sprache setzt.
    Ersetzt die Liste, statt sie zu ändern: setze_sprache() stellt danach den
    Hausstil wieder her. Die Sprache erkennt die Funktion an der Zeile selbst.
    -> die neue Quincunx-Zeile. BeziehungFehler ohne Quincunx-Zeile."""
    neu, treffer = [], None
    for n, w, t in chartdoc_modul.LEGEND_ROWS:
        if n == 'Quincunx':
            treffer = (n, w, QUINCUNX_LEGENDE['en' if 'forces' in t else 'de'])
            neu.append(treffer)
        else:
            neu.append((n, w, t))
    if treffer is None:
        raise BeziehungFehler('chartdoc.LEGEND_ROWS ohne Quincunx-Zeile — Legende prüfen.')
    chartdoc_modul.LEGEND_ROWS = neu
    return treffer


# ---------------------------------------------------------------------------
# Seiten im Hausstil (HTML; Klassen aus chartdoc.struktur_css())
# ---------------------------------------------------------------------------

BEZIEHUNG_CSS = """
/* ---------- Beziehungshoroskop: Staende beider, Verbindungen ---------- */
.bz-zwei { display:flex; gap:0.7cm; align-items:flex-start; }
.bz-zwei > div { flex:1 1 0; }
.bz-name { font-family:"Cinzel"; letter-spacing:0.12em; font-size:10.5pt;
  margin:0 0 0.15cm 0; }
table.bz-st { width:100%; border-collapse:collapse; }
table.bz-st td, table.bz-st th { padding:0.07cm 0.1cm; border-bottom:0.4pt solid #d8cfbd;
  text-align:left; }
table.bz-st th { font-weight:normal; font-style:italic; color:#6d6252; }
/* 2026-10-14b: Grad und Zeichen in einer Zeile — englisch verengte die Kopfzelle
   „in <A>'s chart“ die Spalte, Grad und Zeichen brachen um (13. und 14.10.). */
table.bz-st td:nth-child(2) { white-space:nowrap; }
.bz-asp { column-count:2; column-gap:0.7cm; }
.bz-asp .asp-grp { break-after:avoid; }
.bz-asp table.aspt { width:100%; }
.bz-asp table.aspt td { padding:0.035cm 0; }
.bz-asp td.eng { width:0.35cm; text-align:center; }
.bz-orbis { font-style:italic; color:#6d6252; margin:0.25cm 0 0 0; }
.bz-kopf { display:flex; justify-content:space-between; font-style:italic;
  color:#6d6252; margin:0 0 0.12cm 0; }
.bz-b { color:FARBE_B_PLATZ; }
""".replace('FARBE_B_PLATZ', FARBE_B)

# Seitentitel — wortgleich in build.PFLICHT_BAUSTEINE['beziehung'] und
# build.PFLICHT_GLEICHWERTIG (englisch); wer einen aendert, zieht beide nach.
KREUZ_TITEL = 'Die Verbindungen zwischen beiden Bildern'
STAENDE_TITEL = 'Die Stände beider Bilder'
DOPPELRAD_TITEL = 'Das Doppelrad'
KREUZ_KICKER = 'Zwei Bilder'
SEITEN_EN = {KREUZ_TITEL: 'The Connections Between Both Charts',
             STAENDE_TITEL: 'The Positions in Both Charts',
             DOPPELRAD_TITEL: 'The Double Wheel',
             KREUZ_KICKER: 'Two Charts'}
_LAB = {'de': {'faktor': 'Faktor', 'stand': 'Stand', 'haus': 'Haus', 'bei': 'bei %s',
               'voll': 'Hauptaspekte', 'einseitig': 'Einseitige Hauptaspekte',
               'neben': 'Nebenaspekte', 'achsen': 'Die Achsen zueinander'},
        'en': {'faktor': 'Factor', 'stand': 'Position', 'haus': 'House',
               'bei': 'in %s’s chart', 'voll': 'Major aspects',
               'einseitig': 'One-sided major aspects', 'neben': 'Minor aspects',
               'achsen': 'The axes to each other'}}


def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def _gy(name, farbe_b=False):
    if name in ACHSEN:
        return '<span class="gy%s">%s</span>' % (' bz-b' if farbe_b else '', name)
    import chartdoc
    g = (_fglyph(name) or '').strip()
    disp = _esc(chartdoc.anzeige(name))       # folgt der Sprache (setze_sprache)
    if len(g) != 1:
        return disp
    return '<span class="gy%s">%s</span> %s' % (' bz-b' if farbe_b else '', g, disp)


def staende_page(r, kicker=None, titel=None, anker='PG_staende', skala=1.0, lead=None,
                 sprache='de'):
    """Seite mit den Staenden beider nebeneinander: Faktor, Stand, eigenes Haus
    und das Haus im Bild des anderen (Ueberlagerung). Grenzlage wie in der
    Konstellationsseite: '11/12' (fuehrendes Haus vorn), '9=10' (beide gleich
    stark). `skala` wird eingemessen (chartdoc.passe_ein); sprache 'de'|'en'
    (Titel, Kopfzeilen und Vorspann; ein eigener `lead` ersetzt den Vorspann)."""
    na, nb = r['A']['vorname'], r['B']['vorname']
    lab = _LAB[sprache]
    if kicker is None:
        kicker = KREUZ_KICKER if sprache == 'de' else SEITEN_EN[KREUZ_KICKER]
    if titel is None:
        titel = STAENDE_TITEL if sprache == 'de' else SEITEN_EN[STAENDE_TITEL]
    if lead is None:
        lead = (('Links %s, rechts %s. „Haus“ ist das eigene Haus, die letzte Spalte '
                 'das Haus im Bild der anderen Person. 11/12: Grenzlage, das führende '
                 'Haus steht vorn; 9=10: beide Häuser gleich stark.' % (na, nb))
                if sprache == 'de' else
                ('%s on the left, %s on the right. “House” is the house in one’s own '
                 'chart, the last column the house in the other person’s chart. '
                 '11/12: on the cusp, the leading house first; 9=10: both houses '
                 'equally strong.' % (na, nb)))

    def tab(p, ueb, ander, farbe_b):
        ub = {u['faktor']: u for u in ueb}
        zeilen = []
        for f in _faktoren(p['factors']):
            n = f['name']
            if n in ('DC', 'IC'):
                continue
            if n in ACHSEN:
                haus = str(radix.haus_und_grenzlage(f['lon'], p['cusps'], name=n)['haus'])
            else:
                haus = _haus_eigen(p, n, f['lon'])
            z = zeichen_von(f['lon'])
            zeilen.append('<tr><td>%s%s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>' % (
                _gy(n, farbe_b), ' ℞' if f.get('retro') and n not in ACHSEN else '',
                radix.gr_zeichen(f['lon']), ZEICHEN_GLYPHE[z], haus,
                ub[n]['spalte'] if n in ub else '—'))
        return ('<div><div class="bz-name%s">%s</div><table class="bz-st">'
                '<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>%s'
                '</table></div>' % (' bz-b' if farbe_b else '', _esc(p['vorname']),
                                    lab['faktor'], lab['stand'], lab['haus'],
                                    _esc(lab['bei'] % ander), ''.join(zeilen)))
    pt = 9.0 * skala
    return ('<section class="front" id="%s"><div class="fm-kicker">%s</div>'
            '<h2 class="fm-title">%s</h2><div class="fm-rule"></div>'
            '<p class="fm-lead">%s</p><div class="bz-zwei" style="font-size:%.2fpt">%s%s'
            '</div></section>' % (anker, _esc(kicker), _esc(titel), _esc(lead), pt,
                                   tab(r['A'], r['ueb_a_in_b'], nb, False),
                                   tab(r['B'], r['ueb_b_in_a'], na, True)))


def kreuz_page(r, kicker=None, titel=None, anker='PG_kreuz', skala=1.0, lead=None,
               sprache='de'):
    """Seite mit allen Verbindungen zwischen beiden Bildern: nach Stufe
    gruppiert, links der Faktor von A, rechts der von B, Orb, ● = eng; dazu
    die Achsen zueinander (die Aspekt-Legende steht auf der Doppelrad-Seite).
    Die Zahl der Orb-Eintraege ist len(r['kreuz']) + len(r['achsen']) —
    die Sollzahl fuer build.verify(aspect_rows=…, aspect_section=(KREUZ_TITEL,
    <naechster Titel>)). Die Aspekt-Legende steht auf der Doppelrad-Seite
    (chartdoc.radix_page); hier steht unter der Tabelle nur die
    Orbis-Staffelung (chartdoc.ORBIS_ZEILE) — so passt die Tabelle auch bei
    achtzig Verbindungen auf eine Seite. sprache 'de'|'en'."""
    import chartdoc
    na, nb = r['A']['vorname'], r['B']['vorname']
    lab = _LAB[sprache]
    if kicker is None:
        kicker = KREUZ_KICKER if sprache == 'de' else SEITEN_EN[KREUZ_KICKER]
    if titel is None:
        titel = KREUZ_TITEL if sprache == 'de' else SEITEN_EN[KREUZ_TITEL]
    if lead is None:
        lead = (('Jede Verbindung zwischen den beiden Bildern, voll ausgeschrieben: '
                 'links %s, rechts %s. ● eng: innerhalb des halben Orbis — auf diese '
                 'stützt sich die Deutung. „%s“: nur nach dem größeren der beiden Orben.'
                 % (na, nb, chartdoc.ASP_EINSEITIG)) if sprache == 'de' else
                ('Every connection between the two charts, written out: %s on the '
                 'left, %s on the right. ● close: within half the orb — the reading '
                 'rests on these. “%s”: only within the larger of the two orbs.'
                 % (na, nb, chartdoc.ASP_EINSEITIG)))
    gruppen = [('voll', lab['voll']), ('einseitig', lab['einseitig']),
               ('neben', lab['neben'])]
    bl = []
    for key, label in gruppen:
        grp = [e for e in r['kreuz'] if e['strength'] == key]
        if not grp:
            continue
        rows = []
        for e in grp:
            k = chartdoc.ASPEKT_KLASSE.get(e['name'], 'konj')
            mir = (' <span class="mir">(%s)</span>' % _esc(chartdoc._spiegel_anzeige(
                e['spiegel']))) if e.get('spiegel') else ''
            ee = '<span class="eins">%s</span>' % chartdoc.ASP_EINSEITIG \
                if key == 'einseitig' else ''
            rows.append('<tr><td class="ax">%s <span class="an a-%s">%s</span> %s%s</td>'
                        '<td class="ao">%s%s</td><td class="eng">%s</td></tr>' % (
                            _gy(e['a']), k, chartdoc.anzeige(e['name']), _gy(e['b'], True),
                            mir, chartdoc._orb_text(e['orb']), ee,
                            '●' if e['eng'] else ''))
        bl.append('<div class="asp-grp">%s</div><table class="aspt">%s</table>'
                  % (_esc(label), ''.join(rows)))
    if r['achsen']:
        rows = []
        for e in r['achsen']:
            k = chartdoc.ASPEKT_KLASSE.get(e['name'], 'konj')
            mir = (' <span class="mir">(%s)</span>' % _esc(chartdoc._spiegel_anzeige(
                e['spiegel']))) if e.get('spiegel') else ''
            rows.append('<tr><td class="ax">%s <span class="an a-%s">%s</span> %s%s</td>'
                        '<td class="ao">%s</td><td class="eng">%s</td></tr>' % (
                            _gy(e['a']), k, chartdoc.anzeige(e['name']), _gy(e['b'], True),
                            mir, chartdoc._orb_text(e['orb']), '●' if e['eng'] else ''))
        bl.append('<div class="asp-grp">%s</div><table class="aspt">'
                  '%s</table>' % (lab['achsen'], ''.join(rows)))
    tab_pt, leg_pt = 8.6 * skala, 7.8 * skala
    return ('<section class="front" id="%s"><div class="fm-kicker">%s</div>'
            '<h2 class="fm-title">%s</h2><div class="fm-rule"></div>'
            '<p class="fm-lead">%s</p><div class="bz-kopf" style="font-size:%.2fpt">'
            '<span>%s</span><span class="bz-b">%s</span></div>'
            '<div class="asp bz-asp" style="font-size:%.2fpt">%s</div>'
            '<p class="bz-orbis" style="font-size:%.2fpt">%s</p></section>' % (
                anker, _esc(kicker), _esc(titel), _esc(lead), tab_pt, _esc(na),
                _esc(nb), tab_pt, ''.join(bl), leg_pt, _esc(chartdoc.ORBIS_ZEILE)))


# ---------------------------------------------------------------------------
# Englische Belege (Modul Sprachfassung)
# ---------------------------------------------------------------------------

def beleg_en(beleg, namen):
    """Einen deutschen Beleg des Beziehungshoroskops mechanisch ins Englische.

    Die Belege tragen Vornamen („<A>: Venus ♀ …“) und die Ueberlagerung im
    Genitiv („<B>: Mond ☽ in <A>s 11. Haus“) — beides kennt
    chartdoc.beleg_segment_en() nicht. Hier werden die Namen stehen gelassen,
    die Teile dazwischen von chartdoc uebersetzt und die Ueberlagerung als
    „in <A>’s 11th house“ gesetzt. Segmente anderer Form (Struktur-Befunde
    des Getriebes) gehen ganz durch chartdoc; ein Vorname darin ist kein
    Fehler. Bleibt ein unbekanntes Wort, wirft chartdoc.SprachfassungError —
    dann den Beleg von Hand in BELEG_EN eintragen. -> englischer Beleg.
    """
    import chartdoc
    namen = [n for n in namen if n]

    def en(t):
        if not t.strip():
            return t
        e = chartdoc.beleg_segment_en(t, streng=False)
        fremd = [w for w in chartdoc.beleg_fremdwoerter(e)
                 if w not in namen and w != 's' and w.rstrip('s’\'') not in namen]
        if fremd:
            raise chartdoc.SprachfassungError(
                'Englische Fassung: Beleg nicht mechanisch uebersetzbar — unbekannt: '
                '%s. Teil: %r. Den GANZEN Beleg in BELEG_EN des Builders eintragen.'
                % (', '.join(fremd), t))
        return e

    def haus_en(h, sep, h2):
        out = chartdoc._ordinal_en(h)
        if h2:
            out += sep + chartdoc._ordinal_en(h2)
        return out + ' house'
    teile = []
    for seg in beleg.split(' · '):
        m = SEG_ASP_RE.match(seg)
        if m and m.group('pa') in namen and m.group('pb') in namen:
            i = seg.index(' %s: ' % m.group('pb'), m.end('pa'))
            teile.append('%s: %s %s: %s' % (m.group('pa'), en(seg[m.end('pa') + 2:i]),
                                            m.group('pb'),
                                            en(seg[i + len(m.group('pb')) + 3:])))
            continue
        m = SEG_UEB_RE.match(seg)
        if m and m.group('p') in namen and m.group('q') in namen:
            f_teil = seg[m.end('p') + 2:m.start('q') - len(' in ')]
            teile.append('%s: %s in %s’s %s%s' % (
                m.group('p'), en(f_teil), m.group('q'),
                haus_en(m.group('h'), m.group('s') or '', m.group('h2')),
                en(m.group('rest'))))
            continue
        m = SEG_STAND_RE.match(seg)
        if m and m.group('p') in namen:
            teile.append('%s: %s' % (m.group('p'), en(seg[m.end('p') + 2:])))
            continue
        teile.append(en(seg))
    return ' · '.join(teile)


def belege_en(analyse_pfad, namen, hand=None):
    """Alle Belege einer analyse.md -> {deutscher Beleg: englischer Beleg} fuer
    chartdoc.konfiguriere(belege_en=…) — die analyse.md behaelt Signatur und
    Beleg deutsch (Modul Sprachfassung). `namen`: die beiden Vornamen.
    `hand`: {deutscher Beleg: englischer Beleg} von Hand (BELEG_HAND der
    Vorlage) — er gilt vor der Mechanik. Schafft die Mechanik einen Beleg
    nicht und steht er nicht in `hand`, bricht es mit SprachfassungError ab
    und nennt ALLE solchen Belege samt Kapitel (typisch: der Getriebe-Beleg
    mit seinen Struktur-Befunden)."""
    import build
    import chartdoc
    hand = hand or {}
    parsed = build.parse_analyse(analyse_pfad)
    out, offen = {}, []
    for c in parsed['chapters']:
        b = c.get('beleg')
        if not b:
            continue
        if b in hand:
            out[b] = hand[b]
            continue
        try:
            out[b] = beleg_en(b, namen)
        except chartdoc.SprachfassungError as e:
            offen.append('%s: %s' % (c['kicker'], e))
    if offen:
        raise chartdoc.SprachfassungError(
            'Englische Fassung: %d Beleg(e) nicht mechanisch uebersetzbar — je den '
            'GANZEN deutschen Beleg als Schluessel mit der englischen Fassung in '
            'BELEG_HAND eintragen:\n  %s' % (len(offen), '\n  '.join(offen)))
    return out


# ---------------------------------------------------------------------------
# Die Beziehung-Probe (Chat 1 nach dem Schreiben, Chat 2 vor dem Render)
# ---------------------------------------------------------------------------

_FAKTOR_WORT = {'Aszendent': 'AC', 'Medium Coeli': 'MC', 'Deszendent': 'DC',
                'Imum Coeli': 'IC'}
_FW = (r'(?P<{n}>Sonne|Mond|Merkur|Venus|Mars|Jupiter|Saturn|Uranus|Neptun|Pluto|'
       r'Mondknoten|Chiron|Lilith|Pholus|Aszendent|Medium Coeli|Deszendent|'
       r'Imum Coeli|AC|MC|DC|IC)(?: \((?:AC|MC|DC|IC)\))?(?: [^\s,A-Za-zÄÖÜäöüß0-9]{{1,2}})?')
_NW = r'(?P<{n}>[A-ZÄÖÜ][\wäöüß\-]*)'
_ZW = (r'(?P<z>Widder|Stier|Zwillinge|Krebs|Löwe|Jungfrau|Waage|Skorpion|Schütze|'
       r'Steinbock|Wassermann|Fische)(?: [^\s,]{1,2})?')
_ASPW = (r'(?P<asp>Konjunktion|Opposition|Quadrat|Trigon|Sextil|Quincunx|Halbsextil)'
         r'(?: [^\s,A-Za-z]{1,2})?')
SEG_STAND_RE = re.compile(
    '^' + _NW.format(n='p') + ': ' + _FW.format(n='f') + r' (?P<g>\d{1,2}°\d{2}′) '
    + _ZW + r'(?:, (?P<h>\d{1,2})\.(?:\s*(?P<s>[/=])\s*(?P<h2>\d{1,2})\.)? Haus)?(?P<rest>.*)$')
SEG_ASP_RE = re.compile(
    '^' + _NW.format(n='pa') + ': ' + _FW.format(n='fa') + ' ' + _ASPW + ' '
    + _NW.format(n='pb') + ': ' + _FW.format(n='fb') +
    r', Orb (?P<orb>\d{1,2}°\d{2}′)(?P<rest>.*)$')
SEG_UEB_RE = re.compile(
    '^' + _NW.format(n='p') + ': ' + _FW.format(n='f') + ' in '
    + _NW.format(n='q') + r'(?:s|’|\') (?P<h>\d{1,2})\.(?:\s*(?P<s>[/=])\s*'
    r'(?P<h2>\d{1,2})\.)? Haus(?P<rest>.*)$')


def _fkanon(w):
    return _FAKTOR_WORT.get(w, w)


def _saetze(text):
    return [s for s in re.split(r'(?<=[.!?…])\s+', text) if s.strip()]


def _ohne_zitate(s):
    return re.sub(r'„[^“]*“|"[^"]*"|»[^«]*«', ' ', s)


def _kicker_art(kicker):
    k = KICKER_EN.get(kicker, kicker) if kicker else ''
    if k.startswith('Kapitel') or k.startswith('Chapter'):
        return 'Kapitel'
    return k


def probe(analyse_pfad, datenblatt_pfad):
    """Die Beziehung-Probe: haelt die Analyse gegen das Datenblatt der
    Beziehung und die Regeln des Moduls. -> Prueftext; letzte Zeile
    `BEZIEHUNGSPROBE: f FEHLER · p PRÜFEN`. Davor der Block „FÜR CHRIS“ mit
    jeder Stelle, die den Satz zum realen Problem traegt (Chris liest sie nach
    der ersten Erstellung, Chris-Entscheidung 2026-10-11).

    Proben: B1 Schema und H1 · B2 Skelett, Kicker, Kopfbloecke · B3 Kapitel
    gegen Themenliste · B4 Bewegungsfolge (Wortlaute der Art) · B5 Belege
    (Staende, Verbindungen mit Orb auf die Bogenminute, Ueberlagerung) · B6
    Heimat im Text (aspekte= im Beleg des Themas, Ressourcen in „Was traegt“,
    enge Achsenkontakte ohne Thema im Getriebe, „Ohne Deutungs-Heimat“ in der
    Rechenschaft) · B7 Leitsatz im Schlusswort ·
    B8 Verwerfungs-Erlaubnis genau zweimal · B9 Anrede · B10 dritte Person ·
    B11 Kind unter 18, bei Eltern-Kind und Freundschaft romantische oder sexuelle
    Lesart (seit 2026-10-14c) · B12 Gleichgewicht beim Paar und bei Freundschaft ·
    B13 Satz zum realen Problem · B14 Wortscan (Regexe aus inhaltsprobe) · B15 Rang-, Zahl- und
    Einzigkeitsaussagen (PRUEFEN gegen die Rangzeilen) · B16 Nichtwissens-Satz
    der Wurzel · B17 kein Urteil ueber die Passung · B18 eng* fuehrt kein Thema ·
    B19 Laengen-Gegenprobe (Mittel der letzten drei Themenkapitel unter 60 %
    der ersten drei ohne form=kurz oder form=ressource: FEHLER, wie
    inhaltsprobe P16) · B20 Subjekt-Probe (Innere Arbeit, Pruefung 1; die
    Satzmuster von inhaltsprobe P17, der Genitiv eines Vornamens gelesen wie
    ein Possessiv: „<B>s Saturn bremst dich“; nur deutsch) · B21 Wiederholung
    (seit 2026-10-11: derselbe Satz mehr als zweimal oder derselbe Satzanfang an
    derselben Stelle in mehr als zwei Kapiteln, die Wegweiser ausgenommen —
    dieselbe Zaehlung wie inhaltsprobe P19, inhaltsprobe.wiederholungen()).
    B13 seit 2026-10-11: der Satz zum realen Problem in „Zur Lesart“ und in
    hoechstens einem weiteren Kapitel. FEHLER ist eindeutig; PRUEFEN braucht
    ein Auge.
    """
    import build
    r = lies_beziehung(datenblatt_pfad)
    na, nb = r['A']['vorname'], r['B']['vorname']
    art = r['art']
    fehler, pruefen, zeilen = [], [], []

    def F(code, text):
        fehler.append('  FEHLER %s: %s' % (code, text))

    def P(code, text):
        pruefen.append('  PRÜFEN %s: %s' % (code, text))
    try:
        parsed = build.parse_analyse(analyse_pfad)
    except Exception as e:
        return 'B1 Schema: FEHLER — %s\nBEZIEHUNGSPROBE: 1 FEHLER · 0 PRÜFEN' % e
    doctype = (parsed.get('doctype') or '').strip()
    # 2026-10-14c: der Dokumenttyp haengt an der Art (Freundschaft: Freundschaftshoroskop)
    soll_de = DOKUMENTTYP.get(art, 'Beziehungshoroskop')
    soll_en = DOKUMENTTYP_EN.get(art, 'Relationship Horoscope')
    if doctype not in (soll_de, soll_en):
        F('B1', 'H1-Dokumenttyp „%s“ statt „%s“' % (doctype, soll_de))
    client = (parsed.get('client') or '').strip()
    if client not in ('%s und %s' % (na, nb), '%s and %s' % (na, nb)):
        F('B1', 'H1-Name „%s“ statt „%s und %s“' % (client, na, nb))
    englisch = doctype == soll_en
    kap = parsed['chapters']
    arten = [_kicker_art(c['kicker']) for c in kap]
    # B2 Skelett
    soll = ['Zur Lesart', 'Getriebe', 'Anlagen'] + ['Kapitel'] * len(
        r['themen']['themen']) + ['Was trägt', 'Lernfelder', 'Rechenschaft', 'Schlusswort']
    if arten != soll:
        F('B2', 'Kapitelfolge %s — erwartet %s' % (' · '.join(arten), ' · '.join(soll)))
    for c, a in zip(kap, arten):
        kb = KOPFBLOCK.get(a)
        if kb is None:
            F('B2', 'Kicker „%s“ gehört nicht zum Skelett' % c['kicker'])
            continue
        if bool(c.get('signatur')) != kb[0]:
            F('B2', '%s: Signatur %s' % (c['kicker'], 'fehlt' if kb[0] else 'gehört nicht hierher'))
        if bool(c.get('beleg')) != kb[1]:
            F('B2', '%s: Beleg %s' % (c['kicker'], 'fehlt' if kb[1] else 'gehört nicht hierher'))
    # B3 Kapitel gegen Themenliste
    kapitel = [c for c, a in zip(kap, arten) if a == 'Kapitel']
    for c, t in zip(kapitel, r['themen']['themen']):
        if c['title'].strip() != t['titel'].strip() and not englisch:
            P('B3', '%s: Titel „%s“ — Themenliste „%s“' % (c['kicker'], c['title'], t['titel']))
    # B4 Bewegungsfolge
    wl = BEWEGUNGEN_EN if englisch else BEWEGUNGEN[art]
    for c, a in zip(kap, arten):
        subs = [b['text'] for b in c['blocks'] if b['type'] == 'subhead']
        if a in ('Kapitel', 'Was trägt'):
            unbekannt = [s for s in subs if s not in wl]
            if unbekannt:
                F('B4', '%s: Zwischentitel außerhalb der Bewegungsfolge: %s' % (
                    c['kicker'], ', '.join('„%s“' % s for s in unbekannt)))
            idx = [wl.index(s) for s in subs if s in wl]
            if idx != sorted(idx) or len(set(idx)) != len(idx):
                F('B4', '%s: Bewegungen nicht in der Folge' % c['kicker'])
            fehlen = [w for i, w in enumerate(wl) if i not in idx and i not in (2, 3)]
            if fehlen:
                F('B4', '%s: es fehlen %s' % (c['kicker'], ', '.join('„%s“' % w for w in fehlen)))
        elif any(s in wl for s in subs):
            F('B4', '%s: trägt Bewegungs-Wortlaute, ist aber kein Kapitel mit Bewegungsfolge'
              % c['kicker'])
    # B5 Belege
    idx = _kreuz_index(r)
    fx = {'A': {f['name']: f for f in r['A']['factors']},
          'B': {f['name']: f for f in r['B']['factors']}}
    wer = {na: 'A', nb: 'B'}
    ueb = {('B', u['faktor']): u for u in r['ueb_b_in_a']}
    ueb.update({('A', u['faktor']): u for u in r['ueb_a_in_b']})
    beleg_keys = {}
    for c, a in zip(kap, arten):
        if not c.get('beleg'):
            continue
        segs = [s.strip() for s in c['beleg'].split(' · ') if s.strip()]
        keys = []
        for s in segs:
            m = SEG_ASP_RE.match(s)
            if m:
                pa_, pb_ = wer.get(m.group('pa')), wer.get(m.group('pb'))
                fa_, fb_ = _fkanon(m.group('fa')), _fkanon(m.group('fb'))
                if not pa_ or not pb_ or pa_ == pb_:
                    F('B5', '%s: „%s“ — Personen nicht %s und %s' % (c['kicker'], s, na, nb))
                    continue
                k = (fa_, fb_, m.group('asp')) if pa_ == 'A' else (fb_, fa_, m.group('asp'))
                e = idx.get(k)
                if e is None:
                    F('B5', '%s: „%s“ — keine solche Verbindung in der Rechnung' % (c['kicker'], s))
                    continue
                if _gr(e['orb']) != m.group('orb'):
                    F('B5', '%s: „%s“ — Orb gerechnet %s' % (c['kicker'], s, _gr(e['orb'])))
                rest = m.group('rest')
                if ', eng' in rest and not e['eng']:
                    F('B5', '%s: „%s“ — nicht eng' % (c['kicker'], s))
                for st_wort, st in (('voll', 'voll'), ('einseitig', 'einseitig'),
                                    ('Nebenaspekt', 'neben')):
                    if (', ' + st_wort) in rest and e['strength'] != st:
                        F('B5', '%s: „%s“ — Stufe gerechnet %s' % (c['kicker'], s, e['strength']))
                keys.append(id(e))
                continue
            m = SEG_UEB_RE.match(s)
            if m:
                p_ = wer.get(m.group('p'))
                q_ = wer.get(m.group('q'))
                f_ = _fkanon(m.group('f'))
                u = ueb.get((p_, f_)) if p_ and q_ and p_ != q_ else None
                if u is None:
                    F('B5', '%s: „%s“ — keine solche Überlagerung' % (c['kicker'], s))
                    continue
                h = int(m.group('h'))
                erlaubt = {u['haus'], u['fuehrend']} | ({u['nebenhaus']} if u['grenzlage'] else set())
                if h not in erlaubt or (m.group('h2') and int(m.group('h2')) not in erlaubt):
                    F('B5', '%s: „%s“ — gerechnet %s' % (c['kicker'], s, u['spalte']))
                keys.append(('ueb', p_, f_))
                continue
            m = SEG_STAND_RE.match(s)
            if m:
                p_ = wer.get(m.group('p'))
                f_ = _fkanon(m.group('f'))
                if not p_ or f_ not in fx[p_]:
                    F('B5', '%s: „%s“ — Person oder Faktor unbekannt' % (c['kicker'], s))
                    continue
                lon = fx[p_][f_]['lon']
                if radix.gr_zeichen(lon) != m.group('g') or zeichen_von(lon) != m.group('z'):
                    F('B5', '%s: „%s“ — gerechnet %s' % (c['kicker'], s, stand_text(lon)))
                if m.group('h'):
                    pp = r[p_]
                    if f_ in ACHSEN:
                        hs = str(radix.haus_und_grenzlage(lon, pp['cusps'], name=f_)['haus'])
                    else:
                        hs = _haus_eigen(pp, f_, lon)
                    geschrieben = m.group('h') + (m.group('s') + m.group('h2') if m.group('h2') else '')
                    if geschrieben != hs and m.group('h') not in re.split(r'[/=]', hs):
                        F('B5', '%s: „%s“ — Haus gerechnet %s' % (c['kicker'], s, hs))
                continue
            if a in ('Kapitel', 'Was trägt', 'Anlagen'):
                F('B5', '%s: Segment nicht lesbar: „%s“' % (c['kicker'], s[:90]))
        beleg_keys[c['kicker']] = keys
    # B6 Heimat im Text
    for c, t in zip(kapitel, r['themen']['themen']):
        bk = beleg_keys.get(c['kicker'], [])
        for tok in t['aspekte']:
            m = ASP_TOKEN_RE.fullmatch(tok)
            k = (_asp_schluessel(m.group('fa'), m.group('pa'), m.group('fb'), m.group('pb'),
                                 na, nb, GLYPHE_ASPEKT.get(m.group('g'))) if m else None)
            e = idx.get(k) if k else None
            if e is not None and id(e) not in bk:
                P('B6', '%s: %s aus der Themenliste steht nicht im Beleg' % (c['kicker'], tok))
    wt = [c for c, a in zip(kap, arten) if a == 'Was trägt']
    bk = beleg_keys.get(wt[0]['kicker'], []) if wt else []
    for x in r['ressourcen']:
        if x['deutungsort'] == 'Was trägt' and id(x['zeile']) not in bk:
            e = x['zeile']
            F('B6', 'Ressource %s %s %s fehlt im Beleg von „Was trägt“' % (
                _mit(e['a'], na), e['name'], _mit(e['b'], nb)))
    gt = [c for c, a in zip(kap, arten) if a == 'Getriebe']
    gk = beleg_keys.get(gt[0]['kicker'], []) if gt else []
    in_thema = set()
    for t in r['themen']['themen']:
        for tok in t['aspekte']:
            m = ASP_TOKEN_RE.fullmatch(tok)
            k = (_asp_schluessel(m.group('fa'), m.group('pa'), m.group('fb'), m.group('pb'),
                                 na, nb, GLYPHE_ASPEKT.get(m.group('g'))) if m else None)
            if k and idx.get(k) is not None:
                in_thema.add(id(idx[k]))
    for e in r['achsen']:
        if e['eng'] and id(e) not in in_thema and id(e) not in gk:
            F('B6', 'enger Achsenkontakt %s %s %s fehlt im Beleg des Getriebes' % (
                _mit(e['a'], na), e['name'], _mit(e['b'], nb)))
    rech = [c for c, a in zip(kap, arten) if a == 'Rechenschaft']
    rtext = ' '.join(b['text'] for b in rech[0]['blocks']) if rech else ''
    for z in r['themen']['ohne']:
        m = ASP_TOKEN_RE.search(z)
        if m and not (m.group('fa') in rtext and m.group('fb') in rtext):
            P('B6', '„Ohne Deutungs-Heimat“ %s: in der Rechenschaft nicht gefunden' % m.group(0))
    # B7 Leitsatz
    sw = [c for c, a in zip(kap, arten) if a == 'Schlusswort']
    if r.get('deckblatt'):
        leit = ' '.join(r['deckblatt'].get('LEITSATZ', '').split())
        swt = ' '.join(' '.join(b['text'] for b in sw[0]['blocks']).split()) if sw else ''
        if leit and leit not in swt:
            F('B7', 'Leitsatz des @@DECKBLATT steht nicht wörtlich im Schlusswort')
    else:
        P('B7', 'kein @@DECKBLATT im Datenblatt — Leitsatz nicht prüfbar')
    # Fliesstext je Kapitel (Absaetze und Listen, ohne Signatur/Beleg)
    def text_von(c):
        return [b for b in c['blocks'] if b['type'] in ('p', 'li')]
    # B8 Verwerfungs-Erlaubnis
    stellen = []
    for c in kap:
        t = ' '.join(b['text'] for b in text_von(c))
        pos = sorted({m.start() for m in VERWERF_RE.finditer(t)})
        cl = []
        for p_ in pos:
            if cl and p_ - cl[-1][-1] < 400:
                cl[-1].append(p_)
            else:
                cl.append([p_])
        stellen += [c['kicker']] * len(cl)
    erstes = kapitel[0]['kicker'] if kapitel else None
    if sorted(stellen) != sorted(['Zur Lesart', erstes]) and not englisch:
        F('B8', 'Verwerfungs-Erlaubnis an %d Stelle(n): %s — erwartet Zur Lesart und %s'
          % (len(stellen), ', '.join(stellen) or '—', erstes))
    # B9 Anrede
    for c in kap:
        for b in text_von(c):
            for s in _saetze(_ohne_zitate(b['text'])):
                # 2026-10-11 (W3): das Nomen „Du“ („sich im Du findet“) ist keine Anrede
                s_nomen = B9_DU_NOMEN_RE.sub('', s)
                if art in IHR_ARTEN and not englisch and B9_DU_RE.search(s_nomen):
                    P('B9', '%s: „du“ %s: %s' % (c['kicker'], 'beim Paar' if art == 'paar'
                                                 else 'bei Freundschaft', s[:120]))
                if art == 'eltern-kind' and not englisch and B9_IHR_RE.search(s):
                    P('B9', '%s: „ihr“ bei Eltern-Kind (die dritte Person wird nicht '
                      'angeredet): %s' % (c['kicker'], s[:120]))
    # B10 dritte Person (Eltern-Kind)
    if art == 'eltern-kind':
        dritte = r[r['kind']]['vorname'] if (r.get('eltern') or 'A') == 'A' \
            else r['B' if r['kind'] == 'A' else 'A']['vorname']
        drit_re = _b10_re(dritte)
        for c in kap:
            for b in text_von(c):
                for s in _saetze(b['text']):
                    if drit_re.search(s) and not REALPROBLEM_RE.search(s):
                        P('B10', '%s: %s' % (c['kicker'], s[:140]))
    # B11 Kind unter 18 — seit 2026-10-14c ausserdem die romantische oder sexuelle
    # Lesart bei Eltern-Kind in jedem Alter und bei Freundschaft (Modul, „Über wen der
    # Text spricht“); nur deutsch, wie B9
    if r.get('kind_minderjaehrig'):
        for c in kap:
            for b in text_von(c):
                for s in _saetze(b['text']):
                    if B11_KIND_RE.search(s):
                        P('B11', '%s: %s' % (c['kicker'], s[:140]))
    elif art in OHNE_ROMANTIK and not englisch:
        for c in kap:
            for b in text_von(c):
                for s in _saetze(b['text']):
                    if ROMANTIK_RE.search(s):
                        P('B11', '%s: romantische oder sexuelle Lesart? %s'
                          % (c['kicker'], s[:140]))
    # B12 Gleichgewicht beim Paar und (seit 2026-10-14c) bei Freundschaft
    if art in IHR_ARTEN:
        alle = ' '.join(b['text'] for c in kap for b in text_von(c))
        # 2026-10-11 (W3): der Genitiv auf -s zaehlt mit („<A>s“); vorher
        # 95 : 205 statt 311 : 302 im Paar-Pruefffall
        def _nennungen(n):
            return len(re.findall(r'(?<!\w)%s(?=s\b|’|\'|\b)' % re.escape(n), alle))
        za, zb = _nennungen(na), _nennungen(nb)
        if min(za, zb) and max(za, zb) / float(min(za, zb)) > 1.5:
            P('B12', '%s %d-mal, %s %d-mal genannt — sind beide Seiten gleich gewichtet?'
              % (na, za, nb, zb))
        seiten = [t['seite'] for t in r['themen']['themen']]
        if abs(seiten.count(na) - seiten.count(nb)) > 1:
            P('B12', 'Themenliste seite=: %s %d, %s %d' % (na, seiten.count(na), nb,
                                                          seiten.count(nb)))
        # 2026-10-11 (W3): „weil <Name>’ Venus …“ spricht ueber einen Stand,
        # nicht ueber die Person — Genitiv ausgenommen
        schuld = re.compile(r'(?:wegen|weil|durch) (?:%s|%s)(?![s’\'\w])|(?:%s|%s) (?:ist|trägt) schuld|'
                            r'schuld (?:ist|hat|trägt) (?:%s|%s)' % ((re.escape(na), re.escape(nb)) * 3))
        for c in kap:
            for b in text_von(c):
                for s in _saetze(b['text']):
                    if schuld.search(s):
                        P('B12', '%s: Schuld in eine Richtung? %s' % (c['kicker'], s[:140]))
    # B13 Satz zum realen Problem
    fuer_chris = []
    zl = [c for c, a in zip(kap, arten) if a == 'Zur Lesart']
    for c in kap:
        akt = None
        for b in c['blocks']:
            if b['type'] == 'subhead':
                akt = b['text']
            elif b['type'] in ('p', 'li') and REALPROBLEM_RE.search(b['text']):
                # 2026-10-11 (BT-P): woertlich, wie das Modul es verlangt —
                # vorher auf 160 Zeichen gekuerzt
                fuer_chris.append('%s%s: „%s“' % (c['kicker'], (' · ' + akt) if akt else '',
                                                   ' '.join(b['text'].split())))
    if not zl or not any(REALPROBLEM_RE.search(b['text']) for b in text_von(zl[0])):
        F('B13', '„Zur Lesart“ trägt den Satz zum realen Problem nicht')
    # 2026-10-11 (Auswertung 11.10., Teil 2, F5; Chris-Entscheidung 11.10.,
    # Nachtrag im Pruefbericht Beziehung Text Paar): ausser in „Zur Lesart“ steht
    # der Satz in hoechstens EINEM Themenkapitel — dem, in dem es um Druck oder ein
    # Nein geht, das gelten muss — als erster Absatz von „Was da arbeitet“. Welches
    # Kapitel das ist, entscheidet der Lauf; die Probe zaehlt nur.
    mit_satz = [(c, a) for c, a in zip(kap, arten) if a != 'Zur Lesart'
                and any(REALPROBLEM_RE.search(b['text']) for b in text_von(c))]
    if len(mit_satz) > 1:
        F('B13', 'Satz zum realen Problem in %d Kapiteln (%s) — erlaubt ist neben „Zur Lesart“ '
          'nur das eine Themenkapitel über Druck oder ein Nein, das gelten muss'
          % (len(mit_satz), ', '.join(c['kicker'] for c, _ in mit_satz)))
    for c, a in mit_satz:
        if a != 'Kapitel':
            P('B13', '%s trägt den Satz zum realen Problem — er gehört in ein Themenkapitel'
              % c['kicker'])
            continue
        erster, sehen = None, False
        for b in c['blocks']:
            if b['type'] == 'subhead':
                sehen = b['text'] == wl[1]
            elif sehen and b['type'] == 'p':
                erster = b['text']
                break
        if not (erster and REALPROBLEM_RE.search(erster)):
            P('B13', '%s: der Satz zum realen Problem steht nicht als erster Absatz von „%s“'
              % (c['kicker'], wl[1]))
    # B14 Wortscan
    try:
        import inhaltsprobe as ip
        regs = [('Klinisches', getattr(ip, 'KLINISCH_RE', None), 'F'),
                ('Bestätigung', getattr(ip, 'BESTAETIGUNG_RE', None), 'F'),
                ('Frist', getattr(ip, 'FRIST_RE', None), 'P'),
                ('Superlativ', getattr(ip, 'SUPERLATIV_RE', None), 'P'),
                ('Fachbegriff', getattr(ip, 'FACHBEGRIFF_RE', None), 'P'),
                ('Gradzahl', getattr(ip, 'GRADZAHL_RE', None), 'P')]
        vern = getattr(ip, 'KLINISCH_VERNEINT_RE', None)
    except Exception:                          # pragma: no cover
        regs, vern = [], None
        P('B14', 'inhaltsprobe nicht ladbar — Wortscan nicht gelaufen')
    for c in kap:
        for b in text_von(c):
            for s in _saetze(b['text']):
                for name, rx, stufe in regs:
                    if rx is None or not rx.search(s):
                        continue
                    if name == 'Klinisches' and vern is not None and vern.search(s):
                        continue
                    (F if stufe == 'F' else P)('B14', '%s · %s: %s' % (c['kicker'], name, s[:130]))
    # B15 Rang, Zahl, Einzigkeit
    rang_re = B15_RANG_RE
    # 2026-10-11 (W3): „ein einziges Mal“, „eine einzige Übung“ (Pflichtsatz in „Zur
    # Lesart“) und „die eine Hälfte eines Spiegels“ sind keine Rang- oder
    # Anteilsaussagen; „zweimal“ ist eine Zahlaussage und kam vorher nicht.
    nicht_rang = B15_NICHT_RANG_RE
    for c in kap:
        for b in text_von(c):
            for s in _saetze(b['text']):
                if rang_re.search(nicht_rang.sub('', s)):
                    P('B15', '%s: %s' % (c['kicker'], s[:140]))
    # B16 Nichtwissens-Satz
    try:
        import inhaltsprobe as ip
        nw = ip.NICHTWISSEN_RE
    except Exception:                          # pragma: no cover
        nw = re.compile(r'wei(?:ß|ss) ich nicht|in keinem Horoskop')
    for c in kap:
        akt, buf = None, {}
        for b in c['blocks']:
            if b['type'] == 'subhead':
                akt = b['text']
            elif akt == wl[2]:
                buf.setdefault(akt, []).append(b['text'])
        if wl[2] in buf and not nw.search(' '.join(buf[wl[2]])):
            F('B16', '%s: „%s“ ohne den Satz, dass ein Horoskop die Herkunft nicht kennt'
              % (c['kicker'], wl[2]))
    # B17 Passung
    for c in kap:
        for b in text_von(c):
            for s in _saetze(b['text']):
                if PASSUNG_RE.search(s):
                    F('B17', '%s: Urteil über die Passung? %s' % (c['kicker'], s[:140]))
                if re.search(r'Composit|Transit', s):
                    P('B17', '%s: Composit/Transit gehören nicht zum %s: %s'
                      % (c['kicker'], soll_de, s[:120]))
    # B18 eng* fuehrt kein Thema
    kipp = _kipp_ids(r) if r.get('zeit', {}).get('eng_kippt') else set()
    for t in r['themen']['themen']:
        m = ASP_TOKEN_RE.fullmatch(t['fuehrt'].strip()) if t['fuehrt'] else None
        if m:
            k = _asp_schluessel(m.group('fa'), m.group('pa'), m.group('fb'), m.group('pb'),
                                na, nb, GLYPHE_ASPEKT.get(m.group('g')))
            e = idx.get(k) if k else None
            if e is not None and id(e) in kipp:
                F('B18', 'Thema %d führt mit %s — eng* (kippt in der Zeitprobe)' % (t['nr'], t['fuehrt']))
            if e is not None and not e['eng']:
                F('B18', 'Thema %d führt mit %s — nicht eng' % (t['nr'], t['fuehrt']))
    # B19 Laengen-Gegenprobe (Datenblatt-Modul, Schritt 2; wie inhaltsprobe P16)
    laengen = [sum(len(b['text']) for b in text_von(c)) for c in kapitel]
    if len(laengen) >= 4:
        n3 = min(3, len(laengen) // 2)
        vorn, hinten = laengen[:n3], laengen[-n3:]
        formen = [t['form'] for t in r['themen']['themen'][-n3:]]
        if sum(hinten) / float(n3) < 0.6 * sum(vorn) / float(n3) and \
                not any(f in ('kurz', 'ressource') for f in formen):
            F('B19', 'die letzten %d Themenkapitel im Mittel %d Zeichen, die ersten %d '
              'im Mittel %d — unter 60 %%: nachschreiben, nicht wegdiskutieren'
              % (n3, sum(hinten) // n3, n3, sum(vorn) // n3))
    # B20 Subjekt-Probe (Leseprobe 2026-10-11: Pruefung 1 der Inneren Arbeit lief
    # sonst nirgends). Zonen wie P17: „Was da arbeitet“ und „Wohin das gehört“
    # sind Anker (frei), die uebrigen Bewegungen streng, Text ohne Bewegung nur
    # mit handelndem Verb.
    if not englisch:
        try:
            import inhaltsprobe as ip
            kand_f, handelt_f = ip._p17_kandidaten, ip._p17_handelt
        except Exception:                      # pragma: no cover
            kand_f = handelt_f = None
            P('B20', 'inhaltsprobe nicht ladbar — Subjekt-Probe nicht gelaufen')
        if kand_f is not None:
            gen_re = re.compile(r'(^|(?<=[\s„(]))(?:%s)(?:s|’|\')(?=\s)'
                                % '|'.join(re.escape(n) for n in (na, nb) if n))
            for c in kap:
                bew = None
                for b in c['blocks']:
                    if b['type'] == 'subhead':
                        bew = b['text']
                        continue
                    if b['type'] not in ('p', 'li') or bew in (wl[1], wl[6]):
                        continue
                    streng = bew in wl
                    for s in _saetze(b['text']):
                        # 2026-10-11 (W3): „der Punkt dessen, was …“ ist kein
                        # Relativsatz; die Definition einer Achse in einem Kapitel
                        # ohne Bewegungen („Der MC ist der Punkt, …“) verortet nur.
                        if not bew and re.match(r'(?:Der|Das|Die) (?:MC|IC|AC|DC|Aszendent|'
                                                r'Deszendent|Medium Coeli|Imum Coeli)\b[^.]{0,40}?'
                                                r'\bist (?:der|die|das) ', s):
                            continue
                        s = re.sub(r'\bdessen, was\b', 'davon, was', s)
                        kand, tok = kand_f(gen_re.sub(lambda m: m.group(1) + 'ihr', s))
                        if not streng:
                            kand = [k for k in kand if handelt_f(tok, k[1], k[2])]
                        if kand:
                            P('B20', '%s%s: „%s“ — %s als Satzsubjekt' % (
                                c['kicker'], (' · ' + bew) if bew else '', s[:110],
                                ', '.join(dict.fromkeys(k[0] for k in kand))))
    # B21 Wiederholung (2026-10-11; Chris-Entscheidung 2026-10-11: hoechstens zweimal
    # gleich, die Wegweiser bleiben) — dieselbe Zaehlung wie inhaltsprobe P19.
    try:
        import inhaltsprobe as ip
        wh_f, wh_z = ip.wiederholungen, ip.wiederholung_zeile
    except Exception:                          # pragma: no cover
        wh_f = None
        P('B21', 'inhaltsprobe nicht ladbar — Wiederholungs-Probe nicht gelaufen')
    if wh_f is not None:
        einheiten = []
        for c, a in zip(kap, arten):
            if a == 'Rechenschaft':
                continue
            bew = None
            for b in c['blocks']:
                if b['type'] == 'subhead':
                    bew = b['text']
                    continue
                if b['type'] in ('p', 'li'):
                    einheiten.append((c['kicker'], bew, b['text']))
        for w in wh_f(einheiten, satzanfaenge=not englisch):
            P('B21', wh_z(w))
    zeilen = ['BEZIEHUNGSPROBE — %s' % os.path.basename(str(analyse_pfad))]
    zeilen += fehler + pruefen
    zeilen.append('FÜR CHRIS — Stellen mit dem Satz zum realen Problem (nach der ersten '
                  'Erstellung zeigen, mit Kapitel und Bewegung):')
    zeilen += ['  %s' % x for x in fuer_chris] or ['  keine']
    zeilen.append('BEZIEHUNGSPROBE: %d FEHLER · %d PRÜFEN' % (len(fehler), len(pruefen)))
    return '\n'.join(zeilen)


def _pruefmuster_text():
    """Anhang an den Docstring von probe(): was die Probe genau liest — gebaut aus
    denselben Objekten, mit denen sie prueft (2026-10-14c, Punkt b), damit
    hilfe('probe') die Pruefgrammatik nennt und Chat 1 den Quelltext nicht liest."""
    def m(rx):
        return rx.pattern if hasattr(rx, 'pattern') else rx
    folgen = '\n'.join('      %s: %s' % (ART_TITEL[a], ' · '.join(BEWEGUNGEN[a]))
                       for a in ARTEN)
    T = """

PRUEFMUSTER — was die Probe genau liest (gebaut aus denselben Objekten, mit
denen sie prueft; einzeln: hilfe('<NAME>')):

Belege (B5, B6): Segmente, getrennt durch „ · “, in einer von drei Formen.
  Stand       <Vorname>: <Faktor> [Symbol] <G°MM′> <Zeichen> [Symbol][, <n>. Haus]
              — Grenzlage „, 11./12. Haus“, offene Fuehrung „, 9.=10. Haus“.
              Beispiel: „Aaa: Venus ♀ 13°00′ Stier ♉, 11. Haus“
  Verbindung  <Vorname>: <Faktor> [Symbol] <Aspekt> [Symbol] <Vorname>: <Faktor>
              [Symbol], Orb <G°MM′> — dahinter erlaubt „, eng“ und „, voll“ |
              „, einseitig“ | „, Nebenaspekt“; Orb, „eng“ und Stufe werden gegen die
              Rechnung gehalten. Beispiel: „Aaa: Venus ♀ Konjunktion ☌ Bbb: Mond ☽,
              Orb 1°48′“
  Stellung    <Vorname>: <Faktor> [Symbol] in <Vorname>s <n>. Haus — Genitiv mit
              Apostroph bei s, ß, x, z („<Vorname>’“), Grenzlage „11./12. Haus“.
              Beispiel: „Bbb: Mond ☽ in Aaas 11. Haus“
  Faktor: Sonne … Pholus, Aszendent (AC), Medium Coeli (MC), Deszendent (DC), Imum
  Coeli (IC) oder das Kuerzel allein. In Themenkapiteln, „Was trägt“ und Anlagen ist
  ein Segment ohne eine der drei Formen FEHLER B5; im Getriebe sind Segmente frei
  (Struktur-Befunde), geprueft werden dort nur Verbindungen und Stellungen.
  Muster: SEG_STAND_RE, SEG_ASP_RE, SEG_UEB_RE.
B6: jede Verbindung aus aspekte= steht im Beleg ihres Kapitels (PRUEFEN); jede
  Ressource mit Deutungsort „Was trägt“ im Beleg von „Was trägt“, jeder enge
  Achsenkontakt ohne Thema im Beleg des Getriebes (FEHLER); jede Zeile „Ohne
  Deutungs-Heimat“ mit beiden Faktoren in der Rechenschaft (PRUEFEN).
B4 Bewegungsfolge: In jedem Themenkapitel und in „Was trägt“ stehen als ### nur
  die Wortlaute der Art, in dieser Folge, jeder hoechstens einmal; fehlen duerfen
  nur Bewegung 3 und 4. Andere Kapitel tragen keinen davon. Englisch BEWEGUNGEN_EN.
%(folgen)s
B8 Verwerfungs-Erlaubnis genau an zwei Stellen, „Zur Lesart“ und das erste
  Themenkapitel (Treffer unter 400 Zeichen Abstand sind EINE Stelle; nur deutsch):
      VERWERF_RE = %(verwerf)s
B9 Anrede (nur deutsch, PRUEFEN je Satz, Zitate „…“ ausgenommen):
  Paar und Freundschaft, „du“:  B9_DU_RE = %(du)s
      — vorher gestrichen, das Nomen „Du“: B9_DU_NOMEN_RE = %(du_nomen)s
  Eltern-Kind, „ihr“:  B9_IHR_RE = %(ihr)s
B10 dritte Person (Eltern-Kind, PRUEFEN je Satz, Gross/klein egal; ein Satz mit
  dem Satz zum realen Problem zaehlt nicht; <VORNAME> = die nicht angeredete Person):
      B10_MUSTER = %(b10)s
B11 (PRUEFEN je Satz, Gross/klein egal) — Kind unter 18:
      B11_KIND_RE = %(b11)s
  sonst bei Eltern-Kind und Freundschaft (nur deutsch):
      ROMANTIK_RE = %(rom)s
B12 Gleichgewicht (Paar und Freundschaft, PRUEFEN): Nennungen der Vornamen samt
  Genitiv im Verhaeltnis ueber 1,5; seite= der Themenliste mehr als 1 auseinander;
  Schuldsaetze „wegen/weil/durch <Vorname>“ (ohne Genitiv), „<Vorname> ist/trägt
  schuld“, „schuld ist/hat/trägt <Vorname>“.
B13 Satz zum realen Problem, in „Zur Lesart“ (FEHLER ohne) und hoechstens EINEM
  Themenkapitel, dort als erster Absatz von „Was da arbeitet“:
      REALPROBLEM_RE = %(real)s
B14 Wortscan mit den Mustern der Inhaltsprobe: FEHLER KLINISCH_RE (ausser verneint,
  KLINISCH_VERNEINT_RE) und BESTAETIGUNG_RE; PRUEFEN FRIST_RE, SUPERLATIV_RE,
  FACHBEGRIFF_RE, GRADZAHL_RE — Muster: inhaltsprobe.hilfe('<NAME>').
B15 Rang, Zahl, Einzigkeit (PRUEFEN je Satz, gegen die Rangzeilen halten):
      B15_RANG_RE = %(rang)s
  vorher gestrichen (keine Rangaussage):
      B15_NICHT_RANG_RE = %(nicht_rang)s
B16 „Wie so etwas zur Regel wird“ traegt den Nichtwissens-Satz (FEHLER ohne):
  inhaltsprobe.NICHTWISSEN_RE.
B17 Urteil ueber die Passung (FEHLER): PASSUNG_RE = %(passung)s
  „Composit“ oder „Transit“ im Text: PRUEFEN.
B18 fuehrt= traegt eine enge Verbindung ohne eng* (FEHLER).
B19 Laengen-Gegenprobe: Mittel der letzten drei Themenkapitel unter 60 %% der ersten
  drei, ohne form=kurz oder form=ressource dort: FEHLER.
B20 Subjekt-Probe (nur deutsch, PRUEFEN): „Was da arbeitet“ und „Wohin das gehört“
  sind frei; in den uebrigen Bewegungen wird jeder Planet und Punkt als Satzsubjekt
  gemeldet, in Text ohne Bewegung (Getriebe, Anlagen, Lernfelder …) nur mit einem
  handelnden Verb (inhaltsprobe._p17_handelt). Der Genitiv eines Vornamens („<B>s
  Saturn“) gilt wie ein Possessiv; ein Satz „Der MC ist der …“ ohne Bewegung ist
  frei. Satzmuster: inhaltsprobe._p17_kandidaten.
B21 Wiederholung (PRUEFEN; Rechenschaft ausgenommen): derselbe Satz (ab 12 Zeichen,
  ausser Wegweisern, inhaltsprobe.WEGWEISER_RE) mehr als zweimal; derselbe Satzanfang
  in derselben Bewegung in mehr als zwei Kapiteln. Satzanfang = das Etikett vor einem
  Doppelpunkt in den ersten sechs Woertern, sonst die ersten vier Woerter, klein
  geschrieben; englisch zaehlt nur der ganze Satz.""" % {
        'folgen': folgen, 'verwerf': m(VERWERF_RE), 'du': m(B9_DU_RE),
        'du_nomen': m(B9_DU_NOMEN_RE), 'ihr': m(B9_IHR_RE), 'b10': B10_MUSTER,
        'b11': m(B11_KIND_RE), 'rom': m(ROMANTIK_RE), 'real': m(REALPROBLEM_RE),
        'rang': m(B15_RANG_RE), 'nicht_rang': m(B15_NICHT_RANG_RE),
        'passung': m(PASSUNG_RE)}
    return T


probe.__doc__ = (probe.__doc__ or '').rstrip() + '\n' + _pruefmuster_text() + '\n'


# ---------------------------------------------------------------------------
# Selbsttest — konstruierte Staende, Platzhalternamen, Daten nur zur Laufzeit
# (Datenschutz-Guardrail: kein Name, kein Datum, keine Uhrzeit realer oder
# erfundener Personen in dieser Datei)
# ---------------------------------------------------------------------------

_T_A = {'Sonne': 10.0, 'Mond': 200.0, 'Merkur': 25.0, 'Venus': 43.0, 'Mars': 280.0,
        'Jupiter': 148.5, 'Saturn': 300.0, 'Uranus': 320.0, 'Neptun': 350.0,
        'Pluto': 230.0, 'Mondknoten': 70.0, 'Chiron': 18.0, 'Lilith': 260.0,
        'AC': 95.0, 'MC': 5.0}
_T_B = {'Sonne': 11.5, 'Mond': 41.2, 'Merkur': 190.3, 'Venus': 98.0, 'Mars': 289.0,
        'Jupiter': 151.0, 'Saturn': 163.5, 'Uranus': 338.0, 'Neptun': 123.5,
        'Pluto': 232.5, 'Mondknoten': 255.0, 'Chiron': 64.0, 'AC': 197.0,
        'MC': 96.0}
_T_CUSPS_A = [(95.0 + 30 * k) % 360 for k in range(12)]
_T_CUSPS_B = [(197.0 + 30 * k) % 360 for k in range(12)]

_T_THEMEN = """## Themenliste der Beziehung

THEMA 1 | titel=Nähe, die sich vertraut anfühlt | fuehrt=Venus (Aaa) ☌ Mond (Bbb) | aspekte=Venus (Aaa) ☌ Mond (Bbb), Sonne (Aaa) ☌ Sonne (Bbb) | ueberlagerung=Mond (Bbb) in Haus 11 von Aaa | seite=beide | form=voll | praxis=ein stiller Abend | leitachse=ja
THEMA 2 | titel=Wort und Wille | fuehrt=Sonne (Aaa) ☍ Merkur (Bbb) | aspekte=Sonne (Aaa) ☍ Merkur (Bbb), Mars (Aaa) ☍ Venus (Bbb) | ueberlagerung=Neptun (Bbb) in Haus 2 von Aaa | seite=Aaa | form=voll | praxis=ein Atemzug

### Ohne Deutungs-Heimat
- Jupiter (Aaa) ☌ Jupiter (Bbb) — eng, in der Rechenschaft genannt
"""

_T_LEITSATZ = 'Nähe wächst dort, wo niemand sie beweisen muss.'
_T_DECKBLATT = """@@DECKBLATT
LEITSATZ: %s
LEITACHSE: Thema 1 — Venus (Aaa) ☌ Mond (Bbb)
TITELMOTIV: zwei Kreise, die einander berühren, in ruhigem Licht
@@ENDE
""" % _T_LEITSATZ

_T_BUNDLE = """@@FILE=01_Planeten_Grundprinzipien.txt@@
@@BLOCK key=GRUNDLAGEN_A@@
------------------------------------------------------------
SONNE ☉
------------------------------------------------------------
Archetyp: der Held
Schatten: der Selbstherrliche

PRINZIP: Das Wesenhafte, Wille und Wärme.

------------------------------------------------------------
MOND ☽
------------------------------------------------------------
Archetyp: die Mutter
Schatten: die Launische

PRINZIP: Gefühl, Geborgenheit und das Bedürfnis nach Nähe.

------------------------------------------------------------
NEPTUN ♆
------------------------------------------------------------
Archetyp: der Träumer
Schatten: der Getäuschte

PRINZIP: Das Grenzenlose, Sehnsucht und Hingabe.
@@FILE=02_Sonne_und_Mond_in_Zeichen.txt@@
@@BLOCK key=SONNE_IN_WIDDER@@
WIDDER – Der Streiter
Tatkraft und Anfang.
@@BLOCK key=MOND_IN_WAAGE@@
------------------------------------------------------------
MOND IN WAAGE ♎ – Die Diplomatin
------------------------------------------------------------
Als Kind – das ausgleichende Kind: Sucht Harmonie.
Inneres Mutterbild: die schöne, freundliche Frau
Schwierige Lernaufgaben: Nein sagen

Als Mutter – die Ausgleichende: Erzieht mit Freundlichkeit und Maß.

Bild der Frau – die Charmante: Verführerisch und gewandt.
@@BLOCK key=MOND_IN_STIER@@
------------------------------------------------------------
MOND IN STIER ♉ – Die Bewahrerin
------------------------------------------------------------
Als Kind – das genießende Kind: Braucht Ruhe und Wiederholung.
Inneres Mutterbild: die nährende Frau
Schwierige Lernaufgaben: Wandel zulassen

Als Mutter – die Nährende: Gibt Sicherheit durch Gewohnheit.

Bild der Frau – die Genießerin: Ruhig und beständig.
@@FILE=05_Aszendent_MC_Deszendent_Tabellen.txt@@
@@BLOCK key=ASZENDENT_KREBS@@
ASZENDENT KREBS – Der Fürsorgliche
@@BLOCK key=ASZENDENT_WAAGE@@
ASZENDENT WAAGE – Der Vermittler
@@FILE=Mond_Aspekte.txt@@
@@BLOCK key=MOND_VENUS@@
MOND – VENUS : Seelenfrieden

ARCHETYP: die anmutige Königin und die Hofdame
SCHATTEN: die Launische und die Eitle

GEGENÜBERSTELLUNG:
Fürsorge – Erotik
Gemüt – Sinnlichkeit
Geborgenheit – Wärme

ALLGEMEIN: Sehnsucht nach Geborgenheit und Harmonie. Von Liebe und Erotik träumen. Ein gutes Gefühl in Fragen von Geschmack und Stil.

EINKLANG: der Charmeur
Harmonie zwischen Gemüt und Ausstrahlung. Stets bereit, sich zu verlieben. Zu tiefer, echter Anteilnahme fähig.

MISSKLANG: der Unerfüllte
Zwischen Geborgenheit und Lust hin- und hergerissen. Emotional unausgeglichen, launisch und schnell gekränkt.
@@FILE=Sonne_Aspekte.txt@@
@@BLOCK key=SONNE_MERKUR@@
SONNE – MERKUR : Der Denker
ALLGEMEIN: Wille und Wort.
@@FILE=Venus_Aspekte.txt@@
@@BLOCK key=VENUS_MARS@@
VENUS – MARS : Die Begegnung
ALLGEMEIN: Wärme und Tatkraft.
@@BLOCK key=VENUS_SATURN@@
VENUS – SATURN : Die Treue
ALLGEMEIN: Wärme und Verlässlichkeit.
@@FILE=Haus_11.txt@@
@@BLOCK key=HAUS_11_ALLG@@
11. HAUS – Freundschaft
Allgemein: Freunde, Gleichgesinnte, Zukunft.
@@FILE=Haus_02_Planeten.txt@@
@@BLOCK key=HAUS_2_ALLG@@
2. HAUS – Besitz
Allgemein: Sicherheit, Werte, Besitz.
"""


def _t_person(pfad, name, geschlecht, geburtsdatum, lons, cusps, jd=None, lat=None,
              lon=None, geburtszeit='nicht angegeben (Selbsttest)', leitachse=True):
    """Selbsttest: schreibt ein Personen-Datenblatt im Format der Pipeline
    (nur, was lies_datenblatt() liest)."""
    z = ['# Datenblatt — %s' % name, '', '## Kopf', '', '- Name: %s' % name,
         '- Geschlecht: %s' % geschlecht,
         '- Geburtsdatum: %s' % geburtsdatum.strftime('%d.%m.%Y'),
         '- Geburtszeit: %s' % geburtszeit, '- Geburtsort: Prüfort (erfunden)',
         '- Fassung: Selbsttest, konstruierte Stände',
         '- Zeitunsicherheit: keine Angabe', '', '## Stände', '',
         '(im Selbsttest ohne Tabelle)', '', '## factors und cusps', '', '```python']
    if jd is not None:
        z.append('JD_UT = %.6f' % jd)
        z.append('LAT, LON = %.6f, %.6f' % (lat, lon))
    z.append('factors = [')
    for n, L in lons.items():
        z.append("    {'name': %r, 'glyph': %r, 'lon': %.6f, 'retro': False},"
                 % (n, radix.FAKTOR_GLYPHE.get(n, n), L))
    z.append(']')
    z.append('CUSPS = %r' % [round(c, 6) for c in cusps])
    z.append('```')
    if leitachse:
        z += ['', '## Themenliste', '',
              'THEMA 1 | titel=Selbsttest-Thema | fuehrt=Sonne | leitachse=ja']
    with open(pfad, 'w', encoding='utf-8') as f:
        f.write('\n'.join(z) + '\n')
    return pfad


def _t_beleg_asp(e, na, nb):
    return '%s: %s %s %s %s: %s, Orb %s' % (
        na, _faktor_beleg(e['a']), e['name'], ASPEKT_GLYPHE[e['name']], nb,
        _faktor_beleg(e['b']), _gr(e['orb']))


def _t_analyse(r, fehler=False):
    """Selbsttest: eine kleine Eltern-Kind-Analyse (A Elternteil, B Kind)."""
    na, nb = r['A']['vorname'], r['B']['vorname']
    traegt = [x['zeile'] for x in r['ressourcen'] if x['deutungsort'] == 'Was trägt']
    beleg_gt = ' · '.join(['%s: Sonne ☉ 10°00′ Widder ♈, 10. Haus' % na,
                           '%s: Sonne ☉ Konjunktion ☌ %s: Sonne ☉, Orb 1°30′' % (na, nb)] +
                          [_t_beleg_asp(e, na, nb) for e in r['achsen'] if e['eng']])
    beleg_wt = ' · '.join(['%s: Venus ♀ 13°00′ Stier ♉, 11. Haus' % na] +
                          [_t_beleg_asp(e, na, nb) for e in traegt])
    lesart_real = ('' if fehler else
                   'Ein echter Streit oder eine echte Angst zwischen dir und %s ist kein '
                   'Thema für ein Horoskop, sondern eines für ein Gespräch mit jemandem, '
                   'dem du vertraust. ' % nb)
    orb_vm = '1°50′' if fehler else '1°48′'
    passung = ' Ihr passt gut zusammen.' if fehler else ''
    saturn = (' %s Saturn bremst dich dabei.' % _genitiv(nb)) if fehler else ''
    T = """# Beziehungshoroskop — {na} und {nb}

## Zur Lesart · Wie du dieses Horoskop liest

Dieses Horoskop legt dein Bild und das Bild von {nb} nebeneinander und zeigt Anlagen, keine Ereignisse.

{lesart_real}Wenn du ein Kapitel nicht wiedererkennst, lass es liegen.

## Getriebe · Wie die beiden Bilder ineinandergreifen

**Signatur:** Zwei Bilder, ein gemeinsamer Takt.

**Beleg:** {beleg_gt}

Die beiden Bilder greifen an wenigen Stellen ineinander, und dort greifen sie fest.

## Anlagen · Was jede Seite mitbringt

**Signatur:** Wärme und ein eigener Takt.

**Beleg:** {na}: Venus ♀ 13°00′ Stier ♉, 11. Haus · {nb}: Mond ☽ 11°12′ Stier ♉, 7. Haus

Du bringst eine ruhige Wärme mit, {nb} einen eigenen Takt.

## Kapitel I · Nähe, die sich vertraut anfühlt

**Signatur:** Eine Nähe, die keine Erklärung braucht.

**Beleg:** {na}: Venus ♀ 13°00′ Stier ♉, 11. Haus · {na}: Venus ♀ Konjunktion ☌ {nb}: Mond ☽, Orb {orb_vm} · {na}: Sonne ☉ Konjunktion ☌ {nb}: Sonne ☉, Orb 1°30′ · {nb}: Mond ☽ in {gen} 11. Haus

### Woran du es merkst

Du merkst es an stillen Abenden mit {nb}, an denen nichts gesagt werden muss.{saturn} Wenn du das nicht wiedererkennst, überspring dieses Kapitel.

### Was da arbeitet

Deine Venus und der Mond von {nb} stehen nah beieinander.{passung}

### Wie so etwas zur Regel wird

Woher dieses Vertrauen kommt, steht in keinem Horoskop.

### Die zwei Formen und das Dazwischen

In der einen Form trägt die Nähe, in der anderen wird sie selbstverständlich.

### Womit du arbeiten kannst

Nimm dir einmal in der Woche Zeit für einen stillen Abend mit {nb}.

### Wohin das gehört

Dieses Thema ist der Boden der anderen Kapitel.

## Kapitel II · Wort und Wille

**Signatur:** Wo dein Wille auf das Wort von {nb} trifft.

**Beleg:** {na}: Sonne ☉ 10°00′ Widder ♈, 10. Haus · {na}: Sonne ☉ Opposition ☍ {nb}: Merkur ☿, Orb 0°18′ · {na}: Mars ♂ Opposition ☍ {nb}: Venus ♀, Orb 2°00′ · {nb}: Neptun ♆ in {gen} 2. Haus

### Woran du es merkst

Du merkst es, wenn ein Wort von {nb} dich trifft und du schneller antwortest, als du willst.

### Was da arbeitet

Wenn aus einem solchen Moment ein echter Streit wird, der dir oder {nb} Angst macht, ist das kein Thema für ein Horoskop. Hier geht es um die Anlage dahinter: Dein Wille und das Wort von {nb} stehen einander gegenüber.

### Die zwei Formen und das Dazwischen

In der einen Form wird aus dem Gegenüber ein Gespräch, in der anderen ein Kräftemessen.

### Womit du arbeiten kannst

Warte einen Atemzug, bevor du antwortest.

### Wohin das gehört

Dieses Thema steht neben dem ersten Kapitel.

## Was trägt · Was von selbst gelingt

**Signatur:** Ein Boden, der hält.

**Beleg:** {beleg_wt}

### Woran du es merkst

Du merkst es daran, dass manches mit {nb} ohne Mühe gelingt.

### Was da arbeitet

Deine Wärme und die Verlässlichkeit von {nb} greifen ineinander.

### Die zwei Formen und das Dazwischen

Genutzt wird daraus ein ruhiger Boden, verschleudert eine Selbstverständlichkeit.

### Womit du arbeiten kannst

Benutze diese Ruhe einmal bewusst und lass sie stehen.

### Wohin das gehört

Dieser Boden trägt beide Kapitel.

## Lernfelder · Was beide üben können

**Signatur:** Geduld und ausgesprochene Wärme.

1. Du übst, einen Atemzug zu warten.
2. Du übst, Wärme auszusprechen.

## Rechenschaft · Was gerechnet und was gedeutet ist

Die Verbindung von Jupiter ({na}) und Jupiter ({nb}) ist eng gerechnet und trägt kein eigenes Kapitel.

## Schlusswort · Was bleibt

{leitsatz}
""".format(na=na, nb=nb, gen=_genitiv(na), lesart_real=lesart_real, orb_vm=orb_vm,
           passung=passung, beleg_wt=beleg_wt, beleg_gt=beleg_gt, leitsatz=_T_LEITSATZ,
           saturn=saturn)
    return T


def _selbsttest():
    """Selbsttest mit konstruierten Staenden und Platzhalternamen. Teile, die
    pyswisseph, matplotlib, build oder chartdoc brauchen, laufen nur, wenn das
    Modul ladbar ist; der Rest immer. Druckt eine Ergebniszeile, wirft
    AssertionError beim ersten Fehlschlag."""
    import io
    import tempfile
    from contextlib import redirect_stdout
    tmp = tempfile.mkdtemp(prefix='bz_selbst_')
    ok, aus = [], []

    def check(bed, text):
        if not bed:
            raise AssertionError('beziehung.py Selbsttest: ' + text)
        ok.append(text)

    heute = _heute_berlin()

    def vor_jahren(n):
        try:
            return heute.replace(year=heute.year - n)
        except ValueError:                               # 29. Februar
            return heute.replace(year=heute.year - n, day=28)

    # 1 Aspekte zwischen zwei Bildern (Huber-Orbis, eng = halber Orbis)
    a = paar_aspekt('Sonne', 0.0, 'Mond', 7.0)
    check(a and a['name'] == 'Konjunktion' and a['strength'] == 'voll' and not a['eng'],
          'voll, nicht eng')
    check(paar_aspekt('Sonne', 0.0, 'Mond', 3.9)['eng'], 'eng bis zum halben Orbis')
    check(paar_aspekt('Venus', 0.0, 'Saturn', 5.5)['strength'] == 'einseitig',
          'einseitig zwischen kleinerem und größerem Orbis')
    a = paar_aspekt('Sonne', 0.0, 'Venus', 63.0)
    check(a['name'] == 'Sextil' and a['strength'] == 'neben' and a['eng'],
          'Sextil als Nebenaspekt, eng auf der Grenze')
    a = paar_aspekt('Merkur', 0.0, 'Mars', 152.0)
    check(a['name'] == 'Quincunx' and not a['eng'], 'Quincunx nicht eng')
    check(paar_aspekt('Mondknoten', 0.0, 'Venus', 6.5) is None and
          paar_aspekt('Mondknoten', 0.0, 'Sonne', 7.5)['strength'] == 'voll',
          'Mondknoten erbt den Orbis des Partners')

    # 2 Datenblaetter, Rechnung, Datenblatt der Beziehung (Eltern-Kind)
    pa = _t_person(os.path.join(tmp, 'Aaa_chart_data.md'), 'Aaa', 'weiblich',
                   vor_jahren(40), _T_A, _T_CUSPS_A)
    pk = _t_person(os.path.join(tmp, 'Bbb_kind_chart_data.md'), 'Bbb', 'weiblich',
                   vor_jahren(10), _T_B, _T_CUSPS_B)
    pp = _t_person(os.path.join(tmp, 'Bbb_paar_chart_data.md'), 'Bbb', 'männlich',
                   vor_jahren(42), _T_B, _T_CUSPS_B)
    th = os.path.join(tmp, 'bz_themen.md')
    db = os.path.join(tmp, 'bz_deckblatt.md')
    open(th, 'w', encoding='utf-8').write(_T_THEMEN)
    open(db, 'w', encoding='utf-8').write(_T_DECKBLATT)
    ziel = os.path.join(tmp, 'Aaa_Beziehung_Bbb_chart_data.md')
    with redirect_stdout(io.StringIO()):
        ek = datenblatt(pa, pk, ziel, 'Eltern-Kind', themen=th, deckblatt=db,
                        datum=heute, beziehung='Mutter und Tochter',
                        einwilligung='beide Sorgeberechtigten (Selbsttest)')
    r = ek['r']
    na, nb = 'Aaa', 'Bbb'
    idx = _kreuz_index(r)
    soll = {('Sonne', 'Sonne', 'Konjunktion'): ('1°30′', True),
            ('Venus', 'Mond', 'Konjunktion'): ('1°48′', True),
            ('Sonne', 'Merkur', 'Opposition'): ('0°18′', True),
            ('Mars', 'Venus', 'Opposition'): ('2°00′', True),
            ('Jupiter', 'Jupiter', 'Konjunktion'): ('2°30′', True),
            ('Venus', 'Saturn', 'Trigon'): ('0°30′', True),
            ('Pluto', 'Pluto', 'Konjunktion'): ('2°30′', False)}
    for k, (orb, eng) in soll.items():
        e = idx.get(k)
        check(e is not None and _gr(e['orb']) == orb and e['eng'] == eng,
              'Verbindung %s %s %s: Orb %s, eng=%s' % (k[0], k[2], k[1], orb, eng))
    sp = [e for e in r['kreuz'] if e['b'] == 'Venus' and e['a'] in ('AC', 'DC')]
    check(len(sp) == 1 and sp[0]['a'] == 'AC' and sp[0].get('spiegel') == 'Opposition DC',
          'Achsen-Spiegel AC/DC als eine Zeile, Konjunktion führt')
    ub = {u['faktor']: u for u in r['ueb_b_in_a']}
    check(ub['Neptun']['haus'] == 1 and ub['Neptun']['fuehrend'] == 2 and
          ub['Neptun']['spalte'] == '2/1', 'Überlagerung Schwellenlage 2/1')
    check(ub['Jupiter']['spalte'] == '2/3' and ub['Jupiter']['fuehrend'] == 2,
          'Überlagerung Grenzlage 2/3')
    check(ub['Mond']['spalte'] == '11', 'Überlagerung ohne Grenzlage')
    check(r['kind'] == 'B' and r['kind_minderjaehrig'], 'Kind unter 18 erkannt')
    rz = radix.rangzeilen_lesen('\n'.join(r['rang']))
    check(all('roh' not in e for v in rz.values() for e in v['eintraege']) and
          {'engste-zwischen-beiden', 'verbindungen-eng-aaa', 'ueberlagerung-bbb-in-aaa',
           'elemente-gewichtet-bbb'} <= set(rz),
          'Rangzeilen lesbar (radix.rangzeilen_lesen), keine roh-Einträge')
    erst = rz['engste-zwischen-beiden']['eintraege'][0]
    check(erst['a'] == 'Sonne(Aaa)' and erst['b'] == 'Merkur(Bbb)' and erst['orb'] == '0°18′',
          'Rangzeile engste Verbindung')
    rb = lies_beziehung(ziel)
    check(len(rb['kreuz']) == len(r['kreuz']) and len(rb['achsen']) == len(r['achsen'])
          and rb['deckblatt']['LEITSATZ'] == _T_LEITSATZ,
          'lies_beziehung rechnet dasselbe, @@DECKBLATT lesbar')
    text = open(ziel, encoding='utf-8').read()
    check(text.index('@@SELEKTOR') < text.index('@@DECKBLATT') and
          'PAAR Venus Mond aspekt=Konjunktion' in text and 'KERN B Mond zeichen=Stier' in text,
          '@@SELEKTOR vor @@DECKBLATT, PAAR- und KERN-Zeilen')
    h = heimat(ziel)
    check(len(h['thema']) == 4 and len(h['ohne_heimat']) == 1 and not h['doppelt'] and
          not h['unbekannt'] and not h['ueb_falsch'] and not h['fehler'] and
          any(x.startswith('Venus (Aaa) △ Saturn (Bbb)') for x in h['was_traegt']),
          'Heimat-Probe: Themen, Was trägt, Ohne Deutungs-Heimat')
    check(heimat_bericht(ziel).startswith('BEZIEHUNG-HEIMAT: %d eng' % len(h['eng'])),
          'Heimat-Ergebniszeile')
    ax = {(e['a'], e['b'], e['name']): e for e in r['achsen']}
    check(set(ax) == {('AC', 'MC', 'Konjunktion'), ('MC', 'MC', 'Quadrat')} and
          ax[('AC', 'MC', 'Konjunktion')].get('spiegel') == 'Opposition IC' and
          ax[('MC', 'MC', 'Quadrat')].get('spiegel') == 'Quadrat IC' and
          len(h['getriebe']) == 2 and 'herkunft=Getriebe' in text,
          'Achsen zueinander: Spiegel zusammengezogen, enge Kontakte ins Getriebe')

    # 3 Referenzschnitt mit Mini-Bibliothek: Filter und Mond-Schnitte
    bp = os.path.join(tmp, 'mini_bundle.txt')
    open(bp, 'w', encoding='utf-8').write(_T_BUNDLE)
    with redirect_stdout(io.StringIO()):
        rs = referenzschnitt(ziel, bp, os.path.join(tmp, 'ek_referenz.md'))
    rt = open(rs['ziel'], encoding='utf-8').read()
    check({'MOND_VENUS', 'SONNE_MERKUR', 'VENUS_MARS', 'VENUS_SATURN', 'HAUS_11_ALLG',
           'HAUS_2_ALLG', 'PRINZIP_SONNE', 'PRINZIP_NEPTUN', 'SONNE_IN_WIDDER',
           'MOND_IN_STIER · Als Kind · B', 'MOND_IN_WAAGE · Als Mutter · A'}
          <= set(rs['bloecke']), 'Referenzschnitt: Paar-, Haus-, Prinzip- und Kernblöcke')
    check('Erotik' not in rt and 'verlieben' not in rt and 'Lust' not in rt and
          'Hingabe' not in rt and 'Geborgenheit' in rt and rs['gefiltert'] >= 5,
          'Eltern-Kind-Filter entfernt Sexuelles und Romantisches, lässt den Rest')
    check('Als Kind – das genießende Kind' in rt and 'Als Mutter – die Ausgleichende' in rt
          and 'Bild der Frau' not in rt and 'Als Mutter – die Nährende' not in rt,
          'Mond: Kind nur „Als Kind“, Elternteil nur „Als Mutter“')
    with redirect_stdout(io.StringIO()):
        zp = os.path.join(tmp, 'paar_chart_data.md')
        datenblatt(pa, pp, zp, 'Paar', themen=th, deckblatt=db, datum=heute)
        rsp = referenzschnitt(zp, bp, os.path.join(tmp, 'paar_referenz.md'))
    check('Erotik' in open(rsp['ziel'], encoding='utf-8').read() and rsp['gefiltert'] == 0,
          'Paar: kein Filter')

    # 3b Freundschaft (2026-10-14c, Wartungslauf „Art Freundschaft“): Kopf, Anrede,
    # Filter ohne Mond-Schnitt, Dateinamen
    with redirect_stdout(io.StringIO()):
        zf = os.path.join(tmp, 'Aaa_Freundschaft_Bbb_chart_data.md')
        fr = datenblatt(pa, pp, zf, 'Freundschaft', themen=th, deckblatt=db, datum=heute,
                        beziehung='Freunde', einwilligung='beide (Selbsttest)')
        rsf = referenzschnitt(zf, bp, os.path.join(tmp, 'fr_referenz.md'))
    ftext = open(zf, encoding='utf-8').read()
    check(fr['r']['art'] == 'freundschaft' and '- Art: Freundschaft' in ftext and
          '- Freundschaftshoroskop: Aaa und Bbb' in ftext and
          'Freundschaft — beide sind Leser: „ihr“' in ftext and
          "ART = 'freundschaft'" in ftext and 'ELTERN = None' in ftext and
          not any('Erwachsen' in x or 'Geburtsdatum' in x for x in fr['r']['anhalten'])
          and lies_beziehung(zf)['kind'] is None,
          'Freundschaft: Kopf, Anrede „ihr“, maschinenlesbarer Block, kein Kind')
    frt = open(rsf['ziel'], encoding='utf-8').read()
    check('Erotik' not in frt and 'verlieben' not in frt and 'Verführerisch' not in frt
          and 'Hingabe' not in frt and rsf['gefiltert'] >= 5 and
          '- Art: Freundschaft — Filter:' in frt,
          'Freundschaft: Referenzschnitt mit dem Filter (nichts Romantisches, nichts Sexuelles)')
    check('Als Kind – das ausgleichende Kind' in frt and 'Als Mutter – die Nährende' in frt
          and 'Bild der Frau – die Charmante: [gefiltert]' in frt,
          'Freundschaft: Mond-Blöcke ganz, ohne den Schnitt „Als Kind“/„Als Mutter“')
    check(dateiname('Freundschaft', 'Aaa', 'Bbb', 'JJJJ-MM-TT', 'pdf') ==
          'Freundschaftshoroskop_Aaa_und_Bbb_JJJJ-MM-TT.pdf' and
          dateiname('freundschaft', 'Aaa', 'Bbb', 'JJJJ-MM-TT', 'pdf', englisch=True) ==
          'Friendship_Horoscope_Aaa_and_Bbb_JJJJ-MM-TT.pdf' and
          dateiname('paar', 'Aaa', 'Bbb', 'JJJJ-MM-TT', 'pdf', englisch=True) ==
          'Relationship_Horoscope_Aaa_and_Bbb_JJJJ-MM-TT.pdf' and
          dateiname('eltern-kind', 'Aaa', 'Bbb', 'JJJJ-MM-TT', 'analyse') ==
          'Aaa_Beziehung_Bbb_JJJJ-MM-TT_analyse.md' and
          dateiname('freundschaft', 'Aaa', 'Bbb', 'JJJJ-MM-TT', 'chart_data', englisch=True)
          == 'Aaa_Freundschaft_Bbb_JJJJ-MM-TT_EN_chart_data.md',
          'dateiname: Kürzel, PDF-Name und _EN je Art')

    # 3c Filter satzweise (2026-10-14c, Punkt a): umbrochene Prosa, Feldköpfe, Listen
    _roh = ('THEMA: Wärme und Hingabe (♀) treffen auf die Achse — Verfeinerung des\n'
            'Wegs oder Ruhe im Vertrauten.\n\n'
            'FLUSS ZUR ACHSE – die tragende Hingabe  Feines Gespür stützt die\n'
            'Richtung mühelos; Gefahr der Trägheit.\n\n'
            'SPANNUNG ZUR ACHSE – Wille und Ziel als Brennpunkt  Der besonders betonte\n'
            'Umschlagpunkt: Kraft gegen Stillstand. Die Lust am Wettstreit treibt\n'
            'voran, ehe die Zeit reif ist.\n\n'
            'GEGENÜBERSTELLUNG:\nFürsorge – Erotik\nGemüt – Wärme\n\n'
            'EINKLANG: der Sinnliche\nRuhe und Takt. Ein Leben in Fülle.\n\n'
            'Waage: freie Partnerwahl und die Freiheit in der Partnerschaft; das '
            'Gleichgewicht / Problem: Unentschlossenheit')
    _neu, _n = _filtern(_roh)
    check(not FILTER_ELTERN_KIND.search(_neu) and _n == 6 and
          'THEMA: [gefiltert]' in _neu and 'Wegs oder' not in _neu and
          'FLUSS ZUR ACHSE: […] Feines Gespür stützt die Richtung mühelos; Gefahr der '
          'Trägheit.' in _neu and
          'SPANNUNG ZUR ACHSE – Wille und Ziel als Brennpunkt  Der besonders betonte '
          'Umschlagpunkt: Kraft gegen Stillstand.' in _neu and 'treibt' not in _neu and
          'Gemüt – Wärme' in _neu and 'Fürsorge' not in _neu and
          'EINKLANG: [gefiltert]\nRuhe und Takt. Ein Leben in Fülle.' in _neu and
          'Waage: […] Problem: Unentschlossenheit' in _neu,
          'Filter satzweise: keine Satzreste, Feldköpfe bleiben, Listenzeilen ganz')
    check(_filtern('Ruhe, ehe der Sturm kommt. Wärme.')[1] == 0 and
          _filtern('In Ehe und Freundschaft.')[1] == 1 and
          _saetze_bibliothek('Nach M. Kelley Hunter u. a. gilt das. Ca. 9 Jahre. Gut.') ==
          ['Nach M. Kelley Hunter u. a. gilt das.', 'Ca. 9 Jahre.', 'Gut.'],
          'Filter: „ehe“ ist keine Ehe; Satzgrenzen nicht nach Initialen und Abkürzungen')

    # 4 Haltegruende
    for fn, text_ in ((lambda: rechnung(pa, pk, 'Paar', datum=heute),
                       'Paar mit einer Person unter 18 hält an'),
                      (lambda: rechnung(pk, pa, 'Eltern-Kind', datum=heute, eltern='B'),
                       'Kind unter 18 bestellt nicht selbst'),
                      (lambda: rechnung(pa, pp, 'Kollegen', datum=heute),
                       'unbekannte Art hält an'),
                      (lambda: rechnung(pa, pk, 'Freundschaft', datum=heute),
                       'Freundschaft mit einer Person unter 18 hält an')):
        try:
            with redirect_stdout(io.StringIO()):
                fn()
            check(False, text_)
        except BeziehungFehler:
            check(True, text_)
    with redirect_stdout(io.StringIO()):
        r2 = rechnung(pa, pp, 'Paar', datum=heute, auftrag_zeit={'B': 'x'})
    check(any('Der Auftrag nennt' in x for x in r2['anhalten']),
          'Fassungsabgleich: andere Geburtszeit im Auftrag -> ANHALTEN')
    check(any('Einwilligung nicht vermerkt' in x for x in r2['anhalten']) and
          not any('Einwilligung' in x for x in r['anhalten']),
          'Einwilligung ohne Vermerk -> ANHALTEN, mit Vermerk nicht')
    with redirect_stdout(io.StringIO()):
        r3 = rechnung(pa, pk, 'Eltern-Kind', datum=heute, eltern='A',
                      einwilligung='liegt vor — <wer: beide | Sorgeberechtigte>')
        pk_alt = _t_person(os.path.join(tmp, 'Bbb_alt_chart_data.md'), 'Bbb', 'weiblich',
                           vor_jahren(70), _T_B, _T_CUSPS_B)
        r4 = rechnung(pa, pk_alt, 'Eltern-Kind', datum=heute, eltern='A',
                      einwilligung='beide')
    check(any('Einwilligung nicht vermerkt' in x for x in r3['anhalten']),
          'Einwilligung als unaufgeräumte Vorlagenzeile -> ANHALTEN')
    check(any('nicht älter' in x for x in r4['anhalten']) and
          not any('nicht älter' in x for x in r['anhalten']),
          'Elternteil nicht älter als das Kind -> ANHALTEN')
    qd = os.path.join(tmp, 'zurueck')
    os.makedirs(qd, exist_ok=True)
    qt, qb = os.path.join(qd, 'bz_themen.md'), os.path.join(qd, 'bz_deckblatt.md')
    check(quellen_aus(ziel, qt, qb) == [qt, qb] and
          open(qt, encoding='utf-8').read().strip() == _T_THEMEN.strip() and
          open(qb, encoding='utf-8').read().strip() == _T_DECKBLATT.strip(),
          'quellen_aus: Themenliste und Deckblatt-Block wortgleich zurück')

    # 2b Kopfformate echter Datenblaetter (2026-10-14, F2) — Platzhalter, erfundene Werte
    _gd = vor_jahren(40).strftime('%d.%m.%Y')
    _jd_t = 2451545.0 + 4321.375
    _roh = open(pa, encoding='utf-8').read()
    _fac = _roh[_roh.index('factors = ['):_roh.index('```', _roh.index('factors = ['))]

    def _variante(datei, kopf, py=''):
        p = os.path.join(tmp, datei)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(kopf + '\n\n## Stände\n\n(im Selbsttest ohne Tabelle)\n\n'
                    '## factors und cusps\n\n```python\n' + py + _fac + '```\n')
        return p
    _g = _variante('Ggg_chart_data.md',
                   '# Chart-Datenblatt — Ggg\n\n## Kopf\n\n- **Name:** Ggg\n'
                   '- **Geschlecht:** weiblich\n- **Geburtsdatum:** %s\n'
                   '- **Geburtszeit:** mittags (Selbsttest), in UT eine Stunde früher\n'
                   '- **Geburtsort:** Prüfort (erfunden)\n'
                   '- **Koordinaten der Rechnung:** 50,0000° N, 10,0000° O (aus Fassung 1)\n'
                   '- **Julianisches Datum (UT):** %.6f\n- **Fassung:** 2 — Selbsttest\n'
                   '- (d) Achsen doppelt: mit den Koordinaten eines Vergleichsorts (51,0000° N, '
                   '11,0000° O) ohne Differenz' % (_gd, _jd_t))
    pg = lies_datenblatt(_g)
    check(abs(pg['jd'] - _jd_t) < 1e-6 and (pg['lat'], pg['lon']) == (50.0, 10.0)
          and pg['vorname'] == 'Ggg' and pg['fassung'].startswith('2'),
          'Datenblatt im Gerüst-Format: jd und Koordinaten der Rechnung, nicht der Vergleichsort')
    _s = _variante('Sss_chart_data.md',
                   '# Datenblatt — Sss\n**Klientin:** Sss · **Geschlecht/Anrede:** weiblich, Du '
                   '· **Fassung 1**  \n**Geburtsdatum:** %s · **Geburtszeit:** mittags (Selbsttest), '
                   'Zone GMT +3 = vormittags UT · JD %.4f  \n**Geburtsort:** Prüfort (erfunden)'
                   % (_gd, _jd_t),
                   py='JD_GEBURT, LAT, LON, ALTER = %.6f, 10.5000, -60.2500, 40\n' % _jd_t)
    ps = lies_datenblatt(_s)
    check(abs(ps['jd'] - _jd_t) < 1e-6 and (ps['lat'], ps['lon']) == (10.5, -60.25)
          and ps['geburtszeit'].startswith('mittags') and ps['geburtsort'] == 'Prüfort (erfunden)'
          and ps['fassung'] == '1' and ps['vorname'] == 'Sss',
          'Datenblatt im September-Format: Tupel JD_GEBURT, Kopfzeilen mit „·“, Fassung ohne Doppelpunkt')
    for _k, _soll in (('Koordinaten der Rechnung: 50°00′00″ S, 10°30′00″ W', (-50.0, -10.5)),
                      ('Koordinaten der Rechnung: 50.0000 N, 10.0000 O (50°00′ N / 10°00′ O)',
                       (50.0, 10.0)),
                      ('Koordinaten (Setzung des Laufs): 10°30′ N, 60°15′ W (Dezimal 10.5000 / '
                       '\u221260.2500)', (10.5, -60.25)),
                      ('Koordinaten der Rechnung: 50°00′00″ N, 10°00′00″ O (50.00000, 10.00000; '
                       'Prüfort)', (50.0, 10.0)),
                      ('Koordinaten der Rechnung: 50,0000° N, 10,0000° O (51.00000, 10.00000; '
                       'Widerspruch)', (None, None)),
                      ('Ortskoordinaten (Setzung dieses Laufs): Prüfort, 50°00′00″ N, 10°00′00″ O',
                       (50.0, 10.0))):
        check(_koord_aus_zeile(_k.split(':', 1)[1]) == _soll if _soll[0] is None else
              all(abs(a - b) < 1e-9 for a, b in zip(_koord_aus_zeile(_k.split(':', 1)[1]), _soll)),
              'Koordinatenzeile: %s' % _k[:60])
    for _h1 in ('# Transit-Horoskop — Datenblatt — Ttt', '# Chart-Datenblatt Transit — Ttt'):
        _t = _variante('Ttt_Transit_chart_data.md', _h1 + '\n\n## Kopf\n\n- Name: Ttt\n'
                       '- JD (UT): %.6f' % _jd_t)
        try:
            lies_datenblatt(_t)
            check(False, 'Transit-Datenblatt abgelehnt: %s' % _h1)
        except BeziehungFehler as e:
            check('Transit-Datenblatt' in str(e) and 'Schritt 1' in str(e),
                  'Transit-Datenblatt abgelehnt: %s' % _h1)
    _o = _variante('Ooo_chart_data.md',
                   '# Chart-Datenblatt — Ooo\n\n| Feld | Wert |\n|---|---|\n'
                   '| Geburtsdatum | %s |\n| Ortskoordinaten (Setzung dieses Laufs) | '
                   '**50.0000 N / 10.0000 O** | erfunden |\n| Julianisches Datum (UT) | %.6f |'
                   % (_gd, _jd_t))
    po = lies_datenblatt(_o)
    check(abs(po['jd'] - _jd_t) < 1e-6 and (po['lat'], po['lon']) == (50.0, 10.0),
          'Datenblatt mit Tabellenkopf: Ortskoordinaten als Tabellenzeile')
    # 2026-10-14b (FFU, Auswertung 14.10. c): der ganze Kopf als Tabelle, das Geschlecht
    # gross geschrieben, die Zeile „**Geburt:** …“, ein Datum mit Monatsnamen
    _gd_n = vor_jahren(40)
    _o2 = _variante('Ppp_chart_data.md',
                    '# Chart-Datenblatt — Ppp\n\n**Klientin: Ppp** (erfunden). Weiblich, '
                    'Anrede „du“.\n\n| Angabe | Wert |\n|---|---|\n'
                    '| Geburtsdatum | %s (Selbsttest) |\n| Geburtszeit | mittags (Selbsttest) |\n'
                    '| Geburtsort | Prüfort (erfunden) |\n'
                    '| Ortskoordinaten (Setzung dieses Laufs) | 50.0000 N / 10.0000 O |\n'
                    '| Julianisches Datum (UT) | %.6f |\n| Fassung | Fassung 1 (Selbsttest) | — |\n'
                    '| Zeitunsicherheit | eine Minute (Selbsttest) |' % (_gd, _jd_t))
    pp2 = lies_datenblatt(_o2)
    check(pp2['geburtsdatum'] == _gd_n and pp2['geburtszeit'] == 'mittags (Selbsttest)'
          and pp2['geburtsort'] == 'Prüfort (erfunden)' and pp2['fassung'].startswith('1')
          and pp2['zeitunsicherheit'].startswith('eine Minute')
          and pp2['geschlecht'] == 'weiblich',
          'Datenblatt mit Tabellenkopf: alle Kopfangaben, Geschlecht groß geschrieben')
    _o3 = _variante('Qqq_chart_data.md',
                    '# Chart-Datenblatt — Qqq\n\n**Chart-Subjekt:** Qqq (männlich)\n'
                    '**Geburt:** %s, mittags (Selbsttest) = vormittags UT · Geburtsort: '
                    'Prüfort (erfunden)\n- JD (UT): %.6f' % (_gd, _jd_t))
    pq = lies_datenblatt(_o3)
    check(pq['geburtsdatum'] == _gd_n and pq['geburtszeit'].startswith('mittags')
          and pq['geburtsort'] == 'Prüfort (erfunden)' and pq['geschlecht'] == 'männlich',
          'Kopfzeile „**Geburt:** Datum, Zeit · Geburtsort: …“')
    _pz = lies_datenblatt(_variante('Zzz_chart_data.md',
                                    '# Chart-Datenblatt — Zzz\n\nGeburtsdatum: %s\n'
                                    'Geburtszeit: mittags (Selbsttest)\nGeburtsort: Prüfort (erfunden)\n'
                                    '- JD (UT): %.6f' % (_gd, _jd_t)))
    check(_pz['geburtsdatum'] == _gd_n and _pz['geburtszeit'] == 'mittags (Selbsttest)'
          and _pz['geburtsort'] == 'Prüfort (erfunden)', 'Kopf in schlichten Zeilen „Geburtszeit: …“')
    _mon = [k for k, v in _MONATE.items() if v == _gd_n.month][0]
    check(lies_datenblatt(_variante('Rrr_chart_data.md',
                                    '# Chart-Datenblatt — Rrr\n\n- **Geburtsdatum:** %d. %s %d'
                                    '\n- JD (UT): %.6f' % (_gd_n.day, _mon, _gd_n.year, _jd_t))
                          )['geburtsdatum'] == _gd_n, 'Geburtsdatum mit Monatsnamen')
    # 2026-10-14b (F4): Gleichstand am Ende der Elemente
    _el = {n: 3.0 for n in radix._ELEM_NAMES}
    _el[radix._ELEM_NAMES[1]] = _el[radix._ELEM_NAMES[3]] = 5.0
    check(_schwaechstes_element({'gewichtet': {'elemente': _el}}) == '%s und %s gleichauf'
          % (radix._ELEM_NAMES[0], radix._ELEM_NAMES[2]) and
          _schwaechstes_element({'gewichtet': {'elemente': dict(_el, **{radix._ELEM_NAMES[0]:
                                                                       4.0})}})
          == radix._ELEM_NAMES[2], 'schwächstes Element: Gleichstand benannt, sonst eines')
    # 2026-10-14b (F5): die führende Verbindung zählt in aspekte= mit, ohne Doppelung
    _lt = lies_themen('## Themenliste der Beziehung\n\n'
                      'THEMA 1 | titel=Probe | fuehrt=Sonne (Aaa) △ Mond (Bbb) | '
                      'aspekte=Venus (Aaa) □ Mars (Bbb) | leitachse=ja\n'
                      'THEMA 2 | titel=Probe zwei | fuehrt=Mond (Bbb) △ Sonne (Aaa) | '
                      'aspekte=Sonne (Aaa) △ Mond (Bbb)\n')['themen']
    check(_lt[0]['aspekte'] == ['Sonne (Aaa) △ Mond (Bbb)', 'Venus (Aaa) □ Mars (Bbb)']
          and _lt[1]['aspekte'] == ['Sonne (Aaa) △ Mond (Bbb)'],
          'führende Verbindung in aspekte= mitgezählt, gleiche Verbindung nicht doppelt')
    check('table.bz-st td:nth-child(2) { white-space:nowrap; }' in BEZIEHUNG_CSS,
          'Ständetabelle: Grad und Zeichen bleiben in einer Zeile')
    check(lies_datenblatt(_variante('Vvv_chart_data.md',
                                    '# Geburtshoroskop — Datenblatt — Vvv\n\n## Kopf\n\n'
                                    '- Geburtsdatum: %s' % _gd))['vorname'] == 'Vvv',
          'Vorname hinter dem letzten Gedankenstrich der H1')
    # 2026-10-15 (FFU, Auswertung 14.10. d, Punkt 2): Kopf von Mitte September — H1
    # „Datenblatt — Geburtshoroskop <Vorname> <Nachname>“, alles als Tabelle; geprueft wird
    # JEDES Kopffeld, nicht nur das gemeldete (die Formatprobe vom 14.10. zaehlte nur jd
    # und Koordinaten)
    _o4 = _variante('Uuu_Nnn_chart_data.md',
                    '# Datenblatt — Geburtshoroskop Uuu Nnn\n\n| Feld | Wert |\n|---|---|\n'
                    '| Name | Uuu Nnn |\n| Geschlecht | weiblich |\n'
                    '| Geburtsdatum | %s |\n| Geburtszeit | mittags (Selbsttest) |\n'
                    '| Geburtsort | Prüfort (erfunden) |\n'
                    '| Ortskoordinaten (Setzung dieses Laufs) | 50.0000 N / 10.0000 O |\n'
                    '| Julianisches Datum (UT) | %.6f |\n| Fassung | Fassung 1 (Selbsttest) |\n'
                    '| Zeitunsicherheit | eine Minute (Selbsttest) |' % (_gd, _jd_t))
    pu = lies_datenblatt(_o4)
    check(pu['vorname'] == 'Uuu' and pu['geschlecht'] == 'weiblich'
          and pu['geburtsdatum'] == _gd_n and pu['geburtszeit'] == 'mittags (Selbsttest)'
          and pu['geburtsort'] == 'Prüfort (erfunden)' and pu['fassung'].startswith('1')
          and pu['zeitunsicherheit'].startswith('eine Minute')
          and abs(pu['jd'] - _jd_t) < 1e-6 and (pu['lat'], pu['lon']) == (50.0, 10.0),
          'Datenblatt von Mitte September (H1 „Datenblatt — Geburtshoroskop <Name>“, Kopf '
          'als Tabelle): jedes Kopffeld, Vorname nicht „Geburtshoroskop“')
    for _datei, _kopf, _soll in (
            ('Www_Nnn_chart_data.md', '# Geburtshoroskop — Datenblatt (Schritt 1)\n\n'
             '- **Name:** Www Nnn', 'Www'),
            ('Ttt_Nnn_chart_data.md', '# Datenblatt — Ultimativ-Horoskop\n\n| Name | Ttt Nnn |',
             'Ttt'),
            ('Kkk_chart_data.md', '# Datenblatt — Kombi-Horoskop Kkk', 'Kkk'),
            ('Eee_chart_data.md', '# Datenblatt — Eee · Standard-Geburtshoroskop', 'Eee'),
            ('Ddd_chart_data.md', '# Chart-Datenblatt — Ddd Nnn (Ultimativ-Horoskop)', 'Ddd'),
            ('Mmm_chart_data.md', '# Datenblatt Modul III — Datenblatt Modul III\n\n'
             'Name: Mmm Nnn', 'Mmm'),
            ('fff_nnn_chart_data.md', '# Geburtshoroskop — Datenblatt (Schritt 1)', 'Fff'),
            ('chart_data.md', '# Geburtshoroskop — Datenblatt', '?')):
        check(lies_datenblatt(_variante(_datei, '%s\n- Geburtsdatum: %s' % (_kopf, _gd)))
              ['vorname'] == _soll, 'Vorname „%s“: %s' % (_soll, _kopf.split('\n')[0]))
    with redirect_stdout(io.StringIO()):
        _rx = rechnung(os.path.join(tmp, 'chart_data.md'), _s, 'Paar', datum=heute,
                       einwilligung='beide (Selbsttest)')
        _ry = rechnung(_o4, _s, 'Paar', datum=heute, einwilligung='beide (Selbsttest)')
    check(any('kein Vorname lesbar' in x for x in _rx['anhalten'])
          and not any('kein Vorname' in x for x in _ry['anhalten']),
          'ohne lesbaren Vornamen -> ANHALTEN, mit Vornamen nicht')
    # 2026-10-15 (FFU, Auswertung 14.10. d, Punkt 1): offene Fuehrung des eigenen Hauses aus
    # `fuehrung=offen` des Personen-Datenblatts — Staende und Staendeseite „2=3“ wie im
    # Geburtshoroskop (vorher „3/2“, die Stufe allein); ein aelteres Datenblatt der Beziehung
    # ohne das Feld bleibt lesbar
    _po = os.path.join(tmp, 'Bbb_offen_chart_data.md')
    with open(_po, 'w', encoding='utf-8') as f:
        f.write(open(pp, encoding='utf-8').read() + '\n## @@SELEKTOR-Block\n\n```\n@@SELEKTOR\n'
                'FAKTOR MONDKNOTEN zeichen=%s haus=2 nebenhaus=3 abstand=2.00 fuehrung=offen\n'
                'FAKTOR SATURN zeichen=%s haus=11 nebenhaus=12 abstand=3.50\n@@ENDE\n'
                '@@DECKBLATT\nFAKTOR SONNE fuehrung=offen\n@@ENDE\n```\n'
                % (zeichen_von(_T_B['Mondknoten']), zeichen_von(_T_B['Saturn'])))
    check(lies_datenblatt(_po)['offen_eigen'] == ['Mondknoten']
          and lies_datenblatt(pp)['offen_eigen'] == [],
          'offene Führung des eigenen Hauses aus fuehrung=offen gelesen, nur im @@SELEKTOR-Block')
    with redirect_stdout(io.StringIO()):
        zo = os.path.join(tmp, 'Aaa_Beziehung_Bbbo_chart_data.md')
        datenblatt(pa, _po, zo, 'Paar', themen=th, deckblatt=db, datum=heute,
                   einwilligung='beide (Selbsttest)')
    _ot = open(zo, encoding='utf-8').read()
    _ro = lies_beziehung(zo)
    check(re.search(r'^\| Mondknoten \|[^|\n]*\|[^|\n]*\| 2=3 \|', _ot, re.M)
          and re.search(r'^\| Saturn \|[^|\n]*\|[^|\n]*\| 11/12 \|', _ot, re.M)
          and _ro['B'].get('offen_eigen') == ['Mondknoten'] and _ro['A'].get('offen_eigen') == [],
          'Stände: offene Führung des eigenen Hauses „2=3“, sonst „11/12“; maschinenlesbar')
    _alt = _ot.replace(", 'offen_eigen': ['Mondknoten']", '')
    check(_alt != _ot, 'Selbsttest: PERSON_B trägt offen_eigen')
    za = os.path.join(tmp, 'Aaa_Beziehung_Bbba_chart_data.md')
    open(za, 'w', encoding='utf-8').write(_alt)
    _ra = lies_beziehung(za)
    try:
        import chartdoc  # noqa: F401
        check('<td>2=3</td>' in staende_page(_ro) and '<td>2=3</td>' not in staende_page(_ra)
              and _ra['B'].get('offen_eigen') is None,
              'Ständeseite: „2=3“ aus dem Datenblatt der Beziehung; älteres ohne Feld lesbar')
    except ImportError:
        aus.append('Ständeseite offene Führung (chartdoc fehlt)')
    with redirect_stdout(io.StringIO()):
        _r0 = rechnung(pa, pp, 'Paar', datum=heute, einwilligung='beide (Selbsttest)')
        _r1 = rechnung(_g, _s, 'Paar', datum=heute, einwilligung='beide (Selbsttest)')
    check(sum(1 for x in _r0['anhalten'] if 'nicht lesbar' in x) == 2 and
          not any('nicht lesbar' in x for x in _r1['anhalten']),
          'ohne jd oder Koordinaten -> ANHALTEN, mit beiden nicht')
    check(sum(1 for x in _r1['anhalten'] if 'ohne Leitachse' in x) == 2 and
          not any('ohne Leitachse' in x for x in _r0['anhalten']) and
          not any('nicht lesbar' in x for x in _r1['anhalten']),
          'ohne Leitachse -> ANHALTEN, mit Leitachse nicht')

    # 5 Zeitprobe (pyswisseph)
    swe = _swe()
    if swe is None:
        aus.append('Zeitprobe (pyswisseph fehlt)')
    else:
        jd0, lat, lon = 2451545.0 + 4321.375, 50.0, 10.0
        c0, ax0 = _achsen_bei(swe, jd0, lat, lon)
        cm15 = _achsen_bei(swe, jd0 - 1.5 / 1440.0, lat, lon)[0]
        cm03 = _achsen_bei(swe, jd0 - 0.3 / 1440.0, lat, lon)[0]
        axp1 = _achsen_bei(swe, jd0 + 1.0 / 1440.0, lat, lon)[1]
        za = {'vorname': 'Aaa', 'jd': jd0, 'lat': lat, 'lon': lon, 'cusps': c0,
              'factors': [{'name': n, 'lon': ax0[n]} for n in ACHSEN]}
        zb = {'vorname': 'Bbb', 'jd': None, 'lat': None, 'lon': None,
              'cusps': [(ax0['AC'] + 15.0 + 30 * k) % 360 for k in range(12)],
              'factors': [{'name': 'Mond', 'lon': (cm15[6] - 2.0) % 360},
                          {'name': 'Sonne', 'lon': (cm03[3] - 2.0) % 360},
                          {'name': 'Venus', 'lon': (axp1['AC'] + 2.5) % 360}]}
        z = zeitprobe(za, zb)
        km = [k for k in z['A']['kippt'] if k['was'] == 'überlagerung'
              and k['faktor'] == 'Mond']
        check(('B', 'Mond') in z['ueb_kippt'] and km and abs(km[0]['minuten'] - 1.5) < 0.05
              and km[0]['richtung'] == 'früher', 'Zeitprobe: führendes Haus kippt')
        check('Sonne' in z['offen']['A'] and 'Mond' not in z['offen']['A'],
              'Zeitprobe: offene Führung unter einer Minute')
        check(('AC', 'Venus', 'Konjunktion') in z['eng_kippt'] and
              any('AC/DC' in x and 'Venus' in x and 'wird eng' in x for x in z['zeilen']),
              'Zeitprobe: „eng“ kippt, Spiegelzeile AC/DC zusammengezogen')
        check(any('Zeitprobe für Bbb nicht gerechnet' in w for w in z['warnungen']),
              'Zeitprobe ohne jd: Warnung')

    # 6b Legende im Beziehungshoroskop (2026-10-14, F3)
    try:
        import chartdoc as _cd
    except ImportError:
        _cd = None
    if _cd is None:
        aus.append('Legende (chartdoc fehlt)')
    else:
        _cd.setze_sprache('de')
        legende_beziehung(_cd)
        _h = _cd.aspekt_legende()
        check('zu ständigem Nachjustieren zwingen' in _h and 'nicht zusammenpassen' not in _h,
              'Legende deutsch: Quincunx nach Regel 5')
        _cd.setze_sprache('en')
        legende_beziehung(_cd)
        _h = _cd.aspekt_legende()
        check('constant readjustment' in _h and 'do not fit together' not in _h,
              'Legende englisch: Quincunx nach Regel 5')
        _cd.setze_sprache('de')
        check('nicht zusammenpassen' in _cd.aspekt_legende(),
              'setze_sprache stellt danach die Hausstil-Legende wieder her')

    # 6 Doppelrad und Seiten
    try:
        import matplotlib  # noqa: F401
        png = doppelrad(ziel, os.path.join(tmp, 'doppelrad.png'), dpi=90)
        check(os.path.getsize(png) > 10000, 'Doppelrad gezeichnet')
    except ImportError:
        aus.append('Doppelrad (matplotlib fehlt)')
    try:
        import chartdoc  # noqa: F401
        html = kreuz_page(rb)
        check(html.count('<td class="ao">') == len(rb['kreuz']) + len(rb['achsen']),
              'Verbindungsseite: eine Orb-Zelle je Zeile (Sollzahl für build.verify)')
        check('2/1' in staende_page(rb), 'Ständeseite mit Überlagerung')
    except ImportError:
        aus.append('Seiten (chartdoc fehlt)')

    # 7 Die Beziehung-Probe
    try:
        import build  # noqa: F401
    except ImportError:
        build = None
        aus.append('Beziehung-Probe (build fehlt)')
    if build is not None:
        ap = os.path.join(tmp, 'gut_analyse.md')
        open(ap, 'w', encoding='utf-8').write(_t_analyse(rb))
        pr = probe(ap, ziel)
        letzte = pr.strip().splitlines()[-1]
        check(letzte.startswith('BEZIEHUNGSPROBE: 0 FEHLER'),
              'Probe: saubere Analyse ohne FEHLER (%s)' % letzte)
        fc = pr.split('FÜR CHRIS', 1)[1]
        check(fc.count('„') == 2 and 'Zur Lesart' in fc and 'Was da arbeitet' in fc,
              'Probe: „FÜR CHRIS“ nennt beide Stellen mit Kapitel und Bewegung')
        ap2 = os.path.join(tmp, 'fehler_analyse.md')
        open(ap2, 'w', encoding='utf-8').write(_t_analyse(rb, fehler=True))
        pr2 = probe(ap2, ziel)
        check('FEHLER B5' in pr2 and 'FEHLER B13' in pr2 and 'FEHLER B17' in pr2,
              'Probe: falscher Orb, fehlender Satz zum realen Problem, Urteil über die Passung')
        check('PRÜFEN B20' in pr2 and 'Saturn als Satzsubjekt' in pr2 and 'B20' not in pr,
              'Probe: Planet als Satzsubjekt auch im Genitiv des Vornamens (B20)')
        pr3 = probe(ap, zp)
        check('FEHLER B4' in pr3 and 'PRÜFEN B9' in pr3,
              'Probe: Paar verlangt „ihr“-Wortlaute und kein „du“')
        # 2026-10-11 (Auswertung 11.10., Teil 2, F5): Satz zum realen Problem in
        # einem zweiten Kapitel -> FEHLER; FÜR CHRIS woertlich, nicht gekuerzt.
        gut = open(ap, encoding='utf-8').read()
        zwei = gut.replace('Deine Wärme und die Verlässlichkeit von',
                           'Wenn daraus eine Angst wird, die bleibt, ist das kein Thema für ein '
                           'Horoskop. Deine Wärme und die Verlässlichkeit von', 1)
        check(zwei != gut, 'Selbsttest: Einfügestelle für den zweiten Satz fehlt')
        ap4 = os.path.join(tmp, 'zwei_saetze_analyse.md')
        open(ap4, 'w', encoding='utf-8').write(zwei)
        pr4 = probe(ap4, ziel)
        check('FEHLER B13' in pr4 and 'in 2 Kapiteln' in pr4,
              'Probe: Satz zum realen Problem in zwei Kapiteln (B13, F5)')
        check('B21' not in pr, 'Probe: saubere Analyse ohne Wiederholungs-Meldung (B21)')
        check(all(len(z) > 0 for z in pr.split('FÜR CHRIS', 1)[1].splitlines()[1:3])
              and '…' not in pr.split('FÜR CHRIS', 1)[1],
              'Probe: „FÜR CHRIS“ ungekürzt')
        # 2026-10-14c: Freundschaft — H1 je Art (B1), „ihr“-Wortlaute (B4), kein „du“
        # (B9), romantische oder sexuelle Lesart (B11)
        fr_an = gut.replace('# Beziehungshoroskop — ', '# Freundschaftshoroskop — ', 1).replace(
            'Du bringst eine ruhige Wärme mit', 'Du bringst eine ruhige, sinnliche Wärme mit', 1)
        check(fr_an.count('Freundschaftshoroskop') == 1 and 'sinnliche' in fr_an,
              'Selbsttest: Einfügestellen der Freundschafts-Analyse fehlen')
        ap5 = os.path.join(tmp, 'freundschaft_analyse.md')
        open(ap5, 'w', encoding='utf-8').write(fr_an)
        pr5 = probe(ap5, zf)
        check('FEHLER B1' not in pr5 and 'FEHLER B4' in pr5 and
              '„du“ bei Freundschaft' in pr5 and
              'PRÜFEN B11: Anlagen: romantische oder sexuelle Lesart?' in pr5,
              'Probe Freundschaft: Wortlaute „ihr“, kein „du“, Romantik-Probe (B4, B9, B11)')
        pr6 = probe(ap, zf)
        check('FEHLER B1: H1-Dokumenttyp „Beziehungshoroskop“ statt „Freundschaftshoroskop“'
              in pr6, 'Probe Freundschaft: H1 „Freundschaftshoroskop“ verlangt (B1)')
        # 2026-10-14c (Punkt b): hilfe('probe') nennt die Pruefmuster
        _h = io.StringIO()
        with redirect_stdout(_h):
            hilfe('probe')
        _h = _h.getvalue()
        check('PRUEFMUSTER' in _h and B9_DU_RE.pattern in _h and ROMANTIK_RE.pattern in _h
              and B15_RANG_RE.pattern in _h and 'SEG_ASP_RE' in _h and
              'Freundschaft: ' + BEWEGUNGEN['freundschaft'][0] in _h,
              "hilfe('probe') nennt Segmentformen, Bewegungsfolgen und Wortlisten")
    # 2026-10-11 (F5/K-a, W3, W4): Muster ohne Datei
    check(REALPROBLEM_RE.search('Ob zwei Menschen zusammenpassen, sagt es nicht; das kann '
                                'kein Horoskop.') is None
          and REALPROBLEM_RE.search('Dann ist das kein Thema für ein Horoskop, sondern eines '
                                    'für ein Gespräch.') is not None,
          'REALPROBLEM_RE: nur die Wendung des Moduls')
    for _satz, _soll in (('Ihr Denken und sein Handeln passen nicht zusammen.', True),
                         ('Sein Ernst passt nicht mit ihrer Leichtigkeit zusammen.', True),
                         ('Zwei Kräfte, die nicht zusammenpassen, reiben sich.', True),
                         ('Ob zwei Menschen zusammenpassen, sagt es nicht.', False),
                         ('Die beiden Arten greifen nicht glatt ineinander.', False)):
        check(bool(PASSUNG_RE.search(_satz)) == _soll, 'PASSUNG_RE: %s' % _satz)
    # B15-Ausnahmen (2026-10-11, W3) — dieselbe Liste wie in probe(), hier nur als Muster
    for _satz, _soll in (('Genau diesen Saturn berührt ihr Bild zweimal.', True),
                         ('Wenn du es ein- oder zweimal bemerkst, reicht es.', False),
                         ('Nimm eine einzige Übung mit.', False),
                         ('Das ist die einzige Verbindung dieser Art.', True)):
        _rr = re.compile(r'einzig|\b(?:zwei|drei|vier|fünf|sechs)mal\b')
        _nr = re.compile(r'\bein(?:e|en|em|er|es)? einzig\w*|\bein- oder zweimal\b')
        check(bool(_rr.search(_nr.sub('', _satz))) == _soll, 'B15-Muster: %s' % _satz)
    print('beziehung.py Selbsttest: %d Proben bestanden%s' % (
        len(ok), (' · übersprungen: ' + '; '.join(aus)) if aus else ''))
    return True


# ---------------------------------------------------------------------------
# Schnittstellen-Auskunft — wortgleich in jedem Builder. Er liest Signaturen und
# Docstrings zur LAUFZEIT — er kann also nicht veralten. Was hilfe() nicht sagt,
# fehlt im Docstring der Funktion und wird DORT ergaenzt, nie hier.
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
    if _hilfe_cli():          # python3 beziehung.py --hilfe [<name>]
        raise SystemExit(0)
    _selbsttest()             # python3 beziehung.py [--selbsttest]
