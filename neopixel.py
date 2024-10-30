from machine import Pin
from neopixel import NeoPixel
pin = Pin(1, Pin.OUT)
np = NeoPixel(pin, 10)
np[0] = (255, 0, 255)
