import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
esp.osdebug(None)
import gc
gc.collect()

ssid = 'Hippo Oasis'
password = 'chillwithhippos'

last_message = 0
message_interval = 5
counter = 0

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

print("Connecting to Wifi...")

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())
