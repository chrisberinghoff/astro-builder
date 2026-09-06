#!/usr/bin/env python3
"""
radix.py — selbst gezeichnetes Chart-Rad (Radix) für die Horoskop-Pipeline.

Zweck: Das Rad auf Seite 1 des Horoskops wird NICHT mehr aus einem fremden
PDF (astroschmid) eingebettet, sondern hier aus den bereits berechneten
Chart-Daten selbst gezeichnet. Vorteil: Das Rad zeigt exakt dieselben
Huber-Aspekte wie die Aspekttabelle (beide speisen sich aus `huber_aspects`),
ist vektorscharf, im Cover-Stil einfärbbar und quellen-unabhängig.

Öffentliche Funktionen:

    huber_aspects(factors, orbs=None) -> list
        Berechnet die Aspekte nach Huber-Orbis (planetenindividuell). DIESELBE
        Liste speist Rad UND Aspekttabelle -> beide sind garantiert deckungsgleich.

    haus_und_grenzlage(lon, cusps, orb=5) -> dict
        Haupthaus + Grenzlage eines Faktors nach der einheitlichen 5°-Haus-Regel
        (zweite, von den Aspekt-Orben STRIKT getrennte Orb-Ebene).

    radix(factors, cusps, asc, mc, out_path=..., title=..., aspects=None,
          palette=None, gradmarke=True) -> str
        Zeichnet das Rad als PNG und gibt den Pfad zurück.

    strukturbild(factors, cusps, aspects=None, zusatz=None, alter=None) -> dict
        ALLE Struktur-Befunde in einem Aufruf: Element-/Modusverteilung in drei
        Zählungen (auch gewichtet), Rückläufigkeit, Herrscherketten mit Kreisen
        und Enddispositoren, HAUSHERRSCHER, Rezeptionen, Aspektdichte je Faktor,
        das Netz der Spezialfaktoren, Aspektfiguren, Zyklusfenster.
        strukturbild_text(sb) schreibt daraus den fertigen `## Strukturbild`-
        Abschnitt fürs chart_data.md. Eingeführt 2026-09-06 (Prüfbericht 5.1–5.6);
        bis dahin wurde das alles von Hand gerechnet, und vier Ebenen fehlten
        ganz, weil keine Regel nach ihnen fragte.

Verwendung als Modul (Schritt 3/4, Design-Konversation):
    import sys; sys.path.insert(0, "/home/claude")
    import radix
    asp = radix.huber_aspects(factors)          # einmal rechnen
    radix.radix(factors, cusps, asc, mc,        # Rad daraus
                out_path="/home/claude/<klient>_radix.png",
                title="<Klient> — Radix (Koch)", aspects=asp)
    #  ... und dieselbe `asp`-Liste für die Aspekttabelle im HTML verwenden.

WICHTIG: matplotlib wird bei Bedarf automatisch nachinstalliert. Der Container
wird zwischen Sessions zurückgesetzt — diese Datei liegt darum im Projektwissen.
Braucht KEIN pyswisseph (bekommt fertige Positionen); die Ephemeride-Rechnung
(Pholus, True Node) passiert in Schritt 1, s. Datenblatt-Modul.
"""

import subprocess
import sys

# --- Konstanten -------------------------------------------------------------

SIGN_GLYPHS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
_ELEM_OF_SIGN = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]  # Feuer, Erde, Luft, Wasser

# Hausstil-Palette (gemeinsam festgelegt 2026-07-27). Gegenüber der ersten
# Fassung sind die Zeichenfarben des Aussenrings und vor allem das Aspekt-Grün
# satter: Grün und Blau waren im gedruckten Rad bei 1,4 pt Strichstärke kaum
# auseinanderzuhalten. palette=... in radix() überschreibt sie fürs Cover.
DEFAULT_PALETTE = {
    # Fe, Er, Lu, Wa — je eine Stufe voller als die erste Fassung
    # (#e6c9c2 / #d2e0cf / #ece4c2 / #cbd8e6)
    'elements': ['#e0b6ab', '#bcd3b5', '#e6d9a6', '#b5c9de'],
    'rot':   '#b0392b',   # Spannung: Opposition, Quadrat
    'blau':  '#2f5f97',   # harmonisch: Trigon, Sextil
    'gruen': '#1f7a3c',   # Wahrnehmung: Quincunx, Halbsextil — satt, nicht oliv
    'ink':   '#2b2b2b',   # Glyphen
    'ring':  '#9a9a9a',   # Ringe/Hauslinien
    'grund': '#f8f4ec',   # Bildhintergrund = Papierfarbe des Dokuments
}

# Huber-Standardorbis pro Faktor (individuelle Seite; Details im Datenblatt-Modul)
HUBER_ORB = {
    'Sonne': 8, 'Mond': 8, 'Merkur': 8, 'Venus': 6, 'Jupiter': 6,
    'Saturn': 4, 'Mars': 4, 'Uranus': 3, 'Neptun': 3, 'Pluto': 3,
    'Knoten': 3, 'Suedknoten': 3, 'Lilith': 3, 'Chiron': 3, 'Pholus': 3,
    'Glueckspunkt': 3, 'AC': 9, 'MC': 9, 'DC': 9, 'IC': 9,
}

# Aspektwinkel -> (Farbkategorie, Nebenaspekt-Fixorb | None für Haupt/Konjunktion)
_ASPECT_DEFS = [
    (0,   'konj',  None),
    (30,  'gruen', 2),
    (60,  'blau',  6),
    (90,  'rot',   None),
    (120, 'blau',  None),
    (150, 'gruen', 3),
    (180, 'rot',   None),
]
_MAIN_ANGLES = {0, 90, 120, 180}   # inkl. Konjunktion: Einzelseiten-Prüfung
_ANG_NAME = {0: 'Konjunktion', 30: 'Halbsextil', 60: 'Sextil', 90: 'Quadrat',
             120: 'Trigon', 150: 'Quincunx', 180: 'Opposition'}


# --- Aspektrechnung ---------------------------------------------------------

def huber_aspects(factors, orbs=None):
    """Aspekte zwischen allen `factors` nach Huber-Orbis.

    factors: Liste von dicts mit mindestens {'name', 'lon'} (lon = ekl. Länge°).
    orbs:    optionales dict name->Orb; überschreibt HUBER_ORB je Faktor.

    Rückgabe: Liste von dicts
        {'a','b','angle','name','color','strength','orb'}
    """
    def orb_of(n):
        if orbs and n in orbs:
            return orbs[n]
        return HUBER_ORB.get(n, 3)

    out = []
    for i in range(len(factors)):
        for j in range(i + 1, len(factors)):
            a, b = factors[i], factors[j]
            d = abs(a['lon'] - b['lon']) % 360
            if d > 180:
                d = 360 - d
            o1, o2 = orb_of(a['name']), orb_of(b['name'])
            for angle, color, neben in _ASPECT_DEFS:
                dev = abs(d - angle)
                if angle in _MAIN_ANGLES:
                    if dev <= min(o1, o2):
                        strength = 'voll'
                    elif dev <= max(o1, o2):
                        strength = 'einseitig'
                    else:
                        continue
                else:  # Nebenaspekt: fixer Orb, auf beide Faktor-Orbis gedeckelt
                    if dev <= min(neben, o1, o2):
                        strength = 'neben'
                    else:
                        continue
                out.append({'a': a['name'], 'b': b['name'], 'angle': angle,
                            'name': _ANG_NAME[angle], 'color': color,
                            'strength': strength, 'orb': round(dev, 2)})
                break
    return out


# --- Zusatzebene: Halb-/Anderthalbquadrate (Beschluss 2026-08-08) -----------
# Huber kennt diese Aspektklasse nicht; sie läuft deshalb bewusst NICHT durch
# huber_aspects und NICHT ins Rad (Datenblatt, Aspekttabelle und Rad bleiben
# Huber-deckungsgleich). Ergebnis wird im chart_data als eigene Tabelle
# „Untergrund-Aspekte" geführt und niedriger gewichtet gedeutet; gedeutete
# Kontakte zusätzlich in den ⚠-Schritt-3-Block (manuell aufgenommene Aspekte).

_ZUSATZ_ANGLES = [(45, 'Halbquadrat'), (135, 'Anderthalbquadrat')]
_PLANETEN = ('Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'Jupiter',
             'Saturn', 'Uranus', 'Neptun', 'Pluto')


def zusatz_aspekte(factors, orb=2.0, nur_planeten=True):
    """Halb- (45°) und Anderthalbquadrate (135°), fixer Orb, Default nur
    Planet–Planet (die zehn klassischen Planeten, keine Achsen/Punkte).

    Rückgabeformat wie huber_aspects; strength='zusatz', Farbe 'rot'
    (Spannungsfamilie). Getrennt von huber_aspects gehalten — s. Kommentar oben.
    """
    pool = [f for f in factors if (not nur_planeten) or f['name'] in _PLANETEN]
    out = []
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            a, b = pool[i], pool[j]
            d = abs(a['lon'] - b['lon']) % 360
            if d > 180:
                d = 360 - d
            for angle, name in _ZUSATZ_ANGLES:
                dev = abs(d - angle)
                if dev <= orb:
                    out.append({'a': a['name'], 'b': b['name'], 'angle': angle,
                                'name': name, 'color': 'rot',
                                'strength': 'zusatz', 'orb': round(dev, 2)})
                    break
    return out


# --- Haus-Zuordnung & Grenzlage (einheitliche 5°-Regel) ---------------------

HAUS_ORB = 5   # Grenzlagen-Orb in Grad, planetenunabhängig


def _gr(deg):
    """Grad-Betrag als N°NN′ (Grad + Bogenminuten)."""
    d = int(deg)
    m = int(round((deg - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"{d}°{m:02d}′"


def haus_und_grenzlage(lon, cusps, orb=HAUS_ORB):
    """Haupthaus + Grenzlage eines Faktors nach der einheitlichen Haus-Orb-Regel."""
    lon = lon % 360
    for k in range(12):
        span = (cusps[(k + 1) % 12] - cusps[k]) % 360
        rel = (lon - cusps[k]) % 360
        if rel < span:
            haus = k + 1
            bis_spitze = span - rel
            grenz = bis_spitze <= orb
            neben = (haus % 12) + 1 if grenz else None
            if grenz:
                label = (f"Haus {haus} (Grenzlage → {neben}, "
                         f"{_gr(bis_spitze)} vor Spitze {neben})")
            else:
                label = f"Haus {haus}"
            return {'haus': haus, 'nebenhaus': neben, 'grenzlage': grenz,
                    'abstand_spitze': round(bis_spitze, 2), 'label': label}
    return {'haus': None, 'nebenhaus': None, 'grenzlage': False,
            'abstand_spitze': None, 'label': 'Haus ?'}


def haus_spalte(lon, cusps, orb=HAUS_ORB):
    """Kompakte Haus-Angabe für die Konstellationstabelle: '7' oder '11/12'.

    Hausstil seit 2026-07-27: In der Tabelle steht bei einer Grenzlage NUR die
    Doppelzahl, kein Wort „Grenzlage" und keine Gradangabe — führendes Haus
    vorn. Die Stufe (≤2° Schwelle / 2–5° Grenzlage) entscheidet, welches Haus
    führt; sie wird weiter in Schritt 1/2 aus `abstand_spitze` bestimmt.
    """
    h = haus_und_grenzlage(lon, cusps, orb)
    if not h['grenzlage']:
        return str(h['haus'])
    if h['abstand_spitze'] <= 2:                 # Schwellenlage: Nebenhaus führt
        return f"{h['nebenhaus']}/{h['haus']}"
    return f"{h['haus']}/{h['nebenhaus']}"       # Grenzlage: rechnerisch führt


# --- Zeichnung --------------------------------------------------------------

def radix(factors, cusps, asc, mc, out_path='/home/claude/radix.png',
          title=None, aspects=None, palette=None, dpi=210, grade=False,
          gradmarke=True):
    """Zeichnet das Chart-Rad (Koch) als PNG, gibt out_path zurück.

    Geometrie: AC links (9 Uhr), Zeichen laufen gegen den Uhrzeigersinn;
    screen-Winkel = 180 + (lon - asc). Ein schiefes Achsenkreuz bei hoher
    geogr. Breite (Quadrant < 90°) ist KORREKT, kein Fehler.

    grade=False (Hausstil seit 2026-07-27): KEINE Gradzahlen unter den
    Planetenglyphen. Sie liefen bei eng stehenden Faktoren regelmässig in die
    Nachbarglyphe, und dieselbe Angabe steht eine Seite weiter in der
    Konstellationstabelle vollständig (Grad, Bogenminute, Laufrichtung). Das
    Rad zeigt seitdem nur noch die Figur. grade=True stellt das alte Verhalten
    wieder her — NICHT zusammen mit gradmarke benutzen, die Zahl landet dann
    auf der Haarlinie des Nachbarn.

    gradmarke=True (HAUSSTIL seit 2026-07-30, mit Chris abgenommen): jeder
    Faktor bekommt eine **Positionsmarke auf seinem exakten Grad** — ein
    kräftiger dunkler Strich am Innenrand des Zeichenbands, dazu eine Haarlinie
    zur Glyphe, wenn die Kollisionsstaffelung diese nach innen gerückt hat.
    Grund: die Glyphe steht zwar am richtigen Winkel, ist aber breit und wird
    bei Häufungen radial nach innen verschoben — im Rad war damit nicht
    ablesbar, wo ein Faktor GENAU steht und welche Glyphe zu welcher Stelle
    gehört. Sichtbar wird das immer dann, wenn zwei Faktoren weniger als etwa
    3° auseinanderliegen: bisher standen dort zwei Glyphen scheinbar
    nebeneinander ohne jede Gradangabe.

    Damit die Marke nicht mit einem Skalenstrich zu verwechseln ist, wandert
    die graue 5°/10°-Skala in das farbige Zeichenband (feiner Rand am
    Innenrand); der Ring zwischen Band und Glyphen gehört seitdem allein den
    Positionsmarken. Die Glyphen rücken dafür minimal nach innen (0,80 →
    0,775). AC/DC/MC/IC bekommen KEINE Marke — sie tragen ihre rote Achslinie
    von R_ASP bis R_OUT und sind damit schon exakt markiert.

    Wer gradmarke=False setzt, bekommt das Rad im Stand vom 2026-07-27 zurück
    (5°-Skala innen, Glyphen auf 0,80, keine Marken).

    Der Hintergrund ist die Papierfarbe des Dokuments (palette['grund']), nicht
    Weiss — sonst steht das Rad als weisses Rechteck auf der cremefarbenen
    Seite.
    """
    try:
        import matplotlib
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'matplotlib',
                        '--break-system-packages', '-q'], check=True)
        import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge
    import numpy as np

    pal = dict(DEFAULT_PALETTE)
    if palette:
        pal.update(palette)
    if aspects is None:
        aspects = huber_aspects(factors)
    pos = {f['name']: f['lon'] for f in factors}
    INK, RING = pal['ink'], pal['ring']
    AXC = pal['rot']

    def th(L):
        return (180 + (L - asc)) % 360

    def xy(L, r):
        t = np.radians(th(L))
        return r * np.cos(t), r * np.sin(t)

    fig, ax = plt.subplots(figsize=(7, 7), dpi=dpi)
    ax.set_xlim(-1.16, 1.16)
    ax.set_ylim(-1.16, 1.16)
    ax.set_aspect('equal')
    ax.axis('off')
    R_OUT, R_SIGN, R_HOUSE, R_ASP = 1.0, 0.86, 0.66, 0.575
    # Mit Positionsmarken rücken die Glyphen etwas nach innen: der freigeräumte
    # Ring braucht Platz für Marke UND Haarlinie.
    R_PL = 0.775 if gradmarke else 0.80
    # Ohne Gradzahlen darf die Staffelung enger sein — der frueher noetige
    # Abstand ging fast ganz auf das Gradkaertchen unter der Glyphe.
    TIER_DR, TAG_DR = (0.105 if grade else 0.078), 0.052

    # Zeichenring nach Element gefärbt + Glyphen
    for k in range(12):
        t1 = th(30 * k)
        ax.add_patch(Wedge((0, 0), R_OUT, t1, t1 + 30, width=R_OUT - R_SIGN,
                     facecolor=pal['elements'][_ELEM_OF_SIGN[k]],
                     edgecolor='white', lw=1.2, zorder=1))
        gx, gy = xy(30 * k + 15, (R_OUT + R_SIGN) / 2)
        ax.text(gx, gy, SIGN_GLYPHS[k], ha='center', va='center',
                fontsize=15, color=INK, zorder=3)
    for r in (R_OUT, R_SIGN, R_HOUSE):
        ax.add_patch(plt.Circle((0, 0), r, fill=False, ec=RING, lw=1.0, zorder=2))
    ax.add_patch(plt.Circle((0, 0), R_ASP, fill=False, ec='#c9c9c9', lw=0.8, zorder=2))

    # 5°/10°-Skala. Mit Positionsmarken liegt sie IM farbigen Zeichenband (als
    # feiner Rand am Innenrand), sonst wie früher innen davor. Grund: läge sie
    # weiter in demselben Ring wie die Marken, liest sich die Marke als vierter,
    # aus der Reihe getanzter Skalenstrich.
    for g in range(0, 360, 5):
        d = 0.035 if g % 10 == 0 else 0.02
        r1 = (R_SIGN + d * 0.80) if gradmarke else (R_SIGN - d)
        x0, y0 = xy(g, R_SIGN)
        x1, y1 = xy(g, r1)
        ax.plot([x0, x1], [y0, y1], color='#8a8a8a', lw=0.6, zorder=2)

    # Hausspitzen + Nummern
    for k in range(12):
        c = cusps[k]
        span = (cusps[(k + 1) % 12] - c) % 360
        x0, y0 = xy(c, R_ASP)
        x1, y1 = xy(c, R_HOUSE)
        ax.plot([x0, x1], [y0, y1], color=RING, lw=0.8, zorder=2)
        mid = (c + span / 2) % 360
        nx, ny = xy(mid, R_HOUSE - 0.045)
        ax.text(nx, ny, str(k + 1), ha='center', va='center',
                fontsize=8, color='#6f6f6f', zorder=3)

    # Achsenkreuz AC/DC/MC/IC
    for L, lab in [(asc, 'AC'), ((asc + 180) % 360, 'DC'),
                   (mc, 'MC'), ((mc + 180) % 360, 'IC')]:
        lx, ly = xy(L, R_OUT + 0.06)
        ax.text(lx, ly, lab, ha='center', va='center', fontsize=10,
                color=AXC, fontweight='bold', zorder=4)
        x0, y0 = xy(L, R_ASP)
        x1, y1 = xy(L, R_OUT)
        ax.plot([x0, x1], [y0, y1], color=AXC, lw=1.3, zorder=2)

    # Aspektlinien (Konjunktion ohne Linie)
    for asp in aspects:
        if asp['color'] == 'konj':
            continue
        if asp['a'] not in pos or asp['b'] not in pos:
            continue
        col = pal[asp['color']]
        x0, y0 = xy(pos[asp['a']], R_ASP)
        x1, y1 = xy(pos[asp['b']], R_ASP)
        if asp['strength'] == 'voll':
            lw, al, ls = 1.4, 0.85, '-'
        elif asp['strength'] == 'einseitig':
            lw, al, ls = 0.8, 0.5, (0, (4, 3))
        else:
            lw, al, ls = 0.9, 0.7, '-'
        ax.plot([x0, x1], [y0, y1], color=col, lw=lw, alpha=al, ls=ls, zorder=1.5)

    # Planeten mit einfacher Kollisionsstaffelung (bei <6° Abstand alternierend).
    # Bekannte Grenze, am 2026-07-30 bewusst so gelassen: bei DREI dicht
    # beieinander stehenden Faktoren springt die Staffelung zurueck auf Stufe 0,
    # der erste und dritte koennen sich dann beruehren. Die Positionsmarke traegt
    # in diesem Fall die genaue Stelle, auch wenn die Glyphen eng liegen.
    ACHSEN = ('AC', 'DC', 'MC', 'IC')
    order = sorted(factors, key=lambda f: f['lon'])
    last, tier = -999.0, 0
    for f in order:
        L = f['lon']
        g = f.get('glyph', '?')
        tier = (tier + 1) % 2 if 0 <= (L - last) % 360 < 6 else 0
        last = L
        r = R_PL - tier * TIER_DR
        px, py = xy(L, r)

        # Positionsmarke auf dem exakten Grad + Haarlinie zur Glyphe.
        if gradmarke and f['name'] not in ACHSEN:
            xa, ya = xy(L, R_SIGN - 0.002)
            xb, yb = xy(L, R_SIGN - 0.034)
            ax.plot([xa, xb], [ya, yb], color=INK, lw=1.45,
                    solid_capstyle='butt', zorder=3.5)
            r_glyph = r + 0.030
            if (R_SIGN - 0.034) - r_glyph > 0.004:
                xc, yc = xy(L, R_SIGN - 0.034)
                xd, yd = xy(L, r_glyph)
                ax.plot([xc, xd], [yc, yd], color=INK, lw=0.5, alpha=0.40,
                        zorder=3.2)

        ax.text(px, py, g, ha='center', va='center',
                fontsize=(13 if len(g) == 1 else 8.5), color=INK, zorder=4)
        if grade:
            dx, dy = xy(L, r - TAG_DR)
            tag = f"{int(f['lon'] % 30)}°" + ("℞" if f.get('retro') else "")
            ax.text(dx, dy, tag, ha='center', va='center',
                    fontsize=6.2, color='#707070', zorder=4)

    if title:
        ax.text(0, -1.115, title, ha='center', va='center',
                fontsize=8.5, color='#555555')
    grund = pal.get('grund', 'white')
    fig.patch.set_facecolor(grund)
    ax.set_facecolor(grund)
    fig.savefig(out_path, bbox_inches='tight', facecolor=grund, dpi=dpi)
    plt.close(fig)
    return out_path


# --- Strukturbild: die Statik unter den Einzeldeutungen ---------------------
#
# Eingefuehrt 2026-09-06 nach dem ersten Prueflauf des Standard-Geburtshoroskops
# (PRUEFBERICHT_Geburtshoroskop_2026-09-05, Rubrik 5). Bis dahin wurde das
# Strukturbild in Schritt 1 von Hand in Python zusammengerechnet und von Hand
# ausgeschrieben. Zwei Folgen: Erstens fehlten Ebenen, nach denen keine Regel
# ausdruecklich fragte — Hausherrscher (Befund 5.2, „die groesste fachliche
# Luecke\"), Aspektdichte je Faktor (5.1), Rezeption (5.4), das Netz der
# Spezialfaktoren untereinander (5.5). Zweitens zaehlte die Element-/
# Modusverteilung eine Sonne wie einen Pholus (5.3). Beides ist reine
# Arithmetik auf Daten, die nach huber_aspects ohnehin fertig vorliegen; es
# gehoert deshalb in den Code und nicht in die Handrechnung.
#
# strukturbild() rechnet, strukturbild_text() schreibt den fertigen
# `## Strukturbild`-Abschnitt fuers chart_data. Beides deterministisch und
# ohne Deutung — die Deutung bleibt Schritt 2.

SIGN_NAMES = ['Widder', 'Stier', 'Zwillinge', 'Krebs', 'Löwe', 'Jungfrau',
              'Waage', 'Skorpion', 'Schütze', 'Steinbock', 'Wassermann',
              'Fische']
_ELEM_NAMES = ['Feuer', 'Erde', 'Luft', 'Wasser']
_MODUS_NAMES = ['kardinal', 'fix', 'veränderlich']

# Moderne Herrscher (Projekt-Standard, s. Datenblatt-Modul, Strukturbild §3);
# die klassischen Zweitherrscher laufen als eigene Kette mit, weil sie bei
# Skorpion/Wassermann/Fische regelmaessig eine ANDERE Kette ergeben — und die
# Rezeptionen, die es nur klassisch gibt, sonst unsichtbar blieben.
HERRSCHER = {
    'Widder': 'Mars', 'Stier': 'Venus', 'Zwillinge': 'Merkur', 'Krebs': 'Mond',
    'Löwe': 'Sonne', 'Jungfrau': 'Merkur', 'Waage': 'Venus', 'Skorpion': 'Pluto',
    'Schütze': 'Jupiter', 'Steinbock': 'Saturn', 'Wassermann': 'Uranus',
    'Fische': 'Neptun',
}
HERRSCHER_KLASSISCH = dict(HERRSCHER, **{
    'Skorpion': 'Mars', 'Wassermann': 'Saturn', 'Fische': 'Jupiter'})

# Zaehlgewichte fuer die dritte, gewichtete Element-/Modusrechnung (Befund 5.3).
# Grund: Ein schwaechstes Element, das nur von Pholus oder vom Gluueckspunkt
# getragen wird, ist etwas anderes als eines, das die Sonne traegt — die
# ungewichtete Zaehlung kann beides nicht unterscheiden und fuehrt die
# Befundzeile dann in die Irre. DC und IC zaehlen NICHT mit: sie sind die
# Spiegelpole von AC und MC und wuerden dieselbe Aussage doppelt gewichten.
GEWICHT = {
    'Sonne': 2.0, 'Mond': 2.0, 'AC': 2.0, 'MC': 2.0,
    'Merkur': 1.0, 'Venus': 1.0, 'Mars': 1.0, 'Jupiter': 1.0, 'Saturn': 1.0,
    'Uranus': 1.0, 'Neptun': 1.0, 'Pluto': 1.0,
    'Knoten': 0.5, 'Suedknoten': 0.5, 'Chiron': 0.5, 'Lilith': 0.5,
    'Pholus': 0.5, 'Glueckspunkt': 0.5,
    'DC': 0.0, 'IC': 0.0,
}

SPEZIALFAKTOREN = ('Chiron', 'Lilith', 'Pholus', 'Glueckspunkt',
                   'Knoten', 'Suedknoten')
WINKEL = ('AC', 'MC', 'DC', 'IC')
PERSOENLICH = ('Sonne', 'Mond', 'Merkur', 'Venus', 'Mars')

# Aspektgewichte fuer die Dichterechnung (Befund 5.1). Ein voller Hauptaspekt
# zaehlt eins, alles Schwaechere ein halbes. Die Zahl ist kein Messwert,
# sondern ein Ordnungsmass: sie sagt, welche Funktionen im Chart viel Verkehr
# haben und welche isoliert arbeiten — das wird im Alltag ganz anders erlebt
# als eine Einzeldeutung.
_DICHTE_GEWICHT = {'voll': 1.0, 'einseitig': 0.5, 'neben': 0.5, 'zusatz': 0.5}


def zeichen_index(lon):
    """Ekliptikale Laenge -> Zeichenindex 0..11 (Widder = 0)."""
    return int((lon % 360) // 30)


def zeichen_name(lon):
    return SIGN_NAMES[zeichen_index(lon)]


def _norm_name(s):
    """Faktor-/Zeichennamen robust vergleichbar machen (Umlaute, Gross/Klein)."""
    s = (s or '').strip()
    for a, b in (('ö', 'oe'), ('ü', 'ue'), ('ä', 'ae'), ('ß', 'ss'),
                 ('Ö', 'Oe'), ('Ü', 'Ue'), ('Ä', 'Ae')):
        s = s.replace(a, b)
    return s.lower()


_SIGN_LOOKUP = {_norm_name(n): n for n in SIGN_NAMES}


def _sign_kanonisch(name):
    return _SIGN_LOOKUP.get(_norm_name(name))


def verteilung(factors, gewichtet=False, nur_planeten=False):
    """Element- und Modusverteilung.

    gewichtet=False, nur_planeten=True   -> die Zaehlung der Konstellationsseite
    gewichtet=False, nur_planeten=False  -> alle uebergebenen Faktoren, je 1
    gewichtet=True                       -> nach GEWICHT (Lichter/Winkel doppelt,
                                            Spezialfaktoren halb, DC/IC gar nicht)

    Rueckgabe: {'elemente': {name: wert}, 'modi': {name: wert},
                'schwaechstes_element': …, 'schwaechster_modus': …,
                'traeger': {elementname: [Faktornamen]}}
    """
    el = {n: 0.0 for n in _ELEM_NAMES}
    mo = {n: 0.0 for n in _MODUS_NAMES}
    traeger = {n: [] for n in _ELEM_NAMES}
    traeger_mo = {n: [] for n in _MODUS_NAMES}
    for f in factors:
        nm = f['name']
        if nur_planeten and nm not in _PLANETEN:
            continue
        g = GEWICHT.get(nm, 1.0) if gewichtet else 1.0
        if g == 0:
            continue
        k = zeichen_index(f['lon'])
        el[_ELEM_NAMES[k % 4]] += g
        mo[_MODUS_NAMES[k % 3]] += g
        traeger[_ELEM_NAMES[k % 4]].append(nm)
        traeger_mo[_MODUS_NAMES[k % 3]].append(nm)
    schw_el = min(el, key=lambda k: el[k])
    schw_mo = min(mo, key=lambda k: mo[k])
    return {'elemente': {k: round(v, 1) for k, v in el.items()},
            'modi': {k: round(v, 1) for k, v in mo.items()},
            'schwaechstes_element': schw_el, 'schwaechster_modus': schw_mo,
            'traeger': traeger, 'traeger_modus': traeger_mo}


def aspektdichte(factors, aspects, zusatz=None):
    """Aspektdichte je Faktor (Befund 5.1 des Prueflaufs).

    Zaehlt je Faktor die Aspekte, gewichtet nach Staerke (_DICHTE_GEWICHT), und
    teilt in drei Gruppen: dicht verschaltet (oberes Drittel der Spanne), duenn
    (unteres Drittel) und unaspektiert (kein einziger Kontakt).

    Ein unaspektierter Faktor ist der wichtigste Einzelbefund dieser Rechnung —
    er arbeitet ohne Verbindung zum Rest des Bildes und wird im Alltag als etwas
    erlebt, das sich nicht mit dem uebrigen Leben verzahnt. Bis 2026-09-06 fiel
    er nur auf, wenn er jemandem beim Schreiben zufaellig auffiel.
    """
    zaehl = {f['name']: 0.0 for f in factors}
    anzahl = {f['name']: 0 for f in factors}
    for a in list(aspects) + list(zusatz or []):
        g = _DICHTE_GEWICHT.get(a.get('strength'), 0.5)
        for seite in ('a', 'b'):
            nm = a[seite]
            if nm in zaehl:
                zaehl[nm] += g
                anzahl[nm] += 1
    # Die vier Winkel bleiben aus der Gruppierung heraus. Zwei Gruende: DC und
    # IC tragen die Aspekte ihrer Gegenachse gespiegelt und wuerden doppelt
    # zaehlen; und alle vier haben mit 9 Grad den weitesten Orb im System und
    # stehen darum bauartbedingt an der Spitze jeder Dichteliste. Ein Winkel
    # unter den „dicht verschalteten" Faktoren waere keine Information. Ihre
    # Werte stehen weiter in 'gewichtet' und werden getrennt ausgewiesen.
    pool = {k: v for k, v in zaehl.items() if k not in WINKEL}
    werte = sorted(pool.values())
    if werte:
        lo, hi = werte[0], werte[-1]
        spanne = hi - lo
        g_dicht = lo + spanne * 2 / 3 if spanne else hi
        g_duenn = lo + spanne / 3 if spanne else lo
    else:
        g_dicht = g_duenn = 0
    dicht = sorted([k for k, v in pool.items() if v >= g_dicht and v > 0],
                   key=lambda k: -pool[k])
    duenn = sorted([k for k, v in pool.items() if 0 < v <= g_duenn],
                   key=lambda k: pool[k])
    unaspektiert = sorted([k for k, v in pool.items() if v == 0])
    return {'gewichtet': {k: round(v, 1) for k, v in zaehl.items()},
            'anzahl': anzahl, 'dicht': dicht, 'duenn': duenn,
            'unaspektiert': unaspektiert,
            'winkel': {k: round(zaehl[k], 1) for k in WINKEL if k in zaehl}}


def _kette(faktor, zeichen_von, herrscher_tab):
    """Herrscherkette ab `faktor`, bis sie sich schliesst oder ausserhalb endet.

    Rueckgabe: (pfad, zyklus)  — zyklus ist die geschlossene Teilkette oder [].
    """
    pfad, gesehen = [faktor], {faktor: 0}
    cur = faktor
    while True:
        z = zeichen_von.get(cur)
        if not z:
            return pfad, []
        nxt = herrscher_tab.get(z)
        if not nxt or nxt not in zeichen_von:
            if nxt:
                pfad.append(nxt)
            return pfad, []
        if nxt in gesehen:
            return pfad, pfad[gesehen[nxt]:]
        gesehen[nxt] = len(pfad)
        pfad.append(nxt)
        cur = nxt


def herrscherketten(factors, klassisch=False):
    """Zeichenherrscher-Ketten, geschlossene Kreise und Enddispositoren.

    Ein Enddispositor steht im eigenen Zeichen; bei ihm enden Faeden. Ein
    geschlossener Kreis ohne Enddispositor bedeutet, dass jedes Glied die
    Bedingungen des naechsten erbt (Befund 5.4 des Prueflaufs) — daher wird der
    Kreis mit ausgegeben und nicht nur seine Existenz vermerkt.
    """
    tab = HERRSCHER_KLASSISCH if klassisch else HERRSCHER
    zeichen_von = {f['name']: zeichen_name(f['lon']) for f in factors
                   if f['name'] in _PLANETEN}
    ketten, kreise, endd = {}, [], []
    for nm in zeichen_von:
        pfad, zyklus = _kette(nm, zeichen_von, tab)
        ketten[nm] = pfad
        if len(zyklus) == 1 and zyklus[0] == nm:
            endd.append(nm)
        elif zyklus and sorted(zyklus) not in [sorted(k) for k in kreise]:
            kreise.append(zyklus)
    return {'zeichen_von': zeichen_von, 'ketten': ketten,
            'kreise': [k for k in kreise if len(k) > 1],
            'enddispositoren': sorted(endd)}


def hausherrscher(factors, cusps, aspects=None, klassisch=False):
    """Wo steht der Herrscher jedes Hauses? (Befund 5.2 des Prueflaufs.)

    Bis 2026-09-06 fragte keine Regel danach: Das Strukturbild verlangte
    Zeichenherrscher-Ketten (wer steht in wessen Zeichen), aber nicht, wo der
    Herrscher des 7., des 10. oder des 12. Hauses steht. Diese Ebene traegt in
    der klassischen wie in der psychologischen Schule einen erheblichen Teil
    der Deutung — sie sagt, wohin ein Lebensbereich seine Geschaefte auslagert.

    Rueckgabe je Haus 1..12:
        {'haus', 'spitzenzeichen', 'herrscher', 'steht_in_zeichen',
         'steht_in_haus', 'im_eigenen_haus', 'auf_winkel', 'aspekt_zur_spitze'}
    'auf_winkel' nennt den Winkel, wenn der Herrscher mit ihm in Konjunktion
    steht; 'aspekt_zur_spitze' den Aspekt zur Spitze seines eigenen Hauses,
    soweit die Achsen in `aspects` gefuehrt sind.
    """
    tab = HERRSCHER_KLASSISCH if klassisch else HERRSCHER
    pos = {f['name']: f['lon'] for f in factors}
    konj_winkel = {}
    for a in (aspects or []):
        if a['angle'] == 0:
            for x, y in ((a['a'], a['b']), (a['b'], a['a'])):
                if y in WINKEL:
                    konj_winkel.setdefault(x, []).append(y)
    out = []
    for n in range(1, 13):
        zsp = SIGN_NAMES[zeichen_index(cusps[n - 1])]
        hr = tab.get(zsp)
        eintrag = {'haus': n, 'spitzenzeichen': zsp, 'herrscher': hr,
                   'steht_in_zeichen': None, 'steht_in_haus': None,
                   'haus_spalte': None, 'grenzlage': False, 'nebenhaus': None,
                   'im_eigenen_haus': False, 'auf_winkel': None}
        if hr and hr in pos:
            hg = haus_und_grenzlage(pos[hr], cusps)
            eintrag['steht_in_zeichen'] = zeichen_name(pos[hr])
            eintrag['steht_in_haus'] = hg['haus']
            # Die Haus-Angabe traegt dieselbe Schreibweise wie die
            # Konstellationstabelle („11/12", fuehrendes Haus vorn). Ohne sie
            # stuende hier das rechnerische Haus, waehrend die Faktorenliste
            # zwei nennt — genau der Drift, den der Grenzlagen-Standard des
            # Kerns schliessen soll.
            eintrag['haus_spalte'] = haus_spalte(pos[hr], cusps)
            eintrag['grenzlage'] = hg['grenzlage']
            eintrag['nebenhaus'] = hg['nebenhaus']
            eintrag['im_eigenen_haus'] = (
                hg['haus'] == n or (hg['grenzlage'] and hg['nebenhaus'] == n))
            eintrag['auf_winkel'] = ', '.join(konj_winkel.get(hr, [])) or None
        out.append(eintrag)
    return out


def rezeptionen(factors, klassisch=False):
    """Gegenseitige und einseitige Zeichenrezeptionen (Befund 5.4).

    Gegenseitig: A steht im Zeichen, dessen Herrscher B ist, UND umgekehrt —
    die beiden tauschen ihre Wirkung aus. Einseitig: nur eine Richtung; das ist
    die haeufigere Lage und der Grund, warum Ketten ueberhaupt entstehen.
    Zusaetzlich wird gemeldet, ob eine Rezeption nur klassisch besteht.
    """
    tab = HERRSCHER_KLASSISCH if klassisch else HERRSCHER
    zv = {f['name']: zeichen_name(f['lon']) for f in factors
          if f['name'] in _PLANETEN}
    disp = {nm: tab.get(z) for nm, z in zv.items()}
    gegen, einseitig = [], []
    namen = sorted(zv)
    for i, a in enumerate(namen):
        for b in namen[i + 1:]:
            if disp.get(a) == b and disp.get(b) == a:
                gegen.append((a, b))
    for a in namen:
        b = disp.get(a)
        if b and b in zv and not any(a in p and b in p for p in gegen):
            einseitig.append((a, b))
    return {'gegenseitig': gegen, 'einseitig': einseitig, 'dispositor': disp}


def spezialfaktor_netz(factors, aspects):
    """Wie stehen Chiron, Lilith, Pholus, Glueckspunkt und die Knotenachse
    zueinander und zu den Winkeln? (Befund 5.5 des Prueflaufs.)

    In vielen Charts bilden sie ein eigenes, sehr sprechendes Netz. Das
    Regelwerk verteilte sie bis 2026-09-06 auf Themen oder ins
    Rechenschaftskapitel, ohne je zu fragen, wie sie zueinander stehen.
    Ein Spezialfaktor ganz ausserhalb dieses Netzes ist ebenso ein Befund.
    """
    vorhanden = {f['name'] for f in factors}
    spez = [s for s in SPEZIALFAKTOREN if s in vorhanden]
    untereinander, an_winkel = [], []
    beteiligt = set()
    for a in aspects:
        x, y = a['a'], a['b']
        if x in spez and y in spez:
            untereinander.append(a)
            beteiligt.update((x, y))
        elif (x in spez and y in WINKEL) or (y in spez and x in WINKEL):
            an_winkel.append(a)
            beteiligt.add(x if x in spez else y)
    return {'faktoren': spez, 'untereinander': untereinander,
            'an_winkel': an_winkel,
            'ohne_netz': [s for s in spez if s not in beteiligt]}


def konfigurationen(factors, aspects, orb_stellium_zeichen=True, cusps=None):
    """Aspektfiguren aus der fertigen Aspektliste: T-Quadrat, Grosskreuz,
    Grosstrigon, Jod, Stellium (Zeichen und Haus).

    Nur Figuren aus vollen und einseitigen Hauptaspekten; Nebenaspekte tragen
    ausschliesslich das Jod (das per Definition aus zwei Quincunxen besteht).
    """
    def paare(winkel, staerken=('voll', 'einseitig')):
        """Aspektpaare eines Winkels — OHNE Achse-Achse-Paare.

        AC/DC, MC/IC, AC/MC und ihre Kombinationen sind triviale Geometrie:
        Sie stehen in jedem Chart und ergeben sonst ein „Grosskreuz AC DC MC IC"
        und beliebig viele T-Quadrate auf der AC/DC-Opposition. Dieselbe
        Filterregel wendet das Design-Modul auf die Aspekttabelle an. Eine Figur
        MIT einem Winkel (Sonne ☍ Mond, beide im Quadrat zum AC) bleibt
        selbstverstaendlich erhalten — sie ist genau das, was Gewichtungsrang 1
        des Typmoduls sucht.
        """
        s = set()
        for a in aspects:
            if a['angle'] != winkel or a['strength'] not in staerken:
                continue
            if a['a'] in WINKEL and a['b'] in WINKEL:
                continue
            s.add(frozenset((a['a'], a['b'])))
        return s

    opp, qua, tri = paare(180), paare(90), paare(120)
    sex = paare(60, ('voll', 'einseitig', 'neben'))
    qcx = paare(150, ('voll', 'einseitig', 'neben'))
    namen = sorted({f['name'] for f in factors})
    verbunden = lambda menge, x, y: frozenset((x, y)) in menge

    tq, gk, gt, jod = [], [], [], []
    for o in opp:
        a, b = tuple(o)
        for c in namen:
            if c in (a, b):
                continue
            if verbunden(qua, a, c) and verbunden(qua, b, c):
                apex = c
                gegen = [d for d in namen if d not in (a, b, c)
                         and verbunden(opp, c, d)
                         and verbunden(qua, a, d) and verbunden(qua, b, d)]
                if gegen:
                    figur = sorted([a, b, c, gegen[0]])
                    if figur not in gk:
                        gk.append(figur)
                else:
                    eintrag = {'achse': sorted([a, b]), 'apex': apex}
                    if eintrag not in tq:
                        tq.append(eintrag)
    for i, a in enumerate(namen):
        for b in namen[i + 1:]:
            if not verbunden(tri, a, b):
                continue
            for c in namen:
                if c in (a, b):
                    continue
                if verbunden(tri, a, c) and verbunden(tri, b, c):
                    figur = sorted([a, b, c])
                    if figur not in gt:
                        gt.append(figur)
    for c in namen:
        partner = [x for x in namen if x != c and verbunden(qcx, c, x)]
        for i, a in enumerate(partner):
            for b in partner[i + 1:]:
                if verbunden(sex, a, b):
                    eintrag = {'apex': c, 'basis': sorted([a, b])}
                    if eintrag not in jod:
                        jod.append(eintrag)

    stell_z, stell_h = [], []
    if orb_stellium_zeichen:
        nach_zeichen = {}
        for f in factors:
            if f['name'] in WINKEL:
                continue
            nach_zeichen.setdefault(zeichen_name(f['lon']), []).append(f['name'])
        stell_z = [{'zeichen': z, 'faktoren': sorted(v)}
                   for z, v in sorted(nach_zeichen.items()) if len(v) >= 3]
    if cusps:
        nach_haus = {}
        for f in factors:
            if f['name'] in WINKEL:
                continue
            h = haus_und_grenzlage(f['lon'], cusps)['haus']
            nach_haus.setdefault(h, []).append(f['name'])
        stell_h = [{'haus': h, 'faktoren': sorted(v)}
                   for h, v in sorted(nach_haus.items()) if len(v) >= 3]
    return {'t_quadrat': tq, 'grosskreuz': gk, 'grosstrigon': gt, 'jod': jod,
            'stellium_zeichen': stell_z, 'stellium_haus': stell_h}


# --- Zyklusfenster: wann eine Anlage sich erfahrungsgemaess meldet -----------
#
# Chris-Entscheidung 2026-09-06 (Prueflauf, Befund 5.6): Das Geburtshoroskop
# darf sagen, in welchem Lebensalter eine Anlage erfahrungsgemaess laut wird.
# Das ist EINORDNUNG, keine Prognose — und es ist ausdruecklich KEINE
# Transitrechnung: Die Fenster unten sind die allgemeinen Zyklen, die fuer
# jeden Menschen gelten, nicht die Transite dieses Charts. Wer echte Transite
# will, macht ein Transit-Horoskop.
#
# Die Regel, unter der das steht, ist im Typmodul Geburtshoroskop und in der
# Inneren Arbeit (Prinzip 15) formuliert. Kurz: erlaubt ist „Themen, die Saturn
# fuehrt, melden sich klassisch um die neunundzwanzig\"; verboten bleibt jede
# Aussage darueber, was in diesem Alter GESCHIEHT.

ZYKLEN = {
    'Saturn': [(29.5, 'Saturn-Rückkehr'), (44.0, 'Saturn-Opposition'),
               (58.9, 'zweite Saturn-Rückkehr'), (14.7, 'erstes Saturn-Quadrat')],
    'Uranus': [(21.0, 'Uranus-Quadrat'), (42.0, 'Uranus-Opposition'),
               (63.0, 'zweites Uranus-Quadrat')],
    'Chiron': [(50.5, 'Chiron-Rückkehr')],
    'Knoten': [(18.6, 'erste Knoten-Rückkehr'), (37.2, 'zweite Knoten-Rückkehr'),
               (55.8, 'dritte Knoten-Rückkehr')],
    'Suedknoten': [(18.6, 'erste Knoten-Rückkehr'), (37.2, 'zweite Knoten-Rückkehr'),
                   (55.8, 'dritte Knoten-Rückkehr')],
    'Jupiter': [(11.9, 'Jupiter-Rückkehr'), (23.8, 'Jupiter-Rückkehr'),
                (35.7, 'Jupiter-Rückkehr'), (47.6, 'Jupiter-Rückkehr'),
                (59.5, 'Jupiter-Rückkehr')],
    'Pluto': [(38.0, 'Pluto-Quadrat (Jahrgangsschätzung, 36–45 — '
                     'wird von pluto_quadrat_alter() überschrieben)')],
}


def pluto_quadrat_alter(jd_geburt, pluto_lon, max_alter=70):
    """Alter beim ERSTEN exakten Quadrat des laufenden Pluto zum Radix-Pluto.

    Neu am 2026-09-06 (Prüfbericht EA 1.4). Der Tabellenwert in ZYKLEN ist ein
    Jahrgangsmittel und lag im Prüffall zwei Jahre daneben — er wies den
    aktuell laufenden Transit als „zurückliegend" aus. Weil Plutos Bahn stark
    exzentrisch ist, schwankt das Alter beim Quadrat je nach Radix-Position
    zwischen etwa 36 und 45 Jahren; ein Mittelwert ist dafür untauglich.

    Rechnet gegen die Ephemeride, wenn pyswisseph verfügbar ist, sonst None —
    dann gilt der Tabellenwert weiter und `strukturbild_text()` kennzeichnet ihn
    ausdrücklich als Schätzung.
    """
    try:
        import swisseph as swe
    except Exception:
        return None
    ziel_a = (pluto_lon + 90.0) % 360.0
    ziel_b = (pluto_lon - 90.0) % 360.0
    prev = {}
    schritt = 30.0                      # Tage; Pluto laeuft langsam genug
    for i in range(int(max_alter * 365.25 / schritt) + 1):
        jd = jd_geburt + i * schritt
        try:
            lo = swe.calc_ut(jd, swe.PLUTO, swe.FLG_SWIEPH)[0][0]
        except Exception:
            return None
        for lab, ziel in (('a', ziel_a), ('b', ziel_b)):
            val = ((lo - ziel + 180.0) % 360.0) - 180.0
            if prev.get(lab) is not None and prev[lab] * val < 0 \
                    and abs(prev[lab] - val) < 30:
                return round((jd - jd_geburt) / 365.25, 1)
            prev[lab] = val
    return None


def zyklusfenster(faktor, alter=None, gerechnet=None):
    """Die Lebensalter, in denen eine von `faktor` gefuehrte Anlage
    erfahrungsgemaess laut wird.

    alter: das heutige Alter der Person in Jahren (aus dem Geburtsdatum). Ist es
    angegeben, wird je Fenster vermerkt, ob es zurueckliegt, laeuft (±1,5 Jahre)
    oder noch bevorsteht — damit ein Kapitel weiss, in welcher Zeitform es
    schreibt.

    Ein Faktor ohne Eintrag liefert eine leere Liste; das ist der Normalfall
    (Sonne, Mond, Merkur, Venus, Mars, Neptun haben keinen eigenen Lebenszyklus
    dieser Art) und ausdruecklich kein Mangel.
    """
    out = []
    eintraege = sorted(ZYKLEN.get(faktor, []))
    if gerechnet and faktor in gerechnet and gerechnet[faktor] is not None:
        # Gerechneter Wert schlaegt die Jahrgangstabelle (s. pluto_quadrat_alter).
        eintraege = [(gerechnet[faktor],
                      (name.split(' (')[0] + ' (aus der Radix-Position gerechnet)')
                      if eintraege else '%s-Fenster (gerechnet)' % faktor)
                     for _j, name in (eintraege or [(None, faktor)])]
    for jahre, name in eintraege:
        lage = None
        if alter is not None:
            if abs(alter - jahre) <= 1.5:
                lage = 'läuft'
            elif alter > jahre:
                lage = 'zurückliegend'
            else:
                lage = 'bevorstehend'
        out.append({'alter': jahre, 'name': name, 'lage': lage})
    return out


def strukturbild(factors, cusps, aspects=None, zusatz=None, alter=None,
                 jd_geburt=None):
    """Alle Struktur-Befunde eines Charts in einem Aufruf.

    factors  Liste {'name','lon',...} inkl. Achsen AC/MC/DC/IC und der
             Spezialfaktoren — dieselbe Liste, die huber_aspects bekommt.
    cusps    die zwoelf selbst gerechneten Koch-Spitzen (Dezimalgrad).
    aspects  Ergebnis von huber_aspects(); wird sonst selbst gerechnet.
    zusatz   Ergebnis von zusatz_aspekte(); optional, geht nur in die Dichte ein.
    alter    heutiges Alter der Person in Jahren (fuer die Zyklusfenster).
    jd_geburt  Julianisches Datum der Geburt in UT. Nur noetig, damit das
             Pluto-Quadrat aus der Radix-Position statt aus dem Jahrgangsmittel
             gerechnet wird (s. pluto_quadrat_alter, Pruefbericht EA 1.4).
             Ohne Angabe bleibt der Tabellenwert und wird als Schaetzung
             gekennzeichnet.

    Rueckgabe: dict mit den Schluesseln verteilung_planeten, verteilung_alle,
    verteilung_gewichtet, retro, ketten, ketten_klassisch, hausherrscher,
    rezeptionen, aspektdichte, spezialnetz, konfigurationen, zyklen.
    """
    if aspects is None:
        aspects = huber_aspects(factors)
    retro = [f['name'] for f in factors if f.get('retro')]
    sb = {
        'verteilung_planeten': verteilung(factors, nur_planeten=True),
        'verteilung_alle': verteilung(factors),
        'verteilung_gewichtet': verteilung(factors, gewichtet=True),
        'retro': retro,
        'retro_persoenlich': [n for n in retro if n in ('Merkur', 'Venus', 'Mars')],
        'ketten': herrscherketten(factors),
        'ketten_klassisch': herrscherketten(factors, klassisch=True),
        'hausherrscher': hausherrscher(factors, cusps, aspects),
        'rezeptionen': rezeptionen(factors),
        'rezeptionen_klassisch': rezeptionen(factors, klassisch=True),
        'aspektdichte': aspektdichte(factors, aspects, zusatz),
        'spezialnetz': spezialfaktor_netz(factors, aspects),
        'konfigurationen': konfigurationen(factors, aspects, cusps=cusps),
        'zyklen': {},
        'alter': alter,
    }
    ger = {}
    if jd_geburt is not None:
        pl = next((f['lon'] for f in factors if f['name'] == 'Pluto'), None)
        if pl is not None:
            a = pluto_quadrat_alter(jd_geburt, pl)
            if a is not None:
                ger['Pluto'] = a
    sb['pluto_quadrat_gerechnet'] = ger.get('Pluto')
    sb['zyklen'] = {f['name']: zyklusfenster(f['name'], alter, ger)
                    for f in factors if zyklusfenster(f['name'])}
    return sb


# --- Die evolutionaere Achse (EA-Modul, Modus TIEF) --------------------------
# Neu am 2026-09-06 (Pruefbericht EA 5.1/5.2/5.3). Bis dahin wurden die sechs
# Punkte, die Knoten-Hausherrscher und die Skipped Steps in jedem EA-Lauf von
# Hand zusammengesucht; drei Ebenen fielen dabei regelmaessig aus: die Herrscher
# der beiden Knoten-HAEUSER, die Laufrichtung des Skipped Step und die
# Ruecklaeufigkeit des Radix-Pluto.

def ea_achse(factors, cusps, deckel=3.0):
    """Die sechs Punkte der evolutionaeren Achse plus Sekundaermaterial.

    Rueckgabe: dict mit
      punkte            Liste der sechs Punkte, je {nr,label,name,lon,zeichen,
                        haus_label,herrscher,retro}
      haus_herrscher    {'nordknoten': …, 'suedknoten': …} — wer das HAUS des
                        jeweiligen Knotens regiert und wo er steht
      skipped           Liste {name,lon,orb,richtung,ueber_deckel} — Quadrate zur
                        Knotenachse; `richtung` sagt, ob der Planet auf den
                        Nord- oder auf den Suedknoten zulaeuft (applikativ), was
                        ueber Wiederholung vs. Vermeidung entscheidet
      knoten_konj       Faktoren in Konjunktion zu einem Knoten (Orb <= 8°)
      pluto_aspekte     alle Kontakte zum Radix-Pluto
    """
    by = {f['name']: f for f in factors}
    def sep(a, b): return abs(((a - b + 180) % 360) - 180)
    nk = by['Mondknoten']['lon']
    sk = (nk + 180) % 360
    pl = by['Pluto']['lon']
    ppp = (pl + 180) % 360

    def herrscher_von(lon, klassisch=False):
        tab = HERRSCHER_KLASSISCH if klassisch else HERRSCHER
        return tab[zeichen_name(lon)]

    def punkt(nr, label, name, lon, retro=None):
        hg = haus_und_grenzlage(lon, cusps)
        return {'nr': nr, 'label': label, 'name': name, 'lon': lon,
                'zeichen': zeichen_name(lon), 'haus_label': hg['label'],
                'haus': hg['haus'], 'nebenhaus': hg.get('nebenhaus'),
                'herrscher': herrscher_von(lon),
                'herrscher_klassisch': herrscher_von(lon, True),
                'retro': retro}

    sk_h = herrscher_von(sk)
    nk_h = herrscher_von(nk)
    punkte = [
        punkt(1, 'Pluto', 'Pluto', pl, by['Pluto'].get('retro')),
        punkt(2, 'Südknoten', 'Südknoten', sk, by['Mondknoten'].get('retro')),
        punkt(3, 'Südknoten-Herrscher', sk_h, by[sk_h]['lon'],
              by[sk_h].get('retro')),
        punkt(4, 'Pluto-Polaritätspunkt', 'Pluto-Polaritätspunkt', ppp, None),
        punkt(5, 'Nordknoten', 'Mondknoten', nk, by['Mondknoten'].get('retro')),
        punkt(6, 'Nordknoten-Herrscher', nk_h, by[nk_h]['lon'],
              by[nk_h].get('retro')),
    ]

    # Haus-Herrscher der beiden Knotenhaeuser (Green liest sie mit)
    hh = hausherrscher(factors, cusps)
    def hh_fuer(lon):
        h = haus_und_grenzlage(lon, cusps)['haus']
        for e in hh:
            if e.get('haus') == h:
                return e
        return None
    haus_h = {'nordknoten': hh_fuer(nk), 'suedknoten': hh_fuer(sk)}

    # Skipped Steps mit Laufrichtung
    skipped = []
    for f in factors:
        nm = f['name']
        if nm in ('Mondknoten', 'AC', 'MC', 'DC', 'IC'):
            continue
        d = min(sep(f['lon'], (nk + 90) % 360), sep(f['lon'], (nk + 270) % 360))
        if d <= deckel + 2.0:
            # applikativ wohin? Kuerzerer Weg im Tierkreis entscheidet.
            zu_nk, zu_sk = sep(f['lon'], nk), sep(f['lon'], sk)
            richtung = ('Nordknoten' if zu_nk < zu_sk else 'Südknoten')
            skipped.append({'name': nm, 'lon': f['lon'], 'orb': d,
                            'richtung': richtung,
                            'ueber_deckel': d > deckel})
    skipped.sort(key=lambda x: x['orb'])

    knoten_konj = []
    for f in factors:
        if f['name'] == 'Mondknoten':
            continue
        for knoten, knm in ((nk, 'Nordknoten'), (sk, 'Südknoten')):
            d = sep(f['lon'], knoten)
            if d <= 8.0:
                knoten_konj.append({'name': f['name'], 'knoten': knm, 'orb': d})

    return {'punkte': punkte, 'haus_herrscher': haus_h, 'skipped': skipped,
            'knoten_konj': knoten_konj,
            'pluto_retro': bool(by['Pluto'].get('retro')),
            'nordknoten_lon': nk, 'suedknoten_lon': sk, 'ppp_lon': ppp}


def ea_achse_text(ea):
    """Der fertige Abschnitt `## Die evolutionäre Achse` fuers chart_data.md."""
    def gr(lon):
        g = lon % 30
        return '%d°%02d′ %s' % (int(g), round((g - int(g)) * 60), zeichen_name(lon))
    L = ['## Die evolutionäre Achse — das Rückgrat (Modus TIEF)', '',
         'Gerechnet mit `radix.ea_achse()`. Alle sechs Punkte sind '
         'Deckungsauftrag, nicht Gliederung.', '',
         '| # | Punkt | Stand | Haus | Herrscher | R |',
         '|---|---|---|---|---|---|']
    for p in ea['punkte']:
        L.append('| %d | **%s** | %s | %s | %s | %s |'
                 % (p['nr'], p['label'], gr(p['lon']), p['haus_label'],
                    p['herrscher'], 'R' if p['retro'] else '—'))
    L.append('')
    L.append('**Herrscher der Knoten-Häuser** (Green liest sie zusätzlich zu den '
             'Zeichenherrschern):')
    for k, e in ea['haus_herrscher'].items():
        if e:
            L.append('- %s-Haus %s (%s) → %s in %s, Haus %s'
                     % ('Nordknoten' if k == 'nordknoten' else 'Südknoten',
                        e.get('haus'), e.get('spitzenzeichen'),
                        e.get('herrscher'), e.get('steht_in_zeichen'),
                        e.get('haus_spalte')))
    L.append('')
    L.append('**Skipped Steps** (Quadrate zur Knotenachse, Deckel %s°):'
             % '3')
    if not ea['skipped']:
        L.append('- keine.')
    for sp in ea['skipped']:
        L.append('- %s, %s, Orb %d°%02d′ — läuft auf den %s zu%s'
                 % (sp['name'], gr(sp['lon']), int(sp['orb']),
                    round((sp['orb'] - int(sp['orb'])) * 60), sp['richtung'],
                    ' · ÜBER DEM DECKEL, Aufnahme begründen'
                    if sp['ueber_deckel'] else ''))
    L.append('')
    L.append('**Radix-Pluto ist %s.** %s'
             % ('rückläufig' if ea['pluto_retro'] else 'direktläufig',
                'Eigener Befund der evolutionären Lesart: das Wandlungsgeschehen '
                'ist stark nach innen gerichtet und meldet sich seltener über '
                'äußere Anlässe.' if ea['pluto_retro'] else ''))
    L.append('')
    return '\n'.join(L) + '\n'


def _vert_zeile(v):
    el = ' · '.join(f"{k} {v['elemente'][k]:g}" for k in _ELEM_NAMES)
    mo = ' · '.join(f"{k} {v['modi'][k]:g}" for k in _MODUS_NAMES)
    return el, mo


def strukturbild_text(sb):
    """Der fertige `## Strukturbild`-Abschnitt fuers chart_data.md.

    Schreibt AUSSCHLIESSLICH Befunde, keine Deutung — die kommt in Schritt 2.
    Die Befundzeilen, die das Datenblatt-Modul verlangt, sind als „Befund:\"
    ausgewiesen und dort von Hand zu vervollstaendigen, wo sie eine Aussage
    ueber die Person und nicht ueber die Zahl treffen.
    """
    L = ['## Strukturbild', '']

    L.append('### 1 · Elemente und Modi')
    for titel, key in (('zehn klassische Planeten', 'verteilung_planeten'),
                       ('alle Faktoren inkl. Achsen', 'verteilung_alle'),
                       ('gewichtet (Lichter/Winkel ×2, Spezialfaktoren ×0,5)',
                        'verteilung_gewichtet')):
        v = sb[key]
        el, mo = _vert_zeile(v)
        L.append(f'- {titel}: {el} | {mo}')
    vg = sb['verteilung_gewichtet']
    vp = sb['verteilung_planeten']
    L.append(f"- Schwächstes Element: {vg['schwaechstes_element']} "
             f"(gewichtet {vg['elemente'][vg['schwaechstes_element']]:g}; "
             f"getragen von "
             f"{', '.join(vp['traeger'][vg['schwaechstes_element']]) or '—'}).")
    L.append(f"- Schwächster Modus: {vg['schwaechster_modus']} "
             f"(gewichtet {vg['modi'][vg['schwaechster_modus']]:g}).")
    if vp['schwaechstes_element'] != vg['schwaechstes_element']:
        L.append(f"- ⚠ Ungewichtet wäre {vp['schwaechstes_element']} das "
                 f"schwächste Element, gewichtet ist es "
                 f"{vg['schwaechstes_element']} — die Befundzeile richtet sich "
                 f"nach der GEWICHTETEN Zählung.")
    L.append('- Befund: <eine Zeile, was das strukturell heißt>')
    L.append('')

    L.append('### 2 · Rückläufigkeit')
    L.append(f"- Rückläufig ({len(sb['retro'])}): "
             f"{', '.join(sb['retro']) or 'keiner'}.")
    L.append(f"- davon persönliche Planeten: "
             f"{', '.join(sb['retro_persoenlich']) or 'keiner'}.")
    L.append('- Befund: <eine Zeile>')
    L.append('')

    L.append('### 3 · Herrscherketten, Rezeption, Hausherrscher')
    k = sb['ketten']
    for kr in k['kreise']:
        L.append(f"- Geschlossener Kreis: {' → '.join(kr)} → {kr[0]}. "
                 f"Jedes Glied erbt die Bedingungen des nächsten.")
    if not k['kreise']:
        L.append('- Kein geschlossener Kreis unter den modernen Herrschern.')
    L.append(f"- Enddispositoren: {', '.join(k['enddispositoren']) or 'keiner'}.")
    kk = sb['ketten_klassisch']
    if [sorted(x) for x in kk['kreise']] != [sorted(x) for x in k['kreise']]:
        L.append(f"- Klassisch gerechnet ergibt sich ein anderes Bild: Kreise "
                 f"{kk['kreise'] or 'keine'}, Enddispositoren "
                 f"{', '.join(kk['enddispositoren']) or 'keine'}.")
    r = sb['rezeptionen']
    L.append(f"- Gegenseitige Rezeption: "
             f"{', '.join(a + '↔' + b for a, b in r['gegenseitig']) or 'keine'}.")
    rk = sb['rezeptionen_klassisch']
    nur_kl = [p for p in rk['gegenseitig'] if p not in r['gegenseitig']]
    if nur_kl:
        L.append(f"- Nur klassisch: "
                 f"{', '.join(a + '↔' + b for a, b in nur_kl)}.")
    L.append('- Hausherrscher (Spitzenzeichen → Herrscher → wo er steht):')
    for h in sb['hausherrscher']:
        mark = []
        if h['im_eigenen_haus']:
            mark.append('im eigenen Haus')
        if h['auf_winkel']:
            mark.append(f"auf {h['auf_winkel']}")
        zusatz_ = f"  ⟵ {', '.join(mark)}" if mark else ''
        L.append(f"  - Haus {h['haus']:>2} ({h['spitzenzeichen']}) → "
                 f"{h['herrscher']} in {h['steht_in_zeichen']}, Haus "
                 f"{h['haus_spalte'] or h['steht_in_haus']}{zusatz_}")
    L.append('- Befund: <die strukturelle Pointe in einer Zeile>')
    L.append('')

    L.append('### 4 · Aspektdichte je Faktor')
    ad = sb['aspektdichte']
    gw = ad['gewichtet']
    dicht = ', '.join('%s (%g)' % (n, gw[n]) for n in ad['dicht'])
    duenn = ', '.join('%s (%g)' % (n, gw[n]) for n in ad['duenn'])
    L.append('- Dicht verschaltet: %s.' % (dicht or '—'))
    L.append('- Dünn verschaltet: %s.' % (duenn or '—'))
    L.append('- Unaspektiert: %s.' % (', '.join(ad['unaspektiert']) or 'keiner'))
    if ad.get('winkel'):
        L.append('- Zum Vergleich, außer Konkurrenz (Winkel, Orb 9°): %s.'
                 % ' · '.join('%s %g' % (k, v) for k, v in ad['winkel'].items()))
    L.append('- Befund: <welche Funktionen viel Verkehr haben, welche isoliert '
             'arbeiten>')
    L.append('')

    L.append('### 5 · Das Netz der Spezialfaktoren')
    sn = sb['spezialnetz']
    if sn['untereinander']:
        for a in sn['untereinander']:
            L.append(f"- {a['a']} {a['name']} {a['b']} "
                     f"({a['strength']}, Orb {a['orb']}°)")
    else:
        L.append('- Keine Aspekte der Spezialfaktoren untereinander.')
    for a in sn['an_winkel']:
        L.append(f"- an der Achse: {a['a']} {a['name']} {a['b']} "
                 f"({a['strength']}, Orb {a['orb']}°)")
    L.append(f"- Ganz außerhalb dieses Netzes: "
             f"{', '.join(sn['ohne_netz']) or 'keiner'}.")
    L.append('')

    L.append('### 6 · Konfigurationen')
    kf = sb['konfigurationen']
    for t in kf['t_quadrat']:
        L.append(f"- T-Quadrat: {' ☍ '.join(t['achse'])}, Brennpunkt "
                 f"{t['apex']}")
    for g in kf['grosskreuz']:
        L.append(f"- Großkreuz: {', '.join(g)}")
    for g in kf['grosstrigon']:
        L.append(f"- Großtrigon: {', '.join(g)}")
    for j in kf['jod']:
        L.append(f"- Jod: Basis {' ⚹ '.join(j['basis'])}, Spitze {j['apex']}")
    z_gruppen = [tuple(s['faktoren']) for s in kf['stellium_zeichen']]
    for s in kf['stellium_zeichen']:
        L.append(f"- Stellium in {s['zeichen']}: {', '.join(s['faktoren'])}")
    for s in kf['stellium_haus']:
        # Ein Zeichen-Stellium liegt haeufig ganz in einem Haus. Beide Zeilen
        # ungekennzeichnet nebeneinander lesen sich als ZWEI Befunde und
        # verdoppeln das Gewicht einer einzigen Haeufung.
        doppelt = (' — dieselbe Gruppe wie das Zeichen-Stellium, EIN Befund'
                   if tuple(s['faktoren']) in z_gruppen else '')
        L.append(f"- Stellium in Haus {s['haus']}: "
                 f"{', '.join(s['faktoren'])}{doppelt}")
    if not any(kf.values()):
        L.append('- Keine Aspektfigur und kein Stellium.')
    L.append('')

    if sb['zyklen']:
        L.append('### 7 · Zyklusfenster (Einordnung, keine Prognose)')
        if sb['alter'] is not None:
            L.append(f"- Alter der Person: {sb['alter']:g} Jahre.")
        for nm, fenster in sorted(sb['zyklen'].items()):
            teile = []
            for f in fenster:
                lage = f" [{f['lage']}]" if f['lage'] else ''
                teile.append(f"{f['name']} ~{f['alter']:g}{lage}")
            L.append(f"  - {nm}: " + ' · '.join(teile))
        L.append('- Verwendung s. Typmodul, Bewegung 7. Erlaubt ist die '
                 'Einordnung, verboten jede Aussage darüber, was in diesem '
                 'Alter geschieht.')
        L.append('')
    return '\n'.join(L)


# --- Selbsttest (neutrales Demo-Chart, KEINE Klientendaten) -----------------

if __name__ == '__main__':
    _c = [i * 30.0 for i in range(12)]
    assert haus_und_grenzlage(28.0, _c)['grenzlage'] is True
    assert haus_und_grenzlage(28.0, _c)['nebenhaus'] == 2
    assert haus_und_grenzlage(15.0, _c)['grenzlage'] is False
    assert haus_und_grenzlage(15.0, _c)['haus'] == 1
    assert haus_und_grenzlage(359.0, _c)['nebenhaus'] == 1
    assert haus_und_grenzlage(25.0, _c)['grenzlage'] is True
    assert haus_spalte(15.0, _c) == '1'
    assert haus_spalte(28.5, _c) == '2/1'      # 1°30' vor Spitze -> Nebenhaus fuehrt
    assert haus_spalte(26.5, _c) == '1/2'      # 3°30' vor Spitze -> rechnerisch fuehrt
    print('Grenzlage-Test:', haus_und_grenzlage(28.0, _c)['label'],
          '| Spalte:', haus_spalte(28.5, _c))

    # --- Strukturbild gegen ein anonymes Pruefchart (nur Gradzahlen; kein
    # Name, kein Datum, keine Zeit, kein Ort — Datenschutz-Guardrail) --------
    _cu = [131.0, 158.0, 190.0, 226.0, 262.0, 296.0,
           311.0, 338.0, 10.0, 46.0, 82.0, 116.0]
    _f = [{'name': 'Sonne', 'lon': 112.5}, {'name': 'Mond', 'lon': 195.2},
          {'name': 'Merkur', 'lon': 128.9, 'retro': True},
          {'name': 'Venus', 'lon': 93.4}, {'name': 'Mars', 'lon': 298.7},
          {'name': 'Jupiter', 'lon': 340.1},
          {'name': 'Saturn', 'lon': 112.9, 'retro': True},
          {'name': 'Uranus', 'lon': 262.3, 'retro': True},
          {'name': 'Neptun', 'lon': 273.8, 'retro': True},
          {'name': 'Pluto', 'lon': 215.6, 'retro': True},
          {'name': 'Knoten', 'lon': 318.4}, {'name': 'Chiron', 'lon': 64.2},
          {'name': 'Lilith', 'lon': 7.9}, {'name': 'Pholus', 'lon': 348.5},
          {'name': 'Glueckspunkt', 'lon': 213.7},
          {'name': 'AC', 'lon': 131.0}, {'name': 'MC', 'lon': 46.0},
          {'name': 'DC', 'lon': 311.0}, {'name': 'IC', 'lon': 226.0}]
    _a = huber_aspects(_f)
    _sb = strukturbild(_f, _cu, _a, zusatz_aspekte(_f), alter=40)

    # Gewichtung greift: Merkur steht knapp VOR dem AC -> Haus 12 mit
    # Grenzlage nach 1; die Hausherrscher-Zeile muss das im Format der
    # Konstellationstabelle tragen, sonst driftet sie gegen die Faktorenliste.
    _hh = {h['haus']: h for h in _sb['hausherrscher']}
    assert _hh[2]['herrscher'] == 'Merkur'
    assert _hh[2]['haus_spalte'] == '12/1', _hh[2]['haus_spalte']
    assert _hh[4]['im_eigenen_haus'] is False        # Pluto in Skorpion, Haus 3
    assert _hh[12]['herrscher'] == 'Mond'

    # Keine trivialen Achsenfiguren: AC/DC/MC/IC bilden in JEDEM Chart ein
    # Grosskreuz — es darf hier nicht auftauchen.
    for _g in _sb['konfigurationen']['grosskreuz']:
        assert not all(x in ('AC', 'DC', 'MC', 'IC') for x in _g), _g
    for _t in _sb['konfigurationen']['t_quadrat']:
        assert not all(x in ('AC', 'DC', 'MC', 'IC') for x in _t['achse']), _t

    # Winkel stehen nicht in der Dichte-Rangliste (Orb 9 -> bauartbedingt vorn)
    for _w in ('AC', 'MC', 'DC', 'IC'):
        assert _w not in _sb['aspektdichte']['dicht']
    assert 'AC' in _sb['aspektdichte']['winkel']

    # Gegenseitige Rezeption Mond<->Venus (Mond in Waage, Venus in Krebs)
    assert ('Mond', 'Venus') in _sb['rezeptionen']['gegenseitig']

    # Gewichtete Zaehlung unterscheidet sich von der ungewichteten
    assert _sb['verteilung_gewichtet']['elemente'] != \
        _sb['verteilung_planeten']['elemente']

    # Zyklusfenster: Lage relativ zum Alter
    _z = zyklusfenster('Saturn', alter=40)
    assert [x['lage'] for x in _z] == ['zurückliegend', 'zurückliegend',
                                       'bevorstehend', 'bevorstehend'], _z
    assert zyklusfenster('Venus') == []          # kein eigener Lebenszyklus

    _txt = strukturbild_text(_sb)
    assert '## Strukturbild' in _txt and 'Hausherrscher' in _txt
    print('Strukturbild-Test: OK —', len(_txt), 'Zeichen,',
          len(_sb['hausherrscher']), 'Hausherrscher,',
          len(_sb['konfigurationen']['t_quadrat']), 'T-Quadrate')
