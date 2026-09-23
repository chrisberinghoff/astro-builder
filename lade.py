#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ladeweg fuer die Astro-Builder — stellt sie auf der Platte bereit und sagt,
welcher Schritt welche braucht.

Warum es dieses Modul gibt: Builder per `project_read` zu holen legt ihren
kompletten Quelltext in den Kontext (build.py allein ~18.000 Token) und der
bleibt dort fuer den Rest des Chats liegen. Ueber die Platte kosten sie null
Token.

DIE LEITER (Werkzeuge-Modul Punkt 3, Design-Render-Modul „Builder beschaffen";
hier neu gefasst am 2026-09-19, W5 — der alte Docstring beschrieb noch den
Repo-Download von lade.py per urlretrieve als ersten Schritt):

  Stufe 1 — der BUILDER-Ordner auf Chris' Rechner (Chris-Entscheidung
  2026-09-17). Alle .py des Ordners in EINEM device_stage_files-Aufruf holen,
  an den Arbeitsplatz kopieren, importieren:

    import glob, os, shutil, sys
    for q in glob.glob("/mnt/user-data/uploads/Projektanweisung und dateien/"
                       "BUILDER/*.py"):
        shutil.copy(q, "/home/claude/" + os.path.basename(q))
    sys.path.insert(0, "/home/claude")
    from lade import lade, lade_schritt, ephemeriden, uebersicht, pruefe_repo

  Stufe 2 — Rechner nicht verbunden oder das Stagen klemmt: `curl` aus dem
  Repo, einzeln nach den Namen aus SCHRITTE, ohne etwas auszufuehren:

    curl -sS -o /home/claude/<datei> <REPO><datei>

  Klemmen beide Stufen: anhalten und Chris fragen. `project_read` ist kein
  Ladeweg fuer Builder mehr (2026-09-19, W5): Er legte in einem Lauf rund
  620.000 Zeichen Quelltext inline in den Kontext und brachte grosse Builder
  trotzdem nicht auf die Platte. Code aus dem Netz AUSFUEHREN (python3 -c,
  Skriptdatei, timeout-Praefix) ist kein Weg.

lade() und lade_schritt() HOLEN NICHTS, WAS SCHON LOKAL LIEGT (seit
2026-09-19, W5). Vorher lud lade() jede Datei bei jedem Aufruf per urlretrieve
neu — anders als beide Module sagten — und ueberschrieb damit still die Kopien
aus dem BUILDER-Ordner mit dem Repo-Stand; hing der Repo-Upload nach, rechnete
der Lauf mit altem Code. Jetzt wird eine Datei, die unter `ziel` (Vorgabe
/home/claude) liegt, nur auf Nullgroesse und gueltiges Python geprueft; aus
dem Repo geholt wird allein, was dort fehlt. `frisch=True` holt trotzdem neu
und ueberschreibt — nur auf Chris' Ansage.

Dann EINE Zeile je Schritt — welche Builder das sind, steht in SCHRITTE und
nirgends sonst:

    lade_schritt("1")         # Datenblatt
    lade_schritt("2")         # Referenzschnitt
    lade_schritt("3+4")       # Design/Render
    lade_schritt("transit")   # zusaetzlich beim Transit-Lauf

`lade("build", "chartdoc")` von Hand geht weiter und ist fuer Einzelproben
richtig; fuer einen normalen Lauf ist `lade_schritt()` vorzuziehen, weil die
Liste dann nicht chatweise abweichen kann.

`uebersicht()` druckt, welcher Schritt was zieht — das ist die Antwort auf
"von wo wird was geholt", und die Anweisungsmodule verweisen darauf, statt
eigene Listen zu fuehren (Chris-Entscheidung 2026-09-08; die Listen standen
dreifach und liefen dreifach auseinander).

`pruefe_repo()` haelt BEKANNT gegen das echte Repo — einmal laufen lassen,
wenn ein Builder sich merkwuerdig verhaelt.

Alle Builder liegen im BUILDER-Ordner und im Repo, hd.py und
REFERENZ_Chart_Builder_Ultimativ.py seit dem 2026-09-08 ebenfalls (davor per
project_read, weil sie Klientendaten trugen — die sind an dem Tag anonymisiert
worden). NICHT ueber diesen Weg: blocks_bundle.txt (die Bibliothek selbst,
Werkzeuge-Modul Punkt 1) und alle .md-Module, die nur im Projektwissen liegen.

Wer wirklich rechnet — Pholus in Schritt 1, transit.py im Transit-Lauf —
braucht die Swiss-Ephemeris-Dateien. EINE Zeile beschafft sie
und liefert gleich ihr Verzeichnis:

    from lade import ephemeriden
    ephe = ephemeriden()          # installiert nur, wenn noetig
    swe.set_ephe_path(ephe)       # bzw. --ephe <ephe> an transit.py

Welche Pakete das sind, steht in PAKETE und nirgends sonst (Chris-Entscheidung
2026-09-08). Die Zeilen standen vorher in drei Modulen in drei verschieden guten
Fassungen — Einzelheiten im Kommentar ueber PAKETE.

Ohne die Dateien faellt transit.py fuer die Hauptplaneten auf Moshier zurueck
(bis zu einer Bogensekunde bei den Langsamen) und kann Transit-Chiron gar nicht
rechnen; seit dem 2026-09-06 bricht es in dem Fall ab. `lade()` nennt darum beim
Laden von `transit` den naechsten Schritt `ephemeriden()`, solange keine
`seas_*.se1` erreichbar ist — seit 2026-09-19 (F23) als Hinweis, nicht als
Warnung: In der vorgeschriebenen Reihenfolge (erst lade_schritt("transit"),
dann ephemeriden()) sind die Dateien in einem frischen Container an dieser
Stelle nie da.

Selbsttest ohne Netz: `python3 lade.py` (urlretrieve gemockt). Mit
`python3 lade.py --netz` zusaetzlich der alte Repo-Test (holt alle Builder
frisch nach /tmp/ladeselbsttest).
"""

import glob
import importlib
import os
import pathlib
import py_compile
import site
import subprocess
import sys
import urllib.request

REPO = "https://raw.githubusercontent.com/chrisberinghoff/astro-builder/main/"

BEKANNT = {
    "build", "chartdoc", "radix", "transit", "transitdata",
    "transituhr_fusion", "transituhr", "selektor", "markiere", "restyle",
    "hd", "REFERENZ_Chart_Builder_Ultimativ",
    "REFERENZ_Chart_Builder_Geburtshoroskop",   # seit 2026-09-20 (D3, K7): schlanke Vorlage fuer das Geburtshoroskop
    "inhaltsprobe",          # seit 2026-09-16: Analyse gegen chart_data (Schritt 2 und 3+4)
    "lade",
}

# Welche Builder ein Schritt braucht — DIE EINZIGE VERBINDLICHE FASSUNG.
#
# Warum hier und nicht in den Anweisungsmodulen (Chris-Entscheidung 2026-09-08):
# Die Staffelung stand in DREI Fassungen — Werkzeuge-Modul, Design-Render-Modul
# und im Docstring dieser Datei — und alle drei sind mehrfach auseinandergelaufen.
# Zuletzt fehlte `restyle` in allen drei Modul-Listen, obwohl es im Repo liegt,
# und der Docstring hier nannte fuer Schritt 1 nur `radix` ohne `build`, womit
# `build.aspekt_heimat_bericht()` in der Heimat-Probe ins Leere lief. Dieselbe
# Begruendung wie bei `_ephemeriden_warnung()`: `lade()` ist die einzige Stelle,
# durch die JEDER Lauf geht, egal welches Modul er gelesen hat.
#
# Die Module nennen ab jetzt keine Dateilisten und keine Aufrufe mehr, sondern
# verweisen hierher. Wer wissen will, was ein Schritt zieht: `uebersicht()`.
SCHRITTE = {
    # `selektor` seit dem 2026-09-19 (W40): Die Referenzdatei-Liste am Ende von
    # Schritt 1 kommt aus `selektor.py --liste` (Nur-Liste-Modus, ohne
    # Bibliothek). Ein Import kostet keine Token.
    "1":        ("radix", "build", "selektor"),
    # Schritt 2 zieht seit dem 2026-09-16 auch `build` (das Werkzeuge-Modul
    # verlangt dort `build.parse_analyse()`) und `inhaltsprobe` (Analyse gegen
    # chart_data, nach dem Schreiben); Schritt 3+4 laesst die Inhaltsprobe vor
    # dem Render laufen. Startprompt claude/STARTPROMPT_Inhaltsprobe_2026-09-16.md.
    # `chartdoc` seit dem 2026-09-17 (Klasse-2-Entscheidungslauf,
    # Wiederholungstaeter aus zwei Laufabschnitten): Der Kern verlangt in
    # Arbeitsablauf 2 ausdruecklich `chartdoc.pruefe_kapitelkopf()` — die harte
    # Kicker-Probe, die seit dem 2026-09-08 einen fehlenden Kicker abbricht.
    # Schritt 2 lieferte chartdoc aber nicht, und der Aufruf brach mit
    # ModuleNotFoundError ab. Ein Import kostet keine Token; die Alternative waere
    # gewesen, den Kern zu aendern, damit er weniger verlangt.
    "2":        ("selektor", "build", "inhaltsprobe", "chartdoc"),
    # `selektor` gehoert auch zu 3+4: inhaltsprobe.py importiert es (Zeile
    # `import selektor`), und ohne den Eintrag brach der erste Aufruf im
    # Design-Lauf mit ModuleNotFoundError ab (Pruefbericht Geburtshoroskop
    # Schritt 3+4 vom 2026-09-16d, Klasse 1 Nr. 1.1).
    "3+4":      ("build", "chartdoc", "radix", "selektor", "inhaltsprobe"),
    "transit":  ("transit", "transitdata", "transituhr_fusion"),
    "restyle":  ("build", "chartdoc", "radix", "restyle"),
    "hdgk":     ("hd",),
    "bibliothek": ("markiere", "selektor"),
}

# Was ein Schritt bedeutet — nur fuer die Ausgabe von uebersicht().
_SCHRITT_TEXT = {
    "1":        "Datenblatt (Heimat-Probe braucht build, Referenzdatei-Liste selektor)",
    "2":        "Referenzschnitt, Schemapruefung und Inhaltsprobe der Analyse",
    "3+4":      "Design, HTML, Rendern, Pruefen (Inhaltsprobe vor dem Render)",
    "transit":  "zusaetzlich beim Transit-Lauf",
    "restyle":  "Schreibweise-Wechsel einer fertigen Analyse",
    "hdgk":     "Human Design / Gene Keys",
    "bibliothek": "Bibliotheks-Umbau und Selektor-Pflege",
}


def ephemeriden_pfad():
    """Erstes Verzeichnis mit einer `seas_*.se1`, sonst None.

    Sucht in derselben Reihenfolge wie transit.py: Umgebungsvariable
    SE_EPHE_PATH, dann die Paketverzeichnisse, dann die ueblichen Systemorte.
    Rein lesend, installiert nichts.
    """
    kandidaten = []
    env = os.environ.get("SE_EPHE_PATH")
    if env:
        kandidaten += env.split(os.pathsep)
    basen = list(site.getsitepackages()) if hasattr(site, "getsitepackages") else []
    basis = site.getusersitepackages() if hasattr(site, "getusersitepackages") else None
    if basis:
        basen.append(basis)
    for b in basen:
        kandidaten.append(os.path.join(b, "flatlib", "resources", "swefiles"))
    kandidaten += ["/usr/share/swisseph", "/usr/local/share/swisseph"]
    for d in kandidaten:
        if d and os.path.isdir(d) and glob.glob(os.path.join(d, "seas_*.se1")):
            return d
    # Letzter Versuch: irgendwo unter /usr
    treffer = glob.glob("/usr/**/flatlib/resources/swefiles", recursive=True)
    return treffer[0] if treffer else None


# Die Pakete, die die Swiss-Ephemeris-Dateien beschaffen — DIE EINZIGE
# VERBINDLICHE FASSUNG (Chris-Entscheidung 2026-09-08).
#
# Warum hier: Die Installationszeilen standen an DREI produktiven Stellen —
# Datenblatt-Modul, Werkzeuge-Modul und Design-Render-Modul — und die drei waren
# nicht nur doppelt, sondern technisch verschieden gut. Das Datenblatt-Modul rief
# `sys.executable -m pip`, die anderen beiden das `pip` aus dem PATH; in einer
# Umgebung mit mehreren Interpretern installiert das ins falsche Ziel. Am
# 2026-09-06 hatte das Design-Modul ausserdem `flatlib` schlicht nicht genannt,
# und ein Schritt-3-Lauf liest laut Kern nur dieses eine Modul (Pruefbericht
# Transit 4.5). Dieselbe Begruendung wie bei SCHRITTE: `lade()` ist die einzige
# Stelle, durch die jeder Lauf geht.
#
# `flatlib` wird nur wegen der mitgelieferten swefiles installiert (sepl_*,
# semo_*, seas_*), nicht als Bibliothek — daher `--no-deps`.
PAKETE = (
    ("pyswisseph", ()),
    ("flatlib", ("--no-deps",)),
)


def _swisseph_importierbar():
    """True, wenn `import swisseph` (Paket pyswisseph) gelingt.

    Neu 2026-09-16 (Pruefbericht Geburtshoroskop Schritt 1+2, dritter Lauf, Befund 1.1).
    `ephemeriden()` prueft nach der Installation nur, ob die Ephemeriden-DATEIEN da
    sind — die kommen aus `flatlib`. Bricht der `pyswisseph`-Download ab (im Prueflauf
    ein ReadTimeout des Proxys), laeuft `pip` mit check=False still durch, `flatlib`
    kommt trotzdem an, die Dateien sind da, und die Funktion meldete "Ephemeriden
    installiert" — der naechste `import swisseph` brach dann mit ModuleNotFoundError
    ab. Dieselbe Klasse Fehler wie die fehlende Ephemeriden-Datei vor dem 2026-09-06
    (nur als Hinweis gemeldet), diesmal auf der Paketseite.

    `invalidate_caches()` ist noetig: Ein Paket, das im laufenden Interpreter eben
    erst installiert wurde, sieht der Importer sonst nicht.
    """
    importlib.invalidate_caches()
    try:
        importlib.import_module("swisseph")
        return True
    except ImportError:
        return False


def ephemeriden(still=False):
    """Sorgt dafuer, dass die Swiss-Ephemeris-Dateien da sind, und gibt ihr
    Verzeichnis zurueck — fuer `swe.set_ephe_path(...)` bzw. `--ephe <...>`.

        from lade import ephemeriden
        import swisseph as swe
        swe.set_ephe_path(ephemeriden())

    Installiert nur, wenn die Dateien fehlen; sind sie schon da, kostet der
    Aufruf nichts. Nimmt `sys.executable -m pip`, trifft also immer den
    laufenden Interpreter.

    Ersetzt in den Modulen die pip-Zeilen UND die Pfadsuche per
    `glob.glob("/usr/**/flatlib/resources/swefiles", recursive=True)[0]` — die
    warf einen IndexError, wenn nichts gefunden wurde, statt zu sagen was fehlt.

    Prueft seit dem 2026-09-16 auch, ob `pyswisseph` importierbar ist — Dateien
    ohne Paket sind derselbe Ausfall wie Paket ohne Dateien (Befund 1.1 des
    Pruefberichts Geburtshoroskop Schritt 1+2 vom 16.09., dritter Lauf). Fehlt das
    Paket, wird einmal nachinstalliert (ein Download-Timeout des Proxys ist im
    naechsten Moment meist weg); bleibt es weg, harter Fehler mit dem pip-Befehl.

    ERSTINSTALLATION IN EINEM FRISCHEN CONTAINER IST TEUER (hierher gezogen
    2026-09-17, Klasse-2-Entscheidungslauf; stand vorher als vier Zeilen im
    Werkzeuge-Modul und lief damit in jedem Chart-Lauf mit, obwohl der Fall je
    Container genau EINMAL auftritt). `pyswisseph` wird aus dem Quelltext gebaut
    und ueberschreitet das Standard-Zeitlimit des Bash-Werkzeugs von zwei
    Minuten; im Prueflauf vom 16.09. kostete das zwei Abbrueche (Lesetimeout von
    files.pythonhosted.org, dann Exit 143) und rund vier Minuten vor dem ersten
    Rechenschritt. Wer diese Funktion in einem frischen Container ruft, gibt dem
    Bash-Aufruf MINDESTENS FUENF MINUTEN Zeitlimit und installiert die beiden
    Pakete getrennt. Im Dauerbetrieb kostet der Aufruf nichts.

    Die pip-Warnung "flatlib requires pyswisseph==2.08.00-1, but you have
    pyswisseph <neuer>" bei der Erstinstallation ist HARMLOS und erwartet
    (erklaert 2026-09-17): `flatlib` wird mit `--no-deps` allein wegen seiner
    mitgelieferten swefiles installiert, nicht als Bibliothek — seine
    Versionsforderung an pyswisseph spielt hier keine Rolle. Sie war bis dahin
    unerklaert und stand als Befund in der Klasse-2-Liste.

    Wirft, wenn die Dateien auch nach der Installation nicht auffindbar sind.
    Nicht abfangen: Ohne sie rechnet der Builder auf Moshier (bis zu einer
    Bogensekunde bei den Langsamen, ein Exaktpunkt nahe Mitternacht kann auf den
    Nachbartag kippen) und Transit-Chiron gar nicht — seit dem 2026-09-06 ein
    harter Fehler. Bewusst ohne Chiron rechnet man mit `--ohne-chiron`.
    """
    pfad = ephemeriden_pfad()
    if pfad and _swisseph_importierbar():
        if not still:
            print("Ephemeriden schon da:", pfad)
        return pfad

    # Dateien da, aber Paket nicht importierbar: nur pyswisseph nachziehen.
    # Sonst beide Pakete (PAKETE ist die einzige verbindliche Liste).
    pakete = [p for p in PAKETE if p[0] == "pyswisseph"] if pfad else list(PAKETE)
    if not still and len(pakete) > 1:
        print("[lade] Erstinstallation der Ephemeriden-Pakete: pyswisseph wird "
              "gebaut, das dauert im frischen Container mehrere Minuten — "
              "Bash-Zeitlimit auf mindestens 5 Minuten setzen. Die pip-Warnung "
              "'flatlib requires pyswisseph==2.08.00-1' ist harmlos (flatlib "
              "kommt mit --no-deps, nur wegen der swefiles).", file=sys.stderr)
    for paket, extra in pakete:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", paket, *extra,
             "--break-system-packages", "-q"],
            check=False,
        )

    if not _swisseph_importierbar():
        # Einmal nachfassen — dieselbe Regel wie beim Ladeweg ("einmal mit curl
        # nachfassen", Werkzeuge-Modul): Ein Timeout des Proxys ist meist vorbei.
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyswisseph",
             "--break-system-packages", "-q"],
            check=False,
        )
    if not _swisseph_importierbar():
        raise RuntimeError(
            "pyswisseph ist nach zwei Installationsversuchen nicht importierbar "
            "(`import swisseph` schlaegt fehl) — pip hat den Download vermutlich "
            "abgebrochen (Timeout). Von Hand: "
            + sys.executable + " -m pip install pyswisseph --break-system-packages"
        )

    pfad = ephemeriden_pfad()
    if not pfad:
        raise RuntimeError(
            "Swiss-Ephemeris-Dateien (seas_*.se1) auch nach der Installation "
            "nicht gefunden. Installiert wurden: "
            + ", ".join(p for p, _ in PAKETE)
            + ". Pruefen, ob pip durchlief; notfalls das Verzeichnis von Hand "
              "an --ephe uebergeben."
        )
    if not still:
        print("Ephemeriden installiert:", pfad)
    return pfad


def _ephemeriden_warnung():
    """Warnt, wenn `transit` geladen wird, ohne dass die swefiles da sind.

    Warum hier (2026-09-07, Prueflauf Transit 4.5): Die Installationszeilen
    standen in ZWEI Modulen und sind auseinandergelaufen — das Design-Modul
    nannte nur `pyswisseph`, das Werkzeuge-Modul beide Zeilen. Ein
    Schritt-3-Lauf liest laut Kern nur das Design-Modul und installiert damit
    die falsche Menge. `lade()` ist die einzige Stelle, durch die JEDER Lauf
    geht, egal welches Modul er gelesen hat — die Warnung gehoert deshalb
    hierher und nicht in eine dritte Modulzeile.

    Bewusst nur eine Warnung, kein Abbruch: ein Schritt-3-Lauf laedt `transit`
    regelmaessig mit, ohne je zu rechnen (er parst nur den fertigen Report aus
    der chart_data). Wer wirklich rechnet, bekommt in transit.py den harten
    Fehler.

    SEIT 2026-09-19 (F23, T12-18c Nr. 26) ein HINWEIS auf den naechsten
    Schritt statt „[WARNUNG]" auf stderr: Die Module schreiben die Reihenfolge
    lade_schritt("transit") -> ephemeriden() vor, und in einem frischen
    Container sind die Dateien an dieser Stelle nie da. Die Warnung schlug
    deshalb in jedem Transit-Lauf an, und vier Pruefberichte fuehrten sie als
    Meldung, obwohl nichts fehlte.
    """
    if ephemeriden_pfad():
        return
    print(
        "[lade] Hinweis, kein Fehler: transit ist geladen, die "
        "Swiss-Ephemeris-Dateien (seas_*.se1) sind\n"
        "  noch nicht geholt — in einem frischen Container normal. Vor dem "
        "ersten Rechenlauf von transit.py:\n"
        "      from lade import ephemeriden\n"
        "      ephe = ephemeriden()      # installiert nur, wenn noetig, und "
        "liefert den Pfad fuer --ephe\n"
        "  Wer nur den fertigen Report aus der chart_data parst "
        "(Schritt 3+4), braucht sie nicht.\n"
        "  Rechnet transit.py ohne sie, bricht es selbst hart ab."
    )


def lade(*module, ziel="/home/claude", frisch=False, still=False):
    """Builder bereitstellen: was unter `ziel` liegt, nehmen; nur FEHLENDES aus
    dem Repo holen; `ziel` in den sys.path legen.

    module  Modulnamen ohne oder mit .py — `lade("build", "chartdoc")`
    ziel    Zielverzeichnis, Vorgabe /home/claude (dort erwarten die Builder
            einander; build.BASE_DIR und die sys.path-Zeilen in chartdoc.py und
            den Uhr-Modulen sind fest darauf eingestellt). Hierhin kopiert
            Stufe 1 die Dateien aus dem BUILDER-Ordner, hierhin schreibt Stufe 2
            per curl.
    frisch  True holt AUCH vorhandene Dateien neu aus dem Repo und
            UEBERSCHREIBT die lokale Kopie; umgeht dabei den ~5-Minuten-Cache
            von raw.githubusercontent.com. Nur auf Chris' Ansage, etwa direkt
            nach einem Repo-Upload — sonst gilt der BUILDER-Ordner.
    still   True unterdrueckt die Erfolgsmeldung

    SEIT 2026-09-19 (W5): Eine Datei, die schon unter `ziel` liegt, wird NICHT
    mehr geladen. Vorher lief urlretrieve bei jedem Aufruf und ueberschrieb
    still die Kopien aus dem BUILDER-Ordner mit dem Repo-Stand — anders als
    Werkzeuge- und Design-Render-Modul sagten („laedt nichts mehr nach").

    Prueft jede Datei — lokal vorgefundene wie frisch geholte — auf
    Nullgroesse und laesst sie von py_compile uebersetzen. Damit faellt eine
    Fehlerseite, die der Proxy statt der Datei ausliefert, oder eine
    abgeschnittene Kopie sofort auf — und nicht erst als raetselhafter
    SyntaxError mitten im Render.

    Rueckgabe: LISTE der Dateinamen in der Reihenfolge von `module` (lokal
    vorgefundene und geholte), kein dict.

    Wirft bei jedem Fehlschlag. NICHT abfangen und stillschweigend auf eine
    Altfassung ausweichen: Klemmt der Ladeweg, anhalten und Chris fragen.
    """
    pfad_ziel = pathlib.Path(ziel)
    pfad_ziel.mkdir(parents=True, exist_ok=True)

    geladen = []            # (Dateiname, Anzeige) in der Reihenfolge von `module`
    for m in module:
        name = m if m.endswith(".py") else m + ".py"
        stamm = name[:-3]
        if stamm not in BEKANNT:
            raise ValueError(
                f"{name} ist nicht im Repo. Verfuegbar: "
                + ", ".join(sorted(BEKANNT - {'lade'}))
            )
        pfad = pfad_ziel / name
        if pfad.exists() and not frisch:
            # 2026-09-19 (W5): lokal vorhanden -> nicht holen, nur pruefen.
            if pfad.stat().st_size == 0:
                raise RuntimeError(
                    f"{name} liegt unter {ziel}, ist aber LEER. Die Kopie aus dem "
                    "BUILDER-Ordner neu stagen und kopieren (Stufe 1) oder die "
                    "Datei per curl holen (Stufe 2); klemmt beides: anhalten und "
                    "Chris fragen.")
            try:
                py_compile.compile(str(pfad), cfile="/tmp/_ladecheck.pyc",
                                   doraise=True)
            except py_compile.PyCompileError as e:
                raise RuntimeError(
                    f"{name} liegt unter {ziel}, ist aber kein gueltiges Python "
                    "(abgeschnittene oder falsche Datei?). Die Kopie aus dem "
                    "BUILDER-Ordner neu stagen und kopieren (Stufe 1) oder per "
                    "curl holen (Stufe 2); klemmt beides: anhalten und Chris "
                    "fragen."
                ) from e
            geladen.append((name, f"{name} ({pfad.stat().st_size} B, lokal)"))
            continue
        url = REPO + name + ("?frisch=1" if frisch else "")
        try:
            urllib.request.urlretrieve(url, pfad)
        except Exception as e:
            # 2026-09-19 (W5): Stufe 3 (project_read) ist gestrichen.
            raise RuntimeError(
                f"{name} liess sich nicht aus dem Repo laden ({type(e).__name__}: "
                f"{e}). Ladeweg klemmt — anhalten und Chris fragen. Liegt die "
                f"Datei nicht unter {ziel}: Stufe 1 (BUILDER-Ordner per "
                "device_stage_files) oder Stufe 2 (curl) nehmen; project_read "
                "ist kein Ladeweg fuer Builder."
            ) from e
        if pfad.stat().st_size == 0:
            raise RuntimeError(f"{name} kam leer an — Ladeweg pruefen")
        try:
            py_compile.compile(str(pfad), cfile="/tmp/_ladecheck.pyc", doraise=True)
        except py_compile.PyCompileError as e:
            raise RuntimeError(
                f"{name} kam beschaedigt an (kein gueltiges Python). "
                "Vermutlich hat der Proxy eine Fehlerseite geliefert statt der Datei."
            ) from e
        geladen.append((name, f"{name} ({pfad.stat().st_size} B, aus dem Repo)"))

    if ziel not in sys.path:
        sys.path.insert(0, ziel)

    if not still:
        print("geladen:", ", ".join(a for _, a in geladen))
    if any((m[:-3] if m.endswith(".py") else m) == "transit" for m in module):
        _ephemeriden_warnung()
    return [n for n, _ in geladen]


def lade_schritt(schritt, **kw):
    """Stellt genau die Builder bereit, die dieser Schritt braucht — s.
    SCHRITTE. Holt seit 2026-09-19 (W5) nur, was unter `ziel` fehlt.

        lade_schritt("1")        # Datenblatt
        lade_schritt("3+4")      # Design/Render
        lade_schritt("transit")  # zusaetzlich beim Transit-Lauf

    Nimmt dieselben Zusatzargumente wie lade() (ziel, frisch, still).
    Vorzuziehen gegenueber lade("a", "b", ...) von Hand: die Liste steht dann
    an genau einer Stelle und kann nicht chatweise abweichen.

    Rueckgabe: LISTE der Dateinamen, genau wie lade() sie liefert — KEIN dict.
    Also `list(mods)` und nicht `mods.keys()`; der naheliegende zweite Aufruf
    bricht mit `AttributeError: 'list' object has no attribute 'keys'` ab.
    """
    if schritt not in SCHRITTE:
        raise ValueError(
            f"Unbekannter Schritt {schritt!r}. Bekannt: "
            + ", ".join(sorted(SCHRITTE))
        )
    return lade(*SCHRITTE[schritt], **kw)


def pruefe_repo(still=False):
    """Haelt BEKANNT gegen das, was wirklich im Repo liegt.

    Ohne diese Probe faellt eine Divergenz erst auf, wenn ein Lauf bricht —
    beim `transituhr_fusion`-Fund vom 2026-09-08 hatte sie fuenf Wochen
    unbemerkt bestanden. Gibt (fehlend, ueberzaehlig) zurueck; beides leer
    heisst: Liste und Repo sagen dasselbe.

    Rein lesend, aendert nichts. Braucht Netz.
    """
    fehlend, da = [], []
    for name in sorted(BEKANNT):
        req = urllib.request.Request(REPO + name + ".py", method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                (da if r.status == 200 else fehlend).append(name)
        except Exception:
            fehlend.append(name)
    if not still:
        if fehlend:
            print("NICHT im Repo, obwohl in BEKANNT:", ", ".join(fehlend))
        else:
            # Zaehlung ausdruecklich benannt: BEKANNT enthaelt `lade` selbst,
            # die Liste in uebersicht() blendet es aus. Bis zum 2026-09-09
            # sagten beide nur eine Zahl — 13 hier, 12 dort — und keine sagte,
            # was sie zaehlt (Pruefbericht Geburtshoroskop Schritt 3+4).
            print(f"Repo-Probe: alle {len(da)} Dateien aus BEKANNT sind da "
                  f"({len(da) - 1} Builder + lade.py selbst).")
    return fehlend, []


def uebersicht():
    """Druckt, welcher Schritt was zieht und woher — die Antwort auf
    'von wo wird was geholt'. Die Anweisungsmodule verweisen hierher,
    statt eigene Listen zu fuehren."""
    # 2026-09-19 (W5): Die Quelle ist nicht mehr „immer das Repo".
    print("Ladeweg — Stufe 1: BUILDER-Ordner per device_stage_files, nach "
          "/home/claude kopiert;")
    print("          Stufe 2: curl aus", REPO)
    print("          lade()/lade_schritt() holen nur, was lokal fehlt "
          "(frisch=True: alles neu).")
    print("\nJe Schritt:")
    for s, mods in SCHRITTE.items():
        print("  lade_schritt(%-12s -> %-42s # %s"
              % (repr(s) + ")", ", ".join(mods), _SCHRITT_TEXT.get(s, "")))
    print("\nAlle bekannten Builder (%d, ohne lade.py selbst):"
          % len(BEKANNT - {"lade"}))
    print("  " + ", ".join(sorted(BEKANNT - {"lade"})))
    print("\nEphemeriden (nur wer rechnet — Pholus, transit.py):")
    print("  ephe = ephemeriden()   installiert %s und liefert den Pfad"
          % " + ".join(p for p, _ in PAKETE))
    print("\nNicht ueber diesen Weg, weiter per project_read:")
    print("  blocks_bundle.txt (die Bibliothek selbst) und alle .md-Module.")
    print("\nSchnittstellen ohne Quelltext-Lektuere (seit 2026-09-20, D3):")
    print("  <builder>.hilfe()            Uebersicht aller Funktionen und Konstanten")
    print("  <builder>.hilfe('<name>')    voller Docstring: Argumente, Rueckgabeschluessel")
    print("  python3 <builder>.py --hilfe [<name>]   dasselbe von der Kommandozeile")


def _selbsttest():
    """Selbsttest OHNE Netz (neu 2026-09-19, W5 und F23): urlretrieve gemockt,
    Temp-Verzeichnis. Prueft: vorhandene Dateien werden nicht geholt und nicht
    ueberschrieben, fehlende schon; frisch=True holt neu; leere oder kaputte
    lokale Kopie und ein scheiternder Abruf werfen mit klarer Meldung (ohne
    project_read); lade_schritt("1") enthaelt selektor (W40); der
    Ephemeriden-Hinweis ist keine Warnung mehr."""
    import contextlib
    import io
    import tempfile
    from unittest import mock

    abrufe = []

    def falscher_abruf(url, pfad):
        abrufe.append(url)
        pathlib.Path(pfad).write_text("GEHOLT = True\n", encoding="utf-8")
        return str(pfad), None

    pfad_vorher = list(sys.path)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            (pathlib.Path(tmp) / "build.py").write_text("LOKAL = True\n",
                                                        encoding="utf-8")
            with mock.patch.object(urllib.request, "urlretrieve", falscher_abruf):
                namen = lade("build", "chartdoc", ziel=tmp, still=True)
                assert namen == ["build.py", "chartdoc.py"], namen
                assert [u.rsplit("/", 1)[-1] for u in abrufe] == ["chartdoc.py"], abrufe
                assert "LOKAL" in (pathlib.Path(tmp) / "build.py").read_text(
                    encoding="utf-8"), "lokale Datei wurde ueberschrieben"
                abrufe.clear()
                lade("build", ziel=tmp, frisch=True, still=True)
                assert abrufe and abrufe[0].endswith("build.py?frisch=1"), abrufe
                assert "GEHOLT" in (pathlib.Path(tmp) / "build.py").read_text(
                    encoding="utf-8")
                abrufe.clear()
                namen = lade_schritt("1", ziel=tmp, still=True)
                assert "selektor.py" in namen, namen
            (pathlib.Path(tmp) / "radix.py").write_text("", encoding="utf-8")
            try:
                lade("radix", ziel=tmp, still=True)
                raise AssertionError("leere lokale Datei nicht erkannt")
            except RuntimeError as e:
                assert "LEER" in str(e) and "Chris fragen" in str(e), e
            (pathlib.Path(tmp) / "radix.py").write_text("def kaputt(:\n",
                                                        encoding="utf-8")
            try:
                lade("radix", ziel=tmp, still=True)
                raise AssertionError("kaputte lokale Datei nicht erkannt")
            except RuntimeError as e:
                assert "kein gueltiges Python" in str(e), e

            def abruf_scheitert(url, pfad):
                raise OSError("kein Netz (Selbsttest)")

            with mock.patch.object(urllib.request, "urlretrieve", abruf_scheitert):
                try:
                    lade("hd", ziel=tmp, still=True)
                    raise AssertionError("gescheiterter Abruf nicht gemeldet")
                except RuntimeError as e:
                    assert "anhalten und Chris fragen" in str(e), e
                    assert "auf project_read zurueckfallen" not in str(e), e
            puffer, fehler = io.StringIO(), io.StringIO()
            with mock.patch(__name__ + ".ephemeriden_pfad", return_value=None), \
                    contextlib.redirect_stdout(puffer), \
                    contextlib.redirect_stderr(fehler):
                _ephemeriden_warnung()
            text = puffer.getvalue() + fehler.getvalue()
            assert "WARNUNG" not in text and "ephemeriden()" in text, text
            assert not fehler.getvalue(), "Hinweis gehoert nicht nach stderr"
    finally:
        sys.path[:] = pfad_vorher
    print("[lade-Selbsttest ohne Netz bestanden: lokal vorhandene Dateien "
          "bleiben (W5), frisch=True holt neu, klare Fehlermeldungen, "
          "Schritt 1 mit selektor (W40), Ephemeriden-Hinweis (F23)]")


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
    if _hilfe_cli():          # python3 lade.py --hilfe [<name>]
        raise SystemExit(0)
    _selbsttest()
    if "--netz" in sys.argv[1:]:
        # Der bisherige Selbsttest: holt alle Builder aus dem Repo und meldet,
        # ob jeder ankommt. Seit 2026-09-19 mit frisch=True — sonst naehme er
        # Dateien, die von einem frueheren Lauf in /tmp/ladeselbsttest liegen,
        # und pruefte das Repo gar nicht.
        alle = sorted(BEKANNT - {"lade"})
        lade(*alle, ziel="/tmp/ladeselbsttest", frisch=True)
        print(f"\n[Selbsttest bestanden: {len(alle)} Builder geladen und uebersetzbar]")
    print()
    uebersicht()
