#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transit-Uhr, Fusionsfassung — Themenbloecke + Einzellinien.

Was von welcher Seite kommt:
  aus der THEMEN-Uhr    die Gliederung nach Themen statt nach Planeten, der
                        Themenname direkt am Balken, die Stationsleiste unter
                        der Zeitachse, die ruhige Grundflaeche
  aus der LINIEN-Uhr    jede einzelne Linie bleibt sichtbar, mit voller
                        Beschriftung, blasser Gesamtspanne, kraeftigem
                        Wirkorb-Abschnitt und Rauten auf den Exaktdaten
  neu                   ueber jedem Block ein dicker Themenbogen, der die
                        Gesamtspanne des Themas zusammenfasst — man liest also
                        erst die vier, fuenf grossen Zeiten und geht dann ins
                        Detail, statt 42 gleichrangige Zeilen abzusuchen

Die Themennamen sind NICHT erfunden: es sind die Kapiteltitel aus Teil III B
des Ultimativ-Laufs — dieselben Woerter, die der Text spaeter benutzt.
"""
import sys
from datetime import timedelta

sys.path.insert(0, '/home/claude')
import transitdata as td                                # noqa: E402

PAPER = '#f8f4ec'
GOLD = '#a37c37'
INK = '#241f1a'
STONE = '#7a6a52'
DEEP = '#123540'

FARBE = {'Pluto': '#7d3b46', 'Neptun': '#2f6070', 'Uranus': '#4a7a63',
         'Saturn': '#6b5c48', 'Chiron': '#a8553a', 'Jupiter': '#b8862f',
         'Knoten': '#7a6a52'}

# (Themenname, Untertitel, [Transiter], Farbe) — Reihenfolge und Wortlaut wie
# die Kapitel 30-35 in Teil III B.
THEMEN = [
    ('Die Tiefenlinie', 'was die Wandlungskraft zwei Jahre lang durcharbeitet',
     ['Pluto'], '#7d3b46'),
    ('Die Leiselinie', 'das Feine prüft Ideal, Struktur und Wort',
     ['Neptun'], '#2f6070'),
    ('Der Weckruf', 'Uranus rüttelt an Denken, Bindung und Struktur',
     ['Uranus'], '#4a7a63'),
    ('Die Heilerlinie', 'Chiron zwischen Wurzel, Liebe und Tiefe',
     ['Chiron'], '#a8553a'),
    ('Die Straße der Verbindlichkeit', 'Saturn nimmt den Weg ab',
     ['Saturn'], '#6b5c48'),
    ('Das Jupiter-Jahr und der Knotentakt', 'die schnelleren Zeiger',
     ['Jupiter', 'Knoten'], '#b8862f'),
]

# Geometrie in Zeileneinheiten
H_KOPF = 1.15      # Themenkopf (Name + Untertitel)
H_BOGEN = 0.85     # dicker Themenbogen
H_ZEILE = 0.95     # eine Detailzeile
H_LUFT = 0.35      # Luft nach einem Block
H_ACHSE = 4.2      # Achse + Stationsleiste unten


def stationen(daten):
    """Stationen der langsamen Planeten im Fenster.

    Kommen aus dem §11-Block (transitdata.parse -> 'stationen'); gerechnet wird
    hier nichts. Faellt der Block aus, bleibt die Leiste einfach leer.
    """
    out = []
    for s in daten.get('stationen', []):
        out.append({'planet': s['planet'], 'datum': s['datum'],
                    'richtung': s['richtung']})
    return sorted(out, key=lambda x: x['datum'])


def bauen(out_path, daten, breite=12.4, dpi=210):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = ['DejaVu Sans', 'FreeSerif', 'FreeSans']
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle, FancyBboxPatch

    f = daten['fenster']
    ll = daten['langlaeufer']
    st_liste = stationen(daten)

    # --- Bloecke zusammenstellen, Hoehe vorab bestimmen ---------------------
    # Ein THEMEN-Eintrag ist (Name, Untertitel, [Transiter], Farbe) oder
    # (Name, Untertitel, [Transiter], Farbe, [Ziele]). Die Zielliste ist
    # noetig, sobald EIN laufender Planet zwei Themenkapitel traegt (Pluto auf
    # der Wertachse vs. Pluto auf der Seelenachse) — ohne sie liefen beide
    # Kapitel in einen Block mit nur einem der beiden Namen. Jede Zeile geht in
    # das ERSTE passende Thema; ein Eintrag ohne Zielliste sammelt den Rest.
    bloecke, vergeben = [], set()
    for eintrag in THEMEN:
        name, unter, transiter, col = eintrag[:4]
        ziele = eintrag[4] if len(eintrag) > 4 else None
        idx = [i for i, r in enumerate(ll)
               if i not in vergeben and r['transiter'] in transiter
               and (ziele is None or r['ziel'] in ziele)]
        vergeben.update(idx)
        zeilen = [ll[i] for i in idx]
        if not zeilen:
            continue
        zeilen.sort(key=lambda r: r['start'])
        bloecke.append({'name': name, 'unter': unter, 'col': col,
                        'zeilen': zeilen,
                        'start': min(r['start'] for r in zeilen),
                        'ende': max(r['ende'] for r in zeilen)})
    hoehe_e = sum(H_KOPF + H_BOGEN + len(b['zeilen']) * H_ZEILE + H_LUFT
                  for b in bloecke) + H_ACHSE + 1.00

    sk = breite / 11.0
    fig, ax = plt.subplots(figsize=(breite, 0.26 + hoehe_e * 0.206), dpi=dpi)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    X0 = mdates.date2num(f['rueckblick'])
    X1 = mdates.date2num(f['ende'])
    ax.set_xlim(X0, X1)
    ax.set_ylim(0, hoehe_e)
    ax.axis('off')
    spanne = X1 - X0

    # --- Hintergrund: Rueckblickzone, Quartalsbaender, Stichtag -------------
    st = mdates.date2num(f['stichtag'])
    y_unten = H_ACHSE - 1.5
    y_oben = hoehe_e
    ax.add_patch(Rectangle((X0, y_unten), st - X0, y_oben - y_unten,
                           facecolor='#e8e2d4', edgecolor='none', zorder=0))
    for i, q in enumerate(daten['quartale']):
        lab, a, b = q[0], q[1], q[2]
        sub = q[3] if len(q) > 3 else ''
        A, B = mdates.date2num(a), mdates.date2num(b)
        if i % 2 == 0:
            ax.add_patch(Rectangle((A, y_unten), B - A, y_oben - y_unten,
                                   facecolor='#efe9db', edgecolor='none',
                                   zorder=0))
        ax.plot([A, A], [y_unten, y_oben], color='#d5cbb4', lw=0.7, zorder=0.5)
        ax.text((A + B) / 2, y_oben - 0.40, lab, ha='center', va='center',
                fontsize=9.0 * sk, color=DEEP, zorder=3)
        if sub:
            ax.text((A + B) / 2, y_oben - 0.90, sub, ha='center', va='center',
                    fontsize=6.8 * sk, color=STONE, zorder=3)
    ax.plot([X1, X1], [y_unten, y_oben], color='#d5cbb4', lw=0.7, zorder=0.5)
    ax.plot([st, st], [y_unten, y_oben], color=GOLD, lw=1.5, zorder=4)

    # --- Bloecke ------------------------------------------------------------
    y = hoehe_e - 2.15
    for b in bloecke:
        col = b['col']
        # Themenkopf: Name links am Satzspiegel, nie ueber den Rand hinaus
        ax.add_patch(Rectangle((X0 + spanne * 0.004, y - 0.30),
                               spanne * 0.0085, 0.60, facecolor=col,
                               edgecolor='none', zorder=5))
        ax.text(X0 + spanne * 0.019, y + 0.06, b['name'], ha='left',
                va='center', fontsize=9.6 * sk, color=DEEP, zorder=5)
        ax.text(X0 + spanne * 0.019, y - 0.50, b['unter'], ha='left',
                va='center', fontsize=7.6 * sk, color=STONE, zorder=5,
                style='italic')
        y -= H_KOPF

        # Themenbogen: Gesamtspanne des Themas, dick und weich
        A = max(mdates.date2num(b['start']), X0)
        B = min(mdates.date2num(b['ende']), X1)
        ax.add_patch(FancyBboxPatch((A, y - 0.28), B - A, 0.56,
                                    boxstyle='round,pad=0,rounding_size=0.26',
                                    facecolor=col, alpha=0.42,
                                    edgecolor='none', zorder=2))
        mon = round((b['ende'] - b['start']).days / 30.44)
        ax.text(min(B - spanne * 0.006, X1 - spanne * 0.006), y,
                f'{mon} Monate', ha='right', va='center',
                fontsize=6.8 * sk, color='#fdfaf2', zorder=6)
        y -= H_BOGEN

        # Detailzeilen
        for r in b['zeilen']:
            rc = FARBE.get(r['transiter'], STONE)
            prim = r['primaer']
            a = max(mdates.date2num(r['start']), X0)
            bb = min(mdates.date2num(r['ende']), X1)
            ax.add_patch(Rectangle((a, y - 0.24), bb - a, 0.48, facecolor=rc,
                                   alpha=0.18 if prim else 0.11,
                                   edgecolor='none', zorder=2))
            for pa, pb in (r['wirkorb'] or [(r['start'], r['ende'])]):
                A2 = max(mdates.date2num(pa), X0)
                B2 = min(mdates.date2num(pb), X1)
                if B2 > A2:
                    ax.add_patch(Rectangle((A2, y - 0.155), B2 - A2, 0.31,
                                           facecolor=rc,
                                           alpha=0.92 if prim else 0.50,
                                           edgecolor='none', zorder=3))
            for ex in r['exakt']:
                E = mdates.date2num(ex)
                if X0 <= E <= X1:
                    ax.plot([E], [y], marker='D', ms=2.7 * sk,
                            color='#fdfaf2', markeredgecolor=rc,
                            markeredgewidth=0.9, zorder=5)
            lab = td.kurz(r['transiter'], r['aspekt'], r['ziel'])
            ax.text(X0 - spanne * 0.008, y, lab, ha='right', va='center',
                    fontsize=7.2 * sk, color=INK if prim else '#8d8371',
                    zorder=5)
            if not prim:
                ax.text(bb + spanne * 0.006, y, 'sekundär', ha='left',
                        va='center', fontsize=6.2 * sk, color='#a99b80',
                        zorder=5)
            y -= H_ZEILE
        y -= H_LUFT

    # --- Zeitachse ----------------------------------------------------------
    y_ach = H_ACHSE - 1.5
    ax.plot([X0, X1], [y_ach, y_ach], color='#c9bda4', lw=0.9, zorder=4)
    d = f['rueckblick'].replace(day=1)
    while d <= f['ende']:
        if d.month in (1, 4, 7, 10) and d >= f['rueckblick']:
            X = mdates.date2num(d)
            ax.plot([X, X], [y_ach, y_ach - 0.16], color='#c9bda4', lw=0.9,
                    zorder=4)
            ax.text(X, y_ach - 0.42, d.strftime('%m/%y'), ha='center',
                    va='center', fontsize=7.4 * sk, color=STONE, zorder=4)
        d = (d.replace(day=28) + timedelta(days=8)).replace(day=1)
    ax.text(X0 + spanne * 0.004, y_ach + 0.30, 'Rückblick', ha='left',
            va='bottom', fontsize=7.6 * sk, color='#9a8f77', zorder=6)
    ax.text(st + spanne * 0.004, y_ach + 0.30,
            'Stichtag ' + f['stichtag'].strftime('%d.%m.%Y'), ha='left',
            va='bottom', fontsize=8.2 * sk, color=GOLD, zorder=6)

    # --- Stationsleiste (aus der Themen-Uhr) --------------------------------
    ax.text(X0 - spanne * 0.008, y_ach - 1.05, 'Stationen', ha='right',
            va='center', fontsize=7.4 * sk, color=GOLD, zorder=5)
    # Beschriftungsbreite in Datumseinheiten schaetzen und je Station die
    # oberste Reihe suchen, in der sie kollisionsfrei sitzt. Der starre
    # Zweizeiler davor liess bei 24 Stationen die Daten uebereinanderlaufen.
    breit = spanne * 0.062
    belegt = []
    for s in st_liste:
        X = mdates.date2num(s['datum'])
        if X < X0 or X > X1:
            continue
        r = 0
        while r < len(belegt) and belegt[r] > X - breit:
            r += 1
        if r == len(belegt):
            belegt.append(X + breit)
        else:
            belegt[r] = X + breit
        yy = y_ach - 1.0 - r * 0.72
        col = FARBE.get(s['planet'], STONE)
        ax.plot([X], [y_ach], marker='o', ms=3.4 * sk, color=col,
                markeredgecolor=PAPER, markeredgewidth=0.7, zorder=6)
        if r:
            ax.plot([X, X], [y_ach, yy + 0.22], color=col, lw=0.5,
                    alpha=0.45, zorder=5)
        ax.plot([X], [yy], marker='o', ms=4.4 * sk, color=col,
                markeredgecolor=PAPER, markeredgewidth=0.8, zorder=6)
        ax.text(X, yy - 0.42, td.GLYPH.get(s['planet'], '') + ' '
                + s['datum'].strftime('%d.%m.%y'), ha='center', va='center',
                fontsize=6.2 * sk, color=STONE, zorder=6)

    fig.tight_layout(pad=0.4)
    fig.savefig(out_path, facecolor=PAPER, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return out_path, len(ll), len(st_liste)


if __name__ == '__main__':
    import sys as _s
    import transitdata as _td
    quelle = _s.argv[2] if len(_s.argv) > 2 else None
    p, n, ns = bauen(_s.argv[1] if len(_s.argv) > 1 else
                     '/home/claude/transituhr.png', _td.parse(quelle))
    print('geschrieben:', p, '|', n, 'Linien,', ns, 'Stationen')
