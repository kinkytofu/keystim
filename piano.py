#!/usr/bin/env python

import rtmidi_python as rtmidi
import time
from time import sleep
import serial
from ConfigParser import SafeConfigParser

"""
Opens the external config/settings file.
"""
config = SafeConfigParser()
config.read('settings.txt')


"""
This is currently only written to work with the E-stim Systems 2B.

In the future, this should also work with the Erostek ET-312.
"""


"""
Settings for Device 1
"""

d1On = config.get('device1', 'on')
d1Box = config.get('device1', 'box')
d1USB = config.get('device1', 'usb')
d1Mode = config.get('device1', 'mode')
d1Level = config.get('device1', 'level')
d1AInt = config.get('device1', 'a-intensity')
d1AFreq = config.get('device1', 'a-frequency')
d1BInt = config.get('device1', 'b-intensity')
d1BFreq = config.get('device1', 'b-frequency')

"""
Settings for Device 2
"""
d2On = config.get('device2', 'on')
d2Box = config.get('device2', 'box')
d2USB = config.get('device2', 'usb')
d2Mode = config.get('device2', 'mode')
d2Level = config.get('device2', 'level')
d2AInt = config.get('device2', 'a-intensity')
d2AFreq = config.get('device2', 'a-frequency')
d2BInt = config.get('device2', 'b-intensity')
d2BFreq = config.get('device2', 'b-frequency')


"""
Settings conversion
"""

modes = {"pulse": 0, "bounce": 1, "continuous": 2, "a-split": 3, "b-split": 4, "wave": 5, "waterfall": 6, "squeeze": 7, "milk": 8, "throb": 9, "thrust": 10, "random": 11, "step": 12, "training": 13}

d1Modes = modes[d1Mode.lower()]
d2Modes = modes[d2Mode.lower()]

levels = {"high": "H", "low": "L"}

d1Levels = levels[d1Level.lower()]
d2Levels = levels[d2Level.lower()]

channels = {"AInt": "A", "BInt": "B", "AFreq": "C", "BFreq": "D"}

lineEnd = "\\r"
channelOff = "0"

"""
Not currently using the below variables because the performance hit is too great - there seem to be major delays when pressing the MIDI keys.
"""

d1AOn = "A%s%s" % (str(d1AInt), lineEnd)
d1BOn = "B%s%s" % (str(d1BInt), lineEnd)
d1AOff = "A%s%s" % (channelOff, lineEnd)
d1BOff = "B%s%s" % (channelOff, lineEnd)


"""
Opens the correct serial port.
"""
try:
    if d1On == 'yes':
        ser1 = serial.Serial(
            port='/dev/ttyUSB' + str(d1USB),
            baudrate=9600,
            timeout=0
            )
        device1 = "connected"
        print("Device 1 is connected to: " + ser1.portstr)
    elif d1On =='no':
        print("Device 1 is not marked as 'on' in settings.txt")
        device1 = "disconnected"
    else:
        print("Device 1 'on' setting must be set to 'yes' or 'no'")
except:
    device1 = "disconnected"
    print("Device 1 is not connected")

try:
    if d2On == 'yes':
        ser2 = serial.Serial(
            port='/dev/ttyUSB' + str(d2USB),
            baudrate=9600,
            timeout=0
            )
        device2 = "connected"
        print("Device 2 is connected to: " + ser2.portstr)
    elif d2On == 'no':
        print("Device 2 is not marked as 'on' in settings.txt")
        device2 = "disconnected"
    else:
        print("Device 2 'on' setting must be set to 'yes' or 'no'")
except SerialException:
    device2 = "disconnected"
    print("Device 2 is not connected")

"""
Set estim box base settings.
"""

if device1 == "connected" and d1Box == "2B":
    ser1.write("M" + str(d1Modes) + "\\r")
    ser1.write(d1Levels + "\\r")
    ser1.write("C" + str(d1AFreq) + "\\r")
    ser1.write("D" + str(d1BFreq) + "\\r")
else:
    pass

if device2 == "connected" and d2Box == "2B":
    ser2.write("M" + str(d2Modes) + "\\r")
    ser2.write(d1Levels + "\\r")
    ser2.write("C" + str(d2AFreq) + "\\r")
    ser2.write("D" + str(d2BFreq) + "\\r")
else:
    pass


"""
MIDI-Estim interaction
"""

def MidiCallback(message, time_stamp):
    messagetype = message[0] >> 4
    note = message[1] if len(message) > 1 else None

    if messagetype == 9:
        keystate = "down"
    elif messagetype == 8:
        keystate = "up"
    else:
        pass

    if note == 48 and keystate == "down":
        ser1.write("A30\r")
        print(d1AOn)
        sleep(1)
    elif keystate == "up":
        ser1.write("A0\r")
        print(d1AOff)
    else:
        pass

    print("keystate is %s " % (keystate))
    print("note is %s" % (str(note)))


"""
Detect MIDI port, ignore loop through port.
"""

midi_in = [rtmidi.MidiIn()]
previous = []
while True:
    for port in midi_in[0].ports:
        if port not in previous and 'Midi Through' not in port:
            midi_in.append(rtmidi.MidiIn())
            midi_in[-1].callback = MidiCallback
            midi_in[-1].open_port(port)
            print("Connected MIDI device: " + port)
    previous = midi_in[0].ports
    time.sleep(0.5)

