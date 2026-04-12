"""
main.py
-------
Einstiegspunkt des EMV-Filter-Auslegungswerkzeugs.

Ablauf:
  1. Banner anzeigen
  2. Benutzereingaben abfragen     → Eingabe
  3. Filter berechnen              → FilterBerechnung
  4. Ergebnisse im Terminal ausgeben → FilterAusgabe
  5. Grafische Plots erstellen     → FilterPlot

Starte mit:
  python main.py
"""

from eingabe import Eingabe
from filter_berechnung import FilterBerechnung
from filter_ausgabe import FilterAusgabe
from filter_plot import FilterPlot


class EMVFilterApp:
    """Orchestriert den gesamten Ablauf des Auslegungswerkzeugs."""

    def run(self):
        self._banner()

        # ── 1. Eingaben ───────────────────────────────────────────────────────
        u_v          = Eingabe.float("Versorgungsspannung",          12,  " V")
        i_ma         = Eingabe.float("Laststrom",                   200,  " mA")
        f_stoer_khz  = Eingabe.float("Störfrequenz (Schaltregler)", 500,  " kHz")
        daempfung_db = Eingabe.float("Gewünschte Dämpfung",          40,  " dB")
        stufen       = int(Eingabe.wahl("Filterstufenzahl", [1, 2], 1))
        anwendung    = Eingabe.wahl("Anwendung", ['kfz', 'industrie', 'consumer'], 'kfz')

        # ── 2. Berechnung ─────────────────────────────────────────────────────
        berechnung = FilterBerechnung(u_v, i_ma, f_stoer_khz, daempfung_db, stufen)
        res = berechnung.ergebnis
        res['anwendung'] = anwendung.upper()

        # ── 3. Terminal-Ausgabe ────────────────────────────────────────────────
        ausgabe = FilterAusgabe(res)
        ausgabe.drucke_ergebnisse()

        f_tabelle = [1, 5, 10, res['f0_real']/1e3, 50, 100, 200,
                     f_stoer_khz, f_stoer_khz*2, f_stoer_khz*5, 10000]
        f_tabelle = sorted(set([round(f, 2) for f in f_tabelle if 0.1 < f < 100000]))
        ausgabe.drucke_daempfungstabelle(f_tabelle)

        # ── 4. Layout-Hinweise ────────────────────────────────────────────────
        self._layout_hinweise(anwendung)

        # ── 5. Plots ──────────────────────────────────────────────────────────
        FilterPlot(res).erstelle_plots()

    @staticmethod
    def _banner():
        print("\n" + "╔" + "═"*58 + "╗")
        print("║    EMV-LC-Tiefpassfilter Auslegungswerkzeug              ║")
        print("║    für Versorgungsleitungen (CISPR 25 / ISO 11452)       ║")
        print("╚" + "═"*58 + "╝\n")
        print("  Drücke [Enter] für den Default-Wert (Beispiel: 12V/200mA/500kHz)\n")

    @staticmethod
    def _layout_hinweise(anwendung):
        print("  📐 Layout-Hinweise")
        print("  • Kondensatoren so nah wie möglich an der Last platzieren")
        print("  • GND-Plane unter dem Filter durchgehend (keine Schlitze)")
        print("  • Eingang/Ausgang räumlich trennen (kein Übersprechen)")
        print("  • C2+C3 direkt parallel zu C1 (nicht in Reihe auf der Leitung)")
        print("  • Keine Via-in-Pad unter der Spule (erhöht parasitäre Kapazität)")
        if anwendung == 'kfz':
            print("  • KFZ: Zusätzlich stromkompensierte Drossel für Common-Mode empfohlen")
            print("         (z.B. Würth 744232150) — schützt gegen asymmetrische Störströme")
        print()


if __name__ == "__main__":
    EMVFilterApp().run()
