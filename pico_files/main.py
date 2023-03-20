from machine import Pin, I2C
import network
import ubinascii
import utime
import gc
import urequests
from dht20 import DHT20

MAX_ATTEMPTS = 5 # Sets the maximum amount of attempts the device will make before it resets given that it is not able to connect to the network
ssid = 'ut-open' 
CHECK_TIME = 5 # Set the interval (in seconds) at which the device will check if it is connected to the network
MEASURE_TIME = 2 # Sets the interval (in seconds) at which the device will post measuremnts to the database
ATTEMPT_TIME = 5 # Sets the interval (in seconds) at which the device will attempt to connect to the network in the condition if unsuccessful connection

# Defining pins 
i2c0_sda = Pin(8)
i2c0_scl = Pin(9)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl)
dht20 = DHT20(0x38, i2c0)
led = Pin("LED", Pin.OUT)

def main():
    
    connect_wifi()
    
    check_measurements()
             
#-------------------------------------------------------------------------------------------#
    #Function Definitions: Begin
#-------------------------------------------------------------------------------------------#
def connect_wifi():
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid)
    mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
    print("The MAC address of this device is", mac)


    if wlan.isconnected():
        print("Already connected to Wi-Fi")
        return True

    for retry in range(MAX_ATTEMPTS):
        print("Trying to connect to Wi-Fi, attempt", retry+1)
        wlan.connect(ssid)
        utime.sleep(ATTEMPT_TIME)

        if wlan.isconnected():
            print("Successfully connected to Wi-Fi")
            return True

    print("Failed to connect to Wi-Fi after", MAX_ATTEMPTS, "attempts")

    # Try soft reset
    print("Trying soft reset")
    machine.reset()

def check_measurements():
    while True:
        measurements = dht20.measurements
        data = f"Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH"
        try:
            led.on()
            response = urequests.post('http://serf212a.desktop.utk.edu:8086/write', auth=('mydb', 'db'), data=data)
            print(response)
            print(f"Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH")
            gc.collect()
            led.off()
            utime.sleep(MEASURE_TIME)
            
        except:
            print("Failed to post to database, checking connection")
            connect_wifi()
            utime.sleep(CHECK_TIME)

#-------------------------------------------------------------------------------------------#
    #Function Definitions: END
#-------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    main()