"""
emv_filter_auslegung.py
-----------------------
Rückwärtskompatibilität — leitet direkt an main.py weiter.

Der Code wurde in mehrere Module aufgeteilt:
  bauteil_utils.py     — BauteilUtils  (E12, Formatierung)
  eingabe.py           — Eingabe       (Terminal-Eingaben)
  filter_berechnung.py — FilterBerechnung (Kernberechnung)
  filter_ausgabe.py    — FilterAusgabe (Terminal-Ausgabe)
  filter_plot.py       — FilterPlot    (Grafik)
  main.py              — EMVFilterApp  (Hauptprogramm)

Starte am besten direkt mit:
  python main.py
"""

from main import EMVFilterApp

if __name__ == "__main__":
    EMVFilterApp().run()
