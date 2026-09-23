#!/usr/bin/env python3
"""
transit.py — generischer Transit-Rechner (Builder fuer das Transit-Horoskop), v2.

Rechnet drei Ebenen aus derselben Ephemeriden-Sampling-Basis:

  1. JETZT  — Momentaufnahme zum Stichtag (Default: Startdatum): jeder Kontakt,
     der am Stichtag im weiten Orb (Default 3.0 Grad) steht, mit Richtung
     (zulaufend/auslaufend/stationaer), letztem und naechstem Exaktdatum,
     Restlaufzeit; dazu Nachhall (kurz zurueckliegende Exaktkontakte) und
     Anmarsch (Exaktkontakte der naechsten 90 Tage). Dafuer wird ein
     Rueckblickfenster VOR dem Start mitgerechnet (Default 6 Monate) — sonst
     bekaemen auslaufende Kontakte kein echtes Exaktdatum.
  2. LANGLAEUFER — Kontakte, die ueber viele Monate oder das ganze Fenster
     laufen: Gesamtspanne, Dauer, Mehrfachkontakte durch Rueckläufigkeit,
     Teilperioden, Stationen darin. Dazu Zeichen-Aufenthalte und (wenn die
     Koch-Spitzen lesbar sind) Haus-Durchgaenge der langsamen Planeten.
  3. QUARTALE — die datierte 8-Quartals-Vorschau ueber N Monate (Default 24):
     Wirk-Orb 1.5 Grad, Exaktdaten, Stationen, Ingresse. Die Quartale sind
     KALENDERQUARTALE; das Fenster beginnt am ersten Tag des Quartals, in
     dem der Start-/Erstellungstag liegt, und endet mit dem achten Quartal
     (Hausstil 2026-07-27). --start ist damit ein Hinweis auf das Quartal,
     nicht mehr der exakte Fensteranfang; --asof bleibt taggenau.

Kontakte werden im WEITEN Orb erfasst und mit `im_wirkorb` markiert
(min. Orb <= 1.5). Die Quartalsdeutung nutzt NUR Wirkorb-Kontakte; der
Jetzt-Teil darf die weiteren als Anmarsch/Ausklang nennen.

Transit-Chiron wird automatisch mitgerechnet, WENN die Asteroiden-Ephemeride
(seas_*.se1) verfuegbar ist; sonst sauber ausgeklammert (Radix-Chiron bleibt
immer Ziel). Hauptplaneten laufen ueber die Moshier-Ephemeride — ohne externe
Dateien, bogenminutengenau.

SEIT 30.07.2026 (Fehlerkorrektur): Der Ephemeriden-Suchpfad wird beim Import
gesucht und gesetzt (`ephe_pfad_setzen`). Vorher stand dort ein hartes
`swe.set_ephe_path(None)` — dadurch fand die Bibliothek `seas_*.se1` NIE, und
Transit-Chiron war ausnahmslos ausgeklammert, auch bei installierter
Ephemeride. Der Report meldete das nur als "AUSGEKLAMMERT", ohne Grund; jetzt
steht der Grund als eigene `[hinweis]`-Zeile darunter, und im Erfolgsfall nennt
eine `[ephemeride]`-Zeile das benutzte Verzeichnis. Notfalls `--ephe <verz>`
setzen. Die beiden bisherigen Kopfzeilen bleiben unveraendert (transitdata.py
parst sie). `_transiters` gibt seither drei statt zwei Werte zurueck.

SEIT 2026-09-19 (Wartungslauf A, W1/W3/W45/W46/F20/F21): EXAKT HEISST
NULLDURCHGANG — gesucht im Stundenraster mit Bisektion; ein Minimum ohne
Kreuzung ist eine Annaeherung ("Annaeherung bis x′", JSON `annaeherung`), kein
Exaktdatum. Der Report hat zwei neue Abschnitte, "Fortsetzung nach dem Fenster"
(bis 36 Monate nach Fensterende) und "Frühere Durchgänge mit Datum und Alter"
(bis zur Geburt, mit --geburt); ein Prozessbeginn vor dem Rueckblick steht in der
Langlaeufer-Zeile "vor dem Rueckblick:". Die JETZT-Zeile trennt Orb am Stichtag,
Nulldurchgang und Wirkorb-Periode. --moseph rechnet alles auf Moshier (ohne
Chiron) fuer die Zwei-Modell-Probe. Zeitangaben ausserhalb des Fensters stehen
NUR in diesen Abschnitten — nie selbst nachrechnen. Selbsttest:
python3 transit.py --selbsttest.

Radix kommt aus der bereits gerechneten <klient>_chart_data.md (factors/achsen-
Block) — NIE neu rechnen (Token-Oekonomie, s. Kern). Die Koch-Hausspitzen werden
aus derselben Datei gelesen, wenn sie dort maschinenlesbar (cusps-Liste) oder als
Text/Tabelle stehen; sonst laeuft alles ausser den Haus-Durchgaengen normal
weiter (Status im Report: haeuser: JA/AUSGEKLAMMERT).

CLI:
    python3 transit.py <chart_data.md> [--start YYYY-MM-DD] [--months 24] \\
            [--asof YYYY-MM-DD] [--lookback 6] [--orb 1.5] [--orb-weit 3.0] \\
            [--primary Venus,Mars,Pluto,Saturn,Chiron,Mondknoten] \\
            [--cusps "175.3,201.0,..."] [--ephe <verzeichnis>] [--json out.json] \\
            [--tz Europe/Berlin] [--geburt YYYY-MM-DDTHH:MM] [--moseph] \\
            [--ohne-chiron] [--mars]
    python3 transit.py --selbsttest

Modul:
    from transit import radix_from_chart_data, cusps_from_chart_data, run, format_report
    radix = radix_from_chart_data("<klient>_chart_data.md")
    cusps = cusps_from_chart_data("<klient>_chart_data.md", radix)   # oder None
    res   = run(radix, primary_extra=["Venus","Mars","Pluto"], cusps=cusps)
    print(format_report(res))
    # res = {"start","end","asof","lookback_start","events","jetzt","langlaeufer",
    #        "hausdurchgang","zeichenaufenthalt","hotspots","stations","ingress",
    #        "quarter_bounds","chiron_transit","haeuser","primary", ...}
"""
import swisseph as swe
import json, re, sys, os, glob, site, argparse
from datetime import date, timedelta, datetime, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:                                  # Python < 3.9
    ZoneInfo = None

MOSEPH = swe.FLG_MOSEPH | swe.FLG_SPEED          # Rueckfall: keine ext. Dateien
HAUPT_MODELL = 'Moshier'                         # wird in _transiters() gesetzt
SWIEPH = swe.FLG_SWIEPH | swe.FLG_SPEED          # Chiron: braucht seas_*.se1

# ---------------------------------------------------------------------------
# Ephemeriden-Suchpfad — Voraussetzung fuer Transit-Chiron
# ---------------------------------------------------------------------------
# FEHLERKORREKTUR 30.07.2026. Hier stand `swe.set_ephe_path(None)`. Damit hatte
# die Swiss Ephemeris nur ihren eingebauten Standardpfad (".:/users/ephe2/:
# /users/ephe/"), und der Chiron-Probeaufruf in `_transiters` schlug IMMER mit
# "SwissEph file 'seas_18.se1' not found" fehl — auch dann, wenn die
# Asteroiden-Ephemeride laengst installiert war. Folge: Transit-Chiron wurde
# ausnahmslos ausgeklammert, der Report meldete brav "AUSGEKLAMMERT", und
# niemand konnte sehen, dass die Ebene nicht fehlen MUSSTE. In einem Chart mit
# chart-tragendem Chiron (z. B. Chiron als Arm eines Kosmischen Kreuzes) fehlte
# damit eine ganze Deutungsebene.
#
# Die Hauptplaneten sind davon unberuehrt: sie laufen ueber MOSEPH und lesen
# keine Dateien. Ein gesetzter Pfad aendert an ihren Zahlen nichts.
#
# Reihenfolge der Suche: expliziter Wunsch (--ephe / ephe_pfad_setzen) > Umgebungs-
# variable SE_EPHE_PATH > Paketverzeichnisse > uebliche Systemorte. Findet sich
# nichts, bleibt es beim alten Verhalten (Standardpfad) — dann aber MIT lauter
# Meldung im Report statt stiller Ausklammerung.

EPHE_PFAD = None            # gesetztes Verzeichnis, oder None = nicht gefunden


def _ephe_kandidaten():
    """Verzeichnisse, in denen die Ephemeriden-Dateien liegen koennten.
    Bewusst KEIN unbegrenzter Dateibaum-Lauf — nur bekannte Orte plus eine
    flache Suche in den Paketverzeichnissen."""
    kand = []
    env = os.environ.get("SE_EPHE_PATH")
    if env:
        kand += [x for x in env.split(os.pathsep) if x]
    try:
        kand.append(os.path.join(os.path.dirname(swe.__file__), "ephe"))
    except Exception:
        pass
    basen = []
    for holen in (getattr(site, "getsitepackages", None),
                  getattr(site, "getusersitepackages", None)):
        try:
            got = holen() if holen else None
            basen += [got] if isinstance(got, str) else list(got or [])
        except Exception:
            pass
    basen += [x for x in sys.path if x.endswith(("site-packages", "dist-packages"))]
    for b in dict.fromkeys(basen):
        kand.append(os.path.join(b, "flatlib", "resources", "swefiles"))
        kand.append(os.path.join(b, "swisseph", "ephe"))
        kand.append(os.path.join(b, "pyswisseph", "ephe"))
    kand += ["/usr/share/libswe/ephe", "/usr/share/ephe", "/usr/local/share/ephe",
             os.path.expanduser("~/.swisseph"), os.path.expanduser("~/swisseph"),
             os.path.join(os.getcwd(), "swefiles"), os.path.join(os.getcwd(), "ephe")]
    for b in dict.fromkeys(basen):                      # flache Restsuche
        for muster in ("*/resources/swefiles", "*/swefiles", "*/ephe"):
            try:
                kand += sorted(glob.glob(os.path.join(b, muster)))[:5]
            except Exception:
                pass
    return [k for k in dict.fromkeys(kand) if k]


def ephe_pfad_finden(extra=None):
    """Erstes Verzeichnis, das eine `seas_*.se1` enthaelt (die Asteroiden-Datei
    mit Chiron). None, wenn keines gefunden wird."""
    for d in ([extra] if extra else []) + _ephe_kandidaten():
        try:
            if d and os.path.isdir(d) and glob.glob(os.path.join(d, "seas_*.se1")):
                return d
        except Exception:
            continue
    return None


def ephe_pfad_setzen(pfad=None):
    """Setzt den Swiss-Ephemeris-Suchpfad und gibt das Verzeichnis zurueck.
    None = nichts gefunden; dann gilt der eingebaute Standardpfad wie bisher."""
    global EPHE_PFAD
    EPHE_PFAD = ephe_pfad_finden(pfad)
    swe.set_ephe_path(EPHE_PFAD)      # None ist zulaessig und bedeutet Standard
    return EPHE_PFAD


ephe_pfad_setzen()

ZODIAC = ['Widder','Stier','Zwillinge','Krebs','Loewe','Jungfrau',
          'Waage','Skorpion','Schuetze','Steinbock','Wassermann','Fische']
ZOD_ALIAS = {'loewe':'Loewe','löwe':'Loewe','lowe':'Loewe','schuetze':'Schuetze',
             'schütze':'Schuetze','schutze':'Schuetze','widder':'Widder','stier':'Stier',
             'zwillinge':'Zwillinge','krebs':'Krebs','jungfrau':'Jungfrau','waage':'Waage',
             'skorpion':'Skorpion','steinbock':'Steinbock','wassermann':'Wassermann',
             'fische':'Fische'}
ASPECTS = {'Konjunktion':0,'Sextil':60,'Quadrat':90,'Trigon':120,'Opposition':180}
SLOW_QUINCUNX = {'Neptun','Pluto','Chiron'}      # Quincunx nur bei den ganz langsamen
PERSONAL = {'Sonne','Mond','AC','MC'}            # immer primaer
AEUSSERE = {'Uranus','Neptun','Pluto','Chiron'}  # per se Langlaeufer
ORB = 1.5                                        # Wirk-Orb (Deutung, Quartale)
ORB_WEIT = 3.0                                   # Erfassungs-/Snapshot-Orb (Jetzt)
LOOKBACK_M = 6                                   # Rueckblick vor dem Start (Monate)
LANG_TAGE = 120                                  # ab hier gilt ein Kontakt als Langlaeufer
ANMARSCH_TAGE = 90                               # Vorlauf-Fenster im Jetzt-Teil
# Nach-/Vorwirkzeit im Jetzt-Teil, gedeckelt nach Verweildauer des Transiters.
# Ohne Eintrag gilt das volle Rueckblick- bzw. Anmarschfenster (die ganz Langsamen).
NACHWIRK = {'Mars':21,'Jupiter':60,'Knoten':90,'Saturn':120}
# REPARATUR 2026-09-18 (Pruefbericht Transit Schritt 1+2 2026-09-17, Klasse 1
# Nr. 1.1; Betreiber-Entscheidung 18.09.: `Mondknoten` ist der Zielname).
# Vorher: {'Knoten':'Nordknoten'} — die Abbildung ging vom ALTEN factors-Namen
# `Knoten` aus. Der chartdata.py-Vertrag des Datenblatt-Moduls schreibt seit der
# Vertragsnamen-Umstellung `Mondknoten` vor; bei einem vertragskonformen Block
# lief NAME_MAP deshalb leer, das Ziel hiess `Mondknoten`, und `--primary
# Nordknoten` brach hart ab, obwohl Transit-Modul und Fehlermeldung genau
# diesen Namen vorschrieben. Jetzt normalisieren beide Altnamen auf den
# Vertragsnamen; ALIAS_ZIEL unten tut dasselbe fuer die EINGABE.
NAME_MAP = {'Knoten': 'Mondknoten',              # factors-Name -> Radix-Zielname
            'Nordknoten': 'Mondknoten'}

# Eingabe-Aliasse fuer --primary / primary_extra. Ein Aufruf mit `Knoten` oder
# `Nordknoten` soll nicht mehr abbrechen, sondern auf den Vertragsnamen zeigen.
ALIAS_ZIEL = {'Knoten': 'Mondknoten', 'Nordknoten': 'Mondknoten'}

# Ausgemustert seit 2026-09-23 (Chris-Entscheidung; dieselbe Liste wie
# radix.AUSGEMUSTERT): der Glueckspunkt. Ein Datenblatt von vor dem Stichtag
# fuehrt ihn noch im factors-Block. radix_from_chart_data() nimmt ihn nicht
# als Transitziel auf — sonst rechnete ein neues Transit- oder EA-Dokument ihn
# mit — und sagt das auf stderr.
AUSGEMUSTERT = ('Glückspunkt', 'Glueckspunkt')

# 2026-09-19 (W1): Exakt heisst Nulldurchgang. Ein Minimum OHNE Vorzeichenwechsel
# der Differenz zum Aspektpunkt (Umkehr vor dem Punkt, Stationsberuehrung,
# Pendel des wahren Knotens) ist eine Annaeherung, auch wenn es dem Punkt bis auf
# Bogenminuten nahekommt. Bis 2026-09-18 stand jedes Minimum unter 0,05° als
# „exakt" im Report und in `exakt`; seither steht es unter `annaeherung`
# („Annaeherung bis x′"). Minima zwischen 0,05° und 0,3° bleiben wie bisher in
# `fast_exakt`.
ANNAEHERUNG_ORB = 0.05                           # Grad (= 3′)
FAST_EXAKT_ORB = 0.3                             # Grad, Obergrenze von `fast_exakt`
WINKEL = dict(ASPECTS, Quincunx=150)             # Aspektname -> Winkel

# 2026-09-19 (W3): Zeitangaben ueber das Rechenfenster hinaus.
# Fortsetzung: 36 Monate nach Fensterende. Laengste Wirkorb-Passage eines
# langsamen Transiters (Pluto nahe seiner langsamsten Bahnstrecke, dreifacher
# Durchgang) dauert rund zweieinhalb bis drei Jahre; ein Kontakt, der am
# Fensterende im Orb steht, endet damit praktisch immer innerhalb des Horizonts.
# Reicht er doch darueber, sagt es der Report ("ueber den Rechenhorizont
# hinaus"), statt still abzuschneiden. Rechenzeit: unter einer Sekunde.
FORTSETZUNG_MONATE = 36
# Fruehere Durchgaenge: mit --geburt bis zur Geburt zurueck; ohne pauschal so
# viele Jahre vor dem Rueckblick-Anfang (Durchgaenge vor der Geburt sind dann
# nicht ausgeschlossen — der Report sagt es in einer eigenen Zeile).
FRUEHER_OHNE_GEBURT_JAHRE = 90
# Luecke, ab der zwei Orb-Perioden getrennte Durchgaenge sind (wie in run()).
def _passage_luecke(tname):
    return 150 if tname == 'Mars' else 210

# 2026-09-19 (F21): --moseph / run(moseph=True) erzwingt die Moshier-Ephemeride
# fuer ALLE Faktoren (Zwei-Modell-Probe ohne eigenes Nullstellen-Skript).
ERZWINGE_MOSEPH = False

# 2026-09-19 (W55, L15): Selbst-Transit = der laufende Planet trifft seinen
# eigenen Radix-Ort, in jedem Aspekt (Saturn-Quadrat wie Saturn-Return); beim
# Knoten auch die Knotenrueckkehr (Transit `Knoten` auf Radix `Mondknoten`).
# Feld `selbst_transit` im JSON; das Transit-Modul fuehrt sie als Rang 1.
def ist_selbst_transit(transit, ziel):
    if transit == 'Knoten':
        return ziel in ('Mondknoten', 'Nordknoten', 'Knoten', 'Suedknoten', 'Südknoten')
    return transit == ziel

# ---------------------------------------------------------------------------
# Radix aus chart_data.md (factors/achsen-Block)
# ---------------------------------------------------------------------------
def radix_from_chart_data(path):
    """Liest name/lon-Paare aus dem factors- UND achsen-Block der chart_data.md.
    Erwartet Dict-Literale wie {'name':'Sonne', ... 'lon':45.4833, ...}. Gibt
    {Name: ekl. Laenge} zurueck (Knoten/Nordknoten -> Mondknoten normalisiert)."""
    txt = open(path, encoding='utf-8').read()
    rx = re.compile(r"'name'\s*:\s*'([^']+)'[^{}]*?'lon'\s*:\s*(-?\d+\.?\d*)")
    radix = {}
    weg = set()
    for name, lon in rx.findall(txt):
        if name in AUSGEMUSTERT:
            weg.add(name)
            continue
        radix[NAME_MAP.get(name, name)] = float(lon)
    if weg:
        print("[hinweis] %s: seit dem 2026-09-23 ausgemustert, nicht als "
              "Transitziel gerechnet (altes Datenblatt)." % ', '.join(sorted(weg)),
              file=sys.stderr)
    if not radix:
        raise SystemExit(
            f"Keine Radix gefunden in {path}: erwartet den factors/achsen-Block "
            "der chart_data mit {{'name':...,'lon':...}}-Eintraegen. Bei "
            "Folgeprodukten IMMER die Grundhoroskop-chart_data uebergeben.")
    return radix

# ---------------------------------------------------------------------------
# Koch-Hausspitzen aus chart_data.md (optional — sonst ausgeklammert)
# ---------------------------------------------------------------------------
def _plausible_cusps(c, radix=None):
    """12 Werte, zyklisch aufsteigend, H1~AC und H10~MC (je <=1.0 Grad Abweichung)."""
    if not c or len(c) != 12 or any(x is None for x in c):
        return False
    for i in range(12):
        step = (c[(i+1) % 12] - c[i]) % 360.0
        if not (0.5 < step < 170.0):       # kein Nullschritt, keine Umsortierung
            return False
    if radix:
        for name, idx in (('AC', 0), ('MC', 9)):
            if name in radix:
                d = abs((c[idx] - radix[name] + 180.0) % 360.0 - 180.0)
                if d > 1.0:
                    return False
    return True

def cusps_from_chart_data(path, radix=None, quiet=False):
    """Versucht die 12 Koch-Spitzen aus der chart_data zu lesen. Reihenfolge:
    (1) maschinenlesbare Liste `cusps = [...]` / `'cusps': [...]`,
    (2) Text/Tabelle mit Hausnummer + Zeichen + Grad(+Minute).
    Gibt eine 12er-Liste ekliptikaler Laengen zurueck oder None (dann werden die
    Haus-Durchgaenge sauber ausgeklammert — lieber nichts als falsch)."""
    try:
        txt = open(path, encoding='utf-8').read()
    except OSError:
        return None

    # (1) maschinenlesbare Liste
    # FEHLERKORREKTUR 14.09.2026 (Pruefbericht EA Schritt 1+2, 1.1/5.2):
    # Der Ausdruck war case-sensitiv und fand die VERTRAGSSCHREIBWEISE des
    # Datenblatt-Moduls (`CUSPS = [...]`, gross) nicht. Folge: In jedem
    # Transit-, EA- und Ultimativ-Lauf fielen die Haus-Durchgaenge still aus
    # ("Haus-Durchgaenge: AUSGEKLAMMERT" im Report-Kopf, ohne Ursache).
    m = re.search(r"cusps'?\s*[:=]\s*\[([^\]]+)\]", txt, re.IGNORECASE)
    if m:
        try:
            vals = [float(x) for x in re.findall(r"-?\d+\.?\d*", m.group(1))]
            if _plausible_cusps(vals[:12], radix):
                return [v % 360.0 for v in vals[:12]]
        except ValueError:
            pass

    # (2) Text/Tabelle: Zeile enthaelt Hausnummer + Zeichen + Grad(+Minute)
    zod_rx = "|".join(sorted(ZOD_ALIAS.keys(), key=len, reverse=True))
    num_rx = re.compile(r"(?:haus\s*(\d{1,2})|^\s*\|?\s*(\d{1,2})\s*\.?\s*(?:haus)?\b)",
                        re.IGNORECASE)
    pos_rx = re.compile(r"(?:(" + zod_rx + r")\s*[^0-9\n]{0,6}(\d{1,2})\s*[°º:\s]\s*(\d{1,2})?"
                        # FEHLERKORREKTUR 14.09.2026 (Pruefbericht EA 1.2/5.3):
                        # Die Minutenzeichen-Klasse kannte nur die beiden
                        # Apostrophe. Das PRIME ′ (U+2032), das Datenblatt- und
                        # Klartext-Modul ueberall vorschreiben ("7°06′ Waage"),
                        # war nicht darin — die projekteigene Notation war fuer
                        # diesen Parser unlesbar. ′ ″ ´ ` ergaenzt.
                        r"|(\d{1,2})\s*[°º]\s*(\d{1,2})?\s*['’′″´`\s]*\s*(" + zod_rx + r"))",
                        re.IGNORECASE)
    found = {}
    for line in txt.splitlines():
        low = line.strip()
        if not low or len(low) > 200:
            continue
        nm = num_rx.search(low)
        if not nm:
            continue
        h = int(nm.group(1) or nm.group(2) or 0)
        if not 1 <= h <= 12 or h in found:
            continue
        pm = pos_rx.search(low)
        if not pm:
            continue
        if pm.group(1):
            sign, deg, mnt = pm.group(1), pm.group(2), pm.group(3)
        else:
            sign, deg, mnt = pm.group(6), pm.group(4), pm.group(5)
        sign = ZOD_ALIAS.get(sign.lower())
        if not sign:
            continue
        found[h] = (ZODIAC.index(sign) * 30.0 + float(deg) + float(mnt or 0) / 60.0) % 360.0
    cusps = [found.get(i) for i in range(1, 13)]
    if _plausible_cusps(cusps, radix):
        return cusps
    if not quiet and any(x is not None for x in cusps):
        print(f"[hinweis] Hausspitzen in {path} nicht plausibel/vollstaendig gelesen "
              f"({sum(x is not None for x in cusps)}/12) — Haus-Durchgaenge ausgeklammert.",
              file=sys.stderr)
    return None

# ---------------------------------------------------------------------------
# Transit-Faktoren (Chiron nur wenn Asteroiden-Ephemeride vorhanden)
# ---------------------------------------------------------------------------
def _transiters(mit_mars=False, probe=None):
    """Gibt (transiters, chiron_an, grund) zurueck.

    `probe`: Julianische Tage, an denen Chiron geprueft wird — normalerweise die
    beiden Fensterraender. Vorher wurde an einem festen Datum (01.01.2027)
    geprueft; eine Bereichsluecke der Ephemeride waere damit erst mitten im Lauf
    aufgefallen. `grund` ist im Erfolgsfall das benutzte Verzeichnis, sonst der
    Klartext-Grund fuer die Ausklammerung (wandert in den Report).
    ACHTUNG: Rueckgabe seit 30.07.2026 dreiteilig statt zweiteilig."""
    jds = list(probe) if probe else [swe.julday(2027,1,1,0.0)]
    # EIN Ephemeriden-Modell fuer das ganze Dokument (neu 2026-09-06,
    # Pruefbericht Transit 4.10). Bis dahin liefen die Hauptplaneten auf Moshier
    # (MOSEPH, dateifrei) und Chiron auf der Swiss Ephemeris (SWIEPH). Beide
    # Modelle unterscheiden sich fuer die Langsamen um bis zu einer Bogensekunde
    # — bei Pluto sind das rund 26 Minuten Laufzeit, genug, um einen Exaktpunkt
    # dicht an Mitternacht auf den Nachbartag zu kippen. astro.com rechnet mit
    # der Swiss Ephemeris; liegen deren Dateien vor, rechnet dieser Builder jetzt
    # ebenso. Ohne sie bleibt Moshier der Rueckfall, damit ein Lauf ohne
    # Ephemeridendateien weiter moeglich ist.
    haupt = SWIEPH
    try:
        if ERZWINGE_MOSEPH:                  # 2026-09-19 (F21): --moseph
            raise RuntimeError("--moseph")
        for jd in jds:
            for pl in (swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE,
                       swe.PLUTO, swe.TRUE_NODE):
                swe.calc_ut(jd, pl, SWIEPH)
    except Exception:
        haupt = MOSEPH
    base = ([('Mars',swe.MARS,haupt)] if mit_mars else []) + \
           [('Jupiter',swe.JUPITER,haupt),('Saturn',swe.SATURN,haupt),
            ('Uranus',swe.URANUS,haupt),('Neptun',swe.NEPTUNE,haupt),
            ('Pluto',swe.PLUTO,haupt),('Knoten',swe.TRUE_NODE,haupt)]
    global HAUPT_MODELL
    HAUPT_MODELL = "Swiss Ephemeris" if haupt is SWIEPH else "Moshier"
    if ERZWINGE_MOSEPH:
        # Moshier kennt keine Asteroiden: Chiron liefe sonst auf einem zweiten
        # Modell — genau das, was die Zwei-Modell-Probe ausschliessen soll.
        return base, False, ("--moseph erzwingt die Moshier-Ephemeride fuer alle "
                             "Faktoren; sie kennt keine Asteroiden, darum ohne "
                             "Transit-Chiron (Probelauf, kein Klientendokument)")
    try:
        for jd in jds:
            swe.calc_ut(jd, swe.CHIRON, SWIEPH)
        base.append(('Chiron',swe.CHIRON,SWIEPH))
        return base, True, (EPHE_PFAD or "eingebauter Standardpfad")
    except Exception as e:
        kurz = str(e).split("\n")[0][:160]
        if EPHE_PFAD is None:
            grund = ("keine seas_*.se1 gefunden — Asteroiden-Ephemeride "
                     "installieren oder --ephe <verzeichnis> setzen [%s]" % kurz)
        else:
            grund = ("Ephemeride %s deckt das Fenster nicht [%s]" % (EPHE_PFAD, kurz))
        return base, False, grund

# ---------------------------------------------------------------------------
# Winkel-/Zeit-Helfer
# ---------------------------------------------------------------------------
def quartal_start(d):
    """Erster Tag des Kalenderquartals, in dem d liegt."""
    return date(d.year, ((d.month-1)//3)*3+1, 1)

def plus_quartale(d, n):
    """n Kalenderquartale weiter (n darf negativ sein); immer Monatserster."""
    m = d.month-1 + 3*n
    return date(d.year + m//12, m%12 + 1, 1)

def wrap180(x): return (x+180.0)%360.0-180.0
def orb_for(tlon,rlon,a):
    d=wrap180(tlon-rlon)
    return min(abs(wrap180(d-a)),abs(wrap180(d+a)))
def jd_of(d,h=12.0): return swe.julday(d.year,d.month,d.day,h)
def deg2sign(lon):
    s=int(lon//30)%12; d=lon-30*(lon//30); dd=int(d); mm=int(round((d-dd)*60))
    if mm==60: dd+=1; mm=0
    return f"{ZODIAC[s]} {dd}°{mm:02d}'"
ZEITZONE = None          # None = Weltzeit (UT), wie bis 2026-09-06

def setze_zeitzone(name):
    """Zeitzone fuer die AUSGABE der Exaktdaten setzen (IANA-Name, z. B.
    'Europe/Berlin'). None = Weltzeit.

    Grund (Pruefbericht Transit 2026-09-06, 4.10, Ursache 2): `swe.revjul()`
    liefert den WELTZEIT-Kalendertag. astro.com und jede Klientin lesen den
    ORTSTAG. Faellt ein Exaktpunkt in die letzten Minuten eines UT-Tages, nennt
    der Report deshalb den Vortag — im Pruefall fuenfmal. Die Rechnung war nie
    falsch, nur die Beschriftung.

    Rueckgabe: der gesetzte Name oder None. Ein unbekannter Name ist ein harter
    Fehler; stilles Zurueckfallen auf UT waere genau der Fehler, den diese
    Funktion behebt."""
    global ZEITZONE
    if not name:
        ZEITZONE = None; return None
    if ZoneInfo is None:
        raise RuntimeError("zoneinfo nicht verfuegbar (Python < 3.9) — "
                           "--tz kann nicht benutzt werden.")
    try:
        ZEITZONE = ZoneInfo(name)
    except Exception as e:
        raise ValueError("unbekannte Zeitzone %r (%s). IANA-Name erwartet, "
                         "z. B. Europe/Berlin." % (name, e)) from e
    return name


def d_from_jd(jd):
    """Kalendertag eines julianischen Datums — in ZEITZONE, sonst in Weltzeit."""
    y,m,dd,ut=swe.revjul(jd)
    if ZEITZONE is None:
        return date(y,m,dd)
    st=int(ut); mi=int((ut-st)*60); se=int(round((((ut-st)*60)-mi)*60))
    if se>59: se=59
    if st>23: st=23
    dt=datetime(y,m,dd,st,mi,se,tzinfo=timezone.utc)
    return dt.astimezone(ZEITZONE).date()
def _iso(d): return d.isoformat() if hasattr(d,'isoformat') else d
def _mon(tage): return round(tage/30.4375,1)
SPIEGEL_PAAR = {'DC':'AC','IC':'MC','Suedknoten':'Nordknoten'}
def spiegel_ziele(radix):
    """DC/IC/Suedknoten liefern zu jedem Transit denselben Kontakt wie AC/MC/
    Nordknoten, nur mit gespiegeltem Aspektnamen. Solche Ziele werden markiert
    (Feld `spiegel`) und im Report ausgeblendet — im JSON bleiben sie erhalten."""
    out=set()
    for sec,prim in SPIEGEL_PAAR.items():
        if sec in radix and prim in radix:
            if abs(abs(wrap180(radix[sec]-radix[prim]))-180.0)<0.5:
                out.add(sec)
    return out

def house_of(lon, cusps):
    for i in range(12):
        a=cusps[i]; b=cusps[(i+1)%12]
        if ((lon-a) % 360.0) < ((b-a) % 360.0):
            return i+1
    return 12


def haus_fuehrung(lon, cusps, orb=5.0, schwelle=2.0):
    """Haus eines RADIX-Faktors nach der Grenzlagen-Regel des Datenblatt-Moduls
    (2026-09-19, F20) — dieselbe Regel wie `radix.haus_spalte()`: Steht der
    Faktor hoechstens `orb` Grad VOR der naechsten Spitze, ist das eine
    Grenzlage; bei hoechstens `schwelle` Grad (Schwellenlage) FUEHRT das
    Nebenhaus, sonst das rechnerische Haus.

    Rueckgabe: dict(haus=rechnerisch, nebenhaus=int|None, fuehrend=int,
    stufe='Schwellenlage'|'Grenzlage'|None, abstand=Grad bis zur Spitze|None,
    spalte='12/11' bzw. '7' — fuehrendes Haus vorn, wie in der Staendetabelle)."""
    lon = lon % 360.0
    for k in range(12):
        span = (cusps[(k + 1) % 12] - cusps[k]) % 360.0
        rel = (lon - cusps[k]) % 360.0
        if rel < span:
            haus = k + 1
            bis = span - rel
            if bis > orb:
                return dict(haus=haus, nebenhaus=None, fuehrend=haus, stufe=None,
                            abstand=None, spalte=str(haus))
            neben = haus % 12 + 1
            # Stufe auf dem auf 0,01° gerundeten Abstand — wie radix.haus_spalte(),
            # damit die Angabe mit der Staendetabelle der chart_data uebereinstimmt
            if round(bis, 2) <= schwelle:
                return dict(haus=haus, nebenhaus=neben, fuehrend=neben,
                            stufe='Schwellenlage', abstand=round(bis, 4),
                            spalte=f"{neben}/{haus}")
            return dict(haus=haus, nebenhaus=neben, fuehrend=haus, stufe='Grenzlage',
                        abstand=round(bis, 4), spalte=f"{haus}/{neben}")
    h = house_of(lon, cusps)
    return dict(haus=h, nebenhaus=None, fuehrend=h, stufe=None, abstand=None,
                spalte=str(h))


# ---------------------------------------------------------------------------
# Nulldurchgaenge, Minima, Abschnitte — 2026-09-19 (W1, W3)
# ---------------------------------------------------------------------------
def _ziele(rlon, a):
    """Aspektpunkte auf der Ekliptik: rlon+a und rlon-a (bei 0° und 180° einer)."""
    if a % 180 == 0:
        return [(rlon + a) % 360.0]
    return [(rlon + a) % 360.0, (rlon - a) % 360.0]


def _tagesreihe(pl, flag, d_von, d_bis):
    """[(jd, laenge, geschwindigkeit)] je Kalendertag 12 Uhr UT, d_von..d_bis
    einschliesslich — dasselbe Raster wie die Hauptrechnung (`jd_of`)."""
    out = []
    for i in range((d_bis - d_von).days + 1):
        jd = jd_of(d_von + timedelta(days=i))
        xx, _ = swe.calc_ut(jd, pl, flag)
        out.append((jd, xx[0], xx[3]))
    return out


def _nulldurchgaenge(pl, flag, ziel, reihe):
    """ALLE Zeitpunkte, an denen die vorzeichenbehaftete Differenz Laenge − ziel
    in der Tagesreihe die Null kreuzt (2026-09-19, W1).

    Ein Tagesintervall kommt nur in Frage, wenn |f| an einem seiner Enden
    hoechstens die Tagesbewegung betraegt (Sicherheitsfaktor 1,5, dazu 0,01°);
    sonst kann der Faktor den Punkt in diesem Tag nicht erreichen. Jedes
    Kandidatenintervall wird im STUNDENRASTER abgetastet, jeder
    Vorzeichenwechsel (|f| < 5° auf beiden Seiten, also kein Sprung ueber ±180°)
    auf unter eine Sekunde bisektiert. Das Ergebnis ist dasselbe wie ein
    Stundenraster ueber den ganzen Zeitraum: Zwei Kreuzungen in derselben Stunde
    gaebe es nur bei einer Station genau auf dem Punkt.

    Vorher (bis 2026-09-18) wurden nur Tagesminima des Orbs verfeinert, und
    `refine_min()` gab je Zwei-Tage-Fenster nur die ERSTE Kreuzung zurueck — beim
    pendelnden wahren Knoten ging dadurch eine von drei Kreuzungen verloren.
    Rueckgabe: jd-Liste in zeitlicher Reihenfolge."""
    out = []
    for k in range(len(reihe) - 1):
        j0, l0, s0 = reihe[k]
        j1, l1, s1 = reihe[k + 1]
        f0 = wrap180(l0 - ziel); f1 = wrap180(l1 - ziel)
        grenze = 1.5 * max(abs(s0), abs(s1)) * (j1 - j0) + 0.01
        if abs(f0) > grenze and abs(f1) > grenze:
            continue
        js = [j0 + (j1 - j0) * h / 24.0 for h in range(25)]
        fs = ([f0] + [wrap180(swe.calc_ut(j, pl, flag)[0][0] - ziel) for j in js[1:24]]
              + [f1])
        for h in range(24):
            if (fs[h] < 0) != (fs[h + 1] < 0) and abs(fs[h]) < 5.0 and abs(fs[h + 1]) < 5.0:
                lo, hi = js[h], js[h + 1]
                slo = fs[h] < 0
                for _ in range(16):                  # 1 h / 2**16 << 1 Sekunde
                    m = (lo + hi) / 2.0
                    if (wrap180(swe.calc_ut(m, pl, flag)[0][0] - ziel) < 0) == slo:
                        lo = m
                    else:
                        hi = m
                out.append((lo + hi) / 2.0)
    return out


def _kontakt_kreuzungen(pl, flag, rlon, a, reihe):
    """Nulldurchgaenge eines Kontakts ueber beide Aspektpunkte, zeitlich sortiert."""
    out = []
    for z in _ziele(rlon, a):
        out += _nulldurchgaenge(pl, flag, z, reihe)
    return sorted(out)


def refine_min(pl, flag, rlon, a, jd_lo, jd_hi):
    """Engster Punkt des Aspekts im Fenster [jd_lo, jd_hi] (meist zwei Tage).

    Bis zum 2026-09-06 wurden hier 73 Punkte ueber zwei Tage abgetastet
    (Schrittweite 40 Minuten) und der kleinste ABGETASTETE Orb genommen.
    Lag der wahre Exaktpunkt dicht an Mitternacht, kippte das gemeldete
    Datum auf den Nachbartag — mit wechselndem Vorzeichen, je nachdem,
    welcher Rasterpunkt naeher lag (Pruefbericht Transit 2026-09-06, 4.10,
    Ursache 1; im Pruefall vier von 146 Exaktdaten betroffen).

    Jetzt zweistufig: Kreuzt die vorzeichenbehaftete Winkeldifferenz zum
    Aspektpunkt die Null, wird bis auf rund eine Sekunde bisektiert. Tut
    sie es nicht (Streifkontakt, Stationsnaehe), wird das Minimum von |f|
    per Goldenem Schnitt gesucht statt auf einem festen Raster.

    2026-09-19 (W1): seit 2026-09-19 auf Modulebene statt innerhalb von run()
    (Vorlauf, Fortsetzung und fruehere Durchgaenge brauchen dieselbe Rechnung),
    und die Rueckgabe ist DREITEILIG: (jd, orb, gekreuzt). Nur `gekreuzt=True`
    ist ein Exaktkontakt; ohne Kreuzung ist der Punkt das Minimum einer
    Annaeherung, auch wenn der Orb Bogenminuten betraegt — frueher galt er unter
    0,05° als exakt (Scheinexaktheit, Pruefbericht Transit 3+4 2026-09-18b, 1.5).
    Welche Kreuzungen es insgesamt gibt, sagt `_nulldurchgaenge()`; diese
    Funktion meldet je Fenster nur eine."""
    def calc(jd):
        return swe.calc_ut(jd, pl, flag)[0][0]
    mitte=(jd_lo+jd_hi)/2.0
    l0=calc(mitte)
    ziel=min(((rlon+a)%360.0, (rlon-a)%360.0),
             key=lambda z: abs(wrap180(l0-z)))
    def f(jd):
        return wrap180(calc(jd)-ziel)
    N=48                                   # Vorabtastung, ~1 h bei 2 Tagen
    js=[jd_lo+(jd_hi-jd_lo)*k/float(N) for k in range(N+1)]
    vs=[f(j) for j in js]
    for k in range(N):
        if (vs[k]<0)!=(vs[k+1]<0) and abs(vs[k])<5.0 and abs(vs[k+1])<5.0:
            lo,hi=js[k],js[k+1]; slo=(vs[k]<0)
            for _ in range(40):            # 2 Tage / 2**40 << 1 Sekunde
                m=(lo+hi)/2.0
                if (f(m)<0)==slo: lo=m
                else: hi=m
            jd=(lo+hi)/2.0
            return jd, orb_for(calc(jd),rlon,a), True
    k=min(range(N+1), key=lambda i: abs(vs[i]))
    lo,hi=js[max(0,k-1)],js[min(N,k+1)]
    gr=(5.0**0.5-1.0)/2.0
    for _ in range(60):                    # Goldener Schnitt auf |f|
        m1=hi-gr*(hi-lo); m2=lo+gr*(hi-lo)
        if abs(f(m1))<abs(f(m2)): hi=m2
        else: lo=m1
    jd=(lo+hi)/2.0
    return jd, orb_for(calc(jd),rlon,a), False


def _perioden_idx(orbs, schwelle, von=0, bis=None):
    """Zusammenhaengende Indexbereiche [(a, b)] mit orbs[i] <= schwelle."""
    bis = len(orbs) - 1 if bis is None else bis
    out = []; a = None
    for i in range(von, bis + 1):
        if orbs[i] <= schwelle:
            if a is None:
                a = i
        elif a is not None:
            out.append((a, i - 1)); a = None
    if a is not None:
        out.append((a, bis))
    return out


def _abschnitt(pl, flag, rlon, a, reihe, tag0, i_a, i_b, orb, orb_weit,
               d_von=None, d_bis=None):
    """Kennzahlen eines Kontakts in reihe[i_a..i_b] (2026-09-19, W3).

    reihe  [(jd, laenge, geschw.)] je Tag, Index 0 = Datum tag0.
    Nulldurchgaenge werden einen Tag ueber beide Raender hinaus gesucht und nach
    ORTSDATUM gezaehlt (d_von..d_bis, Vorgabe: die Tage der Indexspanne) — so
    zaehlt eine Kreuzung am Abend des letzten Fenstertags zum Fenster und nicht
    doppelt zur Fortsetzung.
    Rueckgabe: dict(exakt=[date], annaeherung=[(date, orb)], min_orb=Grad,
    min_datum=date, wirkorb=[(date, date)])."""
    n = len(reihe)
    tag = lambda i: tag0 + timedelta(days=i)
    d_von = d_von or tag(i_a)
    d_bis = d_bis or tag(i_b)
    orbs = [orb_for(reihe[i][1], rlon, a) for i in range(i_a, i_b + 1)]
    lo = max(0, i_a - 1); hi = min(n - 1, i_b + 1)
    exakt = sorted(set(d for d in (d_from_jd(j) for j in
                                   _kontakt_kreuzungen(pl, flag, rlon, a, reihe[lo:hi + 1]))
                       if d_von <= d <= d_bis))
    minima = []
    for k, o in enumerate(orbs):
        if o >= orb_weit:
            continue
        i = i_a + k
        j = reihe[i][0]
        links = (orb_for(reihe[i - 1][1], rlon, a) if i >= 1 else
                 orb_for(swe.calc_ut(j - 1.0, pl, flag)[0][0], rlon, a))
        rechts = (orb_for(reihe[i + 1][1], rlon, a) if i + 1 < n else
                  orb_for(swe.calc_ut(j + 1.0, pl, flag)[0][0], rlon, a))
        if o <= links and o <= rechts:
            minima.append(refine_min(pl, flag, rlon, a, j - 1.0, j + 1.0))
    ann = {}
    kand = [(o, tag(i_a + k)) for k, o in enumerate(orbs)] + [(0.0, d) for d in exakt]
    for jd, om, gek in minima:
        d = d_from_jd(jd)
        if not (d_von <= d <= d_bis):
            continue
        kand.append((om, d))
        if not gek and om <= ANNAEHERUNG_ORB and (d not in ann or om < ann[d]):
            ann[d] = om
    mo, md = min(kand)
    wirk = [(tag(i_a + x), tag(i_a + y)) for x, y in _perioden_idx(orbs, orb)]
    return dict(exakt=exakt, annaeherung=sorted(ann.items()), min_orb=mo,
                min_datum=md, wirkorb=wirk)


def _alter_voll(d, geb):
    """Vollendete Lebensjahre am Datum d (Kalenderrechnung; geb = Geburtstag)."""
    if geb is None:
        return None
    return d.year - geb.year - ((d.month, d.day) < (geb.month, geb.day))

# ---------------------------------------------------------------------------
# Hauptrechnung
# ---------------------------------------------------------------------------
def run(radix, start=None, months=24, primary_extra=None, orb=ORB, orb_weit=ORB_WEIT,
        lookback_months=LOOKBACK_M, cusps=None, asof=None, lang_tage=LANG_TAGE,
        mit_mars=False, ohne_chiron=False, tz=None, jd_geburt=None, moseph=False,
        fortsetzung_monate=FORTSETZUNG_MONATE):
    """radix: {Name: ekl. Laenge}. start: date (Default heute). months: Fensterlaenge.
    primary_extra: zusaetzliche Radix-Ziele neben den persoenlichen Punkten.
    lookback_months: Rueckblick VOR dem Start (fuer echte Exaktdaten auslaufender
    Kontakte im Jetzt-Teil). cusps: 12 Koch-Spitzen (optional, fuer Haus-Durchgaenge).
    asof: Stichtag der Momentaufnahme (Default = start).

    Seit 2026-09-19:
    jd_geburt  Geburtszeitpunkt als julianisches Datum in UT (CLI: --geburt).
               Liefert das Lebensalter der frueheren Durchgaenge und begrenzt deren
               Rueckrechnung auf die Geburt; ohne ihn Daten ohne Alter, pauschal
               FRUEHER_OHNE_GEBURT_JAHRE zurueck (Report-Hinweis).
    moseph     Moshier-Ephemeride fuer ALLE Faktoren erzwingen (CLI: --moseph),
               zwangslaeufig ohne Transit-Chiron — fuer die Zwei-Modell-Probe.
    fortsetzung_monate  Rechenhorizont nach dem Fenster (Vorgabe 36).

    `exakt` enthaelt nur echte Nulldurchgaenge; Minima ohne Kreuzung stehen in
    `annaeherung`. Jedes Ereignis traegt ausserdem `vorlauf` (Passage begann vor
    dem Rueckblick), `fortsetzung` (Passage laeuft nach dem Fenster weiter) und
    die Sammelfelder `exakt_gesamt`, `wirkorb_von_gesamt`, `wirkorb_bis_gesamt`;
    `fruehere_durchgaenge` fuehrt je Wirkorb-Kontakt der langsamen Transiter die
    frueheren Durchgaenge mit Datum und Alter. Schema:
    log/SCHNITTSTELLE_events_json.md des Wartungslaufs 2026-09-19.

    EIN KONTAKT, MEHRERE EINTRAEGE (2026-09-23, Pruefbericht Transit 1+2 vom
    22.09.c, Klasse 1 Nr. 4): `events` fuehrt je PASSAGE einen Eintrag. Liegen
    zwei Perioden im Erfassungsorb weiter als _passage_luecke() auseinander (Mars
    150, sonst 210 Tage), sind es zwei Eintraege mit demselben Schluessel
    (transit, ziel, aspekt). Einer davon kann den Wirkorb nie erreichen:
    im_wirkorb=False, `exakt` und `wirkorb_perioden` leer — eine Annaeherung, kein
    Fehler. Wer je Kontakt gruppiert (Dichte, Zeitleiste, Register), sammelt ALLE
    Eintraege eines Schluessels und rechnet mit `wirkorb_perioden`; ein dict ueber
    den Schluessel behaelt sonst den zuletzt gelesenen — ein Lauf setzte so ein
    Kapitel auf null Tage."""
    global ERZWINGE_MOSEPH
    ERZWINGE_MOSEPH = bool(moseph)           # 2026-09-19 (F21)
    if tz is not None:
        setze_zeitzone(tz)
    if start is None:
        start = date.today()
    if asof is None:
        asof = start
    orb_weit = max(orb, orb_weit)
    # HAUSSTIL 2026-07-27 (gemeinsam festgelegt): Die Quartale sind
    # KALENDERQUARTALE (Jan-Mrz, Apr-Jun, Jul-Sep, Okt-Dez), nicht acht
    # Dreimonatsbloecke ab dem Erstellungstag. Q1 ist also das Kalenderquartal,
    # in dem das Horoskop entsteht; das Fenster beginnt an dessen erstem Tag.
    # Der Stichtag (asof) bleibt der tatsaechliche Erstellungstag und liegt
    # damit meist mitten in Q1 — genau das soll die Uhr auch zeigen.
    # Grund: die Quartalskapitel decken sich so mit den Zeitraeumen, in denen
    # Klient und Therapeut ohnehin denken; vorher fielen sie auf krumme
    # Stichtags-Vielfache.
    n_q   = max(1, int(round(months/3.0)))
    start = quartal_start(start)
    qb    = [plus_quartale(start, k) for k in range(n_q+1)]
    end   = qb[-1] - timedelta(days=1)
    t0    = plus_quartale(start, -max(1, int(round(lookback_months/3.0))))
    ndays = (end-t0).days
    # Namensprobe der zusaetzlichen Ziele (Pruefbericht Transit 2026-09-06, 1.2).
    # Bis dahin wurde ein unbekannter Name STILL verworfen; im Pruefall fielen
    # dadurch zwei Langlaeufer von 20 und 17 Monaten aus der primaeren Auswahl,
    # weil `Knoten` uebergeben wurde, das Radix-Ziel aber `Nordknoten` heisst.
    # REPARATUR 2026-09-18: Altnamen der Knotenachse werden auf den Vertragsnamen
    # gezogen, statt einen Abbruch auszuloesen (s. Kommentar bei NAME_MAP).
    primary_extra = [ALIAS_ZIEL.get(x, x) for x in (primary_extra or [])]
    unbekannt = [x for x in primary_extra if x not in radix]
    if unbekannt:
        raise ValueError(
            "unbekannte primaere Ziele: %s\n"
            "  Erlaubt sind die Namen der Radix-Punkte: %s\n"
            "  Haeufige Verwechslung: der Mondknoten heisst hier `Mondknoten` "
            "(Vertragsname des Datenblatt-Moduls); `Knoten` und `Nordknoten` "
            "werden still darauf abgebildet." % (", ".join(unbekannt),
                                                 ", ".join(sorted(radix))))
    primary = set(PERSONAL) | set(primary_extra or [])
    spiegel = spiegel_ziele(radix)
    transiters, chiron_on, chiron_info = _transiters(
        mit_mars, probe=(swe.julday(t0.year, t0.month, t0.day, 0.0),
                         swe.julday(end.year, end.month, end.day, 0.0)))
    # Chiron-Pflicht (Pruefbericht Transit 2026-09-06, 1.1). Vorher lief ein
    # Lauf ohne Asteroiden-Ephemeride mit einer blossen Hinweiszeile durch und
    # verlor im Pruefall 27 Kontakte, darunter den am Stichtag engsten. Wer
    # bewusst ohne Chiron rechnen will, sagt es jetzt ausdruecklich.
    if not chiron_on and not ohne_chiron and not ERZWINGE_MOSEPH:
        raise RuntimeError(
            "Transit-Chiron nicht rechenbar: %s\n"
            "  Behebung:  pip install flatlib --no-deps --break-system-packages\n"
            "             danach --ephe <.../flatlib/resources/swefiles> setzen,\n"
            "             falls die Autosuche das Verzeichnis nicht findet.\n"
            "  Bewusst ohne Chiron rechnen: ohne_chiron=True bzw. --ohne-chiron."
            % chiron_info)
    i_asof = max(0, min(ndays, (asof-t0).days))

    def q_of(d):
        """Quartal 1..n_q; 0 = vor dem Fenster (Rueckblick)."""
        if d < start: return 0
        for k in range(n_q):
            if qb[k] <= d < qb[k+1]: return k+1
        return n_q

    def calc(pl, jd, flag):
        xx,_=swe.calc_ut(jd, pl, flag); return xx[0], xx[3]

    # --- Tages-Sampling ueber [t0, end] --------------------------------------
    samples={}
    for tname,pl,flag in transiters:
        arr=[]
        for i in range(ndays+1):
            jd=jd_of(t0+timedelta(days=i)); lon,sp=calc(pl,jd,flag)
            arr.append((i,jd,lon,sp))
        samples[tname]=arr
    day = lambda i: t0+timedelta(days=i)

    # 2026-09-19 (W1): refine_min() steht seither auf Modulebene (dreiteilige
    # Rueckgabe mit `gekreuzt`). Dazu je ein Tag jenseits beider Raender: fuer
    # die Suche der Nulldurchgaenge bis an den Rand und fuer die Randprobe der
    # Minima (ein Randpunkt ist nur ein Minimum, wenn der Orb dahinter steigt).
    rand_vor={}; rand_nach={}
    for tname,pl,flag in transiters:
        jv=jd_of(t0-timedelta(days=1)); jn=jd_of(end+timedelta(days=1))
        lv,sv=calc(pl,jv,flag); ln,sn=calc(pl,jn,flag)
        rand_vor[tname]=(jv,lv,sv); rand_nach[tname]=(jn,ln,sn)

    def refine_cross(pl,flag,jd_lo,jd_hi,fn):
        """Bisektion auf ~1h fuer den Zeitpunkt, an dem fn(lon) das Vorzeichen wechselt."""
        lo,hi=jd_lo,jd_hi; s0=fn(calc(pl,lo,flag)[0])
        for _ in range(12):
            mid=(lo+hi)/2.0
            if fn(calc(pl,mid,flag)[0])==s0: lo=mid
            else: hi=mid
        return hi

    # --- Kontakte: lokale Minima der Orb-Funktion (< orb_weit) ---------------
    groups={}; orbcache={}
    for tname,pl,flag in transiters:
        arr=samples[tname]; n=len(arr)
        for rname,rlon in radix.items():
            asp=dict(ASPECTS)
            if tname in SLOW_QUINCUNX: asp['Quincunx']=150
            for aname,a in asp.items():
                orbs=[orb_for(lon,rlon,a) for (_,_,lon,_) in arr]
                if min(orbs) >= orb_weit:
                    continue
                orbcache[(tname,rname,aname)]=orbs
                for i in range(n):
                    left = orbs[i-1] if i>0 else 1e9
                    right= orbs[i+1] if i<n-1 else 1e9
                    if orbs[i]<orb_weit and orbs[i]<=left and orbs[i]<=right:
                        lo=arr[max(0,i-1)][1]; hi=arr[min(n-1,i+1)][1]
                        jd_ex,o_ex,gek=refine_min(pl,flag,rlon,a,lo,hi)
                        # 2026-09-19 (W1): Randpunkt nur dann ein echtes Minimum,
                        # wenn der Orb jenseits des Randes nicht weiter faellt.
                        echt=True
                        if i==0 or i==n-1:
                            rv=(rand_vor if i==0 else rand_nach)[tname]
                            echt=(orb_for(rv[1],rlon,a)>=orbs[i])
                        groups.setdefault((tname,rname,aname),[]).append(
                            (jd_ex,o_ex,gek,echt))

    # --- 2026-09-19 (W1): alle Nulldurchgaenge je Kontakt ------------------
    # Stundenraster + Bisektion ueber das ganze Tagesraster (samt je einem Tag
    # jenseits der Raender); nur diese Zeitpunkte gelten als exakt.
    kreuz={}
    for tname,pl,flag in transiters:
        reihe=([rand_vor[tname]] + [(jd,lon,sp) for (_,jd,lon,sp) in samples[tname]]
               + [rand_nach[tname]])
        for key in orbcache:
            if key[0]==tname:
                kreuz[key]=_kontakt_kreuzungen(pl,flag,radix[key[1]],WINKEL[key[2]],reihe)

    def perioden(orbs, schwelle):
        """zusammenhaengende Tagesbereiche mit orb <= schwelle -> [(von,bis)] als date."""
        out=[]; run_start=None
        for i,o in enumerate(orbs):
            if o<=schwelle and run_start is None: run_start=i
            elif o>schwelle and run_start is not None:
                out.append((day(run_start), day(i-1))); run_start=None
        if run_start is not None: out.append((day(run_start), day(len(orbs)-1)))
        return out

    events=[]; _intern=[]                 # _intern[i]: Rechendaten zu events[i]
    for (tname,rname,aname),lst in groups.items():
        # Luecke, ab der zwei Orb-Perioden als getrennte Durchgaenge gelten (nicht als
        # Retro-Serie eines Kontakts): Mars kommt binnen eines Jahres wieder, die
        # langsamen nicht — ihre Dreifachkontakte liegen bis zu ~5 Monate auseinander.
        PASSAGE_LUECKE = _passage_luecke(tname)   # 150 Mars, sonst 210 (2026-09-19 zentral)
        lst.sort()
        orbs=orbcache[(tname,rname,aname)]
        p_wirk=perioden(orbs, orb); p_weit=perioden(orbs, orb_weit)
        # Passagen bilden: weite Perioden mit Luecke <= PASSAGE_LUECKE gehoeren zusammen
        passagen=[]
        for a,b in (p_weit or [(d_from_jd(lst[0][0]),d_from_jd(lst[-1][0]))]):
            if passagen and (a-passagen[-1][1]).days<=PASSAGE_LUECKE:
                passagen[-1]=(passagen[-1][0],b)
            else:
                passagen.append((a,b))
        for pa,pb in passagen:
            sel=[m for m in lst if pa<=d_from_jd(m[0])<=pb]
            i0=max(0,(pa-t0).days); i1=min(len(orbs)-1,(pb-t0).days)
            # 2026-09-19 (W1): exakt = Nulldurchgang (kreuz), nicht mehr jedes
            # Minimum unter 0,05°. Minima ohne Kreuzung darunter -> annaeherung.
            kr=[jd for jd in kreuz.get((tname,rname,aname),[]) if pa<=d_from_jd(jd)<=pb]
            exacts=sorted(set(d_from_jd(jd) for jd in kr))
            mino=min([m[1] for m in sel] + orbs[i0:i1+1] + ([0.0] if kr else []))
            w=[(x,y) for x,y in p_wirk if x>=pa and y<=pb]
            ann={}
            for jd,o,gek,echt in sel:
                if not gek and echt and o<=ANNAEHERUNG_ORB:
                    dd=d_from_jd(jd)
                    if dd not in ann or o<ann[dd]: ann[dd]=o
            eng   =[(d_from_jd(jd),round(o,3)) for jd,o,_,_ in sel
                    if ANNAEHERUNG_ORB<o<=FAST_EXAKT_ORB]
            # Engster Orb NUR im Fenster [start, end] (None: Passage liegt ganz
            # im Rueckblick) — die Passagen-Zahl min_orb_grad kann im Rueckblick
            # liegen und stand dann als "streift 0.0°" im Quartal (W45).
            j0=max(i0,(start-t0).days)
            mf=(min(orbs[j0:i1+1] + [m[1] for m in sel if start<=d_from_jd(m[0])<=end]
                    + ([0.0] if any(start<=d<=end for d in exacts) else []))
                if j0<=i1 else None)
            win_from,win_to = (w[0][0],w[-1][1]) if w else (pa,pb)
            ex_im_fenster=[d for d in exacts if start<=d<=end]
            ex_vor_start =[d for d in exacts if d<start]
            qs=sorted(set(q_of(d) for d in ex_im_fenster))
            if not qs:
                qs=[q_of(win_from if win_from>=start else start)] if win_to>=start else [0]
            dauer=(win_to-win_from).days+1
            events.append(dict(transit=tname,ziel=rname,aspekt=aname,
                exakt=[d.isoformat() for d in exacts],
                exakt_im_fenster=[d.isoformat() for d in ex_im_fenster],
                exakt_vor_start=[d.isoformat() for d in ex_vor_start],
                fast_exakt=[[d.isoformat(),o] for d,o in eng],
                min_orb_grad=round(mino,3), im_wirkorb=(mino<=orb),
                fenster_von=win_from.isoformat(), fenster_bis=win_to.isoformat(),
                weit_von=pa.isoformat(), weit_bis=pb.isoformat(),
                dauer_tage=dauer, dauer_monate=_mon(dauer),
                perioden=[[a.isoformat(),b.isoformat()] for a,b in (w or [(pa,pb)])],
                kontakte=len(exacts), mehrfach=(len(exacts)>=2),
                quartale=qs, primaer=(rname in primary), spiegel=(rname in spiegel),
                wird_exakt=bool(ex_im_fenster),
                # 2026-09-19 — neue Felder, Schema s. run()-Docstring:
                annaeherung=[[d.isoformat(),round(o,4)] for d,o in sorted(ann.items())],
                wirkorb_perioden=[[x.isoformat(),y.isoformat()] for x,y in w],
                min_orb_im_fenster=(round(mf,3) if mf is not None else None),
                wirkorb_im_fenster=bool(mf is not None and mf<=orb),
                orb_stichtag=round(orbs[i_asof],4),
                selbst_transit=ist_selbst_transit(tname,rname)))
            _intern.append(dict(key=(tname,rname,aname),sel=sel,kr=kr,i0=i0,i1=i1,
                                w=w,pa=pa,pb=pb))

    # --- Stationen (nahe eines Radix-Punkts), stuendlich verfeinert ----------
    stations=[]
    for tname,pl,flag in transiters:
        if tname=='Knoten': continue
        arr=samples[tname]
        for i in range(1,len(arr)):
            if (arr[i-1][3]<0)!=(arr[i][3]<0):
                # Vorzeichenwechsel der Geschwindigkeit: Bisektion ueber speed
                lo,hi=arr[i-1][1],arr[i][1]; s0=calc(pl,lo,flag)[1]<0
                for _ in range(12):
                    mid=(lo+hi)/2.0
                    if (calc(pl,mid,flag)[1]<0)==s0: lo=mid
                    else: hi=mid
                jd=hi; d=d_from_jd(jd); lon=calc(pl,jd,flag)[0]
                near=[]
                for rn,rl in radix.items():
                    asp=dict(ASPECTS)
                    if tname in SLOW_QUINCUNX: asp['Quincunx']=150
                    for an,av in asp.items():
                        o=orb_for(lon,rl,av)
                        if o<=orb_weit:
                            near.append(dict(ziel=rn,aspekt=an,orb=round(o,2),
                                             primaer=(rn in primary),
                                             spiegel=(rn in spiegel)))
                if any(not x['spiegel'] for x in near):
                    stations.append(dict(transit=tname,datum=d.isoformat(),
                        stand=deg2sign(lon),
                        richtung=('wird rueckl.' if calc(pl,jd+2,flag)[1]<0 else 'wird direkt'),
                        nahe=[f"{x['aspekt']} {x['ziel']}" for x in near if not x['spiegel']],
                        nahe_detail=near, quartal=q_of(d), vor_start=(d<start)))

    # --- Zeichen-Ingresse (stuendlich verfeinert) + Zeichen-Aufenthalte ------
    ingress=[]; zeichenaufenthalt=[]
    for tname,pl,flag in transiters:
        arr=samples[tname]; cur=int(arr[0][2]//30)%12; seg_start=0
        for i in range(1,len(arr)):
            s1=int(arr[i][2]//30)%12
            if s1!=cur:
                jd=refine_cross(pl,flag,arr[i-1][1],arr[i][1],
                                lambda L,_c=cur: int(L//30)%12==_c)
                d=d_from_jd(jd)
                if d>=start:
                    ingress.append(dict(transit=tname,datum=d.isoformat(),
                        von=ZODIAC[cur],nach=ZODIAC[s1],quartal=q_of(d)))
                zeichenaufenthalt.append(dict(transit=tname,zeichen=ZODIAC[cur],
                    von=_iso(max(day(seg_start),start)),bis=d.isoformat(),
                    tage=(d-max(day(seg_start),start)).days))
                cur=s1; seg_start=i
        zeichenaufenthalt.append(dict(transit=tname,zeichen=ZODIAC[cur],
            von=_iso(max(day(seg_start),start)),bis=end.isoformat(),
            tage=(end-max(day(seg_start),start)).days))
    zeichenaufenthalt=[z for z in zeichenaufenthalt if z['tage']>0]

    # --- Haus-Durchgaenge (nur wenn Koch-Spitzen vorliegen) ------------------
    hausdurchgang=[]
    if cusps:
        for tname,pl,flag in transiters:
            arr=samples[tname]
            cur=house_of(arr[0][2],cusps); seg_start=0
            for i in range(1,len(arr)):
                h=house_of(arr[i][2],cusps)
                if h!=cur:
                    jd=refine_cross(pl,flag,arr[i-1][1],arr[i][1],
                                    lambda L,_c=cur: house_of(L,cusps)==_c)
                    d=d_from_jd(jd); v=max(day(seg_start),start)
                    if (d-v).days>0:
                        hausdurchgang.append(dict(transit=tname,haus=cur,
                            von=_iso(v),bis=d.isoformat(),tage=(d-v).days,
                            angeschnitten=(day(seg_start)<start)))
                    cur=h; seg_start=i
            v=max(day(seg_start),start)
            if (end-v).days>0:
                hausdurchgang.append(dict(transit=tname,haus=cur,von=_iso(v),
                    bis=end.isoformat(),tage=(end-v).days,
                    angeschnitten=(day(seg_start)<start),laeuft_weiter=True))

    # --- 2026-09-19 (W3): Vorlauf, Fortsetzung, fruehere Durchgaenge -------
    # Der Rechenrahmen [Rueckblick-Anfang, Fensterende] ist keine Erzaehlgrenze.
    # (a) Vorlauf: Stand ein Kontakt beim Rueckblick-Anfang schon im Orb (oder
    #     binnen der Passagen-Luecke davor), wird seine Passage rueckwaerts bis
    #     zum tatsaechlichen Eintritt gerechnet -> e['vorlauf'] (vorher nannte der
    #     Report den Rueckblick-Anfang als Beginn, ohne Kennzeichen).
    # (b) Fortsetzung: Laeuft die Passage am Fensterende noch (oder setzt binnen
    #     der Luecke wieder ein), bis zum endgueltigen Austritt, hoechstens
    #     `fortsetzung_monate` -> e['fortsetzung'].
    # (c) Fruehere Durchgaenge je Wirkorb-Kontakt der langsamen Transiter (ohne
    #     Mars) bis zur Geburt, mit Alter -> res['fruehere_durchgaenge'].
    tr_pl={t:(pl,flag) for t,pl,flag in transiters}
    ext_end=(plus_quartale(qb[-1], max(1,int(round(fortsetzung_monate/3.0))))
             - timedelta(days=1))
    geb=d_from_jd(jd_geburt) if jd_geburt is not None else None
    hist_start=min(geb if geb is not None else
                   date(t0.year-FRUEHER_OHNE_GEBURT_JAHRE, t0.month, 1), t0)
    _ext={}; _hist={}; _o_hist={}
    def ext_reihe(tn):                       # Index 0 = Fensterende
        if tn not in _ext:
            pl,flag=tr_pl[tn]; _ext[tn]=_tagesreihe(pl,flag,end,ext_end)
        return _ext[tn]
    def hist_orbs(key):                      # Index 0 = hist_start, letzter = t0
        if key not in _o_hist:
            if key[0] not in _hist:
                pl,flag=tr_pl[key[0]]; _hist[key[0]]=_tagesreihe(pl,flag,hist_start,t0)
            rl=radix[key[1]]; w_=WINKEL[key[2]]
            _o_hist[key]=[orb_for(x[1],rl,w_) for x in _hist[key[0]]]
        return _hist[key[0]], _o_hist[key]
    def _pp(ps):
        return [[x.isoformat(),y.isoformat()] for x,y in ps]

    erstes={}                                # je Kontakt die frueheste Passage
    for idx,e in enumerate(events):
        k=(e['transit'],e['ziel'],e['aspekt'])
        if k not in erstes or e['weit_von']<events[erstes[k]]['weit_von']:
            erstes[k]=idx
    for idx,e in enumerate(events):
        e['vorlauf']=None; e['fortsetzung']=None
        if e['spiegel']:
            continue                         # Spiegelziele doppeln AC/MC/Knoten
        tn,rn,an=_intern[idx]['key']; pl,flag=tr_pl[tn]
        rl=radix[rn]; w_=WINKEL[an]; L=_passage_luecke(tn)
        wb=date.fromisoformat(e['weit_bis'])
        if (end-wb).days<=L:                                   # (b)
            R=ext_reihe(tn); o_ext=[orb_for(x[1],rl,w_) for x in R]
            cur=(wb-end).days; i_last=None
            for ia,ib in _perioden_idx(o_ext, orb_weit, von=1):
                if ia-cur<=L: cur=ib; i_last=ib
                else: break
            if i_last is not None:
                s=_abschnitt(pl,flag,rl,w_,R,end,1,i_last,orb,orb_weit)
                e['fortsetzung']=dict(
                    exakt=[d.isoformat() for d in s['exakt']],
                    annaeherung=[[d.isoformat(),round(o,4)] for d,o in s['annaeherung']],
                    min_orb_grad=round(s['min_orb'],3),
                    min_orb_datum=s['min_datum'].isoformat(),
                    wirkorb_perioden=_pp(s['wirkorb']),
                    wirkorb_bis=(s['wirkorb'][-1][1].isoformat() if s['wirkorb'] else None),
                    bis=(end+timedelta(days=i_last)).isoformat(),
                    im_orb_am_fensterende=(wb==end),
                    horizont=ext_end.isoformat(),
                    horizont_erreicht=(i_last==len(R)-1))
        wv=date.fromisoformat(e['weit_von'])
        if idx==erstes[(tn,rn,an)] and (wv-t0).days<=L and hist_start<t0:   # (a)
            H,o_h=hist_orbs((tn,rn,an)); nh=len(H)
            cur=(wv-hist_start).days; i_first=None
            for ia,ib in reversed(_perioden_idx(o_h, orb_weit, von=0, bis=nh-2)):
                if cur-ib<=L: cur=ia; i_first=ia
                else: break
            if i_first is not None:
                s=_abschnitt(pl,flag,rl,w_,H,hist_start,i_first,nh-2,orb,orb_weit)
                e['vorlauf']=dict(
                    von=(hist_start+timedelta(days=i_first)).isoformat(),
                    wirkorb_von=(s['wirkorb'][0][0].isoformat() if s['wirkorb'] else None),
                    wirkorb_perioden=_pp(s['wirkorb']),
                    exakt=[d.isoformat() for d in s['exakt']],
                    annaeherung=[[d.isoformat(),round(o,4)] for d,o in s['annaeherung']],
                    min_orb_grad=round(s['min_orb'],3),
                    min_orb_datum=s['min_datum'].isoformat(),
                    horizont_erreicht=(i_first==0))

    def _wirk_gesamt(e):
        """Wirkorb-Perioden der ganzen Passage (Vorlauf + Rechenzeitraum +
        Fortsetzung), an den Nahtstellen zusammengezogen."""
        v=e.get('vorlauf'); f=e.get('fortsetzung')
        ps=[(date.fromisoformat(a),date.fromisoformat(b)) for a,b in
            ((v['wirkorb_perioden'] if v else []) + e['wirkorb_perioden']
             + (f['wirkorb_perioden'] if f else []))]
        out=[]
        for a,b in ps:
            if out and (a-out[-1][1]).days<=1: out[-1]=(out[-1][0],max(b,out[-1][1]))
            else: out.append((a,b))
        return out
    for e in events:
        v=e['vorlauf']; f=e['fortsetzung']
        e['beginn_abgeschnitten']=v is not None
        e['exakt_nach_fenster']=list(f['exakt']) if f else []
        e['exakt_gesamt']=sorted(set((v['exakt'] if v else []) + e['exakt']
                                     + (f['exakt'] if f else [])))
        wg=_wirk_gesamt(e)
        e['wirkorb_von_gesamt']=wg[0][0].isoformat() if wg else None
        e['wirkorb_bis_gesamt']=wg[-1][1].isoformat() if wg else None

    def _ist_langlaeufer(e):
        """Kriterium der LANGLAEUFER-Liste (unten), zugleich Grundlage von (c)."""
        if not e['im_wirkorb'] or e['spiegel'] or e['transit']=='Mars': return False
        if e['fenster_bis']<start.isoformat(): return False
        return (e['dauer_tage']>=lang_tage) or e['mehrfach'] or (e['transit'] in AEUSSERE)

    # (c) fuer jeden Langlaeufer und jeden Selbst-Transit (Rang 1, W55) mit
    # Wirkorb im Fenster — dieselbe Menge in Report und JSON.
    fruehere=[]
    fr_keys={(e['transit'],e['ziel'],e['aspekt']) for e in events
             if _ist_langlaeufer(e) or (e['selbst_transit'] and not e['spiegel']
                                         and e['transit']!='Mars'
                                         and e['wirkorb_im_fenster'])}
    reihenfolge=[t for t,_,_ in transiters]
    for k in sorted(fr_keys, key=lambda k:(0 if k[1] in primary else 1,
                                           reihenfolge.index(k[0]), k[1], k[2])):
        tn,rn,an=k; pl,flag=tr_pl[tn]; rl=radix[rn]; w_=WINKEL[an]
        L=_passage_luecke(tn); dg=[]
        if hist_start<t0:
            H,o_h=hist_orbs(k); nh=len(H)
            e0=events[erstes[k]]
            grenze=((date.fromisoformat(e0['vorlauf']['von'])-hist_start).days-1
                    if e0['vorlauf'] else nh-2)
            pas=[]
            for ia,ib in (_perioden_idx(o_h, orb_weit, von=0, bis=grenze)
                          if grenze>=0 else []):
                if pas and ia-pas[-1][1]<=L: pas[-1]=(pas[-1][0],ib)
                else: pas.append((ia,ib))
            for ia,ib in reversed(pas):                         # juengster zuerst
                if min(o_h[ia:ib+1])>orb+0.25:
                    continue                                    # nie nahe am Wirkorb
                if (ia==0 and geb is not None and an=='Konjunktion'
                        and ist_selbst_transit(tn,rn)):
                    continue            # Rueckkehr-Konjunktion bei der Geburt = Radix selbst
                s=_abschnitt(pl,flag,rl,w_,H,hist_start,ia,ib,orb,orb_weit)
                if s['min_orb']>orb:
                    continue                                    # kein Wirkorb-Durchgang
                dg.append(dict(nr=len(dg)+1,
                    von=(hist_start+timedelta(days=ia)).isoformat(),
                    bis=(hist_start+timedelta(days=ib)).isoformat(),
                    wirkorb_von=(s['wirkorb'][0][0].isoformat() if s['wirkorb'] else None),
                    wirkorb_bis=(s['wirkorb'][-1][1].isoformat() if s['wirkorb'] else None),
                    exakt=[dict(datum=d.isoformat(),alter=_alter_voll(d,geb))
                           for d in s['exakt']],
                    annaeherung=[dict(datum=d.isoformat(),orb_grad=round(o,4),
                                      alter=_alter_voll(d,geb))
                                 for d,o in s['annaeherung']],
                    min_orb_grad=round(s['min_orb'],3),
                    min_orb_datum=s['min_datum'].isoformat(),
                    min_orb_alter=_alter_voll(s['min_datum'],geb),
                    ab_rechenbeginn=(ia==0)))
        fruehere.append(dict(transit=tn,aspekt=an,ziel=rn,primaer=(rn in primary),
                             selbst_transit=ist_selbst_transit(tn,rn),durchgaenge=dg))

    # --- JETZT: Momentaufnahme zum Stichtag ---------------------------------
    _idx={id(e):i for i,e in enumerate(events)}
    ev_by_key={}
    for e in events:
        ev_by_key.setdefault((e['transit'],e['ziel'],e['aspekt']),[]).append(e)
    def passage_am(key, tag):
        """Die Passage, die den Stichtag enthaelt; sonst die zeitlich naechste."""
        cand=ev_by_key.get(key)
        if not cand: return None
        iso=tag.isoformat()
        for e in cand:
            if e['weit_von']<=iso<=e['weit_bis']: return e
        return min(cand, key=lambda e: min(abs((date.fromisoformat(e['weit_von'])-tag).days),
                                           abs((date.fromisoformat(e['weit_bis'])-tag).days)))
    im_orb=[]
    for (tname,rname,aname),orbs in orbcache.items():
        o_now=orbs[i_asof]
        if o_now>orb_weit: continue
        lo=orbs[max(0,i_asof-2)]; hi=orbs[min(len(orbs)-1,i_asof+2)]
        if   hi<lo-0.002: richtung='zulaufend'
        elif hi>lo+0.002: richtung='auslaufend'
        else:             richtung='stehend'
        e=passage_am((tname,rname,aname), asof)
        ex=[date.fromisoformat(x) for x in (e['exakt'] if e else [])]
        letzte=[d for d in ex if d<=asof]; naechste=[d for d in ex if d>asof]
        p=(e['perioden'][-1] if e and e['perioden'] else None)
        # 2026-09-19 (W45): Die Zeile mischte den Stichtags-Orb mit dem
        # Passagen-Minimum und dem Wirkorb-Ende — beide lagen oft im Rueckblick
        # ("zulaufend ... wird nicht exakt (min X°) | bis <Rueckblick-Datum>").
        # Jetzt je Groesse ein eigenes Feld, bezogen auf den Stichtag und ueber
        # Vorlauf und Fortsetzung hinweg.
        wj=wk=wv=None; ex_k=[]; ex_g=[]; ann_k=[]; m_ab=m_bis=None
        if e:
            it=_intern[_idx[id(e)]]; iso=asof.isoformat()
            wg=_wirk_gesamt(e)
            wj=next(([x.isoformat(),y.isoformat()] for x,y in wg if x<=asof<=y),None)
            wk=next(([x.isoformat(),y.isoformat()] for x,y in wg if x>asof),None)
            wv=([[x.isoformat(),y.isoformat()] for x,y in wg if y<asof] or [None])[-1]
            ex_k=[d for d in e['exakt_gesamt'] if d>iso]
            ex_g=[d for d in e['exakt_gesamt'] if d<=iso]
            vl=e['vorlauf']; fs=e['fortsetzung']
            ann_k=[q for q in (e['annaeherung'] + (fs['annaeherung'] if fs else []))
                   if q[0]>iso]
            c=([(orbs[i],day(i)) for i in range(max(i_asof,it['i0']),it['i1']+1)]
               + [(m[1],d_from_jd(m[0])) for m in it['sel'] if d_from_jd(m[0])>=asof]
               + [(0.0,date.fromisoformat(d)) for d in ex_k])
            if fs: c.append((fs['min_orb_grad'],date.fromisoformat(fs['min_orb_datum'])))
            m_ab=min(c) if c else None
            c=([(orbs[i],day(i)) for i in range(it['i0'],min(i_asof,it['i1']+1))]
               + [(m[1],d_from_jd(m[0])) for m in it['sel'] if d_from_jd(m[0])<asof]
               + [(0.0,date.fromisoformat(d)) for d in ex_g if d<iso])
            if vl: c.append((vl['min_orb_grad'],date.fromisoformat(vl['min_orb_datum'])))
            m_bis=min(c) if c else None
        im_orb.append(dict(transit=tname,ziel=rname,aspekt=aname,
            orb_grad=round(o_now,2), richtung=richtung,
            primaer=(rname in primary), spiegel=(rname in spiegel),
            kehrt_zurueck=(richtung=='auslaufend' and bool([d for d in
                          (date.fromisoformat(x) for x in (e['exakt'] if e else [])) if d>asof])),
            im_wirkorb=(o_now<=orb),
            kommt_in_wirkorb=bool(e and e['im_wirkorb']),
            letztes_exakt=(letzte[-1].isoformat() if letzte else None),
            tage_seit=( (asof-letzte[-1]).days if letzte else None),
            naechstes_exakt=(naechste[0].isoformat() if naechste else None),
            tage_bis=( (naechste[0]-asof).days if naechste else None),
            min_orb_grad=(e['min_orb_grad'] if e else round(min(orbs),3)),
            fenster_von=(e['fenster_von'] if e else None),
            fenster_bis=(e['fenster_bis'] if e else None),
            kontakte_gesamt=(e['kontakte'] if e else 0),
            # 2026-09-19 (W45) — Schema s. run()-Docstring:
            event_nr=(_idx[id(e)] if e else None),
            exakt_kommend=ex_k, exakt_gewesen=ex_g, annaeherung_kommend=ann_k,
            min_orb_ab_stichtag=(round(m_ab[0],3) if m_ab else None),
            min_orb_ab_stichtag_datum=(m_ab[1].isoformat() if m_ab else None),
            min_orb_bis_stichtag=(round(m_bis[0],3) if m_bis else None),
            wirkorb_jetzt=wj, wirkorb_kommend=wk, wirkorb_vorbei=wv,
            selbst_transit=ist_selbst_transit(tname,rname)))
    im_orb.sort(key=lambda x:(0 if x['primaer'] else 1, x['orb_grad']))

    nachhall=[]; anmarsch=[]
    for e in events:
        k=(e['transit'],e['ziel'],e['aspekt'])
        if e['weit_von']<=asof.isoformat()<=e['weit_bis']: continue   # steht jetzt im Orb
        ex=[date.fromisoformat(x) for x in e['exakt']]
        prev=[d for d in ex if d<=asof]; nxt=[d for d in ex if d>asof]
        lb_max=min(NACHWIRK.get(e['transit'], 10**6), int(lookback_months*30.4375))
        am_max=min(NACHWIRK.get(e['transit'], 10**6), ANMARSCH_TAGE)
        if prev and (asof-prev[-1]).days<=lb_max:
            nachhall.append(dict(transit=e['transit'],ziel=e['ziel'],aspekt=e['aspekt'],
                exakt=prev[-1].isoformat(),tage_seit=(asof-prev[-1]).days,
                primaer=e['primaer'],spiegel=e['spiegel'],
                orb_grad=round(orbcache[k][i_asof],2)))
        if nxt and (nxt[0]-asof).days<=am_max:
            anmarsch.append(dict(transit=e['transit'],ziel=e['ziel'],aspekt=e['aspekt'],
                exakt=nxt[0].isoformat(),tage_bis=(nxt[0]-asof).days,
                primaer=e['primaer'],spiegel=e['spiegel'],
                orb_grad=round(orbcache[k][i_asof],2)))
    nachhall.sort(key=lambda x:(0 if x['primaer'] else 1, x['tage_seit']))
    anmarsch.sort(key=lambda x:(0 if x['primaer'] else 1, x['tage_bis']))

    st_now=[s for s in stations
            if abs((date.fromisoformat(s['datum'])-asof).days)<=int(lookback_months*30.4375)]

    jetzt=dict(stichtag=asof.isoformat(), orb_weit=orb_weit, orb_wirk=orb,
               im_orb=im_orb, nachhall=nachhall, anmarsch=anmarsch,
               stationen_nah=st_now,
               stand={t:deg2sign(samples[t][i_asof][2])
                        + (' R' if samples[t][i_asof][3]<0 else '')
                        + (f" (H{house_of(samples[t][i_asof][2],cusps)})" if cusps else '')
                      for t,_,_ in transiters})

    # --- LANGLAEUFER --------------------------------------------------------
    langlaeufer=[]
    for idx,e in enumerate(events):
        if not _ist_langlaeufer(e): continue      # Kriterium s. oben (unveraendert)
        st=[s for s in stations
            if s['transit']==e['transit']
            and e['fenster_von']<=s['datum']<=e['fenster_bis']
            and any(n['ziel']==e['ziel'] and n['aspekt']==e['aspekt'] for n in s['nahe_detail'])]
        langlaeufer.append(dict(**{k:e[k] for k in
            ('transit','ziel','aspekt','exakt','exakt_im_fenster','exakt_vor_start',
             'min_orb_grad','fenster_von','fenster_bis','dauer_tage','dauer_monate',
             'perioden','kontakte','mehrfach','quartale','primaer','wird_exakt')},
            stationen=[s['datum'] for s in st],
            laeuft_ueber_ende=(e['fenster_bis']>=end.isoformat()),
            lief_vor_start=(e['fenster_von']<start.isoformat()),
            # 2026-09-19 (W1, W3, W55): Verweis aufs Ereignis und Kurzfelder
            event_nr=idx, annaeherung=e['annaeherung'],
            beginn_abgeschnitten=e['beginn_abgeschnitten'],
            exakt_nach_fenster=e['exakt_nach_fenster'],
            selbst_transit=e['selbst_transit']))
    langlaeufer.sort(key=lambda x:(0 if x['primaer'] else 1, -x['dauer_tage']))

    # --- Verdichtungen je Monat (primaere Wirkorb-Kontakte) -----------------
    hotspots=[]
    cur=date(start.year,start.month,1)
    while cur<=end:
        nxt=date(cur.year+(cur.month//12), (cur.month%12)+1, 1)
        aktiv=[]
        for e in events:
            if not (e['primaer'] and e['im_wirkorb']) or e['spiegel']: continue
            for a,b in e['perioden']:
                if a<nxt.isoformat() and b>=cur.isoformat():
                    aktiv.append(f"{e['transit']} {e['aspekt']} {e['ziel']}"); break
        ex=[x for e in events if e['primaer'] and e['im_wirkorb'] and not e['spiegel']
            for x in e['exakt_im_fenster'] if cur.isoformat()<=x<nxt.isoformat()]
        if cur>=date(start.year,start.month,1):
            hotspots.append(dict(monat=cur.strftime('%Y-%m'), aktiv=len(aktiv),
                                 exakt=len(ex), namen=sorted(set(aktiv)),
                                 quartal=q_of(max(cur,start))))
        cur=nxt
    hotspots=[h for h in hotspots if h['quartal']>=1]

    return dict(start=start.isoformat(), end=end.isoformat(), months=months,
                asof=asof.isoformat(), lookback_start=t0.isoformat(),
                lookback_months=lookback_months, orb_wirk=orb, orb_weit=orb_weit,
                events=events, jetzt=jetzt, langlaeufer=langlaeufer,
                hausdurchgang=hausdurchgang, zeichenaufenthalt=zeichenaufenthalt,
                hotspots=hotspots, stations=stations, ingress=ingress,
                chiron_transit=chiron_on, chiron_info=chiron_info,
                zeitzone=(str(ZEITZONE) if ZEITZONE else 'UT'),
                ephe_modell=HAUPT_MODELL,
                ephe_pfad=EPHE_PFAD,
                haeuser=bool(cusps), mars=mit_mars,
                primary=sorted(primary), quartale=n_q,
                quarter_bounds=[d.isoformat() for d in qb],
                # 2026-09-19 (W3, F21) — Schema s. run()-Docstring:
                moseph=ERZWINGE_MOSEPH,
                fortsetzung_monate=fortsetzung_monate,
                fortsetzung_horizont=ext_end.isoformat(),
                alter_bekannt=(geb is not None),
                fruehere_rueckrechnung=dict(
                    bis_zur_geburt=(geb is not None),
                    horizont=(None if geb is not None else hist_start.isoformat()),
                    jahre=(None if geb is not None else FRUEHER_OHNE_GEBURT_JAHRE)),
                fruehere_durchgaenge=fruehere)

# ---------------------------------------------------------------------------
# Lesbarer Report
# ---------------------------------------------------------------------------
def _bm(o):
    """Orb in Grad -> Bogenminuten mit einer Stelle, 'n.n′'."""
    return f"{o*60:.1f}′"


def _jetzt_exakt(x, res):
    """Exakt-Spalte der JETZT-Zeile (2026-09-19, W45): naechster Nulldurchgang
    (auch nach dem Fenster), sonst letzter (auch vor dem Rueckblick), sonst die
    engste Annaeherung bzw. der engste Orb AB DEM STICHTAG."""
    asof = date.fromisoformat(res['asof'])
    kom = x.get('exakt_kommend') or []
    gew = x.get('exakt_gewesen') or []
    if kom:
        d = kom[0]
        return (f"exakt {d} (in {(date.fromisoformat(d)-asof).days} T)"
                + (" nach dem Fenster" if d > res['end'] else ""))
    if gew:
        d = gew[-1]
        return (f"exakt war {d} (vor {(asof-date.fromisoformat(d)).days} T)"
                + (" vor dem Rueckblick" if d < res['lookback_start'] else ""))
    ann = x.get('annaeherung_kommend') or []
    if ann:
        d, o = min(ann, key=lambda q: q[1])
        return f"kein Exaktkontakt, Annaeherung bis {_bm(o)} am {d}"
    return (f"kein Exaktkontakt (engster Orb ab Stichtag {x.get('min_orb_ab_stichtag')}° "
            f"am {x.get('min_orb_ab_stichtag_datum')})")


def _jetzt_wirkorb(x, res):
    """Wirkorb-Spalte der JETZT-Zeile (2026-09-19, W45): die Periode, in der der
    Stichtag liegt (echtes Ende, auch nach dem Fenster), sonst die naechste,
    sonst die letzte vergangene."""
    hz = res.get('fortsetzung_horizont') or '9999'
    def bis(b):
        if b >= hz:
            return f"ueber den Rechenhorizont {hz} hinaus"
        return f"bis {b}" + (" (nach dem Fenster)" if b > res['end'] else "")
    wj, wk, wv = x.get('wirkorb_jetzt'), x.get('wirkorb_kommend'), x.get('wirkorb_vorbei')
    if wj:
        return f"Wirkorb {bis(wj[1])}" + (f", wieder {wk[0]}..{wk[1]}" if wk else "")
    if wk:
        return f"Wirkorb ab {wk[0]} {bis(wk[1])}"
    if wv:
        return f"Wirkorb vorbei (zuletzt bis {wv[1]})"
    return "nie im Wirkorb"


def _vorlauf_text(v, res):
    """Zeile 'vor dem Rueckblick' eines Langlaeufers (2026-09-19, W3)."""
    t = [f"Orb {res['orb_weit']}° ab {v['von']}"
         + (" (reicht vor den Rechenbeginn)" if v.get('horizont_erreicht') else ""),
         (f"Wirkorb ab {v['wirkorb_von']}" if v.get('wirkorb_von')
          else "im Vorlauf nie im Wirkorb")]
    if v.get('exakt'):
        t.append("exakt " + ", ".join(v['exakt']))
    elif v.get('annaeherung'):
        d, o = min(v['annaeherung'], key=lambda q: q[1])
        t.append(f"kein Exaktkontakt, Annaeherung bis {_bm(o)} am {d}")
    else:
        t.append(f"kein Exaktkontakt (min {v['min_orb_grad']}° am {v['min_orb_datum']})")
    return " | ".join(t)


def _fortsetzung_text(f, res):
    """Fortsetzung eines Kontakts nach dem Fenster (2026-09-19, W3):
    Nulldurchgaenge, endgueltiges Wirkorb-Ende, Austritt aus dem Erfassungsorb."""
    if f.get('exakt'):
        t = ["exakt " + ", ".join(f['exakt'])]
    elif f.get('annaeherung'):
        d, o = min(f['annaeherung'], key=lambda q: q[1])
        t = [f"kein Exaktkontakt, Annaeherung bis {_bm(o)} am {d}"]
    else:
        t = [f"kein Exaktkontakt (min {f['min_orb_grad']}° am {f['min_orb_datum']})"]
    t.append(f"Wirkorb bis {f['wirkorb_bis']}" if f.get('wirkorb_bis')
             else "nach dem Fenster nie im Wirkorb")
    t.append(f"Orb {res['orb_weit']}° ueber den Rechenhorizont {f['horizont']} hinaus"
             if f.get('horizont_erreicht') else f"Orb {res['orb_weit']}° bis {f['bis']}")
    return " | ".join(t)


def _frueher_text(g, alter):
    """Ein frueherer Durchgang (2026-09-19, W3): Nulldurchgaenge mit Alter
    (vollendete Jahre), Daten gleichen Alters zusammengefasst —
    '#2 JJJJ-MM-TT, JJJJ-MM-TT (Alter n), JJJJ-MM-TT (Alter n+1)'. Ohne
    Nulldurchgang: 'nicht exakt, ...' mit der engsten Stelle."""
    def gruppen(paare):
        teile, puffer, a0 = [], [], object()
        for d, a in paare:
            if puffer and a != a0:
                teile.append(", ".join(puffer) + (f" (Alter {a0})" if alter and a0 is not None else ""))
                puffer = []
            puffer.append(d); a0 = a
        if puffer:
            teile.append(", ".join(puffer) + (f" (Alter {a0})" if alter and a0 is not None else ""))
        return ", ".join(teile)
    if g['exakt']:
        t = gruppen([(x['datum'], x['alter']) for x in g['exakt']])
    elif g['annaeherung']:
        x = min(g['annaeherung'], key=lambda q: q['orb_grad'])
        t = (f"nicht exakt, Annaeherung bis {_bm(x['orb_grad'])} am "
             + gruppen([(x['datum'], x['alter'])]))
    else:
        t = (f"nicht exakt, engster Orb {g['min_orb_grad']}° am "
             + gruppen([(g['min_orb_datum'], g['min_orb_alter'])]))
    if g.get('ab_rechenbeginn'):
        t += " [lief schon bei der Geburt]" if alter else " [reicht vor den Rechenbeginn]"
    return f"#{g['nr']} {t}"


def format_report(res):
    """Das Ergebnis von run() als Text-Report — genau die Form, die
    transitdata.parse() wieder liest und die in §11 der chart_data steht."""
    out=[]; j=res['jetzt']
    out.append(f"Fenster {res['start']} .. {res['end']}   Stichtag {res['asof']}   "
               f"Rueckblick ab {res['lookback_start']}")
    out.append(f"Orb: Wirk {res['orb_wirk']}° / weit {res['orb_weit']}°   "
               f"Transit-Chiron: {'JA' if res['chiron_transit'] else 'AUSGEKLAMMERT'}   "
               f"Haus-Durchgaenge: {'JA' if res['haeuser'] else 'AUSGEKLAMMERT'}   "
               f"Mars: {'MIT' if res.get('mars') else 'ohne (Standard)'}")
    # Zusatzzeilen seit 30.07.2026: die Chiron-Ausklammerung war frueher stumm.
    # Die beiden Kopfzeilen darueber bleiben unveraendert — transitdata.py liest
    # sie, und §11 der chart_data traegt den Report unveraendert.
    # Zeitzonen-Zeile seit 2026-09-06 (Pruefbericht 4.10). Sie steht BEWUSST
    # unter den beiden ersten Kopfzeilen, die transitdata.py liest.
    out.append(f"Ephemeride: {res.get('ephe_modell','?')} fuer alle Faktoren"
               + ("   (erzwungen mit --moseph: Probelauf, kein Klientendokument)"
                  if res.get('moseph') else ""))
    out.append(f"Exaktdaten in: {res.get('zeitzone','UT')}"
               + ("   (Weltzeit — bei Bedarf --tz <IANA-Zone> setzen, damit die "
                  "Daten dem Ortstag der Klientin entsprechen)"
                  if res.get('zeitzone','UT')=='UT' else ""))
    if res.get('chiron_transit'):
        if res.get('ephe_pfad'):
            out.append(f"[ephemeride] Transit-Chiron aus {res['ephe_pfad']}")
    elif res.get('chiron_info'):
        out.append(f"[hinweis] Transit-Chiron ausgeklammert: {res['chiron_info']}")
    qb=res['quarter_bounds']
    nq=len(qb)-1
    # qb[k+1] ist der ERSTE Tag des Folgequartals. Gedruckt wird der LETZTE Tag
    # des Quartals — sonst ueberlappen sich in der Transit-Uhr zwei Baender um
    # einen Tag (transitdata liest genau diese Zeile).
    def q_bis(k):
        return (date.fromisoformat(qb[k]) - timedelta(days=1)).isoformat()
    out.append("Quartale: " + " · ".join(f"Q{q+1} {qb[q]}–{q_bis(q+1)}"
                                         for q in range(nq)))

    out.append("\n" + "="*70)
    out.append(f"JETZT — Stand am {j['stichtag']}")
    out.append("="*70)
    out.append("  Transit-Staende: " + " · ".join(f"{k} {v}" for k,v in j['stand'].items()))
    out.append(f"\n  -- im Orb (<= {j['orb_weit']}°), primaer zuerst  "
               f"[* = im Wirkorb {j['orb_wirk']}°] --")
    out.append("     Spalten: Orb am Stichtag | Richtung | Nulldurchgang (naechster, "
               "sonst letzter) | Wirkorb-Periode")
    rows=[x for x in j['im_orb'] if not x['spiegel']]
    if not rows: out.append("     (keiner)")
    for x in rows:
        tag='P' if x['primaer'] else ' '
        kern='*' if x['im_wirkorb'] else ' '
        richt=x['richtung']+(' (kehrt zurueck)' if x.get('kehrt_zurueck') else '')
        s=(f"  [{tag}{kern}] {x['transit']:7s} {x['aspekt']:11s} {x['ziel']:12s} "
           f"orb {x['orb_grad']:4.2f}° {richt:22s}")
        # 2026-09-19 (W45): Spalten entflochten — Orb AM STICHTAG | Richtung |
        # Exaktdatum | Wirkorb-Periode. Vorher stand hinter "wird nicht exakt"
        # das Passagen-Minimum und hinter "| bis" das Wirkorb-Ende, beide oft
        # aus dem Rueckblick.
        s+=" "+_jetzt_exakt(x,res)+" | "+_jetzt_wirkorb(x,res)
        out.append(s)
    out.append(f"\n  -- Nachhall (exakt kuerzlich, Orb inzwischen offen; Fenster je nach "
               f"Transiter bis {res['lookback_months']} Mon.) --")
    nh=[x for x in j['nachhall'] if not x['spiegel']]
    if not nh: out.append("     (keiner)")
    for x in nh:
        out.append(f"  [{'P' if x['primaer'] else ' '} ] {x['transit']:7s} {x['aspekt']:11s} "
                   f"{x['ziel']:12s} exakt {x['exakt']} (vor {x['tage_seit']} T)")
    out.append(f"\n  -- Anmarsch (exakt in den naechsten {ANMARSCH_TAGE} Tagen) --")
    am=[x for x in j['anmarsch'] if not x['spiegel']]
    if not am: out.append("     (keiner)")
    for x in am:
        out.append(f"  [{'P' if x['primaer'] else ' '} ] {x['transit']:7s} {x['aspekt']:11s} "
                   f"{x['ziel']:12s} exakt {x['exakt']} (in {x['tage_bis']} T)")
    if j['stationen_nah']:
        out.append("\n  -- Stationen im Umfeld des Stichtags --")
        for s in j['stationen_nah']:
            out.append(f"     {s['datum']} {s['transit']} {s['richtung']} {s['stand']} "
                       f"-> {', '.join(s['nahe'])}")

    out.append("\n" + "="*70)
    out.append("LANGLAEUFER — was ueber Monate/Jahre traegt")
    out.append("="*70)
    if not res['langlaeufer']: out.append("  (keine)")
    for x in res['langlaeufer']:
        tag='P' if x['primaer'] else ' '
        # 2026-09-19 (W1, W3): exakt = Nulldurchgang; "nie exakt" nur, wenn auch
        # Vorlauf und Fortsetzung keinen haben. In der exakt:-Zeile stehen nur
        # Daten des Rechenzeitraums (transitdata liest sie als Exaktdaten).
        e=(res['events'][x['event_nr']] if x.get('event_nr') is not None else {})
        v=e.get('vorlauf'); f=e.get('fortsetzung')
        if x['exakt']:
            ex=', '.join(x['exakt'])
        elif e.get('exakt_gesamt'):
            wo=[t_ for t_,z in (("vor dem Rueckblick",v),("Fortsetzung nach dem Fenster",f))
                if z and z.get('exakt')]
            ex=f"keiner im Rechenzeitraum (min {x['min_orb_grad']}°) — s. {' / '.join(wo)}"
        else:
            m=min([x['min_orb_grad']] + [z['min_orb_grad'] for z in (v,f) if z])
            ex=f"nie exakt (min {m}°)"
        flags=[]
        if x['lief_vor_start']: flags.append('laeuft schon')
        if v and v.get('wirkorb_von'): flags.append('Wirkorb-Beginn vor dem Rueckblick')
        if x['laeuft_ueber_ende']: flags.append('reicht ueber das Fenster hinaus')
        if x['mehrfach']: flags.append(f"{x['kontakte']}x exakt (rueckl.)")
        if x['stationen']: flags.append('Station '+', '.join(x['stationen']))
        out.append(f"  [{tag}] {x['transit']:7s} {x['aspekt']:11s} {x['ziel']:12s} "
                   f"{x['fenster_von']} .. {x['fenster_bis']} ({x['dauer_monate']} Mon, "
                   f"Q{'/'.join(str(q) for q in x['quartale'])})")
        out.append(f"        exakt: {ex}" + (f"   [{'; '.join(flags)}]" if flags else ""))
        if len(x['perioden'])>1:
            out.append("        im Wirkorb nur: " +
                       " | ".join(f"{a}..{b}" for a,b in x['perioden']))
        if v:
            out.append("        vor dem Rueckblick: " + _vorlauf_text(v,res))
        # (die Fortsetzung steht im eigenen Abschnitt "Fortsetzung nach dem Fenster")
        if x.get('annaeherung'):
            out.append("        Annaeherung ohne Nulldurchgang: " +
                       ", ".join(f"{d} bis {_bm(o)}" for d,o in x['annaeherung']))
    out.append("\n  -- Zeichen-Aufenthalte im Fenster --")
    for z in sorted(res['zeichenaufenthalt'], key=lambda z:(-z['tage'],z['transit'])):
        out.append(f"     {z['transit']:7s} {z['zeichen']:11s} {z['von']} .. {z['bis']} "
                   f"({_mon(z['tage'])} Mon)")
    if res['haeuser']:
        out.append("\n  -- Haus-Durchgaenge im Fenster (Koch) --")
        for h in sorted(res['hausdurchgang'], key=lambda h:(-h['tage'],h['transit'])):
            mark=[]
            if h.get('angeschnitten'): mark.append('lief schon')
            if h.get('laeuft_weiter'): mark.append('laeuft weiter')
            out.append(f"     {h['transit']:7s} Haus {h['haus']:2d}  {h['von']} .. {h['bis']} "
                       f"({_mon(h['tage'])} Mon)" + (f"  [{', '.join(mark)}]" if mark else ""))
    else:
        out.append("\n  -- Haus-Durchgaenge: AUSGEKLAMMERT (keine plausiblen Koch-Spitzen "
                   "in der chart_data gefunden; --cusps setzen) --")

    out.append("\n" + "="*70)
    out.append("QUARTALE")
    out.append("="*70)
    def key(e): return (0 if e['primaer'] else 1, min(e['quartale']), e['min_orb_grad'])
    hs={h['monat']:h for h in res['hotspots']}
    for q in range(1,nq+1):
        mon=[m for m,h in hs.items() if h['quartal']==q]
        dichte=sum(hs[m]['exakt'] for m in mon)
        out.append(f"\n=== Q{q} ({qb[q-1]}–{q_bis(q)})  "
                   f"exakte primaere Kontakte: {dichte} ===")
        qrows=[x for x in res['events']
               if q in x['quartale'] and x['im_wirkorb'] and not x['spiegel']]
        if not qrows: out.append("  (ruhig — kein Wirkorb-Kontakt)")
        for e in sorted(qrows, key=key):
            tag='P' if e['primaer'] else ' '
            hier=[d for d in e['exakt_im_fenster'] if qb[q-1]<=d<qb[q]]
            rest=[d for d in e['exakt_im_fenster'] if d not in hier]
            if hier:
                ex=';'.join(hier) + (f"  (auch {', '.join(rest)})" if rest else '')
            elif e['exakt_im_fenster']:
                ex=f"im Orb, exakt {', '.join(e['exakt_im_fenster'])}"
            else:
                # 2026-09-19 (W1, W45, W3): engster Orb IM FENSTER statt
                # Passagen-Minimum (das lag oft im Rueckblick: "streift 0.0°");
                # Annaeherung ohne Nulldurchgang und Exaktdaten ausserhalb des
                # Fensters ausdruecklich benannt.
                ann=[q for q in e.get('annaeherung',[]) if res['start']<=q[0]<=res['end']]
                mf=e.get('min_orb_im_fenster')
                if ann:
                    d_,o_=min(ann,key=lambda q:q[1])
                    ex=f"Annaeherung bis {_bm(o_)} am {d_} (kein Nulldurchgang)"
                else:
                    ex=f"streift {mf if mf is not None else e['min_orb_grad']}°"
                vor=[d for d in e.get('exakt_gesamt',[]) if d<res['start']]
                if vor: ex+=f" · exakt vor dem Fenster {', '.join(vor)}"
                if e.get('exakt_nach_fenster'):
                    ex+=f" · exakt nach dem Fenster {', '.join(e['exakt_nach_fenster'])}"
            lang=' [Langlaeufer]' if e['dauer_tage']>=LANG_TAGE else ''
            out.append(f"  [{tag}] {e['transit']:7s} {e['aspekt']:11s} {e['ziel']:12s} {ex}{lang}")
    out.append("\n=== MONATS-DICHTE (primaere Wirkorb-Kontakte) ===")
    out.append("  " + " · ".join(f"{h['monat']}:{h['aktiv']}({h['exakt']})" for h in res['hotspots']))
    out.append(f"\n=== STATIONEN nahe Radix ({len(res['stations'])}) ===")
    for s in res['stations']:
        pre='(vor Start) ' if s['vor_start'] else f"Q{s['quartal']} "
        out.append(f"  {pre}{s['datum']} {s['transit']} {s['richtung']} "
                   f"{s['stand']} -> {', '.join(s['nahe'])}")
    out.append(f"\n=== INGRESSE ({len(res['ingress'])}) ===")
    for g in res['ingress']:
        out.append(f"  Q{g['quartal']} {g['datum']} {g['transit']}: {g['von']} -> {g['nach']}")
    nsp=sum(1 for e in res['events'] if e['spiegel'])
    if nsp:
        out.append(f"\n[{nsp} Spiegel-Kontakte auf DC/IC/Suedknoten ausgeblendet — sie "
                   f"doppeln AC/MC/Nordknoten. Vollstaendig im JSON (Feld 'spiegel').]")

    # --- 2026-09-19 (W3): zwei Abschnitte mit Zeitangaben ausserhalb des
    # Rechenzeitraums. Ueberschriften woertlich, transitdata.parse() liest sie.
    if 'fortsetzung_horizont' in res:
        out.append("\n" + "="*70)
        out.append("Fortsetzung nach dem Fenster")
        out.append("="*70)
        out.append(f"  Kontakte, deren Passage am Fensterende ({res['end']}) noch laeuft oder "
                   f"binnen der Passagen-Luecke wieder einsetzt; gerechnet bis "
                   f"{res['fortsetzung_horizont']} ({res['fortsetzung_monate']} Monate).")
        out.append("  Spalten: Nulldurchgaenge nach dem Fenster | endgueltiges Wirkorb-Ende "
                   f"({res['orb_wirk']}°) | Austritt aus dem Erfassungsorb ({res['orb_weit']}°)")
        fo=[e for e in res['events'] if e.get('fortsetzung') and not e['spiegel']]
        if not fo: out.append("     (keiner)")
        for e in sorted(fo, key=lambda e:(0 if e['primaer'] else 1, e['transit'],
                                          e['ziel'], e['aspekt'], e['weit_von'])):
            out.append(f"  [{'P' if e['primaer'] else ' '}] {e['transit']:7s} "
                       f"{e['aspekt']:11s} {e['ziel']:12s} "
                       + _fortsetzung_text(e['fortsetzung'], res))
    if 'fruehere_durchgaenge' in res:
        rr=res.get('fruehere_rueckrechnung') or {}
        alter=bool(res.get('alter_bekannt'))
        out.append("\n" + "="*70)
        out.append("Frühere Durchgänge mit Datum und Alter")
        out.append("="*70)
        out.append(f"  Je Langlaeufer und Selbst-Transit mit Wirkorb im Fenster: fruehere "
                   f"Durchgaenge durch den Wirkorb ({res['orb_wirk']}°), #1 = der juengste, "
                   f"getrennt durch ' · '. Datum = Nulldurchgang.")
        if alter:
            out.append("  Alter = vollendete Lebensjahre am Datum (das „n. Lebensjahr\" ist "
                       "Alter + 1). Rueckgerechnet bis zur Geburt.")
        else:
            out.append(f"[hinweis] ohne --geburt: Daten ohne Alter; rueckgerechnet pauschal "
                       f"{rr.get('jahre')} Jahre (ab {rr.get('horizont')}) — Durchgaenge vor "
                       f"der Geburt sind nicht ausgeschlossen. Fuer ein Klientendokument "
                       f"--geburt setzen.")
        if not res['fruehere_durchgaenge']: out.append("     (keiner)")
        for k in res['fruehere_durchgaenge']:
            kopf=(f"  [{'P' if k['primaer'] else ' '}] {k['transit']:7s} "
                  f"{k['aspekt']:11s} {k['ziel']:12s} ")
            if not k['durchgaenge']:
                out.append(kopf + ("keiner seit der Geburt" if alter
                                   else f"keiner seit {rr.get('horizont')}"))
            else:
                out.append(kopf + " · ".join(_frueher_text(g, alter)
                                             for g in k['durchgaenge']))
    return "\n".join(out)

# ---------------------------------------------------------------------------
# Zusatz-Zeitmasse: progressiver Mond, Sonnenbogen, Profektion, Finsternisse
# Neu am 2026-09-06 (Pruefbericht Transit, Rubrik 5.1 bis 5.4). Ein
# Transitdokument ueber zwei Jahre ohne diese vier Masse ist fachlich
# unvollstaendig: Der progressive Mond faerbt das Jahr, der Sonnenbogen ist
# punktgenauer als jeder Transit, die Profektion nennt das Jahresthema, und
# eine Finsternis auf einem tragenden Punkt ist die staerkste Einzelmarke, die
# es gibt. Alles vier optional — sie brauchen das Geburtsdatum, das die
# blosse Radix-Laengenliste nicht enthaelt (--geburt).
# ---------------------------------------------------------------------------
HERRSCHER = {'Widder':'Mars','Stier':'Venus','Zwillinge':'Merkur','Krebs':'Mond',
             'Loewe':'Sonne','Jungfrau':'Merkur','Waage':'Venus',
             'Skorpion':'Pluto','Schuetze':'Jupiter','Steinbock':'Saturn',
             'Wassermann':'Uranus','Fische':'Neptun'}
KLASSISCH = {'Skorpion':'Mars','Wassermann':'Saturn','Fische':'Jupiter'}


def zusatzzeitmasse(radix, jd_geburt, start, end, cusps=None, orb=1.0):
    """Progressiver Mond, Sonnenbogen-Achsenkontakte, Profektion, Finsternisse.

    radix       {Name: ekl. Laenge} wie fuer run()
    jd_geburt   julianisches Datum der Geburt in UT
    start, end  date-Objekte des Rechenfensters
    cusps       12 Koch-Spitzen (fuer die Profektion noetig)
    orb         Orb der Sonnenbogen-Kontakte in Grad (Vorgabe 1,0)

    Rueckgabe: dict mit 'prog_mond', 'sonnenbogen', 'profektion', 'finsternisse'.

    2026-09-19 (W46, F20): 'prog_mond_wechsel' (Zeichen- und Hauswechsel mit
    Tagesdatum), je Sonnenbogen-Kontakt 'exakt' (Tagesdatum der Exaktheit, auch
    ausserhalb des Fensters) und 'exakt_im_fenster', das Finsternisdatum als
    Ortstag in der gesetzten Zeitzone, beim Jahresherrscher das FUEHRENDE Haus
    nach der Grenzlagen-Regel ('herrscher_haus_fuehrend', '..._spalte',
    '..._grenzlage', '..._abstand_spitze'; 'herrscher_haus' bleibt rechnerisch).
    """
    aus = {}
    jahr = 365.2422
    # 2026-09-19 (F21): unter --moseph rechnen auch die Zusatz-Zeitmasse Moshier.
    ZF = MOSEPH if ERZWINGE_MOSEPH else SWIEPH

    def alter(d):
        return (swe.julday(d.year, d.month, d.day, 12.0) - jd_geburt) / jahr

    # --- 1) progressiver Mond: 1 Tag nach Geburt = 1 Lebensjahr --------------
    pm = []
    d = start
    while d <= end:
        jd = jd_geburt + alter(d)
        lon = swe.calc_ut(jd, swe.MOON, ZF)[0][0]
        eintrag = dict(datum=d.isoformat(), laenge=round(lon, 4),
                       stand=deg2sign(lon))
        if cusps:
            eintrag['haus'] = house_of(lon, cusps)
        pm.append(eintrag)
        d = plus_quartale(quartal_start(d), 1)
    aus['prog_mond'] = pm
    # 2026-09-19 (W46): Zeichen- und Hauswechsel mit Tagesdatum (erster Tag im
    # neuen Zeichen bzw. Haus) — vorher nur der Stand je Quartalsanfang.
    wechsel = []
    d = start; vor = None
    while d <= end:
        lon = swe.calc_ut(jd_geburt + alter(d), swe.MOON, ZF)[0][0]
        zz = int(lon // 30) % 12
        hh = house_of(lon, cusps) if cusps else None
        if vor is not None:
            if zz != vor[0]:
                wechsel.append(dict(datum=d.isoformat(), art='Zeichen',
                                    von=ZODIAC[vor[0]], nach=ZODIAC[zz]))
            if hh is not None and hh != vor[1]:
                wechsel.append(dict(datum=d.isoformat(), art='Haus', von=vor[1], nach=hh))
        vor = (zz, hh)
        d = d + timedelta(days=1)
    aus['prog_mond_wechsel'] = wechsel

    # --- 2) Sonnenbogen: alle Radixpunkte um den Sonnenbogen weitergerueckt --
    sb = []
    sonne0 = radix.get('Sonne')
    if sonne0 is not None:
        d = start
        while d <= end:
            jd = jd_geburt + alter(d)
            bogen = (swe.calc_ut(jd, swe.SUN, ZF)[0][0] - sonne0) % 360.0
            for a_name, a_lon in radix.items():
                if a_name in ('DC', 'IC', 'Suedknoten'):
                    continue                      # Spiegelziele nie doppelt
                dir_lon = (a_lon + bogen) % 360.0
                for z_name, z_lon in radix.items():
                    for asp_name, asp in (('Konjunktion', 0), ('Opposition', 180),
                                          ('Quadrat', 90)):
                        o = orb_for(dir_lon, z_lon, asp)
                        if o <= orb and not (a_name == z_name and asp == 0):
                            sb.append(dict(monat=d.isoformat()[:7], punkt=a_name,
                                           aspekt=asp_name, ziel=z_name,
                                           orb=round(o, 3),
                                           bogen=round(bogen, 3), _tag=d))
            d = d + timedelta(days=30)
    # je (Punkt, Aspekt, Ziel) nur den engsten Monat behalten
    eng = {}
    for e in sb:
        k = (e['punkt'], e['aspekt'], e['ziel'])
        if k not in eng or e['orb'] < eng[k]['orb']:
            eng[k] = e
    # 2026-09-19 (W46): Tagesdatum der Exaktheit je Kontakt. Der Sonnenbogen
    # waechst stetig (~1° im Jahr); die Differenz zum Aspektpunkt wird darum
    # tageweise bisektiert, im Bereich ±800 Tage um den engsten Monat. Vorher
    # stand nur der engste Monat IM Fenster da, auch wenn die Exaktheit davor
    # oder dahinter lag.
    SB_W = {'Konjunktion': 0, 'Opposition': 180, 'Quadrat': 90}
    def sb_f(dd, a_lon, ziel):
        bg = (swe.calc_ut(jd_geburt + alter(dd), swe.SUN, ZF)[0][0] - sonne0) % 360.0
        return wrap180((a_lon + bg) % 360.0 - ziel)
    for e in eng.values():
        d0 = e.pop('_tag')
        a_lon = radix[e['punkt']]
        ziel = min(_ziele(radix[e['ziel']], SB_W[e['aspekt']]),
                   key=lambda z: abs(sb_f(d0, a_lon, z)))
        lo = d0 - timedelta(days=800); hi = d0 + timedelta(days=800)
        f_lo = sb_f(lo, a_lon, ziel); f_hi = sb_f(hi, a_lon, ziel)
        ex = None
        if (f_lo < 0) != (f_hi < 0):
            while (hi - lo).days > 1:
                mid = lo + timedelta(days=(hi - lo).days // 2)
                if (sb_f(mid, a_lon, ziel) < 0) == (f_lo < 0):
                    lo = mid
                else:
                    hi = mid
            ex = lo if abs(sb_f(lo, a_lon, ziel)) <= abs(sb_f(hi, a_lon, ziel)) else hi
        e['exakt'] = ex.isoformat() if ex else None
        e['exakt_im_fenster'] = bool(ex and start <= ex <= end)
    for e in sb:
        e.pop('_tag', None)
    aus['sonnenbogen'] = sorted(eng.values(), key=lambda e: e['monat'])

    # --- 3) Jahresprofektion: Alter mod 12 -> Haus, dessen Spitzenzeichen ----
    prof = []
    if cusps:
        j0 = int(alter(start))
        for k in (0, 1, 2):
            a = j0 + k
            h = a % 12                                  # 0 = 1. Haus
            zeichen = ZODIAC[int(cusps[h] // 30) % 12]
            herr = HERRSCHER.get(zeichen)
            herr_lon = radix.get(herr)
            # 2026-09-19 (F20): fuehrendes Haus nach der Grenzlagen-Regel
            hf = haus_fuehrung(herr_lon, cusps) if herr_lon is not None else None
            prof.append(dict(alter=a, haus=h + 1, zeichen=zeichen,
                             herrscher=herr,
                             herrscher_stand=(deg2sign(herr_lon)
                                              if herr_lon is not None else None),
                             herrscher_haus=(house_of(herr_lon, cusps)
                                             if herr_lon is not None else None),
                             klassisch=KLASSISCH.get(zeichen),
                             herrscher_haus_fuehrend=(hf['fuehrend'] if hf else None),
                             herrscher_haus_spalte=(hf['spalte'] if hf else None),
                             herrscher_grenzlage=(hf['stufe'] if hf else None),
                             herrscher_abstand_spitze=(hf['abstand'] if hf else None)))
    aus['profektion'] = prof

    # --- 4) Finsternisse im Fenster auf primaeren Punkten -------------------
    fin = []
    try:
        jd = swe.julday(start.year, start.month, start.day, 0.0)
        jd_end = swe.julday(end.year, end.month, end.day, 0.0)
        for typ, fn in (('Sonnenfinsternis', swe.sol_eclipse_when_glob),
                        ('Mondfinsternis', swe.lun_eclipse_when)):
            j = jd
            for _ in range(60):
                try:
                    r = fn(j, ZF, 0, False)
                except Exception:
                    break
                t = r[1][0]
                if t > jd_end or t <= j:
                    break
                lon = swe.calc_ut(t, swe.SUN, ZF)[0][0]
                if typ == 'Mondfinsternis':
                    lon = swe.calc_ut(t, swe.MOON, ZF)[0][0]
                treffer = [(n, round(orb_for(lon, l, 0), 3))
                           for n, l in radix.items()
                           if orb_for(lon, l, 0) <= 2.0]
                if treffer:
                    # 2026-09-19 (W46): Ortstag in der gesetzten Zeitzone wie
                    # alle Exaktdaten (vorher der Weltzeit-Tag aus revjul()).
                    fin.append(dict(typ=typ, datum=d_from_jd(t).isoformat(),
                                    stand=deg2sign(lon),
                                    trifft=[{'ziel': n, 'orb': o}
                                            for n, o in sorted(treffer,
                                                               key=lambda x: x[1])]))
                j = t + 1.0
    except Exception:
        pass
    aus['finsternisse'] = fin
    return aus


def format_zusatz(z):
    """Der Zusatzblock als Text fuer das Datenblatt."""
    out = ["", "=" * 70, "ZUSATZ-ZEITMASSE (progressiver Mond, Sonnenbogen, "
           "Profektion, Finsternisse)", "=" * 70]
    out.append("\n  -- progressiver Mond, je Quartalsanfang --")
    for e in z.get('prog_mond', []):
        out.append("     %s  %s%s" % (e['datum'], e['stand'],
                                      ("  (H%s)" % e['haus']) if e.get('haus') else ""))
    # 2026-09-19 (W46): Wechsel mit Tagesdatum, zitierfaehig im Beleg
    if 'prog_mond_wechsel' in z:
        out.append("\n  -- progressiver Mond, Zeichen- und Hauswechsel im Fenster "
                   "(Tagesdatum = erster Tag im neuen Zeichen/Haus) --")
        if not z['prog_mond_wechsel']:
            out.append("     keiner")
        for e in z['prog_mond_wechsel']:
            out.append("     %s  %-7s %s -> %s" % (e['datum'], e['art'], e['von'], e['nach']))
    out.append("\n  -- Sonnenbogen-Kontakte im Fenster (Orb <= 1°, engster Monat; "
               "exakt = Tagesdatum der Exaktheit, auch ausserhalb des Fensters) --")
    if not z.get('sonnenbogen'):
        out.append("     keine")
    for e in z.get('sonnenbogen', []):
        ex = ""
        if e.get('exakt'):
            ex = "   exakt %s%s" % (e['exakt'], "" if e.get('exakt_im_fenster')
                                   else (" (vor dem Fenster)" if e['exakt'] < e['monat']
                                         else " (nach dem Fenster)"))
        out.append("     %s  %-12s %-12s %-12s Orb %.2f°%s"
                   % (e['monat'], e['punkt'], e['aspekt'], e['ziel'], e['orb'], ex))
    out.append("\n  -- Jahresprofektion --")

    def _haus(e):
        # 2026-09-19 (F20): fuehrendes Haus vorn (Grenzlagen-Regel), wie in der
        # Staendetabelle der chart_data; vorher nur das rechnerische Haus.
        if e.get('herrscher_grenzlage'):
            ab = e['herrscher_abstand_spitze']; g = int(ab); m = int(round((ab - g) * 60))
            if m == 60:
                g, m = g + 1, 0
            return (", Haus %s (%s, %d°%02d′ vor Spitze %s — Haus %s fuehrt)"
                    % (e['herrscher_haus_spalte'], e['herrscher_grenzlage'], g, m,
                       e['herrscher_haus'] % 12 + 1, e['herrscher_haus_fuehrend']))
        return (", Haus %s" % e['herrscher_haus']) if e['herrscher_haus'] else ""
    for e in z.get('profektion', []):
        out.append("     Alter %d -> %d. Haus (%s), Herrscher %s%s%s"
                   % (e['alter'], e['haus'], e['zeichen'], e['herrscher'],
                      (" in %s" % e['herrscher_stand']) if e['herrscher_stand'] else "",
                      _haus(e)))
    out.append("\n  -- Finsternisse auf Radixpunkten (Orb <= 2°) --")
    if not z.get('finsternisse'):
        out.append("     keine im Fenster")
    for e in z.get('finsternisse', []):
        zi = ", ".join("%s %.2f°" % (t['ziel'], t['orb']) for t in e['trifft'])
        out.append("     %s  %-16s %-18s -> %s"
                   % (e['datum'], e['typ'], e['stand'], zi))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Selbsttest (2026-09-19) — python3 transit.py --selbsttest
# ---------------------------------------------------------------------------
def _selbsttest(still=False):
    """Konstruierte Faelle, KEINE Personendaten: Radix-Laengen werden aus
    Ephemeriden-Staenden an frei gewaehlten julianischen Daten gebildet, Daten
    nur aus diesen JD abgeleitet. Alles auf Moshier (dateiunabhaengig).
    Rueckgabe True, wenn alle Faelle gruen sind."""
    global ERZWINGE_MOSEPH, ZEITZONE
    fehler = []
    def pruefe(bed, text):
        if not bed:
            fehler.append(text)
    FL = MOSEPH
    lon = lambda pl, jd: swe.calc_ut(jd, pl, FL)[0][0]
    alt_zz = ZEITZONE; alt_mo = ERZWINGE_MOSEPH
    setze_zeitzone(None)
    try:
        # --- W1: Knotenstation (Laenge dort minimal oder maximal) -----------
        j = 2451545.0; sp0 = swe.calc_ut(j, swe.TRUE_NODE, FL)[0][3]; js = None
        for k in range(1, 60):
            sp = swe.calc_ut(j + k, swe.TRUE_NODE, FL)[0][3]
            if (sp < 0) != (sp0 < 0):
                lo, hi = j + k - 1, j + k
                for _ in range(40):
                    m = (lo + hi) / 2.0
                    if (swe.calc_ut(m, swe.TRUE_NODE, FL)[0][3] < 0) == (sp0 < 0): lo = m
                    else: hi = m
                js, vz = hi, (1.0 if sp0 < 0 else -1.0)   # +1: Minimum der Laenge
                break
            sp0 = sp
        pruefe(js is not None, "W1: keine Knotenstation im Suchbereich gefunden")
        if js:
            ls = lon(swe.TRUE_NODE, js)
            reihe = [(js - 10 + k, lon(swe.TRUE_NODE, js - 10 + k),
                      swe.calc_ut(js - 10 + k, swe.TRUE_NODE, FL)[0][3]) for k in range(21)]
            z_nah = (ls + vz * 0.005) % 360.0      # zweimal gekreuzt, binnen zwei Tagen
            kr = _nulldurchgaenge(swe.TRUE_NODE, FL, z_nah, reihe)
            pruefe(len(kr) == 2, f"W1: zwei Kreuzungen erwartet, {len(kr)} gefunden")
            pruefe(all(abs(wrap180(lon(swe.TRUE_NODE, x) - z_nah)) < 1e-5 for x in kr),
                   "W1: Kreuzung nicht auf den Punkt bisektiert")
            pruefe(len(kr) == 2 and kr[1] - kr[0] < 2.0,
                   "W1: die zwei Kreuzungen sollten binnen zwei Tagen liegen")
            z_weg = (ls - vz * 0.01) % 360.0       # nie erreicht: Umkehr 0,6′ davor
            pruefe(_nulldurchgaenge(swe.TRUE_NODE, FL, z_weg, reihe) == [],
                   "W1: Station ohne Kreuzung als Nulldurchgang gemeldet")
            jd_m, o_m, gek = refine_min(swe.TRUE_NODE, FL, z_weg, 0, js - 1, js + 1)
            pruefe(not gek and abs(o_m - 0.01) < 0.002,
                   f"W1: Annaeherung erwartet (0,01°), bekam gekreuzt={gek}, orb={o_m:.4f}")
            # auf run()-Ebene: 'Mond' zweimal gekreuzt (±~2 Tage), 'Sonne' nur angenaehert
            d_s = d_from_jd(js)
            rad = {'Mond': (ls + vz * 0.02) % 360.0, 'Sonne': z_weg}
            res = run(rad, start=d_s, months=3, lookback_months=3, ohne_chiron=True,
                      moseph=True, jd_geburt=js - 3652.5)
            ev = {(e['transit'], e['ziel'], e['aspekt']): e for e in res['events']
                  if e['weit_von'] <= d_s.isoformat() <= e['weit_bis']}
            e_m = ev.get(('Knoten', 'Mond', 'Konjunktion')); e_s = ev.get(('Knoten', 'Sonne', 'Konjunktion'))
            # der Knoten pendelt ueber Wochen um beide Punkte; geprueft wird die
            # Station selbst (±3 Tage)
            nah = lambda d: abs((date.fromisoformat(d) - d_s).days) <= 3
            pruefe(e_m is not None and len([d for d in e_m['exakt'] if nah(d)]) == 2,
                   "W1: run() sollte an der Station zwei Exaktdaten fuer Knoten ☌ Mond "
                   "liefern: %r" % ((e_m and e_m['exakt']),))
            pruefe(e_s is not None and not [d for d in e_s['exakt'] if nah(d)]
                   and [q for q in e_s['annaeherung'] if nah(q[0]) and abs(q[1] - 0.01) < 0.002],
                   "W1: Knoten ☌ Sonne sollte an der Station Annaeherung statt exakt sein: %r"
                   % ((e_s and (e_s['exakt'], e_s['annaeherung'])),))
            # F21: erzwungenes Moshier
            pruefe(res['moseph'] and res['ephe_modell'] == 'Moshier' and not res['chiron_transit'],
                   "F21: --moseph nicht wirksam")
            rep = format_report(res)
            pruefe('erzwungen mit --moseph' in rep, "F21: Report-Kopf nennt --moseph nicht")
            pruefe('\nFortsetzung nach dem Fenster\n' in rep
                   and '\nFrühere Durchgänge mit Datum und Alter\n' in rep,
                   "W3: Abschnittsueberschriften fehlen oder weichen ab")
            pruefe('Annaeherung ohne Nulldurchgang' in rep
                   or not any(l_['annaeherung'] for l_ in res['langlaeufer']),
                   "W1: Report nennt die Annaeherung eines Langlaeufers nicht")
            json.dumps(res)                          # muss serialisierbar sein
            # W45: Spalten des Jetzt-Teils passen zum Stichtag
            for x in res['jetzt']['im_orb']:
                a_ = res['asof']
                if x['wirkorb_jetzt']:
                    pruefe(x['wirkorb_jetzt'][0] <= a_ <= x['wirkorb_jetzt'][1],
                           "W45: wirkorb_jetzt enthaelt den Stichtag nicht")
                pruefe(all(d > a_ for d in x['exakt_kommend'])
                       and all(d <= a_ for d in x['exakt_gewesen']),
                       "W45: exakt_kommend/exakt_gewesen falsch einsortiert")
            # W55
            pruefe(ist_selbst_transit('Saturn', 'Saturn') and ist_selbst_transit('Knoten', 'Mondknoten')
                   and not ist_selbst_transit('Saturn', 'Sonne'), "W55: Selbst-Transit falsch erkannt")

        # --- W3: fruehere Durchgaenge mit Alter (Jupiter-Rueckkehr) -----------
        jg = 2440000.5                                   # konstruierter Geburtszeitpunkt
        jup0 = lon(swe.JUPITER, jg)
        r2 = [(jg + 7300 + k, lon(swe.JUPITER, jg + 7300 + k),
               swe.calc_ut(jg + 7300 + k, swe.JUPITER, FL)[0][3]) for k in range(2200)]
        k2 = _nulldurchgaenge(swe.JUPITER, FL, jup0, r2)
        r1 = [(jg + 3300 + k, lon(swe.JUPITER, jg + 3300 + k),
               swe.calc_ut(jg + 3300 + k, swe.JUPITER, FL)[0][3]) for k in range(1800)]
        k1 = _nulldurchgaenge(swe.JUPITER, FL, jup0, r1)
        pruefe(bool(k1) and bool(k2), "W3: Jupiter-Rueckkehr im Testaufbau nicht gefunden")
        if k1 and k2:
            geb = d_from_jd(jg)
            res = run({'Jupiter': jup0, 'Sonne': (jup0 + 100.0) % 360.0}, start=d_from_jd(k2[0]),
                      months=3, lookback_months=3, ohne_chiron=True, moseph=True, jd_geburt=jg)
            fr = {(f['transit'], f['aspekt'], f['ziel']): f for f in res['fruehere_durchgaenge']}
            f = fr.get(('Jupiter', 'Konjunktion', 'Jupiter'))
            pruefe(f is not None and f['selbst_transit'], "W3: Jupiter-Rueckkehr fehlt in fruehere_durchgaenge")
            if f:
                erw = [(d_from_jd(x).isoformat(), _alter_voll(d_from_jd(x), geb)) for x in k1]
                ist = [(x['datum'], x['alter']) for x in f['durchgaenge'][0]['exakt']] if f['durchgaenge'] else []
                pruefe(ist == erw, f"W3: erste Rueckkehr {ist} statt {erw}")
                pruefe(all(not g['ab_rechenbeginn'] for g in f['durchgaenge']),
                       "W3: Geburts-Passage einer Rueckkehr-Konjunktion darf nicht zaehlen")
                pruefe(len(f['durchgaenge']) == 1, "W3: genau ein frueherer Durchgang erwartet")
            pruefe(res['alter_bekannt'] and res['fruehere_rueckrechnung']['bis_zur_geburt'],
                   "W3: Rueckrechnung bis zur Geburt nicht vermerkt")
            # (b) Fortsetzung: Kontakt im Orb am Fensterende -> fortsetzung gesetzt
            for e in res['events']:
                if e['weit_bis'] == res['end'] and not e['spiegel']:
                    pruefe(e['fortsetzung'] is not None,
                           "W3: Fortsetzung fehlt bei Kontakt im Orb am Fensterende")
                if e['fortsetzung']:
                    pruefe(all(d > res['end'] for d in e['fortsetzung']['exakt'])
                           and e['fortsetzung']['bis'] > res['end'],
                           "W3: Fortsetzung enthaelt Daten aus dem Fenster")
                if e['vorlauf']:
                    pruefe(e['vorlauf']['von'] < res['lookback_start']
                           and all(d < res['lookback_start'] for d in e['vorlauf']['exakt']),
                           "W3: Vorlauf enthaelt Daten aus dem Rechenzeitraum")
                pruefe(e['exakt_gesamt'] == sorted(set(e['exakt_gesamt']))
                       and set(e['exakt']) <= set(e['exakt_gesamt']),
                       "W3: exakt_gesamt unvollstaendig")
            fo = [e for e in res['events'] if e['fortsetzung'] and e['fortsetzung']['exakt']]
            pruefe(bool(fo), "W3: im Testaufbau keine Exaktdaten nach dem Fenster gefunden")
            # ohne Geburt: Daten ohne Alter, Hinweiszeile
            res0 = run({'Jupiter': jup0}, start=d_from_jd(k2[0]), months=3, lookback_months=3,
                       ohne_chiron=True, moseph=True)
            pruefe(not res0['alter_bekannt'] and '[hinweis] ohne --geburt' in format_report(res0),
                   "W3: ohne --geburt fehlt die Hinweiszeile")
            pruefe(all(x['alter'] is None for f0 in res0['fruehere_durchgaenge']
                       for g in f0['durchgaenge'] for x in g['exakt']),
                   "W3: ohne --geburt darf kein Alter stehen")

        # --- W46 / F20: Zusatz-Zeitmasse --------------------------------------
        ERZWINGE_MOSEPH = True
        s0 = lon(swe.SUN, jg)
        start = d_from_jd(jg + 30 * 365.25); start = quartal_start(start)
        end = plus_quartale(start, 8) - timedelta(days=1)
        def bogen(d):
            a_ = (swe.julday(d.year, d.month, d.day, 12.0) - jg) / 365.2422
            return (lon(swe.SUN, jg + a_) - s0) % 360.0
        mitte = start + (end - start) // 2
        vor = start - timedelta(days=200)
        rad = {'Sonne': s0, 'Venus': (s0 + bogen(mitte)) % 360.0,
               'Mars': (s0 + bogen(vor) + 90.0) % 360.0, 'Mond': lon(swe.MOON, jg)}
        cz = [k * 30.0 for k in range(12)]
        z = zusatzzeitmasse(rad, jg, start, end, cusps=cz)
        sb = {(e['punkt'], e['aspekt'], e['ziel']): e for e in z['sonnenbogen']}
        e1 = sb.get(('Sonne', 'Konjunktion', 'Venus')); e2 = sb.get(('Sonne', 'Quadrat', 'Mars'))
        pruefe(e1 is not None and abs((date.fromisoformat(e1['exakt']) - mitte).days) <= 2
               and e1['exakt_im_fenster'], "W46: Sonnenbogen-Tagesdatum im Fenster falsch: %s" % e1)
        pruefe(e2 is not None and abs((date.fromisoformat(e2['exakt']) - vor).days) <= 2
               and not e2['exakt_im_fenster'], "W46: Sonnenbogen-Tagesdatum vor dem Fenster falsch: %s" % e2)
        for w in z['prog_mond_wechsel']:
            d = date.fromisoformat(w['datum'])
            l1 = swe.calc_ut(jg + (swe.julday(d.year, d.month, d.day, 12.0) - jg) / 365.2422, swe.MOON, FL)[0][0]
            d0 = d - timedelta(days=1)
            l0 = swe.calc_ut(jg + (swe.julday(d0.year, d0.month, d0.day, 12.0) - jg) / 365.2422, swe.MOON, FL)[0][0]
            if w['art'] == 'Zeichen':
                pruefe(ZODIAC[int(l1 // 30) % 12] == w['nach'] and ZODIAC[int(l0 // 30) % 12] == w['von'],
                       "W46: Zeichenwechsel des progressiven Mondes falsch datiert")
            else:
                pruefe(house_of(l1, cz) == w['nach'] and house_of(l0, cz) == w['von'],
                       "W46: Hauswechsel des progressiven Mondes falsch datiert")
        pruefe(bool(z['prog_mond_wechsel']), "W46: in zwei Jahren kein Wechsel des progressiven Mondes")
        # F20: Herrscher des ersten Profektionsjahres in Schwellenlage (1° vor Spitze 3)
        a0 = int((swe.julday(start.year, start.month, start.day, 12.0) - jg) / 365.2422)
        herr = HERRSCHER[ZODIAC[a0 % 12]]
        rad2 = dict(rad); rad2[herr] = 59.0
        z2 = zusatzzeitmasse(rad2, jg, start, end, cusps=cz)
        p0 = z2['profektion'][0]
        pruefe(p0['herrscher_haus'] == 2 and p0['herrscher_haus_fuehrend'] == 3
               and p0['herrscher_haus_spalte'] == '3/2' and p0['herrscher_grenzlage'] == 'Schwellenlage',
               "F20: fuehrendes Haus des Jahresherrschers falsch: %s" % p0)
        pruefe('Haus 3/2 (Schwellenlage, 1°00′ vor Spitze 3 — Haus 3 fuehrt)' in format_zusatz(z2),
               "F20: Report nennt das fuehrende Haus nicht vorn")
        hf = haus_fuehrung(56.5, cz)
        pruefe(hf['spalte'] == '2/3' and hf['stufe'] == 'Grenzlage' and haus_fuehrung(40.0, cz)['spalte'] == '2',
               "F20: Grenzlage 2°–5° falsch")
        try:
            import radix as _r                       # gleiche Regel wie radix.haus_spalte()
        except Exception:                            # radix.py fehlt/ist nicht ladbar
            _r = None
        if _r is not None and hasattr(_r, 'haus_spalte'):
            pruefe(all(haus_fuehrung(x / 7.0, cz)['spalte'] == _r.haus_spalte(x / 7.0, cz)
                       for x in range(0, 2520)), "F20: Abweichung von radix.haus_spalte()")
    finally:
        ERZWINGE_MOSEPH = alt_mo
        ZEITZONE = alt_zz
    # Ausgemustert (2026-09-23): ein Glueckspunkt im factors-Block eines alten
    # Datenblatts wird kein Transitziel. Konstruierter Block, keine echten Daten.
    import tempfile, contextlib, io
    with tempfile.NamedTemporaryFile('w', suffix='_chart_data.md', delete=False,
                                     encoding='utf-8') as _tf:
        _tf.write("factors = [{'name': 'Sonne', 'lon': 10.5}, "
                  "{'name': 'Glückspunkt', 'lon': 99.0}, "
                  "{'name': 'Knoten', 'lon': 200.0}]\n")
    _err = io.StringIO()
    with contextlib.redirect_stderr(_err):
        _rx = radix_from_chart_data(_tf.name)
    os.unlink(_tf.name)
    pruefe(_rx == {'Sonne': 10.5, 'Mondknoten': 200.0},
           "Ausgemustert: Glueckspunkt darf kein Transitziel sein (%r)" % (_rx,))
    pruefe('ausgemustert' in _err.getvalue(),
           "Ausgemustert: der Hinweis auf stderr fehlt")
    if not still:
        if fehler:
            print("Selbsttest transit.py: %d FEHLER" % len(fehler))
            for f_ in fehler:
                print("  - " + f_)
        else:
            print("Selbsttest transit.py: alle Faelle gruen (W1, W3, W45, W46, W55, F20, F21, "
                  "Glueckspunkt ausgemustert)")
    return not fehler


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


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


if __name__ == "__main__":
    if _hilfe_cli():          # python3 transit.py --hilfe [<name>]
        sys.exit(0)
    if "--selbsttest" in sys.argv[1:]:             # 2026-09-19: python3 transit.py --selbsttest
        sys.exit(0 if _selbsttest() else 1)
    ap=argparse.ArgumentParser(description="Transit-Rechner: Jetzt + Langlaeufer + 8 Quartale")
    ap.add_argument("chart_data", help="Pfad zur <klient>_chart_data.md (Grundhoroskop)")
    ap.add_argument("--start", default=None, help="YYYY-MM-DD (Default: heute)")
    ap.add_argument("--asof", default=None, help="Stichtag der Jetzt-Aufnahme (Default: start)")
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--lookback", type=int, default=LOOKBACK_M, help="Rueckblick in Monaten")
    ap.add_argument("--orb", type=float, default=ORB, help="Wirk-Orb (Deutung/Quartale)")
    ap.add_argument("--orb-weit", type=float, default=ORB_WEIT, help="Erfassungs-/Jetzt-Orb")
    ap.add_argument("--primary", default="",
                    help="zusaetzliche primaere Ziele, kommagetrennt "
                         "(Radix-Namen; die Knotenachse heisst `Mondknoten`)")
    ap.add_argument("--cusps", default=None,
                    help="12 Koch-Spitzen als Dezimalgrad, kommagetrennt (ueberschreibt Datei)")
    ap.add_argument("--ephe", default=None,
                    help="Verzeichnis mit den Swiss-Ephemeris-Dateien (seas_*.se1) — "
                         "nur noetig, wenn die Autosuche sie nicht findet")
    ap.add_argument("--mars", action="store_true",
                    help="Mars als Feintrigger mitrechnen (Opt-in, nicht Standard)")
    ap.add_argument("--tz", default=None,
                    help="IANA-Zeitzone fuer die AUSGABE der Exaktdaten, z. B. "
                         "Europe/Berlin. Ohne Angabe Weltzeit (UT) wie bisher.")
    ap.add_argument("--ohne-chiron", dest="ohne_chiron", action="store_true",
                    help="bewusst ohne Transit-Chiron rechnen; ohne dieses Flag "
                         "ist eine fehlende Asteroiden-Ephemeride ein harter Fehler")
    ap.add_argument("--geburt", default=None,
                    help="Geburtszeitpunkt in UT als YYYY-MM-DDTHH:MM — schaltet die "
                         "Zusatz-Zeitmasse frei (progressiver Mond, Sonnenbogen, "
                         "Jahresprofektion, Finsternisse auf Radixpunkten) und liefert "
                         "das Lebensalter der frueheren Durchgaenge (Rueckrechnung "
                         "bis zur Geburt)")
    ap.add_argument("--moseph", action="store_true",
                    help="Moshier-Ephemeride fuer ALLE Faktoren erzwingen, auch wenn "
                         "Swiss-Ephemeris-Dateien vorliegen (Zwei-Modell-Probe). "
                         "Rechnet zwangslaeufig ohne Transit-Chiron; der Report-Kopf "
                         "sagt es. Kein Schalter fuer Klientendokumente.")
    ap.add_argument("--json", default=None, help="Ereignisliste als JSON hierhin schreiben")
    args=ap.parse_args()
    if args.ephe and ephe_pfad_setzen(args.ephe) is None:
        print(f"[warnung] --ephe {args.ephe}: keine seas_*.se1 darin gefunden — "
              "Autosuche/Standardpfad greift stattdessen.", file=sys.stderr)
        ephe_pfad_setzen()
    start = date.fromisoformat(args.start) if args.start else None
    asof  = date.fromisoformat(args.asof)  if args.asof  else None
    extra = [x.strip() for x in args.primary.split(",") if x.strip()]
    radix = radix_from_chart_data(args.chart_data)
    if args.cusps:
        cusps=[float(x)%360.0 for x in args.cusps.split(",")][:12]
        if not _plausible_cusps(cusps, radix):
            print("[warnung] --cusps unplausibel (12 Werte, aufsteigend, H1=AC, H10=MC?) "
                  "— Haus-Durchgaenge ausgeklammert.", file=sys.stderr)
            cusps=None
    else:
        cusps = cusps_from_chart_data(args.chart_data, radix)
    # 2026-09-19 (W3): --geburt wird VOR der Rechnung gelesen — run() braucht
    # ihn fuer Alter und Rueckrechnung der frueheren Durchgaenge.
    jdg = None
    if args.geburt:
        try:
            g = args.geburt.replace("T", " ").strip()
            gd, gt = (g.split(" ") + ["0:00"])[:2]
            gy, gm, gdd = [int(x) for x in gd.split("-")]
            gh, gmi = [int(x) for x in (gt.split(":") + ["0"])[:2]]
            jdg = swe.julday(gy, gm, gdd, gh + gmi / 60.0)
        except Exception as e:
            print("[FEHLER] --geburt %r nicht lesbar (%s). Erwartet: "
                  "YYYY-MM-DDTHH:MM in UT." % (args.geburt, e), file=sys.stderr)
            sys.exit(2)
    try:
        res = run(radix, start=start, months=args.months, primary_extra=extra,
                  orb=args.orb, orb_weit=args.orb_weit, lookback_months=args.lookback,
                  cusps=cusps, asof=asof, mit_mars=args.mars,
                  ohne_chiron=args.ohne_chiron, tz=args.tz,
                  jd_geburt=jdg, moseph=args.moseph)
    except (ValueError, RuntimeError) as e:
        print("[FEHLER] %s" % e, file=sys.stderr)
        sys.exit(2)
    print(format_report(res))
    if jdg is not None:
        z = zusatzzeitmasse(radix, jdg, date.fromisoformat(res["start"]),
                            date.fromisoformat(res["end"]), cusps=cusps)
        res["zusatz"] = z
        print(format_zusatz(z))
    if args.json:
        json.dump(res, open(args.json,"w"), indent=1, ensure_ascii=False)
        print(f"\n[json -> {args.json}]")
