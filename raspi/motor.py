from gpiozero import PWMOutputDevice
from time import sleep
import threading
import socket
import json
import struct

controller_ipaddr = '192.168.1.40'
controller_port = 8000
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((controller_ipaddr,controller_port))
angle_ipaddr = '192.168.1.40'
angle_port = 5002
angle_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
angle_sock.bind((angle_ipaddr, angle_port))
'''
w = 前進
s = 後退
a = 右
d = 左
space = 上昇
shift = 降下
e = 右回転
q = 左回転
'''
w, s, a, d, space, shift, e, q = (0, 0, 0, 0, 0, 0, 0, 0)

angle_x, angle_y, angle_z = (0, 0, 0)

pin = 12
pin2 = 13
pin3 = 18
pin4 = 19
#PWM周波数が500ならなんかうまく動く
esc = PWMOutputDevice(pin=pin,frequency=500)
esc1 = PWMOutputDevice(pin=pin2,frequency=500)
esc2 = PWMOutputDevice(pin=pin3,frequency=500)
esc3 = PWMOutputDevice(pin=pin4,frequency=500)
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
def receive_controller():
    global w, s, a, d, space, shift, e, q, sock
    while True:
        data, addr = sock.recvfrom(1024)
        w, s, a, d, space, shift, e, q = struct.unpack("BBBBBBBB",data)
def run(esc):
    global w, s, a, d, space, shift, e, q, angle_x, angle_y, angle_z
    esc.value = 0.65
    #esc.value 0.65~0.99
    esc.value = 0.9
    print(esc.value)
    sleep(1)
    esc.value = 0.9
    print(esc.value)
    sleep(4)
    esc.value = 0.1
    print(esc.value)
    sleep(5)
    while True:
        esc_value_map = map_value(esc.value, 0.65, 0.99, 0, 100)
        #上昇
        if space == 1:
            if esc_value_map < 100:
                esc_value_map += 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        #降下
        if shift == 1:
            if esc_value_map > 0:
                esc_value_map -= 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        #前進
        if w == 1 and (esc is esc or esc is esc3):
            #front_min = 70
            #back_max = 100
            if esc_value_map > 70:
                esc_value_map -= 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        elif w == 1 and (esc is esc1 or esc is esc2):
            if esc_value_map < 100:
                esc_value_map += 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        #後進
        if s == 1 and (esc is esc1 or esc is esc2):
            #front_min = 100
            #back_max = 70
            if esc_value_map > 70:
                esc_value_map -= 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        elif s == 1 and (esc is esc or esc is esc3):
            if esc_value_map < 100:
                esc_value_map += 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        #右移動
        if d == 1 and (esc is esc2 or esc is esc3):
            if esc_value_map > 70:
                esc_value_map -= 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        elif d == 1 and (esc is esc or esc is esc1):
            if esc_value_map < 100:
                esc_value_map += 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        #左移動
        if a == 1 and (esc is esc or esc is esc1):
            if esc_value_map > 70:
                esc_value_map -= 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        elif a == 1 and (esc is esc2 or esc is esc3):
            if esc_value_map < 100:
                esc_value_map += 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        #右回転
        if e == 1 and (esc is esc1 or esc is esc3):
            if esc_value_map > 70:
                esc_value_map -= 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        elif e == 1 and (esc is esc or esc is esc2):
            if esc_value_map < 100:
                esc_value_map += 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        #左回転
        if q == 1 and (esc is esc or esc is esc2):
            if esc_value_map > 70:
                esc_value_map -= 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        elif q == 1 and (esc is esc1 or esc is esc3):
            if esc_value_map < 100:
                esc_value_map += 5
                esc.value = map_value(esc_value_map, 0, 100, 0.65, 0.99)
        print(esc.value)
        sleep(0.01)
def receive_angle():
    global angle_x, angle_y, angle_z
    while True:
        data, addr = angle_sock.recvfrom(1024)
        try:
            decoded_data = json.loads(data.decode())
            angle_x = decoded_data['angle_x']
            angle_y = decoded_data['angle_y']
            angle_z = decoded_data['angle_z']
        except socket.timeout:
            pass

thread1 = threading.Thread(target=run,args=(esc,))
thread2 = threading.Thread(target=run,args=(esc1,))
thread3 = threading.Thread(target=run,args=(esc2,))
thread4 = threading.Thread(target=run,args=(esc3,))
thread5 = threading.Thread(target=receive_controller)
thread6 = threading.Thread(target=receive_angle)

thread1.start()
thread2.start()
thread3.start()
thread4.start()
thread5.start()
thread6.start()

thread1.join()
thread2.join()
thread3.join()
thread4.join()
thread5.join()
thread6.join()