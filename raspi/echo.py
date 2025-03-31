import gpiozero
from gpiozero.pins.pigpio import PiGPIOFactory
import time
factory = PiGPIOFactory()
sensor = gpiozero.DistanceSensor(echo=22, trigger=17, pin_factory=factory)
def museruDist():
    global sensor
    while True:
        distance = sensor.distance * 100
        print(f'{distance}cm')
        time.sleep(0.1)
museruDist()