import socket
import struct
import time

controller_ipaddr = '192.168.1.40'
controller_port = 800

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((controller_ipaddr,controller_port))

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
while True:
    data, addr = sock.recvfrom(1024)
    #w, s, a, d, space, shift, e, q = struct.unpack("BBBBBBBB",data)
    #print(f'w:{w},s:{s},a:{a},d:{d},space:{space},shift:{shift},e:{e},q:{q}')
    time.sleep(0.01)