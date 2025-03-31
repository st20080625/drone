import time
import board
import busio
from adafruit_bno08x import BNO_REPORT_MAGNETOMETER
from adafruit_bno08x.i2c import BNO08X_I2C
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import ball_origin as bo

# I2Cバスの初期化
i2c = busio.I2C(3, 2, frequency=400000)
bno = BNO08X_I2C(i2c, address=0x4B)

# 磁力計データのみ有効化
bno.enable_feature(BNO_REPORT_MAGNETOMETER)
data = [[],[],[]]
start_time = time.time()
while time.time()-start_time < 15:
    # 地磁気データ取得
    mag_x, mag_y, mag_z = bno.magnetic  # pylint:disable=no-member
    print("Magnetometer (uT): X: {:.6f}  Y: {:.6f}  Z: {:.6f}".format(mag_x, mag_y, mag_z))
    data[0].append(mag_x)
    data[1].append(mag_y)
    data[2].append(mag_z)
origin = bo.get_origin(np.array(data[0]),np.array(data[1]),np.array(data[2]))
x0 = origin[0]
y0 = origin[1]
z0 = origin[2]

figure = plt.figure()
ax = figure.add_subplot(111, projection='3d')
ax.plot(data[0],data[1],data[2])
ax.scatter(x0, y0, z0, c='r', marker='o')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
plt.show()
