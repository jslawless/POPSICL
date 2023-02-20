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

#Getting MAC Address, hostname, and IP
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
hostname = network.WLAN().config('hostname')
ip = network.WLAN().config('ip')
print(f"My MAC address is: {mac}")
print(f"My hostname is: {hostname}")
print(f"My hostname is: {ip}")


#Connect to the internet
wlan.connect(ssid='ut-open')
if wlan.isconnected():
    print("Pico is online")

else:
    print("Pico could not connect to the internet!")
    reboot = input("Reboot Pico? (y/n): ")
    if reboot == y:
        machine.reset()


#Some ideas on how to set variables necessary to communicate with influxDB on SERF server
# Set the location name
location = "SERF_212"

# Set the URL for the influxDB 2.0 HTTP API
url = "http://localhost:8086/api/v2/write?bucket=db/rp&precision=ns"

# Set the authentication header
auth_header = f"Token {username}:{password}"

#Set the refresh rate
refresh = 10

# Checking the temp and humidity every 10s and posting that to DB
while True:
    if not wlan.isconnected():
        print("Pico has lost connection!")
        machine.reset()
        break

    measurements = dht20.measurements
    status = f"In {location}, Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH"
    print(status)

    data = f"climate,location={location} temperature={measurements['t']},humidity={measurements['rh']}"

    # Use the requests library to send a POST request to the influxDB

    response = requests.post(
        url=url,
        headers={"Authorization": auth_header},
        status=status
    )

    print(response.status_code)

    # Code 204 = ok
    
    sleep(refresh)