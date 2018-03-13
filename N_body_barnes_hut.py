'''Made by Vallabh and Arnav'''

'''
Implements barnes hut algorithm for nlogn complexity.
Can input values or randomize.

This can be extended to 3-D with a few modifications but the displaying oon screen bit will be tricky,
'''



import pygame,sys,random,time
from pygame.locals import *
import gc
pygame.init()
sys.setrecursionlimit(100)                                                  #recusion might go this deep if 2 bodies are really close together

def dist(x1,y1,x2,y2):                                                      #returns dist bw 2 points
    d=((x1-x2)**2+(y1-y2)**2)**.5
    if d<1:
        return 1
    return d

G=.07

class body:                                                                 #all bodies will be objects of this class
    def __init__(self, m, c, vx=0, vy=0):
        self.m = m
        self.c = c
        self.vx = vx
        self.vy = vy
        self.ax = self.ay = 0
    def bounce(self):                                                       #rebouds off walls
        if self.c[0]>800 and self.vx>0:
            self.vx*=-1
        if self.c[1]>800 and self.vy>0:
            self.vy*=-1
        if self.c[0]<0 and self.vx<0:
            self.vx*=-1
        if self.c[1]<0 and self.vy<0:
            self.vy*=-1
    def blit(self):                                                         #displays on screen
        global screen
        pygame.draw.circle(screen,(255,255,255),(int(self.c[0]),int(self.c[1])),int((self.m**.3)/2.0))
    

class cell:                                                                 #to implement barnes hut, screen will be divided into cells. Each one will be an object of this class
    def __init__(self, d, o):
        self.n = 0
        self.m_t = 0
        self.com = (0,0)
        self.d = d
        self.origin = o

    def add_body(self, b):                                                  #adds a body into the tree
        backup=list(self.com)
        self.com = ((self.com[0]*self.m_t + b.m*b.c[0])/(self.m_t + b.m),   #as the body passes through a cell the whole cells COM, NUMBER OF BODIES and MASS is updated
                    (self.com[1]*self.m_t + b.m*b.c[1])/(self.m_t + b.m))
        self.m_t += b.m
        o=self.origin
        if(self.n == 1):                                                    #if the cell has only 1 body
            sub = body(self.m_t-b.m, backup)                                #the cell is split into 4 quadrants
            nd=(self.d[0]/2.0, self.d[1]/2.0)                               #and the 2 bodies are added based on their coordinates
            self.tl=cell(nd,o)
            self.tr=cell(nd,(o[0]+nd[0],o[1]))
            self.br=cell(nd,(o[0]+nd[0],o[1]+nd[1]))
            self.bl=cell(nd,(o[0],o[1]+nd[1]))
            cx = o[0] + nd[0]
            cy = o[1] + nd[1]
            if(sub.c[0] == cx and sub.c[1] == cy):
                self.tl.add_body(sub)
            elif(sub.c[0] <= cx and sub.c[1] <= cy):
                self.tl.add_body(sub)
            elif(sub.c[0] > cx and sub.c[1] < cy):
                self.tr.add_body(sub)
            elif(sub.c[0] >= cx and sub.c[1] >= cy):
                self.br.add_body(sub)
            elif(sub.c[0] < cx and sub.c[1] > cy):
                self.bl.add_body(sub)
                

            if(b.c[0] == cx and b.c[1] == cy):
                self.tl.add_body(b)
            elif(b.c[0] <= cx and b.c[1] <= cy):
                self.tl.add_body(b)
            elif(b.c[0] > cx and b.c[1] < cy):
                self.tr.add_body(b)
            elif(b.c[0] >= cx and b.c[1] >= cy):
                self.br.add_body(b)
            elif(b.c[0] < cx and b.c[1] > cy):
                self.bl.add_body(b)
                

        elif(self.n>1):                                                     #if cell has multiple bodies, the current body traverses the tree
            nd=(self.d[0]/2,self.d[1]/2)                                    #based on its coordinates
            cx = o[0] + nd[0]
            cy = o[1] + nd[1]
            if(b.c[0] == cx and b.c[1] == cy):
                self.tl.add_body(b)
            elif(b.c[0] <= cx and b.c[1] <= cy):
                self.tl.add_body(b)
            elif(b.c[0] > cx and b.c[1] < cy):
                self.tr.add_body(b)
            elif(b.c[0] >= cx and b.c[1] >= cy):
                self.br.add_body(b)
            elif(b.c[0] < cx and b.c[1] > cy):
                self.bl.add_body(b)                
        self.n += 1


def calc_acc(b,top):
    if top.n>1 or (top.n==1 and dist(top.com[0],top.com[1],b.c[0],b.c[1])>1):   #traverse throught the tree for each body
        dd=dist(b.c[0],b.c[1],top.com[0],top.com[1])                            #if the COM of a cell is far enough then aproximate all the bodies 
        if dd/top.d[0]<.5 and top.n>1:                                          #inside the cell to be at COM and fing acc
            calc_acc(b,top.tl)                                                  #if COM is close enough, find acc similarly for its children nodes
            calc_acc(b,top.tr)
            calc_acc(b,top.br)
            calc_acc(b,top.bl)
        else:
            b.ax+=G*top.m_t*(top.com[0]-b.c[0])/(dd)**3
            b.ay+=G*top.m_t*(top.com[1]-b.c[1])/(dd)**3

##const = (G*100000)**0.5
##r=[((l[i]%400-200)**2+(l[i]/400-200)**2)**0.75 for i in range(n)]
##bodies=[body(random.randint(20,100),[l[i]%400+200,l[i]/400+200],float(l[i]/400-200)*const/r[i],-float(l[i]%400-200)*const/r[i]) for i in range(n)]
##bodies+=[body(100000,[400,400],0,0)]


#user can choose bodies initial conditions
n=int(raw_input("enter number of bodies : "))
l = random.sample(range(0, 160000), n)
print "press 's' to specify values, anything else to randomize"
ch=raw_input("")
if ch=='s':
    bodies=[]
    for i in range(n):
        print "body",i
        bodies+=[body(int(raw_input("mass : ")),list(eval(raw_input("coord : "))),int(raw_input("x vel : ")),int(raw_input("y vel : ")))]
else:
    bodies=[body(random.randint(20,100),[l[i]%400+200,l[i]/400+200],random.random()-.5,random.random()-.5) for i in range(n)]


#setting up display and main root
root=cell((800,800),(0,0))
screen = pygame.display.set_mode((800,800))
while True:
    screen.fill((0,0,0))
    root=cell((800,800),(0,0))
    for i in bodies:            #resets acc and creates tree
        i.ax=i.ay=0
        root.add_body(i)
    for i in bodies:            #calcs the stats of each body and displays it on screen
        i.bounce()
        calc_acc(i,root)
        i.vx+=i.ax
        i.c[0]+=i.vx
        i.vy+=i.ay
        i.c[1]+=i.vy
        i.blit()
    pygame.display.update()
