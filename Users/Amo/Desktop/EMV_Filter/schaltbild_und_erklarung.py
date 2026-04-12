"""
schaltbild_und_erklarung.py
Zeigt die komplette LC-Filter-Schaltung mit allen Bauteilen
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Dark Theme
DUNKEL = '#0f1117'
SURFACE = '#1a1d27'
GRID = '#2a2d3a'
TEXTF = '#c8ccd8'
TEXTM = '#7a7f96'
AKZENT1 = '#4f8ef7'  # Blau
AKZENT2 = '#f7c948'  # Gelb
AKZENT3 = '#5de8a0'  # Grün
AKZENT4 = '#f76e6e'  # Rot

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
fig.patch.set_facecolor(DUNKEL)

# ════════════════════════════════════════════════════════════════════════════
# PLOT 1: Schaltbild
# ════════════════════════════════════════════════════════════════════════════

ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_facecolor(SURFACE)

# Titel
ax1.text(5, 9.5, 'EMV-LC-Tiefpassfilter Schaltung', 
         fontsize=14, fontweight='bold', color=TEXTF, ha='center')

# ── Eingangslinie ────────────────────────────────────────────────────────
ax1.plot([0.5, 2], [7, 7], color=TEXTF, lw=2)
ax1.text(0.2, 7, 'Vin\n12V', fontsize=9, color=TEXTF, va='center')

# ── Spule L1 ──────────────────────────────────────────────────────────────
l_x, l_y = 2.5, 7
circle1_x, circle1_y = 2.8, 7
circle2_x, circle2_y = 3.2, 7
ax1.plot([2, 2.5], [7, 7], color=AKZENT1, lw=2)
circle1 = plt.Circle((circle1_x, circle1_y), 0.2, fill=False, edgecolor=AKZENT1, lw=2)
circle2 = plt.Circle((circle2_x, circle2_y), 0.2, fill=False, edgecolor=AKZENT1, lw=2)
ax1.add_patch(circle1)
ax1.add_patch(circle2)
ax1.plot([3.5, 4.5], [7, 7], color=AKZENT1, lw=2)
ax1.text(3, 7.6, 'L1\n47µH', fontsize=9, fontweight='bold', color=AKZENT1, ha='center')

# ── Knoten nach L1 (mit Masse-Symbol) ──────────────────────────────────────
node_x = 4.5
ax1.plot([node_x, node_x], [7, 2.5], color=TEXTF, lw=2)
ax1.plot([node_x-0.1, node_x+0.1], [7, 7], color=TEXTF, lw=3)

# ── C1 (Haupt-Kondensator) ─────────────────────────────────────────────────
c1_x = 5.5
ax1.plot([c1_x, c1_x], [7, 2.5], color=AKZENT4, lw=2.5)
ax1.plot([c1_x-0.25, c1_x+0.25], [6.3, 6.3], color=AKZENT4, lw=2.5)
ax1.plot([c1_x-0.25, c1_x+0.25], [6, 6], color=AKZENT4, lw=2.5)
ax1.text(6.2, 6.3, 'C1\n270nF\nX7R 25V', fontsize=8, fontweight='bold', color=AKZENT4)

# ── C2 (100nF Bypass) ──────────────────────────────────────────────────────
c2_x = 7
ax1.plot([c2_x, c2_x], [7, 2.5], color=AKZENT3, lw=2)
ax1.plot([c2_x-0.2, c2_x+0.2], [5.8, 5.8], color=AKZENT3, lw=2)
ax1.plot([c2_x-0.2, c2_x+0.2], [5.5, 5.5], color=AKZENT3, lw=2)
ax1.text(7.7, 5.6, 'C2\n100nF\nX7R 0402', fontsize=8, fontweight='bold', color=AKZENT3)

# ── C3 (10nF Bypass) ────────────────────────────────────────────────────────
c3_x = 8.2
ax1.plot([c3_x, c3_x], [7, 2.5], color=AKZENT2, lw=2)
ax1.plot([c3_x-0.15, c3_x+0.15], [5.2, 5.2], color=AKZENT2, lw=2)
ax1.plot([c3_x-0.15, c3_x+0.15], [4.9, 4.9], color=AKZENT2, lw=2)
ax1.text(8.9, 5, 'C3\n10nF\nX7R 0402', fontsize=8, fontweight='bold', color=AKZENT2)

# ── Massa-Ebene ──────────────────────────────────────────────────────────────
gnd_y = 2.5
ax1.plot([0.5, 9.5], [gnd_y, gnd_y], color=TEXTM, lw=3, linestyle='-')
ax1.plot([0.7, 9.3], [gnd_y-0.15, gnd_y-0.15], color=TEXTM, lw=2)
ax1.plot([0.9, 9.1], [gnd_y-0.3, gnd_y-0.3], color=TEXTM, lw=2)
ax1.text(0.2, gnd_y-0.5, 'GND', fontsize=9, color=TEXTM, fontweight='bold')

# ── Ausgang ────────────────────────────────────────────────────────────────
ax1.plot([4.5, 4.5], [2.5, 1.5], color=TEXTF, lw=2)
ax1.plot([4.5, 9.5], [1.5, 1.5], color=TEXTF, lw=2)
ax1.text(9.8, 1.5, 'Vout\nZu Last', fontsize=9, color=TEXTF, va='center', fontweight='bold')

# ── Info-Box ───────────────────────────────────────────────────────────────
info_text = (
    'Topologie: LC-Tiefpassfilter (π-Glied)\n\n'
    '• L1 = Serieninduktivität (blockiert HF)\n'
    '• C1 = Haupt-Kondensator (shunt zu GND)\n'
    '• C2, C3 = Bypass-Stack für höhere Frequenzen\n\n'
    'Funktion:\n'
    '• 0-10 kHz: Hauptfilterung durch L1+C1\n'
    '• 10-100 kHz: Unterstützung durch C2\n'
    '• >100 kHz: Hauptrolle bei C3 (10nF)\n'
    '• ESL des Kondensators → Resonanzen'
)
ax1.text(5, 0.2, info_text, fontsize=7.5, color=TEXTF, ha='center', va='bottom',
         bbox=dict(boxstyle='round,pad=0.6', fc=SURFACE, ec=GRID, lw=1.5))

# ════════════════════════════════════════════════════════════════════════════
# PLOT 2: Impedanz-Stack Erklärung
# ════════════════════════════════════════════════════════════════════════════

ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')
ax2.set_facecolor(SURFACE)

# Titel
ax2.text(5, 9.5, 'Impedanz-Charakteristik der Bypass-Komponenten', 
         fontsize=12, fontweight='bold', color=TEXTF, ha='center')

# ── Frequenzbereiche ───────────────────────────────────────────────────────
y_start = 8
box_height = 1.2
spacing = 0.3

# Box 1: C1 Dominanz
y_pos = y_start
rect1 = FancyBboxPatch((0.5, y_pos-box_height), 9, box_height,
                        boxstyle="round,pad=0.1", edgecolor=AKZENT4, 
                        facecolor=SURFACE, lw=2)
ax2.add_patch(rect1)
ax2.text(0.8, y_pos-0.35, 'Bereich 1: 1 kHz - 10 kHz', fontsize=9, 
         fontweight='bold', color=AKZENT4)
ax2.text(3.5, y_pos-0.35, 'C1 (270nF) dominiert\n→ Niedrige Impedanz, beste Filterung', 
         fontsize=8, color=TEXTF)
ax2.text(8.5, y_pos-0.35, 'SRF(C1):\n~15 MHz', fontsize=8, 
         color=TEXTM, ha='center')

# Box 2: C1 + C2 Kombinatio
y_pos = y_start - box_height - spacing
rect2 = FancyBboxPatch((0.5, y_pos-box_height), 9, box_height,
                        boxstyle="round,pad=0.1", edgecolor=AKZENT3, 
                        facecolor=SURFACE, lw=2)
ax2.add_patch(rect2)
ax2.text(0.8, y_pos-0.35, 'Bereich 2: 10 kHz - 100 kHz', fontsize=9, 
         fontweight='bold', color=AKZENT3)
ax2.text(3.5, y_pos-0.35, 'C1 + C2 (370nF) parallel\n→ Noch bessere Hochfrequenz-Ableitung', 
         fontsize=8, color=TEXTF)
ax2.text(8.5, y_pos-0.35, 'ESL(C2):\n~0.8nH\nSRF: ~60MHz', fontsize=8, 
         color=TEXTM, ha='center')

# Box 3: C1 + C2 + C3 Kombination
y_pos = y_start - 2*(box_height + spacing)
rect3 = FancyBboxPatch((0.5, y_pos-box_height), 9, box_height,
                        boxstyle="round,pad=0.1", edgecolor=AKZENT2, 
                        facecolor=SURFACE, lw=2)
ax2.add_patch(rect3)
ax2.text(0.8, y_pos-0.35, 'Bereich 3: >100 kHz', fontsize=9, 
         fontweight='bold', color=AKZENT2)
ax2.text(3.5, y_pos-0.35, 'C1 + C2 + C3 (380nF) parallel\n→ Ultra-niedrige Impedanz, Resonanzen gedämpft', 
         fontsize=8, color=TEXTF)
ax2.text(8.5, y_pos-0.35, 'ESL(C3):\n~0.4nH\nSRF: ~200MHz', fontsize=8, 
         color=TEXTM, ha='center')

# ── PCB Layout Best Practice ────────────────────────────────────────────────
layout_y = 0.5
layout_text = (
    '🔧 PCB-Layout Best Practice:\n'
    '✓ Alle C1, C2, C3 DIREKT parallel schalten (nicht in Reihe!)\n'
    '✓ Kurze Via-Pfade zu GND-Ebene (< 0.5mm)\n'
    '✓ L1 und C1 zentral nah an der Last platzieren\n'
    '✓ GND-Ebene durchgehend unter dem Filter (keine Schlitze)\n'
    '✓ Eingang/Ausgang räumlich trennen (min. 1cm)'
)
ax2.text(5, layout_y, layout_text, fontsize=7.5, color=TEXTF, ha='center', va='bottom',
         bbox=dict(boxstyle='round,pad=0.5', fc=SURFACE, ec=GRID, lw=1.5))

plt.tight_layout()
plt.savefig('emv_schaltung_erklaerung.png', dpi=150, bbox_inches='tight',
            facecolor=DUNKEL, edgecolor='none')
print("✅ Schaltbild gespeichert: emv_schaltung_erklaerung.png")
plt.show()
