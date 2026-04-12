"""
bauteil_utils.py
----------------
Hilfsfunktionen für Bauteilwerte:
  - E12-Normreihe (nächsten Standardwert finden)
  - SI-Formatierung (µH, nF, kΩ …)

Keine Abhängigkeiten zu anderen Projektmodulen.
"""

import numpy as np


class BauteilUtils:
    """Hilfsfunktionen für Bauteilwerte: E12-Reihe und Wert-Formatierung."""

    E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

    @staticmethod
    def e12_naechster(wert, einheit_exp):
        """Gibt den nächsten E12-Normwert zurück.

        Parameters
        ----------
        wert        : gesuchter Wert in SI-Einheit (z.B. 4.7e-6 für 4.7 µH)
        einheit_exp : Exponent der Einheit (-6 für µH, -9 für nF, -3 für mH)
        """
        wert_norm = wert / (10 ** einheit_exp)
        dekade = np.floor(np.log10(wert_norm))
        kandidaten = []
        for e in BauteilUtils.E12:
            for d in [10**(dekade-1), 10**dekade, 10**(dekade+1)]:
                kandidaten.append(e * d * (10 ** einheit_exp))
        kandidaten = sorted(set([round(k, 15) for k in kandidaten]))
        for k in kandidaten:
            if k >= wert * 0.98:
                return k
        return kandidaten[-1]

    @staticmethod
    def format_wert(wert, einheit):
        """Formatiert einen Bauteilwert mit passender SI-Einheit.

        Beispiele: 4.7e-6 H  → '4.7 µH'
                   220e-9 F  → '220.0 nF'
                   1500 Ohm  → '1.50 kΩ'
        """
        if einheit == 'H':
            if wert >= 1e-3:
                return f"{wert*1e3:.1f} mH"
            elif wert >= 1e-6:
                return f"{wert*1e6:.1f} µH"
            else:
                return f"{wert*1e9:.1f} nH"
        elif einheit == 'F':
            if wert >= 1e-6:
                return f"{wert*1e6:.2f} µF"
            elif wert >= 1e-9:
                return f"{wert*1e9:.1f} nF"
            else:
                return f"{wert*1e12:.1f} pF"
        elif einheit == 'Ohm':
            if wert >= 1e3:
                return f"{wert/1e3:.2f} kΩ"
            else:
                return f"{wert:.2f} Ω"
        return str(wert)
