#!/usr/bin/env python

import rtmidi_python as rtmidi
import time
from time import sleep
import serial


"""
Opens and parses the external settings file.
"""
with open('settings.txt', 'r') as myfile:
    data=myfile.read().replace('\n', '')


"""
Opens the correct serial port.
"""
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=9600,
    timeout=0
    )

"""
Need to check which ttyUSB# ports are connected, and then connect all present.
"""


def MidiCallback(message, time_stamp):
    messagetype = message[0] >> 4
    note = message[1] if len(message) > 1 else None

    if messagetype == 9:
        keystate = "down"
    elif messagetype == 8:
        keystate = "up"

    if note == 48 and keystate == "down":
        ser.write("A15\r")
        sleep(1)
    elif note == 48 and keystate == "up":
        ser.write("A0\r")
    elif note == 50 and keystate == "down":
        ser.write("A20\r")
        sleep(1)
    elif note == 50 and keystate == "up":
        ser.write("A0\r")
    else:
        pass

    print "keystate is " + keystate
    print "note is " + str(note)

# detect MIDI port, ignore loop through port
midi_in = [rtmidi.MidiIn()]
previous = []
while True:
    for port in midi_in[0].ports:
        if port not in previous and 'Midi Through' not in port:
            midi_in.append(rtmidi.MidiIn())
            midi_in[-1].callback = MidiCallback
            midi_in[-1].open_port(port)
            print 'Opened MIDI: ' + port
    previous = midi_in[0].ports
    time.sleep(0.5)


