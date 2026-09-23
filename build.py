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

/* HÄRTUNG (layoutneutral): Listenpunkte nie ueber die Seitenkante gerissen
   (Listen laufen nicht durch den Satz-Schutz von render_sentence_safe, darum
   hier per CSS gesichert).

   ACHTUNG, korrigiert 2026-09-09: Hier stand die Zusicherung „Zwischentitel nie
   allein am Seitenfuss". Sie traf nicht zu. **WeasyPrint setzt
   `break-after: avoid` nicht um** — die Deklaration bleibt stehen, weil sie
   nach Spezifikation richtig ist und in einer kuenftigen Fassung greifen kann,
   aber sie traegt heute nichts. Im Pruefdokument vom 09.09. stand ein
   Zwischentitel allein am Seitenfuss, und `verify()` meldete ihn korrekt als
   „endet mitten im Satz" — an einer Stelle, die kein Modul erklaerte.
   Die Bindung leistet `chartdoc.build_bloecke()`: Zwischentitel und
   Folgeabsatz in einem `.subwrap`-Block mit `break-inside: avoid`, der
   einzigen Umbruchsperre, die WeasyPrint tatsaechlich umsetzt. */
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
# Abgeleitet, nicht im Block geschrieben: der Erklaerteil hinter den
# Symbolen der GLYPHEN-Zeile (s. lies_deckblatt).
DECKBLATT_ABGELEITET = ('GLYPHEN_GRUND',)

_DB_START_RE = re.compile(r'^@@DECKBLATT\s*$')
_DB_ENDE_RE = re.compile(r'^@@ENDE\s*$')
# ERGAENZT 14.09.2026 (Pruefbericht EA Schritt 1+2, 1.7): Der Unterstrich
# fehlte in der Zeichenklasse, weshalb eine eigene `GLYPHEN_GRUND:`-Zeile gar
# nicht als Feld erkannt wurde und sich stumm an den GLYPHEN-Wert anhaengte
# (heraus kam '♇ ♂ ☊ ☋ GLYPHEN_').
_DB_FELD_RE = re.compile(r'^([A-ZÄÖÜ][A-ZÄÖÜ_]{3,24})\s*:\s*(.*)$')
# 2026-09-19 (W14, Frage 3 = Option 1): KICKER und UNTERTITEL sind gestrichen.
# Sie werden in jeder Schreibweise als unbekanntes Feld erkannt und gemeldet,
# damit eine Zeile „Untertitel: …" nicht still im Wert davor landet.
DECKBLATT_GESTRICHEN = ('KICKER', 'UNTERTITEL')
_DB_GESTRICHEN_RE = re.compile(r'^(KICKER|UNTERTITEL)\s*:\s*(.*)$', re.I)


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

    Eine Zeile `FELD:` mit einem Feld, das der Block nicht kennt (etwa
    `KICKER:` oder `UNTERTITEL:`), wird seit 2026-09-19 (W14) NICHT mehr still
    an das vorige Feld gehaengt: Sie wird samt ihren Folgezeilen verworfen und
    laut gemeldet (Zeile „!! @@DECKBLATT …“ auf stdout, kein Abbruch).
    KICKER und UNTERTITEL gibt es nicht (Chris-Entscheidung 2026-09-19): Die
    Kickerzeile des Covers traegt den Dokumenttyp aus der H1 der analyse.md,
    einen Untertitel hat das Cover nicht.

    Rueckgabe: {'LEITSATZ':…, 'LEITACHSE':…, 'TITELMOTIV':…,
                'PALETTE':… , 'GLYPHEN':…, 'GLYPHEN_GRUND':…} — die letzten
    drei ggf. ''. GLYPHEN traegt NUR die Symbole (genau das, was als Ornament
    gedruckt wird); eine Begruendung hinter den Symbolen wandert nach
    GLYPHEN_GRUND und gehoert in kein Dokument.
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

    felder, key, unbekannt = {}, None, []
    for z in zeilen[start:]:
        if _DB_ENDE_RE.match(z):
            break
        m = _DB_FELD_RE.match(z) or _DB_GESTRICHEN_RE.match(z)
        if m and m.group(1) in DECKBLATT_FELDER + DECKBLATT_ABGELEITET:
            key = m.group(1)
            felder[key] = m.group(2).strip()
        elif m:
            # 2026-09-19 (W14): unbekanntes Feld nicht an das vorige haengen —
            # vorher landete eine KICKER-Zeile still im Wert davor.
            unbekannt.append(m.group(1))
            key = None
        elif key and z.strip():
            felder[key] = (felder[key] + ' ' + z.strip()).strip()
    for feld in unbekannt:
        if feld.upper() in DECKBLATT_GESTRICHEN:
            grund = ('KICKER und UNTERTITEL sind seit 2026-09-19 kein Feld des '
                     'Blocks: Die Kickerzeile des Covers traegt den Dokumenttyp '
                     'aus der H1 der analyse.md, einen Untertitel hat das Cover '
                     'nicht. Die Zeile kann aus dem Block gestrichen werden.')
        else:
            grund = ('Tippfehler? Erlaubt sind '
                     + ', '.join(DECKBLATT_FELDER + DECKBLATT_ABGELEITET) + '.')
        print(f'  !! @@DECKBLATT in {os.path.basename(pfad)}: unbekanntes Feld '
              f'"{feld}:" — die Zeile und ihre Folgezeilen werden NICHT '
              f'uebernommen und nicht an das vorige Feld gehaengt. {grund}')

    fehlt = [k for k in DECKBLATT_PFLICHT if not felder.get(k)]
    if fehlt:
        raise DeckblattError(
            f'@@DECKBLATT-Block in {os.path.basename(pfad)} unvollstaendig — '
            f'leer oder fehlend: {", ".join(fehlt)}. '
            f'Pflicht sind {", ".join(DECKBLATT_PFLICHT)}.')
    for k in ('PALETTE', 'GLYPHEN'):
        felder.setdefault(k, '')
    # GLYPHEN traegt haeufig eine Begruendung hinter den Symbolen
    # („♅ ⚷ ♃ ♐ — Uranus und Chiron als Gegenpaar …"). Als Ornament darf nur
    # die Symbolzeile in Dokument und Inhaltsverzeichnis; ungefiltert druckte
    # sich der ganze Erklaersatz quer ueber die Seite (Befund 2026-09-06).
    # GLYPHEN traegt darum nur noch die Symbole, GLYPHEN_GRUND den Rest.
    glyph, grund = _glyphen_trennen(felder['GLYPHEN'])
    felder['GLYPHEN'] = glyph
    # Eine ausdrueckliche GLYPHEN_GRUND-Zeile schlaegt die abgeleitete
    # Trennung, wird aber von ihr ergaenzt (14.09.2026, s. o.).
    felder['GLYPHEN_GRUND'] = grund or felder.get('GLYPHEN_GRUND', '')
    return {k: felder[k] for k in DECKBLATT_FELDER + DECKBLATT_ABGELEITET}


_GLYPH_TRENNER_RE = re.compile(r'\s+[—–-]\s+|\s*\((?=[A-ZÄÖÜa-zäöü])')


def _glyphen_trennen(wert: str):
    """GLYPHEN-Feld in Symbolzeile und Begruendung teilen.

    Getrennt wird am ersten Gedankenstrich mit Leerzeichen drumherum oder an
    der ersten oeffnenden Klammer. Steht kein Trenner drin, ist das ganze Feld
    die Symbolzeile und die Begruendung leer. Zusaetzlich wird alles nach dem
    letzten Symbolzeichen abgeschnitten, damit auch ein Feld ohne Trenner
    („♅ ⚷ ♃ ♐ Uranus und Chiron …") sauber bleibt.
    """
    wert = (wert or '').strip()
    if not wert:
        return '', ''
    teil = _GLYPH_TRENNER_RE.split(wert, maxsplit=1)
    kopf = teil[0].strip()
    rest = wert[len(kopf):].lstrip(' —–-(').strip() if len(teil) > 1 else ''
    # Zweite Sicherung: hinter dem letzten Symbol abschneiden.
    treffer = list(re.finditer(r'[^\sA-Za-zÄÖÜäöüß.,;:0-9()\[\]/]', kopf))
    if treffer:
        ende = treffer[-1].end()
        wort = kopf[ende:].strip()
        if wort:
            rest = (wort + (' ' + rest if rest else '')).strip()
            kopf = kopf[:ende].strip()
    return kopf, rest.rstrip(')').strip()


ANALYSE_SCHEMA = """\
STRUKTUR-SCHEMA für <klient>_analyse.md (v1). Schritt 2 SCHREIBT genau so,
parse_analyse() LIEST genau so — jede Abweichung ist ein harter SchemaError
mit Zeilennummer, kein stilles Fehlrendern.

    # <Dokumenttyp> — <Vorname Nachname>
        Genau EINE H1 als erste inhaltliche Zeile. Rechts vom " — " der
        Klientenname (Identitäts-Guardrail: Name explizit am Dateianfang).
        Beispiel: "# Geburtshoroskop — Alex Muster"

    <Untertitelzeile>
        OPTIONAL, genau EINE einzeilige Zeile direkt unter der H1 und vor der
        ersten H2 (Modus, Stand, Fassung). Landet in parsed['untertitel'] und
        zählt nicht als Absatz. Jede weitere Zeile vor der ersten H2 bleibt ein
        harter Fehler.

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
    Zerreiß-Artefakt aus PDF-Rekonstruktionen.
    AUSNAHME (seit 2026-09-06): Ein Absatz DARF auf einer Ordinalzahl enden,
    wenn ein Bezugswort davorsteht — "… steht in Kapitel 10.", "… in den
    Häusern 3 und 9.". Das ist der Querverweis, den die Ordnungs-Probe der
    Inneren Arbeit (Prinzip 10) ausdrücklich verlangt; er wird am Bezugswort
    erkannt (_ORD_REF_WORDS) und durchgelassen. Ohne Bezugswort bleibt es ein
    Fehler
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

# Ein Absatz, der auf einer Ordinalzahl endet, ist normalerweise ein
# Zerreiss-Artefakt aus einer PDF-Rekonstruktion („… ins 3." — abgerissen von
# „3. Haus"). Es gibt aber einen legitimen Fall, und er ist im Standardlauf
# sogar VORGESCHRIEBEN: Die Ordnungs-Probe der Inneren Arbeit (Prinzip 10)
# verlangt, dass ein Kapitel, das die Rueckseite eines frueheren behandelt,
# dieses ausdruecklich beim Namen nennt — und das natuerliche Satzende eines
# solchen Querverweises IST die Kapitelnummer („… steht in Kapitel 2 und
# Kapitel 10.").
#
# Bis 2026-09-06 brach parse_analyse an genau diesen Saetzen ab. Der Ausweg
# im Prueflauf war, den Verweis unschaerfer zu formulieren („im Kapitel ueber
# dein Auftreten") — also eine Regel zu verletzen, um eine andere zu
# erfuellen. Seither wird der Verweis am Bezugswort erkannt und
# durchgelassen. Ein echtes Artefakt hat kein Bezugswort vor der Zahl.
_ORD_REF_WORDS = (r'Kapiteln?|Haus|H(?:ae|ä)user[n]?|Teile?[nrs]?|'
                  r'Abschnitte?[ns]?|Punkte?[ns]?|Prinzip(?:ien)?|'
                  r'Bewegung(?:en)?|Schritte?[ns]?|R(?:ang|aenge|änge)|'
                  r'Seiten?|Nr\.?|Nummer|Themen?|Quartale?[ns]?|Stufen?|'
                  r'Regeln?|Segmente?[ns]?|Anhang|Tabellen?|Zeilen?|'
                  r'Abs(?:atz|aetze|ätze)|S(?:atz|aetze|ätze)|Fragen?|'
                  r'(?:Ue|Ü)bung(?:en)?|Aufgaben?|Fu(?:ss|ß)noten?|'
                  r'B(?:and|aende|ände)|'
                  # 2026-09-22 (W57-Nachzug): die englischen Bezugswoerter. Bis
                  # heute war ein Absatzende „… in Chapter 2." ein SchemaError,
                  # und die englische Fassung musste den Verweis umschreiben
                  # („named in Chapter 2 as a co-carrier." statt „Sounds in
                  # Chapter 2.") — eine Regel verletzt, um eine andere zu
                  # erfuellen, genau der Fall, den dieser Block verhindern soll.
                  r'Chapters?|Houses?|Parts?|Sections?|Points?|Principles?|'
                  r'Movements?|Steps?|Ranks?|Pages?|No\.?|Number|Themes?|'
                  r'Quarters?|Stages?|Rules?|Segments?|Appendix|Tables?|'
                  r'Lines?|Paragraphs?|Sentences?|Questions?|Exercises?|'
                  r'Tasks?|Footnotes?|Volumes?|Chart')
# a) Bezugswort unmittelbar vor der Zahl: „… in Kapitel 10."
_ORD_REF_DIREKT_RE = re.compile(
    r'(?:^|[\s(„"»])(?:' + _ORD_REF_WORDS + r')\s+\d{1,2}\.$')
# b) Bezugswort vor einer Zahlenkette: „… in den Kapiteln 2, 7 und 10."
# 2026-09-22: die englischen Bindewoerter dazu („Chapters 2 and 6."), sonst
# faellt die Kette durch, waehrend der Einzelverweis laeuft.
_ORD_REF_KETTE_RE = re.compile(
    r'(?:^|[\s(„"»])(?:' + _ORD_REF_WORDS + r')\s+'
    r'(?:\d{1,2}\s*(?:,|und|oder|bis|and|or|to|through|/|–|-)\s*)+\d{1,2}\.$')


def _ist_kapitelverweis(tail: str) -> bool:
    """Endet der Absatz auf einem BENANNTEN Verweis statt auf einem
    abgerissenen Satz? Nur dann ist die Ordinalzahl am Absatzende zulaessig."""
    return bool(_ORD_REF_DIREKT_RE.search(tail)
                or _ORD_REF_KETTE_RE.search(tail))
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


def _analyse_quelle(quelle):
    """Text und Anzeigename der analyse.md — aus einem Pfad ODER dem Text selbst.

    Neu 2026-09-19 (W61): Wer den Text übergab, bekam `OSError [Errno 36] File
    name too long` samt dem ganzen Text als Dateinamen. Text ist ein str mit
    Zeilenumbruch oder einer, der mit '# ' beginnt (die H1); alles andere ist
    ein Pfad. Keine Meldung enthält den ganzen Text."""
    if isinstance(quelle, os.PathLike):
        pfad = os.fspath(quelle)
    elif isinstance(quelle, str):
        if "\n" in quelle or quelle.lstrip("\ufeff \t").startswith("# "):
            return quelle, "analyse.md (als Text übergeben)"
        pfad = quelle
    else:
        raise TypeError(
            "parse_analyse(): erwartet wird der Pfad der <klient>_analyse.md "
            "(str oder Path) ODER ihr Text als str, bekommen: "
            f"{type(quelle).__name__}.")
    if not os.path.isfile(pfad):
        kurz = pfad if len(pfad) <= 120 else pfad[:117] + "…"
        raise FileNotFoundError(
            f"parse_analyse(): Datei nicht gefunden: {kurz!r}. Erwartet wird "
            "der Pfad der <klient>_analyse.md ODER ihr Text als str "
            "(mehrzeilig bzw. mit der H1 '# <Dokumenttyp> — <Klientenname>' "
            "am Anfang).")
    with open(pfad, encoding="utf-8") as f:
        return f.read(), os.path.basename(pfad)


def parse_analyse(path, client: str = None) -> dict:
    """Liest <klient>_analyse.md strikt nach ANALYSE_SCHEMA.

    path: Pfad der analyse.md (str oder Path) ODER ihr Text als str — seit
    2026-09-19 (W61). Als Text gilt ein str mit Zeilenumbruch oder mit '# '
    am Anfang; sonst ist es ein Pfad, und eine fehlende Datei meldet
    FileNotFoundError mit dem, was erwartet ist.

    client: erwarteter Klientenname; weicht die H1 ab, ist das ein Fehler
    (Identitäts-Guardrail gegen Datei-Verwechslung).

    Rückgabe: {'h1','doctype','client','untertitel','chapters':[{'kicker',
    'title','line','blocks':[{'type':'p'|'li'|'subhead','text','line'},...]},...]}
    'untertitel' ist die EINE Untertitelzeile unter der H1 (ANALYSE_SCHEMA) oder
    None, wenn keine dasteht — seit 2026-09-21 hier genannt, vorher fehlte sie
    in dieser Liste und stand nur im Werkzeuge- und im Design-Render-Modul.
    Wirft SchemaError mit ALLEN Funden (Zeilennummer + Erwartung)."""
    raw, quelle_name = _analyse_quelle(path)
    raw = raw.replace("\r\n", "\n").replace("\r", "\n")
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
    untertitel = None
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
                # ADDITIV seit 2026-09-06 (Prüfbericht EA 1.12): GENAU EINE
                # Zeile zwischen H1 und der ersten H2 ist zulässig — die
                # Untertitelzeile (Modus, Stand, Fassung). Datierte Dokumente
                # (EA-Jetzt-Teil, Transit) brauchen sie; vorher brach der Lauf
                # dort mit "Text vor dem ersten Kapitel" ab, ohne dass das
                # Schema die Zeile irgendwo verboten hätte.
                if untertitel is None and h1 is not None and "\n" not in text:
                    untertitel = text.strip()
                    continue
                err(ln, "Text vor dem ersten Kapitel (##). Zulässig ist dort "
                        "genau EINE einzeilige Untertitelzeile direkt unter "
                        "der H1.")
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
                if _ORD_END_RE.search(tail) and not _ist_kapitelverweis(tail):
                    err(b["line"], f"Absatz endet auf Ordinalzahl ({tail[-25:]!r}) — "
                                   "zerrissener Absatz (PDF-Artefakt)? Mit Folgeabsatz "
                                   "zusammenführen. Ein BENANNTER Verweis "
                                   "(„… in Kapitel 10.\u201c, „… in den Häusern 3 und 9.\u201c) "
                                   "ist dagegen zulässig und wird durchgelassen — "
                                   "das Bezugswort vor der Zahl ist die Bedingung.")
            else:
                err(b["line"], f"Absatz endet mitten im Satz ({tail[-40:]!r}).")

    if errors:
        errors.sort()
        listing = "\n".join(f"  Zeile {ln}: {m}" for ln, m in errors)
        raise SchemaError(
            f"{quelle_name} verletzt das analyse.md-Schema "
            f"({len(errors)} Fund(e)):\n{listing}\n"
            f"Schema: build.ANALYSE_SCHEMA. Quelle korrigieren statt rendern.")
    return {"h1": h1, "doctype": doctype, "client": client_name,
            "untertitel": untertitel, "chapters": chapters}


def chapter_markers(parsed: dict, nur_titel: bool = False) -> list:
    """(Kicker, Titel) je Kapitel in Dokumentreihenfolge — direkt für
    verify(markers=...).

    Seit dem 2026-09-17 Tupel statt nackter Titel (Klasse-2-Entscheidungslauf,
    Wiederholungstäter aus zwei Laufabschnitten): `verify()` nahm die ERSTE
    Fundstelle eines Titels im PDF-Text. Ein Titel, der vorher in der Prosa
    vorkommt oder Präfix eines anderen ist („The way up" / „The way up into
    Taurus"), wurde damit auf der falschen Seite gefunden, und die
    Reihenfolgeprobe blieb grün. Mit dem Kicker daneben nagelt `verify()` die
    Fundstelle auf die Überschrift fest: Titel allein auf eigener Zeile,
    Kicker direkt darüber (seit 2026-09-19, W47 — vorher genügte eine Seite,
    die den Kicker irgendwo trug, auch in einem Querverweis).

    `nur_titel=True` gibt die alte Form zurück — für Aufrufer, die die Liste
    ausgeben statt sie an `verify()` zu übergeben."""
    if nur_titel:
        return [ch["title"] for ch in parsed["chapters"]]
    return [(ch.get("kicker"), ch["title"]) for ch in parsed["chapters"]]


def prepare_chapters(parsed: dict) -> list:
    """Dekoriert parse_analyse()-Kapitel für den satzsicheren Builder:
    p-Blöcke bekommen 'sent' (split_sentences), 'colon_end' und 'next_p' —
    exakt die Struktur, die der Referenz-Builder erwartet.
    Rueckgabe: NEUE Liste von Kapitel-dicts {'kicker', 'title', 'signatur',
    'beleg', 'blocks': [{'type', 'text', …, bei 'p' zusaetzlich 'sent',
    'colon_end', 'next_p'}]} — das `items` der Chart-Builder; `parsed` bleibt
    unveraendert."""
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
                 ("Die Zeitleiste", "Zeitleisten-Seite am Ende von Teil III"),
                 ("Die langen Linien im Überblick", "Anhang: volle Transit-Tabelle"),
                 ("Der Stichtag im Überblick", "Anhang: Jetzt-Tabelle")],
        "html": [("_transituhr.png", "Transit-Uhr-Grafik (transituhr.py)")],
    },
    # Eigenstaendiges Transit-Horoskop. Bis zum 2026-09-05 GAR NICHT
    # hinterlegt: `doctype='transit'` fiel als unbekannter Typ auf die
    # Chart-Basis zurueck, und damit waren Transit-Uhr und Anhang in einem
    # Transit-PDF ueberhaupt nicht erzwungen — obwohl das Transit-Modul beide
    # ausdruecklich verlangt („nie weglassen"). Die Zeitleiste kommt mit dem
    # Teil-III-Umbau vom 2026-09-03 dazu; sie ersetzt die acht
    # Quartalskapitel und ist die einzige Navigationsebene, die davon
    # uebrigbleibt. Der Titel wird zur Laufzeit aus chartdoc.ZEITLEISTE_TITEL
    # nachgezogen (chartdoc._pflicht_baustein_angleichen), genau wie der
    # Aspektseiten-Titel — hier steht nur der Vorgabewert.
    "transit": {
        "text": [("Die Transit-Uhr", "Transit-Uhr auf der Chartbild-Strecke"),
                 ("Die Zeitleiste",
                  "Zeitleisten-Seite hinter den Themenkapiteln"),
                 ("Die langen Linien im Überblick", "Anhang: volle Transit-Tabelle"),
                 ("Der Stichtag im Überblick", "Anhang: Jetzt-Tabelle")],
        "html": [("_transituhr.png",
                  "Transit-Uhr-Grafik (transituhr_fusion.py)")],
    },
    # EA und das Standard-Geburtshoroskop (doctype=None) haben KEINE
    # Zeitleiste — sie tragen kein Quartalsraster. Der EA-Eintrag steht
    # trotzdem hier, damit die Pruefung typabhaengig LESBAR ist und ein
    # EA-Lauf nicht als „unbekannter Typ" gewarnt wird.
    "ea": {
        "text": [],
        "html": [],
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


# Gleichwertige Titel der beiden Sprachfassungen. Gepflegt wird die Zuordnung
# in chartdoc (_LABELS und _PFLICHT_PAARE) — hier steht nur, was verify() ohne
# chartdoc kennen muss, damit ein englisches PDF nicht an einer deutschen
# Erwartung scheitert und umgekehrt.
PFLICHT_GLEICHWERTIG = (
    ('Inhalt', 'Contents'),
    ('Die Aspekte im Wortlaut', 'The Aspects in Detail'),
    ('Die Aspekte im Einzelnen', 'The Aspects in Detail'),
    ('Die Aspekte und was sie bedeuten', 'The Aspects and What They Mean'),
    ('Die Transit-Uhr', 'The Transit Clock'),
    ('Die Zeitleiste', 'The Timeline'),
    ('Die langen Linien im Überblick', 'The Long Lines at a Glance'),
    ('Der Stichtag im Überblick', 'The Reference Date at a Glance'),
    ('Die tragenden Konstellationen', 'The Constellations That Carry Them'),
    ('Die Zeitfenster im Überblick', 'The Time Windows at a Glance'),
)


def _pflicht_kandidaten(needle):
    """Der Titel selbst und sein gleichwertiger Titel der anderen Sprache."""
    out = [needle]
    for paar in PFLICHT_GLEICHWERTIG:
        if needle in paar:
            out.extend(x for x in paar if x != needle)
    return tuple(dict.fromkeys(out))


def pflicht_bausteine(doctype=None) -> dict:
    """Pflichtliste fuer einen Dokumenttyp.

    Standardfall: die '*'-Chart-Basis PLUS die typ-eigenen Eintraege.
    Setzt ein Typ "basis": False, gilt AUSSCHLIESSLICH seine eigene Liste —
    fuer Begleitdokumente, die kein Geburtsbild abbilden. Unbekannte Typen
    liefern die Chart-Basis; ein Tippfehler im doctype schwaecht den Guardrail
    also nicht ab, sondern faellt auf die strengere Liste zurueck.

    Der Rueckfall ist aber NICHT harmlos, wenn der Typ echt ist und nur nicht
    hinterlegt: `doctype='transit'` lief bis zum 2026-09-05 genau so — still,
    ohne Transit-Uhr- und Anhang-Pflicht. Ein nicht hinterlegter, nicht leerer
    doctype wird darum jetzt laut gemeldet.
    """
    basis = PFLICHT_BAUSTEINE["*"]
    key = (doctype or "").strip().lower()
    extra = PFLICHT_BAUSTEINE.get(key)
    if extra is None:
        if key:
            bekannt = ", ".join(sorted(k for k in PFLICHT_BAUSTEINE
                                       if k != "*"))
            print(f"  !! doctype={doctype!r} ist in PFLICHT_BAUSTEINE nicht "
                  f"hinterlegt — es gilt nur die Chart-Basis, die typ-eigenen "
                  f"Pflichtseiten werden NICHT geprueft. Tippfehler, oder "
                  f"fehlt der Typ? Bekannt: {bekannt}.")
        extra = {"text": [], "html": []}
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
        # 2026-09-22 (W57-Nachzug): chartdoc.setze_sprache() zieht die Titel hier
        # nach, bevor verify() laeuft. Der Fall, den diese Zeile trotzdem
        # abfaengt: ein Lauf, der die Sprache erst NACH dem Seitenaufbau
        # umstellt oder ein Titel aus einer Liste, die die Angleichung nicht
        # kennt. Dann gilt auch der gleichwertige Titel der anderen Sprache —
        # ein fehlender Baustein bleibt ein Befund, nur eine gemischte
        # Sprachfassung faellt nicht mehr durch.
        if not any(re.sub(r'\s+', ' ', kand).strip() in hay
                   for kand in _pflicht_kandidaten(needle)):
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


def _kopf_schluessel(s: str) -> str:
    """Vergleichsform fuer Kapitelkoepfe (neu 2026-09-19, W47): nur Buchstaben
    und Ziffern, klein geschrieben. Sperrung ('K A P I T E L 2'),
    Zeilenumbruch, Trenn- und Bindestrich, Anfuehrungszeichen und
    Glyphen-Varianten (U+FE0E) fallen weg."""
    return re.sub(r"[\W_]+", "", _nrm(s or "")).casefold()


def _kopf_finden(seiten_zeilen, kick, titel, ab=(0, -1), max_zeilen=4):
    """(Seite, letzte Titelzeile) der ersten Kapitelueberschrift `titel` hinter
    der Position `ab` — oder None. Neu 2026-09-19 (W47).

    Ueberschrift heisst: Der Titel fuellt eine bis `max_zeilen` GANZE Zeilen
    allein, und — wenn ein Kicker mitgegeben ist — die Zeile (oder die zwei
    Zeilen) direkt darueber sind genau der Kicker. Ein Querverweis im
    Fliesstext („… in Kapitel 2, ‚Titel‘, …") erfuellt das nicht: Seine
    Zeile traegt anderen Text, und ueber ihr steht kein Kicker. Vorher
    genuegte die erste Fundstelle auf einer Seite, die den Kicker IRGENDWO
    trug — ein Querverweis „Kapitel 2 … Titel" nannte beides."""
    t_key = _kopf_schluessel(titel)
    k_key = _kopf_schluessel(kick) if kick else ""
    if not t_key:
        return None
    s0, z0 = ab
    for s in range(max(0, s0), len(seiten_zeilen)):
        keys = [_kopf_schluessel(z) for z in seiten_zeilen[s]]
        for i in range(z0 + 1 if s == s0 else 0, len(keys)):
            if not keys[i] or not t_key.startswith(keys[i]):
                continue
            acc = ""
            for j in range(i, min(i + max_zeilen, len(keys))):
                acc += keys[j]
                if acc == t_key:
                    if not k_key or any("".join(keys[max(0, i - n):i]) == k_key
                                        for n in (1, 2)):
                        return (s, j)
                    break
                if not t_key.startswith(acc):
                    break
    return None


def _pdf_pages_text(pdf_path: str) -> list:
    out = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8",
                          pdf_path, "-"], capture_output=True, check=True)
    pages = out.stdout.decode("utf-8", "replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def pdf_info(pdf_path: str) -> dict:
    """`pdfinfo` als dict — Schluessel wie pdfinfo sie druckt ('Pages', 'Page size',
    'File size' …), Werte als Strings; die Seitenzahl also int(info['Pages'])."""
    out = subprocess.run(["pdfinfo", pdf_path], capture_output=True, check=True)
    info = {}
    for line in out.stdout.decode("utf-8", "replace").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            info[k.strip()] = v.strip()
    return info


# 2026-09-22 (W57-Nachzug): Das gesperrte Gold-Label des Kapitelfusses heisst
# in einem englischen PDF „EVIDENCE:". Die ANALYSE traegt weiter `**Beleg:**`
# (Werkzeuge-Modul A3, weil parse_analyse genau dieses Wort erkennt) — hier geht
# es um die gerenderte Fusszeile, die der Anker-Suche als Kopfzeile dient.
_FUSS_LABEL_RE = re.compile(r'^\s*(?:B\s?E\s?L\s?E\s?G|E\s?V\s?I\s?D\s?E\s?N\s?C\s?E)\s?:')
_FUSS_ASPEKT_RE = re.compile(r'^\s*[–—]\s')
# Woran eine Zeile des Kapitelfusses erkennbar ist — auch als Fortsetzung
# einer umgebrochenen Beleg- oder Stand-Zeile (s. _fuss_zeilen).
_FUSS_ZEILE_RE = re.compile(
    r'^\s*[–—]\s|\d{1,3}\s*°\s*\d{1,2}\s*[′\']|\bOrb\b|·|'
    r'Konjunktion|Opposition|Quadrat|Trigon|Sextil|Quincunx|Halbsextil|'
    r'[☉☽☿♀♂♃♄♅♆♇☊☋⚷⚸⊗♈♉♊♋♌♍♎♏♐♑♒♓]')
# Eine Zeile, die NUR eine Zahl traegt, ist die Seitenzahl — nie Prosa.
_NUR_ZIFFERN_RE = re.compile(r'\s*\d{1,3}\s*')


def _fuss_typ(zeile, einzug) -> bool:
    """Traegt die Zeile ein Fuss-Merkmal, oder haengt sie als eingerueckte
    Fortsetzung an der Zeile darueber?"""
    return bool(_FUSS_ZEILE_RE.search(zeile)) \
        or (len(zeile) - len(zeile.lstrip())) > einzug


def source_text_chars(parsed) -> int:
    """Vergleichswert fuer verify(source_text_chars=…) — Summe der
    normalisierten Laengen von Kicker, Titel, Signatur, Beleg und allen
    Blocktexten der geparsten Kapitel.

    Neu am 2026-09-15 (Pruefbericht Geburtshoroskop Schritt 3+4, 5.2). Bis
    dahin war das das EINZIGE verify()-Argument ohne Hilfsfunktion: Das
    Design-Modul beschrieb die Summe in Prosa („selbst ausrechnen"), waehrend
    `markers` ueber chapter_markers(), die Fusszeilen ueber fuss_signaturen()
    und die Aspektzahl ueber radix.aspektliste() kamen. Jeder Lauf hat
    dieselbe Schleife neu geschrieben — und ein Zaehlfehler darin tarnt sich
    als „Textdeckung zu niedrig", also als Layoutfehler an einer Stelle, an
    der gar keiner ist.

    Nimmt das Ergebnis von parse_analyse() oder prepare_chapters().
    """
    kap = parsed.get('chapters', parsed) if hasattr(parsed, 'get') else parsed

    def _n(x):
        return len(re.sub(r'\s+', ' ', (x or '')).strip())

    gesamt = 0
    for it in kap:
        if not isinstance(it, dict):
            continue
        gesamt += _n(it.get('kicker')) + _n(it.get('title'))
        gesamt += _n(it.get('signatur')) + _n(it.get('beleg'))
        for b in it.get('blocks') or ():
            gesamt += _n(b.get('text'))
    return gesamt


def fuss_signaturen(parsed) -> list:
    """Alle Kapitel-Signaturen eines geparsten Dokuments.

    Fuer verify(fuss_signaturen=…): eine Signatur ist die einzige Zeile des
    Kapitelfusses, die sich nicht an ihrer Form erkennen laesst (der Beleg
    traegt das „BELEG:\"-Label und die eingerueckten „–\"-Zeilen). Ohne diese
    Liste bleibt genau ein Fall ungedeckt — ein Kapitel MIT Signatur und OHNE
    Beleg, dessen Streifen eine Seite abschliesst.
    Nimmt das Ergebnis von parse_analyse() oder prepare_chapters().
    """
    kap = parsed.get('chapters', parsed) if hasattr(parsed, 'get') else parsed
    return [it['signatur'] for it in kap
            if isinstance(it, dict) and (it.get('signatur') or '').strip()]


def _sig_anfang(plines, i, sigs, max_zeilen=6):
    """Index der ERSTEN Zeile einer Kapitel-Signatur, die auf Zeile `i` endet.

    Neu 2026-09-14 (Pruefbericht Geburtshoroskop Schritt 3+4, Rubrik 2.4). Der
    Signatur-Anker in `_fuss_zeilen()` verglich bis dahin Zeile FUER Zeile
    gegen den vollen Signaturtext. Eine Signatur, die im schmalen Streifen
    umbricht — und das ist der Normalfall, nicht die Ausnahme —, steht in
    keiner EINZELNEN Zeile und wurde damit gar nicht als Anker erkannt.
    Betroffen war genau die Kapitelart, die Signatur OHNE Beleg traegt: die
    drei Buendel-Kapitel (Hauptthemen, Konfliktfelder, Lebensaufgaben) des
    Geburtshoroskops. Dort fehlt die „BELEG:"-Kopfzeile, die den Anker sonst
    rettet, und `verify()` meldete eine regelkonforme Seite als „endet mitten
    im Satz" — mit dem Hinweis, der Fehler liege in genau dieser Funktion.
    Derselbe Fehlertyp wie die Korrektur vom selben Tag an der umgebrochenen
    BELEG-Kopfzeile, eine Stufe weiter.

    Die Zusammensetzung oeffnet keine Luecke: Zurueckgegeben wird nur, wenn
    der zusammengefuegte Text EXAKT einer bekannten Signatur entspricht.
    Rueckgabe: Startindex oder None.
    """
    for k in range(max_zeilen):
        s = i - k
        if s < 0:
            break
        if _dehyph(_nrm(' '.join(plines[s:i + 1]))) in sigs:
            return s
    return None


def _fuss_zeilen(plines, sig_set) -> int:
    """Wie viele Zeilen am Seitenende gehoeren zu einem Kapitelfuss?

    Gesucht wird ZUERST der Anker — die „BELEG:\"-Kopfzeile oder eine bekannte
    Signatur —, danach wird geprueft, ob alles UNTER ihm beleg-typisch ist
    (fuehrender Gedankenstrich, Gradminute, „Orb\", ein Aspektname, der
    Segmenttrenner „·\" oder ein Faktor-/Zeichenglyph). Nur dann wird
    abgezogen. Eine Prosazeile kann die Satzende-Probe damit nicht umgehen:
    ohne Anker gibt es keinen Abzug, und steht hinter dem Fuss noch Prosa auf
    derselben Seite, faellt sie durch die Typ-Probe.

    Korrektur 2026-09-06 (Prueflauf Geburtshoroskop): Die frueherer Fassung
    lief von unten und brach an der ersten Zeile ab, die nicht mit „–\"
    beginnt. Der Streifen ist aber schmal gesetzt und im Zweispalter erst
    recht — Beleg-Eintraege UND die mehrzeilige Stand-Kopfzeile brechen
    regelmaessig um. Damit riss die Kette bei praktisch jedem Chart, und
    verify() meldete Kapitelfuesse als Satzabbruch.

    Korrektur 2026-09-14 (Prueflauf EA Schritt 3+4, Rubrik 2 und 5.3): Die
    Korrektur von 2026-09-06 deckte die umgebrochene BELEG-Kopfzeile nur ab,
    solange ihre Fortsetzung zufaellig einen Typ-Marker trug (Gradminute,
    „Orb\", Aspektname, Glyphe, „·\"). Eine Fortsetzung aus reinem Text —
    gemessen an einer umgebrochenen Stand-Kopfzeile, deren zweite Zeile nur
    aus Wortmaterial und einer Anzahl bestand — traegt keinen davon, hat
    denselben Einzug wie das Label und liess die Probe reissen; verify()
    meldete eine
    regelkonforme Seite als Satzabbruch, und zwar mit dem Hinweis, der Fehler
    liege in genau dieser Funktion. Die ERSTE Zeile unter dem Label gehoert
    definitionsgemaess zur Kopfzeile und zaehlt jetzt unbedingt als
    Fortsetzung. Das oeffnet keine Luecke: Prosa steht nie unmittelbar unter
    einer BELEG-Kopfzeile, und alle weiteren Zeilen laufen unveraendert durch
    die Typ- und Einzugsprobe. Die Ausnahme gilt NUR fuer den Label-Anker,
    nicht fuer den Signatur-Anker.
    """
    n = len(plines)
    if not n:
        return 0
    sigs = {_dehyph(s) for s in (sig_set or ())}
    for i in range(n - 1, max(-1, n - 30), -1):
        zeile = plines[i]
        ist_label = bool(_FUSS_LABEL_RE.match(zeile))
        # Der Signatur-Anker wird MEHRZEILIG gesucht (s. _sig_anfang):
        # eine umgebrochene Signatur steht in keiner einzelnen Zeile.
        sig_start = _sig_anfang(plines, i, sigs) if sigs else None
        ist_sig = sig_start is not None
        if not (ist_label or ist_sig):
            continue
        # Der Einzug wird an der ERSTEN Zeile des Ankers gemessen, nicht an
        # seiner letzten — sonst gilt die Fortsetzungszeile als Bezug.
        kopf = zeile if ist_label else plines[sig_start]
        einzug = len(kopf) - len(kopf.lstrip())
        # Die erste Zeile unter dem BELEG-Label ist die Fortsetzung seiner
        # Kopfzeile und wird nicht auf Typ oder Einzug geprueft (s. o.).
        rest = plines[i + 1:]
        if ist_label and rest:
            rest = rest[1:]
        # Eine reine Ziffernzeile ist die Seitenzahl. verify() streift sie
        # nur, wenn sie die LETZTE Zeile der Seite ist; steht darunter noch
        # etwas, blieb sie bis zum 2026-09-22 in `rest` und fiel durch die
        # Typprobe.
        while rest and _NUR_ZIFFERN_RE.fullmatch(rest[-1]):
            rest = rest[:-1]
        # Korrektur 2026-09-22 (Prueflauf Geburtshoroskop Schritt 3+4 vom
        # 2026-09-20, 1.1): Der Beleg ist EIN Absatz aus „ · "-Segmenten, der
        # im schmalen Streifen umbricht. Seine LETZTE Zeile ist der Auslauf
        # des letzten Segments und traegt deshalb regelmaessig gar kein
        # Merkmal mehr — im Struktur-Beleg des Getriebe-Kapitels etwa
        # „Aspektdichte gewichtet dicht Merkur 7, Pluto 6 — duenn Mars 0,5":
        # kein fuehrender Gedankenstrich, keine Gradminute, kein „Orb", kein
        # Aspektname, kein „·", keine Glyphe. verify() meldete die Seite
        # daraufhin als Satzabbruch, obwohl sie regelkonform mit dem Streifen
        # endet.
        # Durchgelassen wird deshalb GENAU EINE solche Zeile, und nur die
        # letzte: Ein Prosa-BLOCK hinter dem Fuss faellt weiter durch die
        # Probe, und eine einzelne Prosazeile hinter einem vollstaendigen
        # Kapitelfuss kann das Dokument nicht erzeugen — build_fuss() setzt
        # den Streifen als letztes Element des Kapitels, das naechste Kapitel
        # beginnt mit seinem Kopf auf einer neuen Seite.
        if rest and not _fuss_typ(rest[-1], einzug):
            rest = rest[:-1]
        if not all(_fuss_typ(x, einzug) for x in rest):
            continue
        start = i if ist_label else sig_start
        if ist_label and sigs:
            # Die Signatur steht direkt ueber der BELEG-Kopfzeile und bricht
            # ihrerseits um; sie wird als zusammengesetzter Text erkannt.
            for k in range(1, 7):
                if i - k < 0:
                    break
                if _dehyph(_nrm(' '.join(plines[i - k:i]))) in sigs:
                    start = i - k
                    break
        return n - start
    return 0


def verify(pdf_path: str, expected_pages=None, markers=None, kickers=None,
           aspect_rows=None, aspect_section=None, prose_start=None,
           source_text_chars=None, min_coverage=0.97, min_lines=8,
           sample_page=1, sample_dpi=80, fuss_signaturen=None,
           verbose=True) -> dict:
    """Deterministische End-Prüfung des PDFs über pdfinfo/pdftotext.
    KEINE Bildschau außer genau EINER Stichprobenseite (sample_page,
    Standard 1 = Cover; None = keine).

      expected_pages     int oder (min, max): erwartete Seitenzahl
      markers            Kapiteltitel in Reihenfolge (chapter_markers(parsed));
                         jeder muss vorkommen, Reihenfolge wird geprüft.
                         Seit 2026-09-19 (W47) nur als ÜBERSCHRIFT: Der Titel
                         steht allein auf eigener Zeile (auch umbrochen), bei
                         (Kicker, Titel) mit dem Kicker direkt darüber — ein
                         Querverweis im Fließtext zählt nicht
      kickers            Kicker-Liste; Präsenz (uppercase) wird geprüft
      aspect_rows        erwartete Zeilen der Aspekttabelle (= len(aspektliste))
      aspect_section     (start_marker, end_marker|None) grenzt den Tabellen-
                         abschnitt im Text ab; gezählt werden Orb-Einträge N°NN′
      prose_start        Marker der ersten Prosaseite. Ab dort gilt je Seite:
                         letzte Textzeile endet auf Satzende (. ! ? …), nie auf
                         : ; oder mitten im Satz/Wort — und keine Seite außer
                         der letzten ist auffällig leer (< min_lines Zeilen)
      fuss_signaturen    Liste der Kapitel-Signaturen, am einfachsten
                         build.fuss_signaturen(parsed). Seit dem 2026-09-05
                         steht der Signatur-/Beleg-Streifen am KAPITELENDE und
                         kann damit eine Seite abschließen; seine Zeilen sind
                         keine Prosa und werden für die Satzende-Probe
                         abgezogen. Ohne die Liste greift nur die
                         Formerkennung („BELEG:" plus „–"-Zeilen) — ein
                         Kapitel mit Signatur, aber ohne Beleg meldet dann
                         fälschlich „endet mitten im Satz"
      source_text_chars  Zeichenzahl der Quelle (Prosa, normalisiert):
                         Textdeckung < min_coverage => verlorene Absätze
      sample_page        genau EINE Seite als PNG rastern (Report['sample_png'])

    Rückgabe: Report-dict; `report['ok']` ist True, wenn die Prüfung grün ist
    (seit 2026-09-19, W61 — ein zurückgegebener Report ist immer grün).
    Wirft VerifyError mit ALLEN Befunden; der Fehler trägt den Report als
    Attribut `report` (dort ok=False)."""
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
        # KAPITELKOPF STATT ERSTER FUNDSTELLE (neu 2026-09-17). markers nimmt
        # (Kicker, Titel) aus chapter_markers(); nackte Titel gehen weiter.
        # 2026-09-19 (W47): Die Marke gilt nur noch als UEBERSCHRIFT — der Titel
        # steht allein auf ganzen Zeilen, der Kicker direkt darueber
        # (_kopf_finden). Vorher genuegte eine Seite, die den Kicker irgendwo
        # trug, und ein Querverweis „Kapitel 2, ‚Titel‘" im Lagebild wurde als
        # Kapitelanfang verortet; die Reihenfolgeprobe lief darueber gruen.
        seiten_zeilen = [[z for z in p.splitlines() if z.strip()]
                         for p in pages]
        pos = (0, -1)
        for eintrag in markers:
            if isinstance(eintrag, (tuple, list)):
                kick, mk = eintrag[0], eintrag[1]
            else:
                kick, mk = None, eintrag
            treffer = _kopf_finden(seiten_zeilen, kick, mk, pos)
            if treffer is None:
                needle = _dehyph(_nrm(mk))
                wo = f" unter dem Kicker {kick!r}" if kick else ""
                if _kopf_finden(seiten_zeilen, kick, mk) is not None:
                    fails.append(f"MARKER-REIHENFOLGE verletzt: {mk!r} — die "
                                 f"Ueberschrift steht vor der des vorigen "
                                 f"Markers.")
                elif whole_d.find(needle) >= 0:
                    fails.append(f"MARKER nicht am Kapitelkopf: {mk!r} — im "
                                 f"PDF-Text gefunden, aber nicht als "
                                 f"Ueberschrift (Titel allein auf eigener "
                                 f"Zeile{wo}); nur Fliesstext oder "
                                 f"Querverweis. Fehlt der Kapitelkopf im "
                                 f"Render, oder weicht der Titel ab?")
                else:
                    fails.append(f"MARKER fehlt im PDF-Text: {mk!r}.")
                continue
            pos = treffer
            marker_pages[mk] = treffer[0] + 1
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

    sig_set = {_nrm(s).strip() for s in (fuss_signaturen or ()) if s
               and str(s).strip()}
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
            # Seit dem 2026-09-05 rendern Signatur und Beleg am KAPITELENDE
            # (chartdoc.build_fuss). Endet eine Seite mit diesem Streifen, ist
            # ihre letzte Textzeile eine Beleg-Zeile — sie endet naturgemaess
            # auf einer Gradminute, nicht auf einem Satzende. Der Streifen ist
            # keine Prosa und wird fuer die Satzende-Probe abgezogen; fuer die
            # Textdeckung zaehlt er weiter mit (er steht auch in
            # source_text_chars). Vor dem Umbau konnte der Fall nicht
            # auftreten: der Streifen sass im unteilbaren Block Kopf+erster
            # Absatz.
            fz = _fuss_zeilen(plines, sig_set)
            pruef = plines[:len(plines) - fz]
            if not pruef:
                continue                # Seite traegt nur einen Kapitelfuss
            tail = pruef[-1].strip()
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
                fails.append(f"SEITE {pi + 1} endet mitten im Satz: {show!r} "
                             f"[Kapitelfuss-Abzug: {fz} Zeile(n)]")
                if not sig_set:
                    fails[-1] += (" — Hinweis: verify() lief OHNE "
                                  "fuss_signaturen=. Seit dem 2026-09-05 "
                                  "steht der Signatur-/Beleg-Streifen am "
                                  "Kapitelende; endet eine Seite damit, "
                                  "meldet die Satzende-Probe ihn "
                                  "faelschlich. Mit "
                                  "fuss_signaturen=build.fuss_signaturen("
                                  "parsed) erneut pruefen, bevor der Befund "
                                  "als echt gilt.")
                elif fz == 0:
                    fails[-1] += (" — Hinweis: auf dieser Seite wurde KEIN "
                                  "Kapitelfuss erkannt. Endet sie sichtbar "
                                  "mit dem Signatur-/Beleg-Streifen, liegt "
                                  "der Fehler in der Fuss-Erkennung "
                                  "(_fuss_zeilen), nicht im Satz.")
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
              "warnings": warns, "failures": fails, "sample_png": sample_png,
              "ok": not fails}                  # 2026-09-19 (W61): True = gruen
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
        fehler = VerifyError(
            f"PDF-Prüfung fehlgeschlagen ({len(fails)} Befund(e)):\n"
            + "\n".join(f"  [{i + 1}] {f}" for i, f in enumerate(fails))
            + ("\nWarnungen:\n" + "\n".join(f"  - {w}" for w in warns)
               if warns else ""))
        fehler.report = report          # 2026-09-19 (W61): ok=False darin
        raise fehler
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
    elif "--selbsttest" not in sys.argv[1:] and "--hilfe" not in sys.argv[1:]:
        # --selbsttest und --hilfe werden am Dateiende bedient (2026-09-19 / 2026-09-20)
        print(__doc__)


# --- Orb-Formatierung ---------------------------------------------------------
# Neu 2026-09-19 (Wartungslauf A, W2). radix liefert den Orb seither
# UNGERUNDET; gerundet wird genau einmal, beim Schreiben — und zwar ueberall
# mit dieser Funktion: Aspekttabelle des Datenblatts, Aspektseite
# (chartdoc.aspekt_page) und was build selbst ausgibt. Vorher rundete radix
# auf 0,01° und chartdoc danach auf die Minute; die Aspektseite stand dadurch
# bis zu 1′ neben Tabelle und Belegen. Die Rundung ist wortgleich die von
# radix._gr() (Grad abschneiden, Minuten runden, Uebertrag bei 60), mit der
# radix seine eigenen Texte schreibt; _selbsttest() haelt beide gegeneinander.

def orb_text(grad) -> str:
    """Orb in Grad (ungerundet) -> 'N°NN′', genau einmal auf die Bogenminute
    gerundet — dieselbe Rundung wie radix._gr() und die Aspekttabelle des
    Datenblatts. Beispiel: 1.4917 -> '1°30′' (die alte Doppelrundung über
    round(1.4917, 2) = 1.49 ergab '1°29′'). Nie einen schon gerundeten Wert
    übergeben — das wäre wieder die Doppelrundung."""
    if grad is None:
        raise TypeError("orb_text(): Orb fehlt (None) — erwartet wird der "
                        "ungerundete Orb in Grad aus radix (Feld 'orb').")
    deg = abs(float(grad))
    d = int(deg)
    m = int(round((deg - d) * 60))
    if m == 60:
        d, m = d + 1, 0
    return f"{d}°{m:02d}′"


# --- Aspekt-Heimat-Probe -----------------------------------------------------
# Neu am 2026-09-06 (Prüfbericht EA, Handlungspunkt 4). Das Datenblatt-Modul
# verlangt für jeden vollen und einseitigen Aspekt genau EIN Thema als Heimat.
# Im Prüflauf fielen von Hand zwei Doppelheimaten und sieben ungedeckte Aspekte
# auf, die sonst durchgegangen wären. Diese Probe macht das mechanisch.
#
# Die Auflösung der Regelkollision mit der Auswahlregel steckt in `dokumentiert`:
# Ein Aspekt darf ohne Heimat bleiben, WENN er im chart_data ausdrücklich als
# Weglassung geführt ist. Vollständigkeit der Rechenschaft, Auswahl der Deutung.

_AH_GLYPH = "☌☍□△⚹⚻⚺"
_AH_NAME = r"(?:AC|MC|DC|IC|[A-ZÄÖÜ][a-zäöüß]+)"
# SCHNITTMARKE fuer JEDEN Teilscan dieser Probe (neu 2026-09-17,
# Klasse-2-Entscheidungslauf, Wiederholungstaeter aus drei Laufabschnitten).
# Ein Abschnitt endet an der naechsten Ueberschrift ODER am naechsten
# @@-Block. Vorher stand das Muster dreimal als Literal im Code, und der
# Untergrund-Zweig hatte ein viertes, abweichendes (`.split("\n**")[0]`):
# fehlte darunter eine `**`-Zeile, lief er bis Dateiende. Die @@-Marke fehlte
# ueberall — @@SELEKTOR und @@ZUGANG stehen hinter der Weglassungsliste und
# landeten mit ihren ASPEKT-Zeilen in `dok`, womit jeder Aspekt als
# dokumentiert weggelassen galt. Seit dieser Fassung regelt KEIN Modul mehr,
# in welcher Reihenfolge die Schlussbloecke stehen muessen — die Probe
# begrenzt sich selbst.
_AH_SCHNITT = r"\n(?:#{2,3} |@@)"

# WORT-TRENNER DER ZUSATZEBENE (neu 2026-09-18, Pruefbericht Geburtshoroskop
# Schritt 1+2 vom 17.09.d, Klasse 1 Nr. 1.3). Das Datenblatt-Modul schreibt fuer
# Untergrund-Aspekte einen Trenner in Halbgeviertstrichen vor
# (`Merkur --Anderthalbquadrat-- Uranus`, mit U+2013). Im `aspekte=`-Feld der
# Themenliste wurde er erkannt, in der WEGLASSUNGSLISTE und in der
# Untergrund-Tabelle nicht: Wer den Satz aus dem Modul dorthin uebertrug, bekam
# FEHLER auf eine korrekt dokumentierte Weglassung. Nachgestellt mit drei
# Minimalfaellen — Modulform FEHLER, Glyphe gruen, Gedankenstrich gruen. Seither
# gilt an ALLEN drei Stellen dieselbe Trennermenge.
_AH_WORT = r"\u2013[A-Za-z\u00c4\u00d6\u00dca-z\u00e4\u00f6\u00fc\u00df]+\u2013"

# Trennzeile einer Markdown-Tabelle (|---|:---:|) — keine Datenzeile (F2).
_AH_TRENNZEILE = re.compile(r"^\s*\|[\s:|\-]*-[\s:|\-]*$")
# Erwartete Form einer Tabellenzeile, fuer die Meldung unlesbarer Zeilen (F2).
_AH_ZEILENFORM = ("| Faktor | <Glyphe> <Aspektname> | Faktor | Orb | … |, "
                  "Faktorzellen mit nacktem Namen; Glyphen ☌ ☍ □ △ ⚹ ⚻ ⚺, "
                  "in der Untergrund-Tabelle ∠ Halbquadrat und "
                  "⚼ Anderthalbquadrat (oder der –Wort–-Trenner). Eine leere "
                  "Tabelle steht als Satz („Keine.“), nicht als Tabellenzeile.")


def _ah_abschnitt(txt, marke, ab=0):
    """Text ab `marke` bis zur naechsten Ueberschrift oder zum naechsten
    @@-Block. Einzige Begrenzungsstelle der Aspekt-Heimat-Probe."""
    i = txt.find(marke, ab)
    if i < 0:
        return None, -1
    ende = i + len(marke)
    teil = txt[ende:]
    schnitt = re.search(_AH_SCHNITT, teil)
    if schnitt:
        teil = teil[:schnitt.start()]
    return teil, ende


# FELDGRENZE DER THEMENLISTE (neu 2026-09-19, W9). Ein Feld endet an der
# naechsten Feldgrenze — gleich welcher: „| name=" oder ein Zeilenanfang mit
# „name=". Vorher standen die Folgefelder einzeln in einer Liste; was darin
# fehlte (klingt=, fuehrt=, familie=, leitachse=, grund=, titel=, teil=),
# wurde dem aspekte=-Feld zugeschlagen, und eine Feldreihenfolge schreibt
# kein Modul vor.
_THEMA_FELDGRENZE = re.compile(r"(?:\||\n)\s*[a-zäöüß_]+\s*=")


def _themen_feld(blk, name):
    """Inhalt des Feldes `name=` eines THEMA-Blocks bis zur naechsten
    Feldgrenze — oder None, wenn das Feld fehlt."""
    m = re.search(r"(?<![\w-])%s\s*=" % re.escape(name), blk)
    if not m:
        return None
    rest = blk[m.end():]
    g = _THEMA_FELDGRENZE.search(rest)
    return rest[:g.start()] if g else rest


# DER RECHENSCHAFTS-BLOCK EINES FOLGEPRODUKTS (neu 2026-09-19, W9): beginnt
# an „TRANSIT-RECHENSCHAFT:" (EA, Transit; im Ultimativ „SAMMELKAPITEL:") und
# endet an der naechsten Ueberschrift, am naechsten @@-Block, an der
# naechsten THEMA-Zeile oder an der naechsten Pflichtzeile der Themenliste.
# Der Rest der Kopfzeile hinter dem Doppelpunkt gehoert dazu: Die
# Ultimativ-Pflichtzeile „SAMMELKAPITEL: T-… , T-…" traegt ihre Kontakte
# oft direkt dort.
_TR_BLOCK_START = re.compile(
    r"^[ \t>*-]*(?:TRANSIT-RECHENSCHAFT|SAMMELKAPITEL)\s*:", re.M)
_TR_BLOCK_ENDE = re.compile(
    r"^(?:#{1,6} |@@|THEMA \d+ \||[ \t>*-]*(?:GESTRICHEN|RECHENSCHAFT|"
    r"REGISTER|SAMMELKAPITEL|TRANSIT-RECHENSCHAFT)\s*:)", re.M)


def _wirkorb_im_fenster(e, orb_wirk=1.5, orb_json=None):
    """Steht diese Passage (ein Eintrag aus events.json) im Wirkorb INNERHALB
    des Fensters? Neu 2026-09-19 (W22) als eine Stelle fuer die Soll-Menge von
    kontakt_heimat() und die Ressourcen-Zaehlmenge des Transits.

    Maßgeblich ist das Feld `wirkorb_im_fenster` (transit.py seit 2026-09-19,
    aus dem engsten Orb im Fenster — nicht `im_wirkorb`, das den Rueckblick
    einschliesst). Weicht `orb_wirk` vom Wirk-Orb des Laufs (`orb_json`) ab,
    zaehlt `min_orb_im_fenster`. Ein events.json von vor dem 2026-09-19 hat
    beide Felder nicht; dann gilt die bisherige Naeherung (exakt im Fenster,
    oder ein Quartal im Fenster und ein engster Orb der Passage im Wirkorb)."""
    if "wirkorb_im_fenster" in e:
        if orb_json is None or abs(float(orb_wirk) - float(orb_json)) < 1e-9:
            return bool(e["wirkorb_im_fenster"])
        mf = e.get("min_orb_im_fenster")
        return mf is not None and mf <= orb_wirk
    return bool(e.get("exakt_im_fenster")) or bool(
        [q for q in (e.get("quartale") or []) if q > 0]
        and e.get("min_orb_grad") is not None
        and e["min_orb_grad"] <= orb_wirk)


def aspekt_heimat(chart_data_pfad: str) -> dict:
    """Prüft die Aspekt-Heimat der Themenliste gegen die Aspekttabellen.

    Liest NUR das chart_data.md — die Themenliste und die Aspekttabellen stehen
    beide dort, die Probe läuft also schon in Schritt 1, vor der Freigabe.

    Rückgabe: {'tabelle': n, 'mit_heimat': [...], 'ohne_heimat': [...],
               'dokumentiert': [...], 'offen': [...], 'doppelt': [...],
               'unlesbar': [(abschnitt, zeile), ...], 'ok': bool}
    `offen` ist die Fehlerliste: weder Heimat noch dokumentierte Weglassung.
    `unlesbar` (neu 2026-09-19, F2): Zeilen der Aspekttabellen, die wie eine
    Tabellenzeile aussehen, aber kein Paar ergeben — etwa ein Zeichen, das die
    Probe nicht kennt (`∡` statt `⚼`), oder ein Symbol in der Faktorzelle.
    Vorher fielen sie still aus der Prüfmenge (falsch-grün); jetzt ist die
    Probe dann nicht grün, und der Bericht nennt die Zeile.
    """
    import re as _re
    txt = open(chart_data_pfad, encoding="utf-8").read()

    def _paare(block, trenner, unlesbar=None, abschnitt=""):
        """Aspektpaare aus einer Markdown-Tabelle ziehen.

        Zwei Tabellenformen werden erkannt (zweite neu am 2026-09-06,
        Prüfbericht Transit 1.4):
          A  | Sonne ☍ Pluto | 2°30′ |          — Paar in EINER Zelle
          B  | Sonne | ☍ Opposition | Pluto | 2°30′ |   — Paar über drei Zellen
        Form B ist die, die Datenblatt- und Typmodul tatsächlich schreiben; sie
        wurde bis dahin nicht erkannt, weshalb die Probe leer lief.

        `unlesbar` (Liste, 2026-09-19, F2): Tabellenzeilen, die kein Paar
        ergeben, werden dort mit `abschnitt` gesammelt statt still
        übersprungen — außer Kopf- und Trennzeilen."""
        out = set()
        pa = _re.compile(r"\|\s*(%s)\s*(?:%s)\s*(%s)\s*\|"
                         % (_AH_NAME, trenner, _AH_NAME))
        pb = _re.compile(r"\|\s*(%s)\s*\|\s*(?:%s|[A-Za-zÄÖÜäöüß]+)[^|]*\|\s*(%s)\s*\|"
                         % (_AH_NAME, trenner, _AH_NAME))
        zeilen = block.splitlines()
        for n, z in enumerate(zeilen):
            m = pa.match(z) or pb.match(z)
            if m and m.group(1) not in ("Aspekt", "Faktor", "Punkt"):
                out.add(frozenset([m.group(1), m.group(2)]))
            elif unlesbar is not None and z.lstrip().startswith("|"):
                if _AH_TRENNZEILE.match(z):
                    continue
                folge = zeilen[n + 1] if n + 1 < len(zeilen) else ""
                erste = z.strip().strip("|").split("|")[0].strip()
                if _AH_TRENNZEILE.match(folge) or erste in (
                        "Aspekt", "Faktor", "Punkt"):
                    continue                    # Kopfzeile der Tabelle
                unlesbar.append((abschnitt, z.strip()))
        return out

    # ÜBERSCHRIFTEN (korrigiert 2026-09-06, Prüfbericht Transit 1.4).
    # Bis dahin wurde ausschließlich "### Hauptaspekte" gesucht. Die
    # Geburtshoroskop- und Ultimativ-Datenblätter schreiben aber
    # "### Volle Aspekte" / "### Einseitige Aspekte" / "### Nebenaspekte".
    # Folge: Die Prüftabelle bestand in JEDEM Standardlauf nur aus den drei
    # Untergrund-Aspekten, die Probe übersah den Rest und meldete trotzdem
    # "keine offenen" — ein stiller Freispruch.
    tabelle, unlesbar = set(), []
    for kopf in ("### Hauptaspekte", "### Volle Aspekte",
                 "### Einseitige Aspekte", "### Nebenaspekte"):
        if kopf not in txt:
            continue
        teil, _ = _ah_abschnitt(txt, kopf)
        tabelle |= _paare(teil, "[%s]" % _AH_GLYPH, unlesbar, kopf)
    if "### Untergrund-Aspekte" in txt:
        teil, _ = _ah_abschnitt(txt, "### Untergrund-Aspekte")
        # TRENNER DER UNTERGRUND-TABELLE (korrigiert 2026-09-16, Pruefbericht
        # Geburtshoroskop Schritt 1+2 vom 16.09., Befund 1.2). Hier stand
        # `_paare(teil, "—")`. Die Spaltenform von `_paare` verlangt in der
        # mittleren Zelle entweder den Trenner oder einen Buchstaben; die
        # Aspektarten der Zusatzebene tragen aber die Glyphen ⚼ und ∠, und die
        # stehen nicht in _AH_GLYPH. Wer die Untergrund-Tabelle wie die drei
        # Haupttabellen schreibt (| Sonne | ⚼ Anderthalbquadrat | Uranus | …),
        # bekam die Zeilen LAUTLOS nicht in die Pruefmenge — die Probe meldete
        # dann "ok", ohne die Zusatzebene je angesehen zu haben. Derselbe
        # Fehlertyp wie der Befund vom 06.09. ("las nur ### Hauptaspekte").
        # _AH_GLYPH bleibt bewusst unangetastet: Dieselbe Konstante steuert die
        # `aspekte=`-Felder der Themenliste, und dort verlangt das
        # Datenblatt-Modul fuer Zusatzaspekte ausdruecklich den
        # –Wort–-Trenner statt der Glyphe.
        # 2026-09-19 (F2): Glyphen der Tabelle sind ∠ Halbquadrat und
        # ⚼ Anderthalbquadrat (Datenblatt-Modul); jedes andere Zeichen
        # (etwa ∡) landet in `unlesbar`, statt still zu fehlen.
        tabelle |= _paare(teil, "[—⚼∠]|" + _AH_WORT, unlesbar,
                          "### Untergrund-Aspekte")

    heimat, doppelt = {}, []
    # EINSTIEGSMARKE DER THEMENLISTE (korrigiert 2026-09-16, Pruefbericht
    # Geburtshoroskop Schritt 1+2 vom 16.09., Befund 1.1). Hier stand
    # `if "THEMA 1 |" in txt:` — die Themenliste wurde also nur gelesen, wenn
    # ihre Nummerierung bei 1 beginnt. Dass sie das muss, steht in keinem
    # Modul. Ein Lauf, der Themennummer und Kapitelnummer gleichziehen wollte
    # (THEMA 2 … THEMA 10, damit "Deutungsort: Thema n" eindeutig auf ein
    # Kapitel zeigt), bekam SAEMTLICHE Aspekte als "ohne Heimat" gemeldet,
    # obwohl jeder eine hatte: `heimat` blieb leer, und die Probe meldete
    # einen Fehler, ohne geprueft zu haben. Jetzt wird die erste THEMA-Zeile
    # gesucht, gleich mit welcher Zahl sie anfaengt; der Rest ist unveraendert.
    _erste = _re.search(r"THEMA \d+ \|", txt)
    if _erste:
        tl = "\n" + txt[_erste.start():]
        _ende = _re.search(_AH_SCHNITT, tl)
        if _ende:
            tl = tl[:_ende.start()]
        for schluss in ("RECHENSCHAFT", "REGISTER:", "GESTRICHEN:"):
            tl = tl.split(schluss)[0]
        for blk in _re.split(r"\nTHEMA \d+ \|", tl):
            if "aspekte=" not in blk:
                continue
            t = _re.search(r"titel=(.+)", blk)
            titel = (t.group(1).strip()[:40] if t else "?")
            if "teil=jetzt" in blk:       # Transit-Kapitel: eigene Aspektmenge
                continue
            # 2026-09-19 (W9): dieselbe Feldgrenze wie in kontakt_heimat() —
            # vorher endete das Feld nur an traegt|rang|form|verweis|praxis=.
            feld = _themen_feld(blk, "aspekte") or ""
            feld = _re.sub(r"[TR]-\w+", " ", feld)
            for m in _re.finditer(r"(%s)\s*(?:[%s]|–[A-Za-zä]+–)\s*(%s)"
                                  % (_AH_NAME, _AH_GLYPH, _AH_NAME), feld):
                paar = frozenset([m.group(1), m.group(2)])
                if len(paar) < 2:
                    continue
                if paar in heimat and heimat[paar] != titel:
                    doppelt.append((sorted(paar), heimat[paar], titel))
                heimat.setdefault(paar, titel)

    # DOKUMENTIERTE WEGLASSUNGEN — der Scan ist seit dem 2026-09-14 BEGRENZT
    # (Pruefbericht Geburtshoroskop Schritt 1+2 vom 14.09., Rubrik 5.1).
    # Vorher las er ab der ersten Fundstelle einer Marke BIS ZUM DATEIENDE. Das
    # Datenblatt-Modul schreibt die Weglassungs-Ueberschrift aber in den
    # Aspekt-Abschnitt, also VOR Strukturbild, Themenliste und Ressourcen-Block
    # — mit der Folge, dass saemtliche `aspekte=`-Felder der Themenliste und
    # saemtliche Zeilen des Ressourcen-Blocks in `dok` landeten. Damit galt
    # JEDER Aspekt ohne Heimat automatisch als dokumentiert weggelassen, und
    # `offen` konnte nie etwas melden: eine Probe, die nichts mehr finden kann.
    # Aufgefallen ist es nur, weil der Prueffall zufaellig keine Fehlstelle
    # hatte. Jetzt endet jeder Marken-Abschnitt an der naechsten Ueberschrift —
    # dieselbe Begrenzung, die der Tabellen-Scan oben schon benutzt.
    dok = set()
    for marke in ("Aspekte ohne Deutungs-Heimat", "Weglassung", "GESTRICHEN"):
        stelle = 0
        while True:
            i = txt.find(marke, stelle)
            if i < 0:
                break
            teil, stelle = _ah_abschnitt(txt, marke, i)
            # ZUSATZEBENE MIT (neu 2026-09-17): Seit dem 2026-09-16 liegt die
            # Untergrund-Tabelle in der Pruefmenge, ihre Aspektarten tragen ⚼
            # und ∠ — ohne sie hier ist eine Untergrund-Zeile pruefbar, aber
            # nicht dokumentierbar. Beim Patchen der Grenzen aufgefallen.
            dok |= _paare(teil, "[%s—⚼∠]|%s" % (_AH_GLYPH, _AH_WORT))
            for m in _re.finditer(r"(%s)\s*(?:[%s⚼∠]|—|%s)\s*(%s)"
                                  % (_AH_NAME, _AH_GLYPH, _AH_WORT, _AH_NAME), teil):
                dok.add(frozenset([m.group(1), m.group(2)]))

    ohne = sorted(tabelle - set(heimat), key=lambda x: sorted(x))
    offen = [p for p in ohne if p not in dok]
    # AUSSAGELOS (neu 2026-09-06, Prüfbericht Transit 1.3): Findet die Probe
    # keine einzige Aspektzeile, hat sie NICHTS geprüft. Das als "ok" zu melden
    # ist gefährlicher als ein Fehler, weil es wie eine bestandene Prüfung
    # aussieht. Typischer Fall: ein Transit-, EA- oder Folgeprodukt-Datenblatt,
    # das keine Radix-Aspekttabellen trägt — dort ist statt dieser Probe
    # `kontakt_heimat()` zuständig.
    return {
        "tabelle": len(tabelle),
        "aussagelos": not tabelle,
        "mit_heimat": sorted(" — ".join(sorted(p)) for p in set(heimat) & tabelle),
        "ohne_heimat": [" — ".join(sorted(p)) for p in ohne],
        "dokumentiert": [" — ".join(sorted(p)) for p in ohne if p in dok],
        "offen": [" — ".join(sorted(p)) for p in offen],
        "doppelt": [(" — ".join(a), b, c) for a, b, c in doppelt],
        "unlesbar": unlesbar,
        "ok": bool(tabelle) and not offen and not doppelt and not unlesbar,
    }


def kontakt_heimat(chart_data_pfad: str, events_json_pfad: str,
                   orb_wirk: float = 1.5) -> dict:
    """Kontakt-Heimat-Probe für Folgeprodukte (Transit, EA) — neu 2026-09-06.

    Das Gegenstück zu `aspekt_heimat()` für Dokumente, deren Deutung aus
    TRANSIT-Kontakten besteht und die deshalb keine Radix-Aspekttabellen
    tragen (Prüfbericht Transit 2026-09-06, 1.3 und 4.3). Geprüft wird
    dasselbe Prinzip: Jeder Kontakt gehört zu höchstens EINEM Thema, und kein
    Kontakt verschwindet stillschweigend.

    Gehalten wird die Themenliste des `chart_data` gegen die vom Builder
    gerechneten Kontakte im JSON. Erwartete Notation in den `aspekte=`-Feldern:
    `T-Saturn ☌ R-Venus` — der T-/R-Präfix ist zugleich das, woran
    `aspekt_heimat()` Transit-Kapitel erkennt und überspringt.

    Gezählt werden nur PRIMÄRE Kontakte im Wirkorb innerhalb des Fensters; das
    ist genau die Menge, für die das Typmodul Rechenschaft verlangt.

    Rückgabe: {'kontakte', 'in_themen', 'rechenschaft', 'ohne_heimat',
               'doppelt', 'unbekannt', 'ok'}
    """
    import json as _json
    import re as _re2

    GLYPH = {"☌": "Konjunktion", "☍": "Opposition", "□": "Quadrat",
             "△": "Trigon", "⚹": "Sextil", "⚻": "Quincunx", "⚺": "Halbsextil"}
    txt = open(chart_data_pfad, encoding="utf-8").read()
    daten = _json.load(open(events_json_pfad, encoding="utf-8"))

    # 1) Soll-Menge: primäre Wirkorb-Kontakte im Fenster
    soll, alle = set(), set()
    for e in daten.get("events", []):
        if e.get("spiegel"):
            continue
        alle.add((e["transit"], e["aspekt"], e["ziel"]))
        if not e.get("primaer"):
            continue
        # 2026-09-19 (W22): eine Definition fuer Soll-Menge und
        # Ressourcen-Zaehlmenge (_wirkorb_im_fenster); fuer ein events.json
        # von vor dem 2026-09-19 dieselbe Naeherung wie bisher.
        if _wirkorb_im_fenster(e, orb_wirk, daten.get("orb_wirk")):
            soll.add((e["transit"], e["aspekt"], e["ziel"]))

    # Namensbrücke: das analyse-/chart_data-Deutsch schreibt Umlaute
    # (Glückspunkt, Südknoten), der Builder schreibt sie aus (Glueckspunkt).
    def _norm(n):
        n = n.lower()
        for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
            n = n.replace(a, b)
        return n
    # 2026-09-19 (W9): getrennt fuer Transiter und Ziele. Vorher teilten beide
    # EIN Woerterbuch; stand `Mondknoten` unter den Zielen, wurde `T-Mondknoten`
    # (die Beleg-Notation des laufenden Knotens) als Ziel `Mondknoten` gelesen
    # und als unbekannter Kontakt gemeldet.
    tnamen, znamen = {}, {}
    for t, a, z in alle:
        tnamen.setdefault(_norm(t), t)
        znamen.setdefault(_norm(z), z)
    tnamen.setdefault("mondknoten", "Knoten")

    # 2) Ist-Menge: die Felder fuehrt= und aspekte= der Themenliste.
    #    2026-09-19 (L19): Im Transit traegt `fuehrt=` den fuehrenden KONTAKT
    #    (Transit-Modul); er muss nicht in aspekte= wiederholt werden.
    #    2026-09-19 (W9): Ein Feld endet an der naechsten Feldgrenze, gleich
    #    welche (_themen_feld) — vorher fehlten klingt=, fuehrt=, familie=,
    #    leitachse=, grund=, titel= und teil= in der Trennerliste, und ein
    #    solches Feld hinter aspekte= wurde mitgezaehlt. Die Liste beginnt an
    #    der ersten THEMA-Zeile (wie in aspekt_heimat()) und endet an der
    #    naechsten Ueberschrift oder dem naechsten @@-Block.
    heimat, doppelt, unbekannt = {}, [], []
    _erste = _re2.search(r"THEMA \d+ \|", txt)
    if _erste:
        tl = "\n" + txt[_erste.start():]
        _ende = _re2.search(_AH_SCHNITT, tl)
        if _ende:
            tl = tl[:_ende.start()]
        for schluss in ("RECHENSCHAFT", "REGISTER:", "GESTRICHEN:",
                        "SAMMELKAPITEL:"):
            tl = tl.split(schluss)[0]
        for blk in _re2.split(r"\nTHEMA \d+ \|", tl):
            felder = [f for f in (_themen_feld(blk, "fuehrt"),
                                  _themen_feld(blk, "aspekte")) if f]
            if not felder:
                continue
            t = _re2.search(r"titel=(.+)", blk)
            titel = (t.group(1).strip()[:40] if t else "?")
            for m in _re2.finditer(r"T-(\w+)\s*([%s])\s*R-([\wÄÖÜäöüß]+)"
                                   % "".join(GLYPH), " ".join(felder)):
                k = (tnamen.get(_norm(m.group(1)), m.group(1)),
                     GLYPH[m.group(2)],
                     znamen.get(_norm(m.group(3)), m.group(3)))
                # Sekundäre Ziele dürfen ein Thema tragen (Selbst-Transite!),
                # sie stehen nur nicht in der Rechenschaftspflicht. Gemeldet
                # wird deshalb nur ein Kontakt, den der Builder gar nicht kennt.
                if k not in alle:
                    unbekannt.append((titel, " ".join(k)))
                    continue
                if k not in soll:
                    continue
                if k in heimat and heimat[k] != titel:
                    doppelt.append((" ".join(k), heimat[k], titel))
                heimat.setdefault(k, titel)

    # 3) Rechenschaft: was im Sammelkapitel steht
    ALIAS = {"Knoten": "(?:mond)?knoten", "Nordknoten": "(?:nord)?knoten",
             "Glueckspunkt": "gl(?:ue|ü)ckspunkt"}
    def _mst(n):
        return ALIAS.get(n, _re2.escape(n.lower()))
    rech = set()
    # VERSCHAERFT 14.09.2026 (Pruefbericht EA Schritt 1+2, 1.5, Nebenbefund):
    # Bis dahin galt ein Kontakt als "in der Rechenschaft", sobald Transiter-
    # und Zielname irgendwo innerhalb von 80 Zeichen auf EINER Zeile standen.
    # Im EA-Prueflauf traf der reine RADIX-Rechenschaftsblock, der kein
    # einziges Transit-Wort enthaelt, so zufaellig 18 von 45 Kontakten — ein
    # Freispruch, der nichts prueft. Gezaehlt werden jetzt nur noch Zeilen, die
    # sich auch als Transit-Zeile zu erkennen geben: T-Praefix, das Wort
    # Transit, oder "laufend".
    # 2026-09-19 (W9): gelesen wird NUR der Block TRANSIT-RECHENSCHAFT (im
    # Ultimativ die Zeile SAMMELKAPITEL:), bis zur naechsten Ueberschrift, zum
    # naechsten @@-Block oder zur naechsten Pflichtzeile. Vorher zaehlte alles
    # ab dem ersten „RECHENSCHAFT" — auch der Ressourcen-Block, dessen
    # Deckel-Zeile eine Negativkontrolle gruen hielt (T12-18c). Und die Zeile
    # muss die Aspektart nennen (Glyphe oder Wort): eine Zeile zu Saturn □
    # Sonne verbucht nicht mehr Saturn △ Sonne mit.
    _TR_MARKE = _re2.compile(r"(?:\bt-|transit|laufend)")
    bloecke = []
    for m in _TR_BLOCK_START.finditer(txt):
        rest = txt[m.end():]
        # Kopfzeilen-Rest immer mit; die Blockgrenze gilt ab der Folgezeile.
        nl = rest.find("\n")
        kopf, folge = (rest, "") if nl < 0 else (rest[:nl], rest[nl:])
        ende = _TR_BLOCK_ENDE.search(folge)
        bloecke.append(kopf + (folge[:ende.start()] if ende else folge))
    zeilen_tr = [z for z in "\n".join(bloecke).lower().splitlines()
                 if _TR_MARKE.search(z)]
    zeichen = {v: k for k, v in GLYPH.items()}
    # Zwischen Name und Aspekt kein fremdes Aspektzeichen: Auf einer Zeile mit
    # mehreren Kontakten („T-Jupiter △ R-Sonne, T-Saturn □ R-Mond") gilt
    # sonst Jupiter □ Mond als benannt.
    zw = r"[^\n%s]{0,40}?" % "".join(GLYPH)
    for k in soll:
        a, b = _mst(k[0]), _mst(k[2])
        asp = "(?:%s|%s)" % (_re2.escape(zeichen.get(k[1], k[1])),
                             _re2.escape(k[1].lower()))
        muster = (a + zw + asp + zw + b, b + zw + asp + zw + a)
        if any(_re2.search(p, z) for z in zeilen_tr for p in muster):
            rech.add(k)

    ohne = sorted(soll - set(heimat) - rech)
    return {
        "kontakte": len(soll),
        "in_themen": len(heimat),
        # Korrigiert 2026-09-15 (Pruefbericht EA Schritt 1+2, Rubrik 2):
        # gezaehlt wird, was NUR in der Rechenschaft steht. Vorher zaehlte
        # der Wert jeden Soll-Kontakt mit, dessen beide Namen irgendwo
        # hinter der Marke "RECHENSCHAFT" auf einer Transit-Zeile standen —
        # auch die, die ein Kapitel tragen. Im EA-Prueffall meldete er 35
        # bei 27 Rechenschaftszeilen. Auf "ohne_heimat" und "ok" hatte das
        # nie Einfluss; irrefuehrend war allein die Zahl im Bericht.
        "rechenschaft": len(rech - set(heimat)),
        "ohne_heimat": [" ".join(k) for k in ohne],
        "doppelt": doppelt,
        "unbekannt": unbekannt,
        "ok": not ohne and not doppelt and not unbekannt,
        # Ergaenzt 2026-09-15: die Schluesselmengen selbst, damit
        # transit_rechenschaft() die Differenz bilden kann, ohne die
        # Themenliste ein zweites Mal zu parsen. Rein additiv.
        "soll_keys": sorted(soll),
        "heimat_keys": sorted(heimat),
    }


def kontakt_heimat_bericht(chart_data_pfad: str, events_json_pfad: str,
                           orb_wirk: float = 1.5) -> str:
    """Einzeiliger Prüftext für Schritt 1 eines Folgeprodukts."""
    r = kontakt_heimat(chart_data_pfad, events_json_pfad, orb_wirk)
    if r["ok"]:
        return ("Kontakt-Heimat: %d primaere Wirkorb-Kontakte im Fenster, "
                "%d in Themen, %d in der Rechenschaft, keine Doppelheimat, "
                "keine offenen." % (r["kontakte"], r["in_themen"],
                                    r["rechenschaft"]))
    L = ["Kontakt-Heimat: FEHLER (%d Kontakte im Fenster, %d in Themen, "
         "%d in der Rechenschaft)." % (r["kontakte"], r["in_themen"],
                                       r["rechenschaft"])]
    for k in r["ohne_heimat"]:
        L.append("  OHNE HEIMAT und nicht in der Rechenschaft: %s" % k)
    if r["ohne_heimat"]:
        # 2026-09-19 (W9, L19): sagen, wo die Probe liest.
        L.append("  Gelesen wird: Heimat in fuehrt= und aspekte= der Themenliste "
                 "(klingt= ist keine Heimat), Rechenschaft nur im Block "
                 "TRANSIT-RECHENSCHAFT: bzw. im Ultimativ SAMMELKAPITEL:, je "
                 "Kontakt mit Transiter, Aspektzeichen oder -wort und Radixpunkt. "
                 "Den Block liefert build.transit_rechenschaft_block(chart_data, "
                 "events_json).")
    for k, a, b in r["doppelt"]:
        L.append("  DOPPELTE HEIMAT: %s -> %s / %s" % (k, a, b))
    for titel, k in r["unbekannt"]:
        # 2026-09-19 (W9): Die Meldung sagte „kein primaerer Wirkorb-Kontakt";
        # gemeint ist ein Kontakt, den events.json gar nicht fuehrt.
        L.append("  IM THEMA, aber in events.json kein solcher Kontakt: %s (%s)"
                 " — Namen, Aspektzeichen und Notation T-<Transiter> <Glyphe> "
                 "R-<Radixpunkt> pruefen" % (k, titel))
    return "\n".join(L)


GLYPH_ZU_ASPEKT = {"☌": "Konjunktion", "☍": "Opposition", "□": "Quadrat",
                   "△": "Trigon", "⚹": "Sextil", "⚻": "Quincunx",
                   "⚺": "Halbsextil"}
ASPEKT_ZU_GLYPH = {v: k for k, v in GLYPH_ZU_ASPEKT.items()}


def _datum_de(d):
    """2030-01-02 -> 02.01.2030; unbekanntes Format bleibt stehen."""
    teile = str(d).split("-")
    return ("%s.%s.%s" % (teile[2], teile[1], teile[0])
            if len(teile) == 3 else str(d))


def _bogenminuten(grad):
    """Annaeherung in Grad -> 'n.n′' — dieselbe Form wie der transit.py-Report
    („Annaeherung bis 1.8′")."""
    return "%.1f′" % (float(grad) * 60)


def _passagen_zeitangaben(sel, start, end):
    """Zeitangaben eines Kontakts aus seinen Passagen mit Wirkorb im Fenster
    (neu 2026-09-19, W7): Nulldurchgaenge im, vor und nach dem Fenster (samt
    Vorlauf und Fortsetzung), Annaeherungen, engster Orb IM Fenster, die
    Wirkorb-Perioden im Fenster und das wahre Wirkorb-Ende bzw. den Beginn.
    `neu_format` ist False fuer ein events.json von vor dem 2026-09-19 (dann
    fehlen Fortsetzung und Vorlauf, und „nie exakt" ist nicht belegbar)."""
    neu_format = all("exakt_gesamt" in e for e in sel)
    alle_ex = sorted({d for e in sel
                      for d in (e.get("exakt_gesamt") or e.get("exakt") or [])})
    ex_f = [d for d in alle_ex if start <= d <= end]
    ex_vor = [d for d in alle_ex if d < start]
    ex_nach = sorted(set(alle_ex + [d for e in sel
                                    for d in (e.get("exakt_nach_fenster")
                                              or [])]))
    ex_nach = [d for d in ex_nach if d > end]
    ann = []
    for e in sel:
        ann += [tuple(a) for a in (e.get("annaeherung") or [])]
        for teil in ("vorlauf", "fortsetzung"):
            ann += [tuple(a) for a in ((e.get(teil) or {}).get("annaeherung")
                                       or [])]
    ann = sorted(set(ann))
    orbs_f = [e.get("min_orb_im_fenster") for e in sel
              if e.get("min_orb_im_fenster") is not None]
    if not orbs_f and not neu_format:          # altes Format: Passagenwert
        orbs_f = [e.get("min_orb_grad") for e in sel
                  if e.get("min_orb_grad") is not None]
    per = []
    for e in sel:
        wp = e.get("wirkorb_perioden")
        if wp is None:                         # altes Format
            wp = e.get("perioden") if e.get("im_wirkorb") else []
        for a, b in wp or []:
            if b >= start and a <= end:
                per.append((max(a, start), min(b, end), a < start, b >= end))
    per.sort()
    von_g = min((e["wirkorb_von_gesamt"] for e in sel
                 if e.get("wirkorb_von_gesamt")), default=None)
    bis_g = max((e["wirkorb_bis_gesamt"] for e in sel
                 if e.get("wirkorb_bis_gesamt")), default=None)
    return {"neu_format": neu_format, "ex_f": ex_f, "ex_vor": ex_vor,
            "ex_nach": ex_nach, "alle_ex": sorted(set(ex_vor + ex_f + ex_nach)),
            "ann": ann, "ann_f": [a for a in ann if start <= a[0] <= end],
            "orb_f": min(orbs_f) if orbs_f else None, "perioden": per,
            "von_g": von_g, "bis_g": bis_g}


def _wirkorb_text(z, start, end):
    """„Wirkorb im Fenster A–B[, C–D] (begonnen X, bis Y nach dem Fenster)"."""
    per = z["perioden"]
    if not per:
        return "im Fenster nicht im Wirkorb"
    txt = "Wirkorb im Fenster " + ", ".join(
        "%s–%s" % (_datum_de(a), _datum_de(b)) for a, b, _, _ in per)
    zusatz = []
    if per[0][2] and z["von_g"] and z["von_g"] < start:
        zusatz.append("begonnen %s" % _datum_de(z["von_g"]))
    if per[-1][3] and z["bis_g"] and z["bis_g"] > end:
        zusatz.append("bis %s, nach dem Fenster" % _datum_de(z["bis_g"]))
    return txt + (" (%s)" % "; ".join(zusatz) if zusatz else "")


def _kontakt_zeit_text(z, start, end):
    """Zeitangaben eines Transit-Kontakts als eine Zeile (W7, W22): exakt im
    Fenster — sonst Annaeherung oder engster Orb im Fenster („nie exakt" nur
    ohne jeden Nulldurchgang der Passage) —, dazu exakt vor/nach dem Fenster
    und die Wirkorb-Perioden. `z` aus _passagen_zeitangaben()."""
    orb_f = ("%s°" % z["orb_f"]) if z["orb_f"] is not None else "?"
    teile = []
    if z["ex_f"]:
        teile.append("exakt " + ", ".join(_datum_de(d) for d in z["ex_f"]))
    elif z["ann_f"]:
        d, o = min(z["ann_f"], key=lambda a: a[1])
        teile.append("im Fenster nicht exakt, Annäherung bis %s am %s"
                     % (_bogenminuten(o), _datum_de(d)))
    elif z["alle_ex"] or not z["neu_format"]:
        teile.append("im Fenster nicht exakt (engster Orb im Fenster %s)"
                     % orb_f)
    else:
        teile.append("nie exakt (engster Orb im Fenster %s)" % orb_f)
    if z["ex_vor"]:
        teile.append("exakt vor dem Fenster "
                     + ", ".join(_datum_de(d) for d in z["ex_vor"]))
    if z["ex_nach"]:
        teile.append("exakt nach dem Fenster "
                     + ", ".join(_datum_de(d) for d in z["ex_nach"]))
    for d, o in z["ann"]:
        if d < start or d > end:
            teile.append("Annäherung %s dem Fenster bis %s am %s"
                         % ("vor" if d < start else "nach",
                            _bogenminuten(o), _datum_de(d)))
    if not z["neu_format"]:
        teile.append("Fortsetzung nach dem Fenster unbekannt")
    teile.append(_wirkorb_text(z, start, end))
    return " · ".join(teile)


# Die events.json fuehrt den laufenden Mondknoten als „Knoten", der
# chartdata.py-Vertrag und inhaltsprobe P3 kennen nur „Mondknoten". Bis zum
# 2026-09-22 schrieben transit_rechenschaft_block() und ressourcen_block()
# deshalb `T-Knoten Quadrat R-Mondknoten`: build.kontakt_heimat() las die Zeile ueber
# ihre ALIAS-Tabelle gruen, inhaltsprobe P3 verwarf dieselbe Zeile als
# „traegt keinen lesbaren Kontakt" (Prueflauf Transit Schritt 1+2 vom
# 2026-09-22, 1.3). Geschrieben wird jetzt der Vertragsname; gelesen wird
# unveraendert beides.
_VERTRAGSNAME = {"Knoten": "Mondknoten", "Nordknoten": "Mondknoten",
                 "Suedknoten": "Südknoten", "Glueckspunkt": "Glückspunkt"}


def _vertragsname(n: str) -> str:
    """Faktorname der events.json -> Name des chartdata.py-Vertrags."""
    return _VERTRAGSNAME.get(n, n)


def transit_rechenschaft(chart_data_pfad: str, events_json_pfad: str,
                         stichtag: str = None, orb_wirk: float = 1.5,
                         typ: str = None) -> dict:
    """Die fertigen Zeilen des Blocks `TRANSIT-RECHENSCHAFT:` — neu 2026-09-15.

    Gebaut nach dem Prüfbericht EA Schritt 1+2 vom 15.09., Rubrik 2
    ("von Hand nachgebaut, obwohl eine Funktion es liefern könnte"); Chris hat
    sie am selben Tag bestellt.

    Warum es sie gibt: `kontakt_heimat()` zählt ALLE primären Wirkorb-Kontakte
    des Rechenfensters — bei `--months 24` also über zwei Jahre. Ein EA deutet
    davon nur die Momentaufnahme zum Stichtag, ein Transit-Horoskop nur seine
    Kapitel. Damit die Probe grün läuft, ohne dass etwas stillschweigend
    verschwindet, trägt das Datenblatt hinter `GESTRICHEN:` je eine Zeile für
    jeden Fensterkontakt OHNE Kapitel. Diese Liste ist eine reine Subtraktion
    aus Daten, die der Builder ohnehin hat, und wurde trotzdem je Lauf von Hand
    gefiltert — im Prüflauf vom 15.09. mit einem geratenen Feldnamen
    (`exakt_datum` statt `exakt`), woraufhin alle 27 Zeilen "nie exakt" sagten,
    obwohl 22 davon ein Exaktdatum haben. Der Fehler wirft nicht, er liefert
    leer, und wäre durch jede Probe gekommen.

    `stichtag` wird, wenn nicht übergeben, aus dem JSON gelesen
    (`jetzt.stichtag`, sonst `asof`). Die Zeilen sind nach dem ersten
    Exaktdatum sortiert (seit 2026-09-19 auch vor und nach dem Fenster; ohne
    Nulldurchgang nach dem Datum der engsten Annäherung), undatierte ans Ende.

    Seit 2026-09-19 (W7) — was eine Zeile sagt und woher es kommt
    (events.json von transit.py, Stand 2026-09-19):
      * Gewertet werden die Passagen des Kontakts mit Wirkorb IM FENSTER (vorher
        die „engste" — und der exakte Wert 0,0 galt dabei als 99, sodass eine
        Teilspanne ohne Exaktkontakt gewann und die Zeile „nie exakt" sagte).
      * „exakt …" nennt die Nulldurchgänge im Fenster; die davor und danach
        (auch aus Vorlauf und Fortsetzung) stehen ausdrücklich als „exakt vor
        dem Fenster" / „exakt nach dem Fenster". „nie exakt" steht nur, wenn
        die ganze Passage keinen Nulldurchgang hat; ein Minimum ohne
        Nulldurchgang heißt „Annäherung bis x′ am D".
      * Der engste Orb ist der IM FENSTER (`min_orb_im_fenster`), nicht der der
        Passage, der im Rückblick liegen kann; die Wirkorb-Perioden stehen mit
        Datum, ein Beginn vor dem Fenster und ein Ende danach ausdrücklich.
      * typ='transit' (Transit-Horoskop, Ultimativ): Grund „ohne eigenes
        Kapitel, Zeile in ‚Mitlaufendes'". typ='ea': der Wortlaut der
        Momentaufnahme wie bisher. typ=None: EA, wenn die Themenliste `teil=`
        mit `jetzt`/`zeitlos` trägt oder der Dateiname `_EA_` enthält, sonst
        Transit — `r['typ']` sagt, welcher Wortlaut gewählt wurde.

    Rückgabe: {'zeilen', 'kontakte', 'in_themen', 'offen', 'stichtag', 'typ',
               'fenster'}
    """
    import json as _json

    r = kontakt_heimat(chart_data_pfad, events_json_pfad, orb_wirk)
    soll = set(tuple(k) for k in r["soll_keys"])
    heimat = set(tuple(k) for k in r["heimat_keys"])
    rest = soll - heimat

    daten = _json.load(open(events_json_pfad, encoding="utf-8"))
    if not stichtag:
        stichtag = (daten.get("jetzt") or {}).get("stichtag") or daten.get("asof")
    start, end = daten.get("start") or "", daten.get("end") or "9999"
    typ = _rechenschaft_typ(chart_data_pfad, typ)

    # Passagen je Schluessel: nur die mit Wirkorb IM FENSTER (die Soll-Menge
    # zaehlt genau diese). 2026-09-19 (W7): vorher „die engste" per
    # `(min_orb_grad or 99)` — 0,0 (exakt) wurde dabei zu 99.
    nach_key = {}
    for e in daten.get("events", []):
        if e.get("spiegel"):
            continue
        k = (e["transit"], e["aspekt"], e["ziel"])
        if k in rest:
            ok = _wirkorb_im_fenster(e, orb_wirk, daten.get("orb_wirk"))
            nach_key.setdefault(k, []).append((ok, e))

    alt_format = False
    zeilen, sortier = [], []
    for k in sorted(rest):
        paare = nach_key.get(k, [])
        sel = [e for ok, e in paare if ok] or [e for _, e in paare]
        z = _passagen_zeitangaben(sel, start, end)
        alt_format = alt_format or not z["neu_format"]
        orb_f = ("%s°" % z["orb_f"]) if z["orb_f"] is not None else "?"
        if typ == "ea":
            if z["alle_ex"]:
                datum = ", ".join(_datum_de(d) for d in z["alle_ex"])
                if all(d < (stichtag or "") for d in z["alle_ex"]):
                    grund = ("exakt %s — lag vor der Momentaufnahme, Orb am "
                             "Stichtag %s" % (datum, _orb_am_stichtag(
                                 daten, k, stichtag)))
                else:
                    grund = ("exakt %s — liegt außerhalb der Momentaufnahme "
                             "vom %s" % (datum, _datum_de(stichtag)))
            elif z["ann"]:
                d, o = min(z["ann"], key=lambda a: a[1])
                grund = ("nicht exakt, Annäherung bis %s am %s — liegt außerhalb "
                         "der Momentaufnahme vom %s"
                         % (_bogenminuten(o), _datum_de(d), _datum_de(stichtag)))
            elif z["neu_format"]:
                grund = ("nie exakt (engster Orb im Fenster %s) — streift das "
                         "Fenster nur" % orb_f)
            else:
                grund = ("im Rechenzeitraum nicht exakt (engster Orb %s) — "
                         "Fortsetzung unbekannt, transit.py neu laufen lassen"
                         % orb_f)
        else:
            grund = (_kontakt_zeit_text(z, start, end)
                     + " — ohne eigenes Kapitel, Zeile in „Mitlaufendes“")
        zeile = "- T-%s %s R-%s — %s" % (_vertragsname(k[0]),
                                            ASPEKT_ZU_GLYPH.get(k[1], k[1]),
                                         k[2], grund)
        erstes = (z["alle_ex"] or [a[0] for a in z["ann"]] or ["9999"])[0]
        sortier.append((erstes, zeile))

    if alt_format:
        print("  !! transit_rechenschaft(): events.json im Format vor "
              "2026-09-19 (ohne exakt_gesamt/Fortsetzung) — die Zeilen sagen "
              "nur, was im Rechenzeitraum liegt. transit.py neu laufen lassen.")
    sortier.sort()
    zeilen = [z for _, z in sortier]
    return {"zeilen": zeilen, "kontakte": r["kontakte"],
            "in_themen": r["in_themen"], "offen": len(zeilen),
            "stichtag": stichtag, "typ": typ, "fenster": (start, end)}


def _orb_am_stichtag(daten, k, stichtag):
    """Stichtags-Orb eines Kontakts fuer den EA-Wortlaut (W7, 2026-09-19):
    genau die Zahl der JETZT-Liste (`jetzt.im_orb[].orb_grad`, zwei Stellen,
    wie Report und Anhang sie zeigen) — nicht `orb_stichtag` ein zweites Mal
    gerundet, sonst stuende dieselbe Groesse an zwei Stellen verschieden da.
    Fehlt der Kontakt in der Liste, lag er am Stichtag ausserhalb des
    Erfassungsorbs; ohne Liste oder bei einem anderen Stichtag: „offen"."""
    jetzt = daten.get("jetzt") or {}
    if "im_orb" not in jetzt or (jetzt.get("stichtag") or stichtag) != stichtag:
        return "offen"
    for x in jetzt["im_orb"]:
        if (x.get("transit"), x.get("aspekt"), x.get("ziel")) == tuple(k):
            return "%.2f°" % x["orb_grad"]
    weit = jetzt.get("orb_weit") or daten.get("orb_weit")
    return ("über %s° (außerhalb des Erfassungsorbs)" % weit) if weit else "offen"


def _rechenschaft_typ(chart_data_pfad, typ):
    """'transit' oder 'ea' fuer den Wortlaut der Rechenschaftszeilen (W7)."""
    if typ is not None:
        t = str(typ).strip().casefold()
        if t in ("transit", "ultimativ"):
            return "transit"
        if t == "ea":
            return "ea"
        raise ValueError(
            "transit_rechenschaft(): typ=%r ist unbekannt — erlaubt sind "
            "'transit' (Transit-Horoskop, Ultimativ: Grund „ohne eigenes "
            "Kapitel“), 'ea' (Wortlaut der Momentaufnahme) oder None "
            "(aus der chart_data erkannt)." % (typ,))
    txt = open(chart_data_pfad, encoding="utf-8").read()
    if (re.search(r"\bteil\s*=\s*(?:jetzt|zeitlos)\b", txt)
            or "_EA_" in os.path.basename(chart_data_pfad)):
        return "ea"
    return "transit"


def transit_rechenschaft_block(chart_data_pfad: str, events_json_pfad: str,
                               stichtag: str = None,
                               orb_wirk: float = 1.5, typ: str = None) -> str:
    """Der fertige Block samt Kopfzeile — 1:1 ans Ende des `chart_data`.

    Gehört hinter `GESTRICHEN:`. Nach dem Einfügen läuft
    `kontakt_heimat_bericht()` grün; die Zeilen tragen den `T-`-Präfix, an dem
    die Probe seit dem 14.09. eine Transit-Zeile erkennt. Was die Zeilen sagen
    und `typ=`: s. transit_rechenschaft(). Die Kopfzeile nennt seit
    2026-09-19 das Fenster, auf das sich „im Fenster" bezieht.
    """
    r = transit_rechenschaft(chart_data_pfad, events_json_pfad, stichtag,
                             orb_wirk, typ)
    kopf = ("TRANSIT-RECHENSCHAFT: %d primaere Wirkorb-Kontakte im Fenster "
            "%s–%s, %d tragen ein Kapitel, %d ohne Kapitel — hier einzeln "
            "benannt (Stichtag %s)."
            % (r["kontakte"], _datum_de(r["fenster"][0]),
               _datum_de(r["fenster"][1]), r["in_themen"], r["offen"],
               _datum_de(r["stichtag"])))
    return "\n".join([kopf, ""] + r["zeilen"])


def aspekt_heimat_bericht(chart_data_pfad: str) -> str:
    """Einzeiliger Prüftext für Schritt 1; nur Abweichungen werden ausführlich."""
    r = aspekt_heimat(chart_data_pfad)
    # 2026-09-19 (F2): unlesbare Tabellenzeilen werden genannt, nie still
    # uebergangen — vorher meldete die Probe gruen ueber eine Pruefmenge, in
    # der eine Zeile fehlte.
    unl = ["  UNLESBARE TABELLENZEILE (nicht in der Pruefmenge): %s: %s"
           % (abschnitt, zeile) for abschnitt, zeile in r.get("unlesbar", [])]
    if unl:
        unl.append("  Erwartete Form: " + _AH_ZEILENFORM)
    if r.get("aussagelos") and unl:
        return "\n".join(["Aspekt-Heimat: KEINE PRUEFUNG MOEGLICH — die "
                          "Aspekttabellen tragen %d Zeile(n), aber keine ist "
                          "lesbar." % (len(unl) - 1)] + unl)
    if r.get("aussagelos"):
        return ("Aspekt-Heimat: KEINE PRUEFUNG MOEGLICH — im chart_data steht "
                "keine Aspekttabelle (weder Volle/Einseitige/Nebenaspekte noch "
                "Hauptaspekte). Bei einem Folgeprodukt (Transit, EA) ist das "
                "normal: dort gilt kontakt_heimat_bericht(chart_data, events_json). "
                "Bei einem Geburtshoroskop ist es ein Fehler im Datenblatt.")
    if r["ok"]:
        return ("Aspekt-Heimat: %d Aspekte, %d mit Heimat, %d dokumentiert "
                "weggelassen, keine Doppelheimat, keine offenen."
                % (r["tabelle"], len(r["mit_heimat"]), len(r["dokumentiert"])))
    L = ["Aspekt-Heimat: FEHLER (%d Aspekte in der Tabelle)." % r["tabelle"]]
    for p in r["offen"]:
        L.append("  OHNE HEIMAT und nicht dokumentiert: %s" % p)
    for p, a, b in r["doppelt"]:
        L.append("  DOPPELTE HEIMAT: %s -> %s / %s" % (p, a, b))
    return "\n".join(L + unl)


# ---------------------------------------------------------------------------
# RESSOURCEN-BLOCK  (neu 2026-09-15, Pruefbericht Geburtshoroskop Schritt 1+2,
# Rubrik 5.6)
#
# Gegenstueck zu transit_rechenschaft_block() fuer den zeitlosen Modus. Der
# Ressourcen-Block des Datenblatts ist eine mechanisch bestimmbare Menge: jeder
# harmonische Aspekt (Konjunktion, Trigon, Sextil) an einem der Faktoren, die
# das Typmodul nennt, nach Enge sortiert, mit Staerkestufe als Merkmal. Bis zu
# diesem Tag wurde er je Lauf von Hand aus der Aspektliste gefiltert — im
# Pruefall 21 Zeilen, jede eine Fehlerquelle, und die Vollstaendigkeit pruefte
# keine Funktion. Genau die Begruendung, mit der die Transit-Funktion gebaut
# wurde.
#
# Die Funktion filtert und sortiert; sie ENTSCHEIDET NICHT. Der Deutungsort
# bleibt Handarbeit und steht als leeres Feld hinter jeder Zeile.
# ---------------------------------------------------------------------------

# Zaehlmenge des Standard-Geburtshoroskops (Typmodul, "Die Ressourcen-Pflicht").
# Andere Typen geben ihre eigene Menge mit; die Mengen selbst stehen in den
# Typmodulen, nicht hier.
RESSOURCEN_FAKTOREN = ("Sonne", "Mond", "Merkur", "Venus", "Mars", "AC", "MC")
_HARMONISCH = {"☌": "Konjunktion", "△": "Trigon", "⚹": "Sextil"}
_STAERKE_KOPF = (("### Volle Aspekte", "voll"),
                 ("### Einseitige Aspekte", "einseitig"),
                 ("### Nebenaspekte", "neben"))


def _ressourcen_zeilen(chart_data_pfad: str, faktoren=None) -> list:
    """Die Rohzeilen der Aspekttabellen als dicts, ungefiltert nach Menge."""
    import re as _re
    txt = open(chart_data_pfad, encoding="utf-8").read()
    # Sechsspaltige Form des Datenblatt-Moduls (Spalte 6 "zugleich" seit
    # 15.09.2026 optional): | Faktor | ☌ Konjunktion | Faktor | 0°41′ | konj | … |
    zeile = _re.compile(
        r"\|\s*(%s)\s*\|\s*([%s])\s*[A-Za-zÄÖÜäöüß]*\s*\|\s*(%s)\s*\|"
        r"\s*(\d{1,3}°\d{2}′)\s*\|" % (_AH_NAME, "".join(_HARMONISCH), _AH_NAME))
    out = []
    for kopf, stufe in _STAERKE_KOPF:
        if kopf not in txt:
            continue
        teil = txt.split(kopf, 1)[1]
        schnitt = _re.search(r"\n#{2,3} ", teil)
        if schnitt:
            teil = teil[:schnitt.start()]
        for z in teil.splitlines():
            m = zeile.match(z)
            if not m:
                continue
            g, mi = m.group(4).split("°")
            out.append({"a": m.group(1), "glyph": m.group(2), "b": m.group(3),
                        "name": _HARMONISCH[m.group(2)], "orb_txt": m.group(4),
                        "orb": int(g) + int(mi.rstrip("′")) / 60.0,
                        "stufe": stufe})
    return out


# Zaehlmenge des Transits (Transit-Modul, „Die Ressourcen-Pflicht des
# Transit-Horoskops"; neu 2026-09-19, W22): die langsamen Transiter, so wie
# events.json sie nennt (`Knoten` = laufender Mondknoten). Mars gehoert nie
# dazu, auch nicht mit --mars.
RESSOURCEN_TRANSITER = ("Jupiter", "Saturn", "Uranus", "Neptun", "Pluto",
                        "Chiron", "Knoten")
_HARMONISCH_NAMEN = ("Trigon", "Sextil", "Konjunktion")


def _ist_knotenrueckkehr(e):
    """L16 (2026-09-19): Transit-Knoten ☌ Radix-Mondknoten ist ein Wendepunkt,
    keine Gabe — er zaehlt nicht zur Ressourcen-Zaehlmenge."""
    return (e.get("transit") == "Knoten" and e.get("aspekt") == "Konjunktion"
            and (e.get("selbst_transit")
                 or e.get("ziel") in ("Mondknoten", "Nordknoten")))


def _gegenenden(fak):
    """Die Gegenenden der Achsen in `fak`, die selbst nicht in `fak` stehen
    (bei RESSOURCEN_FAKTOREN: IC und DC). Ohne radix leer — dann bricht
    _achsen_spiegel_zusammenziehen() ohnehin mit einer klaren Meldung ab."""
    try:
        import radix as _rx
    except Exception:                          # noqa: BLE001
        return set()
    return {_rx._GEGENACHSE[x] for x in fak if x in _rx._GEGENACHSE} - set(fak)


def _zaehlt_fuer_ressource(e, fak):
    """Ein Eintrag zaehlt, wenn ein Ende in `fak` steht oder sein Spiegel
    ('Sextil MC') an einem Ende aus `fak` liegt."""
    if e["a"] in fak or e["b"] in fak:
        return True
    sp = (e.get("spiegel") or "").split()
    return bool(sp) and sp[-1] in fak


def _achsen_spiegel_zusammenziehen(treffer):
    """F18 (2026-09-19): Eine Achsen-Spiegelzeile ist EINE Gabe mit EINEM
    Eintrag (Datenblatt-Modul, geklaert 2026-09-18). Harmonisch trifft ein
    Faktor beide Enden einer Achse nur als Trigon zum einen und Sextil zum
    anderen (Konjunktion/Opposition: die Opposition ist nicht harmonisch).
    Die Aspekttabelle fuehrt solche Paare als zwei Zeilen (Design-Modul: bei
    Huber eigene Klassen), der Ressourcen-Block fuehrte darum zwei Eintraege
    mit je eigenem Deutungsort. Jetzt EIN Eintrag, das andere Ende als
    `spiegel` ('Sextil DC'). Es fuehrt die hoehere Staerkestufe (sie setzt
    die Deutungstiefe), bei gleicher Stufe AC vor DC und MC vor IC — die
    Achsenregel aus radix. Achsenpaare und Rangfolgen kommen aus radix, nicht
    aus einer zweiten Liste hier."""
    if not treffer:
        return []
    try:
        import radix as _rx
    except Exception as fehler:                 # noqa: BLE001
        raise BuildError(
            "ressourcen_liste(): radix.py ist nicht importierbar (%s). Der "
            "Ressourcen-Block braucht radix fuer den Achsen-Spiegel; "
            "lade_schritt('1') laedt radix und build gemeinsam." % fehler)
    gegen, rang = _rx._GEGENACHSE, _rx._STAERKE_RANG
    out, weg = [], set()
    for i, e in enumerate(treffer):
        if i in weg:
            continue
        ach = (e["b"] if _rx.ist_achse(e["b"])
               else (e["a"] if _rx.ist_achse(e["a"]) else None))
        if ach is None or (_rx.ist_achse(e["a"]) and _rx.ist_achse(e["b"])):
            out.append(e)
            continue
        fak = e["a"] if ach == e["b"] else e["b"]
        j = next((j for j in range(i + 1, len(treffer)) if j not in weg
                  and {treffer[j]["a"], treffer[j]["b"]} == {fak, gegen[ach]}),
                 None)
        if j is None:
            out.append(e)
            continue
        weg.add(j)
        f = treffer[j]

        def _vorn(x, achse):
            return (rang.get(x["stufe"], 9),
                    0 if achse in _rx._FUEHRT_QUADRAT else 1)
        if _vorn(f, gegen[ach]) < _vorn(e, ach):
            fuehrt, zweit, z_ach = f, e, ach
        else:
            fuehrt, zweit, z_ach = e, f, gegen[ach]
        r = dict(fuehrt)
        r["spiegel"] = "%s %s" % (zweit["name"], z_ach)
        out.append(r)
    return out


def _transit_ressourcen(events_json_pfad, orb_wirk=None):
    """Die Transit-Zaehlmenge aus events.json (W22, 2026-09-19): jeder
    harmonische Kontakt (Trigon, Sextil, Konjunktion) eines langsamen
    Transiters an einem PRIMAEREN Ziel, im Wirkorb INNERHALB des Fensters
    (`wirkorb_im_fenster`, nicht `im_wirkorb` — das schliesst den Rueckblick
    ein), ohne Mars und ohne Spiegelziele. Ein Kontakt ist EIN Eintrag, auch
    wenn er mehrere Passagen hat. Die Knotenrueckkehr steht getrennt unter
    `nicht_gezaehlt` (L16) — sichtbar, nicht still weggelassen."""
    import json as _json
    daten = _json.load(open(events_json_pfad, encoding="utf-8"))
    orb_json = daten.get("orb_wirk")
    orb = orb_wirk if orb_wirk is not None else (orb_json or 1.5)
    start, end = daten.get("start") or "", daten.get("end") or "9999"
    passagen = {}
    for e in daten.get("events", []):
        if (e.get("spiegel") or not e.get("primaer")
                or e.get("transit") not in RESSOURCEN_TRANSITER
                or e.get("aspekt") not in _HARMONISCH_NAMEN
                or not _wirkorb_im_fenster(e, orb, orb_json)):
            continue
        passagen.setdefault((e["transit"], e["aspekt"], e["ziel"]), []).append(e)
    eintraege, nicht = [], []
    for (t, a, z), sel in passagen.items():
        zeit = _passagen_zeitangaben(sel, start, end)
        label = "T-%s %s R-%s" % (_vertragsname(t),
                                  ASPEKT_ZU_GLYPH.get(a, a), _vertragsname(z))
        eintrag = {"transit": t, "aspekt": a, "ziel": z, "label": label,
                   "orb_f": zeit["orb_f"], "zeit": zeit,
                   "text": _kontakt_zeit_text(zeit, start, end)}
        if any(_ist_knotenrueckkehr(e) for e in sel):
            nicht.append(eintrag)
        else:
            eintraege.append(eintrag)
    def _enge(x):
        per = x["zeit"]["perioden"]
        return (x["orb_f"] if x["orb_f"] is not None else 99.0,
                per[0][0] if per else "9999", x["label"])
    eintraege.sort(key=_enge)
    nicht.sort(key=_enge)
    return {"eintraege": eintraege, "nicht_gezaehlt": nicht,
            "fenster": (start, end), "orb_wirk": orb,
            "primaer": list(daten.get("primary") or [])}


def ressourcen_liste(chart_data_pfad: str, faktoren=None,
                     events_json_pfad: str = None, radix: bool = None,
                     orb_wirk: float = None) -> dict:
    """Die Zaehlmenge des Ressourcen-Blocks, nach Enge sortiert.

    faktoren: Tupel der Punkte, an denen gezaehlt wird. Ohne Angabe die Menge
    des Standard-Geburtshoroskops (RESSOURCEN_FAKTOREN). Die Staerkestufe ist
    ein MERKMAL der Zeile und kein Filter (Datenblatt-Modul, 14.09.2026): Jeder
    harmonische Aspekt zaehlt, die Stufe ordnet nur.

    events_json_pfad (neu 2026-09-19, W22): die events.json aus
    `transit.py --json`. Mit ihr kommt die Transit-Zaehlmenge dazu — jeder
    harmonische Kontakt eines langsamen Transiters (RESSOURCEN_TRANSITER) an
    einem primaeren Ziel, im Wirkorb innerhalb des Fensters, ohne Mars, ohne
    Spiegelziele und ohne die Knotenrueckkehr (L16: ein Wendepunkt, keine
    Gabe; sie steht unter 'nicht_gezaehlt').
    radix: Radix-Aspekte zaehlen? Vorgabe: ja ohne events_json_pfad, nein mit
    — das Transit-Horoskop fuehrt im Block NUR Kontakte (ein uebernommener
    Radix-Block wird ersetzt, Transit-Modul). Das Ultimativ zaehlt beide
    Mengen und gibt radix=True mit.
    orb_wirk: Wirk-Orb; Vorgabe der des transit.py-Laufs (events.json).

    Achsen-Spiegel (F18, 2026-09-19): Trifft ein Faktor beide Enden einer
    Achse harmonisch (Trigon zum einen, Sextil zum anderen), ist das EIN
    Eintrag unter dem fuehrenden Ende; das andere steht als 'spiegel'.

    -> {'faktoren': (...), 'tabelle': n, 'zeilen': [str], 'eintraege': [dict],
        'konjunktionen': [str], 'radix': bool}
       mit events_json_pfad zusaetzlich 'transit': [dict], 'transit_zeilen',
       'nicht_gezaehlt': [dict], 'fenster': (start, end), 'orb_wirk', 'primaer'
    `zeilen` sind alle Zeilen der Menge (erst Radix, dann Transit) mit leerem
    Deutungsort. `konjunktionen` nennt die Konjunktionen der Menge — sie
    bleiben nach der Regel vom 15.09.2026 in der Liste, sind aber nicht in
    jedem Fall eine Gabe und brauchen die Anmerkung darunter. Welche das sind,
    entscheidet die Deutung, nicht diese Funktion.
    """
    if radix is None:
        radix = events_json_pfad is None
    if not radix and not events_json_pfad:
        raise ValueError("ressourcen_liste(): radix=False ohne "
                         "events_json_pfad — dann gibt es nichts zu zaehlen. "
                         "Fuer das Transit-Horoskop events_json_pfad=<events.json> "
                         "angeben.")
    fak = tuple(faktoren or RESSOURCEN_FAKTOREN)
    roh = _ressourcen_zeilen(chart_data_pfad)
    treffer = []
    if radix:
        # 2026-09-23 (Pruefbericht Geburtshoroskop 1+2 vom 22.09.c, Klasse 1
        # Nr. 1): Das Gegenende einer Achse aus `fak` (IC zum MC, DC zum AC)
        # muss mit in den Zusammenzug, sonst sieht er die zweite Zeile eines
        # Faktors ausserhalb von `fak` nie — Trigon IC plus Sextil MC fiel auf
        # „⚹ MC … neben" ohne Spiegel, und die Satzpflicht am Deutungsort sank
        # von drei auf einen Satz. Eine Zeile zum Gegenende zaehlt danach nur,
        # wenn sie Spiegel eines Eintrags an einem Ende aus `fak` geworden ist.
        gegen = _gegenenden(fak)
        kand = [e for e in roh if {e["a"], e["b"]} & (set(fak) | gegen)]
        treffer = [e for e in _achsen_spiegel_zusammenziehen(kand)
                   if _zaehlt_fuer_ressource(e, fak)]
    treffer.sort(key=lambda e: e["orb"])
    zeilen = ["%s %s %s %s %s%s — Deutungsort: "
              % (e["a"], e["glyph"], e["b"], e["orb_txt"], e["stufe"],
                 (" (zugleich %s)" % e["spiegel"]) if e.get("spiegel") else "")
              for e in treffer]
    konj = ["%s %s %s" % (e["a"], e["glyph"], e["b"])
            for e in treffer if e["glyph"] == "☌"]
    out = {"faktoren": fak, "tabelle": len(roh), "zeilen": zeilen,
           "eintraege": treffer, "konjunktionen": konj, "radix": radix}
    if events_json_pfad:
        t = _transit_ressourcen(events_json_pfad, orb_wirk)
        t_zeilen = ["%s · %s — Deutungsort: " % (e["label"], e["text"])
                    for e in t["eintraege"]]
        out.update({"transit": t["eintraege"], "transit_zeilen": t_zeilen,
                    "nicht_gezaehlt": t["nicht_gezaehlt"],
                    "fenster": t["fenster"], "orb_wirk": t["orb_wirk"],
                    "primaer": t["primaer"]})
        out["zeilen"] = zeilen + t_zeilen
        out["konjunktionen"] = konj + [e["label"] for e in t["eintraege"]
                                       if e["aspekt"] == "Konjunktion"]
    return out


def ressourcen_block(chart_data_pfad: str, faktoren=None,
                     events_json_pfad: str = None, radix: bool = None,
                     orb_wirk: float = None) -> str:
    """Der fertige Abschnitt `## Ressourcen` — 1:1 ins chart_data.

    Gehoert hinter die Themenliste und vor den Abschnitt „Aspekte ohne
    Deutungs-Heimat". Der Deutungsort bleibt hinter jeder Zeile leer und wird
    von Hand gesetzt; ohne ihn ist der Block unfertig (Datenblatt-Modul).
    Parameter wie ressourcen_liste(): im Transit-Horoskop
    `ressourcen_block(chart_data, events_json_pfad=<events.json>)` — dann
    traegt der Block nur die Transit-Zaehlmenge (W22, 2026-09-19); im
    Ultimativ zusaetzlich radix=True.
    """
    r = ressourcen_liste(chart_data_pfad, faktoren, events_json_pfad, radix,
                         orb_wirk)
    L = ["## Ressourcen", ""]
    if r["radix"]:
        satz = ("Zählmenge: jeder harmonische Aspekt (Trigon, Sextil, "
                "Konjunktion) an "
                + ", ".join(r["faktoren"][:-1]) + " oder " + r["faktoren"][-1]
                + " — ohne Stärkefilter, die Stufe steht als Merkmal in der "
                  "Zeile und ordnet nur die Reihenfolge. Sortiert nach Enge.")
        if any(e.get("spiegel") for e in r["eintraege"]):
            satz += (" Ein Achsen-Spiegel (derselbe Faktor im Trigon zum einen "
                     "und im Sextil zum anderen Ende einer Achse) ist EIN "
                     "Eintrag unter dem führenden Ende; das andere steht in "
                     "Klammern.")
        L += [satz, ""]
        L += r["zeilen"][:len(r["eintraege"])]
    if "transit" in r:
        if r["radix"]:
            L += [""]
        prim = ", ".join(r["primaer"]) if r["primaer"] else "laut events.json"
        L += ["Zählmenge (Transit): jeder harmonische Kontakt (Trigon, Sextil, "
              "Konjunktion) eines langsamen Transiters (Jupiter, Saturn, "
              "Uranus, Neptun, Pluto, Chiron, Mondknoten) an einem primären "
              "Ziel (%s), im Wirkorb (%s°) innerhalb des Fensters %s–%s — ohne "
              "Mars, ohne Spiegelziele und ohne die Knotenrückkehr (ein "
              "Wendepunkt, keine Gabe). Sortiert nach Enge (engster Orb im "
              "Fenster)." % (prim, r["orb_wirk"], _datum_de(r["fenster"][0]),
                              _datum_de(r["fenster"][1])), ""]
        L += r["transit_zeilen"] or ["— (kein Kontakt der Zählmenge im "
                                     "Fenster)"]
        if r["nicht_gezaehlt"]:
            L += ["", "Nicht in der Zählmenge (die Knotenrückkehr ist ein "
                      "Wendepunkt, keine Gabe):"]
            L += ["- %s · %s" % (e["label"], e["text"])
                  for e in r["nicht_gezaehlt"]]
    if r["konjunktionen"]:
        kopf = ("Konjunktionen der Menge (bleiben in der Liste; je Zeile "
                "Gabe: ja — oder nein mit Begründung):")
        if r.get("transit") and any(e["aspekt"] == "Konjunktion"
                                    for e in r["transit"]):
            kopf = kopf[:-2] + ("; Transit-Modul: eine Konjunktion zählt nur, "
                                "wenn der Transiter sie trägt — eine Saturn- "
                                "oder Pluto-Konjunktion ist eine "
                                "Verdichtung):")
        L += ["", kopf]
        L += ["- %s — Gabe: " % k for k in r["konjunktionen"]]
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Selbsttest (neu 2026-09-19, Wartungslauf A) — python3 build.py --selbsttest
# Nur konstruierte Daten: erfundene Aspekttabellen und ein erfundenes
# events.json (Fenster ab 2031), keine Person, kein Echtfall.
# ---------------------------------------------------------------------------

def _selbsttest():
    import contextlib
    import io
    import json
    import pathlib
    import shutil
    import tempfile

    fehler = []

    def pruefe(bed, text):
        if not bed:
            fehler.append(text)

    tmp = tempfile.mkdtemp(prefix="build_selbsttest_")

    def datei(name, text):
        p = os.path.join(tmp, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    def still(fn, *a, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            wert = fn(*a, **kw)
        return wert, buf.getvalue()

    try:
        # --- W2: eine Orb-Rundung ------------------------------------------
        pruefe(orb_text(0.4917) == "0°30′", "W2: 0.4917 -> %s" % orb_text(0.4917))
        pruefe(orb_text(1.4917) == "1°30′", "W2: 1.4917 -> %s" % orb_text(1.4917))
        pruefe(orb_text(round(1.4917, 2)) == "1°29′",
               "W2: Doppelrundung nicht nachgestellt")
        pruefe(orb_text(29.9999) == "30°00′", "W2: Uebertrag bei 60′")
        try:
            import radix as _rx
            abw = [i for i in range(0, 30 * 3600, 7)
                   if orb_text(i / 3600.0) != _rx._gr(i / 3600.0)]
            pruefe(not abw, "W2: orb_text weicht von radix._gr ab bei %s"
                   % abw[:3])
        except ImportError:
            print("  (W2: radix nicht ladbar — Abgleich mit radix._gr "
                  "uebersprungen)")

        # --- W14: unbekannte Felder im @@DECKBLATT-Block -------------------
        cd = datei("deck_chart_data.md", "\n".join([
            "# konstruiert", "@@DECKBLATT", "LEITSATZ: Ein Satz.",
            "LEITACHSE: Eine Achse.", "TITELMOTIV: Ein Motiv,",
            "  das weiterlaeuft.", "KICKER: Transit-Horoskop",
            "Untertitel: Zweite Zeile", "  Folgezeile des Untertitels",
            "PALETTE: dunkel", "FARBE: rot", "GLYPHEN: ♄ ☉", "@@ENDE", ""]))
        deck, aus = still(lies_deckblatt, cd)
        pruefe(deck["TITELMOTIV"] == "Ein Motiv, das weiterlaeuft.",
               "W14: TITELMOTIV verschmutzt: %r" % deck["TITELMOTIV"])
        pruefe(deck["PALETTE"] == "dunkel" and deck["GLYPHEN"] == "♄ ☉",
               "W14: PALETTE/GLYPHEN verschmutzt: %r / %r"
               % (deck["PALETTE"], deck["GLYPHEN"]))
        pruefe(set(deck) == set(DECKBLATT_FELDER + DECKBLATT_ABGELEITET),
               "W14: Rueckgabeschluessel veraendert")
        pruefe(aus.count("!! @@DECKBLATT") == 3 and '"KICKER:"' in aus
               and '"Untertitel:"' in aus and '"FARBE:"' in aus
               and "Dokumenttyp" in aus and "Tippfehler" in aus,
               "W14: Warnungen fehlen oder unklar: %r" % aus[:300])

        # --- W61: parse_analyse nimmt Pfad ODER Text -------------------------
        text = ("# Transit-Horoskop — Alex Muster\n\n"
                "## Kapitel 1 · Ein Titel\n\nEin Absatz, der endet.\n")
        pa = datei("x_analyse.md", text)
        p1, p2, p3 = (parse_analyse(pa), parse_analyse(text),
                      parse_analyse(pathlib.Path(pa)))
        pruefe(p1 == p2 == p3 and p1["chapters"][0]["title"] == "Ein Titel",
               "W61: Pfad, Text und Path lesen verschieden")
        try:
            parse_analyse("x" * 100000)
            pruefe(False, "W61: langer Nicht-Pfad ohne Fehler")
        except FileNotFoundError as e:
            pruefe(len(str(e)) < 600 and "Datei nicht gefunden" in str(e)
                   and "Text" in str(e), "W61: Meldung unklar/zu lang (%d)"
                   % len(str(e)))
        try:
            parse_analyse(123)
            pruefe(False, "W61: Zahl statt Pfad ohne Fehler")
        except TypeError as e:
            pruefe("Pfad" in str(e), "W61: TypeError ohne Erklaerung")
        try:
            parse_analyse(text.replace("Ein Absatz, der endet.", "ohne Ende"))
            pruefe(False, "W61: Schemafehler im Text nicht erkannt")
        except SchemaError as e:
            pruefe("als Text übergeben" in str(e), "W61: Quelle in der "
                   "Schemameldung fehlt")

        # --- F2 und W9: Aspekt-Heimat -------------------------------------
        tab = "\n".join([
            "### Volle Aspekte (2)", "",
            "| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |",
            "|---|---|---|---|---|---|",
            "| Sonne | △ Trigon | Mond | 1°00′ | blau |  |",
            "| Venus | △ Trigon | Saturn | 2°00′ | blau |  |", "",
            "### Untergrund-Aspekte (2)", "",
            "| Faktor | Aspekt | Faktor | Orb |", "|---|---|---|---|",
            "| Merkur | ∠ Halbquadrat | Venus | 0°40′ |",
            "| Mars | ⚼ Anderthalbquadrat | Jupiter | 1°10′ |", "",
            "## Themenliste", ""])
        th1 = ("THEMA 1 | titel=Eins | fuehrt=Sonne Krebs H4 | aspekte=Sonne "
               "△ Mond, Merkur –Halbquadrat– Venus | grund=Venus △ Saturn "
               "traegt mit | rang=1\n")
        th2 = ("THEMA 2 | titel=Zwei | fuehrt=Mars Widder H1 | aspekte=Mars "
               "–Anderthalbquadrat– Jupiter | rang=2\n")
        schluss = "\nRECHENSCHAFT: konstruiert.\nGESTRICHEN: keine.\n"
        r = aspekt_heimat(datei("g1.md", tab + th1 + th2 + schluss))
        pruefe(r["tabelle"] == 4 and r["offen"] == ["Saturn — Venus"]
               and not r["ok"], "W9: grund= als Heimat gezaehlt: %r" % r)
        th2b = th2.replace("Jupiter |", "Jupiter, Venus △ Saturn |")
        r = aspekt_heimat(datei("g2.md", tab + th1 + th2b + schluss))
        pruefe(r["ok"] and r["tabelle"] == 4 and not r["unlesbar"]
               and "Merkur — Venus" in r["mit_heimat"],
               "F2: lesbare Tabelle nicht gruen: %r" % r)
        r = aspekt_heimat(datei("g3.md", tab.replace("⚼", "∡") + th1 + th2b
                                + schluss))
        b = aspekt_heimat_bericht(os.path.join(tmp, "g3.md"))
        pruefe(r["tabelle"] == 3 and len(r["unlesbar"]) == 1 and not r["ok"]
               and "UNLESBARE TABELLENZEILE" in b and "∡" in b and "⚼" in b,
               "F2: unlesbare Zeile nicht gemeldet: %r / %s" % (r, b))

        # --- W7, W9, L19, W22, L16: Transit mit konstruiertem events.json ---
        S0, E0 = "2031-01-01", "2032-12-31"

        def ev(t, a, z, **kw):
            e = dict(transit=t, aspekt=a, ziel=z, exakt=[], exakt_im_fenster=[],
                     exakt_vor_start=[], fast_exakt=[], min_orb_grad=0.5,
                     im_wirkorb=True, fenster_von=S0, fenster_bis=E0,
                     weit_von=S0, weit_bis=E0, dauer_tage=90, dauer_monate=3.0,
                     perioden=[[S0, "2031-04-01"]], kontakte=0, mehrfach=False,
                     quartale=[1], primaer=True, spiegel=False, wird_exakt=False,
                     annaeherung=[], wirkorb_perioden=[[S0, "2031-04-01"]],
                     min_orb_im_fenster=0.5, wirkorb_im_fenster=True,
                     orb_stichtag=1.0, selbst_transit=False, vorlauf=None,
                     beginn_abgeschnitten=False, fortsetzung=None,
                     exakt_nach_fenster=[], exakt_gesamt=[],
                     wirkorb_von_gesamt=S0, wirkorb_bis_gesamt="2031-04-01")
            e.update(kw)
            if e["exakt_im_fenster"] or e["exakt_vor_start"]:
                e["exakt"] = sorted(e["exakt_vor_start"] + e["exakt_im_fenster"])
            e["exakt_gesamt"] = sorted(set(e["exakt"] + e["exakt_nach_fenster"]
                                           + e["exakt_gesamt"]))
            return e

        events = [
            ev("Saturn", "Quadrat", "Sonne", exakt_im_fenster=["2031-03-02"],
               min_orb_grad=0.0, min_orb_im_fenster=0.0),
            ev("Jupiter", "Trigon", "Mond", exakt_im_fenster=["2031-06-10"],
               min_orb_grad=0.0, min_orb_im_fenster=0.0,
               wirkorb_perioden=[["2031-05-01", "2031-07-20"]]),
            ev("Neptun", "Sextil", "MC", min_orb_grad=0.4, min_orb_im_fenster=0.4,
               exakt_nach_fenster=["2033-02-11"],
               wirkorb_perioden=[["2032-11-14", E0]],
               wirkorb_von_gesamt="2032-11-14", wirkorb_bis_gesamt="2033-03-30",
               fortsetzung={"exakt": ["2033-02-11"], "annaeherung": []}),
            ev("Pluto", "Sextil", "Sonne", exakt_vor_start=["2030-09-13"],
               min_orb_grad=0.0, min_orb_im_fenster=0.738,
               wirkorb_perioden=[["2030-08-01", "2031-02-10"]],
               wirkorb_von_gesamt="2030-08-01", wirkorb_bis_gesamt="2031-02-10"),
            ev("Pluto", "Sextil", "Sonne", min_orb_grad=2.847,
               min_orb_im_fenster=2.847, im_wirkorb=False,
               wirkorb_im_fenster=False, wirkorb_perioden=[], quartale=[7],
               wirkorb_von_gesamt=None, wirkorb_bis_gesamt=None),
            ev("Uranus", "Trigon", "Venus", min_orb_grad=0.03,
               min_orb_im_fenster=0.03, annaeherung=[["2031-05-06", 0.0295]],
               wirkorb_perioden=[["2031-03-01", "2031-08-01"]]),
            ev("Chiron", "Konjunktion", "Venus", min_orb_grad=0.61,
               min_orb_im_fenster=0.61,
               wirkorb_perioden=[["2032-02-01", "2032-05-01"]]),
            ev("Knoten", "Konjunktion", "Mondknoten", selbst_transit=True,
               exakt_im_fenster=["2031-10-05"], min_orb_grad=0.0,
               min_orb_im_fenster=0.0),
            ev("Mars", "Trigon", "Sonne", exakt_im_fenster=["2031-04-04"],
               min_orb_grad=0.0, min_orb_im_fenster=0.0),
            ev("Jupiter", "Sextil", "Merkur", primaer=False),
            ev("Saturn", "Sextil", "DC", spiegel=True),
            ev("Jupiter", "Konjunktion", "Sonne", exakt_vor_start=["2030-08-20"],
               min_orb_grad=0.0, min_orb_im_fenster=None,
               wirkorb_im_fenster=False, quartale=[0],
               wirkorb_perioden=[["2030-08-01", "2030-09-10"]]),
        ]
        evj = datei("t_events.json", json.dumps({
            "start": S0, "end": E0, "asof": "2031-02-14",
            "lookback_start": "2030-07-01", "orb_wirk": 1.5, "orb_weit": 3.0,
            "primary": ["Sonne", "Mond", "Venus", "MC", "Mondknoten"],
            "jetzt": {"stichtag": "2031-02-14"}, "events": events},
            ensure_ascii=False))
        themen = (
            "# Transit-Datenblatt (konstruiert)\n\n## Themenliste\n\n"
            "THEMA 1 | titel=Erstes Thema | fuehrt=T-Saturn □ R-Sonne | "
            "aspekte=T-Jupiter △ R-Mond | klingt=T-Neptun ⚹ R-MC | rang=2\n"
            "THEMA 2 | titel=Zweites Thema | aspekte=T-Mondknoten ☌ R-Mondknoten\n"
            "  | grund=T-Chiron ☌ R-Venus traegt mit | rang=1\n\n"
            "RECHENSCHAFT: konstruiert.\nGESTRICHEN: keine.\n")
        t1 = datei("t1_Transit_chart_data.md", themen)
        k = kontakt_heimat(t1, evj)
        ohne = {x.split()[0] for x in k["ohne_heimat"]}
        pruefe(k["kontakte"] == 8 and k["in_themen"] == 3 and not k["unbekannt"]
               and ohne == {"Neptun", "Pluto", "Uranus", "Chiron", "Mars"},
               "W9/L19: Heimat falsch: %r" % k)
        tr, _ = still(transit_rechenschaft, t1, evj)
        z = {x.split()[1].replace("T-", ""): x for x in tr["zeilen"]}
        pruefe(tr["typ"] == "transit" and len(tr["zeilen"]) == 5,
               "W7: Zahl/Typ der Zeilen: %r" % tr)
        pruefe("exakt nach dem Fenster 11.02.2033" in z["Neptun"]
               and "nie exakt" not in z["Neptun"] and "streift" not in z["Neptun"]
               and "bis 30.03.2033, nach dem Fenster" in z["Neptun"],
               "W7: Kontakt, der nach dem Fenster exakt wird: %s" % z["Neptun"])
        pruefe("exakt vor dem Fenster 13.09.2030" in z["Pluto"]
               and "0.738°" in z["Pluto"] and "2.847" not in z["Pluto"]
               and "begonnen 01.08.2030" in z["Pluto"],
               "W7: 0,0-Fehler/Orb im Fenster: %s" % z["Pluto"])
        pruefe("Annäherung bis 1.8′ am 06.05.2031" in z["Uranus"]
               and "exakt 0" not in z["Uranus"], "W7: Annaeherung: %s" % z["Uranus"])
        pruefe("nie exakt (engster Orb im Fenster 0.61°)" in z["Chiron"],
               "W7: nie exakt: %s" % z["Chiron"])
        pruefe(all("Momentaufnahme" not in x and "ohne eigenes Kapitel" in x
                   for x in tr["zeilen"]), "W7: Transit-Wortlaut")
        pruefe([x.split()[1] for x in tr["zeilen"]]
               == ["T-Pluto", "T-Mars", "T-Uranus", "T-Neptun", "T-Chiron"],
               "W7: Sortierung: %r" % [x.split()[1] for x in tr["zeilen"]])
        tr_ea, _ = still(transit_rechenschaft, t1, evj, typ="ea")
        pruefe(all("Momentaufnahme" in x or "streift" in x
                   for x in tr_ea["zeilen"]), "W7: EA-Wortlaut")
        # EA: Stichtags-Orb = die Zahl der JETZT-Liste (zwei Stellen), sonst
        # „über orb_weit" (nicht in der Liste) bzw. „offen" (keine Liste).
        pl = [x for x in tr_ea["zeilen"] if x.startswith("- T-Pluto")][0]
        pruefe("Orb am Stichtag offen" in pl, "W7: EA ohne Jetzt-Liste: %s" % pl)
        d_ev = json.load(open(evj, encoding="utf-8"))
        for liste, soll in (([{"transit": "Pluto", "aspekt": "Sextil",
                               "ziel": "Sonne", "orb_grad": 0.62}],
                             "Orb am Stichtag 0.62°"),
                            ([], "Orb am Stichtag über 3.0°")):
            d_ev["jetzt"] = {"stichtag": "2031-02-14", "orb_weit": 3.0,
                             "im_orb": liste}
            evj2 = datei("t_events_jetzt.json", json.dumps(d_ev))
            pl = [x for x in still(transit_rechenschaft, t1, evj2,
                                   typ="ea")[0]["zeilen"]
                  if x.startswith("- T-Pluto")][0]
            pruefe(soll in pl, "W7: EA-Stichtagsorb: %s" % pl)
        pruefe(_rechenschaft_typ(datei("t_ea.md", themen.replace(
            "| rang=1", "| teil=jetzt | rang=1")), None) == "ea",
            "W7: EA nicht erkannt")
        block, _ = still(transit_rechenschaft_block, t1, evj)
        pruefe(block.startswith("TRANSIT-RECHENSCHAFT: 8 primaere Wirkorb-Kontakte "
                                "im Fenster 01.01.2031–31.12.2032, 3 tragen"),
               "W7: Kopfzeile: %s" % block[:120])

        # W22 / L16: Ressourcen-Zaehlmenge des Transits
        rr = ressourcen_liste(t1, events_json_pfad=evj)
        pruefe([e["label"] for e in rr["transit"]]
               == ["T-Jupiter △ R-Mond", "T-Uranus △ R-Venus", "T-Neptun ⚹ R-MC",
                   "T-Chiron ☌ R-Venus", "T-Pluto ⚹ R-Sonne"]
               and not rr["eintraege"] and not rr["radix"],
               "W22: Zaehlmenge: %r" % [e["label"] for e in rr["transit"]])
        pruefe([e["label"] for e in rr["nicht_gezaehlt"]]
               == ["T-Mondknoten ☌ R-Mondknoten"], "L16: Knotenrueckkehr")
        pruefe(rr["konjunktionen"] == ["T-Chiron ☌ R-Venus"], "W22: Konjunktionen")
        rb = ressourcen_block(t1, events_json_pfad=evj)
        pruefe("Zählmenge (Transit)" in rb and "Nicht in der Zählmenge" in rb
               and "- T-Chiron ☌ R-Venus — Gabe: " in rb
               and "Saturn- oder Pluto-Konjunktion" in rb
               and "T-Mars" not in rb and "Merkur" not in rb,
               "W22: Block: %s" % rb[:300])

        # W9: Block eingefuegt -> gruen; Negativkontrollen -> rot
        voll = datei("t2_Transit_chart_data.md", themen + "\n" + block + "\n\n"
                     + rb + "\nDeckel: Transit Chiron ☌ Venus ausgedeutet.\n")
        k = kontakt_heimat(voll, evj)
        pruefe(k["ok"] and k["rechenschaft"] == 5, "W9: mit Block nicht gruen: %r" % k)
        ohne_chiron = "\n".join(x for x in open(voll, encoding="utf-8").read()
                                .splitlines() if not x.startswith("- T-Chiron ☌"))
        k = kontakt_heimat(datei("t3.md", ohne_chiron + "\n"), evj)
        pruefe(not k["ok"] and k["ohne_heimat"] == ["Chiron Konjunktion Venus"],
               "W9: Negativkontrolle (Ressourcen-/Deckelzeile) blieb gruen: %r"
               % k["ohne_heimat"])
        falsche_art = "\n".join(
            ("- T-Pluto □ R-Sonne — Testzeile" if x.startswith("- T-Pluto ⚹")
             else x) for x in open(voll, encoding="utf-8").read().splitlines())
        k = kontakt_heimat(datei("t4.md", falsche_art + "\n"), evj)
        pruefe(k["ohne_heimat"] == ["Pluto Sextil Sonne"],
               "W9: Zeile einer anderen Aspektart verbucht: %r" % k["ohne_heimat"])
        doppel = themen.replace("RECHENSCHAFT:", "THEMA 3 | titel=Drittes | "
                                "aspekte=T-Saturn □ R-Sonne\n\nRECHENSCHAFT:")
        k = kontakt_heimat(datei("t5.md", doppel), evj)
        pruefe(len(k["doppelt"]) == 1 and "Saturn" in k["doppelt"][0][0],
               "L19: fuehrt=/aspekte=-Doppelheimat nicht gemeldet: %r" % k["doppelt"])
        unb = themen.replace("T-Jupiter △ R-Mond", "T-Jupiter △ R-Mondd")
        b = kontakt_heimat_bericht(datei("t6.md", unb), evj)
        pruefe("in events.json kein solcher Kontakt" in b, "W9: Meldung unbekannt")
        # Ultimativ: Kontakte direkt auf der Pflichtzeile SAMMELKAPITEL: —
        # der Rest der Kopfzeile gehoert zum Block.
        sk = ("SAMMELKAPITEL: T-Neptun ⚹ R-MC, T-Pluto ⚹ R-Sonne, "
              "T-Uranus △ R-Venus, T-Chiron ☌ R-Venus, T-Mars △ R-Sonne\n")
        k = kontakt_heimat(datei("u1.md", themen.replace(
            "GESTRICHEN: keine.", "GESTRICHEN: keine.\n" + sk)), evj)
        pruefe(k["ok"] and k["rechenschaft"] == 5,
               "W9: SAMMELKAPITEL-Zeile nicht gelesen: %r" % k["ohne_heimat"])
        # Mehrere Kontakte auf einer Zeile: Chiron und Venus stehen nur in
        # ZWEI verschiedenen Kontakten — das ist nicht Chiron ☌ Venus.
        quer = sk.replace("T-Chiron ☌ R-Venus", "T-Chiron △ R-Mond, T-Saturn ☌ R-Venus")
        pq = datei("u2.md", themen.replace("GESTRICHEN: keine.",
                                           "GESTRICHEN: keine.\n" + quer))
        k = kontakt_heimat(pq, evj)
        pruefe(k["ohne_heimat"] == ["Chiron Konjunktion Venus"],
               "W9: Kontakt ueber Nachbarkontakte verbucht: %r" % k["ohne_heimat"])
        pruefe("Gelesen wird: Heimat in fuehrt= und aspekte=" in
               kontakt_heimat_bericht(pq, evj), "W9: Lesehinweis im Bericht fehlt")

        # --- F18: Achsen-Spiegel im Ressourcen-Block (Radix) ----------------
        rtab = "\n".join([
            "### Volle Aspekte (3)", "",
            "| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |",
            "|---|---|---|---|---|---|",
            "| Venus | △ Trigon | AC | 1°00′ | blau |  |",
            "| Mond | ⚹ Sextil | MC | 2°10′ | blau |  |",
            "| Mond | △ Trigon | IC | 2°10′ | blau |  |", "",
            "### Nebenaspekte (1)", "",
            "| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |",
            "|---|---|---|---|---|---|",
            "| Venus | ⚹ Sextil | DC | 1°00′ | blau |  |", ""])
        rg = datei("r_chart_data.md", rtab)
        try:
            rl = ressourcen_liste(rg)
            pruefe(rl["zeilen"] == [
                "Venus △ AC 1°00′ voll (zugleich Sextil DC) — Deutungsort: ",
                "Mond ⚹ MC 2°10′ voll (zugleich Trigon IC) — Deutungsort: "],
                "F18: %r" % rl["zeilen"])
            pruefe("EIN Eintrag" in ressourcen_block(rg), "F18: Kopfsatz")
            # 2026-09-23: Faktor AUSSERHALB der Menge — das Gegenende muss in
            # den Zusammenzug; eine einzelne Zeile zum DC zaehlt nicht.
            rtab2 = "\n".join([
                "### Volle Aspekte (1)", "",
                "| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |",
                "|---|---|---|---|---|---|",
                "| Jupiter | △ Trigon | IC | 1°20′ | blau |  |", "",
                "### Nebenaspekte (2)", "",
                "| Faktor | Aspekt | Faktor | Orb | Farbe | zugleich |",
                "|---|---|---|---|---|---|",
                "| Jupiter | ⚹ Sextil | MC | 1°20′ | blau |  |",
                "| Saturn | ⚹ Sextil | DC | 0°40′ | blau |  |", ""])
            rl2 = ressourcen_liste(datei("r2_chart_data.md", rtab2))
            pruefe(rl2["zeilen"] == [
                "Jupiter △ IC 1°20′ voll (zugleich Sextil MC) — Deutungsort: "],
                "F18/Gegenende: %r" % rl2["zeilen"])
            beide = ressourcen_liste(rg, events_json_pfad=evj, radix=True)
            pruefe(len(beide["eintraege"]) == 2 and len(beide["transit"]) == 5
                   and len(beide["zeilen"]) == 7, "W22: Ultimativ (radix=True)")
        except BuildError as e:
            print("  (F18: radix nicht ladbar — uebersprungen: %s)" % e)

        # --- W47 und W61: verify() ------------------------------------------
        _selbsttest_verify(tmp, pruefe)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # --- W57-Nachzug 2026-09-22: englische Sprachfassung -------------------
    for s in ('Sounds in Chapter 2.', 'Klingt mit in Kapitel 2.'):
        if not _ORD_REF_DIREKT_RE.search(s):
            fehler.append("W57: Einzelverweis nicht erkannt: %r" % s)
    for s in ('Sounds in Chapters 2 and 6.', 'Klingt mit in den Kapiteln 2, 7 und 10.'):
        if not _ORD_REF_KETTE_RE.search(s):
            fehler.append("W57: Verweiskette nicht erkannt: %r" % s)
    if _ORD_REF_DIREKT_RE.search('und dann 2.'):
        fehler.append("W57: Verweis ohne Bezugswort wird durchgelassen")
    for lab in ('B E L E G:', 'E V I D E N C E:', 'BELEG:', 'EVIDENCE:'):
        if not _FUSS_LABEL_RE.match(lab):
            fehler.append("W57: Fusslabel nicht erkannt: %r" % lab)
    if _FUSS_LABEL_RE.match('Belege:'):
        fehler.append("W57: Fusslabel greift zu weit (Belege:)")
    if _pflicht_kandidaten('Inhalt') != ('Inhalt', 'Contents'):
        fehler.append("W57: Pflicht-Kandidaten deutsch->englisch falsch")
    if _pflicht_kandidaten('Contents') != ('Contents', 'Inhalt'):
        fehler.append("W57: Pflicht-Kandidaten englisch->deutsch falsch")
    if _pflicht_kandidaten('Bodygraph') != ('Bodygraph',):
        fehler.append("W57: Titel ohne Paar bekommt Kandidaten dazu")

    if fehler:
        print("Selbsttest build.py: %d Fehler" % len(fehler))
        for f_ in fehler:
            print("  - " + f_)
        raise SystemExit(1)
    print("Selbsttest build.py: alle Faelle gruen (W2, W7, W9, L19, W14, W22, "
          "W57, "
          "L16, F18, F2, W47, W61)")


def _selbsttest_verify(tmp, pruefe):
    """W47/W61 am gerenderten Mini-PDF: Ein Querverweis „Kapitel 2, ‚Titel‘"
    im Lagebild darf nicht als Kapitelanfang gelten; `ok` im Report."""
    try:
        import weasyprint
        subprocess.run(["pdftotext", "-v"], capture_output=True, check=False)
    except Exception as e:                      # noqa: BLE001
        print("  (W47/W61: WeasyPrint/pdftotext fehlt — verify-Teil "
              "uebersprungen: %s)" % e)
        return

    def seite(kicker, titel, text):
        return ('<section><div class="kicker">%s</div><h2>%s</h2><p>%s</p>'
                '</section>' % (kicker, titel, text))
    css = ("@page { size: A5; margin: 1.5cm; @top-right { content: "
           "string(kk, start); font-size: 7pt } } .kicker { text-transform: "
           "uppercase; letter-spacing: 0.3em; string-set: kk content() } "
           "section { break-before: page } h2 { font-size: 15pt }")
    lage = seite("Der Stand heute", "Wo du gerade stehst",
                 "Was in Kapitel 2, „Rückenwind im Auftreten“, beschrieben "
                 "wird, beginnt früh; Kapitel 1 · Das eigene Maß folgt.")
    k1 = seite("Kapitel 1", "Das eigene Maß", "Text eins.")
    k2 = seite("Kapitel 2", "Rückenwind im Auftreten", "Text zwei.")
    k3 = seite("Kapitel 3", "Ein sehr langer Titel, der in dieser schmalen "
               "Spalte sicher auf eine zweite Zeile umbricht", "Text drei.")
    marker = [("Der Stand heute", "Wo du gerade stehst"),
              ("Kapitel 1", "Das eigene Maß"),
              ("Kapitel 2", "Rückenwind im Auftreten"),
              ("Kapitel 3", "Ein sehr langer Titel, der in dieser schmalen "
                            "Spalte sicher auf eine zweite Zeile umbricht")]

    def pdf(name, *teile):
        p = os.path.join(tmp, name)
        weasyprint.HTML(string="<html><head><style>%s</style></head><body>%s"
                        "</body></html>" % (css, "".join(teile))).write_pdf(p)
        return p

    import contextlib
    import io as _io
    aus = _io.StringIO()
    with contextlib.redirect_stdout(aus):
        rep = verify(pdf("gut.pdf", lage, k1, k2, k3), markers=marker,
                     sample_page=None)
    pruefe(rep.get("ok") is True and rep["marker_pages"] == {
        "Wo du gerade stehst": 1, "Das eigene Maß": 2,
        "Rückenwind im Auftreten": 3, marker[3][1]: 4},
        "W47: Marken falsch verortet: %r" % rep["marker_pages"])
    ohne_kopf = k2.replace("<h2>Rückenwind im Auftreten</h2>", "")
    try:
        with contextlib.redirect_stdout(aus):
            verify(pdf("ohne.pdf", lage, k1, ohne_kopf, k3), markers=marker,
                   sample_page=None)
        pruefe(False, "W47: fehlende Ueberschrift nicht erkannt (Querverweis "
                      "als Kapitelanfang gewertet)")
    except VerifyError as e:
        pruefe("nicht am Kapitelkopf" in str(e) and "Rückenwind" in str(e)
               and getattr(e, "report", {}).get("ok") is False,
               "W47/W61: Meldung oder report.ok falsch: %s" % e)
    try:
        with contextlib.redirect_stdout(aus):
            verify(pdf("folge.pdf", lage, k2, k1, k3), markers=marker,
                   sample_page=None)
        pruefe(False, "W47: vertauschte Kapitel nicht erkannt")
    except VerifyError as e:
        pruefe("REIHENFOLGE" in str(e), "W47: Reihenfolge-Meldung: %s" % e)


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


if __name__ == "__main__" and "--selbsttest" in sys.argv[1:]:
    _selbsttest()


if __name__ == "__main__" and _hilfe_cli():   # python3 build.py --hilfe [<name>]
    sys.exit(0)
