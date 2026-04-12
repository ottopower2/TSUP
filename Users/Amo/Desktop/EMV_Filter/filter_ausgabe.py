"""
filter_ausgabe.py
-----------------
Terminal-Ausgabe der Berechnungsergebnisse.

Enthält:
  FilterAusgabe  — drucke_ergebnisse() + drucke_daempfungstabelle()

Abhängigkeiten:
  bauteil_utils.BauteilUtils
"""

import numpy as np
from bauteil_utils import BauteilUtils


class FilterAusgabe:
    """
    Gibt alle Berechnungsergebnisse formatiert im Terminal aus.

    Parameters
    ----------
    ergebnis : dict — Rückgabe von FilterBerechnung.ergebnis
    """

    def __init__(self, ergebnis):
        self.r = ergebnis

    def drucke_ergebnisse(self):
        """Vollständige Ergebnisausgabe mit Sicherheitschecks und Stückliste."""
        r = self.r
        W = 60
        print("\n" + "═"*W)
        print("  EMV-LC-Tiefpassfilter — Auslegungsergebnis")
        print("═"*W)

        # ── Eingabeparameter ─────────────────────────────────────────────────
        print(f"\n  📥 Eingabeparameter")
        print(f"  {'Versorgungsspannung':<28} {r['u_v']:.1f} V")
        print(f"  {'Laststrom':<28} {r['i_a']*1000:.0f} mA")
        print(f"  {'Störfrequenz':<28} {r['f_s']/1e3:.0f} kHz")
        print(f"  {'Gewünschte Dämpfung':<28} {r['daempfung_db']:.0f} dB")
        print(f"  {'Filterstufenzahl':<28} {r['stufen']}")
        print(f"  {'Lastimpedanz Z_Last':<28} {BauteilUtils.format_wert(r['z_last'],'Ohm')}")

        # ── Grenzfrequenz ────────────────────────────────────────────────────
        print(f"\n  🔢 Berechnete Grenzfrequenz")
        print(f"  {'f₀ (ideal)':<28} {r['f0']/1e3:.2f} kHz")
        print(f"  {'f₀ (mit E12-Werten)':<28} {r['f0_real']/1e3:.2f} kHz")

        # ── Bauteilwerte ─────────────────────────────────────────────────────
        print(f"\n  🔧 Bauteilwerte")
        print(f"  {'Spule L (ideal)':<28} {BauteilUtils.format_wert(r['L_ideal'],'H')}")
        print(f"  {'Spule L (E12)':<28} {BauteilUtils.format_wert(r['L_e12'],'H')}")
        print(f"  {'Kondensator C (ideal)':<28} {BauteilUtils.format_wert(r['C_ideal'],'F')}")
        print(f"  {'Kondensator C (E12)':<28} {BauteilUtils.format_wert(r['C_e12'],'F')}")
        print(f"  {'Char. Impedanz Z₀':<28} {BauteilUtils.format_wert(r['z0'],'Ohm')}")

        # ── Sicherheitsdimensionierung ────────────────────────────────────────
        print(f"\n  ✅ Sicherheitsdimensionierung")
        print(f"  {'I_sat (min) Spule':<28} {r['i_sat_min']*1000:.0f} mA  (= 1.5 × {r['i_a']*1000:.0f} mA)")
        u_std = max(16, int(np.ceil(r['u_cap_min'] / 6.3) * 6.3 + 0.1))
        print(f"  {'U_min Kondensator':<28} {r['u_cap_min']:.1f} V  → Standard: {u_std:.0f} V wählen")
        print(f"  {'Kondensatortyp':<28} X7R oder X5R (kein Y5V!)")

        # ── Checks & Warnungen ────────────────────────────────────────────────
        print(f"\n  📊 Checks & Warnungen")
        ok_drop   = r['u_drop_pct']    < 2.0
        ok_q      = r['Q']             < 5.0
        ok_srf    = r['srf_l']         > 10 * r['f0_real']
        ok_daempf = r['daempfung_real'] >= r['daempfung_db'] * 0.95

        sym_ok   = "✅"
        sym_warn = "⚠️ "

        print(f"  {sym_ok if ok_drop   else sym_warn} Spannungsabfall:   {r['u_drop']*1000:.1f} mV ({r['u_drop_pct']:.2f}%)  {'< 2% ✓' if ok_drop else '> 2% WARNUNG!'}")
        print(f"  {sym_ok if ok_q      else sym_warn} Q-Faktor:          {r['Q']:.2f}  {'→ keine Resonanzüberhöhung' if ok_q else '→ WARNUNG: Resonanzüberhöhung möglich!'}")
        print(f"  {sym_ok if ok_srf    else sym_warn} SRF Spule (est.):  {r['srf_l']/1e6:.1f} MHz  {'>> 10×f₀ ✓' if ok_srf else '→ SRF zu niedrig!'}")
        print(f"  {sym_ok if ok_daempf else sym_warn} Dämpfung @ f_Stör: {r['daempfung_real']:.1f} dB  {'≥ Ziel ✓' if ok_daempf else '→ Ziel nicht erreicht!'}")
        print(f"  {'ℹ️ '} SRF Kondensator (est.): {r['srf_c']/1e6:.1f} MHz")

        # ── HF-Bypass ─────────────────────────────────────────────────────────
        print(f"\n  📋 HF-Bypass-Empfehlung (parallel zu C)")
        print(f"  {'C_bypass1':<28} 100 nF  X7R 25V 0402 (SRF ≈ 60 MHz)")
        print(f"  {'C_bypass2':<28}  10 nF  X7R 25V 0402 (SRF ≈ 200 MHz)")

        # ── Stückliste ────────────────────────────────────────────────────────
        print(f"\n  🏷️  Stückliste (Empfehlungen)")
        l_uh = r['L_e12'] * 1e6
        if l_uh <= 10:
            l_bst = f"Würth 744043{int(l_uh):03d}  (oder ähnlich)"
        elif l_uh <= 100:
            l_bst = f"Würth 7447021{int(l_uh):03d} / TDK MLZ2012 Serie"
        else:
            l_bst = f"Würth 744051 Serie / Bourns SRR1260 Serie"

        print(f"  L1  {BauteilUtils.format_wert(r['L_e12'],'H'):<12} I_sat≥{r['i_sat_min']*1000:.0f}mA  {l_bst}")
        print(f"  C1  {BauteilUtils.format_wert(r['C_e12'],'F'):<12} X7R 25V   Murata GRM21BR71E / TDK C2012X7R")
        print(f"  C2  100 nF        X7R 25V   Murata GRM155R71E104KA88 (0402)")
        print(f"  C3   10 nF        X7R 25V   TDK C1005X7R1E103K050BB  (0402)")

        print("\n" + "═"*W + "\n")

    def drucke_daempfungstabelle(self, f_punkte_khz):
        """Gibt eine tabellarische Übersicht der Dämpfung je Frequenzpunkt aus.

        Parameters
        ----------
        f_punkte_khz : Liste von Frequenzpunkten [kHz]
        """
        r = self.r
        print("  📉 Dämpfungstabelle")
        print(f"  {'Frequenz':<20} {'Dämpfung [dB]':>15}")
        print("  " + "-"*36)
        for f_khz in f_punkte_khz:
            f = f_khz * 1e3
            d = r['stufen'] * 40 * np.log10(f / r['f0_real']) if f > r['f0_real'] else 0.0
            marker  = " ← ZIEL" if abs(f - r['f_s'])     < r['f_s']     * 0.1  else ""
            marker2 = " ← f₀"   if abs(f - r['f0_real']) < r['f0_real'] * 0.15 else ""
            print(f"  {f_khz:>8.0f} kHz         {d:>8.1f} dB{marker}{marker2}")
        print()
