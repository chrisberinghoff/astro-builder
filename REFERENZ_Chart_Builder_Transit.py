#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REFERENZ: Chart-Builder fuer das Transit-Horoskop (Transit-Uhr, Zeitleiste,
Anhang). Das Geburtshoroskop nimmt `REFERENZ_Chart_Builder_Geburtshoroskop.py`.
Die chart-unabhaengige Mechanik UND die Chartbild-Seiten stecken in
`claude/chartdoc.py`; hier steht nur, was sich je Chart wirklich aendert:

    1. PALETTE           die Farbwerte oben (RAD_PALETTE = Radfarben), abgeleitet
                         aus DECKBLATT['PALETTE']
    2. COVER_CSS + cover_svg()/cover_stars()/cover_html()
                         das individuelle Titelmotiv aus DECKBLATT['TITELMOTIV']
    3. KONST / ACHSEN    die Chartdaten (kommen aus chartdata.py)
    4. ANALYSE / CHARTDATA / OUT / RADPNG / UHRPNG
    5. tdat.setze_quelle(...) auf die chart_data,
                         die Zeitleisten-Seite (vor dem Schlusswort) und die
                         beiden Anhangtabellen

Alles andere — Struktur-CSS, Inhaltsverzeichnis, Radseite, Konstellationsseite,
Aspektseite, Transit-Uhr-Seite, Kapitelkopf und Kapitelfuss mit Signatur/Beleg,
satzsicherer Umbruch, Zwei-Pass-Seitenzahlen, Einmessung „passt auf eine Seite"
— kommt aus chartdoc und wird NICHT neu geschrieben.

SECHS DINGE, DIE HIER BEWUSST SO STEHEN:
  * LEITSATZ, LEITACHSE, TITELMOTIV, PALETTE und GLYPHEN werden GELESEN, nicht
    abgetippt: `build.lies_deckblatt()` holt sie aus dem @@DECKBLATT-Block am
    Ende der chart_data.md. Fehlt der Block, bricht der Lauf ab.
  * Der Builder ZEICHNET SEINE GRAFIKEN SELBST, bei jedem Lauf (rad_zeichnen,
    uhr_zeichnen). Ein PNG, das vom letzten Direktaufruf herumliegt, rendert
    still einen alten Datenstand.
  * Radbreite, Uhrbreite, Aspektskala UND die Skala der Konstellationsseite
    werden EINGEMESSEN, nicht gesetzt — am FRONTMATTER allein
    (build_html(nur_frontmatter=True): Cover, Inhalt, Chartbild-Strecke, dazu
    die Zeitleiste). Die gemessenen Seiten liegen vor den Kapiteln, ihr
    Umbruch haengt nicht an ihnen; ein Messrender ist damit fuenf Seiten
    statt fuenfzig. Die Breitenleiter beginnt bei 15,6 cm.
  * Palette, Cover-Verlauf und Sternfeld sind PLATZHALTER mit sichtbarer Marke
    (PALETTE_GESETZT, STERNE): Solange die Marke steht, laeuft der Builder
    nicht — so schleppt niemand die Farben eines anderen Charts mit.
  * Die Seitenfolge hinter dem Cover ist fest: Inhalt, Radix, Konstellationen,
    Aspekte, Transit-Uhr.
  * Die Kapitel-Schleife baut den Koerper NICHT selbst: ihn liefert
    `chartdoc.build_bloecke(i, it, breaks, allow_drop)`, das Zwischentitel und
    Folgeabsatz aneinander bindet — `break-after: avoid` wirkt in WeasyPrint
    nicht. Danach ruft sie `chartdoc.build_fuss(it)`: Signatur und Beleg
    rendern am KAPITELENDE. Fehlt der Aufruf, bricht render_mit_inhalt() hart
    ab — sonst verschwaenden Signatur und Beleg lautlos aus dem Dokument.

ENGLISCHE FASSUNG (seit 2026-09-26): SPRACHE = 'en' setzen, SIGNATUR_EN
fuellen (je Kapitel die Signatur, deutsch -> englisch) und, wo der Beleg nicht
mechanisch uebersetzbar ist, BELEG_EN. Seitenlabels, Verzeichnis, Uhr,
Zeitleiste, Anhang, Fussnoten, Namen und Daten sowie Signatur und Beleg stehen
dann englisch; die analyse.md behaelt Signatur und Beleg deutsch. Die
Kapitelkicker duerfen deutsch oder englisch sein (Zur Lesart / On Reading
This, Kapitel n / Chapter n, Schlusswort / Closing Word). Verfahren: Modul
Sprachfassung.

Aufruf:  python3 <klient>_builder.py
Geprueft wird beim Rendern automatisch: build.PFLICHT_BAUSTEINE fuer den
uebergebenen doctype (hier 'transit').
"""
import html
import re
import sys

sys.path.insert(0, '/home/claude')
import build                                   # noqa: E402
import radix                                   # noqa: E402
import chartdata as cd                         # noqa: E402
import chartdoc                                # noqa: E402
import transitdata as tdat                     # noqa: E402
import transituhr_fusion as tuhr               # noqa: E402

KLIENT = '<Vollstaendiger Name aus der H1 der analyse.md>'
VORNAME = '<Vorname>'
CHARTDATA = '/home/claude/<klient>_Transit_chart_data.md'
ANALYSE = '/home/claude/<klient>_Transit_analyse.md'
RADPNG = '<klient>_radix.png'
UHRPNG = '<klient>_transituhr.png'
OUT = '/home/claude/<klient>_Transit_Horoskop.pdf'

# Geburtsmoment fuer die Fussnoten der Konstellationsseite (Zeichengrenze,
# Hauswechsel) — aus dem KOPF der chart_data uebernommen,
# nicht gerechnet: JD in UT mit mindestens fuenf Nachkommastellen, Breite und
# Laenge in Dezimalgrad. Solange einer fehlt, bricht der Builder mit Meldung ab.
JD_GEBURT = None          # <<JD (UT) aus dem Kopf der chart_data>>
LAT, LON = None, None     # <<Breite, Laenge aus dem Kopf der chart_data>>
# Weitere Fussnoten der Konstellationsseite mit Wortlaut AUS DEM DATENBLATT
# (unaspektierter Faktor, Strukturbild §4) — je Satz ein Eintrag; in einer
# englischen Fassung der Satz englisch (von Hand, sinngleich).
FUSSNOTEN_EXTRA = []
# Geburtszeile des Covers — Platzhalter mit Abbruch in __main__.
GEBURTSZEILE = '<T. MONAT JJJJ · HH:MM ZONE · ORT>'   # Tag ohne fuehrende Null, Monat und Ort in VERSALIEN, Ort ohne Land, Zonenkuerzel wie in der Quelle (MEZ, MESZ, GMT …); englisch Monat englisch, '<D> <MONTH> <YYYY> · …'
# Sprache des PDFs (2026-09-26): 'de' oder 'en' (Modul Sprachfassung). Bei 'en'
# SIGNATUR_EN fuellen — Schluessel ist die deutsche Signatur der analyse.md,
# Wert die englische; BELEG_EN nur fuer einen Beleg, den die mechanische
# Uebersetzung nicht schafft, Schluessel ist der GANZE deutsche Beleg.
SPRACHE = 'de'
SIGNATUR_EN = {}
BELEG_EN = {}

tdat.setze_quelle(CHARTDATA)
from build import BASE_CSS                     # noqa: E402

# --- Cover-Bestellung: gelesen, nie abgetippt ------------------------------
# Der @@DECKBLATT-Block steht am ENDE der chart_data.md, direkt hinter dem
# @@SELEKTOR-Block — NICHT in der analyse.md. lies_deckblatt() wirft, wenn er
# fehlt oder unvollstaendig ist; nur so kann kein Lauf still ein eigenes Motiv
# erfinden. Einzelheiten im Design-Render-Modul, Abschnitt „Woher Leitsatz und
# Motiv kommen".
DECKBLATT = build.lies_deckblatt(CHARTDATA)
LEITSATZ = DECKBLATT['LEITSATZ']
LEITACHSE = DECKBLATT['LEITACHSE']
TITELMOTIV = DECKBLATT['TITELMOTIV']
PALETTE_VORGABE = DECKBLATT['PALETTE']      # steuert die Farbwahl unten
ORNAMENT = DECKBLATT['GLYPHEN']             # Teiler-Seiten + Inhaltsverzeichnis

PART_KICKER = set()       # Transit: keine Teiler-Kapitel
# Eigene Seite (kein Teiler-Layout); das Schlusswort bewusst NICHT. Der
# Auftakt des Transits heisst `Zur Lesart` (englisch `On Reading This`).
OPEN_PAGE = {'Zur Lesart', 'On Reading This'}
# Vor dem Schlusswort steht die Zeitleiste (Design-Zeitebene-Modul).
SCHLUSS_KICKER = ('Schlusswort', 'Closing Word')

# Breitenleiter fuer die Einmessung von Radseite und Transit-Uhr: 15,6 cm
# abwaerts in 0,2-cm-Schritten.
BREITEN = ['%.1fcm' % (x / 10) for x in range(156, 118, -2)]

# --- Palette ---------------------------------------------------------------
# Die Werte kommen aus PALETTE_VORGABE (Grundstimmung aus den dominanten
# Elementen). Hier stehen Platzhalter — je Chart neu setzen, nicht uebernehmen.
# Sind Palette UND die Verlaufsstopps in COVER_CSS gesetzt, PALETTE_GESETZT
# auf True stellen; vorher bricht der Builder im __main__ mit einer Meldung ab.
PALETTE_GESETZT = False   # <<auf True setzen, sobald NIGHT … BELEG_BD und .cv-sky aus PALETTE_VORGABE abgeleitet sind>>
NIGHT = '#0a1a26'
PETROL = '#1d4a53'
PETROL_L = '#3d6b72'
DEEP = '#123540'
GOLD = '#a37c37'
GOLD_L = '#c9a45e'
STONE = '#7a6a52'
PAPER = '#f8f4ec'          # = radix.DEFAULT_PALETTE['grund'], nicht aendern
INK = '#241f1a'
BELEG_BG = '#f1ebda'
BELEG_BD = '#cbb07a'

# Radfarben: Hausstil-Standard aus radix.DEFAULT_PALETTE, nur Tinte und Ring an
# die Dokumentfarben angeglichen. Wer hier eingreift, muss `aspektfarben` in
# chartdoc.konfiguriere mitgeben — sonst zeigt die Legende eine andere Farbe
# als das Rad.
RAD_PALETTE = dict(radix.DEFAULT_PALETTE)
RAD_PALETTE.update({'ink': INK, 'ring': '#9c9384'})

PAL = {'night': NIGHT, 'petrol': PETROL, 'petrol_l': PETROL_L, 'deep': DEEP,
       'gold': GOLD, 'gold_l': GOLD_L, 'stone': STONE, 'paper': PAPER,
       'ink': INK, 'beleg_bg': BELEG_BG, 'beleg_bd': BELEG_BD}
GLYPH_OF = {f['name']: f['glyph'] for f in cd.factors}
GLYPH_OF.update({'Suedknoten': '☋'})

# sprache= VOR tdat.parse() weiter unten: parse() baut die Monatsspannen der
# Zeitleiste beim Lesen, in der Sprache, die dann gilt.
chartdoc.konfiguriere(pal=PAL, part_kicker=PART_KICKER, glyphen=GLYPH_OF,
                      gr=cd.gr, name_of=cd.name_of, kopfzeile=VORNAME.upper(),
                      aspektfarben=RAD_PALETTE, part_ornament=ORNAMENT,
                      sprache=SPRACHE, signaturen_en=SIGNATUR_EN,
                      belege_en=BELEG_EN)
esc = chartdoc.esc

COVER_CSS = f"""
/* ---------- Cover ---------- */
section.cover {{ page: cover; position:relative; width:21cm; height:29.7cm;
                 overflow:hidden; }}
.cv-sky {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm;
  background: linear-gradient(to bottom, /* PLATZHALTER — Verlauf aus PALETTE_VORGABE, je Chart neu */
     #06121c 0%, #123340 33%, #35605c 62%, #f0d9a6 100%); }}
.cv-art {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm; }}
.cv-star {{ position:absolute; border-radius:50%; background:#eaf1f5; }}
.cv-block {{ position:absolute; left:0; right:0; text-align:center; }}
.cv-kicker {{ font-family:"EB Garamond"; font-size:8.2pt; letter-spacing:0.42em;
   color:{GOLD_L}; }}
.cv-name {{ font-family:"Cinzel"; font-size:31pt; letter-spacing:0.15em;
   color:#f2ead6; }}
.cv-rule {{ width:3.2cm; height:1pt; background:{GOLD_L}; margin:0 auto; }}
/* Leitsatz und Geburtszeile: Farben fuer HELLEN unteren Rand; dunkles Motiv
   -> COVER_HELL = True (Klasse .hell unten) */
.cv-leit {{ font-family:"EB Garamond Italic"; font-style:italic; font-size:15.4pt;
   color:#4a3512; letter-spacing:0.02em; }}
.cv-birth {{ font-family:"EB Garamond"; font-size:8.6pt; letter-spacing:0.2em;
   color:#6b5220; }}
.cv-bild {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm; }}
section.cover.hell .cv-leit {{ color:#f3ead6; }}
section.cover.hell .cv-birth {{ color:#e3d3ae; }}
.cv-gl {{ position:absolute; font-family:"DejaVu Sans","FreeSerif",sans-serif;
   text-align:center; }}
"""

DESIGN_CSS = chartdoc.struktur_css() + COVER_CSS


# ===========================================================================
# Cover — das Motiv setzt TITELMOTIV um, nichts anderes
#
# Render-sichere Bausteine (Einzelheiten im Design-Modul, Abschnitt
# „Render-Sicherheit"):
#   * KEINE SVG-Verlaeufe — Flaechen als Vollton, Verlaeufe per CSS auf <div>
#     oder als Stapel schmaler Vollton-Streifen.
#   * Soll eine Flaeche nach AUSSEN dunkler werden, in SENKRECHTE Scheiben
#     zerlegen und nach horizontalem Abstand faerben.
#   * Randabblendung ueber die FARBE (Richtung Hintergrundton), nicht ueber
#     fill-opacity — 1-px-Scheiben mit Alpha zeigen senkrechte Naehte.
#   * Kurven per Catmull-Rom in kubische Bezierpfade; weiche Hoefe aus vielen
#     flachen Stufen, nicht aus drei kraeftigen.
#   * KEIN <svg><text> — Glyphen als absolut positionierte HTML-Spans darueber.
# ===========================================================================

def _mix(stops, t):
    """Farbe auf einer Stuetzstellenleiter interpolieren (Vollton-Verlaeufe)."""
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        if p0 <= t <= p1:
            f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
            r, g, b = (round(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
            return f'#{r:02x}{g:02x}{b:02x}'
    c = stops[-1][1]
    return f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}'


def _nach(hexfarbe, ziel, f):
    """Farbe anteilig auf `ziel` ziehen — deckend statt halbtransparent."""
    r = int(hexfarbe[1:3], 16); g = int(hexfarbe[3:5], 16)
    b = int(hexfarbe[5:7], 16)
    r = round(r + (ziel[0] - r) * f)
    g = round(g + (ziel[1] - g) * f)
    b = round(b + (ziel[2] - b) * f)
    return f'#{r:02x}{g:02x}{b:02x}'


def _catmull_pfad(pts, zyklisch=False):
    """Stuetzpunkte als glatten kubischen Bezierpfad (Catmull-Rom)."""
    n = len(pts)

    def q(i):
        return pts[i % n] if zyklisch else pts[max(0, min(n - 1, i))]

    d = [f'M {pts[0][0]:.1f},{pts[0][1]:.1f}']
    for i in range(n if zyklisch else n - 1):
        p0, p1, p2, p3 = q(i - 1), q(i), q(i + 1), q(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f'C {c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} '
                 f'{p2[0]:.1f},{p2[1]:.1f}')
    if zyklisch:
        d.append('Z')
    return ' '.join(d)


def cover_svg():
    """Das Titelmotiv. Je Chart neu gebaut — hier steht nur das Geruest."""
    p = ['<svg class="cv-art" viewBox="0 0 595 842" preserveAspectRatio="none" '
         'xmlns="http://www.w3.org/2000/svg">']
    # … Vollton-Flaechen, Scheibenverlaeufe, Bezierkurven nach TITELMOTIV …
    return '\n'.join(p) + '</svg>'


# Sternfeld: (x, y, radius, deckung) im 595x842-Raster — je Chart aus dem
# TITELMOTIV gesetzt, leer = kein Sternfeld.
STERNE = []


def cover_stars():
    """Sternfeld aus STERNE — nie in den Textbereich des Covers (x 120–475, y 74–240)."""
    pts = [q for q in STERNE if not (120 <= q[0] <= 475 and 74 <= q[1] <= 240)]
    out = []
    for x, y, r, o in pts:
        out.append(f'<div class="cv-star" style="left:{x/595*21:.3f}cm;'
                   f'top:{y/842*29.7:.3f}cm;width:{r*2/595*21:.3f}cm;'
                   f'height:{r*2/595*21:.3f}cm;opacity:{o}"></div>')
    return ''.join(out)


def y2cm(y):
    return y / 842 * 29.7


# VOLLBILD-COVER. Rechnet der Lauf das Titelmotiv als ganzseitiges PNG
# (Design-Render-Modul, „Eine Flaeche, die von MEHREREN Seiten abblendet"),
# setzt er COVER_BILD auf den Pfad und schreibt die Rechnung in
# cover_bild_rechnen(); __main__ ruft sie bei jedem Lauf, wie rad_zeichnen().
# cover_html() legt das PNG an die Stelle von .cv-sky, Sternfeld und SVG.
# COVER_HELL schaltet Leitsatz und Geburtszeile auf helle Schrift: Die Farben in
# COVER_CSS sind fuer einen HELLEN unteren Rand gesetzt; auf einem dunklen
# Motiv verschwinden sie, und kein Preflight sieht das.
COVER_BILD = None      # <<Pfad des im Lauf gerechneten Vollbild-PNG — oder None>>
COVER_HELL = False     # True: dunkles Motiv am unteren Rand, Leitsatz und Geburtszeile hell


def cover_bild_rechnen():
    """Rechnet das Vollbild-PNG nach TITELMOTIV und schreibt es nach COVER_BILD.
    Je Chart neu — hier steht nur die Schnittstelle. __main__ ruft sie, sobald
    COVER_BILD gesetzt ist; ein herumliegendes PNG ist nicht vertrauenswuerdig."""
    raise SystemExit('REFERENZ-Vorlage: COVER_BILD ist gesetzt, aber '
                     'cover_bild_rechnen() rechnet noch nichts.')


def _cover_grund():
    """Hintergrund des Covers: das gerechnete Vollbild oder Verlauf, Sterne, SVG."""
    if COVER_BILD:
        import base64
        with open(COVER_BILD, 'rb') as f:
            daten = base64.b64encode(f.read()).decode('ascii')
        return '<img class="cv-bild" src="data:image/png;base64,%s">' % daten
    return '<div class="cv-sky"></div>\n%s\n%s' % (cover_stars(), cover_svg())


def glyphe(x, y, size, color, zeichen, op=0.9):
    """Eine tragende Glyphe aus DECKBLATT['GLYPHEN'], dezent ueber dem SVG."""
    return (f'<div class="cv-gl" style="left:{(x-40)/595*21:.3f}cm;'
            f'width:{80/595*21:.3f}cm;top:{y2cm(y):.2f}cm;font-size:{size}pt;'
            f'color:{color};opacity:{op}">{zeichen}</div>')


def cover_html():
    # Die Kickerzeile traegt eine sichtbare Marke statt eines Vorgabewerts: Dort
    # steht der DOKUMENTTYP AUS DER H1 DER analyse.md (Design-Render-Modul,
    # „Deckblatt") — im laufenden Chart `parsed['doctype']`, in Versalien;
    # KEIN Feld des @@DECKBLATT-Blocks. Einen Untertitel und eine zweite
    # Typzeile hat das Cover nicht. Hoehen im 842-Raster: 88 Kicker, 112 Name,
    # 168 Linie, 788 Leitsatz, 822 Geburtsdaten. 788 ist die LETZTE
    # Leitsatzzeile: chartdoc.leitsatz_block() bricht am Gedankenstrich um
    # und laesst einen langen Leitsatz nach oben wachsen.
    return f"""<section class="{'cover hell' if COVER_HELL else 'cover'}">
{_cover_grund()}
<div class="cv-block cv-kicker" style="top:{y2cm(88):.2f}cm">&lt;&lt;KICKER — Dokumenttyp aus der H1 der analyse.md (parsed['doctype']), in VERSALIEN; KEIN Feld des @@DECKBLATT-Blocks&gt;&gt;</div>
<div class="cv-block cv-name" style="top:{y2cm(112):.2f}cm">{VORNAME.upper()}</div>
<div class="cv-block" style="top:{y2cm(168):.2f}cm"><div class="cv-rule"></div></div>
{chartdoc.leitsatz_block(LEITSATZ)}
<div class="cv-block cv-birth" style="top:{y2cm(822):.2f}cm">{esc(GEBURTSZEILE)}</div>
</section>"""


# ===========================================================================
# Chartbild-Strecke — die Seiten baut chartdoc, hier stehen nur die Daten
# ===========================================================================

ASPEKTE = cd.aspektliste()   # -> radix.aspektliste(...), s. chartdata.py
TD = tdat.parse()

# Die Themennamen der Uhr sind die TITEL DER THEMENKAPITEL des laufenden
# Charts — erfundene Namen sind ein Fehler. tuhr.THEMEN ist im Repo mit
# Platzhaltern vorbelegt und MUSS hier ueberschrieben werden.
# Eine Zielliste als fuenftes Feld braucht ein Eintrag, sobald ein Transiter
# zwei Themenkapitel traegt oder ein Thema mehrere Transiter an verschiedenen
# Zielen hat — Formen s. tuhr._passt() ('Mond', 'Quadrat Sonne', 'Saturn Mond',
# 'Saturn Quadrat Mond'); jede Zeile geht in das ERSTE passende Thema.
tuhr.THEMEN = [
    ('<Titel Themenkapitel>', '<Untertitel>', ['<Transiter>'], '#7d3b46',
     ['<Ziel>', '<Ziel>']),
    ('<Titel Themenkapitel>', '<Untertitel>', ['<Transiter>'], '#6b5c48'),
]

REIHENFOLGE = ['Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'Jupiter', 'Saturn',
               'Uranus', 'Neptun', 'Pluto', 'SEP', 'Mondknoten', 'Suedknoten',
               'Chiron', 'Lilith', 'Pholus', 'Glueckspunkt']
KLASSISCH = ['Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'Jupiter', 'Saturn',
             'Uranus', 'Neptun', 'Pluto']
_BY = {f['name']: f for f in cd.factors}
# Namenstoleranz: beide Schreibweisen fuehren auf denselben Faktor. Der
# Glueckspunkt ist ausgemustert und steht nur in alten Datenblaettern.
for _a, _b in (('Suedknoten', 'Südknoten'), ('Glueckspunkt', 'Glückspunkt')):
    if _a in _BY and _b not in _BY:
        _BY[_b] = _BY[_a]
    elif _b in _BY and _a not in _BY:
        _BY[_a] = _BY[_b]

# Datum und Zone wie GEBURTSZEILE (Tag ohne fuehrende Null), hier in Normalschrift.
RAD_NOTE = {
    'de': (f'{VORNAME} · <T. Monat JJJJ, HH:MM ZONE> · <Ort> · '
           'Häuser nach Koch · wahrer Mondknoten · wahre Lilith · Aspekte '
           'nach Huber-Orbis'),
    'en': (f'{VORNAME} · <D Month YYYY, HH:MM ZONE> · <Place> · '
           'Koch houses · true lunar node · true Lilith · aspects by '
           'Huber orbs')}[SPRACHE]
KONST_NOTE = {
    'de': ('Doppelte Hausangabe: Der Faktor steht bis 5° vor der nächsten '
           'Hausspitze und wird in beiden Häusern gedeutet — das führende '
           'Haus steht vorn.'),
    'en': ('Double house entry: the factor stands up to 5° before the next '
           'house cusp and is read in both houses — the leading house comes '
           'first.')}[SPRACHE]


def konst_note(zeilen):
    """KONST_NOTE nur, wenn die Haus-Spalte eine Doppelangabe traegt (`8/9`), sonst
    None — Design-Render-Modul, Konstellationsseite."""
    return KONST_NOTE if any('/' in str(z[4]) for z in zeilen if z[0] != 'SEP') else None


def rad_zeichnen():
    """Radix-Rad. Kein `title=` — die Bildunterschrift steht als RAD_NOTE im
    Dokument und laeuft damit in EB Garamond statt in matplotlibs Groteske."""
    return radix.radix(cd.factors, cd.CUSPS, cd.ASC, cd.MC,
                       out_path='/home/claude/' + RADPNG,
                       aspects=ASPEKTE, palette=RAD_PALETTE)


def uhr_zeichnen():
    """Transit-Uhr in der Themenfassung."""
    return tuhr.bauen('/home/claude/' + UHRPNG, TD)


def konst_zeilen():
    out = []
    for n in REIHENFOLGE:
        if n == 'SEP':
            out.append(('SEP', '', '', '', '', ''))
            continue
        if n == 'Suedknoten':
            # Der Suedknoten ist der Mondknoten um 180 Grad — beide Enden der
            # Achse laufen gleich; der Lauf wird ABGELEITET, nie gesetzt.
            out.append(('☋', 'Südknoten', cd.sign_name(cd.SUEDKNOTEN),
                        cd.gr(cd.SUEDKNOTEN % 30), cd.haus(cd.SUEDKNOTEN),
                        'rückläufig' if _BY['Mondknoten']['retro'] else 'direkt'))
            continue
        if n == 'Glueckspunkt' and n not in _BY:
            # Ausgemustert; nur ein altes Datenblatt traegt ihn noch — dann
            # rendert er wie bisher (Design-Render-Modul, Konstellationsseite).
            continue
        f = _BY[n]
        lauf = 'rückläufig' if f['retro'] else 'direkt'
        if n == 'Glueckspunkt':
            lauf = '—'                       # gerechneter Punkt, Altbestand
        # Glyphenregel wie in chartdoc._fac(): ueber die ZEICHENLAENGE — ein
        # Feld von mehr als einem Zeichen ist ein Name, kein Symbol.
        glyph = '' if len(f['glyph']) > 1 else f['glyph']
        # NICHT `cd.name_of(n)` — `n` ist der Name der REIHENFOLGE-Liste;
        # `f['name']` traegt den Vertragsnamen. Einen ASCII-Namen in der
        # Tabelle sehen verify(), Pflicht-Bausteine und Preflight nicht.
        out.append((glyph, cd.name_of(f['name']), cd.sign_name(f['lon']),
                    cd.gr(f['lon'] % 30), cd.haus(f['lon']), lauf))
    return out


def achsen_zeilen():
    return [(k, lab, cd.sign_name(lo), cd.gr(lo % 30))
            for k, lab, lo in cd.ACHSEN]


ELEMENTE, MODI = chartdoc.verteilung(
    [(cd.name_of(_BY[n]['name']), _BY[n]['lon']) for n in KLASSISCH])

# Daten ueber tdat.datum_lang(): deutsch TT.MM.JJJJ, englisch „1 Mar 2030".
UHR_STICHTAG = tdat.datum_lang(TD['fenster']['stichtag'])
UHR_NOTE = {
    'de': (f"Fenster {tdat.datum_lang(TD['fenster']['start'])} bis "
           f"{tdat.datum_lang(TD['fenster']['ende'])} — acht "
           f"Kalenderquartale ab dem Quartal des Stichtags · Rückblick ab "
           f"{tdat.datum_lang(TD['fenster']['rueckblick'])} · "
           f"Wirk-Orb 1,5° · Snapshot-Orb 3,0°"),
    'en': (f"Window {tdat.datum_lang(TD['fenster']['start'])} to "
           f"{tdat.datum_lang(TD['fenster']['ende'])} — eight calendar "
           f"quarters from the quarter of the reference date · look-back from "
           f"{tdat.datum_lang(TD['fenster']['rueckblick'])} · "
           f"working orb 1.5° · snapshot orb 3.0°")}[SPRACHE]

# Dreiteiliger Vorspann der Uhr. chartdoc.uhr_lead() liefert eine einteilige
# Fassung; die Themenuhr braucht mehr Erklaerung, darum hier ausgeschrieben.
# Blasse Zeilen stehen in der Uhr, WEIL ein Kapitel sie zu seiner Figur zaehlt.
UHR_LEAD = [
    'Jede Zeile ist eine lange Linie: ein Planet, der gerade am Himmel läuft, '
    'berührt über Wochen oder Monate hinweg eine Stelle deines Geburtsbildes. '
    'Die Linien stehen nicht einzeln nebeneinander, sondern in Themenblöcken — '
    'jeder Block trägt oben den Namen, unter dem der Text ihn später behandelt, '
    'und darunter einen dicken Bogen über die gesamte Laufzeit des Themas. So '
    'liest man erst die großen Zeiten und geht dann ins Einzelne.',

    'Die Beschriftung am Zeilenanfang nennt beide Seiten in dieser Reihenfolge '
    '— zuerst den laufenden Planeten, dann den Winkel, den er bildet, dann die '
    'Stelle deines Geburtsbildes, die er trifft. Der Balken rechts daneben '
    'zeigt, wann das geschieht: blass die volle Berührungszeit, kräftig die '
    'Strecke, in der die Linie wirklich arbeitet, und die kleinen weißen '
    'Punkte die einzelnen Tage, an denen der Winkel exakt steht. Blass '
    'gesetzte Zeilen — wo es sie gibt — sind Nebenlinien: Sie berühren keinen '
    'der Punkte, die dieses Dokument durchgehend verfolgt, und stehen hier, '
    'weil das Kapitel ihres Blocks von ihnen erzählt.',

    f'Die acht Quartale sind Kalenderquartale; Q1 ist das Quartal, in dem '
    f'dieses Horoskop entstanden ist. Was links der senkrechten Marke liegt, '
    f'lief schon vor dem {UHR_STICHTAG}. Unter der Zeitachse stehen als '
    f'farbige Punkte die Stationen: die Tage, an denen ein langsamer Planet '
    f'die Richtung wechselt. Sie erklären, warum dieselbe Linie oft zwei- oder '
    f'dreimal exakt wird statt nur einmal.']
if SPRACHE == 'en':
    UHR_LEAD = [
        'Each line is a long line: a planet moving in the sky now touches a '
        'point of your birth chart over weeks or months. The lines do not '
        'stand side by side one by one but in theme blocks — each block '
        'carries at the top the name under which the text later deals with '
        'it, and beneath it a thick arc over the whole running time of the '
        'theme. So one reads the large periods first and then goes into '
        'detail.',

        'The label at the start of each line names both sides in this order '
        '— first the moving planet, then the angle it forms, then the point '
        'of your birth chart that it meets. The bar beside it shows when this '
        'happens: pale for the full time of contact, strong for the stretch '
        'in which the line is really at work, and the small white dots for '
        'the single days on which the angle is exact. Lines set in pale type '
        '— where there are any — are side lines: they touch none of the '
        'points this document follows throughout, and they stand here because '
        'the chapter of their block tells of them.',

        f'The eight quarters are calendar quarters; Q1 is the quarter in '
        f'which this horoscope was drawn up. Whatever lies to the left of the '
        f'vertical mark was already running before {UHR_STICHTAG}. Below the '
        f'time axis, the coloured dots are the stations: the days on which a '
        f'slow planet changes direction. They explain why the same line is '
        f'often exact two or three times instead of once.']


# --- Fussnoten der Konstellationsseite --------------------------------------
# Die beiden Geburtszeit-Saetze (Zeichengrenze, Hauswechsel) kommen fertig aus
# radix.konstellations_fussnoten(); die Funktion setzt den Ephemeridenpfad
# selbst und bricht ab, statt einen Satz still wegzulassen. lade.ephemeriden()
# holt pyswisseph und die Dateien, wenn sie fehlen — im frischen Container bis
# zu zehn Minuten, darum den Builder im Hintergrund starten. Vorn stehen die
# Saetze aus dem Datenblatt.
def konst_fussnoten():
    if None in (JD_GEBURT, LAT, LON):
        raise SystemExit('JD_GEBURT, LAT und LON aus dem Kopf der chart_data '
                         'eintragen (Fussnoten der Konstellationsseite).')
    from lade import ephemeriden
    ephemeriden(still=True)
    return list(FUSSNOTEN_EXTRA) + radix.konstellations_fussnoten(
        JD_GEBURT, cd.factors, cd.CUSPS, LAT, LON, sprache=SPRACHE)


KONST_FUSSNOTEN = konst_fussnoten()


def chartbild(rad_breite, uhr_breite, skala, konst_skala=1.0):
    zeilen = konst_zeilen()
    return (chartdoc.radix_page(RADPNG, RAD_NOTE, bild_breite=rad_breite)
            + chartdoc.konstellationen_page(zeilen, achsen_zeilen(),
                                            ELEMENTE, MODI, note=konst_note(zeilen),
                                            fussnoten=KONST_FUSSNOTEN,
                                            skala=konst_skala)
            + chartdoc.aspekt_page(ASPEKTE, skala=skala)
            + chartdoc.transituhr_page(UHRPNG, UHR_STICHTAG, UHR_NOTE,
                                       lead=UHR_LEAD, bild_breite=uhr_breite))


# ===========================================================================
# Anhang — die beiden Pflichttabellen des Transits (chart-eigen)
# ===========================================================================

def dt(d, kurz=False):
    # 2026-09-26: ueber transitdata — deutsch TT.MM.JJ / TT.MM.JJJJ wie bisher,
    # englisch „14 Jun 27" / „14 Jun 2027"
    return tdat.datum_kurz(d) if kurz else tdat.datum_lang(d)


# Texte des Anhangs je Sprache (2026-09-26). Die deutschen Werte sind
# zeichengleich die bisherigen Wortlaute.
_ANH = {
    'de': {
        'lang_lead': ('Alle {n} Langläufer des Fensters mit\nSpanne, Dauer, '
                      'sämtlichen Exaktdaten und den Stationen des laufenden '
                      'Planeten.\nGrau gesetzt sind die sekundären Linien — sie '
                      'berühren keinen der primären\nZielpunkte; im Text kommen '
                      'sie nur vor, wo ein Kapitel sie zu seinem Thema zählt.'),
        'lang_kopf': ('Transit', 'Aspekt', 'Ziel', 'Spanne', 'Mon.', 'exakt',
                      'Stationen'),
        'lang_note': ('Dauer in Monaten über die volle Berührung\n(Snapshot-Orb '
                      '3,0°). Datumsangaben TT.MM.JJ. <span class="mk">←</span> '
                      'vor der\nSpanne heißt: die Linie lief schon vor Beginn des '
                      'Fensters; <span class="mk">→</span>\ndahinter: sie reicht '
                      'über das Fenster hinaus.'),
        'jetzt_lead': ('Die Momentaufnahme vom {datum}: was an diesem Tag\nan '
                       'deinem Geburtsbild arbeitet, mit Orb und Laufrichtung. '
                       'Zulaufend heißt, die\nBerührung wird enger; auslaufend, '
                       'sie löst sich — kann aber rückläufig\nzurückkehren.'),
        'stand': 'Transit-Stände', 'haus': 'Haus',
        'jetzt_kopf': ('Transit', 'Aspekt', 'Ziel', 'Orb', 'Richtung', 'exakt',
                       'bis'),
        'nachhall': 'Nachhall — kürzlich exakt',
        'anmarsch': 'Anmarsch — exakt in den nächsten 90 Tagen',
        'stationen': 'Stationen im Umfeld des Stichtags',
        'jetzt_note': ('Snapshot-Orb 3,0°; was im Wirk-Orb von 1,5° an einem '
                       'primären\nZiel steht, deuten die Themenkapitel oder '
                       'nennt das Kapitel „Mitlaufendes“.'),
        'kehrt': ', kehrt zurück', 'tage': '{n} Tage', 'komma': True},
    'en': {
        'lang_lead': ('All {n} long-running lines of the window with\ntheir '
                      'span, duration, every exact date and the stations of the '
                      'moving planet.\nSecondary lines are set in grey — they '
                      'touch none of the primary\ntarget points; the text '
                      'mentions them only where a chapter counts them as part '
                      'of its theme.'),
        'lang_kopf': ('Transit', 'Aspect', 'Target', 'Span', 'Mo.', 'exact',
                      'Stations'),
        'lang_note': ('Duration in months over the full contact\n(snapshot orb '
                      '3.0°). Dates as D Mon YY. <span class="mk">←</span> '
                      'before the\nspan means: the line was already running '
                      'before the window began; <span class="mk">→</span>\n'
                      'after it: it reaches beyond the window.'),
        'jetzt_lead': ('The snapshot of {datum}: what is at work on your birth '
                       'chart on this day,\nwith orb and direction. Applying '
                       'means the contact is\ntightening; separating, it is '
                       'loosening — but it can return\nin retrograde motion.'),
        'stand': 'Transit positions', 'haus': 'house',
        'jetzt_kopf': ('Transit', 'Aspect', 'Target', 'Orb', 'Direction',
                       'exact', 'until'),
        'nachhall': 'Echo — recently exact',
        'anmarsch': 'Approach — exact within the next 90 days',
        'stationen': 'Stations around the reference date',
        'jetzt_note': ('Snapshot orb 3.0°; whatever stands within the working '
                       'orb of 1.5° of a primary\ntarget is interpreted in the '
                       'theme chapters or named in the chapter “Also '
                       'Running”.'),
        'kehrt': ', returns', 'tage': '{n} days', 'komma': False},
}
ANH = _ANH[SPRACHE]


def _zahl(x):
    """Dezimalzahl in der Schreibweise der Sprache (deutsch mit Komma)."""
    return str(x).replace('.', ',') if ANH['komma'] else str(x)


# Der §11-Report ist ASCII: freie Textfelder (Transit-Staende,
# Stationen-Position, Ziel-Aufzaehlung) tragen 'Loewe' (in alten
# Datenblaettern auch 'Glueckspunkt'). ziel_label() greift dort nicht —
# darum hier einmal zurueckuebersetzen.
_UM = {'Loewe': 'Löwe', 'Schuetze': 'Schütze', 'Glueckspunkt': 'Glückspunkt',
       'Suedknoten': 'Südknoten'}


def um(s):
    # 2026-09-26: englisch zuerst Faktor- und Zeichennamen uebersetzen
    # (deutsch unveraendert), dann wie bisher die Umlaute
    s = tdat.anzeige_text(s)
    for a, b in _UM.items():
        s = s.replace(a, b)
    return s


def _stationen_aus(flags):
    return ', '.join(dt(tdat._d(x), True) for x in
                     re.findall(r'\d{4}-\d\d-\d\d', flags))


def anhang_langlaeufer():
    rows = []
    for r in sorted(TD['langlaeufer'],
                    key=lambda x: (not x['primaer'], -x['monate'])):
        st = _stationen_aus(r['flags'])
        # Kompakte Randmarken statt Klammertexten: sie hielten die
        # Spanne-Spalte sonst dreizeilig.
        vor = ('<span class="mk">←</span> '
               if 'laeuft schon' in r['flags'] else '')
        nach = (' <span class="mk">→</span>'
                if 'ueber das Fenster hinaus' in r['flags'] else '')
        trc = '' if r['primaer'] else ' class="sec"'
        mon = _zahl(r['monate'])
        exl = ', '.join(dt(x, True) for x in r['exakt'])
        rows.append(
            f'<tr{trc}>'
            f'<td class="tg">{tdat.GLYPH.get(r["transiter"], "")}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(r["transiter"]))}</td>'
            f'<td class="ta">{esc(tdat.aspekt_label(r["aspekt"]))}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(r["ziel"]))}</td>'
            f'<td class="ts">{vor}{dt(r["start"], True)} – '
            f'{dt(r["ende"], True)}{nach}</td>'
            f'<td class="td_">{mon}</td>'
            f'<td class="te">{exl}</td>'
            f'<td class="tst">{st}</td></tr>')
    k = ANH['lang_kopf']
    return f"""<section class="anhang" id="PG_anh1">
<div class="fm-kicker">{esc(chartdoc.ANHANG_KICKER)}</div>
<h2 class="fm-title">{esc(chartdoc.ANH_LANG_TITEL)}</h2>
<div class="fm-rule"></div>
<p class="fm-lead">{ANH['lang_lead'].format(n=len(TD['langlaeufer']))}</p>
<table class="anh">
<colgroup><col style="width:0.5cm"><col style="width:1.6cm">
<col style="width:1.5cm"><col style="width:1.55cm"><col style="width:2.85cm">
<col style="width:1.0cm"><col style="width:4.9cm"><col style="width:3.25cm">
</colgroup>
<thead><tr><th></th><th>{k[0]}</th><th>{k[1]}</th>
<th>{k[2]}</th><th>{k[3]}</th><th>{k[4]}</th><th>{k[5]}</th>
<th>{k[6]}</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<div class="anh-note">{ANH['lang_note']}</div>
</section>"""


def anhang_jetzt():
    f = TD['fenster']
    stand = ' · '.join(
        f'{tdat.GLYPH.get(x["planet"], "")} {um(x["planet"])} '
        f'{um(x["zeichen"])} {um(x["pos"])} ({ANH["haus"]} {x["haus"]})'
        for x in TD['stand'])
    rows = []
    for r in TD['im_orb']:
        # 2026-09-26: die Umformung steht in transitdata (deutsch unveraendert)
        ex = tdat.exakt_anzeige(r['exakt_txt'])
        richtung = (tdat.richtung_label(r['richtung'])
                    + (ANH['kehrt'] if r['kehrt'] else ''))
        trc = '' if r['primaer'] else ' class="sec"'
        orb = _zahl(r['orb'])
        bis = dt(tdat._d(r['bis']), True) if r['bis'] else ''
        rows.append(
            f'<tr{trc}>'
            f'<td class="tg">{tdat.GLYPH.get(r["transiter"], "")}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(r["transiter"]))}</td>'
            f'<td class="ta">{esc(tdat.aspekt_label(r["aspekt"]))}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(r["ziel"]))}</td>'
            f'<td class="tor">{orb}°</td>'
            f'<td class="tri">{esc(richtung)}</td>'
            f'<td class="te">{esc(ex)}</td>'
            f'<td class="tb">{bis}</td></tr>')

    def liste(key, titel):
        xs = TD[key]
        if not xs:
            return ''
        z = ''.join(
            f'<tr><td class="tg">{tdat.GLYPH.get(x["transiter"], "")}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(x["transiter"]))}</td>'
            f'<td class="ta">{esc(tdat.aspekt_label(x["aspekt"]))}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(x["ziel"]))}</td>'
            f'<td class="te">{dt(x["exakt"])}</td>'
            f'<td class="tri">{ANH["tage"].format(n=x["tage"])}</td></tr>'
            for x in xs)
        return (f'<div class="anh-sub">{titel}</div>'
                f'<table class="anh"><colgroup>'
                f'<col style="width:0.5cm"><col style="width:1.6cm">'
                f'<col style="width:1.6cm"><col style="width:1.55cm">'
                f'<col style="width:2.5cm"><col style="width:9.45cm">'
                f'</colgroup><tbody>{z}</tbody></table>')

    stat = ''.join(
        f'<tr><td class="ts">{dt(x["datum"])}</td>'
        f'<td class="tg">{tdat.GLYPH.get(x["planet"], "")}</td>'
        f'<td class="tz">{esc(um(x["planet"]))}</td>'
        f'<td class="tri">{esc(tdat.richtung_label(x["richtung"]))}</td>'
        f'<td class="tz">{esc(um(x["pos"]))}</td>'
        f'<td class="te">{esc(um(x["ziele"]))}</td></tr>'
        for x in TD['stationen'])

    k = ANH['jetzt_kopf']
    return f"""<section class="anhang flow" id="PG_anh2">
<div class="anh-kopf">
<div class="fm-kicker">{esc(chartdoc.ANHANG_KICKER)}</div>
<h2 class="fm-title">{esc(chartdoc.ANH_JETZT_TITEL)}</h2>
<div class="fm-rule"></div>
<p class="fm-lead">{ANH['jetzt_lead'].format(datum=dt(f['stichtag']))}</p>
<div class="anh-note" style="margin:0 0 0.4cm 0">{ANH['stand']}: {stand}</div>
</div>
<table class="anh">
<colgroup><col style="width:0.5cm"><col style="width:1.6cm">
<col style="width:1.6cm"><col style="width:1.55cm"><col style="width:1.1cm">
<col style="width:2.5cm"><col style="width:6.9cm"><col style="width:1.45cm">
</colgroup>
<thead><tr><th></th><th>{k[0]}</th><th>{k[1]}</th>
<th>{k[2]}</th><th>{k[3]}</th><th>{k[4]}</th><th>{k[5]}</th>
<th>{k[6]}</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
{liste('nachhall', ANH['nachhall'])}
{liste('anmarsch', ANH['anmarsch'])}
<div class="anh-sub">{ANH['stationen']}</div>
<table class="anh">
<colgroup><col style="width:1.45cm"><col style="width:0.5cm">
<col style="width:1.6cm"><col style="width:1.75cm"><col style="width:2.5cm">
<col style="width:9.4cm"></colgroup>
<tbody>{stat}</tbody></table>
<div class="anh-note">{ANH['jetzt_note']}</div>
</section>"""


# ===========================================================================
# Zusammenbau
# ===========================================================================

parsed = build.parse_analyse(ANALYSE, client=KLIENT)
items = build.prepare_chapters(parsed)
colon_pairs = build.make_colon_pairs(items)
ANHANG = anhang_langlaeufer() + anhang_jetzt()

# Zeitleisten-Seite (Design-Zeitebene-Modul): der @@ZEITLEISTE-Block der
# chart_data, gelesen mit chartdoc.lies_zeitleiste(titel=...) — Titel sind
# WORTGLEICH die Kapiteltitel.
# 2026-09-26: auch englische Nummernkicker (`Chapter n`)
TITEL = {int(it['kicker'].split()[1]): it['title'] for it in items
         if it.get('kicker', '').startswith(('Kapitel ', 'Chapter '))
         and it['kicker'].split()[1].isdigit()}
ZL = chartdoc.lies_zeitleiste(CHARTDATA, titel=TITEL)
ZL_ZEILEN = []
for _q, (_qq, _a, _b, _spanne) in zip(ZL['quartale'], TD['quartale']):
    assert _q['quartal'] == _qq, (_q['quartal'], _qq)
    ZL_ZEILEN.append((_qq, _spanne, _q['dicht_titel'], _q['ruht_titel'],
                      tdat.dichte_je_monat(TD, _a, _b), _q['marke']))


def zeitleiste(skala=1.0):
    return chartdoc.zeitleiste_page(ZL_ZEILEN, lead=ZL['lead'], skala=skala)


# Gruppentitel wie der Standardaufruf des Design-Moduls („Das Chartbild").
# Titel aus chartdoc (folgen SPRACHE); deutsch zeichengleich die bisherigen.
TOC_VORNE = [(chartdoc.CHARTBILD_TITEL, [
    (chartdoc.RADIX_TITEL, 'PG_rad'),
    (chartdoc.KONST_TITEL, 'PG_konst'),
    (chartdoc.ASPEKT_TITEL, 'PG_asp'),
    (chartdoc.UHR_TITEL_KURZ, 'PG_uhr')])]
TOC_HINTEN = [(chartdoc.ZEITLEISTE_KICKER,
               [(chartdoc.ZEITLEISTE_TITEL, 'PG_zeit')]),
              (chartdoc.ANHANG_KICKER, [
    (chartdoc.ANH_LANG_TITEL, 'PG_anh1'),
    (chartdoc.ANH_JETZT_TITEL, 'PG_anh2')])]

# Seitenzahlen fuers Inhaltsverzeichnis: erster Durchlauf leer, danach aus dem
# gerenderten Dokument gefuellt (chartdoc.render_mit_inhalt).
SEITEN = {}


def build_html(breaks=(), skala=1.0, uhr_breite=None, rad_breite=None,
               konst_skala=1.0, zl_skala=1.0, nur_frontmatter=False):
    """Das ganze Dokument — oder mit nur_frontmatter=True nur Cover, Inhalt,
    Chartbild-Strecke und Zeitleiste (fuer die Einmessung; s. Docstring der
    Datei)."""
    # lang= folgt SPRACHE: die Silbentrennung laeuft nach den Mustern der
    # Sprache des Dokuments.
    parts = [f'<!doctype html><html lang="{SPRACHE}"><head><meta charset="utf-8">'
             '<style>', BASE_CSS, chartdoc.struktur_css(), COVER_CSS,
             '</style></head><body>',
             cover_html(),
             chartdoc.inhalt_page(items, SEITEN,
                                  chartdoc.INHALT_KOPF.format(name=VORNAME),
                                  vorne=TOC_VORNE, hinten=TOC_HINTEN,
                                  ornament=ORNAMENT),
             chartbild(rad_breite, uhr_breite, skala, konst_skala)]
    if nur_frontmatter:
        parts.append(zeitleiste(zl_skala))
        parts.append('</body></html>')
        return '\n'.join(parts)
    first_chapter = True
    for i, it in enumerate(items):
        if it.get('kicker') in SCHLUSS_KICKER:
            # Die Zeitleiste steht hinten, vor Schlusswort und Anhang
            # (Design-Zeitebene-Modul, „Wo sie steht").
            parts.append(zeitleiste(zl_skala))
        is_part = it.get('kicker') in PART_KICKER
        allow_drop = not is_part
        cls = ['chapter']
        if is_part:
            cls.append('part')
        if first_chapter:
            cls.append('chapter-first')
            first_chapter = False
        elif it.get('kicker') in OPEN_PAGE:
            cls.append('chapter-first')
        head = (chartdoc.build_part_head(it) if is_part
                else chartdoc.build_head(it))
        # Den Kapitelkoerper baut chartdoc: build_bloecke() bindet Zwischentitel
        # und Folgeabsatz in einen `.subwrap`-Block (`break-after: avoid` wirkt
        # in WeasyPrint nicht). Signatur und Beleg rendern am KAPITELENDE;
        # build_fuss() gibt '' zurueck bei Teiler-Kapiteln und bei jedem
        # Kapitel ohne Signatur UND ohne Beleg — der Aufruf darf also unbedingt
        # stehen. Fehlt er, bricht render_mit_inhalt() hart ab
        # (chartdoc.pruefe_kapitelfuss).
        inner = (head + chartdoc.build_bloecke(i, it, breaks, allow_drop)
                 + chartdoc.build_fuss(it))
        if is_part:
            inner = f'<div class="part-inner">{inner}</div>'
        parts.append(f'<section class="{" ".join(cls)}" id="CH_{i}">'
                     f'{inner}</section>')
    if not any(it.get('kicker') in SCHLUSS_KICKER for it in items):
        parts.append(zeitleiste(zl_skala))     # Rueckfall: ohne Schlusswort vor den Anhang
    parts.append(ANHANG)
    parts.append('</body></html>')
    return '\n'.join(parts)


if __name__ == '__main__':
    if not PALETTE_GESETZT:
        raise SystemExit('REFERENZ-Vorlage: Palette und Cover-Verlauf sind noch '
                         'Platzhalter — aus DECKBLATT["PALETTE"] ableiten, dann '
                         'PALETTE_GESETZT = True setzen (Design-Render-Modul, '
                         '„Deckblatt": die Vorlage liefert Mechanik, nie Inhalt).')

    # GEBURTSZEILE und RAD_NOTE: Geprueft wird der Platzhalter selbst — seine
    # spitzen Klammern gingen sonst still ins PDF.
    for _n, _v in (('GEBURTSZEILE', GEBURTSZEILE), ('RAD_NOTE', RAD_NOTE)):
        if '<' in _v and '>' in _v:
            raise SystemExit('REFERENZ-Vorlage: %s traegt noch den Platzhalter '
                             '— Datum, Zeit und Ort aus der chart_data '
                             'eintragen.' % _n)

    # 1. Grafiken (und ein Vollbild-Cover) IMMER selbst zeichnen — nie ein
    #    herumliegendes PNG benutzen.
    rad_zeichnen()
    uhr_zeichnen()
    if COVER_BILD:
        cover_bild_rechnen()

    # 2. Einmessen statt schaetzen — am Frontmatter allein (s. Docstring der
    #    Datei): groesste Breite/Schriftstufe, bei der die Seite einseitig bleibt.
    def frontmatter(**kw):
        return build_html(nur_frontmatter=True, **kw)

    rad = chartdoc.passe_ein(lambda w: frontmatter(rad_breite=w), 'PG_rad',
                             BREITEN, was='Radseite')
    uhr = chartdoc.passe_ein(lambda w: frontmatter(uhr_breite=w, rad_breite=rad),
                             'PG_uhr', BREITEN, was='Transit-Uhr')
    skala = chartdoc.passe_aspektseite_ein(
        lambda s: frontmatter(skala=s, uhr_breite=uhr, rad_breite=rad), ASPEKTE)
    # Die Konstellationsseite wird ebenfalls eingemessen — ihr Inhalt waechst
    # je Chart.
    kskala = chartdoc.passe_ein(
        lambda ks: frontmatter(skala=skala, uhr_breite=uhr, rad_breite=rad,
                               konst_skala=ks),
        'PG_konst', chartdoc.KONST_STUFEN, was='Konstellationsseite')
    # Die Zeitleiste wird IMMER eingemessen — auch beim Standardfenster (acht
    # Quartale) passt sie nicht sicher bei 1,0.
    zl_skala = chartdoc.passe_ein(
        lambda zs: frontmatter(skala=skala, uhr_breite=uhr, rad_breite=rad,
                               konst_skala=kskala, zl_skala=zs),
        'PG_zeit', [1.0, .96, .92, .88, .84, .80], was='Zeitleiste')

    # 3. Satzsicher rendern, Seitenzahlen im Inhalt aus dem echten Dokument.
    doc, seiten = chartdoc.render_mit_inhalt(
        lambda breaks: build_html(breaks, skala, uhr, rad, kskala, zl_skala),
        OUT, items, colon_pairs, SEITEN,
        required_fields={'Leitsatz': LEITSATZ, 'Titelmotiv': TITELMOTIV},
        # Die ERSTE Zeile (Design-Render, „Durchsetzung") — mehrzeilig gesetzt
        # steht der ganze Leitsatz im HTML nirgends am Stueck.
        extra_must=[(LEITSATZ.split(" — ")[0].split("\n")[0], 'Leitsatz aufs Cover')],
        doctype='transit')
    print('Aspektzeilen:', len(ASPEKTE), '| Kapitel:', len(items),
          '| Langlaeufer:', len(TD['langlaeufer']),
          '| Jetzt-Kontakte:', len(TD['im_orb']))
    print('Inhalt:', seiten.get('PG_inhalt'), '| Rad:', seiten.get('PG_rad'),
          '| Konstellationen:', seiten.get('PG_konst'),
          '| Aspekte:', seiten.get('PG_asp'), '| Uhr:', seiten.get('PG_uhr'),
          '| Zeitleiste:', seiten.get('PG_zeit'),
          '| Anhang:', seiten.get('PG_anh1'), seiten.get('PG_anh2'))
