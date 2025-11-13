import serial

class SMU:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float | None = 1.0):
        self.__port = port
        self.__baudrate = baudrate
        self.__timeout = timeout
        self.__serial = serial.Serial(
            port=self.__port,
            baudrate=self.__baudrate,
            timeout=self.__timeout
        )

    def __write(self, command: str) -> None:
        self.__serial.write((command + "\n").encode())

    def __read(self, command: str) -> str:
        self.__write(command)
        return self.__serial.readline().decode().strip()

    def enable(self) -> None:
        """Enable the SMU output."""
        self.__write(":OUTP ON")

    def disable(self) -> None:
        """Disable the SMU output."""
        self.__write(":OUTP OFF")

    def voltage_mode(self, voltage: float, current_limit: float) -> None:
        """Set the SMU to voltage mode, use negative voltage for sinking operation."""
        self.__write(f":SOUR:VOLT {voltage}")
        self.__write(f":SOUR:CURR:LIM {current_limit}")

    def current_mode(self, current: float, voltage_limit: float) -> None:
        """Set the SMU to current mode, use negative current for sinking operation."""
        self.__write(f":SOUR:CURR {current}")
        self.__write(f":SOUR:VOLT:LIM {voltage_limit}")

    def mode(self) -> str:
        """Get the current mode of the SMU."""
        return self.__read(":SOUR:FUNC?")

    def voltage(self) -> float:
        """Get the current voltage setting."""
        return float(self.__read(":SOUR:VOLT?"))

    def current(self) -> float:
        """Get the current current setting."""
        return float(self.__read(":SOUR:CURR?"))

    def voltage_limit(self) -> float:
        """Get the current voltage limit."""
        return float(self.__read(":SOUR:VOLT:LIM?"))

    def current_limit(self) -> float:
        """Get the current current limit."""
        return float(self.__read(":SOUR:CURR:LIM?"))

    def measure_voltage(self) -> float:
        """Measure the voltage."""
        return float(self.__read(":MEAS:VOLT?"))

    def measure_current(self) -> float:
        """Measure the current."""
        return float(self.__read(":MEAS:CURR?"))
