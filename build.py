#!/usr/bin/env python3
"""
build.py — deterministische Render-Pipeline für die Horoskop-PDF-Produktion.

Zweck: alles, was bei jedem Chart IDENTISCH ist (Font-Setup, Fontconfig,
Emoji-Fallback-Fix, WeasyPrint-Aufruf, visuelle Prüfung) liegt hier als Code
statt jedes Mal neu in der Konversation geschrieben/debuggt zu werden.
Variabel bleibt pro Chart nur: das Designkonzept (Farben/Motive/Cover) und
der Analysetext aus analyse.md — beides kommt von außen, nicht aus diesem
Skript.

Verwendung als CLI (einmal pro neuer Session, idempotent):
    python3 build.py setup

Verwendung als Modul:
    import sys; sys.path.insert(0, "/home/claude")
    from build import setup_fonts, apply_fe0e, render, verify, BASE_CSS

    setup_fonts()                          # einmal pro Session
    render("chart.html", "ausgabe.pdf")    # Preflight + FE0E-Fix automatisch
    verify("ausgabe.pdf", expected_pages=24,
           markers=[...], aspect_rows=32)  # deterministisch via pdftotext/pdfinfo
    # verify_visual("ausgabe.pdf", pages=[1])  # Bildschau nur als Stichprobe

HÄRTUNGSSCHICHT (Fehler früh und sprechend statt kaputtes PDF):
    parse_analyse("x_analyse.md")          # festes Schema, s. ANALYSE_SCHEMA
    assert_render_ready(html)              # WeasyPrint-Fallen als Assertions
    render()/render_sentence_safe()        # fangen WeasyPrint-WARNINGs ab
    verify()                               # prüft Text/Seiten/Aspekte, 1 Bild

WICHTIG ZUM DATEISYSTEM: /home/claude wird zwischen Konversationen
zurückgesetzt. setup_fonts() muss deshalb in JEDER neuen Session einmal
laufen (dauert ca. 5-10 Sekunden, lädt Cinzel/EB Garamond von GitHub).
Dieses Skript selbst muss daher als Datei im Projektwissen liegen, nicht
nur im Container — sonst muss es ebenfalls jedes Mal neu geschrieben werden.
"""

import html as _html
import logging
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
from contextlib import contextmanager

# ---------------------------------------------------------------------------
# Fehlerklassen — jede Stufe bricht HART und SPRECHEND ab, statt still ein
# fehlerhaftes PDF zu erzeugen.
# ---------------------------------------------------------------------------

class BuildError(Exception):
    """Basisklasse aller Pipeline-Fehler."""


class SchemaError(BuildError):
    """analyse.md weicht vom dokumentierten Struktur-Schema ab (ANALYSE_SCHEMA)."""


class RenderReadyError(BuildError):
    """Vorab-Assertions verletzt (WeasyPrint-Fallen) — HTML nicht renderfähig."""


class RenderWarningError(BuildError):
    """WeasyPrint hat beim Rendern Warnungen gemeldet (fehlende Fonts/Assets,
    ungültiges CSS, unbekannte font-family) — das PDF wäre still fehlerhaft."""


class VerifyError(BuildError):
    """Deterministische PDF-Endprüfung fehlgeschlagen."""


class DeckblattError(BuildError):
    """@@DECKBLATT-Block fehlt oder ist unvollständig (s. lies_deckblatt)."""


# ---------------------------------------------------------------------------
# WeasyPrint-Warnlog-Abfang. WeasyPrint stürzt bei fehlenden Fonts/Bildern
# oder ungültigem CSS NICHT ab — es loggt eine WARNING und rendert still ein
# kaputtes PDF. Diese Warnungen werden hier zu harten Fehlern.
# ---------------------------------------------------------------------------

_WEASY_LOGGER_NAMES = ("weasyprint", "weasyprint.progress")


class _ListHandler(logging.Handler):
    def __init__(self):
        super().__init__(level=logging.WARNING)
        self.records = []

    def emit(self, record):
        self.records.append(record)


@contextmanager
def _weasy_log_capture():
    handler = _ListHandler()
    loggers = [logging.getLogger(n) for n in _WEASY_LOGGER_NAMES]
    saved = []
    for lg in loggers:
        saved.append((lg, lg.level))
        if lg.level > logging.WARNING:
            lg.setLevel(logging.WARNING)     # WARNINGs müssen durchkommen
        lg.addHandler(handler)
    try:
        yield handler
    finally:
        for lg, lvl in saved:
            lg.removeHandler(handler)
            lg.setLevel(lvl)


def _raise_on_weasy_warnings(handler, ignore_warnings=(), context=""):
    msgs = []
    for rec in handler.records:
        m = rec.getMessage()
        if any(re.search(pat, m) for pat in ignore_warnings):
            continue
        msgs.append(f"  [{rec.levelname}] {m}")
    if msgs:
        uniq = sorted(set(msgs))
        where = f" ({context})" if context else ""
        raise RenderWarningError(
            f"WeasyPrint meldete beim Rendern{where} {len(uniq)} Problem(e) — "
            "das PDF wäre still fehlerhaft:\n" + "\n".join(uniq) +
            "\nTypische Ursachen: fehlende Font-/Bilddatei, ungültiger CSS-Wert, "
            "unbekannte font-family. Ursache beheben; nur nachweislich harmlose "
            "Meldungen per ignore_warnings=[regex, ...] freigeben.")


# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------

BASE_DIR = "/home/claude"
FONTS_DIR = os.path.join(BASE_DIR, ".fonts")
FONTS_LINK = os.path.join(BASE_DIR, "fonts")          # nicht-versteckter Alias für relative HTML-Pfade
FONTS_SRC_DIR = os.path.join(BASE_DIR, "fonts_src")   # Rohdaten (Variable Fonts) vor der Instanzierung
FCCONF_DIR = os.path.join(BASE_DIR, "fcconf")
FCCONF_PATH = os.path.join(FCCONF_DIR, "fonts.conf")
FC_CACHE_DIR = os.path.join(BASE_DIR, ".fontconfig-cache")

GOOGLE_FONTS_RAW = "https://raw.githubusercontent.com/google/fonts/main/ofl"

# (Quelldatei-URL-Suffix, lokaler Variable-Font-Name, [(Gewicht, Ausgabedatei, Familienname, italic)])
FONT_JOBS = [
    (
        f"{GOOGLE_FONTS_RAW}/cinzel/Cinzel%5Bwght%5D.ttf",
        "Cinzel-VF.ttf",
        [
            (400, "Cinzel-Regular.ttf", "Cinzel", False),
            (700, "Cinzel-Bold.ttf", "Cinzel Bold", False),
            (900, "Cinzel-Black.ttf", "Cinzel Black", False),
        ],
    ),
    (
        f"{GOOGLE_FONTS_RAW}/ebgaramond/EBGaramond%5Bwght%5D.ttf",
        "EBGaramond-VF.ttf",
        [
            (400, "EBGaramond-Regular.ttf", "EB Garamond", False),
            (700, "EBGaramond-Bold.ttf", "EB Garamond Bold", False),
        ],
    ),
    (
        f"{GOOGLE_FONTS_RAW}/ebgaramond/EBGaramond-Italic%5Bwght%5D.ttf",
        "EBGaramond-Italic-VF.ttf",
        [
            (400, "EBGaramond-Italic.ttf", "EB Garamond Italic", True),
            (700, "EBGaramond-BoldItalic.ttf", "EB Garamond Bold Italic", True),
        ],
    ),
]

# Erwartete Enddateien — wenn die alle existieren, gilt Setup als erledigt.
EXPECTED_FONT_FILES = [
    spec[1] for _, _, specs in FONT_JOBS for spec in specs
]

FONTCONFIG_XML = """<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>/usr/share/fonts</dir>
  <dir>/usr/local/share/fonts</dir>
  <dir prefix="xdg">fonts</dir>
  <dir>{fonts_dir}</dir>

  <match target="pattern">
    <test qual="any" name="family"><string>mono</string></test>
    <edit name="family" mode="assign" binding="same"><string>monospace</string></edit>
  </match>
  <match target="pattern">
    <test qual="any" name="family"><string>sans serif</string></test>
    <edit name="family" mode="assign" binding="same"><string>sans-serif</string></edit>
  </match>
  <match target="pattern">
    <test qual="any" name="family"><string>sans</string></test>
    <edit name="family" mode="assign" binding="same"><string>sans-serif</string></edit>
  </match>
  <match target="pattern">
    <test qual="any" name="family"><string>system ui</string></test>
    <edit name="family" mode="assign" binding="same"><string>system-ui</string></edit>
  </match>

  <selectfont>
    <rejectfont><glob>*.dpkg-tmp</glob></rejectfont>
  </selectfont>
  <selectfont>
    <rejectfont><glob>*.dpkg-new</glob></rejectfont>
  </selectfont>

  <!-- KERNSTÜCK: Noto Color Emoji ausschliessen, sonst werden astrologische
       Symbole als Farb-Emoji statt als Text-Glyphen gerendert. -->
  <selectfont>
    <rejectfont><glob>*NotoColorEmoji*</glob></rejectfont>
  </selectfont>

  <include ignore_missing="yes">/etc/fonts/conf.d</include>

  <cachedir>/var/cache/fontconfig</cachedir>
  <cachedir prefix="xdg">fontconfig</cachedir>
  <cachedir>{cache_dir}</cachedir>

  <config>
    <rescan><int>30</int></rescan>
  </config>
</fontconfig>
"""

# ---------------------------------------------------------------------------
# Glyph-Sicherheit
# ---------------------------------------------------------------------------

# Tierkreis-Glyphen (Widder..Fische) brauchen den Text-Presentation-Selektor,
# sonst rendern manche Engines sie als Farb-Emoji. Planeten-/Asteroiden-
# Glyphen (☉☽☿♀♂♃♄♅♆♇☊⚸⚷) brauchen ihn NICHT und werden hier bewusst
# nicht angefasst.
_ZODIAC_RANGE = re.compile(r"([♈-♓])(?!︎)")


def apply_fe0e(text: str) -> str:
    """Hängt U+FE0E an alle Tierkreis-Glyphen an, die es noch nicht haben."""
    return _ZODIAC_RANGE.sub(lambda m: m.group(1) + "︎", text)


# CSS-Baustein, der in jedes Chart-HTML eingebunden werden sollte. Enthält:
# - @font-face für alle 7 Schriftschnitte (relative Pfade ab /home/claude)
# - Glyph-sichere Font-Stacks (.glyph) gegen stillen Fallback auf
#   Georgia/Helvetica-Stacks
# - Quellenfarbcodierung als optionale Klassen (nur nutzen wenn explizit
#   gewünscht)
# - .page.dense als Hook für Zeilenhöhen-Reduktion bei verwaisten Zeilen
#   (Margin-Reduktion wirkt wegen Margin-Collapsing nicht zuverlässig)
BASE_CSS = """
@font-face { font-family: "Cinzel";                 src: url("fonts/Cinzel-Regular.ttf");        font-weight: 400; }
@font-face { font-family: "Cinzel Bold";             src: url("fonts/Cinzel-Bold.ttf");            font-weight: 700; }
@font-face { font-family: "Cinzel Black";            src: url("fonts/Cinzel-Black.ttf");           font-weight: 900; }
@font-face { font-family: "EB Garamond";             src: url("fonts/EBGaramond-Regular.ttf");     font-weight: 400; }
@font-face { font-family: "EB Garamond Bold";        src: url("fonts/EBGaramond-Bold.ttf");        font-weight: 700; }
@font-face { font-family: "EB Garamond Italic";      src: url("fonts/EBGaramond-Italic.ttf");      font-style: italic; }
@font-face { font-family: "EB Garamond Bold Italic"; src: url("fonts/EBGaramond-BoldItalic.ttf");  font-style: italic; font-weight: 700; }

/* Glyph-sicherer Stack fuer JEDES Element, das astrologische Unicode-Zeichen
   enthaelt. Ohne explizite font-family fallen diese Zeichen sonst still auf
   die Georgia/Helvetica-Stacks zurueck und werden als Leerzeichen/Box
   gerendert. */
.glyph, .planet-glyph, .zodiac-glyph {
  font-family: "DejaVu Sans", "FreeSerif", sans-serif;
}

/* Quellenfarbcodierung - nur einsetzen, wenn explizit gewuenscht */
.src-buch      { color: #1a3a5c; }
.src-web       { color: #6b4226; }
.src-synthese  { color: #4a4a4a; font-style: italic; }

/* Hook gegen verwaiste Zeilen in dichten Textbloecken. Margin-Reduktion auf
   einzelnen Bloecken wirkt wegen Margin-Collapsing nicht zuverlaessig -
   stattdessen line-height auf der ganzen Seite reduzieren. */
.page.dense { line-height: 1.32; }

/* WeasyPrint kennt margin-top:auto in Flex-Spalten nicht. Cover-Elemente
   IMMER mit position:absolute + top/bottom positionieren, nicht mit Flex
   zentrieren. */
.cover { position: relative; }
.cover-anchor-top    { position: absolute; top: 0; }
.cover-anchor-bottom { position: absolute; bottom: 0; }

/* ===================================================================
   KAPITEL-UMBRUCH: Smart-Break
   Kapitel fliessen fortlaufend statt jedes auf einer neuen Seite zu
   beginnen (das liess bei variabler Kapitellaenge halbe Seiten leer).
   Kopf (Kicker+Titel+Ornament) + ganzer erster Absatz bleiben als
   Einheit zusammen und rutschen bei Platzmangel geschlossen auf die
   naechste Seite - nie ein verwaister Kopf, nie ein Loch.
   VORAUSSETZUNG an das Chart-HTML (Konvention):
     <section class="chapter">
       <div class="chapter-head"> Kicker + <h2> + Ornament </div>
       <p class="first"> erster Absatz (ggf. mit Drop-Cap) </p>
       <p> weitere Absaetze ... </p>
     </section>
   =================================================================== */
.chapter                { break-before: auto; margin-top: 2.3cm; }
/* Erstes Kapitel ohne oberen Abstand. ACHTUNG: :first-of-type zaehlt den
   Section-TYP, nicht die Klasse — sobald VOR den Kapiteln Frontmatter-Sections
   stehen (Cover, Radseite), ist die erste <section> das Cover, und diese Regel
   greift NICHT mehr aufs erste Kapitel. Dann dem ersten Kapitel zusaetzlich
   class="chapter-first" geben (wirkt ueber die zweite Regel); soll es auf einer
   eigenen Seite starten, break-before:page an .chapter-first im chart-eigenen
   DESIGN_CSS ergaenzen. Rein additiv: chapters-only-Charts bleiben unveraendert. */
.chapter:first-of-type,
.chapter.chapter-first  { margin-top: 0; }
.chapter-head           { break-inside: avoid; break-after: avoid; }
.chapter > p.first      { break-before: avoid; break-inside: avoid; }
.chapter > ol:first-of-type { break-before: avoid; }
p        { orphans: 2; widows: 2; }
p.first  { orphans: 3; widows: 3; }

/* SATZWEISER SEITENUMBRUCH: Der Satz-Schutz (render_sentence_safe) setzt
   die Klasse .sbrk vor den Absatzteil, der als Ganzes auf die naechste
   Seite gezogen wird - damit kein Satz (und kein Doppelpunkt-Absatz) ueber
   die Seitenkante reisst. Nur die Mechanik ist hier; die Umbruchpunkte
   werden pro Chart gemessen, nicht fest verdrahtet. */
.sbrk { break-before: page; margin-top: 0; }

/* HÄRTUNG (layoutneutral, verhindert kaputte Umbrueche, aendert nichts am
   Erscheinungsbild): Zwischentitel nie allein am Seitenfuss; Listenpunkte
   nie ueber die Seitenkante gerissen (Listen laufen nicht durch den
   Satz-Schutz von render_sentence_safe, darum hier per CSS gesichert). */
.subhead { break-after: avoid; break-inside: avoid; }
ol li, ul li { break-inside: avoid; }
"""


# ---------------------------------------------------------------------------
# Satz-Segmentierung (fuer den satzweisen Seitenumbruch)
# ---------------------------------------------------------------------------

# Abkuerzungen/Kuerzel, nach denen ein Punkt KEIN Satzende ist.
_ABBR = {"z", "B", "u", "a", "d", "h", "ca", "etc", "usw", "bzw", "ggf", "evtl",
         "inkl", "vgl", "sog", "Nr", "S", "Abs", "Art", "Dr", "Prof", "o", "ae",
         "ff", "f", "vs", "ebd", "Jh", "Jhd", "St", "Bd", "Kap"}
_SENT_END = re.compile(r'[.!?…]+["»”\'\)\]]*\s+')


def split_sentences(text: str) -> list:
    """Zerlegt einen Absatz in Saetze. Ein Punkt gilt NICHT als Satzende,
    wenn davor eine reine Zahl (Ordinalzahl wie '8.' oder '1./2.'), eine
    bekannte Abkuerzung oder ein einzelner Grossbuchstabe steht, oder wenn
    danach kein satzstartartiges Zeichen folgt. Gibt mindestens den ganzen
    Text als eine 'Satz'-Liste zurueck."""
    out, start = [], 0
    for m in _SENT_END.finditer(text):
        wm = re.search(r'(\S+)$', text[:m.start()])
        core = (wm.group(1) if wm else '').strip('.„"“»(')
        nxt = text[m.end():m.end() + 1]
        if (re.fullmatch(r'[0-9./]+', core) or core in _ABBR
                or re.fullmatch(r'[A-ZÄÖÜ]', core)
                or not (nxt and (nxt.isupper() or nxt.isdigit() or nxt in '„"“»('))):
            continue
        out.append(text[start:m.end()].rstrip())
        start = m.end()
    if start < len(text):
        out.append(text[start:].strip())
    return [s for s in out if s.strip()] or [text.strip()]


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def _already_set_up() -> bool:
    if not os.path.isfile(FCCONF_PATH):
        return False
    for fname in EXPECTED_FONT_FILES:
        if not os.path.isfile(os.path.join(FONTS_DIR, fname)):
            return False
    return True


def setup_fonts(force: bool = False) -> None:
    """Lädt Cinzel/EB Garamond, instanziert sie statisch, vergibt eigene
    Familiennamen, baut die Fontconfig und cacht alles. Idempotent: läuft
    nur, wenn nicht schon alles vorhanden ist (force=True erzwingt Neubau)."""
    if not force and _already_set_up():
        print("Fonts/Fontconfig bereits vorhanden, Setup übersprungen.")
        os.environ["FONTCONFIG_FILE"] = FCCONF_PATH
        return

    os.makedirs(FONTS_SRC_DIR, exist_ok=True)
    os.makedirs(FONTS_DIR, exist_ok=True)
    os.makedirs(FCCONF_DIR, exist_ok=True)
    os.makedirs(FC_CACHE_DIR, exist_ok=True)

    from fontTools.ttLib import TTFont
    from fontTools import varLib

    for url, vf_name, instances in FONT_JOBS:
        vf_path = os.path.join(FONTS_SRC_DIR, vf_name)
        if not os.path.isfile(vf_path):
            print(f"Lade {vf_name} ...")
            urllib.request.urlretrieve(url, vf_path)

        for weight, out_name, family, italic in instances:
            out_path = os.path.join(FONTS_DIR, out_name)
            subprocess.run(
                [
                    sys.executable, "-m", "fontTools.varLib.instancer",
                    "-q", "-o", out_path, vf_path, f"wght={weight}",
                ],
                check=True,
            )
            _rename_font(out_path, family, italic, weight)
            print(f"  -> {out_name}: family='{family}', weight={weight}, italic={italic}")

    if not os.path.islink(FONTS_LINK):
        if os.path.exists(FONTS_LINK):
            os.remove(FONTS_LINK)
        os.symlink(FONTS_DIR, FONTS_LINK)

    with open(FCCONF_PATH, "w") as f:
        f.write(FONTCONFIG_XML.format(fonts_dir=FONTS_DIR, cache_dir=FC_CACHE_DIR))

    os.environ["FONTCONFIG_FILE"] = FCCONF_PATH
    subprocess.run(["fc-cache", "-f", FONTS_DIR], check=True,
                    capture_output=True)
    print("Setup abgeschlossen.")


def _rename_font(path: str, family: str, italic: bool, weight: int) -> None:
    from fontTools.ttLib import TTFont
    tt = TTFont(path)
    name = tt["name"]
    subfamily = "Italic" if italic else "Regular"
    full = family if subfamily == "Regular" else f"{family} {subfamily}"
    ps = full.replace(" ", "")
    for plat_id, enc_id, lang_id in [(3, 1, 0x409), (1, 0, 0)]:
        name.setName(family, 1, plat_id, enc_id, lang_id)
        name.setName(subfamily, 2, plat_id, enc_id, lang_id)
        name.setName(full, 4, plat_id, enc_id, lang_id)
        name.setName(ps, 6, plat_id, enc_id, lang_id)
        name.setName(family, 16, plat_id, enc_id, lang_id)
        name.setName(subfamily, 17, plat_id, enc_id, lang_id)
    if "OS/2" in tt:
        tt["OS/2"].usWeightClass = weight
    if "head" in tt:
        mac = tt["head"].macStyle
        tt["head"].macStyle = (mac | 0x2) if italic else (mac & ~0x2)
    tt.save(path)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render(html_path: str, pdf_path: str, apply_glyph_fix: bool = True,
           preflight: bool = True, fail_on_warnings: bool = True,
           ignore_warnings=(), doctype=None) -> str:
    """Rendert HTML -> PDF mit WeasyPrint, inkl. FE0E-Fix und korrekter
    Fontconfig. Läuft immer mit Arbeitsverzeichnis /home/claude, damit
    relative Font-Pfade im CSS aufgehen. Gibt den absoluten PDF-Pfad zurück.

    HÄRTUNG: preflight=True lässt vor dem Rendern assert_render_ready()
    laufen (WeasyPrint-Fallen als harte Fehler). fail_on_warnings=True
    verwandelt jede WeasyPrint-WARNING (fehlende Fonts/Assets, ungültiges
    CSS) in einen RenderWarningError statt eines still kaputten PDFs."""
    if not _already_set_up():
        setup_fonts()
    os.environ["FONTCONFIG_FILE"] = FCCONF_PATH

    html_path = os.path.abspath(html_path)
    pdf_path = os.path.abspath(pdf_path)

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    if preflight:
        assert_render_ready(content, doctype=doctype)

    render_source = html_path
    if apply_glyph_fix:
        fixed = apply_fe0e(content)
        if fixed != content:
            render_source = html_path + ".fe0e.html"
            with open(render_source, "w", encoding="utf-8") as f:
                f.write(fixed)

    from weasyprint import HTML
    cwd = os.getcwd()
    try:
        os.chdir(BASE_DIR)
        with _weasy_log_capture() as caught:
            HTML(render_source).write_pdf(pdf_path)
    finally:
        os.chdir(cwd)
    if fail_on_warnings:
        _raise_on_weasy_warnings(caught, ignore_warnings,
                                 context=os.path.basename(html_path))

    print(f"Gerendert: {pdf_path}")
    return pdf_path


# ---------------------------------------------------------------------------
# Satzweiser Seitenumbruch (misst pro Chart, verdrahtet nichts fest)
# ---------------------------------------------------------------------------

def _walk(box):
    stack = [box]
    while stack:
        x = stack.pop()
        yield x
        stack.extend(getattr(x, "children", None) or [])


def _render_doc(html_str: str, apply_glyph_fix: bool = True,
                fail_on_warnings: bool = True, ignore_warnings=()):
    """Rendert einen HTML-String zu einem WeasyPrint-Document (nicht PDF),
    mit korrekter Fontconfig und Arbeitsverzeichnis - fuer die Vermessung der
    Satz-Positionen vor der PDF-Ausgabe. WeasyPrint-WARNINGs werden
    abgefangen und (fail_on_warnings=True) zu harten Fehlern."""
    if not _already_set_up():
        setup_fonts()
    os.environ["FONTCONFIG_FILE"] = FCCONF_PATH
    if apply_glyph_fix:
        html_str = apply_fe0e(html_str)
    from weasyprint import HTML
    cwd = os.getcwd()
    try:
        os.chdir(BASE_DIR)
        with _weasy_log_capture() as caught:
            # base_url ist PFLICHT: ohne sie verwirft WeasyPrint bei
            # HTML(string=...) ALLE relativen Pfade (Fonts, Radix-PNG) still.
            doc = HTML(string=html_str, base_url=BASE_DIR + "/").render()
    finally:
        os.chdir(cwd)
    if fail_on_warnings:
        _raise_on_weasy_warnings(caught, ignore_warnings,
                                 context="render_sentence_safe")
    return doc


def _sentence_pages(doc) -> dict:
    """id -> (min_seite, max_seite) fuer jeden Satz-Span (id beginnt 'S_')."""
    from collections import defaultdict
    pages = defaultdict(set)
    for pi, page in enumerate(doc.pages):
        for bx in _walk(page._page_box):
            el = getattr(bx, "element", None)
            if el is not None and hasattr(el, "get"):
                iid = el.get("id")
                if iid and iid.startswith("S_"):
                    pages[iid].add(pi)
    return {iid: (min(ps), max(ps)) for iid, ps in pages.items()}


def render_sentence_safe(build_html, pdf_path, colon_pairs=None,
                         apply_glyph_fix=True, max_rounds=300, verbose=True,
                         preflight=True, must_contain=None,
                         required_fields=None, fail_on_warnings=True,
                         ignore_warnings=(), doctype=None):
    """Rendert satz-sicher: KEIN Satz reisst ueber eine Seitenkante, und
    (via colon_pairs) kein Absatz endet mit Doppelpunkt/Semikolon als letzter
    Zeile einer Seite.

    build_html(breaks) -> HTML-String. Vertrag an den Chart-Builder:
      * Jeden Satz in <span id="S_<i>_<j>_<k>"> wrappen
        (i=Kapitel-Index, j=Block-Index, k=Satz-Index).
      * Satz-Segmente via build.split_sentences(absatztext) bilden.
      * Die uebergebene Menge `breaks` von (i,j,k)-Tupeln respektieren:
          - k > 0 : den Absatz VOR Satz k intern trennen; der zweite Teil
                    bekommt class="sbrk".
          - k = 0 : den GANZEN Absatz mit class="sbrk" auf die naechste Seite
                    (fuer Ein-Satz-Absaetze, die als Ganzes rutschen muessen);
                    NICHT beim ersten Absatz eines Kapitels anwenden (der bleibt
                    ueber break-inside:avoid am Kopf).
    colon_pairs: optionale Liste [(id_last, id_next), ...]. Fuer jeden Absatz,
      dessen letzter Satz auf : oder ; endet, das id seines letzten Satzes und
      das id des ersten Satzes des unmittelbar folgenden Absatzes (nur wenn der
      auch ein Textabsatz ist).
    doctype: 'ultimativ' | 'hdgk' | None — schaltet die typ-eigenen
      Pflicht-Bausteine im Preflight scharf (s. PFLICHT_BAUSTEINE).

    Greedy von oben: pro Runde wird nur der oberste noch offene Umbruch gesetzt,
    jeweils auf dem bereits fixierten Layout darueber - so wird kein Umbruch
    durch spaetere 'veraltet' (das liesse sonst halbe Seiten leer). Konvergiert
    typisch in wenigen Durchlaeufen. Gibt (doc, breaks, unfixable) zurueck und
    schreibt pdf_path.
    """
    colon_pairs = colon_pairs or []
    breaks, unfixable = set(), set()
    doc, rounds = None, 0
    first_round = True
    for _ in range(max_rounds):
        html_str = build_html(breaks)
        if first_round:
            if preflight:
                assert_render_ready(html_str, must_contain=must_contain,
                                    required_fields=required_fields,
                                    doctype=doctype)
            first_round = False
        doc = _render_doc(html_str, apply_glyph_fix=apply_glyph_fix,
                          fail_on_warnings=fail_on_warnings,
                          ignore_warnings=ignore_warnings)
        rounds += 1
        sp = _sentence_pages(doc)
        problems = []
        for iid, (mn, mx) in sp.items():           # a) Satz auf zwei Seiten
            if mx > mn:
                key = tuple(int(x) for x in iid.split("_")[1:])
                problems.append((mn, key, iid))
        for id_last, id_next in colon_pairs:       # b) Doppelpunkt am Seitenende
            if id_last in sp and id_next in sp and sp[id_next][0] > sp[id_last][1]:
                key = tuple(int(x) for x in id_last.split("_")[1:])
                problems.append((sp[id_last][1], key, id_last))
        problems.sort(key=lambda x: (x[0], x[1]))
        todo = None
        for _pg, key, iid in problems:
            if iid in unfixable:
                continue
            if key in breaks:                      # trotz Umbruch davor noch offen -> Satz > Seite
                unfixable.add(iid)
                continue
            todo = key
            break
        if todo is None:
            break
        breaks.add(todo)
    pdf_path = os.path.abspath(pdf_path)
    doc.write_pdf(pdf_path)
    if verbose:
        print(f"Satz-sicher gerendert: {pdf_path} ({len(doc.pages)} Seiten, "
              f"{len(breaks)} Umbrueche, {len(unfixable)} unfixbar, {rounds} Durchlaeufe)")
    return doc, breaks, unfixable


# ---------------------------------------------------------------------------
# HÄRTUNG 1: Festes Struktur-Schema für analyse.md + deterministischer Parser
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# @@DECKBLATT-Block — die Cover-Bestellung aus dem Datenblatt
#
# Der Block steht am Ende von <klient>[_KUERZEL]_chart_data.md, direkt hinter
# dem @@SELEKTOR-Block. NICHT in der analyse.md — das ist die Verwechslung, die
# am 2026-07-30 ein komplett falsches Cover erzeugt hat (Schritt 3 suchte nur
# in der analyse.md, fand nichts, zog die Fallback-Regel und erfand Leitsatz,
# Motiv, Palette und Glyphen neu).
#
# Deshalb wird der Block ab jetzt GELESEN statt abgetippt: der Chart-Builder
# ruft lies_deckblatt() und traegt Leitsatz/Titelmotiv nirgends von Hand ein.
# Fehlt der Block, bricht der Lauf ab, statt sich still etwas auszudenken.
# ---------------------------------------------------------------------------

DECKBLATT_PFLICHT = ('LEITSATZ', 'LEITACHSE', 'TITELMOTIV')
DECKBLATT_FELDER = DECKBLATT_PFLICHT + ('PALETTE', 'GLYPHEN')

_DB_START_RE = re.compile(r'^@@DECKBLATT\s*$')
_DB_ENDE_RE = re.compile(r'^@@ENDE\s*$')
_DB_FELD_RE = re.compile(r'^([A-ZÄÖÜ]{4,20})\s*:\s*(.*)$')


def lies_deckblatt(pfad: str, pflicht: bool = True) -> dict:
    """@@DECKBLATT-Block aus der chart_data.md lesen.

    pfad    Pfad der <klient>[_KUERZEL]_chart_data.md
    pflicht True (Vorgabe): fehlender oder unvollstaendiger Block ist ein
            harter Fehler. False: gibt None zurueck, wenn kein Block da ist —
            NUR fuer den dokumentierten Fallback, und nur nachdem in BEIDEN
            Dateien (chart_data.md UND analyse.md) gesucht wurde.

    Mehrzeilige Werte werden zusammengezogen: eine Zeile gehoert zum
    vorherigen Feld, solange sie nicht selbst mit `FELD:` beginnt. Damit sind
    umbrochene TITELMOTIV-/PALETTE-Zeilen unproblematisch.

    Rueckgabe: {'LEITSATZ':…, 'LEITACHSE':…, 'TITELMOTIV':…,
                'PALETTE':… , 'GLYPHEN':…} — die letzten beiden ggf. ''.
    """
    try:
        with open(pfad, encoding='utf-8') as fh:
            zeilen = fh.read().splitlines()
    except OSError as e:
        raise DeckblattError(f'chart_data nicht lesbar: {pfad} ({e})') from e

    start = None
    for i, z in enumerate(zeilen):
        if _DB_START_RE.match(z):
            start = i + 1
    if start is None:
        if not pflicht:
            return None
        raise DeckblattError(
            f'@@DECKBLATT-Block fehlt in {os.path.basename(pfad)}.\n'
            '  Der Block gehoert ans ENDE der chart_data.md, direkt hinter\n'
            '  den @@SELEKTOR-Block (s. Ultimativ-/Typ-Modul, Schritt 2) —\n'
            '  NICHT in die analyse.md.\n'
            '  Bevor die Fallback-Regel des Design-Moduls gezogen wird: in\n'
            '  BEIDEN Dateien nach "@@DECKBLATT" greppen und das Ergebnis\n'
            '  nennen. Ein ungeprueftes "fehlt" gilt nicht.')

    felder, key = {}, None
    for z in zeilen[start:]:
        if _DB_ENDE_RE.match(z):
            break
        m = _DB_FELD_RE.match(z)
        if m and m.group(1) in DECKBLATT_FELDER:
            key = m.group(1)
            felder[key] = m.group(2).strip()
        elif key and z.strip():
            felder[key] = (felder[key] + ' ' + z.strip()).strip()

    fehlt = [k for k in DECKBLATT_PFLICHT if not felder.get(k)]
    if fehlt:
        raise DeckblattError(
            f'@@DECKBLATT-Block in {os.path.basename(pfad)} unvollstaendig — '
            f'leer oder fehlend: {", ".join(fehlt)}. '
            f'Pflicht sind {", ".join(DECKBLATT_PFLICHT)}.')
    for k in ('PALETTE', 'GLYPHEN'):
        felder.setdefault(k, '')
    return {k: felder[k] for k in DECKBLATT_FELDER}


ANALYSE_SCHEMA = """\
STRUKTUR-SCHEMA für <klient>_analyse.md (v1). Schritt 2 SCHREIBT genau so,
parse_analyse() LIEST genau so — jede Abweichung ist ein harter SchemaError
mit Zeilennummer, kein stilles Fehlrendern.

    # <Dokumenttyp> — <Vorname Nachname>
        Genau EINE H1 als erste inhaltliche Zeile. Rechts vom " — " der
        Klientenname (Identitäts-Guardrail: Name explizit am Dateianfang).
        Beispiel: "# Geburtshoroskop — Alex Muster"

    ## <Kicker> — <Kapiteltitel>
        Jede H2 beginnt ein Kapitel. Links vom ersten " — " der Kicker
        (z. B. "Kapitel IV", "Zur Lesart"), rechts der Titel. Ohne " — "
        gilt die ganze Zeile als Titel, der Kicker bleibt leer
        (z. B. "## Schlusswort").

    ### <Zwischentitel>
        H3 = Zwischentitel (subhead) INNERHALB eines Kapitels.

    1. <Text>
        Nummerierte Liste: lückenlos ab 1, mindestens 2 Punkte, je Punkt ein
        eigener Block. Ein einzelner Absatz, der zufällig mit "N." beginnt
        ("3. Haus heißt: ..."), ist KEINE Liste — Listen starten bei 1.

    <Absatz>
        Alles andere: Fließtext-Absätze, durch Leerzeilen getrennt. Ein
        Absatz darf mit ":" oder ";" enden (Weiterführung; wird beim Umbruch
        an den Folgeabsatz gebunden).

    ## KAPITEL <n> · <Titel>  +  **Signatur:** …  +  **Beleg:** …
        OPTIONAL, additiv (Klartext-Modus): Kicker/Titel dürfen statt mit " — "
        auch mit " · " getrennt werden. Direkt unter der H2 — vor dem ersten
        Fließtextabsatz — dürfen eine "**Signatur:** …"- und eine "**Beleg:** …"-
        Zeile stehen (auch mit Leerzeile dazwischen). Sie wandern nach
        chapter['signatur']/['beleg'], zählen NICHT als Absatz und sind von der
        Inline-Markup- (**) und Satzende-Prüfung ausgenommen. Fehlen sie, gilt
        exakt das Standardverhalten.

VERBOTEN (harte Fehler, je mit Zeilennummer):
  - H4+ (####); Text vor der H1 oder zwischen H1 und erstem Kapitel
  - Zeilen, die Listennummer und Überschrift mischen ("3. ## Kapitel ...")
  - Markdown-Tabellen und Inline-Markup (**fett**, `code`, [link](...)) —
    analyse.md ist reiner Fließtext; Tabellen gehören in chart_data.md
  - Platzhalter ({{...}}, TODO, FIXME, ???)
  - leere Kapitel (H2 ohne Textblöcke); doppelte Kicker/Titel
  - Absätze, die mitten im Satz enden (letztes Zeichen kein . ! ? … : ;)
    oder auf 1-2-stelliger Ordinalzahl ("… ins 3.") enden — typisches
    Zerreiß-Artefakt aus PDF-Rekonstruktionen
  - Absätze, die (nach öffnenden Anführungszeichen) klein beginnen —
    ebenfalls Zerreiß-Artefakt: mit dem Vorgänger zusammenführen
"""

_H_RE = re.compile(r'^(#{1,6})\s+(.*\S)\s*$')
_LI_START_RE = re.compile(r'^(\d{1,2})\.\s+(?!#)(.+)$', re.S)
_MIXED_HEAD_RE = re.compile(r'^\s*\d{1,2}\.\s*#{1,6}')
_PLACEHOLDER_RE = re.compile(r'\{\{|\}\}|\bTODO\b|\bFIXME\b|\?\?\?')
_INLINE_MARKUP_RE = re.compile(r'\*\*|`|\]\(')
_TABLE_LINE_RE = re.compile(r'^\s*\|')
_ORD_END_RE = re.compile(r'(?:^|[\s(])\d{1,2}\.$')
_OPENERS = '„“"»«(\'‘‚['
_CLOSERS = '“”"»«)\'’]'


# ---------------------------------------------------------------------------
# Klartext-Erweiterung (ADDITIV): Kapitelkopf-Trenner „·" gleichwertig zu
# „ — ", plus optionale Signatur/Beleg-Zeilen direkt unter der Kapitel-H2.
# Greift ausschließlich bei Klartext-Charts; eine normale analyse.md (ohne „·"
# im Kapiteltitel und ohne **-Zeilen) durchläuft unverändert das alte Verhalten.
# ---------------------------------------------------------------------------
_KICKER_SEPS = (" — ", " · ")
_SIG_LINE_RE = re.compile(r'^\*\*\s*Signatur\s*:\s*\*\*\s*(.*)$', re.S)
_BEL_LINE_RE = re.compile(r'^\*\*\s*Beleg\s*:\s*\*\*\s*(.*)$', re.S)
_BEL_INLINE_SPLIT_RE = re.compile(r'\s*\*\*\s*Beleg\s*:\s*\*\*\s*')

# Astrologische Glyphen, die im Beleg-Streifen zulässig sind (Planeten/Punkte,
# Aspektzeichen, Tierkreiszeichen, Grad/Bogenminute). Werden von der GLYPHEN-
# Prüfung in assert_render_ready mitkontrolliert (targeted hint, s. u.).
_BELEG_GLYPHS = set("☉☽☿♀♂♃♄♅♆♇⚷⚸☊☋☌☍□△⚹♈♉♊♋♌♍♎♏♐♑♒♓°′″")


def _split_kicker_title(text):
    """Kicker/Titel am ERSTEN vorkommenden Trenner aus _KICKER_SEPS trennen
    („ — " ODER „ · ", positionsbasiert gleichwertig). Ohne Trenner: kein
    Kicker, ganze Zeile ist Titel. Für „ — " exakt das bisherige Verhalten."""
    best = None
    for sep in _KICKER_SEPS:
        i = text.find(sep)
        if i >= 0 and (best is None or i < best[0]):
            best = (i, sep)
    if best is None:
        return "", text.strip()
    i, sep = best
    return text[:i].strip(), text[i + len(sep):].strip()


def _consume_klartext_head(cur, text):
    """Fängt in einem Rohblock direkt unter der Kapitel-H2 die optionalen
    Klartext-Zeilen **Signatur:** … und **Beleg:** … ab (auch gemeinsam in
    EINEM Block, wenn keine Leerzeile dazwischenstand). Füllt cur['signatur']/
    ['beleg'] und gibt True zurück, wenn der Block ein Kopfblock war (dann NICHT
    als Absatz weiterverarbeiten). So bleiben Signatur/Beleg aus blocks heraus,
    von der Inline-Markup- und Satzende-Prüfung ausgenommen (analog subhead),
    und die Drop-Cap bleibt auf dem ersten echten Fließtextabsatz."""
    ms = _SIG_LINE_RE.match(text)
    if ms and cur["signatur"] is None:
        parts = _BEL_INLINE_SPLIT_RE.split(ms.group(1), 1)
        cur["signatur"] = parts[0].strip()
        if len(parts) > 1 and cur["beleg"] is None:
            cur["beleg"] = parts[1].strip()
        return True
    mb = _BEL_LINE_RE.match(text)
    if mb and cur["beleg"] is None:
        cur["beleg"] = mb.group(1).strip()
        return True
    return False


def parse_analyse(path: str, client: str = None) -> dict:
    """Liest <klient>_analyse.md strikt nach ANALYSE_SCHEMA.

    client: erwarteter Klientenname; weicht die H1 ab, ist das ein Fehler
    (Identitäts-Guardrail gegen Datei-Verwechslung).

    Rückgabe: {'h1','doctype','client','chapters':[{'kicker','title','line',
    'blocks':[{'type':'p'|'li'|'subhead','text','line'},...]},...]}
    Wirft SchemaError mit ALLEN Funden (Zeilennummer + Erwartung)."""
    with open(path, encoding="utf-8") as f:
        raw = f.read().replace("\r\n", "\n").replace("\r", "\n")
    lines = raw.split("\n")
    errors = []

    def err(ln, msg):
        errors.append((ln, msg))

    # 1) Zeilen -> Rohblöcke (Überschriften einzeln; Text bis zur Leerzeile)
    blocks = []          # (zeile, art, text)   art: h1..h6 | raw
    buf, buf_start = [], None

    def flush():
        nonlocal buf, buf_start
        if buf:
            blocks.append((buf_start, "raw", " ".join(s.strip() for s in buf)))
        buf, buf_start = [], None

    for idx, line in enumerate(lines, 1):
        if not line.strip():
            flush()
            continue
        if _MIXED_HEAD_RE.match(line):
            flush()
            err(idx, f"Zeile mischt Listennummer und Überschrift: "
                     f"{line.strip()[:60]!r} — Nummer entfernen.")
            m = _H_RE.match(re.sub(r'^\s*\d{1,2}\.\s*', '', line))
            if m:
                blocks.append((idx, f"h{len(m.group(1))}", m.group(2).strip()))
            continue
        m = _H_RE.match(line)
        if m:
            flush()
            blocks.append((idx, f"h{len(m.group(1))}", m.group(2).strip()))
            continue
        if _TABLE_LINE_RE.match(line):
            flush()
            err(idx, "Markdown-Tabellenzeile — Tabellen gehören nach chart_data.md.")
            continue
        if buf_start is None:
            buf_start = idx
        buf.append(line)
    flush()

    # 2) Struktur aufbauen
    h1, h1_line, doctype, client_name = None, None, None, None
    chapters, cur = [], None
    if not blocks:
        err(1, "Datei ist leer.")
    elif blocks[0][1] != "h1":
        err(blocks[0][0], "Erste inhaltliche Zeile muss die H1 sein "
                          "('# <Dokumenttyp> — <Klientenname>').")
    for ln, kind, text in blocks:
        if kind == "h1":
            if h1 is not None:
                err(ln, "Mehr als eine H1 — genau eine erlaubt.")
                continue
            h1, h1_line = text, ln
        elif kind == "h2":
            kicker, title = _split_kicker_title(text)
            cur = {"kicker": kicker, "title": title, "line": ln, "blocks": [],
                   "signatur": None, "beleg": None}
            chapters.append(cur)
        elif kind == "h3":
            if cur is None:
                err(ln, "Zwischentitel (###) vor dem ersten Kapitel (##).")
            else:
                cur["blocks"].append({"type": "subhead", "text": text, "line": ln})
        elif kind in ("h4", "h5", "h6"):
            err(ln, f"Überschriftenebene {kind.upper()} nicht im Schema "
                    "(nur #, ##, ###).")
        else:  # raw
            if cur is None:
                err(ln, "Text vor dem ersten Kapitel (##).")
                continue
            # Klartext-Kopfblock (ADDITIV): optionale Signatur/Beleg-Zeile direkt
            # unter der H2, VOR dem ersten Fließtextabsatz. Nur solange das
            # Kapitel noch keinen Block hat; normale Kapitel (ohne **) nie.
            if not cur["blocks"] and _consume_klartext_head(cur, text):
                continue
            m = _LI_START_RE.match(text)
            if m:
                cur["blocks"].append({"type": "li?", "num": int(m.group(1)),
                                      "text": text, "line": ln})
            else:
                cur["blocks"].append({"type": "p", "text": text, "line": ln})

    if h1 is None:
        err(1, "H1 fehlt: '# <Dokumenttyp> — <Klientenname>' als erste Zeile.")
    else:
        if " — " in h1:
            doctype, client_name = (x.strip() for x in h1.split(" — ", 1))
        else:
            err(h1_line, "H1 braucht das Format '# <Dokumenttyp> — <Klientenname>'.")
        if client and client_name and client.strip().casefold() != client_name.casefold():
            err(h1_line, f"Klientenname in H1 ({client_name!r}) != erwartet "
                         f"({client!r}) — Identitäts-Guardrail: richtige Datei?")

    # 3) Listen auflösen: nur lückenlose Läufe ab 1 (>=2 Punkte) sind Listen
    for ch in chapters:
        bl, i = ch["blocks"], 0
        while i < len(bl):
            if bl[i]["type"] == "li?":
                j = i
                while j < len(bl) and bl[j]["type"] == "li?":
                    j += 1
                nums = [bl[k]["num"] for k in range(i, j)]
                if nums == list(range(1, len(nums) + 1)) and len(nums) >= 2:
                    for k in range(i, j):
                        bl[k]["type"] = "li"
                        bl[k]["text"] = re.sub(r'^\d{1,2}\.\s+', '', bl[k]["text"])
                else:
                    for k in range(i, j):
                        bl[k]["type"] = "p"
                i = j
            else:
                i += 1

    # 4) Kapitel-/Absatz-Prüfungen
    seen = {}
    for ch in chapters:
        key = (ch["kicker"] or ch["title"]).casefold()
        if key in seen:
            err(ch["line"], f"Kapitel doppelt: {ch['kicker'] or ch['title']!r} "
                            f"(auch Zeile {seen[key]}).")
        else:
            seen[key] = ch["line"]
        if not ch["blocks"]:
            err(ch["line"], f"Kapitel {ch['kicker'] or ch['title']!r} ist leer.")
        for b in ch["blocks"]:
            if b["type"] == "subhead":
                continue
            t = b["text"]
            if _PLACEHOLDER_RE.search(t):
                err(b["line"], "Platzhalter im Text ({{...}}/TODO/FIXME/???).")
            if _INLINE_MARKUP_RE.search(t):
                err(b["line"], "Inline-Markup (** ` ]( ) — analyse.md ist reiner Fließtext.")
            head = t.lstrip()
            while head and head[0] in _OPENERS:
                head = head[1:]
            fa = next((c for c in head if c.isalpha()), "")
            if fa and fa.islower():
                err(b["line"], f"Absatz beginnt klein ({head[:40]!r}…) — "
                               "zerrissener Absatz? Mit Vorgänger zusammenführen.")
            tail = t.rstrip()
            while tail and tail[-1] in _CLOSERS:
                tail = tail[:-1].rstrip()
            last = tail[-1] if tail else ""
            if last in ":;":
                pass
            elif last in ".!?…":
                if _ORD_END_RE.search(tail):
                    err(b["line"], f"Absatz endet auf Ordinalzahl ({tail[-25:]!r}) — "
                                   "zerrissener Absatz (PDF-Artefakt)? Mit Folgeabsatz "
                                   "zusammenführen.")
            else:
                err(b["line"], f"Absatz endet mitten im Satz ({tail[-40:]!r}).")

    if errors:
        errors.sort()
        listing = "\n".join(f"  Zeile {ln}: {m}" for ln, m in errors)
        raise SchemaError(
            f"{os.path.basename(path)} verletzt das analyse.md-Schema "
            f"({len(errors)} Fund(e)):\n{listing}\n"
            f"Schema: build.ANALYSE_SCHEMA. Quelle korrigieren statt rendern.")
    return {"h1": h1, "doctype": doctype, "client": client_name,
            "chapters": chapters}


def chapter_markers(parsed: dict) -> list:
    """Kapiteltitel in Dokumentreihenfolge — direkt für verify(markers=...)."""
    return [ch["title"] for ch in parsed["chapters"]]


def prepare_chapters(parsed: dict) -> list:
    """Dekoriert parse_analyse()-Kapitel für den satzsicheren Builder:
    p-Blöcke bekommen 'sent' (split_sentences), 'colon_end' und 'next_p' —
    exakt die Struktur, die der Referenz-Builder erwartet."""
    items = []
    for ch in parsed["chapters"]:
        it = {"kicker": ch["kicker"], "title": ch["title"],
              "signatur": ch.get("signatur"), "beleg": ch.get("beleg"),
              "blocks": [dict(b) for b in ch["blocks"]]}
        bl = it["blocks"]
        for j, b in enumerate(bl):
            if b["type"] == "p":
                b["sent"] = split_sentences(b["text"])
                last = b["sent"][-1].rstrip()
                b["colon_end"] = last.endswith(":") or last.endswith(";")
                nj = j + 1
                b["next_p"] = nj if (nj < len(bl) and bl[nj]["type"] == "p") else None
        items.append(it)
    return items


def make_colon_pairs(items: list) -> list:
    """(id_letzter_satz, id_erster_satz_folgeabsatz) für alle :-/;-Absätze —
    direkt als colon_pairs an render_sentence_safe()."""
    pairs = []
    for i, it in enumerate(items):
        for j, b in enumerate(it["blocks"]):
            if b["type"] == "p" and b.get("colon_end") and b.get("next_p") is not None:
                pairs.append((f"S_{i}_{j}_{len(b['sent']) - 1}",
                              f"S_{i}_{b['next_p']}_0"))
    return pairs


# ---------------------------------------------------------------------------
# HÄRTUNG 2: WeasyPrint-Fallen als harte Vorab-Assertions
# ---------------------------------------------------------------------------

_STYLE_RE = re.compile(r'<style[^>]*>([\s\S]*?)</style>', re.I)
_TAG_RE = re.compile(r'<[^>]+>')
_URL_RE = re.compile(r'url\(\s*["\']?([^"\')]+?)["\']?\s*\)')
_IMG_RE = re.compile(r'<img[^>]+src\s*=\s*["\']([^"\']+)["\']', re.I)
_ENTITY_RE = re.compile(r'&#(x[0-9A-Fa-f]+|[0-9]+);')
_CSS_HEX_ESCAPE_RE = re.compile(r'\\[0-9A-Fa-f]{2,6}\b')
_FIRSTLETTER_FLOAT_RE = re.compile(r'::?first-letter[^{}]*\{[^}]*float', re.I)
_MARGIN_AUTO_RE = re.compile(r'margin-top\s*:\s*auto', re.I)
_SVG_RE = re.compile(r'<svg\b[\s\S]*?</svg>', re.I)
_CONTENT_STR_RE = re.compile(r'content\s*:\s*"((?:[^"\\]|\\.)*)"')

_COVERAGE_CACHE = {"chars": None}


def _coverage_charset() -> set:
    """Vereinigte cmap aller über UNSERE Fontconfig sichtbaren Fonts
    (NotoColorEmoji ist dort ausgeschlossen). Einmal pro Session gecacht."""
    if _COVERAGE_CACHE["chars"] is not None:
        return _COVERAGE_CACHE["chars"]
    files = set()
    try:
        outp = subprocess.run(
            ["fc-list", "--format", "%{file}\n"], capture_output=True,
            text=True, timeout=60,
            env={**os.environ, "FONTCONFIG_FILE": FCCONF_PATH})
        for line in outp.stdout.splitlines():
            line = line.strip()
            if line and os.path.isfile(line) and line.lower().endswith((".ttf", ".otf")):
                files.add(line)
    except Exception:
        pass
    if os.path.isdir(FONTS_DIR):
        for f in os.listdir(FONTS_DIR):
            if f.endswith(".ttf"):
                files.add(os.path.join(FONTS_DIR, f))
    chars = set()
    from fontTools.ttLib import TTFont
    for p in sorted(files):
        try:
            tt = TTFont(p, lazy=True, fontNumber=0)
            cm = tt.getBestCmap()
            if cm:
                chars.update(cm.keys())
            tt.close()
        except Exception:
            continue
    _COVERAGE_CACHE["chars"] = chars
    return chars


# ---------------------------------------------------------------------------
# Pflicht-Bausteine je Dokumenttyp.
#
# Warum als Code und nicht nur als Modultext: Am 2026-07-26 fehlten in einem
# Ultimativ-Lauf Inhaltsverzeichnis, Transit-Uhr und Anhang, obwohl die Regel
# im Ultimativ-Modul stand — sie wurde beim Lesen der Schritt-3-Module schlicht
# nicht mitgenommen. Eine Vorschrift, an die man sich erinnern muss, ist
# schwaecher als eine, die anschlaegt. Fehlt hier ein Baustein, rendert das
# Dokument gar nicht erst.
#
# 'text' wird im SICHTBAREN Text gesucht (Ueberschriften), 'html' im Rohtext
# (z. B. eingebundene Grafiken). Aenderst du eine Zeile, ziehe den Abschnitt
# „Pflicht-Bausteine" in Projektanweisung_Modul_Design_Render.md nach.
# ---------------------------------------------------------------------------

PFLICHT_BAUSTEINE = {
    # Die '*'-Basis ist die Chart-Basis: sie gilt fuer jedes Dokument, das ein
    # Geburtsbild ABBILDET. Begleitdokumente, die auf ein bereits geliefertes
    # Horoskop aufsetzen, setzen "basis": False und bringen ihre eigene Liste
    # mit (s. 'themen').
    "*": {
        "text": [("Inhalt", "Inhaltsverzeichnis-Seite nach dem Deckblatt"),
                 ("Die Aspekte im Wortlaut", "voll ausgeschriebene Aspekttabelle"),
                 ("Die Aspekte und was sie bedeuten", "Aspekt-Legende")],
        "html": [("_radix.png", "Radix-Rad auf Seite 1 (radix.py)")],
    },
    "ultimativ": {
        "text": [("Die Transit-Uhr", "Transit-Uhr auf der Chartbild-Strecke"),
                 ("Die langen Linien im Überblick", "Anhang: volle Transit-Tabelle"),
                 ("Der Stichtag im Überblick", "Anhang: Jetzt-Tabelle")],
        "html": [("_transituhr.png", "Transit-Uhr-Grafik (transituhr.py)")],
    },
    "hdgk": {
        "text": [("Bodygraph", "Bodygraph-Grafik im HD/GK-Teil")],
        "html": [],
    },
    # Themen-Analyse (eingefuehrt 2026-08-01): eigenstaendiges Begleitheft zu
    # einem bereits ausgelieferten Horoskop, das zwei bis drei Lebensthemen
    # vertieft. Es zeigt bewusst KEIN Radix-Rad und KEINE Aspekttabelle — beide
    # stehen im Hauptdokument, und eine zweite Kopie waere Ballast. Statt der
    # Chartbild-Strecke traegt es eine Uebersicht der Faktoren, die seine
    # Themen tragen. Die Pflicht bleibt damit erhalten, sie zeigt nur auf
    # andere Bausteine.
    "themen": {
        "basis": False,
        "text": [("Inhalt", "Inhaltsverzeichnis-Seite nach dem Deckblatt"),
                 ("Die tragenden Konstellationen",
                  "Übersicht der Faktoren, auf denen die Themen fußen"),
                 ("Die Transit-Uhr", "Transit-Uhr über das Themenfenster"),
                 ("Die Zeitfenster im Überblick", "Anhang: Zeitfenster-Tabelle")],
        "html": [("_uhr.png", "Transit-Uhr-Grafik (transituhr_fusion.py)")],
    },
}


def pflicht_bausteine(doctype=None) -> dict:
    """Pflichtliste fuer einen Dokumenttyp.

    Standardfall: die '*'-Chart-Basis PLUS die typ-eigenen Eintraege.
    Setzt ein Typ "basis": False, gilt AUSSCHLIESSLICH seine eigene Liste —
    fuer Begleitdokumente, die kein Geburtsbild abbilden. Unbekannte Typen
    liefern die Chart-Basis; ein Tippfehler im doctype schwaecht den Guardrail
    also nicht ab, sondern faellt auf die strengere Liste zurueck.
    """
    basis = PFLICHT_BAUSTEINE["*"]
    extra = PFLICHT_BAUSTEINE.get((doctype or "").strip().lower(),
                                  {"text": [], "html": []})
    if extra.get("basis", True) is False:
        return {"text": list(extra["text"]), "html": list(extra["html"])}
    return {"text": list(basis["text"]) + list(extra["text"]),
            "html": list(basis["html"]) + list(extra["html"])}


def assert_render_ready(html_str: str, base_dir: str = None, must_contain=None,
                        required_fields=None, check_glyph_coverage=True,
                        doctype=None) -> dict:
    """Harte Vorab-Assertions gegen die bekannten WeasyPrint-Fallen. Wirft
    RenderReadyError mit ALLEN Funden (nicht nur dem ersten):

      FONTS      alle 7 Schriftschnitte instanziert (sonst setup_fonts())
      ASSETS     jedes url(...)/<img src=...> existiert (relativ zu base_dir)
      CHARSET    <meta charset="utf-8"> vorhanden
      ENTITIES   keine numerischen HTML-Entities >= U+2000: FE0E-Fix und
                 Glyph-Prüfung sehen Entities nicht — literal schreiben
      CSS-ESCAPE keine CSS-Hex-Escapes (\\2609 …) — literal schreiben
      DROP-CAP   kein float auf ::first-letter — <span class="dropcap">
      SVG-TEXT   kein <text> in Inline-SVG (rendert nicht) — HTML-Span drüber
      FLEX-AUTO  kein margin-top:auto (wird ignoriert) — .cover-anchor-*
      GLYPHEN    jedes sichtbare Nicht-ASCII-Zeichen ist in mindestens einer
                 verfügbaren Font vorhanden (sonst leere Box im PDF)
      FELDER     required_fields={'Name': wert, ...} alle nicht-leer
      VOLLTEXT   must_contain=[(text,label)|text, ...]: jeder Block ist
                 wirklich im HTML gelandet (gegen still verlorene Absätze)
      PFLICHT    doctype='ultimativ'|'hdgk'|None: die Pflicht-Bausteine aus
                 PFLICHT_BAUSTEINE sind im Dokument vorhanden (Inhalts-
                 verzeichnis, Radix, Aspekttabelle, Legende + typ-eigene)
      REST       keine Platzhalter ({{...}}, TODO, FIXME, ???)"""
    if base_dir is None:
        base_dir = BASE_DIR
    problems = []
    styles = "\n".join(m.group(1) for m in _STYLE_RE.finditer(html_str))
    styles = re.sub(r'/\*[\s\S]*?\*/', '', styles)     # CSS-Kommentare sind
    body_html = _STYLE_RE.sub(" ", html_str)           # keine Befunde
    visible = _html.unescape(_TAG_RE.sub("", body_html))

    missing_fonts = [f for f in EXPECTED_FONT_FILES
                     if not os.path.isfile(os.path.join(FONTS_DIR, f))]
    if missing_fonts:
        problems.append(f"FONTS fehlen ({', '.join(missing_fonts)}) — "
                        "build.setup_fonts() ausführen.")

    seen_assets = set()
    for m in list(_URL_RE.finditer(styles)) + list(_URL_RE.finditer(body_html)) \
            + list(_IMG_RE.finditer(body_html)):
        ref = m.group(1).strip()
        if (ref.startswith(("data:", "http://", "https://", "#"))
                or ref in seen_assets):
            continue
        seen_assets.add(ref)
        full = ref if os.path.isabs(ref) else os.path.join(base_dir, ref)
        if not os.path.isfile(full):
            problems.append(f"ASSET fehlt: {ref!r} (aufgelöst: {full}) — "
                            "Pfad/Erzeugung prüfen; render() läuft mit "
                            f"Arbeitsverzeichnis {base_dir}.")

    if not re.search(r'<meta\s+charset\s*=\s*["\']?utf-8', html_str, re.I):
        problems.append('CHARSET: <meta charset="utf-8"> fehlt im <head>.')

    bad_entities = set()
    for m in _ENTITY_RE.finditer(html_str):
        g = m.group(1)
        cp = int(g[1:], 16) if g.startswith("x") else int(g)
        if cp >= 0x2000:                    # &#39; u. ä. aus html.escape bleiben ok
            bad_entities.add(m.group(0))
    bad_entities = sorted(bad_entities)
    if bad_entities:
        problems.append("ENTITIES: numerische HTML-Entities für Symbole "
                        f"({', '.join(bad_entities[:8])}) — literale "
                        "Unicode-Glyphen schreiben (FE0E-Fix greift sonst nicht).")

    if _CSS_HEX_ESCAPE_RE.search(styles):
        problems.append("CSS-ESCAPE: CSS-Hex-Escape (\\XXXX) gefunden — "
                        "literale Zeichen statt Escapes verwenden.")
    if _FIRSTLETTER_FLOAT_RE.search(styles):
        problems.append("DROP-CAP: float auf ::first-letter rendert in "
                        "WeasyPrint falsch — <span class=\"dropcap\"> verwenden.")
    if (_MARGIN_AUTO_RE.search(styles)
            or re.search(r'style\s*=\s*"[^"]*margin-top\s*:\s*auto', body_html, re.I)):
        problems.append("FLEX-AUTO: margin-top:auto wird von WeasyPrint "
                        "ignoriert — absolute Positionierung (.cover-anchor-*).")
    for svg in _SVG_RE.finditer(body_html):
        if re.search(r'<text\b', svg.group(0), re.I):
            problems.append("SVG-TEXT: <text> in Inline-SVG rendert nicht — "
                            "Glyphen als absolut positionierte HTML-Spans "
                            "über das SVG legen.")
            break

    chars = []
    if check_glyph_coverage:
        pool = set(visible)
        for m in _CONTENT_STR_RE.finditer(styles):
            pool.update(m.group(1))
        chars = sorted({c for c in pool if ord(c) > 126
                        and unicodedata.category(c)[0] not in ("C", "Z")
                        and unicodedata.category(c) != "Mn"})
        cov = _coverage_charset()
        uncovered = [c for c in chars if ord(c) not in cov]
        if uncovered:
            lst = ", ".join(f"{c!r} U+{ord(c):04X}" for c in uncovered[:20])
            # ADDITIV: Beleg-/Aspektglyphen (Klartext-Modus) gezielt benennen,
            # falls sie unter den ungedeckten sind — sie sind dort zwingend.
            beleg_hit = [c for c in uncovered if c in _BELEG_GLYPHS]
            extra = ("" if not beleg_hit else
                     " Darunter Beleg-/Aspektglyphen (" + " ".join(beleg_hit) +
                     ") — im Klartext-Modus zwingend; Font mit diesen Symbolen "
                     "(z. B. DejaVu Sans/Symbola) bereitstellen.")
            problems.append(f"GLYPHEN ohne Font-Abdeckung: {lst} — würden als "
                            "leere Box gerendert. Zeichen prüfen oder Font ergänzen."
                            + extra)

    for k, v in (required_fields or {}).items():
        if v is None or not str(v).strip():
            problems.append(f"PFLICHTFELD leer: {k!r}.")

    hay = re.sub(r'\s+', ' ', visible)
    if must_contain:
        for item in must_contain:
            text, label = item if isinstance(item, (tuple, list)) else (item, None)
            needle = re.sub(r'\s+', ' ', str(text)).strip()
            if needle and needle not in hay:
                problems.append("VOLLTEXT: Block fehlt im HTML: "
                                f"{label or needle[:60] + '…'!r}")

    pflicht = pflicht_bausteine(doctype)
    for needle, label in pflicht["text"]:
        if re.sub(r'\s+', ' ', needle).strip() not in hay:
            problems.append(f"PFLICHT-BAUSTEIN fehlt: {label} "
                            f"(erwartet im sichtbaren Text: {needle!r}). "
                            "Siehe build.PFLICHT_BAUSTEINE und den Abschnitt "
                            "„Pflicht-Bausteine\" im Design-Modul.")
    for needle, label in pflicht["html"]:
        if needle not in html_str:
            problems.append(f"PFLICHT-BAUSTEIN fehlt: {label} "
                            f"(erwartet im HTML: {needle!r}). "
                            "Siehe build.PFLICHT_BAUSTEINE und den Abschnitt "
                            "„Pflicht-Bausteine\" im Design-Modul.")

    if _PLACEHOLDER_RE.search(visible):
        problems.append("PLATZHALTER im sichtbaren Text ({{...}}/TODO/FIXME/???).")

    if problems:
        raise RenderReadyError(
            f"HTML nicht renderfähig — {len(problems)} Befund(e):\n"
            + "\n".join(f"  [{i + 1}] {p}" for i, p in enumerate(problems)))
    return {"checks": 12, "glyphs_checked": len(chars)}


# ---------------------------------------------------------------------------
# HÄRTUNG 3: Deterministische PDF-Endprüfung (pdfinfo/pdftotext statt Bilder)
# ---------------------------------------------------------------------------

_LIG_MAP = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi",
            "ﬄ": "ffl", "\u00ad": ""}


def _nrm(s: str) -> str:
    for k, v in _LIG_MAP.items():
        s = s.replace(k, v)
    return re.sub(r'\s+', ' ', s).strip()


def _dehyph(s: str) -> str:
    """Löst Silbentrennungen aus dem Seitentext ('Selbstbe- hauptung').

    Zweite Regel (2026-07-31): ein ECHTER Bindestrich in einem Kompositum darf
    am Zeilenende stehen ('Nicht-\nDazugehörens'). Er wird nicht geschluckt —
    nur der Zeilenumbruch dahinter fällt weg, der Bindestrich bleibt. Ohne das
    verfehlte verify(markers=…) jeden Kapiteltitel, der an einem eigenen
    Bindestrich umbricht, und meldete ihn als fehlend, obwohl er vollständig
    im PDF steht.
    """
    s = re.sub(r'([A-Za-zÄÖÜäöüß])-\s([a-zäöüß])', r'\1\2', s)
    return re.sub(r'([A-Za-zÄÖÜäöüß])-\s+([A-ZÄÖÜ])', r'\1-\2', s)


def _find_marker(marker, hay, start=0):
    """Findet `marker` in `hay` tolerant gegen Gross-/Kleinschreibung UND
    beliebige Leerraeume zwischen den Zeichen. Hintergrund: gesperrt gesetzte
    Versal-Ueberschriften (text-transform:uppercase + letter-spacing) liefert
    pdftotext mal als 'ASPEKTE', mal als 'A S P E K T E' — ein woertliches
    find() verfehlt sie dann. Gibt ein Match-Objekt (.start()/.end()) oder None
    zurueck; gedacht fuer die Abschnittsmarker in verify(aspect_section=...).
    Damit duerfen diese Marker im Chart-HTML beliebig gestylt sein (Versalien,
    Sperrung) — sie muessen nicht mehr in Normalschrift stehen."""
    chars = [c for c in marker if not c.isspace()]
    if not chars:
        return None
    pat = re.compile(r'\s*'.join(re.escape(c) for c in chars), re.I)
    return pat.search(hay, start)


def _pdf_pages_text(pdf_path: str) -> list:
    out = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8",
                          pdf_path, "-"], capture_output=True, check=True)
    pages = out.stdout.decode("utf-8", "replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def pdf_info(pdf_path: str) -> dict:
    out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, check=True)
    info = {}
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            info[k.strip()] = v.strip()
    return info


def verify(pdf_path: str, expected_pages=None, markers=None, kickers=None,
           aspect_rows=None, aspect_section=None, prose_start=None,
           source_text_chars=None, min_coverage=0.97, min_lines=8,
           sample_page=1, sample_dpi=80, verbose=True) -> dict:
    """Deterministische End-Prüfung des PDFs über pdfinfo/pdftotext.
    KEINE Bildschau außer genau EINER Stichprobenseite (sample_page,
    Standard 1 = Cover; None = keine).

      expected_pages     int oder (min, max): erwartete Seitenzahl
      markers            Kapiteltitel in Reihenfolge (chapter_markers(parsed));
                         jeder muss vorkommen, Reihenfolge wird geprüft
      kickers            Kicker-Liste; Präsenz (uppercase) wird geprüft
      aspect_rows        erwartete Zeilen der Aspekttabelle (= len(aspektliste))
      aspect_section     (start_marker, end_marker|None) grenzt den Tabellen-
                         abschnitt im Text ab; gezählt werden Orb-Einträge N°NN′
      prose_start        Marker der ersten Prosaseite. Ab dort gilt je Seite:
                         letzte Textzeile endet auf Satzende (. ! ? …), nie auf
                         : ; oder mitten im Satz/Wort — und keine Seite außer
                         der letzten ist auffällig leer (< min_lines Zeilen)
      source_text_chars  Zeichenzahl der Quelle (Prosa, normalisiert):
                         Textdeckung < min_coverage => verlorene Absätze
      sample_page        genau EINE Seite als PNG rastern (Report['sample_png'])

    Rückgabe: Report-dict. Wirft VerifyError mit ALLEN Befunden."""
    pdf_path = os.path.abspath(pdf_path)
    fails, warns = [], []
    info = pdf_info(pdf_path)
    n_pages = int(info.get("Pages", "0"))
    if expected_pages is not None:
        if isinstance(expected_pages, (tuple, list)):
            lo, hi = expected_pages
            if not (lo <= n_pages <= hi):
                fails.append(f"SEITENZAHL {n_pages} außerhalb {lo}–{hi}.")
        elif n_pages != int(expected_pages):
            fails.append(f"SEITENZAHL {n_pages} statt erwartet {expected_pages}.")

    pages = _pdf_pages_text(pdf_path)
    if len(pages) != n_pages:
        warns.append(f"pdftotext lieferte {len(pages)} Seiten, pdfinfo {n_pages}.")
    pages_n = [_nrm(p) for p in pages]
    whole = " \x0c ".join(pages_n)
    whole_d = _dehyph(whole)

    marker_pages = {}
    if markers:
        pos = 0
        for mk in markers:
            needle = _dehyph(_nrm(mk))
            i = whole_d.find(needle, pos)
            if i < 0:
                if whole_d.find(needle) >= 0:
                    fails.append(f"MARKER-REIHENFOLGE verletzt: {mk!r}.")
                else:
                    fails.append(f"MARKER fehlt im PDF-Text: {mk!r}.")
                continue
            pos = i + len(needle)
            marker_pages[mk] = next((pi + 1 for pi, pt in enumerate(pages_n)
                                     if needle in _dehyph(pt)), None)
    if kickers:
        # Kicker sind gesperrt gesetzt (letter-spacing) -> pdftotext liefert
        # 'Z U R L E S A RT'; Vergleich darum ohne jede Leerstelle.
        hay_ds = whole_d.replace(" ", "")
        for k in kickers:
            if k and k.upper().replace(" ", "") not in hay_ds:
                fails.append(f"KICKER fehlt im PDF-Text: {k.upper()!r}.")

    found_rows = None
    if aspect_rows is not None:
        if not aspect_section:
            fails.append("ASPEKTE: aspect_rows gesetzt, aber aspect_section "
                         "(start, ende) fehlt.")
        else:
            start_m, end_m = aspect_section
            ms = _find_marker(start_m, whole)
            if ms is None:
                fails.append(f"ASPEKTE: Abschnittsmarker {start_m!r} nicht gefunden.")
            else:
                me = _find_marker(end_m, whole, ms.end()) if end_m else None
                seg = whole[ms.end():me.start()] if me else whole[ms.end():]
                found_rows = len(re.findall(r"\d{1,3}\s*°\s*\d{1,2}\s*[′']", seg))
                if found_rows != aspect_rows:
                    fails.append(f"ASPEKTTABELLE: {found_rows} Orb-Einträge "
                                 f"gefunden, {aspect_rows} erwartet — Tabelle "
                                 "unvollständig/abgeschnitten?")

    ratio, first_prose = None, None
    if prose_start:
        needle = _dehyph(_nrm(prose_start))
        first_prose = next((pi for pi, pt in enumerate(pages_n)
                            if needle in _dehyph(pt)), None)
        if first_prose is None:
            fails.append(f"PROSA-START {prose_start!r} nicht gefunden.")
    if first_prose is not None:
        prose_chars = 0
        for pi in range(first_prose, len(pages)):
            plines = [l for l in (x.rstrip() for x in pages[pi].splitlines())
                      if l.strip()]
            is_last = (pi == len(pages) - 1)
            if plines and re.fullmatch(r'\s*\d{1,3}\s*', plines[-1]):
                plines = plines[:-1]                 # Fußzeile (Seitenzahl)
            if plines:
                plines = plines[1:]                  # Kopfzeile (Kolumnentitel)
            if not plines:
                if not is_last:
                    fails.append(f"SEITE {pi + 1}: leer (nur Kopf/Fuß).")
                continue
            prose_chars += sum(len(_nrm(l)) for l in plines)
            if not is_last and len(plines) < min_lines:
                warns.append(f"SEITE {pi + 1}: nur {len(plines)} Textzeilen — "
                             "auffällig leer?")
            tail = plines[-1].strip()
            show = tail[-50:]
            while tail and tail[-1] in _CLOSERS:
                tail = tail[:-1].rstrip()
            lc = tail[-1] if tail else ""
            if lc in ":;":
                fails.append(f"SEITE {pi + 1} endet mit '{lc}' — "
                             f"Doppelpunkt-Bindung verletzt: {show!r}")
            elif lc == "-":
                fails.append(f"SEITE {pi + 1} endet im getrennten Wort: {show!r}")
            elif lc not in ".!?…":
                fails.append(f"SEITE {pi + 1} endet mitten im Satz: {show!r}")
        if source_text_chars:
            ratio = prose_chars / source_text_chars
            if ratio < min_coverage:
                fails.append(f"TEXTDECKUNG nur {ratio:.1%} (< {min_coverage:.0%}) "
                             "— Absätze im Render verloren?")

    if _PLACEHOLDER_RE.search(whole):
        fails.append("PLATZHALTER im PDF-Text ({{...}}/TODO/FIXME/???).")

    sample_png = None
    if sample_page and 1 <= int(sample_page) <= n_pages:
        prefix = os.path.splitext(pdf_path)[0] + "_sample"
        d = os.path.dirname(prefix) or "."
        for f in os.listdir(d):
            if f.startswith(os.path.basename(prefix)) and f.endswith(".png"):
                os.remove(os.path.join(d, f))
        subprocess.run(["pdftoppm", "-png", "-f", str(sample_page),
                        "-l", str(sample_page), "-r", str(sample_dpi),
                        pdf_path, prefix], check=True)
        cand = sorted(f for f in os.listdir(d)
                      if f.startswith(os.path.basename(prefix))
                      and f.endswith(".png"))
        if cand:
            sample_png = os.path.join(d, cand[0])

    report = {"pdf": pdf_path, "pages": n_pages, "marker_pages": marker_pages,
              "aspect_rows_found": found_rows, "coverage": ratio,
              "warnings": warns, "failures": fails, "sample_png": sample_png}
    if verbose:
        ok = "FEHLGESCHLAGEN" if fails else "OK"
        asp = f", Aspekte {found_rows}/{aspect_rows}" if aspect_rows is not None else ""
        cov = f", Deckung {ratio:.1%}" if ratio is not None else ""
        print(f"verify {os.path.basename(pdf_path)}: {ok} — {n_pages} Seiten, "
              f"{len(marker_pages)}/{len(markers or [])} Marker{asp}{cov}, "
              f"{len(warns)} Warnung(en).")
        for w in warns:
            print(f"  ! {w}")
    if fails:
        raise VerifyError(
            f"PDF-Prüfung fehlgeschlagen ({len(fails)} Befund(e)):\n"
            + "\n".join(f"  [{i + 1}] {f}" for i, f in enumerate(fails))
            + ("\nWarnungen:\n" + "\n".join(f"  - {w}" for w in warns)
               if warns else ""))
    return report


# ---------------------------------------------------------------------------
# Visuelle Prüfung — nur noch STICHPROBE (verify() ist die eigentliche
# Prüfung; hierher nur für gezielten Blick auf einzelne Seiten)
# ---------------------------------------------------------------------------

def verify_visual(pdf_path: str, pages=None, dpi: int = 80,
                  out_prefix: str = None) -> list:
    """Rastert Seiten via pdftoppm zu PNGs für einen gezielten Blick.
    pages=None rastert ALLE Seiten (teuer — nur wenn wirklich nötig);
    pages=[1,3] nur diese. Die inhaltliche Prüfung macht verify()."""
    pdf_path = os.path.abspath(pdf_path)
    if out_prefix is None:
        out_prefix = os.path.join(
            os.path.dirname(pdf_path),
            os.path.splitext(os.path.basename(pdf_path))[0] + "_check",
        )
    produced_dir = os.path.dirname(out_prefix) or "."
    prefix_base = os.path.basename(out_prefix)

    if pages is None:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf_path,
                        out_prefix], check=True)
        return sorted(
            os.path.join(produced_dir, f)
            for f in os.listdir(produced_dir)
            if f.startswith(prefix_base) and f.endswith(".png")
        )

    paths = []
    for p in pages:
        subprocess.run(["pdftoppm", "-png", "-f", str(p), "-l", str(p),
                        "-r", str(dpi), pdf_path, out_prefix], check=True)
        pat = re.compile(rf"^{re.escape(prefix_base)}-0*{int(p)}\.png$")
        for f in os.listdir(produced_dir):
            if pat.match(f):
                paths.append(os.path.join(produced_dir, f))
    return sorted(set(paths))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_fonts(force="--force" in sys.argv)
    else:
        print(__doc__)
