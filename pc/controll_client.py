import socket
import win32api
import struct
import time
addr = '192.168.1.40'
port = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
'''
w = 前進 0x57
s = 後退 0x53
a = 右 0x41
d = 左 0x44
space = 上昇 0x20
shift = 降下 0x10
e = 右回転 0x45
q = 左回転 0x51
'''
while True:
    w = 0
    s = 0
    a = 0
    d = 0
    space = 0
    shift = 0
    e = 0
    q = 0
    if win32api.GetAsyncKeyState(0x57) < 0:
        w = 1
    if win32api.GetAsyncKeyState(0x53) < 0:
        s = 1
    if win32api.GetAsyncKeyState(0x41) < 0:
        a = 1
    if win32api.GetAsyncKeyState(0x44) < 0:
        d = 1
    if win32api.GetAsyncKeyState(0x20) < 0:
        space = 1
    if win32api.GetAsyncKeyState(0x10) < 0:
        shift = 1
    if win32api.GetAsyncKeyState(0x45) < 0:
        e = 1
    if win32api.GetAsyncKeyState(0x51) < 0:
        q = 1
    #print(f'w:{w},s:{s},a:{a},d:{d},space:{space},shift:{shift},e:{e},q:{q}')
    data = struct.pack("BBBBBBBB",w,s,a,d,space,shift,e,q)
    sock.sendto(data,(addr,port))
    time.sleep(0.01)