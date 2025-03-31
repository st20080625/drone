import socket
import json
from smbus2 import SMBus
import math
import time
import numpy as np
import ball_origin as bo

ip_addr = '192.168.1.41'
port = 5001
motor_ipaddr = '192.168.1.40'
motor_port = 5002

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

motor_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

alpha = 0.98

bus_num = 3
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

# Compass
compass_addr = 0x1E
CRA_REG_M = 0x00
CRB_REG_M = 0x01
MR_REG_M = 0x02
MAGNET_XOUT = 0x03
MAGNET_YOUT = 0x07
MAGNET_ZOUT = 0x05
LSB_compass = 0.000122
LSB_GAUSS_XY = 450
LSB_GAUSS_Z = 400
smbus2.write_byte_data(compass_addr, CRA_REG_M, 0x1C)
smbus2.write_byte_data(compass_addr, CRB_REG_M, 0x80)
smbus2.write_byte_data(compass_addr, MR_REG_M, 0x00)
offset_cx = 0
offset_cy = 0

def read_compass_sensor(addr):
    high = smbus2.read_byte_data(compass_addr, addr)
    low = smbus2.read_byte_data(compass_addr, addr + 1)
    value = (high << 8) | low
    if value >= 32768:
        value -= 65536
    return value

# Gyro offset
def calibrate_gyro():
    print('start_calibration')
    time.sleep(1)
    print("Calibrating gyro...")
    num_samples = 100
    offset_gx, offset_gy, offset_gz = 0.0, 0.0, 0.0
    for _ in range(num_samples):
        data = smbus2.read_i2c_block_data(gyro_addr, gyro_data_start | 0x80, 6)
        gx = (data[1] << 8) | data[0]
        gy = (data[3] << 8) | data[2]
        gz = (data[5] << 8) | data[4]
        if gx > 32767: gx -= 65536
        if gy > 32767: gy -= 65536
        if gz > 32767: gz -= 65536
        offset_gx += gx
        offset_gy += gy
        offset_gz += gz
        time.sleep(0.01)
    offset_gx /= num_samples
    offset_gy /= num_samples
    offset_gz /= num_samples
    print(f"Gyro offsets: gx={offset_gx}, gy={offset_gy}, gz={offset_gz}")
    time.sleep(1)
    return offset_gx * LSB_gyro, offset_gy * LSB_gyro, offset_gz * LSB_gyro

def calibrate_compass():
    LSB = 0.000122
    LSB_GAUSS_XY = 450
    LSB_GAUSS_Z = 400
    print("Calibrating compass...")
    data = [[],[],[]]
    start_time = time.time()
    while time.time() - start_time < 15:
        x = read_compass_sensor(MAGNET_XOUT)
        y = read_compass_sensor(MAGNET_YOUT)
        z = read_compass_sensor(MAGNET_ZOUT)

        x_gauss = (x * LSB) / LSB_GAUSS_XY
        y_gauss = (y * LSB) / LSB_GAUSS_XY
        z_gauss = (z * LSB) / LSB_GAUSS_Z

        data[0].append(x_gauss)
        data[1].append(y_gauss)
        data[2].append(z_gauss)
        print(f'calibrating x{x_gauss},y{y_gauss},z{z_gauss}')
        time.sleep(0.01)
    print('end_calibrating')
    time.sleep(1)
    origin = bo.get_origin(np.array(data[0]),np.array(data[1]),np.array(data[2]))
    x0 = origin[0] 
    y0 = origin[1]
    return x0, y0

def offset_angle_z(offset_cx, offset_cy):
    cx = read_compass_sensor(MAGNET_XOUT)
    cy = read_compass_sensor(MAGNET_YOUT)

    cx_gauss = (cx * LSB_compass) / LSB_GAUSS_XY
    cy_gauss = (cy * LSB_compass) / LSB_GAUSS_XY

    cx_gauss -= offset_cx
    cy_gauss -= offset_cy

    offset_angle_z = np.arctan2(cy_gauss, cx_gauss)*180/np.pi
    return offset_angle_z
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0
current_time = time.time()

offset_gx, offset_gy, offset_gz = calibrate_gyro()
time.sleep(1)
offset_cx, offset_cy = calibrate_compass()
time.sleep(5)
offset_angle_z = offset_angle_z(offset_cx, offset_cy)
while True:
    try:
        # Gyro
        data = smbus2.read_i2c_block_data(gyro_addr, gyro_data_start | 0x80, 6)
        gx = (data[1] << 8) | data[0]
        gy = (data[3] << 8) | data[2]
        gz = (data[5] << 8) | data[4]
        if gx > 32767: gx -= 65536
        if gy > 32767: gy -= 65536
        if gz > 32767: gz -= 65536

        # Offset
        gx = gx * LSB_gyro - offset_gx
        gy = gy * LSB_gyro - offset_gy
        gz = gz * LSB_gyro - offset_gz

        # Accel
        data = smbus2.read_i2c_block_data(accel_addr, accel_data_start | 0x80, 6)
        ax = (data[1] << 8) | data[0]
        ay = (data[3] << 8) | data[2]
        az = (data[5] << 8) | data[4]
        if ax > 32767: ax -= 65536
        if ay > 32767: ay -= 65536
        if az > 32767: az -= 65536

        # Compass
        cx = read_compass_sensor(MAGNET_XOUT)
        cy = read_compass_sensor(MAGNET_YOUT)
        cz = read_compass_sensor(MAGNET_ZOUT)

        cx_gauss = (cx * LSB_compass) / LSB_GAUSS_XY
        cy_gauss = (cy * LSB_compass) / LSB_GAUSS_XY
        cz_gauss = (cz * LSB_compass) / LSB_GAUSS_Z

        cx_gauss -= offset_cx
        cy_gauss -= offset_cy


    except Exception as e:
        print(f"Error reading data: {e}")
        continue

    # Delta t
    new_time = time.time()
    delta_t_r = new_time - current_time

    acc_angle_x = math.atan2(ay, az) * 180 / math.pi
    acc_angle_y = math.atan2(ax, az) * 180 / math.pi

    angle_x = alpha * (angle_x + gx * delta_t_r) + (1 - alpha) * acc_angle_x
    angle_y = alpha * (angle_y + gy * delta_t_r) + (1 - alpha) * acc_angle_y
    angle_z = np.arctan2(cy_gauss, cx_gauss)*180/np.pi
    if angle_z < 0:
        angle_z += 360
    angle_z -= offset_angle_z
    if angle_z < 0:
        angle_z += 360+abs(offset_angle_z)

    send_data = json.dumps({'angle_x': angle_x, 'angle_y': angle_y, 'angle_z': angle_z})
    sock.sendto(send_data.encode(),(ip_addr, port))
    motor_sock.sendto(send_data.encode(),(motor_ipaddr, motor_port))

    #print(f"Angle X: {angle_x:.2f}, Y: {angle_y:.2f}, Z: {angle_z:.2f}")

    current_time = new_time

    time.sleep(0.01)
