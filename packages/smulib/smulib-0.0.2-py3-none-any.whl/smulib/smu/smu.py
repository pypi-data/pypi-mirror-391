import logging
import time

import serial

from smulib.smu.base import SMUBase

_LOG = logging.getLogger(__name__)

class SMU(SMUBase):
    def __init__(self, port: str, baudrate: int = 115200, timeout: float | None = 1.0):
        self.__port = port
        self.__baudrate = baudrate
        self.__timeout = timeout
        self._serial = None
        self._connect_attempts: int = 0
        self._last_connect_time: float = 0.0
        self.max_backoff: float = 3.0
        self.initial_backoff: float = 0.1

        try:
            self.connect()
        except Exception:
            _LOG.exception("Initial connect failed for %s", port)
            self._serial = None

    @property
    def port(self) -> str:
        return self.__port

    def connect(self) -> None:
        try:
            self._serial = serial.Serial(port=self.__port, baudrate=self.__baudrate, timeout=self.__timeout)
            self._connect_attempts = 0
            self._last_connect_time = time.monotonic()
            _LOG.debug("Connected to SMU on %s", self.__port)
        except Exception as e:
            _LOG.exception("Failed to open serial port %s", self.__port)
            self._serial = None
            raise IOError(f"Could not open port {self.__port}: {e}") from e

    def disconnect(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                _LOG.exception("Error while closing serial port")
            finally:
                self._serial = None
                _LOG.debug("Disconnected from %s", self.__port)

    def reconnect(self) -> None:
        backoff = self.initial_backoff
        attempts = 0
        while True:
            try:
                self.connect()
                return
            except IOError:
                attempts += 1
                if backoff > self.max_backoff:
                    raise IOError(f"Failed to reconnect after {attempts} attempts") from None
                _LOG.warning("Reconnect attempt %d failed, backing off %.2fs", attempts, backoff)
                time.sleep(backoff)
                backoff *= 2

    def __write(self, command: str) -> None:
        if self._serial is None:
            raise IOError("Serial not connected")
        self._serial.write((command + "\n").encode())

    def __read(self, command: str) -> str:
        if self._serial is None:
            raise IOError("Serial not connected")
        self.__write(command)
        raw = self._serial.readline()
        if isinstance(raw, bytes):
            raw = raw.decode(errors='ignore')
        return str(raw).strip()

    def set_voltage(self, v: float) -> None:
        self.__write(f":SOUR:VOLT {float(v)}")

    def set_current(self, i: float) -> None:
        self.__write(f":SOUR:CURR {float(i)}")

    def voltage_limit(self) -> float:
        return float(self.__read(":SOUR:VOLT:LIM?"))

    def current_limit(self) -> float:
        return float(self.__read(":SOUR:CURR:LIM?"))

    def measure_voltage(self) -> float:
        return float(self.__read(":MEAS:VOLT?"))

    def measure_current(self) -> float:
        return float(self.__read(":MEAS:CURR?"))
