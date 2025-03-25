#!/usr/bin/env python
import random
import threading
import tkinter as tk

from bacpypes.consolelogging import ConfigArgumentParser
from bacpypes.core import run, stop
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import AnalogInputObject, AnalogValueObject
from bacpypes.pdu import Address
import signal

# Hardcoded BACnet/IP address.
ADDRESS = "192.168.1.105:47808"

# Configure the local BACnet device.
this_device = LocalDeviceObject(
    objectName="SimpleThermostat",
    objectIdentifier=599,  # Unique device instance number
    maxApduLengthAccepted=1024,
    segmentationSupported="noSegmentation",
    vendorIdentifier=15,
)

# Create a Temperature Sensor as an Analog Input.
temperature_sensor = AnalogInputObject(
    objectIdentifier=('analogInput', 1),
    objectName="Temperature Sensor",
    presentValue=22.0,  # Initial temperature in °C
    units="degreesCelsius",
)

# Create a Setpoint as an Analog Value that is writable.
setpoint = AnalogValueObject(
    objectIdentifier=('analogValue', 1),
    objectName="Setpoint",
    presentValue=22.0,  # Initial setpoint in °C
    units="degreesCelsius",
)
setpoint._properties['presentValue'].writable = True  # Allow writing from BACnet

# Register the objects with the BACnet application.
this_application = BIPSimpleApplication(this_device, ADDRESS)
this_application.add_object(temperature_sensor)
this_application.add_object(setpoint)

# Update the device object list to include all objects.
this_device.objectList = [
    this_device.objectIdentifier,
    temperature_sensor.objectIdentifier,
    setpoint.objectIdentifier,
]

# Create a Tkinter GUI for the thermostat.
class ThermostatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BACnet Thermostat Simulation")
        self.geometry("300x200")
        
        # Variables for GUI display.
        self.temperature_var = tk.StringVar()
        self.setpoint_var = tk.DoubleVar(value=setpoint.presentValue)
        
        # Current Temperature display.
        tk.Label(self, text="Current Temperature:").pack(pady=(10, 0))
        self.temp_label = tk.Label(self, textvariable=self.temperature_var, font=("Helvetica", 16))
        self.temp_label.pack(pady=(0, 10))
        
        # Setpoint entry.
        tk.Label(self, text="Setpoint:").pack()
        self.setpoint_entry = tk.Entry(self, textvariable=self.setpoint_var)
        self.setpoint_entry.pack(pady=(0, 10))
        
        # Button to update the setpoint.
        tk.Button(self, text="Update Setpoint", command=self.update_setpoint).pack()
        
        # Schedule the temperature update.
        self.update_temperature()

    def update_setpoint(self):
        try:
            value = float(self.setpoint_entry.get())
            setpoint.presentValue = value
            self.setpoint_var.set(value)
        except ValueError:
            pass  # Ignore invalid input

    def update_temperature(self):
        # Simulate a realistic temperature variation near the setpoint.
        new_temp = setpoint.presentValue + random.uniform(-0.5, 0.5)
        temperature_sensor.presentValue = new_temp
        self.temperature_var.set(f"{new_temp:.2f} °C")
        # Update every 2 seconds.
        self.after(2000, self.update_temperature)


def shutdown_handler(signum, frame):
    print("Shutting down BACnet stack...")
    stop()
    exit(0)

# Register signal handlers for graceful shutdown.
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# Start BACnet in the main thread before launching the GUI.
print("Starting BACnet event loop...")
threading.Thread(target=run, daemon=True).start()

# Start the Tkinter GUI.
app = ThermostatGUI()
app.mainloop()