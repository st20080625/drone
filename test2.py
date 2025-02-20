import socket
import json
from smbus2 import SMBus
import math
import time

ip_addr = '192.168.1.41'
port = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((ip_addr, port))

alpha = 0.98

bus_num = 1
smbus2 = SMBus(bus_num)

# Gyro
gyro_addr = 0x69
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG4 = 0x23
gyro_data_start = 0x28
LSB_gyro = 0.0175
smbus2.write_byte_data(gyro_addr, CTRL_REG1, 0x8F)
smbus2.write_byte_data(gyro_addr, CTRL_REG2, 0x00)
smbus2.write_byte_data(gyro_addr, CTRL_REG4, 0x10)

# Accel
accel_addr = 0x19
accel_data_start = 0x28
CTRL_REG1_A = 0x20
CTRL_REG4_A = 0x23
LSB_accel = 0.000244
smbus2.write_byte_data(accel_addr, CTRL_REG1_A, 0x57)
smbus2.write_byte_data(accel_addr, CTRL_REG4_A, 0x20)

'''# Compass
compass_addr = 0x1E
REG_CONFIG_A = 0x00
REG_MODE = 0x02
MAGNET_XOUT = 0x03
MAGNET_YOUT = 0x07
MAGNET_ZOUT = 0x05
LSB_compass = 0.000122
LSB_GAUSS_XY = 450
LSB_GAUSS_Z = 400
smbus2.write_byte_data(compass_addr, REG_CONFIG_A, 0xE0)
smbus2.write_byte_data(compass_addr, REG_MODE, 0x00)'''

'''def read_sensor(addr):
    high = smbus2.read_byte_data(compass_addr, addr)
    low = smbus2.read_byte_data(compass_addr, addr + 1)
    value = (high << 8) | low
    if value >= 32768:
        value -= 65536
    return value'''

angle_x, angle_y, angle_z = 0.0, 0.0, 0.0
current_time = time.time()

while True:
    try:
        # Data of gyro
        data = smbus2.read_i2c_block_data(gyro_addr, gyro_data_start | 0x80, 6)
        gx = (data[1] << 8) | data[0]
        gy = (data[3] << 8) | data[2]
        gz = (data[5] << 8) | data[4]
        if gx > 32767: gx -= 65536
        if gy > 32767: gy -= 65536
        if gz > 32767: gz -= 65536

        # Data of accel
        data = smbus2.read_i2c_block_data(accel_addr, accel_data_start | 0x80, 6)
        ax = (data[1] << 8) | data[0]
        ay = (data[3] << 8) | data[2]
        az = (data[5] << 8) | data[4]
        if ax > 32767: ax -= 65536
        if ay > 32767: ay -= 65536
        if az > 32767: az -= 65536

        '''# Data of compass
        cx = read_sensor(MAGNET_XOUT)
        cy = read_sensor(MAGNET_YOUT)
        cz = read_sensor(MAGNET_ZOUT)
        
        x_gauss = (cx * LSB_compass) / LSB_GAUSS_XY
        y_gauss = (cy * LSB_compass) / LSB_GAUSS_XY
        z_gauss = (cz * LSB_compass) / LSB_GAUSS_Z'''
        
    except Exception as e:
        print(f"Error reading data: {e}")
        continue

    # Gyro to degree
    gx *= LSB_gyro
    gy *= LSB_gyro
    gz *= LSB_gyro

    new_time = time.time()
    delta_t_r = new_time - current_time

    acc_angle_x = math.atan2(ay, az) * 180 / math.pi
    acc_angle_y = math.atan2(ax, az) * 180 / math.pi

    angle_x = alpha * (angle_x + gx * delta_t_r) + (1 - alpha) * acc_angle_x
    angle_y = alpha * (angle_y + gy * delta_t_r) + (1 - alpha) * acc_angle_y
    angle_z += gz * delta_t_r

    send_data = json.dumps({'angle_x': angle_x, 'angle_y': angle_y, 'angle_z': angle_z})
    sock.sendto((ip_addr, port),send_data.encode())

    print(f"Angle X: {angle_x:.2f}, Y: {angle_y:.2f}, Z: {angle_z:.2f}")

    current_time = new_time

    time.sleep(0.01)