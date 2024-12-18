from gpiozero import PWMOutputDevice
from time import sleep
import threading
pin = 12
pin2 = 13
pin3 = 18
pin4 = 19
#なんかよくわからんけど500なら動く　これでESCの初期化完了
esc = PWMOutputDevice(pin=pin,frequency=500)
esc2 = PWMOutputDevice(pin=pin2,frequency=500)
esc3 = PWMOutputDevice(pin=pin3,frequency=500)
esc4 = PWMOutputDevice(pin=pin4,frequency=500)
def init_esc(esc):
    esc.value = 0.9
    print(esc.value)
    sleep(1)
    esc.value = 0.9
    print(esc.value)
    sleep(4)
    esc.value = 0.1
    print(esc.value)
    sleep(10)
    esc.value = 0.9
    print(esc.value)
    sleep(5)
    esc.value = 0.7 
    print(esc.value)
    sleep(5)
    esc.value = 0
    print(esc.value)
thread1 = threading.Thread(target=init_esc, args=(esc,))
thread2 = threading.Thread(target=init_esc, args=(esc2,))
thread3 = threading.Thread(target=init_esc, args=(esc3,))
thread4 = threading.Thread(target=init_esc, args=(esc4,))
thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread1.join()
thread2.join()
thread3.join()
thread4.join()