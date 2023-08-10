import pygame
import numpy as np
import datetime

from rotate import *
from functions import *
from obj import *



class Sun(Object):


    def __init__(self,position,radius) -> None:
        super().__init__(position)
        
        self.color = (241,191,61)#241/255,191/255,61/255
        
        self.light_color=(1,1,1,1)
        self.radius=radius
        self.vertices=load_stl("circle",1)

        self.display_id=self.drawSun_display_list()
       
        
    @create_display_list
    def drawSun_display_list(self):
        color=to_one(self.color)#get color 241/255,191/255,61/255

        glPushMatrix()
        

        # 设置光源属性
        glLightfv(GL_LIGHT0, GL_POSITION,self.getPosition(self.position))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.light_color)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.light_color)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.light_color)

        setMateral(color,color,color,(100))

        # 绘制太阳球体
        glTranslatef(*self.getPosition(self.position))
        gluSphere(gluNewQuadric(), self.radius, 32, 32)
        glPopMatrix()

    def display(self):
        
        glCallList(self.display_id)
        

        
        