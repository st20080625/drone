import subprocess
import socket
import win32api
addr = '192.168.1.40'
port = 5003
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cam = subprocess.Popen(['python', 'cam_receive.py'])
controller = subprocess.Popen(['python', 'controll_client.py'])
render_3d = subprocess.Popen(['python', 'receive_angle.py'])
running = True
while running:
    if win32api.GetAsyncKeyState(0x47) < 0:
        sock.sendto(b'0',(addr, port))
        running = False
    else:
        pass
cam.terminate()
controller.terminate()
render_3d.terminate()

cam.terminate()
controller.terminate()
render_3d.terminate()