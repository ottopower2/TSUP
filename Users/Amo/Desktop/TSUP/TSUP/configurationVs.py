

# ==========================================
# RTM3004 Pulse1 Vs Konfiguration auf CH1
# Freeze bei Trigger
# ==========================================

import pyvisa


SCOPE_IP = "192.168.50.96"
rm= pyvisa.ResourceManager('@py')
scope = rm.open_resource(
    f"TCPIP::{SCOPE_IP}::INSTR"
)
scope.timeout = 5000

# Kanal CH1 EIN
scope.write("CHAN1:STAT ON")

# Vertikal für -100V Pulse
scope.write("CHAN1:SCAL 20")      # 20 V/div
scope.write("CHAN1:OFFS -40")     # Signal nach unten verschieben

# Zeitbasis
scope.write("TIM:SCAL 0.001")     # 1 ms/div
scope.write("TIM:POS 0")          # Trigger mittig

# Trigger auf CH1
scope.write("TRIG:A:TYPE EDGE")
scope.write("TRIG:A:SOUR CH1")

# Negative Flanke für Pulse1
scope.write("TRIG:A:EDGE:SLOP NEG")

# Trigger Level
scope.write("TRIG:A:LEV -10")

# Single Shot = Freeze nach Puls
scope.write("SING")