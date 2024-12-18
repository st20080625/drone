import math
from smbus2 import SMBus
import time

bus_num = 1
compass_addr = 0x1E
compass_start_data = 0x03
MR_REG_M = 0x02
CRB_REG_M = 0x01

'''
+-4 gauss
16bit
4/32768 = 1LSB = 0.0001220703125
LSB/gauss = 450 (x,y)
gauss = LSB/(LSB/gauss)
'''
LSB = 0.000122
LSB_GAUSS_XY = 450 

smbus2 = SMBus(bus_num)
smbus2.write_byte_data(compass_addr, MR_REG_M, 0x00) # Wake up
smbus2.write_byte_data(compass_addr, CRB_REG_M, 0x80)
while True:
    data = smbus2.read_i2c_block_data(compass_addr, compass_start_data | 0x80, 6)

    x = (data[0] | (data[1] << 8))
    y = (data[2] | (data[3] << 8))
    if x >= 32768: x -= 65536
    if y >= 32768: y -= 65536

    x_gauss = (x * LSB) / LSB_GAUSS_XY
    y_gauss = (y * LSB) / LSB_GAUSS_XY

    angle = math.atan2(y_gauss,x_gauss) * (180/math.pi)
    if angle < 0:
        angle += 360
    print(angle)
    time.sleep(0.1)