#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selektor.py — Schritt-2-Referenzschnitt.

Liest aus <klient>_chart_data.md den maschinenlesbaren @@SELEKTOR-Block,
leitet nach Plan §5 die benoetigten Blockschluessel ab, zieht NUR diese Bloecke
aus blocks/ und schreibt eine kompakte <klient>_referenz.md.

PFLICHT-Vollstaendigkeitspruefung: fuer JEDEN Faktor und JEDEN Aspekt wird
protokolliert, welche Bloecke gezogen wurden. Fehlt ein abgeleiteter Block in
blocks/ -> HARTER Fehler mit Namen (nie stilles Weglassen). Lieber ein Block zu
viel.

GRENZLAGEN (5°-Haus-Regel, s. radix.haus_und_grenzlage): Steht ein Faktor 5° oder
weniger VOR der naechsten Hausspitze, faerbt er das Folgehaus mit. Schritt 1 haengt
dann `nebenhaus=<N> abstand=<Grad>` an die FAKTOR-Zeile; der Selektor zieht BEIDE
Hausbloecke und schreibt die Gewichtungsstufe als Deutungsanweisung in die
referenz.md (Abstand <= 2° -> Nebenhaus fuehrt; 2°-5° -> Nebenhaus als Nebenton).
Ohne `nebenhaus=` verhaelt sich alles wie zuvor.

FAKTORNAMEN: kanonisch sind die zehn Planeten und die fuenf Spezialfaktoren
CHIRON, LILITH, MONDKNOTEN, PHOLUS, GLUECKSPUNKT. Gaengige Schreibweisen loest
FAKTOR_ALIAS auf (KNOTEN/NORDKNOTEN -> MONDKNOTEN, VERMOEGEN -> GLUECKSPUNKT ...).
Die Knotenachse wird IMMER ueber die Nordknoten-Zeile gefuehrt — eine eigene
SUEDKNOTEN-Zeile wird uebersprungen und protokolliert, weil die Referenz
achsenbasiert ist (MONDKNOTEN_HAUS_6 = ☊6/☋12) und eine zweite Zeile mit haus=12
die GESPIEGELTE Achse zoege. Ein Faktorname, der sich nicht aufloesen laesst, ist
seit 30.07.2026 ein HARTER Fehler (vorher fiel er lautlos durch, s. Kommentar bei
FAKTOR_ALIAS).

FUEHRT-FELD (seit 2026-09-06): Traegt eine FAKTOR-Zeile `fuehrt=ja`, fuehrt
dieser Faktor laut Themenliste ein Kapitel. Zwei Wirkungen: (a) bei einem
Spezialfaktor werden seine Methoden-Segmente (_ALLG/_SEC_*) in die normale
Gruppe gezogen statt in die ueberspringbare 'Spezialfaktor-Methodik'; (b) der
Grenzlagen-Warnblock sagt je Faktor, ob beide Haeuser auszudeuten sind oder ob
beide nur in seiner Zeile im Rechenschaftskapitel stehen. Ohne das Feld
verhaelt sich alles wie zuvor — das Feld ist optional und additiv.

@@SELEKTOR-Blockformat (Schritt 1 schreibt ihn ins chart_data.md):
    @@SELEKTOR
    FAKTOR SONNE zeichen=Krebs haus=11 nebenhaus=12 abstand=3.22 fuehrt=ja
    FAKTOR MOND zeichen=Krebs haus=12 fuehrt=ja
    ...
    FAKTOR MONDKNOTEN zeichen=Wassermann haus=6
    FAKTOR PHOLUS zeichen=Fische haus=7 nebenhaus=8 abstand=4.17
    FAKTOR GLUECKSPUNKT zeichen=Fische haus=7
    ACHSE AC zeichen=Loewe
    ACHSE MC zeichen=Widder
    ASPEKT SONNE MOND
    ASPEKT MARS AC
    ...
    @@ENDE

Aufruf:  python3 selektor.py <chart_data.md> [blocks_dir] [out.md]
"""
import os
import re
import sys

PLANETS = ['SONNE', 'MOND', 'MERKUR', 'VENUS', 'MARS', 'JUPITER', 'SATURN',
           'URANUS', 'NEPTUN', 'PLUTO']
PSET = set(PLANETS)
MARK_RE = re.compile(r'^@@BLOCK key=(\S+)@@$')

# --- Faktornamen: Schreibweisen -> kanonischer Blockschluessel ---------------
# Grund (Vorfall 30.07.2026): parse_chart normalisierte FAKTOR-Zeilen nur mit
# norm(); `FAKTOR KNOTEN` blieb also 'KNOTEN' und lag weder in PSET noch in
# SPEZFILE. Der Faktor fiel LAUTLOS durch — keine Bloecke, keine Fehlstelle,
# keine Warnung. Die komplette Mondknoten-Deutung (Zeichen UND Haus) fehlte im
# Referenzschnitt, und der Lauf meldete trotzdem "keine Fehlstelle". Seither:
# (a) Aliasse werden aufgeloest, (b) ein unbekannter Faktorname ist ein HARTER
# Fehler wie eine Fehlstelle.
FAKTOR_ALIAS = {
    'KNOTEN': 'MONDKNOTEN', 'NORDKNOTEN': 'MONDKNOTEN',
    'MONDKNOTENACHSE': 'MONDKNOTEN', 'KNOTENACHSE': 'MONDKNOTEN',
    'AUFSTEIGENDER MONDKNOTEN': 'MONDKNOTEN', 'DRACHENKOPF': 'MONDKNOTEN',
    'SCHWARZER MOND': 'LILITH', 'LILITH (SCHWARZER MOND)': 'LILITH',
    'PARS FORTUNAE': 'GLUECKSPUNKT', 'VERMOEGEN': 'GLUECKSPUNKT',
    'GLUECKSPUNKT (PARS FORTUNAE)': 'GLUECKSPUNKT',
    'ASZENDENT': 'AC', 'DESZENDENT': 'DC',
    'MEDIUM COELI': 'MC', 'IMUM COELI': 'IC', 'IMMUM COELI': 'IC',
}

# Faktoren, die KEINE eigene Deutung bekommen, weil sie der Spiegelpol eines
# bereits gefuehrten Faktors sind. Der Suedknoten wird ueber die Nordknoten-
# Zeile mitgedeutet: die Mondknoten-Referenz ist achsenbasiert (MONDKNOTEN_HAUS_6
# behandelt ☊6/☋12). Eine eigene Suedknoten-Zeile mit haus=12 zoege
# MONDKNOTEN_HAUS_12 — also die GESPIEGELTE Achse und damit die falsche Deutung.
SPIEGEL_FAKTOREN = {
    'SUEDKNOTEN': 'MONDKNOTEN', 'ABSTEIGENDER MONDKNOTEN': 'MONDKNOTEN',
    'DRACHENSCHWANZ': 'MONDKNOTEN',
}

# Grenzlagen-Schwellen (Grad vor der naechsten Hausspitze).
GRENZ_ORB = 5.0      # bis hierher gilt ueberhaupt Grenzlage (= radix.HAUS_ORB)
SCHWELLE_ORB = 2.0   # bis hierher fuehrt das Nebenhaus die Deutung

STEM = {'WIDDER': 'Widder', 'STIER': 'Stier', 'ZWILLINGE': 'Zwillinge',
        'KREBS': 'Krebs', 'LOEWE': 'Loewe', 'JUNGFRAU': 'Jungfrau',
        'WAAGE': 'Waage', 'SKORPION': 'Skorpion', 'SCHUETZE': 'Schuetze',
        'STEINBOCK': 'Steinbock', 'WASSERMANN': 'Wassermann', 'FISCHE': 'Fische'}
ASPSTEM = {'SONNE': 'Sonne', 'MOND': 'Mond', 'MERKUR': 'Merkur', 'VENUS': 'Venus',
           'MARS': 'Mars', 'JUPITER': 'Jupiter', 'SATURN': 'Saturn',
           'URANUS': 'Uranus', 'NEPTUN': 'Neptun', 'PLUTO': 'Pluto'}

F02, F03, F04, F01 = ('02_Sonne_und_Mond_in_Zeichen.txt',
                      '03_Merkur_Venus_Mars_in_Zeichen.txt',
                      '04_Jupiter_Saturn_Generationsplaneten.txt',
                      '01_Planeten_Grundprinzipien.txt')
F05 = '05_Aszendent_MC_Deszendent_Tabellen.txt'
SPEZFILE = {'CHIRON': 'Chiron_Haus_Zeichen_Aspekte.txt',
            'LILITH': 'Lilith_SchwarzerMond_Haus_Zeichen_Aspekte.txt',
            'MONDKNOTEN': 'Mondknotenachse_Haus_Zeichen_Aspekte.txt',
            'PHOLUS': 'Pholus_Haus_Zeichen_Aspekte.txt',
            'GLUECKSPUNKT': 'Glueckspunkt_Haus_Zeichen_Aspekte.txt'}
ZEICHENFILE = {'SONNE': F02, 'MOND': F02, 'MERKUR': F03, 'VENUS': F03,
               'MARS': F03, 'JUPITER': F04, 'SATURN': F04,
               'URANUS': F01, 'NEPTUN': F01, 'PLUTO': F01}


def norm(s):
    s = (s or '').strip().upper()
    for a, b in (('Ö', 'OE'), ('Ü', 'UE'), ('Ä', 'AE'), ('ß', 'SS')):
        s = s.replace(a, b)
    return s


def norm_faktor(t):
    """Kanonischer Faktorname fuer FAKTOR-Zeilen (Zeichen-/Hausbloecke).

    Anders als norm_token (das fuer ASPEKT-Zeilen alle Knoten-Schreibweisen auf
    'KNOTEN' zusammenzieht, weil resolve_aspect diesen Token erwartet) liefert
    diese Funktion den Schluessel, unter dem PSET/SPEZFILE nachschlagen —
    fuer die Knotenachse also 'MONDKNOTEN'.
    """
    t = norm(t)
    return FAKTOR_ALIAS.get(t, t)


def norm_token(t):
    t = norm(t)
    if t in ('KNOTEN', 'MONDKNOTEN', 'NORDKNOTEN', 'SUEDKNOTEN', 'AUFSTEIGENDER MONDKNOTEN'):
        return 'KNOTEN'
    if t in ('ASZENDENT', 'AC'):
        return 'AC'
    if t in ('DESZENDENT', 'DC'):
        return 'DC'
    if t in ('MC', 'MEDIUM COELI'):
        return 'MC'
    if t in ('IC', 'IMUM COELI', 'IMMUM COELI'):
        return 'IC'
    return t


def haus_file(n):
    n = int(n)
    return 'Haus_0%d_Planeten.txt' % n if 1 <= n <= 6 else 'Haus_%d.txt' % n


def aspekt_file(pl):
    return ASPSTEM[pl] + '_Aspekte.txt'


def _gradmin(deg):
    """Dezimalgrad -> N°NN′ (fuer Signatur/Beleg im Klartext-Modus)."""
    try:
        d = float(deg)
    except (TypeError, ValueError):
        return '?'
    g = int(d)
    m = int(round((d - g) * 60))
    if m == 60:
        g, m = g + 1, 0
    return '%d°%02d′' % (g, m)


def grenz_stufe(abstand):
    """Gewichtungsstufe der Grenzlage als Klartext-Deutungsanweisung.

    <= SCHWELLE_ORB (2°): der Faktor sitzt praktisch auf der Spitze -> das
    Nebenhaus fuehrt die Deutung. Darueber bis GRENZ_ORB (5°): das rechnerische
    Haus fuehrt, das Nebenhaus klingt als deutlicher Nebenton mit.
    """
    try:
        a = float(abstand)
    except (TypeError, ValueError):
        return 'fuehrend', 'Abstand nicht angegeben — beide Haeuser gleichrangig deuten'
    if a <= SCHWELLE_ORB:
        return 'nebenhaus_fuehrt', (
            'Schwellenlage (%.2f° vor der Spitze): das NEBENHAUS fuehrt die '
            'Deutung, das rechnerische Haus klingt mit' % a)
    return 'nebenton', (
        'Grenzlage (%.2f° vor der Spitze): das rechnerische Haus fuehrt, das '
        'Nebenhaus als deutlicher Nebenton' % a)


def signatur_notation(g):
    """Fertige Signatur-Zeile fuer den Klartext-Modus (Schritt 2 uebernimmt sie 1:1).

    Das fuehrende Haus steht vorn. Gradzahl und Hausnummern gehoeren im
    Klartext-Modus ausschliesslich in Signatur/Beleg, nie in den Fliesstext.
    """
    h, nh = g['haus'], g['nebenhaus']
    grad = _gradmin(g['abstand'])
    if g['stufe'] == 'nebenhaus_fuehrt':
        return ('Haus %s/%s (Schwellenlage, %s vor Spitze %s; Haus %s fuehrt, '
                '%s klingt mit)' % (nh, h, grad, nh, nh, h))
    return ('Haus %s/%s (Grenzlage, %s vor Spitze %s; Haus %s fuehrt, '
            '%s klingt mit)' % (h, nh, grad, nh, h, nh))


# ---------------------------------------------------------------- Eingabe
def parse_chart(text):
    """-> dict: faktoren [{name,zeichen,haus,nebenhaus,abstand}], achsen, aspekte,
    spiegel [(rohname, kanonisch)]"""
    faktoren, achsen, aspekte, spiegel, hinweise = [], {}, [], [], []
    inblock = False
    for ln in text.split('\n'):
        s = ln.strip()
        if s == '@@SELEKTOR':
            inblock = True
            continue
        if s == '@@ENDE':
            inblock = False
            continue
        if not inblock or not s or s.startswith('#'):
            continue
        parts = s.split()
        kw = parts[0].upper()
        if kw == 'FAKTOR':
            roh = norm(' '.join(p for p in parts[1:] if '=' not in p))
            # ACHSEN-RETTUNG (neu 2026-09-06, Pruefbericht Transit 1.8):
            # Das Schluesselwort ACHSE stand in keinem Modul; das Blockformat
            # des Datenblatt-Moduls zeigt nur FAKTOR- und ASPEKT-Zeilen. Wer
            # `FAKTOR AC zeichen=Stier` schrieb, lief in den harten Abbruch
            # "UNBEKANNTE FAKTOREN". Solche Zeilen werden jetzt als ACHSE
            # gelesen — nicht still, sondern mit sichtbarem Hinweis samt der
            # richtigen Zeile, damit der Block korrigiert wird.
            if norm_token(roh) in ('AC', 'MC', 'DC', 'IC'):
                ax = norm_token(roh); z = None
                for q in parts[2:]:
                    if q.lower().startswith('zeichen='):
                        z = norm(q.split('=', 1)[1])
                achsen[ax] = z
                hinweise.append(
                    'FAKTOR %s ... -> als ACHSE gelesen. Richtig waere: '
                    'ACHSE %s zeichen=%s' % (ax, ax, z or '<Zeichen>'))
                continue
            if roh in SPIEGEL_FAKTOREN:
                # Spiegelpol: wird ueber die Gegen-Zeile als Achse mitgedeutet.
                # Eigene Bloecke wuerden die Achse gespiegelt ziehen (s. o.).
                #
                # SEIT 2026-09-06 (Pruefbericht EA 1.1): Uebersprungen werden nur
                # die BLOECKE. Grenzlage und `fuehrt=ja` gehen NICHT mehr
                # verloren — im EA fuehrt der Suedknoten ein eigenes Kapitel und
                # muss dann in BEIDEN Haeusern gedeutet werden. Vorher fiel er
                # lautlos aus dem ⚠-Grenzlagenblock, obwohl das Datenblatt-Modul
                # die Zwei-Haeuser-Deutung fuer jeden fuehrenden Faktor verlangt.
                sp = {'name': norm_faktor(roh), 'zeichen': None, 'haus': None,
                      'nebenhaus': None, 'abstand': None, 'fuehrt': False,
                      'spiegel_von': SPIEGEL_FAKTOREN[roh]}
                for p in parts[2:]:
                    pl = p.lower()
                    if pl.startswith('zeichen='):
                        sp['zeichen'] = norm(p.split('=', 1)[1])
                    elif pl.startswith('nebenhaus='):
                        sp['nebenhaus'] = p.split('=', 1)[1]
                    elif pl.startswith('haus='):
                        sp['haus'] = p.split('=', 1)[1]
                    elif pl.startswith('abstand='):
                        sp['abstand'] = p.split('=', 1)[1]
                    elif pl.startswith('fuehrt='):
                        sp['fuehrt'] = p.split('=', 1)[1].strip().lower() in (
                            'ja', 'j', 'true', '1')
                spiegel.append((roh, SPIEGEL_FAKTOREN[roh]))
                faktoren.append(sp)
                continue
            name = norm_faktor(roh)
            zeichen = haus = nebenhaus = abstand = None
            fuehrt = False
            for p in parts[2:]:
                pl = p.lower()
                if pl.startswith('zeichen='):
                    zeichen = norm(p.split('=', 1)[1])
                elif pl.startswith('nebenhaus='):
                    nebenhaus = p.split('=', 1)[1]
                elif pl.startswith('haus='):
                    haus = p.split('=', 1)[1]
                elif pl.startswith('abstand='):
                    abstand = p.split('=', 1)[1]
                elif pl.startswith('fuehrt='):
                    fuehrt = p.split('=', 1)[1].strip().lower() in (
                        'ja', 'j', 'true', '1')
            faktoren.append({'name': name, 'zeichen': zeichen, 'haus': haus,
                             'nebenhaus': nebenhaus, 'abstand': abstand,
                             'fuehrt': fuehrt})
        elif kw == 'ACHSE':
            ax = norm_token(parts[1])
            z = None
            for p in parts[2:]:
                if p.lower().startswith('zeichen='):
                    z = norm(p.split('=', 1)[1])
            achsen[ax] = z
        elif kw == 'ASPEKT':
            if len(parts) >= 3:
                aspekte.append((norm_token(parts[1]), norm_token(parts[2])))
    return {'faktoren': faktoren, 'achsen': achsen, 'aspekte': aspekte,
            'spiegel': spiegel, 'unbekannt': [], 'hinweise': hinweise}


# ---------------------------------------------------------------- Bloecke laden
FILE_RE = re.compile(r'^@@FILE=(.+)@@$')


def _parse_blocks(text):
    """block-markierter Text -> dict key->text (Marker entfernt)."""
    blocks, key, buf = {}, None, []
    for ln in text.split('\n'):
        m = MARK_RE.match(ln)
        if m:
            if key is not None:
                blocks[key] = '\n'.join(buf).strip('\n')
            key, buf = m.group(1), []
        else:
            buf.append(ln)
    if key is not None:
        blocks[key] = '\n'.join(buf).strip('\n')
    return blocks


def load_blocks(path):
    return _parse_blocks(open(path, encoding='utf-8').read())


def load_bundle(path):
    """Bündel (@@FILE=name@@-getrennt) -> dict dateiname -> {key->text}."""
    out, cur, buf = {}, None, []
    for ln in open(path, encoding='utf-8').read().split('\n'):
        m = FILE_RE.match(ln)
        if m:
            if cur is not None:
                out[cur] = _parse_blocks('\n'.join(buf))
            cur, buf = m.group(1), []
        else:
            buf.append(ln)
    if cur is not None:
        out[cur] = _parse_blocks('\n'.join(buf))
    return out


# ---------------------------------------------------------------- Ableitung
SPEZSET = ('CHIRON', 'LILITH', 'PHOLUS', 'GLUECKSPUNKT')


def resolve_aspect(a, b):
    """-> (srcfile, key, note) oder (None,None,note) fuer nicht-block-gefuehrt."""
    # Planet–Planet: kanonisch nach Planetenordnung
    if a in PSET and b in PSET:
        x, y = sorted([a, b], key=PLANETS.index)
        return aspekt_file(x), '%s_%s' % (x, y), None
    # Mondknoten mit Planet oder Achse -> reichere Achsendatei
    if 'KNOTEN' in (a, b):
        other = b if a == 'KNOTEN' else a
        if other in PSET or other in ('AC', 'MC'):
            return SPEZFILE['MONDKNOTEN'], 'MONDKNOTEN_' + other, None
        if other in ('DC', 'IC'):
            ax2 = 'AC' if other == 'DC' else 'MC'
            return SPEZFILE['MONDKNOTEN'], 'MONDKNOTEN_' + ax2, 'für %s an der Achse gekippt' % other
        return None, None, 'nicht als Block geführt (%s-%s)' % (a, b)
    # Spezialfaktor (Chiron/Lilith/Pholus/Glückspunkt) mit Planet oder Achse
    for sp in SPEZSET:
        if sp in (a, b):
            other = b if a == sp else a
            if other in PSET or other in ('AC', 'MC'):
                return SPEZFILE[sp], '%s_%s' % (sp, other), None
            if other in ('DC', 'IC'):
                ax2 = 'AC' if other == 'DC' else 'MC'
                return SPEZFILE[sp], '%s_%s' % (sp, ax2), 'für %s gekippt' % other
            return None, None, 'nicht als Block geführt (%s-%s)' % (a, b)
    # Planet mit Achse
    pl = a if a in PSET else (b if b in PSET else None)
    ax = b if a in PSET else a
    if pl and ax in ('AC', 'MC'):
        return aspekt_file(pl), '%s_%s' % (pl, ax), None
    if pl and ax == 'DC':
        return aspekt_file(pl), '%s_AC' % pl, 'für DC an der Horizontachse gekippt gelesen'
    if pl and ax == 'IC':
        return aspekt_file(pl), '%s_MC' % pl, 'für IC am MC gekippt gelesen'
    return None, None, 'nicht als Block geführt (Achse-Achse/außersystemisch)'


def build_requests(chart):
    """-> (requests, protocol, grenzlagen)   request=(gruppe, srcfile, key, note)"""
    req, prot, grenz = [], [], []
    haeuser = set()

    def add(gruppe, src, key, note=None):
        req.append((gruppe, src, key, note))

    # Grundlagen 01 (alle Prinzip-Segmente GRUNDLAGEN_* immer; Wildcard =
    # robust gegen kuenftige Aenderung der Segmentzahl in 01)
    add('Grundlagen', F01, 'GRUNDLAGEN_*')

    fak_by = {f['name']: f for f in chart['faktoren']}
    # Sonnenzeichen-Doppelquelle
    if 'SONNE' in fak_by and fak_by['SONNE']['zeichen']:
        sz = fak_by['SONNE']['zeichen']
        gruppe_sz = ('Sonnenzeichen' if fak_by['SONNE'].get('fuehrt')
                     else 'Sonnenzeichen-Hintergrund')
        add(gruppe_sz, STEM[sz] + '_Sonnenzeichen.txt', 'SONNENZEICHEN_' + sz)

    for f in chart['faktoren']:
        nm, z, h = f['name'], f['zeichen'], f['haus']
        nh, ab = f.get('nebenhaus'), f.get('abstand')
        got = []
        if nh:
            stufe, text = grenz_stufe(ab)
            grenz.append({'faktor': nm, 'haus': h, 'nebenhaus': nh,
                          'abstand': ab, 'stufe': stufe, 'text': text,
                          'fuehrt': bool(f.get('fuehrt')),
                          'spiegel_von': f.get('spiegel_von')})
        if f.get('spiegel_von'):
            # Blockanfragen bewusst NICHT stellen: Die Deutung kommt gespiegelt
            # ueber den Gegenpol. Die Grenzlage oben ist der Teil, der bleibt.
            prot.append('%-14s -> keine eigenen Bloecke (Spiegelpol von %s); '
                        'Grenzlage bleibt im ⚠-Block%s'
                        % (nm, f['spiegel_von'],
                           ', FUEHRT ein Thema' if f.get('fuehrt') else ''))
            continue
        if nm in PSET:
            if z:
                add('Planet-in-Zeichen', ZEICHENFILE[nm], '%s_IN_%s' % (nm, z))
                got.append('%s_IN_%s' % (nm, z))
            if h:
                add('Planet-in-Haus', haus_file(h), '%s_HAUS_%s' % (nm, h))
                got.append('%s_HAUS_%s' % (nm, h))
                haeuser.add(int(h))
            if nh:
                add('Planet-in-Haus', haus_file(nh), '%s_HAUS_%s' % (nm, nh),
                    'Grenzlage aus Haus %s' % h)
                got.append('%s_HAUS_%s [Grenzlage]' % (nm, nh))
                haeuser.add(int(nh))
        elif nm in SPEZFILE:
            src = SPEZFILE[nm]
            # Die vier Methoden-Segmente eines Spezialfaktors (Quellenlage,
            # Umlaufzeiten, Deutungsregeln) sind in JEDEM Lauf identisch und
            # haben keinen Bezug zum konkreten Chart — bei fuenf
            # Spezialfaktoren rund 700 Zeilen. Sie stehen deshalb seit dem
            # 2026-09-06 in einer EIGENEN Gruppe ganz am Ende der referenz.md
            # und sind dort ueberspringbar wie die GRUNDLAGEN_*-Segmente
            # (Werkzeug-Modul, Punkt 2). Fuehrt der Faktor ein Thema
            # (`fuehrt=ja` in der FAKTOR-Zeile), traegt seine Methodik die
            # Deutung mit und wandert in die normale Gruppe, wird also gelesen.
            gruppe_meth = ('Spezialfaktor' if f.get('fuehrt')
                           else 'Spezialfaktor-Methodik')
            for suf in ('ALLG', 'SEC_HAUS', 'SEC_ZEICHEN', 'SEC_ASPEKT'):
                add(gruppe_meth, src, '%s_%s' % (nm, suf))
            if z:
                add('Spezialfaktor', src, '%s_IN_%s' % (nm, z))
                got.append('%s_IN_%s' % (nm, z))
            if h:
                add('Spezialfaktor', src, '%s_HAUS_%s' % (nm, h))
                got.append('%s_HAUS_%s' % (nm, h))
                if nm == 'MONDKNOTEN':
                    haeuser.add(int(h))
            if nh:
                add('Spezialfaktor', src, '%s_HAUS_%s' % (nm, nh),
                    'Grenzlage aus Haus %s' % h)
                got.append('%s_HAUS_%s [Grenzlage]' % (nm, nh))
                if nm == 'MONDKNOTEN':
                    haeuser.add(int(nh))
        else:
            # Weder Planet noch bekannter Spezialfaktor: FRUEHER fiel dieser
            # Faktor lautlos durch (keine Bloecke, keine Fehlstelle). Jetzt
            # harter Fehler — eine geschluckte Deutung faellt sonst erst beim
            # Korrekturlesen des fertigen PDFs auf, wenn ueberhaupt.
            chart.setdefault('unbekannt', []).append(nm)
            prot.append('FAKTOR %-13s -> UNBEKANNT (keine Bloecke gezogen!)' % nm)
            continue
        prot.append('FAKTOR %-13s -> %s' % (nm, ', '.join(got) or '(nur ALLG/SEC)'))

    # Haus-Allgemein je belegtem Haus (Grenzlagen-Nebenhaeuser eingeschlossen)
    for n in sorted(haeuser):
        add('Haus-Allgemein', haus_file(n), 'HAUS_%d_ALLG' % n)

    # Achsen
    ac = chart['achsen']
    if ac.get('AC'):
        add('Achsen', F05, 'ASZENDENT_' + ac['AC'])
        prot.append('ACHSE AC (%s) -> ASZENDENT_%s' % (ac['AC'], ac['AC']))
    if 'MC' in ac:
        add('Achsen', F05, 'MC_IN_ZEICHEN')
        prot.append('ACHSE MC -> MC_IN_ZEICHEN')
    if 'DC' in ac:
        add('Achsen', F05, 'DESZENDENT_TABELLE')
    if 'IC' in ac:
        add('Achsen', F04, 'IC_IN_ZEICHEN')

    # Aspekte
    for a, b in chart['aspekte']:
        src, key, note = resolve_aspect(a, b)
        if key:
            add('Aspekte', src, key, note)
            prot.append('ASPEKT %s-%s -> %s%s' % (a, b, key, ' [' + note + ']' if note else ''))
        else:
            prot.append('ASPEKT %s-%s -> %s' % (a, b, note))
    return req, prot, grenz


# ---------------------------------------------------------------- Assemblage
# Reihenfolge der Abschnitte in der referenz.md. 'Spezialfaktor-Methodik'
# steht bewusst GANZ HINTEN, direkt vor dem Auswahl-Protokoll: Der Abschnitt
# ist ueberspringbar (s. build_requests), und was uebersprungen werden darf,
# gehoert ans Ende, damit der Schnitt ohne Suchen moeglich ist.
GRUPPEN = ['Planet-in-Zeichen', 'Planet-in-Haus', 'Haus-Allgemein', 'Achsen',
           'Spezialfaktor', 'Sonnenzeichen', 'Aspekte',
           'Sonnenzeichen-Hintergrund', 'Grundlagen', 'Spezialfaktor-Methodik']

# Gruppen, die Schritt 2 ueberspringen DARF (nicht muss). Der Kopf der
# referenz.md weist sie mit Zeilenzahl aus, damit die Ersparnis sichtbar ist.
#
# SEIT 2026-09-06 (Pruefbericht EA 1.9/4.1 und Rubrik 2): Die drei
# ueberspringbaren Gruppen stehen jetzt tatsaechlich am ENDE der GRUPPEN-Liste —
# vorher stand `Grundlagen` an erster Stelle, obwohl Modul und Quellkommentar
# behaupteten, sie stuenden hinten. `Sonnenzeichen-Hintergrund` ist neu: Das
# Sonnenzeichen-Kapitel der Bibliothek (Thema, Motivation, Psychologie,
# Lernaufgabe, Lebensziel, Symbol) ist rund 400 Zeilen Buchtext ueber das ZEICHEN
# und in jedem Lauf mit demselben Sonnenzeichen identisch; die chart-spezifische
# Stellung traegt der getrennte Block SONNE_IN_<Zeichen>. Fuehrt die Sonne ein
# Thema (`fuehrt=ja`), bleibt das Kapitel in der normal zu lesenden Gruppe
# `Sonnenzeichen` — dort traegt es die Deutung tatsaechlich mit.
UEBERSPRINGBAR = ('Sonnenzeichen-Hintergrund', 'Grundlagen',
                  'Spezialfaktor-Methodik')


def select(chart_text, blocks_ref):
    """blocks_ref = Verzeichnis blocks/ ODER Bündeldatei blocks_bundle.txt."""
    chart = parse_chart(chart_text)
    req, prot, grenz = build_requests(chart)
    bundle = None if os.path.isdir(blocks_ref) else load_bundle(blocks_ref)
    cache = {}

    def blocks_of(src):
        if bundle is not None:
            return bundle.get(src, {})
        if src not in cache:
            p = os.path.join(blocks_ref, src)
            cache[src] = load_blocks(p) if os.path.exists(p) else {}
        return cache[src]

    missing, seen, ordered = [], set(), []
    for gruppe, src, key, note in req:
        bl = blocks_of(src)
        if key.endswith('*'):                       # Wildcard-Praefix
            matched = sorted(k for k in bl if k.startswith(key[:-1]))
            if not matched:
                missing.append((src, key))
            for k in matched:
                if (src, k) not in seen:
                    seen.add((src, k))
                    ordered.append((gruppe, src, k, note, bl[k]))
            continue
        if key not in bl:
            missing.append((src, key))
            continue
        if (src, key) not in seen:
            seen.add((src, key))
            ordered.append((gruppe, src, key, note, bl[key]))
    return chart, req, prot, ordered, missing, grenz


def assemble_md(chart, ordered, prot, missing, grenz=None):
    out = ['# Referenzschnitt (Schritt 2) — nur chart-relevante Bloecke', '']
    out.append('> Maschinell aus blocks/ gezogen. Bloecke: %d. '
               'Fehlstellen: %d.' % (len(ordered), len(missing)))
    # Ueberspringbare Abschnitte mit ihrem Umfang ausweisen. Ohne diese Zeile
    # ist beim Lesen nicht zu sehen, was der Schnitt kostet — und was er
    # sparen wuerde. Zahlen aus dem tatsaechlich gezogenen Schnitt, nicht
    # geschaetzt.
    _z = {}
    for gruppe, _s, _k, _n, text in ordered:
        _z[gruppe] = _z.get(gruppe, 0) + len(text.split('\n')) + 2
    _skip = [(g, _z[g]) for g in UEBERSPRINGBAR if _z.get(g)]
    if _skip:
        out.append('>')
        out.append('> UEBERSPRINGBAR (s. Werkzeug-Modul, Punkt 2): %s. '
                   'Zusammen rund %d Zeilen.'
                   % (' · '.join('%s ~%d Zeilen' % (g, n) for g, n in _skip),
                      sum(n for _, n in _skip)))
        out.append('> Sie tragen Methoden-, Zeichen- und Grundlagenwissen, das '
                   'in jedem Lauf identisch ist und')
        out.append('> keinen Bezug zum konkreten Chart hat. Chart-spezifische '
                   'Bloecke (Zeichen, Haus,')
        out.append('> Aspekt, Spezialfaktor-Staende) werden IMMER voll '
                   'gelesen.')
    out.append('')
    if grenz:
        out.append('\n' + '=' * 70)
        out.append('## ⚠ GRENZLAGEN — Pflichtanweisung fuer die Deutung')
        out.append('=' * 70)
        out.append(
            'Diese Faktoren stehen 5° oder weniger VOR einer Hausspitze. Was '
            'daraus folgt,\nhaengt seit dem Kern-Umbau vom 2026-09-04 davon ab, '
            'ob der Faktor ein Thema FUEHRT:\n'
            '\n'
            '  - Er FUEHRT ein Thema  -> er wird in BEIDEN Haeusern gedeutet, in '
            'der unten\n'
            '    genannten Rangfolge. Die Hausdeutung des Nebenhauses darf dann '
            'nicht\n'
            '    wegfallen; sie faellt sonst bei der Deckungsprobe (a) auf wie '
            'eine fehlende\n'
            '    Zeichenebene.\n'
            '  - Er fuehrt KEINES -> seine Zeile im Rechenschaftskapitel traegt '
            'beide Haeuser\n'
            '    mit der Stufe („Haus 11/12, Schwellenlage"). Ausgedeutet wird '
            'dort nichts.\n'
            '\n'
            'Bis zum 2026-09-06 stand hier pauschal „werden in BEIDEN Haeusern '
            'gedeutet" —\ndas war gegenueber dem Kern veraltet und wies bei '
            'jedem Lauf eine Pflicht an,\ndie fuer nicht fuehrende Faktoren '
            'nicht gilt.\n'
            '\n'
            'Beide Hausbloecke stehen unten unter "Planet-in-Haus" bzw. '
            '"Spezialfaktor". Die\nfertige Signatur-Zeile (Klartext-Modus) '
            'steht jeweils dabei und wird 1:1 in den\nKapitelkopf uebernommen; '
            'im Fliesstext erscheint KEINE Gradzahl. Die Hausnummer darf '
            'dort stehen\n(Klartext-Modul, Anker-Regel: "DARF stehen — beim '
            'ersten Mal mit dem\nLebensbereich dahinter"). Bis zum 2026-09-06 '
            'stand hier "weder Hausnummer\nnoch Gradzahl" — das widersprach '
            'dem Klartext-Modul (Pruefbericht Transit 1.7).\n')
        for g in grenz:
            marke = (' [FUEHRT ein Thema — beide Haeuser deuten]'
                     if g.get('fuehrt')
                     else ' [fuehrt kein Thema — Zeile im Rechenschaftskapitel, '
                          'beide Haeuser, keine Ausdeutung]')
            out.append('- **%s**: Haus %s → Haus %s. %s.%s'
                       % (g['faktor'].capitalize(), g['haus'], g['nebenhaus'],
                          g['text'], marke))
            out.append('  `Signatur: %s`' % signatur_notation(g))
            if g.get('spiegel_von'):
                out.append('  ACHTUNG Spiegelpol: Deutungstext kommt gespiegelt '
                           'ueber %s (eigene Bloecke wuerden die Achse '
                           'verkehrt herum ziehen). Die Haus- und '
                           'Zeichenangabe oben gilt trotzdem und ist bei einem '
                           'fuehrenden Faktor auszudeuten.'
                           % g['spiegel_von'].capitalize())
        out.append('')
    for g in GRUPPEN:
        items = [o for o in ordered if o[0] == g]
        if not items:
            continue
        out.append('\n' + '=' * 70)
        out.append('## %s' % g)
        out.append('=' * 70)
        for gruppe, src, key, note, text in items:
            hdr = '### [%s]  Quelle: %s' % (key, src)
            if note:
                hdr += '   — %s' % note
            out.append('\n' + hdr)
            out.append(text)
    out.append('\n' + '=' * 70)
    out.append('## Auswahl-Protokoll (Faktor/Aspekt -> Block)')
    out.append('=' * 70)
    out.extend(prot)
    return '\n'.join(out) + '\n'


def main():
    chart_path = sys.argv[1]
    blocks_dir = sys.argv[2] if len(sys.argv) > 2 else 'blocks'
    out_path = sys.argv[3] if len(sys.argv) > 3 else \
        os.path.basename(chart_path).replace('chart_data', 'referenz')
    text = open(chart_path, encoding='utf-8').read()
    chart, req, prot, ordered, missing, grenz = select(text, blocks_dir)
    print('Faktoren :', len(chart['faktoren']),
          '| Aspekte:', len(chart['aspekte']),
          '| Bloecke gezogen:', len(ordered),
          '| Grenzlagen:', len(grenz))
    for g in grenz:
        print('   GRENZLAGE %-12s Haus %s -> %s  (%s)'
              % (g['faktor'], g['haus'], g['nebenhaus'], g['stufe']))
    for h in chart.get('hinweise', []):
        print('   HINWEIS %s' % h)
    for roh, ziel in chart.get('spiegel', []):
        print('   SPIEGELPOL %-12s -> uebersprungen, wird ueber %s als Achse '
              'mitgedeutet' % (roh, ziel))
    unbek = chart.get('unbekannt', [])
    if unbek:
        print('UNBEKANNTE FAKTOREN (harter Fehler — frueher fielen sie lautlos durch):')
        for nm in unbek:
            print('   UNBEKANNT %s — weder Planet noch Spezialfaktor.' % nm)
        print('   Erlaubt sind: %s' % ', '.join(PLANETS))
        print('   sowie:        %s' % ', '.join(sorted(SPEZFILE)))
        print('   Aliasse:      %s' % ', '.join(
            '%s->%s' % (k, v) for k, v in sorted(FAKTOR_ALIAS.items())))
        print('   Spiegelpole (bewusst uebersprungen): %s'
              % ', '.join(sorted(SPIEGEL_FAKTOREN)))
        sys.exit(1)
    if missing:
        print('FEHLSTELLEN (harter Fehler):')
        for src, key in missing:
            print('   FEHLT %s in %s' % (key, src))
        sys.exit(1)
    open(out_path, 'w', encoding='utf-8').write(
        assemble_md(chart, ordered, prot, missing, grenz))
    print('OK — geschrieben:', out_path, '(keine Fehlstelle)')


if __name__ == '__main__':
    main()
