from smbus2 import SMBus
import time
import ball_origin as bo
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
bus_num = 3
compass_addr = 0x1E
CRA_REG_M = 0x00
CRB_REG_M = 0x01
MR_REG_M = 0x02
MAGNET_XOUT = 0x03
MAGNET_YOUT = 0x07
MAGNET_ZOUT = 0x05
LSB = 0.000122
LSB_GAUSS_XY = 450
LSB_GAUSS_Z = 400

bus = SMBus(bus_num)
bus.write_byte_data(compass_addr, CRA_REG_M, 0x1C)
bus.write_byte_data(compass_addr, CRB_REG_M, 0x80)
bus.write_byte_data(compass_addr, MR_REG_M, 0x00)

def read_word_sensor(addr):
    high = bus.read_byte_data(compass_addr, addr)
    low = bus.read_byte_data(compass_addr, addr + 1)
    value = (high << 8) | low
    if value >= 32768:
        value -= 65536
    return value
data = [[],[],[]]
start_time = time.time()
while time.time() - start_time < 15:
    x = read_word_sensor(MAGNET_XOUT)
    y = read_word_sensor(MAGNET_YOUT)
    z = read_word_sensor(MAGNET_ZOUT)

    x_gauss = (x * LSB) / LSB_GAUSS_XY
    y_gauss = (y * LSB) / LSB_GAUSS_XY
    z_gauss = (z * LSB) / LSB_GAUSS_Z

    data[0].append(x_gauss)
    data[1].append(y_gauss)
    data[2].append(z_gauss)
    print(f'calibrating x{x_gauss},y{y_gauss},z{z_gauss}')
    time.sleep(0.01)
print('end_calibrating')
origin = bo.get_origin(np.array(data[0]),np.array(data[1]),np.array(data[2]))
x0 = origin[0]
y0 = origin[1]
z0 = origin[2]
'''
figure = plt.figure()
ax = figure.add_subplot(111, projection='3d')
ax.plot(data[0], data[1], data[2])
ax.scatter(x0, y0, z0, c='r', marker='o')
print(origin)
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
plt.show()'''
offset_x = origin[0]
offset_y = origin[1]
offset_flag = True
offset_angle_z = 0
while True:
    x = read_word_sensor(MAGNET_XOUT)
    y = read_word_sensor(MAGNET_YOUT)
    z = read_word_sensor(MAGNET_ZOUT)

    x_gauss = (x * LSB) / LSB_GAUSS_XY
    y_gauss = (y * LSB) / LSB_GAUSS_XY
    z_gauss = (z * LSB) / LSB_GAUSS_Z

    x_gauss -= offset_x
    y_gauss -= offset_y
    
    angle_z = np.arctan2(y_gauss, x_gauss)*180/np.pi
    angle_z -= offset_angle_z
    if angle_z < 0:
        angle_z += 360
    print(f'angle_z:{angle_z}')
    if offset_flag:
        offset_angle_z = angle_z
        offset_flag = False
    time.sleep(0.01)