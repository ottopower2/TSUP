"""
filter_berechnung.py
--------------------
Kernberechnung des LC-Tiefpassfilters.

Enthält:
  FilterBerechnung  — berechnet L, C, Q, f0, Dämpfung, Parasitics
                      und stellt statische Methoden für H(jω) und Z_bypass bereit.

Abhängigkeiten:
  bauteil_utils.BauteilUtils
"""

import numpy as np
from bauteil_utils import BauteilUtils


class FilterBerechnung:
    """
    Berechnet alle Parameter eines LC-Tiefpassfilters.

    Nach der Initialisierung liegen alle Ergebnisse in self.ergebnis (dict).

    Parameters
    ----------
    u_v          : Versorgungsspannung [V]
    i_ma         : Laststrom [mA]
    f_stoer_khz  : Störfrequenz [kHz]
    daempfung_db : Gewünschte Dämpfung [dB] bei f_stoer
    stufen       : 1 oder 2 (Filterpole)
    z0_faktor    : Z0 als Anteil von Z_Last (Standard: 0.25)
    """

    def __init__(self, u_v, i_ma, f_stoer_khz, daempfung_db, stufen, z0_faktor=0.25):
        self.u_v          = u_v
        self.i_ma         = i_ma
        self.f_stoer_khz  = f_stoer_khz
        self.daempfung_db = daempfung_db
        self.stufen       = stufen
        self.z0_faktor    = z0_faktor
        self.ergebnis     = self._berechne()

    def _berechne(self):
        """Führt alle Berechnungen durch und gibt ein Ergebnis-Dict zurück."""
        r = {}

        f_s    = self.f_stoer_khz * 1e3   # Hz
        i_a    = self.i_ma * 1e-3          # A
        z_last = self.u_v / i_a            # Lastimpedanz [Ω]

        r['u_v']          = self.u_v
        r['i_a']          = i_a
        r['f_s']          = f_s
        r['daempfung_db'] = self.daempfung_db
        r['z_last']       = z_last
        r['stufen']       = self.stufen

        # ── Grenzfrequenz ────────────────────────────────────────────────────
        # n-stufig: Dämpfung ≈ n × 40 dB/Dekade  →  f0 = f_s / 10^(D / (n×40))
        f0 = f_s / (10 ** (self.daempfung_db / (self.stufen * 40)))
        r['f0'] = f0

        # ── Charakteristische Impedanz ───────────────────────────────────────
        z0 = z_last * self.z0_faktor
        r['z0'] = z0

        # ── Ideale L und C ───────────────────────────────────────────────────
        omega0   = 2 * np.pi * f0
        L_ideal  = z0 / omega0
        C_ideal  = 1 / (z0 * omega0)
        r['L_ideal'] = L_ideal
        r['C_ideal'] = C_ideal

        # ── E12-Normwerte ────────────────────────────────────────────────────
        L_e12 = BauteilUtils.e12_naechster(L_ideal, -6)   # µH-Bereich
        C_e12 = BauteilUtils.e12_naechster(C_ideal, -9)   # nF-Bereich

        if C_ideal >= 500e-9:                              # Bereich → µF
            C_e12 = BauteilUtils.e12_naechster(C_ideal, -6)
        if L_ideal >= 1e-3:                                # Bereich → mH
            L_e12 = BauteilUtils.e12_naechster(L_ideal, -3)

        r['L_e12'] = L_e12
        r['C_e12'] = C_e12

        # ── Tatsächliche f0 mit E12-Werten ───────────────────────────────────
        f0_real = 1 / (2 * np.pi * np.sqrt(L_e12 * C_e12))
        r['f0_real'] = f0_real

        # ── Q-Faktor (Güte relativ zur Last) ─────────────────────────────────
        Q = z_last / np.sqrt(L_e12 / C_e12)
        r['Q'] = Q

        # ── Sicherheitsdimensionierung ────────────────────────────────────────
        r['i_sat_min'] = i_a * 1.5         # min. Sättigungsstrom Spule
        r['u_cap_min'] = self.u_v * 1.25   # min. Spannungsfestigkeit Kondensator

        # ── Spannungsabfall über DC-Widerstand der Spule ─────────────────────
        rdc_schaetz      = 0.3 * (L_e12 / 47e-6)   # grobe Schätzung [Ω]
        r['rdc_schaetz'] = rdc_schaetz
        r['u_drop']      = rdc_schaetz * i_a
        r['u_drop_pct']  = r['u_drop'] / self.u_v * 100

        # ── Parasitäre Parameter ──────────────────────────────────────────────
        esl_c    = 1e-9                                        # ESL Kondensator (0805 SMD)
        srf_c    = 1 / (2 * np.pi * np.sqrt(esl_c * C_e12))   # Eigenresonanz C
        srf_l    = 10e6 / np.sqrt(L_e12 / 1e-6)               # Eigenresonanz L (Schätzung)
        r['esl_c'] = esl_c
        r['srf_c'] = srf_c
        r['srf_l'] = srf_l

        # ── HF-Bypass-Kondensatoren ───────────────────────────────────────────
        r['c_bypass1'] = 100e-9   # 100 nF
        r['c_bypass2'] =  10e-9   #  10 nF

        # ── Tatsächliche Dämpfung bei Störfrequenz ────────────────────────────
        r['daempfung_real'] = self.stufen * 40 * np.log10(f_s / f0_real)

        return r

    # ── Statische Methoden (auch von FilterPlot verwendet) ───────────────────

    @staticmethod
    def uebertragung_lc(f_arr, L, C, R_last, stufen, esl=1e-9, esr=0.01):
        """
        Berechnet H(jω) und Eingangsimpedanz Z_in des LC-Filters.

        Berücksichtigt ESL und ESR des Kondensators sowie die Lastimpedanz.

        Parameters
        ----------
        f_arr  : Frequenzarray [Hz]
        L      : Induktivität [H]
        C      : Kapazität [F]
        R_last : Lastimpedanz [Ω]
        stufen : 1 oder 2
        esl    : Serien-Induktivität des Kondensators [H]
        esr    : Serienwiderstand des Kondensators [Ω]

        Returns
        -------
        H    : komplexe Übertragungsfunktion (Array)
        Z_in : Eingangsimpedanz (komplexes Array)
        """
        omega = 2 * np.pi * f_arr
        Z_C   = esr + 1j * omega * esl + 1 / (1j * omega * C)
        Z_L   = 1j * omega * L

        if stufen == 1:
            Z_par = (Z_C * R_last) / (Z_C + R_last)
            H     = Z_par / (Z_L + Z_par)
            Z_in  = Z_L + Z_par
        else:
            # 2-stufig: L/2 — C — L/2 — C — R  (π-Näherung)
            L2   = L / 2
            Z_L2 = 1j * omega * L2
            Z_stufe2_par = (Z_C * R_last) / (Z_C + R_last)
            Z_stufe2     = Z_L2 + Z_stufe2_par
            Z_par1 = (Z_C * Z_stufe2) / (Z_C + Z_stufe2)
            H_1    = Z_par1 / (Z_L2 + Z_par1)
            Z_par2 = (Z_C * R_last) / (Z_C + R_last)
            H_2    = Z_par2 / (Z_L2 + Z_par2)
            H      = H_1 * H_2
            Z_in   = Z_L2 + Z_par1

        return H, Z_in

    @staticmethod
    def bypass_impedanz(f_arr, C_values, esl_vals):
        """Gesamtimpedanz von parallel geschalteten Bypass-Kondensatoren.

        Parameters
        ----------
        f_arr    : Frequenzarray [Hz]
        C_values : Liste der Kapazitäten [F]
        esl_vals : Liste der zugehörigen ESL-Werte [H]
        """
        omega   = 2 * np.pi * f_arr
        Y_total = np.zeros(len(f_arr), dtype=complex)
        for C, esl in zip(C_values, esl_vals):
            Z_c      = 1j * omega * esl + 1 / (1j * omega * C) + 0.01
            Y_total += 1 / Z_c
        return 1 / Y_total
