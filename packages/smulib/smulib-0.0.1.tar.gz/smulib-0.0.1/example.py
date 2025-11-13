from src.smulib import SMU

smu = SMU("/dev/cu.usbserial-0001")

smu.voltage_mode(voltage=12.0, current_limit=0.1)
smu.enable()
i = smu.measure_current()
smu.disable()

print(f"Current: {i}")
