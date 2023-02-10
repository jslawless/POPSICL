import network
import secrets
import time
import urequests


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid='ut-open')
print(wlan.isconnected())

SSID = "ut-open"
PASSWORD = ""


astronauts = urequests.get("http://api.open-notify.org/astros.json").json()
number = astronauts['number']
for i in range(number):
   print(astronauts['people'][i]['name'])
