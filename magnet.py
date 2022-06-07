import sys, pygame, pygame.gfxdraw
import numpy as np
from pygame.locals import *

np.random.seed(11001)

width, height = (600, 600)
display_surf = pygame.display.set_mode((width, height))
pygame.display.set_caption('magnet')

fps = 180
fps_clock = pygame.time.Clock()

def coord_convert(x, y): #도넛형 공간에 맞게 좌, 우 양극과 상, 하 양극을 연결한다
	coord_x = x
	if x <= width / 2:
		coord_x += width / 2
	else:
		coord_x -= width / 2
	coord_y = y
	if y <= height / 2:
		coord_y += height / 2
	else:
		coord_y -= height / 2
	return (coord_x, coord_y)

def get_distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def get_vector(x1, y1, x2, y2):
    A = coord_convert(x1, y1)
    B = coord_convert(x2, y2)
    if get_distance(*A, *B) < get_distance(x1, y1, x2, y2):
        return (B[0] - A[0], B[1] - A[1])
    else:
        return (x2 - x1, y2 - y1)

def normalize(x, y, sign):
    size = (x ** 2 + y ** 2) ** 0.5
    if size > electron_r * 2 or sign > 0:
        return (x / (size ** 2), y / (size ** 2))
    else:
        return (0, 0)

class electron:
    def __init__(self, x, y, r, electric_charge):
        self.x = x
        self.y = y
        self.r = r
        self.max_spd = 10000
        self.friction_size = 0.01
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity_size = 0
        self.electric_charge = electric_charge
        self.colors = [(255, 0, 0), (0, 0, 255)]
        self.color = 0
        if self.electric_charge < 0:
            self.color = 1

    def apply_force(self, force_x, force_y):
        self.velocity_x += force_x
        self.velocity_y += force_y
        self.velocity_size = (self.velocity_x ** 2 + self.velocity_y ** 2) ** 0.5
        if self.velocity_size > self.max_spd:
            self.velocity_x *= self.max_spd / self.velocity_size
            self.velocity_y *= self.max_spd / self.velocity_size
            self.velocity_size = self.max_spd

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def apply_friction(self):
        if self.velocity_size > self.friction_size:
            self.velocity_x *= (self.velocity_size - self.friction_size) / self.velocity_size
            self.velocity_y *= (self.velocity_size - self.friction_size) / self.velocity_size
            self.velocity_size -= self.friction_size
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            self.velocity_size = 0

    def reverse(self):
        self.electric_charge *= -1
        self.color += 1
        self.color %= 2

timer = 0
act_time = 1

White = (255, 255, 255)

electrons = []
num_electron = 30
electron_r = 12
electric_charge_init = 2
for i in range(0, num_electron):
    electrons.append(electron(np.random.randint(electron_r, width - electron_r), np.random.randint(electron_r, height - electron_r), electron_r, electric_charge_init * [1, -1][np.random.randint(0, 2)]))

system_force = 1

while True: #상호작용 부분 처리 효율화하기
    display_surf.fill(White)
    if timer == act_time:
        timer = 0
        for i in range(0, num_electron):
            i_total_force_x = 0
            i_total_force_y = 0
            if electrons[i].x < -electron_r:
                electrons[i].x += width
            if electrons[i].x > width + electron_r:
                electrons[i].x -= width
            if electrons[i].y < -electron_r:
                electrons[i].y += height
            if electrons[i].y > height + electron_r:
                electrons[i].y -= height
            for j in range(0, num_electron):
                if i != j:
                    i_force_x, i_force_y = normalize(*get_vector(electrons[i].x, electrons[i].y, electrons[j].x, electrons[j].y), electrons[i].electric_charge * electrons[j].electric_charge)
                    i_total_force_x += -i_force_x * electrons[i].electric_charge * electrons[j].electric_charge
                    i_total_force_y += -i_force_y * electrons[i].electric_charge * electrons[j].electric_charge
            #print('{0} {1}'.format(i_total_force_x, i_total_force_y))
            electrons[i].apply_force(i_total_force_x, i_total_force_y)
            if np.random.randint(0, 1000000) == 0:
                electrons[i].reverse()
            
    for i in range(0, num_electron):
        pygame.gfxdraw.aacircle(display_surf, int(electrons[i].x), int(electrons[i].y), electron_r, electrons[i].colors[electrons[i].color])
        if electrons[i].x < electron_r:
            pygame.gfxdraw.aacircle(display_surf, int(electrons[i].x + width), int(electrons[i].y), electron_r, electrons[i].colors[electrons[i].color])
        if electrons[i].x > width - electron_r:
            pygame.gfxdraw.aacircle(display_surf, int(electrons[i].x - width), int(electrons[i].y), electron_r, electrons[i].colors[electrons[i].color])
        if electrons[i].y < electron_r:
            pygame.gfxdraw.aacircle(display_surf, int(electrons[i].x), int(electrons[i].y + height), electron_r, electrons[i].colors[electrons[i].color])
        if electrons[i].y > height - electron_r:
            pygame.gfxdraw.aacircle(display_surf, int(electrons[i].x), int(electrons[i].y - height), electron_r, electrons[i].colors[electrons[i].color])
        electrons[i].move()
        electrons[i].apply_friction()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if event.button == 2:
                for i in range(0, num_electron):
                    if (electrons[i].x - mouse_x) ** 2 + (electrons[i].y - mouse_y) ** 2 <= electron_r ** 2:
                        electrons[i].reverse()
            if event.button == 1:
                num_electron += 1
                electrons.append(electron(mouse_x, mouse_y, electron_r, 1))
            if event.button == 3:
                num_electron += 1
                electrons.append(electron(mouse_x, mouse_y, electron_r, -1))

    pygame.display.update()
    fps_clock.tick()
    timer += 1
