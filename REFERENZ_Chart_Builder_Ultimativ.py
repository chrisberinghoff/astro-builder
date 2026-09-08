#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REFERENZ: vollstaendiger Chart-Builder (Beispiel Ultimativ-Modus).

Stand nach dem Hausstil-Beschluss vom 2026-07-27, ergaenzt am 2026-07-30 um
die gelesene Deckblatt-Bestellung. Die chart-unabhaengige Mechanik UND die
Chartbild-Seiten stecken in `claude/chartdoc.py`; hier steht nur noch, was sich
je Chart wirklich aendert:

    1. PALETTE           die Farbwerte oben (RAD_PALETTE = Radfarben), abgeleitet
                         aus DECKBLATT['PALETTE']
    2. COVER_CSS + cover_svg()/cover_stars()/cover_html()
                         das individuelle Titelmotiv aus DECKBLATT['TITELMOTIV']
    3. KONST / ACHSEN    die Chartdaten (kommen aus chartdata.py)
    4. ANALYSE / CHARTDATA / OUT / RADPNG / UHRPNG
    5. beim Ultimativ zusaetzlich: tdat.setze_quelle(...) auf die chart_data
                         und die beiden Anhangtabellen

Alles andere — Struktur-CSS, Inhaltsverzeichnis, Radseite, Konstellationsseite,
Aspektseite, Transit-Uhr-Seite, Kapitelkopf und Kapitelfuss mit Signatur/Beleg,
satzsicherer Umbruch, Zwei-Pass-Seitenzahlen, Einmessung „passt auf eine Seite"
— kommt aus chartdoc und wird NICHT neu geschrieben.

FUENF DINGE, DIE HIER BEWUSST SO STEHEN:
  * LEITSATZ, LEITACHSE, TITELMOTIV, PALETTE und GLYPHEN werden GELESEN, nicht
    abgetippt: `build.lies_deckblatt()` holt sie aus dem @@DECKBLATT-Block am
    Ende der chart_data.md. Fehlt der Block, bricht der Lauf ab. Grund
    (Vorfall 2026-07-30, Chart A): Schritt 3 suchte den Block nur in der
    analyse.md, fand nichts, zog die Fallback-Regel und erfand ein komplett
    anderes Cover. Nebeneffekt: in dieser Vorlage steht kein fremder Leitsatz
    mehr im Klartext, der sich abschreiben liesse (Vorfall 2026-07-29, Chart B).
  * Der Builder ZEICHNET SEINE GRAFIKEN SELBST, bei jedem Lauf (rad_zeichnen,
    uhr_zeichnen). Ein PNG, das vom letzten Direktaufruf herumliegt, rendert
    still einen alten Datenstand — genau das ist am 2026-07-27 passiert.
  * Radbreite, Uhrbreite und Aspektskala werden EINGEMESSEN, nicht gesetzt.
  * Die Seitenfolge hinter dem Cover ist fest: Inhalt, Radix, Konstellationen,
    Aspekte, Transit-Uhr.
  * Die Kapitel-Schleife ruft `chartdoc.build_fuss(it)` hinter dem letzten
    Absatz auf. Signatur und Beleg rendern seit dem 2026-09-05 am KAPITELENDE,
    nicht mehr im Kopf (Innere Arbeit, „Verhaeltnis zum Klartext-Modul",
    Punkt 2). Fehlt der Aufruf, bricht render_mit_inhalt() hart ab — sonst
    verschwaenden Signatur und Beleg lautlos aus dem ganzen Dokument.

Aufruf:  python3 <klient>_builder.py
Geprueft wird beim Rendern automatisch: build.PFLICHT_BAUSTEINE fuer den
uebergebenen doctype (hier 'ultimativ').
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
CHARTDATA = '/home/claude/<klient>_Ultimativ_chart_data.md'
ANALYSE = '/home/claude/<klient>_Ultimativ_analyse.md'
RADPNG = '<klient>_radix.png'
UHRPNG = '<klient>_transituhr.png'
OUT = '/home/claude/<klient>_Ultimativ_Horoskop.pdf'

tdat.setze_quelle(CHARTDATA)
from build import BASE_CSS                     # noqa: E402

# --- Cover-Bestellung: gelesen, nie abgetippt ------------------------------
# Der @@DECKBLATT-Block steht am ENDE der chart_data.md, direkt hinter dem
# @@SELEKTOR-Block — NICHT in der analyse.md. lies_deckblatt() wirft, wenn er
# fehlt oder unvollstaendig ist; nur so kann kein Lauf still ein eigenes Motiv
# erfinden. Einzelheiten s. claude/REGISTER_Leitsaetze.md, Abschnitt „Wo der
# @@DECKBLATT-Block steht".
DECKBLATT = build.lies_deckblatt(CHARTDATA)
LEITSATZ = DECKBLATT['LEITSATZ']
LEITACHSE = DECKBLATT['LEITACHSE']
TITELMOTIV = DECKBLATT['TITELMOTIV']
PALETTE_VORGABE = DECKBLATT['PALETTE']      # steuert die Farbwahl unten
ORNAMENT = DECKBLATT['GLYPHEN']             # Teiler-Seiten + Inhaltsverzeichnis

PART_KICKER = {'Teil I', 'Teil II', 'Teil III', 'Vertiefung'}
# Eigene Seite (kein Teiler-Layout). Das Schlusswort laeuft bewusst NICHT hier
# mit: der erzwungene Umbruch liess im Erstlauf eine Seite mit vier Zeilen.
OPEN_PAGE = {'Auftakt'}

# Breitenleiter fuer die Einmessung von Radseite und Transit-Uhr.
BREITEN = ['%.1fcm' % (x / 10) for x in range(172, 118, -2)]

# --- Palette ---------------------------------------------------------------
# Die Werte kommen aus PALETTE_VORGABE (Grundstimmung aus den dominanten
# Elementen). Hier stehen Platzhalter — je Chart neu setzen, nicht uebernehmen.
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
                      aspektfarben=RAD_PALETTE, part_ornament=ORNAMENT)
esc = chartdoc.esc

COVER_CSS = f"""
/* ---------- Cover ---------- */
section.cover {{ page: cover; position:relative; width:21cm; height:29.7cm;
                 overflow:hidden; }}
.cv-sky {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm;
  background: linear-gradient(to bottom, /* Verlauf aus PALETTE_VORGABE */
     #06121c 0%, #123340 33%, #35605c 62%, #f0d9a6 100%); }}
.cv-art {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm; }}
.cv-star {{ position:absolute; border-radius:50%; background:#eaf1f5; }}
.cv-block {{ position:absolute; left:0; right:0; text-align:center; }}
.cv-kicker {{ font-family:"EB Garamond"; font-size:8.2pt; letter-spacing:0.42em;
   color:{GOLD_L}; }}
.cv-name {{ font-family:"Cinzel"; font-size:31pt; letter-spacing:0.15em;
   color:#f2ead6; }}
.cv-rule {{ width:3.2cm; height:1pt; background:{GOLD_L}; margin:0 auto; }}
.cv-sub {{ font-family:"EB Garamond"; font-size:11.4pt; letter-spacing:0.05em;
   color:#cfd9d8; }}
.cv-sub2 {{ font-family:"EB Garamond Italic"; font-style:italic; font-size:10.4pt;
   color:#b9c8c8; }}
.cv-leit {{ font-family:"EB Garamond Italic"; font-style:italic; font-size:15.4pt;
   color:#4a3512; letter-spacing:0.02em; }}
.cv-birth {{ font-family:"EB Garamond"; font-size:8.6pt; letter-spacing:0.2em;
   color:#6b5220; }}
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


def cover_stars():
    """Sternfeld — nie in den Textbereich des Covers legen."""
    pts = [(38, 62, 1.5, .85), (142, 44, 1.8, .9), (556, 112, 1.7, .85)]
    pts = [q for q in pts if not (120 <= q[0] <= 475 and 74 <= q[1] <= 240)]
    out = []
    for x, y, r, o in pts:
        out.append(f'<div class="cv-star" style="left:{x/595*21:.3f}cm;'
                   f'top:{y/842*29.7:.3f}cm;width:{r*2/595*21:.3f}cm;'
                   f'height:{r*2/595*21:.3f}cm;opacity:{o}"></div>')
    return ''.join(out)


def y2cm(y):
    return y / 842 * 29.7


def glyphe(x, y, size, color, zeichen, op=0.9):
    """Eine tragende Glyphe aus DECKBLATT['GLYPHEN'], dezent ueber dem SVG."""
    return (f'<div class="cv-gl" style="left:{(x-40)/595*21:.3f}cm;'
            f'width:{80/595*21:.3f}cm;top:{y2cm(y):.2f}cm;font-size:{size}pt;'
            f'color:{color};opacity:{op}">{zeichen}</div>')


def cover_html():
    return f"""<section class="cover">
<div class="cv-sky"></div>
{cover_stars()}
{cover_svg()}
<div class="cv-block cv-kicker" style="top:{y2cm(88):.2f}cm">GEBURTSBILD · SEELE · ZEIT</div>
<div class="cv-block cv-name" style="top:{y2cm(112):.2f}cm">{VORNAME.upper()}</div>
<div class="cv-block" style="top:{y2cm(168):.2f}cm"><div class="cv-rule"></div></div>
<div class="cv-block cv-sub" style="top:{y2cm(186):.2f}cm">Horoskop</div>
<div class="cv-block cv-sub2" style="top:{y2cm(208):.2f}cm">Anlage, Seelenweg und die Jahre &lt;von&gt; bis &lt;bis&gt;</div>
<div class="cv-block cv-leit" style="top:{y2cm(788):.2f}cm">{html.escape(LEITSATZ)}</div>
<div class="cv-block cv-birth" style="top:{y2cm(822):.2f}cm">&lt;TT. MONAT JJJJ · HH:MM MEZ/MESZ · ORT&gt;</div>
</section>"""


# ===========================================================================
# Chartbild-Strecke — die Seiten baut chartdoc, hier stehen nur die Daten
# ===========================================================================

ASPEKTE = cd.aspektliste()
TD = tdat.parse()

# Zielnamen mit Umlaut brauchen einen Glyphen-Eintrag (der §11-Report schreibt
# „Glückspunkt"/„Mondknoten", transitdata.GLYPH kennt nur ASCII).
tdat.GLYPH.update({'Glückspunkt': '⊗', 'Mondknoten': '☊'})

# Die Themennamen der Uhr sind die KAPITELTITEL AUS TEIL III B des laufenden
# Charts — erfundene Namen sind ein Fehler. tuhr.THEMEN ist im Repo mit den
# Namen eines einzelnen Laufs vorbelegt und MUSS hier ueberschrieben werden.
# Traegt EIN Transiter zwei Themenkapitel, bekommt der erste Eintrag eine
# Zielliste als fuenftes Feld; jede Zeile geht in das ERSTE passende Thema.
tuhr.THEMEN = [
    ('<Kapiteltitel Teil III B>', '<Untertitel>', ['<Transiter>'], '#7d3b46',
     ['<Ziel>', '<Ziel>']),
    ('<Kapiteltitel Teil III B>', '<Untertitel>', ['<Transiter>'], '#6b5c48'),
]

REIHENFOLGE = ['Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'Jupiter', 'Saturn',
               'Uranus', 'Neptun', 'Pluto', 'SEP', 'Knoten', 'Suedknoten',
               'Chiron', 'Lilith', 'Pholus', 'Glueckspunkt']
KLASSISCH = ['Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'Jupiter', 'Saturn',
             'Uranus', 'Neptun', 'Pluto']
_BY = {f['name']: f for f in cd.factors}

RAD_NOTE = (f'{VORNAME} · <TT. Monat JJJJ, HH:MM MEZ/MESZ> · <Ort> · '
            'Häuser nach Koch · wahrer Mondknoten · wahre Lilith · Aspekte '
            'nach Huber-Orbis')
KONST_NOTE = ('Doppelte Hausangabe: Der Faktor steht bis 5° vor der nächsten '
              'Hausspitze und wird in beiden Häusern gedeutet — das führende '
              'Haus steht vorn.')


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
            out.append(('☋', 'Südknoten', cd.sign_name(cd.SUEDKNOTEN),
                        cd.gr(cd.SUEDKNOTEN % 30), cd.haus(cd.SUEDKNOTEN),
                        'rückläufig'))
            continue
        f = _BY[n]
        lauf = 'rückläufig' if f['retro'] else 'direkt'
        if n == 'Glueckspunkt':
            lauf = '—'
        glyph = '' if f['glyph'] == 'Pho' else f['glyph']
        out.append((glyph, cd.name_of(n), cd.sign_name(f['lon']),
                    cd.gr(f['lon'] % 30), cd.haus(f['lon']), lauf))
    return out


def achsen_zeilen():
    return [(k, lab, cd.sign_name(lo), cd.gr(lo % 30))
            for k, lab, lo in cd.ACHSEN]


ELEMENTE, MODI = chartdoc.verteilung(
    [(cd.name_of(n), _BY[n]['lon']) for n in KLASSISCH])

UHR_STICHTAG = TD['fenster']['stichtag'].strftime('%d.%m.%Y')
UHR_NOTE = (f"Fenster {TD['fenster']['start'].strftime('%d.%m.%Y')} bis "
            f"{TD['fenster']['ende'].strftime('%d.%m.%Y')} — acht "
            f"Kalenderquartale ab dem Quartal des Stichtags · Rückblick ab "
            f"{TD['fenster']['rueckblick'].strftime('%d.%m.%Y')} · "
            f"Wirk-Orb 1,5° · Snapshot-Orb 3,0°")

# Dreiteiliger Vorspann der Uhr. chartdoc.uhr_lead() liefert eine einteilige
# Fassung; die Themenuhr braucht mehr Erklaerung, darum hier ausgeschrieben.
UHR_LEAD = [
    'Jede Zeile ist eine lange Linie: ein Planet, der gerade am Himmel läuft, '
    'berührt über Wochen oder Monate hinweg eine Stelle deines Geburtsbildes. '
    'Die Linien stehen nicht einzeln nebeneinander, sondern in Themenblöcken — '
    'jeder Block trägt oben den Namen, unter dem der Text ihn später behandelt, '
    'und darunter einen dicken Bogen über die gesamte Laufzeit des Themas. So '
    'liest man erst die fünf, sechs großen Zeiten und geht dann ins Einzelne.',

    'Die Beschriftung am Zeilenanfang nennt beide Seiten in dieser Reihenfolge '
    '— zuerst den laufenden Planeten, dann den Winkel, den er bildet, dann die '
    'Stelle deines Geburtsbildes, die er trifft. Der Balken rechts daneben '
    'zeigt, wann das geschieht: blass die volle Berührungszeit, kräftig die '
    'Strecke, in der die Linie wirklich arbeitet, und die kleinen weißen '
    'Punkte die einzelnen Tage, an denen der Winkel exakt steht. Blass '
    'gesetzte Zeilen sind Nebenlinien, die im Text nicht eigens behandelt '
    'werden.',

    f'Die acht Quartale sind Kalenderquartale; Q1 ist das Quartal, in dem '
    f'dieses Horoskop entstanden ist. Was links der senkrechten Marke liegt, '
    f'lief schon vor dem {UHR_STICHTAG}. Unter der Zeitachse stehen als '
    f'farbige Punkte die Stationen: die Tage, an denen ein langsamer Planet '
    f'die Richtung wechselt. Sie erklären, warum dieselbe Linie oft zwei- oder '
    f'dreimal exakt wird statt nur einmal.']


def chartbild(rad_breite, uhr_breite, skala):
    return (chartdoc.radix_page(RADPNG, RAD_NOTE, bild_breite=rad_breite)
            + chartdoc.konstellationen_page(konst_zeilen(), achsen_zeilen(),
                                            ELEMENTE, MODI, note=KONST_NOTE)
            + chartdoc.aspekt_page(ASPEKTE, skala=skala)
            + chartdoc.transituhr_page(UHRPNG, UHR_STICHTAG, UHR_NOTE,
                                       lead=UHR_LEAD, bild_breite=uhr_breite))


# ===========================================================================
# Anhang — die beiden Ultimativ-Pflichttabellen (chart-eigen)
# ===========================================================================

def dt(d, kurz=False):
    return d.strftime('%d.%m.%y' if kurz else '%d.%m.%Y')


# Der §11-Report ist ASCII: freie Textfelder (Transit-Staende,
# Stationen-Position, Ziel-Aufzaehlung) tragen 'Loewe' und 'Glueckspunkt'.
# ziel_label() greift dort nicht — darum hier einmal zurueckuebersetzen.
_UM = {'Loewe': 'Löwe', 'Schuetze': 'Schütze', 'Glueckspunkt': 'Glückspunkt',
       'Suedknoten': 'Südknoten'}


def um(s):
    s = str(s)
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
        mon = str(r['monate']).replace('.', ',')
        exl = ', '.join(dt(x, True) for x in r['exakt'])
        rows.append(
            f'<tr{trc}>'
            f'<td class="tg">{tdat.GLYPH.get(r["transiter"], "")}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(r["transiter"]))}</td>'
            f'<td class="ta">{esc(r["aspekt"])}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(r["ziel"]))}</td>'
            f'<td class="ts">{vor}{dt(r["start"], True)} – '
            f'{dt(r["ende"], True)}{nach}</td>'
            f'<td class="td_">{mon}</td>'
            f'<td class="te">{exl}</td>'
            f'<td class="tst">{st}</td></tr>')
    return f"""<section class="anhang" id="PG_anh1">
<div class="fm-kicker">Anhang</div>
<h2 class="fm-title">Die langen Linien im Überblick</h2>
<div class="fm-rule"></div>
<p class="fm-lead">Alle {len(TD['langlaeufer'])} Langläufer des Fensters mit
Spanne, Dauer, sämtlichen Exaktdaten und den Stationen des laufenden Planeten.
Grau gesetzt sind die sekundären Linien — sie berühren keinen der primären
Zielpunkte und werden im Text nicht eigens gedeutet.</p>
<table class="anh">
<colgroup><col style="width:0.5cm"><col style="width:1.6cm">
<col style="width:1.5cm"><col style="width:1.55cm"><col style="width:2.85cm">
<col style="width:1.0cm"><col style="width:4.9cm"><col style="width:3.25cm">
</colgroup>
<thead><tr><th></th><th>Transit</th><th>Aspekt</th>
<th>Ziel</th><th>Spanne</th><th>Mon.</th><th>exakt</th>
<th>Stationen</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<div class="anh-note">Dauer in Monaten über die volle Berührung
(Snapshot-Orb 3,0°). Datumsangaben TT.MM.JJ. <span class="mk">←</span> vor der
Spanne heißt: die Linie lief schon vor dem Stichtag; <span class="mk">→</span>
dahinter: sie reicht über das Fenster hinaus.</div>
</section>"""


def anhang_jetzt():
    f = TD['fenster']
    stand = ' · '.join(
        f'{tdat.GLYPH.get(x["planet"], "")} {um(x["planet"])} '
        f'{um(x["zeichen"])} {um(x["pos"])} (Haus {x["haus"]})'
        for x in TD['stand'])
    rows = []
    for r in TD['im_orb']:
        ex = r['exakt_txt'].replace('exakt war ', 'zuletzt ').replace('exakt ', '')
        ex = re.sub(r'(\d{4})-(\d\d)-(\d\d)', lambda m:
                    f'{m.group(3)}.{m.group(2)}.{m.group(1)[2:]}', ex)
        ex = re.sub(r'\b1 T\)', '1 Tag)', ex.replace(' T)', ' Tagen)'))
        richtung = r['richtung'] + (', kehrt zurück' if r['kehrt'] else '')
        trc = '' if r['primaer'] else ' class="sec"'
        orb = str(r['orb']).replace('.', ',')
        bis = dt(tdat._d(r['bis']), True) if r['bis'] else ''
        rows.append(
            f'<tr{trc}>'
            f'<td class="tg">{tdat.GLYPH.get(r["transiter"], "")}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(r["transiter"]))}</td>'
            f'<td class="ta">{esc(r["aspekt"])}</td>'
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
            f'<td class="ta">{esc(x["aspekt"])}</td>'
            f'<td class="tz">{esc(tdat.ziel_label(x["ziel"]))}</td>'
            f'<td class="te">{dt(x["exakt"])}</td>'
            f'<td class="tri">{x["tage"]} Tage</td></tr>' for x in xs)
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
        f'<td class="tri">{esc(x["richtung"])}</td>'
        f'<td class="tz">{esc(um(x["pos"]))}</td>'
        f'<td class="te">{esc(um(x["ziele"]))}</td></tr>'
        for x in TD['stationen'])

    return f"""<section class="anhang flow" id="PG_anh2">
<div class="anh-kopf">
<div class="fm-kicker">Anhang</div>
<h2 class="fm-title">Der Stichtag im Überblick</h2>
<div class="fm-rule"></div>
<p class="fm-lead">Die Momentaufnahme vom {dt(f['stichtag'])}: was an diesem Tag
an deinem Geburtsbild arbeitet, mit Orb und Laufrichtung. Zulaufend heißt, die
Berührung wird enger; auslaufend, sie löst sich — kann aber rückläufig
zurückkehren.</p>
<div class="anh-note" style="margin:0 0 0.4cm 0">Transit-Stände: {stand}</div>
</div>
<table class="anh">
<colgroup><col style="width:0.5cm"><col style="width:1.6cm">
<col style="width:1.6cm"><col style="width:1.55cm"><col style="width:1.1cm">
<col style="width:2.5cm"><col style="width:6.9cm"><col style="width:1.45cm">
</colgroup>
<thead><tr><th></th><th>Transit</th><th>Aspekt</th>
<th>Ziel</th><th>Orb</th><th>Richtung</th><th>exakt</th>
<th>bis</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
{liste('nachhall', 'Nachhall — kürzlich exakt')}
{liste('anmarsch', 'Anmarsch — exakt in den nächsten 90 Tagen')}
<div class="anh-sub">Stationen im Umfeld des Stichtags</div>
<table class="anh">
<colgroup><col style="width:1.45cm"><col style="width:0.5cm">
<col style="width:1.6cm"><col style="width:1.75cm"><col style="width:2.5cm">
<col style="width:9.4cm"></colgroup>
<tbody>{stat}</tbody></table>
<div class="anh-note">Snapshot-Orb 3,0°; was im Wirk-Orb von 1,5° steht, wird
in Teil III eigens gedeutet.</div>
</section>"""


# ===========================================================================
# Zusammenbau
# ===========================================================================

parsed = build.parse_analyse(ANALYSE, client=KLIENT)
items = build.prepare_chapters(parsed)
colon_pairs = build.make_colon_pairs(items)
ANHANG = anhang_langlaeufer() + anhang_jetzt()

TOC_VORNE = [('Das Chart im Bild', [
    ('Die Radix', 'PG_rad'),
    ('Die Konstellationen', 'PG_konst'),
    (chartdoc.ASPEKT_TITEL, 'PG_asp'),
    ('Die Transit-Uhr', 'PG_uhr')])]
TOC_HINTEN = [('Anhang', [
    ('Die langen Linien im Überblick', 'PG_anh1'),
    ('Der Stichtag im Überblick', 'PG_anh2')])]

# Seitenzahlen fuers Inhaltsverzeichnis: erster Durchlauf leer, danach aus dem
# gerenderten Dokument gefuellt (chartdoc.render_mit_inhalt).
SEITEN = {}


def build_html(breaks=(), skala=1.0, uhr_breite=None, rad_breite=None):
    parts = ['<!doctype html><html lang="de"><head><meta charset="utf-8">'
             '<style>', BASE_CSS, chartdoc.struktur_css(), COVER_CSS,
             '</style></head><body>',
             cover_html(),
             chartdoc.inhalt_page(items, SEITEN, f'Horoskop für {VORNAME}',
                                  vorne=TOC_VORNE, hinten=TOC_HINTEN,
                                  ornament=ORNAMENT),
             chartbild(rad_breite, uhr_breite, skala)]
    first_chapter = True
    for i, it in enumerate(items):
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
                body.append(f'<div class="subhead">{esc(b["text"])}</div>')
            else:
                is_first_block = not first_p_used
                first_p_used = True
                body.append(chartdoc.build_paragraph(i, j, b, breaks,
                                                     allow_drop, is_first_block))
            j += 1
        # Signatur und Beleg rendern seit dem 2026-09-05 am KAPITELENDE, unter
        # der letzten Bewegung (Innere Arbeit, „Verhaeltnis zum
        # Klartext-Modul", Punkt 2). build_fuss() gibt '' zurueck bei
        # Teiler-Kapiteln und bei jedem Kapitel ohne Signatur UND ohne Beleg —
        # der Aufruf darf also unbedingt stehen. Fehlt er, bricht
        # render_mit_inhalt() hart ab (chartdoc.pruefe_kapitelfuss).
        inner = head + ''.join(body) + chartdoc.build_fuss(it)
        if is_part:
            inner = f'<div class="part-inner">{inner}</div>'
        parts.append(f'<section class="{" ".join(cls)}" id="CH_{i}">'
                     f'{inner}</section>')
    parts.append(ANHANG)
    parts.append('</body></html>')
    return '\n'.join(parts)


if __name__ == '__main__':
    # 1. Grafiken IMMER selbst zeichnen — nie ein herumliegendes PNG benutzen.
    rad_zeichnen()
    uhr_zeichnen()

    # 2. Einmessen statt schaetzen: groesste Breite/Schriftstufe, bei der die
    #    jeweilige Seite einseitig bleibt.
    rad = chartdoc.passe_ein(lambda w: build_html(rad_breite=w), 'PG_rad',
                             BREITEN, was='Radseite')
    uhr = chartdoc.passe_ein(lambda w: build_html(uhr_breite=w, rad_breite=rad),
                             'PG_uhr', BREITEN, was='Transit-Uhr')
    skala = chartdoc.passe_aspektseite_ein(
        lambda s: build_html(skala=s, uhr_breite=uhr, rad_breite=rad), ASPEKTE)

    # 3. Satzsicher rendern, Seitenzahlen im Inhalt aus dem echten Dokument.
    doc, seiten = chartdoc.render_mit_inhalt(
        lambda breaks: build_html(breaks, skala, uhr, rad),
        OUT, items, colon_pairs, SEITEN,
        required_fields={'Leitsatz': LEITSATZ, 'Titelmotiv': TITELMOTIV},
        extra_must=[(LEITSATZ, 'Leitsatz aufs Cover')],
        doctype='ultimativ')
    print('Aspektzeilen:', len(ASPEKTE), '| Kapitel:', len(items),
          '| Langlaeufer:', len(TD['langlaeufer']),
          '| Jetzt-Kontakte:', len(TD['im_orb']))
    print('Inhalt:', seiten.get('PG_inhalt'), '| Rad:', seiten.get('PG_rad'),
          '| Konstellationen:', seiten.get('PG_konst'),
          '| Aspekte:', seiten.get('PG_asp'), '| Uhr:', seiten.get('PG_uhr'),
          '| Anhang:', seiten.get('PG_anh1'), seiten.get('PG_anh2'))
