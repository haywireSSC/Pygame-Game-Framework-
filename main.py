from vectors import *
from map import *
from math import *
import pygame as p
import asepriteImport as ase

from player import *
from bullet import *
from gun import *
import entities as en
import utils as ut
from map import *
p.init()
p.font.init()

class loop():
    def __init__(self,fps=60,fpsLimit=60,scale=2,spriteScale=2,bg=(0,0,0),size=vec(256,256)):
        self.fpsLimit=fpsLimit
        self.fps=fps
        self.clock=p.time.Clock()
        self.bg=bg
        self.scale=scale
        self.size=size
        self.screenSize=size*scale
        self.s=p.Surface(size.pos)
        self.screen = p.display.set_mode(self.screenSize.pos, p.RESIZABLE)
        self.quit=False
        self.entities={}
        self.chunkSize=vec(256,256)
        self.anims={}
        self.sprites={}
        self.spriteScale=spriteScale
        self.rootEntity=en.entity()


        self.events={
        'fixedUpdate':p.USEREVENT+1
        }

        ase.generateSheets()

        p.time.set_timer(self.events['fixedUpdate'],1000//self.fps)

    @property
    #def delta(self): return 1/(self.clock.get_fps()/self.fps) if self.clock.get_fps() else 0
    def delta(self): return min(10, float(self.clock.get_time())/((1/self.fps)*1000)) if self.clock.get_time() else 1

    def arrows(self):
        arrows=vec()
        k=p.key.get_pressed()
        if k[K_RIGHT]:
            arrows.x+=1
        if k[K_LEFT]:
            arrows.x-=1
        if k[K_UP]:
            arrows.y+=1
        if k[K_DOWN]:
            arrows.y-=1
        return arrows


    def eventsCheck(self):
        for e in p.event.get():
            if e.type == p.QUIT:
                self.quit=True
            elif e.type == p.VIDEORESIZE:
                self.screenSize=vec(e.w,e.h)
                self.size=self.screenSize//self.scale+1
                self.s=p.Surface(self.size.pos)

            elif e.type == self.events['fixedUpdate']:
                self.fixedUpdate()

    def update(self):
        self.eventsCheck()
        for e in list(self.entities.values()):
            e.update(self,self.rootEntity)

    def fixedUpdate(self):
        for e in list(self.entities.values()):
            e.fixedUpdate(self,self.rootEntity)

    def draw(self):
        for e in list(self.entities.values()):
            e.draw(self.s,self.rootEntity)
        self.screen.blit(p.transform.scale(self.s, self.screenSize.pos), (0,0))
        p.display.update()
        self.s.fill(self.bg)
        self.clock.tick(self.fpsLimit)

    def getAnim(self,name):
        if name in self.anims:
            return self.anims[name]
        else:
            self.anims[name] = ase.loadSheet(name)
            for i,v in enumerate(self.anims[name][0]):
                self.anims[name][0][i] = p.transform.scale(v, (toVec(v.get_size())*self.spriteScale).pos)
            return self.anims[name]

    def getSprite(self,name):
        if name in self.sprites:
            return self.sprites[name]
        else:
            sprite=p.image.load(f'assets/{name}.png').convert()
            sprite.set_colorkey((0,0,0))
            sprite=p.transform.scale(sprite, (toVec(sprite.get_size())*self.spriteScale).pos)
            self.sprites[name]=sprite
            return sprite


    def add(self,e):
        self.entities[e.name]=e



loop=loop(scale=1,bg=(240,246,240),fpsLimit=-1,fps=60)
c = en.animation('character',loop)
c.collisions=False
gun=gun(loop)
player = player({'anim':c,'gun':gun})

ch = en.chunkSystem()
loop.add(ch)
loop.add(ut.debugInfo())
ch.add(player)
ch.pos=vec(100,100)
s=p.Surface((10,10))
s.fill((255,100,0))
class a(en.static):
    def __init__(self):
        super().__init__(sprite=p.image.load('assets/tst.png').convert())
    def update(self,root,parent):
        self.rotation+=root.delta
        self.callChild('update',root,self)



map=map(loop,ch,name='tilemap')
ch.add(map)

while not loop.quit:
    loop.update()
    loop.draw()
