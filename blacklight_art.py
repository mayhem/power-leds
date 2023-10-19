from math import pi, sin, cos
from machine import Pin, PWM
from time import sleep
import ubinascii
from umqtt.simple import MQTTClient

MQTT_SERVER = "10.1.1.2"
MQTT_PORT = 1883

MAX_BRIGHTNESS_LED0 = 1023 
MAX_BRIGHTNESS_LED1 = 100

# Blacklight LED
led0 = Pin(14, Pin.OUT)
pwm_led0 = PWM(led0)
pwm_led0.freq(1000)

# pink LED
led1 = Pin(12, Pin.OUT)
pwm_led1 = PWM(led1)
pwm_led1.freq(1000)

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

state = False
steps = 1500
index = 0
inc = 0.0

def loop(pwm_led0, pwm_led1):
    global state, index, inc

    if not state:
        return

    v0 = sin(index * inc) / 2.0 + .5
    v1 = cos(index * inc) / 2.0 + .5
    pwm_led0.duty(int(v0 * MAX_BRIGHTNESS_LED0))
    pwm_led1.duty(int(v1 * MAX_BRIGHTNESS_LED1))

    sleep(.01)

    index += 1
    if index == steps:
        index = 0


def callback(topic, msg):
    global state, index, inc
        
    try:
        b = int(msg)
    except ValueError:
        return

    if b < 0 or b > 100:
        return

    if b > 0:
        state = True
        inc = pi * 2 / steps
        index = 0
    else:
        state = False
        pwm_led0.duty(0)
        pwm_led1.duty(0)

def main():
    c = MQTTClient(CLIENT_ID, MQTT_SERVER, MQTT_PORT)
    c.set_callback(callback)
    c.connect()
    c.subscribe("blacklight-art/set")
    print("Connected, subscribed")

    try:
        while 1:
            c.check_msg()
            loop(pwm_led0, pwm_led1)
    finally:
        c.disconnect()

pwm_led0.duty(0)
pwm_led1.duty(0)
main()
