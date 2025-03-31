import time
import board
import busio
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
from adafruit_bno08x.i2c import BNO08X_I2C
import socket
import json
import gpiozero

i2c = busio.I2C(3, 2, frequency=400000)
bno = BNO08X_I2C(i2c, address=0x4b)
bno.soft_reset()
bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

ip = '192.168.1.23'
port_q = 5000
sock_q = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

port_e = 5001
sock_e = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
def get_data():
    try:
        print("Rotation Vector Quaternion:")
        quats = bno.quaternion
        print(
            "I: %0.6f  J: %0.6f K: %0.6f  Real: %0.6f" % (quats[0], quats[1], quats[2], quats[3])
        )
        print("")
        data = {'i':quats[0],'j':quats[1],'k':quats[2],'r':quats[3]}
        data = json.dumps(data)
        sock_q.sendto(data.encode(), (ip, port_q))
        sock_e.sendto(data.encode(), (ip, port_e))
    except:
        print("Can't read data")
while True:
    get_data()
    time.sleep(0.01)

