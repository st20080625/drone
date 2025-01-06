import subprocess
import socket
addr = '192.168.1.40'
port = 5003
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((addr, port))

cam = subprocess.run(['python', 'cam.py'])
controller = subprocess.run(['python', 'controll.py'])
angle = subprocess.run(['python', 'send_angle.py'])
running = True
while running:
    data, addr = sock.recvfrom(1024)
    if data == 0:
        running = False
    else:
        pass