import pygame
import numpy as np
import random

from rotate import *
from functions import *
from obj import *

TIME_INTERVAL=0.02


class Candle(Object):
    def __init__(self, position) -> None:
        # 218 48 34
        self.vertices_candle = load_stl("candle")
        self.vertices_string = load_stl("string")

        self.canlde_color = (218, 48, 34)
        self.string_color = (31, 8, 7)

        self.position = position
        self.size = 0.5  # size of candle

        self.display_id = self.draw_body()
        self.lights = [Light(self.position) for i in range(3)]

    @create_display_list
    def draw_body(self):
        canlde_color = to_one(self.canlde_color, 1)
        string_color = to_one(self.string_color, 1)

        material_diffuse = (0.1, 0.1, 0.1, 0)
        material_shininess = 0

        drawPicture(
            self.vertices_candle,
            *self.getPosition(self.position),
            -90,
            0,
            0,
            *[self.size] * 3,
            material_ambient=canlde_color,
            material_diffuse=material_diffuse,
            material_shininess=material_shininess,
            material_specular=(0.9, 0.1, 0.1)
        )

        drawPicture(
            self.vertices_string,
            *self.getPosition(self.position),
            -90,
            0,
            0,
            *[self.size] * 3,
            material_ambient=string_color,
            material_diffuse=material_diffuse,
            material_shininess=material_shininess,
            material_specular=(0, 0, 0, 0)
        )

    def display(self):
        glCallList(self.display_id)


class Light(Object):
    vertices_light = load_stl("circle", 1)
    vertices_len = len(vertices_light)
    iniSize_Range = (0.5, 1)
    iniPos_Range = (-0.5, 0.5)
    Color_list = [(252, 235, 82), (246, 225, 248), (225, 146, 189), (206, 243, 239)]

    def __init__(self, position) -> None:
        self.live = 100

        self.Z_acc = 0
        self.Z_velocity = 0

        self.iniPosition = position
        self.size = self.generate_size()
        self.change_size = TIME_INTERVAL/1.5
        self.change_hight = TIME_INTERVAL*2

        self.transparent = 0.5
        self.transparent_change = TIME_INTERVAL
        self.transparent_change_flag = 1  # 1 增加，0 减少
        

        self.color = self.generate_color()

        self.position = self.generate_position()
        #self.vbo_id = create_vbo(self.vertices_light)

    def generate_position(self):
        pos_change = np.array(
            [
                [random.uniform(*self.iniPos_Range)],
                [random.uniform(*self.iniPos_Range) + 2],
                [random.uniform(*self.iniPos_Range)],
            ]
        )
        return self.iniPosition + pos_change

    def generate_size(self):
        return random.uniform(*self.iniPos_Range)

    def generate_color(self):
        return self.Color_list[random.randint(0, len(self.Color_list) - 1)]

    def start_blowed(self):
        self.Z_acc = -0.001

    def stop_blowed(self):
        self.Z_acc = 0

    def update(self):
        change_time=(TIME_INTERVAL/0.001)
        self.Z_velocity += self.Z_acc*change_time
        if self.Z_acc:
            self.live -= random.uniform(-1.5, 3) * 0.5*change_time
            # print(self.live)

        self.position[1][0] += self.change_hight
        self.position[2][0] += self.Z_velocity*change_time
        self.size -= self.change_size

        if self.size <= 0:
            self.transparent_change_flag = 1
            self.transparent = 0
            self.Z_velocity = 0
            self.size = self.generate_size()
            self.position = self.generate_position()
            self.color = self.generate_color()

        if self.transparent_change_flag:
            self.transparent += self.transparent_change
            if self.transparent > 0.5:
                self.transparent_change_flag = 0

    
    def display(self):
        glPushMatrix()

        glTranslatef(*self.getPosition(self.position))

        ###
        glScalef(*[self.size] * 3)
        glColor4f(*to_one(self.color, self.transparent))  # 设置颜色和透明度
        glDrawArrays(GL_TRIANGLES, 0, self.vertices_len)


        # draw_vbo_model(
        #     self.vbo_id, self.vertices_len, to_one(self.color, self.transparent)
        # )
        glPopMatrix()

        # self.update()
