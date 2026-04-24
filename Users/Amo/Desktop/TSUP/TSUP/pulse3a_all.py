# ==========================================================
# RTM3004 AUTO TEST SCRIPT
# ISO 7637-2 Pulse 3a  (Us = -150 V, 12 V system)
#
# Waveform: repeating burst of fast negative pulses
#   Each individual pulse:
#     UA (13.5 V) -> falls to Us (-150 V) -> recovers to UA
#     tr = 5 ns   (0.1·Us → 0.9·Us on fall)
#     td = 150 ns (at 0.9·Us level)
#     t1 = 100 µs (pulse repetition period)
#   Burst envelope:
#     t4 = 10 ms  (burst ON duration)
#     t5 = 90 ms  (burst OFF / pause)
#
# Measurement levels:
#   0.1·Us = -15 V   (10 % of -150 V)
#   0.9·Us = -135 V  (90 % of -150 V)
#
# Captures (in order):
#   1. Pulse3a_Us  — MIN measurement + Y cursors
#   2. Pulse3a_tr  — cursor ΔX  (2 ns/div, trigger -75 V NEG)
#   3. Pulse3a_td  — cursor ΔX  (50 ns/div, trigger -135 V NEG)
#   4. Pulse3a_t1  — PER measurement  (20 µs/div)
#   5. Pulse3a_t4  — cursor ΔX  (5 ms/div, shows burst ON)
#   6. Pulse3a_t5  — cursor ΔX  (50 ms/div, shows burst pause)
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
TRIGGER_TIMEOUT = 60
CHANNEL         = "CHAN1"
MEAS_SOURCE     = "C1"
TRIGGER_SOURCE  = "C1"

VERTICAL_SCALE  = 20             # V/div  →  200 V range
VERTICAL_OFFSET = -65            # V      →  center -65 V  (range -165 V … +35 V)

UA_NOMINAL  =  13.5              # battery voltage [V]
US_NOMINAL  = -150.0             # pulse peak voltage [V]

_01_US = round(0.1 * US_NOMINAL, 1)   # -15.0 V
_09_US = round(0.9 * US_NOMINAL, 1)   # -135.0 V
_MID   = round((_01_US + _09_US) / 2, 1)  # -75.0 V  (trigger midpoint)

SCOPE_RESOURCES = (
    f"TCPIP0::{SCOPE_IP}::inst0::INSTR",
    f"TCPIP0::{SCOPE_IP}::5025::SOCKET",
)

CAPTURES = [
    # --------------------------------------------------
    # Us  —  peak negative voltage
    # --------------------------------------------------
    {
        "name": "Pulse3a_Us",
        "title": "Us",
        "trigger_level": _MID,       # -75 V, NEG
        "time_scale": 50e-9,         # 50 ns/div  →  500 ns  (shows single pulse)
        "time_position": 0,
        "measure": "MIN",
        "cursor_y1": 0,
        "cursor_y2": US_NOMINAL,     # -150 V nominal; updated to measured MIN
    },
    # --------------------------------------------------
    # tr  —  rise (fall) time  0.1·Us → 0.9·Us  (≈ 5 ns)
    #         trigger at midpoint (-75 V), 2 ns/div
    #         cursor_x1 ≈ -2.5 ns  (at 0.1·Us = -15 V)
    #         cursor_x2 ≈ +2.5 ns  (at 0.9·Us = -135 V)
    # --------------------------------------------------
    {
        "name": "Pulse3a_tr",
        "title": "tr",
        "trigger_level": _MID,
        "time_scale": 2e-9,          # 2 ns/div  →  20 ns window
        "time_position": 0,
        "measure": None,
        "cursor_x1": -2.5e-9,        # tune after first run
        "cursor_x2":  2.5e-9,        # tune after first run
    },
    # --------------------------------------------------
    # td  —  pulse duration at 0.9·Us  (≈ 150 ns)
    #         trigger directly at 0.9·Us (-135 V) on the fall
    #         cursor_x1 = 0  (trigger = 0.9·Us crossing on fall)
    #         cursor_x2 ≈ +150 ns  (0.9·Us crossing on recovery)
    # --------------------------------------------------
    {
        "name": "Pulse3a_td",
        "title": "td",
        "trigger_level": _09_US,     # -135 V  (0.9·Us)
        "time_scale": 50e-9,         # 50 ns/div  →  500 ns window
        "time_position": 0,
        "measure": None,
        "cursor_x1":   0,            # 0.9·Us on fall  = trigger point
        "cursor_x2": 150e-9,         # 0.9·Us on recovery ≈ 150 ns later
    },
    # --------------------------------------------------
    # t1  —  pulse repetition period  (≈ 100 µs)
    # --------------------------------------------------
    {
        "name": "Pulse3a_t1",
        "title": "t1",
        "trigger_level": _MID,
        "time_scale": 20e-6,         # 20 µs/div  →  200 µs window
        "time_position": 0,
        "measure": "PER",
    },
    # --------------------------------------------------
    # t4  —  burst ON duration  (≈ 10 ms)
    #         cursor_x1 = 0   (start of burst = trigger)
    #         cursor_x2 = 10 ms  (end of burst)
    # --------------------------------------------------
    {
        "name": "Pulse3a_t4",
        "title": "t4",
        "trigger_level": _MID,
        "time_scale": 5e-3,          # 5 ms/div  →  50 ms window
        "time_position": 0,
        "measure": None,
        "cursor_x1":  0,
        "cursor_x2":  10e-3,         # tune after first run
    },
    # --------------------------------------------------
    # t5  —  burst pause  (≈ 90 ms)
    #         trigger on first pulse of burst
    #         cursor_x1 = 10 ms  (end of burst)
    #         cursor_x2 = 100 ms (start of next burst = t4 + t5)
    # --------------------------------------------------
    {
        "name": "Pulse3a_t5",
        "title": "t5",
        "trigger_level": _MID,
        "time_scale": 50e-3,         # 50 ms/div  →  500 ms window
        "time_position": 0,
        "measure": None,
        "cursor_x1":  10e-3,         # end of burst  (tune after first run)
        "cursor_x2": 100e-3,         # start of next burst = t4 + t5
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


def setup_clean_trigger(trigger_level, slope="NEG"):
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
    slope = capture.get("trigger_slope", "NEG")
    setup_clean_trigger(capture["trigger_level"], slope)
    scope.write("*CLS")
    print(f"Starte Pulse3a  [trigger {capture['trigger_level']} V, {slope}]...")
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
    slope = capture.get("trigger_slope", "NEG")
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
        if delta_s < 1e-6:
            return f"{delta_s * 1e9:.1f} ns"
        if delta_s < 1e-3:
            return f"{delta_s * 1e6:.3f} us"
        return f"{delta_s * 1e3:.3f} ms"
    except (pyvisa.errors.VisaIOError, ValueError):
        delta_s = abs(capture["cursor_x2"] - capture["cursor_x1"])
        if delta_s < 1e-6:
            return f"{delta_s * 1e9:.1f} ns (config)"
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

print(f"\nReferenzspannungen:")
print(f"  UA     = {UA_NOMINAL} V")
print(f"  Us     = {US_NOMINAL} V")
print(f"  0.1·Us = {_01_US} V   (tr start / td end level)")
print(f"  0.9·Us = {_09_US} V   (tr end  / td level)")
print(f"  Trigger-Mitte = {_MID} V")

for capture in CAPTURES:
    run_capture(capture)

# ----------------------------------------------------------
# Ende
# ----------------------------------------------------------
scope.close()
rm.close()

print("\nFERTIG - Alle Bilder gespeichert.")
