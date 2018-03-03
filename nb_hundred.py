#BY VALLABH RAMAKANTH

import pygame
from pygame.locals import *
import random
from time import sleep

#SOME CONSTANTS
G = 0.1
dt = 1
N = 101


class planet:
    def __init__(self,m, x, y, vx, vy):
        self.m = m
        self.r = int((m)**(1.0/3))
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.colour = (random.randint(20,255),random.randint(20,255),random.randint(20,255))

#CLEAR ACCELERATION
def clear_a(p):
    for i in range(N-1):
        p[i].ax = p[i].ay = 0

#UPDATES x AND y ACCELERATIONS OF EACH PLANET IN EACH ITERATION 
def set_a(p):
    for i in range(N-1):
        for j in range(i+1, N-1):
            dist = ((p[i].x - p[j].x)**2 + (p[i].y - p[j].y)**2)**0.5
            ux = (p[i].x - p[j].x)*1.0/dist
            uy = (p[i].y - p[j].y)*1.0/dist
            p[i].ax = p[i].ax - ((G * p[j].m * 1.0)/(dist**2))*ux
            p[i].ay = p[i].ay - ((G * p[j].m * 1.0)/(dist**2))*uy
            p[j].ax = p[j].ax + ((G * p[i].m * 1.0)/(dist**2))*ux
            p[j].ay = p[j].ay + ((G * p[i].m * 1.0)/(dist**2))*uy

#UPDATES x AND y VELOCITIES OF EACH PLANET IN EACH ITERATION 
def update_v(p):
    for i in range(N-1):
        p[i].vx = (p[i].vx + p[i].ax * dt)
        p[i].vy = (p[i].vy + p[i].ay * dt)
        
#UPDATES POSITION OF EACH PLANET IN EACH ITERATION        
def update_pos(p):
    for i in range(N-1):
        #CHECKS IF PLANET IS NEAR THE BOUNDARY OF WINDOW 
        if(p[i].x >= 1000 - p[i].r or p[i].x <= p[i].r):
            p[i].vx = -p[i].vx
        if(p[i].y >= 600 - p[i].r or p[i].y <= p[i].r):
            p[i].vy = -p[i].vy
        #INCREMENT POSITION
        p[i].x = p[i].x + p[i].vx * dt
        p[i].y = p[i].y + p[i].vy * dt
        

def create_p():
    lx = random.sample(range(2, 998), N)
    ly = random.sample(range(2, 598), N)
    return [planet(random.randint(100,2000)*0.1, lx[i], ly[i], random.randint(0,100)*0.01,random.randint(0,100)*0.01) for i in range(N-1)]

#INITIALIZATION OF WINDOW
pygame.init()
canvas = pygame.display.set_mode((1000,600), 0, 0);
canvas.fill((0,0,0))

#INITIALIZATION OF PLANETS
p = create_p()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
    #UPDATE CANVAS
    canvas.fill((0,0,0))
    clear_a(p)
    set_a(p)
    update_v(p)
    update_pos(p)
    for i in range(N-1):
        pygame.draw.circle(canvas, p[i].colour, (int(p[i].x), int(p[i].y)), p[i].r,0)  
    pygame.display.update()
