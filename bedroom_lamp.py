import network
from machine import Pin, unique_id
from neopixel import NeoPixel
import json
from random import random, randint
from time import sleep, time
from math import fmod
from umqttsimple import MQTTClient
import ubinascii

from gradient import Gradient
from _colorsys import c_hsv_to_rgb, c_rgb_to_hsv

SSID = 'Hippo Oasis'
PASSWORD = 'chillwithhippos'

MAX_BRIGHTNESS = 50
NUM_LEDS = 288 
HUE_STEP = 10

USE_NETWORK = True
MQTT_SERVER = "10.1.1.2"
MQTT_PORT = 1883
CLIENT_ID = ubinascii.hexlify(unique_id())

class Pattern:

    def __init__(self, lamp):
        self.name = None
        self.lamp = lamp

    def set_color(self, color):
        leds = [ [0,0,0] for n in range(NUM_LEDS) ]
        for led in range(NUM_LEDS):
            leds[led] = color
        self.lamp.set_leds(leds)

    def run(self):
        pass


class PatternSolid(Pattern):

    def __init__(self, lamp):
        Pattern.__init__(self, lamp)
        self.name = "solid"
        self.color = (255, 255, 245)

    def run(self):
        self.set_color(self.color)
        while not self.lamp.should_exit():
            sleep(.03)

class PatternDaytime(Pattern):

    def __init__(self, lamp):
        Pattern.__init__(self, lamp)
        self.name = "daytime"
        self.color = (255, 128, 128)

    def run(self):
        self.set_color(self.color)
        while not self.lamp.should_exit():
            sleep(.03)


class PatternBedtime(Pattern):

    def __init__(self, lamp):
        Pattern.__init__(self, lamp)
        self.name = "nighttime"
        self.color = (255, 5, 0)

    def run(self):
        self.set_color(self.color)
        while not self.lamp.should_exit():
            sleep(.03)


bedroom_light = None
def callback(topic, msg):
    global bedroom_light
    try:
        bedroom_light.callback(str(topic, "utf-8"), str(msg, "utf-8"))
    except Exception as err:
        print(err)

class BedroomLamp:
    def __init__(self):
        pin = Pin(1, Pin.OUT)
        self.np = NeoPixel(pin, NUM_LEDS)
        self.brightness = 10
        self.state = False
        self.stop = False
        self.effect = None
        self.current_pattern = None
        self.next_pattern_args = None
        self.solid_color = [255, 0, 190]

        self.startup()
        self.connect_wifi()

        if USE_NETWORK:
            self.c = MQTTClient(CLIENT_ID, MQTT_SERVER, MQTT_PORT)
            self.c.set_callback(callback)
            self.c.connect()
            self.c.subscribe("mood-light/set")
            self.c.subscribe("mood-light/color")
            self.c.subscribe("mood-light/brightness")
            self.next_ping_time = None
        else:
            self.c = None

#        self.wdt = WDT()

        print("Start lamp!")
        self.set_all()

    def startup(self):
        for i in range(3):
            for i in range(NUM_LEDS):
                self.np[i] = (214, 95, 4)
            self.np.write()
            sleep(.15)
            for i in range(NUM_LEDS-1):
                self.np[i] = (83, 4, 186)
            self.np.write()
            sleep(.15)
        self.set_all((8, 0, 0))

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
#        print('network config:', wlan.ipconfig('addr4'))

    def set_brightness(self, b):
        self.brightness = b

    def set_leds(self, leds):
        for i, led in enumerate(leds):
            self.np[i] = [ int((led[0] * self.brightness * MAX_BRIGHTNESS) / 10000),
                          int((led[1] * self.brightness * MAX_BRIGHTNESS) / 10000),
                          int((led[2] * self.brightness * MAX_BRIGHTNESS) / 10000) ]
        self.np.write()

    def set_all(self, color=(0,0,0)):
        self.set_leds([ color for n in range(NUM_LEDS) ])

    def run(self):
        if not USE_NETWORK:
            p = PatternSolid()
            p.run()

        self.next_ping_time = time() + 500

        self.patterns = { "daytime": PatternDaytime , 
                          "bedtime": PatternBedtime }
        while True:

            if self.current_pattern:
                self.current_pattern.run()
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
                self.current_pattern = self.patterns[self.next_pattern_args["effect"]](self)
                self.brightness = self.next_pattern_args["brightness"]
                if "color" in self.next_pattern_args:
                    self.solid_color = self.next_pattern_args["color"]
                self.state = True
            # Turn off?
            elif self.state and not self.next_pattern_args["state"]:
                self.current_pattern = None
                self.state = False
                self.set_all()
            # Change pattern?
            elif self.state and "effect" in self.next_pattern_args and \
                self.next_pattern_args["state"] and \
                self.current_pattern.name != self.next_pattern_args["effect"]:

                self.current_pattern = self.patterns[self.next_pattern_args["effect"]](self)
                self.brightness = self.next_pattern_args["brightness"]
                try:
                    self.solid_color = self.next_pattern_args["color"]
                except KeyError:
                    pass
            # Keep pattern, update params
            else:
                print("adj", self.next_pattern_args)
                if "brightness" in self.next_pattern_args:
                    self.brightness = self.next_pattern_args["brightness"]
                if "color" in self.next_pattern_args:
                    self.solid_color = self.next_pattern_args["color"]

            self.next_pattern_args = None


    def should_exit(self):

        if self.c is not None:
            self.c.check_msg()
            if time() > self.next_ping_time:
                self.next_ping_time = time() + 500
                self.c.ping()

#        self.wdt.feed()

        return self.stop
    
    def hex_to_rgb(self, hex):
        rgb = []
        for i in (0, 2, 4):
            rgb.append(int(hex[i:i+2], 16))
        return rgb

    def callback(self, topic, msg):
        print(topic, msg)
        if msg[0] == "{":
            try:
                args = json.loads(msg)
            except ValueError:
                return
        else:
            if topic.endswith("brightness"):
                step = 5 if self.brightness > 10 else 1
                if msg == "up":
                    brightness = min(100, self.brightness + step)
                elif msg == "down":
                    brightness = max(1, self.brightness - step)
                else:
                    try:
                        brightness = int(msg)
                        if brightness > 100 or brightness < 1:
                            return
                    except ValueError:
                        return
                self.next_pattern_args = { "brightness": brightness, "state": True }
                self.stop = True
                return
            if topic.endswith("color"):
                if msg in ("up", "down"):
                    h,s,v = c_rgb_to_hsv(self.solid_color)
                    if msg == "up":
                        h = min(255, h + HUE_STEP)
                    else:
                        h = max(0, h - HUE_STEP)
                    color = c_hsv_to_rgb((h,s,v))
                else:
                    color = self.hex_to_rgb(msg[1:])
                    for i in range(3):
                        if color[0] < 0 or color[0] > 255:
                            return
                
                self.next_pattern_args = { "color": color, "state": True}
                self.stop = True
                return
            return

        try:
            state = args["state"]
        except KeyError:
            state = self.state

        brightness = args.get("brightness", 0)
        if brightness < 0 or brightness > 100:
            return
        
        color = args.get("color", None)
        if color is not None:
            r,g,b = [ int(x) for x in color.split(",") ]
            if r >= 0 and g >= 0 and b >= 0 and r <= 255 and g <= 255 and b <= 255:
                args["color"] = (r,g,b)
            else:
                return

        rgb = args.get("rgb", None)
        if rgb is not None:
            args["color"] = rgb

        effect = args.get("effect", "")
        if args["state"] and effect not in self.patterns:
            return

        if args["state"] and self.state and args["effect"] == self.current_pattern.name:
            self.brightness = args["brightness"]
            return

        self.stop = True
        self.next_pattern_args = args

bedroom_light = BedroomLamp()
bedroom_light.run()
