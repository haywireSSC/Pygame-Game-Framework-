from math import *
from vectors import *
import asepriteImport as ase
import numpy as np
import pygame as p
from random import uniform

class entity:
    def __init__(self,name='entity',pos=vec()):
        self.pos=pos
        self.collisions=False
        self.name=name
        self.childs={}
        self.globalpos=vec()

    def callChild(self,func,*argv):
        for i in list(self.childs.values()):
            getattr(i, func)(*argv)

    def fixedUpdate(self,root,parent):
        self.callChild('fixedUpdate',root,self)

    def update(self,root,parent):
        self.callChild('update',root,self)

    def draw(self,s,parent):
        self.globalpos=self.pos+parent.pos
        self.callChild('draw',s,self)

class static(entity):
    def __init__(self,name='static',
            pos=vec(),
            size=vec(16,16),
            colour=(255,255,255),
            rect=None,
            sprite=None):
        super().__init__(name,pos)
        self.collisions=True
        self.size = size
        self.colour = colour
        self.rect = rect if rect else (sprite.get_rect() if sprite else p.Rect(self.pos.pos, self.size.pos))
        self.flipH,self.flipV=False,False
        self.sprite=sprite
        self.rotation=90
        self.collisionLayer=0
        self.collideWith=0
        self.origin=vec()

    def draw(self,s,parent):
        self.globalpos=self.pos+parent.pos
        if self.sprite:
            pos=self.pos+parent.globalpos
            surf=p.transform.flip(self.sprite, self.flipH,self.flipV)
            surf.set_colorkey((0,0,0))
            if self.rotation!=90:
                surf=p.transform.rotate(surf, self.rotation-90)
                center=pos-surf.get_rect().center
                center-=fromPolar(self.rotation+135,toVec(self.rect.size).mag/2)+fromPolar(self.rotation-90+self.origin.angle,self.origin.mag*2)
                surf.set_colorkey((0,0,0))
                s.blit(surf,center.pos)
            else:
                s.blit(surf,(pos-self.origin*2).pos)
        else:
            rect = p.Rect.move(self.rect, parent.globalpos.pos)
            p.draw.rect(s,self.colour, rect)
        self.callChild('draw',s,self)

class dynamic(static):
    def __init__(self,name='dynamic',
            chunk='0 0',
            pos=vec(),
            size=vec(16,16),
            colour=(255,255,255),
            rect=None,
            sprite=None):
        super().__init__(name=name,pos=pos,size=size,colour=colour,rect=rect,sprite=sprite)
        self.rectoffset=toVec(self.rect.topleft)

    def update(self,root,parent):
        self.preUpdate(root,parent)
        self.postUpdate(root,parent)

    def postUpdate(self,root,parent):
        if type(parent)==chunkSystem:
            self.chunk = parent.updateChunk(self)
        else:
            self.chunk = parent.chunk
        self.rect.topleft=(self.pos+self.rectoffset).pos
        self.callChild('update',root,self)

class collisions(dynamic):
    def __init__(self,name='collisions',
            pos=vec(),
            size=vec(16,16),
            colour=(255,255,255),
            rect=None,
            sprite=None):
        super().__init__(name=name,pos=pos,size=size,colour=colour,rect=rect,sprite=sprite)
        self.vel=vec()
        self.collisionNormal=vec()
        self.collisionRough=vec()
        self.hit=vec()
        self.collisionLine=(vec(),vec())

    def update(self,root,parent):
        self.preUpdate(root,parent)
        if root.entities['chunkSystem']:
            chunkPos = self.pos//root.entities['chunkSystem'].size
            rects=[i.rect for i in root.entities['chunkSystem'].getChunksRect(chunkPos-1, chunkPos+1).values() if i.collisions and i.collisionLayer==self.collideWith]
        else:
            rects=[i.rect for i in parent.childs if i.collisions and i.collisionLayer==self.collideWith]
        try:
            rects.remove(self.rect)
        except:
            pass

        if self.collisionNormal.x!=0:
            if not int(self.collisionLine[0].x)==int(self.pos.x) or not (self.pos.y>self.collisionLine[0].y and self.pos.y<self.collisionLine[1].y):
                self.collisionNormal.x=0

        if self.collisionNormal.y!=0:
            if not int(self.collisionLine[0].y)==int(self.pos.y) or not (self.pos.x>self.collisionLine[0].x and self.pos.x<self.collisionLine[1].x):
                self.collisionNormal.y=0

        if self.collisionRough.x!=0:
            if not int(self.collisionLine[0].x)==int(self.pos.x):
                self.collisionRough.x=0
        if self.collisionRough.y!=0:
            if not int(self.collisionLine[0].y)==int(self.pos.y):
                self.collisionRough.y=0

        startpos=self.pos.copy()
        self.hit.y=0
        self.pos.y+=self.vel.y*root.delta
        self.rect.top=self.pos.y+self.rectoffset.y
        collide = self.rect.collidelist(rects)
        if collide!=-1:
            other=rects[collide]
            if self.vel.y>0:
                self.pos.y += other.top-self.rect.bottom
                self.collisionNormal.y=-1
            else:
                self.pos.y += other.bottom-self.rect.top
                self.collisionNormal.y=1
            self.collisionRough.y=self.collisionNormal.y
            self.hit.y=self.collisionNormal.y
            self.collisionLine=(vec(other.left-self.rect.width,self.pos.y), vec(other.right,self.pos.y))


        self.hit.x=0
        self.pos.x+=self.vel.x*root.delta
        self.rect.top=startpos.y
        self.rect.left=self.pos.x+self.rectoffset.x
        collide = self.rect.collidelist(rects)
        if collide!=-1:
            other=rects[collide]
            if self.vel.x>0:
                self.pos.x += other.left-self.rect.right
                self.collisionNormal.x=-1
            else:
                self.pos.x += other.right-self.rect.left
                self.collisionNormal.x=1
            self.collisionRough.x=self.collisionNormal.x
            self.hit.x=self.collisionNormal.x
            self.collisionLine=(vec(self.pos.x,other.top-self.rect.height), vec(self.pos.x,other.bottom))

        self.postUpdate(root,parent)

class collisionsNoSolving(dynamic):
    def __init__(self,name='collisions',
            pos=vec(),
            size=vec(16,16),
            colour=(255,255,255),
            rect=None,
            sprite=None):
        super().__init__(name=name,pos=pos,size=size,colour=colour,rect=rect,sprite=sprite)
        self.vel=vec()
        self.hit=vec()

    def update(self,root,parent):
        self.preUpdate(root,parent)

        if root.entities['chunkSystem']:
            chunkPos = self.pos//root.entities['chunkSystem'].size
            rects=[i.rect for i in root.entities['chunkSystem'].getChunksRect(chunkPos-1, chunkPos+1).values() if i.collisions and i.collisionLayer==self.collideWith]
        else:
            rects=[i.rect for i in parent.childs if i.collisions and i.collisionLayer==self.collideWith]
        try:
            rects.remove(self.rect)
        except:
            pass

        startpos=self.pos.copy()
        self.hit.y=0
        self.pos.y+=self.vel.y*root.delta
        self.rect.top=self.pos.y+self.rectoffset.y
        collide=self.rect.collidelist(rects)
        if collide!=-1:
            if self.vel.y>0:
                self.hit.y=-1
            else:
                self.hit.y=1
            self.pos.y-=self.vel.y*root.delta

        self.hit.x=0
        self.pos.x+=self.vel.x*root.delta
        self.rect.top=startpos.y
        self.rect.left=self.pos.x+self.rectoffset.x
        collide=self.rect.collidelist(rects)
        if collide!=-1:
            if self.vel.x>0:
                self.hit.x=-1
            else:
                self.hit.x=1
            self.pos.x-=self.vel.x*root.delta

        self.postUpdate(root,parent)


class animation(static):
    def __init__(self,name,root,pos=vec()):
        self.frames,durations,self.anims = root.getAnim(name)

        self.durations=durations.copy()
        for i,v in enumerate(durations):
            self.durations[i]=sum(durations[:i+1])
        self.durations.insert(0,0)

        size=toVec(self.frames[0].get_size())
        super().__init__(name=name,size=size,pos=pos,sprite=self.frames[0])
        self.frame=0
        self.currentAnim='idle'
        self.speed=1

    @property
    def bounds(self): return self.anims[self.currentAnim]


    def update(self,root,parent):
        if self.bounds[1]-self.bounds[0]==0:
            self.frame=self.bounds[0]
        else:
            starttime,endtime = self.durations[self.bounds[0]-1],self.durations[self.bounds[1]]
            delta = (p.time.get_ticks()*self.speed) % (endtime - starttime)
            for i,v in enumerate(self.durations[self.bounds[0]:self.bounds[1]+1]):
                if delta < v-starttime:
                    self.frame=i+self.bounds[0]
                    break
        self.sprite=self.frames[self.frame]
        self.callChild('update',root,self)

class animationPlayOnce(static):
    def __init__(self,name,animName,root,pos=vec()):
        self.frames,durations,self.anims = root.getAnim(animName)

        self.durations=durations.copy()
        for i,v in enumerate(durations):
            self.durations[i]=sum(durations[:i+1])

        size=toVec(self.frames[0].get_size())
        super().__init__(name=name,size=size,pos=pos,sprite=self.frames[0])
        self.frame=0
        self.speed=1
        self.starttime=p.time.get_ticks()
        self.loops=1
        self.collisions=False
        self.origin=vec(6,6)


    def update(self,root,parent):
        timepassed = (p.time.get_ticks()-self.starttime)*self.speed
        delta = timepassed % self.durations[-1]
        if timepassed > self.durations[-1]*self.loops:
            parent.remove(self.name)
        for i,v in enumerate(self.durations):
            if delta < v:
                self.frame=i
                break
        self.sprite=self.frames[self.frame]

        self.callChild('update',root,self)

class chunkSystem(entity):
    def __init__(self,name='chunkSystem'):
        super().__init__(name=name)
        self.entities={}
        self.size=vec(128,128)
        self.mousePos=vec()
        self.shake=0
        self.shakeDamp=0.99
        self.offset=vec()
        self.prevNames=[]
        self.onScreen=[]

    def lerpTo(self,root,pos,div):
        if type(root)==p.Surface:
            center = toVec(root.get_rect().center)
        else:
            center = toVec(root.s.get_rect().center)
        self.pos+=(((center-pos)-self.pos-self.offset)/div)-self.offset

    def update(self,root,parent):
        self.shake*=self.shakeDamp
        if int(self.shake)==0:
            self.offset=vec()
        else:
            self.offset.x=uniform(-self.shake,self.shake)
            self.offset.y=uniform(-self.shake,self.shake)
        self.mousePos=toVec(p.mouse.get_pos())-self.pos

        self.onScreen=self.getChunkRectPixels(self.pos*-1, root.size-self.pos)
        for i in self.onScreen:
            i.update(root,self)

        names=[i.name for i in self.onScreen]
        for i,name in enumerate(self.prevNames):
            if not name in names:
                try:
                    self.find(name).onHide(root)
                except AttributeError:
                    pass

        self.prevNames=names

    def fixedUpdate(self,root,parent):
        for i in self.onScreen:
            i.fixedUpdate(root,self)
    def draw(self,s,parent):
        self.globalpos=self.pos+parent.pos
        for i in self.onScreen:
            i.draw(s,self)

    def add(self,e):
        chunk = self.getChunkPos(e.pos)
        e.chunk=chunk
        if not chunk in self.entities:
            self.entities[chunk] = {}
        self.entities[chunk][e.name] = e

    def updateChunk(self,e):
        if self.getChunkPos(e.pos) != e.chunk:
            del self.entities[e.chunk][e.name]
            self.add(e)
        return self.getChunkPos(e.pos)

    def getChunkPos(self,pos):
        pos=pos//self.size
        return f'{int(pos.x)} {int(pos.y)}'

    def getChunk(self,chunk):
        if chunk in self.entities:
            return self.entities[chunk]
        else:
            return {}

    def getChunksRect(self,start,end):
        entities={}
        for x in range(int(end.x-start.x)+1):
            for y in range(int(end.y-start.y)+1):
                entities.update(self.getChunk(f'{int(start.x+x)} {int(start.y+y)}'))
        return entities

    def getChunkRectPixels(self,start,end):
        start=start//self.size
        end=end//self.size+1
        return self.getChunksRect(start,end).values()

    def find(self,name):
        for chunk in self.entities.values():
            if name in chunk:
                return chunk[name]
        return False

    def findOnScreen(self,name):
        for e in self.onScreen:
            if e.name==name:
                return e
        return False

    def remove(self,name):
        for chunk in self.entities.values():
            chunk.pop(name,False)
