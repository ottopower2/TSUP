"""
filter_plot.py
--------------
Grafische Darstellung des EMV-Filters mit 4 Subplots.

Subplots:
  1. Amplitudengang (Dämpfungsverlauf)
  2. Phasengang
  3. Eingangsimpedanz
  4. Bauteil-Impedanzen inkl. Parasitics und SRF-Markierungen

Abhängigkeiten:
  bauteil_utils.BauteilUtils
  filter_berechnung.FilterBerechnung  (statische Methoden)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec

from bauteil_utils import BauteilUtils
from filter_berechnung import FilterBerechnung


class FilterPlot:
    """
    Erstellt die vollständige grafische Auswertung mit 4 Subplots.

    Parameters
    ----------
    ergebnis : dict — Rückgabe von FilterBerechnung.ergebnis
    """

    # ── Farbpalette (Dark-Theme) ──────────────────────────────────────────────
    DUNKEL  = '#0f1117'
    SURFACE = '#1a1d27'
    GRID    = '#2a2d3a'
    AKZENT1 = '#4f8ef7'   # Blau  — Hauptkurve
    AKZENT2 = '#f7c948'   # Gelb  — Marker / Soll
    AKZENT3 = '#5de8a0'   # Grün  — Ideal / Bypass
    AKZENT4 = '#f76e6e'   # Rot   — Warnung / Störfrequenz
    AKZENT5 = '#a78bfa'   # Lila  — Phase / Parasitäres
    TEXTF   = '#c8ccd8'
    TEXTM   = '#7a7f96'

    def __init__(self, ergebnis):
        self.r = ergebnis

    # ── Öffentliche Methode ───────────────────────────────────────────────────

    def erstelle_plots(self):
        """Berechnet alle Kurven, rendert die 4 Subplots und speichert das Bild."""
        r      = self.r
        L      = r['L_e12']
        C      = r['C_e12']
        Rl     = r['z_last']
        f0     = r['f0_real']
        fs     = r['f_s']
        stufen = r['stufen']

        # Frequenzachse: 100 Hz … 100 MHz
        f = np.logspace(2, 8, 2000)

        # Übertragungsfunktionen (mit und ohne Parasitics)
        H,       Z_in = FilterBerechnung.uebertragung_lc(f, L, C, Rl, stufen)
        H_ideal, _    = FilterBerechnung.uebertragung_lc(f, L, C, Rl, stufen, esl=0, esr=0)
        H_dB       = 20 * np.log10(np.abs(H)       + 1e-15)
        H_ideal_dB = 20 * np.log10(np.abs(H_ideal) + 1e-15)

        # Impedanzverläufe der einzelnen Bauteile
        omega     = 2 * np.pi * f
        esl_c     = 1e-9
        esr_c     = 0.01
        Z_C_real  = np.abs(esr_c + 1j*omega*esl_c + 1/(1j*omega*C))
        Z_C_ideal = np.abs(1 / (1j*omega*C))
        Z_L_real  = np.abs(1j*omega*L)
        
        # Gesamt-LC-Serien-Impedanz (ideal und real)
        Z_LC_ideal = np.abs(1j*omega*L + 1/(1j*omega*C))
        Z_LC_real  = np.abs(1j*omega*L + esr_c + 1j*omega*esl_c + 1/(1j*omega*C))

        # Bypass-Kondensatoren (Parallel-Impedanz)
        C_bp       = [C, 100e-9, 10e-9]
        esl_bp     = [1e-9, 0.8e-9, 0.4e-9]
        Z_bp_total = np.abs(FilterBerechnung.bypass_impedanz(f, C_bp, esl_bp))

        # Phasengang
        phase_deg = np.angle(H, deg=True)

        # ── Figure & Layout ───────────────────────────────────────────────────
        fig = plt.figure(figsize=(18, 14), dpi=100)
        fig.patch.set_facecolor(self.DUNKEL)
        gs = GridSpec(2, 3, figure=fig, hspace=0.38, wspace=0.35,
                      left=0.07, right=0.97, top=0.92, bottom=0.07)

        ax1 = fig.add_subplot(gs[0, :2])   # Amplitudengang  (breit)
        ax2 = fig.add_subplot(gs[0, 2])    # Phasengang
        ax3 = fig.add_subplot(gs[1, :2])   # Eingangsimpedanz (breit)
        ax4 = fig.add_subplot(gs[1, 2])    # Bauteil-Impedanzen

        self._plot_amplitudengang(ax1, f, H_dB, H_ideal_dB, f0, fs, stufen, r, L, C)
        self._plot_phasengang(ax2, f, phase_deg, f0, fs, stufen)
        self._plot_eingangsimpedanz(ax3, f, Z_in, Rl, f0, fs, r)
        self._plot_bauteil_impedanzen(ax4, f, Z_C_ideal, Z_C_real, Z_L_real,
                                      Z_bp_total, Z_LC_ideal, Z_LC_real, fs, r, L, C)

        # ── Haupttitel ────────────────────────────────────────────────────────
        anw = r.get('anwendung', 'Allgemein')
        fig.suptitle(
            f"EMV-Tiefpassfilter Auslegung  |  {r['u_v']:.0f} V / {r['i_a']*1000:.0f} mA  |  "
            f"f_Störung = {r['f_s']/1e3:.0f} kHz  |  Ziel: {r['daempfung_db']:.0f} dB  |  {anw}",
            color=self.TEXTF, fontsize=11, fontweight='bold', y=0.97
        )

        # ── Info-Box (oben rechts) ────────────────────────────────────────────
        idx_s   = np.argmin(np.abs(f - fs))
        d_at_fs = H_dB[idx_s]
        info = (
            f"L1 = {BauteilUtils.format_wert(L,'H')} (E12)\n"
            f"C1 = {BauteilUtils.format_wert(C,'F')} X7R\n"
            f"f₀ = {f0/1e3:.1f} kHz\n"
            f"Dämpfung @ fs = {abs(d_at_fs):.1f} dB\n"
            f"Q = {r['Q']:.2f}  {'✓' if r['Q']<5 else '⚠'}\n"
            f"ΔU = {r['u_drop']*1000:.1f} mV ({r['u_drop_pct']:.2f}%)"
        )
        fig.text(0.985, 0.94, info, transform=fig.transFigure,
                 fontsize=8.5, color=self.TEXTF, va='top', ha='right',
                 fontfamily='monospace',
                 bbox=dict(boxstyle='round,pad=0.5', fc=self.SURFACE, ec=self.GRID, lw=0.8))

        plt.savefig('emv_filter_auslegung.png', dpi=150, bbox_inches='tight',
                    facecolor=self.DUNKEL)
        print("  📊 Plot gespeichert: emv_filter_auslegung.png")
        plt.show()

    # ── Private Subplot-Methoden ──────────────────────────────────────────────

    def _style_ax(self, ax):
        """Wendet das dunkle Theme auf eine Axes-Instanz an."""
        ax.set_facecolor(self.SURFACE)
        ax.tick_params(colors=self.TEXTM, labelsize=9)
        ax.xaxis.label.set_color(self.TEXTM)
        ax.yaxis.label.set_color(self.TEXTM)
        ax.title.set_color(self.TEXTF)
        for sp in ax.spines.values():
            sp.set_edgecolor(self.GRID)
        ax.grid(True, which='major', color=self.GRID, linewidth=0.8, alpha=0.9)
        ax.grid(True, which='minor', color=self.GRID, linewidth=0.4, alpha=0.5)
        ax.set_xscale('log')

    def _plot_amplitudengang(self, ax, f, H_dB, H_ideal_dB, f0, fs, stufen, r, L, C):
        """Plot 1: Amplitudengang / Dämpfungsverlauf mit Annotationen."""
        self._style_ax(ax)
        ax.plot(f, H_ideal_dB, color=self.AKZENT3, linewidth=2.0, ls='--', alpha=0.7,
                label='Ideal (ohne Parasitics)')
        ax.plot(f, H_dB,       color=self.AKZENT1, linewidth=4.5,
                label=f'LC-Filter {stufen}-stufig (mit ESL/ESR)')

        ax.axvline(f0, color=self.AKZENT2, linewidth=1.5, ls=':', alpha=0.8)
        ax.axvline(fs, color=self.AKZENT4, linewidth=2.0, ls='--', alpha=0.9)
        ax.axhline(-r['daempfung_db'], color=self.AKZENT4, linewidth=1.2, ls=':', alpha=0.7)

        # Annotation: Dämpfung an Störfrequenz
        idx_s   = np.argmin(np.abs(f - fs))
        d_at_fs = H_dB[idx_s]
        ax.annotate(f'{abs(d_at_fs):.1f} dB\nbei {fs/1e3:.0f} kHz',
                    xy=(fs, d_at_fs), xytext=(fs*2.5, d_at_fs+15),
                    color=self.AKZENT4, fontsize=8.5,
                    arrowprops=dict(arrowstyle='->', color=self.AKZENT4, lw=1.0),
                    bbox=dict(boxstyle='round,pad=0.3', fc=self.SURFACE,
                              ec=self.AKZENT4, lw=0.8))

        # Annotation: Grenzfrequenz f0
        ax.annotate(f'f₀ = {f0/1e3:.1f} kHz',
                    xy=(f0, -3), xytext=(f0*0.2, -25),
                    color=self.AKZENT2, fontsize=8.5,
                    arrowprops=dict(arrowstyle='->', color=self.AKZENT2, lw=1.0),
                    bbox=dict(boxstyle='round,pad=0.3', fc=self.SURFACE,
                              ec=self.AKZENT2, lw=0.8))

        # Rolloff-Linie
        f_roll = np.array([f0*2, f0*200])
        h_roll = -40 * stufen * np.log10(f_roll / f0)
        ax.plot(f_roll, h_roll, color=self.TEXTM, lw=0.8, ls='-.', alpha=0.5,
                label=f'−{40*stufen} dB/Dek Rolloff')

        # CISPR 25 Bereich hervorheben
        ax.axvspan(150e3, 1e8, alpha=0.05, color=self.AKZENT2)
        ax.text(200e3, -85, 'CISPR 25', color=self.AKZENT2, fontsize=7.5, alpha=0.7)

        ax.set_xlabel('Frequenz [Hz]', fontsize=9)
        ax.set_ylabel('Dämpfung [dB]', fontsize=9)
        ax.set_title(
            f'Amplitudengang — LC-Filter {stufen}-stufig  '
            f'(L={BauteilUtils.format_wert(L,"H")}, C={BauteilUtils.format_wert(C,"F")})',
            fontsize=10)
        ax.set_ylim(-90, 25)
        ax.set_xlim(1e2, 1e8)
        ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))
        ax.legend(loc='lower left', fontsize=8,
                  facecolor=self.DUNKEL, edgecolor=self.GRID, labelcolor=self.TEXTF)

    def _plot_phasengang(self, ax, f, phase_deg, f0, fs, stufen):
        """Plot 2: Phasengang."""
        self._style_ax(ax)
        ax.plot(f, phase_deg, color=self.AKZENT5, linewidth=3.5)
        ax.axvline(f0, color=self.AKZENT2, linewidth=1.5, ls=':', alpha=0.7)
        ax.axvline(fs, color=self.AKZENT4, linewidth=1.5, ls='--', alpha=0.8)
        ax.axhline(-90*stufen, color=self.GRID, linewidth=1.0, ls=':')
        ax.set_xlabel('Frequenz [Hz]', fontsize=10, fontweight='bold')
        ax.set_ylabel('Phase [°]', fontsize=10, fontweight='bold')
        ax.set_title('Phasengang', fontsize=11, fontweight='bold')
        ax.set_ylim(-200, 10)
        ax.set_xlim(1e2, 1e8)
        ax.yaxis.set_major_locator(ticker.MultipleLocator(45))
        ax.yaxis.set_minor_locator(ticker.MultipleLocator(9))

    def _plot_eingangsimpedanz(self, ax, f, Z_in, Rl, f0, fs, r):
        """Plot 3: Eingangsimpedanz mit Resonanzpeak-Annotation."""
        self._style_ax(ax)
        Z_in_abs = np.abs(Z_in)

        ax.plot(f, Z_in_abs, color=self.AKZENT1, linewidth=3.5, label='Z_in Filter')
        ax.axhline(Rl,      color=self.AKZENT2, linewidth=1.5, ls=':', alpha=0.8,
                   label=f'Z_Last = {Rl:.0f} Ω')
        ax.axhline(r['z0'], color=self.AKZENT3, linewidth=1.2, ls='--', alpha=0.7,
                   label=f'Z₀ = {r["z0"]:.1f} Ω')
        ax.axvline(f0, color=self.AKZENT2, linewidth=1.5, ls=':', alpha=0.7)
        ax.axvline(fs, color=self.AKZENT4, linewidth=1.5, ls='--', alpha=0.8)

        # Resonanzpeak annotieren
        idx_peak = np.argmax(Z_in_abs[:len(f)//2])
        ax.annotate(f'Resonanz\n{Z_in_abs[idx_peak]:.1f} Ω\n@ {f[idx_peak]/1e3:.1f} kHz',
                    xy=(f[idx_peak], Z_in_abs[idx_peak]),
                    xytext=(f[idx_peak]*5, Z_in_abs[idx_peak]*1.3),
                    color=self.AKZENT1, fontsize=8,
                    arrowprops=dict(arrowstyle='->', color=self.AKZENT1, lw=1.0),
                    bbox=dict(boxstyle='round,pad=0.3', fc=self.SURFACE,
                              ec=self.AKZENT1, lw=0.8))

        ax.set_yscale('log')
        ax.set_xlabel('Frequenz [Hz]', fontsize=9)
        ax.set_ylabel('|Z_in| [Ω]', fontsize=9)
        ax.set_title('Eingangsimpedanz des Filters', fontsize=10)
        ax.set_xlim(1e2, 1e8)
        ax.legend(loc='upper right', fontsize=8,
                  facecolor=self.DUNKEL, edgecolor=self.GRID, labelcolor=self.TEXTF)

    def _plot_bauteil_impedanzen(self, ax, f, Z_C_ideal, Z_C_real, Z_L_real,
                                  Z_bp_total, Z_LC_ideal, Z_LC_real, fs, r, L, C):
        """Plot 4: Bauteil-Impedanzen inkl. Parasitics und SRF-Markierungen."""
        self._style_ax(ax)
        ax.set_yscale('log')

        ax.plot(f, Z_C_ideal,  color=self.TEXTM,   linewidth=1.5,   ls='--', alpha=0.6,
                label='C (ideal)')
        ax.plot(f, Z_C_real,   color=self.AKZENT5, linewidth=2.8,
                label=f'C = {BauteilUtils.format_wert(C,"F")} (mit ESL)')
        ax.plot(f, Z_L_real,   color=self.AKZENT1, linewidth=2.8,
                label=f'L = {BauteilUtils.format_wert(L,"H")}')
        ax.plot(f, Z_LC_ideal, color='#ff9f40', linewidth=2.5, ls='--', alpha=0.7,
                label='L+C (ideal, Serien)')
        ax.plot(f, Z_LC_real,  color='#ff5733', linewidth=3.0, ls='-',
                label='L+C (real, Serien)')
        ax.plot(f, Z_bp_total, color=self.AKZENT3, linewidth=2.5, ls='-.',
                label='C+Bypass (220n+100n+10n)')

        # SRF-Linien beschriften
        ax.axvline(r['srf_c'], color=self.AKZENT5, linewidth=1.2, ls=':', alpha=0.6)
        ax.axvline(r['srf_l'], color=self.AKZENT1, linewidth=1.2, ls=':', alpha=0.6)
        ax.text(r['srf_c']*1.1, 0.005, f"SRF(C)\n{r['srf_c']/1e6:.0f}MHz",
                color=self.AKZENT5, fontsize=7.5, alpha=0.9)
        ax.text(r['srf_l']*1.1, 0.005, f"SRF(L)\n{r['srf_l']/1e6:.0f}MHz",
                color=self.AKZENT1, fontsize=7.5, alpha=0.9)

        ax.axvline(fs, color=self.AKZENT4, linewidth=1.3, ls='--', alpha=0.7)
        ax.set_xlabel('Frequenz [Hz]', fontsize=10, fontweight='bold')
        ax.set_ylabel('Impedanz [Ω]', fontsize=10, fontweight='bold')
        ax.set_title('Bauteil-Impedanzen & Parasitics', fontsize=11, fontweight='bold')
        ax.set_xlim(1e2, 1e8)
        ax.set_ylim(1e-3, 1e5)
        ax.legend(loc='upper left', fontsize=6.5,
                  facecolor=self.DUNKEL, edgecolor=self.GRID, labelcolor=self.TEXTF, ncol=2)
