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

Die Themennamen sind NICHT erfunden: es sind die Titel der Themenkapitel des
Transit-Laufs — dieselben Woerter, die der Text spaeter benutzt.
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

# (Themenname, Untertitel, [Transiter], Farbe) oder
# (Themenname, Untertitel, [Transiter], Farbe, [Ziele]) — Reihenfolge und
# Wortlaut wie die Themenkapitel des Transits. Ein Eintrag der Zielliste ist ein
# reiner Zielname ('Mond'), ein Paar aus Aspekt und Ziel ('Quadrat Sonne'), ein
# Paar aus Transiter und Ziel ('Saturn Mond') oder alle drei ('Saturn Quadrat
# Mond'); s. _passt().
# 2026-09-24 (Klasse-2-Entscheidungslauf, Datenschutz-Grep vor dem Upload): Hier
# standen bis dahin die Themennamen und Untertitel EINES echten Laufs — abgeleitete
# Deutungsergebnisse, die nach dem Datenschutz-Guardrail des Kerns nicht ins Repo
# gehoeren. Jetzt Platzhalter: Wer vergisst, THEMEN im Chart-Builder zu
# ueberschreiben, sieht die spitzen Klammern in der Uhr, statt fremde Namen zu
# drucken.
THEMEN = [
    ('<Titel Themenkapitel 1>', '<laufende Planeten und getroffene Punkte>',
     ['Pluto', 'Neptun', 'Uranus'], '#7d3b46'),
    ('<Titel Themenkapitel 2>', '<laufende Planeten und getroffene Punkte>',
     ['Saturn', 'Chiron', 'Jupiter', 'Knoten'], '#6b5c48'),
]

# Beschriftungen der Zeitachse. Nur diese drei Woerter der Grafik sind
# sprachgebunden; eine zweite Sprachfassung setzt sie vor dem Aufruf von
# bauen() um: tuhr.LABELS.update({'rueckblick': 'Look-back', ...}).
# Eingefuehrt 2026-08-01 fuer die englische Zweitfassung eines Ultimativ-
# Horoskops — vorher standen die Woerter fest im Code und die Grafik blieb
# im englischen PDF deutsch beschriftet.
LABELS = {'rueckblick': 'Rückblick', 'stichtag': 'Stichtag',
          'stationen': 'Stationen', 'sekundaer': 'sekundär',
          'monat': '1 Monat', 'monate': '{n} Monate'}
# 2026-09-22 (W57-Nachzug): Die englische Tafel steht jetzt hier, statt dass
# jeder englische Lauf sie selbst zusammensetzt — und mit ihr das DATUMSFORMAT.
# Bis heute war `%d.%m.%Y` fest verdrahtet: in einem englischen PDF las sich
# der Stichtag als Monat-vor-Tag, also als ein anderer Tag. Deshalb schreibt
# die englische Fassung den Monat als Wort ab (nicht `%b` — das haengt an der
# Locale des Rechners und kann deutsch zurueckkommen).
LABELS_EN = {'rueckblick': 'Look-back', 'stichtag': 'As of',
             'stationen': 'Stations', 'sekundaer': 'secondary',
             'monat': '1 month', 'monate': '{n} months'}
_LABELS_DE = dict(LABELS)
_MONAT_KURZ_EN = ('', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
SPRACHE = 'de'


def datum_text(d):
    """Stichtagsdatum in der gesetzten Sprache: „01.03.2030" / „1 Mar 2030"."""
    if SPRACHE == 'en':
        return '%d %s %d' % (d.day, _MONAT_KURZ_EN[d.month], d.year)
    return d.strftime('%d.%m.%Y')


def achse_text(d):
    """Monatsmarke der Zeitachse: „03/30" / „Mar 30"."""
    if SPRACHE == 'en':
        return '%s %02d' % (_MONAT_KURZ_EN[d.month], d.year % 100)
    return d.strftime('%m/%y')


def stations_text(d):
    """Datum einer Station unter der Zeitachse: „14.06.27" / „14 Jun 27".

    Neu 2026-09-26 (Pruefbericht Transit 3+4 vom 26.09., K1-6): Hier stand
    `%d.%m.%y` fest, auch nach setze_sprache('en') — im englischen PDF las
    sich jedes Stationsdatum als Monat-vor-Tag."""
    if SPRACHE == 'en':
        return '%d %s %02d' % (d.day, _MONAT_KURZ_EN[d.month], d.year % 100)
    return d.strftime('%d.%m.%y')


def setze_sprache(code='de'):
    """Sprache der Uhr-Beschriftungen und des Datumsformats setzen.

    Vor `bauen()` aufrufen. Die Themennamen kommen vom Aufrufer und werden
    hier NICHT uebersetzt — sie stehen so, wie der Lauf sie uebergibt.
    """
    global SPRACHE
    code = (code or 'de').strip().lower()[:2]
    if code not in ('de', 'en'):
        raise ValueError("sprache: 'de' oder 'en', nicht %r" % code)
    LABELS.clear()
    LABELS.update(LABELS_EN if code == 'en' else _LABELS_DE)
    SPRACHE = code
    return code

# Geometrie in Zeileneinheiten
H_KOPF = 1.15      # Themenkopf (Name + Untertitel)
H_BOGEN = 0.85     # dicker Themenbogen
H_ZEILE = 0.95     # eine Detailzeile
H_LUFT = 0.35      # Luft nach einem Block
H_ACHSE = 4.2      # Achse + Stationsleiste unten


def _passt(r, ziele):
    """Trifft eine Langlaeufer-Zeile die Zielliste eines Themas?

    Ein Eintrag der Liste ist einer von vier Formen:
      'Mond'                  reiner Zielname — jede Zeile an diesem Ziel
      'Quadrat Sonne'         Aspekt und Ziel
      'Saturn Mond'           Transiter und Ziel
      'Saturn Quadrat Mond'   alle drei
    Aspekt und Ziel werden gebraucht, sobald EIN laufender Planet zwei
    Themenkapitel mit DENSELBEN Zielen traegt und die Kapitel sich nur im Winkel
    unterscheiden. Transiter und Ziel (2026-09-24, Klasse-2-Entscheidungslauf
    T12) werden gebraucht, sobald ein Thema MEHRERE Transiter hat, die an
    verschiedenen Zielen mitklingen: Ohne sie zog ein Zielname die Linie jedes
    Transiters des Themas an sich, auch themenlose — die Uhr zeichnete dann
    fremde Linien mit oder liess eigene weg. Jede Zeile geht in das ERSTE
    passende Thema; ein Eintrag ohne Zielliste nimmt jede Zeile seiner
    Transiter. Die aelteren Formen gelten unveraendert.
    """
    if ziele is None:
        return True
    return (r['ziel'] in ziele or f"{r['aspekt']} {r['ziel']}" in ziele
            or f"{r['transiter']} {r['ziel']}" in ziele
            or f"{r['transiter']} {r['aspekt']} {r['ziel']}" in ziele)


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
    # noetig, sobald EIN laufender Planet zwei Themenkapitel traegt oder ein
    # Thema mehrere Transiter an verschiedenen Zielen hat (Formen s. _passt()).
    # Jede Zeile geht in das ERSTE passende Thema; ein Eintrag ohne Zielliste
    # nimmt jede Zeile seiner Transiter.
    bloecke, vergeben = [], set()
    for eintrag in THEMEN:
        name, unter, transiter, col = eintrag[:4]
        ziele = eintrag[4] if len(eintrag) > 4 else None
        idx = [i for i, r in enumerate(ll)
               if i not in vergeben and r['transiter'] in transiter
               and _passt(r, ziele)]
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
        lab = (LABELS['monat'] if mon == 1
               else LABELS['monate'].format(n=mon))
        # Kurze Boegen tragen das Label nicht: dann steht es LINKS daneben in
        # der Themenfarbe statt weiss im Balken (sonst laeuft es ueber den
        # Rand hinaus — Themenbloecke am Fensterrand, 2026-07-30).
        if B - A < spanne * 0.085:
            ax.text(A - spanne * 0.006, y, lab, ha='right', va='center',
                    fontsize=6.8 * sk, color=col, zorder=6)
        else:
            ax.text(min(B - spanne * 0.006, X1 - spanne * 0.006), y,
                    lab, ha='right', va='center',
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
                ax.text(bb + spanne * 0.006, y, LABELS['sekundaer'], ha='left',
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
            ax.text(X, y_ach - 0.42, achse_text(d), ha='center',
                    va='center', fontsize=7.4 * sk, color=STONE, zorder=4)
        d = (d.replace(day=28) + timedelta(days=8)).replace(day=1)
    ax.text(X0 + spanne * 0.004, y_ach + 0.30, LABELS['rueckblick'],
            ha='left', va='bottom', fontsize=7.6 * sk, color='#9a8f77',
            zorder=6)
    ax.text(st + spanne * 0.004, y_ach + 0.30,
            LABELS['stichtag'] + ' ' + datum_text(f['stichtag']),
            ha='left', va='bottom', fontsize=8.2 * sk, color=GOLD, zorder=6)

    # --- Stationsleiste (aus der Themen-Uhr) --------------------------------
    ax.text(X0 - spanne * 0.008, y_ach - 1.05, LABELS['stationen'], ha='right',
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
                + stations_text(s['datum']), ha='center', va='center',
                fontsize=6.2 * sk, color=STONE, zorder=6)

    fig.tight_layout(pad=0.4)
    fig.savefig(out_path, facecolor=PAPER, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return out_path, len(ll), len(st_liste)


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
    import sys as _s
    if _hilfe_cli():          # python3 transituhr_fusion.py --hilfe [<name>]
        _s.exit(0)
    import transitdata as _td
    quelle = _s.argv[2] if len(_s.argv) > 2 else None
    p, n, ns = bauen(_s.argv[1] if len(_s.argv) > 1 else
                     '/home/claude/transituhr.png', _td.parse(quelle))
    print('geschrieben:', p, '|', n, 'Linien,', ns, 'Stationen')
