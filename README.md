# Fan control
 Code for managing cooling fans that use a custom PCB to construct a simple on/off controller with a PNP transistor that is 'switched' with a GPIO pin signal.

 Initially, python code for a Raspberry Pi has been developed, but additional code for a variety of microcontrollers is planned - more details on this project are published <a href="https://onlinedevices.co.uk/Raspberry+Pi+cooling+fan+control+project" target="_blank" >here</a>.

## Raspberry Pi
Typical use is as shown below for a 3D printed case for a Pi4 with a separate 3D printed frame for the custom PCB - the designs for these 3D prints can be downloaded from <a href="https://www.prusaprinters.org/prints/71045-fan-cooled-raspberry-pi-4-case" target="_blank">here</a>.

<img src="https://onlinedevices.co.uk/display1679" width="354" height="300"> &nbsp; &nbsp; <img src="https://onlinedevices.co.uk/display1844" width="354" height="300">


 For the Python code a .txt control file is used to set:
- upper and lower CPU temperature limits (fan on/off) 
- a sleep interval in seconds, and
- which GPIO pin is used

 The CPU temperature is 'read' every 'sleep interval' seconds and the fan turned on/off as 
 required with the accumulative on/off periods of time calculated and written out to a log file.
