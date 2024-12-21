import pygame
import module_3d as m3
from smbus2 import SMBus
import math
import time

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
alpha = 0.98

bus_num = 1
smbus2 = SMBus(bus_num)

gyro_addr = 0x69
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG4 = 0x23
start_data_addr = 0x28
LSB_gyro = 0.0152 
smbus2.write_byte_data(gyro_addr, CTRL_REG1, 0x8F)
smbus2.write_byte_data(gyro_addr, CTRL_REG2, 0x00)
smbus2.write_byte_data(gyro_addr, CTRL_REG4, 0x10)

accel_addr = 0x19
accel_data_start = 0x28
CTRL_REG1_A = 0x20
CTRL_REG4_A = 0x23
LSB_accel = 0.000244
smbus2.write_byte_data(accel_addr, CTRL_REG1_A, 0x57)
smbus2.write_byte_data(accel_addr, CTRL_REG4_A, 0x20)


angle_x, angle_y, angle_z = 0.0, 0.0, 0.0
delta_t = 0.1

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    data = smbus2.read_i2c_block_data(gyro_addr, start_data_addr | 0x80, 6)
    gx = (data[0] | (data[1] << 8)) - (0 if data[1] < 128 else 65536)
    gy = (data[2] | (data[3] << 8)) - (0 if data[3] < 128 else 65536)
    gz = (data[4] | (data[5] << 8)) - (0 if data[5] < 128 else 65536)

    # 加速度センサーデータ取得
    data = smbus2.read_i2c_block_data(accel_addr, accel_data_start | 0x80, 6)
    ax = (data[1] << 8) | data[0]
    ay = (data[3] << 8) | data[2]
    az = (data[5] << 8) | data[4]
    if ax > 32767: ax -= 65536
    if ay > 32767: ay -= 65536
    if az > 32767: az -= 65536

    gx *= LSB_gyro
    gy *= LSB_gyro
    gz *= LSB_gyro

    #angle_x += gx * delta_t
    #angle_y += gy * delta_t
    #angle_z += gz * delta_t

    acc_angle_x = math.atan2(ay, az) * 180 / math.pi
    acc_angle_y = math.atan2(ax, az) * 180 / math.pi

    # コンプリメンタリフィルタ
    angle_x = alpha * (angle_x + gx * delta_t) + (1 - alpha) * acc_angle_x
    angle_y = alpha * (angle_y + gy * delta_t) + (1 - alpha) * acc_angle_y
    angle_z += gz * delta_t

    screen.fill("gray")
    rotated_x = axis_x.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_y = axis_y.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)
    rotated_z = axis_z.rotate('x', angle_x).rotate('y', angle_z).rotate('z', -angle_y)

    rotated_x.draw_line(red)
    rotated_y.draw_line(blue)
    rotated_z.draw_line(green)
    pygame.draw.line(screen, 'yellow', ((rotated_x.x*150+width/2)/(500/(rotated_x.z + 500)),-rotated_x.y*150+height/2),(((rotated_y.x*150+width/2)/(500/(rotated_y.z+500)),-rotated_y.y*150+height/2)), width=2)
    pygame.draw.line(screen, 'yellow', ((rotated_x.x*150+width/2)/(500/(rotated_x.z + 500)),-rotated_x.y*150+height/2),(((rotated_z.x*150+width/2)/(500/(rotated_z.z+500)),-rotated_z.y*150+height/2)), width=2)
    pygame.draw.line(screen, 'yellow', ((rotated_z.x*150+width/2)/(500/(rotated_z.z + 500)),-rotated_z.y*150+height/2),(((rotated_y.x*150+width/2)/(500/(rotated_y.z+500)),-rotated_y.y*150+height/2)), width=2)

    pygame.display.flip()
    print(f"Angle X: {angle_x:.2f}, Y: {angle_y:.2f}, Z: {angle_z:.2f}")
    time.sleep(delta_t)

pygame.quit()
