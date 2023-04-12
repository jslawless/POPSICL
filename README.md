# POPSICL
POPSICL - Proactive Optimization of Physics Space Integrated Climate Logging

## How to Make a POPSICL
Acquire the following items:


Raspberry Pi Pico W
DHT20 Temperature and Humidity Sensor
Wires
Popsicle  Sticks
Solder
Soldering Iron

## Part 1: Programming the Raspberry Pi Pico
### Part A: Setting Up the Pico

You’re going to want to have Thonny installed on your computer. It is like an IDE/Code Editor specifically for raspberry pi computers and microcontrollers.  Once you have that, take your Pico, push and hold the BOOTSEL button and plug your Pico into your computer. Release the BOOTSEL button after your Pico is connected. It will mount as a Mass Storage Device called RPI-RP2. Go to 
[this] (https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) website to download the UF2 file that will allow the Pico to read Micropython (make sure to install the latest version!), the language this project was done in. Drag and drop the MicroPython UF2 file onto the RPI-RP2 volume. Your Pico will reboot. You are now running MicroPython. Go ahead and open up Thonny, go to Tools in the upper left corner, then click options. Then go to the Interpreter header, tell Thonny to use the MicroPython interpreter, and click on the “Port” drop down menu and select your Pico (there should only be one option). After that hit Okay, and then you should get an indication in the terminal that micropython is running on the Pico! If not just restart Thonny.

### Part B: Importing the DHT20 Reading Library:

In Thonny, make a new file on the Pico called “dht20.py” and copy past the code under the file of the same name on this [repo] (https://github.com/flrrth/pico-dht20). This file takes the information from the DHT20 and makes it accessible in other python scripts. Also add a file called “__init__.py” with the string “from .dht20 import DHT20” so the class “DHT20” in the “dht20.py” file becomes globally accessible for all files made on the pico.

Create a new file on the pico called “main.py” and this is where the code we wrote goes! You can get it from the main.py file on this repo. Essentially there are two main tasks that it needs to complete. The pico needs to connect to the internet, and the pico needs to send data from the DHT20 to the influxDB server. But before any of that happens the first thing one must do is define the pins used by the DHT20 and the LED. After those are defined, create a connect_wifi_() function. You will use the network library of micropython and for most of what we’ll do it will come from network.WLAN(network.STA_IF), so we can just set it to a variable like “wlan = network.WLAN(network.STA_IF)”. Use “wlan.active(True)” to turn on wifi functionality, then “wlan.connect(insert string of wifi ssid)” to connect it to the wifi. This is utopen in our case, and the pico needs to be registered through NetReg beforehand for it to connect. Then get the mac address and print it.
