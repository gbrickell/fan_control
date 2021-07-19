#!/usr/bin/env python3

# assumed RPi installation location for code for the command below: /home/pi/fan_control
# CLI command to run: python3 /home/pi/fan_control/fan_control_rpi-1.py
# assumed RPi installation location for control file: /home/pi/control_files/ which must already exist
# assumed RPi installation location for log file: /home/pi/usbdrive/server_logs/ 
#  this log file must already exist and because this file has a lot of reads/writes, it is 
#  recommended that /usbdrive is mapped to a USB drive using /etc/fstab to avoid the RPI's SD card 
#  from early degradation/failure

version = "v2: "    # text to be used for version control and added to the logs

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to read the current default parameter set from its log file 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def readdefaults():
    # open default file to read
    # default file, called 'server_fan_control.txt' contains the various control parameters
    # file path hardcoded for simplicity and should be updated to wherever the file is located
    # file contents is typically something like:
    # {'ontemp': '55', 'offtemp': '48', 'sleep': '10', 'gpiopin': '17'}
    # which specifies:
    # switch on temp of 55 degC
    # switch off temp of 48 deg c
    # a sleep interval of 10 seconds
    # the use of BCM GPIO #17 for the fan control GPIO pin
    defaultfile = open("/home/pi/control_files/server_fan_control.txt", "r") 
    readdefaults = defaultfile.read()
    defaults = eval(readdefaults)
    # close the log file
    defaultfile.close()
    return(defaults);


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to write a designated msg to a designated log file 
#  keeping only a designated number of records
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def writetolog(msgtext, writetofile, records):
   # open log file to read
   # because we do a read before a write the file must exist!
   local_logfile = open(writetofile, "r") # file path passed as a parameter
   currentcontent = local_logfile.readlines()
   #print ("writetolog - initial content: " + str(currentcontent))
   print ("writetolog - length of initial log: " + str(len(currentcontent)))
   currentcontent.append(msgtext +"\r\n" )
   print ("writetolog - text to be added to log file: ")
   print (msgtext )
   if len(currentcontent) > int(records):
       currentcontent = currentcontent[1:]
   print ("writetolog - length of final log: " + str(len(currentcontent)))
   # open log file to write
   local_logfile = open(writetofile,"w") # file path passed as a parameter
   # Loop through each item in the list and write it to the output file.
   for eachitem in currentcontent:
       local_logfile.write(str(eachitem)) 
   # close the log file
   local_logfile.close()
   return();


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to return the CPU temperature
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Return CPU temperature as a character string                                     
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))


#+-+-+-+-+-+-+-+-+
#
# main code
#
#+-+-+-+-+-+-+-+-+

import os
import RPi.GPIO as GPIO   # this imports the module to allow the GPIO pins to be easily utilised
import time               # this imports the module to allow various time functions to be used

logfile = "/home/pi/usbdrive/server_logs/server_fan_usage_log.txt"
# this initially empty file is assumed to exist

now = time.strftime("%Y-%m-%d_%H.%M.%S")   # this creates a string in a designated format e.g. YYYY-mm-dd_HH.MM.SS
print (now + ":")
print ("program starting")

# Get the various defaults from their control file
defaults = readdefaults()

ON_THRESHOLD = float(defaults['ontemp'])    # usually 55.0 (degrees Celsius): fan starts up at this temperature.
OFF_THRESHOLD = float(defaults['offtemp'])  # usually 48.0 (degress Celsius): fan shuts off at this temperature.
SLEEP_INTERVAL = int(defaults['sleep'])     # usually 10 (seconds): how often to check the CPU core temperature.
GPIO_pin = int(defaults['gpiopin'])         # usually #14

GPIO.setmode(GPIO.BCM)   # This code sets the RPi to use the BCM (Broadcom) pin numbers which is usually the default but is positively set here
GPIO.setup(GPIO_pin, GPIO.OUT)  # this sets the fan control GPIO pin to be an output 'type'

print ("on threshold  : " + str(ON_THRESHOLD) + "degC" )
print ("off threshold : " + str(OFF_THRESHOLD) + "degC"  )
print ("sleep interval: " + str(SLEEP_INTERVAL) + " secs" )

# write start data to usage log file
logmsg = "pitiki01 - fan control started " + version + time.strftime('%a %d %b %Y %H:%M:%S %Z') + " - on threshold: " + str(ON_THRESHOLD) + "degC" + " - off threshold: " + str(OFF_THRESHOLD) + "degC" + " - sleep interval: " + str(SLEEP_INTERVAL) + " secs"
writetolog(logmsg, logfile, 100)

# set the start values for the fan on/off times and the start time
StartTime = time.time() # floating point number of seconds since the 'epoch'
#print ("StartTime: " + str(StartTime))
NowTime = StartTime
LastElapsedTime = StartTime
FanOnTime = 0.0
FanOffTime = 0.0
fan_off_percent = 0.0
fan_on_percent =0.0

# Set the fan control GPIP pin LOW
GPIO.output(GPIO_pin, False)
fan = 'off'
print ("fan off")

CPU_temp = getCPUtemperature()
print ("CPU temperature  : " + str(CPU_temp))
print ("---------------------------------")
print (" ")

# Validate the on and off thresholds
if OFF_THRESHOLD >= ON_THRESHOLD:
    raise RuntimeError('OFF_THRESHOLD must be less than ON_THRESHOLD')

try:  # this try loop is not strictly necessary but it does allow the script to be easily stopped with CTRL-C    

    while True:
        CPU_temp = getCPUtemperature()
        #print ("CPU temperature  : " + str(CPU_temp))

        # Start the fan if the temperature has reached the limit 
        #    and the fan isn't already running.
        if float(CPU_temp) > ON_THRESHOLD and fan == 'off':
            # if here then the fan is about to be switchd on and the incremental
            #   elapsed time up to now 'adds to' the FanOffTime time
            NowTime = time.time()
            now = time.strftime("%Y-%m-%d_%H.%M.%S")   # this creates a string in a designated format e.g. YYYY-mm-dd_HH.MM.SS
            #print ("NowTime: " + str(NowTime) )
            FanOffTime = FanOffTime + (NowTime - LastElapsedTime)
            #print ("FanOffTime: " + str(FanOffTime) )
            LastElapsedTime = NowTime
            fan_off_percent = 100.0*FanOffTime/(NowTime-StartTime)
            fan_on_percent = 100.0 - fan_off_percent
            GPIO.output(GPIO_pin, True)  # set fan control GPIO pin HIGH 
            fan = 'on'
            print (now + ": fan on")
            print ("CPU temperature   : " + str(CPU_temp) + "degC")
            print ("fan on percentage : " + "{:.2f}".format(fan_on_percent) +"%")
            print ("fan off percentage: " + "{:.2f}".format(fan_off_percent) +"%")
            print ("---------------------------------")
            print (" ")

        # Stop the fan if the fan is running and the temperature has 
        #   dropped to the lower limit.
        elif fan == 'on' and float(CPU_temp) < OFF_THRESHOLD:
            # if here then the fan is about to be switchd off and the incremental
            #   elapsed time up to now 'adds to' the FanOnTime time
            NowTime = time.time()
            now = time.strftime("%Y-%m-%d_%H.%M.%S")   # this creates a string in a designated format e.g. YYYY-mm-dd_HH.MM.SS
            FanOnTime = FanOnTime + (NowTime - LastElapsedTime)
            LastElapsedTime = NowTime
            fan_on_percent = 100.0*FanOnTime/(NowTime-StartTime)
            fan_off_percent = 100.0 - fan_on_percent
            GPIO.output(GPIO_pin, False)  # set fan control GPIO pin LOW
            fan = 'off'
            print (now + ": fan off")
            print ("CPU temperature   : " + str(CPU_temp) + "degC")
            print ("fan on percentage : " + "{:.2f}".format(fan_on_percent) +"%")
            print ("fan off percentage: " + "{:.2f}".format(fan_off_percent) +"%")
            print ("---------------------------------")
            print (" ")

        #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # write data to the fan usage log every 60 minutes
        #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        numbermins, numsecs = divmod(time.time(), 60)
        #print ("mins, secs, modulus 60-mins: " + str(numbermins) + " - " + str(numsecs) + " - " + str(numbermins % 60) ) 
        if numbermins % 60 == 0 and numsecs >= 0 and numsecs <= SLEEP_INTERVAL+3   :  ###     % is modulus operator
            logmsg = "pitiki01 - fan stats " + version + time.strftime('%a %d %b %Y %H:%M:%S %Z') + " - CPU temp: " + str(CPU_temp) + " - fan on %: " + "{:.2f}".format(fan_on_percent) +"%"
            writetolog(logmsg, logfile, 100)

        #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # recheck the fan control file every day 
        #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        numhours, extramins = divmod(numbermins, 60)
        #print (" hours + extra mins + modulus 24-hours: " + str(numhours) + " - " + str(extramins) + " - " + str(numhours % 24)  )
        if numhours % 24 == 21 and extramins == 30 and numsecs >= 0 and numsecs <= SLEEP_INTERVAL+3: 
            # recheck the parameters from their file once a day
            print ("** parameter daily recheck ** - number of minutes: " + str(numbermins) + " - " + str(numbermins % 24))
            defaults = readdefaults()
            ON_THRESHOLD = float(defaults['ontemp'])    # usually 55.0 (degrees Celsius): fan starts up at this temperature.
            OFF_THRESHOLD = float(defaults['offtemp'])  # usually 48.0 (degress Celsius): fan shuts off at this temperature.
            SLEEP_INTERVAL = int(defaults['sleep'])     # usually 10 (seconds): how often to check the CPU core temperature.
            logmsg = "pitiki01 - fan control rechecked " + version + time.strftime('%a %d %b %Y %H:%M:%S %Z') + " - on threshold: " + str(ON_THRESHOLD) + "degC" + " - off threshold: " + str(OFF_THRESHOLD) + "degC" + " - sleep interval: " + str(SLEEP_INTERVAL) + " secs" 
            writetolog(logmsg, logfile, 100)

        time.sleep(SLEEP_INTERVAL)

finally:  # this code is run when the try is interrupted with a CTRL-C
    print(" ")
    print("Cleaning up the GPIO pins before stopping")
    print(" ")
    print(" ")
    GPIO.cleanup()
    print ("program ended")

