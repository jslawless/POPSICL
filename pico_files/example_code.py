# Link: https://forums.raspberrypi.com/viewtopic.php?t=344667
# Source: Electrocredible.com, Language: MicroPython
# load libraries

import credentials
import machine
import sys
import network
import rp2
import utime as time
import urequests as requests
from bmp280 import *

led_onboard = machine.Pin('LED', machine.Pin.OUT)
led_onboard.value(0)

# Wifi configuration
rp2.country('DE')
wlan = network.WLAN(network.STA_IF)

# Function: connect to Wifi
def wlanConnect():
    if not wlan.isconnected():
        print('WLAN-Verbindung herstellen')
        wlan.active(True)
        wlan.connect(credentials.wlanSSID, credentials.wlanPW)
        for i in range(15):
            if wlan.status() < 0 or wlan.status() >= 3:
                break
            led_onboard.toggle()
            time.sleep(1)
    if wlan.isconnected():
        led_onboard.on()
        netConfig = wlan.ifconfig()
        print('IPv4 adress:', netConfig[0], '/', netConfig[1])
    else:
        print('No wifi connection')
        led_onboard.on()

def send_data(dictPackage):
    # Connect to wifi
    wlanConnect()

    # Set the databasename,measurement name
    database = "weather"
    measurement_name = "indoor"
    location = "office"

    # Set the URL for the influxDB 2.0 HTTP API
    url = f"http://raspberrypi.fritz.box:8086/write?db={database}"

    # Set the authentication header
    auth_header = f"Token {credentials.influxUser}:{credentials.influxPW}"

    # form the data as a string, beginning with measurement name/flags, then the key/values and delete last char
    data = f"{measurement_name},location={location} "
    for key,value in dictPackage.items():
        data += f"{key}={value},"
    data = data[0:-1]

    # Use the requests library to send a POST request to the influxDB
    response = requests.post(
        url=url,
        headers={"Authorization": auth_header},
        data=data
    )

    print(response.status_code)
    # Code 204 = ok

# Initialise I2C bus
i2c = machine.I2C(0,scl=machine.Pin(17),sda=machine.Pin(16),freq=400000)
i2cscan = i2c.scan()

if i2cscan == []:
    print("Error establishing I2C bus")
    raise ValueError('I2C problems')
else:
    print(i2cscan)

# And a short delay to wait until the I2C port has finished activating.
time.sleep(1)

# initialize the sensors
bmp = BMP280(i2c)
bmp.use_case(BMP280_CASE_INDOOR)

dictData = {
        'temperaturebmp280':0,
        'pressurebmp280':0,
        }

while True:
    try:
        dictData['pressurebmp280'] = bmp.pressure
        dictData['temperaturebmp280'] = bmp.temperature
        
        send_data(dictData)
        print('disconnecting and going to sleep')
        wlan.disconnect()
        led_onboard.off()
        time.sleep(300)

    except KeyboardInterrupt:
        led_onboard.off()
        wlan.disconnect()
        sys.exit()

    except Exception as e:
        print('Exception in while-loop')
        with open("PicoWLog.txt", "a") as logfile:
            logfile.write(str(machine.RTC().datetime()) + ' Exception in while loop \n')
            logfile.write(getattr(e, 'message', repr(e)))
            logfile.write('\n I2C scan: ')
            logfile.write(str(i2c.scan()))
            logfile.write('\n')
        led_onboard.on()
        wlan.disconnect()
        time.sleep(10)
        machine.reset()

