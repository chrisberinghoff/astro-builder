#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hd.py — deterministische Human-Design-/Gene-Keys-Rechenpipeline.

Schwester zu build.py: alles, was bei jedem Chart IDENTISCH ist (Torrad,
Zentren, Kanäle, Typ-/Autoritäts-/Profil-Logik, Gene-Keys-Sphären), liegt hier
als verifizierter Code — statt es in jeder Themen-Horoskop-Konversation neu
abzuleiten und zu prüfen. Variabel bleibt nur das Geburtsdatum (rein) und die
Deutung (Web/Synthese, kommt von außen — NICHT aus diesem Skript).

Verifikationsstand (anonymer Prüffall, Geburtsdaten bewusst nicht im Code):
  - Personality-Längen ≤ 1' gegen ein astroschmid-PDF.
  - Torrad-Anker per zwei unabhängigen Quellen bestätigt.
  - Inkarnationskreuz doc-genau bestätigt.
  - Alle Gene-Keys-Sphären-Tore einzeln gegengerechnet.
  Anonymisiert 2026-09-08 vor der Aufnahme ins Repo: der Datenschutz-
  Guardrail des Kerns verbietet Namen, Geburtsdaten und daraus abgeleitete
  Ergebnisse in jeder Datei, die öffentlich wird — auch im Docstring.

Verwendung:
    import sys; sys.path.insert(0, "/home/claude")
    import hd
    p = hd.compute(2000, 1, 1, 12.0)   # Geburtszeit in UT (Std. als float)
    hd.print_report(p)                          # lesbarer Report
    # p ist ein dict mit allen Werten für hd_gk_data.md

WICHTIG: Zeit als UT übergeben (Zonenzeit minus Zeitzonenoffset; Sommerzeit
beachten). Ort ist für Tore irrelevant (Tore = ekliptikale Länge), nur für
Häuser/AC — die kommen aus dem astrologischen Datenblatt, nicht hierher.
Braucht pyswisseph:  pip install pyswisseph --break-system-packages
"""

import sys

try:
    import swisseph as swe
except ImportError:
    swe = None

# ---------------------------------------------------------------------------
# Verifizierte Konstanten — NICHT ändern ohne erneute Gegenprobe
# ---------------------------------------------------------------------------

# HD-Rave-Mandala: Sequenz beginnt bei Tor 41 @ 302.0000° (2°00' Wassermann),
# je Tor 5.625°, je Linie 0.9375°. Verifiziert gegen zwei unabhängige Quellen.
WHEEL = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 27, 24,
         2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56, 31, 33, 7, 4, 29,
         59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50, 28, 44, 1, 43, 14, 34, 9, 5,
         26, 11, 10, 58, 38, 54, 61, 60]
WHEEL_START = 302.0
GATE_W = 5.625
LINE_W = GATE_W / 6.0     # 0.9375

# 9 Zentren -> ihre Tore (Summe 64)
CENTERS = {
    "Kopf":        [64, 61, 63],
    "Ajna":        [47, 24, 4, 17, 43, 11],
    "Kehle":       [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16],
    "G/Selbst":    [7, 1, 13, 25, 46, 2, 15, 10],
    "Herz/Ego":    [21, 40, 26, 51],
    "Sakral":      [34, 5, 14, 29, 59, 9, 3, 42, 27],
    "Solarplexus": [6, 37, 30, 55, 49, 22, 36],
    "Milz":        [48, 57, 44, 50, 32, 28, 18],
    "Wurzel":      [58, 38, 54, 53, 60, 52, 19, 39, 41],
}
GATE2CENTER = {g: c for c, gs in CENTERS.items() for g in gs}

# 36 Kanäle (Torpaare)
CHANNELS = [(1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31),
            (9, 52), (10, 20), (10, 34), (10, 57), (11, 56), (12, 22), (13, 33),
            (16, 48), (17, 62), (18, 58), (19, 49), (20, 34), (20, 57), (21, 45),
            (23, 43), (24, 61), (25, 51), (26, 44), (27, 50), (28, 38), (29, 46),
            (30, 41), (32, 54), (34, 57), (35, 36), (37, 40), (39, 55), (42, 53),
            (47, 64)]

MOTORS = {"Herz/Ego", "Solarplexus", "Wurzel", "Sakral"}

# Gene-Keys-Sphären -> Aktivierung (offiziell, genekeys.com)
# ('P'=Personality/Geburt, 'D'=Design/vorgeburtlich)
GK_SPHERES = {
    # Aktivierungssequenz
    "Life's Work": ("P", "Sonne"),  "Evolution": ("P", "Erde"),
    "Radiance":    ("D", "Sonne"),  "Purpose":   ("D", "Erde"),
    # Venus-Sequenz (Beziehungen)
    "Attraction":  ("D", "Mond"),   "IQ":  ("P", "Venus"),
    "EQ":          ("P", "Mars"),   "SQ":  ("D", "Venus"),
    "Core/Vocation": ("D", "Mars"),
    # Pearl-Sequenz
    "Culture":     ("D", "Jupiter"), "Pearl": ("P", "Jupiter"),
    # optional/Star Pearl
    "Creativity":  ("D", "Uranus"),
}

_ANGLE_RA = {"1/3", "1/4", "2/4", "2/5", "3/5", "3/6", "4/6"}

# ---------------------------------------------------------------------------
# Kern
# ---------------------------------------------------------------------------

def gate_line(lon):
    """Ekliptikale Länge (Grad) -> (Tor, Linie)."""
    off = (lon - WHEEL_START) % 360.0
    idx = int(off // GATE_W)
    gate = WHEEL[idx]
    line = int((off - idx * GATE_W) // LINE_W) + 1
    return gate, min(line, 6)


def _flag():
    return swe.FLG_SWIEPH | swe.FLG_MOSEPH   # Moshier-Fallback, keine Datendateien


def _lon(jd, planet):
    xx, _ = swe.calc_ut(jd, planet, _flag())
    return xx[0] % 360.0


_BODIES = [("Sonne", "SUN"), ("Mond", "MOON"), ("Merkur", "MERCURY"),
           ("Venus", "VENUS"), ("Mars", "MARS"), ("Jupiter", "JUPITER"),
           ("Saturn", "SATURN"), ("Uranus", "URANUS"), ("Neptun", "NEPTUNE"),
           ("Pluto", "PLUTO")]


def _positions(jd):
    """Liefert dict {Faktor: Länge} inkl. Erde, Nord-/Südknoten."""
    d = {}
    for name, attr in _BODIES:
        d[name] = _lon(jd, getattr(swe, attr))
    node = _lon(jd, swe.TRUE_NODE)
    d["Knoten"] = node
    d["Südknoten"] = (node + 180) % 360
    d["Erde"] = (d["Sonne"] + 180) % 360
    return d


def _design_jd(jd_birth):
    """JD, an dem die Sonne exakt 88°00' Bogen VOR der Geburtssonne stand."""
    sun_b = _lon(jd_birth, swe.SUN)
    target = (sun_b - 88.0) % 360.0

    def diff(jd):
        return (_lon(jd, swe.SUN) - target + 180) % 360 - 180

    # Bracket im Fenster ~80-100 Tage vor Geburt suchen, dann Bisektion
    a = b = None
    prev = None
    jd = jd_birth - 95
    while jd < jd_birth - 80:
        dv = diff(jd)
        if prev is not None and prev[1] * dv < 0:
            a, b = prev[0], jd
            break
        prev = (jd, dv)
        jd += 0.5
    if a is None:               # Fallback: linear von -88 Tagen
        return jd_birth - 88.0
    for _ in range(60):
        m = (a + b) / 2
        if diff(a) * diff(m) <= 0:
            b = m
        else:
            a = m
    return (a + b) / 2


def compute(year, month, day, hour_ut):
    """Vollständiges HD/GK-Profil. hour_ut = Stunde in UT als float."""
    if swe is None:
        raise RuntimeError("pyswisseph fehlt: pip install pyswisseph --break-system-packages")
    swe.set_ephe_path(None)
    jd_b = swe.julday(year, month, day, hour_ut, swe.GREG_CAL)
    jd_d = _design_jd(jd_b)

    pers_lon = _positions(jd_b)
    des_lon = _positions(jd_d)
    pers = {k: (v, *gate_line(v)) for k, v in pers_lon.items()}
    des = {k: (v, *gate_line(v)) for k, v in des_lon.items()}

    # aktivierte Tore
    activated = set()
    for r in (pers, des):
        for (_, g, _l) in r.values():
            activated.add(g)

    # aktive Kanäle + definierte Zentren
    active_ch = [(a, b) for a, b in CHANNELS if a in activated and b in activated]
    defined = set()
    for a, b in active_ch:
        defined.add(GATE2CENTER[a]); defined.add(GATE2CENTER[b])

    # Adjazenz der definierten Zentren
    import collections
    adj = collections.defaultdict(set)
    for a, b in active_ch:
        adj[GATE2CENTER[a]].add(GATE2CENTER[b])
        adj[GATE2CENTER[b]].add(GATE2CENTER[a])

    def reaches(src, targets):
        seen, dq = {src}, collections.deque([src])
        while dq:
            x = dq.popleft()
            for y in adj[x]:
                if y in targets:
                    return True
                if y not in seen:
                    seen.add(y); dq.append(y)
        return False

    sacral = "Sakral" in defined
    throat = "Kehle" in defined
    throat_to_motor = throat and reaches("Kehle", MOTORS)

    if not defined:
        typ = "Reflektor"
    elif sacral:
        typ = "Manifestierender Generator" if throat_to_motor else "Generator"
    elif throat and reaches("Kehle", MOTORS - {"Sakral"}):
        typ = "Manifestor"
    else:
        typ = "Projektor"

    if "Solarplexus" in defined:
        auth = "Emotional (Solarplexus)"
    elif "Sakral" in defined:
        auth = "Sakral"
    elif "Milz" in defined:
        auth = "Splenisch"
    elif "Herz/Ego" in defined:
        auth = "Ego"
    elif "G/Selbst" in defined:
        auth = "Selbst-projiziert (G)"
    elif defined:
        auth = "Mental/Umgebung (kein innerer Ansage)"
    else:
        auth = "Lunar (Reflektor)"

    p_line = pers["Sonne"][2]; d_line = des["Sonne"][2]
    profil = f"{p_line}/{d_line}"
    angle = ("Right Angle" if profil in _ANGLE_RA
             else "Juxtaposition" if profil == "4/1" else "Left Angle")

    # Definition (Zusammenhangskomponenten)
    comp, seen = 0, set()
    for c in defined:
        if c not in seen:
            comp += 1; dq = collections.deque([c]); seen.add(c)
            while dq:
                x = dq.popleft()
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y); dq.append(y)
    definition = {0: "keine", 1: "Einfach", 2: "Split", 3: "Dreifach-Split",
                  4: "Vierfach-Split"}.get(comp, f"{comp} Gruppen")

    # Split-Brücken-Tore: Tore, die (allein) zwei getrennte Gruppen verbinden
    bridges = []
    if comp >= 2:
        # Gruppen-Id je Zentrum
        gid, seen2, cid = {}, set(), 0
        for c in defined:
            if c not in seen2:
                cid += 1; dq = collections.deque([c]); seen2.add(c); gid[c] = cid
                while dq:
                    x = dq.popleft()
                    for y in adj[x]:
                        if y not in seen2:
                            seen2.add(y); gid[y] = cid; dq.append(y)
        for a, b in CHANNELS:
            ca, cb = GATE2CENTER[a], GATE2CENTER[b]
            if ca in defined and cb in defined and gid.get(ca) != gid.get(cb):
                if (a in activated) ^ (b in activated):
                    bridges.append(a if a not in activated else b)
        bridges = sorted(set(bridges))

    cross = [pers["Sonne"][1], pers["Erde"][1], des["Sonne"][1], des["Erde"][1]]

    # Gene-Keys-Sphären
    gk = {}
    for sphere, (side, factor) in GK_SPHERES.items():
        r = pers if side == "P" else des
        _, g, l = r[factor]
        gk[sphere] = (g, l)

    return {
        "jd_birth": jd_b, "jd_design": jd_d,
        "pers": pers, "des": des,
        "typ": typ, "authority": auth, "profil": profil,
        "definition": definition, "components": comp, "bridges": bridges,
        "defined_centers": sorted(defined),
        "open_centers": sorted(set(CENTERS) - defined),
        "channels": active_ch, "cross_gates": cross, "cross_angle": angle,
        "gene_keys": gk,
    }


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------

_STRAT = {"Generator": "Reagieren (warten, dann sakral antworten)",
          "Manifestierender Generator": "Reagieren, dann informieren",
          "Manifestor": "Informieren vor dem Handeln",
          "Projektor": "Auf Einladung/Anerkennung warten",
          "Reflektor": "Einen Mondzyklus (~28 Tage) abwarten"}
_SEQ = ["Sonne", "Erde", "Mond", "Knoten", "Südknoten", "Merkur", "Venus",
        "Mars", "Jupiter", "Saturn", "Uranus", "Neptun", "Pluto"]


def print_report(p):
    print(f"Design-JD {p['jd_design']:.5f} (Sonne −88°)")
    print(f"{'Faktor':11s} {'Personality':>14s}   {'Design':>10s}")
    for k in _SEQ:
        pg = f"{p['pers'][k][1]}.{p['pers'][k][2]}"
        dg = f"{p['des'][k][1]}.{p['des'][k][2]}"
        print(f"  {k:9s} {pg:>12s}   {dg:>10s}")
    print(f"\nTyp: {p['typ']}   Strategie: {_STRAT[p['typ']]}")
    print(f"Autorität: {p['authority']}   Profil: {p['profil']}")
    print(f"Definition: {p['definition']}"
          + (f"   Brücken-Tore: {p['bridges']}" if p['bridges'] else ""))
    print(f"Definiert: {', '.join(p['defined_centers'])}")
    print(f"Offen: {', '.join(p['open_centers'])}")
    print(f"Kanäle: {', '.join(f'{a}-{b}' for a, b in p['channels'])}")
    c = p['cross_gates']
    print(f"Inkarnationskreuz ({p['cross_angle']}): {c[0]}/{c[1]} | {c[2]}/{c[3]}")
    print("Gene Keys:")
    for s in ["Life's Work", "Evolution", "Radiance", "Purpose", "Attraction",
              "IQ", "EQ", "SQ", "Core/Vocation", "Culture", "Pearl"]:
        g, l = p['gene_keys'][s]
        print(f"  {s:14s} {g}.{l}")


if __name__ == "__main__":
    # Selbsttest gegen einen SYNTHETISCHEN Fall: 01.01.2000, 12:00 UT.
    # Bewusst konstruiert, kein realer Prüffall. Bis zum 2026-09-08 standen
    # hier die echten Geburtsdaten einer Klientin samt abgeleitetem Profil —
    # genau der Fall, den der Datenschutz-Guardrail des Kerns ausdrücklich
    # auch für den __main__-Selbsttest verbietet.
    p = compute(2000, 1, 1, 12.0)
    print_report(p)
    assert p["typ"] == "Manifestierender Generator"
    assert p["authority"].startswith("Emotional")
    assert p["profil"] == "1/4"
    assert p["cross_gates"] == [38, 39, 48, 21]
    assert p["definition"] == "Split"
    print("\n[Selbsttest bestanden: Manifestierender Generator / Emotional / 1/4 / Split]")
