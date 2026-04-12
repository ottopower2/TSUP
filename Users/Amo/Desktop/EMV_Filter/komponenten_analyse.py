"""
komponenten_analyse.py
Detaillierte Analyse: Impedanz und Dämpfung von L1, C1, C2, C3 im Detail
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec

# Dark Theme
DUNKEL = '#0f1117'
SURFACE = '#1a1d27'
GRID = '#2a2d3a'
TEXTF = '#c8ccd8'
TEXTM = '#7a7f96'
AKZENT1 = '#4f8ef7'   # Blau - L1
AKZENT2 = '#f7c948'   # Gelb - C3
AKZENT3 = '#5de8a0'   # Grün - C2
AKZENT4 = '#f76e6e'   # Rot - Gesamt
AKZENT5 = '#a78bfa'   # Lila - C1

# Parameter (aus 12V / 200mA / 150kHz / 40dB)
L1 = 180.0e-6        # 180 µH
C1 = 820.0e-9        # 820 nF
C2 = 100.0e-9        # 100 nF
C3 = 10.0e-9         # 10 nF
Rl = 60              # Lastimpedanz

# ESL der Kondensatoren (abhängig von Größe)
esl_c1 = 1.0e-9      # 0805 = ~1nH
esl_c2 = 0.8e-9      # 0402 = ~0.8nH
esl_c3 = 0.4e-9      # 0402 = ~0.4nH

# Frequenzachse: 100 Hz bis 100 MHz
f = np.logspace(2, 8, 3000)
omega = 2 * np.pi * f

# ── Impedanzen berechnen ────────────────────────────────────────────────────

# ── Figure & Layout ───────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor(DUNKEL)
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3,
              left=0.08, right=0.96, top=0.93, bottom=0.06)

ax1 = fig.add_subplot(gs[0, 0])  # L1 & C1 Impedanzen
ax2 = fig.add_subplot(gs[0, 1])  # C2 & C3 Bypass
ax3 = fig.add_subplot(gs[1, 0])  # Gesamt-Impedanz (mit/ohne Bypass)
ax4 = fig.add_subplot(gs[1, 1])  # Phasenwinkel
ax5 = fig.add_subplot(gs[2, :])  # Dämpfungs-Vergleich (großer Plot)

# ════════════════════════════════════════════════════════════════════════════
# Plot 1: L1 & C1 Impedanzen
# ════════════════════════════════════════════════════════════════════════════

def style_ax(ax):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXTM, labelsize=9)
    ax.xaxis.label.set_color(TEXTM)
    ax.yaxis.label.set_color(TEXTM)
    ax.title.set_color(TEXTF)
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID)
    ax.grid(True, which='major', color=GRID, linewidth=0.7, alpha=0.8)
    ax.grid(True, which='minor', color=GRID, linewidth=0.3, alpha=0.4)
    ax.set_xscale('log')

style_ax(ax1)
ax1.set_yscale('log')

ax1.plot(f, Z_L1, color=AKZENT1, linewidth=3, label='L1 = 180µH (nur Spule)', marker='')
ax1.plot(f, Z_C1_real, color=AKZENT5, linewidth=3, label='C1 = 820nF (mit ESL)', marker='')
ax1.axvline(f0_L1_C1, color='white', linewidth=1.5, ls='--', alpha=0.5, label=f'f₀(L1+C1) = {f0_L1_C1/1e3:.1f}kHz')
ax1.fill_between(f, Z_L1, Z_C1_real, where=(Z_L1<=Z_C1_real), alpha=0.1, color=AKZENT1)
ax1.fill_between(f, Z_L1, Z_C1_real, where=(Z_L1>Z_C1_real), alpha=0.1, color=AKZENT5)

ax1.set_ylabel('Impedanz |Z| [Ω]', fontsize=10, fontweight='bold')
ax1.set_title('L1 & C1: Hauptfilter-Komponenten', fontsize=11, fontweight='bold')
ax1.set_ylim(1e-2, 1e5)
ax1.set_xlim(1e2, 1e8)
ax1.legend(loc='center right', fontsize=8, framealpha=0.95)

# ════════════════════════════════════════════════════════════════════════════
# Plot 2: C2 & C3 Bypass
# ════════════════════════════════════════════════════════════════════════════

style_ax(ax2)
ax2.set_yscale('log')

ax2.plot(f, Z_C2_real, color=AKZENT3, linewidth=2.5, label='C2 = 100nF (ESL=0.8nH)', linestyle='-')
ax2.plot(f, Z_C3_real, color=AKZENT2, linewidth=2.5, label='C3 = 10nF (ESL=0.4nH)', linestyle='-')
ax2.plot(f, Z_bypass_abs, color='#ff9f40', linewidth=3, label='C2 || C3 (Parallel)', linestyle='--')

# SRF Markierungen
srf_c2 = 1 / (2*np.pi*np.sqrt(esl_c2 * C2))
srf_c3 = 1 / (2*np.pi*np.sqrt(esl_c3 * C3))
ax2.axvline(srf_c2, color=AKZENT3, linewidth=1, ls=':', alpha=0.6)
ax2.axvline(srf_c3, color=AKZENT2, linewidth=1, ls=':', alpha=0.6)

ax2.text(srf_c2, 100, f'SRF(C2)\n{srf_c2/1e6:.0f}MHz', fontsize=7, color=AKZENT3, ha='center')
ax2.text(srf_c3, 10, f'SRF(C3)\n{srf_c3/1e6:.0f}MHz', fontsize=7, color=AKZENT2, ha='center')

ax2.set_ylabel('Impedanz |Z| [Ω]', fontsize=10, fontweight='bold')
ax2.set_title('C2 & C3: Bypass-Stack für Hochfrequenzen', fontsize=11, fontweight='bold')
ax2.set_ylim(1e-3, 1e4)
ax2.set_xlim(1e2, 1e8)
ax2.legend(loc='upper right', fontsize=8)

# ════════════════════════════════════════════════════════════════════════════
# Plot 3: Gesamt-Impedanz (mit/ohne Bypass)
# ════════════════════════════════════════════════════════════════════════════

style_ax(ax3)
ax3.set_yscale('log')

ax3.plot(f, Z_total_ohne_bypass, color=AKZENT4, linewidth=3.5, label='L1 + C1 (OHNE Bypass)', linestyle='-')
ax3.plot(f, Z_total_mit_bypass, color=AKZENT3, linewidth=3.5, label='L1 + C1||C2||C3 (MIT Bypass)', linestyle='-')

ax3.axvline(f0_L1_C1, color=AKZENT4, linewidth=1.2, ls='--', alpha=0.6, label=f'Resonanz ohne: {f0_L1_C1/1e3:.1f}kHz')
ax3.axvline(f0_L1_C_all, color=AKZENT3, linewidth=1.2, ls='--', alpha=0.6, label=f'Resonanz mit: {f0_L1_C_all/1e3:.1f}kHz')

# Schattierung der Verbesserung
ax3.fill_between(f, Z_total_ohne_bypass, Z_total_mit_bypass, 
                 where=(Z_total_ohne_bypass >= Z_total_mit_bypass), 
                 alpha=0.15, color=AKZENT3, label='Verbesserung durch Bypass')

ax3.set_ylabel('Impedanz |Z| [Ω]', fontsize=10, fontweight='bold')
ax3.set_title('Auswirkung des Bypass-Stacks auf die Gesamt-Filterimpedanz', fontsize=11, fontweight='bold')
ax3.set_ylim(1e-1, 1e3)
ax3.set_xlim(1e2, 1e8)
ax3.legend(loc='upper right', fontsize=7.5)

# ════════════════════════════════════════════════════════════════════════════
# Plot 4: Phasenwinkel
# ════════════════════════════════════════════════════════════════════════════

style_ax(ax4)

# Phase berechnen
phase_L1 = 90  # Induktivität always +90°
phase_C1 = np.angle(1/(1j*omega*C1), deg=True)
phase_C2 = np.angle(1/(1j*omega*C2), deg=True)
phase_C3 = np.angle(1/(1j*omega*C3), deg=True)

phase_total_ohne = np.angle(1j*omega*L1 + 1/(1j*omega*C1), deg=True)
phase_total_mit = np.angle(1j*omega*L1 + 1/(1j*omega*(C1+C2+C3)), deg=True)

ax4.plot(f, phase_total_ohne, color=AKZENT4, linewidth=2.5, label='Phase: L1+C1 (ohne Bypass)', linestyle='-')
ax4.plot(f, phase_total_mit, color=AKZENT3, linewidth=2.5, label='Phase: L1+C1||C2||C3 (mit Bypass)', linestyle='-')

ax4.axhline(0, color=GRID, linewidth=0.8, ls='--', alpha=0.5)
ax4.axhline(90, color=GRID, linewidth=0.8, ls='--', alpha=0.5)
ax4.axhline(-90, color=GRID, linewidth=0.8, ls='--', alpha=0.5)

ax4.set_ylabel('Phase [°]', fontsize=10, fontweight='bold')
ax4.set_title('Phasengang: Einfluss der Bypass-Kondensatoren', fontsize=11, fontweight='bold')
ax4.set_ylim(-100, 100)
ax4.set_xlim(1e2, 1e8)
ax4.legend(loc='center right', fontsize=8)
ax4.grid(True, which='major', color=GRID, linewidth=0.7, alpha=0.8)

# ════════════════════════════════════════════════════════════════════════════
# Plot 5: Dämpfungs-Komparison (großer unten)
# ════════════════════════════════════════════════════════════════════════════

style_ax(ax5)

# Dämpfung = 20*log10(Z_out / Z_in)
# Vereinfachung: Annahme Z_in = 1 (normalisiert)
H_ohne_bypass = Z_total_ohne_bypass / 60  # normalisiert auf Last
H_mit_bypass = Z_total_mit_bypass / 60

H_dB_ohne = 20 * np.log10(np.abs(H_ohne_bypass) + 1e-15)
H_dB_mit = 20 * np.log10(np.abs(H_mit_bypass) + 1e-15)

ax5.plot(f, H_dB_ohne, color=AKZENT4, linewidth=3.5, label='Dämpfung: L1+C1 (OHNE Bypass C2/C3)', marker='')
ax5.plot(f, H_dB_mit, color=AKZENT3, linewidth=3.5, label='Dämpfung: L1+C1 + Bypass (MIT C2/C3)', marker='')

# Verbesserung schattieren
ax5.fill_between(f, H_dB_ohne, H_dB_mit, 
                 where=(np.abs(H_dB_ohne) >= np.abs(H_dB_mit)), 
                 alpha=0.2, color=AKZENT3)

# Referenzlinien
ax5.axhline(-40, color=AKZENT2, linewidth=1.5, ls=':', alpha=0.6, label='Ziel-Dämpfung: -40dB')
ax5.axvline(150e3, color='white', linewidth=1.5, ls='--', alpha=0.5, label='Störfrequenz: 150kHz')

ax5.set_xlabel('Frequenz [Hz]', fontsize=11, fontweight='bold')
ax5.set_ylabel('Dämpfung [dB]', fontsize=11, fontweight='bold')
ax5.set_title('Vergleich: Hämpfung MIT vs OHNE Bypass-Stack (C2, C3)', fontsize=12, fontweight='bold')
ax5.set_ylim(-90, 20)
ax5.set_xlim(1e2, 1e8)
ax5.legend(loc='lower left', fontsize=9, framealpha=0.95, ncol=2)
ax5.grid(True, which='both', color=GRID, linewidth=0.7, alpha=0.8)
ax5.yaxis.set_major_locator(ticker.MultipleLocator(10))

# ── Haupttitel ────────────────────────────────────────────────────────────
fig.suptitle(
    'EMV-Filter: Detaillierte Komponenten-Analyse (L1=180µH, C1=820nF, C2=100nF, C3=10nF)',
    color=TEXTF, fontsize=13, fontweight='bold', y=0.96
)

plt.savefig('emv_komponenten_detailanalyse.png', dpi=150, bbox_inches='tight',
            facecolor=DUNKEL)
print("✅ Komponenten-Analyse gespeichert: emv_komponenten_detailanalyse.png")
plt.show()
