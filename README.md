# fan_control
 Code for managing cooling fans that use a custom PCB to construct a simple on/off controller
 with a PNP transistor that is 'switched' with a GPIO pin signal.

# Raspberry Pi
<p align="center">
  <img src="https://onlinedevices.co.uk/display167" width="250" title="Raspberry Pi4 in a fan cooled case">
</p>

 A control file is used to set:
- upper and lower CPU temperature limits (fan on/off) 
- a sleep interval in seconds, and
- which GPIO pin is used

 The CPU temperature is 'read' every 'sleep interval' seconds and the fan turned on/off as 
 required with the accumulative on/off periods of time calculated and written out to a log file.
