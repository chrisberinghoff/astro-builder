#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REFERENZ: Chart-Builder fuer das PDF der Vertiefung (neu 2026-10-10).

Die Vertiefung ist ein eigenes PDF zu einer Frage oder bis zu zwei
Lebensbereichen, gelesen aus einem schon gelieferten Horoskop (Erweiterung
Vertiefung, `claude/Projektanweisung_Erweiterung_Vertiefung.md`). Diese
Vorlage traegt nur, was sie braucht:

    1. PALETTE   Farbwerte, abgeleitet aus DECKBLATT['PALETTE'] — derselbe
                 Wortlaut wie im frueheren Horoskop, damit das Heft dazu passt
    2. das schlichte Deckblatt: Kicker (Dokumenttyp der H1), Vorname, Linie,
       die tragenden Glyphen, der TITEL (die Untertitelzeile der analyse.md:
       die Frage oder das Thema), unten Leitsatz und Quellzeile.
       KEIN Titelmotiv, kein Sternfeld, kein Rad.
    3. ANALYSE / CHARTDATA / OUT / QUELLZEILE / DATUM

Keine Chartbild-Strecke (Radix, Konstellationen, Aspekte) — sie steht im
Hauptdokument. DOCTYPE = 'vertiefung' prueft deshalb als Pflicht nur das
Inhaltsverzeichnis (build.PFLICHT_BAUSTEINE). Kapitel, Verzeichnis,
Kapitelfuss mit Signatur und Beleg, satzsicherer Umbruch, Zwei-Pass-
Seitenzahlen und die Datenschutz-Zeile der Inhaltsseite kommen aus chartdoc
und werden NICHT neu geschrieben.

ZWEI DINGE, DIE HIER BEWUSST SO STEHEN:
  * LEITSATZ, PALETTE und GLYPHEN werden GELESEN, nicht abgetippt:
    `build.lies_deckblatt()` holt sie aus dem @@DECKBLATT-Block am Ende der
    Vertiefungs-chart_data (`<klient>_Vertiefung_<Datum>_chart_data.md`).
    Der TITEL ist die Untertitelzeile der analyse.md (`parsed['untertitel']`).
    Fehlt einer von beiden, bricht der Lauf ab.
  * Die Vorlage liefert MECHANIK, nie Inhalt. Die Palette ist PLATZHALTER mit
    sichtbarer Marke (PALETTE_GESETZT): Solange sie steht, laeuft der Builder
    nicht — so rendert kein Lauf still die Farben eines anderen Horoskops.

ENGLISCHE FASSUNG: SPRACHE = 'en', SIGNATUR_EN fuellen (je Kapitel die
Signatur, deutsch -> englisch), BELEG_EN nur, wo die mechanische Uebersetzung
nicht reicht; QUELLZEILE englisch. Verfahren: Modul Sprachfassung.

Aufruf:  python3 <klient>_vertiefung_builder.py
Geprueft wird beim Rendern automatisch: build.PFLICHT_BAUSTEINE fuer DOCTYPE.
"""
import sys

sys.path.insert(0, '/home/claude')
import build                                   # noqa: E402
import chartdoc                                # noqa: E402

KLIENT = '<Vollstaendiger Name aus der H1 der analyse.md>'
VORNAME = '<Vorname>'
DATUM = '<JJJJ-MM-TT>'    # das Datum im Namen der Vertiefungs-Dateien — PDF, Analyse und Datenblatt tragen dasselbe
CHARTDATA = f'/home/claude/<klient>_Vertiefung_{DATUM}_chart_data.md'
ANALYSE = f'/home/claude/<klient>_Vertiefung_{DATUM}_analyse.md'
OUT = f'/home/claude/Vertiefung_<klient>_{DATUM}.pdf'   # = Name im Klientenordner, Unterordner 05_Vertiefung
DOCTYPE = 'vertiefung'    # build.PFLICHT_BAUSTEINE
# Quellzeile des Deckblatts (unten, Versalien): woraus gelesen wurde.
# Wortlaute: Erweiterung Vertiefung, Chat 2, „Deckblatt“ — z. B. 'AUS DEINEM GEBURTSHOROSKOP'
# · 'AUS DEINEM GEBURTS- UND TRANSIT-HOROSKOP' · englisch 'FROM YOUR BIRTH CHART'
QUELLZEILE = '<AUS DEINEM GEBURTSHOROSKOP>'
SPRACHE = 'de'
SIGNATUR_EN = {}
BELEG_EN = {}

from build import BASE_CSS                     # noqa: E402

# --- Deckblatt-Angaben: gelesen, nie abgetippt -------------------------------
DECKBLATT = build.lies_deckblatt(CHARTDATA)
LEITSATZ = DECKBLATT['LEITSATZ']
PALETTE_VORGABE = DECKBLATT['PALETTE']      # steuert die Farbwahl unten
ORNAMENT = DECKBLATT['GLYPHEN']             # Deckblatt und Inhaltsverzeichnis

parsed = build.parse_analyse(ANALYSE, client=KLIENT)
TITEL = (parsed.get('untertitel') or '').strip()
items = build.prepare_chapters(parsed)
colon_pairs = build.make_colon_pairs(items)
KICKER = parsed['doctype'].upper()          # Cover-Kickerzeile = Dokumenttyp der H1
INHALT_KOPF = {'de': 'Vertiefung für {name}',
               'en': 'Deep Dive for {name}'}[SPRACHE]

PART_KICKER = set()                         # keine Teiler-Kapitel
OPEN_PAGE = {'Zur Lesart', 'On Reading This'}   # eigene Seite; die uebrigen laufen weiter

# --- Palette ---------------------------------------------------------------
# Je Vertiefung aus PALETTE_VORGABE abgeleitet — dem Wortlaut des frueheren
# Horoskops. Was hier steht, sind PLATZHALTER. Sind die Werte und die zwei
# Verlaufsstopps unten gesetzt, PALETTE_GESETZT auf True stellen.
PALETTE_GESETZT = False   # <<auf True setzen, sobald NIGHT … BELEG_BD und VERLAUF aus PALETTE_VORGABE abgeleitet sind>>
NIGHT = '#0a1a26'
PETROL = '#1d4a53'
PETROL_L = '#3d6b72'
DEEP = '#123540'
GOLD = '#a37c37'
GOLD_L = '#c9a45e'
STONE = '#7a6a52'
PAPER = '#f8f4ec'          # = radix.DEFAULT_PALETTE['grund'], nicht aendern
INK = '#241f1a'
BELEG_BG = '#f1ebda'
BELEG_BD = '#cbb07a'
VERLAUF = (NIGHT, DEEP)    # Deckblatt von oben nach unten — zwei dunkle Toene der Palette

PAL = {'night': NIGHT, 'petrol': PETROL, 'petrol_l': PETROL_L, 'deep': DEEP,
       'gold': GOLD, 'gold_l': GOLD_L, 'stone': STONE, 'paper': PAPER,
       'ink': INK, 'beleg_bg': BELEG_BG, 'beleg_bd': BELEG_BD}

chartdoc.konfiguriere(pal=PAL, part_kicker=PART_KICKER, glyphen={},
                      kopfzeile=VORNAME.upper(), part_ornament=ORNAMENT,
                      sprache=SPRACHE, signaturen_en=SIGNATUR_EN,
                      belege_en=BELEG_EN)
esc = chartdoc.esc

COVER_CSS = f"""
/* ---------- Deckblatt der Vertiefung (schlicht) ---------- */
section.cover {{ page: cover; position:relative; width:21cm; height:29.7cm;
                 overflow:hidden; }}
.cv-grund {{ position:absolute; top:0; left:0; width:21cm; height:29.7cm;
  background: linear-gradient(to bottom, {VERLAUF[0]} 0%, {VERLAUF[1]} 100%); }}
.cv-block {{ position:absolute; left:0; right:0; text-align:center; }}
.cv-kicker {{ font-family:"EB Garamond"; font-size:8.2pt; letter-spacing:0.42em;
   color:{GOLD_L}; }}
.cv-name {{ font-family:"Cinzel"; font-size:31pt; letter-spacing:0.15em;
   color:#f2ead6; }}
.cv-rule {{ width:3.2cm; height:1pt; background:{GOLD_L}; margin:0 auto; }}
.cv-orn {{ font-family:"DejaVu Sans","FreeSerif",sans-serif; font-size:17pt;
   letter-spacing:0.5em; color:{GOLD_L}; }}
.cv-titel {{ position:absolute; left:2.6cm; right:2.6cm; text-align:center;
   font-family:"EB Garamond Italic"; font-style:italic; font-size:21pt;
   line-height:1.3; color:#f3ead6; }}
.cv-leit {{ font-family:"EB Garamond Italic"; font-style:italic; font-size:15.4pt;
   color:#f3ead6; letter-spacing:0.02em; }}
.cv-birth {{ font-family:"EB Garamond"; font-size:8.6pt; letter-spacing:0.2em;
   color:#e3d3ae; }}
"""


def y2cm(y):
    return y / 842 * 29.7


def cover_html(kicker):
    """Das schlichte Deckblatt. `kicker` ist der DOKUMENTTYP AUS DER H1 der
    analyse.md in Versalien. Hoehen im 842-Raster: 88 Kicker, 112 Name,
    168 Linie, 230 Glyphen, 300 Titel (waechst nach unten), 788 letzte
    Leitsatzzeile (waechst nach oben, chartdoc.leitsatz_block()),
    822 Quellzeile."""
    return f"""<section class="cover">
<div class="cv-grund"></div>
<div class="cv-block cv-kicker" style="top:{y2cm(88):.2f}cm">{esc(kicker)}</div>
<div class="cv-block cv-name" style="top:{y2cm(112):.2f}cm">{esc(VORNAME.upper())}</div>
<div class="cv-block" style="top:{y2cm(168):.2f}cm"><div class="cv-rule"></div></div>
<div class="cv-block cv-orn" style="top:{y2cm(230):.2f}cm">{esc(ORNAMENT)}</div>
<div class="cv-titel" style="top:{y2cm(300):.2f}cm">{esc(TITEL)}</div>
{chartdoc.leitsatz_block(LEITSATZ)}
<div class="cv-block cv-birth" style="top:{y2cm(822):.2f}cm">{esc(QUELLZEILE)}</div>
</section>"""


# Seitenzahlen fuers Inhaltsverzeichnis: erster Durchlauf leer, danach aus dem
# gerenderten Dokument gefuellt (chartdoc.render_mit_inhalt).
SEITEN = {}


def build_html(breaks=()):
    """Das ganze Dokument: Deckblatt, Inhalt, Kapitel."""
    parts = [f'<!doctype html><html lang="{SPRACHE}"><head><meta charset="utf-8">'
             '<style>', BASE_CSS, chartdoc.struktur_css(), COVER_CSS,
             '</style></head><body>',
             cover_html(KICKER),
             chartdoc.inhalt_page(items, SEITEN, INHALT_KOPF.format(name=VORNAME),
                                  vorne=(), ornament=ORNAMENT)]
    # Kapitel-Sektionen: Kopf, Koerper und Fuss mit Signatur/Beleg in EINEM
    # Aufruf. Fehlt der Fuss, bricht render_mit_inhalt() hart ab.
    for i, it in enumerate(items):
        parts.append(chartdoc.build_section(i, it, breaks,
                                            part_kicker=PART_KICKER,
                                            open_page=OPEN_PAGE,
                                            erstes=(i == 0)))
    parts.append('</body></html>')
    return '\n'.join(parts)


if __name__ == '__main__':
    if not PALETTE_GESETZT:
        raise SystemExit('REFERENZ-Vorlage: Palette und Verlauf sind noch '
                         'Platzhalter — aus DECKBLATT["PALETTE"] ableiten, dann '
                         'PALETTE_GESETZT = True setzen (Erweiterung Vertiefung, '
                         '„Chat 2“).')
    for _n, _v in (('QUELLZEILE', QUELLZEILE), ('OUT', OUT), ('DATUM', DATUM)):
        if '<' in _v and '>' in _v:
            raise SystemExit('REFERENZ-Vorlage: %s traegt noch den Platzhalter.' % _n)
    if not TITEL:
        raise SystemExit('Der Titel des Deckblatts fehlt: Er ist die '
                         'Untertitelzeile direkt unter der H1 der analyse.md '
                         '(die Frage oder das Thema) — in Chat 1 nachtragen.')
    _titel_probe = TITEL.split('\n')[0][:30]
    doc, seiten = chartdoc.render_mit_inhalt(
        build_html, OUT, items, colon_pairs, SEITEN,
        required_fields={'Leitsatz': LEITSATZ, 'Titel': TITEL},
        extra_must=[(LEITSATZ.split(' — ')[0].split('\n')[0], 'Leitsatz aufs Deckblatt'),
                    (_titel_probe, 'Titel aufs Deckblatt')],
        doctype=DOCTYPE)
    print('Kapitel:', len(items), '| Seiten:', len(doc.pages),
          '| Inhalt:', seiten.get('PG_inhalt'))
