import win32api
import time
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
a = 0
while True:
    if win32api.GetAsyncKeyState(0x20) < 0:
        if a < 10:
            a += 1
        elif a >= 10:
            pass
    if win32api.GetAsyncKeyState(0x10) < 0:
        if a <= -10:
            pass
        if a > -10:
            a -= 1
    print(map_value(a,-10,10,0,100))
    time.sleep(0.5)