from smbus2 import SMBus
import time
gyro_addr = 0x69
CTRL_REG1 = 0x20
CTRL_REG2 = 0x21
CTRL_REG4 = 0x23
start_data_addr = 0x28
bus_num = 3
LSB = 0.0175
smbus2 = SMBus(bus_num)

smbus2.write_byte_data(gyro_addr, CTRL_REG1, 0x8F)  # Wakeup and set mode
smbus2.write_byte_data(gyro_addr, CTRL_REG2, 0x00)
smbus2.write_byte_data(gyro_addr, CTRL_REG4, 0x10)

accumulated_angle_x = 0.0
accumulated_angle_y = 0.0
accumulated_angle_z = 0.0

delta_t = 0.1

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

    print(f"累積角度: X={accumulated_angle_x:.2f}°, Y={accumulated_angle_y:.2f}°, Z={accumulated_angle_z:.2f}°")
    
    time.sleep(delta_t)
