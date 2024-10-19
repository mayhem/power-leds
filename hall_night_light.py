from math import pi, sin, cos
from machine import Pin, PWM
from time import sleep, time
import ubinascii
from umqtt.simple import MQTTClient
#from machine import WDT


MQTT_SERVER = "10.1.1.2"
MQTT_PORT = 1883

MAX_BRIGHTNESS_LED0 = 512 

led0 = Pin(1, Pin.OUT)
pwm_led0 = PWM(led0)
pwm_led0.freq(5000)
pwm_led0.duty(0)

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

def callback(topic, msg):
    global pwm_led0

    print(topic, msg)
    try:
        b = int(msg)
    except ValueError:
        return

    if b < 0 or b > 100:
        return

    b = int(MAX_BRIGHTNESS_LED0 * b / 100)
    pwm_led0.duty(b)

def main():
    c = MQTTClient(CLIENT_ID, MQTT_SERVER, MQTT_PORT)
    c.set_callback(callback)
    c.connect()
    c.subscribe("blacklight-art/set")
    print("Connected, subscribed, yo")

#    wdt = WDT()

    next_ping_time = time() + 500

    try:
        while 1:
            c.check_msg()

            if time() > next_ping_time:
                next_ping_time = time() + 500
                c.ping()

#            wdt.feed()

    finally:
        c.disconnect()

main()
