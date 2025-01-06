from picamera2 import Picamera2
import socket
import cv2

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.1.41', 5000))

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888","size": (640, 480)})
picam2.configure(config)
picam2.set_controls({"FrameDurationLimits":(16666, 16666)})
picam2.start()

try:
    while True:
        frame = picam2.capture_array()
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

        length = len(buffer)
        sock.sendall(length.to_bytes(4, 'big') + buffer.tobytes())
finally:
    picam2.stop()
    sock.close()