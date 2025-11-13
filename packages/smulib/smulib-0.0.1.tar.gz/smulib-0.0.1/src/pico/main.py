import sys
import select
import time
import random

# Internal mock state
state = {
    "mode": "VOLT",  # "VOLT" or "CURR"
    "source_voltage": 0.0,
    "source_current": 0.0,
    "voltage_limit": 5.0,
    "current_limit": 0.1,
    "output": False,
}

def scpi_process(cmd: str) -> str:
    sys.stdout.write(f"CMD: {cmd}")

    """Process a single SCPI command and return reply (if any)."""
    cmd = cmd.strip().upper()

    # Identification
    if cmd == "*IDN?":
        return "ZOUTIGEWOLF,SMU-MOCK,0001,1.0\n"

    # Mode control
    elif cmd.startswith(":SOUR:FUNC?"):
        return state["mode"] + "\n"
    elif cmd.startswith(":SOUR:VOLT") and not cmd.endswith("?"):
        # Set voltage
        try:
            val = float(cmd.split()[-1])
            state["source_voltage"] = val
            state["mode"] = "VOLT"
            return ""
        except:
            return "ERR\n"
    elif cmd.startswith(":SOUR:CURR") and not cmd.endswith("?"):
        # Set current
        try:
            val = float(cmd.split()[-1])
            state["source_current"] = val
            state["mode"] = "CURR"
            return ""
        except:
            return "ERR\n"

    # Limits
    elif cmd.startswith(":SOUR:VOLT:LIM"):
        if cmd.endswith("?"):
            return f"{state['voltage_limit']:.4f}\n"
        else:
            try:
                state["voltage_limit"] = float(cmd.split()[-1])
                return ""
            except:
                return "ERR\n"
    elif cmd.startswith(":SOUR:CURR:LIM"):
        if cmd.endswith("?"):
            return f"{state['current_limit']:.6f}\n"
        else:
            try:
                state["current_limit"] = float(cmd.split()[-1])
                return ""
            except:
                return "ERR\n"

    # Measurement
    elif cmd == ":MEAS:VOLT?":
        # Return simulated voltage around source_voltage
        v = state["source_voltage"] + random.uniform(-12, 12)
        return f"{v:.4f}\n"
    elif cmd == ":MEAS:CURR?":
        # Return simulated current around source_current
        i = state["source_current"] + random.uniform(-0.1, 0.1)
        return f"{i:.6f}\n"

    # Output
    elif cmd.startswith(":OUTP"):
        if cmd.endswith("?"):
            return "1\n" if state["output"] else "0\n"
        else:
            val = cmd.split()[-1]
            state["output"] = val in ("1", "ON", "TRUE")
            return ""

    # Reset
    elif cmd == "*RST":
        state.update({
            "mode": "VOLT",
            "source_voltage": 0.0,
            "source_current": 0.0,
            "voltage_limit": 5.0,
            "current_limit": 0.1,
            "output": False,
        })
        return ""

    else:
        return "ERR:UNKNOWN\n"


def main():
    print("Mock SMU ready")
    while True:
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            if line:
                reply = scpi_process(line)
                if reply:
                    sys.stdout.write(reply)
        time.sleep(0.01)


if __name__ == "__main__":
    main()