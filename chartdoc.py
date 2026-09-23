#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chartdoc.py — die chart-UNABHAENGIGE Haelfte des Schritt-3-Builders.

Alles, was bei jedem Horoskop gleich ist, liegt hier als Code, statt in jeder
Design-Konversation neu geschrieben zu werden: Struktur-CSS (Seitenrahmen,
Inhaltsverzeichnis, Aspekt-Legende, Aspekttabelle, Kapitelkopf und
Kapitelfuss mit Signatur und Beleg, Anhangstabellen), der Aufbau von
Inhaltsverzeichnis, Radseite,
Konstellationsseite und Aspektseite, der satz-sichere Kapitelbau und der
Zwei-Pass-Lauf, der die Seitenzahlen fuers Inhaltsverzeichnis aus dem
gerenderten Dokument holt statt sie zu schaetzen.

HAUSSTIL — gemeinsam festgelegt am 2026-07-27, Vorlage waren Seite 2-4 eines
Kombi-Horoskops und Seite 2 eines Ultimativ-Horoskops.
Die Werte in HAUSSTIL unten sind ENTSCHIEDEN, nicht gewachsen; wer sie aendert,
aendert den Hausstil aller kuenftigen Horoskope. Kurzfassung der Beschluesse:
  * Chartbild-Strecke in fester Reihenfolge: Inhalt -> Radseite ->
    Konstellationen -> Aspekte -> (typ-eigene Sonderseiten, z. B. Transit-Uhr).
  * Radseite: Rad so gross wie die Seite es traegt (RAD_BREITE), darunter zwei
    Legendenkaesten nebeneinander — links „Die Linien im Rad", rechts
    „Die Aspekte und was sie bedeuten".
  * Aspektnamen stehen ueberall in ihrer Aspektfarbe (rot/blau/gruen/neutral),
    in beiden Legenden und in der Aspekttabelle.
  * Konstellationsseite: Faktorentabelle, darunter Achsenkreuze und
    Modus-Verteilung nebeneinander, darunter die Element-Verteilung ueber die
    volle Breite. Unter jedem Balken stehen die beteiligten Planeten.
  * Grenzlagen erscheinen in der Haus-Spalte NUR als Doppelzahl („11/12"),
    ohne das Wort „Grenzlage" und ohne Gradangabe.
  * Die Aspektseite passt IMMER auf eine Seite — Tabelle und Legende zusammen
    (aspekt_page skaliert dafuer notfalls die Schriftgroesse, s. `skala`).
  * Signatur und Beleg rendern seit dem 2026-09-05 am KAPITELENDE, fuer jeden
    Dokumenttyp: `build_head()` traegt nur noch Kicker, Titel und Regel,
    `build_fuss()` baut den Streifen hinter den letzten Absatz. Die
    Kapitel-Schleife des Chart-Builders MUSS ihn aufrufen — `render_mit_inhalt`
    bricht sonst hart ab (s. `pruefe_kapitelfuss`). Im analyse.md aendert sich
    nichts.

Chart-spezifisch bleibt im jeweiligen `<klient>_builder.py`: Palette, Cover
(Motiv + Leitsatz), die Chartdaten selbst und die typ-eigenen Sonderseiten —
im Ultimativ-Modus die Transit-Uhr und der Anhang.

Ablauf im Chart-Builder:
    import sys; sys.path.insert(0, '/home/claude')
    import build, chartdoc
    chartdoc.konfiguriere(pal=PAL, part_kicker=PART_KICKER, glyphen=GLYPH_OF,
                          gr=cd.gr, name_of=cd.name_of, kopfzeile='VORNAME',
                          aspektfarben=RAD_PALETTE)
    DESIGN_CSS = chartdoc.struktur_css() + COVER_CSS
    ...
    doc, seiten = chartdoc.render_mit_inhalt(
        build_html, OUT, items, colon_pairs, SEITEN,
        required_fields={'Leitsatz': ..., 'Titelmotiv': ...},
        doctype='ultimativ')
"""
import html
import os
import re
import sys

sys.path.insert(0, '/home/claude')
import build                                        # noqa: E402

# --- Hausstil: die gemeinsam festgelegten Masse ------------------------------

HAUSSTIL = {
    'seitenrand':      '2.15cm 1.9cm 1.95cm 1.9cm',
    'grundschrift':    '10.7pt',
    'zeilenabstand':   '1.5',
    'kapitel_vorab':   '2.3cm',   # 08.09.2026 zurueckgedreht (war 1.7cm)
    'rad_breite':      '14.6cm',  # Radseite nutzt die Seitenhoehe wirklich aus
    'uhr_breite':      '17.2cm',
    'titelgrad':       '17pt',
    'kapiteltitel':    '15.6pt',
}
RAD_BREITE = HAUSSTIL['rad_breite']
UHR_BREITE = HAUSSTIL['uhr_breite']

# --- Konfiguration (setzt der Chart-Builder) --------------------------------

PAL = {
    'night': '#0a1a26', 'petrol': '#1d4a53', 'petrol_l': '#3d6b72',
    'deep': '#123540', 'gold': '#a37c37', 'gold_l': '#c9a45e',
    'stone': '#7a6a52', 'paper': '#f8f4ec', 'ink': '#241f1a',
    'beleg_bg': '#f1ebda', 'beleg_bd': '#cbb07a',
}

# Aspektfarben — MUESSEN mit der Radpalette (radix.DEFAULT_PALETTE bzw.
# RAD_PALETTE des Charts) uebereinstimmen, sonst zeigt die Legende eine andere
# Farbe als das Rad. konfiguriere(aspektfarben=RAD_PALETTE) zieht sie nach.
ASPEKTFARBE = {'rot': '#b0392b', 'blau': '#2f5f97', 'gruen': '#1f7a3c',
               'konj': '#3f382c'}

# Balkenfarben fuer Element- und Modus-Verteilung. Satter als die erste
# Fassung — die blassen Toene verschwanden im Druck fast im Papier.
BALKEN = {
    # Luft klar gelb statt beige (2026-07-27); Erde bleibt gruen.
    'Feuer': '#c1553d', 'Erde': '#5e8f52', 'Luft': '#d3ac25',
    'Wasser': '#3a7599',
    # Modus: fix traegt das Braun, veraenderlich das Blau — veraenderlich
    # liegt inhaltlich am Wasser, darum die Wasserfarbe (so entschieden).
    'kardinal': '#c1553d', 'fix': '#8c7833', 'veränderlich': '#3a7599',
}
BALKEN_BETT = '#ece3cf'

PART_KICKER = set()
GLYPH_OF = {}
KOPFZEILE = ''
# Ornament unter den Teiler-Titeln. Chart-eigen (die tragenden Glyphen aus dem
# @@DECKBLATT-Block); der Vorgabewert ist nur ein Rueckfall, damit aeltere
# Builder ohne konfiguriere(part_ornament=…) unveraendert rendern.
PART_ORNAMENT = '♇ ☉ ☊'

# Bis zu so vielen Verzeichniszeilen wird das Inhaltsverzeichnis einspaltig und
# groesser gesetzt (.toc.weit). Gemessen am 2026-09-08: einspaltig passen 28
# Zeilen auf eine Seite, 30 nicht mehr; 26 ist der Wert mit Reserve fuer
# umbrechende Kapiteltitel. Darueber greift der Zweispalter wie bisher.
TOC_WEIT_MAX = 26

# Aspektname -> Farbschluessel (dieselbe Zuordnung wie radix._ASPECT_DEFS)
ASPEKT_KLASSE = {'Konjunktion': 'konj', 'Opposition': 'rot', 'Quadrat': 'rot',
                 'Trigon': 'blau', 'Sextil': 'blau', 'Quincunx': 'gruen',
                 'Halbsextil': 'gruen'}
ASPEKT_GLYPH = {'Konjunktion': '☌', 'Opposition': '☍', 'Quadrat': '□',
                'Trigon': '△', 'Sextil': '⚹', 'Quincunx': '⚻',
                'Halbsextil': '⚺'}
# 2026-09-22 (W57-Nachzug): die englischen Aspektnamen als zusaetzliche
# Schluessel — die Aspekt-Legende zieht ihren Namen aus LEGEND_ROWS, und mit der
# englischen Tafel fiel die Farbzuordnung sonst mit KeyError aus. Es sind
# dieselben Woerter, die das Klartext-Modul als Anker der englischen Fassung
# festlegt (square, trine, opposition, conjunction, sextile, quincunx,
# semisextile) — hier in der Schreibweise der gedruckten Legende.
ASPEKT_KLASSE.update({'Conjunction': 'konj', 'Square': 'rot', 'Trine': 'blau',
                      'Sextile': 'blau', 'Semisextile': 'gruen'})
ASPEKT_GLYPH.update({'Conjunction': '☌', 'Square': '□', 'Trine': '△',
                     'Sextile': '⚹', 'Semisextile': '⚺'})

# Farbe der gerechneten Punkte im Rad. Steht seit dem 2026-09-14 als Konstante
# statt zweimal als verdrahteter Hexwert (einmal im CSS, einmal in
# linien_legende()).
#
# QUELLE IST `radix.MARKE_FARBE`, nicht dieser Wert (geaendert 2026-09-14,
# Pruefbericht Geburtshoroskop Schritt 3+4, Rubrik 5.8): Der Hexwert stand
# wortgleich in beiden Dateien, mit der Bitte, ihn von Hand nachzuziehen —
# genau die Zweifach-Pflege, die der Drift-Schutz sonst ueberall abschafft
# (vgl. ASPEKT_TITEL, das sich beim Import selbst bei build anmeldet).
# chartdoc importiert radix weiterhin NICHT hart: radix zieht matplotlib,
# numpy und swisseph nach, und chartdoc soll ohne sie importierbar bleiben.
# Der Abgleich laeuft deshalb weich — ist radix erreichbar (im Chart-Lauf
# immer), gilt sein Wert; sonst bleibt die Spiegelung unten stehen.
MARKE_FARBE = '#7d6f93'
try:
    import radix as _radix                                        # noqa: E402
    if getattr(_radix, 'MARKE_FARBE', None):
        MARKE_FARBE = _radix.MARKE_FARBE
except Exception:                       # radix nicht geladen -> Spiegelwert
    pass


class _Farben:
    """Palette ohne Anfuehrungszeichen im Zugriff: `C.gold` statt PAL['gold'].
    Noetig, weil Python 3.11 in f-String-Ausdruecken keine gleichartigen
    Anfuehrungszeichen erlaubt."""

    def __getattr__(self, k):
        try:
            return PAL[k]
        except KeyError as e:
            raise AttributeError(f'Palette kennt {k!r} nicht') from e


C = _Farben()


def gr(x):
    """Gradangabe im Zeichen als N°NN′ — die per konfiguriere(gr=cd.gr) gesetzte
    Funktion der chart-eigenen chartdata.py."""
    return _CFG['gr'](x)


def name_of(n):
    """Ausgeschriebener Faktorname fuer Tabellen — die per konfiguriere(name_of=
    cd.name_of) gesetzte Funktion der chart-eigenen chartdata.py."""
    return _CFG['name_of'](n)


def _orb_text(x):
    """Orb -> 'N°NN′' mit build.orb_text() (2026-09-19, W2) — die eine
    Rundung fuer Aspektseite und Aspekttabelle des Datenblatts."""
    f = getattr(build, 'orb_text', None)
    if f is None:
        raise RuntimeError(
            'chartdoc: build.py ist aelter als chartdoc.py (build.orb_text '
            'fehlt, Stand vor 2026-09-19). Beide aus demselben Stand laden '
            '(lade_schritt), sonst rundet die Aspektseite anders als die '
            'Aspekttabelle.')
    return f(x)


# 2026-09-19 (W2): Vorgabe fuer gr ist die Minutenformatierung (_orb_text)
# statt str — radix liefert den Orb seither ungerundet, und str() schrieb ihn
# als lange Dezimalzahl.
_CFG = {'gr': _orb_text, 'name_of': lambda n: n}


def konfiguriere(pal=None, part_kicker=None, glyphen=None, gr=None,
                 name_of=None, kopfzeile=None, aspektfarben=None,
                 balken=None, part_ornament=None, beleg_platz=None,
                 sprache=None):
    """Einmal je Chart aufrufen, vor dem ersten Seitenaufbau.

    pal           Palette (Schluessel s. PAL oben)
    part_kicker   Kicker der Teiler-Kapitel, z. B. {'Teil I', 'Teil II', ...}
    glyphen       Faktorname -> Glyphe (fuer Aspekttabelle und Konstellationen)
    gr            Funktion Gradbetrag -> 'N°NN′'. Die Orbspalte der
                  Aspektseite benutzt sie seit 2026-09-19 NICHT mehr: dort
                  rundet build.orb_text() — dieselbe Rundung wie die
                  Aspekttabelle des Datenblatts (W2)
    name_of       Funktion interner Faktorname -> Anzeigename
    kopfzeile     Text der linken Kolumnentitel-Zeile (meist der Vorname)
    aspektfarben  dict mit 'rot'/'blau'/'gruen' (und optional 'konj') — die
                  Radpalette des Charts, damit Legende und Rad dieselbe Farbe
                  zeigen
    balken        optionale Ueberschreibung einzelner Balkenfarben
    part_ornament Glyphenzeile unter den Teiler-Titeln — die tragenden
                  Glyphen des Charts aus dem @@DECKBLATT-Block
    beleg_platz   'fuss' (Standard) oder 'kopf'. 'kopf' NUR fuer Laeufe ohne
                  die therapeutische Wirkform — s. BELEG_PLATZ.
    sprache       'de' (Standard) oder 'en' — Sprache ALLER sichtbaren Labels
                  (Seitentitel, Kolumnen, Aspekt-Legende, Orbis-Zeile,
                  Zeitleisten-Texte). Zieht build.PFLICHT_BAUSTEINE mit nach,
                  s. setze_sprache(). Die Kopfzeilen `**Signatur:**` und
                  `**Beleg:**` der Analyse bleiben in JEDER Sprache deutsch
                  (Werkzeuge-Modul A3).
    """
    if sprache is not None:
        setze_sprache(sprache)
    global PART_KICKER, GLYPH_OF, KOPFZEILE, PART_ORNAMENT, BELEG_PLATZ
    if part_ornament is not None:
        PART_ORNAMENT = part_ornament
    if beleg_platz is not None:
        if beleg_platz not in ('fuss', 'kopf'):
            raise ValueError("beleg_platz muss 'fuss' oder 'kopf' sein, "
                             f'nicht {beleg_platz!r}')
        BELEG_PLATZ = beleg_platz
    if pal:
        PAL.update(pal)
    if part_kicker is not None:
        PART_KICKER = set(part_kicker)
    if glyphen is not None:
        GLYPH_OF = dict(glyphen)
    if gr is not None:
        _CFG['gr'] = gr
    if name_of is not None:
        _CFG['name_of'] = name_of
    if kopfzeile is not None:
        KOPFZEILE = kopfzeile
    if aspektfarben:
        for k in ('rot', 'blau', 'gruen', 'konj'):
            if k in aspektfarben:
                ASPEKTFARBE[k] = aspektfarben[k]
    if balken:
        BALKEN.update(balken)


def struktur_css():
    """Chart-unabhaengiges CSS. Das Cover-CSS des Charts kommt dahinter."""
    NIGHT = PAL['night']; PETROL = PAL['petrol']; PETROL_L = PAL['petrol_l']
    DEEP = PAL['deep']; GOLD = PAL['gold']; GOLD_L = PAL['gold_l']
    STONE = PAL['stone']; PAPER = PAL['paper']; INK = PAL['ink']
    BELEG_BG = PAL['beleg_bg']; BELEG_BD = PAL['beleg_bd']
    KOPF = KOPFZEILE
    A_ROT = ASPEKTFARBE['rot']; A_BLAU = ASPEKTFARBE['blau']
    A_GRUEN = ASPEKTFARBE['gruen']; A_KONJ = ASPEKTFARBE['konj']
    balken_css = '\n'.join(
        f'.fill.b-{_slug(k)} {{ background:{v}; }}' for k, v in BALKEN.items())
    return f"""
@page {{
  size: A4;
  margin: {HAUSSTIL['seitenrand']};
  background: {PAPER};
  @top-left  {{ content: "{KOPF}"; font-family:"EB Garamond";
               font-size:7.2pt; letter-spacing:0.22em; color:{GOLD}; }}
  /* `start` statt `last`: Der Kolumnentitel nennt das Kapitel, in dem die
     Seite BEGINNT. Ohne Schluesselwort liefert WeasyPrint den LETZTEN Wert
     der Seite — eine Seite, die zu zwei Dritteln das vorige Kapitel traegt,
     war mit dem naechsten ueberschrieben (Pruefbericht EA 2026-09-08, 4.8).
     Seit dem Smart-Break ist das der Normalfall, nicht die Ausnahme.
     `first` behebt es NICHT: es liefert die erste ZUWEISUNG auf der Seite,
     also ebenfalls das neue Kapitel — an einem Testdokument mit WeasyPrint
     69.0 am 2026-09-08 gemessen. `start` liefert den Stand am Seitenanfang
     und faellt nur dann auf eine Zuweisung zurueck, wenn diese vor allem
     Inhalt steht (Kapitel mit hartem Umbruch) — beide Faelle geprueft. */
  @top-right {{ content: string(chapkick, start); font-family:"EB Garamond";
               font-size:7.2pt; letter-spacing:0.16em; color:{PETROL_L}; }}
  @bottom-center {{ content: counter(page); font-family:"EB Garamond";
               font-size:9pt; color:{GOLD}; }}
}}
@page cover {{
  margin: 0;
  background: {NIGHT};
  @top-left {{ content: none; }}
  @top-right {{ content: none; }}
  @bottom-center {{ content: none; }}
}}
/* Ausgleich fuer den UA-Rand von <body>. WeasyPrints Standard-Stylesheet gibt
   <body> 8px Rand; struktur_css() setzt ihn NICHT zurueck, weil die
   Hausstil-Seitenraender (2,15/1,9/1,95/1,9 cm) mit ihm eingemessen sind —
   ein `body {{ margin:0 }}` verschoebe den Satzspiegel jeder Seite des Bandes.
   `@page cover {{ margin:0 }}` nimmt nur den SEITENrand weg. Ohne die Zeile
   unten beginnt die Coverseite deshalb bei (8,8) statt bei (0,0), ihre Hoehe
   ist auf 29,7cm-16px gestutzt, rundum steht ein 0,21 cm breiter Streifen in
   der @page-cover-Hintergrundfarbe, und die unteren 0,21 cm des Motivs fallen
   weg. Unsichtbar, solange die Coverraender dunkel sind und die Seitenfarbe
   dazu passt — sichtbar, sobald das Motiv bis an die Kante hell ist; im
   Pruefdokument war das genau der Lichtstreifen, die einzige Lichtquelle.
   Kein Preflight und kein verify() sieht das; gefunden hat es allein der vom
   Design-Modul vorgeschriebene Rasterblick aufs Cover (Pruefbericht
   Geburtshoroskop Schritt 3+4, 2026-09-16, Befund 1.1). Die Regel steht hier
   statt im Modultext, damit sie niemand lesen und niemand uebersehen muss;
   ein chart-eigenes COVER_CSS kann sie ueberschreiben, weil es nach
   struktur_css() geladen wird. */
section.cover {{ margin: -8px 0 0 -8px; }}
@page front {{
  @top-right {{ content: "DAS CHARTBILD"; font-family:"EB Garamond";
               font-size:7.2pt; letter-spacing:0.16em; color:{PETROL_L}; }}
}}
@page inhalt {{
  @top-right {{ content: "INHALT"; font-family:"EB Garamond";
               font-size:7.2pt; letter-spacing:0.16em; color:{PETROL_L}; }}
}}
@page anhang {{
  @top-right {{ content: "ANHANG"; font-family:"EB Garamond";
               font-size:7.2pt; letter-spacing:0.16em; color:{PETROL_L}; }}
}}
@page zeit {{
  @top-right {{ content: "ZEITLEISTE"; font-family:"EB Garamond";
               font-size:7.2pt; letter-spacing:0.16em; color:{PETROL_L}; }}
}}

body {{ font-family:"EB Garamond"; color:{INK};
        font-size:{HAUSSTIL['grundschrift']};
        line-height:{HAUSSTIL['zeilenabstand']}; }}
/* ---------- Frontmatter ---------- */
section.front {{ page: front; break-before: page; }}
.fm-kicker {{ text-transform:uppercase; letter-spacing:0.26em; font-size:8.2pt;
   color:{GOLD}; margin-bottom:0.3cm; }}
/* Hausstil 2026-07-27: Der Strich unter dem Seitentitel ist genau so breit
   wie der Titel selbst — weder der alte 2,1-cm-Stummel noch die volle
   Satzbreite. Umgesetzt als Unterkante des Titels (display:inline-block
   schrumpft auf die Textbreite), nicht als eigenes Element: so passt sich der
   Strich jedem Titel automatisch an, ohne dass irgendwo eine Breite gepflegt
   werden muss. `.fm-rule` bleibt als leeres Element im Markup stehen und wird
   ausgeblendet — damit wirkt die Aenderung auch auf die Anhangseiten des
   Chart-Builders, ohne dass dort etwas angefasst wird. Die Kapitelregel
   (.rule) bleibt kurz: dort trennt sie Kopf und Text, hier schliesst sie den
   Seitenkopf ab. */
.fm-title {{ font-family:"Cinzel"; font-weight:400; color:{DEEP};
   font-size:{HAUSSTIL['titelgrad']};
   line-height:1.15; display:inline-block;
   border-bottom:1.1pt solid {GOLD};
   padding-bottom:0.28cm; margin:0 0 0.46cm 0; }}
.fm-rule {{ display:none; }}
.fm-lead {{ font-family:"EB Garamond Italic"; font-style:italic; font-size:10.2pt;
   color:{PETROL_L}; margin:0 0 0.32cm 0; text-align:justify; hyphens:auto; }}
.fm-lead:last-of-type {{ margin-bottom:0.44cm; }}
/* Mehrabsaetziger Vorspann (Transit-Uhr): etwas kleiner und enger gesetzt.
   Bei voller Vorspanngroesse blieb fuer die Grafik nur noch 14,4 cm Breite —
   die Zeilenbeschriftung war dann nicht mehr lesbar. */
.fm-lead.kompakt {{ font-size:9.4pt; line-height:1.38; margin-bottom:0.24cm; }}
.radwrap {{ text-align:center; margin:0.05cm 0 0.16cm 0; }}
.radwrap img {{ width:{RAD_BREITE}; }}
.uhrwrap {{ text-align:center; margin:0.1cm 0 0.2cm 0; }}
.uhrwrap img {{ width:{UHR_BREITE}; }}
.radnote {{ text-align:center; font-family:"EB Garamond Italic";
   font-style:italic; font-size:8.2pt; line-height:1.3; color:{STONE};
   margin:0 0 0.32cm 0; letter-spacing:0.02em; }}

/* ---------- Aspektfarben (Legenden UND Tabelle) ---------- */
.a-rot   {{ color:{A_ROT}; }}
.a-blau  {{ color:{A_BLAU}; }}
.a-gruen {{ color:{A_GRUEN}; }}
.a-konj  {{ color:{A_KONJ}; }}
.a-sym {{ font-family:"DejaVu Sans","FreeSerif",sans-serif; }}

/* ---------- Legendenkaesten ---------- */
/* break-inside:avoid ist Pflicht — ohne sie rutschten die letzten Eintraege
   auf eine sonst leere Folgeseite. */
.lbox {{ border:0.6pt solid #ddd2ba; border-left:2.4pt solid {BELEG_BD};
   background:#f4eede; padding:0.28cm 0.38cm 0.24cm 0.38cm;
   break-inside:avoid; color:#544a38; font-size:7.9pt; line-height:1.30; }}
.lbox h5 {{ font-family:"Cinzel"; font-weight:400; font-size:9.8pt;
   color:{DEEP}; margin:0 0 0.22cm 0; letter-spacing:0.02em; }}
.lbox p {{ margin:0 0 0.13cm 0; text-align:left; hyphens:none;
   line-height:1.30; }}
.lbox p:last-child {{ margin-bottom:0; }}
.lbox b {{ font-family:"EB Garamond Bold"; font-weight:400; }}
.lbox .lgn {{ font-family:"EB Garamond Italic"; font-style:italic;
   color:{STONE}; }}
.lbox.zwei {{ column-count:2; column-gap:0.7cm; }}
.lbox.zwei h5 {{ column-span:all; }}

.legs {{ display:table; width:100%; table-layout:fixed; }}
.legs > .row {{ display:table-row; }}
/* box-sizing (2026-09-23, Pruefbericht Transit 3+4 vom 23.09., 1.5): Ohne es
   schiebt das padding-right der linken Zelle die rechte um genau diesen Betrag
   ueber die Satzkante (gemessen 19,32 cm bei 19,1 cm). */
.legs .cell {{ display:table-cell; width:50%; vertical-align:top;
   box-sizing:border-box; }}
.legs .cell.links {{ padding-right:0.46cm; }}

/* Farb-/Strichmuster in „Die Linien im Rad" */
.swatch {{ display:inline-block; width:0.85cm; height:0.24cm;
   vertical-align:-0.02cm; margin-right:0.2cm; }}
.stroke {{ display:inline-block; width:0.85cm; margin-right:0.2cm;
   vertical-align:0.1cm; }}
.stroke.voll {{ border-top:1.5pt solid #8a8272; }}
.stroke.gestr {{ border-top:1.5pt dashed #8a8272; }}
/* Positionsmarke: kurzer kraeftiger Strich plus feine Fortsetzung — steht
   senkrecht zur Leserichtung, wie im Rad senkrecht zum Zeichenring. */
.stroke.marke {{ border-top:none; height:0.30cm; width:0.85cm;
   vertical-align:-0.06cm; position:relative; }}
.stroke.marke::before {{ content:""; position:absolute; left:0.30cm; top:0;
   width:1.6pt; height:0.17cm; background:{C.ink}; }}
.stroke.marke::after {{ content:""; position:absolute; left:0.335cm;
   top:0.17cm; width:0.5pt; height:0.13cm; background:{C.ink}; opacity:0.40; }}
/* Gerechneter Punkt: OFFENER Kreis — dieselbe Form, die radix.radix(marken=…)
   ins Rad zeichnet. Bis zum 2026-09-14 lief diese Zeile ueber `.stroke.marke`
   mit ueberschriebener Hintergrundfarbe und zeigte damit einen violetten
   BALKEN, waehrend im Rad ein Kreis stand — jede andere Zeile des Kastens
   zeigt das Zeichen, das sie erklaert (Pruefbericht EA Schritt 3+4, 5.5;
   dieselbe Regel, die 2026-09-08 die Zusatz-Aspektglyphen erzwungen hat). */
.stroke.kreis {{ border-top:none; width:0.85cm; height:0.30cm;
   vertical-align:-0.06cm; position:relative; }}
.stroke.kreis::before {{ content:""; position:absolute; left:0.265cm;
   top:0.035cm; width:0.20cm; height:0.20cm; border-radius:50%;
   border:1.1pt solid {MARKE_FARBE}; background:transparent;
   box-sizing:border-box; }}

/* ---------- Element- / Modus-Verteilung ---------- */
.dist {{ display:table; width:100%; table-layout:fixed; margin:0 0 0.46cm 0; }}
.dist > .row {{ display:table-row; }}
.dist .cell {{ display:table-cell; width:50%; vertical-align:top;
   box-sizing:border-box; }}   /* wie .legs .cell, s. dort */
.dist .cell.links {{ padding-right:0.6cm; }}
h4.blockkopf {{ font-family:"EB Garamond"; font-weight:400;
   text-transform:uppercase; letter-spacing:0.18em; font-size:7.4pt;
   line-height:1.2; color:{GOLD}; margin:0 0 0.22cm 0; }}
.vrow {{ margin:0 0 0.19cm 0; }}
.vlab {{ font-family:"EB Garamond Bold"; font-weight:400; font-size:9pt;
   line-height:1.2; color:{DEEP}; margin:0 0 0.05cm 0; }}
.track {{ background:{BALKEN_BETT}; height:0.34cm; line-height:0.34cm;
   text-align:right; overflow:hidden; }}
.fill {{ float:left; height:0.34cm; }}
{balken_css}
.vnum {{ font-size:8pt; color:#6b6250; padding-right:0.14cm; }}
.vpl {{ font-family:"EB Garamond Italic"; font-style:italic; font-size:7.6pt;
   color:{STONE}; margin:0.06cm 0 0 0; line-height:1.2; }}

/* ---------- Konstellationstabelle ---------- */
table.konst {{ width:100%; border-collapse:collapse; font-size:9.3pt;
   line-height:1.22; }}
table.konst th {{ font-family:"EB Garamond"; font-weight:400;
   text-transform:uppercase; letter-spacing:0.14em; font-size:7pt; color:{GOLD};
   text-align:left; padding:0 0.2cm 0.14cm 0; border-bottom:0.8pt solid #ddd2ba; }}
table.konst td {{ padding:0.078cm 0.2cm 0.078cm 0;
   border-bottom:0.4pt solid #e7dfcc; color:{INK}; }}
table.konst td.g {{ width:0.8cm; font-family:"DejaVu Sans","FreeSerif",sans-serif;
   font-size:10pt; color:{DEEP}; }}
table.konst td.nm {{ width:3.4cm; font-family:"EB Garamond Bold";
   font-weight:400; }}
table.konst td.zn {{ width:3.4cm; }}
table.konst td.gd {{ width:2.4cm; color:#4c4335; }}
table.konst td.hs {{ width:2.4cm; color:{DEEP}; }}
table.konst td.lf {{ color:{STONE}; font-size:8.6pt; }}
tr.sep td {{ border-bottom:0.8pt solid #ddd2ba; }}
.tabnote {{ font-size:7.6pt; color:{STONE}; margin:0.22cm 0 0.46cm 0;
   line-height:1.28; }}

/* Achsenkreuz-Tabelle */
table.achsen {{ width:100%; border-collapse:collapse; font-size:9.2pt;
   line-height:1.22; }}
table.achsen th {{ font-family:"EB Garamond"; font-weight:400;
   text-transform:uppercase; letter-spacing:0.14em; font-size:7pt; color:{GOLD};
   text-align:left; padding:0 0.2cm 0.12cm 0; border-bottom:0.8pt solid #ddd2ba; }}
table.achsen td {{ padding:0.085cm 0.2cm 0.085cm 0;
   border-bottom:0.4pt solid #e7dfcc; }}
table.achsen td.ak {{ width:1.1cm; font-family:"EB Garamond Bold";
   font-weight:400; color:{DEEP}; }}
table.achsen td.an_ {{ width:2.9cm; }}
table.achsen td.az {{ width:2.6cm; }}
table.achsen td.ag {{ color:#4c4335; }}

/* ---------- Aspekttabelle ---------- */
.asp {{ column-count:2; column-gap:0.85cm; font-size:9pt; line-height:1.26; }}
.asp-grp {{ text-transform:uppercase; letter-spacing:0.18em; font-size:0.78em;
   color:{GOLD}; margin:0.20cm 0 0.14cm 0; break-after:avoid; }}
.asp-grp.first {{ margin-top:0; }}
table.aspt {{ width:100%; border-collapse:collapse; }}
/* Zweizeilige Zeilen (Spiegelklammer, langer Faktorname) wurden am
   Spaltenwechsel der Aspektseite auseinandergerissen: Beschriftung oben in
   der zweiten Spalte, Orb allein als letzte Zeile der ersten. Auf der
   Tabellenzeile greift break-inside — anders als auf dem Multicol-Container
   selbst. */
table.aspt tr, table.aspt td {{ break-inside: avoid; }}
table.aspt td {{ padding:0.075cm 0; border-bottom:0.4pt solid #e7dfcc;
   vertical-align:baseline; }}
td.ax {{ color:{INK}; }}
td.ao {{ text-align:right; white-space:nowrap; color:#4c4335; width:1.75cm;
   font-size:0.96em; }}
.gy {{ font-family:"DejaVu Sans","FreeSerif",sans-serif; color:{DEEP}; }}
.an {{ font-family:"EB Garamond Italic"; font-style:italic; }}
.mir {{ font-size:0.82em; color:{STONE}; }}
.eins {{ color:#a99b80; font-size:0.84em; padding-left:0.1cm; }}

/* ---------- Inhaltsverzeichnis (Pflichtseite bei jedem Chart) ---------- */
section.inhalt {{ page: inhalt; break-before: page; }}
.toc {{ column-count:2; column-gap:0.9cm; font-size:8.3pt; line-height:1.25; }}
/* Kurzes Verzeichnis: einspaltig und groesser gesetzt, damit die Seite nicht
   zu zwei Dritteln leer bleibt (Chris-Entscheidung 2026-09-08, Pruefbericht
   EA 4.11 — Variante D). inhalt_page() setzt die Klasse selbst, sobald das
   Verzeichnis TOC_WEIT_MAX Zeilen nicht ueberschreitet; darueber bleibt der
   Zweispalter, weil einspaltig ab etwa 30 Zeilen auf zwei Seiten laeuft
   (gemessen 2026-09-08). */
.toc.weit {{ column-count:1; font-size:10.2pt; line-height:1.45; }}
.toc.weit .toc-grp {{ font-size:10.4pt; margin:0.72cm 0 0.26cm 0; }}
.toc.weit .toc-grp.first {{ margin-top:0; }}
.toc.weit .toc-grp .gs {{ font-size:10pt; }}
.toc.weit .toc-sub {{ font-size:7.6pt; margin:0.34cm 0 0.14cm 0.4cm; }}
.toc.weit table.toct td {{ padding:0.115cm 0; }}
.toc.weit td.tn {{ width:0.95cm; font-size:9.4pt; }}
.toc.weit td.tp {{ width:1.1cm; font-size:9.6pt; }}
.toc.weit ~ .toc-orn {{ margin-top:1.4cm; }}
.toc-grp {{ font-family:"Cinzel"; font-size:8.5pt; color:{DEEP};
   letter-spacing:0.1em; margin:0.27cm 0 0.13cm 0; break-after:avoid; }}
.toc-grp.first {{ margin-top:0; }}
.toc-grp .gs {{ font-family:"EB Garamond Italic"; font-style:italic;
   font-size:8.2pt; color:{PETROL_L}; letter-spacing:0; }}
.toc-sub {{ text-transform:uppercase; letter-spacing:0.16em; font-size:6.8pt;
   color:{GOLD}; margin:0.18cm 0 0.08cm 0.35cm; break-after:avoid; }}
table.toct {{ width:100%; border-collapse:collapse; }}
/* Zweizeilige Verzeichniseintraege duerfen nicht ueber den Spaltenwechsel
   brechen (Vorfall 2026-07-30): dort standen Kapitelnummer und
   Seitenzahl unten in der linken Spalte, der Titel oben in der rechten.
   Dieselbe Falle wie bei table.aspt — auf der Tabellenzeile greift
   break-inside, auf dem Multicol-Container nicht. */
table.toct tr {{ break-inside:avoid; }}
table.toct td {{ padding:0.028cm 0; vertical-align:baseline; }}
td.tn {{ width:0.72cm; color:{GOLD}; font-size:7.8pt; }}
td.tt {{ color:{INK}; }}
td.tp {{ width:0.85cm; text-align:right; color:{STONE}; font-size:8pt; }}
.toc-orn {{ font-family:"DejaVu Sans","FreeSerif",sans-serif; color:{GOLD_L};
   font-size:11pt; letter-spacing:0.5em; text-align:center;
   margin:0.34cm 0 0 0; break-before:avoid; }}

/* ---------- Anhang-Tabellen ---------- */
section.anhang {{ page: anhang; break-before: page; }}
section.anhang.flow {{ break-before: auto; margin-top: 1.25cm; }}
.anh-kopf {{ break-inside: avoid; break-after: avoid; }}
table.anh {{ width:100%; border-collapse:collapse; font-size:7.4pt;
   line-height:1.26; table-layout:fixed; }}
table.anh th {{ font-family:"EB Garamond"; font-weight:400;
   text-transform:uppercase; letter-spacing:0.12em; font-size:6.6pt;
   color:{GOLD}; text-align:left; padding:0 0.18cm 0.12cm 0;
   border-bottom:0.8pt solid #ddd2ba; }}
table.anh td {{ padding:0.085cm 0.18cm 0.085cm 0;
   border-bottom:0.4pt solid #ebe3d1; color:{INK}; vertical-align:top; }}
table.anh tr {{ break-inside:avoid; }}
table.anh thead {{ display:table-header-group; }}
td.tg {{ width:0.5cm; font-family:"DejaVu Sans","FreeSerif",sans-serif;
   color:{DEEP}; }}
td.ta {{ width:1.7cm; font-family:"EB Garamond Italic"; font-style:italic;
   color:{PETROL}; }}
td.tz {{ width:1.68cm; }}
td.ts {{ width:3.05cm; color:#4c4335; white-space:nowrap; }}
td.tb {{ width:1.5cm; color:#4c4335; white-space:nowrap; }}
td.td_ {{ width:0.8cm; text-align:right; color:{STONE}; }}
td.te {{ color:#4c4335; }}
td.tst {{ width:2.95cm; color:{STONE}; }}
td.tor {{ width:1.15cm; text-align:right; color:#4c4335; }}
td.tri {{ width:2.55cm; color:{STONE}; }}
.mk {{ color:{GOLD}; }}
tr.sec td {{ color:#8d8371; }}
.anh-sub {{ font-family:"Cinzel"; font-size:9.4pt; color:{DEEP};
   margin:0.6cm 0 0.24cm 0; break-after:avoid; }}
.anh-sub.first {{ margin-top:0.1cm; }}
.anh-note {{ font-size:7.4pt; color:{STONE}; margin:0.22cm 0 0 0;
   line-height:1.3; }}

/* ---------- Zeitleisten-Seite (nur Transit und Ultimativ) ---------- */
/* Eine Seite, keine Prosa: je Kalenderquartal eine Zeile. Sie ersetzt seit
   dem 2026-09-03 die acht Quartalskapitel und bewahrt deren einzige echte
   Leistung — die Navigation. Alle Werte sind UEBERNOMMEN, nicht gerechnet:
   Spannen aus `quartale`, Dichte aus `hotspots` (s. zeitleiste_page). */
/* break-AFTER ist so noetig wie break-before: ohne ihn beginnt das folgende
   Kapitel (Schlusswort) noch auf der Zeitleisten-Seite, und diese Seite traegt
   dann den Kolumnentitel „ZEITLEISTE" ueber einem Kapitelanfang — die benannte
   @page-Regel gilt der ganzen Seite (gefunden 2026-09-07, Prueflauf Transit).
   Die Zeitleiste ist per Definition ein eigenes Blatt. */
section.zeit {{ page: zeit; break-before: page; break-after: page; }}
table.zl {{ width:100%; border-collapse:collapse; font-size:8.1pt;
   line-height:1.30; table-layout:fixed; }}
/* Kopfzeile relativ (0.84em statt 6.8pt), damit sie beim Einmessen mit
   zeitleiste_page(skala=…) mitskaliert. */
table.zl th {{ font-family:"EB Garamond"; font-weight:400;
   text-transform:uppercase; letter-spacing:0.12em; font-size:0.84em;
   color:{GOLD}; text-align:left; padding:0 0.2cm 0.14cm 0;
   border-bottom:0.8pt solid #ddd2ba; }}
table.zl td {{ padding:0.16cm 0.2cm 0.16cm 0;
   border-bottom:0.4pt solid #ebe3d1; color:{INK}; vertical-align:top; }}
table.zl tr {{ break-inside:avoid; }}
table.zl thead {{ display:table-header-group; }}
td.zq {{ font-family:"EB Garamond Bold"; font-weight:400; color:{DEEP}; }}
td.zs {{ color:#4c4335; white-space:nowrap; }}
td.zr {{ color:#8d8371; font-family:"EB Garamond Italic"; font-style:italic; }}
td.zz {{ color:#4c4335; font-size:0.94em; }}
.zl-leer {{ color:#a99b80; }}
/* 2026-09-19 (W12): die Marke des Quartals (marke= im @@ZEITLEISTE-Block) —
   hinter den Themen der Dicht-Zelle, durch „ · " abgesetzt und gedaempft
   gesetzt wie die Ruht-Spalte. Vorher baute jeder Lauf dafuer einen eigenen
   Span per HTML-Nachbearbeitung. */
.zl-marke {{ color:#8d8371; font-family:"EB Garamond Italic";
   font-style:italic; }}

/* ---------- Kapitel ---------- */
/* Vorabstand vor Kapiteln: HAUSSTIL['kapitel_vorab'], seit dem 2026-09-08
   wieder 2.3cm.
   Geschichte in zwei Zeilen: Bis zum 2026-09-05 trug der Kapitelkopf auch
   Signatur und Beleg; der unteilbare Block Kopf+erster Absatz wurde damit so
   hoch, dass 2.3cm regelmaessig Restluecken ueber 30% liessen — daher die
   Kuerzung auf 1.7cm. Mit der Beleg-Verlagerung an den Kapitelfuss ist dieser
   Grund entfallen, und der gemessene Fuellgrad des EA-Laufs lag bei 100%: die
   0.6cm haetten nichts gekostet. Chris-Beschluss vom 2026-09-08
   (Pruefbericht EA 4.9), Modul nachgezogen.
   BERICHTIGT 2026-09-14: Hier stand bis dahin weiter „Der Wert BLEIBT
   trotzdem bei 1.7cm … Beschluss noetig" — ein Kommentar, der dem Wert
   darunter widersprach und den bereits gefallenen Beschluss verschwieg
   (Pruefbericht EA Schritt 3+4, 5.4).
   Wer den Wert erneut aendert, braucht wieder einen Beschluss und zieht hier
   UND im Abschnitt „HAUSSTIL" des Design-Moduls nach. */
.chapter {{ margin-top: {HAUSSTIL['kapitel_vorab']}; }}
.chapter.chapter-first {{ break-before: page; }}
.chapter-head {{ margin-bottom:0.34cm; }}
.kicker {{ text-transform:uppercase; letter-spacing:0.26em; font-size:8.2pt;
   color:{GOLD}; margin-bottom:0.3cm; string-set: chapkick content(); }}
.chaptitle {{ font-family:"Cinzel"; font-weight:400; color:{DEEP};
   font-size:{HAUSSTIL['kapiteltitel']}; line-height:1.18; margin:0; }}
.signatur {{ font-family:"EB Garamond Italic"; font-style:italic; color:{PETROL_L};
   font-size:10.2pt; line-height:1.33; margin:0.17cm 0 0 0; }}
.rule {{ width:2.1cm; height:1.3pt; background:{GOLD}; margin:0.38cm 0 0 0; }}
.beleg {{ font-family:"EB Garamond","DejaVu Sans","FreeSerif",sans-serif;
   color:#6f6350; font-size:7.7pt; line-height:1.36; letter-spacing:0.015em;
   margin:0.32cm 0 0 0; padding:0.17cm 0.4cm; background:{BELEG_BG};
   border-left:2.4pt solid {BELEG_BD}; }}
.beleg.two {{ column-count:2; column-gap:0.6cm; }}
.beleg .lbl {{ text-transform:uppercase; letter-spacing:0.14em; font-size:6.8pt;
   color:{GOLD}; }}
.beleg-stand {{ color:#5a4d36; column-span:all; margin-bottom:0.06cm; }}
.beleg-asp {{ padding-left:0.56cm; text-indent:-0.32cm; margin-top:0.04cm;
   break-inside:avoid; }}
.beleg-asp .mk {{ color:{GOLD}; padding-right:0.07cm; }}

/* ---------- Kapitelfuss (Standard seit 2026-09-05) ---------- */
/* Signatur und Beleg rendern am KAPITELENDE, unter der letzten Bewegung —
   nicht mehr im Kopf. Grund s. Innere Arbeit, „Verhaeltnis zum
   Klartext-Modul", Punkt 2: Ein Kopf aus Gradminuten errichtet eine
   Fachhierarchie genau dort, wo Wiedererkennung entstehen muesste. Der
   Kapitelkopf traegt seitdem nur noch Kicker und Titel; der Leser trifft
   zuerst auf „Woran du es merkst".
   Der Fuss ist ein EIGENSTAENDIGER BLOCK hinter dem letzten Absatz — kein
   float, kein seitliches Element: Float plus Seitenumbruch kollidiert mit
   dem satzsicheren Umbruch (build.render_sentence_safe).
   break-inside steht auf dem WRAPPER, nicht auf .beleg — bei .beleg.two ist
   das ein Multicol-Container, und dort ignoriert WeasyPrint break-inside
   (dieselbe Falle wie bei .lbox und table.aspt). */
.kapitel-fuss {{ margin:0.60cm 0 0 0; break-inside:avoid; }}
.kapitel-fuss .beleg {{ margin:0; }}
/* Die Signaturzeile spannt ueber beide Spalten (column-span:all), traegt aber
   BEWUSST KEINE Trennlinie: WeasyPrint 69 zeichnet den border-bottom eines
   column-span:all-Elements ueber die rechte Innenkante des Streifens hinaus —
   im Einspalter sitzt die Linie richtig, im Zweispalter ragt sie rund 3 mm in
   den Seitenrand (gemessen 2026-09-05). Getrennt wird darum ueber Abstand und
   Farbe: kursives Petrol oben, gesperrtes Gold-Label „BELEG:" darunter. */
.fuss-sig {{ font-family:"EB Garamond Italic"; font-style:italic;
   color:{PETROL_L}; font-size:8.8pt; line-height:1.34; column-span:all;
   margin:0 0 0.22cm 0; }}
/* 2026-09-23 (Pruefbericht Transit 3+4 vom 23.09., 1.4): Im Zweispalter gibt
   WeasyPrint einem column-span:all-Element nicht nur die Linie (s. o.), sondern
   auch die Breite INKLUSIVE beider Innenabstaende von .beleg — Signatur- und
   Stand-Zeile liefen bis 19,35 cm bei einer Satzkante von 19,1 cm. Der Ausgleich
   ist die Summe beider Innenabstaende (2 x 0,4 cm) und gilt nur im Zweispalter;
   wer das Padding von .beleg aendert, zieht ihn nach. */
.beleg.two .fuss-sig, .beleg.two .beleg-stand {{ margin-right:0.8cm; }}

p {{ margin:0 0 0.5em 0; text-align:justify; hyphens:auto; }}
p.first {{ margin-top:0.4cm; }}
.dropcap {{ font-family:"Cinzel"; float:left; color:{GOLD}; font-size:2.55em;
   line-height:0.95; padding:0.02em 0.10em 0 0; }}
.subhead {{ text-transform:uppercase; letter-spacing:0.16em; font-size:8.6pt;
   color:{PETROL_L}; margin:0.62cm 0 0.36cm 0; }}
/* Zwischentitel + Folgeabsatz als EINE Einheit. `break-inside: avoid` ist die
   einzige Umbruchsperre, die WeasyPrint tatsaechlich umsetzt — das
   `break-after: avoid` auf `.subhead` in build.BASE_CSS wirkt nicht (gemessen
   2026-09-09, Pruefbericht Geburtshoroskop Schritt 3+4). Gesetzt wird der
   Wrapper von `build_bloecke()`. */
.subwrap {{ break-inside: avoid; }}
ol.lesart {{ margin:0.15cm 0 0 0; padding:0; list-style:none; counter-reset:li; }}
ol.lesart li {{ position:relative; padding-left:0.85cm; margin:0 0 0.4em 0;
   text-align:justify; hyphens:auto; }}
ol.lesart li::before {{ counter-increment:li; content: counter(li) ".";
   position:absolute; left:0.1cm; color:{GOLD}; font-weight:700; }}

/* ---------- Teiler-Seiten ---------- */
.chapter.part {{ break-before:page; break-after:page; margin-top:0; }}
.part-inner {{ padding-top:8.4cm; text-align:center; }}
.part .kicker {{ letter-spacing:0.5em; font-size:9pt; margin-bottom:0.55cm; }}
.part .chaptitle {{ font-size:22pt; line-height:1.25; }}
.part-orn {{ font-family:"DejaVu Sans","FreeSerif",sans-serif; color:{GOLD};
   font-size:16pt; letter-spacing:0.6em; margin:0.7cm 0 0.85cm 0; }}
.part p {{ text-align:center; hyphens:none; font-family:"EB Garamond Italic";
   font-style:italic; font-size:11.2pt; line-height:1.6; color:#4c4335;
   margin:0 2.2cm; }}
.part p.first {{ margin-top:0; }}
"""


def _slug(s):
    return (s.lower().replace('ä', 'ae').replace('ö', 'oe')
            .replace('ü', 'ue').replace('ß', 'ss'))


def esc(s):
    return html.escape(s)


# --- Aspekt-Legende ---------------------------------------------------------

LEGEND_ROWS = [
    ("Konjunktion", "0°", "zwei Kräfte am selben Punkt — sie verschmelzen, "
     "verstärken und färben sich gegenseitig."),
    ("Opposition", "180°", "Gegenüberstellung, oft über andere erlebt — es geht "
     "ums Ausbalancieren statt Entweder-oder."),
    ("Quadrat", "90°", "innere Reibung, die drängt — unbequem, aber der stärkste "
     "Entwicklungsmotor."),
    ("Trigon", "120°", "müheloser Fluss, angeborenes Talent — das gerade deshalb "
     "leicht brachliegt."),
    ("Sextil", "60°", "Anregung und Gelegenheit — leichter zugänglich als das "
     "Trigon, will aktiv ergriffen werden."),
    ("Quincunx", "150°", "zwei Kräfte, die nicht zusammenpassen und sich nicht "
     "ignorieren lassen — ständiges Nachjustieren."),
    ("Halbsextil", "30°", "leiser Reiz zwischen Nachbarkräften — eine "
     "Suchbewegung."),
]

LEGEND_TITEL = 'Die Aspekte und was sie bedeuten'
# 2026-09-22 (W57-Nachzug): Seitentitel, die bis heute an ihrer Fundstelle
# standen und deshalb in einer englischen Fassung deutsch blieben. Sie sind
# jetzt Globals wie die uebrigen Labels und werden von setze_sprache()
# mitgetauscht.
INHALT_TITEL = 'Inhalt'
RADIX_TITEL = 'Die Radix'
RADIX_KICKER = 'Das Chart im Bild'
KONST_TITEL = 'Die Konstellationen'
KONST_KICKER = 'Stände & Verteilung'
# Spaltenkoepfe und Blockueberschriften der Konstellationsseite. Standen bis zum
# 2026-09-22 fest im f-String — die einzige Seite ohne Parameter dafuer, und
# damit die Stelle, an der eine englische Fassung deutsch blieb (Klasse-2
# Transit 3+4 vom 22.09., Nr. 9).
KONST_KOPF = {'faktor': 'Faktor', 'zeichen': 'Zeichen', 'grad': 'Grad',
              'haus': 'Haus', 'lauf': 'Lauf', 'achse': 'Achse',
              'achsenkreuze': 'Die Achsenkreuze',
              'modi': 'Modus-Verteilung (ungewichtet)',
              'elemente': 'Element-Verteilung (zehn klassische Planeten, '
                          'ungewichtet)'}

# Die Orbis-Staffelung als eine Zeile unter der Aspekttabelle. Ohne sie sagt
# das Dokument „Huber-Orbis, individuell gestaffelt nach Faktor", nennt aber
# nirgends die Zahlen — bei einem Band, dessen Kapitel mit Gradminuten
# belegen, ist das die eine Angabe, mit der ein Leser eine Zeile nachpruefen
# koennte (Pruefbericht EA 5d, 2026-09-08). Sie steht NUR unter der
# Aspekttabelle, nicht auf der Radseite: dort haengt die eingemessene
# Radbreite an der Kastenhoehe.
# Steht gedruckt unter jeder Aspektseite. Neu gefasst 2026-09-15 mit der
# Orbis-Umstellung (s. radix.ASPEKT_ORB): Der frueher hier stehende Sammelwert
# „alles Übrige 3°" hat verschwiegen, dass er Chiron, Lilith, Pholus,
# Mondknoten und Glueckspunkt zu einer Gruppe zusammenfasste, die inzwischen
# vier verschiedene Werte traegt. Seit dem 2026-09-23 steht der Glueckspunkt
# nicht mehr darin (ausgemustert, radix.AUSGEMUSTERT). Aendert sich ein Wert
# in radix.ASPEKT_ORB,
# aendert sich diese Zeile mit — sie ist die einzige Stelle, an der der Leser
# erfaehrt, womit gerechnet wurde.
ORBIS_ZEILE = ('Orbis nach Faktor: Sonne, Mond 8° · Merkur, Venus, Jupiter 6° '
               '· Mars, Saturn 5° · Uranus, Neptun, Pluto 4° · Achsen und '
               'Chiron 5° · Lilith 3° · Pholus 2°. Der Mondknoten '
               'übernimmt den Orbis des aspektierenden Faktors. Nebenaspekte '
               'enger, auf beide Faktor-Orbis gedeckelt.')

# Aspektarten AUSSERHALB des Huber-Systems, die ein Chart bewusst in die
# Tabelle haengen kann (Datenblatt-Modul, „Zusatzebene"). Sie stehen nicht im
# Rad und tragen darum keine der vier Radfarben. Erklaert werden sie
# trotzdem — der Klartext-Standard verlangt, dass jedes sichtbare Zeichen im
# Dokument einmal benannt wird (Befund 2026-09-06).
ZUSATZ_LEGENDE = {
    'Halbquadrat': ('45°', 'halbe Reibung — ein Spannungspunkt im Untergrund, '
                    'leiser als ein Quadrat und dauerhafter.'),
    'Anderthalbquadrat': ('135°', 'dieselbe Reibung aus der Gegenrichtung — '
                          'sie meldet sich spaeter und in fremder Gestalt.'),
}
# Symbole der Zusatz-Aspektarten. Ohne sie stand im gerenderten Kasten vor
# „Halbquadrat (45°)" ein nackter Mittelpunkt, wo jede andere Zeile ihr
# Aspektzeichen traegt (Pruefbericht EA 2026-09-08, 4.10). Beide Zeichen sind
# im Font-Stack gedeckt — am 2026-09-08 gegen build._coverage_charset()
# geprueft. Sie stehen in der NEUTRALEN Farbe, nicht in einer der vier
# Radfarben: eine Radfarbe verspraeche eine Linie, die im Rad nicht gezeichnet
# ist. Eine Zusatzart OHNE Eintrag hier bekommt gar keine Symbolspalte — nie
# wieder einen Ersatzpunkt.
ZUSATZ_GLYPH = {'Halbquadrat': '∠', 'Anderthalbquadrat': '⚼'}

# Welche davon in DIESEM Chart vorkommen. Wird von aspekt_page() aus der
# uebergebenen Aspektliste selbst gesetzt, damit Radseite und Aspektseite
# nicht auseinanderlaufen koennen; setze_zusatzaspekte() ist der Weg, sie im
# Chart-Builder VOR dem ersten Seitenaufbau bekannt zu machen.
AKTIVE_ZUSATZ = ()


def setze_zusatzaspekte(aspekte):
    """Die Zusatz-Aspektarten dieses Charts aus seiner Aspektliste ableiten.

    Einmal je Chart aufrufen, VOR dem ersten Seitenaufbau — sonst traegt die
    Legende auf der Radseite (die vor der Aspektseite gebaut wird) im ersten
    Durchlauf noch keine Zusatzzeile. aspekt_page() ruft es zur Sicherheit
    selbst noch einmal auf.
    """
    global AKTIVE_ZUSATZ
    namen = []
    for a in aspekte or ():
        n = a.get('name')
        if n in ZUSATZ_LEGENDE and n not in namen:
            namen.append(n)
    AKTIVE_ZUSATZ = tuple(namen)
    return AKTIVE_ZUSATZ


def aspekt_legende(spalten=1, titel=None, stil='', zusatz=False,
                   orbis=False):
    """Legendenkasten „Die Aspekte und was sie bedeuten".

    Symbol UND Aspektname stehen in der Aspektfarbe (Beschluss 2026-07-27) —
    dieselbe Farbe, die das Rad und die Aspekttabelle verwenden.
    spalten=2 setzt den Kasten zweispaltig (fuer schmale Seitenreste).

    zusatz=True haengt die Erklaerzeilen der Zusatz-Aspektarten an
    (AKTIVE_ZUSATZ). Sie stehen NUR unter der Aspekttabelle, nicht auf der
    Radseite: im Rad kommen diese Aspekte gar nicht vor, dort waere die Zeile
    verwirrend — und sie kostete auf der Radseite rund 1,4 cm Raddurchmesser,
    weil die eingemessene Bildbreite an der Kastenhoehe haengt
    (Befund 2026-09-06). Der Klartext-Standard ist erfuellt, weil jedes
    Zeichen im Dokument einmal benannt wird, nicht zweimal.

    orbis=True haengt ORBIS_ZEILE an (die Orbis-Staffelung nach Faktor). Sie
    steht aus demselben Grund NUR unter der Aspekttabelle: auf der Radseite
    haengt die eingemessene Radbreite an der Kastenhoehe. Gesetzt wird sie
    allein von aspekt_page().
    **Bis zum 2026-09-14 setzte aspekt_page() sie NICHT** — der Parameter und
    die Zeile lagen seit dem 2026-09-08 im Code, der Aufruf uebergab nur
    zusatz=True, und die Zeile stand folglich in keinem gerenderten Dokument
    (Pruefbericht EA Schritt 3+4, 5.2). Derselbe Fehlertyp wie das
    `vorne=`-Versaeumnis: ein fehlendes Element, das kein Preflight findet,
    weil nichts es zaehlt. Dagegen steht seit demselben Tag die Gegenprobe in
    render_mit_inhalt() (s. pruefe_orbis_zeile).
    """
    titel = LEGEND_TITEL if titel is None else titel
    rows = []
    for n, w, t in LEGEND_ROWS:
        k = ASPEKT_KLASSE[n]
        rows.append(
            f'<p><span class="a-sym a-{k}">{ASPEKT_GLYPH[n]}</span> '
            f'<b class="a-{k}">{n}</b> ({w}) — {t}</p>')
    for n in (AKTIVE_ZUSATZ if zusatz else ()):
        w, t = ZUSATZ_LEGENDE[n]
        sym = ZUSATZ_GLYPH.get(n)
        vor = f'<span class="a-sym a-konj">{sym}</span> ' if sym else ''
        rows.append(f'<p>{vor}'
                    f'<b class="a-konj">{esc(n)}</b> ({w}) — {t} '
                    f'Steht nicht im Rad.</p>')
    if orbis:
        rows.append(f'<p class="lgn">{esc(ORBIS_ZEILE)}</p>')
    cls = 'lbox zwei' if spalten == 2 else 'lbox'
    st = f' style="{stil}"' if stil else ''
    return (f'<div class="{cls}"{st}><h5>{esc(titel)}</h5>'
            + ''.join(rows) + '</div>')


# Alter Name aus der Zeit vor dem Hausstil (2026-07-27): der Legendenkasten
# hiess `legend_html()`, bevor er in „Aspekte" und „Linien im Rad" geteilt wurde.
# Bleibt als Alias, damit aeltere Chart-Builder nicht mit AttributeError brechen.
legend_html = aspekt_legende


def linien_legende(gerechnet=None):
    """Legendenkasten „Die Linien im Rad" — erklaert Farbe, Strichart und die
    Positionsmarke.

    Die Zeile zur Positionsmarke gehoert seit dem 2026-07-30 dazu (Hausstil,
    s. radix.radix(gradmarke=...)). Eine Marke, die niemand erklaert, ist fuer
    den Leser ein Raetsel — und der Klartext-Standard verlangt, dass jedes
    sichtbare Zeichen im Dokument einmal benannt wird.
    """
    A = ASPEKTFARBE
    # Gerechnete Punkte (radix.radix(marken=…)) MUESSEN hier benannt werden.
    ger = ''
    if gerechnet:
        # Das Zeichen im Kasten ist dasselbe, das im Rad steht: ein offener
        # Kreis (`.stroke.kreis`), nicht der Balken der Positionsmarke.
        ger = ('<p><span class="stroke kreis"></span>'
               f'offener Kreis — {esc(gerechnet)}: ein GERECHNETER '
               'Punkt, keine Stellung am Himmel; er bildet deshalb keine '
               'Aspektlinien.</p>')
    return f"""<div class="lbox"><h5>Die Linien im Rad</h5>
<p><span class="swatch" style="background:{A['rot']}"></span>rot — Spannung
(Opposition, Quadrat)</p>
<p><span class="swatch" style="background:{A['blau']}"></span>blau —
harmonischer Fluss (Trigon, Sextil)</p>
<p><span class="swatch" style="background:{A['gruen']}"></span>grün —
Wahrnehmung (Quincunx, Halbsextil)</p>
<p><span class="stroke voll"></span>durchgezogen — voller Aspekt (beide Orbis
erfüllt)</p>
<p><span class="stroke gestr"></span>gestrichelt — einseitig (nur der weitere
Orbis trägt)</p>
<p><span class="stroke marke"></span>kräftiger Strich am Zeichenring — der
genaue Grad des Faktors; die feine Linie führt zu seiner Glyphe</p>
{ger}<p class="lgn">Die Konjunktion (gemeinsamer Punkt) wird nicht als Linie
gezeigt. Der äußere Ring ist nach den vier Elementen eingefärbt; die kleinen
grauen Striche darin sind die 5°-Teilung.</p></div>"""


# --- Seite: das Rad ---------------------------------------------------------

def radix_page(bild, unterzeile, kicker=None, titel=None,
               anker='PG_rad', bild_breite=None, gerechnet=None):
    """Radseite im Hausstil: grosses Rad, darunter die beiden Legendenkaesten.

    bild        Dateiname des von radix.py erzeugten PNG. Das PNG traegt seit
                dem Papierhintergrund KEINE eigene Bildunterschrift mehr —
                matplotlib setzt sie in einer Groteske, und ohne den weissen
                Kasten drumherum las sie sich als Seitentext in der falschen
                Schrift. Alles Erklaerende steht jetzt in `unterzeile`.
    unterzeile  kursive Zeile unter dem Rad, in der Dokumentschrift
    bild_breite ueberschreibt HAUSSTIL['rad_breite'] fuer diese Seite
    gerechnet   Name des gerechneten Punktes, sobald das Rad mit
                `radix.radix(marken=…)` einen zeichnet — z. B.
                'der Pluto-Polaritaetspunkt'. Wird an linien_legende()
                durchgereicht und ist dann PFLICHT: ein sichtbares Zeichen
                ohne Erklaerung verstoesst gegen den Klartext-Standard.
                Neu 2026-09-14 (Pruefbericht EA Schritt 3+4, 5.1): Das
                Design-Modul verlangte die Zeile seit dem 2026-09-08, diese
                Funktion hatte aber keinen Weg, sie zu setzen — jeder Lauf mit
                gerechnetem Punkt musste den Kasten von Hand austauschen.
    """
    kicker = RADIX_KICKER if kicker is None else kicker
    titel = RADIX_TITEL if titel is None else titel
    stil = f' style="width:{bild_breite}"' if bild_breite else ''
    return f"""<section class="front" id="{anker}">
<div class="fm-kicker">{esc(kicker)}</div>
<h2 class="fm-title">{esc(titel)}</h2>
<div class="fm-rule"></div>
<div class="radwrap"><img src="{bild}" alt="Radix"{stil}></div>
<div class="radnote">{esc(unterzeile)}</div>
<div class="legs"><div class="row">
<div class="cell links">{linien_legende(gerechnet=gerechnet)}</div>
<div class="cell">{aspekt_legende()}</div></div></div>
</section>"""


# --- Seite: Transit-Uhr -----------------------------------------------------

def uhr_lead(stichtag):
    """Erklaertext ueber der Transit-Uhr.

    Fassung vom 2026-07-27: die erste Version („links der Planet, rechts der
    Punkt deines Geburtsbildes") wurde als Ortsangabe IM DIAGRAMM gelesen statt
    als Lesereihenfolge der Zeilenbeschriftung, und „Punkt" als einer der
    gezeichneten Marker. Jetzt getrennt in: was eine Zeile ist, wie ihre
    Beschriftung zu lesen ist, und was der Balken zeigt.
    """
    return (
        'Jede Zeile ist eine lange Linie: ein Planet, der gerade am Himmel '
        'läuft, berührt über Wochen oder Monate hinweg eine Stelle deines '
        'Geburtsbildes. Die Beschriftung am Zeilenanfang nennt beide in dieser '
        'Reihenfolge — zuerst den laufenden Planeten, dann den Winkel, den er '
        'bildet, dann die Stelle deines Geburtsbildes, die er trifft. Der '
        'Balken rechts daneben zeigt, wann das geschieht: blass die volle '
        'Berührungszeit, kräftig die Strecke, in der die Linie wirklich '
        'arbeitet, und die kleinen weißen Punkte die einzelnen Tage, an '
        'denen der '
        f'Winkel exakt steht. Was links der senkrechten Marke beginnt, lief '
        f'schon vor dem {stichtag}; ein Pfeil am Rand heißt, die Linie reicht '
        'über das Fenster hinaus.')


_JAHRWORT = {2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf', 6: 'sechs'}


def transituhr_page(bild, stichtag, unterzeile, kicker='Das Chart im Bild',
                    titel=None, anker='PG_uhr', lead=None, bild_breite=None,
                    jahre=2):
    """Transit-Uhr-Seite (Ultimativ-, Transit- und Themen-Modus).

    lead          str ODER Liste von Absaetzen. Die Themenfassung der Uhr
                  braucht mehr Erklaerung als die alte Zeilenfassung — darum
                  mehrere Absaetze statt einem langen Block.
    bild_breite   ueberschreibt HAUSSTIL['uhr_breite'] fuer diese Seite. Noetig,
                  weil Vorspannlaenge und Grafikhoehe gegeneinander laufen: je
                  mehr Text ueber der Uhr steht, desto schmaler muss sie sein,
                  um auf der Seite zu bleiben.
    jahre         Laenge des Fensters in Jahren; baut den Seitentitel. Der
                  Vorgabewert 2 entspricht dem Ultimativ-Standard (acht
                  Kalenderquartale). Bis zum 2026-08-01 stand „zwei Jahre" fest
                  im Titel — ein Dreijahresfenster bekam damit stillschweigend
                  eine falsche Ueberschrift. `titel=` setzt den Text weiterhin
                  vollstaendig selbst und schlaegt `jahre`.
    """
    if titel is None:
        if int(jahre) <= 1:
            titel = 'Die Transit-Uhr — das kommende Jahr'
        else:
            wort = _JAHRWORT.get(int(jahre), str(int(jahre)))
            titel = f'Die Transit-Uhr — {wort} Jahre auf einen Blick'
    txt = lead if lead is not None else uhr_lead(stichtag)
    if isinstance(txt, str):
        txt = [txt]
    kl = 'fm-lead kompakt' if len(txt) > 1 else 'fm-lead'
    vorspann = ''.join(f'<p class="{kl}">{esc(t)}</p>' for t in txt)
    stil = f' style="width:{bild_breite}"' if bild_breite else ''
    return f"""<section class="front" id="{anker}">
<div class="fm-kicker">{esc(kicker)}</div>
<h2 class="fm-title">{esc(titel)}</h2>
<div class="fm-rule"></div>
{vorspann}
<div class="uhrwrap"><img src="{bild}" alt="Transit-Uhr"{stil}></div>
<div class="radnote">{esc(unterzeile)}</div>
</section>"""


# --- Seite: Zeitleiste ------------------------------------------------------

# Seitentitel der Zeitleiste. Steht hier als Konstante, weil er zugleich der
# Pflicht-Baustein ist, den build.assert_render_ready sucht — dieselbe
# Konstruktion wie bei ASPEKT_TITEL, damit der Wortlaut nicht an zwei Orten
# gepflegt werden muss (s. _pflicht_baustein_angleichen).
ZEITLEISTE_TITEL = 'Die Zeitleiste'

# 2026-09-19 (W12): der Satz, der die Dichte-Spalte erklaert, einzeln
# greifbar. ZL_LEAD traegt ihn wortgleich; steht statt ZL_LEAD der LEAD aus dem
# @@ZEITLEISTE-Block als Vorspann, erklaert der die Klammerzahl nicht (T34-18c
# Nr. 13, T34-18d Nr. 8) — dann setzt zeitleiste_page() diesen Satz selbst in
# die Fussnote.
ZL_SPALTE = ('Ganz rechts steht, wie viele Berührungen die Rechnung je Monat '
             'gezählt hat; die Zahl in Klammern sind die Tage, an denen ein '
             'Winkel exakt steht.')

ZL_LEAD = (
    'Diese Seite ist zum Nachschlagen, nicht zum Lesen. Jede Zeile ist ein '
    'Quartal des Fensters: daneben steht, welche Themen in diesen drei '
    'Monaten dicht laufen und welche in derselben Zeit ruhen. ' + ZL_SPALTE
    + ' Eine hohe Zahl heißt nicht, dass viel passiert — sie heißt, dass viel '
    'gleichzeitig angerührt ist.')

ZL_NOTE = ('Die Quartale sind Kalenderquartale; Q1 ist das Quartal, in dem '
           'dieses Horoskop entstanden ist. Spannen und Zahlen sind '
           'unverändert aus der Rechnung übernommen.')


def _zl_liste(x, leer='—'):
    """Themenliste einer Zelle: str bleibt str, Liste wird gefuegt."""
    if not x:
        return f'<span class="zl-leer">{leer}</span>'
    if isinstance(x, str):
        return esc(x)
    return esc(' · '.join(str(t) for t in x))


# --- Leser fuer den @@ZEITLEISTE-Block (neu 2026-09-19, W12) ---------------

class ZeitleisteError(ValueError):
    """@@ZEITLEISTE-Block fehlt, ist unvollstaendig oder traegt eine unbekannte
    Zeile bzw. ein unbekanntes Feld (s. lies_zeitleiste)."""


ZL_FELDER = ('LEAD',)                    # Kopffelder des Blocks
ZL_QUARTAL_FELDER = ('dicht', 'marke')   # Felder einer Quartalszeile
ZL_MARKEN_MAX = 3                        # Transit-/Ultimativ-Modul
_ZL_START_RE = re.compile(r'^@@ZEITLEISTE\s*$')
_ZL_ENDE_RE = re.compile(r'^@@ENDE\s*$')
_ZL_FELD_RE = re.compile(r'^([A-ZÄÖÜ][A-ZÄÖÜ_]{1,24})\s*:\s*(.*)$')
_ZL_QUARTAL_RE = re.compile(r'^Q(\d{1,2})\s*\|(.*)$')


def lies_zeitleiste(pfad_oder_text, titel=None):
    """@@ZEITLEISTE-Block aus der chart_data lesen (Transit und Ultimativ).

    Neu 2026-09-19 (W12). Vorher baute jeder Schritt-3-Lauf seinen eigenen
    Parser; in T34-18b nahm einer mit txt.split('@@ZEITLEISTE') die erste
    Fundstelle des WORTES im Kopf der chart_data statt des Blocks und brach ab.
    Gesucht wird deshalb zeilengebunden wie in build.lies_deckblatt():
    Blockanfang ist eine Zeile, die NUR `@@ZEITLEISTE` traegt (die letzte, falls
    es mehrere gibt), Blockende die naechste Zeile `@@ENDE`.

    Blockformat (Transit-Modul, Struktur Punkt 6; Ultimativ-Modul):
        @@ZEITLEISTE
        LEAD: <ein Absatz Vorspann; Folgezeilen direkt darunter gehoeren dazu>
        Q1 | dicht=1,2,3,6 | marke=
        Q2 | dicht=2,4,5 | marke=<Datum · Befund>
        ...
        @@ENDE
    Die Zahlen hinter dicht= sind KAPITELNUMMERN; `dicht=` leer heisst: nichts
    im Wirkorb. marke= ist optional, hoechstens dreimal je Dokument; ihr Text
    wird wortgleich uebernommen.

    pfad_oder_text  Pfad der <klient>_<KUERZEL>_chart_data.md oder ihr Text
    titel           optional {Kapitelnummer: Kapiteltitel}. Dann traegt jedes
                    Quartal zusaetzlich 'dicht_titel' und 'ruht_titel' (die
                    Gegenmenge, in Kapitelreihenfolge) — fertig fuer
                    zeitleiste_page() —, und eine Nummer ohne Kapitel ist ein
                    harter Fehler.

    Rueckgabe: {'lead': str,
                'quartale': [{'quartal': 'Q1', 'dicht': [1, 2, 3, 6],
                              'marke': ''}, ...]}

    Wirft ZeitleisteError, wenn der Block fehlt, kein @@ENDE hat, LEAD fehlt,
    eine Zeile oder ein Feld unbekannt ist, dicht= keine Kapitelnummern traegt,
    ein Quartal doppelt vorkommt oder die Quartale nicht lueckenlos ab Q1 laufen.
    Mehr als drei Marken: nur ein Hinweis (Regel aus Schritt 2, im Bericht
    melden).

    Im Chart-Builder (TITEL = {Nummer: Titel} aus parse_analyse(),
    TD = transitdata.parse()):
        zl = chartdoc.lies_zeitleiste(CHARTDATA, titel=TITEL)
        zeilen = []
        for q, (qq, a, b, spanne) in zip(zl['quartale'], TD['quartale']):
            assert q['quartal'] == qq
            zeilen.append((qq, spanne, q['dicht_titel'], q['ruht_titel'],
                           tdat.dichte_je_monat(TD, a, b), q['marke']))
        seite = chartdoc.zeitleiste_page(zeilen, lead=zl['lead'])
    """
    text, name = pfad_oder_text, 'Text'
    if isinstance(text, os.PathLike):
        text = os.fspath(text)
    if not isinstance(text, str):
        raise ZeitleisteError(
            'lies_zeitleiste() erwartet den Pfad der chart_data.md oder ihren '
            f'Text als String, bekommen: {type(text).__name__}.')
    if '\n' not in text and os.path.isfile(text):
        name = os.path.basename(text)
        with open(text, encoding='utf-8') as fh:
            text = fh.read()
    elif '\n' not in text and '@@ZEITLEISTE' not in text:
        raise ZeitleisteError(
            f'lies_zeitleiste(): Datei nicht gefunden: {text}. Erwartet: Pfad '
            'der <klient>_<KUERZEL>_chart_data.md oder ihr Text.')
    zeilen = text.splitlines()
    start = None
    for i, z in enumerate(zeilen):
        if _ZL_START_RE.match(z):
            start = i + 1
    if start is None:
        raise ZeitleisteError(
            f'@@ZEITLEISTE-Block fehlt in {name}. Er gehoert ans ENDE der '
            'chart_data.md, hinter den @@DECKBLATT-Block (Transit- bzw. '
            'Ultimativ-Modul): eine Zeile "@@ZEITLEISTE", darunter "LEAD: …", '
            'je Quartal "Q<n> | dicht=<Kapitelnummern> | marke=<optional>", zum '
            'Schluss "@@ENDE". Gesucht wird eine Zeile, die NUR "@@ZEITLEISTE" '
            'traegt — das Wort im Fliesstext zaehlt nicht. Die Zuordnung trifft '
            'Schritt 2, Schritt 3 liest sie nur (Transit-Modul, Struktur Punkt '
            '6): fehlt der Block, das melden, statt sie hier neu zu treffen.')
    ende = next((j for j in range(start, len(zeilen))
                 if _ZL_ENDE_RE.match(zeilen[j])), None)
    if ende is None:
        raise ZeitleisteError(
            f'@@ZEITLEISTE-Block in {name} ohne abschliessende Zeile "@@ENDE".')

    lead, quartale, im_lead = None, [], False
    for nr, z in enumerate(zeilen[start:ende], start + 1):
        s = z.strip()
        wo = f'@@ZEITLEISTE in {name}, Zeile {nr}'
        if not s:
            im_lead = False
            continue
        mq = _ZL_QUARTAL_RE.match(s)
        if mq:
            im_lead = False
            label = 'Q%d' % int(mq.group(1))
            if any(q['quartal'] == label for q in quartale):
                raise ZeitleisteError(f'{wo}: {label} steht doppelt im Block.')
            felder = {}
            for teil in mq.group(2).split('|'):
                teil = teil.strip()
                if not teil:
                    continue
                if '=' not in teil:
                    raise ZeitleisteError(
                        f'{wo} ({label}): Teil "{teil}" ohne "=". Erwartet: '
                        'dicht=<Kapitelnummern> und optional marke=<Text>. '
                        'Steht ein senkrechter Strich im Markentext, ihn '
                        'ersetzen — er trennt die Felder.')
                k, v = teil.split('=', 1)
                k = k.strip()
                if k not in ZL_QUARTAL_FELDER:
                    raise ZeitleisteError(
                        f'{wo} ({label}): unbekanntes Feld "{k}=". Erlaubt: '
                        + ', '.join(f + '=' for f in ZL_QUARTAL_FELDER) + '.')
                if k in felder:
                    raise ZeitleisteError(f'{wo} ({label}): "{k}=" doppelt.')
                felder[k] = v.strip()
            if 'dicht' not in felder:
                raise ZeitleisteError(
                    f'{wo} ({label}): kein "dicht=". Ein Quartal ohne '
                    'Wirkorb-Kontakt traegt "dicht=" leer.')
            try:
                dicht = [int(x) for x in re.split(r'[,\s]+', felder['dicht'])
                         if x]
            except ValueError:
                raise ZeitleisteError(
                    f'{wo} ({label}): dicht= traegt keine Kapitelnummern: '
                    f'"{felder["dicht"]}". Erwartet die NUMMERN der '
                    'Themenkapitel, z. B. dicht=1,2,3 — keine Titel.') from None
            quartale.append({'quartal': label, 'dicht': dicht,
                             'marke': felder.get('marke', '')})
            continue
        mf = _ZL_FELD_RE.match(s)
        if mf:
            if mf.group(1) not in ZL_FELDER:
                raise ZeitleisteError(
                    f'{wo}: unbekanntes Feld "{mf.group(1)}:". Erlaubt: '
                    + ', '.join(f + ':' for f in ZL_FELDER)
                    + '; dazu je Quartal eine Zeile '
                    '"Q<n> | dicht=<Kapitelnummern> | marke=<optional>".')
            if lead is not None:
                raise ZeitleisteError(f'{wo}: LEAD steht doppelt im Block.')
            lead, im_lead = mf.group(2).strip(), True
            continue
        if im_lead and not re.match(r'^Q\d', s):
            lead = (lead + ' ' + s).strip()
            continue
        raise ZeitleisteError(
            f'{wo}: unbekannte Zeile "{s[:60]}". Erwartet "LEAD: …" oder '
            '"Q<n> | dicht=<Kapitelnummern> | marke=<optional>".')

    if not lead:
        raise ZeitleisteError(
            f'@@ZEITLEISTE in {name}: LEAD fehlt oder ist leer. Schritt 2 '
            'schreibt ihn (Transit-Modul: ordnet die Dichte-Zahl ein und nennt '
            'den progressiven Mond) — melden; ZL_LEAD traegt den progressiven '
            'Mond nicht.')
    if not quartale:
        raise ZeitleisteError(f'@@ZEITLEISTE in {name}: keine Quartalszeile.')
    ist = [q['quartal'] for q in quartale]
    soll = ['Q%d' % i for i in range(1, len(quartale) + 1)]
    if ist != soll:
        raise ZeitleisteError(
            f'@@ZEITLEISTE in {name}: Quartale nicht lueckenlos in Reihenfolge '
            f'ab Q1 — im Block {", ".join(ist)}, erwartet {", ".join(soll)}.')
    marken = sum(1 for q in quartale if q['marke'])
    if marken > ZL_MARKEN_MAX:
        print(f'[chartdoc] Hinweis: {marken} Marken im @@ZEITLEISTE-Block — das '
              f'Modul erlaubt hoechstens {ZL_MARKEN_MAX} je Dokument. Gesetzt '
              'wird, was im Block steht; im Bericht melden (Schritt 2).')
    if titel is not None:
        try:
            tmap = {int(k): str(v) for k, v in dict(titel).items()}
        except (TypeError, ValueError):
            raise ZeitleisteError(
                'lies_zeitleiste(titel=…) erwartet {Kapitelnummer: Titel}, '
                'z. B. {1: "Titel von Kapitel 1", 2: "…"}.') from None
        nummern = sorted(tmap)
        for q in quartale:
            fremd = [n for n in q['dicht'] if n not in tmap]
            if fremd:
                raise ZeitleisteError(
                    f'@@ZEITLEISTE in {name}, {q["quartal"]}: dicht= nennt '
                    f'Kapitel {fremd}, die es nicht gibt. Kapitel: {nummern}.')
            q['dicht_titel'] = [tmap[n] for n in q['dicht']]
            q['ruht_titel'] = [tmap[n] for n in nummern if n not in q['dicht']]
    return {'lead': lead, 'quartale': quartale}


def zeitleiste_page(zeilen, kicker='Zeit im Überblick', titel=None,
                    anker='PG_zeit', lead=None, note=None, skala=1.0):
    """Zeitleisten-Seite (Transit und Ultimativ) — EINE Seite, kein Fließtext.

    Sie ersetzt die acht Quartalskapitel (Umbau 2026-09-03) und ist danach die
    einzige Stelle, an der das Kalenderraster noch auftaucht.

    zeilen  [(quartal, spanne, dicht, ruht, dichte[, marke]), ...] — je
            Kalenderquartal eine Zeile, in der Reihenfolge des Fensters:
              quartal  'Q1' … 'Q8'            — aus `quartale`
              spanne   'Jul–Sep 26'           — die Monatsspanne, viertes Feld
                                                der Quartalstupel aus
                                                transitdata.parse()
              dicht    Themenkapitel-Titel, die in diesem Quartal laufen
                       (Liste oder fertiger String)
              ruht     die uebrigen Themen desselben Dokuments
              dichte   'Jul 3 (1) · Aug 5 (2) · Sep 2 (0)' — je Monat
                       aktiv(exakt) aus `hotspots`
              marke    OPTIONAL (seit 2026-09-19, W12): der Text aus
                       `marke=` des @@ZEITLEISTE-Blocks. Er steht in der
                       Dicht-Zelle hinter den Themen, durch „ · " abgesetzt
                       und gedaempft gesetzt (.zl-marke), wortgleich.
                       Vorher kannte die Seite kein Markenfeld und jeder Lauf
                       setzte den Span per HTML-Nachbearbeitung.

    NICHTS DAVON WIRD HIER GERECHNET. Die Werte kommen unveraendert aus dem
    Builder-JSON (transit.py -> transitdata.parse()); auch die Monatsdichte
    wird NICHT zu einer Quartalssumme oder einem Maximum verdichtet — das
    waere gerechnet, und die Regel lautet uebernehmen. Welches Thema in
    welchem Quartal dicht ist, steht im @@ZEITLEISTE-Block der chart_data
    (Zuordnung aus Schritt 2, NICHT das `quartale`-Feld der Kontakte);
    lies_zeitleiste() liest ihn und liefert mit titel= die fertigen
    Titellisten (berichtigt 2026-09-19, W12 — hier stand noch das
    `quartale`-Feld als Quelle).

    lead    Vorspann. Vorgabe ZL_LEAD. Wird der LEAD aus dem Block uebergeben,
            erklaert er die Klammerzahl der Dichte-Spalte nicht — dann haengt
            die Seite ZL_SPALTE an die Fussnote (seit 2026-09-19, W12), es sei
            denn, `note` ist ausdruecklich gesetzt oder der LEAD traegt den
            Satz schon.

    Die Themennamen sind WORTGLEICH die Kapiteltitel des Dokuments. Ein
    erfundener oder gekuerzter Name ist derselbe Fehler wie in der
    Transit-Uhr: die Seite ist eine Navigationshilfe und taugt nur, wenn der
    Leser den Namen im Text wiederfindet.

    skala   skaliert die Tabellenschrift. Beim Standardfenster (8 Quartale)
            passt die Seite bei 1.0; ab etwa elf Quartalen — also bei einem
            Drei-Jahres-Fenster — nicht mehr. Wie bei der Aspektseite wird
            dann EINGEMESSEN, nicht geschaetzt:

                zl = chartdoc.passe_ein(lambda s: build_html(zl_skala=s),
                                        'PG_zeit',
                                        [1.0, .96, .92, .88, .84, .80],
                                        was='Zeitleiste')

            Zweiseitig darf die Zeitleiste nicht werden — sie ist die
            Navigationsseite, und Navigation ueber einen Seitenwechsel hinweg
            ist keine.
    """
    titel = titel or ZEITLEISTE_TITEL
    rows = []
    for nr, z in enumerate(zeilen, 1):
        # 2026-09-19 (W12): optionales sechstes Feld `marke`
        if len(z) not in (5, 6):
            raise ValueError(
                f'zeitleiste_page(): Zeile {nr} hat {len(z)} Felder — erwartet '
                '(quartal, spanne, dicht, ruht, dichte) oder mit Marke '
                '(quartal, spanne, dicht, ruht, dichte, marke).')
        q, spanne, dicht, ruht, dichte = z[:5]
        marke = z[5] if len(z) == 6 else ''
        zd = _zl_liste(dicht, "nichts im Wirkorb")
        if marke:
            zd += f' · <span class="zl-marke">{esc(str(marke))}</span>'
        rows.append(
            f'<tr><td class="zq">{esc(str(q))}</td>'
            f'<td class="zs">{esc(str(spanne))}</td>'
            f'<td class="zd">{zd}</td>'
            f'<td class="zr">{_zl_liste(ruht)}</td>'
            f'<td class="zz">{_zl_liste(dichte)}</td></tr>')
    ld = lead if lead is not None else ZL_LEAD
    nt = note if note is not None else ZL_NOTE
    if lead is not None and note is None and ZL_SPALTE not in lead:
        # 2026-09-19 (W12): Block-LEAD als Vorspann -> Spaltensatz in die
        # Fussnote (so gesetzt in T34-18c und T34-18d, dort je von Hand).
        nt = ZL_NOTE + ' ' + ZL_SPALTE
    return f"""<section class="zeit" id="{anker}">
<div class="fm-kicker">{esc(kicker)}</div>
<h2 class="fm-title">{esc(titel)}</h2>
<div class="fm-rule"></div>
<p class="fm-lead">{esc(ld)}</p>
<table class="zl" style="font-size:{8.1 * skala:.2f}pt">
<colgroup><col style="width:1.0cm"><col style="width:2.35cm">
<col style="width:5.85cm"><col style="width:4.85cm">
<col style="width:3.15cm"></colgroup>
<thead><tr><th>&nbsp;</th><th>Zeitraum</th><th>Dicht</th><th>Ruht</th>
<th>Dichte je Monat</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class="anh-note">{esc(nt)}</div>
</section>"""


# --- Seite: Konstellationen -------------------------------------------------

ELEMENT_VON_ZEICHEN = ['Feuer', 'Erde', 'Luft', 'Wasser']
MODUS_VON_ZEICHEN = ['kardinal', 'fix', 'veränderlich']


def verteilung(planeten):
    """Element- und Modusverteilung der zehn klassischen Planeten.

    planeten: Liste [(Anzeigename, ekl. Laenge), ...] — genau die zehn
    klassischen, in Reihenfolge. Rueckgabe: (elemente, modi), je eine Liste
    [(Label, Anzahl, [Planetennamen]), ...].
    """
    el = {k: [] for k in ELEMENT_VON_ZEICHEN}
    mo = {k: [] for k in MODUS_VON_ZEICHEN}
    for nm, lon in planeten:
        z = int(lon // 30) % 12
        el[ELEMENT_VON_ZEICHEN[z % 4]].append(nm)
        mo[MODUS_VON_ZEICHEN[z % 3]].append(nm)
    return ([(k, len(el[k]), el[k]) for k in ELEMENT_VON_ZEICHEN],
            [(k, len(mo[k]), mo[k]) for k in MODUS_VON_ZEICHEN])


def _balken(reihen):
    """Balkenblock: Label, gefuellter Balken mit Zahl, Planeten darunter."""
    hoch = max([n for _l, n, _p in reihen] + [1])
    out = []
    for lab, n, pl in reihen:
        # 88 %: der laengste Balken endet vor der Zahl, sie bleibt lesbar.
        breite = 0 if n == 0 else max(3.5, n / hoch * 88.0)
        namen = ' · '.join(pl) if pl else '—'
        out.append(
            f'<div class="vrow"><div class="vlab">{esc(lab)}</div>'
            f'<div class="track"><div class="fill b-{_slug(lab)}" '
            f'style="width:{breite:.1f}%"></div>'
            f'<span class="vnum">{n}</span></div>'
            f'<div class="vpl">{esc(namen)}</div></div>')
    return ''.join(out)


# Schriftstufen fuer die Einmessung der Konstellationsseite. Feiner gestaffelt
# als die Aspektseite, weil hier ganze Balkenbloecke kippen und nicht einzelne
# Zeilen.
KONST_STUFEN = (1.0, 0.97, 0.94, 0.91, 0.88, 0.85, 0.82, 0.79)


def _konst_skala_css(anker, s):
    """Lokale Massanpassung der Konstellationsseite, auf ihren Anker begrenzt.

    Nur die Werte, die die Seitenhoehe bestimmen: Schriftgrade, Zeilenpolster,
    Balkenhoehe und die Abstaende der Bloecke. Spaltenbreiten bleiben, sonst
    bricht die Tabelle um. Bei skala == 1.0 wird gar nichts ausgegeben — ein
    Dokument ohne Einmessung ist damit zeichengleich mit dem Stand davor.
    """
    if abs(s - 1.0) < 1e-9:
        return ''
    q = f'#{anker}'
    return f"""<style>
{q} table.konst {{ font-size:{9.3 * s:.2f}pt; }}
{q} table.konst td {{ padding:{0.078 * s:.3f}cm 0.2cm {0.078 * s:.3f}cm 0; }}
{q} table.konst td.g {{ font-size:{10 * s:.2f}pt; }}
{q} table.konst td.lf {{ font-size:{8.6 * s:.2f}pt; }}
{q} table.konst th {{ padding:0 0.2cm {0.14 * s:.3f}cm 0; }}
{q} .tabnote {{ font-size:{7.6 * s:.2f}pt;
   margin:{0.22 * s:.3f}cm 0 {0.46 * s:.3f}cm 0; }}
{q} table.achsen {{ font-size:{9.2 * s:.2f}pt; }}
{q} table.achsen td {{ padding:{0.085 * s:.3f}cm 0.2cm {0.085 * s:.3f}cm 0; }}
{q} h4.blockkopf {{ font-size:{7.4 * s:.2f}pt;
   margin:0 0 {0.22 * s:.3f}cm 0; }}
{q} .dist {{ margin:0 0 {0.46 * s:.3f}cm 0; }}
{q} .vrow {{ margin:0 0 {0.19 * s:.3f}cm 0; }}
{q} .vlab {{ font-size:{9 * s:.2f}pt; }}
{q} .track {{ height:{0.34 * s:.3f}cm; line-height:{0.34 * s:.3f}cm; }}
{q} .fill {{ height:{0.34 * s:.3f}cm; }}
{q} .vnum {{ font-size:{8 * s:.2f}pt; }}
{q} .vpl {{ font-size:{7.6 * s:.2f}pt; margin:{0.06 * s:.3f}cm 0 0 0; }}
</style>"""


def konstellationen_page(zeilen, achsen, elemente, modi, note=None,
                         kicker=None,
                         titel=None, anker='PG_konst',
                         lead=None, fussnoten=(), skala=1.0):
    """Konstellationsseite im Hausstil.

    skala     Massfaktor fuer Schriftgrade, Zeilenpolster und Balkenhoehe.
              **Wird eingemessen, nicht gesetzt** — genau wie Rad-, Aspekt- und
              Uhrseite (Hausstil: „‚Passt auf eine Seite' wird gemessen, nicht
              geschaetzt"). Bis zum 2026-09-09 war die Konstellationsseite die
              einzige Seite mit fester Seitenzahl OHNE Messweg; sie ist zugleich
              die einzige Frontmatter-Seite, deren Inhalt je Chart waechst
              (Fussnoten, Grenzlagen, unaspektierte Faktoren, Achsen-
              Zeichengrenzen). Lief sie ueber, war der Befund stumm: die feste
              Seitenfolge des Hausstils kaputt, `verify` gruen. Aufruf:

                  ks = chartdoc.passe_ein(lambda s: build_html(konst_skala=s),
                                          'PG_konst', chartdoc.KONST_STUFEN,
                                          was='Konstellationsseite')

    zeilen    [(Glyphe, Name, Zeichenname, Gradtext, Haustext, Lauftext), ...]
              — 'SEP' als Glyphe zieht eine Trennlinie.
              Haustext bei Grenzlage NUR als Doppelzahl, z. B. '12/11'.
    achsen    [(Kuerzel, Name, Zeichenname, Gradtext), ...]
    fussnoten weitere Zeilen unter der Tabelle, je ein String. Hierher gehoert
              vor allem der UNASPEKTIERTE Faktor: er taucht in der
              Aspektliste kein einziges Mal auf und steht in der
              Konstellationstabelle wie jeder andere — ein unaspektierter
              Faktor ist aber eine Aussage, kein Loch. Muster:
              „Lilith bildet im Huber-Orbis keinen Aspekt; naechster
              Kandidat 4°58' ausserhalb." Der Befund steht im Strukturbild
              des Datenblatts (Punkt 4) und wird von dort uebernommen, nicht
              nachgerechnet. Neu 2026-09-08 (Pruefbericht EA 5b).
    elemente  [(Label, Anzahl, [Planeten]), ...]  — s. verteilung()
    modi      dito
    """
    titel = KONST_TITEL if titel is None else titel
    kicker = KONST_KICKER if kicker is None else kicker
    rows = []
    for gl, nm, zn, gd, hs, lf in zeilen:
        if gl == 'SEP':
            rows.append('<tr class="sep"><td colspan="6" '
                        'style="height:0.16cm;border-bottom:none"></td></tr>')
            continue
        rows.append(
            f'<tr><td class="g">{gl}</td><td class="nm">{esc(nm)}</td>'
            f'<td class="zn">{esc(zn)}</td><td class="gd">{gd}</td>'
            f'<td class="hs">{esc(hs)}</td><td class="lf">{esc(lf)}</td></tr>')
    ach = ''.join(
        f'<tr><td class="ak">{esc(k)}</td><td class="an_">{esc(n)}</td>'
        f'<td class="az">{esc(z)}</td><td class="ag">{g}</td></tr>'
        for k, n, z, g in achsen)
    ld = f'<p class="fm-lead">{esc(lead)}</p>' if lead else ''
    nt = f'<div class="tabnote">{esc(note)}</div>' if note else ''
    nt += ''.join(f'<div class="tabnote">{esc(z)}</div>'
                  for z in (fussnoten or ()) if z)
    return f"""<section class="front" id="{anker}">
{_konst_skala_css(anker, skala)}
<div class="fm-kicker">{esc(kicker)}</div>
<h2 class="fm-title">{esc(titel)}</h2>
<div class="fm-rule"></div>
{ld}
<table class="konst">
<tr><th>&nbsp;</th><th>{esc(KONST_KOPF['faktor'])}</th><th>{esc(KONST_KOPF['zeichen'])}</th>
<th>{esc(KONST_KOPF['grad'])}</th><th>{esc(KONST_KOPF['haus'])}</th>
<th>{esc(KONST_KOPF['lauf'])}</th></tr>
{''.join(rows)}
</table>
{nt}
<div class="dist"><div class="row"><div class="cell links">
<h4 class="blockkopf">{esc(KONST_KOPF['achsenkreuze'])}</h4>
<table class="achsen"><tr><th>{esc(KONST_KOPF['achse'])}</th><th>&nbsp;</th>
<th>{esc(KONST_KOPF['zeichen'])}</th>
<th>{esc(KONST_KOPF['grad'])}</th></tr>{ach}</table>
</div><div class="cell">
<h4 class="blockkopf">{esc(KONST_KOPF['modi'])}</h4>
{_balken(modi)}
</div></div></div>
<h4 class="blockkopf">{esc(KONST_KOPF['elemente'])}</h4>
{_balken(elemente)}
</section>"""


# --- Seite: Aspekte ---------------------------------------------------------

ASP_GRUPPEN = [('voll', 'Hauptaspekte'),
               ('einseitig', 'Weitere (einseitige) Aspekte'),
               ('neben', 'Nebenaspekte')]

ASP_LEAD = ('Jede Winkelbeziehung deines Charts, voll ausgeschrieben. „e." '
            'markiert einen einseitigen Aspekt (nur einer der beiden Faktoren '
            'hält den Orbis). Bis auf eigens gekennzeichnete Zeilen zeichnet '
            'das Rad dieselbe Liste.')

# Seitentitel der Aspektseite. Steht hier als Konstante, weil er zugleich der
# Pflicht-Baustein ist, den build.assert_render_ready sucht — s. unten.
ASPEKT_TITEL = 'Die Aspekte im Einzelnen'


# ---------------------------------------------------------------------------
# Sprachfassung der sichtbaren Labels (2026-09-22, W57-Nachzug).
#
# Bis heute hatte `chartdoc` keinen Sprachschalter: Seitentitel, Kolumnen,
# Legendenzeilen und die Zeitleisten-Texte standen deutsch im Modul, und eine
# englische Fassung musste sie im Lauf von Hand ueberschreiben — jeder Lauf
# neu, jeder Lauf anders. Die Namen unten sind dieselben Globals wie vorher;
# `setze_sprache()` tauscht ihre Werte und zieht im gleichen Zug die
# Pflicht-Bausteine von `build` nach (s. _pflicht_baustein_angleichen).
#
# WICHTIG fuer neue Labels: Ein Label, das als STANDARDWERT eines Parameters
# steht (`def f(titel=LEGEND_TITEL)`), wird beim Import gebunden und aendert
# sich durch einen Sprachwechsel NICHT mehr. Deshalb heissen diese Parameter
# `None` und holen den Wert im Rumpf. Wer ein Label ergaenzt, haelt sich daran.
SPRACHE = 'de'
_LABEL_NAMEN = ('LEGEND_ROWS', 'LEGEND_TITEL', 'ORBIS_ZEILE', 'ZEITLEISTE_TITEL',
                'ZL_SPALTE', 'ZL_LEAD', 'ZL_NOTE', 'ASPEKT_TITEL',
                'INHALT_TITEL', 'RADIX_TITEL', 'RADIX_KICKER', 'KONST_TITEL',
                'KONST_KICKER', 'KONST_KOPF', 'ASP_GRUPPEN', 'ASP_LEAD')

_LEGEND_ROWS_EN = [
    ("Conjunction", "0°", "two forces at the same point — they merge, amplify "
     "and colour one another."),
    ("Opposition", "180°", "a facing pair, usually met through other people — "
     "the work is balancing, not choosing."),
    ("Square", "90°", "inner friction that pushes — uncomfortable, and the "
     "strongest engine of development."),
    ("Trine", "120°", "effortless flow, an inborn talent — which is exactly why "
     "it is easily left lying idle."),
    ("Sextile", "60°", "stimulus and opportunity — easier to reach than the "
     "trine, but it has to be taken up."),
    ("Quincunx", "150°", "two forces that do not fit together and cannot be "
     "ignored — a constant readjusting."),
    ("Semisextile", "30°", "a quiet irritation between neighbouring forces — a "
     "searching movement."),
]
_ORBIS_ZEILE_EN = ('Orb by factor: Sun, Moon 8° · Mercury, Venus, Jupiter 6° '
                   '· Mars, Saturn 5° · Uranus, Neptune, Pluto 4° · axes and '
                   'Chiron 5° · Lilith 3° · Pholus 2°. The '
                   'lunar node takes the orb of the aspecting factor. Minor '
                   'aspects are tighter, capped at both factors\' orbs.')
_ZL_SPALTE_EN = ('The far right column gives the number of contacts the '
                 'calculation counted for each month; the figure in brackets '
                 'is the number of days on which an angle stands exact.')
_ZL_LEAD_EN = ('This page is for looking things up, not for reading. Each line '
               'is one quarter of the window: beside it stands which themes run '
               'densely in those three months and which are quiet in the same '
               'stretch. ' + _ZL_SPALTE_EN
               + ' A high figure does not mean that much happens — it means '
               'that much is touched at once.')
_ZL_NOTE_EN = ('The quarters are calendar quarters; Q1 is the quarter in which '
               'this horoscope was drawn up. Spans and figures are taken from '
               'the calculation unchanged.')

_LABELS = {
    'en': {
        'LEGEND_ROWS': _LEGEND_ROWS_EN,
        'LEGEND_TITEL': 'The Aspects and What They Mean',
        'ORBIS_ZEILE': _ORBIS_ZEILE_EN,
        'ZEITLEISTE_TITEL': 'The Timeline',
        'ZL_SPALTE': _ZL_SPALTE_EN,
        'ZL_LEAD': _ZL_LEAD_EN,
        'ZL_NOTE': _ZL_NOTE_EN,
        'ASPEKT_TITEL': 'The Aspects in Detail',
        'INHALT_TITEL': 'Contents',
        'RADIX_TITEL': 'The Chart',
        'RADIX_KICKER': 'The Chart as a Picture',
        'KONST_TITEL': 'The Constellations',
        'KONST_KICKER': 'Positions & Distribution',
        'KONST_KOPF': {'faktor': 'Factor', 'zeichen': 'Sign', 'grad': 'Degree',
                       'haus': 'House', 'lauf': 'Motion', 'achse': 'Axis',
                       'achsenkreuze': 'The Axis Crosses',
                       'modi': 'Mode distribution (unweighted)',
                       'elemente': 'Element distribution (ten classical '
                                   'planets, unweighted)'},
        'ASP_GRUPPEN': [('voll', 'Major aspects'),
                        ('einseitig', 'Further (one-sided) aspects'),
                        ('neben', 'Minor aspects')],
        'ASP_LEAD': ('Every angular relationship in your chart, written out in '
                     'full. "o." marks a one-sided aspect (only one of the two '
                     'factors holds the orb). Except for lines marked '
                     'otherwise, the wheel draws the same list.'),
    },
}
# die deutsche Fassung ist der Stand beim Import — nicht abgeschrieben, sondern
# eingesammelt, damit sie nicht an zwei Orten gepflegt werden muss
_LABELS['de'] = {n: globals()[n] for n in _LABEL_NAMEN}
assert set(_LABELS['en']) == set(_LABEL_NAMEN), \
    'Labeltafel und _LABEL_NAMEN laufen auseinander'

# Pflicht-Titel, die NICHT chartdoc druckt, sondern der Schritt-3-Lauf selbst
# setzt (Transit-Uhr-Seite und die beiden Anhangtabellen, s. Design-Modul
# Zeitebene; die Themen-Analyse ihre zwei eigenen). build.verify() verlangt den
# woertlichen Titel im sichtbaren Text — ohne diese Paare wuerde ein englisches
# PDF an einer deutschen Erwartung scheitern. Erstes Element deutsch, zweites
# englisch; die Angleichung tauscht in beide Richtungen.
_PFLICHT_PAARE = (
    ('Die Transit-Uhr', 'The Transit Clock'),
    ('Die langen Linien im Überblick', 'The Long Lines at a Glance'),
    ('Der Stichtag im Überblick', 'The Reference Date at a Glance'),
    ('Die tragenden Konstellationen', 'The Constellations That Carry Them'),
    ('Die Zeitfenster im Überblick', 'The Time Windows at a Glance'),
)


def setze_sprache(code='de'):
    """Sprache aller sichtbaren Labels setzen ('de' oder 'en').

    Wirkt auf Seitentitel, Kolumnenzeilen, Aspekt-Legende, Orbis-Zeile und die
    Texte der Zeitleisten-Seite — und zieht `build.PFLICHT_BAUSTEINE` nach,
    damit `build.verify()` den Titel erwartet, der wirklich gedruckt wird.
    Einmal vor dem ersten Seitenaufbau aufrufen, am einfachsten ueber
    `konfiguriere(sprache='en')`.

    NICHT betroffen (und mit Absicht): die Kopfzeilen `**Signatur:**` und
    `**Beleg:**` der Analyse — `build.parse_analyse()` erkennt genau diese
    beiden Woerter (Werkzeuge-Modul A3).
    """
    global SPRACHE
    code = (code or 'de').strip().lower()[:2]
    if code not in _LABELS:
        raise ValueError("sprache: 'de' oder 'en', nicht %r" % code)
    globals().update(_LABELS[code])
    SPRACHE = code
    _pflicht_baustein_angleichen()
    # Die Transit-Uhr ist eine eigene Datei mit eigener Labeltafel; ohne diesen
    # Zug blieb die Grafik im englischen PDF deutsch beschriftet (W57). Fehlt
    # das Modul (Geburtshoroskop-Lauf), ist das kein Fehler.
    try:
        import transituhr_fusion as _tuf
        _tuf.setze_sprache(code)
    except Exception:
        pass
    return code


def _paare_tauschen():
    """Die Pflicht-Titel aus _PFLICHT_PAARE auf SPRACHE stellen — in jeder
    Liste von build.PFLICHT_BAUSTEINE, in beide Richtungen und mehrfach
    aufrufbar."""
    ziel = {}
    for de, en in _PFLICHT_PAARE:
        gewuenscht = en if SPRACHE == 'en' else de
        ziel[de] = gewuenscht
        ziel[en] = gewuenscht
    try:
        typen = build.PFLICHT_BAUSTEINE
    except AttributeError:
        return
    for eintrag_typ in typen.values():
        liste = eintrag_typ.get('text') if isinstance(eintrag_typ, dict) else None
        if not liste:
            continue
        for i, e in enumerate(liste):
            if e and e[0] in ziel:
                liste[i] = (ziel[e[0]], e[1])


def _pflicht_baustein_angleichen():
    """Die Pflicht-Bausteine auf die hier gesetzten Seitentitel ziehen.

    Betrifft zwei Titel: die Aspektseite (Chart-Basis) und die Zeitleiste
    (Transit und Ultimativ).

    build.PFLICHT_BAUSTEINE verlangt seit jeher den WOERTLICHEN Seitentitel im
    sichtbaren Text; bis zum 2026-07-27 hiess die Seite „Die Aspekte im
    Wortlaut". Mit dem Hausstil heisst sie „Die Aspekte im Einzelnen" (nach dem
    Kombi-Vorbild). Statt denselben Wortlaut an zwei Orten zu pflegen, meldet
    chartdoc ihn beim Import an build — Titel und Guardrail koennen so nicht
    mehr auseinanderlaufen. Wer den Titel hier aendert, aendert automatisch
    auch den Pflicht-Baustein; build.py bleibt unberuehrt.
    """
    try:
        eintraege = build.PFLICHT_BAUSTEINE['*']['text']
    except (AttributeError, KeyError, TypeError):
        return
    for i, eintrag in enumerate(eintraege):
        if eintrag and eintrag[0].startswith(('Die Aspekte im ', 'The Aspects in ')):
            eintraege[i] = (ASPEKT_TITEL, eintrag[1])
            break
    else:
        eintraege.append((ASPEKT_TITEL, 'voll ausgeschriebene Aspekttabelle'))
    # 2026-09-22: dieselbe Konstruktion fuer die zwei weiteren Titel, die
    # chartdoc selbst druckt — erkannt an der BESCHREIBUNG, nicht am Titel, und
    # in JEDER Typ-Liste: die Themen-Analyse setzt `basis: False` und bringt
    # ihre eigene Inhalts-Zeile mit, die sonst deutsch stehen blieb.
    for liste in [v.get('text') for v in build.PFLICHT_BAUSTEINE.values()
                  if isinstance(v, dict)]:
        if not liste:
            continue
        for kennung, wert in (('Inhaltsverzeichnis', INHALT_TITEL),
                              ('Aspekt-Legende', LEGEND_TITEL)):
            for i, eintrag in enumerate(liste):
                if eintrag and kennung in eintrag[1]:
                    liste[i] = (wert, eintrag[1])
                    break
    # und die Titel, die der Lauf selbst setzt: nach Sprache tauschen
    _paare_tauschen()
    # Zeitleiste: dieselbe Konstruktion, aber in den Typ-Listen. Erkannt wird
    # der Eintrag an seiner BESCHREIBUNG, nicht am Titel — sonst faende die
    # Angleichung ihren eigenen Eintrag nicht mehr, sobald der Titel abweicht.
    for typ in ('transit', 'ultimativ'):
        liste = build.PFLICHT_BAUSTEINE.get(typ, {}).get('text')
        if not liste:
            continue
        for i, eintrag in enumerate(liste):
            if eintrag and 'Zeitleist' in eintrag[1]:
                liste[i] = (ZEITLEISTE_TITEL, eintrag[1])
                break


_pflicht_baustein_angleichen()


def _fac(name):
    """Glyph + Name eines Aspektpartners. Achsen als Kuerzel; ein Faktor ohne
    font-gedeckte Glyphe erscheint nur mit Namen.

    Was als „keine Glyphe" gilt, haengt seit dem 2026-09-08 nicht mehr am
    verdrahteten String 'Pho', sondern an der LAENGE: ein Glyphenfeld, das
    nach Abzug der Variantenselektoren mehr als EIN Zeichen traegt, ist ein
    Name, kein Symbol. Vorher rutschte jede andere nicht-symbolische Glyphe
    wortlos durch — `{'name':'Pholus','glyph':'Pholus'}` haette in jeder
    Aspektzeile „Pholus Pholus" gesetzt (Pruefbericht EA 2026-09-08, 1.3
    und 4.2). Der Vertrag im Datenblatt-Modul verlangt weiterhin 'Pho'; diese
    Pruefung ist das Netz darunter, nicht ihr Ersatz.
    """
    if name in ('AC', 'MC', 'DC', 'IC'):
        return f'<span class="gy">{name}</span>'
    g = (GLYPH_OF.get(name) or '').replace('\ufe0e', '').replace('\ufe0f', '').strip()
    disp = esc(name_of(name))
    if len(g) != 1:
        return disp
    return f'<span class="gy">{g}</span> {disp}'


def aspekt_page(aspekte, skala=1.0, kicker='Das Chart im Bild',
                titel=None, anker='PG_asp'):
    """Aspektseite im Hausstil — Tabelle UND Legende auf EINER Seite.

    skala skaliert Tabellen- und Legendenschrift gemeinsam; der Chart-Builder
    sucht damit die groesste Stufe, die noch auf eine Seite passt
    (s. passe_aspektseite_ein).

    Orb (2026-09-19, W2): `aspekte` traegt den UNGERUNDETEN Orb aus
    radix.aspektliste(); die Seite rundet ihn genau einmal mit
    build.orb_text() — dieselbe Funktion wie die Aspekttabelle des
    Datenblatts, damit Seite, Tabelle und Belege dieselbe Bogenminute zeigen.
    Das konfigurierte `gr` greift hier nicht mehr.
    """
    titel = titel or ASPEKT_TITEL
    setze_zusatzaspekte(aspekte)
    unerklaert = sorted({a['name'] for a in aspekte
                         if a['name'] not in ASPEKT_KLASSE
                         and a['name'] not in ZUSATZ_LEGENDE})
    if unerklaert:
        raise RuntimeError(
            'Aspektarten in der Tabelle, die die Legende nicht erklaert: '
            + ', '.join(unerklaert) + '.\n'
            'Der Klartext-Standard verlangt, dass jedes sichtbare Zeichen '
            'einmal benannt wird. Entweder die Art in chartdoc.ZUSATZ_LEGENDE '
            'aufnehmen (dann erscheint sie automatisch in BEIDEN '
            'Legendenkaesten) oder die Zeile aus der Aspektliste nehmen.')
    blocks = []
    for i, (key, label) in enumerate(ASP_GRUPPEN):
        grp = [a for a in aspekte if a['strength'] == key]
        if not grp:
            continue
        cls = 'asp-grp first' if i == 0 else 'asp-grp'
        rows = []
        for a in grp:
            k = ASPEKT_KLASSE.get(a['name'], 'konj')
            mir = (f' <span class="mir">({esc(a["spiegel"])})</span>'
                   if a.get('spiegel') else '')
            e = '<span class="eins">e.</span>' if key == 'einseitig' else ''
            rows.append(
                f'<tr><td class="ax">{_fac(a["a"])} '
                f'<span class="an a-{k}">{a["name"]}</span> '
                f'{_fac(a["b"])}{mir}</td>'
                f'<td class="ao">{_orb_text(a["orb"])}{e}</td></tr>')
        blocks.append(f'<div class="{cls}">{esc(label)}</div>'
                      f'<table class="aspt">{"".join(rows)}</table>')
    tab_pt = 9.0 * skala
    leg_pt = 8.4 * skala
    return f"""<section class="front" id="{anker}">
<div class="fm-kicker">{esc(kicker)}</div>
<h2 class="fm-title">{esc(titel)}</h2>
<div class="fm-rule"></div>
<p class="fm-lead">{esc(ASP_LEAD)}</p>
<div class="asp" style="font-size:{tab_pt:.2f}pt">{''.join(blocks)}</div>
<div style="height:0.34cm"></div>
{aspekt_legende(stil=f'font-size:{leg_pt:.2f}pt', zusatz=True, orbis=True)}
</section>"""


def passe_ein(baue_html, anker, werte, was='Seite', verbose=True):
    """Groessten Wert aus `werte` suchen, bei dem `anker` EINE Seite bleibt.

    baue_html(wert) -> vollstaendiges Dokument-HTML. Damit haengt keine Seite
    des Hausstils mehr an von Hand gesetzten Massen: Aspektseite (Schriftskala)
    und Transit-Uhr (Bildbreite) messen sich selbst ein. Passt kein Wert, wird
    der letzte zurueckgegeben und laut gewarnt — stillschweigend zweiseitig
    darf keine dieser Seiten werden.
    """
    for w in werte:
        doc = build._render_doc(baue_html(w))
        if len(_anker_seiten(doc).get(anker, [])) <= 1:
            if verbose:
                print(f'  {was} passt bei {w}.')
            return w
    print(f'  !! {was} passt auch bei {werte[-1]} nicht auf eine Seite.')
    return werte[-1]


def passe_aspektseite_ein(baue_html, aspekte, anker='PG_asp',
                          stufen=(1.08, 1.04, 1.0, 0.96, 0.92, 0.88, 0.84,
                                  0.80, 0.76),
                          verbose=True):
    """Groesste Schriftstufe suchen, bei der die Aspektseite EINE Seite bleibt.

    baue_html(skala) -> vollstaendiges Dokument-HTML mit aspekt_page(skala).
    Rueckgabe: die gewaehlte Skala. Findet keine Stufe eine Loesung, wird die
    kleinste zurueckgegeben und laut gewarnt — stillschweigend zweiseitig darf
    die Aspektseite nie werden.
    """
    for s in stufen:
        doc = build._render_doc(baue_html(s))
        seiten = _anker_seiten(doc).get(anker, [])
        if len(seiten) <= 1:
            if verbose:
                print(f'  Aspektseite passt bei Skala {s:.2f} '
                      f'({len(aspekte)} Zeilen).')
            return s
    print(f'  !! Aspektseite passt auch bei Skala {stufen[-1]:.2f} nicht auf '
          'eine Seite — Inhalt kuerzen oder Layout pruefen.')
    return stufen[-1]


def _anker_seiten(doc):
    """id -> Liste aller Seiten, auf denen der Anker Kaesten hat."""
    out = {}
    for pi, page in enumerate(doc.pages, 1):
        for bx in build._walk(page._page_box):
            el = getattr(bx, 'element', None)
            if el is not None and hasattr(el, 'get'):
                iid = el.get('id')
                if iid and (iid.startswith('PG_') or iid.startswith('CH_')):
                    out.setdefault(iid, [])
                    if pi not in out[iid]:
                        out[iid].append(pi)
    return out


# --- Kapitelkopf, Absaetze, Teiler ------------------------------------------

ASPEKT_WORT = re.compile(
    r'Konjunktion|Opposition|Quadrat|Trigon|Sextil|Quincunx|Halbsextil|'
    r'\bOrb\b|[☌☍□△⚹⚻⚺]')


# Wo Signatur und Beleg rendern. 'fuss' ist seit dem 2026-09-05 der Standard
# fuer JEDEN Dokumenttyp: beide stehen am Kapitelende, unter der letzten
# Bewegung. 'kopf' ist der Stand davor und gilt nur noch fuer Laeufe OHNE die
# therapeutische Wirkform (Innere Arbeit ausdruecklich abbestellt, „klassische
# Kapitel") — dort gibt es keinen Grund, den Beleg nach hinten zu nehmen.
# Umschalten ueber konfiguriere(beleg_platz='kopf'), nie durch Zuweisung von
# aussen. Im analyse.md aendert sich NICHTS: dort stehen Signatur und Beleg in
# beiden Faellen direkt unter der Kapitel-H2, weil build.parse_analyse() sie
# nur dort erkennt. Die Verlagerung passiert ausschliesslich beim Rendern.
BELEG_PLATZ = 'fuss'


def _beleg_streifen(it, sig_html=''):
    """Der helle Streifen: optionale Signaturzeile, dann der Beleg.

    Der Beleg rendert ZEILENWEISE — die Staende VOR der ersten Aspektangabe
    bilden die Kopfzeile (mit „BELEG:"-Label), jede weitere Angabe bekommt
    eine eigene eingerueckte „–"-Zeile. Ab sechs Beziehungszeilen laeuft der
    Streifen zweispaltig, sonst wird er bei transit- oder aspektreichen
    Kapiteln bis zu 23 Zeilen hoch.

    Gibt '' zurueck, wenn weder Signatur noch Beleg vorliegen — ein Kapitel
    ohne beides (Auftakt, Teiler, Rechenschafts- und Sammelkapitel,
    Schlusswort, Fachmodus) erzeugt damit KEINEN leeren Streifen.
    """
    bel_txt = (it.get('beleg') or '').strip()
    if not bel_txt and not sig_html:
        return ''
    kopf, zeilen, rest = '', '', []
    if bel_txt:
        segs = [s.strip() for s in re.split(r'\s+·\s+', bel_txt) if s.strip()]
        stand, seen_rel = [], False
        for s in segs:
            if not seen_rel and not ASPEKT_WORT.search(s):
                stand.append(s)
            else:
                seen_rel = True
                rest.append(s)
        if not stand and rest:
            stand, rest = [rest[0]], rest[1:]
        kopf = (f'<div class="beleg-stand"><span class="lbl">Beleg:</span> '
                f'{esc(" · ".join(stand))}</div>') if stand else ''
        zeilen = ''.join(f'<div class="beleg-asp"><span class="mk">–</span>'
                         f'{esc(r)}</div>' for r in rest)
    cls = 'beleg two' if len(rest) >= 6 else 'beleg'
    return f'<div class="{cls}">{sig_html}{kopf}{zeilen}</div>'


def build_head(it):
    """Kapitelkopf: Kicker, Titel, Regel.

    Im Standard (BELEG_PLATZ='fuss') traegt der Kopf NUR das — Signatur und
    Beleg baut `build_fuss(it)` ans Kapitelende. Steht BELEG_PLATZ auf 'kopf'
    (Lauf ohne die Innere Arbeit), rendert er wie frueher zweizonig: Signatur
    als kursiver Untertitel, darunter der Beleg als schmaler Streifen (kein
    float — sonst kollidiert er mit dem Satz-Schutz).
    """
    kick = (f'<div class="kicker">{esc(it["kicker"])}</div>'
            if it.get('kicker') else '')
    sig = bel = ''
    if BELEG_PLATZ == 'kopf':
        sig = (f'<div class="signatur">{esc(it["signatur"])}</div>'
               if it.get('signatur') else '')
        bel = _beleg_streifen(it)
    return (f'<div class="chapter-head">{kick}'
            f'<h2 class="chaptitle">{esc(it["title"])}</h2>{sig}'
            f'<div class="rule"></div>{bel}</div>')


def build_section(i, it, breaks, part_kicker=(), open_page=(), erstes=False):
    """Eine ganze Kapitel-SEKTION: Wrapper, Kopf, Koerper, Fuss — ein Aufruf.

    Neu 2026-09-17 (Klasse-2-Entscheidungslauf). Bis dahin stand die
    Kapitel-Schleife samt ihrer CSS-Klassennamen (`chapter`, `chapter-first`,
    `part`, `part-inner`) NUR in `claude/REFERENZ_Chart_Builder_Ultimativ.py`;
    kein Modul nannte sie, und zwei Prueflaeufe haben das als Befund gemeldet.
    Sie gehoeren hierher: dieselbe Begruendung, mit der `build_bloecke()` am
    2026-09-09 die Block-Schleife uebernommen hat. Wer die Schleife weiter von
    Hand baut, ist damit nicht falsch — diese Funktion tut genau dasselbe.

    i              Kapitelindex (0-basiert), wie bei build_bloecke()
    it             das dekorierte Kapitel aus build.prepare_chapters()
    breaks         die Satz-Umbruchmenge von render_sentence_safe()
    part_kicker    Kicker, die eine TEILERSEITE sind (z. B. {'Zweiter Teil'})
    open_page      Kicker, die IMMER auf einer neuen Seite beginnen
    erstes         True fuer das erste Kapitel des Dokuments

    -> vollstaendiges `<section …>…</section>`
    """
    is_part = it.get('kicker') in part_kicker
    allow_drop = not is_part
    cls = ['chapter']
    if is_part:
        cls.append('part')
    if erstes or it.get('kicker') in open_page:
        cls.append('chapter-first')
    head = build_part_head(it) if is_part else build_head(it)
    inner = head + build_bloecke(i, it, breaks, allow_drop) + build_fuss(it)
    if is_part:
        inner = '<div class="part-inner">%s</div>' % inner
    return '<section class="%s" id="CH_%d">%s</section>' % (' '.join(cls), i, inner)


def build_fuss(it):
    """Kapitelfuss: Signatur und Beleg als schmaler heller Streifen.

    Gehoert HINTER den letzten Absatz des Kapitels, innerhalb der
    <section class="chapter">:

        inner = head + ''.join(body) + chartdoc.build_fuss(it)

    Gibt '' zurueck bei Teiler-Kapiteln, bei BELEG_PLATZ='kopf' und bei jedem
    Kapitel ohne Signatur UND ohne Beleg — Auftakt, Trenner,
    Rechenschaftskapitel, Sammelkapitel und Schlusswort laufen also sauber
    durch, ohne einen leeren Streifen zu erzeugen.
    """
    if BELEG_PLATZ != 'fuss' or not _hat_fuss(it):
        return ''
    sig_txt = (it.get('signatur') or '').strip()
    sig = f'<div class="fuss-sig">{esc(sig_txt)}</div>' if sig_txt else ''
    streifen = _beleg_streifen(it, sig_html=sig)
    return f'<div class="kapitel-fuss">{streifen}</div>' if streifen else ''


def _hat_fuss(it):
    """Traegt dieses Kapitel einen Fuss? Teiler-Seiten nie (sie laufen ueber
    build_part_head und tragen weder Signatur noch Beleg)."""
    if (it.get('kicker') or '') in PART_KICKER:
        return False
    return bool((it.get('signatur') or '').strip()
                or (it.get('beleg') or '').strip())


def pruefe_kapitelkopf(items):
    """Harte Gegenprobe vor dem Rendern: traegt JEDES Kapitel einen Kicker?

    Ueberschriften kommen aus Schritt 2 in genau EINER Form,
    `## <Kicker> · <Titel>`. `parse_analyse()` toleriert eine Ueberschrift
    ohne Trenner als Altbestand und setzt einen leeren Kicker — und genau das
    lief bis zum 2026-09-08 folgenlos durch: `toc_gruppen()` erkennt Auftakt
    und Schlusswort AM KICKER, bei leerem Kicker rutscht das Schlusswort als
    gewoehnlicher Eintrag unter die Auftakt-Gruppe. Das Verzeichnis ist dann
    nicht falsch, sondern flacher als vorgesehen; kein Preflight, kein
    `verify()` und keine Gegenprobe schlug an (Pruefbericht EA 2026-09-08,
    1.1). Die Meldung steht deshalb hier, wo sie sichtbar wird, nicht in
    `parse_analyse()`, wo sie ueberlesen wurde — gebaut wie
    `pruefe_kapitelfuss()`: harter Abbruch mit der zu aendernden Zeile.

    Vorgesehen sind Zahl-Kicker fuer die deutenden Kapitel und Wort-Kicker
    fuer alle uebrigen (`Auftakt`, `Rechenschaft`, `Hauptthemen`,
    `Konfliktfelder`, `Lebensaufgaben`, `Schlusswort`) sowie die
    Teiler-Kicker aus PART_KICKER.
    """
    ohne = [(i, it.get('title') or '(ohne Titel)')
            for i, it in enumerate(items) if not (it.get('kicker') or '').strip()]
    if not ohne:
        return
    zeilen = '\n'.join(f'    Kapitel {i}: "## {t}"' for i, t in ohne)
    raise RuntimeError(
        f'{len(ohne)} Kapitelueberschrift(en) ohne Kicker:\n{zeilen}\n'
        'Ueberschriften kommen in genau EINER Form: "## <Kicker> · <Titel>".\n'
        'Die deutenden Kapitel tragen eine Nummer als Kicker, alle uebrigen '
        'ein sprechendes Wort — Auftakt, Rechenschaft, Hauptthemen, '
        'Konfliktfelder, Lebensaufgaben, Schlusswort; Teiler ihren '
        'PART_KICKER.\nDas ist ein Fehler in Schritt 2: die Zeile in der '
        'analyse.md ergaenzen (Trenner ist " · ", kein Bindestrich), dann '
        'erneut rendern. Ohne Kicker bildet toc_gruppen() die Gruppen des '
        'Inhaltsverzeichnisses falsch.')


def pruefe_kapitelfuss(html_str, items):
    """Harte Gegenprobe vor dem Rendern: traegt jedes Kapitel mit Signatur
    oder Beleg auch seinen Fuss-Block?

    Die Kapitel-Schleife steht im chart-eigenen Builder, und der wird je Chart
    neu geschrieben — ein vergessener `build_fuss(it)`-Aufruf wuerde Signatur
    UND Beleg lautlos aus dem ganzen Dokument entfernen. Genau das faengt
    diese Probe ab: sie bricht hart ab, statt still ein Horoskop ohne
    Rueckbindung zu liefern (Barnum-Schutz, s. Klartext-Modul).
    Wird von render_mit_inhalt() selbst aufgerufen.
    """
    if BELEG_PLATZ != 'fuss':
        return
    soll = sum(1 for it in items if _hat_fuss(it))
    ist = html_str.count('class="kapitel-fuss"')
    if ist == soll:
        return
    raise RuntimeError(
        f'Kapitelfuss stimmt nicht: {soll} Kapitel tragen Signatur oder '
        f'Beleg, im HTML stehen aber {ist} Fuss-Bloecke.\n'
        'Seit dem 2026-09-05 rendern Signatur und Beleg am KAPITELENDE. Die '
        'Kapitel-Schleife des Chart-Builders muss den Fuss hinter den letzten '
        'Absatz setzen:\n'
        "    inner = head + ''.join(body) + chartdoc.build_fuss(it)\n"
        'Soll der Beleg ausnahmsweise am Kopf stehen (Lauf ohne die '
        "therapeutische Wirkform), chartdoc.konfiguriere(beleg_platz='kopf') "
        'setzen — dann rendert build_head() wieder zweizonig.')


def pruefe_orbis_zeile(html_str):
    """Harte Gegenprobe vor dem Rendern: traegt eine vorhandene Aspektseite
    auch die Orbis-Staffelung?

    Neu 2026-09-14 (Pruefbericht EA Schritt 3+4, 5.2 und 5.7). Das
    Design-Modul macht ORBIS_ZEILE seit dem 2026-09-08 zur Pflicht unter der
    Aspekttabelle, `aspekt_page()` setzte sie sechs Tage lang nicht, und
    NICHTS hat es gemerkt: kein Preflight, kein verify(), keine Gegenprobe —
    weil nichts sie zaehlt. Dieselbe Bauart wie `pruefe_kapitelfuss()`, aus
    demselben Grund: ein fehlendes Element, das lautlos durchlaeuft, ist
    teurer als ein Abbruch.

    Geprueft wird nur, WENN eine Aspektseite im Dokument steht — Einzelseiten
    und Sonderfaelle ohne sie laufen unberuehrt durch.
    """
    if ASPEKT_TITEL not in html_str:
        return
    if ORBIS_ZEILE[:40] in html_str:
        return
    raise RuntimeError(
        'Aspektseite ohne Orbis-Staffelung: Das Dokument enthaelt '
        f'„{ASPEKT_TITEL}", aber nicht chartdoc.ORBIS_ZEILE.\n'
        'Sie ist seit dem 2026-09-08 Pflicht unter der Aspekttabelle '
        '(Design-Modul, Aspekt-Legende) — bei einem Band, dessen Kapitel mit '
        'Gradminuten belegen, ist sie die eine Angabe, mit der ein Leser eine '
        'Zeile nachpruefen kann.\n'
        'Gesetzt wird sie von aspekt_page() selbst:\n'
        "    aspekt_legende(stil=…, zusatz=True, orbis=True)\n"
        'Baut der Chart-Builder die Aspektseite ausnahmsweise selbst, gehoert '
        'derselbe Aufruf dorthin.')


def build_part_head(it):
    kick = f'<div class="kicker">{esc(it["kicker"])}</div>'
    return (f'{kick}<h2 class="chaptitle">{esc(it["title"])}</h2>'
            f'<div class="part-orn">{esc(PART_ORNAMENT)}</div>')


def build_paragraph(i, j, b, breaks, allow_drop, is_first_block):
    sents = b['sent']
    kset = {k for (ii, jj, k) in breaks
            if ii == i and jj == j and 0 <= k < len(sents)}
    inner = sorted(k for k in kset if k > 0)
    whole_break = (0 in kset) and not is_first_block
    starts, ends = [0] + inner, inner + [len(sents)]
    out = []
    for seg_no, (s, e) in enumerate(zip(starts, ends)):
        if s >= e:
            continue
        cls = []
        if seg_no > 0 or (seg_no == 0 and whole_break):
            cls.append('sbrk')
        if is_first_block and s == 0:
            cls.append('first')
        spans = []
        for k in range(s, e):
            t = sents[k]
            if (is_first_block and s == 0 and k == 0 and allow_drop
                    and t[:1].isalpha()):
                body = f'<span class="dropcap">{esc(t[0])}</span>{esc(t[1:])}'
            else:
                body = esc(t)
            spans.append(f'<span id="S_{i}_{j}_{k}">{body}</span>')
        ca = f' class="{" ".join(cls)}"' if cls else ''
        out.append(f'<p{ca}>' + ' '.join(spans) + '</p>')
    return '\n'.join(out)


def build_bloecke(i, it, breaks, allow_drop=True):
    """Der KOERPER eines Kapitels — Absaetze, Listen, Zwischentitel.

    Ersetzt die Block-Schleife, die bis zum 2026-09-09 in jedem chart-eigenen
    Builder von Hand stand. Grund (Pruefbericht Geburtshoroskop Schritt 3+4,
    Rubrik 2): `build.BASE_CSS` haertet Zwischentitel mit
    `.subhead { break-after: avoid }` und verspricht im Kommentar „Zwischentitel
    nie allein am Seitenfuss". **WeasyPrint setzt `break-after: avoid` nicht um.**
    Im Pruefdokument stand ein Zwischentitel allein am Seitenfuss und
    `verify()` meldete ihn als „endet mitten im Satz" — richtig, aber an einer
    Stelle, die kein Modul erklaerte.

    Gegenmittel: Zwischentitel und Folgeabsatz in einen `.subwrap`-Block mit
    `break-inside: avoid`, das WeasyPrint umsetzt. **Nicht** beim ERSTEN Absatz
    eines Kapitels — dessen Bindung an den Kapitelkopf haengt an
    `.chapter > p.first`, einem Kindselektor, den ein Wrapper brechen wuerde.

    Aufruf in der Kapitel-Schleife:

        inner = (chartdoc.build_head(it)
                 + chartdoc.build_bloecke(i, it, breaks, allow_drop)
                 + chartdoc.build_fuss(it))
    """
    body, first_p_used, n = [], False, len(it['blocks'])
    j = 0
    while j < n:
        b = it['blocks'][j]
        if b['type'] == 'li':
            lis = []
            while j < n and it['blocks'][j]['type'] == 'li':
                lis.append(it['blocks'][j])
                j += 1
            body.append('<ol class="lesart">' + ''.join(
                f'<li>{esc(x["text"])}</li>' for x in lis) + '</ol>')
            continue
        if b['type'] == 'subhead':
            sub = f'<div class="subhead">{esc(b["text"])}</div>'
            nxt = it['blocks'][j + 1] if j + 1 < n else None
            if first_p_used and nxt and nxt['type'] == 'p':
                body.append('<div class="subwrap">' + sub
                            + build_paragraph(i, j + 1, nxt, breaks,
                                              allow_drop, False)
                            + '</div>')
                j += 2
                continue
            body.append(sub)
        else:
            is_first_block = not first_p_used
            first_p_used = True
            body.append(build_paragraph(i, j, b, breaks, allow_drop,
                                        is_first_block))
        j += 1
    return ''.join(body)


# --- Inhaltsverzeichnis -----------------------------------------------------

def _ist_jetzt(titel, teil3_a):
    """Gehoert ein Teil-III-Kapitel in Block A (das Jetzt)?

    Ohne Angabe gilt die alte Vorgabe: nur das Kapitel „Wo du gerade stehst".
    Charts, die den Stichtag auf MEHRERE Kapitel verteilen (etwa je ein
    Kapitel fuer die Knotenkontakte, eine am Stichtag exakte Opposition und
    Nachhall/Anmarsch), geben die Titel oder Titelanfaenge ihrer A-Kapitel als
    Liste mit — oder eine Funktion titel -> bool. Ohne das landen
    Momentaufnahme-Kapitel im Inhaltsverzeichnis unter „B — Die langen Linien"
    und behaupten damit eine Dauer, die sie nicht haben.
    """
    if teil3_a is None:
        return titel.startswith('Wo du gerade stehst')
    if callable(teil3_a):
        return bool(teil3_a(titel))
    return any(titel.startswith(p) for p in teil3_a)


# 2026-09-22 (Prueflauf Transit Schritt 3+4 vom 2026-09-22, 1.1): Beide
# Erkennungen hingen am deutschen Wort. In einem englischen Band heisst der
# Nummernkicker `Chapter n` — er fiel durch die Nummernpruefung, galt als
# WORT-Kicker, wanderte vor den Titel und liess die 0,72 cm schmale
# Nummernspalte leer; Auftakt und Schlusswort heissen `Prelude` und
# `Closing Word` und eroeffneten keine Gruppe mehr, das Schlusswort rutschte
# unter die erste. Beide Schreibweisen gelten jetzt unabhaengig von SPRACHE:
# ein deutscher Band traegt nie einen Kicker `Chapter`, ein englischer nie
# einen Kicker `Kapitel` — eine Fallunterscheidung waere nur eine weitere
# Stelle, an der eine Sprachumschaltung vergessen werden kann.
_GRUPPEN_KICKER = ('Auftakt', 'Schlusswort', 'Prelude', 'Closing Word')
_NUMMERN_KICKER_RE = re.compile(r'(?i)^(?:kapitel|chapter)\b\.?')


def toc_gruppen(items, teil3_a=None):
    """Gliederung aus den geparsten Kapiteln ableiten (nicht hart verdrahtet).

    Rueckgabe: Liste von Gruppen [{'kicker', 'titel', 'idx', 'eintraege':
    [(kapitelindex, kicker, titel), …]}, …] — eine Gruppe je Teiler-Kicker
    (PART_KICKER) sowie fuer Auftakt und Schlusswort; ohne Auftakt eroeffnet
    das erste Kapitel die Gruppe selbst. inhalt_page() ruft es selbst.
    """
    grp, cur = [], None
    for i, it in enumerate(items):
        k = it.get('kicker') or ''
        if k in PART_KICKER or k in _GRUPPEN_KICKER:
            cur = {'kicker': k, 'titel': it['title'], 'idx': i, 'eintraege': []}
            grp.append(cur)
        elif cur is None:
            # Kein Kapitel traegt 'Auftakt', und PART_KICKER ist leer (Transit,
            # EA, Themen-Analyse: dort heisst das erste Kapitel z. B.
            # 'Zur Lesart'). Ohne diesen Zweig blieb `cur` bis zum Schlusswort
            # None und JEDES Kapitel davor fiel lautlos aus dem Verzeichnis —
            # das Inhaltsverzeichnis zeigte dann nur das Schlusswort
            # (gefunden 2026-09-07, Prueflauf Transit). Das erste
            # Kapitel oeffnet die Gruppe also selbst; das ist genau die
            # 'schlichte Kapitelliste', die das Design-Modul beschreibt.
            cur = {'kicker': k, 'titel': it['title'], 'idx': i, 'eintraege': []}
            grp.append(cur)
        else:
            # Kicker-Schreibweise ist im Klartext-Standard „KAPITEL 7"
            # (Versalien) — case-sensitiv gestrippt blieb frueher der ganze
            # Kicker in der 0,72 cm schmalen Nummernspalte stehen.
            nr = _NUMMERN_KICKER_RE.sub('', k).strip()
            titel = it['title']
            if nr and not re.fullmatch(r'[\dIVXivx]+\.?', nr):
                # Ein WORT-Kicker (Rechenschaft, Hauptthemen, Konfliktfelder,
                # Lebensaufgaben) passt nicht in die 0,72 cm schmale
                # Nummernspalte — er lief dort in die Titelspalte hinein.
                # Er wandert deshalb vor den Titel; die Nummernspalte bleibt
                # leer. Numerische Kicker bleiben, wo sie waren.
                titel = f'{nr} — {titel}'
                nr = ''
            cur['eintraege'].append({'nr': nr, 'titel': titel, 'idx': i})
    for g in grp:
        if g['kicker'] != 'Teil III':
            continue
        # Nur noch ZWEI Bloecke. Der dritte („C — Die acht Quartale", erkannt
        # an re.match(r'^Q\d ', titel)) war seit dem 2026-09-03 toter Code:
        # Die acht Quartalskapitel sind vollstaendig durch die
        # Zeitleisten-Seite ersetzt, ein aktuelles Dokument kann kein solches
        # Kapitel mehr tragen. Sichtbar wurde das nie, weil inhalt_page()
        # leere Bloecke ueberspringt — es stand eine Struktur im Code und ein
        # Label, das eine abgeschaffte Gliederung behauptete (Pruefbericht EA
        # 2026-09-08, 4.7). Entfernt am 2026-09-08.
        a, b = [], []
        for e in g['eintraege']:
            if _ist_jetzt(e['titel'], teil3_a):
                a.append(e)
            else:
                b.append(e)
        g['bloecke'] = [('A — Wo du jetzt stehst', a),
                        ('B — Die langen Linien', b)]
    return grp


def _toc_rows(eintraege, seiten):
    out = []
    for e in eintraege:
        p = seiten.get(f"CH_{e['idx']}", '')
        out.append(f'<tr><td class="tn">{e["nr"]}</td>'
                   f'<td class="tt">{esc(e["titel"])}</td>'
                   f'<td class="tp">{p}</td></tr>')
    return '<table class="toct">' + ''.join(out) + '</table>'


def inhalt_page(items, seiten, kopf, vorne=(), hinten=(), ornament='',
                teil3_a=None):
    """Inhaltsverzeichnis-Seite (Pflicht bei JEDEM Chart, direkt nach dem
    Deckblatt). `teil3_a` s. _ist_jetzt().

    kopf  die Kickerzeile ueber „Inhalt" — ein STRING, etwa
          f'Horoskop für {VORNAME}'. Seit 2026-09-19 (W61, G34-17d Nr. 7)
          geprueft: Anderes bricht mit einer Meldung ab, die sagt, was gemeint
          ist.
    """
    if not isinstance(kopf, str):
        raise TypeError(
            'inhalt_page(): kopf ist die Kickerzeile ueber "Inhalt" und muss ein '
            f'String sein, bekommen: {type(kopf).__name__}. Beispiel: '
            'chartdoc.inhalt_page(items, SEITEN, "Horoskop für <Vorname>", '
            'vorne=[...], ornament=ORNAMENT). Liegt das Deckblatt-dict aus '
            'build.lies_deckblatt() vor: den Kicker-Text als String setzen, '
            'nicht das dict uebergeben.')

    def zeile(titel, pid, klasse='toc-grp', unter=''):
        p = seiten.get(pid, '')
        us = f' <span class="gs">{esc(unter)}</span>' if unter else ''
        return (f'<div class="{klasse}">{esc(titel)}{us}'
                f'<span style="float:right;font-family:\'EB Garamond\';'
                f'font-size:8pt;color:{C.stone}">{p}</span></div>')

    def liste(eintraege):
        return '<table class="toct">' + ''.join(
            f'<tr><td class="tn"></td><td class="tt">{esc(t)}</td>'
            f'<td class="tp">{seiten.get(pid, "")}</td></tr>'
            for t, pid in eintraege) + '</table>'

    # Bloecke erst sammeln, dann NACH SEITENZAHL sortiert setzen.
    # Grund (2026-09-07, Prueflauf Transit): `hinten` wurde immer zuletzt
    # gerendert, auch wenn seine Seite vor den Kapitelgruppen liegt. Die
    # Zeitleisten-Seite steht beim Transit hinter dem Sammelkapitel, aber VOR
    # dem Schlusswort — und stand im Verzeichnis trotzdem darunter. Ein
    # Inhaltsverzeichnis, dessen Seitenzahlen nicht monoton steigen, ist
    # kaputt, egal aus welchem Block die Zeile kommt. Die Sortierung ist
    # stabil und im ersten Durchlauf (noch keine Seitenzahlen bekannt)
    # wirkungslos — die Reihenfolge ist dann exakt die frueher gesetzte.
    def _seite_von(anker):
        try:
            return int(seiten.get(anker) or 0) or 10 ** 6
        except (TypeError, ValueError):
            return 10 ** 6

    bloecke = []            # (anker, titel, untertitel, innerer HTML-Block)
    for titel, eintraege in vorne:
        anker = eintraege[0][1] if eintraege else ''
        bloecke.append((anker, titel, '', liste(eintraege) if eintraege else ''))

    for g in toc_gruppen(items, teil3_a):
        if 'bloecke' in g:
            inner = ''.join(f'<div class="toc-sub">{esc(lab)}</div>'
                            + _toc_rows(eintraege, seiten)
                            for lab, eintraege in g['bloecke'] if eintraege)
        else:
            inner = (_toc_rows(g['eintraege'], seiten) if g['eintraege'] else '')
        bloecke.append((f"CH_{g['idx']}", g['kicker'], g['titel'], inner))

    for titel, eintraege in hinten:
        anker = eintraege[0][1] if eintraege else ''
        bloecke.append((anker, titel, '', liste(eintraege) if eintraege else ''))

    bloecke.sort(key=lambda x: _seite_von(x[0]))

    b = []
    zeilen = 0
    for i, (anker, titel, unter, inner) in enumerate(bloecke):
        b.append(zeile(titel, anker, 'toc-grp' + (' first' if i == 0 else ''),
                       unter=unter))
        zeilen += 1
        if inner:
            b.append(inner)
            zeilen += inner.count('<tr') + inner.count('toc-sub')

    cls = 'toc weit' if zeilen <= TOC_WEIT_MAX else 'toc'
    orn = f'<div class="toc-orn">{esc(ornament)}</div>' if ornament else ''
    return f"""<section class="inhalt" id="PG_inhalt">
<div class="fm-kicker">{esc(kopf)}</div>
<h2 class="fm-title">{esc(INHALT_TITEL)}</h2>
<div class="fm-rule"></div>
<div class="{cls}">{''.join(b)}</div>
{orn}
</section>"""


# --- Zwei-Pass-Render mit echten Seitenzahlen -------------------------------

def seiten_aus_doc(doc):
    """id -> gedruckte Seitenzahl fuer alle Anker (PG_* und CH_*)."""
    out = {}
    for pi, page in enumerate(doc.pages, 1):
        for bx in build._walk(page._page_box):
            el = getattr(bx, 'element', None)
            if el is not None and hasattr(el, 'get'):
                iid = el.get('id')
                if iid and (iid.startswith('PG_') or iid.startswith('CH_')):
                    out.setdefault(iid, pi)
    return out


def render_mit_inhalt(build_html, out_pfad, items, colon_pairs, seiten_dict,
                      required_fields=None, doctype=None, extra_must=(),
                      max_pass=3, verbose=True):
    """Zwei-Pass-Render mit ECHTEN Seitenzahlen im Inhaltsverzeichnis.

    build_html(breaks) -> vollstaendiges Dokument-HTML; seiten_dict ist das
    SEITEN-dict des Builders und wird hier gefuellt. Vorher laufen die drei
    harten Gegenproben pruefe_kapitelkopf(), pruefe_kapitelfuss() und
    pruefe_orbis_zeile(). Rueckgabe: (doc, seiten) — das WeasyPrint-Document
    des letzten Passes und {anker: seitenzahl} fuer alle PG_*- und
    CH_*-Anker (seiten_aus_doc()). Das PDF liegt unter out_pfad. Wirft
    RuntimeError, wenn die Seitenzahlen nach max_pass Durchlaeufen nicht
    stabil sind. (Rueckgabe dokumentiert 2026-09-20, D3.)
    """
    must = [(b['text'], f"{it['kicker']} Block {j}")
            for it in items for j, b in enumerate(it['blocks'])
            if b['type'] in ('p', 'li')]
    # Die Signatur steht seit dem 2026-09-05 im Kapitelfuss. Sie hier in die
    # Volltext-Probe zu haengen kostet nichts und faengt den Fall ab, dass ein
    # Fuss zwar gebaut, aber der falschen Quelle entnommen wurde.
    must += [(it['signatur'], f"{it.get('kicker') or 'Kapitel'} Signatur")
             for it in items if (it.get('signatur') or '').strip()]
    must += list(extra_must)
    # Vor dem ersten Render: sitzt der Fuss ueberhaupt im Dokument? Ein
    # vergessener build_fuss()-Aufruf in der Kapitel-Schleife wuerde sonst
    # Signatur und Beleg lautlos aus dem ganzen Horoskop entfernen.
    pruefe_kapitelkopf(items)
    _erstes_html = build_html(set())
    pruefe_kapitelfuss(_erstes_html, items)
    pruefe_orbis_zeile(_erstes_html)
    letzte = None
    for runde in range(1, max_pass + 1):
        doc, breaks, unfix = build.render_sentence_safe(
            build_html, out_pfad, colon_pairs=colon_pairs,
            required_fields=required_fields, must_contain=must,
            verbose=False, doctype=doctype)
        neu = seiten_aus_doc(doc)
        fertig = (neu == letzte)
        if verbose:
            print(f'  Pass {runde}: {len(doc.pages)} Seiten, {len(breaks)} '
                  f'Satz-Umbrueche, {len(unfix)} unfixbar'
                  + (' — Seitenzahlen stabil' if fertig else ''))
        if unfix and verbose:
            print('  !! unfixbare Umbrueche:', unfix)
        if fertig:
            return doc, neu
        letzte = neu
        seiten_dict.clear()
        seiten_dict.update({k: str(v) for k, v in neu.items()})
    raise RuntimeError('Die Seitenzahlen im Inhaltsverzeichnis konvergieren '
                       'nicht — Layout pruefen, nicht die Zahlen von Hand '
                       'eintragen.')


def _selbsttest():
    """Selbsttest ohne Render (neu 2026-09-19): lies_zeitleiste(),
    zeitleiste_page() mit Marke (W12) und die kopf-Pruefung von inhalt_page()
    (W61). Konstruierter Block — keine echten Daten."""
    block = '\n'.join([
        '# Datenblatt (konstruiert)',
        'Sprachfassung: der @@ZEITLEISTE-Block steht am Ende.',
        '@@DECKBLATT',
        'LEITSATZ: Ein Satz.',
        '@@ENDE',
        '@@ZEITLEISTE',
        'LEAD: Eine hohe Zahl heisst nicht, dass viel passiert.',
        'Der progressive Mond wechselt im dritten Quartal das Zeichen.',
        'Q1 | dicht=1,2 | marke=',
        'Q2 | dicht= | marke=',
        'Q3 | dicht=2, 3 | marke=Exaktdatum · Konstruierter Befund <A&B>',
        '@@ENDE'])
    zl = lies_zeitleiste(block, titel={1: 'Erstes Thema', 2: 'Zweites Thema',
                                       3: 'Drittes Thema'})
    assert zl['lead'].startswith('Eine hohe Zahl') and 'Mond' in zl['lead']
    assert [q['quartal'] for q in zl['quartale']] == ['Q1', 'Q2', 'Q3']
    assert zl['quartale'][1]['dicht'] == [] and zl['quartale'][2]['dicht'] == [2, 3]
    assert zl['quartale'][2]['marke'] == 'Exaktdatum · Konstruierter Befund <A&B>'
    assert zl['quartale'][0]['ruht_titel'] == ['Drittes Thema']
    assert zl['quartale'][1]['dicht_titel'] == []
    fehlfaelle = [
        ('# ohne Block\nkein @@ZEITLEISTE hier\n', 'fehlt'),
        (block.replace('LEAD:', 'VORSPANN:'), 'unbekanntes Feld "VORSPANN:"'),
        (block.replace('| marke=\n', '| farbe=rot\n', 1), 'unbekanntes Feld "farbe="'),
        (block.replace('Q3 |', 'Q4 |'), 'lueckenlos'),
        (block.replace('dicht=1,2', 'dicht=Erstes Thema'), 'Kapitelnummern'),
        (block.replace('@@ENDE', '').replace('@@DECKBLATT', ''),
         'ohne abschliessende'),
        ('/gibt/es/nicht_Transit_chart_data.md', 'Datei nicht gefunden'),
        (block.replace('Q2 |', 'Q2 dicht'), 'unbekannte Zeile'),
    ]
    for text, erwartet in fehlfaelle:
        try:
            lies_zeitleiste(text)
        except ZeitleisteError as e:
            assert erwartet in str(e), (erwartet, str(e))
        else:
            raise AssertionError('kein Fehler fuer: ' + erwartet)
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='_chart_data.md',
                                     encoding='utf-8', delete=False) as fh:
        fh.write(block)
    try:
        assert lies_zeitleiste(fh.name)['quartale'] == [
            {k: v for k, v in q.items() if not k.endswith('_titel')}
            for q in zl['quartale']]
    finally:
        os.unlink(fh.name)
    try:
        lies_zeitleiste(block, titel={1: 'Erstes Thema'})
        raise AssertionError('Kapitelnummer ohne Kapitel nicht erkannt')
    except ZeitleisteError as e:
        assert 'die es nicht gibt' in str(e), e
    zeilen = [(q['quartal'], 'Monat–Monat 00', q['dicht_titel'], q['ruht_titel'],
               'M1 1 (0)', q['marke']) for q in zl['quartale']]
    seite = zeitleiste_page(zeilen, lead=zl['lead'])
    assert seite.count('class="zl-marke"') == 1
    assert '· <span class="zl-marke">Exaktdatum · Konstruierter Befund ' \
           '&lt;A&amp;B&gt;</span>' in seite
    assert 'nichts im Wirkorb' in seite
    assert esc(ZL_SPALTE) in seite.split('anh-note')[1], 'Spaltensatz fehlt'
    alt = zeitleiste_page([z[:5] for z in zeilen])      # 5 Felder, Vorgabe-LEAD
    assert 'zl-marke' not in alt.split('<tbody>')[1]
    assert esc(ZL_SPALTE) not in alt.split('anh-note')[1]
    assert ZL_SPALTE in ZL_LEAD
    try:
        zeitleiste_page([('Q1', 'x', [], [])])
        raise AssertionError('Zeile mit vier Feldern nicht erkannt')
    except ValueError as e:
        assert 'Felder' in str(e), e
    try:
        inhalt_page([], {}, {'LEITSATZ': 'x'})
        raise AssertionError('kopf als dict nicht erkannt')
    except TypeError as e:
        assert 'Kickerzeile' in str(e) and 'String' in str(e), e
    # 2026-09-19 (W2): Die Orbspalte der Aspektseite rundet genau einmal mit
    # build.orb_text() — auch wenn ein Chart-Builder ein anderes gr setzt.
    # 0.4917° ist 0°30′; die alte Doppelrundung (0.49°) ergab 0°29′.
    asp = [{'a': 'Sonne', 'b': 'Mond', 'name': 'Trigon', 'orb': 0.4917,
            'strength': 'voll', 'color': 'blau'}]
    vorher = _CFG['gr']
    try:
        konfiguriere(gr=lambda x: 'FALSCH')
        seite = aspekt_page(asp)
    finally:
        _CFG['gr'] = vorher
    assert '0°30′' in seite and '0°29′' not in seite and 'FALSCH' not in seite
    assert gr(0.4917) == '0°30′' and gr(29.9999) == '30°00′'
    print('[chartdoc-Selbsttest bestanden: lies_zeitleiste(), Marke der '
          'Zeitleiste (W12), kopf-Pruefung von inhalt_page() (W61), '
          'Orb der Aspektseite (W2)]')


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
    if _hilfe_cli():          # python3 chartdoc.py --hilfe [<name>]
        raise SystemExit(0)
    _selbsttest()
