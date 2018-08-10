#!/usr/bin/python


import serial
import argparse
import time
from ArmLib import ArmData
from helper import CalcAvg

    

parser = argparse.ArgumentParser()
parser.add_argument('-s','--serialport', help="Robot's debug serial port", default = "/dev/ttyACM0")
parser.add_argument('-b','--baudrate', help='Debug serial port baudrate.', default = "9600")

args = parser.parse_args()

ser = serial.Serial(args.serialport,args.baudrate)
ser.readline() # discard first line
p = ser.readline()

packet = ArmData(p)


# Test Procedure.

# Gather data determine baseline.
# Ask user to add Small Weight
# Ask user to remove Small Weight
# Ask user to add HEavy Weight
# Ask user to  remove HEavy weight




while True:
    packet.parseline(ser.readline())
    
    
    caa = CalcAvg(10)
    cab = CalcAvg(10)
    
    caa.add(packet.loadvalues[1])
    cab.add(packet.loadvalues[2])

    
    
    print "%0.2f\t%0.2f\t%0.2f\t%0.2f\r"%(caa.avg,cab.avg,packet.loadvalues[1],packet.loadvalues[2])
    #print packet
    #time.sleep(1)
print packet ,


