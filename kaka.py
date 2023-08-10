import pygame
import numpy as np
import threading
import time

from rotate import *
from functions import *
from obj import *


class KaKa(Object):

    def __init__(self,width,height,position,cake,firework_generator) -> None:
        super().__init__(position)

        self.kaka_textures=load_glf("ka")
        self.index=0
        
        self.width=width
        self.height=height

        self.alpha=0
        self.change_alpha=0.01

        self.thread_flag=True
        self.display_flag=False
        self.cake=cake
        self.firework_generator=firework_generator


    def update(self):
        while self.alpha<1:
            self.alpha+=self.change_alpha
            time.sleep(0.02)
        self.alpha=1
        self.cake.start_blow_candle()
        while self.index<len(self.kaka_textures):
            self.index+=1
            time.sleep(0.07)
        self.cake.stop_blow_candle()
        while self.alpha>0:
            self.alpha-=self.change_alpha
            time.sleep(0.02)
        self.alpha=0
        self.index=0
        self.display_flag=False
        self.thread_flag=True
        self.firework_generator.start_auto_fire()
        
        


    def display(self):
        if self.display_flag:
            if self.thread_flag:
                thread=threading.Thread(target=self.update)
                thread.start()
                self.thread_flag=False
                
                
            if self.alpha!=0:
                self.display_img()

    def display_img(self):
        
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        #glEnable(GL_COLOR_MATERIAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(1,1,1,self.alpha)  # 设置颜色和透明度
        glBindTexture(GL_TEXTURE_2D, self.kaka_textures[self.index%len(self.kaka_textures)])
        glBegin(GL_QUADS)

        four_corner=[(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)]

        for corner in four_corner:
            glTexCoord2f(*corner)
            x_unit=1 if corner[0]==1 else -1
            y_unit=1 if corner[1]==1 else -1
            glVertex3f(self.position[0][0]+x_unit*self.width, self.position[1][0]+y_unit*self.height,self.position[2])
        
        
        glEnd()
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        #glDisable(GL_COLOR_MATERIAL)
        glPopMatrix()
        

        #self.update()

