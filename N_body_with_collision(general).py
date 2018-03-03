import pygame,sys,random,time
from pygame.locals import *

'''
This code uses a class body to create objects with their own stats(coordinates, velocity, acc etc).
When ran, user inputs the number of bodies and if he wants can specify the beggining stats of each body.
In each loop each body has the force on it calculated and acc updated.
This acc updates vel which updates coord.
all objects are then blit ont o screen.
'''


def dist(x1,y1,x2,y2):              #returns distance between 2 points
    d=((x1-x2)**2+(y1-y2)**2)**.5
    if d<1:
        return 1
    return d
def collide(b1,b2):                 #checks if 2 bodies are touching eachother
    if dist(b1.get_pos()[0],b1.get_pos()[1],b2.get_pos()[0],b2.get_pos()[1])<2.5*b1.get_mass()**(1.0/3)+2.5*b2.get_mass()**(1.0/3)+2:
        return True
    return False
class body:                         
    def __init__(self,x=500,y=350,vx=0,vy=0,m=7):#stats of each body
        self.x,self.y=x,y
        self.desx,self.desy=x,y
        self.vx=vx
        self.vy=vy
        self.ax=self.ay=0
        self.mass=m
    def reset(self):
        self.x,self.y=500,350
        self.desx,self.desy=500,300
        self.vx=self.vy=self.ax=self.ay=0
    def blit(self):
        global screen
        pygame.draw.circle(screen,(255,255,255),(int(self.x),int(self.y)),int(2.5*self.mass**(1.0/3)))
    def changevel(self,v1,v2):      #updates the bodies velocities with provided values
        self.vx=v1
        self.vy=v2
    def change(self):               #uses current acceleration to update vels
        self.vx+=self.ax
        self.vy+=self.ay
        self.x+=self.vx
        self.y+=self.vy
    def get_pos(self):              #gives current coordinates
        return (self.x,self.y)
    def get_mass(self):             #gives mass
        return self.mass
    def updateacc(self,ax,ay):      #use this fn while calcing acc due to all remaining bodies
        self.ax+=ax
        self.ay+=ay
    def resetacc(self):             #resets acc after an instance to calculate the acceleration for the new state
        self.ax=0
        self.ay=0
    def bounce(self):               #didnt want the bodies to fly off screen so they bounce off walls
        if self.x>1000 and self.vx>0:
            self.vx*=-1
        if self.y>700 and self.vy>0:
            self.vy*=-1
        if self.x<0 and self.vx<0:
            self.vx*=-1
        if self.y<0 and self.vy<0:
            self.vy*=-1
            
n=int(raw_input("enter number of bodies : "))
print "press 's' to specify values, anything else to randomize"
ch=raw_input("")
if ch=='s':
    b=[]
    for i in range(n):
        print "body",i
        b=b+[body(int(raw_input("x coord : ")),int(raw_input("y coord : ")),int(raw_input("x vel : ")),int(raw_input("y vel : ")),int(raw_input("mass : ")))]
else:
    b=[body(random.randint(0,1000),random.randint(0,700),0,0,random.randint(5,10)) for i in range(n)]

backup=list(b)

pygame.init()
screen = pygame.display.set_mode((1000,700))

while 1:
    screen.fill((0,0,0))            
    mp=pygame.mouse.get_pos()
    for event in pygame.event.get():  #checks if user closes window or presses 'r' for a new simulation  
        if event.type==KEYDOWN and event.key==114:
            b=list(backup)
        if event.type==QUIT or (event.type==KEYDOWN  and event.key==27):
            pygame.quit()
            break
            quit()


    for i in b:
        i.resetacc()
    for i in range(0,len(b)):           #loop calcs acc for all current bodies
        fx=fy=0
        ipos=b[i].get_pos()
        im=b[i].get_mass()
        for j in range(i+1,len(b)):
            jm=b[j].get_mass()
            jpos=b[j].get_pos()
            d=dist(ipos[0],ipos[1],jpos[0],jpos[1])
            fx=-1*jm*im*(ipos[0]-jpos[0])/d**3
            fy=-1*jm*im*(ipos[1]-jpos[1])/d**3
            b[i].updateacc(fx/im,fy/im)
            b[j].updateacc(-fx/jm,-fy/jm)


    i=j=0
    while i<len(b):                     #this is the collision part
        while j<len(b):                 #if 2 bodies come in contact, they collide inelastically
            if collide(b[i],b[j]) and i!=j:
                i=min(i,j)
                j=max(i,j)
                b[i]=body((b[i].mass*b[i].x+b[j].mass*b[j].x)/(b[i].mass+b[j].mass),(b[i].mass*b[i].y+b[j].mass*b[j].y)/(b[i].mass+b[j].mass),(b[i].mass*b[i].vx+b[j].mass*b[j].vx)/(b[i].mass+b[j].mass),(b[i].mass*b[i].vy+b[j].mass*b[j].vy)/(b[i].mass+b[j].mass),b[i].mass+b[j].mass)
                del b[j]                #del one of the body and update the other as both the collided bodies combined
                j=0
            else:
                j=j+1
        i=i+1
    for k in b:                         #update reqd stuff after each loop
        k.blit()
        k.change()
        k.bounce()
    
    pygame.display.update()
    
