import pygame
import math
width = 1280
height = 720
screen = pygame.display.set_mode((width, height))
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
                self.y * math.cos(angle) + self.z * math.sin(angle),
                -self.y * math.sin(angle) + self.z * math.cos(angle)
            )
        elif axis == 'y':
            return vec3D(
                self.x * math.cos(angle) - self.z * math.sin(angle),
                self.y,
                self.x * math.sin(angle) + self.z * math.cos(angle)
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
        pygame.draw.line(screen, color, (width/2, height/2),((self.x*150+width/2)/scale_factor,-self.y*150+height/2), width=2)