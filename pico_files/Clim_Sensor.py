from machine import Pin, I2C
from utime import sleep
from dht20 import DHT20
import network
import ubinascii
import time
import urequests

#Getting pins from pico
i2c0_sda = Pin(8)
i2c0_scl = Pin(9)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl)

dht20 = DHT20(0x38, i2c0)

#Getting MAC Address
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print(mac)

#Connect to the internet
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid='ut-open')
print(wlan.isconnected())


#Some ideas on how to set variables necessary to communicate with influxDB on SERF server
'''
INFLUXDB_URL = ""
INFLUXDB_TOKEN = ""
INFLUXDB_ORG = ""
INFLUXDB_BUCKET =""
TimeZone_INFO = ""

OR 

# Set the databasename,location name
database = "temp/humd"
location = "SERF_212"

# Set the URL for the influxDB 2.0 HTTP API
url = f"http://serf212a:port/write?db={database}"

# Set the authentication header
auth_header = f"Token {credentials.influxUser}:{credentials.influxPW}"
'''

# Checking the temp and humidity each second and posting that to DB
while True:
    measurements = dht20.measurements
    status = f"In {location}, Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH"
    print(status)
    '''
    # Use the requests library to send a POST request to the influxDB
    response = requests.post(
        url=url,
        headers={"Authorization": auth_header},
        status=status
    )

    print(response.status_code)

    # Code 204 = ok
    '''
    sleep(1)