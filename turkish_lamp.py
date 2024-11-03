import network
from machine import Pin, unique_id
from neopixel import NeoPixel
import json
from time import sleep, time
from math import fmod
from umqttsimple import MQTTClient
import ubinascii

from gradient import Gradient
from colorsys import hsv_to_rgb

SSID = 'Hippo Oasis'
PASSWORD = 'chillwithhippos'

MAX_BRIGHTNESS = 50
NUM_LEDS = 144
NUM_COLS = 28
NUM_ROWS = 5

USE_NETWORK = True
MQTT_SERVER = "10.1.1.2"
MQTT_PORT = 1883
CLIENT_ID = ubinascii.hexlify(unique_id())

class Pattern:

    def __init__(self):
        self.name = None

    def run(turkish_lamp):
        pass


class PatternRainbowSweep:

    def __init__(self):
        self.name = "daytime"

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
                    lamp.set_all()
                    return
                sleep(.01)
                hue += step

            for col in range(NUM_COLS):
                for row in range(NUM_ROWS):
                    led = lamp.led_from_row_col(row, col)
                    leds[led] = (0,0,0)
                    lamp.set_leds(leds)
                if lamp.should_exit():
                    lamp.set_all()
                    return
                sleep(.01)

            hue_offset += .1

    def runs(self, lamp):
        leds = [ [0,0,0] for n in range(NUM_LEDS) ]
        for i in range(1000000000):
            for row in range(NUM_ROWS):
                for col in range(NUM_COLS):
                    led = lamp.led_from_row_col(row, col)
                    if i % 2 == 0:
                        leds[led] = (255, 0, 0)
                    else:
                        leds[led] = (0, 0, 0)
                    lamp.set_leds(leds)
                    sleep(.01)



class PatternHipposAndDamsels:

    def __init__(self):
        self.name = "nighttime"

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
                offset0 = fmod(col * led_step + offset, 1.0)
                color0 = g.get_color(offset0)
                led = lamp.led_from_row_col(0, col)
                leds[led] = color0
                led = lamp.led_from_row_col(1, col)
                leds[led] = color0

                offset1 = fmod(col * led_step + (1.0 - offset), 1.0)
                color1 = g.get_color(offset1)
                led = lamp.led_from_row_col(3, col)
                leds[led] = color1
                led = lamp.led_from_row_col(4, col)
                leds[led] = color1

                led = lamp.led_from_row_col(2, col)
                if led is not None:
                    if col % 2 == 0:
                        leds[led] = color0
                    else:
                        leds[led] = color1

            lamp.set_leds(leds)
            if lamp.should_exit():
                break

            sleep(.05)
            shift_offset += .02

        # turn off the leds
        lamp.set_all()


turkish_light = None
def callback(topic, msg):
    global turkish_light
    turkish_light.callback(str(topic, "utf-8"), str(msg, "utf-8"))

class TurkishLamp:


    def __init__(self):
        pin = Pin(26, Pin.OUT)
        self.np = NeoPixel(pin, NUM_LEDS)
        self.brightness = 100
        self.state = False
        self.stop = False
        self.effect = None
        self.current_pattern = None
        self.next_pattern_args = None

        self.startup()
        self.connect_wifi()

        if USE_NETWORK:
            self.c = MQTTClient(CLIENT_ID, MQTT_SERVER, MQTT_PORT)
            self.c.set_callback(callback)
            self.c.connect()
            self.c.subscribe("turkish-light/set")
            self.c.publish("turkish-light/hello", "hi!")
            print("Connected, subscribed, yo")
            self.next_ping_time = None
        else:
            self.c = None

        #self.wdt = WDT()

        print("Start lamp!")
        self.set_all()

    def startup(self):
        for i in range(3):
            for i in range(50):
                self.np[i] = ((214, 95, 4))
            self.np.write()
            sleep(.5)
            for i in range(50):
                self.np[i] = ((83, 4, 186))
            self.np.write()
            sleep(.5)
        self.set_all((0, 0, 128))

    def connect_wifi(self):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print("Disconnect, starting over clean.")
            wlan.disconnect()

        print('connecting to network...')
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            pass
        print('network config:', wlan.ipconfig('addr4'))

    def set_brightness(self, b):
        self.brightness = b

    def led_from_row_col(self, row, col):
        assert row < NUM_ROWS
        assert col < NUM_COLS
        return (row * NUM_COLS) + col

    def set_leds(self, leds):
        for i, led in enumerate(leds):
            self.np[i] = [ int((led[0] * self.brightness * MAX_BRIGHTNESS) / 10000),
                          int((led[1] * self.brightness * MAX_BRIGHTNESS) / 10000),
                          int((led[2] * self.brightness * MAX_BRIGHTNESS) / 10000) ]
        self.np.write()

    def set_all(self, color=(0,0,0)):
        self.set_leds([ color for n in range(NUM_LEDS) ])

    def run(self):

        self.next_ping_time = time() + 500

        self.patterns = { "daytime": PatternRainbowSweep, 
                          "bedtime": PatternHipposAndDamsels }
        while True:

            if self.current_pattern:
                self.current_pattern.run(self)
            else:
                # Loop until we're told to exit, which means something is about to happen
                while not self.should_exit():
                    sleep(.01)

            # reset the stop flag
            self.stop = False

            if self.next_pattern_args is None:
                continue

            # Shall we turn on?
            if not self.state and self.next_pattern_args["state"]:
                self.current_pattern = self.patterns[self.next_pattern_args["effect"]]()
                self.brightness = self.next_pattern_args["brightness"]
                self.state = True
            elif self.state and not self.next_pattern_args["state"]:
                self.current_pattern = None
                self.state = False
            elif self.state and self.next_pattern_args["state"] and \
                self.current_pattern.name != self.next_pattern_args["effect"]:
                self.current_pattern = self.patterns[self.next_pattern_args["effect"]]()
                self.brightness = self.next_pattern_args["brightness"]

            self.next_pattern_args = None


    def should_exit(self):

        if self.c is not None:
            self.c.check_msg()
            if time() > self.next_ping_time:
                self.next_ping_time = time() + 500
                self.c.ping()

        #self.wdt.feed()

        return self.stop


    def callback(self, topic, msg):
        #print(topic, msg)

        args = json.loads(msg)
        try:
            if args["brightness"] < 0 or args["brightness"] > 100:
                return
            effect = args["effect"]
            state = args["state"]
        except KeyError:
            return

        if effect not in self.patterns:
            return

        if args["state"] and self.state and args["effect"] == self.current_pattern.name:
            self.brightness = args["brightness"]
            return

        self.stop = True
        self.next_pattern_args = args

turkish_light = TurkishLamp()
turkish_light.run()
