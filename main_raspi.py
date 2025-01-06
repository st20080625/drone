import subprocess
import socket
addr = '192.168.1.40'
port = 5003
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((addr, port))

cam = subprocess.Popen(['python', 'cam.py'])
controller = subprocess.Popen(['python', 'motor.py'])
angle = subprocess.Popen(['python', 'send_angle.py'])
running = True
while running:
    data, addr = sock.recvfrom(1024)
    if data == 0:
        running = False
    else:
        pass
cam.terminate()
controller.terminate()
angle.terminate()