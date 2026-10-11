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

Seit 2026-10-11 dazu der UHR-AUSSCHNITT am Kapitelanfang: ausschnitte() zeichnet
je Themenkapitel genau seinen Block der Uhr (gleiche Zuordnung, gleiche
Zeitachse, ohne Namen und Stationsleiste), kopf_mit_ausschnitt() verbindet ihn
mit dem Kapitelkopf. Die Zeichnung des Blocks ist dieselbe Funktion wie in bauen()
(_block), damit grosse Uhr und Ausschnitt nicht auseinanderlaufen.
"""
import os
import re
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
          'monat': '1 Monat', 'monate': '{n} Monate',
          'unter_monat': 'unter 1 Monat',           # 2026-09-30, s. monats_label()
          'ausschnitt': 'Ausschnitt der Transit-Uhr'}   # 2026-10-11, Alt-Text
# 2026-09-22 (W57-Nachzug): Die englische Tafel steht jetzt hier, statt dass
# jeder englische Lauf sie selbst zusammensetzt — und mit ihr das DATUMSFORMAT.
# Bis heute war `%d.%m.%Y` fest verdrahtet: in einem englischen PDF las sich
# der Stichtag als Monat-vor-Tag, also als ein anderer Tag. Deshalb schreibt
# die englische Fassung den Monat als Wort ab (nicht `%b` — das haengt an der
# Locale des Rechners und kann deutsch zurueckkommen).
LABELS_EN = {'rueckblick': 'Look-back', 'stichtag': 'As of',
             'stationen': 'Stations', 'sekundaer': 'secondary',
             'monat': '1 month', 'monate': '{n} months',
             'unter_monat': 'under 1 month',
             'ausschnitt': 'Excerpt of the transit clock'}
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

# Uhr-Ausschnitt am Kapitelanfang (2026-10-11, Chris-Entscheidung nach dem Muster
# an einem echten Transit). Die Figur ist SCHMALER als die grosse Uhr (8,8 statt
# 12,4 Zoll), traegt aber deren Schriftgrad (AUS_SK = 12,4 / 11): auf Satzbreite
# gesetzt wird sie dadurch rund 40 % groesser gedruckt — die Beschriftung der
# grossen Uhr ist gedruckt kaum lesbar, ein einzelner Block hat den Platz. Die
# Hoehen in Zeileneinheiten bleiben die der grossen Uhr, nur der Kopf ist
# einzeilig (H_KOPF_AUS: Untertitel ohne Namen, der Name steht als Kapiteltitel
# darueber) und die Achse traegt keine Stationsleiste (H_ACHSE_AUS).
# Gemessen am Muster: bis 8,8 Zoll keine Ueberlappung im Quartalskopf; eine
# blosse Schriftvergroesserung bei voller Breite (lupe 1,4) liess Quartals- und
# Monatszeile ineinanderlaufen.
AUS_BREITE = 8.8
AUS_SK = 12.4 / 11.0
H_KOPF_AUS = 0.75
H_ACHSE_AUS = 2.3
# .kopf-uhr haelt Kapitelkopf und Ausschnitt als EINE Einheit zusammen und traegt
# dieselbe Bindung an den ersten Absatz wie .chapter-head in build.BASE_CSS
# (break-inside: avoid ist die Sperre, die WeasyPrint sicher umsetzt; s. chartdoc,
# .subwrap). Ohne Wrapper koennte der Kopf am Seitenfuss stehen bleiben und der
# Ausschnitt auf die naechste Seite rutschen.
AUSSCHNITT_CSS = """
.kopf-uhr { break-inside: avoid; break-after: avoid; }
.uhr-aus { margin: 0 0 0.46cm 0; break-inside: avoid; }
.uhr-aus img { width: 100%; display: block; }
"""


# 2026-09-30 (Klasse-2-Entscheidungslauf, Punkt 10; Pruefbericht Transit 3+4 vom
# 30.09., Klasse 2): Der laufende Knoten heisst im Datenstrom `Knoten`, der
# Radix-Knoten als Ziel `Mondknoten`. Ein Themen-Eintrag in der anderen
# Namensform traf keine Zeile, und die Linie fehlte in der Uhr, ohne dass es
# jemand merkte. Jetzt gelten beide Formen (wortweise, s. _nf()), und
# bloecke_zuordnen() meldet jeden Zieleintrag, der keine Zeile trifft.
_NAMENSFORM = {'Mondknoten': 'Knoten', 'Nordknoten': 'Knoten',
               'Aszendent': 'AC', 'Deszendent': 'DC'}


def _nf(s):
    """Namensform fuer den Vergleich, wortweise: `Mondknoten` und `Nordknoten`
    gelten als `Knoten`, `Aszendent` als `AC`, `Deszendent` als `DC`."""
    return ' '.join(_NAMENSFORM.get(w, w) for w in str(s).split())


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
    zn = {_nf(z) for z in ziele}
    return bool({_nf(r['ziel']), _nf(f"{r['aspekt']} {r['ziel']}"),
                 _nf(f"{r['transiter']} {r['ziel']}"),
                 _nf(f"{r['transiter']} {r['aspekt']} {r['ziel']}")} & zn)


def bloecke_zuordnen(ll, themen=None):
    """Ordnet die Langlaeufer-Zeilen den Themen zu und meldet, was sonst still
    verloren ginge. -> (bloecke, warnungen).

    Ein THEMEN-Eintrag ist (Name, Untertitel, [Transiter], Farbe) oder
    (Name, Untertitel, [Transiter], Farbe, [Ziele]); die Formen der Zielliste
    s. _passt(). Jede Zeile geht in das ERSTE passende Thema; ein Eintrag ohne
    Zielliste nimmt jede Zeile seiner Transiter. `warnungen` nennt jeden
    Zieleintrag, den KEINE Zeile der Transiter seines Themas trifft (meist die
    Schreibweise) — bauen() druckt sie mit „⚠ Transit-Uhr:" aus.
    """
    themen = THEMEN if themen is None else themen
    bloecke, vergeben, warnungen = [], set(), []
    for eintrag in themen:
        name, unter, transiter, col = eintrag[:4]
        ziele = eintrag[4] if len(eintrag) > 4 else None
        tr = {_nf(t) for t in transiter}
        eigene = [r for r in ll if _nf(r['transiter']) in tr]
        for z in (ziele or []):
            if not any(_passt(r, [z]) for r in eigene):
                warnungen.append(
                    f"Thema „{name}“: Zieleintrag „{z}“ trifft keine Zeile — "
                    f"Ziele der Transiter dort: "
                    f"{', '.join(sorted({r['ziel'] for r in eigene})) or 'keine'}")
        idx = [i for i, r in enumerate(ll)
               if i not in vergeben and _nf(r['transiter']) in tr
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
    return bloecke, warnungen


def stationen(daten):
    """Stationen der langsamen Planeten im Umfeld des Stichtags — nicht alle
    Stationen des Fensters (so auch der Uhr-Vorspann der Vorlage).

    Kommen aus dem §11-Block „Stationen im Umfeld des Stichtags"
    (transitdata.parse -> 'stationen'); gerechnet wird hier nichts. Faellt
    der Block aus, bleibt die Leiste einfach leer.
    """
    out = []
    for s in daten.get('stationen', []):
        out.append({'planet': s['planet'], 'datum': s['datum'],
                    'richtung': s['richtung']})
    return sorted(out, key=lambda x: x['datum'])


def monats_label(tage):
    """Beschriftung des Themenbogens aus seiner Spanne in Tagen: „unter 1 Monat",
    „1 Monat", „n Monate" (englisch nach setze_sprache('en')).

    2026-09-30 (Pruefbericht Transit 3+4 vom 30.09., Klasse 1): Ein Thema, das im
    Fenster nur rund zwei Wochen lief (am rechten Rand angeschnitten), bekam
    round(Tage / 30,44) = 0 und stand in der Uhr mit „0 Monate".
    """
    mon = round(tage / 30.44)
    if mon < 1:
        return LABELS.get('unter_monat', 'unter 1 Monat')
    return LABELS['monat'] if mon == 1 else LABELS['monate'].format(n=mon)


def _mpl():
    """matplotlib fuer beide Figuren (grosse Uhr, Ausschnitt): Agg, dieselben
    Fonts. -> (plt, mdates, Rectangle, FancyBboxPatch)"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = ['DejaVu Sans', 'FreeSerif', 'FreeSans']
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle, FancyBboxPatch
    return plt, mdates, Rectangle, FancyBboxPatch


def _grund(ax, daten, X0, X1, st, y_unten, y_oben, sk, mdates, Rectangle):
    """Hintergrund: Rueckblickzone, Quartalsbaender mit Beschriftung, rechter
    Rand, Stichtagslinie — grosse Uhr und Ausschnitt zeichnen ihn gleich."""
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


def _block(ax, b, y, X0, X1, sk, mdates, Rectangle, FancyBboxPatch,
           mit_name=True):
    """Einen Themenblock zeichnen — Kopf, Themenbogen, Detailzeilen — und das y
    unter seiner letzten Zeile zurueckgeben (ohne H_LUFT). Dieselbe Zeichnung
    fuer die grosse Uhr und den Ausschnitt; mit_name=False (Ausschnitt) setzt
    den Kopf einzeilig: Marke und Untertitel, ohne den Namen."""
    spanne = X1 - X0
    col = b['col']
    # Themenkopf: Name links am Satzspiegel, nie ueber den Rand hinaus
    ax.add_patch(Rectangle((X0 + spanne * 0.004, y - 0.30),
                           spanne * 0.0085, 0.60, facecolor=col,
                           edgecolor='none', zorder=5))
    if mit_name:
        ax.text(X0 + spanne * 0.019, y + 0.06, b['name'], ha='left',
                va='center', fontsize=9.6 * sk, color=DEEP, zorder=5)
        ax.text(X0 + spanne * 0.019, y - 0.50, b['unter'], ha='left',
                va='center', fontsize=7.6 * sk, color=STONE, zorder=5,
                style='italic')
        y -= H_KOPF
    else:
        ax.text(X0 + spanne * 0.019, y, b['unter'], ha='left',
                va='center', fontsize=8.4 * sk, color=STONE, zorder=5,
                style='italic')
        y -= H_KOPF_AUS

    # Themenbogen: Gesamtspanne des Themas, dick und weich
    A = max(mdates.date2num(b['start']), X0)
    B = min(mdates.date2num(b['ende']), X1)
    ax.add_patch(FancyBboxPatch((A, y - 0.28), B - A, 0.56,
                                boxstyle='round,pad=0,rounding_size=0.26',
                                facecolor=col, alpha=0.42,
                                edgecolor='none', zorder=2))
    lab = monats_label((b['ende'] - b['start']).days)
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
    return y


def _achse(ax, f, X0, X1, st, y_ach, sk, mdates):
    """Zeitachse mit Quartalsmarken, dazu „Rueckblick" und „Stichtag …" ueber
    der Linie — grosse Uhr und Ausschnitt zeichnen sie gleich."""
    spanne = X1 - X0
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


def bauen(out_path, daten, breite=12.4, dpi=210):
    """Die grosse Transit-Uhr als PNG -> (out_path, Zahl der Langlaeufer, Zahl
    der Stationen). Bloecke aus THEMEN ueber bloecke_zuordnen(); jeder Block
    wird mit _block() gezeichnet — derselben Funktion wie im Ausschnitt."""
    plt, mdates, Rectangle, FancyBboxPatch = _mpl()

    f = daten['fenster']
    ll = daten['langlaeufer']
    st_liste = stationen(daten)

    # --- Bloecke zusammenstellen, Hoehe vorab bestimmen ---------------------
    # Die Zielliste eines THEMEN-Eintrags ist noetig, sobald EIN laufender
    # Planet zwei Themenkapitel traegt oder ein Thema mehrere Transiter an
    # verschiedenen Zielen hat (Formen s. _passt(), Zuordnung s.
    # bloecke_zuordnen()).
    bloecke, warnungen = bloecke_zuordnen(ll)
    for w in warnungen:
        print('⚠ Transit-Uhr:', w)
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
    y_ach = H_ACHSE - 1.5
    _grund(ax, daten, X0, X1, st, y_ach, hoehe_e, sk, mdates, Rectangle)

    # --- Bloecke ------------------------------------------------------------
    y = hoehe_e - 2.15
    for b in bloecke:
        y = _block(ax, b, y, X0, X1, sk, mdates, Rectangle, FancyBboxPatch)
        y -= H_LUFT

    # --- Zeitachse ----------------------------------------------------------
    _achse(ax, f, X0, X1, st, y_ach, sk, mdates)

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
# Uhr-Ausschnitt am Kapitelanfang (neu 2026-10-11, Chris-Entscheidung nach einem
# Muster an einem echten Transit: Beim Lesen eines Kapitels wollte man immer
# zur Uhr hochblaettern, um zu sehen, wann und wie lange das Thema laeuft).
# Eine Von-bis-Zeile im Kolumnentitel war die Alternative und wurde verworfen: Die
# Uhr kennt nur das Fenster und waere neben einem Text, der ueber Jahre davor und
# danach spricht, ein Widerspruch; aus dem Text gelesen braeuchte sie ein neues
# Feld samt Probe.
# ---------------------------------------------------------------------------

_KONTAKT_RE = re.compile(r"T-(\w+)\s*([☌☍□△⚹⚻⚺])\s*R-([\wÄÖÜäöüß]+)")
_GLYPH_ASPEKT = {'☌': 'Konjunktion', '☍': 'Opposition', '□': 'Quadrat',
                 '△': 'Trigon', '⚹': 'Sextil', '⚻': 'Quincunx',
                 '⚺': 'Halbsextil'}


def _titel_norm(s):
    return ' '.join(str(s).split())


def ausschnitt(out_path, daten, name, breite=None, dpi=210, themen=None):
    """Ausschnitt der Transit-Uhr fuer EIN Themenkapitel -> out_path, oder None,
    wenn das Thema keinen Block hat.

    Gezeichnet wird genau der Block `name`, mit derselben Zuordnung wie in der
    grossen Uhr: bloecke_zuordnen() laeuft ueber ALLE Themen (`themen`, sonst
    THEMEN), denn jede Linie geht in das ERSTE passende Thema — wer die Liste
    vorher auf ein Thema filtert, zieht fremde Linien in den Block. Dazu
    Quartalskopf, Rueckblickzone, Stichtagslinie und Zeitachse; ohne den
    Themennamen (er steht als Kapiteltitel darueber) und ohne Stationsleiste.
    Links spannen die Beschriftungen ALLER Bloecke die Spalte unsichtbar auf,
    rechts ein unsichtbares „sekundär" am Fensterrand: So liegt die Zeitachse in
    jedem Ausschnitt eines Laufs an derselben Stelle.
    breite   Figurbreite in Zoll, Vorgabe AUS_BREITE; der Schriftgrad bleibt
             AUS_SK (der der grossen Uhr) — auf Satzbreite gesetzt wird der
             Ausschnitt dadurch groesser gedruckt als die Uhr selbst.
    """
    breite = AUS_BREITE if breite is None else breite
    f = daten['fenster']
    bloecke, _w = bloecke_zuordnen(daten['langlaeufer'], themen)
    b = next((x for x in bloecke if x['name'] == name), None)
    if b is None:
        return None
    plt, mdates, Rectangle, FancyBboxPatch = _mpl()

    hoehe_e = (H_KOPF_AUS + H_BOGEN + len(b['zeilen']) * H_ZEILE + H_LUFT
               + H_ACHSE_AUS + 1.00)
    sk = AUS_SK
    fig, ax = plt.subplots(figsize=(breite, 0.26 + hoehe_e * 0.206), dpi=dpi)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    X0 = mdates.date2num(f['rueckblick'])
    X1 = mdates.date2num(f['ende'])
    ax.set_xlim(X0, X1)
    ax.set_ylim(0, hoehe_e)
    ax.axis('off')
    spanne = X1 - X0

    st = mdates.date2num(f['stichtag'])
    y_ach = H_ACHSE_AUS - 1.5
    _grund(ax, daten, X0, X1, st, y_ach, hoehe_e, sk, mdates, Rectangle)
    # unsichtbare Anker — dieselbe Breite links und rechts in jedem Ausschnitt
    for bb in bloecke:
        for r in bb['zeilen']:
            ax.text(X0 - spanne * 0.008, hoehe_e - 2.0,
                    td.kurz(r['transiter'], r['aspekt'], r['ziel']),
                    ha='right', va='center', fontsize=7.2 * sk, alpha=0.0,
                    zorder=0)
    ax.text(X1 + spanne * 0.006, hoehe_e - 2.0, LABELS['sekundaer'],
            ha='left', va='center', fontsize=6.2 * sk, alpha=0.0, zorder=0)
    _block(ax, b, hoehe_e - 2.15, X0, X1, sk, mdates, Rectangle,
           FancyBboxPatch, mit_name=False)
    _achse(ax, f, X0, X1, st, y_ach, sk, mdates)

    fig.tight_layout(pad=0.4)
    fig.savefig(out_path, facecolor=PAPER, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    return out_path


def fuehrende_kontakte(chart_data):
    """{Thementitel: (Transiter, Aspekt, Ziel)} aus der Themenliste der
    chart_data (Pfad oder Text): je `THEMA n |`-Block das Feld `titel=` und der
    ERSTE Kontakt im Feld `fuehrt=`, in der Form `T-<Faktor> <Glyphe> R-<Faktor>`
    (dieselbe Form, die build.transit_beleg() liest). Ein Thema ohne lesbaren
    Kontakt fehlt im Ergebnis — ausschnitte() meldet es mit ⚠."""
    txt = str(chart_data)
    if '\n' not in txt and os.path.exists(txt):
        with open(txt, encoding='utf-8') as fh:
            txt = fh.read()
    out = {}
    for blk in re.split(r'\n(?=THEMA \d+ \|)', '\n' + txt)[1:]:
        mt = re.search(r'titel=([^\n|]+)', blk)
        mf = re.search(r'fuehrt=([^\n]*)', blk)
        if not mt or not mf:
            continue
        k = _KONTAKT_RE.search(mf.group(1))
        if k:
            out[_titel_norm(mt.group(1))] = (k.group(1),
                                             _GLYPH_ASPEKT[k.group(2)],
                                             k.group(3))
    return out


def _gezeichnet(b, kontakt):
    """Steht der Kontakt (Transiter, Aspekt, Ziel) als Zeile im Block?
    Namensformen wie in _passt() (`Mondknoten` = `Knoten`, `Aszendent` = `AC`)."""
    t, a, z = kontakt
    return any(_nf(r['transiter']) == _nf(t) and r['aspekt'] == a
               and _nf(r['ziel']) == _nf(z) for r in b['zeilen'])


def ausschnitte(daten, kapitel_titel, fuehrt, ordner='/home/claude',
                stamm='uhr_ausschnitt', themen=None, breite=None, dpi=210):
    """Alle Uhr-Ausschnitte eines Laufs -> ({Kapiteltitel: Dateiname}, bericht).

    Je THEMEN-Eintrag ein Ausschnitt (ausschnitt()), gespeichert unter
    <ordner>/<stamm>_<n>.png; der Dateiname im Ergebnis ist RELATIV, so steht er
    im HTML (gerendert wird mit Arbeitsverzeichnis /home/claude). KEIN
    Ausschnitt, mit einer Zeile in `bericht`, wenn das Thema keinen Block hat
    oder sein fuehrender Kontakt nicht in seinem Block gezeichnet ist: lieber
    kein Bild als eines, das die Kernmonate des Kapitels leer zeigt
    (Chris-Entscheidung 2026-10-11; Musterfall: ein Kapitel, das der laufende
    Mondknoten fuehrt — er laeuft zu schnell fuer die Uhr).
    kapitel_titel  die Titel ALLER Kapitel (items). Ein Themenname der Uhr, der
                   kein Kapiteltitel ist, bricht mit ValueError ab: Die Namen
                   sind wortgleich die Kapiteltitel (Design-Zeitebene-Modul) —
                   bis heute war das nur eine Leseregel.
    fuehrt         fuehrende_kontakte(<chart_data>). Ein Thema ohne lesbaren
                   Eintrag bekommt keinen Ausschnitt; seine Zeile im Bericht
                   beginnt mit ⚠ — eine kaputte Sache, kein Regelfall.
    """
    themen = THEMEN if themen is None else themen
    titel = {_titel_norm(t) for t in kapitel_titel}
    fremd = [e[0] for e in themen if _titel_norm(e[0]) not in titel]
    if fremd:
        raise ValueError(
            'Transit-Uhr: Themenname ohne gleichlautenden Kapiteltitel — '
            + '; '.join('„%s“' % n for n in fremd)
            + '. Die Namen in THEMEN sind wortgleich die Kapiteltitel der '
              'analyse.md (Design-Zeitebene-Modul).')
    fuehrt = {_titel_norm(k): v for k, v in dict(fuehrt or {}).items()}
    bloecke, _w = bloecke_zuordnen(daten['langlaeufer'], themen)
    nach_name = {b['name']: b for b in bloecke}
    aus, bericht = {}, []
    for n, eintrag in enumerate(themen, 1):
        name = eintrag[0]
        b = nach_name.get(name)
        if b is None:
            bericht.append('„%s“: kein Block in der Uhr — kein Ausschnitt' % name)
            continue
        k = fuehrt.get(_titel_norm(name))
        if k is None:
            bericht.append('⚠ „%s“: kein lesbarer fuehrt=-Kontakt in der '
                           'Themenliste — kein Ausschnitt' % name)
            continue
        if not _gezeichnet(b, k):
            bericht.append('„%s“: fuehrender Kontakt %s %s %s steht nicht im '
                           'Block der Uhr — kein Ausschnitt' % ((name,) + tuple(k)))
            continue
        datei = '%s_%d.png' % (stamm, n)
        ausschnitt(os.path.join(ordner, datei), daten, name, breite=breite,
                   dpi=dpi, themen=themen)
        aus[name] = datei
    return aus, bericht


def ausschnitt_html(datei):
    """Der Ausschnitt als HTML-Block — '' ohne Datei. Im Kapitel steht er nie
    allein, sondern ueber kopf_mit_ausschnitt() mit dem Kapitelkopf verbunden.
    Das CSS dazu ist AUSSCHNITT_CSS."""
    if not datei:
        return ''
    import html as _html
    return ('<div class="uhr-aus"><img src="%s" alt="%s"></div>'
            % (_html.escape(datei), _html.escape(LABELS['ausschnitt'])))


def kopf_mit_ausschnitt(kopf_html, datei):
    """Kapitelkopf + Ausschnitt als eine Einheit (`.kopf-uhr`): der Kopf aus
    chartdoc.build_head(it), dahinter der Ausschnitt, beides im Wrapper. Ohne
    Datei kommt der Kopf UNVERAENDERT zurueck — ein Kapitel ohne Ausschnitt
    rendert bytegleich wie vor dem 2026-10-11, der Aufruf darf also fuer jedes
    Kapitel stehen. Der erste Absatz bleibt Kind der Section; seine Bindung
    (`.chapter > p.first`, build.BASE_CSS) wirkt unveraendert."""
    if not datei:
        return kopf_html
    return '<div class="kopf-uhr">%s%s</div>' % (kopf_html, ausschnitt_html(datei))


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
    if '--selbsttest' in _s.argv:     # 2026-09-30: Monatsbeschriftung, beide Sprachen
        assert (monats_label(15), monats_label(30), monats_label(92)) == \
            ('unter 1 Monat', '1 Monat', '3 Monate'), monats_label(15)
        setze_sprache('en')
        assert (monats_label(0), monats_label(61)) == ('under 1 month', '2 months'), \
            monats_label(0)
        setze_sprache('de')
        # 2026-09-30: Namensform und Warnung (Klasse-2-Entscheidungslauf, Punkt 10)
        _ll = [{'transiter': 'Knoten', 'aspekt': 'Konjunktion', 'ziel': 'Mondknoten',
                'start': 1, 'ende': 2},
               {'transiter': 'Saturn', 'aspekt': 'Quadrat', 'ziel': 'Mond',
                'start': 1, 'ende': 3}]
        _b, _w = bloecke_zuordnen(_ll, [('A', 'a', ['Mondknoten'], '#000', ['Knoten']),
                                        ('B', 'b', ['Saturn'], '#000', ['Saturn Mondknoten'])])
        assert [len(x['zeilen']) for x in _b] == [1], _b
        assert len(_w) == 1 and '„Saturn Mondknoten“' in _w[0] and 'Mond' in _w[0], _w
        _b2, _w2 = bloecke_zuordnen(_ll, [('B', 'b', ['Saturn'], '#000', ['Quadrat Mond'])])
        assert [len(x['zeilen']) for x in _b2] == [1] and not _w2, (_b2, _w2)
        # 2026-10-11: Uhr-Ausschnitt — Themenliste lesen, Auslassregel, Namensprobe,
        # Kopf ohne Ausschnitt unveraendert (anonyme Daten, nichts wird gezeichnet)
        _tl = ('## Themenliste\n\nTHEMA 1 | titel=Erstes Thema\n  | fuehrt=T-Saturn □ R-Mond\n'
               '  | aspekte=T-Pluto ⚻ R-Merkur\nTHEMA 2 | titel=Zweites Thema\n'
               '  | fuehrt=T-Mondknoten ☍ R-Sonne\nTHEMA 3 | titel=Drittes Thema\n'
               '  | fuehrt=keine Form\n')
        _fk = fuehrende_kontakte(_tl)
        assert _fk == {'Erstes Thema': ('Saturn', 'Quadrat', 'Mond'),
                       'Zweites Thema': ('Mondknoten', 'Opposition', 'Sonne')}, _fk
        _th = [('Erstes Thema', 'a', ['Saturn'], '#000', ['Saturn Mond']),
               ('Zweites Thema', 'b', ['Saturn'], '#000', ['Saturn Sonne']),
               ('Drittes Thema', 'c', ['Pluto'], '#000')]
        _ll3 = [{'transiter': 'Saturn', 'aspekt': 'Trigon', 'ziel': 'Sonne',
                 'start': 1, 'ende': 2}]
        _a3, _r3 = ausschnitte({'langlaeufer': _ll3},
                               ['Erstes Thema', 'Zweites Thema', 'Drittes Thema'],
                               _fk, themen=_th)
        assert _a3 == {} and len(_r3) == 3, (_a3, _r3)
        assert 'kein Block' in _r3[0] and 'steht nicht im' in _r3[1] \
            and 'kein Block' in _r3[2], _r3
        assert _gezeichnet({'zeilen': _ll3}, ('Saturn', 'Trigon', 'Sonne'))
        assert not _gezeichnet({'zeilen': _ll3}, ('Mondknoten', 'Opposition', 'Sonne'))
        try:
            ausschnitte({'langlaeufer': _ll3}, ['Erstes Thema'], _fk, themen=_th)
            raise AssertionError('Namensprobe: kein Abbruch')
        except ValueError as _e:
            assert 'Zweites Thema' in str(_e), _e
        assert kopf_mit_ausschnitt('<div>K</div>', None) == '<div>K</div>'
        assert kopf_mit_ausschnitt('<div>K</div>', 'a.png').startswith(
            '<div class="kopf-uhr"><div>K</div><div class="uhr-aus">')
        print('Selbsttest bestanden: Monatsbeschriftung deutsch und englisch; '
              'Namensform Knoten/Mondknoten und Warnung bei Zieleintrag ohne Treffer; '
              'Uhr-Ausschnitt (Themenliste, Auslassregel, Namensprobe, Kopf)')
        _s.exit(0)
    import transitdata as _td
    quelle = _s.argv[2] if len(_s.argv) > 2 else None
    p, n, ns = bauen(_s.argv[1] if len(_s.argv) > 1 else
                     '/home/claude/transituhr.png', _td.parse(quelle))
    print('geschrieben:', p, '|', n, 'Linien,', ns, 'Stationen')
