import numpy as np
import pygame
import socket
import json
import copy
import time

ip = '192.168.1.23'
port = 5001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))

esp_ip = '192.168.1.38'
port_esp = 5000
sock_esp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class vec3D:
    def __init__(self, x, y, z, color=None):
        self.base_x = x
        self.base_y = y
        self.base_z = z
        self.reset()
        self.color = color

    def reset(self):
        self.x = self.base_x
        self.y = self.base_y
        self.z = self.base_z

    def rotate(self, w, x, y, z):
        quaternion_matrix_rotation = np.array([
            [w**2 + x**2 - y**2 - z**2, 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), w**2 - x**2 + y**2 - z**2, 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), w**2 - x**2 - y**2 + z**2]
        ])
        
        new_vec = quaternion_matrix_rotation @ np.array([self.x, self.y, self.z])
        self.x, self.y, self.z = new_vec

    def rotate_euler(self, rotate_matrix):
        coords = np.array([self.x, self.y, self.z])
        rotated_coords = rotate_matrix @ coords
        self.x = rotated_coords[0]
        self.y = rotated_coords[1]
        self.z = rotated_coords[2]
    
    def scale_factor(self):
        return 500 / (self.y + 500)

    def draw_line(self, color, vec):
        scale_factor = self.scale_factor()
        if vec is not None:
            pygame.draw.line(screen, color, (vec.x*150+width/2, -vec.z*150+height/2),
            ((self.x * 150 + width/2) * scale_factor, -self.z * 150 + height/2 * scale_factor), width=5)
        else:    
            pygame.draw.line(screen, color, (width/2, height/2),
            ((self.x * 150 + width/2) * scale_factor, -self.z * 150 + height/2 * scale_factor), width=5)

# quaternion multiplication            
def calc_quaternion_mul(q1, q2):
    r = q1[0]*q2[0] - q1[1]*q2[1] - q1[2]*q2[2] - q1[3]*q2[3]
    i = q1[0]*q2[1] + q1[1]*q2[0] + q1[2]*q2[3] - q1[3]*q2[2]
    j = q1[0]*q2[2] - q1[1]*q2[3] + q1[2]*q2[0] + q1[3]*q2[1]
    k = q1[0]*q2[3] + q1[1]*q2[2] - q1[2]*q2[1] + q1[3]*q2[0]
    return r, i, j, k

# calculate target quaternion
#q1 = q' = target_quaternion see from global coordinate
#q2 = q = axis quaternion
def calc_target_quaternion(q1, q2):
    q3 = [q2[0], -1*q2[1], -1*q2[2], -1*q2[3]]
    
    q3q1 = calc_quaternion_mul(q3, q1)
    calc_goal_quaternion = calc_quaternion_mul(q3q1, q2)
    r, i, j, k = calc_goal_quaternion[0], calc_goal_quaternion[1], calc_goal_quaternion[2], calc_goal_quaternion[3]
    return r, i, j, k

def rotate(w, x, y, z):
    quaternion_matrix_rotation = np.array([
        [w**2 + x**2 - y**2 - z**2, 2*(x*y - w*z), 2*(x*z + w*y)],
        [2*(x*y + w*z), w**2 - x**2 + y**2 - z**2, 2*(y*z - w*x)],
        [2*(x*z - w*y), 2*(y*z + w*x), w**2 - x**2 - y**2 + z**2]
        ])
    return quaternion_matrix_rotation

def normalize_quaternion(q):
    norm = np.sqrt(q[0]**2 + q[1]**2 + q[2]**2 + q[3]**2)
    return q[0]/norm, q[1]/norm, q[2]/norm, q[3]/norm

def euler2quaternion(roll, pitch, yaw):
    cy = np.cos(yaw / 2)
    sy = np.sin(yaw / 2)
    cp = np.cos(pitch / 2)
    sp = np.sin(pitch / 2)
    cr = np.cos(roll / 2)
    sr = np.sin(roll / 2)

    r = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return r, x, y, z

def quaternion2euler(r, x, y, z):
    # Normalize the quaternion
    r, x, y, z = normalize_quaternion((r, x, y, z))
    
    # Compute Euler angles (ZYX order)
    yaw = np.arctan2(2 * (r * z + x * y), 1 - 2 * (y**2 + z**2))
    pitch = np.arcsin(2 * (r * y - z * x))
    roll = np.arctan2(2 * (r * x + y * z), 1 - 2 * (x**2 + y**2))
    
    return roll, pitch, yaw

def rotate_euler(roll, pitch, yaw):
    rotate_matrix = np.array([
        [np.cos(pitch)*np.cos(yaw), np.sin(roll)*np.sin(pitch)*np.cos(yaw)-np.cos(roll)*np.sin(yaw), np.cos(roll)*np.sin(pitch)*np.cos(yaw)+np.sin(roll)*np.sin(yaw)],
        [np.cos(pitch)*np.sin(yaw), np.sin(roll)*np.sin(pitch)*np.sin(yaw)+np.cos(roll)*np.cos(yaw), np.cos(roll)*np.sin(pitch)*np.sin(yaw)-np.sin(roll)*np.cos(yaw)],
        [-np.sin(pitch), np.sin(roll)*np.cos(pitch), np.cos(roll)*np.cos(pitch)]
    ])
    return rotate_matrix

def sort_small_y(vec_list):
    vec_list.sort(key=lambda x: x.y, reverse=True)
    return vec_list

pygame.font.init()
font = pygame.font.Font(None, 36)

def draw_text(text, pos, color):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)

pygame.init()
width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
pygame.joystick.init()
try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("joystick_name:", joystick.get_name())
    print("button_count:", joystick.get_numbuttons())
except pygame.error:
    print("joystick hasn't connected")
# colors
red, blue, green, gray, white, black = [255, 0, 0], [0, 0, 255], [0, 255, 0], [128, 128, 128],[0,0,0], [255, 255, 255]

# axis_vectors
axis_x = vec3D(0.4, 0, 0)
axis_y = vec3D(0, 0.4, 0)
axis_z = vec3D(0, 0, 0.4)

# explain_axis_vectors
explain_axis_x_right = vec3D(1.5, 2, 0)
explain_axis_x_left = vec3D(0.5, 2, 0)
explain_axis_y_front = vec3D(0.5, 0, 0)
explain_axis_y_back = vec3D(0.5, 1, 0)
explain_axis_z_up = vec3D(0.5, 2, 1)
explain_axis_z_down = vec3D(0.5, 2, 0)

# line_vectors
line_pos1 = vec3D(0.23, 0.53, 0.25)
line_pos2 = vec3D(-0.53, -0.23, 0.25)
line_pos3 = vec3D(0.53, 0.23, 0.25)
line_pos4 = vec3D(-0.23, -0.53, 0.25)

line_pos5 = copy.deepcopy(vec3D(-1*line_pos1.x, line_pos1.y, line_pos1.z))
line_pos6 = copy.deepcopy(vec3D(-1*line_pos2.x, line_pos2.y, line_pos2.z))
line_pos7 = copy.deepcopy(vec3D(-1*line_pos3.x, line_pos3.y, line_pos3.z))
line_pos8 = copy.deepcopy(vec3D(-1*line_pos4.x, line_pos4.y, line_pos4.z))

line_pos_list_up = [line_pos1, line_pos2, line_pos3, line_pos4, line_pos5, line_pos6, line_pos7, line_pos8]
line_pos_list_down = [vec3D(pos.base_x, pos.base_y, pos.base_z*-1) for pos in line_pos_list_up]
for pos in line_pos_list_down:
    pos.z = pos.z*-1

# circle_vectors  
radius = 0.5
center_x, center_y = 0.7, 0.7
x_values = np.linspace(0.2, 1.2, 100)

vectors1 = []
for x in x_values:
    term = radius**2 - (x - center_x)**2
    if term >= 0:
        y1 = center_y + np.sqrt(term)
        y2 = center_y - np.sqrt(term)
        vectors1.append(vec3D(x, y1, 0.25))
        vectors1.append(vec3D(x, y2, 0.25))
vectors2 = []
for n in vectors1:
    vectors2.append(vec3D(n.x-1.4, n.y, n.z))
vectors3 = []
for n in vectors1:
    vectors3.append(vec3D(n.x-1.4, n.y-1.4, n.z))
vectors4 = []
for n in vectors1:
    vectors4.append(vec3D(n.x, n.y-1.4, n.z))

vectors_up = []
for vec_list in [vectors1, vectors2, vectors3, vectors4]:
    vectors_up.extend(vec_list)

vectors_down = []
for n in vectors_up:
    vectors_down.append(vec3D(n.x, n.y, -n.z))

color_flag = False
  
for vec in vectors_up:
    if vec == vectors_up[400]:
        color_flag = True
    if color_flag:
        vec.color = black
    else:
        vec.color = red        

color_flag = False
for vec in vectors_down:
    if vec == vectors_down[400]:
        color_flag = True
    if color_flag:
        vec.color = black
    else:
        vec.color = red

# スムージング用の補間関数
def smooth_transition(current, target, rate=0.1):
    """
    current: 現在の値
    target: 目標値
    rate: 補間率（0.0～1.0、値が小さいほど変化がゆっくり）
    """
    return current + (target - current) * rate

# スピードの現在値を保持
current_speed = 0  # 初期値を32に設定

running = True
clock = pygame.time.Clock()

motor_speed = 0
target_roll, target_pitch, target_yaw = 0, 0, 0
yaw = 0
while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if joystick:
        gamepad_data = [
            # rx
            (joystick.get_axis(3)),
            # ry
            (joystick.get_axis(4)),
            # lx
            (joystick.get_axis(0)),
            # ly
            (joystick.get_axis(1)),
            # stop
            joystick.get_button(1),
            # offset
            joystick.get_button(2),
        ]
        for n in range(4):
            if -0.02 < gamepad_data[n] < 0.02:
                gamepad_data[n] = 0
        stop = gamepad_data[4]
        offset = gamepad_data[5]

    target_speed = -gamepad_data[3] * 100

    if gamepad_data[4] == 1:
        target_speed = 0
    if target_speed < 0:
        target_speed = 0

    # スピードをなめらかに補間
    #current_speed = smooth_transition(current_speed, target_speed, rate=0.1)

    # スティック入力を送信
    target_roll = gamepad_data[1] * 25
    target_pitch = gamepad_data[0] * 25
    target_yaw = yaw * 180/np.pi + -gamepad_data[2] * 10

    gamepads = {
        'speed': target_speed,  # スムージング後のスピードを送信
        'target_roll': target_roll,
        'target_pitch': target_pitch,
        'target_yaw': target_yaw
    }
    data = json.dumps(gamepads).encode('utf-8')
    sock_esp.sendto(data, (esp_ip, port_esp))

    # ドローンからクォータニオンを受信
    try:
        data, addr = sock.recvfrom(1024)
        data = json.loads(data.decode())
        r, i, j, k = data['r'], data['i'], data['j'], data['k']
    except socket.timeout:
        continue

    # クォータニオンをオイラー角に変換
    roll, pitch, yaw = quaternion2euler(r, i, j, k)

    rotate_matrix = rotate_euler(target_roll * np.pi / 180, target_pitch * np.pi / 180, yaw)
    screen.fill(gray)

    for pos in line_pos_list_up:
        pos.reset()
        pos.rotate_euler(rotate_matrix)

    for pos in line_pos_list_down:
        pos.reset()
        pos.rotate_euler(rotate_matrix)

    for vec in vectors_up:
        vec.reset()
        vec.rotate_euler(rotate_matrix)

    for vec in vectors_down:
        vec.reset()
        vec.rotate_euler(rotate_matrix)

    axis_x.reset()
    axis_y.reset()
    axis_z.reset()

    axis_x.rotate_euler(rotate_matrix)
    axis_y.rotate_euler(rotate_matrix)
    axis_z.rotate_euler(rotate_matrix)

    # 描画処理
    vectors_up = sort_small_y(vectors_up)
    vectors_down = sort_small_y(vectors_down)

    line_pos_list_up[0].draw_line(white, line_pos_list_up[1])
    line_pos_list_up[2].draw_line(white, line_pos_list_up[3])
    line_pos_list_up[4].draw_line(white, line_pos_list_up[5])
    line_pos_list_up[6].draw_line(white, line_pos_list_up[7])

    line_pos_list_down[0].draw_line(white, line_pos_list_down[1])
    line_pos_list_down[2].draw_line(white, line_pos_list_down[3])
    line_pos_list_down[4].draw_line(white, line_pos_list_down[5])
    line_pos_list_down[6].draw_line(white, line_pos_list_down[7])

    circle_vectors = []
    circle_vectors.extend(vectors_up)
    circle_vectors.extend(vectors_down)
    circle_vectors = sort_small_y(circle_vectors)
    for vec in circle_vectors:
        pygame.draw.circle(screen, vec.color, (int(vec.x * 150 + width / 2), int(-vec.z * 150 + height / 2)), 3)

    for vec in vectors_up:
        vec.draw_line(vec.color, vectors_down[vectors_up.index(vec)])

    axis_x.draw_line(red, None)
    axis_y.draw_line(green, None)
    axis_z.draw_line(blue, None)

    # 軸の説明を描画
    pygame.draw.line(screen, red, (1000, 500), (1200, 500), width=5)
    pygame.draw.line(screen, green, (1000, 500), (940, 440), width=5)
    pygame.draw.line(screen, blue, (1000, 500), (1000, 300), width=5)

    draw_text("X", (1210, 490), red)
    draw_text("Y", (920, 420), green)
    draw_text("Z", (1010, 280), blue)
    draw_text("Current_EulerAngles", (width / 2, 550), white)
    draw_text("Target_Angles", (width / 2, 640), white)

    draw_text(str(np.floor(roll * 180 / np.pi)), (width / 2, 600), white)
    draw_text(str(np.floor(pitch * 180 / np.pi)), (width / 2 + 100, 600), white)
    draw_text(str(np.floor(yaw * 180 / np.pi)), (width / 2 + 200, 600), white)
    
    draw_text(str(np.floor(target_roll)), (width / 2, 690), white)
    draw_text(str(np.floor(target_pitch)), (width / 2 + 100, 690), white)
    draw_text(str(np.floor(target_yaw)), (width / 2 + 200, 690), white)
    
    draw_text(str(motor_speed*100), (width / 2 + 300, 540), white)

    pygame.display.flip()
    clock.tick(240)

pygame.quit()