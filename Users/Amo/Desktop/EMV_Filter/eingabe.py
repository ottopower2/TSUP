"""
eingabe.py
----------
Interaktive Benutzereingaben über das Terminal mit Validierung.

Keine Abhängigkeiten zu anderen Projektmodulen.
"""


class Eingabe:
    """Statische Methoden für validierte Terminal-Eingaben."""

    @staticmethod
    def float(prompt, default, einheit="", min_val=0):
        """Fragt nach einer Gleitkommazahl; Enter übernimmt den Default-Wert.

        Parameters
        ----------
        prompt   : Anzeigetext für den Benutzer
        default  : Standardwert (wird bei leerem Enter verwendet)
        einheit  : Einheit als String, z.B. ' V' oder ' kHz'
        min_val  : Mindestwert (exklusiv) — verhindert negative oder Null-Eingaben
        """
        while True:
            try:
                eingabe = input(f"  {prompt} [{default}{einheit}]: ").strip()
                if eingabe == "":
                    return float(default)
                val = float(eingabe)
                if val <= min_val:
                    print(f"    ⚠  Wert muss > {min_val} sein.")
                    continue
                return val
            except ValueError:
                print("    ⚠  Bitte eine Zahl eingeben.")

    @staticmethod
    def wahl(prompt, optionen, default):
        """Fragt nach einer Auswahl aus einer festen Liste von Optionen.

        Parameters
        ----------
        prompt  : Anzeigetext für den Benutzer
        optionen: Liste der gültigen Optionen, z.B. [1, 2] oder ['kfz', 'industrie']
        default : Standardwert bei leerem Enter
        """
        while True:
            eingabe = input(f"  {prompt} {optionen} [{default}]: ").strip().lower()
            if eingabe == "":
                return default
            if eingabe in [str(o).lower() for o in optionen]:
                return eingabe
            print(f"    ⚠  Bitte eine der Optionen wählen: {optionen}")
