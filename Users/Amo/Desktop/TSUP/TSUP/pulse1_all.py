# ==========================================================
# RTM3004 AUTO TEST SCRIPT
# ISO 7637-2 Pulse 1 (-100V)
# Automatisch:
# 1. Us Screenshot
# 2. tr Screenshot
# 3. td Screenshot
# 4. t1 Screenshot
# 5. t2 Screenshot
# Peakwert speichern
# ==========================================================

import pyvisa
import time
import os
from datetime import datetime

# ----------------------------------------------------------
# Einstellungen
# ----------------------------------------------------------
SCOPE_IP = "192.168.50.96"
SAVE_PATH = os.path.dirname(os.path.abspath(__file__))
TRIGGER_TIMEOUT = 60
CHANNEL = "CHAN1"
MEAS_SOURCE = "C1"
TRIGGER_SOURCE = "C1"
VERTICAL_SCALE = 20
VERTICAL_OFFSET = -50
SCOPE_RESOURCES = (
    f"TCPIP0::{SCOPE_IP}::inst0::INSTR",
    f"TCPIP0::{SCOPE_IP}::5025::SOCKET",
)

CAPTURES = [
    {
        "name": "Pulse1_Us",
        "title": "Us",
        "trigger_level": -80,
        "time_scale": 1e-3,
        "time_position": 0,
        "measure": "MIN",
        "cursor_y1": 0,
        "cursor_y2": -100,
    },
    {
        "name": "Pulse1_tr",
        "title": "tr",
        "trigger_level": -65.5,
        "time_scale": 4e-6,
        "time_position": 0,
        "measure": None,
        "cursor_x1": -0.5e-6,
        "cursor_x2": 0.3e-6,
    },
    {
        "name": "Pulse1_td",
        "title": "td",
        "trigger_level": -80.1,
        "time_scale": 500e-6,
        "time_position": 0,
        "measure": "NWID",
        "cursor_x1": -170e-6,
        "cursor_x2": 1.83e-3,
    },
    {
        "name": "Pulse1_t2",
        "title": "t2",
        "trigger_level": -65.5,
        "time_scale": 40e-3,
        "time_position": 70.6e-3,
        "measure": "NWID",
        "cursor_x1": -345e-6,
        "cursor_x2": 199.6e-3,
    },
    {
        "name": "Pulse1_t1",
        "title": "t1",
        "trigger_level": -65.5,
        "time_scale": 200e-3,
        "time_position": 406e-3,
        "measure": "PER",
    },
    # {
    #     "name": "Pulse1_Vs",
    #     "title": "Vs",
    #     "trigger_level": -80.1,
    #     "time_scale": 500e-6,
    #     "time_position": 0,
    #     "measure": "MIN",
    # },
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
        '  python -m pip install pyvisa-py\n'
        "Oder starte dieses Projekt mit .\\run_pulse1_all.ps1"
    ) from exc

def open_scope(resource_manager):
    last_error = None

    for resource in SCOPE_RESOURCES:
        try:
            print("Verbinde mit:", resource)
            instrument = resource_manager.open_resource(resource)
            instrument.timeout = 5000
            instrument.read_termination = "\n"
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
    scope.write("TRIG:A:EDGE:SLOP NEG")
    scope.write(f"TRIG:A:LEV {trigger_level}")

    # Normal mode avoids auto-triggered captures when no valid pulse is present.
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

    data = scope.query_binary_values(
        "HCOP:DATA?",
        datatype='B',
        container=bytes
    )

    with open(filename, "wb") as f:
        f.write(data)

    print("Gespeichert:", filename)


def single_wait(trigger_level):

    setup_clean_trigger(trigger_level)
    scope.write("*CLS")
    print("Starte jetzt Pulse1...")
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
        except:
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
    """Read ΔX between cursor 1 and cursor 2 from scope."""
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

    if capture.get("zoom_only"):
        # Reuse the waveform already in memory — just zoom in, no new trigger
        time.sleep(0.3)
        value = read_cursor_delta(capture)
        print(f"{capture['title']}:", value)
        screenshot(capture["name"])
        return

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
