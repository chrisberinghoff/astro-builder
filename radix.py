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

    strukturbild(factors, cusps, aspects=None, zusatz=None, alter=None,
                 jd_geburt=None) -> dict
        ALLE Struktur-Befunde in einem Aufruf: Element-/Modusverteilung in drei
        Zählungen (auch gewichtet), Rückläufigkeit, Herrscherketten mit Kreisen
        und Enddispositoren, HAUSHERRSCHER, Rezeptionen, Aspektdichte je Faktor,
        das Netz der Spezialfaktoren, Aspektfiguren, Zyklusfenster — und seit
        dem 2026-09-08 (zweiter Durchgang) das VERTEILUNGSMUSTER (Hemisphären,
        Quadranten, Jones-Muster) und die MONDPHASE.
        strukturbild_text(sb) schreibt daraus den fertigen `## Strukturbild`-
        Abschnitt fürs chart_data.md (neun Unterpunkte). Eingeführt 2026-09-06
        (Prüfbericht 5.1–5.6); bis dahin wurde das alles von Hand gerechnet,
        und vier Ebenen fehlten ganz, weil keine Regel nach ihnen fragte.

    konfigurationen(factors, aspects, cusps=None) -> dict
    gruppiere_figuren(konf, aspects) -> dict      (Achsen-Doppelung, 2026-09-09)
    glueckspunkt(factors, cusps) -> dict          (Tag/Nacht selbst, 2026-09-09)
        T-Quadrat (mit leerer Spitze), Großkreuz, Großtrigon, Jod, Stellium —
        und seit 2026-09-08 Drachen (Kite) und Mystisches Rechteck. Ein Drachen
        führt sein Großtrigon selbst (EIN Befund).

    verteilungsmuster(factors, cusps=None) -> dict
        Hemisphären und Quadranten nach Häusern (Koch), Muster nach Jones
        (Bündel, Schüssel, Eimer, Lokomotive, Wippe, Streuung, Spritzer) über
        die zehn klassischen Planeten. Grenzwerte: Konstanten MUSTER_* / HENKEL_*.

    mondphase(factors) -> dict
        Winkel Sonne → Mond, Phase in den acht Stufen nach Rudhyar,
        Finsternisnähe-Flag (nur ein Flag, keine Finsternisrechnung).

    Grundsatz hinter allen dreien (Chris-Entscheidung 2026-09-08): Was das
    Strukturbild nicht ausgibt, prüft keine Gegenprobe — ein Befund, den die
    Rechnung nicht kennt, kann in der Deutung nie fehlen. Deshalb stehen die
    Dinge im Code und nicht in einer Mahnung.

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


# --- Die fertige Aspektliste fuer die Aspektseite ---------------------------
# Bis zum 2026-09-09 stand diese Mechanik als Prosa im Design-Modul und wurde
# in JEDER chart-eigenen `chartdata.aspektliste()` neu von Hand geschrieben —
# in genau der einen Datei, die je Chart neu entsteht (Pruefbericht
# Geburtshoroskop Schritt 3+4, Rubrik 5.5). Die Regel ist eine Festlegung, keine
# Ableitung, und hat keine chart-eigene Ausnahme; sie gehoert deshalb hierher.

ACHSEN_NAMEN = ('AC', 'MC', 'DC', 'IC')
_GEGENACHSE = {'AC': 'DC', 'DC': 'AC', 'MC': 'IC', 'IC': 'MC'}
_STAERKE_RANG = {'voll': 0, 'einseitig': 1, 'neben': 2}

# Welche Seite einer Achsen-Spiegelzeile vorn steht (Design-Modul, festgelegt
# 2026-09-08): Konjunktion vor Opposition; bei Quadrat/Quadrat AC vor DC und
# MC vor IC.
_FUEHRT_QUADRAT = ('AC', 'MC')


def ist_achse(name):
    return name in ACHSEN_NAMEN


def aspektliste(factors, zusatz_paare=(), zusatz_orb=2.0, orbs=None,
                sortieren=True):
    """Die Aspektliste, wie die Aspektseite sie braucht — gerechnet, nie
    abgeschrieben.

    Vier Arbeitsgaenge, alle im Design-Modul geregelt:

    1. `huber_aspects(factors)` rechnen.
    2. Die vier Achse<->Achse-Paare (AC/DC, MC/IC, AC/MC, AC/IC, MC/DC, DC/IC)
       herausfiltern — triviale Geometrie, sie gehoeren in keine Zeile.
    3. Echte Achsen-Spiegelzeilen zusammenziehen: Trifft ein Faktor beide Enden
       derselben Achse UND landen beide in derselben Staerkegruppe, steht die
       Spiegelseite als `spiegel`-Feld in Klammern statt in einer eigenen Zeile.
       Zusammengezogen wird NUR Konjunktion/Opposition und Quadrat/Quadrat;
       Trigon<->Sextil und Quincunx<->Halbsextil sind bei Huber eigene Klassen
       mit eigenen Orbis und bleiben getrennte Zeilen.
       Fuehrung: Konjunktion vor Opposition, bei Quadrat/Quadrat AC vor DC und
       MC vor IC.
    4. Bewusst aufgenommene Zusatzzeilen anhaengen (Halb-/Anderthalbquadrate
       aus dem ⚠-Block der chart_data). Sie laufen als `strength='neben'`
       (`ASP_GRUPPEN` kennt kein 'zusatz'), tragen die NEUTRALE Farbe — eine
       Radfarbe verspraeche eine Linie, die im Rad nicht gezeichnet ist — und
       werden im `spiegel`-Feld als „Zusatzebene" gekennzeichnet.

    zusatz_paare  Iterable von Namenspaaren, z. B. [('Merkur', 'Uranus')].
                  Leer = keine Zusatzebene. Die Reihenfolge im Paar ist egal.
    sortieren     nach Staerkegruppe, dann nach Orb (wie die chart_data-Tabelle).

    Rueckgabe: Liste von dicts wie `huber_aspects`, zusaetzlich mit optionalem
    `spiegel`-Feld. Ihre LAENGE ist die Sollzahl fuer `build.verify(aspect_rows=…)`.
    """
    roh = [a for a in huber_aspects(factors, orbs=orbs)
           if not (ist_achse(a['a']) and ist_achse(a['b']))]

    gewollt = {frozenset(p) for p in zusatz_paare}
    if gewollt:
        for a in zusatz_aspekte(factors, orb=zusatz_orb):
            if frozenset((a['a'], a['b'])) in gewollt:
                b = dict(a)
                b['strength'] = 'neben'
                b['color'] = 'konj'
                b['spiegel'] = 'Zusatzebene'
                roh.append(b)

    out, verbraucht = [], set()
    for i, a in enumerate(roh):
        if i in verbraucht:
            continue
        achse = (a['b'] if ist_achse(a['b'])
                 else (a['a'] if ist_achse(a['a']) else None))
        gegen = _GEGENACHSE.get(achse) if achse else None
        treffer = None
        if gegen and a['name'] in ('Konjunktion', 'Opposition', 'Quadrat'):
            faktor = a['a'] if achse == a['b'] else a['b']
            for j in range(i + 1, len(roh)):
                if j in verbraucht:
                    continue
                b = roh[j]
                if b['strength'] != a['strength']:
                    continue
                if {b['a'], b['b']} != {faktor, gegen}:
                    continue
                if a['name'] == 'Quadrat' and b['name'] == 'Quadrat':
                    treffer = (j, b)
                    break
                if {a['name'], b['name']} == {'Konjunktion', 'Opposition'}:
                    treffer = (j, b)
                    break
        if treffer is None:
            out.append(a)
            continue
        j, b = treffer
        verbraucht.add(j)
        if a['name'] == 'Quadrat':
            fuehrt, zweit = (a, b) if achse in _FUEHRT_QUADRAT else (b, a)
        else:
            fuehrt, zweit = (a, b) if a['name'] == 'Konjunktion' else (b, a)
        z_achse = zweit['b'] if ist_achse(zweit['b']) else zweit['a']
        r = dict(fuehrt)
        r['spiegel'] = f"{zweit['name']} {z_achse}"
        out.append(r)

    if sortieren:
        out.sort(key=lambda x: (_STAERKE_RANG.get(x['strength'], 9), x['orb']))
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

# Farbe der gerechneten Punkte im Rad (kein Ephemeriden-Faktor). Bewusst
# KEINE der vier Aspektfarben und nicht das Ink der Faktoren — ein gerechneter
# Punkt darf nicht wie eine Stellung aussehen. Gesetzt 2026-09-08
# (Pruefbericht EA 5c).
MARKE_FARBE = '#7d6f93'


def radix(factors, cusps, asc, mc, out_path='/home/claude/radix.png',
          title=None, aspects=None, palette=None, dpi=210, grade=False,
          gradmarke=True, marken=()):
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

    # Gerechnete Punkte — z. B. der Pluto-Polaritaetspunkt im EA. Sie sind
    # KEINE Ephemeriden-Faktoren und bekommen deshalb weder Glyphe im
    # Faktorring noch Aspektlinien, sondern einen offenen Kreis auf dem
    # Zeichenring plus einen kurzen Strich nach innen, in eigener Farbe.
    # marken = [{'lon': float, 'label': '<kurzer Text>'}, ...]
    # Die Legende MUSS sie benennen (chartdoc.linien_legende(gerechnet=...)) —
    # Klartext-Standard: jedes sichtbare Zeichen wird einmal erklaert.
    # Neu 2026-09-08 (Pruefbericht EA 5c): Der Polaritaetspunkt trug im
    # Pruefdokument Leitachse, Titelmotiv und Schlusswort und war auf keiner
    # Grafik zu sehen.
    for m in (marken or ()):
        L = float(m['lon'])
        xa, ya = xy(L, R_SIGN - 0.004)
        xb, yb = xy(L, R_SIGN - 0.052)
        ax.plot([xa, xb], [ya, yb], color=MARKE_FARBE, lw=1.0,
                ls=(0, (2.0, 1.8)), zorder=3.4)
        cx, cy = xy(L, R_SIGN - 0.070)
        ax.plot([cx], [cy], marker='o', ms=4.6, mfc='none',
                mec=MARKE_FARBE, mew=1.1, zorder=3.6)
        lab = m.get('label') or ''
        if lab:
            tx, ty = xy(L, R_SIGN - 0.138)
            ax.text(tx, ty, lab, ha='center', va='center', fontsize=6.6,
                    color=MARKE_FARBE, zorder=3.6)

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

# --- Verteilungsmuster (Jones) und Hemisphaeren: Grenzwerte -------------------
# Chris-Entscheidung 2026-09-08, zweiter Durchgang (Strukturbild-Luecken, Prompt A
# des Stilvergleichs). ALLE Werte sind Setzungen, keine Lehrbuchzahlen: Die
# Literatur (Jones 1941 und die Sekundaerquellen) nennt nur fuer die Lokomotive
# eine Toleranz (±12°) und sonst „ungefaehr". Dokumentiert im Datenblatt-Modul,
# Strukturbild §8. Wer einen Wert aendert, zieht dort nach.
#
# Gerechnet wird ausschliesslich ueber die zehn klassischen Planeten (_PLANETEN):
# keine Knoten, keine Spezialfaktoren, kein Glueckspunkt, keine Achsen.
MUSTER_BUENDEL = 120.0          # Buendel: alle Planeten innerhalb dieser Spanne
MUSTER_SCHUESSEL = 180.0        # Schuessel: innerhalb einer Haelfte
MUSTER_LOKOMOTIVE = 240.0       # Lokomotive: innerhalb zweier Drittel
                                #   (= leerer Bogen von mindestens 120°)
MUSTER_WIPPE_LUECKE = 60.0      # Wippe: zwei Luecken von je mindestens so viel,
                                #   beide Gruppen mindestens zwei Planeten
MUSTER_STREUUNG_LUECKE = 60.0   # Streuung: groesste Luecke hoechstens so gross
MUSTER_SPRITZER_LUECKE = 30.0   # Spritzer: mindestens drei Gruppen, getrennt
                                #   durch Luecken von mindestens so viel
MUSTER_TOLERANZ = 6.0           # Grenzfall: Spanne bis zu so viel ueber dem
                                #   Grenzwert -> „auch lesbar als", nie erste Wahl
HENKEL_KONJUNKTION = 8.0        # Eimer: zwei Planeten bis zu diesem Abstand
                                #   zaehlen als EIN Henkel (weitester Huber-Orb)
HENKEL_RANDABSTAND = 15.0       # Eimer: der Henkel steht mindestens so weit von
                                #   BEIDEN Raendern der Schuessel — sonst ist es
                                #   eine Schuessel mit Ueberhang, kein Eimer
HEMISPHAERE_BETONT = 7          # Befund „betont" ab so vielen von zehn
QUADRANT_BETONT = 5             # Befund „betont" ab so vielen von zehn
STELLIUM_MIN = 3                # Stellium: ab so vielen Faktoren in Zeichen/Haus
STELLIUM_MIN_PLANETEN = 2       # ... davon mindestens so viele klassische
                                #   Planeten (Spezialfaktoren zaehlen nur mit)

# Reihenfolge, in der ein Muster erste Wahl wird, wenn mehrere passen
# (das engste zuerst). Spritzer wird nie als „auch lesbar" gefuehrt — es ist
# die positiv definierte letzte Stufe vor „kein eindeutiges Muster";
# Streuung schliesst die Spannen-Muster geometrisch aus und erscheint als
# Zweitlesart nur im Grenzfall (groesste Luecke genau am Wippe-Grenzwert).
_MUSTER_RANG = ('Bündel', 'Schüssel', 'Eimer', 'Lokomotive', 'Wippe',
                'Streuung', 'Spritzer')

# Hemisphaeren und Quadranten nach HAEUSERN (Koch, wie das ganze Projekt),
# nicht nach Graden: ueber dem Horizont = Haeuser 7–12, oestlich = die
# Haeuser um den AC (10, 11, 12, 1, 2, 3). Die Spitzen von Haus 1, 4, 7 und 10
# sind AC, IC, DC und MC — genau die Grenzen der vier Hemisphaeren.
_HEMI_OBEN = (7, 8, 9, 10, 11, 12)
_HEMI_OST = (10, 11, 12, 1, 2, 3)
_QUADRANT_VON_HAUS = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2,
                      7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}
_WINKEL_HINTER_HAUS = {12: 'AC', 3: 'IC', 6: 'DC', 9: 'MC'}   # Spitze, die folgt

# --- Mondphase: die acht Stufen nach Rudhyar --------------------------------
# Je 45°, beginnend bei 0° (Winkel Sonne -> Mond, gegen den Uhrzeigersinn).
MONDPHASEN = ('Neumond', 'zunehmende Sichel', 'erstes Viertel',
              'zunehmender Dreiviertelmond', 'Vollmond',
              'abnehmender Dreiviertelmond', 'letztes Viertel', 'Balsamisch')
MONDPHASE_SCHRITT = 45.0
FINSTERNIS_SYZYGIE_ORB = 8.0    # Lichter in Konjunktion/Opposition bis zu diesem
                                #   Orb (= Huber-Orb der Lichter, s. HUBER_ORB)
FINSTERNIS_KNOTEN_ORB = 15.0    # ... UND ein Licht so nah an der Knotenachse:
                                #   Finsternisnaehe. Ein Flag, keine Rechnung —
                                #   die echten Grenzen liegen bei ~18° (Sonne)
                                #   und ~12° (Mond) und braeuchten die Mondbreite.


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


def glueckspunkt(factors, cusps, ac=None, sonne=None, mond=None):
    """Glueckspunkt (Pars Fortunae) mit eingebauter Tag-/Nacht-Entscheidung.

    Tagformel   AC + Mond − Sonne  (Sonne UEBER dem Horizont, Haeuser 7–12)
    Nachtformel AC + Sonne − Mond  (Sonne UNTER dem Horizont, Haeuser 1–6)

    Neu am 2026-09-09 (Pruefbericht Geburtshoroskop, 5.9). Bis dahin stand nur
    die Formel im Datenblatt-Modul und wurde in jedem Lauf von Hand gerechnet —
    mit zwei Fallen: dem Vorzeichenwechsel zwischen beiden Formeln und der
    Frage, woran „Tag" haengt. Es haengt am HAUS der Sonne (7–12 = ueber dem
    Horizont), nicht an der Uhrzeit: Dieselbe Abenduhrzeit liegt im Sommer
    noch im Tagbogen und im Winter laengst nicht mehr.

    -> {'lon', 'tag', 'sonne_haus', 'formel'}
    """
    lon = {f['name']: f['lon'] for f in factors}
    ac = lon['AC'] if ac is None else ac
    sonne = lon['Sonne'] if sonne is None else sonne
    mond = lon['Mond'] if mond is None else mond
    h = haus_und_grenzlage(sonne, cusps)['haus']
    tag = 7 <= h <= 12
    p = (ac + mond - sonne) % 360.0 if tag else (ac + sonne - mond) % 360.0
    return {'lon': p, 'tag': tag, 'sonne_haus': h,
            'formel': 'AC + Mond − Sonne (Tagformel)' if tag
                      else 'AC + Sonne − Mond (Nachtformel)'}


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


def leere_spitze(apex_lon, factors, cusps=None, orb=HAUS_ORB,
                 apex_name=None, aspects=None):
    """Die leere Spitze eines T-Quadrats: der Punkt GEGENUEBER dem Brennpunkt.

    Ein T-Quadrat ist ein Grosskreuz, dem eine Ecke fehlt. Diese fehlende
    Ecke — Zeichen und Haus des Punktes 180 Grad gegenueber dem Apex — ist in
    der Deutung die Richtung, in der die Figur entlastet wird: die Qualitaet,
    die dem Spannungsdreieck fehlt und die es ins Gleichgewicht braechte.
    Bis zum 2026-09-08 lieferte `konfigurationen()` nur Achse und Apex; die
    leere Spitze musste im Kopf gerechnet werden und fiel in der Deutung
    regelmaessig weg (Befund Stilvergleich 2026-09-08, Chris-Entscheidung:
    Figur-Regel des Typmoduls Geburtshoroskop). Was nicht gerechnet vorliegt,
    wird nicht gedeutet — deshalb steht sie jetzt im Strukturbild.

    Rueckgabe: {'lon', 'zeichen', 'haus', 'haus_spalte', 'besetzt'} —
    `besetzt` sind die Faktoren (auch Achsen), die innerhalb von `orb` Grad
    auf der leeren Spitze stehen, je mit ihrem Abstand. Steht dort etwas
    (typisch: ein Knoten, eine Achse, ein Spezialfaktor), ist die Spitze nicht
    wirklich leer, und genau das ist der Befund. Der Orb ist bewusst der
    Haus-Orb (5 Grad), kein Aspekt-Orb: Es geht um die Nachbarschaft zu einem
    Punkt, nicht um einen Aspekt. ZUSAETZLICH zaehlt jeder Faktor als
    besetzt, der laut Aspektliste in Opposition zum Apex steht — er sitzt per
    Definition auf der leeren Spitze, auch wenn er (mit dem groesseren
    Huber-Orb der Lichter) mehr als 5 Grad entfernt ist. Dafuer `apex_name`
    und `aspects` mitgeben; `konfigurationen()` tut das selbst.
    """
    lon = (apex_lon + 180.0) % 360
    out = {'lon': round(lon, 2), 'zeichen': zeichen_name(lon), 'haus': None,
           'haus_spalte': None, 'besetzt': []}
    if cusps:
        out['haus'] = haus_und_grenzlage(lon, cusps)['haus']
        out['haus_spalte'] = haus_spalte(lon, cusps)
    per_opposition = set()
    if apex_name and aspects:
        for a in aspects:
            if a.get('angle') != 180:
                continue
            if a['a'] == apex_name:
                per_opposition.add(a['b'])
            elif a['b'] == apex_name:
                per_opposition.add(a['a'])
    for f in factors:
        d = abs((f['lon'] - lon + 180.0) % 360 - 180.0)
        if d <= orb or f['name'] in per_opposition:
            out['besetzt'].append({'name': f['name'], 'orb': round(d, 2)})
    out['besetzt'].sort(key=lambda x: x['orb'])
    return out


def konfigurationen(factors, aspects, orb_stellium_zeichen=True, cusps=None):
    """Aspektfiguren aus der fertigen Aspektliste: T-Quadrat, Grosskreuz,
    Grosstrigon, Jod, Stellium (Zeichen und Haus) — und seit dem 2026-09-08
    (zweiter Durchgang) DRACHEN und MYSTISCHES RECHTECK.

    Jeder T-Quadrat-Eintrag traegt seit dem 2026-09-08 zusaetzlich
    `leere_spitze` (s. `leere_spitze()`): Zeichen, Haus und was dort steht.

    Drachen (Kite): ein Grosstrigon plus ein Faktor (der Kopf) in Opposition zu
    einer Ecke und im Sextil zu den beiden anderen. Eintrag: {'trigon',
    'kopf', 'achse' (Kopf ☍ Ecke), 'sextile'}. EIN-Befund-Regel: Ein Drachen
    fuehrt sein Grosstrigon selbst — das Trigon erscheint dann NICHT mehr in
    'grosstrigon', genauso wie ein T-Quadrat nicht neben seinem Grosskreuz
    steht. Tragen zwei Koepfe dasselbe Trigon, gibt es zwei Drachen-Eintraege
    mit demselben 'trigon'.

    Mystisches Rechteck: zwei Oppositionen, deren Enden durch zwei Trigone und
    zwei Sextile (abwechselnd) verbunden sind. Eintrag: {'achsen', 'trigone',
    'sextile'}. Alle vier Seiten muessen im Orb stehen; bei drei von vier ist
    es kein Rechteck (und wird nicht „grosszuegig" gemeldet).

    Staerken: Oppositionen und Trigone voll oder einseitig; Sextile als
    Nebenaspekt (Orb 6°) — dieselben Staerken, die das Jod schon benutzt.

    Nur Figuren aus vollen und einseitigen Hauptaspekten; Nebenaspekte tragen
    ausschliesslich Jod, Drachen und Rechteck (ueber ihre Sextile). Der
    Winkel-Ausschluss von `paare()` (kein Achse-Achse-Paar) greift fuer die
    neuen Figuren genauso: Ein Drachen mit AC in der Basis und DC als Kopf und
    ein Rechteck auf der AC/DC- oder MC/IC-Achse werden nicht gemeldet, weil
    ihre tragende Opposition triviale Geometrie waere.
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
    lon_of = {f['name']: f['lon'] for f in factors}
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
                    eintrag = {'achse': sorted([a, b]), 'apex': apex,
                               'leere_spitze': leere_spitze(
                                   lon_of[apex], factors, cusps,
                                   apex_name=apex, aspects=aspects)}
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

    # Drachen: Grosstrigon + Kopf in Opposition zu EINER Ecke und im Sextil zu
    # den beiden anderen. Das Trigon wandert aus der Grosstrigon-Liste in den
    # Drachen (EIN Befund) — Datenebene, nicht nur Textzeile, damit auch die
    # Synthese-Gegenprobe (a) einen Befund sieht und nicht zwei.
    drachen = []
    for trig in gt:
        for kopf in namen:
            if kopf in trig:
                continue
            for ecke in trig:
                if not verbunden(opp, ecke, kopf):
                    continue
                andere = [x for x in trig if x != ecke]
                if all(verbunden(sex, kopf, x) for x in andere):
                    eintrag = {'trigon': list(trig), 'kopf': kopf,
                               'achse': [kopf, ecke],
                               'sextile': [[kopf, x] for x in andere]}
                    if eintrag not in drachen:
                        drachen.append(eintrag)
    getragen = [d['trigon'] for d in drachen]
    gt = [t for t in gt if t not in getragen]

    # Mystisches Rechteck: zwei Oppositionen ohne gemeinsamen Faktor, deren
    # vier Seiten abwechselnd Trigon und Sextil sind. Geometrisch folgt aus
    # a ☍ c und b ☍ d, dass a–b und c–d denselben Winkel haben (und b–c, d–a den
    # Gegenwinkel) — mit Orben kann eine Seite trotzdem herausfallen, dann ist
    # es kein Rechteck.
    def _seite(x, y):
        if verbunden(tri, x, y):
            return 'Trigon'
        if verbunden(sex, x, y):
            return 'Sextil'
        return None

    rechteck = []
    opps = sorted(sorted(o) for o in opp)
    for i, o1 in enumerate(opps):
        for o2 in opps[i + 1:]:
            if set(o1) & set(o2):
                continue
            a, c = o1
            b, d = o2
            seiten = [(a, b), (b, c), (c, d), (d, a)]
            typen = [_seite(x, y) for x, y in seiten]
            if None in typen:
                continue
            if typen[0] == typen[2] and typen[1] == typen[3] \
                    and typen[0] != typen[1]:
                eintrag = {
                    'achsen': [list(o1), list(o2)],
                    'trigone': [sorted(s) for s, t in zip(seiten, typen)
                                if t == 'Trigon'],
                    'sextile': [sorted(s) for s, t in zip(seiten, typen)
                                if t == 'Sextil']}
                if eintrag not in rechteck:
                    rechteck.append(eintrag)

    # Stellium: mindestens STELLIUM_MIN Faktoren in einem Zeichen bzw. Haus,
    # darunter mindestens STELLIUM_MIN_PLANETEN klassische Planeten (seit
    # 2026-09-08, zweiter Durchgang). Vorher zaehlten alle Nicht-Winkel-
    # Faktoren gleich, und drei Spezialfaktoren (Knoten, Chiron, Lilith) in
    # einem Haus ergaben ein „Stellium" ohne einen einzigen Planeten — eine
    # Verdichtung, in der niemand die Hand heben kann (Figur-Regel, Stellium).
    # Spezialfaktoren zaehlen weiter MIT, sobald zwei Planeten dabei sind.
    def _stellium(gruppe):
        return (len(gruppe) >= STELLIUM_MIN and
                sum(1 for x in gruppe if x in _PLANETEN) >= STELLIUM_MIN_PLANETEN)

    stell_z, stell_h = [], []
    if orb_stellium_zeichen:
        nach_zeichen = {}
        for f in factors:
            if f['name'] in WINKEL:
                continue
            nach_zeichen.setdefault(zeichen_name(f['lon']), []).append(f['name'])
        stell_z = [{'zeichen': z, 'faktoren': sorted(v)}
                   for z, v in sorted(nach_zeichen.items()) if _stellium(v)]
    if cusps:
        nach_haus = {}
        for f in factors:
            if f['name'] in WINKEL:
                continue
            h = haus_und_grenzlage(f['lon'], cusps)['haus']
            nach_haus.setdefault(h, []).append(f['name'])
        stell_h = [{'haus': h, 'faktoren': sorted(v)}
                   for h, v in sorted(nach_haus.items()) if _stellium(v)]
    return {'t_quadrat': tq, 'grosskreuz': gk, 'grosstrigon': gt, 'jod': jod,
            'drachen': drachen, 'rechteck': rechteck,
            'stellium_zeichen': stell_z, 'stellium_haus': stell_h}


# --- Verteilungsmuster: Hemisphaeren, Quadranten, Jones-Muster ---------------
# Neu am 2026-09-08, zweiter Durchgang (Chris-Entscheidung; Befund Stilvergleich
# §7, Prompt A). Bis dahin rechnete das Strukturbild keine Verteilung — und was
# es nicht rechnete, konnte in der Deutung nie fehlen. Grenzwerte: s. die
# MUSTER_*- und HENKEL_*-Konstanten oben, dokumentiert im Datenblatt-Modul §8.
#
# ZUR LOKOMOTIVE UND IHREM „LOKFUEHRER" — die Quellen sind uneins, und zwar
# woertlich: „der erste Planet im Uhrzeigersinn nach der Luecke" (Kerykeion,
# Great Almanac) meint den Planeten, der dem leeren Bogen im Tierkreis
# VORAUSGEHT; „der Planet, der die Gruppe in der taeglichen Drehung anfuehrt"
# (Understanding Astrology, auf Jones zurueckgefuehrt) meint den, der dem
# leeren Bogen im Tierkreis FOLGT — er ist der erste, der nach acht Stunden
# Leere ueber den Horizont steigt; eine Quelle (Esoteric Meanings) schreibt
# sogar „gegen den Uhrzeigersinn". Diese Funktion legt sich deshalb NICHT
# fest: Sie gibt beide Randplaneten mit geometrischen Namen aus —
#   'rand_nach_luecke' = der Planet, an dem der leere Bogen (in
#                        Tierkreisrichtung gezaehlt) ENDET; er folgt der Luecke
#   'rand_vor_luecke'  = der Planet, hinter dem der leere Bogen BEGINNT
# Die Deutungsregel (Typmodul Geburtshoroskop, Getriebe-Kapitel) entscheidet,
# welcher fuehrt. Sie liest seit dem 2026-09-08 'rand_nach_luecke' als
# Lokfuehrer und 'rand_vor_luecke' als Schlusslicht — nach ueberwiegender
# Lesart Jones' Bild von der taeglichen Drehung; als Zitat ist das nicht
# gesichert, deshalb steht es hier als Konvention und nicht als Faktum.

def _winkelabstand(a, b):
    """Kleinster Winkel zwischen zwei Laengen, 0..180."""
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _bogen_daten(pts):
    """Luecken und Spanne einer sortierten Punktliste [(lon, name), ...].

    Rueckgabe: (luecken, groesste, spanne) — luecken je {'von','bis','grad'} in
    Tierkreisrichtung (von -> bis = zunehmende Laenge), groesste = die groesste
    Luecke, spanne = 360 - groesste (der kleinste Bogen, der alle Punkte traegt).
    """
    n = len(pts)
    luecken = []
    for i in range(n):
        lon_i, nm_i = pts[i]
        lon_j, nm_j = pts[(i + 1) % n]
        g = (lon_j - lon_i) % 360.0 if n > 1 else 360.0
        luecken.append({'von': nm_i, 'bis': nm_j, 'grad': round(g, 2),
                        'von_lon': lon_i, 'bis_lon': lon_j})
    groesste = max(luecken, key=lambda x: x['grad'])
    return luecken, groesste, round(360.0 - groesste['grad'], 2)


def _gruppen(pts, min_luecke):
    """Zerlegt die sortierten Punkte an jeder Luecke >= min_luecke in Gruppen.

    Rueckgabe: Liste von Gruppen (je Liste von Namen, in Tierkreisrichtung),
    beginnend hinter der groessten Luecke.
    """
    luecken, groesste, _ = _bogen_daten(pts)
    n = len(pts)
    start = (luecken.index(groesste) + 1) % n
    gruppen, aktuell = [], []
    for k in range(n):
        idx = (start + k) % n
        aktuell.append(pts[idx][1])
        if luecken[idx]['grad'] >= min_luecke or k == n - 1:
            gruppen.append(aktuell)
            aktuell = []
    if aktuell:
        gruppen.append(aktuell)
    return gruppen


def gruppiere_figuren(konf, aspects, konj_orb_namen=None):
    """Fasst mehrfach gemeldete T-Quadrate zu Figuren zusammen.

    Neu am 2026-09-09 (Pruefbericht Geburtshoroskop, 5.7). `konfigurationen()`
    meldet jede Figur einmal je Endpunkt-Kombination. Steht ein Planet in
    Konjunktion zu einem Winkel, erscheint dasselbe Dreieck deshalb mehrfach —
    im Pruefall SIEBEN Meldungen fuer VIER Figuren. Das Datenblatt-Modul
    verlangte dafuer bis dahin Handarbeit („vor der Deutung zusammenfassen und
    im chart_data sagen, wie viele Figuren es tatsaechlich sind"), und
    Handarbeit an dieser Stelle ist eine Fehlerquelle in jedem Chart mit
    Planeten auf Winkeln — also in der Mehrheit.

    Die Funktion GRUPPIERT, sie ENTSCHEIDET NICHT. Zwei Regeln:

    HART — dieselbe Figur: gleicher Apex, und die beiden Achsenenden sind
    paarweise identisch oder durch eine Konjunktion verbunden. Das ist die
    reine Achsen-Doppelung; sie wird zusammengefasst.

    WEICH — Kandidat: gleicher Apex und ein gemeinsames Achsenende, aber die
    zweiten Enden sind weder identisch noch konjunkt. Ob das EINE Figur mit
    zwei dicht benachbarten Enden ist oder ZWEI Figuren, haengt vom Abstand
    und von der Deutung ab und bleibt offen. Solche Gruppen tragen
    `pruefen=True` und werden NICHT zusammengefasst.

    -> {'figuren': [{'achse','apex','leere_spitze','meldungen'}],
        'kandidaten': [[i, j, ...]],   # Indizes in 'figuren'
        'meldungen': n, 'anzahl': m}
    """
    tq = konf.get('t_quadrat', [])
    konj = set()
    for a in aspects or ():
        if a.get('name') == 'Konjunktion':
            konj.add(frozenset((a['a'], a['b'])))
    gleich = lambda x, y: x == y or frozenset((x, y)) in konj

    def deckungsgleich(t1, t2):
        if t1['apex'] != t2['apex']:
            return False
        a1, b1 = t1['achse']
        a2, b2 = t2['achse']
        return ((gleich(a1, a2) and gleich(b1, b2))
                or (gleich(a1, b2) and gleich(b1, a2)))

    figuren = []
    for t in tq:
        for f in figuren:
            if deckungsgleich(f['_erst'], t):
                f['meldungen'].append(t['achse'])
                break
        else:
            figuren.append({'achse': t['achse'], 'apex': t['apex'],
                            'leere_spitze': t.get('leere_spitze'),
                            'meldungen': [t['achse']], '_erst': t})
    for f in figuren:
        f.pop('_erst', None)

    kandidaten = []
    for i, f in enumerate(figuren):
        for j in range(i + 1, len(figuren)):
            g = figuren[j]
            if f['apex'] != g['apex']:
                continue
            if set(f['achse']) & set(g['achse']):
                kandidaten.append([i, j])
    return {'figuren': figuren, 'kandidaten': kandidaten,
            'meldungen': len(tq), 'anzahl': len(figuren)}


def verteilungsmuster(factors, cusps=None):
    """Hemisphaeren, Quadranten und Jones-Muster der zehn klassischen Planeten.

    factors  dieselbe Liste wie fuer huber_aspects; gezaehlt werden nur die
             Namen aus _PLANETEN (Sonne bis Pluto).
    cusps    die zwoelf Koch-Spitzen; ohne sie entfallen Hemisphaeren und
             Quadranten (sie werden nach Haeusern gezaehlt), das Muster nach
             Jones wird trotzdem gerechnet (es haengt nur an den Graden).

    Rueckgabe (alles Befund, keine Deutung):
      'planeten'        die gezaehlten Namen in Tierkreisrichtung
      'hemisphaeren'    {'oben','unten','ost','west': [Namen]}
      'quadranten'      {1..4: [Namen]}  (I = Haeuser 1–3, … IV = 10–12)
      'betont'/'leer'   Befundzeilen-Rohmaterial nach HEMISPHAERE_BETONT und
                        QUADRANT_BETONT; leer = 0 von 10
      'wechsler'        Planeten in Grenzlage ueber eine Winkel-Spitze (AC, IC,
                        DC, MC) — sie koennten die Hemisphaere wechseln
      'spanne'          kleinster Bogen, der alle zehn traegt
      'groesste_luecke' {'von','bis','grad'}
      'luecken'         alle Luecken, absteigend
      'muster'          erste Wahl nach _MUSTER_RANG oder None
      'auch_lesbar'     [{'muster','grund'}] — echte Zweitlesarten und
                        Grenzfaelle innerhalb MUSTER_TOLERANZ
      'details'         das Muster-spezifische Material der ersten Wahl:
          Buendel     'raender' (erster, letzter Planet), 'mitte' (lon,
                      zeichen, haus)
          Schuessel   'raender', 'leere_mitte' (Mitte der leeren Haelfte)
          Eimer       'henkel' [{'name','zeichen','haus'}] (ein oder zwei),
                      'schuessel_raender', 'schuessel_spanne',
                      'henkel_zur_leeren_mitte' (Grad Abstand)
          Lokomotive  'leerer_bogen' (Grad), 'rand_nach_luecke',
                      'rand_vor_luecke' (je name/zeichen/haus; Konvention
                      s. Kommentar ueber dieser Funktion), 'leere_mitte'
          Wippe       'gruppen' (zwei Namenslisten), 'luecken' (die zwei)
          Streuung    'groesste_luecke', 'zeichen_besetzt', 'haeuser_besetzt'
          Spritzer    'gruppen' (drei oder mehr)
    „Kein eindeutiges Muster" ist ein legitimer Befund (muster=None) — die
    Bogenmasse stehen dann trotzdem da, damit die Deutung die Geometrie sieht.
    """
    pool = [(f['lon'] % 360.0, f['name']) for f in factors
            if f['name'] in _PLANETEN]
    pool.sort()
    out = {'planeten': [nm for _, nm in pool], 'hemisphaeren': None,
           'quadranten': None, 'betont': [], 'leer': [], 'wechsler': [],
           'spanne': None, 'groesste_luecke': None, 'luecken': [],
           'muster': None, 'auch_lesbar': [], 'details': {}}
    if len(pool) < 3:
        return out

    def ort(lon):
        d = {'lon': round(lon % 360.0, 2), 'zeichen': zeichen_name(lon),
             'haus': None, 'haus_spalte': None}
        if cusps:
            d['haus'] = haus_und_grenzlage(lon, cusps)['haus']
            d['haus_spalte'] = haus_spalte(lon, cusps)
        return d

    lon_of = {nm: lon for lon, nm in pool}

    def planet_ort(nm):
        d = ort(lon_of[nm])
        d['name'] = nm
        return d

    # --- Hemisphaeren und Quadranten nach Haeusern ---------------------------
    if cusps:
        hemi = {'oben': [], 'unten': [], 'ost': [], 'west': []}
        quad = {1: [], 2: [], 3: [], 4: []}
        for lon, nm in pool:
            hg = haus_und_grenzlage(lon, cusps)
            h = hg['haus']
            hemi['oben' if h in _HEMI_OBEN else 'unten'].append(nm)
            hemi['ost' if h in _HEMI_OST else 'west'].append(nm)
            quad[_QUADRANT_VON_HAUS[h]].append(nm)
            if hg['grenzlage'] and h in _WINKEL_HINTER_HAUS:
                out['wechsler'].append({
                    'name': nm, 'haus': h, 'nebenhaus': hg['nebenhaus'],
                    'abstand': hg['abstand_spitze'],
                    'winkel': _WINKEL_HINTER_HAUS[h]})
        out['hemisphaeren'] = hemi
        out['quadranten'] = quad
        n = len(pool)
        for key, label in (('oben', 'über dem Horizont'),
                           ('unten', 'unter dem Horizont'),
                           ('ost', 'östlich'), ('west', 'westlich')):
            k = len(hemi[key])
            if k == 0:
                out['leer'].append(f'Hemisphäre {label}')
            elif k >= HEMISPHAERE_BETONT:
                out['betont'].append(f'Hemisphäre {label} ({k} von {n})')
        for q in (1, 2, 3, 4):
            k = len(quad[q])
            if k == 0:
                out['leer'].append(f'Quadrant {"I II III IV".split()[q - 1]}')
            elif k >= QUADRANT_BETONT:
                out['betont'].append(
                    f'Quadrant {"I II III IV".split()[q - 1]} ({k} von {n})')

    # --- Bogenmasse ----------------------------------------------------------
    luecken, groesste, spanne = _bogen_daten(pool)
    out['spanne'] = spanne
    out['groesste_luecke'] = {k: groesste[k] for k in ('von', 'bis', 'grad')}
    out['luecken'] = sorted(({k: x[k] for k in ('von', 'bis', 'grad')}
                             for x in luecken), key=lambda x: -x['grad'])
    rand_nach = groesste['bis']      # Planet, an dem der leere Bogen endet
    rand_vor = groesste['von']       # Planet, hinter dem er beginnt
    leere_mitte = ort((groesste['von_lon'] + groesste['grad'] / 2.0) % 360.0)
    tol = MUSTER_TOLERANZ

    # --- Kandidaten: (Muster, strikt?, Details, Grund) -------------------------
    kandidaten = []

    def melde(name, strikt, details, grund):
        kandidaten.append({'muster': name, 'strikt': strikt,
                           'details': details, 'grund': grund})

    # Buendel / Schuessel / Lokomotive: reine Spannenfrage
    for name, grenze in (('Bündel', MUSTER_BUENDEL),
                         ('Schüssel', MUSTER_SCHUESSEL),
                         ('Lokomotive', MUSTER_LOKOMOTIVE)):
        if spanne <= grenze:
            strikt, grund = True, f'Spanne {_gr(spanne)} ≤ {grenze:g}°'
        elif spanne <= grenze + tol:
            strikt = False
            grund = (f'grenzwertig: Spanne {_gr(spanne)} über {grenze:g}°, '
                     f'innerhalb der Toleranz von {tol:g}°')
        else:
            continue
        if name == 'Bündel':
            mitte = ort((lon_of[rand_nach] + spanne / 2.0) % 360.0)
            det = {'raender': [planet_ort(rand_nach), planet_ort(rand_vor)],
                   'spanne': spanne, 'mitte': mitte}
        elif name == 'Schüssel':
            det = {'raender': [planet_ort(rand_nach), planet_ort(rand_vor)],
                   'spanne': spanne, 'leere_mitte': leere_mitte}
        else:
            det = {'leerer_bogen': groesste['grad'],
                   'rand_nach_luecke': planet_ort(rand_nach),
                   'rand_vor_luecke': planet_ort(rand_vor),
                   'leere_mitte': leere_mitte, 'spanne': spanne}
        melde(name, strikt, det, grund)

    # Eimer: ein Henkel (ein Planet, oder zwei innerhalb HENKEL_KONJUNKTION)
    # allein in der leeren Haelfte, mindestens HENKEL_RANDABSTAND von beiden
    # Raendern der Schuessel entfernt.
    namen = [nm for _, nm in pool]
    henkel_kandidaten = [[nm] for nm in namen]
    for i, a in enumerate(namen):
        for b in namen[i + 1:]:
            if _winkelabstand(lon_of[a], lon_of[b]) <= HENKEL_KONJUNKTION:
                henkel_kandidaten.append([a, b])
    beste = None
    for hk in henkel_kandidaten:
        # Stehen alle zehn zusammen in einer Haelfte, ist das eine Schuessel
        # und kein Eimer — der „Henkel" waere nur ihr Rand.
        if spanne <= MUSTER_SCHUESSEL:
            break
        rest = [(lon, nm) for lon, nm in pool if nm not in hk]
        if len(rest) < 3:
            continue
        r_luecken, r_groesste, r_spanne = _bogen_daten(rest)
        if r_spanne > MUSTER_SCHUESSEL + tol:
            continue
        r_strikt = r_spanne <= MUSTER_SCHUESSEL
        r_anfang, r_ende = r_groesste['bis'], r_groesste['von']
        # Henkel muss AUSSERHALB des Schuessel-Bogens liegen …
        h_lon = lon_of[hk[0]] if len(hk) == 1 else (
            lon_of[hk[0]] + ((lon_of[hk[1]] - lon_of[hk[0]] + 180.0) % 360.0
                             - 180.0) / 2.0) % 360.0
        if (h_lon - lon_of[r_anfang]) % 360.0 <= r_spanne:
            continue
        # … in der der Schuessel GEGENUEBERLIEGENDEN Haelfte (hoechstens 90°
        # von der Mitte der leeren Haelfte; sonst ist ein Planet 40° hinter
        # dem Rand einer engen Schuessel schon ein „Henkel") …
        r_leere_mitte = (lon_of[r_anfang] + r_spanne / 2.0 + 180.0) % 360.0
        if _winkelabstand(h_lon, r_leere_mitte) > 90.0:
            continue
        # … und von beiden Raendern mindestens HENKEL_RANDABSTAND entfernt
        # (bei zwei Henkelplaneten zaehlt der jeweils naehere)
        d_ende = min((lon_of[x] - lon_of[r_ende]) % 360.0 for x in hk)
        d_anfang = min((lon_of[r_anfang] - lon_of[x]) % 360.0 for x in hk)
        if min(d_ende, d_anfang) < HENKEL_RANDABSTAND:
            continue
        det = {'henkel': [planet_ort(x) for x in hk],
               'schuessel_raender': [planet_ort(r_anfang), planet_ort(r_ende)],
               'schuessel_spanne': r_spanne,
               'henkel_zur_leeren_mitte': round(
                   _winkelabstand(h_lon, r_leere_mitte), 2),
               'leere_mitte': ort(r_leere_mitte)}
        if beste is None or r_spanne < beste[1]:
            beste = (det, r_spanne, r_strikt)
    if beste:
        det, r_spanne, r_strikt = beste
        henkel_txt = ' + '.join(h['name'] for h in det['henkel'])
        if r_strikt:
            grund = (f'Schüssel-Spanne {_gr(r_spanne)} ≤ {MUSTER_SCHUESSEL:g}°, '
                     f'Henkel {henkel_txt} allein in der leeren Hälfte')
        else:
            grund = (f'grenzwertig: Schüssel-Spanne {_gr(r_spanne)} über '
                     f'{MUSTER_SCHUESSEL:g}°, innerhalb der Toleranz; Henkel '
                     f'{henkel_txt}')
        melde('Eimer', r_strikt, det, grund)

    # Wippe: genau zwei Luecken >= MUSTER_WIPPE_LUECKE, zwei Gruppen mit je
    # mindestens zwei Planeten
    for strikt, schwelle in ((True, MUSTER_WIPPE_LUECKE),
                             (False, MUSTER_WIPPE_LUECKE - tol)):
        grosse = [x for x in luecken if x['grad'] >= schwelle]
        if len(grosse) != 2:
            continue
        gruppen = _gruppen(pool, schwelle)
        if len(gruppen) != 2 or min(len(g) for g in gruppen) < 2:
            continue
        det = {'gruppen': gruppen,
               'luecken': [{k: x[k] for k in ('von', 'bis', 'grad')}
                           for x in grosse]}
        grund = ('zwei Lücken von ' +
                 ' und '.join(_gr(x['grad']) for x in grosse) +
                 (f' (je ≥ {MUSTER_WIPPE_LUECKE:g}°)' if strikt else
                  f' (grenzwertig, Toleranz {tol:g}°)'))
        melde('Wippe', strikt, det, grund)
        break

    # Streuung: groesste Luecke <= MUSTER_STREUUNG_LUECKE
    if groesste['grad'] <= MUSTER_STREUUNG_LUECKE + tol:
        strikt = groesste['grad'] <= MUSTER_STREUUNG_LUECKE
        det = {'groesste_luecke': out['groesste_luecke'],
               'zeichen_besetzt': len({zeichen_index(lon) for lon, _ in pool}),
               'haeuser_besetzt': (len({haus_und_grenzlage(lon, cusps)['haus']
                                        for lon, _ in pool}) if cusps else None)}
        grund = (f'größte Lücke {_gr(groesste["grad"])} '
                 + (f'≤ {MUSTER_STREUUNG_LUECKE:g}°' if strikt else
                    f'(grenzwertig, Toleranz {tol:g}°)'))
        melde('Streuung', strikt, det, grund)

    # Spritzer: drei oder mehr Gruppen, getrennt durch Luecken >=
    # MUSTER_SPRITZER_LUECKE, und keine Streuung (groesste Luecke > 60°)
    gruppen_s = _gruppen(pool, MUSTER_SPRITZER_LUECKE)
    if len(gruppen_s) >= 3 and groesste['grad'] > MUSTER_STREUUNG_LUECKE:
        melde('Spritzer', True, {'gruppen': gruppen_s},
              f'{len(gruppen_s)} Gruppen, getrennt durch Lücken ≥ '
              f'{MUSTER_SPRITZER_LUECKE:g}°')

    # --- Erste Wahl und Zweitlesarten ------------------------------------------
    strikte = [k for k in kandidaten if k['strikt']]
    erste = None
    for name in _MUSTER_RANG:
        treffer = [k for k in strikte if k['muster'] == name]
        if treffer:
            erste = treffer[0]
            break
    # Spritzer ist nur erste Wahl, wenn nichts Engeres passt — nie Zweitlesart
    verdeckt = set()
    if erste:
        out['muster'] = erste['muster']
        out['details'] = erste['details']
        # trivial mitgeltende Obermengen (jedes Buendel ist auch eine
        # Schuessel und eine Lokomotive) werden nicht als Zweitlesart genannt
        if erste['muster'] == 'Bündel':
            verdeckt = {'Schüssel', 'Lokomotive', 'Spritzer'}
        elif erste['muster'] == 'Schüssel':
            verdeckt = {'Lokomotive', 'Spritzer'}
        else:
            verdeckt = {'Spritzer'}
    for k in kandidaten:
        if erste is not None and k is erste:
            continue
        if k['muster'] in verdeckt:
            continue
        if k['muster'] == 'Spritzer':
            continue
        out['auch_lesbar'].append({'muster': k['muster'], 'grund': k['grund'],
                                   'details': k['details'],
                                   'strikt': k['strikt']})
    return out


# --- Mondphase ---------------------------------------------------------------

def mondphase(factors):
    """Winkel Sonne -> Mond, Rudhyar-Phase, Finsternisnaehe-Flag.

    Neu am 2026-09-08, zweiter Durchgang (Chris-Entscheidung; Befund
    Stilvergleich §7). Der Sonne-Mond-ASPEKT steht schon in der Aspektliste;
    die Phase ist die Ergaenzung fuer die Winkel dazwischen — eine Geburt bei
    100° Sonne-Mond ist eine Erstes-Viertel-Geburt, auch wenn kein Quadrat im
    Orb steht.

    Rueckgabe:
      'winkel'       Sonne -> Mond in Tierkreisrichtung, 0..360
      'phase'        Name aus MONDPHASEN, 'phase_index' 1..8,
      'von'/'bis'    das 45°-Fenster der Phase
      'zunehmend'    True unter 180°
      'syzygie'      {'art': 'Konjunktion'|'Opposition', 'orb'} innerhalb
                     FINSTERNIS_SYZYGIE_ORB, sonst None
      'finsternis'   nur bei Syzygie und vorhandenem Knoten: {'naehe': bool,
                     'art', 'sonne_knoten': (Knotenname, Grad),
                     'mond_knoten': (Knotenname, Grad)} — ein FLAG nach
                     FINSTERNIS_KNOTEN_ORB, keine Finsternisrechnung (dafuer
                     fehlt die Mondbreite in den Daten)
    Ohne Sonne oder Mond in `factors`: None.
    """
    pos = {f['name']: f['lon'] % 360.0 for f in factors}
    if 'Sonne' not in pos or 'Mond' not in pos:
        return None
    winkel = (pos['Mond'] - pos['Sonne']) % 360.0
    idx = int(winkel // MONDPHASE_SCHRITT) % len(MONDPHASEN)
    out = {'winkel': round(winkel, 2), 'phase': MONDPHASEN[idx],
           'phase_index': idx + 1,
           'von': idx * MONDPHASE_SCHRITT, 'bis': (idx + 1) * MONDPHASE_SCHRITT,
           'zunehmend': winkel < 180.0, 'syzygie': None, 'finsternis': None}
    d_konj = min(winkel, 360.0 - winkel)
    d_opp = abs(180.0 - winkel)
    if d_konj <= FINSTERNIS_SYZYGIE_ORB:
        out['syzygie'] = {'art': 'Konjunktion', 'orb': round(d_konj, 2)}
    elif d_opp <= FINSTERNIS_SYZYGIE_ORB:
        out['syzygie'] = {'art': 'Opposition', 'orb': round(d_opp, 2)}
    if out['syzygie'] and 'Knoten' in pos:
        kn = pos['Knoten']

        def naechster_knoten(lon):
            d_nord = _winkelabstand(lon, kn)
            d_sued = _winkelabstand(lon, kn + 180.0)
            return (('Nordknoten', round(d_nord, 2)) if d_nord <= d_sued
                    else ('Südknoten', round(d_sued, 2)))

        s_kn = naechster_knoten(pos['Sonne'])
        m_kn = naechster_knoten(pos['Mond'])
        naehe = min(s_kn[1], m_kn[1]) <= FINSTERNIS_KNOTEN_ORB
        art = None
        if naehe:
            art = ('Sonnenfinsternis-Nähe'
                   if out['syzygie']['art'] == 'Konjunktion'
                   else 'Mondfinsternis-Nähe')
        out['finsternis'] = {'naehe': naehe, 'art': art,
                             'sonne_knoten': s_kn, 'mond_knoten': m_kn}
    return out


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
    # Lilith neu am 2026-09-09 (Pruefbericht Geburtshoroskop, 5.8). Die
    # Lilith-Referenz nennt eine Wiederkehr alle knapp neun Jahre als „stillen
    # Reifungstakt"; ZYKLEN kannte sie nicht, weshalb ein Lilith-Kapitel nach
    # Prinzip 15 gar keine Zeitangabe bekommen durfte — eine Deutungsfrage,
    # die am Fehlen einer Zeile in einer Konstante haengt. Es ist ein TAKT,
    # keine markante Station wie die Saturn-Rueckkehr; strukturbild_text()
    # kennzeichnet das.
    'Lilith': [(8.9, 'erste Lilith-Rückkehr'), (17.7, 'zweite Lilith-Rückkehr'),
               (26.6, 'dritte Lilith-Rückkehr'), (35.4, 'vierte Lilith-Rückkehr'),
               (44.3, 'fünfte Lilith-Rückkehr'), (53.1, 'sechste Lilith-Rückkehr'),
               (62.0, 'siebte Lilith-Rückkehr')],
}
ZYKLUS_TAKT = ('Lilith',)   # Takte, keine markanten Stationen — s. ZYKLEN


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
    rezeptionen, aspektdichte, spezialnetz, konfigurationen, zyklen — und seit
    dem 2026-09-08 (zweiter Durchgang) verteilungsmuster und mondphase.
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
        'verteilungsmuster': verteilungsmuster(factors, cusps),
        'mondphase': mondphase(factors),
        'zyklen': {},
        'alter': alter,
    }
    # Achsen-Doppelungen gruppieren (neu 2026-09-09, Pruefbericht 5.7): Die
    # Handarbeit, die das Datenblatt-Modul bisher verlangte, macht jetzt
    # gruppiere_figuren() — sie fasst zusammen, was zweifelsfrei dieselbe Figur
    # ist, und markiert den Rest als Kandidat statt zu entscheiden.
    sb['figurgruppen'] = gruppiere_figuren(sb['konfigurationen'], aspects)
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
    fg = sb.get('figurgruppen')
    if fg and fg['meldungen'] != fg['anzahl']:
        # Achsen-Doppelung aufgeloest (neu 2026-09-09, Pruefbericht 5.7):
        # Steht ein Planet in Konjunktion zu einem Winkel, meldet
        # konfigurationen() dasselbe Dreieck mehrfach. Frueher musste das von
        # Hand zusammengefasst werden; die Zeile hier sagt jetzt, wie viele
        # Figuren es tatsaechlich sind.
        L.append('- Achsen-Doppelung: %d T-Quadrat-Meldungen entsprechen %d '
                 'Figuren (die übrigen sind dieselbe Figur über eine '
                 'Winkel-Konjunktion).' % (fg['meldungen'], fg['anzahl']))
    if fg and fg['kandidaten']:
        # Weiche Gruppe: gleicher Brennpunkt, ein gemeinsames Achsenende, aber
        # die zweiten Enden sind weder identisch noch konjunkt. Ob das EINE
        # Figur mit zwei Enden ist oder ZWEI, ist eine Deutungsentscheidung —
        # die Funktion legt sie vor, statt sie zu treffen.
        for i, j in fg['kandidaten']:
            a, b = fg['figuren'][i], fg['figuren'][j]
            L.append('- Zu prüfen: %s und %s teilen den Brennpunkt %s und ein '
                     'Achsenende. Ob das eine Figur mit zwei benachbarten '
                     'Enden ist oder zwei Figuren, entscheidet die Deutung; '
                     'die Entscheidung gehört ins chart_data.'
                     % (' ☍ '.join(a['achse']), ' ☍ '.join(b['achse']),
                        a['apex']))
    for t in kf['t_quadrat']:
        zeile = (f"- T-Quadrat: {' ☍ '.join(t['achse'])}, Brennpunkt "
                 f"{t['apex']}")
        ls = t.get('leere_spitze')
        if ls:
            # Die leere Spitze gehoert zur Figur wie der Apex: Sie ist die
            # Richtung, in der die Figur entlastet wird (Figur-Regel des
            # Typmoduls, 2026-09-08). Steht dort ein Faktor, wird er genannt —
            # dann ist die Spitze nicht leer, und das ist der Befund.
            haus = f", Haus {ls['haus_spalte']}" if ls.get('haus_spalte') else ''
            dort = ', '.join(f"{b['name']} ({_gr(b['orb'])})"
                             for b in ls['besetzt']) or 'nichts'
            zeile += (f" — leere Spitze {_gr(ls['lon'] % 30)} {ls['zeichen']}"
                      f"{haus}; dort: {dort}")
        L.append(zeile)
    for g in kf['grosskreuz']:
        L.append(f"- Großkreuz: {', '.join(g)}")
    for g in kf['grosstrigon']:
        L.append(f"- Großtrigon: {', '.join(g)}")
    for d in kf.get('drachen', []):
        # Der Drachen fuehrt sein Grosstrigon selbst: konfigurationen() hat es
        # aus der Grosstrigon-Liste genommen — EIN Befund, nicht zwei (dieselbe
        # Regel wie beim Zeichen-/Haus-Stellium unten).
        L.append(f"- Drachen: Großtrigon {', '.join(d['trigon'])} — Kopf "
                 f"{d['kopf']} (Opposition zu {d['achse'][1]}; Sextile zu "
                 f"{' und '.join(s[1] for s in d['sextile'])}). Trägt sein "
                 f"Großtrigon selbst, EIN Befund.")
    for r in kf.get('rechteck', []):
        L.append(f"- Mystisches Rechteck: Achsen "
                 f"{' ☍ '.join(r['achsen'][0])} und {' ☍ '.join(r['achsen'][1])}"
                 f" — Trigone {', '.join('–'.join(s) for s in r['trigone'])}; "
                 f"Sextile {', '.join('–'.join(s) for s in r['sextile'])}.")
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
            takt = ('  (Takt, keine markante Station — die Wiederkehr ist '
                    'kurz und wiederholt sich oft)'
                    if nm in ZYKLUS_TAKT else '')
            L.append(f"  - {nm}: " + ' · '.join(teile) + takt)
        L.append('- Verwendung s. Typmodul, Bewegung 7. Erlaubt ist die '
                 'Einordnung, verboten jede Aussage darüber, was in diesem '
                 'Alter geschieht.')
        L.append('')

    # §8 und §9 seit dem 2026-09-08 (zweiter Durchgang). Beide tragen eine
    # Befundzeile: Was hier nicht steht, prueft keine Gegenprobe.
    vm = sb.get('verteilungsmuster')
    if vm and vm.get('planeten'):
        L.append('### 8 · Verteilung (zehn klassische Planeten)')
        n = len(vm['planeten'])
        hemi, quad = vm.get('hemisphaeren'), vm.get('quadranten')
        if hemi:
            def _h(key):
                return f"{len(hemi[key])} — {', '.join(hemi[key]) or 'keiner'}"
            L.append(f"- Über dem Horizont (Häuser 7–12): {_h('oben')}; "
                     f"unter dem Horizont (1–6): {_h('unten')}.")
            L.append(f"- Östlich (Häuser 10–3): {_h('ost')}; "
                     f"westlich (4–9): {_h('west')}.")
            L.append('- Quadranten: ' + ' · '.join(
                f"{roem} (Häuser {h}) {len(quad[q])}"
                for q, roem, h in ((1, 'I', '1–3'), (2, 'II', '4–6'),
                                   (3, 'III', '7–9'), (4, 'IV', '10–12'))))
            marken = [f"{b} ⟵ betont" for b in vm['betont']] + \
                     [f"{l} ⟵ leer" for l in vm['leer']]
            L.append('- Betonung: ' + ('; '.join(marken) if marken else
                     f'keine (kein Bereich mit {HEMISPHAERE_BETONT} von {n} '
                     f'oder {QUADRANT_BETONT} je Quadrant, keiner leer)') + '.')
            if vm['wechsler']:
                L.append('- Hemisphären-Wechsler (Grenzlage über eine '
                         'Winkel-Spitze): ' + '; '.join(
                             f"{w['name']} {_gr(w['abstand'])} vor {w['winkel']} "
                             f"(Haus {w['haus']} → {w['nebenhaus']})"
                             for w in vm['wechsler']) + '.')
            else:
                L.append('- Hemisphären-Wechsler (Grenzlage über eine '
                         'Winkel-Spitze): keiner.')
        else:
            L.append('- Hemisphären und Quadranten: nicht gerechnet (keine '
                     'Hausspitzen übergeben).')

        gl = vm['groesste_luecke']
        det = vm.get('details') or {}

        def _ortstr(o):
            if not o:
                return '?'
            haus = f", Haus {o['haus_spalte']}" if o.get('haus_spalte') else ''
            return f"{_gr(o['lon'] % 30)} {o['zeichen']}{haus}"

        def _pl(o):
            return f"{o['name']} ({o['zeichen']}" + (
                f", Haus {o['haus_spalte']})" if o.get('haus_spalte') else ')')

        m = vm['muster']
        if m == 'Bündel':
            zeile = (f"- Muster nach Jones: Bündel — Spanne {_gr(det['spanne'])} "
                     f"von {_pl(det['raender'][0])} bis {_pl(det['raender'][1])}, "
                     f"Mitte {_ortstr(det['mitte'])}.")
        elif m == 'Schüssel':
            zeile = (f"- Muster nach Jones: Schüssel — Spanne {_gr(det['spanne'])} "
                     f"von {_pl(det['raender'][0])} bis {_pl(det['raender'][1])}; "
                     f"Mitte der leeren Hälfte {_ortstr(det['leere_mitte'])}.")
        elif m == 'Eimer':
            hk = det['henkel']
            zeile = (f"- Muster nach Jones: Eimer — Henkel "
                     f"{' + '.join(_pl(h) for h in hk)}"
                     f"{' (zwei Planeten in enger Konjunktion, EIN Henkel)' if len(hk) > 1 else ''}, "
                     f"{_gr(det['henkel_zur_leeren_mitte'])} neben der Mitte der "
                     f"leeren Hälfte; Schüssel {_gr(det['schuessel_spanne'])} von "
                     f"{_pl(det['schuessel_raender'][0])} bis "
                     f"{_pl(det['schuessel_raender'][1])}.")
        elif m == 'Lokomotive':
            zeile = (f"- Muster nach Jones: Lokomotive — leerer Bogen "
                     f"{_gr(det['leerer_bogen'])} von "
                     f"{det['rand_vor_luecke']['name']} bis "
                     f"{det['rand_nach_luecke']['name']}, Mitte "
                     f"{_ortstr(det['leere_mitte'])}; Ränder: "
                     f"{_pl(det['rand_nach_luecke'])} folgt dem leeren Bogen "
                     f"(Lokführer nach Deutungsregel), "
                     f"{_pl(det['rand_vor_luecke'])} geht ihm voraus "
                     f"(Schlusslicht). Konvention s. radix.verteilungsmuster().")
        elif m == 'Wippe':
            zeile = (f"- Muster nach Jones: Wippe — Gruppen "
                     f"{', '.join(det['gruppen'][0])} gegen "
                     f"{', '.join(det['gruppen'][1])}; Lücken "
                     f"{' und '.join(_gr(x['grad']) for x in det['luecken'])}.")
        elif m == 'Streuung':
            zeile = (f"- Muster nach Jones: Streuung — größte Lücke "
                     f"{_gr(gl['grad'])} ({gl['von']} → {gl['bis']}); "
                     f"{det['zeichen_besetzt']} Zeichen"
                     + (f", {det['haeuser_besetzt']} Häuser" if det.get('haeuser_besetzt') else '')
                     + " besetzt.")
        elif m == 'Spritzer':
            zeile = (f"- Muster nach Jones: Spritzer — {len(det['gruppen'])} Gruppen: "
                     + '; '.join(', '.join(g) for g in det['gruppen'])
                     + f". Größte Lücke {_gr(gl['grad'])}.")
        else:
            zeile = (f"- Muster nach Jones: kein eindeutiges Muster — Spanne "
                     f"{_gr(vm['spanne'])}, größte Lücke {_gr(gl['grad'])} "
                     f"({gl['von']} → {gl['bis']}). Das ist ein legitimer "
                     f"Befund, kein Fehler.")
        L.append(zeile)
        if vm['auch_lesbar']:
            L.append('- Auch lesbar als: ' + '; '.join(
                f"{z['muster']} ({z['grund']})" for z in vm['auch_lesbar']) + '.')
        L.append('- Befund: <eine Zeile — was Hemisphäre und Muster als Statik '
                 'heißen; Henkelplanet oder Lokführer als Brennpunkt (Typmodul, '
                 'Rang 5) oder ins Getriebe>')
        L.append('')

    mp = sb.get('mondphase')
    if mp:
        L.append('### 9 · Mondphase')
        L.append(f"- Winkel Sonne → Mond: {_gr(mp['winkel'])} — "
                 f"{mp['phase']} ({mp['von']:g}°–{mp['bis']:g}°, "
                 f"{mp['phase_index']}. von acht Stufen nach Rudhyar), "
                 f"{'zunehmend' if mp['zunehmend'] else 'abnehmend'}.")
        sy = mp.get('syzygie')
        if sy:
            wort = 'Neumond' if sy['art'] == 'Konjunktion' else 'Vollmond'
            L.append(f"- Lichter in {sy['art']} (Orb {_gr(sy['orb'])}): "
                     f"{wort}-Geburt — darf über Rang 5 ein Thema tragen "
                     f"(Typmodul).")
            fi = mp.get('finsternis')
            if fi:
                L.append(f"- Finsternisnähe: Sonne {_gr(fi['sonne_knoten'][1])} "
                         f"vom {fi['sonne_knoten'][0]}, Mond "
                         f"{_gr(fi['mond_knoten'][1])} vom {fi['mond_knoten'][0]}"
                         + (f" — innerhalb {FINSTERNIS_KNOTEN_ORB:g}°: {fi['art']} "
                            f"(Flag, keine Finsternisrechnung)." if fi['naehe']
                            else f" — keine (Grenze {FINSTERNIS_KNOTEN_ORB:g}°)."))
            else:
                L.append('- Finsternisnähe: nicht prüfbar (kein Knoten in der '
                         'Faktorenliste).')
        else:
            L.append(f"- Lichter weder in Konjunktion noch in Opposition "
                     f"(Orb {FINSTERNIS_SYZYGIE_ORB:g}°) — keine Neumond-/"
                     f"Vollmond-Geburt, Finsternisnähe entfällt.")
        L.append('- Befund: <ein Satz für den Mond-Block des '
                 'Instrument-Kapitels: wie diese Phase beginnt, erntet oder '
                 'loslässt — Anlage, keine Biografie>')
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
        # Leere Spitze: genau gegenueber dem Apex, mit Zeichen und Haus
        _ls = _t['leere_spitze']
        _apex_lon = next(x['lon'] for x in _f if x['name'] == _t['apex'])
        assert abs(((_apex_lon + 180) % 360) - _ls['lon']) < 0.01, _ls
        assert _ls['zeichen'] and _ls['haus'] in range(1, 13), _ls
    # Direkter Test der leeren Spitze: Apex 0° Widder -> Spitze 0° Waage,
    # und ein Faktor 3° daneben wird als besetzt gemeldet, einer 6° weg nicht.
    _ls2 = leere_spitze(0.0, [{'name': 'X', 'lon': 183.0},
                              {'name': 'Y', 'lon': 186.0}], _c)
    assert _ls2['zeichen'] == 'Waage' and _ls2['haus'] == 7, _ls2
    assert [b['name'] for b in _ls2['besetzt']] == ['X'], _ls2

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

    # --- Seit 2026-09-08 (zweiter Durchgang): Verteilungsmuster, Drachen,
    # Rechteck, Mondphase — ALLE Staende unten sind ERFUNDEN (synthetische
    # Faelle, je Muster einer), kein echtes Chart. -----------------------------
    _P = list(_PLANETEN)

    def _synth(lons):
        """Zehn Planeten auf frei gewaehlte Laengen setzen."""
        return [{'name': n, 'lon': float(l)} for n, l in zip(_P, lons)]

    # Buendel: alle innerhalb 100°
    _v = verteilungsmuster(_synth([0, 10, 20, 35, 45, 60, 70, 80, 90, 100]), _c)
    assert _v['muster'] == 'Bündel' and _v['spanne'] == 100.0, _v['muster']
    assert _v['auch_lesbar'] == [], _v['auch_lesbar']   # keine trivialen Obermengen
    # Buendel grenzwertig (124°): Schuessel erste Wahl, Buendel als Zweitlesart
    _v = verteilungsmuster(_synth([0, 10, 20, 35, 45, 60, 70, 80, 90, 124]), _c)
    assert _v['muster'] == 'Schüssel', _v['muster']
    assert [z['muster'] for z in _v['auch_lesbar']] == ['Bündel'], _v['auch_lesbar']
    # Schuessel: innerhalb 170°
    _v = verteilungsmuster(_synth([0, 20, 40, 60, 80, 100, 120, 140, 160, 170]), _c)
    assert _v['muster'] == 'Schüssel' and _v['auch_lesbar'] == [], _v
    assert _v['details']['raender'][0]['name'] == 'Sonne'
    assert _v['details']['raender'][1]['name'] == 'Pluto'
    # Eimer: neun innerhalb 150°, Henkel gegenueber (255°)
    _v = verteilungsmuster(_synth([0, 20, 40, 60, 80, 100, 120, 140, 150, 255]), _c)
    assert _v['muster'] == 'Eimer', _v['muster']
    assert [h['name'] for h in _v['details']['henkel']] == ['Pluto'], _v['details']
    assert _v['details']['henkel_zur_leeren_mitte'] == 0.0
    assert _v['details']['henkel'][0]['zeichen'] == 'Schütze'
    assert _v['details']['henkel'][0]['haus_spalte'] == '9'
    # Eimer mit Doppel-Henkel (zwei Planeten 6° auseinander = EIN Henkel)
    _v = verteilungsmuster(_synth([0, 20, 40, 60, 80, 100, 120, 150, 250, 256]), _c)
    assert _v['muster'] == 'Eimer', _v['muster']
    assert sorted(h['name'] for h in _v['details']['henkel']) == ['Neptun', 'Pluto']
    # KEIN Eimer: ein Planet 40° hinter dem Rand einer engen Schuessel
    _v = verteilungsmuster(_synth([0, 10, 20, 30, 40, 50, 60, 70, 90, 130]), _c)
    assert _v['muster'] == 'Schüssel', _v['muster']
    assert not any(z['muster'] == 'Eimer' for z in _v['auch_lesbar']), _v['auch_lesbar']
    # Lokomotive: innerhalb 230°, leerer Bogen 130°
    _v = verteilungsmuster(_synth([0, 25, 50, 75, 100, 125, 150, 175, 200, 230]), _c)
    assert _v['muster'] == 'Lokomotive', _v['muster']
    assert _v['details']['leerer_bogen'] == 130.0
    assert _v['details']['rand_nach_luecke']['name'] == 'Sonne'    # folgt der Luecke
    assert _v['details']['rand_vor_luecke']['name'] == 'Pluto'     # geht ihr voraus
    assert _v['details']['leere_mitte']['zeichen'] == 'Steinbock'  # 295°
    # Wippe: zwei Gruppen, Luecken 100° und 110°
    _v = verteilungsmuster(_synth([0, 20, 40, 55, 70, 170, 190, 210, 230, 250]), _c)
    assert _v['muster'] == 'Wippe', _v['muster']
    assert sorted(len(g) for g in _v['details']['gruppen']) == [5, 5]
    # Streuung: alle 36°
    _v = verteilungsmuster(_synth([i * 36 for i in range(10)]), _c)
    assert _v['muster'] == 'Streuung', _v['muster']
    assert _v['details']['zeichen_besetzt'] == 10
    # Spritzer: drei Gruppen, Luecken je 100°
    _v = verteilungsmuster(_synth([0, 10, 20, 120, 130, 140, 240, 250, 255, 260]), _c)
    assert _v['muster'] == 'Spritzer', _v['muster']
    assert len(_v['details']['gruppen']) == 3
    # Kein eindeutiges Muster: Luecken 110° und 50°, sonst 25°
    _v = verteilungsmuster(_synth([0, 25, 50, 75, 100, 125, 150, 175, 200, 250]), _c)
    assert _v['muster'] is None and _v['auch_lesbar'] == [], _v
    assert _v['spanne'] == 250.0
    # Eimer, der zugleich Lokomotive ist: Eimer erste Wahl, Lokomotive Zweitlesart
    _v = verteilungsmuster(_synth([0, 15, 30, 45, 60, 75, 90, 105, 120, 240]), _c)
    assert _v['muster'] == 'Eimer', _v['muster']
    assert 'Lokomotive' in [z['muster'] for z in _v['auch_lesbar']], _v['auch_lesbar']
    # Hemisphaeren nach Haeusern: Spitzen bei 0, 30, … -> 100° = Haus 4
    _v = verteilungsmuster(_synth([100, 105, 110, 115, 120, 125, 130, 135, 140, 88]), _c)
    assert 'Sonne' in _v['hemisphaeren']['unten'] and 'Sonne' in _v['hemisphaeren']['west']
    assert 'Sonne' in _v['quadranten'][2]
    assert _v['wechsler'] and _v['wechsler'][0]['name'] == 'Pluto'      # 88°: 2° vor IC
    assert _v['wechsler'][0]['winkel'] == 'IC' and _v['wechsler'][0]['nebenhaus'] == 4
    assert any(b.startswith('Hemisphäre unter dem Horizont') for b in _v['betont'])
    assert any(b.startswith('Quadrant II') for b in _v['betont'])
    assert 'Hemisphäre über dem Horizont' in _v['leer']

    # Drachen: Grosstrigon 0/120/240, Kopf 180 (Opposition zu 0, Sextile zu
    # 120 und 240). Das Trigon darf danach NICHT mehr als Grosstrigon stehen.
    _fd = [{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': 120.0},
           {'name': 'Jupiter', 'lon': 240.0}, {'name': 'Venus', 'lon': 180.0}]
    _kd = konfigurationen(_fd, huber_aspects(_fd))
    assert len(_kd['drachen']) == 1, _kd['drachen']
    assert _kd['drachen'][0]['kopf'] == 'Venus'
    assert _kd['drachen'][0]['achse'] == ['Venus', 'Sonne']
    assert sorted(_kd['drachen'][0]['trigon']) == ['Jupiter', 'Mond', 'Sonne']
    assert _kd['grosstrigon'] == [], _kd['grosstrigon']      # EIN Befund
    assert _kd['rechteck'] == []
    # Winkel-Ausschluss: dasselbe mit AC in der Basis und DC als Kopf -> kein
    # Drachen (die AC/DC-Opposition ist triviale Geometrie), das Trigon bleibt
    _fw = [{'name': 'AC', 'lon': 0.0}, {'name': 'Mond', 'lon': 120.0},
           {'name': 'Jupiter', 'lon': 240.0}, {'name': 'DC', 'lon': 180.0}]
    _kw = konfigurationen(_fw, huber_aspects(_fw))
    assert _kw['drachen'] == [] and len(_kw['grosstrigon']) == 1, _kw
    # Mystisches Rechteck: Oppositionen 0/180 und 60/240, Seiten 60/120/60/120
    _fr = [{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': 180.0},
           {'name': 'Venus', 'lon': 60.0}, {'name': 'Jupiter', 'lon': 240.0}]
    _kr = konfigurationen(_fr, huber_aspects(_fr))
    assert len(_kr['rechteck']) == 1, _kr['rechteck']
    assert sorted(_kr['rechteck'][0]['achsen']) == [['Jupiter', 'Venus'],
                                                    ['Mond', 'Sonne']]
    assert len(_kr['rechteck'][0]['trigone']) == 2
    assert len(_kr['rechteck'][0]['sextile']) == 2
    assert _kr['drachen'] == [] and _kr['grosstrigon'] == []
    # Winkel-Ausschluss: AC/DC als eine der beiden Achsen -> kein Rechteck
    _fx = [{'name': 'AC', 'lon': 0.0}, {'name': 'DC', 'lon': 180.0},
           {'name': 'Venus', 'lon': 60.0}, {'name': 'Jupiter', 'lon': 240.0}]
    assert konfigurationen(_fx, huber_aspects(_fx))['rechteck'] == []
    # Drei von vier Seiten sind kein Rechteck (Jupiter 12° zu weit)
    _f3 = [{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': 180.0},
           {'name': 'Venus', 'lon': 60.0}, {'name': 'Jupiter', 'lon': 252.0}]
    assert konfigurationen(_f3, huber_aspects(_f3))['rechteck'] == []

    # Stellium: drei Spezialfaktoren allein sind keins, zwei Planeten plus
    # ein Spezialfaktor schon
    _fs = [{'name': 'Knoten', 'lon': 10.0}, {'name': 'Chiron', 'lon': 15.0},
           {'name': 'Lilith', 'lon': 20.0}, {'name': 'Sonne', 'lon': 100.0},
           {'name': 'Mars', 'lon': 105.0}, {'name': 'Pholus', 'lon': 110.0}]
    _ks = konfigurationen(_fs, huber_aspects(_fs), cusps=_c)
    assert [s['zeichen'] for s in _ks['stellium_zeichen']] == ['Krebs'], _ks
    assert [s['haus'] for s in _ks['stellium_haus']] == [4], _ks

    # Mondphase: alle acht Stufen, dann Finsternisnaehe
    for _w, _erw in ((10, 'Neumond'), (50, 'zunehmende Sichel'),
                     (100, 'erstes Viertel'), (140, 'zunehmender Dreiviertelmond'),
                     (190, 'Vollmond'), (230, 'abnehmender Dreiviertelmond'),
                     (280, 'letztes Viertel'), (330, 'Balsamisch')):
        _mp = mondphase([{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': _w}])
        assert _mp['phase'] == _erw and _mp['winkel'] == _w, _mp
    _mp = mondphase([{'name': 'Sonne', 'lon': 300.0}, {'name': 'Mond', 'lon': 5.0}])
    assert _mp['winkel'] == 65.0 and _mp['zunehmend'] is True
    _mp = mondphase([{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': 5.0},
                     {'name': 'Knoten', 'lon': 10.0}])
    assert _mp['syzygie']['art'] == 'Konjunktion' and _mp['finsternis']['naehe']
    assert _mp['finsternis']['art'] == 'Sonnenfinsternis-Nähe'
    assert _mp['finsternis']['sonne_knoten'] == ('Nordknoten', 10.0)
    _mp = mondphase([{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': 177.0},
                     {'name': 'Knoten', 'lon': 190.0}])
    assert _mp['syzygie']['art'] == 'Opposition' and _mp['finsternis']['naehe']
    assert _mp['finsternis']['art'] == 'Mondfinsternis-Nähe'
    assert _mp['finsternis']['mond_knoten'] == ('Nordknoten', 13.0)
    _mp = mondphase([{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': 5.0},
                     {'name': 'Knoten', 'lon': 100.0}])
    assert _mp['finsternis']['naehe'] is False and _mp['finsternis']['art'] is None
    _mp = mondphase([{'name': 'Sonne', 'lon': 0.0}, {'name': 'Mond', 'lon': 100.0},
                     {'name': 'Knoten', 'lon': 5.0}])
    assert _mp['syzygie'] is None and _mp['finsternis'] is None

    # Die neuen Abschnitte stehen im Text des anonymen Pruefcharts
    assert '### 8 · Verteilung' in _txt and '### 9 · Mondphase' in _txt
    assert 'Muster nach Jones' in _txt and 'Winkel Sonne → Mond' in _txt
    print('Verteilung/Figuren/Mondphase-Test: OK —',
          _sb['verteilungsmuster']['muster'], '|',
          _sb['mondphase']['phase'], '|',
          len(_sb['konfigurationen']['drachen']), 'Drachen,',
          len(_sb['konfigurationen']['rechteck']), 'Rechtecke')
