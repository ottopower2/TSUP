# ==========================================================
# RTM3004 AUTO TEST SCRIPT
# ISO 7637-2 Pulse 2a (+75 V)
# Automatisch:
# 1. Us  Screenshot + MAX-Messung
# 2. tr  Screenshot + Cursor ΔX
# 3. td  Screenshot + Cursor ΔX
# 4. t1  Screenshot + Periodenmessung
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
TRIGGER_SLOPE   = "POS"          # Pulse 2a is positive-going
VERTICAL_SCALE  = 10             # V/div  → 100 V full range
VERTICAL_OFFSET = 50             # V      → center at +50 V (shows 0…+100 V)
US_NOMINAL      = 75             # ISO nominal pulse voltage [V]

SCOPE_RESOURCES = (
    f"TCPIP0::{SCOPE_IP}::inst0::INSTR",
    f"TCPIP0::{SCOPE_IP}::5025::SOCKET",
)

CAPTURES = [
    {
        "name": "Pulse2a_Us",
        "title": "Us",
        "trigger_level": 37.5,       # 50 % of Us, fires on rising edge
        "time_scale": 100e-6,        # 100 µs/div  →  1 ms window
        "time_position": 0,
        "measure": "MAX",
        "cursor_y1": 0,
        "cursor_y2": US_NOMINAL,     # updated to measured MAX after capture
    },
    {
        "name": "Pulse2a_tr",
        "title": "tr",
        "trigger_level": 37.5,       # fires at midpoint of rising edge
        "time_scale": 2e-6,          # 2 µs/div  →  20 µs window
        "time_position": 0,
        "measure": None,             # cursor ΔX
        "cursor_x1": -0.5e-6,        # ≈ 0.1·Us = 7.5 V crossing  (tune after first run)
        "cursor_x2":  0.5e-6,        # ≈ 0.9·Us = 67.5 V crossing (tune after first run)
    },
    {
        "name": "Pulse2a_td",
        "title": "td",
        "trigger_level": 67.5,       # 0.9·Us, fires at 90 % level on rising edge
        "time_scale": 10e-6,         # 10 µs/div  →  100 µs window
        "time_position": 0,
        "measure": None,             # cursor ΔX
        "cursor_x1":  0,             # 0.9·Us crossing on rise  (≈ trigger point)
        "cursor_x2":  50e-6,         # 0.9·Us crossing on fall  (≈ td = 50 µs later)
    },
    {
        "name": "Pulse2a_t1",
        "title": "t1",
        "trigger_level": 37.5,
        "time_scale": 500e-3,        # 500 ms/div  →  5 s window
        "time_position": 0,
        "measure": "PER",
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


def setup_clean_trigger(trigger_level):
    scope.write("TRIG:A:TYPE EDGE")
    scope.write(f"TRIG:A:SOUR {TRIGGER_SOURCE}")
    scope.write(f"TRIG:A:EDGE:SLOP {TRIGGER_SLOPE}")
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


def single_wait(trigger_level):
    setup_clean_trigger(trigger_level)
    scope.write("*CLS")
    print("Starte jetzt Pulse2a...")
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
    setup_clean_trigger(capture["trigger_level"])
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

    if not single_wait(capture["trigger_level"]):
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

for capture in CAPTURES:
    run_capture(capture)

# ----------------------------------------------------------
# Ende
# ----------------------------------------------------------
scope.close()
rm.close()

print("\nFERTIG - Alle Bilder gespeichert.")
