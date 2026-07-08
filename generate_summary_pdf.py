#!/usr/bin/env python3
"""Generate FirstPass_Summary.pdf — a polished, clickable summary doc."""

from fpdf import FPDF
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

# Brand colours
INK   = (21, 23, 28)
DIM   = (90, 100, 114)
FAINT = (138, 147, 160)
WHITE = (255, 255, 255)
SOFT  = (245, 246, 248)
ACC   = (255, 102, 51)     # PortSwigger orange
ACC2  = (225, 78, 18)
GREEN = (18, 161, 80)
AMBER = (192, 124, 0)
RED   = (222, 50, 38)
GREEN_T = (231, 246, 238)
AMBER_T = (251, 242, 220)
RED_T   = (251, 233, 231)
BLUE   = (47, 111, 176)
BLUE_T = (232, 241, 251)

GITHUB = "https://github.com/Abdelrhman-Rayis/FirstPass"
DECK_PDF  = f"{GITHUB}/blob/main/deck/FirstPass_PortSwigger.pdf"
DECK_PPTX = f"{GITHUB}/blob/main/deck/FirstPass_PortSwigger.pptx"


class SummaryPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(False)
        self.add_font("ArialUni", "", "/Library/Fonts/Arial Unicode.ttf", uni=True)
        self.add_font("ArialUni", "B", "/Library/Fonts/Arial Unicode.ttf", uni=True)

    # ---- helpers ----
    def _pill(self, x, y, w, text, bg, fg):
        self.set_fill_color(*bg)
        self.set_text_color(*fg)
        self.set_font("ArialUni", "B", 11)
        r = 4  # corner radius (simulated with rect)
        self.rect(x, y, w, 7, "F")
        self.set_xy(x, y + 0.8)
        self.cell(w, 5.5, text, align="C")

    def _badge(self, x, y, text, bg, fg, w=36):
        self.set_fill_color(*bg)
        self.set_text_color(*fg)
        self.set_font("ArialUni", "B", 10)
        self.rect(x, y, w, 7, "F")
        self.set_xy(x, y + 0.8)
        self.cell(w, 5.5, text, align="C")

    def _metric(self, x, y, w, big, lbl, color):
        self.set_fill_color(*SOFT)
        self.set_draw_color(200, 200, 206)
        self.rect(x, y, w, 24, "DF")
        self.set_text_color(*color)
        self.set_font("ArialUni", "B", 22)
        self.set_xy(x + 4, y + 2)
        self.cell(w - 8, 10, big, align="L")
        self.set_text_color(*DIM)
        self.set_font("ArialUni", "", 8)
        self.set_xy(x + 4, y + 13.5)
        self.cell(w - 8, 8, lbl, align="L")

    def _section_title(self, num, title):
        self.set_text_color(*ACC2)
        self.set_font("ArialUni", "B", 10)
        self.cell(0, 6, num, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)
        self.set_font("ArialUni", "B", 28)
        self.cell(0, 14, title, new_x="LMARGIN", new_y="NEXT")

    # ---- PAGES ----
    def cover(self):
        self.add_page()
        # dots
        for i, (col, label) in enumerate([(GREEN, "G"), (AMBER, "A"), (RED, "R")]):
            self.set_fill_color(*col)
            self.circle(24 + i * 10, 80, 2.5, "F")
        # title
        self.set_text_color(*INK)
        self.set_font("ArialUni", "B", 48)
        self.set_xy(24, 90)
        self.cell(0, 20, "FirstPass")
        self.set_xy(24, 112)
        self.set_font("ArialUni", "", 13)
        self.set_text_color(*DIM)
        self.cell(0, 7, "AI contract triage for in-house legal teams")
        self.set_xy(24, 120)
        self.cell(0, 7, "Every contract gets an AI first pass. A human confirms.")
        self.set_xy(24, 128)
        self.cell(0, 7, "The queue gets shorter every month.")
        self.set_xy(24, 144)
        self.set_text_color(*FAINT)
        self.set_font("ArialUni", "", 10)
        self.cell(0, 6, "Abdelrhman Rayis  ·  PortSwigger AI Pioneer  ·  July 2026")
        # badges
        self._badge(24, 165, "RED  escalate", RED_T, RED, 38)
        self._badge(66, 165, "AMBER  confirm", AMBER_T, AMBER, 42)
        self._badge(112, 165, "GREEN  auto-clear", GREEN_T, GREEN, 44)
        self._badge(24, 175, "on-prem  ·  local AI  ·  no cloud", GREEN_T, GREEN, 60)

    def section_code(self):
        self.add_page()
        self.set_xy(24, 28)
        self._section_title("01  ·  The Solution", "The Code")

        self.set_xy(24, 62)
        self.set_text_color(*DIM)
        self.set_font("ArialUni", "", 10.5)
        self.multi_cell(150, 5.5,
            "A working, measurable prototype that reads commercial contracts "
            "(NDAs, order forms), checks them against a living playbook of "
            "standard positions, and routes each one as GREEN, AMBER or RED. "
            "Built to run entirely on your own servers.")

        # pills
        y = 96
        for txt, bg, fg, w in [
            ("7-step agentic loop", SOFT, INK, 38),
            ("Deterministic engine", AMBER_T, AMBER, 38),
            ("Local-model reasoning", BLUE_T, BLUE, 42),
            ("Learning flywheel", RED_T, RED, 36),
        ]:
            self._pill(24, y, w, txt, bg, fg)
            y += 9

        # metrics
        self._metric(24, 130, 38, "0", "unsafe misses", GREEN)
        self._metric(66, 130, 38, "100%", "triage accuracy", INK)
        self._metric(108, 130, 38, "93%", "issue recall, no LLM", AMBER)
        self._metric(150, 130, 38, "58%", "review time removed", ACC2)

        # screenshots
        for i, fn in enumerate(["shot_dashboard.png", "shot_detail_amber.png"]):
            p = ASSETS / fn
            if p.exists():
                self.image(str(p), x=24 + i * 84, y=168, w=80)

        # CTA button
        self.set_fill_color(*ACC)
        self.set_text_color(*WHITE)
        self.set_font("ArialUni", "B", 12)
        self.set_xy(24, 235)
        self.cell(58, 9, "  View on GitHub  >", fill=True)
        self.link(24, 235, 58, 9, GITHUB)

    def section_video(self):
        self.add_page()
        self.set_xy(24, 28)
        self._section_title("02  ·  See it in action", "Demo Video")

        self.set_xy(24, 62)
        self.set_text_color(*DIM)
        self.set_font("ArialUni", "", 10.5)
        self.multi_cell(150, 5.5,
            "A walkthrough of FirstPass running live: the CLI queue in under "
            "30 seconds, the web console a lawyer would open each morning, and "
            "the learning flywheel closing the one recall gap the eval found.")

        # Card 1
        self.set_fill_color(*SOFT)
        self.set_draw_color(200, 200, 206)
        self.rect(24, 90, 162, 42, "DF")
        self.set_xy(30, 94)
        self.set_text_color(*INK)
        self.set_font("ArialUni", "B", 13)
        self.cell(0, 7, "▶  FirstPass demo")
        self.set_xy(30, 103)
        self.set_text_color(*DIM)
        self.set_font("ArialUni", "", 10)
        self.multi_cell(150, 5,
            "Watch the prototype triage 10 contracts, the web console at work, "
            "and the learning loop in action — all running offline on a local "
            "machine. No cloud, no API keys, no contract text leaving the building.")
        self.set_text_color(*ACC2)
        self.set_font("ArialUni", "B", 11)
        self.set_xy(30, 122)
        self.cell(40, 6, "Watch on GitHub  >")
        self.link(30, 122, 40, 6, GITHUB)

        # Card 2: Quickstart
        self.set_fill_color(*SOFT)
        self.rect(24, 144, 162, 36, "DF")
        self.set_xy(30, 148)
        self.set_text_color(*INK)
        self.set_font("ArialUni", "B", 13)
        self.cell(0, 7, "Quickstart (30 seconds)")
        self.set_xy(30, 157)
        self.set_text_color(*INK)
        self.set_font("ArialUni", "", 9)
        for i, line in enumerate([
            "python3 -m venv .venv && source .venv/bin/activate",
            "pip install -r requirements.txt",
            "python run.py --all",
            "python webapp/app.py     # http://localhost:5050",
        ]):
            self.set_xy(30, 157 + i * 5)
            self.cell(0, 5, line)

    def section_deck(self):
        self.add_page()
        self.set_xy(24, 28)
        self._section_title("03  ·  The Story", "Presentation Deck")

        self.set_xy(24, 62)
        self.set_text_color(*DIM)
        self.set_font("ArialUni", "", 10.5)
        self.multi_cell(150, 5.5,
            "18 slides that walk through the thinking, not just the feature "
            "list. From first principles and five whys through the agentic "
            "loop, measured results, privacy architecture, and how I would "
            "add value at PortSwigger.")

        # pills
        y = 96
        for txt, bg, fg, w in [
            ("How I think", SOFT, INK, 26),
            ("First principles", GREEN_T, GREEN, 30),
            ("Five whys", AMBER_T, AMBER, 22),
            ("Systems thinking", RED_T, RED, 30),
            ("80/20", BLUE_T, BLUE, 18),
        ]:
            self._pill(24 + (y - 96) * 0, y, w, txt, bg, fg)
            y += 9
        # second row of pills
        y = 96
        for txt, bg, fg, w in [
            ("Measured results", GREEN_T, GREEN, 32),
            ("Privacy by design", AMBER_T, AMBER, 30),
        ]:
            self._pill(100 + (y - 96) * 0, y, w, txt, bg, fg)
            y += 9

        # Deck card
        self.set_fill_color(*SOFT)
        self.rect(24, 120, 162, 34, "DF")
        self.set_xy(30, 124)
        self.set_text_color(*INK)
        self.set_font("ArialUni", "B", 13)
        self.cell(0, 7, "FirstPass_PortSwigger.pdf  -  18 slides")
        self.set_xy(30, 133)
        self.set_text_color(*DIM)
        self.set_font("ArialUni", "", 10)
        self.multi_cell(150, 5,
            "PortSwigger-branded. Covers the scenario, root cause, the solution "
            "running live, console screenshots, evaluation metrics, the learning "
            "flywheel, GDPR and privacy, and my fit. Reproducible: generated "
            "from deck/build_deck.py.")
        # Buttons
        self.set_fill_color(*INK)
        self.set_text_color(*WHITE)
        self.set_font("ArialUni", "B", 10)
        self.set_xy(30, 148)
        self.cell(42, 7, "  Open PDF  >", fill=True)
        self.link(30, 148, 42, 7, DECK_PDF)
        self.set_fill_color(*WHITE)
        self.set_text_color(*ACC2)
        self.set_draw_color(*ACC2)
        self.set_xy(78, 148)
        self.cell(42, 7, "  Download PPTX  >", fill=True)
        self.link(78, 148, 42, 7, DECK_PPTX)

        # Slide list card
        self.set_fill_color(*SOFT)
        self.rect(24, 164, 162, 42, "DF")
        self.set_xy(30, 168)
        self.set_text_color(*INK)
        self.set_font("ArialUni", "B", 12)
        self.cell(0, 6, "What the deck covers")
        self.set_xy(30, 177)
        self.set_text_color(*DIM)
        self.set_font("ArialUni", "", 9.5)
        self.multi_cell(150, 5,
            "Cover  >  Agenda  >  Delivery plan  >  How I think  >  The scenario  >  "
            "Five whys  >  First principles  >  Systems thinking  >  "
            "Business analysis  >  The agentic loop  >  Why agentic not n8n  >  "
            "Live console  >  Inside a review  >  Measured results  >  "
            "Learning flywheel  >  Privacy & standards  >  My fit  >  Close")

    def footer_page(self):
        self.add_page()
        self.set_draw_color(200, 200, 206)
        self.line(24, 28, 186, 28)
        self.set_xy(24, 36)
        self.set_text_color(*FAINT)
        self.set_font("ArialUni", "", 9)
        self.cell(0, 5, "FirstPass  ·  AI contract triage  ·  Abdelrhman Rayis")
        self.set_xy(24, 44)
        self.set_text_color(*ACC2)
        self.set_font("ArialUni", "B", 10)
        self.cell(0, 5, GITHUB)
        self.link(24, 44, 80, 5, GITHUB)
        self.set_xy(24, 52)
        self.set_text_color(*FAINT)
        self.set_font("ArialUni", "", 9)
        self.cell(0, 5, "abdelrhman.rayis@gmail.com")


def main():
    pdf = SummaryPDF()
    pdf.cover()
    pdf.section_code()
    pdf.section_video()
    pdf.section_deck()
    pdf.footer_page()

    out = ROOT / "FirstPass_Summary.pdf"
    pdf.output(str(out))
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
