import time
import board
import busio
from adafruit_bno08x import BNO_REPORT_GYROSCOPE
from adafruit_bno08x.i2c import BNO08X_I2C

# I2Cバスの初期化
i2c = busio.I2C(3, 2, frequency=400000)
bno = BNO08X_I2C(i2c, address=0x4B)

# ジャイロデータのみ有効化
bno.enable_feature(BNO_REPORT_GYROSCOPE)

while True:
    # ジャイロデータ取得
    gyro_x, gyro_y, gyro_z = bno.gyro  # pylint:disable=no-member
    print("Gyro (rad/s): X: {:.6f}  Y: {:.6f}  Z: {:.6f}".format(gyro_x, gyro_y, gyro_z))

