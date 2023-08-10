import pygame
import numpy as np

from rotate import *
from functions import *
from obj import *


class Font(Object):
    font_color = (255, 255, 255)  # 白色

    def __init__(self,position,string,size,color,diffuse=(0.5,0.5,0.5,0.5),rotate=(0,0,0)) -> None:
        super().__init__(position)
        self.vertices=load_stl(string)
        self.size=size
        self.color=color
        self.diffuse=diffuse
        self.rotate=rotate

        self.display_id=self.draw()

    @create_display_list
    def draw(self):
        drawPicture(self.vertices,
                    *self.getPosition(self.position),
                    *self.rotate,
                    *self.size,
                    material_ambient=to_one(self.color),
                    material_diffuse=self.diffuse,
                    material_specular=self.diffuse,
                    material_shininess=(2))
        
    def display(self):
        
        glCallList(self.display_id)
        