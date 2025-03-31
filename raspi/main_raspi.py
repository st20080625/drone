import subprocess
import socket
import time
addr = '192.168.1.40'
port = 5003
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((addr, port))

cam = subprocess.Popen(['python', 'cam.py'])
controller = subprocess.Popen(['python', 'motor.py'])
angle = subprocess.Popen(['python', 'send_angle.py'])
running = True
try:
    while running:
        data, addr = sock.recvfrom(1024)
        if data == b'0':
            running = False
        else:
            time.sleep(0.1)
finally:
    cam.terminate()
    controller.terminate()
    angle.terminate()

    cam.wait()
    controller.wait()
    angle.wait()

    sock.close()