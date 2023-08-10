import numpy as np
import pygame



from obj import Object
from rotate import *



TIME_INTERVAL=0.02
class Camera(Object):

    MOVE=0.02
    move_flag_dict={pygame.K_w:0,
               pygame.K_a:-90,
               pygame.K_s:180,
               pygame.K_d:90,
               }#(angle_change)
    fly_flag_dict={
        pygame.K_SPACE:1,
        pygame.K_LSHIFT:-1
    }
    
          
    def __init__(self,position) -> None:
        super().__init__(position)
        self.rotation_x=0# 绕x轴转
        self.rotation_y=0# 绕y轴转

        self.move_flag=0#0 not move
        self.fly_flag=0#0 not move,1:up -1:down
        self.eye_flag=0#0 not move 1 move
        self.target_position=np.array([
            [0],
            [0],
            [0]
        ],dtype='float64')#x.y.z
    
    
    def update(self):
        change_time=(TIME_INTERVAL/0.001)
        if self.move_flag:
            move_ini=np.array([
                [0],
                [0],
                [self.MOVE*change_time]
            ],dtype='float64')#x.y.z
            move_new=Ry(self.rotation_y+self.move_flag_dict[self.move_flag])*move_ini
            
            self.position+=move_new
            self.target_position+=move_new
        if self.fly_flag:
            move_ini=np.array([
                [0],
                [self.fly_flag*self.MOVE*change_time],
                [0]
            ],dtype='float64')#x.y.z
            self.position+=move_ini
            self.target_position+=move_ini

            



    def getResult_target(self):
        
        new_t=Ry(self.rotation_y)*Rx(self.rotation_x)*(self.target_position-self.position)
        
        return self.position+new_t