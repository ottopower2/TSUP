# ==========================================================
# RTM3004 AUTO TEST SCRIPT
# ISO 7637-2 Pulse 2b  (Us = -10 V, 12 V system)
#
# Waveform:
#   UA (13.5 V) ──> falls through 0.9·UA (12.15 V)
#                ──> 0.1·UA (1.35 V)   ← t12 measured here (1 ms)
#                ──> 0.9·Us  (-9 V)    ← tr  measured here (1 ms)
#                ──> minimum Us (-10 V)
#                ──> recovery: 0.1·Us (-1 V) → 0.1·UA (1.35 V) ← t6 (1 ms)
#                ──> full recovery to UA       ← td = 0.2 … 2 s
#
# Captures (in order):
#   1. Pulse2b_Us  — MIN voltage measurement + Y cursors
#   2. Pulse2b_t12 — cursor ΔX  (0.9·UA → 0.1·UA, NEG)
#   3. Pulse2b_tr  — cursor ΔX  (0.1·UA → 0.9·Us, NEG)
#   4. Pulse2b_t6  — cursor ΔX  (0.1·Us → 0.1·UA, POS recovery)
#   5. Pulse2b_td  — NWID measurement  (full negative pulse width)
# ==========================================================

import pyvisa
import time
import os
from datetime import datetime

# ----------------------------------------------------------
# Einstellungen
# ----------------------------------------------------------
SCOPE_IP        = "192.168.50.96"
SAVE_PATH       = os.path.dirname(os.path.abspath(__file__))
TRIGGER_TIMEOUT = 30
CHANNEL         = "CHAN1"
MEAS_SOURCE     = "C1"
TRIGGER_SOURCE  = "C1"
DEFAULT_SLOPE   = "NEG"          # most captures trigger on the falling edge

VERTICAL_SCALE  = 5              # V/div  →  ±25 V from center
VERTICAL_OFFSET = 2              # V      →  center +2 V  (range −23 V … +27 V)

UA_NOMINAL  =  13.5              # battery voltage  [V]
US_NOMINAL  = -10.0              # pulse peak voltage [V]  (negative)

# Measurement levels derived from the ISO standard
_09_UA = round(0.9 * UA_NOMINAL, 2)   #  12.15 V
_01_UA = round(0.1 * UA_NOMINAL, 2)   #   1.35 V
_09_US = round(0.9 * US_NOMINAL, 2)   #  −9.0  V
_01_US = round(0.1 * US_NOMINAL, 2)   #  −1.0  V

SCOPE_RESOURCES = (
    f"TCPIP0::{SCOPE_IP}::inst0::INSTR",
    f"TCPIP0::{SCOPE_IP}::5025::SOCKET",
)

# ----------------------------------------------------------
# Trigger midpoints (used as trigger level for each capture)
# ----------------------------------------------------------
_MID_T12 = round((_09_UA + _01_UA) / 2, 2)   #  ~6.75 V
_MID_TR  = round((_01_UA + _09_US) / 2, 2)   #  ~-3.8 V
_MID_T6  = round((_01_US + _01_UA) / 2, 2)   #  ~0.18 V  (recovery, POS slope)

CAPTURES = [
    # --------------------------------------------------
    # Us  —  peak negative voltage, wide view
    # --------------------------------------------------
    {
        "name": "Pulse2b_Us",
        "title": "Us",
        "trigger_level": -5.0,
        "trigger_slope": "NEG",
        "time_scale": 1.0,           # 1 s/div  →  10 s window (shows full td)
        "time_position": 0,
        "measure": "MIN",
        "cursor_y1": 0,
        "cursor_y2": US_NOMINAL,     # −10 V nominal; updated to measured MIN
    },
    # --------------------------------------------------
    # t12  —  from 0.9·UA (12.15 V) to 0.1·UA (1.35 V)
    # --------------------------------------------------
    {
        "name": "Pulse2b_t12",
        "title": "t12",
        "trigger_level": _MID_T12,
        "trigger_slope": "NEG",
        "time_scale": 500e-6,        # 500 µs/div  →  5 ms window
        "time_position": 0,
        "measure": None,
        "cursor_x1": -0.5e-3,        # ≈ 0.9·UA crossing  (tune after first run)
        "cursor_x2":  0.5e-3,        # ≈ 0.1·UA crossing  (tune after first run)
    },
    # --------------------------------------------------
    # tr  —  from 0.1·UA (1.35 V) to 0.9·Us (−9 V)
    # --------------------------------------------------
    {
        "name": "Pulse2b_tr",
        "title": "tr",
        "trigger_level": _MID_TR,
        "trigger_slope": "NEG",
        "time_scale": 500e-6,        # 500 µs/div  →  5 ms window
        "time_position": 0,
        "measure": None,
        "cursor_x1": -0.5e-3,        # ≈ 0.1·UA crossing  (tune after first run)
        "cursor_x2":  0.5e-3,        # ≈ 0.9·Us crossing  (tune after first run)
    },
    # --------------------------------------------------
    # t6  —  recovery from 0.1·Us (−1 V) to 0.1·UA (1.35 V)
    # --------------------------------------------------
    {
        "name": "Pulse2b_t6",
        "title": "t6",
        "trigger_level": _MID_T6,
        "trigger_slope": "POS",      # signal is rising during recovery
        "time_scale": 500e-6,        # 500 µs/div  →  5 ms window
        "time_position": 0,
        "measure": None,
        "cursor_x1": -0.5e-3,        # ≈ 0.1·Us crossing  (tune after first run)
        "cursor_x2":  0.5e-3,        # ≈ 0.1·UA crossing  (tune after first run)
    },
    # --------------------------------------------------
    # td  —  total negative pulse duration
    # --------------------------------------------------
    {
        "name": "Pulse2b_td",
        "title": "td",
        "trigger_level": -5.0,
        "trigger_slope": "NEG",
        "time_scale": 1.0,           # 1 s/div  →  10 s window
        "time_position": 0,
        "measure": "NWID",           # negative pulse width
    },
]

os.makedirs(SAVE_PATH, exist_ok=True)

# ----------------------------------------------------------
# Verbindung
# ----------------------------------------------------------
try:
    rm = pyvisa.ResourceManager('@py')
except ValueError as exc:
    raise SystemExit(
        "PyVISA backend fehlt. Installiere ihn mit:\n"
        "  python -m pip install pyvisa-py\n"
    ) from exc


def open_scope(resource_manager):
    last_error = None
    for resource in SCOPE_RESOURCES:
        try:
            print("Verbinde mit:", resource)
            instrument = resource_manager.open_resource(resource)
            instrument.timeout = 5000
            instrument.read_termination  = "\n"
            instrument.write_termination = "\n"
            return instrument
        except pyvisa.errors.VisaIOError as exc:
            last_error = exc
            print("Verbindung fehlgeschlagen:", exc)
    raise SystemExit(
        f"Oszilloskop nicht erreichbar unter {SCOPE_IP}.\n"
        "Bitte pruefen:\n"
        "- Ist das Oszilloskop eingeschaltet?\n"
        "- Ist der PC im gleichen Netzwerk?\n"
        "- Stimmt die IP-Adresse am Oszilloskop?\n"
        "- Ist LAN/SCPI/VXI-11 am Oszilloskop aktiviert?\n"
        f"Letzter VISA-Fehler: {last_error}"
    )


scope = open_scope(rm)
scope.timeout = 5000
print(scope.query("*IDN?").strip())

# ----------------------------------------------------------
# Hilfsfunktionen
# ----------------------------------------------------------
def write_optional(command):
    try:
        scope.write(command)
    except pyvisa.errors.VisaIOError:
        pass


def wait_trigger(timeout=TRIGGER_TIMEOUT):
    old_timeout = scope.timeout
    scope.timeout = int((timeout + 5) * 1000)
    try:
        state = scope.query("*OPC?").strip()
        return state == "1"
    except pyvisa.errors.VisaIOError as exc:
        print("Trigger Timeout:", exc)
        return False
    finally:
        scope.timeout = old_timeout


def setup_clean_trigger(trigger_level, slope):
    scope.write("TRIG:A:TYPE EDGE")
    scope.write(f"TRIG:A:SOUR {TRIGGER_SOURCE}")
    scope.write(f"TRIG:A:EDGE:SLOP {slope}")
    scope.write(f"TRIG:A:LEV {trigger_level}")
    write_optional("TRIG:A:MODE NORM")
    write_optional("TRIG:A:COUP DC")
    write_optional("ACQ:MODE HRES")
    write_optional("ACQ:POIN:AUTO RES")


def screenshot(name):
    filename = os.path.join(
        SAVE_PATH,
        name + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"
    )
    scope.write("HCOP:DEV:LANG PNG")
    scope.write("HCOP:DEST 'REMOTE'")
    data = scope.query_binary_values("HCOP:DATA?", datatype='B', container=bytes)
    with open(filename, "wb") as f:
        f.write(data)
    print("Gespeichert:", filename)


def single_wait(capture):
    slope = capture.get("trigger_slope", DEFAULT_SLOPE)
    setup_clean_trigger(capture["trigger_level"], slope)
    scope.write("*CLS")
    print(f"Starte jetzt Pulse2b  [trigger {capture['trigger_level']} V, {slope}]...")
    scope.write("SING")
    ok = wait_trigger()
    if not ok:
        print("Kein Trigger erkannt")
        return False
    print("Trigger erkannt")
    time.sleep(1)
    return True


def reset_measure():
    for i in range(1, 5):
        try:
            scope.write(f"MEAS{i}:STAT OFF")
        except Exception:
            pass


def configure_capture(capture):
    slope = capture.get("trigger_slope", DEFAULT_SLOPE)
    setup_clean_trigger(capture["trigger_level"], slope)
    scope.write(f"{CHANNEL}:STAT ON")
    scope.write(f"{CHANNEL}:SCAL {VERTICAL_SCALE}")
    scope.write(f"{CHANNEL}:OFFS {VERTICAL_OFFSET}")
    scope.write(f"TIM:SCAL {capture['time_scale']}")
    scope.write(f"TIM:POS {capture['time_position']}")
    configure_cursors(capture)


def configure_cursors(capture):
    has_x = "cursor_x1" in capture and "cursor_x2" in capture
    has_y = "cursor_y1" in capture and "cursor_y2" in capture

    if not has_x and not has_y:
        write_optional("CURS:STAT OFF")
        return

    write_optional("CURS:STAT ON")
    write_optional("CURS:SOUR " + MEAS_SOURCE)

    if has_x:
        write_optional("CURS:FUNC VERT")
        write_optional("CURS:TRAC ON")
        write_optional(f"CURS:X1P {capture['cursor_x1']}")
        write_optional(f"CURS:X2P {capture['cursor_x2']}")

    if has_y:
        write_optional("CURS:FUNC HOR")
        write_optional(f"CURS:Y1P {capture['cursor_y1']}")
        write_optional(f"CURS:Y2P {capture['cursor_y2']}")


def read_cursor_delta(capture):
    try:
        x1 = float(scope.query("CURS:X1P?").strip())
        x2 = float(scope.query("CURS:X2P?").strip())
        delta_s = abs(x2 - x1)
        if delta_s < 1e-3:
            return f"{delta_s * 1e6:.3f} us"
        return f"{delta_s * 1e3:.3f} ms"
    except (pyvisa.errors.VisaIOError, ValueError):
        delta_s = abs(capture["cursor_x2"] - capture["cursor_x1"])
        if delta_s < 1e-3:
            return f"{delta_s * 1e6:.3f} us (config)"
        return f"{delta_s * 1e3:.3f} ms (config)"


def run_capture(capture):
    print(f"\n--- {capture['title']} ---")
    configure_capture(capture)

    if not single_wait(capture):
        return

    if capture.get("measure") is None:
        value = read_cursor_delta(capture)
        print(f"{capture['title']}:", value)
    else:
        reset_measure()
        scope.write(f"MEAS1:SOUR {MEAS_SOURCE}")
        scope.write(f"MEAS1:MAIN {capture['measure']}")
        scope.write("MEAS1:STAT ON")
        time.sleep(0.5)

        try:
            value = scope.query("MEAS1:RES:ACT?").strip()
            print(f"{capture['title']}:", value)
            if "cursor_y2" in capture:
                try:
                    write_optional(f"CURS:Y2P {float(value)}")
                except ValueError:
                    pass
        except pyvisa.errors.VisaIOError as exc:
            try:
                err = scope.query("SYST:ERR?").strip()
            except Exception:
                err = str(exc)
            print(f"{capture['title']} Messwert konnte nicht gelesen werden: {err}")

    screenshot(capture["name"])


# ----------------------------------------------------------
# Grundsetup
# ----------------------------------------------------------
scope.write("*RST")
time.sleep(2)
scope.write("*CLS")

scope.write(f"{CHANNEL}:STAT ON")
scope.write(f"{CHANNEL}:SCAL {VERTICAL_SCALE}")
scope.write(f"{CHANNEL}:OFFS {VERTICAL_OFFSET}")

print(f"\nReferenzspannungen (12-V-System):")
print(f"  UA        = {UA_NOMINAL} V")
print(f"  Us        = {US_NOMINAL} V")
print(f"  0.9·UA    = {_09_UA} V")
print(f"  0.1·UA    = {_01_UA} V")
print(f"  0.9·Us    = {_09_US} V")
print(f"  0.1·Us    = {_01_US} V")

for capture in CAPTURES:
    run_capture(capture)

# ----------------------------------------------------------
# Ende
# ----------------------------------------------------------
scope.close()
rm.close()

print("\nFERTIG - Alle Bilder gespeichert.")
