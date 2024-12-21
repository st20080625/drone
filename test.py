import pygame
import module_3d as m3
from smbus2 import SMBus
import math
import time

pygame.init()

# Pygame ウィンドウ設定
width = m3.width
height = m3.height
screen = pygame.display.set_mode((width, height))
red = [255, 0, 0]
blue = [0, 0, 255]
green = [0, 255, 0]

# 3D軸定義
axis_x = m3.vec3D(1, 0, 0)
axis_y = m3.vec3D(0, 1, 0)
axis_z = m3.vec3D(0, 0, 1)

# I2C設定
bus_num = 1
smbus2 = SMBus(bus_num)

# ジャイロスコープ設定
gyro_addr = 0x69
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG4 = 0x23
start_data_addr = 0x28
LSB_gyro = 0.0152  # ジャイロスコープスケールファクター（°/sec per LSB）
smbus2.write_byte_data(gyro_addr, CTRL_REG1, 0x8F)  # ジャイロ有効化
smbus2.write_byte_data(gyro_addr, CTRL_REG2, 0x00)
smbus2.write_byte_data(gyro_addr, CTRL_REG4, 0x10)

# 加速度センサー設定
accel_addr = 0x19
accel_data_start = 0x28
CTRL_REG1_A = 0x20
CTRL_REG4_A = 0x23
LSB_accel = 0.000244  # 加速度センサーのスケールファクター (g per LSB)
smbus2.write_byte_data(accel_addr, CTRL_REG1_A, 0x57)
smbus2.write_byte_data(accel_addr, CTRL_REG4_A, 0x20)

# 角度初期化
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0
delta_t = 0.1  # サンプリング時間

# コンプリメンタリフィルタ係数
alpha = 0.98  # ジャイロの信頼性

# メインループ
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ジャイロスコープデータ取得
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

    # ジャイロスコープ角速度変換
    gx *= LSB_gyro
    gy *= LSB_gyro
    gz *= LSB_gyro

    # 加速度センサー重力成分から角度計算
    acc_angle_x = math.atan2(ay, az) * 180 / math.pi
    acc_angle_y = math.atan2(ax, az) * 180 / math.pi

    # コンプリメンタリフィルタ
    angle_x = alpha * (angle_x + gx * delta_t) + (1 - alpha) * acc_angle_x
    angle_y = alpha * (angle_y + gy * delta_t) + (1 - alpha) * acc_angle_y
    angle_z += gz * delta_t  # ジャイロの角速度のみ使用

    # 描画
    screen.fill("gray")
    rotated_x = axis_x.rotate('x', angle_x).rotate('y', angle_y).rotate('z', angle_z)
    rotated_y = axis_y.rotate('x', angle_x).rotate('y', angle_y).rotate('z', angle_z)
    rotated_z = axis_z.rotate('x', angle_x).rotate('y', angle_y).rotate('z', angle_z)

    rotated_x.draw_line(red)
    rotated_y.draw_line(blue)
    rotated_z.draw_line(green)

    pygame.display.flip()
    print(f"Angle X: {angle_x:.2f}, Y: {angle_y:.2f}, Z: {angle_z:.2f}")
    time.sleep(delta_t)

pygame.quit()
