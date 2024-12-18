import pygame
import math

class vec3D:
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
    def add(self, x, y, z):
        return vec3D(self.x + x, self.y + y, self.z + z)
    def sub(self, x, y, z):
        return vec3D(self.x - x, self.y - y, self.z - z)
    def mul(self, scale):
        return vec3D(self.x * scale, self.y * scale, self.z * scale)
    def div(self, scale):
        return vec3D(self.x / scale, self.y / scale, self.z / scale)
    def rotate(self, axis, angle):
        angle = math.radians(angle)
        if axis == 'x':
            return vec3D(
                self.x,
                self.y * math.cos(angle) - self.z * math.sin(angle),
                self.y * math.sin(angle) + self.z * math.cos(angle)
            )
        elif axis == 'y':
            return vec3D(
                self.x * math.cos(angle) + self.z * math.sin(angle),
                self.y,
                -self.x * math.sin(angle) + self.z * math.cos(angle)
            )
        elif axis == 'z':
            return vec3D(
                self.x * math.cos(angle) - self.y * math.sin(angle),
                self.x * math.sin(angle) + self.y * math.cos(angle),
                self.z
            )
    def scale_factor(self):
        return 500/(self.z + 500)
    def draw_line(self,color):
        scale_factor = self.scale_factor()
        pygame.draw.line(screen, color, (width/2, height/2),((self.x*150+width/2)/scale_factor,-self.y*150+height/2), width=1)
pygame.init()
width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
red = [255,0,0]
blue = [0,0,255]
green = [0,255,0]
axis_x = vec3D(1,0,0)
axis_y = vec3D(0,1,0)
axis_z = vec3D(0,0,1)
angle_x = -2
angle_y = 10
angle_z = 0
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill("gray")
    axis_x.rotate('x', angle_x).rotate('y', angle_y).rotate('z', angle_z).draw_line(red)
    axis_y.rotate('x', angle_x).rotate('y', angle_y).rotate('z', angle_z).draw_line(blue)
    axis_z.rotate('x', angle_x).rotate('y', angle_y).rotate('z', angle_z).draw_line(green)
    pygame.display.flip()
    clock.tick(60)#fps

pygame.quit()
