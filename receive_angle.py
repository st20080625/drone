import socket, json
import module_3d as m3
import pygame
ip_addr = '192.168.1.41'
port = 5001
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind((ip_addr,port))

pygame.init()

width = m3.width
height = m3.height
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
origin = m3.vec3D(-1, -1, -1)
axis_x = m3.vec3D(1, -1, -1)
axis_y = m3.vec3D(-1, 1, -1)
axis_z = m3.vec3D(-1, -1, 1)
v1 = m3.vec3D(1,1,-1)
v2 = m3.vec3D(1,-1,1)
v3 = m3.vec3D(-1,1,1)
v4 = m3.vec3D(1,1,1)
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    data, addr = sock.recvfrom(1024)
    try:
        decoded_data = json.loads(data.decode())
        angle_x = decoded_data['angle_x']
        angle_y = decoded_data['angle_y']
        angle_z = decoded_data['angle_z']
    except socket.timeout:
        pass
    screen.fill("gray")
    angle_y *= -1
    rotated_origin = origin.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_x = axis_x.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_y = axis_y.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_z = axis_z.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_v1 = v1.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_v2 = v2.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_v3 = v3.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_v4 = v4.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)



    rotated_x.draw_line(rotated_origin,'red')
    rotated_y.draw_line(rotated_origin,'blue')
    rotated_z.draw_line(rotated_origin,'green')
    rotated_y.draw_line(rotated_v1,'orange')
    rotated_x.draw_line(rotated_v1,'orange')
    rotated_x.draw_line(rotated_v2,'orange')
    rotated_v3.draw_line(rotated_v4,'orange')
    rotated_z.draw_line(rotated_v3,'orange')
    rotated_v1.draw_line(rotated_v4,'orange')
    rotated_v2.draw_line(rotated_v4,'orange')
    rotated_x.draw_line(rotated_v1,'orange')
    rotated_z.draw_line(rotated_v2,'orange')
    rotated_y.draw_line(rotated_v3,'orange')

    pygame.display.flip()
    clock.tick(240)
pygame.quit()