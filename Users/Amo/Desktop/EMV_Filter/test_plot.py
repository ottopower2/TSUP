"""
test_plot.py - Schnelltest für die Plot-Anpassungen
"""

from filter_berechnung import FilterBerechnung
from filter_plot import FilterPlot

# Standardwerte
u_v          = 12.0
i_ma         = 200.0
f_stoer_khz  = 150.0
daempfung_db = 40.0
stufen       = 1
anwendung    = 'KFZ'

# Berechnung
print("🔄 Berechne Filter...")
berechnung = FilterBerechnung(u_v, i_ma, f_stoer_khz, daempfung_db, stufen)
res = berechnung.ergebnis
res['anwendung'] = anwendung

# Plots
print("📊 Erstelle Plots...")
FilterPlot(res).erstelle_plots()
print("✅ Fertig!")
