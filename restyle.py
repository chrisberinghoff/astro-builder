#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""restyle.py — Werkzeug fuer den Restyle-Modus (Schreibweise wechseln).

Zerlegt eine fertige `<klient>_analyse.md` in Abschnitte, gibt NUR die
Fliesstext-Rumpfe zum Umschreiben heraus, setzt sie hinterher wieder mit den
UNVERAENDERTEN Kopfbloecken (Signatur/Beleg) zusammen und faehrt die beiden
mechanischen Pruefungen.

Warum das ein Skript ist und keine Handarbeit: Signatur und Beleg duerfen sich
beim Restyle nicht um ein Zeichen aendern — sie speisen Aspekttabelle,
Kapitelkopf und Beleg-Deckung. Wer sie mit abtippt, riskiert stille
Abweichungen. Hier werden sie byteweise durchgereicht.

Aufrufe
-------
  python3 restyle.py zerlege  <analyse.md> <arbeit.json>
        -> JSON mit allen Abschnitten; 'rumpf' ist der umzuschreibende Text.
  python3 restyle.py pakete   <arbeit.json> <n>
        -> gibt die Abschnitts-Indizes in n-er Paketen aus (fuer Subagenten).
  python3 restyle.py setze    <analyse.md> <neu.json> <analyse_neu.md>
        -> neu.json = {"<index>": "<neuer Rumpf>", ...}; nicht genannte
           Abschnitte bleiben unveraendert.
  python3 restyle.py pruefe   <analyse_neu.md>
        -> Verbotsscan, Anker-Gegenprobe, Beleg-Deckung. Exitcode 1 bei Befund.

Traegt KEINE Klientendaten (Datenschutz-Guardrail).
"""
import json
import re
import sys

KOPFZEILE = re.compile(r'^\*\*(Signatur|Beleg):\*\*')
KAPITEL = re.compile(r'^##\s+KAPITEL\s+(\d+)', re.I)

# --- Was im Fliesstext nichts zu suchen hat (Anker-Klartext, Stand 2026-08-02)
# Die Rechenebene. Aspekt-, Planeten-, Zeichen- und Achsennamen sowie
# Hausnummern sind seit der Anker-Regel ERWUENSCHT und stehen deshalb nicht
# hier. „Bogenminute"/„Grad Abstand" sind ausgeschriebene Orbs — der alte
# Zeichen-Scan (° ′) findet sie nicht, sie gehoeren aber genauso in den Beleg.
VERBOTEN = ['°', '′', 'Orb', 'Bogenminute', 'Grad Abstand', 'einseitig',
            'Nebenaspekt', 'Domizil', 'Exil', 'Exaltation', 'Cazimi', 'Apex',
            'Dispositor', 'Endherrscher', 'AC-Herrscher', 'Chart-Herrscher',
            'T-Quadrat']

ASPEKTE = ['Konjunktion', 'Opposition', 'Quadrat', 'Trigon', 'Sextil',
           'Quincunx', 'Halbsextil']
FAKTOREN = ['Sonne', 'Mond', 'Merkur', 'Venus', 'Mars', 'Jupiter', 'Saturn',
            'Uranus', 'Neptun', 'Pluto', 'Chiron', 'Lilith', 'Pholus',
            'Glückspunkt', 'Mondknoten', 'Nordknoten', 'Südknoten',
            'Aszendent', 'Deszendent', 'MC', 'IC']
ZEICHEN = ['Widder', 'Stier', 'Zwillinge', 'Krebs', 'Löwe', 'Jungfrau',
           'Waage', 'Skorpion', 'Schütze', 'Steinbock', 'Wassermann', 'Fische']
HAUS = re.compile(r'\b(erst|zweit|dritt|viert|fünft|sechst|siebt|acht|neunt|'
                  r'zehnt|elft|zwölft)en\s+Haus\b|\b\d{1,2}\.\s*Haus\b')


# ---------------------------------------------------------------- zerlegen ---

def _teile(text):
    """Datei in Abschnitte schneiden; teile[0] ist der Vorspann (H1)."""
    return re.split(r'(?m)^(?=##\s)', text)


def _kopf_rumpf(abschnitt):
    """Kopf (Ueberschrift + Signatur/Beleg + Leerzeilen) vom Rumpf trennen.

    Byte-exakt: kopf + rumpf ergibt wieder den Abschnitt.
    """
    zeilen = abschnitt.splitlines(keepends=True)
    i = 1
    while i < len(zeilen):
        s = zeilen[i].strip()
        if s == '' or KOPFZEILE.match(s):
            i += 1
        else:
            break
    return ''.join(zeilen[:i]), ''.join(zeilen[i:])


def zerlege(pfad, out):
    text = open(pfad, encoding='utf-8').read()
    teile = _teile(text)
    daten = {'quelle': pfad, 'vorspann': teile[0], 'abschnitte': []}
    for idx, t in enumerate(teile[1:]):
        kopf, rumpf = _kopf_rumpf(t)
        zeilen = kopf.splitlines()
        sig = next((z for z in zeilen if z.startswith('**Signatur:**')), '')
        bel = next((z for z in zeilen if z.startswith('**Beleg:**')), '')
        daten['abschnitte'].append({
            'index': idx,
            'ueberschrift': zeilen[0].strip(),
            'ist_kapitel': bool(KAPITEL.match(zeilen[0])),
            'signatur': sig,
            'beleg': bel,
            'kopf': kopf,
            'rumpf': rumpf,
            'zeichen': len(rumpf),
        })
    json.dump(daten, open(out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    k = sum(1 for a in daten['abschnitte'] if a['ist_kapitel'])
    z = sum(a['zeichen'] for a in daten['abschnitte'])
    print(f'{len(daten["abschnitte"])} Abschnitte ({k} nummerierte Kapitel), '
          f'{z} Zeichen Fliesstext -> {out}')
    return daten


def pakete(arbeit, n):
    daten = json.load(open(arbeit, encoding='utf-8'))
    xs = daten['abschnitte']
    for i in range(0, len(xs), n):
        grp = xs[i:i + n]
        z = sum(a['zeichen'] for a in grp)
        print(f'Paket {i // n + 1}: Abschnitte {grp[0]["index"]}–'
              f'{grp[-1]["index"]}  ({z} Zeichen)  '
              f'{grp[0]["ueberschrift"][:48]} …')


# ------------------------------------------------------------ zusammensetzen -

def setze(pfad, neu_json, out):
    text = open(pfad, encoding='utf-8').read()
    teile = _teile(text)
    neu = {int(k): v for k, v in
           json.load(open(neu_json, encoding='utf-8')).items()}
    raus = [teile[0]]
    getauscht = 0
    for idx, t in enumerate(teile[1:]):
        kopf, rumpf = _kopf_rumpf(t)
        if idx in neu:
            r = neu[idx]
            if not r.endswith('\n'):
                r += '\n'
            if not r.startswith('\n') and not kopf.endswith('\n\n'):
                r = '\n' + r
            raus.append(kopf + r)
            getauscht += 1
        else:
            raus.append(t)
    open(out, 'w', encoding='utf-8').write(''.join(raus))
    print(f'{getauscht} Abschnitte getauscht, {len(teile) - 1 - getauscht} '
          f'unveraendert -> {out}')


# ------------------------------------------------------------------ pruefen --

def _absaetze(rumpf):
    return [p.strip() for p in rumpf.split('\n\n') if p.strip()]


def _anker(text):
    n = 0
    for w in ASPEKTE + FAKTOREN + ZEICHEN:
        n += len(re.findall(r'(?<![\wäöüß])' + re.escape(w), text))
    n += len(HAUS.findall(text))
    return n


def pruefe(pfad):
    text = open(pfad, encoding='utf-8').read()
    teile = _teile(text)
    alle_belege = ' '.join(re.findall(r'(?m)^\*\*Beleg:\*\*.*', text))
    befunde, hinweise = [], []
    kap = 0
    for t in teile[1:]:
        kopf, rumpf = _kopf_rumpf(t)
        titel = kopf.splitlines()[0].strip()
        ist_kap = bool(KAPITEL.match(titel))
        if ist_kap:
            kap += 1
        eigener_beleg = next((z for z in kopf.splitlines()
                              if z.startswith('**Beleg:**')), '')
        for j, a in enumerate(_absaetze(rumpf), 1):
            for w in VERBOTEN:
                if w in a:
                    stelle = a.find(w)
                    befunde.append(
                        f'VERBOT  {titel[:44]} · Absatz {j}: „{w}" in '
                        f'…{a[max(0, stelle - 40):stelle + 30]}…')
            if ist_kap and _anker(a) == 0:
                befunde.append(f'ANKER   {titel[:44]} · Absatz {j}: '
                               f'kein Anker im Absatz')
            for asp in ASPEKTE:
                if asp in a and asp not in eigener_beleg:
                    if asp not in alle_belege:
                        befunde.append(
                            f'BELEG   {titel[:44]} · Absatz {j}: „{asp}" '
                            f'steht in KEINEM Beleg des Dokuments')
                    else:
                        hinweise.append(
                            f'quer    {titel[:44]} · Absatz {j}: „{asp}" '
                            f'aus einem anderen Kapitel (erlaubt)')
    print(f'{kap} nummerierte Kapitel geprueft.')
    if hinweise:
        print(f'{len(hinweise)} Quer-Anker (erlaubt, nur zur Kenntnis):')
        for h in hinweise[:12]:
            print('  ' + h)
        if len(hinweise) > 12:
            print(f'  … und {len(hinweise) - 12} weitere')
    if befunde:
        print(f'\n{len(befunde)} BEFUND(E):')
        for b in befunde:
            print('  ' + b)
        return 1
    print('Verbotsscan 0 · jeder Kapitelabsatz hat einen Anker · '
          'Beleg-Deckung vollstaendig.')
    return 0


# --------------------------------------------------------------------- CLI ---

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == 'zerlege':
        zerlege(sys.argv[2], sys.argv[3])
    elif cmd == 'pakete':
        pakete(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    elif cmd == 'setze':
        setze(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == 'pruefe':
        sys.exit(pruefe(sys.argv[2]))
    else:
        print(__doc__)
        sys.exit(2)
