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
    import sys; sys.path.insert(0, "/home/claude"); from lade import lade

Dann nach Schritt:

    lade("radix")                              # Schritt 1, Datenblatt
    lade("selektor")                           # Schritt 2, Referenzschnitt
    lade("build", "chartdoc", "radix")         # Schritt 3+4, Design/Render
    lade("transit", "transitdata", "transituhr_fusion")   # Transit / Ultimativ

Im Repo verfuegbar: build, chartdoc, radix, transit, transitdata,
transituhr_fusion, transituhr (abgeloeste Zeilenfassung), selektor, markiere.
NICHT im Repo und weiter per project_read: hd.py (enthaelt Klientendaten),
REFERENZ_Chart_Builder_Ultimativ.py, blocks_bundle.txt.

transit.py braucht zusaetzlich pyswisseph:
    pip install pyswisseph --break-system-packages
"""

import urllib.request
import pathlib
import py_compile
import sys

REPO = "https://raw.githubusercontent.com/chrisberinghoff/astro-builder/main/"

BEKANNT = {
    "build", "chartdoc", "radix", "transit", "transitdata",
    "transituhr_fusion", "transituhr", "selektor", "markiere", "lade",
}


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
    return [g.split(" ")[0] for g in geholt]


if __name__ == "__main__":
    # Selbsttest: holt alle Builder und meldet, ob jeder ankommt.
    alle = sorted(BEKANNT - {"lade"})
    lade(*alle, ziel="/tmp/ladeselbsttest")
    print(f"\n[Selbsttest bestanden: {len(alle)} Builder geladen und uebersetzbar]")
