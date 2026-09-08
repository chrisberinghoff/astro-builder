#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ladeweg fuer die Astro-Builder — holt sie aus dem Repo direkt auf die Disk.

Warum es dieses Modul gibt: Builder per `project_read` zu holen legt ihren
kompletten Quelltext in den Kontext (build.py allein ~18.000 Token) und der
bleibt dort fuer den Rest des Chats liegen. Ueber diesen Weg landen sie
ausschliesslich auf der Platte und kosten null Token.

Verwendung — zwei Zeilen am Anfang des Laufs:

    import urllib.request; urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/chrisberinghoff/astro-builder/main/lade.py",
        "/home/claude/lade.py")
    import sys; sys.path.insert(0, "/home/claude")
    from lade import lade, lade_schritt, ephemeriden, uebersicht, pruefe_repo

Dann EINE Zeile je Schritt — welche Builder das sind, steht in SCHRITTE und
nirgends sonst:

    lade_schritt("1")         # Datenblatt
    lade_schritt("2")         # Referenzschnitt
    lade_schritt("3+4")       # Design/Render
    lade_schritt("transit")   # zusaetzlich beim Transit-/Ultimativ-Lauf

`lade("build", "chartdoc")` von Hand geht weiter und ist fuer Einzelproben
richtig; fuer einen normalen Lauf ist `lade_schritt()` vorzuziehen, weil die
Liste dann nicht chatweise abweichen kann.

`uebersicht()` druckt, welcher Schritt was zieht — das ist die Antwort auf
"von wo wird was geholt", und die Anweisungsmodule verweisen darauf, statt
eigene Listen zu fuehren (Chris-Entscheidung 2026-09-08; die Listen standen
dreifach und liefen dreifach auseinander).

`pruefe_repo()` haelt BEKANNT gegen das echte Repo — einmal laufen lassen,
wenn ein Builder sich merkwuerdig verhaelt.

Alle Builder kommen aus dem Repo, hd.py und REFERENZ_Chart_Builder_Ultimativ.py
seit dem 2026-09-08 ebenfalls (davor per project_read, weil sie Klientendaten
trugen — die sind an dem Tag anonymisiert worden). NICHT ueber diesen Weg:
blocks_bundle.txt (die Bibliothek selbst) und alle .md-Module, die nur im
Projektwissen liegen.

Wer wirklich rechnet — Pholus in Schritt 1, transit.py im Transit- und
Ultimativ-Lauf — braucht die Swiss-Ephemeris-Dateien. EINE Zeile beschafft sie
und liefert gleich ihr Verzeichnis:

    from lade import ephemeriden
    ephe = ephemeriden()          # installiert nur, wenn noetig
    swe.set_ephe_path(ephe)       # bzw. --ephe <ephe> an transit.py

Welche Pakete das sind, steht in PAKETE und nirgends sonst (Chris-Entscheidung
2026-09-08). Die Zeilen standen vorher in drei Modulen in drei verschieden guten
Fassungen — Einzelheiten im Kommentar ueber PAKETE.

Ohne die Dateien faellt transit.py fuer die Hauptplaneten auf Moshier zurueck
(bis zu einer Bogensekunde bei den Langsamen) und kann Transit-Chiron gar nicht
rechnen; seit dem 2026-09-06 bricht es in dem Fall ab. `lade()` warnt darum beim
Laden von `transit`, wenn keine `seas_*.se1` erreichbar ist.
"""

import glob
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
    "1":        ("radix", "build"),
    "2":        ("selektor",),
    "3+4":      ("build", "chartdoc", "radix"),
    "transit":  ("transit", "transitdata", "transituhr_fusion"),
    "restyle":  ("build", "chartdoc", "radix", "restyle"),
    "hdgk":     ("hd",),
    "bibliothek": ("markiere", "selektor"),
}

# Was ein Schritt bedeutet — nur fuer die Ausgabe von uebersicht().
_SCHRITT_TEXT = {
    "1":        "Datenblatt (Heimat-Probe braucht build)",
    "2":        "Referenzschnitt fuer die Analyse",
    "3+4":      "Design, HTML, Rendern, Pruefen",
    "transit":  "zusaetzlich bei Transit- und Ultimativ-Lauf",
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

    Wirft, wenn die Dateien auch nach der Installation nicht auffindbar sind.
    Nicht abfangen: Ohne sie rechnet der Builder auf Moshier (bis zu einer
    Bogensekunde bei den Langsamen, ein Exaktpunkt nahe Mitternacht kann auf den
    Nachbartag kippen) und Transit-Chiron gar nicht — seit dem 2026-09-06 ein
    harter Fehler. Bewusst ohne Chiron rechnet man mit `--ohne-chiron`.
    """
    pfad = ephemeriden_pfad()
    if pfad:
        if not still:
            print("Ephemeriden schon da:", pfad)
        return pfad

    for paket, extra in PAKETE:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", paket, *extra,
             "--break-system-packages", "-q"],
            check=False,
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
    """
    if ephemeriden_pfad():
        return
    print(
        "\n[WARNUNG] transit geladen, aber keine Swiss-Ephemeris-Dateien "
        "gefunden (seas_*.se1).\n"
        "  Solange nur der fertige Report aus der chart_data geparst wird, ist "
        "das folgenlos.\n"
        "  Sobald transit.py RECHNET, fehlt Transit-Chiron und die "
        "Hauptplaneten laufen auf Moshier. Dann:\n"
        "      from lade import ephemeriden\n"
        "      ephe = ephemeriden()      # installiert und liefert den Pfad\n"
        "  Notfalls diesen Pfad an --ephe uebergeben.\n",
        file=sys.stderr,
    )


def lade(*module, ziel="/home/claude", frisch=False, still=False):
    """Builder aus dem Repo auf die Disk holen und `ziel` in den sys.path legen.

    module  Modulnamen ohne oder mit .py — `lade("build", "chartdoc")`
    ziel    Zielverzeichnis, Vorgabe /home/claude (dort erwarten die Builder
            einander; build.BASE_DIR und die sys.path-Zeilen in chartdoc.py und
            den Uhr-Modulen sind fest darauf eingestellt)
    frisch  True umgeht den ~5-Minuten-Cache von raw.githubusercontent.com —
            direkt nach einem Upload benutzen, sonst kommt die alte Fassung
    still   True unterdrueckt die Erfolgsmeldung

    Prueft jede Datei nach dem Download auf Nullgroesse und laesst sie von
    py_compile uebersetzen. Damit faellt eine Fehlerseite, die der Proxy statt
    der Datei ausliefert, sofort auf — und nicht erst als raetselhafter
    SyntaxError mitten im Render.

    Wirft bei jedem Fehlschlag. NICHT abfangen und stillschweigend auf eine
    Altfassung ausweichen: in dem Fall auf project_read zurueckfallen UND melden,
    dass der Ladeweg klemmt.
    """
    pfad_ziel = pathlib.Path(ziel)
    pfad_ziel.mkdir(parents=True, exist_ok=True)

    geholt = []
    for m in module:
        name = m if m.endswith(".py") else m + ".py"
        stamm = name[:-3]
        if stamm not in BEKANNT:
            raise ValueError(
                f"{name} ist nicht im Repo. Verfuegbar: "
                + ", ".join(sorted(BEKANNT - {'lade'}))
            )
        pfad = pfad_ziel / name
        url = REPO + name + ("?frisch=1" if frisch else "")
        try:
            urllib.request.urlretrieve(url, pfad)
        except Exception as e:
            raise RuntimeError(
                f"{name} liess sich nicht laden ({type(e).__name__}: {e}). "
                "Ladeweg klemmt — auf project_read zurueckfallen und melden."
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
        geholt.append(f"{name} ({pfad.stat().st_size} B)")

    if ziel not in sys.path:
        sys.path.insert(0, ziel)

    if not still:
        print("geladen:", ", ".join(geholt))
    if any((m[:-3] if m.endswith(".py") else m) == "transit" for m in module):
        _ephemeriden_warnung()
    return [g.split(" ")[0] for g in geholt]


def lade_schritt(schritt, **kw):
    """Holt genau die Builder, die dieser Schritt braucht — s. SCHRITTE.

        lade_schritt("1")        # Datenblatt
        lade_schritt("3+4")      # Design/Render
        lade_schritt("transit")  # zusaetzlich beim Transit-/Ultimativ-Lauf

    Nimmt dieselben Zusatzargumente wie lade() (ziel, frisch, still).
    Vorzuziehen gegenueber lade("a", "b", ...) von Hand: die Liste steht dann
    an genau einer Stelle und kann nicht chatweise abweichen.
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
            print(f"Repo-Probe: alle {len(da)} Builder aus BEKANNT sind da.")
    return fehlend, []


def uebersicht():
    """Druckt, welcher Schritt was zieht und woher — die Antwort auf
    'von wo wird was geholt'. Die Anweisungsmodule verweisen hierher,
    statt eigene Listen zu fuehren."""
    print("Ladeweg — Quelle ist immer das Repo:")
    print(" ", REPO)
    print("\nJe Schritt:")
    for s, mods in SCHRITTE.items():
        print("  lade_schritt(%-12s -> %-42s # %s"
              % (repr(s) + ")", ", ".join(mods), _SCHRITT_TEXT.get(s, "")))
    print("\nAlle bekannten Builder (%d):" % len(BEKANNT - {"lade"}))
    print("  " + ", ".join(sorted(BEKANNT - {"lade"})))
    print("\nEphemeriden (nur wer rechnet — Pholus, transit.py):")
    print("  ephe = ephemeriden()   installiert %s und liefert den Pfad"
          % " + ".join(p for p, _ in PAKETE))
    print("\nNicht ueber diesen Weg, weiter per project_read:")
    print("  blocks_bundle.txt (die Bibliothek selbst) und alle .md-Module.")


if __name__ == "__main__":
    # Selbsttest: holt alle Builder und meldet, ob jeder ankommt.
    alle = sorted(BEKANNT - {"lade"})
    lade(*alle, ziel="/tmp/ladeselbsttest")
    print(f"\n[Selbsttest bestanden: {len(alle)} Builder geladen und uebersetzbar]")
    print()
    uebersicht()
