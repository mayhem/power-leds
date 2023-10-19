from machine import Pin, PWM
from time import sleep
import ubinascii
from umqtt.simple import MQTTClient

MQTT_SERVER = "10.1.1.2"
MQTT_PORT = 1883

led = Pin(14, Pin.OUT)
pwm_led = PWM(led)
pwm_led.freq(1000)

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MAX_BRIGHTNESS = 800

def fade_on(pwm_led, target, duration=500):

    inc = target / duration
    for i in range(duration / 10):
        index = ((i + 1) * inc ) * 10
        pwm_led.duty(int(index))
        sleep(.01)
    
    
def fade_off(pwm_led, duration=500):

    current = pwm_led.duty()
    inc = current / duration
    for i in range(duration / 10):
        index = 1023 - (((i + 1) * inc) * 10)
        print(int(index))
        pwm_led.duty(int(index))
        sleep(.01)

def fade_to(pwm_led, target, duration=500):

    steps = duration / 10
    current = pwm_led.duty()
    if current == target:
        return

    diff = target - current
    inc = int(diff / steps)
    if inc == 0:
        pwm_led.duty(target)
        return

    if diff >= 0:
        start = 1
        end = target
    else:
        start = current
        end = target

    for i in range(start, end, inc):
        pwm_led.duty(i)
        sleep(.01)

    pwm_led.duty(target)


def callback(topic, msg):
        
    try:
        b = int(msg)
    except ValueError:
        return

    if b < 0 or b > 100:
        return

    fade_to(pwm_led, int(b * MAX_BRIGHTNESS / 100.0))

def main():
    c = MQTTClient(CLIENT_ID, MQTT_SERVER, MQTT_PORT)
    c.set_callback(callback)
    c.connect()
    c.subscribe("ht-backlight/set")
    print("Connected, subscribed")

    try:
        while 1:
            c.wait_msg()
    finally:
        c.disconnect()

print("start main")
pwm_led.duty(0)
sleep(1)
main()
