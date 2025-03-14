import network
from time import sleep
import gc

gc.collect()

SSID = 'Hippo Oasis'
PASSWORD = 'chillwithhippos'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("Disconnect, starting over clean.")
    wlan.disconnect()

print("Sleeping for 5 seconds...")
sleep(5)

print('connecting to network...')
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():
    pass
print('network config:', wlan.ipconfig('addr4'))
