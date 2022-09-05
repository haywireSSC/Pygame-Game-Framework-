from math import *
from vectors import *
import pygame as p
import entities as e
from time import time

def arrows():
    arrows=vec()
    k=p.key.get_pressed()
    if k[p.K_RIGHT]:
        arrows.x+=1
    if k[p.K_LEFT]:
        arrows.x-=1
    if k[p.K_DOWN]:
        arrows.y+=1
    if k[p.K_UP]:
        arrows.y-=1
    return arrows

def drawGrid(s,pos,size,cellSize):
    for x in range(size.x):
        for y in range(size.y):
            p.draw.rect(s, (255,0,0), p.Rect((vec(x,y)*cellSize).pos, cellSize.pos), 2)


def clamp(num,start,end):
    return max(min(num,end),start)


class flashEffect(e.entity):
    def __init__(self):
        super().__init__()

    def draw(self,s,parent):
        self.callChild('draw',s,self)


class debugInfo(e.entity):
    def __init__(self):
        self.start=time()
        super().__init__(name='debugInfo')
        self.font=p.font.Font('Minecraftia-Regular.ttf',8)
        self.lines=()
    def update(self,root,parent):
        self.lines=(
            'fps: '+str(int(root.clock.get_fps())),
            #'sdl: '+str(p.version.SDL),
            #'pygame: '+p.version.ver,
            #'runtime: '+str(round(time()-self.start, 1))
        )
        self.callChild('update',root,self)

    def draw(self,s,parent):
        y=0
        for line in self.lines:
            text=self.font.render(line,False,(0,0,0))
            s.blit(text,(0,y))
            y+=text.get_height()
        self.callChild('draw',s,self)
