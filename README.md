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

You’re going to want to have Thonny installed on your computer. It is like an IDE/Code Editor specifically for raspberry pi computers and microcontrollers.  Once you have that, take your Pico, push and hold the BOOTSEL button and plug your Pico into your computer. Release the BOOTSEL button after your Pico is connected. It will mount as a Mass Storage Device called RPI-RP2. Go to [this](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) website to download the UF2 file that will allow the Pico to read Micropython (make sure to install the latest version!), the language this project was done in. Drag and drop the MicroPython UF2 file onto the RPI-RP2 volume. Your Pico will reboot. You are now running MicroPython. Go ahead and open up Thonny, go to Tools in the upper left corner, then click options. Then go to the Interpreter header, tell Thonny to use the MicroPython interpreter, and click on the “Port” drop down menu and select your Pico (there should only be one option). After that hit Okay, and then you should get an indication in the terminal that micropython is running on the Pico! If not just restart Thonny.

### Part B: Importing the DHT20 Reading Library:

In Thonny, make a new file on the Pico called “dht20.py” and copy past the code under the file of the same name on this [repo](https://github.com/flrrth/pico-dht20). This file takes the information from the DHT20 and makes it accessible in other python scripts. Also add a file called “__init__.py” with the string “from .dht20 import DHT20” so the class “DHT20” in the “dht20.py” file becomes globally accessible for all files made on the pico.

### Part C: "main.py" code

Create a new file on the pico called “main.py” and this is where the code we wrote goes! You can get it from the main.py file on this [repo](https://github.com/jslawless/POPSICL/blob/main/pico_files/main.py). Essentially there are two main tasks that it needs to complete. The pico needs to connect to the internet, and the pico needs to send data from the DHT20 to the influxDB server. But before any of that happens, we'll need to set our foundation.  
   
First let's import the necessary libraries.
```python
from machine import Pin, I2C
import network
import ubinascii
import socket
import utime
import gc
import sys
import urequests
import hashlib
from dht20 import DHT20
```

Next, we set some variables to be used later in the code, they'll make more sense later. 
```python
MAX_ATTEMPTS = 5 # Sets the maximum amount of attempts the device will make before it resets given that it is not able to connect to the network
ssid='ut-open' 
CHECK_TIME = 5 # Set the interval (in seconds) at which the device will check if it is connected to the network
MEASURE_TIME = 60 # Sets the interval (in seconds) at which the device will post measuremnts to the database
ATTEMPT_TIME = 5 # Sets the interval (in seconds) at which the device will attempt to connect to the network in the condition if unsuccessful connection
```

Now we must define the pins used by the DHT20 and the LED.
```python
# Defining pins 
i2c0_sda = Pin(8)
i2c0_scl = Pin(9)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl)
dht20 = DHT20(0x38, i2c0)
led = Pin("LED", Pin.OUT)
```

After those are defined, let's go ahead and define our main function which will call the two functions that make up this program.
```python
def main():
    
    mac,password = connect_wifi()
    
    check_measurements(mac,password)
```

Then, let's create a connect_wifi_() function. You will use the network library of micropython and for most of what we’ll do it will come from network.WLAN(network.STA_IF), so we can just set it to a variable like “wlan = network.WLAN(network.STA_IF)”. Use “wlan.active(True)” to turn on wifi functionality, then “wlan.connect("ssid name")” to connect the Pico to your router. This is utopen in our case, and the pico needs to be registered through NetReg beforehand for it to connect. Then we get the mac address of the pico (this will be useful as a unique identifier later) and print
```python
def conne
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    mac = mac.replace(":","")
    password = ubinascii.hexlify(hashlib.sha256(mac.encode("utf-8")).digest())
    print(f"The MAC address of this device is {mac}")
    print(f"The authentication header password for this device is {password}")
```

Then we're going to want to ensure that the Pico successfully connected to the Wi-Fi, and if it is, we will print a state so we know it was successful and we also get the ip address of the Pico.
```python
if wlan.isconnected():
        print("Already connected to Wi-Fi")
        ip = wlan.ifconfig()[0]
        print("The IP address of this device is", ip)
        return True
```

Now if the above if statement is false, we will then try to reconnect to the wifi a number of times before doing a soft reset of the pico as a last resort. This is where the MAX_ATTEMPTS and ATTEMPT_TIME variables comes into play, as part of the for loop to reconnect. After wlan.connect() is run again, we use another if statement to see if the connection was successful just as we did above, but if it doesn't successfully connect then we go back to the top of the for loop and try again.
```python
else:
    for retry in range(MAX_ATTEMPTS):
        print("Trying to connect to Wi-Fi, attempt", retry+1)
        wlan.connect(ssid)
        utime.sleep(ATTEMPT_TIME)

        if wlan.isconnected():
            print("Successfully connected to Wi-Fi")
            ip = wlan.ifconfig()[0]
            print("The IP address of this device is", ip)
            return True
```

If the Pico fails to connect for MAX_ATTEMPTS number of attempts, then it will go into a soft reset and the program will start from the beginning afterwards.
```python
print("Failed to connect to Wi-Fi after", MAX_ATTEMPTS, "attempts")

# Try soft reset
print("Trying soft reset")
sys.exit()
```
And that finishes our code for our connect_wifi() function! Now moving on to the check_measurements() function.  

First we want to get the measurements from the DHT20 at that instant. Then we take the element of the temperature and relative humidity from that list that the measurements are stored in. We make two strings, one for temperature and humidity, for us to push to our influxDB. In the first part of the string, we give the type of data being measured that corresponds to a place on the influxDB "measurement" then we give the mac address of the pico to create a new entry for data on the database, and finally we give the actual data value to store, indicating whether the value is temperature or humidity.
```python
while True:
        measurements = dht20.measurements     
        dataT = f"measurement,host={mac} temp={measurements['t']}"
        dataH = f"measurement,host={mac} humidity={measurements['rh']}"
```

Once we set the strings with the recorded data values for that instant, we are going to try to post the data strings to the database. The led on the pico should turn on and back off when this happen to serve as a visual indicator that it is successfully running. In our post request we give the URL of the database, a username and password to authenticate, and then the specific data string to be posted. We then print the status code of the request in the console, which should read 204 to indicate a successful post. "gc.collect()" is a function that essentially clears the cache on the Pico to prevent it from running out of RAM after making so many data measurements and posts. And before the Pico gets new data, it'll wait the amount of time put in initially to the MEASURE_TIME variable.
```python
try:
            led.on()
            responseT = urequests.post('http://serf212a.desktop.utk.edu:8086/write?db=mydb',auth=('popsicl_test', 'test'),data=dataT)
            print(responseT.status_code)
            responseH = urequests.post('http://serf212a.desktop.utk.edu:8086/write?db=mydb',auth=('popsicl_test', 'test'),data=dataH)
            print(responseH.status_code)
            print(f"Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH")
            gc.collect()
            led.off()
            utime.sleep(MEASURE_TIME)
```

If the try bloock fails, it means that the server request failed, so we run this except block, hopefully fixing the issue by attempting to reconnect to the wifi, and then waiting a few seconds just to make sure the Pico is ready to try and post again, this time using the CHECK_TIME variable.
```python
except:
      print("Failed to post to database, checking connection")
      led.off()
      connect_wifi()
      utime.sleep(CHECK_TIME)
```

And that's the end of our check_measurements() function! Other than that, we put our connect_wifi() and check_measurements() function in the main function of the main.py script, and then we call the function main():
```python
if __name__ == '__main__':
    main()
```

## Part 2: Setting up the Database

Follow the instructions on [this website](https://hub.docker.com/r/philhawthorne/docker-influxdb-grafana) in order to set the docker image. This will run Chronograf, Influxdb and Grafana in a docker image on your machine. To stop the image, run
```bash
docker stop docker-influxdb-grafana
```
and to start it run
```
docker start docker-influxdb-grafana
```
To create a database in influxdb, you'll need to communicate through the port you chose for it to run on through the use of the curl command. Here's how to make a new database with the name 'mydb':
```
curl -i -XPOST http://localhost:8086/query --data-urlencode "q=CREATE DATABASE mydb"
```
Now data from your popsicl can be posted to mydb through that port.

If you want to enable security, you'll need to create an admin user of the database. Then you'll need to ssh into the docker image using 
```
docker exec -it docker-influxdb-grafana bash
```
and follow the instructions [here](https://docs.influxdata.com/influxdb/v1.8/administration/authentication_and_authorization/) to enable authentication.
