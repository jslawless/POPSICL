from machine import Pin, I2C
from utime import sleep

from dht20 import DHT20


i2c0_sda = Pin(8)
i2c0_scl = Pin(9)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl)

dht20 = DHT20(0x38, i2c0)

while True:
    measurements = dht20.measurements
    print(f"Temperature: {measurements['t']} °C, humidity: {measurements['rh']} %RH")
    sleep(1)