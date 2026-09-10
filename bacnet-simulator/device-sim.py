#!/usr/bin/env python
import random
import threading
import tkinter as tk
import signal
import sys
import argparse

from bacpypes.core import run, stop
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import AnalogInputObject, AnalogValueObject

# Use standard argparse to avoid INI file complications.
parser = argparse.ArgumentParser(description="Multi-Device BACnet Simulation")
parser.add_argument("--ip", type=str, default="0.0.0.0",
                    help="Local address for BACnet (default: 0.0.0.0)")
parser.add_argument("--port", type=int, default=47808,
                    help="BACnet/IP UDP port (default: 47808)")
args = parser.parse_args()

ADDRESS = f"{args.ip}:{args.port}"

def create_device(device_instance, device_name):
    # Create a LocalDeviceObject for the simulated device.
    device = LocalDeviceObject(
        objectName=device_name,
        objectIdentifier=device_instance,
        maxApduLengthAccepted=1024,
        segmentationSupported="noSegmentation",
        vendorIdentifier=15,
    )
    # Create an Analog Input (Temperature Sensor)
    temp_sensor = AnalogInputObject(
        objectIdentifier=('analogInput', 1),
        objectName="Temperature Sensor",
        presentValue=22.0,
        units="degreesCelsius",
    )
    # Create an Analog Value (Setpoint)
    setpoint = AnalogValueObject(
        objectIdentifier=('analogValue', 1),
        objectName="Setpoint",
        presentValue=22.0,
        units="degreesCelsius",
    )
    setpoint._properties['presentValue'].writable = True

    # Update the device object list.
    device.objectList = [device.objectIdentifier,
                         temp_sensor.objectIdentifier,
                         setpoint.objectIdentifier]
    return device, temp_sensor, setpoint

# Create two simulated devices with unique instance numbers.
device1, temp_sensor1, setpoint1 = create_device(599, "Thermostat 1")
device2, temp_sensor2, setpoint2 = create_device(600, "Thermostat 2")

# Create one BIPSimpleApplication bound to the standard port.
# (This is non-standard – bacpypes is typically one device per application –
# so further customization might be needed so that both devices can
# broadcast I-Am messages from the same UDP socket.)
application = BIPSimpleApplication(device1, ADDRESS)
# Manually add device2's objects to the application.
application.add_object(temp_sensor2)
application.add_object(setpoint2)
# (You may also need to adjust internal data structures so that both
# device1 and device2 are known. This example focuses on the broadcast aspect.)

# For demonstration, we simulate temperature changes for both devices.
def update_device_temperatures():
    new_temp1 = setpoint1.presentValue + random.uniform(-0.5, 0.5)
    temp_sensor1.presentValue = new_temp1
    new_temp2 = setpoint2.presentValue + random.uniform(-0.5, 0.5)
    temp_sensor2.presentValue = new_temp2
    # In a full implementation, you’d also trigger I-Am broadcasts.
    threading.Timer(2.0, update_device_temperatures).start()

update_device_temperatures()

# Simple GUI to adjust setpoints for both devices.
class MultiThermostatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Multi-Device BACnet Simulation")
        self.geometry("400x300")
        
        # Frame for Thermostat 1.
        frame1 = tk.Frame(self, bd=2, relief="groove")
        frame1.pack(pady=10, padx=10, fill="x")
        tk.Label(frame1, text="Thermostat 1").pack()
        self.temp_var1 = tk.StringVar(value=f"{temp_sensor1.presentValue:.2f} °C")
        self.setpoint_var1 = tk.DoubleVar(value=setpoint1.presentValue)
        tk.Label(frame1, text="Current Temperature:").pack()
        tk.Label(frame1, textvariable=self.temp_var1, font=("Helvetica", 14)).pack()
        tk.Label(frame1, text="Setpoint:").pack()
        entry1 = tk.Entry(frame1, textvariable=self.setpoint_var1)
        entry1.pack()
        tk.Button(frame1, text="Update Setpoint",
                  command=lambda: self.update_setpoint(setpoint1, self.setpoint_var1)).pack()
        
        # Frame for Thermostat 2.
        frame2 = tk.Frame(self, bd=2, relief="groove")
        frame2.pack(pady=10, padx=10, fill="x")
        tk.Label(frame2, text="Thermostat 2").pack()
        self.temp_var2 = tk.StringVar(value=f"{temp_sensor2.presentValue:.2f} °C")
        self.setpoint_var2 = tk.DoubleVar(value=setpoint2.presentValue)
        tk.Label(frame2, text="Current Temperature:").pack()
        tk.Label(frame2, textvariable=self.temp_var2, font=("Helvetica", 14)).pack()
        tk.Label(frame2, text="Setpoint:").pack()
        entry2 = tk.Entry(frame2, textvariable=self.setpoint_var2)
        entry2.pack()
        tk.Button(frame2, text="Update Setpoint",
                  command=lambda: self.update_setpoint(setpoint2, self.setpoint_var2)).pack()
        
        self.update_display()

    def update_setpoint(self, setpoint, var):
        try:
            value = float(var.get())
            setpoint.presentValue = value
        except ValueError:
            pass

    def update_display(self):
        self.temp_var1.set(f"{temp_sensor1.presentValue:.2f} °C")
        self.temp_var2.set(f"{temp_sensor2.presentValue:.2f} °C")
        self.after(2000, self.update_display)

def shutdown_handler(signum, frame):
    print("Shutting down BACnet stack...")
    stop()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

print("Starting BACnet event loop on", ADDRESS)
threading.Thread(target=run, daemon=True).start()

app_gui = MultiThermostatGUI()
app_gui.mainloop()
