#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REFERENZ: Chart-Builder fuer das PDF des Beziehungshoroskops (neu 2026-10-11).

Das Beziehungshoroskop legt die Geburtsbilder zweier Menschen nebeneinander —
ein Paar, Elternteil und Kind oder (seit 2026-10-14) zwei Freunde; die Art
Freundschaft heisst „Freundschaftshoroskop“ (Erweiterung Beziehung,
`claude/Projektanweisung_Erweiterung_Beziehung.md`). Diese Vorlage traegt nur,
was der Typ braucht:

    1. PALETTE   Farbwerte, abgeleitet aus DECKBLATT['PALETTE']
    2. COVER     das Titelmotiv aus DECKBLATT['TITELMOTIV'] wie beim
                 Geburtshoroskop; Kicker (Dokumenttyp der H1), beide Vornamen,
                 Linie, Leitsatz und die Geburtszeile beider
    3. CHARTDATA / ANALYSE / OUT / DATUM / GEBURTSZEILE / RAD_NOTE

Die Seitenfolge hinter dem Cover ist fest: Inhalt, Doppelrad, Staende beider
Bilder, Verbindungen zwischen beiden (samt Orbis-Zeile; die Aspekt-Legende steht
beim Doppelrad, 2026-10-14b), dann die
Kapitel. Doppelrad, Staende- und Verbindungsseite baut beziehung.py aus dem
maschinenlesbaren Block des Datenblatts der Beziehung (lies_beziehung) —
gelesen, nie abgetippt; nichts wird aus Geburtsdaten neu gerechnet.
Inhaltsverzeichnis, Kapitel (chartdoc.build_section: Kopf, Koerper, Fuss mit
Signatur und Beleg), satzsicherer Umbruch, Zwei-Pass-Seitenzahlen und die
Datenschutz-Zeile der Inhaltsseite kommen aus chartdoc und werden NICHT neu
geschrieben. Schnittstellen ohne Quelltext-Lektuere: beziehung.hilfe(),
chartdoc.hilfe(), build.hilfe().

FUENF DINGE, DIE HIER BEWUSST SO STEHEN:
  * LEITSATZ, LEITACHSE, TITELMOTIV, PALETTE und GLYPHEN werden GELESEN, nicht
    abgetippt: build.lies_deckblatt() holt sie aus dem @@DECKBLATT-Block am
    Ende des Datenblatts der Beziehung. Fehlt der Block, bricht der Lauf ab.
  * Die Vorlage liefert MECHANIK, nie Inhalt. Palette und Cover-Verlauf sind
    PLATZHALTER mit sichtbarer Marke (PALETTE_GESETZT): Solange sie steht,
    laeuft der Builder nicht.
  * Der Builder ZEICHNET SEIN DOPPELRAD SELBST, bei jedem Lauf
    (beziehung.doppelrad). Ein herumliegendes PNG ist nicht vertrauenswuerdig.
  * Radbreite und die Skalen der Staende- und der Verbindungsseite werden
    EINGEMESSEN, am Frontmatter allein (nur_frontmatter=True).
  * Die Sollzahl fuer verify(): aspect_rows = ASPEKT_ZEILEN
    (len(R['kreuz']) + len(R['achsen'])), aspect_section =
    (beziehung.KREUZ_TITEL, <erster Kapiteltitel>) — auf der Teilmenge ohne
    Inhaltsseite (build.pruef_teilmenge).

DOCTYPE = 'beziehung' (build.PFLICHT_BAUSTEINE: Inhalt, Doppelrad, Staende
beider Bilder, Verbindungen zwischen beiden Bildern, Aspekt-Legende,
_doppelrad.png).

ENGLISCHE FASSUNG: SPRACHE = 'en', SIGNATUR_EN fuellen (je Kapitel die
Signatur, deutsch -> englisch). BELEG_EN baut beziehung.belege_en() aus der
analyse.md selbst (Vornamen und Ueberlagerung im Genitiv kennt die
mechanische Uebersetzung von chartdoc nicht); was es nicht schafft, meldet es
mit SprachfassungError — dann den Beleg von Hand in BELEG_HAND eintragen.
Verfahren: Modul Sprachfassung.

Aufruf:  python3 <a>_beziehung_builder.py
Geprueft wird beim Rendern automatisch: build.PFLICHT_BAUSTEINE fuer DOCTYPE.
"""
import os
import sys

sys.path.insert(0, '/home/claude')
import build                                   # noqa: E402
import radix                                   # noqa: E402
import chartdoc                                # noqa: E402
import beziehung                               # noqa: E402

A_VORNAME = '<Vorname der bestellenden Person>'
B_VORNAME = '<Vorname der zweiten Person>'
KLIENT = '<Name aus der H1 der analyse.md, z. B. „<A> und <B>“>'
DATUM = '<JJJJ-MM-TT>'    # das Datum im Namen der Dateien aus Chat 1 — PDF, Analyse und Datenblatt tragen dasselbe
# Namen der Dateien je Art und Sprache: beziehung.dateiname() — Kuerzel `Beziehung`, bei
# Freundschaft `Freundschaft`; das PDF Beziehungshoroskop_… bzw. Freundschaftshoroskop_…,
# englisch Relationship_Horoscope_… bzw. Friendship_Horoscope_… (__main__ prueft OUT).
CHARTDATA = f'/home/claude/<A>_Beziehung_<B>_{DATUM}_chart_data.md'
ANALYSE = f'/home/claude/<A>_Beziehung_<B>_{DATUM}_analyse.md'
RADPNG = '<A>_Beziehung_<B>_doppelrad.png'     # muss auf _doppelrad.png enden (PFLICHT_BAUSTEINE)
OUT = f'/home/claude/Beziehungshoroskop_<A>_und_<B>_{DATUM}.pdf'   # = Name im Klientenordner, Unterordner 06_Beziehung
DOCTYPE = 'beziehung'     # build.PFLICHT_BAUSTEINE
# Cover, letzte Zeile: beide Vornamen mit Geburtsdatum, Tag ohne fuehrende
# Null, Monat in VERSALIEN, z. B. '<A> · 3. MAI 1980   —   <B> · 9. JULI 2012';
# englisch Monat englisch ('<A> · 3 MAY 1980 — …').
GEBURTSZEILE = '<A · T. MONAT JJJJ   —   B · T. MONAT JJJJ>'
SPRACHE = 'de'
SIGNATUR_EN = {}
BELEG_HAND = {}           # nur fuer Belege, die beziehung.belege_en() nicht schafft

from build import BASE_CSS                     # noqa: E402

# --- Deckblatt-Angaben: gelesen, nie abgetippt -------------------------------
DECKBLATT = build.lies_deckblatt(CHARTDATA)
LEITSATZ = DECKBLATT['LEITSATZ']
LEITACHSE = DECKBLATT['LEITACHSE']
TITELMOTIV = DECKBLATT['TITELMOTIV']
PALETTE_VORGABE = DECKBLATT['PALETTE']      # steuert die Farbwahl unten
ORNAMENT = DECKBLATT['GLYPHEN']             # Inhaltsverzeichnis

# --- Die Rechnung: gelesen aus dem Datenblatt der Beziehung -----------------
R = beziehung.lies_beziehung(CHARTDATA)
if (R['A']['vorname'], R['B']['vorname']) != (A_VORNAME, B_VORNAME):
    raise SystemExit('Datenblatt der Beziehung traegt %s und %s, die Vorlage %s und %s '
                     '— Datei verwechselt oder Platzhalter?' % (
                         R['A']['vorname'], R['B']['vorname'], A_VORNAME, B_VORNAME))
ASPEKT_ZEILEN = len(R['kreuz']) + len(R['achsen'])

PART_KICKER = set()                         # keine Teiler-Kapitel
OPEN_PAGE = {'Zur Lesart', 'On Reading This'}   # eigene Seite; das Schlusswort bewusst NICHT

# Breitenleiter fuer die Einmessung der Radseite: 15,6 cm abwaerts.
BREITEN = ['%.1fcm' % (x / 10) for x in range(156, 118, -2)]
SKALEN = (1.0, 0.96, 0.92, 0.88, 0.84, 0.80, 0.76, 0.72)

# --- Palette -----------------------------------------------------------------
# Je Beziehungshoroskop aus PALETTE_VORGABE abgeleitet. Was hier steht, sind
# PLATZHALTER. Sind Palette UND die Verlaufsstopps in COVER_CSS gesetzt,
# PALETTE_GESETZT auf True stellen; vorher bricht der Builder unten ab.
# Schon eingemessene Werte hier eintragen, dann misst __main__ nicht noch
# einmal (None = messen).
RAD_BREITE = None         # cm, Doppelrad-Seite
STAENDE_SKALA = None      # Skala der Staendeseite
KREUZ_SKALA = None        # Skala der Verbindungsseite
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

# Radfarben: Hausstil-Standard, Tinte und Ring an die Dokumentfarben
# angeglichen; die zweite Person steht im Aussenring in beziehung.FARBE_B.
RAD_PALETTE = dict(radix.DEFAULT_PALETTE)
RAD_PALETTE.update({'ink': INK, 'ring': '#9c9384'})

PAL = {'night': NIGHT, 'petrol': PETROL, 'petrol_l': PETROL_L, 'deep': DEEP,
       'gold': GOLD, 'gold_l': GOLD_L, 'stone': STONE, 'paper': PAPER,
       'ink': INK, 'beleg_bg': BELEG_BG, 'beleg_bd': BELEG_BD}

BELEG_EN = {}
if SPRACHE == 'en':
    BELEG_EN = beziehung.belege_en(ANALYSE, [A_VORNAME, B_VORNAME], hand=BELEG_HAND)

chartdoc.konfiguriere(pal=PAL, part_kicker=PART_KICKER, glyphen=dict(radix.FAKTOR_GLYPHE),
                      kopfzeile=('%s %s %s' % (A_VORNAME, 'UND' if SPRACHE == 'de' else 'AND',
                                               B_VORNAME)).upper(),
                      aspektfarben=RAD_PALETTE, part_ornament=ORNAMENT,
                      sprache=SPRACHE, signaturen_en=SIGNATUR_EN, belege_en=BELEG_EN,
                      # 2026-10-11 (F3): Paar „ihr“ — die Datenschutz-Zeile der
                      # Inhaltsseite heisst dann „zu eurem Horoskop“. Nicht aendern.
                      # 2026-10-14c: Freundschaft ebenso (beziehung.IHR_ARTEN).
                      anrede='ihr' if R['art'] in beziehung.IHR_ARTEN else 'du')
# 2026-10-14 (Auswertung 14.10., F3): Quincunx-Zeile der Aspekt-Legende nach Regel 5
# des Beziehungsmoduls („zwingt zu ständigem Nachjustieren“) — gleich nach
# konfiguriere(), das die Legende der Sprache setzt. Nicht ändern.
beziehung.legende_beziehung(chartdoc)
esc = chartdoc.esc

COVER_CSS = f"""
/* ---------- Cover ---------- */
section.cover {{ page: cover; position:relative; width:21cm; height:29.7cm;
                 overflow:hidden; }}
.cv-sky {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm;
  background: linear-gradient(to bottom, /* PLATZHALTER — Verlauf aus PALETTE_VORGABE, je Horoskop neu */
     #06121c 0%, #123340 33%, #35605c 62%, #f0d9a6 100%); }}
.cv-art {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm; }}
.cv-star {{ position:absolute; border-radius:50%; background:#eaf1f5; }}
.cv-block {{ position:absolute; left:0; right:0; text-align:center; }}
.cv-kicker {{ font-family:"EB Garamond"; font-size:8.2pt; letter-spacing:0.42em;
   color:{GOLD_L}; }}
.cv-name {{ font-family:"Cinzel"; font-size:27pt; letter-spacing:0.13em;
   color:#f2ead6; }}
.cv-und {{ font-family:"EB Garamond Italic"; font-style:italic; font-size:17pt;
   letter-spacing:0.02em; text-transform:none; }}
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
""" + beziehung.BEZIEHUNG_CSS


# ===========================================================================
# Cover — das Motiv setzt TITELMOTIV um, nichts anderes. Render-sichere
# Bausteine und Fallen: Design-Render-Modul, „Render-Sicherheit" (keine
# SVG-Verlaeufe, kein <svg><text>, Abblenden ueber die Farbe, Catmull-Rom).
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
    """Das Titelmotiv. Je Horoskop neu gebaut — hier steht nur das Geruest.
    Es zeigt, was die Leitachse zwischen BEIDEN Bildern traegt (Datenblatt-
    Modul, @@DECKBLATT, Regeln 1, 3, 4)."""
    p = ['<svg class="cv-art" viewBox="0 0 595 842" preserveAspectRatio="none" '
         'xmlns="http://www.w3.org/2000/svg">']
    # … Vollton-Flaechen, Scheibenverlaeufe, Bezierkurven nach TITELMOTIV …
    return '\n'.join(p) + '</svg>'


# Sternfeld: (x, y, radius, deckung) im 595x842-Raster — leer = keins. Nie in
# den Textbereich (x 120–475, y 74–260) legen; cover_stars() filtert das ab.
STERNE = []


def cover_stars():
    """Sternfeld aus STERNE — nie im Textbereich des Covers."""
    pts = [q for q in STERNE if not (120 <= q[0] <= 475 and 74 <= q[1] <= 260)]
    return ''.join(f'<div class="cv-star" style="left:{x/595*21:.3f}cm;'
                   f'top:{y/842*29.7:.3f}cm;width:{r*2/595*21:.3f}cm;'
                   f'height:{r*2/595*21:.3f}cm;opacity:{o}"></div>'
                   for x, y, r, o in pts)


def y2cm(y):
    return y / 842 * 29.7


# VOLLBILD-COVER wie beim Geburtshoroskop: Rechnet der Lauf das Titelmotiv als
# ganzseitiges PNG, setzt er COVER_BILD und schreibt die Rechnung in
# cover_bild_rechnen(); __main__ ruft sie bei jedem Lauf. COVER_HELL schaltet
# Leitsatz und Geburtszeile auf helle Schrift (dunkles Motiv am unteren Rand).
COVER_BILD = None      # <<Pfad des im Lauf gerechneten Vollbilds (PNG oder JPEG) — oder None>>
COVER_HELL = False


def cover_bild_rechnen():
    """Rechnet das Vollbild nach TITELMOTIV und schreibt es nach COVER_BILD."""
    raise SystemExit('REFERENZ-Vorlage: COVER_BILD ist gesetzt, aber '
                     'cover_bild_rechnen() rechnet noch nichts.')


def _cover_grund():
    """Hintergrund des Covers: das gerechnete Vollbild oder Verlauf, Sterne, SVG."""
    if COVER_BILD:
        import base64
        with open(COVER_BILD, 'rb') as f:
            roh = f.read()
        mime = 'image/jpeg' if roh[:3] == b'\xff\xd8\xff' else 'image/png'
        return '<img class="cv-bild" src="data:%s;base64,%s">' % (
            mime, base64.b64encode(roh).decode('ascii'))
    return '<div class="cv-sky"></div>\n%s\n%s' % (cover_stars(), cover_svg())


def glyphe(x, y, size, color, zeichen, op=0.9):
    """Eine tragende Glyphe aus DECKBLATT['GLYPHEN'], dezent ueber dem SVG."""
    return (f'<div class="cv-gl" style="left:{(x-40)/595*21:.3f}cm;'
            f'width:{80/595*21:.3f}cm;top:{y2cm(y):.2f}cm;font-size:{size}pt;'
            f'color:{color};opacity:{op}">{zeichen}</div>')


def cover_html(kicker):
    """Das Cover. `kicker` ist der DOKUMENTTYP AUS DER H1 der analyse.md in
    Versalien. Hoehen im 842-Raster: 88 Kicker, 112 Namen („A und B“, das
    Bindewort klein und kursiv), 168 Linie, 788 letzte Leitsatzzeile (waechst
    nach oben, chartdoc.leitsatz_block()), 822 Geburtszeile beider."""
    und = 'und' if SPRACHE == 'de' else 'and'
    namen = (f'{esc(A_VORNAME.upper())} <span class="cv-und">{und}</span> '
             f'{esc(B_VORNAME.upper())}')
    return f"""<section class="{'cover hell' if COVER_HELL else 'cover'}">
{_cover_grund()}
<div class="cv-block cv-kicker" style="top:{y2cm(88):.2f}cm">{esc(kicker)}</div>
<div class="cv-block cv-name" style="top:{y2cm(112):.2f}cm">{namen}</div>
<div class="cv-block" style="top:{y2cm(168):.2f}cm"><div class="cv-rule"></div></div>
{chartdoc.leitsatz_block(LEITSATZ)}
<div class="cv-block cv-birth" style="top:{y2cm(822):.2f}cm">{esc(GEBURTSZEILE)}</div>
</section>"""


# ===========================================================================
# Chartbild-Strecke — Doppelrad, Staende, Verbindungen (beziehung.py)
# ===========================================================================

# Unterzeile des Doppelrads: wer innen, wer aussen steht, beide Geburtsdaten
# wie im Kopf der Datenblaetter (Tag ohne fuehrende Null), Haeuser der inneren
# Person, und dass nur die engen Verbindungen als Linie stehen.
RAD_NOTE = {
    'de': (f'Innen {A_VORNAME} mit den eigenen Häusern · <T. Monat JJJJ, HH:MM ZONE> · <Ort> — '
           f'außen {B_VORNAME} · <T. Monat JJJJ, HH:MM ZONE> · <Ort>. Häuser nach Koch; '
           'die Linien zeigen nur die engen Verbindungen zwischen beiden Bildern '
           '(innerhalb des halben Orbis), alle stehen auf der Seite der Verbindungen.'),
    'en': (f'Inside {A_VORNAME} with {A_VORNAME}’s houses · <D Month YYYY, HH:MM ZONE> · <Place> — '
           f'outside {B_VORNAME} · <D Month YYYY, HH:MM ZONE> · <Place>. Koch houses; '
           'the lines show only the close connections between the two charts '
           '(within half the orb); all are listed on the page of connections.')}[SPRACHE]


def rad_zeichnen():
    """Das Doppelrad, bei jedem Lauf neu (beziehung.doppelrad)."""
    return beziehung.doppelrad(R, '/home/claude/' + RADPNG, palette=RAD_PALETTE)


def chartbild(rad_breite=None, staende_skala=1.0, kreuz_skala=1.0):
    titel = beziehung.DOPPELRAD_TITEL if SPRACHE == 'de' else \
        beziehung.SEITEN_EN[beziehung.DOPPELRAD_TITEL]
    kicker = beziehung.KREUZ_KICKER if SPRACHE == 'de' else \
        beziehung.SEITEN_EN[beziehung.KREUZ_KICKER]
    return (chartdoc.radix_page(RADPNG, RAD_NOTE, kicker=kicker, titel=titel,
                                bild_breite=rad_breite)
            + beziehung.staende_page(R, skala=staende_skala, sprache=SPRACHE)
            + beziehung.kreuz_page(R, skala=kreuz_skala, sprache=SPRACHE))


# ===========================================================================
# Zusammenbau
# ===========================================================================

parsed = build.parse_analyse(ANALYSE, client=KLIENT)
items = build.prepare_chapters(parsed)
colon_pairs = build.make_colon_pairs(items)
KICKER = parsed['doctype'].upper()          # Cover-Kickerzeile = Dokumenttyp der H1
# 2026-10-14c: Kopf der Inhaltsseite aus dem Dokumenttyp der H1 („Beziehungshoroskop
# für …“, „Freundschaftshoroskop für …“, „Relationship Horoscope for …“, „Friendship
# Horoscope for …“) — die Beziehung-Probe (B1) haelt die H1 gegen die Art.
INHALT_KOPF = parsed['doctype'] + {'de': ' für {a} und {b}',
                                   'en': ' for {a} and {b}'}[SPRACHE]


def _t(de):
    return de if SPRACHE == 'de' else beziehung.SEITEN_EN[de]


TOC_VORNE = [(_t(beziehung.KREUZ_KICKER), [
    (_t(beziehung.DOPPELRAD_TITEL), 'PG_rad'),
    (_t(beziehung.STAENDE_TITEL), 'PG_staende'),
    (_t(beziehung.KREUZ_TITEL), 'PG_kreuz')])]

SEITEN = {}


def build_html(breaks=(), rad_breite=None, staende_skala=1.0, kreuz_skala=1.0,
               nur_frontmatter=False):
    """Das ganze Dokument — oder mit nur_frontmatter=True nur Cover, Inhalt und
    Chartbild-Strecke (fuer die Einmessung)."""
    parts = [f'<!doctype html><html lang="{SPRACHE}"><head><meta charset="utf-8">'
             '<style>', BASE_CSS, chartdoc.struktur_css(), COVER_CSS,
             '</style></head><body>',
             cover_html(KICKER),
             chartdoc.inhalt_page(items, SEITEN,
                                  INHALT_KOPF.format(a=A_VORNAME, b=B_VORNAME),
                                  vorne=TOC_VORNE, ornament=ORNAMENT),
             chartbild(rad_breite, staende_skala, kreuz_skala)]
    if not nur_frontmatter:
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
    for _n, _v in (('GEBURTSZEILE', GEBURTSZEILE), ('RAD_NOTE', RAD_NOTE),
                   ('OUT', OUT), ('DATUM', DATUM), ('RADPNG', RADPNG)):
        if '<' in _v and '>' in _v:
            raise SystemExit('REFERENZ-Vorlage: %s traegt noch den Platzhalter — '
                             'aus den Datenblaettern eintragen.' % _n)
    # 2026-10-14c: der PDF-Name folgt Art und Sprache (Freundschaft: Freundschaftshoroskop_…)
    _stamm = beziehung.dateiname(R['art'], A_VORNAME, B_VORNAME, DATUM, 'pdf',
                                 englisch=(SPRACHE == 'en'))[:-len('.pdf')]
    if _stamm not in os.path.basename(OUT):
        raise SystemExit('REFERENZ-Vorlage: OUT heisst %s — fuer diese Art und Sprache '
                         'heisst das PDF %s.pdf (ein Zusatz _b, _c ist erlaubt; '
                         'beziehung.dateiname, Modul „Dateinamen und Ablage“).'
                         % (os.path.basename(OUT), _stamm))

    # 1. Doppelrad (und ein Vollbild-Cover) IMMER selbst zeichnen.
    rad_zeichnen()
    if COVER_BILD:
        cover_bild_rechnen()

    # 2. Einmessen statt schaetzen — am Frontmatter allein.
    def frontmatter(**kw):
        return build_html(nur_frontmatter=True, **kw)

    rad = RAD_BREITE if RAD_BREITE is not None else chartdoc.passe_ein(
        lambda w: frontmatter(rad_breite=w), 'PG_rad', BREITEN, was='Doppelrad-Seite')
    ss = STAENDE_SKALA if STAENDE_SKALA is not None else chartdoc.passe_ein(
        lambda x: frontmatter(rad_breite=rad, staende_skala=x), 'PG_staende', SKALEN,
        was='Ständeseite')
    ks = KREUZ_SKALA if KREUZ_SKALA is not None else chartdoc.passe_ein(
        lambda x: frontmatter(rad_breite=rad, staende_skala=ss, kreuz_skala=x),
        'PG_kreuz', SKALEN, was='Verbindungsseite')

    # 3. Satzsicher rendern, Seitenzahlen im Inhalt aus dem echten Dokument.
    doc, seiten = chartdoc.render_mit_inhalt(
        lambda breaks: build_html(breaks, rad, ss, ks),
        OUT, items, colon_pairs, SEITEN,
        required_fields={'Leitsatz': LEITSATZ, 'Titelmotiv': TITELMOTIV},
        extra_must=[(LEITSATZ.split(' — ')[0].split('\n')[0], 'Leitsatz aufs Cover')],
        doctype=DOCTYPE)
    print('Verbindungen (Sollzahl verify):', ASPEKT_ZEILEN, '| Kapitel:', len(items),
          '| Seiten:', len(doc.pages))
    print('Inhalt:', seiten.get('PG_inhalt'), '| Doppelrad:', seiten.get('PG_rad'),
          '| Stände:', seiten.get('PG_staende'), '| Verbindungen:', seiten.get('PG_kreuz'))
