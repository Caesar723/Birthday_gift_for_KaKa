from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime, timedelta
import random

from functions import *
from rotate import *



ORGPATH=os.path.dirname(os.path.abspath(__file__))
PATH=ORGPATH+"/{}"

class Favourite_Img:
    
    
    def __init__(self,position,rotate_angle) -> None:
        self.position=position
        self.rotate_angle=rotate_angle
        self.paths=os.listdir(PATH.format("HAPPY_TIME_IMAGE"))
        if self.paths:
            self.img=Image.open(PATH.format(f"HAPPY_TIME_IMAGE/{self.paths[random.randint(0,len(self.paths)-1)]}"))
            self.adjust_length()
            frame = self.img.convert("RGBA")
            flipped_image = frame.transpose(Image.FLIP_TOP_BOTTOM)
            
            data = np.array(flipped_image)
            self.texture_id=img2texture(data,(self.width,self.height))
            
            self.position_process()
            

    def adjust_length(self):
        
        self.width=self.img.size[0]
        self.height=self.img.size[1]

    def position_process(self):
        change_pos=to_np_array(self.position)
        four_corner=[(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)]
        self.four_points=[[],[],[]]
        adjust_height=15
        adjust_factor=self.height/adjust_height
        for corner in four_corner:
            x_unit=1 if corner[0]==1 else -1
            y_unit=1 if corner[1]==1 else -1
            self.four_points[0].append(self.position[0]+x_unit*self.width/adjust_factor)
            self.four_points[1].append(self.position[1]+y_unit*self.height/adjust_factor)
            self.four_points[2].append(0)
        self.four_points=np.array(self.four_points)
        self.four_points=Ry(self.rotate_angle)*self.four_points
        self.four_points=[self.four_points[:,i]+change_pos for i in range(4)]

    def display_img(self):
        #self.position=[0,0,0]
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        #glEnable(GL_COLOR_MATERIAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glEnable(GL_BLEND)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor4f(1,1,1,0.9)  # 设置颜色和透明度
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glBegin(GL_QUADS)

        four_corner=[(0.0, 0.0),(1.0, 0.0),(1.0, 1.0),(0.0, 1.0)]

        for point,corner in zip(self.four_points,four_corner):
            glTexCoord2f(*corner)
            
            glVertex3f(point[0][0], point[1][0],point[2][0])
        
        
        glEnd()
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        #glDisable(GL_COLOR_MATERIAL)
        glPopMatrix()

    def display(self):
        if self.paths:
            self.display_img()




if __name__=="__main__":
    print(os.listdir(PATH.format("HAPPY_TIME_IMAGE")))
    Favourite_Img((-25,0,-7),40)
