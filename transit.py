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

Radix kommt aus der bereits gerechneten <klient>_chart_data.md (factors/achsen-
Block) — NIE neu rechnen (Token-Oekonomie, s. Kern). Die Koch-Hausspitzen werden
aus derselben Datei gelesen, wenn sie dort maschinenlesbar (cusps-Liste) oder als
Text/Tabelle stehen; sonst laeuft alles ausser den Haus-Durchgaengen normal
weiter (Status im Report: haeuser: JA/AUSGEKLAMMERT).

CLI:
    python3 transit.py <chart_data.md> [--start YYYY-MM-DD] [--months 24] \\
            [--asof YYYY-MM-DD] [--lookback 6] [--orb 1.5] [--orb-weit 3.0] \\
            [--primary Venus,Mars,Pluto,Saturn,Chiron,Nordknoten] \\
            [--cusps "175.3,201.0,..."] [--ephe <verzeichnis>] [--json out.json]

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
NAME_MAP = {'Knoten':'Nordknoten'}               # factors-Name -> Radix-Zielname

# ---------------------------------------------------------------------------
# Radix aus chart_data.md (factors/achsen-Block)
# ---------------------------------------------------------------------------
def radix_from_chart_data(path):
    """Liest name/lon-Paare aus dem factors- UND achsen-Block der chart_data.md.
    Erwartet Dict-Literale wie {'name':'Sonne', ... 'lon':45.4833, ...}. Gibt
    {Name: ekl. Laenge} zurueck (Knoten -> Nordknoten normalisiert)."""
    txt = open(path, encoding='utf-8').read()
    rx = re.compile(r"'name'\s*:\s*'([^']+)'[^{}]*?'lon'\s*:\s*(-?\d+\.?\d*)")
    radix = {}
    for name, lon in rx.findall(txt):
        radix[NAME_MAP.get(name, name)] = float(lon)
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
    m = re.search(r"cusps'?\s*[:=]\s*\[([^\]]+)\]", txt)
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
                        r"|(\d{1,2})\s*[°º]\s*(\d{1,2})?\s*['’\s]*\s*(" + zod_rx + r"))",
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

# ---------------------------------------------------------------------------
# Hauptrechnung
# ---------------------------------------------------------------------------
def run(radix, start=None, months=24, primary_extra=None, orb=ORB, orb_weit=ORB_WEIT,
        lookback_months=LOOKBACK_M, cusps=None, asof=None, lang_tage=LANG_TAGE,
        mit_mars=False, ohne_chiron=False, tz=None):
    """radix: {Name: ekl. Laenge}. start: date (Default heute). months: Fensterlaenge.
    primary_extra: zusaetzliche Radix-Ziele neben den persoenlichen Punkten.
    lookback_months: Rueckblick VOR dem Start (fuer echte Exaktdaten auslaufender
    Kontakte im Jetzt-Teil). cusps: 12 Koch-Spitzen (optional, fuer Haus-Durchgaenge).
    asof: Stichtag der Momentaufnahme (Default = start)."""
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
    unbekannt = [x for x in (primary_extra or []) if x not in radix]
    if unbekannt:
        raise ValueError(
            "unbekannte primaere Ziele: %s\n"
            "  Erlaubt sind die Namen der Radix-Punkte: %s\n"
            "  Haeufige Verwechslung: der Mondknoten heisst hier `Nordknoten`, "
            "nicht `Knoten`." % (", ".join(unbekannt), ", ".join(sorted(radix))))
    primary = set(PERSONAL) | set(primary_extra or [])
    spiegel = spiegel_ziele(radix)
    transiters, chiron_on, chiron_info = _transiters(
        mit_mars, probe=(swe.julday(t0.year, t0.month, t0.day, 0.0),
                         swe.julday(end.year, end.month, end.day, 0.0)))
    # Chiron-Pflicht (Pruefbericht Transit 2026-09-06, 1.1). Vorher lief ein
    # Lauf ohne Asteroiden-Ephemeride mit einer blossen Hinweiszeile durch und
    # verlor im Pruefall 27 Kontakte, darunter den am Stichtag engsten. Wer
    # bewusst ohne Chiron rechnen will, sagt es jetzt ausdruecklich.
    if not chiron_on and not ohne_chiron:
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

    def refine_min(pl,flag,rlon,a,jd_lo,jd_hi):
        """Exakter Zeitpunkt des Aspekts im Fenster [jd_lo, jd_hi].

        Bis zum 2026-09-06 wurden hier 73 Punkte ueber zwei Tage abgetastet
        (Schrittweite 40 Minuten) und der kleinste ABGETASTETE Orb genommen.
        Lag der wahre Exaktpunkt dicht an Mitternacht, kippte das gemeldete
        Datum auf den Nachbartag — mit wechselndem Vorzeichen, je nachdem,
        welcher Rasterpunkt naeher lag (Pruefbericht Transit 2026-09-06, 4.10,
        Ursache 1; im Pruefall vier von 146 Exaktdaten betroffen).

        Jetzt zweistufig: Kreuzt die vorzeichenbehaftete Winkeldifferenz zum
        Aspektpunkt die Null, wird bis auf rund eine Sekunde bisektiert. Tut
        sie es nicht (Streifkontakt, Stationsnaehe), wird das Minimum von |f|
        per Goldenem Schnitt gesucht statt auf einem festen Raster."""
        mitte=(jd_lo+jd_hi)/2.0
        l0,_=calc(pl,mitte,flag)
        ziel=min(((rlon+a)%360.0, (rlon-a)%360.0),
                 key=lambda z: abs(wrap180(l0-z)))
        def f(jd):
            lon,_=calc(pl,jd,flag)
            return wrap180(lon-ziel)
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
                lon,_=calc(pl,jd,flag)
                return jd, orb_for(lon,rlon,a)
        k=min(range(N+1), key=lambda i: abs(vs[i]))
        lo,hi=js[max(0,k-1)],js[min(N,k+1)]
        gr=(5.0**0.5-1.0)/2.0
        for _ in range(60):                    # Goldener Schnitt auf |f|
            m1=hi-gr*(hi-lo); m2=lo+gr*(hi-lo)
            if abs(f(m1))<abs(f(m2)): hi=m2
            else: lo=m1
        jd=(lo+hi)/2.0
        lon,_=calc(pl,jd,flag)
        return jd, orb_for(lon,rlon,a)

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
                        jd_ex,o_ex=refine_min(pl,flag,rlon,a,lo,hi)
                        groups.setdefault((tname,rname,aname),[]).append((jd_ex,o_ex))

    def perioden(orbs, schwelle):
        """zusammenhaengende Tagesbereiche mit orb <= schwelle -> [(von,bis)] als date."""
        out=[]; run_start=None
        for i,o in enumerate(orbs):
            if o<=schwelle and run_start is None: run_start=i
            elif o>schwelle and run_start is not None:
                out.append((day(run_start), day(i-1))); run_start=None
        if run_start is not None: out.append((day(run_start), day(len(orbs)-1)))
        return out

    events=[]
    for (tname,rname,aname),lst in groups.items():
        # Luecke, ab der zwei Orb-Perioden als getrennte Durchgaenge gelten (nicht als
        # Retro-Serie eines Kontakts): Mars kommt binnen eines Jahres wieder, die
        # langsamen nicht — ihre Dreifachkontakte liegen bis zu ~5 Monate auseinander.
        PASSAGE_LUECKE = 150 if tname=='Mars' else 210
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
            sel=[(jd,o) for jd,o in lst if pa<=d_from_jd(jd)<=pb]
            i0=max(0,(pa-t0).days); i1=min(len(orbs)-1,(pb-t0).days)
            mino=min([o for _,o in sel] + orbs[i0:i1+1])
            w=[(x,y) for x,y in p_wirk if x>=pa and y<=pb]
            exacts=[d_from_jd(jd) for jd,o in sel if o<=0.05]
            eng   =[(d_from_jd(jd),round(o,3)) for jd,o in sel if 0.05<o<=0.3]
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
                wird_exakt=bool(ex_im_fenster)))

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

    # --- JETZT: Momentaufnahme zum Stichtag ---------------------------------
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
            kontakte_gesamt=(e['kontakte'] if e else 0)))
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
    for e in events:
        if not e['im_wirkorb'] or e['spiegel'] or e['transit']=='Mars': continue
        if e['fenster_bis']<start.isoformat(): continue
        lang = (e['dauer_tage']>=lang_tage) or e['mehrfach'] or (e['transit'] in AEUSSERE)
        if not lang: continue
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
            lief_vor_start=(e['fenster_von']<start.isoformat())))
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
                quarter_bounds=[d.isoformat() for d in qb])

# ---------------------------------------------------------------------------
# Lesbarer Report
# ---------------------------------------------------------------------------
def format_report(res):
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
    out.append(f"Ephemeride: {res.get('ephe_modell','?')} fuer alle Faktoren")
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
    rows=[x for x in j['im_orb'] if not x['spiegel']]
    if not rows: out.append("     (keiner)")
    for x in rows:
        tag='P' if x['primaer'] else ' '
        kern='*' if x['im_wirkorb'] else ' '
        richt=x['richtung']+(' (kehrt zurueck)' if x.get('kehrt_zurueck') else '')
        s=(f"  [{tag}{kern}] {x['transit']:7s} {x['aspekt']:11s} {x['ziel']:12s} "
           f"orb {x['orb_grad']:4.2f}° {richt:22s}")
        if x['naechstes_exakt']: s+=f" exakt {x['naechstes_exakt']} (in {x['tage_bis']} T)"
        elif x['letztes_exakt']: s+=f" exakt war {x['letztes_exakt']} (vor {x['tage_seit']} T)"
        else: s+=f" wird nicht exakt (min {x['min_orb_grad']}°)"
        if x['fenster_bis']: s+=f" | bis {x['fenster_bis']}"
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
        ex=', '.join(x['exakt']) if x['exakt'] else f"nie exakt (min {x['min_orb_grad']}°)"
        flags=[]
        if x['lief_vor_start']: flags.append('laeuft schon')
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
                ex=f"streift {e['min_orb_grad']}°"
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
    """
    aus = {}
    jahr = 365.2422

    def alter(d):
        return (swe.julday(d.year, d.month, d.day, 12.0) - jd_geburt) / jahr

    # --- 1) progressiver Mond: 1 Tag nach Geburt = 1 Lebensjahr --------------
    pm = []
    d = start
    while d <= end:
        jd = jd_geburt + alter(d)
        lon = swe.calc_ut(jd, swe.MOON, SWIEPH)[0][0]
        eintrag = dict(datum=d.isoformat(), laenge=round(lon, 4),
                       stand=deg2sign(lon))
        if cusps:
            eintrag['haus'] = house_of(lon, cusps)
        pm.append(eintrag)
        d = plus_quartale(quartal_start(d), 1)
    aus['prog_mond'] = pm

    # --- 2) Sonnenbogen: alle Radixpunkte um den Sonnenbogen weitergerueckt --
    sb = []
    sonne0 = radix.get('Sonne')
    if sonne0 is not None:
        d = start
        while d <= end:
            jd = jd_geburt + alter(d)
            bogen = (swe.calc_ut(jd, swe.SUN, SWIEPH)[0][0] - sonne0) % 360.0
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
                                           bogen=round(bogen, 3)))
            d = d + timedelta(days=30)
    # je (Punkt, Aspekt, Ziel) nur den engsten Monat behalten
    eng = {}
    for e in sb:
        k = (e['punkt'], e['aspekt'], e['ziel'])
        if k not in eng or e['orb'] < eng[k]['orb']:
            eng[k] = e
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
            prof.append(dict(alter=a, haus=h + 1, zeichen=zeichen,
                             herrscher=herr,
                             herrscher_stand=(deg2sign(herr_lon)
                                              if herr_lon is not None else None),
                             herrscher_haus=(house_of(herr_lon, cusps)
                                             if herr_lon is not None else None),
                             klassisch=KLASSISCH.get(zeichen)))
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
                    r = fn(j, SWIEPH, 0, False)
                except Exception:
                    break
                t = r[1][0]
                if t > jd_end or t <= j:
                    break
                lon = swe.calc_ut(t, swe.SUN, SWIEPH)[0][0]
                if typ == 'Mondfinsternis':
                    lon = swe.calc_ut(t, swe.MOON, SWIEPH)[0][0]
                y, m, dd, _ = swe.revjul(t)
                treffer = [(n, round(orb_for(lon, l, 0), 3))
                           for n, l in radix.items()
                           if orb_for(lon, l, 0) <= 2.0]
                if treffer:
                    fin.append(dict(typ=typ, datum=date(y, m, dd).isoformat(),
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
    out.append("\n  -- Sonnenbogen-Kontakte im Fenster (Orb <= 1°, engster Monat) --")
    if not z.get('sonnenbogen'):
        out.append("     keine")
    for e in z.get('sonnenbogen', []):
        out.append("     %s  %-12s %-12s %-12s Orb %.2f°"
                   % (e['monat'], e['punkt'], e['aspekt'], e['ziel'], e['orb']))
    out.append("\n  -- Jahresprofektion --")
    for e in z.get('profektion', []):
        out.append("     Alter %d -> %d. Haus (%s), Herrscher %s%s%s"
                   % (e['alter'], e['haus'], e['zeichen'], e['herrscher'],
                      (" in %s" % e['herrscher_stand']) if e['herrscher_stand'] else "",
                      (", Haus %s" % e['herrscher_haus']) if e['herrscher_haus'] else ""))
    out.append("\n  -- Finsternisse auf Radixpunkten (Orb <= 2°) --")
    if not z.get('finsternisse'):
        out.append("     keine im Fenster")
    for e in z.get('finsternisse', []):
        zi = ", ".join("%s %.2f°" % (t['ziel'], t['orb']) for t in e['trifft'])
        out.append("     %s  %-16s %-18s -> %s"
                   % (e['datum'], e['typ'], e['stand'], zi))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    ap=argparse.ArgumentParser(description="Transit-Rechner: Jetzt + Langlaeufer + 8 Quartale")
    ap.add_argument("chart_data", help="Pfad zur <klient>_chart_data.md (Grundhoroskop)")
    ap.add_argument("--start", default=None, help="YYYY-MM-DD (Default: heute)")
    ap.add_argument("--asof", default=None, help="Stichtag der Jetzt-Aufnahme (Default: start)")
    ap.add_argument("--months", type=int, default=24)
    ap.add_argument("--lookback", type=int, default=LOOKBACK_M, help="Rueckblick in Monaten")
    ap.add_argument("--orb", type=float, default=ORB, help="Wirk-Orb (Deutung/Quartale)")
    ap.add_argument("--orb-weit", type=float, default=ORB_WEIT, help="Erfassungs-/Jetzt-Orb")
    ap.add_argument("--primary", default="", help="zusaetzliche primaere Ziele, kommagetrennt")
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
                         "Jahresprofektion, Finsternisse auf Radixpunkten)")
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
    try:
        res = run(radix, start=start, months=args.months, primary_extra=extra,
                  orb=args.orb, orb_weit=args.orb_weit, lookback_months=args.lookback,
                  cusps=cusps, asof=asof, mit_mars=args.mars,
                  ohne_chiron=args.ohne_chiron, tz=args.tz)
    except (ValueError, RuntimeError) as e:
        print("[FEHLER] %s" % e, file=sys.stderr)
        sys.exit(2)
    print(format_report(res))
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
        z = zusatzzeitmasse(radix, jdg, date.fromisoformat(res["start"]),
                            date.fromisoformat(res["end"]), cusps=cusps)
        res["zusatz"] = z
        print(format_zusatz(z))
    if args.json:
        json.dump(res, open(args.json,"w"), indent=1, ensure_ascii=False)
        print(f"\n[json -> {args.json}]")
