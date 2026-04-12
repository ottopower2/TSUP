"""
komponenten_vergleich.py
Detaillierte Analyse: Impedanz und Dämpfung von L1, C1, C2, C3
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

# Parameter
L1 = 180.0e-6
C1 = 820.0e-9
C2 = 100.0e-9
C3 = 10.0e-9

esl_c1 = 1.0e-9
esl_c2 = 0.8e-9
esl_c3 = 0.4e-9

f = np.logspace(2, 8, 3000)
omega = 2 * np.pi * f

# Import FilterBerechnung für Impedanz-Berechnung
from filter_berechnung import FilterBerechnung

# Simulierte Impedanzen
Z_L1 = np.abs(1j * omega * L1)
Z_C1_real = np.abs(0.001 + 1j*omega*esl_c1 + 1/(1j*omega*C1))
Z_C2_real = np.abs(0.002 + 1j*omega*esl_c2 + 1/(1j*omega*C2))
Z_C3_real = np.abs(0.002 + 1j*omega*esl_c3 + 1/(1j*omega*C3))

# Parallel-Umrechnung
Y_c2_c3 = 1/(Z_C2_real + 1e-15) + 1/(Z_C3_real + 1e-15)
Z_bypass = np.abs(1 / (Y_c2_c3 + 1e-15))

# Gesamt-Impedanzen
Z_ohne = np.abs(1j*omega*L1 + 1/(1j*omega*C1 + 1e-15))
Z_mit = np.abs(1j*omega*L1 + 1/(1j*omega*(C1+C2+C3) + 1e-15))

# Resonanzfrequenzen
f0_ohne = 1 / (2*np.pi*np.sqrt(L1 * C1))
f0_mit = 1 / (2*np.pi*np.sqrt(L1 * (C1+C2+C3)))

# Figure
fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor(DUNKEL)
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3,
              left=0.08, right=0.96, top=0.93, bottom=0.06)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[1, 0])
ax4 = fig.add_subplot(gs[1, 1])
ax5 = fig.add_subplot(gs[2, :])

def style_ax(ax):
    ax.set_facecolor(SURFACE)
    ax.tick_params(colors=TEXTM, labelsize=9)
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID)
    ax.grid(True, which='major', color=GRID, linewidth=0.7, alpha=0.8)
    ax.set_xscale('log')

# Plot 1
style_ax(ax1)
ax1.set_yscale('log')
ax1.plot(f, Z_L1, color=AKZENT1, linewidth=3, label='L1 = 180µH')
ax1.plot(f, Z_C1_real, color=AKZENT5, linewidth=3, label='C1 = 820nF')
ax1.axvline(f0_ohne, color='white', linewidth=1.5, ls='--', alpha=0.5, label=f'f₀={f0_ohne/1e3:.1f}kHz')
ax1.set_ylabel('Impedanz |Z| [Ω]', fontsize=10, fontweight='bold')
ax1.set_title('L1 & C1: Haupt-Filter', fontsize=11, fontweight='bold')
ax1.set_ylim(1e-2, 1e5)
ax1.set_xlim(1e2, 1e8)
ax1.legend(loc='center right', fontsize=8)

# Plot 2
style_ax(ax2)
ax2.set_yscale('log')
ax2.plot(f, Z_C2_real, color=AKZENT3, linewidth=2.5, label='C2 = 100nF')
ax2.plot(f, Z_C3_real, color=AKZENT2, linewidth=2.5, label='C3 = 10nF')
ax2.plot(f, Z_bypass, color='#ff9f40', linewidth=3, label='C2 || C3', linestyle='--')
ax2.set_ylabel('Impedanz |Z| [Ω]', fontsize=10, fontweight='bold')
ax2.set_title('C2 & C3: Bypass-Stack', fontsize=11, fontweight='bold')
ax2.set_ylim(1e-3, 1e4)
ax2.set_xlim(1e2, 1e8)
ax2.legend(loc='upper right', fontsize=8)

# Plot 3
style_ax(ax3)
ax3.set_yscale('log')
ax3.plot(f, Z_ohne, color=AKZENT4, linewidth=3.5, label='L1+C1 (OHNE Bypass)')
ax3.plot(f, Z_mit, color=AKZENT3, linewidth=3.5, label='L1+C1||C2||C3 (MIT Bypass)')
ax3.axvline(f0_ohne, color=AKZENT4, linewidth=1, ls='--', alpha=0.6)
ax3.axvline(f0_mit, color=AKZENT3, linewidth=1, ls='--', alpha=0.6)
ax3.set_ylabel('Impedanz |Z| [Ω]', fontsize=10, fontweight='bold')
ax3.set_title('Gesamt-Impedanz Vergleich', fontsize=11, fontweight='bold')
ax3.set_ylim(1e-1, 1e3)
ax3.set_xlim(1e2, 1e8)
ax3.legend(loc='upper right', fontsize=8)

# Plot 4 - Phase
style_ax(ax4)
phase_ohne = np.angle(1j*omega*L1 + 1/(1j*omega*C1), deg=True)
phase_mit = np.angle(1j*omega*L1 + 1/(1j*omega*(C1+C2+C3)), deg=True)
ax4.plot(f, phase_ohne, color=AKZENT4, linewidth=2.5, label='Phase: ohne Bypass')
ax4.plot(f, phase_mit, color=AKZENT3, linewidth=2.5, label='Phase: mit Bypass')
ax4.axhline(0, color=GRID, linewidth=0.8, ls='--', alpha=0.5)
ax4.axhline(90, color=GRID, linewidth=0.8, ls='--', alpha=0.5)
ax4.set_ylabel('Phase [°]', fontsize=10, fontweight='bold')
ax4.set_title('Phasengang-Vergleich', fontsize=11, fontweight='bold')
ax4.set_ylim(-100, 100)
ax4.set_xlim(1e2, 1e8)
ax4.legend(loc='center right', fontsize=8)

# Plot 5 - Dämpfung
style_ax(ax5)
H_ohne = 20 * np.log10(Z_ohne / 60 + 1e-15)
H_mit  = 20 * np.log10(Z_mit / 60 + 1e-15)
ax5.plot(f, H_ohne, color=AKZENT4, linewidth=3.5, label='Dämpfung: L1+C1 (OHNE C2/C3)', marker='')
ax5.plot(f, H_mit, color=AKZENT3, linewidth=3.5, label='Dämpfung: L1+C1 + Bypass (MIT C2/C3)', marker='')
ax5.fill_between(f, H_ohne, H_mit, where=(np.abs(H_ohne) >= np.abs(H_mit)), alpha=0.2, color=AKZENT3)
ax5.axhline(-40, color=AKZENT2, linewidth=1.5, ls=':', alpha=0.6, label='Ziel: -40dB')
ax5.axvline(150e3, color='white', linewidth=1.5, ls='--', alpha=0.5, label='Störfrequenz: 150kHz')
ax5.set_xlabel('Frequenz [Hz]', fontsize=11, fontweight='bold')
ax5.set_ylabel('Dämpfung [dB]', fontsize=11, fontweight='bold')
ax5.set_title('Dämpfungs-Vergleich: MIT vs OHNE Bypass-Stack', fontsize=12, fontweight='bold')
ax5.set_ylim(-90, 20)
ax5.set_xlim(1e2, 1e8)
ax5.legend(loc='lower left', fontsize=9, ncol=2)
ax5.yaxis.set_major_locator(ticker.MultipleLocator(10))
ax5.grid(True, which='both', color=GRID, linewidth=0.7, alpha=0.8)

fig.suptitle('EMV-Filter: Komponenten-Analyse (L1=180µH, C1=820nF, C2=100nF, C3=10nF)',
             color=TEXTF, fontsize=13, fontweight='bold', y=0.96)

plt.savefig('emv_komponenten_detailanalyse.png', dpi=150, bbox_inches='tight', facecolor=DUNKEL)
print("✅ Komponenten-Analyse gespeichert: emv_komponenten_detailanalyse.png")
plt.show()
