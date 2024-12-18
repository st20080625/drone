from gpiozero import PWMOutputDevice
from time import sleep
import threading
pin = 12
pin2 = 13
pin3 = 18
pin4 = 19
#PWM周波数が500ならなんかうまく動く
esc = PWMOutputDevice(pin=pin,frequency=500)
esc2 = PWMOutputDevice(pin=pin2,frequency=500)
esc3 = PWMOutputDevice(pin=pin3,frequency=500)
esc4 = PWMOutputDevice(pin=pin4,frequency=500)
def run(esc):
    esc.value = 0.9
    print(esc.value)
    sleep(1)
    esc.value = 0.9
    print(esc.value)
    sleep(2)
    esc.value = 0.5
    print(esc.value)
    sleep(1)
    esc.value = 0.6
    print(esc.value)
    sleep(2)
    esc.value = 0.7
    print(esc.value)
    sleep(2)
    esc.value = 0.8 
    print(esc.value)
    sleep(3)
thread1 = threading.Thread(target=run,args=(esc,))
thread2 = threading.Thread(target=run,args=(esc2,))
thread3 = threading.Thread(target=run,args=(esc3,))
thread4 = threading.Thread(target=run,args=(esc4,))
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread1.join()
thread2.join()
thread3.join()
thread4.join()