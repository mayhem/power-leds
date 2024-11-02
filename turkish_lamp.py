from machine import Pin
from neopixel import NeoPixel
from time import sleep
from math import fmod

from gradient import Gradient

NUM_LEDS = 144
NUM_COLS = 28
NUM_ROWS = 5
ROWS = [ 0, 28, 57, 85, 113, 141 ]

class TurkishLamp:


    def __init__(self):
        pin = Pin(1, Pin.OUT)
        self.np = NeoPixel(pin, NUM_LEDS)
        self.stop = False
        self.brightness = 20

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

    def hsv_to_rgb(self, H, S, V):

        # Check if the color is Grayscale
        if S == 0:
            R = V
            G = V
            B = V
            return (R, G, B)

        # Make hue 0-5
        region = H // 43;

        # Find remainder part, make it from 0-255
        remainder = (H - (region * 43)) * 6; 

        # Calculate temp vars, doing integer multiplication
        P = (V * (255 - S)) >> 8;
        Q = (V * (255 - ((S * remainder) >> 8))) >> 8;
        T = (V * (255 - ((S * (255 - remainder)) >> 8))) >> 8;


        # Assign temp vars based on color cone region
        if region == 0:
            R = V
            G = T
            B = P
        
        elif region == 1:
            R = Q; 
            G = V; 
            B = P;

        elif region == 2:
            R = P; 
            G = V; 
            B = T;

        elif region == 3:
            R = P; 
            G = Q; 
            B = V;

        elif region == 4:
            R = T; 
            G = P; 
            B = V;

        else: 
            R = V; 
            G = P; 
            B = Q;


        return (R, G, B)


    def rainbow_sweep(self):
        step = 1 / NUM_COLS
        hue_offset = 0.0

        leds = [ [0,0,0] for n in range(NUM_LEDS) ]
        while not self.stop:
            hue = fmod(hue_offset, 1.0)
            for col in range(NUM_COLS):
                for row in range(NUM_ROWS):
                    led = self.led_from_row_col(row, col)
                    r,g,b = self.hsv_to_rgb(int(fmod(hue, 1.0) * 255), 255, 255)
                    leds[led] = (r,g,b)
                    self.set_leds(leds)
                    sleep(.01)
                hue += step

                if self.stop:
                    break

            for col in range(NUM_COLS):
                for row in range(NUM_ROWS):
                    led = self.led_from_row_col(row, col)
                    leds[led] = (0,0,0)
                    self.set_leds(leds)
                    sleep(.01)

            hue_offset += .1


    def sleepy_hippos_and_damsels(self):

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
        while not self.stop:
            offset = fmod(shift_offset, 1.0)
            for col in range(NUM_COLS):
                color0 = g.get_color(fmod(col * led_step + offset, 1.0))
                led = self.led_from_row_col(0, col)
                leds[led] = color0
                led = self.led_from_row_col(1, col)
                leds[led] = color0

                color1 = g.get_color(fmod(col * led_step + (1.0 - offset), 1.0))
                led = self.led_from_row_col(3, col)
                leds[led] = color1
                led = self.led_from_row_col(4, col)
                leds[led] = color1

                led = self.led_from_row_col(2, col)
                if col % 2 == 0:
                    leds[led] = color0
                else:
                    leds[led] = color1

                if self.stop:
                    break

            self.set_leds(leds)
            sleep(.05)
            shift_offset += .02


tl = TurkishLamp()
#tl.rainbow_sweep()
tl.sleepy_hippos_and_damsels()

