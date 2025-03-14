from machine import Pin
from neopixel import NeoPixel
from time import sleep

def hsv_to_rgb(H, S, V):

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


NUM_LEDS = 144

pin = Pin(1, Pin.OUT)
np = NeoPixel(pin, NUM_LEDS)


while True:

    for hue in range(255):
        rgb = hsv_to_rgb(hue, 255, 255)
        rgb = [ x // 6 for x in rgb ]

        for j in range(NUM_LEDS):
            np[j] = rgb

        np.write()
        sleep(.1)
