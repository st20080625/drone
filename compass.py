import math
from smbus2 import SMBus
import time

bus_num = 1
compass_addr = 0x1E
REG_CONFIG_A = 0x00
REG_MODE = 0x02
MAGNET_XOUT = 0x03
MAGNET_YOUT = 0x07
MAGNET_ZOUT = 0x05
LSB = 0.000122
LSB_GAUSS_XY = 450

bus = SMBus(bus_num)
bus.write_byte_data(compass_addr, REG_CONFIG_A, 0xE0)
bus.write_byte_data(compass_addr, REG_MODE, 0x00)

def read_word_sensor(addr):
    high = bus.read_byte_data(compass_addr, addr)
    low = bus.read_byte_data(compass_addr, addr + 1)
    value = (high << 8) | low
    if value >= 32768:
        value -= 65536
    return value

while True:
    x = read_word_sensor(MAGNET_XOUT)
    y = read_word_sensor(MAGNET_YOUT)
    z = read_word_sensor(MAGNET_ZOUT)

    x_gauss = (x * LSB) / LSB_GAUSS_XY
    y_gauss = (y * LSB) / LSB_GAUSS_XY

    angle = math.atan2(y_gauss, x_gauss) * (180 / math.pi)
    if angle < 0:
        angle += 360

    print(f"X={x:6d}, Y={y:6d}, Z={z:6d}, Angle={angle:.2f}")

    time.sleep(0.1)