import pygame
import socket
import json

recv_ip = '192.168.1.23'
recv_port = 5000
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
recv_sock.bind((recv_ip, recv_port))

send_ip = '192.168.1.23'
send_port = 5001
send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:    
    # receive quaternion from drone
    try:
        data, addr = recv_sock.recvfrom(1024)
        data = json.loads(data.decode())
        r, i, j, k = data['r'], data['i'], data['j'], data['k']
    except socket.timeout:
        continue
    data = f'{r},{i},{j},{k}'
    send_sock.sendto(data.encode(), (send_ip, send_port))
