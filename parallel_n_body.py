import numpy as np
import time,random
import pygame,sys
from numba import vectorize, cuda, jit

G=10
N=700
x=np.array([random.randint(350,650) for i in range(N)],dtype=np.float32)
y=np.array([random.randint(150,450) for i in range(N)],dtype=np.float32)
xv=np.array([random.random() for i in range(0,N)],dtype=np.float32)
yv=np.array([random.random() for i in range(0,N)],dtype=np.float32)


'''This should ideally parallelize all numpy array operations and make it faster,
however after we used numpy to calc all the acc at once, the speed already greatly improved
since numpyhas its own in-built optimizations for said calculations. So the @jit doesnt make too much of a diff.
Anyway this makes the brute force implementation around 7x faster.'''
@jit
def updatev(x,vx,y):
    xx=np.reshape(x,[N,1])
    yy=np.reshape(y,[N,1])
    ax=G*np.sum(np.nan_to_num((xx-x)/np.power((np.power(x-xx,2)+np.power(y-yy,2)),1.5)),axis=0)
    fx=vx+np.reshape(ax,[N])
    return fx

pygame.init()
canvas = pygame.display.set_mode((1000,600), 0, 0);
canvas.fill((0,0,0))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
    #UPDATE CANVAS
    canvas.fill((0,0,0))
    xv=updatev(x,xv,y)
    yv=updatev(y,yv,x)
    x+=xv
    y+=yv
    xv=np.sign(1000-x)*np.sign(x)*xv
    yv=np.sign(600-y)*np.sign(y)*yv
    #print(xv)
    #print(yv)
    for i in range(N):
        pygame.draw.circle(canvas, (255,0,0), (int(x[i]), int(y[i])), 3,0)  
    pygame.display.update()
