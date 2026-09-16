#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inhaltsprobe — haelt eine fertige `<klient>_analyse.md` gegen ihre
`<klient>_chart_data.md`.

Warum es dieses Modul gibt (Startprompt `claude/STARTPROMPT_Inhaltsprobe_2026-09-16.md`,
Chris-Auftrag vom 16.09.2026): Rund dreissig inhaltliche Gegenproben stehen in
Datenblatt-, Klartext-, Innere-Arbeit- und Typmodul. Alle laufen in demselben Lauf,
der den Text gerade geschrieben hat, still und ohne Ergebniszeile — und keine
Funktion haelt die Analyse gegen das Datenblatt. `build.verify()` prueft Struktur
und Layout, `build.aspekt_heimat()` die Themenliste gegen die Aspekttabellen: beides
INNERHALB einer Datei, nie zwischen den beiden. Der "erfundene Aspekt" (liest sich
praezise und ist falsch) hatte bis zu diesem Modul keine einzige Pruefung.

Die Inhaltsprobe prueft, sie beurteilt nicht: Ob eine Deutung trifft, kann kein
Skript sagen. Was sie meldet, ist falsch oder regelwidrig, mit Stelle. Sie kostet
null Token je Lauf und laeuft in Schritt 2 (nach dem Schreiben) und in Schritt 3+4
(vor dem Rendern) — s. `lade.SCHRITTE`.

Schnittstelle
-------------
    inhaltsprobe.pruefe(analyse_pfad, chart_data_pfad, typ=None) -> dict
    inhaltsprobe.bericht(analyse_pfad, chart_data_pfad, typ=None) -> str
    python3 inhaltsprobe.py <analyse.md> <chart_data.md> [--typ geburt|ea|transit|ultimativ]
    python3 inhaltsprobe.py --selbsttest

`typ` wird aus der H1 der Analyse abgeleitet (Dokumenttyp links vom " — "); der
Parameter ueberstimmt. Ein unbekannter Typ laeuft mit den typunabhaengigen Proben,
die typabhaengigen werden als uebersprungen gemeldet — nie geraten.

Rueckgabewert der CLI: 0 ohne FEHLER, 1 mit FEHLER, 2 wenn eine der beiden Dateien
nicht lesbar ist (SchemaError aus `build.parse_analyse()`, fehlende Datei).

Wiederverwendet, nicht nachgebaut: `build.parse_analyse()` (Kapitel mit kicker,
title, signatur, beleg, blocks), `build.lies_deckblatt()` (Leitsatz),
`selektor.parse_chart()` (Faktoren, Zeichen, Haeuser, Achsen aus dem
`@@SELEKTOR`-Block), `selektor.norm()` / `norm_faktor()` (Namensnormalisierung).
Die Regexe fuer Aspekttabellen und Themenliste sind woertlich aus
`build.aspekt_heimat()` und `build._ressourcen_zeilen()` uebernommen — dort sind sie
verschachtelt und nicht importierbar; die Fundstelle steht jeweils im Kommentar,
damit eine spaetere Aenderung an einer Stelle die andere findet. `build.py` selbst
wird nicht geaendert.

Zwei Schweregrade, sonst nichts
-------------------------------
FEHLER   eindeutig, mechanisch entscheidbar (Aspekt nicht in der Tabelle, Orb
         weicht ab, falscher Fuehrer, fehlende Bewegung, fehlende Registerzeile,
         Leitsatz nicht im Schlusswort).
PRUEFEN  ein Treffer, der ein Auge braucht (Wortlisten, Stufe im Beleg, Titel
         weicht von der Themenliste ab, Suedknoten-Aspekt als Spiegel).
Dazu AUSSAGELOS: Findet eine Probe nichts, was sie pruefen koennte — keine
Beleg-Segmente, keine Themenliste, kein Rechenschaftskapitel —, meldet sie das
ausdruecklich und nie "bestanden". Der stille Freispruch ist der Fehler, der in
`aspekt_heimat()` zweimal gebaut wurde (06.09. und 14.09.); er wird hier nicht ein
drittes Mal gebaut. UEBERSPRUNGEN heisst: bewusst nicht gelaufen (Typ unbekannt,
Getriebe-Beleg, kein Rechenschaftskapitel im Typ) — mit Grund.

Die neun Proben
---------------
P1  Beleg-Aspekte    jedes Aspekt-Segment eines Normal-Belegs (Faktor A, Aspektart,
                     Faktor B, Orb) muss so in einer der vier Aspekttabellen stehen,
                     Orb auf 1' genau; Stufe (voll/einseitig/neben) nur PRUEFEN.
                     Instrument- und Zugang-Beleg: nur die Aspektangaben hinter den
                     Staenden; Getriebe-Beleg (Struktur-Format) uebersprungen.
P2  Beleg-Staende    Segment 1 jedes Normal-Belegs und jedes Instrument-Segment:
                     Zeichen und Haus gegen den @@SELEKTOR-Block (bei Grenzlage das
                     fuehrende Haus vorn), Gradminute gegen die Staendetabelle.
P3  Kapitel/Themen   nummerierte Themenkapitel (Kapitel n, n >= 2) in
                     Dokumentreihenfolge gegen die THEMA-Zeilen: gleiche Zahl, an
                     jeder Stelle der Fuehrer aus fuehrt= in Segment 1 des Belegs
                     UND in der Signatur; Titel nur PRUEFEN. (Nur Geburtshoroskop —
                     das Kapitel-Skelett der anderen Typen ist hier nicht hinterlegt.)
P4  Bewegungsfolge   je Themenkapitel die ###-Zwischentitel gegen WORTLAUTE[typ]:
                     volle Folge sieben in fester Reihenfolge; Kurzform (form=kurz,
                     Ressourcen-Bauform, Zugang) ohne Wurzel und Widerstand.
P5  Rechenschaft     jeder Faktor des @@SELEKTOR-Blocks, der kein Thema fuehrt,
                     braucht eine Zeile im Kapitel `Rechenschaft`, die mit seinem
                     Namen beginnt; eine Zeile fuer einen Fuehrer: PRUEFEN. Achsen
                     zaehlen nicht, der Suedknoten mit eigener FAKTOR-Zeile schon.
P6  Leitsatz         LEITSATZ aus @@DECKBLATT im Schlusswort (wortgleich nach
                     Leerraum-Normalisierung, ersatzweise vier Fuenftel der Woerter
                     in Reihenfolge); genau EINE THEMA-Zeile mit leitachse=ja.
P7  Signatur         der Fuehrer steht in der Signatur — eigene Ergebniszeile,
                     inhaltlich in P3 mitgeprueft.
P8  Wortlisten       ueber den Fliesstext aller Kapitel ausser Auftakt und
                     Rechenschaft, nie ueber Signatur und Beleg: Dritte (Innere
                     Arbeit, Prinzip 13), Vergangenheits-Indikativ (Prinzip 5),
                     Fachbegriffe, Gradzahlen und Hausnummern in Ziffern
                     (Klartext-Verbotsscan; Liste aus `restyle.VERBOTEN`). Nur PRUEFEN.
P9  Zwei Saetze      der Nichtwissens-Satz in jeder Wurzel-Bewegung ("weiss ich
                     nicht" oder "steht in keinem Horoskop"); "verwerf"/"verwirf"
                     ausserhalb von Auftakt und erstem Themenkapitel. Nur PRUEFEN.

Selbsttest: `python3 inhaltsprobe.py --selbsttest` laeuft gegen einen KONSTRUIERTEN
Fall ohne reales Geburtsdatum, ohne Uhrzeit, ohne Namen, ohne Staende eines realen
Charts (Datenschutz-Guardrail des Kerns) — einmal fehlerfrei, einmal mit je einem
eingebauten Fehler je Probe P1–P6 und je einem Treffer fuer P8 und P9. Eine Probe,
die ihren Testfehler nicht findet, ist nicht fertig. Der Selbsttest ist Teil des
Moduls und laeuft bei jedem spaeteren Umbau wieder.

Phase 1 (2026-09-16): Bau des Werkzeugs. Der Aufruf in den Modulen (Datenblatt-,
Klartext-, Design-Render-Modul) ist Phase 2 und kommt erst, wenn die Probe in
mindestens einem echten Prueflauf je Schritt ohne Fehlalarm gelaufen ist.
"""

import os
import re
import sys

_HIER = os.path.dirname(os.path.abspath(__file__))
for _p in (_HIER, "/home/claude"):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import build                       # noqa: E402  (Ladeweg: lade("build", "selektor", "inhaltsprobe"))
import selektor                    # noqa: E402

try:                               # restyle traegt die Verbotsliste des Klartext-Moduls
    import restyle as _restyle     # noqa: E402
    VERBOTEN_FACHBEGRIFFE = list(_restyle.VERBOTEN)
except Exception:                  # pragma: no cover — Fallback: Stand restyle.py 2026-09-16
    VERBOTEN_FACHBEGRIFFE = ['°', '′', 'Orb', 'Bogenminute', 'Grad Abstand', 'einseitig',
                             'Nebenaspekt', 'Domizil', 'Exil', 'Exaltation', 'Cazimi',
                             'Apex', 'Dispositor', 'Endherrscher', 'AC-Herrscher',
                             'Chart-Herrscher', 'T-Quadrat']

# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

# Die verbindlichen ###-Wortlaute der Bewegungsfolge, abgeschrieben aus den
# Typmodulen am 2026-09-16:
#   geburt    claude/Projektanweisung_Modul_Geburtshoroskop.md, "Die Bewegungsfolge"
#   ea        claude/Projektanweisung_Erweiterung_EA.md, "Die Bewegungsfolge im
#             EA-Kapitel" — Bewegung 7 heisst im zeitlosen Teil "Wo das im Ganzen
#             steht", im Jetzt-Teil "Der Rahmen dieses Themas"; beide sind gueltig
#   transit   claude/Projektanweisung_Erweiterung_Transit.md, "Die Bewegungsfolge"
#   ultimativ claude/Projektanweisung_Erweiterung_Ultimativ.md, Tabelle "Die
#             Bewegungsfolgen": Teil I und Vertiefung = geburt, Teil II = ea
#             (mit "Wo das im Ganzen steht"), Teil III = transit
# Bewegung 1, 2, 4, 5 und 6 sind ueber alle Typen gleich; 3 und 7 typspezifisch
# (Chris-Entscheidung 2026-09-04, Variante B2). Ein Eintrag darf ein Tupel sein:
# dann ist jeder seiner Wortlaute an dieser Stelle gueltig.
_B1 = "Woran du es merkst"
_B2 = "Was da arbeitet"
_B4 = "Der Teil von dir, der das nicht aufgeben will"
_B5 = "Die zwei Formen und das Dazwischen"
_B6 = "Womit du arbeiten kannst"
WORTLAUTE = {
    "geburt":  (_B1, _B2, "Wie so etwas zur Regel wird", _B4, _B5, _B6, "Wohin das gehört"),
    "ea":      (_B1, _B2, "Woher so etwas kommt", _B4, _B5, _B6,
                ("Wo das im Ganzen steht", "Der Rahmen dieses Themas")),
    "transit": (_B1, _B2, "Warum das alt ist", _B4, _B5, _B6, "Zeit"),
}
# Das Ultimativ traegt alle drei Saetze in einem Dokument; welcher Teil ein Kapitel
# ist, sagt das Kapitel selbst ueber seine dritte und siebte Bewegung.
WORTLAUTE["ultimativ"] = {
    "Teil I":   WORTLAUTE["geburt"],
    "Teil II":  (_B1, _B2, "Woher so etwas kommt", _B4, _B5, _B6, "Wo das im Ganzen steht"),
    "Teil III": WORTLAUTE["transit"],
}
TYPEN = ("geburt", "ea", "transit", "ultimativ")

# Jeder Wortlaut, den irgendein Typ kennt — zum Erkennen, OB ein Kapitel eine
# Bewegungsfolge traegt (erstes Themenkapitel, P9), unabhaengig vom Typ.
def _alle_wortlaute():
    out = set()
    def _add(seq):
        for w in seq:
            if isinstance(w, tuple):
                out.update(w)
            else:
                out.add(w)
    for t, v in WORTLAUTE.items():
        if isinstance(v, dict):
            for seq in v.values():
                _add(seq)
        else:
            _add(v)
    return out
ALLE_WORTLAUTE = _alle_wortlaute()

# Faktornamen, wie sie in Beleg, Signatur und Register geschrieben werden, und ihr
# kanonischer Schluessel (derselbe wie in selektor.parse_chart(): Versalien, ASCII).
# Reihenfolge: laengere Schreibweisen zuerst, damit "Mondknotenachse" nicht als
# "Mond" gelesen wird.
_FAKTOR_SCHREIBWEISEN = (
    ("Mondknotenachse", "MONDKNOTEN"), ("Knotenachse", "MONDKNOTEN"),
    ("Mondknoten", "MONDKNOTEN"), ("Nordknoten", "MONDKNOTEN"),
    ("aufsteigender Knoten", "MONDKNOTEN"), ("aufsteigenden Knoten", "MONDKNOTEN"),
    ("Südknoten", "SUEDKNOTEN"), ("Suedknoten", "SUEDKNOTEN"),
    ("absteigender Knoten", "SUEDKNOTEN"), ("absteigenden Knoten", "SUEDKNOTEN"),
    ("Sonne", "SONNE"), ("Mond", "MOND"), ("Merkur", "MERKUR"), ("Venus", "VENUS"),
    ("Mars", "MARS"), ("Jupiter", "JUPITER"), ("Saturn", "SATURN"),
    ("Uranus", "URANUS"), ("Neptun", "NEPTUN"), ("Pluto", "PLUTO"),
    ("Chiron", "CHIRON"), ("Lilith", "LILITH"), ("Pholus", "PHOLUS"),
    ("Glückspunkt", "GLUECKSPUNKT"), ("Glueckspunkt", "GLUECKSPUNKT"),
    ("Pars Fortunae", "GLUECKSPUNKT"),
    ("Aszendent", "AC"), ("Deszendent", "DC"), ("Medium Coeli", "MC"),
    ("Himmelsmitte", "MC"), ("Imum Coeli", "IC"), ("Immum Coeli", "IC"),
    ("AC", "AC"), ("MC", "MC"), ("DC", "DC"), ("IC", "IC"),
)
_FAKTOR_RE = "(?:%s)" % "|".join(re.escape(s) for s, _ in _FAKTOR_SCHREIBWEISEN)
# Ein Faktorname im Text: mit Wortgrenzen, optional gefolgt von "(AC)"-Klammer.
FAKTOR_RE = re.compile(r"(?<![\wäöüÄÖÜß-])(" + _FAKTOR_RE + r")(?![\wäöüÄÖÜß])"
                       r"(?:\s*\((?:AC|MC|DC|IC)\))?")
_FAKTOR_KANON = {s.casefold(): k for s, k in _FAKTOR_SCHREIBWEISEN}
ACHSEN = ("AC", "MC", "DC", "IC")

def kanon(name):
    """Schreibweise -> kanonischer Schluessel ('Aszendent (AC)' -> 'AC')."""
    n = re.sub(r"\s*\((?:AC|MC|DC|IC)\)\s*$", "", name.strip())
    k = _FAKTOR_KANON.get(n.casefold())
    return k or selektor.norm_faktor(n)

# Anzeigename je Schluessel (fuer Meldungen).
ANZEIGE = {"SONNE": "Sonne", "MOND": "Mond", "MERKUR": "Merkur", "VENUS": "Venus",
           "MARS": "Mars", "JUPITER": "Jupiter", "SATURN": "Saturn", "URANUS": "Uranus",
           "NEPTUN": "Neptun", "PLUTO": "Pluto", "MONDKNOTEN": "Mondknoten",
           "SUEDKNOTEN": "Südknoten", "CHIRON": "Chiron", "LILITH": "Lilith",
           "PHOLUS": "Pholus", "GLUECKSPUNKT": "Glückspunkt",
           "AC": "AC", "MC": "MC", "DC": "DC", "IC": "IC"}

# Aspektarten: Wort, Glyphe, Spiegelbild an einer Achse (AC/DC, MC/IC, Nord-/Suedknoten).
ASPEKTE = (("Anderthalbquadrat", "⚼"), ("Halbquadrat", "∠"), ("Halbsextil", "⚺"),
           ("Konjunktion", "☌"), ("Opposition", "☍"), ("Quadrat", "□"),
           ("Trigon", "△"), ("Sextil", "⚹"), ("Quincunx", "⚻"))
_ASP_WORT = {w: w for w, _ in ASPEKTE}
_ASP_GLYPH = {g: w for w, g in ASPEKTE}
ASPEKT_RE = re.compile(r"(?<![\wäöüÄÖÜß])(%s)(?![\wäöüÄÖÜß])|([%s])"
                       % ("|".join(w for w, _ in ASPEKTE), "".join(g for _, g in ASPEKTE)))
SPIEGEL_ASPEKT = {"Konjunktion": "Opposition", "Opposition": "Konjunktion",
                  "Trigon": "Sextil", "Sextil": "Trigon", "Quadrat": "Quadrat",
                  "Quincunx": "Halbsextil", "Halbsextil": "Quincunx",
                  "Halbquadrat": "Anderthalbquadrat", "Anderthalbquadrat": "Halbquadrat"}
SPIEGEL_FAKTOR = {"AC": "DC", "DC": "AC", "MC": "IC", "IC": "MC",
                  "MONDKNOTEN": "SUEDKNOTEN", "SUEDKNOTEN": "MONDKNOTEN"}

ZEICHEN = ("Widder", "Stier", "Zwillinge", "Krebs", "Löwe", "Loewe", "Jungfrau", "Waage",
           "Skorpion", "Schütze", "Schuetze", "Steinbock", "Wassermann", "Fische")
ZEICHEN_RE = "(?:%s)" % "|".join(ZEICHEN)
ZEICHEN_GLYPHEN = "♈♉♊♋♌♍♎♏♐♑♒♓"
GRAD_RE = r"(\d{1,3})°\s*(\d{1,2})[′']"
# Haus-Schreibweisen: "4. Haus", "4./3. Haus", "Haus 4", "Haus 4/3"
HAUS_RE = (r"(?:(?P<h1>\d{1,2})\.(?:\s*/\s*(?P<h2>\d{1,2})\.)?\s*Haus"
           r"|Haus(?:es)?\s+(?P<h3>\d{1,2})(?:\s*/\s*(?P<h4>\d{1,2}))?)")
# Segment 1 eines Normal-Belegs / Staende-Teil eines Instrument-Segments:
# "Sonne ☉ 10°00′ Widder ♈, 1. Haus" (Form nach Klartext-Modul, Beleg-Format; konstruierte Werte).
STAENDE_RE = re.compile(
    r"^\s*(?P<faktor>" + _FAKTOR_RE + r")(?:\s*\((?:AC|MC|DC|IC)\))?[^\d°]{0,4}?"
    r"(?P<g>\d{1,3})°\s*(?P<m>\d{1,2})[′']\s*(?P<zeichen>" + ZEICHEN_RE + r")"
    r"\s*[" + ZEICHEN_GLYPHEN + r"]?\s*(?:,\s*(?P<haus>" + HAUS_RE + r"))?")

STUFEN = ("voll", "einseitig", "neben", "untergrund")

# ---------------------------------------------------------------------------
# Kleine Helfer
# ---------------------------------------------------------------------------

def _ws(s):
    """Leerraum normalisieren."""
    return re.sub(r"\s+", " ", (s or "")).strip()

def _min(g, m):
    return int(g) * 60 + int(m)

def _orb_txt(minuten):
    return "%d°%02d′" % (minuten // 60, minuten % 60)

def _kicker_nr(kicker):
    m = re.match(r"^Kapitel\s+(\d+)\s*$", kicker or "", re.I)
    return int(m.group(1)) if m else None

def _kurz(s, n=110):
    s = _ws(s)
    return s if len(s) <= n else s[:n - 1] + "…"

def _ist_kicker(ch, *namen):
    k = (ch.get("kicker") or "").strip().casefold()
    return k in tuple(n.casefold() for n in namen)

def _saetze(text):
    return [s for s in re.split(r"(?<=[.!?…])\s+(?=[„\"(A-ZÄÖÜ])", text) if s.strip()]

def _satz_mit(text, pos):
    start = 0
    for s in _saetze(text):
        i = text.find(s, start)
        if i < 0:
            continue
        if i <= pos < i + len(s):
            return s
        start = i + len(s)
    return text

class _Probe:
    """Ergebnis einer Probe."""
    def __init__(self, nr, name):
        self.nr, self.name = nr, name
        self.fehler, self.pruefen, self.hinweise = [], [], []
        self.geprueft = 0
        self.status = None          # OK | FEHLER | PRUEFEN | AUSSAGELOS | UEBERSPRUNGEN
        self.grund = ""
        self.einheit = "Stellen"

    def uebersprungen(self, grund):
        self.status, self.grund = "UEBERSPRUNGEN", grund
        return self

    def aussagelos(self, grund):
        self.status, self.grund = "AUSSAGELOS", grund
        return self

    def abschluss(self):
        if self.status in ("UEBERSPRUNGEN", "AUSSAGELOS"):
            return self
        if self.fehler:
            self.status = "FEHLER"
        elif self.pruefen:
            self.status = "PRUEFEN"
        else:
            self.status = "OK"
        return self

    def als_dict(self):
        return {"nr": self.nr, "name": self.name, "status": self.status,
                "geprueft": self.geprueft, "einheit": self.einheit,
                "fehler": list(self.fehler), "pruefen": list(self.pruefen),
                "hinweise": list(self.hinweise), "grund": self.grund}

# ---------------------------------------------------------------------------
# Datenblatt lesen
# ---------------------------------------------------------------------------

_AH_NAME = build._AH_NAME            # '(?:AC|MC|DC|IC|[A-ZÄÖÜ][a-zäöüß]+)'

def _tabellen_lesen(txt):
    """Alle Aspektzeilen der vier Tabellen als Liste von dicts.

    Zeilenregex woertlich aus `build._ressourcen_zeilen()` (sechsspaltige Form des
    Datenblatt-Moduls, Spalte 6 "zugleich" seit 15.09.2026 optional):
        | Faktor | ☌ Konjunktion | Faktor | 0°41′ | konj | … |
    — dort nur mit den harmonischen Glyphen (`_HARMONISCH`); hier mit ALLEN
    Aspektglyphen und dem Aspektwort als Alternative, dazu die Spalten 5 und 6.
    Die Ueberschriften und der Ueberschriften-Schnitt (`\\n#{2,3} `) stammen aus
    `build.aspekt_heimat()`; die Stufenzuordnung aus `build._STAERKE_KOPF`.
    Achsen-Spiegelzeilen aus Spalte 6 ("Opposition DC") werden als eigene Eintraege
    mit `spiegel=True` gefuehrt.
    """
    glyphen = "".join(g for _, g in ASPEKTE)
    zeile = re.compile(
        r"\|\s*(%s)\s*\|\s*([%s])?\s*([A-Za-zÄÖÜäöüß]*)\s*\|\s*(%s)\s*\|"
        r"\s*(\d{1,3}°\d{2}′)\s*\|(?:\s*([^|]*)\|)?(?:\s*([^|]*)\|)?"
        % (_AH_NAME, glyphen, _AH_NAME))
    koepfe = [(k, s) for k, s in build._STAERKE_KOPF] + [("### Hauptaspekte", "voll"),
                                                          ("### Untergrund-Aspekte", "untergrund")]
    out = []
    for kopf, stufe in koepfe:
        if kopf not in txt:
            continue
        teil = txt.split(kopf, 1)[1]
        schnitt = re.search(r"\n#{2,3} ", teil)
        if schnitt:
            teil = teil[:schnitt.start()]
        for z in teil.splitlines():
            m = zeile.match(z)
            if not m:
                continue
            a, g, w, b, orb = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            if a in ("Aspekt", "Faktor", "Punkt"):
                continue
            art = _ASP_WORT.get(w) if w else None
            if art is None and g:
                art = _ASP_GLYPH.get(g)
            if art is None:
                continue
            gr, mi = orb.split("°")
            mins = _min(gr, mi.rstrip("′"))
            eintrag = {"a": kanon(a), "b": kanon(b), "art": art, "orb": mins,
                       "orb_txt": orb, "stufe": stufe, "zeile": _ws(z), "spiegel": False}
            out.append(eintrag)
            zugleich = (m.group(7) or "").strip()
            mz = re.match(r"^(%s)\s+(%s)$" % ("|".join(w for w, _ in ASPEKTE), _FAKTOR_RE),
                          zugleich)
            if mz:
                out.append({"a": eintrag["a"], "b": kanon(mz.group(2)), "art": mz.group(1),
                            "orb": mins, "orb_txt": orb, "stufe": stufe,
                            "zeile": _ws(z), "spiegel": True})
    return out

def _staende_lesen(txt):
    """Staendetabelle (`## Staende`): Faktor -> (Minuten, Zeichen). None, wenn nicht
    sicher lesbar (dann wird die Gradminuten-Probe uebersprungen und gesagt)."""
    m = re.search(r"\n## St[äa]nde", txt)
    if not m:
        return None
    teil = txt[m.end():]
    schnitt = re.search(r"\n## ", teil)
    if schnitt:
        teil = teil[:schnitt.start()]
    zeile = re.compile(r"^\|\s*(%s)\s*\|\s*(\d{1,3})°(\d{1,2})[′']\s*\|\s*(%s)"
                       % (_AH_NAME, ZEICHEN_RE))
    out = {}
    for z in teil.splitlines():
        mm = zeile.match(z)
        if mm:
            out[kanon(mm.group(1))] = (_min(mm.group(2), mm.group(3)),
                                       selektor.norm(mm.group(4)))
    return out or None

def _themenliste_lesen(txt):
    """THEMA-Zeilen als Liste von dicts (nr, titel, fuehrt, fuehrt_roh, form,
    leitachse, roh). Einstieg, Schluss und Zerlegung woertlich aus
    `build.aspekt_heimat()` (Einstiegsmarke seit 2026-09-16 `THEMA \\d+ \\|`)."""
    _erste = re.search(r"THEMA \d+ \|", txt)
    if not _erste:
        return []
    tl = "\n" + txt[_erste.start():]
    for schluss in ("RECHENSCHAFT", "REGISTER:", "GESTRICHEN:"):
        tl = tl.split(schluss)[0]
    out = []
    nummern = re.findall(r"\nTHEMA (\d+) \|", tl)
    for nr, blk in zip(nummern, re.split(r"\nTHEMA \d+ \|", tl)[1:]):
        def feld(name):
            m = re.search(r"(?:^|\|)\s*%s=(.*?)(?=\s*\|\s*[a-z_]+=|\s*$)" % name, blk, re.S)
            return _ws(m.group(1)) if m else None
        fuehrt_roh = feld("fuehrt") or ""
        mf = FAKTOR_RE.match(fuehrt_roh)
        out.append({"nr": int(nr), "titel": feld("titel"), "fuehrt_roh": fuehrt_roh,
                    "fuehrt": kanon(mf.group(1)) if mf else None,
                    "form": (feld("form") or "voll").casefold(),
                    "leitachse": (feld("leitachse") or "").casefold().startswith("ja"),
                    "teil": (feld("teil") or "").casefold(), "roh": _ws(blk)})
    return out

# ---------------------------------------------------------------------------
# Beleg zerlegen
# ---------------------------------------------------------------------------

def _segmente(beleg):
    return [s.strip() for s in (beleg or "").split(" · ") if s.strip()]

def _staende_segment(seg):
    """-> dict(faktor, minuten, zeichen, haus1, haus2) oder None."""
    m = STAENDE_RE.match(seg)
    if not m:
        return None
    h1 = m.group("h1") or m.group("h3")
    h2 = m.group("h2") or m.group("h4")
    return {"faktor": kanon(m.group("faktor")), "minuten": _min(m.group("g"), m.group("m")),
            "zeichen": selektor.norm(m.group("zeichen")),
            "haus1": h1, "haus2": h2, "roh": seg}

def _aspekt_eintraege(text, faktor_a=None):
    """Zerlegt einen Text in Aspektangaben.

    Normal-Segment (faktor_a=None): Faktor A ist der erste Faktorname des Segments,
    dahinter genau eine Aspektart, dann Faktor B und "Orb N°NN′".
    Instrument-Segment (faktor_a gesetzt): kommagetrennte Angaben hinter den
    Staenden, jede "Aspektart Faktor Orb" — Faktor A ist die Funktion des Segments.
    Rueckgabe: Liste von dicts (a, art, b, orb, orb_sicher, stufe, roh, mehrfach).
    """
    out = []
    # Aspektangaben im Text; Wort und unmittelbar folgende Glyphe ("Trigon △") sind
    # EINE Angabe, nicht zwei.
    starts = []
    for t in ASPEKT_RE.finditer(text):
        art = t.group(1) or _ASP_GLYPH.get(t.group(2))
        if starts and t.group(2) and t.start() - starts[-1][1] <= 3 and starts[-1][2] == art:
            continue
        starts.append((t.start(), t.end(), art, t))
    if not starts:
        return out
    if faktor_a is None:
        # Normalformat: genau EINE Aspektbeziehung je Segment; Faktor A steht vor
        # der Aspektart (mit oder ohne eigene Staende dazwischen).
        s, e, art, t = starts[0]
        ma = FAKTOR_RE.search(text[:s])
        a = kanon(ma.group(1)) if ma else None
        out.append(_eintrag(a, t, text[s:], len(starts) > 1))
    else:
        # Instrument-Format: Angabe fuer Angabe, jede beginnt mit der Aspektart;
        # Faktor A ist die Funktion des Segments.
        for i, (s, e, art, t) in enumerate(starts):
            ende = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            out.append(_eintrag(faktor_a, t, text[s:ende], False))
    return out

def _eintrag(a, t, rest, mehrfach):
    art = t.group(1) or _ASP_GLYPH.get(t.group(2))
    nach = rest[t.end() - t.start():]
    # Glyphe hinter dem Wort ueberspringen
    nach = re.sub(r"^\s*[%s]" % "".join(g for _, g in ASPEKTE), "", nach)
    mb = FAKTOR_RE.search(nach)
    b = kanon(mb.group(1)) if mb else None
    tail = nach[mb.end():] if mb else nach
    mo = re.search(r"\bOrb\s*" + GRAD_RE, tail)
    orb, sicher = None, True
    if mo:
        orb = _min(mo.group(1), mo.group(2))
    else:
        grade = re.findall(GRAD_RE, tail)
        hat_zeichen = re.search(r"(?<![\wäöüß])" + ZEICHEN_RE + r"(?![\wäöüß])", tail)
        if grade and not hat_zeichen and len(grade) == 1:
            orb = _min(*grade[-1])
        elif grade:
            orb, sicher = _min(*grade[-1]), False
    stufe = None
    ms = re.search(r"(?<![\wäöüß])(voll|einseitig|Nebenaspekt|neben)(?![\wäöüß])", rest)
    if ms:
        stufe = {"Nebenaspekt": "neben"}.get(ms.group(1), ms.group(1))
    return {"a": a, "art": art, "b": b, "orb": orb, "orb_sicher": sicher,
            "stufe": stufe, "roh": _ws(rest), "mehrfach": mehrfach}

def _beleg_form(ch, typ):
    """'struktur' | 'instrument' | 'zugang' | 'normal' | None (kein Beleg)."""
    if not ch.get("beleg"):
        return None
    if _ist_kicker(ch, "Instrument"):
        return "instrument"
    if _ist_kicker(ch, "Zugang"):
        return "zugang"
    segs = _segmente(ch["beleg"])
    if typ in ("geburt", "ultimativ") and _kicker_nr(ch["kicker"]) == 1:
        return "struktur"
    if segs and _staende_segment(segs[0]) is None:
        # Segment 1 sind keine Staende: Struktur-Format, wenn kein Aspekt darin
        # steht oder es das erste nummerierte Kapitel ist; sonst ein Normal-Beleg
        # mit kaputtem Segment 1, den P2 meldet.
        if not ASPEKT_RE.search(ch["beleg"]) or _kicker_nr(ch["kicker"]) == 1:
            return "struktur"
    return "normal"

# ---------------------------------------------------------------------------
# Typ und Kapitelklassen
# ---------------------------------------------------------------------------

def typ_aus_h1(doctype):
    d = (doctype or "").casefold()
    if "ultimativ" in d:
        return "ultimativ"
    if "transit" in d or "jahresvorschau" in d:
        return "transit"
    if "evolution" in d or "seelen" in d or d.startswith("ea") or " ea" in d:
        return "ea"
    if "geburtshoroskop" in d or "geburt" in d:
        return "geburt"
    return None

def _subheads(ch):
    return [_ws(b["text"]) for b in ch["blocks"] if b.get("type") == "subhead"]

def _hat_bewegungen(ch):
    return any(s in ALLE_WORTLAUTE for s in _subheads(ch))

def _themenkapitel(chapters, typ):
    """Kapitel mit Bewegungsfolge, in Dokumentreihenfolge.
    geburt: Kicker `Kapitel n` mit n >= 2, dazu `Zugang`. Andere Typen: jedes
    Kapitel, das einen bekannten Bewegungs-Wortlaut traegt, plus jedes `Kapitel n`."""
    out = []
    for ch in chapters:
        n = _kicker_nr(ch["kicker"])
        if typ == "geburt":
            if (n is not None and n >= 2) or _ist_kicker(ch, "Zugang"):
                out.append(ch)
        else:
            if n is not None or _ist_kicker(ch, "Zugang") or _hat_bewegungen(ch):
                out.append(ch)
    return out

def _bezeichnung(ch):
    return "%s · %s" % (ch.get("kicker") or "—", _kurz(ch.get("title"), 50))

# ---------------------------------------------------------------------------
# Die Proben
# ---------------------------------------------------------------------------

def _p1_beleg_aspekte(chapters, typ, tabelle):
    p = _Probe("P1", "Beleg-Aspekte")
    p.einheit = "Segmente"
    if not tabelle:
        return p.aussagelos("keine Aspektzeile in den vier Aspekttabellen gefunden")
    index = {}
    for e in tabelle:
        index.setdefault(frozenset([e["a"], e["b"]]), []).append(e)

    def naechste(a, b, art):
        kand = [e for e in tabelle if a in (e["a"], e["b"]) or b in (e["a"], e["b"])]
        if not kand:
            return "keine Tabellenzeile mit %s oder %s" % (ANZEIGE.get(a, a), ANZEIGE.get(b, b))
        kand.sort(key=lambda e: (-(a in (e["a"], e["b"]) and b in (e["a"], e["b"])),
                                 e["art"] != art, e["orb"]))
        e = kand[0]
        return "nächste Zeile: %s%s" % (e["zeile"], " (Spiegelzeile)" if e["spiegel"] else "")

    def pruefe_eintrag(ort, e):
        p.geprueft += 1
        stelle = "%s: „%s“" % (ort, _kurz(e["roh"], 90))
        if e["mehrfach"]:
            p.pruefen.append("%s — mehr als eine Aspektangabe im Segment (Beleg-Format: "
                             "genau EINE je Segment); geprüft wurde die erste" % stelle)
        if not e["a"] or not e["b"] or not e["art"]:
            p.pruefen.append("%s — nicht als „Faktor Aspektart Faktor Orb“ lesbar" % stelle)
            return
        a, b, art = e["a"], e["b"], e["art"]
        # Suedknoten steht nicht in der Aspektrechnung: Spiegel des Nordknoten-Aspekts
        spiegel_hinweis = None
        if "SUEDKNOTEN" in (a, b):
            a2 = "MONDKNOTEN" if a == "SUEDKNOTEN" else a
            b2 = "MONDKNOTEN" if b == "SUEDKNOTEN" else b
            art2 = SPIEGEL_ASPEKT.get(art, art)
            treffer = [t for t in index.get(frozenset([a2, b2]), []) if t["art"] == art2]
            if treffer:
                p.pruefen.append("%s — Südknoten-Aspekt, in der Tabelle steht nur der "
                                 "Spiegel %s (der Südknoten geht nicht in die "
                                 "Aspektrechnung)" % (stelle, treffer[0]["zeile"]))
                return
            p.fehler.append("%s — Paar nicht in den Aspekttabellen, auch nicht als "
                            "Spiegel des Nordknotens; %s" % (stelle, naechste(a, b, art)))
            return
        zeilen = index.get(frozenset([a, b]), [])
        gleiche_art = [t for t in zeilen if t["art"] == art]
        if not zeilen:
            # nur ueber die Achsen-Spiegelung ableitbar?
            for x, y in ((a, b), (b, a)):
                if y in SPIEGEL_FAKTOR and y in ACHSEN:
                    alt = index.get(frozenset([x, SPIEGEL_FAKTOR[y]]), [])
                    alt = [t for t in alt if t["art"] == SPIEGEL_ASPEKT.get(art)]
                    if alt:
                        spiegel_hinweis = alt[0]
            if spiegel_hinweis:
                p.pruefen.append("%s — keine Tabellenzeile; nur als Achsen-Spiegel von "
                                 "%s ableitbar (Spalte „zugleich“ fehlt)"
                                 % (stelle, spiegel_hinweis["zeile"]))
                return
            p.fehler.append("%s — Paar %s/%s nicht in den Aspekttabellen; %s"
                            % (stelle, ANZEIGE.get(a, a), ANZEIGE.get(b, b), naechste(a, b, art)))
            return
        if not gleiche_art:
            p.fehler.append("%s — Aspektart %s stimmt nicht; Tabelle: %s"
                            % (stelle, art, "; ".join(t["zeile"] for t in zeilen)))
            return
        if e["orb"] is None:
            p.pruefen.append("%s — kein Orb im Segment; Tabelle: %s" % (stelle, gleiche_art[0]["zeile"]))
            return
        passend = [t for t in gleiche_art if abs(t["orb"] - e["orb"]) <= 1]
        if not passend:
            if not e["orb_sicher"]:
                p.pruefen.append("%s — Orb nicht eindeutig lesbar (Position oder Orb?); "
                                 "Tabelle: %s" % (stelle, gleiche_art[0]["zeile"]))
            else:
                p.fehler.append("%s — Orb %s weicht ab; Tabelle: %s"
                                % (stelle, _orb_txt(e["orb"]), gleiche_art[0]["zeile"]))
            return
        if not e["orb_sicher"]:
            p.hinweise.append("%s — Orb ohne Schlüsselwort gelesen, stimmt mit der Tabelle" % stelle)
        if e["stufe"] and passend[0]["stufe"] not in (e["stufe"],):
            p.pruefen.append("%s — Beleg nennt Stufe „%s“, Tabelle führt „%s“"
                             % (stelle, e["stufe"], passend[0]["stufe"]))

    for ch in chapters:
        form = _beleg_form(ch, typ)
        if form is None:
            continue
        bez = _bezeichnung(ch)
        segs = _segmente(ch["beleg"])
        if form == "struktur":
            p.hinweise.append("Getriebe-Beleg (Struktur-Format) übersprungen: %s" % bez)
            continue
        if form == "normal":
            for i, seg in enumerate(segs[1:], start=2):
                eintr = _aspekt_eintraege(seg)
                if not eintr:
                    p.pruefen.append("%s, Segment %d: „%s“ — kein Aspekt im Segment (Normalformat: "
                                     "jedes Segment ab dem zweiten genau EINE Aspektbeziehung)"
                                     % (bez, i, _kurz(seg, 90)))
                    continue
                for e in eintr:
                    pruefe_eintrag("%s, Segment %d" % (bez, i), e)
        elif form == "instrument":
            for i, seg in enumerate(segs, start=1):
                st = _staende_segment(seg)
                if st is None:
                    ma = FAKTOR_RE.match(seg)
                    a = kanon(ma.group(1)) if ma else None
                else:
                    a = st["faktor"]
                teile = seg.split(" — ", 1)
                rest = teile[1] if len(teile) > 1 else seg
                for e in _aspekt_eintraege(rest, faktor_a=a):
                    pruefe_eintrag("%s, Segment %d (%s)" % (bez, i, ANZEIGE.get(a, a) if a else "?"), e)
        elif form == "zugang":
            muster = re.compile(r"(" + _FAKTOR_RE + r")(?:\s*\((?:AC|MC|DC|IC)\))?\s*[☉☽☿♀♂♃♄♅♆♇☊☋⚷⚸⊗]?\s*"
                                r"(%s)\s*[%s]?\s*(%s)(?:\s*\((?:AC|MC|DC|IC)\))?[^,·]*?(?:Orb\s*)?"
                                r"(\d{1,3})°\s*(\d{1,2})[′']"
                                % ("|".join(w for w, _ in ASPEKTE), "".join(g for _, g in ASPEKTE),
                                   _FAKTOR_RE))
            for i, seg in enumerate(segs, start=1):
                for m in muster.finditer(seg):
                    e = {"a": kanon(m.group(1)), "art": m.group(2), "b": kanon(m.group(3)),
                         "orb": _min(m.group(4), m.group(5)), "orb_sicher": True,
                         "stufe": None, "roh": m.group(0), "mehrfach": False}
                    pruefe_eintrag("%s, Segment %d" % (bez, i), e)
    if p.geprueft == 0:
        return p.aussagelos("kein Aspekt-Segment in einem Normal-, Instrument- oder Zugang-Beleg gefunden")
    return p.abschluss()

def _erwartete_haeuser(f):
    """(fuehrendes Haus, Nebenhaus) aus einer FAKTOR-Zeile — Schwellenlage (<= 2°)
    fuehrt das Nebenhaus, Grenzlage (2°–5°) das rechnerische Haus (Datenblatt-Modul)."""
    h, nh, ab = f.get("haus"), f.get("nebenhaus"), f.get("abstand")
    if not nh:
        return h, None
    try:
        a = float(ab) if ab is not None else 99.0
    except ValueError:
        a = 99.0
    return (nh, h) if a <= selektor.SCHWELLE_ORB else (h, nh)

def _p2_beleg_staende(chapters, typ, chart, staende):
    p = _Probe("P2", "Beleg-Stände")
    p.einheit = "Stände-Segmente"
    fak = {f["name"]: f for f in chart.get("faktoren", [])}
    achsen = chart.get("achsen", {})
    if staende is None:
        p.hinweise.append("Ständetabelle nicht sicher lesbar — Gradminuten übersprungen")

    def pruefe(ort, st):
        p.geprueft += 1
        f = st["faktor"]
        stelle = "%s: „%s“" % (ort, _kurz(st["roh"], 80))
        if f in ACHSEN:
            soll = achsen.get(f)
            if soll is None:
                p.pruefen.append("%s — Achse %s hat keine ACHSE-Zeile im @@SELEKTOR-Block" % (stelle, f))
            elif soll != st["zeichen"]:
                p.fehler.append("%s — Zeichen %s, @@SELEKTOR sagt %s" % (stelle, st["zeichen"], soll))
        else:
            fz = fak.get(f)
            if fz is None:
                p.pruefen.append("%s — %s hat keine FAKTOR-Zeile im @@SELEKTOR-Block"
                                 % (stelle, ANZEIGE.get(f, f)))
            else:
                if fz.get("zeichen") and fz["zeichen"] != st["zeichen"]:
                    p.fehler.append("%s — Zeichen %s, @@SELEKTOR sagt %s"
                                    % (stelle, st["zeichen"], fz["zeichen"]))
                soll1, soll2 = _erwartete_haeuser(fz)
                if st["haus1"] is None:
                    if soll1:
                        p.pruefen.append("%s — kein Haus im Segment; @@SELEKTOR: Haus %s%s"
                                         % (stelle, soll1, "/" + soll2 if soll2 else ""))
                else:
                    if soll1 and st["haus1"] != soll1:
                        p.fehler.append("%s — führendes Haus %s, @@SELEKTOR verlangt %s%s vorn"
                                        % (stelle, st["haus1"], soll1,
                                           " (Grenzlage, Nebenhaus %s)" % soll2 if soll2 else ""))
                    elif st["haus2"] and not soll2:
                        p.fehler.append("%s — Beleg nennt ein Nebenhaus %s, @@SELEKTOR kennt keine "
                                        "Grenzlage" % (stelle, st["haus2"]))
                    elif st["haus2"] and soll2 and st["haus2"] != soll2:
                        p.fehler.append("%s — Nebenhaus %s, @@SELEKTOR sagt %s"
                                        % (stelle, st["haus2"], soll2))
        if staende is not None:
            tab = staende.get(f)
            if tab is None:
                p.hinweise.append("%s — nicht in der Ständetabelle, Gradminute nicht geprüft" % stelle)
            else:
                if abs(tab[0] - st["minuten"]) > 1:
                    p.fehler.append("%s — %s, Ständetabelle sagt %s"
                                    % (stelle, _orb_txt(st["minuten"]), _orb_txt(tab[0])))
                if tab[1] != st["zeichen"]:
                    p.fehler.append("%s — Zeichen %s, Ständetabelle sagt %s"
                                    % (stelle, st["zeichen"], tab[1]))

    for ch in chapters:
        form = _beleg_form(ch, typ)
        if form not in ("normal", "instrument"):
            continue
        bez = _bezeichnung(ch)
        segs = _segmente(ch["beleg"])
        if form == "normal":
            st = _staende_segment(segs[0]) if segs else None
            if st is None:
                p.fehler.append("%s, Segment 1: „%s“ — nicht als Stände des führenden Faktors lesbar "
                                "(Faktor Gradminute Zeichen, Haus)" % (bez, _kurz(segs[0] if segs else "", 80)))
                continue
            pruefe("%s, Segment 1" % bez, st)
        else:
            for i, seg in enumerate(segs, start=1):
                st = _staende_segment(seg)
                if st is None:
                    p.fehler.append("%s, Segment %d: „%s“ — Instrument-Segment nicht als Stände lesbar"
                                    % (bez, i, _kurz(seg, 80)))
                    continue
                pruefe("%s, Segment %d" % (bez, i), st)
    if p.geprueft == 0 and not p.fehler:
        return p.aussagelos("kein Stände-Segment gefunden")
    return p.abschluss()

def _fuehrer_im_beleg(ch):
    segs = _segmente(ch.get("beleg"))
    st = _staende_segment(segs[0]) if segs else None
    if st:
        return st["faktor"]
    if segs:
        m = FAKTOR_RE.match(segs[0])
        return kanon(m.group(1)) if m else None
    return None

def _name_in_text(schluessel, text):
    """Steht der Faktor (in einer seiner Schreibweisen) im Text?"""
    for s, k in _FAKTOR_SCHREIBWEISEN:
        if k == schluessel and re.search(r"(?<![\wäöüÄÖÜß-])" + re.escape(s) + r"(?![\wäöüÄÖÜß])", text or ""):
            return True
    # "Knoten" allein gilt fuer den Mondknoten
    if schluessel == "MONDKNOTEN" and re.search(r"(?<![\wäöüß])Knoten(?:achse)?(?![\wäöüß])", text or ""):
        return True
    return False

def _p3_p7_kapitel_themen(chapters, typ, themen):
    p3 = _Probe("P3", "Kapitel gegen Themenliste")
    p7 = _Probe("P7", "Signatur nennt den Führer")
    p3.einheit = p7.einheit = "Kapitel"
    if typ != "geburt":
        grund = ("Kapitel-Skelett des Typs %s ist in dieser Probe nicht hinterlegt (nur Geburtshoroskop)"
                 % (typ or "unbekannt"))
        return p3.uebersprungen(grund), p7.uebersprungen(grund), {}
    if not themen:
        return p3.aussagelos("keine THEMA-Zeile in der chart_data gefunden"), \
               p7.aussagelos("keine THEMA-Zeile in der chart_data gefunden"), {}
    kap = [ch for ch in chapters if (_kicker_nr(ch["kicker"]) or 0) >= 2]
    zuordnung = {}
    if len(kap) != len(themen):
        p3.fehler.append("Zahl: %d nummerierte Themenkapitel (Kapitel 2 ff.), aber %d THEMA-Zeilen"
                         % (len(kap), len(themen)))
    for i, (ch, th) in enumerate(zip(kap, themen)):
        p3.geprueft += 1
        p7.geprueft += 1
        zuordnung[id(ch)] = th
        bez = _bezeichnung(ch)
        soll = th["fuehrt"]
        if soll is None:
            p3.fehler.append("THEMA %d: fuehrt= trägt keinen lesbaren Faktor („%s“)"
                             % (th["nr"], _kurz(th["fuehrt_roh"], 60)))
            continue
        ist = _fuehrer_im_beleg(ch)
        if ist != soll:
            p3.fehler.append("%s ↔ THEMA %d: Beleg-Segment 1 führt %s, Themenliste sagt %s"
                             % (bez, th["nr"], ANZEIGE.get(ist, ist) if ist else "—", ANZEIGE.get(soll, soll)))
        if not _name_in_text(soll, ch.get("signatur")):
            p7.fehler.append("%s ↔ THEMA %d: Signatur nennt %s nicht („%s“)"
                             % (bez, th["nr"], ANZEIGE.get(soll, soll), _kurz(ch.get("signatur"), 70)))
        if th["titel"] and _ws(th["titel"]).casefold() != _ws(ch["title"]).casefold():
            p3.pruefen.append("%s ↔ THEMA %d: Titel weicht ab — Themenliste: „%s“"
                              % (bez, th["nr"], _kurz(th["titel"], 70)))
    for ch in kap[len(themen):]:
        p3.fehler.append("%s: Kapitel ohne THEMA-Zeile" % _bezeichnung(ch))
    for th in themen[len(kap):]:
        p3.fehler.append("THEMA %d „%s“: Thema ohne Kapitel" % (th["nr"], _kurz(th["titel"], 60)))
    return p3.abschluss(), p7.abschluss(), zuordnung

def _folge_variante(wortlaute, kurz):
    """Sollfolge: volle sieben oder Kurzform ohne Bewegung 3 und 4."""
    return [w for i, w in enumerate(wortlaute) if not (kurz and i in (2, 3))]

def _passt(subs, soll):
    if len(subs) != len(soll):
        return False
    for s, w in zip(subs, soll):
        if isinstance(w, tuple):
            if s not in w:
                return False
        elif s != w:
            return False
    return True

def _p4_bewegungsfolge(chapters, typ, zuordnung):
    p = _Probe("P4", "Bewegungsfolge")
    p.einheit = "Kapitel"
    if typ not in WORTLAUTE:
        return p.uebersprungen("Typ %s hat keine Wortlaute in WORTLAUTE" % (typ or "unbekannt"))
    saetze = WORTLAUTE[typ] if isinstance(WORTLAUTE[typ], dict) else {typ: WORTLAUTE[typ]}
    kapitel = _themenkapitel(chapters, typ)
    if not kapitel:
        return p.aussagelos("kein Themenkapitel mit Bewegungsfolge gefunden")
    for ch in kapitel:
        bez = _bezeichnung(ch)
        subs = _subheads(ch)
        th = zuordnung.get(id(ch))
        form = th["form"] if th else None
        zugang = _ist_kicker(ch, "Zugang")
        if not subs:
            if typ == "geburt":
                p.fehler.append("%s: keine ###-Bewegung — Themenkapitel ohne Bewegungsfolge" % bez)
            else:
                p.pruefen.append("%s: kein ###-Zwischentitel — Getriebe-Kapitel oder fehlende Folge?" % bez)
            continue
        p.geprueft += 1
        # zulaessige Sollfolgen je form=
        varianten = []
        for teil, wl in saetze.items():
            voll = _folge_variante(wl, False)
            kurz = _folge_variante(wl, True)
            ohne_wurzel = [w for i, w in enumerate(wl) if i != 2]
            if zugang:
                varianten += [(teil, "Zugang ohne Wurzel und Widerstand", kurz),
                              (teil, "Zugang ohne Wurzel", ohne_wurzel)]
            elif form == "kurz":
                varianten.append((teil, "form=kurz", kurz))
            elif form == "ressource":
                varianten += [(teil, "form=ressource (Kurzform)", kurz),
                              (teil, "form=ressource (volle Folge)", voll)]
            elif form == "voll":
                varianten.append((teil, "form=voll", voll))
            else:   # form unbekannt (keine Zuordnung zur Themenliste)
                varianten += [(teil, "volle Folge", voll), (teil, "Kurzform", kurz)]
        if any(_passt(subs, v[2]) for v in varianten):
            continue
        # Befund formulieren: fehlend / ueberzaehlig / vertauscht, gegen die
        # naechstliegende Sollfolge (groesste Schnittmenge mit den Zwischentiteln)
        def _flach(folge):
            return set(x for w in folge for x in (w if isinstance(w, tuple) else (w,)))
        bekannte = set()                       # Wortlaute DIESES Typs
        for wl in saetze.values():
            bekannte |= _flach(wl)
        fremd = [s for s in subs if s not in ALLE_WORTLAUTE]
        anderer_typ = [s for s in subs if s not in bekannte and s in ALLE_WORTLAUTE]
        best = max(varianten, key=lambda v: len(set(subs) & _flach(v[2])))
        soll_set = _flach(best[2])
        fehlend = [w[0] if isinstance(w, tuple) else w for w in best[2]
                   if not any((s in w) if isinstance(w, tuple) else (s == w) for s in subs)]
        ueberz = [s for s in subs if s not in soll_set and s in bekannte]
        teile = []
        if fremd:
            teile.append("unbekannter Zwischentitel: " + ", ".join("„%s“" % s for s in fremd))
        if anderer_typ:
            teile.append("Wortlaut eines anderen Typs: " + ", ".join("„%s“" % s for s in anderer_typ))
        if fehlend:
            teile.append("fehlt: " + ", ".join("„%s“" % s for s in fehlend))
        if ueberz:
            teile.append("überzählig: " + ", ".join("„%s“" % s for s in ueberz))
        if not teile:
            teile.append("Reihenfolge vertauscht: " + " → ".join(subs))
        p.fehler.append("%s (%s): %s" % (bez, best[1] + ("" if len(saetze) == 1 else ", " + best[0]),
                                          "; ".join(teile)))
    return p.abschluss()

def _register_eintraege(ch):
    """Die Zeilen des Rechenschaftskapitels als Liste von Texten (ohne Listennummer)."""
    out = []
    for b in ch["blocks"]:
        if b.get("type") == "subhead":
            continue
        t = b["text"]
        if b.get("type") == "li":
            out.append(_ws(t))
            continue
        # nummerierte Liste, die parse_analyse als einen Absatz gelesen hat, und
        # Zeilen ohne Nummer: an Zeilenanfang und an "n. " trennen
        for stueck in re.split(r"\n|(?:(?<=\s)|^)\d{1,2}\.\s+(?=[A-ZÄÖÜ])", t):
            if stueck.strip():
                out.append(_ws(stueck))
    return out

def _p5_rechenschaft(chapters, chart, themen):
    p = _Probe("P5", "Rechenschafts-Register")
    p.einheit = "Faktoren"
    rech = [ch for ch in chapters if _ist_kicker(ch, "Rechenschaft")]
    if not rech:
        return p.uebersprungen("kein Kapitel mit Kicker „Rechenschaft“ (der Transit führt sein "
                               "Register in der chart_data)")
    if not chart.get("faktoren"):
        return p.aussagelos("keine FAKTOR-Zeile im @@SELEKTOR-Block")
    if not themen:
        return p.aussagelos("keine THEMA-Zeile in der chart_data — Führer nicht bestimmbar")
    fuehrer = {t["fuehrt"] for t in themen if t["fuehrt"]}
    eintraege = _register_eintraege(rech[0])
    if not eintraege:
        return p.aussagelos("Rechenschaftskapitel ohne Zeilen")

    def hat_zeile(schluessel):
        # Die Zeile beginnt mit dem Namen; ein Artikel davor ("Der Glückspunkt, …")
        # wird geduldet, mehr nicht.
        for e in eintraege:
            m = FAKTOR_RE.match(re.sub(r"^(?:[Dd](?:er|ie|as))\s+", "", e))
            if m and kanon(m.group(1)) == schluessel:
                return e
        return None

    for f in chart["faktoren"]:
        name = f["name"]
        if name in ACHSEN:
            continue
        p.geprueft += 1
        z = hat_zeile(name)
        if name in fuehrer:
            if z:
                p.pruefen.append("%s führt ein Thema und hat trotzdem eine Registerzeile: „%s“"
                                 % (ANZEIGE.get(name, name), _kurz(z, 80)))
        elif not z:
            p.fehler.append("%s führt kein Thema und hat keine Zeile im Rechenschaftskapitel, "
                            "die mit seinem Namen beginnt" % ANZEIGE.get(name, name))
    return p.abschluss()

def _p6_leitsatz(chapters, chart_data_pfad, themen):
    p = _Probe("P6", "Leitsatz und Leitachse")
    p.einheit = "Prüfungen"
    try:
        deck = build.lies_deckblatt(chart_data_pfad)
        leitsatz = _ws(deck.get("LEITSATZ"))
    except Exception as e:      # DeckblattError, fehlender Block
        leitsatz = None
        p.fehler.append("@@DECKBLATT nicht lesbar: %s" % _kurz(str(e), 120))
    schluss = [ch for ch in chapters if _ist_kicker(ch, "Schlusswort")]
    if leitsatz:
        p.geprueft += 1
        if not schluss:
            p.fehler.append("kein Kapitel mit Kicker „Schlusswort“ — Leitsatz nicht verankert")
        else:
            text = _ws(" ".join(b["text"] for b in schluss[0]["blocks"] if b.get("type") != "subhead"))
            def woerter(s):
                return [w for w in re.findall(r"[\wäöüÄÖÜß]+", s.casefold())]
            if leitsatz.casefold() in text.casefold():
                pass
            else:
                lw, tw = woerter(leitsatz), woerter(text)
                # laengste gemeinsame Teilfolge (in Reihenfolge), vier Fuenftel noetig
                i = j = 0
                # gierig ist hier zu schwach; echte LCS ueber DP
                n, m = len(lw), len(tw)
                prev = [0] * (m + 1)
                for a in lw:
                    cur = [0] * (m + 1)
                    for k in range(1, m + 1):
                        cur[k] = prev[k - 1] + 1 if a == tw[k - 1] else max(prev[k], cur[k - 1])
                    prev = cur
                anteil = prev[m] / float(n) if n else 0.0
                if anteil >= 0.8:
                    p.hinweise.append("Leitsatz im Schlusswort verankert (Wortfolge %d %%)" % round(anteil * 100))
                else:
                    p.fehler.append("Leitsatz nicht im Schlusswort: „%s“ (Wortfolge nur %d %%)"
                                    % (_kurz(leitsatz, 90), round(anteil * 100)))
    if not themen:
        p.pruefen.append("keine THEMA-Zeile — leitachse=ja nicht prüfbar")
    else:
        p.geprueft += 1
        n = sum(1 for t in themen if t["leitachse"])
        if n != 1:
            p.fehler.append("leitachse=ja steht bei %d Themen, verlangt ist genau eines%s"
                            % (n, " (" + ", ".join("THEMA %d" % t["nr"] for t in themen if t["leitachse"]) + ")" if n else ""))
    if p.geprueft == 0 and not p.fehler:
        return p.aussagelos("weder Leitsatz noch Themenliste lesbar")
    return p.abschluss()

# Wortlisten fuer P8 — Quellen im Kommentar; alles nur PRUEFEN.
# Dritte: Innere Arbeit, Prinzip 13 / Dritte-Probe (Nr. 8): "dein Partner", "deine
# Mutter", "dein Vater", "deine Kinder", "dein Chef" — hier mit Beugung und den
# naechstliegenden Formen (Partnerin, Eltern, Kind, Chefin).
DRITTE_RE = re.compile(r"(?<![\wäöüß])dein(?:e|em|er|es|en)?\s+"
                       r"(Partner(?:in|s)?|Mutter|Vater(?:s)?|Eltern|Kind(?:er|es|ern)?|Chef(?:in|s)?)"
                       r"(?![\wäöüß])", re.I)
# Vergangenheits-Indikativ: Innere Arbeit, Prinzip 5 und Guardrail ("du hast frueh
# gelernt, dass") sowie Wortscan Nr. 9, Liste "Zeit" ("damals hast du", "damals ist").
VERGANGENHEIT = ("du hast früh gelernt", "du hast gelernt", "hast du gelernt", "damals hast du",
                 "damals ist", "damals war", "als Kind hast du", "als Kind warst du",
                 "du bist aufgewachsen", "bist du aufgewachsen", "du wurdest", "dir wurde",
                 "in deiner Kindheit", "du hast erlebt", "du hast erfahren")
VERGANGENHEIT_RE = re.compile("|".join(r"(?<![\wäöüß])" + re.escape(w) + r"(?![\wäöüß])"
                                       for w in VERGANGENHEIT), re.I)
# Aspekt-Wertung: Klartext-Modul, Abschnitt Pruefung, Stand 2026-09-14 — "voll" und
# "einseitig" nur als Wortpaar oder unmittelbar bei einer Gradangabe. `restyle.VERBOTEN`
# fuehrt "einseitig" noch als nacktes Wort (Stand vor dem 14.09.); es wird hier in
# der Wertungs-Form gesucht, nicht als Wort.
WERTUNG_RE = re.compile(r"\d{1,3}°\s*\d{1,2}[′']\s*,?\s*(?:voll|einseitig)\b"
                        r"|,?\s*(?:voll|einseitig)\s*,?\s*\d{1,3}°\s*\d{1,2}[′']"
                        r"|\bvoll\s*/\s*einseitig\b")
GRADZAHL_RE = re.compile(r"\d{1,3}\s*°|\d{1,3}\s*[′']|(?<![\wäöüß])\d{1,3}\s*Grad(?![\wäöüß])")
HAUSZIFFER_RE = re.compile(r"(?<![\wäöüß])\d{1,2}\.\s*Haus(?![\wäöüß])"
                           r"|(?<![\wäöüß])H[äa]us(?:es|er|ern)?\s+\d{1,2}(?![\wäöüß])")

def _fachbegriff_re():
    woerter = [w for w in VERBOTEN_FACHBEGRIFFE if w not in ("°", "′", "einseitig", "voll")]
    return re.compile("|".join(r"(?<![\wäöüÄÖÜß])" + re.escape(w) + r"(?![\wäöüÄÖÜß])" for w in woerter))
FACHBEGRIFF_RE = _fachbegriff_re()

def _p8_wortlisten(chapters):
    p = _Probe("P8", "Wortlisten")
    p.einheit = "Absätze"
    listen = (("Dritte", DRITTE_RE), ("Vergangenheits-Indikativ", VERGANGENHEIT_RE),
              ("Fachbegriff", FACHBEGRIFF_RE), ("Aspekt-Wertung", WERTUNG_RE),
              ("Gradzahl", GRADZAHL_RE), ("Hausnummer in Ziffern", HAUSZIFFER_RE))
    for ch in chapters:
        if _ist_kicker(ch, "Auftakt", "Rechenschaft"):
            continue
        bewegung = "—"
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bewegung = _ws(b["text"])
                continue
            p.geprueft += 1
            t = b["text"]
            for name, rx in listen:
                gesehen = set()
                for m in rx.finditer(t):
                    satz = _satz_mit(t, m.start())
                    key = (name, satz)
                    if key in gesehen:
                        continue
                    gesehen.add(key)
                    p.pruefen.append("%s · %s · %s: „%s“ — Treffer „%s“"
                                     % (name, _bezeichnung(ch), bewegung, _kurz(satz, 140), m.group(0)))
    if p.geprueft == 0:
        return p.aussagelos("kein Fließtext-Absatz gefunden")
    return p.abschluss()

NICHTWISSEN_RE = re.compile(r"wei(?:ß|ss) ich nicht|(?:steht|stehen) in keinem Horoskop|in keinem Horoskop", re.I)
VERWERF_RE = re.compile(r"verwerf|verwirf", re.I)

def _p9_zwei_saetze(chapters, typ):
    p = _Probe("P9", "Zwei Sätze")
    p.einheit = "Kapitel"
    # (a) Nichtwissens-Satz je Wurzel-Bewegung
    wurzeln = set()
    if typ in WORTLAUTE:
        v = WORTLAUTE[typ]
        for wl in (v.values() if isinstance(v, dict) else [v]):
            w = wl[2]
            wurzeln.update(w if isinstance(w, tuple) else (w,))
    else:
        p.hinweise.append("Typ %s ohne Wortlaute — Nichtwissens-Satz nicht geprüft" % (typ or "unbekannt"))
    kapitel = [ch for ch in chapters if _hat_bewegungen(ch)]
    for ch in kapitel:
        if not wurzeln:
            break
        aktuell, text_wurzel, hat_wurzel = None, [], False
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                aktuell = _ws(b["text"])
                if aktuell in wurzeln:
                    hat_wurzel = True
                continue
            if aktuell in wurzeln:
                text_wurzel.append(b["text"])
        if hat_wurzel:
            p.geprueft += 1
            if not NICHTWISSEN_RE.search(" ".join(text_wurzel)):
                p.pruefen.append("%s · Wurzel-Bewegung ohne Nichtwissens-Satz („weiß ich nicht“ / "
                                 "„steht in keinem Horoskop“)" % _bezeichnung(ch))
    # (b) Verwerfungs-Erlaubnis nur im Auftakt und im ersten Themenkapitel
    erstes = kapitel[0] if kapitel else None
    for ch in chapters:
        if _ist_kicker(ch, "Auftakt") or ch is erstes:
            continue
        bewegung = "—"
        for b in ch["blocks"]:
            if b.get("type") == "subhead":
                bewegung = _ws(b["text"])
                continue
            for m in VERWERF_RE.finditer(b["text"]):
                p.pruefen.append("Verwerfungs-Erlaubnis außerhalb des ersten Themenkapitels · %s · %s: „%s“"
                                 % (_bezeichnung(ch), bewegung, _kurz(_satz_mit(b["text"], m.start()), 140)))
                break
    if p.geprueft == 0 and not kapitel:
        return p.aussagelos("kein Kapitel mit Bewegungsfolge gefunden")
    return p.abschluss()

# ---------------------------------------------------------------------------
# Hauptaufrufe
# ---------------------------------------------------------------------------

class InhaltsprobeFehler(Exception):
    """Eingabe nicht lesbar (fehlende Datei, SchemaError der Analyse)."""

def pruefe(analyse_pfad, chart_data_pfad, typ=None):
    """Haelt die Analyse gegen die chart_data. -> dict (s. Docstring des Moduls).

    typ: 'geburt' | 'ea' | 'transit' | 'ultimativ' | None (aus der H1 ableiten)."""
    for pf in (analyse_pfad, chart_data_pfad):
        if not os.path.isfile(pf):
            raise InhaltsprobeFehler("Datei nicht gefunden: %s" % pf)
    try:
        parsed = build.parse_analyse(analyse_pfad)
    except Exception as e:
        raise InhaltsprobeFehler("Analyse nicht lesbar (%s): %s" % (type(e).__name__, _kurz(str(e), 300)))
    txt = open(chart_data_pfad, encoding="utf-8").read()
    chapters = parsed["chapters"]

    if typ:
        typ = {"geburtshoroskop": "geburt"}.get(typ.casefold(), typ.casefold())
        if typ not in TYPEN:
            raise InhaltsprobeFehler("Unbekannter --typ %r; bekannt: %s" % (typ, ", ".join(TYPEN)))
        typ_quelle = "Parameter"
    else:
        typ = typ_aus_h1(parsed.get("doctype"))
        typ_quelle = "H1 „%s“" % parsed.get("doctype") if typ else "H1 „%s“ nicht zuordenbar" % parsed.get("doctype")

    chart = selektor.parse_chart(txt)
    tabelle = _tabellen_lesen(txt)
    staende = _staende_lesen(txt)
    themen = _themenliste_lesen(txt)

    p1 = _p1_beleg_aspekte(chapters, typ, tabelle)
    p2 = _p2_beleg_staende(chapters, typ, chart, staende)
    p3, p7, zuordnung = _p3_p7_kapitel_themen(chapters, typ, themen)
    p4 = _p4_bewegungsfolge(chapters, typ, zuordnung)
    p5 = _p5_rechenschaft(chapters, chart, themen)
    p6 = _p6_leitsatz(chapters, chart_data_pfad, themen)
    p8 = _p8_wortlisten(chapters)
    p9 = _p9_zwei_saetze(chapters, typ)
    proben = [p1, p2, p3, p4, p5, p6, p7, p8, p9]

    fehler = sum(len(p.fehler) for p in proben)
    pruefen_n = sum(len(p.pruefen) for p in proben)
    ueber = [(p.nr, p.status.lower(), p.grund) for p in proben if p.status in ("UEBERSPRUNGEN", "AUSSAGELOS")]
    return {
        "analyse": analyse_pfad, "chart_data": chart_data_pfad,
        "typ": typ, "typ_quelle": typ_quelle, "doctype": parsed.get("doctype"),
        "proben": {p.nr: p.als_dict() for p in proben},
        "fehler": fehler, "pruefen": pruefen_n, "uebersprungen": ueber,
        "ok": fehler == 0,
    }

def _zeile(p):
    kopf = "%s %s:" % (p["nr"], p["name"])
    st = p["status"]
    if st == "UEBERSPRUNGEN":
        return ["%s übersprungen — %s" % (kopf, p["grund"])]
    if st == "AUSSAGELOS":
        return ["%s AUSSAGELOS — %s" % (kopf, p["grund"])]
    zaehl = "%d %s" % (p["geprueft"], p["einheit"])
    if st == "FEHLER":
        out = ["%s FEHLER (%d Fehler, %s%s)" % (kopf, len(p["fehler"]), zaehl,
                                                 ", %d PRÜFEN" % len(p["pruefen"]) if p["pruefen"] else "")]
    elif st == "PRUEFEN":
        out = ["%s %s, 0 Fehler, %d PRÜFEN" % (kopf, zaehl, len(p["pruefen"]))]
    else:
        out = ["%s %s, 0 Fehler" % (kopf, zaehl)]
    out += ["    FEHLER  " + f for f in p["fehler"]]
    out += ["    PRÜFEN  " + f for f in p["pruefen"]]
    out += ["    Hinweis " + h for h in p["hinweise"]]
    return out

def bericht(analyse_pfad, chart_data_pfad, typ=None):
    """Der Prueftext: eine Zeile je Probe, je Befund eine eingerueckte Zeile,
    zuletzt `INHALTSPROBE: f FEHLER · p PRÜFEN · s übersprungen (Gründe)`."""
    return bericht_aus(pruefe(analyse_pfad, chart_data_pfad, typ))

def bericht_aus(r):
    """Prueftext aus einem Ergebnis von pruefe()."""
    zeilen = ["Inhaltsprobe — %s gegen %s (Typ: %s, aus %s)"
              % (os.path.basename(r["analyse"]), os.path.basename(r["chart_data"]),
                 r["typ"] or "unbekannt", r["typ_quelle"])]
    for nr in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"):
        zeilen += _zeile(r["proben"][nr])
    gruende = "; ".join("%s %s: %s" % (nr, art, g) for nr, art, g in r["uebersprungen"])
    zeilen.append("INHALTSPROBE: %d FEHLER · %d PRÜFEN · %d übersprungen%s"
                  % (r["fehler"], r["pruefen"], len(r["uebersprungen"]),
                     " (%s)" % gruende if gruende else ""))
    return "\n".join(zeilen)

# ---------------------------------------------------------------------------
# Selbsttest — KONSTRUIERTER Fall. Kein reales Geburtsdatum, keine Uhrzeit, kein
# Name, keine Staende eines realen Charts (Datenschutz-Guardrail des Kerns).
# ---------------------------------------------------------------------------

_TEST_CHART = """# Chart-Datenblatt — Prüffall

## Stände (konstruiert)

| Faktor | Grad | Zeichen | Haus | Lauf |
|---|---|---|---|---|
| Sonne | 10°00′ | Widder ♈ | 1 | direkt |
| Mond | 20°00′ | Stier ♉ | 2 | direkt |
| Merkur | 11°10′ | Widder ♈ | 1 | direkt |
| Mars | 5°00′ | Krebs ♋ | 4/3 | direkt |
| Saturn | 22°05′ | Jungfrau ♍ | 6 | direkt |
| AC | 0°00′ | Widder ♈ | 1 | — |
| MC | 0°00′ | Steinbock ♑ | 10 | — |
| DC | 0°00′ | Waage ♎ | 7 | — |
| IC | 0°00′ | Krebs ♋ | 4 | — |

## Aspekte (konstruiert)

### Volle Aspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Sonne | ☌ Konjunktion | Merkur | 1°10′ | konj |  |
| Mond | △ Trigon | Saturn | 2°05′ | blau |  |
| Mars | □ Quadrat | AC | 0°40′ | rot | Quadrat DC |

### Einseitige Aspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Mars | ☍ Opposition | MC | 0°40′ | rot | Konjunktion IC |

### Nebenaspekte

| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |
|---|---|---|---|---|---|
| Sonne | ⚹ Sextil | Mond | 4°30′ | gruen |  |

### Untergrund-Aspekte

_keine_

## Themenliste

```
THEMA 1 | titel=Der Anfang, der sich selbst genügt
  | fuehrt=Sonne, Widder, Haus 1
  | klingt=Merkur Widder Haus 1
  | aspekte=Sonne ☌ Merkur, Sonne ⚹ Mond
  | rang=4 | form=voll
  | praxis=Einmal am Tag den ersten Impuls bemerken.
  | familie=Bemerken und Benennen
  | leitachse=ja

THEMA 2 | titel=Was hält, wenn nichts drängt
  | fuehrt=Mond, Stier, Haus 2
  | klingt=Saturn Jungfrau Haus 6
  | aspekte=Mond △ Saturn
  | rang=5 | form=kurz | grund=kein Aspektmaterial für Wurzel und Widerstand
  | praxis=Einmal in der Woche etwas stehen lassen, das fertig ist.
  | familie=Innehalten
```
RECHENSCHAFT: Merkur, Widder, Haus 1 — klingt mit in Kapitel 2. Mars, Krebs,
              Haus 4/3 (Grenzlage). Saturn, Jungfrau, Haus 6 — klingt mit in Kapitel 3.
GESTRICHEN:   keines.

## Ressourcen
Mond △ Saturn 2°05′ voll — Deutungsort: Thema 2

@@SELEKTOR
FAKTOR SONNE zeichen=Widder haus=1 fuehrt=ja
FAKTOR MOND zeichen=Stier haus=2 fuehrt=ja
FAKTOR MERKUR zeichen=Widder haus=1
FAKTOR MARS zeichen=Krebs haus=3 nebenhaus=4 abstand=1.5
FAKTOR SATURN zeichen=Jungfrau haus=6
ACHSE AC zeichen=Widder
ACHSE MC zeichen=Steinbock
ACHSE DC zeichen=Waage
ACHSE IC zeichen=Krebs
ASPEKT SONNE MERKUR
ASPEKT MOND SATURN
@@ENDE
@@DECKBLATT
LEITSATZ: Du fängst an, bevor jemand dich darum bittet — und das ist kein Fehler.
LEITACHSE: Der Anfang, der sich selbst genügt
TITELMOTIV: Ein einzelner Stein auf einem leeren Feld im ersten Licht.
PALETTE: Sandgelb, Grau, ein kühles Blau.
GLYPHEN: ☉ ♈ — die Sonne im Widder als der Anfang
@@ENDE
"""

_TEST_ANALYSE = """# Geburtshoroskop — Prüffall

## Auftakt · Wie dieses Horoskop zu lesen ist

Dieses Dokument beschreibt Anlagen, keine Tatsachen. Wenn du ein Kapitel liest und dich darin nicht wiederfindest, darfst du es verwerfen; das gilt für jedes Kapitel dieses Bandes. Am Ende steht eine Liste dessen, was gerechnet und nicht gedeutet wurde.

## Kapitel 1 · Was unter allem liegt

**Signatur:** Die Statik des Bildes — viel Feuer, wenig Wasser, ein kurzer Herrscherkreis

**Beleg:** Elemente Feuer 3 · Erde 1 · Luft 0 · Wasser 1 · Herrscherkreis Sonne → Mars → Mond → Venus

Das Bild ruht auf wenigen Kräften, die einander kaum stützen. Was fehlt, ersetzt die Anstrengung.

## Instrument · Wie du gebaut bist

**Signatur:** Die persönlichen Funktionen in ihrer Anlage — Sonne im Widder im ersten Haus, Mond im Stier im zweiten

**Beleg:** Sonne ☉ 10°00′ Widder ♈, 1. Haus — Konjunktion ☌ Merkur ☿ 1°10′, Sextil ⚹ Mond ☽ 4°30′ · Mond ☽ 20°00′ Stier ♉, 2. Haus — Trigon △ Saturn ♄ 2°05′

### Die Sonne — der Kern

Deine Sonne im Widder im ersten Haus fängt an, bevor die Frage gestellt ist. Was daraus unter Druck wird, steht in Kapitel 2.

### Der Mond — wie du fühlst

Dein Mond im Stier im zweiten Haus braucht Dauer, um sich sicher zu fühlen. Er hält, was einmal da ist.

## Kapitel 2 · Der Anfang, der sich selbst genügt

**Signatur:** Die Sonne im Widder im ersten Haus, verschmolzen mit Merkur — mitklingend der Mond im Stier

**Beleg:** Sonne ☉ 10°00′ Widder ♈, 1. Haus · Sonne ☉ Konjunktion ☌ Merkur ☿ 11°10′ Widder ♈, 1. Haus, Orb 1°10′ · Sonne ☉ Sextil ⚹ Mond ☽ 20°00′ Stier ♉, 2. Haus, Orb 4°30′

### Woran du es merkst

Du hast angefangen, bevor die anderen fertig überlegt haben. Und ein Letztes, das schwerer zuzugeben ist: Es ärgert dich, wenn jemand vor dir anfängt. Wenn du das nicht kennst, leg das Kapitel weg; das gilt für alle folgenden Kapitel ebenso.

### Was da arbeitet

Deine Sonne im Widder im ersten Haus, verschmolzen mit Merkur — ein Denken, das im Moment des Anfangens entsteht — sucht den ersten Schritt, weil dort die Kraft ist.

### Wie so etwas zur Regel wird

Regeln dieser Art entstehen in Umgebungen, in denen Warten teuer war. Wo du das gelernt hast, weiß ich nicht — das steht in keinem Horoskop.

### Der Teil von dir, der das nicht aufgeben will

Der Teil, der zuerst losgeht, hat oft recht gehabt. Er rechnet mit alten Zahlen, aber er rechnet.

### Die zwei Formen und das Dazwischen

Die reife Form fängt an und lässt andere nachkommen. Die regressive Form fängt an, um nicht warten zu müssen, und fühlt sich dabei wie Fortschritt an. Dazwischen liegt der Normalfall: Du merkst es und gehst trotzdem los.

### Womit du arbeiten kannst

Einmal am Tag den ersten Impuls bemerken, ohne ihm zu folgen. Nicht tun: dich zum Warten zwingen. Gut genug ist, es einmal bemerkt zu haben.

### Wohin das gehört

Dieses Thema ist die Vorderseite von Kapitel 3. Es ist groß in deinem Bild, aber nicht das Ganze; was ein Text davon leisten kann, ist die Landkarte, nicht der Weg.

## Kapitel 3 · Was hält, wenn nichts drängt

**Signatur:** Der Mond im Stier im zweiten Haus, getragen von Saturn — mitklingend Saturn in der Jungfrau

**Beleg:** Mond ☽ 20°00′ Stier ♉, 2. Haus · Mond ☽ Trigon △ Saturn ♄ 22°05′ Jungfrau ♍, 6. Haus, Orb 2°05′

### Woran du es merkst

Du bleibst, wo andere längst gegangen sind. Und ein Letztes, das schwerer zuzugeben ist: Manchmal bleibst du aus Bequemlichkeit.

### Was da arbeitet

Dein Mond im Stier im zweiten Haus, im Trigon zu Saturn — eine Verbindung, die von selbst hält — braucht keine Bewegung, um sich sicher zu fühlen. Dieses Kapitel läuft in der Kurzform: Ein einzelner harmonischer Aspekt liefert kein Material für Wurzel und Widerstand.

### Die zwei Formen und das Dazwischen

Genutzt: Du hältst, was gehalten werden muss. Verschleudert: Du hältst auch, was gehen dürfte. Dazwischen liegt der Normalfall.

### Womit du arbeiten kannst

Einmal in der Woche etwas stehen lassen, das fertig ist. Nicht tun: daraus ein Projekt machen. Gut genug ist, es einmal getan zu haben.

### Wohin das gehört

Dies ist die Rückseite von Kapitel 2. Es ist eine ruhige Stelle in deinem Bild.

## Rechenschaft · Was sonst in deinem Bild steht

Gerechnet wurde das ganze Bild; gedeutet wurden zwei Themen. Was dazwischen liegt, steht hier.

1. Merkur, Widder, erstes Haus — das schnelle Wort. Klingt mit in Kapitel 2.
2. Mars, Krebs, viertes/drittes Haus in Grenzlage — die Kraft, die nach innen geht.
3. Saturn, Jungfrau, sechstes Haus — die Ordnung im Alltag. Klingt mit in Kapitel 3.

## Hauptthemen · Zwei Linien

**Signatur:** Zusammenführung der Kapitel 2 und 3

Anfangen und Halten sind die beiden Linien dieses Bildes. Was trägt: Der Mond im Trigon zu Saturn — was dir leicht zufällt und gerade deshalb brachliegen kann — hält, ohne dass du es merkst.

## Konfliktfelder · Wo es reibt

**Signatur:** Die Gegensatzpaare der Kapitel 2 und 3

Anfangen gegen Halten: Beides ist in dir angelegt, und beides will zuerst.

## Lebensaufgaben · Woran du wächst

**Signatur:** Was aus den Kapiteln 2 und 3 als Richtung bleibt

Den Anfang machen und dann bleiben, bis er trägt.

## Schlusswort · Was bleibt

Du fängst an, bevor jemand dich darum bittet — und das ist kein Fehler. Das ist der Satz, auf den dieses Horoskop hinausläuft. Was ein Text leisten kann, ist eine Landkarte; gehen musst du selbst.
"""

def _selbsttest(still=False):
    """Konstruierter Fall, zweimal: fehlerfrei und mit je einem Fehler je Probe."""
    import tempfile
    def lauf(chart, analyse):
        d = tempfile.mkdtemp(prefix="inhaltsprobe_")
        pa, pc = os.path.join(d, "prueffall_analyse.md"), os.path.join(d, "prueffall_chart_data.md")
        open(pa, "w", encoding="utf-8").write(analyse)
        open(pc, "w", encoding="utf-8").write(chart)
        return pruefe(pa, pc)

    def ersetze(text, alt, neu):
        assert text.count(alt) == 1, "Selbsttest-Marke nicht eindeutig: %r" % alt
        return text.replace(alt, neu)

    berichte = []
    # 1) fehlerfrei
    r = lauf(_TEST_CHART, _TEST_ANALYSE)
    st = {nr: p["status"] for nr, p in r["proben"].items()}
    berichte.append("Lauf 1 (fehlerfrei): " + ", ".join("%s=%s" % kv for kv in st.items()))
    assert all(s == "OK" for s in st.values()), "Lauf 1 nicht sauber: %s\n%s" % (
        st, "\n".join(f for p in r["proben"].values() for f in p["fehler"] + p["pruefen"]))
    assert r["fehler"] == 0 and r["pruefen"] == 0 and not r["uebersprungen"]

    # 2) je ein Fehler je Probe P1–P6 (P7 haengt an P3), je ein Treffer P8 und P9
    a, c = _TEST_ANALYSE, _TEST_CHART
    a = ersetze(a, "Sonne ☉ Konjunktion ☌ Merkur ☿ 11°10′ Widder ♈, 1. Haus, Orb 1°10′",
                   "Sonne ☉ Konjunktion ☌ Merkur ☿ 11°10′ Widder ♈, 1. Haus, Orb 2°10′")      # P1 Orb
    a = ersetze(a, "**Beleg:** Mond ☽ 20°00′ Stier ♉, 2. Haus ·",
                   "**Beleg:** Mond ☽ 20°00′ Stier ♉, 3. Haus ·")                              # P2 Haus
    c = ersetze(c, "  | fuehrt=Mond, Stier, Haus 2", "  | fuehrt=Merkur, Widder, Haus 1")     # P3/P7 Fuehrer
    a = ersetze(a, "### Der Teil von dir, der das nicht aufgeben will\n\nDer Teil, der zuerst losgeht, hat oft recht gehabt. Er rechnet mit alten Zahlen, aber er rechnet.\n\n", "")  # P4 Bewegung fehlt
    a = ersetze(a, "\n3. Saturn, Jungfrau, sechstes Haus — die Ordnung im Alltag. Klingt mit in Kapitel 3.",
                   "")                                                                          # P5 Zeile fehlt
    c = ersetze(c, "LEITSATZ: Du fängst an, bevor jemand dich darum bittet — und das ist kein Fehler.",
                   "LEITSATZ: Was dich trägt, meldet sich nicht — es ist trotzdem da.")          # P6 Leitsatz
    a = ersetze(a, "Du bleibst, wo andere längst gegangen sind.",
                   "Du bleibst, wo dein Partner längst gegangen ist.")                          # P8 Dritte
    a = ersetze(a, "Wo du das gelernt hast, weiß ich nicht — das steht in keinem Horoskop.",
                   "Die Prüfung daran ist deine Sache.")                                          # P9a Nichtwissen
    a = ersetze(a, "Es ist eine ruhige Stelle in deinem Bild.",
                   "Es ist eine ruhige Stelle in deinem Bild; auch dieses Kapitel darfst du verwerfen.")  # P9b
    r2 = lauf(c, a)
    erwartet = {"P1": ("fehler", "Orb 2°10′"), "P2": ("fehler", "führendes Haus 3"),
                "P3": ("fehler", "Themenliste sagt Merkur"), "P4": ("fehler", "fehlt: „Der Teil von dir"),
                "P5": ("fehler", "Saturn führt kein Thema"), "P6": ("fehler", "Leitsatz nicht im Schlusswort"),
                "P7": ("fehler", "Signatur nennt Merkur nicht"),
                "P8": ("pruefen", "dein Partner"), "P9": ("pruefen", "Nichtwissens-Satz")}
    fehlt = []
    for nr, (feld, marke) in erwartet.items():
        treffer = r2["proben"][nr][feld]
        if not any(marke in t for t in treffer):
            fehlt.append("%s: erwartet %s mit „%s“, gefunden: %s" % (nr, feld.upper(), marke, treffer or "nichts"))
    if not any("Verwerfungs-Erlaubnis" in t for t in r2["proben"]["P9"]["pruefen"]):
        fehlt.append("P9: erwartet PRUEFEN zur Verwerfungs-Erlaubnis")
    st2 = {nr: p["status"] for nr, p in r2["proben"].items()}
    berichte.append("Lauf 2 (eingebaute Fehler): " + ", ".join("%s=%s" % kv for kv in st2.items()))
    assert not fehlt, "Eine Probe findet ihren Testfehler nicht:\n  " + "\n  ".join(fehlt)
    if not still:
        print("\n".join(berichte))
        print("[Selbsttest bestanden: Lauf 1 ohne Befund, Lauf 2 findet je Probe den eingebauten Fehler]")
    return True

def _main(argv):
    if "--selbsttest" in argv:
        _selbsttest()
        return 0
    args = [x for x in argv if not x.startswith("--")]
    typ = None
    if "--typ" in argv:
        i = argv.index("--typ")
        typ = argv[i + 1] if i + 1 < len(argv) else None
        args = [x for x in args if x != typ]
    if len(args) != 2:
        print("Aufruf: python3 inhaltsprobe.py <analyse.md> <chart_data.md> [--typ geburt|ea|transit|ultimativ]\n"
              "        python3 inhaltsprobe.py --selbsttest", file=sys.stderr)
        return 2
    try:
        r = pruefe(args[0], args[1], typ)
    except InhaltsprobeFehler as e:
        print("INHALTSPROBE: nicht lesbar — %s" % e, file=sys.stderr)
        return 2
    print(bericht_aus(r))
    return 1 if r["fehler"] else 0

if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
