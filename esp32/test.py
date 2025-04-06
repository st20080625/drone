import pygame
import math
import sys
import random

pygame.init()

# ------------------------------
# 定数・設定
# ------------------------------
WIDTH, HEIGHT = 640, 480
TILE_SIZE = 64
FOV = math.pi / 3  # 視野角
RAY_COUNT = 120    # レイの本数
MAX_DEPTH = 300    # レイの最大距離

# マップデータ（1が壁、0が床）
MAP = [
    [1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,0,0,1,1,1,1,0,0,1],
    [1,0,0,0,0,0,1,0,0,1],
    [1,0,1,1,0,0,0,0,0,1],
    [1,0,0,0,0,1,0,0,0,1],
    [1,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,1],
    [1,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1],
]

MAP_HEIGHT = len(MAP)
MAP_WIDTH = len(MAP[0])

# プレイヤー関連
player_x = 2.5 * TILE_SIZE
player_y = 2.5 * TILE_SIZE
player_angle = 0.0
player_speed = 2.0
rotation_speed = 0.03
player_hp = 100

# 弾関連
bullets = []
bullet_speed = 6
can_shoot = True
shoot_cooldown = 300  # ms
last_shot_time = 0

# 敵関連
enemies = []
enemy_speed = 1.0
ENEMY_SPAWN_COUNT = 5  # スポーンする敵の数
enemy_min_dist = 16    # 当たり判定時に使う距離(プレイヤーや弾との衝突判定)

# Pygameセットアップ
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def init_enemies():
    """ランダムな空きタイルに敵を配置"""
    for _ in range(ENEMY_SPAWN_COUNT):
        while True:
            # ランダムなマップ上の座標を選択
            rand_row = random.randint(1, MAP_HEIGHT - 2)
            rand_col = random.randint(1, MAP_WIDTH - 2)
            if MAP[rand_row][rand_col] == 0:
                ex = rand_col * TILE_SIZE + TILE_SIZE // 2
                ey = rand_row * TILE_SIZE + TILE_SIZE // 2
                enemies.append([ex, ey, 100])  # [x位置, y位置, HP]
                break

def cast_rays(px, py, angle):
    """レイキャスティングによる3D描画"""
    half_fov = FOV / 2
    start_angle = angle - half_fov
    step_angle = FOV / RAY_COUNT
    wall_strips = []

    for ray_index in range(RAY_COUNT):
        ray_angle = start_angle + ray_index * step_angle
        depth = 0
        hit_wall = False

        while depth < MAX_DEPTH and not hit_wall:
            depth += 1
            test_x = int(px + math.cos(ray_angle) * depth)
            test_y = int(py + math.sin(ray_angle) * depth)
            map_x = test_x // TILE_SIZE
            map_y = test_y // TILE_SIZE

            if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
                hit_wall = True
                depth = MAX_DEPTH
            else:
                if MAP[map_y][map_x] == 1:
                    hit_wall = True

        dist_to_wall = depth * math.cos(angle - ray_angle)
        wall_height = 0
        if dist_to_wall != 0:
            wall_height = min(int(TILE_SIZE * 300 / (dist_to_wall + 0.0001)), HEIGHT)

        color = (200, max(0, 200 - wall_height // 3), max(0, 200 - wall_height // 3))
        column_width = WIDTH / RAY_COUNT
        wall_strips.append((color, int(ray_index * column_width),
                            (HEIGHT // 2) - (wall_height // 2),
                            math.ceil(column_width), wall_height))

    # 壁の描画をまとめて実行
    for strip in wall_strips:
        color, col_x, wall_top, cwidth, wheight = strip
        pygame.draw.rect(screen, color, (col_x, wall_top, cwidth, wheight))

def check_wall_collision(nx, ny):
    """次の移動先(nx, ny)が壁かどうかをチェックし、壁ならFalseを返す"""
    map_x = int(nx // TILE_SIZE)
    map_y = int(ny // TILE_SIZE)
    if map_x < 0 or map_x >= MAP_WIDTH or map_y < 0 or map_y >= MAP_HEIGHT:
        return False
    return (MAP[map_y][map_x] == 0)

def distance(x1, y1, x2, y2):
    """2点間の距離"""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def move_player(keys):
    """プレイヤーの移動と回転"""
    global player_x, player_y, player_angle

    if keys[pygame.K_w]:
        nx = player_x + math.cos(player_angle) * player_speed
        ny = player_y + math.sin(player_angle) * player_speed
        if check_wall_collision(nx, ny):
            player_x, player_y = nx, ny
    if keys[pygame.K_s]:
        nx = player_x - math.cos(player_angle) * player_speed
        ny = player_y - math.sin(player_angle) * player_speed
        if check_wall_collision(nx, ny):
            player_x, player_y = nx, ny
    if keys[pygame.K_a]:
        player_angle -= rotation_speed
    if keys[pygame.K_d]:
        player_angle += rotation_speed

def shoot_bullet():
    """銃弾を発射"""
    global can_shoot, last_shot_time
    now = pygame.time.get_ticks()
    if can_shoot and (now - last_shot_time) > shoot_cooldown:
        # 弾の位置と向きを指定
        bx = player_x
        by = player_y
        bullets.append([bx, by, player_angle])
        last_shot_time = now

def update_bullets():
    """弾の移動と画面外/壁衝突判定"""
    global bullets
    updated_bullets = []
    for b in bullets:
        bx, by, angle = b
        nx = bx + math.cos(angle) * bullet_speed
        ny = by + math.sin(angle) * bullet_speed
        # 壁衝突判定
        if check_wall_collision(nx, ny):
            updated_bullets.append([nx, ny, angle])
        # そうでなければ消滅
    bullets = updated_bullets

def detect_enemy_hit():
    """弾と敵の衝突判定"""
    global enemies, bullets
    removed_bullets = set()
    for i, b in enumerate(bullets):
        bx, by, angle = b
        for e in enemies:
            ex, ey, ehp = e
            # 距離判定
            if distance(bx, by, ex, ey) < enemy_min_dist:
                e[2] -= 50  # 敵のHPを減らす
                removed_bullets.add(i)
    # HPが0以下の敵消去
    enemies = [e for e in enemies if e[2] > 0]
    # 衝突した弾を削除
    bullets = [b for i, b in enumerate(bullets) if i not in removed_bullets]

def move_enemies():
    """敵の追跡ロジックとプレイヤーとの衝突判定"""
    global player_hp
    for e in enemies:
        ex, ey, ehp = e
        angle_to_player = math.atan2(player_y - ey, player_x - ex)
        nx = ex + math.cos(angle_to_player) * enemy_speed
        ny = ey + math.sin(angle_to_player) * enemy_speed
        if check_wall_collision(nx, ny):
            e[0] = nx
            e[1] = ny
        # プレイヤーとの衝突時にHPを減らす
        if distance(nx, ny, player_x, player_y) < enemy_min_dist * 1.2:
            player_hp -= 0.05  # 衝突している間じわじわ減る
            if player_hp < 0:
                player_hp = 0

def draw_ui():
    """HPなどのUI描画"""
    font = pygame.font.SysFont(None, 24)
    hp_text = font.render(f"HP: {int(player_hp)}", True, (255, 0, 0))
    screen.blit(hp_text, (10, 10))

def main():
    global player_hp
    init_enemies()

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shoot_bullet()

        # 入力処理
        keys = pygame.key.get_pressed()
        move_player(keys)

        # 3Dレンダリング（壁の描画）
        screen.fill((100, 100, 100))
        cast_rays(player_x, player_y, player_angle)

        # 弾の更新＆衝突判定
        update_bullets()
        detect_enemy_hit()

        # 敵の移動＆衝突判定
        move_enemies()

        # 弾の表示
        for bx, by, ang in bullets:
            bx_screen = int(bx / 4)
            by_screen = int(by / 4)
            pygame.draw.circle(screen, (255, 255, 0), 
                               (bx_screen, by_screen), 2)

        # 2Dマップ上の敵表示（デバッグ用簡易表示）
        for e in enemies:
            ex, ey, ehp = e
            ex_screen = int(ex / 4)
            ey_screen = int(ey / 4)
            pygame.draw.circle(screen, (0, 128, 0), 
                               (ex_screen, ey_screen), 3)

        # UI描画 (HPなど)
        draw_ui()

        pygame.display.flip()

        # ゲームオーバー判定（HPが0で終了）
        if player_hp <= 0:
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
