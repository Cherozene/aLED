# LED's go
## Control leds behind you screen with a simple USB-plugged Arduino Nano 

## Hardware Installation
_Coming ~~soon~~_

## Software Installation
### _Set up the controller on host PC_
Project is made for Windows 10 with Python 3.9.7.
(See this tutorial to get Python for Windows 10: https://docs.microsoft.com/en-us/windows/python/beginners)

Install the Python libs listed in _requirements.txt_ file.

```sh
pip install -r requirements.txt
```

Run the .exe by double-clicking the _ihm/ihm.exe_. Should work ¯\_(ツ)_/¯

### _Set up the Arduino Nano - USB Plugged_
Open _arduino/screen\_to\_ledstrip\_fast/screen\_to\_ledstrip\_fast.ino_ with Arduino IDE (https://www.arduino.cc/en/software).
Download FastLED Arduino's library (go through this tuto and search for FastLED in the library manager: https://www.arduino.cc/en/guide/libraries)

Change the macros if needed (N\_LEDS and PIN). 
N\_LEDS is the number of LEDs you want to light up. It should match the LEDs you wrote in _ihm/scripts/default\_config.ini_.
PIN is the pinout of the Arduino, plugged into the LEDs strip control pin.

Compile and download the code to the Arduino.
Arduino has to remain USB-plugged to the computer in order to receive messages from the control center.


