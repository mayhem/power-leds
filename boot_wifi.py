import network
import gc

gc.collect()

SSID = 'Hippo Oasis'
PASSWORD = 'chillwithhippos'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        pass
print('network config:', wlan.ipconfig('addr4'))
