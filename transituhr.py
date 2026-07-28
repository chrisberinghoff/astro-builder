#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Transit-Uhr: Zeitleiste der langen Linien über die 24 Monate des Fensters.

Gegenüber dem Projektstand zwei Änderungen (2026-07-27):
  1. `bauen(..., daten=...)` — die Daten dürfen direkt übergeben werden statt
     immer aus td.parse(quelle) zu kommen. Rein additiv; ohne `daten` verhält
     sich die Funktion wie bisher.
  2. `breite` — Figurbreite als Parameter. Die Zeilenbeschriftung trägt jetzt
     beide Planetennamen und braucht dadurch mehr Platz; ohne breitere Figur
     schrumpft der Balkenbereich.

Balkenlogik je Linie: blasser Balken = volle Spanne (Snapshot-Orb), kräftige
Segmente = Wirkorb-Perioden (1,5°, das Gedeutete), Rauten = Exaktdaten.
"""
import sys

sys.path.insert(0, '/home/claude')
import transitdata as td                                    # noqa: E402

FARBE = {'Pluto': '#7d3b46', 'Neptun': '#2f6070', 'Uranus': '#4a7a63',
         'Saturn': '#6b5c48', 'Chiron': '#a8553a', 'Jupiter': '#b8862f',
         'Knoten': '#7a6a52'}
ORDNUNG = ['Pluto', 'Neptun', 'Uranus', 'Saturn', 'Chiron', 'Jupiter', 'Knoten']
PAPER = '#f8f4ec'
GOLD = '#a37c37'
INK = '#241f1a'
STONE = '#7a6a52'


def bauen(out_path, quelle=None, dpi=210, daten=None, breite=12.4,
          zeilenhoehe=0.272, label_fn=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = ['DejaVu Sans', 'FreeSerif', 'FreeSans']
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle, Polygon

    d = daten if daten is not None else td.parse(quelle)
    kurz = label_fn or td.kurz
    f = d['fenster']
    x0, x1 = f['rueckblick'], f['ende']
    ll = sorted(d['langlaeufer'],
                key=lambda r: (ORDNUNG.index(r['transiter'])
                               if r['transiter'] in ORDNUNG else 99,
                               r['start']))
    n = len(ll)
    # Die Grafik wird im Dokument immer auf dieselbe Breite skaliert. Wird die
    # Figur breiter (laengere Beschriftung), schrumpfen alle Schriften auf der
    # Seite im selben Verhaeltnis — darum hier gegenskalieren, damit die
    # Beschriftung gedruckt gleich gross bleibt wie bisher.
    sk = breite / 11.0
    fig, ax = plt.subplots(figsize=(breite, 1.55 + n * zeilenhoehe), dpi=dpi)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    X0, X1 = mdates.date2num(x0), mdates.date2num(x1)
    ax.set_xlim(X0, X1)
    ax.set_ylim(-0.8, n)

    st = mdates.date2num(f['stichtag'])
    ax.add_patch(Rectangle((X0, -0.8), st - X0, n + 0.8, facecolor='#e8e2d4',
                           edgecolor='none', zorder=0))
    for i, q in enumerate(d['quartale']):
        lab, a, b = q[0], q[1], q[2]
        A, B = mdates.date2num(a), mdates.date2num(b)
        if i % 2 == 0:
            ax.add_patch(Rectangle((A, -0.8), B - A, n + 0.8,
                                   facecolor='#efe9db', edgecolor='none',
                                   zorder=0))
        ax.plot([A, A], [-0.8, n], color='#d5cbb4', lw=0.7, zorder=0.5)
        ax.text((A + B) / 2, n - 0.28, lab, ha='center', va='bottom',
                fontsize=8.4 * sk, color=GOLD, zorder=3)
    ax.plot([mdates.date2num(d['quartale'][-1][2])] * 2, [-0.8, n],
            color='#d5cbb4', lw=0.7, zorder=0.5)

    ax.plot([st, st], [-0.8, n], color=GOLD, lw=1.5, zorder=4)
    ax.text(st, -0.72, ' Stichtag ' + f['stichtag'].strftime('%d.%m.%Y'),
            ha='left', va='bottom', fontsize=8.2 * sk, color=GOLD, zorder=6)
    ax.text(X0, -0.72, ' Rückblick ', ha='left', va='bottom',
            fontsize=7.6 * sk, color='#9a8f77', zorder=6)

    labels = []
    for r, row in enumerate(ll):
        y = n - 1 - r
        col = FARBE.get(row['transiter'], STONE)
        prim = row['primaer']
        a = max(mdates.date2num(row['start']), X0)
        b = min(mdates.date2num(row['ende']), X1)
        ax.add_patch(Rectangle((a, y - 0.30), b - a, 0.60, facecolor=col,
                               alpha=0.20 if prim else 0.13, edgecolor='none',
                               zorder=2))
        perioden = row['wirkorb'] or [(row['start'], row['ende'])]
        for pa, pb in perioden:
            A = max(mdates.date2num(pa), X0)
            B = min(mdates.date2num(pb), X1)
            if B <= A:
                continue
            ax.add_patch(Rectangle((A, y - 0.185), B - A, 0.37, facecolor=col,
                                   alpha=0.92 if prim else 0.50,
                                   edgecolor='none', zorder=3))
        for ex in row['exakt']:
            E = mdates.date2num(ex)
            if X0 <= E <= X1:
                ax.plot([E], [y], marker='D', ms=3.0, color='#fdfaf2',
                        markeredgecolor=col, markeredgewidth=0.9, zorder=5)
        w = (X1 - X0) * 0.006
        if mdates.date2num(row['start']) < X0:
            ax.add_patch(Polygon([(X0, y), (X0 + w * 1.6, y + 0.30),
                                  (X0 + w * 1.6, y - 0.30)], closed=True,
                                 facecolor=col, alpha=0.9, zorder=4))
        if mdates.date2num(row['ende']) > X1:
            ax.add_patch(Polygon([(X1, y), (X1 - w * 1.6, y + 0.30),
                                  (X1 - w * 1.6, y - 0.30)], closed=True,
                                 facecolor=col, alpha=0.9, zorder=4))
        labels.append(kurz(row['transiter'], row['aspekt'], row['ziel'])
                      + ('' if prim else '  (sekundär)'))

    ax.set_yticks(list(range(n)))
    ax.set_yticklabels(list(reversed(labels)), fontsize=7.2 * sk)
    for t, row in zip(reversed(ax.get_yticklabels()), ll):
        t.set_color(INK if row['primaer'] else '#8d8371')
    ax.tick_params(axis='y', length=0, pad=4)

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%y'))
    ax.tick_params(axis='x', labelsize=7.4 * sk, colors=STONE, length=2.5)
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color('#c9bda4')

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, facecolor=PAPER, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return out_path, n


if __name__ == '__main__':
    import sys as _s
    p, n = bauen(_s.argv[1] if len(_s.argv) > 1 else
                 '/home/claude/transituhr.png',
                 quelle=(_s.argv[2] if len(_s.argv) > 2 else None))
    print('geschrieben:', p, '|', n, 'Linien')
