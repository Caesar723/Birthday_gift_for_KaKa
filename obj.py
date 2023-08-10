import pygame
import numpy as np

from functions import *



class Object:


    def __init__(self,position) -> None:
        self.position=np.array([
            [position[0]],
            [position[1]],
            [position[2]]
        ],dtype='float64')#x.y.z

    def getPosition(self,position,change_x=0,change_y=0,change_z=0):
        return (position[0,0]+change_x,position[1,0]+change_y,position[2,0]+change_z)
    
    def display(self):
        pass