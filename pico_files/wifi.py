import network
import secrets
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid='eduroam', auth=(wlan.wpa2_ent, 'dstewa30', 'Blue082004!!'))
print(wlan.isconnected())

SSID = "eduroam"
PASSWORD = ""
