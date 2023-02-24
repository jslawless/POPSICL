from machine import Pin, I2C
import network
import secrets
import utime
import urequests
import uasyncio
from dht20 import DHT20

MAX_ATTEMPTS = 5 # Sets the maximum amount of attempts the device will make before it resets given that it is not able to connect to the network
ssid = 'ut-open' 
CHECK_TIME = 900 # Set the interval (in seconds) at which the device will check if it is connected to the network
MEASURE_TIME = 5 # Sets the interval (in seconds) at which the device will post measuremnts to the database
ATTEMPT_TIME = 5 # Sets the interval (in seconds) at which the device will attempt to connect to the network in the condition if unsuccessful connection

# Defining pins 
i2c0_sda = Pin(8)
i2c0_scl = Pin(9)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl)
dht20 = DHT20(0x38, i2c0)

def main():
    
    loop = uasyncio.get_event_loop()
    loop.create_task(schedule_check())
    loop.create_task(check_measurements())
    loop.run_forever()
             
#-------------------------------------------------------------------------------------------#
    #Function Definitions: Begin
#-------------------------------------------------------------------------------------------#
async def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)


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

    # Wait for the reset to complete
    utime.sleep(ATTEMPT_TIME)

    # Try connecting to Wi-Fi again after reset
    return connect_wifi()

async def check_measurements():
    while True:
        measurements = dht20.measurements
        data = f"Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH"
        response = urequests.post('http://serf212a.desktop.utk.edu:8086/write', auth=('mydb', 'db'), data=data)
        print(response)
        print(f"Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH")
        await uasyncio.sleep(MEASURE_TIME)
        
async def schedule_check():
    while True:
        await connect_wifi()
        await uasyncio.sleep(CHECK_TIME) # Wait for 15 minutes
    
#-------------------------------------------------------------------------------------------#
    #Function Definitions: END
#-------------------------------------------------------------------------------------------#

if __name__ == '__main__':
    main()