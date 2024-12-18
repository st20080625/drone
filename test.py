import pygame
import module_3d as m3
from smbus2 import SMBus
import time
from threading import Thread, Lock

pygame.init()
width = m3.width
height = m3.height
screen = pygame.display.set_mode((width, height))
red = [255, 0, 0]
blue = [0, 0, 255]
green = [0, 255, 0]
axis_x = m3.vec3D(1, 0, 0)
axis_y = m3.vec3D(0, 1, 0)
axis_z = m3.vec3D(0, 0, 1)
angle_x = -2
angle_y = 10
angle_z = 0

gyro_addr = 0x69
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG4 = 0x23
start_data_addr = 0x28
bus_num = 1
LSB = 0.0152
sensitivity = 0.0175
smbus2 = SMBus(bus_num)

smbus2.write_byte_data(gyro_addr, CTRL_REG1, 0x8F)  # Wakeup and set mode
smbus2.write_byte_data(gyro_addr, CTRL_REG2, 0x00)
smbus2.write_byte_data(gyro_addr, CTRL_REG4, 0x10)

accumulated_angle_x = 0.0
accumulated_angle_y = 0.0
accumulated_angle_z = 0.0

delta_t = 0.1
angle_lock = Lock()  # スレッド間で角度を安全に更新するためのロック

def gyro():
    global accumulated_angle_x
    global accumulated_angle_y
    global accumulated_angle_z
    global delta_t
    global angle_x
    global angle_y
    global angle_z
    while True:
        data = smbus2.read_i2c_block_data(gyro_addr, start_data_addr | 0x80, 6)

        x = (data[0] | (data[1] << 8))
        y = (data[2] | (data[3] << 8))
        z = (data[4] | (data[5] << 8))

        if x >= 32768:
            x -= 65536
        if y >= 32768:
            y -= 65536
        if z >= 32768:
            z -= 65536

        x = x * LSB
        y = y * LSB
        z = z * LSB

        delta_angle_x = x * delta_t
        delta_angle_y = y * delta_t
        delta_angle_z = z * delta_t

        accumulated_angle_x += delta_angle_x
        accumulated_angle_y += delta_angle_y
        accumulated_angle_z += delta_angle_z

        with angle_lock:
            angle_x = accumulated_angle_x
            angle_y = accumulated_angle_y
            angle_z = accumulated_angle_z

        print(f"累積角度: X={accumulated_angle_x:.2f}°, Y={accumulated_angle_y:.2f}°, Z={accumulated_angle_z:.2f}°")

        time.sleep(delta_t)

def draw():
    global angle_x
    global angle_y
    global angle_z
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        current_angle_x = angle_x
        current_angle_y = angle_y
        current_angle_z = angle_z

        screen.fill("gray")
        axis_x.rotate('x', current_angle_x).rotate('y', current_angle_y).rotate('z', current_angle_z).draw_line(red)
        axis_y.rotate('x', current_angle_x).rotate('y', current_angle_y).rotate('z', current_angle_z).draw_line(blue)
        axis_z.rotate('x', current_angle_x).rotate('y', current_angle_y).rotate('z', current_angle_z).draw_line(green)
        pygame.display.flip()
        clock.tick(60)  # fps

    pygame.quit()

gyro_thread = Thread(target=gyro)
draw_thread = Thread(target=draw)
gyro_thread.start()
draw_thread.start()
gyro_thread.join()
draw_thread.join()
