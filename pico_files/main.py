from machine import Pin, I2C
import machine
import network
import ubinascii
import socket
import utime
import gc
import sys
import urequests
import hashlib
# import bootsel
from dht20 import DHT20

MAX_ATTEMPTS = 5 # Sets the maximum amount of attempts the device will make before it resets given that it is not able to connect to the network
ssid='ut-open'
CHECK_TIME = 5 # Set the interval (in seconds) at which the device will check if it is connected to the network
MEASURE_TIME = 60 # Sets the interval (in seconds) at which the device will post measuremnts to the database
ATTEMPT_TIME = 5 # Sets the interval (in seconds) at which the device will attempt to connect to the network in the condition if unsuccessful connection

# Defining pins
i2c0_sda = Pin(8)
i2c0_scl = Pin(9)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl)
dht20 = DHT20(0x38, i2c0)
led = Pin("LED", Pin.OUT)

def main():

    blinky()
    blinky()
    blinky()
    blinky()
    blinky()
    utime.sleep(0.5)

    mac,password = connect_wifi()

    check_measurements(mac,password)

#-------------------------------------------------------------------------------------------#
    #Function Definitions: Begin
#-------------------------------------------------------------------------------------------#

def print_device_info(mac,password):
    print(f"The MAC address of this device is {mac}")
    print(f"The authentication header password for this device is {password}")

def connect_wifi():

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    mac = mac.replace(":","")
    password = ubinascii.hexlify(hashlib.sha256(mac.encode("utf-8")).digest())
    password = password.decode("UTF-8")

    print_device_info(mac,password)

    if wlan.isconnected():
        print("Already connected to Wi-Fi")
        ip = wlan.ifconfig()[0]
        print("The IP address of this device is", ip)
        return mac,password

    else:
        for retry in range(MAX_ATTEMPTS):
            # checkForResetButton()
            print_device_info(mac,password)
            print("Trying to connect to Wi-Fi, attempt", retry+1)
            wlan.connect(ssid)

            if wlan.isconnected():
                print("Successfully connected to Wi-Fi")
                ip = wlan.ifconfig()[0]
                print("The IP address of this device is", ip)
                return mac,password
            else:
                print("Unable to connect. Sleeping before trying again.")
                utime.sleep(ATTEMPT_TIME)

        print("Failed to connect to Wi-Fi after", MAX_ATTEMPTS, "attempts")

        # Try soft reset
        print("Trying soft reset -- ")
        machine.reset()

def blinky():
    led.on()
    utime.sleep(0.1)
    led.off()
    utime.sleep(0.05)

# def checkForResetButton():
#     if bootsel.button():
#         blinky()
#         blinky()
#         machine.reset()

def check_measurements(mac,password):
    while True:

        # checkForResetButton()

        measurements = dht20.measurements
        dataT = f"measurement,host={mac} temp={measurements['t']}"
        dataH = f"measurement,host={mac} humidity={measurements['rh']}"

        try:
            led.on()
            responseT = urequests.post('http://serf212a.desktop.utk.edu:8086/write?db=nielsen',auth=(mac, password),data=dataT)
            print(responseT.status_code)
            responseH = urequests.post('http://serf212a.desktop.utk.edu:8086/write?db=nielsen',auth=(mac, password),data=dataH)
            print(responseH.status_code)
            print(f"Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH")
            gc.collect()
            led.off()
            utime.sleep(MEASURE_TIME)

        except:
            print("Failed to post to database, checking connection")
            led.off()
            connect_wifi()
            utime.sleep(CHECK_TIME)

#-------------------------------------------------------------------------------------------#
    #Function Definitions: END
#-------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    main()
