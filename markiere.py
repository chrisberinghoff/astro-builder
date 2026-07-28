#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""markiere.py — setzt @@BLOCK key=...@@-Marker an die BESTEHENDEN Blockgrenzen
einer Referenzdatei. VERLUSTFREI konstruiert: fuegt ausschliesslich eigene
Markerzeilen ein und veraendert keinen einzigen Originalzeichen.

Zwei maschinelle Beweise pro Datei:
  (A) Rueck-Diff:   entmarkierte Fassung == Original (md5 identisch).
  (B) Ueberdeckung: erste Markerzeile steht an Zeilenindex 0, Marker streng
      aufsteigend & eindeutig -> JEDE Originalzeile liegt in genau einem Block
      (kein Text faellt zwischen die Bloecke).

Kategorien:
  zeichen       02/03/04  (Planet-in-Zeichen; 04 TEIL3 IC als 1 Block)
  haus          Haus_*    (beide Namensstile, Faktor-in-Haus)
  sonnenzeichen *_Sonnenzeichen  (ganze Datei = 1 Block)
  aspekt        *_Aspekte (Partnerblock je Aspekt, Textbasierte Partnererkennung)
  spezial       Chiron/Glueckspunkt/Lilith/Pholus/Mondknotenachse (Haus/Zeichen/Aspekt)
  grundlagen    01        (ganze Datei = 1 Block)
  achsen        05        (AC je Zeichen + DC-Tabelle + MC-Tabelle)

Aufruf:  python3 markiere.py <kategorie|auto> <infile> <outfile>
"""
import hashlib
import re
import sys

MARK_PREFIX = '@@BLOCK key='
MARK_SUFFIX = '@@'
MARK_RE = re.compile(r'^@@BLOCK key=\S+' + re.escape(MARK_SUFFIX) + r'$')

SIGNS = ['WIDDER', 'STIER', 'ZWILLINGE', 'KREBS', 'LÖWE', 'JUNGFRAU', 'WAAGE',
         'SKORPION', 'SCHÜTZE', 'STEINBOCK', 'WASSERMANN', 'FISCHE']
PLANETS = ['SONNE', 'MOND', 'MERKUR', 'VENUS', 'MARS', 'JUPITER', 'SATURN',
           'URANUS', 'NEPTUN', 'PLUTO']


def norm(s):
    s = s.strip().upper()
    for a, b in (('Ö', 'OE'), ('Ü', 'UE'), ('Ä', 'AE'), ('ß', 'SS')):
        s = s.replace(a, b)
    return s


SIGNSET = set(norm(z) for z in SIGNS)
SIGN_RX = '|'.join(SIGNS)
PLAN_RX = '|'.join(PLANETS)

SEP_RE = re.compile(r'^\s*[-=_─━═·]{4,}\s*$')
RE_TEIL = re.compile(r'^TEIL\s*\d+')
RE_PLIN = re.compile(r'^(' + PLAN_RX + r')\s+IN\s+(' + SIGN_RX + r')\b')
RE_SIGN = re.compile(r'^(' + SIGN_RX + r')\b')
RE_SIGN_I = re.compile(r'^(' + SIGN_RX + r')\b', re.IGNORECASE)
RE_ASZ = re.compile(r'^ASZENDENT\s+(' + SIGN_RX + r')\b')
# Faktor im/IM N. Haus  (optional fuehrendes Glyph; optional Knoten-Glyph nach Name)
RE_HAUSFACT = re.compile(
    r'^(?:[☉☽☿♀♂♃♄♅♆♇☊☋C⚷⚸⯛⊗]\s+)?'
    r'(AUFSTEIGENDER\s+MONDKNOTEN|MONDKNOTEN|' + PLAN_RX + r')'
    r'\s+(?:[☊☋]\s+)?(?:im|IM)\s+(\d+)\.\s+(?:Haus|HAUS)\b')
# Aspekt-Kopf: <tok> / <tok>  <A-Name> – <B-Name> [: Titel]
ASP = re.compile(r'^(\S{1,3})\s*/\s*(\S{1,6})\s{2,}(.+?)\s+[–—-]\s+([^:]+?)(?:\s*:.*)?$')

# Textbasierte Partnererkennung: nur DISTINKTE Worte (keine 2-Buchstaben-Kuerzel
# wie AC/MC, die als Substring in 'MeridianACHse' o.ae. falsch treffen).
PARTNERS = [('AUFSTEIGENDER MONDKNOTEN', 'KNOTEN'), ('MONDKNOTEN', 'KNOTEN'),
            ('KNOTENACHSE', 'KNOTEN'), ('MEDIUM COELI', 'MC'), ('MERIDIANACHSE', 'MC'),
            ('HORIZONTACHSE', 'AC'), ('ASZENDENT', 'AC'), ('DESZENDENT', 'DC'),
            ('IMUM COELI', 'IC'), ('IMMUM COELI', 'IC'),
            ('SONNE', 'SONNE'), ('MERKUR', 'MERKUR'), ('MOND', 'MOND'),
            ('VENUS', 'VENUS'), ('MARS', 'MARS'), ('JUPITER', 'JUPITER'),
            ('SATURN', 'SATURN'), ('URANUS', 'URANUS'), ('NEPTUN', 'NEPTUN'),
            ('PLUTO', 'PLUTO'), ('KNOTEN', 'KNOTEN')]


def sep(s):
    return bool(SEP_RE.match(s))


def back(i, lines):
    """Marker vor eine unmittelbar vorausgehende Trennlinie ziehen, damit die
    Linie beim folgenden Block bleibt."""
    if i > 0 and sep(lines[i - 1].strip()):
        return i - 1
    return i


def asp_partner(s):
    m = ASP.match(s)
    if not m:
        return None
    b = m.group(4).upper()
    g2 = m.group(2).upper()
    # Achsen-Kuerzel im Glyphtoken (Mondknoten: 'AC-DC' Horizont, 'MC-IC' Meridian)
    if 'MC' in g2 and 'IC' in g2:
        return 'MC'
    if 'AC' in g2 and 'DC' in g2:
        return 'AC'
    for name, canon in PARTNERS:
        if name in b:
            return canon
    if re.search(r'\bMC\b', b):
        return 'MC'
    if re.search(r'\bAC\b', b):
        return 'AC'
    return None


def norm_planet(p):
    p = norm(p)
    if 'MONDKNOTEN' in p:
        return 'MONDKNOTEN'
    return p


# ---------------------------------------------------------------- Kategorien
def cat_zeichen(lines, fname):
    ins = [(0, 'KOPF')]
    planet = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if RE_TEIL.match(s):
            up = s.upper()
            if 'IMMUM COELI' in up or 'IMUM COELI' in up or re.search(r'\(IC\)', up):
                ins.append((back(i, lines), 'IC_IN_ZEICHEN'))
                planet = 'IC'
                continue
            pl = None
            for p in PLANETS:
                if p in up:
                    pl = p
                    break
            planet = pl
            ins.append((back(i, lines), 'SEC_' + (pl or 'X')))
            continue
        if planet == 'IC':
            continue
        m = RE_PLIN.match(s)
        if m:
            ins.append((back(i, lines), norm(m.group(1)) + '_IN_' + norm(m.group(2))))
            continue
        m = RE_SIGN.match(s)
        if m and planet and 0 < i < len(lines) - 1 \
                and sep(lines[i - 1].strip()) and sep(lines[i + 1].strip()):
            ins.append((back(i, lines), norm(planet) + '_IN_' + norm(m.group(1))))
    return ins


def cat_haus(lines, fname):
    mnum = re.search(r'Haus_0*(\d+)', fname)
    N = int(mnum.group(1))
    ins = [(0, 'HAUS_%d_ALLG' % N)]
    for i, ln in enumerate(lines):
        m = RE_HAUSFACT.match(ln.strip())
        if m:
            ins.append((back(i, lines), '%s_HAUS_%d' % (norm_planet(m.group(1)), N)))
    return ins


def cat_sonnenzeichen(lines, fname):
    sign = fname.split('_')[0]
    return [(0, 'SONNENZEICHEN_' + norm(sign))]


def cat_aspekt(lines, fname):
    A = norm(fname.split('_')[0])
    ins = [(0, 'KOPF')]
    for i, ln in enumerate(lines):
        pa = asp_partner(ln.strip())
        if pa:
            ins.append((back(i, lines), A + '_' + pa))
    return ins


THDR = re.compile(r'^(URANUS|NEPTUN|PLUTO)\b.*in den Zeichen', re.IGNORECASE)


def cat_grundlagen(lines, fname):
    """01: Prinzip-Text bleibt als lade-immer-Segmente GRUNDLAGEN_*; die drei
    Generationen-Tabellen (U/N/P) werden zeilenweise als <PLANET>_IN_<ZEICHEN>
    selektierbar."""
    ins = [(0, 'GRUNDLAGEN_A')]
    seg = 0
    planet = None
    intable = False
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not intable:
            m = THDR.match(s)
            if m:
                planet = norm(m.group(1))
                intable = True
            continue
        ms = RE_SIGN_I.match(s)
        if ms:
            ins.append((i, '%s_IN_%s' % (planet, norm(ms.group(1)))))
            continue
        if s == '':
            continue
        intable = False
        seg += 1
        ins.append((back(i, lines), 'GRUNDLAGEN_' + chr(ord('B') + seg - 1)))
        m = THDR.match(s)
        if m:
            planet = norm(m.group(1))
            intable = True
    return ins


def cat_achsen(lines, fname):
    ins = [(0, 'KOPF')]
    for i, ln in enumerate(lines):
        s = ln.strip()
        m = RE_ASZ.match(s)
        if m:
            ins.append((back(i, lines), 'ASZENDENT_' + norm(m.group(1))))
            continue
        if RE_TEIL.match(s):
            up = s.upper()
            if 'DESZENDENT' in up:
                ins.append((back(i, lines), 'DESZENDENT_TABELLE'))
            elif 'MEDIUM COELI' in up or re.search(r'\bMC\b', up):
                ins.append((back(i, lines), 'MC_IN_ZEICHEN'))
    return ins


def spezfaktor(fname):
    f = fname.lower()
    if f.startswith('chiron'):
        return 'CHIRON'
    if f.startswith('glueck') or f.startswith('glück'):
        return 'GLUECKSPUNKT'
    if f.startswith('lilith'):
        return 'LILITH'
    if f.startswith('pholus'):
        return 'PHOLUS'
    if f.startswith('mondknoten'):
        return 'MONDKNOTEN'
    raise ValueError('unbekannter Spezialfaktor: ' + fname)


def section_of(s, fak):
    up = s.upper()
    if fak == 'MONDKNOTEN':
        if re.match(r'^DIE ACHSE DURCH DIE HÄUSER$', up):
            return 'HAUS'
        if re.match(r'^DIE ACHSE DURCH DIE ZEICHEN$', up):
            return 'ZEICHEN'
        if re.match(r'^DIE ACHSE IN ASPEKTEN$', up):
            return 'ASPEKT'
        return None
    if re.match(r'^[A-ZÄÖÜ0-9()/ ]+ IN DEN HÄUSERN$', up):
        return 'HAUS'
    if re.match(r'^[A-ZÄÖÜ0-9()/ ]+ IN DEN ZEICHEN$', up):
        return 'ZEICHEN'
    if re.match(r'^[A-ZÄÖÜ0-9()/ ]+ IN ASPEKTEN$', up):
        return 'ASPEKT'
    return None


def cat_spezial(lines, fname):
    fak = spezfaktor(fname)
    ins = [(0, fak + '_ALLG')]
    mode = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        sm = section_of(s, fak)
        if sm:
            mode = sm
            ins.append((back(i, lines), fak + '_SEC_' + sm))
            continue
        if fak == 'MONDKNOTEN':
            if mode == 'HAUS':
                m = re.match(r'^☊\s+(\d+)\.\s+HAUS\s*/\s*☋', s)
                if m:
                    ins.append((back(i, lines), 'MONDKNOTEN_HAUS_' + m.group(1)))
            elif mode == 'ZEICHEN':
                m = re.match(r'^☊\s+([A-ZÄÖÜ]+)\s*/\s*☋', s)
                if m and norm(m.group(1)) in SIGNSET:
                    ins.append((back(i, lines), 'MONDKNOTEN_IN_' + norm(m.group(1))))
            elif mode == 'ASPEKT':
                pa = asp_partner(s)
                if pa:
                    ins.append((back(i, lines), 'MONDKNOTEN_' + pa))
        else:
            if mode == 'HAUS':
                m = re.match(r'^(?:\S{1,2}\s+)?[A-ZÄÖÜ]+\s+IM\s+(\d+)\.\s+HAUS\b', s)
                if m:
                    ins.append((back(i, lines), fak + '_HAUS_' + m.group(1)))
            elif mode == 'ZEICHEN':
                m = re.match(r'^([A-ZÄÖÜ]+)\s*[—–-]\s', s)
                if m and norm(m.group(1)) in SIGNSET:
                    ins.append((back(i, lines), fak + '_IN_' + norm(m.group(1))))
            elif mode == 'ASPEKT':
                pa = asp_partner(s)
                if pa:
                    ins.append((back(i, lines), fak + '_' + pa))
    return ins


# ---------------------------------------------------------------- Dispatch
def which_category(fname):
    f = fname
    if re.match(r'^(02|03|04)_', f):
        return 'zeichen'
    if f == '01_Planeten_Grundprinzipien.txt':
        return 'grundlagen'
    if f == '05_Aszendent_MC_Deszendent_Tabellen.txt':
        return 'achsen'
    if f.startswith('Haus_'):
        return 'haus'
    if f.endswith('_Sonnenzeichen.txt'):
        return 'sonnenzeichen'
    if f.endswith('_Haus_Zeichen_Aspekte.txt'):   # VOR _Aspekte pruefen!
        return 'spezial'
    if f.endswith('_Aspekte.txt'):
        return 'aspekt'
    raise ValueError('keine Kategorie fuer: ' + fname)


DISPATCH = {'zeichen': cat_zeichen, 'haus': cat_haus,
            'sonnenzeichen': cat_sonnenzeichen, 'aspekt': cat_aspekt,
            'grundlagen': cat_grundlagen, 'achsen': cat_achsen,
            'spezial': cat_spezial}


def build(text, kat, fname):
    """-> (marked_text, keys, proofA_ok, proofB_ok, proofC_ok, msg)"""
    lines = text.split('\n')
    raw = DISPATCH[kat](lines, fname)
    # dedupe nach idx (erste Zuweisung gewinnt), sortieren
    seen = {}
    for idx, key in raw:
        if idx not in seen:
            seen[idx] = key
    ins = sorted(seen.items())
    idxs = [i for i, _ in ins]
    keys = [k for _, k in ins]
    # (B) Ueberdeckung: erster Marker bei 0, Indizes streng aufsteigend
    covB = (len(idxs) > 0 and idxs[0] == 0 and idxs == sorted(set(idxs)))
    # (C) Schluessel pro Datei eindeutig
    covC = (len(keys) == len(set(keys)))
    # Marker einsetzen
    out = []
    imap = dict(ins)
    for i, ln in enumerate(lines):
        if i in imap:
            out.append(MARK_PREFIX + imap[i] + MARK_SUFFIX)
        out.append(ln)
    marked = '\n'.join(out)
    # (A) Rueck-Diff
    stripped = '\n'.join(l for l in marked.split('\n') if not MARK_RE.match(l))
    covA = (stripped == text)
    msg = ''
    if not covA:
        a, b = text.split('\n'), stripped.split('\n')
        for n, (x, y) in enumerate(zip(a, b)):
            if x != y:
                msg = 'Rueck-Diff Abweichung Zeile %d: %r != %r' % (n, x, y)
                break
        else:
            msg = 'Laengendifferenz %d != %d' % (len(a), len(b))
    if covC is False and not msg:
        dup = [k for k in keys if keys.count(k) > 1]
        msg = 'Doppelte Schluessel: ' + ','.join(sorted(set(dup)))
    return marked, keys, covA, covB, covC, msg


def main():
    kat, infile, outfile = sys.argv[1], sys.argv[2], sys.argv[3]
    import os
    fname = os.path.basename(infile)
    if kat == 'auto':
        kat = which_category(fname)
    text = open(infile, encoding='utf-8').read()
    marked, keys, covA, covB, covC, msg = build(text, kat, fname)
    open(outfile, 'w', encoding='utf-8').write(marked)
    print('Datei      :', fname, '(' + kat + ')')
    print('Bloecke    :', len(keys))
    print('Rueck-Diff :', 'OK' if covA else 'FEHLER — ' + msg)
    print('Ueberdeck. :', 'OK' if covB else 'FEHLER')
    print('Eindeutig  :', 'OK' if covC else 'FEHLER — ' + msg)
    md5o = hashlib.md5(text.encode('utf-8')).hexdigest()
    strip = '\n'.join(l for l in marked.split('\n') if not MARK_RE.match(l))
    md5s = hashlib.md5(strip.encode('utf-8')).hexdigest()
    print('md5 orig   :', md5o)
    print('md5 entmrk :', md5s, '(identisch)' if md5o == md5s else '(!!!)')
    print('Schluessel :')
    for k in keys:
        print('   ' + k)
    if not (covA and covB and covC):
        sys.exit(1)


if __name__ == '__main__':
    main()
