#!/usr/bin/python


import serial
import argparse
import time
import datetime
from ArmLib import ArmData
from helper import CalcAvg
from tqdm import tqdm
import os

samples = 30

def generateAvg(samples):
  avg = [0,0,0]
  for i in range(3):
    for sample in samples:
      avg[i] += sample[i]
    avg[i] = avg[i]/len(samples)
  return avg

class RobotData:
  name = ''
  number = 0
  heavy_weight = []
  light_weight = []
  noload_post  = []
  noload       = []
  date = None

  testpass = False
  def __init__(self,number,name):
    self.number = int(number)
    self.name = name
    self.date = datetime.datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument('-s','--serialport', help="Robot's debug serial port", default = "/dev/ttyACM0")
parser.add_argument('-b','--baudrate', help='Debug serial port baudrate.', default = "9600")
parser.add_argument('-n','--namesdb', help='List of team names and numbers', default = "arm-names")

args = parser.parse_args()


#load arm names
namesdb = open(args.namesdb)
if namesdb == None:
  print("Could not open team names file '%s'"%args.namesdb)
  exit(-1)

names = namesdb.read().split('\n')
arms = []

#create array of arm names
for name in names:
  vals = name.strip().split(' ')
  if len(vals)==2:
    number,name = vals
    arms.append( [int(number),name] )






while True:
  print
  RobotNumber = raw_input("Robot Number: ")
  print
  print("Working on robot '%s'"%RobotNumber)

  #Find robot
  RobotName = None
  for bot in arms:
    if bot[0] == int(RobotNumber):
      RobotName = bot[1]
  if RobotName == None:
    print("Could notfind a robot with that number")
  else:
    print("Robot Name: '%s'"%RobotName)

  robot = RobotData(RobotNumber,RobotName)
  filename = '%s-%s-%s'%(RobotNumber,RobotName,datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
  log = open(filename, 'w') 
  print "Logging data to %s" % (filename)
  print
  lab = raw_input("Would you like to print a label? [Y/N]")
  print
  if lab=='Y' or lab == 'y':
    labeltext = "%s : %s" % (RobotNumber,RobotName)
    if os.path.exists("data-64.bmp"):
      os.remove("data-64.bmp")
    os.system("convert -size x64 label:\"%s\" +dither -negate -monochrome label-64.bmp" % labeltext)
    time.sleep(5)
    os.system("python ptd600.py label-64.bmp")

  print
  # tRY AND OPEN A SERIAL PORT
  while True:
    print("Connecting to '%s' pn port %s..."%(RobotName,args.serialport))
    try:
      ser = serial.Serial(args.serialport,args.baudrate)
      break
    except serial.serialutil.SerialException:
      print("Cound not connect to '%s'  Retrying.."%RobotName)
    time.sleep(5)

  ser.readline() # discard first line
  print
  RobotNumber = raw_input("Please pose the robot, switch on power, and press [ENTER] to continue.. ")
  print
  for i in tqdm(range(5)):
    time.sleep(1)


  print "\nInitial Loading of arm.."
  print
  raw_input("\tPlace the Heavy Weight onto the tip of the robot arm.\n\tand press [ENTER] to continue.. ")
  print
  for i in tqdm(range(5)):
    time.sleep(1)
  print
  raw_input("\n\tRemove the weight from the arm. \n\tand press [ENTER] to continue..  ")
  print
  for i in tqdm(range(5)):
    time.sleep(1)  




  print "\n\nGathering data for tare .."
  print


  #flush input buffer.
  print "flushing %d bytes of stale data" % ser.in_waiting
  f = ser.read(ser.in_waiting)
  f = ser.readline()
  f = ser.readline()
  for i in tqdm(range(samples+10)):
    p = ArmData(ser.readline())
    if p.valid:
      robot.noload.append(p.loadvalues)

  print "\n\tGot %d valid packets!" % len(robot.noload)


  print
  raw_input("\n\tPlace the Heavy Weight onto the tip of the robot arm.\n\tand press [ENTER] to continue..  ")
  print

  print "\n\nGathering data for Heavy Weight .."
  print
 
  #flush input buffer.
  print "flushing %d bytes of stale data" % ser.in_waiting
  f = ser.read(ser.in_waiting)
  f = ser.readline()
  f = ser.readline()
  for i in tqdm(range(samples+10)):
    p = ArmData(ser.readline())
    if p.valid:
      robot.heavy_weight.append(p.loadvalues)

  print "\n\tGot %d valid packets!" % len(robot.heavy_weight)

  print
  raw_input("\n\tRemove the weight from the arm. \n\tand press [ENTER] to continue..  ")
  print
  for i in tqdm(range(5)):
    time.sleep(1)  

  print "\n\nGathering data for Hysteresis .."
  print

  #flush input buffer.
  print "flushing %d bytes of stale data" % ser.in_waiting
  f = ser.read(ser.in_waiting)
  f = ser.readline()
  f = ser.readline()
  for i in tqdm(range(samples+10)):
    p = ArmData(ser.readline())
    if p.valid:
      robot.noload_post.append(p.loadvalues)

  print "\n\tGot %d valid packets!" % len(robot.noload_post)

  print
  raw_input("\n\tPlace the Light Weight onto the tip of the robot arm.\n\tand press [ENTER] to continue..  ")
  print

  print "\n\nGathering data for Light Weight .."
  packets = []

  #flush input buffer.
  print "flushing %d bytes of stale data" % ser.in_waiting
  f = ser.read(ser.in_waiting)
  f = ser.readline()
  f = ser.readline()
  for i in tqdm(range(samples+10)):
    p = ArmData(ser.readline())
    if p.valid:
      robot.light_weight.append(p.loadvalues)

  print "\n\tGot %d valid packets!" % len(robot.light_weight)


  Failure = False
  
  # process data
  print robot.heavy_weight[0]
  print robot.light_weight[0]
  print robot.noload[0]
  print robot.noload_post[0]

  log.write("Heavy\n")
  log.write(str(robot.heavy_weight))

  log.write("Light\n")
  log.write(str(robot.light_weight))

  log.write("Noload\n")
  log.write(str(robot.noload))

  log.write("Hyst\n")
  log.write(str(robot.noload_post))
  #averages for each category
  heavy_avg = generateAvg(robot.heavy_weight[0:samples])
  light_avg = generateAvg(robot.light_weight[0:samples])
  noload_avg = generateAvg(robot.noload[0:samples])
  noload_post_avg = generateAvg(robot.noload_post[0:samples])

  hyst = [0.0,0.0,0.0]
  for i in range(3):
    hyst[i] = noload_avg[i] - noload_post_avg[i]

  #calculate noise
  noise = [[0.0]] * 3
  for i in range(len(robot.noload)):
    for j in range(len(noise)):
      n = abs(robot.noload[i][j]-noload_avg[j])
      noise[j].append(n)
  noisemax = [max(noise[0]),max(noise[1]),max(noise[2])]

  print "Heavy Avg:  %s" % str(heavy_avg)
  print "Light Avg:  %s" % str(light_avg)
  print "noload Avg: %s" % str(noload_avg)
  print "Hysteresis: %s" % str(hyst)
  print "Noise PKPK: %s" % str(noisemax)

  log.write("Heavy Avg:  %s\n" % str(heavy_avg))
  log.write("Light Avg:  %s\n" % str(light_avg))
  log.write("noload Avg: %s\n" % str(noload_avg))
  log.write("Hysteresis: %s\n" % str(hyst))
  log.write("Noise PKPK: %s\n" % str(noisemax)) 


  print
  print
  print "Final Report\n\n"
  print "\tHeavy Weight:"
  for i in range(1,3):
    hw = abs(heavy_avg[i]-noload_avg[i])
    hys = abs(hyst[i])
    if hw<30.0:
      print "\tFailure for link %d. Heavy Weight measurement smaller than noise floor (%f) %f/%f" % \
        (i,hw/hys,hw,hys)
      log.write("Heavy Test: Failure for link %d. Noise Floor\n"%i)
      Failure = True
    elif hys>hw:
      print "\tFailure for link %d. Heavy Weight measurement smaller than hysteresis (%f) %f/%f" % \
        (i,hw/hys,hw,hys)
      log.write("Heavy Test: Failure for link %d. Hysteresis\n"%i)
      Failure = True
    else:
      print "\tLink %d Passes with a weight/hyst of (%f) %f/%f"%\
            (i,hw/hys,hw,hys)
      log.write("Light Test: PASS link %d.\n"%i)
  print "\tlight Weight:"
  for i in range(1,3):
    lw = abs(light_avg[i]-noload_avg[i])
    hys = abs(hyst[i])
    if lw<30.0:
      print "\tFailure for link %d. Light Weight measurement smaller than noise floor  (%f) %f/%f"%\
              (i,lw/hys,lw,hys)
      log.write("Light Test: Failure for link %d. Hysteresis\n"%i)
      Failure = True
    elif hys>lw:
      print "\tFailure for link %d. Light Weight measurement smaller than hysteresis (%f) %f/%f"%\
              (i,lw/hys,lw,hys)
      log.write("Light Test: Failure for link %d. Noise Floor\n"%i)
      Failure = True
    else:
      print "\tLink %d Passes with a weight/hyst of (%f) %f/%f"%\
            (i,lw/hys,lw,hys)
      log.write("Light Test: PASS link %d.\n"%i)

  print
  print

  print
  print
  if Failure:
    print "\tArm '%s' \033[1;31;40m Failed \033[0;37;40m Test" % robot.name
    log.write("Arm Result: FAIL.\n")
  else:
    print "\tArm '%s' \033[1;32;40m Passed \033[0;37;40m Test" % robot.name
    log.write("Arm Result: FAIL.\n")    
  
  #testdataq = raw_input( "Would you like test data printed to a label? [Y/N]")
  #if testdataq == 'Y' or testdataq == 'y':
  #  labeltext = "Heavy: %s\nLight: %s\nNo Load: %s\nHysteresis: %s" % (str(heavy_avg),str(light_avg),str(noload_avg),str(hyst))
  #  if os.path.exists("data-64.bmp"):
  #    os.remove("data-64.bmp")
  #  os.system("convert -size x64 label:\"%s\" +dither -negate -monochrome data-64.bmp" % labeltext)
  #  time.sleep(5)
  #  os.system("python ptd600.py data-64.bmp")
  log.close()

# Test Procedure.

# Gather data determine baseline.
# Ask user to add Small Weight
# Ask user to remove Small Weight
# Ask user to add HEavy Weight
# Ask user to  remove HEavy weight




