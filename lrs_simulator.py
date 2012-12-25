# -*- coding: cp1250 -*-
import serial

port='COM22'
speed=57600

ser = serial.Serial(port, speed, timeout=1)

sample_data="""CH=937D0073
RSSI=051 RCQ=100 U=11.7V T=27°C
CH=937D0073
RSSI=040 RCQ=90 U=11.7V T=27°C
CH=937D0073
"""

print "LRS simulator running on %s at %d baud" % (port,speed)

while 1:
    for line in sample_data:
        ser.write(line)
        print "."
