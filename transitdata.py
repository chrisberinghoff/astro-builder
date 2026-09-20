#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parser für §11 (Transit-Datenblock) aus <klient>_Ultimativ_chart_data.md.

Liest den unveränderten transit.py-v2-Report aus dem Codeblock in §11 und gibt
ihn strukturiert zurück. Seit 2026-09-19 (W11) aus ALLEN Report-Codeblöcken ab
der Fensterzeile (oder aus der rohen transit.py-Ausgabe); Selbsttest:
python3 transitdata.py --selbsttest. Bewusst geparst statt abgetippt: die Vorschau hängt an
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
    hotspots     [{jahr, monat, aktiv, exakt, label}]
  seit 2026-09-19 zusaetzlich (leer bzw. None bei aelteren Reports):
    im_orb[...]  + wirkorb_txt, wirkorb_kommend (a,b), wirkorb_vorbei_bis,
                   exakt_datum, exakt_art ('kommend'|'gewesen'|'keiner');
                   `bis` ist im neuen Format das Ende der Wirkorb-Periode, in
                   der der Stichtag liegt (sonst None)
    langlaeufer[...] + vorlauf {orb_ab, wirkorb_ab, exakt[], text} | None,
                   annaeherung [(datum, bogenminuten)], beginn_abgeschnitten
    fortsetzung  [{primaer, transiter, aspekt, ziel, exakt[], annaeherung,
                   min_orb, min_datum, wirkorb_bis, orb_bis, ueber_horizont, text}]
    fruehere     [{primaer, transiter, aspekt, ziel, keiner, durchgaenge:
                   [{nr, exakt[(datum, alter)], nicht_exakt, datum, alter,
                     orb_grad, annaeherung, bei_geburt, text}]}]
    zusatz       {prog_mond, prog_mond_wechsel, sonnenbogen, profektion,
                  finsternisse} (Abschnitt ZUSATZ-ZEITMASSE) oder {}
  Schema von Report und events.json: log/SCHNITTSTELLE_events_json.md des
  Wartungslaufs 2026-09-19.

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
    """Die chart_data festlegen, aus der parse() ohne Argument liest (QUELLE)."""
    global QUELLE
    QUELLE = pfad
    return pfad

GLYPH = {
    'Sonne': '☉', 'Mond': '☽', 'Merkur': '☿', 'Venus': '♀', 'Mars': '♂',
    'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptun': '♆', 'Pluto': '♇',
    'Knoten': '☊', 'Nordknoten': '☊', 'Suedknoten': '☋', 'Chiron': '⚷',
    # 2026-09-19 (F24, Runde 2): Das leere Feld heisst hier „keine gedeckte
    # Glyphe — nur der Name" und bleibt ABSICHTLICH leer: kurz() und die
    # Anhangspalten setzen Glyphe UND Namen nebeneinander, mit den
    # Vertrags-Kuerzeln aus radix.FAKTOR_GLYPHE stuende dort „MC MC" bzw.
    # „Pho Pholus". Diese Tabelle ist KEINE Quelle fuer den factors-Block der
    # chart_data — dort gilt radix.FAKTOR_GLYPHE / radix.glyphen_ergaenzen().
    'Lilith': '⚸', 'Glueckspunkt': '⊗', 'Pholus': '', 'AC': '', 'MC': '',
    # 2026-09-19 (F22): Vertragsnamen des chartdata.py-Vertrags. events.json und
    # Report fuehren die Ziele als `Mondknoten` und `Glückspunkt`; ohne diese
    # Eintraege standen Uhr-Zeilen und Anhang ohne Glyphe (die Vorlage trug die
    # Umgehung `tdat.GLYPH.update(...)`, die damit entfallen kann).
    'Mondknoten': '☊', 'Glückspunkt': '⊗', 'Südknoten': '☋',
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
    """Anzeigename eines Ziels mit Umlaut (ZIELNAME: Glueckspunkt -> Glückspunkt,
    Suedknoten -> Südknoten, Knoten -> Mondknoten); Unbekanntes unveraendert."""
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
    """Text zwischen start_marker und dem ersten end_marker danach.

    2026-09-19 (W11): end_marker darf ein Tupel von Alternativen sein (die
    frueheste gilt; findet sich keine, reicht der Block bis zum Textende), und
    ein fehlender start_marker bricht mit einer lesbaren Meldung ab statt mit
    'substring not found'."""
    i = txt.find(start_marker)
    if i < 0:
        raise ValueError('transitdata: Abschnitt "%s" fehlt im Transit-Report. '
                         'Steht der Report vollstaendig in der chart_data (alle '
                         'Codebloecke ab der Fensterzeile)? Sonst transit.py neu '
                         'laufen lassen und den Report unveraendert uebernehmen.'
                         % start_marker.strip())
    i += len(start_marker)
    if not end_marker:
        return txt[i:]
    enden = [end_marker] if isinstance(end_marker, str) else list(end_marker)
    js = [j for j in (txt.find(e, i) for e in enden) if j >= 0]
    return txt[i:min(js)] if js else txt[i:]


# 2026-09-19 (W11): Zeilen, an denen ein weiterer Codeblock als Teil des
# Transit-Reports erkannt wird (Trennlinien, Abschnittskoepfe, Report-Zeilen).
# Themenliste, Ressourcen- und Rechenschaftsbloecke tragen keine davon.
_REPORT_ZEILE = re.compile(
    r'^(?:={20,}\s*$|=== |\s*-- |JETZT|LANGLAEUFER|QUARTALE\s*$|ZUSATZ-ZEITMASSE'
    r'|Fortsetzung nach dem Fenster|Frühere Durchgänge|Orb: Wirk|Quartale: '
    r'|Ephemeride: |Exaktdaten in: |\s+\[(?:P| )(?:\*| )?\] |\s+exakt: '
    r'|\s+im Wirkorb nur: |\s+\d{4}-\d\d(?:-\d\d)?\s)', re.M)
_FENSTER_RE = re.compile(r'Fenster \d{4}-\d\d-\d\d\s*\.\.\s*\d{4}-\d\d-\d\d')


def _report_text(raw):
    """Der Transit-Report als EIN Text (2026-09-19, W11).

    Bis 2026-09-18 las parse() nur den Codeblock mit der Fensterzeile; ein
    Datenblatt, das den Report auf mehrere Bloecke mit Zwischenueberschriften
    verteilt (Rahmen, Jetzt, Langlaeufer, Quartale, Zusatz ...), brach mit
    'substring not found' ab. Jetzt: ab der Fensterzeile der Rest ihres Blocks
    und JEDER folgende Codeblock ohne Sprachangabe (oder ```text), der
    Report-Zeilen traegt; andere Bloecke (Themenliste, Ressourcen, python)
    werden uebersprungen. Steht die Fensterzeile in keinem Codeblock (etwa die
    unveraenderte Ausgabe von transit.py als Datei), gilt der Text ab dort."""
    treffer = list(_FENSTER_RE.finditer(raw))
    if not treffer:
        raise ValueError('transitdata: Fensterzeile "Fenster JJJJ-MM-TT .. '
                         'JJJJ-MM-TT" nicht gefunden — steht der Transit-Report '
                         '(transit.py-Ausgabe) in der chart_data?')
    bloecke = [(m.start(), m.end(), m.group(1).strip().lower(), m.start(2), m.group(2))
               for m in re.finditer(r'^```([^\n]*)\n(.*?)^```[ \t]*$', raw, re.M | re.S)]
    for m0 in treffer:
        for k, (a, b, spr, c0, inhalt) in enumerate(bloecke):
            if a <= m0.start() < b:
                teile = [inhalt[m0.start() - c0:]]
                for _a, _b, spr2, _c, inhalt2 in bloecke[k + 1:]:
                    if spr2 in ('', 'text', 'txt') and _REPORT_ZEILE.search(inhalt2):
                        teile.append(inhalt2)
                return '\n\n'.join(teile)
    return raw[treffer[0].start():]


def parse(pfad=None):
    """Den transit.py-Report aus der chart_data (oder der rohen Report-Datei)
    strukturiert lesen. pfad=None nimmt QUELLE (setze_quelle()).
    Rueckgabe: dict mit den Schluesseln fenster, quartale, stand, im_orb,
    nachhall, anmarsch, stationen, langlaeufer, zeichen, haeuser, hotspots,
    fortsetzung, fruehere, zusatz — Feld fuer Feld im Modul-Docstring
    beschrieben: hilfe('modul'). Wirft ValueError ohne Quelle und mit einer
    lesbaren Meldung, wenn ein Report-Abschnitt fehlt (W11)."""
    pfad = pfad or QUELLE
    if not pfad:
        raise ValueError('transitdata: keine Quelle gesetzt — '
                         'setze_quelle(<klient>_Ultimativ_chart_data.md) '
                         'oder parse(pfad=...) aufrufen.')
    raw = open(pfad, encoding='utf-8').read()
    # §11 liegt in einem eingezäunten Codeblock. Der Anker muss auf die
    # ISO-Fensterzeile IM Codeblock treffen — 'Fenster 2' allein traf bei
    # Fenstern ab 20 Monaten zuerst die §11-Ueberschrift ("Fenster 24 Monate
    # bis ..."), txt endete dann vor dem Codeblock und der Fenster-Regex lief
    # auf None (gefunden 2026-08-03).
    # 2026-09-19 (W11): alle Report-Bloecke ab der Fensterzeile, s. _report_text().
    txt = _report_text(raw)

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
        # 2026-09-19 (W45): Die Zeile traegt seither vier eindeutige Spalten
        # (Orb am Stichtag | Richtung | Nulldurchgang | Wirkorb-Periode).
        # Das alte Format ("... | bis JJJJ-MM-TT") wird weiter gelesen.
        mm = re.match(r'\s*\[(P| )(\*| )\]\s+(\w+)\s+(\w+)\s+(\S+)\s+orb ([\d.]+)° '
                      r'(\w+)(\s*\(kehrt zurueck\))?\s+(.*?)\s*$', ln)
        if mm:
            ex_txt, _, spalte = mm.group(9).partition(' | ')
            ex_txt, spalte = ex_txt.strip(), spalte.strip()
            bis = w_komm = w_vorbei = None
            if spalte.startswith('bis '):                     # Format bis 2026-09-18
                bis = spalte[4:].strip()
            else:
                m2 = re.match(r'Wirkorb bis (\d{4}-\d\d-\d\d)', spalte)
                bis = m2.group(1) if m2 else None
                m2 = re.search(r'(?:wieder |Wirkorb ab )(\d{4}-\d\d-\d\d)'
                               r'(?:\.\.| bis )?(\d{4}-\d\d-\d\d)?', spalte)
                if m2:
                    w_komm = (_d(m2.group(1)), _d(m2.group(2)) if m2.group(2) else None)
                m2 = re.search(r'zuletzt bis (\d{4}-\d\d-\d\d)', spalte)
                w_vorbei = _d(m2.group(1)) if m2 else None
            m3 = re.match(r'exakt (war )?(\d{4}-\d\d-\d\d)', ex_txt)
            out['im_orb'].append({
                'primaer': mm.group(1) == 'P', 'wirkorb': mm.group(2) == '*',
                'transiter': mm.group(3), 'aspekt': mm.group(4), 'ziel': mm.group(5),
                'orb': float(mm.group(6)), 'richtung': mm.group(7),
                'kehrt': bool(mm.group(8)), 'exakt_txt': ex_txt,
                'bis': bis,
                'exakt_datum': _d(m3.group(2)) if m3 else None,
                'exakt_art': ('gewesen' if m3.group(1) else 'kommend') if m3 else 'keiner',
                'wirkorb_txt': (spalte or None) if not spalte.startswith('bis ') else None,
                'wirkorb_kommend': w_komm, 'wirkorb_vorbei_bis': w_vorbei})

    for key, a, b in (('nachhall', '-- Nachhall', '-- Anmarsch'),
                      ('anmarsch', '-- Anmarsch', ('-- Stationen', '\n====='))):
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
    # 2026-09-19: der Block fehlt im Report, wenn keine Station nahe liegt
    for ln in (_block(txt, '-- Stationen im Umfeld', '====')
               if '-- Stationen im Umfeld' in txt else '').splitlines():
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
                   'exakt': [], 'flags': '', 'wirkorb': [],
                   # 2026-09-19 (W1, W3): Vorlauf vor dem Rueckblick, Annaeherungen
                   'vorlauf': None, 'annaeherung': [], 'beginn_abgeschnitten': False}
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
            continue
        # 2026-09-19 (W3): 'vor dem Rueckblick: Orb 3.0° ab D | Wirkorb ab D |
        # exakt D, D' — Beginn der Passage vor dem gerechneten Zeitraum
        mm = re.match(r'\s*vor dem Rueckblick: (.+)$', ln)
        if mm:
            teile = [t.strip() for t in mm.group(1).split(' | ')]
            m_orb = re.search(r'ab (\d{4}-\d\d-\d\d)', teile[0])
            m_wo = re.search(r'Wirkorb ab (\d{4}-\d\d-\d\d)', mm.group(1))
            m_ex = next((t for t in teile if t.startswith('exakt ')), '')
            cur['vorlauf'] = {'orb_ab': _d(m_orb.group(1)) if m_orb else None,
                              'wirkorb_ab': _d(m_wo.group(1)) if m_wo else None,
                              'exakt': [_d(x) for x in re.findall(r'\d{4}-\d\d-\d\d', m_ex)],
                              'text': mm.group(1).strip()}
            cur['beginn_abgeschnitten'] = True
            continue
        # 2026-09-19 (W1): Minima ohne Nulldurchgang — keine Exaktdaten
        mm = re.match(r'\s*Annaeherung ohne Nulldurchgang: (.+)$', ln)
        if mm:
            cur['annaeherung'] = [(_d(a), float(b)) for a, b in
                                  re.findall(r'(\d{4}-\d\d-\d\d) bis ([\d.]+)′', mm.group(1))]

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

    # --- Monats-Dichte -> hotspots -----------------------------------------
    # Das Design-Modul und chartdoc.zeitleiste_page() nennen `hotspots` als
    # Quelle der Spalte „Dichte je Monat"; geparst wurde der Block bis zum
    # 2026-09-07 nicht — die Zeitleisten-Seite haette ihre fuenfte Spalte
    # abtippen muessen (gefunden im Prueflauf Transit). Format im Report:
    #   === MONATS-DICHTE (primaere Wirkorb-Kontakte) ===
    #     2026-07:15(10) · 2026-08:15(3) · ...
    out['hotspots'] = []
    if 'MONATS-DICHTE' in txt:
        # Endmarker erst NACH der Kopfzeile suchen: die Kopfzeile schliesst
        # selbst mit '===' ab, ein Start bei 'MONATS-DICHTE' lieferte sonst
        # nur ' (primaere Wirkorb-Kontakte) '.
        _i = txt.index('MONATS-DICHTE')
        _i = txt.index('\n', _i)
        _j = txt.find('===', _i)                  # 2026-09-19: Ende auch am Textende
        seg = txt[_i:_j if _j >= 0 else len(txt)]
        for jahr, mon, aktiv, exakt in re.findall(
                r'(\d{4})-(\d\d):(\d+)\((\d+)\)', seg):
            out['hotspots'].append({'jahr': int(jahr), 'monat': int(mon),
                                    'aktiv': int(aktiv), 'exakt': int(exakt),
                                    'label': MON_KURZ[int(mon)]})

    # --- 2026-09-19 (W3, W46): Abschnitte hinter den Ingressen -------------
    out['fortsetzung'] = []
    for ln in (_sektion(txt, 'Fortsetzung nach dem Fenster') or '').splitlines():
        mm = _KONTAKT_RE.match(ln)
        if not mm:
            continue
        teile = [t.strip() for t in mm.group(5).split(' | ')]
        ex, mo, md, ann = _exakt_teil(teile[0])
        wb = re.match(r'Wirkorb bis (\d{4}-\d\d-\d\d)', teile[1]) if len(teile) > 1 else None
        ob = re.search(r'bis (\d{4}-\d\d-\d\d)', teile[2]) if len(teile) > 2 else None
        out['fortsetzung'].append({
            'primaer': mm.group(1) == 'P', 'transiter': mm.group(2),
            'aspekt': mm.group(3), 'ziel': mm.group(4), 'exakt': ex,
            'annaeherung': ann, 'min_orb': mo, 'min_datum': md,
            'wirkorb_bis': _d(wb.group(1)) if wb else None,
            'orb_bis': _d(ob.group(1)) if ob else None,
            'ueber_horizont': len(teile) > 2 and 'Rechenhorizont' in teile[2],
            'text': mm.group(5).strip()})

    out['fruehere'] = []
    for ln in (_sektion(txt, 'Frühere Durchgänge mit Datum und Alter') or '').splitlines():
        mm = _KONTAKT_RE.match(ln)
        if not mm:
            continue
        rest = mm.group(5).strip()
        eintrag = {'primaer': mm.group(1) == 'P', 'transiter': mm.group(2),
                   'aspekt': mm.group(3), 'ziel': mm.group(4),
                   'keiner': rest.startswith('keiner'), 'durchgaenge': []}
        if not eintrag['keiner']:
            for teil in re.split(r'\s·\s(?=#\d)', rest):
                m2 = re.match(r'#(\d+) (.*)$', teil.strip())
                if not m2:
                    continue
                body = m2.group(2)
                paare, offen = [], []
                for d_, a_ in re.findall(r'(\d{4}-\d\d-\d\d)|\(Alter (\d+)\)', body):
                    if d_:
                        offen.append(_d(d_))
                    else:
                        paare += [(x, int(a_)) for x in offen]; offen = []
                paare += [(x, None) for x in offen]
                nicht = body.startswith('nicht exakt')
                m_orb = re.search(r'engster Orb ([\d.]+)°', body)
                m_ann = re.search(r'Annaeherung bis ([\d.]+)′', body)
                eintrag['durchgaenge'].append({
                    'nr': int(m2.group(1)),
                    'exakt': [] if nicht else paare, 'nicht_exakt': nicht,
                    'datum': paare[0][0] if (nicht and paare) else None,
                    'alter': paare[0][1] if (nicht and paare) else None,
                    'orb_grad': (float(m_orb.group(1)) if m_orb else
                                 (float(m_ann.group(1)) / 60.0 if m_ann else None)),
                    'annaeherung': bool(m_ann),
                    'bei_geburt': ('[lief schon bei der Geburt]' in body
                                   or '[reicht vor den Rechenbeginn]' in body),
                    'text': teil.strip()})
        out['fruehere'].append(eintrag)

    out['zusatz'] = _zusatz(_sektion(txt, 'ZUSATZ-ZEITMASSE (progressiver Mond, '
                                          'Sonnenbogen, Profektion, Finsternisse)'))
    return out


# --- 2026-09-19: Hilfen fuer die neuen Abschnitte --------------------------
_KONTAKT_RE = re.compile(r'\s*\[(P| )\]\s+(\w+)\s+(\w+)\s+(\S+)\s+(.*)$')


def _sektion(txt, titel):
    """Inhalt eines mit '=====' gerahmten Abschnitts (Titelzeile woertlich)
    bis zur naechsten Trennlinie; None, wenn der Abschnitt fehlt (aelterer
    Report)."""
    m = re.search(r'^' + re.escape(titel) + r'\s*\n=+[ \t]*\n', txt, re.M)
    if not m:
        return None
    rest = txt[m.end():]
    n = re.search(r'^={20,}[ \t]*$', rest, re.M)
    return rest[:n.start()] if n else rest


def _exakt_teil(t):
    """'exakt D, D' | 'kein Exaktkontakt (min X° am D)' |
    'kein Exaktkontakt, Annaeherung bis x′ am D' ->
    (exakt[], min_orb|None, min_datum|None, (datum, bogenminuten)|None)"""
    if t.startswith('exakt '):
        return [_d(x) for x in re.findall(r'\d{4}-\d\d-\d\d', t)], 0.0, None, None
    m = re.search(r'Annaeherung bis ([\d.]+)′ am (\d{4}-\d\d-\d\d)', t)
    if m:
        return [], float(m.group(1)) / 60.0, _d(m.group(2)), (_d(m.group(2)), float(m.group(1)))
    m = re.search(r'min ([\d.]+)° am (\d{4}-\d\d-\d\d)', t)
    if m:
        return [], float(m.group(1)), _d(m.group(2)), None
    return [], None, None, None


def _zusatz(seg):
    """Abschnitt ZUSATZ-ZEITMASSE -> dict (2026-09-19, W46); {} ohne Abschnitt."""
    if not seg:
        return {}
    z = {'prog_mond': [], 'prog_mond_wechsel': [], 'sonnenbogen': [],
         'profektion': [], 'finsternisse': []}
    teil = None
    for ln in seg.splitlines():
        s = ln.strip()
        if s.startswith('-- '):
            k = s.lower()
            teil = ('prog_mond_wechsel' if 'wechsel' in k else
                    'prog_mond' if 'progressiver mond' in k else
                    'sonnenbogen' if 'sonnenbogen' in k else
                    'profektion' if 'profektion' in k else
                    'finsternisse' if 'finsternis' in k else None)
            continue
        if not s or teil is None:
            continue
        if teil == 'prog_mond':
            m = re.match(r'(\d{4}-\d\d-\d\d)\s+(.+?)(?:\s+\(H(\d+)\))?$', s)
            if m:
                z[teil].append({'datum': _d(m.group(1)), 'stand': m.group(2).strip(),
                                'haus': int(m.group(3)) if m.group(3) else None})
        elif teil == 'prog_mond_wechsel':
            m = re.match(r'(\d{4}-\d\d-\d\d)\s+(Zeichen|Haus)\s+(\S+) -> (\S+)$', s)
            if m:
                z[teil].append({'datum': _d(m.group(1)), 'art': m.group(2),
                                'von': m.group(3), 'nach': m.group(4)})
        elif teil == 'sonnenbogen':
            m = re.match(r'(\d{4}-\d\d)\s+(\S+)\s+(\S+)\s+(\S+)\s+Orb ([\d.]+)°'
                         r'(?:\s+exakt (\d{4}-\d\d-\d\d)(?: \((vor|nach) dem Fenster\))?)?', s)
            if m:
                z[teil].append({'monat': m.group(1), 'punkt': m.group(2),
                                'aspekt': m.group(3), 'ziel': m.group(4),
                                'orb': float(m.group(5)),
                                'exakt': _d(m.group(6)) if m.group(6) else None,
                                'exakt_im_fenster': bool(m.group(6)) and not m.group(7)})
        elif teil == 'profektion':
            m = re.match(r'Alter (\d+) -> (\d+)\. Haus \((\S+)\), Herrscher (\S+)'
                         r'(?: in (.+?))?(?:, Haus (\S+?)(?: \((.*)\))?)?$', s)
            if m:
                z[teil].append({'alter': int(m.group(1)), 'haus': int(m.group(2)),
                                'zeichen': m.group(3), 'herrscher': m.group(4),
                                'herrscher_stand': m.group(5),
                                'herrscher_haus': m.group(6),       # '12/11' = fuehrend vorn
                                'grenzlage': m.group(7)})
        elif teil == 'finsternisse':
            m = re.match(r'(\d{4}-\d\d-\d\d)\s+(Sonnenfinsternis|Mondfinsternis)\s+'
                         r'(.+?)\s+-> (.*)$', s)
            if m:
                z[teil].append({'datum': _d(m.group(1)), 'typ': m.group(2),
                                'stand': m.group(3).strip(),
                                'trifft': [(n, float(o)) for n, o in
                                           re.findall(r'(\S+) ([\d.]+)°', m.group(4))]})
    return z


def dichte_je_monat(daten, a, b, trenner=' · '):
    """'Jul 15 (10) · Aug 15 (3) · Sep 14 (4)' fuer die Quartalsspanne a..b.

    Reine Auswahl aus `hotspots`, keine Rechnung: die Monatswerte werden
    weder summiert noch gemittelt noch gerundet (Design-Modul,
    „Zeitleisten-Seite"). Fehlt der MONATS-DICHTE-Block im Report, kommt ein
    leerer String zurueck — dann steht die Spalte leer statt falsch.
    """
    return trenner.join(
        f"{h['label']} {h['aktiv']} ({h['exakt']})"
        for h in daten.get('hotspots', [])
        if (a.year, a.month) <= (h['jahr'], h['monat']) <= (b.year, b.month))


def _selbsttest(still=False):
    """2026-09-19 (W11, W45, W3, W46, F22) — python3 transitdata.py --selbsttest.

    Der Report wird mit transit.py aus einem KONSTRUIERTEN Radix erzeugt
    (Laengen aus Ephemeriden-Staenden an frei gewaehlten julianischen Daten,
    Moshier, keine Personendaten) und einmal als Datei, einmal auf mehrere
    Codebloecke verteilt gelesen. Rueckgabe True, wenn alles gruen ist."""
    import os, tempfile, sys as _s
    fehler = []
    def pruefe(bed, text):
        if not bed:
            fehler.append(text)
    # F22
    pruefe('☊' in kurz('Saturn', 'Quadrat', 'Mondknoten')
           and '⊗' in kurz('Saturn', 'Quadrat', 'Glückspunkt'),
           "F22: Glyphe fuer Mondknoten/Glückspunkt fehlt")
    # F24 (2026-09-19, Runde 2): Achsen und Pholus stehen in der Uhr-Zeile nur
    # mit Namen — ein Kuerzel als Glyphe verdoppelte ihn („MC MC").
    for _n in ('AC', 'MC', 'DC', 'IC', 'Pholus'):
        _k = kurz('Neptun', 'Quincunx', _n)
        pruefe(_k.split().count(_n) == 1 and GLYPH.get(_n, '') == '',
               "F24: %s steht in kurz() doppelt oder mit Kuerzel: %r" % (_n, _k))
    try:
        _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import transit as T
        import swisseph as swe
    except ImportError as e:
        print("Selbsttest transitdata.py: transit.py/pyswisseph nicht ladbar (%s) — "
              "nur F22 geprueft" % e)
        return not fehler
    FL = T.MOSEPH
    jg = 2440000.5
    lon = lambda pl, jd: swe.calc_ut(jd, pl, FL)[0][0]
    rad = {'Sonne': lon(swe.SUN, jg), 'Mond': lon(swe.MOON, jg),
           'Jupiter': lon(swe.JUPITER, jg), 'Saturn': lon(swe.SATURN, jg),
           'Mondknoten': lon(swe.TRUE_NODE, jg), 'AC': (lon(swe.SUN, jg) + 95.0) % 360.0,
           'MC': (lon(swe.SUN, jg) + 5.0) % 360.0}
    start = T.d_from_jd(jg + 23.5 * 365.25)
    res = T.run(rad, start=start, months=24, lookback_months=6, ohne_chiron=True,
                moseph=True, jd_geburt=jg)
    rep = T.format_report(res) + '\n' + T.format_zusatz(
        T.zusatzzeitmasse(rad, jg, T.date.fromisoformat(res['start']),
                          T.date.fromisoformat(res['end'])))
    tmp = tempfile.mkdtemp(prefix='transitdata_test_')
    def schreibe(name, text):
        p = os.path.join(tmp, name)
        open(p, 'w', encoding='utf-8').write(text)
        return p
    d1 = parse(schreibe('report.txt', rep))
    # W11: derselbe Report auf Codebloecke verteilt, dazwischen Ueberschriften,
    # davor ein python-Block, dahinter eine Themenliste
    zeilen = rep.split('\n')
    schnitt = [i for i, l in enumerate(zeilen) if l.startswith('=' * 70)
               and i + 1 < len(zeilen) and not zeilen[i + 1].startswith('=')]
    md = ['# Testblatt', '', '```python', "factors = [{'name': 'X', 'lon': 1.0}]", '```', '']
    a = 0
    for k, i in enumerate(schnitt[1:] + [len(zeilen)]):
        md += ['### Block %d' % k, '', '```'] + zeilen[a:i] + ['```', '']
        a = i
    md += ['## Themenliste', '', '```', 'THEMA 1 | titel=Test | aspekte=T-Saturn □ R-Sonne', '```']
    d2 = parse(schreibe('mehrblock.md', '\n'.join(md)))
    pruefe(len(schnitt) >= 5, "W11: Testaufbau hat zu wenige Bloecke")
    pruefe(d1 == d2, "W11: Mehrblock-Lesung weicht von der Einblock-Lesung ab: %s"
           % [k for k in d1 if d1.get(k) != d2.get(k)])
    # Inhalt gegen die Rechnung
    rows = [x for x in res['jetzt']['im_orb'] if not x['spiegel']]
    pruefe(len(d1['im_orb']) == len(rows), "W45: Zahl der Jetzt-Zeilen weicht ab")
    for x, y in zip(rows, d1['im_orb']):
        pruefe(y['bis'] == (x['wirkorb_jetzt'][1] if x['wirkorb_jetzt'] else None)
               or (x['wirkorb_jetzt'] and x['wirkorb_jetzt'][1] >= res['fortsetzung_horizont']),
               "W45: 'bis' ist nicht das Ende der Wirkorb-Periode am Stichtag")
        pruefe('|' not in y['exakt_txt'], "W45: Exakt-Spalte enthaelt die Wirkorb-Spalte")
    pruefe(len(d1['langlaeufer']) == len(res['langlaeufer'])
           and all([str(e) for e in y['exakt']] == x['exakt']
                   for x, y in zip(res['langlaeufer'], d1['langlaeufer'])),
           "W1: Exaktdaten der Langlaeufer weichen von der Rechnung ab")
    fo = [e for e in res['events'] if e.get('fortsetzung') and not e['spiegel']]
    pruefe(len(d1['fortsetzung']) == len(fo) and len(fo) > 0,
           "W3: Abschnitt 'Fortsetzung nach dem Fenster' unvollstaendig gelesen")
    ex_res = sorted(d for e in fo for d in e['fortsetzung']['exakt'])
    ex_rep = sorted(str(d) for f in d1['fortsetzung'] for d in f['exakt'])
    pruefe(ex_res == ex_rep, "W3: Exaktdaten nach dem Fenster weichen ab")
    pruefe(len(d1['fruehere']) == len(res['fruehere_durchgaenge']),
           "W3: Abschnitt 'Frühere Durchgänge mit Datum und Alter' unvollstaendig gelesen")
    for f, g in zip(res['fruehere_durchgaenge'], d1['fruehere']):
        erw = [[(x['datum'], x['alter']) for x in dg['exakt']] for dg in f['durchgaenge']]
        ist = [[(str(dd), aa) for dd, aa in dg['exakt']] for dg in g['durchgaenge']]
        pruefe(erw == ist, "W3: Daten/Alter der frueheren Durchgaenge weichen ab: %s" % f['transit'])
    pruefe(any(g['durchgaenge'] for g in d1['fruehere']),
           "W3: im Testaufbau kein frueherer Durchgang gefunden")
    pruefe(d1['zusatz'] and len(d1['zusatz']['prog_mond']) == 8,
           "W46: Zusatz-Zeitmasse nicht gelesen")
    # altes Jetzt-Format ("| bis JJJJ-MM-TT") bleibt lesbar
    import re as _re
    tag_alt = T.d_from_jd(2451545.0).isoformat()      # konstruiert, aus einem JD
    alt = _re.sub(r' \| (?:Wirkorb|nie im Wirkorb)[^\n]*', ' | bis ' + tag_alt, rep)
    d3 = parse(schreibe('alt.txt', alt))
    pruefe(all(y['bis'] == tag_alt for y in d3['im_orb']) and d3['im_orb'],
           "W45: altes Jetzt-Format nicht mehr lesbar")
    # fehlender Stationen-Block bricht nicht ab; fehlender Pflichtabschnitt laut
    ohne = _re.sub(r'\n  -- Stationen im Umfeld des Stichtags --\n(?:     [^\n]*\n)*', '\n', rep)
    pruefe(parse(schreibe('ohne_st.txt', ohne))['stationen'] == [],
           "W11: Report ohne Stationen-Block nicht lesbar")
    try:
        parse(schreibe('kaputt.txt', rep.replace('-- im Orb', '-- XX')))
        pruefe(False, "W11: fehlender Abschnitt ohne Fehlermeldung")
    except ValueError as e:
        pruefe('fehlt im Transit-Report' in str(e), "W11: Fehlermeldung unklar: %s" % e)
    if not still:
        if fehler:
            print("Selbsttest transitdata.py: %d FEHLER" % len(fehler))
            for f_ in fehler:
                print("  - " + f_)
        else:
            print("Selbsttest transitdata.py: alle Faelle gruen (W11, W45, W3, W46, F22, F24)")
    return not fehler


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
    if _hilfe_cli():          # python3 transitdata.py --hilfe [<name>]
        _s.exit(0)
    if '--selbsttest' in _s.argv[1:]:
        _s.exit(0 if _selbsttest() else 1)
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
