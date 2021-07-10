# fan_control
 Code for managing cooling fans that use a custom PCB to construct a simple on/off controller
 with a PNP transistor that is 'switched' with a GPIO pin signal.

# Raspberry Pi
.. image:: https://onlinedevices.co.uk/display167
   :width: 300 px

 A control file is used to set:
- upper and lower CPU temperature limits (fan on/off) 
- a sleep interval in seconds, and
- which GPIO pin is used

 The CPU temperature is 'read' every 'sleep interval' seconds and the fan turned on/off as 
 required with the accumulative on/off periods of time calculated and written out to a log file.
