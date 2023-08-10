import pygame
import numpy as np
import random


from functions import *
from obj import *
from candle import *

class Cake(Object):

    def __init__(self,position,num_layers) -> None:
        super().__init__(position)
        self.num_layers=num_layers
        self.vertices_cake=load_stl("cake")
        self.vertices_cream=load_stl("cream")
        self.cream_color=[(214,226,172),(209,224,224),(224,180,189),(107,69,110),(131,128,147),(158,161,108)]
        self.cake_color=[(109,58,29)]

        self.sizes=[]
        self.positions=[]
        self.candles=[]


        self.hight=0.42
        self.size=10

        self.display_id=self.draw()
        self.drawCandles()

        self.vbo_id_circle = create_vbo(load_stl("circle", 1))

        

    
    def draw_cake_cream(self):
    
        #dis_to_org=7
        Size=self.size
        Size_change=1
        hight_org=0

        material_diffuse=(1,1,1,1)
        #material_ambient=(0.7,0.7,0.7,1)

        for i in range(self.num_layers):
            
            change_position=np.array([
                [0],
                [hight_org-Size*self.hight],
                [0]
            ])
            hight_org=change_position[1][0]
            position=self.position+change_position
            Size+=Size_change+i

            self.sizes.append(Size)
            self.positions.append(position)
            
            
            cream_color=to_one(self.cream_color[random.randint(0,len(self.cream_color)-1)],1)
            cake_color=to_one(self.cake_color[random.randint(0,len(self.cake_color)-1)],1)

            drawPicture(self.vertices_cake,
                        *self.getPosition(position),
                        -90,0,0,
                        *[Size]*3,material_diffuse=material_diffuse,material_ambient=cake_color)
            drawPicture(self.vertices_cream,
                        *self.getPosition(position),
                        -90,0,0,
                        *[Size]*3,material_diffuse=material_diffuse,material_ambient=cream_color)
        #drawPicture()

    def drawCandles(self):#,size,hight
        num_candle=self.num_layers
        for i in range(len(self.positions)):

            position=np.array([[0],[self.sizes[i]/10],[(self.sizes[i]-1)/2]])+self.positions[i]

            if num_candle/5>=1:
                rotate_num=5
                num_candle-=5
            elif num_candle!=0:
                rotate_num=num_candle%5
                num_candle=0
            else:
                break

            rotate_angle=360//rotate_num
            
            for i in range(rotate_num):
                
                self.candles.append(Candle(position))
                position=Ry(rotate_angle)*position

        
        

    def display(self):
        glCallList(self.display_id)
        for cand in self.candles:
            cand.display()



        glEnable(GL_COLOR_MATERIAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_id_circle)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, None)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for cand in self.candles:
            [light.display() for light in cand.lights]

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisable(GL_BLEND)
        glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)



    @create_display_list
    def draw(self):
        self.draw_cake_cream()


    def start_blow_candle(self):
        for candle in self.candles:
            for light in candle.lights:
                light.start_blowed()


    def stop_blow_candle(self):
        for candle in self.candles:
            for light in list(candle.lights):
                light.stop_blowed()
                if light.live<=0:
                    candle.lights.remove(light)
        

    
