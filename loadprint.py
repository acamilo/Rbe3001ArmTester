#!/usr/bin/python


import serial
import argparse
import time
from ArmLib import ArmData
from helper import CalcAvg
import numpy as np

    

parser = argparse.ArgumentParser()
parser.add_argument('-s','--serialport', help="Robot's debug serial port", default = "/dev/ttyACM0")
parser.add_argument('-b','--baudrate', help='Debug serial port baudrate.', default = "9600")

args = parser.parse_args()

ser = serial.Serial(args.serialport,args.baudrate)
ser.readline() # discard first line
p = ser.readline()

packet = ArmData(p,tare=False)


# Test Procedure.

# Gather data determine baseline.
# Ask user to add Small Weight
# Ask user to remove Small Weight
# Ask user to add HEavy Weight
# Ask user to  remove HEavy weight



caa = CalcAvg(10)
cab = CalcAvg(10)
ta = 0.0
tb = 0.0

tamax = 0.0
tbmax = 0.0


inc = 0
while True:
  packet.parseline(ser.readline())
  caa.add(packet.loadvalues[1])
  cab.add(packet.loadvalues[2])
  inc += 1

  if inc%20 == 0:
    tamax = 0.0
    tbmax = 0.0      
  if inc == 15:
    tamax = 0.0
    tbmax = 0.0
    ta = caa.avg
    tb = cab.avg
  if abs(packet.loadvalues[1]-ta)>tamax:
    tamax = abs(packet.loadvalues[1]-ta)
  if abs(packet.loadvalues[2]-tb)>tbmax:
    tbmax = abs(packet.loadvalues[2]-tb)
  
  
  print "%0.4f\t%0.4f\t%0.4f\t%0.4f\r"%(caa.avg-ta, cab.avg-tb,tamax,tbmax)
  #print packet
  #time.sleep(1)

