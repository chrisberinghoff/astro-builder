#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REFERENZ: schlanker Chart-Builder fuer das Geburtshoroskop.

Diese Vorlage traegt NUR, was ein Typ ohne Zeitebene braucht:

    1. PALETTE             die Farbwerte, abgeleitet aus DECKBLATT['PALETTE']
    2. COVER_CSS + cover_svg()/cover_html()
                           das Titelmotiv aus DECKBLATT['TITELMOTIV']
    3. KONST / ACHSEN      die Chartdaten (kommen aus chartdata.py)
    4. ANALYSE / CHARTDATA / OUT / RADPNG / DOCTYPE

Der Transit nimmt `REFERENZ_Chart_Builder_Transit.py` (Transit-Uhr,
Zeitleisten-Seite, Anhangtabellen).

Alles andere — Struktur-CSS, Inhaltsverzeichnis, Radseite, Konstellationsseite,
Aspektseite, Kapitel-Sektionen (`chartdoc.build_section()`: Kopf, Koerper,
Fuss mit Signatur/Beleg), satzsicherer Umbruch, Zwei-Pass-Seitenzahlen,
Einmessung „passt auf eine Seite" — kommt aus chartdoc und wird NICHT neu
geschrieben. Schnittstellen ohne Quelltext-Lektuere: `chartdoc.hilfe()`,
`build.hilfe()`, `radix.hilfe()`.

FUENF DINGE, DIE HIER BEWUSST SO STEHEN:
  * LEITSATZ, LEITACHSE, TITELMOTIV, PALETTE und GLYPHEN werden GELESEN, nicht
    abgetippt: `build.lies_deckblatt()` holt sie aus dem @@DECKBLATT-Block am
    Ende der chart_data.md. Fehlt der Block, bricht der Lauf ab.
  * Die Vorlage liefert MECHANIK, nie Inhalt. Palette und Cover-Verlauf sind
    PLATZHALTER mit sichtbarer Marke (PALETTE_GESETZT): Solange die Marke
    steht, laeuft der Builder nicht — so rendert kein Lauf still die Farben
    eines anderen Charts.
  * Der Builder ZEICHNET SEIN RAD SELBST, bei jedem Lauf (rad_zeichnen). Ein
    PNG, das vom letzten Direktaufruf herumliegt, rendert still einen alten
    Datenstand.
  * Radbreite, Aspektskala UND die Skala der Konstellationsseite werden
    EINGEMESSEN, nicht gesetzt — und zwar am FRONTMATTER allein
    (`nur_frontmatter=True`): Cover, Inhalt und Chartbild-Strecke ohne die
    Kapitel. Die gemessenen Seiten liegen vor den Kapiteln, ihr Umbruch
    haengt nicht an ihnen; jeder Messrender ist damit vier Seiten statt
    vierzig. Die Breitenleiter beginnt bei 15,6 cm.
  * Die Seitenfolge hinter dem Cover ist fest: Inhalt, Radix, Konstellationen,
    Aspekte, dann die Kapitel. Beim Geburtshoroskop gibt es keine
    Teiler-Kapitel (PART_KICKER leer) und keine typ-eigenen Grafikseiten.

ENGLISCHE FASSUNG (seit 2026-09-26): SPRACHE = 'en' setzen, SIGNATUR_EN
fuellen (je Kapitel die Signatur, deutsch -> englisch) und, wo der Beleg nicht
mechanisch uebersetzbar ist, BELEG_EN. Alle Seitenlabels, Verzeichnis,
Fussnoten, Namen auf Konstellations- und Aspektseite sowie Signatur und Beleg
stehen dann englisch; die analyse.md behaelt Signatur und Beleg deutsch.
Fehlt eine Uebersetzung, bricht der Render ab und nennt alle fehlenden
(chartdoc.pruefe_sprachfassung). Verfahren: Modul Sprachfassung.

Aufruf:  python3 <klient>_builder.py
Geprueft wird beim Rendern automatisch: build.PFLICHT_BAUSTEINE fuer DOCTYPE.
"""
import html
import sys

sys.path.insert(0, '/home/claude')
import build                                   # noqa: E402
import radix                                   # noqa: E402
import chartdata as cd                         # noqa: E402
import chartdoc                                # noqa: E402

KLIENT = '<Vollstaendiger Name aus der H1 der analyse.md>'
VORNAME = '<Vorname>'
CHARTDATA = '/home/claude/<klient>_chart_data.md'
ANALYSE = '/home/claude/<klient>_analyse.md'
RADPNG = '<klient>_radix.png'
OUT = '/home/claude/<klient>_Geburtshoroskop.pdf'
DOCTYPE = None            # Geburtshoroskop: None (build.PFLICHT_BAUSTEINE)
GEBURTSZEILE = '<T. MONAT JJJJ · HH:MM ZONE · ORT>'   # Cover, letzte Zeile — Tag ohne fuehrende Null, Monat und Ort in VERSALIEN, Ort ohne Land, Zonenkuerzel wie in der Quelle (MEZ, MESZ, GMT …); englisch Monat englisch, '<D> <MONTH> <YYYY> · …'
# Sprache des PDFs (2026-09-26): 'de' oder 'en' (Modul Sprachfassung). Bei 'en'
# SIGNATUR_EN fuellen — Schluessel ist die deutsche Signatur der analyse.md,
# Wert die englische; BELEG_EN nur fuer einen Beleg, den die mechanische
# Uebersetzung nicht schafft (typisch der Getriebe-Beleg), Schluessel ist der
# GANZE deutsche Beleg des Kapitels.
SPRACHE = 'de'
SIGNATUR_EN = {}
BELEG_EN = {}

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

from build import BASE_CSS                     # noqa: E402

# --- Cover-Bestellung: gelesen, nie abgetippt ------------------------------
# Der @@DECKBLATT-Block steht am ENDE der chart_data.md, direkt hinter dem
# @@SELEKTOR-Block — NICHT in der analyse.md. lies_deckblatt() wirft, wenn er
# fehlt oder unvollstaendig ist (Design-Render-Modul, Abschnitt „Deckblatt").
DECKBLATT = build.lies_deckblatt(CHARTDATA)
LEITSATZ = DECKBLATT['LEITSATZ']
LEITACHSE = DECKBLATT['LEITACHSE']
TITELMOTIV = DECKBLATT['TITELMOTIV']
PALETTE_VORGABE = DECKBLATT['PALETTE']      # steuert die Farbwahl unten
ORNAMENT = DECKBLATT['GLYPHEN']             # Inhaltsverzeichnis

PART_KICKER = set()       # Geburtshoroskop: keine Teiler-Kapitel
OPEN_PAGE = {'Auftakt', 'Prelude'}   # eigene Seite; das Schlusswort bewusst NICHT

# Breitenleiter fuer die Einmessung der Radseite: 15,6 cm abwaerts in
# 0,2-cm-Schritten.
BREITEN = ['%.1fcm' % (x / 10) for x in range(156, 118, -2)]

# --- Palette ---------------------------------------------------------------
# Die Werte werden je Chart aus PALETTE_VORGABE abgeleitet (Grundstimmung aus
# den dominanten Elementen). Was hier steht, sind PLATZHALTER, damit die
# Vorlage uebersetzbar bleibt — nicht uebernehmen. Sind Palette UND die
# Verlaufsstopps in COVER_CSS gesetzt, PALETTE_GESETZT auf True stellen;
# vorher bricht der Builder unten mit einer Meldung ab.
# Schon eingemessene Werte hier eintragen, dann misst __main__ nicht noch
# einmal (None = messen).
RAD_BREITE = None         # cm, Radseite
ASPEKT_SKALA = None       # Schriftstufe der Aspektseite
KONST_SKALA = None        # Skala der Konstellationsseite
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
# TITELMOTIV gesetzt, leer = kein Sternfeld. Nie in den Textbereich des Covers
# (x 120–475, y 74–240) legen; cover_stars() filtert das ab.
STERNE = []


def cover_stars():
    """Sternfeld aus STERNE — nie im Textbereich des Covers."""
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


def cover_html(kicker):
    """Das Cover. `kicker` ist der DOKUMENTTYP AUS DER H1 der analyse.md
    (parsed['doctype']) in Versalien — kein Feld des @@DECKBLATT-Blocks;
    einen beschreibenden Untertitel und eine zweite Typzeile hat das Cover
    nicht. Hoehen im 842-Raster: 88 Kicker,
    112 Name, 168 Linie, 788 Leitsatz, 822 Geburtsdaten. 788 ist die LETZTE
    Leitsatzzeile: Ein langer Leitsatz wird am Gedankenstrich umbrochen und
    waechst nach oben (chartdoc.leitsatz_block())."""
    return f"""<section class="{'cover hell' if COVER_HELL else 'cover'}">
{_cover_grund()}
<div class="cv-block cv-kicker" style="top:{y2cm(88):.2f}cm">{esc(kicker)}</div>
<div class="cv-block cv-name" style="top:{y2cm(112):.2f}cm">{VORNAME.upper()}</div>
<div class="cv-block" style="top:{y2cm(168):.2f}cm"><div class="cv-rule"></div></div>
{chartdoc.leitsatz_block(LEITSATZ)}
<div class="cv-block cv-birth" style="top:{y2cm(822):.2f}cm">{esc(GEBURTSZEILE)}</div>
</section>"""


# ===========================================================================
# Chartbild-Strecke — die Seiten baut chartdoc, hier stehen nur die Daten
# ===========================================================================

ASPEKTE = cd.aspektliste()   # -> radix.aspektliste(...), s. chartdata.py
chartdoc.setze_zusatzaspekte(ASPEKTE)

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
        if n not in _BY:
            raise SystemExit(f'konst_zeilen(): Faktor {n!r} fehlt in chartdata.factors '
                             '— der chartdata.py-Vertrag (Datenblatt-Modul) verlangt '
                             'ihn; in Schritt 3 melden, nicht ueberspringen.')
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


def chartbild(rad_breite, skala, konst_skala=1.0):
    zeilen = konst_zeilen()
    return (chartdoc.radix_page(RADPNG, RAD_NOTE, bild_breite=rad_breite)
            + chartdoc.konstellationen_page(zeilen, achsen_zeilen(),
                                            ELEMENTE, MODI, note=konst_note(zeilen),
                                            fussnoten=KONST_FUSSNOTEN,
                                            skala=konst_skala)
            + chartdoc.aspekt_page(ASPEKTE, skala=skala))


# ===========================================================================
# Zusammenbau
# ===========================================================================

parsed = build.parse_analyse(ANALYSE, client=KLIENT)
items = build.prepare_chapters(parsed)
colon_pairs = build.make_colon_pairs(items)
KICKER = parsed['doctype'].upper()          # Cover-Kickerzeile = Dokumenttyp der H1

# Titel aus chartdoc (folgen SPRACHE); deutsch: Das Chartbild, Die Radix, …
TOC_VORNE = [(chartdoc.CHARTBILD_TITEL, [
    (chartdoc.RADIX_TITEL, 'PG_rad'),
    (chartdoc.KONST_TITEL, 'PG_konst'),
    (chartdoc.ASPEKT_TITEL, 'PG_asp')])]

# Seitenzahlen fuers Inhaltsverzeichnis: erster Durchlauf leer, danach aus dem
# gerenderten Dokument gefuellt (chartdoc.render_mit_inhalt).
SEITEN = {}


def build_html(breaks=(), skala=1.0, rad_breite=None, konst_skala=1.0,
               nur_frontmatter=False):
    """Das ganze Dokument — oder mit nur_frontmatter=True nur Cover, Inhalt und
    Chartbild-Strecke (fuer die Einmessung; s. Docstring der Datei)."""
    # lang= folgt SPRACHE: die Silbentrennung laeuft nach den Mustern der
    # Sprache des Dokuments.
    parts = [f'<!doctype html><html lang="{SPRACHE}"><head><meta charset="utf-8">'
             '<style>', BASE_CSS, chartdoc.struktur_css(), COVER_CSS,
             '</style></head><body>',
             cover_html(KICKER),
             chartdoc.inhalt_page(items, SEITEN,
                                  chartdoc.INHALT_KOPF.format(name=VORNAME),
                                  vorne=TOC_VORNE, ornament=ORNAMENT),
             chartbild(rad_breite, skala, konst_skala)]
    if not nur_frontmatter:
        # Kapitel-Sektionen: Kopf, Koerper (build_bloecke) und Fuss mit
        # Signatur/Beleg (build_fuss) in EINEM Aufruf. Fehlt der Fuss, bricht
        # render_mit_inhalt() hart ab (chartdoc.pruefe_kapitelfuss).
        for i, it in enumerate(items):
            parts.append(chartdoc.build_section(i, it, breaks,
                                                part_kicker=PART_KICKER,
                                                open_page=OPEN_PAGE,
                                                erstes=(i == 0)))
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

    # 1. Rad (und ein Vollbild-Cover) IMMER selbst zeichnen — nie ein
    #    herumliegendes PNG benutzen.
    rad_zeichnen()
    if COVER_BILD:
        cover_bild_rechnen()

    # 2. Einmessen statt schaetzen — am Frontmatter allein (s. Docstring der
    #    Datei): groesste Breite/Schriftstufe, bei der die Seite einseitig bleibt.
    def frontmatter(**kw):
        return build_html(nur_frontmatter=True, **kw)

    #    Hat der Lauf schon eingemessen, werden die Werte oben gesetzt und
    #    hier NICHT neu gemessen.
    rad = RAD_BREITE if RAD_BREITE is not None else chartdoc.passe_ein(
        lambda w: frontmatter(rad_breite=w), 'PG_rad', BREITEN, was='Radseite')
    skala = ASPEKT_SKALA if ASPEKT_SKALA is not None else \
        chartdoc.passe_aspektseite_ein(
            lambda s: frontmatter(skala=s, rad_breite=rad), ASPEKTE)
    kskala = KONST_SKALA if KONST_SKALA is not None else chartdoc.passe_ein(
        lambda ks: frontmatter(skala=skala, rad_breite=rad, konst_skala=ks),
        'PG_konst', chartdoc.KONST_STUFEN, was='Konstellationsseite')

    # 3. Satzsicher rendern, Seitenzahlen im Inhalt aus dem echten Dokument.
    doc, seiten = chartdoc.render_mit_inhalt(
        lambda breaks: build_html(breaks, skala, rad, kskala),
        OUT, items, colon_pairs, SEITEN,
        required_fields={'Leitsatz': LEITSATZ, 'Titelmotiv': TITELMOTIV},
        # Die ERSTE Zeile (Design-Render, „Durchsetzung") — mehrzeilig gesetzt
        # steht der ganze Leitsatz im HTML nirgends am Stueck.
        extra_must=[(LEITSATZ.split(" — ")[0].split("\n")[0], 'Leitsatz aufs Cover')],
        doctype=DOCTYPE)
    print('Aspektzeilen:', len(ASPEKTE), '| Kapitel:', len(items),
          '| Seiten:', len(doc.pages))
    print('Inhalt:', seiten.get('PG_inhalt'), '| Rad:', seiten.get('PG_rad'),
          '| Konstellationen:', seiten.get('PG_konst'),
          '| Aspekte:', seiten.get('PG_asp'))
