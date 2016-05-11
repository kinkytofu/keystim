#!/usr/bin/env python

try:
    from ConfigParser import SafeConfigParser
    import time
    import os
    from time import sleep
    import rtmidi_python as rtmidi
    import serial
except ImportError, e:
    raise ImportError (str(e) + " found, please install")

global PORT_COUNT
PORT_COUNT = 0

def serial_setup(port):
    global PORT_COUNT
    PORT_COUNT += 1

    print("Attempting to use port " + port + " (Device #" + str(PORT_COUNT) + ")")

    try:
        fp = open(port)
    except IOError, errormsg:
        print "Could not write to port %s: %s" % (port, errormsg)
        raise
    else:
        try:
            ser = serial.Serial(
                port=str(port),
                baudrate=9600,
                timeout=0
            )
            print("Connected Device " + str(PORT_COUNT) + " port: " + ser.portstr)
    
            ser.write("M" + str(d1Modes) + "\\r")
            ser.write(d1Levels + "\\r")
            ser.write("C" + str(d1AFreq) + "\\r")
            ser.write("D" + str(d1BFreq) + "\\r")
    
        except serial.SerialException:
            print("Device " + str(PORT_COUNT) + " is not connected")
            print("\n")

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
        ser1.write(d1AOn)
        print(d1AOn)
        sleep(1)
    elif keystate == "up":
        ser1.write(d1AOff)
        print(d1AOff)
    else:
        pass

    print("keystate is %s " % (keystate))
    print("note is %s" % (str(note)))

if __name__ == "__main__":

    config = SafeConfigParser()
    try:
        config.read('settings.txt')
    except ConfigParser.ParsingError, err:
        print 'Could not parse:', err

    '''
    Settings for Device 1
    '''
    d1On = config.getboolean('device1', 'on')
    d1Box = config.get('device1', 'box')
    d1Port = config.get('device1', 'port')
    d1Mode = config.get('device1', 'mode')
    d1Level = config.get('device1', 'level')
    d1AInt = config.get('device1', 'a-intensity')
    d1AFreq = config.get('device1', 'a-frequency')
    d1BInt = config.get('device1', 'b-intensity')
    d1BFreq = config.get('device1', 'b-frequency')
    
    '''
    Settings for Device 2
    '''
    d2On = config.getboolean('device2', 'on')
    d2Box = config.get('device2', 'box')
    d2Port = config.get('device2', 'port')
    d2Mode = config.get('device2', 'mode')
    d2Level = config.get('device2', 'level')
    d2AInt = config.get('device2', 'a-intensity')
    d2AFreq = config.get('device2', 'a-frequency')
    d2BInt = config.get('device2', 'b-intensity')
    d2BFreq = config.get('device2', 'b-frequency')
    
    '''
    Settings conversion
    '''
    modes = {"pulse": 0, "bounce": 1, "continuous": 2, "a-split": 3, "b-split": 4, "wave": 5, "waterfall": 6, "squeeze": 7, "milk": 8, "throb": 9, "thrust": 10, "random": 11, "step": 12, "training": 13}
    
    d1Modes = modes[d1Mode.lower()]
    d2Modes = modes[d2Mode.lower()]
    
    levels = {"high": "H", "low": "L"}
    
    d1Levels = levels[d1Level.lower()]
    d2Levels = levels[d2Level.lower()]
    
    channels = {"AInt": "A", "BInt": "B", "AFreq": "C", "BFreq": "D"}
    
    lineEnd = "\r"
    channelOff = "0"
    
    '''
    Sets the on/off levels for the Channels, to be passed into the MIDICallback.
    '''
    
    d1AOn = "A%s%s" % (str(d1AInt), lineEnd)
    d1BOn = "B%s%s" % (str(d1BInt), lineEnd)
    d1AOff = "A%s%s" % (channelOff, lineEnd)
    d1BOff = "B%s%s" % (channelOff, lineEnd)

    serial_setup(d1Port)
    serial_setup(d2Port)

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
