from machine import Pin, unique_id
from neopixel import NeoPixel
from time import sleep, time
from math import fmod
from umqttsimple import MQTTClient
import ubinascii

from gradient import Gradient
from colorsys import hsv_to_rgb

MAX_BRIGHTNESS = 20
NUM_LEDS = 144
NUM_COLS = 28
NUM_ROWS = 5
ROWS = [ 0, 28, 57, 85, 113, 141 ]

MQTT_SERVER = "10.1.1.2"
MQTT_PORT = 1883
CLIENT_ID = ubinascii.hexlify(unique_id())

class Pattern:

    def run(turkish_lamp):
        pass


class PatternRainbowSweep:

    def run(self, lamp):
        step = 1 / NUM_COLS
        hue_offset = 0.0

        leds = [ [0,0,0] for n in range(NUM_LEDS) ]
        while True:
            hue = fmod(hue_offset, 1.0)
            for col in range(NUM_COLS):
                for row in range(NUM_ROWS):
                    led = lamp.led_from_row_col(row, col)
                    r,g,b = hsv_to_rgb(int(fmod(hue, 1.0) * 255), 255, 255)
                    leds[led] = (r,g,b)
                    lamp.set_leds(leds)
                    if lamp.should_exit():
                        return
                    sleep(.01)
                hue += step

            for col in range(NUM_COLS):
                for row in range(NUM_ROWS):
                    led = lamp.led_from_row_col(row, col)
                    leds[led] = (0,0,0)
                    lamp.set_leds(leds)
                    if lamp.should_exit():
                        return
                    sleep(.01)

            hue_offset += .1


class PatternHipposAndDamsels:

    def run(self, lamp):
        g = Gradient([ (0.00, (247, 25, 125)),
                       (0.25, (255, 136, 0)),
                       (0.50, (247, 25, 125)),
                       (0.75, (255, 136, 0)),
                       (1.0, (247, 25, 125)) ])
        leds = [ [0,0,0] for n in range(NUM_LEDS) ]

        # How far we should step for each pixel
        led_step = 1.0 / NUM_COLS 

        # The total gradient shift offset, could be > 1.0!
        shift_offset = 0.0
        while True:
            offset = fmod(shift_offset, 1.0)
            for col in range(NUM_COLS):
                color0 = g.get_color(fmod(col * led_step + offset, 1.0))
                led = lamp.led_from_row_col(0, col)
                leds[led] = color0
                led = lamp.led_from_row_col(1, col)
                leds[led] = color0

                color1 = g.get_color(fmod(col * led_step + (1.0 - offset), 1.0))
                led = lamp.led_from_row_col(3, col)
                leds[led] = color1
                led = lamp.led_from_row_col(4, col)
                leds[led] = color1

                led = lamp.led_from_row_col(2, col)
                if col % 2 == 0:
                    leds[led] = color0
                else:
                    leds[led] = color1

            lamp.set_leds(leds)
            if lamp.should_exit():
                return
            sleep(.05)
            shift_offset += .02

turkish_light = None
def callback(topic, msg):
    global turkish_light
    turkish_light.callback(str(topic, "utf-8"), str(msg, "utf-8"))

class TurkishLamp:


    def __init__(self):
        pin = Pin(1, Pin.OUT)
        self.np = NeoPixel(pin, NUM_LEDS)
        self.stop = False
        self.brightness = 20

        self.c = MQTTClient(CLIENT_ID, MQTT_SERVER, MQTT_PORT)
        self.c.set_callback(callback)
        self.c.connect()
        self.c.subscribe("turkish-light/set")
        print("Connected, subscribed, yo")
        self.next_ping_time = None
        #self.wdt = WDT()

    def set_brightness(self, b):
        self.brightness = b

    def led_from_row_col(self, row, col):
        if row >= len(ROWS):
            return

        start = ROWS[row]
        end = ROWS[row + 1]

        if col >= end - start:
            return None

        return start + col

    def set_leds(self, leds):
        for i, led in enumerate(leds):
            self.np[i] = [ int((led[0] * self.brightness) / 100),
                           int((led[1] * self.brightness) / 100),
                           int((led[2] * self.brightness) / 100) ]
        self.np.write()

    def run(self):
        self.next_ping_time = time() + 500

        patterns = [ PatternRainbowSweep, PatternHipposAndDamsels ]
        pattern = patterns[1]()
        pattern.run(self)


    def should_exit(self):

        self.c.check_msg()
        if time() > self.next_ping_time:
            self.next_ping_time = time() + 500
            self.c.ping()

        #self.wdt.feed()


    def callback(self, topic, msg):
        print(topic, msg)
        try:
            b = int(msg)
        except ValueError:
            return

        if b < 0 or b > MAX_BRIGHTNESS:
            return

        self.brightness = b


turkish_light = TurkishLamp()
turkish_light.run()
