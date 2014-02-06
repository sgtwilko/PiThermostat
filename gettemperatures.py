#!/usr/bin/python
# Modified 30-Oct-2013
# tng@chegwin.org
# Retrieve: 
# 1: target temperature from a calendar
# 2: current temperature from a TMP102 sensor
# 3: weather from the weather_file (or run weather_script and try again)
#    file is populated by weather-util. See retrieve-weather.sh for details

import sys,time
from sys import path
#import threading
import datetime
from time import sleep
import redis
from processcalendar import parse_calendar
import re
sys.path.append("/usr/local/lib/python2.7/site-packages/Adafruit/I2C")
from Adafruit_I2C import Adafruit_I2C
redthis = redis.StrictRedis(host='433board',port=6379, db=0)

def find_redis():
    outside_temp=int(redthis.get("temperature/weather"))
    required_temp=(redthis.get("temperature/required"))
##### Optimal temp is the debug value we want to set the house to
##### if all else fails
    optimal_temp=float(redthis.get("temperature/optimal"))
    return(outside_temp,required_temp,optimal_temp)



class Tmp102:
  i2c = None

  # Constructor
  def __init__(self, address=0x48, mode=1, debug=False):
    self.i2c = Adafruit_I2C(address, debug=debug)

    self.address = address
    self.debug = debug
    # Make sure the specified mode is in the appropriate range
    if ((mode < 0) | (mode > 3)):
      if (self.debug):
        print "Invalid Mode: Using STANDARD by default"
      self.mode = self.__BMP085_STANDARD
    else:
      self.mode = mode

  def readRawTemp(self):
    "Reads the raw (uncompensated) temperature from the sensor"
    self.i2c.write8(0, 0x00)                 # Set temp reading mode
    raw = self.i2c.readList(0,2)

    val = raw[0] << 4;
    val |= raw[1] >> 4;

    return val


  def readTemperature(self):
    "Gets the compensated temperature in degrees celcius"

    RawBytes = self.readRawTemp()  #get the temp from readRawTemp (above)
    temp = float(float(RawBytes) * 0.0625)  #this is the conversion value from the data sheet.
    if (self.debug):
      print "DBG: Raw Temp: 0x%04X (%d)" % (RawBytes & 0xFFFF, RawBytes)
      print "DBG: Calibrated temperature = %f C" % temp
    
    return RawBytes,temp


def read_temps():
    try:
        mytemp = Tmp102(address=0x48)
        floattemp = mytemp.readTemperature()[1]
    except:
        mytemp = 14
        floattemp = 14.00
    try:
        (weather_temp,working_temp,optimal_temp)=find_redis()
        weather_temp=int(weather_temp)
#        boost_temp=(float(boost_temp))
        working_temp=(float(working_temp))
        optimal_temp=(int(optimal_temp))
#        print ("Found weather %i" % weather_temp)
#        print ("Found boost %i" % boost_temp)
#        print ("Found working %f" % working_temp)
#        print ("Found optimal %i" % optimal_temp)
    except:
        print ("Unable to find redis stats ")
        weather_temp=0 
        optimal_temp=20
        working_temp=optimal_temp
    try:
        target_temp=int(parse_calendar())
    except:
        target_temp=14
    return (floattemp, target_temp, weather_temp, working_temp, optimal_temp)

