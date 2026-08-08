#!/usr/bin/env python3
"""
radix.py — selbst gezeichnetes Chart-Rad (Radix) für die Horoskop-Pipeline.

Zweck: Das Rad auf Seite 1 des Horoskops wird NICHT mehr aus einem fremden
PDF (astroschmid) eingebettet, sondern hier aus den bereits berechneten
Chart-Daten selbst gezeichnet. Vorteil: Das Rad zeigt exakt dieselben
Huber-Aspekte wie die Aspekttabelle (beide speisen sich aus `huber_aspects`),
ist vektorscharf, im Cover-Stil einfärbbar und quellen-unabhängig.

Drei öffentliche Funktionen:

    huber_aspects(factors, orbs=None) -> list
        Berechnet die Aspekte nach Huber-Orbis (planetenindividuell). DIESELBE
        Liste speist Rad UND Aspekttabelle -> beide sind garantiert deckungsgleich.

    haus_und_grenzlage(lon, cusps, orb=5) -> dict
        Haupthaus + Grenzlage eines Faktors nach der einheitlichen 5°-Haus-Regel
        (zweite, von den Aspekt-Orben STRIKT getrennte Orb-Ebene).

    radix(factors, cusps, asc, mc, out_path=..., title=..., aspects=None,
          palette=None, gradmarke=True) -> str
        Zeichnet das Rad als PNG und gibt den Pfad zurück.

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
