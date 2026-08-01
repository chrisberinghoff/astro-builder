#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parser für §11 (Transit-Datenblock) aus <klient>_Ultimativ_chart_data.md.

Liest den unveränderten transit.py-v2-Report aus dem Codeblock in §11 und gibt
ihn strukturiert zurück. Bewusst geparst statt abgetippt: die Vorschau hängt an
Datum, Orb und Richtung — Tippfehler wären hier teuer und unsichtbar.

Liefert:
    fenster      {'start','ende','stichtag','rueckblick'}   (date-Objekte)
    quartale     [(label, start, ende, monatsspanne), ...]
    stand        [(Planet, 'Loewe 5°45\\'', 'H8'), ...]
    im_orb       [{transiter, aspekt, ziel, orb, richtung, kehrt, exakt_txt,
                   bis, primaer, wirkorb}]
    nachhall     [{transiter, aspekt, ziel, exakt, tage, primaer}]
    anmarsch     [{transiter, aspekt, ziel, exakt, tage, primaer}]
    stationen    [{datum, planet, richtung, pos, ziele}]
    langlaeufer  [{primaer, transiter, aspekt, ziel, start, ende, monate,
                   quartale, exakt[], flags, wirkorb[(a,b),...]}]
    zeichen      [{planet, zeichen, start, ende, monate}]
    haeuser      [{planet, haus, start, ende, monate, note}]

HAUSSTIL-AENDERUNGEN 2026-07-27 (gemeinsam festgelegt):
  * `kurz()` setzt hinter BEIDE Seiten den Namen — vorher stand der laufende
    Planet nur als Glyphe da ('♄ ☍ ☽ Mond'), was dem Erklaertext der Uhr
    widersprach („zuerst der laufende Planet, dann der Winkel, dann die Stelle
    deines Geburtsbildes"): der Leser sucht zwei Namen und findet einen.
  * 'Knoten' wird als 'Mondknoten' ausgeschrieben.
  * Die Quartalstupel tragen ein viertes Feld mit der Monatsspanne
    ('Jul–Sep 26'). Seit transit.py auf Kalenderquartale rechnet, ist die
    Zuordnung Q-Nummer -> Kalendermonate nicht mehr selbsterklaerend; die Uhr
    schreibt sie darum unter die Q-Nummer. Aeltere Aufrufer, die nur drei
    Felder auspacken, brechen daran nicht — die Uhren lesen defensiv
    (`q[3] if len(q) > 3 else ''`).
"""
import re
from datetime import date

# Wird vom Chart-Builder gesetzt: setze_quelle('<klient>_Ultimativ_chart_data.md').
# Kein Default auf einen Klientennamen — sonst parst ein Folgechart still die
# Datei des vorigen.
QUELLE = None


def setze_quelle(pfad):
    global QUELLE
    QUELLE = pfad
    return pfad

GLYPH = {
    'Sonne': '☉', 'Mond': '☽', 'Merkur': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptun': '♆', 'Pluto': '♇',
    'Knoten': '☊', 'Nordknoten': '☊', 'Suedknoten': '☋', 'Chiron': '⚷',
    'Lilith': '⚸', 'Glueckspunkt': '⊗', 'Pholus': '', 'AC': '', 'MC': '',
}
ZIELNAME = {'Glueckspunkt': 'Glückspunkt', 'Suedknoten': 'Südknoten',
            'Knoten': 'Mondknoten'}
# Nur font-gedeckte Aspektzeichen (Klartext-Modul): Quincunx/Halbsextil haben
# KEINE gedeckte Glyphe -> dort bleibt das Wort stehen.
ASP_GLYPH = {'Konjunktion': '☌', 'Opposition': '☍', 'Quadrat': '□',
             'Trigon': '△', 'Sextil': '⚹'}

MON_KURZ = ['', 'Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep',
            'Okt', 'Nov', 'Dez']


def _d(s):
    y, m, dd = s.split('-')
    return date(int(y), int(m), int(dd))


def ziel_label(n):
    return ZIELNAME.get(n, n)


def kurz(transiter, aspekt, ziel):
    """Label einer Uhr-Zeile: '♇ Pluto ☍ ☿ Merkur', '♆ Neptun Quincunx MC'.

    Beide Seiten mit Namen — links der laufende Planet, rechts der Punkt des
    Geburtsbildes. Faktoren ohne gedeckte Glyphe (Pholus, AC, MC) stehen nur
    mit Namen da. Quincunx und Halbsextil bleiben als Wort stehen, weil ihre
    Zeichen in keiner verfuegbaren Font gedeckt sind.
    """
    tg = GLYPH.get(transiter, '')
    ag = ASP_GLYPH.get(aspekt, aspekt)
    zg = GLYPH.get(ziel, '')
    teile = [t for t in (tg, ziel_label(transiter), ag, zg, ziel_label(ziel))
             if t]
    return ' '.join(teile)


def _monatsspanne(a, b):
    """'Jul–Sep 26' aus Anfangs- und Enddatum eines Quartals."""
    if a.year == b.year:
        return f'{MON_KURZ[a.month]}–{MON_KURZ[b.month]} {str(a.year)[2:]}'
    return (f'{MON_KURZ[a.month]} {str(a.year)[2:]}–'
            f'{MON_KURZ[b.month]} {str(b.year)[2:]}')


def _block(txt, start_marker, end_marker=None):
    i = txt.index(start_marker) + len(start_marker)
    j = txt.index(end_marker, i) if end_marker else len(txt)
    return txt[i:j]


def parse(pfad=None):
    pfad = pfad or QUELLE
    if not pfad:
        raise ValueError('transitdata: keine Quelle gesetzt — '
                         'setze_quelle(<klient>_Ultimativ_chart_data.md) '
                         'oder parse(pfad=...) aufrufen.')
    raw = open(pfad, encoding='utf-8').read()
    # §11 liegt in einem eingezäunten Codeblock
    s = raw.index('Fenster 2')
    e = raw.index('\n```', s)
    txt = raw[s:e]

    out = {}
    m = re.search(r'Fenster (\S+) \.\. (\S+)\s+Stichtag (\S+)\s+'
                  r'Rueckblick ab (\S+)', txt)
    out['fenster'] = {'start': _d(m.group(1)), 'ende': _d(m.group(2)),
                      'stichtag': _d(m.group(3)), 'rueckblick': _d(m.group(4))}

    out['quartale'] = [
        (q, _d(a), _d(b), _monatsspanne(_d(a), _d(b))) for q, a, b in
        # Q\d+ statt Q\d: bei Fenstern ueber zwei Jahre gibt es Q10 bis Q12,
        # und die fielen mit der einstelligen Fassung stillschweigend aus der
        # Liste — die Uhr zeichnete dann nur acht von zwoelf Quartalen
        # (gefunden 2026-08-01 beim ersten 36-Monats-Lauf).
        re.findall(r'(Q\d+) (\d{4}-\d\d-\d\d)–(\d{4}-\d\d-\d\d)', txt)]

    stand = _block(txt, 'Transit-Staende:', '\n\n')
    out['stand'] = []
    for teil in stand.split('·'):
        mm = re.match(r"\s*(\w+)\s+(\w+)\s+([\d°'R ]+?)\s*\(H(\d+)\)", teil.strip())
        if mm:
            out['stand'].append({'planet': mm.group(1), 'zeichen': mm.group(2),
                                 'pos': mm.group(3).strip(), 'haus': mm.group(4)})

    # --- Jetzt: im Orb ---
    seg = _block(txt, '-- im Orb', '-- Nachhall')
    out['im_orb'] = []
    for ln in seg.splitlines():
        mm = re.match(r'\s*\[(P| )(\*| )\]\s+(\w+)\s+(\w+)\s+(\S+)\s+orb ([\d.]+)° '
                      r'(\w+)(\s*\(kehrt zurueck\))?\s+(.*?)\s*(?:\| bis (\S+))?$', ln)
        if mm:
            out['im_orb'].append({
                'primaer': mm.group(1) == 'P', 'wirkorb': mm.group(2) == '*',
                'transiter': mm.group(3), 'aspekt': mm.group(4), 'ziel': mm.group(5),
                'orb': float(mm.group(6)), 'richtung': mm.group(7),
                'kehrt': bool(mm.group(8)), 'exakt_txt': mm.group(9).strip(),
                'bis': mm.group(10)})

    for key, a, b in (('nachhall', '-- Nachhall', '-- Anmarsch'),
                      ('anmarsch', '-- Anmarsch', '-- Stationen')):
        out[key] = []
        for ln in _block(txt, a, b).splitlines():
            mm = re.match(r'\s*\[(P| ) \]\s+(\w+)\s+(\w+)\s+(\S+)\s+exakt (\S+) '
                          r'\((?:vor|in) (\d+) T\)', ln)
            if mm:
                out[key].append({'primaer': mm.group(1) == 'P',
                                 'transiter': mm.group(2), 'aspekt': mm.group(3),
                                 'ziel': mm.group(4), 'exakt': _d(mm.group(5)),
                                 'tage': int(mm.group(6))})

    out['stationen'] = []
    for ln in _block(txt, '-- Stationen im Umfeld', '====').splitlines():
        mm = re.match(r"\s*(\d{4}-\d\d-\d\d) (\w+) wird (direkt|rueckl\.) "
                      r"(.+?) -> (.*)$", ln)
        if mm:
            out['stationen'].append({
                'datum': _d(mm.group(1)), 'planet': mm.group(2),
                'richtung': 'direkt' if mm.group(3) == 'direkt' else 'rückläufig',
                'pos': mm.group(4).strip(), 'ziele': mm.group(5).strip()})

    # --- Langläufer ---
    seg = _block(txt, 'LANGLAEUFER', '-- Zeichen-Aufenthalte')
    out['langlaeufer'] = []
    cur = None
    for ln in seg.splitlines():
        mm = re.match(r'\s*\[(P| )\]\s+(\w+)\s+(\w+)\s+(\S+)\s+'
                      r'(\d{4}-\d\d-\d\d) \.\. (\d{4}-\d\d-\d\d) '
                      r'\(([\d.]+) Mon(?:, (\S+))?\)', ln)
        if mm:
            cur = {'primaer': mm.group(1) == 'P', 'transiter': mm.group(2),
                   'aspekt': mm.group(3), 'ziel': mm.group(4),
                   'start': _d(mm.group(5)), 'ende': _d(mm.group(6)),
                   'monate': float(mm.group(7)), 'quartale': mm.group(8) or '',
                   'exakt': [], 'flags': '', 'wirkorb': []}
            out['langlaeufer'].append(cur)
            continue
        if cur is None:
            continue
        mm = re.match(r'\s*exakt: ([^\[]+)(?:\[(.*)\])?', ln)
        if mm:
            cur['exakt'] = [_d(x) for x in
                            re.findall(r'\d{4}-\d\d-\d\d', mm.group(1))]
            cur['flags'] = (mm.group(2) or '').strip()
            continue
        mm = re.match(r'\s*im Wirkorb nur: (.+)$', ln)
        if mm:
            for a, b in re.findall(r'(\d{4}-\d\d-\d\d)\.\.(\d{4}-\d\d-\d\d)',
                                   mm.group(1).replace(' ', '')):
                cur['wirkorb'].append((_d(a), _d(b)))

    out['zeichen'] = []
    for ln in _block(txt, '-- Zeichen-Aufenthalte', '-- Haus-Durchgaenge').splitlines():
        mm = re.match(r'\s*(\w+)\s+(\w+)\s+(\d{4}-\d\d-\d\d) \.\. '
                      r'(\d{4}-\d\d-\d\d) \(([\d.]+) Mon\)', ln)
        if mm:
            out['zeichen'].append({'planet': mm.group(1), 'zeichen': mm.group(2),
                                   'start': _d(mm.group(3)), 'ende': _d(mm.group(4)),
                                   'monate': float(mm.group(5))})

    out['haeuser'] = []
    for ln in _block(txt, '-- Haus-Durchgaenge', '====').splitlines():
        mm = re.match(r'\s*(\w+)\s+Haus\s+(\d+)\s+(\d{4}-\d\d-\d\d) \.\. '
                      r'(\d{4}-\d\d-\d\d) \(([\d.]+) Mon\)\s*(?:\[(.*)\])?', ln)
        if mm:
            out['haeuser'].append({'planet': mm.group(1), 'haus': int(mm.group(2)),
                                   'start': _d(mm.group(3)), 'ende': _d(mm.group(4)),
                                   'monate': float(mm.group(5)),
                                   'note': (mm.group(6) or '').strip()})
    return out


if __name__ == '__main__':
    import sys as _s
    d = parse(_s.argv[1] if len(_s.argv) > 1 else None)
    print('Fenster:', d['fenster'])
    print('Quartale:', len(d['quartale']), d['quartale'][0], d['quartale'][-1])
    print('Stand:', len(d['stand']), d['stand'][0])
    print('im Orb:', len(d['im_orb']), '| davon Wirkorb:',
          sum(1 for x in d['im_orb'] if x['wirkorb']))
    print('Nachhall:', len(d['nachhall']), '| Anmarsch:', len(d['anmarsch']))
    print('Stationen:', len(d['stationen']))
    ll = d['langlaeufer']
    print('Langlaeufer:', len(ll), '| primaer:', sum(1 for x in ll if x['primaer']))
    print('Labels:', [kurz(x['transiter'], x['aspekt'], x['ziel']) for x in ll[:6]])
