import socket
import numpy as np
import cv2

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('192.168.1.41', 5000))
sock.listen(1)
conn, addr = sock.accept()
print(f"接続を受け付けました: {addr}")

try:
    while True:
        length_data = conn.recv(4)
        if not length_data:
            break
        length = int.from_bytes(length_data, 'big')
        
        frame_data = b''
        while len(frame_data) < length:
            packet = conn.recv(length - len(frame_data))
            if not packet:
                break
            frame_data += packet

        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        
        if frame is not None:
            cv2.imshow('Stream', frame)
            if cv2.waitKey(1) == ord('g'):
                break
finally:
    cv2.destroyAllWindows()
    conn.close()
    sock.close()
