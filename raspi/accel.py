from smbus2 import SMBus
import time
'''
2^16 = 65536
65536/2 = 32768
+,- = 32768,-32767
16bit max,min = 32768,-32767
8(g) setting
1LSB(g) = 8g/32768 = 0.00024414062(g)
input = 10000pyth
g = input * 1LSB
  = 2.4414062(g)
'''
bus_num = 3
smbus2 = SMBus(bus_num)
accel_addr = 0x19
accel_data_start = 0x28
CTRL_REG1_A = 0x20
CTRL_REG4_A = 0x23
smbus2.write_byte_data(accel_addr, CTRL_REG1_A, 0x57)
#0b00100000
smbus2.write_byte_data(accel_addr, CTRL_REG4_A, 0x20)
scale_factor = 0.000244
while True:
    data = smbus2.read_i2c_block_data(accel_addr, accel_data_start | 0x80, 6)
    x = (data[1] << 8) | data[0]
    y = (data[3] << 8) | data[2]
    z = (data[5] << 8) | data[4]
    
    if x > 32767:
        x -= 65536
    if y > 32767:
        y -= 65536
    if z > 32767:
        z -= 65536
    x_g = -x * scale_factor 
    y_g = -y * scale_factor
    z_g = z * scale_factor

    print(f"X: {x_g:.3f}g, Y: {y_g:.3f}g, Z: {z_g:.3f}g")
    time.sleep(0.1)